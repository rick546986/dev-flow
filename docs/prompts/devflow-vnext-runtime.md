> **正本聲明**:本檔為需求正本(canonical specification)。原始 DOCX 僅為歷史輸入快照(historical input snapshot),不維護、不進 Git;後續決策與修改只更新本 Markdown。
> This DOCX-derived Markdown is the maintained source of truth. The original DOCX is a historical input snapshot and is not the maintained source.

> **優先序**:本檔含兩部分 — Part 1 為主要執行計畫,Part 2 為補充執行決策;**兩者衝突時一律以 Part 2 為準**。

# Part 1:主要執行計畫

# DevFlow VNext Runtime 完成、Owner Call 落地與最終驗收 Prompt
你現在要繼續完成 dev-flow 的 VNext 改造。
目前四軌方法論、模板、參考契約、fixtures、Observability 工具及 Evidence Gauntlet 已經在本地方法論 repository 合併，但尚未 push。真正執行 /dev-flow、dev-run、guard、scheduler、review dispatch 與 hooks 的外部 Claude Code Plugin 尚未完成對應改造。
本次工作的核心不是再增加大量說明文件，而是：
讓方法論正本、Plugin Runtime、Gate 規則、Observability、Gauntlet 和真實執行行為完全一致，並使用真正的 /dev-flow 跑完端到端驗證。
在全部 Runtime 和真實 E2E 驗證通過前，不得 push 方法論 repository，也不得宣稱 Parallel Runtime 已正式完成。

# 一、不可違反的核心原則
不得覆蓋使用者現有未提交內容。
不得 force reset、force checkout 或刪除不明 branch。
不得假設 HTML 報告裡的 SHA、branch 與本機現況仍一致，必須重新實際檢查。
不得把「參考契約測試通過」寫成「正式 Runtime 已完成」。
不得讓方法論文件描述 Plugin 尚未支援的能力，而沒有明確標示狀態。
不得建立第二套 Spec、Task、Evidence、Risk、Review 或 Gate 正本。
不得讓 Coordinator 親自修 Worker／Reviewer finding。
不得由 Agent 偽造 Human verdict、Owner Call 或真實使用者接受。
不得讓 Gauntlet 取代 Standards Review、Spec Review 或 Operational Walkthrough。
不得 push remote，除非使用者在全部驗收完成後另外明示。

# 二、先建立工作狀態分類
不要再只使用模糊的 PASS。
本次所有能力必須以以下狀態回報：
DESIGN_PASS方法論與語意設計已完成並通過審查。REFERENCE_PASS參考實作、schema、fixtures 與契約測試已通過。RUNTIME_PASS真正 Plugin Runtime 已實作並通過 Plugin selftest。E2E_PASS使用真正 /dev-flow、dev-run、guard、reviewer 與 gauntlet完成端到端驗證。PENDING尚未完成。BLOCKED因外部依賴、Owner Call 或無法安全確認現場狀態而停止。
在 Runtime 完成前，Stage 6 Parallel、Agent Ledger 與 Final Fresh Run 最多只能是：
DESIGN_PASSREFERENCE_PASSRUNTIME_PENDINGE2E_PENDING

