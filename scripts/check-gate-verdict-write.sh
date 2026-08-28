#!/bin/bash
# check-gate-verdict-write.sh — Human gate verdict 寫入契約牙
#
# 咬什麼:notes/design/gate-verdict-write.md 丟了鎖死句子
# (md 頂欄 verdict: 是正本／提交判定／全勾不算 PASS／sidecar 不是正本／
# md 勝／不得手改／File System Access／dev-flow gate serve),
# 或 hop／產生器／寫入器不再點名這些句,必須紅。
#
# 另跑 write + serve POST 實測:寫的是 md verdict:,sidecar 衝突時 md 勝。
# 不把判定做成 build-gate-twin 第六個 stage。補助產品詞不得當通用規則。
#
# 用法:
#   scripts/check-gate-verdict-write.sh [root]
# exit:0 = 全過 / 1 = 契約句丟了或寫入錯 / 2 = 環境或用法失敗

set -uo pipefail

SELF=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" "$SELF" <<'PY'
import importlib.util
import json
import os
import re
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

root = sys.argv[1]
self_dir = sys.argv[2]
CONTRACT = "notes/design/gate-verdict-write.md"
BUILDER = "scripts/build-gate-twin.py"
HELPER = "scripts/devflow_gate.py"
HOPS = (
    "skills/dev-flow/stage7/nodes/N5-verdict.md",
    "skills/dev-flow/stage2/nodes/N7-g1.md",
    "skills/dev-flow/stage4/nodes/N7-end.md",
    "skills/dev-flow/SKILL.md",
)
TEMPLATES = (
    "_templates/2-decision.md",
    "_templates/4-spec.md",
    "_templates/7-review.md",
)

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
    "提交判定",
    "全勾不算 PASS",
    "verdict:",
    "md 勝",
    "sidecar 不是正本",
    "不得手改",
    "File System Access",
    "dev-flow gate serve",
    "localStorage",
    "PASS",
    "REQUEST_CHANGES",
    "HOLD",
    "7-review.md",
    "2-decision.md",
    "4-spec.md",
)

HOP_NEEDLES = (
    "提交判定",
    "全勾不算 PASS",
    "不得手改",
    "verdict:",
    "尚無寫入",
    "md 勝",
)

BUILDER_NEEDLES = (
    "提交判定",
    "全勾不算 PASS",
    "File System Access",
    "devflow_gate.py serve",
    "GATE_STAGES",
    "patchMd",
)

HELPER_NEEDLES = (
    "verdict:",
    "PASS",
    "REQUEST_CHANGES",
    "HOLD",
    "md 勝",
    "/devflow-gate/verdict",
    "Human verdict note",
)

FORBIDDEN = (
    "PLUS",
    "形成併取卵",
    "27004",
    "apply_date",
)


def judge(contract_text, hop_texts, builder_text, helper_text, template_texts):
    local = []

    def fail(label):
        local.append(label)

    if contract_text is None:
        fail("契約存在 " + CONTRACT)
        return local
    if "鎖死" not in contract_text:
        fail("契約標題／本文含「鎖死」")
    for needle in CONTRACT_NEEDLES:
        if needle not in contract_text:
            fail("契約含「%s」" % needle)
    for bad in FORBIDDEN:
        if bad in contract_text:
            fail("契約未把補助產品詞「%s」寫成通用規則" % bad)

    for rel, text in hop_texts.items():
        if text is None:
            fail("%s 存在" % rel)
            continue
        for needle in HOP_NEEDLES:
            if needle not in text:
                fail("%s 含「%s」" % (rel, needle))
        if "不得手改" not in text:
            fail("%s 含「不得手改」" % rel)

    if builder_text is None:
        fail("%s 存在" % BUILDER)
    else:
        for needle in BUILDER_NEEDLES:
            if needle not in builder_text:
                fail("產生器含「%s」" % needle)
        if re.search(r"STAGES\s*=\s*\([^)]*verdict", builder_text):
            fail("產生器未把判定做成 STAGES 第六個 stage")
        if "5-tasks" in builder_text and "GATE_STAGES" in builder_text:
            if "GATE_STAGES = (\"2-decision\", \"4-spec\", \"7-review\")" not in builder_text:
                fail("GATE_STAGES 只含三個 gate,不含 5-tasks")

    if helper_text is None:
        fail("%s 存在" % HELPER)
    else:
        for needle in HELPER_NEEDLES:
            if needle not in helper_text:
                fail("寫入器含「%s」" % needle)

    for rel, text in template_texts.items():
        if text is None:
            fail("%s 存在" % rel)
        elif "verdict:" not in text:
            fail("%s 含頂欄 verdict:" % rel)
    return local


