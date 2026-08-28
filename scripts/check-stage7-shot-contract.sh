#!/bin/bash
# check-stage7-shot-contract.sh — 第 7 站審查頁截圖槽契約牙
#
# 咬什麼:notes/design/stage7-review-ui-contract.md 丟了鎖死句子
# (分組／data-shot／shots/／進場／已存在／不准新增／未掛／佔位／
# 不准發明／lightbox 或點圖／chrome 三件／.r-block／mermaid 禁／ASCII 禁),
# 或模板／S2e-walkthrough 不再點名進場+檔名,或產檔器消失／吐未掛／發明 edit URL,
# 必須紅。
#
# 產檔器:`scripts/build-stage7-html.py`。不改 twin、不把第 7 站審頁
# 塞進 build-gate-twin.py STAGES、不包 markdown-it + html-shell。
# 補助產品詞不得當通用規則寫進契約。
# 不要求 IVF 檔名(那些留在 example/subsidy-3-0-plus)。
#
# 用法:
#   scripts/check-stage7-shot-contract.sh [root]
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
CONTRACT = "notes/design/stage7-review-ui-contract.md"
TEMPLATE = "_templates/7-review.md"
HOP = "skills/dev-flow/stage7/nodes/S2e-walkthrough.md"
BUILDER = "scripts/build-stage7-html.py"
FIXTURE = "scripts/fixtures/stage7-html/review-page.md"
GATE = "scripts/build-gate-twin.py"
CHECKER = "scripts/devflow-check.sh"
VERDICT = "notes/design/gate-verdict-write.md"

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
    if text is None:
        return None, None
    match = re.search(
        rf"^(## {re.escape(prefix)}[^\n]*)\n(.*?)(?=^## |\Z)",
        text, re.M | re.S,
    )
    if not match:
        return None, None
    return match.group(1), match.group(2)


CONTRACT_NEEDLES = (
    "分組",
    "data-shot",
    "shots/",
    "進場",
    "已存在",
    "不准新增",
    "未掛",
    "佔位",
    "不准發明",
    "--ground",
    "--panel",
    "--accent",
    ".r-block",
    "mermaid 禁",
    "ASCII 禁",
    "build-stage7-html.py",
    "--action",
    "lightbox",
    "hang-point",
    "提交判定",
    "verdict:",
)

FORBIDDEN = (
    "PLUS",
    "表五",
    "表六",
    "8604",
    "27004",
)

TEMPLATE_NEEDLES = (
    "分組",
    "data-shot",
    "shots/",
    "進場",
    "已存在",
    "不准新增",
    "notes/design/stage7-review-ui-contract.md",
    "build-stage7-html.py",
)

HOP_NEEDLES = (
    "進場",
    "已存在",
    "不准新增",
    "data-shot",
    "shots/",
    "notes/design/stage7-review-ui-contract.md",
    "build-stage7-html.py",
)

HOP_DONE_NEEDLES = (
    "進場",
    "已存在",
    "不准新增",
    "未完成",
    "build-stage7-html.py",
)

OUTPUT_NEEDLES = (
    "data-shot",
    "shots/",
    "進場",
    "lightbox",
    "hang-point",
    "佔位",
    "提交判定",
    "verdict:",
    "--ground",
    "--panel",
    "--accent",
    "r-block",
    "masthead",
)


def has_lightbox_or_click(text):
    return text is not None and ("lightbox" in text or "點圖" in text)


def judge(contract_text, template_text, hop_text):
    local = []

    def fail(label):
        local.append(label)

    if contract_text is None:
        fail("契約存在 %s" % CONTRACT)
        return local

    heading, body = heading_and_body(contract_text, "版面鎖死")
    if heading is None or body is None:
        fail("契約有「## 版面鎖死」節")
        return local
    if "鎖死" not in heading:
        fail("§版面鎖死 標題含「鎖死」(不是選配／還沒拍)")
    whole = contract_text
    for needle in CONTRACT_NEEDLES:
        if needle not in whole:
            fail("契約含「%s」" % needle)
    if not has_lightbox_or_click(whole):
        fail("契約含「lightbox」或「點圖」")
    for bad in FORBIDDEN:
        if bad in whole:
            fail("契約未把補助產品詞「%s」寫成通用規則" % bad)

    if template_text is None:
        fail("%s 存在" % TEMPLATE)
    else:
        for needle in TEMPLATE_NEEDLES:
            if needle not in template_text:
                fail("模板含「%s」" % needle)
        if not has_lightbox_or_click(template_text):
            fail("模板含「lightbox」或「點圖」")

    if hop_text is None:
        fail("%s 存在" % HOP)
        return local

    for needle in HOP_NEEDLES:
        if needle not in hop_text:
            fail("S2e-walkthrough 含「%s」" % needle)

    hop_heading, hop_body = heading_and_body(hop_text, "完成條件")
    if hop_heading is None or hop_body is None:
        fail("S2e-walkthrough 有「## 完成條件」")
    else:
        done = hop_heading + "\n" + hop_body
        for needle in HOP_DONE_NEEDLES:
            if needle not in done:
                fail("S2e-walkthrough 完成條件含「%s」" % needle)
    return local