# 三、重新審核兩個 Repository
## 3.1 方法論 Repository
確認目前實際路徑，然後執行：
git status --shortgit branch --show-currentgit rev-parse HEADgit log --oneline --decorate -15git worktree listgit branch --mergedgit branch --no-merged
預期但不得直接相信的狀態：
先前報告的 local main:fc2bf34先前狀態:尚未 push
建立安全備份 branch：
git branch backup/devflow-vnext-before-runtime-$(date +%Y%m%d-%H%M%S) HEAD
如果 main 有新的變更：
不得回退。
重新比較它和 fc2bf34 的差異。
將新增內容納入 Audit。
檢查是否已有後續人工作業。
## 3.2 Plugin Repository
先找出真實 Plugin 路徑，不得把 HTML 報告中的個人絕對路徑寫入公開文件。
候選位置可能是：
~/.claude/plugins/local/dev-flow/
進入 Plugin repository 後執行：
git status --shortgit branch --show-currentgit rev-parse HEADgit log --oneline --decorate -20git worktree listgit branch --mergedgit branch --no-merged
特別檢查：
codex/dev-flow-methodology-corrections
或任何未合併 branch。
回答：
該 branch 是否包含仍需保留的變更？
是否已部分修改 _exec_impl.py、gate、skill 或 hooks？
Plugin 是否有 remote？
Plugin 現有測試與 selftest 是什麼？
Plugin 目前支援的方法論契約版本是什麼？
哪些檔案是真正 Runtime 正本？
哪些檔案由 setup／installer 產生，不能直接手改？
如果無法安全判定未合併 branch 是否應保留：
不得 merge 或刪除。
建立 Audit 報告。
將它列為 BLOCKED。
其餘不衝突工作可以繼續，但不得完成最終 Integration。

# 四、產出新的 Runtime Audit
在方法論 repository 建立或更新：
notes/change-manifests/20-runtime-audit.md
內容：
# Runtime Audit## Methodology Repository- Path:- HEAD:- Branch:- Dirty files:- Backup branch:- Existing VNext status:## Plugin Repository- Path:- HEAD:- Branch:- Dirty files:- Unmerged branches:- Existing tests:- Runtime entry points:- Generated files:- Existing partial implementation:## Capability Matrix| Capability | Design | Reference | Runtime | E2E ||---|---|---|---|---|| Parallel scheduler | | | | || Task-scoped guard | | | | || Candidate gate | | | | || Wave review | | | | || Operational Stage 3 | | | | || Attempt ledger | | | | || Prompt registry | | | | || Final Fresh Run | | | | || Gate consistency | | | | |## Risks- ## Safe implementation base- Plugin Base SHA:- Methodology Base SHA:

# 五、正式採納的 Owner Call 決策
以下決策視為使用者已核准，不再等待 Agent 自行判斷。
## OC-1：Evidence 正式納入 G3
同意升格為正式 G3 條件。
但不得寫成「所有驗證 Layer 都必須 PASS」。
精確條件：
1. Final Fresh Run 必須綁定目前接受審查的 source SHA。2. 所有 Required Layer 必須為 pass。3. 所有已觸發的 Conditional Layer 必須為 pass。4. 不得存在 fail。5. Required Layer 不得為 unverified 或 n-a。6. Explicitly Excluded Layer 可以為 n-a，但必須附理由。7. Optional Layer 可以為 unverified，但必須誠實標示。8. Gauntlet PASS 不取代：   - Standards Axis Review   - Spec Axis Review   - Operational Walkthrough   - Coverage Matrix   - 真實現象複驗
請同步修改：
README Gate 唯一正本。
Gate 摘要與 quick reference。
Stage 7 模板。
Plugin gate consistency table。
Plugin _gate_consistency_impl.py 或實際等價檔案。
Gate consistency tests。
不得只改 README 而讓 Plugin test 失敗。

## OC-2：Verification Profile 與 Demo Verdict 納入 G2
拆成兩個獨立條件。
### OC-2A：Verification Profile
G2 必須確認 Verification Profile 已依 lane 正確填寫。
### OC-2B：Stage 3 Demo Verdict
只有在 Stage 3 trigger 成立時，G2 才要求：
Human verdict: ACCEPTED
規則：
沒有 Stage 3 trigger→ N/A + 明確原因，可以過 G2。有 trigger 且完成 Demo→ 必須 ACCEPTED。有 trigger，結果為 REVISE→ 不得過 G2，必須重做 Demo。有 trigger，結果為 NOT_REVIEWED→ 不得過 G2。有 trigger 但決定跳過→ 必須有使用者／Owner 明示的 Owner Call。
Agent 不得自行填入 ACCEPTED。

