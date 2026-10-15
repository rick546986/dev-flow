#!/bin/bash
# devflow-stop-selftest.sh — plugin 版 Stop hook:產品專案改完要結束時自動跑 dev-flow 守衛自測
# (hooks/selftest.sh),沒過就擋住結束(exit 2),要求回報。
#
# 與本 repo 自己的 .claude/hooks/run-selftest.sh(掛在 .claude/settings.json)是兩支、分開掛:
# 那支只給母版 repo 的 session 用;這支隨 plugin 的 hooks/hooks.json 發給所有採用專案。
# 同一個專案若已自己掛了 run-selftest.sh(母版 repo 就是),這支讓出、不重複跑。
#
# 官方語意:Stop hook 無 matcher;exit 2 = 讓 Claude 繼續、stderr 當理由;stdin JSON 帶
# stop_hook_active;exit 0 時 stdout 的 JSON systemMessage 會當警告顯示給使用者。
#
# 行為(依序):
#   ① DEVFLOW_STOP_SELFTEST=off(或 0/false/no)→ exit 0。只關這一支的開關;官方的
#      "disableAllHooks": true 會連所有守衛一起關,這是比較不傷的選項。
#   ② stop_hook_active 為 true(已因本 hook 續跑過一輪)→ exit 0,避免無限迴圈。
#   ③ 專案自己的 .claude/settings(.local).json 已提到 run-selftest.sh → exit 0(不重複跑)。
#   ④ 不是 git 工作樹,或工作樹相對 HEAD 無變更(含未追蹤檔)且本分支沒有 origin/main(無則
#      main)以外的 commit → exit 0(純問答不浪費時間)。找不到基準分支 → 保守視為有 commit。
#   ⑤ 節流:同一組「plugin 版本 + 直譯器」在 TTL 內已通過就不再跑。理由:這支自測驗的是
#      dev-flow 守衛與本機環境,結果不隨產品程式碼變動;每個回合都花 30–75 秒重驗,沒有新資訊。
#      TTL 預設 21600 秒(6 小時),DEVFLOW_STOP_SELFTEST_TTL=0 → 每次都跑。只記「通過」,
#      失敗不記。狀態檔放 ${CLAUDE_PLUGIN_DATA:-${XDG_CACHE_HOME:-~/.cache}/dev-flow}/stop-selftest/。
#   ⑥ 找 Python 3.12+(自測內的 doctor printer-python 項釘死 3.12:macOS 系統 python3 是 3.9,
#      只保證語法層,跑自測會紅)。順序:DEVFLOW_PYTHON → python3.15…3.12 → python3;
#      除 PATH 外也找 /opt/homebrew/bin、/usr/local/bin、~/.local/bin(Claude 從 GUI 起時
#      PATH 常不含 Homebrew)。找不到 → **fail-open**:exit 0 並用 systemMessage 說明要哪版、
#      怎麼裝、怎麼關(每 24 小時最多提醒一次)。理由同 devflow-python-lib.sh:環境沒備齊
#      不是這次改動的錯,擋住只會讓 Claude 去試著「裝 Python」。DEVFLOW_PYTHON 明示指定但
#      不到 3.12 時同樣只提醒、不偷換。
#   ⑦ 跑 ${DEVFLOW_STOP_SELFTEST_CMD:-bash <plugin>/hooks/selftest.sh}(DEVFLOW_PYTHON 設為
#      上一步找到的直譯器;不需網路、不讀 secret、不動專案檔)。失敗 → 尾 40 行 + 提示
#      印 stderr、exit 2;成功 exit 0。
#
# 測試:scripts/test-stop-selftest-hook.sh(用 DEVFLOW_STOP_SELFTEST_CMD 替身,不跑真自測)。

set -uo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)

INPUT=""
if [ ! -t 0 ]; then
  INPUT=$(cat)
fi

case "${DEVFLOW_STOP_SELFTEST:-}" in
  off|OFF|0|false|no) exit 0 ;;
esac

if printf '%s' "$INPUT" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

PROJECT=${CLAUDE_PROJECT_DIR:-$PWD}
cd "$PROJECT" || exit 0

if grep -qs 'run-selftest\.sh' .claude/settings.json .claude/settings.local.json; then
  exit 0
fi

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

STATE_DIR="${CLAUDE_PLUGIN_DATA:-${XDG_CACHE_HOME:-${HOME:-/tmp}/.cache}/dev-flow}/stop-selftest"
NOW=$(date +%s)

