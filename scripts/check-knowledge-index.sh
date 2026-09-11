#!/bin/bash
# Knowledge index freshness guard (#155 Pilot-2).
#
# Machine truth: docs/knowledge/index.yaml
# Human projection: docs/knowledge/index.md (must be regenerated, never hand-edited).
#
# 用法:
#   scripts/check-knowledge-index.sh [root]
# exit:0 = 全過 / 1 = 過期或缺檔 / 2 = 環境問題
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

BUILD="$SELF_DIR/build-knowledge-index.py"
if [ ! -f "$BUILD" ]; then
  echo "⛔ 找不到 $BUILD" >&2
  exit 2
fi

python3 "$BUILD" --root "$ROOT" --check
exit $?