## OC-3：採用同 Wave 同 Base SHA
正式採用，但要明確定義三種 Base：
feature_initial_baseFeature 開始時的原始 SHA。wave_base_sha某個 Wave 開始時，integration branch 的固定 SHA。candidate_base_sha每個 Candidate 記錄自己建立時使用的 wave_base_sha。
規則：
同一 Wave 的所有 Task 必須共用同一個 wave_base_sha。
下一 Wave 以先前所有 ACCEPTED Wave 的 integration HEAD 為新 Base。
Blocked-by 的 Task 只能在依賴 Task ACCEPTED 並整合後進入後續 Wave。
Candidate 必須保存 candidate_base_sha。
Mechanical Gate 必須驗證 Candidate Base。
上游 Accepted Commit 變更時，下游未整合 Candidate 必須標記：
INVALIDATED_BY_UPSTREAM
Invalidated Candidate 不得繼續 Review 或整合，必須從新 Wave Base 重建。
Rework 若上游未變，仍從原 Wave Base 重建。
Integration branch 必須可由：
wave_base_sha + ordered candidate SHA list
完整重現。

## OC-4：Verification Profile 的 lane 規則
不採用「Fast lane 完全選配」。
### Full lane
必須填完整 Profile：
Feature RiskFailure ModelNegative ConstraintsRequired LayersConditional LayersExplicitly Excluded LayersFinal Fresh Entry Point
### Fast lane
仍必須填最小 Profile：
Risk: normalVerify:Negative Constraints:Advanced verification excluded:Exclusion reason:
Fast lane 若出現以下任一情況，必須自動升為 Full：
Risk: highschema migration權限或資料隔離資料刪除不可逆資料轉換金流或交易核心醫療業務邏輯並發、鎖或排程新增 network/filesystem/subprocess/credential capability對外 API 契約變更高風險人機互動
Runtime、模板檢查與 Gate 必須拒絕：
lane: fastRisk: high
除非 Owner Call 明示例外。

## OC-5：Ledger Retention
採用 Git 外保存。
支援設定：
DEVFLOW_LEDGER_HOME
預設：
macOS:~/Library/Application Support/DevFlow/ledger/Linux:${XDG_STATE_HOME:-~/.local/state}/devflow/ledger/
保存政策：
Raw events / manifests:180 天。去識別化 aggregate statistics:365 天或長期。完整 transcript:不保存。完整 Prompt body:不保存，只保存 ID、version、hash、source SHA。Source body / raw production logs:不保存。客戶資料 / 醫療資料 / token / secret:禁止寫入。
每個 run manifest 必須有：
repo_idrun_idschema_versioncreated_atexpires_atsource_sha
提供：
devflow-obs retention statusdevflow-obs prune --dry-rundevflow-obs prune
不得建立背景自動刪除服務。
預設不做一般雲端同步。

## OC-6：補 Parallel 流程圖
同意立即補圖，不必等待 OC-1／OC-2。
Stage 6 圖只呈現：
Task DAG→ Wave Base→ Task Worktrees→ RED / GREEN / Verify→ Candidate→ Mechanical Gate→ Integration DAG→ Dedicated Review 或 Wave Review→ ACCEPTED
另畫一張跨階段圖：
ACCEPTED Tasks→ Final Fresh Gauntlet→ G3
所有圖遵守：
_templates/diagram-style.md
Markdown 保留 ASCII 正本，HTML 使用 inline SVG。

# 六、修正現有方法論設計中的六個問題
## 6.1 Feature Risk 與 Task Risk 分開
Risk rubric 只有一個正本，但 Risk 有兩個 scope：
Feature Risk定義於 Stage 4 Verification Profile。Task Risk定義於 Stage 5 單一 Task。
例如：
Feature Risk: highT-1 migration:Task Risk: highT-2 UI copy:Task Risk: normal
Feature high 不代表所有 Task 都必須 Dedicated Review。
Task high 必須 Dedicated Review。
請更新模板、reference contract、tests 和說明。

## 6.2 Stage 3 Demo 與多 Variant 分開
規則改成：
存在真實世界互動風險→ Stage 3 Demo 必要。存在尚未決定的互動方案→ 必須提供 2～4 個結構不同 Variant。互動方式已由既有核准 Pattern 明確決定→ 可以只提供 1 個可操作 Demo。
不得為了符合數量而製作沒有差異的假 Variant。

