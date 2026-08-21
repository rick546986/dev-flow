#!/bin/bash
# 架構守衛的**負向回歸測試**(常設,進 CI)。
#
# 為什麼存在:守衛「跑得過」不代表「擋得住」。一次性的 mutation 結果寫在 PR 說明裡,
# 下一個人改壞守衛時沒有任何東西會紅。本檔把最關鍵的負向案例釘成 repo 內的常設測試,
# 每次 PR 由 GitHub Actions 重跑。
#
# 涵蓋(每案都是「變異 → 守衛必須失敗」;另有未變異對照組必須通過):
#   Design Contract  DC-0 對照組 / DC-1 Risk high→normal / DC-2 applicable→n-a
#                    DC-3 刪 Data owner 欄 / DC-4 canon 壞例(Forbidden「無」+ 模糊詞)
#                    DC-5 刪 Template Applicability / DC-6 刪 Stage 7 承接
#                    DC-7 finding 全改 n-a / DC-8 只填① / DC-9 finding 留空
#                    DC-X1/X2(2026-08-17 補,F-2 HIGH-3)跨檔恆真斷言掃描的負向覆蓋:
#                    check-realworld.sh 混入單行 check(1 == 1, …)(DC-X1)/ 多行排版
#                    check(\n True, …)(DC-X2),兩者都必須讓 check-design-contract.sh 失敗
#   Gate Token       GT-0 對照組 / GT-1 刪 G2 一個 token / GT-2 G3 token 去粗體
#                    GT-3 刪 G3 錨定義八點中的一點 / GT-4 憑空新增 G4
#                    GT-5a~d 八點極性反轉 / GT-6a 同句 decoy / GT-6b 片語搬到別點
#   Version Sync     VS-0 對照組 / VS-1 README 9.9.9 / VS-2 contract 9.9.9
#                    VS-3 design doc 9.9.9 / VS-4 版本錨被刪 / VS-5 docs/dev/tools
#                    散發副本版本改 9.9.9(2026-08-15 補,第五處同步點)
#   Guard Source     GS-0a/0b 對照組 / GS-1~GS-8 變異**守衛本體**(含 co-edit 守衛+資料)
#   Stale Paths      SP-0 對照組 / SP-1 混入過期 dev-flow 路徑 / SP-2 混入過期 dev-talk
#                    路徑 / SP-3 混入開發者個人絕對路徑 / SP-4 混入 docs/dev/STATUS.md
#                    (2026-08-15 補,第三批獨立審查 P1 —— 該路徑此前完全不在掃描目標
#                    也不在可見豁免清單,塞禁字仍零命中) / SP-5 混入 observability/
#                    (2026-08-15 補,N-5 fail-closed 改版 —— 驗「新目錄不必補清單
#                    就會被掃到」,不是再補一條清單項)(check-no-stale-paths.sh)
#   Real-world       RW-0 對照組 / RW-1 Out of Scope 整段 Stage 3 對帳被刪 / RW-2 一條
#                    場景保留但拿掉逐場點名引用(check-realworld.sh;§7 第 1 點,2026-08-15)
#   TF(2026-08-16 補)  TF-1 模板「測試檔路徑也要列進 Files」紀律句被弱化 / TF-2
#                    範例 T-1 的 Files 欄被拿掉測試檔路徑(check-stage67-enforcement.sh
#                    的 D-39 紀律;對照組沿用既有 S67-0)
#   DSD(2026-08-16 補,B-2) DSD-0 對照組 / DSD-1 過渡態處置句被刪 / DSD-2 三方比對
#                    判別法字面被改寫(check-dev-setup-discipline.sh,dev-setup
#                    upgrade 三方比對紀律)
#   FM(2026-08-16 補,檔案地圖守衛) FM-0 對照組(表與現實同步)/ FM-1 guide 刪一列
#                    (hooks/selftest.sh 那列被拿掉,檔案仍在 → forward 缺列)/ FM-2
#                    guide 加一列指向不存在的檔(reverse 不存在)(check-file-map.sh)
#   FG(2026-08-17 補,X-6 兩份導覽生命週期圖同步守衛) FG-0 對照組(兩張圖正規化後
#                    一致)/ FG-1 quickstart 版 svg 內一個 node 文字被改,dev-flow
#                    版未動 / FG-2 quickstart 版畫圖 CSS 規則被改(svg 標記不動,
#                    只有渲染規則漂移)/ FG-3(X-7 第三層)quickstart 版頁內錨點
#                    捲動 JS 的 scrollIntoView 選項被單邊改掉 / FG-4(驗證 X-6 HIGH
#                    深度感知抽取修復)對稱插入巢狀假 svg 後單邊改真實節點文字,
#                    5cabf4e 版此毒是逃逸的假 PASS / FG-5(2026-08-17 補,二次複審
#                    誘餌攻擊)三份 guides 的頁內錨點捲動 JS marker 後都插同一段
#                    誘餌 <script>(逐位元組相同),真正的 JS 被推到誘餌後面再單邊
#                    改,d1dd5b3 版此毒是逃逸的假 PASS(check-guides-fig-sync.sh)
#   MT(2026-08-17 補,X-5a 模型分層守衛零外部變異涵蓋) MT-0 對照組 ——
#                    對守衛複本的 scripts/fixtures/model-tiering/ 跑**自測模式**
#                    (不帶 CLI 參數),expect pass / MT-1 負向 —— 把 bad-first-top
#                    的 run 目錄當「真實 runs 根」以 CLI 參數餵給守衛複本的**正常模式**,
#                    expect fail;此案專咬「若守衛被挖空成永遠印全過,外部呼叫路徑
#                    (CLI 參數 real 模式)是否也一起失守」——之前只驗過 fixture 自測,
#                    real 模式的紅路徑完全零外部變異覆蓋(check-model-tiering.sh)
#   靜態互釘(2026-08-16 補,獨立審查 finding 4;2026-08-17 二次複審後補到七支;
#                    v3.8.0 落地輪 B-4 補到九支)
#                    九支散落地板/群組數的字面值互釘 —— hooks/selftest.sh
#                    MIN_CASES / tests/parallel-stage6/run_tests.py EXPECTED_CHECKS /
#                    check-dev-setup-discipline.sh、check-integration-regression-
#                    guard.sh、check-status-policy.sh 與 check-gate-twin.sh 的
#                    MIN_CHECKS / check-file-map.sh 的 MIN_CHECKS / check-gate-twin.sh
#                    的 EXPECTED_GROUPS(含 24 個群組名逐字整行釘)/
#                    check-design-contract.sh 的 EXPECTED_CHECK_SKIP_CALLS。另有
#                    B-4 的三支守衛「地板 block」AST 外釘(check_floor_block:
#                    condition+記錄 failure+非零退出必須同鏈,防「常數還在、if 整段
#                    被刪」與「condition 保留、body 換 pass」兩型假綠)。**非**
#                    seed→mutate→expect_local 的變異案例,不計入
#                    EXPECTED_CONTROLS/NEGATIVES/TOTAL(見結果區塊「GS-9」註解自己的
#                    說明,以及下面這行案例數地板不變的理由)。
#
# 案例數是**斷言**不是裝飾:EXPECTED_CONTROLS / EXPECTED_NEGATIVES / EXPECTED_TOTAL
# 由 expect()/expect_local() 實際累計後比對,刪任何一案(含對照組)都會非零退出。
# 地板/群組數的靜態互釘不是這種案例(不 seed、不 mutate、不呼叫 expect_local),不計入
# 這三個數字 —— 加了它們之後 EXPECTED_CONTROLS/NEGATIVES/TOTAL(見本檔頂部宣告值)
# 不動,是設計如此,不是漏算。
#
# 安全(fail-closed,正式 working tree 全程唯讀):
#   - set -euo pipefail;所有變數非空檢查
#   - 暫存根目錄由 mktemp -d 產生,且必須落在 /tmp 或 /private/tmp 前綴內才動它
#   - 刪除前印出完整 target;拒絕刪除空值、根目錄、或前綴外路徑
#   - 只複製守衛會讀到的**資料檔**;守衛本體仍從正式 repo 執行,以 root 參數指向暫存副本
#   - 結束時比對正式 repo 的檔案指紋,證明未被污染
#
# 用法:scripts/test-architecture-guards.sh        (由 devflow-check.sh architecture 呼叫)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${ROOT:?ROOT is empty}"
[[ -f "$ROOT/README.md" ]] || { echo "ROOT 不像 dev-flow repo:$ROOT" >&2; exit 2; }

# 動手前的正式 repo 指紋(結束比對用)
fingerprint() {
  find "$ROOT/README.md" "$ROOT/devflow-contract.json" "$ROOT/_templates" \
       "$ROOT/example" "$ROOT/notes/design" "$ROOT/scripts" \
       "$ROOT/docs/dev/tools/devflow-evidence-gauntlet.sh" \
       "$ROOT/docs/dev/STATUS.md" "$ROOT/docs/dev/devflow-contract.json" \
       "$ROOT/docs/adr" "$ROOT/observability" \
       "$ROOT/skills/dev-setup/SKILL.md" \
       "$ROOT/guides/guide-dev-flow.html" "$ROOT/hooks" "$ROOT/tests/parallel-stage6" \
       -type f -exec shasum {} + 2>/dev/null | shasum | awk '{print $1}'
}
FP_BEFORE=$(fingerprint)
: "${FP_BEFORE:?fingerprint failed}"

