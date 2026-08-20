"""durable ⇄ local 的兩個方向。

    rebuild_local()   .dev-flow/  ──→  local SQLite index      (clone 後、砍 DB 後)
    consolidate()     local candidates ──→ .dev-flow/          (checkpoint / session end)

**方向不對稱是刻意的**:
- rebuild 是「durable 是正本,local 是鏡射」——所以它只清 durable=1 的鏡射列,
  legacy 與 local-only 的資料一律留著(§29:legacy 資料不得被破壞)。
- consolidate 是「local 是草稿,durable 要付代價」——所以它逐筆過 Signal Gate 與
  敏感守衛,只有全過的才寫進 Git。這是 durable memory 的**唯一寫入時機**:
  不在對話中每說一句話就把 repository 弄 dirty(§17)。
"""
import json

from . import durable, ids, signal, store as store_mod

_FACT_STATUS_DURABLE = {"VERIFIED", "CONFLICT", "SUPERSEDED", "UNKNOWN", "STALE"}


# ─────────────────────────── durable → local ────────────────────────────────
def rebuild_local(repo_root, store, embedder=None):
    """從 `.dev-flow/` 重建 local index。回傳每一類的筆數(dev-setup 直接回報)。

    這支就是 §13「clone 到另一台電腦」的實作:project.yaml 給 project_id,
    其餘 durable 檔給內容,local SQLite/FTS/embedding 全部重算。
    """
    store.clear_durable_mirror()
    store.clear_index()
    counts = {"facts": 0, "knowledge": 0, "decisions": 0, "skills": 0,
              "events": 0, "entities": 0}

    for state in durable.iter_states(repo_root):
        counts["entities"] += 1
        for fact in state.get("facts") or []:
            store.upsert_fact({
                "entity_type": state["entity_type"],
                "entity_key": state["entity_key"],
                "fact_key": fact["fact_key"],
                "value": fact["value"],
                "status": fact.get("status", "CANDIDATE"),
                "confidence": fact.get("confidence", 0.0),
                "effective_at": fact.get("effective_at"),
                "recorded_at": fact.get("recorded_at") or store_mod.utc_now(),
                "superseded_at": fact.get("superseded_at"),
                "superseded_by": fact.get("superseded_by"),
                "source_type": fact.get("source_type"),
                "source_ref": fact.get("source_ref"),
                "source_commit": fact.get("source_commit"),
                "verified_at": fact.get("verified_at"),
                "verified_commit": fact.get("verified_commit"),
                "verification_count": fact.get("verification_count", 0),
                "contradiction_count": fact.get("contradiction_count", 0),
                "dependencies": fact.get("dependencies") or [],
                "fingerprints": fact.get("fingerprints") or {},
                "durable": True,
            })
            counts["facts"] += 1

    for record in durable.iter_knowledge(repo_root):
        store.upsert_knowledge({
            "kind": record["kind"], "key": record["key"],
            "title": record["title"], "body": record.get("body", ""),
            "authority": record["authority"],
            "status": record.get("status", "CANDIDATE"),
            "confidence": record.get("confidence", 0.0),
            "recorded_at": record.get("recorded_at") or store_mod.utc_now(),
            "superseded_at": record.get("superseded_at"),
            "superseded_by": record.get("superseded_by"),
            "evidence": record.get("evidence") or [],
            "conflicts": record.get("conflicts") or [],
            "implemented": record.get("implemented"),
            "durable": True,
        })
        counts["knowledge"] += 1

    for record in durable.iter_decisions(repo_root):
        store.upsert_decision({
            "key": record["key"], "title": record.get("title", record["key"]),
            "decision": record.get("decision", ""),
            "alternatives": record.get("alternatives", ""),
            "reason": record.get("reason", ""),
            "tradeoff": record.get("tradeoff", ""),
            "status": record.get("status", "ACCEPTED"),
            "decided_at": record.get("decided_at"),
            "recorded_at": record.get("decided_at") or store_mod.utc_now(),
            "supersedes": record.get("supersedes"),
            "evidence": record.get("evidence") or [],
            "durable": True,
        })
        counts["decisions"] += 1

    for record in durable.iter_skills(repo_root):
        store.upsert_skill({
            "key": record["key"], "title": record["title"],
            "steps": record.get("steps") or [],
            "preconditions": record.get("preconditions", ""),
            "verification": record.get("verification", ""),
            "status": record.get("status", "CANDIDATE"),
            "success_count": record.get("success_count", 0),
            "failure_count": record.get("failure_count", 0),
            "recorded_at": record.get("recorded_at") or store_mod.utc_now(),
            "evidence": record.get("evidence") or [],
            "durable": True,
        })
        counts["skills"] += 1

    for record in durable.iter_events(repo_root):
        store.add_event(
            record.get("kind", "important_discovery"),
            record.get("title", ""), record.get("body", ""),
            occurred_at=record.get("occurred_at"),
            branch=record.get("branch"), commit_sha=record.get("commit_sha"),
            session_id=record.get("session_id"),
            signal=record.get("signal", "high"),
            file_paths=record.get("paths") or [],
            source_type=record.get("source_type"),
            source_ref=record.get("source_ref"),
            durable=True, durable_ref=record.get("durable_ref"),
            event_id=(record.get("event_id")
                      if ids.is_valid_id("event", record.get("event_id"))
                      else None))
        counts["events"] += 1

    if embedder is not None:
        counts["embeddings"] = embedder.reindex(store)
    return counts