## 6.3 Task Type 不進 5-tasks 必填欄
不要新增必填 Task Type。
Observability 使用受控 metadata：
{  "task_tags": [    "api",    "authorization"  ]}
建議 enum：
apiuidatabaseintegrationinfrastructuretestdocumentationsecurityauthorizationmigrationworkflowother
允許多選。
禁止無限制自由字串造成統計分類漂移。

## 6.4 result 相容別名必須有移除計畫
目前 Event Schema 的正式欄位為：
status
舊欄位：
result
只作 migration alias。
規則：
Schema 1.x:允許 status 或 result。兩者並存時必須一致。輸出新事件一律只寫 status。Schema 2.0:移除 result，只允許 status。
文件標示：
result:deprecated since 1.xremoved in 2.0
增加 migration tests。

## 6.5 Changed-line Coverage 不取代 Global Coverage
正式措辭：
Changed-line coverage 是本次變更充分測試的主要 coverage 證據；Global coverage 是整體專案回歸與趨勢指標，不能單獨證明本次改動已充分驗證。
Evidence 可同時記：
changed-line coveragebranch coverageglobal coverage trend
禁止只靠 global percentage 宣稱本次改動充分測試。
也不要完全禁止 global coverage。

## 6.6 Ledger 長度限制改成欄位級
不要所有字串統一限制 2,000 字。
至少採：
prompt_id             <= 100prompt_version        <= 40model                  <= 100failure_reason         <= 500finding_summary        <= 1000command_reference      <= 500artifact_reference     <= 1000result_summary         <= 2000task_tag               <= 50
明確禁止欄位：
transcriptprompt_bodysource_bodyraw_logpatient_datacustomer_datamedical_datatokensecretcredential
對 artifact／transcript 只保存 reference 與 hash。

# 七、新增方法論與 Runtime 的版本握手
這是本次必須增加的防漂移設計。
目前最大的風險是：
方法論文件已升級但 Plugin Runtime 還停在舊版
請建立單一機器可讀契約版本。
先審視 repo 是否已有等價版本機制；已有則沿用，不得建立第二套。
若沒有，新增最小契約檔，例如：
{  "devflow_contract_version": "2.0.0",  "required_runtime_capabilities": [    "task_scoped_guard",    "parallel_wave_execution",    "candidate_gate",    "attempt_ledger",    "final_fresh_run",    "operational_demo_gate"  ]}
Plugin 必須聲明：
{  "supported_contract_versions": [    "2.0.0"  ],  "runtime_version": "...",  "capabilities": [    "..."  ]}
新增：
devflow doctor
或現有 CLI 的等價指令。
至少檢查：
方法論契約版本Plugin Runtime 版本必要 capabilityschema versiongauntlet versionledger schema versiongate consistency
不相容時 fail closed：
Methodology requires contract 2.0.0Runtime supports only 1.xParallel execution is unavailable
不得靜默退回舊行為。
Sequential 舊專案可以繼續使用相容模式，但必須明確顯示：
legacy compatibility mode

# 八、Plugin Runtime 使用 Worktree 並行實作
先建立 Plugin integration branch。
所有 branch 從同一個已確認安全的 Plugin Base SHA 建立。
建議：
devflow-runtime-vnext/integrationdevflow-runtime-vnext/executiondevflow-runtime-vnext/operationaldevflow-runtime-vnext/observabilitydevflow-runtime-vnext/gauntlet-gates
建立四個獨立 worktree。
## Workstream P1：Execution Runtime
負責：
解析 execution.mode。
解析 Integrate-after。
解析 Feature／Task Risk。
解析 Review-mode。
建立 execution DAG。
建立 integration DAG。
cycle detection。
Files overlap detection。
Semantic conflict handling。
max parallel tasks。
Wave Base 計算。
Candidate invalidation。
start <slug> --task T-n。
Task-scoped guard。
Candidate Commit。
Mechanical Gate。
Task state machine。
Wave integration。
Dedicated／Wave Review。
Rework 後 integration rebuild。
sequential regression。
必須對拍方法論 repo 中的 reference fixtures。
不要複製 reference implementation 當正式 Runtime 而不審視 Plugin 架構。

