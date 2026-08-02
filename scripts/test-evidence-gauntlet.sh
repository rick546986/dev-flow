#!/bin/bash
# Tests for scripts/devflow-evidence-gauntlet.sh(文檔方法論層的 gauntlet 入口)。
# 獨立新檔:不動既有 methodology check 基線(條數動態,以該腳本自身輸出為準);
# fixtures 住 scripts/fixtures/evidence-gauntlet/。
# 跑法:bash scripts/test-evidence-gauntlet.sh
set -u

ROOT=$(cd "$(dirname "$0")/.." && pwd)
TOOL="$ROOT/scripts/devflow-evidence-gauntlet.sh"
FIX="$ROOT/scripts/fixtures/evidence-gauntlet"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

checks=0
failures=0

fail() {
  failures=$((failures + 1))
  echo "  ❌ $1"
}

# run_case <label> <expected_exit> <required_output_pattern|-> [tool args...]
run_case() {
  local label="$1" expected_exit="$2" pattern="$3"
  shift 3
  checks=$((checks + 1))
  local out rc
  out=$("$TOOL" "$@" 2>&1)
  rc=$?
  if [ "$rc" -ne "$expected_exit" ]; then
    fail "$label: exit $rc(預期 $expected_exit)"
    echo "$out" | sed 's/^/     /'
    return
  fi
  if [ "$pattern" != "-" ] && ! printf '%s' "$out" | grep -q "$pattern"; then
    fail "$label: 輸出缺少 pattern「$pattern」"
    echo "$out" | sed 's/^/     /'
    return
  fi
  echo "  ✅ $label"
}

if [ ! -x "$TOOL" ]; then
  echo "❌ evidence gauntlet tests: tool 不存在或不可執行:$TOOL"
  exit 1
fi

echo "== 十六.單一 entry point / 四值 status(pass|fail|unverified|n-a)=="
# 合法 evidence:四值都出現且合規,SHA 綁定相符 → 唯一一條指令全部層驗完,exit 0
run_case "good evidence 全綠" 0 "evidence gauntlet" \
  "$FIX/good-evidence.md" --source-sha abc1234def5678
run_case "good evidence 不帶 --source-sha 亦可跑(SHA 檢查降為宣告存在性)" 0 "-" \
  "$FIX/good-evidence.md"

echo "== 七.status 只能四值;沒跑不能寫 PASS =="
run_case "非法 status 值被擋(E3)" 1 "E3" "$FIX/bad-status-value.md"
run_case "pass 但 Command/Result 空 = 沒跑寫 PASS(E4)" 1 "E4" "$FIX/bad-pass-no-run.md"
run_case "pass 但 Result 無數字 = 形容詞非證據(anti-gaming,E4)" 1 "E4" \
  "$FIX/bad-pass-adjective.md"

echo "== 七.skipped layer 必有理由 =="
run_case "unverified 無 Skipped reason(E5)" 1 "E5" "$FIX/bad-missing-reason.md"

echo "== 七.Gauntlet 失敗不得宣告 PASS =="
run_case "任一層 fail → 整體非零退出(E6)" 1 "E6" "$FIX/bad-fail-layer.md"

echo "== 六.source SHA binding / Final Fresh Run 晚於最後修改 =="
# 宣告 SHA ≠ 當下 SHA = 證據產生後又改過碼 → stale,擋下
run_case "宣告 SHA 與當下 SHA 不符 = stale evidence(E2)" 1 "E2" \
  "$FIX/good-evidence.md" --source-sha 999beef000
run_case "header 欄位缺漏(E1)" 1 "E1" "$FIX/bad-missing-header.md"

echo "== 二/四.Required layers(Verification Profile 對照)=="
# Race/stress 在 fixture 內是 unverified:required 層必須實跑,unverified 不滿足
run_case "required layer 未實跑(unverified 不滿足 required,E7)" 1 "E7" \
  "$FIX/good-evidence.md" --require-layer "Race/stress"
run_case "required layer 完全缺席(E7)" 1 "E7" \
  "$FIX/good-evidence.md" --require-layer "Fuzzing"
run_case "required layer 實跑 pass 則過" 0 "-" \
  "$FIX/good-evidence.md" --require-layer "Mutation"

echo "== 八.changed-line coverage:列 covered/total,禁全域 % 虛榮數字 =="
run_case "coverage pass 只寫百分比無 covered/total(E8)" 1 "E8" \
  "$FIX/bad-coverage-vanity.md"

echo "== 九.mutation:survivor 未解釋不得 pass;tool error 不算 killed =="
run_case "mutation 7/8 killed 無 equivalent 註記仍 pass(E9)" 1 "E9" \
  "$FIX/bad-mutation-survivor.md"
run_case "mutation 有 ERROR 仍 pass(E9)" 1 "E9" "$FIX/bad-mutation-error.md"

echo "== 十二/SKILL.negative constraints:必須映射,skipped 不得 pass =="
run_case "缺 Negative Constraint Mapping 節(E10)" 1 "E10" \
  "$FIX/bad-no-negative-section.md"
run_case "constraint 標 skipped 卻 pass(E10)" 1 "E10" \
  "$FIX/bad-negative-skipped-pass.md"

