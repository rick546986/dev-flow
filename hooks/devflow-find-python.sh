# devflow-find-python.sh — 「找跑得起來的 Python 3.12+」唯一正本(被 source,不被執行;
# 644 無執行位元,比照 devflow-python-lib.sh)。只定義函式,source 時不做任何事、不 exit。
#
# 誰用:Stop hook(devflow-stop-selftest.sh)、手動跑的 selftest.sh、手動跑的 devflow-doctor.sh。
# 三條路徑共用這一份,不要各抄一份 —— 抄過一次就漂移過一次(手動路徑沒有這套,macOS 上
# 系統內建 python3 是 3.9,未設 DEVFLOW_PYTHON 的手動 doctor/selftest 直接 INCOMPATIBLE)。
#
# 跟 devflow-python-lib.sh 的分工:python-lib 管「各支 hook 用哪支直譯器跑」(系統 python3
# 優先,3.9 就夠,找不到 fail-open);本檔管「要 3.12+ 的場合(自測內的 doctor printer-python 項、
# markdown-it-py==4.0.0)去哪找」。本檔不改 python-lib 的任何行為。
#
# 候選一律「先試跑才採用」:Mac 的 /usr/local/bin 常是 x86 版的 bash／python3.12,在 Apple
# Silicon 上會 `Bad CPU type in executable`(exit 126)。只看 `-x` 會選到它、之後整套自測以
# exit 126 死掉。所以候選要 `--version` 跑得起來(exit 0)才算數;跑不起來就跳過、找下一個,
# 而且 PATH 裡的每個目錄都會找(`command -v` 只回第一個,第一個是壞的就整個漏掉後面好的)。
#
# 順序:DEVFLOW_PYTHON(明示;不到 3.12 或跑不起來 → 找不到,不偷換)
#       → python3.15 / 3.14 / 3.13 / 3.12(PATH 各目錄,再加額外目錄)→ PATH 上的 python3。
# 額外目錄預設 /opt/homebrew/bin /usr/local/bin ~/.local/bin(Claude 從 GUI 起時 PATH 常不含
# Homebrew);DEVFLOW_STOP_PY_DIRS 覆寫(空白分隔;設成空字串 = 不找額外目錄,測試用)。
# 另有 devflow_find_twin_python:給 build-gate-twin.py 用(專案 .venv 優先、要 import markdown_it),
# 見該函式註解;devflow_find_py312 與其呼叫端(selftest、Stop hook)不受影響。
# PATH 裡的空項與相對路徑會略過(空項 = 目前目錄,不准從專案目錄撿可執行檔來跑)。

devflow_exe_runs() {  # devflow_exe_runs <exe>:是可執行檔,且 `--version` 真的跑得起來
  [ -n "${1:-}" ] && [ -f "$1" ] && [ -x "$1" ] && "$1" --version >/dev/null 2>&1
}

devflow_py_ok() {  # devflow_py_ok <exe>:跑得起來、且是 3.12 以上
  devflow_exe_runs "${1:-}" \
    && "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' >/dev/null 2>&1
}

devflow_py_version() {  # devflow_py_version <exe>:印 X.Y.Z;跑不起來印空字串
  devflow_exe_runs "${1:-}" || return 0
  "$1" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || true
}

devflow__path_dirs() {  # PATH 裡的絕對路徑目錄,一行一個(純 shell 切字串,不依賴 tr 等外部指令)
  local _rest="${PATH:-}:" _d
  while [ -n "$_rest" ]; do
    _d=${_rest%%:*}
    _rest=${_rest#*:}
    case "$_d" in /*) printf '%s\n' "$_d" ;; esac
  done
}

devflow__extra_dirs() {
  local _d
  for _d in ${DEVFLOW_STOP_PY_DIRS-/opt/homebrew/bin /usr/local/bin ${HOME:-/nonexistent}/.local/bin}; do
    printf '%s\n' "$_d"
  done
}

devflow_find_py312() {  # 印找到的直譯器路徑並 return 0;找不到 return 1
  local _name _d _c _dirs
  if [ -n "${DEVFLOW_PYTHON:-}" ]; then
    _c=$DEVFLOW_PYTHON
    case "$_c" in */*) : ;; *) _c=$(command -v "$_c" 2>/dev/null || true) ;; esac
    devflow_py_ok "$_c" && { printf '%s\n' "$_c"; return 0; }
    return 1
  fi
  _dirs=$(devflow__path_dirs; devflow__extra_dirs)
  for _name in python3.15 python3.14 python3.13 python3.12; do
    while IFS= read -r _d; do
      [ -n "$_d" ] || continue
      devflow_py_ok "$_d/$_name" && { printf '%s\n' "$_d/$_name"; return 0; }
    done <<EOF
$_dirs
EOF
  done
  while IFS= read -r _d; do
    [ -n "$_d" ] || continue
    devflow_py_ok "$_d/python3" && { printf '%s\n' "$_d/python3"; return 0; }
  done <<EOF
$(devflow__path_dirs)
EOF
  return 1
}

# ── gate-twin(build-gate-twin.py)用的直譯器 ─────────────────────────────────────────────
# devflow_find_py312 只看版本;但 build-gate-twin.py 還要 `import markdown_it`(markdown-it-py==4.0.0,
# 缺 → exit 3)。版本對、卻沒裝 markdown-it-py 的 3.12+(例如另一個 python3.13)會讓 gate-twin 一跑就 exit 3。
# 所以「給 gate-twin 用」的另開 devflow_find_twin_python,devflow_find_py312 本身一個字不動 ——
# 不需要 markdown_it 的呼叫端(Stop hook 自測、手動 selftest、doctor 的備選)不會因此變嚴。
devflow_py_has_mdit() {  # devflow_py_has_mdit <exe>:`import markdown_it` 成功
  [ -n "${1:-}" ] && "$1" -c 'import markdown_it' >/dev/null 2>&1
}

