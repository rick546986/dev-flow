#!/bin/bash
# test-devstage2-graph.sh — check-devstage2-graph.sh 的負向牙
#
# 對照組是一份最小合法 graph(九真節點)。
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
    expect("G-0 對照組(九真節點)必須綠", good, 0)

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

    case = os.path.join(tmpbase, "n3-missing-late-owner")
    seed(case)
    n3 = os.path.join(case, "skills", "dev-flow", "stage2", "nodes", "N3-write-md.md")
    text = open(n3, encoding="utf-8").read().replace("先改 Decision", "先改規格")
    open(n3, "w", encoding="utf-8").write(text)
    expect("P0 N3 完成條件缺「先改 Decision」必須紅", case, 1, "先改 Decision")

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

    expect(
        "P0 N1 已核准仍寫 2-decision 必須紅",
        good,
        1,
        "N1-handoff",
        extra=["--action", os.path.join(actions, "n1-write-decision.json")],
    )

    case = os.path.join(tmpbase, "n7-no-cursor-call")
    seed(case)
    n7 = os.path.join(case, "skills", "dev-flow", "stage2", "nodes", "N7-g1.md")
    text = open(n7, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(n7, "w", encoding="utf-8").write(text)
    expect("P0 N7 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "n8-no-cursor-call")
    seed(case)
    n8 = os.path.join(case, "skills", "dev-flow", "stage2", "nodes", "N8-end.md")
    text = open(n8, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(n8, "w", encoding="utf-8").write(text)
    expect("P0 N8 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "s1-no-cursor-call")
    seed(case)
    s1 = os.path.join(
        case, "skills", "dev-flow", "stage2", "nodes", "S1-approaches.md"
    )
    text = open(s1, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(s1, "w", encoding="utf-8").write(text)
    expect("P0 S1 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "missing-s1")
    seed(case)
    os.remove(
        os.path.join(case, "skills", "dev-flow", "stage2", "nodes", "S1-approaches.md")
    )
    expect("P0 缺 S1-approaches 節點檔必須紅", case, 1, "S1-approaches")

    case = os.path.join(tmpbase, "legacy-blob")
    seed(case)
    graph = os.path.join(case, "skills", "dev-flow", "stage2", "graph.yaml")
    text = open(graph, encoding="utf-8").read()
    text = text.replace(
        "  S1-approaches:\n    file: nodes/S1-approaches.md\n    next: S2-stress\n"
        "    forbid:\n      - write_decision\n",
        "  skill-legacy-1-2:\n    kind: skill-legacy\n    next: S2-stress\n"
        "    forbid:\n      - write_decision\n",
    )
    text = text.replace("    next: S1-approaches\n", "    next: skill-legacy-1-2\n")
    open(graph, "w", encoding="utf-8").write(text)
    expect("P0 skill-legacy 團塊仍在必須紅", case, 1, "skill-legacy")

    expect(
        "P0 S4 + 已核准 → write_decision 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "s4-write-decision-ok.json")],
    )
    expect(
        "P0 S1 不得 write_decision",
        good,
        1,
        "S1-approaches",
        extra=["--action", os.path.join(actions, "s1-write-decision.json")],
    )
    expect(
        "P0 N7 不得 write_decision",
        good,
        1,
        "N7-g1",
        extra=["--action", os.path.join(actions, "n7-write-decision.json")],
    )
    expect(
        "P0 N8 + write_spec 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n8-write-spec-ok.json")],
    )
    expect(
        "P0 N7 寫 4-spec 必須紅",
        good,
        1,
        "4-spec",
        extra=["--action", os.path.join(actions, "n7-write-spec.json")],
    )

    case = os.path.join(tmpbase, "s4-no-allow")
    seed(case)
    graph = os.path.join(case, "skills", "dev-flow", "stage2", "graph.yaml")
    text = open(graph, encoding="utf-8").read()
    text = text.replace(
        "  S4-oc:\n    file: nodes/S4-oc.md\n    next: S5-adr\n"
        "    write:\n      - docs/dev/<slug>/2-decision.md\n"
        "    write_mode: overwrite\n    allow:\n      - write_decision\n",
        "  S4-oc:\n    file: nodes/S4-oc.md\n    next: S5-adr\n"
        "    forbid:\n      - write_decision\n",
    )
    open(graph, "w", encoding="utf-8").write(text)
    expect("P0 S4 缺 allow write_decision 必須紅", case, 1, "S4-oc")

    case = os.path.join(tmpbase, "guide-stale")
    seed(case)
    os.makedirs(os.path.join(case, "guides"), exist_ok=True)
    open(os.path.join(case, "guides", "guide-dev-flow.html"), "w", encoding="utf-8").write(
        '<h3 id="stage2">Stage 2 — 收斂(G1)</h3>\n'
        "<p>N1-handoff S1-approaches S2-stress N3-write-md "
        "S4-oc S5-adr S6-selfcheck N7-g1 N8-end</p>\n"
        "<p>Stage 2 還在單一 SKILL</p>\n"
        "<h3 id=\"stage3\">Stage 3</h3>\n"
    )
    expect("P0 guide 出現「Stage 2 還在單一 SKILL」必須紅", case, 1, "單一 SKILL")

    case = os.path.join(tmpbase, "guide-no-chain")
    seed(case)
    os.makedirs(os.path.join(case, "guides"), exist_ok=True)
    open(os.path.join(case, "guides", "guide-dev-flow.html"), "w", encoding="utf-8").write(
        '<h3 id="stage2">Stage 2 — 收斂(G1)</h3>\n'
        "<p>把 1 的發散收成一個選定方案。</p>\n"
        "<h3 id=\"stage3\">Stage 3</h3>\n"
    )
    expect("P0 guide 第 2 站開頭沒九節點鏈必須紅", case, 1, "缺節點")

    case = os.path.join(tmpbase, "guide-missing")
    seed(case)
    gpath = os.path.join(case, "guides", "guide-dev-flow.html")
    if os.path.isfile(gpath):
        os.remove(gpath)
    expect("P0 指南檔缺席必須紅", case, 1, "指南檔缺席")

    case = os.path.join(tmpbase, "action-unwired")
    seed(case)
    hooks = os.path.join(case, "hooks")
    os.makedirs(hooks, exist_ok=True)
    open(os.path.join(hooks, "_prebash_impl.py"), "w", encoding="utf-8").write(
        "# fixture:有 hooks 但沒接 check-devstage2-graph --action\n"
    )
    expect("P0 hooks 沒接 --action 必須紅", case, 1, "--action")

    prebash = os.path.join(root, "hooks", "devflow-prebash.sh")
    cursor = os.path.join(root, ".devstage2-cursor.json")
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

        if os.path.isfile(cursor):
            os.remove(cursor)
        expect_prebash(
            "P0 prebash:沒游標寫 2-decision.md 不得編成(不是沙盒)",
            "echo x > docs/dev/fixture-slug/2-decision.md",
            0,
        )

        tmp_slug = os.path.join(root, "docs", "dev", "stage2-prebash-tmp")
        try:
            os.makedirs(tmp_slug, exist_ok=True)
            open(os.path.join(tmp_slug, "1-discussion.md"), "w", encoding="utf-8").write(
                "---\nfeature: stage2-prebash-tmp\nstage: 1-discussion\n"
                "status: approved\n---\n\n# fixture\n\n"
                "## Open Questions\n- [x] Q1\n- [~] Q2\n- [>] Q3\n"
            )
            open(cursor, "w", encoding="utf-8").write(json.dumps({
                "node": "N1-handoff",
                "slug": "stage2-prebash-tmp",
            }))
            expect_prebash(
                "P0 prebash:游標 N1 寫 2-decision.md 必須擋",
                "echo x > docs/dev/stage2-prebash-tmp/2-decision.md",
                2,
                "2-decision",
            )
            open(cursor, "w", encoding="utf-8").write(json.dumps({
                "node": "S4-oc",
                "slug": "stage2-prebash-tmp",
            }))
            expect_prebash(
                "P0 prebash:游標 S4 寫 2-decision.md 必須放行",
                "echo x > docs/dev/stage2-prebash-tmp/2-decision.md",
                0,
            )
            open(cursor, "w", encoding="utf-8").write(json.dumps({
                "node": "N7-g1",
                "slug": "stage2-prebash-tmp",
            }))
            expect_prebash(
                "P0 prebash:游標 N7 寫 4-spec.md 必須擋",
                "echo x > docs/dev/stage2-prebash-tmp/4-spec.md",
                2,
                "4-spec",
            )
            open(cursor, "w", encoding="utf-8").write(json.dumps({
                "node": "N8-end",
                "slug": "stage2-prebash-tmp",
            }))
            expect_prebash(
                "P0 prebash:游標 N8 寫 4-spec.md 必須放行",
                "echo x > docs/dev/stage2-prebash-tmp/4-spec.md",
                0,
            )
        finally:
            if os.path.isfile(cursor):
                os.remove(cursor)
            shutil.rmtree(tmp_slug, ignore_errors=True)
    else:
        failed += 1
        print("  ✗ 找不到 hooks/devflow-prebash.sh", file=sys.stderr)

total = passed + failed
print(f"=== test-devstage2-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < 29:
    print(f"⛔ 案例數 {total} < 28,牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
