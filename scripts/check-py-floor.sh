#!/bin/bash
# check-py-floor.sh — 最低 Python 版本相容守衛(2026-08-19)。
#
# 抓什麼:會在**採用專案的直譯器**上執行的 .py 檔,有沒有用到比宣告下限更新的語法。
#
# 為什麼需要:2026-08-19 實際踩到 —— `scripts/build-gate-twin.py`(會散發到採用專案的
# `docs/dev/tools/`,三個 gate 的審查頁全靠它產)在 f-string 的**表達式部分**寫了反斜線
# (正則的 `\s`/`\S`)。那個寫法 Python 3.12 才允許,3.11 及更早直接 SyntaxError ——
# 整支檔案讀不進去,不是報錯訊息,是語法錯誤。而 macOS 內建的 /usr/bin/python3 是 3.9,
# 且 dev-flow 挑直譯器的順序把系統內建排在 PATH 之前(README 環境需求段)——
# **等於優先挑到跑不動的那個版本**。這個缺陷在 v3.8.0 就已經出貨,全部既有檢查皆綠。
#
# 宣告下限 = PY_FLOOR(下方常數)。改下限要同時改 README 環境需求段。
#
# 做法:找一個「舊到會顯示出問題」的直譯器(版本在下限 ~ 3.11 之間),用它逐檔真的
# compile 一遍。**找不到就 exit 2,不退回靜態掃描** —— 曾經寫過一版靜態掃描 fallback
# (掃 f-string 的 `{...}` 內有沒有反斜線),實測在 Python 3.12 上抓到零筆:3.12 起
# f-string 被拆成多個 token,不再是單一 STRING token,那份掃描等於永遠印綠。
# 沒驗到就說綠比沒有檢查更糟,所以這裡 fail-closed。
# 要在沒有舊版直譯器的機器上跑,設 DEVFLOW_PY_FLOOR_BIN 指向一個。
#
# exit code:0 = 全過 / 1 = 有檔案在下限版跑不動 / 2 = 檢查本身無法執行。
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

python3 - "$ROOT" <<'PY'
import os
import subprocess
import sys

root = sys.argv[1]

# ── 宣告下限 ──────────────────────────────────────────────────────────────
# 3.9 = macOS 內建 /usr/bin/python3。挑這個當下限是因為 dev-flow 的直譯器解析順序
# 把系統內建排在 PATH 之前,採用專案沒設 DEVFLOW_PYTHON 時拿到的就是它。
PY_FLOOR = (3, 9)

# ── 要驗哪些檔 ───────────────────────────────────────────────────────────
# 全部收:hooks/ 與 docs/dev/tools/ 是採用專案真的會跑的;scripts/ 與 observability/
# 雖然只在母版跑,但同一個寫法在這裡出現過就會被抄到會散發的檔案裡(2026-08-19 實際
# 就是 scripts/ 與 docs/dev/tools/ 各一份同時中),所以一起釘。
PATTERNS = ["hooks/*.py", "scripts/*.py", "observability/*.py", "docs/dev/tools/*.py"]
out = subprocess.run(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", *PATTERNS],
    cwd=root, capture_output=True, text=True)
if out.returncode != 0:
    print(f"⛔ git ls-files 失敗:{out.stderr.strip()}", file=sys.stderr)
    sys.exit(2)
files = sorted(f for f in out.stdout.split() if f.endswith(".py"))
if not files:
    print("⛔ 掃到零個 .py —— 檢查沒有真的跑到東西(PATTERNS 壞了或 repo 空的)",
          file=sys.stderr)
    sys.exit(2)

# ── 找下限版直譯器 ───────────────────────────────────────────────────────
def version_of(exe):
    try:
        r = subprocess.run([exe, "-c",
                            "import sys;print('%d.%d' % sys.version_info[:2])"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return tuple(int(x) for x in r.stdout.strip().split("."))
    except Exception:                                              # noqa: BLE001
        pass
    return None


floor_exe = None
floor_ver = None
for cand in (os.environ.get("DEVFLOW_PY_FLOOR_BIN"), "/usr/bin/python3",
             "python3.9", "python3.10", "python3.11"):
    if not cand:
        continue
    ver = version_of(cand)
    # 只有「舊到會顯示出問題」的版本才算有效證據;3.12+ 什麼都收,驗不到東西
    if ver and PY_FLOOR <= ver < (3, 12):
        floor_exe, floor_ver = cand, ver
        break

failures = []
checked = 0

if floor_exe:
    print(f"• 真編譯模式:用 {floor_exe}(Python {floor_ver[0]}.{floor_ver[1]})逐檔 compile")
    for rel in files:
        checked += 1
        r = subprocess.run(
            [floor_exe, "-c",
             "import sys;src=open(sys.argv[1],encoding='utf-8').read();"
             "compile(src,sys.argv[1],'exec')", os.path.join(root, rel)],
            capture_output=True, text=True)
        if r.returncode != 0:
            tail = (r.stderr.strip().splitlines() or ["(無 stderr)"])[-1]
            failures.append(f"{rel}:在 Python {floor_ver[0]}.{floor_ver[1]} 編譯不過 —— {tail}")
else:
    print(f"⛔ 找不到 Python {PY_FLOOR[0]}.{PY_FLOOR[1]}–3.11 的直譯器 —— 這支檢查無法取得證據。",
          file=sys.stderr)
    print("   試過:$DEVFLOW_PY_FLOOR_BIN、/usr/bin/python3、python3.9/3.10/3.11。",
          file=sys.stderr)
    print("   裝一個下限版直譯器,或設 DEVFLOW_PY_FLOOR_BIN 指向它。"
          "不退回靜態掃描的理由見本檔頂註。", file=sys.stderr)
    sys.exit(2)

# ── 檢查數地板 ──────────────────────────────────────────────────────────
# ⚠️ 必須等於當下實際檔案數(同 repo 慣例:留餘裕 = 沒有牙齒)。增刪 .py 時一起改。
MIN_FILES = 40
if checked < MIN_FILES:
    failures.append(f"⛔ 只驗了 {checked} 個檔(地板 {MIN_FILES})—— PATTERNS 被縮小或 repo 缺檔")

print(f"=== Python 下限相容({PY_FLOOR[0]}.{PY_FLOOR[1]}):驗了 {checked} 個 .py ===")
if failures:
    print(f"❌ {len(failures)} 項不符:")
    for f in failures:
        print(f"   {f}")
    print("   修法:把值落成變數再進 f-string;或改 PY_FLOOR 並同步 README 環境需求段。")
    sys.exit(1)
print(f"✅ {checked} 個 .py 在宣告下限 {PY_FLOOR[0]}.{PY_FLOOR[1]} 下皆可解析")
PY
