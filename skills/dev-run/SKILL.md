---
name: dev-run
description: dev-flow Stage 6 內部執行引擎 — 多模型派工(haiku 寫碼 → sonnet 審 → 錯誤升階),配 devflow-exec 執行守衛,全程不打斷問人。正常由 /dev-flow 定位到 Stage 6 時自動載入,使用者不需直接呼叫;使用者說「dev-run <slug>」「開始執行 <slug>」「跑實作」時亦啟用(相容直呼)。
---

# dev-run — Stage 6 執行引擎

你是**派工者**(主對話,opus/fable5 層):讀 spec、派 T、收驗、**commit 與記帳** ——
不下場寫碼。逐 T acceptance seam 的唯一核心規則在 README §5,執行順序與證據
格式以 `_templates/6-implementation-notes.md` 頂註清單 / T Review Log 為準;
本檔只定義 `dev-run` 的派工、模型升階與職責適配,不另立第二套 review policy。

## 前置(缺一不啟;順序不可調)

1. **先進工作樹**:單線 → feature branch;並行 → 先建 worktree 並 `cd` 進去。
2. 在該工作樹跑 `devflow-exec.sh start <slug>`(plugin `hooks/` 內)。守衛只武裝
   「start 當下所在的那棵樹」—— 先 start 再換樹 = 安全網失效。跑 `status` 確認
   slug 與 cwd 相符。被拒(4-spec 非 approved / 無可解析 Files / 4-spec Profile
   lane: fast + Risk: high 無 Owner Call)→ 停,回報使用者。
3. 讀 4-spec、5-tasks、living spec、`.claude/rules/*.md`;業務語意改查長期記憶
   (`${CLAUDE_PLUGIN_ROOT}/memory/dev-memory.py ask "<詞> 是什麼意思"`),不再讀 CONTEXT.md。
   **禁讀 1/2/3**(守衛會擋,含 shell)。
4. **開 memory session**(記憶生命週期的起點,見「記憶生命週期」節):
   ```
   ${CLAUDE_PLUGIN_ROOT}/memory/dev-memory.py session start \
     --mode implementation --slug <slug>
   ```
   把回傳的 `session_id` 當本次 Stage 6 的 workflow state 全程重用
   (下稱 `MEMORY_SESSION_ID`)。**不開 session = 這次實作學到的東西不會留下來**
   —— Git 會有 commit,而記憶什麼都不知道。

5-tasks frontmatter 有 `execution.mode: parallel` → 走「並行模式」節(wave 派工迴圈,
任務樹以 `start <slug> --task T-n` 武裝);否則走下方逐 T 迴圈,行為與既往完全相同。

## 誰做什麼(職責分配)

| 動作 | 誰 |
|---|---|
| 寫碼、跑 Verify、貼 RED/GREEN 原文輸出到回報 | 執行者(fresh subagent) |
| 依共用 T acceptance seam 收驗、判 PASS/FAIL | reviewer(fresh sonnet) |
| **PASS 後 commit、寫 Progress Log(hash)/T Review Log、勾 checkbox、謄 TDD Evidence/Decisions/執行軌跡** | **派工者(你)** |
| 判偏差級、呼叫 `allow`/`stop`、諮詢 adviser | 派工者(你) |

執行者**不得自行 commit**(先審後 commit 是引擎順序)。文件記帳 edit 累積,
隨下一個 T 的 commit 帶入;最後一個 T 之後補一次 bookkeeping commit。

**派工者禁親修**(README §5 驗證五律 2):reviewer 的 finding 一律重派執行者修、
重新送審 —— 你親自動手修 = 跳過 review,你的 context 也不再乾淨。同理,
**反預判禁令**(五律 3):你寫的 reviewer 派工 prompt 出現「不要標記 X」「最多算
Minor」「計畫已決定所以不算」→ 停手重寫。大材料(diff、報告)以檔案路徑交接,
不整份貼進主對話。

## 模型分層與升階