devflow__twin_warn() {  # devflow__twin_warn <exe>:退回「版本 3.12+ 即可」時的提示(stderr)
  {
    echo "dev-flow:gate-twin 用的直譯器 $1 是 3.12+,但 import markdown_it 失敗(沒裝 markdown-it-py),"
    echo "  build-gate-twin.py 在它上面會 exit 3。已找過:DEVFLOW_PYTHON、專案 .venv、PATH 各目錄與額外目錄的 python3.12–3.15,"
    echo "  沒有任何一支裝了 markdown-it-py。建議:"
    echo "    ① 設 DEVFLOW_PYTHON 指向已裝好的 3.12+ 直譯器(例如專案 .venv/bin/python);或"
    echo "    ② 在專案 venv 裝:pip install 'markdown-it-py==4.0.0'(不要覆寫 Apple／系統 Python)。"
  } >&2
}

# devflow_find_twin_python [專案根]:印 gate-twin 該用的直譯器並 return 0;連 3.12+ 都沒有 return 1。
# 順序:① DEVFLOW_PYTHON 明示 → 最優先(3.12+ 且跑得起來才算;沒裝 markdown_it 只警告、不偷換)
#       ② 專案 .venv(<專案根>/.venv/bin/python、python3;Windows 為 .venv/Scripts/python.exe),
#          專案根 = 第 1 個參數,沒給用 $CLAUDE_PROJECT_DIR;須 3.12+ 且 import markdown_it 成功
#       ③ 其餘候選(同 devflow_find_py312 的順序與試跑規則)中第一支 import markdown_it 成功的
#       ④ 都沒有含 markdown_it 的 → 退回 devflow_find_py312 的結果(版本 3.12+ 即可),並印提示到 stderr。
devflow_find_twin_python() {
  local _proj=${1:-${CLAUDE_PROJECT_DIR:-}} _c _name _d _dirs
  if [ -n "${DEVFLOW_PYTHON:-}" ]; then
    _c=$DEVFLOW_PYTHON
    case "$_c" in */*) : ;; *) _c=$(command -v "$_c" 2>/dev/null || true) ;; esac
    devflow_py_ok "$_c" || return 1
    devflow_py_has_mdit "$_c" || devflow__twin_warn "$_c"
    printf '%s\n' "$_c"
    return 0
  fi
  if [ -n "$_proj" ]; then
    for _c in "$_proj/.venv/bin/python" "$_proj/.venv/bin/python3" "$_proj/.venv/Scripts/python.exe"; do
      devflow_py_ok "$_c" && devflow_py_has_mdit "$_c" && { printf '%s\n' "$_c"; return 0; }
    done
  fi
  _dirs=$(devflow__path_dirs; devflow__extra_dirs)
  for _name in python3.15 python3.14 python3.13 python3.12; do
    while IFS= read -r _d; do
      [ -n "$_d" ] || continue
      devflow_py_ok "$_d/$_name" && devflow_py_has_mdit "$_d/$_name" && { printf '%s\n' "$_d/$_name"; return 0; }
    done <<EOF
$_dirs
EOF
  done
  while IFS= read -r _d; do
    [ -n "$_d" ] || continue
    devflow_py_ok "$_d/python3" && devflow_py_has_mdit "$_d/python3" && { printf '%s\n' "$_d/python3"; return 0; }
  done <<EOF
$(devflow__path_dirs)
EOF
  _c=$(devflow_find_py312) || return 1
  devflow__twin_warn "$_c"
  printf '%s\n' "$_c"
}

devflow_find_bash() {  # 印第一個跑得起來的 bash;都不行 return 1(呼叫端自行退回字面 bash)
  local _d _c
  while IFS= read -r _d; do
    [ -n "$_d" ] || continue
    devflow_exe_runs "$_d/bash" && { printf '%s\n' "$_d/bash"; return 0; }
  done <<EOF
$(devflow__path_dirs; printf '%s\n' /bin /usr/bin /opt/homebrew/bin /usr/local/bin)
EOF
  return 1
}

devflow_no_py312_text() {  # 手動路徑(selftest)找不到 3.12+ 時的說明;印到 stdout
  local _p _v
  _p=$(command -v python3 2>/dev/null || true)
  _v=$(devflow_py_version "$_p")
  echo "dev-flow:找不到可用的 Python 3.12 以上直譯器,自測沒有跑。"
  if [ -n "$_v" ]; then
    echo "  PATH 上的 python3 是 $_p(Python $_v)—— 自測內 doctor 的 printer-python 項要 3.12+"
    echo "  (macOS 系統內建 python3 是 3.9,只保證語法可解析,跑不了自測)。"
  elif [ -n "$_p" ]; then
    echo "  PATH 上的 python3($_p)跑不起來(例如 x86 版在 Apple Silicon 上 Bad CPU type),已跳過。"
  else
    echo "  PATH 上沒有 python3。"
  fi
  echo "  已找過:PATH 各目錄、/opt/homebrew/bin、/usr/local/bin、~/.local/bin 的 python3.15–3.12。"
  echo "  安裝其一:brew install python@3.12 / uv python install 3.12 / 從 python.org 下載。"
  echo "  裝好後設 DEVFLOW_PYTHON 指向它再重跑,例如:"
  echo "    DEVFLOW_PYTHON=/opt/homebrew/bin/python3.12 bash <plugin-root>/hooks/selftest.sh"
}
