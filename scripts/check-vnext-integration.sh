#!/bin/bash
# check-vnext-integration — DevFlow VNext「最薄整合案例」機械檢查(Prompt 0 第十步)。
#
# 用一條 T-1/T-2 可平行的假想 feature(fixtures 住 scripts/fixtures/vnext-integration/)
# 機械驗證四軌串得起來:
#   A(parallel Stage 6):5-tasks(execution.mode: parallel)→ contract_ref 解析零錯誤
#     → 派生單一 Wave 含 T-1/T-2 → 兩個 candidate 過 Mechanical Gate(14 項全 PASS)
#     → 按 integration DAG 排序(Integrate-after 軟依賴)→ wave review 有每 T 獨立
#     verdict + integration verdict → 狀態機 CANDIDATE→…→ACCEPTED 全程合法轉移
#   C(observability):同一條事件流(run→attempt→candidate→gate→review→accepted→
#     verification_layer→run_completed)過 `observability/devflow-obs.py validate`
#   D(evidence gauntlet):Final Fresh Run evidence fixture 過
#     `scripts/devflow-evidence-gauntlet.sh`(含 --source-sha 綁定)
#
# 獨立腳本:不動 74 條基線(check-methodology-corrections)、不動 94/133/21 各家 suite;
# 只複用 A/C/D 的既有工具與 fixture 格式。exit 0 = 全過;exit 1 = 逐條列出失敗。
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
python3 - "$ROOT" <<'PY'
import json
import os
import re
import subprocess
import sys

root = sys.argv[1]
sys.path.insert(0, os.path.join(root, "tests", "parallel-stage6"))
import contract_ref  # noqa: E402

FIX = os.path.join(root, "scripts", "fixtures", "vnext-integration")
checks = 0
failures = []


def check(condition, label, detail=""):
    global checks
    checks += 1
    if not condition:
        failures.append(label + (f": {detail}" if detail else ""))


def load_json(rel):
    with open(os.path.join(FIX, rel), encoding="utf-8") as stream:
        return json.load(stream)


def read(rel):
    with open(os.path.join(FIX, rel), encoding="utf-8") as stream:
        return stream.read()


# ---- 1-3. A:5-tasks 解析 + parallel + 單一 wave 含 T-1/T-2 ----
parsed = None
try:
    parsed = contract_ref.parse_5_tasks(read("5-tasks.md"))
except FileNotFoundError as e:
    check(False, "fixture 5-tasks.md 存在", str(e))
if parsed is not None:
    check(not parsed["errors"], "5-tasks 解析零錯誤(contract_ref)", str(parsed["errors"]))
    check(parsed["execution"]["mode"] == "parallel",
          "execution.mode = parallel(並行明確啟用)", parsed["execution"]["mode"])
    waves = None
    if not parsed["errors"]:
        waves = contract_ref.compute_waves(parsed)
    check(waves == [["T-1", "T-2"]],
          "派生單一 Wave 且同時含 T-1/T-2(Files 不重疊、無硬依賴)", repr(waves))

# ---- 4-5. A:兩個 candidate 過 Mechanical Gate(14 項全 PASS)----
for tid in ("T-1", "T-2"):
    try:
        bundle = load_json(f"gate-{tid}.json")
    except FileNotFoundError as e:
        check(False, f"gate {tid} verdict PASS(14 項全 PASS)", f"fixture 缺:{e}")
        continue
    result = contract_ref.run_gate(bundle)
    bad = [c["id"] for c in result["checks"] if c["status"] != "PASS"]
    check(result["verdict"] == "PASS" and len(result["checks"]) == 14 and not bad,
          f"gate {tid} verdict PASS(14 項全 PASS)",
          f"verdict={result['verdict']} fail={bad}")

# ---- 6. A:integration DAG 排序(Integrate-after 軟依賴:T-1 先整合)----
if parsed is not None and not parsed["errors"]:
    edges = contract_ref.integration_edges(parsed)
    check(("T-1", "T-2") in edges,
          "integration DAG:T-2 Integrate-after T-1(整合順序 T-1 → T-2)", repr(sorted(edges)))
    order = [t["id"] for t in sorted(
        parsed["tasks"],
        key=lambda t: (len([e for e in edges if e[1] == t["id"]]), t["id"]))]
    check(order == ["T-1", "T-2"], "整合排序 = [T-1, T-2]", repr(order))
else:
    check(False, "integration DAG:T-2 Integrate-after T-1(整合順序 T-1 → T-2)", "5-tasks 未解析")
    check(False, "整合排序 = [T-1, T-2]", "5-tasks 未解析")

# ---- 7-8. A:wave review schema + 每 T verdict + integration verdict ----
try:
    wave_review = load_json("wave-review.json")
