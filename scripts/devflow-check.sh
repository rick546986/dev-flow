#!/bin/bash
# Repo-local check aggregator for the dev-flow methodology master repo.
#
# 這是**聚合器**,不是 Runtime,也不取代外部 plugin。它只做四件事:
#   ①固定順序輸出 ②組內 fail-fast ③清楚列出哪一組失敗 ④最後輸出摘要。
# 它不重寫、不複製任何既有檢查的邏輯 —— 每一項都是直接呼叫既有腳本。
# `all` 模式四大組**平行執行**(2026-08-17 效能輪;各組輸出捕捉後按固定順序重放,
# 不交錯),組間不再 fail-fast —— 失敗時其他組照跑,沒有檢查被少跑;
# 要回序列版:DEVFLOW_CHECK_SEQUENTIAL=1。
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
#   scripts/devflow-check.sh contracts     # 機器可讀契約(並行/vnext/gauntlet/observability/memory)
#   scripts/devflow-check.sh architecture  # 架構與完整性守衛(design contract/ADR/版本/切片)
#   scripts/devflow-check.sh render        # 衍生檔固定點 + 空白字元衛生

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT" || exit 1

# devflow:tmpdir-normalize:start
# 派工單 §2.1:Git Bash 的 /tmp 與 Windows 原生 Python 解讀的 /tmp 不是同一個資料夾。
# 前者是 C:\Users\<user>\AppData\Local\Temp;後者把開頭的 / 當成「現行磁碟機根目錄
# 底下的路徑」→ C:\tmp。而 C:\tmp 在多數機器上真的存在,所以 os.path.exists('/tmp')
# 回 True —— 不會噴「找不到目錄」這種好認的錯,只會安靜地在空目錄裡找不到樣本,
# 失敗訊息看起來五花八門(期望 0 得 1、期望 2 得 0),根其實是同一個。
# cygpath -m 產出的 C:/Users/... 兩邊都認得(正斜線 + 磁碟機代號),與 issue #5 的
# --print-root 同一招。底下所有 mktemp 都吃 ${TMPDIR:-/tmp},所以在此正規化一次
# 即全涵蓋,不必動每一個落點。無 cygpath 的環境不進這個分支,行為零變化。
# ⚠️ 本區塊在 hooks/selftest.sh 與 scripts/devflow-check.sh 各有一份**逐字**副本
#    (兩支都是可獨立執行的入口,誰先跑都要正規化)。兩份必須完全一致,由
#    test-architecture-guards.sh 的 tmpdir-normalize 對帳釘住 —— 改一邊必改兩邊。
if command -v cygpath >/dev/null 2>&1; then
  TMPDIR=$(cygpath -m "${TMPDIR:-/tmp}") && export TMPDIR
