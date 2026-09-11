#!/bin/bash
# test-bootstrap-knowledge-index.sh — #155 knife-2 setup bootstrap teeth
#
# Covers:
#   • dry-run does not write
#   • --apply writes index.yaml + index.md + conflicts-queue.yaml
#   • multi-active / bad-status / dangling / unparseable → queue (no auto-winner)
#   • CONTEXT.md → warn-candidate-only (not resurrected as index truth)
#   • #176 context-warn.detail forks: pre-migrate vs post-migrate
#   • mother-shaped clean tree → empty queue
#
# 用法: scripts/test-bootstrap-knowledge-index.sh [pack]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
PACK=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  PACK=$(cd "$1" && pwd) || exit 2
fi

TOOL="$SELF_DIR/bootstrap-knowledge-index.py"
[ -f "$TOOL" ] || { echo "FATAL: 找不到 $TOOL" >&2; exit 2; }

python3 - "$PACK" "$TOOL" <<'PY'
import os
import re
import shutil
import subprocess
import sys
import tempfile

pack, tool = sys.argv[1], sys.argv[2]
passed = 0
failed = 0
MIN_CASES = 14


def run(root, *args):
    return subprocess.run(
        [sys.executable, tool, "--root", root, *args],
        capture_output=True,
        text=True,
    )


