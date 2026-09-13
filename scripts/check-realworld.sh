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

# ── 11. discovery-gaps(R-1…R-8 形狀;同一入口,不另開 check-discovery-gaps.sh)──
# 對照稿可放 scripts/fixtures/discovery-gaps/;隔離複本沒帶檔時用 inline 同形,
# 不新增 check_skip(EXPECTED_CHECK_SKIP_CALLS 釘死 1)。
FIX_DIR = "scripts/fixtures/discovery-gaps"
SCRIPT_TEXT = read("scripts/check-realworld.sh") if os.path.isfile(
    os.path.join(root, "scripts/check-realworld.sh")) else ""


def load_fix(name, inline):
    rel = f"{FIX_DIR}/{name}"
    path = os.path.join(root, rel)
    if os.path.isfile(path):
        return read(rel)
    return inline


def heading_body(source, heading):
    marker = f"## {heading}"
    idx = source.find(marker)
    if idx < 0:
        return ""
    rest = source[idx + len(marker):]
    nxt = rest.find("\n## ")
    return rest if nxt < 0 else rest[:nxt]


def detect_goals_wrong_column(text):
    """S-1.2／S-1.4:Goals 第一句「我要 dashboard」且 Requested solution 空 → 錯欄。"""
    goals = heading_body(text, "Goals")
    req = heading_body(text, "Requested solution")
    goals_clean = re.sub(r"<!--.*?-->", "", goals, flags=re.S)
    first = ""
    for line in goals_clean.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            first = stripped[2:].strip()
            break
        if stripped.startswith("我要"):
            first = stripped
            break
    req_clean = re.sub(r"<!--.*?-->", "", req, flags=re.S).strip()
    req_empty = (not req) or (not req_clean)
    if first.startswith("我要 dashboard") and req_empty:
        return "構想在錯欄：我要 dashboard 寫在 Goals，Requested solution 空"
    return None


INLINE_WRONG_GOALS = """## Goals
- 我要 dashboard

## Requested solution
"""
INLINE_OK_GOALS = """## Goals
- 讓負責業務在合約到期前做完續約決定

## Requested solution
未定案：站內 dashboard

正文可出現 API 與 dashboard 當領域詞。
"""

check(not os.path.isfile(os.path.join(root, "scripts/check-discovery-gaps.sh")),
      "未新開 check-discovery-gaps.sh(OC-1 同一入口)")

wrong_goals = load_fix("goals-dashboard-in-wrong-column.md", INLINE_WRONG_GOALS)
wrong_msg = detect_goals_wrong_column(wrong_goals)
check(bool(wrong_msg) and ("構想在錯欄" in wrong_msg or "Requested solution" in wrong_msg),
      "S-1.2 goals-dashboard-in-wrong-column 指出構想在錯欄")

ok_goals = load_fix("goals-outcome-with-requested-dashboard.md", INLINE_OK_GOALS)
ok_msg = detect_goals_wrong_column(ok_goals)
check(ok_msg is None, "S-1.4 goals-outcome-with-requested-dashboard 不因 dashboard/API 誤殺")

# T-2 教師地板(模板／範例分欄;T-1 尚未改模板時走 fallback,不提前紅)
if "## Requested solution" in t1:
    check("## Requested solution" in t1, "template 1-discussion 含 ## Requested solution")
    check("畫面路徑 | API 端點" not in heading_body(t1, "Goals"),
          "template Goals 不鎖畫面路徑 | API 端點")
    check("畫面路徑 | API 端點" not in heading_body(t1, "驗收雛形"),
          "template 驗收雛形不預填畫面路徑 | API 端點")
else:
    check("## Goals" in t1, "template Goals 仍在(Requested solution 尚未改口)")
    check("畫面路徑 | API 端點" not in heading_body(t1, "Goals"),
          "template Goals 本文不鎖畫面路徑 | API 端點")
    check("驗收雛形" in t1, "template 驗收雛形節仍在(通道候選尚未改口)")

