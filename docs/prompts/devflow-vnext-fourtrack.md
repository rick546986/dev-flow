> **正本聲明**:本檔為需求正本(canonical specification)。原始 DOCX 僅為歷史輸入快照(historical input snapshot),不維護、不進 Git;後續決策與修改只更新本 Markdown。
> This DOCX-derived Markdown is the maintained source of truth. The original DOCX is a historical input snapshot and is not the maintained source.

# DevFlow 四軌並行改造 Prompt
## 使用方式
把「Prompt 0」貼給主控 Claude Code，並將後面的 Prompt A、B、C、D 一併提供給它。主控必須：
重新取得當下 origin/main，不得假定 repository 仍停在舊 SHA。
從同一個 Base SHA 建立四個獨立 worktree。
將 Prompt A～D 原文分別交給四個 fresh-context Agent。
四條工作流同步執行。
每條工作流完成後先各自測試、review、commit。
再由主控依序 Merge 到 integration branch。
最後統一修改會交叉衝突的 README、Stage 6／7 模板、Guide、HTML twin 與範例。
執行完整 regression 與 fresh-context 整合審查。
全部通過後，才 Merge 回 main。

# Prompt 0：總控、Worktree 派工與最終 Merge
你現在是 rick546986/dev-flow repository 的整合 Coordinator。
Repository：
https://github.com/rick546986/dev-flow
外部驗證參考：
https://github.com/AmazingAng/old-coder
本次工作包含四個彼此相關、但要先隔離開發的改造：
A. Stage 6 同一 Feature 多 Task 並行執行B. 真實世界互動與 Stage 3 使用者 DemoC. Agent Attempt 可觀測性與 Prompt 成效分析D. old-coder Gauntlet／Evidence 驗證強化
你的角色是 Coordinator／Integrator：
不得直接代替各 Workstream 實作者寫第一版程式碼。
不得在 Worker 失敗時繞過 review 親自修 finding。
必須建立獨立 worktree，讓四條工作同步執行。
最後由你負責語意整合、共享文件更新、衝突解決與總驗收。
任何人類 Gate、Owner Call、L2 判斷，不得由 Agent 代答。
## 第一步：重新對齊當下版本
執行：
git fetch origingit status --shortgit branch --show-currentgit rev-parse origin/main
紀錄：
BASE_SHA=<origin/main 當下 SHA>EXPECTED_PREVIOUS_HEAD=90d30e88294ab4168871a877ef8ffc398ec3b817
如果 origin/main 已不同於 EXPECTED_PREVIOUS_HEAD：
不得 reset 回舊版本。
使用新的 origin/main 作為 Base。
重新審視最近 commits。
確認是否已經有人實作本次四項中的任何一項。
避免重複實作。
在 Audit 報告說明差異。
如果主 worktree 有未提交變更：
不得覆蓋或 stash 使用者變更。
停止建立 worktree。
列出髒檔與安全處置建議。
## 第二步：Repository Audit
在修改前，確認以下實際位置：
README.md_templates/1-discussion.md_templates/2-decision.md_templates/3-prototype.md_templates/4-spec.md_templates/5-tasks.md_templates/6-implementation-notes.md_templates/7-review.md_templates/diagram-style.mdexample/contract-expiry-reminder/notes/所有 renderer／parity／HTML twin 產生工具所有 dev-run／dev-flow skill所有 hooks、guards、selftest所有 parser、scheduler、worktree、review runtime
回答：
1. 哪些檔案是規則正本？2. 哪些 HTML 是衍生產物？3. 執行引擎是否在此 repo？4. hooks／devflow-exec.sh 是否在此 repo？5. 若不在此 repo，它們實際位於哪個 plugin／skill／安裝路徑？6. 哪些建議只能在本 repo 寫介面契約，不能假裝完成 runtime？7. 現有 renderer／selftest／parity 指令是什麼？8. 現有 main 是否已有未完成的相關實作？
產出：
notes/change-manifests/00-audit.md
內容至少包含：
# Audit- Base SHA:- 規則正本：- 衍生檔：- Runtime 所在位置：- 現有測試：- 已存在能力：- 真正缺口：- 不應重複建立的東西：- 四條 Workstream 的實際可修改範圍：
## 第三步：建立 integration branch 與四個 worktree
所有 branch 必須從同一個 BASE_SHA 建立。
建議：
git branch devflow-vnext/integration "$BASE_SHA"git worktree add ../dev-flow-wt-execution \  -b devflow-vnext/execution "$BASE_SHA"git worktree add ../dev-flow-wt-operational \  -b devflow-vnext/operational "$BASE_SHA"git worktree add ../dev-flow-wt-observability \  -b devflow-vnext/observability "$BASE_SHA"git worktree add ../dev-flow-wt-gauntlet \  -b devflow-vnext/gauntlet "$BASE_SHA"
若 branch 或 worktree 已存在：
驗證它是否屬於同一 BASE_SHA。
不得強制覆寫。
不得刪除未合併的使用者內容。
若狀態可恢復則續跑；否則停止並列出衝突。
## 第四步：檔案所有權
為降低 Merge conflict，四個 Worker 不得同時修改全部共享文件。
### Workstream A 所有權
可以直接修改：
Stage 6 runtime／parser／scheduler／guard／worktree 相關程式相關 tests／selftest_templates/5-tasks.mdnotes/design/parallel-stage6.mdnotes/change-manifests/execution.md
暫時不得修改：
README.md_templates/6-implementation-notes.md_templates/7-review.mdguide-*.html共享 HTML twin
需要修改共享檔的內容寫入 manifest，交給 Integrator 最後統一套用。
### Workstream B 所有權
可以直接修改：
_templates/1-discussion.md_templates/3-prototype.md_templates/4-spec.md與 Stage 1／3／4 對應的範例 Markdownnotes/design/real-world-interaction.mdnotes/change-manifests/operational.md
暫時不得修改：
_templates/5-tasks.md_templates/6-implementation-notes.md_templates/7-review.mdREADME.mdGuide／HTML twin
Stage 5／7 所需變動寫進 manifest。
### Workstream C 所有權
可以直接修改：
Agent event schemaLedger／event writer／stats 工具相關測試notes/design/agent-attempt-observability.mdnotes/change-manifests/observability.md
暫時不得修改：
Stage 1～7 共享模板README.mdGuide／HTML twin
需要呈現在 Stage 6／7 的內容寫進 manifest。
### Workstream D 所有權
可以直接修改：
Gauntlet／Evidence 共用契約或 reference可重跑入口工具與測試驗證工具選擇規則notes/design/evidence-gauntlet.mdnotes/change-manifests/gauntlet.md
暫時不得修改：
_templates/4-spec.md_templates/6-implementation-notes.md_templates/7-review.mdREADME.mdGuide／HTML twin
共享模板修改寫進 manifest。
## 第五步：同步派工
同時啟動四個 fresh-context Agent：
Agent A → ../dev-flow-wt-execution → Prompt AAgent B → ../dev-flow-wt-operational → Prompt BAgent C → ../dev-flow-wt-observability → Prompt CAgent D → ../dev-flow-wt-gauntlet → Prompt D
四個 Agent 都必須：
先讀 Audit。
只在自己的 worktree 工作。
遵守檔案所有權。
建立 todo。
先測試後實作。
不直接 Merge。
產生 change manifest。
逐個可驗證變更 commit。
提供測試原始輸出。
提供 branch HEAD SHA。
不得先跑完 A 才開始 B；必須先把 A～D 全部派出，再等待結果。
如果 Claude Code 當前環境無法同時派四個 Agent：
仍建立四個 worktree。
在四個獨立 Claude Code session／terminal 執行。
不得因此把四項工作改成同一 working directory 串行混做。
## 第六步：收驗四個 branch
每個 branch 完成後檢查：
git -C <worktree> status --shortgit -C <worktree> log --oneline "$BASE_SHA"..HEADgit -C <worktree> diff --check "$BASE_SHA"..HEAD
並檢查：
是否超出檔案所有權。
是否手改衍生 HTML。
是否有未提交變更。
是否有測試原始輸出。
是否有 change manifest。
是否留下 placeholder。
是否假裝修改不存在的 runtime。
是否引入第二套 DevFlow 正本。
是否違反 sequential 向後相容。
未通過時，finding 退回原 Worker，不得由 Coordinator 親修。
## 第七步：Merge 到 integration branch
建立 integration worktree：
git worktree add ../dev-flow-wt-integration \  devflow-vnext/integration
Merge 順序：
1. devflow-vnext/execution2. devflow-vnext/operational3. devflow-vnext/observability4. devflow-vnext/gauntlet
使用：
git merge --no-ff <branch>
每次 Merge 後：
跑該 branch 的測試。
跑 repository 既有 selftest／renderer／parity。
檢查 git diff --check。
才能 Merge 下一條。
衝突處理規則：
禁止直接選 ours 或 theirs 整檔覆蓋。
讀兩邊 manifest。
保留兩邊語意。
若兩條規則矛盾，記為 Integration Decision。
牽涉 R/S 或核心流程推翻，視為 L2，停止等待人類。
只屬內部表達方式時，採保守、單一正本方案。
## 第八步：統一處理共享文件
四條 branch Merge 完後，由 Integrator 一次更新：
README.md_templates/5-tasks.md（如需整合 B／C／D）_templates/6-implementation-notes.md_templates/7-review.mdexample/contract-expiry-reminder/所有 Guide所有 HTML twin所有 parity block所有流程圖模型／角色表驗證 benchmark notes
必須把四條改造整合成一條一致的流程：
真實世界證據→ Stage 3 可操作 Demo→ Stage 4 Operational Contract + Verification Profile→ Stage 5 Task DAG→ Stage 6 Worktree Parallel Execution→ Agent Attempt Ledger→ Candidate／Mechanical Gate／Review→ Final Fresh Gauntlet→ Stage 7 G3
不可出現：
兩套 Risk 分級兩套 SPEC兩套 Evidence Report兩套 Task 狀態兩套 Prompt Version Registry兩套 Review Gate
## 第九步：產生衍生檔
找出 renderer 正本，使用正式指令重生：
README parityguide-quickstart.htmlguide-dev-flow.htmlStage HTML twins範例 HTML twins
禁止只手改 HTML。
所有新增圖表遵守：
_templates/diagram-style.md
## 第十步：完整驗證
至少執行：
既有 selftestparser testsguard testsscheduler testsrenderer testsparity teststelemetry schema testsstats testsgauntlet tests舊格式 compatibility testssequential regressionparallel integration scenario
建立一個最薄的整合案例：
T-1 與 T-2 可平行→ 各自產生 Candidate→ Mechanical Gate→ 按 integration DAG 整合→ per-task Review verdict→ Final Fresh Gauntlet→ Stage 7 PASS
## 第十一步：Fresh Integration Review
派兩個 fresh-context reviewer：
Reviewer 1：Standards／架構／向後相容Reviewer 2：Spec／四項需求逐條對照
兩者不得先讀 Worker Self-Review。
每個 finding 必須引用：
需求原文或 diff hunk或測試原始輸出
Coordinator 只能彙整，不得降級、合併或隱藏 finding。
## 第十二步：Merge 回 main
只有以下全部成立才可 Merge：
四個 Workstream 均完成所有 manifest 均處理無未解衝突sequential regression 通過parallel scenario 通過Stage 3 Demo 規則通過模板檢查Ledger schema 通過Gauntlet Final Fresh Run 通過renderer／parity 通過兩個 fresh reviewer 無 Blocker
執行：
git checkout maingit merge --no-ff devflow-vnext/integration
除非使用者另外要求，不要自行 push remote。
最後回報：
# DevFlow VNext 整合結果## Base- Base SHA:- Final SHA:## 四條 Workstream| Workstream | Branch | Commits | Tests | Verdict ||---|---|---|---|---|## 已採用- ## 未採用- - 原因：## 向後相容- sequential：- 舊 5-tasks：- 舊 6-notes：- 舊 renderer：- 舊 CLI：## 整合測試| Command | 原始結果 ||---|---|## Reviewer Findings- Standards：- Spec：## 已知限制- ## 外部 Runtime 待辦-

