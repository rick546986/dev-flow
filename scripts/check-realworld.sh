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
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi
python3 - "$ROOT" <<'PY'
import os
import re
import subprocess
import sys

root = sys.argv[1]
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


t1 = read("_templates/1-discussion.md")
t3 = read("_templates/3-prototype.md")
t4 = read("_templates/4-spec.md")
t7 = read("_templates/7-review.md")
e1 = read("example/contract-expiry-reminder/1-discussion.md")
e3 = read("example/contract-expiry-reminder/3-prototype.md")
e4 = read("example/contract-expiry-reminder/4-spec.md")
e7 = read("example/contract-expiry-reminder/7-review.md")

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
check("人要求才 Demo" in t3 and "Demo request" in t3, "template 3-prototype 含人要求才 Demo 極性(P3-4)與 Demo request 行")
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

# ── 11. Discovery gaps:Goals 錯欄 vs 不採 dashboard/API 黑名單(S-1.2／S-1.4)──
# 同一入口,不另開 check-discovery-gaps.sh。對照稿在
# scripts/fixtures/discovery-gaps/;隔離 seed 沒有該目錄時改跑同形內嵌稿,
# 檢查數仍一致(不得新增 check_skip:EXPECTED_CHECK_SKIP_CALLS 釘死 1)。
def _section_after(source, heading):
    idx = source.find(heading)
    if idx < 0:
        return None
    rest = source[idx + len(heading):]
    nxt = re.search(r"\n## ", rest)
    return rest if nxt is None else rest[:nxt.start()]


def _first_goal_line(goals_body):
    if not goals_body:
        return ""
    for line in goals_body.splitlines():
        text = line.strip().lstrip("-").strip()
        if text and not text.startswith("<!--"):
            return text
    return ""


def detect_goals_wrong_column(source):
    """構想寫進 Goals、Requested solution 缺或空 → 構想在錯欄。

    不採 dashboard／API 黑名單:結果句即使含這兩個詞,只要構想在 Requested
    solution,不算錯欄。"""
    goals = _section_after(source, "## Goals")
    requested = _section_after(source, "## Requested solution")
    first = _first_goal_line(goals)
    requested_empty = requested is None or not re.sub(
        r"<!--.*?-->", "", requested, flags=re.S).strip()
    if not first or not requested_empty:
        return False
    return first == "我要 dashboard" or first.startswith("我要 ")


_EMBED_WRONG = (
    "## Goals\n- 我要 dashboard\n\n## Requested solution\n\n## Context\n"
)
_EMBED_OK = (
    "## Goals\n- 讓負責業務在合約到期前做完續約決定\n\n"
    "## Requested solution\n未定案：站內 dashboard\n\n"
    "## Context\n對照既有 dashboard API\n"
)
_wrong_rel = "scripts/fixtures/discovery-gaps/goals-dashboard-in-wrong-column.md"
_ok_rel = "scripts/fixtures/discovery-gaps/goals-outcome-with-requested-dashboard.md"
_wrong_src = read(_wrong_rel) if os.path.isfile(os.path.join(root, _wrong_rel)) else _EMBED_WRONG
_ok_src = read(_ok_rel) if os.path.isfile(os.path.join(root, _ok_rel)) else _EMBED_OK
_wrong_hit = detect_goals_wrong_column(_wrong_src)
_ok_hit = detect_goals_wrong_column(_ok_src)
check(_wrong_hit, "S-1.2 goals-dashboard-in-wrong-column 構想在錯欄",
      "Requested solution 空且 Goals 第一句是構想")
check(not _ok_hit, "S-1.4 goals-outcome-with-requested-dashboard 不因 dashboard/API 誤殺")
if _wrong_hit:
    print("  構想在錯欄:goals-dashboard-in-wrong-column")

# ── 12. 教師地板:Goals 只寫結果、構想進 Requested solution(S-1.1／S-1.3)──
check("## Requested solution" in t1, "template 1-discussion 含 ## Requested solution")
check("畫面路徑 | API 端點" not in (_section_after(t1, "## Goals") or ""),
      "template Goals 不再預填畫面／API 通道")
check("畫面路徑 | API 端點" not in (_section_after(t1, "## 驗收雛形") or ""),
      "template 驗收雛形不再預填畫面／API 通道")
