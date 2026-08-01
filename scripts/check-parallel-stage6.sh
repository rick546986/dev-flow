#!/bin/bash
# parallel-stage6 契約檢查(Workstream A):模板選配欄位 + 設計文件契約錨 + 可執行契約行為。
# 獨立於 check-methodology-corrections.sh(74 條基線不動);plugin runtime 落地時必須
# 通過同一組 tests/parallel-stage6/fixtures/。
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
exec python3 "$ROOT/tests/parallel-stage6/run_tests.py" "$ROOT"
