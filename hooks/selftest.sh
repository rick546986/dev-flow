#!/bin/bash
# selftest.sh — dev-flow 守衛全情境自測(可重跑)。
# 自建 temp 假 repo → 跑所有已宣告情境 → 自清。任何專案任何時候可跑,不動真實檔案。
# 用法:<plugin-root>/hooks/selftest.sh [-v](plugin-root 由安裝方式決定,勿寫死)
set -u
H=$(cd "$(dirname "$0")" && pwd)
. "$H/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)
V=${1:-}
T=$(mktemp -d "${TMPDIR:-/tmp}/devflow-selftest.XXXXXX")
C=$(mktemp -d "${TMPDIR:-/tmp}/devflow-gate-selftest.XXXXXX")
PASS=0; FAIL=0; FAILED=()
TOTAL_CASES=$(grep -Ec '^[[:space:]]*(ck|ck_msg) "' "$0")
# ⚠️ MIN_CASES 是釘死地板,一律等於當下實際案例數(2026-08-16 起 348;X-5b 派工
# 分層守衛補 9 案:未武裝放行 / 首派最高階擋下 / 已有低階 attempt 視為合法升階 /
# 豁免消耗+留痕斷言 / 豁免耗盡後仍擋 / 非最高階模型放行 / exec-v2 舊字面值雙讀
# 相容 / tool_name=Agent 與 Task 同等對待;2026-08-17 F2 大 payload ARG_MAX 補
# 7 案 → 355;同日 G3 全形冒號 Owner Call 例外回歸 +1 → 356;同日 F4 豁免卡
# 唯讀 fail-open +2 → 358;同日 G1 history-append 專案根 +4 → 362;同日 Backlog
# D-4 postbash 審查白名單 +3、C-2 stop 清未消耗豁免卡 +3 → 368;同日 report-guard
# 去識別化 +7、審查修正回歸(非 UTF-8/長行回溯/.. 繞路)+3 → 378;2026-08-19 §7
# 前置修復(派工單 notes/dispatch-agent-dispatch-layer.md):s7 legacy sequential
# 真跑 start 驗證 schema=exec-v4+run_id 真的生效(schema 檢查/run_id 格式/正常
# 派工放行/首派最高階擋下/已有低階攔升階放行/非 dev-flow 派工靜默放行 共 6 案)、
# s7b VNext feature-scope(非 --task)同型驗證(schema+run_id 真寫出/首派最高階
# 擋下 共 2 案)→ 378+8 = 386;同日 s7c Stage 7 review 事後補審自建武裝(第三個
# exec.json 寫點,前兩組都沒驗過的分支)同型驗證(schema+run_id 真寫出/首派最高階
# 擋下/已有低階攔升階放行 共 3 案)→ 386+3 = 389)——新增案例時同步 +;絕不
# 「大概抓個下限」。
# 起因:TOTAL_CASES 本身是靠 grep 自算,案例被刪時
# TOTAL_CASES 與實際執行數會一起掉、彼此仍自洽(尾聲的 TOTAL_CASES==TOTAL 比對照樣
# 通過),於是刪一條案例仍印「全過」。這個常數把「案例數不得低於當下已知值」變成
# 獨立於 grep 自算之外的斷言。
MIN_CASES=392

ck() { # ck <名稱> <期望exit> <實際exit>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); [ "$V" = "-v" ] && echo "  ✓ $1"
  else FAIL=$((FAIL+1)); FAILED+=("$1(期望 $2,得 $3)"); echo "  ✗ $1:期望 exit $2,實得 $3"; fi
}
ck_msg() { # ck_msg <名稱> <期望exit> <輸出片段> <實際exit> <實際輸出>
  if [ "$2" = "$4" ] && [[ "$5" == *"$3"* ]]; then PASS=$((PASS+1)); [ "$V" = "-v" ] && echo "  ✓ $1"
  else
    FAIL=$((FAIL+1)); FAILED+=("$1(期望 exit $2 且含 '$3',得 exit $4: $5)")
    echo "  ✗ $1:期望 exit $2 且含 '$3',實得 exit $4: $5"
  fi
}
g() { echo "{\"tool_name\":\"$1\",\"tool_input\":{\"file_path\":\"$T/$2\"}}" | "$H/devflow-guard.sh" >/dev/null 2>&1; echo $?; }
g_capture() { G_OUT=$(echo "{\"tool_name\":\"$1\",\"tool_input\":{\"file_path\":\"$T/$2\"}}" | "$H/devflow-guard.sh" 2>&1); G_RC=$?; }
pb() { echo "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$1\"}}" | "$H/devflow-prebash.sh" >/dev/null 2>&1; echo $?; }
pb_capture() { PB_OUT=$(echo "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$1\"}}" | "$H/devflow-prebash.sh" 2>&1); PB_RC=$?; }
post() { echo '{}' | "$H/devflow-postbash.sh" >/dev/null 2>&1; echo $?; }
post_capture() { P_OUT=$(echo '{}' | "$H/devflow-postbash.sh" 2>&1); P_RC=$?; }
dt_capture() { # dt_capture <tool> <relpath> [ENV=VAL ...](devtalk-guard.sh 直測)
  local dttool="$1" dtrel="$2"; shift 2
  DT_OUT=$(echo "{\"tool_name\":\"$dttool\",\"tool_input\":{\"file_path\":\"$T/$dtrel\"}}" \
    | env "$@" "$H/devtalk-guard.sh" 2>&1); DT_RC=$?
}
x() { ( cd "$T" && "$H/devflow-exec.sh" "$@" >/dev/null 2>&1; echo $? ); }
x_capture() { X_OUT=$(cd "$T" && "$H/devflow-exec.sh" "$@" 2>&1); X_RC=$?; }
scope_is() { "$DEVFLOW_PY" - "$T/.devflow/exec.json" "$1" <<'PY'
import json
import sys
with open(sys.argv[1]) as f:
    state = json.load(f)
sys.exit(0 if state.get("scope") == [sys.argv[2]] else 1)
PY
}
task() {
  printf '%s\n' \
    '## T-1 guard fixture' \
    '- Covers: R-1' \
    "- Files: $1" \
    '- Verify: `true`' \
    '- Blocked-by: —' > "$T/docs/dev/f1/5-tasks.md"
}
missing_field() {
  task "src/a.py"
  sed -i.bak "/- $1:/d" "$T/docs/dev/f1/5-tasks.md"
  rm -f "$T/docs/dev/f1/5-tasks.md.bak"
  x_capture start f1
}
cleanup_start_state() {
  x stop >/dev/null
  git checkout -- .gitignore
}
gate_fixture() { # gate_fixture <template sentence> [live-skill sentence]
  local template_clause="$1"
  local skill_clause="${2:-$1}"
  rm -rf "$C/master" "$C/plugin"
  mkdir -p "$C/master/_templates" "$C/plugin/skills/dev-flow"
  printf '%s\n' \
    '## 3. 七份文檔' \
    '| # | 檔 | 用途 | Gate |' \
    '| 2 | 2-decision | | **G1** 方向核准 + OC 全裁決 |' \
    '| 4 | 4-spec | | **G2** R/S 全審 + DD 全裁決 |' \
    '| 7 | 7-review | | **G3** 本次 S 全綠 + 回歸綠 + 現象證據 |' \
    '## 4. 下一節' \
    '## 7. 角色與 Gate' \
    '- 審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審（留痕的最後手段）。' \
    '- G1 = 方向核准 + **Owner Calls 全裁決**。G2 = **R/S 全審 + Drafting Decisions 全裁決**。G3 = **本次 S 全綠 + 既有測試套件全綠 + 現象證據逐 S 相符**。' \
    '## 8. 下一節' > "$C/master/README.md"
  printf '%s\n' \
    '| stage | gate |' \
    '| 2 | **G1** Owner Calls 全裁決 |' \
    '| 4 | **G2** R/S 全審 + Drafting Decisions 全裁決 |' \
    '| 7 | **G3** 本次 S 全綠 + 既有測試套件全綠 + 現象證據 |' \
    "$skill_clause" > "$C/plugin/skills/dev-flow/SKILL.md"
  for n in 2 4 7; do
    case "$n" in
      2) gate='**G1** Owner Calls 全裁決' ;;
      4) gate='**G2** R/S 全審 + Drafting Decisions 全裁決' ;;
      7) gate='**G3** 本次 S 全綠 + 既有測試套件全綠 + 現象證據' ;;
    esac
    printf '%s\n' "$template_clause" "> $gate" '## 本文' > "$C/master/_templates/$n-fixture.md"
  done
  cp "$C/master/_templates/2-fixture.md" "$C/master/_templates/2-decision.md"
  cp "$C/master/_templates/4-fixture.md" "$C/master/_templates/4-spec.md"
  cp "$C/master/_templates/7-fixture.md" "$C/master/_templates/7-review.md"
  rm -f "$C/master/_templates/"*-fixture.md
}
gate_capture() {
  GATE_OUT=$(DEVFLOW_MASTER="$C/master" DEVFLOW_PLUGIN="$C/plugin" "$H/gate-consistency.sh" 2>&1)
  GATE_RC=$?
}

mkdir -p "$T/docs/dev/f1" "$T/docs/dev/f2" "$T/src/lib"
cd "$T" || exit 1
git init -q . && git config user.email t@t && git config user.name t
printf -- "---\nstatus: approved\n---\n" > docs/dev/f1/4-spec.md
printf -- "---\nstatus: approved\n---\n" > docs/dev/f2/4-spec.md
echo "up1" > docs/dev/f1/1-discussion.md; echo "up2" > docs/dev/f2/1-discussion.md
task "src/a.py, src/lib/"
echo "a" > src/a.py; echo "tracked" > src/tracked.txt; echo "rename" > src/rename-source.py
printf 'ignored/\n' > .gitignore
git add -A >/dev/null; git commit -qm init

echo "=== dev-flow 守衛自測(${TOTAL_CASES} 案)==="
echo "-- 未武裝時全靜默 --"
ck "無旗標:Edit 契約檔放行" 0 "$(g Edit docs/dev/f1/4-spec.md)"
ck "無旗標:postbash 沉默"   0 "$(post)"
ck "無旗標:prebash 沉默"    0 "$(pb 'cat docs/dev/f1/1-discussion.md')"

echo "-- start 前置檢查 --"
sed -i.bak 's/approved/draft/' docs/dev/f1/4-spec.md
ck "4-spec 非 approved → 拒啟" 1 "$(x start f1)"
sed -i.bak 's/draft/approved/' docs/dev/f1/4-spec.md; rm -f docs/dev/f1/4-spec.md.bak
ck "缺 slug → 拒"              1 "$(x start)"
missing_field Covers
ck_msg "T-1 缺 Covers → 拒啟" 1 "T-1 缺 Covers" "$X_RC" "$X_OUT"
missing_field Files
ck_msg "T-1 缺 Files → 拒啟" 1 "T-1 缺 Files" "$X_RC" "$X_OUT"
missing_field Verify
ck_msg "T-1 缺 Verify → 拒啟" 1 "T-1 缺 Verify" "$X_RC" "$X_OUT"
missing_field Blocked-by
ck_msg "T-1 缺 Blocked-by → 拒啟" 1 "T-1 缺 Blocked-by" "$X_RC" "$X_OUT"
task "src/a.py"
printf '%s\n' \
  '## T-2 second task' \
  '- Covers: R-2' \
  '- Files: src/second.py' \
  '- Blocked-by: T-1' >> docs/dev/f1/5-tasks.md
x_capture start f1
ck_msg "每個 T 都驗欄位" 1 "T-2 缺 Verify" "$X_RC" "$X_OUT"
task "/tmp/outside.py"
x_capture start f1
ck_msg "Files 絕對路徑 → 拒啟" 1 "絕對路徑" "$X_RC" "$X_OUT"
task "src/../outside.py"
x_capture start f1
ck_msg "Files .. traversal → 拒啟" 1 ".." "$X_RC" "$X_OUT"
task "./src/a.py"
ck "./ Files canonical scope → 啟動" 0 "$(x start f1)"
ck "canonical scope 儲存 src/a.py" 0 "$(scope_is src/a.py; echo $?)"
ck "canonical scope 放行 src/a.py" 0 "$(g Write src/a.py)"
cleanup_start_state
task "internal/x_test.go"
ck "monorepo Files scope → 啟動" 0 "$(x start f1)"
g_capture Write backend-go/internal/x_test.go
ck_msg "monorepo sibling path 不在 scope" 2 "internal/x_test.go 與 backend-go/internal/x_test.go" "$G_RC" "$G_OUT"
cleanup_start_state
task "src/a.py, src/lib/"
echo "dirty" > src/pre.txt
x_capture start f1
ck_msg "開跑前 scope 外髒檔 → 拒啟" 1 "commit、還原或使用乾淨 worktree" "$X_RC" "$X_OUT"
ck_msg "start scope 診斷含 monorepo root 提醒" 1 "internal/x_test.go 與 backend-go/internal/x_test.go" "$X_RC" "$X_OUT"
cleanup_start_state
rm -f src/pre.txt
echo "changed" > src/tracked.txt
x_capture start f1
ck_msg "開跑前 tracked scope 外髒檔 → 拒啟" 1 "src/tracked.txt" "$X_RC" "$X_OUT"
cleanup_start_state
git checkout -- src/tracked.txt
mkdir -p ignored/nested
echo "ambient" > ignored/.DS_Store
echo "ambient" > ignored/nested/Thumbs.db
ck "開跑前 ignored parent 僅 ambient leaves → 啟動" 0 "$(x start f1)"
cleanup_start_state
# A-13:被 .gitignore 忽略的檔(本機環境切換檔、IDE 產物)不擋開工 —— 這條 2026-08-04
# 前是「拒啟」,實地採用時讓「有本機開發目錄的專案一律 start 不了」。放寬的同時
# 這些檔仍收進 baseline,所以下面兩條遮蔽測試必須照舊擋。
echo "ignored" > ignored/nested/pre.txt
ck "A-13:開跑前 ignored 髒檔不擋開工" 0 "$(x start f1)"
echo "changed-after-start" > ignored/nested/pre.txt
post_capture
ck_msg "A-13:開跑前 ignored 檔執行期被改 → postbash 擋" 2 "ignored/nested/pre.txt" "$P_RC" "$P_OUT"
cleanup_start_state
ck "A-13:ignored 髒檔仍在時可重複 start" 0 "$(x start f1)"
echo "shadowed" > ignored/nested/after-start.txt
post_capture
ck_msg "A-13:執行期新增 ignored 檔 → postbash 擋(遮蔽漏洞未打開)" 2 "ignored/nested/after-start.txt" "$P_RC" "$P_OUT"
cleanup_start_state
rm -rf ignored
printf 'pre-start ignore\n' >> .gitignore
x_capture start f1
ck_msg "開跑前 .gitignore 髒檔 → 拒啟" 1 ".gitignore" "$X_RC" "$X_OUT"
cleanup_start_state
task ".gitignore"
printf 'declared pre-start ignore\n' >> .gitignore
x_capture start f1
ck_msg "宣告 .gitignore 仍拒開跑前髒檔" 1 ".gitignore" "$X_RC" "$X_OUT"
cleanup_start_state
task ".gitignore"
ck "宣告 .gitignore 的乾淨起跑" 0 "$(x start f1)"
printf 'declared post-start ignore\n' >> .gitignore
post_capture
ck_msg "postbash 擋宣告的 .gitignore shell 改動" 2 ".gitignore" "$P_RC" "$P_OUT"
cleanup_start_state
task "src/a.py"
ck "allow .gitignore 的乾淨起跑" 0 "$(x start f1)"
ck "allow 可加入 .gitignore" 0 "$(x allow .gitignore --reason 'L1 D-control')"
printf 'allowed post-start ignore\n' >> .gitignore
post_capture
ck_msg "postbash 擋 allow 的 .gitignore shell 改動" 2 ".gitignore" "$P_RC" "$P_OUT"
cleanup_start_state
task "src/rename-target.py"
git mv src/rename-source.py src/rename-target.py
x_capture start f1
ck_msg "開跑前 rename source scope 外 → 拒啟" 1 "src/rename-source.py" "$X_RC" "$X_OUT"
cleanup_start_state
git mv src/rename-target.py src/rename-source.py
task "src/a.py, src/lib/"
echo "ambient-before" > .DS_Store
ck "approved → 啟動成功"       0 "$(x start f1)"

echo "-- 雙 start 防護 --"
ck "武裝中他 slug start → 拒啟" 1 "$(x start f2)"
ck "武裝中同 slug re-arm → 允許" 0 "$(x start f1)"

echo "-- PreToolUse 守衛 --"
ck "擋改本 slug 4-spec"        2 "$(g Edit docs/dev/f1/4-spec.md)"
ck "擋改本 slug 4-spec.html"   2 "$(g Write docs/dev/f1/4-spec.html)"
ck "擋改他 slug 4-spec(跨 feature)" 2 "$(g Edit docs/dev/f2/4-spec.md)"
ck "擋讀本 slug 1-discussion"  2 "$(g Read docs/dev/f1/1-discussion.md)"
ck "擋讀他 slug 1-discussion"  2 "$(g Read docs/dev/f2/1-discussion.md)"
ck "放行讀 4-spec(執行需要)"  0 "$(g Read docs/dev/f1/4-spec.md)"
ck "擋改 .devflow/exec.json"   2 "$(g Edit .devflow/exec.json)"
ck "擋改 .gitignore"           2 "$(g Edit .gitignore)"
ck "ambient metadata 不需 allow" 0 "$(g Write nested/.DS_Store)"
ln -sf "$T/docs/dev/f1/4-spec.md" src/link.py
ck "symlink 指向契約檔 → 擋"   2 "$(g Write src/link.py)"; rm -f src/link.py
ck "放行 scope 內(檔)"        0 "$(g Write src/a.py)"
ck "放行 scope 內(目錄前綴)"  0 "$(g Write src/lib/deep/x.py)"
ck "放行 6-notes"              0 "$(g Write docs/dev/f1/6-implementation-notes.md)"
ck "擋 scope 外"               2 "$(g Write src/other.py)"

echo "-- Stage 7 review 圍欄③(phase=review;A-11)--"
ck "回歸:舊 exec.json(無 phase 鍵)讀 6-notes 放行(升版前後行為一致)" \
  0 "$(g Read docs/dev/f1/6-implementation-notes.md)"
ck "回歸(prebash 鏡像):舊 exec.json(無 phase 鍵)shell cat 6-notes 放行" \
  0 "$(pb 'cat docs/dev/f1/6-implementation-notes.md')"
# postbash 鏡像③(回歸):舊 exec.json 尚無 "phase" 鍵時,5-tasks 的 shell 改動恆許
# 不受影響 —— 5-tasks.md 此刻仍是 task() 反覆改寫留下的未提交髒檔(Stage 6 進行中
# 的正常樣貌),postbash 必須維持升版前行為,靜默放行。
ck "postbash 鏡像回歸:舊 exec.json(無 phase 鍵)shell 改 5-tasks 仍放行" 0 "$(post)"
ck "基準:review 武裝前寫 7-review.md 仍受 scope 擋(對照武裝後放行)" \
  2 "$(g Write docs/dev/f1/7-review.md)"
# postbash 鏡像基準(D-4 白名單的負向):**非 review 期**shell 產 7-review.md →
# 偵測網仍擋 —— 白名單只在 phase=review 生效,不得變成常駐豁免。
echo "premature-review-notes" > docs/dev/f1/7-review.md
post_capture
ck_msg "postbash D-4 基準:非 review 期 shell 產 7-review.md → 仍擋" 2 "scope 外" "$P_RC" "$P_OUT"
rm -f docs/dev/f1/7-review.md
# 模擬 Stage 6 收工:5-tasks.md 進 review 前先提交,之後 postbash 才能分辨「review
# 期間又被 shell 動」與「Stage 6 遺留未提交」——這兩者不是同一件事,見下方圍欄③收緊註解。
git add docs/dev/f1/5-tasks.md && git commit -qm "selftest: pin 5-tasks before review arm" >/dev/null
ck "devflow-exec.sh review f1 → 武裝圍欄③"    0 "$(x review f1)"
# postbash 鏡像(canary):review 剛武裝、5-tasks 尚未被 shell 動過 → 必須沉默,否則
# review 期間每一個 Bash 呼叫都會被誤擋(dirty-detection 而非 change-detection)。
ck "postbash 鏡像:review 武裝後未動 5-tasks → 仍沉默" 0 "$(post)"
g_capture Read docs/dev/f1/6-implementation-notes.md
ck_msg "① review 中讀 6-notes → 擋,訊息指步 4" 2 "步 4" "$G_RC" "$G_OUT"
pb_capture 'cat docs/dev/f1/6-implementation-notes.md'
ck_msg "prebash 鏡像①:review 中 shell cat 6-notes → 擋,訊息指步 4 與 review-unlock" \
  2 "步 4" "$PB_RC" "$PB_OUT"
ck_msg "prebash 鏡像①訊息含 review-unlock 出口" 2 "review-unlock" "$PB_RC" "$PB_OUT"
# MED-1(第二批獨立審查):圍欄③鏡像改用裸檔名比對,補繞路案 —— cd 把路徑拆開、
# 萬用字元代換 slug,兩者原本都不含連續路徑字串,舊版嚴格路徑正則抓不到。
pb_capture 'cd docs/dev/f1 && cat 6-implementation-notes.md'
ck_msg "prebash 鏡像③(cd 繞路):review 中 cd+cat 6-notes → 擋" \
  2 "6-implementation-notes" "$PB_RC" "$PB_OUT"
pb_capture 'cat docs/dev/*/6-implementation-notes.md'
ck_msg "prebash 鏡像④(glob 繞路):review 中萬用字元讀 6-notes → 擋" \
  2 "6-implementation-notes" "$PB_RC" "$PB_OUT"
ck "② review 中寫 7-review.md → 放行"          0 "$(g Write docs/dev/f1/7-review.md)"
ck "review 中寫 evidence/ → 放行"              0 "$(g Write docs/dev/f1/evidence/screenshot.png)"
# postbash 鏡像(D-4 白名單,Backlog 第 6 型實例):guard 側放行 7-review*/evidence/
# 的 review 期寫入,偵測網也必須放行 —— 修前這裡被當 scope 外改動(採用現場實測
# 撞到,以 L1 allow 應急)。與 unlock 無關,同 guard 側語意。
echo "review-notes" > docs/dev/f1/7-review.md
mkdir -p docs/dev/f1/evidence && echo "e" > docs/dev/f1/evidence/e2e.log
post_capture
ck "postbash D-4 白名單:review 中 shell 產 7-review*/evidence/ → 放行(修前誤擋)" 0 "$P_RC"
rm -rf docs/dev/f1/7-review.md docs/dev/f1/evidence
ck "postbash D-4 清理後仍沉默(基準恢復)" 0 "$(post)"
g_capture Write docs/dev/f1/5-tasks.md
ck_msg "③ review 中寫 5-tasks.md → 擋"         2 "圍欄③" "$G_RC" "$G_OUT"
# postbash 鏡像①:review 中(未 unlock)shell 側直接改 5-tasks.md(繞過 Edit/Write
# hook)也必須被抓 —— 這正是本次收緊要堵的破口(舊碼:allowed_prefix 恆許,靜默放行)。
echo "shell-edit-during-review" >> docs/dev/f1/5-tasks.md
post_capture
ck_msg "postbash 鏡像①:review 中(未 unlock)shell 改 5-tasks → 擋" 2 "圍欄③" "$P_RC" "$P_OUT"
ck "⑥ review 中寫非 dev-flow 檔(scope 內)恆放行" 0 "$(g Write src/a.py)"
ck "devflow-exec.sh review-unlock f1 → 解鎖"   0 "$(x review-unlock f1)"
# postbash 鏡像②:review-unlock 後,5-tasks.md 的 shell 改動恆許恢復 —— 上一步留下
# 的髒內容原封不動,只靠 review_unlocked 翻轉就該轉為放行(與 unlock 後既有行為
# 完全不變一致)。
ck "postbash 鏡像②:review-unlock 後 shell 改 5-tasks → 恢復豁免" 0 "$(post)"
ck "④ review-unlock 後讀 6-notes → 放行"       0 "$(g Read docs/dev/f1/6-implementation-notes.md)"
ck "prebash 鏡像②:review-unlock 後 shell cat 6-notes → 放行" \
  0 "$(pb 'cat docs/dev/f1/6-implementation-notes.md')"
