# Stage 6 並行執行設計 + External Interface Contract(parallel-stage6 v1)

> Workstream A(devflow-vnext/execution)產出。**本檔是設計文件 + 對外部 runtime 的
> 精確介面契約**,不是規則正本 —— 方法論正本仍是 `README.md` 與 `_templates/`;
> 執行引擎(runtime)住 `~/.claude/plugins/local/dev-flow/`(獨立 repo),
> 本 repo 一行 runtime 程式碼都不含。plugin 側落地清單見
> `notes/change-manifests/execution.md` 的「外部 plugin 待辦」。
>
> 機械可驗部分(欄位語意、DAG/Wave、狀態機、gate 檢查、result schema)以
> `tests/parallel-stage6/contract_ref.py` 為**可執行契約**(executable spec):
> plugin 實作必須通過同一組 fixtures(`tests/parallel-stage6/fixtures/`)。
> contract_ref 是文檔校驗器(與 `scripts/` 兩支同類),**不是引擎、不派工、不碰 git**。

## 0. 目標與邊界

在**完全保留 sequential 行為**的前提下,為同一 Feature 的多 Task 新增**可選** parallel 模式:

```
Stage 5 Task DAG
→ Coordinator 計算執行 Wave
→ Haiku Worker 在獨立 task worktree 執行
→ Candidate Commit
→ Mechanical Gate
→ Integration Queue
→ Wave/Dedicated Review
→ ACCEPTED
→ Stage 7
```

邊界:

- `execution.mode` 缺省 = `sequential`;舊 `5-tasks.md`(無任何新欄位)**行為完全不變**。
- parallel 必須明確啟用(`mode: parallel`),不自動套用任何 Feature。
- 既有 acceptance seam(README §5)在 sequential 模式一字不動;parallel 模式的 seam
  變體(Candidate/Gate/整合後 Review)須由 Integrator 依 manifest 補進 README 正本,
  在那之前本檔僅為提案 + 契約。

## 1. 現況審核結論(2026-08-02,逐項)

| 項 | 現況 | 出處 |
|---|---|---|
| Stage 5 parser | 只解析 `## T-n` 區塊的必填四欄 Covers/Files/Verify/Blocked-by;**忽略未知行**(選配欄位天然向後相容);不讀 5-tasks frontmatter | plugin `hooks/_exec_impl.py:61-98` |
| Blocked-by 語意 | 純文檔序(拓撲序派工),runtime 只驗欄位非空,不建 DAG、不驗引用/環 | `_exec_impl.py:86-88`、dev-run SKILL「照 Blocked-by 拓撲序,禁併 T」 |
| Stage 6 acceptance seam | `RED → GREEN → scope check → Verify → independent T review → PASS → commit → bookkeeping`;PASS 前禁 commit | README §5(:113-119)、6-notes 模板頂註 |
| commit 規則 | 一 T 一 commit,派工者(Coordinator)commit,執行者禁 commit | dev-run SKILL「執行者不得自行 commit」 |
| worktree 規則 | 並行 = 各開 git worktree;守衛以工作樹為單位;同樹異 slug start 一律拒絕 | README :155-161、`_exec_impl.py:27-45` |
| guard state | `.devflow/exec.json`(slug/scope/extra/baseline/contract_hashes)+ git-dir sentinel `devflow-armed`;fail-closed | `_exec_impl.py:13-15,146-152`、`devflow-lib.py:118-139` |
| devflow-exec.sh | 15 行薄殼,start/stop/status/allow 四子命令,無 `--task` 概念 | plugin `hooks/devflow-exec.sh` |
| dev-run skill | prompt 層引擎:opus 派工、haiku 執行、sonnet fresh review、逐 T 迴圈,**無 wave/candidate 概念** | plugin `skills/dev-run/SKILL.md` |
| reviewer prompt | fresh sonnet,給 T + S 原文 + diff + 執行者輸出,不給結論;T Review Log 格式 | dev-run SKILL 步 2、6-notes 模板 T Review Log |
| model escalation | haiku 錯 1 → sonnet;sonnet 同 T 錯 2 → opus;同 T 上限 4;失敗先分類 SPEC/ENV/IMPL/UNKNOWN | README §5 五律 5 + §9(:301-303) |
| runtime 在本 repo? | **否**。引擎全在 `~/.claude/plugins/local/dev-flow/`(獨立 repo、無 remote);本 repo `scripts/` 是文檔校驗器 | 00-audit.md「Runtime 所在位置」 |

