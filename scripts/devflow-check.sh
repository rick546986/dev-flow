#!/bin/bash
# Repo-local check aggregator for the dev-flow methodology master repo.
#
# 這是**聚合器**,不是 Runtime,也不取代外部 plugin。它只做四件事:
#   ①固定順序 ②fail-fast ③清楚列出哪一組失敗 ④最後輸出摘要。
# 它不重寫、不複製任何既有檢查的邏輯 —— 每一項都是直接呼叫既有腳本。
#
# 邊界宣告(誠實分界,勿混用):
#   REPO_REFERENCE_PASS  = 本檔跑得完的東西。只驗本 repo 的模板/範例/fixture/契約檔。
#   EXTERNAL_RUNTIME_PASS = 外部 plugin(~/.claude/plugins/local/dev-flow/)的
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
  run "architecture/check-version-sync"    scripts/check-version-sync.sh    || return 1
  # 反水平切層是 warning-only heuristic:它自己絕不 exit 1(見腳本頂註),
  # 因此不會讓本聚合器紅。它印 WARNING 供人判斷,不取代 Reviewer。
  run "architecture/check-task-slicing (warning-only)" scripts/check-task-slicing.sh || return 1
  # 負向回歸:守衛「跑得過」≠「擋得住」。這支把關鍵 mutation 釘成常設測試,
  # 每次 PR 由 CI 重跑;不靠「某次 mutation 結果寫在 PR 說明裡」。
  run "architecture/test-architecture-guards (負向)" scripts/test-architecture-guards.sh || return 1
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
