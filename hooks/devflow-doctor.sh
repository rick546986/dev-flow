#!/bin/bash
# devflow-doctor.sh — devflow doctor 薄殼(P3):方法論/Runtime 版本握手,fail-closed。
# 用法: devflow-doctor.sh [--contract PATH] [--gate-cmd CMD]
# 契約解析:--contract / $DEVFLOW_CONTRACT / <專案>/docs/dev/devflow-contract.json。
set -u
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
HERE=$(cd "$(dirname "$0")" && pwd)
. "$HERE/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)
PYTHONDONTWRITEBYTECODE=1 exec "$DEVFLOW_PY" "$HERE/_doctor_impl.py" "$ROOT" "$@"
