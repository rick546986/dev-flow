#!/bin/bash
# Real-world interaction / Stage 3 Demo checks (Workstream B, 2026-08-02).
# 驗 prompt-b 十二節:Real-world Context 欄位、Assumption/Evidence 區分、Stage 3 觸發判定、
# Demo + Human verdict、NOT_REVIEWED ≠ ACCEPTED、Operational Context 附著 S-id、
# 無第二 ID 鏈、純後端仍可跳過 Stage 3、舊模板仍可渲染、Stage 3 對帳存在性。
#
# 可選第一參數:指向隔離複本的 root(供 scripts/test-architecture-guards.sh 的
# mutation 回歸用;缺省 = 本 repo)。同 scripts/check-version-sync.sh 的慣例。
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
FILE_MODE=""
if [ -n "${1:-}" ]; then
  if [ -f "$1" ]; then
    # 單檔形狀檢查（discovery-gaps 對照稿）：對該 md 跑錯欄／主張牙，不掃模板。
    FILE_MODE=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
  else
    ROOT=$(cd "$1" && pwd) || exit 2
  fi
fi
python3 - "$ROOT" "$FILE_MODE" <<'PY'
import os
import re
import subprocess
import sys

root = sys.argv[1]
file_mode = sys.argv[2] if len(sys.argv) > 2 else ""
checks = 0
failures = []


def check(condition, label, detail=""):
    global checks
    checks += 1
    if not condition:
        failures.append(label + (f": {detail}" if detail else ""))


def check_skip(label, reason):
    """顯性跳過(不是恆真斷言):某條檢查在此 root 下條件不成立、無法真的驗
    (例如 renderer 不存在於隔離測試根目錄),但仍要計入 checks —— N-2 地板要求
    「兩種環境下檢查數一致」,若不計入,地板會把「合法跳過」誤判成「檢查被刪掉」。
    與 `check(True, …)` 的差別:那是把一條原本會判斷條件的斷言解除武裝、且不留痕;
    這裡印出「↷ 跳過」讓輸出上看得出這條沒有真的驗到什麼,且呼叫字面是
    `check_skip(` 不是 `check(`,天生不落在 check-design-contract.sh 的跨檔恆真
    掃描(`check\\(\\s*(True|1==1|not False)`)命中範圍內 —— 這是合法的顯性跳過,
    不是被掃描盯防的對象。"""
    global checks
    checks += 1
    print(f"  ↷ 跳過:{label}({reason})")


def read(rel):
    with open(os.path.join(root, rel), encoding="utf-8") as stream:
        return stream.read()


def section(source, heading, level="###"):
    pattern = re.compile(
        rf"^{re.escape(level)} {re.escape(heading)}.*?\n(.*?)(?=^#{{2,3}} |\Z)", re.M | re.S)
    match = pattern.search(source)
    return match.group(1) if match else ""


def table_rows(body):
    rows = [line for line in body.splitlines() if line.lstrip().startswith("|")]
    return max(0, len(rows) - 2)  # minus header + separator