| 角色 | 模型 | 規則 |
|---|---|---|
| 派工者(你) | opus / fable5 | 派工、彙整、commit、記帳;不寫碼 |
| T 執行 | **haiku 起步** | 「錯」= reviewer 判 FAIL(或執行者自陳卡關送不出)。haiku 錯 1 次**立即**升 sonnet(同層不重試);sonnet 同 T 最多 2 次(換方法不歸零)才升 opus;升階時把完整失敗軌跡帶給下一階 |
| T review | **sonnet**(fresh context) | 依 README §5 / 6-notes 共用 acceptance seam;高風險或爭議時由 opus 作第二 reviewer |
| adviser | opus,唯讀 | **三層皆 FAIL = 連敗** → 派 adviser 診斷:是 T/5-tasks 定義問題,還是純執行問題;verdict=STOP → 走 L2 路徑 |

## 事件寫入通道(四軌 obs W2/W3;sequential 與並行共用)

> **Runtime 現況(誠實條件,2026-08-19 更新)**:`start <slug> --task T-n`(parallel task
> 武裝,schema=exec-v3)與 sequential 整 feature start(legacy/VNext feature-scope,
> schema=exec-v4)、Stage 7 review 自建武裝現在都會生 `run_id`(§7 前置修復,見
> `notes/dispatch-agent-dispatch-layer.md` 裁決 8/9)——`run_id` 本身不再是 sequential
> 的缺口。但本節下方的逐 T 事件寫入迴圈仍只描述 task-scoped 派工者動作;sequential
> 是否要比照逐步寫 `agent_dispatched`/`attempt_started` 等事件是後續工作範圍,執行
> 記錄現況仍以 6-notes 散文為準,不因 run_id 已存在就回頭幫 sequential 補寫本節
> 未定義的事件序列。

執行軌跡事件由**你**(派工者)經 `devflow-exec.sh event <slug>` 逐步寫入 run ledger
(事件 JSON 走 **stdin**;命令列不鋪 `.devflow/` 路徑)—— 這是 coordinator 唯一合法
落盤通道,guard/prebash 擋直改與 shell 重導向。run_id / base_sha 取 `start` 輸出;
事件的 `prompt` 物件({id, version, hash})一律取 `hooks/prompt-registry.json`
**現值**(id:執行者=stage6-worker、收驗=stage6-reviewer、adviser=stage6-adviser;
hash 必須是 registry 內 `prompt_hash` 實值,**禁佔位 hash** / 禁自編)。

## 逐 T 迴圈(照 Blocked-by 拓撲序,禁併 T)

1. **派工**:
   - **1a. 組派工 prompt**(三件套):
     - 目標與動機:T 內容 + Covers 的 S **原文** + 該 S 的 **Test Skeleton**(4-spec 有就附)
       + Verify 指令 + **該 T Files 現有檔案內容/慣例片段**(執行者只知道你給的,不靠它自行探路)
       + `.claude/rules/` **與該 T 相關的節**(全量貼是稀釋)
     - 驗收條件:先 RED 後 GREEN、測試名含 S-id、只動該 T 的 Files、**不要 commit**
     - 回報格式:diff 摘要 + RED/GREEN 原文輸出 + 自由選擇清單 + 卡關點
     完成 = 三件套齊全,prompt 已送出給執行者。
   - **1b. 寫事件**:派出即送 `agent_dispatched` + `attempt_started`(attempt_id /
     agent_role / model / prompt / base_sha)。完成 = 兩筆事件皆已送 ledger。