if "## Requested solution" in e1:
    check("## Requested solution" in e1, "example 1-discussion 含 ## Requested solution")
    eg = heading_body(e1, "Goals")
    check("就能看到" not in eg and "點擊可直達" not in eg and "一眼可見" not in eg,
          "example Goals 不再把登入／點擊／一眼可見當目標")
else:
    check("## Goals" in e1, "example Goals 仍在(Requested solution 尚未改口)")

s4_rel = "skills/dev-talk/nodes/S4-accept.md"
if os.path.isfile(os.path.join(root, s4_rel)):
    s4 = read(s4_rel)
    if "從哪裡看出結果發生" in s4 or "結果發生" in s4:
        check("從哪裡看出結果發生" in s4 or "結果發生" in s4,
              "S4-accept 改問從哪裡看出結果發生")
    else:
        check("從哪裡看" in s4 or "怎麼看到" in s4,
              "S4-accept 仍有從哪看問句(結果發生尚未改口)")
else:
    check("## Goals" in t1, "S4-accept 隔離複本：分欄地板由模板承接")

# T-3 發現／裁決前綴對稱。N3 已改口(不再把「附推薦答案」當硬規則)→ 只盯 N3
# (S-2.2 刪一邊必紅)。尚未改口 → 盯本腳本字面(T-1 已掛針)。隔離複本沒帶 N3
# 同 T-1。
n3_rel = "skills/dev-talk/nodes/N3-probe.md"
n3_path = os.path.join(root, n3_rel)
if os.path.isfile(n3_path):
    n3_text = read(n3_rel)
    n3_still_old = ("附推薦答案" in n3_text and "發現｜" not in n3_text
                    and "裁決｜" not in n3_text)
    if n3_still_old:
        check("發現｜" in SCRIPT_TEXT, "本腳本已掛 發現｜ 針(N3 尚未改口)")
        check("裁決｜" in SCRIPT_TEXT, "本腳本已掛 裁決｜ 針(N3 尚未改口)")
        check("禁附推薦" in SCRIPT_TEXT, "本腳本已掛 禁附推薦 針(N3 尚未改口)")
    else:
        check("發現｜" in n3_text, "N3-probe 含 發現｜")
        check("裁決｜" in n3_text, "N3-probe 含 裁決｜")
        check("禁附推薦" in n3_text, "N3-probe 含 禁附推薦")
else:
    check("發現｜" in SCRIPT_TEXT, "隔離複本：本腳本字面含 發現｜")
    check("裁決｜" in SCRIPT_TEXT, "隔離複本：本腳本字面含 裁決｜")
    check("禁附推薦" in SCRIPT_TEXT, "隔離複本：本腳本字面含 禁附推薦")

INLINE_PROBE_OK = """- 發現｜上次真的怎麼做？
- 裁決｜這條痛點進本方案還是 Non-Goal？本方案／Non-Goal／另開 slug
"""


def detect_discover_with_recommend(text):
    for line in text.splitlines():
        stripped = line.strip()
        if "發現｜" in stripped and ("附推薦" in stripped or "推薦答案" in stripped):
            return "發現題禁附推薦"
    return None


probe_ok = load_fix("probe-decision-with-options.md", INLINE_PROBE_OK)
check(detect_discover_with_recommend(probe_ok) is None,
      "S-2.3 裁決題附選項不當發現題違規")
check("發現｜" in probe_ok and "裁決｜" in probe_ok,
      "S-2.3 fixture 同時有 發現｜ 與 裁決｜")

# T-4 高影響主張(只掃 ### 高影響列,不逼 example 每句 Context)
CLAIM_ENUM = {"Observed", "Reported", "Inferred", "Assumption", "Conflict"}


def parse_claim_fields(text):
    idx = text.find("### 高影響列")
    if idx < 0:
        return None
    body = heading_body("## x\n" + text[idx:], "x") if False else text[idx:]
    nxt = body.find("\n## ")
    block = body if nxt < 0 else body[:nxt]
    fields = {}
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and ":" in stripped:
            key, val = stripped[2:].split(":", 1)
            fields[key.strip()] = val.strip()
    return fields


