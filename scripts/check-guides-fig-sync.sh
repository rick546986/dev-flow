#!/bin/bash
# 兩份導覽的生命週期圖同步守衛(Repo-local)。
#
# 為什麼是「雙副本 + 守衛」而不是「單正本 + 引用/縮減版」:
#   guides/guide-dev-flow.html 的 <svg id="fig-lifecycle"> 與
#   guides/guide-quickstart.html 的 <svg id="fig-lifecycle-qs"> 是同一張 Claude Code
#   agent 生命週期圖的兩份完整複製體 —— owner 已明確裁決(見
#   notes/dispatch-guard-symmetry.md X-6):兩份導覽各自都要放「全圖」,quickstart
#   不接受縮減版/連結取代,因為 quickstart 讀者不見得會去翻 guide-dev-flow.html。
#   單正本(只放一份 + 用連結/iframe 帶過)會犧牲 quickstart 的自足性,owner 不採。
#   但雙副本天生會漂移(改一張、忘了改另一張,靜默發生、沒有任何檢查會紅)——這正是
#   本 repo「假綠第⑥型(不對稱保護:只對某檔/某群組補防線,同類的另一份沒有)」的
#   預防案例:與其等它真的漂移了才發現,先補這支同步守衛。
#
# ⚠️ 覆蓋邊界(說不出理由就該推廣或列 Backlog——這裡把理由寫清楚,別讓本檔自己
#    也變成「只對某個實例補防線」的反例):
#   - 已用 `grep -rn 'fig-lifecycle\|<svg id=' guides/ docs/ _templates/ example/`
#     核對過:整個 repo 只有這兩份導覽各嵌一份這張生命週期圖的複製體,沒有第三份
#     (guide-dev-talk.html / dev-setup-record.html 裡的 <svg id=…> 是完全不同的圖,
#     不是同一張圖的複製體;_templates/diagram-style.md 只是提到這兩份圖當範例,
#     不是第三份圖的複製體)。若日後任何地方再多嵌一份這張圖的複製體,必須把它
#     一併納入本檢查,或在這裡寫明為什麼那份不算數——不接受悄悄漏掉。
#   - 本檢查涵蓋**三層**,不是只比 svg 標記:①svg 標記本身(見下①)②渲染這張圖用
#     到的 CSS 規則區塊(見下②)③三份 guides 共用的頁內錨點捲動 JS(見下③)。只比
#     svg、不比 CSS 的話,兩邊 svg 標記逐位元組相同、但其中一邊的
#     `.hk`/`.att`/`.loopscope`/`edge-*` 等規則被單獨改壞,圖會渲染成兩個不同的
#     東西,本守衛卻還是綠燈——這正是同一種「不對稱保護」的漏洞換了一層皮再犯
#     一次,所以三層都要顧。
#   - **誠實邊界**(2026-08-17 補,X-6 MED):本檢查是比較型守衛——比的是「兩邊/
#     三邊彼此是否一致」,天生抓不到「兩邊同步同樣改壞」的情形(例如有人把
#     dev-flow 與 quickstart 的同一段規則,同時改成同一個錯的值)。本守衛防的是
#     **單邊漂移**(假綠第⑥型:不對稱保護,只有一邊被改、另一邊沒跟上),不防
#     **雙邊一致的錯誤**——那是另一種問題(內容正確性),要靠別的檢查或人工審查
#     顧,不是本檢查的職責範圍,說清楚以免誤以為本守衛=內容正確性保證。
#
# 做三件事:
#   ①svg 標記:從兩份導覽各自抽出生命週期圖的 <svg id="...">…</svg> 區塊,正規化掉
#     頂層 id 的預期差異後逐位元組比對。抽取本身是**深度感知**的(見 extract_svg
#     內註解)——不是天真地找第一個 </svg> 就當結尾,巢狀 <svg> 會被 fail-closed
#     擋下來,不會被截斷成一段看似能比對、實則漏掉真漂移的殘缺區塊。
#   ②CSS 規則:從兩份導覽各自抽出繪這張圖專用的 CSS 區塊(以雙生註解為錨點),
#     去掉純註解行/空白行後逐行比對規則本身(兩邊的註解文字本來就不同——dev-flow
#     那份有逐條中文說明、quickstart 那份沒有——這是允許的差異,規則才是要顧的東西)。
#     錨點文字本身在各自檔案內必須恰好出現 1 次,不唯一就代表擷取窗口不可信,
#     fail-closed,不猜是哪一次命中。
#   ③JS 規則:從三份 guides(guide-dev-flow / guide-quickstart / guide-dev-talk)各自
#     以頁內錨點捲動修正的 HTML 註解為錨點,抽出其後的 <script>…</script> 區塊,
#     三份逐位元組比對必須相同(這段 JS 沒有預期差異、不需要正規化)。
#   任一邊抽取失敗(找不到錨點、錨點不唯一、regex 沒命中)或抽到空內容
#   → exit 2(NOT-PARSED,見下)。正規化/去註解後仍不同 = 真漂移 → FAIL,並印出
#   第一個差異點的上下文,點名差在哪。
#
# 用法:
#   scripts/check-guides-fig-sync.sh [root]   # 缺省 root = repo root
# root 可指向 /private/tmp 下的複本,供 test-architecture-guards.sh 的 mutation 驗證。
#
# exit:0 = 三層都同步 / 1 = 至少一層正規化後仍有差異(FAIL)/
#      2 = 抽取失敗、錨點不唯一、或解析到空內容(fail-closed,不猜)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import difflib
import os
import re
import sys

