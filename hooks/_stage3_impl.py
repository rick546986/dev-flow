"""_stage3_impl.py — Stage 3 觸發判定 / Demo verdict 機械驗證器(OC-2B;P2 Operational)。

正本:方法論 repo `notes/design/vnext-shared-contract.md` §2(G2 Demo verdict 條件)、
`_templates/{1-discussion,3-prototype}.md`(Real-world Context / 觸發判定 / User Demo
Feedback 結構)、`scripts/check-realworld.sh`(檢查語意)。本檔只做機械讀取與判定,
不做語意猜測;語意判斷(九條觸發是否命中)由人/agent 在 3-prototype 落檔,本檔驗記錄。

判定矩陣(docs/dev/<slug>/ 底下):
1. feature 目錄不存在 → exit 1(用法錯誤,防 typo 誤判)。
2. 3-prototype.md 存在:
   a. 含「## Stage 3 觸發判定」節(≥1 個 checkbox 行才算有效記錄):
      - 檔內含 `test-only human fixture` 字樣且未帶 --accept-test-fixture
        → REJECT(測試 fixture 不得產生正式 PASS)。
      - 命中 0 條 → PASS(N/A:全未勾清單即「無 trigger + 明確原因」記錄)。
      - 命中 ≥1 條 → 看 Human verdict(取最後一個非佔位行):
        - ACCEPTED → 必須伴隨人類 attestation 行
          `- Verdict attestation: human:<姓名> @ <YYYY-MM-DD>`;缺/格式不符 →
          REJECT(**Agent 不得自行填入 ACCEPTED** 的機械防線)。
        - REVISE → REJECT(必須重做 Demo;Owner Call 不得繞過)。
        - NOT_REVIEWED / 未填 → 2-decision「## Owner Calls」節有含
          「Stage 3」+「跳過/skip/略過」的行 → PASS(SKIPPED_OWNER_CALL);
          否則 REJECT。
   b. 無觸發判定節:1-discussion 有「## Real-world Context」→ REJECT(VNext 檔須
      補判定節);沒有 → legacy PASS(不誤殺舊 feature)。
3. 3-prototype.md 不存在:
   a. 2-decision Owner Call 跳過記錄 → PASS(SKIPPED_OWNER_CALL)。
   b. 1-discussion 不存在 → PASS(N/A:fast lane 或 legacy,Stage 1–3 本就不跑)。
   c. 1-discussion 無 Real-world Context 節 → legacy PASS。
   d. 1-discussion 有 Real-world Context 節 → REJECT(觸發判定未記錄)。

attestation 防線的誠實邊界:本機制是 tripwire 不是密碼學證明 —— 擋的是「agent 照模板
順手填 ACCEPTED」的預設失敗模式(模板不含 attestation 行,SKILL 明令 Agent 禁寫該行);
蓄意造假無法機械攔截,由 G2 人審與 author≠approver 把關。committed 範例 / 測試 fixture
一律要含 `test-only human fixture` 字樣 → 正式模式必拒,fixture 永遠不可能誤過正式判定。

exit code:0 = G2 Demo verdict 可過(含 N/A / legacy / Owner Call 跳過);
2 = 拒(G2 不得過);1 = 用法 / IO 錯誤。
stdout = 單一 JSON(schema stage3-verdict-v1);stderr = 一行人讀摘要。
用法:python3 _stage3_impl.py <slug> [--root <repo-root>] [--accept-test-fixture]
"""
import json
import os
import re
import sys

sys.dont_write_bytecode = True   # 對齊 _obs/_doctor:不落 __pycache__

SCHEMA = "stage3-verdict-v1"
TEST_FIXTURE_MARKER = "test-only human fixture"
VERDICT_ENUM = ("ACCEPTED", "REVISE", "NOT_REVIEWED")
PLACEHOLDER = re.compile(r"ACCEPTED\s*\|\s*REVISE\s*\|\s*NOT_REVIEWED")
# G3(2026-08-17):三個冒號字元集曾各是兩個半形 0x3a(本想寫「:或：」),
# 人類確認用全形冒號寫會解析不到 → 判成沒填。現值:半形 0x3a + 全形 0xff1a。
VERDICT_LINE = re.compile(r"Human verdict\s*[:：]\s*(.+)$")
ATTEST_LINE = re.compile(r"^\s*-\s*Verdict attestation\s*[:：]\s*(\S.*)$")
ATTEST_HUMAN = re.compile(r"^human\s*[:：]\s*\S.*@\s*\d{4}-\d{2}-\d{2}")
CHECKBOX = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(.+?)\s*$")
OC_SKIP_WORDS = re.compile(r"跳過|略過|skip", re.IGNORECASE)
OC_STAGE3 = re.compile(r"Stage\s*3", re.IGNORECASE)


