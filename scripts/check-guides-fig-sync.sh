#!/bin/bash
# 主指南單一正本 + quickstart stub 牙齒(Repo-local)。
#
# 合併後不再有第二份生命週期圖。本檢查改盯:
#   ①guide-quickstart.html 必須是 stub(短頁、轉去主指南 #start 的 Pages URL)
#   ②guide-dev-flow.html 必須有 id="start"(開工章)
#   ③仍活著、仍嵌頁內錨點捲動 JS 的導覽(guide-dev-flow / guide-dev-talk)
#     那段 JS 必須逐位元組一致(stub 沒有這段 JS,不納入)
#
# 用法:
#   scripts/check-guides-fig-sync.sh [root]
# exit:0 = 全過 / 1 = stub 或 #start 或 JS 漂移(FAIL)/
#      2 = 抽取失敗、錨點不唯一、或解析到空內容(fail-closed,不猜)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import difflib
import os
import sys

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root = sys.argv[1]

DEVFLOW_HTML = os.path.join(root, "guides", "guide-dev-flow.html")
QUICKSTART_HTML = os.path.join(root, "guides", "guide-quickstart.html")
DEVTALK_HTML = os.path.join(root, "guides", "guide-dev-talk.html")
START_URL = "https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#start"

for path in (DEVFLOW_HTML, QUICKSTART_HTML, DEVTALK_HTML):
    if not os.path.isfile(path):
        print(f"FATAL: 找不到 {path}", file=sys.stderr)
        sys.exit(2)

FAILURES = []


# ── ① stub + ② canonical #start ──────────────────────────────────────────
canon = open(DEVFLOW_HTML, encoding="utf-8").read()
stub = open(QUICKSTART_HTML, encoding="utf-8").read()

if 'id="start"' not in canon:
    FAILURES.append("[start] ❌ guide-dev-flow.html 沒有 id=\"start\" —— 開工章必須在主指南。")
else:
    print("[start] ✅ guide-dev-flow.html 有 #start")

stub_lines = stub.splitlines()
if len(stub_lines) >= 20:
    FAILURES.append(f"[stub]  ❌ guide-quickstart.html 有 {len(stub_lines)} 行 —— 必須是 stub,不得再放第二份正文。")
else:
    print(f"[stub]  ✅ guide-quickstart.html 是 stub({len(stub_lines)} 行)")

if START_URL not in stub:
    FAILURES.append("[stub]  ❌ guide-quickstart.html 沒有轉去 " + START_URL)
else:
    print("[stub]  ✅ stub 轉去主指南 #start(Pages URL)")

if 'http-equiv="refresh"' not in stub and "http-equiv='refresh'" not in stub:
    FAILURES.append("[stub]  ❌ guide-quickstart.html 沒有 meta refresh")
else:
    print("[stub]  ✅ stub 有 meta refresh")

if 'id="fig-lifecycle-qs"' in stub or "parity:start" in stub:
    FAILURES.append("[stub]  ❌ guide-quickstart.html 仍含生命週期圖或 parity 正文 —— 不是 stub")


# ── ③JS 規則:仍活著的導覽頁內錨點捲動 JS ────────────────────────────────
# stub 沒有這段 JS。只比 guide-dev-flow 與 guide-dev-talk。
# 抽取紀律沿用舊版:marker 唯一、--> 後緊接 <script>、抽到的 </script> 後
# 不得再疊一段 <script>(誘餌攻擊 fail-closed)。
JS_ANCHOR_MARKER = "頁內錨點捲動修正"
GUIDE_PATHS = {
    "guide-dev-flow": DEVFLOW_HTML,
    "guide-dev-talk": DEVTALK_HTML,
}


def extract_anchor_scroll_js(path, marker):
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
    after_stripped = text[script_end:].lstrip()
    if after_stripped.startswith("<script"):
        return None, ('抽到的 </script> 收尾之後,除空白/換行外緊接著又是一個 '
                       '<script>——anchor 槽位裡疑似疊了誘餌 + 真身兩段 script,'
                       '擷取窗口不可信')
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
    print(f"[js]   ✅ 仍活著的導覽頁內錨點捲動 JS 逐位元組一致(以 {reference_name} 為參照)。")
else:
    msg = ["[js]   ❌ 仍活著的導覽頁內錨點捲動 JS 不一致——真實漂移。"]
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
    msg.append("       修法:仍活著的導覽頁內錨點捲動 JS 是逐字複製的同一段,"
               "以其中一份為正本同步其餘(只動這段 <script>,其餘內容不動)。")
    FAILURES.append("\n".join(msg))


if FAILURES:
    print(file=sys.stderr)
    for f in FAILURES:
        print(f, file=sys.stderr)
    sys.exit(1)

print("✅ PASS:quickstart 是 stub、主指南有 #start、仍活著的導覽 JS 同步")
sys.exit(0)
PY
