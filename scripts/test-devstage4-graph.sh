#!/bin/bash
# test-devstage4-graph.sh — check-devstage4-graph.sh 的負向牙
#
# 對照組是一份最小合法 graph(四真節點 + 兩個 skill-legacy 暫留 hop)。
# 每個案例把對照組改壞一次,確認檢查真的紅。
# 另有一份「舊實作(單一 SKILL、沒有 graph)」fixture,必須紅 ——
# 這就是「先寫測試、舊實作先紅」的永久牙齒,不是散文。
# 第一刀:必須有 N5-write-md;只有它可 allow write_spec;write_tasks 一律 deny;
# 有 via 必須紅;kind: skill-legacy 本刀合法(第二刀才改成必須紅)。
# 本刀不測 prebash、不測 guide #stage4 鏈 —— 那是第三刀。
#
# 用法:scripts/test-devstage4-graph.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-devstage4-graph.sh"
FIX="$SELF_DIR/fixtures/devstage4-graph"
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

NODES = ("skills", "dev-flow", "stage4", "nodes")


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
    return os.path.join(case, "skills", "dev-flow", "stage4", "graph.yaml")


def node_of(case, name):
    return os.path.join(case, *NODES, name)


# 第 3 站觸發判定命中一條、frontmatter 仍是 draft —— 第 4 站不得當入口。
STAGE3_HIT = """---
feature: fixture-slug
stage: 3-prototype
status: draft
---

# 3. 原型 — fixture

## Stage 3 觸發判定(條件式必要)
- [x] 有新的前端流程
- [ ] 改變使用者下一步
"""


