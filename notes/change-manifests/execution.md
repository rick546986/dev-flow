# Change Manifest — Workstream A(Stage 6 Execution Architecture)

> Branch:`devflow-vnext/execution`(base 90d30e88294ab4168871a877ef8ffc398ec3b817)
> Worktree:`/Users/asheng/dev/dev-flow-wt-execution`
> 日期:2026-08-02

## 1. 實際 Runtime 位置(audit 覆核一致)

**不在本 repo**。執行引擎全部住 `/Users/asheng/.claude/plugins/local/dev-flow/`
(獨立 git repo、master、無 remote):

- `hooks/devflow-exec.sh`(薄殼)+ `_exec_impl.py`(5-tasks parser :61-98、start/stop/status/allow)
- `hooks/_guard_impl.py`、`devflow-lib.py`、`_prebash_impl.py`、`_postbash_impl.py`、`hooks.json`、`selftest.sh`
- `skills/{dev-flow,dev-run,dev-setup}/SKILL.md`(scheduler/review 皆 prompt 層)

因此本 workstream 產出 = 模板欄位 + **精確 external interface contract**
(`notes/design/parallel-stage6.md`)+ 可執行契約與 fixtures(`tests/parallel-stage6/`)。
**未建立任何假 runtime**;runtime 行為變更全數列 §6 外部 plugin 待辦。

## 2. 修改/新增檔案(全部在本 worktree)

| 檔 | 動作 |
|---|---|
| `notes/design/parallel-stage6.md` | 新增:設計 + 介面契約(§0-§15) |
| `_templates/5-tasks.md` | 修改(additive):frontmatter `execution:` 區塊 + 頂註並行選配欄位文檔;必填四欄一字未動 |
| `tests/parallel-stage6/run_tests.py` | 新增:契約測試 runner(94 檢查) |
| `tests/parallel-stage6/contract_ref.py` | 新增:可執行契約(解析/DAG/wave/狀態機/gate/review schema) |
| `tests/parallel-stage6/fixtures/`(24 檔) | 新增:9 個 5-tasks md + 10 個 gate JSON + 4 個 wave-review JSON + 1 舊格式 |
| `scripts/check-parallel-stage6.sh` | 新增:檢查入口(獨立於 74 條基線腳本,additive) |
| `notes/change-manifests/execution.md` | 新增:本檔 |

未動:README.md、`_templates/6-implementation-notes.md`、`_templates/7-review.md`、
guide-*.html、example/、renderer/check 兩支既有腳本(74 條基線零修改)。

## 3. Commit SHA

| SHA | 內容 |
|---|---|
| `e85a1a6` | 設計 + external interface contract |
| `2d10093` | RED:契約測試層(fixtures + runner + check 入口)→ 14/24 |
| `e90fdc8` | GREEN:模板選配欄位 + contract_ref → 94/94;基線保綠 |
| (本檔 commit) | manifest |

## 4. 測試原始輸出

開工基線(worktree 內,@ 90d30e8):

```
✅ methodology correction checks: 74/74 passed
✅ renderer fixed point: 4/4 tracked outputs byte-identical
```

RED(@ 2d10093,`bash scripts/check-parallel-stage6.sh`):

```
⚠️  contract_ref 缺失,行為契約檢查全數未執行(RED)。
❌ parallel stage6 contract checks: 14/24 passed
  - 模板含選配 parallel 欄位/設定 'execution:'
  - 模板含選配 parallel 欄位/設定 'mode: sequential'
  - 模板含選配 parallel 欄位/設定 'max_parallel_tasks:'
  - 模板含選配 parallel 欄位/設定 'rebuild_integration_on_rework:'
  - 模板含選配 parallel 欄位/設定 'Integrate-after:'
  - 模板含選配 parallel 欄位/設定 'Risk:'
  - 模板含選配 parallel 欄位/設定 'Review-mode:'
  - 模板含選配 parallel 欄位/設定 'Semantic-conflicts-with:'
  - 模板明文 sequential 缺省 / parallel 須明確啟用
  - contract_ref.py 可載入(可執行契約存在): ModuleNotFoundError("No module named 'contract_ref'")
exit=1
```

GREEN(@ e90fdc8):

```
✅ parallel stage6 contract checks: 94/94 passed
✅ methodology correction checks: 74/74 passed
✅ renderer fixed point: 4/4 tracked outputs byte-identical
```

檢查總數說明:既有 74 + 4 不變;新增獨立腳本 `check-parallel-stage6.sh` = 94 條。

**Sequential 向後相容專屬證據**(94 條內):舊格式 fixture 零錯誤、缺省
mode=sequential、真檔 `example/contract-expiry-reminder/5-tasks.md` 解析零錯誤且落
sequential、sequential 模式 compute_waves 拒派生、必填四欄驗法與 runtime 相同。

