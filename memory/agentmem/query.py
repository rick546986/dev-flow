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
`uncertainty`,外加必填的 `per_coordinate`(owner 裁決 D-4):每個已解析
`(entity_key, fact_key)` 一列,讓呼叫端分得出「被問的那筆是 STALE」與
「別筆是 STALE、被問的那筆其實 OK」。既有頂層欄位語意一個字都不准動。
查不到就回 `NO_RELIABLE_MATCH`,不拿低分 observation 湊答案。
"""
import re

from . import cues, retrieval, signal as signal_mod, sync, textnorm, truth

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
    # D-4:必填。extra 可以填內容,但不能讓欄位缺席或變成 None ——
    # 呼叫端寫 .get() 時 None 與「空」同義,少一個欄位就靜默降級。
    if "per_coordinate" not in payload or payload["per_coordinate"] is None:
        payload["per_coordinate"] = []
    return payload


def execute(store, repo_root, query, workspace_id, snapshot=None, embedder=None,
            limit=5, branch=None, plan_dict=None):
    """執行查詢。回傳統一 envelope(retrieval_status/confidence/evidence/uncertainty)。"""
    plan_dict = plan_dict or plan(query, branch=branch)
    for _attempt in range(sync.READ_MAX_ATTEMPTS):
        rebuilt, certified = sync.observe_certified_generation(
            repo_root, store, embedder)
        if embedder is not None and (rebuilt or certified):
            # `_resolve` / context 可能已經 rebuild 過但沒帶 embedder。
            # reindex 只補缺,完整時是一次 LEFT JOIN。
            embedder.reindex(store)
        answer = _execute_prepared(
            store, repo_root, plan_dict, workspace_id, snapshot, embedder,
            limit)
        if sync.generation_still_certified(repo_root, certified):
            store.record_metric(plan_dict["kind"], answer["retrieval_status"],
                                answer.get("latency_ms", 0.0),
                                len(answer["results"]))
            return answer
    raise sync.DurableMirrorDrift(
        "query could not certify a stable durable generation "
        "after {0} attempts".format(sync.READ_MAX_ATTEMPTS))


def _execute_prepared(store, repo_root, plan_dict, workspace_id, snapshot,
                      embedder, limit):
    """在已認定的世代上組答案。呼叫端負責讀後驗證。"""
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
    coords = _per_coordinate(resolved)

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
                   "per_coordinate": coords, "latency_ms": 0.0})

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
                            "per_coordinate": coords,
                            "needs_inspect": bool(needs),
                            "latency_ms": found["latency_ms"],
                            "channels_active": found["channels_active"]})


def _per_coordinate(resolved):
    """D-4:每個已解析座標一列。必填明細,不改既有欄位語意。

    每一列同時帶 truth_status(LVP:VERIFIED/STALE/CANDIDATE/CONFLICT/UNKNOWN)
    與 retrieval_status(契約四態),呼叫端才能在 entity-only 聚合降級時
    指出是哪一座標造成的,而不必去猜 `resolved` 的內部形狀。
    """
    rows = []
    for record in resolved:
        rows.append({
            "entity_type": record["entity_type"],
            "entity_key": record["entity_key"],
            "fact_key": record["fact_key"],
            "truth_status": record["status"],
            "retrieval_status": _fact_status(record),
            "value": record["value"],
        })
    return rows


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
    """從查詢裡的 symbol/實體推出候選 fact 座標(不猜:只回真的存在的組合)。

    **不能設列數上限。** 這裡做的是精確匹配(entity/fact key 或它們的值是否
    命中查詢),不是模糊排序後的探索式檢索 —— 探索式檢索(`_search`)才有資格
    在**相關性排序之後**加視窗。在這裡先套 `limit=N` 再比對,等於用「最近
    N 筆」這個跟相關性無關的排序當篩子:唯一正確的那筆 CURRENT fact 只要
    比 N 筆別的 live fact舊,就會在比對開始之前被砍掉,而砍法對呼叫端完全
    不可見(`GPT-P1-CURRENT-500`)。

    **座標感知,不能只靠共用的 fact_key/value 做 OR 比對。** 如果查詢已經
    指名了某個目前存在的 entity(entity_key 的文字出現在查詢裡),就只在
    這個 entity 底下找 fact —— 不能因為另一個沒被指名的 entity 剛好共用
    同一個 fact_key(例如兩個 entity 都有 `current_table`)就把它也拉進
    同一筆聚合查詢,讓它的 STALE/CANDIDATE 狀態去拖累被指名 entity 的
    精確答案(`GPT-P1-CURRENT-TARGET-SCOPE`)。如果查詢完全沒有指名任何
    entity,只能靠 fact_key/value 反查,而命中的 entity 不只一個 —— 代表
    查詢本身是歧義的,不猜一個當答案,回空列表讓上層退到模糊檢索與
    `NEEDS_VERIFICATION`。

    **座標的兩個分量都要收,不只 entity。** 只按 entity 收斂還不夠:一個
    entity 天生擁有很多 fact(`current_table` / `port` / `version` …),
    只按 entity 篩會讓查詢明確指名的那個座標被同 entity 底下**沒被問到**的
    fact 拖累 —— 一筆不相關的 CANDIDATE 就足以把精確答案從 OK 降成
    NEEDS_VERIFICATION,一筆 CONFLICT 更會直接升級成 CONFLICT
    (`GPT-P1-CURRENT-FACT-SCOPE`)。所以 entity 被指名時再分三種:

    - 查詢也指名了 fact_key,且該 fact_key 存在於被指名的 entity 底下 →
      只收這個**交集**。
    - 查詢指名了 fact_key,但它只存在於別的 entity 底下 → 被問的座標不存在,
      回空。**不得**退回「那就把這個 entity 全部 fact 都給你」—— 那是拿一個
      沒被問的座標當答案。
    - 查詢完全沒指名任何 fact_key → 被問的座標就是 entity 本身,這時整個
      entity 底下每一筆都在範圍內,整體降級是對的(這是**刻意保留**的既有
      語意,由 `test_current_entity_only_query_still_aggregates_all_facts`
      釘住)。

    已知界線:「有沒有指名 fact_key」只認得**目前存在於 store 裡的** fact_key。
    查詢寫了一個 store 裡不存在的 fact_key(打錯字、還沒記錄過)時無從辨識,
    會落到第三種當成 entity-level 查詢。這是「不猜」的直接後果 —— 要辨識它就得
    先假設查詢裡的哪個 token 是 fact_key,而那正是本函式拒絕做的猜測。"""
    entities = [textnorm.normalize_symbol(e) for e in plan_dict["entities"]]
    query_norm = textnorm.normalize_symbol(plan_dict["query"])
    rows = list(store.facts(statuses=truth.LIVE_STATUSES, limit=None))

    def named(token):
        return bool(token) and (token in query_norm or token in entities)

    entity_named = {row["entity_key"] for row in rows
                    if named(textnorm.normalize_symbol(row["entity_key"]))}
    fact_key_named = {row["fact_key"] for row in rows
                      if named(textnorm.normalize_symbol(row["fact_key"]))}

    seen = set()
    targets = []
    if entity_named:
        scoped = [row for row in rows if row["entity_key"] in entity_named]
        if fact_key_named:
            scoped = [row for row in scoped
                      if row["fact_key"] in fact_key_named]
        for row in scoped:
            coord = (row["entity_type"], row["entity_key"], row["fact_key"])
            if coord in seen:
                continue
            seen.add(coord)
            targets.append(coord)
        return targets

    fact_key_entities = {}
    candidates = []
    for row in rows:
        coord = (row["entity_type"], row["entity_key"], row["fact_key"])
        if coord in seen:
            continue
        if named(textnorm.normalize_symbol(row["value"])):
            seen.add(coord)
            candidates.append((coord, None))
            continue
        fact_key_norm = textnorm.normalize_symbol(row["fact_key"])
        if named(fact_key_norm):
            seen.add(coord)
            candidates.append((coord, fact_key_norm))
            fact_key_entities.setdefault(fact_key_norm, set()).add(
                row["entity_key"])

    ambiguous = {key for key, ents in fact_key_entities.items()
                if len(ents) > 1}
    return [coord for coord, key in candidates if key not in ambiguous]


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
        # 主鍵撈,不掃「最近 200 筆」:檢索索引沒有那個視窗,命中較舊的
        # decision 時掃不到,而下面仍然回 OK —— 那是「聲稱有答案卻沒附上
        # 構成答案的欄位」,比查不到更糟。
        row = store.decision_row(hit["item_id"])
        if row:
            hit["reason"] = row["reason"]
            hit["alternatives"] = row["alternatives"]
            hit["tradeoff"] = row["tradeoff"]
            import json
            evidence.extend(json.loads(row["evidence_json"]))
    uncertainty = _uncertain(ordered)
    if not decisions:
        # **沒有 decision 就沒有「為什麼」。** 事件說的是「發生了什麼」,
        # 把它當理由回答等於拿現象冒充動機 —— 那是這個系統最該避免的一種捏造。
        # 相關事件仍然回傳,但放在 related_events,絕不放進 results,
        # 免得呼叫端把它當成答案。
        if events:
            uncertainty.append(
                "找到 {0} 筆相關歷史事件,但**沒有任何 decision 記錄** —— "
                "「當初為什麼這樣選」沒有被記下來。事件在 related_events,"
                "不要拿它推測理由".format(len(events)))
        return _envelope(plan_dict, retrieval.NO_RELIABLE_MATCH, [], 0.0,
                         evidence, uncertainty,
                         extra={"latency_ms": found["latency_ms"],
                                "related_events": events})
    return _envelope(plan_dict, retrieval.OK, ordered, 0.8, evidence,
                     uncertainty,
                     extra={"latency_ms": found["latency_ms"]})


def _how(store, plan_dict, embedder, limit):
    found = _search(store, plan_dict, embedder, limit, item_types=("skill",))
    import json
    for hit in found["results"]:
        row = store.skill_row(hit["item_id"])   # 主鍵撈(理由同 _why)
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
    # 只回高訊號事件:「以前發生過什麼」問的是重要的事,不是我 grep 過什麼。
    # 低訊號觀察仍留在本機、仍可用 DISCOVERY 查到,只是不該淹沒歷史問句。
    found = _search(store, plan_dict, embedder, limit, item_types=("event",),
                    branch=branch, statuses=(signal_mod.HIGH,))
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