fi
# devflow:tmpdir-normalize:end

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
CONTINUED_AFTER_RED=""

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
  # G3 回歸(2026-08-17 採用現場):全形冒號版 fixture 必須同樣通過 —— C1 的冒號
  # 字元集曾把「:或：」打成兩個半形,全形觀測欄被判缺欄、全形例外欄被判沒寫。
  run "methodology/check-spec-gate (全形冒號回歸)" \
      scripts/check-spec-gate.sh scripts/fixtures/spec-gate-fullwidth-colon/4-spec.md || return 1
  # G3 通解:掃 scripts/ hooks/ 正則字元集內「相鄰重複半形標點」(本想寫全形的
  # 機械徵象)。單修已知 6 處只是治標,沒有這支,下次再寫一個 [::] 又會重演。
  run "methodology/check-regex-charclass" scripts/check-regex-charclass.sh || return 1
  # B-1/G2 通解:母版自己的 dev-talk 產物逐檔餵真的 devtalk-guard,必須全過 ——
  # 「母版產物過不了母版守衛」已發作兩次,寫入時才發現太晚,這裡每次先驗。
  run "methodology/check-devtalk-selfclean" scripts/check-devtalk-selfclean.sh || return 1
  # 自判表對稱性(2026-08-19):四份自判表的「依據」欄、代價欄與上下兩層分流必須齊,
  # 並帶一支負向 fixture 釘住 C5 的掃描範圍(DD 子節內的殘留待裁決要抓得到)。
  run "methodology/check-selfjudgment-tables" scripts/check-selfjudgment-tables.sh || return 1
  # 第 7 型「不對稱記帳」:guide-dev-talk.html 是 skills/dev-talk/SKILL.md 的鏡像導覽,
  # 機制(SKILL.md)改了、鏡像沒跟上會靜默漂移(曾發生漏列一整步、逐字引用錯引正本)。
  run "methodology/check-devtalk-guide-sync" scripts/check-devtalk-guide-sync.sh || return 1
  # Stage 1:節點鏈可單獨當入口、重跑 N9 不得另存、沒游標檔 --action 仍擋、重跑不得重開 session。
  run "methodology/check-devtalk-graph"       scripts/check-devtalk-graph.sh     || return 1
  run "methodology/test-devtalk-graph"        scripts/test-devtalk-graph.sh      || return 1
  # 方法流程圖對 hop:guide 全程地圖必須對上 graph.yaml next 鏈;掃頁樣張六件齊。
  # 不拆不放寬 check-devtalk-graph / check-devtalk-guide-sync / check-guides-fig-sync。
  run "methodology/check-devtalk-fig-graph"   scripts/check-devtalk-fig-graph.sh || return 1
  # feature 現況圖對 Journey／Actors:改誰／工具不改圖必須紅。這顆牙不管 skill hop,
  # 不取代 check-devtalk-fig-graph.sh。
  run "methodology/check-devtalk-fig-journey" scripts/check-devtalk-fig-journey.sh || return 1
  # 2／3／4／5／7 站圖對文字:選定標／variant／SHALL 行為詞／Blocked-by／Diff
  # 改了、該站圖沒改必須紅。第 6 站無必產圖槽、本輪不開。不取代 hop／Journey 牙。
  run "methodology/check-devstage-fig-text"  scripts/check-devstage-fig-text.sh  || return 1
  # 直式置中方塊圖母版:腳本壞了或吐 mermaid／pre／沒 viewBox／沒置中字必須紅。
  # 不塞 hop graph,不取代 fig-text／Journey／guides-fig-sync,不改 --action。
  run "methodology/check-vbox-fig"           scripts/check-vbox-fig.sh         || return 1
  # Stage 2:九真節點;單產物 2-decision.md;N1 不得寫檔;每個 hop --write-cursor。
  run "methodology/check-devstage2-graph"     scripts/check-devstage2-graph.sh   || return 1
  run "methodology/test-devstage2-graph"      scripts/test-devstage2-graph.sh    || return 1
  # Stage 3:觸發判定 + 跳過 hop;單產物 3-prototype.md;N1／N-skip 不得寫檔。
  run "methodology/check-devstage3-graph"     scripts/check-devstage3-graph.sh   || return 1
  run "methodology/test-devstage3-graph"      scripts/test-devstage3-graph.sh    || return 1
  # Stage 4:四真節點 + 兩暫留 hop;單產物 4-spec.md;只有 N5 可寫;G2 前不寫 5-tasks。
  run "methodology/check-devstage4-graph"     scripts/check-devstage4-graph.sh   || return 1
  run "methodology/test-devstage4-graph"      scripts/test-devstage4-graph.sh    || return 1
  # Stage 5:四真節點 + 兩暫留 hop;單產物 5-tasks.md;只有 N4 可寫;未定案不寫 6-notes。
  run "methodology/check-devstage5-graph"     scripts/check-devstage5-graph.sh   || return 1
  run "methodology/test-devstage5-graph"      scripts/test-devstage5-graph.sh    || return 1
  # Stage 6:四真節點 + 一暫留 hop;單產物 6-implementation-notes.md;只有 N1-arm 可寫;沒武裝不寫 6-notes。
  run "methodology/check-devstage6-graph"     scripts/check-devstage6-graph.sh   || return 1
  run "methodology/test-devstage6-graph"      scripts/test-devstage6-graph.sh    || return 1
  # Stage 7:五真節點 + 一暫留 hop;單產物 7-review.md;只有 N4-author 可寫;N4 才准讀 6-notes。
  run "methodology/check-devstage7-graph"     scripts/check-devstage7-graph.sh   || return 1
  run "methodology/test-devstage7-graph"      scripts/test-devstage7-graph.sh    || return 1
  # 主機轉接:DEVFLOW_ROOT + 三邊發現 + 採用專案掛整棵 + 主機探測/--action/--probe。
  # 不重寫 1–7 站編成,不准為了別的主機改鬆 --action。
  run "methodology/check-host-adapter"        scripts/check-host-adapter.sh      || return 1
  run "methodology/test-host-adapter"         scripts/test-host-adapter.sh       || return 1
}