推論:runtime 不在本 repo → 本檔寫**精確 external interface contract**;本 repo 只改
模板(`_templates/5-tasks.md`)、schema、fixtures、可執行契約與設計文件;plugin 側
逐檔待辦 + 驗收方式列 manifest。**不建立假 runtime**。

## 2. 資料契約:5-tasks.md 擴充(全部選配)

### 2.1 Execution 設定(frontmatter,選配區塊)

```yaml
---
feature: <slug>
stage: 5-tasks
status: draft
owner:
updated:
execution:                              # 選配;整塊缺省 = 下列預設值
  mode: sequential                      # sequential(缺省)| parallel
  max_parallel_tasks: 3                 # 選配;>=1 整數;缺省 3
  rebuild_integration_on_rework: true   # 選配;true|false;缺省 true
---
```

解析契約(plugin `_exec_impl.py` 落地時必守):

- 只掃 frontmatter(首行 `---` 至下一 `---`)內的 `execution:` 行;其後**縮排 ≥2 空格**
  的 `key: value` 行屬於該區塊,遇非縮排行即結束。不引入 YAML 函式庫也能解析。
- `execution:` 區塊**不存在** → `mode=sequential`,行為與現行完全相同(bit-for-bit)。
- fail-closed 驗證(拒啟 + 明確訊息,不靜默忽略):
  - `mode` ∉ {`sequential`,`parallel`} → 拒。
  - `execution` 區塊內出現未知 key(例 `max_parallel` 拼錯)→ 拒(靜默忽略 = 守衛裝上但沒鎖)。
  - `max_parallel_tasks` 非正整數 → 拒;`rebuild_integration_on_rework` ∉ {true,false} → 拒。
- `mode: sequential` 且帶其餘合法 key → 合法,行為同缺省(執行層忽略 parallel 專用值)。

### 2.2 Per-T 選配欄位

保留必填四欄 Covers / Files / Verify / Blocked-by 與既有選配 Intent / Boundaries,新增:

| 欄 | 值域 | 缺省 | 語意 |
|---|---|---|---|
| `Integrate-after:` | `—` 或 T-id 清單(逗號分隔) | `—` | **整合順序約束**:可依核准契約平行實作,但 candidate 進 integration branch 必須在指定 T 之後 |
| `Risk:` | `normal` \| `high` | `normal` | 風險分級,決定 review 路徑缺省 |
| `Review-mode:` | `wave` \| `dedicated` | `normal→wave`、`high→dedicated` | wave = 整批 wave review;dedicated = 專屬 review,**PASS 才准進 integration** |
| `Semantic-conflicts-with:` | `—` 或 T-id 清單 | `—` | 檔案不重疊但語意衝突的 T,禁同 Wave(對稱生效) |

明文不做:

- **不新增必填的手工 `Execution-wave:`** —— Wave 是 runtime 派生資料(§4)。
- **不強制人維護 `Conflicts-with:`** —— Files overlap 由 Scheduler 自動判(§4.3)。

語意釐清(兩種依賴):

- `Blocked-by` = **硬執行依賴**:前置 T 未達安全狀態(§4.2)前,本 T 不得開始實作。
- `Integrate-after` = **軟整合依賴**:可同 Wave 平行實作,只約束整合順序。

驗證規則(parallel 模式 start 時;sequential 模式同樣驗引用完整性,但欄位無執行效果):

- 引用的 T-id 必須存在(`Integrate-after`/`Semantic-conflicts-with`/`Blocked-by` 同)。
- `Risk: high` + 明寫 `Review-mode: wave` → 拒(§7 規則「high 必 dedicated」不可被欄位繞過)。
- 自我引用(T-n 引 T-n)→ 拒。

### 2.3 向後相容鐵則