ck "prebash 鏡像③:review-unlock 後 cd+cat 6-notes → 放行" \
  0 "$(pb 'cd docs/dev/f1 && cat 6-implementation-notes.md')"
ck "prebash 鏡像④:review-unlock 後萬用字元讀 6-notes → 放行" \
  0 "$(pb 'cat docs/dev/*/6-implementation-notes.md')"
g_capture Write docs/dev/f1/5-tasks.md
ck_msg "review-unlock 後寫 5-tasks.md 仍擋(Write 限縮維持)" 2 "圍欄③" "$G_RC" "$G_OUT"

echo "-- prebash 圍欄 --"
ck "shell 讀上游 → 擋"         2 "$(pb 'cat docs/dev/f1/1-discussion.md')"
ck "shell 刪旗標 → 擋"         2 "$(pb 'rm -f .devflow/exec.json')"
ck "正常 shell 放行"           0 "$(pb 'pytest -q')"

echo "-- allow(L1 出口)--"
ck "allow 無 reason → 拒"      1 "$(x allow src/other.py)"
ck "allow 帶 reason → 成功"    0 "$(x allow ./src/other.py --reason 'L1 D-1')"
ck "allow canonical 後放行"    0 "$(g Write src/other.py)"

echo "-- postbash 偵測網 --"
ck "乾淨時沉默"                0 "$(post)"
echo "ambient-after" > .DS_Store
ck "既有 .DS_Store 改動不擋"  0 "$(post)"
mkdir -p nested/cache
echo "ds" > nested/.DS_Store; echo "apple" > nested/cache/._finder; echo "thumb" > nested/cache/Thumbs.db
ck "新增 ambient metadata 不擋" 0 "$(post)"; rm -rf nested
mkdir -p ignored/cache
echo "ds" > ignored/.DS_Store; echo "apple" > ignored/cache/._finder; echo "thumb" > ignored/cache/Thumbs.db
ck "postbash ignored parent 僅 ambient leaves 不擋" 0 "$(post)"
echo "meaningful" > ignored/cache/source.py
post_capture
ck_msg "postbash ignored parent 的 meaningful sibling 仍擋" 2 "ignored/cache/source.py" "$P_RC" "$P_OUT"
rm -rf ignored
git mv src/rename-source.py src/rename-target.py
post_capture
ck_msg "postbash 抓 rename source scope 外" 2 "src/rename-source.py" "$P_RC" "$P_OUT"
git mv src/rename-target.py src/rename-source.py
echo "sneak" > src/sneaky.py
post_capture
ck_msg "抓 shell 新增 scope 外檔" 2 "src/sneaky.py" "$P_RC" "$P_OUT"
ck_msg "postbash scope 診斷含 monorepo root 提醒" 2 "internal/x_test.go 與 backend-go/internal/x_test.go" "$P_RC" "$P_OUT"
rm -f src/sneaky.py
echo "evil" >> docs/dev/f1/4-spec.md
ck "抓契約檔內容被改(hash)"   2 "$(post)"; git checkout -- docs/dev/f1/4-spec.md 2>/dev/null
echo "evil-cross-feature" >> docs/dev/f2/4-spec.md
git add docs/dev/f2/4-spec.md && git commit -qm committed-cross-feature-contract-mutation
post_capture
ck_msg "postbash 抓已 commit 的跨 feature 契約修改" 2 "docs/dev/f2/4-spec.md" "$P_RC" "$P_OUT"
git checkout HEAD^ -- docs/dev/f2/4-spec.md && git commit -qm restore-cross-feature-contract
git rm -q docs/dev/f2/1-discussion.md && git commit -qm committed-cross-feature-contract-deletion
post_capture
ck_msg "postbash 抓已 commit 的跨 feature 契約刪除" 2 "docs/dev/f2/1-discussion.md" "$P_RC" "$P_OUT"
git checkout HEAD^ -- docs/dev/f2/1-discussion.md && git commit -qm restore-cross-feature-upstream
mkdir -p docs/dev/f3
printf -- "---\nstatus: approved\n---\n" > docs/dev/f3/4-spec.md
git add docs/dev/f3/4-spec.md && git commit -qm committed-cross-feature-contract-addition
post_capture
ck_msg "postbash 抓已 commit 的跨 feature 契約新增" 2 "docs/dev/f3/4-spec.md" "$P_RC" "$P_OUT"
git rm -q docs/dev/f3/4-spec.md && git commit -qm remove-cross-feature-contract-addition
printf 'post-start ignore\n' >> .gitignore
post_capture
ck_msg "postbash 抓 .gitignore shell 改動" 2 ".gitignore" "$P_RC" "$P_OUT"
git add .gitignore && git commit -qm control-plane-change
post_capture
ck_msg "postbash 抓已 commit 的 .gitignore 改動" 2 ".gitignore" "$P_RC" "$P_OUT"

echo "-- devtalk-guard(PostToolUse Edit|Write;dev-talk 盲原則 + deny 補 obs 事件)--"
mkdir -p "$T/skills/dev-talk"
echo "plain content, nothing forbidden here" > "$T/skills/dev-talk/plain.md"
dt_capture Write skills/dev-talk/plain.md
ck "devtalk-guard 無洩漏 → 放行" 0 "$DT_RC"
echo "誤帶 5-tasks 與 gate 字眼(盲原則洩漏)" > "$T/skills/dev-talk/leaky.md"
dt_capture Write skills/dev-talk/leaky.md
ck_msg "① devtalk-guard 洩漏 → 擋(既有行為回歸)" 2 "盲原則洩漏" "$DT_RC" "$DT_OUT"
# ②③ 需要真武裝的 run_id 才能驗事件落盤/obs 壞掉不影響 deny —— $T 主 fixture 全程走
# legacy start(無 --task),不生 run_id(同 p3/pw 區塊點出的既有限制),故另開最小
# fixture、手寫 exec-v3 exec.json(仿 p3 區塊寫法,不走 CLI)。
DTT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-dt-selftest.XXXXXX")
DTRUN="01JG8C4V2M0000000000000DT0"; DTRUN="run_$DTRUN"
mkdir -p "$DTT/skills/dev-talk" "$DTT/.devflow"
( cd "$DTT" && git init -q . && git config user.email t@t && git config user.name t \
  && git commit --allow-empty -qm init >/dev/null )
printf '{"schema":"exec-v3","slug":"dt","run_id":"%s","scope":[],"extra":[]}\n' "$DTRUN" \
  > "$DTT/.devflow/exec.json"
echo "誤帶 5-tasks 與 gate 字眼(盲原則洩漏)" > "$DTT/skills/dev-talk/leaky.md"
DT_OUT=$(echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$DTT/skills/dev-talk/leaky.md\"}}" \
  | (cd "$DTT" && "$H/devtalk-guard.sh") 2>&1); DT_RC=$?
ck_msg "devtalk-guard(獨立 fixture)洩漏仍擋" 2 "盲原則洩漏" "$DT_RC" "$DT_OUT"
ck "② devtalk-guard deny 落 hook 事件一筆(gate=devtalk-guard)" 0 \
  "$(grep -q '"gate": "devtalk-guard"' "$DTT/.devflow/runs/$DTRUN/hooks/events-"*.jsonl 2>/dev/null; echo $?)"
DTBAD=$(mktemp "${TMPDIR:-/tmp}/devflow-dt-badroot.XXXXXX")   # 一般檔案,非目錄 = 不可 mkdir
DT_OUT=$(echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$DTT/skills/dev-talk/leaky.md\"}}" \
  | (cd "$DTT" && env DEVFLOW_RUNS_ROOT="$DTBAD/x" "$H/devtalk-guard.sh") 2>&1); DT_RC=$?
ck_msg "③ devtalk-guard obs 通道壞掉(目錄不可寫):deny 判定不變" 2 "盲原則洩漏" "$DT_RC" "$DT_OUT"
rm -f "$DTBAD"; rm -rf "$DTT"

echo "-- fail-closed --"
rm -f .devflow/exec.json
ck "旗標消失但 sentinel 在 → 擋" 2 "$(g Write src/a.py)"
mkdir -p .devflow; echo "{壞" > .devflow/exec.json
ck "旗標損壞 → 擋"            2 "$(g Write src/a.py)"
ck "旗標損壞 → 異 slug start 拒啟" 1 "$(x start f2)"

echo "-- gate reviewer-selection semantics --"
gate_fixture '審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審（留痕的最後手段）。'
gate_capture
ck_msg "gate 合法 reviewer fallback → 通過" 0 "全部一致" "$GATE_RC" "$GATE_OUT"
gate_fixture '審查者依序：適格人類 reviewer → 不派 fresh-context reviewer Agent → owner 自審（留痕的最後手段）。'
gate_capture
ck_msg "gate 擋否定 fresh reviewer 語意" 1 "reviewer-selection" "$GATE_RC" "$GATE_OUT"
gate_fixture '審查者依序：不使用適格人類 reviewer → fresh-context reviewer Agent → owner 自審（留痕的最後手段）。'
gate_capture
ck_msg "gate 擋否定適格人類 reviewer 語意" 1 "reviewer-selection" "$GATE_RC" "$GATE_OUT"
gate_fixture '審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審（不需記錄的最後手段）。'
gate_capture
ck_msg "gate 擋否定 owner 留痕語意" 1 "reviewer-selection" "$GATE_RC" "$GATE_OUT"
gate_fixture '審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審（有記錄但不是最後手段）。'
gate_capture
ck_msg "gate 擋否定 owner 最後手段語意" 1 "reviewer-selection" "$GATE_RC" "$GATE_OUT"
gate_fixture '審查者依序：owner 自審（留痕的最後手段）→ fresh-context reviewer Agent → 適格人類 reviewer。'
gate_capture
ck_msg "gate 擋反轉 reviewer fallback 順序" 1 "reviewer-selection" "$GATE_RC" "$GATE_OUT"
gate_fixture \
  '審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審（留痕的最後手段）。' \
  '審查者依序：owner 自審（留痕的最後手段）→ fresh-context reviewer Agent → 適格人類 reviewer。'
gate_capture
ck_msg "gate 擋 live skill 反轉 reviewer fallback 順序" 1 "plugin dev-flow SKILL.md" "$GATE_RC" "$GATE_OUT"
gate_fixture \
  '審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審（留痕的最後手段）。' \
  '審查者依序：適格人類 reviewer → 不派 fresh-context reviewer Agent → owner 自審（留痕的最後手段）。'
gate_capture
ck_msg "gate 擋 live skill 否定 fresh reviewer" 1 "plugin dev-flow SKILL.md" "$GATE_RC" "$GATE_OUT"

# ---- p4_ gate-consistency VNext 錨(共享契約 §1/§2;fixture 自帶新舊條文,不依賴 live README)----
p4_g2_echo='R/S 全審 + Drafting Decisions 全裁決 + Verification Profile + Demo verdict'
p4_g3_echo='本次 S 全綠 + 既有測試套件全綠 + 現象證據 + Evidence 契約全過'
p4_s7_default='- G1 = 方向核准 + **Owner Calls 全裁決**。G2 = 契約寫得對不對(**R/S 全審 + Drafting Decisions 全裁決** + **Verification Profile**(依 lane 正確填寫;fast+high 拒絕) + **Demo verdict**(依 Stage 3 trigger 判定;Agent 不得自填 ACCEPTED))。G3 = 做出來的對不對(**本次 S 全綠 + 既有測試套件全綠 + 現象證據** + **Evidence 契約全過**(八點全部成立))。'
p4_s7_mixed='- G1 = 方向核准 + **Owner Calls 全裁決**。G2 = 契約寫得對不對(**R/S 全審 + Drafting Decisions 全裁決** **+ Verification Profile** + **Demo verdict**)。G3 = 做出來的對不對(**本次 S 全綠 + 既有測試套件全綠 + 現象證據** **+ Evidence 契約全過**)。'
p4_gate_fixture_vnext() { # <tpl4 G2 摘要> <tpl7 G3 摘要> <skill G2 摘要> <skill G3 摘要> <readme3 G2 摘要> <readme3 G3 摘要> [§7 gate 定義列]
  local p4_reviewer='審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審（留痕的最後手段）。'
  local p4_s7="${7:-$p4_s7_default}"
  rm -rf "$C/master" "$C/plugin"
  mkdir -p "$C/master/_templates" "$C/plugin/skills/dev-flow"
  printf '%s\n' \
    '## 3. 七份文檔' \
    '| # | 檔 | 用途 | Gate |' \
    '| 2 | 2-decision | | **G1** OC 全裁決 |' \
    "| 4 | 4-spec | | **G2** $5 |" \
    "| 7 | 7-review | | **G3** $6 |" \
    '## 4. 下一節' \
    '## 7. 角色與 Gate' \
    "- $p4_reviewer" \
    "$p4_s7" \
    '## 8. 下一節' > "$C/master/README.md"
  printf '%s\n' \
    '| stage | gate |' \
    '| 2 | **G1** Owner Calls 全裁決 |' \
    "| 4 | **G2** $3 |" \
    "| 7 | **G3** $4 |" \
    "$p4_reviewer" > "$C/plugin/skills/dev-flow/SKILL.md"
  printf '%s\n' "$p4_reviewer" '> **G1** Owner Calls 全裁決' '## 本文' > "$C/master/_templates/2-decision.md"
  printf '%s\n' "$p4_reviewer" "> **G2** $1" '## 本文' > "$C/master/_templates/4-spec.md"
  printf '%s\n' "$p4_reviewer" "> **G3** $2" '## 本文' > "$C/master/_templates/7-review.md"
}

echo "-- p4_ gate-consistency VNext 錨(G2 Verification Profile/Demo verdict、G3 Evidence 契約全過)--"
p4_gate_fixture_vnext "$p4_g2_echo" "$p4_g3_echo" "$p4_g2_echo" "$p4_g3_echo" "$p4_g2_echo" "$p4_g3_echo"
gate_capture
ck_msg "p4_vnext 錨全同步 → 通過" 0 "全部一致" "$GATE_RC" "$GATE_OUT"
ck_msg "p4_vnext G2 正本 tokens 含 Verification Profile" 0 "Verification Profile" "$GATE_RC" "$GATE_OUT"
ck_msg "p4_vnext G2 正本 tokens 含 Demo verdict" 0 "Demo verdict" "$GATE_RC" "$GATE_OUT"
ck_msg "p4_vnext G3 正本 tokens 含 Evidence 契約全過" 0 "契約全過" "$GATE_RC" "$GATE_OUT"
p4_gate_fixture_vnext 'R/S 全審 + Drafting Decisions 全裁決 + Demo verdict' "$p4_g3_echo" "$p4_g2_echo" "$p4_g3_echo" "$p4_g2_echo" "$p4_g3_echo"
gate_capture
ck_msg "p4_vnext 4-spec 頂註缺 Verification Profile → 抓漂移" 1 '✗ _templates/4-spec.md 頂註:缺 token「Verification Profile」' "$GATE_RC" "$GATE_OUT"
p4_gate_fixture_vnext "$p4_g2_echo" "$p4_g3_echo" 'R/S 全審 + Drafting Decisions 全裁決 + Verification Profile' "$p4_g3_echo" "$p4_g2_echo" "$p4_g3_echo"
gate_capture
ck_msg "p4_vnext SKILL 階段表缺 Demo verdict → 抓漂移" 1 '✗ plugin dev-flow SKILL.md 階段表:缺 token「Demo verdict」' "$GATE_RC" "$GATE_OUT"
p4_gate_fixture_vnext "$p4_g2_echo" '本次 S 全綠 + 既有測試套件全綠 + 現象證據' "$p4_g2_echo" "$p4_g3_echo" "$p4_g2_echo" "$p4_g3_echo"
gate_capture
ck_msg "p4_vnext 7-review 頂註缺 Evidence 契約全過 → 抓漂移" 1 '✗ _templates/7-review.md 頂註:缺 token「Evidence、契約全過」' "$GATE_RC" "$GATE_OUT"
p4_gate_fixture_vnext "$p4_g2_echo" "$p4_g3_echo" "$p4_g2_echo" "$p4_g3_echo" "$p4_g2_echo" '本次 S 全綠 + 既有測試套件全綠 + 現象證據'
gate_capture
ck_msg "p4_vnext README §3 表缺 Evidence 契約全過 → 抓漂移" 1 '✗ README §3 七份文檔表:缺 token「Evidence、契約全過」' "$GATE_RC" "$GATE_OUT"
p4_gate_fixture_vnext "$p4_g2_echo" "$p4_g3_echo" "$p4_g2_echo" "$p4_g3_echo" "$p4_g2_echo" "$p4_g3_echo" "$p4_s7_mixed"
gate_capture
ck_msg "p4_vnext 混寫形(**+ 錨**/+ **錨**)全抽到 → 通過" 0 "Demo verdict" "$GATE_RC" "$GATE_OUT"
gate_fixture '審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審（留痕的最後手段）。'
gate_capture
ck_msg "p4_舊條文格式 G2 tokens 行為不變" 0 "Drafting Decisions" "$GATE_RC" "$GATE_OUT"

echo "-- stop 後恢復沉睡 --"
x stop >/dev/null
ck "stop 後放行契約檔"         0 "$(g Edit docs/dev/f1/4-spec.md)"
ck "stop 後 postbash 沉默"     0 "$(post)"

# ====================================================================
# p1_*:parallel 執行契約(vnext §5/§7;行為正本 = tests/parallel-stage6/)
# 只增不改:以下全部為新增案,不動上方既有 80 案。
# ====================================================================

