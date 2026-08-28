#!/bin/bash
# check-stage1-now-contract.sh — 第 1 站審頁三框現況圖契約牙
#
# 咬什麼:notes/design/stage1-review-ui-contract.md 丟了鎖死句子
# (scan-sum／scan-now／scan-people／viewBox 200×420／height 88／
# max-width 360／已解／假設／移交／痛／繞／珠鏈／mermaid／chrome),
# 或模板／產檔器消失／吐 html-shell／吐珠鏈,必須紅。
#
# 產檔器:`scripts/build-stage1-html.py`。不改 build-scan-html.py、
# 不進 build-gate-twin.py STAGES、不包 html-shell。
# 第 1 站三框不併進 vbox-fig 生命週期圖。補助產品詞不得當通用規則。
#
# 用法:
#   scripts/check-stage1-now-contract.sh [root]
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
CONTRACT = "notes/design/stage1-review-ui-contract.md"
TEMPLATE = "_templates/1-discussion.md"
BUILDER = "scripts/build-stage1-html.py"
FIXTURE = "scripts/fixtures/stage1-html/scan-page.md"
SUBSIDY = "scripts/fixtures/stage1-html/subsidy-page.md"
SCAN = "scripts/build-scan-html.py"
GATE = "scripts/build-gate-twin.py"
CHECKER = "scripts/devflow-check.sh"
VBOX = "notes/design/vbox-fig-contract.md"

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


CONTRACT_NEEDLES = (
    "scan-sum",
    "scan-now",
    "scan-people",
    "viewBox",
    "200",
    "420",
    "88",
    "max-width:360",
    "已解",
    "假設",
    "移交",
    "痛",
    "繞",
    "珠鏈",
    "mermaid",
    "build-stage1-html.py",
    "html-shell",
    "build-scan-html.py",
    "--action",
    "--ground",
    "--panel",
    "--accent",
    ".r-block",
    ".masthead",
    ".now-wrap",
    "無標籤",
    "不併進",
)

FORBIDDEN = (
    "PLUS",
    "兩格",
    "形成併取卵",
    "27004",
    "apply_date",
)

TEMPLATE_NEEDLES = (
    "build-stage1-html.py",
    "notes/design/stage1-review-ui-contract.md",
    "scan-sum",
    "scan-now",
    "scan-people",
    "now-wrap",
)

OUTPUT_NEEDLES = (
    'id="scan-sum"',
    'id="scan-now"',
    'id="scan-people"',
    'viewBox="0 0 200 420"',
    'height="88"',
    "max-width:360",
    "已解",
    "假設",
    "移交",
    "--ground",
    "--panel",
    "--accent",
    "masthead",
    "r-block",
    "now-wrap",
)


def judge(contract_text, template_text):
    local = []
    if contract_text is None:
        local.append("契約存在 %s" % CONTRACT)
        return local
    for needle in CONTRACT_NEEDLES:
        if needle not in contract_text:
            local.append("契約含「%s」" % needle)
    for bad in FORBIDDEN:
        if bad in contract_text:
            local.append("契約未把補助產品詞「%s」寫成通用規則" % bad)
    if template_text is None:
        local.append("%s 存在" % TEMPLATE)
    else:
        for needle in TEMPLATE_NEEDLES:
            if needle not in template_text:
                local.append("模板含「%s」" % needle)
    return local


def looks_like_shell_article(html_text):
    if 'id="scan-now"' in html_text and "r-block" in html_text:
        return False
    return (
        "html-shell" in html_text
        or "html 外殼" in html_text
        or ("<article" in html_text and "max-width:880px" in html_text)
    )


def judge_html(html_text, label):
    issues = []
    if looks_like_shell_article(html_text):
        issues.append("是 html-shell 長文")
    for needle in OUTPUT_NEEDLES:
        if needle not in html_text:
            issues.append("缺「%s」" % needle)
    if "mermaid" in html_text.lower():
        issues.append("吐 mermaid")
    if "珠鏈" in html_text and "不是珠鏈" not in html_text:
        issues.append("吐珠鏈")
    if re.search(r"<pre[^>]*id=\"scan-now\"", html_text):
        issues.append("#scan-now 是 pre 不是 SVG")
    if issues:
        return False, label + ":" + "、".join(issues)
    return True, label