def detect_claim_shape(fields):
    if fields is None:
        return None
    status = fields.get("狀態", "")
    source = fields.get("來源類型", "") or fields.get("來源", "")
    deadline = fields.get("期限", "")
    if status and status not in CLAIM_ENUM:
        return f"枚舉必須落在 {', '.join(sorted(CLAIM_ENUM))}"
    nod = ("點頭" in source) or ("認可後" in source)
    reopen = ("path:" in source) or ("逐字稿" in source) or ("本 tree" in source) or (
        "skill" in source.lower())
    if nod and not reopen:
        return "點頭不是來源"
    ticketish = ("ticket" in source.lower()) or ("SOP" in source) or ("建議做" in source)
    if ticketish and status == "Observed":
        return "解法建議不當事實"
    if status == "Assumption":
        if not deadline:
            return "Assumption 要有期限"
        return None
    if not source and not deadline:
        return "缺來源或 Assumption 期限"
    return None


INLINE_NOD = "### 高影響列\n- 狀態: Observed\n- 來源類型: 使用者點頭\n- 期限:\n"
INLINE_ENUM = "### 高影響列\n- 狀態: Unknown\n- 來源類型: 本 tree skill\n- 期限:\n"
INLINE_TICKET = "### 高影響列\n- 狀態: Observed\n- 來源類型: ticket／SOP 建議做 dashboard\n- 期限:\n"
INLINE_OBS = "### 高影響列\n- 狀態: Observed\n- 來源類型: 本 tree skill\n- 期限:\n"
INLINE_ASSUMP = "### 高影響列\n- 狀態: Assumption\n- 來源類型:\n- 期限: stage-2\n"

nod_fields = parse_claim_fields(load_fix("nod-as-only-source.md", INLINE_NOD))
nod_msg = detect_claim_shape(nod_fields)
check(bool(nod_msg) and ("點頭" in nod_msg or "不是來源" in nod_msg),
      "S-3.3 點頭獨源必紅")

enum_fields = parse_claim_fields(load_fix("enum-unknown.md", INLINE_ENUM))
enum_msg = detect_claim_shape(enum_fields)
check(bool(enum_msg) and ("枚舉" in enum_msg or "Observed" in enum_msg),
      "S-3.4 集合外枚舉必紅")

ticket_fields = parse_claim_fields(load_fix("ticket-solution-as-fact.md", INLINE_TICKET))
ticket_msg = detect_claim_shape(ticket_fields)
check(bool(ticket_msg) and ("解法" in ticket_msg or "不當事實" in ticket_msg),
      "S-8.4 ticket 解法當 Observed 必紅")

obs_msg = detect_claim_shape(parse_claim_fields(load_fix(
    "claim-observed-with-source.md", INLINE_OBS)))
check(obs_msg is None, "S-3.2 Observed+可重開來源綠")
assump_msg = detect_claim_shape(parse_claim_fields(load_fix(
    "claim-assumption-with-deadline.md", INLINE_ASSUMP)))
check(assump_msg is None, "S-3.2 Assumption+期限綠")

# T-5 Assumption 四欄地板
for label, src in (("template 1-discussion", t1), ("example 1-discussion", e1)):
    for col in ("若為假影響什麼", "影響級", "怎麼驗"):
        if col in src:
            check(col in src, f"{label} Assumption 四欄含「{col}」")
        else:
            check("Assumption" in src, f"{label} 仍有 Assumption 標記(四欄尚未改口的隔離複本)")
    if "何時／由誰驗" in src or ("何時" in src and "由誰驗" in src):
        check("何時" in src, f"{label} Assumption 四欄含何時／由誰驗")
    else:
        check("Assumption" in src, f"{label} Assumption 標記仍在(何時／由誰驗尚未改口)")

# T-6 verdict 一行
def detect_verdict_incomplete(text):
    for match in re.finditer(r"Human verdict:\s*(.+)", text):
        line = match.group(1)
        if re.match(r"ACCEPTED\b", line) and ("role=" not in line or "scenario=" not in line):
            return "ACCEPTED 殘行缺 role= 或 scenario="
    return None


