# Agent Attempt 可觀測性設計(Workstream C)

> 目的:為 dev-flow Stage 6/7 的多模型派工建立 **Agent Attempt 級**可觀測性 ——
> 量化 first-pass rate / rework / escalation,找出高失敗 Prompt 組合,
> 人類核准後改版(閉環)。
> 定位:本檔是設計正本;可執行正本 = `observability/schema/*.schema.json` +
> `observability/devflow_obs/`(驗證器/寫入器/讀取器/統計)。
> runtime(dev-run 派工迴圈、hooks)在 plugin repo
> `~/.claude/plugins/local/dev-flow/`,本 repo 一律只寫 **interface
> contract**(§7);待辦清單見 `notes/change-manifests/observability.md`。

## 0. 核心原則

- 追蹤單位 = 一次有意義的 **Agent Attempt / Review / Tool lifecycle**;
  **不為每段 LLM 文字打 Trace ID、不將段落當 span**(ids.py 只有四種 kind)。
- 兩條追溯鏈分離,不混 ID:
  - **業務鏈**:`R → S → T → 測試名含 S-id → D → F`(既有,README §4,不動)
  - **執行鏈**:`Run → Attempt → Candidate → Review → Finding`
    (`run_`/`att_`/candidate_sha/`rev_`/`fnd_`)
  - 橋接欄位:事件上的 `task_id`(T-n)、`scenario_ids`(S-n)、
    `business_finding_id`(F-n)把執行鏈掛回業務鏈,但兩邊各自配號。

## 1. 現況審核結論(2026-08-02,對照 audit)

| 問 | 答 | 證據 |
|---|---|---|
| dev-run 如何派 Agent | prompt 層:主對話(opus/fable5)逐 T 派 fresh subagent,無程式碼 scheduler | dev-run SKILL.md:49-63 |
| Worker/Reviewer prompt 在哪 | 內嵌在 SKILL.md 逐 T 迴圈的三件套描述,**每次臨場組裝、無固定模板檔** → prompt registry 先給穩定 prompt_id 才可統計 | SKILL.md:51-59 |
| model escalation 在哪 | README §5 驗證五律 5 + §9 表(正本);SKILL.md:45 摘要副本 | README.md:182-186、293-305 |
| Claude Code transcript 可重用 ID? | hooks 收到 HOOK_INPUT(含 session_id);但 coordinator 拿不到 subagent 的 session id,transcript 訊息 uuid 也非穩定 API → **只作 `session_ref` 關聯參考,不當主鍵** | _guard_impl.py:12 |
| hooks 能捕捉什麼 | PreToolUse Edit/Write/Read(契約防篡改/圍欄②/scope 外寫入)、PreToolUse Bash(守衛破壞/上游 shell 讀)、PostToolUse Bash(git status 對照+契約 hash 漂移+工具結束)、devtalk-guard(盲檢) | hooks.json:3-50;_guard/_prebash/_postbash_impl.py |
| 6-notes 已記什麼 | 執行軌跡節:每 T 一列(T-id\|失敗分類\|升階史\|回合數\|原因)——**沿用,是 legacy 資料源** | _templates/6-implementation-notes.md:75-78 |
| Stage 7 已彙總什麼 | 執行記錄節:模型分佈\|升階次數\|allow/D-n 清單 | _templates/7-review.md:54-55 |
| runtime state 在哪 | **per-worktree**:`<root>/.devflow/exec.json` + git-dir sentinel(worktree 的 git-dir 各自獨立) | _exec_impl.py:13-15;devflow-lib.py:101-107 |
| 多 worktree 同寫 ledger 有無競爭 | 現制無 ledger;若硬塞單一共用檔會有。本設計:runs 住各 worktree 自己的 `.devflow/`,且 run 內**每寫入者一檔** → 無共用 append | §4 |
| `.devflow/` 守衛語意 | agent 端 Edit/Write 直改 `.devflow/` 被 guard 擋;shell `rm/mv/truncate/>` 進 `.devflow/` 被 prebash 擋;postbash 把 `.devflow/` 列 allowed_prefix(不當 scope 違規) | _guard_impl.py:46-47;_prebash_impl.py:26;_postbash_impl.py:17 |

結論:**不能**叫 Worker/agent 直接 append `.devflow/ledger.jsonl`(會被守衛擋,
且違反單一寫入者)。事件寫入必須走正式 runtime writer(§7)。

