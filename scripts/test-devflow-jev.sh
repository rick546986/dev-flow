#!/bin/bash
# test-devflow-jev.sh — G2 自動審查上線(G2R 分流 + g2-misrelease)的牙。
#
# main 上只有 research/jev-supermemory W9/W10 搬過來的 G2 部分;J1–J5 runtime 不在 main。
# 跑 scripts/devflow_jev/test_*.py(unittest,stdlib only;Jev 一律 FakeTransport,零外部網路)。本檔同時釘:
#   ① 網路 import 白名單:套件內**只有** scripts/devflow_jev/http_transport.py 准 import urllib/socket;
#      其餘模組與 scripts/devflow-jev.py 本身零網路 import(test_*.py 不掃)。
#   ② runtime 存在、可執行、三個 live 開關寫死 False;未設 key 的 g2r → exit 0、route=HUMAN、零網路、不寫 .dev-flow/。
#   ③ key + opt-in(mode: live)但 endpoint 是 loopback 閉埠 → 仍 exit 0、route=HUMAN(Jev 失敗 = 交給人審),key 不外露。
#   ④ 測試案例數地板(同 repo 慣例:等於當下實際數)。
#   ⑤ unittest 全過。
#
# 用法:bash scripts/test-devflow-jev.sh [root]
# exit:0 = 全過 / 1 = 任一牙紅 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi
PKG="$ROOT/scripts/devflow_jev"
RUNTIME="$ROOT/scripts/devflow-jev.py"
[ -d "$PKG" ] || { echo "FATAL: 找不到 $PKG" >&2; exit 2; }
[ -f "$PKG/test_g2.py" ] || { echo "FATAL: 找不到 $PKG/test_g2.py" >&2; exit 2; }
NET_RE='^\s*(import\s+([A-Za-z_][A-Za-z0-9_.]*\s*,\s*)*|from\s+)(urllib|http|socket|requests|ssl)\b|(__import__|import_module)\(\s*["'"'"'](urllib|http|socket|requests|ssl)'

echo "-- ① 網路 import 白名單(只准 http_transport.py)--"
OFFEND=$(grep -lE "$NET_RE" "$PKG"/*.py "$RUNTIME" 2>/dev/null | grep -vE '/(http_transport|test_[a-z_]+)\.py$' || true)
if [ -n "$OFFEND" ]; then
  echo "⛔ 白名單外的檔 import 網路模組:" >&2; echo "$OFFEND" >&2; exit 1
fi
grep -qE "$NET_RE" "$PKG/http_transport.py" || { echo "⛔ http_transport.py 反而沒有網路 import —— 白名單失義" >&2; exit 1; }
echo "  ✓ 只有 scripts/devflow_jev/http_transport.py import 網路模組;runtime 本身零網路 import"

echo "-- ② runtime 存在、可執行、live 開關寫死 False、off 路徑零網路 --"
[ -f "$RUNTIME" ] || { echo "⛔ scripts/devflow-jev.py 不存在" >&2; exit 1; }
[ -x "$RUNTIME" ] || { echo "⛔ scripts/devflow-jev.py 不可執行(ship-manifest mode 755)" >&2; exit 1; }
grep -qE '^GRADUATED = False\b' "$RUNTIME" || { echo "⛔ runtime 的 GRADUATED 不是寫死 False" >&2; exit 1; }
grep -qE '^J5_LIVE_RATIFIED = False\b' "$PKG/gate.py" || { echo "⛔ gate.J5_LIVE_RATIFIED 不是寫死 False" >&2; exit 1; }
grep -qE '^J2_WINDOW_RATIFIED = False\b' "$PKG/policy.py" || { echo "⛔ policy.J2_WINDOW_RATIFIED 不是寫死 False" >&2; exit 1; }
T=$(mktemp -d 2>/dev/null || mktemp -d -t jevrt)
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/docs/dev/s"
cp "$ROOT/example/contract-expiry-reminder/4-spec.md" "$T/docs/dev/s/4-spec.md"
OUT=$(cd "$T" && env -u TYPESAFE_API_KEY DEVFLOW_PLUGIN="$ROOT" PYTHONDONTWRITEBYTECODE=1 \
      python3 "$RUNTIME" --root "$T" g2r --slug s 2>&1); RC=$?
if [ "$RC" -ne 0 ] || ! grep -q '"jev_unavailable:no_api_key"' <<<"$OUT" || ! grep -q '"route": "HUMAN"' <<<"$OUT" \
   || ! grep -q '"network": false' <<<"$OUT" || [ -e "$T/.dev-flow" ]; then
  echo "⛔ 未設 key 的 g2r 應 exit 0 + HUMAN + no_api_key + 零網路;實得 rc=$RC" >&2; echo "$OUT" | head -20 >&2; exit 1
fi
echo "  ✓ 未設 key → exit 0、route=HUMAN(jev_unavailable:no_api_key)、零網路"

echo "-- ③ key + opt-in 但 endpoint 是 loopback 閉埠 → HUMAN、不 crash --"
mkdir -p "$T/.dev-flow" && printf 'mode: live\n' > "$T/.dev-flow/jev.yaml"
OUT=$(cd "$T" && env -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u all_proxy -u ALL_PROXY \
      no_proxy="127.0.0.1,localhost" TYPESAFE_API_KEY=not-a-real-key DEVFLOW_JEV_ENDPOINT="http://127.0.0.1:9/" \
      DEVFLOW_PLUGIN="$ROOT" PYTHONDONTWRITEBYTECODE=1 python3 "$RUNTIME" --root "$T" g2r --slug s 2>&1); RC=$?
if [ "$RC" -ne 0 ] || ! grep -qE '"jev_unavailable:transport:(network|timeout)"' <<<"$OUT" \
   || ! grep -q '"route": "HUMAN"' <<<"$OUT"; then
  echo "⛔ 閉埠 endpoint 的 g2r 應 exit 0 + transport:network/timeout + HUMAN;實得 rc=$RC" >&2; echo "$OUT" | head -30 >&2; exit 1
fi
grep -q "not-a-real-key" <<<"$OUT" && { echo "⛔ key 出現在輸出" >&2; exit 1; }
echo "  ✓ transport 失敗 → exit 0、route=HUMAN、key 不外露"

echo "-- ④ 案例數地板 --"
MIN_TESTS=96
ACTUAL=$(cat "$PKG"/test_*.py | grep -cE '^\s+def test_')
if [ "$ACTUAL" -lt "$MIN_TESTS" ]; then
  echo "⛔ test_*.py 只有 $ACTUAL 個 test_(地板 $MIN_TESTS)—— 案例被刪" >&2; exit 1
fi
echo "  ✓ test_ 定義 $ACTUAL 個(地板 $MIN_TESTS)"

echo "-- ⑤ unittest --"
cd "$ROOT" || exit 2
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/devflow_jev -t scripts -p 'test_*.py' 2>&1 \
  | grep -vE '^(ok|\.+)$' | tail -25
RC=${PIPESTATUS[0]}
find "$PKG" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
if [ "$RC" -ne 0 ]; then
  echo "⛔ devflow_jev unittest 紅(exit $RC)" >&2; exit 1
fi
echo "✅ test-devflow-jev: G2R 分流 + G2 自動放行 + g2-misrelease 牙全過(Jev 只分流、不寫 verdict;Jev 不在 = 人審)"
