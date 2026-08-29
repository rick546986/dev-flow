#!/bin/bash
# test-write-scope.sh — Bash 寫 scope 外必須當場失敗(prevent-before)
#
# 重現 engine-fence-masking Known Limits #5:Edit 擋得住,Bash 舊路先寫再
# postbash 示警。本檔的牙是:先跑 --action,允許才真的寫。收寬成只
# detect-after(--action 恆 allow)必須紅,因為檔會落盤。
#
# 三邊共同入口是 scripts/check-write-scope.sh --action,不是 Claude hook。
# prebash / Edit 擋法另有對照案,不准比 --action 更鬆。
#
# 用法:scripts/test-write-scope.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-write-scope.sh"
GUARD="$ROOT/hooks/devflow-guard.sh"
PREBASH="$ROOT/hooks/devflow-prebash.sh"
EXEC="$ROOT/hooks/devflow-exec.sh"
LIB="$ROOT/hooks/devflow-lib.py"
[ -f "$CHECK" ] || { echo "FATAL: 找不到 $CHECK" >&2; exit 2; }
[ -f "$GUARD" ] || { echo "FATAL: 找不到 $GUARD" >&2; exit 2; }
[ -f "$PREBASH" ] || { echo "FATAL: 找不到 $PREBASH" >&2; exit 2; }
[ -f "$EXEC" ] || { echo "FATAL: 找不到 $EXEC" >&2; exit 2; }
[ -f "$LIB" ] || { echo "FATAL: 找不到 $LIB" >&2; exit 2; }
chmod +x "$CHECK"

# 必須接 --action。拿掉這段字面 = 三邊共同入口沒了。
if ! grep -q '\[ "${1:-}" = "--action" \]' "$CHECK"; then
  echo "FATAL: $CHECK 不再接 --action" >&2
  exit 2
fi

. "$ROOT/hooks/devflow-python-lib.sh"

python3 - "$ROOT" "$CHECK" "$GUARD" "$PREBASH" "$EXEC" "$DEVFLOW_PY" <<'PY'
import json
import os
import shutil
import subprocess
import sys
import tempfile

root, check, guard, prebash, exec_sh, py = sys.argv[1:7]
passed = 0
failed = 0
MIN_CASES = 8


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


def run(cmd, cwd, env=None, input_text=None):
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        cmd, cwd=cwd, env=merged, input=input_text,
        capture_output=True, text=True)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def action(tree, payload):
    payload_path = os.path.join(tree, ".action.json")
    write_json(payload_path, payload)
    return run(["bash", check, "--action", payload_path, tree], cwd=tree)


def prevent_then_write(tree, command, dest_rel, wipe_new=True):
    """先 --action,允許才執行指令。detect-after 實作會讓 dest 落盤。

    wipe_new=True:測「新檔不該出現」時先清掉殘件。
    wipe_new=False:測「既有檔內容不準變」時不動原檔。
    """
    dest = os.path.join(tree, dest_rel)
    if wipe_new and os.path.exists(dest):
        os.remove(dest)
    proc = action(tree, {"command": command})
    if proc.returncode == 0:
        subprocess.run(["bash", "-lc", command], cwd=tree, check=False)
    return proc, dest


def hook_payload(tool, **tool_input):
    return json.dumps({"tool_name": tool, "tool_input": tool_input})


def setup_armed(tmp):
    subprocess.run(["git", "init", "-q", "."], cwd=tmp, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp, check=True)
    os.makedirs(os.path.join(tmp, "docs", "dev", "f1"))
    os.makedirs(os.path.join(tmp, "src"))
    os.makedirs(os.path.join(tmp, "tests", "parallel-stage6"))
    open(os.path.join(tmp, "docs", "dev", "f1", "4-spec.md"), "w").write(
        "---\nstatus: approved\n---\n"
    )
    open(os.path.join(tmp, "docs", "dev", "f1", "5-tasks.md"), "w").write(
        "## T-1 guard fixture\n"
        "- Covers: R-1\n"
        "- Files: src/a.py, src/lib/\n"
        "- Verify: `true`\n"
        "- Blocked-by: —\n"
    )
    open(os.path.join(tmp, "src", "a.py"), "w").write("a\n")
    os.makedirs(os.path.join(tmp, "src", "lib"))
    open(os.path.join(tmp, "src", "lib", "keep.py"), "w").write("k\n")
    open(os.path.join(tmp, "tests", "parallel-stage6", "contract_ref.py"), "w").write(
        "orig\n"
    )
    open(os.path.join(tmp, ".gitignore"), "w").write("\n")
    subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp, check=True)
    proc = run(["bash", exec_sh, "start", "f1"], cwd=tmp)
    if proc.returncode != 0:
        raise RuntimeError("start 失敗:\n" + (proc.stdout or "") + (proc.stderr or ""))


