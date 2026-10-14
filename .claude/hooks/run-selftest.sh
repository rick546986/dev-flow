#!/bin/bash
# Claude Code Stop hook:改完要結束時自動跑 selftest,沒過就擋住結束(exit 2)。
#
# 掛載在 .claude/settings.json 的 hooks.Stop(本專案自己的 session 用;與外掛自帶的
# hooks/hooks.json 無關,兩者分開)。官方語意:Stop hook 無 matcher;exit 2 = 讓 Claude
# 繼續工作、stderr 當理由;stdin JSON 帶 stop_hook_active。
#
# 行為:
#   ① stop_hook_active 為 true(已經因本 hook 續跑過一輪)→ exit 0,避免無限迴圈。
#   ② 工作樹相對 HEAD 無變更(含未追蹤檔),且本分支沒有 origin/main(無則 main)以外的
#      commit → exit 0(純問答不浪費時間)。找不到 origin/main 也找不到 main → 無從比對,
#      保守視為「有 commit」,照跑。
#   ③ 否則跑 ${DEVFLOW_STOP_SELFTEST_CMD:-bash hooks/selftest.sh}(在專案根目錄、
#      不需網路、不讀 secret)。失敗 → 尾 40 行 + 提示印 stderr、exit 2;成功 exit 0。
#
# 暫時關閉:官方只有 "disableAllHooks": true(可放 .claude/settings.local.json)或
# claude --settings '{"disableAllHooks": true}',沒有只關單一 hook 的開關。
#
# 解析 JSON 不假設有 jq / python3:只比對 stop_hook_active 這個布林欄位。

set -uo pipefail

INPUT=""
if [ ! -t 0 ]; then
  INPUT=$(cat)
fi

if printf '%s' "$INPUT" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$PWD}" || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

DIRTY=$(git status --porcelain 2>/dev/null)

AHEAD=1
BASE=""
for ref in origin/main main; do
  if git rev-parse --verify --quiet "refs/remotes/$ref" >/dev/null 2>&1 \
     || git rev-parse --verify --quiet "refs/heads/$ref" >/dev/null 2>&1; then
    BASE=$ref
    break
  fi
done
if [ -n "$BASE" ]; then
  AHEAD=$(git rev-list --count "$BASE..HEAD" 2>/dev/null || echo 1)
fi

if [ -z "$DIRTY" ] && [ "$AHEAD" = "0" ]; then
  exit 0
fi

OUT=$(mktemp "${TMPDIR:-/tmp}/devflow-stop-selftest.XXXXXX") || exit 0
trap 'rm -f "$OUT"' EXIT

CMD=${DEVFLOW_STOP_SELFTEST_CMD:-bash hooks/selftest.sh}
if bash -c "$CMD" >"$OUT" 2>&1; then
  exit 0
fi

{
  tail -n 40 "$OUT"
  echo "selftest 未過，請修到全綠再結束"
} >&2
exit 2
