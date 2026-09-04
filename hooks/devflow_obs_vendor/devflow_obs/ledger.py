"""Run 目錄讀取與衍生(四節佈局)。

```
.devflow/runs/<run_id>/
├── manifest.json                  # coordinator 開 run 時 atomic 寫入
├── coordinator/events.jsonl       # run/stage/task lifecycle(coordinator 單寫)
├── attempts/<attempt_id>/
│   ├── events.jsonl               # 該 attempt 單寫
│   ├── context-manifest.json
│   └── result.json                # atomic finalize 標記;缺 + 無 completed = incomplete
├── reviews/<review_id>/events.jsonl
├── hooks/events-<session>.jsonl   # hook 機械事件(每 session 一檔,避免互踩)
├── verifier/events.jsonl          # Gauntlet 層事件(verification engine 單寫)
└── derived/run-events.jsonl       # 衍生 aggregate,隨時可重建
```
"""
import datetime
import json
import os
import tempfile

from . import event_validate, writer


def _sources(run_dir):
    """列出全部事件檔 (rel_path, abs_path),排序保證 derive 決定性。"""
    out = []
    coord = os.path.join(run_dir, "coordinator", "events.jsonl")
    if os.path.exists(coord):
        out.append(("coordinator/events.jsonl", coord))
    for sub in ("attempts", "reviews"):
        base = os.path.join(run_dir, sub)
        if os.path.isdir(base):
            for name in sorted(os.listdir(base)):
                p = os.path.join(base, name, "events.jsonl")
                if os.path.exists(p):
                    out.append((f"{sub}/{name}/events.jsonl", p))
    hooks = os.path.join(run_dir, "hooks")
    if os.path.isdir(hooks):
        for name in sorted(os.listdir(hooks)):
            if name.endswith(".jsonl"):
                out.append((f"hooks/{name}", os.path.join(hooks, name)))
    verif = os.path.join(run_dir, "verifier", "events.jsonl")
    if os.path.exists(verif):
        out.append(("verifier/events.jsonl", verif))
    return out


