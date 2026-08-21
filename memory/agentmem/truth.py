"""LVP-inspired Current Truth Resolver + invalidation + authority model。

**不是實作 CPU 的 Load Value Prediction。** 借的是它那套機制的形狀:

    last known value + confidence + validation + invalidation + recovery

用在 **A. IMPLEMENTATION TRUTH** 上:「程式現在實際怎麼運作」有一條 fast path ——
上次驗過、依賴檔的指紋沒變、當前 checkout 也沒改動它 → 直接回 VERIFIED,
不必每次重新讀一遍原始碼。

真正關鍵的不是 last value,是 **invalidation**:

    durable(Git)側        VERIFIED        ← 不因為某台機器改了檔就翻掉
    local workspace 側    STALE(overlay) ← 只影響這台機器這個 workspace
    查詢時看到 local STALE → 重新 inspect 當前原始碼 → 相同則回 VERIFIED、
                             不同則舊 fact SUPERSEDED + 新 fact VERIFIED

**Domain knowledge 不套同一組失效規則(§10)。** 「registration 代表一個客戶」
不會因為某支 TypeScript 檔被改就變 STALE —— 它的 authority 來自人,不來自檔案指紋。
code 只能 SUPPORT 或 CONFLICT 已確認的 domain truth,**不能直接 override**;
真的對不上時建立 CONFLICT,讓未來的 agent 看得到兩邊各說什麼(§18)。
"""
import hashlib
import json
import os

from . import ids, lineage, paths, store as store_mod

# ── fact status(不只靠 confidence 數字;§8)──────────────────────────────────
CANDIDATE = "CANDIDATE"
VERIFIED = "VERIFIED"
STALE = "STALE"
CONFLICT = "CONFLICT"
SUPERSEDED = "SUPERSEDED"
UNKNOWN = "UNKNOWN"

FACT_STATUSES = (CANDIDATE, VERIFIED, STALE, CONFLICT, SUPERSEDED, UNKNOWN)
LIVE_STATUSES = (CANDIDATE, VERIFIED, STALE, CONFLICT, UNKNOWN)

ABSENT = "absent"
"""依賴檔不存在時的指紋值 —— 「檔案被刪掉」本身就是一種變化,不是「無法判定」。"""


# ── authority model(§11):不同 knowledge type 各有各的權威序 ────────────────
# **刻意不做全域 `code > everything` 排序** —— 那個排序對 implementation truth 對,
# 對 domain truth 就是錯的:程式碼寫錯業務規則的時候,權威在人身上,不在檔案裡。
IMPLEMENTATION_AUTHORITY = {
    "current_code": 100, "current_config": 95, "current_schema": 95,
    "migration": 90, "runtime_evidence": 85, "code_inference": 60,
    "documentation": 40, "user_claim": 35, "agent_hypothesis": 20,
}
DOMAIN_AUTHORITY = {
    "domain_expert": 100, "user_confirmed": 95, "business_requirement": 90,
    "approved_documentation": 80, "documentation": 60, "code_inference": 40,
    "runtime_evidence": 35, "agent_hypothesis": 20,
}
INTENT_AUTHORITY = {
    "product_decision": 100, "architecture_decision": 100, "approved_plan": 90,
    "user_confirmed": 85, "documentation": 50, "code_inference": 30,
    "agent_hypothesis": 20,
}
DECISION_AUTHORITY = {
    "adr": 100, "pull_request": 90, "commit": 80, "explicit_discussion": 70,
    "documentation": 60, "code_inference": 30, "agent_hypothesis": 20,
}

AUTHORITY_TABLES = {
    "implementation": IMPLEMENTATION_AUTHORITY,
    "domain": DOMAIN_AUTHORITY,
    "invariant": DOMAIN_AUTHORITY,
    "entity": DOMAIN_AUTHORITY,
    "relationship": DOMAIN_AUTHORITY,
    "intent": INTENT_AUTHORITY,
    "decision": DECISION_AUTHORITY,
}

CODE_AUTHORITIES = {"current_code", "current_config", "current_schema",
                    "migration", "runtime_evidence", "code_inference"}


