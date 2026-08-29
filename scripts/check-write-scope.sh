#!/bin/bash
# check-write-scope.sh — Bash 寫入 prevent-before 的三邊共同入口
#
# 為什麼需要:Edit/Write 走 PreToolUse 當場擋;Bash 舊路是先寫再 postbash
# 事後抓(engine-fence-masking Known Limits #5)。Claude / Cursor / Codex
# 沒有同一套 PreToolUse。共同 runtime 是本檔 --action + hooks/devflow-lib.py
# 的 write_scope_verdict。誰要經 shell 寫檔,先跑 --action;deny → 不准執行
# 那條指令。本檔自己不落盤。
#
# Claude prebash 接到同一套 deny_write_command,不是另一份較鬆的規則。
# 不准為了別的主機改鬆判定。
#
# 用法:
#   scripts/check-write-scope.sh                  # 載入自檢(devflow-check 註冊用)
#   scripts/check-write-scope.sh --action FILE [root]
#       FILE 是一份 JSON:{command:"..."} 或 {paths:["..."]}
#       未武裝 → allow(exit 0);武裝且寫 scope 外 → deny(exit 1);
#       契約缺失 / 讀不到 → exit 2。
#
# exit:0 = allow / 自檢過 / 1 = deny / 2 = 檢查自身故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
PACK=$(cd "$SELF_DIR/.." && pwd)
ROOT=$PACK
ACTION_FILE=""
SANITY=0
if [ "${1:-}" = "--action" ]; then
  ACTION_FILE=${2:-}
  [ -n "$ACTION_FILE" ] || { echo "FATAL: --action 需要 JSON 路徑" >&2; exit 2; }
  if [ -n "${3:-}" ]; then
    ROOT=$(cd "$3" && pwd) || exit 2
  fi
elif [ -z "${1:-}" ]; then
  SANITY=1
else
  echo "FATAL: 只收 --action FILE [root] 或無參數自檢" >&2
  exit 2
fi

LIB="$PACK/hooks/devflow-lib.py"
[ -f "$LIB" ] || { echo "FATAL: 找不到 $LIB" >&2; exit 2; }

. "$PACK/hooks/devflow-python-lib.sh"

if [ "$SANITY" = "1" ]; then
  exec "$DEVFLOW_PY" - "$LIB" <<'PY'
import sys
from importlib.machinery import SourceFileLoader
L = SourceFileLoader("devflow_lib", sys.argv[1]).load_module()
need = ("extract_write_targets", "resolve_write_rel",
        "write_scope_verdict", "deny_write_command")
missing = [n for n in need if not hasattr(L, n)]
if missing:
    print("FATAL: devflow-lib 缺 " + ",".join(missing), file=sys.stderr)
    sys.exit(2)
if L.extract_write_targets("echo sneak > src/sneaky.py") != ["src/sneaky.py"]:
    print("FATAL: extract_write_targets 解不出 echo > 寫路徑", file=sys.stderr)
    sys.exit(1)
if L.extract_write_targets("pytest -q"):
    print("FATAL: 只讀指令不該抽出寫路徑", file=sys.stderr)
    sys.exit(1)
print("PASS: check-write-scope 載入自檢")
sys.exit(0)
PY
fi

exec "$DEVFLOW_PY" - "$ROOT" "$ACTION_FILE" "$LIB" <<'PY'
import json
import os
import sys

sys.dont_write_bytecode = True
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root = sys.argv[1]
action_file = sys.argv[2]
lib_path = sys.argv[3]

from importlib.machinery import SourceFileLoader
L = SourceFileLoader("devflow_lib", lib_path).load_module()

try:
    payload = json.load(open(action_file, encoding="utf-8"))
except (OSError, ValueError) as exc:
    print("FATAL: --action JSON 讀不到/解不出:%s" % exc, file=sys.stderr)
    sys.exit(2)
if not isinstance(payload, dict):
    print("FATAL: --action JSON 頂層必須是 object", file=sys.stderr)
    sys.exit(2)

state, _armed, err = L.load_state(root)
if err:
    print(err, file=sys.stderr)
    sys.exit(2)
if state is None:
    print("allow")
    sys.exit(0)

command = payload.get("command") or ""
paths = payload.get("paths") or []
if not isinstance(command, str):
    print("FATAL: command 必須是字串", file=sys.stderr)
    sys.exit(2)
if paths and not isinstance(paths, list):
    print("FATAL: paths 必須是陣列", file=sys.stderr)
    sys.exit(2)

denied = None
if command:
    denied = L.deny_write_command(root, command, state)
if denied is None:
    for raw in paths:
        if not isinstance(raw, str):
            continue
        rel = L.resolve_write_rel(root, raw)
        if rel is None or L.is_ambient_path(rel):
            continue
        verdict = L.write_scope_verdict(rel, state)
        if verdict is not None:
            denied = (rel, verdict[0], verdict[1])
            break

if denied is None:
    print("allow")
    sys.exit(0)

_rel, _violation, msg = denied
print(msg, file=sys.stderr)
print("deny")
sys.exit(1)
PY
