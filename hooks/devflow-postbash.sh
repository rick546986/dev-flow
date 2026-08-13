#!/bin/bash
# devflow-postbash.sh — PostToolUse(Bash):偵測網。git status(含 ignored)對照 scope,
# 並比對 baseline 內容 hash 與 4-spec hash —— 抓「路徑沒變但內容變」與「經 shell 改契約」。
cat >/dev/null
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
/usr/bin/python3 "$(dirname "$0")/_postbash_impl.py" "$ROOT"
