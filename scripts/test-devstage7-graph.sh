#!/bin/bash
# test-devstage7-graph.sh — check-devstage7-graph.sh 的負向牙
#
# 對照組是一份最小合法 graph(第二刀:十個真節點,沒有 skill-legacy 團塊)。
# 每個案例把對照組改壞一次,確認檢查真的紅。
# 另有一份「舊實作(單一 SKILL、沒有 graph)」fixture,必須紅 ——
# 這就是「先寫測試、舊實作先紅」的永久牙齒,不是散文。
# 第二刀:乘客步 2／2b／2c／2d／2e 必須是真節點檔;kind: skill-legacy 必須紅;
# 每個真節點「做什麼」必須 --write-cursor <自己的 id>;
# S2-* 與 N4-author 才 allow write_review(同一份 7-review.md,overwrite);
# 不放寬 N0-role／N1-matrix／N3-axes／N5-verdict;write_notes 一律 deny;
# 只有 N4 可 read_notes;有 via 必須紅;
# S2c 必須點名現有 devflow-integration-regression.sh 且在 Final Fresh 之前;
# S2d 必須點名現有 devflow-evidence-gauntlet.sh 且綁 SHA。
# 本刀不測 prebash、不測 guide #stage7 鏈 —— 那是第三刀。
#
# 用法:scripts/test-devstage7-graph.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-devstage7-graph.sh"
FIX="$SELF_DIR/fixtures/devstage7-graph"
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

NODES = ("skills", "dev-flow", "stage7", "nodes")


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
    return os.path.join(case, "skills", "dev-flow", "stage7", "graph.yaml")


def node_of(case, name):
    return os.path.join(case, *NODES, name)


S2_BLOCK = """  S2-run:
    file: nodes/S2-run.md
    next: S2b-phenomena
    write:
      - docs/dev/<slug>/7-review.md
    write_mode: overwrite
    allow:
      - write_review
    forbid:
      - read_notes
      - write_notes
"""