2. **收驗**:以 `subagent_type=dev-flow:devflow-reviewer`(`agents/devflow-reviewer.md`,
   fresh sonnet、`tools: Read` 唯讀——沒有 Bash,也沒有 Grep/Glob/Skill 與專案裝的
   MCP 工具;`git diff` 由你先跑好貼進 prompt,要搜的東西(例如「這個符號還有哪裡
   引用」)也是你先搜好貼進去,不要指望它自己查)明確派出(給 T + S 原文 + diff +
   執行者輸出,不給執行者結論;每 F 引 spec 原文或 diff hunk),依 README §5 /
   6-notes 的共用 seam 裁決並回傳 T Review Log 所需證據。
   FAIL → **先分類再路由**(README §5 驗證五律 5)。分三類,各走各的路:

   | 分類 | 什麼算 | 怎麼走 | 計不計入嘗試上限 |
   |---|---|---|---|
   | SPEC | T/S 定義本身有問題 | L2 停,回 G2 | 不計(已停工) |
   | ENV | 環境或相依壞了 | 修環境後重跑 | **不計** |
   | IMPL / UNKNOWN | 實作沒做對,或看不出原因 | 同一 T 升階重派(失敗軌跡全帶)並重新送審 | 計入 |

   **上限與強制動作**(與上表分開讀):同一個 T 總嘗試上限 4 次
   (haiku 1 + sonnet 2 + opus 1)。用盡 4 次 → **強制問 adviser**(以
   `subagent_type=dev-flow:devflow-adviser`——`agents/devflow-adviser.md`,同樣
   `tools: Read` 唯讀——沒有 Bash,也沒有 Grep/Glob/Skill 與專案裝的 MCP 工具;
   要它查證的東西你先查好貼進 prompt,附完整失敗軌跡),不得再重試。
   PASS → 你 commit → 讀出 hash。
   **寫事件**:派 reviewer 時 `review_started`,收到裁決 `review_completed`
   (review_verdict)+ 每個 finding 一筆 `finding_created`;收裁決後補
   `attempt_completed`(result=裁決結果;**FAIL 必附 failure_category**
   SPEC/ENV/IMPL/UNKNOWN);路由:同 T 重派 → `task_rework_requested`,
   升階 → `task_escalated`。
3. **記帳**(你寫):T Review Log 一筆、Progress Log 一列(日期|T-id|hash)、勾 checkbox、
   TDD Evidence 貼 RED/GREEN、Decisions 記自由選擇、執行軌跡一列(T-id|失敗分類
   SPEC/ENV/IMPL/UNKNOWN(無失敗填 —)|升階史|回合數|原因;回合數 = 三層合計,
   ENV 重跑不計)。以上全部在 PASS → commit 後寫入。
   **寫事件**:commit 後 `candidate_created`(candidate_sha = 該 T commit)+
   `task_accepted`。
4. **偏差**:L1(不動 R/S)→ 保守方案 + 記 D-n +(需要時)`devflow-exec.sh allow
   <file> --reason "D-n …"` + 續走。L2 或分不清 → 先問 adviser,verdict=STOP 或仍
   分不清 → `devflow-exec.sh stop`,回報使用者重走 G2。**全程不打斷問人,只有 L2 停。**

## Test Integrity Check(T review 七項;Stage 6 T-review prompt 增補)

sequential 收驗與並行 dedicated / wave review 的 reviewer prompt **必含**下列七項檢查
(P4 Gauntlet+Gates 條文):

1. 刪 assertion?2. 放寬 assertion(容忍度/範圍/型別)?3. 新增 skip/xfail/todo?
4. 同一步同時改測試與實作以重新定義正確性?5. mock 掉核心邏輯(mock 邊界可以,mock 被測物不行)?
6. 只追 coverage(無有意義 assertion)?7. 沒跑的 layer 寫 PASS(對 6-notes 宣稱抽查原始輸出)?
任一命中 → T review FAIL 回同一 T,失敗分類照驗證五律 5。

## 收尾

全 T 完 → **你**跑回歸(既有全套,全綠才算)→ 6-notes Self-Review 自檢(答不出 → 回補,
必要時重派該 T)→ bookkeeping commit → **發布最終成果:最後一個 bookkeeping commit
完成後、`stop`/回報 Stage 7 之前,push feature branch 到 remote,再 `git fetch` 驗證
remote tip 等於當下 feature HEAD;push 或驗證失敗就停在這裡,不得宣稱 Stage 6 完成**
(STATUS 的 `Branch` 欄與 README「直接補修」算法都拿 remote ref 當座標,沒推上去 =
其他人算聯集時看不到你的戰場)→ `devflow-exec.sh stop` → 回報使用者進
Stage 7(送審前置派工見「Stage 7 送審前置」節)。7-review.html 須含執行記錄表
(模型分佈/升階次數/D-n 與 allow 清單)。
**固化記憶(W6)**:回歸綠 + bookkeeping 完成 + 最終 commit 存在**之後**,跑
`dev-memory.py checkpoint $MEMORY_SESSION_ID --end`(見「記憶生命週期」節)。
時機在回歸綠之後不是之前:沒過回歸的東西還不是「這個專案現在的樣子」。
`.dev-flow/` 的改動隨 feature branch 一起 commit/push,不另開 branch。

