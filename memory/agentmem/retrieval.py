"""Retrieval v3:multi-channel + RRF fusion(§21/§25)。

**不做傳統的單通道 top-k RAG,也不混原始分數。**

六個通道各自獨立產出排名:

    exact_symbol   code symbol 精確/正規化命中(table、function、file path、env key)
    lexical        可攜的 IDF 加權 token 重疊(中文 unigram+bigram 也在內)
    fts            SQLite FTS5 unicode61 的 BM25(有 FTS5 才有)
    trigram        SQLite FTS5 trigram(部分字串/錯字;有 trigram 才有)
    vector         embedding cosine(見 embedding.py 的誠實聲明)
    entity         查詢裡的 entity/key 與 item 標題的直接對應

再用 **RRF(Reciprocal Rank Fusion)** 合併:`score = Σ wᶜ / (k + rankᶜ)`。

為什麼不用「0.4×FTS + 0.6×vector」這種固定權重直接混:BM25 是無界的、cosine 是
[-1,1] 的,兩者相加等於讓「哪個通道的分數尺度大」決定結果,而尺度會隨語料改變 ——
同一個查詢在資料長大之後排序會無聲改變。RRF 只吃**排名**,對尺度免疫。

**NO_RELIABLE_MATCH 是一等結果(§25)。** 沒有可信命中時回空清單 + 狀態,
絕不因為 FTS 掃到一筆低分 observation 就拿它當答案。
"""
import json
import math
import time

from . import cues, schema, textnorm

RRF_K = 60

CHANNEL_WEIGHTS = {
    # exact symbol 權重最高:coding agent 問的是「哪一張表」,答錯一個字就是答錯
    "exact_symbol": 3.0,
    "lexical": 2.0,
    "fts": 1.5,
    "entity": 1.5,
    "vector": 1.0,
    "trigram": 0.7,
}

OK = "OK"
NO_RELIABLE_MATCH = "NO_RELIABLE_MATCH"

MIN_FUSED_SCORE = 1.0 / (RRF_K + 40)
"""排名門檻:任何通道都排不進前 40 名的東西,不配當答案。"""

MIN_COVERAGE = 0.30
"""資訊量門檻:lexical 命中必須佔查詢資訊量的三成以上才算「相關」。

沒有這道門檻,「完全不存在的東西 zzzz」會因為命中「的」「不」「在」這些
低資訊量單字而撈回一筆無關記憶 —— 那正是 §25 要禁的 arbitrary fallback。
"""

HIGH_PRECISION_CHANNELS = ("exact_symbol", "entity")
"""高精度通道:命中即可背書相關性(問「哪一張表」時,表名對上就是對上)。

fts / trigram / vector 是**召回**通道:它們可以把候選帶進來、可以參與排序,
但不能單獨背書「這筆真的相關」——三者都會對任何一句中文回一堆低分結果。
"""


def _filters(project_id, item_types=None, branch=None, since=None, until=None,
             statuses=None):
    clauses = ["i.project_id = ?"]
    args = [project_id]
    if item_types:
        clauses.append("i.item_type IN ({0})".format(
            ",".join("?" for _ in item_types)))
        args.extend(item_types)
    if branch:
        # branch 為 NULL 的 item 是「跨 branch 都成立」的記憶,不該被 branch 過濾掉
        clauses.append("(i.branch = ? OR i.branch IS NULL)")
        args.append(branch)
    if since:
        clauses.append("(i.occurred_at IS NULL OR i.occurred_at >= ?)")
        args.append(since)
    if until:
        clauses.append("(i.occurred_at IS NULL OR i.occurred_at <= ?)")
        args.append(until)
    if statuses:
        clauses.append("i.status IN ({0})".format(
            ",".join("?" for _ in statuses)))
        args.extend(statuses)
    return " AND ".join(clauses), args


def channel_exact_symbol(store, query, scope, limit):
    syms = textnorm.symbols(query)
    if not syms:
        return []
    norms = sorted({textnorm.normalize_symbol(s) for s in syms})
    where, args = _filters(store.project_id, **scope)
    rows = store.conn.execute(
        "SELECT i.item_uid, COUNT(*) AS hits FROM item_symbols s"
        " JOIN items i ON i.item_uid = s.item_uid"
        " WHERE s.norm IN ({0}) AND {1}"
        " GROUP BY i.item_uid ORDER BY hits DESC, i.item_uid LIMIT ?".format(
            ",".join("?" for _ in norms), where),
        [*norms, *args, int(limit)]).fetchall()
    return [row["item_uid"] for row in rows]


