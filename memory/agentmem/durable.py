"""`.dev-flow/` —— Git-synced durable Agent Memory(唯一 durable 寫入口)。

這個目錄不是「一般文件目錄」,是**可攜的 project brain**:clone 到任何機器、
任何路徑,跑一次 dev-setup 就能把 local index 重建回來。

    .dev-flow/
    ├── project.yaml                    identity(見 identity.py)
    ├── state/implementation/<entity>.yaml   A. implementation truth(LVP facts)
    ├── knowledge/entities/<key>.yaml
    ├── knowledge/relationships/<key>.yaml
    ├── knowledge/invariants/<key>.yaml
    ├── knowledge/domain/<key>.yaml     B. domain knowledge
    ├── knowledge/intents/<key>.yaml    C. intent(planned ≠ implemented)
    ├── decisions/DEC-<key>.md          E. decision
    ├── events/YYYY/MM/<session>.jsonl  D. historical event(append-only)
    └── skills/<key>.yaml               F. procedural skill

**禁止進這裡的東西**(§5):SQLite DB、embedding 向量、raw transcript、cache、
暫時性 retrieval 結果。那些住 local runtime,刪掉可重建。

**Git conflict 設計**(§30):
- events 一律 per-session 分檔(`events/YYYY/MM/<session-id>.jsonl`)——
  Mac 與 Windows 同時新增會落在**不同檔**,不會 append 同一個 events.jsonl。
- state / knowledge 檔一律 deterministic serialization(key 順序固定、LF、
  無尾隨空白),同一份資料寫兩次 byte 相同 → 沒有假 diff。
- 讀檔時偵測 Git conflict 標記 → **fail-loud**。同一個 fact 真的衝突時不得
  靜默 last-write-wins,那會讓兩台機器的記憶悄悄分岔。
"""
import hashlib
import json
import os
import re
import tempfile

from . import DURABLE_SCHEMA_VERSION, identity, paths, yamlmini

STATE_DIR = ("state", "implementation")
KNOWLEDGE_DIRS = {
    "entity": ("knowledge", "entities"),
    "relationship": ("knowledge", "relationships"),
    "invariant": ("knowledge", "invariants"),
    "domain": ("knowledge", "domain"),
    "intent": ("knowledge", "intents"),
}
DECISION_DIR = ("decisions",)
EVENT_DIR = ("events",)
SKILL_DIR = ("skills",)

DECISION_FENCE = "dev-flow-decision"

_SLUG_SAFE = re.compile(r"[^A-Za-z0-9._-]+")
_CONFLICT = re.compile(r"^(?:<{7}|={7}|>{7})", re.M)

_FACT_KEY_ORDER = ["fact_key", "value", "status", "confidence"]
_STATE_KEY_ORDER = ["schema_version", "entity_type", "entity_key", "facts"]
_KNOWLEDGE_KEY_ORDER = ["schema_version", "kind", "key", "title", "authority",
                        "status", "implemented", "confidence", "body"]
_SKILL_KEY_ORDER = ["schema_version", "key", "title", "status", "preconditions",
                    "verification", "steps"]
_DECISION_KEY_ORDER = ["schema_version", "key", "status", "decided_at",
                       "decision_id"]


class DurableError(RuntimeError):
    """durable 檔案不可信(conflict 標記 / 格式錯 / 路徑不可攜)—— 一律 fail-loud。"""


def _assert_portable_content(*texts):
    """durable writer 邊界:敏感內容與絕對路徑不得進 Git。

    這是最後一道閘。呼叫端(consolidate / legacy promote)也會先過
    `signal.gate`,但 writer 自己必須再擋一次 —— 第二個直接呼叫者
    不該成為第二個繞過點。
    """
    from . import signal
    verdict = signal.gate("domain_clarification", extra_texts=texts)
    if not verdict["durable_allowed"]:
        raise DurableError("; ".join(verdict["reasons"]))


