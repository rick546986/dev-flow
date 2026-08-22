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
# 每個負向 fixture 只缺一節,且 pattern 對到「缺哪一節」的訊息 —— 否則多節同時缺時,
# 任一節的規則被刪掉測試仍會綠(E11 五節各自要能被單獨證偽)。
run_case "review 檔 evidence 全 pass 但缺 Spec Axis(E11)" 1 "缺「## Spec Axis」" \
  "$FIX/bad-review-missing-axis.md" --review-file
# G3 信心 = Gauntlet + Code Review + Walkthrough:雙軸在、Walkthrough 缺一樣不得過
run_case "review 檔雙軸俱在但缺 Operational Walkthrough(E11)" 1 "缺「## Operational Walkthrough」" \
  "$FIX/bad-review-missing-walkthrough.md" --review-file
run_case "review 檔雙軸+Walkthrough 俱在但缺 Coverage Matrix(E11)" 1 "缺「## Coverage Matrix」" \
  "$FIX/bad-review-missing-coverage-matrix.md" --review-file
# 2026-08-15 補(devflow-4cap-remediation-2026-08.md §7 第 2 點):Standards Axis 與
# 現象證據兩節此前無負向 fixture(bf05b59 既有缺口),規則被刪掉測試仍綠。
run_case "review 檔雙軸+Walkthrough+Coverage Matrix 俱在但缺 Standards Axis(E11)" 1 \
  "缺「## Standards Axis」" "$FIX/bad-review-missing-standards-axis.md" --review-file
run_case "review 檔雙軸+Walkthrough+Coverage Matrix 俱在但缺 現象證據(E11)" 1 \
  "缺「## 現象證據」" "$FIX/bad-review-missing-phenomena.md" --review-file
# 1630-P1 起 --profile 不得指向別份 feature;E11 正案改用 sibling 4-spec。
run_case "review 檔雙軸+現象證據+Walkthrough+Coverage Matrix 俱在且 sibling 4-spec 則過" 0 "-" \
  "$FIX/profile-pass/7-review.md" --review-file --source-sha abc1234def5678

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

echo "== B-4.--print-root 印出本副本解析到的 ROOT(供 doctor 探測散發副本 ROOT 解析差異)=="
run_case "--print-root 印出母版 ROOT(repo 根,GAUNTLET_VERSION 不動)" 0 "$ROOT" --print-root

echo "== 小項②.flag 缺值 = 用法錯誤 exit 2 =="
run_case "--source-sha 缺值 → usage + exit 2" 2 "usage" \
  "$FIX/good-evidence.md" --source-sha

echo "== P0-2.Gauntlet 讀 sibling 4-spec Required;漏帶旗標不再 fail-open=="
# 舊實作不讀 4-spec:漏帶 --require-layer 時 Race/stress=unverified 仍 exit 0。
# 新實作以 4-spec 為準,Required 沒有 pass → E7 紅。
run_case "sibling 4-spec Required=Race/stress 標 unverified、漏旗標 → E7 紅" 1 "E7" \
  "$FIX/profile-unverified/7-review.md" --review-file --source-sha abc1234def5678
run_case "sibling 4-spec Required 皆 pass、漏旗標 → 綠" 0 "-" \
  "$FIX/profile-pass/7-review.md" --review-file --source-sha abc1234def5678
# 已列入 Evidence 且非 n-a 的 Conditional 必須 pass(本 fixture 的 Supply chain=unverified)
run_case "已觸發 Conditional(Supply chain unverified)→ E7 紅" 1 "E7" \
  "$FIX/profile-unverified/7-review.md" --review-file --source-sha abc1234def5678
# 旗標只能加嚴:4-spec 沒列 Mutation,人硬加 --require-layer Mutation → 仍紅
run_case "旗標加嚴(Mutation unverified)仍 E7 紅,不能當覆寫拿掉 Required" 1 "E7" \
  "$FIX/profile-unverified/7-review.md" --review-file --source-sha abc1234def5678 \
  --require-layer "Mutation"

echo "== P0-3.--review-file 漏帶 --source-sha 預設當下 HEAD,宣告不符即紅=="
# 舊實作:不帶 --source-sha 只驗宣告存在 → good-review(SHA=abc1234)仍綠。
# 新實作:--review-file 預設 git HEAD,abc1234 ≠ HEAD → E2 stale。
run_case "review-file 不帶 --source-sha 且宣告 SHA ≠ HEAD → E2 紅" 1 "E2" \
  "$FIX/good-review.md" --review-file