# 行緩衝:FAIL 訊息走 stderr、計數走 stdout,兩者若混用預設緩衝在管線/CI log 裡會
# 讓 stderr(通常不緩衝)搶先印出、蓋過本應先出現的計數行——與本檔遵循的「先看
# 計數,再看 exit code」順序相反。逼兩邊都用行緩衝,順序才會照程式碼寫的順序落地。
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root = sys.argv[1]

DEVFLOW_HTML = os.path.join(root, "guides", "guide-dev-flow.html")
QUICKSTART_HTML = os.path.join(root, "guides", "guide-quickstart.html")
DEVTALK_HTML = os.path.join(root, "guides", "guide-dev-talk.html")
DEVFLOW_SVG_ID = "fig-lifecycle"
QUICKSTART_SVG_ID = "fig-lifecycle-qs"

for path in (DEVFLOW_HTML, QUICKSTART_HTML, DEVTALK_HTML):
    if not os.path.isfile(path):
        print(f"FATAL: 找不到 {path}", file=sys.stderr)
        sys.exit(2)

FAILURES = []  # 累積兩層各自的 FAIL 訊息,兩層都跑完才一次回報,不 fail-fast 漏看另一層


# ─────────────────────────────── ①svg 標記 ───────────────────────────────
# 2026-08-17 補(X-6 HIGH,抽取截斷):舊版用非貪婪 regex
# `<svg id="{id}"[^>]*>.*?</svg>` 找「第一個 </svg>」當結尾——如果這張圖的內容裡
# 未來被(不管是不是惡意)塞進任何巢狀 <svg>(例如內嵌一個 icon 用的 <svg>…</svg>),
# 非貪婪比對會在那個巢狀 svg 的收尾就停下,把外層真正的圖截斷成一小段。截斷後的
# 殘缺區塊仍可能兩邊都「看起來一致」(因為兩邊都被同樣截斷、且截斷點之前恰好相同),
# 於是真正的漂移(藏在截斷點之後、沒被抽到的內容裡)完全不會被比對到,守衛卻回報
# PASS——這是實測驗證過的假綠(worktree 重現:對稱插入巢狀假 svg + 單邊真實文字
# 漂移,舊版逃逸)。
#
# 修法:深度感知掃描,不再相信「第一個 </svg>」。從起始標籤之後逐一尋找
# <svg ...> / </svg> 兩種 token,遇開頭深度 +1、遇收尾深度 -1,直到深度歸零才是
# 真正的結尾。掃描過程中深度若曾經 > 1(代表遇到巢狀 <svg>),代表這張圖的內容
# 結構超出本檢查抽取邏輯原先假設的「扁平、不巢狀」前提——**不嘗試聰明處理**
# (例如硬選最後一個 </svg>、或忽略巢狀內容),直接 fail-closed:exit 2,叫人來看,
# 因為此時「兩邊抽出來的區塊是否真的對應同一段內容」已經無法只憑這支腳本判斷。
def extract_svg(path, svg_id):
    """深度感知抽出 <svg id="{svg_id}" ...>...</svg> 整塊(inclusive)。
    回傳 (block, reason):
      - 成功:(區塊字串, None)
      - 失敗(找不到 / 不平衡 / 巢狀 / id 不唯一):(None, 失敗原因文字)
    呼叫端一律把 block is None 視為抽取失敗,exit 2,不臆測「差異」。
    """
    text = open(path, encoding="utf-8").read()

    # 先斷言:這個 id 的開始標籤在整檔恰好出現一次。不唯一就代表「抽的是哪一個」
    # 本身就是含糊的,擷取窗口不可信,不猜是第幾個命中。
    id_marker = f'<svg id="{svg_id}"'
    id_count = text.count(id_marker)
    if id_count != 1:
        return None, (f'id="{svg_id}" 的開始標籤在整檔出現 {id_count} 次'
                       '(需恰為 1)——擷取窗口不可信')

    start_re = re.compile(re.escape(id_marker) + r'[^>]*>')
    start_m = start_re.search(text)
    if not start_m:
        return None, f'找不到 <svg id="{svg_id}" ...> 開始標籤本身(屬性沒有以 > 收尾?)'

    token_re = re.compile(r'<svg\b[^>]*>|</svg>')
    pos = start_m.end()
    depth = 1
    max_depth = 1
    while depth > 0:
        m = token_re.search(text, pos)
        if not m:
            return None, f'<svg id="{svg_id}"> 找不到對應收尾 </svg>(標籤不平衡)'
        if m.group(0) == '</svg>':
            depth -= 1
        else:
            depth += 1
            max_depth = max(max_depth, depth)
        pos = m.end()

    if max_depth > 1:
        return None, (f'<svg id="{svg_id}"> 區塊內偵測到巢狀 <svg>(深度曾達 {max_depth})'
                       '——結構不支援本檢查的扁平抽取假設,fail-closed,不嘗試聰明處理,人來看')

    return text[start_m.start():pos], None