## Workstream P2：Operational Runtime
負責：
/dev-flow Stage 1 提醒收集 Real-world Context。
Stage 3 trigger 判斷。
Stage 3 Demo 必要性。
多 Variant 是否真的需要的判斷。
Human verdict 讀取。
Agent 不得自行填 ACCEPTED。
G2 的 Demo 條件。
Task Context Packet 加入最小 Operational Context。
Stage 7 Operational Walkthrough 派工。
Plugin skill／agent prompt 更新。
legacy Feature 相容。
不得把完整訪談逐字稿塞入 Worker Context。

## Workstream P3：Observability Runtime
負責：
run_id 建立。
attempt_id 建立。
Review ID 與 Finding ID。
run directory。
per-writer event files。
atomic write。
incomplete attempt。
resume。
event writer CLI。
Coordinator lifecycle events。
Hook mechanical events。
Prompt registry。
Prompt version／hash。
Context manifest。
Retention。
stats。
recommend。
privacy field validation。
contract version integration。
devflow doctor capability reporting。
Hooks 不得填入它無法知道的：
agent_rolemodelprompt_version

## Workstream P4：Gauntlet 與 Gate
負責：
Plugin 派發 Final Fresh Run。
安裝／散發 evidence gauntlet。
Stage 7 單一入口。
清除 stale artifacts。
source SHA binding。
Required／Conditional／Excluded 驗證。
Test Integrity Review prompt。
Verification Layer events。
G2 Gate consistency。
G3 Gate consistency。
Fast／Full Profile 驗證。
Fast＋High Risk 拒絕。
Changed-line＋Global coverage 語意。
Evidence 四值。
Gauntlet 不取代雙軸 Review。
setup／installer 更新。

# 九、Workstream 收驗
每個 Plugin Workstream 必須：
先跑現有測試。
新增失敗測試。
最小實作到綠。
跑相關 selftest。
git diff --check。
確認沒有生成檔誤入 Git。
產出 branch manifest。
逐個可驗證功能 commit。
不修改其他 Workstream 所有權檔案。
finding 退回原 Worker。
收驗報告：
# Plugin Workstream Result- Base SHA:- Branch:- HEAD:- Modified files:- Added capabilities:- Tests before:- Tests after:- Raw outputs:- Known limitations:- External dependencies:- Status:

# 十、整合 Plugin
Merge 順序：
1. execution2. operational3. observability4. gauntlet-gates
每次 merge：
跑該 Workstream tests。
跑 Plugin 全 selftest。
跑 methodology reference fixtures。
跑 gate consistency。
跑 devflow doctor。
確認 capability matrix。
全綠才能 merge 下一軌。
衝突不得用整檔 ours／theirs 粗暴解決。

# 十一、回到方法論 Repository 同步修正
Plugin Runtime 完成後，回到方法論 repository：
落實 OC-1～OC-6。
套用六項設計修正。
加入契約版本握手。
更新 Capability Matrix。
將狀態改成：
DESIGN_PASSREFERENCE_PASSRUNTIME_PASSE2E_PENDING
更新 README。
更新 Stage 1～7 模板。
更新 example。
更新 Guide。
重生 HTML twins。
新增 Parallel SVG。
移除所有本機絕對路徑。
搜尋：
grep -R "/Users/" \  README.md _templates notes tests observability scripts example
公開文件只使用：
~/.claude/plugins/local/dev-flow/
或抽象設定名稱。