## 5. 共享模板待整合內容(本 workstream 無權改,交 Integrator 統一套用)

### 5.1 README.md §5(新增一段,置於「守衛與並行」條目之後)

提案文字:

> - **T 級並行(選配,同一 feature 內)**:`5-tasks.md` frontmatter 明寫
>   `execution.mode: parallel` 才啟用(缺省 sequential,行為不變)。並行 seam 變體:
>   RED → GREEN → scope check → Verify → **Candidate Commit(task branch)→
>   Mechanical Gate → 整合(按 integration DAG)→ Wave/Dedicated Review → ACCEPTED**
>   → 派工者記帳。核心規則:未 Review 的程式碼可形成隔離 Candidate Commit,但未過
>   Review 的 Candidate 不得進正式 integration branch、不得標完成;只有 ACCEPTED
>   才勾 checkbox。每 T 一個 task worktree(`task/<slug>/T-n`)+ task-scoped 守衛;
>   Worker 不寫 5-tasks/6-notes/STATUS/twin(單寫者 = 派工者)。細節與欄位語意見
>   `notes/design/parallel-stage6.md`。

⚠️ Integrator 注意:**不得**把上述 seam 寫成與既有 ```text 區塊同款結尾
(`…review evidence`)—— renderer 的 `fenced_seam()` 以
`RED → GREEN.*?review evidence` findall==1 抽取,出現第二個匹配即 SystemExit。
上文以「ACCEPTED」收尾,安全。改 README 後跑 `render --write` + 兩檢查腳本。

### 5.2 README.md §5「守衛與並行」條目補一句

> 同 feature 內 T 級並行 = 每 T 各開 task worktree(`task/<slug>/T-n`,同 Wave 同
> Base SHA),守衛以 `--task` 釘單 T scope;仍然是「一工作樹一武裝」,不破例。

### 5.3 README.md §9 模型表(additive 兩列)

| 階段/角色 | 模型 | effort | 備註 |
|---|---|---|---|
| 6 Wave review(parallel) | sonnet fresh | high | 一次審一個 wave;**必須**輸出每 T 獨立 verdict + finding 歸屬 + integration verdict |
| 6 Mechanical Gate | (無模型,機械) | — | 14 項檢查全 PASS 才 READY_FOR_INTEGRATION |

### 5.4 `_templates/6-implementation-notes.md` 執行軌跡節(註解擴充,additive)

在現有「每 T 一列」註解補:

> parallel 模式加記:wave 編號 | candidate SHA | gate verdict(devflow-gate-result.v1
> 的 verdict)| review 途徑(wave n / dedicated)。sequential 留白照舊。

### 5.5 `_templates/7-review.md` 執行記錄表

補一句(執行記錄表說明處):「parallel 模式加列 wave 分佈與 gate FAIL 重工次數」。

### 5.6 guide html

README/模板改動後由 Integrator 跑 `scripts/render-methodology-corrections.sh --write`
重生 parity 區;本 workstream 未動任何 html。

## 6. 外部 plugin 待辦(`/Users/asheng/.claude/plugins/local/dev-flow/`)

| # | 檔案 | 變更 | 驗收方式 |
|---|---|---|---|
| 1 | `hooks/_exec_impl.py` | frontmatter `execution:` 迷你解析(縮排式,fail-closed)+ 新選配欄位驗證(引用/環/high+wave)+ `start <slug> --task T-n` 子模式(scope=單 T Files;exec.json 加 `task/mode/base_sha/state/candidate_sha/attempt`;status 擴充輸出) | 對拍 `tests/parallel-stage6/fixtures/*.md`:每個 fixture 的 accept/reject 與錯誤要點須與 `contract_ref.parse_5_tasks` 一致;不帶 `--task` 時舊 `selftest.sh` 全綠(行為 byte-identical) |
| 2 | `hooks/devflow-exec.sh` | start 轉發 `--task` 參數;新增 `gate` 子命令分派 | `start <slug> --task T-1` 可達 task 模式;無 `--task` 輸出不變 |
| 3 | `hooks/_guard_impl.py`、`devflow-lib.py` | task 模式恆許變更:**移除** 5-tasks/6-notes 恆許、**新增** `.devflow/task/<T-id>/` evidence 放行(其餘 `.devflow/` 仍禁) | selftest 新案例:task 模式寫 6-notes 被擋(exit 2)、寫他 T Files 被擋、寫 `.devflow/task/T-1/x.log` 放行 |
| 4 | `hooks/_prebash_impl.py`、`_postbash_impl.py` | shell 側同步 task scope 比對 | selftest:shell 寫 scope 外 → postbash 抓;stop 只撤本 worktree(雙 worktree 案例互不影響) |
| 5 | 新 `hooks/_gate_impl.py`(建議) | Mechanical Gate 14 項,輸出 `devflow-gate-result.v1` | 對拍 `fixtures/gate-*.json`:verdict 與 failed check id 集合須與 `contract_ref.run_gate` 完全一致(10 個 fixture 全數) |
| 6 | `hooks/selftest.sh` | 新增 #1-#5 的案例 | selftest 全綠(含既有 ~33 案) |
| 7 | `skills/dev-run/SKILL.md` | parallel 派工迴圈:wave 計算(§4 演算法)、Task Context Packet(§5 清單)、candidate→gate→integration queue→wave/dedicated review→ACCEPTED 記帳、conflict 不親修、rebuild 規則、狀態機(§10) | `gate-consistency.sh` 綠;人工對照 `notes/design/parallel-stage6.md` §5/§11/§12 逐條有落點 |
| 8 | `skills/dev-flow/SKILL.md` | Stage 6 列補一句「5-tasks 明寫 execution.mode: parallel 時走並行引擎(選配)」 | gate-consistency 綠 |

前置注意(audit 不確定事項 8):plugin repo 有未合併 branch
`codex/dev-flow-methodology-corrections`,plugin 側開工前先確認其狀態。

## 7. 不採用的建議(+ 理由)

1. **Prompt 七「(全 feature)同一 Base SHA」字面義** → 細化為「同 Wave 同 Base SHA」
   (DD-1):Blocked-by 硬依賴者必須建立在前置程式碼之上,全域單一 Base 與硬依賴互斥;
   candidate 記錄自己的 base_sha 供 gate `base_sha_match` 驗證。
2. **在本 repo 實作 scheduler/worktree 管理程式** → 不採:runtime 不在本 repo,
   audit 明令不建假 runtime;改為可執行契約 + fixtures 對拍。
3. **execution 設定放獨立設定檔或正文 YAML 區塊** → 不採,住 5-tasks frontmatter
   (DD-2):單一正本、機器可讀、不動 T 區塊 parser。
4. **execution 未知 key 靜默忽略** → 不採,fail-closed 拒啟(DD-3):拼錯
   `max_parallel_tasks` 被靜默忽略 = 以為有上限而沒有。
5. **`rebuild_integration_on_rework` 預設 false(省重建時間)** → 不採,預設 true:
   review 紀律優先,受汙染的 integration branch 必須重建。
6. **手工 `Execution-wave:` / 人工 `Conflicts-with:` 欄位**(prompt 已明言不要,記錄
   確認):不採 —— wave 是派生資料,overlap 由 Scheduler 判。
7. **README/6-notes/7-review 直接修改** → 不採(檔案所有權),改列 §5 提案文字。

## 8. Prompt A 十五節對照(逐節交代)

| 節 | 落點 |
|---|---|
| 一 現況審核 | 設計文件 §1(11 項逐條 + runtime 不在本 repo 推論) |
| 二 保留 sequential | 模板 execution 缺省 sequential;契約 §2.3;94 條內 sequential regression 檢查;74/74 保綠 |
| 三 parallel 模式 | 模板 frontmatter execution 區塊(明確啟用);契約 §2.1 |
| 四 Task metadata | 模板頂註 + 契約 §2.2(四個選配欄 + 缺省 + 不設手工 wave/conflicts) |
| 五 兩種 DAG | 契約 §3-§4 + contract_ref(環/未知引用/overlap/max/退化/不回寫/restart 全測) |
| 六 Task Context Packet | 契約 §5(內容清單 + Worker 禁令);runtime 落地 = 待辦 #7 |
| 七 Task worktree | 契約 §6(branch 命名/不覆蓋/不 force/可恢復/rework 回原 branch;DD-1) |
| 八 Task-scoped Guard | 契約 §7(CLI 文法/恆許變更/status 欄位/exec.json v2);待辦 #1-#4 |
| 九 Candidate Commit | 契約 §8 + devflow-candidate.v1 schema + 核心規則原句 |
| 十 Mechanical Gate | 契約 §9(14 check id)+ contract_ref.run_gate + 10 個 gate fixtures;待辦 #5 |
| 十一 狀態機 | 契約 §10 + contract_ref 轉移表 + can_tick(只有 ACCEPTED 勾)全測 |
| 十二 整合與 Review | 契約 §11(integration DAG 序/conflict 不親修/rebuild/wave 三輸出);待辦 #7 |
| 十三 共享文件單寫者 | 契約 §12 + gate `shared_docs_untouched` + guard 恆許變更(待辦 #3) |
| 十四 測試 | 契約 §14 對照表:15 項全數落 94 條或外部驗收(§6 表) |
| 十五 輸出 | 本檔 + `notes/design/parallel-stage6.md` |
