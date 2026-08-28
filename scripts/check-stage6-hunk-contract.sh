#!/bin/bash
# check-stage6-hunk-contract.sh — 第 6 站審碼 hunk 顯示契約牙
#
# 咬什麼:notes/design/stage5-review-ui-contract.md §第6站審碼 丟了鎖死句子
# (改什麼／T-n／關聯／.ln.add／--ok-soft／不准發明 minus／chrome 三件),
# 或模板／S2-tdd 完成條件不再點名這些欄,必須紅。
#
# 不產 HTML、不發明產檔器、不改 twin、不取代 check-vbox-fig.sh／
# check-devstage6-graph.sh。補助產品詞不得當通用規則寫進契約。
#
# 用法:
#   scripts/check-stage6-hunk-contract.sh [root]
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
CONTRACT = "notes/design/stage5-review-ui-contract.md"
TEMPLATE = "_templates/6-implementation-notes.md"
HOP = "skills/dev-flow/stage6/nodes/S2-tdd.md"

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
    "產檔器這輪不做",
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
)

HOP_DONE_NEEDLES = (
    "改什麼",
    "T-n",
    "關聯",
    "色碼",
    "未完成",
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
    stripped = contract_text.replace("改什麼", "")
    check(bool(judge(stripped, template_text, hop_text)),
          "牙咬:§第6站審碼 刪「改什麼」必須紅")
    stripped_ln = contract_text.replace(".ln.add", "")
    check(bool(judge(stripped_ln, template_text, hop_text)),
          "牙咬:§第6站審碼 刪「.ln.add」必須紅")
    poisoned = contract_text + "\n形成併取卵\n"
    check(bool(judge(poisoned, template_text, hop_text)),
          "牙咬:契約寫入補助產品詞必須紅")
    hop_stripped = hop_text.replace("未完成", "", 1)
    check(bool(judge(contract_text, template_text, hop_stripped)),
          "牙咬:S2-tdd 完成條件刪「未完成」必須紅")

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:第 6 站審碼 hunk 契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