except FileNotFoundError as e:
    wave_review = None
    check(False, "wave review schema 驗證零錯誤", f"fixture 缺:{e}")
    check(False, "wave review 每 T verdict = PASS 且 integration_verdict = PASS", "fixture 缺")
if wave_review is not None:
    errors = contract_ref.validate_wave_review(
        wave_review["review"], wave_review["wave_tasks"])
    check(not errors, "wave review schema 驗證零錯誤", str(errors))
    verdicts = {e["task"]: e.get("verdict") for e in wave_review["review"].get("tasks", [])}
    check(verdicts == {"T-1": "PASS", "T-2": "PASS"}
          and wave_review["review"].get("integration_verdict") == "PASS",
          "wave review 每 T verdict = PASS 且 integration_verdict = PASS",
          f"verdicts={verdicts} integration={wave_review['review'].get('integration_verdict')}")

# ---- 9. A:狀態機 CANDIDATE→…→ACCEPTED 全程合法 + 只有 ACCEPTED 可勾 ----
path = ["CANDIDATE", "MECHANICAL_PASS", "QUEUED_FOR_INTEGRATION",
        "INTEGRATED", "IN_REVIEW", "ACCEPTED"]
illegal = [(a, b) for a, b in zip(path, path[1:])
           if not contract_ref.is_legal_transition(a, b)]
check(not illegal and contract_ref.can_tick("ACCEPTED")
      and not any(contract_ref.can_tick(s) for s in path[:-1]),
      "狀態機:candidate→gate→整合→review→ACCEPTED 全程合法,且僅 ACCEPTED 可勾 checkbox",
      f"illegal={illegal}")

# ---- 10. C:事件流過 devflow-obs validate ----
run_dir = os.path.join(FIX, "run", "run_01JG8C4V2M0000000000000V01")
obs = subprocess.run(
    [sys.executable, os.path.join(root, "observability", "devflow-obs.py"),
     "validate", run_dir],
    capture_output=True, text=True)
check(os.path.isdir(run_dir) and obs.returncode == 0,
      "C:ledger 事件流 schema + 交叉引用零錯誤(devflow-obs validate)",
      (obs.stdout + obs.stderr).strip()[:400])

# ---- 11. C:事件鏈完整且時序遞增 ----
CHAIN = ["run_started", "attempt_started", "candidate_created",
         "mechanical_gate_completed", "review_completed", "task_accepted",
         "verification_layer_completed", "run_completed"]
events = []
if os.path.isdir(run_dir):
    for dirpath, _, names in os.walk(run_dir):
        for name in sorted(names):
            if name.endswith(".jsonl"):
                with open(os.path.join(dirpath, name), encoding="utf-8") as stream:
                    for line in stream:
                        if line.strip():
                            events.append(json.loads(line))
events.sort(key=lambda e: e.get("timestamp", ""))
positions = {}
ok_chain = True
detail = ""
for etype in CHAIN:
    matched = [i for i, e in enumerate(events) if e.get("event_type") == etype
               and e.get("result", e.get("review_verdict", "PASS")) == "PASS"]
    if not matched:
        ok_chain, detail = False, f"缺事件 {etype}(或非 PASS)"
        break
    positions[etype] = matched[0]
if ok_chain:
    seq = [positions[t] for t in CHAIN]
    if seq != sorted(seq):
        ok_chain, detail = False, f"時序亂:{[(t, positions[t]) for t in CHAIN]}"
accepted_tasks = {e.get("task_id") for e in events
                  if e.get("event_type") == "task_accepted"}
check(ok_chain and accepted_tasks == {"T-1", "T-2"},
      "C:run→attempt→candidate→gate→review→accepted(T-1+T-2)→verification_layer→run_completed 鏈完整",
      detail or f"accepted={sorted(accepted_tasks - {None})}")

# ---- 12. D:evidence fixture 過 gauntlet(含 source SHA 綁定)----
evidence = os.path.join(FIX, "evidence.md")
declared = ""
if os.path.isfile(evidence):
    match = re.search(r"^- Source SHA:\s*(\S+)", read("evidence.md"), re.M)
    declared = match.group(1) if match else ""
gauntlet = subprocess.run(
    ["bash", os.path.join(root, "scripts", "devflow-evidence-gauntlet.sh"),
     evidence] + (["--source-sha", declared] if declared else []),
    capture_output=True, text=True)
check(os.path.isfile(evidence) and gauntlet.returncode == 0,
      "D:Final Fresh Run evidence 過 devflow-evidence-gauntlet(E1–E10 + SHA 綁定)",
      (gauntlet.stdout + gauntlet.stderr).strip()[:400])

if failures:
    print(f"❌ vnext integration scenario: {checks - len(failures)}/{checks} passed")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)
print(f"✅ vnext integration scenario: {checks}/{checks} passed")
PY
