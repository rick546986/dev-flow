#!/bin/bash
# F1 牙入口：讀 fixture／annex／本 slug 文檔。紅則 exit 1。
# 用法:
#   scripts/check-five-station-f1.sh <path>
#   scripts/check-five-station-f1.sh --live
set -uo pipefail
SELF=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF/.." && pwd)
exec python3 "$SELF/five_station_f1.py" --root "$ROOT" "$@"
