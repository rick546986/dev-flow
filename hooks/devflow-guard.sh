#!/bin/bash
# devflow-guard.sh — PreToolUse(Edit|Write|Read):執行期契約防篡改 + 圍欄② + scope 硬擋。
# fail-CLOSED:sentinel 武裝中而旗標壞/消失 → 擋。未武裝 → 靜默放行。
# ⚠️ payload 一律走 stdin 直通 python,殼層不碰內容(F2,2026-08-17):曾用
# `HOOK_INPUT=$(cat); export HOOK_INPUT`,>1MB payload 令其後每個 exec 撞 ARG_MAX
# → rc=126,fail-closed 靜默自壞等同放行。同型四支殼(guard/prebash/postbash/
# dispatch-guard)一起改;讀取正本 = devflow-lib.py read_hook_input()。
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
. "$(dirname "$0")/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)
exec "$DEVFLOW_PY" "$(dirname "$0")/_guard_impl.py" "$ROOT"
