#!/bin/bash
# test-devstage6-graph.sh — check-devstage6-graph.sh 的負向牙
#
# 對照組是一份最小合法 graph(四真節點 + 一個 skill-legacy-T 暫留 hop)。
# 每個案例把對照組改壞一次,確認檢查真的紅。
# 另有一份「舊實作(單一 SKILL、沒有 graph)」fixture,必須紅 ——
# 這就是「先寫測試、舊實作先紅」的永久牙齒,不是散文。
# 第一刀:必須有 N1-arm;只有它可 allow write_notes;沒武裝一律 deny;
# FORK_INTEGRATION_SHA 缺或被改寫必須紅;有 via 必須紅;
# kind: skill-legacy 本刀合法(第二刀才改成必須紅)。
# 本刀不測 prebash、不測 guide #stage6 鏈 —— 那是後兩刀。
#
# 用法:scripts/test-devstage6-graph.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-devstage6-graph.sh"
FIX="$SELF_DIR/fixtures/devstage6-graph"
[ -x "$CHECK" ] || chmod +x "$CHECK"
[ -f "$CHECK" ] || { echo "FATAL: 找不到 $CHECK" >&2; exit 2; }
[ -d "$FIX/good" ] || { echo "FATAL: 找不到 $FIX/good" >&2; exit 2; }
[ -d "$FIX/old-skill" ] || { echo "FATAL: 找不到 $FIX/old-skill" >&2; exit 2; }
[ -d "$FIX/actions" ] || { echo "FATAL: 找不到 $FIX/actions" >&2; exit 2; }

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

NODES = ("skills", "dev-flow", "stage6", "nodes")


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


def patch(path, old, new):
    text = open(path, encoding="utf-8").read()
    if old not in text:
        print(f"FATAL: 治具找不到待改字串 {old!r} in {path}", file=sys.stderr)
        sys.exit(2)
    open(path, "w", encoding="utf-8").write(text.replace(old, new, 1))


def graph_of(case):
    return os.path.join(case, "skills", "dev-flow", "stage6", "graph.yaml")


def node_of(case, name):
    return os.path.join(case, *NODES, name)


