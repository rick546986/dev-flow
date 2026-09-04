"""_obs_impl.py — devflow-obs runtime(P3 Observability;薄殼 = devflow-obs.sh)。

事件唯一合法落盤通道:agent 禁直寫 .devflow/(guard/prebash 會擋),事件一律經本
CLI —— stdin 吃 JSON、自行解析 run 路徑,**命令列不鋪 .devflow/ 路徑**(prebash
regex 會攔「rm/mv/> + .devflow/」組合,四節陷阱)。
run_id 由 P1 於 start 時生成(exec.json v2,schema="exec-v2");本 CLI 只讀不生,
讀不到(v1 旗標/未武裝)= 明確錯誤,不猜、不靜默退回。
vendor 行為正本:hooks/devflow_obs_vendor/(方法論 repo observability/ 副本,
來源 SHA 見 VENDOR-SOURCE.md);本檔只加 runtime 側加嚴與落盤通道,不重抄規則。

子命令:
  event [slug]            stdin 事件 JSON → 驗證(vendor+runtime 加嚴)→ 依事件型別
                          路由落盤 runs/<run_id>/{coordinator,attempts,reviews,verifier}
  hook-event              stdin 事件 JSON(writer=hook)→ hooks/events-<session>.jsonl;
                          schema 機械拒收 agent_role/model/prompt(hook 不推測歸屬)
  context-manifest <att>  stdin manifest JSON → attempts/<att>/context-manifest.json,
                          回印 context_manifest_hash
  validate [--strict] [run_id ...]   schema+交叉引用驗證(--strict 加 runtime 加嚴表)
  derive [run_id ...]     重建 derived/run-events.jsonl(byte 決定性)
  repair <run_id> [--apply]  #103:壞 run 有出口。預設 dry-run 只印計畫;
                          --apply 才把壞行起隔離到 <file>.corrupt-<UTC 時戳>,
                          原檔留壞行前乾淨事件,之後可正常重開續寫
  stats / recommend       vendor stats 聚合(--run-id/--legacy-md/--min-n/--threshold)
  archive [run_id]        歸檔至 LEDGER_HOME/runs/<repo_id>/<run_id>/(OC-5)
  retention status|prune [--dry-run]  保存政策(180 天 raw);**僅手動執行,
                          禁背景自動刪除服務**(OC-5)
  ledger-home             印出解析後的 DEVFLOW_LEDGER_HOME
  registry validate [path] 驗 prompt-registry.json(vendor validator)
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "devflow_obs_vendor"))
from devflow_obs import event_validate, ids, ledger, stats, writer  # noqa: E402

SCHEMA_LINE = "devflow-agent-event/1.1"        # 1.1:新寫入一律 /1.1;舊 /1 讀取相容
RETENTION_DAYS_RAW = 180                       # OC-5:raw events/manifests 180 天

# ── 共享契約 §6 runtime 加嚴(schema 1.1 已含欄位級 maxlen;本表為 runtime 端
#    雙保險,上限與正本一致,vendor re-vendor 落後時仍把關)────────────────
FIELD_MAX = {
    "prompt.id": 100, "prompt.version": 40, "model": 100,
    "failure_reason": 500, "reason": 500,
    "finding_summary": 1000, "title": 1000,
    "command_reference": 500, "command_ref": 500,
    "artifact_reference": 1000, "artifact_ref": 1000,
    "result_summary": 2000,
}
# §6 禁載欄位中 vendor privacy 名單掃不到的(其餘 token/secret/credential/
# patient/medical/transcript/prompt_body/raw_log 已由 vendor 機械拒收)
EXTRA_FORBIDDEN_KEYS = {"source_body", "customer_data"}

ATTEMPT_FILE_EVENTS = {"attempt_started", "attempt_completed",
                       "tool_invoked", "tool_completed"}
REVIEW_FILE_EVENTS = {"review_started", "review_completed", "finding_created"}
VERIFIER_EVENTS = {"verification_layer_started", "verification_layer_completed",
                   "final_fresh_run_started", "final_fresh_run_completed"}


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def _print(obj):
    # 與方法論 CLI devflow-obs.py 相同輸出格式(對拍 §11 要求 byte 一致)
    print(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True))


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _find_contract_for_enum(root):
    """task_tags 受控 enum 正本 = devflow-contract.json(1.1;schema 只留指標)。
    plugin 環境解析鏈:$DEVFLOW_CONTRACT(明示指定,缺檔即錯不 fallback)→
    受測專案 docs/dev/ 散發副本 → plugin 根(vendor _CONTRACT_DIR 預設解析點)。
    回傳 (path|None, tried_paths)。"""
    env = os.environ.get("DEVFLOW_CONTRACT")
    if env:
        return (env if os.path.exists(env) else None), [env]
    tried = [os.path.join(root, "docs", "dev", "devflow-contract.json"),
             os.path.join(os.path.dirname(HERE), "devflow-contract.json")]
    for c in tried:
        if os.path.exists(c):
            return c, tried
    return None, tried


def seed_task_tags_enum(root, required):
    """把 enum 現值灌進 vendor validator 的 contract cache(單一正本,不重抄值)。
    required=True 且找不到契約 → 明確 fail-closed,**不靜默跳過 task_tags 驗證**。
    回傳 enum list 或 None(未 seed)。"""
    path, tried = _find_contract_for_enum(root)
    if not path:
        if required:
            die("⛔ devflow-obs:事件帶 task_tags,但找不到受控 enum 正本 "
                "devflow-contract.json(找過:" + "、".join(tried) + ")。"
                "fail-closed 拒收,不靜默跳過 task_tags 驗證 —— 先跑 dev-setup "
                "散發契約至專案 docs/dev/,或以 DEVFLOW_CONTRACT 指定。")
        return None
    try:
        with open(path) as f:
            tags = json.load(f)["task_tags"]
    except Exception as e:
        die(f"⛔ devflow-obs:契約 {path} 讀取失敗({e}),task_tags 驗證 "
            f"fail-closed。")
    # vendor event_validate 的 _resolve_item_enum 以此 cache key 取 enum;
    # 預灌後其解析不再回退到 plugin 根檔案。
    event_validate._cache["contract:devflow-contract.json#task_tags"] = tags
    return tags


def _has_task_tags(obj):
    return "task_tags" in obj or "x_task_tags" in obj


def runtime_check(obj, tags_enum=None):
    """共享契約 §6 加嚴:欄位級長度上限 + 追加禁載欄位 + task_tags 受控 enum
    (x_task_tags 為 1.0 相容承接欄,與正式 task_tags 同 enum 驗證)。"""
    errs = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                p = f"{path}.{k}" if path else str(k)
                bare = str(k).lower()
                # r2-#98 F1:同型迴圈同型修法,見 event_validate.py 同段註解。
                bare = re.sub(r"^(?:x_+)+", "", bare)
                if bare in EXTRA_FORBIDDEN_KEYS:
                    errs.append({"code": "privacy_forbidden_key", "field": p,
                                 "msg": f"禁載欄位 {k!r}(共享契約 §6 runtime 加嚴)"})
                    continue
                walk(v, p)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(obj, "")
    for key, cap in FIELD_MAX.items():
        cur = obj
        for part in key.split("."):
            cur = cur.get(part) if isinstance(cur, dict) else None
            if cur is None:
                break
        if isinstance(cur, str) and len(cur) > cap:
            errs.append({"code": "field_too_long", "field": key,
                         "msg": f"長度 {len(cur)} 超過共享契約 §6 上限 {cap}"})
    tags = obj.get("x_task_tags")
    if tags is not None and tags_enum is not None:
        if not isinstance(tags, list):
            errs.append({"code": "invalid_format", "field": "x_task_tags",
                         "msg": "須為陣列(受控 enum 多選)"})
        else:
            for i, t in enumerate(tags):
                if not isinstance(t, str) or t not in tags_enum:
                    errs.append({"code": "invalid_enum", "field": f"x_task_tags[{i}]",
                                 "msg": f"task_tag 受控 enum(正本 = devflow-"
                                        f"contract.json),禁自由字串;得到 {t!r}"})
    return errs


# ── 狀態/路徑解析 ────────────────────────────────────────────────


def read_state(root):
    """讀 exec.json 取 run_id;v1/未武裝 = 明確錯誤(run_id 生成歸 P1)。"""
    execp = os.path.join(root, ".devflow", "exec.json")
    if not os.path.exists(execp):
        die("⛔ devflow-obs:守衛未武裝(找不到執行旗標)。事件必須綁 run_id"
            "(由 devflow-exec.sh start 生成,exec-v2)——先 start 再記事件。")
    try:
        with open(execp) as f:
            state = json.load(f)
    except Exception as e:
        die(f"⛔ devflow-obs:執行旗標損壞({e})。fail-closed 不落盤;"
            f"跑 devflow-exec.sh stop 後重新 start。")
    run_id = state.get("run_id")
    if not run_id:
        die("⛔ devflow-obs:exec.json 沒有 run_id(v1 旗標;run_id 由 P1 的 "
            "exec-v2 start 生成)。不猜 ID、不自建 run —— 待 exec-v2 落地或重新 start。")
    if not ids.is_valid_id("run", run_id):
        die(f"⛔ devflow-obs:exec.json run_id={run_id!r} 非法"
            f"(須 run_<26 字 Crockford ULID>)。")
    return state, run_id


def runs_root(root):
    env = os.environ.get("DEVFLOW_RUNS_ROOT")
    if not env:
        return os.path.join(root, ".devflow", "runs")
    # MINOR-3:override 不得把事件檔導進受測 repo 內 .devflow/ 之外的路徑
    # (= 繞守衛把檔案走私進工作樹;postbash 會抓,但這裡直接拒於源頭)。
    # repo 外路徑與 .devflow/ 內照常允許 —— 對拍/selftest 測試用途保留。
    real = os.path.realpath(env)
    root_real = os.path.realpath(root)
    devflow_real = os.path.join(root_real, ".devflow")
    inside_repo = real == root_real or real.startswith(root_real + os.sep)
    inside_devflow = real == devflow_real or real.startswith(devflow_real + os.sep)
    if inside_repo and not inside_devflow:
        die(f"⛔ devflow-obs:DEVFLOW_RUNS_ROOT 指向受測 repo 內部但 .devflow/ 之外"
            f"({real})—— 拒絕把事件檔走私進工作樹。"
            f"repo 外路徑或 .devflow/ 內照常允許(測試用途)。")
    return env


def repo_id(root):
    real = os.path.realpath(root)
    return "repo_" + hashlib.sha256(real.encode("utf-8")).hexdigest()[:16]


def head_sha(root):
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                       capture_output=True, text=True)
    sha = r.stdout.strip()
    if r.returncode or not sha:
        die("⛔ devflow-obs:無法取得 HEAD SHA(manifest source_sha 必填,OC-5)。")
    return sha


def ensure_manifest(root, run_dir, run_id, state):
    """run 首事件時建 manifest(OC-5 六必填:repo_id/run_id/schema_version/
    created_at/expires_at/source_sha;另帶 run fixture 慣用欄位)。

    #103:兩行程同時首事件會同時通過下面的存在檢查、各自算出 manifest 內容
    (created_at 等會不同),原本各自 atomic_write_json(temp+rename)最後一個
    replace 靜默蓋掉先到者。改用互斥建立語義:先把完整內容寫進同目錄 tmp 檔
    (fsync),用 os.link 把 tmp 曝光成正式檔名 —— link() 是核心保證的互斥
    操作,兩行程同時 link 只有一個成功,另一個拿 FileExistsError(= 別人已建,
    讀回既有內容不覆寫)。先寫滿 tmp 再曝光,不會像直接對正式檔名開
    O_CREAT|O_EXCL 那樣讓其他讀者看到半成品(零位元組)manifest.json,維持
    四節②「快照類一律 atomic write」的規則。開頭的 os.path.exists 只是快
    路徑優化(manifest 建好後,同 run 後續每筆事件都會再呼叫本函式),真正
    的互斥由 os.link 提供,不受這條檢查的 TOCTOU 影響。"""
    mp = os.path.join(run_dir, "manifest.json")
    if os.path.exists(mp):
        return
    os.makedirs(run_dir, exist_ok=True)
    created = now_iso()
    expires = (datetime.datetime.fromisoformat(created)
               + datetime.timedelta(days=RETENTION_DAYS_RAW)).isoformat(timespec="seconds")
    sha = head_sha(root)
    payload = {
        "schema": "devflow-run-manifest/1",
        "schema_version": "1.0.0",
        "repo_id": repo_id(root),
        "run_id": run_id,
        "feature_slug": state.get("slug", ""),
        "base_sha": sha[:7],
        "source_sha": sha,
        "workspace": os.path.basename(os.path.realpath(root)),
        "started": created,
        "created_at": created,
        "expires_at": expires,
    }
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=run_dir)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        try:
            os.link(tmp, mp)
        except FileExistsError:
            pass  # 別人已建(os.link 提供真正互斥);不覆寫,讀回既有內容
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def resolve_run_dirs(root, run_ids):
    base = runs_root(root)
    if run_ids:
        dirs = []
        for rid in run_ids:
            d = os.path.join(base, rid)
            if not os.path.isdir(d):
                die(f"⛔ devflow-obs:找不到 run {rid}(於 runs 目錄下)。")
            dirs.append(d)
        return dirs
    if not os.path.isdir(base):
        die("⛔ devflow-obs:尚無任何 run 目錄(先經 event 子命令落盤)。")
    return [os.path.join(base, n) for n in sorted(os.listdir(base))
            if n.startswith("run_") and os.path.isdir(os.path.join(base, n))]


# ── event / hook-event ──────────────────────────────────────────


def read_stdin_json():
    raw = sys.stdin.read()
    try:
        obj = json.loads(raw)
    except ValueError as e:
        die(f"⛔ devflow-obs:stdin 不是合法 JSON({e})。")
    if not isinstance(obj, dict):
        die("⛔ devflow-obs:事件須為 JSON object。")
    return obj


def validate_or_die(root, event):
    # seq 由 writer 於 append 時補號(單檔遞增);驗證用 probe 帶佔位 seq。
    # 事件帶 task_tags/x_task_tags → 必先解析受控 enum(缺契約 = 明確拒收)。
    tags_enum = seed_task_tags_enum(root, required=_has_task_tags(event))
    probe = dict(event)
    probe.setdefault("seq", 1)
    errors = event_validate.validate_event(probe) + runtime_check(probe, tags_enum)
    if errors:
        _print({"errors": errors})
        sys.exit(1)


def target_dir(run_dir, event):
    etype = event.get("event_type")
    if event.get("writer") == "verifier" or etype in VERIFIER_EVENTS:
        return os.path.join(run_dir, "verifier")
    if etype in ATTEMPT_FILE_EVENTS and event.get("attempt_id"):
        return os.path.join(run_dir, "attempts", event["attempt_id"])
    if etype in REVIEW_FILE_EVENTS and event.get("review_id"):
        return os.path.join(run_dir, "reviews", event["review_id"])
    return os.path.join(run_dir, "coordinator")


def cmd_event(root, slug_arg):
    event = read_stdin_json()
    state, run_id = read_state(root)
    if slug_arg and slug_arg != state.get("slug"):
        die(f"⛔ devflow-obs:slug 不符(旗標 {state.get('slug')!r},"
            f"命令列 {slug_arg!r})。")
    event.setdefault("schema", SCHEMA_LINE)
    event.setdefault("timestamp", now_iso())
    event.setdefault("writer", "coordinator")
    if event["writer"] == "hook":
        die("⛔ devflow-obs:hook 事件請走 hook-event 子命令(分檔避免互踩)。")
    event.setdefault("run_id", run_id)
    if event["run_id"] != run_id:
        die(f"⛔ devflow-obs:事件 run_id={event['run_id']} 與旗標 {run_id} 不符。")
    validate_or_die(root, event)
    run_dir = os.path.join(runs_root(root), run_id)
    ensure_manifest(root, run_dir, run_id, state)
    d = target_dir(run_dir, event)
    try:
        w = writer.EventWriter(d)
    except writer.AlreadyLocked as e:
        die(f"⛔ devflow-obs:{e}")
    try:
        rec = w.append(event)              # 6.4:verification_layer_completed
    except ValueError as e:                # 由 writer 正規化 status-only,壞形狀拒寫
        die(f"⛔ devflow-obs:{e}")
    finally:
        w.close()
    if event.get("event_type") == "attempt_completed" and event.get("attempt_id"):
        result = {"result": event.get("result")}
        for k in ("failure_category", "candidate_sha"):
            if event.get(k):
                result[k] = event[k]
        writer.atomic_write_json(
            os.path.join(run_dir, "attempts", event["attempt_id"], "result.json"),
            result)
    print(f"✅ event {event.get('event_type')} → run {run_id}(seq {rec['seq']})")


def _sanitize_session(session):
    return "".join(c if (c.isalnum() or c in "._-") else "-" for c in session) or "unknown"


def cmd_hook_event(root):
    event = read_stdin_json()
    state, run_id = read_state(root)
    event["writer"] = "hook"
    event.setdefault("schema", SCHEMA_LINE)
    event.setdefault("timestamp", now_iso())
    event.setdefault("run_id", run_id)
    if event["run_id"] != run_id:
        die(f"⛔ devflow-obs:事件 run_id={event['run_id']} 與旗標 {run_id} 不符。")
    session = event.get("session_ref")
    if not session:
        try:
            session = json.loads(os.environ.get("HOOK_INPUT", "{}")).get("session_id", "")
        except Exception:
            session = ""
        if session:
            event["session_ref"] = session
    session = _sanitize_session(session or "unknown")
    try:                                   # 6.4:status-only 正規化同樣適用 hook 通道
        event = writer._normalize_status_only(event)
    except ValueError as e:
        die(f"⛔ devflow-obs:{e}")
    validate_or_die(root, event)
    run_dir = os.path.join(runs_root(root), run_id)
    ensure_manifest(root, run_dir, run_id, state)
    d = os.path.join(run_dir, "hooks")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"events-{session}.jsonl")
    lock = path + ".lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        die(f"⛔ devflow-obs:hook 事件檔已有寫入者(或 crash 遺留鎖 events-"
            f"{session}.jsonl.lock)。")
    try:
        existing, _ = writer._read_complete_events(path)
        event.setdefault("seq", max([e.get("seq", 0) for e in existing], default=0) + 1)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
    finally:
        os.close(fd)
        os.remove(lock)
    print(f"✅ hook-event {event.get('event_type')} → session {session}"
          f"(seq {event['seq']})")


def cmd_context_manifest(root, attempt_id):
    if not ids.is_valid_id("attempt", attempt_id):
        die(f"⛔ devflow-obs:attempt_id {attempt_id!r} 非法。")
    manifest = read_stdin_json()
    errors = event_validate.validate_context_manifest(manifest) \
        + runtime_check(manifest, seed_task_tags_enum(root, required=False))
    if errors:
        _print({"errors": errors})
        sys.exit(1)
    state, run_id = read_state(root)
    run_dir = os.path.join(runs_root(root), run_id)
    ensure_manifest(root, run_dir, run_id, state)
    writer.atomic_write_json(
        os.path.join(run_dir, "attempts", attempt_id, "context-manifest.json"), manifest)
    print(event_validate.context_manifest_hash(manifest))


# ── validate / derive / stats / recommend ───────────────────────


def cmd_validate(root, args):
    strict = "--strict" in args
    run_ids = [a for a in args if not a.startswith("--")]
    tags_enum = seed_task_tags_enum(root, required=False)
    report, dirty = {}, False
    for rd in resolve_run_dirs(root, run_ids):
        try:
            errors = ledger.validate_run(rd)
            if strict:
                for rel, path in ledger._sources(rd):
                    events, _ = writer._read_complete_events(path)
                    for e in events:
                        for err in runtime_check(e, tags_enum):
                            errors.append(dict(err, source=rel))
        except Exception as e:
            # #103:strict 重讀同一批檔與非 strict 共用這個 try/except,
            # 壞檔轉成結構化 run_error(同錯誤碼、同欄位),不讓單一 run 拖垮
            # 整批(裸 traceback 會連 _print(report) 都跑不到,乾淨 run 也
            # 印不出報告)。exit code 語義不變:errors 非空仍算 dirty。
            errors = [{"code": "run_error", "field": rd,
                       "msg": f"{type(e).__name__}: {e}"}]
        report[os.path.basename(rd.rstrip("/"))] = errors
        dirty = dirty or bool(errors)
    _print(report)
    return 1 if dirty else 0


def cmd_derive(root, run_ids):
    _print({os.path.basename(rd.rstrip("/")): ledger.derive(rd)
            for rd in resolve_run_dirs(root, run_ids)})
    return 0


def cmd_repair(root, args):
    # #103:壞 run 有出口。命令列只吃 run_id(經 resolve_run_dirs 解析路徑),
    # 不在命令列鋪 .devflow/ 路徑 —— 與本檔其餘子命令同一慣例(見檔頭註解)。
    apply = "--apply" in args
    run_ids = [a for a in args if not a.startswith("--")]
    if len(run_ids) != 1:
        die("用法: devflow-obs.sh repair <run_id> [--apply]")
    rd = resolve_run_dirs(root, run_ids)[0]
    _print(ledger.repair_run(rd, apply=apply))
    return 0


def _parse_stats_args(args):
    run_ids, legacy, min_n, threshold = [], [], 5, 0.6
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--run-id":
            i += 1
            run_ids.append(args[i])
        elif a == "--legacy-md":
            i += 1
            legacy.append(args[i])
        elif a == "--min-n":
            i += 1
            min_n = int(args[i])
        elif a == "--threshold":
            i += 1
            threshold = float(args[i])
        else:
            die(f"⛔ devflow-obs:未知參數 {a!r}。")
        i += 1
    return run_ids, legacy, min_n, threshold


def cmd_stats(root, args, recommend=False):
    run_ids, legacy, min_n, threshold = _parse_stats_args(args)
    dirs = resolve_run_dirs(root, run_ids)
    agg = stats.aggregate_runs(dirs, legacy_paths=legacy, min_n=min_n)
    _print(stats.recommendations(agg, success_threshold=threshold) if recommend else agg)
    return 0


# ── Ledger Retention(OC-5)────────────────────────────────────


def ledger_home():
    env = os.environ.get("DEVFLOW_LEDGER_HOME")
    if env:
        return os.path.expanduser(env)
    plat = os.environ.get("DEVFLOW_LEDGER_OS", sys.platform)
    if plat.startswith("darwin"):
        return os.path.expanduser("~/Library/Application Support/DevFlow/ledger")
    xdg = os.environ.get("XDG_STATE_HOME", "").strip() \
        or os.path.expanduser("~/.local/state")
    return os.path.join(xdg, "devflow", "ledger")


def cmd_archive(root, run_id_arg):
    if run_id_arg:
        run_id = run_id_arg
        if not ids.is_valid_id("run", run_id):
            die(f"⛔ devflow-obs:run_id {run_id!r} 非法。")
    else:
        _, run_id = read_state(root)
    src = os.path.join(runs_root(root), run_id)
    if not os.path.isdir(src):
        die(f"⛔ devflow-obs:找不到 run {run_id},無可歸檔。")
    dst = os.path.join(ledger_home(), "runs", repo_id(root), run_id)
    if os.path.exists(dst):
        die(f"⛔ devflow-obs:{run_id} 已歸檔過(LEDGER_HOME 內已存在),不覆寫。")
    shutil.copytree(src, dst,
                    ignore=shutil.ignore_patterns("*.lock", ".tmp-*"))
    mp = os.path.join(dst, "manifest.json")
    manifest = {}
    if os.path.exists(mp):
        try:
            with open(mp) as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}
    created = manifest.get("created_at") or manifest.get("started") or now_iso()
    source_sha = manifest.get("source_sha") or manifest.get("base_sha")
    if not source_sha:
        die("⛔ devflow-obs:run manifest 缺 source_sha/base_sha,歸檔 manifest "
            "必含 source_sha(OC-5)——先補 manifest 再歸檔。")
    manifest.update({
        "repo_id": manifest.get("repo_id") or repo_id(root),
        "run_id": run_id,
        "schema_version": manifest.get("schema_version") or "1.0.0",
        "created_at": created,
        "expires_at": manifest.get("expires_at")
        or (datetime.datetime.fromisoformat(created)
            + datetime.timedelta(days=RETENTION_DAYS_RAW)).isoformat(timespec="seconds"),
        "source_sha": source_sha,
    })
    writer.atomic_write_json(mp, manifest)
    print(f"✅ 已歸檔 run {run_id} → LEDGER_HOME(180 天 raw retention;"
          f"prune 僅手動,禁背景自動刪除)")


def scan_ledger():
    home = ledger_home()
    base = os.path.join(home, "runs")
    entries = []
    now = datetime.datetime.now().astimezone()
    if os.path.isdir(base):
        for repo in sorted(os.listdir(base)):
            rp = os.path.join(base, repo)
            if not os.path.isdir(rp):
                continue
            for run in sorted(os.listdir(rp)):
                rd = os.path.join(rp, run)
                if not os.path.isdir(rd):
                    continue
                entry = {"repo_id": repo, "run_id": run,
                         "expires_at": None, "expired": False,
                         "manifest_ok": False}
                mp = os.path.join(rd, "manifest.json")
                try:
                    with open(mp) as f:
                        m = json.load(f)
                    exp = m.get("expires_at")
                    entry["expires_at"] = exp
                    entry["manifest_ok"] = True
                    if exp:
                        entry["expired"] = \
                            datetime.datetime.fromisoformat(exp) <= now
                except Exception:
                    pass                      # 無法判齡 → 保守:永不視為過期
                entry["_path"] = rd
                entries.append(entry)
    return home, entries


def cmd_retention(args):
    if not args or args[0] not in ("status", "prune"):
        die("用法: devflow-obs.sh retention status | prune [--dry-run]"
            "(僅手動執行;禁背景自動刪除服務,OC-5)")
    action = args[0]
    dry = "--dry-run" in args[1:]
    home, entries = scan_ledger()
    expired = [e for e in entries if e["expired"]]
    if action == "status":
        _print({"ledger_home": home,
                "retention_days_raw": RETENTION_DAYS_RAW,
                "runs_total": len(entries),
                "expired_n": len(expired),
                "runs": [{k: v for k, v in e.items() if k != "_path"}
                         for e in entries],
                "note": "raw 180 天/去識別化 aggregate 365 天;prune 僅手動,"
                        "禁背景自動刪除;預設不雲端同步(OC-5)"})
        return 0
    if dry:
        _print({"ledger_home": home,
                "would_remove": [{"repo_id": e["repo_id"], "run_id": e["run_id"],
                                  "expires_at": e["expires_at"]} for e in expired],
                "note": "dry-run:未刪除任何檔案"})
        return 0
    removed = []
    for e in expired:
        shutil.rmtree(e["_path"])
        removed.append({"repo_id": e["repo_id"], "run_id": e["run_id"]})
    _print({"ledger_home": home, "removed": removed})
    return 0


# ── registry ────────────────────────────────────────────────────


def cmd_registry(args):
    if not args or args[0] != "validate":
        die("用法: devflow-obs.sh registry validate [path]")
    path = args[1] if len(args) > 1 else os.path.join(HERE, "prompt-registry.json")
    try:
        with open(path) as f:
            registry = json.load(f)
    except Exception as e:
        die(f"⛔ devflow-obs:讀不到 registry {path}({e})。")
    errors = event_validate.validate_prompt_registry(registry)
    _print(errors)
    return 1 if errors else 0


# ── main ────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 3:
        die("用法: _obs_impl.py <cmd> <root> [args...](經 devflow-obs.sh 呼叫)")
    cmd, root, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    if cmd == "event":
        cmd_event(root, args[0] if args else "")
        return 0
    if cmd == "hook-event":
        cmd_hook_event(root)
        return 0
    if cmd == "context-manifest":
        if not args:
            die("用法: devflow-obs.sh context-manifest <attempt_id> < manifest.json")
        cmd_context_manifest(root, args[0])
        return 0
    if cmd == "validate":
        return cmd_validate(root, args)
    if cmd == "derive":
        return cmd_derive(root, args)
    if cmd == "repair":
        return cmd_repair(root, args)
    if cmd == "stats":
        return cmd_stats(root, args)
    if cmd == "recommend":
        return cmd_stats(root, args, recommend=True)
    if cmd == "archive":
        cmd_archive(root, args[0] if args else "")
        return 0
    if cmd == "retention":
        return cmd_retention(args)
    if cmd == "ledger-home":
        print(ledger_home())
        return 0
    if cmd == "registry":
        return cmd_registry(args)
    die(f"未知子命令 {cmd!r}。可用:event/hook-event/context-manifest/validate/"
        f"derive/repair/stats/recommend/archive/retention/ledger-home/registry")


if __name__ == "__main__":
    sys.exit(main())