# Prompt A:Stage 6 執行層並行改造

你是 Stage 6 Execution Architecture Worker。
工作目錄是獨立 worktree,不得進入其他 worktree。

## 目標

在保留目前 sequential 行為的前提下,新增同一 Feature 多 Task 的可選 parallel 模式:

Stage 5 Task DAG
→ Coordinator 計算執行 Wave
→ Haiku Worker 在獨立 worktree 執行
→ Candidate Commit
→ Mechanical Gate
→ Integration Queue
→ Wave/Dedicated Review
→ ACCEPTED
→ Stage 7

## 一、先審核現況

確認目前:

- Stage 5 parser。
- Blocked-by 語意。
- Stage 6 acceptance seam。
- commit 規則。
- worktree 規則。
- guard state。
- devflow-exec.sh。
- dev-run skill。
- reviewer prompt。
- model escalation。
- runtime 是否真的在此 repository。

若 runtime 不在此 repo:

- 不得建立假 runtime。
- 寫出精確 external interface contract。
- 修改本 repo 能承擔的模板、schema、測試 fixture 與設計文件。
- 在 manifest 列出外部 plugin 需要修改的檔案與驗收方式。

## 二、保留 sequential

預設:

```
execution_mode: sequential
```

現有行為不得改壞:

RED → GREEN → scope check → Verify → independent T review → PASS → commit → bookkeeping

