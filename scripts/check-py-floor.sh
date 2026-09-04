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
# 宣告下限 = PY_FLOOR(下方常數)= 編譯地板。printers 在 3.9 仍可 parse(本輪用
# 真的 3.9.25 compile 過);markdown-it-py==4.0.0 的**執行地板**是 3.12+,
# 由 doctor `printer-python` 查,不把編譯地板偷偷升到 3.12。
# 改編譯下限要同時改 README 環境需求段;改執行地板要同時改 doctor 與 README。
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
import re
import subprocess
import sys
import tempfile

root = sys.argv[1]

# ── 宣告下限 ──────────────────────────────────────────────────────────────
# 3.9 = hook／.py 編譯地板(printers 仍可 parse)。macOS /usr/bin/python3 常是 3.9;
# 那只夠跑 hook,不夠裝 markdown-it-py 4。執行地板 3.12+ 見 doctor printer-python。
# 不要叫人覆寫 Apple 系統 Python。
PY_FLOOR = (3, 9)

plugin_md = open(os.path.join(root, "docs", "PLUGIN.md"), encoding="utf-8").read()
skill = open(os.path.join(root, "skills", "dev-setup", "SKILL.md"), encoding="utf-8").read()
doc_fails = []
if "3.9" not in plugin_md:
    doc_fails.append("docs/PLUGIN.md 沒宣告編譯下限 3.9")
if "3.12" not in plugin_md or "markdown-it-py" not in plugin_md:
    doc_fails.append("docs/PLUGIN.md 沒宣告產圖執行地板 3.12+／markdown-it-py")
if "venv" not in plugin_md or "不要覆寫" not in plugin_md:
    doc_fails.append("docs/PLUGIN.md 沒要求專案 venv、也沒寫不要覆寫系統 Python")
if "3.12" not in skill or "不要覆寫" not in skill or "venv" not in skill:
    doc_fails.append("SKILL.md 沒把 3.12+／專案 venv／不要覆寫系統 Python 寫進安裝前提")
if doc_fails:
    print("⛔ Python 地板文件與實作不一致:", file=sys.stderr)
    for item in doc_fails:
        print("   " + item, file=sys.stderr)
    sys.exit(1)

# ── 要驗哪些檔 ───────────────────────────────────────────────────────────
# 全部收:hooks/ 與 docs/dev/tools/ 是採用專案真的會跑的;scripts/ 與 observability/
# 雖然只在母版跑,但同一個寫法在這裡出現過就會被抄到會散發的檔案裡(2026-08-19 實際
# 就是 scripts/ 與 docs/dev/tools/ 各一份同時中),所以一起釘。
PATTERNS = ["hooks/*.py", "scripts/*.py", "observability/*.py",
            "memory/*.py", "docs/dev/tools/*.py"]
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

# ── 要驗哪些 heredoc ─────────────────────────────────────────────────────
# scripts/、hooks/ 的 .sh 常見手法:`python3 - <<'PY' ... PY` 內嵌一整段 Python。
# 那段內容不是 .py 檔,上面那組 .py 掃描完全看不到它 —— 2026-08-19 那次事故
# (check-gate-twin.sh heredoc 裡的 f-string 反斜線,3.12 才合法)就是從這個
# 缺口漏過去的,全部既有 .py 檢查皆綠。
SH_PATTERNS = ["scripts/*.sh", "hooks/*.sh"]
out_sh = subprocess.run(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", *SH_PATTERNS],
    cwd=root, capture_output=True, text=True)
if out_sh.returncode != 0:
    print(f"⛔ git ls-files(.sh)失敗:{out_sh.stderr.strip()}", file=sys.stderr)
    sys.exit(2)
sh_files = sorted(f for f in out_sh.stdout.split() if f.endswith(".sh"))
if not sh_files:
    print("⛔ 掃到零個 .sh —— 檢查沒有真的跑到東西(SH_PATTERNS 壞了或 repo 空的)",
          file=sys.stderr)
    sys.exit(2)

# heredoc 起頭:`python3`/`python` 後面接 `<<'PY'`(或 PYTHON/EOF_PY/PYEOF,可加
# `-` 用 `<<-` 讓終止行允許前導 tab)。只吃**有引號**的 delimiter —— 無引號的
# heredoc 內容進 shell 前會先展開 `$VAR`/反引號,抽出來的字串已經不是原始碼字面
# 值,拿去 compile 只會誤判,所以跳過並計數,既不算過也不算 FAIL。
HEREDOC_OPEN_RE = re.compile(
    r"python3?\b.*<<(-)?\s*(['\"]?)(PY|PYTHON|EOF_PY|PYEOF)\2")