def _load_json(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def load_run(run_dir):
    """讀整個 run 目錄 → view dict(crash 截尾容忍;不改動任何檔案)。"""
    view = {
        "run_dir": run_dir,
        "manifest": _load_json(os.path.join(run_dir, "manifest.json")),
        "coordinator_events": [],
        "attempts": {},
        "reviews": {},
        "hook_events": [],
        "verifier_events": [],
    }
    for rel, path in _sources(run_dir):
        events, partial = writer._read_complete_events(path)
        parts = rel.split("/")
        if parts[0] == "coordinator":
            view["coordinator_events"] = events
        elif parts[0] == "attempts":
            att = parts[1]
            view["attempts"][att] = {
                "events": events,
                "partial_tail": partial,
                "result": _load_json(os.path.join(run_dir, "attempts", att,
                                                  "result.json")),
                "context_manifest": _load_json(
                    os.path.join(run_dir, "attempts", att,
                                 "context-manifest.json")),
                "stale_lock": writer.has_stale_lock(
                    os.path.join(run_dir, "attempts", att)),
            }
        elif parts[0] == "reviews":
            view["reviews"][parts[1]] = {"events": events, "partial_tail": partial}
        elif parts[0] == "hooks":
            view["hook_events"].extend(events)
        elif parts[0] == "verifier":
            view["verifier_events"] = events
    return view


def incomplete_attempts(run_dir):
    """crash 判定:有 attempt_started、無 attempt_completed 事件、無 result.json。"""
    view = load_run(run_dir)
    out = []
    for att, data in sorted(view["attempts"].items()):
        types = {e.get("event_type") for e in data["events"]}
        if "attempt_started" in types and "attempt_completed" not in types \
                and data["result"] is None:
            out.append(att)
    return out


def resume_state(run_dir):
    """restart 恢復:只靠檔案系統重建每 T 進度(ID 皆為持久字串)。"""
    view = load_run(run_dir)
    tasks = {}
    completed_atts = set()
    att_task = {}
    for att, data in view["attempts"].items():
        for e in data["events"]:
            if e.get("task_id"):
                att_task[att] = e["task_id"]
            if e.get("event_type") == "attempt_completed":
                completed_atts.add(att)
        if data["result"] is not None:
            completed_atts.add(att)
    for att, task in att_task.items():
        t = tasks.setdefault(task, {"attempts": [], "accepted": False,
                                    "attempt_count": 0, "open_attempt": None})
        t["attempts"].append(att)
        t["attempt_count"] += 1
        if att not in completed_atts:
            t["open_attempt"] = att
    for e in view["coordinator_events"]:
        if e.get("event_type") == "task_accepted" and e.get("task_id") in tasks:
            tasks[e["task_id"]]["accepted"] = True
    for t in tasks.values():
        t["attempts"].sort()
    return {"tasks": tasks,
            "incomplete_attempts": incomplete_attempts(run_dir),
            "run_id": (view["manifest"] or {}).get("run_id")}


def iter_run_events(run_dir):
    """全 run 事件依 (timestamp, source, seq) 排序後回傳(不寫檔)。"""
    merged = []
    for rel, path in _sources(run_dir):
        events, _ = writer._read_complete_events(path)
        for e in events:
            merged.append((e.get("timestamp", ""), rel, e.get("seq", 0), e))
    merged.sort(key=lambda item: item[:3])
    return [e for _, _, _, e in merged]


def derive(run_dir):
    """重建 derived/run-events.jsonl(衍生資料;隨時可刪可重建,byte 決定性)。"""
    events = iter_run_events(run_dir)
    derived_dir = os.path.join(run_dir, "derived")
    os.makedirs(derived_dir, exist_ok=True)
    out_path = os.path.join(derived_dir, "run-events.jsonl")
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=derived_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for e in events:
                f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, out_path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return out_path


def validate_run(run_dir):
    """schema 驗證每筆事件 + 交叉引用(parent attempt、review→attempt)。"""
    errors = []
    view = load_run(run_dir)
    known_atts = set(view["attempts"])
    all_events = []
    for rel, path in _sources(run_dir):
        events, _ = writer._read_complete_events(path)
        for e in events:
            all_events.append((rel, e))
            for err in event_validate.validate_event(e):
                err = dict(err, source=rel)
                errors.append(err)
    for att, data in view["attempts"].items():
        for e in data["events"]:
            if e.get("attempt_id") not in (None, att):
                errors.append({"code": "broken_ref", "field": "attempt_id",
                               "source": f"attempts/{att}",
                               "msg": f"事件 attempt_id={e.get('attempt_id')} "
                                      f"與所在目錄 {att} 不符"})
    for rel, e in all_events:
        parent = e.get("parent_attempt_id")
        if parent and parent not in known_atts:
            errors.append({"code": "broken_ref", "field": "parent_attempt_id",
                           "source": rel,
                           "msg": f"parent_attempt_id={parent} 不存在於 attempts/"})
        if e.get("event_type", "").startswith("review_") \
                and e.get("attempt_id") and e["attempt_id"] not in known_atts:
            errors.append({"code": "broken_ref", "field": "attempt_id",
                           "source": rel,
                           "msg": f"review 引用的 attempt {e['attempt_id']} 不存在"})
        run_id = e.get("run_id")
        manifest_run = (view["manifest"] or {}).get("run_id")
        if manifest_run and run_id and run_id != manifest_run:
            errors.append({"code": "broken_ref", "field": "run_id",
                           "source": rel,
                           "msg": f"事件 run_id={run_id} 與 manifest {manifest_run} 不符"})
    return errors


# ── repair(#103:壞 run 有出口)────────────────────────────────────
#
# 契約不變:「非截尾＝損壞」(writer.py `_read_complete_events`);截尾殘行
# (壞行落在最後一行、或檔案沒有結尾換行)由 reader 既有容忍,**不算損壞**、
# 不在 repair 範圍內 —— 那是既有 crash/incomplete 模型(`incomplete_attempts`
# 、`has_stale_lock`)的管轄,repair 不重複判定、也不搶著「續寫」。
# repair 處理的是中間一行壞掉、拖垮整檔重讀(`_read_complete_events` 對非
# 截尾壞行會 raise)的情況:把壞行起(含之後所有內容,無論是否還有合法行)
# 整段原子隔離到 `<file>.corrupt-<UTC 時戳>`,原檔只留壞行前的乾淨事件,
# 讓 `EventWriter` 之後能正常對該目錄重開續寫。**是破壞性動作**:壞行之後
# 若還有合法事件,一併進隔離檔,不逐行搶救。


def _scan_events_file(rel, path):
    """逐行掃一個事件檔,回傳壞行掃描結果或 None(乾淨/僅截尾殘行)。
    掃描邏輯與 `writer._read_complete_events` 判斷「是否截尾」同一套規則
    (`i >= len(lines) - 2`),差別只在這裡不 raise、改回傳診斷用的位置資訊。"""
    with open(path, "rb") as f:
        raw = f.read()
    lines = raw.split(b"\n")
    offset = 0
    clean_events = 0
    for i, line in enumerate(lines):
        line_len = len(line) + (1 if i < len(lines) - 1 else 0)
        if line.strip():
            try:
                json.loads(line.decode("utf-8"))
                clean_events += 1
            except (ValueError, UnicodeDecodeError):
                if i >= len(lines) - 2:
                    return None          # 截尾殘行:既有契約可續寫,非 repair 對象
                total = len(raw)
                lock_path = path + ".lock"
                return {
                    "source": rel, "path": path,
                    "clean_events": clean_events,
                    "bad_line_no": i + 1,
                    "total_bytes": total,
                    "corrupt_offset": offset,
                    "quarantine_bytes": total - offset,
                    "locked": os.path.exists(lock_path),
                    "lock_path": lock_path,
                }
        offset += line_len
    return None


def scan_corruption(run_dir):
    """掃描 run_dir 下所有事件檔,列出每個「非截尾＝損壞」檔案的修復計畫
    (不動任何檔案)。找不到 run_dir 本身視為呼叫端誤用,明確 raise —— 不要
    讓打錯路徑靜默回報「沒有損壞」。"""
    if not os.path.isdir(run_dir):
        raise FileNotFoundError(f"run_dir 不存在:{run_dir}")
    out = []
    for rel, path in _sources(run_dir):
        found = _scan_events_file(rel, path)
        if found is not None:
            out.append(found)
    return out


def _quarantine_path(path):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y%m%dT%H%M%S.%fZ")
    candidate = f"{path}.corrupt-{ts}"
    n = 0
    while os.path.exists(candidate):
        n += 1
        candidate = f"{path}.corrupt-{ts}-{n}"
    return candidate


def repair_run(run_dir, apply=False):
    """#103:壞 run 有出口。dry-run(預設,apply=False)只回報計畫,不動任何
    檔案,呼叫端可安全重跑。apply=True 才真的動作:

    1. 壞行前的乾淨事件先寫進同目錄 tmp 檔(fsync),
    2. 把原檔原子搬成 `<file>.corrupt-<UTC 時戳>`(保留全部原始 bytes,供稽核
       回溯 —— 壞行之後若還有合法事件,一併隔離,repair 不逐行搶救),
    3. 把 tmp 頂上原檔名(os.replace,同 `atomic_write_json` 手法)。

    有 `events.jsonl.lock`(或 hook 的 `events-<session>.jsonl.lock`)的檔案
    **跳過不修**:crash 遺留鎖是 `has_stale_lock` 的既有佐證,可能還有寫入者
    在跑,repair 不搶著清鎖或搬檔(fail-closed;人工確認無人在寫、手動清鎖
    後再重跑 repair)。回傳結構化摘要,風格同 `validate_run` 的 error dict
    (帶 `code`/`source`/`msg`)。

    repair 後 `derived/run-events.jsonl` 已過期(不含隔離掉的內容),下一次
    `derive` 會依現況重建,不需另外處理。"""
    plan = scan_corruption(run_dir)
    if not plan:
        return {"run_dir": run_dir, "apply": apply, "corrupt_found": False,
                "items": [],
                "msg": "未發現需要 repair 的損壞檔"
                       "(截尾殘行由既有契約容忍,不算損壞,不需 repair)"}
    items = []
    for p in plan:
        if not apply:
            items.append({
                "code": "would_repair", "source": p["source"],
                "path": p["path"], "bad_line_no": p["bad_line_no"],
                "clean_events_before_bad_line": p["clean_events"],
                "total_bytes": p["total_bytes"],
                "quarantine_bytes": p["quarantine_bytes"],
                "locked": p["locked"],
                "msg": (f"第 {p['bad_line_no']} 行壞(非截尾);壞行前 "
                        f"{p['clean_events']} 筆乾淨事件;--apply 後會把壞行起 "
                        f"{p['quarantine_bytes']} bytes 隔離到 "
                        f"{os.path.basename(p['path'])}.corrupt-<UTC 時戳>,原檔"
                        f"只留壞行前的乾淨事件" +
                        (";⚠ 該檔有 lock,--apply 時會跳過不修"
                         if p["locked"] else ""))})
            continue
        if p["locked"]:
            items.append({
                "code": "locked_skip", "source": p["source"],
                "path": p["path"], "lock_path": p["lock_path"],
                "msg": f"{p['lock_path']} 存在(crash 遺留鎖或仍有寫入者),"
                       f"repair 跳過此檔不動 —— 先確認無人在寫、手動清鎖後再重跑"})
            continue
        path = p["path"]
        with open(path, "rb") as f:
            raw = f.read()
        clean_part = raw[:p["corrupt_offset"]]
        directory = os.path.dirname(path)
        fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(clean_part)
                f.flush()
                os.fsync(f.fileno())
            quarantine_path = _quarantine_path(path)
            os.replace(path, quarantine_path)   # 原檔(全部原始 bytes)先搬走
            os.replace(tmp, path)                # 乾淨前綴(已 fsync)頂上原檔名
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        items.append({
            "code": "repaired", "source": p["source"], "path": path,
            "quarantined_to": quarantine_path,
            "clean_events_kept": p["clean_events"],
            "quarantine_bytes": p["quarantine_bytes"],
            "msg": (f"壞行起 {p['quarantine_bytes']} bytes 已隔離到 "
                    f"{os.path.basename(quarantine_path)};原檔留 "
                    f"{p['clean_events']} 筆乾淨事件,可正常重開續寫")})
    return {"run_dir": run_dir, "apply": apply, "corrupt_found": True,
            "items": items}