## 2. ID 體系(二節)

| ID | 格式 | 生成者 | 說明 |
|---|---|---|---|
| `run_id` | `run_<26 字 Crockford ULID>` | Coordinator(devflow_obs.ids) | 一次 Stage 6 開跑(start→stop)= 一個 run;restart 續用檔案系統裡的 run 目錄 |
| `stage` | `6-implementation` / `7-review` | 常量 | 事件欄位,非 ID |
| `task_id` | `T-n`(既有) | 5-tasks | 業務鏈,保留 |
| `attempt_id` | `att_<ULID>` | Coordinator 派工當下 | 一次執行者派工 = 一個 attempt |
| `parent_attempt_id` | 同上 | Coordinator | 升階/rework 重派時指向前一攻 → 可重建升階鏈 |
| `agent_role` | enum worker/reviewer/adviser/verifier | — | 事件欄位 |
| `review_id` | `rev_<ULID>` | Coordinator | 一次 reviewer 派工 |
| `finding_id` | `fnd_<ULID>` | Coordinator(收 reviewer 回報時配號) | 執行鏈 finding;Stage 7 的業務 F-n 用 `business_finding_id` 橋接 |
| `prompt_id` | slug(如 `stage6-worker`) | registry | §5 |
| `prompt_version` | semver | registry(人類核准) | §5 |
| `prompt_hash` | `sha256:<64hex>` | runtime 對派工模板正文計算 | 抓「版本沒升但內容改了」的漂移 |
| `context_manifest_hash` | `sha256:<64hex>` | `event_validate.context_manifest_hash()`(canonical JSON) | §6 |

性質保證:可跨 restart(純字串、住檔案系統);Worker↔Reviewer 靠
`attempt_id`/`review_id` 互指關聯;**由 Coordinator/runtime 生成,不讓 LLM 自編**
(LLM 只轉抄 runtime 給的 ID);ULID 時戳可回讀(`ids.timestamp_of`)供 retention。

## 3. 事件 lifecycle(三節)

22 種事件(正本:`observability/schema/agent-event.schema.json` events 區;ID-10 合流補 final_fresh_run 兩事件):

```
run_started → stage_started → [每 T:
  agent_dispatched → attempt_started → (tool_invoked/tool_completed)* →
  attempt_completed → candidate_created? →
  mechanical_gate_started/completed* →
  review_started → review_completed → finding_created* →
  (task_rework_requested | task_escalated)* → task_accepted ]
→ final_fresh_run_started → verification_layer_started/completed*(Gauntlet)
  → final_fresh_run_completed
→ stage_completed → run_completed
```

- envelope 必填:`schema, seq, timestamp(含時區), run_id, event_type, writer`;
  `stage/task_id/session_ref/note` 選填;其餘欄位**只在適用事件出現**
  (欄位矩陣在 schema JSON,validator 機械強制;未知欄位拒收,擴充走 `x_` 前綴)。
- `attempt_completed.result` 語意:**裁決後結果**(Verify 紅 → 直接 FAIL;
  Verify 綠 → 依 review verdict),由 coordinator 於裁決當下寫入,
  並附 `failure_category`(FAIL 時必填,五律 5)。
- `candidate_created.candidate_sha` = T review PASS 後 coordinator 所做的 commit hash。

## 4. Ledger 佈局與併發安全(四節)

```
<worktree>/.devflow/runs/<run_id>/
├── manifest.json                  # coordinator 開 run 時 atomic 寫
├── coordinator/events.jsonl       # run/stage/task lifecycle(coordinator 單寫)
├── attempts/<attempt_id>/
│   ├── events.jsonl               # 只有該 attempt 的 runtime writer 寫
│   ├── context-manifest.json      # atomic
│   └── result.json                # atomic finalize 標記
├── reviews/<review_id>/events.jsonl
├── hooks/events-<session>.jsonl   # hook 機械事件,每 session 一檔避免互踩
├── verifier/events.jsonl          # Gauntlet 層(verification engine 單寫)
└── derived/run-events.jsonl       # coordinator 收尾產生;衍生、可隨時重建
```

規則(全部有測試,`observability/tests/`):