echo "== 1230-P0.--review-file 找不到 Profile 不得退回 1.2.0=="
# 舊實作:找不到 sibling 4-spec 也不帶 --profile → 旗標行為退回 1.2.0,
# good-review 漏帶 --require-layer 仍 exit 0 / 27 checks(假綠)。
run_case "review-file 無 sibling 4-spec 也無 --profile → E7 紅" 1 "E7" \
  "$FIX/good-review.md" --review-file --source-sha abc1234def5678
# 1630-P1:無 sibling 時 --profile 指向別份不得再當逃生口(舊 1.3.1 綠)。
run_case "review-file 無 sibling、--profile 指向別份 4-spec → E7 紅" 1 "E7" \
  "$FIX/good-review.md" --review-file --source-sha abc1234def5678 \
  --profile "$FIX/profile-pass/4-spec.md"
# 檔在但沒有 Verification Profile 節 = 一樣找不到 Profile
mkdir -p "$TMP/no-section"
cp "$FIX/good-review.md" "$TMP/no-section/7-review.md"
printf '# fixture:有 4-spec 檔但沒有 Verification Profile 節\n\n## ADDED Requirements\n- none\n' \
  > "$TMP/no-section/4-spec.md"
run_case "review-file sibling 4-spec 無 Verification Profile 節 → E7 紅" 1 "E7" \
  "$TMP/no-section/7-review.md" --review-file --source-sha abc1234def5678
# 顯式 --profile 指向自己的 sibling 仍綠
run_case "review-file --profile 指向自己的 sibling 4-spec 仍綠" 0 "-" \
  "$FIX/profile-pass/7-review.md" --review-file --source-sha abc1234def5678 \
  --profile "$FIX/profile-pass/4-spec.md"

echo "== 1230-P1.docs/dev/<feature>/7-review.md 顯式 SHA 也必須 = HEAD=="
# 舊實作:顯式 --source-sha 只比對該值。live feature 宣告=abc1234、HEAD 已走,
# 仍 exit 0 / 29 checks(假綠)。example/ 與 scripts/fixtures/ 不套這條。
live="$TMP/live-repo"
mkdir -p "$live/docs/dev/live-feature" "$live/example/demo" \
  "$live/scripts/fixtures/evidence-gauntlet/x"
cp "$FIX/profile-pass/7-review.md" "$live/docs/dev/live-feature/7-review.md"
cp "$FIX/profile-pass/4-spec.md" "$live/docs/dev/live-feature/4-spec.md"
cp "$FIX/profile-pass/7-review.md" "$live/example/demo/7-review.md"
cp "$FIX/profile-pass/4-spec.md" "$live/example/demo/4-spec.md"
cp "$FIX/profile-pass/7-review.md" "$live/scripts/fixtures/evidence-gauntlet/x/7-review.md"
cp "$FIX/profile-pass/4-spec.md" "$live/scripts/fixtures/evidence-gauntlet/x/4-spec.md"
git -C "$live" init -q
git -C "$live" add docs example scripts
git -C "$live" -c user.email=t@t -c user.name=t commit -qm seed
live_head=$(git -C "$live" rev-parse HEAD)
run_case "docs/dev/<feature>/7-review 顯式 --source-sha ≠ HEAD → E2 紅" 1 "E2" \
  "$live/docs/dev/live-feature/7-review.md" --review-file --source-sha abc1234def5678
run_case "example/ 顯式 stale SHA 仍綠(不套 live 規則)" 0 "-" \
  "$live/example/demo/7-review.md" --review-file --source-sha abc1234def5678
run_case "scripts/fixtures/ 顯式 stale SHA 仍綠(不套 live 規則)" 0 "-" \
  "$live/scripts/fixtures/evidence-gauntlet/x/7-review.md" --review-file \
  --source-sha abc1234def5678
# 宣告改成當下 HEAD 後,顯式也傳 HEAD → 綠(證明不是一律殺 --source-sha)
python3 - "$live/docs/dev/live-feature/7-review.md" "$live_head" <<'PY'
import sys
path, head = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read().replace("abc1234def5678", head)
open(path, "w", encoding="utf-8").write(text)
PY
run_case "docs/dev/<feature>/7-review 宣告=HEAD 且顯式也傳 HEAD → 綠" 0 "-" \
  "$live/docs/dev/live-feature/7-review.md" --review-file --source-sha "$live_head"

