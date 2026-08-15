#!/usr/bin/env python3
"""parallel-stage6 契約測試 runner。

用法:python3 tests/parallel-stage6/run_tests.py <repo-root>

驗三層:
1. `_templates/5-tasks.md` 含選配 parallel 欄位文檔(sequential 必填四欄不動)。
2. `notes/design/parallel-stage6.md` 契約錨(狀態機/gate check id/schema 名/CLI)齊備。
3. `contract_ref.py` 可執行契約行為(解析/缺省/DAG/wave/scope/狀態機/gate/review)
   —— plugin runtime 落地時必須通過同一組 fixtures。
"""
import json
import os
import sys

sys.dont_write_bytecode = True  # 不落 __pycache__,保持工作樹乾淨

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")

checks = 0
failures = []


def check(cond, label, detail=""):
    global checks
    checks += 1
    if not cond:
        failures.append(label + (f": {detail}" if detail else ""))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def fixture(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


def jfixture(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return json.load(f)


def finish():
    if failures:
        print(f"❌ parallel stage6 contract checks: {checks - len(failures)}/{checks} passed")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print(f"✅ parallel stage6 contract checks: {checks}/{checks} passed")
    sys.exit(0)


# ---------- 1. 模板檢查(sequential 不動 + 選配欄位入檔) ----------
tpl = read("_templates/5-tasks.md")
for token in ("- Covers:", "- Files:", "- Verify: `<指令>`", "- Blocked-by:"):
    check(token in tpl, f"模板保留必填欄 {token!r}")
for token in ("execution:", "mode: sequential", "max_parallel_tasks:",
              "rebuild_integration_on_rework:",
              "Integrate-after:", "Risk:", "Review-mode:", "Semantic-conflicts-with:"):
    check(token in tpl, f"模板含選配 parallel 欄位/設定 {token!r}")
check("sequential" in tpl and "parallel" in tpl,
      "模板明文 sequential 缺省 / parallel 須明確啟用")
check("Execution-wave" not in tpl, "模板不得出現手工 Execution-wave 欄")
check("Conflicts-with:" not in tpl.replace("Semantic-conflicts-with:", ""),
      "模板不得要求人工 Conflicts-with(Files overlap 由 Scheduler 判)")

spec_tpl = read("_templates/4-spec.md")
check("- Owner Call 例外:" in spec_tpl,
      "4-spec 模板記載 runtime 唯一認的 Owner Call 例外結構欄(- Owner Call 例外:<理由>)")
check("同一行需同時含" not in spec_tpl,
      "4-spec 模板不得殘留舊版例外描述(同行含 owner call+fast+high),與 runtime predicate 不符")

# ---------- 2. 設計文件契約錨 ----------
design = read("notes/design/parallel-stage6.md")
STATES = ["PENDING", "READY", "RUNNING", "CANDIDATE", "MECHANICAL_PASS",
          "QUEUED_FOR_INTEGRATION", "INTEGRATED", "IN_REVIEW", "REWORK",
          "ACCEPTED", "BLOCKED"]
check(all(s in design for s in STATES), "設計文件含 11 個狀態名",
      f"missing={[s for s in STATES if s not in design]}")
GATE_IDS = ["candidate_exists", "base_sha_match", "files_within_scope",
            "protected_untouched", "red_present_failing", "green_present_passing",
            "red_before_green", "verify_command_match", "verify_exit_zero",
            "s_id_present", "contract_hash_unchanged", "diff_applies",
            "result_schema_complete", "shared_docs_untouched"]
check(all(g in design for g in GATE_IDS), "設計文件含 14 個 gate check id",
      f"missing={[g for g in GATE_IDS if g not in design]}")
for schema in ("devflow-candidate.v1", "devflow-gate-result.v1", "devflow-wave-review.v1"):
    check(schema in design, f"設計文件含 schema {schema}")
check("--task" in design, "設計文件含 start --task CLI 契約")
check("task/<slug>/T-" in design, "設計文件含 task branch 命名")
check("integration/<slug>" in design, "設計文件含 integration branch 命名")

# ---------- 3. 可執行契約(contract_ref) ----------
sys.path.insert(0, HERE)
try:
    import contract_ref as C
except Exception as e:
    check(False, "contract_ref.py 可載入(可執行契約存在)", repr(e))
    print("⚠️  contract_ref 缺失,行為契約檢查全數未執行(RED)。")
    finish()

# --- 3a. 解析與缺省 ---
old = C.parse_5_tasks(fixture("old-format.md"))
check(old["errors"] == [], "舊格式:零錯誤", str(old["errors"]))
check(old["execution"]["mode"] == "sequential", "舊格式:缺省 mode=sequential")
check(old["execution"]["max_parallel_tasks"] == 3, "舊格式:缺省 max_parallel_tasks=3")
check(old["execution"]["rebuild_integration_on_rework"] is True,
      "舊格式:缺省 rebuild_integration_on_rework=true")
check([t["id"] for t in old["tasks"]] == ["T-1", "T-2", "T-3"], "舊格式:T 全解析")
t2 = old["tasks"][1]
check(t2["integrate_after"] == [] and t2["risk"] == "normal" and t2["review_mode"] == "wave",
      "舊格式:per-T 缺省 integrate_after=[]/risk=normal/review_mode=wave")

par = C.parse_5_tasks(fixture("parallel-basic.md"))
check(par["errors"] == [], "parallel-basic:零錯誤", str(par["errors"]))
check(par["execution"]["mode"] == "parallel", "parallel-basic:mode=parallel")
check(par["execution"]["max_parallel_tasks"] == 2, "parallel-basic:max_parallel_tasks=2")
by_id = {t["id"]: t for t in par["tasks"]}
check(by_id["T-2"]["integrate_after"] == ["T-1"], "parallel-basic:Integrate-after 解析")
check(by_id["T-3"]["risk"] == "high" and by_id["T-3"]["review_mode"] == "dedicated",
      "parallel-basic:Risk high → 缺省 dedicated")
check(by_id["T-5"]["risk"] == "normal" and by_id["T-5"]["review_mode"] == "dedicated",
      "parallel-basic:normal 明寫 dedicated 有效")
check(by_id["T-5"]["semantic_conflicts"] == ["T-2"], "parallel-basic:Semantic-conflicts-with 解析")
check(by_id["T-4"]["blocked_by"] == ["T-1", "T-2"], "parallel-basic:Blocked-by 多值解析")
check(by_id["T-1"]["blocked_by"] == [], "parallel-basic:— 解析為空依賴")

bad = C.parse_5_tasks(fixture("bad-mode.md"))
check(any("turbo" in e for e in bad["errors"]), "非法 mode 拒收(fail-closed)", str(bad["errors"]))
unk = C.parse_5_tasks(fixture("unknown-exec-key.md"))
check(any("max_parallel" in e and "未知" in e for e in unk["errors"]),
      "execution 未知 key 拒收(fail-closed)", str(unk["errors"]))
hw = C.parse_5_tasks(fixture("high-wave-invalid.md"))
check(any("high" in e and "wave" in e for e in hw["errors"]),
      "Risk high + Review-mode wave 拒收", str(hw["errors"]))
sb = C.parse_5_tasks(fixture("sequential-badref.md"))
check(any("T-9" in e for e in sb["errors"]),
      "sequential 模式也驗新欄位引用完整性(T-9 不存在)", str(sb["errors"]))

# --- 3a-2. 續行禁令:保留欄名不得被 Boundaries/Intent 續行遮蔽(fail-closed) ---
# 舊行為是 last-write-wins:縮排的 `- Files:` 子項會靜默換掉該 T 真正的 Files,
# errors 為空,而 Files 是 task_scope() 與 gate 的 files_within_scope 的唯一依據。
sh = C.parse_5_tasks(fixture("boundaries-shadow.md"))
check(any("重複保留欄" in e and "Files" in e for e in sh["errors"]),
      "Boundaries 續行的 `- Files:` 子項被判為重複保留欄(不得靜默覆蓋)", str(sh["errors"]))
check(any("重複保留欄" in e and "Verify" in e for e in sh["errors"]),
      "Boundaries 續行的 `- Verify:` 子項被判為重複保留欄", str(sh["errors"]))
check(any("重複保留欄" in e and "Risk" in e for e in sh["errors"]),
      "Intent 續行的 `- Risk:` 子項被判為重複保留欄(Task Risk 決定 review-mode)",
      str(sh["errors"]))
sh_t1 = [t for t in sh["tasks"] if t["id"] == "T-1"][0]
check(sh_t1["files"] == ["internal/handler/contract.go", "internal/service/contract.go"],
      "遮蔽發生時保留首筆 Files,不被續行子項覆蓋", str(sh_t1["files"]))
check(C.task_scope(sh, "T-1") == sorted(sh_t1["files"]),
      "遮蔽發生時 task_scope 不被放寬成整目錄", str(C.task_scope(sh, "T-1")))
sh_t2 = [t for t in sh["tasks"] if t["id"] == "T-2"][0]
check(sh_t2["risk"] == "normal" and sh_t2["review_mode"] != "dedicated",
      "遮蔽發生時 Task Risk / review-mode 不被續行子項改寫",
      f"{sh_t2['risk']}/{sh_t2['review_mode']}")

# 相容性對照組:合法的純文字續寫(example 用的寫法)不得被誤判
cont = C.parse_5_tasks(fixture("boundaries-continuation.md"))
check(cont["errors"] == [], "合法的 Boundaries 純文字續寫不被誤判為重複欄", str(cont["errors"]))
cont_t1 = [t for t in cont["tasks"] if t["id"] == "T-1"][0]
check(cont_t1["files"] == ["internal/handler/contract.go", "internal/service/contract.go"]
      and cont_t1["verify"] == "go test ./internal/... -run TestExpiring",
      "合法續寫時 Files / Verify 維持該 T 自己宣告的值",
      f"{cont_t1['files']} / {cont_t1['verify']}")

# 模板必須明文寫出續行禁令(否則作者無從得知),且保留欄清單與 FIELD_RE 一致
_tpl5 = read("_templates/5-tasks.md")
check("續行禁令" in _tpl5, "5-tasks 模板有「續行禁令」段落")
for _reserved in ("- Covers:", "- Files:", "- Verify:", "- Blocked-by:", "- Risk:",
                  "- Review-mode:", "- Intent:", "- Boundaries:", "- Owner:",
                  "- Integrate-after:", "- Semantic-conflicts-with:"):
    check(_reserved in _tpl5, f"續行禁令列出保留欄「{_reserved}」")

# --- 3b. DAG ---
ur = C.parse_5_tasks(fixture("unknown-ref.md"))
check(any("T-9" in e for e in ur["errors"]), "Blocked-by 引用不存在 T 拒收", str(ur["errors"]))
ce = C.parse_5_tasks(fixture("cycle-execution.md"))
check(any("環" in e and "T-1" in e and "T-2" in e for e in ce["errors"]),
      "execution DAG cycle 拒收且列環路徑", str(ce["errors"]))
ci = C.parse_5_tasks(fixture("cycle-integration.md"))
check(any("環" in e for e in ci["errors"]),
      "integration DAG cycle 拒收(execution 無環仍抓)", str(ci["errors"]))
check(C.execution_edges(par) == {("T-1", "T-4"), ("T-2", "T-4")},
      "execution DAG 邊 = Blocked-by")
check(C.integration_edges(par) == {("T-1", "T-4"), ("T-2", "T-4"), ("T-1", "T-2")},
      "integration DAG 邊 = Blocked-by ∪ Integrate-after")

# --- 3c. Wave ---
waves = C.compute_waves(par)
check(waves == [["T-1", "T-2"], ["T-3", "T-4"], ["T-5"]],
      "parallel-basic waves(決定論 greedy + max=2)", str(waves))
waves4 = C.compute_waves(par, max_parallel=4)
w_of = {t: i for i, w in enumerate(waves4) for t in w}
check(w_of["T-2"] != w_of["T-5"], "Semantic-conflicts-with 禁同 wave(max=4)", str(waves4))
check(all(w_of[p] < w_of["T-4"] for p in ("T-1", "T-2")), "Blocked-by 前置在較早 wave")
check(C.compute_waves(par) == waves, "同輸入同輸出(決定論)")
snapshot = json.dumps(par, sort_keys=True, default=str)
C.compute_waves(par)
check(json.dumps(par, sort_keys=True, default=str) == snapshot,
      "compute_waves 不改輸入(wave 是派生資料,不回寫)")
resumed = C.compute_waves(par, done={"T-1", "T-2"})
check(resumed == [["T-3", "T-4"], ["T-5"]], "restart:done 集合重算恢復", str(resumed))

ov = C.parse_5_tasks(fixture("overlap.md"))
check(ov["errors"] == [], "overlap fixture 本身合法", str(ov["errors"]))
ow = C.compute_waves(ov)
check(ow == [["T-1", "T-3"], ["T-2", "T-4"]], "Files overlap 同 wave 分離", str(ow))
o_of = {t: i for i, w in enumerate(ow) for t in w}
check(o_of["T-1"] != o_of["T-2"], "同檔 overlap 不同 wave")
check(o_of["T-3"] != o_of["T-4"], "目錄前綴 overlap 不同 wave")
pairwise_ok = all(
    not any(C.files_overlap(fa, fb)
            for fa in C.task_scope(ov, a) for fb in C.task_scope(ov, b))
    for w in ow for i, a in enumerate(w) for b in w[i + 1:])
check(pairwise_ok, "同 wave 成員 scope 兩兩不相交(property)")
check(all(len(w) <= 2 for w in waves), "max_parallel_tasks 上限生效")

single = C.parse_5_tasks("""---
feature: single
stage: 5-tasks
status: approved
execution:
  mode: parallel
---
## T-1 單任務
- [ ] 完成
- Covers: R-1 / S-1
- Files: `src/only.ts`
- Verify: `npm test`
- Blocked-by: —
""")
check(single["errors"] == [] and C.compute_waves(single) == [["T-1"]],
      "單一 T 自然退化為 1 wave × 1 task")

seq_err = None
try:
    C.compute_waves(old)
except C.ContractError as e:
    seq_err = e
check(seq_err is not None, "sequential 模式不派生 wave(compute_waves 拒)")

# --- 3a-3. contract_ref/devflow-lib task dict 鍵集合 parity(MED-3) ---
# contract_ref.py 是方法論這邊的可執行契約複本;runtime 正本是 hooks/devflow-lib.py。
# 兩邊各自維護一份 parse_5_tasks,形狀(尤其 A-6 加的 boundaries/intent/owner)
# 必須一致 —— 否則 contract_ref 可能悄悄漏一個鍵,而兩邊各自的測試各過各的,
# 誰都測不出「兩邊其實不一樣」。直接兩邊 import、比對同一份輸入解析出的 task
# dict 鍵集合,釘住正本(不是憑印象寫一份鍵清單去對)。
from importlib.machinery import SourceFileLoader as _SFL
_lib = _SFL("devflow_lib_ref", os.path.join(ROOT, "hooks", "devflow-lib.py")).load_module()
_lib_par = _lib.parse_5_tasks(fixture("parallel-basic.md"))
check(_lib_par["errors"] == [], "devflow-lib parallel-basic:零錯誤(parity 前提)",
      str(_lib_par["errors"]))
_ref_keys = set(par["tasks"][0].keys())
_lib_keys = set(_lib_par["tasks"][0].keys())
check(_ref_keys == _lib_keys,
      "contract_ref/devflow-lib task dict 鍵集合一致(parity)",
      f"contract_ref={sorted(_ref_keys)} devflow-lib={sorted(_lib_keys)}")
check({"boundaries", "intent", "owner"} <= _ref_keys,
      "contract_ref task dict 含 boundaries/intent/owner 全套(A-6,釘正本)",
      str(sorted(_ref_keys)))

# --- 3d. Task scope ---
check(C.task_scope(par, "T-2") == ["src/components/Card.tsx"],
      "task_scope = 單 T Files(task-scoped guard 契約)")
check(C.task_scope(ov, "T-3") == ["src/api/"], "task_scope 保留目錄語意")
check(C.files_overlap("src/api/", "src/api/x.ts") and C.files_overlap("src/a.ts", "src/a.ts")
      and not C.files_overlap("src/a.ts", "src/b.ts"), "files_overlap 判定(相等+目錄前綴)")

# --- 3e. 狀態機 ---
happy_normal = ["PENDING", "READY", "RUNNING", "CANDIDATE", "MECHANICAL_PASS",
                "QUEUED_FOR_INTEGRATION", "INTEGRATED", "IN_REVIEW", "ACCEPTED"]
check(all(C.is_legal_transition(a, b) for a, b in zip(happy_normal, happy_normal[1:])),
      "normal 快樂路徑全合法")
check(C.is_legal_transition("MECHANICAL_PASS", "IN_REVIEW")
      and C.is_legal_transition("IN_REVIEW", "QUEUED_FOR_INTEGRATION"),
      "high 路徑:dedicated review 先於 integration 合法")
for a, b in (("CANDIDATE", "ACCEPTED"), ("RUNNING", "INTEGRATED"),
             ("MECHANICAL_PASS", "ACCEPTED"), ("REWORK", "ACCEPTED"),
             ("PENDING", "RUNNING")):
    check(not C.is_legal_transition(a, b), f"非法轉移 {a}→{b} 被拒")
check(C.is_legal_transition("IN_REVIEW", "REWORK") and C.is_legal_transition("REWORK", "RUNNING"),
      "REWORK 迴圈(回原 task branch 新 attempt)合法")
check(C.is_legal_transition("PENDING", "BLOCKED") and C.is_legal_transition("BLOCKED", "READY"),
      "BLOCKED 進出合法")
check([s for s in C.STATES if C.can_tick(s)] == ["ACCEPTED"],
      "只有 ACCEPTED 可勾 checkbox(未 Review 不可完成)")

# --- 3f. Mechanical Gate ---
def gate(name):
    result = C.run_gate(jfixture(name))
    failed = {c["id"] for c in result["checks"] if c["status"] == "FAIL"}
    return result, failed

res, failed = gate("gate-pass.json")
check(res["verdict"] == "PASS" and failed == set(), "gate-pass:14 項全 PASS", str(failed))
check([c["id"] for c in res["checks"]] == GATE_IDS, "gate 輸出 14 檢查、順序固定")
check(res["schema"] == "devflow-gate-result.v1", "gate 輸出 schema 名正確")
for name, expect in (
    ("gate-scope-excess.json", {"files_within_scope"}),
    ("gate-red-after-green.json", {"red_before_green"}),
    ("gate-contract-drift.json", {"contract_hash_unchanged"}),
    ("gate-verify-mismatch.json", {"verify_command_match"}),
    ("gate-verify-fail.json", {"verify_exit_zero"}),
    ("gate-missing-red.json", {"red_present_failing", "red_before_green"}),
    ("gate-protected.json", {"protected_untouched", "shared_docs_untouched"}),
    ("gate-missing-sid.json", {"s_id_present"}),
    ("gate-schema-incomplete.json", {"result_schema_complete", "s_id_present"}),
):
    res, failed = gate(name)
    check(res["verdict"] == "FAIL" and failed == expect,
          f"{name}:verdict FAIL 且 failed=={sorted(expect)}", str(sorted(failed)))

# --- 3g. Wave review schema ---
ok = jfixture("wave-review-ok.json")
check(C.validate_wave_review(ok["review"], ok["wave_tasks"]) == [],
      "wave review 合法樣本通過")
mv = jfixture("wave-review-missing-verdict.json")
check(any("T-4" in e for e in C.validate_wave_review(mv["review"], mv["wave_tasks"])),
      "缺 per-T verdict → 無效")
ua = jfixture("wave-review-unattributed.json")
check(any("歸屬" in e for e in C.validate_wave_review(ua["review"], ua["wave_tasks"])),
      "finding 無 task 歸屬 → 無效")
ni = jfixture("wave-review-no-integration.json")
check(any("integration_verdict" in e for e in C.validate_wave_review(ni["review"], ni["wave_tasks"])),
      "缺 integration verdict → 無效")
dup = jfixture("wave-review-duplicate-task.json")
check(any("重複" in e and "T-4" in e
          for e in C.validate_wave_review(dup["review"], dup["wave_tasks"])),
      "同一 T 重複 entry → 無效(先 FAIL 後 PASS 不得洗掉 FAIL)")

# --- 3h. sequential regression(真檔) ---
ex = C.parse_5_tasks(read("example/contract-expiry-reminder/5-tasks.md"))
check(ex["errors"] == [], "真檔 example 5-tasks 解析零錯誤", str(ex["errors"]))
check(ex["execution"]["mode"] == "sequential", "真檔 example 落在 sequential(行為不變)")
check([t["id"] for t in ex["tasks"]] == [f"T-{n}" for n in range(1, 8)],
      "真檔 example 7 T 全解析(T-5~T-7 = ID-8 補 S-4~S-6)")
req = ("covers", "files", "verify")
check(all(t[k] for t in ex["tasks"] for k in req), "真檔 example 必填欄完整(同 runtime 驗法)")

finish()