**寫事件與衍生(W5)**:回歸綠後送 `stage_completed`(stage=6)→ 跑
`devflow-obs.sh derive` 重建 run-events.jsonl —— 6-notes 執行軌跡列與 7-review
執行記錄由 ledger **衍生**(禁手動雙寫),`devflow-obs.sh stats` 產模型分佈/升階
摘要供 7-review 執行記錄表 → 最後送 `run_completed`。

## 記憶生命週期(Stage 6 做完要真的「長記憶」)

沒有這一節的話,Stage 6 做完只有 Git commit,**Memory 什麼都不知道** ——
下一個 session、下一台機器、下一個人都得重新讀一次 code 才知道發生過什麼。

```
Stage 6 開工                     session start --mode implementation --slug <slug>
   │                               (記 session_id / feature slug / branch / 起始 HEAD)
   ▼
每個 T PASS 之後(可選)          session observe <sid> …
   │                               高訊號 → 累積成候選(本機);低訊號 → 只留本機
   ▼
回歸綠 + 記帳完成 + 最終 commit   checkpoint <sid> --end
   │                               ← durable 寫入**只在這裡**發生
   ▼
.dev-flow/ 隨 feature branch commit/push
```

**每個 T PASS 之後**可以記一筆(不是義務,只在真的有東西學到時才記;
`observe` 不會馬上寫 Git,候選累積到 checkpoint 才一次固化):

```
dev-memory.py session observe $MEMORY_SESSION_ID \
  --kind <種類> --title "<一句話>" [--body "<細節>"] \
  [--path-ref <repo 相對路徑>]... [--commit <sha>]
```

`--kind` 可以是**事件種類**,或 `fact` / `decision` / `skill` / `knowledge`
(後四種各自配 `--fact-json` / `--decision-json` / `--skill-json` /
`--knowledge-json`)。

| 值得記(高訊號) | 不要記(低訊號,工具會自己擋掉) |
|---|---|
| 架構變更、schema 變更、表改名、API 契約變更 | 讀檔、grep、列目錄 |
| 業務規則、bug root cause、重要設計決策 | 一般成功指令、中間 debug |
| 驗證過的流程、breaking config、實作事實 | 暫時假設、未確認推論、raw log |
| 發現的重要關聯 | 每輪對話逐字稿 |

低訊號送進去**不是錯**:工具回 `signal: low` 並只留本機,不進 Git。
所以拿不準時照送,由 Signal Gate 判,不要自己先過濾掉真正重要的東西。

**三條硬規則**:

1. **`--kind fact` 標成 VERIFIED 必須有 `dependencies`,而且那些檔要真的存在。**
   工具會擋下「VERIFIED 但沒有任何驗證依據」的事實 —— 那種事實在查詢時只能被
   誠實降級,等於宣稱驗過卻驗不了。沒把握就讓它是 `CANDIDATE`。
2. **domain 語意不要用 `--kind knowledge` 自行確認。** 從程式碼推出來的語意一律
   落成 `CANDIDATE` + `code_inference`;要成為已確認的業務語意,走 `dev-talk`
   讓使用者點頭。
3. **這次沒學到東西是正常的。** checkpoint 回 `promoted: 0` 是合法結果,
   **不要為了「有記一筆」而硬記一筆「本次完成」** —— 那種紀錄沒有資訊量,
   只會把 `.dev-flow/` 稀釋成沒人讀的流水帳。

中途放棄(使用者喊停 / 走不下去):跑
`dev-memory.py abort $MEMORY_SESSION_ID --reason "<原因>"`,
讓 session 狀態明寫 `ABORTED`。**不要就這樣不管它** —— 留一個永遠 OPEN 的
session,下次回顧時分不出「還在做」與「早就放棄」。

## 並行模式(execution.mode: parallel)—— wave 派工迴圈