echo "== 十二.dependency diff:supply chain 層 pass 也要有實跑證據 =="
# 依 E4 通則:Supply chain pass 而 Result 空 → 沒跑寫 PASS
run_case "supply chain pass 無結果(E4)" 1 "E4" "$FIX/bad-supplychain-empty.md"

echo "== 十五.Stage 7 不因 Gauntlet PASS 跳過雙軸審查 =="
run_case "review 檔 evidence 全 pass 但缺 Spec Axis(E11)" 1 "E11" \
  "$FIX/bad-review-missing-axis.md" --review-file
run_case "review 檔雙軸+現象證據俱在則過" 0 "-" \
  "$FIX/good-review.md" --review-file --source-sha abc1234def5678

echo "== 六.stale artifact 清除:舊 report 必先刪、新 report 綁本次 run =="
checks=$((checks + 1))
report="$TMP/gauntlet-report.md"
printf 'STALE_SENTINEL_FROM_PREVIOUS_RUN\n' > "$report"
"$TOOL" "$FIX/good-evidence.md" --source-sha abc1234def5678 --report "$report" >/dev/null 2>&1
if grep -q "STALE_SENTINEL_FROM_PREVIOUS_RUN" "$report" 2>/dev/null; then
  fail "stale report 未被清除,舊結果可混入本次 run"
elif ! grep -q "run-id:" "$report" 2>/dev/null; then
  fail "新 report 缺 run-id(無法與本次 fresh run 綁定)"
elif ! grep -q "abc1234def5678" "$report" 2>/dev/null; then
  fail "新 report 未綁 source SHA"
elif ! grep -q "tool-version:" "$report" 2>/dev/null; then
  fail "新 report 缺 tool-version(rerun 無法對齊工具版本)"
else
  echo "  ✅ stale report 清除 + 新 report 綁 run-id/SHA/tool-version"
fi

echo "== M3.malformed 表列 fail-closed(欄數≠預期 = error,禁靜默丟列)=="
run_case "fail 列 Result 含多餘 | 整列欄數跑掉 → E13 error 非零退出" 1 "E13" \
  "$FIX/bad-malformed-row.md"

echo "== m1.SHA 綁定最短長度(<7 字元拒絕比對)=="
run_case "宣告 SHA 僅 1 字元 → 拒絕比對(E2)" 1 "E2" \
  "$FIX/bad-short-sha.md" --source-sha f92c1d5aaaa
run_case "宣告 SHA 過短即便無 --source-sha 也擋(E2)" 1 "E2" "$FIX/bad-short-sha.md"
run_case "--source-sha 值 <7 字元 → 拒絕比對(E2)" 1 "E2" \
  "$FIX/good-evidence.md" --source-sha abc12

echo "== 版本聲明(--version 與 devflow-contract.json schema_versions.gauntlet 一致)=="
contract_version=$(python3 -c "import json; print(json.load(open('$ROOT/devflow-contract.json'))['schema_versions']['gauntlet'])")
run_case "--version 輸出 contract 宣告版本($contract_version)+ exit 0" 0 \
  "$contract_version" --version

echo "== 小項②.flag 缺值 = 用法錯誤 exit 2 =="
run_case "--source-sha 缺值 → usage + exit 2" 2 "usage" \
  "$FIX/good-evidence.md" --source-sha

echo "== M2.文檔化命令必須機械強制 E7(模板 2c 與 example 示範命令)=="
checks=$((checks + 1))
if grep -q -- "--require-layer" "$ROOT/_templates/7-review.md"; then
  echo "  ✅ 模板 2c 文檔化命令含 --require-layer(E7 機械強制)"
else
  fail "模板 2c 文檔化命令未帶 --require-layer(Profile 必跑層標 unverified 仍 exit 0 = E7 死路)"
fi
checks=$((checks + 1))
if grep -q -- "--require-layer" "$ROOT/example/contract-expiry-reminder/7-review.md"; then
  echo "  ✅ example 示範命令含 --require-layer(與模板 2c 同步)"
else
  fail "example 示範命令未帶 --require-layer(與模板 2c 不同步)"
fi
# 文檔化命令實跑:example 7-review 經該命令(含 required 層)必須綠
run_case "example 7-review 經文檔化命令(--review-file + required 層)綠" 0 "-" \
  "$ROOT/example/contract-expiry-reminder/7-review.md" --review-file \
  --source-sha f92c1d5 \
  --require-layer "Full test suite" \
  --require-layer "Changed-line coverage" \
  --require-layer "Real execution"
# 硬要求案例:required 層在 evidence 裡標 unverified → 文檔化命令必 fail
run_case "required 層標 unverified(example Mutation)→ 文檔化命令 fail(E7)" 1 "E7" \
  "$ROOT/example/contract-expiry-reminder/7-review.md" --review-file \
  --source-sha f92c1d5 --require-layer "Mutation"

echo
if [ "$failures" -gt 0 ]; then
  echo "❌ evidence gauntlet tests: $((checks - failures))/$checks passed"
  exit 1
fi
echo "✅ evidence gauntlet tests: $checks/$checks passed"