def find_heredocs(src_lines):
    """掃一支檔案的行陣列,回傳 [(起始行號 1-based, tag, 有無引號, body 行陣列)]。
    body 用 None 代表「找不到對應結尾標記」(呼叫端要另外記一筆失敗,不是靜默跳過)。"""
    out = []
    i, n = 0, len(src_lines)
    while i < n:
        m = HEREDOC_OPEN_RE.search(src_lines[i])
        if not m:
            i += 1
            continue
        dash, quote, tag = m.group(1), m.group(2), m.group(3)
        open_no = i + 1
        j = i + 1
        body = []
        end_no = None
        while j < n:
            probe = src_lines[j]
            term = probe.lstrip("\t") if dash else probe
            if term == tag:
                end_no = j + 1
                break
            body.append(probe.lstrip("\t") if dash else probe)
            j += 1
        out.append((open_no, tag, bool(quote), body if end_no else None))
        i = (j + 1) if end_no else n
    return out


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
heredoc_checked = 0
heredoc_skipped = 0

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

    # ── heredoc 掃描:scripts/、hooks/ 的 .sh 裡 python3 <<'PY' 內嵌片段 ──────
    # 寫到暫存檔(不進 repo,不留 __pycache__)用同一支下限直譯器的 `-m py_compile`
    # 真的編一遍;temp 檔前面補跟 heredoc 起始行等量的空白行,py_compile 回報的行號
    # 就直接對得上 .sh 檔案的行號,不用另外做 offset 換算。
    with tempfile.TemporaryDirectory(prefix="devflow-py-floor-heredoc-") as heredoc_dir:
        for rel in sh_files:
            src_lines = open(os.path.join(root, rel), encoding="utf-8").read().split("\n")
            for open_no, tag, quoted, body in find_heredocs(src_lines):
                if body is None:
                    failures.append(
                        f"{rel}:第 {open_no} 行 heredoc(<<'{tag}')找不到對應結尾標記,"
                        "無法解析")
                    continue
                if not quoted:
                    heredoc_skipped += 1
                    continue
                heredoc_checked += 1
                padded = ("\n" * open_no) + "\n".join(body) + "\n"
                tmp_path = os.path.join(heredoc_dir, f"h{heredoc_checked}.py")
                with open(tmp_path, "w", encoding="utf-8") as tf:
                    tf.write(padded)
                r = subprocess.run(
                    [floor_exe, "-m", "py_compile", tmp_path],
                    capture_output=True, text=True)
                if r.returncode != 0:
                    tail = (r.stderr.strip().splitlines() or ["(無 stderr)"])[-1]
                    failures.append(
                        f"{rel}:第 {open_no} 行起的 heredoc 在 Python "
                        f"{floor_ver[0]}.{floor_ver[1]} 編譯不過 —— {tail}")

    # 掃到零個 heredoc 跟掃到零個 .py 同等級:pattern 壞了或漏檔,不能悄悄放行。
    if heredoc_checked == 0:
        print("⛔ 掃到零個 heredoc —— 檢查沒有真的跑到東西(pattern 壞了或 repo 缺檔)",
              file=sys.stderr)
        sys.exit(2)
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

# ⚠️ 成功訊息一律報**實際用到的版本**,不准報 PY_FLOOR。
# 起因(2026-08-19,由 dev-flow:devflow-adviser 唯讀複核抓到):接受區間是
# PY_FLOOR ~ 3.11,但舊版訊息把 PY_FLOOR 寫死進 ✅ 那一行 —— 當下若只找到 3.11,
# 實際上沒有任何東西驗過 3.9,而 gate log 抓走的通常就是 ✅ 那一行,於是
# 「用 3.10+ 才有的語法」會照過、訊息卻宣稱 3.9 皆可解析。
# 這正是本檔頂註在防的「沒驗到就說綠」,只是換了個地方發作。
used = f"{floor_ver[0]}.{floor_ver[1]}"
floor_s = f"{PY_FLOOR[0]}.{PY_FLOOR[1]}"
gap = "" if floor_ver == PY_FLOOR else (
    f";⚠️ 這一輪**沒有**真的驗到 {floor_s} —— 本機找不到那個版本,"
    f"只驗到 {used}。{floor_s} 到 {used} 之間新增的語法不會被抓到")
print(f"=== Python 下限相容(宣告下限 {floor_s},本輪實際用 {used}):驗了 {checked} 個 .py ===")
print(f"=== heredoc 下限相容:掃了 {heredoc_checked} 個 heredoc"
      f"(略過 {heredoc_skipped} 個無引號 delimiter)===")
if failures:
    print(f"❌ {len(failures)} 項不符:")
    for f in failures:
        print(f"   {f}")
    print("   修法:把值落成變數再進 f-string;或改 PY_FLOOR 並同步 README 環境需求段。")
    sys.exit(1)
print(f"✅ {checked} 個 .py 在 Python {used} 下皆可解析{gap}")
PY
