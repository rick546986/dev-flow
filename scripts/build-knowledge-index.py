#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Knowledge topic index generator (#155 Pilot-2).

正本(機器可讀):docs/knowledge/index.yaml
人讀投影:docs/knowledge/index.md —— **只**由本腳本從 yaml 同輪產出,禁手維。

掃:
  - docs/adr/NNNN-*.md  (YAML frontmatter 優先;無則相容舊 `- Status:` 自由文字)
  - docs/specs/<domain>.md  (living spec 指標)
  - .dev-flow/knowledge/**/*.yaml  (domain/glossary + invariant/intent keys,只收 key)
  - .dev-flow/decisions/DEC-*.md  (decision keys,只收 key)

不做:Full ask 路由、語意衝突裁決(衝突進 queue,永不自動挑 winner)、LLM 聚類、手寫第二份真相。

用法:
  python3 scripts/build-knowledge-index.py [--root DIR] [--write|--check]
  # adopting repos / setup: prefer scripts/bootstrap-knowledge-index.py
  #   (--apply also writes docs/knowledge/conflicts-queue.yaml)
  --write  寫出 index.yaml + index.md(預設)
  --check  重生到記憶體,與現檔逐位元組比;差一點就 exit 1

exit:0 = 寫出／對得上 / 1 = 過期或缺檔 / 2 = 用法或環境
"""
from __future__ import print_function

import argparse
import os
import re
import sys

# --- paths -----------------------------------------------------------------

SCHEMA_VERSION = 1
INDEX_YAML_REL = os.path.join("docs", "knowledge", "index.yaml")
INDEX_MD_REL = os.path.join("docs", "knowledge", "index.md")

ADR_NAME_RE = re.compile(r"^(\d{4})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
STATUS_LINE_RE = re.compile(
    r"^-\s*Status:\s*(.+?)(?:\s*#.*)?$", re.IGNORECASE | re.MULTILINE
)
FM_FENCE_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DEC_FENCE_RE = re.compile(
    r"```dev-flow-decision\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE
)
KEY_LINE_RE = re.compile(r"^key:\s*[\"']?([^\"'\n#]+?)[\"']?\s*(?:#.*)?$", re.M)
STOP_TOKENS = frozenset(
    {
        "the",
        "and",
        "for",
        "into",
        "with",
        "from",
        "two",
        "layer",
        "split",
        "must",
        "not",
        "is",
        "vs",
        "by",
        "of",
        "to",
        "a",
        "an",
        "or",
        "in",
        "on",
        "at",
        "be",
        "as",
    }
)

ACTIVE_STATUSES = frozenset({"accepted"})
KNOWN_STATUSES = frozenset(
    {"proposed", "accepted", "deprecated", "superseded"}
)


def die(msg, code=2):
    sys.stderr.write("⛔ build-knowledge-index: %s\n" % msg)
    raise SystemExit(code)


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_text(path, text):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# --- minimal YAML subset (no PyYAML dep; 3.9-safe) -------------------------

def parse_simple_yaml_mapping(text):
    """Parse a flat-ish YAML mapping used in ADR frontmatter / knowledge heads.

    Supports: scalars, null, inline [a, b], and one-level `- item` / `- key: val`
    lists. Not a general YAML parser.
    """
    lines = text.splitlines()
    data = {}
    i = 0
    n = len(lines)

    def parse_scalar(raw):
        s = raw.strip()
        if s in ("null", "~", ""):
            return None
        if (s.startswith('"') and s.endswith('"')) or (
            s.startswith("'") and s.endswith("'")
        ):
            return s[1:-1]
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if not inner:
                return []
            return [parse_scalar(p) for p in inner.split(",")]
        return s

    while i < n:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith(" ") or line.startswith("\t"):
            # orphan indent — skip (unsupported nesting outside list handler)
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2)
        if rest.strip() == "" or rest.strip().startswith("#"):
            # block list or empty
            items = []
            i += 1
            while i < n:
                nxt = lines[i]
                if not nxt.strip() or nxt.lstrip().startswith("#"):
                    i += 1
                    continue
                if not (nxt.startswith("  ") or nxt.startswith("\t")):
                    break
                lm = re.match(r"^\s*-\s+(.*)$", nxt)
                if not lm:
                    break
                item_raw = lm.group(1).strip()
                # mapping item: `- id: "0001"`
                km = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", item_raw)
                if km and not item_raw.startswith("["):
                    obj = {km.group(1): parse_scalar(km.group(2))}
                    i += 1
                    while i < n:
                        deeper = lines[i]
                        if not re.match(r"^\s{4,}[A-Za-z0-9_]+:", deeper):
                            break
                        dm = re.match(r"^\s+([A-Za-z0-9_]+):\s*(.*)$", deeper)
                        if not dm:
                            break
                        obj[dm.group(1)] = parse_scalar(dm.group(2))
                        i += 1
                    items.append(obj)
                else:
                    items.append(parse_scalar(item_raw))
                    i += 1
            data[key] = items
            continue
        data[key] = parse_scalar(rest)
        i += 1
    return data


def yaml_escape_scalar(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    s = str(value)
    if s == "":
        return '""'
    # Quote digit-only / leading-zero ids so YAML does not coerce (e.g. 0003).
    if re.fullmatch(r"[0-9]+", s) or re.search(r'[:#\[\]{}",\n]', s) or s.strip() != s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def yaml_escape_key(key):
    """Topic / mapping keys: quote when not a plain ASCII identifier (#190).

    Unquoted keys with spaces or CJK make yamlmini (and many subset parsers)
    reject the whole index.yaml — ask then degrades to unreadable.
    """
    s = str(key)
    if not s:
        return '""'
    if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_./@+-]*", s) and s.lower() not in (
        "true",
        "false",
        "null",
        "yes",
        "no",
        "on",
        "off",
        "~",
    ):
        return s
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def emit_yaml(doc):
    """Emit index.yaml with stable key order."""
    out = []
    out.append("# GENERATED by scripts/build-knowledge-index.py — do not hand-edit.")
    out.append("# Human view: docs/knowledge/index.md (same generator). Schema: docs/knowledge/README.md")
    out.append("schema_version: %d" % doc["schema_version"])
    out.append("generated_from:")
    for src in doc["generated_from"]:
        out.append("  - %s" % yaml_escape_scalar(src))
    out.append("notes:")
    for note in doc.get("notes") or []:
        out.append("  - %s" % yaml_escape_scalar(note))
    out.append("topics:")
    topics = doc["topics"]
    if not topics:
        out.append("  {}")
    else:
        for topic in sorted(topics.keys()):
            row = topics[topic]
            out.append("  %s:" % yaml_escape_key(topic))
            out.append("    glossary: %s" % emit_inline_list(row.get("glossary") or []))
            out.append(
                "    active_adr: %s" % emit_inline_list(row.get("active_adr") or [])
            )
            out.append(
                "    active_spec: %s" % emit_inline_list(row.get("active_spec") or [])
            )
            durable = row.get("durable") or {}
            out.append("    durable:")
            out.append(
                "      decisions: %s"
                % emit_inline_list(durable.get("decisions") or [])
            )
            out.append(
                "      knowledge: %s"
                % emit_inline_list(durable.get("knowledge") or [])
            )
            supersedes = row.get("supersedes") or []
            if not supersedes:
                out.append("    supersedes: []")
            else:
                out.append("    supersedes:")
                for edge in supersedes:
                    out.append("      - from: %s" % yaml_escape_scalar(edge["from"]))
                    out.append("        to: %s" % yaml_escape_scalar(edge["to"]))
                    out.append("        mode: %s" % yaml_escape_scalar(edge["mode"]))
                    out.append(
                        "        scopes: %s"
                        % emit_inline_list(edge.get("scopes") or [])
                    )
            conflicts = row.get("conflicts") or []
            out.append("    conflicts: %s" % emit_inline_list(conflicts))
    unscoped = doc.get("unscoped") or {}
    out.append("unscoped:")
    out.append(
        "  decisions: %s" % emit_inline_list(unscoped.get("decisions") or [])
    )
    out.append(
        "  knowledge: %s" % emit_inline_list(unscoped.get("knowledge") or [])
    )
    out.append("")
    return "\n".join(out)


def emit_inline_list(items):
    if not items:
        return "[]"
    return "[" + ", ".join(yaml_escape_scalar(x) for x in items) + "]"


def emit_markdown(doc):
    lines = []
    lines.append("<!-- GENERATED by scripts/build-knowledge-index.py — do not hand-edit. -->")
    lines.append("")
    lines.append("# Knowledge index")
    lines.append("")
    lines.append(
        "Machine truth: [`index.yaml`](./index.yaml). "
        "This page is a projection only — regenerate with "
        "`python3 scripts/build-knowledge-index.py --write`."
    )
    lines.append("")
    lines.append("Schema: [`README.md`](./README.md).")
    lines.append("")
    if doc.get("notes"):
        lines.append("## Notes")
        lines.append("")
        for note in doc["notes"]:
            lines.append("- %s" % note)
        lines.append("")
    lines.append("## Topics")
    lines.append("")
    topics = doc["topics"]
    if not topics:
        lines.append("_No topics yet._")
        lines.append("")
    else:
        for topic in sorted(topics.keys()):
            row = topics[topic]
            lines.append("### `%s`" % topic)
            lines.append("")
            lines.append("| Field | Pointers |")
            lines.append("|---|---|")
            lines.append(
                "| active_adr | %s |"
                % (md_list(row.get("active_adr")) or "—")
            )
            lines.append(
                "| active_spec | %s |"
                % (md_list(row.get("active_spec")) or "—")
            )
            lines.append(
                "| glossary | %s |" % (md_list(row.get("glossary")) or "—")
            )
            durable = row.get("durable") or {}
            lines.append(
                "| durable.decisions | %s |"
                % (md_list(durable.get("decisions")) or "—")
            )
            lines.append(
                "| durable.knowledge | %s |"
                % (md_list(durable.get("knowledge")) or "—")
            )
            lines.append(
                "| conflicts | %s |"
                % (md_list(row.get("conflicts")) or "—")
            )
            lines.append("")
            supersedes = row.get("supersedes") or []
            if supersedes:
                lines.append("Supersedes:")
                lines.append("")
                for edge in supersedes:
                    scopes = edge.get("scopes") or []
                    extra = (
                        " scopes=%s" % ",".join(scopes) if scopes else ""
                    )
                    lines.append(
                        "- `%s` → `%s` (%s)%s"
                        % (edge["from"], edge["to"], edge["mode"], extra)
                    )
                lines.append("")
    unscoped = doc.get("unscoped") or {}
    lines.append("## Unscoped durable pointers")
    lines.append("")
    lines.append(
        "Keys that did not token-match any topic (await human topic tags / Pilot-1)."
    )
    lines.append("")
    lines.append(
        "- decisions: %s"
        % (md_list(unscoped.get("decisions")) or "—")
    )
    lines.append(
        "- knowledge: %s"
        % (md_list(unscoped.get("knowledge")) or "—")
    )
    lines.append("")
    lines.append("## Sample lookup")
    lines.append("")
    sample = None
    for topic, row in sorted(doc["topics"].items()):
        if row.get("active_adr"):
            sample = (topic, row["active_adr"])
            break
    if sample:
        lines.append(
            "Topic `%s` → active_adr %s (open `index.yaml`, search that topic key)."
            % (sample[0], ", ".join("`%s`" % a for a in sample[1]))
        )
    else:
        lines.append("No topic with `active_adr` yet.")
    lines.append("")
    return "\n".join(lines)


def md_list(items):
    if not items:
        return ""
    return ", ".join("`%s`" % x for x in items)


# --- scanners --------------------------------------------------------------

def normalize_status(raw):
    if raw is None:
        return None
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if raw is None:
        return None
    s = str(raw).strip().lower()
    # drop trailing comments ("accepted  # note")
    s = s.split("#", 1)[0].strip()
    if s in KNOWN_STATUSES:
        return s
    # legacy free text with trailing words: "superseded by 0003", "accepted "
    # — require word boundary so "accepted-ish" stays bad (queue, not auto-fix).
    m = re.match(
        r"^(proposed|accepted|deprecated|superseded)(?:\s+|$)", s
    )
    if m:
        return m.group(1)
    return s


def as_id_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, dict):
                # supersedes_partial entry — id field
                if "id" in item:
                    out.append(str(item["id"]).strip().strip('"'))
            else:
                out.append(str(item).strip().strip('"'))
        return [x for x in out if x]
    return [str(value).strip().strip('"')]


def parse_adr(path):
    name = os.path.basename(path)
    m = ADR_NAME_RE.match(name)
    if not m:
        return None
    adr_id, slug = m.group(1), m.group(2)
    text = read_text(path)
    meta = {
        "id": adr_id,
        "slug": slug,
        "path": None,
        "status": None,
        "topics": [],
        "supersedes": [],
        "superseded_by": None,
        "supersedes_partial": [],
        "source_form": "legacy",
    }
    fm = FM_FENCE_RE.match(text)
    if fm:
        data = parse_simple_yaml_mapping(fm.group(1))
        meta["source_form"] = "yaml-frontmatter"
        if "id" in data and data["id"] is not None:
            meta["id"] = str(data["id"]).strip().strip('"')
        if "slug" in data and data["slug"]:
            meta["slug"] = str(data["slug"]).strip().strip('"')
        meta["status"] = normalize_status(data.get("status"))
        topics = data.get("topics") or []
        if isinstance(topics, str):
            topics = [topics]
        meta["topics"] = [str(t).strip() for t in topics if str(t).strip()]
        meta["supersedes"] = as_id_list(data.get("supersedes"))
        sb = data.get("superseded_by")
        meta["superseded_by"] = (
            None if sb in (None, "null") else str(sb).strip().strip('"')
        )
        partial = data.get("supersedes_partial") or []
        if isinstance(partial, list):
            meta["supersedes_partial"] = partial
    else:
        sm = STATUS_LINE_RE.search(text)
        if sm:
            meta["status"] = normalize_status(sm.group(1))
        # legacy "superseded by NNNN"
        if sm:
            m2 = re.search(
                r"superseded\s+by\s+(\d{4})", sm.group(1), re.I
            )
            if m2:
                meta["superseded_by"] = m2.group(1)
                meta["status"] = "superseded"
    if not meta["topics"]:
        meta["topics"] = [slug]
    return meta


def scan_adrs(root):
    adr_dir = os.path.join(root, "docs", "adr")
    if not os.path.isdir(adr_dir):
        return [], False
    rows = []
    for name in sorted(os.listdir(adr_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(adr_dir, name)
        if not os.path.isfile(path):
            continue
        row = parse_adr(path)
        if row:
            row["path"] = os.path.join("docs", "adr", name).replace("\\", "/")
            rows.append(row)
    return rows, True


def scan_specs(root):
    spec_dir = os.path.join(root, "docs", "specs")
    if not os.path.isdir(spec_dir):
        return []
    out = []
    for name in sorted(os.listdir(spec_dir)):
        if not name.endswith(".md"):
            continue
        domain = name[:-3]
        out.append(
            {
                "domain": domain,
                "path": os.path.join("docs", "specs", name).replace("\\", "/"),
            }
        )
    return out


def scan_knowledge_keys(root):
    base = os.path.join(root, ".dev-flow", "knowledge")
    if not os.path.isdir(base):
        return [], []
    glossary = []
    knowledge = []
    for dirpath, _dirnames, filenames in os.walk(base):
        for name in sorted(filenames):
            if not name.endswith((".yaml", ".yml")):
                continue
            path = os.path.join(dirpath, name)
            text = read_text(path)
            km = KEY_LINE_RE.search(text)
            if not km:
                continue
            key = km.group(1).strip()
            rel = os.path.relpath(path, root).replace("\\", "/")
            kind_m = re.search(r"^kind:\s*(\S+)", text, re.M)
            kind = kind_m.group(1) if kind_m else ""
            rel_parts = rel.split("/")
            if "domain" in rel_parts or kind in ("domain", "glossary", "term"):
                glossary.append({"key": key, "path": rel})
            else:
                knowledge.append({"key": key, "path": rel, "kind": kind})
    return glossary, knowledge


def scan_decisions(root):
    base = os.path.join(root, ".dev-flow", "decisions")
    if not os.path.isdir(base):
        return []
    out = []
    for name in sorted(os.listdir(base)):
        if not (name.startswith("DEC-") and name.endswith(".md")):
            continue
        path = os.path.join(base, name)
        text = read_text(path)
        key = None
        fm = DEC_FENCE_RE.search(text)
        if fm:
            data = parse_simple_yaml_mapping(fm.group(1))
            if data.get("key"):
                key = str(data["key"]).strip().strip('"')
        if not key:
            # filename DEC-<key>.<hash>.md
            body = name[4:-3]  # strip DEC- and .md
            key = body.rsplit(".", 1)[0]
        out.append(
            {
                "key": key,
                "path": os.path.join(".dev-flow", "decisions", name).replace(
                    "\\", "/"
                ),
            }
        )
    return out


def tokens(s):
    parts = re.split(r"[^a-z0-9]+", s.lower())
    return {p for p in parts if len(p) >= 4 and p not in STOP_TOKENS}


def topic_match(topic, key):
    tt = tokens(topic)
    kt = tokens(key)
    if not tt or not kt:
        return False
    return bool(tt & kt)


def empty_topic():
    return {
        "glossary": [],
        "active_adr": [],
        "active_spec": [],
        "durable": {"decisions": [], "knowledge": []},
        "supersedes": [],
        "conflicts": [],
    }


def build_index(root):
    notes = []
    adrs, adr_dir_ok = scan_adrs(root)
    specs = scan_specs(root)
    glossary, knowledge = scan_knowledge_keys(root)
    decisions = scan_decisions(root)

    yaml_count = sum(1 for a in adrs if a["source_form"] == "yaml-frontmatter")
    legacy_count = sum(1 for a in adrs if a["source_form"] == "legacy")
    if adr_dir_ok and legacy_count and yaml_count == 0:
        notes.append(
            "This project's ADRs still use legacy `- Status:` lines "
            "(no YAML frontmatter); generator falls back to filename slug as "
            "topic. Prefer Pilot-1 frontmatter when touching ADRs. See "
            "docs/knowledge/README.md."
        )
    elif legacy_count:
        notes.append(
            "Mixed ADR metadata: %d yaml-frontmatter, %d legacy Status lines."
            % (yaml_count, legacy_count)
        )

    generated_from = [
        "docs/adr/*.md",
        "docs/specs/*.md",
        ".dev-flow/knowledge/**",
        ".dev-flow/decisions/**",
    ]

    topics = {}

    def ensure(topic):
        if topic not in topics:
            topics[topic] = empty_topic()
        return topics[topic]

    # ADRs
    by_id = {}
    for adr in adrs:
        by_id[adr["id"]] = adr
        for topic in adr["topics"]:
            row = ensure(topic)
            if adr["status"] in ACTIVE_STATUSES:
                if adr["id"] not in row["active_adr"]:
                    row["active_adr"].append(adr["id"])
            elif adr["status"] == "proposed":
                # proposed never enters active_*; optional visibility via conflicts note
                pass
            # supersede edges (full) when this ADR supersedes others
            for old in adr.get("supersedes") or []:
                edge = {
                    "from": old,
                    "to": adr["id"],
                    "mode": "full",
                    "scopes": [],
                }
                if edge not in row["supersedes"]:
                    row["supersedes"].append(edge)
            for part in adr.get("supersedes_partial") or []:
                if not isinstance(part, dict):
                    continue
                old = str(part.get("id") or "").strip()
                scopes = part.get("scopes") or []
                if isinstance(scopes, str):
                    scopes = [scopes]
                if not old:
                    continue
                edge = {
                    "from": old,
                    "to": adr["id"],
                    "mode": "partial",
                    "scopes": [str(s) for s in scopes],
                }
                if edge not in row["supersedes"]:
                    row["supersedes"].append(edge)

    # Multi-active → conflicts only; clear active_adr (never auto-pick a winner).
    # Gate teeth live in check-adr-integrity; this index must not invent authority.
    for topic, row in topics.items():
        if len(row["active_adr"]) > 1:
            candidates = list(row["active_adr"])
            row["conflicts"].append(
                "multi-active-adr:" + ",".join(candidates)
            )
            row["active_adr"] = []

    # Bad status / unparseable / dangling supersede → topic conflicts (+ bootstrap queue)
    known_ids = set(by_id.keys())
    for adr in adrs:
        st = adr.get("status")
        topics_for = adr.get("topics") or [adr["slug"]]
        if st is None:
            tag = "unparseable-status:%s" % adr["id"]
            for topic in topics_for:
                row = ensure(topic)
                if tag not in row["conflicts"]:
                    row["conflicts"].append(tag)
        elif st not in KNOWN_STATUSES:
            tag = "bad-status:%s:%s" % (adr["id"], st)
            for topic in topics_for:
                row = ensure(topic)
                if tag not in row["conflicts"]:
                    row["conflicts"].append(tag)
        dangling = []
        for old in adr.get("supersedes") or []:
            if old not in known_ids:
                dangling.append(old)
        sb = adr.get("superseded_by")
        if sb and sb not in known_ids:
            dangling.append(sb)
        for part in adr.get("supersedes_partial") or []:
            if isinstance(part, dict):
                old = str(part.get("id") or "").strip()
                if old and old not in known_ids:
                    dangling.append(old)
        if dangling:
            tag = "dangling-supersede:%s:%s" % (
                adr["id"],
                ",".join(sorted(set(dangling))),
            )
            for topic in topics_for:
                row = ensure(topic)
                if tag not in row["conflicts"]:
                    row["conflicts"].append(tag)

    # Living specs
    for spec in specs:
        row = ensure(spec["domain"])
        if spec["path"] not in row["active_spec"]:
            row["active_spec"].append(spec["path"])

    # Attach durable pointers by token overlap; leftovers → unscoped
    topic_keys = list(topics.keys())
    unscoped_decisions = []
    unscoped_knowledge = []

    for g in glossary:
        matched = [t for t in topic_keys if topic_match(t, g["key"])]
        if not matched:
            # domain glossary with no topic yet → create topic = key
            row = ensure(g["key"])
            if g["key"] not in row["glossary"]:
                row["glossary"].append(g["key"])
            topic_keys = list(topics.keys())
            continue
        for t in matched:
            row = topics[t]
            if g["key"] not in row["glossary"]:
                row["glossary"].append(g["key"])

    for d in decisions:
        matched = [t for t in topic_keys if topic_match(t, d["key"])]
        if not matched:
            unscoped_decisions.append(d["key"])
            continue
        for t in matched:
            row = topics[t]
            if d["key"] not in row["durable"]["decisions"]:
                row["durable"]["decisions"].append(d["key"])

    for k in knowledge:
        matched = [t for t in topic_keys if topic_match(t, k["key"])]
        if not matched:
            unscoped_knowledge.append(k["key"])
            continue
        for t in matched:
            row = topics[t]
            if k["key"] not in row["durable"]["knowledge"]:
                row["durable"]["knowledge"].append(k["key"])

    # Stable sort lists
    for row in topics.values():
        row["glossary"] = sorted(row["glossary"])
        row["active_adr"] = sorted(row["active_adr"])
        row["active_spec"] = sorted(row["active_spec"])
        row["durable"]["decisions"] = sorted(row["durable"]["decisions"])
        row["durable"]["knowledge"] = sorted(row["durable"]["knowledge"])
        row["conflicts"] = sorted(row["conflicts"])
        row["supersedes"] = sorted(
            row["supersedes"], key=lambda e: (e["from"], e["to"], e["mode"])
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_from": generated_from,
        "notes": notes,
        "topics": topics,
        "unscoped": {
            "decisions": sorted(unscoped_decisions),
            "knowledge": sorted(unscoped_knowledge),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=None, help="repo root (default: parent of scripts/)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write index files (default)")
    mode.add_argument("--check", action="store_true", help="compare regenerated to committed")
    args = ap.parse_args(argv)

    self_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(args.root or os.path.join(self_dir, ".."))
    if not os.path.isdir(root):
        die("root not a directory: %s" % root)

    # make relative paths stable
    os.chdir(root)

    doc = build_index(root)
    yaml_text = emit_yaml(doc)
    md_text = emit_markdown(doc)

    yaml_path = os.path.join(root, INDEX_YAML_REL)
    md_path = os.path.join(root, INDEX_MD_REL)

    do_check = args.check
    do_write = args.write or not args.check

    if do_check:
        problems = []
        for path, expected, label in (
            (yaml_path, yaml_text, INDEX_YAML_REL),
            (md_path, md_text, INDEX_MD_REL),
        ):
            if not os.path.isfile(path):
                problems.append("missing %s" % label)
                continue
            actual = read_text(path)
            if actual != expected:
                problems.append("stale %s (run: python3 scripts/build-knowledge-index.py --write)" % label)
        if problems:
            print("=== knowledge index check: FAIL ===")
            for p in problems:
                print("  ✗ %s" % p)
            return 1
        print("=== knowledge index check: OK ===")
        print("  ✓ %s" % INDEX_YAML_REL)
        print("  ✓ %s" % INDEX_MD_REL)
        print("  topics=%d" % len(doc["topics"]))
        return 0

    if do_write:
        write_text(yaml_path, yaml_text)
        write_text(md_path, md_text)
        print("wrote %s" % INDEX_YAML_REL)
        print("wrote %s" % INDEX_MD_REL)
        print("topics=%d adrs_active=%s" % (
            len(doc["topics"]),
            sorted(
                {
                    a
                    for row in doc["topics"].values()
                    for a in row.get("active_adr") or []
                }
            ),
        ))
        for note in doc.get("notes") or []:
            print("note: %s" % note)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
