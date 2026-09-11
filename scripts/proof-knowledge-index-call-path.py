#!/usr/bin/env python3
"""Pilot-3 (#155): prove short-index call path.

Resolve topic → active_adr id → docs/adr/NNNN-*.md → file exists.

Index selection (first hit):
  1. --index PATH
  2. <repo>/docs/knowledge/index.yaml   (when P2 lands)
  3. scripts/fixtures/knowledge-index/index.yaml

Content root for ADR lookup:
  --root, else parent of index when using fixture, else repo root.

exit 0 = resolved + file exists
exit 1 = lookup/resolve failure
exit 2 = usage / unreadable index
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

# Zero third-party deps: CI REPO_REFERENCE only pins markdown-it-py for render.
# build-knowledge-index.py already ships without PyYAML; this proof must too
# or architecture/check-preload-ban goes red on runners without yaml installed.


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def pick_index(explicit: str | None) -> tuple[str, str]:
    """Return (index_path, content_root)."""
    root = repo_root()
    if explicit:
        index = os.path.abspath(explicit)
        return index, os.path.dirname(index)

    prod = os.path.join(root, "docs", "knowledge", "index.yaml")
    if os.path.isfile(prod):
        return prod, root

    fixture = os.path.join(
        root, "scripts", "fixtures", "knowledge-index", "index.yaml"
    )
    if os.path.isfile(fixture):
        return fixture, os.path.dirname(fixture)

    print(
        "FATAL: no index — expected docs/knowledge/index.yaml "
        "or scripts/fixtures/knowledge-index/index.yaml",
        file=sys.stderr,
    )
    raise SystemExit(2)


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_scalar(raw: str):
    s = raw.strip()
    if not s or s.startswith("#"):
        return None
    if s in ("null", "~"):
        return None
    if (s.startswith('"') and s.endswith('"')) or (
        s.startswith("'") and s.endswith("'")
    ):
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(p) for p in inner.split(",")]
    return s


def _parse_yaml_subset(text: str) -> dict:
    """Minimal nested YAML mapping/list parser for knowledge index.yaml.

    Enough for schema_version / topics.<key>.active_adr (inline list or
    block list). Not a general YAML implementation — same philosophy as
    build-knowledge-index.parse_simple_yaml_mapping, but nested.
    """
    lines = text.splitlines()
    root: dict = {}
    # stack entries: (indent, container) where container is dict or list
    stack: list[tuple[int, object]] = [(-1, root)]
    i = 0
    n = len(lines)

    while i < n:
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        ind = _indent(raw)
        stripped = raw.strip()

        while len(stack) > 1 and ind <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        # list item
        if stripped.startswith("- "):
            if not isinstance(parent, list):
                print(
                    "FATAL: list item under non-list at line %d: %s" % (i + 1, stripped),
                    file=sys.stderr,
                )
                raise SystemExit(2)
            item_raw = stripped[2:].strip()
            km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", item_raw)
            if km:
                obj: dict = {km.group(1): _parse_scalar(km.group(2))}
                parent.append(obj)
                stack.append((ind, obj))
            else:
                parent.append(_parse_scalar(item_raw))
            i += 1
            continue

        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", stripped)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2)
        if not isinstance(parent, dict):
            print(
                "FATAL: mapping key under non-mapping at line %d: %s"
                % (i + 1, stripped),
                file=sys.stderr,
            )
            raise SystemExit(2)

        if rest.strip() == "" or rest.strip().startswith("#"):
            # Peek next non-empty line to decide list vs mapping child.
            j = i + 1
            child: object = {}
            while j < n and (
                not lines[j].strip() or lines[j].lstrip().startswith("#")
            ):
                j += 1
            if j < n and _indent(lines[j]) > ind:
                nxt = lines[j].strip()
                if nxt.startswith("- "):
                    child = []
            parent[key] = child
            stack.append((ind, child))
            i += 1
            continue

        parent[key] = _parse_scalar(rest)
        i += 1

    return root


def load_index(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = _parse_yaml_subset(fh.read())
    if not isinstance(data, dict):
        print(f"FATAL: index is not a mapping: {path}", file=sys.stderr)
        raise SystemExit(2)
    topics = data.get("topics")
    if not isinstance(topics, dict) or not topics:
        print(f"FATAL: index missing non-empty topics: {path}", file=sys.stderr)
        raise SystemExit(2)
    return data


def resolve_adr(content_root: str, adr_id: str) -> str:
    """Map NNNN id → unique docs/adr/NNNN-*.md under content_root."""
    adr_id = str(adr_id).strip()
    if not adr_id:
        raise ValueError("empty active_adr id")
    pattern = os.path.join(content_root, "docs", "adr", f"{adr_id}-*.md")
    matches = sorted(glob.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"no ADR file for id {adr_id!r} under {pattern}")
    if len(matches) > 1:
        raise RuntimeError(f"ambiguous ADR id {adr_id!r}: {matches}")
    return matches[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prove topic → active ADR path → file exists (#155 Pilot-3)"
    )
    parser.add_argument("--index", default=None, help="path to index.yaml")
    parser.add_argument(
        "--root",
        default=None,
        help="content root for docs/adr lookup (default: derived from index)",
    )
    parser.add_argument(
        "--topic",
        default="agent-memory",
        help="topic key to resolve (default: agent-memory)",
    )
    args = parser.parse_args(argv)

    index_path, derived_root = pick_index(args.index)
    content_root = os.path.abspath(args.root) if args.root else derived_root

    data = load_index(index_path)
    topics = data["topics"]
    if args.topic not in topics:
        print(
            f"FAIL: topic {args.topic!r} not in index "
            f"({index_path}); keys={sorted(topics)}",
            file=sys.stderr,
        )
        return 1

    entry = topics[args.topic]
    if not isinstance(entry, dict):
        print(f"FAIL: topic entry is not a mapping: {args.topic}", file=sys.stderr)
        return 1

    active = entry.get("active_adr") or []
    if not isinstance(active, list) or not active:
        print(
            f"FAIL: topic {args.topic!r} has no active_adr in {index_path}",
            file=sys.stderr,
        )
        return 1

    resolved = []
    for adr_id in active:
        try:
            path = resolve_adr(content_root, adr_id)
        except (OSError, ValueError, RuntimeError) as err:
            print(f"FAIL: {err}", file=sys.stderr)
            return 1
        if not os.path.isfile(path):
            print(f"FAIL: active ADR path missing: {path}", file=sys.stderr)
            return 1
        resolved.append((adr_id, path))

    print("=== knowledge-index call-path proof (#155 Pilot-3) ===")
    print(f"index:  {index_path}")
    print(f"root:   {content_root}")
    print(f"topic:  {args.topic}")
    for adr_id, path in resolved:
        rel = os.path.relpath(path, content_root)
        print(f"active_adr: {adr_id} → {rel}  (exists)")
    print("PASS: topic → active ADR path → file exists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