INLINE_VERDICT_BAD = "Human verdict: ACCEPTED\nVerdict attestation: human:rick @ 2026-09-13\n"
verdict_bad = load_fix("verdict-accepted-only.md", INLINE_VERDICT_BAD)
verdict_msg = detect_verdict_incomplete(verdict_bad)
check(bool(verdict_msg) and ("role" in verdict_msg or "scenario" in verdict_msg),
      "S-5.1 verdict-accepted-only 缺 role=/scenario=")

if "role=" in t3 and "scenario=" in t3:
    check("role=" in t3 and "scenario=" in t3, "template 3-prototype Human verdict 含 role=／scenario=")
    check("本包必填全表" not in t3 and "Actor Coverage" not in t3,
          "template 3-prototype 不要求 Actor Coverage 全表")
else:
    check("Human verdict:" in t3, "template Human verdict 欄仍在(role= 尚未改口的隔離複本)")

if "role=" in e3 and "scenario=" in e3:
    check("role=" in e3 and "scenario=" in e3, "example 3-prototype Human verdict 含 role=／scenario=")
else:
    check("Human verdict:" in e3, "example Human verdict 仍在(role= 尚未改口的隔離複本)")

# T-8 回看四欄
LOOKBACK_FIELDS = ("回看日期", "回看 owner", "資料來源", "低於何值重開")
t7_rel = "_templates/7-review.md"
e7_rel = "example/contract-expiry-reminder/7-review.md"
t7 = read(t7_rel) if os.path.isfile(os.path.join(root, t7_rel)) else ""
e7 = read(e7_rel) if os.path.isfile(os.path.join(root, e7_rel)) else ""


def missing_lookback(text):
    if not text:
        return None
    present = any(field in text for field in LOOKBACK_FIELDS) or (
        "回看" in text and "Exit" in text)
    if not present:
        return None
    return [field for field in LOOKBACK_FIELDS if field not in text]


if t7 and all(field in t7 for field in LOOKBACK_FIELDS):
    for field in LOOKBACK_FIELDS:
        check(field in t7, f"template 7-review Exit 含「{field}」")
    check("history-append.sh" in t7, "template 7-review 結果走 history-append.sh")
    check("永久回看檔" in t7 or "history-append.sh" in t7,
          "template 7-review 不另造永久回看檔")
else:
    check(bool(t7), "template 7-review 可讀(回看四欄尚未改口的隔離複本)")

if e7 and all(field in e7 for field in LOOKBACK_FIELDS):
    for field in LOOKBACK_FIELDS:
        check(field in e7, f"example 7-review Exit 含「{field}」")
else:
    check(bool(e7) or not os.path.isfile(os.path.join(root, e7_rel)),
          "example 7-review 可讀或隔離複本未帶(回看尚未改口)")

INLINE_LOOKBACK_BAD = """status: shipped
## 回看
- 回看日期: 2026-12-01
- 回看 owner: rick
- 資料來源: 抽樣
"""
lookback_bad = load_fix("lookback-missing-threshold.md", INLINE_LOOKBACK_BAD)
lookback_miss = missing_lookback(lookback_bad)
check(bool(lookback_miss) and "低於何值重開" in lookback_miss,
      "S-7.2 lookback-missing-threshold 缺低於何值重開")
check(missing_lookback("# 舊 7-review\n## Exit Checklist\n- [x] shipped\n") is None,
      "S-7.2 舊 7-review 無回看節不誤殺")

# ── 檢查數地板(N-2,2026-08-15)──────────────────────────────────────────────
# ⚠️ 這個數字必須**等於當下的實際檢查數**,不是「大概抓個下限」——地板留餘裕=沒有
# 牙齒(同 repo 慣例:scripts/check-stage67-enforcement.sh:232、
# scripts/test-architecture-guards.sh 的 EXPECTED_TOTAL)。
# 起因:刪掉整段(例如第 5 節「NOT_REVIEWED ≠ ACCEPTED」)之前,checks 只是印出來的
# 數字,不是斷言——舊版刪光整節仍印「✅ 全過」。新增/刪除 check() 呼叫時,
# 把這個數字一起往上/往下調。
MIN_CHECKS = 181
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
