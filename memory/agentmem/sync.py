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
import os

from . import durable, ids, lineage, signal, store as store_mod

# CANDIDATE 也進 durable:狀態欄本來就會明寫,查詢時它會被當成
# NEEDS_VERIFICATION。把它擋在外面反而製造一個洞 —— 「觀察到但還沒驗證」
# 的事實會完全不留痕跡,另一台機器連「有人看過這件事」都不知道。
_FACT_STATUS_DURABLE = {"VERIFIED", "CANDIDATE", "CONFLICT", "SUPERSEDED",
                        "UNKNOWN", "STALE"}


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

    回傳 `(path, rejected, written_ids)`;沒有可寫的 fact 時 path 為 None。
    `written_ids` 是**真的落進檔案**的那些 fact_id —— 呼叫端要靠它決定哪一筆
    候選可以前進到 CONSOLIDATED。回一個 path 不夠:整檔寫回會逐筆過 gate,
    「檔案寫成功了」與「我這一筆在裡面」是兩件事。

    **不得設筆數視窗。** 整檔取代 + 撈前 N 筆 = 刪掉視窗外的那些:它們上一輪
    已經在檔裡也已經 `durable=1`,這一輪的取代把它們拿掉,而 local 那幾列仍然
    聲稱「我就是檔裡的那份」。`durable-check` 於是判 PASS 在一個不完整的鏡射
    上,砍掉 local 重建之後那些 fact 永遠回不來。status 過濾也必須下推到 SQL
    —— 套在視窗之後的話,夠多的 SUPERSEDED 鄰居就能把唯一的現況擠出去。

    **每一筆都要重過 Signal Gate。** 候選的 gate 檢查的是「那一筆候選」,
    而 fact 進 local DB 的路不只候選一條 —— `truth.reverify()`(公開 CLI
    `verify --observed`)直接寫值。整檔寫回時,一筆乾淨的候選會把同一個 entity
    裡未經檢查的鄰居一起帶進 Git。這裡是最後一個能攔的地方,而 durable 寫入
    不可逆(進了 commit 就在歷史裡)。
    """
    facts = store.facts(entity_type=entity_type, entity_key=entity_key,
                        statuses=sorted(_FACT_STATUS_DURABLE), limit=None)
    writable = []
    rejected = []
    for fact in facts:
        fact["dependencies"] = json.loads(fact["dependencies_json"])
        fact["fingerprints"] = json.loads(fact["fingerprints_json"])
        verdict = signal.gate(
            "architecture_change", fact["fact_key"], str(fact["value"]),
            extra_texts=[json.dumps(
                {k: fact[k] for k in ("value", "source_ref", "fact_key")},
                ensure_ascii=False)])
        if verdict["durable_allowed"]:
            writable.append(fact)
        else:
            # 只擋這一筆,不連坐:其餘 fact 照樣固化。被擋的留在 local
            # (durable=0)—— 沒寫進去的東西不得被標成已耐久。
            rejected.append({"candidate_id": None, "target_kind": "fact",
                             "fact_id": fact["fact_id"],
                             "reasons": verdict["reasons"]})
    if not writable:
        return None, rejected, set()
    durable.ensure_layout(repo_root, [durable.STATE_DIR])
    path = durable.write_state(repo_root, entity_type, entity_key, writable)
    with store.conn:
        store.conn.executemany(
            "UPDATE facts SET durable=1 WHERE fact_id=?",
            [(fact["fact_id"],) for fact in writable])
    return path, rejected, {fact["fact_id"] for fact in writable}


def _derived_id(kind, candidate_id):
    """從 candidate 推導 durable 實體 id —— 同一個候選重跑一定得到同一個 id。

    retry 安全需要它。durable 寫入失敗後候選會留在 CONFIRMED 等下一次
    checkpoint,而每次都 `ids.new_id()` 的話補寫會產生**第二筆**:歷史從「缺」
    變成「重複」,而重複比缺更難發現(兩筆都長得像真的)。

    ULID body 的字元集在各 kind 之間相同,所以換前綴就是合法 id;推導不出合法
    id(candidate_id 不是這套格式)才退回隨機 —— 不猜、不硬湊。
    """
    body = candidate_id.split("_", 1)[1] if "_" in (candidate_id or "") else ""
    derived = ids.KINDS[kind] + "_" + body
    return derived if ids.is_valid_id(kind, derived) else ids.new_id(kind)


def consolidate(repo_root, store, session_id=None, now=None):
    """把已確認的候選知識固化進 `.dev-flow/`(durable 的唯一寫入時機)。

    回傳 dict:written(檔案清單)/ promoted(筆數)/ rejected(逐筆理由)。
    被拒絕的候選**不會消失** —— 它留在 local,狀態改成 LOCAL_ONLY 並記下理由,
    這樣「為什麼這條沒進 Git」下次還查得到(§25 的同一種誠實)。

    **候選狀態只在 durable 寫入成功之後才前進。** knowledge/decision/skill 的
    durable 寫入就在迴圈裡(寫檔在前、動 local 在後);fact 與 event 的寫入
    發生在迴圈**之後**(fact 要整個 entity 一起寫回、event 要整批 append),
    所以這兩類的候選在迴圈裡只登記、不結案 —— 提早結案的話寫檔失敗就再也
    看不到它,`.dev-flow/` 永遠缺那一筆,而 local 自洽、沒有任何測試會紅。
    """
    now = now or store_mod.utc_now()
    written = []
    promoted = 0
    rejected = []
    entities_touched = set()
    # (candidate_id, fact_id) / (candidate_id, event record):等 durable 寫入成功
    fact_candidates = {}
    event_candidates = []
    pending_revisions = []

    for candidate in store.candidates(session_id=session_id,
                                      statuses=("CONFIRMED",)):
        payload = candidate["payload"]
        kind = candidate["target_kind"]
        # 最後一道防線:候選必須掛在一個**真實存在且還開著**的 session 上。
        # devtalk/session 層已經擋過「沒有 start 就 propose」,但 store 是內部
        # API,直接呼叫它塞候選會繞過那一層 —— durable writer 是最後有機會
        # 攔下來的地方,而 durable 寫入是不可逆的(進了 commit 就在歷史裡)。
        #
        # 「存在」不夠:ABORTED 的 session 也存在。abort 的語意是「這一輪不算」,
        # 它的候選還能被固化的話,「中止」就只是一個沒有效力的標籤 ——
        # 而 `session_id=None`(全專案掃)這條路正好會撿到它們。
        owner = store.session(candidate["session_id"])
        if owner is None or owner["status"] != "OPEN":
            reason = ("session {0} 不存在 —— 候選沒有來源可追溯".format(
                candidate["session_id"]) if owner is None
                else "session {0} 已是 {1} —— 已結束的一輪不得再固化".format(
                    candidate["session_id"], owner["status"]))
            store.set_candidate_status(
                candidate["candidate_id"], "LOCAL_ONLY",
                note=reason + ",不予固化", now=now)
            rejected.append({"candidate_id": candidate["candidate_id"],
                             "target_kind": kind, "reasons": [reason]})
            continue
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
            # **寫檔在前,supersede 在後。** 反過來的話,寫檔失敗(磁碟滿 /
            # conflict 標記 / 路徑守衛)會留下一個比沒寫更糟的狀態:local 已經
            # 是新值、durable 還是舊值,而下一次重跑會把「新值 supersede 新值」
            # 記成 lineage —— 真正的 v1 → v2 那一段就永久消失了。
            entry = {
                "kind": kind, "key": payload["key"], "title": title,
                "body": body, "authority": candidate["authority"],
                "status": payload.get("status", "CONFIRMED"),
                "confidence": float(payload.get("confidence", 0.8)),
                "recorded_at": now,
                "evidence": payload.get("evidence") or [],
                "conflicts": payload.get("conflicts") or [],
                "implemented": payload.get("implemented")}
            written.append(durable.write_knowledge(repo_root, entry))
            previous = _supersede_previous_knowledge(store, kind, payload, now)
            knowledge_id = store.upsert_knowledge(dict(entry, durable=True))
            if previous:
                pending_revisions.append(lineage.build_knowledge_revision(
                    kind, payload["key"], previous,
                    dict(entry, knowledge_id=knowledge_id),
                    reason=payload.get("_lineage_reason", "")
                    or payload.get("correction_reason", ""),
                    session_id=candidate["session_id"], occurred_at=now))
        elif kind == "decision":
            # id 先產:durable 檔要記它,而寫檔必須發生在 DB 變更之前(同上)。
            decision_id = ids.new_id("decision")
            entry = {
                "key": payload["key"], "title": title,
                "decision": payload.get("decision", ""),
                "alternatives": payload.get("alternatives", ""),
                "reason": payload.get("reason", ""),
                "tradeoff": payload.get("tradeoff", ""),
                "status": payload.get("status", "ACCEPTED"),
                "decided_at": payload.get("decided_at") or now,
                "decision_id": decision_id,
                "supersedes": payload.get("supersedes"),
                "evidence": payload.get("evidence") or []}
            written.append(durable.write_decision(repo_root, entry))
            previous = _supersede_previous_decision(store, payload["key"], now)
            store.upsert_decision(dict(entry, recorded_at=now, durable=True))
            if previous:
                pending_revisions.append(lineage.build_decision_revision(
                    payload["key"], previous,
                    {"decision_id": decision_id, "title": title,
                     "decision": payload.get("decision", ""),
                     "status": payload.get("status", "ACCEPTED")},
                    reason=payload.get("supersedes_reason", "")
                    or payload.get("correction_reason", ""),
                    session_id=candidate["session_id"], occurred_at=now))
        elif kind == "skill":
            entry = {
                "key": payload["key"], "title": title,
                "steps": payload.get("steps") or [],
                "preconditions": payload.get("preconditions", ""),
                "verification": payload.get("verification", ""),
                "status": payload.get("status", "CANDIDATE"),
                "recorded_at": now,
                "evidence": payload.get("evidence") or []}
            written.append(durable.write_skill(repo_root, entry))
            store.upsert_skill(dict(entry, durable=True))
        elif kind == "fact":
            from . import truth
            dependencies = payload.get("dependencies") or []
            fingerprints = payload.get("fingerprints") or {}
            if dependencies and not fingerprints:
                # 候選只宣告了依賴、沒帶指紋時,在**固化的這一刻**對當前 checkout
                # 現算。少了這一步,fact 會以「VERIFIED 但沒有任何指紋」落地,
                # 查詢時只能降級成 CANDIDATE(無從驗證)—— 等於白宣告了依賴。
                # 現算是正確的基準:consolidation 本來就發生在當前 checkout 上。
                fingerprints = truth.fingerprints_for(repo_root, dependencies)
            verified_commit = (payload.get("verified_commit")
                               or payload.get("commit_sha"))
            record = {
                "entity_type": payload["entity_type"],
                "entity_key": payload["entity_key"],
                "fact_key": payload["fact_key"], "value": payload["value"],
                "status": payload.get("status", "CANDIDATE"),
                "confidence": payload.get("confidence", 0.5),
                "recorded_at": now, "effective_at": now,
                "source_type": payload.get("source_type"),
                "source_ref": payload.get("source_ref"),
                "source_commit": (payload.get("source_commit")
                                  or payload.get("commit_sha")),
                "dependencies": dependencies,
                "fingerprints": fingerprints}
            if record["status"] == truth.VERIFIED:
                record["verified_at"] = now
                record["verified_commit"] = verified_commit
                record["verification_count"] = 1
            # fact_id 由 candidate 推導,不隨機:寫檔失敗後重跑會 UPDATE 同一列,
            # 而不是插入第二筆同義 fact(那會被整檔寫回一起帶進 `.dev-flow/`)。
            record["fact_id"] = _derived_id("fact", candidate["candidate_id"])
            store.upsert_fact(record)
            entities_touched.add((payload["entity_type"], payload["entity_key"]))
            # durable 寫入在迴圈之後(整個 entity 一起寫回)—— 只登記,不結案。
            fact_candidates.setdefault(
                (payload["entity_type"], payload["entity_key"]), []).append(
                    (candidate["candidate_id"], record["fact_id"]))
            continue
        elif kind == "event":
            # observe() 已經落過本機事件時重用它的 id(之後把它升級成 durable),
            # 不另產一筆 —— 否則同一件事在檢索裡會出現兩次。沒有 id 可重用時
            # 從 candidate 推導,理由同 fact:重跑必須補寫同一筆,不是第二筆。
            event_id = (payload.get("event_id")
                        if ids.is_valid_id("event", payload.get("event_id"))
                        else _derived_id("event", candidate["candidate_id"]))
            # **這裡不呼叫 store.add_event。** 它會把 local 列標成 durable=1,
            # 而 `.dev-flow/` 要等迴圈之後的 append_events 才寫 —— 提早標記就是
            # 一句沒有憑據的「已耐久」(指向一個不存在的檔),而且是靜默的。
            # durable record 的欄位一字不加:`append_events` 直接序列化拿到的
            # 每一個 key,多帶欄位就是改了 durable 格式。local 那一筆要用的
            # source_type / source_ref 從 payload 取,不塞進要落檔的 dict。
            event_candidates.append((candidate["candidate_id"], {
                "event_id": event_id, "kind": payload.get(
                    "kind", "important_discovery"),
                "title": title, "body": body,
                "occurred_at": payload.get("occurred_at") or now,
                "branch": payload.get("branch"),
                "commit_sha": payload.get("commit_sha"),
                "session_id": candidate["session_id"], "signal": signal.HIGH,
                "paths": payload.get("paths") or []},
                {"source_type": payload.get("source_type"),
                 "source_ref": payload.get("source_ref")}))
            continue
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

    # 候選不是進 facts 表的唯一一條路,所以 `entities_touched` 不足以決定要
    # 重寫哪些現況檔。`truth.reverify()`(公開 CLI `verify --observed`)直接
    # 改值:它把舊列標 SUPERSEDED、插入新的 VERIFIED 列、記一筆 revision,
    # 但**不建候選** —— 於是這一段之前沒有任何東西會把那個 entity 加進來,
    # `.dev-flow/state/` 的現況檔停在舊值。revision 是歷史,不是現況物化視圖
    # 的替代品:砍掉 SQLite 再 rebuild,現況就退回 v1,而 local 說它 VERIFIED。
    #
    # 判準用 fact 列自己的 `durable` 旗標,不是列舉「有哪些路會改 fact」——
    # 後者要求每次新增寫入路徑的人記得回來改這裡,而忘記是靜默的。
    entities_touched.update(
        store.entities_pending_durable(sorted(_FACT_STATUS_DURABLE)))

    # ── fact 的 durable 寫入(這裡可能拋)→ 才結案 ────────────────────────
    for entity_type, entity_key in sorted(entities_touched):
        path, fact_rejected, written_ids = promote_entity_facts(
            repo_root, store, entity_type, entity_key)
        if path:
            written.append(path)
        rejected.extend(fact_rejected)
        for candidate_id, fact_id in fact_candidates.get(
                (entity_type, entity_key), []):
            if fact_id in written_ids:
                store.set_candidate_status(candidate_id, "CONSOLIDATED",
                                           now=now)
                promoted += 1
            else:
                # 檔案寫成功了,但**這一筆**被逐筆 gate 擋在外面。
                # 沒進 `.dev-flow/` 的候選不得記成已固化。
                store.set_candidate_status(
                    candidate_id, "LOCAL_ONLY",
                    note="durable writer 逐筆檢查未通過 —— 這一筆沒有寫進 "
                         ".dev-flow/,留在本機", now=now)

    # ── revision lineage(P0-3)──────────────────────────────────────────
    # **順序就是這一段的正確性**:pending → 過守衛 → 寫檔 → 才標 durable。
    #
    # 先前的寫法在 `append_events()` 之**前**就 mark_durable,而且不分這一筆
    # 到底有沒有被寫出去。後果有兩種,都是靜默且永久的失憶:
    #   ①被敏感守衛擋掉的 revision 也被標 durable=1 —— 它不再是 pending,
    #     永遠不會再被嘗試,而 `.dev-flow/` 裡從來沒有它。
    #   ②寫檔失敗(磁碟滿 / conflict 標記 / 路徑守衛)時例外往上拋,
    #     但狀態已經前進了 —— 重跑也補不回來。
    #
    # 本輪產生的 revision 也一律先落 pending 表,和 `truth.reverify()` 走同一
    # 條路。否則「用哪條路更正」會決定失敗時救不救得回來:reverify 的有表
    # 撐著,correct() 的只活在記憶體裡,一次例外就消失。
    for revision in pending_revisions:
        lineage.record_pending(store, revision)

    revision_records = []
    flushed_ids = []
    for row in lineage.pending(store, session_id):
        revision = row["payload"]
        verdict = signal.gate(
            revision["kind"], revision["title"], revision["body"],
            extra_texts=[json.dumps(revision, ensure_ascii=False)])
        if not verdict["durable_allowed"]:
            # 留在 pending(durable=0):沒寫進 Git 的東西不得被標成已耐久。
            # 它會在每次 checkpoint 被重新回報 —— 刻意的:一筆永遠固化不了的
            # revision(例如舊值裡有 secret)應該一直看得見,不是被結案。
            rejected.append({"candidate_id": None,
                             "target_kind": revision["kind"],
                             "reasons": verdict["reasons"]})
            continue
        record = dict(revision)
        # event_id 由 revision_id 推導,不隨機 —— 理由同 `_derived_id` 的註解:
        # 寫檔成功而 local 狀態還沒前進時重跑會補寫同一筆,而 durable 去重的
        # 依據是 event_id。每次新產一個 id 等於讓去重永遠對不上:同一次
        # supersede 會在 `.dev-flow/events/` 累積成 N 筆,每筆都聲稱是它。
        record.setdefault("event_id",
                          _derived_id("event", row["revision_id"]))
        revision_records.append(record)
        flushed_ids.append(row["revision_id"])
    event_records = [record for _cid, record, _extra in event_candidates]
    event_records.extend(revision_records)

    # 寫檔在前(這一行可能拋),狀態在後。
    session_key = session_id or "consolidation"
    if event_records:
        written.extend(durable.append_events(
            repo_root, session_key, event_records))

    # 到這裡才算「真的寫進 .dev-flow」——才可以動 local 狀態。
    for candidate_id, record, extra in event_candidates:
        store.add_event(record["kind"], record["title"], record["body"],
                        occurred_at=record["occurred_at"],
                        branch=record.get("branch"),
                        commit_sha=record.get("commit_sha"),
                        session_id=record.get("session_id") or None,
                        signal=signal.HIGH,
                        file_paths=record.get("paths") or [],
                        source_type=extra["source_type"],
                        source_ref=extra["source_ref"], durable=True,
                        event_id=record["event_id"])
        store.set_candidate_status(candidate_id, "CONSOLIDATED", now=now)
        promoted += 1
    for record in revision_records:
        store.add_event(record["kind"], record["title"], record["body"],
                        occurred_at=record["occurred_at"],
                        session_id=record.get("session_id") or None,
                        signal=signal.HIGH, durable=True,
                        source_type="revision",
                        source_ref=record["key"],
                        event_id=record["event_id"])
    for revision_id, record in zip(flushed_ids, revision_records):
        # durable_ref 記**落在哪個檔**:「已耐久」要可稽核,否則它只是一個
        # 沒有人能驗證的布林值。
        lineage.mark_durable(
            store, [revision_id],
            durable_ref=_event_ref(repo_root, session_key, record))

    return {"written": sorted(set(written)), "promoted": promoted,
            "rejected": rejected, "revisions": len(revision_records)}


# ─────────────────────── durable barrier 的機械驗證 ──────────────────────────
UNCOMMITTED = "DURABLE_UNCOMMITTED"
UNPUSHED = "DURABLE_UNPUSHED"
OPEN_SESSION = "SESSION_STILL_OPEN"
PENDING_REVISION = "REVISION_STILL_PENDING"
PENDING_FACT = "FACT_STATE_NOT_REWRITTEN"
REMOTE_UNVERIFIED = "DURABLE_REMOTE_UNVERIFIED"
REMOTE_LOCAL = "DURABLE_REMOTE_IS_LOCAL"
REMOTE_ENDPOINT_LOCAL = "DURABLE_REMOTE_ENDPOINT_IS_LOCAL"


def _remote_url(repo_root, remote):
    """這個 remote **實際會連上去**的 URL。

    走 `ls-remote --get-url` 而不是讀 `remote.<name>.url`:後者是設定檔裡的
    字面值,而 `url.<base>.insteadOf` 會在連線時把它改寫掉。只看字面值的話,
    一個實際只寫到本機目錄的 remote 可以掛著網路形狀的名字通過判定。
    `--get-url` 不連網,它只做改寫後的解析。
    """
    from . import identity
    return identity._git(repo_root, "ls-remote", "--get-url", remote)


def _observe_remote(repo_root, branch):
    """向**遠端本身**問那個 branch 現在指到哪。回 `(sha, code, message)`。

    不用 `rev-parse origin/<branch>`:那是本機快取,另一台機器 force-push 或
    刪掉 branch 之後它仍然指著我的 commit —— 這一關會替一個伺服器上已經不存在
    的 commit 背書,而那正是它唯一要防的事。

    不用 `fetch`:這是一支判定,不該順手改本機的 ref(判定改變被判定的狀態,
    下一次判定就不是獨立的)。`ls-remote` 是唯讀的,而且問的是伺服器。

    remote 與 ref 從 `branch.<name>.remote` / `.merge` 讀,不從 `origin/xxx`
    這個字串切 —— branch 名字本身可以有 `/`,切錯會問錯 ref 然後判 FAIL。

    連得上**不等於**在別台機器上:remote 可以是 `/Volumes/backup/mirror.git`。
    所以 URL 先過 `identity.remote_is_offmachine()`,判不出是別台機器就不給
    證據 —— 見那支的註解。訊息裡只提 remote **名字**,不提 URL:URL 可能帶
    token,而這段輸出會被貼進紀錄。

    形狀判定只看 URL 字面(host 長得像不像本機)——一個具名的非 loopback
    主機仍然可能解析回這台機器:`remote.example.test` 被 `/etc/hosts` 或
    內網 DNS 重映到 `127.0.0.1`、或這台機器自己的另一個介面,`ls-remote`
    照樣回報正確的 SHA。所以形狀過關之後還要再解析 host 拿位址證據
    (`identity.resolve_host_ips` + `identity.ip_is_offmachine`);解析不到
    一律 fail closed(`REMOTE_UNVERIFIED`),不得因為問不到而放行。
    `identity._local_machine_ips()` 本身是 best-effort、可能全部探測失敗
    回空集合 —— 這裡明確先查一次、空集合本身就 fail closed 到
    `REMOTE_UNVERIFIED`,不把它當成「這台機器沒有任何位址」直接丟給
    `ip_is_offmachine` 比對(那樣任何位址都會被誤判成離開這台機器)。
    SSH config 的 Host 別名重映(`~/.ssh/config` 的 `HostName`)不在這一關
    的偵測範圍內 —— 那需要額外呼叫 `ssh -G` 才能拿到 SSH 實際會解析的
    host,這裡沒有做,是已知的殘留缺口,不是沒注意到。
    """
    from . import identity
    remote = identity._git(repo_root, "config",
                           "branch.{0}.remote".format(branch))
    merge = identity._git(repo_root, "config",
                          "branch.{0}.merge".format(branch))
    if not remote or not merge:
        return (None, REMOTE_UNVERIFIED,
                "讀不到 branch.{0} 的 remote/merge 設定".format(branch))
    url = _remote_url(repo_root, remote)
    if not url:
        return (None, REMOTE_UNVERIFIED,
                "讀不到 remote {0} 的 URL".format(remote))
    if not identity.remote_is_offmachine(url):
        return (None, REMOTE_LOCAL,
                "remote {0} 指向這台機器,或無法判定它在別台機器上 —— "
                "本機的 bare repo / file:// / localhost 跟工作樹一起壞掉,"
                "它不是「記憶離開這台機器」的證據".format(remote))
    host = identity._parse_host(url)
    ips = identity.resolve_host_ips(host) if host else None
    if not ips:
        return (None, REMOTE_UNVERIFIED,
                "remote {0} 的主機名解析不到位址 —— 分不出來不得當成"
                "離開這台機器的證據".format(remote))
    local_ips = identity._local_machine_ips()
    if not local_ips:
        return (None, REMOTE_UNVERIFIED,
                "這台機器自己的介面位址列表拿不到(best-effort 探測全部"
                "失敗)—— 分不出來解析到的位址是不是這台機器自己,不得"
                "因為查不到本機介面就當成離開這台機器的證據")
    if not all(identity.ip_is_offmachine(ip, local_ips=local_ips)
               for ip in ips):
        return (None, REMOTE_ENDPOINT_LOCAL,
                "remote {0} 的主機名解析後是這台機器自己(loopback / "
                "link-local / 本機介面位址)—— 主機名長得像別台機器,"
                "實際解析到的卻是自己".format(remote))
    raw = identity._git_raw(repo_root, "ls-remote", "--exit-code",
                            remote, merge)
    if raw is None:
        return (None, REMOTE_UNVERIFIED,
                "問不到遠端 {0} 的 {1}(網路不通、無權限、或該 ref 不存在)"
                .format(remote, merge))
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[1].strip() == merge:
            return parts[0].strip(), None, None
    return (None, REMOTE_UNVERIFIED,
            "遠端 {0} 沒有回報 {1}".format(remote, merge))


def durable_check(repo_root, store, local_only=False):
    """「記憶真的離開這台機器了嗎?」—— Stage 6 收尾的最後一道機械驗證。

    `checkpoint` 成功只代表**檔案寫進工作樹**。工作樹不是耐久性:
    沒 commit 就 `git checkout` 會掉,沒 push 就只有這台機器有。
    Stage 6 的收尾順序(萃取 → checkpoint → memory commit → 最終 push →
    remote HEAD 驗證)之所以需要這一支,是因為前面每一步都可能「看起來做完了」:
    checkpoint 回 promoted: 3 而 `.dev-flow/` 從來沒被 commit,是最容易發生的
    一種,而它不會讓任何測試變紅。

    回傳 dict:verdict(PASS/FAIL)+ 逐項證據。判定一律**明說理由**,
    不回一個沒人能複驗的布林值。

    `local_only=True` 時不問遠端,只比對本機追蹤 ref,並且回傳
    `remote_observed=False` —— 離線時可以放行,但不得聲稱驗過遠端。
    """
    from . import identity
    problems = []
    rel_root = os.path.relpath(durable.root(repo_root), repo_root)
    rel_root = rel_root.replace(os.sep, "/")

    # ①durable 樹有沒有未 commit 的改動(含未追蹤檔)
    raw = identity._git_raw(repo_root, "status", "--porcelain=v1", "-z",
                            "-uall", "--", rel_root)
    uncommitted = []
    if raw is None:
        problems.append("git status 失敗 —— 無法判定 durable 樹是否已 commit")
    else:
        changed, unparsed = identity.parse_porcelain_z(raw)
        uncommitted = sorted(changed)
        if unparsed:
            problems.append(
                "git status 有 {0} 筆無法解析 —— 不猜,視為未判定".format(
                    len(unparsed)))
    if uncommitted:
        problems.append(
            "{0}:{1} 個 durable 檔還沒 commit —— 記憶只在工作樹裡,"
            "checkout 就沒了".format(UNCOMMITTED, len(uncommitted)))

    # ②HEAD 有沒有真的到 remote —— 問遠端本身,不問本機的追蹤 ref
    head = identity._git(repo_root, "rev-parse", "HEAD")
    upstream = identity._git(repo_root, "rev-parse", "--abbrev-ref",
                             "--symbolic-full-name", "@{upstream}")
    branch = identity._git(repo_root, "symbolic-ref", "--short", "HEAD")
    remote_observed = False
    remote_head = None
    if upstream is None:
        problems.append(
            "{0}:這個分支沒有 upstream —— 無法驗證記憶是否離開本機".format(
                UNPUSHED))
    elif local_only:
        # 明確要求只驗本機。追蹤 ref 可能是舊的,所以**不聲稱**觀察過遠端。
        remote_head = identity._git(repo_root, "rev-parse", upstream)
    else:
        remote_head, code, error = _observe_remote(repo_root, branch or "")
        if error:
            problems.append(
                "{0}:{1} —— 沒有證據就是沒有證據,不得因為問不到而放行"
                "(離線或刻意只用本機 remote 時要放行請明確用 --local-only,"
                "它不會聲稱驗過遠端)".format(code, error))
        else:
            remote_observed = True
    pushed = bool(head and remote_head and head == remote_head)
    if upstream is not None and remote_head and not pushed:
        problems.append(
            "{0}:HEAD 與遠端的 {1} 不同 —— push 沒做、沒成功,或被別人改掉了"
            .format(UNPUSHED, upstream))

    # ③還開著的 session(沒 checkpoint 也沒 abort = 這一輪的記憶懸在半空)
    from . import session as session_mod
    open_sessions = [row["session_id"]
                     for row in session_mod.open_sessions(store)]
    if open_sessions:
        problems.append(
            "{0}:{1} 個 session 還是 OPEN —— 要 checkpoint --end 或 abort".format(
                OPEN_SESSION, len(open_sessions)))

    # ④還沒落地的 revision(修正歷史留在 local 就等於沒有)
    from . import lineage
    pending_revisions = [row["revision_id"] for row in lineage.pending(store)]
    if pending_revisions:
        problems.append(
            "{0}:{1} 筆 revision 還沒寫進 durable —— 修正歷史尚未離開本機".format(
                PENDING_REVISION, len(pending_revisions)))

    # ⑤現況檔還沒重寫的 entity(`verify --observed` 之後忘了 checkpoint)
    # revision pending 與這一項不是同一件事:前者是歷史沒落地,後者是**現況**
    # 沒落地。只檢查前者的話,「revision 寫成功、現況檔沒重寫」會判 PASS。
    pending_facts = store.entities_pending_durable(
        sorted(_FACT_STATUS_DURABLE))
    if pending_facts:
        problems.append(
            "{0}:{1} 個 entity 的現況檔還沒重寫 —— 新的 current truth 還在"
            "本機".format(PENDING_FACT, len(pending_facts)))

    return {
        "verdict": "FAIL" if problems else "PASS",
        "durable_root": rel_root,
        "uncommitted": uncommitted,
        "head": head or "",
        "upstream": upstream or "",
        "remote_head": remote_head or "",
        "remote_observed": remote_observed,
        "pushed": pushed,
        "open_sessions": open_sessions,
        "pending_revisions": pending_revisions,
        "pending_facts": ["{0}/{1}".format(t, k) for t, k in pending_facts],
        "problems": problems,
    }


def _event_ref(repo_root, session_key, record):
    """事件落點的 repo 相對路徑(durable 側絕不記絕對路徑)。"""
    from . import paths
    path = durable.event_file(repo_root, session_key, record.get("occurred_at"))
    try:
        return paths.to_repo_relative(path, repo_root)
    except paths.NonPortablePath:
        return ""


def _supersede_previous_knowledge(store, kind, payload, now):
    """同一個 key 已有現行記錄 → 標 SUPERSEDED,並回傳舊值快照。

    兩條路都會走到這裡:`devtalk.correct()`(帶 `_lineage_previous` 快照)與
    「同 key 再 propose 一次」(沒帶快照,從 local 現況取)。兩條都要留下 lineage,
    否則「用哪條路更正」會決定歷史有沒有被記下來 —— 那是不可預測的失憶。
    """
    snapshot = payload.get("_lineage_previous")
    rows = store.knowledge(kind=kind, key=payload["key"],
                           statuses=("CANDIDATE", "CONFIRMED", "CONFLICT"),
                           limit=1)
    if not rows and not snapshot:
        return None
    if rows:
        previous = dict(rows[0])
        store.upsert_knowledge({
            "knowledge_id": previous["knowledge_id"], "kind": kind,
            "key": payload["key"], "title": previous["title"],
            "body": previous["body"], "authority": previous["authority"],
            "status": "SUPERSEDED", "confidence": previous["confidence"],
            "recorded_at": previous["recorded_at"], "superseded_at": now,
            "evidence": json.loads(previous["evidence_json"]),
            "conflicts": json.loads(previous["conflicts_json"]),
            "implemented": (None if previous["implemented"] is None
                            else bool(previous["implemented"])),
            "durable": bool(previous["durable"])})
        previous["status"] = "SUPERSEDED"
        return previous
    return snapshot


def _supersede_previous_decision(store, key, now):
    rows = store.decisions(key=key, statuses=("ACCEPTED", "PROPOSED"), limit=1)
    if not rows:
        return None
    previous = dict(rows[0])
    store.upsert_decision({
        "decision_id": previous["decision_id"], "key": key,
        "title": previous["title"], "decision": previous["decision"],
        "alternatives": previous["alternatives"], "reason": previous["reason"],
        "tradeoff": previous["tradeoff"], "status": "SUPERSEDED",
        "decided_at": previous["decided_at"],
        "recorded_at": previous["recorded_at"],
        "supersedes": previous["supersedes"],
        "evidence": json.loads(previous["evidence_json"]),
        "durable": bool(previous["durable"])})
    previous["status"] = "SUPERSEDED"
    return previous


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