group_contracts() {
  run "contracts/check-parallel-stage6"   scripts/check-parallel-stage6.sh   || return 1
  run "contracts/check-vnext-integration" scripts/check-vnext-integration.sh || return 1
  run "contracts/test-evidence-gauntlet"  scripts/test-evidence-gauntlet.sh  || return 1
  run "contracts/observability"           observability/run-tests.sh         || return 1
  # Agent Memory 的可執行契約:identity/durable 格式、LVP 失效、retrieval 相關性、
  # dev-talk 生命週期、legacy 遷移、評測 harness —— 全部在 mktemp 的假 repo 與
  # 暫存記憶家目錄裡跑,不碰使用者真實的 ~/.agentmem/ 與本 repo 的 .dev-flow/。
  run "contracts/memory"                 memory/run-tests.sh                || return 1
}

group_architecture() {
  # 2030-P1:parity 必須在 py-floor 之前。本機缺 3.9–3.11 時 check-py-floor
  # exit 2 —— 1930 散發副本漂移就是這樣本機看不見的。
  # 2130-P1:直譯器缺席(exit 2)該項記紅、組內繼續;語法超下限(exit 1)仍
  # fail-fast。不把 py-floor 改 WARN(門檻不降)。
  run "architecture/check-integration-regression-guard" scripts/check-integration-regression-guard.sh || return 1
  # 最低 Python 版本相容(2026-08-19 採用現場踩到):會在採用專案直譯器上跑的 .py
  # 不得用到比宣告下限更新的語法。build-gate-twin.py 曾在 f-string 表達式寫反斜線,
  # 3.11 及更早直接 SyntaxError,而 v3.8.0 全部既有檢查皆綠 —— 這支就是那個缺的檢查。
  echo "── architecture/check-py-floor ─────────────────────────────────────────"
  scripts/check-py-floor.sh
  floor_rc=$?
  if [ "$floor_rc" -eq 0 ]; then
    PASSED+=("architecture/check-py-floor")
  elif [ "$floor_rc" -eq 2 ]; then
    FAILED="architecture/check-py-floor (exit $floor_rc)"
    echo "   ❌ architecture/check-py-floor 直譯器缺席(exit 2):該項記紅,組內繼續。"
    CONTINUED_AFTER_RED=1
  elif [ "$floor_rc" -eq 1 ]; then
    FAILED="architecture/check-py-floor (exit $floor_rc)"
    return 1
  else
    FAILED="architecture/check-py-floor (exit $floor_rc)"
    return 1
  fi
  run "architecture/check-gate-tokens"     scripts/check-gate-tokens.sh     || return 1
  run "architecture/check-design-contract" scripts/check-design-contract.sh || return 1
  run "architecture/check-adr-integrity"   scripts/check-adr-integrity.sh   || return 1
  # 過期外掛路徑守衛:dev-talk 已併入 dev-flow 單一 plugin,散發路徑改為 cache 形式,
  # 活文件不得殘留舊版 local marketplace 路徑或開發者個人絕對路徑(見腳本頂註)。
  run "architecture/check-no-stale-paths"  scripts/check-no-stale-paths.sh  || return 1
  # 改版歷史索引:append-only 沒有天然保證,插到中間或手改看起來一樣正常 → 機械驗形狀
  run "architecture/check-history-integrity" scripts/check-history-integrity.sh || return 1
  # adr / HISTORY 人頁:md 是正本,html 過期就紅。新增 ADR 跑
  # scripts/build-public-docs.py,不要手改 html。
  run "architecture/check-public-docs" scripts/check-public-docs.sh || return 1
  # gate twin 是審查介面不是文件視覺版(README §6):三件必含 + 預設只寫本機完整文件,對四站實跑
  run "architecture/check-gate-twin"         scripts/check-gate-twin.sh         || return 1
  # 模型分層是散文紀律(prompt 級),沒照做不會現形——事後從 ledger 的 attempt 事件流
  # 稽核有沒有首派即最高階、或跳過中間層直接升階(worker 這條線,見腳本頂註的稽核邊界)
  run "architecture/check-model-tiering"   scripts/check-model-tiering.sh   || return 1
  run "architecture/check-version-sync"    scripts/check-version-sync.sh    || return 1
  # hooks 記帳對帳(F1/第 7 型):hooks.json 掛載 vs 三份列舉文件(dev-setup 健檢
  # 清單/README/guide 註冊表),數量與名稱都比 —— 曾發生掛載長到 6 條而健檢清單
  # 靜默停在 5 條,採用專案照清單健檢會把真 hook 判成多餘。
  run "architecture/check-hooks-accounting" scripts/check-hooks-accounting.sh || return 1
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
  # 新增/改名/刪除 hooks|scripts|observability|memory|tests/parallel-stage6 底下的 *.sh/*.py 沒同步
  # 更新那張表就紅;表裡寫了不存在的檔名也紅。
  run "architecture/check-file-map" scripts/check-file-map.sh || return 1
  # STATUS 規則對帳(S-1):模板/母版自用兩份要點、Active 表頭 Branch 欄、
  # quickstart 手寫範例列(renderer 不同步那段,只有這支在看)。
  run "architecture/check-status-policy" scripts/check-status-policy.sh || return 1
  # 兩份導覽各自嵌一張完整的生命週期圖(fig-lifecycle / fig-lifecycle-qs)是 owner
  # 明確裁決的雙副本(quickstart 要能自足,不接受單正本+連結取代;見腳本頂註與
  # notes/dispatch-guard-symmetry.md X-6)——雙副本天生會漂移,補這支同步守衛。
  run "architecture/check-guides-fig-sync" scripts/check-guides-fig-sync.sh || return 1
  # Agent Memory 架構不變量(§16):目錄進不進 Git、durable↔local 相依單向、
  # domain 失效隔離、權威排序不對稱、唯一 setup 入口、線索詞兩份、契約與常數同值、
  # 評測覆蓋面。八條全是「壞掉之後既有檢查照樣全綠」的型別,負向回歸在
  # test-architecture-guards.sh 的 MEM 組。
  run "architecture/check-memory-architecture" scripts/check-memory-architecture.sh || return 1
  # 2130-P1:py-floor 缺席時後面的 run 都過了,不能讓函式以 0 結束把缺席當綠。
  [ -z "$FAILED" ] || return 1
}