echo "== 1630-P0.Verification Profile 缺 Required layers 欄不得當零層放行=="
# 舊實作:有 ## Verification Profile 但沒有 Required layers 那列 → required=[]
# → E7 不擋,exit 0 / 27 checks(假綠)。缺欄必須紅;明示「無」/none 才是零層。
run_case "review-file sibling Profile 缺 Required layers 欄 → E7 紅" 1 "E7" \
  "$FIX/profile-no-required-row/7-review.md" --review-file --source-sha abc1234def5678
run_case "review-file Required layers:無(明示零層)→ 綠" 0 "-" \
  "$FIX/profile-required-none/7-review.md" --review-file --source-sha abc1234def5678
mkdir -p "$TMP/req-none-en"
cp "$FIX/profile-required-none/7-review.md" "$TMP/req-none-en/7-review.md"
printf '%s\n' \
  '## Verification Profile(G2 一併審)' \
  '- lane: full' \
  '- Risk: normal' \
  '- Required layers:none' \
  '- Explicitly excluded layers:Mutation' \
  '- Final fresh entry point:`pytest -q`' \
  > "$TMP/req-none-en/4-spec.md"
run_case "review-file Required layers:none(明示零層)→ 綠" 0 "-" \
  "$TMP/req-none-en/7-review.md" --review-file --source-sha abc1234def5678

echo "== 1830-P0.Required layers 欄在但值空不得當零層放行=="
# 舊實作:欄在、值空/空白 → required=[]、required_present=True → E7 不擋。
# 1630 只擋缺欄;空值仍當「零層必跑」假綠。只有「無」/none/n-a 是明示零層。
mkdir -p "$TMP/req-blank"
cp "$FIX/profile-pass/7-review.md" "$TMP/req-blank/7-review.md"
printf '%s\n' \
  '## Verification Profile(G2 一併審)' \
  '- lane: full' \
  '- Risk: normal' \
  '- Required layers:' \
  '- Explicitly excluded layers:Mutation' \
  '- Final fresh entry point:`pytest -q`' \
  > "$TMP/req-blank/4-spec.md"
run_case "review-file Required layers 空值 → E7 紅" 1 "E7" \
  "$TMP/req-blank/7-review.md" --review-file --source-sha abc1234def5678
mkdir -p "$TMP/req-ws"
cp "$FIX/profile-pass/7-review.md" "$TMP/req-ws/7-review.md"
printf '%s\n' \
  '## Verification Profile(G2 一併審)' \
  '- lane: full' \
  '- Risk: normal' \
  '- Required layers:   ' \
  '- Explicitly excluded layers:Mutation' \
  '- Final fresh entry point:`pytest -q`' \
  > "$TMP/req-ws/4-spec.md"
run_case "review-file Required layers 只有空白 → E7 紅" 1 "E7" \
  "$TMP/req-ws/7-review.md" --review-file --source-sha abc1234def5678

echo "== 1830-P1.Required 層名必須全等,不得 substring 誤配=="
# 舊實作:wanted.lower() in row[0].lower()。Required unit 被 unit-smoke pass 滿足。
mkdir -p "$TMP/req-substr"
cp "$FIX/profile-pass/7-review.md" "$TMP/req-substr/7-review.md"
python3 - "$TMP/req-substr/7-review.md" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
text = text.replace("| Full test suite |", "| unit-smoke |")
text = text.replace("| Real execution |", "| other-layer |")
open(sys.argv[1], "w", encoding="utf-8").write(text)
PY
printf '%s\n' \
  '## Verification Profile(G2 一併審)' \
  '- lane: full' \
  '- Risk: normal' \
  '- Required layers:unit' \
  '- Explicitly excluded layers:Mutation' \
  '- Final fresh entry point:`pytest -q`' \
  > "$TMP/req-substr/4-spec.md"
run_case "Required unit 被 unit-smoke pass 滿足 → E7 紅" 1 "E7" \
  "$TMP/req-substr/7-review.md" --review-file --source-sha abc1234def5678
mkdir -p "$TMP/req-exact"
cp "$FIX/profile-pass/7-review.md" "$TMP/req-exact/7-review.md"
python3 - "$TMP/req-exact/7-review.md" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
text = text.replace("| Full test suite |", "| unit |")
text = text.replace("| Real execution |", "| other-layer |")
open(sys.argv[1], "w", encoding="utf-8").write(text)
PY
printf '%s\n' \
  '## Verification Profile(G2 一併審)' \
  '- lane: full' \
  '- Risk: normal' \
  '- Required layers:unit' \
  '- Explicitly excluded layers:Mutation' \
  '- Final fresh entry point:`pytest -q`' \
  > "$TMP/req-exact/4-spec.md"