# 十二、真正的端到端驗證
契約 fixture 不算最終 E2E。
建立一個獨立 throwaway 測試 repository，不使用正式醫療資料或 production credentials。
必須透過真正 Plugin 執行：
Stage 1→ Real-world ContextStage 2→ DecisionStage 3→ Trigger 判斷→ 可操作 Demo→ 測試用明確 Human fixture  不得把 Agent 自填當真人核准Stage 4→ Operational Context→ Verification Profile→ Failure ModelStage 5→ Parallel Task DAGStage 6→ 真正 devflow-exec --task→ 獨立 worktree→ Haiku Worker→ RED→ GREEN→ Verify→ Candidate→ Mechanical Gate→ Integration DAG→ Wave／Dedicated Review→ ACCEPTEDObservability→ 真正 Run／Attempt／Review events→ Prompt Version→ derive→ statsFinal Fresh Gauntlet→ 清 stale→ 綁 source SHA→ Required layers passStage 7→ Evidence→ Operational Walkthrough→ Standards Review→ Spec Review→ G3
自動測試中的 Human fixture 必須明確標示：
test-only human fixture
正式 Runtime 必須拒絕 Agent 自己產生的 ACCEPTED。
另外做一個負向 E2E：
Stage 3 trigger = trueHuman verdict = NOT_REVIEWED→ G2 必須拒絕
再做：
Fast lane + Risk high→ 必須拒絕或升 Full
以及：
Required layer = unverified→ G3 必須拒絕
以及：
上游 Candidate 被替換→ 下游 Candidate INVALIDATED_BY_UPSTREAM

# 十三、Fresh Review
派兩位 fresh-context Reviewer。
## Reviewer 1：Standards／Architecture
檢查：
單一正本。
Runtime／方法論一致。
向後相容。
worktree safety。
guard fail-closed。
schema migration。
security／privacy。
maintainability。
contract version handshake。
## Reviewer 2：Spec／Owner Decisions
逐項檢查：
OC-1～OC-6。
六項設計修正。
19 項 Plugin Runtime 待辦。
真正 E2E。
負向案例。
不可出現第二套流程。
文件沒有高於 Runtime 能力。
Reviewer 不得先讀 Worker 自評。
每個 finding 必須附：
requirementfile / lineevidenceseverityreturn_to
所有 finding 退回原 Workstream。

# 十四、完成條件
只有全部成立，才能將狀態改成：
DESIGN_PASSREFERENCE_PASSRUNTIME_PASSE2E_PASS
完成清單：
[ ] Plugin 未合併 branch 已安全處理[ ] OC-1 已進 G3 正本與 Plugin consistency[ ] OC-2A 已進 G2[ ] OC-2B 使用 trigger 條件[ ] OC-3 Wave Base 已實作[ ] OC-4 Fast／Full 已實作[ ] OC-5 Retention 已實作[ ] OC-6 Parallel 圖已完成[ ] Feature Risk／Task Risk 已分離[ ] Demo／Variant 規則已分離[ ] Task tags 受控[ ] result alias 有移除計畫[ ] Coverage 語意已修正[ ] Ledger field-level limits 已實作[ ] Contract version handshake 已實作[ ] Plugin Runtime tests 全綠[ ] Methodology tests 全綠[ ] Renderer fixed point 全綠[ ] 真正 /dev-flow E2E PASS[ ] 負向 E2E 全部正確拒絕[ ] 雙 fresh reviewer APPROVE[ ] 沒有 /Users/... 絕對路徑[ ] 沒有未提交變更

# 十五、Push 規則
完成後：
不得自行 push。
保留 methodology 與 Plugin integration branch。
提供 final SHA。
提供所有測試原始輸出摘要。
提供待 push 的 commits。
提供 rollback 方法。
等待使用者明示 push。

# 十六、最終報告格式
# DevFlow VNext Runtime 最終報告## Repository State### Methodology- Path:- Base SHA:- Final SHA:- Branch:- Dirty:### Plugin- Path:- Base SHA:- Final SHA:- Branch:- Dirty:## Owner Decisions| Owner Call | Decision | Runtime Evidence | Status ||---|---|---|---|## Capability Matrix| Capability | Design | Reference | Runtime | E2E ||---|---|---|---|---|## Plugin Workstreams| Workstream | Branch | Commits | Tests | Verdict ||---|---|---|---|---|## Contract Version- Methodology:- Runtime:- Schema:- Doctor result:## E2E- Positive scenario:- Negative scenarios:- Raw commands:- Results:## Reviewer Findings### Standards- ### Spec- ## Fixed Decisions- ## Known Limitations- ## Rollback- ## Push Readiness- READY | NOT READY## Unpushed Commits- 
不要用「測試很多、應該沒問題」作結論。
最終必須明確回答：
方法論是否完成？參考契約是否完成？Plugin Runtime 是否完成？真實 E2E 是否完成？現在是否可以安全 push？

