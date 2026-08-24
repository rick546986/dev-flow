#!/bin/bash
# test-devstage5-graph.sh — check-devstage5-graph.sh 的負向牙(第二刀)
#
# 對照組是一份最小合法 graph(第二刀:八個真節點,沒有 skill-legacy 團塊)。
# 每個案例把對照組改壞一次,確認檢查真的紅。
# 另有一份「舊實作(單一 SKILL、沒有 graph)」fixture,必須紅 ——
# 這就是「先寫測試、舊實作先紅」的永久牙齒,不是散文。
# 第二刀:乘客步 1／2／3／4 必須是真節點檔;kind: skill-legacy 必須紅;
# 每個真節點「做什麼」必須 --write-cursor <自己的 id>;
# S1-slice／S2-fields／S3-deps／S4-selfcheck 與 N4-write-md 才 allow write_tasks
# (同一份 5-tasks.md,overwrite);不放寬 N1-handoff／N5-twin／N6-end;
# write_notes 一律 deny;有 via 必須紅;
# S4-selfcheck 必須點名既有 contract_ref.py 的 parse_5_tasks;
# 四必填欄缺一必須紅 —— 判準是現有 parser,換成不判缺欄的 parser 必須紅。
# 本刀不測 prebash、不測 guide #stage5 鏈 —— 那是第三刀。
#
# 用法:scripts/test-devstage5-graph.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-devstage5-graph.sh"
FIX="$SELF_DIR/fixtures/devstage5-graph"
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

NODES = ("skills", "dev-flow", "stage5", "nodes")


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
    return os.path.join(case, "skills", "dev-flow", "stage5", "graph.yaml")


def node_of(case, name):
    return os.path.join(case, *NODES, name)


def tasks_block(node_id, next_id):
    return (
        f"  {node_id}:\n"
        f"    file: nodes/{node_id}.md\n"
        f"    next: {next_id}\n"
        "    write:\n"
        "      - docs/dev/<slug>/5-tasks.md\n"
        "    write_mode: overwrite\n"
        "    allow:\n"
        "      - write_tasks\n"
        "    forbid:\n"
        "      - write_notes\n"
    )


# 四必填欄的判準是現有 parser。這兩份 stub 只出現在治具裡:一份忠實判缺欄、
# 一份放水,用來證明檢查真的在讀 parser 的輸出,不是自己另寫一套解析。
FAITHFUL_PARSER = '''import re


def parse_5_tasks(text):
    errors = []
    for block in re.split(r"^## (?=T-[0-9])", text, flags=re.M)[1:]:
        tid = block.split()[0]
        for name in ("Covers", "Files", "Verify", "Blocked-by"):
            if not re.search(r"^- " + name + r": *\\S", block, re.M):
                errors.append(tid + " 缺 " + name)
    return {"execution": {}, "tasks": [], "errors": errors}
'''

LAX_PARSER = '''def parse_5_tasks(text):
    return {"execution": {}, "tasks": [], "errors": []}
'''


def put_parser(case, body):
    hooks = os.path.join(case, "hooks")
    os.makedirs(hooks, exist_ok=True)
    with open(os.path.join(hooks, "devflow-lib.py"), "w", encoding="utf-8") as fh:
        fh.write(body)


