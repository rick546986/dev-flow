# dev-flow — 團隊開發流程 SOP

> 給 4-6 人團隊 + AI 協作的開發流程。
>
> 母版:`~/dev/dev-flow/`。新專案採用:把 `_templates/` 複製進專案 `docs/dev/_templates/`,
> 本 README 複製為 `docs/dev/README.md`,建 `docs/dev/STATUS.md` 與 repo root `CONTEXT.md`。
> 或直接叫 AI:`/dev-flow 初始化這個專案`。

**這是什麼**:一套讓「討論 → 決策 → 規格 → 實作 → 驗證」全程留痕的文檔管線。每個
feature 走 7 份文檔、過 3 道 gate(G1 方向核准、G2 契約審查、G3 驗證出貨),AI 負責
產出、人負責裁決。解決的痛:需求討論完就散、spec 與程式碼漂移、AI 改動無法審計、
決策半年後沒人記得為什麼。

**怎麼逛這個 repo**:

- 本 README = 制度正本(7 階段規則、gate 條件、切片與大案規則)——往下讀就是全部規則
- `_templates/` = 七份階段文檔 + STATUS/CONTEXT/ADR/living-spec 模板
- `example/contract-expiry-reminder/` = 一個 feature 從討論到驗證走完全程的真實形狀
- 圖解導覽(線上看):[quickstart](https://rick546986.github.io/dev-flow/guide-quickstart.html)、
  [dev-flow](https://rick546986.github.io/dev-flow/guide-dev-flow.html)、
  [dev-talk](https://rick546986.github.io/dev-flow/guide-dev-talk.html)
  ——repo 內任一 html(含 example 的 twin)都可把路徑接在 `rick546986.github.io/dev-flow/` 後線上檢視

**採用方式**:最低配是把模板複製進專案、人工照本 README 走流程;搭配 Claude Code 的
dev-flow / dev-talk plugin 可用 `/dev-talk`、`/dev-flow` 指令自動導引與守衛(plugin
目前未隨本 repo 發佈)。

## 0. 一張圖

```mermaid
flowchart LR
    idea([需求/想法]) --> s1[1 討論<br/>發散]
    s1 --> s2[2 收斂<br/>決策]
    s2 -- G1 過 --> s3{{3 原型<br/>選配}}
    s3 --> s4[4 規格<br/>change spec]
    s2 -- G1 過·無技術疑問 --> s4
    s4 -- G2 reviewer 核准 --> s5[5 任務]
    s5 --> s6[6 實作<br/>TDD]
    s6 --> s7[7 驗證]
    s7 -- G3 PASS --> pr[PR → develop]
    pr --> merge[延伸 living spec<br/>docs/specs/]
```

## 1. 文件地圖(四象限 + STATUS 看板)

| 檔 | 回答什麼 | 生命週期 | 誰寫 / 誰讀 |
|---|---|---|---|
| `CONTEXT.md`(repo root) | 這個詞是什麼意思 | 永生 | 階段1順手維護 / 新人第一讀 |
| `docs/specs/<domain>.md` | 系統**現在**的行為(唯一真相) | 永生,只由階段7出口併入 | 7-Exit / 動這塊前必讀 |
| `docs/adr/NNNN-slug.md` | 當初**為何**這樣選 | 永生,可 superseded | 2-decision 晉升 / 想翻案的人 |
| `docs/dev/STATUS.md` | 誰正在做什麼、到哪一階段 | 常駐看板 | 每過 gate 更新 / 全隊 |
| `docs/dev/<feature>/1-7` | 這次變更的完整生命週期 | ship 後封存 | 流程產出 / reviewer + 考古 |
| `.claude/rules/*.md` | 架構不變量/技術慣例/坑(Claude Code 官方規則路徑,無 `paths` frontmatter 者每 session 自動載入) | 永生 | setup 產草稿 / 全員+執行引擎;**只放 gotchas,禁流程規則(§11),spec 不重抄**;CLAUDE.md 對應段改指標避免雙正本;檔案長大(>~100 行)或多技術棧時可用 `paths:` frontmatter 做 path-scoped 按需載入(判準見模板頂註) |

一句話:**CONTEXT=語言、specs=現況、adr=過去、dev/=進行中**。

**歸位規則**(init 與全程):文檔不散落 `docs/` 根 —— living 規格/規則/資料字典歸
`docs/specs/`、feature 過程檔歸 `docs/dev/<slug>/`、長命決策歸 `docs/adr/`。既有散檔
由 /dev-flow init 偵測,徵得同意後 `git mv` + 同步全部引用(code 註解/文檔/
CLAUDE.md;舊路徑 grep 歸零才算完)。
流程外草稿收編為 `docs/dev/<slug>/0-draft-<名>.md`,只當 Stage 2 原料,不得跳關當 spec。

## 2. 兩軌(lane)

| | Full lane | Fast lane |
|---|---|---|
| 判準 | 新能力 / 不可逆改動(schema、API 契約、跨模組介面) | bugfix / ≤2 檔小改 / 行為已有 spec 條目(可逆的跨模組小改也算) |
| 文檔 | 1→7 全套(3 選配) | `4-spec`(補 bug scenario) → `5-tasks`(mini) → `6-implementation-notes` → `7-review`(mini) |
| Gate | G1 G2 G3 | G3(spec 改動大再補 G2) |

拿不準 → Full。被流程煩到 → 檢討判準,不要繞過流程。

**Fast lane 起手 = 診斷迴圈**(mattpocock×superpowers 聯集):重現 → 最小化 →
假設 → 驗證定位 → 修 → 回歸測試。`4-spec` 的 bug scenario 從「重現步驟」直接長出
(GIVEN=重現前置 / WHEN=觸發 / THEN=正確行為)。修根因,禁 symptom patch。
Fast lane 仍使用同一份 `_templates/5-tasks.md`:可只有一個 T,但必須填
`Covers`、`Files`、`Verify`、`Blocked-by`。Stage 1–3 省略,Stage 5 不省略;
`devflow-exec.sh start <slug>` 會逐 T 驗這四欄,並從這份 `5-tasks.md` 解析 Git repository
root 相對的 `Files` scope。

## 3. 七份文檔(用途一句話;骨架見 `_templates/`,填好範例見 `example/`)

| # | 檔 | 用途 | Gate |
|---|---|---|---|
| 1 | `1-discussion.md` | 發散:把「不知道自己不知道」變成可收斂的問題清單。不做決定 | Open Questions 全解或明標假設 |
| 2 | `2-decision.md` | 收斂:2-3 方案比較 → 選定 + rejected + 理由 | **G1** 方向核准 + OC 全裁決(全文見 §7) |
| 3 | `3-prototype.md` | 選配:throwaway 實驗回答技術/UI 疑問,答案回寫 2;命中觸發判定(前端/交接/核准/等待/權限/系統外/多互動設計)→ 條件式必要,產可操作 Demo + User Demo Feedback(Human verdict 人類親填) | 答案回寫 2-decision + frontmatter 收尾同步(終態 approved) |
| 4 | `4-spec.md` | 本次變更的可測契約(delta + GIVEN/WHEN/THEN)。SDD 真相 | **G2** R/S 全審 + DD 全裁決 + Verification Profile + Demo verdict(全文見 §7) |
| 5 | `5-tasks.md` | 切成可勾選任務,tracer-bullet 順序,每 T 有 Covers/Files/Verify/Blocked-by | 每 T 欄位完整 |
| 6 | `6-implementation-notes.md` | 實作日誌:TDD 證據 + 偏差記錄 | 每 T review PASS + 全 S 綠 |
| 7 | `7-review.md` + `.html` | 雙軸審 + coverage matrix + Exit checklist | **G3** 本次 S 全綠 + 回歸綠 + 現象證據 + Evidence 契約全過(全文見 §7);PASS → PR |

**執行清單四原則**(Stage 2/3/4/6/7;清單全文住各模板頂註,Stage 1 同款機制內建於
/dev-talk):①開場第一動把清單建成 todo,每步有「完成 =」客觀條件,達成才勾;
②交審前必過自檢步 —— 產物勾稽、附證據,不憑印象;③禁跳項、禁併項;
④完成條件達不成 → 回上游步驟補,不硬過。

## 4. ID 追溯鏈

`R-n`(requirement,4-spec)→ `S-n`(scenario,4-spec)→ `T-n`(task,5-tasks,標 Covers)
→ 測試名含 S-id(6 實作)→ `D-n`(deviation,6)→ `F-n`(finding,7,標影響的 S/T)。

Reviewer 靠這條鏈機械檢查「每條需求都有測試」,不靠肉眼。

裁決用 ID **不入鏈**:`OC-n`(2-decision)、`DD-n`(4-spec)不被 T 實作,不參與
「需求→測試」勾稽;OC 被推翻 = 上游修訂(改 2-decision,連動後續 R/S),非鏈上斷點。

## 5. 實作期鐵則:不打斷、自主推進(源:Anthropic「Finding your unknowns」field guide)

實作中**不打斷問人**,靠三條規則自主推進、事後可稽核。每個 T 一律照同一條
acceptance seam,手動實作與 `dev-run` 不得各自另訂順序:

```text
RED → GREEN → scope check → Verify
→ independent T review
→ PASS
→ commit
→ Progress Log + checkbox + review evidence
```

- **檢查點**:T 在獨立審查 PASS 前一律未完成、不得 commit。reviewer 必須不同於該
  T 的 implementer;優先由適格人類 reviewer 審,否則派 fresh-context reviewer
  Agent。reviewer 必須親自跑該 T 的 Verify,並檢查 Covers、RED→GREEN 證據與
  **該 T 自己的 Files scope**。FAIL 回同一 T 修正後重新送審;尚未取得後續 PASS
  就維持未完成。高風險或 findings 有爭議時可加第二位 reviewer。PASS 後才做一 T
  一 commit(可逐點回滾),再把 hash、checkbox 與 review evidence 寫入 6-notes 的
  Progress Log / T Review Log。
- **分層**:上述是 Stage 6 的逐 T acceptance seam;Stage 7 G3 仍是獨立的 feature-level
  gate,不被 T review 取代或重複。Stage 6 只跑快速 Task-local 驗證,即上述 seam 的
  RED → GREEN → scope check → Verify → independent T review(Test Integrity Check
  是 T review 的檢查清單擴充,不是新階段;「Candidate」僅 parallel 模式使用,
  sequential 案照舊 = 送 T review);mutation/property 等重驗證層屬
  feature 級 Final Fresh Run,**不逐 T 跑**。
- **Decisions**(spec 未載明的自由選擇,如內部命名、資料結構):自己選、記一行入
  6-notes 的 Decisions 節、繼續。不屬偏差,不需回審。
- **偏差兩級**:
  - **L1 計畫內偏差**(不動任何 R/S):選**保守方案** → 記 Deviations(D-n:現象/
    保守選擇/理由/影響)→ **繼續執行**。(= field guide 原版 prompt)
  - **L2 契約偏差**(要改 R/S 或推翻 2-decision):**停**。修訂 `4-spec.md` → 重新
    G2 → 才能繼續。禁止 silent drift —— spec 說謊,SDD 就死了。(本 SOP 加嚴,
    field guide 無此級)
- **起手式**:開 feature branch 才動工;多 feature 並行用 git worktree 隔離,免互踩。
- **Scope guard**:改動檔案 ⊆ 5-tasks 全部 T 的 Files 聯集;Files 一律以 Git repository
  root 為相對根,`internal/x_test.go` 和 `backend-go/internal/x_test.go` 在 monorepo 是不同
  scope。超出 → 依偏差兩級判(不動 R/S = L1 記錄續走;動到 = L2 停)。
- **執行守衛**(機械強制,dev-flow plugin 內建):Stage 6 起手在工作樹跑
  `hooks/devflow-exec.sh start <slug>`(驗 4-spec=approved、逐 T 驗 Covers/Files/Verify/
  Blocked-by、正規化 Files → 產 scope 快照 + 契約 hash)。start 前只容許 scope 內髒檔;
  scope 外的 tracked/untracked/ignored 真實改動一律拒啟,先 commit、還原或改用乾淨 worktree,
  不再收進 baseline。`.DS_Store`、`._*`、`Thumbs.db`、`__pycache__/`、`*.pyc` 是 ambient
  metadata:不進 baseline、不擋 start/post-Bash,也不需 allow;其餘路徑即使被 `.gitignore`
  忽略仍會掃描。旗標存在期間四條 hook 生效:
  `devflow-guard`(PreToolUse Edit|Write|Read:擋改任何 feature 的 1/2/3/4、擋讀 1/2/3、
  擋 scope 外寫入)、`devflow-prebash`(PreToolUse Bash:擋 shell 讀上游與破壞旗標)、
  `devflow-postbash`(PostToolUse Bash:git status 對照 + 內容 hash,抓 shell 寫入)、
  `devtalk-guard`(盲原則掃描)。L1 出口 = `devflow-exec.sh allow <file> --reason`;
  L2 = `stop`。收尾 `stop` 後全部沉睡。自測:`hooks/selftest.sh`(動態發現案例,可重跑)。
  界線:紀律工具非安全沙箱,詳 `dev-setup-record.html`。
- **守衛與並行**:守衛狀態以「當前工作樹」為單位(`.devflow/exec.json` + git-dir sentinel),
  一個工作樹同一時間只武裝一個模組。武裝中他模組 `start` → 一律拒絕(不靜默覆寫);
  同模組重跑 `start` = re-arm,允許(5-tasks 改動後重釘 scope 的正常路徑)。
  **多模組並行的正解是各開 git worktree**:每個 worktree 有獨立 toplevel 與 git-dir,
  守衛互不相見 —— 模組 A 在 worktree 甲跑 Stage 6 時,模組 B 在 worktree 乙寫 spec、
  跑自己的 Stage 6,零互擋。同一工作樹內硬要並行做不到:武裝期間跨 feature 的
  1/2/3/4 契約檔一律受保護(hooks 分不清寫入來自哪個 session,fail-closed)。
  同 feature 內 T 級並行 = 每 T 各開 task worktree(`task/<slug>/T-n`,同 Wave 同
  Base SHA),守衛以 `--task` 釘單 T scope;仍然是「一工作樹一武裝」,不破例。
- **T 級並行(選配,同一 feature 內)**:`5-tasks.md` frontmatter 明寫
  `execution.mode: parallel` 才啟用(缺省 sequential,行為不變)。並行 seam 變體:
  RED → GREEN → scope check → Verify → **Candidate Commit(task branch)→
  Mechanical Gate → 整合(按 integration DAG)→ Wave/Dedicated Review → ACCEPTED**
  → 派工者記帳。核心規則:未 Review 的程式碼可形成隔離 Candidate Commit,但未過
  Review 的 Candidate 不得進正式 integration branch、不得標完成;只有 ACCEPTED
  才勾 checkbox。每 T 一個 task worktree(`task/<slug>/T-n`)+ task-scoped 守衛;
  Worker 不寫 5-tasks/6-notes/STATUS/twin(單寫者 = 派工者)。細節與欄位語意見
  `notes/design/parallel-stage6.md`。全流程一張圖(ASCII 正本;SVG 版見
  `guide-quickstart.html` ③):

  ```text
  Task DAG → Wave Base → Task Worktrees
  → RED/GREEN/Verify(每 T 一個 task worktree,各自跑 seam)
  → Candidate(task branch,不可變)
  → Mechanical Gate(14 項機械檢查)
  → 整合(按 integration DAG)
  → Dedicated Review(Task high,整合前)或 Wave Review(normal,整合後)
  → ACCEPTED(才勾 checkbox、才記帳)
  ```

  跨階段收束(sequential/parallel 皆同;Final Fresh Gauntlet = §7 G3 錨的
  Final Fresh Run + Evidence 契約,SVG 版見 `guide-quickstart.html` ⑥):

  ```text
  ACCEPTED Tasks → Final Fresh Gauntlet → G3
  ```
- **接收審查**(G3 打回時):逐 F 驗證後才動手 —— 同意的改並一句說明為何對;
  不同意的擺論證,不盲改(禁 performative fix)。
- **判級疑義**:分不清 L1/L2 → 一律當 L2。Diff Budget 超支本身非偏差,
  是停下判級的訊號。
- **Demo verdict**(Stage 3→4 流程規則):3-prototype Human verdict ≠ ACCEPTED 的
  互動 S,4-spec 不得將其標記定案(列 Drafting Decisions 待裁決或退回 Stage 3
  重新 Demo)—— 屬 Stage 4 執行清單義務;NOT_REVIEWED ≠ ACCEPTED;
  gate 條件正本見 §7。

**驗證五律**(2026-08 對照 openspec/superpowers/mattpocock/harness-engineering
四家驗證機制後定案;適用 T 執行、T review 與各 gate):

1. **證據 = 原始輸出**:任何「完成/通過/綠了」宣稱必附**原始指令輸出或 檔案:行號**,
   禁「我跑過了」「應該過了」式自陳;review finding 必逐條引用 spec 原文或 diff hunk。
   (源:superpowers Iron Law、mattpocock paste-the-output)
2. **派工者不下場修**:主控(派工者)不得繞過 T review 親自修 finding —— 修復一律
   重派執行者、重新送審;主控 context 保持乾淨,主控親修 = 跳過 review 的漏洞。
   (源:superpowers controller-never-fixes;呼應本 SOP「不下場寫碼」)
3. **反預判禁令**:派工 prompt 禁止出現「不要標記 X」「X 最多算 Minor」「計畫已決定
   所以不算問題」等預先框定 reviewer 判斷的措辭 —— 發現自己正在寫,停手。
   (源:superpowers anti-prejudgment)
4. **HITL 不可代答**:需要人裁決的問題(gate 核准、Owner Call、L2 判定)不得由
   agent 代答或「合理推測使用者會同意」;沒有人的裁決就停在待裁狀態。
   (源:mattpocock wayfinder 反模式)
5. **失敗先分類再路由**:T FAIL 先歸類 —— **SPEC**(T/S 定義有問題)→ L2 停,回 G2;
   **ENV**(環境/依賴壞)→ 修環境重跑,不計升階;**IMPL/UNKNOWN** → 走 §9 升階鏈。
   同 T 總嘗試上限 = 4(haiku 1 + sonnet 2 + opus 1),用盡**強制** adviser 裁決,
   禁無限重試;分類與升階史記 6-notes 執行軌跡。(源:harness-engineering failure
   category + loop budget)

**自判分層**(同字不同義,先分清):
| 名 | 誰拍 | 住哪 |
|---|---|---|
| Decision(方案決策) | **人** | 2-decision |
| Owner Calls(自判裁決) | owner,G1 全裁決 | 2-decision |
| Drafting Decisions(草擬自判) | 模型,G2 全裁決 | 4-spec |
| Split Decisions(拆分自判,選配) | 模型 | 5-tasks |
| Decisions(實作自判) | 模型,7 審對照 | 6-notes |

## 6. HTML twin(可視化)+ Artifact

**重生規則**:md = git 正本,html twin = 衍生視覺版、**隨時可重生**
(dev-talk 內稱「視覺版」,同一物 —— 盲故那邊不用 twin 一詞)。gate 時必產;
**Stage 5 於 tasks 定稿(供 start 解析/派工)時必產、Stage 6 於全 T 完成
(bookkeeping commit 前)必產 —— 1~7 每階段終態皆有 twin,不因「本階段無 gate」省略**;
草稿期遇到**分歧點**(模型自判待裁決、方案分叉)必重生,且「⚠️ 待裁決」區置頂。
你對著 html 在對話裁決(「D-3 ✗,理由…」)→ AI 改 md → html 重生。
`1-discussion.html` 由 /dev-talk 收尾即產(殼在 skill 目錄,防破盲)。

**圖規則(全域)**:每站 html 至少一張圖,**判準看關係形狀**:
- 純線性步驟 / 單層樹 → ASCII(md code block,html `<pre>`,git-diffable;
  **限半形字元** `| - + > < = [ ]` —— 全形框線與中文不參與欄位對齊,瀏覽器 pre
  全形寬度不定必歪,中文只放行首標籤/行尾註)
- 方塊+連線的空間關係(多層模型/時間軸/分支交錯/跨層互動)→ **inline SVG 真圖**
  (block+線條+箭頭)。拿不準 → SVG。
禁外部庫。md 永遠留 ASCII 正本,html 依判準選渲染。
畫法規範(顏色變數/class 約定/佈局紀律,不依賴任何 skill 或本機軟體)見
`_templates/diagram-style.md`;新圖先抄現成範本結構再改節點。

**Per-stage 規格表**:

| twin | 必含圖 | 分歧/自判區 | diff |
|---|---|---|---|
| 1-discussion | 脈絡圖 | OQ+假設 badge、驗收雛形表、Real-world Context 表 | — |
| 2-decision | 方案架構圖(比較期可並排) | Approaches+Rejected、Owner Calls(待裁決置頂) | — |
| 3-prototype | variant 流程/結構圖 | Demo Script、User Demo Feedback(Human verdict 人類親填)、Verdict | — |
| 4-spec | 行為流程圖(R 級) | Drafting Decisions(待裁決置頂) | — |
| 5-tasks | T 依賴 DAG(ASCII 天生適合) | Split Decisions(選配) | — |
| 6-notes | progress 時間線(選配) | Decisions+Deviations 表 | ✅ 每 T commit |
| 7-review | 變更架構圖(動了哪些模組) | F-id 分級表 + **現象證據表**(逐 S 觀測 vs 實跑;前端截圖引 `evidence/`) | ✅ 全 branch |

**Diff 細則**(6/7 的 html):每檔一個 `<details>` 折疊條 —— hover 顯示 stat 摘要
(+N/−N、動到的函式),click 展開完整 diff(紅綠著色);內容必 HTML-escape;
單檔 >400 行截斷留 stat+首段註「完整見 git」;base:6 = 該 T 的 commit,
7 = merge-base(develop)..HEAD。

要對外報告:跟 AI 說「這份 html 上 artifact」→ 發布成連結。
殼檔有兩處副本(`_templates/html-shell.html` 與 dev-talk skill 目錄內),改殼須同步兩處。

## 7. 角色與 Gate

> **本節 = gate 條件(G1/G2/G3)的唯一正本**。改任何 gate 條件先改這裡,再同步
> 三處摘要:①plugin `dev-flow` 的 SKILL.md 階段動作表 ②本 README §3 七份文檔表
> ③對應模板頂註的送審/verdict 步(2-decision/4-spec/7-review)。摘要一律只寫
> 「關鍵條件一句 + 全文見 §7」,不重抄全文;衝突以本節為準。

- **author ≠ approver**:G1/G2/G3 的核准者不可以是該文檔的 owner(四眼原則)。
  無適格人類第二人不豁免下述 Agent fallback;只有前兩種 reviewer 都不可用時,owner
  才得自審 —— reviewers 留空即示無獨立審,留痕即可,不假裝有四眼。
- **審查者產生**:G1/G2/G3 一律依序選 **適格人類 reviewer → fresh-context reviewer
  Agent → owner 自審(有記錄的最後手段)**。Agent 必須是乾淨 context,只給審核對象+基準+回報格式,不給
  作者結論;verdict 與審者身分記 reviewers 欄(如 `[independent-fresh-context-reviewer]`)
  + 檔內留 round 紀錄。owner 自審僅能作為**有記錄的最後手段**,不假裝有四眼。
- **規劃層 git**:接手起手先看 `git status`,working tree 有與本 feature 無關的
  改動 → 回報使用者處置,不與文檔混流;每過一個 gate,把該階段文檔
  (`docs/dev/<slug>/` + STATUS + CONTEXT)commit 一次,只含文檔。尚未開
  feature branch 的規劃階段(1-5),文檔 commit 直接落 develop(純文檔無程式碼,
  低風險;Stage 6 起手式才開 feature branch,見 §5)。
- 機械錨點註記:以下 G1/G2/G3 定義句內的粗體詞組是 gate-consistency 機械比對
  錨(dev-setup check 第 8 項);增改 gate 條件務必加粗,不加粗則不被機械驗證
  涵蓋。
- G1 = 方向對不對(2-decision:方向核准 + **Owner Calls 全裁決**,有未裁決 OC
  不得過;下層內部技術項告知即可,但 reviewer **須抽查下層清單有無該上未上的
  誤放** —— 抽查是規則要求,不是 reviewer 自由心證)。G2 = 契約寫得對不對
  (4-spec:**R/S 全審 + Drafting Decisions 全裁決** + **Verification Profile**
  + **Demo verdict**,有未裁決項不得過;兩錨的條件式定義見下方「G2 錨定義」)。
  G3 = 做出來的對不對(7-review:**本次 S 全綠** **+ 既有測試套件全綠**(回歸義務)
  **+ 現象證據逐 S 相符** + **Evidence 契約全過**(八點定義見下方「G3 錨定義」)——
  reviewer 照 4-spec 的「觀測方式」親自實跑,測試綠不等於看得到它動起來)。
- G2 錨定義(錨句在上;此處為條件式全文):
  - 「Verification Profile」:G2 必須確認 4-spec Verification Profile 已依 lane 正確
    填寫 —— full lane = 完整 Profile(Feature Risk/Failure Model/Negative Constraints/
    Required/Conditional/Explicitly Excluded/Final Fresh Entry Point);fast lane =
    最小 Profile(五欄,見 4-spec 模板);命中「自動升 Full」清單(見 4-spec 模板)
    仍寫 fast → 不得過。`lane: fast` 配 `Risk: high` → Runtime(start 時)、模板檢查
    與 Gate 一律拒絕,例外僅限 Owner Call 明示。
  - 「Demo verdict」(條件式):無 Stage 3 trigger → N/A + 明確原因,可過 G2;
    有 trigger 且完成 Demo → 必須 `Human verdict: ACCEPTED`;REVISE → 不得過 G2,
    必須重做 Demo;NOT_REVIEWED → 不得過 G2;有 trigger 但跳過 → 必須有 Owner Call
    明示。Agent 不得自行填入 ACCEPTED;Runtime 必須拒絕 Agent 自產的 ACCEPTED。
- G3 錨定義:「Evidence 契約全過」= 以下八點全部成立:
  1. Final Fresh Run 綁定目前受審的 source SHA。
  2. 所有 Required Layer = pass。
  3. 所有已觸發的 Conditional Layer = pass。
  4. 不得存在任何 fail。
  5. Required Layer 不得為 unverified 或 n-a。
  6. Explicitly Excluded Layer 可為 n-a,但必須附理由。
  7. Optional Layer 可為 unverified,但必須誠實標示。
  8. Gauntlet PASS 不取代 Standards Axis / Spec Axis / Operational Walkthrough /
     Coverage Matrix / 真實現象複驗。
- frontmatter 是狀態機:`draft → in-review → approved → superseded/shipped`。
- 已知限界(明文接受,不另設機制):①Stage 1 討論期的自判無獨立節(單一機制
  原則,不在 1-discussion 設節)—— 由 2-decision 步 0 接手盤點「連同討論期自判
  一併清點」承接。②OC 的「若被推翻會怎樣」在 G1 時點是預估;4-spec 展開後發現
  代價估錯 → 回頭校準該 OC 的代價欄(不改裁決)。

## 8. 每階段呼叫的技能(AI 對照表)

| 階段 | 呼叫 | 來源 |
|---|---|---|
| 1 討論 | **`/dev-talk`**(獨立 skill,盲下游):三層訪談(盤現況→逼問→發散;方法細節以其 SKILL 為準,收斂半在 Stage 2) | openspec / mattpocock / superpowers |
| 2 收斂 | 2-3 方案並排比較 + 壓測定案(方法內建於 `_templates/2-decision.md` 清單;可搭 mattpocock `grill-me`) | 內建 / mattpocock |
| 3 原型 | throwaway 實驗(code→throwaway branch、資料實驗→scratchpad);UI 疑問做 2-4 個結構不同 variant | 內建 / mattpocock `prototype` |
| 4 規格 | openspec delta 格式手寫(模板已內建) | openspec |
| 5 任務 | tracer-bullet 順序 + Covers/Verify/Blocked-by(模板內建) | 內建 |
| 6 實作 | **由 `/dev-flow` 自動接執行引擎**(對外入口一律 `/dev-flow`,定位到 Stage 6 即自動載入 `dev-run`,使用者不需記第二個指令;haiku 執行→sonnet 審→升階;守衛 `devflow-exec` start/stop)或手動逐 T;TDD 紅綠(每 S-id 先 RED 貼輸出再 GREEN)+ checkbox 追蹤 | 本 plugin / 內建 |
| 7 驗證 | 雙軸審(Standards + Spec)+ 自建 coverage matrix(可搭 mattpocock `code-review`) | 內建 / mattpocock |

> **外部 skill 依賴原則**:方法一律內建於模板執行清單,外部 skill 只當**選配加分**(叫不到不影響流程)。
> 原因:第三方 skill 常自帶終點鏈(跑完強制導向它自己的後續流程),會把本流程拖出七文檔管線;
> 且常駐注入有 context 成本與觸發權衝突。歷史上本 SOP 綜合三家精髓,但**精髓已內化,不依賴其安裝**。

## 9. 模型分層與 effort(AI 執行時)

**這張表是預設約定:各階段自動採用對應模型與 effort,不因一時偏好切換;
要偏離(表內建的升降階除外)須使用者明示同意,並記入該階段文檔
(Stage 6 記 6-notes Decisions / 執行軌跡)。**

| 階段/角色 | 模型 | effort | 備註 |
|---|---|---|---|
| 1 討論(/dev-talk 訪談) | opus(或 fable5) | medium | 一次一問;逐字稿整理可交 sonnet |
| 2 收斂/決策文檔 | opus(或 fable5) | high | 多方案辯論、壓測定案 |
| 3 原型(選配) | sonnet | medium | throwaway 實驗、variant 製作 |
| 4 規格撰寫 | opus(或 fable5) | high | step-by-step delta 生成、反模糊三律 |
| 5 任務拆解 | sonnet | medium | tracer-bullet 順序 + 依賴 DAG |
| 6 派工者(引擎主對話) | opus(或 fable5) | medium | 派工、收驗、commit、記帳;不下場寫碼 |
| 6 T 執行 | **haiku 起步** | low | 錯 1 次升 sonnet(medium);sonnet 同 T 錯 2 次升 opus(high)。同層最多兩次,換方法不歸零;升階帶完整失敗軌跡 |
| 6 T review | **sonnet fresh** | high | 高風險/爭議由 opus 作第二 reviewer |
| 6 Wave review(parallel) | sonnet fresh | high | 一次審一個 wave;**必須**輸出每 T 獨立 verdict + finding 歸屬 + integration verdict |
| 6 Mechanical Gate | (無模型,機械) | — | 14 項檢查全 PASS 才 READY_FOR_INTEGRATION |
| 6 adviser | opus,唯讀 | high | 三層連敗才派;verdict=STOP → L2 |
| 7 驗證產檔/coverage matrix | sonnet | medium | 雙軸審材料準備 |
| G1/G2/G3 審查與 verdict | (不指定模型) | high | 見下條;順序正本在 §7 |

- **G1/G2/G3 審查與 verdict**:依 §7 的人類→fresh-context reviewer Agent→有記錄的
  owner 自審順序;Agent 只要求乾淨 context、審核對象、基準與回報格式,不指定模型。
- **effort 定位**:low = 機械執行(照 spec 寫碼、格式轉換、抄錄);medium = 一般分析
  與產檔;high = 審查、gate 判定、規格生成。原則:**判斷密度越高 effort 越高**;
  執行密度高而判斷密度低的活壓 low。派工工具無 effort 參數時,此欄退化為
  派工 prompt 內明示的思考深度要求。
- **fresh context 鐵則**:一切 review(G1/G2/G3 與 T review)一律開新 agent,給乾淨
  context 與按模板組裝的派工 prompt(審核對象/基準/回報格式),禁止在實作對話內
  自演 reviewer —— 舊 context 汙染 = 審查失效。
- 升階史記 6-notes「執行軌跡」→ 7-review.html 呈現(升階 = spec 品質訊號)。
- 手動(非引擎)實作亦可整段用 sonnet,但 T review 的 fresh context 鐵則不豁免。

## 10. 新 feature 快速上手

1. **討論**:(建議開獨立 session)跟 AI 說 `/dev-talk 我想做 <想法>` → 一次一問
   挖到 Open Questions 收斂,產出 `docs/dev/<feature-slug>/1-discussion.md`
2. `STATUS.md` 加一列(lane / stage / owner)
3. 換 session 說:`/dev-flow 繼續 <feature>` → 初次接手只讀 1-discussion.md
   (續跑則讀 STATUS + frontmatter 定位),按 §8 帶你走。**之後每個階段
   (含 Stage 6 實作)都是同一句指令** —— `/dev-flow` 自動判 stage 接對應動作,
   Stage 6 由它自動載入執行引擎,不需要學 `dev-run`
4. 每過 gate:更新 frontmatter status + STATUS.md + 產 html twin
5. G3 過:走 Exit checklist(PR→develop、delta 併 living spec、標 shipped)

**Session 邊界(哪些階段要另開 session,唯一正本)**:

| 階段 | session | 理由 |
|---|---|---|
| 1 討論 | **必開獨立 session** | 圍欄①討論盲下游;/dev-talk 收尾也會提醒 |
| 2 收斂 | 回主 session | 讀 1-discussion 接手(對話不是契約) |
| 3 原型(選配) | **建議獨立 session** | throwaway 心態,實驗過程不進主線 context,答案只回寫文檔 |
| 4 規格、5 任務 | 同一規劃 session 連走 | G1 後的連續規劃思路 |
| 6 實作 | **建議另開 session** | 規劃 context 不帶入執行;執行者只讀 4/5/6+CONTEXT+living spec(圍欄②機械強制) |
| 7 驗證 | 可同 session | reviewer 本來就是 fresh-context agent(§9 鐵則),隔離在 agent 層,不靠 user session |
| 中斷續跑 | 任何階段可換 | 靠 STATUS.md + frontmatter 定位接力(§13) |

## 11. 資訊隔離(anti-premature-convergence)

LLM 知道「終點要產 plan」就會引導式提問、提早收斂。對策:階段間只用文件交接,
對上游隱藏下游。四道圍欄:

1. **討論盲下游**:`/dev-talk` 全文零提及後續階段;讀取白名單(CONTEXT.md /
   docs/specs/ / 原始碼 / 使用者指名),不進其他文件資料夾、不列目錄 —— 第二個
   feature 起專案內已有 pipeline 檔案,盲靠圍欄不靠運氣。最強用法:獨立 session。
2. **實作盲討論**:implementer 只讀 4/5/6 + CONTEXT + living spec,**禁讀 1/2/3**;
   要翻討論才寫得出來 = spec 不完整 → 回 G2(用隔離測 spec 完整度)。
   誠實界定:此欄對「換人 / fresh subagent 實作」可機械強制;同一人從討論做到
   實作時退化為紀律 —— 一切以 spec 為準,不得引討論內容當依據。
3. **審查防錨定**:reviewer 先自建 Coverage Matrix 再看 Self-Review;author ≠ approver。
4. **Quiz gate**:不可逆改動(schema/API 契約/跨模組介面)merge 前**必做** ——
   AI 出 3-5 題考 approver,全對才 merge;其餘 full lane 選配(approver 可要求),
   fast lane 免。

⚠️ **禁把流程規則寫進專案 CLAUDE.md / AGENTS.md**(每 session 自動注入 = 盲全滅)。
規則只住 `docs/dev/README.md`,由 /dev-flow 需要時自己讀。

界線:盲是**降偏不是密封** —— 封得掉檔案/檔名/git log/skill 互叫;白名單是 prompt
約束非權限硬擋;擋不掉使用者自己提及下游與模型先驗。防的是「本次要產 plan」的
**目標**,不是知識。破盲徵兆(dogfood 盯):討論 agent 主動比方案、提規劃、文檔
冒規格字眼 → 回報修圍欄。

交接鐵則:**文件是唯一通道,對話不是契約**。

## 12. SDD × TDD 雙迴圈(V 對應)

SDD 是脊椎(spec 驅動什麼該做),TDD 是右側驗證(測試證明做對)。左邊每個產物,
右邊都有對應驗證;測試在 4 設計(S 即測試規格)、在 6 執行(ATDD 外圈+單元內圈):

```
1 驗收雛形(怎樣算解決)────────────┐
   2 決策(方案)──────────────┐   │
      4-spec R/S(GWT 契約)──┐ │   │
         5-tasks(工單)──┐   │ │   │
            6 實作 ──────┤   │ │   │
         每T Verify+commit┘   │ │   │
      6 TDD:每 S 先RED後GREEN┘ │   │
   7 Spec Axis(對照方案/契約)──┘   │
7 Quiz + G3 驗收(人確認解決了)─────┘
```

- 外圈(ATDD):每個 S-id → 失敗的驗收測試 → 打綠;測試名含 S-id。
- 內圈:實作中的單元級 red-green,自由發揮。
- 回歸義務見 §7(G3 定義);living spec 全量 S = 天然回歸集。
- 行為不變類驗收 → **golden master** pattern:同輸入,改動前後輸出逐列一致。

## 13. 大案與切片

大案先評估切片可行性(見 §14)。≥3 個可獨立 phase、Diff Budget >15 檔、
跨 repo,都是「可能需要切片」的訊號,不是強制切片條件;這些訊號也不證明
必然存在合法切片接縫。切片仍必須滿足 §14 的架構接縫規則;若無法在不洩漏
片際內部設計的情況下拆分,大 feature 可保留單一 `4 → 5 → 6 → 7` 管線。

長時間與跨 session 工作以 `STATUS.md`、`5-tasks.md`、
`6-implementation-notes.md` 接力;開新 session 不需要第二套執行系統。
無人看管的多 phase orchestration 屬專案層選擇,在 dev-flow 方法之外;
dev-flow 不依賴也不規範外部 orchestration。

## 14. Spec 切片(單份 4-spec 過大時)

- **可行性評估訊號**:除 §13 的大案訊號外,4-spec 起草前估 S 條數
  >~40 條、或 reviewer 預判一次審不動,也都要評估切片。起草中途發現超標,
  同樣回頭評估,不硬撐寫完;但數量只是訊號,不能單獨使切片合法。
- **切點判準**:只能切在「後片只依賴前片的**對外產出**(介面/資料契約),不依賴
  其內部設計」的接縫 —— 切點是架構邊界,不是條數平分;
  repo 分開也不自動成為切片接縫。找不到合法接縫時,保留單一 `4 → 5 → 6 → 7` 管線。
- **管線語義**:切片**不回切上游** —— 1-discussion、2-decision 全片共用一份,
  不因切片拆分;切點只發生於 4-spec 起,每片各自擁有完整 `4-spec → 5-tasks →
  6-notes → 7-review` 生命週期與獨立 G2/G3。
- **STATUS 記法**:一片一行,slug 帶後綴(如 `<slug>-a`、`<slug>-b`),連到片資料夾
  `docs/dev/<slug>-a/`(住各自 4→7);1-discussion、2-decision 仍住母資料夾
  `docs/dev/<slug>/`,母 slug 因無自己的 stage 不單獨佔行。
- **ID 配號(跨片不重號)**:片間 R/S 號段接續,不各自從 1 起 —— 前片用到
  S-38,後片自 S-39 起;coverage 比對(測試名含 S-id)與 living spec 合併靠
  號段唯一辨片,foo-a、foo-b 都從 S-1 起號會讓跨片 coverage 誤判。
- **上游定位(frontmatter,不靠字串猜)**:片資料夾 4-spec frontmatter 明載
  `parent`(如 `parent: docs/dev/<slug>/`),1-discussion/2-decision 由此欄
  定位;禁止用 slug 後綴反推母資料夾 —— 後綴只是人讀命名,不是機械依據。
- **片序**:後片 G2 不得先於前片 G2 —— 前片對外契約未凍結(未過 G2)不得被
  依賴;片可各自獨立出貨(先 A 後 B),feature 整體完成 = 全片 G3 皆過。
- **前片契約變更**:前片對外產出(介面/資料契約)需變更 → 前片回 G2 重審;
  所有依賴該產出的後片逐一 impact review,受影響 R/S 一併重審,不可只改
  前片不通知後片。

## 15. 附錄:跨 repo 與非 feature 入口

**跨 repo feature**(如前後端成對 repo):feature 資料夾住**主 repo**(通常後端),
配對 repo 的 `docs/dev/STATUS.md` 加一列連結過去,不重複建檔。

**非 feature 入口**:架構巡檢/償債機會 → 一樣開 `/dev-talk` 討論,產物同格式。

疑義以本 README 為準;範例看 `example/contract-expiry-reminder/`(填好的完整一輪)。