WORK=$(mktemp -d "${TMPDIR:-/tmp}/devflow-guard-regression.XXXXXX")
: "${WORK:?mktemp failed}"
[[ "$WORK" == /tmp/* || "$WORK" == /private/tmp/* || "$WORK" == /var/folders/* ]] || {
  echo "暫存目錄不在允許的前綴內:$WORK" >&2; exit 1; }

safe_rm() {
  local target="${1:-}"
  : "${target:?safe_rm: target is empty}"
  [[ "$target" == /tmp/* || "$target" == /private/tmp/* || "$target" == /var/folders/* ]] || {
    echo "safe_rm 拒絕:目標不在允許前綴內:$target" >&2; exit 1; }
  [[ "$target" != "/" && "$target" != "/tmp" && "$target" != "/private/tmp" ]] || {
    echo "safe_rm 拒絕:不得刪除根或前綴本身:$target" >&2; exit 1; }
  rm -rf -- "$target"
}
cleanup() { safe_rm "$WORK"; }
trap cleanup EXIT

PASS=0
FAIL=0
RESULTS=()
# ── 精確案例數地板(2026-08 final verdict M-2)────────────────────────────────
# 舊版只有 PASS/FAIL 兩個計數,尾聲的「5 對照組」是硬編字串、從不參與比對。
# 實測(fresh reviewer 重現):刪掉整個 GS-8 負向案 → 仍印「30/30 全過(5 對照組…)」、exit 0;
# 只刪 GS-0b 對照組一行 → 仍印「5 對照組」、exit 0。也就是那行摘要是裝飾,不是斷言。
# 改法:由 expect()/expect_local() 依 want 實際累計 control 與 negative,尾聲與釘死值比對。
CONTROL_RUN=0     # 實際跑過的「未變異必須 pass」對照組
NEGATIVE_RUN=0    # 實際跑過的「變異必須 fail」負向案
EXPECTED_CONTROLS=14
EXPECTED_NEGATIVES=111
EXPECTED_TOTAL=125

count_case() { # count_case <pass|fail>
  if [ "$1" = "pass" ]; then CONTROL_RUN=$((CONTROL_RUN + 1)); else NEGATIVE_RUN=$((NEGATIVE_RUN + 1)); fi
}

# seed <name> → 在 $WORK/<name> 建一份「守衛會讀到的資料檔」副本,印出完整路徑
seed() {
  local name="${1:?seed: name is empty}"
  local dst="$WORK/$name"
  [[ "$dst" == "$WORK/"* ]] || { echo "seed: 目標逃逸 $dst" >&2; exit 1; }
  safe_rm "$dst"
  mkdir -p "$dst/_templates" "$dst/example/contract-expiry-reminder" \
           "$dst/notes/design" "$dst/scripts" "$dst/docs/dev/tools" "$dst/docs/adr" \
           "$dst/skills/dev-setup"
  cp "$ROOT/README.md" "$dst/README.md"
  cp "$ROOT/devflow-contract.json" "$dst/devflow-contract.json"
  cp "$ROOT"/_templates/{1-discussion,3-prototype,4-spec,5-tasks,6-implementation-notes,7-review}.md \
     "$dst/_templates/"
  cp "$ROOT"/example/contract-expiry-reminder/{1-discussion,3-prototype,4-spec,5-tasks,6-implementation-notes,7-review}.md \
     "$dst/example/contract-expiry-reminder/"
  cp "$ROOT"/notes/design/{design-boundary-contract,evidence-gauntlet}.md "$dst/notes/design/"
  cp "$ROOT/scripts/devflow-evidence-gauntlet.sh" "$dst/scripts/"
  cp "$ROOT/docs/dev/tools/devflow-evidence-gauntlet.sh" "$dst/docs/dev/tools/"
  # 2026-08-15 補(第三批獨立審查 P1):SP-4 需要 docs/dev/STATUS.md 在 seed 副本內才
  # 咬得到 mutation;docs/dev/devflow-contract.json、docs/adr/ 一併補齊,對齊
  # check-no-stale-paths.sh 新增的掃描目標。
  cp "$ROOT/docs/dev/STATUS.md" "$dst/docs/dev/STATUS.md"
  cp "$ROOT/docs/dev/devflow-contract.json" "$dst/docs/dev/devflow-contract.json"
  cp "$ROOT/docs/adr/0001-merge-plugin-into-methodology-repo.md" "$dst/docs/adr/"
  # B-2(dev-setup 三方比對紀律)需要 skills/dev-setup/SKILL.md 在 seed 副本內才咬得到
  # mutation;check-dev-setup-discipline.sh 讀的正是這份檔。
  cp "$ROOT/skills/dev-setup/SKILL.md" "$dst/skills/dev-setup/SKILL.md"
  # 2026-08-17 補(F-2 MED):check-design-contract.sh 的跨檔恆真斷言掃描新增了掃描
  # 清單哨兵,要求 scripts/check-realworld.sh 與 scripts/check-gate-twin.sh 必須出現在
  # $dst/scripts/ 底下,缺席就 exit 2。這兩支不是 DC-* 案例本來要驗的資料,是掃描的
  # **旁證檔**——所有走 seed() 的 check-design-contract.sh 呼叫(DC-0…DC-9、DC-X1/X2 等)
  # 都會跑到這道哨兵,不補就會讓既有 DC-0 對照組也變 exit 2。
  cp "$ROOT/scripts/check-realworld.sh" "$dst/scripts/"
  cp "$ROOT/scripts/check-gate-twin.sh" "$dst/scripts/"
  echo "$dst"
}

# expect <pass|fail> <guard-script> <root> <label>
expect() {
  local want="${1:?}" guard="${2:?}" target="${3:?}" label="${4:?}"
  [[ "$target" == "$WORK/"* ]] || { echo "expect: root 逃逸 $target" >&2; exit 1; }
  count_case "$want"
  local out rc got
  out=$("$ROOT/scripts/$guard" "$target" 2>&1)
  rc=$?
  got=pass; [ "$rc" -ne 0 ] && got=fail
  if [ "$got" = "$want" ]; then
    RESULTS+=("  ✅ $label — 預期 $want,實得 $got")
    PASS=$((PASS + 1))
  else
    RESULTS+=("  ❌ $label — 預期 $want,實得 $got (exit $rc)")
    RESULTS+=("       $(printf '%s' "$out" | tail -3 | tr '\n' ' ')")
    FAIL=$((FAIL + 1))
  fi
}

# seed_sp <name> → 同 seed(),另外把 $dst 初始化成一個真 git repo,並多複製一份
# observability/ 底下的檔案。
# 起因(2026-08-15,N-5 fail-closed 改版):check-no-stale-paths.sh 的掃描來源從
# 「明確列入 ACTIVE_TARGETS 才掃」改成「git ls-files 全量追蹤檔 − 印出來的
# ALLOWLIST」,目標 root 本身必須是 git working tree,單純複製的檔案樹跑
# `git ls-files` 會直接失敗(exit 2)。多複製 observability/ 一份真檔是為了讓
# SP-5 有一個「先前完全不在任何清單上」的活檔可用來驗 fail-closed 的核心宣稱:
# 新目錄不用列清單就會被掃到。
# 2026-08-17(X-2)補:守衛新增 SENTINELS 斷言(README.md、_templates/4-spec.md 已在
# seed() 的既有複製清單內,不必再補),另外四個哨兵——hooks/devflow-lib.py、
# scripts/build-gate-twin.py、guides/guide-dev-flow.html、.claude-plugin/plugin.json
# ——seed() 沒有複製,不補就會讓 SP-0 對照組在 SENTINELS 檢查就先炸(哨兵缺席,
# 不是掃描來源被縮小,是 fixture 本來就沒帶那幾個檔),所以在這裡補齊。
seed_sp() {
  local name="${1:?seed_sp: name is empty}"
  local dst; dst=$(seed "$name")
  mkdir -p "$dst/observability" "$dst/hooks" "$dst/guides" "$dst/.claude-plugin"
  cp "$ROOT/observability/devflow-obs.py" "$dst/observability/devflow-obs.py"
  cp "$ROOT/hooks/devflow-lib.py" "$dst/hooks/devflow-lib.py"
  cp "$ROOT/scripts/build-gate-twin.py" "$dst/scripts/build-gate-twin.py"
  cp "$ROOT/guides/guide-dev-flow.html" "$dst/guides/guide-dev-flow.html"
  cp "$ROOT/.claude-plugin/plugin.json" "$dst/.claude-plugin/plugin.json"
  git -C "$dst" init -q
  git -C "$dst" -c user.email=test@dev-flow.local -c user.name=test add -A
  git -C "$dst" -c user.email=test@dev-flow.local -c user.name=test commit -q -m seed
  echo "$dst"
}

# seed_guard <name> <guard-script…> → 同 seed(),外加把指名的**守衛本體**複製進
# $WORK/<name>/scripts/。用於「守衛自己被改弱」這一類負向案 —— 這是原本整個缺的一類:
# 舊版本檔只變異資料檔(見檔頭「只複製守衛會讀到的資料檔」),因此
# 「co-edit 守衛 + 資料讓兩邊自洽」可以全綠通過。fresh review F-2。
seed_guard() {
  local name="${1:?seed_guard: name is empty}"; shift
  local dst; dst=$(seed "$name")
  local guard
  for guard in "$@"; do
    cp "$ROOT/scripts/$guard" "$dst/scripts/$guard"
    chmod +x "$dst/scripts/$guard"
  done
  echo "$dst"
}

# seed_fm <name> → 同 seed(),另外把 hooks/scripts/observability/memory/agents/
# tests/parallel-stage6/ 整包 + guides/guide-dev-flow.html 複製進去,並初始化成
# 一個真 git repo。
# 起因:check-file-map.sh 用 `git ls-files --cached --others --exclude-standard` 當
# 掃描來源(同 check-no-stale-paths.sh 的 seed_sp 模式),單純的檔案樹跑不了
# git ls-files。額外複製根目錄 .gitignore 到複本內,確保 --exclude-standard 在複本
# 與正式 repo 兩邊排除同一組 pattern(否則複本裡若混進 __pycache__ 之類雜物,
# 兩邊 scanned 數會對不上)。
# ⚠️ 2026-08-19:PATTERNS 加了 `agents/*.md` 後,這裡漏複製 agents/ 曾讓 FM-0
# 對照組自己變紅(seed 出來的複本掃到 81 支,EXPECTED_MAPPED_FILES 已改成 83)——
# 這不是 check-file-map.sh 的缺陷,是本測試治具沒跟著 PATTERNS 一起長,見
# hooks/selftest.sh 同類「記帳」教訓。以後 PATTERNS 再加新目錄,這裡也要同步加。
seed_fm() {
  local name="${1:?seed_fm: name is empty}"
  local dst; dst=$(seed "$name")
  rm -rf "$dst/scripts"
  cp -r "$ROOT/hooks" "$dst/hooks"
  cp -r "$ROOT/scripts" "$dst/scripts"
  cp -r "$ROOT/observability" "$dst/observability"
  cp -r "$ROOT/memory" "$dst/memory"
  cp -r "$ROOT/agents" "$dst/agents"
  mkdir -p "$dst/tests" "$dst/guides"
  cp -r "$ROOT/tests/parallel-stage6" "$dst/tests/parallel-stage6"
  cp "$ROOT/guides/guide-dev-flow.html" "$dst/guides/guide-dev-flow.html"
  [ -f "$ROOT/.gitignore" ] && cp "$ROOT/.gitignore" "$dst/.gitignore"
  git -C "$dst" init -q
  git -C "$dst" -c user.email=test@dev-flow.local -c user.name=test add -A
  git -C "$dst" -c user.email=test@dev-flow.local -c user.name=test commit -q -m seed
  echo "$dst"
}

# expect_local <pass|fail> <guard-script> <root> <label>
# 與 expect() 的差別:跑的是 **$root/scripts/ 底下那份複本**,不是正式 repo 的守衛。
expect_local() {
  local want="${1:?}" guard="${2:?}" target="${3:?}" label="${4:?}"
  [[ "$target" == "$WORK/"* ]] || { echo "expect_local: root 逃逸 $target" >&2; exit 1; }
  [[ -x "$target/scripts/$guard" ]] || { echo "expect_local: 找不到守衛複本 $target/scripts/$guard" >&2; exit 1; }
  count_case "$want"
  local out rc got
  out=$("$target/scripts/$guard" "$target" 2>&1)
  rc=$?
  got=pass; [ "$rc" -ne 0 ] && got=fail
  if [ "$got" = "$want" ]; then
    RESULTS+=("  ✅ $label — 預期 $want,實得 $got")
    PASS=$((PASS + 1))
  else
    RESULTS+=("  ❌ $label — 預期 $want,實得 $got (exit $rc)")
    RESULTS+=("       $(printf '%s' "$out" | tail -3 | tr '\n' ' ')")
    FAIL=$((FAIL + 1))
  fi
}

# mutate <root> <<'PY' … python 片段,sys.argv[1] = root
mutate() { python3 - "$1"; }

# expect_local_self <pass|fail> <guard-script> <root> <label>
# 與 expect_local() 的差別:跑守衛複本時**不帶任何 CLI 參數**(觸發守衛自己的
# 自測模式,例如 check-model-tiering.sh 沒收到 runs-root 參數時會去掃自己旁邊的
# scripts/fixtures/)。用於「守衛自測模式本身有沒有被繞過」這一類案例。
expect_local_self() {
  local want="${1:?}" guard="${2:?}" target="${3:?}" label="${4:?}"
  [[ "$target" == "$WORK/"* ]] || { echo "expect_local_self: root 逃逸 $target" >&2; exit 1; }
  [[ -x "$target/scripts/$guard" ]] || { echo "expect_local_self: 找不到守衛複本 $target/scripts/$guard" >&2; exit 1; }
  count_case "$want"
  local out rc got
  out=$("$target/scripts/$guard" 2>&1)
  rc=$?
  got=pass; [ "$rc" -ne 0 ] && got=fail
  if [ "$got" = "$want" ]; then
    RESULTS+=("  ✅ $label — 預期 $want,實得 $got")
    PASS=$((PASS + 1))
  else
    RESULTS+=("  ❌ $label — 預期 $want,實得 $got (exit $rc)")
    RESULTS+=("       $(printf '%s' "$out" | tail -3 | tr '\n' ' ')")
    FAIL=$((FAIL + 1))
  fi
}

# expect_local_arg <pass|fail> <guard-script> <root> <cli-arg> <label>
# 與 expect_local() 的差別:CLI 參數是呼叫方指定的 <cli-arg>(通常是 $root 之外、
# 另外準備的一個「外部 runs 根」目錄),不是預設的 $root 本身。用於驗證守衛的
# 正常模式(接受外部 runs-root 路徑當參數)真的有咬到給定目錄,不是只有自測模式
# 內部的 fixture 掃描路徑被驗證過。
expect_local_arg() {
  local want="${1:?}" guard="${2:?}" target="${3:?}" arg="${4:?}" label="${5:?}"
  [[ "$target" == "$WORK/"* ]] || { echo "expect_local_arg: root 逃逸 $target" >&2; exit 1; }
  [[ -x "$target/scripts/$guard" ]] || { echo "expect_local_arg: 找不到守衛複本 $target/scripts/$guard" >&2; exit 1; }
  count_case "$want"
  local out rc got
  out=$("$target/scripts/$guard" "$arg" 2>&1)
  rc=$?
  got=pass; [ "$rc" -ne 0 ] && got=fail
  if [ "$got" = "$want" ]; then
    RESULTS+=("  ✅ $label — 預期 $want,實得 $got")
    PASS=$((PASS + 1))
  else
    RESULTS+=("  ❌ $label — 預期 $want,實得 $got (exit $rc)")
    RESULTS+=("       $(printf '%s' "$out" | tail -3 | tr '\n' ' ')")
    FAIL=$((FAIL + 1))
  fi
}

echo "=== 架構守衛負向回歸測試 ==="
echo "ROOT(唯讀)= $ROOT"
echo "WORK(暫存)= $WORK"
echo

# ───────────────────────────── Design Contract ─────────────────────────────
D=$(seed dc0); expect pass check-design-contract.sh "$D" "DC-0 對照組(未變異)"

D=$(seed dc1); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Risk: high", "- Risk: normal", t, count=1, flags=re.M)
assert n != t, "DC-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-1 example Risk high→normal(單一編輯,舊版會靜默略過整組)"

D=$(seed dc2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
t = p.read_text(encoding="utf-8")
n = t.replace("- Applicability: applicable",
              "- Applicability: n-a — 本次僅調整前端文案,不跨模組、不動 API 與 schema", 1)
assert n != t, "DC-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-2 example applicable→n-a(附合理理由)"

D=$(seed dc3); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
hit = False
for i, line in enumerate(lines):
    if line.startswith("| Boundary / Module |") and "Data owner" in line:
        lines[i] = line.replace(" Data owner |", " ")
        hit = True
        break
assert hit, "DC-3 mutation 沒生效:找不到 Architecture Boundaries 表頭"
p.write_text("".join(lines), encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-3 example 刪 Data owner 欄"

D=$(seed dc4); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
t = p.read_text(encoding="utf-8")
n = t.replace("不得直接觸 DB;不得自行推導權限結論以外的狀態(權限正本在 API 層)", "無", 1)
n = re.sub(r"- Known design limit:\n(  ①.*?\n)+.*?本期不新增樂觀鎖、idempotency key、重試 UI、新 API 或新 schema。\n",
           "- Known design limit:併發情況可能有問題,後續評估。\n", n, count=1, flags=re.S)
assert n != t, "DC-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-4 example 填成 canon 明列的壞例(Forbidden「無」+ 模糊詞)"

D=$(seed dc5); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "_templates/4-spec.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Applicability: applicable \| n-a — <理由>\n", "", t, count=1, flags=re.M)
assert n != t, "DC-5 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-5 刪 Template 的 Applicability 欄"

D=$(seed dc6); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "_templates/7-review.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Dependency Direction", "XXX").replace("Data Ownership", "XXX")
n = n.replace("Interface Stability", "XXX").replace("Design Boundary Contract", "XXX")
assert n != t, "DC-6 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-6 刪 Stage 7 承接規則"

# DC-7/8/9(2026-08 final verdict M-3):Stage 6 的 Design boundary finding 內容檢查。
# 舊版只比「行數 == Test Integrity finding 行數」,填 n-a、只填①、留空都過。
D=$(seed dc7); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Design boundary finding:.*$", "- Design boundary finding:n-a", t, flags=re.M)
assert n != t, "DC-7 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-7 example 七筆 Design boundary finding 全改 n-a"

D=$(seed dc8); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Design boundary finding:.*$", "- Design boundary finding:①無。",
           t, count=1, flags=re.M)
assert n != t, "DC-8 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-8 某一筆只有①、缺②～⑤"

D=$(seed dc9); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Design boundary finding:.*$", "- Design boundary finding:",
           t, count=1, flags=re.M)
assert n != t, "DC-9 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-9 某一筆冒號後留空"

# DC-X1/X2(2026-08-17,F-2 HIGH-3):跨檔恆真斷言掃描本身此前零負向覆蓋 —— 掃描
# scripts/check-realworld.sh 這件事從沒被任何案例驗過「真的抓得到別的檔」,只驗過
# 「本檔(check-design-contract.sh 自己)被下毒會抓到」(GS-8)。這裡補別的檔中毒的案例,
# 且刻意覆蓋單行與多行排版兩種寫法(HIGH-1 修的正是多行排版舊版抓不到)。
# 插入點選 check-realworld.sh 的 `def read(rel):` 之前(module 層級,語法上合法但不會
# 被執行到,因為這裡只測 check-design-contract.sh 的靜態掃描,不會真的跑
# check-realworld.sh)。
D=$(seed dcx1); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts/check-realworld.sh"
t = p.read_text(encoding="utf-8")
marker = "def read(rel):"
assert marker in t, "DC-X1: 找不到插入點"
n = t.replace(marker, 'check(1 == 1, "poison")\n\n\n' + marker, 1)
assert n != t, "DC-X1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-X1 check-realworld.sh 混入單行 check(1 == 1, poison)(跨檔掃描須抓到別的檔,不只自掃)"

D=$(seed dcx2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts/check-realworld.sh"
t = p.read_text(encoding="utf-8")
marker = "def read(rel):"
assert marker in t, "DC-X2: 找不到插入點"
n = t.replace(marker, 'check(\n    True,\n    "poison"\n)\n\n\n' + marker, 1)
assert n != t, "DC-X2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-X2 check-realworld.sh 混入多行排版 check(\\n    True,\\n    poison)(HIGH-1 修的正是這種逐行 match 抓不到的排版)"

# ─────────────────────────────── Gate Token ────────────────────────────────
D=$(seed gt0); expect pass check-gate-tokens.sh "$D" "GT-0 對照組(未變異)"

D=$(seed gt1); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace(" + **Demo verdict**", "", 1)
assert n != t, "GT-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-1 刪 G2 的一個粗體 token(Demo verdict)"

D=$(seed gt2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("**本次 S 全綠**", "本次 S 全綠", 1)
assert n != t, "GT-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-2 G3 的一個 token 被去掉粗體(外部 gate-consistency 抓不到)"

D=$(seed gt3); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^  7\. Optional Layer[^\n]*\n", "", t, count=1, flags=re.M)
assert n != t, "GT-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-3 刪 G3 錨定義八點中的一點"

# GT-4(fresh review F-3):憑空多一道 gate。措辭刻意避開會被別的守衛誤觸的字串
# (例如 "Forbidden dependencies" 會撞 check-design-contract 的 readme-canonical 規則),
# 確保紅燈是 check-gate-tokens 抓到的,不是別人順手擋下的。
D=$(seed gt4); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("- G2 錨定義(錨句在上;此處為條件式全文):",
              "- G4 = 設計邊界對不對(4-spec:**設計契約三表全填**,未過不得進入 Stage 5;\n"
              "  核准者不得為該文檔 owner)。\n"
              "- G2 錨定義(錨句在上;此處為條件式全文):", 1)
assert n != t, "GT-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-4 §7 憑空新增第四道 gate 標籤(G4)"

# GT-5(fresh review F-4):八點的**極性**被反轉。編號仍 1–8、原本的寬鬆關鍵詞仍在,
# 舊版守衛對這四種 mutation 全部 exit 0 —— 規則語意反過來而測試不紅。
D=$(seed gt5a); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Gauntlet PASS 不取代 Standards Axis", "Gauntlet PASS 取代 Standards Axis", 1)
assert n != t, "GT-5a mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-5a 第 8 點極性反轉(Gauntlet PASS「不」取代雙軸)"

D=$(seed gt5b); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Required Layer 不得為 unverified", "Required Layer 得為 unverified", 1)
assert n != t, "GT-5b mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-5b 第 5 點極性反轉(Required Layer「不得」為 unverified)"

D=$(seed gt5c); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Optional Layer 可為 unverified,但必須誠實標示",
              "Optional Layer 可為 unverified", 1)
assert n != t, "GT-5c mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-5c 第 7 點刪掉「必須誠實標示」義務"

D=$(seed gt5d); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Explicitly Excluded Layer 可為 n-a,但必須附理由",
              "Explicitly Excluded Layer 可為 n-a", 1)
assert n != t, "GT-5d mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-5d 第 6 點刪掉「必須附理由」義務"

# GT-6(2026-08 final verdict M-1):逐編號完整比對必須擋住 decoy 與片語搬家。
# 舊版是在整個八點 body 做子字串搜尋,這兩種都繞得過(fresh reviewer 實測重現)。
D=$(seed gt6a); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("  5. Required Layer 不得為 unverified 或 n-a。",
              "  5. Required Layer 得為 unverified 或 n-a(reviewer 自行判斷即可,"
              "不需要 Required Layer 不得為 unverified 的機械檢查)。", 1)
assert n != t, "GT-6a mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-6a 第 5 點反義 + 同句保留原片語當 decoy"

D=$(seed gt6b); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("  5. Required Layer 不得為 unverified 或 n-a。\n"
              "  6. Explicitly Excluded Layer 可為 n-a,但必須附理由。",
              "  5. 由 reviewer 依 Verification Profile 判斷即可。\n"
              "  6. Explicitly Excluded Layer 可為 n-a,但必須附理由;"
              "Required Layer 不得為 unverified 或 n-a。", 1)
assert n != t, "GT-6b mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-6b 第 5 點必要句被搬到第 6 點(片語仍在 body 內)"

# ────────────────────────────── Version Sync ───────────────────────────────
D=$(seed vs0); expect pass check-version-sync.sh "$D" "VS-0 對照組(四處一致)"

D=$(seed vs1); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("devflow-evidence-gauntlet.sh`(1.3.3,", "devflow-evidence-gauntlet.sh`(9.9.9,", 1)
assert n != t, "VS-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-version-sync.sh "$D" "VS-1 README 版本改 9.9.9"

D=$(seed vs2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "devflow-contract.json"
t = p.read_text(encoding="utf-8")
n = t.replace('"gauntlet": "1.3.3"', '"gauntlet": "9.9.9"', 1)
assert n != t, "VS-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-version-sync.sh "$D" "VS-2 devflow-contract.json 版本改 9.9.9"

D=$(seed vs3); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "notes/design/evidence-gauntlet.md"
t = p.read_text(encoding="utf-8")
n = t.replace("**現行 Gauntlet 版本:1.3.3**", "**現行 Gauntlet 版本:9.9.9**", 1)
assert n != t, "VS-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-version-sync.sh "$D" "VS-3 notes/design 版本改 9.9.9"

D=$(seed vs4); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "notes/design/evidence-gauntlet.md"
t = p.read_text(encoding="utf-8")
n = t.replace("**現行 Gauntlet 版本:1.3.3**\n", "", 1)
assert n != t, "VS-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-version-sync.sh "$D" "VS-4 版本錨整行被刪(fail-closed,不得靜默略過)"

D=$(seed vs5); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "docs/dev/tools/devflow-evidence-gauntlet.sh"
t = p.read_text(encoding="utf-8")
n = t.replace('GAUNTLET_VERSION="1.3.3"', 'GAUNTLET_VERSION="9.9.9"', 1)
assert n != t, "VS-5 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-version-sync.sh "$D" "VS-5 docs/dev/tools 散發副本版本改 9.9.9(第 5 處單獨漂移)"

# ──────────────── Real-world / Stage 3 對帳存在性(check-realworld.sh;§7 第 1 點)────────────────
# 只驗存在性/結構(見 scripts/check-realworld.sh 第 10 節註解),不驗場景名字面。
D=$(seed rw0); expect pass check-realworld.sh "$D" "RW-0 對照組(Stage 3 對帳段完整、逐場點名)"

D=$(seed rw1); mutate "$D" <<'PY'
import sys, re, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"\nStage 3 對帳.*?(?=\n## Diff Budget)", "\n", t, flags=re.S)
assert n != t, "RW-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-realworld.sh "$D" "RW-1 Out of Scope 整段 Stage 3 對帳被刪(恆綠漏洞:P6 沒有機械檢查會發現)"

D=$(seed rw2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
t = p.read_text(encoding="utf-8")
old = "- 資料過期/併發編輯:偵測他人已改動後拒絕以過期資料標狀態、提示重新整理(3-prototype「Scenario AC-1(資料過期)」)。"
new = "- 資料過期/併發編輯:偵測他人已改動後拒絕以過期資料標狀態、提示重新整理。"
n = t.replace(old, new, 1)
assert n != t, "RW-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-realworld.sh "$D" "RW-2 一條 Out of Scope 場景保留但拿掉逐場點名引用(vacuous-truth 陷阱:len>=1 抓不到,需逐條比對)"

# ─────────────────── 守衛本體被改弱(Guard Source;fresh review F-2)───────────────────
# 這一整類原本零覆蓋:上面所有案例都只變異資料檔,守衛本體始終從正式 repo 執行。
# 於是「co-edit 守衛 + 資料,讓兩邊互相自洽」可以端到端全綠。以下每一案都是
# **改守衛自己的原始碼**,並斷言守衛必須因此變紅。

D=$(seed_guard gs0 check-design-contract.sh check-gate-tokens.sh)
expect_local pass check-design-contract.sh "$D" "GS-0a 對照組(守衛複本未變異)"
expect_local pass check-gate-tokens.sh     "$D" "GS-0b 對照組(守衛複本未變異)"

# GS-1:單行把 TRIGGER_KEYWORDS 由 21 條砍成 1 條。
# 修正前:檢查數 127→107,heartbeat 仍報 trigger-parity>0,MIN_CHECKS=100 也還在 → 全綠。
D=$(seed_guard gs1 check-design-contract.sh); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-design-contract.sh"
t = p.read_text(encoding="utf-8")
n = re.sub(r"TRIGGER_KEYWORDS = \[.*?\n\]\n", 'TRIGGER_KEYWORDS = [\n    "跨模組",\n]\n',
           t, count=1, flags=re.S)
assert n != t, "GS-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-1 守衛的 TRIGGER_KEYWORDS 被砍成 1 條"

# GS-2:兩行 —— 停掉 handoff-example 群組 + 刪它的 REQUIRED_GROUPS 條目。
# 修正前:116/116 全綠(heartbeat 看不到不存在的群組,總數仍 > MIN_CHECKS)。
D=$(seed_guard gs2 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-design-contract.sh"
t = p.read_text(encoding="utf-8")
n = t.replace('    "handoff-example",\n', "", 1)
assert n != t, "GS-2 mutation(刪 REQUIRED_GROUPS 條目)沒生效"
marker = 'CURRENT_GROUP = "handoff-example"'
i = n.index(marker)
j = n.index("if True:", i)
n = n[:j] + "if False:" + n[j + len("if True:"):]
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-2 守衛停掉 handoff-example 群組並同步刪註冊條目"

# GS-3:守衛與資料 co-edit —— 從 DESIGN_COLUMNS 刪掉 Test seam,同時把模板與 example
# 的該欄一起刪掉,讓兩邊互相自洽。canon 交叉核對必須抓到(canon §2.4 仍列該欄)。
D=$(seed_guard gs3 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1])
g = root / "scripts" / "check-design-contract.sh"
t = g.read_text(encoding="utf-8")
n = t.replace('"State / Data flow", "Error handling", "Test seam"]',
              '"State / Data flow", "Error handling"]', 1)
assert n != t, "GS-3 mutation(守衛端)沒生效"
g.write_text(n, encoding="utf-8")
for rel in ("_templates/4-spec.md", "example/contract-expiry-reminder/4-spec.md"):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    s = s.replace(" | Error handling | Test seam |", " | Error handling |")
    p.write_text(s, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-3 守衛與資料 co-edit 刪掉必填欄 Test seam(canon 交叉核對接住)"

# GS-4:把 MIN_CHECKS 由 164 調到 10(讓次級 backstop 形同虛設)。
D=$(seed_guard gs4 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-design-contract.sh"
t = p.read_text(encoding="utf-8")
n = t.replace("MIN_CHECKS = 164", "MIN_CHECKS = 10", 1)
assert n != t, "GS-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-4 守衛的 MIN_CHECKS 被調低"

# GS-5:守衛與資料 co-edit —— 把 Stage 6 的承接 needle「Design Boundary Check」
# 從 handoffs 清單刪掉,同時把模板裡的該檢查也刪掉。needle 數量釘死必須接住。
D=$(seed_guard gs5 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1])
g = root / "scripts" / "check-design-contract.sh"
t = g.read_text(encoding="utf-8")
n = t.replace('("_templates/6-implementation-notes.md", ["Design Boundary Check"],',
              '("_templates/6-implementation-notes.md", [],', 1)
assert n != t, "GS-5 mutation(守衛端)沒生效"
g.write_text(n, encoding="utf-8")
p = root / "_templates" / "6-implementation-notes.md"
p.write_text(p.read_text(encoding="utf-8").replace("Design Boundary Check", "邊界檢查"),
             encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-5 守衛與資料 co-edit 刪掉 Stage 6 承接 needle"

# GS-6:gate-tokens 的守衛與資料 co-edit —— 從 EXPECTED["G3"] 刪一個 token,
# 同時把 README §7 的該 token 也去掉粗體。兩邊自洽,靠長度釘死才抓得到。
D=$(seed_guard gs6 check-gate-tokens.sh); mutate "$D" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1])
g = root / "scripts" / "check-gate-tokens.sh"
t = g.read_text(encoding="utf-8")
n = t.replace('        "+ 現象證據逐 S 相符",\n', "", 1)
assert n != t, "GS-6 mutation(守衛端)沒生效"
g.write_text(n, encoding="utf-8")
p = root / "README.md"
p.write_text(p.read_text(encoding="utf-8").replace(
    "**+ 現象證據逐 S 相符**", "+ 現象證據逐 S 相符", 1), encoding="utf-8")
PY
expect_local fail check-gate-tokens.sh "$D" "GS-6 守衛與 README co-edit 刪掉一個 G3 token"

# GS-7:gate-tokens 的 G3_POINTS 被縮短(八點守衛被改弱),資料不動。
D=$(seed_guard gs7 check-gate-tokens.sh); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-gate-tokens.sh"
t = p.read_text(encoding="utf-8")
n = t.replace('    "8": "Gauntlet PASS 不取代 Standards Axis / Spec Axis / Operational Walkthrough / "\n'
              '         "Coverage Matrix / 真實現象複驗。",\n', "", 1)
assert n != t, "GS-7 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-gate-tokens.sh "$D" "GS-7 守衛的 EXPECTED_G3_POINTS 被縮短(第 8 點守衛消失)"

# GS-8:把一條斷言改成恆真(`check(rows >= 1, …)` → `check(True, …)`)。
# 檢查數不變、群組還在、長度釘死也全過 —— 長度類的釘死本質上防不到這一類。
# 這是 2026-08 驗收實測抓到的殘留,補上 guard-selfpin 的 `check(True` 掃描後才擋得住。
D=$(seed_guard gs8 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-design-contract.sh"
t = p.read_text(encoding="utf-8")
n = t.replace('        check(rows >= 1, f"{EXAMPLE}「{heading}」表至少一列已填內容", f"資料列數={rows}")',
              '        check(True, f"{EXAMPLE}「{heading}」表至少一列已填內容", f"資料列數={rows}")', 1)
assert n != t, "GS-8 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-8 守衛的一條斷言被改成恆真(check(True))"

# ── S67 群組:Stage 6/7 執行期強制條款(check-stage67-enforcement.sh)──────────
#
# 起因是 2026-08 order-intake 的真實執行:四條散文規則同時失效而所有產出看起來完整。
# 這一組把「條款有沒有被刪掉」變成會紅的測試 —— 條款寫在模板裡沒人守,
# 只有這裡的負向案能證明「守衛真的擋得住」。
# S67-ST(2026-08-22):頂註執行清單拿掉「整合回歸」必須紅 —— 舊節序
# (Final Fresh 在整合回歸之前)的假綠。加案後 EXPECTED_NEGATIVES 104→105、
# EXPECTED_TOTAL 118→119。

D=$(seed s67-control)
expect pass check-stage67-enforcement.sh "$D" "S67-0 對照組(模板與範例未變異)"

D=$(seed s67-a1)
mutate "$D" <<'PY'
import pathlib, sys, re
p = pathlib.Path(sys.argv[1]) / "_templates/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = t.replace("守衛武裝自檢", "起手提醒")
assert n != t, "S67-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-1 Stage 6 步 0 的「守衛武裝自檢」被改名(條款名消失)"

D=$(seed s67-a3-template)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/5-tasks.md"
t = p.read_text(encoding="utf-8")
n = t.replace("=== RUN", "測試輸出")
assert n != t, "S67-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-2 5-tasks 模板的「數 === RUN」骨架被抽掉"

D=$(seed s67-a3-example)
mutate "$D" <<'PY'
import pathlib, sys, re
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/5-tasks.md"
t = p.read_text(encoding="utf-8")
# 把範例的 Verify 退回「只有 -run、沒有案例數斷言」的舊形狀
n = re.sub(r"- Verify: `n=\$\(go test ([^)]*?) -run (\w+) -v 2>&1 \| grep -c '\^=== RUN'\); test \"\$n\" -ge \d+`",
           r"- Verify: `go test \1 -run \2`", t)
assert n != t, "S67-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-3 範例的 Verify 退回沒有案例數斷言的形狀(-run 假綠)"

D=$(seed s67-a4)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/7-review.md"
t = p.read_text(encoding="utf-8")
n = t.replace("補跑 `dev-setup`", "自己想辦法裝一支")
assert n != t, "S67-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-4 gauntlet 缺件的補救不再指向補跑 dev-setup(手動 cp 會繞過版本握手)"

D=$(seed s67-a5)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/4-spec.md"
t = p.read_text(encoding="utf-8")
n = t.replace("觀測方式必須在本 repo 可執行", "觀測方式盡量具體")
assert n != t, "S67-5 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-5 4-spec 觀測欄的「必須在本 repo 可執行」被弱化成建議"

# S67-6/7/8(2026-08-15 追加,findings A-3 = VF、findings A-12 = DOC):
# 三案的 needle 都刻意挑**新條款獨有**的字面,不重疊 A1/A3/A4/A5 既有 needle,
# 才能證明是新檢查抓到的,不是誤觸舊檢查(同檔頭「VF 不要跟內部代號 A3 搞混」)。

D=$(seed s67-vf-template)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/5-tasks.md"
t = p.read_text(encoding="utf-8")
n = t.replace("可原樣貼進 shell 的純指令", "盡量簡潔的指令")
assert n != t, "S67-6 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-6 5-tasks 模板的「Verify 必須單行純指令」硬紀律被弱化"

D=$(seed s67-vf-example)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/5-tasks.md"
t = p.read_text(encoding="utf-8")
# 保留 grep -c / === RUN(不觸發舊 A3 例子檢查),只在同一行尾端混進中文說明——
# 這正是 findings A-3 的原始成因(指令 + 說明混寫成單行)。
old = ("- Verify: `n=$(go test ./internal/... -run TestExpiring -v 2>&1 "
       "| grep -c '^=== RUN'); test \"$n\" -ge 1`")
new = old + ";需先啟動測試用資料庫"
n = t.replace(old, new, 1)
assert n != t, "S67-7 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-7 範例 T-1 的 Verify 值尾端混進中文說明(指令+說明同一行)"

D=$(seed s67-doc)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = t.replace("devflow-doctor.sh", "devflow-check.sh")
assert n != t, "S67-8 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-8 6-notes 步 0 的 doctor 必跑要求被抽掉(devflow-doctor.sh 消失)"

D=$(seed_guard s67-guard check-stage67-enforcement.sh)
mutate "$D" <<'PY'
import pathlib, sys, re
p = pathlib.Path(sys.argv[1]) / "scripts/check-stage67-enforcement.sh"
t = p.read_text(encoding="utf-8")
# 把 A1 整組 need() 拿掉(但不動 MIN_CHECKS)—— 應由檢查數地板接住
n = re.sub(r'for rel in \("_templates/6-implementation-notes\.md".*?f"A1:\{rel\} 沒給可執行的自檢指令 `devflow-exec\.sh status`"\)\n',
           'for rel in ():\n    pass\n', t, flags=re.S)
assert n != t, "S67-9 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-stage67-enforcement.sh "$D" "S67-9 守衛自己的 A1 整組被刪(檢查數地板接住)"

# ST:舊節序(Final Fresh 在整合回歸之前)必須紅。把頂註裡的「整合回歸」抽掉,
# 模擬 2026-08 當時「整合回歸只住 Exit Checklist」的形狀。
D=$(seed s67-st); mutate "$D" <<'PY'
import sys, pathlib, re
p = pathlib.Path(sys.argv[1]) / "_templates/7-review.md"
t = p.read_text(encoding="utf-8")
header, rest = re.split(r"\n##[ \t]", t, 1)
header = header.replace("整合回歸", "INTEGRATION_PLACEHOLDER")
n = header + "\n## " + rest
assert n != t, "S67-ST mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-ST 頂註執行清單拿掉整合回歸(舊節序假綠)"

# ── TF 群組:測試檔路徑必須列進 Files(check-stage67-enforcement.sh 的 D-39 紀律)──
#
# 起因:D-39(order-intake 實測歸納)—— Verify 跑測試但 Files 沒列測試檔,candidate
# 產出前就被 Stage 6 scope guard 擋死。S67-0(對照組)已涵蓋這兩項檢查的未變異
# 基準,本群組只需要負向案。

D=$(seed tf-template)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/5-tasks.md"
t = p.read_text(encoding="utf-8")
n = t.replace("測試檔路徑也要列進 `Files`", "測試檔案盡量列進去", 1)
assert n != t, "TF-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "TF-1 5-tasks 模板的「測試檔路徑也要列進 Files」紀律句被弱化"

D=$(seed tf-example)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/5-tasks.md"
t = p.read_text(encoding="utf-8")
old = "Files: `internal/handler/contract.go`, `internal/service/contract.go`, `internal/repo/contract.go`, `internal/service/contract_test.go`, `internal/handler/contract_test.go`"
new = "Files: `internal/handler/contract.go`, `internal/service/contract.go`, `internal/repo/contract.go`"
n = t.replace(old, new, 1)
assert n != t, "TF-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "TF-2 範例 T-1 的 Files 欄被拿掉測試檔路徑(跑測試的 T 卻沒有測試路徑)"

# ── DSD 群組:dev-setup upgrade 三方比對紀律(check-dev-setup-discipline.sh;B-2)──
#
# 起因:skills/dev-setup/SKILL.md 的 upgrade 三方比對/baseline 快照/逐檔徵同意/
# 過渡態/master-only 剝除/gate twin 相依全是散文規則,退回等於原地重現
# 「upgrade 靜默蓋掉本地客製」。

D=$(seed dsd0); expect pass check-dev-setup-discipline.sh "$D" "DSD-0 對照組(未變異)"

D=$(seed dsd1); mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "skills/dev-setup/SKILL.md"
t = p.read_text(encoding="utf-8")
n = t.replace("全部受管檔視為②本地客製,逐檔徵同意", "比照一般流程處理", 1)
assert n != t, "DSD-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-dev-setup-discipline.sh "$D" "DSD-1 過渡態條款的處置句被刪(全部視為②逐檔徵同意 → 比照一般流程)"

D=$(seed dsd2); mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "skills/dev-setup/SKILL.md"
t = p.read_text(encoding="utf-8")
n = t.replace("三方比對", "比對法")
assert n != t, "DSD-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-dev-setup-discipline.sh "$D" "DSD-2 三方比對判別法字面全數被改寫"

# ── MM 群組:README master-only 標記平衡(check-readme-markers.sh;MED-4)──────
#
# 起因:skills/dev-setup/SKILL.md 的 install/upgrade/check 全靠 sed 抽
# `<!-- devflow:master-only:start/end -->` 之間的區塊。這對標記若不對稱(數量不等、
# 或巢狀/交錯),sed range 會靜默抽到檔尾或抽出錯誤內容,沒有任何報錯。

D=$(seed mm-control)
expect pass check-readme-markers.sh "$D" "MM-0 對照組(README 標記未變異)"

D=$(seed mm-missing-end)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("<!-- devflow:master-only:end -->\n", "", 1)
assert n != t, "MM-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-readme-markers.sh "$D" "MM-1 刪掉一個 end marker(start/end 數量不對稱,sed 會跑到檔尾)"

D=$(seed mm-nested-start)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("<!-- devflow:master-only:start -->\n",
              "<!-- devflow:master-only:start -->\n<!-- devflow:master-only:start -->\n", 1)
assert n != t, "MM-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-readme-markers.sh "$D" "MM-2 巢狀 start(兩個 start 中間沒有 end 先閉合)"

D=$(seed mm-both-removed)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("<!-- devflow:master-only:start -->\n", "").replace(
    "<!-- devflow:master-only:end -->\n", "")
assert n != t, "MM-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-readme-markers.sh "$D" "MM-3 start/end 整組被刪(0 對『平衡』但 sed 剝除變無操作)"

# ── SP 群組:過期外掛路徑守衛(check-no-stale-paths.sh)────────────────────────
#
# 起因:dev-talk 併入 dev-flow 單一 plugin 後,散發路徑從 local marketplace 改為
# cache 安裝,活文件不得殘留舊路徑或開發者個人絕對路徑。這一組證明守衛真的會抓到
# 混入的舊路徑/個人路徑,而不是空轉。
#
# 禁字用字串相加組出(不留連續字面)——本檔自己也落在 scripts/ 掃描範圍內,
# 直接寫出連續禁字會讓 devflow-check 的真實掃描對本檔誤報。
#
# 2026-08-15 N-5 改版後,seed 副本改用 seed_sp()(見上方定義)——目標 root 必須是
# git working tree 才能跑 `git ls-files`。

D=$(seed_sp sp0)
expect pass check-no-stale-paths.sh "$D" "SP-0 對照組(未變異)"

D=$(seed_sp sp1); mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
banned = "plugins/local/dev-" + "flow"
n = t + "\n測試混入舊路徑:~/.claude/" + banned + "/hooks/devflow-exec.sh\n"
assert n != t, "SP-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-no-stale-paths.sh "$D" "SP-1 README 混入過期 dev-flow local marketplace 路徑"

D=$(seed_sp sp2); mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
banned = "plugins/local/dev-" + "talk"
n = t + "\n測試混入舊路徑:~/.claude/" + banned + "/skills/dev-talk/SKILL.md\n"
assert n != t, "SP-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-no-stale-paths.sh "$D" "SP-2 README 混入過期 dev-talk local marketplace 路徑"

D=$(seed_sp sp3); mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "devflow-contract.json"
t = p.read_text(encoding="utf-8")
banned = "/Users/" + "asheng"
n = t + "\n// debug path: " + banned + "/dev/dev-flow\n"
assert n != t, "SP-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-no-stale-paths.sh "$D" "SP-3 devflow-contract.json 混入開發者個人絕對路徑"

# SP-4(2026-08-15 補,第三批獨立審查 P1):docs/dev/STATUS.md 此前既不在掃描目標也
# 不在可見豁免清單,塞禁字守衛仍零命中 exit 0。本案證明補上掃描目標後真的會咬到。
D=$(seed_sp sp4); mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "docs/dev/STATUS.md"
t = p.read_text(encoding="utf-8")
banned = "plugins/local/dev-" + "flow"
n = t + "\n測試混入舊路徑:~/.claude/" + banned + "/hooks/devflow-exec.sh\n"
assert n != t, "SP-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-no-stale-paths.sh "$D" "SP-4 docs/dev/STATUS.md 混入過期 dev-flow local marketplace 路徑(P1 補:此路徑先前完全不可見)"

# SP-5(2026-08-15 補,N-5 fail-closed 改版):observability/ 此前完全不在掃描目標
# 也不在可見豁免清單,塞禁字守衛仍零命中 exit 0(獨立審查實測的破口之一)。本案
# 證明改用 git ls-files 全量掃描 − 印出來的 ALLOWLIST 後,任意活文件目錄(不需
# 要像 SP-4 那樣先補進清單)都會被自動掃到——這就是「新增目錄自動被掃」的驗證。
D=$(seed_sp sp5); mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "observability/devflow-obs.py"
t = p.read_text(encoding="utf-8")
banned = "plugins/local/dev-" + "flow"
n = t + "\n# 測試混入舊路徑:~/.claude/" + banned + "/hooks/devflow-exec.sh\n"
assert n != t, "SP-5 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-no-stale-paths.sh "$D" "SP-5 observability/ 混入過期 dev-flow local marketplace 路徑(fail-closed:新目錄不必列清單就會被掃到)"

# SP-6(X-2,2026-08-17,守衛本體被弱化):把 check-no-stale-paths.sh 的
# `git ls-files` 呼叫縮小成只認 "--","README.md" 這一個檔(mutation 只動 1 行)。
# 舊版(N-2 地板)只釘「跑了幾條禁字規則」,candidates 只剩 1 個檔一樣能跑滿
# MIN_CHECKS,不會現形。這是本輪補的 SENTINELS 斷言要接住的案例:哨兵
# hooks/devflow-lib.py 不在被縮小後的掃描名單裡 → exit 2 點名。
# 用 seed_sp(不是 seed_guard)是因為守衛本體要 git ls-files,target 必須是真 git
# working tree;守衛複本另外用 cp 放進去(seed_sp 本身不放守衛複本)。
D=$(seed_sp sp6)
cp "$ROOT/scripts/check-no-stale-paths.sh" "$D/scripts/check-no-stale-paths.sh"
chmod +x "$D/scripts/check-no-stale-paths.sh"
mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts/check-no-stale-paths.sh"
t = p.read_text(encoding="utf-8")
old = '["git", "-C", root, "ls-files", "-z", *extra_args],'
new = '["git", "-C", root, "ls-files", "-z", "--", "README.md"],'
assert old in t, "SP-6 mutation 沒生效:找不到 _ls_files 的 subprocess.run 呼叫"
n = t.replace(old, new, 1)
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-no-stale-paths.sh "$D" "SP-6 守衛的 ls-files 呼叫被縮小成只掃 README.md(SENTINELS 斷言接住)"

# SP-7(X-2,2026-08-17,新能力的牙):放一個**未 git add** 的檔,內含禁字。改前的
# 舊版掃描來源只有 `git ls-files`(已追蹤檔),這種檔案完全看不到、零命中 exit 0
# ——新檔在 commit 前不受保護。本案跑的是 $ROOT/scripts/(真正修好的版本,非
# 守衛複本),證明 tracked_files() 併入 `--others --exclude-standard` 後真的會咬到。
D=$(seed_sp sp7); mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "untracked-banned.md"
banned = "plugins/local/dev-" + "flow"
p.write_text("測試混入舊路徑(未 git add):~/.claude/" + banned + "/hooks/devflow-exec.sh\n",
             encoding="utf-8")
assert p.exists(), "SP-7 mutation 沒生效"
PY
expect fail check-no-stale-paths.sh "$D" "SP-7 未追蹤檔混入過期 dev-flow local marketplace 路徑(新檔在 commit 前也受保護)"

# SP-8/SP-9(F3:X-2,2026-08-17,兩位 fresh 審查者對 check-no-stale-paths.sh 提出的
# HIGH finding,常設化)——裁決者要求先驗證外層(本檔)原本接不接得住這兩種攻擊,
# 結論記在下面每案的註解:兩種攻擊在裁決驗證階段(對本檔尚未加 SP-8/SP-9 的舊版)
# 跑 `bash scripts/test-architecture-guards.sh` 實測都已經是紅——攻擊 (a) 讓 SP-7
# 從 fail 變 pass(1 案落地);攻擊 (b) 因為 seed_sp 複製的活文件散在多個不在 6 個
# 哨兵名單內的路徑,連帶讓 SP-3/SP-4/SP-5/SP-6/SP-7 都從 fail 變 pass 或炸
# AssertionError(5 案落地)——不是「零防禦」,是「外層本來就會炸,但只在多案
# 連帶失敗裡間接看得出來,沒有一條案名清楚點出『pathspec 攻擊』或『untracked 呼叫
# 被拿掉』這件事本身」。SP-8/SP-9 把這兩種攻擊各自獨立成一條具名案例,並且直接
# 咬在**單支腳本**上(用 expect_local 跑守衛複本,不依賴 seed_sp 複製了哪些活文件
# 這種間接旁證),使原本「靠連帶效應被動接住」變成「常設明文接住」。
# check-no-stale-paths.sh 本體這輪加了自釘(self_pin_check):兩條 _ls_files 呼叫
# 字面各恰一次、呼叫總數恰 2、_ls_files() 內部 subprocess.run 的動態 pathspec
# 標記恰一次——下面兩案驗證的正是自釘接住,不是靠 seed 進去的禁字檔被掃到才紅。

# SP-8:把 tracked_files() 的 `--others --exclude-standard` 那條呼叫拿掉(還原成
# 舊版只掃已追蹤檔),同時 seed 一個未追蹤禁字檔。自釘應在讀自己原始碼那一步就
# 現形(_ls_files 呼叫總數變 1),不需要等到真的漏放行未追蹤檔案這一步。
D=$(seed_sp sp8)
cp "$ROOT/scripts/check-no-stale-paths.sh" "$D/scripts/check-no-stale-paths.sh"
chmod +x "$D/scripts/check-no-stale-paths.sh"
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "scripts/check-no-stale-paths.sh"
t = p.read_text(encoding="utf-8")
old = ('    tracked = _ls_files(root)\n'
       '    untracked = _ls_files(root, "--others", "--exclude-standard")\n'
       '    return sorted(tracked | untracked)')
new = ('    tracked = _ls_files(root)\n'
       '    return sorted(tracked)')
assert old in t, "SP-8 mutation 沒生效:找不到 tracked_files() 的兩條呼叫"
p.write_text(t.replace(old, new, 1), encoding="utf-8")
untracked = pathlib.Path(sys.argv[1]) / "untracked-banned-sp8.md"
banned = "plugins/local/dev-" + "flow"
untracked.write_text("測試混入舊路徑(未 git add):~/.claude/" + banned + "/hooks/devflow-exec.sh\n",
                      encoding="utf-8")
PY
expect_local fail check-no-stale-paths.sh "$D" "SP-8 tracked_files() 的 --others/--exclude-standard 呼叫被拿掉(還原成只掃已追蹤檔)+ seed 未追蹤禁字檔(自釘接住,單支腳本靜默綠已修)"

# SP-9:把 _ls_files() 內 subprocess.run 的參數從動態 *extra_args 換成寫死的 6 個
# 哨兵檔 pathspec(SENTINELS 斷言剛好全部命中,不會現形),同時 seed 一個不在這 6
# 個哨兵之列的禁字檔。自釘應咬住 subprocess.run 的動態 pathspec 標記消失。
D=$(seed_sp sp9)
cp "$ROOT/scripts/check-no-stale-paths.sh" "$D/scripts/check-no-stale-paths.sh"
chmod +x "$D/scripts/check-no-stale-paths.sh"
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "scripts/check-no-stale-paths.sh"
t = p.read_text(encoding="utf-8")
old = ('def _ls_files(root, *extra_args):\n'
       '    result = subprocess.run(\n'
       '        ["git", "-C", root, "ls-files", "-z", *extra_args],\n'
       '        capture_output=True,\n'
       '    )')
new = ('SENTINEL_PATHSPEC_SP9 = [\n'
       '    "README.md",\n'
       '    "hooks/devflow-lib.py",\n'
       '    "scripts/build-gate-twin.py",\n'
       '    "guides/guide-dev-flow.html",\n'
       '    "_templates/4-spec.md",\n'
       '    ".claude-plugin/plugin.json",\n'
       ']\n'
       '\n'
       '\n'
       'def _ls_files(root, *extra_args):\n'
       '    result = subprocess.run(\n'
       '        ["git", "-C", root, "ls-files", "-z", "--", *SENTINEL_PATHSPEC_SP9],\n'
       '        capture_output=True,\n'
       '    )')
assert old in t, "SP-9 mutation 沒生效:找不到 _ls_files() 的 subprocess.run 呼叫"
p.write_text(t.replace(old, new, 1), encoding="utf-8")
poison = pathlib.Path(sys.argv[1]) / "observability/devflow-obs.py"
c = poison.read_text(encoding="utf-8")
banned = "plugins/local/dev-" + "flow"
poison.write_text(c + "\n# 測試混入舊路徑(不在 6 個哨兵之列):~/.claude/" + banned + "/hooks/devflow-exec.sh\n",
                   encoding="utf-8")
PY
expect_local fail check-no-stale-paths.sh "$D" "SP-9 _ls_files() 的 pathspec 被換成寫死的 6 個哨兵(SENTINELS 剛好全過)+ seed 非哨兵禁字檔(自釘接住,單支腳本靜默綠已修)"

# seed_mem <name> → 給 check-memory-architecture.sh 用的最小 seed:它讀 .gitignore、
# memory/ 整包、skills/dev-setup/SKILL.md、devflow-contract.json、
# hooks/runtime-capabilities.json,少任何一樣它會 exit 2(fail-closed),
# 那會讓 MEM-0 對照組自己變紅而不是測到東西。
# ⚠️ 守衛以後多讀一個檔,這裡也要跟著補 —— 同 seed_fm 的教訓。
seed_mem() {
  local name="${1:?seed_mem: name is empty}"
  local dst; dst=$(seed "$name")
  cp -r "$ROOT/memory" "$dst/memory"
  mkdir -p "$dst/hooks"
  cp "$ROOT/hooks/runtime-capabilities.json" "$dst/hooks/runtime-capabilities.json"
  cp "$ROOT/skills/dev-setup/SKILL.md" "$dst/skills/dev-setup/SKILL.md"
  [ -f "$ROOT/.gitignore" ] && cp "$ROOT/.gitignore" "$dst/.gitignore"
  cp "$ROOT/scripts/check-memory-architecture.sh" "$dst/scripts/"
  chmod +x "$dst/scripts/check-memory-architecture.sh"
  echo "$dst"
}

# ── FM 群組:檔案地圖雙向盤點守衛(check-file-map.sh)────────────────────────
#
# guides/guide-dev-flow.html「附錄:檔案地圖」節是手寫表,手寫表必腐化。這一組證明
# 守衛真的會抓到兩個方向的漂移:①表少列一支真實存在的檔(forward)②表多寫一個不存在
# 的檔名(reverse)——而不是只在對照組上空轉。
D=$(seed_fm fm0)
expect pass check-file-map.sh "$D" "FM-0 對照組(檔案地圖與現實同步)"

D=$(seed_fm fm1); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "guides/guide-dev-flow.html"
t = p.read_text(encoding="utf-8")
n = re.sub(r'<tr><td><code>selftest\.sh</code></td>.*?</tr>\n', '', t, count=1, flags=re.S)
assert n != t, "FM-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-file-map.sh "$D" "FM-1 檔案地圖刪一列(hooks/selftest.sh 那列被拿掉,檔案仍在 → forward 缺列)"

D=$(seed_fm fm2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "guides/guide-dev-flow.html"
t = p.read_text(encoding="utf-8")
marker = '<tr><td><code>check-file-map.sh</code></td>'
assert marker in t, "FM-2 anchor 不見:check-file-map.sh 那列找不到"
fake = ('<tr><td><code>scripts/does-not-exist-guard.sh</code></td>'
        '<td>假造的檔名,測試反向盤點。</td><td>無</td></tr>\n    ')
n = t.replace(marker, fake + marker, 1)
assert n != t, "FM-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-file-map.sh "$D" "FM-2 檔案地圖加一列指向不存在的檔(reverse 找不到對應檔案)"

# ── FG 群組:兩份導覽的生命週期圖同步守衛(check-guides-fig-sync.sh,X-6)──────
#
# guide-dev-flow.html 的 fig-lifecycle 與 guide-quickstart.html 的 fig-lifecycle-qs
# 是 owner 裁決保留的雙副本(quickstart 要能自足看完整圖,不接受單正本+連結取代)。
# 雙副本天生會漂移——改一張圖裡的文字,另一張沒人會自動跟著改,且改之前完全沒有
# 任何既有檢查會紅(這正是本檔「假綠第⑥型:不對稱保護」要防的案例)。這一組證明
# 守衛真的抓得到:FG-0 兩張圖同步時必須 pass;FG-1 只改 quickstart 那張圖裡一個
# node 的文字(dev-flow 那張不動),必須 fail 並點名差異。
#
# 2026-08-17 補(X-7):守衛新增第三層(三份 guides 共用的頁內錨點捲動 JS),
# guide-dev-talk.html 也要在場,否則新版守衛找不到第三份檔案會 exit 2——
# seed_fg() 一併補齊,FG-0…FG-2 既有案例才不會因為這支新哨兵一起變 exit 2。
seed_fg() { # seed_fg <name> → 同 seed(),另外複製三份導覽 HTML 進 guides/
  local name="${1:?seed_fg: name is empty}"
  local dst; dst=$(seed "$name")
  mkdir -p "$dst/guides"
  cp "$ROOT/guides/guide-dev-flow.html" "$dst/guides/guide-dev-flow.html"
  cp "$ROOT/guides/guide-quickstart.html" "$dst/guides/guide-quickstart.html"
  cp "$ROOT/guides/guide-dev-talk.html" "$dst/guides/guide-dev-talk.html"
  echo "$dst"
}

D=$(seed_fg fg0)
expect pass check-guides-fig-sync.sh "$D" "FG-0 對照組(兩張生命週期圖正規化後一致)"

D=$(seed_fg fg1); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "guides/guide-quickstart.html"
t = p.read_text(encoding="utf-8")
old = '>Session Start<'
new = '>Session Start MUTATED<'
assert t.count(old) == 1, "FG-1 anchor 不是唯一命中,mutation 目標不明確"
n = t.replace(old, new, 1)
assert n != t, "FG-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-guides-fig-sync.sh "$D" "FG-1 quickstart 版 svg 內一個 node 文字被改(dev-flow 版未動,漂移必須現形)"

# FG-2:只改 CSS 規則層(svg 標記不動)。守衛顧的是「svg 標記」與「畫這張圖的 CSS
# 規則」兩層,不是只顧其中一層——這一案專門證明 CSS 這層真的被咬到,不是只在
# svg 那層空轉。
D=$(seed_fg fg2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "guides/guide-quickstart.html"
t = p.read_text(encoding="utf-8")
old = 'svg .hk{fill:color-mix(in srgb,var(--warn) 16%,var(--card));stroke:var(--warn)}'
new = 'svg .hk{fill:color-mix(in srgb,var(--warn) 99%,var(--card));stroke:var(--warn)}'
assert t.count(old) == 1, "FG-2 anchor 不是唯一命中,mutation 目標不明確"
n = t.replace(old, new, 1)
assert n != t, "FG-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-guides-fig-sync.sh "$D" "FG-2 quickstart 版畫圖用的 CSS 規則被改(svg 標記本身沒動,只有渲染規則漂移,一樣必須現形)"

# FG-3(X-7 第三層):三份 guides 共用的頁內錨點捲動 JS,只改其中一份的
# scrollIntoView 選項(quickstart 那份的 behavior 從 smooth 改成 auto,dev-flow/
# dev-talk 兩份不動)。這段 JS 在守衛新增第三層之前完全沒有任何檢查覆蓋——
# worktree 已對舊版驗證過:單改一份 JS,devflow-check 24 組全綠(零守衛),
# 這一案就是證明新增的第三層真的咬得到。
D=$(seed_fg fg3); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "guides/guide-quickstart.html"
t = p.read_text(encoding="utf-8")
old = "{ behavior: 'smooth', block: 'start' }"
new = "{ behavior: 'auto', block: 'start' }"
assert t.count(old) == 1, "FG-3 anchor 不是唯一命中,mutation 目標不明確"
n = t.replace(old, new, 1)
assert n != t, "FG-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-guides-fig-sync.sh "$D" "FG-3 quickstart 版頁內錨點捲動 JS 的 scrollIntoView 選項被改(dev-flow/dev-talk 兩份未動,三份不再逐位元組一致必須現形)"

# FG-4(X-6 HIGH,驗證深度感知抽取修復):對兩份導覽的 fig-lifecycle 區塊「對稱」
# 插入同一段巢狀假 <svg>(兩邊插入點與插入內容逐位元組相同,這部分本身不是漂移),
# 再只對 quickstart 那份、插入點**之後**的一段真實節點文字做單邊修改。
#
# 這一案重現的是 X-6 HIGH 那個「抽取截斷」漏洞:舊版(非貪婪 regex,認第一個
# </svg> 就收工)在插入點就被巢狀假 svg 的 </svg> 截斷,插入點之後的內容(含這裡
# 單邊改掉的真實文字)整段不在抽出來的比對範圍內——worktree 已對舊版驗證過:
# 這組對稱插入+單邊真漂移的組合,舊版會給出假的 PASS(逃逸)。新版深度感知抽取
# 掃到巢狀 <svg> 會直接 fail-closed(exit 2,不嘗試聰明處理、叫人來看),不會被
# 誤判成「一致」,也不會误判成別的東西——這裡只驗證「不再是假 PASS」(expect fail
# 涵蓋 exit 1 與 exit 2 兩種非零結果,見 expect() 的 got=fail 判定)。
D=$(seed_fg fg4); mutate "$D" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1])

INSERT_ANCHOR = ">Session Start</text></g>"
FAKE_SVG = ('<svg class="fake-icon-mut" width="1" height="1">'
            '<rect width="1" height="1"/><text x="0" y="0">x</text></svg>')
DIVERGE_OLD = ">InstructionsLoaded<"
DIVERGE_NEW = ">InstructionsLoaded MUTATED<"

# 對稱插入:兩份導覽的插入點與插入內容逐位元組相同,單獨看這一步不構成漂移。
for relpath in ("guides/guide-dev-flow.html", "guides/guide-quickstart.html"):
    p = root / relpath
    t = p.read_text(encoding="utf-8")
    assert t.count(INSERT_ANCHOR) == 1, f"FG-4 插入錨點在 {relpath} 不是唯一命中"
    n = t.replace(INSERT_ANCHOR, INSERT_ANCHOR + FAKE_SVG, 1)
    assert n != t, f"FG-4 對稱插入沒生效於 {relpath}"
    p.write_text(n, encoding="utf-8")

# 單邊真漂移:只改 quickstart,位置在對稱插入點之後——落在舊版(非貪婪 regex)
# truncated 抽取窗口之外,這正是舊版會逃逸的原因。
p = root / "guides/guide-quickstart.html"
t = p.read_text(encoding="utf-8")
assert t.count(DIVERGE_OLD) == 1, "FG-4 單邊漂移錨點不是唯一命中"
n = t.replace(DIVERGE_OLD, DIVERGE_NEW, 1)
assert n != t, "FG-4 單邊漂移沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-guides-fig-sync.sh "$D" "FG-4 對稱插入巢狀假 svg 後單邊改真實節點文字(驗證深度感知抽取修復:5cabf4e 版此毒是逃逸的假 PASS,修復後必須 fail-closed)"

# FG-5(2026-08-17,二次複審誘餌攻擊常設案例):三份 guides 的頁內錨點捲動 JS
# marker 所在註解收尾 --> 之後,都插入同一段誘餌 <script>/* decoy */</script>
# (三份逐位元組相同,插入本身不構成漂移),再只對 quickstart 那份、誘餌之後的
# 真正 <script> 內容做單邊修改。
#
# 這一案重現的是二次複審者實測的繞法:d1dd5b3 版「找 marker 之後第一個
# <script>」的抽取邏輯,遇到誘餌就會把誘餌本身當成「唯一」的 script 抓走——三份
# 誘餌逐位元組相同,比對通過,真正單邊漂移的內容整段沒被抽到也沒被比對
# (worktree 已驗證:此毒對 d1dd5b3 版是逃逸的假 PASS,exit 0)。修復後的
# extract_anchor_scroll_js() 從收尾 </script> 反向檢查:除空白/換行外不能緊接著
# 又是一個 <script>,偵測到誘餌+真身疊在同一個 anchor 槽位時必須 fail-closed
# (exit 2,不猜先抓到的是誘餌還是真身)。
D=$(seed_fg fg5); mutate "$D" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1])

