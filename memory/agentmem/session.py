"""通用 memory session / checkpoint(不分 dev-talk 與 dev-run)。

**這一檔在修一個具體缺陷**:先前只有 `dev-talk` 那條路能把記憶固化。
一般開發(Stage 6 / dev-run)做完一個 schema change,Git 有 commit,
**Memory 什麼都不知道** —— 記憶系統變成「可以存、可以查」,而不是
「每做一次專案就更了解專案」。

兩種模式共用同一組原語,`dev-run` 不必假裝自己是 dev-talk:

    understanding   dev-talk:對話 → 候選 → 使用者確認 → checkpoint
    implementation  dev-run:實作 → 觀察 → 高訊號萃取 → checkpoint

**不變的三件事**:
1. `sync.consolidate()` 仍是唯一的 durable writer —— 本檔不另開寫入路徑。
2. Signal Gate 照舊:讀檔 / grep / 列目錄 / 一般成功指令**不進 Git**,
   但仍留在本機(可稽核)。
3. **不自動 promote 使用者沒確認的 domain truth**:implementation 模式產生的
   knowledge 一律 CANDIDATE + code_inference,要升級成已確認得走 dev-talk。

`observe()` 是 implementation 模式的入口。它做三件事:記一筆本機事件、過 Signal
Gate、高訊號才登記成候選。候選帶完整 provenance(project/session/branch/commit/
paths/evidence/occurred_at/confidence/authority),沒有 provenance 的記憶在別台
機器上等於傳聞。
"""
import os

from . import identity, signal, store as store_mod, sync, truth

UNDERSTANDING = "understanding"
IMPLEMENTATION = "implementation"
MODES = (UNDERSTANDING, IMPLEMENTATION)

OPEN = "OPEN"
CLOSED = "CLOSED"
ABORTED = "ABORTED"

# `observe()` 的結構化目標;其餘 kind 一律當事件種類處理。
STRUCTURAL_KINDS = ("fact", "decision", "skill", "knowledge")


class SessionError(RuntimeError):
    """session 狀態錯誤,或證據不足以支撐所宣稱的狀態 —— 一律 fail-loud。"""


def start(store, repo_root, mode, topic, feature_slug=None, snapshot=None,
          now=None):
    """開一個 memory session。回傳的 dict 就是呼叫端要保存的 workflow state。"""
    if mode not in MODES:
        raise SessionError(
            "未知的 session mode:{0!r}(合法值 {1})".format(mode, list(MODES)))
    snapshot = snapshot or identity.workspace_snapshot(repo_root)
    session_id = store.start_session(
        topic, mode=mode, branch=snapshot.get("branch"),
        head_sha=snapshot.get("head_sha"), now=now, feature_slug=feature_slug)
    return {
        "session_id": session_id,
        "mode": mode,
        "topic": topic,
        "feature_slug": feature_slug,
        "branch": snapshot.get("branch"),
        "starting_head": snapshot.get("head_sha"),
        "started_at": store.session(session_id)["started_at"],
    }


def require_open(store, session_id):
    row = store.session(session_id)
    if row is None:
        raise SessionError(
            "session 不存在:{0} —— 先跑 `session start`(或 `talk start`)"
            "取得 session_id,不要自己編一個".format(session_id))
    if row["status"] != OPEN:
        raise SessionError(
            "session {0} 已是 {1};要繼續請開新的 session,"
            "不得接上已結束的那一個".format(session_id, row["status"]))
    return row


