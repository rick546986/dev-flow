#!/bin/bash
# check-devtalk-guide-sync.sh — guide-dev-talk.html 與 skills/dev-talk/SKILL.md 之間的
# 引用同步守衛(第 7 型「不對稱記帳」,2026-08-17)。
#
# 為什麼需要:skills/dev-talk/SKILL.md 是 dev-talk 這個 skill 唯一的方法正本
# (見該檔頭「方法全部內建於本檔,本檔是你唯一的方法來源」)。guides/guide-dev-talk.html
# 是它的乘客手冊/導覽頁 —— 一份鏡像文件,理論上只是把正本翻譯成好讀的表格與圖。
# 但這面鏡子沒有任何機制強迫它跟著正本走:2026-08-17 盤點發現兩處真實漂移 ——
#   ①guide 的「全程地圖」寫 11 步,SKILL.md 執行清單其實是 0-11 共 12 步 ——
#     guide 漏了「真實世界互動盤點」整整一步,全文對這步(Real-world/Workarounds)
#     零命中;
#   ②guide 多處標「原文」的逐字引用,其中一段寫「步 8 對帳」,SKILL.md 現文其實是
#     「步 9 對帳」—— 標了「原文」卻引錯正本,比沒標引用更危險(讀者會照單全收)。
# 這正是「機制(SKILL.md)改了,鏡像它的導覽(guide)沒跟上,且無守衛」的第 7 型
# 不對稱記帳:改 SKILL.md 的人沒有義務同時去核對 guide 的每一段引用與步數,靜默
# 漂移不會有任何紅字。本守衛把「引用不對」與「步數不對」都變成機械檢查。
#
# 做兩件事(對應上面兩種真實漂移):
#   A. 逐字引用:guide 內每一段標「原文」的 <blockquote>,HTML 去標籤 + unescape
#      實體之後,必須是 SKILL.md(去 markdown 強調記號)之後的逐字子字串 —— 抓
#      「標了原文卻引錯正本」。兩側都先「去格式、去空白」再比對子字串,原因:
#        - guide 端 **粗體**/`code`/_斜體_ 在轉成 HTML 時變成 <strong>/<code>/<em>,
#          去標籤後這些強調記號本來就會消失,SKILL.md 端若保留 markdown 記號
#          (**/`/_)不去掉,兩側逐字比對永遠對不上,是比對本身的假陽性,不是真漂移。
#        - guide 端的 <br> 換行位置本來就不必、也不會跟 SKILL.md 原始的 78 字自動
#          換行位置一致(guide 是另外排版的 HTML,不是逐行照抄) —— 若只 collapse
#          空白成單一空格仍可能因為兩側斷行不同插入的空格位置不同而誤判不符,
#          乾脆把所有空白整個刪除(不留任何空格)比對最穩:中文本來就沒有詞間空
#          格,英文詞組(如 "unknown unknowns")兩側都會變成
#          "unknownunknowns",子字串測試依然成立,失敗模式最少。
#      去標籤與去實體的順序:先去 HTML 標籤、再 unescape 實體 —— 反過來的話
#      `&lt;` 這類實體被還原成 `<` 之後可能被誤認成標籤起點,把後面的內容吃掉。
#   B. 步數一致:SKILL.md 執行清單的步驟數,與 guide 全程地圖(② 標題數字 + 步驟
#      表列數)的步驟數必須相等 —— 抓「guide 少列/多列了幾步」。兩側都各自用
#      「兩種各自獨立的解析方式」互相印證,兩種方式對不上就是解析本身不可信
#      (parse 沒有真的跑對),fail-closed 不猜是哪個數字對:
#        - SKILL.md:①「把 N-M 建成 todo」的範圍字面(執行清單開場白就有寫)
#                    ②逐行列舉 `^\d+\. **標題**` 數出多少個獨立步驟
#        - guide   :①「② 全程地圖(N 步)」標題數字
#                    ②全程地圖後那張步驟表裡,「非 colspan(即非「原文」展開列)」
#                      的 <tr> 列數(每步一列)
#
# fail-closed(exit 2,不是「沒有漂移」,是「檢查沒真的跑」):
#   - guide 裡一段「原文」標記都找不到(dev-talk 的導覽一直都有這個慣例,
#     找不到代表擷取窗口本身壞了,不是它剛好沒有引用)
#   - SKILL.md 或 guide 任一側的步數解析結果為 0
#   - 同一側(SKILL.md 內部、或 guide 內部)的兩種獨立解析方式互不相同
#     (parse 本身不可信,不猜哪個數字對)
#
# 用法:
#   scripts/check-devtalk-guide-sync.sh [root]   # 缺省 root = repo root
# root 可指向 /private/tmp 下的複本,供破壞實驗(mutation test)使用,不動真檔。
#
# exit:0 = 引用與步數皆同步 / 1 = 真漂移(列出哪一段/哪個數字對不上)/
#      2 = 檢查自身故障(NOT-PARSED,見上)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import html
import re
import sys

