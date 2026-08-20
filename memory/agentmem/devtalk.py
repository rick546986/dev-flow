"""Project Understanding Mode 的候選知識生命週期(§14-§18)。

這一層服務的互動是「聊懂一個主題」,不是寫程式。它的三條紀律:

①**主動,不被動**(§15)。使用者說「想聊 PGS」時,先自己去看 schema / model /
  migration / 既有記憶,把**不確定的地方**變成具體問題再問 —— 而不是等使用者
  把知識口述完。`probe()` 就是這一步:它產出 open question 清單與已知事實清單。

②**transcript 不是 durable memory**(§16)。每一句對話只進 local transcript;
  進 Git 的是萃取後的結構化知識。流程固定:

      對話 → local transcript → 萃取 → candidate → 確認/授權 → 固化 → .dev-flow

③**不要每說一句話就把 repository 弄 dirty**(§17)。durable 寫入只發生在
  checkpoint / session end / 明確存檔 —— 中間全部留 local。

修正(§18/§31):使用者或 agent 之後推翻先前的說法時,走 `correct()` ——
新知識 supersede 舊知識,舊的留著(看得到轉折才叫記憶,不是覆蓋)。
"""
import json
import os
import re

from . import durable, paths, signal, store as store_mod, sync, textnorm, truth

MODE = "understanding"

# probe 會去翻的檔案類型(按「這裡通常寫著 entity 語意」排序)。
# 刻意不掃整個 repo:主動學習的價值在「問對問題」,不在「讀完所有檔案」。
_PROBE_GLOBS = (
    ("schema", ("**/schema.*", "**/schema/**/*", "**/*.prisma", "**/*.sql")),
    ("migration", ("**/migrations/**/*", "**/migrate/**/*")),
    ("model", ("**/models/**/*", "**/model/**/*", "**/entities/**/*",
               "**/domain/**/*")),
    ("doc", ("docs/**/*.md", "README.md")),
)

_MAX_PROBE_FILES = 40


class DevTalkError(RuntimeError):
    """理解模式的狀態錯誤(例如對已結束的 session 繼續寫入)。"""


# ─────────────────────────── session ────────────────────────────────────────
def start(store, repo_root, topic, snapshot=None, now=None):
    """開一個理解模式 session,並回傳 inspection brief(主動學習的起點)。"""
    snapshot = snapshot or {}
    session_id = store.start_session(
        topic, mode=MODE, branch=snapshot.get("branch"),
        head_sha=snapshot.get("head_sha"), now=now)
    return {"session_id": session_id, "topic": topic,
            "brief": probe(store, repo_root, topic)}


def record_turn(store, session_id, role, text, now=None):
    """記一輪對話 —— **只**進 local transcript,永遠不進 Git。"""
    session = store.session(session_id)
    if session is None:
        raise DevTalkError("session 不存在:{0}".format(session_id))
    if session["status"] != "OPEN":
        raise DevTalkError(
            "session {0} 已結束({1});要繼續請開新的 session".format(
                session_id, session["status"]))
    return store.add_turn(session_id, role, text, now=now)


def end(store, repo_root, session_id, now=None):
    """收尾:先 checkpoint(固化已確認的候選),再關 session。"""
    result = checkpoint(store, repo_root, session_id, now=now)
    store.end_session(session_id, "CLOSED", now=now)
    return result