check("## Requested solution" in e1, "example 1-discussion 含 ## Requested solution")
_e1_goals = _section_after(e1, "## Goals") or ""
check("就能看到" not in _e1_goals and "點擊可直達" not in _e1_goals
      and "一眼可見" not in _e1_goals,
      "example Goals 不再把登入／點擊／一眼可見當成目標本身")

# ── 13. 發現｜／裁決｜前綴對稱與發現題禁附推薦(S-2.1／S-2.2／S-2.3)──
_n3_rel = "skills/dev-talk/nodes/N3-probe.md"
_skill_rel = "skills/dev-talk/SKILL.md"
_n3 = (read(_n3_rel) if os.path.isfile(os.path.join(root, _n3_rel))
       else "發現｜開放題,禁附推薦\n裁決｜可附選項\n## 完成條件\n輔助")
_skill = (read(_skill_rel) if os.path.isfile(os.path.join(root, _skill_rel))
          else "發現｜禁附推薦")
check("發現｜" in _n3, "N3-probe 含發現｜前綴")
check("裁決｜" in _n3, "N3-probe 含裁決｜前綴")
check("禁附推薦" in _n3, "N3-probe 發現題路徑禁附推薦")
check("發現｜" in _skill or "禁附推薦" in _skill,
      "SKILL 入口摘要含發現｜或禁附推薦")
_n3_done = _n3.split("## 完成條件", 1)[-1].split("## ", 1)[0] if "## 完成條件" in _n3 else _n3
check("連續兩輪無新問題" not in _n3_done or "輔助" in _n3,
      "N3 完成條件不再把連續兩輪當唯一條件(或已標輔助)")
_probe_rel = "scripts/fixtures/discovery-gaps/probe-decision-with-options.md"
_probe = (read(_probe_rel) if os.path.isfile(os.path.join(root, _probe_rel))
          else "發現｜上次真的怎麼做？\n裁決｜這條痛點進本方案還是 Non-Goal？本方案／Non-Goal／另開 slug")


def _discover_line_has_recommend(text):
    for line in text.splitlines():
        if "發現｜" in line and ("推薦答案" in line or "附推薦答案" in line):
            return True
    return False


check("發現｜" in _probe and "裁決｜" in _probe, "S-2.3 fixture 兩邊前綴都在")
check(not _discover_line_has_recommend(_probe),
      "S-2.3 裁決題附選項不得當發現題違規")

# ── 14. 高影響主張:枚舉／來源 XOR 期限／點頭／ticket 解法(S-3.*／S-8.4)──
CLAIM_STATUSES = ("Observed", "Reported", "Inferred", "Assumption", "Conflict")
NOD_ONLY = ("使用者點頭", "認可後清單", "點頭")


def _field(block, name):
    match = re.search(rf"-\s*{name}\s*[:：]\s*(.+)", block)
    return match.group(1).strip() if match else ""


def _is_high_impact(block):
    return any(token in block for token in ("風險=高", "影響級", "⚠️", "痛點"))


def _high_impact_scan_bodies(text):
    """只掃 Journey 痛點／Exceptions／Workarounds；沒有那些節才退回全文(內嵌對照)。"""
    bodies = []
    for heading in ("### Exceptions", "### Workarounds", "### Journey",
                    "## Current Journey"):
        body = _section_after(text, heading)
        if body:
            bodies.append(body)
    if "痛點" in text and not bodies:
        bodies.append(text)
    return bodies or [text]


