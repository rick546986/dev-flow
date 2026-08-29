#!/bin/bash
# test-history-seed-cleanup.sh — HISTORY 出廠種子一次性清理的行為牙
#
# 只准刪可見的出廠四行。真紀錄、註解裡的格式範例、長得像但不是原文的列
# 都不動;認不出就 fail-closed。不准當成每次 upgrade 的預設動作。
#
# 用法:scripts/test-history-seed-cleanup.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

TOOL="$SELF_DIR/history-append.sh"
[ -f "$TOOL" ] || { echo "FATAL: 找不到 $TOOL" >&2; exit 2; }
chmod +x "$TOOL"

python3 - "$TOOL" <<'PY'
import os
import subprocess
import sys
import tempfile

tool = sys.argv[1]
passed = 0
failed = 0
MIN_CASES = 4
SEED = """## YYYY-MM-DD · <第一筆的代號>
- 做了什麼:<可觀測的結果>
- 為什麼:<當初的痛點>
- 落在哪:<檔案或目錄>"""
REAL = """## 2026-08-20 · live-feature
- 做了什麼:真的做完了
- 為什麼:現場痛點
- 落在哪:src/app.ts"""
HEADER = """# 改版歷史索引

> 只增不改。

<!--
## YYYY-MM-DD · <第一筆的代號>
- 做了什麼:<可觀測的結果>
- 為什麼:<當初的痛點>
- 落在哪:<檔案或目錄>
-->

"""


def run(path, *args):
    return subprocess.run(
        ["bash", tool, "--action", "factory-seed-cleanup", "--file", path, *args],
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


with tempfile.TemporaryDirectory(prefix="history-seed-") as tmp:
    good = os.path.join(tmp, "good.md")
    open(good, "w", encoding="utf-8").write(HEADER + SEED + "\n\n" + REAL + "\n")
    dry = run(good, "--dry-run")
    text = open(good, encoding="utf-8").read()
    expect(
        "dry-run 列出種子且不改檔",
        dry.returncode == 0 and "factory-seed:" in dry.stdout and SEED in text,
        (dry.stdout or "") + (dry.stderr or ""),
    )
    applied = run(good)
    after = open(good, encoding="utf-8").read()
    expect(
        "apply 只刪可見種子,真紀錄與註解範例留下",
        applied.returncode == 0
        and "factory-seed: removed" in applied.stdout
        and SEED not in after.split("-->")[-1]
        and REAL in after
        and "<!--" in after
        and "<第一筆的代號>" in after,
        (applied.stdout or "") + (applied.stderr or "") + "\n---\n" + after,
    )

    live = os.path.join(tmp, "live-only.md")
    open(live, "w", encoding="utf-8").write(HEADER + REAL + "\n")
    none = run(live)
    expect(
        "沒有可見種子 → exit 0 且檔案不動",
        none.returncode == 0
        and "factory-seed: none" in none.stdout
        and REAL in open(live, encoding="utf-8").read(),
        (none.stdout or "") + (none.stderr or ""),
    )

    weird = os.path.join(tmp, "lookalike.md")
    open(weird, "w", encoding="utf-8").write(
        HEADER + "## YYYY-MM-DD · <被改過的代號>\n- 做了什麼:有人填了\n"
    )
    closed = run(weird)
    expect(
        "長得像種子但不是原文 → fail-closed 不刪",
        closed.returncode == 2
        and "fail-closed" in (closed.stderr or "")
        and "<被改過的代號>" in open(weird, encoding="utf-8").read(),
        (closed.stdout or "") + (closed.stderr or ""),
    )

if passed < MIN_CASES:
    print("⛔ 實際只跑了 %d 案(地板 %d)" % (passed + failed, MIN_CASES), file=sys.stderr)
    sys.exit(1)
if failed:
    print("⛔ test-history-seed-cleanup: %d 案失敗" % failed, file=sys.stderr)
    sys.exit(1)
print("✅ test-history-seed-cleanup: %d 案全過" % passed)
sys.exit(0)
PY