1. **每檔單一寫入者**:`writer.EventWriter` 以 `events.jsonl.lock`(O_EXCL)強制,
   雙開即 `AlreadyLocked`;多 worktree 天然分 `.devflow/` 不相見。
2. **atomic write**:快照類(manifest/result/context-manifest/derived)一律
   同目錄 temp + `os.replace`;失敗不毀原檔、不留半成品。
3. **crash 可判**:events 只可能截尾最後一行(reader 容忍並標 `partial_tail`);
   `attempt_started` 存在 + 無 `attempt_completed` + 無 result.json =
   **incomplete attempt**(`ledger.incomplete_attempts`);遺留 lock = 佐證。
4. **restart 恢復**:`ledger.resume_state` 只靠檔案系統重建每 T 進度
   (attempts 數 = 升階預算消耗、open_attempt、accepted)。
5. **derived 是衍生資料**:排序鍵 (timestamp, source, seq),byte 決定性,
   刪掉可重建;JSON/JSONL 是 runtime source,Markdown 摘要一律由 ledger 衍生
   (十一節),禁手動雙寫。
6. **守衛互動**:`.devflow/` 受 guard/prebash 保護 → 事件寫入只能由
   coordinator 經正式 CLI/runtime writer(§7),**Worker 不得直接手改 ledger**。
   ⚠️ prebash regex 陷阱:指令字串中「rm/mv 子字串 + `.devflow/` 路徑」會被攔
   (無 word boundary,`confirm .devflow/...` 也中),故 writer CLI 介面設計成
   **吃 slug/state 自行解析路徑,不在命令列鋪 `.devflow/` 路徑**。

## 5. Prompt Version(五節)

- Registry 格式正本:`observability/schema/prompt-registry.schema.json`
  + 驗證器 `validate_prompt_registry` + 示範 `observability/fixtures/prompt-registry.json`。
- 每版記:`version(semver)、prompt_hash(sha256 of 模板正文)、source_sha(git)、
  change_class、changed、approved_by`;選配 `rubric_version`(review 基準版)、
  `context_packet_version`。
- 版本規則:**Patch** = 文字澄清不改行為;**Minor** = 新增欄位/流程;
  **Major** = 責任邊界或輸出 schema 改變。改版必經人類核准(`approved_by` 必填)。
- ledger 事件只放 `{id, version, hash, source_sha?}`,**預設不保存 Prompt body**。
- 初始 prompt_id 集(對應 dev-run 派工模板):`stage6-worker`、`stage6-reviewer`、
  `stage6-adviser`、`stage7-standards-reviewer`、`stage7-spec-reviewer`。
- registry 檔案住 prompt 正本所在 repo(= plugin repo,外部待辦);本 repo 提供
  schema/驗證/fixture。

## 6. Context Manifest(六節)

`attempts/<id>/context-manifest.json`(schema:`context-manifest.schema.json`):
記 `context_packet_version、files_count、scenario_count、estimated_tokens、
included_artifacts(路徑清單)、contract_hash、living_spec_hash`。
hash 進事件(`context_manifest_hash`),內容不進事件。

**隱私紅線(機械強制,validator + 測試)**:
- 禁載欄位:客戶個資、未去識別化醫療資料、API token、完整 production log、
  完整 source code、完整 LLM transcript → schema `privacy` 區
  (forbidden_exact + forbidden_substrings,巢狀掃描,`estimated_tokens`/
  `transcript_ref` 白名單)。
- 長度管制(1.1,共享契約 §6 表):以**欄位級 maxlen** 為正
  (prompt_id≤100 / prompt_version≤40 / model≤100 / failure_reason≤500 /
  finding_summary(title)≤1000 / command_ref≤500 / artifact_ref≤1000 /
  result_summary≤2000 / task_tag≤50),超限逐欄報錯(訊息含欄名與上限);
  `privacy_value_too_long`(>2000)只當 `x_` 擴充欄與未列欄的 backstop
  (堵「整份貼進來」)。
- transcript 要留:**獨立權限、獨立 retention 的外部儲存**,ledger 只放
  `transcript_ref`(路徑或 hash)。

## 7. 事件寫入責任(七節;runtime 皆在 plugin repo → interface contract)