你(派工者)坐鎮 **integration worktree**(branch `integration/<slug>`,自 feature base
建立);每個 T 在自己的 task worktree(branch `task/<slug>/T-n`)執行。CLI 是唯一狀態
寫者 —— 你與 Worker 都不得手改 `.devflow/`(Worker 僅恆許 `.devflow/task/<T-id>/`
evidence 專區)。模型分層/升階/失敗分類/嘗試上限與 sequential 完全同一套(上表)。

### 起手

1. `devflow-exec.sh parallel-init <slug>`(釘 feature_initial_base 與契約 hash;
   OC-4:4-spec Profile `lane: fast` + `Risk: high` 在 init 與每次 start 一律被拒,
   除非 4-spec 留有 Owner Call 例外記錄)。
2. 建 integration branch(`git branch integration/<slug>`)並 checkout 之。
3. `devflow-exec.sh plan <slug>` → 雙 DAG(execution = Blocked-by;integration =
   Blocked-by ∪ Integrate-after)與預估 waves。

### 每個 Wave

1. `devflow-exec.sh wave-open <slug>` → 成員清單 + `wave_base_sha`(**同 Wave 同 Base**,
   OC-3)。
2. 逐成員 T 準備:`git worktree add <repo>-task-<slug>-T-n <wave_base_sha>
   -b task/<slug>/T-n`(目錄已存在 → 拒,不 force reset;rework 回原 branch 不開新樹)
   → 進該樹 `devflow-exec.sh start <slug> --task T-n --wave <N> --base <wave_base_sha>`
   → 回 integration 樹 `task-state <slug> T-n RUNNING` → 派 Worker(Task Context
   Packet,見下)。同 wave 成員可真並行(檔案不重疊 + 無語意衝突已由排程保證)。
3. Worker 回報(RED/GREEN/Verify 原文齊)→ **你**在 task worktree commit candidate
   (執行者不 commit 不變;candidate 只落 task branch)→ 該樹 `devflow-exec.sh
   candidate <sha>` + integration 樹 `task-candidate <slug> T-n <sha>`。
4. **Mechanical Gate**(14 項機械檢查,無語意判斷):`devflow-exec.sh gate
   --slug <slug> --task T-n --candidate-json <task 樹>/.devflow/task/T-n/candidate.json`。
   FAIL → `task-rework <slug> T-n` + failed check 清單作 finding 回**原 Worker**
   (升階照常計);PASS → `task-state <slug> T-n MECHANICAL_PASS`。
5. Review 路徑(缺省 normal→wave、high→dedicated;`Risk: high` 配 wave 是解析期錯誤):
   - dedicated:`task-state ... IN_REVIEW` → 派 fresh reviewer 單獨審(給 T + S 原文 +
     diff + 執行者輸出,不給結論)→ PASS 才 `task-state ... QUEUED_FOR_INTEGRATION`。
   - wave:直接 `task-state ... QUEUED_FOR_INTEGRATION`(review 在整合後整批做)。
6. 整合(**你**做,按 integration DAG 拓撲序,同序位按 T 編號):在 integration 樹
   `git cherry-pick <candidate_sha>` → 跑該 T Verify → `task-integrate <slug> T-n`。
   **cherry-pick conflict 你不得親修**(五律 2):`task-rework <slug> T-n --reason
   "<conflict 原文>"`,conflict 原文作 finding 回原 Worker;rework 產新 candidate
   重過 Gate。
7. wave 全員 INTEGRATED → 跑 wave regression(既有全套 + 本 wave 全部 Verify)→
   派 fresh **Wave Reviewer**,輸出必須是 `devflow-wave-review.v1`(wave 內**每 T
   獨立 verdict**、每 finding 帶 task 歸屬、`integration_verdict`;缺一 = 無效)→
   `devflow-exec.sh review <slug> --file <review.json>` 驗結構,無效 = 整份重審。
8. 逐 T 收斂:PASS → `task-state ... IN_REVIEW` → `task-state ... ACCEPTED` →
   **你記帳**(勾 checkbox / T Review Log / Progress Log / TDD Evidence 謄錄 /
   執行軌跡 —— **只有 ACCEPTED 才勾**,單寫者 = 你);FAIL → `task-rework` +
   finding 回原 Worker(先分類 SPEC/ENV/IMPL/UNKNOWN 再路由,同 sequential)。
