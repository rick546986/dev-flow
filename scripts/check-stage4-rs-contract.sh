#!/bin/bash
# check-stage4-rs-contract.sh — 第 4 站審頁 R/S 卡／生命週期契約牙
#
# 咬什麼:notes/design/stage4-review-ui-contract.md 丟了鎖死句子
# (R/S 卡／審的時候看什麼／GIVEN／WHEN／THEN／新生／改行為／退役／不動／
# 補助模組生命週期／max-width:360px／直式 SVG／verdict:／chrome),
# 或模板／產檔器消失／只認自創標題／吐 mermaid／吐 html-shell,必須紅。
#
# 產檔器:`scripts/build-stage4-html.py`。不進 build-gate-twin.py STAGES、
# 不包 html-shell。補助產品詞不得當通用規則。
#
# 用法:
#   scripts/check-stage4-rs-contract.sh [root]
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
CONTRACT = "notes/design/stage4-review-ui-contract.md"
TEMPLATE = "_templates/4-spec.md"
HOP = "skills/dev-flow/stage4/nodes/N6-g2.md"
BUILDER = "scripts/build-stage4-html.py"
FIXTURE = "scripts/fixtures/stage4-html/spec-page.md"
SUBSIDY = "scripts/fixtures/stage4-html/subsidy-page.md"
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
    "審的時候看什麼",
    "GIVEN",
    "WHEN",
    "THEN",
    "新生",
    "改行為",
    "退役",
    "不動",
    "補助模組生命週期",
    "max-width:360px",
    "直式",
    "SVG",
    "verdict:",
    "提交判定",
    "sidecar",
    "--ground",
    "--panel",
    "--accent",
    ".masthead",
    ".dash",
    ".r-block",
    "build-stage4-html.py",
    "--action",
    "html-shell",
    "mermaid",
    "不拆檔名",
)

FORBIDDEN = (
    "PLUS",
    "兩格",
    "形成併取卵",
    "27004",
    "apply_date",
)

TEMPLATE_NEEDLES = (
    "build-stage4-html.py",
    "notes/design/stage4-review-ui-contract.md",
    "審的時候看什麼",
)

HOP_NEEDLES = (
    "build-stage4-html.py",
    "notes/design/stage4-review-ui-contract.md",
)

OUTPUT_NEEDLES = (
    "r-block",
    "審的時候看什麼",
    "GIVEN",
    "WHEN",
    "THEN",
    "新生",
    "改行為",
    "退役",
    "不動",
    "max-width:360px",
    "<svg",
    "viewBox",
    "--ground",
    "--panel",
    "--accent",
    "masthead",
    "dash",
    "id=\"lifecycle\"",
    "id=\"lifecycle-note\"",
    "id=\"gate-verdict\"",
    "提交判定",
    "verdict:",
)


def judge(contract_text, template_text, hop_text):
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
    if hop_text is None:
        local.append("%s 存在" % HOP)
    else:
        for needle in HOP_NEEDLES:
            if needle not in hop_text:
                local.append("N6-g2 含「%s」" % needle)
    return local


def looks_like_shell_article(html_text):
    if 'id="lifecycle"' in html_text and "審的時候看什麼" in html_text:
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
    if re.search(r"<pre[^>]*>", html_text):
        issues.append("吐 ASCII pre")
    if re.search(r"\.r-body[^}]*max-width:\s*62ch", html_text):
        issues.append("說明被 62ch 卡住")
    fig = html_text.find('id="lifecycle"')
    note = html_text.find('id="lifecycle-note"')
    if fig >= 0 and note >= 0 and note < fig:
        issues.append("說明卡在圖前面")
    if issues:
        return False, label + ":" + "、".join(issues)
    return True, label


contract_text = read(CONTRACT)
template_text = read(TEMPLATE)
hop_text = read(HOP)
builder_text = read(BUILDER)
gate_text = read(GATE)
check_text = read(CHECKER)
vbox_text = read(VBOX)

check(contract_text is not None, "契約存在 " + CONTRACT)
check(template_text is not None, "模板存在 " + TEMPLATE)
check(hop_text is not None, "hop 存在 " + HOP)
check(builder_text is not None, "產檔器存在 " + BUILDER)
check(os.path.isfile(os.path.join(root, FIXTURE)), "fixture 存在 " + FIXTURE)
check(os.path.isfile(os.path.join(root, SUBSIDY)), "補助寫法 fixture 存在 " + SUBSIDY)

