#!/bin/bash
# check-stage6-hunk-contract.sh — 第 6 站審碼 hunk 顯示契約牙
#
# 咬什麼:notes/design/stage5-review-ui-contract.md §第6站審碼 丟了鎖死句子
# (改什麼／T-n／關聯／.ln.add／--ok-soft／不准發明 minus／chrome 三件),
# 或模板／S2-tdd 完成條件不再點名這些欄,或產檔器消失／不再吐 details.hunk,
# 必須紅。
#
# 產檔器吃 ## Diff(`scripts/build-stage6-html.py`)。不改 twin、不把第 6 站
# 塞進 build-gate-twin.py STAGES、不包 markdown-it + html-shell、不取代
# check-vbox-fig.sh／check-devstage6-graph.sh。補助產品詞不得當通用規則
# 寫進契約。
#
# 用法:
#   scripts/check-stage6-hunk-contract.sh [root]
# exit:0 = 全過 / 1 = 契約句丟了或產檔器吐錯形 / 2 = 環境或用法失敗

set -uo pipefail

SELF=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import os
import re
import subprocess
import sys

root = sys.argv[1]
CONTRACT = "notes/design/stage5-review-ui-contract.md"
TEMPLATE = "_templates/6-implementation-notes.md"
HOP = "skills/dev-flow/stage6/nodes/S2-tdd.md"
BUILDER = "scripts/build-stage6-html.py"
FIXTURE = "scripts/fixtures/stage6-html/hunk-page.md"
GATE = "scripts/build-gate-twin.py"
CHECKER = "scripts/devflow-check.sh"

failures = []
checks = 0


def check(ok, label):
    global checks
    checks += 1
    if ok:
        print("[ok] " + label)
        return
    print("[FAIL] " + label)
    failures.append(label)


def read(rel):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as stream:
        return stream.read()


def heading_and_body(text, prefix):
    """抽 `## <prefix>…` 標題行 + 到下一 `## ` 的本文。找不到回 (None, None)。"""
    if text is None:
        return None, None
    match = re.search(
        rf"^(## {re.escape(prefix)}[^\n]*)\n(.*?)(?=^## |\Z)",
        text, re.M | re.S,
    )
    if not match:
        return None, None
    return match.group(1), match.group(2)


# §第6站審碼 必須出現的句子(鎖死,不是口味)。刪任何一條,這支要紅。
SECTION_NEEDLES = (
    "一函式一塊",
    "改什麼",
    ".ln.add",
    "--ok-soft",
    "不准發明 minus",
    "T-n",
    "關聯一行",
    "不要整檔貼上",
    "第二份正本",
    "--ground",
    "--panel",
    "--accent",
    ".r-block",
    "產檔器吃 ## Diff",
    "details.hunk",
    "hunk-why",
    "hunk-rel",
    "build-stage6-html.py",
    "不是口味",
)

# 契約正本不得拿補助產品詞當通用規則。
FORBIDDEN = (
    "PLUS",
    "兩格",
    "形成併取卵",
    "27004",
    "apply_date",
)

TEMPLATE_NEEDLES = (
    "改什麼",
    "T-n",
    "關聯",
    ".ln.add",
    "--ok-soft",
    "不要整檔貼上",
    "notes/design/stage5-review-ui-contract.md",
    "產檔器吃 ## Diff",
    "build-stage6-html.py",
    "### <fn> · `<file>` <lines>  T-n",
)

HOP_DONE_NEEDLES = (
    "改什麼",
    "T-n",
    "關聯",
    "色碼",
    "未完成",
    "build-stage6-html.py",
)

OUTPUT_NEEDLES = (
    "details.hunk",
    "hunk-why",
    "hunk-rel",
    "ln.add",
    "--ground",
    "--panel",
    "--accent",
    'id="hunks"',
    "tag base",
)


def judge(contract_text, template_text, hop_text):
    local = []

    def fail(label):
        local.append(label)

    heading, body = heading_and_body(contract_text, "第 6 站審碼")
    if heading is None or body is None:
        fail("契約有「## 第 6 站審碼」節")
        return local
    if "鎖死" not in heading:
        fail("§第6站審碼 標題含「鎖死」(不是選配／還沒拍)")
    if "還沒拍" in heading or "只鎖這條" in heading:
        fail("§第6站審碼 標題不再寫「還沒拍」或「只鎖這條」")
    section = heading + "\n" + body
    for needle in SECTION_NEEDLES:
        if needle not in section:
            fail("§第6站審碼 含「%s」" % needle)
    for bad in FORBIDDEN:
        if bad in (contract_text or ""):
            fail("契約未把補助產品詞「%s」寫成通用規則" % bad)

    if template_text is None:
        fail("%s 存在" % TEMPLATE)
    else:
        for needle in TEMPLATE_NEEDLES:
            if needle not in template_text:
                fail("模板含「%s」" % needle)

    hop_heading, hop_body = heading_and_body(hop_text, "完成條件")
    if hop_heading is None or hop_body is None:
        fail("S2-tdd 有「## 完成條件」")
    else:
        done = hop_heading + "\n" + hop_body
        for needle in HOP_DONE_NEEDLES:
            if needle not in done:
                fail("S2-tdd 完成條件含「%s」" % needle)
    return local


