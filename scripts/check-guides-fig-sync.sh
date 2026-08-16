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
#   - 本檢查涵蓋**兩層**,不是只比 svg 標記:①svg 標記本身(見下①)②渲染這張圖用
#     到的 CSS 規則區塊(見下②)。只比 svg、不比 CSS 的話,兩邊 svg 標記逐位元組
#     相同、但其中一邊的 `.hk`/`.att`/`.loopscope`/`edge-*` 等規則被單獨改壞,圖會
#     渲染成兩個不同的東西,本守衛卻還是綠燈——這正是同一種「不對稱保護」的漏洞
#     換了一層皮再犯一次,所以兩層都要顧。
#
# 做兩件事:
#   ①svg 標記:從兩份導覽各自抽出生命週期圖的 <svg id="...">…</svg> 區塊,正規化掉
#     頂層 id 的預期差異後逐位元組比對。
#   ②CSS 規則:從兩份導覽各自抽出繪這張圖專用的 CSS 區塊(以雙生註解為錨點),
#     去掉純註解行/空白行後逐行比對規則本身(兩邊的註解文字本來就不同——dev-flow
#     那份有逐條中文說明、quickstart 那份沒有——這是允許的差異,規則才是要顧的東西)。
#   任一邊抽取失敗(regex 沒命中)或抽到空內容 → exit 2(NOT-PARSED,見下)。
#   正規化/去註解後仍不同 = 真漂移 → FAIL,並印出第一個差異點的上下文,點名差在哪。
#
# 用法:
#   scripts/check-guides-fig-sync.sh [root]   # 缺省 root = repo root
# root 可指向 /private/tmp 下的複本,供 test-architecture-guards.sh 的 mutation 驗證。
#
# exit:0 = 兩層都同步 / 1 = 至少一層正規化後仍有差異(FAIL)/
#      2 = 抽取失敗或解析到空內容(fail-closed,不猜)

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
DEVFLOW_SVG_ID = "fig-lifecycle"
QUICKSTART_SVG_ID = "fig-lifecycle-qs"

for path in (DEVFLOW_HTML, QUICKSTART_HTML):
    if not os.path.isfile(path):
        print(f"FATAL: 找不到 {path}", file=sys.stderr)
        sys.exit(2)

FAILURES = []  # 累積兩層各自的 FAIL 訊息,兩層都跑完才一次回報,不 fail-fast 漏看另一層


# ─────────────────────────────── ①svg 標記 ───────────────────────────────
def extract_svg(path, svg_id):
    """抽出 <svg id="{svg_id}" ...>...</svg> 整塊(inclusive)。
    找不到起始標籤,或起始後找不到對應 </svg>,一律回傳 None(呼叫端視為抽取失敗)。
    """
    text = open(path, encoding="utf-8").read()
    pattern = re.compile(
        r'<svg id="' + re.escape(svg_id) + r'"[^>]*>.*?</svg>', re.S
    )
    m = pattern.search(text)
    if not m:
        return None
    return m.group(0)


devflow_svg = extract_svg(DEVFLOW_HTML, DEVFLOW_SVG_ID)
quickstart_svg = extract_svg(QUICKSTART_HTML, QUICKSTART_SVG_ID)

if devflow_svg is None:
    print(f'FATAL: {DEVFLOW_HTML} 抽不到 <svg id="{DEVFLOW_SVG_ID}">…</svg>'
          '(NOT-PARSED,不是「沒有差異」)', file=sys.stderr)
    sys.exit(2)
if quickstart_svg is None:
    print(f'FATAL: {QUICKSTART_HTML} 抽不到 <svg id="{QUICKSTART_SVG_ID}">…</svg>'
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


def extract_css_block(path, start_marker, end_marker):
    text = open(path, encoding="utf-8").read()
    i = text.find(start_marker)
    if i == -1:
        return None
    # 往回找到該行行首,把整條註解(含 /* ── … ──）都算進區塊,而不是從關鍵字中間截斷
    line_start = text.rfind("\n", 0, i) + 1
    j = text.find(end_marker, i)
    if j == -1:
        return None
    # 同樣退回到 end_marker 所在行的行首,避免切斷 end_marker 前那一行本身
    # (例如 dev-flow 側的下一個 Phase 註解跟本圖註解同一行風格,若切在關鍵字
    # 中間會留下一截沒有收尾的殘破註解行,被誤判成「規則行」)。
    line_end = text.rfind("\n", 0, j) + 1
    return text[line_start:line_end]


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


devflow_css = extract_css_block(DEVFLOW_HTML, DEVFLOW_CSS_START, DEVFLOW_CSS_END)
quickstart_css = extract_css_block(QUICKSTART_HTML, QUICKSTART_CSS_START, QUICKSTART_CSS_END)

if devflow_css is None:
    print(f"FATAL: {DEVFLOW_HTML} 抽不到生命週期圖的 CSS 區塊(錨點「{DEVFLOW_CSS_START}」"
          "或「{DEVFLOW_CSS_END}」找不到,NOT-PARSED)", file=sys.stderr)
    sys.exit(2)
if quickstart_css is None:
    print(f"FATAL: {QUICKSTART_HTML} 抽不到生命週期圖的 CSS 區塊(錨點"
          f"「{QUICKSTART_CSS_START}」或「{QUICKSTART_CSS_END}」找不到,NOT-PARSED)", file=sys.stderr)
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


# ─────────────────────────────────── 結論 ───────────────────────────────────
if FAILURES:
    print(file=sys.stderr)
    for f in FAILURES:
        print(f, file=sys.stderr)
    sys.exit(1)

print(f"✅ PASS:svg 標記與 CSS 規則兩層皆同步(白名單套用 {len(SVG_NORMALIZE_RULES)} 條)。")
sys.exit(0)
PY