contract_text = read(CONTRACT)
builder_text = read(BUILDER)
helper_text = read(HELPER)
hop_texts = {rel: read(rel) for rel in HOPS}
template_texts = {rel: read(rel) for rel in TEMPLATES}

check(contract_text is not None, "契約存在 " + CONTRACT)
check(builder_text is not None, "產生器存在 " + BUILDER)
check(helper_text is not None, "寫入器存在 " + HELPER)
for rel in HOPS:
    check(hop_texts[rel] is not None, "hop 存在 " + rel)

for item in judge(contract_text, hop_texts, builder_text, helper_text, template_texts):
    check(False, item)

if contract_text is not None:
    stripped = contract_text.replace("提交判定", "")
    check(bool(judge(stripped, hop_texts, builder_text, helper_text, template_texts)),
          "牙咬:契約刪「提交判定」必須紅")
    stripped = contract_text.replace("全勾不算 PASS", "")
    check(bool(judge(stripped, hop_texts, builder_text, helper_text, template_texts)),
          "牙咬:契約刪「全勾不算 PASS」必須紅")
    stripped = contract_text.replace("md 勝", "")
    check(bool(judge(stripped, hop_texts, builder_text, helper_text, template_texts)),
          "牙咬:契約刪「md 勝」必須紅")
    poisoned = contract_text + "\n形成併取卵\n"
    check(bool(judge(poisoned, hop_texts, builder_text, helper_text, template_texts)),
          "牙咬:契約寫入補助產品詞必須紅")
    hop0 = hop_texts[HOPS[0]]
    if hop0 is not None:
        hop_stripped = dict(hop_texts)
        hop_stripped[HOPS[0]] = hop0.replace("不得手改", "", 1)
        check(bool(judge(contract_text, hop_stripped, builder_text, helper_text, template_texts)),
              "牙咬:N5-verdict 刪「不得手改」必須紅")

# ── 寫入器實測:md 是正本,sidecar 衝突時 md 勝 ──
spec = importlib.util.spec_from_file_location(
    "devflow_gate", os.path.join(root, HELPER)
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

md_src = """---
feature: demo
stage: 7-review
status: draft
verdict:
owner: x
---

# 7. 驗證
"""
with tempfile.TemporaryDirectory() as tmp:
    slug_dir = Path(tmp) / "docs" / "dev" / "demo"
    slug_dir.mkdir(parents=True)
    md = slug_dir / "7-review.md"
    md.write_text(md_src, encoding="utf-8")
    result = gate.write_verdict(
        Path(tmp), "demo", "7-review", "HOLD",
        notes="wait", reviewer="ada", checked=["S-1", "S-2"],
        source_sha="deadbeef", sidecar=True,
    )
    got = md.read_text(encoding="utf-8")
    check(result["verdict"] == "HOLD", "write:回傳 verdict=HOLD")
    check(re.search(r"^verdict:\s*HOLD\s*$", got, re.M) is not None,
          "write:md 頂欄 verdict: HOLD")
    check("- Human verdict note: wait" in got, "write:可寫一行 Human verdict note")
    side = slug_dir / "7-review.verdict.json"
    check(side.is_file(), "write:可另寫選配 sidecar")
    # sidecar 說 PASS、md 說 HOLD → 正本仍是 md
    side.write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")
    check(gate.read_canonical_verdict(md.read_text(encoding="utf-8")) == "HOLD",
          "sidecar 與 md 衝突時 md 勝")
    # 全勾不是寫入 API 的預設 PASS。條件必須能假:接受非法值、或拒了卻改 md,都紅。
    md.write_text(md_src, encoding="utf-8")
    before = md.read_text(encoding="utf-8")
    rejected = False
    try:
        gate.write_verdict(Path(tmp), "demo", "7-review", "ALL_CHECKED")
    except ValueError:
        rejected = True
    after = md.read_text(encoding="utf-8")
    check(
        rejected
        and after == before
        and gate.read_canonical_verdict(after) == "",
        "write:全勾／非法值必須拒收,且不得改 md",
    )

    # serve POST
    md.write_text(md_src, encoding="utf-8")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), gate.make_handler(Path(tmp)))
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        req = Request(
            "http://127.0.0.1:%d/devflow-gate/verdict" % port,
            data=json.dumps({
                "slug": "demo",
                "gate": "7-review",
                "verdict": "PASS",
                "notes": "ok",
                "reviewer": "bea",
                "checked": ["S-1"],
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        after = md.read_text(encoding="utf-8")
        check(body.get("verdict") == "PASS", "serve POST:回傳 PASS")
        check(re.search(r"^verdict:\s*PASS\s*$", after, re.M) is not None,
              "serve POST:寫入 md 頂欄 verdict: PASS")
        check("- Human verdict note: ok" in after, "serve POST:可寫一行 note")
    finally:
        httpd.shutdown()

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:Human gate verdict 寫入契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