# 行緩衝:先看計數、再看 exit code 的順序若被 stdout/stderr 各自預設緩衝打亂,
# 計數行可能被 fail 訊息蓋過(見 check-guides-fig-sync.sh 同款教訓)。
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root = sys.argv[1]

SKILL_PATH = f"{root}/skills/dev-talk/SKILL.md"
GUIDE_PATH = f"{root}/guides/guide-dev-talk.html"

import os
for p in (SKILL_PATH, GUIDE_PATH):
    if not os.path.isfile(p):
        print(f"FATAL: 找不到 {p}", file=sys.stderr)
        sys.exit(2)

skill_text = open(SKILL_PATH, encoding="utf-8").read()
guide_text = open(GUIDE_PATH, encoding="utf-8").read()


# ─────────────────────────── 正規化(assertion A 共用)───────────────────────
def normalize_skill(text):
    """去 markdown 強調記號(**粗體**/`code`/_斜體_)再去全部空白。
    只認這三種記號,理由見頂註——SKILL.md 全文檢查過,`_..._` 僅出現一次
    (_Avoid_),沒有其他合法底線用途會被誤傷;若未來 SKILL.md 新增底線用法
    (例如檔名內底線),這條正規化規則需要一併檢視,不是本檢查的隱藏假設。
    """
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    text = re.sub(r"\s+", "", text)
    return text


def normalize_guide_fragment(frag):
    """去 HTML 標籤 → unescape 實體 → 去全部空白。順序不可換(見頂註)。"""
    text = re.sub(r"<[^>]+>", "", frag)
    text = html.unescape(text)
    text = re.sub(r"\s+", "", text)
    return text


skill_normalized = normalize_skill(skill_text)

if not skill_normalized:
    print("FATAL: SKILL.md 正規化後為空字串(NOT-PARSED)", file=sys.stderr)
    sys.exit(2)


# ─────────────────────────── assertion A:逐字引用 ───────────────────────────
QUOTE_RE = re.compile(
    r"<summary>原文</summary><blockquote>(.*?)</blockquote>", re.DOTALL
)
quotes = QUOTE_RE.findall(guide_text)

print(f"[quote] guide 內「原文」標記段數 = {len(quotes)}")

if len(quotes) == 0:
    print(
        "FATAL: guide 裡找不到任何「原文」標記(NOT-PARSED,不是「沒有漂移」——"
        "dev-talk 導覽一直有這個慣例,找不到代表擷取窗口本身壞了)",
        file=sys.stderr,
    )
    sys.exit(2)

quote_failures = []
for idx, raw in enumerate(quotes):
    normalized = normalize_guide_fragment(raw)
    if not normalized:
        print(f"FATAL: 第 {idx} 段「原文」正規化後為空字串(NOT-PARSED)", file=sys.stderr)
        sys.exit(2)
    if normalized not in skill_normalized:
        # 給人看的上下文:只去標籤,不去空白,截斷到可讀長度
        readable = re.sub(r"<[^>]+>", "", raw)
        readable = html.unescape(readable)
        readable = re.sub(r"\s+", " ", readable).strip()
        quote_failures.append((idx, readable[:160]))


# ─────────────────────────── assertion B:步數一致 ───────────────────────────
# SKILL.md 側,方法①:執行清單開場白「把 N-M 建成 todo」
m = re.search(r"把\s*(\d+)-(\d+)\s*建成\s*todo", skill_text)
if not m:
    print(
        "FATAL: SKILL.md 找不到「把 N-M 建成 todo」開場白(NOT-PARSED,步數解析方法①失敗)",
        file=sys.stderr,
    )
    sys.exit(2)
skill_range_count = int(m.group(2)) - int(m.group(1)) + 1

# SKILL.md 側,方法②:逐行列舉 `^N. **標題**`
skill_enum_steps = re.findall(r"^(\d+)\.\s+\*\*", skill_text, re.MULTILINE)
skill_enum_count = len(skill_enum_steps)

print(f"[skill] 方法①「N-M 建成 todo」解析步數 = {skill_range_count}")
print(f"[skill] 方法②逐行列舉步驟解析步數     = {skill_enum_count}")

