#!/bin/bash
# test-spec-gate-e2e.sh — G2 機械關卡 C10(P2-1 executable e2e)的牙。
#
# roadmap P2-1 驗收是**紅路**:「缺 e2e 且無理由 → G2 紅」。devflow-check 只對正例跑 check-spec-gate,
# 沒有東西釘住 C10 真的會紅;本檔用 scripts/fixtures/spec-gate-e2e/ 六份 fixture:
#   bad-missing / bad-bare-none / bad-empty      → exit 1 且只有 C10 紅
#   good-command / good-none-reason             → exit 0
#   bad-none-punct / bad-none-synonym / bad-none-english(無。／不適用／N/A.)→ exit 1(同義形仍是「只寫了無」)
#   bad-placeholder(模板佈局字沒填)／bad-draft-with-verdict-pass(draft 打 PASS 不算 legacy)→ exit 1
#   bad-none-bang／bad-na-dotted／bad-prose-placeholder／bad-symbols-only／bad-wrapped-placeholder → exit 1
#   bad-inreview-with-verdict-pass(in-review 打 PASS 不算 legacy)→ exit 1
#   good-subshell-command／good-bracket-command／good-nats-command(括號起頭、na 開頭的真命令)→ exit 0
#   legacy-pass-no-field(verdict: PASS + status approved、無欄)→ exit 0(legacy 不套;不回頭打紅已出貨 feature)
# 用法:bash scripts/test-spec-gate-e2e.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail
SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then ROOT=$(cd "$1" && pwd) || exit 2; fi
GATE="$ROOT/scripts/check-spec-gate.sh"; FIX="$ROOT/scripts/fixtures/spec-gate-e2e"
[ -f "$GATE" ] || { echo "FATAL: 找不到 $GATE" >&2; exit 2; }
[ -d "$FIX" ] || { echo "FATAL: 找不到 $FIX" >&2; exit 2; }
pass=0; fail=0
case_() { # case_ <fixture> <expected_exit> <must_contain|-> <must_not_contain|->
  local out rc
  out=$(bash "$GATE" "$FIX/$1" 2>&1); rc=$?
  if [ "$rc" -ne "$2" ]; then echo "  ❌ $1: exit $rc(預期 $2)"; echo "$out" | grep "❌" | sed 's/^/     /'; fail=$((fail+1)); return; fi
  if [ "$3" != "-" ] && ! printf '%s' "$out" | grep -q -- "$3"; then echo "  ❌ $1: 輸出缺「$3」"; fail=$((fail+1)); return; fi
  if [ "$4" != "-" ] && printf '%s' "$out" | grep -q -- "$4"; then echo "  ❌ $1: 輸出不該含「$4」"; fail=$((fail+1)); return; fi
  echo "  ✅ $1 (exit $rc)"; pass=$((pass+1))
}
case_ bad-missing.md        1 "❌ C10" "❌ C[1-9] "
case_ bad-bare-none.md      1 "❌ C10" "❌ C[1-9] "
case_ bad-empty.md          1 "❌ C10" "❌ C[1-9] "
case_ bad-none-punct.md     1 "❌ C10" "❌ C[1-9] "
case_ bad-none-synonym.md   1 "❌ C10" "❌ C[1-9] "
case_ bad-none-english.md   1 "❌ C10" "❌ C[1-9] "
case_ bad-placeholder.md    1 "❌ C10" "❌ C[1-9] "
case_ bad-draft-with-verdict-pass.md 1 "❌ C10" "❌ C[1-9] "
case_ bad-none-bang.md      1 "❌ C10" "❌ C[1-9] "
case_ bad-na-dotted.md      1 "❌ C10" "❌ C[1-9] "
case_ bad-prose-placeholder.md 1 "❌ C10" "❌ C[1-9] "
case_ bad-symbols-only.md   1 "❌ C10" "❌ C[1-9] "
case_ bad-wrapped-placeholder.md 1 "❌ C10" "❌ C[1-9] "
case_ bad-inreview-with-verdict-pass.md 1 "❌ C10" "❌ C[1-9] "
case_ good-subshell-command.md 0 "✅ C10" -
case_ good-nats-command.md  0 "✅ C10" -
case_ good-bracket-command.md 0 "✅ C10" -
case_ good-command.md       0 "✅ C10" -
case_ good-none-reason.md   0 "✅ C10" -
case_ legacy-pass-no-field.md 0 "legacy" -
MIN_CASES=20
[ $((pass+fail)) -ge $MIN_CASES ] || { echo "⛔ 案例數 $((pass+fail)) < $MIN_CASES" >&2; exit 1; }
if [ "$fail" -ne 0 ]; then echo "⛔ test-spec-gate-e2e: $fail 失敗 / $((pass+fail))"; exit 1; fi
echo "✅ test-spec-gate-e2e: C10 紅路／綠路／legacy 全部依預期($pass 案)"
