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
