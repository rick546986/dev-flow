# devflow-python-lib.sh — hook 直譯器解析唯一正本(被 source,不被執行;644 無執行位元,
# 比照 devflow_twin_ui.py 的先例)。用法:source 本檔後以 "$DEVFLOW_PY" 呼叫 python。
#
# 直譯器解析。優先系統 python3(避免撿到 pyenv/conda/homebrew shim ——
# 那類直譯器可能缺標準函式庫、啟動慢、或在不同目錄解析成不同版本;
# hook 每次工具呼叫都跑,撿錯就是守衛隨機自壞),找不到才退回 PATH。
# DEVFLOW_PYTHON 供 Windows Git Bash / 非標準環境覆寫。
# ⚠️ 不要改成 env python3 或裸 python3 —— 那正是這段要防的事。
DEVFLOW_PY="${DEVFLOW_PYTHON:-$([ -x /usr/bin/python3 ] && echo /usr/bin/python3 || command -v python3)}"

# 解析不到可用直譯器 → fail-open:印一行警告後 exit 0(放行本次工具呼叫)。
# ⚠️ 這跟本 repo 到處都是的 fail-closed 相反,是刻意的:這條路徑上「擋住」的代價
# 是把使用者的宿主卡死(Windows 現場 = 每次工具呼叫噴錯,只能整個關掉 plugin),
# 而不是漏掉一次檢查 —— 守衛失效總比把宿主卡死好。
# 只有「找不到直譯器」這一種情況 fail-open;找到直譯器之後,各守衛原本的
# fail-closed 行為一個都不變。
if [ -z "$DEVFLOW_PY" ] || ! command -v "$DEVFLOW_PY" >/dev/null 2>&1; then
  echo "devflow: 找不到 python3,本次守衛跳過(設 DEVFLOW_PYTHON 可指定)" >&2
  exit 0
fi
