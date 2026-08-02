# VNext 共享契約(Phase 1 正本;P1~P4 開工前必讀)

> 目的:四個 Plugin Workstream 使用同一套詞彙/schema/gate 條文,避免各說各話。
> 機器可讀版:`devflow-contract.json`(repo 根)。需求正本:docs/prompts/devflow-vnext-runtime.md(衝突以其 Part 2 為準)。
> 本檔「先確定、不完整實作」:條文在此定案,落地由各 Phase 執行。

## 1. G3 正式條件(OC-1;Phase 3 裝入 README §7 正本 + gate-consistency)

G3 新增粗體錨:「**Evidence 契約全過**」,定義為(八點,全部成立):

1. Final Fresh Run 綁定目前受審的 source SHA。
2. 所有 Required Layer = pass。
3. 所有已觸發的 Conditional Layer = pass。
4. 不得存在任何 fail。
5. Required Layer 不得為 unverified 或 n-a。
6. Explicitly Excluded Layer 可為 n-a,但必須附理由。
7. Optional Layer 可為 unverified,但必須誠實標示。
8. Gauntlet PASS 不取代 Standards Axis / Spec Axis / Operational Walkthrough / Coverage Matrix / 真實現象複驗。

同步位置(缺一即 gate-consistency FAIL):README §7 G3 句、gate 摘要/quick reference、7-review 模板頂註、plugin SKILL 階段表、plugin `_gate_consistency_impl.py` 比對表與 tests。

## 2. G2 正式條件(OC-2A/2B;同上同步機制)

新增兩粗體錨:

- 「**Verification Profile**」:G2 必須確認 Profile 已依 lane 正確填寫(見 §4)。
- 「**Demo verdict**」:條件式 —
  - 無 Stage 3 trigger → N/A + 明確原因,可過 G2。
  - 有 trigger 且完成 Demo → 必須 `Human verdict: ACCEPTED`。
  - REVISE → 不得過 G2,必須重做 Demo。NOT_REVIEWED → 不得過 G2。
  - 有 trigger 但跳過 → 必須有 Owner Call 明示。
  - **Agent 不得自行填入 ACCEPTED;Runtime 必須拒絕 Agent 自產的 ACCEPTED**。

## 3. Risk:單一 rubric、兩個 scope(六修正 6.1)

- rubric 唯一正本 = 4-spec Verification Profile 的判準句(金流/auth/資料遺失/併發/公開 API/不可逆/核心醫療)。
- **Feature Risk**(Stage 4 Profile):決定 Profile 深度與 lane 升級。
- **Task Risk**(Stage 5 逐 T `Risk:` 欄):決定 review-mode 缺省 — Task high → Dedicated Review 必要;Feature high **不**強制全 T Dedicated。

## 4. Lane 規則(OC-4)

- Full lane:完整 Profile(Feature Risk/Failure Model/Negative Constraints/Required/Conditional/Explicitly Excluded/Final Fresh Entry Point)。
- Fast lane:最小 Profile(`Risk: normal` / `Verify:` / `Negative Constraints:` / `Advanced verification excluded:` / `Exclusion reason:`)。
- 自動升 Full 條件(任一命中):Risk high、schema migration、權限或資料隔離、資料刪除、不可逆資料轉換、金流/交易、核心醫療業務邏輯、並發/鎖/排程、新增 network/filesystem/subprocess/credential capability、對外 API 契約變更、高風險人機互動。
- `lane: fast` + `Risk: high` → Runtime(start 時)、模板檢查與 Gate **一律拒絕**,除非 Owner Call 明示例外。

## 5. Wave Base 語意(OC-3)

- `feature_initial_base`:feature 開始時的原始 SHA。
- `wave_base_sha`:某 Wave 開始時 integration branch 的固定 SHA;同 Wave 全部 Task 共用。
- `candidate_base_sha`:每個 Candidate 記錄自己建立時的 wave_base_sha;Mechanical Gate 驗證之。
- 下一 Wave 以「所有已 ACCEPTED Wave 的 integration HEAD」為新 Base;Blocked-by 的 Task 只能在依賴 ACCEPTED 並整合後進入後續 Wave。
- 上游 Accepted Commit 變更 → 下游未整合 Candidate 標 `INVALIDATED_BY_UPSTREAM`,不得續審/整合,必須從新 Wave Base 重建;Rework 上游未變則仍用原 Wave Base。
- Integration branch 必須可由 `wave_base_sha + ordered candidate SHA list` 完整重現。

## 6. Event schema(6.4/6.6;正本 = observability/schema/agent-event.schema.json)

- `status`(四值)為正式欄;`result`(PASS|FAIL)= **deprecated since 1.x, removed in 2.0**;1.x 兩者至少擇一、並存必須一致;**輸出新事件一律只寫 status**;需 migration tests。
- 欄位級長度上限(取代單一 2000 字):prompt_id≤100 / prompt_version≤40 / model≤100 / failure_reason≤500 / finding_summary≤1000 / command_reference≤500 / artifact_reference≤1000 / result_summary≤2000 / task_tag≤50。
- 禁載欄位:transcript / prompt_body / source_body / raw_log / patient_data / customer_data / medical_data / token / secret / credential。artifact/transcript 只存 reference+hash。
- `task_tags`:受控 enum(見 devflow-contract.json),多選,禁自由字串。