p1_setup_battery() {
  P1D=$(mktemp -d "${TMPDIR:-/tmp}/devflow-p1.XXXXXX")
  cat > "$P1D/p1check.py" <<'P1PY'
#!/usr/bin/env python3
"""p1 battery — parallel 契約自測(selftest.sh 生成;鏡射方法論 parallel-stage6 fixtures)。
用法:p1check.py <hooks-dir> <check> [<repo-root>];exit 0 = PASS。"""
import json, os, re, subprocess, sys
sys.dont_write_bytecode = True
from importlib.machinery import SourceFileLoader

H, CHECK = sys.argv[1], sys.argv[2]
ROOT = sys.argv[3] if len(sys.argv) > 3 else ""
L = SourceFileLoader("devflow_lib", os.path.join(H, "devflow-lib.py")).load_module()
G = SourceFileLoader("devflow_gate", os.path.join(H, "_gate_impl.py")).load_module()


def bad(msg=""):
    print(msg)
    sys.exit(1)


def need(cond, msg="assert"):
    if not cond:
        bad(msg)


def md(exec_lines, tasks):
    out = ["---", "feature: fx", "stage: 5-tasks", "status: approved"]
    if exec_lines:
        out.append("execution:")
        out += ["  " + l for l in exec_lines]
    out += ["---", ""]
    for tid, title, fields in tasks:
        out.append(f"## {tid} {title}")
        out.append("- [ ] 完成")
        out += [f"- {k}: {v}" for k, v in fields]
        out.append("")
    return "\n".join(out)


BASET = [("Covers", "R-1 / S-1"), ("Files", "`src/a.ts`"), ("Verify", "`npm test`"),
         ("Blocked-by", "—")]
F = {
    "old": md([], [
        ("T-1", "api", [("Covers", "R-1 / S-1, S-2"),
                        ("Files", "`internal/handler/contract.go`, `internal/service/contract.go`"),
                        ("Verify", "`go test ./internal/... -run TestExpiring`"), ("Blocked-by", "—")]),
        ("T-2", "fe", [("Covers", "R-1 / S-1, S-2"), ("Files", "`src/C.tsx`"),
                       ("Verify", "`npm test -- C`"), ("Blocked-by", "T-1")]),
        ("T-3", "click", [("Covers", "R-2 / S-3"), ("Files", "`src/C.tsx`"),
                          ("Verify", "`npm test -- C`"), ("Blocked-by", "T-2")])]),
    "par": md(["mode: parallel", "max_parallel_tasks: 2", "rebuild_integration_on_rework: true"], [
        ("T-1", "api", [("Covers", "R-1 / S-1"), ("Files", "`internal/handler/contract.go`"),
                        ("Verify", "`go test ./internal/handler/...`"), ("Blocked-by", "—")]),
        ("T-2", "card", [("Covers", "R-1 / S-2"), ("Files", "`src/components/Card.tsx`"),
                         ("Verify", "`npm test -- Card`"), ("Blocked-by", "—"),
                         ("Integrate-after", "T-1")]),
        ("T-3", "mig", [("Covers", "R-2 / S-3"), ("Files", "`migrations/0007.sql`"),
                        ("Verify", "`make migrate-test`"), ("Blocked-by", "—"), ("Risk", "high")]),
        ("T-4", "e2e", [("Covers", "R-1, R-2 / S-4"), ("Files", "`e2e/x.spec.ts`"),
                        ("Verify", "`npx pw`"), ("Blocked-by", "T-1, T-2")]),
        ("T-5", "docs", [("Covers", "R-3 / S-5"), ("Files", "`docs/specs/x.md`"),
                         ("Verify", "`bash c.sh`"), ("Blocked-by", "—"), ("Risk", "normal"),
                         ("Review-mode", "dedicated"), ("Semantic-conflicts-with", "T-2")])]),
    # 續行遮蔽:`Boundaries:`／`Intent:` 的續行寫成保留欄名子項。
    # 舊 last-write-wins 行為會靜默把 T-1 的 Files 換成整目錄、Verify 換成散文、
    # T-2 的 Risk 由 normal 變 high(review-mode 跟著變 dedicated),且 errors 為空。
    "boundshadow": "\n".join([
        "---", "feature: fx", "stage: 5-tasks", "status: approved", "---", "",
        "## T-1 api", "- [ ] 完成",
        "- Covers: R-1 / S-1",
        "- Files: `internal/handler/contract.go`, `internal/service/contract.go`",
        "- Verify: `go test ./internal/... -run TestExpiring`",
        "- Blocked-by: —",
        "- Boundaries: 查詢邏輯抽在 `service.ListExpiring`。",
        "  Design Boundary(摘自 4-spec):",
        "  - Files: `internal/handler/`, `internal/service/`, `internal/repo/`",
        "  - Verify: 依賴方向不得反向", "",
        "## T-2 fe", "- [ ] 完成",
        "- Covers: R-1 / S-2", "- Files: `src/C.tsx`", "- Verify: `npm test -- C`",
        "- Blocked-by: T-1", "- Risk: normal",
        "- Intent: dashboard 多了到期卡片。",
        "  補充:", "  - Risk: high", ""]),
    # 對照組:合法的純文字續寫(母版 example 的寫法)不得被誤判。
    "boundcont": "\n".join([
        "---", "feature: fx", "stage: 5-tasks", "status: approved", "---", "",
        "## T-1 api", "- [ ] 完成",
        "- Covers: R-1 / S-1",
        "- Files: `internal/handler/contract.go`, `internal/service/contract.go`",
        "- Verify: `go test ./internal/... -run TestExpiring`",
        "- Blocked-by: —",
        "- Boundaries: 查詢邏輯抽在 `service.ListExpiring`。",
        "  Design Boundary(摘自 4-spec,只取本 T 相關的最小子集):可動 handler／service／read repo;",
        "  依賴方向單向 handler → service → repo,禁反向;本 T 不擁有 contracts(唯讀)。",
        "- Owner: alice", ""]),
    "badmode": md(["mode: turbo"], [("T-1", "甲", BASET)]),
    "unknownkey": md(["mode: parallel", "max_parallel: 3"], [("T-1", "甲", BASET)]),
    "highwave": md(["mode: parallel"], [("T-1", "甲", BASET + [("Risk", "high"), ("Review-mode", "wave")])]),
    "seqbadref": md([], [("T-1", "甲", BASET + [("Integrate-after", "T-9")])]),
    "unknownref": md(["mode: parallel"], [("T-1", "甲", BASET[:3] + [("Blocked-by", "T-9")])]),
    "cycexec": md(["mode: parallel"], [
        ("T-1", "甲", BASET[:3] + [("Blocked-by", "T-2")]),
        ("T-2", "乙", [("Covers", "R-1 / S-2"), ("Files", "`src/b.ts`"), ("Verify", "`npm test`"),
                       ("Blocked-by", "T-1")])]),
    "cycinteg": md(["mode: parallel"], [
        ("T-1", "甲", BASET + [("Integrate-after", "T-2")]),
        ("T-2", "乙", [("Covers", "R-1 / S-2"), ("Files", "`src/b.ts`"), ("Verify", "`npm test`"),
                       ("Blocked-by", "T-1")])]),
    # R-1(engine-fence-masking):fence 內容對引擎必須視而不見,與 twin 判定一致。
    # S-1.1:fence 內的 `## T-99` 不長成任務。
    "fence_ghost": "\n".join([
        "---", "feature: fx", "stage: 5-tasks", "status: approved", "---", "",
        "## T-1 api", "- [ ] 完成",
        "- Covers: R-1 / S-1",
        "- Files: `internal/handler/contract.go`",
        "- Verify: `go test ./internal/... -run TestExpiring`",
        "- Blocked-by: —",
        "- Boundaries: 範例(勿照做):",
        "```",
        "## T-99 假任務",
        "- Files: `不存在/path.go`",
        "```", ""]),
    # S-1.2:fence 內的保留欄位行(`- Files: 假的`)不觸發重複欄 fail-closed,真值不變。
    "fence_field": "\n".join([
        "---", "feature: fx", "stage: 5-tasks", "status: approved", "---", "",
        "## T-1 api", "- [ ] 完成",
        "- Covers: R-1 / S-1",
        "- Files: `internal/handler/contract.go`",
        "- Verify: `go test ./internal/... -run TestExpiring`",
        "- Blocked-by: —",
        "- Boundaries: 範例(勿照做):",
        "```",
        "- Files: 假的",
        "```", ""]),
    # S-1.3(F-1 回歸):fence 外的重複保留欄仍 fail-closed,遮蔽不得誤傷真違規。
    "fence_dup_outside": "\n".join([
        "---", "feature: fx", "stage: 5-tasks", "status: approved", "---", "",
        "## T-1 api", "- [ ] 完成",
        "- Covers: R-1 / S-1",
        "- Files: `internal/handler/contract.go`",
        "- Files: `internal/other/contract.go`",
        "- Verify: `go test ./internal/... -run TestExpiring`",
        "- Blocked-by: —", ""]),
    # 未閉合 fence:遮到檔尾(含其後原本合法的 `## T-2`)—— 已知行為,見 _fence_mask docstring。
    "fence_unclosed": "\n".join([
        "---", "feature: fx", "stage: 5-tasks", "status: approved", "---", "",
        "## T-1 api", "- [ ] 完成",
        "- Covers: R-1 / S-1",
        "- Files: `internal/handler/contract.go`",
        "- Verify: `go test ./internal/... -run TestExpiring`",
        "- Blocked-by: —",
        "- Boundaries: 未閉合示例:",
        "```",
        "## T-2 fe",
        "- Covers: R-1 / S-2",
        "- Files: `src/C.tsx`",
        "- Verify: `npm test -- C`",
        "- Blocked-by: T-1", ""]),
    "overlap": md(["mode: parallel", "max_parallel_tasks: 3"], [
        ("T-1", "a", [("Covers", "R-1 / S-1"), ("Files", "`src/a.ts`"), ("Verify", "`npm test`"),
                      ("Blocked-by", "—")]),
        ("T-2", "ab", [("Covers", "R-1 / S-2"), ("Files", "`src/a.ts`, `src/b.ts`"),
                       ("Verify", "`npm test`"), ("Blocked-by", "—")]),
        ("T-3", "api", [("Covers", "R-2 / S-3"), ("Files", "`src/api/`"), ("Verify", "`npm test`"),
                        ("Blocked-by", "—")]),
        ("T-4", "apix", [("Covers", "R-2 / S-4"), ("Files", "`src/api/x.ts`"),
                         ("Verify", "`npm test`"), ("Blocked-by", "—")])]),
}

GATE_BASE = {
    "task": {"files": ["internal/handler/contract.go", "internal/handler/contract_test.go"],
             "verify": "go test ./internal/handler/... -run TestExpiring", "s_ids": ["S-1", "S-2"]},
    "pinned": {"base_sha": "aaaa1111", "contract_hash": "cafe0001"},
    "extra_allowed": [], "candidate_exists": True, "diff_applies": True,
    "candidate": {
        "schema": "devflow-candidate.v1", "feature": "expiry", "task": "T-1", "attempt": 1,
        "branch": "task/expiry/T-1", "base_sha": "aaaa1111", "candidate_sha": "bbbb2222",
        "prompt_id": "packet-expiry-T-1", "prompt_version": "v1", "contract_hash": "cafe0001",
        "verify": {"command": "go test ./internal/handler/... -run TestExpiring",
                   "exit_code": 0, "log": "verify.log"},
        "red": {"command": "go test ./internal/handler/... -run TestExpiring",
                "exit_code": 1, "log": "red.log", "at": "2026-08-02T10:00:00"},
        "green": {"command": "go test ./internal/handler/... -run TestExpiring",
                  "exit_code": 0, "log": "green.log", "at": "2026-08-02T10:20:00"},
        "test_names": ["TestExpiring_S1_returns_rows", "TestExpiring_S2_empty_state"],
        "changed_files": ["internal/handler/contract.go", "internal/handler/contract_test.go"],
        "created_at": "2026-08-02T10:21:00"},
}


def gate_bundle(**mut):
    b = json.loads(json.dumps(GATE_BASE))
    for key, val in mut.items():
        cur = b
        parts = key.split(".")
        for pk in parts[:-1]:
            cur = cur[pk]
        if val == "__DEL__":
            del cur[parts[-1]]
        else:
            cur[parts[-1]] = val
    return b


def gate_expect(bundle, verdict, failed):
    r = G.run_gate(bundle)
    got = {c["id"] for c in r["checks"] if c["status"] == "FAIL"}
    need(r["verdict"] == verdict and got == set(failed),
         f"verdict={r['verdict']} failed={sorted(got)} 期望 {verdict}/{sorted(failed)}")


REVIEW_OK = {"schema": "devflow-wave-review.v1", "feature": "expiry", "wave": 2,
             "tasks": [{"task": "T-3", "verdict": "PASS", "findings": []},
                       {"task": "T-4", "verdict": "FAIL",
                        "findings": [{"id": "F-1", "task": "T-4", "severity": "major",
                                      "evidence": "S-4 未處理 rows==0"}]}],
             "integration_verdict": "PASS", "reviewed_at": "2026-08-02T12:00:00"}
WAVE_TASKS = ["T-3", "T-4"]


def rv(mutator):
    r = json.loads(json.dumps(REVIEW_OK))
    mutator(r)
    return r


def pstate():
    return json.load(open(os.path.join(ROOT, ".devflow", "parallel.json")))


def head():
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def c_parse_old():
    p = L.parse_5_tasks(F["old"])
    need(p["errors"] == [], str(p["errors"]))
    e = p["execution"]
    need(e["mode"] == "sequential" and e["max_parallel_tasks"] == 3
         and e["rebuild_integration_on_rework"] is True, str(e))
    need([t["id"] for t in p["tasks"]] == ["T-1", "T-2", "T-3"])
    t2 = p["tasks"][1]
    need(t2["integrate_after"] == [] and t2["risk"] == "normal" and t2["review_mode"] == "wave")


def c_parse_boundshadow():
    """續行遮蔽必須 fail-closed,且首筆值不被覆蓋(scope 不得被放寬)。"""
    p = L.parse_5_tasks(F["boundshadow"])
    for key in ("Files", "Verify", "Risk"):
        need(any("重複保留欄" in e and key in e for e in p["errors"]),
             f"{key} 遮蔽未被拒收:{p['errors']}")
    t = {x["id"]: x for x in p["tasks"]}
    need(t["T-1"]["files"] == ["internal/handler/contract.go",
                               "internal/service/contract.go"], str(t["T-1"]["files"]))
    need(L.task_scope(p, "T-1") == sorted(t["T-1"]["files"]), str(L.task_scope(p, "T-1")))
    need(t["T-1"]["verify"] == "go test ./internal/... -run TestExpiring", t["T-1"]["verify"])
    need(t["T-2"]["risk"] == "normal" and t["T-2"]["review_mode"] != "dedicated",
         f"{t['T-2']['risk']}/{t['T-2']['review_mode']}")
    # A-6:即便續行遮蔽觸發 fail-closed,Boundaries/Intent 首筆值本身仍要進 task
    # dict(不因後面被判為重複保留欄而整欄消失)。
    need(t["T-1"]["boundaries"] == "查詢邏輯抽在 `service.ListExpiring`。",
         t["T-1"]["boundaries"])
    need(t["T-2"]["intent"] == "dashboard 多了到期卡片。", t["T-2"]["intent"])


def c_parse_boundcont():
    """合法的純文字續寫不得被誤判為重複欄(相容性對照組)。"""
    p = L.parse_5_tasks(F["boundcont"])
    need(p["errors"] == [], str(p["errors"]))
    t = p["tasks"][0]
    need(t["files"] == ["internal/handler/contract.go", "internal/service/contract.go"],
         str(t["files"]))
    need(t["verify"] == "go test ./internal/... -run TestExpiring", t["verify"])
    # A-6:Boundaries/Intent/Owner 現在真的進 task dict,不再解析後就丟棄。
    need(t["boundaries"] == "查詢邏輯抽在 `service.ListExpiring`。", t["boundaries"])
    need(t["owner"] == "alice", t["owner"])


def c_parse_fence_ghost():
    """S-1.1:fence 內的 `## T-99` 標題不長成任務。"""
    p = L.parse_5_tasks(F["fence_ghost"])
    need(p["errors"] == [], str(p["errors"]))
    need([t["id"] for t in p["tasks"]] == ["T-1"], str([t["id"] for t in p["tasks"]]))


def c_parse_fence_field():
    """S-1.2:fence 內的保留欄位行不觸發重複欄 fail-closed;真值不變。"""
    p = L.parse_5_tasks(F["fence_field"])
    need(p["errors"] == [], str(p["errors"]))
    need(p["tasks"][0]["files"] == ["internal/handler/contract.go"],
         str(p["tasks"][0]["files"]))


def c_parse_fence_dup_outside():
    """S-1.3(F-1 回歸):fence 外的重複保留欄仍 fail-closed。"""
    errs = L.parse_5_tasks(F["fence_dup_outside"])["errors"]
    need(any("重複保留欄" in e and "Files" in e for e in errs), str(errs))


def c_parse_fence_unclosed():
    """未閉合 fence 遮到檔尾,含其後的 `## T-2`(已知行為,見 _fence_mask docstring)。"""
    p = L.parse_5_tasks(F["fence_unclosed"])
    need(p["errors"] == [], str(p["errors"]))
    need([t["id"] for t in p["tasks"]] == ["T-1"], str([t["id"] for t in p["tasks"]]))


def c_parse_parallel():
    p = L.parse_5_tasks(F["par"])
    need(p["errors"] == [], str(p["errors"]))
    need(p["execution"]["mode"] == "parallel" and p["execution"]["max_parallel_tasks"] == 2)
    t = {x["id"]: x for x in p["tasks"]}
    need(t["T-2"]["integrate_after"] == ["T-1"])
    need(t["T-3"]["risk"] == "high" and t["T-3"]["review_mode"] == "dedicated")
    need(t["T-5"]["risk"] == "normal" and t["T-5"]["review_mode"] == "dedicated")
    need(t["T-5"]["semantic_conflicts"] == ["T-2"])
    need(t["T-4"]["blocked_by"] == ["T-1", "T-2"] and t["T-1"]["blocked_by"] == [])


def c_parse_badmode():
    need(any("turbo" in e for e in L.parse_5_tasks(F["badmode"])["errors"]))


def c_parse_unknownkey():
    errs = L.parse_5_tasks(F["unknownkey"])["errors"]
    need(any("max_parallel" in e and "未知" in e for e in errs), str(errs))


def c_parse_highwave():
    errs = L.parse_5_tasks(F["highwave"])["errors"]
    need(any("high" in e and "wave" in e for e in errs), str(errs))


def c_parse_seqbadref():
    need(any("T-9" in e for e in L.parse_5_tasks(F["seqbadref"])["errors"]))


def c_parse_unknownref():
    need(any("T-9" in e for e in L.parse_5_tasks(F["unknownref"])["errors"]))


def c_parse_cycexec():
    errs = L.parse_5_tasks(F["cycexec"])["errors"]
    need(any("環" in e and "T-1" in e and "T-2" in e for e in errs), str(errs))


def c_parse_cycinteg():
    need(any("環" in e for e in L.parse_5_tasks(F["cycinteg"])["errors"]))


def c_dag_edges():
    p = L.parse_5_tasks(F["par"])
    need(L.execution_edges(p) == {("T-1", "T-4"), ("T-2", "T-4")})
    need(L.integration_edges(p) == {("T-1", "T-4"), ("T-2", "T-4"), ("T-1", "T-2")})


def c_waves_basic():
    p = L.parse_5_tasks(F["par"])
    w = L.compute_waves(p)
    need(w == [["T-1", "T-2"], ["T-3", "T-4"], ["T-5"]], str(w))
    need(L.compute_waves(p) == w, "決定論")
    snap = json.dumps(p, sort_keys=True, default=str)
    L.compute_waves(p)
    need(json.dumps(p, sort_keys=True, default=str) == snap, "不回寫輸入")
    need(all(len(x) <= 2 for x in w), "max_parallel 上限")


def c_waves_restart():
    p = L.parse_5_tasks(F["par"])
    need(L.compute_waves(p, done={"T-1", "T-2"}) == [["T-3", "T-4"], ["T-5"]])


def c_waves_overlap():
    p = L.parse_5_tasks(F["overlap"])
    need(p["errors"] == [], str(p["errors"]))
    w = L.compute_waves(p)
    need(w == [["T-1", "T-3"], ["T-2", "T-4"]], str(w))


def c_waves_semconflict():
    p = L.parse_5_tasks(F["par"])
    w = L.compute_waves(p, max_parallel=4)
    at = {t: i for i, x in enumerate(w) for t in x}
    need(at["T-2"] != at["T-5"], str(w))


def c_waves_seq_refuse():
    try:
        L.compute_waves(L.parse_5_tasks(F["old"]))
    except L.ContractError:
        return
    bad("sequential 未拒派生 wave")


def c_task_scope():
    p = L.parse_5_tasks(F["par"])
    need(L.task_scope(p, "T-2") == ["src/components/Card.tsx"])
    o = L.parse_5_tasks(F["overlap"])
    need(L.task_scope(o, "T-3") == ["src/api/"])
    need(L.files_overlap("src/api/", "src/api/x.ts") and not L.files_overlap("src/a.ts", "src/b.ts"))


def c_statemachine():
    happy = ["PENDING", "READY", "RUNNING", "CANDIDATE", "MECHANICAL_PASS",
             "QUEUED_FOR_INTEGRATION", "INTEGRATED", "IN_REVIEW", "ACCEPTED"]
    need(all(L.is_legal_transition(a, b) for a, b in zip(happy, happy[1:])))
    need(L.is_legal_transition("MECHANICAL_PASS", "IN_REVIEW")
         and L.is_legal_transition("IN_REVIEW", "QUEUED_FOR_INTEGRATION"))
    for a, b in (("CANDIDATE", "ACCEPTED"), ("RUNNING", "INTEGRATED"),
                 ("MECHANICAL_PASS", "ACCEPTED"), ("REWORK", "ACCEPTED"),
                 ("PENDING", "RUNNING")):
        need(not L.is_legal_transition(a, b), f"{a}→{b} 應非法")
    need([s for s in L.STATES if L.can_tick(s)] == ["ACCEPTED"])


def c_run_id():
    a, b = L.new_run_id(), L.new_run_id()
    need(L.RUN_ID_RE.match(a) and L.RUN_ID_RE.match(b) and a != b, f"{a} {b}")


def c_gate_pass():
    r = G.run_gate(GATE_BASE)
    need(r["verdict"] == "PASS", str(r))
    need([c["id"] for c in r["checks"]] == G.GATE_CHECK_IDS, "14 檢查順序固定")
    need(r["schema"] == "devflow-gate-result.v1" and r["checked_at"] == "")


def c_gate_scope_excess():
    gate_expect(gate_bundle(**{"task.s_ids": ["S-1"],
                               "candidate.test_names": ["TestExpiring_S1_returns_rows"],
                               "candidate.changed_files": ["internal/handler/contract.go", "src/evil.ts"]}),
                "FAIL", {"files_within_scope"})


def c_gate_red_after_green():
    gate_expect(gate_bundle(**{"candidate.red.at": "2026-08-02T11:00:00"}),
                "FAIL", {"red_before_green"})


def c_gate_contract_drift():
    gate_expect(gate_bundle(**{"candidate.contract_hash": "dead9999"}),
                "FAIL", {"contract_hash_unchanged"})


def c_gate_verify_mismatch():
    gate_expect(gate_bundle(**{"candidate.verify.command": "go test ./... -run TestOther"}),
                "FAIL", {"verify_command_match"})


def c_gate_verify_fail():
    gate_expect(gate_bundle(**{"candidate.verify.exit_code": 1}), "FAIL", {"verify_exit_zero"})


def c_gate_missing_red():
    gate_expect(gate_bundle(**{"candidate.red": None}),
                "FAIL", {"red_present_failing", "red_before_green"})


def c_gate_protected():
    files = ["internal/handler/contract.go", "docs/dev/expiry/4-spec.md",
             "docs/dev/expiry/6-implementation-notes.md"]
    gate_expect(gate_bundle(**{"task.files": files, "candidate.changed_files": files}),
                "FAIL", {"protected_untouched", "shared_docs_untouched"})


def c_gate_missing_sid():
    gate_expect(gate_bundle(**{"candidate.test_names": ["TestExpiring_S1_returns_rows"]}),
                "FAIL", {"s_id_present"})


def c_sids_of_dotted():
    """A-2 ①:_s_ids_of 對點號分層 covers 非恆空(母版/實務慣例寫法,不帶連字號)。
    範圍寫法 S1.1–S1.4 只抓兩端點,不展開成 S1.2/S1.3(known limitation)。"""
    ids = G._s_ids_of("R1 / S1.1–S1.4、S2.5")
    need(ids == ["S1.1", "S1.4", "S2.5"], str(ids))


def c_sids_of_legacy():
    """A-2 ④:舊形 S-13(連字號、無點)仍通。"""
    need(G._s_ids_of("R1 / S-13") == ["S-13"], str(G._s_ids_of("R1 / S-13")))


def c_gate_sid_dotted_present():
    """A-2 ②:S1.1/S1.4/S2.5 都有對應測試名(底線續寫或原樣皆可)→ s_id_present
    True,gate 整體 PASS。"""
    gate_expect(gate_bundle(**{
        "task.s_ids": ["S1.1", "S1.4", "S2.5"],
        "candidate.test_names": ["Test_S_1_1_ok", "TestS1_4_ok", "Test_S_2_5_ok"],
    }), "PASS", set())


def c_gate_sid_dotted_missing():
    """A-2 ③:少一條測試名(S2.5 沒有對應測試)→ s_id_present False。"""
    gate_expect(gate_bundle(**{
        "task.s_ids": ["S1.1", "S1.4", "S2.5"],
        "candidate.test_names": ["Test_S_1_1_ok", "TestS1_4_ok"],
    }), "FAIL", {"s_id_present"})


def c_gate_sid_boundary_no_overmatch():
    """MED-2(第二批獨立審查):_sid_matched 的 (?!\\d) 尾端邊界回歸釘。S1.1 不得
    誤配到多一位數字的測試名 Test_S_1_12_x(那其實是 S1.12,不是 S1.1)。"""
    gate_expect(gate_bundle(**{
        "task.s_ids": ["S1.1"],
        "candidate.test_names": ["Test_S_1_12_x"],
    }), "FAIL", {"s_id_present"})


def c_gate_sid_boundary_matches_exact():
    """對照組:候選裡若真的有精準符合的測試名(即使旁邊混了 S1.12 這種近似項),
    仍要判定 True —— 證明上一案是邊界問題,不是規則本身失效。"""
    gate_expect(gate_bundle(**{
        "task.s_ids": ["S1.1"],
        "candidate.test_names": ["Test_S_1_1_x", "Test_S_1_12_y"],
    }), "PASS", set())


def c_gate_schema_incomplete():
    gate_expect(gate_bundle(**{"candidate.prompt_version": "__DEL__",
                               "candidate.test_names": "__DEL__"}),
                "FAIL", {"result_schema_complete", "s_id_present"})


def c_review_ok():
    need(L.validate_wave_review(REVIEW_OK, WAVE_TASKS) == [])


def c_review_missing_verdict():
    r = rv(lambda x: x["tasks"].pop(1))
    need(any("T-4" in e for e in L.validate_wave_review(r, WAVE_TASKS)))


def c_review_unattributed():
    r = rv(lambda x: x["tasks"][1]["findings"][0].pop("task"))
    need(any("歸屬" in e for e in L.validate_wave_review(r, WAVE_TASKS)))


def c_review_no_integration():
    r = rv(lambda x: x.pop("integration_verdict"))
    need(any("integration_verdict" in e for e in L.validate_wave_review(r, WAVE_TASKS)))


def c_review_duplicate():
    r = rv(lambda x: x["tasks"].append({"task": "T-4", "verdict": "PASS", "findings": []}))
    need(any("重複" in e and "T-4" in e for e in L.validate_wave_review(r, WAVE_TASKS)))


def c_legacy_exec_v4():
    # §7 前置修復(2026-08-19):legacy sequential start 過去不寫 schema/run_id,
    # 派工分層守衛(_dispatch_impl.py)整支失效。現在改寫 exec-v4 + 真 run_id ——
    # 仍不是 task-scoped(不帶 "task" 欄),v1 相容欄位(scope/baseline/契約 hash
    # 等)原樣保留,不因補 schema/run_id 而消失。
    d = json.load(open(os.path.join(ROOT, ".devflow", "exec.json")))
    need(d.get("schema") == "exec-v4", f"schema={d.get('schema')!r}(應為 exec-v4)")
    need(bool(L.RUN_ID_RE.match(d.get("run_id", ""))), f"run_id={d.get('run_id')!r} 格式不對")
    need("task" not in d, f"legacy sequential 不應被判為 task-scoped:{sorted(d)}")
    for k in ("slug", "started", "scope", "extra", "baseline", "contract_hashes",
              "contract_hash_scope"):
        need(k in d, f"缺 v1 相容欄位 {k}")


def c_exec_v3():
    d = json.load(open(os.path.join(ROOT, ".devflow", "exec.json")))
    h = head()
    need(d.get("schema") == "exec-v3", "schema")
    need(bool(L.RUN_ID_RE.match(d.get("run_id", ""))), f"run_id={d.get('run_id')}")
    need(d.get("task") == "T-1" and d.get("mode") == "parallel" and d.get("state") == "RUNNING")
    need(d.get("scope") == ["src/a.py"], f"scope={d.get('scope')}(task-scoped = 單 T Files)")
    need(d.get("wave", {}).get("number") == 1 and d.get("wave", {}).get("wave_base_sha") == h)
    need(d.get("candidate_sha") is None and d.get("feature_initial_base") == h)
    for k in ("slug", "started", "scope", "extra", "baseline", "contract_hashes",
              "contract_hash_scope"):
        need(k in d, f"缺 v1 相容欄位 {k}")
    # A-6:task-scoped exec.json 是派工者拿 boundaries/intent 的最小露出點之一,
    # 不必回頭重讀 5-tasks。
    need(d.get("boundaries") == "只能動 `src/a.py`,不得動其他檔。",
         f"boundaries={d.get('boundaries')!r}")
    need(d.get("intent") == "補上最小 API 回應。", f"intent={d.get('intent')!r}")
    need(d.get("owner") == "alice", f"owner={d.get('owner')!r}")


def c_parallel_init():
    p = pstate()
    need(p["schema"] == "devflow-parallel.v1" and p["slug"] == "pf")
    need(all(r["state"] == "PENDING" for r in p["tasks"].values()))
    need(re.fullmatch(r"[0-9a-f]{16}", p["contract_hash"] or ""), p.get("contract_hash"))
    need(p["feature_initial_base"] == head())
    need(p["current_wave"] is None and p["wave_number"] == 0)


def c_plan():
    r = subprocess.run([os.path.join(H, "devflow-exec.sh"), "plan", "pf"],
                       cwd=ROOT, capture_output=True, text=True)
    need(r.returncode == 0, r.stdout + r.stderr)
    out = json.loads(r.stdout)
    need(out["waves"] == [["T-1", "T-2"], ["T-3"]], str(out["waves"]))
    need(["T-1", "T-2"] in out["integration_edges"], str(out["integration_edges"]))
    need(["T-1", "T-3"] in out["execution_edges"], str(out["execution_edges"]))
    # A-6:plan 輸出的 tasks 物件現在帶 boundaries/intent/owner(派工者的另一個
    # 最小露出點);T-2 沒填 Boundaries/Intent/Owner → 缺省空字串,不是恆真。
    t1 = out["tasks"]["T-1"]
    need(t1["boundaries"] == "只能動 `src/a.py`,不得動其他檔。", str(t1))
    need(t1["intent"] == "補上最小 API 回應。", str(t1))
    need(t1["owner"] == "alice", str(t1))
    t2 = out["tasks"]["T-2"]
    need(t2["boundaries"] == "" and t2["intent"] == "" and t2["owner"] == "", str(t2))


def c_wave_open1():
    p = pstate()
    cw = p["current_wave"]
    need(cw and cw["number"] == 1 and cw["tasks"] == ["T-1", "T-2"], str(cw))
    need(cw["wave_base_sha"] == head())
    need(p["tasks"]["T-1"]["state"] == "READY" and p["tasks"]["T-2"]["state"] == "READY")
    need(p["tasks"]["T-1"]["wave_base_sha"] == cw["wave_base_sha"], "wave-open 釘 base")


def c_cand_base():
    p = pstate()
    r = p["tasks"]["T-1"]
    need(r["state"] == "CANDIDATE" and r["candidate_status"] == "VALID")
    need(r["candidate_base_sha"] == r["wave_base_sha"], "candidate_base_sha = wave base(OC-3)")


def c_skill_events():
    text = open(os.path.join(H, "..", "skills", "dev-run", "SKILL.md"),
                encoding="utf-8").read()
    toks = ["devflow-exec.sh event", "agent_dispatched", "attempt_started",
            "attempt_completed", "failure_category", "review_started", "review_completed",
            "finding_created", "task_rework_requested", "task_escalated",
            "candidate_created", "task_accepted", "stage_completed", "run_completed",
            "derive", "prompt-registry.json", "禁佔位"]
    missing = [t for t in toks if t not in text]
    need(not missing, f"dev-run SKILL 缺 W3/W5 事件動作 token:{missing}")


def c_skill_parallel_route():
    text = open(os.path.join(H, "..", "skills", "dev-flow", "SKILL.md"),
                encoding="utf-8").read()
    need("execution.mode: parallel" in text and "並行引擎" in text,
         "dev-flow SKILL Stage 6 缺並行引擎路由句")


def c_reviews_reg():
    p = pstate()
    rv = (p.get("reviews") or {}).get("1") or {}
    need(rv.get("tasks", {}).get("T-1") == "PASS" and rv.get("tasks", {}).get("T-2") == "PASS",
         f"wave 1 review 未登記或 verdict 不對:{rv}")
    need(rv.get("integration_verdict") == "PASS")


def c_invalidated():
    p = pstate()
    need(p["tasks"]["T-3"]["candidate_status"] == "INVALIDATED_BY_UPSTREAM")
    need(all(e["task"] != "T-1" for e in p["integration_log"]), "T-1 已移出 integration_log")
    need(any(e["task"] == "T-2" for e in p["integration_log"]), "T-2 存活")


def c_wave3():
    p = pstate()
    cw = p["current_wave"]
    need(cw and cw["number"] == 3 and cw["tasks"] == ["T-1"], str(cw))


CHECKS = {k[2:].replace("_", "-"): v for k, v in list(globals().items())
          if k.startswith("c_") and callable(v)}
fn = CHECKS.get(CHECK)
if fn is None:
    bad(f"unknown check {CHECK}(有:{sorted(CHECKS)})")
fn()
sys.exit(0)
P1PY
}

