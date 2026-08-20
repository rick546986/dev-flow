#!/usr/bin/env bash
# memory(Agent Memory v3)測試 runner:禁落 .pyc(防編譯產物進 tree,同
# observability/run-tests.sh 的理由 —— Finding C-1)。
#
# 用法:bash memory/run-tests.sh [unittest discover 額外引數]
#
# 測試一律在 mktemp 的假 repo + AGENTMEM_HOME 裡跑,不碰使用者真實的
# ~/.agentmem/ 與本 repo 的 .dev-flow/(memtools.py 的 MemoryCase 負責隔離)。
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONDONTWRITEBYTECODE=1 exec python3 -m unittest discover -s memory/tests "$@"
