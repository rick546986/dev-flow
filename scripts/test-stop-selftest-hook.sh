#!/bin/bash
# test-stop-selftest-hook.sh — .claude/hooks/run-selftest.sh(Claude Code Stop hook)的行為牙。
#
# 咬兩支 Stop hook:本 repo 自用的 .claude/hooks/run-selftest.sh(掛 .claude/settings.json),
# 與隨 plugin 發給採用專案的 hooks/devflow-stop-selftest.sh(掛 hooks/hooks.json;後半段
# 「plugin 版」)。
#
# 咬什麼(repo 版):Stop hook 改完自動跑 selftest,沒過擋住結束。三個必守情境 + 周邊:
#   ① stop_hook_active=true → exit 0(就算有變更、selftest 會紅也不得再擋 = 防無限迴圈)
#   ② 無變更且本分支沒有 main 以外的 commit → exit 0,且 selftest 指令根本沒被呼叫
#   ③ selftest 失敗 → exit 2,stderr 有「selftest 未過,請修到全綠再結束」與尾 40 行
#   周邊:成功 → exit 0 且不印東西;分支領先 main(工作樹乾淨)也要跑;未追蹤檔算變更;
#   .claude/settings.json 的 Stop 掛載用官方 exec form、timeout 600、沒有官方說對 Stop
#   無效的 onFailure、既有 permissions.allow 還在。
# plugin 版另咬:關閉開關、專案自己已掛 run-selftest.sh 時讓出(母版不重複跑)、通過後 TTL 內
# 節流(失敗不記、換直譯器失效、TTL=0 每次跑)、找 Python 3.12+(版本優先序、舊版被跳過、
# 全找不到 → fail-open + 合法 JSON systemMessage 且 24 小時只提醒一次、DEVFLOW_PYTHON 明示但
# 太舊不偷換)、失敗訊息告訴 Claude 別改 plugin、hooks.json Stop 掛載形狀與可執行位元。
# selftest 以 DEVFLOW_STOP_SELFTEST_CMD 注入替身,不跑真的 hooks/selftest.sh(否則遞迴)。
#
# 用法:scripts/test-stop-selftest-hook.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

HOOK="$ROOT/.claude/hooks/run-selftest.sh"
SETTINGS="$ROOT/.claude/settings.json"
PHOOK="$ROOT/hooks/devflow-stop-selftest.sh"
HOOKS_JSON="$ROOT/hooks/hooks.json"
[ -f "$HOOK" ] || { echo "FATAL: 找不到 $HOOK" >&2; exit 2; }
[ -f "$SETTINGS" ] || { echo "FATAL: 找不到 $SETTINGS" >&2; exit 2; }
[ -f "$PHOOK" ] || { echo "FATAL: 找不到 $PHOOK" >&2; exit 2; }
[ -f "$HOOKS_JSON" ] || { echo "FATAL: 找不到 $HOOKS_JSON" >&2; exit 2; }
command -v git >/dev/null 2>&1 || { echo "FATAL: 需要 git" >&2; exit 2; }

MIN_CASES=44
PASS=0
FAIL=0
TOTAL=0

WORK=$(mktemp -d "${TMPDIR:-/tmp}/devflow-stop-hook-test.XXXXXX") || exit 2
trap 'rm -rf "$WORK"' EXIT

expect() {  # expect <label> <condition-rc>
  TOTAL=$((TOTAL + 1))
  if [ "$2" -eq 0 ]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $1" >&2
  fi
}

mkrepo() {  # mkrepo <dir> [分支名,預設 main]:建一個該分支上有一個 commit 的假專案
  rm -rf "$1" && mkdir -p "$1"
  (
    cd "$1" || exit 1
    git init -q -b "${2:-main}" . \
      && git config user.email t@example.invalid && git config user.name t \
      && echo base > base.txt && git add base.txt && git commit -q -m base
  ) || { echo "FATAL: 建不了假 repo" >&2; exit 2; }
}

