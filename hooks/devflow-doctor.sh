#!/bin/bash
# devflow-doctor.sh — devflow doctor 薄殼(P3):方法論/Runtime 版本握手,fail-closed。
# 用法: devflow-doctor.sh [--contract PATH] [--gate-cmd CMD]
# 契約解析:--contract / $DEVFLOW_CONTRACT / <專案>/docs/dev/devflow-contract.json。
set -u
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
HERE=$(cd "$(dirname "$0")" && pwd)
. "$HERE/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)
# printer-python 項要 3.12+,但 doctor 本身用 python-lib 選的直譯器就夠跑(3.9 OK)。
# 未明示 DEVFLOW_PYTHON 時,把共用「找 3.12+」(hooks/devflow-find-python.sh,與 Stop hook、
# selftest 同一份)找到的路徑交給 doctor 當產圖直譯器的備選;專案 venv 與系統 python3 夠用時
# doctor 不採用它。找不到就不設,doctor 照原樣報 printer-python ✗ 並說明。
. "$HERE/devflow-find-python.sh"
if [ -z "${DEVFLOW_PYTHON:-}" ]; then
  # 這支備選是給 printer-python(= gate-twin 的 markdown-it-py==4.0.0)用的:優先專案 .venv、
  # 且要 import markdown_it 成功;都沒有才退回「版本 3.12+ 即可」並印提示(見 devflow_find_twin_python)。
  DEVFLOW_FOUND_PYTHON=$(devflow_find_twin_python "$ROOT") && export DEVFLOW_FOUND_PYTHON
fi
# doctor 內要執行 gauntlet／history-append／gate-consistency 等 .sh:用跑得起來的 bash
# (外部已設且跑得起來的照舊;否則優先目前這支 $BASH,再 devflow_find_bash;都不行維持字面 bash)。
if ! { [ -n "${DEVFLOW_BASH:-}" ] && devflow_exe_runs "$DEVFLOW_BASH"; }; then
  if [ -n "${BASH:-}" ] && devflow_exe_runs "$BASH"; then
    DEVFLOW_BASH=$BASH
  else
    DEVFLOW_BASH=$(devflow_find_bash) || DEVFLOW_BASH=bash
  fi
fi
export DEVFLOW_BASH
PYTHONDONTWRITEBYTECODE=1 exec "$DEVFLOW_PY" "$HERE/_doctor_impl.py" "$ROOT" "$@"
