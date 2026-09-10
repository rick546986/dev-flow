#!/bin/bash
# test-host-receipt.sh — host-stack-fit 收據鑄／核對牙
#
# 群組:
#   mint-stage4        T-1  S-1.1(stage4)／S-1.2／S-1.3／S-1.4
#   mint-rest          T-2  其餘六站 allow 鑄檔
#   verify-receipt     T-3  verify_receipt:true
#   fail-closed-claim  T-4  start-only 與主機文案
#
# 用法:
#   scripts/test-host-receipt.sh [--group NAME] [-v] [root]
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

STAGE4="$SELF_DIR/check-devstage4-graph.sh"
PROBE="$SELF_DIR/check-host-adapter.sh"
SCOPE="$SELF_DIR/check-write-scope.sh"
EXEC="$ROOT/hooks/devflow-exec.sh"
FIX="$SELF_DIR/fixtures/host-receipt"
GOOD4="$SELF_DIR/fixtures/devstage4-graph/good"
[ -x "$STAGE4" ] || chmod +x "$STAGE4"
[ -f "$STAGE4" ] || { echo "FATAL: 找不到 $STAGE4" >&2; exit 2; }
[ -d "$FIX/actions" ] || { echo "FATAL: 找不到 $FIX/actions" >&2; exit 2; }
[ -f "$FIX/run_cases.py" ] || { echo "FATAL: 找不到 $FIX/run_cases.py" >&2; exit 2; }
[ -d "$GOOD4" ] || { echo "FATAL: 找不到 $GOOD4" >&2; exit 2; }

python3 "$FIX/run_cases.py" "$ROOT" "$STAGE4" "$PROBE" "$SCOPE" "$EXEC" "$FIX" "$GOOD4" "$GROUP" "$VERBOSE"