# run_hook <repo> <stdin-json> <cmd>:印 exit code 到 $WORK/rc、stderr 到 $WORK/err
run_hook() {
  local repo=$1 json=$2 cmd=$3
  printf '%s' "$json" \
    | CLAUDE_PROJECT_DIR="$repo" DEVFLOW_STOP_SELFTEST_CMD="$cmd" bash "$HOOK" \
      >"$WORK/out" 2>"$WORK/err"
  echo $? >"$WORK/rc"
}
rc() { cat "$WORK/rc"; }

REPO="$WORK/repo"
MARK="$WORK/called"
SPY="echo called >> $MARK"
FAILCMD="seq 1 60; exit 1"

# ① stop_hook_active=true:有變更 + selftest 會紅,仍 exit 0 且不跑
mkrepo "$REPO"; echo dirty >> "$REPO/base.txt"; rm -f "$MARK"
run_hook "$REPO" '{"session_id":"s","stop_hook_active": true}' "$SPY; exit 1"
expect "stop_hook_active=true → exit 0" "$([ "$(rc)" = 0 ]; echo $?)"
expect "stop_hook_active=true → selftest 未被呼叫" "$([ ! -e "$MARK" ]; echo $?)"

# ② 無變更、HEAD == main:exit 0 且不跑
mkrepo "$REPO"; rm -f "$MARK"
run_hook "$REPO" '{"stop_hook_active":false}' "$SPY; exit 1"
expect "無變更 → exit 0" "$([ "$(rc)" = 0 ]; echo $?)"
expect "無變更 → selftest 未被呼叫" "$([ ! -e "$MARK" ]; echo $?)"

# ③ 有變更 + selftest 失敗:exit 2、stderr 有提示、只留尾 40 行
mkrepo "$REPO"; echo dirty >> "$REPO/base.txt"
run_hook "$REPO" '{"stop_hook_active":false}' "$FAILCMD"
expect "selftest 失敗 → exit 2" "$([ "$(rc)" = 2 ]; echo $?)"
expect "失敗 → stderr 有「selftest 未過,請修到全綠再結束」" \
  "$(grep -q 'selftest 未過，請修到全綠再結束' "$WORK/err"; echo $?)"
expect "失敗 → stderr 含輸出最後一行(60)" "$(grep -qx 60 "$WORK/err"; echo $?)"
expect "失敗 → stderr 只留尾 40 行(第 20 行不在)" "$(! grep -qx 20 "$WORK/err"; echo $?)"

# 周邊:成功 → exit 0 且無 stderr
mkrepo "$REPO"; echo dirty >> "$REPO/base.txt"
run_hook "$REPO" '' "true"
expect "selftest 通過 → exit 0 且 stderr 空" "$([ "$(rc)" = 0 ] && [ ! -s "$WORK/err" ]; echo $?)"

# 周邊:工作樹乾淨但分支領先 main → 照跑(失敗 → 2)
mkrepo "$REPO"
( cd "$REPO" && git checkout -q -b feat && echo x > f.txt && git add f.txt && git commit -q -m feat ) || exit 2
run_hook "$REPO" '{}' "$FAILCMD"
expect "分支領先 main、工作樹乾淨、selftest 失敗 → exit 2" "$([ "$(rc)" = 2 ]; echo $?)"

# 周邊:只有未追蹤檔也算變更
mkrepo "$REPO"; echo new > "$REPO/untracked.txt"
run_hook "$REPO" '{}' "$FAILCMD"
expect "只有未追蹤檔、selftest 失敗 → exit 2" "$([ "$(rc)" = 2 ]; echo $?)"

# settings.json 掛載
python3 - "$SETTINGS" <<'PY'
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
allow = d.get("permissions", {}).get("allow", [])
entries = d.get("hooks", {}).get("Stop", [])
ok_mount = (
    len(entries) == 1
    and "matcher" not in entries[0]
    and len(entries[0]["hooks"]) == 1
    and entries[0]["hooks"][0].get("type") == "command"
    and entries[0]["hooks"][0].get("command") == "bash"
    and entries[0]["hooks"][0].get("args") == ["${CLAUDE_PROJECT_DIR}/.claude/hooks/run-selftest.sh"]
    and entries[0]["hooks"][0].get("timeout") == 600
)
bad = "onFailure" in json.dumps(d.get("hooks", {}))
sys.exit(0 if ok_mount and not bad and "mcp__Google_Drive__read_file_content" in allow else 1)
PY
expect "settings.json Stop 掛載(exec form/timeout 600/無 onFailure/permissions 保留)" "$?"

