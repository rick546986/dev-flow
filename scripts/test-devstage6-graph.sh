#!/bin/bash
# test-devstage6-graph.sh — check-devstage6-graph.sh 的負向牙(第三刀)
#
# 對照組是一份最小合法 graph(第二刀:五個真節點,沒有 skill-legacy 團塊)。
# 每個案例把對照組改壞一次,確認檢查真的紅。
# 另有一份「舊實作(單一 SKILL、沒有 graph)」fixture,必須紅 ——
# 這就是「先寫測試、舊實作先紅」的永久牙齒,不是散文。
# 第二刀:乘客步 2(逐 T)必須是真節點檔 S2-tdd;kind: skill-legacy 必須紅;
# 每個真節點「做什麼」必須 --write-cursor <自己的 id>;
# N1-arm 與 S2-tdd 才 allow write_notes(同一份 6-implementation-notes.md,
# overwrite);不放寬 N2-handoff／N4-selfcheck／N5-end;
# 有 via 必須紅;S2-tdd 做什麼必須點名 README §5 且寫明「不是一 T 一 hop」;
# 一 T 一 hop(節點名 T-1)必須紅。
# 第三刀:hooks 沒接 --action(或只寫在註解)必須紅;guide 第 6 站開頭缺五節點鏈、
# 缺「逐 T 仍走引擎」、或出現「Stage 6 還在單一 SKILL」必須紅;prebash 實跑 ——
# 沒游標不攔截,有游標時 N2／N4／N5 寫 6-notes 擋、N1／S2 放行、5-tasks 未定案擋、
# S2 沒武裝擋,且不搶第 4／5 站的 4-spec.md／5-tasks.md。圍欄②不改鬆。
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
MIN_CASES = 57


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


def notes_block(node_id, next_id):
    return (
        f"  {node_id}:\n"
        f"    file: nodes/{node_id}.md\n"
        f"    next: {next_id}\n"
        "    write:\n"
        "      - docs/dev/<slug>/6-implementation-notes.md\n"
        "    write_mode: overwrite\n"
        "    allow:\n"
        "      - write_notes\n"
    )


def put_guide(case, body):
    folder = os.path.join(case, "guides")
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, "guide-dev-flow.html"), "w", encoding="utf-8").write(
        body
    )


def put_hooks(case, body):
    folder = os.path.join(case, "hooks")
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, "_prebash_impl.py"), "w", encoding="utf-8").write(
        body
    )


CHAIN_GUIDE = """<h3 id="stage6">Stage 6 — 實作(TDD)</h3>
<p>節點鏈正本 skills/dev-flow/stage6/graph.yaml:
N1-arm → N2-handoff → S2-tdd → N4-selfcheck → N5-end。
逐 T 仍走引擎。</p>
<h3 id="stage7">Stage 7</h3>
"""