with tempfile.TemporaryDirectory(prefix="devstage6-graph-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(四真節點 + 一暫留 hop)必須綠", good, 0)

    old = os.path.join(tmpbase, "old")
    shutil.copytree(os.path.join(fix, "old-skill"), old)
    expect(
        "G-old 舊實作(單一 SKILL、沒有 graph)必須紅",
        old,
        1,
        "沒有 graph",
    )

    case = os.path.join(tmpbase, "missing-entry-heading")
    seed(case)
    patch(node_of(case, "N1-arm.md"), "## 進條件", "## 入口備註")
    expect("P0 真節點缺進條件必須紅", case, 1, "進條件")

    case = os.path.join(tmpbase, "missing-done-heading")
    seed(case)
    patch(node_of(case, "N1-arm.md"), "## 完成條件", "## 收尾備註")
    expect("P0 真節點缺完成條件必須紅", case, 1, "完成條件")

    case = os.path.join(tmpbase, "second-md")
    seed(case)
    slug = os.path.join(case, "docs", "dev", "fixture-slug")
    open(os.path.join(slug, "6-implementation-notes-rerun.md"), "w", encoding="utf-8").write("x\n")
    expect(
        "P0 同 slug 第二份 6-implementation-notes*.md 必須紅",
        case,
        1,
        "6-implementation-notes*.md",
    )

    case = os.path.join(tmpbase, "save-as")
    seed(case)
    patch(graph_of(case), "write_mode: overwrite", "write_mode: save_as")
    expect("P0 write_mode≠overwrite 必須紅", case, 1, "overwrite")

    case = os.path.join(tmpbase, "no-write-node")
    seed(case)
    patch(graph_of(case), "  N1-arm:\n", "  N1-later:\n")
    expect(
        "P0 缺 N1-arm 必須紅(第一刀不能只做 handoff)",
        case,
        1,
        "第一刀必須有寫檔節點",
    )

    case = os.path.join(tmpbase, "via-hop")
    seed(case)
    patch(
        graph_of(case),
        "  skill-legacy-T:\n    kind: skill-legacy\n",
        "  skill-legacy-T:\n    via: README.md\n    kind: skill-legacy\n",
    )
    expect("P0 有 via 當 hop 必須紅", case, 1, "via")

    case = os.path.join(tmpbase, "legacy-not-real-node")
    seed(case)
    patch(graph_of(case), "  skill-legacy-T:\n    kind: skill-legacy\n", "  skill-legacy-T:\n")
    expect(
        "P0 暫留步不是 kind: skill-legacy 真節點必須紅",
        case,
        1,
        "skill-legacy",
    )

    case = os.path.join(tmpbase, "bad-entry")
    seed(case)
    patch(graph_of(case), "entry: N1-arm", "entry: N2-handoff")
    expect("P0 entry 不是 N1-arm 必須紅", case, 1, "entry")

    case = os.path.join(tmpbase, "broken-chain")
    seed(case)
    patch(graph_of(case), "    next: skill-legacy-T\n", "    next: N4-selfcheck\n")
    expect("P0 鏈跳過 skill-legacy-T 必須紅", case, 1, "skill-legacy-T")

    case = os.path.join(tmpbase, "no-cursor-call")
    seed(case)
    patch(node_of(case, "N2-handoff.md"), "--write-cursor", "--no-cursor-call")
    expect("P0 真節點缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "n2-allow-notes")
    seed(case)
    patch(
        graph_of(case),
        "  N2-handoff:\n    file: nodes/N2-handoff.md\n    next: skill-legacy-T\n",
        "  N2-handoff:\n    file: nodes/N2-handoff.md\n    next: skill-legacy-T\n"
        "    allow:\n      - write_notes\n",
    )
    expect("P0 N1-arm 之外 allow write_notes 必須紅", case, 1, "N2-handoff")

    case = os.path.join(tmpbase, "n1-no-allow-notes")
    seed(case)
    patch(graph_of(case), "    allow:\n      - write_notes\n", "")
    expect("P0 N1-arm 缺 allow write_notes 必須紅", case, 1, "N1-arm")

    case = os.path.join(tmpbase, "sha-missing")
    seed(case)
    patch(
        os.path.join(case, "docs", "dev", "fixture-slug", "6-implementation-notes.md"),
        "FORK_INTEGRATION_SHA: 0123456789abcdef0123456789abcdef01234567\n",
        "",
    )
    expect("P0 FORK_INTEGRATION_SHA 缺必須紅", case, 1, "FORK_INTEGRATION_SHA")

    case = os.path.join(tmpbase, "sha-rewritten")
    seed(case)
    patch(
        os.path.join(case, "docs", "dev", "fixture-slug", "6-implementation-notes.md"),
        "FORK_INTEGRATION_SHA: 0123456789abcdef0123456789abcdef01234567\n",
        "FORK_INTEGRATION_SHA: 0123456789abcdef0123456789abcdef01234567\n"
        "FORK_INTEGRATION_SHA: abcdef0123456789abcdef0123456789abcdef01\n",
    )
    expect("P0 FORK_INTEGRATION_SHA 被改寫必須紅", case, 1, "被改寫")

    case = os.path.join(tmpbase, "tasks-not-approved")
    seed(case)
    patch(
        os.path.join(case, "docs", "dev", "fixture-slug", "5-tasks.md"),
        "status: approved",
        "status: draft",
    )
    expect(
        "P0 已有 6-notes 卻 5-tasks 不是 approved,N1 當入口必須紅",
        case,
        1,
        "退回第 5 站",
    )

    actions = os.path.join(fix, "actions")

    expect(
        "P0 N2-handoff 做 write_notes 必須紅(沒武裝)",
        good,
        1,
        "N2-handoff",
        extra=["--action", os.path.join(actions, "n2-write-notes.json")],
    )
    expect(
        "P0 N4-selfcheck 做 write_notes 必須紅(沒武裝)",
        good,
        1,
        "N4-selfcheck",
        extra=["--action", os.path.join(actions, "n4-write-notes.json")],
    )
    expect(
        "P0 N5-end 做 write_notes 必須紅(沒武裝)",
        good,
        1,
        "N5-end",
        extra=["--action", os.path.join(actions, "n5-write-notes.json")],
    )
    expect(
        "P0 skill-legacy-T 做 write_notes 必須紅(沒武裝)",
        good,
        1,
        "skill-legacy-T",
        extra=["--action", os.path.join(actions, "legacy-write-notes.json")],
    )
    expect(
        "G-action N1-arm + 5-tasks approved → write_notes 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n1-write-notes-ok.json")],
    )
    expect(
        "P0 5-tasks 不是 approved 卻 write_notes 必須紅",
        good,
        1,
        "approved",
        extra=["--action", os.path.join(actions, "n1-write-notes-pending.json")],
    )
    expect(
        "P0 graph 沒這節點 → exit 2(不是靜默放行)",
        good,
        2,
        "沒有節點",
        extra=["--action", os.path.join(actions, "unknown-node.json")],
    )
    expect(
        "P0 舊實作跑 --action → exit 2(缺 graph 不得偽裝成 allow)",
        old,
        2,
        "沒有 graph",
        extra=["--action", os.path.join(actions, "n1-write-notes-ok.json")],
    )

    wrote = os.path.join(tmpbase, "cursor")
    os.makedirs(wrote)
    proc = subprocess.run(
        ["bash", check, "--write-cursor", "N1-arm", "fixture-slug", wrote],
        capture_output=True,
        text=True,
    )
    cursor_path = os.path.join(wrote, ".devstage6-cursor.json")
    ok = proc.returncode == 0 and os.path.isfile(cursor_path)
    if ok:
        data = json.loads(open(cursor_path, encoding="utf-8").read())
        ok = data.get("node") == "N1-arm" and data.get("slug") == "fixture-slug"
    if ok:
        passed += 1
        print("  ✓ G-cursor --write-cursor N1-arm 寫出 .devstage6-cursor.json")
    else:
        failed += 1
        print("  ✗ G-cursor --write-cursor 沒寫出游標檔", file=sys.stderr)
        print((proc.stdout or "") + (proc.stderr or ""), file=sys.stderr)

total = passed + failed
print(f"=== test-devstage6-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < 8:
    print(f"⛔ 案例數 {total} < 8,牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