p1c() { "$DEVFLOW_PY" "$P1D/p1check.py" "$H" "$1" "${2:-}" >/dev/null 2>&1; echo $?; }
p1x() { "$H/devflow-exec.sh" "$@" >/dev/null 2>&1; echo $?; }
p1x_cap() { P1X_OUT=$("$H/devflow-exec.sh" "$@" 2>&1); P1X_RC=$?; }
p1g() { echo "{\"tool_name\":\"$1\",\"tool_input\":{\"file_path\":\"$P1T/$2\"}}" | "$H/devflow-guard.sh" >/dev/null 2>&1; echo $?; }
p1g_cap() { P1G_OUT=$(echo "{\"tool_name\":\"$1\",\"tool_input\":{\"file_path\":\"$P1T/$2\"}}" | "$H/devflow-guard.sh" 2>&1); P1G_RC=$?; }
p1pb() { echo "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$1\"}}" | "$H/devflow-prebash.sh" >/dev/null 2>&1; echo $?; }
p1post() { echo '{}' | "$H/devflow-postbash.sh" >/dev/null 2>&1; echo $?; }
p1post_cap() { P1P_OUT=$(echo '{}' | "$H/devflow-postbash.sh" 2>&1); P1P_RC=$?; }

p1_setup_repo() {
  P1T=$(mktemp -d "${TMPDIR:-/tmp}/devflow-p1rt.XXXXXX")
  mkdir -p "$P1T/docs/dev/pf" "$P1T/docs/dev/pf2" "$P1T/src"
  cd "$P1T" || exit 1
  git init -q . && git config user.email t@t && git config user.name t
  printf -- "---\nstatus: approved\n---\n" > docs/dev/pf/4-spec.md
  cat > docs/dev/pf/5-tasks.md <<'EOF'
---
feature: pf
stage: 5-tasks
status: approved
execution:
  mode: parallel
  max_parallel_tasks: 2
---

# 5. 任務(p1 runtime fixture)

## T-1 甲
- [ ] 完成
- Covers: R-1 / S-1
- Files: `src/a.py`
- Verify: `true`
- Blocked-by: —
- Boundaries: 只能動 `src/a.py`,不得動其他檔。
- Intent: 補上最小 API 回應。
- Owner: alice

## T-2 乙
- [ ] 完成
- Covers: R-1 / S-2
- Files: `src/b.py`
- Verify: `true`
- Blocked-by: —
- Integrate-after: T-1

## T-3 丙
- [ ] 完成
- Covers: R-2 / S-3
- Files: `src/c.py`
- Verify: `true`
- Blocked-by: T-1
- Risk: high
EOF
  printf -- "---\nstatus: approved\n---\n- lane: fast\n- Risk: high\n" > docs/dev/pf2/4-spec.md
  printf '%s\n' '## T-1 fixture' '- Covers: R-1' '- Files: src/p2.py' '- Verify: `true`' \
    '- Blocked-by: —' > docs/dev/pf2/5-tasks.md
  echo a > src/a.py; echo b > src/b.py; echo c > src/c.py
  git add -A >/dev/null && git commit -qm p1init
}

echo "-- p1 契約battery:parser / DAG / wave / 狀態機 / run_id --"
p1_setup_battery
ck "p1 舊格式解析+全缺省"            0 "$(p1c parse-old)"
ck "p1 parallel 全欄位解析"          0 "$(p1c parse-parallel)"
ck "p1 續行遮蔽保留欄拒收+首筆不被覆蓋" 0 "$(p1c parse-boundshadow)"
ck "p1 合法純文字續寫不被誤判"        0 "$(p1c parse-boundcont)"
ck "p1 R-1 fence 內 T-99 不長成任務"  0 "$(p1c parse-fence-ghost)"
ck "p1 R-1 fence 內假重複欄不 fail-closed" 0 "$(p1c parse-fence-field)"
ck "p1 R-1 fence 外重複欄仍 fail-closed(回歸)" 0 "$(p1c parse-fence-dup-outside)"
ck "p1 R-1 未閉合 fence 遮到檔尾"     0 "$(p1c parse-fence-unclosed)"
ck "p1 非法 mode 拒收"               0 "$(p1c parse-badmode)"
ck "p1 execution 未知 key 拒收"      0 "$(p1c parse-unknownkey)"
ck "p1 high+wave 拒收"               0 "$(p1c parse-highwave)"
ck "p1 sequential 也驗新欄位引用"    0 "$(p1c parse-seqbadref)"
ck "p1 Blocked-by 引用不存在拒收"    0 "$(p1c parse-unknownref)"
ck "p1 execution DAG 環拒收+列路徑"  0 "$(p1c parse-cycexec)"
ck "p1 integration DAG 環拒收"       0 "$(p1c parse-cycinteg)"
ck "p1 雙 DAG 邊集合"                0 "$(p1c dag-edges)"
ck "p1 waves 決定論+不回寫+上限"     0 "$(p1c waves-basic)"
ck "p1 waves restart done 重算"      0 "$(p1c waves-restart)"
ck "p1 waves Files overlap 分離"     0 "$(p1c waves-overlap)"
ck "p1 waves 語意衝突禁同 wave"      0 "$(p1c waves-semconflict)"
ck "p1 sequential 拒派生 wave"       0 "$(p1c waves-seq-refuse)"
ck "p1 task scope=單 T Files"        0 "$(p1c task-scope)"
ck "p1 狀態機合法/非法全集"          0 "$(p1c statemachine)"
ck "p1 run_id 格式+唯一"             0 "$(p1c run-id)"
ck "p1 dev-run SKILL 含 W3/W5 事件動作" 0 "$(p1c skill-events)"
ck "p1 dev-flow SKILL Stage 6 並行路由句" 0 "$(p1c skill-parallel-route)"

echo "-- p1 Mechanical Gate(14 項;對拍 gate fixtures)--"
ck "p1 gate 全 PASS+順序+schema"     0 "$(p1c gate-pass)"
ck "p1 gate scope 超界"              0 "$(p1c gate-scope-excess)"
ck "p1 gate red 晚於 green"          0 "$(p1c gate-red-after-green)"
ck "p1 gate 契約 hash 漂移"          0 "$(p1c gate-contract-drift)"
ck "p1 gate verify 指令不符"         0 "$(p1c gate-verify-mismatch)"
ck "p1 gate verify 紅"               0 "$(p1c gate-verify-fail)"
ck "p1 gate 缺 RED"                  0 "$(p1c gate-missing-red)"
ck "p1 gate 碰保護檔+共享文件"       0 "$(p1c gate-protected)"
ck "p1 gate 缺 S-id 測試名"          0 "$(p1c gate-missing-sid)"
ck "p1 A-2 s_ids_of 點號分層非恆空"  0 "$(p1c sids-of-dotted)"
ck "p1 A-2 s_ids_of 舊形仍通"        0 "$(p1c sids-of-legacy)"
ck "p1 A-2 gate 點號 sid 有測試名 PASS" 0 "$(p1c gate-sid-dotted-present)"
ck "p1 A-2 gate 點號 sid 少測試名 FAIL" 0 "$(p1c gate-sid-dotted-missing)"
ck "p1 MED-2 _sid_matched 尾端邊界不誤配(S1.1≠Test_S_1_12_x)" 0 "$(p1c gate-sid-boundary-no-overmatch)"
ck "p1 MED-2 _sid_matched 精準符合對照組仍判 True"           0 "$(p1c gate-sid-boundary-matches-exact)"
ck "p1 gate schema 不完整"           0 "$(p1c gate-schema-incomplete)"

echo "-- p1 wave review 驗證(對拍 review fixtures)--"
ck "p1 review 合法樣本"              0 "$(p1c review-ok)"
ck "p1 review 缺 per-T verdict"      0 "$(p1c review-missing-verdict)"
ck "p1 review finding 無歸屬"        0 "$(p1c review-unattributed)"
ck "p1 review 缺 integration"        0 "$(p1c review-no-integration)"
ck "p1 review 重複 entry"            0 "$(p1c review-duplicate)"

echo "-- p1 runtime:OC-4 fast+high / task-scoped start / guard --"
p1_setup_repo
p1x_cap start pf2
ck_msg "p1 OC-4 fast+high → start 拒" 1 "lane: fast + Risk: high" "$P1X_RC" "$P1X_OUT"
# F3:雜訊行(同行含 Owner Call/fast/high 字樣但非結構化裁決欄)不得觸發例外
printf -- "附註:標題行提過 Owner Call 將討論 fast 與 high 風險議題(非裁決)\n" >> docs/dev/pf2/4-spec.md
git add docs/dev/pf2/4-spec.md && git commit -qm oc-noise >/dev/null
p1x_cap start pf2
ck_msg "p1 F3:雜訊行不觸發 owner-call 例外" 1 "lane: fast + Risk: high" "$P1X_RC" "$P1X_OUT"
printf -- "- Owner Call 例外:\n" >> docs/dev/pf2/4-spec.md
git add docs/dev/pf2/4-spec.md && git commit -qm oc-empty >/dev/null
p1x_cap start pf2
ck_msg "p1 F3:例外欄無理由不生效" 1 "lane: fast + Risk: high" "$P1X_RC" "$P1X_OUT"
printf -- "- Owner Call 例外:同意 fast+high(test fixture)\n" >> docs/dev/pf2/4-spec.md
git add docs/dev/pf2/4-spec.md && git commit -qm oc >/dev/null
ck "p1 OC-4 owner-call 例外放行"     0 "$(p1x start pf2)"
ck "p1 legacy start 產生 exec-v4 schema+run_id(v1 相容欄位仍在,非 task-scoped)" 0 "$(p1c legacy-exec-v4 "$P1T")"
"$H/devflow-exec.sh" stop >/dev/null 2>&1
# G3 回歸(2026-08-17):**全形冒號**版的 Owner Call 例外必須同樣生效。字元集曾把
# 「:或：」打成兩個半形冒號(0x3a×2),全形版被判成沒寫例外 → fast+high 明明寫了
# 例外卻開不了工,而且不知道為什麼(採用專案實踩)。
printf -- "---\nstatus: approved\n---\n- lane: fast\n- Risk: high\n- Owner Call 例外：同意 fast+high(全形冒號 fixture)\n" > docs/dev/pf2/4-spec.md
git add docs/dev/pf2/4-spec.md && git commit -qm oc-fullwidth >/dev/null
ck "p1 G3 回歸:全形冒號 Owner Call 例外同樣放行" 0 "$(p1x start pf2)"
"$H/devflow-exec.sh" stop >/dev/null 2>&1
p1x_cap start pf2 --task T-1
ck_msg "p1 sequential 檔 --task → 拒" 1 "execution.mode: parallel" "$P1X_RC" "$P1X_OUT"
p1x_cap start pf --task T-9
ck_msg "p1 --task 指不存在 T → 拒"   1 "找不到 T-9" "$P1X_RC" "$P1X_OUT"
ck "p1 start --task 啟動"            0 "$(p1x start pf --task T-1)"
ck "p1 exec.json v3 schema+run_id+單 T scope" 0 "$(p1c exec-v3 "$P1T")"
OLDSCHEMA=$(mktemp -d "${TMPDIR:-/tmp}/devflow-oldschema.XXXXXX")
mkdir -p "$OLDSCHEMA/.devflow"
printf '%s\n' '{"schema":"exec-v2","slug":"old","task":"T-1","mode":"parallel","scope":["src/a.py"],"extra":[],"baseline":{},"contract_hashes":{},"contract_hash_scope":"repo-wide-v1","wave":{"number":1,"wave_base_sha":"deadbeef"},"candidate_sha":null,"state":"RUNNING","attempt":0,"feature_initial_base":"deadbeef"}' > "$OLDSCHEMA/.devflow/exec.json"
OLD_OUT=$(cd "$OLDSCHEMA" && "$H/devflow-exec.sh" status 2>&1); OLD_RC=$?
ck_msg "回歸:舊 exec-v2 schema 字面值仍被 status 辨識為 task-scoped" 0 "task=T-1" "$OLD_RC" "$OLD_OUT"
rm -rf "$OLDSCHEMA"
p1x_cap status
ck_msg "p1 status v2 顯示 task"      0 "task=T-1" "$P1X_RC" "$P1X_OUT"
ck_msg "p1 status v2 顯示 state"     0 "state=RUNNING" "$P1X_RC" "$P1X_OUT"
ck "p1 task guard:放行本 T Files"    0 "$(p1g Write src/a.py)"
ck "p1 task guard:擋他 T Files"      2 "$(p1g Write src/b.py)"
p1g_cap Write docs/dev/pf/5-tasks.md
ck_msg "p1 task guard:5-tasks 移出恆許" 2 "單寫者" "$P1G_RC" "$P1G_OUT"
ck "p1 task guard:6-notes 移出恆許"  2 "$(p1g Write docs/dev/pf/6-implementation-notes.md)"
ck "p1 task guard:evidence 專區放行" 0 "$(p1g Write .devflow/task/T-1/red.log)"
ck "p1 task guard:他 T evidence 擋"  2 "$(p1g Write .devflow/task/T-2/red.log)"
ck "p1 task guard:exec.json 仍禁"    2 "$(p1g Edit .devflow/exec.json)"
ck "p1 task prebash:redirect 自己 evidence 放行" 0 "$(p1pb 'go test > .devflow/task/T-1/red.log 2>&1')"
ck "p1 task prebash:redirect 他 T evidence 擋" 2 "$(p1pb 'echo x > .devflow/task/T-2/red.log')"
ck "p1 task prebash:仍擋刪旗標"      2 "$(p1pb 'rm -f .devflow/exec.json')"
ck "p1 task prebash:仍擋 sentinel"   2 "$(p1pb 'rm -f .git/devflow-armed')"
mkdir -p .devflow/task/T-1 && echo log > .devflow/task/T-1/red.log
ck "p1 task postbash:evidence 區沉默" 0 "$(p1post)"
echo sneak >> docs/dev/pf/5-tasks.md
p1post_cap
ck_msg "p1 task postbash:抓共享文件 shell 改動" 2 "docs/dev/pf/5-tasks.md" "$P1P_RC" "$P1P_OUT"
git checkout -q -- docs/dev/pf/5-tasks.md
ck "p1 同 slug 異 task → 拒"         1 "$(p1x start pf --task T-2)"
ck "p1 task 武裝中 feature start → 拒" 1 "$(p1x start pf)"
ck "p1 同 slug 同 task re-arm"       0 "$(p1x start pf --task T-1)"
p1x_cap start pf --task T-1 --base deadbeef
ck_msg "p1 --base 與 HEAD 不符 → 拒" 1 "不符" "$P1X_RC" "$P1X_OUT"
P1SHA=$(git rev-parse HEAD)
ck "p1 candidate 登記(RUNNING→CANDIDATE)" 0 "$(p1x candidate "$P1SHA")"
p1x_cap status
ck_msg "p1 status 顯示 candidate 狀態" 0 "state=CANDIDATE" "$P1X_RC" "$P1X_OUT"
ck "p1 candidate 假 SHA → 拒"        1 "$(p1x candidate 00000000)"
"$H/devflow-exec.sh" stop >/dev/null 2>&1