contract_text = read(CONTRACT)
template_text = read(TEMPLATE)
builder_text = read(BUILDER)
scan_text = read(SCAN)
gate_text = read(GATE)
check_text = read(CHECKER)
vbox_text = read(VBOX)

check(contract_text is not None, "契約存在 " + CONTRACT)
check(template_text is not None, "模板存在 " + TEMPLATE)
check(builder_text is not None, "產檔器存在 " + BUILDER)
check(os.path.isfile(os.path.join(root, FIXTURE)), "fixture 存在 " + FIXTURE)
check(os.path.isfile(os.path.join(root, SUBSIDY)), "補助寫法 fixture 存在 " + SUBSIDY)

for item in judge(contract_text, template_text):
    check(False, item)

if builder_text is not None:
    check("import markdown_it" not in builder_text
          and "from markdown_it" not in builder_text,
          "產檔器不 import markdown-it")
    check("html-shell.html" not in builder_text,
          "產檔器不包 html-shell")
    check("--action" in builder_text, "產檔器授權 --action")
    check('id="scan-now"' in builder_text and 'id="scan-sum"' in builder_text,
          "產檔器源碼點名 scan-now／scan-sum")

if scan_text is not None:
    check("build-stage1-html" not in scan_text,
          "build-scan-html.py 未被改成第 1 站審頁")

if gate_text is not None:
    stages = re.search(r"^STAGES\s*=\s*\((.*?)\)", gate_text, re.S | re.M)
    stage_blob = stages.group(1) if stages else ""
    check("1-discussion" not in stage_blob,
          "build-gate-twin.py STAGES 不含 1-discussion")

if check_text is not None:
    check("check-stage1-now-contract.sh" in check_text,
          "產檔器牙已掛進 devflow-check.sh")

if vbox_text is not None:
    check("build-stage1-html.py" in vbox_text or "第 1 站審頁" in vbox_text,
          "vbox-fig 何時不用點名第 1 站審頁三框(不併進生命週期)")

if contract_text is not None and template_text is not None:
    stripped = contract_text.replace("scan-now", "")
    check(bool(judge(stripped, template_text)),
          "牙咬:契約刪「scan-now」必須紅")
    stripped_vb = contract_text.replace("viewBox", "")
    check(bool(judge(stripped_vb, template_text)),
          "牙咬:契約刪「viewBox」必須紅")
    poisoned = contract_text + "\n形成併取卵\n"
    check(bool(judge(poisoned, template_text)),
          "牙咬:契約寫入補助產品詞必須紅")

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
    check(html_out.count("<rect") >= 3, "fixture 直式三框")
    shell_fake = (
        "<!DOCTYPE html><html><body><main style='max-width:880px'>"
        "<article><h1>1. 討論</h1><p>html 外殼直轉</p></article>"
        "</main></body></html>"
    )
    shell_ok, _ = judge_html(shell_fake, "html-shell 假輸出")
    check(not shell_ok, "牙咬:html-shell 長文必須紅")
    missing = html_out.replace('id="scan-now"', 'id="scan-old"')
    missing_ok, _ = judge_html(missing, "刪 scan-now")
    check(not missing_ok, "牙咬:輸出刪 scan-now 必須紅")
    subsidy = subprocess.run(
        [sys.executable, builder, os.path.join(root, SUBSIDY), "--out",
         os.path.join(root, "scripts/fixtures/stage1-html/_subsidy.out.html")],
        cwd=root, capture_output=True, text=True,
    )
    check(subsidy.returncode == 0, "產檔器吃補助無標籤四行＋| 寫法 exit 0")
    sub_html = ""
    sub_path = os.path.join(root, "scripts/fixtures/stage1-html/_subsidy.out.html")
    if os.path.isfile(sub_path):
        with open(sub_path, encoding="utf-8") as stream:
            sub_html = stream.read()
        os.remove(sub_path)
    sub_ok, sub_detail = judge_html(sub_html, "補助寫法輸出形狀")
    check(sub_ok, sub_detail)
    check(sub_html.count("<rect") == 3, "補助寫法正好三框,不含 |")
    check("now-wrap" in sub_html, "補助寫法有 .now-wrap 置中")
    check(">|</text>" not in sub_html and ">|</text>" not in sub_html,
          "補助寫法不把 | 印成一框")
else:
    check(False, "產檔器存在且可跑 " + BUILDER)

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:第 1 站審頁三框契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