devflow_svg, devflow_svg_err = extract_svg(DEVFLOW_HTML, DEVFLOW_SVG_ID)
quickstart_svg, quickstart_svg_err = extract_svg(QUICKSTART_HTML, QUICKSTART_SVG_ID)

if devflow_svg is None:
    print(f'FATAL: {DEVFLOW_HTML} 抽取失敗:{devflow_svg_err}'
          '(NOT-PARSED,不是「沒有差異」)', file=sys.stderr)
    sys.exit(2)
if quickstart_svg is None:
    print(f'FATAL: {QUICKSTART_HTML} 抽取失敗:{quickstart_svg_err}'
          '(NOT-PARSED,不是「沒有差異」)', file=sys.stderr)
    sys.exit(2)
if not devflow_svg.strip() or not quickstart_svg.strip():
    print("FATAL: 抽到的 svg 區塊為空字串(NOT-PARSED)", file=sys.stderr)
    sys.exit(2)


# ── 先印計數:任一為 0 = 抽取沒有真的解析到東西,不是「兩邊一樣沒差異」───────────
def svg_counts(block):
    b = len(block.encode("utf-8"))
    nodes = len(re.findall(r"<rect ", block))
    texts = len(re.findall(r"<text", block))
    return b, nodes, texts


df_bytes, df_nodes, df_texts = svg_counts(devflow_svg)
qs_bytes, qs_nodes, qs_texts = svg_counts(quickstart_svg)

print(f"[svg]  guide-dev-flow  fig-lifecycle    : bytes={df_bytes} nodes={df_nodes} texts={df_texts}")
print(f"[svg]  guide-quickstart fig-lifecycle-qs: bytes={qs_bytes} nodes={qs_nodes} texts={qs_texts}")

if df_bytes == 0 or df_nodes == 0 or df_texts == 0:
    print("FATAL: guide-dev-flow.html svg 這側計數為 0——解析沒有真的跑,不是圖本身是空的",
          file=sys.stderr)
    sys.exit(2)
if qs_bytes == 0 or qs_nodes == 0 or qs_texts == 0:
    print("FATAL: guide-quickstart.html svg 這側計數為 0——解析沒有真的跑,不是圖本身是空的",
          file=sys.stderr)
    sys.exit(2)