echo "-- p1 runtime:wave 排程 / 狀態機 / OC-3 invalidation --"
ck "p1 parallel-init"                0 "$(p1x parallel-init pf)"
p1x_cap parallel-init pf
ck_msg "p1 parallel-init 拒重複"     1 "已存在" "$P1X_RC" "$P1X_OUT"
ck "p1 parallel-init state 正確"     0 "$(p1c parallel-init "$P1T")"
ck "p1 plan waves+雙 DAG 輸出"       0 "$(p1c plan "$P1T")"
ck "p1 wave-open"                    0 "$(p1x wave-open pf)"
ck "p1 wave-open state(同 Wave 同 Base)" 0 "$(p1c wave-open1 "$P1T")"
p1x_cap wave-open pf
ck_msg "p1 wave 未關不得再開"        1 "wave-close" "$P1X_RC" "$P1X_OUT"
p1x_cap task-state pf T-2 IN_REVIEW
ck_msg "p1 非法轉移拒(READY→IN_REVIEW)" 1 "非法轉移" "$P1X_RC" "$P1X_OUT"
ck "p1 READY→RUNNING"                0 "$(p1x task-state pf T-1 RUNNING)"
# F1:candidate 變更必須真的在目前 branch 才准 INTEGRATED
"$H/devflow-exec.sh" task-candidate pf T-1 deadbeef00 >/dev/null 2>&1
p1x_cap task-integrate pf T-1
ck_msg "p1 F1:candidate SHA 非 commit 不得整合" 1 "不是本 repo" "$P1X_RC" "$P1X_OUT"
echo impl1 > src/a.py && git add src/a.py && git commit -qm p1cand1 && P1C1=$(git rev-parse HEAD)
ck "p1 task-candidate 登記"          0 "$(p1x task-candidate pf T-1 "$P1C1")"
ck "p1 candidate_base_sha=wave base(OC-3)" 0 "$(p1c cand-base "$P1T")"
p1x_cap task-state pf T-1 ACCEPTED
ck_msg "p1 未整合不得 ACCEPTED"      1 "尚未整合" "$P1X_RC" "$P1X_OUT"
"$H/devflow-exec.sh" task-state pf T-1 MECHANICAL_PASS >/dev/null 2>&1
"$H/devflow-exec.sh" task-state pf T-1 QUEUED_FOR_INTEGRATION >/dev/null 2>&1
p1x_cap task-integrate pf T-2
ck_msg "p1 無 candidate 不得整合"    1 "不得整合" "$P1X_RC" "$P1X_OUT"
"$H/devflow-exec.sh" task-state pf T-2 RUNNING >/dev/null 2>&1
# T-2 candidate 落在 side branch(模擬 task branch;尚未 cherry-pick 進本 branch)
git checkout -q -b p1side && echo impl2 > src/b.py && git add src/b.py \
  && git commit -qm p1cand2 && P1C2=$(git rev-parse HEAD) && git checkout -q -
"$H/devflow-exec.sh" task-candidate pf T-2 "$P1C2" >/dev/null 2>&1
"$H/devflow-exec.sh" task-state pf T-2 MECHANICAL_PASS >/dev/null 2>&1
"$H/devflow-exec.sh" task-state pf T-2 QUEUED_FOR_INTEGRATION >/dev/null 2>&1
p1x_cap task-integrate pf T-2
ck_msg "p1 integration DAG 順序:前置未整合拒" 1 "前置未整合" "$P1X_RC" "$P1X_OUT"
ck "p1 T-1 整合"                     0 "$(p1x task-integrate pf T-1)"
p1x_cap task-integrate pf T-2
ck_msg "p1 F1:cherry-pick 未生效不得 INTEGRATED" 1 "未在目前 branch" "$P1X_RC" "$P1X_OUT"
git cherry-pick "$P1C2" >/dev/null 2>&1
ck "p1 前置整合後 T-2 放行"          0 "$(p1x task-integrate pf T-2)"
# F2:wave review 未登記(或非 PASS)不得 ACCEPTED
"$H/devflow-exec.sh" task-state pf T-2 IN_REVIEW >/dev/null 2>&1
p1x_cap task-state pf T-2 ACCEPTED
ck_msg "p1 F2:review 未登記不得 ACCEPTED" 1 "尚未登記" "$P1X_RC" "$P1X_OUT"
cat > "$P1D/rv-ok.json" <<'EOF'
{"schema":"devflow-wave-review.v1","feature":"pf","wave":1,
 "tasks":[{"task":"T-1","verdict":"PASS","findings":[]},
          {"task":"T-2","verdict":"PASS","findings":[]}],
 "integration_verdict":"PASS","reviewed_at":"2026-08-02T12:00:00"}
EOF
cat > "$P1D/rv-bad.json" <<'EOF'
{"schema":"devflow-wave-review.v1","feature":"pf","wave":1,
 "tasks":[{"task":"T-1","verdict":"PASS","findings":[]}],
 "integration_verdict":"PASS","reviewed_at":"2026-08-02T12:00:00"}
EOF
ck "p1 wave review 合法(live wave)"  0 "$(p1x review pf --file "$P1D/rv-ok.json")"
ck "p1 F2:review 驗過即登記 verdicts" 0 "$(p1c reviews-reg "$P1T")"
p1x_cap review pf --file "$P1D/rv-bad.json"
ck_msg "p1 wave review 缺 verdict 無效" 1 "缺 T-2" "$P1X_RC" "$P1X_OUT"
"$H/devflow-exec.sh" task-state pf T-1 IN_REVIEW >/dev/null 2>&1
ck "p1 IN_REVIEW→ACCEPTED(已整合)"   0 "$(p1x task-state pf T-1 ACCEPTED)"
"$H/devflow-exec.sh" task-state pf T-2 IN_REVIEW >/dev/null 2>&1
"$H/devflow-exec.sh" task-state pf T-2 ACCEPTED >/dev/null 2>&1
ck "p1 wave-close(全 ACCEPTED)"      0 "$(p1x wave-close pf)"
"$H/devflow-exec.sh" wave-open pf >/dev/null 2>&1
"$H/devflow-exec.sh" task-state pf T-3 RUNNING >/dev/null 2>&1
echo impl3 > src/c.py && git add src/c.py && git commit -qm p1cand3 && P1C3=$(git rev-parse HEAD)
"$H/devflow-exec.sh" task-candidate pf T-3 "$P1C3" >/dev/null 2>&1
"$H/devflow-exec.sh" task-state pf T-3 MECHANICAL_PASS >/dev/null 2>&1
p1x_cap task-state pf T-3 QUEUED_FOR_INTEGRATION
ck_msg "p1 dedicated 未審不得進整合" 1 "IN_REVIEW" "$P1X_RC" "$P1X_OUT"
ck "p1 dedicated MECHANICAL_PASS→IN_REVIEW" 0 "$(p1x task-state pf T-3 IN_REVIEW)"
p1x_cap task-rework pf T-1
ck_msg "p1 ACCEPTED rework 需 owner-call" 1 "owner-call" "$P1X_RC" "$P1X_OUT"
p1x_cap task-rework pf T-1 --owner-call "upstream candidate replaced(test)"
ck_msg "p1 上游 rework → 下游 INVALIDATED_BY_UPSTREAM" 0 "INVALIDATED_BY_UPSTREAM" "$P1X_RC" "$P1X_OUT"
ck "p1 invalidation 落帳(T-3 標記+T-1 出 log)" 0 "$(p1c invalidated "$P1T")"
p1x_cap task-state pf T-3 ACCEPTED
ck_msg "p1 invalidated 不得續審/整合" 1 "INVALIDATED_BY_UPSTREAM" "$P1X_RC" "$P1X_OUT"
p1x_cap task-integrate pf T-3
ck_msg "p1 invalidated 不得 task-integrate" 1 "不得整合" "$P1X_RC" "$P1X_OUT"
p1x_cap rebuild-plan pf
ck_msg "p1 rebuild-plan 輸出重放清單" 0 "devflow-rebuild-plan.v1" "$P1X_RC" "$P1X_OUT"
ck "p1 rebuild-plan 不含被打回的 T-1" 1 "$(echo "$P1X_OUT" | grep -q '"task": "T-1"'; echo $?)"
ck "p1 invalidated 走 task-rework 重建" 0 "$(p1x task-rework pf T-3)"
p1x_cap task-state pf T-1 RUNNING
ck_msg "p1 REWORK 非本 wave 成員不得直接重跑" 1 "不在開啟中的 wave" "$P1X_RC" "$P1X_OUT"
ck "p1 wave-close 容許 REWORK 順延"  0 "$(p1x wave-close pf)"
"$H/devflow-exec.sh" wave-open pf >/dev/null 2>&1
ck "p1 新 wave 只含 ready 的 REWORK T" 0 "$(p1c wave3 "$P1T")"
# F2:wave 3 完整 rework 重跑 —— review verdict/integration_verdict 未 PASS 皆不得 ACCEPTED
"$H/devflow-exec.sh" task-state pf T-1 RUNNING >/dev/null 2>&1
echo impl1b > src/a.py && git add src/a.py && git commit -qm p1cand4 && P1C4=$(git rev-parse HEAD)
"$H/devflow-exec.sh" task-candidate pf T-1 "$P1C4" >/dev/null 2>&1
"$H/devflow-exec.sh" task-state pf T-1 MECHANICAL_PASS >/dev/null 2>&1
"$H/devflow-exec.sh" task-state pf T-1 QUEUED_FOR_INTEGRATION >/dev/null 2>&1
ck "p1 F1:rework 後真 candidate 重整合" 0 "$(p1x task-integrate pf T-1)"
"$H/devflow-exec.sh" task-state pf T-1 IN_REVIEW >/dev/null 2>&1
cat > "$P1D/rv3-wrongwave.json" <<'EOF'
{"schema":"devflow-wave-review.v1","feature":"pf","wave":1,
 "tasks":[{"task":"T-1","verdict":"PASS","findings":[]}],
 "integration_verdict":"PASS","reviewed_at":"2026-08-02T13:00:00"}
EOF
p1x_cap review pf --file "$P1D/rv3-wrongwave.json"
ck_msg "p1 F2:review wave 編號不符拒登記" 1 "不符" "$P1X_RC" "$P1X_OUT"
cat > "$P1D/rv3-fail.json" <<'EOF'
{"schema":"devflow-wave-review.v1","feature":"pf","wave":3,
 "tasks":[{"task":"T-1","verdict":"FAIL",
           "findings":[{"id":"F-1","task":"T-1","severity":"major",
                        "evidence":"S-1 原文:rework 後行為仍未符"}]}],
 "integration_verdict":"PASS","reviewed_at":"2026-08-02T13:10:00"}
EOF
"$H/devflow-exec.sh" review pf --file "$P1D/rv3-fail.json" >/dev/null 2>&1
p1x_cap task-state pf T-1 ACCEPTED
ck_msg "p1 F2:T verdict=FAIL 不得 ACCEPTED" 1 "verdict" "$P1X_RC" "$P1X_OUT"
cat > "$P1D/rv3-intfail.json" <<'EOF'
{"schema":"devflow-wave-review.v1","feature":"pf","wave":3,
 "tasks":[{"task":"T-1","verdict":"PASS","findings":[]}],
 "integration_verdict":"FAIL","reviewed_at":"2026-08-02T13:20:00"}
EOF
"$H/devflow-exec.sh" review pf --file "$P1D/rv3-intfail.json" >/dev/null 2>&1
p1x_cap task-state pf T-1 ACCEPTED
ck_msg "p1 F2:integration_verdict=FAIL 不得 ACCEPTED" 1 "integration_verdict" "$P1X_RC" "$P1X_OUT"
cat > "$P1D/rv3-ok.json" <<'EOF'
{"schema":"devflow-wave-review.v1","feature":"pf","wave":3,
 "tasks":[{"task":"T-1","verdict":"PASS","findings":[]}],
 "integration_verdict":"PASS","reviewed_at":"2026-08-02T13:30:00"}
EOF
"$H/devflow-exec.sh" review pf --file "$P1D/rv3-ok.json" >/dev/null 2>&1
ck "p1 F2:review PASS 登記後 ACCEPTED 放行" 0 "$(p1x task-state pf T-1 ACCEPTED)"

echo "-- p1 gate live(真 git candidate)--"
P1G=$(mktemp -d "${TMPDIR:-/tmp}/devflow-p1g.XXXXXX")
mkdir -p "$P1G/docs/dev/pf" "$P1G/src"
cd "$P1G" || exit 1
git init -q . && git config user.email t@t && git config user.name t
printf -- "---\nstatus: approved\n---\n" > docs/dev/pf/4-spec.md
printf '%s\n' '---' 'feature: pf' 'stage: 5-tasks' 'status: approved' 'execution:' \
  '  mode: parallel' '---' '' '## T-1 甲' '- [ ] 完成' '- Covers: R-1 / S-1' \
  '- Files: `src/a.py`' '- Verify: `true`' '- Blocked-by: —' > docs/dev/pf/5-tasks.md
echo base > src/a.py
git add -A >/dev/null && git commit -qm base
"$H/devflow-exec.sh" parallel-init pf >/dev/null 2>&1
"$H/devflow-exec.sh" wave-open pf >/dev/null 2>&1
P1BASE=$(git rev-parse HEAD)
git checkout -q -b task/pf/T-1
echo impl > src/a.py && git add src/a.py && git commit -qm candidate
P1CAND=$(git rev-parse HEAD)
git checkout -q - 2>/dev/null
mkdir -p .devflow/task/T-1
P1CH=$("$DEVFLOW_PY" -c 'import json;print(json.load(open(".devflow/parallel.json"))["contract_hash"])')
cat > .devflow/task/T-1/candidate.json <<EOF
{"schema":"devflow-candidate.v1","feature":"pf","task":"T-1","attempt":1,
 "branch":"task/pf/T-1","base_sha":"$P1BASE","candidate_sha":"$P1CAND",
 "prompt_id":"packet-pf-T-1","prompt_version":"v1","contract_hash":"$P1CH",
 "verify":{"command":"true","exit_code":0,"log":"v.log"},
 "red":{"command":"true","exit_code":1,"log":"r.log","at":"2026-08-02T10:00:00"},
 "green":{"command":"true","exit_code":0,"log":"g.log","at":"2026-08-02T10:20:00"},
 "test_names":["test_S1_ok"],"changed_files":["src/a.py"],
 "created_at":"2026-08-02T10:21:00"}
EOF
p1x_cap gate --slug pf --task T-1 --candidate-json .devflow/task/T-1/candidate.json
ck_msg "p1 gate live:真 candidate 全 PASS" 0 '"verdict": "PASS"' "$P1X_RC" "$P1X_OUT"
ck "p1 gate live:結果落 evidence 區含 checked_at" 0 "$(grep -q '"checked_at": "2' .devflow/task/T-1/gate-result.json; echo $?)"
sed -i.bak "s/$P1BASE/wrongbase0000000/" .devflow/task/T-1/candidate.json && rm -f .devflow/task/T-1/candidate.json.bak
p1x_cap gate --slug pf --task T-1 --candidate-json .devflow/task/T-1/candidate.json
ck_msg "p1 gate live:base 不符 → FAIL" 1 "base_sha_match" "$P1X_RC" "$P1X_OUT"

echo "-- p1 shadow-hash 竄改偵測(MAJOR-C:.devflow 狀態檔只准 CLI 寫)--"
cd "$P1T" || exit 1
ck "p1 shadow:re-arm(CLI 合法寫 exec.json)" 0 "$(p1x start pf --task T-1)"
ck "p1 shadow:CLI 合法寫後 postbash 綠"  0 "$(p1post)"
"$DEVFLOW_PY" - <<'PY'
import json
d = json.load(open(".devflow/exec.json"))
d["scope"] = ["src/", "docs/", "lib/"]
json.dump(d, open(".devflow/exec.json", "w"))
PY
p1post_cap
ck_msg "p1 shadow:heredoc 直改 exec.json scope → postbash 攔" 2 "exec.json" "$P1P_RC" "$P1P_OUT"
p1x_cap allow src/other.py --reason "tamper-test"
ck_msg "p1 shadow:CLI 拒建立在遭竄改 exec.json 上" 1 "竄改" "$P1X_RC" "$P1X_OUT"
ck "p1 shadow:重新 start 重建 shadow"    0 "$(p1x start pf --task T-1)"
"$DEVFLOW_PY" - <<'PY'
import json
p = json.load(open(".devflow/parallel.json"))
p["tasks"]["T-3"]["state"] = "ACCEPTED"
json.dump(p, open(".devflow/parallel.json", "w"))
PY
p1post_cap
ck_msg "p1 shadow:heredoc 偽造 parallel.json ACCEPTED → postbash 攔" 2 "parallel.json" "$P1P_RC" "$P1P_OUT"
p1x_cap task-state pf T-3 RUNNING
ck_msg "p1 shadow:CLI 拒建立在遭竄改 parallel.json 上" 1 "竄改" "$P1X_RC" "$P1X_OUT"
"$H/devflow-exec.sh" parallel-init pf --reset >/dev/null 2>&1
ck "p1 shadow:CLI 重建(--reset)後 postbash 綠" 0 "$(p1post)"
"$H/devflow-exec.sh" stop >/dev/null 2>&1

cd /tmp && rm -rf "$P1D" "$P1T" "$P1G"
echo "-- p2 stage3 觸發判定/Demo verdict 機械驗證 --"
P2=$(mktemp -d "${TMPDIR:-/tmp}/devflow-p2-stage3.XXXXXX")
p2_s3() { S3_OUT=$(cd "$P2" && "$DEVFLOW_PY" "$H/_stage3_impl.py" "$@" 2>&1); S3_RC=$?; }
p2_feature() { rm -rf "$P2/docs/dev/$1"; mkdir -p "$P2/docs/dev/$1"; }
p2_disc_rwc() { printf '%s\n' '# 1. 討論' '## Problem' 'x' '## Real-world Context' \
  '### Actors' '| Actor | 真實目標 |' '|---|---|' '| 業務 | 跟催 |' \
  > "$P2/docs/dev/$1/1-discussion.md"; }
p2_disc_plain() { printf '%s\n' '# 1. 討論' '## Problem' 'legacy feature,無 RWC 節' \
  > "$P2/docs/dev/$1/1-discussion.md"; }
p2_oc_skip() { printf '%s\n' '# 2. 收斂' '## Owner Calls(自判裁決,待人審)' \
  '- OC-9(流程層):跳過 Stage 3 — 無互動風險,人類明示。' \
  > "$P2/docs/dev/$1/2-decision.md"; }
p2_proto() { # p2_proto <slug> <checked:0|1> [User Demo Feedback 行...]
  local p2slug="$1" p2hit="$2"; shift 2
  { printf -- '---\nfeature: %s\nstage: 3-prototype\nstatus: draft\n---\n' "$p2slug"
    echo '# 3. 原型'
    echo '## Stage 3 觸發判定(條件式必要)'
    if [ "$p2hit" = 1 ]; then echo '- [x] 涉及人工核准'; else echo '- [ ] 涉及人工核准'; fi
    echo '- [ ] 涉及權限差異'
    echo '## User Demo Feedback'
    for p2line in "$@"; do echo "$p2line"; done
  } > "$P2/docs/dev/$p2slug/3-prototype.md"
}
p2_proto_old() { printf '%s\n' '# 3. 原型(舊模板)' '## Question' '舊 feature,無觸發判定節' \
  > "$P2/docs/dev/$1/3-prototype.md"; }
mkdir -p "$P2/docs/dev"
p2_s3 no-such-slug
ck_msg "p2:slug 目錄不存在 → 錯誤" 1 "找不到" "$S3_RC" "$S3_OUT"
p2_feature l1; p2_disc_plain l1
p2_s3 l1
ck_msg "p2:legacy 無 RWC 無 3-prototype → 放行" 0 "legacy" "$S3_RC" "$S3_OUT"
p2_feature f0
p2_s3 f0
ck_msg "p2:fast lane 無 1/3 檔 → N/A 放行" 0 "N/A" "$S3_RC" "$S3_OUT"
p2_feature v1; p2_disc_rwc v1
p2_s3 v1
ck_msg "p2:有 RWC 無 3-prototype 無 Owner Call → 拒" 2 "未記錄" "$S3_RC" "$S3_OUT"
p2_oc_skip v1
p2_s3 v1
ck_msg "p2:有 RWC 無 3-prototype + Owner Call 跳過 → 放行" 0 "Owner Call" "$S3_RC" "$S3_OUT"
p2_feature v2; p2_disc_rwc v2; p2_proto v2 0
p2_s3 v2
ck_msg "p2:觸發判定全未勾 → N/A 放行" 0 "N/A" "$S3_RC" "$S3_OUT"
p2_proto v2 1 '- Human verdict: ACCEPTED | REVISE | NOT_REVIEWED'
p2_s3 v2
ck_msg "p2:命中 + verdict 佔位未填 → 拒" 2 "NOT_REVIEWED" "$S3_RC" "$S3_OUT"
p2_proto v2 1 '- Human verdict: REVISE'
p2_s3 v2
ck_msg "p2:命中 + REVISE → 拒" 2 "REVISE" "$S3_RC" "$S3_OUT"
p2_oc_skip v2
p2_s3 v2
ck_msg "p2:REVISE 不得以 Owner Call 繞過" 2 "REVISE" "$S3_RC" "$S3_OUT"
p2_proto v2 1 '- Human verdict: NOT_REVIEWED'
p2_s3 v2
ck_msg "p2:NOT_REVIEWED + Owner Call 跳過 → 放行" 0 "Owner Call" "$S3_RC" "$S3_OUT"
p2_feature v3; p2_disc_rwc v3
p2_proto v3 1 '- Human verdict: ACCEPTED'
p2_s3 v3
ck_msg "p2:Agent 自填 ACCEPTED 無 attestation → 拒" 2 "attestation" "$S3_RC" "$S3_OUT"
p2_proto v3 1 '- Human verdict: ACCEPTED' '- Verdict attestation: human:rick @ 2026-08-02'
p2_s3 v3
ck_msg "p2:ACCEPTED + 人類 attestation → 放行" 0 "ACCEPTED" "$S3_RC" "$S3_OUT"
ck_msg "p2:輸出含結構化 g2_demo 欄" 0 "\"g2_demo\": \"PASS\"" "$S3_RC" "$S3_OUT"
p2_proto v3 1 '- Human verdict: ACCEPTED' '- Verdict attestation: test-only human fixture @ 2026-08-02'
p2_s3 v3
ck_msg "p2:test-only fixture 正式模式 → 拒" 2 "test-only" "$S3_RC" "$S3_OUT"
p2_s3 v3 --accept-test-fixture
ck_msg "p2:test-only fixture + flag(僅測試)→ 放行" 0 "ACCEPTED" "$S3_RC" "$S3_OUT"
p2_proto v3 1 '- Human verdict: ACCEPTED(第 2 輪;第 1 輪 REVISE)' '- Verdict attestation: human:rick @ 2026-08-02'
p2_s3 v3
ck_msg "p2:ACCEPTED 帶尾註仍可解析 → 放行" 0 "ACCEPTED" "$S3_RC" "$S3_OUT"
p2_feature v4; p2_disc_rwc v4; p2_proto_old v4
p2_s3 v4
ck_msg "p2:VNext 檔配舊 3-prototype 缺判定節 → 拒" 2 "觸發判定" "$S3_RC" "$S3_OUT"
p2_feature l2; p2_disc_plain l2; p2_proto_old l2
p2_s3 l2
ck_msg "p2:legacy 舊 3-prototype 無判定節 → 放行" 0 "legacy" "$S3_RC" "$S3_OUT"
rm -rf "$P2"
echo "-- p3 observability runtime(event/derive/stats/retention/doctor/registry)--"
P3T=$(mktemp -d "${TMPDIR:-/tmp}/devflow-p3-selftest.XXXXXX")
P3RUN="run_01JG8C4V2M0000000000000P30"
P3ATT="att_01JG8C4V2M0000000000000P31"
P3LONG=$(printf 'a%.0s' $(seq 1 101))
P3HASH=$(printf '1%.0s' $(seq 1 64))
p3_ev() { P3_OUT=$(printf '%s\n' "$1" | (cd "$P3T" && "$H/devflow-obs.sh" event) 2>&1); P3_RC=$?; }
p3_hookev() { P3_OUT=$(printf '%s\n' "$1" | (cd "$P3T" && "$H/devflow-obs.sh" hook-event) 2>&1); P3_RC=$?; }
p3_obs() { P3_OUT=$( (cd "$P3T" && "$H/devflow-obs.sh" "$@") 2>&1 ); P3_RC=$?; }
p3_lh() { P3_OUT=$( (cd "$P3T" && env "$@" "$H/devflow-obs.sh" ledger-home) 2>&1 ); P3_RC=$?; }
p3_ret() { P3_OUT=$( (cd "$P3T" && DEVFLOW_LEDGER_HOME="$P3T/ledger" "$H/devflow-obs.sh" "$@") 2>&1 ); P3_RC=$?; }
p3_doctor() { P3_OUT=$( (cd "$P3T" && DEVFLOW_CONTRACT="$1" DEVFLOW_RUNTIME_CAPS="$2" DEVFLOW_GATE_CMD="${3:-true}" "$H/devflow-doctor.sh") 2>&1 ); P3_RC=$?; }
p3_json_has() { # p3_json_has <file> <manifest|registry5|caps>
  "$DEVFLOW_PY" - "$1" "$2" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(1)
mode = sys.argv[2]
if mode == "manifest":
    need = ["repo_id", "run_id", "schema_version", "created_at", "expires_at", "source_sha"]
    sys.exit(0 if all(data.get(k) for k in need) else 1)
if mode == "registry5":
    need = {"stage6-worker", "stage6-reviewer", "stage6-adviser",
            "stage7-standards-reviewer", "stage7-spec-reviewer"}
    sys.exit(0 if need <= set(data.get("prompts", {})) else 1)
if mode == "caps":
    sys.exit(0 if ("2.0.0" in data.get("supported_contract_versions", [])
                   and data.get("runtime_version")
                   and "attempt_ledger" in data.get("capabilities", [])) else 1)
sys.exit(1)
PY
}
p3_expire() { # 把歸檔 manifest 的 expires_at 改成過去(retention 測試用)
  "$DEVFLOW_PY" - "$1" <<'PY'
import json, sys
path = sys.argv[1]
with open(path) as f:
    m = json.load(f)
m["expires_at"] = "2000-01-01T00:00:00+00:00"
with open(path, "w") as f:
    json.dump(m, f, ensure_ascii=False, indent=1, sort_keys=True)
PY
}
( cd "$P3T" && git init -q . && git config user.email t@t && git config user.name t \
  && echo x > x.txt && git add -A && git commit -qm init )
