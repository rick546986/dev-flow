"""修正歷史(revision lineage):current view + append-only revision。

**問題**:`.dev-flow/knowledge/domain/<key>.yaml` 是**現況物化視圖** ——
correct() 之後它只剩新版。另一台機器 clone → 沒有 local DB → rebuild,
就只重建得出新版。「以前理解成什麼、什麼時候改、為什麼改」這段 lineage 消失。
Git commit history 也許看得到,但 **Agent Memory 自己查不到** ——
而查得到才是 durable memory 存在的理由。

**解法**(刻意維持現有簡單架構,不引入 event sourcing framework):

    current materialized view   `.dev-flow/knowledge|state|decisions/…`
  + append-only revision event  `.dev-flow/events/YYYY/MM/<session>.jsonl`

三種 supersede 走**同一套語意**,不是只修 domain knowledge 一種:

    knowledge_corrected   domain / invariant / entity / relationship / intent
    fact_superseded       implementation truth 的重新驗證換了值
    decision_superseded   同一個 decision key 被新的決定取代

**寫入時機**:revision 先落 local `revisions` 表(durable=0),
由 `sync.consolidate()` 一併刷進 `.dev-flow/` ——
`consolidate()` 仍是唯一的 durable writer,這裡不另開第二條寫入路徑。

**守衛**:revision 一樣要過 Signal Gate 的敏感內容與絕對路徑檢查。
系統產生的記錄不因為「是系統產生的」就跳過守衛 —— 被更正掉的舊值裡一樣可能
有人貼過連線字串。
"""
import json

from . import ids, signal, store as store_mod

KNOWLEDGE_CORRECTED = "knowledge_corrected"
FACT_SUPERSEDED = "fact_superseded"
DECISION_SUPERSEDED = "decision_superseded"

REVISION_KINDS = (KNOWLEDGE_CORRECTED, FACT_SUPERSEDED, DECISION_SUPERSEDED)

_TITLES = {
    KNOWLEDGE_CORRECTED: "知識更正",
    FACT_SUPERSEDED: "現況事實更新",
    DECISION_SUPERSEDED: "決定被取代",
}


def _clean(value):
    return "" if value is None else str(value)


def build_knowledge_revision(memory_kind, key, previous, new, reason="",
                             session_id=None, occurred_at=None, evidence=()):
    """previous / new 皆為 knowledge row(dict-like)。"""
    return _finish({
        "kind": KNOWLEDGE_CORRECTED,
        "memory_kind": memory_kind,
        "key": key,
        "previous_id": _clean(previous.get("knowledge_id")),
        "new_id": _clean(new.get("knowledge_id")),
        "previous_title": _clean(previous.get("title")),
        "new_title": _clean(new.get("title")),
        "previous_body": _clean(previous.get("body")),
        "new_body": _clean(new.get("body")),
        "previous_status": _clean(previous.get("status")),
        "new_status": _clean(new.get("status")),
        "previous_authority": _clean(previous.get("authority")),
        "new_authority": _clean(new.get("authority")),
        "reason": _clean(reason),
    }, session_id, occurred_at, evidence)


def build_fact_revision(entity_type, entity_key, fact_key, previous, new,
                        reason="", session_id=None, occurred_at=None,
                        evidence=()):
    return _finish({
        "kind": FACT_SUPERSEDED,
        "memory_kind": "implementation",
        "key": "{0}.{1}.{2}".format(entity_type, entity_key, fact_key),
        "previous_id": _clean(previous.get("fact_id")),
        "new_id": _clean(new.get("fact_id")),
        "previous_value": _clean(previous.get("value")),
        "new_value": _clean(new.get("value")),
        "previous_status": _clean(previous.get("status")),
        "new_status": _clean(new.get("status")),
        "previous_authority": _clean(previous.get("source_type")),
        "new_authority": _clean(new.get("source_type")),
        "reason": _clean(reason) or "重新驗證後觀察到不同的值",
    }, session_id, occurred_at, evidence)


def build_decision_revision(key, previous, new, reason="", session_id=None,
                            occurred_at=None, evidence=()):
    return _finish({
        "kind": DECISION_SUPERSEDED,
        "memory_kind": "decision",
        "key": key,
        "previous_id": _clean(previous.get("decision_id")),
        "new_id": _clean(new.get("decision_id")),
        "previous_title": _clean(previous.get("title")),
        "new_title": _clean(new.get("title")),
        "previous_body": _clean(previous.get("decision")),
        "new_body": _clean(new.get("decision")),
        "previous_status": _clean(previous.get("status")),
        "new_status": _clean(new.get("status")),
        "previous_authority": "",
        "new_authority": "",
        "reason": _clean(reason),
    }, session_id, occurred_at, evidence)