舊 5-tasks.md(無 `execution:` 區塊、無新欄位)→ parser 產出與現行 `_exec_impl.py`
完全相同的 scope/行為;新欄位行對舊 runtime 是未知行,**現行 regex 本來就忽略**,
因此新模板檔餵舊 runtime 也不炸(雙向相容)。可執行證據:
`tests/parallel-stage6/` 的 sequential regression 檢查 + 本 repo 既有 check 基線保綠
(條數以 `scripts/check-methodology-corrections.sh` 當次輸出為準,不寫死)。

## 3. 兩種 DAG

- **execution DAG**:節點 = T,邊 = `Blocked-by → T`。決定「誰能開始實作」。
- **integration DAG**:節點 = T,邊 = `(Blocked-by ∪ Integrate-after) → T`。決定「candidate 依什麼順序整合」。

驗證(兩張圖皆是,start 時機械執行):

1. 引用不存在的 T → 拒,訊息含缺的 T-id。
2. cycle → 拒,訊息含環路徑(如 `T-1 → T-2 → T-1`)。
3. execution DAG ⊆ integration DAG(Blocked-by 邊兩張圖都有)。

## 4. Wave(runtime 派生,不回寫)

### 4.1 演算法(決定論)

```
done = 已達安全狀態的 T 集合(restart 時從 runtime state 還原;冷啟 = ∅)
waves = []
while 尚有未排 T:
    ready = [T | T ∉ done ∧ T 的 execution DAG 前置全部 ∈ done],按 T 編號昇冪
    wave = []
    for T in ready:
        if len(wave) < max_parallel_tasks
           且 T 與 wave 內任一成員無 Files overlap
           且 T 與 wave 內任一成員無 Semantic-conflicts-with(對稱):
            wave.append(T)
    if wave 為空 → 內部錯誤(環已在 §3 擋掉)
    waves.append(wave); done ∪= wave
```

- 同輸入同狀態 → 同輸出(greedy + T-id 序,無隨機)。
- 單一 T 的 feature 自然退化成 1 wave × 1 task,行為等價 sequential。
- **Wave 不回寫 5-tasks.md**:5-tasks 是唯一正本,wave 只存 runtime state(§8),
  restart 以「per-task state → done 集合 → 重算」恢復,不信任何快取。

### 4.2 安全狀態(Blocked-by 的「可開始」門檻)

前置 T 的狀態 ∈ {`INTEGRATED`,`IN_REVIEW`,`ACCEPTED`} 才算安全 —— 依賴者要
**建立在前置程式碼之上**,所以門檻是「已進 integration branch」,不是「有 candidate」。
前置被打回(`REWORK`)→ 依賴者若未開工轉 `BLOCKED`;已開工由 Coordinator 依
§9 rebuild 規則處置。

### 4.3 Files overlap 判定

- 路徑先過 canonical 化(同 runtime `canonical_scope_path`:repo-root 相對、禁絕對/
  `..`/root 條目;目錄以 `/` 結尾)。
- overlap = 路徑相等,或一方為目錄前綴蓋住另一方(`src/api/` vs `src/api/x.ts`)。
- 同 Wave 禁 overlap(硬規則);跨 Wave overlap 合法(後 wave 基於已整合 tip)。

## 5. Task Context Packet(Coordinator 動態組裝,非永久契約)

派給 Worker 的 prompt 固定含(缺一不派):

Run ID、Feature slug、Task ID、Task 標題、Intent、Covers 的 R/S **原文**、
Operational Context、Allowed Files(= 該 T Files,canonical)、Verify 指令、
Blocked-by、Integrate-after、Risk、Review-mode、Boundaries、必要的 living spec 節錄、
相關 interface 定義、可模仿 pattern(現有檔案片段)、Base SHA、Contract hash、
Prompt ID/Version、完成回報格式。

Worker 禁令(Packet 內明文 + 守衛機械強制,對應 §7):

- 禁讀 Stage 1/2/3(既有圍欄②)。
- 禁改 4-spec、5-tasks、6-notes、STATUS、HTML twin。
- 禁碰其他 Task 的 runtime state/worktree。
- 未經 L1 流程(allow + D-n)不得擴 scope。
- 禁自行改 API 契約(= L2,停)。
- 禁 commit 到 integration/feature branch(candidate 只落 task branch)。

