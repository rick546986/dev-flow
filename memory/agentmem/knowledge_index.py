"""Short knowledge index routing for `dev-memory.py ask` (#155 knife-2).

正本:`docs/knowledge/index.yaml`(Pilot-2 產生)。ask 在 CURRENT 或 topic-like
問句時**先**查這份短索引:topic → active_adr / active_spec / durable 指標 →
只回那些 path,禁止預載全部 `docs/adr/` 或全量 specs。

缺檔／不可讀 → 優雅降級(回 missing_index / unreadable,呼叫端繼續走既有
FTS/embedding 路徑),不炸 CLI。

無第三方依賴:產生器寫的 flow list(`active_adr: ["0003"]`)先展開成 block,
再交給 yamlmini。
"""
import glob
import os
import re

from . import cues, durable, yamlmini

INDEX_REL = os.path.join("docs", "knowledge", "index.yaml")

HIT = "hit"
UNKNOWN_TOPIC = "unknown_topic"
MISSING_INDEX = "missing_index"
UNREADABLE = "unreadable"
SKIPPED = "skipped"

_FLOW_LIST_LINE = re.compile(
    r"^(\s*)([A-Za-z0-9_.-]+):\s*\[(.*)\]\s*(?:#.*)?$"
)


def index_abspath(repo_root):
    return os.path.join(repo_root, INDEX_REL)


def should_consult(plan_dict, query=None):
    """CURRENT 意圖,或問句看起來像在點名一個 topic(稍後再對表)。"""
    if not plan_dict:
        return True
    if plan_dict.get("primary") == "CURRENT":
        return True
    text = query if query is not None else plan_dict.get("query") or ""
    content = cues.strip_frame(text).strip()
    if not content:
        return False
    compact = re.sub(r"\s+", "-", content.lower())
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+){0,8}", compact):
        return True
    words = [w for w in re.split(r"[^a-z0-9]+", content.lower()) if w]
    return 1 <= len(words) <= 6


def load(repo_root):
    """讀索引。回傳 (status, data_or_None, abs_path_or_None)。"""
    path = index_abspath(repo_root)
    if not os.path.isfile(path):
        return MISSING_INDEX, None, path
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError:
        return UNREADABLE, None, path
    try:
        data = yamlmini.load(_expand_flow_lists(raw))
    except (yamlmini.YamlMiniError, ValueError, TypeError):
        return UNREADABLE, None, path
    if not isinstance(data, dict):
        return UNREADABLE, None, path
    topics = data.get("topics")
    if topics is None:
        data["topics"] = {}
    elif not isinstance(topics, dict):
        return UNREADABLE, None, path
    return "ok", data, path


def match_topics(query, topics):
    """回傳問句命中的 topic key 列表(穩定排序)。"""
    if not topics or not query:
        return []
    haystack = _normalize_for_match(cues.strip_frame(query) or query)
    raw_hay = _normalize_for_match(query)
    hits = []
    for topic in topics:
        needle = _normalize_for_match(topic)
        if not needle:
            continue
        if _topic_in_haystack(needle, haystack) or _topic_in_haystack(
                needle, raw_hay):
            hits.append(topic)
    return sorted(hits)


def resolve_topic_paths(repo_root, topic, entry):
    """只解析本 topic 指標指向的檔;不掃全部 ADR。"""
    if not isinstance(entry, dict):
        return []
    out = []
    for adr_id in entry.get("active_adr") or []:
        path = _resolve_adr(repo_root, str(adr_id))
        if path:
            out.append({
                "kind": "active_adr",
                "ref": str(adr_id),
                "path": path,
                "topic": topic,
            })
    for spec in entry.get("active_spec") or []:
        rel = str(spec).replace("\\", "/")
        if not rel.startswith("docs/"):
            rel = os.path.join("docs", "specs", rel).replace("\\", "/")
            if not rel.endswith(".md"):
                rel = rel + ".md"
        if os.path.isfile(os.path.join(repo_root, rel)):
            out.append({
                "kind": "active_spec",
                "ref": str(spec),
                "path": rel,
                "topic": topic,
            })
    for key in entry.get("glossary") or []:
        path = _resolve_knowledge(repo_root, str(key), prefer_domain=True)
        if path:
            out.append({
                "kind": "glossary",
                "ref": str(key),
                "path": path,
                "topic": topic,
            })
    durable_row = entry.get("durable") or {}
    if not isinstance(durable_row, dict):
        durable_row = {}
    for key in durable_row.get("decisions") or []:
        path = _resolve_decision(repo_root, str(key))
        if path:
            out.append({
                "kind": "durable_decision",
                "ref": str(key),
                "path": path,
                "topic": topic,
            })
    for key in durable_row.get("knowledge") or []:
        path = _resolve_knowledge(repo_root, str(key), prefer_domain=False)
        if path:
            out.append({
                "kind": "durable_knowledge",
                "ref": str(key),
                "path": path,
                "topic": topic,
            })
    return out


