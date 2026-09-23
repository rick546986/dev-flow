#!/bin/bash
# test-devflow-jev.sh — jev-gate 七組守衛 foundation(W1:P1-G1～G7)+ stdlib runtime(W2:P1-F1/F5/F6)的牙。
#
# 跑 scripts/devflow_jev/test_*.py(unittest,stdlib only;負面 fixtures 住 scripts/fixtures/devflow-jev/)。
# 本檔同時釘五件事。①② 是 W1 的 tripwire,**2026-09-23 W2 PR 明改**(owner 前提 ②:不得靜默放行;
# 裁決見 docs/dev/jev-gate/owner-decisions-pending.md §0 D、roadmap §0 第 2/11 條):
#   ① 網路 import 白名單:套件內**只有** scripts/devflow_jev/http_transport.py 准 import urllib/socket;
#      其餘模組與 scripts/devflow-jev.py 本身仍零網路 import(W1 原文:「套件內不得 import 任何網路模組」)。
#      test_*.py 不掃(測試造假錯誤要 import urllib.error;測試只打假 opener 與 loopback 閉埠,零外部網路)。
#   ② runtime 必須存在且可執行:scripts/devflow-jev.py(W1 原文:「repo 內不得存在 scripts/devflow-jev.py」;
#      七守衛 127 案於 W1 全綠後,W2 落地);並實跑雙閘門 off 路徑:未設 key → exit 0、零網路、不落盤。
#   ③ 測試案例數地板(同 repo 慣例:等於當下實際數,不抓大概;涵蓋 test_guards/test_runtime/test_http_transport)。
#   ④ unittest 全過。
#   ⑤ 有 key + opt-in 但 endpoint 是 loopback 閉埠 → 仍 exit 0(transport 失敗 = no-op,G2),不 crash、不外連。
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
RUNTIME="$ROOT/scripts/devflow-jev.py"
[ -d "$PKG" ] || { echo "FATAL: 找不到 $PKG" >&2; exit 2; }
[ -f "$PKG/test_guards.py" ] || { echo "FATAL: 找不到 $PKG/test_guards.py" >&2; exit 2; }
[ -f "$PKG/test_runtime.py" ] || { echo "FATAL: 找不到 $PKG/test_runtime.py" >&2; exit 2; }
# 也抓 `import os, socket`(逗號串)與 `__import__("socket")`／`import_module("urllib.request")`
NET_RE='^\s*(import\s+([A-Za-z_][A-Za-z0-9_.]*\s*,\s*)*|from\s+)(urllib|http|socket|requests|ssl)\b|(__import__|import_module)\(\s*["'"'"'](urllib|http|socket|requests|ssl)'

