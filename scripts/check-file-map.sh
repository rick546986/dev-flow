#!/bin/bash
# 檔案地圖雙向盤點守衛(Repo-local)。
#
# guides/guide-dev-flow.html 的「附錄:檔案地圖」節是一張手寫表(每支腳本一句白話職責)。
# 手寫表必腐化——新增/改名/刪除一支腳本後,那張表不會自動跟著動,遲早變成一份好看但
# 不可信的文件。本守衛做雙向盤點:
#
#   ①正向(forward):hooks/、scripts/、observability/、memory/、tests/parallel-stage6/ 底下每個
#     *.sh/*.py(以 git 為準,含尚未 git add 的新檔——用
#     `git ls-files --cached --others --exclude-standard`,不是只認已 commit 的檔)都必須
#     在檔案地圖節(<h2 id="filemap"> 到下一個 <h2 之間)的「檔名」欄被點名——
#     vendor 目錄(hooks/devflow_obs_vendor/)與各 fixtures/ 目錄按「目錄」豁免整包一列,
#     不必逐檔列,豁免會印出來,不是靜默略過。
#   ②反向(reverse):檔案地圖節「檔名」欄裡寫的每一個 <code> 內容,都必須是真實存在的
#     檔案或目錄——防止有人手寫了一個已經改名、或從沒存在過的檔案。
#
# 用法:
#   scripts/check-file-map.sh [root]   # 缺省 root = repo root
# root 可指向 /private/tmp 下的複本,供 test-architecture-guards.sh 的 mutation 驗證
# (root 必須是 git working tree——本檔以 git ls-files 為掃描來源)。
#
# exit:0 = 雙向全過 / 1 = 有缺漏(FAIL)/ 2 = 環境或解析失敗(fail-closed,不猜)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import html
import os
import re
import subprocess
import sys

root = sys.argv[1]
guide = os.path.join(root, "guides", "guide-dev-flow.html")

if not os.path.isfile(guide):
    print(f"FATAL: 找不到 {guide}", file=sys.stderr)
    sys.exit(2)

text = open(guide, encoding="utf-8").read()

# ── 抽「附錄:檔案地圖」節:<h2 id="filemap"> 到下一個 <h2 之間(含頭,不含下一節)──
m = re.search(r'<h2 id="filemap">.*?(?=<h2 |\Z)', text, re.S)
if not m:
    print('FATAL: guide-dev-flow.html 找不到 <h2 id="filemap"> 節', file=sys.stderr)
    sys.exit(2)
section = m.group(0)
if not section.strip():
    print('FATAL: filemap 節內容為空', file=sys.stderr)
    sys.exit(2)

# ── 正向掃描來源:git ls-files(含尚未 add 的新檔,不含 .gitignore 排除的東西)──────
# `agents/*.md`(2026-08-19 派工單 §4.4 第 5 項新增):先前 PATTERNS 完全不含 `.md`,
# 加之前實測過 `git ls-files ... 'agents/*.md'` 只命中 agents/ 目錄下兩檔(不像
# shell glob 的 `*` 可能跨目錄漂移吃進其他 .md),才敢直接加、不必再收窄成明列
# 兩個檔名——若之後 agents/ 底下出現子目錄,行為要重新實測,不能假設。
PATTERNS = [
    "hooks/*.sh", "hooks/*.py",
    "scripts/*.sh", "scripts/*.py",
    "observability/*.sh", "observability/*.py",
    "memory/*.sh", "memory/*.py",
    "tests/parallel-stage6/*.py",
    "agents/*.md",
]
out = subprocess.run(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", *PATTERNS],
    cwd=root, capture_output=True, text=True,
)
if out.returncode != 0:
    print(f"FATAL: git ls-files 失敗(root 不是 git working tree?):{out.stderr.strip()}",
          file=sys.stderr)
    sys.exit(2)
all_files = sorted({f for f in out.stdout.splitlines() if f})

EXEMPT_PREFIXES = [
    "hooks/devflow_obs_vendor/",
    "scripts/fixtures/",
    "observability/fixtures/",
    "memory/fixtures/",
    "tests/parallel-stage6/fixtures/",
]

required = []
exempted = []
for f in all_files:
    if any(f.startswith(p) for p in EXEMPT_PREFIXES):
        exempted.append(f)
    else:
        required.append(f)

scanned = len(required)
print(f"scanned={scanned} exempted={len(exempted)}")

if scanned == 0:
    print("FATAL: 掃到 0 支必列檔,守衛沒有真的跑——不是「沒有缺陷」", file=sys.stderr)
    sys.exit(2)