if skill_range_count == 0 or skill_enum_count == 0:
    print("FATAL: SKILL.md 步數解析結果為 0(NOT-PARSED)", file=sys.stderr)
    sys.exit(2)
if skill_range_count != skill_enum_count:
    print(
        f"FATAL: SKILL.md 內部兩種步數解析方式互不相同"
        f"(①={skill_range_count} ②={skill_enum_count})—— parse 本身不可信,"
        "不猜哪個數字對(NOT-PARSED)",
        file=sys.stderr,
    )
    sys.exit(2)

# guide 側,方法①:「② 全程地圖(N 步)」標題(錨在 <h2 id="map"> 上,避免命中
# nav 那行同樣文字的重複片語——nav 與 h2 理應一致,但錨定 h2 才是解析的權威來源)
m2 = re.search(r'<h2 id="map">.*?全程地圖\((\d+)\s*步\)</h2>', guide_text)
if not m2:
    print(
        'FATAL: guide 找不到 <h2 id="map">…全程地圖(N 步)</h2>(NOT-PARSED,'
        "guide 側步數解析方法①失敗)",
        file=sys.stderr,
    )
    sys.exit(2)
guide_heading_count = int(m2.group(1))

# guide 側,方法②:全程地圖之後、實例走一遍之前的步驟表,數非 colspan 的 <tr> 列
# (colspan="4" 那列是「原文」展開列,不是獨立步驟,不能算進步數)
try:
    seg_start = guide_text.index('<h2 id="map">')
    seg_end = guide_text.index("<h3>實例走一遍")
except ValueError:
    print(
        "FATAL: guide 找不到全程地圖區塊或「實例走一遍」標題,步驟表擷取窗口不可信"
        "(NOT-PARSED)",
        file=sys.stderr,
    )
    sys.exit(2)
segment = guide_text[seg_start:seg_end]
guide_row_steps = re.findall(r"<tr><td>(\d+)\s[^<]*</td><td>", segment)
guide_row_count = len(guide_row_steps)

print(f"[guide] 方法①「② 全程地圖(N 步)」標題解析步數 = {guide_heading_count}")
print(f"[guide] 方法②步驟表非展開列列數                = {guide_row_count}")

if guide_heading_count == 0 or guide_row_count == 0:
    print("FATAL: guide 步數解析結果為 0(NOT-PARSED)", file=sys.stderr)
    sys.exit(2)
if guide_heading_count != guide_row_count:
    print(
        f"FATAL: guide 內部兩種步數解析方式互不相同"
        f"(①={guide_heading_count} ②={guide_row_count})—— parse 本身不可信,"
        "不猜哪個數字對(NOT-PARSED)",
        file=sys.stderr,
    )
    sys.exit(2)

skill_step_count = skill_range_count
guide_step_count = guide_heading_count
step_count_mismatch = skill_step_count != guide_step_count


# ─────────────────────────────────── 結論 ───────────────────────────────────
FAILURES = []

if quote_failures:
    msg = [f"[quote] ❌ {len(quote_failures)} 段「原文」與 SKILL.md 現文不符(錯引正本):"]
    for idx, readable in quote_failures:
        msg.append(f"        第 {idx} 段:{readable}...")
    msg.append("        修法:把 guide 這段「原文」改成與 SKILL.md 現文逐字一致"
               "(SKILL.md 是唯一正本,不得反向修改 SKILL.md 遷就 guide)。")
    FAILURES.append("\n".join(msg))
else:
    print(f"[quote] ✅ {len(quotes)} 段「原文」皆與 SKILL.md 現文逐字相符(正規化後子字串比對)。")

if step_count_mismatch:
    FAILURES.append(
        f"[steps] ❌ 步數漂移:SKILL.md 執行清單共 {skill_step_count} 步,"
        f"guide 全程地圖卻是 {guide_step_count} 步——guide 少列或多列了步驟"
        "(常見成因:SKILL.md 新增/刪除一步,guide 的地圖與步驟表沒有同步跟上)。"
    )
else:
    print(f"[steps] ✅ SKILL.md 與 guide 步數一致,皆為 {skill_step_count} 步。")

if FAILURES:
    print(file=sys.stderr)
    for f in FAILURES:
        print(f, file=sys.stderr)
    sys.exit(1)

print("✅ PASS:guide-dev-talk.html 與 skills/dev-talk/SKILL.md 逐字引用與步數皆同步。")
sys.exit(0)
PY
