# Change Manifest — Workstream C:Agent Attempt Ledger 與 Prompt 優化

> Branch:`devflow-vnext/observability`(base 90d30e88294ab4168871a877ef8ffc398ec3b817)
> Worktree:`../dev-flow-wt-observability`
> 設計正本:`notes/design/agent-attempt-observability.md`
> 依 audit 邊界:runtime(plugin repo)一律不動,只寫 interface contract 與外部待辦。
> 需求正本:docs/prompts/devflow-vnext-fourtrack.md「Prompt C:Agent Attempt Ledger 與 Prompt 優化」— 本檔節號引用以該正本為準。

## 1. 本 repo 實際改動(全為新檔;共享模板/README/Guide twin 零觸碰)

| 路徑 | 內容 |
|---|---|
| `observability/schema/agent-event.schema.json` | 事件 schema 正本(20 事件、欄位矩陣、hook 禁填、隱私區) |
| `observability/schema/context-manifest.schema.json` | context packet 摘要 schema |
| `observability/schema/prompt-registry.schema.json` | Prompt Version registry schema |
| `observability/devflow_obs/`(ids/event_validate/writer/ledger/stats/legacy_md) | 驗證器+寫入器+讀取器+統計(python3 stdlib,零第三方) |
| `observability/devflow-obs.py` | CLI:validate / validate-registry / incomplete / resume / derive / stats / recommend |
| `observability/fixtures/` | 兩個示範 run(升階+crash;stage6 PASS→stage7 blocker+Gauntlet)+ legacy md + registry |
| `observability/tests/`(6 檔 + evtools) | 83 案,十三節逐項對應(對照表:設計文檔 §12) |
| `notes/design/agent-attempt-observability.md` | 設計正本 |
| `notes/change-manifests/observability.md` | 本檔 |

## 2. 事件 schema(摘要;正本 = schema JSON)

- envelope:`schema, seq, timestamp(含時區), run_id, event_type,
  writer(coordinator|hook|verifier)` + 選填 `stage/task_id/session_ref/note`。
- 20 事件:run/stage started+completed、agent_dispatched、attempt_started/completed、
  tool_invoked/completed、candidate_created、mechanical_gate_started/completed、
  review_started/completed、finding_created、task_rework_requested/escalated/accepted、
  verification_layer_started/completed。
- ID:`run_/att_/rev_/fnd_` + 26 字 ULID(Coordinator 生成,非 LLM);業務鏈
  T-n/S-n/F-n 保留,以 `task_id/scenario_ids/business_finding_id` 橋接。
- prompt 物件僅 `{id, version, hash, source_sha?, rubric_version?,
  context_packet_version?}`,禁 body 走私(未知子鍵拒收)。
- 未知頂層欄位拒收;擴充一律 `x_` 前綴(仍受隱私掃描)。

## 3. 實際 runtime 寫入點(外部契約;plugin repo,本 workstream 不改)

| # | 寫入點 | 契約 |
|---|---|---|
| W1 | `devflow-exec.sh start`(_exec_impl.py) | 建 `.devflow/runs/<run_id>/` + manifest.json;把 `run_id` 寫進 exec.json 供 hooks 讀 |
| W2 | 新子命令 `devflow-exec.sh event`(或 `devflow-obs-write`) | coordinator 唯一落盤通道(guard 擋 Edit/Write 直改 .devflow;prebash 擋 shell 重導向)。介面:吃 slug+事件 JSON(stdin),自行解析 run 路徑 —— **命令列不鋪 `.devflow/` 路徑**(prebash regex 無 word boundary,`rm|mv` 子字串 + `.devflow/` 即攔) |
| W3 | dev-run SKILL.md 逐 T 迴圈 | 步 1 派工 → agent_dispatched+attempt_started;收執行者回報/裁決 → attempt_completed(result=裁決後;FAIL 必附 failure_category);步 2 收驗 → review_started/completed+finding_created;路由 → task_rework_requested/task_escalated;PASS commit → candidate_created+task_accepted;收尾 → stage_completed、derive、run_completed |
| W4 | hooks(_guard/_prebash/_postbash/devtalk-guard) | deny/偵測時 append `hooks/events-<session_id>.jsonl`:mechanical_gate_completed(gate=guard-write/guard-read/prebash/postbash-detect/devtalk;violation enum)、tool_completed(exit code)。**不填 agent_role/prompt/model**(schema 機械拒收),只帶 session_ref |
| W5 | dev-run 收尾 | `derive` 重建 run-events.jsonl → 由 ledger 衍生 6-notes 執行軌跡列與 7-review 執行記錄(十一節:禁手動雙寫) |

