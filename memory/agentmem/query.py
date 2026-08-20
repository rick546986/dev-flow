"""Query Planner 與 Execution Engine(§20/§25)。

先分類再檢索。理由:同一句話問的是不同層的記憶,拿同一條 retrieval 路徑回答
一定會混:

    CURRENT    現在實際怎麼運作      → LVP Current Truth Resolver(fast path)
    HISTORY    以前發生過什麼        → events + 時間序
    WHY        為什麼做這個選擇      → decisions 優先,再補 events
    HOW        怎麼做某件事          → procedural skills + 相關文件
    DOMAIN     這個詞/規則是什麼意思 → 已確認的 domain knowledge 與 invariant
    INTENT     我們打算怎麼發展      → intent(必須標 planned / implemented)
    DISCOVERY  有哪些 / 列出         → 全通道檢索
    MIXED      同時含多種意圖        → 主意圖優先,附上次意圖的結果

每個結果一律帶四件(§25):`retrieval_status` / `confidence` / `evidence` /
`uncertainty`。查不到就回 `NO_RELIABLE_MATCH`,不拿低分 observation 湊答案。
"""
import re

from . import cues, retrieval, textnorm, truth

# ── retrieval status contract(P0-4)──────────────────────────────────────────
# 上層 agent 很容易只看 `retrieval_status` 這一個欄位。所以「其實還沒驗證」
# 必須是一個**狀態**,不能是塞在 uncertainty 裡的一句註解 —— 註解不會被程式讀。
#
#   OK                  已驗證且證據仍成立
#   NEEDS_VERIFICATION  有記憶,但當前 checkout 下還沒驗證過(STALE/未驗/只有旁證)
#   CONFLICT            兩份證據互相矛盾 —— 不挑邊,也不算 OK
#   NO_RELIABLE_MATCH   沒有可信命中(不是「比較差的 OK」)
NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
CONFLICT = "CONFLICT"

RETRIEVAL_STATUSES = (retrieval.OK, NEEDS_VERIFICATION, CONFLICT,
                      retrieval.NO_RELIABLE_MATCH)

# 多筆結果取**最嚴重**的那個:一筆 STALE 就足以讓整體不是 OK。
# NO_RELIABLE_MATCH 不參與這個排序 —— 它是「沒有東西可以升級」的終態,
# 只有在完全沒有命中時才會被選中(見 _overall_status)。
_SEVERITY = {retrieval.OK: 0, NEEDS_VERIFICATION: 1, CONFLICT: 2}


def severity(status):
    """回傳狀態的嚴重度;未知狀態 fail-loud(不默默當成 OK)。"""
    if status not in _SEVERITY:
        raise ValueError(
            "未知的 retrieval status:{0!r}(合法值 {1})".format(
                status, sorted(_SEVERITY)))
    return _SEVERITY[status]


def _overall_status(statuses, has_any_evidence):
    """把多筆狀態收斂成一個;沒有任何證據時才是 NO_RELIABLE_MATCH。"""
    escalatable = [s for s in statuses if s in _SEVERITY]
    if escalatable:
        return max(escalatable, key=severity)
    return retrieval.OK if has_any_evidence else retrieval.NO_RELIABLE_MATCH


CURRENT = "CURRENT"
HISTORY = "HISTORY"
WHY = "WHY"
HOW = "HOW"
DOMAIN = "DOMAIN"
INTENT = "INTENT"
DISCOVERY = "DISCOVERY"
MIXED = "MIXED"

KINDS = (CURRENT, HISTORY, WHY, HOW, DOMAIN, INTENT, DISCOVERY)

# 同分時的優先序(**不是字典序**):「為什麼」是最具體的意圖訊號,
# 而「之前/現在」多半只是伴隨的時間修飾語 —— 「之前為什麼改 X」問的是理由,
# 不是那天發生了什麼。靠字典序決定同分勝負會讓 HISTORY 恰好贏過 WHY,
# 於是所有「之前為什麼」都被路由到事件流而拿不到 decision。
_PRIORITY = (WHY, INTENT, DOMAIN, HOW, CURRENT, HISTORY, DISCOVERY)


def _priority(kind):
    return _PRIORITY.index(kind)


_AS_OF = re.compile(r"(\d{4}-\d{2}-\d{2})")
_BRANCH = re.compile(r"(?:branch|分支)[\s:：]*([A-Za-z0-9._/-]+)")

_ITEM_TYPES = {
    CURRENT: ("fact",),
    HISTORY: ("event",),
    WHY: ("decision", "event"),
    HOW: ("skill",),
    DOMAIN: ("knowledge",),
    INTENT: ("knowledge",),
    DISCOVERY: None,
    MIXED: None,
}