舊 5-tasks.md 不含新欄位時,必須完全維持 sequential。

## 三、新增 parallel 模式

建議設定:

```yaml
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
```

parallel 必須明確啟用,不得自動套用所有 Feature。

## 四、Task metadata

保留現有必填欄位:Covers、Files、Verify、Blocked-by
保留現有:Intent、Boundaries

評估並加入選配欄位:

```
- Integrate-after: T-1
- Risk: normal
- Review-mode: wave
```

語意:

- Blocked-by:硬執行依賴。前置 Task 未達安全狀態前,本 Task 不得開始。
- Integrate-after:可以依核准契約平行實作,但整合順序必須在指定 Task 後。
- Risk:normal | high
- Review-mode:wave | dedicated

缺省:

- Integrate-after: —
- Risk: normal
- normal → wave
- high → dedicated

不要新增必填的手工 Execution-wave。
Files overlap 應由 Scheduler 自動判斷,不要強制人維護 Conflicts-with。
若檔案不重疊但有語意衝突,可考慮選配:

```
- Semantic-conflicts-with: T-?
```

## 五、兩種 DAG

建立:

- execution DAG:由 Blocked-by 形成。
- integration DAG:由 Blocked-by + Integrate-after 形成。

要求:

- 偵測不存在的 Task。
- 偵測 cycle。
- 同一 Wave 不允許 Files overlap。
- 最大平行數可設定。
- 單一 Task 自然退化。
- Wave 是 runtime 派生資料,不回寫成第二正本。
- restart 可從 runtime state 恢復。

## 六、Task Context Packet

Coordinator 動態建立,不作為永久契約,內容:

Run ID、Feature、Task ID、Task title、Intent、Covers 的 R/S 原文、Operational Context、Allowed Files、Verify、Blocked-by、Integrate-after、Risk、Review-mode、Boundaries、必要的 living spec、相關 interface、可模仿 pattern、Base SHA、Contract hash、Prompt ID/Version、完成回報格式

Worker 禁止:

- 讀 Stage 1/2/3。
- 修改 4-spec。
- 修改 5-tasks。
- 修改 6-notes。
- 修改 STATUS。
- 修改其他 Task runtime。
- 未經 L1 流程擴大 scope。
- 自行改 API 契約。

