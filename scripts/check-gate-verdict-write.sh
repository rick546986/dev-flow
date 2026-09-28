#!/bin/bash
# check-gate-verdict-write.sh — Human gate verdict 寫入契約牙
#
# 咬什麼:notes/design/gate-verdict-write.md 丟了鎖死句子
# (md 頂欄 verdict: 是正本／提交判定／全勾不算 PASS／sidecar 不是正本／
# md 勝／不得手改／File System Access／dev-flow gate serve／verdict_source／attested_by),
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
    "verdict_source:",
    "attested_by:",
    "unverified",
    "不得寫 `verdict:`",
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
        else:
            for field in ("verdict_source:", "attested_by:"):
                if field not in text:
                    fail("%s 含頂欄 %s(P3-2 出處欄)" % (rel, field))
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
    stripped = contract_text.replace("verdict_source:", "")
    check(bool(judge(stripped, hop_texts, builder_text, helper_text, template_texts)),
          "牙咬:契約刪「verdict_source:」必須紅(P3-2)")
    tpl_stripped = dict(template_texts)
    tpl_stripped[TEMPLATES[2]] = (template_texts[TEMPLATES[2]] or "").replace("attested_by:", "")
    check(bool(judge(contract_text, hop_texts, builder_text, helper_text, tpl_stripped)),
          "牙咬:7-review 模板刪「attested_by:」必須紅(P3-2)")
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
    check(re.search(r"^verdict_source:\s*human_attested\s*$", got, re.M) is not None
          and re.search(r"^attested_by:\s*human:ada\s*$", got, re.M) is not None,
          "write:有 reviewer 時代填 verdict_source: human_attested + attested_by: human:<reviewer>(P3-2)")
    agent_rejected = False
    try:
        gate.write_verdict(Path(tmp), "demo", "7-review", "PASS", reviewer="agent:jev-1")
    except ValueError:
        agent_rejected = True
    check(agent_rejected and gate.read_canonical_verdict(md.read_text(encoding="utf-8")) == "HOLD",
          "write:reviewer 是 agent/Jev 必須拒收且不改 md(P3-2:Jev 不得寫 verdict)")
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

    # serve POST(CSRF／DNS rebinding 收緊:Host／Origin 限本機、只收 JSON、必帶啟動 token;不送 CORS `*`)
    import http.client
    md.write_text(md_src, encoding="utf-8")
    token = gate.new_serve_token()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), gate.make_handler(Path(tmp), token))
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    payload = json.dumps({"slug": "demo", "gate": "7-review", "verdict": "PASS", "notes": "ok",
                          "reviewer": "bea", "checked": ["S-1"]}).encode("utf-8")

    def call(method, path, headers, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        try:
            conn.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
            for key, value in headers.items():
                conn.putheader(key, value)
            if body is not None:
                conn.putheader("Content-Length", str(len(body)))
            conn.endheaders(body)
            resp = conn.getresponse()
            return resp.status, dict((k.lower(), v) for k, v in resp.getheaders()), resp.read()
        finally:
            conn.close()

    good = {"Host": "127.0.0.1:%d" % port, "Origin": "http://127.0.0.1:%d" % port,
            "Content-Type": "application/json", gate.TOKEN_HEADER: token}
    try:
        # 負向:每一種都必須被拒,而且 md 不得被改
        negatives = (
            ("缺 token", dict((k, v) for k, v in good.items() if k != gate.TOKEN_HEADER), 403),
            ("token 不符", dict(good, **{gate.TOKEN_HEADER: token[:-2] + "xx"}), 403),
            ("Origin 是別的網站", dict(good, Origin="https://evil.example"), 403),
            ("Origin: null(file:// / sandbox)", dict(good, Origin="null"), 403),
            ("Origin 是本機別的 port", dict(good, Origin="http://localhost:%d" % (port + 1)), 403),
            ("Host 不是本機(DNS rebinding)", dict(good, Host="evil.example:%d" % port), 403),
            ("Sec-Fetch-Site: cross-site", dict(good, **{"Sec-Fetch-Site": "cross-site"}), 403),
            ("Content-Type text/plain(simple request)", dict(good, **{"Content-Type": "text/plain"}), 415),
            ("Content-Type form", dict(good, **{"Content-Type": "application/x-www-form-urlencoded"}), 415),
        )
        for label, headers, want in negatives:
            status, _, _ = call("POST", "/devflow-gate/verdict", headers, payload)
            after = md.read_text(encoding="utf-8")
            check(status == want and gate.read_canonical_verdict(after) == "",
                  "serve 拒收:%s → %d 且不改 md(實得 %d)" % (label, want, status))
        status, hdrs, _ = call("OPTIONS", "/devflow-gate/verdict",
                               {"Host": "127.0.0.1:%d" % port, "Origin": "https://evil.example"})
        check(status == 403 and "access-control-allow-origin" not in hdrs,
              "serve OPTIONS:別的網站 preflight → 403、無 CORS 放行")
        status, hdrs, _ = call("GET", "/docs/dev/demo/7-review.md", {"Host": "evil.example:%d" % port})
        check(status == 403 and "set-cookie" not in hdrs, "serve GET:Host 不是本機 → 403、不發 token cookie")

        # 正向:同源頁 GET 拿到 SameSite=Strict HttpOnly cookie,只帶 cookie 就能寫(twin 頁不用改 JS)
        status, hdrs, _ = call("GET", "/docs/dev/demo/7-review.md", {"Host": "localhost:%d" % port})
        cookie = hdrs.get("set-cookie", "")
        check(status == 200 and ("%s=%s" % (gate.TOKEN_COOKIE, token)) in cookie
              and "SameSite=Strict" in cookie and "HttpOnly" in cookie
              and "access-control-allow-origin" not in hdrs,
              "serve GET:同源發 SameSite=Strict HttpOnly token cookie、不送 CORS `*`")
        cookie_headers = {"Host": "localhost:%d" % port, "Origin": "http://localhost:%d" % port,
                          "Sec-Fetch-Site": "same-origin", "Content-Type": "application/json; charset=utf-8",
                          "Cookie": "other=1; %s=%s" % (gate.TOKEN_COOKIE, token)}
        status, hdrs, raw = call("POST", "/devflow-gate/verdict", cookie_headers, payload)
        body = json.loads(raw.decode("utf-8")) if status == 200 else {}
        after = md.read_text(encoding="utf-8")
        check(status == 200 and body.get("verdict") == "PASS" and "access-control-allow-origin" not in hdrs,
              "serve POST(同源 + cookie token):回傳 PASS、不送 CORS `*`")
        check(re.search(r"^verdict:\s*PASS\s*$", after, re.M) is not None,
              "serve POST:寫入 md 頂欄 verdict: PASS")
        check("- Human verdict note: ok" in after, "serve POST:可寫一行 note")
        # 正向:CLI／curl 走 header token、無 Origin
        md.write_text(md_src, encoding="utf-8")
        status, _, _ = call("POST", "/devflow-gate/verdict",
                            dict((k, v) for k, v in good.items() if k != "Origin"), payload)
        check(status == 200 and gate.read_canonical_verdict(md.read_text(encoding="utf-8")) == "PASS",
              "serve POST(header token、無 Origin):寫入 PASS")
        check(gate.new_serve_token() != token, "serve token 每次啟動重產")
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