def _finish(record, session_id, occurred_at, evidence):
    record["occurred_at"] = occurred_at or store_mod.utc_now()
    record["session_id"] = session_id or ""
    record["signal"] = signal.HIGH
    if evidence:
        record["evidence"] = [dict(sorted(item.items())) for item in evidence]
    record["title"] = render_title(record)
    record["body"] = render_body(record)
    return record


def render_title(record):
    """標題要**自我解釋**:它會單獨出現在歷史清單與檢索結果裡。

    只寫「知識更正:registration」的話,使用者問「之前 registration 改過什麼」
    時,這筆記憶的標題完全沒有回答那個問題 —— 而且相關性門檻也吃不到足夠的
    內容詞,結果是「歷史明明存在卻查不到」。舊值與新值都放進標題。
    """
    label = _TITLES[record["kind"]]
    if record["kind"] == FACT_SUPERSEDED:
        previous = record.get("previous_value", "")
        new = record.get("new_value", "")
    else:
        previous = record.get("previous_title", "")
        new = record.get("new_title", "")
    if previous and new:
        return "{0}:{1} —— 原本理解成「{2}」,後來改為「{3}」".format(
            label, record["key"], previous, new)
    return "{0}:{1}".format(label, record["key"])


def render_body(record):
    """給人讀、也給 retrieval 索引的文字。

    舊值與新值都要在文字裡 —— 「以前理解成什麼」是這筆記憶的**主要價值**,
    只寫新值等於又回到現況視圖,查不到轉折。
    """
    lines = []
    if record["kind"] == FACT_SUPERSEDED:
        lines.append("原本:{0}".format(record.get("previous_value", "")))
        lines.append("改為:{0}".format(record.get("new_value", "")))
    else:
        lines.append("原本:{0}".format(record.get("previous_title", "")))
        if record.get("previous_body"):
            lines.append("原本內容:{0}".format(record["previous_body"]))
        lines.append("改為:{0}".format(record.get("new_title", "")))
        if record.get("new_body"):
            lines.append("新內容:{0}".format(record["new_body"]))
    if record.get("reason"):
        lines.append("原因:{0}".format(record["reason"]))
    lines.append("這是一筆修正紀錄:先前的理解已被取代,舊版本保留於此供追溯。")
    lines.append("狀態:{0} → {1}".format(record.get("previous_status", ""),
                                          record.get("new_status", "")))
    if record.get("previous_authority") or record.get("new_authority"):
        lines.append("權威:{0} → {1}".format(
            record.get("previous_authority", ""),
            record.get("new_authority", "")))
    return "\n".join(lines)


def record_pending(store, revision):
    """把 revision 記進 local `revisions` 表(durable=0),等 consolidation 刷出去。

    刻意不直接寫 `.dev-flow/` —— `sync.consolidate()` 是唯一的 durable writer,
    這裡多開一條寫入路徑會讓「什麼時候會弄髒工作樹」變得不可預測。
    """
    if revision["kind"] not in REVISION_KINDS:
        raise ValueError("未知的 revision kind:{0!r}".format(revision["kind"]))
    revision_id = ids.new_id("event")
    with store.conn:
        store.conn.execute(
            "INSERT INTO revisions(revision_id, project_id, session_id, kind,"
            " memory_kind, key, payload_json, occurred_at, durable)"
            " VALUES(?,?,?,?,?,?,?,?,0)",
            (revision_id, store.project_id, revision.get("session_id") or None,
             revision["kind"], revision.get("memory_kind"), revision["key"],
             json.dumps(revision, ensure_ascii=False, sort_keys=True),
             revision["occurred_at"]))
    return revision_id


def pending(store, session_id=None):
    sql = ["SELECT * FROM revisions WHERE project_id=? AND durable=0"]
    args = [store.project_id]
    if session_id:
        # session 為空的 revision(例如 CLI verify 產生的)一併帶走 ——
        # 否則它們會永遠留在 local,而那正是這一題要修的失憶。
        sql.append("AND (session_id=? OR session_id IS NULL)")
        args.append(session_id)
    sql.append("ORDER BY occurred_at, revision_id")
    out = []
    for row in store.conn.execute(" ".join(sql), args):
        record = dict(row)
        record["payload"] = json.loads(record["payload_json"])
        out.append(record)
    return out


def mark_durable(store, revision_ids, durable_ref=""):
    if not revision_ids:
        return
    with store.conn:
        store.conn.executemany(
            "UPDATE revisions SET durable=1, durable_ref=? WHERE revision_id=?",
            [(durable_ref, rid) for rid in revision_ids])