## 6. Task worktree

- Branch 命名:`task/<slug>/T-n`;worktree 目錄由 runtime 配置(建議 `<repo>-task-<slug>-T-n`)。
- **同 Wave 同 Base SHA**:wave 起跑時 integration branch tip = 該 wave 全部 T 的
  Base SHA;wave 1 的 Base = feature branch 起點。每個 candidate 記錄自己的 Base SHA
  (§8),Mechanical Gate 驗證一致。(DD-1,見 §13:prompt 原文「同一 Base SHA」在
  存在 Blocked-by 時與「依賴者要建立在前置程式碼上」互斥,故細化為 per-wave。)
- 每個 task worktree:獨立 guard(`.devflow/exec.json` 本來就 per-worktree,零改動
  即隔離)、不共用 working directory、**不覆蓋既有 worktree**(目標目錄已存在 → 拒,
  不 force reset)、可中斷恢復(state 落盤,re-arm 同 slug+task 合法)。
- Rework 回**原 task branch** 繼續(新 attempt、新 candidate),不開新 branch。

## 7. Task-scoped Guard(CLI 契約;plugin 落地)

### 7.1 指令文法

```
devflow-exec.sh start <slug>                    # 舊行為,一字不動(feature-level scope)
devflow-exec.sh start <slug> --task T-1         # 新:task-level scope
devflow-exec.sh stop                            # 不變;只撤本 worktree 的守衛
devflow-exec.sh status                          # 擴充輸出(見 7.3)
devflow-exec.sh allow <file> --reason "..."     # 不變;task 模式下 allow 仍記 D-n
```

### 7.2 `start --task` 語意

- scope = **只有該 T 的 Files**(canonical 聯集),不是全 T 聯集。
- 前置驗證同現行(4-spec approved、必填四欄)+ §2/§3 新驗證。
- `--task` 指到不存在的 T → 拒。
- task 模式下恆許路徑變更(單寫者原則,§11):
  - **移除**現行對 `docs/dev/<slug>/5-tasks*` 與 `6-implementation-notes*` 的恆許 ——
    Worker 禁寫共享文件。
  - **新增**恆許 `.devflow/task/<task-id>/`(task-local runtime evidence 專區:RED/GREEN
    log、candidate metadata);`.devflow/` 其餘仍禁(守衛狀態只准 CLI 動)。
- 異 slug 或異 task 已武裝 → 拒(沿用現行「絕不靜默覆寫」);同 slug+同 task re-arm 合法。
- 不帶 `--task` 時**逐 byte 維持舊行為**(含輸出文案),舊測試(selftest.sh)全過。

### 7.3 `status` 輸出(task 模式至少含)

```
feature=<slug> task=T-1 mode=parallel worktree=<path>
scope=<n 項> base_sha=<sha> contract_hash=<h> candidate_sha=<sha|—> state=<狀態機值>
```

sequential/feature-level 模式輸出維持現行格式(向後相容),僅允許 additive 附加行。

### 7.4 exec.json v2(additive)

現有欄位全保留;task 模式新增:

```json
{
  "slug": "...", "started": "...", "scope": [...], "extra": [...],
  "baseline": {...}, "contract_hashes": {...}, "contract_hash_scope": "repo-wide-v1",
  "task": "T-1", "mode": "parallel",
  "base_sha": "<wave base>", "state": "RUNNING",
  "candidate_sha": null, "attempt": 1
}
```

無 `task`/`mode` 欄 = legacy feature-level state(舊檔可讀,fail-closed 原則不變)。
不同 task worktree 各有自己的 exec.json + sentinel → `stop` 天然互不影響(需 selftest 案例證明)。

## 8. Candidate Commit

parallel 模式的 per-T seam:

```
RED → GREEN → scope check → Verify
→ Candidate Commit(task branch)
→ Mechanical Gate
→ READY_FOR_INTEGRATION(狀態機 MECHANICAL_PASS → QUEUED_FOR_INTEGRATION)
```

