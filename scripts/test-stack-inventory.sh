#!/bin/bash
# test-stack-inventory.sh — I2／I4 堆疊盤點牙
#
#   i2  T-5  S-3.1..S-3.5／S-5.1
#   i4  T-6  S-4.1..S-4.3
#
# 用法: scripts/test-stack-inventory.sh [--group NAME] [-v] [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
GROUP=""
VERBOSE=0
POSITIONAL=()
while [ $# -gt 0 ]; do
  case "$1" in
    --group)
      GROUP=${2:-}
      [ -n "$GROUP" ] || { echo "FATAL: --group 需要名稱" >&2; exit 2; }
      shift 2
      ;;
    -v|--verbose) VERBOSE=1; shift ;;
    -*) echo "FATAL: 未知旗標 $1" >&2; exit 2 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done
if [ "${#POSITIONAL[@]}" -gt 0 ]; then
  ROOT=$(cd "${POSITIONAL[0]}" && pwd) || exit 2
fi

WRITER="$SELF_DIR/write-stack-inventory.py"
FIX="$SELF_DIR/fixtures/stack-inventory"
[ -f "$WRITER" ] || { echo "FATAL: 找不到 $WRITER" >&2; exit 2; }
[ -d "$FIX" ] || { echo "FATAL: 找不到 $FIX" >&2; exit 2; }
[ -f "$FIX/run_cases.py" ] || { echo "FATAL: 找不到 $FIX/run_cases.py" >&2; exit 2; }

python3 "$FIX/run_cases.py" "$ROOT" "$WRITER" "$FIX" "$GROUP" "$VERBOSE"