def read_file(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as stream:
        return stream.read()


def section(text, heading_prefix):
    """切出 `## <heading_prefix>…` 到下一個 `## ` 之間的內文(標題可帶尾註)。"""
    pattern = re.compile(
        rf"^##\s*{re.escape(heading_prefix)}.*?\n(.*?)(?=^##\s|\Z)", re.M | re.S)
    match = pattern.search(text)
    return match.group(1) if match else None


def parse_checklist(body):
    """回傳 (checkbox 總數, 命中清單)。"""
    hits = []
    total = 0
    for line in body.splitlines():
        match = CHECKBOX.match(line)
        if not match:
            continue
        total += 1
        if match.group(1) in ("x", "X"):
            hits.append(match.group(2))
    return total, hits


def parse_verdict(text):
    """取最後一個非佔位的 Human verdict 行;容忍尾註(如「(第 2 輪…)」)。"""
    found = None
    for line in text.splitlines():
        match = VERDICT_LINE.search(line)
        if not match or PLACEHOLDER.search(match.group(1)):
            continue
        value = re.search(r"\b(ACCEPTED|REVISE|NOT_REVIEWED)\b", match.group(1))
        if value:
            found = value.group(1)
    return found


def parse_attestation(text):
    """回傳最後一個 attestation 行原文;無 → None。"""
    found = None
    for line in text.splitlines():
        match = ATTEST_LINE.match(line)
        if match:
            found = match.group(1).strip()
    return found


def find_owner_call_skip(decision_text):
    """在 2-decision「## Owner Calls」節找同時含 Stage 3 與 跳過/skip 的行。"""
    if decision_text is None:
        return None
    body = section(decision_text, "Owner Calls")
    if body is None:
        return None
    for line in body.splitlines():
        if OC_STAGE3.search(line) and OC_SKIP_WORDS.search(line):
            return line.strip()
    return None


def frontmatter_status(text):
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    status = re.search(r"^status:\s*(\S+)", match.group(1), re.M)
    return status.group(1) if status else None


def emit(result, exit_code):
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"stage3({result['slug']}): {result['g2_demo']} — {result['reason']}",
          file=sys.stderr)
    sys.exit(exit_code)