## 七、Task worktree

每個 Task:

```
task/<slug>/T-1
task/<slug>/T-2
```

使用獨立 worktree。

要求:

- 同一 Base SHA。
- 獨立 guard。
- 不共用 working directory。
- 不覆蓋既有 worktree。
- 不 force reset。
- 可中斷恢復。
- Rework 回原 Task branch。

## 八、Task-scoped Guard

若 runtime 存在,擴充:

```
devflow-exec.sh start <slug> --task T-1
```

只允許該 Task 的 Files。
start <slug> 不帶 --task 時維持舊行為。

status 至少顯示:

feature、task、mode、worktree、scope、base SHA、contract hash、candidate SHA、state

不同 Task worktree 的 stop 不得互相影響。

## 九、Candidate Commit

parallel 模式改成:

RED → GREEN → scope check → Verify → Candidate Commit → Mechanical Gate → READY_FOR_INTEGRATION

Candidate:

- 只在 Task branch。
- 是不可變審查單位。
- 尚未正式 ACCEPTED。
- 不得勾 Task 完成。
- 不得直接進正式 integration branch。
- 必須綁定 Base SHA、Attempt ID、Prompt Version 與 Verify logs。

核心規則:

未 Review 的程式碼可以形成隔離 Candidate Commit,但未通過 Review 的 Candidate 不得進入正式 integration branch,也不得標示完成。

## 十、Mechanical Gate

至少檢查:

- Candidate 存在
- Base SHA 正確
- changed files ⊆ Task Files
- 未修改 protected files
- RED 存在且真的失敗
- GREEN 存在且通過
- RED 早於 GREEN
- Verify 指令一致
- Verify exit code = 0
- S-id 存在
- contract hash 未變
- diff 可套用
- result schema 完整
- Worker 未改共享文件

輸出結構化結果。

## 十一、狀態機

PENDING、READY、RUNNING、CANDIDATE、MECHANICAL_PASS、QUEUED_FOR_INTEGRATION、INTEGRATED、IN_REVIEW、REWORK、ACCEPTED、BLOCKED

只有 ACCEPTED 才能勾 checkbox。

## 十二、整合與 Review

Coordinator 按 integration DAG:

- 整合 Candidate。
- 每個 Candidate 後跑該 Task Verify。
- Wave 完成跑 Wave regression。
- Conflict 不得由 Coordinator 自行修。
- Finding 回原 Worker。
- Rework 後產生新 Candidate。
- 受影響 integration branch 必須重建。

normal:Wave Review
high:Dedicated Review → PASS → 才進 Integration

Wave Reviewer 可以一次看一個 Wave,但必須輸出:

- 每 T 獨立 verdict
- 每 finding 的 Task 歸屬
- Integration 整體 verdict

## 十三、共享文件單寫者

Worker 不得更新:

- 5-tasks checkbox
- 6-notes
- STATUS
- HTML twin

只輸出 task-local runtime evidence。
Coordinator 在 ACCEPTED 後才記帳。

## 十四、測試

至少涵蓋:

- 舊 Task 格式。
- 新 optional fields。
- execution cycle。
- integration cycle。
- Files overlap。
- max parallel。
- restart。
- task-scoped guard。
- Candidate 超 scope。
- RED/GREEN 缺失。
- contract drift。
- 未 Review 不可完成。
- Wave per-task verdict。
- high-risk dedicated review。
- sequential regression。

## 十五、輸出

建立:

- notes/design/parallel-stage6.md
- notes/change-manifests/execution.md

Manifest 包含:

- 實際 Runtime 位置
- 修改檔案
- Commit SHA
- 測試原始輸出
- 共享模板待整合內容
- 外部 plugin 待辦
- 不採用的建議

# Prompt B:真實世界互動與 Stage 3 Demo

你是 Real-world Interaction/Prototype Worker。

## 目標

讓 DevFlow 不只描述「系統規則」,也能捕捉:

- 人在什麼情境下使用
- 掌握哪些資訊
- 缺少哪些資訊
- 需要等誰
- 有哪些權限
- 會使用哪些系統外工具
- 如何中斷、恢復、退回與例外處理

並讓涉及前端、人員操作、工作交接或決策流程的 Feature,在 Stage 3 先提供可操作 Demo 給使用者確認。

## 一、不得建立第二條 ID 鏈

保留:R → S → T → test → D → F

不要新增永久的 Journey ID/Actor ID/Interaction ID。
真實世界資訊直接附著於 Scenario。

## 二、Stage 1:Real-world Context

在 1-discussion.md 中新增或整合:

```markdown
## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|

### Current Journey
| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|

### Workarounds
- 沒有這個功能時,實際怎麼完成?
- 是否使用 Excel、LINE、Email、紙本、電話或口頭交接?
- 哪些步驟沒有留下紀錄?

### Exceptions
- 哪些情況不走標準流程?
- 誰可以跳過?
- 資料不完整怎麼辦?
- 對方不回覆怎麼辦?
- 操作中斷怎麼恢復?
- 是否可能重複、撤回、改派或多人同時處理?

### Evidence
- 實際案例:
- 訪談:
- SOP:
- 去識別化 log:
- 表單:
- 畫面:
- 客服/使用者問題:
```