def expect(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("  ✓ " + label)
        return
    failed += 1
    print("  ✗ " + label, file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)


def write(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)


def adr(path, status, topics, supersedes=None, body="# fixture\n"):
    supersedes = supersedes or []
    fm = [
        "---",
        "status: %s" % status,
        "topics:",
    ]
    for t in topics:
        fm.append("  - %s" % t)
    if supersedes:
        fm.append("supersedes: [%s]" % ", ".join('"%s"' % s for s in supersedes))
    else:
        fm.append("supersedes: []")
    fm.append("superseded_by: null")
    fm.append("---")
    fm.append("")
    write(path, "\n".join(fm) + body)


def plant_clean(tmp):
    root = os.path.join(tmp, "clean")
    adr(
        os.path.join(root, "docs", "adr", "0001-payments-sync.md"),
        "accepted",
        ["payments"],
    )
    return root


def plant_conflicts(tmp):
    root = os.path.join(tmp, "dirty")
    adr_dir = os.path.join(root, "docs", "adr")
    # multi-active same topic
    adr(os.path.join(adr_dir, "0001-sync-payments.md"), "accepted", ["payments"])
    adr(os.path.join(adr_dir, "0002-async-payments.md"), "accepted", ["payments"])
    # bad status
    adr(os.path.join(adr_dir, "0003-weird-status.md"), "accepted-ish", ["weird"])
    # dangling supersede
    adr(
        os.path.join(adr_dir, "0004-points-nowhere.md"),
        "accepted",
        ["orphan-link"],
        supersedes=["0099"],
    )
    # unparseable filename
    write(os.path.join(adr_dir, "not-an-adr.md"), "# nope\n")
    # missing status (YAML without status)
    write(
        os.path.join(adr_dir, "0005-no-status.md"),
        "---\ntopics: [nostat]\nsupersedes: []\nsuperseded_by: null\n---\n# x\n",
    )
    # CONTEXT.md warn only — with domain yaml ⇒ post-migrate CTA (#176)
    write(os.path.join(root, "CONTEXT.md"), "# legacy glossary — not truth\n")
    # domain knowledge key (should index, not conflict)
    write(
        os.path.join(root, ".dev-flow", "knowledge", "domain", "payments.yaml"),
        "kind: domain\nkey: payments\nbody: |\n  term\n",
    )
    return root


def plant_pre_migrate(tmp):
    """CONTEXT present, no domain yaml → pre-migrate dry-run CTA."""
    root = os.path.join(tmp, "pre-migrate")
    adr(
        os.path.join(root, "docs", "adr", "0001-solo.md"),
        "accepted",
        ["solo"],
    )
    write(os.path.join(root, "CONTEXT.md"), "# legacy glossary — not truth\n")
    return root


def plant_post_migrate(tmp):
    """CONTEXT present + domain yaml → post-migrate leftover CTA."""
    root = os.path.join(tmp, "post-migrate")
    adr(
        os.path.join(root, "docs", "adr", "0001-solo.md"),
        "accepted",
        ["solo"],
    )
    write(os.path.join(root, "CONTEXT.md"), "# legacy glossary — not truth\n")
    write(
        os.path.join(root, ".dev-flow", "knowledge", "domain", "sample.yaml"),
        "kind: domain\nkey: sample\nstatus: CANDIDATE\nbody: |\n  from CONTEXT\n",
    )
    return root


print("=== test-bootstrap-knowledge-index ===")

with tempfile.TemporaryDirectory(prefix="df-kboot-") as tmp:
    clean = plant_clean(tmp)
    dirty = plant_conflicts(tmp)
    pre = plant_pre_migrate(tmp)
    post = plant_post_migrate(tmp)

    # 1) dry-run writes nothing
    before = set()
    for dirpath, _, files in os.walk(dirty):
        for n in files:
            before.add(os.path.relpath(os.path.join(dirpath, n), dirty))
    r = run(dirty, "--dry-run")
    after = set()
    for dirpath, _, files in os.walk(dirty):
        for n in files:
            after.add(os.path.relpath(os.path.join(dirpath, n), dirty))
    expect(
        "dry-run exit 0",
        r.returncode == 0,
        "rc=%s out=%s err=%s" % (r.returncode, r.stdout, r.stderr),
    )
    expect(
        "dry-run creates no new files",
        before == after,
        "added=%s" % sorted(after - before),
    )
    expect(
        "dry-run mentions queue kinds",
        "multi-active" in r.stdout
        and "bad-status" in r.stdout
        and "dangling" in r.stdout
        and "unparseable" in r.stdout
        and "context-warn" in r.stdout,
        r.stdout,
    )

    # 2) --apply writes three artifacts
    r = run(dirty, "--apply")
    expect("apply exit 0", r.returncode == 0, r.stderr or r.stdout)
    yml = os.path.join(dirty, "docs", "knowledge", "index.yaml")
    md = os.path.join(dirty, "docs", "knowledge", "index.md")
    queue = os.path.join(dirty, "docs", "knowledge", "conflicts-queue.yaml")
    expect("wrote index.yaml", os.path.isfile(yml))
    expect("wrote index.md", os.path.isfile(md))
    expect("wrote conflicts-queue.yaml", os.path.isfile(queue))

    qtext = open(queue, encoding="utf-8").read()
    expect("queue has multi-active", "kind: multi-active" in qtext, qtext)
    expect("queue has bad-status", "kind: bad-status" in qtext, qtext)
    expect("queue has dangling", "kind: dangling" in qtext, qtext)
    expect("queue has unparseable", "kind: unparseable" in qtext, qtext)
    expect("queue has context-warn", "kind: context-warn" in qtext, qtext)
    expect(
        "context status warn-candidate-only",
        "status: warn-candidate-only" in qtext,
        qtext,
    )
    # dirty plant has domain yaml → post-migrate leftover CTA (#176)
    expect(
        "dirty context-warn uses post-migrate detail",
        "terms already in .dev-flow/knowledge/domain/" in qtext
        and "migrate-legacy dry-run then --apply --promote" not in qtext,
        qtext,
    )

    ytext = open(yml, encoding="utf-8").read()
    # multi-active must not leave a single auto-picked active_adr winner
    # payments topic: active_adr cleared; conflict retained
    expect(
        "multi-active clears active_adr (no auto-pick)",
        re.search(
            r"payments:\n(?:.*\n)*?    active_adr: \[\]\n(?:.*\n)*?    conflicts: \[.*multi-active-adr",
            ytext,
        )
        is not None,
        ytext,
    )
    expect(
        "CONTEXT body not copied into index as glossary truth",
        "legacy glossary" not in ytext,
        ytext[:800],
    )
    expect(
        "CONTEXT path only appears as warn note (not topic body)",
        "CONTEXT.md still present after migrate" in ytext
        and "legacy glossary" not in ytext,
        ytext[:1200],
    )

    # 3) --check passes on freshly applied dirty tree
    r = run(dirty, "--check")
    expect("check OK after apply", r.returncode == 0, r.stdout + r.stderr)

    # 4) clean tree → empty queue
    r = run(clean, "--apply")
    expect("clean apply exit 0", r.returncode == 0, r.stderr or r.stdout)
    cq = open(
        os.path.join(clean, "docs", "knowledge", "conflicts-queue.yaml"),
        encoding="utf-8",
    ).read()
    expect("clean queue items empty", "items: []" in cq, cq)
    expect("clean context absent", "status: absent" in cq, cq)
    cy = open(
        os.path.join(clean, "docs", "knowledge", "index.yaml"), encoding="utf-8"
    ).read()
    expect(
        "clean active_adr populated",
        'active_adr: ["0001"]' in cy,
        cy,
    )

    # 5) mutating queue makes --check fail
    qpath = os.path.join(clean, "docs", "knowledge", "conflicts-queue.yaml")
    with open(qpath, "a", encoding="utf-8") as fh:
        fh.write("# tampered\n")
    r = run(clean, "--check")
    expect("check fails on stale queue", r.returncode == 1, r.stdout + r.stderr)

    # 6) #176 pre-migrate: CONTEXT + empty domain → dry-run CTA + empty-glossary loudness
    r = run(pre, "--apply")
    expect("pre-migrate apply exit 0", r.returncode == 0, r.stderr or r.stdout)
    pq = open(
        os.path.join(pre, "docs", "knowledge", "conflicts-queue.yaml"),
        encoding="utf-8",
    ).read()
    expect(
        "pre-migrate context-warn detail CTA",
        "migrate-legacy dry-run then --apply --promote" in pq
        and "dry-run" in pq
        and "glossary: []" in pq
        and "terms already in .dev-flow/knowledge/domain/" not in pq,
        pq,
    )
    py = open(
        os.path.join(pre, "docs", "knowledge", "index.yaml"), encoding="utf-8"
    ).read()
    expect(
        "pre-migrate index note loud empty-glossary",
        "glossary: [] until migrate-legacy" in py
        and "dry-run" in py,
        py[:1500],
    )
    # glossary pointers empty (no domain yaml)
    expect(
        "pre-migrate topic glossary empty",
        re.search(r"solo:\n(?:.*\n)*?    glossary: \[\]\n", py) is not None,
        py,
    )

    # 7) #176 post-migrate: CONTEXT + domain yaml → leftover CTA (no re-migrate)
    r = run(post, "--apply")
    expect("post-migrate apply exit 0", r.returncode == 0, r.stderr or r.stdout)
    oq = open(
        os.path.join(post, "docs", "knowledge", "conflicts-queue.yaml"),
        encoding="utf-8",
    ).read()
    expect(
        "post-migrate context-warn leftover detail",
        "terms already in .dev-flow/knowledge/domain/" in oq
        and "wait for owner to confirm no dual cite" in oq
        and "Do not re-run migrate" in oq
        and "migrate-legacy dry-run then --apply --promote" not in oq,
        oq,
    )
    oy = open(
        os.path.join(post, "docs", "knowledge", "index.yaml"), encoding="utf-8"
    ).read()
    expect(
        "post-migrate index note leftover (not empty-glossary CTA)",
        "CONTEXT.md still present after migrate" in oy
        and "glossary: [] until migrate-legacy" not in oy,
        oy[:1500],
    )
    expect(
        "post-migrate does not auto-delete CONTEXT",
        os.path.isfile(os.path.join(post, "CONTEXT.md")),
    )

print()
print("passed=%d failed=%d (min %d)" % (passed, failed, MIN_CASES))
if passed < MIN_CASES:
    print("FAIL: too few cases ran", file=sys.stderr)
    sys.exit(1)
if failed:
    sys.exit(1)
print("OK")
sys.exit(0)
PY