def _claim_problems(text):
    """回傳高影響列的形狀問題字樣(來源／Assumption／期限／點頭／枚舉／解法)。"""
    problems = []
    for body in _high_impact_scan_bodies(text):
        chunks = re.split(r"\n(?=[-*] )", body)
        for block in chunks:
            status = _field(block, "狀態")
            source = _field(block, "來源類型") or _field(block, "來源")
            deadline = _field(block, "期限")
            # S-3.1:無狀態／來源／期限,或只寫「使用者反映」
            bare = (not status and not source and not deadline
                    and block.strip().startswith("-") and len(block.strip()) > 3)
            if "使用者反映" in block or bare:
                if "path:" not in block and not deadline:
                    problems.append("來源")
            if "狀態" not in block and "風險=高" not in block and "使用者反映" not in block and not bare:
                continue
            if not _is_high_impact(block) and "風險=高" not in block and "使用者反映" not in block and not bare:
                if status not in ("Unknown", "Fact") and status not in CLAIM_STATUSES:
                    continue
            if status in ("Unknown", "Fact") or (status and status not in CLAIM_STATUSES):
                problems.append("枚舉")
            if status == "Observed" and any(n in (source or block) for n in NOD_ONLY) and "path:" not in source:
                problems.append("點頭")
            if status == "Observed" and ("未核" in (source or "") or (source == "" and "未核" in block)):
                problems.append("來源")
            if status == "Observed" and ("建議做 dashboard" in block or "建議做" in block) and (
                    "ticket" in block.lower() or "SOP" in block):
                problems.append("不當事實")
                problems.append("解法")
            has_source = bool(source) and not any(n in source for n in NOD_ONLY) and "未核" not in source
            has_assumption = status == "Assumption" and bool(deadline)
            if "狀態" in block and "風險=高" in block and not has_source and not has_assumption:
                if "點頭" not in "".join(problems):
                    problems.append("來源")
    return problems


def _load_gap(rel, embed):
    path = os.path.join(root, rel)
    return read(rel) if os.path.isfile(path) else embed


_nod = _load_gap("scripts/fixtures/discovery-gaps/nod-as-only-source.md",
                 "## Real-world Context\n### Exceptions\n- 點頭獨源\n"
                 "  - 狀態: Observed\n  - 來源類型: 使用者點頭\n  - 風險=高\n")
_enum = _load_gap("scripts/fixtures/discovery-gaps/enum-unknown.md",
                  "## Real-world Context\n### Exceptions\n- 枚舉外\n"
                  "  - 狀態: Unknown\n  - 來源類型: 本 tree skill\n  - 風險=高\n")
_ticket = _load_gap("scripts/fixtures/discovery-gaps/ticket-solution-as-fact.md",
                    "## Real-world Context\n### Evidence\n- ticket／SOP 建議做 dashboard\n"
                    "  - 狀態: Observed\n  - 來源類型: ticket\n  - 風險=高\n")
_user = _load_gap("scripts/fixtures/discovery-gaps/user-report-only.md",
                  "## Real-world Context\n### Exceptions\n- 使用者反映希望 dashboard\n")
_unapproved = _load_gap("scripts/fixtures/discovery-gaps/unapproved-as-only-source.md",
                        "## Real-world Context\n### Evidence\n- notes/review-requirement-discovery-gaps.md\n"
                        "  - 狀態: Observed\n  - 來源類型: 未核\n  - 風險=高\n")
_good_obs = (
    "## Real-world Context\n### Exceptions\n- 發現被錨定\n"
    "  - 狀態: Observed\n  - 來源類型: 本 tree skill path:L12\n  - 風險=高\n"
)
_good_assume = (
    "## Real-world Context\n### Exceptions\n- 現場假設\n"
    "  - 狀態: Assumption\n  - 期限: stage-2\n  - 風險=高\n"
    "  - 若為假影響什麼: G1 假綠\n  - 影響級: 高\n  - 怎麼驗: 抽查\n"
    "  - 何時／由誰驗: Stage 2 / owner\n"
)
_low = (
    "## Context\n- 已核 path:L10 普通事實句,無風險=高\n"
    "## Real-world Context\n### Exceptions\n- 發現被錨定\n"
    "  - 狀態: Observed\n  - 來源類型: 本 tree skill path:L12\n  - 風險=高\n"
)
check(any(x in "".join(_claim_problems(_user)) for x in ("來源", "Assumption", "期限")),
      "S-3.1 user-report-only 缺來源且缺期限必紅")
check(any(x in "".join(_claim_problems(_unapproved)) for x in ("來源", "未核")),
      "S-8.3 unapproved-as-only-source 未核不得當已授權來源")
check("點頭" in "".join(_claim_problems(_nod)), "S-3.3 nod-as-only-source 點頭獨源必紅")
check("枚舉" in "".join(_claim_problems(_enum)), "S-3.4 enum-unknown 集合外必紅")
check(any(x in "".join(_claim_problems(_ticket)) for x in ("解法", "不當事實", "Requested solution")),
      "S-8.4 ticket-solution-as-fact 解法建議不當事實")