stamp_age() {  # stamp_age <檔>:印距上次寫入的秒數;檔不存在或內容壞 → 印很大的數
  local last
  last=$(cat "$1" 2>/dev/null || true)
  case "$last" in ''|*[!0-9]*) echo 999999999; return ;; esac
  echo $((NOW - last))
}
stamp_write() {  # stamp_write <檔>:寫不進去就算了(節流是優化,不是正確性)
  mkdir -p "$STATE_DIR" 2>/dev/null && printf '%s\n' "$NOW" >"$1" 2>/dev/null || true
}

py_ok() {  # py_ok <exe>:是 3.12+ 的可執行直譯器
  [ -n "$1" ] && [ -x "$1" ] \
    && "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' >/dev/null 2>&1
}
find_py() {
  local v c d
  if [ -n "${DEVFLOW_PYTHON:-}" ]; then
    py_ok "$DEVFLOW_PYTHON" && { echo "$DEVFLOW_PYTHON"; return 0; }
    return 1
  fi
  for v in 3.15 3.14 3.13 3.12; do
    c=$(command -v "python$v" 2>/dev/null || true)
    py_ok "$c" && { echo "$c"; return 0; }
    for d in ${DEVFLOW_STOP_PY_DIRS-/opt/homebrew/bin /usr/local/bin ${HOME:-/nonexistent}/.local/bin}; do
      py_ok "$d/python$v" && { echo "$d/python$v"; return 0; }
    done
  done
  c=$(command -v python3 2>/dev/null || true)
  py_ok "$c" && { echo "$c"; return 0; }
  return 1
}

PY=$(find_py) || {
  if [ "$(stamp_age "$STATE_DIR/no-python")" -ge 86400 ]; then
    stamp_write "$STATE_DIR/no-python"
    # 組成 JSON 字串:換行寫成 \n、內文雙引號寫成 \",其餘不含需跳脫字元。
    MSG='dev-flow Stop 自測已略過:找不到 Python 3.12 以上的直譯器(自測內的 printer-python 檢查要 3.12+;macOS 系統內建 python3 是 3.9,只保證語法可解析,跑不了)。'
    MSG="$MSG"'\n安裝其一:brew install python@3.12 / uv python install 3.12 / 從 python.org 下載。裝好後若不在 PATH,設環境變數 DEVFLOW_PYTHON 指向它(例如 /opt/homebrew/bin/python3.12)。'
    MSG="$MSG"'\n不想要這個自測:DEVFLOW_STOP_SELFTEST=off 只關這一支;settings 的 \"disableAllHooks\": true 會連所有 dev-flow 守衛一起關。'
    MSG="$MSG"'\n這個提醒 24 小時內只出現一次,本次不擋結束。'
    printf '{"systemMessage": "%s"}\n' "$MSG"
  fi
  exit 0
}

VERSION=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$HERE/../.claude-plugin/plugin.json" 2>/dev/null | head -n 1)
PYVER=$("$PY" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || echo "?")
KEY=$(printf '%s|%s|%s|%s' "$VERSION" "$PY" "$PYVER" "$HERE" | cksum | cut -d' ' -f1)
TTL=${DEVFLOW_STOP_SELFTEST_TTL:-21600}
case "$TTL" in ''|*[!0-9]*) TTL=21600 ;; esac
if [ "$TTL" -gt 0 ] && [ "$(stamp_age "$STATE_DIR/pass-$KEY")" -lt "$TTL" ]; then
  exit 0
fi

OUT=$(mktemp "${TMPDIR:-/tmp}/devflow-stop-selftest.XXXXXX") || exit 0
trap 'rm -f "$OUT"' EXIT

CMD=${DEVFLOW_STOP_SELFTEST_CMD:-bash "$HERE/selftest.sh"}
if DEVFLOW_PYTHON="$PY" bash -c "$CMD" >"$OUT" 2>&1; then
  stamp_write "$STATE_DIR/pass-$KEY"
  exit 0
fi

{
  tail -n 40 "$OUT"
  echo "dev-flow 守衛自測未過(上面是輸出尾 40 行;直譯器 $PY $PYVER)。"
  echo "這是 dev-flow plugin 或本機環境的問題,不是你剛改的產品程式:請把輸出回報給使用者,不要去改 plugin 檔案。"
  echo "使用者要暫時關掉:DEVFLOW_STOP_SELFTEST=off(只關這一支),或 settings 的 \"disableAllHooks\": true(全關)。"
} >&2
exit 2