PREFIX = "一般瀏覽器直開不受影響。\n-->\n"
DECOY = "<script>/* decoy */</script>\n"
OLD_ANCHOR = PREFIX + "<script>"
NEW_ANCHOR = PREFIX + DECOY + "<script>"

for relpath in ("guides/guide-dev-flow.html", "guides/guide-quickstart.html",
                "guides/guide-dev-talk.html"):
    p = root / relpath
    t = p.read_text(encoding="utf-8")
    assert t.count(OLD_ANCHOR) == 1, f"FG-5 插入錨點在 {relpath} 不是唯一命中"
    n = t.replace(OLD_ANCHOR, NEW_ANCHOR, 1)
    assert n != t, f"FG-5 誘餌插入沒生效於 {relpath}"
    p.write_text(n, encoding="utf-8")

# 單邊真漂移:只改 quickstart,位置在誘餌**之後**的真正 <script> 內容裡——這正是
# d1dd5b3 版逃逸的關鍵,誘餌之後的內容從沒被抽到過。
p = root / "guides/guide-quickstart.html"
t = p.read_text(encoding="utf-8")
DIVERGE_OLD = "var id = decodeURIComponent(href.slice(1));"
DIVERGE_NEW = DIVERGE_OLD + " // MUTATED"
assert t.count(DIVERGE_OLD) == 1, "FG-5 單邊漂移錨點不是唯一命中"
n = t.replace(DIVERGE_OLD, DIVERGE_NEW, 1)
assert n != t, "FG-5 單邊漂移沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-guides-fig-sync.sh "$D" "FG-5 三份 guides 的 marker 後都插同一段誘餌 <script>,真正的 JS 被推到誘餌後面再單邊改(二次複審誘餌攻擊重放:d1dd5b3 版此毒是逃逸的假 PASS,修復後必須 fail-closed)"

