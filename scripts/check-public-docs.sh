#!/bin/bash
# adr / HISTORY 人頁過期守衛(Repo-local)。
#
# md 是 git 正本。html 是衍生檔。新增 ADR 或往 HISTORY 追加之後,
# 必須跑 `python3 scripts/build-public-docs.py` 重生,不能手改 html。
#
# 本守衛把「html 跟 md 標題/條目同步」變成機械檢查:
#   重生到記憶裡,跟現檔逐位元組比。差一點就紅。
#
# 用法:
#   scripts/check-public-docs.sh [root]
# exit:0 = 全過 / 1 = 過期或缺檔 / 2 = 環境問題
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

BUILD="$SELF_DIR/build-public-docs.py"
if [ ! -f "$BUILD" ]; then
  echo "⛔ 找不到 $BUILD" >&2
  exit 2
fi

python3 "$BUILD" --root "$ROOT" --check
exit $?