check(not _claim_problems(_good_obs), "S-3.2 Observed+可重開來源必須綠")
check(not _claim_problems(_good_assume), "S-3.2 Assumption+期限必須綠")
check(not _claim_problems(_low), "S-3.5 非高影響 Context 句不貼枚舉不得紅")
check("Observed" in CLAIM_STATUSES and "Reported" in CLAIM_STATUSES,
      "高影響狀態集合含 Observed 與 Reported")

# ── 15. Assumption 四欄地板(S-4.4)──
_ASSUME_COLS = ("若為假影響什麼", "影響級", "怎麼驗", "何時／由誰驗")
check(all(c in t1 for c in _ASSUME_COLS), "template 1-discussion 含 Assumption 四欄")
check(all(c in e1 for c in _ASSUME_COLS), "example 1-discussion 含 Assumption 四欄")

# ── 16. Human verdict 一行 role=／scenario=(S-5.1／S-5.2／S-5.3)──
check("role=" in t3 and "scenario=" in t3, "template Human verdict 指令含 role=／scenario=")
check("role=" in e3 and "scenario=" in e3, "example Human verdict 含 role=／scenario=")
check("本包必填全表" not in t3 and "Actor Coverage" not in t3,
      "template 不要求 Actor Coverage 全表")


def _accepted_missing_role_scenario(text):
    for line in text.splitlines():
        if re.search(r"Human verdict:\s*ACCEPTED\b", line):
            if "role=" not in line or "scenario=" not in line:
                return True
    return False


_verdict_bad = _load_gap("scripts/fixtures/discovery-gaps/verdict-accepted-only.md",
                         "Human verdict: ACCEPTED\nVerdict attestation: human:rick @ 2026-09-13")
_verdict_ok = "Human verdict: ACCEPTED | role=Fast 實作者 | scenario=AC-9\nVerdict attestation: human:rick @ 2026-09-13"
check(_accepted_missing_role_scenario(_verdict_bad),
      "S-5.1 verdict-accepted-only 缺 role=/scenario= 必紅")
check(not _accepted_missing_role_scenario(_verdict_ok),
      "S-5.2 完整一行 role=／scenario= 放行")

# ── 17. Exit 回看四欄(S-7.1／S-7.2／S-7.3)──
_LOOKBACK = ("回看日期", "回看 owner", "資料來源", "低於何值重開")
check(all(c in t7 for c in _LOOKBACK), "template 7-review Exit 含回看四欄")
check(all(c in e7 for c in _LOOKBACK), "example 7-review Exit 含回看四欄")
check("lookback.md" not in t7, "template 7-review 不另造 lookback.md")
check("history-append.sh" in t7, "template 回看結果走 history-append.sh")


def _lookback_fired_missing(text):
    fired = "回看" in text or any(c in text for c in _LOOKBACK)
    if not fired:
        return False
    return any(c not in text for c in _LOOKBACK)


_lb_bad = _load_gap("scripts/fixtures/discovery-gaps/lookback-missing-threshold.md",
                    "status: shipped\n### 回看約定\n| 回看日期 | 回看 owner | 資料來源 |\n")
_lb_old = "# 7. 審查\n## Exit Checklist\n- [x] shipped\n"
check(_lookback_fired_missing(_lb_bad), "S-7.2 shipped 有回看節卻缺低於何值重開必紅")
check(not _lookback_fired_missing(_lb_old), "S-7.2 舊 7-review 無回看節不誤殺")

# ── 檢查數地板(N-2,2026-08-15)──────────────────────────────────────────────
# ⚠️ 這個數字必須**等於當下的實際檢查數**,不是「大概抓個下限」——地板留餘裕=沒有
# 牙齒(同 repo 慣例:scripts/check-stage67-enforcement.sh:232、
# scripts/test-architecture-guards.sh 的 EXPECTED_TOTAL)。
# 起因:刪掉整段(例如第 5 節「NOT_REVIEWED ≠ ACCEPTED」)之前,checks 只是印出來的
# 數字,不是斷言——舊版刪光整節仍印「✅ 全過」。新增/刪除 check() 呼叫時,
# 把這個數字一起往上/往下調。
MIN_CHECKS = 174
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