with tempfile.TemporaryDirectory(prefix="devstage5-graph-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(八真節點,無 skill-legacy)必須綠", good, 0)

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
    patch(node_of(case, "S2-fields.md"), "## 完成條件", "## 收尾備註")
    expect("P0 真節點缺完成條件必須紅", case, 1, "完成條件")

    case = os.path.join(tmpbase, "second-md")
    seed(case)
    slug = os.path.join(case, "docs", "dev", "fixture-slug")
    open(os.path.join(slug, "5-tasks-rerun.md"), "w", encoding="utf-8").write("x\n")
    expect("P0 同 slug 第二份 5-tasks*.md 必須紅", case, 1, "5-tasks*.md")

    case = os.path.join(tmpbase, "save-as-s1")
    seed(case)
    patch(
        graph_of(case),
        tasks_block("S1-slice", "S2-fields"),
        tasks_block("S1-slice", "S2-fields").replace(
            "write_mode: overwrite", "write_mode: save_as"
        ),
    )
    expect("P0 S1-slice write_mode≠overwrite 必須紅", case, 1, "overwrite")

    case = os.path.join(tmpbase, "save-as-n4")
    seed(case)
    patch(
        graph_of(case),
        tasks_block("N4-write-md", "S4-selfcheck"),
        tasks_block("N4-write-md", "S4-selfcheck").replace(
            "write_mode: overwrite", "write_mode: save_as"
        ),
    )
    expect("P0 N4-write-md write_mode≠overwrite 必須紅", case, 1, "overwrite")

    case = os.path.join(tmpbase, "no-write-node")
    seed(case)
    patch(graph_of(case), "  N4-write-md:\n", "  N4-later:\n")
    expect(
        "P0 缺 N4-write-md 必須紅(不能只做 handoff)",
        case,
        1,
        "必須有寫檔節點",
    )

    case = os.path.join(tmpbase, "via-hop")
    seed(case)
    patch(
        graph_of(case),
        "  S2-fields:\n    file: nodes/S2-fields.md\n",
        "  S2-fields:\n    via: _templates/5-tasks.md\n    file: nodes/S2-fields.md\n",
    )
    expect("P0 有 via 當 hop 必須紅", case, 1, "via")

    case = os.path.join(tmpbase, "legacy-kind")
    seed(case)
    patch(
        graph_of(case),
        "  S3-deps:\n    file: nodes/S3-deps.md\n",
        "  S3-deps:\n    kind: skill-legacy\n    file: nodes/S3-deps.md\n",
    )
    expect("P0 節點仍掛 kind: skill-legacy 必須紅", case, 1, "skill-legacy 團塊")

    case = os.path.join(tmpbase, "legacy-blob")
    seed(case)
    patch(graph_of(case), "    next: S1-slice\n", "    next: skill-legacy-1-2\n")
    patch(
        graph_of(case),
        tasks_block("S1-slice", "S2-fields") + tasks_block("S2-fields", "S3-deps"),
        "  skill-legacy-1-2:\n"
        "    kind: skill-legacy\n"
        "    entry: _templates/5-tasks.md\n"
        '    steps: "1-2"\n'
        "    next: S3-deps\n"
        "    forbid:\n"
        "      - write_tasks\n"
        "      - write_notes\n",
    )
    expect("P0 把 1／2 收回 skill-legacy 團塊必須紅", case, 1, "skill-legacy")

    case = os.path.join(tmpbase, "bad-entry")
    seed(case)
    patch(graph_of(case), "entry: N1-handoff", "entry: N4-write-md")
    expect("P0 entry 不是 N1-handoff 必須紅", case, 1, "entry")

    case = os.path.join(tmpbase, "broken-chain")
    seed(case)
    patch(graph_of(case), "    next: S4-selfcheck\n", "    next: N5-twin\n")
    expect("P0 鏈跳過 S4-selfcheck 必須紅", case, 1, "S4-selfcheck")

    case = os.path.join(tmpbase, "chain-skip-s2")
    seed(case)
    patch(graph_of(case), "    next: S2-fields\n", "    next: S3-deps\n")
    expect("P0 鏈跳過 S2-fields 必須紅", case, 1, "S2-fields")

    for node_file, node_id in (
        ("S1-slice.md", "S1-slice"),
        ("S3-deps.md", "S3-deps"),
        ("S4-selfcheck.md", "S4-selfcheck"),
        ("N5-twin.md", "N5-twin"),
    ):
        case = os.path.join(tmpbase, f"no-cursor-{node_id}")
        seed(case)
        patch(node_of(case, node_file), "--write-cursor", "--no-cursor-call")
        expect(f"P0 {node_id} 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "missing-node-file")
    seed(case)
    os.remove(node_of(case, "S3-deps.md"))
    expect("P0 缺 S3-deps 節點檔必須紅", case, 1, "S3-deps")

    case = os.path.join(tmpbase, "parser-not-called")
    seed(case)
    patch(
        node_of(case, "S4-selfcheck.md"),
        "呼叫既有 `contract_ref.py` 的 `parse_5_tasks`",
        "自己再寫一套 5-tasks 解析",
    )
    expect(
        "P0 S4-selfcheck 做什麼沒點名既有 parse_5_tasks 必須紅",
        case,
        1,
        "parse_5_tasks",
    )

    case = os.path.join(tmpbase, "parser-lax")
    seed(case)
    put_parser(case, LAX_PARSER)
    expect(
        "P0 parser 不判四必填欄缺欄必須紅",
        case,
        1,
        "四必填欄缺一必須紅",
    )

    case = os.path.join(tmpbase, "parser-faithful")
    seed(case)
    put_parser(case, FAITHFUL_PARSER)
    expect("G-parser 四必填欄缺一會判紅的 parser 必須綠", case, 0)

    case = os.path.join(tmpbase, "n1-allow-tasks")
    seed(case)
    patch(
        graph_of(case),
        "  N1-handoff:\n    file: nodes/N1-handoff.md\n    next: S1-slice\n",
        "  N1-handoff:\n    file: nodes/N1-handoff.md\n    next: S1-slice\n"
        "    allow:\n      - write_tasks\n",
    )
    expect("P0 N1-handoff allow write_tasks 必須紅", case, 1, "N1-handoff")

    case = os.path.join(tmpbase, "n5-allow-tasks")
    seed(case)
    patch(
        graph_of(case),
        "  N5-twin:\n    file: nodes/N5-twin.md\n    next: N6-end\n",
        "  N5-twin:\n    file: nodes/N5-twin.md\n    next: N6-end\n"
        "    allow:\n      - write_tasks\n",
    )
    expect("P0 N5-twin allow write_tasks 必須紅", case, 1, "N5-twin")

    case = os.path.join(tmpbase, "n4-no-allow-tasks")
    seed(case)
    patch(
        graph_of(case),
        tasks_block("N4-write-md", "S4-selfcheck"),
        "  N4-write-md:\n"
        "    file: nodes/N4-write-md.md\n"
        "    next: S4-selfcheck\n"
        "    write:\n"
        "      - docs/dev/<slug>/5-tasks.md\n"
        "    write_mode: overwrite\n"
        "    forbid:\n"
        "      - write_notes\n",
    )
    expect("P0 N4 缺 allow write_tasks 必須紅", case, 1, "N4-write-md")

    case = os.path.join(tmpbase, "s2-no-allow-tasks")
    seed(case)
    patch(
        graph_of(case),
        tasks_block("S2-fields", "S3-deps"),
        "  S2-fields:\n"
        "    file: nodes/S2-fields.md\n"
        "    next: S3-deps\n"
        "    write:\n"
        "      - docs/dev/<slug>/5-tasks.md\n"
        "    write_mode: overwrite\n"
        "    forbid:\n"
        "      - write_notes\n",
    )
    expect("P0 S2-fields 缺 allow write_tasks 必須紅", case, 1, "S2-fields")

    case = os.path.join(tmpbase, "allow-notes")
    seed(case)
    patch(
        graph_of(case),
        "    allow:\n      - write_tasks\n",
        "    allow:\n      - write_tasks\n      - write_notes\n",
    )
    expect("P0 任何節點 allow write_notes 必須紅", case, 1, "write_notes")

    case = os.path.join(tmpbase, "g2-not-approved")
    seed(case)
    patch(
        os.path.join(case, "docs", "dev", "fixture-slug", "4-spec.md"),
        "status: approved",
        "status: draft",
    )
    expect(
        "P0 已有 5-tasks.md 卻沒過 G2,N1 當入口必須紅",
        case,
        1,
        "退回第 4 站",
    )

    actions = os.path.join(fix, "actions")

    for label, name in (
        ("N1-handoff", "n1-write-tasks.json"),
        ("N5-twin", "n5-write-tasks.json"),
        ("N6-end", "n6-write-tasks.json"),
    ):
        expect(
            f"P0 {label} 做 write_tasks 必須紅",
            good,
            1,
            label,
            extra=["--action", os.path.join(actions, name)],
        )

    for label, name in (
        ("S1-slice", "s1-write-tasks-ok.json"),
        ("S2-fields", "s2-write-tasks-ok.json"),
        ("S4-selfcheck", "s4-write-tasks-ok.json"),
        ("N4-write-md", "n4-write-tasks-ok.json"),
    ):
        expect(
            f"G-action {label} + 4-spec approved → write_tasks 必須綠",
            good,
            0,
            "allow",
            extra=["--action", os.path.join(actions, name)],
        )

    for label, name in (
        ("N4-write-md", "n4-write-tasks-pending.json"),
        ("S1-slice", "s1-write-tasks-pending.json"),
    ):
        expect(
            f"P0 未過 G2(4-spec 不是 approved)卻 write_tasks 必須紅 — {label}",
            good,
            1,
            "G2",
            extra=["--action", os.path.join(actions, name)],
        )

    for label, name in (
        ("N4-write-md", "n4-write-notes.json"),
        ("N1-handoff", "n1-write-notes.json"),
        ("S3-deps", "s3-write-notes.json"),
    ):
        expect(
            f"P0 5-tasks 未定案卻寫 6-notes(write_notes)必須紅 — {label}",
            good,
            1,
            "6-implementation-notes",
            extra=["--action", os.path.join(actions, name)],
        )

    expect(
        "P0 第一刀的 skill-legacy 節點名跑 --action → exit 2(鏈裡已經沒有它)",
        good,
        2,
        "沒有節點",
        extra=["--action", os.path.join(actions, "legacy-gone.json")],
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
        extra=["--action", os.path.join(actions, "n4-write-tasks-ok.json")],
    )

    wrote = os.path.join(tmpbase, "cursor")
    os.makedirs(wrote)
    proc = subprocess.run(
        ["bash", check, "--write-cursor", "S2-fields", "fixture-slug", wrote],
        capture_output=True,
        text=True,
    )
    cursor_path = os.path.join(wrote, ".devstage5-cursor.json")
    ok = proc.returncode == 0 and os.path.isfile(cursor_path)
    if ok:
        data = json.loads(open(cursor_path, encoding="utf-8").read())
        ok = data.get("node") == "S2-fields" and data.get("slug") == "fixture-slug"
    if ok:
        passed += 1
        print("  ✓ G-cursor --write-cursor S2-fields 寫出 .devstage5-cursor.json")
    else:
        failed += 1
        print("  ✗ G-cursor --write-cursor 沒寫出游標檔", file=sys.stderr)
        print((proc.stdout or "") + (proc.stderr or ""), file=sys.stderr)

total = passed + failed
print(f"=== test-devstage5-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
# 第一刀 27、第二刀 44。下限不跟著上修等於留一個「少跑一半照樣綠」的洞。
if total < 44:
    print(f"⛔ 案例數 {total} < 44,牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