def plan(query, branch=None):
    """把自然語言查詢解析成執行計畫(不碰 DB;純字串分析,可單獨測)。"""
    scores = {}
    for kind, patterns in cues.INTENT_CUES.items():
        total = 0
        for pattern, weight in patterns:
            if re.search(pattern, query, re.I):
                total += weight
        if total:
            scores[kind] = total
    ordered = sorted(scores.items(),
                     key=lambda pair: (-pair[1], _priority(pair[0])))
    if not ordered:
        primary, secondary = DISCOVERY, []
    else:
        primary = ordered[0][0]
        # 次意圖:分數達主意圖的 2/3 才算(否則一句長問句會被判成什麼都問)
        secondary = [k for k, v in ordered[1:] if v * 3 >= ordered[0][1] * 2]
    kind = MIXED if secondary else primary
    as_of = _AS_OF.search(query)
    branch_hit = _BRANCH.search(query)
    symbols = textnorm.symbols(query)
    return {
        "query": query,
        "kind": kind,
        "primary": primary,
        "secondary": secondary,
        "entities": symbols,
        "as_of": as_of.group(1) + "T23:59:59Z" if as_of else None,
        "branch": branch_hit.group(1) if branch_hit else branch,
        "requires_verification": primary in (CURRENT, MIXED),
        "temporal": primary in (HISTORY, WHY),
        "scores": dict(ordered),
    }


def _envelope(plan_dict, status, results, confidence, evidence, uncertainty,
              extra=None):
    payload = {
        "query": plan_dict["query"],
        "query_kind": plan_dict["kind"],
        "primary_intent": plan_dict["primary"],
        "retrieval_status": status,
        "confidence": round(confidence, 4),
        "results": results,
        "evidence": evidence,
        "uncertainty": uncertainty,
    }
    if extra:
        payload.update(extra)
    return payload


def execute(store, repo_root, query, workspace_id, snapshot=None, embedder=None,
            limit=5, branch=None, plan_dict=None):
    """執行查詢。回傳統一 envelope(retrieval_status/confidence/evidence/uncertainty)。"""
    plan_dict = plan_dict or plan(query, branch=branch)
    kind = plan_dict["primary"]
    branch = plan_dict["branch"] or (snapshot or {}).get("branch")

    if kind == CURRENT:
        answer = _current(store, repo_root, plan_dict, workspace_id, snapshot,
                          embedder, limit, branch)
    elif kind == INTENT:
        answer = _intent(store, plan_dict, embedder, limit)
    elif kind == DOMAIN:
        answer = _domain(store, plan_dict, embedder, limit)
    elif kind == WHY:
        answer = _why(store, plan_dict, embedder, limit, branch)
    elif kind == HOW:
        answer = _how(store, plan_dict, embedder, limit)
    elif kind == HISTORY:
        answer = _history(store, plan_dict, embedder, limit, branch)
    else:
        answer = _discovery(store, plan_dict, embedder, limit, branch)

    if plan_dict["secondary"]:
        answer["secondary_intents"] = plan_dict["secondary"]
    store.record_metric(plan_dict["kind"], answer["retrieval_status"],
                        answer.get("latency_ms", 0.0), len(answer["results"]))
    return answer


def _search(store, plan_dict, embedder, limit, kind=None, branch=None,
            item_types=None, statuses=None):
    return retrieval.search(
        store, plan_dict["query"], entities=plan_dict["entities"],
        item_types=item_types if item_types is not None
        else _ITEM_TYPES.get(kind or plan_dict["primary"]),
        branch=branch, until=plan_dict["as_of"], statuses=statuses,
        limit=limit, embedder=embedder)


def _uncertain(found):
    return [] if found else ["沒有可信記憶命中 —— 這是合法結果,不要用低分結果補答案"]