Candidate 規則:

- 只存在於 task branch(`task/<slug>/T-n`),是**不可變審查單位**(rework = 新 commit
  新 candidate,不 amend、不 force-push)。
- 尚未 ACCEPTED:**不得勾 5-tasks checkbox、不得標完成**。
- 不得直接進正式 integration branch —— 只有 Coordinator 依 §9 整合。
- 必須綁定 metadata(`.devflow/task/<T-id>/candidate.json`):

```json
{
  "schema": "devflow-candidate.v1",
  "feature": "<slug>", "task": "T-1", "attempt": 1,
  "branch": "task/<slug>/T-1",
  "base_sha": "<sha>", "candidate_sha": "<sha>",
  "prompt_id": "<packet id>", "prompt_version": "<ver>",
  "contract_hash": "<start 時釘住的 4-spec 契約 hash>",
  "verify": {"command": "<5-tasks Verify 原文>", "exit_code": 0, "log": "<path>"},
  "red":   {"command": "...", "exit_code": 1, "log": "<path>", "at": "<ISO8601>"},
  "green": {"command": "...", "exit_code": 0, "log": "<path>", "at": "<ISO8601>"},
  "test_names": ["..."],
  "changed_files": ["..."],
  "created_at": "<ISO8601>"
}
```

**核心規則**:未 Review 的程式碼可以形成隔離的 Candidate Commit,但未通過 Review 的
Candidate 不得進入正式 integration branch,也不得標示完成。

## 9. Mechanical Gate(機械檢查,無判斷;plugin 落地)

輸入 = candidate.json + task 定義 + 守衛 state;輸出 = 結構化結果。檢查 14 項(id 固定,契約錨):

| # | check id | 判準 |
|---|---|---|
| 1 | `candidate_exists` | candidate_sha 指向的 commit 存在於 task branch |
| 2 | `base_sha_match` | candidate.base_sha == 該 wave base(state 記錄值) |
| 3 | `files_within_scope` | changed_files ⊆ 該 T Files(canonical;含 allow 的 extra) |
| 4 | `protected_untouched` | changed_files 不含任何 feature 的 1/2/3/4 檔(契約防篡改) |
| 5 | `red_present_failing` | red 存在且 exit_code ≠ 0 |
| 6 | `green_present_passing` | green 存在且 exit_code == 0 |
| 7 | `red_before_green` | red.at 早於 green.at |
| 8 | `verify_command_match` | verify.command == 5-tasks 該 T Verify 原文 |
| 9 | `verify_exit_zero` | verify.exit_code == 0 |
| 10 | `s_id_present` | test_names 至少一個含該 T Covers 的每個 S-id |
| 11 | `contract_hash_unchanged` | candidate.contract_hash == start 時釘住值 |
| 12 | `diff_applies` | candidate diff 可乾淨套上當前 integration tip(dry-run) |
| 13 | `result_schema_complete` | candidate.json 含 v1 schema 全部必填鍵 |
| 14 | `shared_docs_untouched` | changed_files 不含 5-tasks/6-notes/STATUS/HTML twin |

輸出 schema:

```json
{
  "schema": "devflow-gate-result.v1",
  "feature": "<slug>", "task": "T-1", "candidate_sha": "<sha>",
  "verdict": "PASS",
  "checks": [{"id": "candidate_exists", "status": "PASS", "detail": ""}, ...14 項全列...],
  "checked_at": "<ISO8601>"
}
```

`checked_at` 語意 = **gate 執行檢查的時刻**(非 candidate 建立時刻),由 runtime 蓋章;
contract_ref 為保決定論不自取時鐘,由呼叫者以參數顯式傳入(fixtures 未傳 → 空字串)。

verdict = PASS ⟺ 14 項全 PASS;任一 FAIL → verdict FAIL + 該 T 轉 REWORK。
Gate 只機械比對,**不做語意判斷**(語意歸 Review)。

## 10. 狀態機

