#!/bin/bash
# Repo-local check aggregator for the dev-flow methodology master repo.
#
# 這是**聚合器**,不是 Runtime,也不取代外部 plugin。它只做四件事:
#   ①固定順序 ②fail-fast ③清楚列出哪一組失敗 ④最後輸出摘要。
# 它不重寫、不複製任何既有檢查的邏輯 —— 每一項都是直接呼叫既有腳本。
#
# 邊界宣告(誠實分界,勿混用):
#   REPO_REFERENCE_PASS  = 本檔跑得完的東西。只驗本 repo 的模板/範例/fixture/契約檔。
#   EXTERNAL_RUNTIME_PASS = 已安裝 plugin runtime(${CLAUDE_PLUGIN_ROOT},散發時實際
#                           路徑為 ~/.claude/plugins/cache/dev-flow/dev-flow/<version>/)的
#                           gate-consistency.sh / selftest.sh / devflow-doctor.sh。
#   本檔**不執行也不冒充**外部 plugin 檢查;兩者用 devflow-contract.json 對版握手,
#   不共用實作。本檔全綠 ≠ 外部 Runtime pass。
#
# 用法:
#   scripts/devflow-check.sh all           # 全部(預設)
#   scripts/devflow-check.sh methodology   # 方法論一致性(README/模板/範例/guide twin)
#   scripts/devflow-check.sh contracts     # 機器可讀契約(並行/vnext/gauntlet/observability)
#   scripts/devflow-check.sh architecture  # 架構與完整性守衛(design contract/ADR/版本/切片)
#   scripts/devflow-check.sh render        # 衍生檔固定點 + 空白字元衛生

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT" || exit 1

MODE=${1:-all}
case "$MODE" in
  all|methodology|contracts|architecture|render) ;;
  -h|--help|help)
    sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'
    exit 0 ;;
  *)
    echo "usage: $0 [all|methodology|contracts|architecture|render]" >&2
    exit 2 ;;
esac

PASSED=()
FAILED=""

# run <label> <cmd...>
# 直接把子命令的 stdout/stderr 原樣放行(不吞、不改寫、不摘要),再記錄 exit code。
run() {
  local label="$1"; shift
  echo "── $label ─────────────────────────────────────────"
  "$@"
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    FAILED="$label (exit $rc)"
    return 1
  fi
  PASSED+=("$label")
  return 0
}

group_methodology() {
  run "methodology/check-methodology-corrections" scripts/check-methodology-corrections.sh || return 1
  run "methodology/check-realworld"               scripts/check-realworld.sh               || return 1
  # MED-4(第二批獨立審查):README master-only 標記必須數量相等、逐一配對(不得巢狀/
  # 交錯)—— 不對稱時 skills/dev-setup/SKILL.md 的 sed 抽取會靜默跑錯範圍,沒有任何
  # 報錯,採用專案的 docs/dev/README.md 就此帶著錯誤內容。放這一群(而非
  # check-stage67-enforcement.sh)是因為這是 README/母版一致性的方法論層問題,
  # 與 check-stage67-enforcement.sh 專管的 Stage 6/7 模板執行期強制條款是不同關切。
  run "methodology/check-readme-markers" scripts/check-readme-markers.sh || return 1
  # G2 機械關卡(B-9):對母版自帶的正例跑一次 —— 等於自帶回歸測試,腳本壞了這裡先紅。
  # ⚠️ 這支是 **Gate**(exit 1 = FAIL 擋流程),與 warning-only 的 check-task-slicing 契約相反。
  run "methodology/check-spec-gate" \
      scripts/check-spec-gate.sh example/contract-expiry-reminder/4-spec.md || return 1
}

group_contracts() {
  run "contracts/check-parallel-stage6"   scripts/check-parallel-stage6.sh   || return 1
  run "contracts/check-vnext-integration" scripts/check-vnext-integration.sh || return 1
  run "contracts/test-evidence-gauntlet"  scripts/test-evidence-gauntlet.sh  || return 1
  run "contracts/observability"           observability/run-tests.sh         || return 1
}