# ─────────────────────────── 檔名 ────────────────────────────────────────────
def slug(value):
    """把任意 key 轉成穩定、跨平台安全的檔名。

    中文 key(domain knowledge 很常見)不能直接當檔名 —— Windows/macOS 的檔名
    正規化(NFC/NFD、大小寫)會讓同一個 key 在兩台機器上變成兩個檔。
    規則:ASCII 安全字元保留,其餘一律換成 `-`,並**永遠**接一段內容 hash ——
    hash 讓「不同 key 被正規化成同一個檔名」不可能發生。
    """
    if not isinstance(value, str) or not value.strip():
        raise DurableError("key 不可為空")
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    ascii_part = _SLUG_SAFE.sub("-", value).strip("-.")[:48]
    if not ascii_part:
        ascii_part = "k"
    return "{0}.{1}".format(ascii_part, digest)


def root(repo_root_path):
    return identity.durable_root(repo_root_path)


def _path(repo_root_path, parts, name=None):
    target = os.path.join(root(repo_root_path), *parts)
    return os.path.join(target, name) if name else target


def _read_text(path):
    with open(path, encoding="utf-8") as stream:
        text = stream.read()
    if _CONFLICT.search(text):
        raise DurableError(
            "{0} 含 Git conflict 標記 —— 同一筆記憶在兩台機器上分岔了。"
            "請人工裁決後再讓工具讀寫(靜默 last-write-wins 會讓其中一邊的記憶消失)"
            .format(path))
    return text


def _atomic_write(path, text):
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _guard_paths(values):
    for value in values or ():
        paths.assert_portable(value)
    return list(values or ())


# ─────────────────────────── A. implementation truth ────────────────────────
def state_file(repo_root_path, entity_type, entity_key):
    return _path(repo_root_path, STATE_DIR,
                 slug(entity_type + "/" + entity_key) + ".yaml")


def read_state(repo_root_path, entity_type, entity_key):
    path = state_file(repo_root_path, entity_type, entity_key)
    if not os.path.isfile(path):
        return None
    data = yamlmini.load(_read_text(path))
    if not isinstance(data, dict) or "facts" not in data:
        raise DurableError("{0} 不是合法的 state 檔(缺 facts)".format(path))
    return data


def write_state(repo_root_path, entity_type, entity_key, facts):
    """寫入一個 entity 的全部 durable facts(deterministic;整檔取代)。

    整檔取代而不是 append:facts 有 supersede 語意,append 會讓同一個 fact_key
    的多個版本在檔案裡堆疊,讀取端得自己猜哪個是現行 —— 猜就會錯。
    """
    normalized = []
    for fact in facts:
        record = {
            "fact_key": fact["fact_key"],
            "value": str(fact["value"]),
            "status": fact["status"],
            "confidence": round(float(fact.get("confidence", 0.0)), 4),
            "recorded_at": fact.get("recorded_at"),
        }
        for optional in ("effective_at", "superseded_at", "superseded_by",
                         "source_type", "source_ref", "source_commit",
                         "verified_at", "verified_commit"):
            if fact.get(optional):
                record[optional] = fact[optional]
        for counter in ("verification_count", "contradiction_count"):
            if fact.get(counter):
                record[counter] = int(fact[counter])
        deps = _guard_paths(fact.get("dependencies") or ())
        if deps:
            record["dependencies"] = sorted(deps)
        fingerprints = fact.get("fingerprints") or {}
        if fingerprints:
            _guard_paths(fingerprints.keys())
            record["fingerprints"] = dict(sorted(fingerprints.items()))
        normalized.append(record)
    normalized.sort(key=lambda r: (r["fact_key"], r.get("recorded_at") or ""))
    payload = {
        "schema_version": DURABLE_SCHEMA_VERSION,
        "entity_type": entity_type,
        "entity_key": entity_key,
        "facts": normalized,
    }
    text = yamlmini.dump(
        payload, key_order=_STATE_KEY_ORDER + _FACT_KEY_ORDER,
        header="A. IMPLEMENTATION TRUTH —— 程式現在實際怎麼運作(LVP current truth)。\n"
               "dependencies/fingerprints 是失效判定的依據:依賴檔變了 → 本機先轉 STALE,"
               "重新驗證後才更新這裡。")
    path = state_file(repo_root_path, entity_type, entity_key)
    _atomic_write(path, text)
    return path


