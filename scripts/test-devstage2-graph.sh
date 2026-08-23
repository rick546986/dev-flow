#!/bin/bash
# test-devstage2-graph.sh — check-devstage2-graph.sh 的負向牙
#
# 對照組是一份最小合法 graph(四真節點 + 中間 skill-legacy)。
# 每個案例把對照組改壞一次,確認檢查真的紅。
# 另有一份「舊實作(單一 SKILL、沒有 graph)」fixture,必須紅 ——
# 這就是「先寫測試、舊實作先紅」的永久牙齒,不是散文。
#
# 用法:scripts/test-devstage2-graph.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-devstage2-graph.sh"
FIX="$SELF_DIR/fixtures/devstage2-graph"
[ -x "$CHECK" ] || chmod +x "$CHECK"
[ -f "$CHECK" ] || { echo "FATAL: 找不到 $CHECK" >&2; exit 2; }
[ -d "$FIX/good" ] || { echo "FATAL: 找不到 $FIX/good" >&2; exit 2; }
[ -d "$FIX/old-skill" ] || { echo "FATAL: 找不到 $FIX/old-skill" >&2; exit 2; }

python3 - "$ROOT" "$CHECK" "$FIX" <<'PY'
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root, check, fix = sys.argv[1], sys.argv[2], sys.argv[3]
passed = 0
failed = 0


def run_check(tree, extra=None):
    cmd = ["bash", check]
    if extra:
        cmd.extend(extra)
    cmd.append(tree)
    return subprocess.run(cmd, capture_output=True, text=True)


def seed(tmp):
    shutil.copytree(os.path.join(fix, "good"), tmp, dirs_exist_ok=True)


def expect(label, tree, want_rc, needle=None, extra=None):
    global passed, failed
    proc = run_check(tree, extra)
    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    ok = proc.returncode == want_rc
    if ok and needle and needle not in blob:
        ok = False
        blob += f"\n[test] 期望輸出含 {needle!r}"
    if ok:
        passed += 1
        print(f"  ✓ {label}")
    else:
        failed += 1
        print(f"  ✗ {label} (rc={proc.returncode} want={want_rc})", file=sys.stderr)
        print(blob[-800:], file=sys.stderr)


with tempfile.TemporaryDirectory(prefix="devstage2-graph-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(四真節點 + skill-legacy)必須綠", good, 0)

    old = os.path.join(tmpbase, "old")
    shutil.copytree(os.path.join(fix, "old-skill"), old)
    expect(
        "G-old 舊實作(單一 SKILL、沒有 graph)必須紅",
        old,
        1,
        "沒有 graph",
    )

    case = os.path.join(tmpbase, "missing-entry")
    seed(case)
    n1 = os.path.join(case, "skills", "dev-flow", "stage2", "nodes", "N1-handoff.md")
    text = open(n1, encoding="utf-8").read().replace("## 進條件", "## 入口備註")
    open(n1, "w", encoding="utf-8").write(text)
    expect("P0 真節點缺進條件必須紅", case, 1, "進條件")

    case = os.path.join(tmpbase, "missing-done")
    seed(case)
    n1 = os.path.join(case, "skills", "dev-flow", "stage2", "nodes", "N1-handoff.md")
    text = open(n1, encoding="utf-8").read().replace("## 完成條件", "## 收尾備註")
    open(n1, "w", encoding="utf-8").write(text)
    expect("P0 真節點缺完成條件必須紅", case, 1, "完成條件")

    case = os.path.join(tmpbase, "second-md")
    seed(case)
    slug = os.path.join(case, "docs", "dev", "fixture-slug")
    open(os.path.join(slug, "2-decision-rerun.md"), "w", encoding="utf-8").write("x\n")
    expect("P0 同 slug 第二份 2-decision*.md 必須紅", case, 1, "2-decision")

    case = os.path.join(tmpbase, "save-as")
    seed(case)
    graph = os.path.join(case, "skills", "dev-flow", "stage2", "graph.yaml")
    text = open(graph, encoding="utf-8").read().replace(
        "write_mode: overwrite", "write_mode: save_as"
    )
    open(graph, "w", encoding="utf-8").write(text)
    expect("P0 write_mode≠overwrite 必須紅", case, 1, "overwrite")

    actions = os.path.join(fix, "actions")
    unapproved = os.path.join(tmpbase, "unapproved")
    seed(unapproved)
    disc = os.path.join(
        unapproved, "docs", "dev", "fixture-slug", "1-discussion.md"
    )
    text = open(disc, encoding="utf-8").read().replace(
        "status: approved", "status: draft"
    )
    open(disc, "w", encoding="utf-8").write(text)
    expect(
        "P0 N1 在 1-discussion 未 approved 時寫 2-decision 必須紅",
        unapproved,
        1,
        "approved",
        extra=["--action", os.path.join(actions, "n1-write-decision.json")],
    )

    expect(
        "G-action N3 + 已核准 1-discussion → write_decision 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n3-write-decision-ok.json")],
    )

    wrote = os.path.join(tmpbase, "cursor")
    os.makedirs(wrote)
    proc = subprocess.run(
        ["bash", check, "--write-cursor", "N1-handoff", "fixture-slug", wrote],
        capture_output=True,
        text=True,
    )
    cursor_path = os.path.join(wrote, ".devstage2-cursor.json")
    ok = proc.returncode == 0 and os.path.isfile(cursor_path)
    data = {}
    if ok:
        data = json.loads(open(cursor_path, encoding="utf-8").read())
        ok = data.get("node") == "N1-handoff"
    if ok:
        passed += 1
        print("  ✓ G-cursor --write-cursor 寫出 .devstage2-cursor.json")
    else:
        failed += 1
        print("  ✗ G-cursor --write-cursor 沒寫出游標檔", file=sys.stderr)
        print((proc.stdout or "") + (proc.stderr or ""), file=sys.stderr)

total = passed + failed
print(f"=== test-devstage2-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < 9:
    print(f"⛔ 案例數 {total} < 9,牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
