#!/bin/bash
# test-find-python.sh — hooks/devflow-find-python.sh(「找跑得起來的 Python 3.12+」共用正本)的行為牙。
#
# 起因(2026-10-15 採用現場,macOS):手動跑 doctor／selftest 且未設 DEVFLOW_PYTHON 時,doctor 的
# printer-python 項抓到 /usr/bin/python3(3.9)→ INCOMPATIBLE exit 1;Stop hook 自己有找 3.12+ 的
# 邏輯,手動路徑沒有。另外 Mac 的 /usr/local/bin 常是 x86 版 bash／python3.12,在 Apple Silicon 上
# `Bad CPU type in executable`(exit 126),只看 `-x` 會選到它。
#
# 咬什麼(共用函式本身):
#   ① 壞掉的候選(跑起來 exit 126)排在 PATH 前面、好的在後面 → 選好的(舊的 `command -v` 只回第一個,
#      第一個壞就整個漏掉);② `--version` 跑不起來但 `-c` 能跑的候選也要跳過(證明有試跑 --version,
#      不是只靠版本檢查);③ PATH 的空項／相對路徑不撿(空項 = 目前目錄);④ 只有 3.9 → 找不到,
#      說明文字講到 3.9／3.12／DEVFLOW_PYTHON;⑤ DEVFLOW_PYTHON 明示不到 3.12 → 不偷換;
#      ⑥ devflow_find_bash 跳過壞 bash。
# 咬三條呼叫路徑(都走同一份,不是各抄一份):
#   ⑦ 手動 selftest.sh 未設 DEVFLOW_PYTHON、只有 3.9 → exit 2 + 清楚訊息、不跑任何案例;
#   ⑧ 手動 selftest.sh 找得到 → 把它設成 DEVFLOW_PYTHON(截斷前言實跑);
#   ⑨ 手動 devflow-doctor.sh → 找到的路徑以 DEVFLOW_FOUND_PYTHON 交給 doctor;
#   ⑩ doctor.resolve_printer_python:系統 3.9 + 自動找到 3.12+ → 採用;系統夠用 / 專案 venv / 明示
#      DEVFLOW_PYTHON 都不被搶;自動找到的跑不起來 → 退回系統(照舊報 ✗);
#   ⑪ 三處 shell 都 source 共用檔、沒有各抄一份(靜態);共用檔 644 且隨 hooks/ 同目錄(plugin 整包散發)。
#
# 用法:scripts/test-find-python.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" 2>/dev/null && pwd) || { echo "找不到 root: $1" >&2; exit 2; }
fi
LIB="$ROOT/hooks/devflow-find-python.sh"
for f in "$LIB" "$ROOT/hooks/selftest.sh" "$ROOT/hooks/devflow-doctor.sh" \
         "$ROOT/hooks/devflow-stop-selftest.sh" "$ROOT/hooks/_doctor_impl.py"; do
  [ -f "$f" ] || { echo "FATAL: 找不到 $f" >&2; exit 2; }
done
REAL_PY=$(command -v python3) || { echo "FATAL: 需要 python3" >&2; exit 2; }

MIN_CASES=31
PASS=0
FAIL=0
TOTAL=0
WORK=$(mktemp -d "${TMPDIR:-/tmp}/devflow-find-python-test.XXXXXX") || exit 2
trap 'rm -rf "$WORK"' EXIT

expect() {  # expect <label> <condition-rc>
  TOTAL=$((TOTAL + 1))
  if [ "$2" -eq 0 ]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $1" >&2
  fi
}