def channel_lexical(store, query, scope, limit):
    """IDF 加權 token 重疊 + **coverage**。純 SQL + 一次 Python 排序,不撈全表(§33)。

    回傳 (ranked_uids, coverage_by_uid)。coverage 是「命中的 token 佔查詢資訊量的
    比例」—— 它是 NO_RELIABLE_MATCH 判定的依據,不是排序用的:
    中文查詢一定會有一堆低資訊量的單字(的/是/在/什麼),光看「有沒有命中」的話
    任何一筆記憶都會被任何一句中文命中,retrieval 就退化成 §25 禁止的
    arbitrary fallback。coverage 逼結果證明自己命中了**有資訊量**的詞。
    """
    toks = list(dict.fromkeys(textnorm.tokens(query)))
    if not toks:
        return [], {}
    # coverage 的分母只算**內容詞**:問句框架(之前/為什麼/現在/哪一張/的/嗎…)
    # 對「答案是什麼」零貢獻,把它們算進分母會讓任何中文問句都達不到門檻。
    content = [t for t in dict.fromkeys(textnorm.tokens(cues.strip_frame(query)))]
    if not content:
        content = toks
    where, args = _filters(store.project_id, **scope)
    total = store.conn.execute(
        "SELECT COUNT(*) FROM items i WHERE {0}".format(where), args).fetchone()[0]
    if not total:
        return [], {}
    rows = store.conn.execute(
        "SELECT t.token, t.item_uid, t.tf FROM item_tokens t"
        " JOIN items i ON i.item_uid = t.item_uid"
        " WHERE t.token IN ({0}) AND {1}".format(
            ",".join("?" for _ in toks), where),
        [*toks, *args]).fetchall()
    df = {}
    for row in rows:
        df[row["token"]] = df.get(row["token"], 0) + 1

    def intrinsic(token):
        """CJK n-gram 的資訊量本質上低於一個完整詞 —— 它們是**沒有分詞器時的
        詞近似**,不是詞本身。

        「改過什麼」會產出 `改過` 這個跨詞邊界的假詞;它在語料裡查不到,是因為
        它本來就不是一個詞,不是因為記憶不相關。反過來,拉丁詞與 identifier
        (`kubernetes`、`zzzz_nonexistent_table`)在語料裡查不到就是**強證據**
        說明這件事沒被記錄過 —— 那正是 NO_RELIABLE_MATCH 該成立的時候。

        所以折扣只給 CJK n-gram,不給拉丁詞;而且分子分母乘同一個係數,
        這是在校正 n-gram 的證據強度,不是在放寬門檻。
        """
        if token.isascii():
            return 1.0
        return 0.35 if len(token) == 1 else 0.6

    def idf(token):
        # 0.5 平滑:查不到的 token 拿到最高 IDF,才會把 coverage 分母撐大 ——
        # 否則「查詢裡有一個沒人提過的關鍵詞」會被當成無所謂。
        return intrinsic(token) * math.log(1.0 + (total / (df.get(token, 0) + 0.5)))

    query_mass = sum(idf(token) for token in content) or 1.0
    scores = {}
    matched = {}
    content_set = set(content)
    for row in rows:
        weight = idf(row["token"])
        scores[row["item_uid"]] = scores.get(row["item_uid"], 0.0) + \
            weight * (1.0 + math.log(row["tf"]))
        if row["token"] in content_set:
            matched[row["item_uid"]] = matched.get(row["item_uid"], 0.0) + weight
    coverage = {uid: min(1.0, value / query_mass) for uid, value in matched.items()}
    ordered = sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
    return [uid for uid, _score in ordered[:limit]], coverage


def channel_fts(store, query, scope, limit):
    if not store.caps.get(schema.CAP_FTS5):
        return []
    match = textnorm.normalize_query(query)
    if not match:
        return []
    where, args = _filters(store.project_id, **scope)
    try:
        rows = store.conn.execute(
            "SELECT f.item_uid FROM items_fts f"
            " JOIN items i ON i.item_uid = f.item_uid"
            " WHERE items_fts MATCH ? AND {0}"
            " ORDER BY bm25(items_fts), f.item_uid LIMIT ?".format(where),
            [match, *args, int(limit)]).fetchall()
    except Exception:
        # FTS 查詢語法在不同 SQLite 版本上寬嚴不同 —— 這個通道失敗只該少一個通道,
        # 不該讓整個查詢炸掉(其他通道仍會給答案,狀態欄會反映可信度)。
        return []
    return [row["item_uid"] for row in rows]