# ───────────────────────── plugin 版:hooks/devflow-stop-selftest.sh ─────────────────────────
# 假直譯器:`-c <code>` 交給真的 python3 跑,但先把 sys.version_info 換成指定版本 ——
# 所以 hook 的「3.12+」判斷是真的被執行(把門檻改鬆測得到),而不是看假檔的 exit 碼。
BIN="$WORK/fakebin"; TOOLS="$WORK/toolbin"; mkdir -p "$BIN" "$TOOLS" "$WORK/home"
REAL_PY=$(command -v python3) || { echo "FATAL: 需要 python3" >&2; exit 2; }
fake_py() {  # fake_py <路徑> <假版本 X.Y>
  printf '#!/bin/sh\n[ "$1" = "-c" ] || exit 0\nexec "%s" -c %s "$2" "%s"\n' "$REAL_PY" \
    "'import sys; sys.version_info = tuple(int(x) for x in sys.argv[2].split(\".\")) + (0,); exec(sys.argv[1])'" "$2" >"$1"
  chmod 755 "$1"
}
fake_py "$WORK/py-ok" 3.13
fake_py "$WORK/py-ok2" 3.12
fake_py "$WORK/py-old" 3.9
# 最小 PATH:只放 hook 自己要用的工具,擋掉本機真的 python3.x(否則「全找不到」測不到)
for t in bash git grep cat date cksum cut sed head tail mktemp rm mkdir dirname seq; do
  src=$(command -v "$t" 2>/dev/null) && ln -sf "$src" "$TOOLS/$t"
done

# run_plugin <repo> <stdin-json> <cmd> [VAR=val ...]:rc → $WORK/rc、stdout → $WORK/out、stderr → $WORK/err
# 狀態檔(節流)放 $WORK/data,每個案例組自己 rm -rf 重來。不繼承使用者環境的開關。
run_plugin() {
  local repo=$1 json=$2 cmd=$3; shift 3
  printf '%s' "$json" \
    | env -u DEVFLOW_STOP_SELFTEST -u DEVFLOW_STOP_SELFTEST_TTL -u DEVFLOW_PYTHON -u DEVFLOW_STOP_PY_DIRS \
        CLAUDE_PROJECT_DIR="$repo" CLAUDE_PLUGIN_DATA="$WORK/data" HOME="$WORK/home" \
        DEVFLOW_STOP_SELFTEST_CMD="$cmd" "$@" bash "$PHOOK" >"$WORK/out" 2>"$WORK/err"
  echo $? >"$WORK/rc"
}
dirty_repo() { mkrepo "$REPO"; echo dirty >> "$REPO/base.txt"; rm -f "$MARK"; rm -rf "$WORK/data"; }

# P1 stop_hook_active=true → 不跑
dirty_repo
run_plugin "$REPO" '{"stop_hook_active": true}' "$SPY" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:stop_hook_active=true → exit 0 且不跑" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"

# P2 DEVFLOW_STOP_SELFTEST=off → 不跑(有變更、selftest 會紅也不擋)
dirty_repo
run_plugin "$REPO" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-ok" DEVFLOW_STOP_SELFTEST=off
expect "plugin:DEVFLOW_STOP_SELFTEST=off → exit 0 且不跑" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"

# P3 專案自己已掛 run-selftest.sh(母版 repo)→ 讓出,不重複跑
dirty_repo; mkdir -p "$REPO/.claude"
printf '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"bash","args":["x/.claude/hooks/run-selftest.sh"]}]}]}}\n' >"$REPO/.claude/settings.json"
run_plugin "$REPO" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:專案 settings 已掛 run-selftest.sh → exit 0 且不跑(不重複)" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"
run_plugin "$ROOT" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:本 repo(已掛 .claude Stop)→ exit 0 且不跑" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"