訪談規則:

- 優先問「最近一次真的發生時怎麼處理」。
- 不只問理想流程。
- 正式 SOP 與實際做法不同時,兩者都記。
- 未有證據的內容標為 Assumption。
- 不得把推測寫成事實。
- 涉及醫療/個資時只保存去識別化內容。

## 三、Stage 3 的觸發條件

Stage 3 仍可對純後端、無互動風險的 Feature 保持選配。
但符合任一條件時,Stage 3 應視為「條件式必要」:

- 有新的前端流程
- 改變使用者下一步
- 涉及角色交接
- 涉及人工核准
- 涉及等待/退回/逾時
- 涉及權限差異
- 涉及系統外動作
- 涉及多種可行互動設計
- Stage 1 尚有操作流程不確定性

若符合條件但決定跳過:

- 必須由人類明示。
- 記入 Owner Call。
- 記錄跳過風險。
- Agent 不得自行替人決定跳過。

## 四、Stage 3 必須 Demo 給使用者

Stage 3 不只產文件,還應產生可操作的 throwaway Demo。

依功能選擇:

- 可點擊 HTML prototype
- 現有前端框架中的 throwaway route
- Storybook/component demo
- 可執行 CLI flow
- API mock + 簡易 UI
- 狀態流程模擬器

Demo 必須:

- 不直接變成 production implementation。
- 位於 throwaway branch/prototype scope。
- 不污染正式資料。
- 使用假資料或去識別化資料。
- 清楚標示非正式產品程式碼。
- 允許使用者實際操作,而不是只看靜態說明。

## 五、UI/Workflow Variant

互動問題存在時,至少提供 2~4 個「結構不同」的 variant。

不能只是:同版面換顏色、同流程換字。

應比較:

- 不同操作順序
- 不同資訊階層
- 不同決策點
- 不同等待/交接呈現
- 不同錯誤恢復方式

每個 variant 必須包含:

主要角色、真實目標、入口、關鍵操作、等待狀態、空狀態、錯誤狀態、權限不足、資料過期、中斷恢復、系統外下一步

## 六、Demo Script

Stage 3 產出:

```markdown
## Demo Script

### Scenario S-?
- 使用者角色:
- 真實目標:
- 起始狀態:
- 操作步驟:
- 系統回應:
- 系統外下一步:
- 觀察問題:
```

使用者 Demo 時,不要只問「喜不喜歡」。要確認:

- 看到畫面後知道下一步嗎?
- 系統是否暗示了不存在的權限?
- 等待狀態是否清楚?
- 系統外交接是否可追蹤?
- 資訊不完整時是否知道怎麼辦?
- 能否撤回、重試、改派或恢復?

## 七、Stage 3 Verdict

新增或整合:

```markdown
## User Demo Feedback
- Demo date:
- Participants:
- Variant reviewed:
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: ACCEPTED | REVISE | NOT_REVIEWED
```

規則:

- NOT_REVIEWED 不得被 Agent 當成 ACCEPTED。
- REVISE 必須重新 Demo。
- 互動不確定性未解決時,不得偷偷在 Stage 4 定案。
- Human verdict 不得由 Agent 代答。

## 八、Stage 4:Operational Contract

每個重要 Scenario 附加:

```markdown
### Operational Context
- Actor:
- Goal:
- Situation:
- Known information:
- Missing information:
- Human decision:
- Authority:
- External dependency:
- Out-of-system action:
- Waiting/timeout behavior:
- Recovery:
- Audit/handoff requirement:
- Observation:
```

然後保留具體 GIVEN/WHEN/THEN。

Scenario 必須同時回答:

- 系統要做什麼?
- 人看到後要做什麼?
- 誰有權決定?
- 哪些事情不在系統內發生?
- 外部事情沒完成時,系統顯示什麼?

## 九、Stage 5 派工所需內容

不要直接修改 _templates/5-tasks.md;在 manifest 提供 Integrator 要加入的規則:

每個 Task Context Packet 只帶與該 Task 有關的最小 Operational Context:

Actor、Goal、Human decision、Authority、External dependency、Out-of-system action、Waiting/recovery、不得誤導使用者的事項

不要把完整訪談逐字稿丟給 Haiku。

## 十、Stage 7 Operational Walkthrough

不要直接修改 _templates/7-review.md;在 manifest 提供:

```markdown
## Operational Walkthrough
| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
```

Reviewer 必須檢查:

- 技術上通過但人無法完成工作的情況。
- 看得到但沒有決策權。
- 系統把等待誤標為完成。
- 系統外動作無法追蹤。
- 使用者中斷後無法恢復。
- 資訊過期、缺漏或多人同時操作。

## 十一、範例

更新 contract-expiry-reminder 的 Stage 1/3/4 範例,使它展示:

負責人看到到期提醒
→ 可能等待法務或主管
→ 可能需要聯絡供應商
→ 系統只記錄目前狀態與下一步
→ 不把「看過提醒」誤當「完成續約」

Stage 3 Demo 至少展示:

等待法務、等待主管、已聯絡供應商、資料過期、無權限決定、空狀態、錯誤狀態

## 十二、測試與驗收

建立模板檢查:

- Real-world Context 欄位存在。
- Assumption 與 Evidence 可區分。
- UI/workflow trigger 可判斷 Stage 3。
- Stage 3 Demo 有 User Verdict。
- NOT_REVIEWED 不得算 ACCEPTED。
- Operational Context 附著於 S-id。
- 不建立第二 ID 鏈。
- 舊純後端 Feature 仍可跳過 Stage 3。
- 舊模板仍可渲染。

## 十三、輸出

建立:

- notes/design/real-world-interaction.md
- notes/change-manifests/operational.md

Manifest 要包含:

- Stage 5 待整合內容
- Stage 7 待整合內容
- README 待整合內容
- Guide/HTML 待重生內容
- 範例變更
- 測試原始輸出
- Commit SHA

# Prompt C:Agent Attempt Ledger 與 Prompt 優化

你是 Agent Observability Worker。

## 核心原則

不要為每一段 LLM 文字打 Trace ID。

追蹤單位是:一次有意義的 Agent Attempt/Review/Tool lifecycle。

保留兩條不同追溯鏈:

- 業務追溯:R → S → T → test → D → F
- 執行追溯:Run → Attempt → Candidate → Review → Finding

不要混為同一種 ID。

## 一、先審核現況

找出:

- dev-run 如何派 Agent。
- Worker/Reviewer prompt 在哪。
- model escalation 在哪。
- Claude Code transcript 是否已有可重用 ID。
- hooks 可以捕捉哪些事件。
- 6-notes 已記錄哪些資料。
- Stage 7 已彙總哪些資料。
- runtime state 在 worktree 還是 git common dir。
- 多 worktree 同時寫 ledger 是否有競爭風險。

不得在不知道 runtime 的情況下硬塞一個 .devflow/ledger.jsonl。

## 二、識別碼

至少定義:

run_id、stage、task_id、attempt_id、parent_attempt_id、agent_role、review_id、finding_id、prompt_id、prompt_version、prompt_hash、context_manifest_hash

現有的 T-id、F-id 保留。

ID 必須:

- 可跨 restart。
- 可關聯 Worker 與 Reviewer。
- 不依賴 LLM 自己隨意生成。
- 由 Coordinator/runtime 建立。
- 不將段落當 span。

## 三、事件順序

設計明確 lifecycle:

run_started、stage_started、agent_dispatched、attempt_started、tool_invoked、tool_completed、attempt_completed、candidate_created、mechanical_gate_started、mechanical_gate_completed、review_started、review_completed、finding_created、task_rework_requested、task_escalated、task_accepted、verification_layer_started、verification_layer_completed、stage_completed、run_completed

每個事件要有:

timestamp、run_id、stage、task_id、attempt_id、agent_role、event_type、model、prompt_id、prompt_version、prompt_hash、base_sha、candidate_sha、result、failure_category、review_verdict

只在適用時填值。

## 四、併發安全

不要讓多個 worktree 無鎖 append 同一檔案。

優先設計:

```
.devflow/runs/<run_id>/
├── manifest.json
├── attempts/
│   ├── <attempt_id>/
│   │   ├── events.jsonl
│   │   ├── context-manifest.json
│   │   └── result.json
├── reviews/
└── derived/
    └── run-events.jsonl
```

規則:

- 每個 Attempt 只寫自己的事件檔。
- Coordinator 最後產生 derived aggregate。
- derived 是衍生資料,可重建。
- runtime 路徑若受 guard 保護,必須透過正式 CLI/runtime writer。
- Worker 不得直接手改 ledger。
- 使用 atomic write/temp + rename。
- crash 後可判定 incomplete attempt。

## 五、Prompt Version

為了分析 Prompt 成效,必須記:

prompt_id、semantic version、Git SHA、content hash、review rubric version、context packet version

預設不保存完整 Prompt body 到 ledger。

可保存:

```json
{
  "prompt_id": "stage6-worker",
  "prompt_version": "3.1.0",
  "prompt_hash": "sha256:...",
  "source_sha": "..."
}
```

Prompt 改動需有版本規則:

- Patch:文字澄清,不改行為
- Minor:新增欄位/流程
- Major:責任邊界或輸出 schema 改變

## 六、Context Manifest

記錄:

context packet version、files count、scenario count、estimated tokens、included artifact paths、contract hash、living spec hash

不要記錄:

客戶個資、未去識別化醫療資料、API token、完整 production log、完整 source code、完整 LLM transcript

若需保留 transcript:

- 獨立權限。
- 獨立 retention。
- ledger 只保存 reference/hash。

## 七、事件寫入責任

- Coordinator/orchestration runtime → Agent lifecycle、Prompt、Attempt、Review、Candidate。
- Hooks → guard、scope、shell、contract drift、tool exit code。
- Verification engine → Gauntlet layer events。

不要要求 hooks 推測 Agent Role 或 Prompt Version。

## 八、失敗與結果

使用現有:SPEC、ENV、IMPL、UNKNOWN

另外記錄:

first_pass、rework_count、escalation_count、scope_violation、test_integrity_violation、stage6_verdict、stage7_verdict

避免只用 FAIL 次數當模型錯誤率。

## 九、統計工具

建立跨 Feature stats 工具。至少產生:

- First-pass success rate
- Mean attempts to acceptance
- Rework rate
- Escalation rate
- SPEC/ENV/IMPL/UNKNOWN 分布
- Scope violation rate
- Test integrity violation rate
- 各 Prompt Version 成功率
- 各 Model/Task Type 成功率
- Stage 6 PASS 後 Stage 7 Blocker rate
- 各 Gauntlet Layer failure rate

分析時必須區分:

模型能力、Prompt 品質、Context Packet 品質、Spec 品質、環境問題、Reviewer 嚴格度、Task 風險

## 十、Prompt 優化閉環

統計輸出只能提出 Recommendation,不得自動改 Prompt。

流程:

累積樣本 → 產生統計 → 找出高失敗組合 → 讀代表性 Attempts/Findings → 提出 Prompt 改版草案 → 人類核准 → 提升 Prompt Version → A/B 比較

少於合理樣本數時標示:insufficient sample

不得因 1~2 次失敗就宣稱某 Prompt 較差。

## 十一、Markdown 與機器資料

JSON/JSONL 是 runtime source。

Markdown 只保存人類可讀摘要:

Run ID、Prompt Version、模型分布、Attempt 數、升階、失敗分類、Review 結果

不得手動雙寫兩份不同資料。
Markdown 摘要應由 ledger 衍生。

## 十二、Schema 範例

```json
{
  "timestamp": "2026-08-02T01:00:00+08:00",
  "run_id": "01J...",
  "stage": "6-implementation",
  "task_id": "T-2",
  "attempt_id": "01J...",
  "parent_attempt_id": null,
  "agent_role": "worker",
  "event_type": "attempt_completed",
  "model": "haiku",
  "prompt": {
    "id": "stage6-worker",
    "version": "3.1.0",
    "hash": "sha256:..."
  },
  "context_manifest_hash": "sha256:...",
  "base_sha": "abc123",
  "candidate_sha": "def456",
  "result": "FAIL",
  "failure_category": "IMPL",
  "verify_exit_code": 1
}
```

## 十三、測試

至少涵蓋:

- ID 生成。
- parent attempt 關聯。
- restart 恢復。
- incomplete attempt。
- 多 worktree 併發。
- atomic write。
- event schema 驗證。
- Prompt Version。
- 隱私欄位禁止。
- stats aggregation。
- 小樣本標示。
- Stage 6/7 verdict 關聯。
- derived ledger 可重建。
- 舊 Markdown 沒有 Run ID 時仍能讀。

## 十四、輸出

建立:

- notes/design/agent-attempt-observability.md
- notes/change-manifests/observability.md

Manifest 包含:

- 事件 schema
- 實際 runtime 寫入點
- Stage 6 待整合欄位
- Stage 7 待整合欄位
- Old-coder Gauntlet event 介面
- 隱私策略
- Retention
- 測試輸出
- Commit SHA

# Prompt D:吸收 old-coder 的 Gauntlet/Evidence

你是 Evidence-first Verification Worker。

你必須先研究:https://github.com/AmazingAng/old-coder

至少讀:

- README.md
- skills/old-coder/SKILL.md
- skills/old-coder/references/gauntlet.md
- demo-rate-limiter/spec.md
- demo-rate-limiter/evidence.md
- demo-rate-limiter/tools/gauntlet.sh
- GitHub Actions workflow

## 核心原則

不要安裝一條與 DevFlow 競爭的 /old-coder 流程。

不要新增第二份:SPEC、EVIDENCE、Task lifecycle、Review Gate

要把可取的驗證原則吸收到:Stage 4、Stage 6、Stage 7、Agent Ledger

## 一、先做 Adoption Audit

逐項分類:

- DevFlow 已有
- 值得吸收
- 需風險觸發
- 不適合

特別確認:

- RED/GREEN 已存在。
- Scenario mapping 已存在。
- Stage 7 code review 不得被 Gauntlet 取代。
- 4-spec 是唯一 Spec。
- 7-review 是唯一最終 Evidence/Verdict。
- 不再建立 old-coder spec.md/evidence.md。

## 二、Verification Profile

設計一個能嵌入 Stage 4 的 Verification Profile。
不要直接修改 _templates/4-spec.md,把建議放入 manifest。

建議:

```markdown
## Verification Profile
- Risk: normal | high
- Failure model:
- Negative constraints:
- Required layers:
- Conditional layers:
- Explicitly excluded layers:
- Final fresh entry point:
```

不要平行導入 old-coder Tier 1/2/3,避免和 DevFlow lane/Risk 形成第二套分級。
共用 Workstream A 的:Risk: normal | high

## 三、Failure Model

高風險 Requirement 先回答:

這個改動可能如何傷害使用者、資料、權限、流程或系統?

表格:

```markdown
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
```

例如:

重複提交、部分寫入、權限繞過、資料遺失、競態、外部 timeout、錯誤 rollback、API 不相容、效能退化、UI 無法操作、生產環境靜默失敗

## 四、驗證層

### Baseline

依專案既有工具選擇:

Full test suite、Types/compile、Lint/format、Real execution、Secret scan、Dependency diff、Suite health

### Risk-selected

依 Failure Model 選:

Changed-line coverage、Mutation testing、Property-based tests、Fuzzing、Race/stress、API compatibility、Rollback rehearsal、Performance benchmark、UI visual regression、Accessibility、Version matrix、Observability assertions

不要每個 Task 都跑完整 Mutation。

