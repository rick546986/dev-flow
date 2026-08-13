#!/bin/bash
# devflow-obs.sh — dev-flow 觀測面 CLI(P3):事件落盤唯一合法通道 + ledger 工具。
# 事件經 stdin 吃 JSON、自行解析 run 路徑 —— 命令列不鋪 .devflow/ 路徑(prebash 會攔)。
# 子命令:event / hook-event / context-manifest / validate / derive / stats / recommend /
#         archive / retention status|prune [--dry-run] / ledger-home / registry validate
# retention 僅手動執行;禁背景自動刪除服務(OC-5)。
set -u
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
HERE=$(cd "$(dirname "$0")" && pwd)
CMD="${1:-help}"
if [ "$CMD" = "help" ]; then
  echo "用法: devflow-obs.sh event [slug] | hook-event | context-manifest <att> |"
  echo "      validate [--strict] [run_id ...] | derive [run_id ...] |"
  echo "      stats/recommend [--run-id R]... [--legacy-md F]... [--min-n N] [--threshold X] |"
  echo "      archive [run_id] | retention status|prune [--dry-run] | ledger-home |"
  echo "      registry validate [path]"
  exit 0
fi
shift
PYTHONDONTWRITEBYTECODE=1 exec /usr/bin/python3 "$HERE/_obs_impl.py" "$CMD" "$ROOT" "$@"
