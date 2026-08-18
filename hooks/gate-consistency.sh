#!/bin/bash
# gate-consistency.sh — gate 條件摘要 vs README §7 正本一致性檢查(手動跑,不掛 hook)。
# 從母版 README §7(G1/G2/G3 唯一正本)動態抽取每個 gate 的關鍵 token,比對三處摘要
# (plugin dev-flow SKILL.md 階段表 / README §3 表 / 三份模板頂註送審步)是否都含該
# token(同義詞如 OC/Owner Calls 經小型映射表正規化)。用法:直接執行,無參數。
# 可用環境變數覆蓋路徑(測試/移植用):DEVFLOW_MASTER(預設 = repo root,即本檔上上層)、
# DEVFLOW_PLUGIN(預設由 _gate_consistency_impl.py 自身位置推導 = plugin root)。
# exit 0 = 三處皆一致 / 1 = 發現漂移 / 2 = 本檢查抽取失敗(anchor 不見,需人工檢查)。
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
. "$HERE/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)
"$DEVFLOW_PY" "$HERE/_gate_consistency_impl.py" "$@"