def route(repo_root, query, plan_dict=None):
    """ask 用的短索引路由。永不拋例外到 CLI。"""
    plan_dict = plan_dict or {"query": query, "primary": None}
    if not should_consult(plan_dict, query=query):
        return _payload(SKIPPED, note="not CURRENT / not topic-like")

    status, data, _abs_path = load(repo_root)
    rel_index = INDEX_REL.replace("\\", "/")
    if status == MISSING_INDEX:
        return _payload(
            MISSING_INDEX,
            index_path=rel_index,
            note="docs/knowledge/index.yaml missing — degraded to store retrieval",
        )
    if status == UNREADABLE:
        return _payload(
            UNREADABLE,
            index_path=rel_index,
            note="docs/knowledge/index.yaml unreadable — degraded to store retrieval",
        )

    topics = data.get("topics") or {}
    matched = match_topics(query, topics)
    if not matched:
        return _payload(
            UNKNOWN_TOPIC,
            index_path=rel_index,
            note="no topic key matched query",
        )

    paths = []
    conflicts = []
    for topic in matched:
        entry = topics.get(topic) or {}
        paths.extend(resolve_topic_paths(repo_root, topic, entry))
        for item in (entry.get("conflicts") or []) if isinstance(entry, dict) else []:
            conflicts.append("{0}:{1}".format(topic, item))

    note = None
    if conflicts:
        note = "index conflicts (queue only, not auto-resolved): " + ", ".join(
            conflicts)
    if not paths:
        note = (note + "; " if note else "") + (
            "topic matched but no resolvable pointer files")

    return _payload(
        HIT,
        index_path=rel_index,
        matched_topics=matched,
        paths=paths,
        note=note,
    )


def path_results(route_payload):
    """把 route paths 轉成 ask envelope 的 results 列(不讀檔內容)。"""
    rows = []
    for item in route_payload.get("paths") or []:
        rows.append({
            "item_type": "knowledge_index",
            "kind": item["kind"],
            "ref": item["ref"],
            "path": item["path"],
            "topic": item.get("topic"),
            "title": "{0}:{1} → {2}".format(
                item["kind"], item["ref"], item["path"]),
        })
    return rows


def _payload(status, index_path=None, matched_topics=None, paths=None,
             note=None):
    return {
        "status": status,
        "index_path": index_path,
        "matched_topics": list(matched_topics or []),
        "paths": list(paths or []),
        "note": note,
    }


def _expand_flow_lists(text):
    """把 `key: [a, b]` / `key: []` 展開成 yamlmini 吃得下的 block。"""
    out = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            out.append(line)
            continue
        m = _FLOW_LIST_LINE.match(line)
        if not m:
            out.append(line)
            continue
        indent, key, inner = m.group(1), m.group(2), m.group(3).strip()
        if not inner:
            out.append("{0}{1}: null".format(indent, key))
            continue
        out.append("{0}{1}:".format(indent, key))
        for item in _split_flow_items(inner):
            out.append("{0}  - {1}".format(indent, item))
    return "\n".join(out) + "\n"


def _split_flow_items(inner):
    items, buf, in_q, qch = [], [], False, ""
    for ch in inner:
        if in_q:
            buf.append(ch)
            if ch == qch:
                in_q = False
            continue
        if ch in ('"', "'"):
            in_q = True
            qch = ch
            buf.append(ch)
            continue
        if ch == ",":
            items.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail or items:
        items.append(tail)
    return [i for i in items if i]


def _normalize_for_match(text):
    text = (text or "").casefold()
    text = text.replace("_", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _topic_in_haystack(topic, haystack):
    if not topic or not haystack:
        return False
    if topic == haystack:
        return True
    spaced = topic.replace("-", " ")
    compact = topic.replace("-", "")
    for cand in (topic, spaced, compact):
        if not cand:
            continue
        if cand == haystack:
            return True
        pattern = r"(?<![a-z0-9])" + re.escape(cand) + r"(?![a-z0-9])"
        if re.search(pattern, haystack):
            return True
    return False


def _repo_rel(repo_root, abspath):
    return os.path.relpath(abspath, repo_root).replace("\\", "/")


def _resolve_adr(repo_root, adr_id):
    adr_id = (adr_id or "").strip()
    if not adr_id:
        return None
    pattern = os.path.join(repo_root, "docs", "adr", "{0}-*.md".format(adr_id))
    matches = sorted(glob.glob(pattern))
    if len(matches) != 1:
        return None
    return _repo_rel(repo_root, matches[0])


def _resolve_decision(repo_root, key):
    try:
        path = durable.decision_file(repo_root, key)
    except durable.DurableError:
        return None
    if os.path.isfile(path):
        return _repo_rel(repo_root, path)
    directory = os.path.join(durable.root(repo_root), "decisions")
    if not os.path.isdir(directory):
        return None
    prefix = "DEC-" + key
    hits = sorted(
        n for n in os.listdir(directory)
        if n.startswith(prefix) and n.endswith(".md")
    )
    if not hits:
        return None
    return _repo_rel(repo_root, os.path.join(directory, hits[0]))


def _resolve_knowledge(repo_root, key, prefer_domain=False):
    kinds = list(durable.KNOWLEDGE_DIRS)
    if prefer_domain:
        kinds = ["domain"] + [k for k in kinds if k != "domain"]
    for kind in kinds:
        try:
            path = durable.knowledge_file(repo_root, kind, key)
        except durable.DurableError:
            continue
        if os.path.isfile(path):
            return _repo_rel(repo_root, path)
    base = os.path.join(durable.root(repo_root), "knowledge")
    if not os.path.isdir(base):
        return None
    key_line = re.compile(
        r"^key:\s*[\"']?{0}[\"']?\s*(?:#.*)?$".format(re.escape(key)), re.M)
    for dirpath, _dirs, files in os.walk(base):
        for name in sorted(files):
            if not name.endswith((".yaml", ".yml")):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                continue
            if key_line.search(text):
                return _repo_rel(repo_root, path)
    return None