def authority_rank(memory_type, authority):
    """回傳 authority 在該記憶類型下的權重;未知 authority 一律最低(不猜)。"""
    table = AUTHORITY_TABLES.get(memory_type)
    if table is None:
        raise ValueError("未知的記憶類型:{0!r}".format(memory_type))
    return table.get(authority, 0)


def can_override(memory_type, incoming_authority, existing_authority):
    """incoming 有資格覆寫 existing 嗎?**同分不覆寫**(平手時建立 CONFLICT 更誠實)。"""
    return (authority_rank(memory_type, incoming_authority)
            > authority_rank(memory_type, existing_authority))


# ── fingerprint ─────────────────────────────────────────────────────────────
def fingerprint(repo_root, rel_path):
    """依賴檔的內容指紋(sha256 前 16 字);檔案不存在回 ABSENT。"""
    paths.assert_portable(rel_path)
    target = os.path.join(repo_root, rel_path)
    if not os.path.isfile(target):
        return ABSENT
    digest = hashlib.sha256()
    with open(target, "rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()[:16]


def fingerprints_for(repo_root, dependencies):
    return {dep: fingerprint(repo_root, dep) for dep in sorted(dependencies)}


# ── fact 寫入 ───────────────────────────────────────────────────────────────
def record_fact(store, repo_root, entity_type, entity_key, fact_key, value,
                dependencies=(), source_type="current_code", source_ref=None,
                source_commit=None, status=CANDIDATE, confidence=0.5, now=None):
    """記一筆 implementation fact,指紋由當前 checkout 現算。"""
    now = now or store_mod.utc_now()
    deps = [paths.assert_portable(d) for d in dependencies]
    record = {
        "entity_type": entity_type, "entity_key": entity_key,
        "fact_key": fact_key, "value": value, "status": status,
        "confidence": confidence, "recorded_at": now, "effective_at": now,
        "source_type": source_type, "source_ref": source_ref,
        "source_commit": source_commit,
        "dependencies": deps,
        "fingerprints": fingerprints_for(repo_root, deps),
    }
    if status == VERIFIED:
        record["verified_at"] = now
        record["verified_commit"] = source_commit
        record["verification_count"] = 1
    return store.upsert_fact(record)


def live_fact(store, entity_type, entity_key, fact_key):
    """取當前(未被 supersede 的)fact;沒有回 None。"""
    rows = store.facts(entity_type=entity_type, entity_key=entity_key,
                       fact_key=fact_key, statuses=LIVE_STATUSES, limit=1)
    return rows[0] if rows else None


# ── invalidation(local overlay;絕不動 shared state)───────────────────────
def invalidate_for_changes(store, workspace_id, changed_paths, now=None):
    """依賴檔被改動 → 在**本機 workspace** 建立 STALE overlay。

    只掃 facts(implementation truth)。**刻意不掃 knowledge** —— domain truth
    的失效條件不是檔案指紋(§10),把它一起翻掉會讓「使用者確認過的業務規則」
    因為一支不相關的 TypeScript 改動而變成不可信。
    """
    changed = {paths.to_posix(p) for p in changed_paths}
    if not changed:
        return []
    touched = []
    for fact in store.facts(statuses=(VERIFIED, CANDIDATE), limit=5000):
        deps = set(json.loads(fact["dependencies_json"]))
        overlap = sorted(deps & changed)
        if not overlap:
            continue
        store.set_overlay(
            fact["fact_id"], workspace_id, STALE,
            "依賴檔在本機 workspace 有改動:{0}".format(", ".join(overlap)),
            changed_paths=overlap, now=now)
        touched.append(fact["fact_id"])
    return touched


def invalidate_from_snapshot(store, repo_root, workspace_id, snapshot, now=None):
    """從 workspace 快照做一次完整失效掃描:dirty 檔 + 指紋不符都算改動。

    dirty 檔與指紋兩條都要看:branch 切換後檔案內容變了但工作樹是乾淨的
    (指紋抓得到、dirty 抓不到);剛編輯還沒 commit 則反之。
    """
    dirty = set(snapshot.get("dirty_files") or ())
    unparsed = bool(snapshot.get("status_unparsed"))
    changed = set()
    for fact in store.facts(statuses=(VERIFIED,), limit=5000):
        stored = json.loads(fact["fingerprints_json"])
        for dep, expected in stored.items():
            if fingerprint(repo_root, dep) != expected:
                changed.add(dep)
        # 與 resolve_current 同一條規則:dirty 只對沒有指紋的依賴有意義
        # (兩處判準不一致的話,查詢說 VERIFIED、掃描說 STALE,誰對?)
        # 解析不完整時「不在 dirty 裡」不再代表乾淨 —— 同上,一致才有意義。
        for dep in json.loads(fact["dependencies_json"]):
            if dep not in stored and (dep in dirty or unparsed):
                changed.add(dep)
    return invalidate_for_changes(store, workspace_id, changed, now=now)


# ── Current Truth Resolver(fast path)──────────────────────────────────────
def resolve_current(store, repo_root, entity_type, entity_key, fact_key,
                    workspace_id, snapshot=None):
    """Current Truth 查詢的單一入口。

    回傳 dict:
      status        VERIFIED | STALE | CONFLICT | CANDIDATE | UNKNOWN
      value         目前值(UNKNOWN 時為 None)
      fast_path     True = 沒有重讀任何原始碼就能回答
      needs_inspect True = 呼叫端必須重新 inspect 當前原始碼再回答
      confidence / evidence / dependencies / reasons
    """
    fact = live_fact(store, entity_type, entity_key, fact_key)
    if fact is None:
        return {
            "status": UNKNOWN, "value": None, "fast_path": False,
            "needs_inspect": True, "confidence": 0.0, "evidence": [],
            "dependencies": [], "fact_id": None,
            "reasons": ["沒有這筆 fact 的任何記憶 —— UNKNOWN 是合法答案,不要猜"],
        }
    deps = json.loads(fact["dependencies_json"])
    stored = json.loads(fact["fingerprints_json"])
    evidence = []
    if fact["source_type"]:
        evidence.append({"type": fact["source_type"], "ref": fact["source_ref"]})
    base = {
        "value": fact["value"], "confidence": fact["confidence"],
        "dependencies": deps, "evidence": evidence, "fact_id": fact["fact_id"],
        "verified_commit": fact["verified_commit"],
    }

    overlay = store.overlay(fact["fact_id"], workspace_id)
    if overlay is not None:
        return dict(base, status=overlay["status"], fast_path=False,
                    needs_inspect=True,
                    reasons=["本機 workspace overlay:{0}".format(overlay["reason"]),
                             "durable 側仍是 {0};要回答當前 workspace 的問題"
                             "必須重新 inspect".format(fact["status"])])

    if fact["status"] == CONFLICT:
        return dict(base, status=CONFLICT, fast_path=False, needs_inspect=True,
                    reasons=["這筆 fact 處於 CONFLICT —— 不要挑一邊回答"])

    if fact["status"] != VERIFIED:
        return dict(base, status=fact["status"], fast_path=False,
                    needs_inspect=True,
                    reasons=["fact 尚未 VERIFIED(現為 {0})".format(fact["status"])])

    # VERIFIED:驗指紋(這是 fast path 的門票)
    changed = [dep for dep, expected in sorted(stored.items())
               if fingerprint(repo_root, dep) != expected]
    # 工作樹 dirty 只對**沒有指紋**的依賴有意義。
    #
    # 為什麼不是「dirty 就一律 STALE」:指紋記的是「我們驗證時看到的內容」。
    # 內容仍與指紋相符 = 我們驗證過的就是現在這份,那筆 fact 現在就是真的 ——
    # 它有沒有被 commit 與它是不是真的無關。若讓 dirty 無條件覆蓋相符的指紋,
    # 重新驗證過的 fact 會永遠停在 STALE(reverify 之後再問還是 STALE),
    # 而開發中的工作樹幾乎永遠是 dirty,fast path 就等於不存在。
    #
    # dirty 的價值在於**指紋缺席時的第二道**:沒有指紋可比的依賴,dirty 是唯一
    # 能察覺「這個檔跟 HEAD 不一樣」的訊號,那種 fact 不得走 fast path。
    unfingerprinted = [dep for dep in deps if dep not in stored]
    dirty = sorted(set(unfingerprinted)
                   & set((snapshot or {}).get("dirty_files") or ()))
    # git status 有解析不出來的欄位 = **dirty 清單不完整**。
    #
    # parser 拒絕猜、原樣回報那些欄位是對的,但那份不確定性必須在這裡被消化,
    # 否則系統可以同時說「這個 workspace 有一部分我看不懂」與「VERIFIED +
    # fast_path」。少算檔案是靜默的錯,而靜默的錯會讓 agent 拿 STALE 的值
    # 當現況回答。
    #
    # 範圍剛好是 dirty 那條路,不多不少:指紋相符代表驗證時看到的內容就是
    # 現在這份,git 看不看得懂它的狀態列與那件事無關(把指紋齊全的 fact 也
    # 打回 STALE 就是拿無關的訊號否定已經驗過的內容)。沒有指紋的依賴則
    # 只剩 dirty 能證明它乾淨 —— 清單不完整就等於證明不了。
    unproven = sorted(unfingerprinted) if (
        unfingerprinted and (snapshot or {}).get("status_unparsed")) else []
    if changed or dirty or unproven:
        reason_parts = []
        if changed:
            reason_parts.append("指紋不符:{0}".format(", ".join(changed)))
        if dirty:
            reason_parts.append(
                "工作樹未提交改動且無指紋可比:{0}".format(", ".join(dirty)))
        if unproven:
            reason_parts.append(
                "git status 有 {0} 筆無法解析,無指紋可比的依賴無從證明乾淨:"
                "{1}".format(len((snapshot or {})["status_unparsed"]),
                             ", ".join(unproven)))
        reason = ";".join(reason_parts)
        store.set_overlay(
            fact["fact_id"], workspace_id, STALE, reason,
            changed_paths=sorted(set(changed) | set(dirty) | set(unproven)))
        return dict(base, status=STALE, fast_path=False, needs_inspect=True,
                    reasons=[reason,
                             "已在本機建立 STALE overlay;durable 側不動"])
    if not stored:
        return dict(base, status=CANDIDATE, fast_path=False, needs_inspect=True,
                    reasons=["VERIFIED 但沒有任何依賴指紋 —— 無從驗證,"
                             "降級成需要 inspect(不假裝驗過)"])
    return dict(base, status=VERIFIED, fast_path=True, needs_inspect=False,
                reasons=["依賴指紋全部相符,fast path 命中"])


def reverify(store, repo_root, fact_id, workspace_id, observed_value,
             source_commit=None, now=None, session_id=None, reason=""):
    """重新驗證的三種結果(§9 recovery):

      observed == 舊值   → 清掉 overlay、重算指紋、VERIFIED、verification_count+1
      observed != 舊值   → 舊 fact SUPERSEDED、新 fact VERIFIED
      observed is None   → 判不出來:留 STALE overlay,contradiction_count+1,
                           **不寫新值**(判不出來時猜一個值是最糟的選擇)
    """
    now = now or store_mod.utc_now()
    fact = store.fact_row(fact_id)
    if fact is None:
        raise ValueError("fact 不存在:{0}".format(fact_id))
    deps = json.loads(fact["dependencies_json"])

    if observed_value is None:
        store.upsert_fact(_as_record(fact, durable=False, contradiction_count=
                                     fact["contradiction_count"] + 1))
        store.set_overlay(fact_id, workspace_id, STALE,
                          "重新驗證無法判定當前值(inspect 失敗或證據不足)",
                          now=now)
        return {"outcome": "undetermined", "fact_id": fact_id, "status": STALE}

    if str(observed_value) == fact["value"]:
        store.clear_overlay(fact_id, workspace_id)
        store.upsert_fact(_as_record(
            fact, durable=False, status=VERIFIED, verified_at=now,
            verified_commit=source_commit or fact["verified_commit"],
            verification_count=fact["verification_count"] + 1,
            fingerprints=fingerprints_for(repo_root, deps),
            confidence=min(0.99, max(fact["confidence"], 0.9))))
        return {"outcome": "reconfirmed", "fact_id": fact_id, "status": VERIFIED}

    new_id = ids.new_id("fact")
    # `durable=False`:這一列的內容變了,`.dev-flow/` 裡那份還是舊的。
    # 旗標的語意是「現在的內容就是檔裡那份」,所以改了內容就必須打回 pending
    # —— 否則現況檔會停在 VERIFIED/舊值,而沒有任何機制會發現。
    store.upsert_fact(_as_record(
        fact, durable=False, status=SUPERSEDED, superseded_at=now,
        superseded_by=new_id))
    # 記一筆 revision(pending):「原本 X、現在 Y、為什麼」是現況視圖留不下來的
    # 東西 —— 少了它,另一台機器 rebuild 之後只看得到現在的值(P0-3)。
    lineage.record_pending(store, lineage.build_fact_revision(
        fact["entity_type"], fact["entity_key"], fact["fact_key"],
        {"fact_id": fact_id, "value": fact["value"], "status": SUPERSEDED,
         "source_type": fact["source_type"]},
        {"fact_id": new_id, "value": str(observed_value), "status": VERIFIED,
         "source_type": fact["source_type"]},
        reason=reason, session_id=session_id, occurred_at=now,
        evidence=[{"type": "file", "ref": dep} for dep in deps]))
    store.upsert_fact({
        "fact_id": new_id, "entity_type": fact["entity_type"],
        "entity_key": fact["entity_key"], "fact_key": fact["fact_key"],
        "value": str(observed_value), "status": VERIFIED, "confidence": 0.95,
        "recorded_at": now, "effective_at": now, "verified_at": now,
        "verified_commit": source_commit, "verification_count": 1,
        "source_type": fact["source_type"], "source_ref": fact["source_ref"],
        "source_commit": source_commit,
        "dependencies": deps,
        "fingerprints": fingerprints_for(repo_root, deps)})
    store.clear_overlay(fact_id, workspace_id)
    return {"outcome": "superseded", "fact_id": fact_id, "status": SUPERSEDED,
            "new_fact_id": new_id}


def _as_record(row, **over):
    record = {
        "fact_id": row["fact_id"], "entity_type": row["entity_type"],
        "entity_key": row["entity_key"], "fact_key": row["fact_key"],
        "value": row["value"], "status": row["status"],
        "confidence": row["confidence"], "effective_at": row["effective_at"],
        "recorded_at": row["recorded_at"], "superseded_at": row["superseded_at"],
        "superseded_by": row["superseded_by"], "source_type": row["source_type"],
        "source_ref": row["source_ref"], "source_commit": row["source_commit"],
        "verified_at": row["verified_at"],
        "verified_commit": row["verified_commit"],
        "verification_count": row["verification_count"],
        "contradiction_count": row["contradiction_count"],
        "dependencies": json.loads(row["dependencies_json"]),
        "fingerprints": json.loads(row["fingerprints_json"]),
        "durable": bool(row["durable"]), "legacy": bool(row["legacy"]),
    }
    record.update(over)
    return record


# ── B/C. domain knowledge 與 intent ─────────────────────────────────────────
def assert_knowledge(store, kind, key, title, body="", authority="domain_expert",
                     status="CONFIRMED", confidence=0.9, evidence=(),
                     implemented=None, now=None):
    """寫入/更新一筆 knowledge。權威不足時**不覆寫**,改成回報既有內容。

    回傳 (knowledge_id, action);action ∈ created | updated | refused。
    """
    now = now or store_mod.utc_now()
    existing = store.knowledge(kind=kind, key=key,
                               statuses=("CANDIDATE", "CONFIRMED", "CONFLICT",
                                         "UNKNOWN"), limit=1)
    if existing:
        current = existing[0]
        if not can_override(kind, authority, current["authority"]) \
                and authority != current["authority"]:
            return current["knowledge_id"], "refused"
        knowledge_id = store.upsert_knowledge({
            "knowledge_id": current["knowledge_id"], "kind": kind, "key": key,
            "title": title, "body": body, "authority": authority,
            "status": status, "confidence": confidence, "recorded_at": now,
            "evidence": list(evidence) or json.loads(current["evidence_json"]),
            "conflicts": json.loads(current["conflicts_json"]),
            "implemented": implemented, "durable": bool(current["durable"])})
        return knowledge_id, "updated"
    knowledge_id = store.upsert_knowledge({
        "kind": kind, "key": key, "title": title, "body": body,
        "authority": authority, "status": status, "confidence": confidence,
        "recorded_at": now, "evidence": list(evidence),
        "implemented": implemented})
    return knowledge_id, "created"


def reconcile_with_code(store, kind, key, observation, observation_authority,
                        supports, evidence=(), now=None):
    """把「程式碼看起來怎樣」對照已確認的 domain knowledge(§18)。

    supports=True  → 加一筆 SUPPORT 證據,status 不降級
    supports=False → **建立 CONFLICT**,body 一字不改
                     (code 不能 override confirmed domain truth)

    回傳 (status, action);action ∈ supported | conflicted | noop。
    """
    now = now or store_mod.utc_now()
    rows = store.knowledge(kind=kind, key=key,
                           statuses=("CANDIDATE", "CONFIRMED", "CONFLICT"),
                           limit=1)
    if not rows:
        return UNKNOWN, "noop"
    current = rows[0]
    evidence_list = json.loads(current["evidence_json"])
    conflicts = json.loads(current["conflicts_json"])
    if supports:
        evidence_list.append({"type": observation_authority,
                              "ref": observation, "stance": "supports",
                              "observed_at": now})
        store.upsert_knowledge({
            "knowledge_id": current["knowledge_id"], "kind": kind, "key": key,
            "title": current["title"], "body": current["body"],
            "authority": current["authority"], "status": current["status"],
            "confidence": min(0.99, current["confidence"] + 0.02),
            "recorded_at": current["recorded_at"], "evidence": evidence_list,
            "conflicts": conflicts,
            "implemented": (None if current["implemented"] is None
                            else bool(current["implemented"])),
            "durable": bool(current["durable"])})
        return current["status"], "supported"

    if observation_authority in CODE_AUTHORITIES \
            and can_override(kind, observation_authority, current["authority"]):
        # 罕見但存在:既有 knowledge 本身只是 agent 猜的,程式碼證據更強 → 允許降級
        new_status = CANDIDATE
    else:
        new_status = CONFLICT
    conflicts.append({"observation": observation,
                      "authority": observation_authority,
                      "stance": "contradicts", "observed_at": now})
    store.upsert_knowledge({
        "knowledge_id": current["knowledge_id"], "kind": kind, "key": key,
        "title": current["title"], "body": current["body"],
        "authority": current["authority"], "status": new_status,
        "confidence": current["confidence"], "recorded_at": current["recorded_at"],
        "evidence": evidence_list, "conflicts": conflicts,
        "implemented": (None if current["implemented"] is None
                        else bool(current["implemented"])),
        "durable": bool(current["durable"])})
    return new_status, "conflicted"


def open_conflicts(store, limit=50):
    """所有處於 CONFLICT 的記憶(startup context 要帶進去,§27)。"""
    out = []
    for row in store.knowledge(statuses=(CONFLICT,), limit=limit):
        out.append({"type": row["kind"], "key": row["key"],
                    "title": row["title"],
                    "conflicts": json.loads(row["conflicts_json"])})
    for row in store.facts(statuses=(CONFLICT,), limit=limit):
        out.append({"type": "implementation", "key": "{0}.{1}.{2}".format(
            row["entity_type"], row["entity_key"], row["fact_key"]),
            "title": row["value"], "conflicts": []})
    return out