# 正規化白名單:兩圖之間唯一預期的系統性差異。每條 (pattern, replacement, 理由)
# 都要能說出「為什麼這條差異是預期的、不是漂移」。說不出理由的差異一律不進這份
# 清單——讓它在下面的逐位元組比對現形為 FAIL,而不是被正規化規則悄悄吃掉(這正是
# 防「不對稱保護」要守住的底線:正規化清單本身也要經得起審查,不能變成第二層可以
# 隨手塞例外的地方)。
SVG_NORMALIZE_RULES = [
    (
        re.compile(r'id="fig-lifecycle-qs"'),
        'id="fig-lifecycle"',
        "quickstart 版頂層 svg id 加 -qs 後綴,只是為了避免兩份導覽的內容若被同時"
        "嵌進同一個 DOM(例如預覽/列印合併)時 id 衝突;圖本身內容不因這個後綴而不同。",
    ),
]

quickstart_svg_normalized = quickstart_svg
for pattern, replacement, _reason in SVG_NORMALIZE_RULES:
    quickstart_svg_normalized = pattern.sub(replacement, quickstart_svg_normalized, count=1)

print("[svg]  正規化白名單:")
for pattern, replacement, _reason in SVG_NORMALIZE_RULES:
    print(f"       · {pattern.pattern} → {replacement}")

if devflow_svg == quickstart_svg_normalized:
    print("[svg]  ✅ 正規化後兩張生命週期圖的 svg 標記逐位元組一致"
          f"(白名單套用 {len(SVG_NORMALIZE_RULES)} 條)。")
else:
    sm = difflib.SequenceMatcher(a=devflow_svg, b=quickstart_svg_normalized)
    ctx = None
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            ctx = (i1,
                   devflow_svg[max(0, i1 - 40):i2 + 40],
                   quickstart_svg_normalized[max(0, j1 - 40):j2 + 40])
            break
    msg = ["[svg]  ❌ 正規化後兩張生命週期圖的 svg 標記仍有差異——真實漂移,不是白名單內的預期差異。"]
    if ctx:
        pos, ctx_a, ctx_b = ctx
        msg.append(f"       第一個差異點(devflow 側偏移約 {pos} bytes)")
        msg.append(f"       guide-dev-flow  (正本)側上下文: ...{ctx_a}...")
        msg.append(f"       guide-quickstart(正規化後)側上下文: ...{ctx_b}...")
    msg.append("       修法:以 guide-dev-flow.html 的 fig-lifecycle 為正本,把"
               " guide-quickstart.html 的 fig-lifecycle-qs 同步回一致(只動 svg 區塊)。")
    FAILURES.append("\n".join(msg))


# ─────────────────────────────── ②CSS 規則 ────────────────────────────────
# 兩邊都用同一句雙生註解當錨點——這是作者已經寫在檔案裡、互相點名對方的說明文字,
# 不是本守衛發明的巧合(guide-dev-flow.html:「quickstart 的 fig-lifecycle-qs 雙生」;
# guide-quickstart.html:「雙生自 guide-dev-flow.html 的 fig-lifecycle」)。
DEVFLOW_CSS_START = "fig-lifecycle 全還原版"
DEVFLOW_CSS_END = "Phase 5(伴讀層)新增"   # 下一個 Phase 註解,獨立於本圖,排除在外
QUICKSTART_CSS_START = "fig-lifecycle-qs,雙生自"
QUICKSTART_CSS_END = "</style>"           # quickstart 這段本來就是該 <style> 的最後一塊


