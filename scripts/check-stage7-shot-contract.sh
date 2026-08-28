#!/bin/bash
# check-stage7-shot-contract.sh — 第 7 站審查頁截圖槽契約牙
#
# 咬什麼:notes/design/stage7-review-ui-contract.md 丟了鎖死句子
# (分組／data-shot／shots/／進場／已存在／不准新增／lightbox 或點圖／
# chrome 三件／.r-block／mermaid 禁／ASCII 禁),
# 或模板／S2e-walkthrough 不再點名進場+檔名,必須紅。
#
# 不產 HTML、不發明產檔器、不改 twin、不取代 check-vbox-fig.sh／
# check-devstage7-graph.sh。補助產品詞不得當通用規則寫進契約。
# 不要求 IVF 檔名(那些留在 example/subsidy-3-0-plus)。
#
# 用法:
#   scripts/check-stage7-shot-contract.sh [root]
# exit:0 = 全過 / 1 = 契約句丟了 / 2 = 環境或用法失敗

set -uo pipefail

SELF=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import os
import re
import sys

root = sys.argv[1]
CONTRACT = "notes/design/stage7-review-ui-contract.md"
TEMPLATE = "_templates/7-review.md"
HOP = "skills/dev-flow/stage7/nodes/S2e-walkthrough.md"

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


# 契約必須出現的句子(鎖死,不是口味)。刪任何一條,這支要紅。
CONTRACT_NEEDLES = (
    "分組",
    "data-shot",
    "shots/",
    "進場",
    "已存在",
    "不准新增",
    "--ground",
    "--panel",
    "--accent",
    ".r-block",
    "mermaid 禁",
    "ASCII 禁",
    "產檔器這輪不做",
    "不產 HTML",
    "不發明產檔器",
    "不改 twin",
)

# 契約正本不得拿補助產品詞當通用規則。IVF 檔名留在 example/subsidy-3-0-plus。
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
)

HOP_NEEDLES = (
    "進場",
    "已存在",
    "不准新增",
    "data-shot",
    "shots/",
    "notes/design/stage7-review-ui-contract.md",
)

HOP_DONE_NEEDLES = (
    "進場",
    "已存在",
    "不准新增",
    "未完成",
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
    section = heading + "\n" + body
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


contract_text = read(CONTRACT)
template_text = read(TEMPLATE)
hop_text = read(HOP)

check(contract_text is not None, "契約存在 " + CONTRACT)
check(template_text is not None, "模板存在 " + TEMPLATE)
check(hop_text is not None, "hop 存在 " + HOP)

for item in judge(contract_text, template_text, hop_text):
    check(False, item)

# 牙自己咬壞契約:同一把 judge,丟句子或塞補助詞必須判紅,否則這支是空殼。
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
    poisoned = contract_text + "\nPLUS\n"
    check(bool(judge(poisoned, template_text, hop_text)),
          "牙咬:契約寫入補助產品詞必須紅")
    hop_stripped = hop_text.replace("未完成", "", 1)
    check(bool(judge(contract_text, template_text, hop_stripped)),
          "牙咬:S2e-walkthrough 完成條件刪「未完成」必須紅")

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:第 7 站審查頁截圖槽契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