# 最小契約 fixture(1.1):task_tags 受控 enum 正本 = devflow-contract.json;
# plugin 環境解析鏈第 2 站 = 受測專案 docs/dev/ 散發副本(dev-setup 產物位置)
mkdir -p "$P3T/docs/dev"
printf '{"task_tags": ["api", "ui", "database", "integration", "infrastructure", "test", "documentation", "security", "authorization", "migration", "workflow", "other"]}\n' > "$P3T/docs/dev/devflow-contract.json"

p3_ev '{"event_type":"run_started","writer":"coordinator","feature_slug":"f1","base_sha":"abc1234"}'
ck_msg "p3 event 未武裝 → 明確錯誤" 1 "run_id" "$P3_RC" "$P3_OUT"
mkdir -p "$P3T/.devflow"
printf '{"slug":"f1","scope":[],"extra":[]}\n' > "$P3T/.devflow/exec.json"
p3_ev '{"event_type":"run_started","writer":"coordinator","feature_slug":"f1","base_sha":"abc1234"}'
ck_msg "p3 event v1 旗標無 run_id → 明確錯誤" 1 "exec-v2" "$P3_RC" "$P3_OUT"
printf '{"schema":"exec-v3","slug":"f1","run_id":"%s","scope":[],"extra":[]}\n' "$P3RUN" > "$P3T/.devflow/exec.json"
p3_ev '{"event_type":"run_started","writer":"coordinator","feature_slug":"f1","base_sha":"abc1234"}'
ck_msg "p3 event v3 落盤成功" 0 "run_started" "$P3_RC" "$P3_OUT"
ck "p3 coordinator events.jsonl 落盤" 0 "$(test -s "$P3T/.devflow/runs/$P3RUN/coordinator/events.jsonl"; echo $?)"
ck "p3 run manifest 含 OC-5 六必填" 0 "$(p3_json_has "$P3T/.devflow/runs/$P3RUN/manifest.json" manifest; echo $?)"
p3_ev '{"event_type":"nonsense_event","writer":"coordinator"}'
ck_msg "p3 未知 event_type → 拒收" 1 "unknown_event_type" "$P3_RC" "$P3_OUT"
p3_ev "{\"event_type\":\"attempt_started\",\"writer\":\"coordinator\",\"task_id\":\"T-1\",\"attempt_id\":\"$P3ATT\",\"agent_role\":\"worker\",\"model\":\"$P3LONG\",\"prompt\":{\"id\":\"stage6-worker\",\"version\":\"1.0.0\",\"hash\":\"sha256:$P3HASH\"},\"base_sha\":\"abc1234\"}"
ck_msg "p3 runtime 加嚴:model>100 → 拒收" 1 "field_too_long" "$P3_RC" "$P3_OUT"
p3_ev '{"event_type":"run_completed","writer":"coordinator","result":"PASS","x_meta":{"customer_data":"x"}}'
ck_msg "p3 runtime 加嚴:customer_data → 拒收" 1 "privacy_forbidden_key" "$P3_RC" "$P3_OUT"
# 1.1:task_tags 為正式欄(agent_dispatched/attempt_* optional),enum 解析自契約
p3_ev "{\"event_type\":\"agent_dispatched\",\"writer\":\"coordinator\",\"task_id\":\"T-1\",\"attempt_id\":\"$P3ATT\",\"agent_role\":\"worker\",\"model\":\"haiku\",\"prompt\":{\"id\":\"stage6-worker\",\"version\":\"1.0.0\",\"hash\":\"sha256:$P3HASH\"},\"task_tags\":[\"frontend-magic\"]}"
ck_msg "p3 task_tags 自由字串 → 拒收" 1 "受控" "$P3_RC" "$P3_OUT"
p3_ev "{\"event_type\":\"agent_dispatched\",\"writer\":\"coordinator\",\"task_id\":\"T-1\",\"attempt_id\":\"$P3ATT\",\"agent_role\":\"worker\",\"model\":\"haiku\",\"prompt\":{\"id\":\"stage6-worker\",\"version\":\"1.0.0\",\"hash\":\"sha256:$P3HASH\"},\"task_tags\":[\"api\",\"authorization\"]}"
ck "p3 task_tags 受控 enum → 放行" 0 "$P3_RC"
p3_ev "{\"event_type\":\"attempt_started\",\"writer\":\"coordinator\",\"task_id\":\"T-1\",\"attempt_id\":\"$P3ATT\",\"agent_role\":\"worker\",\"model\":\"haiku\",\"prompt\":{\"id\":\"stage6-worker\",\"version\":\"1.0.0\",\"hash\":\"sha256:$P3HASH\"},\"base_sha\":\"abc1234\"}"
ck "p3 attempt_started 落盤" 0 "$P3_RC"
p3_ev "{\"event_type\":\"attempt_completed\",\"writer\":\"coordinator\",\"task_id\":\"T-1\",\"attempt_id\":\"$P3ATT\",\"result\":\"FAIL\"}"
ck_msg "p3 FAIL 無 failure_category → 拒收" 1 "missing_field" "$P3_RC" "$P3_OUT"
p3_ev "{\"event_type\":\"attempt_completed\",\"writer\":\"coordinator\",\"task_id\":\"T-1\",\"attempt_id\":\"$P3ATT\",\"result\":\"FAIL\",\"failure_category\":\"IMPL\"}"
ck "p3 attempt_completed 落盤" 0 "$P3_RC"
ck "p3 attempt result.json finalize" 0 "$(test -s "$P3T/.devflow/runs/$P3RUN/attempts/$P3ATT/result.json"; echo $?)"
p3_hookev '{"event_type":"mechanical_gate_completed","gate":"prebash","result":"FAIL","violation":"guard_state","session_ref":"sessP3","model":"haiku"}'
ck_msg "p3 hook 事件帶 model → 拒收" 1 "hook_forbidden_field" "$P3_RC" "$P3_OUT"
p3_hookev '{"event_type":"mechanical_gate_completed","gate":"prebash","result":"FAIL","violation":"guard_state","session_ref":"sessP3"}'
ck "p3 hook 機械事件落盤" 0 "$P3_RC"
ck "p3 hooks/events-<session>.jsonl 存在" 0 "$(test -s "$P3T/.devflow/runs/$P3RUN/hooks/events-sessP3.jsonl"; echo $?)"
# MINOR-3:RUNS_ROOT 不得把事件檔導進受測 repo 內 .devflow/ 之外(走私);repo 外照常允許
P3_OUT=$(printf '%s\n' '{"event_type":"stage_started","writer":"coordinator","stage":"6-implementation"}' | (cd "$P3T" && DEVFLOW_RUNS_ROOT="$P3T/smuggle" "$H/devflow-obs.sh" event) 2>&1); P3_RC=$?
ck_msg "p3 RUNS_ROOT 指向 repo 內非 .devflow → 拒" 1 "走私" "$P3_RC" "$P3_OUT"
P3EXT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-p3-ext.XXXXXX")
P3_OUT=$(printf '%s\n' '{"event_type":"stage_started","writer":"coordinator","stage":"6-implementation"}' | (cd "$P3T" && DEVFLOW_RUNS_ROOT="$P3EXT" "$H/devflow-obs.sh" event) 2>&1); P3_RC=$?
ck "p3 RUNS_ROOT repo 外照常允許(測試用途)" 0 "$P3_RC"
rm -rf "$P3EXT"
p3_obs validate
ck_msg "p3 validate 全綠" 0 "$P3RUN" "$P3_RC" "$P3_OUT"
p3_obs derive
D1=$(shasum -a 256 "$P3T/.devflow/runs/$P3RUN/derived/run-events.jsonl" 2>/dev/null | cut -d' ' -f1)
p3_obs derive
D2=$(shasum -a 256 "$P3T/.devflow/runs/$P3RUN/derived/run-events.jsonl" 2>/dev/null | cut -d' ' -f1)
ck "p3 derive 重建 byte 決定性" 0 "$([ -n "$D1" ] && [ "$D1" = "$D2" ]; echo $?)"
p3_obs stats
ck_msg "p3 stats 輸出指標" 0 "first_pass_success_rate" "$P3_RC" "$P3_OUT"
p3_obs recommend
ck_msg "p3 recommend 只建議不改檔" 0 "recommendations" "$P3_RC" "$P3_OUT"
p3_lh DEVFLOW_LEDGER_HOME="$P3T/ledger"
ck_msg "p3 ledger-home env 覆寫" 0 "$P3T/ledger" "$P3_RC" "$P3_OUT"
p3_lh DEVFLOW_LEDGER_OS=darwin
ck_msg "p3 ledger-home macOS 預設" 0 "Library/Application Support/DevFlow/ledger" "$P3_RC" "$P3_OUT"
p3_lh DEVFLOW_LEDGER_OS=linux XDG_STATE_HOME="$P3T/xdg"
ck_msg "p3 ledger-home Linux XDG 預設" 0 "$P3T/xdg/devflow/ledger" "$P3_RC" "$P3_OUT"
p3_ret archive "$P3RUN"
ck "p3 archive 歸檔成功" 0 "$P3_RC"
P3REPO=$(ls "$P3T/ledger/runs" 2>/dev/null | head -1)
ck "p3 歸檔 manifest 含 OC-5 六必填" 0 "$(p3_json_has "$P3T/ledger/runs/$P3REPO/$P3RUN/manifest.json" manifest; echo $?)"
p3_ret retention status
ck_msg "p3 retention status" 0 "runs_total" "$P3_RC" "$P3_OUT"
p3_ret retention prune --dry-run
ck_msg "p3 prune dry-run 無過期" 0 "\"would_remove\": []" "$P3_RC" "$P3_OUT"
p3_expire "$P3T/ledger/runs/$P3REPO/$P3RUN/manifest.json"
p3_ret retention prune --dry-run
ck_msg "p3 prune dry-run 列出過期" 0 "$P3RUN" "$P3_RC" "$P3_OUT"
ck "p3 dry-run 不刪檔" 0 "$(test -d "$P3T/ledger/runs/$P3REPO/$P3RUN"; echo $?)"
p3_ret retention prune
ck "p3 prune 刪除過期 run" 0 "$P3_RC"
ck "p3 prune 後 run 已移除" 1 "$(test -d "$P3T/ledger/runs/$P3REPO/$P3RUN"; echo $?)"
printf '%s\n' '{"devflow_contract_version": "2.0.0",' \
  ' "required_runtime_capabilities": ["attempt_ledger"],' \
  ' "schema_versions": {"agent_event": "1.1", "context_manifest": "1.0", "prompt_registry": "1.0", "exec_state": "exec-v3"}}' > "$P3T/contract-ok.json"
printf '%s\n' '{"supported_contract_versions": ["2.0.0"], "runtime_version": "2.5.0", "capabilities": ["attempt_ledger"]}' > "$P3T/caps-ok.json"
printf '%s\n' '{"supported_contract_versions": ["1.2.0"], "runtime_version": "1.9.0", "capabilities": ["attempt_ledger"]}' > "$P3T/caps-old.json"
printf '%s\n' '{"devflow_contract_version": "2.0.0",' \
  ' "required_runtime_capabilities": ["attempt_ledger", "parallel_wave_execution"],' \
  ' "schema_versions": {"agent_event": "1.1"}}' > "$P3T/contract-more.json"
# contract-schema9 = 刻意不相容反例(9.9 vs runtime 1.1),驗 doctor fail-closed;勿隨版本升級改綠
printf '%s\n' '{"devflow_contract_version": "2.0.0",' \
  ' "required_runtime_capabilities": ["attempt_ledger"],' \
  ' "schema_versions": {"agent_event": "9.9"}}' > "$P3T/contract-schema9.json"
p3_doctor "$P3T/contract-ok.json" "$P3T/caps-ok.json"
ck_msg "p3 doctor 相容 → COMPATIBLE" 0 "COMPATIBLE" "$P3_RC" "$P3_OUT"
p3_doctor "$P3T/contract-ok.json" "$P3T/caps-old.json"
ck_msg "p3 doctor 版本不符 → fail-closed 例句" 1 "Methodology requires contract 2.0.0" "$P3_RC" "$P3_OUT"
ck_msg "p3 doctor 版本不符 → 標明 parallel 不可用" 1 "Parallel execution is unavailable" "$P3_RC" "$P3_OUT"
p3_doctor "$P3T/contract-more.json" "$P3T/caps-ok.json"
ck_msg "p3 doctor 缺 capability → 列名" 1 "parallel_wave_execution" "$P3_RC" "$P3_OUT"
p3_doctor "$P3T/contract-schema9.json" "$P3T/caps-ok.json"
ck_msg "p3 doctor schema 版本漂移 → fail" 1 "agent_event" "$P3_RC" "$P3_OUT"
p3_doctor "$P3T/nope.json" "$P3T/caps-ok.json"
ck_msg "p3 doctor 契約找不到 → 明確報" 1 "docs/dev" "$P3_RC" "$P3_OUT"
p3_doctor "$P3T/contract-ok.json" "$P3T/caps-ok.json" false
ck_msg "p3 doctor gate-consistency 紅 → fail" 1 "gate" "$P3_RC" "$P3_OUT"
printf '{"slug":"f1","scope":[],"extra":[]}\n' > "$P3T/.devflow/exec.json"
p3_doctor "$P3T/contract-ok.json" "$P3T/caps-ok.json"
ck_msg "p3 doctor v1 旗標 → legacy compatibility mode 明示" 0 "legacy compatibility mode" "$P3_RC" "$P3_OUT"
# M3:gauntlet version(散發副本 --version 實跑)+ wave_review schema(caps 聲明)
mkdir -p "$P3T/docs/dev/tools"
p3_fake_gauntlet() { # p3_fake_gauntlet <version|none> [rootmode]
  # rootmode(B-4,預設 ok):ok=印對的 root($P3T/docs/dev)、bad=印錯的 root、
  # noroot=支援 --version 但不支援 --print-root(舊版散發副本,只加了 --version)。
  local ver="$1" rootmode="${2:-ok}"
  if [ "$ver" = "none" ]; then
    printf '%s\n' '#!/bin/bash' 'echo "usage error: unknown flag" >&2' 'exit 64' \
      > "$P3T/docs/dev/tools/devflow-evidence-gauntlet.sh"
    return
  fi
  {
    echo '#!/bin/bash'
    echo "if [ \"\${1:-}\" = \"--version\" ]; then echo \"devflow-evidence-gauntlet $ver\"; exit 0; fi"
    case "$rootmode" in
      ok)     echo "if [ \"\${1:-}\" = \"--print-root\" ]; then echo \"$P3T/docs/dev\"; exit 0; fi" ;;
      bad)    echo "if [ \"\${1:-}\" = \"--print-root\" ]; then echo \"$P3T/wrong-root\"; exit 0; fi" ;;
      noroot) : ;;
    esac
    echo 'exit 64'
  } > "$P3T/docs/dev/tools/devflow-evidence-gauntlet.sh"
}
printf '%s\n' '{"devflow_contract_version": "2.0.0",' \
  ' "required_runtime_capabilities": ["attempt_ledger"],' \
  ' "schema_versions": {"agent_event": "1.1", "gauntlet": "1.1.0", "wave_review": "devflow-wave-review.v1"}}' > "$P3T/contract-g.json"
printf '%s\n' '{"supported_contract_versions": ["2.0.0"], "runtime_version": "2.5.0", "capabilities": ["attempt_ledger"],' \
  ' "schema_versions": {"agent_event": "1.1", "wave_review": "devflow-wave-review.v1"}}' > "$P3T/caps-wv.json"
p3_fake_gauntlet 1.1.0
p3_doctor "$P3T/contract-g.json" "$P3T/caps-wv.json"
ck_msg "p3 doctor gauntlet 版本一致 → ✓" 0 "✓ gauntlet" "$P3_RC" "$P3_OUT"
ck_msg "p3 doctor wave_review 聲明一致 → ✓" 0 "✓ wave_review" "$P3_RC" "$P3_OUT"
p3_fake_gauntlet 0.9.0
p3_doctor "$P3T/contract-g.json" "$P3T/caps-wv.json"
ck_msg "p3 doctor gauntlet 版本不符 → fail 指 dev-setup" 1 "dev-setup" "$P3_RC" "$P3_OUT"
p3_fake_gauntlet none
p3_doctor "$P3T/contract-g.json" "$P3T/caps-wv.json"
ck_msg "p3 doctor gauntlet 舊版無 --version → fail" 1 "dev-setup" "$P3_RC" "$P3_OUT"
rm -f "$P3T/docs/dev/tools/devflow-evidence-gauntlet.sh"
p3_doctor "$P3T/contract-g.json" "$P3T/caps-wv.json"
ck_msg "p3 doctor gauntlet 散發副本缺 → fail" 1 "散發副本缺" "$P3_RC" "$P3_OUT"
p3_fake_gauntlet 1.1.0
p3_doctor "$P3T/contract-g.json" "$P3T/caps-ok.json"
ck_msg "p3 doctor wave_review 未聲明 → fail" 1 "✗ wave_review" "$P3_RC" "$P3_OUT"
# B-4:doctor 對 gauntlet 只探 --version 驗不到散發副本因目錄深度不同(scripts/
# 對 docs/dev/tools/)造成的 ROOT 解析差異 —— 補 --print-root 探測。
p3_fake_gauntlet 1.1.0 ok
p3_doctor "$P3T/contract-g.json" "$P3T/caps-wv.json"
ck_msg "p3 doctor gauntlet-root 落在受測專案 docs/dev → ✓" 0 "✓ gauntlet-root" "$P3_RC" "$P3_OUT"
p3_fake_gauntlet 1.1.0 bad
p3_doctor "$P3T/contract-g.json" "$P3T/caps-wv.json"
ck_msg "p3 doctor gauntlet-root 落點錯(ROOT 解析跑掉)→ fail" 1 "gauntlet-root" "$P3_RC" "$P3_OUT"
p3_fake_gauntlet 1.1.0 noroot
p3_doctor "$P3T/contract-g.json" "$P3T/caps-wv.json"
ck_msg "p3 doctor 散發副本不支援 --print-root(舊版)→ fail" 1 "gauntlet-root" "$P3_RC" "$P3_OUT"
p3_fake_gauntlet 1.1.0
# nit-1:契約 schema_versions 出現 doctor 不認識的 key → 至少 info 一行,不擋
printf '%s\n' '{"devflow_contract_version": "2.0.0",' \
  ' "required_runtime_capabilities": ["attempt_ledger"],' \
  ' "schema_versions": {"agent_event": "1.1", "future_thing": "9.0"}}' > "$P3T/contract-unk.json"
p3_doctor "$P3T/contract-unk.json" "$P3T/caps-ok.json"
ck_msg "p3 doctor 未知 schema key → info 不擋" 0 "future_thing" "$P3_RC" "$P3_OUT"
p3_obs registry validate
ck "p3 prompt registry schema 綠" 0 "$P3_RC"
ck "p3 registry 五 prompt id 齊" 0 "$(p3_json_has "$H/prompt-registry.json" registry5; echo $?)"
ck "p3 runtime-capabilities 契約聲明" 0 "$(p3_json_has "$H/runtime-capabilities.json" caps; echo $?)"
ck "p3 vendor 無 __pycache__ 生成" 0 "$([ -z "$(find "$H/devflow_obs_vendor" -name '__pycache__' -print -quit 2>/dev/null)" ]; echo $?)"
# MINOR-1:vendor byte-identical 宣稱機械強制(母版在才可驗;不在 → 明確 SKIP,不靜默)
p3_vendor_cmp() { # 0=全檔一致或母版缺(SKIP 已明示);1=漂移
  local master="${DEVFLOW_MASTER:-$(dirname "$H")}/observability" f
  if [ ! -d "$master" ]; then
    echo "  ⚠ SKIP:方法論母版不存在($master)—— vendor 一致性僅本機可驗,他機安裝不算 FAIL"
    return 0
  fi
  for f in __init__ ids event_validate writer ledger stats legacy_md; do
    cmp -s "$H/devflow_obs_vendor/devflow_obs/$f.py" "$master/devflow_obs/$f.py" \
      || { echo "  vendor 漂移:devflow_obs/$f.py ≠ 母版"; return 1; }
  done
  for f in agent-event context-manifest prompt-registry; do
    cmp -s "$H/devflow_obs_vendor/schema/$f.schema.json" "$master/schema/$f.schema.json" \
      || { echo "  vendor 漂移:schema/$f.schema.json ≠ 母版"; return 1; }
  done
  return 0
}
p3_vendor_sha() { # VENDOR-SOURCE.md sha256 表 vs 實檔(自足,母版不需在)
  local f want have
  for f in agent-event context-manifest prompt-registry; do
    want=$(grep "schema/$f.schema.json" "$H/devflow_obs_vendor/VENDOR-SOURCE.md" | grep -o '[0-9a-f]\{64\}')
    have=$(shasum -a 256 "$H/devflow_obs_vendor/schema/$f.schema.json" | cut -d' ' -f1)
    [ -n "$want" ] && [ "$want" = "$have" ] || { echo "  VENDOR-SOURCE sha256 表過期:$f"; return 1; }
  done
  return 0
}
p3_vendor_cmp; P3_RC=$?
ck "p3 vendor byte-identical vs 母版(缺母版=明示 SKIP)" 0 "$P3_RC"
p3_vendor_sha; P3_RC=$?
ck "p3 VENDOR-SOURCE sha256 表與實檔一致" 0 "$P3_RC"
rm -rf "$P3T"