9. `devflow-exec.sh wave-close <slug>`(REWORK 未收斂者順延下一 wave,自新 Wave Base
   重建)→ 回 1;無 wave 可開 = 全 T 完成 → 併行收尾。

### 步驟 → 事件對照表(上面九步各自要寫哪些事件)

上面九步只講業務動作;事件何時寫、寫哪幾筆、帶什麼必附欄位,查下表(通道規則見
「事件寫入通道」節,prompt 物件一律取 registry 現值)。步驟 1、6、9 不寫事件。

| 步驟 | 觸發時點 | 事件 | 必附欄位 / 條件 |
|---|---|---|---|
| 2(派 Worker) | 每個 Worker 派出時 | `agent_dispatched` + `attempt_started` | prompt 取 registry 現值(同「事件寫入通道」節) |
| 3(commit candidate) | candidate commit 後 | `candidate_created` | 帶 `candidate_sha` |
| 4(Mechanical Gate) | gate FAIL(即該 attempt 的裁決) | `attempt_completed` | result=FAIL,**必附 failure_category** |
| 4(Mechanical Gate) | 同上 | `task_rework_requested` | — |
| 4(Mechanical Gate) | 因此升階重派時 | `task_escalated` | 僅升階時 |
| 5(Review,**僅 dedicated**) | 派 fresh reviewer 時 | `review_started` | wave 路徑不送 |
| 5(Review,**僅 dedicated**) | 收到 verdict | `review_completed` | 帶 `review_verdict` |
| 5(Review,**僅 dedicated**) | 收到 verdict | `finding_created` | 每個 finding 一筆 |
| 7(Wave Reviewer) | 派 Wave Reviewer 時 | `review_started` | — |
| 7(Wave Reviewer) | 收到 verdict | `review_completed` | — |
| 7(Wave Reviewer) | 收到 verdict | `finding_created` | 每個 finding 一筆,帶 task 歸屬 |
| 8(逐 T 收斂,PASS) | PASS 裁決後 | `attempt_completed` | result=PASS |
| 8(逐 T 收斂,PASS) | 同上 | `task_accepted` | — |
| 8(逐 T 收斂,FAIL) | FAIL 裁決後 | `attempt_completed` | **必附 failure_category** |
| 8(逐 T 收斂,FAIL) | 同上 | `task_rework_requested` | — |
| 8(逐 T 收斂,FAIL,若升階) | 升階時 | `task_escalated` | 僅升階時 |

### Task Context Packet(派 Worker 的 prompt;缺一不派)

run_id(start 輸出)、slug、T-id/標題/Intent、Covers 的 R/S **原文** + Test Skeleton、
Operational Context、Allowed Files(= 該 T Files)、Verify 指令、Blocked-by /
Integrate-after / Risk / Review-mode、Boundaries、living spec 節錄、相關 interface
定義、可模仿 pattern 片段、wave_base_sha、contract hash(start 輸出)、Prompt
ID/Version、回報格式(diff 摘要 + RED/GREEN 原文 + 測試名含 S-id + 自由選擇清單 +
卡關點)。Packet 內明令(守衛同步機械強制):禁讀 1/2/3;禁碰 5-tasks / 6-notes /
STATUS / HTML twin(單寫者 = 派工者);禁碰他 T 的檔案與 worktree;禁 commit;
evidence 只落 `.devflow/task/T-n/`(RED/GREEN/Verify log + candidate.json)。

派工 prompt 的 Task Context Packet 只帶該 T 相關之 4-spec Operational Context
最小子集:Actor / Goal / Human decision / Authority / External dependency /
Out-of-system action / Waiting-timeout 與 Recovery / 不得誤導使用者事項。
禁引 1-discussion 原文或訪談逐字稿;T 未涉人機互動 → 不帶 Operational Context。
(語意正本:方法論 `notes/design/real-world-interaction.md` §6。)

### Rework 與上游失效(OC-3)

- rework 且上游未變:回**原 task branch** 出新 candidate(仍用**原 wave base**),
  重過 Gate;candidate 不可變 —— 新 commit 新 candidate,不 amend、不 force-push。