# 2026-08-17 補(紀律面 HIGH,CSS 錨點 first-hit):`text.find(marker)` 永遠只找
# 「第一個」命中——如果這句錨點文字在檔案裡不只出現一次(例如同一句說明被複製貼到
# 別的地方,或改版時新增了另一段內容剛好用了同樣的字眼),`find` 默默鎖定的可能是
# 錯的那一個,抽出來的 CSS 區塊就不是本檢查以為的那一段,比對結果不可信、卻不會
# 有任何跡象。修法:抽取前先斷言每個錨點文字在整檔的出現次數恰為 1,不唯一就
# fail-closed(exit 2),不猜是哪一次命中。
def extract_css_block(path, start_marker, end_marker):
    text = open(path, encoding="utf-8").read()

    start_count = text.count(start_marker)
    if start_count != 1:
        return None, (f'起始錨點「{start_marker}」在整檔出現 {start_count} 次'
                       '(需恰為 1)——擷取窗口不可信')
    end_count = text.count(end_marker)
    if end_count != 1:
        return None, (f'結束錨點「{end_marker}」在整檔出現 {end_count} 次'
                       '(需恰為 1)——擷取窗口不可信')

    i = text.find(start_marker)
    # 往回找到該行行首,把整條註解(含 /* ── … ──）都算進區塊,而不是從關鍵字中間截斷
    line_start = text.rfind("\n", 0, i) + 1
    j = text.find(end_marker, i)
    if j == -1:
        return None, f'結束錨點「{end_marker}」出現在起始錨點之前,擷取窗口為空或反向'
    # 同樣退回到 end_marker 所在行的行首,避免切斷 end_marker 前那一行本身
    # (例如 dev-flow 側的下一個 Phase 註解跟本圖註解同一行風格,若切在關鍵字
    # 中間會留下一截沒有收尾的殘破註解行,被誤判成「規則行」)。
    line_end = text.rfind("\n", 0, j) + 1
    return text[line_start:line_end], None


def css_rule_lines(block):
    """去掉純註解行(整行是 /* … */)與空白行,只留規則本身。
    兩邊的中文說明多寡本來就不同(dev-flow 逐條加註解,quickstart 沒有),
    這是允許的差異——比對的是渲染規則,不是旁邊的說明文字。
    """
    lines = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.fullmatch(r"/\*.*\*/", line):
            continue
        lines.append(line)
    return lines


devflow_css, devflow_css_err = extract_css_block(DEVFLOW_HTML, DEVFLOW_CSS_START, DEVFLOW_CSS_END)
quickstart_css, quickstart_css_err = extract_css_block(
    QUICKSTART_HTML, QUICKSTART_CSS_START, QUICKSTART_CSS_END
)

if devflow_css is None:
    print(f"FATAL: {DEVFLOW_HTML} 抽不到生命週期圖的 CSS 區塊:{devflow_css_err}"
          "(NOT-PARSED)", file=sys.stderr)
    sys.exit(2)
if quickstart_css is None:
    print(f"FATAL: {QUICKSTART_HTML} 抽不到生命週期圖的 CSS 區塊:{quickstart_css_err}"
          "(NOT-PARSED)", file=sys.stderr)
    sys.exit(2)

devflow_rules = css_rule_lines(devflow_css)
quickstart_rules = css_rule_lines(quickstart_css)

print(f"[css]  guide-dev-flow  CSS 規則行數  : {len(devflow_rules)}")
print(f"[css]  guide-quickstart CSS 規則行數 : {len(quickstart_rules)}")

if len(devflow_rules) == 0:
    print("FATAL: guide-dev-flow.html CSS 這側規則行數為 0——解析沒有真的跑", file=sys.stderr)
    sys.exit(2)
if len(quickstart_rules) == 0:
    print("FATAL: guide-quickstart.html CSS 這側規則行數為 0——解析沒有真的跑", file=sys.stderr)
    sys.exit(2)

if devflow_rules == quickstart_rules:
    print("[css]  ✅ 兩份導覽的生命週期圖 CSS 規則(去註解/去空白後)逐行一致。")
else:
    sm = difflib.SequenceMatcher(a=devflow_rules, b=quickstart_rules)
    ctx = None
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            ctx = (i1, devflow_rules[i1:i2], quickstart_rules[j1:j2])
            break
    msg = ["[css]  ❌ 兩份導覽的生命週期圖 CSS 規則不同——真實漂移。"]
    if ctx:
        idx, rows_a, rows_b = ctx
        msg.append(f"       第一個差異點(規則行序 #{idx})")
        msg.append(f"       guide-dev-flow  (正本)側: {rows_a!r}")
        msg.append(f"       guide-quickstart        側: {rows_b!r}")
    msg.append("       修法:以 guide-dev-flow.html 的 CSS 規則為正本,同步"
               " guide-quickstart.html 對應的規則(只動規則本身,註解各自保留即可)。")
    FAILURES.append("\n".join(msg))