def iter_states(repo_root_path):
    directory = _path(repo_root_path, STATE_DIR)
    if not os.path.isdir(directory):
        return
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".yaml"):
            continue
        data = yamlmini.load(_read_text(os.path.join(directory, name)))
        if isinstance(data, dict) and "facts" in data:
            yield data


def has_mirrorable_content(repo_root_path):
    """`.dev-flow/` 是否有任何會被 rebuild 鏡射的紀錄。

    project.yaml 是 identity,不是鏡射項目。空 facts 的 state 檔也不算。
    缺世代時只有「DB 沒有 durable 列 **而且** 樹也沒有可鏡射內容」
    才允許只蓋章。
    """
    for state in iter_states(repo_root_path):
        if state.get("facts"):
            return True
    if any(iter_knowledge(repo_root_path)):
        return True
    if any(iter_decisions(repo_root_path)):
        return True
    if any(iter_skills(repo_root_path)):
        return True
    if any(iter_events(repo_root_path)):
        return True
    return False


# ─────────────────────────── B/C/G. knowledge ───────────────────────────────
def knowledge_file(repo_root_path, kind, key):
    if kind not in KNOWLEDGE_DIRS:
        raise DurableError("未知的 knowledge kind:{0!r}".format(kind))
    return _path(repo_root_path, KNOWLEDGE_DIRS[kind], slug(key) + ".yaml")


def write_knowledge(repo_root_path, record):
    _assert_portable_content(record.get("title", ""), record.get("body", ""))
    kind = record["kind"]
    payload = {
        "schema_version": DURABLE_SCHEMA_VERSION,
        "kind": kind,
        "key": record["key"],
        "title": record["title"],
        "authority": record["authority"],
        "status": record.get("status", "CANDIDATE"),
        "confidence": round(float(record.get("confidence", 0.0)), 4),
        "recorded_at": record.get("recorded_at"),
    }
    if record.get("body"):
        payload["body"] = record["body"]
    if record.get("implemented") is not None:
        # intent 專用:planned 與 implemented 必須在檔面上就分得出來(§20)
        payload["implemented"] = bool(record["implemented"])
    for optional in ("superseded_at", "superseded_by"):
        if record.get(optional):
            payload[optional] = record[optional]
    evidence = record.get("evidence") or []
    if evidence:
        payload["evidence"] = _normalize_evidence(evidence)
    conflicts = record.get("conflicts") or []
    if conflicts:
        payload["conflicts"] = [
            {k: v for k, v in sorted(c.items())} for c in conflicts]
    text = yamlmini.dump(
        payload, key_order=_KNOWLEDGE_KEY_ORDER,
        header="{0} knowledge —— authority 決定誰能覆寫誰(見 truth.py)。\n"
               "code 只能 SUPPORT 或 CONFLICT 已確認的 domain truth,"
               "不能直接 override。".format(kind))
    path = knowledge_file(repo_root_path, kind, record["key"])
    _atomic_write(path, text)
    return path


def _normalize_evidence(evidence):
    out = []
    for item in evidence:
        record = {k: v for k, v in item.items() if v is not None}
        if record.get("type") == "file" and record.get("ref"):
            paths.assert_portable(record["ref"])
        out.append({k: record[k] for k in sorted(record)})
    out.sort(key=lambda r: (r.get("type", ""), str(r.get("ref", ""))))
    return out