# P4 無變更、HEAD == main → 不跑
mkrepo "$REPO"; rm -f "$MARK"; rm -rf "$WORK/data"
run_plugin "$REPO" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:無變更 → exit 0 且不跑" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"

# P4b 基準分支探測(v3.26.1):主幹叫 master / origin/HEAD 指向非 main / 全無基準
# master 主幹:乾淨 → 不跑(舊版只認 main,BASE 空、AHEAD=1 → 純問答也觸發)
mkrepo "$REPO" master; rm -f "$MARK"; rm -rf "$WORK/data"
run_plugin "$REPO" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:master 主幹、無變更 → exit 0 且不跑" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"
# master 主幹:有未提交變更 → 跑
mkrepo "$REPO" master; echo dirty >> "$REPO/base.txt"; rm -f "$MARK"; rm -rf "$WORK/data"
run_plugin "$REPO" '{}' "$FAILCMD" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:master 主幹、有未提交變更 → 跑(失敗 exit 2)" "$([ "$(rc)" = 2 ]; echo $?)"
# master 主幹:分支領先 master、工作樹乾淨 → 跑
mkrepo "$REPO" master; rm -rf "$WORK/data"
( cd "$REPO" && git checkout -q -b feat && echo x > f.txt && git add f.txt && git commit -q -m feat ) || exit 2
run_plugin "$REPO" '{}' "$FAILCMD" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:分支領先 master、工作樹乾淨 → 跑(失敗 exit 2)" "$([ "$(rc)" = 2 ]; echo $?)"
# origin/master(無本地 master)也認得
mkrepo "$REPO" master; rm -rf "$WORK/data"
( cd "$REPO" && git update-ref refs/remotes/origin/master HEAD && git checkout -q -b feat \
  && git branch -q -D master ) || exit 2
rm -f "$MARK"; run_plugin "$REPO" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:只有 origin/master(無本地 master)、HEAD 同它、無變更 → 不跑" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"
# origin/HEAD 指向非 main(develop):HEAD 就在 origin/develop、本地另有落後的 main → 不跑
# (若退回只看 main:main 落後 HEAD 1 個 commit → AHEAD=1 → 會誤跑)
mkrepo "$REPO" main; rm -rf "$WORK/data"
( cd "$REPO" && git checkout -q -b develop && echo d > d.txt && git add d.txt && git commit -q -m dev \
  && git update-ref refs/remotes/origin/develop HEAD \
  && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/develop ) || exit 2
rm -f "$MARK"; run_plugin "$REPO" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:origin/HEAD→origin/develop、HEAD 在它上面、無變更 → 不跑(優先於 main)" \
  "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"
# 同一個 repo,HEAD 再領先 origin/develop 一個 commit → 跑
( cd "$REPO" && echo e > e.txt && git add e.txt && git commit -q -m ahead ) || exit 2
run_plugin "$REPO" '{}' "$FAILCMD" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:領先 origin/HEAD 所指分支 → 跑(失敗 exit 2)" "$([ "$(rc)" = 2 ]; echo $?)"
# origin/HEAD 懸空(指向不存在的 ref)→ 不炸、退回名單(main)
mkrepo "$REPO" main; rm -rf "$WORK/data"
( cd "$REPO" && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/gone ) || exit 2
rm -f "$MARK"; run_plugin "$REPO" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:origin/HEAD 懸空 → 退回 main 名單、無變更 → 不跑" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"
# 全無基準(分支叫 trunk、無遠端):乾淨 → 不跑(AHEAD 視為 0);有未提交變更 → 跑
mkrepo "$REPO" trunk; rm -rf "$WORK/data"
( cd "$REPO" && echo y > y.txt && git add y.txt && git commit -q -m more ) || exit 2
rm -f "$MARK"; run_plugin "$REPO" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:全無基準分支、無變更 → 不跑(不再保守視為有 commit)" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"
echo dirty >> "$REPO/base.txt"
run_plugin "$REPO" '{}' "$FAILCMD" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:全無基準分支、有未提交變更 → 跑(失敗 exit 2)" "$([ "$(rc)" = 2 ]; echo $?)"