# ─────────────────────────── local → durable ────────────────────────────────
def promote_entity_facts(repo_root, store, entity_type, entity_key):
    """把某個 entity 目前的 durable-eligible facts 整檔寫回 `.dev-flow/`。

    整檔寫回(而不是 append 一筆)是因為 supersede 語意住在整組 fact 上:
    只寫新的那筆,舊的 VERIFIED 會留在檔裡看起來也還有效。
    """
    facts = [f for f in store.facts(entity_type=entity_type,
                                    entity_key=entity_key, limit=1000)
             if f["status"] in _FACT_STATUS_DURABLE]
    for fact in facts:
        fact["dependencies"] = json.loads(fact["dependencies_json"])
        fact["fingerprints"] = json.loads(fact["fingerprints_json"])
    if not facts:
        return None
    durable.ensure_layout(repo_root, [durable.STATE_DIR])
    path = durable.write_state(repo_root, entity_type, entity_key, facts)
    with store.conn:
        store.conn.execute(
            "UPDATE facts SET durable=1 WHERE project_id=? AND entity_type=?"
            " AND entity_key=? AND status IN ({0})".format(
                ",".join("?" for _ in _FACT_STATUS_DURABLE)),
            [store.project_id, entity_type, entity_key, *sorted(_FACT_STATUS_DURABLE)])
    return path