# 假直譯器:`--version` 與 `-c` 都能跑;`-c` 交給真的 python3,但先把 sys.version_info 換成指定版本,
# 所以「3.12+」判斷是真的被執行,不是看假檔的 exit 碼。
fake_py() {  # fake_py <路徑> <假版本 X.Y>
  printf '#!/bin/sh\nif [ "$1" = "-c" ]; then\n  exec "%s" -c %s "$2" "%s"\nfi\necho "Python %s.0"\nexit 0\n' \
    "$REAL_PY" "'import sys; sys.version_info = tuple(int(x) for x in sys.argv[2].split(\".\")) + (0,); exec(sys.argv[1])'" \
    "$2" "$2" >"$1"
  chmod 755 "$1"
}
broken() {  # broken <路徑>:任何參數都 exit 126(= x86 版在 Apple Silicon 上 Bad CPU type)
  printf '#!/bin/sh\necho "Bad CPU type in executable" >&2\nexit 126\n' >"$1"
  chmod 755 "$1"
}
version_broken_py() {  # version_broken_py <路徑> <假版本>:`--version` 126,但 `-c` 能跑
  printf '#!/bin/sh\n[ "$1" = "--version" ] && exit 126\nexec "%s" -c %s "$2" "%s"\n' \
    "$REAL_PY" "'import sys; sys.version_info = tuple(int(x) for x in sys.argv[2].split(\".\")) + (0,); exec(sys.argv[1])'" \
    "$2" >"$1"
  chmod 755 "$1"
}
# 最小工具目錄:只放共用檔與 selftest 前言要用的外部指令,擋掉本機真的 python3.x
TOOLS="$WORK/tools"; mkdir -p "$TOOLS"
for t in bash sh tr dirname cat grep git mktemp rm sed head tail date cut cksum mkdir seq; do
  src=$(command -v "$t" 2>/dev/null) && ln -sf "$src" "$TOOLS/$t"
done

# find <PATH> [VAR=val ...]:在乾淨環境 source 共用檔後呼叫 devflow_find_py312,印結果、rc 寫 $WORK/rc
find_py() {
  local p=$1; shift
  env -i HOME="$WORK/home" PATH="$p" "$@" bash -c '. "$1"; devflow_find_py312' _ "$LIB" >"$WORK/out" 2>"$WORK/err"
  echo $? >"$WORK/rc"
}
rc() { cat "$WORK/rc"; }
out() { cat "$WORK/out"; }
mkdir -p "$WORK/home"

# ① 壞的排前面、好的在後面(同名 python3.12)
mkdir -p "$WORK/b1" "$WORK/g1"
broken "$WORK/b1/python3.12"; fake_py "$WORK/g1/python3.12" 3.12
find_py "$WORK/b1:$WORK/g1:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "壞的(exit 126)python3.12 排 PATH 前面 → 跳過,選後面好的" \
  "$([ "$(rc)" = 0 ] && [ "$(out)" = "$WORK/g1/python3.12" ]; echo $?)"
# 壞的在 PATH、好的在額外目錄
find_py "$WORK/b1:$TOOLS" DEVFLOW_STOP_PY_DIRS="$WORK/g1"
expect "PATH 上只有壞的 → 額外目錄(Homebrew 等)好的被採用" \
  "$([ "$(rc)" = 0 ] && [ "$(out)" = "$WORK/g1/python3.12" ]; echo $?)"
# 全壞
mkdir -p "$WORK/b2"; broken "$WORK/b2/python3.13"; broken "$WORK/b2/python3"
find_py "$WORK/b1:$WORK/b2:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "候選全是壞的 → 找不到(return 1)、不印路徑" "$([ "$(rc)" = 1 ] && [ -z "$(out)" ]; echo $?)"

# ② --version 跑不起來、-c 能跑 → 也要跳過
mkdir -p "$WORK/v1"; version_broken_py "$WORK/v1/python3.13" 3.13
find_py "$WORK/v1:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "--version 跑不起來(-c 能跑)的候選被跳過 → 有先試跑 --version" \
  "$([ "$(rc)" = 1 ] && [ -z "$(out)" ]; echo $?)"
fake_py "$WORK/g1/python3.13" 3.13
find_py "$WORK/v1:$WORK/g1:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "--version 跑不起來的跳過後,選後面能跑的 python3.13" \
  "$([ "$(rc)" = 0 ] && [ "$(out)" = "$WORK/g1/python3.13" ]; echo $?)"

