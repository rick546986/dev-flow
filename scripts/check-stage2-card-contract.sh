#!/bin/bash
# check-stage2-card-contract.sh — 第 2 站審頁分組卡契約牙
#
# 咬什麼:notes/design/stage2-review-ui-contract.md 丟了鎖死句子
# (分組卡／Decision／max-width:360px／直式 SVG／背景摺疊／mermaid 禁／
# ASCII 禁／勾選提示／你要審什麼／Rejected 釘頂／chrome),
# 或模板／產檔器消失／吐舊主產檔器樣,必須紅。
#
# 產檔器:`scripts/build-stage2-html.py`。不進 build-gate-twin.py STAGES、
# 不包 html-shell。補助產品詞不得當通用規則。
#
# 用法:
#   scripts/check-stage2-card-contract.sh [root]
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
CONTRACT = "notes/design/stage2-review-ui-contract.md"
TEMPLATE = "_templates/2-decision.md"
HOP = "skills/dev-flow/stage2/nodes/N7-g1.md"
BUILDER = "scripts/build-stage2-html.py"
FIXTURE = "scripts/fixtures/stage2-html/decision-page.md"
SUBSIDY = "scripts/fixtures/stage2-html/subsidy-page.md"
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


CONTRACT_NEEDLES = (
    "分組卡",
    "Decision",
    "max-width:360px",
    "直式",
    "SVG",
    "背景摺疊",
    "mermaid",
    "ASCII",
    "勾選提示",
    "你要審什麼",
    "Rejected 釘頂",
    "--ground",
    "--panel",
    "--accent",
    "--ok-soft",
    "--bad-soft",
    ".masthead",
    ".dash",
    ".cell",
    ".r-block",
    "build-stage2-html.py",
    "--action",
    "html-shell",
    "置頂",
    "表格",
)

FORBIDDEN = (
    "PLUS",
    "兩格",
    "形成併取卵",
    "27004",
    "apply_date",
)

TEMPLATE_NEEDLES = (
    "build-stage2-html.py",
    "notes/design/stage2-review-ui-contract.md",
    "分組卡",
)

HOP_NEEDLES = (
    "build-stage2-html.py",
    "notes/design/stage2-review-ui-contract.md",
)

OUTPUT_NEEDLES = (
    "r-block",
    "class=\"card\"",
    "max-width:360px",
    "<svg",
    "viewBox",
    "<details",
    "--ground",
    "--panel",
    "--accent",
    "--ok-soft",
    "--bad-soft",
    "masthead",
    "dash",
    "cell",
    "id=\"decision\"",
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
                local.append("N7-g1 含「%s」" % needle)
    return local


def looks_like_shell_article(html_text):
    if "id=\"decision\"" in html_text and "<svg" in html_text:
        return False
    return (
        "html-shell" in html_text
        or "你要審什麼" in html_text
        or "勾選提示" in html_text
    )


def judge_html(html_text, label):
    issues = []
    if looks_like_shell_article(html_text):
        issues.append("是 html-shell 或舊主產檔器樣")
    for needle in OUTPUT_NEEDLES:
        if needle not in html_text:
            issues.append("缺「%s」" % needle)
    if "mermaid" in html_text.lower():
        issues.append("吐 mermaid")
    if "你要審什麼" in html_text:
        issues.append("吐你要審什麼")
    if "勾選提示" in html_text:
        issues.append("吐勾選提示")
    if re.search(r"<pre[^>]*>", html_text):
        issues.append("吐 ASCII pre")
    # Rejected 不得釘在 Decision 前面
    dec = html_text.find('id="decision"')
    rej = html_text.find('id="rejected"')
    if dec >= 0 and rej >= 0 and rej < dec:
        issues.append("Rejected 釘在 Decision 前面")
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
    check("g1-ask" not in builder_text and "s-ask" not in builder_text,
          "產檔器不吐舊主產檔器樣")

if gate_text is not None:
    stages = re.search(r"^STAGES\s*=\s*\((.*?)\)", gate_text, re.S | re.M)
    stage_blob = stages.group(1) if stages else ""
    names = re.findall(r'"([^"]+)"', stage_blob)
    check(names == ["2-decision", "4-spec", "7-review", "5-tasks"],
          "build-gate-twin.py STAGES 仍是四站 gate 卡,審頁不另塞一筆")

if check_text is not None:
    check("check-stage2-card-contract.sh" in check_text,
          "產檔器牙已掛進 devflow-check.sh")

if contract_text is not None and template_text is not None and hop_text is not None:
    stripped = contract_text.replace("分組卡", "")
    check(bool(judge(stripped, template_text, hop_text)),
          "牙咬:契約刪「分組卡」必須紅")
    stripped_svg = contract_text.replace("max-width:360px", "")
    check(bool(judge(stripped_svg, template_text, hop_text)),
          "牙咬:契約刪「max-width:360px」必須紅")
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
    check(html_out.count('class="card"') >= 4,
          "fixture 至少四張方案卡")
    check("<svg" in html_out and "max-width:360px" in html_out,
          "Decision 後直式 SVG 置中 360")
    dec = html_out.find('id="decision"')
    point = html_out.find('id="point-1"')
    check(dec >= 0 and point >= 0 and dec < point,
          "Decision 置頂在決策點卡前面")
    subsidy = subprocess.run(
        [sys.executable, builder, os.path.join(root, SUBSIDY), "--out",
         os.path.join(root, "scripts/fixtures/stage2-html/_subsidy.out.html")],
        cwd=root, capture_output=True, text=True,
    )
    check(subsidy.returncode == 0, "產檔器吃補助 Approaches 表寫法 exit 0")
    sub_path = os.path.join(root, "scripts/fixtures/stage2-html/_subsidy.out.html")
    sub_html = ""
    if os.path.isfile(sub_path):
        with open(sub_path, encoding="utf-8") as stream:
            sub_html = stream.read()
        os.remove(sub_path)
    sub_ok, sub_detail = judge_html(sub_html, "補助表寫法輸出形狀")
    check(sub_ok, sub_detail)
    check(sub_html.count('id="point-') == 4, "補助表寫法四個決策點 r-block")
    check(sub_html.count('class="card"') >= 12, "補助表寫法每點有 A/B/C 卡")
    check(sub_html.find('id="decision"') < sub_html.find('id="point-1"'),
          "補助表寫法 Decision 置頂")
    check("<details" in sub_html, "補助表寫法背景摺疊")
    check("<pre" not in sub_html and "mermaid" not in sub_html.lower(),
          "補助表寫法禁 mermaid／ASCII pre")
    old_fake = (
        "<!DOCTYPE html><html><body><div>你要審什麼</div>"
        "<div>勾選提示</div><pre>[A]->[B]->[C]</pre></body></html>"
    )
    old_ok, _ = judge_html(old_fake, "舊主產檔器假輸出")
    check(not old_ok, "牙咬:勾選提示／你要審什麼／橫 ASCII 必須紅")
    ex2 = read("example/contract-expiry-reminder/2-decision.html")
    check(bool(ex2) and "html 外殼" not in ex2
          and "<svg" in (ex2 or "") and not re.search(r"<pre[^>]*>", ex2 or "")
          and "方案架構圖" in (ex2 or "")
          and "build-stage2-html.py" in (ex2 or ""),
          "example 2-decision.html 是產器直式 SVG,不是 html-shell／橫 ASCII")
else:
    check(False, "產檔器存在且可跑 " + BUILDER)

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:第 2 站審頁分組卡契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