| 寫入者 | 事件 | 寫入點契約(外部待辦,詳 manifest) |
|---|---|---|
| **Coordinator**(dev-run 主對話) | run/stage lifecycle、agent_dispatched、attempt_started/completed、candidate_created、review_*、finding_created、task_rework/escalated/accepted、derived | dev-run SKILL.md 逐 T 迴圈各步後追加「寫事件」動作;實際落盤經 `devflow-exec.sh event`(新子命令,呼叫 devflow_obs.writer;繞不開 guard 故必須 CLI 化)。start 時建 run 目錄+manifest,並把 run_id 寫進 exec.json 供 hooks 取用 |
| **Hooks**(guard/prebash/postbash/devtalk) | mechanical_gate_completed(gate=guard-write/guard-read/prebash/postbash-detect/devtalk;violation=scope/contract/upstream_read/guard_state)、tool_completed(exit code) | hook 行程直接以 writer API append `hooks/events-<session_id>.jsonl`(hook 非 tool call,不受自家守衛限制);**不推測 agent_role/prompt/model**(schema 機械禁止 hook_forbidden_field),只帶 session_ref,歸屬留給 coordinator 事後關聯 |
| **Verification engine**(old-coder Gauntlet,Workstream D) | final_fresh_run_started/completed、verification_layer_started/completed | 寫 `verifier/events.jsonl`,writer=`verifier`。**欄名正本 = agent-event.schema.json(ID-10 合流)**:layer 事件帶 `layer`、`status`(pass/fail/unverified/n-a,正式欄)、`command_ref`、`result_summary`(單行 ≤2000,受隱私掃描)、`artifact_ref`、`source_sha`、`round?`、`exit_code?`、`failure_kind?`;舊 `result`(PASS\|FAIL)僅讀取相容別名(deprecated since 1.x, removed in 2.0;與 status 並存必須一致,writer API 新寫入一律只寫 status);run 級 completed 帶 `verdict`(PASS/FAIL)、`layers_total`、`layers_failed`、`source_sha` |

## 8. 失敗與結果(八節)

沿用 README §5 驗證五律 5 的 **SPEC/ENV/IMPL/UNKNOWN**(不重定義);另由 ledger
推導 task 級欄位:`first_pass、rework_count、escalation_count、scope_violation、
test_integrity_violation`,run 級:`stage6_verdict、stage7_verdict`
(stage_completed.verdict)。
**避免只用 FAIL 次數當模型錯誤率**:成功率以裁決後 attempt result 計,
rework/escalation/分類分開呈現;ENV 失敗重跑不計升階(legacy 軌跡列同語意)。

## 9. 統計與混淆分離(九節)

`devflow_obs.stats`(CLI `devflow-obs.py stats`)輸出 11 項指標,每項帶
`{value, n, insufficient_sample}`:first-pass rate、mean attempts to acceptance、
rework rate、escalation rate、SPEC/ENV/IMPL/UNKNOWN 分佈、scope violation rate、
test integrity violation rate、per Prompt Version 成功率、per Model(×task_tag,
1.1:受控 enum 多選,一 attempt 進其每個 tag 的組,無 tag 歸 unspecified;舊檔
`x_task_type` 僅讀取相容)成功率、Stage 6 PASS 後 Stage 7 blocker rate、
per Gauntlet layer failure rate。
另附 `reviewer_strictness_by_model`(每 review 平均 finding 數)與
`confound_note`:解讀必須區分 **模型能力 / Prompt 品質 / Context Packet 品質 /
Spec 品質 / 環境問題 / Reviewer 嚴格度 / Task 風險** 七維,單維差異不足以歸因。
legacy Markdown 列只進 task 級指標,不冒充 attempt 級樣本。

## 10. Prompt 優化閉環(十節)

```
累積樣本 → devflow-obs stats → recommend(找高失敗組合)
→ 人讀代表性 Attempts/Findings → 草擬 Prompt 改版
→ 人類核准(registry approved_by)→ 升 Prompt Version(semver)
→ A/B 比較(prompt_version 分組成功率)
```

機械保證(有測試):`recommendations()` **只輸出建議**、每筆
`requires_human_approval: true`、不寫檔不改 Prompt;`n < min_n`(預設 5)一律
列 `skipped_insufficient_sample`,**禁止因 1~2 次失敗宣稱某 Prompt 較差**。

## 11. Markdown 與機器資料(十一節)