def iter_knowledge(repo_root_path):
    for kind, parts in sorted(KNOWLEDGE_DIRS.items()):
        directory = _path(repo_root_path, parts)
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if not name.endswith(".yaml"):
                continue
            data = yamlmini.load(_read_text(os.path.join(directory, name)))
            if isinstance(data, dict) and data.get("kind"):
                yield data


# ─────────────────────────── E. decision ────────────────────────────────────
def decision_file(repo_root_path, key):
    return _path(repo_root_path, DECISION_DIR, "DEC-" + slug(key) + ".md")


def write_decision(repo_root_path, record):
    """decision 用 Markdown(人要讀),機器欄位放在一個 fenced block 裡。

    為什麼不用純 YAML:decision 的價值在 reason / tradeoff 的散文,那是人寫給
    半年後的人看的。純 YAML 會讓人不想寫;純 Markdown 會讓機器讀不到 status。
    """
    header = {
        "schema_version": DURABLE_SCHEMA_VERSION,
        "key": record["key"],
        "status": record.get("status", "ACCEPTED"),
        "decided_at": record.get("decided_at") or record.get("recorded_at"),
    }
    if record.get("decision_id"):
        header["decision_id"] = record["decision_id"]
    if record.get("supersedes"):
        header["supersedes"] = record["supersedes"]
    evidence = record.get("evidence") or []
    if evidence:
        header["evidence"] = _normalize_evidence(evidence)
    block = yamlmini.dump(header, key_order=_DECISION_KEY_ORDER)
    body = [
        "# DEC-{0} — {1}".format(record["key"], record["title"]),
        "",
        "```" + DECISION_FENCE,
        block.rstrip("\n"),
        "```",
        "",
        "## Decision",
        "",
        record.get("decision", "").strip() or "(未填)",
        "",
        "## Alternatives",
        "",
        record.get("alternatives", "").strip() or "(未填)",
        "",
        "## Reason",
        "",
        record.get("reason", "").strip() or "(未填)",
        "",
        "## Tradeoff",
        "",
        record.get("tradeoff", "").strip() or "(未填)",
        "",
    ]
    path = decision_file(repo_root_path, record["key"])
    _atomic_write(path, "\n".join(body))
    return path


_SECTION = re.compile(r"^## (Decision|Alternatives|Reason|Tradeoff)\s*$", re.M)


def parse_decision(text):
    m = re.search(r"^```" + DECISION_FENCE + r"\s*$(.*?)^```\s*$",
                  text, re.M | re.S)
    if not m:
        raise DurableError(
            "decision 檔缺 `{0}` fenced block —— 機器讀不到 status,"
            "不接受只有散文的 decision".format(DECISION_FENCE))
    record = yamlmini.load(m.group(1))
    title = ""
    first = re.search(r"^#\s+DEC-\S+\s+—\s+(.*)$", text, re.M)
    if first:
        title = first.group(1).strip()
    record["title"] = title
    sections = {}
    marks = list(_SECTION.finditer(text))
    for i, mark in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        sections[mark.group(1).lower()] = text[mark.end():end].strip()
    for name in ("decision", "alternatives", "reason", "tradeoff"):
        value = sections.get(name, "")
        record[name] = "" if value == "(未填)" else value
    return record


def iter_decisions(repo_root_path):
    directory = _path(repo_root_path, DECISION_DIR)
    if not os.path.isdir(directory):
        return
    for name in sorted(os.listdir(directory)):
        if name.startswith("DEC-") and name.endswith(".md"):
            yield parse_decision(_read_text(os.path.join(directory, name)))


# ─────────────────────────── F. skill ───────────────────────────────────────
def skill_file(repo_root_path, key):
    return _path(repo_root_path, SKILL_DIR, slug(key) + ".yaml")


