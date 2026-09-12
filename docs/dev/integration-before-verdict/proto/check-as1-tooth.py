#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROTOTYPE — not production.

AS-1 filled-file tooth shape for integration-before-verdict.
Intended Stage 6 landing: extend the existing check-stage67 /
7-review shape family (OC-1). This file is the Stage 3 predicate
only. Do not wire into CI. Do not replace production scripts.

Usage:
  python3 docs/dev/integration-before-verdict/proto/check-as1-tooth.py
"""
from __future__ import print_function

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

VOID_RE = re.compile(r"證據不算數|輸出不算數")
SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
FAIL_RE = re.compile(r"本項\s*FAIL|明示\s*FAIL|2c\s*FAIL|Integration:\s*FAIL")
REBIND_RE = re.compile(r"重綁|重跑\s*Final Fresh|Rebound Source SHA")
ALREADY_RE = re.compile(r"ALREADY_SYNCED")
NA_RE = re.compile(r"N_A_NO_INCOMING")
CLAIM_RE = re.compile(r"\[x\].{0,40}整合回歸")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)

LIVE_TEACHERS = (
    "example/contract-expiry-reminder/7-review.md",
    "example/contract-expiry-reminder/4-spec.md",
    "manifests/p4-gauntlet-gates.md",
    "scripts/devflow-integration-regression.sh",
    "docs/dev/tools/devflow-integration-regression.sh",
)
OLD_TEACHER_RE = re.compile(
    r"執行清單 2c 的 Final Fresh|執行清單 2c gauntlet|執行清單 2c 的文檔化命令"
    r"|Exit Checklist.*整合回歸.*計算工具"
)

INTENDED_ORDER = (
    "2c 整合回歸",
    "2d Final Fresh",
    "雙軸 + 現象",
    "Verdict",
    "Exit 只准文件",
)

FIXTURES = (
    ("filled-void-only.md", "RED"),
    ("filled-rebind.md", "GREEN"),
    ("filled-fail.md", "GREEN"),
    ("filled-n-a.md", "N/A"),
    ("filled-draft.md", "N/A"),
)


def parse_frontmatter(text):
    match = FM_RE.match(text or "")
    meta = {}
    if not match:
        return meta
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta


def classify(text):
    """Return N/A | GREEN | RED. See 3-prototype.md Question."""
    meta = parse_frontmatter(text)
    status = (meta.get("status") or "").lower()
    verdict = (meta.get("verdict") or "").split()[0].upper() if meta.get("verdict") else ""
    sending_g3 = status in ("approved", "shipped") or verdict in (
        "PASS",
        "FAIL",
        "REQUEST_CHANGES",
    )
    claimed = bool(CLAIM_RE.search(text))
    has_already = bool(ALREADY_RE.search(text))
    has_na = bool(NA_RE.search(text))
    has_fail = bool(FAIL_RE.search(text))
    has_rebind = bool(REBIND_RE.search(text)) and bool(SHA_RE.search(text))
    has_void = bool(VOID_RE.search(text))

    if not has_already:
        return "N/A"
    if has_na and not has_already:
        return "N/A"
    if status == "draft" and not claimed and not sending_g3 and not has_fail:
        return "N/A"
    if has_fail:
        return "GREEN"
    if has_rebind:
        return "GREEN"
    if has_void and not has_rebind and not has_fail:
        return "RED"
    if claimed or sending_g3:
        return "RED"
    return "N/A"


def scan_live_teachers():
    hits = []
    for rel in LIVE_TEACHERS:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            hits.append((rel, "MISSING"))
            continue
        with open(path, encoding="utf-8") as handle:
            body = handle.read()
        found = []
        for i, line in enumerate(body.splitlines(), 1):
            if OLD_TEACHER_RE.search(line) or (
                rel.endswith("devflow-integration-regression.sh")
                and i <= 5
                and "Exit Checklist" in line
                and "整合回歸" in line
            ):
                found.append("%d:%s" % (i, line.strip()[:80]))
        hits.append((rel, found or "clean"))
    return hits


def main():
    print("PROTOTYPE — not production")
    print("intended Stage 7 order:")
    print("  " + " → ".join(INTENDED_ORDER))
    print()
    print("%-22s %-8s %-8s %s" % ("fixture", "expect", "got", "ok"))
    failed = 0
    for name, expect in FIXTURES:
        path = os.path.join(HERE, name)
        with open(path, encoding="utf-8") as handle:
            got = classify(handle.read())
        ok = got == expect
        if not ok:
            failed += 1
        print("%-22s %-8s %-8s %s" % (name, expect, got, "yes" if ok else "NO"))
    print()
    print("live-teacher scan (read-only; T-now rewrite is Stage 6):")
    for rel, found in scan_live_teachers():
        if found == "clean":
            print("  CLEAN  %s" % rel)
        elif found == "MISSING":
            print("  MISS   %s" % rel)
            failed += 1
        else:
            print("  OLD    %s" % rel)
            for row in found:
                print("         %s" % row)
    print()
    if failed:
        print("tooth-shape demo: FIXTURE MISMATCH (%d)" % failed)
        return 1
    print("tooth-shape demo: fixtures match intended AS-1 predicate")
    print("live teachers still teach old 2c=Fresh / Exit-Checklist header (expected at Stage 3)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