# 優先序:3.13 優先於 3.12;不到 3.12 的被跳過;只有 python3 且 3.12+ 也接受
mkdir -p "$WORK/o1"; fake_py "$WORK/o1/python3.12" 3.12; fake_py "$WORK/o1/python3.13" 3.13; fake_py "$WORK/o1/python3.14" 3.11
find_py "$WORK/o1:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "優先序:3.14(版本不足)跳過、3.13 優先於 3.12" \
  "$([ "$(rc)" = 0 ] && [ "$(out)" = "$WORK/o1/python3.13" ]; echo $?)"
mkdir -p "$WORK/o2"; fake_py "$WORK/o2/python3" 3.12
find_py "$WORK/o2:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "只有 python3 且是 3.12 → 接受" "$([ "$(rc)" = 0 ] && [ "$(out)" = "$WORK/o2/python3" ]; echo $?)"

# ③ PATH 的空項／相對路徑不撿
mkdir -p "$WORK/cwd"; fake_py "$WORK/cwd/python3.13" 3.13
( cd "$WORK/cwd" && env -i HOME="$WORK/home" PATH=":.:$TOOLS" DEVFLOW_STOP_PY_DIRS="" \
    bash -c '. "$1"; devflow_find_py312' _ "$LIB" >"$WORK/out" 2>"$WORK/err"; echo $? >"$WORK/rc" )
expect "PATH 有空項與 . 時不從目前目錄撿 python3.13" "$([ "$(rc)" = 1 ] && [ -z "$(out)" ]; echo $?)"

# ④ 只有 3.9:找不到,說明文字完整
mkdir -p "$WORK/old"; fake_py "$WORK/old/python3" 3.9; fake_py "$WORK/old/python3.9" 3.9
find_py "$WORK/old:$TOOLS" DEVFLOW_STOP_PY_DIRS=""
expect "只有 3.9 → 找不到" "$([ "$(rc)" = 1 ] && [ -z "$(out)" ]; echo $?)"
env -i HOME="$WORK/home" PATH="$WORK/old:$TOOLS" DEVFLOW_STOP_PY_DIRS="" \
  bash -c '. "$1"; devflow_no_py312_text' _ "$LIB" >"$WORK/out" 2>&1
expect "找不到時的說明:講到 3.9、3.12、怎麼裝、DEVFLOW_PYTHON" \
  "$(grep -q 'Python 3.9' "$WORK/out" && grep -q '3.12' "$WORK/out" && grep -q 'brew install' "$WORK/out" && grep -q 'DEVFLOW_PYTHON=' "$WORK/out"; echo $?)"
env -i HOME="$WORK/home" PATH="$WORK/b2:$TOOLS" DEVFLOW_STOP_PY_DIRS="" \
  bash -c '. "$1"; devflow_no_py312_text' _ "$LIB" >"$WORK/out" 2>&1
expect "找不到且 PATH 的 python3 跑不起來 → 說明講到跑不起來(Bad CPU type)" \
  "$(grep -q 'Bad CPU type' "$WORK/out" && grep -q '跑不起來' "$WORK/out"; echo $?)"

# ⑤ DEVFLOW_PYTHON 明示
find_py "$WORK/g1:$TOOLS" DEVFLOW_STOP_PY_DIRS="" DEVFLOW_PYTHON="$WORK/old/python3"
expect "DEVFLOW_PYTHON 明示但是 3.9 → 不偷換(PATH 上有好的也不用),找不到" \
  "$([ "$(rc)" = 1 ] && [ -z "$(out)" ]; echo $?)"
