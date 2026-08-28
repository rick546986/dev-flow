#!/bin/bash
# check-stage3-proto-contract.sh — 第 3 站審頁觸發判定／Demo／n-a 契約牙
#
# 咬什麼:notes/design/stage3-review-ui-contract.md 丟了鎖死句子
# (觸發判定／Demo／2-decision／n-a／3-prototype.md／html-shell／chrome／
# 深淺色／直式 SVG),或模板／產檔器消失／缺檔當硬缺／吐 html-shell,必須紅。
#
# 產檔器:`scripts/build-stage3-html.py`。不進 build-gate-twin.py STAGES、
# 不包 html-shell。補助產品詞不得當通用規則。
#
# 用法:
#   scripts/check-stage3-proto-contract.sh [root]
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
import tempfile

root = sys.argv[1]
CONTRACT = "notes/design/stage3-review-ui-contract.md"
TEMPLATE = "_templates/3-prototype.md"
HOP = "skills/dev-flow/stage3/nodes/S4-close.md"
BUILDER = "scripts/build-stage3-html.py"
FIXTURE = "scripts/fixtures/stage3-html/proto-page.md"
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
    "觸發判定",
    "Demo",
    "2-decision",
    "n-a",
    "3-prototype.md",
    "html-shell",
    "--ground",
    "--panel",
    "--accent",
    ".masthead",
    ".dash",
    ".r-block",
    "深淺色",
    "prefers-color-scheme",
    "直式",
    "SVG",
    "mermaid",
    "build-stage3-html.py",
    "--action",
    "exit 1",
)

FORBIDDEN = (
    "PLUS",
    "兩格",
    "形成併取卵",
    "27004",
    "apply_date",
)

TEMPLATE_NEEDLES = (
    "build-stage3-html.py",
    "notes/design/stage3-review-ui-contract.md",
    "n-a",
)

HOP_NEEDLES = (
    "build-stage3-html.py",
    "notes/design/stage3-review-ui-contract.md",
)

OUTPUT_NEEDLES = (
    "觸發判定",
    "Demo",
    "2-decision",
    "r-block",
    "--ground",
    "--panel",
    "--accent",
    "masthead",
    "dash",
    "prefers-color-scheme",
    "id=\"trigger\"",
    "id=\"demo\"",
    "id=\"writeback\"",
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
                local.append("S4-close 含「%s」" % needle)
    return local


def looks_like_shell_article(html_text):
    if 'id="trigger"' in html_text and "r-block" in html_text:
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
    check("--action" in builder_text, "產檔器授權 --action")
    check("n-a" in builder_text, "產檔器源碼點名 n-a")

if gate_text is not None:
    stages = re.search(r"^STAGES\s*=\s*\((.*?)\)", gate_text, re.S | re.M)
    stage_blob = stages.group(1) if stages else ""
    check("3-prototype" not in stage_blob,
          "build-gate-twin.py STAGES 不含 3-prototype")

if check_text is not None:
    check("check-stage3-proto-contract.sh" in check_text,
          "產檔器牙已掛進 devflow-check.sh")

if contract_text is not None and template_text is not None and hop_text is not None:
    stripped = contract_text.replace("觸發判定", "")
    check(bool(judge(stripped, template_text, hop_text)),
          "牙咬:契約刪「觸發判定」必須紅")
    stripped_na = contract_text.replace("n-a", "")
    check(bool(judge(stripped_na, template_text, hop_text)),
          "牙咬:契約刪「n-a」必須紅")
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
    check("2-decision" in html_out, "fixture 答案回寫 2-decision")
    check("prefers-color-scheme" in html_out, "fixture 深淺色")
    tmp = tempfile.mkdtemp(prefix="stage3-na-")
    na_dir = subprocess.run(
        [sys.executable, builder, tmp],
        cwd=root, capture_output=True, text=True,
    )
    na_text = (na_dir.stdout or "") + (na_dir.stderr or "")
    check(na_dir.returncode == 0, "feat 目錄沒有 3-prototype.md 時 exit 0(不是硬缺)")
    check("n-a" in na_text, "feat 目錄沒有 3-prototype.md 時印 n-a")
    check(not os.path.isfile(os.path.join(tmp, "3-prototype.html")),
          "n-a 不寫 html")
    missing_file = os.path.join(tmp, "3-prototype.md")
    na_file = subprocess.run(
        [sys.executable, builder, missing_file],
        cwd=root, capture_output=True, text=True,
    )
    na_file_text = (na_file.stdout or "") + (na_file.stderr or "")
    check(na_file.returncode == 0, "缺 3-prototype.md 檔時 exit 0")
    check("n-a" in na_file_text, "缺 3-prototype.md 檔時印 n-a")
    check(na_file.returncode != 1, "缺檔不得當硬缺 exit 1")
    shell_fake = (
        "<!DOCTYPE html><html><body><main style='max-width:880px'>"
        "<article><h1>3. 原型</h1><p>html 外殼直轉</p></article>"
        "</main></body></html>"
    )
    shell_ok, _ = judge_html(shell_fake, "html-shell 假輸出")
    check(not shell_ok, "牙咬:html-shell 長文必須紅")
    missing = html_out.replace('id="trigger"', 'id="old-trigger"')
    missing_ok, _ = judge_html(missing, "刪 trigger")
    check(not missing_ok, "牙咬:輸出刪 trigger 必須紅")
else:
    check(False, "產檔器存在且可跑 " + BUILDER)

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:第 3 站審頁契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