echo "-- pw integrator wiring(event/doctor/stage3 分派 + 守衛觀測插樁 fail-open)--"
# pw_*:Phase 3 Integrator 接線案(只增不改;四軌 manifest「交 Integrator」patch 驗證)
PWT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-pw-wiring.XXXXXX")
pw_g() { # pw_g <tool> <relpath> [env NAME=VAL ...]
  local pwtool="$1" pwrel="$2"; shift 2
  PW_OUT=$(cd "$PWT" && echo "{\"tool_name\":\"$pwtool\",\"tool_input\":{\"file_path\":\"$PWT/$pwrel\"}}" \
    | env "$@" "$H/devflow-guard.sh" 2>&1); PW_RC=$?
}
mkdir -p "$PWT/docs/dev/pw" "$PWT/src"
( cd "$PWT" && git init -q . && git config user.email t@t && git config user.name t )
printf -- "---\nstatus: approved\n---\n" > "$PWT/docs/dev/pw/4-spec.md"
cat > "$PWT/docs/dev/pw/5-tasks.md" <<'EOF'
---
feature: pw
stage: 5-tasks
status: approved
execution:
  mode: parallel
---

# 5. 任務(pw wiring fixture)

## T-1 甲
- [ ] 完成
- Covers: R-1 / S-1
- Files: `src/a.py`
- Verify: `true`
- Blocked-by: —

## T-2 乙
- [ ] 完成
- Covers: R-1 / S-2
- Files: `src/b.py`
- Verify: `true`
- Blocked-by: —
EOF
echo a > "$PWT/src/a.py"; echo b > "$PWT/src/b.py"
( cd "$PWT" && git add -A >/dev/null && git commit -qm pwinit )

PW_OUT=$(cd "$PWT" && echo 'not-json' | "$H/devflow-exec.sh" event 2>&1); PW_RC=$?
ck_msg "pw event 分派可達:壞 JSON → 非 0" 1 "JSON" "$PW_RC" "$PW_OUT"
PWCON=$(mktemp "${TMPDIR:-/tmp}/devflow-pw-contract.XXXXXX")   # 放 repo 外,免污染工作樹
printf '%s\n' '{"devflow_contract_version": "2.0.0",' \
  ' "required_runtime_capabilities": ["task_scoped_guard", "parallel_wave_execution", "candidate_gate", "attempt_ledger", "final_fresh_run", "operational_demo_gate"],' \
  ' "schema_versions": {"agent_event": "1.1", "context_manifest": "1.0", "prompt_registry": "1.0", "exec_state": "exec-v3"}}' > "$PWCON"
PW_OUT=$( (cd "$PWT" && DEVFLOW_CONTRACT="$PWCON" DEVFLOW_GATE_CMD=true "$H/devflow-exec.sh" doctor) 2>&1 ); PW_RC=$?
ck_msg "pw doctor 分派可達(devflow-exec.sh doctor)" 0 "devflow doctor" "$PW_RC" "$PW_OUT"
ck_msg "pw doctor 六 capability 全數聲明" 0 "全數聲明" "$PW_RC" "$PW_OUT"
PW_OUT=$( (cd "$PWT" && "$H/devflow-exec.sh" stage3 no-such-slug) 2>&1 ); PW_RC=$?
ck_msg "pw stage3 分派可達(feature 不存在 → 錯誤)" 1 "找不到" "$PW_RC" "$PW_OUT"

( cd "$PWT" && "$H/devflow-exec.sh" start pw --task T-1 >/dev/null 2>&1 )
PWRUN=$("$DEVFLOW_PY" -c "import json;print(json.load(open('$PWT/.devflow/exec.json'))['run_id'])" 2>/dev/null)
pw_g Write src/b.py
ck_msg "pw guard deny 行為不變(scope 外仍擋)" 2 "scope 外寫入" "$PW_RC" "$PW_OUT"
ck "pw guard deny 落 hook 事件一筆" 0 "$(grep -q mechanical_gate_completed "$PWT/.devflow/runs/$PWRUN/hooks/events-"*.jsonl 2>/dev/null; echo $?)"
pw_g Write src/b.py DEVFLOW_RUNS_ROOT="$PWCON/x"   # runs root 指向檔案下層 = 不可建目錄
ck_msg "pw 觀測不可寫:deny 判定不變(fail-open)" 2 "scope 外寫入" "$PW_RC" "$PW_OUT"
pw_g Write src/a.py DEVFLOW_RUNS_ROOT="$PWCON/x"
ck "pw 觀測不可寫:放行照樣放行(不誤擋)" 0 "$PW_RC"
rm -rf "$PWT" "$PWCON"

echo "-- p4_ dev-setup 契約散發站(doctor 於專案 docs/dev/ 找 devflow-contract.json)--"
# dev-setup install 步 1 散發 docs/dev/devflow-contract.json;doctor 無明示指定時在
# 該站解析(_doctor_impl._find_contract)。此處驗散發位置真的被吃到、缺件真的指路。
P4DT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-p4-contract.XXXXXX")
( cd "$P4DT" && git init -q . && git config user.email t@t && git config user.name t )
mkdir -p "$P4DT/docs/dev"
printf '%s\n' '{"devflow_contract_version": "2.0.0",' \
  ' "required_runtime_capabilities": ["attempt_ledger"],' \
  ' "schema_versions": {"agent_event": "1.1", "context_manifest": "1.0", "prompt_registry": "1.0", "exec_state": "exec-v3"}}' > "$P4DT/docs/dev/devflow-contract.json"
P4_OUT=$( (cd "$P4DT" && DEVFLOW_GATE_CMD=true "$H/devflow-exec.sh" doctor) 2>&1 ); P4_RC=$?
ck_msg "p4_doctor 無明示指定 → 用 docs/dev 散發副本" 0 "docs/dev/devflow-contract.json" "$P4_RC" "$P4_OUT"
rm -f "$P4DT/docs/dev/devflow-contract.json"
P4_OUT=$( (cd "$P4DT" && DEVFLOW_GATE_CMD=true "$H/devflow-exec.sh" doctor) 2>&1 ); P4_RC=$?
ck_msg "p4_doctor 散發副本缺件 → fail-closed 指路 dev-setup" 1 "dev-setup" "$P4_RC" "$P4_OUT"
rm -rf "$P4DT"

echo "-- px 派工分層守衛(X-5b:PreToolUse Task|Agent「首派即最高階」窄版攔截 + 一次性豁免)--"
PXT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-px-dispatch.XXXXXX")
px_d() { # px_d <model>
  PX_OUT=$(cd "$PXT" && echo "{\"tool_name\":\"Task\",\"tool_input\":{\"model\":\"$1\"}}" \
    | "$H/devflow-dispatch-guard.sh" 2>&1); PX_RC=$?
}
mkdir -p "$PXT/docs/dev/px" "$PXT/src"
( cd "$PXT" && git init -q . && git config user.email t@t && git config user.name t )
printf -- "---\nstatus: approved\n---\n" > "$PXT/docs/dev/px/4-spec.md"
cat > "$PXT/docs/dev/px/5-tasks.md" <<'EOF'
---
feature: px
stage: 5-tasks
status: approved
execution:
  mode: parallel
---

# 5. 任務(px dispatch-guard fixture)

## T-1 甲
- [ ] 完成
- Covers: R-1
- Files: `src/a.py`
- Verify: `true`
- Blocked-by: —
EOF
echo a > "$PXT/src/a.py"
( cd "$PXT" && git add -A >/dev/null && git commit -qm pxinit )

# ① 未武裝(.devflow/exec.json 不存在)+ model=opus → 一律放行(舊 state 行為不變)
px_d opus
ck "px 未武裝 + model=opus → 放行" 0 "$PX_RC"

( cd "$PXT" && "$H/devflow-exec.sh" start px --task T-1 >/dev/null 2>&1 )
PXRUN=$("$DEVFLOW_PY" -c "import json;print(json.load(open('$PXT/.devflow/exec.json'))['run_id'])" 2>/dev/null)

# ② 武裝 + 首派 model=opus,本 run 尚無任何低階 attempt → 擋(exit 2),訊息點名 tier-exempt 逃生門
px_d opus
ck_msg "px 武裝+首派 opus(無低階 attempt)→ exit 2 且訊息含 tier-exempt" 2 "tier-exempt" "$PX_RC" "$PX_OUT"

# ③ 補一筆低階(haiku)attempt_started → 首派 opus 屬合法升階路徑,放行
mkdir -p "$PXT/.devflow/runs/$PXRUN/attempts/att-px1"
printf '%s\n' '{"event_type":"attempt_started","model":"haiku"}' \
  > "$PXT/.devflow/runs/$PXRUN/attempts/att-px1/events.jsonl"
px_d opus
ck "px 已有 haiku attempt → 首派 opus 視為合法升階,放行" 0 "$PX_RC"
rm -rf "$PXT/.devflow/runs/$PXRUN/attempts/att-px1"   # 清掉,回到「無低階 attempt」情境測豁免通道

# ④ 豁免卡未用 + model=fable → 放行且卡片轉 used:true(留痕斷言,非只信訊息文字)
( cd "$PXT" && "$H/devflow-exec.sh" tier-exempt --reason "G3 仲裁需要最高階首派" >/dev/null 2>&1 )
px_d fable
ck_msg "px 豁免未用+model=fable → 放行且訊息含「tier-exempt 已消耗」" 0 "tier-exempt 已消耗" "$PX_RC" "$PX_OUT"
ck "px 豁免卡消耗後確實轉 used:true+留 used_at(留痕)" 0 "$("$DEVFLOW_PY" -c "
import json, sys
d = json.load(open('$PXT/.devflow/tier-exempt.json'))
sys.exit(0 if d.get('used') is True and d.get('used_at') else 1)
"; echo $?)"
# 豁免一次性:耗盡後同樣情境(仍無低階 attempt)再次首派最高階 → 必須再度被擋,不得殘留放行
px_d fable
ck_msg "px 豁免耗盡後再次首派最高階 → 仍擋(一次性,非常駐白名單)" 2 "tier-exempt" "$PX_RC" "$PX_OUT"

# ⑤ model=sonnet(非最高階)→ 與本守衛無關,放行
px_d sonnet
ck "px 武裝中但 model=sonnet(非最高階)→ 放行" 0 "$PX_RC"

# exec-v2 舊字面值(A-11 升版前的 schema)雙讀相容:同一窄口徑情境跑一輪,結果須相同
"$DEVFLOW_PY" -c "
import json
p = '$PXT/.devflow/exec.json'
d = json.load(open(p))
d['schema'] = 'exec-v2'
json.dump(d, open(p, 'w'))
"
px_d opus
ck_msg "px exec-v2 舊字面值雙讀相容:同情境同結果(仍擋)" 2 "tier-exempt" "$PX_RC" "$PX_OUT"

# matcher 是 "Task|Agent" 兩種 tool_name 都要接住 —— 只測 Task 會漏掉 Agent 這條路徑
# (本檔第 6 型「不對稱保護」正是這種:同類情境只驗了觸發實例的其中一半)。
PX_OUT=$(cd "$PXT" && echo '{"tool_name":"Agent","tool_input":{"model":"opus"}}' \
  | "$H/devflow-dispatch-guard.sh" 2>&1); PX_RC=$?
ck_msg "px tool_name=Agent(非 Task)同等對待 → 首派最高階仍擋" 2 "tier-exempt" "$PX_RC" "$PX_OUT"
rm -rf "$PXT"

echo "-- s7 §7 前置修復:派工分層守衛真的在 sequential(legacy)生效(exec-v4+run_id 真跑,非手造)--"
# 派工單 §7 裁決:legacy sequential start 過去不寫 schema,守衛整支失效(舊行為
# 等同「窄口徑外一切放行」)。本組**全程走真的 devflow-exec.sh start**(不手造
# exec.json),證明補 schema/run_id 之後守衛是真的在最常用的 sequential 路徑上
# 生效,且四種情境都不誤判(正常派工放行 / 首派最高階擋下 / 已有低階攔升階放行 /
# 非 dev-flow 派工靜默放行)。
S7T=$(mktemp -d "${TMPDIR:-/tmp}/devflow-s7-seq.XXXXXX")
s7_d() { # s7_d <model>
  S7_OUT=$(cd "$S7T" && echo "{\"tool_name\":\"Task\",\"tool_input\":{\"model\":\"$1\"}}" \
    | "$H/devflow-dispatch-guard.sh" 2>&1); S7_RC=$?
}
mkdir -p "$S7T/docs/dev/s7seq" "$S7T/src"
( cd "$S7T" && git init -q . && git config user.email t@t && git config user.name t )
printf -- "---\nstatus: approved\n---\n" > "$S7T/docs/dev/s7seq/4-spec.md"
printf '%s\n' '## T-1 fixture' '- Covers: R-1' '- Files: src/a.py' '- Verify: `true`' \
  '- Blocked-by: —' > "$S7T/docs/dev/s7seq/5-tasks.md"
echo a > "$S7T/src/a.py"
( cd "$S7T" && git add -A >/dev/null && git commit -qm s7init )

# ① 真跑 legacy sequential start(無 --task、無 vnext 欄位)→ exec.json 必須真的
#   帶 schema=exec-v4 + 格式合法的 run_id(不是手造,是 start 命令自己寫出來的)
( cd "$S7T" && "$H/devflow-exec.sh" start s7seq >/dev/null 2>&1 )
ck "s7 legacy sequential start 真寫出 schema=exec-v4" 0 "$("$DEVFLOW_PY" -c "
import json, sys
d = json.load(open('$S7T/.devflow/exec.json'))
sys.exit(0 if d.get('schema') == 'exec-v4' and 'task' not in d else 1)
"; echo $?)"
S7RUN=$("$DEVFLOW_PY" -c "import json;print(json.load(open('$S7T/.devflow/exec.json'))['run_id'])" 2>/dev/null)
ck "s7 legacy sequential start 真生格式合法的 run_id(非 task-scoped 仍要有)" 0 "$("$DEVFLOW_PY" -c "
import re, sys
sys.exit(0 if re.match(r'^run_[0-9A-HJKMNP-TV-Z]{26}\$', '$S7RUN' or '') else 1)
"; echo $?)"

# ② 正常派工(該放行的要放行):武裝中 + model=sonnet(非最高階)→ 與本守衛無關
s7_d sonnet
ck "s7 sequential 真武裝中 + model=sonnet(非最高階)→ 放行" 0 "$S7_RC"

# ③ 首派就直接叫最高階模型(該擋的要擋):本 run 尚無任何低階 attempt → exit 2
s7_d opus
ck_msg "s7 sequential 真武裝+首派 opus(無低階 attempt)→ exit 2 且訊息含 tier-exempt" 2 "tier-exempt" "$S7_RC" "$S7_OUT"

# ④ 已經有低階嘗試後再升階(該放行):補一筆 haiku attempt_started → 首派 opus
#    視為合法升階(這條正是驗證 run_id 真的可用 —— 沒有 run_id 的話 §6.1 稽核與
#    本守衛的「本 run 已有低階 attempt」判斷都會永遠拿不到資料,見 _scan_low_tier
#    _attempt 的 `if not run_id: return False`,合法升階也會被誤擋)
mkdir -p "$S7T/.devflow/runs/$S7RUN/attempts/att-s7-1"
printf '%s\n' '{"event_type":"attempt_started","model":"haiku"}' \
  > "$S7T/.devflow/runs/$S7RUN/attempts/att-s7-1/events.jsonl"
s7_d opus
ck "s7 sequential 已有 haiku attempt → 首派 opus 視為合法升階,放行" 0 "$S7_RC"
rm -rf "$S7T/.devflow/runs/$S7RUN/attempts/att-s7-1"

# ⑤ 不是 dev-flow 派工的一般呼叫(該靜默放行):真武裝中,但 tool_input 無 model 欄
#    → 與本守衛無關,靜默放行(_dispatch_impl.py:9-12 的明文承諾,在真武裝下驗)
S7_OUT=$(cd "$S7T" && echo '{"tool_name":"Task","tool_input":{"prompt":"一般查詢,非 dev-flow 派工"}}' \
  | "$H/devflow-dispatch-guard.sh" 2>&1); S7_RC=$?
ck "s7 sequential 真武裝中但一般呼叫(tool_input 無 model 欄)→ 靜默放行" 0 "$S7_RC"

( cd "$S7T" && "$H/devflow-exec.sh" stop >/dev/null 2>&1 )
rm -rf "$S7T"

echo "-- s7b §7 前置修復:VNext feature-scope(非 --task)sequential 同樣真寫 schema+run_id --"
# 與 legacy 路徑是 _exec_impl.py 裡不同的程式碼段(:352-359 附近),兩條路徑各自
# 補的 schema/run_id 要分開驗證,不能只驗 legacy 那一條就當兩條都對。
S7BT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-s7b-vnext.XXXXXX")
mkdir -p "$S7BT/docs/dev/s7bfeat" "$S7BT/src"
( cd "$S7BT" && git init -q . && git config user.email t@t && git config user.name t )
printf -- "---\nstatus: approved\n---\n" > "$S7BT/docs/dev/s7bfeat/4-spec.md"
cat > "$S7BT/docs/dev/s7bfeat/5-tasks.md" <<'EOF'
---
feature: s7bfeat
stage: 5-tasks
status: approved
execution:
  mode: parallel
  max_parallel_tasks: 2
---

# 5. 任務(s7b VNext feature-scope fixture)

## T-1 甲
- [ ] 完成
- Covers: R-1
- Files: `src/a.py`
- Verify: `true`
- Blocked-by: —
EOF
echo a > "$S7BT/src/a.py"
( cd "$S7BT" && git add -A >/dev/null && git commit -qm s7binit )
# 無 --task → 即使 5-tasks 帶 execution.mode: parallel,仍是 VNext feature-scope
# (v1 語意)武裝,不是 task-scoped(task-scoped 只有 --task 那條路才會產生)
( cd "$S7BT" && "$H/devflow-exec.sh" start s7bfeat >/dev/null 2>&1 )
ck "s7b VNext feature-scope start(非 --task)真寫出 schema=exec-v4+run_id,非 task-scoped" 0 "$("$DEVFLOW_PY" -c "
import json, sys
d = json.load(open('$S7BT/.devflow/exec.json'))
sys.exit(0 if d.get('schema') == 'exec-v4' and 'task' not in d and d.get('run_id') else 1)
"; echo $?)"
S7B_OUT=$(cd "$S7BT" && echo '{"tool_name":"Agent","tool_input":{"model":"fable"}}' \
  | "$H/devflow-dispatch-guard.sh" 2>&1); S7B_RC=$?
ck_msg "s7b VNext feature-scope 真武裝+首派 fable(無低階 attempt)→ exit 2" 2 "tier-exempt" "$S7B_RC" "$S7B_OUT"
( cd "$S7BT" && "$H/devflow-exec.sh" stop >/dev/null 2>&1 )
rm -rf "$S7BT"

echo "-- s7c §7 前置修復:Stage 7 review 事後補審自建武裝(第三個寫點,無 Stage 6 state)同樣真寫 schema+run_id --"
# 與 s7/s7b 是 _exec_impl.py 裡第三個不同的 exec.json 寫點(review 子命令,
# 「事後補審」分支——本組 fixture 刻意不先跑 Stage 6 start,才會落到這個分支,
# 而不是「沿用既有 exec.json」那個 reuse 分支;既有 selftest 261 行那組
# Stage 7 圍欄測試全程都先 start 過,只驗過 reuse 分支,從沒驗過這個自建分支)。
S7CT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-s7c-review.XXXXXX")
mkdir -p "$S7CT/docs/dev/s7creview"
( cd "$S7CT" && git init -q . && git config user.email t@t && git config user.name t )
echo "占位:s7c review 自建武裝 fixture" > "$S7CT/docs/dev/s7creview/4-spec.md"
( cd "$S7CT" && git add -A >/dev/null && git commit -qm s7cinit )
# 無 .devflow/exec.json(未跑過 Stage 6 start)→ review <slug> 走事後補審自建分支
( cd "$S7CT" && "$H/devflow-exec.sh" review s7creview >/dev/null 2>&1 )
ck "s7c Stage 7 review 事後補審自建武裝真寫出 schema=exec-v4+run_id(仍是 phase=review,非 task-scoped)" 0 "$("$DEVFLOW_PY" -c "
import json, sys
d = json.load(open('$S7CT/.devflow/exec.json'))
sys.exit(0 if d.get('schema') == 'exec-v4' and 'task' not in d and d.get('run_id') and d.get('phase') == 'review' else 1)
"; echo $?)"
S7C_OUT=$(cd "$S7CT" && echo '{"tool_name":"Task","tool_input":{"model":"opus"}}' \
  | "$H/devflow-dispatch-guard.sh" 2>&1); S7C_RC=$?
ck_msg "s7c Stage 7 review 自建武裝+首派 opus(無低階 attempt)→ exit 2" 2 "tier-exempt" "$S7C_RC" "$S7C_OUT"
# 已有低階 attempt → 合法升階放行(驗證這個寫點的 run_id 也是真的可用,不是只
# 存在卻查不到——沒有 run_id 的話這條會被誤擋,見 s7 區塊④同款理由)
S7CRUN=$("$DEVFLOW_PY" -c "import json;print(json.load(open('$S7CT/.devflow/exec.json'))['run_id'])" 2>/dev/null)
mkdir -p "$S7CT/.devflow/runs/$S7CRUN/attempts/att-s7c-1"
printf '%s\n' '{"event_type":"attempt_started","model":"haiku"}' \
  > "$S7CT/.devflow/runs/$S7CRUN/attempts/att-s7c-1/events.jsonl"
S7C_OUT=$(cd "$S7CT" && echo '{"tool_name":"Task","tool_input":{"model":"opus"}}' \
  | "$H/devflow-dispatch-guard.sh" 2>&1); S7C_RC=$?
ck "s7c Stage 7 review 已有 haiku attempt → 首派 opus 視為合法升階,放行" 0 "$S7C_RC"
( cd "$S7CT" && "$H/devflow-exec.sh" stop >/dev/null 2>&1 )
rm -rf "$S7CT"