def consolidate(repo_root, store, session_id=None, now=None):
    """把已確認的候選知識固化進 `.dev-flow/`(durable 的唯一寫入時機)。

    回傳 dict:written(檔案清單)/ promoted(筆數)/ rejected(逐筆理由)。
    被拒絕的候選**不會消失** —— 它留在 local,狀態改成 LOCAL_ONLY 並記下理由,
    這樣「為什麼這條沒進 Git」下次還查得到(§25 的同一種誠實)。
    """
    now = now or store_mod.utc_now()
    written = []
    promoted = 0
    rejected = []
    entities_touched = set()
    event_records = []

    for candidate in store.candidates(session_id=session_id,
                                      statuses=("CONFIRMED",)):
        payload = candidate["payload"]
        kind = candidate["target_kind"]
        title = payload.get("title", "")
        body = payload.get("body", "")
        verdict = signal.gate(
            _signal_kind_for(kind), title, body,
            extra_texts=[json.dumps(payload, ensure_ascii=False)])
        if not verdict["durable_allowed"]:
            store.set_candidate_status(
                candidate["candidate_id"], "LOCAL_ONLY",
                note="; ".join(verdict["reasons"]), now=now)
            rejected.append({"candidate_id": candidate["candidate_id"],
                             "target_kind": kind,
                             "reasons": verdict["reasons"]})
            continue

        if kind in durable.KNOWLEDGE_DIRS:
            knowledge_id = store.upsert_knowledge({
                "kind": kind, "key": payload["key"], "title": title,
                "body": body, "authority": candidate["authority"],
                "status": payload.get("status", "CONFIRMED"),
                "confidence": payload.get("confidence", 0.8),
                "recorded_at": now,
                "evidence": payload.get("evidence") or [],
                "conflicts": payload.get("conflicts") or [],
                "implemented": payload.get("implemented"),
                "durable": True})
            record = store.knowledge_row(knowledge_id)
            written.append(durable.write_knowledge(repo_root, {
                "kind": kind, "key": record["key"], "title": record["title"],
                "body": record["body"], "authority": record["authority"],
                "status": record["status"], "confidence": record["confidence"],
                "recorded_at": record["recorded_at"],
                "evidence": json.loads(record["evidence_json"]),
                "conflicts": json.loads(record["conflicts_json"]),
                "implemented": (None if record["implemented"] is None
                                else bool(record["implemented"]))}))
        elif kind == "decision":
            decision_id = store.upsert_decision({
                "key": payload["key"], "title": title,
                "decision": payload.get("decision", ""),
                "alternatives": payload.get("alternatives", ""),
                "reason": payload.get("reason", ""),
                "tradeoff": payload.get("tradeoff", ""),
                "status": payload.get("status", "ACCEPTED"),
                "decided_at": payload.get("decided_at") or now,
                "recorded_at": now,
                "supersedes": payload.get("supersedes"),
                "evidence": payload.get("evidence") or [],
                "durable": True})
            written.append(durable.write_decision(repo_root, {
                "key": payload["key"], "title": title,
                "decision": payload.get("decision", ""),
                "alternatives": payload.get("alternatives", ""),
                "reason": payload.get("reason", ""),
                "tradeoff": payload.get("tradeoff", ""),
                "status": payload.get("status", "ACCEPTED"),
                "decided_at": payload.get("decided_at") or now,
                "decision_id": decision_id,
                "supersedes": payload.get("supersedes"),
                "evidence": payload.get("evidence") or []}))
        elif kind == "skill":
            store.upsert_skill({
                "key": payload["key"], "title": title,
                "steps": payload.get("steps") or [],
                "preconditions": payload.get("preconditions", ""),
                "verification": payload.get("verification", ""),
                "status": payload.get("status", "CANDIDATE"),
                "recorded_at": now,
                "evidence": payload.get("evidence") or [], "durable": True})
            written.append(durable.write_skill(repo_root, {
                "key": payload["key"], "title": title,
                "steps": payload.get("steps") or [],
                "preconditions": payload.get("preconditions", ""),
                "verification": payload.get("verification", ""),
                "status": payload.get("status", "CANDIDATE"),
                "recorded_at": now,
                "evidence": payload.get("evidence") or []}))
        elif kind == "fact":
            store.upsert_fact({
                "entity_type": payload["entity_type"],
                "entity_key": payload["entity_key"],
                "fact_key": payload["fact_key"], "value": payload["value"],
                "status": payload.get("status", "CANDIDATE"),
                "confidence": payload.get("confidence", 0.5),
                "recorded_at": now,
                "source_type": payload.get("source_type"),
                "source_ref": payload.get("source_ref"),
                "dependencies": payload.get("dependencies") or [],
                "fingerprints": payload.get("fingerprints") or {}})
            entities_touched.add((payload["entity_type"], payload["entity_key"]))
        elif kind == "event":
            event_id = store.add_event(
                payload.get("kind", "important_discovery"), title, body,
                occurred_at=payload.get("occurred_at") or now,
                branch=payload.get("branch"),
                commit_sha=payload.get("commit_sha"),
                session_id=candidate["session_id"], signal=signal.HIGH,
                file_paths=payload.get("paths") or [],
                source_type=payload.get("source_type"),
                source_ref=payload.get("source_ref"), durable=True)
            event_records.append({
                "event_id": event_id, "kind": payload.get(
                    "kind", "important_discovery"),
                "title": title, "body": body,
                "occurred_at": payload.get("occurred_at") or now,
                "branch": payload.get("branch"),
                "commit_sha": payload.get("commit_sha"),
                "session_id": candidate["session_id"], "signal": signal.HIGH,
                "paths": payload.get("paths") or []})
        else:
            store.set_candidate_status(
                candidate["candidate_id"], "LOCAL_ONLY",
                note="未知的 target_kind:{0}(不猜、不寫進 Git)".format(kind),
                now=now)
            rejected.append({"candidate_id": candidate["candidate_id"],
                             "target_kind": kind,
                             "reasons": ["未知的 target_kind"]})
            continue

        store.set_candidate_status(candidate["candidate_id"], "CONSOLIDATED",
                                  now=now)
        promoted += 1

    for entity_type, entity_key in sorted(entities_touched):
        path = promote_entity_facts(repo_root, store, entity_type, entity_key)
        if path:
            written.append(path)

    if event_records:
        written.extend(durable.append_events(
            repo_root, session_id or "consolidation", event_records))

    return {"written": sorted(set(written)), "promoted": promoted,
            "rejected": rejected}


def _signal_kind_for(target_kind):
    """候選類型 → Signal Gate 的事件種類。

    domain/intent/invariant/decision/skill 這幾類本質上就是高訊號(它們是人確認過
    的知識,不是 tool 雜訊);fact/event 沿用 payload 自己的 kind 由呼叫端決定。
    """
    return {
        "domain": "domain_clarification",
        "invariant": "business_rule",
        "entity": "domain_clarification",
        "relationship": "domain_clarification",
        "intent": "design_decision",
        "decision": "design_decision",
        "skill": "verified_workflow",
        "fact": "architecture_change",
        "event": "important_discovery",
    }.get(target_kind, target_kind)