# P5 失敗 → exit 2、尾 40 行、叫 Claude 別改 plugin、失敗不記節流
dirty_repo
run_plugin "$REPO" '{}' "$FAILCMD" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:selftest 失敗 → exit 2" "$([ "$(rc)" = 2 ]; echo $?)"
expect "plugin:失敗 → stderr 有「守衛自測未過」與輸出最後一行,且只留尾 40 行" \
  "$(grep -q '守衛自測未過' "$WORK/err" && grep -qx 60 "$WORK/err" && ! grep -qx 20 "$WORK/err"; echo $?)"
expect "plugin:失敗 → stderr 叫 Claude 回報、不要改 plugin,並給關閉開關" \
  "$(grep -q '不要去改 plugin 檔案' "$WORK/err" && grep -q 'DEVFLOW_STOP_SELFTEST=off' "$WORK/err" && grep -q 'disableAllHooks' "$WORK/err"; echo $?)"
run_plugin "$REPO" '{}' "$SPY" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:失敗不記節流 → 下一次仍會跑" "$([ "$(rc)" = 0 ] && [ -e "$MARK" ]; echo $?)"

# P6 通過 → 記節流;TTL 內不重跑;TTL=0 每次跑;換直譯器失效
dirty_repo
run_plugin "$REPO" '{}' "$SPY" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:通過 → exit 0、stderr 空、有跑" "$([ "$(rc)" = 0 ] && [ ! -s "$WORK/err" ] && [ -e "$MARK" ]; echo $?)"
rm -f "$MARK"; run_plugin "$REPO" '{}' "$SPY" DEVFLOW_PYTHON="$WORK/py-ok"
expect "plugin:通過後 TTL 內再 Stop → 不重跑(節流)" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"
rm -f "$MARK"; run_plugin "$REPO" '{}' "$SPY" DEVFLOW_PYTHON="$WORK/py-ok" DEVFLOW_STOP_SELFTEST_TTL=0
expect "plugin:DEVFLOW_STOP_SELFTEST_TTL=0 → 每次都跑" "$([ "$(rc)" = 0 ] && [ -e "$MARK" ]; echo $?)"
rm -f "$MARK"; run_plugin "$REPO" '{}' "$SPY" DEVFLOW_PYTHON="$WORK/py-ok2"
expect "plugin:換直譯器 → 節流失效、重跑" "$([ "$(rc)" = 0 ] && [ -e "$MARK" ]; echo $?)"
rm -f "$MARK"; run_plugin "$REPO" '{}' "$SPY" DEVFLOW_PYTHON="$WORK/py-ok2" DEVFLOW_STOP_SELFTEST_TTL=abc
expect "plugin:TTL 不是數字 → 退回預設 6 小時(已通過 → 不重跑)" "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ]; echo $?)"

# P7 找直譯器:3.13 優先於 3.12;不到 3.12 的(假 3.14 回 1)被跳過;選到的值以 DEVFLOW_PYTHON 傳給自測
rm -rf "$BIN"; mkdir -p "$BIN"
fake_py "$BIN/python3.12" 3.12; fake_py "$BIN/python3.13" 3.13; fake_py "$BIN/python3.14" 3.11
dirty_repo; rm -f "$WORK/picked"
run_plugin "$REPO" '{}' 'printf %s "$DEVFLOW_PYTHON" > '"$WORK/picked" PATH="$BIN:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "plugin:自動找直譯器 → 選 python3.13(3.14 版本不足被跳過、3.13 優先於 3.12)" \
  "$([ "$(rc)" = 0 ] && [ "$(cat "$WORK/picked" 2>/dev/null)" = "$BIN/python3.13" ]; echo $?)"