echo "-- pst §7-3b 探針(記錄用,不阻斷):真實 tool_input.subagent_type 欄位形狀 --"
# 派工單 notes/dispatch-agent-dispatch-layer.md §7-3b:repo 內先前零 fixture 驗證過
# PreToolUse 收到的 tool_input 有沒有 subagent_type 欄位、欄位名叫什麼、plugin 型別
# 帶不帶命名空間(既有 selftest.sh 的 Task/Agent payload 全部只帶 model 欄)。
# 2026-08-19 實測(claude --plugin-dir 把本 repo 當 session-only plugin 從另一個
# 專案載入 + 專案層 PreToolUse hook 直接把 stdin 落地存證):真實派工的
# tool_input 原始樣貌是
#   {"description":"...","prompt":"...","subagent_type":"dev-flow:devflow-reviewer",
#    "run_in_background":false}
# 欄位名確實叫 `subagent_type`(不是 agent_type),plugin 型別確實帶
# `<plugin>:<agent>` 命名空間——與 agents/devflow-reviewer.md 內「型別字串」節記的
# 是同一次測試,原始 payload 另存 `scripts/fixtures/dispatch-guard/pst-real-payload.json`
# 供人核對。R1(subagent_type 白名單攔截)已撤回(§3 裁決表),本守衛目前完全不讀
# 這個欄位——以下三案只是**釘住現況**(有/無 subagent_type 都不改變既有判準,只看
# tool_input.model),留給第二輪要做以型別為判準的檢查時,不必再猜欄位長相。
PSTT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-pst-subtype.XXXXXX")
mkdir -p "$PSTT/docs/dev/pstseq" "$PSTT/src"
( cd "$PSTT" && git init -q . && git config user.email t@t && git config user.name t )
printf -- "---\nstatus: approved\n---\n" > "$PSTT/docs/dev/pstseq/4-spec.md"
printf '%s\n' '## T-1 fixture' '- Covers: R-1' '- Files: src/a.py' '- Verify: `true`' \
  '- Blocked-by: —' > "$PSTT/docs/dev/pstseq/5-tasks.md"
echo a > "$PSTT/src/a.py"
( cd "$PSTT" && git add -A >/dev/null && git commit -qm pstinit )
( cd "$PSTT" && "$H/devflow-exec.sh" start pstseq >/dev/null 2>&1 )

# ① 真實 payload 形狀(subagent_type 命名空間型別,無 model 欄)→ 本守衛只認
#   tool_input.model,這裡沒有 → 與本守衛無關,靜默放行(不是「型別被判定合法」,
#   是根本沒被本守衛檢查——記錄現況,不是背書)
PST_OUT=$(cd "$PSTT" && "$DEVFLOW_PY" -c '
import json
print(json.dumps({"tool_name": "Agent", "tool_input": {
    "description": "T review", "prompt": "審查用 prompt(節錄)",
    "subagent_type": "dev-flow:devflow-reviewer", "run_in_background": False}}))
' | "$H/devflow-dispatch-guard.sh" 2>&1); PST_RC=$?
ck "pst 真實 subagent_type payload(無 model 欄)→ 本守衛不讀這欄,靜默放行" 0 "$PST_RC"
# ⚠️ 這條①是「現況釘」,不是永久契約——它斷言的是「本守衛目前不讀
# subagent_type」。第二輪若真的要做以型別為判準的檢查,這條會需要一起改掉,
# 屬預期反轉(§11 分兩輪的理由是不要跟本輪的行為變更混在一起,不是說這條案例
# 本身不能動)。

# ② 同一個 payload 額外帶 model=opus(有人在指名型別的同時又顯式覆寫模型)、
#   本 run 尚無低階 attempt → 判準仍是「有沒有 tool_input.model」,subagent_type
#   在不在場都不改變這條——確認 subagent_type 存在不會意外繞過既有攔截
PST_OUT=$(cd "$PSTT" && "$DEVFLOW_PY" -c '
import json
print(json.dumps({"tool_name": "Agent", "tool_input": {
    "subagent_type": "dev-flow:devflow-reviewer", "model": "opus"}}))
' | "$H/devflow-dispatch-guard.sh" 2>&1); PST_RC=$?
ck_msg "pst 帶 subagent_type 又顯式 model=opus、無低階 attempt → 仍照舊判準擋" 2 "tier-exempt" "$PST_RC" "$PST_OUT"

# ③ 已有低階 attempt 後,同款 payload(subagent_type + model=opus)→ 合法升階,
#   放行——subagent_type 在場一樣不影響既有升階邏輯
PSTRUN=$("$DEVFLOW_PY" -c "import json;print(json.load(open('$PSTT/.devflow/exec.json'))['run_id'])" 2>/dev/null)
mkdir -p "$PSTT/.devflow/runs/$PSTRUN/attempts/att-pst-1"
printf '%s\n' '{"event_type":"attempt_started","model":"haiku"}' \
  > "$PSTT/.devflow/runs/$PSTRUN/attempts/att-pst-1/events.jsonl"
PST_OUT=$(cd "$PSTT" && "$DEVFLOW_PY" -c '
import json
print(json.dumps({"tool_name": "Agent", "tool_input": {
    "subagent_type": "dev-flow:devflow-reviewer", "model": "opus"}}))
' | "$H/devflow-dispatch-guard.sh" 2>&1); PST_RC=$?
ck "pst 帶 subagent_type + model=opus,已有 haiku attempt → 合法升階,放行" 0 "$PST_RC"
( cd "$PSTT" && "$H/devflow-exec.sh" stop >/dev/null 2>&1 )
rm -rf "$PSTT"

echo "-- f4 豁免卡唯讀(fail-open):有效卡標記寫不回 → 放行 + 警告,不得擋 --"
# F4(2026-08-17):_consume_exemption 寫入遇 OSError 曾 return False → die ——
# 但本守衛自稱 fail-open,「寫不進去」是環境問題不是違規。釘死:唯讀卡照樣放行。
F4T=$(mktemp -d "${TMPDIR:-/tmp}/devflow-f4-exempt.XXXXXX")
mkdir -p "$F4T/.devflow"
printf '%s\n' '{"schema":"exec-v2","run_id":"f4run"}' > "$F4T/.devflow/exec.json"
printf '%s\n' '{"used":false,"reason":"f4 唯讀卡 fixture","created_at":"2026-08-17T00:00:00"}' \
  > "$F4T/.devflow/tier-exempt.json"
chmod 444 "$F4T/.devflow/tier-exempt.json"
F4_OUT=$(cd "$F4T" && echo '{"tool_name":"Task","tool_input":{"model":"opus"}}' \
  | "$H/devflow-dispatch-guard.sh" 2>&1); F4_RC=$?
ck_msg "f4 豁免卡有效但唯讀 → fail-open 放行 + 警告" 0 "標記寫入失敗" "$F4_RC" "$F4_OUT"
ck "f4 唯讀卡未被消耗(used 仍 false —— 下次再放行一次,可接受的降級)" 0 "$("$DEVFLOW_PY" -c "
import json, sys
d = json.load(open('$F4T/.devflow/tier-exempt.json'))
sys.exit(0 if d.get('used') is False else 1)"; echo $?)"
chmod 644 "$F4T/.devflow/tier-exempt.json"
rm -rf "$F4T"

echo "-- f2 大 payload(ARG_MAX):行為必須與小 payload 完全一致,不得 rc=126 靜默自壞 --"
# F2(2026-08-17):舊殼層 `HOOK_INPUT=$(cat); export HOOK_INPUT` 讓 >1MB payload
# 令其後每個 exec 撞 ARG_MAX(macOS 約 1MB)→ rc=126 —— 對宿主是「守衛自壞」,
# 通常等同放行:fail-closed 靜默降級 fail-open。修法 = stdin 直通 python
# (devflow-lib.read_hook_input)。這一組釘死「大 payload 的該擋照擋、該放照放」——
# 沒有它,下次有人改回 env 傳遞不會有任何紅字。
F2T=$(mktemp -d "${TMPDIR:-/tmp}/devflow-f2-argmax.XXXXXX")
mkdir -p "$F2T/docs/dev/f2big" "$F2T/src"
( cd "$F2T" && git init -q . && git config user.email t@t && git config user.name t )
printf -- "---\nstatus: approved\n---\n" > "$F2T/docs/dev/f2big/4-spec.md"
printf '%s\n' \
  '## T-1 f2 fixture' \
  '- Covers: R-1' \
  '- Files: src/a.py' \
  '- Verify: `true`' \
  '- Blocked-by: —' > "$F2T/docs/dev/f2big/5-tasks.md"
echo a > "$F2T/src/a.py"
( cd "$F2T" && git add -A >/dev/null && git commit -qm f2init )

f2_big_write() { # $1 = file_path;1.1MB content 直灌 devflow-guard.sh stdin
  F2_OUT=$(cd "$F2T" && "$DEVFLOW_PY" -c "import json;print(json.dumps({'tool_name':'Write','tool_input':{'file_path':'$1','content':'A'*1100000}}))" \
    | "$H/devflow-guard.sh" 2>&1); F2_RC=$?
}

# ① 未武裝 + 1.1MB Write → 放行(與小 payload 相同;修前 rc=126)
f2_big_write "$F2T/src/a.py"
ck "f2 未武裝 + 1.1MB Write → 放行(修前 rc=126 自壞)" 0 "$F2_RC"

( cd "$F2T" && "$H/devflow-exec.sh" start f2big >/dev/null 2>&1 )

# ② 武裝 + 1.1MB Write 到 scope 內檔 → 放行(該放的照放)
f2_big_write "$F2T/src/a.py"
ck "f2 武裝 + 1.1MB Write scope 內 → 放行" 0 "$F2_RC"

# ③ 武裝 + 1.1MB Write 到 scope 外檔 → exit 2(該擋的照擋,不得 126)
f2_big_write "$F2T/src/outside.py"
ck_msg "f2 武裝 + 1.1MB Write scope 外 → exit 2(硬擋不因 payload 大小失效)" 2 "scope 外寫入" "$F2_RC" "$F2_OUT"

# ④ prebash:武裝 + 1.1MB 指令含 sentinel 破壞字面 → exit 2
F2_OUT=$(cd "$F2T" && "$DEVFLOW_PY" -c "import json;print(json.dumps({'tool_name':'Bash','tool_input':{'command':'rm .devflow/devflow-armed # '+'A'*1100000}}))" \
  | "$H/devflow-prebash.sh" 2>&1); F2_RC=$?
ck_msg "f2 prebash 武裝 + 1.1MB 指令含破壞字面 → exit 2" 2 "破壞守衛狀態" "$F2_RC" "$F2_OUT"

# ⑤ prebash:武裝 + 1.1MB 無害指令 → 放行
F2_OUT=$(cd "$F2T" && "$DEVFLOW_PY" -c "import json;print(json.dumps({'tool_name':'Bash','tool_input':{'command':'echo '+'A'*1100000}}))" \
  | "$H/devflow-prebash.sh" 2>&1); F2_RC=$?
ck "f2 prebash 武裝 + 1.1MB 無害指令 → 放行" 0 "$F2_RC"

# ⑥ dispatch-guard:exec-v2 武裝 + 首派 opus + 1.1MB prompt → exit 2(fail-open 守衛
# 自壞 = 永遠放行,更要釘)。獨立 fixture:sequential start 寫的 exec.json 無 schema
# 欄,dispatch-guard 窄口徑本來就放行 —— 要測 deny 路徑必須手造 exec-v2 旗標
# (dispatch-guard 不驗 shadow hash,手造安全;同 px 段做法)。
F2DT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-f2-dispatch.XXXXXX")
mkdir -p "$F2DT/.devflow"
printf '%s\n' '{"schema":"exec-v2","run_id":"f2run"}' > "$F2DT/.devflow/exec.json"
F2_OUT=$(cd "$F2DT" && "$DEVFLOW_PY" -c "import json;print(json.dumps({'tool_name':'Task','tool_input':{'model':'opus','prompt':'A'*1100000}}))" \
  | "$H/devflow-dispatch-guard.sh" 2>&1); F2_RC=$?
ck_msg "f2 dispatch exec-v2 武裝 + 首派 opus + 1.1MB prompt → exit 2" 2 "tier-exempt" "$F2_RC" "$F2_OUT"
rm -rf "$F2DT"

# ⑦ postbash:1.1MB payload → 偵測網照跑(乾淨樹放行,不得 126)
F2_OUT=$(cd "$F2T" && "$DEVFLOW_PY" -c "import json;print(json.dumps({'tool_name':'Bash','tool_input':{'command':'echo '+'A'*1100000},'session_id':'f2-selftest'}))" \
  | "$H/devflow-postbash.sh" 2>&1); F2_RC=$?
ck "f2 postbash + 1.1MB payload → 偵測網照跑(乾淨樹放行)" 0 "$F2_RC"

( cd "$F2T" && "$H/devflow-exec.sh" stop >/dev/null 2>&1 )
rm -rf "$F2T"

echo "-- rg 缺陷回報去識別化守衛(只掃 .devflow/reports/*.md;結構特徵擋、語意靠人)--"
# 第五部分(2026-08-17):dev-report skill 的機械層。正負向都要:命中要擋、
# 非回報路徑要放行、空輸入/壞 JSON 要放行(fail-open 於環境問題)。
RGT=$(mktemp -d "${TMPDIR:-/tmp}/devflow-rg-report.XXXXXX")
mkdir -p "$RGT/.devflow/reports"
rg_run() { RG_OUT=$(printf '{"tool_name":"Write","tool_input":{"file_path":"%s"}}' "$1" \
  | "$H/devflow-report-guard.sh" 2>&1); RG_RC=$?; }

cat > "$RGT/.devflow/reports/clean.md" <<'EOF'
# 回報:觀測欄字元集不認全形冒號
- 現象:❌ C1 每個 S 都有觀測欄(16 個 S 裡有 13 個被誤判)
- 位置:scripts/check-spec-gate.sh:85
- 重現:<專案根>/docs/dev/<slug>/4-spec.md 用全形冒號寫觀測欄
- 環境:plugin 3.6.1 / 契約 2.0.0
EOF
rg_run "$RGT/.devflow/reports/clean.md"
ck "rg 乾淨回報(母版路徑+泛化+版本+數量)→ 放行" 0 "$RG_RC"

printf '%s\n' '重現:/Users/somebody/dev/companyapp/main.go 觸發' > "$RGT/.devflow/reports/dirty-abs.md"
rg_run "$RGT/.devflow/reports/dirty-abs.md"
ck_msg "rg 絕對路徑 → exit 2 並點名規則" 2 "絕對路徑" "$RG_RC" "$RG_OUT"

printf '%s\n' '受影響檔:src/billing/invoice_service.go 的匯入' > "$RGT/.devflow/reports/dirty-path.md"
rg_run "$RGT/.devflow/reports/dirty-path.md"
ck_msg "rg 母版沒有的相對路徑 → exit 2(疑為採用專案的)" 2 "不存在於母版" "$RG_RC" "$RG_OUT"

printf '%s\n' '已修於 3f2ab9c 這個提交' > "$RGT/.devflow/reports/dirty-sha.md"
rg_run "$RGT/.devflow/reports/dirty-sha.md"
ck_msg "rg git SHA → exit 2" 2 "git SHA" "$RG_RC" "$RG_OUT"

printf '%s\n' '筆記:/Users/somebody/dev/companyapp/main.go' > "$RGT/notes.md"
rg_run "$RGT/notes.md"
ck "rg 非回報路徑(含識別特徵)→ 一律靜默放行" 0 "$RG_RC"

RG_OUT=$(printf '' | "$H/devflow-report-guard.sh" 2>&1); RG_RC=$?
ck "rg 空輸入 → 放行(fail-open 於環境問題)" 0 "$RG_RC"
RG_OUT=$(printf 'not-json{{{' | "$H/devflow-report-guard.sh" 2>&1); RG_RC=$?
ck "rg 壞 JSON → 放行(fail-open 於環境問題)" 0 "$RG_RC"

# 審查修正回歸(2026-08-17 fresh sonnet 三個 HIGH):
# ① 非 UTF-8 位元組不得 crash(曾 traceback rc=1),照掃 —— 髒內容仍要 2
printf '\xff\xfe mojibake \n/Users/somebody/companyapp/x.go\n' > "$RGT/.devflow/reports/rawbytes.md"
rg_run "$RGT/.devflow/reports/rawbytes.md"
ck_msg "rg 非 UTF-8 內容不 crash,照掃出絕對路徑 → exit 2" 2 "絕對路徑" "$RG_RC" "$RG_OUT"
# ② 32KB slash 長行不得回溯爆炸(曾 8.4s,~60KB 就吃掉 15s timeout = 掃描被殺)
"$DEVFLOW_PY" -c "open('$RGT/.devflow/reports/longline.md','w').write('a/'*16000 + '\n')"
rg_run "$RGT/.devflow/reports/longline.md"
ck "rg 32KB slash 長行 → 秒級掃完放行(線性正則,不得逾時自壞)" 0 "$RG_RC"
# ③ 帶 .. 的等價路徑不得跳過掃描(normpath 後比對;somedir 需真實存在,
#    否則 open 原始路徑 ENOENT 走 fail-open,測的就不是繞路而是讀不到)
mkdir -p "$RGT/.devflow/somedir"
printf '/Users/somebody/companyapp/x.go\n' > "$RGT/.devflow/reports/trav.md"
RG_OUT=$(printf '{"tool_name":"Write","tool_input":{"file_path":"%s"}}' "$RGT/.devflow/somedir/../reports/trav.md" \
  | "$H/devflow-report-guard.sh" 2>&1); RG_RC=$?
ck_msg "rg .devflow/x/../reports/ 等價路徑 → 照掃仍擋" 2 "絕對路徑" "$RG_RC" "$RG_OUT"
rm -rf "$RGT"

echo "-- c2 tier-exempt 豁免卡 run 級:stop 清未消耗的卡、留已消耗的卡 --"
# Backlog C-2 裁決(2026-08-17):豁免是 run 級授權 —— stop = run 結束,未消耗的卡
# 不得跨 run 存活(會被下一個不相關 run 的首派吃掉);已消耗的卡是留痕,保留。
C2T=$(mktemp -d "${TMPDIR:-/tmp}/devflow-c2-exempt.XXXXXX")
( cd "$C2T" && git init -q . && git config user.email t@t && git config user.name t )
mkdir -p "$C2T/.devflow"
printf '%s\n' '{"schema":"exec-v2","run_id":"c2"}' > "$C2T/.devflow/exec.json"
printf '%s\n' '{"used":false,"reason":"c2 未消耗卡"}' > "$C2T/.devflow/tier-exempt.json"
C2_OUT=$(cd "$C2T" && "$H/devflow-exec.sh" stop 2>&1); C2_RC=$?
ck_msg "c2 stop 訊息點名清掉未消耗豁免卡(run 級)" 0 "tier-exempt" "$C2_RC" "$C2_OUT"
ck "c2 未消耗卡在 stop 後確實消失" 0 "$([ ! -f "$C2T/.devflow/tier-exempt.json" ]; echo $?)"
printf '%s\n' '{"schema":"exec-v2","run_id":"c2"}' > "$C2T/.devflow/exec.json"
printf '%s\n' '{"used":true,"used_at":"2026-08-17T00:00:00","reason":"c2 已消耗卡"}' > "$C2T/.devflow/tier-exempt.json"
( cd "$C2T" && "$H/devflow-exec.sh" stop >/dev/null 2>&1 )
ck "c2 已消耗卡在 stop 後保留(留痕不清)" 0 "$([ -f "$C2T/.devflow/tier-exempt.json" ]; echo $?)"
rm -rf "$C2T"

echo "-- g1 history-append 專案根解析:散發位置不得巢狀寫入(docs/dev/docs/dev)--"
# G1(2026-08-17 採用現場):腳本曾用「自身位置/..」推專案根,散發到
# docs/dev/tools/ 後預設輸出**靜默**寫到 docs/dev/docs/dev/HISTORY.md。
# 修法 = git toplevel(以腳本自身位置 -C 解析)。四案釘死兩個位置 + 非 git 拒絕。
G1T=$(mktemp -d "${TMPDIR:-/tmp}/devflow-g1-history.XXXXXX")
mkdir -p "$G1T/docs/dev/tools"
( cd "$G1T" && git init -q . && git config user.email t@t && git config user.name t )
cp "$H/../scripts/history-append.sh" "$G1T/docs/dev/tools/history-append.sh"
chmod +x "$G1T/docs/dev/tools/history-append.sh"
( cd "$G1T" && bash docs/dev/tools/history-append.sh --slug g1 --what a --why b --where c >/dev/null 2>&1 )
ck "g1 散發位置不帶 --file → 寫到 <root>/docs/dev/HISTORY.md" 0 "$([ -f "$G1T/docs/dev/HISTORY.md" ]; echo $?)"
ck "g1 不得建出巢狀 docs/dev/docs 目錄(修前真的建出來)" 0 "$([ ! -e "$G1T/docs/dev/docs" ]; echo $?)"
mkdir -p "$G1T/scripts" && cp "$H/../scripts/history-append.sh" "$G1T/scripts/history-append.sh"
( cd "$G1T" && bash scripts/history-append.sh --slug g1b --what a --why b --where c >/dev/null 2>&1 )
ck "g1 母版位置(scripts/)同一支腳本 → 同樣寫到 <root>/docs/dev/HISTORY.md" 0 "$(grep -q "g1b" "$G1T/docs/dev/HISTORY.md"; echo $?)"
G1N=$(mktemp -d "${TMPDIR:-/tmp}/devflow-g1-nogit.XXXXXX")
cp "$H/../scripts/history-append.sh" "$G1N/history-append.sh"
G1_OUT=$(cd "$G1N" && bash history-append.sh --slug g1 --what a --why b --where c 2>&1); G1_RC=$?
ck_msg "g1 不在 git repo 且未帶 --file → 拒絕並指路 --file" 2 "--file" "$G1_RC" "$G1_OUT"
rm -rf "$G1T" "$G1N"

cd / && rm -rf "$T" "$C"
echo
TOTAL=$((PASS+FAIL))
if [ "$TOTAL" != "$TOTAL_CASES" ]; then
  FAIL=$((FAIL+1)); FAILED+=("自測案例發現數 $TOTAL_CASES 與執行數 $TOTAL 不一致")
fi
# 第 5 型地板:TOTAL_CASES 低於釘死值 → 案例可能被刪,即使與 TOTAL 自洽也要紅。
if [ "$TOTAL_CASES" -lt "$MIN_CASES" ]; then
  FAIL=$((FAIL+1))
  FAILED+=("⛔ 案例數地板:TOTAL_CASES=$TOTAL_CASES 低於釘死地板 MIN_CASES=$MIN_CASES —— 可能有測試被刪,即使執行數與發現數自洽也不得視為全過")
fi
if [ "$FAIL" = 0 ]; then echo "✅ 守衛自測 $PASS/$TOTAL 全過"; exit 0
else echo "❌ 守衛自測 $PASS/$TOTAL,失敗 $FAIL 項:"; for f in "${FAILED[@]}"; do echo "   - $f"; done; exit 1; fi
