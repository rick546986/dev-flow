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
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("FATAL: PyYAML required (import yaml)", file=sys.stderr)
    raise SystemExit(2)


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


def load_index(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
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