def write_skill(repo_root_path, record):
    payload = {
        "schema_version": DURABLE_SCHEMA_VERSION,
        "key": record["key"],
        "title": record["title"],
        "status": record.get("status", "CANDIDATE"),
        "recorded_at": record.get("recorded_at"),
    }
    for optional in ("preconditions", "verification"):
        if record.get(optional):
            payload[optional] = record[optional]
    if record.get("steps"):
        payload["steps"] = list(record["steps"])
    for counter in ("success_count", "failure_count"):
        if record.get(counter):
            payload[counter] = int(record[counter])
    evidence = record.get("evidence") or []
    if evidence:
        payload["evidence"] = _normalize_evidence(evidence)
    text = yamlmini.dump(
        payload, key_order=_SKILL_KEY_ORDER,
        header="F. PROCEDURAL SKILL —— 怎麼做某件事(deploy/debug/migration/release)。")
    path = skill_file(repo_root_path, record["key"])
    _atomic_write(path, text)
    return path


def iter_skills(repo_root_path):
    directory = _path(repo_root_path, SKILL_DIR)
    if not os.path.isdir(directory):
        return
    for name in sorted(os.listdir(directory)):
        if name.endswith(".yaml"):
            data = yamlmini.load(_read_text(os.path.join(directory, name)))
            if isinstance(data, dict) and data.get("key"):
                yield data


# ─────────────────────────── D. events(per-session 分檔)────────────────────
def event_file(repo_root_path, session_id, occurred_at):
    """`events/YYYY/MM/<session-id>.jsonl` —— 每個 session/consolidation 自己一個檔。

    §30:不要讓所有機器 append 同一個 events.jsonl。Mac 與 Windows 同時新增
    落在不同檔 = Git 看到的是兩個新檔而不是同一行的兩種版本。
    """
    stamp = (occurred_at or "")[:7]
    if not re.match(r"^\d{4}-\d{2}$", stamp):
        raise DurableError(
            "event 時間戳不合法({0!r});需要 ISO-8601(YYYY-MM-…)".format(occurred_at))
    year, month = stamp.split("-")
    return _path(repo_root_path, EVENT_DIR + (year, month), slug(session_id) + ".jsonl")


def _canonical(payload):
    """去重比對用的正規形式 —— 同內容一定同字串,不同內容一定不同字串。"""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _existing_events(path):
    """回傳 (原樣文字, {event_id: 正規化內容})。壞行一律 fail-loud。

    去重需要知道檔裡已經有哪些 id,而那要逐行 parse。讀不懂的行不得被當成
    「沒有這筆」跳過 —— 那會讓重寫把它旁邊補一筆重複的,或整檔取代時把它
    吃掉。同 `iter_events()`:壞掉的耐久內容由人裁決,不由工具猜。

    帶回內容(不只是 id)是因為「id 已經在檔裡」只有在 id 真的決定內容時
    才等於「這筆已經寫過了」。撞號時要看得出來,不能猜。
    """
    if not os.path.isfile(path):
        return "", {}
    text = _read_text(path)
    seen = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except ValueError as exc:
            raise DurableError(
                "{0}:{1} 不是合法 JSON:{2}".format(path, lineno, exc))
        if isinstance(data, dict) and data.get("event_id"):
            seen[data["event_id"]] = _canonical(data)
    if text and not text.endswith("\n"):
        text += "\n"
    return text, seen