def heading_body(source, heading):
    """`## heading` 本文，直到下一條 `## `。"""
    match = re.search(
        rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", source, re.M | re.S)
    return match.group(1) if match else None


def content_lines(body):
    if body is None:
        return []
    out = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--") or stripped.startswith("-->"):
            continue
        if stripped.startswith(">"):
            continue
        out.append(stripped)
    return out


def goals_wrong_column(text):
    """S-1.2：Goals 第一句「我要 dashboard」且 Requested solution 缺或空。

    不採 dashboard／API 黑名單（S-1.4）：領域詞出現在結果句或他處不構成錯欄。
    """
    goals = heading_body(text, "Goals")
    if goals is None:
        return False
    requested = heading_body(text, "Requested solution")
    first_lines = content_lines(goals)
    if not first_lines:
        return False
    first = first_lines[0].lstrip("-* ").strip()
    requested_empty = requested is None or not content_lines(requested)
    return bool(re.search(r"我要\s*dashboard", first, re.I) and requested_empty)


def prefix_symmetry_issues(text):
    """S-2.2：教師／指南兩邊前綴必須成對。缺一邊指出缺的那一邊。"""
    has_d = "發現｜" in text
    has_j = "裁決｜" in text
    if has_d and not has_j:
        return ["缺 裁決｜"]
    if has_j and not has_d:
        return ["缺 發現｜"]
    return []


def discover_question_has_recommend(text):
    """發現題附推薦 → 紅；裁決題附選項不算。"""
    for line in text.splitlines():
        if "發現｜" in line and ("推薦答案" in line or "建議選" in line or "附推薦" in line):
            return True
    return False


CLAIM_ENUMS = ("Observed", "Reported", "Inferred", "Assumption", "Conflict")


def high_impact_blocks(text):
    blocks = []
    for heading in ("Workarounds", "Exceptions", "Evidence"):
        body = heading_body(text, heading)
        if not body:
            continue
        current = None
        for line in body.splitlines():
            if re.match(r"^- ", line):
                if current:
                    blocks.append(current)
                current = {"heading": heading, "title": line, "fields": line + "\n"}
            elif current is not None:
                current["fields"] += line + "\n"
        if current:
            blocks.append(current)
    return blocks


def claim_issues(text):
    """S-3.*／S-8.4：高影響列來源 XOR 期限；點頭獨源紅；枚舉五值；ticket 解法不當事實。"""
    issues = []
    for block in high_impact_blocks(text):
        fields = block["fields"]
        status_m = re.search(r"狀態:\s*(\S+)", fields)
        source_m = re.search(r"來源(?:類型)?:\s*(.+)", fields)
        status = status_m.group(1).rstrip("。；,") if status_m else ""
        source = source_m.group(1).strip() if source_m else ""
        has_deadline = bool(re.search(r"期限", fields))
        if status and status not in CLAIM_ENUMS:
            issues.append(
                f"枚舉不在五值集合:{status}（Observed／Reported／Inferred／Assumption／Conflict）")
        if block["heading"] in ("Workarounds", "Exceptions"):
            if not status and not source and not has_deadline:
                issues.append("高影響列缺來源且缺期限（要可重開來源或 Assumption 期限）")
            if source and any(tok in source for tok in ("使用者點頭", "認可後清單", "點頭")):
                issues.append("點頭不是來源：點頭／認可不得當唯一來源")
            if ("使用者反映" in block["title"] or "使用者反映" in fields) and not source and not has_deadline:
                issues.append("高影響列缺來源且缺 Assumption 期限")
        if (re.search(r"ticket|SOP", fields, re.I) and "建議" in fields
                and status == "Observed"):
            issues.append("解法不當事實：ticket／SOP 建議應進 Requested solution，不得標 Observed")
    return issues


def discovery_shape_issues(text):
    """discovery-gaps 形狀牙（掛在本入口，不另開 check-discovery-gaps.sh）。"""
    issues = []
    if goals_wrong_column(text):
        issues.append("構想在錯欄：Goals 把通道構想當目標，Requested solution 缺或空")
    issues.extend(prefix_symmetry_issues(text))
    if discover_question_has_recommend(text):
        issues.append("發現題附推薦：發現｜問句禁附推薦")
    issues.extend(claim_issues(text))
    issues.extend(verdict_issues(text))
    return issues


def verdict_issues(text):
    """S-5.1／S-5.2：ENUM=ACCEPTED 時必須同行有 role= 與 scenario=。"""
    issues = []
    for line in text.splitlines():
        if "Human verdict:" not in line:
            continue
        if not re.search(r"\bACCEPTED\b", line):
            continue
        if "role=" in line and "scenario=" in line:
            continue
        issues.append("Human verdict 殘行：ACCEPTED 缺 role 或 scenario")
    return issues


# 單檔模式：只咬對照稿，exit ≠ 0 當構想在錯欄（S-1.2 觀測）。
if file_mode:
    subject = open(file_mode, encoding="utf-8").read()
    issues = discovery_shape_issues(subject)
    if issues:
        print(f"❌ discovery-gaps 形狀:{file_mode}")
        for issue in issues:
            print(f"  - {issue}")
        raise SystemExit(1)
    print(f"✅ discovery-gaps 形狀:{file_mode}")
    raise SystemExit(0)


t1 = read("_templates/1-discussion.md")
t3 = read("_templates/3-prototype.md")
t4 = read("_templates/4-spec.md")
e1 = read("example/contract-expiry-reminder/1-discussion.md")
e3 = read("example/contract-expiry-reminder/3-prototype.md")
e4 = read("example/contract-expiry-reminder/4-spec.md")

# ── 1. Real-world Context 欄位存在(模板 + 範例)──
for label, source in (("template 1-discussion", t1), ("example 1-discussion", e1)):
    for heading in ("## Real-world Context", "### Actors", "### Current Journey",
                    "### Workarounds", "### Exceptions", "### Evidence"):
        check(heading in source, f"{label} 含 {heading}")
    check("| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |" in source,
          f"{label} Actors 表頭六欄")
    check("| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |" in source,
          f"{label} Current Journey 表頭七欄")
for phrase in ("最近一次真的發生", "兩者都記", "不得把推測寫成事實", "去識別化"):
    check(phrase in t1, f"template 1-discussion 訪談規則含「{phrase}」")
check("不另發" in t1, "template 1-discussion 含 ID 規則(不另發第二鏈 ID)")
check(table_rows(section(e1, "Actors")) >= 3, "example Actors 至少 3 個 actor")
check(table_rows(section(e1, "Current Journey", level="###")) >= 4,
      "example Current Journey 至少 4 步",
      f"rows={table_rows(section(e1, 'Current Journey', level='###'))}")

# ── 2. Assumption 與 Evidence 可區分 ──
check("Assumption" in t1, "template 1-discussion 含 Assumption 標記規則")
check("[Assumption]" in e1, "example 1-discussion 有 [Assumption] 標記項")
check("訪談" in section(e1, "Evidence"), "example Evidence 節含訪談證據")

# ── 3. UI/workflow trigger 可判斷 Stage 3 ──
check("條件式必要" in t3, "template 3-prototype 含條件式必要語意")
for trigger in ("有新的前端流程", "改變使用者下一步", "涉及角色交接", "涉及人工核准",
                "涉及等待/退回/逾時", "涉及權限差異", "涉及系統外動作",
                "涉及多種可行互動設計", "操作流程不確定性"):
    check(trigger in t3, f"template 3-prototype 觸發條件含「{trigger}」")
check("Owner Call" in t3, "template 3-prototype 跳過須記 Owner Call")
check("不得自行替人決定" in t3, "template 3-prototype 禁 Agent 代決跳過")
check("## Stage 3 觸發判定" in e3, "example 3-prototype 有觸發判定節")
check("[x]" in e3, "example 3-prototype 觸發判定有命中標記")

# ── 4. Stage 3 Demo 有 User Verdict ──
check("## Demo Script" in t3, "template 3-prototype 有 Demo Script 節")
for field in ("使用者角色:", "真實目標:", "起始狀態:", "操作步驟:", "系統回應:",
              "系統外下一步:", "觀察問題:"):
    check(field in t3, f"template Demo Script 欄位「{field}」")
for probe in ("知道下一步", "不存在的權限", "等待狀態是否清楚", "撤回"):
    check(probe in t3, f"template Demo 確認問題含「{probe}」")
for form in ("HTML prototype", "Storybook", "CLI flow", "狀態流程模擬器"):
    check(form in t3, f"template Demo 形式選項含「{form}」")
for rule in ("不直接變成 production implementation", "假資料或去識別化",
             "清楚標示非正式產品程式碼", "實際操作"):
    check(rule in t3, f"template Demo 鐵則含「{rule}」")
for variant_rule in ("結構不同", "不同操作順序", "資訊階層", "決策點", "錯誤恢復"):
    check(variant_rule in t3, f"template variant 規則含「{variant_rule}」")
for state in ("等待狀態", "空狀態", "錯誤狀態", "權限不足", "資料過期", "中斷恢復",
              "系統外下一步"):
    check(state in t3, f"template variant 必含狀態「{state}」")
check("## User Demo Feedback" in t3, "template 3-prototype 有 User Demo Feedback 節")
for field in ("Demo date:", "Participants:", "Variant reviewed:", "Accepted interaction:",
              "Rejected interaction:", "Confusions observed:", "Missing real-world steps:",
              "Permission corrections:", "External handoffs:", "Required changes:",
              "Human verdict:"):
    check(field in t3, f"template User Demo Feedback 欄位「{field}」")
check("ACCEPTED | REVISE | NOT_REVIEWED" in t3, "template verdict 枚舉三值")
check(len(re.findall(r"^### Scenario ", e3, re.M)) >= 5,
      "example Demo Script 至少 5 個場景",
      f"found={len(re.findall(r'^### Scenario ', e3, re.M))}")
for state in ("等待法務", "等待主管", "已聯絡供應商", "資料過期", "空狀態", "錯誤狀態",
              "僅主管可標"):
    check(state in e3, f"example Demo 展示狀態「{state}」")
check("## User Demo Feedback" in e3, "example 3-prototype 有 User Demo Feedback")
check("示範" in e3, "example Human verdict 標注為示範值")

# ── 5. NOT_REVIEWED ≠ ACCEPTED ──
check("不得由 Agent 代答" in t3, "template:Human verdict 不得由 Agent 代答")
check("NOT_REVIEWED 不得被 Agent 當成 ACCEPTED" in t3, "template:NOT_REVIEWED ≠ ACCEPTED")
check("REVISE 必須" in t3, "template:REVISE 必須重新 Demo")
check("不得偷偷在" in t3, "template:互動未解決不得在 Stage 4 定案")
fm = re.match(r"\A---\n(.*?)\n---\n", e3, re.S)
status = ""
if fm:
    status_match = re.search(r"^status:\s*(\S+)", fm.group(1), re.M)
    status = status_match.group(1) if status_match else ""
verdicts = re.findall(r"Human verdict:\s*(ACCEPTED|REVISE|NOT_REVIEWED)\b", e3)
check(len(verdicts) >= 1, "example 3-prototype Human verdict 已填枚舉值")
if verdicts:
    check(not (status == "approved" and verdicts[-1] != "ACCEPTED"),
          "example:status=approved 時 verdict 必為 ACCEPTED(NOT_REVIEWED/REVISE 不算過)",
          f"status={status} verdict={verdicts[-1]}")

# ── 6. Operational Context 附著於 S-id ──
check("Operational Context" in t4, "template 4-spec 有 Operational Context")
for field in ("Actor:", "Goal:", "Situation:", "Known information:", "Missing information:",
              "Human decision:", "Authority:", "External dependency:",
              "Out-of-system action:", "Waiting/timeout behavior:", "Recovery:",
              "Audit/handoff requirement:", "Observation:"):
    check(field in t4, f"template Operational Context 欄位「{field}」")
check("外部事情沒完成時" in t4, "template 4-spec 含操作五問")
current_heading = ""
for line in e4.splitlines():
    if re.match(r"^#{2,5} ", line):
        current_heading = line
    # 只驗附著形式(- Operational Context: / ():散文提及(如確認紀錄)不算附著
    # G3(2026-08-17):字元集曾是兩個半形冒號 + 半形括號(本想寫全半形都收)。
    if re.match(r"^\s*-\s*Operational Context\s*[:：(（]", line):
        check(re.match(r"^#### S-\d+", current_heading) is not None,
              "example 4-spec Operational Context 附著於 S-id",
              f"under {current_heading!r}")
s_blocks = re.split(r"(?=^#### S-)", e4, flags=re.M)
filled = [b for b in s_blocks if b.startswith("#### S-")
          and "Operational Context" in b and re.search(r"Actor:\s*\S", b)]
check(len(filled) >= 3, "example 4-spec 至少 3 個 S 有已填 Operational Context",
      f"filled={len(filled)}")

# ── 7. 不建立第二 ID 鏈 ──
for rel, source in (("_templates/1-discussion.md", t1), ("_templates/3-prototype.md", t3),
                    ("_templates/4-spec.md", t4),
                    ("example/contract-expiry-reminder/1-discussion.md", e1),
                    ("example/contract-expiry-reminder/3-prototype.md", e3),
                    ("example/contract-expiry-reminder/4-spec.md", e4)):
    check(re.search(r"\b(?:J|JNY|ACT|IX|AID|JID)-\d", source) is None,
          f"{rel} 無第二鏈 ID(J-/JNY-/ACT-/IX-/AID-/JID-)")

# ── 8. 舊純後端 Feature 仍可跳過 Stage 3 ──
check(re.search(r"^# 3\..*選配", t3, re.M) is not None,
      "template 3-prototype H1 保留選配")
check("純後端" in t3, "template 3-prototype 明示純後端可照舊跳過")
check("兩檔皆不建" in t3, "template 3-prototype 保留命中後跳過路徑(兩檔皆不建)")
check("全未勾" in t3, "template 3-prototype 零命中仍落檔全未勾清單")

# ── 9. 舊模板仍可渲染 ──
# renderer 不存在時(隔離測試根目錄,如 test-architecture-guards.sh 的 seed()複本)
# 明著跳過,不得靜默略過(同檔已知教訓:靜默 skip = 假綠)。
renderer = os.path.join(root, "scripts", "render-methodology-corrections.sh")
if os.path.isfile(renderer):
    # 顯式帶 bash(派工單 §2.2):Windows 沒有 shebang 機制,直接 exec .sh 會噴
    # OSError WinError 193 而整支檢查崩掉。
    result = subprocess.run(["bash", renderer, "--check"], cwd=root,
                            capture_output=True, text=True)
    check(result.returncode == 0, "舊模板/衍生檔仍可渲染(renderer --check)",
          (result.stdout + result.stderr).strip())
else:
    print(f"⚠️  renderer 不存在於此 root({renderer}),略過『舊模板仍可渲染』內容驗證 "
          "—— 僅限隔離測試根目錄,正式 repo 執行不會走到這條分支", file=sys.stderr)
    # 仍要算進 checks(N-2 地板要求兩種環境下的檢查數一致,不然地板本身就會把
    # 「renderer 不存在的隔離測試根目錄」誤判成「檢查被刪掉」),但用顯性的
    # check_skip 而不是 check(True, …)——後者是恆真斷言,已被 check-design-contract.sh
    # 的跨檔掃描列為缺陷模式(2026-08-17 家規:規則推廣跨檔,不是就地豁免)。
    check_skip("舊模板/衍生檔仍可渲染(renderer --check)",
                "隔離測試根目錄,renderer 不存在,略過內容驗證")

# ── 10. Stage 3 對帳存在性(devflow-4cap-remediation-2026-08.md §7 第 1 點,2026-08-15)──
# 只驗「Out of Scope 節有 Stage 3 對帳段、且每場都點名」的存在性/結構,不驗語意正確性
# (驗內容正確性 = 過度設計,同 P3/E11 heading-only 慣例、防守清單第 6 條同邏輯)。
# 釘的是結構(marker 片語 + 逐條點名 3-prototype 場景引用),不是會漂移的場景名字面。
oos_e4 = section(e4, "Out of Scope", level="##")
check(bool(oos_e4.strip()), "example 4-spec 有 Out of Scope 節內容")
marker_idx = oos_e4.find("Stage 3 對帳")
check(marker_idx != -1, "example Out of Scope 節含「Stage 3 對帳」段")
after_marker = oos_e4[marker_idx:] if marker_idx != -1 else ""
reconcile_bullets = [ln for ln in after_marker.splitlines() if ln.lstrip().startswith("- ")]
check(bool(reconcile_bullets),
      "Stage 3 對帳段至少有一條已下落的場景(空段落 = 對帳形同虛設)",
      f"bullets={len(reconcile_bullets)}")
named_bullets = [ln for ln in reconcile_bullets
                 if re.search(r"3-prototype「Scenario[^」]*」", ln)]
check(bool(reconcile_bullets) and len(named_bullets) == len(reconcile_bullets),
      "Stage 3 對帳段每一條都逐場點名(引用 3-prototype「Scenario …」)",
      f"未點名 {len(reconcile_bullets) - len(named_bullets)}/{len(reconcile_bullets)} 條")

# ── 11. discovery-gaps：Goals 錯欄牙（S-1.2／S-1.4；fixture 自測）──
# 隔離 root（test-architecture-guards seed）沒有 scripts/fixtures/discovery-gaps/
# 時顯性跳過，兩環境檢查數一致。不另開 check-discovery-gaps.sh。
GAPS = os.path.join(root, "scripts", "fixtures", "discovery-gaps")
WRONG_COL = os.path.join(GAPS, "goals-dashboard-in-wrong-column.md")
OK_COL = os.path.join(GAPS, "goals-outcome-with-requested-dashboard.md")
if os.path.isfile(WRONG_COL):
    wrong_text = open(WRONG_COL, encoding="utf-8").read()
    wrong_issues = discovery_shape_issues(wrong_text)
    check(any("構想在錯欄" in item or "Requested solution" in item for item in wrong_issues),
          "負向 fixture goals-dashboard-in-wrong-column 必須被指出構想在錯欄",
          f"issues={wrong_issues}")
else:
    check_skip("負向 fixture goals-dashboard-in-wrong-column 必須被指出構想在錯欄",
               "隔離測試根目錄無 discovery-gaps fixture")
if os.path.isfile(OK_COL):
    ok_text = open(OK_COL, encoding="utf-8").read()
    ok_issues = discovery_shape_issues(ok_text)
    check(not any("構想在錯欄" in item for item in ok_issues),
          "正向 fixture goals-outcome-with-requested-dashboard 不因 dashboard/API 誤殺",
          f"issues={ok_issues}")
else:
    check_skip("正向 fixture goals-outcome-with-requested-dashboard 不因 dashboard/API 誤殺",
               "隔離測試根目錄無 discovery-gaps fixture")

# ── 12. 教師分欄地板（S-1.1／S-1.3）：Goals 只寫結果，構想進 Requested solution ──
check("## Requested solution" in t1, "template 1-discussion 含 ## Requested solution")
check("## Requested solution" in e1, "example 1-discussion 含 ## Requested solution")
t1_goals = heading_body(t1, "Goals") or ""
t1_ac = heading_body(t1, "驗收雛形") or ""
check("畫面路徑 | API 端點" not in t1_goals and "畫面路徑 | API 端點" not in t1_ac,
      "template Goals／驗收雛形不再預填畫面路徑 | API 端點")
e1_goals = heading_body(e1, "Goals") or ""
check(all(p not in e1_goals for p in ("就能看到", "點擊可直達", "一眼可見")),
      "example Goals 不再把登入／點擊／一眼可見寫成目標本身")

# ── 13. 發現｜／裁決｜前綴對稱（S-2.1／S-2.2／S-2.3）──
n3_rel = "skills/dev-talk/nodes/N3-probe.md"
n3_path = os.path.join(root, n3_rel)
if os.path.isfile(n3_path):
    n3 = read(n3_rel)
    n3_pref = prefix_symmetry_issues(n3)
    check(not n3_pref, "N3-probe 發現｜與裁決｜成對", f"issues={n3_pref}")
    check("禁附推薦" in n3, "N3-probe 發現題路徑含禁附推薦")
else:
    check_skip("N3-probe 發現｜與裁決｜成對", "隔離根無 N3-probe")
    check_skip("N3-probe 發現題路徑含禁附推薦", "隔離根無 N3-probe")
probe_ok = os.path.join(GAPS, "probe-decision-with-options.md")
if os.path.isfile(probe_ok):
    probe_text = open(probe_ok, encoding="utf-8").read()
    probe_issues = discovery_shape_issues(probe_text)
    check(not probe_issues,
          "裁決題附選項不得當發現題違規（probe-decision-with-options）",
          f"issues={probe_issues}")
else:
    check_skip("裁決題附選項不得當發現題違規（probe-decision-with-options）",
               "隔離測試根目錄無 discovery-gaps fixture")

# ── 14. 高影響主張牙（S-3.1–S-3.4／S-8.4）──
def _gaps_must_flag(name, needles, label):
    path = os.path.join(GAPS, name)
    if not os.path.isfile(path):
        check_skip(label, "隔離測試根目錄無 discovery-gaps fixture")
        return
    flagged = discovery_shape_issues(open(path, encoding="utf-8").read())
    blob = " ".join(flagged)
    check(any(n in blob for n in needles), label, f"issues={flagged}")


_gaps_must_flag("nod-as-only-source.md", ("點頭", "不是來源"),
                "點頭獨源 fixture 必須紅")
_gaps_must_flag("enum-unknown.md", ("枚舉", "Observed", "Reported"),
                "枚舉 Unknown fixture 必須紅")
_gaps_must_flag("ticket-solution-as-fact.md", ("解法", "Requested solution", "不當事實"),
                "ticket 解法當 Observed 必須紅")
_gaps_must_flag("high-impact-missing-source.md", ("來源", "Assumption", "期限"),
                "高影響列缺來源且缺期限必須紅")


def _gaps_must_pass(name, label):
    path = os.path.join(GAPS, name)
    if not os.path.isfile(path):
        check_skip(label, "隔離測試根目錄無 discovery-gaps fixture")
        return
    flagged = discovery_shape_issues(open(path, encoding="utf-8").read())
    check(not flagged, label, f"issues={flagged}")


_gaps_must_pass("high-impact-with-source.md", "有可重開來源必須綠")
_gaps_must_pass("high-impact-with-assumption.md", "Assumption 加期限必須綠")
_gaps_must_pass("non-high-impact-context.md", "非高影響 Context 不貼枚舉不得紅")

# ── 15. Assumption 四欄地板（S-4.4）──
ASSUMPTION_COLS = ("若為假影響什麼", "影響級", "怎麼驗", "何時／由誰驗")
check(all(col in t1 for col in ASSUMPTION_COLS),
      "template 1-discussion 含 Assumption 四欄字面")
check(all(col in e1 for col in ASSUMPTION_COLS),
      "example 1-discussion 含 Assumption 四欄字面")

# ── 16. Human verdict 一行（S-5.1／S-5.2／S-5.3）──
check("role=" in t3 and "scenario=" in t3, "template 3-prototype verdict 含 role=／scenario=")
check("role=" in e3 and "scenario=" in e3, "example 3-prototype verdict 含 role=／scenario=")
check("本包必填全表" not in t3 and "Actor Coverage" not in t3,
      "template 3-prototype 不得要求 Actor Coverage 全表")
_gaps_must_flag("verdict-accepted-only.md", ("role", "scenario"),
                "殘行 ACCEPTED 無 role／scenario 必須紅")
_gaps_must_pass("verdict-complete.md", "完整 verdict 一行必須綠")

# ── 檢查數地板(N-2,2026-08-15)──────────────────────────────────────────────
# ⚠️ 這個數字必須**等於當下的實際檢查數**,不是「大概抓個下限」——地板留餘裕=沒有
# 牙齒(同 repo 慣例:scripts/check-stage67-enforcement.sh:232、
# scripts/test-architecture-guards.sh 的 EXPECTED_TOTAL)。
# 起因:刪掉整段(例如第 5 節「NOT_REVIEWED ≠ ACCEPTED」)之前,checks 只是印出來的
# 數字,不是斷言——舊版刪光整節仍印「✅ 全過」。新增/刪除 check() 呼叫時,
# 把這個數字一起往上/往下調。
MIN_CHECKS = 161
if checks < MIN_CHECKS:
    failures.append(f"⛔ 實際只跑了 {checks} 項檢查(地板 {MIN_CHECKS})—— "
                     f"檢查本身被刪掉或迴圈跑了零圈,這比條款失效更嚴重")

if failures:
    print(f"❌ real-world interaction checks: {checks - len(failures)}/{checks} passed"
          f"(地板 {MIN_CHECKS})")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)
print(f"✅ real-world interaction checks: {checks}/{checks} passed(地板 {MIN_CHECKS})")
PY