# ───────────────────────────────── Model Tiering ────────────────────────────
# X-5a HIGH:check-model-tiering.sh 先前只有 fixture 自測(scripts/fixtures/
# model-tiering/ 內 good-*/bad-* 案由腳本自己在自測模式跑),真正對外的「正常模式」
# CLI 路徑(給一個 runs-root 參數去稽核真實 .devflow/runs/ 之類目錄)完全零外部
# 變異覆蓋——若守衛被挖空成永遠印全過,自測模式可能仍會因為內建的
# self_test_failed/断言邏輯被砍而一起失守,沒有任何獨立於守衛本體的紅路徑。
# MT-0/MT-1 補的就是這一層:MT-0 證明「自測模式」這條路徑本身仍是對照組(正常會過);
# MT-1 用 seed_guard 複本 + CLI 參數(而非自測模式)去掃一份外部 bad-first-top
# fixture,證明「正常模式」這條路徑真的會抓到違規、不依賴自測模式的內部斷言。
D=$(seed_guard mt0 check-model-tiering.sh)
mkdir -p "$D/scripts/fixtures"
cp -r "$ROOT/scripts/fixtures/model-tiering" "$D/scripts/fixtures/model-tiering"
expect_local_self pass check-model-tiering.sh "$D" "MT-0 對照組(守衛複本對自己的 fixtures/model-tiering/ 跑自測模式)"