def main(argv):
    slug = None
    root = "."
    accept_test_fixture = False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--root":
            if i + 1 >= len(argv):
                print("⛔ --root 需要路徑參數", file=sys.stderr)
                sys.exit(1)
            root = argv[i + 1]
            i += 2
        elif arg == "--accept-test-fixture":
            accept_test_fixture = True
            i += 1
        elif arg.startswith("-"):
            print(f"⛔ 未知參數:{arg}", file=sys.stderr)
            sys.exit(1)
        elif slug is None:
            slug = arg
            i += 1
        else:
            print(f"⛔ 多餘參數:{arg}", file=sys.stderr)
            sys.exit(1)
    if not slug:
        print("⛔ 用法:_stage3_impl.py <slug> [--root <repo-root>]"
              " [--accept-test-fixture]", file=sys.stderr)
        sys.exit(1)

    feature_dir = os.path.join(root, "docs", "dev", slug)
    if not os.path.isdir(feature_dir):
        print(f"⛔ 找不到 feature 目錄:{feature_dir}", file=sys.stderr)
        sys.exit(1)

    disc = read_file(os.path.join(feature_dir, "1-discussion.md"))
    decision = read_file(os.path.join(feature_dir, "2-decision.md"))
    proto = read_file(os.path.join(feature_dir, "3-prototype.md"))

    has_rwc = disc is not None and re.search(r"^##\s*Real-world Context", disc, re.M)
    owner_call = find_owner_call_skip(decision)

    result = {
        "schema": SCHEMA,
        "slug": slug,
        "legacy": False,
        "trigger": None,
        "trigger_hits": [],
        "trigger_source": None,
        "verdict": None,
        "verdict_attestation": None,
        "owner_call": owner_call,
        "prototype_status": frontmatter_status(proto) if proto else None,
        "g2_demo": None,
        "reason": None,
    }

    def verdict_pass(reason, **extra):
        result.update(extra)
        result["g2_demo"] = "PASS"
        result["reason"] = reason
        emit(result, 0)

    def verdict_reject(reason, **extra):
        result.update(extra)
        result["g2_demo"] = "REJECT"
        result["reason"] = reason
        emit(result, 2)

    # ── 3-prototype 不存在 ──
    if proto is None:
        if owner_call:
            verdict_pass(
                f"Stage 3 由 2-decision Owner Call 明示跳過:「{owner_call}」→ 可過 G2",
                trigger_source="owner-call")
        if disc is None:
            verdict_pass("無 1-discussion 與 3-prototype(fast lane 或 legacy)"
                         "→ Demo verdict N/A,可過 G2", trigger_source="fast-lane")
        if not has_rwc:
            verdict_pass("legacy feature(1-discussion 無 Real-world Context 節)"
                         "→ Demo verdict N/A,可過 G2,不套用 VNext 條件",
                         legacy=True, trigger_source="legacy")
        verdict_reject(
            "Stage 3 觸發判定未記錄:1-discussion 已有 Real-world Context(VNext 檔)"
            "但無 3-prototype 觸發判定、亦無 2-decision Owner Call 跳過記錄 → 不得過 G2"
            "(補 3-prototype 填觸發判定,全未命中亦落檔即為 N/A 記錄;或由人類明示跳過"
            "並記 Owner Call)", trigger_source="unrecorded")

    # ── 3-prototype 存在 ──
    checklist_body = section(proto, "Stage 3 觸發判定")
    total_boxes, hits = (0, [])
    if checklist_body is not None:
        total_boxes, hits = parse_checklist(checklist_body)

    if checklist_body is None or total_boxes == 0:
        if has_rwc:
            verdict_reject(
                "3-prototype 缺「Stage 3 觸發判定」節(1-discussion 已有 Real-world "
                "Context,適用 VNext 規則)→ 不得過 G2,須補觸發判定記錄",
                trigger_source="unrecorded")
        verdict_pass("legacy feature(1-discussion 無 Real-world Context 節、"
                     "3-prototype 為舊模板無觸發判定節)→ Demo verdict N/A,可過 G2",
                     legacy=True, trigger_source="legacy")

    result["trigger_source"] = "3-prototype-checklist"
    result["trigger_hits"] = hits
    result["trigger"] = bool(hits)

    if TEST_FIXTURE_MARKER in proto and not accept_test_fixture:
        verdict_reject(
            f"3-prototype 含「{TEST_FIXTURE_MARKER}」標記:測試 fixture 不得用於"
            "正式判定,一律拒收(僅 selftest 帶 --accept-test-fixture 可收)")

    if not hits:
        verdict_pass(f"觸發判定 0/{total_boxes} 命中(全未勾清單即 N/A + 明確原因記錄)"
                     "→ Demo verdict N/A,可過 G2")

    verdict = parse_verdict(proto)
    result["verdict"] = verdict or "NOT_REVIEWED"
    attestation = parse_attestation(proto)

    if verdict == "ACCEPTED":
        if attestation and (ATTEST_HUMAN.match(attestation)
                            or (accept_test_fixture
                                and TEST_FIXTURE_MARKER in attestation)):
            result["verdict_attestation"] = (
                "test-fixture" if TEST_FIXTURE_MARKER in attestation else "human")
            verdict_pass(f"觸發判定命中 {len(hits)} 條,Human verdict: ACCEPTED"
                         " + 人類 attestation → 可過 G2")
        result["verdict_attestation"] = "invalid" if attestation else "missing"
        verdict_reject(
            "Human verdict: ACCEPTED 但缺有效人類 attestation 行"
            "(要求 `- Verdict attestation: human:<姓名> @ <YYYY-MM-DD>`,由人類親自輸入)"
            "→ Agent 不得自行填入 ACCEPTED,拒收")

    if verdict == "REVISE":
        verdict_reject("Human verdict: REVISE → 不得過 G2,必須修改後重新 Demo"
                       "(Owner Call 不得繞過 REVISE)")

    # NOT_REVIEWED 或未填(未 Demo = NOT_REVIEWED,不得視同 ACCEPTED)
    if owner_call:
        verdict_pass(
            f"觸發判定命中 {len(hits)} 條、未完成 Demo(NOT_REVIEWED),但 2-decision "
            f"Owner Call 明示跳過:「{owner_call}」→ 可過 G2", trigger_source="owner-call")
    verdict_reject(
        f"觸發判定命中 {len(hits)} 條但 Human verdict 未填或 NOT_REVIEWED,"
        "且無 Owner Call 跳過記錄 → 不得過 G2(未 Demo = NOT_REVIEWED ≠ ACCEPTED)")


if __name__ == "__main__":
    main(sys.argv[1:])