JSONL 是 runtime source;6-notes 執行軌跡 / 7-review 執行記錄是**人類摘要視圖**,
應由 ledger 衍生(欄位對應見 manifest「Stage 6/7 待整合欄位」)。無 ledger 的舊
feature 反向相容:`legacy_md.parse_execution_trace` 直接讀執行軌跡表
(無 Run ID 亦可),進 task 級統計。

## 12. 測試對照(十三節逐項)

| 十三節項 | 測試 |
|---|---|
| ID 生成 | test_ids.py(格式/唯一/排序/時戳/kind 拒絕) |
| parent attempt 關聯 | test_event_validate(格式)+ test_ledger `broken_parent_ref` |
| restart 恢復 | test_ledger `test_resume_state_survives_restart` |
| incomplete attempt | test_ledger `test_incomplete_attempt_detected` + CLI fixture R01 |
| 多 worktree 併發 | test_ledger TestConcurrency(雙 attempt 併發 append + 分 worktree) |
| atomic write | test_writer(temp+rename、crash 保原檔、鎖) |
| event schema 驗證 | test_event_validate 全檔 |
| Prompt Version | test_event_validate TestPromptVersion + TestPromptRegistry |
| 隱私欄位禁止 | test_event_validate TestPrivacy(exact/substring/白名單/超長值) |
| stats aggregation | test_stats TestAggregation(11 指標逐項驗數字) |
| 小樣本標示 | test_stats TestSmallSample + TestRecommendations |
| Stage 6/7 verdict 關聯 | test_stats `test_stage6_pass_stage7_blocker_rate` + fixture R02 |
| derived ledger 可重建 | test_ledger `test_derived_is_rebuildable_and_deterministic` |
| 舊 Markdown 無 Run ID 仍能讀 | test_legacy_md + test_cli `test_stats_over_fixtures_and_legacy` |

執行:`python3 -m unittest discover -s observability/tests`(125 案)。
CLI:`python3 observability/devflow-obs.py {validate|validate-registry|incomplete|resume|derive|stats|recommend}`。

## 13. 1.1 變更 + 2.0 移除計畫(共享契約 §6 三項六修正落地,2026-08-02)

`schema_version: "1.1"`(= devflow-contract.json `schema_versions.agent_event`);
事件 envelope `schema` 新寫入用 `devflow-agent-event/1.1`,舊 `/1`(=1.0)讀取相容,
異 major 拒收。fixtures 已同步升 1.1。

**6.3 task_tags(取代 x_task_type 承接方案)**
- 選填 `task_tags`:受控 enum,**正本 = repo 根 `devflow-contract.json` 的
  `task_tags`(12 值)**,schema 只留 `item_enum_source` 指標不重抄;多選陣列;
  非 enum 值拒收(`invalid_enum`);每值 ≤50。掛在 `agent_dispatched` /
  `attempt_started` / `attempt_completed`。
- stats 分組改吃 task_tags(`success_by_model_task_tag`,多選 = 一 attempt 進
  每個 tag 的組),無值歸 `unspecified`;舊檔 `x_task_type` 僅讀取相容,新寫入
  不再產生。

**6.4 result 移除計畫**
- `verification_layer_completed.result`(PASS|FAIL):**deprecated since 1.x,
  removed in 2.0**(schema `deprecations` 區明文)。`status` 四值為唯一正式欄。
- 1.x 讀取端維持相容:result-only 舊檔可過;status/result 並存不一致拒收。
- 新寫入路徑(writer API `EventWriter.append`)一律**只寫 status**:result-only
  輸入正規化為 status,輸出不含 result;不一致或不可映射(ABORTED)拒寫。
- 2.0:`verification_layer_completed` 移除 `result`(optional 列、
  `at_least_one_of`、`field_consistency` 相容規則一併刪);`run_completed` /
  `attempt_completed` / `mechanical_gate_completed` 的 `result` 非別名,不在
  移除範圍。
- migration tests:test_event_validate `TestResultMigration` +
  test_writer `TestWriterStatusOnly`。

**6.6 欄位級長度上限(取代單一 2000 字上限)**
- 見 §6 隱私紅線更新:九項欄位級 maxlen 為正,超限逐欄報錯(訊息含欄名與上限);
  `max_string_len 2000` 降為 `x_` 擴充欄/未列欄 backstop;禁載欄位黑名單維持。