D=$(seed_guard mt1 check-model-tiering.sh)
cp -r "$ROOT/scripts/fixtures/model-tiering/bad-first-top" "$D/external-runs"
expect_local_arg fail check-model-tiering.sh "$D" "$D/external-runs" "MT-1 把 bad-first-top 當外部真實 runs 根,以 CLI 參數餵給守衛複本的正常模式(驗證紅路徑不只活在自測模式內)"

# MT-2(Backlog 補齊,2026-08-17):skip-level(跳級:haiku 失敗直跳 opus,中間無
# sonnet)先前只在自測模式內驗 —— 與 MT-1 同型的 real-mode 外部案例缺席,若正常
# 模式的跳級判定被挖掉,自測模式可能仍綠。比照 MT-1 一字不差的做法補上。
D=$(seed_guard mt2 check-model-tiering.sh)
cp -r "$ROOT/scripts/fixtures/model-tiering/bad-skip-level" "$D/external-runs"
expect_local_arg fail check-model-tiering.sh "$D" "$D/external-runs" "MT-2 把 bad-skip-level 當外部真實 runs 根,以 CLI 參數餵給守衛複本的正常模式(跳級紅路徑同樣不只活在自測模式內)"

# ── MEM 群組:Agent Memory 架構不變量(check-memory-architecture.sh)────────────
#
# memory 的核心分界全是散文規則,退回時所有既有檢查照樣全綠。這一組證明守衛真的
# 抓得到六種退回,而不是在對照組上空轉:
#   MEM-1 把 `.dev-flow/` 也塞進 .gitignore(durable memory 從此完全同步不到)
#   MEM-2 讓失效掃描去碰 knowledge(§10:改一支不相關的檔就讓業務規則變不可信)
#   MEM-3 把 domain 的權威改成程式碼推論贏過 domain expert(全域 code > everything)
#   MEM-4 CLI 長出 init 子指令(第二個安裝器)
#   MEM-5 把帶內容的線索「怎麼部署」塞進剝除清單(「怎麼部署?」從此查不到)
#   MEM-6 評測資料集把中文題全部拿掉(中文檢索退步不會現形)
#   MEM-7 契約檔拿掉 NEEDS_VERIFICATION(STALE 又能以 OK 蒙混)
#   MEM-8 拿掉 status 嚴重度排序(多筆結果無法收斂成最嚴重的)
#   MEM-9  correct() 退回成「固化前就 supersede」(更正失敗時舊值連帶消失)
#   MEM-10 revision 的 mark_durable 挪到寫檔之前(寫檔失敗仍宣稱已耐久)
#   MEM-11 拿掉 durable_check(「記憶真的離開這台機器了嗎」無從複驗)
#   MEM-12 fact 整檔寫回不過 Signal Gate(secret 隨乾淨候選一起進 Git)
#   MEM-13 fact 候選在 durable 寫入前就結案(寫檔失敗後重跑補不回來)
#   MEM-14 event 在寫進 .dev-flow 之前就標 durable(false durability claim)
#   MEM-15 checkpoint 拿掉 require_open(ABORTED 的一輪仍能固化候選)
#   MEM-16 end_session 退回無條件 UPDATE(ABORTED 被覆寫成 CLOSED)
D=$(seed_mem mem0)
expect_local pass check-memory-architecture.sh "$D" "MEM-0 對照組(memory 架構不變量齊)"