def observe(store, session_id, kind, title, body="", file_paths=(),
            commit_sha=None, evidence=(), fact=None, decision=None, skill=None,
            knowledge=None, confidence=None, now=None, repo_root=None):
    """記一次實作期觀察。高訊號才會變成候選;低訊號只留本機。

    回傳 dict:`signal` / `candidate_id`(低訊號為 None)/ `event_id` / `reasons`。
    """
    row = require_open(store, session_id)
    now = now or store_mod.utc_now()
    target_kind, payload, signal_kind = _shape(
        kind, title, body, fact, decision, skill, knowledge)
    if target_kind == "fact":
        # 在**登記候選之前**驗證,不是等到固化才發現 ——
        # 讓不合格的宣稱一開始就進不了系統。
        validate_fact_evidence(repo_root or _repo_root_of(store), payload)

    verdict = signal.gate(signal_kind, title, body)

    if verdict["signal"] != signal.HIGH:
        # 低訊號**不是錯誤**,是正常的多數。留本機、可稽核、不進 Git。
        event_id = store.add_event(
            kind, title, body, occurred_at=now, branch=row["branch"],
            commit_sha=commit_sha, session_id=session_id,
            signal=verdict["signal"], file_paths=list(file_paths),
            source_type="runtime_evidence")
        return {"signal": verdict["signal"], "candidate_id": None,
                "event_id": event_id, "reasons": verdict["reasons"]}

    payload.update(_provenance(row, session_id, now, file_paths, commit_sha,
                               evidence, confidence))
    if target_kind == "event":
        # 事件本身就是那筆記憶:先落一筆本機事件,並把 id 交給 consolidate 重用。
        # 少了這一步,同一個觀察會在本機與 durable 各留一筆,檢索時同一件事出現
        # 兩次(smoke test 實際看到)。
        event_id = store.add_event(
            kind, title, body, occurred_at=now, branch=row["branch"],
            commit_sha=commit_sha, session_id=session_id, signal=signal.HIGH,
            file_paths=list(file_paths), source_type="runtime_evidence")
        payload["event_id"] = event_id
    else:
        # 結構化觀察(fact/decision/skill/knowledge)的記錄就是候選本身 ——
        # 再記一筆「觀察日誌」事件只會讓同一件事在檢索裡出現兩次。
        event_id = None
    payload.setdefault("title", title)
    payload.setdefault("body", body)
    candidate_id = store.add_candidate(
        session_id, target_kind, payload, _authority_for(row["mode"], target_kind),
        sensitive=bool(signal.scan_sensitive("\n".join([title, body]))),
        note="implementation observe", now=now)
    # implementation 模式的「確認」是**證據存在**(commit / 檔案 / 指紋),
    # 不是第二次人工點頭 —— 但 domain 知識例外,見 _shape 的強制降級。
    store.set_candidate_status(candidate_id, "CONFIRMED", now=now)
    return {"signal": signal.HIGH, "candidate_id": candidate_id,
            "event_id": event_id, "reasons": []}


def _repo_root_of(store):
    """從已註冊的 workspace 反推 repo root(observe 沒帶 repo_root 時)。"""
    rows = store.workspaces()
    for row in rows:
        if os.path.isdir(row["local_path"]):
            return row["local_path"]
    raise SessionError(
        "無法判定 repo root:請傳 repo_root,或先跑 dev-setup 註冊 workspace")


def _shape(kind, title, body, fact, decision, skill, knowledge):
    """把 observe 的參數收斂成 (candidate target_kind, payload, signal kind)。"""
    if kind == "fact" or fact is not None:
        payload = dict(fact or {})
        for required in ("entity_type", "entity_key", "fact_key", "value"):
            if not payload.get(required):
                raise SessionError("fact 觀察缺欄位:{0}".format(required))
        deps = list(payload.get("dependencies") or ())
        payload["dependencies"] = deps
        payload.setdefault("status",
                           truth.VERIFIED if deps else truth.CANDIDATE)
        payload.setdefault("source_type", "current_code")
        return "fact", payload, "architecture_change"
    if kind == "decision" or decision is not None:
        payload = dict(decision or {})
        if not payload.get("key"):
            raise SessionError("decision 觀察缺 key")
        return "decision", payload, "design_decision"
    if kind == "skill" or skill is not None:
        payload = dict(skill or {})
        if not payload.get("key"):
            raise SessionError("skill 觀察缺 key")
        return "skill", payload, "verified_workflow"
    if kind == "knowledge" or knowledge is not None:
        payload = dict(knowledge or {})
        knowledge_kind = payload.pop("kind", "domain")
        if not payload.get("key"):
            raise SessionError("knowledge 觀察缺 key")
        # **不自動 promote 使用者沒確認的 domain truth**:從程式碼推出來的語意
        # 一律 CANDIDATE + code_inference。要升級成已確認,走 dev-talk 讓人點頭。
        payload["status"] = truth.CANDIDATE
        return knowledge_kind, payload, "domain_clarification"
    return "event", {"kind": kind}, kind


