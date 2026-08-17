#!/bin/bash
# devflow-dispatch-guard.sh — PreToolUse(Task|Agent):窄版「首派即最高階」攔截 + 一次性豁免。
# fail-OPEN by design(與 devflow-guard.sh 的 fail-closed 不同):未武裝或 schema
# 對不上已知版本 → 放行,不擋非 dev-flow 的一般派工;只在 exec-v2/exec-v3 武裝中
# 且顯式指定最高階模型時才審。
# ⚠️ payload 走 stdin 直通 python,殼層不碰內容(F2:env 傳遞撞 ARG_MAX → rc=126
# 靜默自壞;見 devflow-guard.sh 同註與 devflow-lib.py read_hook_input())。
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
exec /usr/bin/python3 "$(dirname "$0")/_dispatch_impl.py" "$ROOT"
