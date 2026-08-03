#!/bin/bash
# ADR 編號唯一性守衛(Repo-local,相容性守衛,不重編號、不改命名方案)。
#
# 規則(只驗這兩條,不判斷 ADR 內容好壞):
#   ①`docs/adr/NNNN-*.md` 的檔名格式:四位數字 + `-` + kebab-case slug + `.md`。
#   ②同一個 NNNN 不得出現兩次(重複編號 = 引用會指到兩份文件,追溯鏈斷)。
#
# 本腳本**不重新編號既有 ADR**,也不把命名改成 UUID 或時間戳 —— 本輪只做相容性守衛。
#
# 用法:
#   scripts/check-adr-integrity.sh [root]      # 掃 root(缺省 = repo root)+ 跑 fixture battery
#   scripts/check-adr-integrity.sh --scan DIR  # 只掃 DIR 這個 adr 目錄,回傳其 exit code
#                                              # (供 §12 mutation 驗證使用)
#
# Fixture battery(證明負向規則真的被覆蓋;fixture 刻意放在 scripts/fixtures/adr/ 而
# **不是** docs/adr/,否則重複編號 fixture 會讓本 repo 的真實掃描永遠紅):
#   scripts/fixtures/adr/good/            → 必須 PASS
#   scripts/fixtures/adr/duplicate-number/→ 必須 FAIL(重複 0007)
#   scripts/fixtures/adr/bad-filename/    → 必須 FAIL(檔名格式錯)

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

SCAN_ONLY=""
if [ "${1:-}" = "--scan" ]; then
  if [ -z "${2:-}" ]; then
    echo "usage: $0 --scan <adr-dir>" >&2
    exit 2
  fi
  SCAN_ONLY="$2"
elif [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

scan() {
  # $1 = adr directory
  python3 - "$1" <<'PY'
import os
import re
import sys

adr_dir = sys.argv[1]
pattern = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")

if not os.path.isdir(adr_dir):
    print(f"  • {adr_dir} absent — 0 files scanned(採用專案才有 ADR;母版 repo 無)")
    raise SystemExit(0)

names = sorted(n for n in os.listdir(adr_dir) if n.endswith(".md"))
problems = []
numbers = {}
for name in names:
    match = pattern.match(name)
    if not match:
        problems.append(f"檔名格式錯:{name}(需 NNNN-kebab-slug.md,四位數字)")
        continue
    numbers.setdefault(match.group(1), []).append(name)

for number, owners in sorted(numbers.items()):
    if len(owners) > 1:
        problems.append(f"編號重複:{number} 出現 {len(owners)} 次 → {owners}")

print(f"  • {adr_dir}: {len(names)} 個 .md 掃描")
for problem in problems:
    print(f"  ✗ {problem}")
if problems:
    raise SystemExit(1)
print(f"  ✓ 編號唯一且檔名格式合規({len(numbers)} 個編號)")
PY
}

if [ -n "$SCAN_ONLY" ]; then
  scan "$SCAN_ONLY"
  exit $?
fi

echo "=== ADR 編號唯一性守衛 ==="
FAILED=0

echo "-- 真實掃描 --"
scan "$ROOT/docs/adr" || FAILED=1

echo "-- fixture battery(證明負向規則有覆蓋)--"
battery() {
  local dir="$1" expect="$2" label="$3"
  local out rc
  out=$(scan "$SELF_DIR/fixtures/adr/$dir" 2>&1)
  rc=$?
  if [ "$expect" = "pass" ] && [ "$rc" -eq 0 ]; then
    echo "  ✓ $label:如預期 PASS"
  elif [ "$expect" = "fail" ] && [ "$rc" -ne 0 ]; then
    echo "  ✓ $label:如預期 FAIL"
  else
    echo "  ✗ $label:預期 $expect,實得 exit $rc"
    echo "$out" | sed 's/^/      /'
    FAILED=1
  fi
}
battery good             pass "good fixture(編號唯一、檔名合規)"
battery duplicate-number fail "duplicate-number fixture(0007 出現兩次)"
battery bad-filename     fail "bad-filename fixture(檔名格式錯)"

echo
if [ "$FAILED" -ne 0 ]; then
  echo "⛔ ADR 編號唯一性守衛:FAILED"
  exit 1
fi
echo "✅ ADR 編號唯一性守衛:全過"
exit 0