find_py "$WORK/g1:$TOOLS" DEVFLOW_STOP_PY_DIRS="" DEVFLOW_PYTHON="$WORK/g1/python3.12"
expect "DEVFLOW_PYTHON 明示且是 3.12 → 採用" "$([ "$(rc)" = 0 ] && [ "$(out)" = "$WORK/g1/python3.12" ]; echo $?)"
find_py "$WORK/g1:$TOOLS" DEVFLOW_STOP_PY_DIRS="" DEVFLOW_PYTHON="$WORK/b1/python3.12"
expect "DEVFLOW_PYTHON 明示但跑不起來(126)→ 找不到" "$([ "$(rc)" = 1 ] && [ -z "$(out)" ]; echo $?)"
find_py "$WORK/g1:$TOOLS" DEVFLOW_STOP_PY_DIRS="" DEVFLOW_PYTHON="python3.12"
expect "DEVFLOW_PYTHON 給指令名(不含斜線)→ 以 PATH 解析後採用" \
  "$([ "$(rc)" = 0 ] && [ "$(out)" = "$WORK/g1/python3.12" ]; echo $?)"

# ⑥ devflow_find_bash 跳過壞 bash
mkdir -p "$WORK/bb" "$WORK/bg"
broken "$WORK/bb/bash"; printf '#!/bin/sh\necho "GNU bash, version 5"\n' >"$WORK/bg/bash"; chmod 755 "$WORK/bg/bash"
env -i HOME="$WORK/home" PATH="$WORK/bb:$WORK/bg:$TOOLS" "$TOOLS/bash" -c '. "$1"; devflow_find_bash' _ "$LIB" >"$WORK/out" 2>&1
expect "devflow_find_bash:壞 bash(126)排前面 → 選後面能跑的" "$([ "$(out)" = "$WORK/bg/bash" ]; echo $?)"

# ⑦ 手動 selftest.sh 未設 DEVFLOW_PYTHON、只有 3.9
mkdir -p "$WORK/tmpq"
env -i HOME="$WORK/home" TMPDIR="$WORK/tmpq" PATH="$WORK/old:$TOOLS" DEVFLOW_STOP_PY_DIRS="" "$TOOLS/bash" "$ROOT/hooks/selftest.sh" \
  >"$WORK/out" 2>"$WORK/err"; echo $? >"$WORK/rc"
expect "手動 selftest.sh 只有 3.9 → exit 2(環境不備,不是案例失敗)" "$([ "$(rc)" = 2 ]; echo $?)"
expect "手動 selftest.sh 只有 3.9 → stderr 清楚:Python 3.9、需要 3.12、DEVFLOW_PYTHON、怎麼裝" \
  "$(grep -q 'Python 3.9' "$WORK/err" && grep -q '3.12' "$WORK/err" && grep -q 'DEVFLOW_PYTHON=' "$WORK/err" && grep -q 'brew install' "$WORK/err"; echo $?)"
expect "手動 selftest.sh 只有 3.9 → 沒有開始跑案例(stdout 無「守衛自測」)、沒留暫存目錄" \
  "$(! grep -q '守衛自測' "$WORK/out" && [ -z "$(ls -A "$WORK/tmpq")" ]; echo $?)"
# 壞的 x86 python3.12 + 好的在後 → selftest 前言選好的(截斷前言實跑,不跑 30 秒全套)
HK="$WORK/hooks-copy"; mkdir -p "$HK"; cp -R "$ROOT/hooks/." "$HK/"
sed -n '1,/^# devflow:tmpdir-normalize:start/p' "$ROOT/hooks/selftest.sh" >"$HK/selftest-preamble.sh"
printf 'echo "PY=$DEVFLOW_PYTHON"\n' >>"$HK/selftest-preamble.sh"
env -i HOME="$WORK/home" PATH="$WORK/b1:$WORK/g1:$TOOLS" DEVFLOW_STOP_PY_DIRS="" "$TOOLS/bash" "$HK/selftest-preamble.sh" >"$WORK/out" 2>&1
expect "⑧ 手動 selftest.sh 前言:壞的 python3.12 跳過、選好的並設成 DEVFLOW_PYTHON" \
  "$(grep -qx "PY=$WORK/g1/python3.13" "$WORK/out" || grep -qx "PY=$WORK/g1/python3.12" "$WORK/out"; echo $?)"