# 必列檔數精確值(不是地板):它數的是「必須列進檔案地圖的檔案數」。
# 舊版註解寫「一律等於當下實際值」但程式碼只驗「小於」—— 實得數從 68 漂到 74
# 一路綠燈,防第 7 型(清單沒跟著長)的守衛自己成了活標本(2026-08-18 S-2)。
# 現值以實跑輸出為準:`bash scripts/check-file-map.sh` 第一行的 `scanned=` 就是它。
# ⚠️ 這裡刻意不寫「= hooks N + observability N + scripts N + …」的分解。舊註解寫過
# 一份,常數從 77 調到 78 時分解沒跟著改,而且它在那之前就已經算錯(hooks 實際 25
# 卻寫 22、scripts 實際 34 卻寫 36)—— 守衛比的是常數不是註解,錯的分解照樣全綠,
# 下一個做同樣記帳的人卻會照著它算。分解只會爛,要數字就跑一次(2026-08-18 E-3)。
# 新增/刪除必列檔時同步改這個常數(並同步補/刪檔案地圖節對應列),還要同步改
# test-architecture-guards.sh 的靜態互釘清單那一行 —— 只改這裡不改那裡,砍檢查數
# 會在那裡現形;只改那裡不改這裡,這裡的數字跟實得數脫鉤,防線形同虛設。
EXPECTED_MAPPED_FILES = 186
if scanned != EXPECTED_MAPPED_FILES:
    direction = ("多了 —— 若為真實新增,請同步上修本常數並補檔案地圖對應列"
                 if scanned > EXPECTED_MAPPED_FILES
                 else "少了 —— 若為真實刪檔,請同步下修本常數並確認檔案地圖節移除對應列")
    print(f"FAIL: 掃到 {scanned} 支 ≠ EXPECTED_MAPPED_FILES={EXPECTED_MAPPED_FILES},"
          f"{direction}", file=sys.stderr)
    sys.exit(1)

print("── 豁免目錄(按目錄整包一列,不逐檔要求)──")
for p in EXEMPT_PREFIXES:
    n = sum(1 for f in exempted if f.startswith(p))
    print(f"  豁免:{p}({n} 檔)")
print()

# ── 從「檔名」欄(每列第一個 <td>)抽 <code> 內容;不掃第二/三欄,避免第三欄
# (誰呼叫它/掛在哪)裡提到的 hooks.json 之類無關檔名被誤判 ──────────────────────
row_cells = re.findall(r'<tr>\s*<td>(.*?)</td>', section, re.S)
table_rows = len(row_cells)
print(f"table_rows={table_rows}")
if table_rows == 0:
    print("FATAL: 檔案地圖節解析到 0 列(<tr><td> 找不到)——不是「表是空的」,"
          "是解析沒跑,先檢查 HTML 結構", file=sys.stderr)
    sys.exit(2)

filemap_codes = set()
for cell in row_cells:
    for c in re.findall(r'<code>(.*?)</code>', cell, re.S):
        tok = html.unescape(c).strip()
        if tok:
            filemap_codes.add(tok)

if not filemap_codes:
    print("FATAL: 檔案地圖節「檔名」欄解析到 0 個 <code> token——解析沒跑", file=sys.stderr)
    sys.exit(2)

BUNDLE_TOKENS = [
    "hooks/devflow_obs_vendor/",
    "scripts/fixtures/",
    "observability/fixtures/",
    "memory/fixtures/",
    "tests/parallel-stage6/fixtures/",
    "scripts/requirements-methodology-render.txt",
]

failures = []

# ①正向:每個必列檔的 basename 必須是「檔名」欄某個 <code> 的精確內容(集合成員判斷,
# 不是子字串搜尋——observability/devflow_obs/stats.py 與 observability/tests/test_stats.py
# 這類「短檔名是長檔名字尾」的組合,子字串搜尋會把兩者混淆造成假陰性漏報)。
for f in required:
    base = os.path.basename(f)
    if base not in filemap_codes:
        failures.append(f"forward 缺列:{f}(檔案存在,檔案地圖節「檔名」欄找不到 `{base}`)")

for tok in BUNDLE_TOKENS:
    if tok not in filemap_codes:
        failures.append(f"forward 缺 bundle 列:找不到 `{tok}`"
                         "(vendor/fixtures/requirements 整包列被刪或改了字面)")

# ②反向:「檔名」欄裡的每個 token,必須是真實存在的檔案或目錄。
all_basenames = {os.path.basename(f) for f in required} | {os.path.basename(f) for f in exempted}
checked = 0
for tok in sorted(filemap_codes):
    if re.search(r'[一-鿿]', tok):
        continue  # 附註文字誤入 <code>,不是檔名,跳過
    checked += 1
    if tok.endswith("/"):
        ok = os.path.isdir(os.path.join(root, tok))
    elif "/" in tok:
        ok = os.path.isfile(os.path.join(root, tok))
    else:
        ok = tok in all_basenames
    if not ok:
        failures.append(f"reverse 不存在:`{tok}`(檔案地圖節寫了但真實找不到對應檔案/目錄)")

print(f"reverse: 「檔名」欄實查 {checked} 個 token")
print()

if failures:
    print(f"❌ FAIL:{len(failures)} 項違規")
    for x in failures:
        print(f"  - {x}")
    sys.exit(1)

print(f"✅ PASS:forward {scanned} 支必列檔 + {len(BUNDLE_TOKENS)} 個 bundle 列全部在「檔名」欄"
      f"命中;reverse {checked} 個 token 全部真實存在。")
sys.exit(0)
PY