def looks_like_shell_article(html_text):
    if "data-shot" in html_text and "lightbox" in html_text:
        return False
    return "html-shell" in html_text or "<article" in html_text


def judge_html(html_text, label):
    issues = []
    if looks_like_shell_article(html_text):
        issues.append("是 html-shell 長文")
    for needle in OUTPUT_NEEDLES:
        if needle not in html_text:
            issues.append("缺「%s」" % needle)
    if "未掛" in html_text:
        issues.append("留了過期未掛句")
    if re.search(r"""href=["'][^"']*edit""", html_text, re.I):
        issues.append("發明 edit URL")
    if "mermaid" in html_text.lower():
        issues.append("吐 mermaid")
    if issues:
        return False, label + ":" + "、".join(issues)
    return True, label


contract_text = read(CONTRACT)
template_text = read(TEMPLATE)
hop_text = read(HOP)
builder_text = read(BUILDER)
gate_text = read(GATE)
check_text = read(CHECKER)
verdict_text = read(VERDICT)

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
    check("--action" in builder_text, "產檔器授權 --action")
    check("提交判定" in builder_text and "verdict:" in builder_text,
          "產檔器接 #60 提交判定寫 md 頂欄 verdict:")
    check("未掛" not in builder_text or "不得留過期未掛" in builder_text,
          "產檔器不發明未掛句")

if gate_text is not None:
    stages = re.search(r"^STAGES\s*=\s*\((.*?)\)", gate_text, re.S | re.M)
    stage_blob = stages.group(1) if stages else ""
    check("7-review" in stage_blob,
          "build-gate-twin.py STAGES 仍含 G3 7-review(審頁不改這張表)")

if check_text is not None:
    check("check-stage7-shot-contract.sh" in check_text,
          "產檔器牙已掛進 devflow-check.sh")

if verdict_text is not None:
    check("提交判定" in verdict_text and "verdict:" in verdict_text,
          "#60 verdict 正本仍在,審頁只接不重做")

if contract_text is not None and template_text is not None and hop_text is not None:
    stripped = contract_text.replace("分組", "")
    check(bool(judge(stripped, template_text, hop_text)),
          "牙咬:契約刪「分組」必須紅")
    stripped_shot = contract_text.replace("data-shot", "")
    check(bool(judge(stripped_shot, template_text, hop_text)),
          "牙咬:契約刪「data-shot」必須紅")
    stripped_entry = contract_text.replace("進場", "")
    check(bool(judge(stripped_entry, template_text, hop_text)),
          "牙咬:契約刪「進場」必須紅")
    stripped_stale = contract_text.replace("未掛", "")
    check(bool(judge(stripped_stale, template_text, hop_text)),
          "牙咬:契約刪「未掛」必須紅")
    stripped_ph = contract_text.replace("佔位", "")
    check(bool(judge(stripped_ph, template_text, hop_text)),
          "牙咬:契約刪「佔位」必須紅")
    stripped_invent = contract_text.replace("不准發明", "")
    check(bool(judge(stripped_invent, template_text, hop_text)),
          "牙咬:契約刪「不准發明」必須紅")
    poisoned = contract_text + "\nPLUS\n"
    check(bool(judge(poisoned, template_text, hop_text)),
          "牙咬:契約寫入補助產品詞必須紅")
    hop_stripped = hop_text.replace("未完成", "", 1)
    check(bool(judge(contract_text, template_text, hop_stripped)),
          "牙咬:S2e-walkthrough 完成條件刪「未完成」必須紅")

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
    check("未掛" not in html_out, "fixture 不留未掛")
    check("lightbox" in html_out and "hang-point" in html_out,
          "fixture 含 lightbox 與 hang-point")
    check("提交判定" in html_out, "fixture 含提交判定")
    stale = html_out.replace("佔位", "未掛")
    stale_ok, _ = judge_html(stale, "改成未掛")
    check(not stale_ok, "牙咬:輸出改成未掛必須紅")
    edited = html_out + '<a href="/records/1/edit">編輯</a>'
    edited_ok, _ = judge_html(edited, "發明 edit URL")
    check(not edited_ok, "牙咬:發明 edit URL 必須紅")
else:
    check(False, "產檔器存在且可跑 " + BUILDER)

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:第 7 站審查頁截圖槽契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
