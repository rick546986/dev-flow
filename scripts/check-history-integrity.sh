#!/bin/bash
# 改版歷史索引守衛(Repo-local)。只驗**形狀**,不判斷內容好壞。
#
# 為什麼需要:`docs/dev/HISTORY.md` 是 append-only 的索引,而 append-only 這件事
# 沒有任何機制天然保證 —— 有人用 Edit 直接改、或把新條目插到中間,檔案看起來一樣正常。
# 本守衛把「只增不改」變成可查的:
#   H1 檔案存在,且檔頭帶「不要直接編輯」警語(警語被拿掉 = 下一個人不會知道要用腳本)
#   H2 每筆標題格式 `## YYYY-MM-DD · <slug>[ · vX.Y.Z]`
#   H3 每筆必有「做了什麼 / 為什麼 / 落在哪」三行(少「為什麼」= 半年後沒人知道當初痛點)
#   H4 日期**不得倒退**(新的一定在最下面;倒退 = 有人插到中間或手改過順序)
#   H5 唯一寫入口存在且可執行,且散發副本與正本一致
#   H6 hooks.json 有掛 history-guard(擋 Edit/Write 直接改)
#   H7 `_templates/HISTORY.md` 存在(採用專案要 follow 同一個格式)
#
# 用法:
#   scripts/check-history-integrity.sh            # 驗本 repo + 跑 fixture battery
#   scripts/check-history-integrity.sh --scan F   # 只驗某一份 HISTORY.md,回傳其 exit code
#
# exit code:0 = 全過 / 1 = 有 FAIL / 2 = 用法錯誤
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

SCAN_ONLY=""
if [ "${1:-}" = "--scan" ]; then
  [ -n "${2:-}" ] || { echo "usage: $0 --scan <HISTORY.md>" >&2; exit 2; }
  SCAN_ONLY=$2
elif [ $# -gt 0 ]; then
  echo "usage: $0 [--scan <HISTORY.md>]" >&2
  exit 2
fi

DEVFLOW_HISTORY_SCAN="$SCAN_ONLY" DEVFLOW_ROOT="$ROOT" python3 - <<'PY'
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ["DEVFLOW_ROOT"])
SCAN = os.environ.get("DEVFLOW_HISTORY_SCAN", "")

FAILED = 0
CHECKS = 0


def check(cond, label, detail=""):
    global FAILED, CHECKS
    CHECKS += 1
    if cond:
        print(f"  ✓ {label}")
    else:
        FAILED += 1
        print(f"  ✗ {label}" + (f" — {detail}" if detail else ""))


ENTRY_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2}) · ([a-z0-9-]+)(?: · (\S+))?$")
REQUIRED_FIELDS = ("做了什麼", "為什麼", "落在哪")


def scan_history(path: Path, prefix=""):
    """驗一份 HISTORY.md 的形狀;回傳 (通過?, 失敗訊息 list)。"""
    problems = []
    if not path.is_file():
        return False, [f"{path} 不存在"]

    text = path.read_text(encoding="utf-8")

    # H1 檔頭警語
    if "不要直接編輯" not in text:
        problems.append("檔頭缺「不要直接編輯」警語")
    if "history-append.sh" not in text:
        problems.append("檔頭沒指出唯一寫入口 history-append.sh")

    lines = text.splitlines()
    entries = []
    for i, ln in enumerate(lines):
        if not ln.startswith("## "):
            continue
        m = ENTRY_RE.match(ln)
        if not m:
            problems.append(f"第 {i + 1} 行標題格式錯:{ln!r}(要 `## YYYY-MM-DD · <slug>[ · vX.Y.Z]`)")
            continue
        body = []
        for nxt in lines[i + 1:]:
            if nxt.startswith("## "):
                break
            body.append(nxt)
        missing = [f for f in REQUIRED_FIELDS if not any(b.startswith(f"- {f}:") for b in body)]
        if missing:
            problems.append(f"{m.group(1)} · {m.group(2)} 缺欄位 {missing}")
        entries.append((m.group(1), m.group(2), i + 1))

    if not entries:
        problems.append("一筆條目都沒有(空索引不算通過 —— 檢查解析是否失效)")

    # H4 日期不得倒退
    for (d1, s1, _), (d2, s2, ln2) in zip(entries, entries[1:]):
        if d2 < d1:
            problems.append(f"第 {ln2} 行日期倒退:{s1}({d1}) 之後出現 {s2}({d2}) —— append-only 被破壞")

    return not problems, problems


if SCAN:
    ok, problems = scan_history(Path(SCAN))
    for p in problems:
        print(f"  ✗ {p}")
    if ok:
        print(f"✅ {SCAN}: 形狀全過")
    sys.exit(0 if ok else 1)

print("-- 本 repo 的 HISTORY.md --")
hist = ROOT / "docs/dev/HISTORY.md"
ok, problems = scan_history(hist)
check(ok, "docs/dev/HISTORY.md 形狀合規", "; ".join(problems))

print("-- 寫入口與守衛 --")
src = ROOT / "scripts/history-append.sh"
dist = ROOT / "docs/dev/tools/history-append.sh"
check(src.is_file() and os.access(src, os.X_OK), "scripts/history-append.sh 存在且可執行")
check(dist.is_file() and os.access(dist, os.X_OK), "docs/dev/tools/history-append.sh 散發副本存在且可執行")
if src.is_file() and dist.is_file():
    check(src.read_text(encoding="utf-8") == dist.read_text(encoding="utf-8"),
          "散發副本與正本逐字一致", "正本方向:scripts/ → docs/dev/tools/")

hooks_json = (ROOT / "hooks/hooks.json").read_text(encoding="utf-8")
check("history-guard.sh" in hooks_json, "hooks.json 有掛 history-guard")
guard = ROOT / "hooks/history-guard.sh"
check(guard.is_file() and os.access(guard, os.X_OK), "hooks/history-guard.sh 存在且可執行")

tpl = ROOT / "_templates/HISTORY.md"
check(tpl.is_file() and "不要直接編輯" in tpl.read_text(encoding="utf-8"),
      "_templates/HISTORY.md 存在且帶警語(採用專案 follow 同一格式)")

print("-- fixture battery(證明負向規則真的被覆蓋)--")
fx = ROOT / "scripts/fixtures/history"
for name, expect_ok in (("good", True), ("bad-out-of-order", False), ("bad-missing-field", False),
                        ("bad-no-warning", False)):
    f = fx / name / "HISTORY.md"
    got_ok, _ = scan_history(f)
    check(got_ok == expect_ok,
          f"{name} fixture:如預期 {'PASS' if expect_ok else 'FAIL'}",
          f"實際 {'PASS' if got_ok else 'FAIL'}")

print()
if FAILED:
    print(f"❌ 改版歷史索引守衛:{FAILED} 項失敗(共 {CHECKS} 項)")
    sys.exit(1)
print(f"✅ 改版歷史索引守衛:全過({CHECKS} 項)")
PY