run_case "Required unit 對 evidence unit pass → 綠" 0 "-" \
  "$TMP/req-exact/7-review.md" --review-file --source-sha abc1234def5678
mkdir -p "$TMP/req-paren"
cp "$FIX/profile-pass/7-review.md" "$TMP/req-paren/7-review.md"
python3 - "$TMP/req-paren/7-review.md" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
text = text.replace("| Full test suite |", "| Unit (fast) |")
text = text.replace("| Real execution |", "| other-layer |")
open(sys.argv[1], "w", encoding="utf-8").write(text)
PY
printf '%s\n' \
  '## Verification Profile(G2 一併審)' \
  '- lane: full' \
  '- Risk: normal' \
  '- Required layers:unit' \
  '- Explicitly excluded layers:Mutation' \
  '- Final fresh entry point:`pytest -q`' \
  > "$TMP/req-paren/4-spec.md"
run_case "Required unit 對 evidence Unit (fast) pass → 綠" 0 "-" \
  "$TMP/req-paren/7-review.md" --review-file --source-sha abc1234def5678

echo "== 1630-P1.--review-file 的 --profile 只准本 feature,不得跨份覆寫=="
# 舊實作:profile-unverified 的 sibling 會 E7 紅,但 --profile 指向
# profile-pass(Required 皆 pass)仍 exit 0 / 31 checks(假綠)。
run_case "review-file --profile 指向別份 feature 的 4-spec → E7 紅" 1 "E7" \
  "$FIX/profile-unverified/7-review.md" --review-file --source-sha abc1234def5678 \
  --profile "$FIX/profile-pass/4-spec.md"
# 同一 feature 目錄:7-review 在 docs/dev/<slug>/nested/,4-spec 在 slug 根
mkdir -p "$TMP/same-feat/docs/dev/feat-a/nested"
cp "$FIX/profile-pass/7-review.md" "$TMP/same-feat/docs/dev/feat-a/nested/7-review.md"
cp "$FIX/profile-pass/4-spec.md" "$TMP/same-feat/docs/dev/feat-a/4-spec.md"
run_case "review-file --profile 指向同一 feature 目錄的 4-spec 仍綠" 0 "-" \
  "$TMP/same-feat/docs/dev/feat-a/nested/7-review.md" --review-file \
  --source-sha abc1234def5678 \
  --profile "$TMP/same-feat/docs/dev/feat-a/4-spec.md"

echo "== P0-1.模板節序:整合回歸必須在 Final Fresh 之前=="
# 舊模板:Final Fresh 在執行清單 2c,整合回歸在 Exit Checklist(Verdict 之後)。
# 檢查住 check-stage67-enforcement.sh 的 ST 組;此處釘「頂註執行清單」字面順序。
checks=$((checks + 1))
if python3 - "$ROOT/_templates/7-review.md" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
header = re.split(r"\n##[ \t]", text, 1)[0]
integ = header.find("整合回歸")
fresh = header.find("Final Fresh Run")
if integ < 0:
    print("頂註執行清單沒有整合回歸")
    raise SystemExit(1)
if fresh < 0:
    print("頂註執行清單沒有 Final Fresh Run")
    raise SystemExit(1)
if integ > fresh:
    print(f"舊節序:整合回歸@{integ} 在 Final Fresh@{fresh} 之後")
    raise SystemExit(1)
print("新節序:整合回歸在 Final Fresh 之前")
PY
then
  echo "  ✅ 模板頂註:整合回歸在 Final Fresh 之前"
else
  fail "模板頂註仍是舊節序(Final Fresh → Verdict → Exit 才整合回歸)"
fi
checks=$((checks + 1))
if grep -q "重跑 Final Fresh" "$ROOT/_templates/7-review.md" \
   && grep -q "作廢 G3" "$ROOT/_templates/7-review.md"; then
  echo "  ✅ 模板有 ALREADY_SYNCED 恢復路徑 + Verdict 後改碼作廢 G3"
else
  fail "模板缺 ALREADY_SYNCED 恢復路徑(重跑 Final Fresh)或作廢 G3"
fi

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
# 1.3.1:sibling 4-spec 已列 Required,漏旗標不得再 fail-open,也不得誤紅
run_case "example 7-review 不帶 --require-layer(讀 4-spec Required)仍綠" 0 "-" \
  "$ROOT/example/contract-expiry-reminder/7-review.md" --review-file \
  --source-sha f92c1d5
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
