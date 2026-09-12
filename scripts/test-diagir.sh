#!/bin/bash
# test-diagir.sh — diagram-ir-gate 閘／路由／Lab／範圍牙
#
# 群組:
#   validate       T-1  S-1.1..S-1.6
#   deliver        T-2  S-2.1／S-2.2
#   wire           T-3  S-2.3
#   route          T-4  S-3.1..S-3.5
#   lab            T-5  S-4.1..S-4.5
#   static-scope   T-6  S-5.1／S-5.2
#
# 用法:
#   scripts/test-diagir.sh [--group NAME] [-v] [root]
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
    -v|--verbose)
      VERBOSE=1
      shift
      ;;
    --)
      shift
      POSITIONAL+=("$@")
      break
      ;;
    -*)
      echo "FATAL: 未知旗標 $1" >&2
      exit 2
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done
if [ "${#POSITIONAL[@]}" -gt 0 ]; then
  ROOT=$(cd "${POSITIONAL[0]}" && pwd) || exit 2
fi

GATE="$SELF_DIR/diagir.py"
FIX="$SELF_DIR/fixtures/diagir"
RUNNER="$FIX/run_cases.py"
[ -f "$GATE" ] || { echo "FATAL: 找不到 $GATE" >&2; exit 2; }
[ -f "$RUNNER" ] || { echo "FATAL: 找不到 $RUNNER" >&2; exit 2; }

python3 "$RUNNER" "$ROOT" "$GROUP" "$VERBOSE"
