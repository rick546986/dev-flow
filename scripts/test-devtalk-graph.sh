#!/bin/bash
# test-devtalk-graph.sh — check-devtalk-graph.sh 的負向牙(P0-1 / P0-2 / P0-3)
#
# 對照組是一份最小合法 graph。每個案例把對照組改壞一次,確認檢查真的紅。
# 另有一份「舊實作(單一 SKILL、沒有 graph)」fixture,必須紅 —— 這就是
# 「先寫測試、舊實作先紅」的永久牙齒,不是散文。
#
# 用法:scripts/test-devtalk-graph.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-devtalk-graph.sh"
FIX="$SELF_DIR/fixtures/devtalk-graph"
[ -x "$CHECK" ] || chmod +x "$CHECK"
[ -f "$CHECK" ] || { echo "FATAL: 找不到 $CHECK" >&2; exit 2; }
[ -d "$FIX/good" ] || { echo "FATAL: 找不到 $FIX/good" >&2; exit 2; }
[ -d "$FIX/old-skill" ] || { echo "FATAL: 找不到 $FIX/old-skill" >&2; exit 2; }

python3 - "$ROOT" "$CHECK" "$FIX" <<'PY'
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


with tempfile.TemporaryDirectory(prefix="devtalk-graph-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(合法四節點 graph)必須綠", good, 0)

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
    n3 = os.path.join(case, "skills", "dev-talk", "nodes", "N3-probe.md")
    text = open(n3, encoding="utf-8").read().replace("## 進條件", "## 入口備註")
    open(n3, "w", encoding="utf-8").write(text)
    expect("P0-2 缺進條件必須紅", case, 1, "進條件")

    case = os.path.join(tmpbase, "missing-done")
    seed(case)
    n3 = os.path.join(case, "skills", "dev-talk", "nodes", "N3-probe.md")
    text = open(n3, encoding="utf-8").read().replace("## 完成條件", "## 收尾備註")
    open(n3, "w", encoding="utf-8").write(text)
    expect("P0-2 缺完成條件必須紅", case, 1, "完成條件")

    case = os.path.join(tmpbase, "next-mismatch")
    seed(case)
    graph = os.path.join(case, "skills", "dev-talk", "graph.yaml")
    text = open(graph, encoding="utf-8").read().replace(
        "N3-probe:\n    file: nodes/N3-probe.md\n    next: N9-write-md",
        "N3-probe:\n    file: nodes/N3-probe.md\n    next: N13-end",
    )
    open(graph, "w", encoding="utf-8").write(text)
    expect("P0-2 graph next 與節點下一跳不一致必須紅", case, 1, "下一跳")

    case = os.path.join(tmpbase, "dual-n3")
    seed(case)
    skill = os.path.join(case, "skills", "dev-talk", "SKILL.md")
    open(skill, "a", encoding="utf-8").write(
        "\n每輪三律\n3a. 前提被推翻\n3b. 發現實為多題\n"
    )
    expect("P0-2 SKILL 與 N3 雙正本必須紅", case, 1, "雙正本")

    case = os.path.join(tmpbase, "second-md")
    seed(case)
    slug = os.path.join(case, "docs", "dev", "fixture-slug")
    open(os.path.join(slug, "1-discussion-rerun.md"), "w", encoding="utf-8").write("x\n")
    expect("P0-1 同 slug 第二份 1-discussion*.md 必須紅", case, 1, "1-discussion")

    case = os.path.join(tmpbase, "save-as")
    seed(case)
    graph = os.path.join(case, "skills", "dev-talk", "graph.yaml")
    text = open(graph, encoding="utf-8").read().replace(
        "write_mode: overwrite", "write_mode: save_as"
    )
    open(graph, "w", encoding="utf-8").write(text)
    expect("P0-1 重跑另存(write_mode≠overwrite)必須紅", case, 1, "overwrite")

    actions = os.path.join(fix, "actions")
    expect(
        "P0-3 游標在 N3 且已有 session → talk start 必須紅",
        good,
        1,
        "talk start",
        extra=["--action", os.path.join(actions, "n3-restart.json")],
    )
    expect(
        "P0-3 游標在 N9 → write_code 必須紅",
        good,
        1,
        "write_code",
        extra=["--action", os.path.join(actions, "n9-write-code.json")],
    )
    expect(
        "P0-3 游標在 N9 → talk end 必須紅",
        good,
        1,
        "talk_end",
        extra=["--action", os.path.join(actions, "n9-talk-end.json")],
    )
    expect(
        "P0-3 N13 之前 write_knowledge 必須紅",
        good,
        1,
        "write_knowledge",
        extra=["--action", os.path.join(actions, "n3-write-knowledge.json")],
    )
    expect(
        "P0-3 N1 無 session → talk start 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n1-start-ok.json")],
    )
    expect(
        "P0-3 N13 → talk end 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n13-end-ok.json")],
    )

total = passed + failed
print(f"=== test-devtalk-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < 12:
    print(f"FATAL: 只跑了 {total} 案,治具沒有真的跑完", file=sys.stderr)
    sys.exit(2)
print("✅ PASS:graph 負向牙全過")
sys.exit(0)
PY