with tempfile.TemporaryDirectory(prefix="devstage4-graph-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(四真節點 + 兩暫留 hop)必須綠", good, 0)

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
    patch(node_of(case, "N1-handoff.md"), "## 進條件", "## 入口備註")
    expect("P0 真節點缺進條件必須紅", case, 1, "進條件")

    case = os.path.join(tmpbase, "missing-done-heading")
    seed(case)
    patch(node_of(case, "N5-write-md.md"), "## 完成條件", "## 收尾備註")
    expect("P0 真節點缺完成條件必須紅", case, 1, "完成條件")

    case = os.path.join(tmpbase, "second-md")
    seed(case)
    slug = os.path.join(case, "docs", "dev", "fixture-slug")
    open(os.path.join(slug, "4-spec-rerun.md"), "w", encoding="utf-8").write("x\n")
    expect("P0 同 slug 第二份 4-spec*.md 必須紅", case, 1, "4-spec*.md")

    case = os.path.join(tmpbase, "save-as")
    seed(case)
    patch(graph_of(case), "write_mode: overwrite", "write_mode: save_as")
    expect("P0 write_mode≠overwrite 必須紅", case, 1, "overwrite")

    case = os.path.join(tmpbase, "no-write-node")
    seed(case)
    patch(graph_of(case), "  N5-write-md:\n", "  N5-later:\n")
    expect(
        "P0 缺 N5-write-md 必須紅(第一刀不能只做 handoff)",
        case,
        1,
        "第一刀必須有寫檔節點",
    )

    case = os.path.join(tmpbase, "via-hop")
    seed(case)
    patch(
        graph_of(case),
        "  skill-legacy-1-4:\n    kind: skill-legacy\n",
        "  skill-legacy-1-4:\n    via: _templates/4-spec.md\n    kind: skill-legacy\n",
    )
    expect("P0 有 via 當 hop 必須紅", case, 1, "via")

    case = os.path.join(tmpbase, "legacy-not-real-node")
    seed(case)
    patch(graph_of(case), "  skill-legacy-5:\n    kind: skill-legacy\n", "  skill-legacy-5:\n")
    expect(
        "P0 暫留步不是 kind: skill-legacy 真節點必須紅",
        case,
        1,
        "skill-legacy",
    )

    case = os.path.join(tmpbase, "bad-entry")
    seed(case)
    patch(graph_of(case), "entry: N1-handoff", "entry: N5-write-md")
    expect("P0 entry 不是 N1-handoff 必須紅", case, 1, "entry")

    case = os.path.join(tmpbase, "broken-chain")
    seed(case)
    patch(graph_of(case), "    next: skill-legacy-5\n", "    next: N6-g2\n")
    expect("P0 鏈跳過 skill-legacy-5 必須紅", case, 1, "skill-legacy-5")

    case = os.path.join(tmpbase, "no-cursor-call")
    seed(case)
    patch(node_of(case, "N6-g2.md"), "--write-cursor", "--no-cursor-call")
    expect("P0 真節點缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "n1-allow-spec")
    seed(case)
    patch(
        graph_of(case),
        "  N1-handoff:\n    file: nodes/N1-handoff.md\n    next: skill-legacy-1-4\n",
        "  N1-handoff:\n    file: nodes/N1-handoff.md\n    next: skill-legacy-1-4\n"
        "    allow:\n      - write_spec\n",
    )
    expect("P0 N5 之外 allow write_spec 必須紅", case, 1, "N1-handoff")

    case = os.path.join(tmpbase, "n5-no-allow-spec")
    seed(case)
    patch(graph_of(case), "    allow:\n      - write_spec\n", "")
    expect("P0 N5 缺 allow write_spec 必須紅", case, 1, "N5-write-md")

    case = os.path.join(tmpbase, "allow-tasks")
    seed(case)
    patch(
        graph_of(case),
        "    allow:\n      - write_spec\n",
        "    allow:\n      - write_spec\n      - write_tasks\n",
    )
    expect("P0 任何節點 allow write_tasks 必須紅", case, 1, "write_tasks")

    case = os.path.join(tmpbase, "stage3-unfinished")
    seed(case)
    open(
        os.path.join(case, "docs", "dev", "fixture-slug", "3-prototype.md"),
        "w",
        encoding="utf-8",
    ).write(STAGE3_HIT)
    expect(
        "P0 第 3 站必要卻缺 approved、又無 skip OC,N1 當入口必須紅",
        case,
        1,
        "退回第 3 站",
    )

    case = os.path.join(tmpbase, "stage3-skip-oc")
    seed(case)
    open(
        os.path.join(case, "docs", "dev", "fixture-slug", "3-prototype.md"),
        "w",
        encoding="utf-8",
    ).write(STAGE3_HIT)
    patch(
        os.path.join(case, "docs", "dev", "fixture-slug", "2-decision.md"),
        "# 2. 收斂 — fixture",
        "# 2. 收斂 — fixture\n\n- Owner Call:Stage 3 跳過,理由 fixture。",
    )
    expect("G-skip-oc 有 skip OC 時 N1 當入口必須綠", case, 0)

    case = os.path.join(tmpbase, "stage3-approved")
    seed(case)
    open(
        os.path.join(case, "docs", "dev", "fixture-slug", "3-prototype.md"),
        "w",
        encoding="utf-8",
    ).write(STAGE3_HIT.replace("status: draft", "status: approved"))
    expect("G-stage3 已 approved 時 N1 當入口必須綠", case, 0)

    actions = os.path.join(fix, "actions")

    expect(
        "P0 N1-handoff 做 write_spec 必須紅",
        good,
        1,
        "N1-handoff",
        extra=["--action", os.path.join(actions, "n1-write-spec.json")],
    )
    expect(
        "P0 N6-g2 做 write_spec 必須紅",
        good,
        1,
        "N6-g2",
        extra=["--action", os.path.join(actions, "n6-write-spec.json")],
    )
    expect(
        "P0 N7-end 做 write_spec 必須紅",
        good,
        1,
        "N7-end",
        extra=["--action", os.path.join(actions, "n7-write-spec.json")],
    )
    expect(
        "P0 skill-legacy-1-4 做 write_spec 必須紅",
        good,
        1,
        "skill-legacy-1-4",
        extra=["--action", os.path.join(actions, "legacy-write-spec.json")],
    )
    expect(
        "G-action N5-write-md + 2-decision approved → write_spec 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n5-write-spec-ok.json")],
    )
    expect(
        "P0 未過 G1(2-decision 不是 approved)卻 write_spec 必須紅",
        good,
        1,
        "G1",
        extra=["--action", os.path.join(actions, "n5-write-spec-pending.json")],
    )
    expect(
        "P0 G2 前寫 5-tasks.md(write_tasks)必須紅 — N5",
        good,
        1,
        "5-tasks",
        extra=["--action", os.path.join(actions, "n5-write-tasks.json")],
    )
    expect(
        "P0 G2 前寫 5-tasks.md(write_tasks)必須紅 — N1",
        good,
        1,
        "5-tasks",
        extra=["--action", os.path.join(actions, "n1-write-tasks.json")],
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
        extra=["--action", os.path.join(actions, "n5-write-spec-ok.json")],
    )

    wrote = os.path.join(tmpbase, "cursor")
    os.makedirs(wrote)
    proc = subprocess.run(
        ["bash", check, "--write-cursor", "N1-handoff", "fixture-slug", wrote],
        capture_output=True,
        text=True,
    )
    cursor_path = os.path.join(wrote, ".devstage4-cursor.json")
    ok = proc.returncode == 0 and os.path.isfile(cursor_path)
    if ok:
        data = json.loads(open(cursor_path, encoding="utf-8").read())
        ok = data.get("node") == "N1-handoff" and data.get("slug") == "fixture-slug"
    if ok:
        passed += 1
        print("  ✓ G-cursor --write-cursor N1-handoff 寫出 .devstage4-cursor.json")
    else:
        failed += 1
        print("  ✗ G-cursor --write-cursor 沒寫出游標檔", file=sys.stderr)
        print((proc.stdout or "") + (proc.stderr or ""), file=sys.stderr)

total = passed + failed
print(f"=== test-devstage4-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < 8:
    print(f"⛔ 案例數 {total} < 8,牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