# ─────────────────────────── 主動學習 ────────────────────────────────────────
def probe(store, repo_root, topic):
    """針對主題,先自己看一輪,產出「已知」與「不確定」兩份清單。

    回傳 dict:
      known_knowledge / known_facts   已經記得的東西(不要再問一遍)
      repo_signals                    repo 裡疑似相關的檔案(repo-relative)
      candidate_entities              從檔名/既有記憶抽出的 entity 候選
      open_questions                  **具體**問題(帶上下文,不是「請說明」)
      conflicts                       既有的 code/domain 衝突(要優先釐清)
    """
    tokens = [t for t in textnorm.tokens(topic) if len(t) >= 2]
    symbols = textnorm.symbols(topic)
    known_knowledge = [
        {"kind": row["kind"], "key": row["key"], "title": row["title"],
         "authority": row["authority"], "status": row["status"]}
        for row in store.knowledge(statuses=("CONFIRMED", "CANDIDATE",
                                             "CONFLICT"), limit=200)
        if _matches(row["key"] + " " + row["title"] + " " + row["body"], tokens,
                    symbols)]
    known_facts = [
        {"entity": "{0}.{1}".format(row["entity_type"], row["entity_key"]),
         "fact_key": row["fact_key"], "value": row["value"],
         "status": row["status"]}
        for row in store.facts(statuses=truth.LIVE_STATUSES, limit=200)
        if _matches("{0} {1} {2} {3}".format(
            row["entity_type"], row["entity_key"], row["fact_key"],
            row["value"]), tokens, symbols)]
    repo_signals = _repo_signals(repo_root, tokens, symbols)
    candidate_entities = _candidate_entities(repo_signals, known_knowledge)
    conflicts = [c for c in truth.open_conflicts(store)
                 if _matches(c["key"] + " " + c["title"], tokens, symbols)]
    return {
        "topic": topic,
        "known_knowledge": known_knowledge,
        "known_facts": known_facts,
        "repo_signals": repo_signals,
        "candidate_entities": candidate_entities,
        "conflicts": conflicts,
        "open_questions": _open_questions(topic, known_knowledge,
                                          candidate_entities, conflicts),
    }


def _matches(haystack, tokens, symbols):
    lowered = haystack.casefold()
    for symbol in symbols:
        if textnorm.normalize_symbol(symbol) in textnorm.normalize_symbol(lowered):
            return True
    hits = sum(1 for token in tokens if token in lowered)
    return hits >= 1


def _repo_signals(repo_root, tokens, symbols):
    """找疑似相關的檔案。只回 repo-relative 路徑(絕不外洩絕對路徑)。"""
    import glob
    signals = []
    seen = set()
    for category, patterns in _PROBE_GLOBS:
        for pattern in patterns:
            for match in glob.glob(os.path.join(repo_root, pattern),
                                   recursive=True):
                if not os.path.isfile(match):
                    continue
                try:
                    rel = paths.to_repo_relative(match, repo_root)
                except paths.NonPortablePath:
                    continue
                if rel in seen or rel.startswith(".git/"):
                    continue
                if not _matches(rel, tokens, symbols):
                    continue
                seen.add(rel)
                signals.append({"category": category, "path": rel})
                if len(signals) >= _MAX_PROBE_FILES:
                    return signals
    return signals


_WORD = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")


def _candidate_entities(repo_signals, known_knowledge):
    known = {row["key"].casefold() for row in known_knowledge}
    counts = {}
    for entry in repo_signals:
        stem = os.path.splitext(os.path.basename(entry["path"]))[0]
        for word in _WORD.findall(stem):
            key = word.casefold()
            if key in known or key in ("index", "main", "test", "utils",
                                       "readme", "types"):
                continue
            counts[word] = counts.get(word, 0) + 1
    return [w for w, _n in sorted(counts.items(), key=lambda p: (-p[1], p[0]))][:12]


def _open_questions(topic, known_knowledge, candidate_entities, conflicts):
    """產**具體**問題。空泛的「請說明一下」不算問題,不會產出。"""
    questions = []
    for record in conflicts:
        questions.append(
            "「{0}」目前是衝突狀態:記憶說「{1}」,程式觀察不同。"
            "以哪一邊為準?".format(record["key"], record["title"]))
    if candidate_entities:
        questions.append(
            "從 repo 看到這些名詞:{0}。它們在真實世界各自代表什麼?"
            "有沒有哪兩個其實是同一件事(或名字一樣但意思不同)?".format(
                ", ".join(candidate_entities[:6])))
    if len(candidate_entities) >= 2:
        questions.append(
            "{0} 與 {1} 之間是一對多、多對多、還是同一層?"
            "有沒有例外情形?".format(candidate_entities[0], candidate_entities[1]))
    for record in known_knowledge:
        if record["status"] == "CANDIDATE":
            questions.append(
                "「{0}」我先前記成「{1}」但還沒確認過,這樣對嗎?".format(
                    record["key"], record["title"]))
    if not questions:
        questions.append(
            "關於「{0}」我目前沒有任何記憶。先從最上層問:"
            "誰會用到它?一筆資料從產生到結案會經過哪些人與哪些狀態?".format(topic))
    questions.append(
        "上面這些理解裡,有哪一條**在特殊情況下不成立**?例外通常是最重要的一條。")
    return questions


