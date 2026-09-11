#!/bin/bash
# check-preload-ban.sh — #155 knife-2 item 3: preload ban mechanical tooth.
#
# Why: Pilot-3 left 「禁預載全部 docs/adr/」as policy text + a manual call-path
# proof. Agents can still regress the one-liner away, or the index→ADR contract
# can break, and every other check stays green.
#
# Portable limit (not a bug in this tooth):
#   True PreToolUse-style block of bulk Read(docs/adr/**) is **not** available on
#   Cursor / Grok thin shells (host-stack-fit Known limit ①: no Write/Read hooks).
#   Inventing fake Cursor hooks is forbidden. Claude PreToolUse could in theory
#   count multi-file ADR reads, but that would be Claude-only and easy to bypass
#   via Bash — not the portable fail-closed bar. Strongest portable tooth =
#   script + CI (this file).
#
# What this guard fails closed on:
#   ① Ask-first one-liner still present in skills/dev-{flow,talk,run}/SKILL.md
#      and guides/guide-dev-flow.html #memory (markdown + HTML forms).
#   ② Known *positive* preload anti-patterns absent from live skills/ + scripts/
#      (the ban line itself contains 「禁預載…」and is allowlisted).
#   ③ proof-knowledge-index-call-path.py exits 0 on production index AND fixture
#      (topic → active_adr → docs/adr/NNNN-*.md exists).
#
# Usage:
#   scripts/check-preload-ban.sh [root]
# exit:0 = pass / 1 = regression / 2 = environment (fail-closed, do not guess)

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

PROOF="$SELF_DIR/proof-knowledge-index-call-path.py"
if [ ! -f "$PROOF" ]; then
  # When invoked as "$ROOT/scripts/..." from a seed copy, prefer root-local proof.
  if [ -f "$ROOT/scripts/proof-knowledge-index-call-path.py" ]; then
    PROOF="$ROOT/scripts/proof-knowledge-index-call-path.py"
  else
    echo "⛔ 找不到 proof-knowledge-index-call-path.py" >&2
    exit 2
  fi
fi

python3 - "$ROOT" "$PROOF" <<'PY'
import os
import re
import subprocess
import sys

root = sys.argv[1]
proof = sys.argv[2]
problems = []
checks = 0  # incremented by ok()/bad(); MIN_CHECKS floor below

# Canonical ask-first core (punctuation-insensitive after normalize).
# Skills use markdown backticks; guide uses <code>…</code> inside <strong>.
ASK_FIRST_CORE = (
    "專案問答先短索引",
    "dev-memory.py ask",
    "禁預載全部",
    "docs/adr/",
    "再按回傳 path 載單檔",
)

SKILL_TARGETS = [
    "skills/dev-flow/SKILL.md",
    "skills/dev-talk/SKILL.md",
    "skills/dev-run/SKILL.md",
]

GUIDE_REL = "guides/guide-dev-flow.html"

# Positive preload instructions that must never appear as live guidance.
# Do NOT list bare 「預載全部」— the ban line contains 「禁預載全部」.
ANTI_PATTERNS = [
    "preload all docs/adr",
    "preload all ADR",
    "preload every ADR",
    "read all docs/adr",
    "read every ADR",
    "read all ADRs",
    "load all docs/adr",
    "load all ADRs",
    "載入全部 docs/adr",
    "載入全部 ADR",
    "預載所有 docs/adr",
    "預載所有 ADR",
    "先把 docs/adr 全部讀進",
    "先讀完 docs/adr/",
    "cat docs/adr/*",
]


def norm_text(text):
    """Strip markdown/HTML noise so skill + guide forms share one needle set."""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("`", "")
    text = re.sub(r"[*_]+", "", text)
    text = re.sub(r"\s+", "", text)
    return text


def read(rel):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def ok(label):
    global checks
    checks += 1
    print("  ✓ " + label)


def bad(label, detail):
    global checks
    checks += 1
    problems.append("%s: %s" % (label, detail))
    print("  ✗ %s: %s" % (label, detail))


def has_ask_first(text):
    n = norm_text(text)
    return all(norm_text(piece) in n for piece in ASK_FIRST_CORE)


# ── ① Ask-first one-liner pins ─────────────────────────────────────────────
for rel in SKILL_TARGETS:
    body = read(rel)
    if body is None:
        bad(rel, "missing")
        continue
    if has_ask_first(body):
        ok(f"{rel} ask-first one-liner")
    else:
        bad(rel, "missing ask-first one-liner (禁預載全部 docs/adr/)")

guide = read(GUIDE_REL)
if guide is None:
    bad(GUIDE_REL, "missing")
else:
    m = re.search(r'<h2 id="memory">.*?(?=<h2 |\Z)', guide, re.S)
    if not m:
        bad(GUIDE_REL, "missing <h2 id=\"memory\"> section")
    elif has_ask_first(m.group(0)):
        ok(f"{GUIDE_REL} #memory ask-first one-liner")
    else:
        bad(GUIDE_REL + " #memory", "missing ask-first one-liner")

# ── ② Anti-pattern scan (skills/ + scripts/ live surfaces) ─────────────────
SCAN_DIRS = ["skills", "scripts"]
SKIP_DIR_NAMES = {
    "fixtures",
    "__pycache__",
    "node_modules",
    ".git",
}
# This guard documents anti-patterns; allowlist self so listed strings don't self-hit.
SELF_REL = "scripts/check-preload-ban.sh"
ALLOW_PREFIXES = (
    "scripts/fixtures/",
    "scripts/test-",  # mutation/selftest prose may quote banned phrases
)
ALLOW_EXACT = {
    SELF_REL,
    "scripts/fixtures/knowledge-index/README.md",
}