def channel_trigram(store, query, scope, limit):
    if not store.caps.get(schema.CAP_TRIGRAM):
        return []
    cleaned = "".join(ch for ch in query if not ch.isspace())
    if len(cleaned) < 3:
        return []
    where, args = _filters(store.project_id, **scope)
    try:
        rows = store.conn.execute(
            "SELECT t.item_uid FROM items_tri t"
            " JOIN items i ON i.item_uid = t.item_uid"
            " WHERE items_tri MATCH ? AND {0}"
            " ORDER BY bm25(items_tri), t.item_uid LIMIT ?".format(where),
            ['"' + cleaned.replace('"', '""') + '"', *args, int(limit)]).fetchall()
    except Exception:
        return []
    return [row["item_uid"] for row in rows]


def channel_entity(store, entities, scope, limit):
    if not entities:
        return []
    where, args = _filters(store.project_id, **scope)
    clauses = " OR ".join(["i.title LIKE ?"] * len(entities))
    rows = store.conn.execute(
        "SELECT i.item_uid FROM items i WHERE ({0}) AND {1}"
        " ORDER BY i.occurred_at DESC, i.item_uid LIMIT ?".format(clauses, where),
        [*["%" + e + "%" for e in entities], *args, int(limit)]).fetchall()
    return [row["item_uid"] for row in rows]


def channel_vector(store, query, embedder, scope, limit):
    if embedder is None:
        return [], 0
    hits, skipped = embedder.search(store, query, limit=limit * 3)
    if not hits:
        return [], skipped
    allowed = set(_allowed_uids(store, scope, [uid for uid, _ in hits]))
    return [uid for uid, _score in hits if uid in allowed][:limit], skipped


def _allowed_uids(store, scope, uids):
    if not uids:
        return []
    where, args = _filters(store.project_id, **scope)
    rows = store.conn.execute(
        "SELECT i.item_uid FROM items i WHERE i.item_uid IN ({0}) AND {1}".format(
            ",".join("?" for _ in uids), where), [*uids, *args]).fetchall()
    return [row["item_uid"] for row in rows]


def search(store, query, entities=(), item_types=None, branch=None, since=None,
           until=None, statuses=None, limit=10, embedder=None,
           weights=None):
    """multi-channel + RRF。回傳 dict(status / results / channels / latency_ms)。"""
    started = time.time()
    scope = {"item_types": item_types, "branch": branch, "since": since,
             "until": until, "statuses": statuses}
    pool = max(limit * 4, 20)
    weights = dict(CHANNEL_WEIGHTS, **(weights or {}))

    lexical_hits, coverage = channel_lexical(store, query, scope, pool)
    ranked = {
        "exact_symbol": channel_exact_symbol(store, query, scope, pool),
        "lexical": lexical_hits,
        "fts": channel_fts(store, query, scope, pool),
        "trigram": channel_trigram(store, query, scope, pool),
        "entity": channel_entity(store, list(entities), scope, pool),
    }
    vector_hits, vector_skipped = channel_vector(store, query, embedder, scope, pool)
    ranked["vector"] = vector_hits

    fused = {}
    provenance = {}
    for channel, uids in ranked.items():
        weight = weights.get(channel, 1.0)
        for rank, uid in enumerate(uids, 1):
            fused[uid] = fused.get(uid, 0.0) + weight / (RRF_K + rank)
            provenance.setdefault(uid, {})[channel] = rank

    ordered = sorted(fused.items(), key=lambda pair: (-pair[1], pair[0]))
    results = []
    filtered_low_coverage = 0
    for uid, score in ordered:
        if len(results) >= limit:
            break
        if score < MIN_FUSED_SCORE:
            continue
        channels = provenance.get(uid, {})
        endorsed = any(c in channels for c in HIGH_PRECISION_CHANNELS)
        if not endorsed and coverage.get(uid, 0.0) < MIN_COVERAGE:
            filtered_low_coverage += 1
            continue
        row = store.item(uid)
        if row is None:
            continue
        results.append({
            "item_uid": uid, "score": round(score, 6),
            "item_type": row["item_type"], "item_id": row["item_id"],
            "title": row["title"], "text": row["text"],
            "status": row["status"], "authority": row["authority"],
            "branch": row["branch"], "occurred_at": row["occurred_at"],
            "paths": json.loads(row["paths_json"]),
            "channels": channels,
            "coverage": round(coverage.get(uid, 0.0), 4),
        })

    latency_ms = (time.time() - started) * 1000.0
    active = sorted(c for c, uids in ranked.items() if uids)
    return {
        "status": OK if results else NO_RELIABLE_MATCH,
        "results": results,
        "channels_active": active,
        "channels_available": sorted(
            c for c in weights
            if c != "fts" or store.caps.get(schema.CAP_FTS5)),
        "vector_skipped": vector_skipped,
        "filtered_low_coverage": filtered_low_coverage,
        "latency_ms": round(latency_ms, 3),
    }