# ── CURRENT ─────────────────────────────────────────────────────────────────
def _current(store, repo_root, plan_dict, workspace_id, snapshot, embedder,
             limit, branch):
    """先走 LVP fast path;VERIFIED 且指紋有效就不必重讀原始碼。"""
    resolved = []
    for entity_type, entity_key, fact_key in _fact_targets(store, plan_dict):
        result = truth.resolve_current(store, repo_root, entity_type, entity_key,
                                       fact_key, workspace_id, snapshot)
        resolved.append(dict(result, entity_type=entity_type,
                             entity_key=entity_key, fact_key=fact_key))
    # 每一筆 fact 的狀態各自映射成 contract 狀態,再取最嚴重的。
    # **不是**「有 resolved 就 OK」—— 舊實作那樣做,STALE 會以 OK 回給 agent。
    per_fact = [_fact_status(r) for r in resolved]
    fast = [r for r in resolved if r["fast_path"]]
    overall = _overall_status(per_fact, has_any_evidence=bool(resolved))

    if overall == retrieval.OK and fast:
        best = max(fast, key=lambda r: r["confidence"])
        return _envelope(
            plan_dict, retrieval.OK,
            [{"item_type": "fact", "title": "{0}.{1}.{2} = {3}".format(
                best["entity_type"], best["entity_key"], best["fact_key"],
                best["value"]), "status": best["status"],
              "value": best["value"], "fast_path": True}],
            best["confidence"], best["evidence"], [],
            extra={"current_truth": best, "resolved": resolved,
                   "latency_ms": 0.0})

    needs = [r for r in resolved if r["needs_inspect"]]
    found = _search(store, plan_dict, embedder, limit, branch=branch)
    uncertainty = []
    for record in needs:
        uncertainty.append(
            "{0}.{1}.{2} 目前是 {3}:{4}".format(
                record["entity_type"], record["entity_key"], record["fact_key"],
                record["status"], "; ".join(record["reasons"])))

    if resolved:
        status = overall
    elif found["results"]:
        # 有旁證但沒有任何已驗證的 current fact:證據照回,但**不能宣稱 OK**。
        # 「檢索撈得到相關文字」與「這就是現在的值」是兩件事。
        status = NEEDS_VERIFICATION
        uncertainty.append(
            "找到相關記憶,但沒有任何已驗證的 current fact —— "
            "要回答現況必須先 inspect 當前原始碼並 verify")
    else:
        status = retrieval.NO_RELIABLE_MATCH
        uncertainty.extend(_uncertain([]))

    confidence = 0.0
    if resolved:
        # 未驗證的答案不得帶高信心:值可能還在,但「它是現況」這件事沒被證實。
        confidence = max(r["confidence"] for r in resolved) * 0.5
    elif found["results"]:
        confidence = min(0.6, found["results"][0]["score"] * 10)
    return _envelope(plan_dict, status, found["results"], confidence,
                     [e for r in resolved for e in r["evidence"]], uncertainty,
                     extra={"resolved": resolved,
                            "needs_inspect": bool(needs),
                            "latency_ms": found["latency_ms"],
                            "channels_active": found["channels_active"]})


def _fact_status(resolved):
    """單筆 LVP 結果 → contract 狀態。"""
    if resolved["status"] == truth.CONFLICT:
        return CONFLICT
    if resolved["fast_path"]:
        return retrieval.OK
    # STALE / CANDIDATE / UNKNOWN 一律是「還沒驗證」——
    # 舊值可能還在,但沒有人證實它現在仍成立。
    return NEEDS_VERIFICATION


def _fact_targets(store, plan_dict):
    """從查詢裡的 symbol/實體推出候選 fact 座標(不猜:只回真的存在的組合)。"""
    targets = []
    seen = set()
    entities = [textnorm.normalize_symbol(e) for e in plan_dict["entities"]]
    for row in store.facts(statuses=truth.LIVE_STATUSES, limit=500):
        coord = (row["entity_type"], row["entity_key"], row["fact_key"])
        if coord in seen:
            continue
        haystack = textnorm.normalize_symbol(
            "{0} {1} {2} {3}".format(*coord, row["value"]))
        query_norm = textnorm.normalize_symbol(plan_dict["query"])
        hit = any(e and e in haystack for e in entities)
        if not hit:
            hit = textnorm.normalize_symbol(row["entity_key"]) in query_norm \
                or textnorm.normalize_symbol(row["fact_key"]) in query_norm
        if hit:
            seen.add(coord)
            targets.append(coord)
    return targets


# ── DOMAIN / INTENT ─────────────────────────────────────────────────────────
def _domain(store, plan_dict, embedder, limit):
    """已確認的 domain knowledge 優先;code 只能當證據,不取代確認過的語意。"""
    found = _search(store, plan_dict, embedder, limit, item_types=("knowledge",))
    records = []
    for hit in found["results"]:
        row = store.knowledge_row(hit["item_id"])
        if row is None or row["kind"] == "intent":
            continue
        records.append(_knowledge_payload(row, hit))
    conflicts = [r for r in records if r["status"] == truth.CONFLICT]
    status = _overall_status(
        [CONFLICT if r["status"] == truth.CONFLICT else retrieval.OK
         for r in records], has_any_evidence=bool(records))
    uncertainty = _uncertain(records)
    for record in conflicts:
        uncertainty.append(
            "{0} 處於 CONFLICT:domain 說「{1}」,程式觀察不同 —— "
            "兩邊都要看,不要挑一邊".format(record["key"], record["title"]))
    confidence = max((r["confidence"] for r in records), default=0.0)
    return _envelope(plan_dict, status, records, confidence,
                     [e for r in records for e in r["evidence"]], uncertainty,
                     extra={"latency_ms": found["latency_ms"]})


