#!/bin/bash
# devflow-postbash.sh — PostToolUse(Bash):偵測網。git status(含 ignored)對照 scope,
# 並比對 baseline 內容 hash 與 4-spec hash —— 抓「路徑沒變但內容變」與「經 shell 改契約」。
# ⚠️ payload 走 stdin 直通 python(F2 同型對齊:impl 從 stdin 取 session_id 記 obs,
# 舊版 `cat >/dev/null` 丟棄輸入,session_ref 永遠帶不上;env 傳遞則撞 ARG_MAX)。
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
exec /usr/bin/python3 "$(dirname "$0")/_postbash_impl.py" "$ROOT"
