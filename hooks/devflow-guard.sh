#!/bin/bash
# devflow-guard.sh — PreToolUse(Edit|Write|Read):執行期契約防篡改 + 圍欄② + scope 硬擋。
# fail-CLOSED:sentinel 武裝中而旗標壞/消失 → 擋。未武裝 → 靜默放行。
HOOK_INPUT=$(cat); export HOOK_INPUT
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
/usr/bin/python3 "$(dirname "$0")/_guard_impl.py" "$ROOT"