rm -rf "$BIN"; mkdir -p "$BIN/extra"; fake_py "$BIN/extra/python3.12" 3.12
dirty_repo; rm -f "$WORK/picked"
run_plugin "$REPO" '{}' 'printf %s "$DEVFLOW_PYTHON" > '"$WORK/picked" PATH="$TOOLS" DEVFLOW_STOP_PY_DIRS="$BIN/extra"
expect "plugin:PATH 沒有、但在額外目錄(Homebrew 等)→ 找得到" \
  "$([ "$(rc)" = 0 ] && [ "$(cat "$WORK/picked" 2>/dev/null)" = "$BIN/extra/python3.12" ]; echo $?)"
rm -rf "$BIN"; mkdir -p "$BIN"; fake_py "$BIN/python3" 3.12
dirty_repo; rm -f "$WORK/picked"
run_plugin "$REPO" '{}' 'printf %s "$DEVFLOW_PYTHON" > '"$WORK/picked" PATH="$BIN:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "plugin:只有 python3 且是 3.12+ → 也接受" \
  "$([ "$(rc)" = 0 ] && [ "$(cat "$WORK/picked" 2>/dev/null)" = "$BIN/python3" ]; echo $?)"

# P8 找不到 3.12+(macOS 只有 3.9):fail-open、合法 JSON systemMessage、說明版本/怎麼裝/怎麼關,24 小時只提醒一次
rm -rf "$BIN"; mkdir -p "$BIN"; fake_py "$BIN/python3" 3.9; fake_py "$BIN/python3.9" 3.9
dirty_repo
run_plugin "$REPO" '{}' "$SPY; exit 1" PATH="$BIN:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "plugin:只有舊 python3 → exit 0(fail-open)、不跑自測、stderr 空" \
  "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ] && [ ! -s "$WORK/err" ]; echo $?)"
expect "plugin:stdout 是合法 JSON 且 systemMessage 說明 3.12/怎麼裝/DEVFLOW_PYTHON/怎麼關" \
  "$(python3 - "$WORK/out" <<'PY'
import json
import sys

m = json.load(open(sys.argv[1], encoding="utf-8"))["systemMessage"]
need = ("3.12", "brew install", "DEVFLOW_PYTHON", "DEVFLOW_STOP_SELFTEST=off", "disableAllHooks", "24 小時")
sys.exit(0 if all(n in m for n in need) else 1)
PY
echo $?)"
run_plugin "$REPO" '{}' "$SPY; exit 1" PATH="$BIN:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "plugin:24 小時內第二次 → 不再提醒(stdout 空)" "$([ "$(rc)" = 0 ] && [ ! -s "$WORK/out" ]; echo $?)"
dirty_repo
run_plugin "$REPO" '{}' "$SPY; exit 1" DEVFLOW_PYTHON="$WORK/py-old"
expect "plugin:DEVFLOW_PYTHON 明示但不到 3.12 → 不偷換、fail-open 並提醒" \
  "$([ "$(rc)" = 0 ] && [ ! -e "$MARK" ] && grep -q '3.12' "$WORK/out"; echo $?)"

# P9 hooks/hooks.json 掛載形狀 + 可執行位元
python3 - "$HOOKS_JSON" <<'PY'
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
stop = d.get("hooks", {}).get("Stop", [])
ok = (
    len(stop) == 1
    and "matcher" not in stop[0]
    and len(stop[0]["hooks"]) == 1
    and stop[0]["hooks"][0].get("type") == "command"
    and stop[0]["hooks"][0].get("command") == "${CLAUDE_PLUGIN_ROOT}/hooks/devflow-stop-selftest.sh"
    and stop[0]["hooks"][0].get("timeout", 0) >= 300
    and "onFailure" not in json.dumps(stop)
)
sys.exit(0 if ok else 1)
PY
expect "hooks.json Stop 掛載(單一 command、無 matcher、timeout ≥ 300、無 onFailure)" "$?"
expect "hooks/devflow-stop-selftest.sh 有可執行位元" "$([ -x "$PHOOK" ]; echo $?)"

if [ "$TOTAL" -lt "$MIN_CASES" ]; then
  echo "FATAL: 案例數 $TOTAL 低於下限 $MIN_CASES(案例被刪?)" >&2
  exit 2
fi
echo "=== test-stop-selftest-hook:$PASS/$TOTAL ==="
[ "$FAIL" -eq 0 ]
