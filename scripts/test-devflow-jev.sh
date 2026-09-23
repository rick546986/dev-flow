#!/bin/bash
# test-devflow-jev.sh — jev-gate 七組守衛 foundation 的牙(roadmap W1:P1-G1～G7)。
#
# 跑 scripts/devflow_jev/test_guards.py(unittest,stdlib only)。全部負面 fixtures 住
# scripts/fixtures/devflow-jev/。本檔同時釘三件事:
#   ① 套件內不得 import 任何網路模組(urllib/http.client/socket/requests)—— W1 只有 fake transport;
#   ② repo 內不得存在 scripts/devflow-jev.py(roadmap §0 第 2 條:七守衛全綠前不寫 runtime,shadow 也算)
#      —— 這條在 W2 P1-F1 落地時由那次 PR 明改本檔,不是靜默放行;
#   ③ 測試案例數地板(同 repo 慣例:等於當下實際數,不抓大概)。
#
# 用法:bash scripts/test-devflow-jev.sh [root]
# exit:0 = 全過 / 1 = 任一守衛牙紅 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi
PKG="$ROOT/scripts/devflow_jev"
[ -d "$PKG" ] || { echo "FATAL: 找不到 $PKG" >&2; exit 2; }
[ -f "$PKG/test_guards.py" ] || { echo "FATAL: 找不到 $PKG/test_guards.py" >&2; exit 2; }

echo "-- ① 零網路 import --"
if grep -nE '^\s*(import|from)\s+(urllib|http\.client|http\b|socket|requests|ssl)\b' "$PKG"/*.py; then
  echo "⛔ devflow_jev 內出現網路模組 import —— W1 只准 fake transport" >&2; exit 1
fi
echo "  ✓ scripts/devflow_jev/*.py 不 import 網路模組"

echo "-- ② runtime 尚不得存在 --"
if [ -e "$ROOT/scripts/devflow-jev.py" ]; then
  echo "⛔ scripts/devflow-jev.py 已存在 —— roadmap §0 第 2 條:七組守衛負面測試全綠前不准寫 runtime(含 shadow)。" >&2
  echo "   W2 P1-F1 落地時請在同一 PR 明改本檔這條,不得靜默放行。" >&2; exit 1
fi
echo "  ✓ scripts/devflow-jev.py 不存在"

echo "-- ③ 案例數地板 --"
MIN_TESTS=127
ACTUAL=$(grep -cE '^\s+def test_' "$PKG/test_guards.py")
if [ "$ACTUAL" -lt "$MIN_TESTS" ]; then
  echo "⛔ test_guards.py 只有 $ACTUAL 個 test_(地板 $MIN_TESTS)—— 案例被刪" >&2; exit 1
fi
echo "  ✓ test_ 定義 $ACTUAL 個(地板 $MIN_TESTS)"

echo "-- ④ unittest --"
cd "$ROOT" || exit 2
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/devflow_jev -t scripts -p 'test_*.py' 2>&1 | grep -vE '^(ok|\.+)$' | tail -25
RC=${PIPESTATUS[0]}
find "$PKG" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
if [ "$RC" -ne 0 ]; then
  echo "⛔ devflow_jev unittest 紅(exit $RC)" >&2; exit 1
fi
echo "✅ test-devflow-jev: 七組守衛 foundation 牙全過(W1;不是 runtime、不是 production-ready)"