env -i HOME="$WORK/home" PATH="$WORK/old:$TOOLS" DEVFLOW_STOP_PY_DIRS="" DEVFLOW_PYTHON="$WORK/old/python3" \
  "$TOOLS/bash" "$HK/selftest-preamble.sh" >"$WORK/out" 2>&1
expect "手動 selftest.sh 前言:明示 DEVFLOW_PYTHON(3.9)照舊尊重、不偷換也不擋" \
  "$(grep -qx "PY=$WORK/old/python3" "$WORK/out"; echo $?)"

# ⑨ 手動 devflow-doctor.sh:把找到的路徑以 DEVFLOW_FOUND_PYTHON 交給 doctor(換成只印環境的 stub)
printf '#!/usr/bin/env python3\nimport os, sys\nprint("FOUND=" + os.environ.get("DEVFLOW_FOUND_PYTHON", "(unset)"))\n' >"$HK/_doctor_impl.py"
env -i HOME="$WORK/home" PATH="$WORK/b1:$WORK/g1:$TOOLS" DEVFLOW_STOP_PY_DIRS="" "$HK/devflow-doctor.sh" >"$WORK/out" 2>&1
expect "手動 devflow-doctor.sh:壞的 python3.12 跳過,DEVFLOW_FOUND_PYTHON = 好的 python3.13" \
  "$(grep -qx "FOUND=$WORK/g1/python3.13" "$WORK/out"; echo $?)"
env -i HOME="$WORK/home" PATH="$WORK/old:$TOOLS" DEVFLOW_STOP_PY_DIRS="" "$HK/devflow-doctor.sh" >"$WORK/out" 2>&1
expect "手動 devflow-doctor.sh:找不到 3.12+ → 不設 DEVFLOW_FOUND_PYTHON(doctor 照原樣報 ✗)" \
  "$(grep -qx "FOUND=(unset)" "$WORK/out"; echo $?)"
env -i HOME="$WORK/home" PATH="$WORK/g1:$TOOLS" DEVFLOW_STOP_PY_DIRS="" DEVFLOW_PYTHON="$REAL_PY" "$HK/devflow-doctor.sh" >"$WORK/out" 2>&1
expect "手動 devflow-doctor.sh:明示 DEVFLOW_PYTHON 時不自動找(不偷換)" \
  "$(grep -qx "FOUND=(unset)" "$WORK/out"; echo $?)"