```
PENDING → READY → RUNNING → CANDIDATE → MECHANICAL_PASS
  normal:  MECHANICAL_PASS → QUEUED_FOR_INTEGRATION → INTEGRATED → IN_REVIEW → ACCEPTED
  high:    MECHANICAL_PASS → IN_REVIEW(dedicated)→ QUEUED_FOR_INTEGRATION → INTEGRATED → IN_REVIEW(wave 段免)→ ACCEPTED
  失敗:    CANDIDATE|IN_REVIEW → REWORK → RUNNING(原 task branch 新 attempt)
  阻塞:    PENDING|READY ↔ BLOCKED(前置 REWORK / L2)
```

合法轉移全集(契約錨;不在表內 = 非法):

```
PENDING→READY, PENDING→BLOCKED, BLOCKED→READY,
READY→RUNNING, READY→BLOCKED,
RUNNING→CANDIDATE, RUNNING→BLOCKED,
CANDIDATE→MECHANICAL_PASS, CANDIDATE→REWORK,
MECHANICAL_PASS→QUEUED_FOR_INTEGRATION, MECHANICAL_PASS→IN_REVIEW,
QUEUED_FOR_INTEGRATION→INTEGRATED, QUEUED_FOR_INTEGRATION→REWORK,
INTEGRATED→IN_REVIEW, INTEGRATED→REWORK,
IN_REVIEW→ACCEPTED, IN_REVIEW→REWORK, IN_REVIEW→QUEUED_FOR_INTEGRATION,
REWORK→RUNNING
```

補充語意:`MECHANICAL_PASS→IN_REVIEW` 只限 Review-mode=dedicated;
`IN_REVIEW→QUEUED_FOR_INTEGRATION` 只限 dedicated PASS 後;
`QUEUED_FOR_INTEGRATION→REWORK` = 整合衝突/整合後 Verify 紅。

**不變量:只有 `ACCEPTED` 才能勾 5-tasks checkbox**(勾的人 = Coordinator,§11)。

## 11. 整合與 Review

- Integration branch:`integration/<slug>`,由 Coordinator 自 feature base 建立。
- Coordinator 按 **integration DAG** 拓撲序(同序位按 T 編號)cherry-pick candidate;
  每整合一個 candidate 即跑**該 T 的 Verify**;wave 全員整合完跑 **Wave regression**
  (既有全套 + 本 wave 全部 Verify)。
- Cherry-pick conflict → **Coordinator 不得自行修**:該 T 轉 REWORK,conflict 原文
  作為 finding 回原 Worker;rework 產生新 candidate 重過 Gate。
- Review finding 一律回**原 Worker**(五律 2:派工者不下場修)。
- `rebuild_integration_on_rework: true` → 任何已整合 T 被打回時,integration branch
  自 base 重建,按 integration DAG 重放其餘存活 candidate(受影響的後續 T 重驗);
  `false` → 只 revert 該 T(留給小 feature 的快速路徑,風險自負,預設不建議)。
- Review 路徑:
  - `normal` → **Wave Review**:wave 全員 INTEGRATED 後,fresh reviewer 一次審整個 wave。
  - `high` → **Dedicated Review**:MECHANICAL_PASS 後、進 integration **之前**,
    fresh reviewer 單獨審;PASS 才 QUEUED_FOR_INTEGRATION。
- Wave Reviewer 可一次看一個 Wave,但輸出**必須**含:

```json
{
  "schema": "devflow-wave-review.v1",
  "feature": "<slug>", "wave": 2,
  "tasks": [
    {"task": "T-3", "verdict": "PASS", "findings": []},
    {"task": "T-4", "verdict": "FAIL",
     "findings": [{"id": "F-1", "task": "T-4", "severity": "major",
                   "evidence": "<spec 原文或 diff hunk 引用>"}]}
  ],
  "integration_verdict": "PASS",
  "reviewed_at": "<ISO8601>"
}
```

驗證規則(契約):wave 內**每 T 都有獨立 verdict**;**每 finding 都有 task 歸屬**
(且歸屬的 T 在本 wave);`integration_verdict` 必在。缺一 = review 無效,不得推進狀態。

## 12. 共享文件單寫者

