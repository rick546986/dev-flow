#!/bin/bash
# test-stop-selftest-hook.sh — .claude/hooks/run-selftest.sh(Claude Code Stop hook)的行為牙。
#
# 咬什麼:Stop hook 改完自動跑 selftest,沒過擋住結束。三個必守情境 + 周邊:
#   ① stop_hook_active=true → exit 0(就算有變更、selftest 會紅也不得再擋 = 防無限迴圈)
#   ② 無變更且本分支沒有 main 以外的 commit → exit 0,且 selftest 指令根本沒被呼叫
#   ③ selftest 失敗 → exit 2,stderr 有「selftest 未過,請修到全綠再結束」與尾 40 行
#   周邊:成功 → exit 0 且不印東西;分支領先 main(工作樹乾淨)也要跑;未追蹤檔算變更;
#   .claude/settings.json 的 Stop 掛載用官方 exec form、timeout 600、沒有官方說對 Stop
#   無效的 onFailure、既有 permissions.allow 還在。
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
[ -f "$HOOK" ] || { echo "FATAL: 找不到 $HOOK" >&2; exit 2; }
[ -f "$SETTINGS" ] || { echo "FATAL: 找不到 $SETTINGS" >&2; exit 2; }
command -v git >/dev/null 2>&1 || { echo "FATAL: 需要 git" >&2; exit 2; }

MIN_CASES=12
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

mkrepo() {  # mkrepo <dir>:建一個 main 上有一個 commit 的假專案
  rm -rf "$1" && mkdir -p "$1"
  (
    cd "$1" || exit 1
    git init -q -b main . \
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

if [ "$TOTAL" -lt "$MIN_CASES" ]; then
  echo "FATAL: 案例數 $TOTAL 低於下限 $MIN_CASES(案例被刪?)" >&2
  exit 2
fi
echo "=== test-stop-selftest-hook:$PASS/$TOTAL ==="
[ "$FAIL" -eq 0 ]
