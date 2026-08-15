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
    if re.match(r"^\s*-\s*Operational Context\s*[::(]", line):
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
check("跳過本階段 → 兩檔皆不建" in t3, "template 3-prototype 保留跳過路徑")

# ── 9. 舊模板仍可渲染 ──
# renderer 不存在時(隔離測試根目錄,如 test-architecture-guards.sh 的 seed()複本)
# 明著跳過,不得靜默略過(同檔已知教訓:靜默 skip = 假綠)。
renderer = os.path.join(root, "scripts", "render-methodology-corrections.sh")
if os.path.isfile(renderer):
    result = subprocess.run([renderer, "--check"], cwd=root, capture_output=True, text=True)
    check(result.returncode == 0, "舊模板/衍生檔仍可渲染(renderer --check)",
          (result.stdout + result.stderr).strip())
else:
    print(f"⚠️  renderer 不存在於此 root({renderer}),略過『舊模板仍可渲染』檢查 "
          "—— 僅限隔離測試根目錄,正式 repo 執行不會走到這條分支", file=sys.stderr)

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

if failures:
    print(f"❌ real-world interaction checks: {checks - len(failures)}/{checks} passed")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)
print(f"✅ real-world interaction checks: {checks}/{checks} passed")
PY