for item in judge(contract_text, template_text, hop_text):
    check(False, item)

if builder_text is not None:
    check("import markdown_it" not in builder_text
          and "from markdown_it" not in builder_text,
          "產檔器不 import markdown-it")
    check("html-shell.html" not in builder_text,
          "產檔器不包 html-shell")
    check("--action" in builder_text, "產檔器授權 --action")
    check("補助模組生命週期" in builder_text,
          "產檔器源碼點名補助模組生命週期")
    check('id="gv-submit"' in builder_text, "產檔器有提交判定器")

if gate_text is not None:
    stages = re.search(r"^STAGES\s*=\s*\((.*?)\)", gate_text, re.S | re.M)
    stage_blob = stages.group(1) if stages else ""
    names = re.findall(r'"([^"]+)"', stage_blob)
    check(names == ["2-decision", "4-spec", "7-review", "5-tasks"],
          "build-gate-twin.py STAGES 仍是四站 gate 卡,審頁不另塞一筆")

if check_text is not None:
    check("check-stage4-rs-contract.sh" in check_text,
          "產檔器牙已掛進 devflow-check.sh")

if vbox_text is not None:
    check("新生" in vbox_text and "改行為" in vbox_text,
          "vbox-fig 仍鎖新生 → 改行為 → 退役 → 不動")
    check("第 1 站" in vbox_text or "build-stage1-html.py" in vbox_text,
          "vbox-fig 何時不用仍點名第 1 站三框(不併進)")

if contract_text is not None and template_text is not None and hop_text is not None:
    stripped = contract_text.replace("審的時候看什麼", "")
    check(bool(judge(stripped, template_text, hop_text)),
          "牙咬:契約刪「審的時候看什麼」必須紅")
    stripped_life = contract_text.replace("補助模組生命週期", "")
    check(bool(judge(stripped_life, template_text, hop_text)),
          "牙咬:契約刪「補助模組生命週期」必須紅")
    poisoned = contract_text + "\n形成併取卵\n"
    check(bool(judge(poisoned, template_text, hop_text)),
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
    check(html_out.count("<rect") >= 4, "fixture 生命週期四格")
    check("class=\"hl\"" in html_out, "fixture 這輪落點 .hl")
    check(html_out.find('id="lifecycle"') < html_out.find('id="lifecycle-note"'),
          "圖卡與說明卡分開,圖在前")
    subsidy = subprocess.run(
        [sys.executable, builder, os.path.join(root, SUBSIDY), "--out",
         os.path.join(root, "scripts/fixtures/stage4-html/_subsidy.out.html")],
        cwd=root, capture_output=True, text=True,
    )
    check(subsidy.returncode == 0, "產檔器吃補助模組生命週期（預覽） exit 0")
    sub_path = os.path.join(root, "scripts/fixtures/stage4-html/_subsidy.out.html")
    sub_html = ""
    if os.path.isfile(sub_path):
        with open(sub_path, encoding="utf-8") as stream:
            sub_html = stream.read()
        os.remove(sub_path)
    sub_ok, sub_detail = judge_html(sub_html, "補助標題輸出形狀")
    check(sub_ok, sub_detail)
    check(sub_html.count("<rect") == 4, "補助標題正好四格,不拆檔名")
    check("新生" in sub_html and "改行為" in sub_html, "補助四條印成新生／改行為／退役／不動")
    check("查詢入口" in sub_html, "補助改行為格吃到四條正文")
    check("<pre" not in sub_html and "mermaid" not in sub_html.lower(),
          "補助寫法禁 mermaid／ASCII pre")
    check('id="gv-submit"' in sub_html, "補助寫法有提交判定")
    old_fake = (
        "<!DOCTYPE html><html><body><main style='max-width:880px'>"
        "<article><h1>4. 規格</h1><pre>A -> B -> C</pre></article>"
        "</main></body></html>"
    )
    old_ok, _ = judge_html(old_fake, "html-shell 假輸出")
    check(not old_ok, "牙咬:html-shell／橫 ASCII 必須紅")
    missing = html_out.replace("審的時候看什麼", "看什麼")
    missing_ok, _ = judge_html(missing, "刪 審的時候看什麼")
    check(not missing_ok, "牙咬:輸出刪 審的時候看什麼 必須紅")
else:
    check(False, "產檔器存在且可跑 " + BUILDER)

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:第 4 站審頁 R/S 契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