def append_events(repo_root_path, session_id, records):
    """append 一批事件(同一 session 同一月 → 同一檔)。回傳寫入的檔案清單。

    **以 `event_id` 去重、整檔原子取代**,不是 open("a") 直接寫。

    「先寫檔、才動 local 狀態」對 deterministic 整檔取代的 writer 夠用:
    `write_state()` 寫完後行程死掉,重跑寫的是同一份內容取代同一個檔,
    它會收斂。append-only 的 JSONL 不是 —— 它**不是 keyed storage**,
    所以同一個 `event_id` 重跑會變成第二行。而檔案系統與 SQLite 之間沒有
    共同的 transaction,「append 成功、local 還沒前進」這個視窗消不掉,
    只能讓重跑冪等:已經在檔裡的 id 就不再寫。

    原子取代同時解掉第二件事:open("a") 中途斷電會留下半行,而半行讓整個
    檔案之後都讀不出來(`iter_events` fail-loud)。

    沒有 `event_id` 的事件一律拒收:認不出身分的東西無法去重,寫下去就是
    一筆重跑必然變成兩筆的紀錄。這是刻意收緊的契約,不是防禦性檢查。

    **同 id 不同內容一律拒收。**「id 已經在檔裡」只有在 id 真的決定內容時才
    等於「這筆已經寫過了」。推導 id 的來源撞號、或推導規則有瑕疵時,靜默跳過
    會讓第二筆(內容不同的那筆)永遠不存在,而呼叫端會拿到成功。
    """
    pending = {}
    for record in records:
        occurred_at = record.get("occurred_at")
        path = event_file(repo_root_path, session_id, occurred_at)
        payload = {k: v for k, v in record.items() if v is not None}
        _guard_paths(payload.get("paths") or ())
        event_id = payload.get("event_id")
        if not event_id:
            raise DurableError(
                "event 缺 event_id({0!r})—— 沒有身分就無法在重跑時去重"
                .format(payload.get("title")))
        pending.setdefault(path, []).append((event_id, _canonical(payload)))
    # 先把整批算完(含撞號判定)才動任何一個檔:撞號在第二個檔才發現時,
    # 第一個檔不該已經被寫出去 —— 部分寫入的批次沒人能複驗它做到哪裡。
    plans = []
    for path, entries in sorted(pending.items()):
        text, seen = _existing_events(path)
        fresh = []
        for event_id, line in entries:
            if event_id in seen:
                if seen[event_id] != line:
                    raise DurableError(
                        "{0}:event_id {1} 已經存在但內容不同 —— 這不是重跑,"
                        "是兩件事共用一個身分。靜默跳過會讓後者永遠不存在,"
                        "請人裁決(推導 id 的來源撞號,或推導規則有瑕疵)"
                        .format(path, event_id))
                continue
            seen[event_id] = line
            fresh.append(line)
        if fresh:
            plans.append((path, text + "".join(l + "\n" for l in fresh)))
        # fresh 是空的:整批都已經在檔裡,這一輪是重跑補完,不動檔案。
    written = []
    for path, text in plans:
        _atomic_write(path, text)
        written.append(path)
    return sorted(written)


def iter_events(repo_root_path):
    base = _path(repo_root_path, EVENT_DIR)
    if not os.path.isdir(base):
        return
    for dirpath, _dirnames, filenames in sorted(os.walk(base)):
        for name in sorted(filenames):
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(dirpath, name)
            text = _read_text(path)
            for lineno, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    yield json.loads(line)
                except ValueError as exc:
                    raise DurableError(
                        "{0}:{1} 不是合法 JSON:{2}".format(path, lineno, exc))


# ─────────────────────────── rebuild ────────────────────────────────────────
def ensure_layout(repo_root_path, kinds=()):
    """lazy-create:只建**這次真的要寫**的目錄,不為了形式鋪一堆空目錄(§6)。"""
    created = []
    for parts in kinds:
        target = _path(repo_root_path, parts)
        if not os.path.isdir(target):
            os.makedirs(target, exist_ok=True)
            created.append(target)
    return created


def inventory(repo_root_path):
    """durable memory 盤點(dev-setup 回報用;不碰 local DB)。"""
    counts = {"facts": 0, "knowledge": 0, "decisions": 0, "skills": 0,
              "events": 0, "entities": 0}
    for state in iter_states(repo_root_path):
        counts["entities"] += 1
        counts["facts"] += len(state.get("facts") or [])
    counts["knowledge"] = sum(1 for _ in iter_knowledge(repo_root_path))
    counts["decisions"] = sum(1 for _ in iter_decisions(repo_root_path))
    counts["skills"] = sum(1 for _ in iter_skills(repo_root_path))
    counts["events"] = sum(1 for _ in iter_events(repo_root_path))
    return counts