Worker **不得**更新:5-tasks checkbox、6-notes、STATUS、HTML twin。
Worker 只輸出 task-local runtime evidence(`.devflow/task/<T-id>/`:candidate.json、
RED/GREEN/Verify log)。Coordinator 在該 T **ACCEPTED 後**才記帳(勾 checkbox、
T Review Log、Progress Log、TDD Evidence 謄錄、執行軌跡),沿用現行「文件記帳累積、
隨後續 commit 帶入」規則。機械強制 = §7.2 的恆許變更(guard 擋 Worker 寫共享檔)。

## 13. Design Decisions(模型自判,供 review 對照)

- **DD-1 Base SHA per wave**:prompt 七要求「同一 Base SHA」,但 Blocked-by 依賴者
  必須建立在前置程式碼之上,全 feature 單一 Base 與硬依賴互斥。裁決:同 Wave 同
  Base(= wave 起跑時 integration tip),candidate 記錄自己的 base_sha 供 Gate 驗證。
- **DD-2 execution 設定住 frontmatter**:5-tasks 已有 frontmatter,機器可讀且不動
  T 區塊 parser;不另立設定檔(避免第二正本)。縮排式迷你解析,免 YAML 依賴。
- **DD-3 未知 execution key fail-closed**:拼錯 key 靜默忽略會讓「以為有上限」的
  守衛失效;寧可拒啟。與守衛 fail-closed 家風一致。
- **DD-4 `Risk: high` + `Review-mode: wave` = 拒**:high 必 dedicated 是規則不是預設,
  欄位不得繞過。
- **DD-5 sequential 模式也驗新欄位引用完整性**:欄位無執行效果但 typo 早抓;
  不驗 = 留地雷給日後切 parallel。
- **DD-6 contract_ref.py 住 tests/,定位 = 可執行契約**:與 audit「本 repo scripts/
  是文檔校驗工具」同類;不派工、不碰 git、不長駐 —— 非假 runtime。
- **DD-7 Worker evidence 住 `.devflow/task/<T-id>/`**:untracked、per-worktree、
  guard 可白名單;不落 `docs/dev/`(那是共享文件區,單寫者原則)。

## 14. 測試對照(prompt 十四 × 落地位置)

| 十四項 | 本 repo 可執行(tests/parallel-stage6/) | plugin 側(external) |
|---|---|---|
| 舊 Task 格式 | fixture `old-format.md` + 真檔 example 5-tasks 解析 = sequential、零錯誤 | selftest:舊檔 start 行為不變 |
| 新 optional fields | `parallel-basic.md` 全欄位解析 + 缺省補值 | parser 落地同 fixtures |
| execution cycle | `cycle-execution.md` → 拒 + 環路徑 | 同 fixture |
| integration cycle | `cycle-integration.md` → 拒 | 同 fixture |
| Files overlap | `overlap.md` → 同 wave 分離;目錄前綴案 | scheduler 落地 |
| max parallel | wave 大小 ≤ N | 同 |
| restart | done 集合重算 = 決定論恢復 | state 落盤/重讀 |
| task-scoped guard | task scope = 單 T Files(契約層) | selftest:--task 擋跨 T 寫入、stop 隔離 |
| Candidate 超 scope | gate fixture `gate-scope-excess.json` → FAIL | gate 落地 |
| RED/GREEN 缺失 | `gate-missing-red.json` 等 → FAIL | 同 |
| contract drift | `gate-contract-drift.json` → FAIL | 同 |
| 未 Review 不可完成 | 狀態機:CANDIDATE/MECHANICAL_PASS→ACCEPTED 非法;can_tick 只認 ACCEPTED | runtime 強制 |
| Wave per-task verdict | review schema fixtures(缺 verdict/歸屬 → 無效) | reviewer prompt 落地 |
| high-risk dedicated | 缺省解析 high→dedicated;high+wave → 拒 | 排程路徑落地 |
| sequential regression | 真檔 example 解析 + 既有 check 基線全綠 + renderer fixed point 全綠(條數動態,以腳本輸出為準) | selftest 全綠 |

## 15. 外部 plugin 待辦

詳列(檔案 × 變更 × 驗收)見 `notes/change-manifests/execution.md`。
