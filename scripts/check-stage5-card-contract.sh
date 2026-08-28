#!/bin/bash
# check-stage5-card-contract.sh — 第 5 站審頁任務卡契約牙
#
# 咬什麼:notes/design/stage5-review-ui-contract.md §版面鎖死 丟了鎖死句子
# (.r-block／nowrap／T-n／未完成／不要底線／卡文全寬／提交判定／chrome),
# 或模板／產檔器消失／5-tasks 加了提交判定,必須紅。
#
# 產檔器:`scripts/build-stage5-html.py`。不進 build-gate-twin.py STAGES、
# 不包 html-shell。補助產品詞不得當通用規則。
#
# 用法:
#   scripts/check-stage5-card-contract.sh [root]
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
TEMPLATE = "_templates/5-tasks.md"
HOP = "skills/dev-flow/stage5/nodes/N5-twin.md"
BUILDER = "scripts/build-stage5-html.py"
FIXTURE = "scripts/fixtures/stage5-html/tasks-page.md"
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
    if text is None:
        return None, None
    match = re.search(
        rf"^(## {re.escape(prefix)}[^\n]*)\n(.*?)(?=^## |\Z)",
        text, re.M | re.S,
    )
    if not match:
        return None, None
    return match.group(1), match.group(2)


SECTION_NEEDLES = (
    ".r-block",
    "nowrap",
    "T-n",
    "未完成",
    "不要底線",
    "全寬",
    "提交判定",
    "--ground",
    "--panel",
    "--accent",
    "--ok-soft",
    "--bad-soft",
    ".masthead",
    ".dash",
    ".cell",
    "build-stage5-html.py",
    "--action",
    "html-shell",
    "62ch",
)

FORBIDDEN = (
    "PLUS",
    "兩格",
    "形成併取卵",
    "27004",
    "apply_date",
)

TEMPLATE_NEEDLES = (
    "build-stage5-html.py",
    "notes/design/stage5-review-ui-contract.md",
    "nowrap",
    "提交判定",
)

HOP_NEEDLES = (
    "build-stage5-html.py",
    "notes/design/stage5-review-ui-contract.md",
)

OUTPUT_NEEDLES = (
    "r-block",
    "nowrap",
    "T-1",
    "未完成",
    "text-decoration:none",
    "--ground",
    "--panel",
    "--accent",
    "masthead",
    "dash",
    "cell",
    "t-line",
)


def judge(contract_text, template_text, hop_text):
    local = []
    heading, body = heading_and_body(contract_text, "版面鎖死")
    if heading is None or body is None:
        local.append("契約有「## 版面鎖死」節")
        return local
    section = heading + "\n" + body
    for needle in SECTION_NEEDLES:
        if needle not in section:
            local.append("§版面鎖死 含「%s」" % needle)
    for bad in FORBIDDEN:
        if bad in (contract_text or ""):
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
                local.append("N5-twin 含「%s」" % needle)
    return local


def has_verdict_submit(html_text):
    return bool(
        re.search(r"<button[^>]*>\s*提交判定", html_text or "")
        or 'id="gv-submit"' in (html_text or "")
        or 'id="gate-verdict"' in (html_text or "")
    )


def looks_like_shell_article(html_text):
    if "t-line" in html_text and "r-block" in html_text and not has_verdict_submit(html_text):
        return False
    return "html-shell" in html_text or has_verdict_submit(html_text)


def judge_html(html_text, label):
    issues = []
    if looks_like_shell_article(html_text):
        issues.append("是 html-shell 或加了提交判定")
    for needle in OUTPUT_NEEDLES:
        if needle not in html_text:
            issues.append("缺「%s」" % needle)
    if has_verdict_submit(html_text):
        issues.append("5-tasks 加了提交判定")
    if re.search(r"\.r-body[^}]*max-width:\s*62ch", html_text):
        issues.append("卡文被 62ch 卡住")
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
    check('id="gv-submit"' not in builder_text
          and 'id="gate-verdict"' not in builder_text,
          "產檔器不加判定提交器")

if gate_text is not None:
    stages = re.search(r"^STAGES\s*=\s*\((.*?)\)", gate_text, re.S | re.M)
    stage_blob = stages.group(1) if stages else ""
    check("5-tasks" in stage_blob,
          "build-gate-twin.py STAGES 仍含執行板 5-tasks(審頁不改這張表)")

if check_text is not None:
    check("check-stage5-card-contract.sh" in check_text,
          "產檔器牙已掛進 devflow-check.sh")

if contract_text is not None and template_text is not None and hop_text is not None:
    stripped = contract_text.replace("nowrap", "")
    check(bool(judge(stripped, template_text, hop_text)),
          "牙咬:§版面鎖死 刪「nowrap」必須紅")
    stripped_t = contract_text.replace("提交判定", "")
    check(bool(judge(stripped_t, template_text, hop_text)),
          "牙咬:§版面鎖死 刪「提交判定」必須紅")
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
    check(html_out.count("t-line") >= 2, "fixture 至少兩張 T 卡同行 nowrap")
    check(not has_verdict_submit(html_out), "fixture 不加提交判定器")
    fake = html_out + '<button type="button">提交判定</button>'
    fake_ok, _ = judge_html(fake, "加提交判定")
    check(not fake_ok, "牙咬:5-tasks 加提交判定必須紅")
else:
    check(False, "產檔器存在且可跑 " + BUILDER)

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:第 5 站審頁任務卡契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