with tempfile.TemporaryDirectory(prefix="devstage6-graph-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(五真節點,無 skill-legacy)必須綠", good, 0)

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
    patch(node_of(case, "S2-tdd.md"), "## 完成條件", "## 收尾備註")
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

    case = os.path.join(tmpbase, "save-as-n1")
    seed(case)
    patch(
        graph_of(case),
        notes_block("N1-arm", "N2-handoff"),
        notes_block("N1-arm", "N2-handoff").replace(
            "write_mode: overwrite", "write_mode: save_as"
        ),
    )
    expect("P0 N1-arm write_mode≠overwrite 必須紅", case, 1, "overwrite")

    case = os.path.join(tmpbase, "save-as-s2")
    seed(case)
    patch(
        graph_of(case),
        notes_block("S2-tdd", "N4-selfcheck"),
        notes_block("S2-tdd", "N4-selfcheck").replace(
            "write_mode: overwrite", "write_mode: save_as"
        ),
    )
    expect("P0 S2-tdd write_mode≠overwrite 必須紅", case, 1, "overwrite")

    case = os.path.join(tmpbase, "no-write-node")
    seed(case)
    patch(graph_of(case), "  N1-arm:\n", "  N1-later:\n")
    expect(
        "P0 缺 N1-arm 必須紅(不能只做 handoff)",
        case,
        1,
        "必須有寫檔節點",
    )

    case = os.path.join(tmpbase, "via-hop")
    seed(case)
    patch(
        graph_of(case),
        "  S2-tdd:\n    file: nodes/S2-tdd.md\n",
        "  S2-tdd:\n    via: README.md\n    file: nodes/S2-tdd.md\n",
    )
    expect("P0 有 via 當 hop 必須紅", case, 1, "via")

    case = os.path.join(tmpbase, "legacy-kind")
    seed(case)
    patch(
        graph_of(case),
        "  S2-tdd:\n    file: nodes/S2-tdd.md\n",
        "  S2-tdd:\n    kind: skill-legacy\n    file: nodes/S2-tdd.md\n",
    )
    expect("P0 節點仍掛 kind: skill-legacy 必須紅", case, 1, "skill-legacy 團塊")

    case = os.path.join(tmpbase, "legacy-blob")
    seed(case)
    patch(graph_of(case), "    next: S2-tdd\n", "    next: skill-legacy-T\n")
    patch(
        graph_of(case),
        notes_block("S2-tdd", "N4-selfcheck"),
        "  skill-legacy-T:\n"
        "    kind: skill-legacy\n"
        "    entry: _templates/6-implementation-notes.md\n"
        '    steps: "T"\n'
        "    next: N4-selfcheck\n"
        "    forbid:\n"
        "      - write_notes\n",
    )
    expect("P0 把 T 收回 skill-legacy 團塊必須紅", case, 1, "skill-legacy")

    case = os.path.join(tmpbase, "per-t-hop")
    seed(case)
    patch(
        graph_of(case),
        "  N5-end:\n    file: nodes/N5-end.md\n    next: \"\"\n    forbid:\n      - write_notes\n",
        "  N5-end:\n    file: nodes/N5-end.md\n    next: \"\"\n    forbid:\n      - write_notes\n"
        "  T-1:\n    file: nodes/T-1.md\n    next: \"\"\n",
    )
    expect("P0 一 T 一 hop(T-1)必須紅", case, 1, "一 T 一 hop")

    case = os.path.join(tmpbase, "bad-entry")
    seed(case)
    patch(graph_of(case), "entry: N1-arm", "entry: N2-handoff")
    expect("P0 entry 不是 N1-arm 必須紅", case, 1, "entry")

    case = os.path.join(tmpbase, "broken-chain")
    seed(case)
    patch(graph_of(case), "    next: S2-tdd\n", "    next: N4-selfcheck\n")
    expect("P0 鏈跳過 S2-tdd 必須紅", case, 1, "S2-tdd")

    for node_file, node_id in (
        ("N2-handoff.md", "N2-handoff"),
        ("S2-tdd.md", "S2-tdd"),
        ("N4-selfcheck.md", "N4-selfcheck"),
        ("N5-end.md", "N5-end"),
    ):
        case = os.path.join(tmpbase, f"no-cursor-{node_id}")
        seed(case)
        patch(node_of(case, node_file), "--write-cursor", "--no-cursor-call")
        expect(f"P0 {node_id} 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "missing-node-file")
    seed(case)
    os.remove(node_of(case, "S2-tdd.md"))
    expect("P0 缺 S2-tdd 節點檔必須紅", case, 1, "S2-tdd")

    case = os.path.join(tmpbase, "s2-no-readme")
    seed(case)
    patch(node_of(case, "S2-tdd.md"), "共用 README §5 動線", "共用模板頂註動線")
    expect("P0 S2-tdd 做什麼沒點名 README §5 必須紅", case, 1, "README §5")

    case = os.path.join(tmpbase, "s2-no-one-hop")
    seed(case)
    patch(node_of(case, "S2-tdd.md"), "不是一 T 一 hop", "逐 T 各走一跳")
    expect(
        "P0 S2-tdd 做什麼沒寫「不是一 T 一 hop」必須紅",
        case,
        1,
        "不是一 T 一 hop",
    )

    case = os.path.join(tmpbase, "n2-allow-notes")
    seed(case)
    patch(
        graph_of(case),
        "  N2-handoff:\n    file: nodes/N2-handoff.md\n    next: S2-tdd\n",
        "  N2-handoff:\n    file: nodes/N2-handoff.md\n    next: S2-tdd\n"
        "    allow:\n      - write_notes\n",
    )
    expect("P0 N2-handoff allow write_notes 必須紅", case, 1, "N2-handoff")

    case = os.path.join(tmpbase, "n4-allow-notes")
    seed(case)
    patch(
        graph_of(case),
        "  N4-selfcheck:\n    file: nodes/N4-selfcheck.md\n    next: N5-end\n",
        "  N4-selfcheck:\n    file: nodes/N4-selfcheck.md\n    next: N5-end\n"
        "    allow:\n      - write_notes\n",
    )
    expect("P0 N4-selfcheck allow write_notes 必須紅", case, 1, "N4-selfcheck")

    case = os.path.join(tmpbase, "n1-no-allow-notes")
    seed(case)
    patch(
        graph_of(case),
        notes_block("N1-arm", "N2-handoff"),
        "  N1-arm:\n"
        "    file: nodes/N1-arm.md\n"
        "    next: N2-handoff\n"
        "    write:\n"
        "      - docs/dev/<slug>/6-implementation-notes.md\n"
        "    write_mode: overwrite\n",
    )
    expect("P0 N1-arm 缺 allow write_notes 必須紅", case, 1, "N1-arm")

    case = os.path.join(tmpbase, "s2-no-allow-notes")
    seed(case)
    patch(
        graph_of(case),
        notes_block("S2-tdd", "N4-selfcheck"),
        "  S2-tdd:\n"
        "    file: nodes/S2-tdd.md\n"
        "    next: N4-selfcheck\n"
        "    write:\n"
        "      - docs/dev/<slug>/6-implementation-notes.md\n"
        "    write_mode: overwrite\n",
    )
    expect("P0 S2-tdd 缺 allow write_notes 必須紅", case, 1, "S2-tdd")

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
        "P0 N2-handoff 做 write_notes 必須紅",
        good,
        1,
        "N2-handoff",
        extra=["--action", os.path.join(actions, "n2-write-notes.json")],
    )
    expect(
        "P0 N4-selfcheck 做 write_notes 必須紅",
        good,
        1,
        "N4-selfcheck",
        extra=["--action", os.path.join(actions, "n4-write-notes.json")],
    )
    expect(
        "P0 N5-end 做 write_notes 必須紅",
        good,
        1,
        "N5-end",
        extra=["--action", os.path.join(actions, "n5-write-notes.json")],
    )
    expect(
        "P0 第一刀節點名 skill-legacy-T 跑 --action → exit 2",
        good,
        2,
        "沒有節點",
        extra=["--action", os.path.join(actions, "legacy-gone.json")],
    )
    expect(
        "G-action N1-arm + 5-tasks approved → write_notes 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n1-write-notes-ok.json")],
    )
    expect(
        "G-action S2-tdd + 5-tasks approved → write_notes 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "s2-write-notes-ok.json")],
    )
    expect(
        "P0 5-tasks 不是 approved 卻 write_notes(N1)必須紅",
        good,
        1,
        "approved",
        extra=["--action", os.path.join(actions, "n1-write-notes-pending.json")],
    )
    expect(
        "P0 5-tasks 不是 approved 卻 write_notes(S2)必須紅",
        good,
        1,
        "approved",
        extra=["--action", os.path.join(actions, "s2-write-notes-pending.json")],
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

    case = os.path.join(tmpbase, "guide-stale")
    seed(case)
    put_guide(
        case,
        CHAIN_GUIDE.replace(
            "</p>",
            "</p>\n<p>Stage 6 還在單一 SKILL</p>",
        ),
    )
    expect("P0 guide 出現「Stage 6 還在單一 SKILL」必須紅", case, 1, "單一 SKILL")

    case = os.path.join(tmpbase, "guide-no-chain")
    seed(case)
    put_guide(
        case,
        '<h3 id="stage6">Stage 6 — 實作(TDD)</h3>\n'
        "<p>實作期唯一日誌。逐 T 仍走引擎。</p>\n"
        '<h3 id="stage7">Stage 7</h3>\n',
    )
    expect("P0 guide 第 6 站開頭缺五節點鏈必須紅", case, 1, "缺節點")

    case = os.path.join(tmpbase, "guide-no-engine")
    seed(case)
    put_guide(
        case,
        '<h3 id="stage6">Stage 6 — 實作(TDD)</h3>\n'
        "<p>N1-arm → N2-handoff → S2-tdd → N4-selfcheck → N5-end。</p>\n"
        '<h3 id="stage7">Stage 7</h3>\n',
    )
    expect("P0 guide 第 6 站開頭缺「逐 T 仍走引擎」必須紅", case, 1, "逐 T 仍走引擎")

    case = os.path.join(tmpbase, "guide-ok")
    seed(case)
    put_guide(case, CHAIN_GUIDE)
    expect("G-guide 第 6 站開頭對上五節點鏈且寫明逐 T 仍走引擎必須綠", case, 0)

    case = os.path.join(tmpbase, "action-unwired")
    seed(case)
    put_hooks(case, "# fixture:有 hooks 但沒接 check-devstage6-graph --action\n")
    expect("P0 hooks 沒接 --action 必須紅", case, 1, "--action")

    case = os.path.join(tmpbase, "action-comment-only")
    seed(case)
    put_hooks(
        case,
        "# check-devstage6-graph.sh --action 只寫在註解不算接線\n",
    )
    expect("P0 --action 只寫在註解必須紅", case, 1, "--action")

    case = os.path.join(tmpbase, "action-wired")
    seed(case)
    put_hooks(
        case,
        'subprocess.run(["bash", "scripts/check-devstage6-graph.sh",\n'
        '               "--action", payload_path, root])\n',
    )
    expect("G-wired hooks 接了 --action 必須綠", case, 0)

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

    wrote2 = os.path.join(tmpbase, "cursor-s2")
    os.makedirs(wrote2)
    proc = subprocess.run(
        ["bash", check, "--write-cursor", "S2-tdd", "fixture-slug", wrote2],
        capture_output=True,
        text=True,
    )
    cursor_path = os.path.join(wrote2, ".devstage6-cursor.json")
    ok = proc.returncode == 0 and os.path.isfile(cursor_path)
    if ok:
        data = json.loads(open(cursor_path, encoding="utf-8").read())
        ok = data.get("node") == "S2-tdd" and data.get("slug") == "fixture-slug"
    if ok:
        passed += 1
        print("  ✓ G-cursor --write-cursor S2-tdd 寫出 .devstage6-cursor.json")
    else:
        failed += 1
        print("  ✗ G-cursor --write-cursor S2-tdd 沒寫出游標檔", file=sys.stderr)
        print((proc.stdout or "") + (proc.stderr or ""), file=sys.stderr)

    prebash = os.path.join(root, "hooks", "devflow-prebash.sh")
    cursor = os.path.join(root, ".devstage6-cursor.json")
    other_cursors = [
        os.path.join(root, ".devtalk-cursor.json"),
        os.path.join(root, ".devstage2-cursor.json"),
        os.path.join(root, ".devstage3-cursor.json"),
        os.path.join(root, ".devstage4-cursor.json"),
        os.path.join(root, ".devstage5-cursor.json"),
    ]
    if os.path.isfile(prebash):
        def run_prebash(command):
            payload = json.dumps({
                "tool_name": "Bash",
                "tool_input": {"command": command},
            })
            return subprocess.run(
                ["bash", prebash],
                input=payload,
                capture_output=True,
                text=True,
                cwd=root,
            )

        def expect_prebash(label, command, want_rc, needle=None):
            global passed, failed
            proc = run_prebash(command)
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
                print(
                    f"  ✗ {label} (rc={proc.returncode} want={want_rc})",
                    file=sys.stderr,
                )
                print(blob[-800:], file=sys.stderr)

        saved = {}
        for path in other_cursors:
            if os.path.isfile(path):
                saved[path] = open(path, encoding="utf-8").read()
                os.remove(path)
        if os.path.isfile(cursor):
            os.remove(cursor)

        ok_slug = os.path.join(root, "docs", "dev", "stage6-prebash-ok")
        pending_slug = os.path.join(root, "docs", "dev", "stage6-prebash-pending")
        unarmed_slug = os.path.join(root, "docs", "dev", "stage6-prebash-unarmed")
        try:
            def write_tasks(slug_dir, status):
                os.makedirs(slug_dir, exist_ok=True)
                open(
                    os.path.join(slug_dir, "5-tasks.md"), "w", encoding="utf-8"
                ).write(
                    f"---\nfeature: {os.path.basename(slug_dir)}\n"
                    f"stage: 5-tasks\nstatus: {status}\n---\n\n# fixture\n"
                )

            def write_notes(slug_dir, sha=None):
                os.makedirs(slug_dir, exist_ok=True)
                body = (
                    f"---\nfeature: {os.path.basename(slug_dir)}\n"
                    "stage: 6-implementation\nstatus: draft\n---\n\n"
                )
                if sha:
                    body += f"FORK_INTEGRATION_SHA: {sha}\n"
                open(
                    os.path.join(slug_dir, "6-implementation-notes.md"),
                    "w",
                    encoding="utf-8",
                ).write(body)

            write_tasks(ok_slug, "approved")
            write_notes(ok_slug, "a" * 40)
            write_tasks(pending_slug, "draft")
            write_tasks(unarmed_slug, "approved")
            write_notes(unarmed_slug, sha=None)
            open(os.path.join(ok_slug, "4-spec.md"), "w", encoding="utf-8").write(
                "---\nfeature: stage6-prebash-ok\nstage: 4-spec\n"
                "status: approved\n---\n\n# fixture\n"
            )

            def point(node, slug):
                open(cursor, "w", encoding="utf-8").write(
                    json.dumps({"node": node, "slug": slug})
                )

            expect_prebash(
                "P0 prebash:沒游標寫 6-notes 不得編成(不是沙盒)",
                "echo x > docs/dev/stage6-prebash-ok/6-implementation-notes.md",
                0,
            )
            point("N2-handoff", "stage6-prebash-ok")
            expect_prebash(
                "P0 prebash:游標 N2-handoff 寫 6-notes 必須擋",
                "echo x > docs/dev/stage6-prebash-ok/6-implementation-notes.md",
                2,
                "N2-handoff",
            )
            point("N4-selfcheck", "stage6-prebash-ok")
            expect_prebash(
                "P0 prebash:游標 N4-selfcheck 寫 6-notes 必須擋",
                "echo x > docs/dev/stage6-prebash-ok/6-implementation-notes.md",
                2,
                "N4-selfcheck",
            )
            point("N5-end", "stage6-prebash-ok")
            expect_prebash(
                "P0 prebash:游標 N5-end 寫 6-notes 必須擋",
                "echo x > docs/dev/stage6-prebash-ok/6-implementation-notes.md",
                2,
                "N5-end",
            )
            point("N1-arm", "stage6-prebash-ok")
            expect_prebash(
                "G-prebash 游標 N1-arm + 5-tasks approved 寫 6-notes 必須放行",
                "echo x > docs/dev/stage6-prebash-ok/6-implementation-notes.md",
                0,
            )
            point("S2-tdd", "stage6-prebash-ok")
            expect_prebash(
                "G-prebash 游標 S2-tdd + 已武裝寫 6-notes 必須放行",
                "cat > docs/dev/stage6-prebash-ok/6-implementation-notes.md <<'EOF'\nx\nEOF",
                0,
            )
            point("N1-arm", "stage6-prebash-pending")
            expect_prebash(
                "P0 prebash:5-tasks 未定案寫 6-notes 必須擋",
                "echo x > docs/dev/stage6-prebash-pending/6-implementation-notes.md",
                2,
                "approved",
            )
            point("S2-tdd", "stage6-prebash-unarmed")
            expect_prebash(
                "P0 prebash:S2-tdd 沒武裝寫 6-notes 必須擋",
                "echo x > docs/dev/stage6-prebash-unarmed/6-implementation-notes.md",
                2,
                "FORK_INTEGRATION_SHA",
            )
            point("N1-arm", "stage6-prebash-ok")
            expect_prebash(
                "G-prebash 只有第 6 站游標時 5-tasks.md 不被第 6 站編成",
                "echo x > docs/dev/stage6-prebash-ok/5-tasks.md",
                0,
            )
            expect_prebash(
                "G-prebash 只有第 6 站游標時 4-spec.md 不被第 6 站編成",
                "echo x > docs/dev/stage6-prebash-ok/4-spec.md",
                0,
            )
        finally:
            if os.path.isfile(cursor):
                os.remove(cursor)
            for path, text in saved.items():
                open(path, "w", encoding="utf-8").write(text)
            shutil.rmtree(ok_slug, ignore_errors=True)
            shutil.rmtree(pending_slug, ignore_errors=True)
            shutil.rmtree(unarmed_slug, ignore_errors=True)
    else:
        failed += 1
        print("  ✗ 找不到 hooks/devflow-prebash.sh", file=sys.stderr)

total = passed + failed
print(f"=== test-devstage6-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < MIN_CASES:
    print(f"⛔ 案例數 {total} < {MIN_CASES},牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
