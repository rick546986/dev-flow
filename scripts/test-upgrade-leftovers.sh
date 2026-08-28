#!/bin/bash
# test-upgrade-leftovers.sh — upgrade 殘件刪除的行為牙
#
# 種一棵假採用樹:退役 _templates/CONTEXT.md + baseline 複本 + 專案正在用的
# docs/dev/CONTEXT.md + 專案根 CONTEXT.md。upgrade 殘件腳本必須刪掉前兩者,
# 不准動後兩者。dry-run 不准刪。pack 仍出貨的模板不准被當殘件。
#
# 用法:scripts/test-upgrade-leftovers.sh [pack]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
PACK=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  PACK=$(cd "$1" && pwd) || exit 2
fi

TOOL="$SELF_DIR/devflow-upgrade-leftovers.sh"
[ -f "$TOOL" ] || { echo "FATAL: 找不到 $TOOL" >&2; exit 2; }
chmod +x "$TOOL"

python3 - "$PACK" "$TOOL" <<'PY'
import os
import shutil
import subprocess
import sys
import tempfile

pack, tool = sys.argv[1], sys.argv[2]
passed = 0
failed = 0
MIN_CASES = 4


def run(root, *args):
    return subprocess.run(
        ["bash", tool, "--root", root, "--pack", pack, *args],
        capture_output=True,
        text=True,
    )


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


def plant(tmp):
    root = os.path.join(tmp, "proj")
    os.makedirs(os.path.join(root, "docs", "dev", "_templates"))
    os.makedirs(os.path.join(root, "docs", "dev", ".devflow-baseline", "_templates"))
    leftovers = (
        os.path.join(root, "docs", "dev", "_templates", "CONTEXT.md"),
        os.path.join(root, "docs", "dev", ".devflow-baseline", "_templates", "CONTEXT.md"),
    )
    live = os.path.join(root, "docs", "dev", "CONTEXT.md")
    top = os.path.join(root, "CONTEXT.md")
    kept = os.path.join(root, "docs", "dev", "_templates", "HISTORY.md")
    for path, body in (
        (leftovers[0], "retired template leftover\n"),
        (leftovers[1], "retired baseline leftover\n"),
        (live, "live project context\n"),
        (top, "root context\n"),
        (kept, "still-shipped template\n"),
    ):
        open(path, "w", encoding="utf-8").write(body)
    return root, leftovers, live, top, kept


with tempfile.TemporaryDirectory(prefix="upgrade-leftovers-") as tmp:
    root, leftovers, live, top, kept = plant(tmp)
    dry = run(root)
    expect(
        "dry-run 列出殘件且 exit 0",
        dry.returncode == 0 and "leftover:" in dry.stdout,
        (dry.stdout or "") + (dry.stderr or ""),
    )
    expect(
        "dry-run 不准刪檔",
        all(os.path.isfile(p) for p in leftovers + (live, top, kept)),
        "dry-run 後有檔消失",
    )

    applied = run(root, "--apply")
    expect(
        "apply 刪掉 _templates/CONTEXT.md 與 baseline 複本",
        applied.returncode == 0
        and not os.path.isfile(leftovers[0])
        and not os.path.isfile(leftovers[1]),
        (applied.stdout or "") + (applied.stderr or ""),
    )
    expect(
        "apply 保留專案根 CONTEXT.md、live docs/dev/CONTEXT.md、仍出貨的 HISTORY.md",
        os.path.isfile(live)
        and os.path.isfile(top)
        and os.path.isfile(kept)
        and open(live, encoding="utf-8").read() == "live project context\n"
        and open(top, encoding="utf-8").read() == "root context\n",
        "受保護檔被動到",
    )

if passed < MIN_CASES:
    print(
        "⛔ 實際只跑了 %d 案(地板 %d)" % (passed + failed, MIN_CASES),
        file=sys.stderr,
    )
    sys.exit(1)
if failed:
    print("⛔ test-upgrade-leftovers: %d 案失敗" % failed, file=sys.stderr)
    sys.exit(1)
print("✅ test-upgrade-leftovers: %d 案全過" % passed)
sys.exit(0)
PY
