#!/bin/bash
# devflow-prebash.sh — PreToolUse(Bash):擋掉 shell 繞過的兩類動作 ——
# ①讀上游討論檔(圍欄②的 Bash 破口)②破壞守衛狀態(rm 旗標 / 直寫 exec.json)。
# 治標不治本(shell 語意無法窮舉),但堵掉隨手可為的低成本繞過。
HOOK_INPUT=$(cat); export HOOK_INPUT
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
/usr/bin/python3 "$(dirname "$0")/_prebash_impl.py" "$ROOT"