D=$(seed_mem mem1); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / ".gitignore"
p.write_text(p.read_text(encoding="utf-8") + ".dev-flow/\n", encoding="utf-8")
PY
expect_local fail check-memory-architecture.sh "$D" "MEM-1 .gitignore 把 .dev-flow/ 也忽略掉(durable memory 不進 Git)"

D=$(seed_mem mem2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/truth.py"
t = p.read_text(encoding="utf-8")
marker = "    touched = []\n"
assert marker in t, "MEM-2 anchor 不見"
n = t.replace(marker, marker + "    for row in store.knowledge(limit=10):\n"
                               "        store.set_overlay(row[\"knowledge_id\"], workspace_id,\n"
                               "                          STALE, \"leak\")\n", 1)
assert n != t, "MEM-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-memory-architecture.sh "$D" "MEM-2 失效掃描去碰 knowledge(domain truth 被檔案指紋規則牽連)"

D=$(seed_mem mem3); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/truth.py"
t = p.read_text(encoding="utf-8")
old = '"domain_expert": 100, "user_confirmed": 95, "business_requirement": 90,'
assert old in t, "MEM-3 anchor 不見"
n = t.replace(old, '"domain_expert": 10, "user_confirmed": 95, "business_requirement": 90,', 1)
assert n != t, "MEM-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-memory-architecture.sh "$D" "MEM-3 domain 權威改成程式碼推論贏(全域 code > everything)"

D=$(seed_mem mem4); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/dev-memory.py"
t = p.read_text(encoding="utf-8")
old = '    sub.add_parser("doctor").set_defaults(func=cmd_doctor)'
assert old in t, "MEM-4 anchor 不見"
n = t.replace(old, '    sub.add_parser("init").set_defaults(func=cmd_setup)\n' + old, 1)
assert n != t, "MEM-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-memory-architecture.sh "$D" "MEM-4 CLI 長出 init 子指令(第二個安裝器)"

D=$(seed_mem mem5); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/cues.py"
t = p.read_text(encoding="utf-8")
old = '    r"怎麼做", r"如何", r"\\bhow (?:to|do)\\b",'
assert old in t, "MEM-5 anchor 不見"
n = t.replace(old, '    r"怎麼做", r"如何", r"怎麼部署", r"\\bhow (?:to|do)\\b",', 1)
assert n != t, "MEM-5 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-memory-architecture.sh "$D" "MEM-5 帶內容的線索進了剝除清單(「怎麼部署?」查不到)"

D=$(seed_mem mem6); mutate "$D" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/fixtures/eval/dataset.json"
d = json.loads(p.read_text(encoding="utf-8"))
d["cases"] = [c for c in d["cases"] if c.get("language") != "zh"]
assert d["cases"], "MEM-6 mutation 把案例清空了"
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
PY
expect_local fail check-memory-architecture.sh "$D" "MEM-6 評測資料集拿掉中文題(中文檢索退步不會現形)"

D=$(seed_mem mem7); mutate "$D" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "devflow-contract.json"
d = json.loads(p.read_text(encoding="utf-8"))
values = d["memory"]["retrieval_status_values"]
assert "NEEDS_VERIFICATION" in values, "MEM-7 anchor 不見"
d["memory"]["retrieval_status_values"] = [v for v in values
                                          if v != "NEEDS_VERIFICATION"]
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
PY
expect_local fail check-memory-architecture.sh "$D" "MEM-7 契約檔拿掉 NEEDS_VERIFICATION(STALE 又能以 OK 蒙混)"

D=$(seed_mem mem8); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/query.py"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^_SEVERITY\s*=\s*\{", "_SEVERITY_DISABLED = {", t, count=1, flags=re.M)
assert n != t, "MEM-8 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-memory-architecture.sh "$D" "MEM-8 拿掉 status 嚴重度排序(多筆結果無法收斂成最嚴重的)"

D=$(seed_mem mem9); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/devtalk.py"
t = p.read_text(encoding="utf-8")
anchor = '        payload["_lineage_reason"] = reason\n'
assert anchor in t, "MEM-9 anchor 不見"
# 把「固化成功前就把舊值標 SUPERSEDED」種回去 —— 這就是被修掉的那個缺陷本體
injected = (
    '        store.upsert_knowledge({\n'
    '            "knowledge_id": previous["knowledge_id"], "kind": kind,\n'
    '            "key": key, "title": previous["title"],\n'
    '            "body": previous["body"],\n'
    '            "authority": previous["authority"], "status": "SUPERSEDED",\n'
    '            "confidence": previous["confidence"],\n'
    '            "recorded_at": previous["recorded_at"],\n'
    '            "superseded_at": now, "evidence": [], "conflicts": [],\n'
    '            "implemented": None,\n'
    '            "durable": bool(previous["durable"])})\n')