def _authority_for(mode, target_kind):
    if mode == IMPLEMENTATION:
        return "current_code" if target_kind != "decision" \
            else "explicit_discussion"
    return "user_confirmed"


def _provenance(row, session_id, now, file_paths, commit_sha, evidence,
                confidence):
    """候選的 provenance —— 沒有它,記憶在別台機器上等於傳聞。"""
    provenance = {
        "session_id": session_id,
        "feature_slug": row["feature_slug"],
        "branch": row["branch"],
        "commit_sha": commit_sha or row["head_sha"],
        "occurred_at": now,
        "paths": list(file_paths),
        "evidence": [dict(sorted(item.items())) for item in evidence],
    }
    if confidence is not None:
        provenance["confidence"] = confidence
    return provenance


def validate_fact_evidence(repo_root, payload):
    """VERIFIED 的 implementation fact 必須有**可重新驗證**的依據。

    不能產「VERIFIED 但沒有任何驗證依據」的 fact:那種 fact 在查詢時只能被誠實
    降級成 CANDIDATE(見 truth.resolve_current),等於宣稱驗過卻驗不了。
    """
    if payload.get("status") != truth.VERIFIED:
        return
    deps = payload.get("dependencies") or []
    if not deps:
        raise SessionError(
            "fact 標成 VERIFIED 但沒有任何 dependency —— 無從重新驗證。"
            "要嘛給依賴檔,要嘛標成 CANDIDATE")
    missing = [dep for dep in deps
               if not os.path.isfile(os.path.join(repo_root, dep))]
    if missing:
        raise SessionError(
            "fact 標成 VERIFIED 但依賴檔不存在於當前 checkout:{0}".format(
                ", ".join(missing)))


def checkpoint(store, repo_root, session_id, now=None):
    """固化本 session 已確認的候選(唯一 durable 寫入時機)。

    沒有高訊號時合法回 `promoted: 0` —— **不硬產生一筆「本次完成」**。
    那種紀錄沒有資訊量,只會把 `.dev-flow/` 稀釋成沒人讀的流水帳。
    """
    store.session(session_id)      # 不存在就讓呼叫端知道
    result = sync.consolidate(repo_root, store, session_id, now=now)
    result["still_pending"] = [
        {"candidate_id": row["candidate_id"], "target_kind": row["target_kind"],
         "title": row["payload"].get("title", "")}
        for row in store.candidates(session_id, statuses=("PENDING",))]
    return result


def end(store, repo_root, session_id, now=None):
    result = checkpoint(store, repo_root, session_id, now=now)
    store.end_session(session_id, CLOSED, now=now)
    result["session_status"] = CLOSED
    return result


def abort(store, session_id, reason="", now=None):
    """中止:狀態必須看得出來是 ABORTED,**不得默默當成完成**。"""
    store.end_session(session_id, ABORTED, now=now)
    return {"session_id": session_id, "status": ABORTED, "reason": reason}


def status(store, session_id):
    row = store.session(session_id)
    if row is None:
        raise SessionError("session 不存在:{0}".format(session_id))
    counts = {}
    for state in ("PENDING", "CONFIRMED", "REJECTED", "CONSOLIDATED",
                  "LOCAL_ONLY"):
        counts[state] = len(store.candidates(session_id, statuses=(state,)))
    events = store.conn.execute(
        "SELECT signal, COUNT(*) FROM events WHERE session_id=? GROUP BY signal",
        (session_id,)).fetchall()
    by_signal = {r[0]: r[1] for r in events}
    return {
        "session": dict(row),
        "turns": len(store.turns(session_id)),
        "candidates": counts,
        "high_signal_observations": by_signal.get(signal.HIGH, 0),
        "low_signal_observations": by_signal.get(signal.LOW, 0),
    }


def open_sessions(store, mode=None):
    rows = store.sessions(status=OPEN, limit=50)
    if mode:
        rows = [r for r in rows if r["mode"] == mode]
    return rows