## 4. Stage 6 待整合欄位(6-notes 模板屬共享檔,本輪不改;待整合)

- 執行軌跡節首加一行 `Run: <run_id>`(節內表五欄**不變**,legacy parser 相容)。
- 每列「升階史」保持 `haiku→sonnet` 格式(legacy_md 依此解析;`->` 亦容)。
- 模板頂註補一句:dev-run 案此節由 `devflow-obs` 從 ledger 衍生,禁手填。

## 5. Stage 7 待整合欄位(7-review 模板/html,待整合)

- 執行記錄節改由 `devflow-obs stats --run <run_dir>` 衍生,欄位:run_id、
  模型分佈、升階次數、first-pass rate、失敗分類分佈、**Prompt Version 清單**、
  D-n/allow 清單(維持既有三欄再加 prompt/run 兩欄)。
- html 執行記錄表同步加 Run ID 與 Prompt Version 欄(README §6 表 7-review 列)。

## 6. Old-coder Gauntlet event 介面(給 Workstream D)

- 寫入者:verification engine,`writer: "verifier"`,單寫 `verifier/events.jsonl`
  (devflow_obs.writer API)。
- 事件:`verification_layer_started {layer, profile?}`、
  `verification_layer_completed {layer, result(PASS|FAIL), exit_code?,
  failure_kind?, evidence_ref?}`;layer 為 slug(如 unit/mutation/property)。
- 統計端已就緒:`failure_rate_by_gauntlet_layer`(fixture R02 + test_stats 驗證)。

## 7. 隱私策略(六節紅線,機械強制)

- schema `privacy` 區:forbidden_exact(prompt_body/transcript/messages/
  source_code/production_log…)+ forbidden_substrings(token/secret/password/
  api_key/authorization/credential/patient/ssn/medical…)+ 白名單
  (estimated_tokens、transcript_ref);巢狀掃描含 `x_` 擴充欄位。
- 字串值 >2000 字元 → 拒收(堵整份 transcript/log/source 入帳)。
- transcript 保留:獨立權限+獨立 retention 的外部儲存,ledger 只存 `transcript_ref`。
- 測試:test_event_validate TestPrivacy(4 案)+ context manifest 掃描案。

## 8. Retention(提案;含 Owner Call)

- `.devflow/runs/` 隨 worktree 生滅;worktree 清除前由 dev-run 收尾歸檔
  `manifest.json + derived/run-events.jsonl + context-manifest.json` 至
  `~/.devflow/ledger/<repo>/<run_id>/`(跨 feature stats 資料池;git 外)。
- ULID 自帶時戳(`ids.timestamp_of`)→ retention 判齡不需額外欄位;
  提案預設:歸檔保存 180 天,transcript 不歸檔。
- **Owner Call(待 rick 裁決,本輪不代答)**:①歸檔位置(user 層 vs repo 內
  `docs/dev/<slug>/evidence/runs/`)②保存期限 ③是否納入備份。

## 9. 測試輸出(原文)

基線(開工前,worktree @ 90d30e8):
```
✅ methodology correction checks: 74/74 passed
✅ renderer fixed point: 4/4 tracked outputs byte-identical
```
TDD RED(cycle 1,模組未實作):
```
ModuleNotFoundError: No module named 'devflow_obs'
Ran 3 tests in 0.000s
FAILED (errors=3)
```
TDD RED(cycle 2,ledger/stats/CLI 未實作):
```
can't open file '.../observability/tests/../devflow-obs.py': [Errno 2] No such file or directory
Ran 58 tests in 0.124s
FAILED (failures=5, errors=4)
```
GREEN(收工,`python3 -m unittest discover -s observability/tests`):
```
Ran 83 tests in 0.320s
OK
```
收工基線迴歸:
```
✅ methodology correction checks: 74/74 passed
✅ renderer fixed point: 4/4 tracked outputs byte-identical
```

## 10. Commit SHA

- `790e6da` observability: 事件 schema + ID 體系 + 併發安全 writer(TDD)
- `9801c7f` observability: ledger 佈局/恢復 + stats 聚合 + legacy 讀取 + CLI + fixtures(TDD)
- 設計文檔 + 本 manifest 為第三個 commit(SHA 見 `git log`,本檔無法載入自身 commit)。

## 11. 外部 plugin 待辦(彙整;全在 `~/.claude/plugins/local/dev-flow/`)