with tempfile.TemporaryDirectory(prefix="write-scope-") as tmp:
    setup_armed(tmp)
    sneak = "src/sneaky.py"
    observed = "tests/parallel-stage6/contract_ref.py"
    observed_before = open(os.path.join(tmp, observed), encoding="utf-8").read()

    # 1. 原觀察:Bash 寫 scope 外。先 --action,允許才寫。檔不準落盤。
    proc, dest = prevent_then_write(
        tmp, "echo sneak > src/sneaky.py", sneak)
    expect(
        "原觀察:echo > scope 外 --action 必須 deny 且檔不落盤",
        proc.returncode != 0 and not os.path.exists(dest)
        and "scope 外" in ((proc.stdout or "") + (proc.stderr or "")),
        "rc=%s exists=%s out=%s" % (
            proc.returncode, os.path.exists(dest),
            (proc.stdout or "") + (proc.stderr or "")),
    )

    # 2. 收寬成 detect-after 必須紅:若 --action 恆 allow,上一案會寫出檔。
    #    本案再釘「檢查腳本自己不落盤」——呼叫後工作樹仍無 sneaky。
    expect(
        "收寬成 detect-after 必須紅:--action 之後 sneaky 仍不存在",
        not os.path.exists(os.path.join(tmp, sneak)),
        "檔已落盤 —— --action 變成先寫再警告",
    )

    # 3. 原觀察路徑(審查時撞到的檔):Bash 改 contract_ref.py 必須當場失敗。
    proc, dest = prevent_then_write(
        tmp,
        "echo mutated > tests/parallel-stage6/contract_ref.py",
        observed,
        wipe_new=False,
    )
    after = open(os.path.join(tmp, observed), encoding="utf-8").read()
    expect(
        "原觀察路徑:Bash 寫 tests/parallel-stage6/contract_ref.py 必須 deny 且內容不變",
        proc.returncode != 0 and after == observed_before,
        "rc=%s after=%r" % (proc.returncode, after),
    )

    # 4. 正向:scope 內 redirect --action 放行,真寫成功。
    proc, dest = prevent_then_write(
        tmp, "echo in-scope > src/a.py", "src/a.py")
    expect(
        "正向:scope 內 echo > src/a.py --action 放行且寫入成功",
        proc.returncode == 0 and os.path.isfile(dest)
        and "in-scope" in open(dest, encoding="utf-8").read(),
        "rc=%s out=%s" % (proc.returncode, (proc.stdout or "") + (proc.stderr or "")),
    )

    # 5. Edit 擋法不準更鬆:Write scope 外仍 exit 2。
    g = run(
        ["bash", guard],
        cwd=tmp,
        input_text=hook_payload("Write", file_path=os.path.join(tmp, sneak)),
    )
    expect(
        "Edit 路:Write scope 外仍擋(不準比修前更鬆)",
        g.returncode == 2 and "scope 外" in ((g.stdout or "") + (g.stderr or "")),
        "rc=%s out=%s" % (g.returncode, (g.stdout or "") + (g.stderr or "")),
    )

    # 6. Edit 路正向仍放行。
    g = run(
        ["bash", guard],
        cwd=tmp,
        input_text=hook_payload("Write", file_path=os.path.join(tmp, "src/a.py")),
    )
    expect(
        "Edit 路:Write scope 內仍放行",
        g.returncode == 0,
        "rc=%s out=%s" % (g.returncode, (g.stdout or "") + (g.stderr or "")),
    )

    # 7. Claude prebash 接到同一套:payload 擋下,自己不落盤。
    sneak2 = os.path.join(tmp, "src", "prebash-sneaky.py")
    pb = run(
        ["bash", prebash],
        cwd=tmp,
        input_text=hook_payload(
            "Bash", command="echo prebash > src/prebash-sneaky.py"),
    )
    expect(
        "prebash:Bash 寫 scope 外必須 deny 且檔不落盤",
        pb.returncode == 2 and not os.path.exists(sneak2)
        and "scope 外" in ((pb.stdout or "") + (pb.stderr or "")),
        "rc=%s exists=%s out=%s" % (
            pb.returncode, os.path.exists(sneak2),
            (pb.stdout or "") + (pb.stderr or "")),
    )

    # 8. 鎖步:同一 rel,guard Write 與 --action paths 允/拒一致。
    lock_ok = True
    lock_detail = []
    for rel, want_allow in (
        ("src/a.py", True),
        ("src/other.py", False),
        ("tests/parallel-stage6/contract_ref.py", False),
        ("docs/dev/f1/6-implementation-notes.md", True),
        ("docs/dev/f1/4-spec.md", False),
    ):
        g = run(
            ["bash", guard],
            cwd=tmp,
            input_text=hook_payload(
                "Write", file_path=os.path.join(tmp, rel)),
        )
        a = action(tmp, {"paths": [rel]})
        g_allow = g.returncode == 0
        a_allow = a.returncode == 0
        if g_allow != a_allow or g_allow != want_allow:
            lock_ok = False
            lock_detail.append(
                "%s want_allow=%s guard=%s action=%s" % (
                    rel, want_allow, g.returncode, a.returncode))
    expect(
        "鎖步:guard Write 與 --action paths 允/拒一致",
        lock_ok,
        "; ".join(lock_detail),
    )

total = passed + failed
print("=== test-write-scope:%d/%d ===" % (passed, total))
if failed:
    print("⛔ %d 案未依預期" % failed, file=sys.stderr)
    sys.exit(1)
if total < MIN_CASES:
    print("⛔ 案例數 %d < %d,牙齒沒跑齊" % (total, MIN_CASES), file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