group_render() {
  run "render/renderer-fixed-point" scripts/render-methodology-corrections.sh --check || return 1
  run "render/git-diff-whitespace"  git diff --check                                  || return 1
}

# 註冊自審(第 7 型通解;2026-08-17 盤點抓到的洞):scripts/check-*.sh 與
# scripts/test-*.sh 每一支都必須出現在本檔的 run 行裡 —— 新增檢查腳本卻忘了註冊,
# 唯一的下場是「永遠沒被跑」而沒有任何紅字;check-file-map 只保證寫進檔案地圖,
# 不保證被執行。本檔自己列舉自己要跑什麼,所以對帳守衛就放本檔開頭,每種 MODE 都先跑。
# ⚠️ 審查 HIGH 教訓:第一版 grep 全檔,把腳本名寫在**註解**裡就能騙過(名字在、
# run 沒跑)。現版先剝掉註解行再比對 —— 名字必須出現在會被執行的行上。
# ⚠️ CI 教訓(2026-08-17,v3.7.0 上線即紅):不得用「grep -v | grep -q」管線比對 ——
# 本檔 set -o pipefail,grep -q 找到就提早關管線,前段 grep 吃 SIGPIPE 回 141,
# pipefail 把整條判失敗 = 名字越早出現越容易被誤判「沒註冊」;macOS 緩衝大不發作,
# Linux CI 四組同炸。改為:註解剝除一次存變數,用 bash 內建字串包含比對,零管線。
REG_SOURCE=$(grep -v '^[[:space:]]*#' "$0")
REG_MISS=""
for f in "$ROOT"/scripts/check-*.sh "$ROOT"/scripts/test-*.sh; do
  base=$(basename "$f")
  case "$REG_SOURCE" in
    *"scripts/$base"*) ;;
    *) REG_MISS="$REG_MISS $base" ;;
  esac