group_architecture() {
  run "architecture/check-gate-tokens"     scripts/check-gate-tokens.sh     || return 1
  run "architecture/check-design-contract" scripts/check-design-contract.sh || return 1
  run "architecture/check-adr-integrity"   scripts/check-adr-integrity.sh   || return 1
  # 過期外掛路徑守衛:dev-talk 已併入 dev-flow 單一 plugin,散發路徑改為 cache 形式,
  # 活文件不得殘留舊版 local marketplace 路徑或開發者個人絕對路徑(見腳本頂註)。
  run "architecture/check-no-stale-paths"  scripts/check-no-stale-paths.sh  || return 1
  # 改版歷史索引:append-only 沒有天然保證,插到中間或手改看起來一樣正常 → 機械驗形狀
  run "architecture/check-history-integrity" scripts/check-history-integrity.sh || return 1
  # gate twin 是審查介面不是文件視覺版(README §6):三件必含 + 兩種殼,對三站實跑
  run "architecture/check-gate-twin"         scripts/check-gate-twin.sh         || return 1
  run "architecture/check-version-sync"    scripts/check-version-sync.sh    || return 1
  # dev-setup upgrade 三方比對紀律(B-2):skills/dev-setup/SKILL.md 的三方比對/
  # baseline 快照/逐檔徵同意/過渡態/master-only 剝除/gate twin 相依全是散文規則,
  # 退回等於原地重現「upgrade 靜默蓋掉本地客製」。獨立於下面的 Stage 6/7 執行期
  # 條款(check-stage67-enforcement.sh)——那支管模板,這支管安裝器自己。
  run "architecture/check-dev-setup-discipline" scripts/check-dev-setup-discipline.sh || return 1
  # Stage 6/7 執行期強制條款(A1 守衛武裝／A3 Verify 案例數／A4 gauntlet 路徑／
  # A5 觀測可執行性)。四條都是 2026-08 order-intake 實際失效過的散文規則。
  run "architecture/check-stage67-enforcement" scripts/check-stage67-enforcement.sh || return 1
  # 反水平切層是 warning-only heuristic:它自己絕不 exit 1(見腳本頂註),
  # 因此不會讓本聚合器紅。它印 WARNING 供人判斷,不取代 Reviewer。
  run "architecture/check-task-slicing (warning-only)" scripts/check-task-slicing.sh || return 1
  # 負向回歸:守衛「跑得過」≠「擋得住」。這支把關鍵 mutation 釘成常設測試,
  # 每次 PR 由 CI 重跑;不靠「某次 mutation 結果寫在 PR 說明裡」。
  run "architecture/test-architecture-guards (負向)" scripts/test-architecture-guards.sh || return 1
  # 檔案地圖雙向盤點:guides/guide-dev-flow.html「附錄:檔案地圖」是手寫表,手寫表必腐化——
  # 新增/改名/刪除 hooks|scripts|observability|tests/parallel-stage6 底下的 *.sh/*.py 沒同步
  # 更新那張表就紅;表裡寫了不存在的檔名也紅。
  run "architecture/check-file-map" scripts/check-file-map.sh || return 1
}

group_render() {
  run "render/renderer-fixed-point" scripts/render-methodology-corrections.sh --check || return 1
  run "render/git-diff-whitespace"  git diff --check                                  || return 1
}

echo "=== devflow-check: $MODE (REPO_REFERENCE only;外部 plugin 檢查不在此) ==="
echo

case "$MODE" in
  methodology)  group_methodology ;;
  contracts)    group_contracts ;;
  architecture) group_architecture ;;
  render)       group_render ;;
  all)          group_methodology && group_contracts && group_architecture && group_render ;;
esac
STATUS=$?

echo
echo "════════════════════════ summary ════════════════════════"
for item in ${PASSED+"${PASSED[@]}"}; do
  echo "  ✅ $item"
done

if [ "$STATUS" -ne 0 ]; then
  echo "  ❌ $FAILED"
  echo
  # ${FAILED} 必須帶大括號:全形「」緊接 $FAILED 時,bash 會把後面的多位元組字元
  # 一起吃進變數名(FAILED」),配上 set -u 就是 unbound variable —— 失敗訊息永遠印不出來。
  echo "⛔ devflow-check($MODE): FAILED at 「${FAILED}」"
  echo "   fail-fast:該組之後的檢查未執行。原始錯誤輸出在上方,未被摘要覆蓋。"
  exit 1
fi

echo
echo "✅ devflow-check($MODE): REPO_REFERENCE_PASS(${#PASSED[@]} 組全過)"
echo "   注意:REPO_REFERENCE_PASS ≠ EXTERNAL_RUNTIME_PASS。外部 plugin 的"
echo "   gate-consistency.sh / selftest.sh / devflow-doctor.sh 仍須在本機或已安裝"
echo "   plugin 的環境自行執行,本檔不執行也不代表它們。"
exit 0
