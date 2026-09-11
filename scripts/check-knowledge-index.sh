#!/bin/bash
# Knowledge index freshness guard (#155 Pilot-2 + knife-2 bootstrap).
#
# Machine truth: docs/knowledge/index.yaml
# Human projection: docs/knowledge/index.md (must be regenerated, never hand-edited).
# Conflict queue: docs/knowledge/conflicts-queue.yaml (human resolve; never auto-pick).
#
# Prefer bootstrap --check (covers index + twin + queue). Falls back to generator
# --check only if bootstrap script is absent (should not happen on this pack).
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

BOOT="$SELF_DIR/bootstrap-knowledge-index.py"
BUILD="$SELF_DIR/build-knowledge-index.py"

if [ -f "$BOOT" ]; then
  python3 "$BOOT" --root "$ROOT" --check
  exit $?
fi

if [ ! -f "$BUILD" ]; then
  echo "⛔ 找不到 $BOOT 與 $BUILD" >&2
  exit 2
fi

python3 "$BUILD" --root "$ROOT" --check
exit $?