with tempfile.TemporaryDirectory(prefix="devstage7-graph-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(十真節點,無 skill-legacy)必須綠", good, 0)

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
    patch(node_of(case, "N0-role.md"), "## 進條件", "## 入口備註")
    expect("P0 真節點缺進條件必須紅", case, 1, "進條件")

    case = os.path.join(tmpbase, "missing-done-heading")
    seed(case)
    patch(node_of(case, "N4-author.md"), "## 完成條件", "## 收尾備註")
    expect("P0 真節點缺完成條件必須紅", case, 1, "完成條件")

    case = os.path.join(tmpbase, "second-md")
    seed(case)
    slug = os.path.join(case, "docs", "dev", "fixture-slug")
    open(os.path.join(slug, "7-review-rerun.md"), "w", encoding="utf-8").write("x\n")
    expect("P0 同 slug 第二份 7-review*.md 必須紅", case, 1, "7-review-*.md")

    case = os.path.join(tmpbase, "save-as")
    seed(case)
    patch(
        graph_of(case),
        "  N4-author:\n    file: nodes/N4-author.md\n    next: N5-verdict\n"
        "    write:\n      - docs/dev/<slug>/7-review.md\n"
        "    write_mode: overwrite\n",
        "  N4-author:\n    file: nodes/N4-author.md\n    next: N5-verdict\n"
        "    write:\n      - docs/dev/<slug>/7-review.md\n"
        "    write_mode: save_as\n",
    )
    expect("P0 write_mode≠overwrite 必須紅", case, 1, "overwrite")

    case = os.path.join(tmpbase, "no-write-node")
    seed(case)
    patch(graph_of(case), "  N4-author:\n", "  N4-later:\n")
    expect(
        "P0 缺 N4-author 必須紅(不能只做 handoff)",
        case,
        1,
        "N4-author",
    )

    case = os.path.join(tmpbase, "via-hop")
    seed(case)
    patch(
        graph_of(case),
        "  S2-run:\n    file: nodes/S2-run.md\n",
        "  S2-run:\n    via: _templates/7-review.md\n    file: nodes/S2-run.md\n",
    )
    expect("P0 有 via 當 hop 必須紅", case, 1, "via")

    case = os.path.join(tmpbase, "legacy-kind")
    seed(case)
    patch(
        graph_of(case),
        "  S2-run:\n    file: nodes/S2-run.md\n",
        "  S2-run:\n    kind: skill-legacy\n    file: nodes/S2-run.md\n",
    )
    expect("P0 節點仍掛 kind: skill-legacy 必須紅", case, 1, "skill-legacy")

    case = os.path.join(tmpbase, "legacy-blob")
    seed(case)
    patch(graph_of(case), "    next: S2-run\n", "    next: skill-legacy-2\n")
    patch(
        graph_of(case),
        S2_BLOCK,
        "  skill-legacy-2:\n"
        "    kind: skill-legacy\n"
        "    entry: _templates/7-review.md\n"
        "    steps: \"2\"\n"
        "    next: S2c-integration\n"
        "    forbid:\n"
        "      - write_review\n",
    )
    expect("P0 把 2／2b 收回 skill-legacy 團塊必須紅", case, 1, "skill-legacy")

    case = os.path.join(tmpbase, "bad-entry")
    seed(case)
    patch(graph_of(case), "entry: N0-role", "entry: N4-author")
    expect("P0 entry 不是 N0-role 必須紅", case, 1, "entry")

    case = os.path.join(tmpbase, "skip-s2c")
    seed(case)
    patch(graph_of(case), "    next: S2c-integration\n", "    next: S2d-fresh\n")
    expect("P0 鏈跳過 S2c-integration 必須紅", case, 1, "S2c-integration")

    case = os.path.join(tmpbase, "fresh-before-integration")
    seed(case)
    patch(
        graph_of(case),
        "  S2b-phenomena:\n    file: nodes/S2b-phenomena.md\n"
        "    next: S2c-integration\n",
        "  S2b-phenomena:\n    file: nodes/S2b-phenomena.md\n"
        "    next: S2d-fresh\n",
    )
    patch(
        graph_of(case),
        "  S2d-fresh:\n    file: nodes/S2d-fresh.md\n"
        "    next: S2e-walkthrough\n",
        "  S2d-fresh:\n    file: nodes/S2d-fresh.md\n"
        "    next: S2c-integration\n",
    )
    expect(
        "P0 鏈把 S2d-fresh 放在 S2c-integration 之前必須紅",
        case,
        1,
        "S2c-integration",
    )

    case = os.path.join(tmpbase, "no-cursor-n1")
    seed(case)
    patch(node_of(case, "N1-matrix.md"), "--write-cursor", "--no-cursor-call")
    expect("P0 真節點缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "no-cursor-s2")
    seed(case)
    patch(node_of(case, "S2-run.md"), "--write-cursor", "--no-cursor-call")
    expect("P0 S2-run 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "no-cursor-s2c")
    seed(case)
    patch(node_of(case, "S2c-integration.md"), "--write-cursor", "--no-cursor-call")
    expect("P0 S2c 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "no-cursor-s2e")
    seed(case)
    patch(node_of(case, "S2e-walkthrough.md"), "--write-cursor", "--no-cursor-call")
    expect("P0 S2e 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "missing-s2c-file")
    seed(case)
    os.remove(node_of(case, "S2c-integration.md"))
    expect("P0 缺 S2c-integration 節點檔必須紅", case, 1, "S2c-integration")

    case = os.path.join(tmpbase, "s2c-no-script")
    seed(case)
    patch(
        node_of(case, "S2c-integration.md"),
        "呼叫現有 `docs/dev/tools/devflow-integration-regression.sh`(或\n"
        "`scripts/devflow-integration-regression.sh`)。",
        "呼叫本節點自寫的整合回歸。",
    )
    expect(
        "P0 S2c 做什麼沒點名 devflow-integration-regression.sh 必須紅",
        case,
        1,
        "devflow-integration-regression.sh",
    )

    case = os.path.join(tmpbase, "s2c-no-fresh-before")
    seed(case)
    patch(node_of(case, "S2c-integration.md"), "Final Fresh", "Final Gate")
    expect(
        "P0 S2c 做什麼沒寫 Final Fresh 之前必須紅",
        case,
        1,
        "Final Fresh",
    )

    case = os.path.join(tmpbase, "s2d-no-gauntlet")
    seed(case)
    patch(
        node_of(case, "S2d-fresh.md"),
        "呼叫現有 `docs/dev/tools/devflow-evidence-gauntlet.sh`(或\n"
        "`scripts/devflow-evidence-gauntlet.sh`)。",
        "呼叫本節點自寫的 Fresh 腳本。",
    )
    expect(
        "P0 S2d 做什麼沒點名 devflow-evidence-gauntlet.sh 必須紅",
        case,
        1,
        "devflow-evidence-gauntlet.sh",
    )

    case = os.path.join(tmpbase, "s2d-no-sha")
    seed(case)
    patch(
        node_of(case, "S2d-fresh.md"),
        "Source SHA = 當下 HEAD = 送審樹。\n不重寫 Gauntlet,不另寫通過條件。",
        "綁當下送審樹。不重寫 Gauntlet,不另寫通過條件。",
    )
    expect("P0 S2d 做什麼沒寫 SHA／HEAD 必須紅", case, 1, "SHA")

    case = os.path.join(tmpbase, "n0-allow-review")
    seed(case)
    patch(
        graph_of(case),
        "  N0-role:\n    file: nodes/N0-role.md\n    next: N1-matrix\n",
        "  N0-role:\n    file: nodes/N0-role.md\n    next: N1-matrix\n"
        "    allow:\n      - write_review\n",
    )
    expect("P0 N0 之外 allow write_review 必須紅", case, 1, "N0-role")

    case = os.path.join(tmpbase, "s2-no-allow")
    seed(case)
    patch(
        graph_of(case),
        "    allow:\n      - write_review\n    forbid:\n      - read_notes\n      - write_notes\n"
        "  S2b-phenomena:",
        "    forbid:\n      - read_notes\n      - write_notes\n"
        "  S2b-phenomena:",
    )
    expect("P0 S2-run 缺 allow write_review 必須紅", case, 1, "S2-run")

    case = os.path.join(tmpbase, "n4-no-allow-review")
    seed(case)
    patch(
        graph_of(case),
        "    allow:\n      - write_review\n      - read_notes\n",
        "    allow:\n      - read_notes\n",
    )
    expect("P0 N4 缺 allow write_review 必須紅", case, 1, "N4-author")

    case = os.path.join(tmpbase, "allow-notes")
    seed(case)
    patch(
        graph_of(case),
        "    allow:\n      - write_review\n      - read_notes\n",
        "    allow:\n      - write_review\n      - read_notes\n      - write_notes\n",
    )
    expect("P0 任何節點 allow write_notes 必須紅", case, 1, "write_notes")

    case = os.path.join(tmpbase, "s2-allow-read")
    seed(case)
    patch(
        graph_of(case),
        "  S2-run:\n    file: nodes/S2-run.md\n    next: S2b-phenomena\n"
        "    write:\n      - docs/dev/<slug>/7-review.md\n"
        "    write_mode: overwrite\n    allow:\n      - write_review\n"
        "    forbid:\n      - read_notes\n      - write_notes\n",
        "  S2-run:\n    file: nodes/S2-run.md\n    next: S2b-phenomena\n"
        "    write:\n      - docs/dev/<slug>/7-review.md\n"
        "    write_mode: overwrite\n    allow:\n      - write_review\n"
        "      - read_notes\n"
        "    forbid:\n      - write_notes\n",
    )
    expect("P0 S2-run allow read_notes 必須紅", case, 1, "read_notes")

    case = os.path.join(tmpbase, "g2-not-approved")
    seed(case)
    patch(
        os.path.join(case, "docs", "dev", "fixture-slug", "4-spec.md"),
        "status: approved",
        "status: draft",
    )
    expect(
        "P0 已有 7-review.md 卻沒過 G2,N0 當入口必須紅",
        case,
        1,
        "退回第 4 站",
    )

    case = os.path.join(tmpbase, "self-review-extra")
    seed(case)
    open(
        os.path.join(case, "docs", "dev", "fixture-slug", "7-self-review.md"),
        "w",
        encoding="utf-8",
    ).write("x\n")
    expect("P0 同 slug 出現 7-self-review.md 必須紅", case, 1, "7-self-review.md")

    case = os.path.join(tmpbase, "n0-allow-read-notes")
    seed(case)
    patch(
        graph_of(case),
        "  N0-role:\n    file: nodes/N0-role.md\n    next: N1-matrix\n",
        "  N0-role:\n    file: nodes/N0-role.md\n    next: N1-matrix\n"
        "    allow:\n      - read_notes\n",
    )
    expect("P0 N4 之外 allow read_notes 必須紅", case, 1, "read_notes")

    case = os.path.join(tmpbase, "n4-no-allow-read")
    seed(case)
    patch(
        graph_of(case),
        "    allow:\n      - write_review\n      - read_notes\n",
        "    allow:\n      - write_review\n",
    )
    expect("P0 N4 缺 allow read_notes 必須紅", case, 1, "read_notes")

    actions = os.path.join(fix, "actions")

    expect(
        "P0 N0-role 做 write_review 必須紅",
        good,
        1,
        "N0-role",
        extra=["--action", os.path.join(actions, "n0-write-review.json")],
    )
    expect(
        "P0 N1-matrix 做 write_review 必須紅",
        good,
        1,
        "N1-matrix",
        extra=["--action", os.path.join(actions, "n1-write-review.json")],
    )
    expect(
        "P0 N5-verdict 做 write_review 必須紅",
        good,
        1,
        "N5-verdict",
        extra=["--action", os.path.join(actions, "n5-write-review.json")],
    )
    expect(
        "P0 N3-axes 做 write_review 必須紅",
        good,
        1,
        "N3-axes",
        extra=["--action", os.path.join(actions, "n3-write-review.json")],
    )
    expect(
        "P0 第一刀節點名 skill-legacy-2 跑 --action → exit 2",
        good,
        2,
        "沒有節點",
        extra=["--action", os.path.join(actions, "legacy-write-review.json")],
    )
    expect(
        "G-action N4-author + 4-spec approved → write_review 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n4-write-review-ok.json")],
    )
    expect(
        "G-action S2-run + 4-spec approved → write_review 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "s2-write-review-ok.json")],
    )
    expect(
        "G-action S2c-integration + 4-spec approved → write_review 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "s2c-write-review-ok.json")],
    )
    expect(
        "P0 未過 G2(4-spec 不是 approved)卻 write_review 必須紅",
        good,
        1,
        "G2",
        extra=["--action", os.path.join(actions, "n4-write-review-pending.json")],
    )
    expect(
        "P0 S2-run + 未過 G2 → write_review 必須紅",
        good,
        1,
        "G2",
        extra=["--action", os.path.join(actions, "s2-write-review-pending.json")],
    )
    expect(
        "P0 審查期 N4 做 write_notes 必須紅",
        good,
        1,
        "6-implementation-notes",
        extra=["--action", os.path.join(actions, "n4-write-notes.json")],
    )
    expect(
        "P0 審查期 N0 做 write_notes 必須紅",
        good,
        1,
        "6-implementation-notes",
        extra=["--action", os.path.join(actions, "n0-write-notes.json")],
    )
    expect(
        "P0 N0-role 做 read_notes 必須紅",
        good,
        1,
        "read_notes",
        extra=["--action", os.path.join(actions, "n0-read-notes.json")],
    )
    expect(
        "P0 S2-run 做 read_notes 必須紅",
        good,
        1,
        "read_notes",
        extra=["--action", os.path.join(actions, "s2-read-notes.json")],
    )
    expect(
        "G-action N4-author read_notes 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n4-read-notes-ok.json")],
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
        extra=["--action", os.path.join(actions, "n4-write-review-ok.json")],
    )

    wrote = os.path.join(tmpbase, "cursor")
    os.makedirs(wrote)
    proc = subprocess.run(
        ["bash", check, "--write-cursor", "N0-role", "fixture-slug", wrote],
        capture_output=True,
        text=True,
    )
    cursor_path = os.path.join(wrote, ".devstage7-cursor.json")
    ok = proc.returncode == 0 and os.path.isfile(cursor_path)
    if ok:
        data = json.loads(open(cursor_path, encoding="utf-8").read())
        ok = data.get("node") == "N0-role" and data.get("slug") == "fixture-slug"
    if ok:
        passed += 1
        print("  ✓ G-cursor --write-cursor N0-role 寫出 .devstage7-cursor.json")
    else:
        failed += 1
        print("  ✗ G-cursor --write-cursor 沒寫出游標檔", file=sys.stderr)
        print((proc.stdout or "") + (proc.stderr or ""), file=sys.stderr)

    wrote2 = os.path.join(tmpbase, "cursor-s2c")
    os.makedirs(wrote2)
    proc = subprocess.run(
        ["bash", check, "--write-cursor", "S2c-integration", "fixture-slug", wrote2],
        capture_output=True,
        text=True,
    )
    cursor_path = os.path.join(wrote2, ".devstage7-cursor.json")
    ok = proc.returncode == 0 and os.path.isfile(cursor_path)
    if ok:
        data = json.loads(open(cursor_path, encoding="utf-8").read())
        ok = data.get("node") == "S2c-integration"
    if ok:
        passed += 1
        print("  ✓ G-cursor --write-cursor S2c-integration 寫出 .devstage7-cursor.json")
    else:
        failed += 1
        print("  ✗ G-cursor --write-cursor S2c-integration 沒寫出游標檔", file=sys.stderr)
        print((proc.stdout or "") + (proc.stderr or ""), file=sys.stderr)

total = passed + failed
print(f"=== test-devstage7-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < 48:
    print(f"⛔ 案例數 {total} < 48,牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
