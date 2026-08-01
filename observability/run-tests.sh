#!/usr/bin/env bash
# observability 測試 runner:禁落 .pyc(防編譯產物進 tree,Finding C-1)。
# 用法:bash observability/run-tests.sh [unittest discover 額外引數]
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONDONTWRITEBYTECODE=1 exec python3 -m unittest discover -s observability/tests "$@"