def _intent(store, plan_dict, embedder, limit):
    """intent 必須明確標 planned vs implemented(§20;不得冒充 current)。"""
    found = _search(store, plan_dict, embedder, limit, item_types=("knowledge",))
    records = []
    for hit in found["results"]:
        row = store.knowledge_row(hit["item_id"])
        if row is None or row["kind"] != "intent":
            continue
        payload = _knowledge_payload(row, hit)
        payload["implementation_state"] = (
            "implemented" if row["implemented"] else "planned")
        records.append(payload)
    status = _overall_status(
        [CONFLICT if r["status"] == truth.CONFLICT else retrieval.OK
         for r in records], has_any_evidence=bool(records))
    uncertainty = _uncertain(records)
    planned = [r for r in records if r["implementation_state"] == "planned"]
    if planned:
        uncertainty.append(
            "下列 intent 尚未實作,回答時必須與 CURRENT IMPLEMENTATION 分開陳述:"
            + ", ".join(r["key"] for r in planned))
    return _envelope(plan_dict, status, records,
                     max((r["confidence"] for r in records), default=0.0),
                     [e for r in records for e in r["evidence"]], uncertainty,
                     extra={"latency_ms": found["latency_ms"]})


def _knowledge_payload(row, hit):
    import json
    return {
        "item_type": "knowledge", "item_id": row["knowledge_id"],
        "kind": row["kind"], "key": row["key"],
        "title": row["title"], "body": row["body"],
        "authority": row["authority"], "status": row["status"],
        "confidence": row["confidence"],
        "evidence": json.loads(row["evidence_json"]),
        "conflicts": json.loads(row["conflicts_json"]),
        "score": hit["score"], "channels": hit["channels"],
    }


# ── WHY / HOW / HISTORY / DISCOVERY ─────────────────────────────────────────
def _why(store, plan_dict, embedder, limit, branch):
    found = _search(store, plan_dict, embedder, limit,
                    item_types=("decision", "event"), branch=branch)
    decisions = [r for r in found["results"] if r["item_type"] == "decision"]
    events = [r for r in found["results"] if r["item_type"] == "event"]
    ordered = decisions + events
    evidence = []
    for hit in decisions:
        row = next((d for d in store.decisions(limit=200)
                    if d["decision_id"] == hit["item_id"]), None)
        if row:
            hit["reason"] = row["reason"]
            hit["alternatives"] = row["alternatives"]
            hit["tradeoff"] = row["tradeoff"]
            import json
            evidence.extend(json.loads(row["evidence_json"]))
    uncertainty = _uncertain(ordered)
    if ordered and not decisions:
        uncertainty.append(
            "只找到歷史事件、沒有對應的 decision —— 「當初為什麼」缺正式記錄")
    return _envelope(plan_dict, retrieval.OK if ordered
                     else retrieval.NO_RELIABLE_MATCH, ordered,
                     0.8 if decisions else (0.5 if events else 0.0),
                     evidence, uncertainty,
                     extra={"latency_ms": found["latency_ms"]})


def _how(store, plan_dict, embedder, limit):
    found = _search(store, plan_dict, embedder, limit, item_types=("skill",))
    import json
    for hit in found["results"]:
        row = next((s for s in store.skills(limit=200)
                    if s["skill_id"] == hit["item_id"]), None)
        if row:
            hit["steps"] = json.loads(row["steps_json"])
            hit["verification"] = row["verification"]
            hit["skill_status"] = row["status"]
    return _envelope(plan_dict,
                     retrieval.OK if found["results"]
                     else retrieval.NO_RELIABLE_MATCH,
                     found["results"], 0.7 if found["results"] else 0.0, [],
                     _uncertain(found["results"]),
                     extra={"latency_ms": found["latency_ms"]})


def _history(store, plan_dict, embedder, limit, branch):
    found = _search(store, plan_dict, embedder, limit, item_types=("event",),
                    branch=branch)
    results = sorted(found["results"],
                     key=lambda r: (r["occurred_at"] or "", r["score"]),
                     reverse=True)
    return _envelope(plan_dict,
                     retrieval.OK if results else retrieval.NO_RELIABLE_MATCH,
                     results, 0.7 if results else 0.0,
                     [{"type": "event", "ref": r["item_id"]} for r in results],
                     _uncertain(results),
                     extra={"latency_ms": found["latency_ms"]})


def _discovery(store, plan_dict, embedder, limit, branch):
    found = _search(store, plan_dict, embedder, limit, item_types=None,
                    branch=branch)
    return _envelope(plan_dict,
                     retrieval.OK if found["results"]
                     else retrieval.NO_RELIABLE_MATCH,
                     found["results"], 0.5 if found["results"] else 0.0, [],
                     _uncertain(found["results"]),
                     extra={"latency_ms": found["latency_ms"],
                            "channels_active": found["channels_active"]})