---

# Part 2:補充執行決策(衝突時以本部為準)

# 補充執行決策：Push、Plugin 開工順序、清理與需求正本
## 一、遠端 Push 策略
目前方法論 repository 的本地 main 含 VNext 方法論與參考契約，但真正 Plugin Runtime 尚未完成。
不得直接將目前本地 main 推送至 origin/main。
「後續修改 Owner Call 會需要 force push」不是正確理由；後續決策可以使用正常的新 commit。暫緩更新 origin/main 的真正原因是避免遠端穩定分支宣告尚未存在的 Runtime 能力。
### 1.1 建立本地安全快照
SNAPSHOT_SHA="$(git rev-parse HEAD)"SNAPSHOT_NAME="devflow-vnext/methodology-snapshot"BACKUP_NAME="backup/devflow-vnext-before-runtime-$(date +%Y%m%d-%H%M%S)"git branch "$SNAPSHOT_NAME" "$SNAPSHOT_SHA"git branch "$BACKUP_NAME" "$SNAPSHOT_SHA"
若名稱已存在：
比較 SHA。
不得覆蓋。
使用帶時間戳的新名稱。
### 1.2 遠端備份方案
未取得使用者明示前，不得 push。
取得使用者允許備份、但尚未允許更新 main 時，只能推送：
git push origin devflow-vnext/methodology-snapshot
可選擇建立 annotated tag：
git tag -a devflow-vnext-methodology-20260802 "$SNAPSHOT_SHA" \  -m "DevFlow VNext methodology and reference contracts before runtime integration"git push origin devflow-vnext-methodology-20260802
不得在 Runtime／E2E 完成前更新 origin/main。
### 1.3 origin/main 更新條件
只有下列條件全部成立，才能回報 main 為 push-ready：
Plugin Runtime = RUNTIME_PASS真實 /dev-flow E2E = E2E_PASSOC-1～OC-6 已落地Gate consistency 通過Contract version handshake 通過雙 fresh reviewer APPROVE方法論與 Plugin 沒有能力斷層
即使全部成立，也不得自行 push；等待使用者明示。

## 二、Plugin 未合併 Branch 的處置與開工順序
### 2.1 先檢查未合併 branch
特別檢查：
codex/dev-flow-methodology-corrections
執行：
git log --oneline --decorate \  master..codex/dev-flow-methodology-correctionsgit diff --stat \  master...codex/dev-flow-methodology-correctionsgit diff \  master...codex/dev-flow-methodology-corrections
若預設 branch 不是 master，使用實際預設 branch。
產出：
notes/change-manifests/plugin-unmerged-branch-audit.md
必須逐 commit 分類：
already presentstill requiredobsoleteconflicts with VNextunknown
Agent 不得自行丟棄 unknown commit。
需要 Owner 決定時，只阻塞受影響部分；不得偷偷選擇 merge 或 delete。
### 2.2 建立 Plugin 備份
git branch \  backup/plugin-before-vnext-$(date +%Y%m%d-%H%M%S) \  HEAD
不得在髒工作樹建立正式 VNext branch。
### 2.3 最佳實作順序
不要先完整實作 gate-consistency，再去實作 A／B／C／D。
採以下順序：
#### Phase 0：Audit
處理未合併 branch。
找出 Runtime 正本與 generated files。
記錄 Plugin Base SHA。
#### Phase 1：固定共享契約
先確定但不完整實作：
DevFlow contract versionG2 正式條件G3 正式條件Feature Risk / Task Risk rubricEvent schemaCapability namesEvidence status
這一階段目的是避免四個 Worker 使用不同詞彙與 schema。
#### Phase 2：四個 Workstream 並行
P1 ExecutionP2 OperationalP3 ObservabilityP4 Gauntlet
四者使用獨立 worktree。
#### Phase 3：Gate consistency
待 P1～P4 語意與 Runtime 合流後，才完成：
G2 consistencyG3 consistencymethodology/runtime capability consistencyschema consistency
#### Phase 4：真實 E2E
使用真正 Plugin 執行端到端正向與負向案例。

