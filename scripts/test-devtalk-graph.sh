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


with tempfile.TemporaryDirectory(prefix="devtalk-graph-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(合法節點鏈 graph)必須綠", good, 0)

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
        "N3-probe:\n    file: nodes/N3-probe.md\n    next: S4-accept",
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
        "0130-P0 游標在 N1-start 且已有 session → talk start 必須紅",
        good,
        1,
        "talk start",
        extra=["--action", os.path.join(actions, "n1-restart.json")],
    )
    expect(
        "0130-P0 沒游標檔但已有 session → talk start 必須紅",
        good,
        1,
        "talk start",
        extra=["--action", os.path.join(actions, "no-cursor-open-session.json")],
    )

    case = os.path.join(tmpbase, "n1-no-forbid-if-session")
    seed(case)
    graph = os.path.join(case, "skills", "dev-talk", "graph.yaml")
    text = open(graph, encoding="utf-8").read()
    # 舊實作:N1 只有 allow talk_start,沒有 forbid talk_start_if_session
    if "talk_start_if_session" in text:
        text = text.replace(
            "  N1-start:\n    file: nodes/N1-start.md\n    next: S0-scope\n"
            "    allow:\n      - talk_start\n    forbid:\n"
            "      - talk_start_if_session\n",
            "  N1-start:\n    file: nodes/N1-start.md\n    next: S0-scope\n"
            "    allow:\n      - talk_start\n    forbid:\n",
        )
        open(graph, "w", encoding="utf-8").write(text)
    expect(
        "0130-P0 N1 缺 talk_start_if_session 必須紅",
        case,
        1,
        "talk_start_if_session",
    )
    expect(
        "P0-3 N13 → talk end 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n13-end-ok.json")],
    )
    expect(
        "0947-P0 沒游標檔 → write_code --action 必須紅",
        good,
        1,
        "write_code",
        extra=["--action", os.path.join(actions, "no-cursor-write-code.json")],
    )
    expect(
        "0947-P0 沒游標檔 → talk_end --action 必須紅",
        good,
        1,
        "talk_end",
        extra=["--action", os.path.join(actions, "no-cursor-talk-end.json")],
    )
    expect(
        "0947-P0 沒游標檔 → write_knowledge --action 必須紅",
        good,
        1,
        "write_knowledge",
        extra=["--action", os.path.join(actions, "no-cursor-write-knowledge.json")],
    )

    case = os.path.join(tmpbase, "skill-no-cursor-call")
    seed(case)
    skill = os.path.join(case, "skills", "dev-talk", "SKILL.md")
    text = open(skill, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(skill, "w", encoding="utf-8").write(text)
    expect("0947-P0 SKILL 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "n1-no-cursor-call")
    seed(case)
    n1 = os.path.join(case, "skills", "dev-talk", "nodes", "N1-start.md")
    text = open(n1, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(n1, "w", encoding="utf-8").write(text)
    expect("0947-P0 N1 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "missing-s0")
    seed(case)
    os.remove(os.path.join(case, "skills", "dev-talk", "nodes", "S0-scope.md"))
    expect("0947-P0 缺 S0-scope 節點檔必須紅", case, 1, "S0-scope")

    case = os.path.join(tmpbase, "s4-no-entry")
    seed(case)
    s4 = os.path.join(case, "skills", "dev-talk", "nodes", "S4-accept.md")
    text = open(s4, encoding="utf-8").read().replace("## 進條件", "## 入口備註")
    open(s4, "w", encoding="utf-8").write(text)
    expect("0947-P0 leftover 缺進條件必須紅", case, 1, "進條件")

    case = os.path.join(tmpbase, "n3-no-cursor-call")
    seed(case)
    n3 = os.path.join(case, "skills", "dev-talk", "nodes", "N3-probe.md")
    text = open(n3, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(n3, "w", encoding="utf-8").write(text)
    expect("P0-2 N3 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "n13-no-cursor-call")
    seed(case)
    n13 = os.path.join(case, "skills", "dev-talk", "nodes", "N13-end.md")
    text = open(n13, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(n13, "w", encoding="utf-8").write(text)
    expect("P0-2 N13 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "s0-no-cursor-call")
    seed(case)
    s0 = os.path.join(case, "skills", "dev-talk", "nodes", "S0-scope.md")
    text = open(s0, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(s0, "w", encoding="utf-8").write(text)
    expect("P0-2 S0-scope 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "skip-s4")
    seed(case)
    graph = os.path.join(case, "skills", "dev-talk", "graph.yaml")
    text = open(graph, encoding="utf-8").read().replace(
        "N3-probe:\n    file: nodes/N3-probe.md\n    next: S4-accept",
        "N3-probe:\n    file: nodes/N3-probe.md\n    next: S5-diverge",
    )
    open(graph, "w", encoding="utf-8").write(text)
    n3 = os.path.join(case, "skills", "dev-talk", "nodes", "N3-probe.md")
    open(n3, "w", encoding="utf-8").write(
        open(n3, encoding="utf-8").read().replace("S4-accept", "S5-diverge")
    )
    expect("0947-P0 N3 next 跳過 S4 必須紅", case, 1, "暫留")

    case = os.path.join(tmpbase, "dual-s2")
    seed(case)
    skill = os.path.join(case, "skills", "dev-talk", "SKILL.md")
    open(skill, "a", encoding="utf-8").write("\n系統外角色也要列\n")
    expect("0947-P0 SKILL 與 S2 雙正本必須紅", case, 1, "雙正本")

    wrote = os.path.join(tmpbase, "cursor-out")
    os.makedirs(wrote)
    proc = subprocess.run(
        ["bash", check, "--write-cursor", "N1-start", "sess-write", wrote],
        capture_output=True, text=True,
    )
    cursor_path = os.path.join(wrote, ".devtalk-cursor.json")
    got = {}
    if os.path.isfile(cursor_path):
        got = json.load(open(cursor_path, encoding="utf-8"))
    ok = (
        proc.returncode == 0
        and got.get("node") == "N1-start"
        and got.get("MEMORY_SESSION_ID") == "sess-write"
    )
    if ok:
        passed += 1
        print("  ✓ 0947-P0 --write-cursor 真的寫出 node + MEMORY_SESSION_ID")
    else:
        failed += 1
        print(
            f"  ✗ 0947-P0 --write-cursor (rc={proc.returncode} got={got})",
            file=sys.stderr,
        )

    case = os.path.join(tmpbase, "skip-legacy")
    seed(case)
    graph = os.path.join(case, "skills", "dev-talk", "graph.yaml")
    text = open(graph, encoding="utf-8").read()
    text = text.replace("    next: S4-accept\n", "    next: N9-write-md\n")
    open(graph, "w", encoding="utf-8").write(text)
    n3 = os.path.join(case, "skills", "dev-talk", "nodes", "N3-probe.md")
    n3text = open(n3, encoding="utf-8").read().replace(
        "S4-accept", "N9-write-md"
    )
    open(n3, "w", encoding="utf-8").write(n3text)
    expect("0030-P0 N3 next 跨過暫留步 4–6 必須紅", case, 1, "暫留")

    case = os.path.join(tmpbase, "action-unwired")
    seed(case)
    hooks = os.path.join(case, "hooks")
    os.makedirs(hooks, exist_ok=True)
    open(os.path.join(hooks, "_prebash_impl.py"), "w", encoding="utf-8").write(
        "# fixture:有 hooks 但沒接 check-devtalk-graph --action\n"
    )
    expect("0030-P1 hooks 沒接 --action 必須紅", case, 1, "--action")

    prebash = os.path.join(root, "hooks", "devflow-prebash.sh")
    cursor = os.path.join(root, ".devtalk-cursor.json")
    if os.path.isfile(prebash):
        payload = json.dumps({
            "tool_name": "Bash",
            "tool_input": {
                "command": "memory/dev-memory.py talk start topic"
            },
        })
        try:
            open(cursor, "w", encoding="utf-8").write(json.dumps({
                "node": "N3-probe",
                "MEMORY_SESSION_ID": "sess-n3",
            }))
            proc = subprocess.run(
                ["bash", prebash],
                input=payload,
                capture_output=True,
                text=True,
                cwd=root,
            )
            blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
            ok = proc.returncode == 2 and (
                "talk start" in blob or "talk_start" in blob or "--action" in blob
            )
            if ok:
                passed += 1
                print("  ✓ 0030-P1 prebash:游標在 N3 再 talk start 必須擋")
            else:
                failed += 1
                print(
                    f"  ✗ 0030-P1 prebash N3 talk start "
                    f"(rc={proc.returncode} want=2)",
                    file=sys.stderr,
                )
                print(blob[-800:], file=sys.stderr)
        finally:
            if os.path.isfile(cursor):
                os.remove(cursor)

        # 0130-P0:沒游標檔 + 已有 OPEN session → talk start 必須擋
        mem = os.path.join(root, "memory", "dev-memory.py")
        home = tempfile.mkdtemp(prefix="agentmem-0130-")
        env = os.environ.copy()
        env["AGENTMEM_HOME"] = home
        try:
            start = subprocess.run(
                [sys.executable, mem, "talk", "start", "0130-p0-open-session"],
                cwd=root, capture_output=True, text=True, env=env, timeout=30,
            )
            if os.path.isfile(cursor):
                os.remove(cursor)
            proc = subprocess.run(
                ["bash", prebash],
                input=payload,
                capture_output=True,
                text=True,
                cwd=root,
                env=env,
            )
            blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
            ok = (
                start.returncode == 0
                and proc.returncode == 2
                and (
                    "talk start" in blob
                    or "talk_start" in blob
                    or "OPEN" in blob
                    or "session" in blob
                )
            )
            if ok:
                passed += 1
                print("  ✓ 0130-P0 prebash:沒游標但已有 OPEN session 再 talk start 必須擋")
            else:
                failed += 1
                print(
                    f"  ✗ 0130-P0 prebash 沒游標+OPEN session talk start "
                    f"(start_rc={start.returncode} rc={proc.returncode} want=2)",
                    file=sys.stderr,
                )
                print((start.stderr or start.stdout or "")[-400:], file=sys.stderr)
                print(blob[-800:], file=sys.stderr)
        except (OSError, subprocess.TimeoutExpired) as exc:
            failed += 1
            print(f"  ✗ 0130-P0 prebash 建 OPEN session 失敗:{exc}", file=sys.stderr)
        finally:
            if os.path.isfile(cursor):
                os.remove(cursor)
            shutil.rmtree(home, ignore_errors=True)

        if os.path.isfile(cursor):
            os.remove(cursor)
        for label, cmd, needle in (
            ("talk end", "memory/dev-memory.py talk end sess-x", "talk_end"),
            (
                "write knowledge",
                "echo x > .dev-flow/projects/x/knowledge/foo.md",
                "write_knowledge",
            ),
        ):
            payload = json.dumps({
                "tool_name": "Bash",
                "tool_input": {"command": cmd},
            })
            proc = subprocess.run(
                ["bash", prebash],
                input=payload,
                capture_output=True,
                text=True,
                cwd=root,
            )
            blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
            ok = proc.returncode == 2 and (
                needle in blob or "游標" in blob or "--action" in blob
            )
            if ok:
                passed += 1
                print(f"  ✓ 0947-P0 prebash:沒游標 {label} 必須擋")
            else:
                failed += 1
                print(
                    f"  ✗ 0947-P0 prebash 沒游標 {label} "
                    f"(rc={proc.returncode} want=2)",
                    file=sys.stderr,
                )
                print(blob[-800:], file=sys.stderr)

        def run_prebash(command, env=None):
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
                env=env,
            )

        def expect_prebash(label, command, want_rc, needle=None, env=None):
            global passed, failed
            proc = run_prebash(command, env=env)
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

        write_cmds = (
            (
                "python3 -c open/write",
                "python3 -c \"open('n9-w.txt','w').write('x')\"",
            ),
            (
                "python -c open",
                "python -c \"open('n9-w2.txt','w')\"",
            ),
            ("redirect >", "echo n9-write > n9-redirect.txt"),
            ("redirect >>", "echo n9-append >> n9-append.txt"),
            ("tee", "echo n9-tee | tee n9-tee.txt"),
        )
        extra_dir = tempfile.mkdtemp(prefix="devtalk-wc-extra-")
        write_py = os.path.join(extra_dir, "write_file.py")
        read_py = os.path.join(extra_dir, "read_only.py")
        open(write_py, "w", encoding="utf-8").write(
            "open('/tmp/devtalk-wc-script-out','w').write('x')\n"
        )
        open(read_py, "w", encoding="utf-8").write("print('ok')\n")
        extra_cmds = (
            ("python3 script.py", f"python3 {write_py}"),
            ("python script.py", f"python {write_py}"),
            (
                "heredoc",
                "cat > /tmp/devtalk-wc-here.txt <<'EOF'\nhello\nEOF",
            ),
            ("sed -i", f"sed -i 's/a/b/' {write_py}"),
        )
        stdin_write = (
            "python3 - <<'PY'\n"
            "open('/tmp/x','w').write('x')\n"
            "PY"
        )
        stdin_write_py = (
            "python - <<'PY'\n"
            "open('/tmp/x','w').write('x')\n"
            "PY"
        )
        stdin_read = (
            "python3 - <<'PY'\n"
            "print('ok')\n"
            "PY"
        )
        stdin_cmds = (
            ("python3 - << write", stdin_write),
            ("python - << write", stdin_write_py),
        )
        flag_cmds = (
            ("python3 -u script.py", f"python3 -u {write_py}"),
            ("python -B script.py", f"python -B {write_py}"),
        )
        copy_cmds = (
            ("cp SRC DST", "cp README.md /tmp/devtalk-wc-cp.txt"),
            ("cp -f", "cp -f README.md /tmp/devtalk-wc-cpf.txt"),
            ("cp -a", "cp -a README.md /tmp/devtalk-wc-cpa.txt"),
            ("mv SRC DST", "mv /tmp/devtalk-wc-mv-src /tmp/devtalk-wc-mv-dst"),
            ("mv -f", "mv -f /tmp/devtalk-wc-mvf-src /tmp/devtalk-wc-mvf-dst"),
            ("install SRC DST", "install README.md /tmp/devtalk-wc-inst.txt"),
            ("install -m 644", "install -m 644 README.md /tmp/devtalk-wc-instm.txt"),
        )
        try:
            open(cursor, "w", encoding="utf-8").write(json.dumps({
                "node": "N9-write-md",
                "MEMORY_SESSION_ID": "sess-n9",
            }))
            for label, cmd in write_cmds:
                expect_prebash(
                    f"P0-1 prebash:游標 N9 {label} 必須擋",
                    cmd,
                    2,
                    "write_code",
                )
            for label, cmd in (
                ("cat", "cat n9-redirect.txt"),
                ("rg", "rg n9-write"),
                ("ls", "ls"),
                ("talk turn", "memory/dev-memory.py talk turn sess-n9"),
                ("talk propose", "memory/dev-memory.py talk propose sess-n9"),
                ("> /dev/null", "echo n9-null > /dev/null"),
            ):
                expect_prebash(
                    f"P0-1 prebash:游標 N9 {label} 不得編成 write_code",
                    cmd,
                    0,
                )

            for label, cmd in extra_cmds:
                expect_prebash(
                    f"1238-P0 prebash:游標 N9 {label} 必須擋",
                    cmd,
                    2,
                    "write_code",
                )
            expect_prebash(
                "1238-P0 prebash:游標 N9 python3 只讀腳本不得誤編",
                f"python3 {read_py}",
                0,
            )
            for label, cmd in stdin_cmds + flag_cmds:
                expect_prebash(
                    f"1438-P0 prebash:游標 N9 {label} 必須擋",
                    cmd,
                    2,
                    "write_code",
                )
            expect_prebash(
                "1438-P0 prebash:游標 N9 python3 - << 只讀不得誤編",
                stdin_read,
                0,
            )
            expect_prebash(
                "1438-P0 prebash:游標 N9 rg open( && python3 只讀不得誤編",
                f'rg "open(" && python3 {read_py}',
                0,
            )
            for label, cmd in copy_cmds:
                expect_prebash(
                    f"0941-P0 prebash:游標 N9 {label} 必須擋",
                    cmd,
                    2,
                    "write_code",
                )
            for label, cmd in (
                ("cp --help", "cp --help"),
                ("mv --version", "mv --version"),
                ("install --help", "install --help"),
                ("cp 單 operand", "cp README.md"),
            ):
                expect_prebash(
                    f"0941-P0 prebash:游標 N9 {label} 不得編成 write_code",
                    cmd,
                    0,
                )
        finally:
            if os.path.isfile(cursor):
                os.remove(cursor)

        home = tempfile.mkdtemp(prefix="agentmem-p01-")
        env = os.environ.copy()
        env["AGENTMEM_HOME"] = home
        mem = os.path.join(root, "memory", "dev-memory.py")
        try:
            start = subprocess.run(
                [sys.executable, mem, "talk", "start", "p01-open-session"],
                cwd=root, capture_output=True, text=True, env=env, timeout=30,
            )
            if os.path.isfile(cursor):
                os.remove(cursor)
            if start.returncode != 0:
                failed += 1
                print(
                    f"  ✗ P0-1 建 OPEN session 失敗 "
                    f"(rc={start.returncode})",
                    file=sys.stderr,
                )
                print((start.stderr or start.stdout or "")[-400:], file=sys.stderr)
            else:
                for label, cmd in write_cmds:
                    expect_prebash(
                        f"P0-1 prebash:沒游標+OPEN session {label} 必須擋",
                        cmd,
                        2,
                        "write_code",
                        env=env,
                    )
                for label, cmd in extra_cmds:
                    expect_prebash(
                        f"1238-P0 prebash:沒游標+OPEN session {label} 必須擋",
                        cmd,
                        2,
                        "write_code",
                        env=env,
                    )
                for label, cmd in stdin_cmds + flag_cmds:
                    expect_prebash(
                        f"1438-P0 prebash:沒游標+OPEN session {label} 必須擋",
                        cmd,
                        2,
                        "write_code",
                        env=env,
                    )
                for label, cmd in copy_cmds:
                    expect_prebash(
                        f"0941-P0 prebash:沒游標+OPEN session {label} 必須擋",
                        cmd,
                        2,
                        "write_code",
                        env=env,
                    )
        except (OSError, subprocess.TimeoutExpired) as exc:
            failed += 1
            print(f"  ✗ P0-1 prebash 建 OPEN session 失敗:{exc}", file=sys.stderr)
        finally:
            if os.path.isfile(cursor):
                os.remove(cursor)
            shutil.rmtree(home, ignore_errors=True)
            shutil.rmtree(extra_dir, ignore_errors=True)
    else:
        failed += 1
        print("  ✗ 0030-P1 找不到 hooks/devflow-prebash.sh", file=sys.stderr)

    guide_check = os.path.join(os.path.dirname(check), "check-devtalk-guide-sync.sh")
    if os.path.isfile(guide_check):
        live_skill = os.path.join(root, "skills", "dev-talk", "SKILL.md")
        live_guide = os.path.join(root, "guides", "guide-dev-talk.html")
        for label, phrase in (
            ("只拆了四個", "只拆了四個"),
            ("正文還在 SKILL.md", "正文還在 SKILL.md"),
        ):
            case = os.path.join(tmpbase, f"guide-stale-{label}")
            os.makedirs(os.path.join(case, "skills", "dev-talk"), exist_ok=True)
            os.makedirs(os.path.join(case, "guides"), exist_ok=True)
            shutil.copy(live_skill, os.path.join(case, "skills", "dev-talk", "SKILL.md"))
            dest = os.path.join(case, "guides", "guide-dev-talk.html")
            text = open(live_guide, encoding="utf-8").read()
            if phrase not in text:
                text = text.replace(
                    '<h2 id="map">② 全程地圖(12 步)</h2>',
                    f'<h2 id="map">② 全程地圖(12 步)</h2>\n  <p>{phrase}</p>',
                )
            open(dest, "w", encoding="utf-8").write(text)
            proc = subprocess.run(
                ["bash", guide_check, case],
                capture_output=True,
                text=True,
            )
            blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
            ok = proc.returncode == 1 and phrase in blob
            if ok:
                passed += 1
                print(f"  ✓ P1 guide 出現「{label}」必須紅")
            else:
                failed += 1
                print(
                    f"  ✗ P1 guide 「{label}」 "
                    f"(rc={proc.returncode} want=1)",
                    file=sys.stderr,
                )
                print(blob[-800:], file=sys.stderr)
    else:
        failed += 1
        print("  ✗ P1 找不到 scripts/check-devtalk-guide-sync.sh", file=sys.stderr)

total = passed + failed
print(f"=== test-devtalk-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < 91:
    print(f"FATAL: 只跑了 {total} 案,治具沒有真的跑完", file=sys.stderr)
    sys.exit(2)
print("✅ PASS:graph 負向牙全過")
sys.exit(0)
PY