## 7. exec.json v2 草案(P1 落地;`schema: "exec-v2"`)

既有欄位不變(slug/started/scope/extra/baseline/contract_hashes),新增:

```
schema: "exec-v2"            // 版本鉤子;舊檔無此欄 = v1,循 postbash 舊格式分支相容
run_id: "run_<ULID>"         // start 時生成(runtime 產,非 LLM)
mode: "sequential"|"parallel"
task: "T-n"|null             // --task 模式;null = 舊整 feature scope
wave: {number, wave_base_sha}|null
candidate_sha: null|"<sha>"
state: "<task_states 之一>"|null
feature_initial_base: "<sha>"
```

- `start <slug>` 不帶 `--task` = 完全舊行為(v1 語意,sequential)。
- `--task T-n`:scope = 該 T 的 Files(∪ extra);5-tasks/6-notes **移出恆許**(單寫者=派工者);`.devflow/task/<T-id>/` evidence 放行。
- 異 slug 雙 start 拒絕維持;同 slug 異 task 屬不同 worktree(一樹一武裝不變)。

## 8. Ledger 落盤與 Retention(OC-5)

- 位置:`$DEVFLOW_LEDGER_HOME`,預設 macOS `~/Library/Application Support/DevFlow/ledger/`、Linux `${XDG_STATE_HOME:-~/.local/state}/devflow/ledger/`。
- run manifest 必含:repo_id / run_id / schema_version / created_at / expires_at / source_sha。
- Raw events+manifests 180 天;去識別化 aggregate 365 天+;transcript/prompt body/source body 不保存。
- CLI:`devflow-obs retention status` / `prune --dry-run` / `prune`。**禁**背景自動刪除;預設不雲端同步。
- 工作期事件仍寫專案側 `.devflow/runs/<run_id>/`(per-writer 分檔);收尾歸檔至 LEDGER_HOME。agent 禁直寫 `.devflow/` → 唯一合法通道 = 新 CLI 子命令(P3)。

## 9. 版本握手(§7)

- 方法論正本:`devflow-contract.json`(repo 根,version 2.0.0 + required capabilities)。
- Plugin 聲明檔:`hooks/runtime-capabilities.json`(P3 建):`{supported_contract_versions, runtime_version, capabilities[]}`。
- `devflow doctor`(掛 `devflow-exec.sh doctor`):比對契約版本/必要 capability/schema versions/gauntlet version/ledger schema/gate consistency;不相容 **fail-closed** 並明示(例:`Methodology requires contract 2.0.0 / Runtime supports only 1.x / Parallel execution is unavailable`);sequential 舊專案可走 `legacy compatibility mode` 但必須明示。

## 10. Workstream 檔案所有權(防 merge conflict;跨界需求寫 manifest 交 Integrator)

| Workstream | 獨佔可改 | 明確不可改 |
|---|---|---|
| P1 Execution | hooks/_exec_impl.py、devflow-exec.sh、_guard_impl.py、devflow-lib.py、_prebash_impl.py、_postbash_impl.py、selftest.sh(execution 案)、新 hooks/_gate_impl.py、skills/dev-run/SKILL.md | skills/dev-flow、dev-setup、gate-consistency*、obs 檔 |
| P2 Operational | skills/dev-flow/SKILL.md、新 hooks/_stage3_impl.py(trigger/verdict 讀取)與其 selftest 案 | skills/dev-run(需求寫 manifest)、exec/guard 檔、gate-consistency* |
| P3 Observability | 新 hooks/_obs_impl.py + devflow-obs 薄殼、hooks/runtime-capabilities.json、hooks/devflow_obs_vendor/(如採 vendor)、obs selftest 案、doctor 實作(_doctor_impl.py) | exec/guard 檔(run_id 由 P1 依 §7 生成)、SKILL 檔、gate-consistency* |
| P4 Gauntlet+Gates | hooks/gate-consistency.sh、_gate_consistency_impl.py、skills/dev-setup/SKILL.md、gauntlet 散發與 Stage 7 dispatch 素材、gates selftest 案 | exec/guard 檔、dev-flow/dev-run SKILL(需求寫 manifest) |

- selftest.sh 為共用:各軌**只增不改**既有案;新案函數名帶軌別前綴(p1_/p2_/p3_/p4_)降衝突;整合時由 Integrator 合併。
- 跨軌 wiring(如 devflow-exec.sh 增 `event`/`doctor` 子命令分派行)= P1 檔案 → P3 在 manifest 提供 patch 文字,Integrator 於 Phase 3 套用;或 P1 預留分派(擇一,P1 決定並記錄)。

## 11. 對拍驗收(全軌通用)

- 方法論 reference fixtures 為行為正本:`tests/parallel-stage6/fixtures/`(P1)、`scripts/fixtures/evidence-gauntlet/`(P4)、`observability/fixtures/`(P3)、realworld 檢查語意(P2)。
- 完成定義:plugin selftest 全綠(含新案)+ 對拍 fixtures 行為一致 + `git diff --check` 淨 + 無生成檔誤入 + branch manifest(§9 格式)。
- reference tests 通過 = REFERENCE_PASS;**只有 plugin selftest + 真實行為 = RUNTIME_PASS**;不得混稱。
