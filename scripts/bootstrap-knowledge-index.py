#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dev-setup knowledge-index bootstrap (#155 knife-2 item 2).

For already-installed (and fresh) product projects + the mother repo:

  1. Scan docs/adr + domain knowledge (+ specs / decisions)
  2. Create/update docs/knowledge/index.yaml and regenerate the human twin
  3. Unresolvable conflicts → docs/knowledge/conflicts-queue.yaml
     (never auto-pick a winner)
  4. CONTEXT.md → warn / candidate-only note; never resurrect as routing truth

Default is dry-run (report only). Pass --apply to write.

用法:
  python3 scripts/bootstrap-knowledge-index.py [--root DIR] [--dry-run|--apply] [--json]
  python3 scripts/bootstrap-knowledge-index.py [--root DIR] --check

exit:0 = dry-run/apply/check OK
     1 = --check found stale index/queue
     2 = usage / environment
"""
from __future__ import print_function

import argparse
import importlib.util
import json
import os
import re
import sys

QUEUE_REL = os.path.join("docs", "knowledge", "conflicts-queue.yaml")
INDEX_YAML_REL = os.path.join("docs", "knowledge", "index.yaml")
INDEX_MD_REL = os.path.join("docs", "knowledge", "index.md")
QUEUE_SCHEMA = 1

ADR_NAME_RE = re.compile(r"^(\d{4})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")


def die(msg, code=2):
    sys.stderr.write("⛔ bootstrap-knowledge-index: %s\n" % msg)
    raise SystemExit(code)


def load_builder():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "build-knowledge-index.py")
    if not os.path.isfile(path):
        die("missing sibling build-knowledge-index.py at %s" % path)
    spec = importlib.util.spec_from_file_location("build_knowledge_index", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_text(path, text):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def yaml_escape_scalar(s):
    s = str(s)
    if s == "":
        return '""'
    if re.search(r'[:#\[\]{},&*?|>!%@`\'"\n]', s) or s.strip() != s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def emit_inline_list(items):
    if not items:
        return "[]"
    return "[" + ", ".join(yaml_escape_scalar(x) for x in items) + "]"


def scan_unparseable_filenames(root):
    """Filenames under docs/adr/ that are .md but fail the NNNN-slug gate."""
    adr_dir = os.path.join(root, "docs", "adr")
    if not os.path.isdir(adr_dir):
        return []
    out = []
    for name in sorted(os.listdir(adr_dir)):
        if not name.endswith(".md"):
            continue
        if name in ("index.md", "README.md"):
            continue
        path = os.path.join(adr_dir, name)
        if not os.path.isfile(path):
            continue
        if ADR_NAME_RE.match(name):
            continue
        out.append(
            {
                "kind": "unparseable",
                "path": os.path.join("docs", "adr", name).replace("\\", "/"),
                "reason": "filename-not-NNNN-kebab-slug",
                "adr_ids": [],
                "topic": None,
                "detail": name,
            }
        )
    return out


# Pre-migrate CTA: CONTEXT still present and domain glossary not landed yet.
CONTEXT_WARN_DETAIL_PRE_MIGRATE = (
    "migrate-legacy dry-run then --apply --promote "
    "(CANDIDATE + documentation only). "
    "Dry-run alone leaves .dev-flow/knowledge/ absent/empty and index "
    "topics glossary: [] — dry-run ≠ complete. "
    "Do not resurrect CONTEXT.md as index/routing truth. "
    "Delete only after owner confirms migrate + no dual cite."
)

# Post-migrate CTA: terms already in domain/; CONTEXT leftover only.
CONTEXT_WARN_DETAIL_POST_MIGRATE = (
    "terms already in .dev-flow/knowledge/domain/ (CANDIDATE); "
    "CONTEXT still present → wait for owner to confirm no dual cite, "
    "then delete CONTEXT; do not treat CONTEXT as routing truth. "
    "Do not re-run migrate as if nothing landed."
)


def domain_glossary_landed(root, doc=None):
    """True when domain yaml exists or index already points at glossary keys.

    Used to fork context-warn copy: empty domain + empty glossary ⇒ still need
    migrate-legacy --apply --promote; otherwise CONTEXT is leftover cleanup only.
    Never auto-deletes CONTEXT.
    """
    domain_dir = os.path.join(root, ".dev-flow", "knowledge", "domain")
    if os.path.isdir(domain_dir):
        for name in os.listdir(domain_dir):
            if name.endswith(".yaml") or name.endswith(".yml"):
                return True
    if doc:
        for row in (doc.get("topics") or {}).values():
            if row.get("glossary"):
                return True
    return False


def context_warn_detail(root, doc=None):
    """Queue detail for CONTEXT.md — pre vs post migrate (#176)."""
    if domain_glossary_landed(root, doc):
        return CONTEXT_WARN_DETAIL_POST_MIGRATE
    return CONTEXT_WARN_DETAIL_PRE_MIGRATE


def collect_queue_items(bki, root, doc, adrs):
    """Build structured human-queue items. Never invent a winner."""
    items = []
    known_ids = {a["id"] for a in adrs}

    # Filename unparseable
    items.extend(scan_unparseable_filenames(root))

    for adr in adrs:
        st = adr.get("status")
        path = adr.get("path") or ""
        topics = adr.get("topics") or [adr.get("slug") or ""]
        topic0 = topics[0] if topics else None

        if st is None:
            items.append(
                {
                    "kind": "unparseable",
                    "path": path,
                    "reason": "missing-status",
                    "adr_ids": [adr["id"]],
                    "topic": topic0,
                    "detail": "no YAML status and no legacy - Status: line",
                }
            )
        elif st not in bki.KNOWN_STATUSES:
            items.append(
                {
                    "kind": "bad-status",
                    "path": path,
                    "reason": "status-not-in-enum",
                    "adr_ids": [adr["id"]],
                    "topic": topic0,
                    "detail": st,
                }
            )

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
            items.append(
                {
                    "kind": "dangling",
                    "path": path,
                    "reason": "supersede-target-missing",
                    "adr_ids": [adr["id"]],
                    "topic": topic0,
                    "detail": ",".join(sorted(set(dangling))),
                }
            )

    # Multi-active from built index conflicts (authoritative after clear)
    for topic, row in sorted((doc.get("topics") or {}).items()):
        for c in row.get("conflicts") or []:
            if not str(c).startswith("multi-active-adr:"):
                continue
            ids = str(c).split(":", 1)[1].split(",")
            paths = []
            for a in adrs:
                if a["id"] in ids:
                    paths.append(a.get("path") or "")
            items.append(
                {
                    "kind": "multi-active",
                    "path": ";".join(p for p in paths if p),
                    "reason": "multiple-accepted-same-topic",
                    "adr_ids": ids,
                    "topic": topic,
                    "detail": "do-not-auto-pick; human must choose winner or supersede",
                }
            )

    # CONTEXT.md — warn/candidate only; never treat as routing truth;
    # never auto-delete. Detail forks on whether domain glossary already landed.
    context_path = None
    for candidate in ("CONTEXT.md", os.path.join("docs", "dev", "CONTEXT.md")):
        full = os.path.join(root, candidate)
        if os.path.isfile(full):
            context_path = candidate.replace("\\", "/")
            break
    context = {
        "path": context_path,
        "status": "absent" if context_path is None else "warn-candidate-only",
    }
    if context_path:
        items.append(
            {
                "kind": "context-warn",
                "path": context_path,
                "reason": "legacy-context-present",
                "adr_ids": [],
                "topic": None,
                "detail": context_warn_detail(root, doc),
            }
        )

    # Stable order
    kind_order = {
        "bad-status": 0,
        "dangling": 1,
        "multi-active": 2,
        "unparseable": 3,
        "context-warn": 4,
    }
    items.sort(
        key=lambda it: (
            kind_order.get(it["kind"], 9),
            it.get("topic") or "",
            it.get("path") or "",
            it.get("detail") or "",
        )
    )
    return items, context


def emit_queue_yaml(items, context, notes):
    out = []
    out.append(
        "# GENERATED by scripts/bootstrap-knowledge-index.py — resolve by hand."
    )
    out.append(
        "# Never auto-pick a winner. Schema: docs/knowledge/README.md"
    )
    out.append("schema_version: %d" % QUEUE_SCHEMA)
    out.append("context:")
    out.append(
        "  path: %s"
        % (
            "null"
            if not context.get("path")
            else yaml_escape_scalar(context["path"])
        )
    )
    out.append("  status: %s" % yaml_escape_scalar(context.get("status") or "absent"))
    if notes:
        out.append("notes:")
        for n in notes:
            out.append("  - %s" % yaml_escape_scalar(n))
    else:
        out.append("notes: []")
    if not items:
        out.append("items: []")
    else:
        out.append("items:")
        for it in items:
            out.append("  - kind: %s" % yaml_escape_scalar(it["kind"]))
            out.append("    path: %s" % yaml_escape_scalar(it.get("path") or ""))
            out.append("    reason: %s" % yaml_escape_scalar(it.get("reason") or ""))
            out.append(
                "    adr_ids: %s" % emit_inline_list(it.get("adr_ids") or [])
            )
            topic = it.get("topic")
            out.append(
                "    topic: %s"
                % ("null" if topic in (None, "") else yaml_escape_scalar(topic))
            )
            out.append("    detail: %s" % yaml_escape_scalar(it.get("detail") or ""))
    out.append("")
    return "\n".join(out)


def build_payload(bki, root):
    doc = bki.build_index(root)
    adrs, _ = bki.scan_adrs(root)
    items, context = collect_queue_items(bki, root, doc, adrs)
    notes = list(doc.get("notes") or [])
    if context.get("status") == "warn-candidate-only":
        if domain_glossary_landed(root, doc):
            notes.append(
                "CONTEXT.md still present after migrate — leftover only; "
                "terms already in .dev-flow/knowledge/domain/ (CANDIDATE); "
                "not index truth (see conflicts-queue.yaml). "
                "Owner confirms no dual cite before delete; never auto-delete."
            )
        else:
            notes.append(
                "CONTEXT.md present — candidate/warn only; not index truth "
                "(see conflicts-queue.yaml). "
                "Index topics stay glossary: [] until migrate-legacy "
                "--apply --promote; dry-run ≠ complete."
            )
        doc["notes"] = notes
    yaml_text = bki.emit_yaml(doc)
    md_text = bki.emit_markdown(doc)
    queue_text = emit_queue_yaml(items, context, notes=[])
    return {
        "doc": doc,
        "items": items,
        "context": context,
        "yaml_text": yaml_text,
        "md_text": md_text,
        "queue_text": queue_text,
    }


def summarize(payload):
    by_kind = {}
    for it in payload["items"]:
        by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1
    return {
        "topics": len(payload["doc"].get("topics") or {}),
        "queue_items": len(payload["items"]),
        "by_kind": by_kind,
        "context": payload["context"],
        "index_yaml": INDEX_YAML_REL,
        "index_md": INDEX_MD_REL,
        "queue": QUEUE_REL,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=None, help="repo/project root")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="report only (default)",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="write index.yaml + index.md + conflicts-queue.yaml",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="verify committed index + queue match a fresh bootstrap",
    )
    ap.add_argument("--json", action="store_true", help="machine-readable summary")
    args = ap.parse_args(argv)

    self_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(args.root or os.path.join(self_dir, ".."))
    if not os.path.isdir(root):
        die("root not a directory: %s" % root)

    os.chdir(root)
    bki = load_builder()
    payload = build_payload(bki, root)
    summary = summarize(payload)

    do_check = args.check
    do_apply = args.apply
    do_dry = args.dry_run or (not args.apply and not args.check)

    if do_check:
        problems = []
        for path, expected, label in (
            (os.path.join(root, INDEX_YAML_REL), payload["yaml_text"], INDEX_YAML_REL),
            (os.path.join(root, INDEX_MD_REL), payload["md_text"], INDEX_MD_REL),
            (os.path.join(root, QUEUE_REL), payload["queue_text"], QUEUE_REL),
        ):
            if not os.path.isfile(path):
                problems.append("missing %s" % label)
                continue
            if read_text(path) != expected:
                problems.append(
                    "stale %s (run: python3 scripts/bootstrap-knowledge-index.py "
                    "--apply)" % label
                )
        if problems:
            print("=== knowledge bootstrap check: FAIL ===")
            for p in problems:
                print("  ✗ %s" % p)
            return 1
        print("=== knowledge bootstrap check: OK ===")
        print("  ✓ %s" % INDEX_YAML_REL)
        print("  ✓ %s" % INDEX_MD_REL)
        print("  ✓ %s" % QUEUE_REL)
        print(
            "  topics=%d queue_items=%d context=%s"
            % (
                summary["topics"],
                summary["queue_items"],
                summary["context"].get("status"),
            )
        )
        return 0

    if do_apply:
        write_text(os.path.join(root, INDEX_YAML_REL), payload["yaml_text"])
        write_text(os.path.join(root, INDEX_MD_REL), payload["md_text"])
        write_text(os.path.join(root, QUEUE_REL), payload["queue_text"])
        if args.json:
            print(json.dumps({"action": "apply", **summary}, ensure_ascii=False, indent=2))
        else:
            print("wrote %s" % INDEX_YAML_REL)
            print("wrote %s" % INDEX_MD_REL)
            print("wrote %s" % QUEUE_REL)
            print(
                "topics=%d queue_items=%d context=%s"
                % (
                    summary["topics"],
                    summary["queue_items"],
                    summary["context"].get("status"),
                )
            )
            if summary["by_kind"]:
                print("queue_by_kind=%s" % summary["by_kind"])
            for it in payload["items"]:
                print(
                    "  queue: %s topic=%s adr=%s detail=%s"
                    % (
                        it["kind"],
                        it.get("topic"),
                        ",".join(it.get("adr_ids") or []),
                        it.get("detail"),
                    )
                )
        return 0

    # dry-run
    if args.json:
        out = {"action": "dry-run", **summary, "items": payload["items"]}
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("=== knowledge bootstrap dry-run ===")
        print("root=%s" % root)
        print(
            "would write: %s, %s, %s"
            % (INDEX_YAML_REL, INDEX_MD_REL, QUEUE_REL)
        )
        print(
            "topics=%d queue_items=%d context=%s"
            % (
                summary["topics"],
                summary["queue_items"],
                summary["context"].get("status"),
            )
        )
        if summary["by_kind"]:
            print("queue_by_kind=%s" % summary["by_kind"])
        for it in payload["items"]:
            print(
                "  queue: kind=%s topic=%s path=%s detail=%s"
                % (
                    it["kind"],
                    it.get("topic"),
                    it.get("path"),
                    it.get("detail"),
                )
            )
        if not payload["items"]:
            print("  (no conflicts — queue would be empty)")
        print("re-run with --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