1. `_exec_impl.py` start:建 run 目錄 + manifest + exec.json 加 run_id(W1)。
2. 新事件寫入子命令(W2;吃 slug+stdin JSON,內部呼叫 devflow_obs.writer)。
3. dev-run SKILL.md:逐 T 迴圈各步補「寫事件」動作 + 收尾 derive/衍生摘要(W3/W5)。
4. 四支 hook:deny/偵測時 append hooks 事件檔(W4)。
5. prompt registry 檔落地 plugin repo(prompt 正本旁)+ 五個 prompt_id 初版建檔。
6. plugin 側需 vendor 或 import `devflow_obs`(writer/validate)——部署方式待
   coordinator 定(plugin repo 無 remote,同機直接 path import 亦可)。

> ⚠️ 2026-08-15 核對:以下 6 項,5 項已落地於本 repo(併入後),第 4 項僅 3/4 落地,
> 未全數落地,如實記錄不硬標:
> 1 `hooks/_exec_impl.py:389`(`run_id = L.new_run_id()`)、`:396`(manifest 寫入 run_id);
> 2 `hooks/devflow-obs.sh` + `observability/devflow-obs.py`(事件寫入子命令);
> 3 `skills/dev-run/SKILL.md:53-93`(逐步「寫事件」動作,含事件寫入通道說明);
> 4 **僅 3/4**:`hooks/_guard_impl.py:15-28`、`hooks/_prebash_impl.py:18`、
>   `hooks/_postbash_impl.py:17` 皆有 `_obs_deny` 寫 `mechanical_gate_completed` 事件;
>   但四支 hook 中的 `hooks/devtalk-guard.sh`(`hooks/hooks.json:44` 註冊為
>   PostToolUse,全檔 24 行)未見任何事件呼叫或 obs 相關字串,`hooks/selftest.sh`
>   與 `observability/` 亦無 devtalk 事件測試覆蓋 —— 此項未全數落地;
> 5 `hooks/prompt-registry.json`(存在);
> 6 `hooks/devflow_obs_vendor/devflow_obs/`(vendor 目錄存在)。

## 12. 逐節交代(prompt-c 十四節)

| 節 | 處置 |
|---|---|
| 一 現況審核 | 已做,結論入設計文檔 §1(runtime 全讀,零改動) |
| 二 識別碼 | 實作(ids.py + schema patterns);T/F-id 保留 |
| 三 事件順序 | 實作(schema events 區 + validator) |
| 四 併發安全 | 實作(writer/ledger + 測試);runtime 落盤點 → 外部待辦 W1/W2 |
| 五 Prompt Version | 實作(registry schema+驗證+fixture);registry 落地 plugin → 待辦 5 |
| 六 Context Manifest | 實作(schema+hash+隱私掃描) |
| 七 寫入責任 | interface contract(§3 本檔;hooks 禁推測 → schema 機械強制) |
| 八 失敗與結果 | 實作(stats task 級欄位;分類沿用 README §5,未重定義) |
| 九 統計工具 | 實作(11 指標 + 混淆七維註記 + reviewer 嚴格度) |
| 十 優化閉環 | 實作機械部分(recommend,只建議);流程其餘為人類步驟,寫入設計文檔 §10 |
| 十一 Markdown/機器資料 | 實作 legacy 讀取;6/7 模板衍生欄位 → 本檔 §4/§5 待整合 |
| 十二 Schema 範例 | 納入 schema(§12 範例即 attempt_completed,測試以其為 valid 樣本) |
| 十三 測試 | 14 項全對應(設計文檔 §12 對照表;83 案綠) |
| 十四 輸出 | 兩檔皆備(本檔 + 設計文檔) |

## 13. 不採用/調整的建議(+原因)

- **不建 repo 級單一 `ledger.jsonl`**:prompt-c 一節明示禁令;多 worktree 無鎖
  append 有競爭,且 `.devflow/` 受守衛管制 → 改 per-run per-writer 分檔。
- **不用 Claude Code session/transcript id 當主鍵**:coordinator 拿不到 subagent
  session id,非穩定 API → 降級為 `session_ref` 關聯參考。
- **hook 事件不寫 attempt 歸屬**:hooks 分不清寫入來自哪個 agent(audit 已證),
  七節明令不推測 → schema 直接拒收 hook 填 agent_role/prompt/model。
- **stats 的「Task Type」維度**:5-tasks 現無 task type 欄 → 以 `x_task_type`
  選填承接,無值歸 `unspecified`;是否在 5-tasks 加欄位屬共享模板改動,
  留待 coordinator/Workstream A 整合(本輪不碰模板)。