# ─────────────────────────────── ③JS 規則(X-7)────────────────────────────
# 2026-08-17 補(X-7 HIGH):三份 guides(guide-dev-flow / guide-quickstart /
# guide-dev-talk)各自嵌了同一段「頁內錨點捲動修正」JS(iframe/artifact 載體不認
# fragment 導航,原生 #錨點不捲動,靠這段 JS 攔截點擊改用 scrollIntoView)。三份是
# 逐字複製貼上進正式檔的(裁決見 notes/dispatch-guard-symmetry.md X-7)——跟①②
# 一樣是雙/三副本天生會漂移的案例:改一份的 scrollIntoView 選項、忘了同步另外
# 兩份,靜默發生,先前完全沒有任何檢查會紅。
#
# 用該段 JS 前面的 HTML 註解(三份逐字相同的說明文字)當錨點定位,錨點唯一性斷言
# 同①②的紀律(count 必須恰為 1,不唯一就 fail-closed)。抽出來的是錨點之後緊接的
# 第一個 <script>…</script> 整塊——這段 JS 三份之間沒有預期差異(不像①的 svg id
# 後綴、②的中文註解多寡),所以不需要正規化規則,直接逐位元組比對三份。
#
# ⚠️ 2026-08-17 補(二次複審誘餌攻擊):舊版「找到 marker 之後第一個 <script>」
# 這條規則本身就是漏洞——三份 guides 的 marker 後都插同一段誘餌
# <script>/* decoy */</script>(三份逐位元組相同),真正的 JS 被推到誘餌後面再
# 單邊改。舊版 text.find("<script>", i) 抓到的是那段誘餌,誘餌三份相同 → 比對
# 通過,真正單邊漂移的內容整段從沒被抽到、從沒被比對(worktree 實測重現:此攻擊
# 對舊版是逃逸的假 PASS)。
# 修法:①先找到 marker 所在那句 HTML 註解的收尾 -->,②斷言 --> 之後除了空白/
# 換行以外必須緊接著 <script>——中間夾了任何其他內容(含誘餌 <script> 這種「看起來
# 也是個 script」的東西)一律 fail-closed(exit 2),不臆測擷取窗口。
GUIDE_PATHS = {
    "guide-dev-flow": DEVFLOW_HTML,
    "guide-quickstart": QUICKSTART_HTML,
    "guide-dev-talk": DEVTALK_HTML,
}
JS_ANCHOR_MARKER = "頁內錨點捲動修正"