## 三、舊 Methodology Worktree／Branch 清理
### 3.1 清理前檢查
每個 worktree 都必須執行：
git -C <worktree> status --shortgit merge-base --is-ancestor <branch> main
只有在：
status 為空branch 已 mergemanifest 已保存測試結果已保存無重要 untracked files
時，才可以移除。
### 3.2 Worktree
符合條件後可立即移除，不必等 push：
git worktree remove ../dev-flow-wt-executiongit worktree remove ../dev-flow-wt-operationalgit worktree remove ../dev-flow-wt-observabilitygit worktree remove ../dev-flow-wt-gauntletgit worktree remove ../dev-flow-wt-integrationgit worktree prune
路徑不存在或有未提交內容時不得使用 --force。
### 3.3 Branch
保留：
devflow-vnext/integrationdevflow-vnext/methodology-snapshotbackup/devflow-vnext-before-runtime-*
四個已合併 Worker branch，在確認為 main ancestor 後可刪：
git branch -d devflow-vnext/executiongit branch -d devflow-vnext/operationalgit branch -d devflow-vnext/observabilitygit branch -d devflow-vnext/gauntlet
不得使用 -D。
Plugin 新建立的 worktree／branch 則保留到 Plugin Runtime 與 E2E 完成。

## 四、Untracked Files
### 4.1 .serena/
.serena/ 是本機 MCP／專案快取，不得進 Git。
先檢查：
git ls-files .serena
如果沒有 tracked files，在 .gitignore 新增：
.serena/
若已有 tracked files：
git rm -r --cached .serena
只移除 Git index，不得刪除使用者本機快取目錄。
新增測試或檢查，避免 .serena/ 再進版本庫。
### 4.2 需求 DOCX 與 Markdown
不得讓 DOCX 和 Markdown 同時成為需求正本。
正式正本使用：
docs/prompts/devflow-vnext-runtime.md
要求：
將本次完整 Prompt 轉為 Markdown。
保留穩定 heading。
所有 manifest 改引用 Markdown heading／anchor。
後續決策與修改只更新 Markdown。
Git diff／review 以 Markdown 為準。
DOCX 預設不進 Git。
確實需要保存原始輸入時，可存：
docs/source-artifacts/DevFlow-vnext-prompt.docx
但檔案旁與 Markdown 頁首都必須寫：
This DOCX is a historical input snapshot.It is not the maintained source of truth.The canonical specification is:docs/prompts/devflow-vnext-runtime.md
大型 DOCX 使用 Git LFS；沒有保存需求時不要提交。

## 五、更新 ID-1～ID-12 狀態
不要重寫舊決策歷史。
在每個已被 Owner Call 取代的決策加：
- Status: superseded- Superseded by:- Effective date:- Replacement:
更新如下：
ID-1 → superseded by OC-2BID-2 → superseded by OC-1ID-3 → refined：Feature Risk／Task Risk 分 scopeID-4 → refined：受控 task_tagsID-5 → accepted with feature/wave/candidate Base semanticsID-6 → acceptedID-7 → resolved by OC-5ID-8 → acceptedID-9 → refined：保留 sequential 圖，新增 parallel 圖ID-10 → refined：result 只留到 schema 1.xID-11 → acceptedID-12 → superseded by OC-1／OC-2
新增一個 Current Decisions 區塊，列出目前有效規則。
歷史區回答「當時為何這樣決定」；Current Decisions 回答「現在真正生效的是什麼」。兩者不得混用。