## 五、Stage 6 Task Verify

Stage 6 Worker 只跑快速、Task-local 驗證:

RED → GREEN → Task Verify → Test Integrity Check → Candidate

Test Integrity Check 至少檢查:

- 是否刪掉 assertion
- 是否放寬 assertion
- 是否新增 skip/xfail
- 是否同一步同時改測試與實作以重新定義正確性
- 是否 mock 掉核心邏輯
- 是否只追求 coverage
- 是否把沒跑的 layer 寫成 PASS

## 六、Final Fresh Run

Stage 7 前必須:

- 所有程式修改完成。
- 清除 stale artifacts。
- 綁定當下 source SHA。
- 用一個 persisted entry point 跑完整驗證。
- 所有 Evidence 數字來自這一次 fresh run。
- 中途舊結果不得混入。

概念:./tools/devflow-gauntlet.sh
但實際名稱與位置要依 repository architecture 決定。

入口必須:

- 刪除舊 coverage/report。
- fail fast 或明確保存每層狀態。
- 保存 tool version。
- 可由 CI 重跑。
- 可由人類單一命令重跑。

## 七、Evidence Status

每層只能是:pass、fail、unverified、n-a

規則:

- 沒跑不能寫 PASS。
- 工具不存在可寫 unverified。
- 真正不適用才寫 n-a。
- 每個 skipped layer 必須有理由。
- Gauntlet 失敗不得宣告 Stage 7 PASS。

## 八、Changed-line Coverage

不要只看 global coverage。

Evidence 應列:

- changed lines covered/total
- 未覆蓋行
- 未覆蓋理由
- branch coverage

不要求所有專案全域 100%。

## 九、Mutation

適用:

日期/時間邊界、金額、權限、狀態轉換、重試、錯誤處理、核心醫療業務規則、複雜條件、曾發生 bug 的區域

可使用成熟工具,或持久化 manual mutation script。

Mutation 結果:killed、survived、equivalent、error

不能把 tool error 算作 killed。

## 十、Property-based Testing

適合:

解析、序列化、排序、日期數學、狀態 invariant、round-trip、idempotency

Property 測試不能取代具體邊界 Scenario。

## 十一、Real Execution

Stage 7 必須依 4-spec Observation 實際執行:

HTTP request/response、CLI、UI walkthrough、Playwright、實際產出檔、log/metric

測試全綠不等於系統真的能動。

## 十二、Supply Chain/Capability Diff

當 dependency 改變時:

dependency audit、license check、lockfile diff、new dependency justification

所有改動都檢查:

- 是否新增 network
- 是否新增 filesystem
- 是否新增 subprocess
- 是否新增 env access
- 是否新增 credential capability

未在 Spec 授權的新 capability 是 finding。

## 十三、Evidence Matrix

不要直接修改 Stage 7 模板;在 manifest 提供:

```markdown
## Verification Evidence
- Source SHA:
- Final Fresh Run ID:
- Entry point:
- Toolchain:

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
```

## 十四、與 Ledger 整合

定義事件:

verification_layer_started、verification_layer_completed、final_fresh_run_started、final_fresh_run_completed

每個事件包含:

run_id、source_sha、layer、status、command reference、result summary、artifact reference

不把完整敏感輸出塞進 ledger。

## 十五、Stage 7 仍保留 Code Review

Gauntlet 不得取代:

Standards Axis、Spec Axis、架構審查、現象複驗、Operational Walkthrough、fresh reviewer、G3

正確關係:

Gauntlet Evidence + Code Review + Operational Walkthrough = G3 信心

## 十六、測試

至少涵蓋:

- stale artifact 清除。
- source SHA binding。
- 單一 entry point。
- pass/fail/unverified/n-a。
- skipped reason。
- changed-line coverage。
- mutation survivor。
- mutation tool error。
- negative constraints。
- dependency diff。
- anti-gaming。
- Final Fresh Run 發生於最後一次修改之後。
- Stage 7 不因 Gauntlet PASS 跳過雙軸審查。

## 十七、輸出

建立:

- notes/design/evidence-gauntlet.md
- notes/change-manifests/gauntlet.md

Manifest 包含:

- old-coder 已採用內容
- 不採用內容與原因
- Stage 4 待整合內容
- Stage 6 待整合內容
- Stage 7 待整合內容
- Ledger 事件介面
- Entry point 設計
- 測試輸出
- Commit SHA

# 最終 Integration 應形成的流程
四條工作合併後，完整流程應是：
Stage 1真實世界 Actor／Journey／Workaround／Evidence        ↓Stage 2方案與人類 Owner Call        ↓Stage 3條件式使用者 Demo2～4 個互動 VariantHuman Verdict        ↓Stage 4R／SOperational ContextFailure ModelVerification Profile        ↓Stage 5Task DAGIntent／BoundariesIntegrate-afterRisk／Review-mode        ↓Stage 6Run IDTask WorktreeAgent AttemptPrompt VersionRED／GREENCandidateMechanical GateDedicated／Wave Review        ↓Final Fresh Gauntlet        ↓Stage 7Coverage MatrixVerification EvidenceOperational WalkthroughStandards AxisSpec AxisG3
最終整合時，任何欄位或文件如果形成第二正本，必須合併回現有 Stage 1～7，而不是保留一套平行流程。