- 上游(已整合/已接受)candidate 被替換:CLI 自動把下游未整合 candidate 標
  `INVALIDATED_BY_UPSTREAM` —— **不得續審、不得整合**;`task-rework` 後等下一次
  `wave-open` 從**新 Wave Base** 重建。推翻已 ACCEPTED 的 T 屬 Owner 裁決
  (`task-rework ... --owner-call "..."` 留痕)。
- 已整合 T 被打回且 `rebuild_integration_on_rework: true`:`rebuild-plan <slug>` 給出
  base + ordered candidate 清單,integration branch 自 base 重建按序重放(每放一個
  跑該 T Verify);`false` → 只 revert 該 T(快速路徑,風險自負)。

### 收尾(並行)

全 T ACCEPTED → 你在 integration 樹跑回歸(全綠)→ 6-notes Self-Review → bookkeeping
commit → 各 task worktree `devflow-exec.sh stop` + `git worktree remove`(乾淨才移,
不 --force)→ integration branch 依 repo 慣例合回 feature branch → **發布最終成果:
integration 合回 feature branch 之後、回報 Stage 7 之前,push feature branch 到
remote,再 `git fetch` 驗證 remote tip 等於當下 feature HEAD;push 或驗證失敗就停在
這裡,不得宣稱 Stage 6 完成**(理由同 sequential 收尾:remote ref 是補修計算的座標)
→ 回報使用者進 Stage 7(送審前置派工見下節)。7-review 執行記錄表另加:wave 數 / gate FAIL 分佈 /
rework 與 invalidation 清單。
**寫事件與衍生(W5,同 sequential 收尾)**:`stage_completed`(stage=6)→
`devflow-obs.sh derive`(6-notes 執行軌跡與 7-review 執行記錄由 ledger 衍生,
禁手動雙寫)+ `stats` 摘要 → `run_completed`。

## Stage 7 送審前置(G3 前;sequential 與並行皆適用)

### Operational Walkthrough 派工(P2 條文)

G3 前對涉互動 feature 派 fresh-context reviewer 做 Operational Walkthrough:
自建表(S-id|角色|真實目標|系統操作|系統外步驟|等待/例外|結果)實走一遍;
六查:技術過但人做不完 / 看得到沒決策權 / 等待誤標完成 / 系統外不可追蹤 /
中斷無法恢復 / 資訊過期缺漏並發;結果記 7-review。

### Final Fresh Run 派發(P4 條文;送審前置,順序固定)

1. **改動凍結**:所有程式修改完成;其後任何 code 改動 → 全部重跑,無例外。
2. **清 stale artifacts**:入口腳本起手刪舊 coverage/report(機械執行,非靠紀律;
   gauntlet `--report` 模式先刪後寫)。
3. **綁 source SHA**:起跑時 `git rev-parse HEAD`;Evidence 的 `Source SHA` = 該值;
   gauntlet 呼叫必帶 `--source-sha $(git rev-parse HEAD)`(兩端 ≥7 hex;宣告 ≠ 當下
   = stale,E2 機械擋)。
4. **單一入口**:用 4-spec Verification Profile `Final fresh entry point` 指名的
   persisted 一條命令跑完整驗證;所有 Evidence 數字出自這一次 run,禁混入舊結果。
5. **`--require-layer` 逐層**:Profile Required layers 逐層一個 flag 帶入(同
   7-review 執行清單 2c 的文檔化命令;Required 層 unverified/n-a/缺席 = E7 機械擋)。
6. **Evidence 節驗證**:送審前跑
   `bash docs/dev/tools/devflow-evidence-gauntlet.sh <7-review.md> --source-sha $(git rev-parse HEAD) --review-file --require-layer <Required 層,逐層>`
   全綠;`--review-file` 驗 Standards Axis / Spec Axis / 現象證據 三節在場
   (E11:Gauntlet PASS 不取代雙軸審與現象複驗 —— G3 信心 = Gauntlet + Code Review
   + Operational Walkthrough)。
7. **run-id 對帳**:run 產 run_id;Evidence header 與 ledger 事件同 id 同 SHA
   (經 P3 CLI 通道);對不上 = stale 訊號,依 E2 精神擋。