p.write_text(t.replace(anchor, anchor + injected, 1), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-9 correct() 在固化成功前就 supersede 舊值(更正失敗時兩邊都沒有現況)"

D=$(seed_mem mem10); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
i_write = t.find("durable.append_events(")
i_mark = t.find("lineage.mark_durable(")
assert 0 <= i_write < i_mark, "MEM-10 anchor 順序不符(正向早已紅)"
# 只搬 mark_durable 那一行到 append_events 之前:內容都在,唯一的錯是順序
line_start = t.rfind("\n", 0, i_mark) + 1
line_end = t.find("\n", i_mark) + 1
moved = t[line_start:line_end]
t = t[:line_start] + t[line_end:]
i_write = t.find("durable.append_events(")
ins = t.rfind("\n", 0, i_write) + 1
p.write_text(t[:ins] + moved + t[ins:], encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-10 revision 的 mark_durable 挪到寫檔之前(寫檔失敗仍宣稱已耐久)"

D=$(seed_mem mem11); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
assert "durable_check" in t, "MEM-11 anchor 不見"
p.write_text(t.replace("durable_check", "_unused_check"), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-11 拿掉 durable_check(收尾無從複驗記憶是否真的離開本機)"

D=$(seed_mem mem12); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
i = t.find("def promote_entity_facts(")
j = t.find("\ndef ", i + 1)
assert i >= 0 and j > i, "MEM-12 anchor 不見"
body = t[i:j]
assert "signal.gate(" in body, "MEM-12 anchor:promote_entity_facts 本來就沒 gate"
# 只把整檔寫回的那道 gate 拔掉(其餘 gate 原封不動)—— 這正是被修掉的洩漏路徑
p.write_text(t[:i] + body.replace("signal.gate(", "_no_gate(", 1) + t[j:],
             encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-12 fact 整檔寫回不過 Signal Gate(同 entity 的未檢查鄰居隨乾淨候選進 Git)"

D=$(seed_mem mem13); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = "            fact_candidates.setdefault(\n"
assert anchor in t, "MEM-13 anchor 不見"
# 把 fact 候選在 durable 寫入**之前**就結案(其餘完全不動)——
# 這正是被修掉的缺陷:write_state 失敗後重跑再也看不到這筆候選。
injected = ('            store.set_candidate_status(\n'
            '                candidate["candidate_id"], "CONSOLIDATED", now=now)\n')
p.write_text(t.replace(anchor, injected + anchor, 1), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-13 fact 候選在 durable 寫入前就結案(寫檔失敗後重跑補不回來)"

D=$(seed_mem mem14); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
# 限定在 consolidate 窗口內:rebuild_local 也有 store.add_event(,
# 拿全檔第一個位置比會永遠不成立。
i_cons = t.find("def consolidate(")
assert i_cons >= 0, "MEM-14 anchor:找不到 consolidate"
i_add = t.find("store.add_event(", i_cons)
i_append = t.find("durable.append_events(", i_cons)
assert 0 <= i_append < i_add, "MEM-14 anchor 順序不符(正向早已紅)"
anchor = "            event_candidates.append((candidate[\"candidate_id\"], {\n"
assert anchor in t, "MEM-14 anchor 不見"
# local 事件在 append_events 之前就被標 durable=1 —— 一句沒有憑據的「已耐久」
injected = ('            store.add_event(\n'
            '                payload.get("kind", "important_discovery"), title, body,\n'
            '                session_id=candidate["session_id"], signal=signal.HIGH,\n'
            '                durable=True, event_id=event_id)\n')
p.write_text(t.replace(anchor, injected + anchor, 1), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-14 event 在寫進 .dev-flow 之前就標 durable(false durability claim)"

D=$(seed_mem mem15); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/session.py"
t = p.read_text(encoding="utf-8")
i = t.find("def checkpoint(")
j = t.find("\ndef ", i + 1)
assert i >= 0 and j > i, "MEM-15 anchor 不見"
body = t[i:j]
assert "require_open(" in body, "MEM-15 anchor:checkpoint 本來就沒 require_open"
# 只拔掉 checkpoint 的 fail-closed 檢查(observe 的那道原封不動)
p.write_text(t[:i] + body.replace("    require_open(store, session_id)\n", "", 1)
             + t[j:], encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-15 checkpoint 拿掉 require_open(ABORTED 的一輪仍能把候選寫進 Git)"

D=$(seed_mem mem16); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/store.py"
t = p.read_text(encoding="utf-8")
anchor = "                \" WHERE session_id=? AND status='OPEN'\",\n"
assert anchor in t, "MEM-16 anchor 不見"
# 退回無條件 UPDATE:abort 之後的 end 會把 ABORTED 覆寫成 CLOSED
p.write_text(t.replace(anchor, '                " WHERE session_id=?",\n', 1),
             encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-16 end_session 退回無條件 UPDATE(ABORTED 被覆寫成 CLOSED)"

D=$(seed_mem mem17); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/durable.py"
t = p.read_text(encoding="utf-8")
anchor = '    for path, text in plans:\n        _atomic_write(path, text)'
assert anchor in t, "MEM-17 anchor 不見"
# 退回 append 模式:同一個 event_id 重跑會變成第二行(JSONL 不是 keyed
# storage),而 durable 寫入成功、local 狀態還沒前進那個視窗消不掉。
p.write_text(t.replace(
    anchor,
    '    for path, text in plans:\n        open(path, "a").write(text)', 1),
    encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-17 event append 退回 append 模式(重跑把同一筆寫成第二行)"

D=$(seed_mem mem18); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = ('        record.setdefault("event_id",\n'
          '                          _derived_id("event", row["revision_id"]))')
assert anchor in t, "MEM-18 anchor 不見"
# 退回隨機 id:去重的依據是 event_id,隨機 id 讓去重永遠對不上 ——
# 同一次 supersede 會在 events/ 累積成 N 筆,每筆都聲稱是它。
p.write_text(t.replace(
    anchor, '        record.setdefault("event_id", ids.new_id("event"))', 1),
    encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-18 revision event_id 退回隨機(重跑補寫成第二筆,去重對不上)"

D=$(seed_mem mem19); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = ('    entities_touched.update(\n'
          '        store.entities_pending_durable(sorted(_FACT_STATUS_DURABLE)))')
assert anchor in t, "MEM-19 anchor 不見"
# 只讓候選碰到的 entity 被重寫:`verify --observed` 不建候選,於是它產生的
# 新 current truth 永遠不會離開這台機器,而 local 說它 VERIFIED。
p.write_text(t.replace(anchor, "    pass", 1), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-19 consolidate 只重寫候選碰到的 entity(reverify 的新現況留在本機)"

D=$(seed_mem mem20); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = ('    pending_facts = store.entities_pending_durable(\n'
          '        sorted(_FACT_STATUS_DURABLE))')
assert anchor in t, "MEM-20 anchor 不見"
# durable-check 只報「歷史沒落地」:於是「revision 寫成功、現況檔沒重寫」
# 會判 PASS —— 後者變成靜默的。
p.write_text(t.replace(anchor, "    pending_facts = []", 1), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-20 durable-check 漏掉現況沒落地(只報歷史,現況靜默)"

D=$(seed_mem mem21); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/truth.py"
t = p.read_text(encoding="utf-8")
anchor = "    if changed or dirty or unproven:"
assert anchor in t, "MEM-21 anchor 不見"
# 把解析不完整那一項從 STALE 判斷式裡拿掉:git status 有讀不懂的欄位時
# dirty 清單不完整,而沒有指紋可比的依賴只剩 dirty 能證明它乾淨 ——
# 判斷式少了它就仍然回 OK fast path。
p.write_text(t.replace(anchor, "    if changed or dirty:", 1), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-21 解析不完整不進 STALE 判斷(unknown workspace 仍回 OK fast path)"

D=$(seed_mem mem22); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = ('    facts = store.facts(entity_type=entity_type, entity_key=entity_key,\n'
          '                        statuses=sorted(_FACT_STATUS_DURABLE), limit=None)')
assert anchor in t, "MEM-22 anchor 不見"
# 把筆數視窗放回去:整檔取代會把視窗外的 fact 從 `.dev-flow/` 刪掉,而它們
# 在 local 仍標 durable=1 —— durable-check 判 PASS 在不完整的鏡射上。
p.write_text(t.replace(
    anchor,
    '    facts = [f for f in store.facts(entity_type=entity_type,\n'
    '                                    entity_key=entity_key, limit=1000)\n'
    '             if f["status"] in _FACT_STATUS_DURABLE]', 1),
    encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-22 durable 現況檔整檔取代時設筆數視窗(視窗外的現行 fact 被刪掉)"

D=$(seed_mem mem23); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/durable.py"
t = p.read_text(encoding="utf-8")
anchor = '                if seen[event_id] != line:'
assert anchor in t, "MEM-23 anchor 不見"
# 撞號退回靜默跳過:同 id 不同內容時第二筆永遠不存在,而呼叫端拿到成功。
i = t.find(anchor)
j = t.find("                continue", i)
assert j > i, "MEM-23 window 不見"
p.write_text(t[:i] + t[j:], encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-23 event 撞號退回靜默跳過(同 id 不同內容的第二筆永遠不存在)"

D=$(seed_mem mem24); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = ('        remote_head, code, error, preflight_not_known_local = '
          '_observe_remote(\n            repo_root, branch or "")')
assert anchor in t, "MEM-24 anchor 不見"
# 退回本機追蹤 ref:別台機器改掉遠端之後它還指著我的 commit,於是這一關
# 會替一個伺服器上已經不存在的 commit 背書。
p.write_text(t.replace(
    anchor,
    '        remote_head, code, error, preflight_not_known_local = (\n'
    '            identity._git(repo_root, "rev-parse", upstream),\n'
    '            None, None, True)', 1),
    encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-24 durable-check 退回本機追蹤 ref(遠端被改掉仍判 PASS)"

D=$(seed_mem mem24b); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = '''    if problems:
        verdict = "FAIL"
    elif remote_ref_matches:
        verdict = "PASS"
    else:
        verdict = "LOCAL_ONLY_PASS"'''
assert anchor in t, "MEM-24b anchor 不見"
# 把三值壓回兩值:--local-only(走本機追蹤 ref,伺服器從沒被問過)與真的
# 觀察過遠端共用同一個 PASS,只讀 verdict 的呼叫端因此分不出兩者。
p.write_text(t.replace(anchor, '''    if problems:
        verdict = "FAIL"
    else:
        verdict = "PASS"''', 1), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-24b durable-check verdict 把 local-only 壓回一般 PASS(呼叫端分不出強弱)"

D=$(seed_mem mem24c); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = "    elif remote_ref_matches:"
assert anchor in t, "MEM-24c anchor 不見"
# LOCAL_ONLY_PASS 這個字串留著,但 PASS 改由呼叫端傳進來的旗標決定 ——
# remote_ref_matches 退化成只是附註的死碼(守衛不能被自己要檢查的字串餵飽)。
p.write_text(t.replace(anchor, "    elif not local_only:", 1),
             encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-24c durable-check 的 PASS 改由 local_only 旗標決定(誠實欄位變死碼)"

D=$(seed_mem mem24d); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = ('        "remote_ref_matches": remote_ref_matches,\n'
          '        "preflight_not_known_local": '
          'bool(preflight_not_known_local),\n')
assert anchor in t, "MEM-24d anchor 不見"
# 兩個誠實欄位從回傳 dict 拿掉:呼叫端只能 .get(),而 None 在布林語境下
# 與 False 同義 —— 少一個欄位會靜默降級成某一邊,取決於呼叫端怎麼寫。
p.write_text(t.replace(anchor, "", 1), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-24d durable-check 的誠實欄位從必填降成缺席(呼叫端靜默降級)"

D=$(seed_mem mem25); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = "    if not identity.remote_is_offmachine(url):"
assert anchor in t, "MEM-25 anchor 不見"
# 拿掉「remote 在別台機器上嗎」這一問:本機 bare repo / file:// / localhost
# 都會讓 ls-remote 回報正確的 SHA,於是判 PASS 而記憶跟工作樹在同一顆硬碟上。
i = t.find(anchor)
j = t.find("    raw = identity._git_raw(", i)
assert j > i, "MEM-25 window 不見"
p.write_text(t[:i] + t[j:], encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-25 durable-check 收本機 remote 當離開本機的證據"

D=$(seed_mem mem26); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/query.py"
t = p.read_text(encoding="utf-8")
anchor = '        row = store.decision_row(hit["item_id"])'
assert anchor in t, "MEM-26 anchor 不見"
# 退回「掃最近 200 筆找已知主鍵」:命中視窗外的 decision 時 reason 撈不到,
# 而 _why 仍然把它算成 decision、仍然回 OK。
p.write_text(t.replace(
    anchor,
    '        row = next((d for d in store.decisions(limit=200)\n'
    '                    if d["decision_id"] == hit["item_id"]), None)', 1),
    encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-26 WHY 用「最近 N 筆」撈已知主鍵(視窗外的 reason 撈不到仍回 OK)"

D=$(seed_mem mem27); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = "    host = identity._parse_host(url)"
assert anchor in t, "MEM-27 anchor 不見"
# 拿掉「host 解析後的位址是不是這台機器自己」這一問:URL 形狀判定過關的
# remote(remote_is_offmachine 只看字面 host)可能被 /etc/hosts 或內網 DNS
# 重映到 127.0.0.1 或這台機器自己的介面,ls-remote 一樣回報正確的 SHA。
i = t.find(anchor)
j = t.find("    raw = identity._git_raw(", i)
assert j > i, "MEM-27 window 不見"
p.write_text(t[:i] + t[j:], encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-27 durable-check 沒有解析 remote 主機名的實際位址(具名主機重映到本機仍判 PASS)"

D=$(seed_mem mem28); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/store.py"
t = p.read_text(encoding="utf-8")
anchor = '''def db_path(project_id, worktree_key):
    return os.path.join(project_home(project_id), WORKTREE_DIR,
                        _require_worktree_key(worktree_key), DB_NAME)'''
assert anchor in t, "MEM-28 anchor 不見"
# 簽名還收 worktree_key,路徑卻退回專案級共用檔:兩個 worktree 再次寫進
# 同一份 memory.db,而呼叫端看起來已經「傳了 worktree」。
p.write_text(t.replace(
    anchor,
    "def db_path(project_id, worktree_key):\n"
    "    return os.path.join(project_home(project_id), DB_NAME)", 1),
    encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-28 db_path 收下 worktree_key 卻仍指向專案級共用檔"

D=$(seed_mem mem28b); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/store.py"
t = p.read_text(encoding="utf-8")
anchor = '''        if path is None:
            if worktree_key is None:
                raise ValueError(
                    "Store.open 必須給 worktree_key 或 path——"
                    "只給 project_id 會讓兩個 worktree 共用同一份可變 SQLite")
            target = db_path(project_id, worktree_key)
        else:
            target = path'''
assert anchor in t, "MEM-28b anchor 不見"
# 缺 worktree_key 時退回舊的專案級路徑:一個忘記改的呼叫點就讓隔離失效。
p.write_text(t.replace(
    anchor,
    "        if path is None:\n"
    "            target = legacy_shared_db_path(project_id)\n"
    "        else:\n"
    "            target = path", 1),
    encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-28b Store.open 缺 worktree_key 時退回專案級共用檔"

D=$(seed_mem mem29); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/query.py"
t = p.read_text(encoding="utf-8")
anchor = '''    if extra:
        payload.update(extra)
    # D-4:必填。extra 可以填內容,但不能讓欄位缺席或變成 None ——
    # 呼叫端寫 .get() 時 None 與「空」同義,少一個欄位就靜默降級。
    if "per_coordinate" not in payload or payload["per_coordinate"] is None:
        payload["per_coordinate"] = []
    return payload'''
assert anchor in t, "MEM-29 anchor 不見"
# 拿掉 extra merge 之後的必填回填:欄位變成 extra 高興才附上,
# 呼叫端只能 .get(),None 與空同義。
p.write_text(t.replace(
    anchor,
    "    if extra:\n"
    "        payload.update(extra)\n"
    "    return payload", 1),
    encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-29 envelope 拿掉必填 per_coordinate(呼叫端只能 .get())"

D=$(seed_mem mem29b); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/query.py"
t = p.read_text(encoding="utf-8")
anchor = "    coords = _per_coordinate(resolved)"
assert anchor in t, "MEM-29b anchor 不見"
# 函式還在、字串還在,但 CURRENT 改寫死空列表 —— 守衛不能被自己要
# 檢查的那個字串餵飽。entity-only 聚合降級時明細消失。
p.write_text(t.replace(anchor, "    coords = []", 1), encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-29b CURRENT 的 per_coordinate 寫死空列表(_per_coordinate 變死碼)"

D=$(seed_mem mem30); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = "        kind, entries = _snapshot_durable_files(repo_root)"
assert anchor in t, "MEM-30 anchor 不見"
# 退回只觀察活樹兩端:函式還在、字串還在,但 rebuild_local 不再消費快照。
n = t.replace(anchor, "        kind, entries = None, None", 1)
n = n.replace(
    "        generation_before = _generation_of(kind, entries)",
    "        generation_before = durable_generation(repo_root)", 1)
assert n != t, "MEM-30 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-30 rebuild 退回只比對活樹兩端雜湊(ABA 混鏡射可蓋章)"

D=$(seed_mem mem31); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/setup.py"
t = p.read_text(encoding="utf-8")
anchor = '            "level": freshness_level, "check": "durable-mirror-freshness",'
assert anchor in t, "MEM-31 anchor 不見"
n = t.replace(anchor, '            "level": freshness_level, "check": "durable-mirror-stale",', 1)
assert n != t, "MEM-31 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-31 doctor 拿掉 durable-mirror-freshness 檢查名"

D=$(seed_mem mem32); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/embedding.py"
t = p.read_text(encoding="utf-8")
anchor = "        missing = store.embedding_missing(*sig)"
assert anchor in t, "MEM-32 anchor 不見"
n = t.replace(anchor, "        missing = 0", 1)
assert n != t, "MEM-32 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-32 mismatch_report 不再呼叫 embedding_missing"

D=$(seed_mem mem33); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = '                raise durable.DurableError(\n                    "unreadable durable file {0}".format(rel)) from exc'
assert anchor in t, "MEM-33 anchor 不見"
n = t.replace(
    anchor,
    "                data = None",
    1)
assert n != t, "MEM-33 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-33 snapshot 把 OSError 收成 data=None"

D=$(seed_mem mem34); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/sync.py"
t = p.read_text(encoding="utf-8")
anchor = "    store.set_meta(DURABLE_GENERATION_META, UNCERTIFIED_GENERATION)\n"
assert anchor in t, "MEM-34 anchor 不見"
n = t.replace(anchor, "", 1)
assert n != t, "MEM-34 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-34 rebuild 不再先撤銷世代認證"

D=$(seed_mem mem35); mutate "$D" <<'PYX'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "memory/agentmem/embedding.py"
t = p.read_text(encoding="utf-8")
anchor = "        needs = bool(mismatched or missing or orphaned)"
assert anchor in t, "MEM-35 anchor 不見"
n = t.replace(anchor, "        needs = bool(mismatched or missing)", 1)
assert n != t, "MEM-35 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PYX
expect_local fail check-memory-architecture.sh "$D" "MEM-35 mismatch_report 不再把 orphaned 算進 needs"

# ─────────────────────────────────── 結果 ───────────────────────────────────
printf '%s\n' "${RESULTS[@]}"
echo

FP_AFTER=$(fingerprint)
if [ "$FP_BEFORE" != "$FP_AFTER" ]; then
  echo "⛔ 正式 repo 指紋改變了 —— 測試污染了 working tree,這本身就是失敗" >&2
  exit 1
fi
echo "  ✓ 正式 repo 指紋未變($FP_BEFORE)—— working tree 零污染"
echo


# ── 靜態互釘:五支散落地板 + check-gate-twin.sh 的群組數釘(HIGH,獨立審查
# 2026-08-16 finding 4;check-file-map.sh 的 MIN_CHECKS 為第五支,補上是本節
# 「對稱」主題的落實——別的地板都有靜態釘,它原本沒有;check-gate-twin.sh 的
# EXPECTED_GROUPS 則是「群組數」這條軸第一次補上地板 + 靜態釘,對稱於檢查數軸
# 早就有的 MIN_CHECKS + 這份清單——群組被連刪帶藏(區塊 + REQUIRED_GROUPS 條目
# 一起刪、補填充檢查數湊 CHECKS)時,heartbeat 與 guard-selfpin 兩層都看不到,
# 只有這個釘死的字面數字會現形)
# ────────────────────────────────────────────────────────────────────────────
# ⚠️ 這**不是**一個 GS 編號案例 —— 不 seed、不 mutate、不呼叫 expect_local,不計入
# EXPECTED_CONTROLS/NEGATIVES/TOTAL(這三個數字加了它之後不動,是設計如此,
# 不是漏算;見本檔檔頭「涵蓋」清單的「靜態互釘」條目)。
# 為什麼:MIN_CHECKS/MIN_CASES/EXPECTED_CHECKS 這類「檢查數地板」是防砍檢查的
# 最後一道牆,但牆本身沒有牆——同時砍案例數與地板數字(連刪帶藏,兩處一起改)
# 完全防不住。GS-4 對 check-design-contract.sh 的防法是在**該檔自己內部**釘死
# `check(MIN_CHECKS == 100, ...)`;盤點到的其餘地板 —— hooks/selftest.sh 的
# MIN_CASES、tests/parallel-stage6/run_tests.py 的 EXPECTED_CHECKS、
# check-dev-setup-discipline.sh、check-gate-twin.sh 與 check-file-map.sh 的
# MIN_CHECKS —— 所在檔案都沒有那層自我釘死,沒抄到 GS-4 的前例。這裡補上:在
# **另一個獨立檔案**(本檔)對這五支地板的字面值各釘一條 grep 斷言 —— 這份清單
# 本身是會被 review 到的 diff,誰要調動地板就得同步改這裡,只改一邊會在這裡現形。
# ⚠️ 誠實承認防禦邊界:連改三處(案例本身 + 地板數字 + 這裡的靜態釘)仍防不住
# —— 這跟 GS-4 是同一個等級的防禦,防的是「單點手滑」(改了案例忘了改地板,
# 或反過來改了地板卻忘了同步這裡的靜態釘),不是「蓄意繞過同時改三處」的攻擊者。
STATIC_PIN_FAIL=0
check_static_pin() { # check_static_pin <相對路徑> <期望逐字一整行> <說明>
  # 逐字整行存在只證明「那一行還在檔案裡」,防不住「同名變數第二行賦值覆蓋」——
  # Python/bash 都是後面的賦值語意上蓋掉前面那行,例如在 `EXPECTED_GROUPS = 24`
  # 下面偷加一行 `EXPECTED_GROUPS = 25`,逐字行比對兩行都在、都比對得到,完全
  # 看不出「實際生效值」已經漂走(X-3 HIGH-2,獨立審查實測繞過)。這裡多一層:
  # 從期望行抽出變數名,數整檔裡這個變數名被賦值幾次,必須恰為 1。
  # ⚠️ 誠實承認邊界:這只防「加一行」這種手滑,不防同時改本檔(這條計數規則本身)
  # 的蓄意繞過者——蓄意者可以連這條計數規則一起改掉,跟 check_static_pin 原本
  # 「只防單點手滑,不防蓄意連改」的邊界完全一樣,沒有放寬也沒有收緊。
  #
  # ⚠️ 二次複審(X-3 再犯):上面這層原本用 `grep -cE "^VAR[[:space:]]*="` 行首
  # 錨定計數——縮排區塊裡的重綁(例如 `if True:` 底下縮排一格再賦值一次)或同一
  # 實體行內用 `;`/`:` 接的第二次賦值,行首都對不上錨點,舊版完全數不到第二次
  # 賦值,等於這層防線形同虛設(worktree 實測重現:對 check-gate-twin.sh 加一行
  # `if True: EXPECTED_GROUPS = 23`,舊版計數仍是 1,靜態釘照樣綠燈)。
  # 修法:錨點改成「這個變數名出現在陳述式起始位置」——起始位置定義為行首(可有
  # 縮排)或緊接在 `;`/`:` 之後(可有空白),而不要求整行只能是這個賦值。同時排除
  # `==`(比較不算賦值)。
  # ⚠️ 基線實測(六支釘各自的目標檔):純「排除註解行」不足夠——hooks/selftest.sh
  # 與 check-file-map.sh 各有一行**診斷訊息**用同名變數組字串(例如
  # `"...地板 MIN_CASES=$MIN_CASES..."`、`f"...MIN_CHECKS={MIN_CHECKS}..."`),不是
  # 註解、也不是第二次賦值,但字面上一樣命中「VAR 後接空白再一個 =」,若只排除
  # 註解行會被算成假紅(2 次)。這類訊息的共同特徵是「VAR=」出現在字串/訊息中段,
  # 不在陳述式起始位置——上面這條「起始位置錨點」同時解決了這個問題,不需要另外
  # 用「排除 $/{ 開頭的右值」這種會narrow 掉真賦值(例如 `VAR=$(cmd)`)的權宜法。
  # 仍額外排除整行都是註解(`#` 開頭,含縮排)的行,雙重保險。
  local rel="$1" expect_line="$2" label="$3"
  local file="$ROOT/$rel"
  if ! grep -qxF "$expect_line" "$file" 2>/dev/null; then
    echo "  ✗ 靜態互釘:$rel 的 $label —— 找不到逐字一行「${expect_line}」" \
         "(地板可能被調動,但這裡的靜態釘沒有同步更新,或案例被砍卻沒調地板)"
    STATIC_PIN_FAIL=1
    return
  fi
  local varname n
  varname=$(printf '%s' "$expect_line" | grep -oE '^[A-Za-z_][A-Za-z0-9_]*')
  # 群組名這類「整行釘」(見下方 REQUIRED_GROUP_NAMES 迴圈)期望行不是以識別字開頭
  # (例如 `    "gate-stage-baseline",`),抽不出變數名——這種情況不是「VAR = 值」
  # 宣告,不適用賦值覆蓋計數這層,只要逐字整行存在(上面已檢查過)就算過。
  if [ -n "$varname" ]; then
    n=$(grep -E "(^|[:;])[[:space:]]*${varname}[[:space:]]*=[^=]" "$file" 2>/dev/null \
        | grep -vcE '^[[:space:]]*#')
    if [ "$n" -ne 1 ]; then
      echo "  ✗ 靜態互釘:$rel 的 $label —— 變數 ${varname} 在檔案中被賦值 ${n} 次(應恰為 1)" \
           "(疑似同名第二次賦值覆蓋前一次,Python/bash 都是後面蓋掉前面,逐字行比對本身抓不到這種漂移)"
      STATIC_PIN_FAIL=1
      return
    fi
  fi
  echo "  ✓ 靜態互釘:$rel 的 $label"
}
# check_static_pin 要求「逐字一整行」,抓不到「識別字面只是某一行的一段子字串,
# 該行前後還有別的字元(例如 `check(` 前綴、結尾逗號)」這種情況——這種釘法用
# check_static_pin_sub(grep -qF 子字串版)。分工:整行不變 → check_static_pin;
# 只保住行內某段識別字面、行的其餘部分(縮排/前綴/結尾標點)可以變 → check_static_pin_sub。
# 子字串版天生比整行版寬鬆,不重跑「賦值覆蓋計數」那層(子字串比對的對象通常是斷言
# 運算式或清單項目,不是「VAR = 值」這種可被第二行覆蓋的宣告,不適用同一種計數判準)。
check_static_pin_sub() { # check_static_pin_sub <相對路徑> <期望子字串> <說明>
  local rel="$1" expect_sub="$2" label="$3"
  if grep -qF "$expect_sub" "$ROOT/$rel" 2>/dev/null; then
    echo "  ✓ 靜態互釘(子字串):$rel 的 $label"
  else
    echo "  ✗ 靜態互釘(子字串):$rel 的 $label —— 找不到子字串「${expect_sub}」" \
         "(識別字面可能被改寫或整段被刪)"
    STATIC_PIN_FAIL=1
  fi
}
check_static_pin "hooks/selftest.sh" "MIN_CASES=402" "MIN_CASES 釘死 402(2026-08-17 清空輪 378 之後,2026-08-19 §7 前置修復:s7 legacy sequential 真跑 start 驗證+6/s7b VNext feature-scope 同型驗證+2/s7c Stage 7 review 自建武裝同型驗證+3 → 389,同日 §7-3b 探針 pst 真實 subagent_type payload 形狀釘住+3 → 392,2026-08-20 issue #7 路徑分隔符 w1 組+6 → 398,同日派工單 §2.1 TMPDIR 跨平台正規化 w2 組+2 → 400,同日 report-guard 覆蓋缺口+2 → 402)"
check_static_pin "tests/parallel-stage6/run_tests.py" "EXPECTED_CHECKS = 131" "EXPECTED_CHECKS 釘死 131"
check_static_pin "scripts/check-dev-setup-discipline.sh" "MIN_CHECKS = 18" "MIN_CHECKS 釘死 18(A-2/B-5 輪:②改 scoped 拆 3 條 + ⑦⑧⑨ 新增 → 15;2026-08-20 ⑩check 段散發副本 parity map-driven 拆 3 條 → 18)"
check_static_pin "scripts/check-gate-twin.sh" "MIN_CHECKS = 138" "MIN_CHECKS 釘死 138(X-3 補群組數釘之後的實得數)"
check_static_pin "scripts/check-integration-regression-guard.sh" "MIN_CHECKS = 41" "MIN_CHECKS 釘死 41(反證輪 E-1:再加 M-f~M-h 五個(mutant,子案)配對後的實得數)"
check_static_pin "scripts/check-status-policy.sh" "MIN_CHECKS = 35" "MIN_CHECKS 釘死 35(durability-barrier 輪:W6 耐久性鏈的負向⑳㉑㉒ 三案後的實得數)"
check_static_pin "scripts/check-file-map.sh" "EXPECTED_MAPPED_FILES = 135" "EXPECTED_MAPPED_FILES 釘死 135(精確值,不是地板;2026-08-21 D-1 加 test_worktree_store.py 後的實得數)"
check_static_pin "scripts/check-gate-twin.sh" "EXPECTED_GROUPS = 24" "EXPECTED_GROUPS 釘死 24(REQUIRED_GROUPS 實際長度;群組數軸的靜態釘)"

# 第七支地板(二次複審,GS-9 區補上):check-design-contract.sh 的
# EXPECTED_CHECK_SKIP_CALLS 是「顯性跳過 check() 次數」的釘死地板(見該檔第 480、
# 612 行的 check() 呼叫),盤點時漏掉、沒有比照其餘六支補上這裡的靜態釘,是「同型
# 病灶在新守衛裡再犯」的一種:別的地板都有這一層外部互釘,它原本沒有。
check_static_pin "scripts/check-design-contract.sh" "EXPECTED_CHECK_SKIP_CALLS = 1" "EXPECTED_CHECK_SKIP_CALLS 釘死 1"

# X-3 HIGH-1:上面只釘了 EXPECTED_GROUPS 這個常數宣告本身,沒釘「用它的斷言」——
# guard-selfpin 整區塊(含這兩條 meta 斷言)連同 REQUIRED_GROUPS 對應條目一起被刪掉、
# 再補等量填充檢查湊 CHECKS 數時,EXPECTED_GROUPS 常數字面依然原封不動躺在檔案裡,
# 上面那條靜態釘照樣綠燈,heartbeat/guard-selfpin 兩層防線也都被連根拔起,完全看
# 不出來。這裡直接釘兩條斷言運算式本身的識別字面(不是整行,行首縮排/前綴/結尾逗號
# 都可能不同,故用子字串版):斷言消失 = 這裡先紅。
check_static_pin_sub "scripts/check-gate-twin.sh" "len(REQUIRED_GROUPS) == EXPECTED_GROUPS" \
  "群組數斷言 len(REQUIRED_GROUPS) == EXPECTED_GROUPS 仍在原始碼中"
check_static_pin_sub "scripts/check-gate-twin.sh" "_assigned == set(REQUIRED_GROUPS)" \
  "guard-selfpin 斷言 _assigned == set(REQUIRED_GROUPS) 仍在原始碼中"

# X-3 MED:上面兩條只釘「斷言在不在」,群組總數對不對,但 REQUIRED_GROUPS 清單裡
# 個別群組名被改名(decoy 換掉真名、總數與賦值集合等式都不受影響)完全抓不到。這裡
# 逐一釘死 24 個群組名——清單住在本檔(誰要改名/刪名都得同步這裡,否則這裡會現形;
# check-gate-twin.sh 原始碼裡的順序跟這裡不必一致,逐一比對即可)。
# ⚠️ 二次複審(X-3 再犯):原本用 check_static_pin_sub(子字串版,只驗
# `"名字",` 這段字面存在)——子字串比對不管這段字面出現在**哪裡**,名字被拿出
# REQUIRED_GROUPS 清單、改藏進一行 `# "n4-unclosed-comment",` 這種註解裡,子字串
# 「"n4-unclosed-comment",」照樣命中,靜態釘照樣綠燈(worktree 實測重現:REQUIRED_
# GROUPS 刪掉該條目、但把同樣字面留在註解裡,舊版子字串釘不會叫)。
# 修法:改成逐字整行釘(check_static_pin 的 grep -qxF 版),期望行是 REQUIRED_GROUPS
# 清單裡的真實縮排(4 個空白)與尾逗號,例如 `    "gate-stage-baseline",`——名字
# 只活在註解裡時,這行不存在,grep -qxF 找不到逐字整行,直接現形;不像子字串版,
# 「行的其餘部分是不是清單項目」完全不驗。
# ⚠️ 誠實承認剩餘邊界:這只抓「名字被換掉/被搬出清單」,抓不到「保留群組名、把
# 該群組底下的檢查內容掏空換填充」——那屬語意層,由各群組對應的 fixture 正負向
# 案例管,不是這裡的職責。
REQUIRED_GROUP_NAMES=(
  "gate-stage-baseline" "dash-cells-readme" "risk-cell-count" "cross-file-parity"
  "p4-fence-section" "s-head-regression" "h2-zero-deletion" "t6-pinned"
  "t2-missing-required" "k7-missing-then" "k3-missing-intent" "k3-empty-tasks"
  "k3-task-count" "k3-boundaries-dag" "high2-dash-values" "high3-dag-waves"
  "high1-dup-field" "p5-sample-row" "t5-empty-spec" "n7-dist-copy"
  "n1-section-fate" "n4-unclosed-comment" "usage-error-message" "guard-selfpin"
)
for _gname in "${REQUIRED_GROUP_NAMES[@]}"; do
  check_static_pin "scripts/check-gate-twin.sh" "    \"${_gname}\"," \
    "REQUIRED_GROUPS 群組名 ${_gname} 逐字整行仍在原始碼中(非藏在註解裡)"
done
unset _gname

# ── B-4:三支守衛的「地板 block」外釘(不只釘常數)─────────────────────────────
# 只釘 `MIN_CHECKS = N` 的話:把 `if CHECKS < MIN_CHECKS:` 整段刪掉,常數還在、
# 上面的靜態釘照樣綠,地板等於不存在(第 5 型:斷言可被整段刪除);只釘 condition
# 也不夠:保留 `if ...:`、body 換成 `pass`,一樣假綠。這裡解析各守衛 heredoc 內的
# Python AST,對同一個 scoped block 釘三件事:①非註解的 condition(counter <
# MIN_CHECKS 的 If 節點 —— AST 天生不吃註解/字串,別處註解或訊息字串出現同字樣
# 不會誤中)②該 condition 的縮排 body 真的記錄 failure(FAILED += 1 或
# fails.append(...))③記錄的那個名字最後確實走到非零退出(`if FAILED:`/`if fails:`
# 的 body 內含 sys.exit(1) 或 raise SystemExit(1))—— effect 必須綁在同一條鏈上,
# 不是檔案別處剛好有 exit 1。同上方靜態釘:非變異案例,不計入
# EXPECTED_CONTROLS/NEGATIVES/TOTAL。
check_floor_block() { # check_floor_block <相對路徑> <counter名> <fail名> <記錄型:aug|append>
  local rel="$1" counter="$2" failname="$3" kind="$4" out
  out=$(REL="$rel" COUNTER="$counter" FAILNAME="$failname" KIND="$kind" PIN_ROOT="$ROOT" python3 - <<'PYFLOOR' 2>&1
import ast, os, sys
rel = os.environ["REL"]; counter = os.environ["COUNTER"]
failname = os.environ["FAILNAME"]; kind = os.environ["KIND"]
path = os.path.join(os.environ["PIN_ROOT"], rel)
lines = open(path, encoding="utf-8").read().splitlines()
starts = [i for i, l in enumerate(lines) if "<<'PY'" in l]
ends = [i for i, l in enumerate(lines) if l.strip() == "PY"]
if len(starts) != 1 or not ends:
    print(f"heredoc 定位失敗(<<'PY' 出現 {len(starts)} 次)"); sys.exit(1)
tree = ast.parse("\n".join(lines[starts[0] + 1:ends[-1]]))

def is_floor_test(t):
    return (isinstance(t, ast.Compare) and isinstance(t.left, ast.Name)
            and t.left.id == counter and len(t.ops) == 1
            and isinstance(t.ops[0], ast.Lt) and len(t.comparators) == 1
            and isinstance(t.comparators[0], ast.Name)
            and t.comparators[0].id == "MIN_CHECKS")

def records_failure(stmt):
    if kind == "aug":
        return (isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name)
                and stmt.target.id == failname and isinstance(stmt.op, ast.Add))
    return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Attribute)
            and stmt.value.func.attr == "append"
            and isinstance(stmt.value.func.value, ast.Name)
            and stmt.value.func.value.id == failname)

floors = [n for n in ast.walk(tree) if isinstance(n, ast.If) and is_floor_test(n.test)]
if not floors:
    print(f"找不到 `if {counter} < MIN_CHECKS:` 的非註解 condition(地板 if 整段被刪或註解掉)")
    sys.exit(1)
if not any(any(records_failure(s) for s in f.body) for f in floors):
    print(f"condition 還在,但其 body 裡沒有記錄 failure 的 `{failname}`(body 被換成 pass/空操作)")
    sys.exit(1)

def exits_nonzero(node):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "exit" and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "sys" and len(node.args) == 1
            and isinstance(node.args[0], ast.Constant) and node.args[0].value == 1):
        return True
    if (isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call)
            and isinstance(node.exc.func, ast.Name) and node.exc.func.id == "SystemExit"
            and len(node.exc.args) == 1 and isinstance(node.exc.args[0], ast.Constant)
            and node.exc.args[0].value == 1):
        return True
    return False

for n in ast.walk(tree):
    if isinstance(n, ast.If) and isinstance(n.test, ast.Name) and n.test.id == failname:
        for s in n.body:
            if any(exits_nonzero(sub) for sub in ast.walk(s)):
                sys.exit(0)
print(f"`if {failname}:` 的 body 裡找不到 sys.exit(1)/raise SystemExit(1)"
      " —— 地板記錄了 failure 但沒有非零退出路徑")
sys.exit(1)
PYFLOOR
)
  if [ $? -eq 0 ]; then
    echo "  ✓ 地板 block 外釘:$rel(condition+記錄 failure+非零退出同鏈)"
  else
    echo "  ✗ 地板 block 外釘:$rel —— ${out}"
    STATIC_PIN_FAIL=1
  fi
}
check_floor_block "scripts/check-integration-regression-guard.sh" "CHECKS" "FAILED" "aug"
check_floor_block "scripts/check-status-policy.sh" "CHECKS" "FAILED" "aug"
check_floor_block "scripts/check-dev-setup-discipline.sh" "checks" "fails" "append"

# 雙胞胎區塊對帳(派工單 §2.1)。TMPDIR 跨平台正規化在 hooks/selftest.sh 與
# scripts/devflow-check.sh 各有一份 —— 兩支都是可獨立執行的入口,誰先跑都要正規化,
# 所以不能只放一份。既然是副本就得有東西釘住它們一致:只改一邊,Windows 上會變成
# 一支正常、另一支照樣踩到 C:\tmp;而在沒有 cygpath 的機器上兩邊都不進那個分支、
# 看起來都綠 —— 這種漂移只在某個平台現形,靠人 review 抓不住,只能機械對帳。
check_twin_block() { # check_twin_block <相對路徑A> <相對路徑B> <起始標記> <結束標記> <說明>
  local a="$ROOT/$1" b="$ROOT/$2" start="$3" end="$4" label="$5"
  local ta tb
  ta=$(sed -n "/$start/,/$end/p" "$a" 2>/dev/null)
  tb=$(sed -n "/$start/,/$end/p" "$b" 2>/dev/null)
  if [ -z "$ta" ] || [ -z "$tb" ]; then
    echo "  ✗ 雙胞胎區塊:$1 或 $2 找不到標記 ${start}(整段被刪或標記被改名)"
    STATIC_PIN_FAIL=1
  elif [ "$ta" != "$tb" ]; then
    echo "  ✗ 雙胞胎區塊:$1 與 $2 的「${label}」逐字不一致(改了一邊沒改另一邊)"
    STATIC_PIN_FAIL=1
  else
    echo "  ✓ 雙胞胎區塊:$1 ≡ $2(${label})"
  fi
}
check_twin_block "hooks/selftest.sh" "scripts/devflow-check.sh" \
  "devflow:tmpdir-normalize:start" "devflow:tmpdir-normalize:end" "TMPDIR 跨平台正規化"

if [ "$STATIC_PIN_FAIL" -ne 0 ]; then
  echo "⛔ 靜態互釘:至少一處字面值/子字串與釘死清單不符"
  exit 1
fi
echo "  ✓ 九支地板/群組數靜態互釘全過(hooks/selftest.sh / run_tests.py / check-dev-setup-discipline.sh / check-integration-regression-guard.sh / check-status-policy.sh / check-gate-twin.sh MIN_CHECKS / check-file-map.sh / check-gate-twin.sh EXPECTED_GROUPS / check-design-contract.sh EXPECTED_CHECK_SKIP_CALLS)"
echo "  ✓ 三支守衛地板 block AST 外釘全過(check-integration-regression-guard.sh / check-status-policy.sh / check-dev-setup-discipline.sh;condition+記錄 failure+非零退出同鏈,B-4)"
echo "  ✓ guard-selfpin 兩條斷言字面 + 24 個群組名逐字整行釘全過(X-3 HIGH-1/MED,二次複審後改為整行釘)"
echo

if [ "$FAIL" -ne 0 ]; then
  echo "⛔ 架構守衛負向回歸測試:$FAIL 失敗 / $((PASS + FAIL)) 案"
  exit 1
fi
# ── 精確案例數地板(M-2)──────────────────────────────────────────────────────
# CONTROL_RUN / NEGATIVE_RUN 由 expect()/expect_local() 依 want 實際累計,不是硬編字串。
# 任何案例被刪(不論對照組或負向案)都會讓下面四條斷言其中之一對不上 → 非零退出。
TOTAL_RUN=$((CONTROL_RUN + NEGATIVE_RUN))
COUNT_ERR=0
if [ "$CONTROL_RUN" -ne "$EXPECTED_CONTROLS" ]; then
  echo "⛔ 對照組數不符:實際跑了 $CONTROL_RUN 個,釘死值 $EXPECTED_CONTROLS"
  COUNT_ERR=1
fi
if [ "$NEGATIVE_RUN" -ne "$EXPECTED_NEGATIVES" ]; then
  echo "⛔ 負向案數不符:實際跑了 $NEGATIVE_RUN 個,釘死值 $EXPECTED_NEGATIVES"
  COUNT_ERR=1
fi
if [ "$TOTAL_RUN" -ne "$EXPECTED_TOTAL" ]; then
  echo "⛔ 總案例數不符:實際跑了 $TOTAL_RUN 個,釘死值 $EXPECTED_TOTAL"
  COUNT_ERR=1
fi
if [ "$((PASS + FAIL))" -ne "$TOTAL_RUN" ]; then
  echo "⛔ PASS+FAIL($((PASS + FAIL)))≠ 實際案例數($TOTAL_RUN)—— 計數本身壞了"
  COUNT_ERR=1
fi
if [ "$COUNT_ERR" -ne 0 ]; then
  echo
  echo "   要**刻意**增減案例:同步改本檔頂部的 EXPECTED_CONTROLS / EXPECTED_NEGATIVES /"
  echo "   EXPECTED_TOTAL。這三個數字是真的會被比對的斷言,不是顯示用的裝飾。"
  exit 1
fi

echo "✅ 架構守衛負向回歸測試:$PASS/$PASS 全過"
# ⚠️ 變數必須帶大括號:全形「、」緊接 $VAR 時 bash 會把多位元組字元吃進變數名,
#    配上 set -u 就是 unbound variable(同檔 devflow-check.sh 已記過同型教訓)。
echo "   案例數核對通過:對照組 ${CONTROL_RUN}/${EXPECTED_CONTROLS}、負向 ${NEGATIVE_RUN}/${EXPECTED_NEGATIVES}、合計 ${TOTAL_RUN}/${EXPECTED_TOTAL}"
exit 0