done
if [ -n "$REG_MISS" ]; then
  echo "⛔ devflow-check 註冊自審:下列檢查腳本存在但沒被本檔任何 group 執行 ——$REG_MISS" >&2
  echo "   新增檢查必須同 commit 註冊進對應 group,否則它永遠不會跑(且不會有紅字)。" >&2
  exit 1
fi

echo "=== devflow-check: $MODE (REPO_REFERENCE only;外部 plugin 檢查不在此) ==="
echo

run_all_parallel() {
  # 效能輪(2026-08-17):四組互不相依(全部唯讀掃 repo,寫入只進各自 mktemp),
  # `all` 改為平行跑 —— 每組以子行程跑「本腳本 <組名>」,輸出各自捕捉,結束後
  # 按固定順序**原樣重放**(錯誤輸出仍完整、不交錯、不被摘要覆蓋)。
  # 語意變化(誠實宣告):組間 fail-fast 改為「組內 fail-fast 不變、組間全跑」——
  # 沒有任何檢查被少跑或放寬,失敗時反而跑得更多(其他組不因先失敗而略過)。
  # 要回序列版(除錯用):DEVFLOW_CHECK_SEQUENTIAL=1。
  # 防「少跑一組」:四組輸出檔逐一驗存在,缺任何一組 = 平行機制自己壞了,exit 2。
  local tmp; tmp=$(mktemp -d "${TMPDIR:-/tmp}/devflow-check-par.XXXXXX")
  local groups=(methodology contracts architecture render)
  local g pid rc overall=0
  declare -a pids=()
  for g in "${groups[@]}"; do
    bash "$0" "$g" > "$tmp/$g.out" 2>&1 &
    pids+=($!)
  done
  local i=0
  declare -a rcs=()
  for g in "${groups[@]}"; do
    wait "${pids[$i]}"; rcs[$i]=$?
    i=$((i + 1))
  done
  i=0
  for g in "${groups[@]}"; do
    if [ ! -f "$tmp/$g.out" ]; then
      echo "⛔ devflow-check(all/parallel):$g 組的輸出檔不存在 —— 平行機制故障,不是該組全過" >&2
      rm -rf "$tmp"; exit 2
    fi
    cat "$tmp/$g.out"
    echo
    rc=${rcs[$i]}
    if [ "$rc" -ne 0 ]; then
      overall=1
      FAILED="${FAILED:+$FAILED; }$g (exit $rc)"
    else
      PASSED+=("group:$g")
    fi
    i=$((i + 1))
  done
  rm -rf "$tmp"
  return "$overall"
}

case "$MODE" in
  methodology)  group_methodology ;;
  contracts)    group_contracts ;;
  architecture) group_architecture ;;
  render)       group_render ;;
  all)
    if [ "${DEVFLOW_CHECK_SEQUENTIAL:-0}" = "1" ]; then
      group_methodology && group_contracts && group_architecture && group_render
    else
      run_all_parallel
    fi ;;
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
  if [ -n "$CONTINUED_AFTER_RED" ] && [ "$FAILED" = "architecture/check-py-floor (exit 2)" ]; then
    echo "   組內有項記紅(直譯器缺席),後續檢查已繼續跑完。原始錯誤輸出在上方。"
  elif [ -n "$CONTINUED_AFTER_RED" ]; then
    echo "   直譯器缺席已記紅並繼續;之後在「${FAILED}」fail-fast。原始錯誤輸出在上方。"
  elif [ "$MODE" = "all" ] && [ "${DEVFLOW_CHECK_SEQUENTIAL:-0}" != "1" ]; then
    echo "   組內 fail-fast:失敗組內的後續檢查未執行;其他組已全數跑完(輸出在上方)。"
  else
    echo "   fail-fast:該組之後的檢查未執行。原始錯誤輸出在上方,未被摘要覆蓋。"
  fi
  exit 1
fi

echo
echo "✅ devflow-check($MODE): REPO_REFERENCE_PASS(${#PASSED[@]} 組全過)"
echo "   注意:REPO_REFERENCE_PASS ≠ EXTERNAL_RUNTIME_PASS。外部 plugin 的"
echo "   gate-consistency.sh / selftest.sh / devflow-doctor.sh 仍須在本機或已安裝"
echo "   plugin 的環境自行執行,本檔不執行也不代表它們。"
exit 0