# ─────────────────────────── candidate ──────────────────────────────────────
def propose(store, session_id, target_kind, payload, authority, note="",
            now=None):
    """把萃取出來的知識登記成候選(PENDING;不寫 Git)。

    敏感內容在**登記時**就先標記 —— 等到 consolidation 才發現的話,這段內容
    已經在 local 裡被當成「準備進 Git 的東西」處理過一輪了。
    """
    blob = json.dumps(payload, ensure_ascii=False)
    sensitive = bool(signal.scan_sensitive(blob))
    return store.add_candidate(session_id, target_kind, payload, authority,
                               sensitive=sensitive, note=note, now=now)


def confirm(store, candidate_id, now=None):
    """使用者確認 → CONFIRMED(仍不寫 Git;等 checkpoint)。"""
    store.set_candidate_status(candidate_id, "CONFIRMED", now=now)
    return candidate_id


def reject(store, candidate_id, reason="", now=None):
    store.set_candidate_status(candidate_id, "REJECTED", note=reason, now=now)
    return candidate_id


def correct(store, session_id, kind, key, title, body="",
            authority="user_confirmed", reason="", now=None):
    """修正先前的知識:舊筆 SUPERSEDED,新筆成為候選。

    不直接改舊筆的內容 —— 看得到「原本記成什麼、後來改成什麼」才叫記憶。
    """
    now = now or store_mod.utc_now()
    existing = store.knowledge(kind=kind, key=key,
                               statuses=("CANDIDATE", "CONFIRMED", "CONFLICT"),
                               limit=1)
    payload = {"key": key, "title": title, "body": body, "status": "CONFIRMED",
               "confidence": 0.95, "correction_reason": reason}
    if existing:
        payload["supersedes"] = existing[0]["knowledge_id"]
        store.upsert_knowledge({
            "knowledge_id": existing[0]["knowledge_id"], "kind": kind, "key": key,
            "title": existing[0]["title"], "body": existing[0]["body"],
            "authority": existing[0]["authority"], "status": "SUPERSEDED",
            "confidence": existing[0]["confidence"],
            "recorded_at": existing[0]["recorded_at"], "superseded_at": now,
            "evidence": json.loads(existing[0]["evidence_json"]),
            "conflicts": json.loads(existing[0]["conflicts_json"]),
            "implemented": (None if existing[0]["implemented"] is None
                            else bool(existing[0]["implemented"])),
            "durable": bool(existing[0]["durable"])})
    candidate_id = propose(store, session_id, kind, payload, authority,
                           note=reason, now=now)
    confirm(store, candidate_id, now=now)
    return candidate_id


# ─────────────────────────── checkpoint ─────────────────────────────────────
def checkpoint(store, repo_root, session_id, now=None):
    """固化這個 session 已確認的候選(durable 寫入的唯一時機)。"""
    result = sync.consolidate(repo_root, store, session_id, now=now)
    pending = store.candidates(session_id, statuses=("PENDING",))
    result["still_pending"] = [
        {"candidate_id": row["candidate_id"], "target_kind": row["target_kind"],
         "title": row["payload"].get("title", "")} for row in pending]
    result["durable_root"] = os.path.basename(durable.root(repo_root))
    return result


def status(store, session_id):
    session = store.session(session_id)
    if session is None:
        raise DevTalkError("session 不存在:{0}".format(session_id))
    counts = {}
    for state in ("PENDING", "CONFIRMED", "REJECTED", "CONSOLIDATED",
                  "LOCAL_ONLY"):
        counts[state] = len(store.candidates(session_id, statuses=(state,)))
    return {"session": session, "turns": len(store.turns(session_id)),
            "candidates": counts}