def looks_like_shell_article(html_text):
    """html-shell 直轉長文:有 article/main 殼、沒有 details.hunk。"""
    if "details.hunk" in html_text or 'class="hunk"' in html_text:
        return False
    return (
        "<article" in html_text
        or "html-shell" in html_text
        or "html 外殼" in html_text
        or ("<main" in html_text and "max-width:880px" in html_text)
        or ("<main" in html_text and "max-width:62ch" in html_text)
    )


def judge_html(html_text, label):
    issues = []
    if looks_like_shell_article(html_text):
        issues.append("是 html-shell 長文、沒 details.hunk")
    for needle in OUTPUT_NEEDLES:
        if needle not in html_text:
            issues.append("缺「%s」" % needle)
    if "mermaid" in html_text.lower():
        issues.append("吐 mermaid")
    if re.search(r"max-width:\s*62ch", html_text) and ".sub{" not in html_text:
        issues.append("正文被 62ch 卡住")
    if issues:
        return False, label + ":" + "、".join(issues)
    return True, label


contract_text = read(CONTRACT)
template_text = read(TEMPLATE)
hop_text = read(HOP)
builder_text = read(BUILDER)
gate_text = read(GATE)
check_text = read(CHECKER)

check(contract_text is not None, "契約存在 " + CONTRACT)
check(template_text is not None, "模板存在 " + TEMPLATE)
check(hop_text is not None, "hop 存在 " + HOP)
check(builder_text is not None, "產檔器存在 " + BUILDER)
check(os.path.isfile(os.path.join(root, FIXTURE)), "fixture 存在 " + FIXTURE)

for item in judge(contract_text, template_text, hop_text):
    check(False, item)

if builder_text is not None:
    check("import markdown_it" not in builder_text
          and "from markdown_it" not in builder_text,
          "產檔器不 import markdown-it")
    check("html-shell.html" not in builder_text,
          "產檔器不包 html-shell")
    check("details.hunk" in builder_text and "hunk-why" in builder_text
          and "ln.add" in builder_text,
          "產檔器源碼點名 details.hunk／hunk-why／.ln.add")

if gate_text is not None:
    stages = re.search(r"^STAGES\s*=\s*\((.*?)\)", gate_text, re.S | re.M)
    stage_blob = stages.group(1) if stages else ""
    check("6-implementation" not in stage_blob,
          "build-gate-twin.py STAGES 不含 6-implementation")

if check_text is not None:
    check("check-stage6-hunk-contract.sh" in check_text,
          "產檔器牙已掛進 devflow-check.sh")

# 牙自己咬壞契約:同一把 judge,丟句子或塞補助詞必須判紅,否則這支是空殼。
if contract_text is not None and template_text is not None and hop_text is not None:
    stripped = contract_text.replace("改什麼", "")
    check(bool(judge(stripped, template_text, hop_text)),
          "牙咬:§第6站審碼 刪「改什麼」必須紅")
    stripped_ln = contract_text.replace(".ln.add", "")
    check(bool(judge(stripped_ln, template_text, hop_text)),
          "牙咬:§第6站審碼 刪「.ln.add」必須紅")
    stripped_prod = contract_text.replace("產檔器吃 ## Diff", "")
    check(bool(judge(stripped_prod, template_text, hop_text)),
          "牙咬:§第6站審碼 刪「產檔器吃 ## Diff」必須紅")
    poisoned = contract_text + "\n形成併取卵\n"
    check(bool(judge(poisoned, template_text, hop_text)),
          "牙咬:契約寫入補助產品詞必須紅")
    hop_stripped = hop_text.replace("未完成", "", 1)
    check(bool(judge(contract_text, template_text, hop_stripped)),
          "牙咬:S2-tdd 完成條件刪「未完成」必須紅")

builder = os.path.join(root, BUILDER)
if os.path.isfile(builder):
    empty = subprocess.run(
        [sys.executable, builder],
        cwd=root, capture_output=True, text=True,
    )
    check(empty.returncode == 2, "產檔器無參數 exit 2")
    good = subprocess.run(
        [sys.executable, builder, "--fixture"],
        cwd=root, capture_output=True, text=True,
    )
    check(good.returncode == 0, "產檔器 --fixture exit 0")
    html_out = good.stdout
    ok, detail = judge_html(html_out, "fixture 輸出形狀")
    check(ok, detail)
    check(html_out.count("details.hunk") >= 3
          or html_out.count('class="hunk"') >= 3,
          "fixture 至少三塊 details.hunk")
    check('class="ln add"' in html_out, "fixture 含 .ln.add")
    check('class="ln del"' in html_out, "fixture 含已知舊行的 .ln.del")
    check(html_out.count("tag base") >= 4, "雙 T hunk 才帶兩個 T tag")
    shell_fake = (
        "<!DOCTYPE html><html><body><main style='max-width:880px'>"
        "<article><h1>6. 實作筆記</h1><p>html 外殼直轉</p></article>"
        "</main></body></html>"
    )
    shell_ok, _ = judge_html(shell_fake, "html-shell 假輸出")
    check(not shell_ok, "牙咬:html-shell 長文(沒 details.hunk)必須紅")
    missing_hunk = html_out.replace("details.hunk", "details.doc").replace(
        'class="hunk"', 'class="doc"'
    )
    missing_ok, _ = judge_html(missing_hunk, "刪 details.hunk")
    check(not missing_ok, "牙咬:輸出刪 details.hunk 必須紅")
else:
    check(False, "產檔器存在且可跑 " + BUILDER)

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:第 6 站審碼 hunk 契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