def is_allowlisted(rel):
    if rel in ALLOW_EXACT:
        return True
    for prefix in ALLOW_PREFIXES:
        if rel.startswith(prefix):
            return True
    return False


scan_hits = []
scanned_files = 0
# Sort anti-patterns longest-first so "preload all docs/adr" wins over
# substring "load all docs/adr" on the same span.
ANTI_SORTED = sorted(ANTI_PATTERNS, key=len, reverse=True)
for dname in SCAN_DIRS:
    base = os.path.join(root, dname)
    if not os.path.isdir(base):
        bad("scan/%s" % dname, "directory missing")
        continue
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            if not name.endswith((".md", ".sh", ".py", ".html", ".yml", ".yaml")):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if is_allowlisted(rel):
                continue
            if "/fixtures/" in ("/%s/" % rel):
                continue
            scanned_files += 1
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    for lineno, line in enumerate(fh, 1):
                        # Ban line itself: 「禁預載…」is policy, not an anti-pattern.
                        if "禁預載" in line:
                            continue
                        low = line.lower()
                        # Mask longer hits so shorter substring patterns don't double-count.
                        masked = low
                        for pat in ANTI_SORTED:
                            needle = pat.lower()
                            if needle in masked or (pat in line and needle not in low):
                                # Prefer casefold match on masked text.
                                if needle not in masked:
                                    continue
                                scan_hits.append("%s:%d: %s" % (rel, lineno, pat))
                                masked = masked.replace(needle, " " * len(needle))
            except OSError:
                continue

if scanned_files == 0:
    bad("anti-pattern scan", "0 files scanned — guard did not run")
elif scan_hits:
    for h in scan_hits[:20]:
        print("  ✗ anti-pattern: %s" % h)
    if len(scan_hits) > 20:
        print("  ✗ … +%d more" % (len(scan_hits) - 20))
    bad("anti-pattern scan", "%d hit(s) in skills/scripts" % len(scan_hits))
else:
    ok("anti-pattern scan clean (%d files)" % scanned_files)

# Also fail if a line has 「預載全部」without 「禁預載」(positive instruction drift).
pos_hits = []
for dname in ("skills", "guides"):
    base = os.path.join(root, dname)
    if not os.path.isdir(base):
        continue
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            if not name.endswith((".md", ".html")):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    for lineno, line in enumerate(fh, 1):
                        if "預載全部" in line and "禁預載" not in line:
                            pos_hits.append(f"{rel}:{lineno}")
            except OSError:
                continue

if pos_hits:
    for h in pos_hits[:10]:
        print(f"  ✗ positive-preload wording: {h}")
    bad("positive-preload wording", f"{len(pos_hits)} line(s) with 預載全部 sans 禁")
else:
    ok("no positive 預載全部 (sans 禁) in skills/guides")

# ── ③ Call-path proof (index contract selftest) ────────────────────────────
def run_proof(argv, label):
    cmd = [sys.executable, proof] + list(argv)
    try:
        proc = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except OSError as err:
        bad(label, "cannot run proof: %s" % err)
        return
    if proc.returncode == 0:
        ok(label)
        return
    detail = (proc.stderr or proc.stdout or "").strip().splitlines()
    tail = detail[-3:] if detail else ["exit %s" % proc.returncode]
    bad(label, " | ".join(tail))


# Production index (required after Pilot-2).
prod_index = os.path.join(root, "docs", "knowledge", "index.yaml")
if not os.path.isfile(prod_index):
    bad("docs/knowledge/index.yaml", "missing — proof/index contract regress")
else:
    run_proof(
        ["--index", prod_index, "--root", root, "--topic", "agent-memory"],
        "proof production index (topic agent-memory)",
    )

# Fixture path must keep working (Pilot-3 regression bar).
fixture_index = os.path.join(
    root, "scripts", "fixtures", "knowledge-index", "index.yaml"
)
fixture_root = os.path.join(root, "scripts", "fixtures", "knowledge-index")
if not os.path.isfile(fixture_index):
    bad("fixtures/knowledge-index", "missing fixture index")
else:
    run_proof(
        [
            "--index",
            fixture_index,
            "--root",
            fixture_root,
            "--topic",
            "agent-memory",
        ],
        "proof fixture index (topic agent-memory)",
    )

# Floor: enough checks actually ran (not an empty green).
MIN_CHECKS = 8
if checks < MIN_CHECKS:
    print(
        f"⛔ 檢查數地板:實際只跑了 {checks} 項(地板 {MIN_CHECKS})",
        file=sys.stderr,
    )
    raise SystemExit(1)

print()
if problems:
    print(f"⛔ preload-ban: {len(problems)} failure(s)")
    for p in problems:
        print(f"   - {p}")
    print(
        "   note: Cursor/Grok have no PreToolUse Read block; "
        "this CI tooth is the portable fail-closed bar (#155 knife-2.3)."
    )
    raise SystemExit(1)

print(f"✅ preload-ban: {checks} checks passed")
print(
    "   limit: no portable PreToolUse bulk-Read block on Cursor/Grok "
    "(script+CI only)."
)
raise SystemExit(0)
PY