echo "-- ① 網路 import 白名單(只准 http_transport.py)--"
# test_*.py 不在掃描內(test_http_transport.py 要 import urllib.error 造假錯誤;測試本身只用假 opener 與 loopback 閉埠)
OFFEND=$(grep -lE "$NET_RE" "$PKG"/*.py "$RUNTIME" 2>/dev/null | grep -vE '/(http_transport|test_[a-z_]+)\.py$' || true)
if [ -n "$OFFEND" ]; then
  echo "⛔ 白名單外的檔 import 網路模組:" >&2; echo "$OFFEND" >&2
  echo "   W2 只放行 scripts/devflow_jev/http_transport.py 一支;runtime 與其它模組仍零網路。" >&2; exit 1
fi
grep -qE "$NET_RE" "$PKG/http_transport.py" || { echo "⛔ http_transport.py 反而沒有網路 import —— 白名單失義" >&2; exit 1; }
echo "  ✓ 只有 scripts/devflow_jev/http_transport.py import 網路模組;runtime 本身零網路 import"

echo "-- ② runtime 存在、可執行、off 路徑零網路 --"
if [ ! -f "$RUNTIME" ]; then
  echo "⛔ scripts/devflow-jev.py 不存在 —— W2 P1-F1 已落地(2026-09-23),runtime 是散發面的一部分。" >&2; exit 1
fi
[ -x "$RUNTIME" ] || { echo "⛔ scripts/devflow-jev.py 不可執行(ship-manifest mode 755)" >&2; exit 1; }
grep -qE '^GRADUATED = False\b' "$RUNTIME" || { echo "⛔ runtime 的 GRADUATED 不是寫死 False —— W6 前不准有 AUTO 開關" >&2; exit 1; }
T=$(mktemp -d 2>/dev/null || mktemp -d -t jevrt)
trap 'rm -rf "$T"' EXIT
python3 - "$T" <<'PY'
import json, sys
t = sys.argv[1]
sha = "sha256:" + "a" * 64
json.dump({"header": {"slug": "s", "discussion_hash": sha, "open_questions_state": "none_open"},
           "primary_request": "clear?"}, open(t + "/spec.json", "w"))
json.dump({"feature": "s", "gate": "J1", "artifact_hash": sha, "evidence_hash": sha,
           "head_sha": "0" * 40, "evaluated_at": "2026-09-23T00:00:00Z"}, open(t + "/e.json", "w"))
PY
# packet 走真的 pack(送出前 runtime 會重算 packet_hash;手拼的包會被拒 —— 那正是審查後補的檢查)
PYTHONDONTWRITEBYTECODE=1 python3 "$RUNTIME" pack --gate J1 --in "$T/spec.json" --out "$T/p.json" >/dev/null || { echo "⛔ pack 治具失敗" >&2; exit 2; }
OUT=$(cd "$T" && env -u TYPESAFE_API_KEY PYTHONDONTWRITEBYTECODE=1 python3 "$RUNTIME" --root "$T" ask --gate J1 --slug s \
      --packet "$T/p.json" --evidence "$T/e.json" --author-ref a --session-ref s 2>&1); RC=$?
if [ "$RC" -ne 0 ] || ! grep -q '"noop_reason": "no_api_key"' <<<"$OUT" || [ -e "$T/.devflow" ] || [ -e "$T/.dev-flow" ]; then
  echo "⛔ 未設 key 的 ask 應 exit 0 + no_api_key + 不落盤;實得 rc=$RC" >&2; echo "$OUT" | head -20 >&2; exit 1
fi
echo "  ✓ scripts/devflow-jev.py 存在、可執行;未設 key → exit 0、no_api_key、零寫入"

echo "-- ⑤ key + opt-in 但 endpoint 是 loopback 閉埠 → no-op 不 crash --"
mkdir -p "$T/.dev-flow" && printf 'mode: live\n' > "$T/.dev-flow/jev.yaml"
( cd "$T" && git init -q . && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init )
AGENTMEM_HOME="$T/agentmem-home" python3 - "$T" "$ROOT" <<'PY'
import sys; sys.path.insert(0, sys.argv[2] + "/memory")
from agentmem import identity; identity.ensure_project(sys.argv[1], name="jev-tripwire")
PY
# 清掉環境 proxy:否則 http_proxy 在、no_proxy 不在時,這一發會帶著 Bearer key 出去找 proxy,而不是打 loopback 閉埠
OUT=$(cd "$T" && env -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u all_proxy -u ALL_PROXY no_proxy="127.0.0.1,localhost" \
      AGENTMEM_HOME="$T/agentmem-home" TYPESAFE_API_KEY=not-a-real-key DEVFLOW_JEV_ENDPOINT="http://127.0.0.1:9/" \
      DEVFLOW_ROOT="$ROOT" PYTHONDONTWRITEBYTECODE=1 python3 "$RUNTIME" --root "$T" ask --gate J1 --slug s \
      --packet "$T/p.json" --evidence "$T/e.json" --author-ref a --session-ref s 2>&1); RC=$?
if [ "$RC" -ne 0 ] || ! grep -qE '"noop_reason": "transport:(network|timeout)"' <<<"$OUT" || ! grep -q '"route_taken": "HUMAN"' <<<"$OUT"; then
  echo "⛔ 閉埠 endpoint 的 ask 應 exit 0 + transport:network/timeout + HUMAN;實得 rc=$RC" >&2; echo "$OUT" | head -30 >&2; exit 1
fi
grep -q "not-a-real-key" <<<"$OUT" && { echo "⛔ key 出現在輸出" >&2; exit 1; }
echo "  ✓ transport 失敗 → no-op(exit 0)、route_taken=HUMAN、key 不外露"

echo "-- ③ 案例數地板 --"
MIN_TESTS=180
ACTUAL=$(cat "$PKG"/test_*.py | grep -cE '^\s+def test_')
if [ "$ACTUAL" -lt "$MIN_TESTS" ]; then
  echo "⛔ test_*.py 只有 $ACTUAL 個 test_(地板 $MIN_TESTS)—— 案例被刪" >&2; exit 1
fi
GUARDS=$(grep -cE '^\s+def test_' "$PKG/test_guards.py")
[ "$GUARDS" -ge 127 ] || { echo "⛔ test_guards.py 只剩 $GUARDS 案(W1 地板 127)—— 七守衛的牙被拔" >&2; exit 1; }
echo "  ✓ test_ 定義 $ACTUAL 個(地板 $MIN_TESTS;其中 test_guards.py $GUARDS ≥ 127)"

echo "-- ④ unittest --"
cd "$ROOT" || exit 2
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/devflow_jev -t scripts -p 'test_*.py' 2>&1 | grep -vE '^(ok|\.+)$' | tail -25
RC=${PIPESTATUS[0]}
find "$PKG" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
if [ "$RC" -ne 0 ]; then
  echo "⛔ devflow_jev unittest 紅(exit $RC)" >&2; exit 1
fi
echo "✅ test-devflow-jev: 七組守衛 + W2 runtime 牙全過(shadow/no-op runtime;沒有 AUTO、沒有 verdict 寫入)"