# ⑩ doctor.resolve_printer_python 的取捨(以 mock 決定性驗證,不依賴本機 /usr/bin/python3 版本)
PYOUT=$("$REAL_PY" - "$ROOT/hooks/_doctor_impl.py" <<'PY'
import importlib.util
import os
import sys
from unittest import mock

spec = importlib.util.spec_from_file_location("_doctor_impl", sys.argv[1])
d = importlib.util.module_from_spec(spec)
sys.dont_write_bytecode = True
spec.loader.exec_module(d)

SYS = os.path.join(os.sep, "usr", "bin", "python3")
VENV = os.path.join("/proj", ".venv", "bin", "python")
FOUND = "/opt/homebrew/bin/python3.12"
results = []


def case(label, versions, env, expect, files=(SYS,)):
    """versions:{exe: (maj, min) | None};env:要設的環境變數;expect:(exe, kind)。"""
    base = {k: v for k, v in os.environ.items() if k not in ("DEVFLOW_PYTHON", "DEVFLOW_FOUND_PYTHON")}
    base.update(env)
    with mock.patch.dict(os.environ, base, clear=True), \
         mock.patch.object(d, "_python_version", side_effect=lambda exe: versions.get(exe)), \
         mock.patch.object(d.os.path, "isfile", side_effect=lambda p: p in files), \
         mock.patch.object(d.os, "access", return_value=True), \
         mock.patch.object(d.shutil, "which", return_value=None):
        exe, ver, kind = d.resolve_printer_python("/proj")
    ok = (exe, kind) == expect
    results.append(ok)
    print("CASE%d=%s" % (len(results), "ok" if ok else "ng"))
    print(("  ✓ " if ok else "  ✗ ") + label + ("" if ok else " — 得 %r" % ((exe, ver, kind),)), file=sys.stderr)


case("系統 3.9 + 自動找到 3.12 → 採用自動找到的(kind=auto)",
     {SYS: (3, 9), FOUND: (3, 12)}, {"DEVFLOW_FOUND_PYTHON": FOUND}, (FOUND, "auto"))
case("系統 3.9、沒有自動找到 → 回系統 3.9(讓 doctor 照舊報 ✗)",
     {SYS: (3, 9)}, {}, (SYS, "system"))
case("系統 3.13 夠用 + 自動找到 3.12 → 系統不被搶走",
     {SYS: (3, 13), FOUND: (3, 12)}, {"DEVFLOW_FOUND_PYTHON": FOUND}, (SYS, "system"))
case("專案 venv 3.12 + 系統 3.9 + 自動找到 → 專案 venv 優先",
     {VENV: (3, 12), SYS: (3, 9), FOUND: (3, 12)}, {"DEVFLOW_FOUND_PYTHON": FOUND}, (VENV, "venv"),
     files=(SYS, VENV))
case("明示 DEVFLOW_PYTHON(可執行)+ 自動找到 → 明示優先",
     {"/x/py": (3, 11), SYS: (3, 9), FOUND: (3, 12)}, {"DEVFLOW_PYTHON": "/x/py", "DEVFLOW_FOUND_PYTHON": FOUND},
     ("/x/py", "env"))
case("自動找到的跑不起來(版本查不到)→ 退回系統",
     {SYS: (3, 9), FOUND: None}, {"DEVFLOW_FOUND_PYTHON": FOUND}, (SYS, "system"))
case("自動找到的不到 3.12 → 不採用,退回系統",
     {SYS: (3, 9), FOUND: (3, 11)}, {"DEVFLOW_FOUND_PYTHON": FOUND}, (SYS, "system"))
sys.exit(0 if all(results) and len(results) == 7 else 1)
PY
)
for i in 1 2 3 4 5 6 7; do
  expect "⑩ resolve_printer_python mock 案 $i/7" "$(printf '%s\n' "$PYOUT" | grep -qx "CASE$i=ok"; echo $?)"
done

# ⑪ 靜態:三處都 source 共用檔、沒有各抄一份;共用檔 644、與 python-lib 同目錄
expect "selftest.sh／devflow-doctor.sh／devflow-stop-selftest.sh 都 source devflow-find-python.sh" \
  "$(grep -q 'devflow-find-python.sh' "$ROOT/hooks/selftest.sh" && grep -q 'devflow-find-python.sh' "$ROOT/hooks/devflow-doctor.sh" \
     && grep -q 'devflow-find-python.sh' "$ROOT/hooks/devflow-stop-selftest.sh"; echo $?)"
expect "Stop hook 不再自抄 py_ok／find_py(只留共用函式的呼叫)" \
  "$(! grep -Eq '^(py_ok|find_py)\(\)' "$ROOT/hooks/devflow-stop-selftest.sh" && grep -q 'devflow_find_py312' "$ROOT/hooks/devflow-stop-selftest.sh"; echo $?)"
expect "共用檔與 devflow-python-lib.sh 同在 hooks/(plugin 整包散發)、644 無執行位元" \
  "$([ -f "$ROOT/hooks/devflow-python-lib.sh" ] && [ ! -x "$LIB" ]; echo $?)"

if [ "$TOTAL" -lt "$MIN_CASES" ]; then
  echo "FATAL: 案例數 $TOTAL 低於下限 $MIN_CASES(案例被刪?)" >&2
  exit 2
fi
echo "=== test-find-python:$PASS/$TOTAL ==="
[ "$FAIL" -eq 0 ]