def extract_anchor_scroll_js(path, marker):
    """以 marker(HTML 註解裡的說明文字)定位,抽出其後第一個 <script>…</script>
    整塊(inclusive)。回傳 (block, reason):失敗一律 block=None,reason 說明原因。
    """
    text = open(path, encoding="utf-8").read()

    marker_count = text.count(marker)
    if marker_count != 1:
        return None, (f'錨點「{marker}」在整檔出現 {marker_count} 次'
                       '(需恰為 1)——擷取窗口不可信')

    i = text.find(marker)
    comment_close = text.find("-->", i)
    if comment_close == -1:
        return None, f'錨點「{marker}」所在的註解找不到收尾 -->'
    comment_close_end = comment_close + len("-->")

    script_start = text.find("<script>", comment_close_end)
    if script_start == -1:
        return None, f'錨點「{marker}」之後找不到 <script>'

    gap = text[comment_close_end:script_start]
    if gap.strip() != "":
        return None, (f'marker 與 <script> 之間有不明內容,擷取窗口不可信:{gap!r}'
                       '(可能是誘餌內容被插在註解與真正 <script> 之間)')

    script_end = text.find("</script>", script_start)
    if script_end == -1:
        return None, '找不到對應的 </script>(標籤不平衡)'
    script_end += len("</script>")

    # 二次複審誘餌攻擊的關鍵補強:上面①的「--> 之後緊接 <script>」只擋得住
    # 「誘餌前面夾了別的東西」的情況——若誘餌就是緊貼在 --> 後面的那個
    # <script>(gap 仍是純空白,①一樣放行),①仍會把誘餌本身當成「唯一」的
    # script 抓走,真正的 JS 被推到誘餌**後面**、整段沒被抽到也沒被比對(worktree
    # 實測重現:只有①時此攻擊仍是逃逸的假 PASS)。這裡反過來從收尾檢查:抽到的
    # 這個 </script> 之後,除空白/換行外不能緊接著又是一個 <script>——若有,代表
    # anchor 槽位裡疊了不只一段 script(誘餌 + 真身),抽取窗口本身不可信,不猜
    # 先抓到的是誘餌還是真身。
    after_stripped = text[script_end:].lstrip()
    if after_stripped.startswith("<script"):
        return None, ('抽到的 </script> 收尾之後,除空白/換行外緊接著又是一個 '
                       '<script>——anchor 槽位裡疑似疊了誘餌 + 真身兩段 script,'
                       '擷取窗口不可信')

    # ⚠️ 誠實承認邊界(worktree 實測驗證過):這條假設「anchor 槽位裡只該有一段
    # script」——若未來有正當理由要在這個 anchor 之後**再疊一段**無關的
    # <script>(例如新功能的另一段 JS,三份同步新增、彼此不漂移),本檢查一樣會
    # fail-closed(exit 2),不會嘗試分辨「這段是誘餌」還是「這段是正當的新增」。
    # 這是刻意的取捨,不是漏洞:同樣的哲學已用在①的巢狀 svg 處理(結構超出假設
    # 就不猜、叫人來看),這裡對稱地套用在③——真要疊加第二段 script,屆時應該
    # 修這支抽取邏輯本身(改成把整個槽位的多段 script 都納入比對,而不是放寬成
    # 「允許多一段但不比對它」,那樣反而會放過誘餌攻擊)。
    return text[script_start:script_end], None


js_blocks = {}
for name, path in GUIDE_PATHS.items():
    block, err = extract_anchor_scroll_js(path, JS_ANCHOR_MARKER)
    if block is None:
        print(f"FATAL: {path} 抽不到頁內錨點捲動 JS:{err}(NOT-PARSED)", file=sys.stderr)
        sys.exit(2)
    if not block.strip():
        print(f"FATAL: {path} 抽到的頁內錨點捲動 JS 區塊為空字串(NOT-PARSED)", file=sys.stderr)
        sys.exit(2)
    js_blocks[name] = block

for name, block in js_blocks.items():
    print(f"[js]   {name:<16} 頁內錨點捲動 JS bytes={len(block.encode('utf-8'))}")

js_names = list(js_blocks.keys())
reference_name = js_names[0]
reference_block = js_blocks[reference_name]
js_mismatches = [name for name in js_names[1:] if js_blocks[name] != reference_block]

if not js_mismatches:
    print(f"[js]   ✅ 三份 guides 的頁內錨點捲動 JS 逐位元組一致(以 {reference_name} 為參照)。")
else:
    msg = ["[js]   ❌ 三份 guides 的頁內錨點捲動 JS 不一致——真實漂移。"]
    for name in js_mismatches:
        sm = difflib.SequenceMatcher(a=reference_block, b=js_blocks[name])
        ctx = None
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                ctx = (reference_block[max(0, i1 - 30):i2 + 30],
                       js_blocks[name][max(0, j1 - 30):j2 + 30])
                break
        msg.append(f"       {reference_name} 與 {name} 不同")
        if ctx:
            ctx_a, ctx_b = ctx
            msg.append(f"       {reference_name} 側上下文: ...{ctx_a}...")
            msg.append(f"       {name} 側上下文: ...{ctx_b}...")
    msg.append("       修法:三份 guides 的頁內錨點捲動 JS 是逐字複製的同一段,"
               "以其中一份為正本同步其餘兩份(只動這段 <script>,其餘內容不動)。")
    FAILURES.append("\n".join(msg))


# ─────────────────────────────────── 結論 ───────────────────────────────────
if FAILURES:
    print(file=sys.stderr)
    for f in FAILURES:
        print(f, file=sys.stderr)
    sys.exit(1)

print(f"✅ PASS:svg 標記、CSS 規則、頁內錨點捲動 JS 三層皆同步"
      f"(svg 正規化白名單套用 {len(SVG_NORMALIZE_RULES)} 條)。")
sys.exit(0)
PY
