---
name: dev-flow
description: 團隊開發流程 SOP 路由器(7 階段,SDD 為主、TDD 驗證)。當使用者說「dev-flow」「繼續 <feature>」「開新 feature」「初始化開發流程」時啟用。母版在 ~/dev/dev-flow/。
---

# dev-flow 路由器

母版:`~/dev/dev-flow/`(`README.md` = 完整規則;`_templates/` = 模板;
`example/contract-expiry-reminder/` = 填好的完整範例)。細節疑義**先讀母版 README**,以它為準。

## 0. 定位
讀專案 `docs/dev/STATUS.md` + feature 資料夾各檔 frontmatter → 判斷目前 stage 與 lane。
專案沒有 `docs/dev/` → 初始化:複製母版 `README.md`、`_templates/` 進 `docs/dev/`,
從 `_templates/STATUS.md` 建 STATUS,repo root 沒 `CONTEXT.md` 則從模板建。

**文檔歸位**(init 與全程強制):living → `docs/specs/`、feature 過程 →
`docs/dev/<slug>/`、決策 → `docs/adr/`;散檔徵同意 `git mv` 歸位 + 全引用同步;
流程外草稿收編 `0-draft-<名>.md` 只當 Stage 2 原料。細則見 README §1。

## 1. Lane 判準
- **full**(預設):新能力 / 不可逆改動(schema、API 契約、跨模組介面)→ 1-7 全套(3 選配)。
- **fast**:bugfix / ≤2 檔小改 / 行為已有 spec 條目 → 只做 4-spec(補 bug scenario)+ 6-implementation-notes + 7-review(mini)。起手 = **診斷迴圈**(重現→最小化→假設→定位→修→回歸),bug scenario 從重現步驟長出。
- **引擎分流**:預設 Stage 6;大案(≥3 phase / >15 檔 / 跨 repo)可轉 harness(README §13 對照表),一 feature 一引擎。

## 2. 階段動作

| stage | 呼叫技能 | 產出 | gate |
|---|---|---|---|
| 1 討論 | **本 skill 不執行**。討論由 `/dev-talk` 專職(資訊隔離:討論 agent 不知道有後續階段,防直奔結論;最好開獨立 session)。使用者在此要求討論 → 請他改跑 `/dev-talk` | `1-discussion.md`(接手時**只讀此檔**,對話不是契約) | Open Questions 全解或明標假設 |
| 2 收斂 | `brainstorming`(2-3 approaches)+ `grill-me` 壓測;**執行清單見 `_templates/2-decision.md` 頂註** | `2-decision.md`;三條件中→抄 `docs/adr/` | **G1** reviewers 核准(≠owner) |
| 3 原型(選配) | mattpocock `prototype`(code 進 throwaway branch,禁進 main;純資料實驗 → scratchpad)+ superpowers visual companion(UI 2-4 variants 互動挑);**執行清單見 `_templates/3-prototype.md` 頂註** | `3-prototype.md` | 答案回寫 2-decision + frontmatter 收尾同步 |
| 4 規格 | openspec delta 格式,**step-by-step 生成** + **反模糊三律**(S 可轉單一測試、禁模糊詞、禁 TBD);**執行清單與三律見 `_templates/4-spec.md` 頂註** | `4-spec.md`(含 Drafting Decisions) | **G2**:R/S 全審 + 自判全裁決 + 逐 S「fresh 工程師寫得出測試嗎」 |
| 5 任務 | `to-tickets` 概念:tracer-bullet 順序 + Covers/Verify/Blocked-by | `5-tasks.md` | 每 T 有 Verify |
| 6 實作 | mattpocock `implement` 骨架(逐 T 消化)× superpowers `test-driven-development`(每 S-id 先 RED 貼輸出再 GREEN)× openspec checkbox 勾進度;多 T 可走 subagent-driven(每 T fresh subagent);**執行清單見 `_templates/6-implementation-notes.md` 頂註** | `6-implementation-notes.md` | 全 S 綠 |
| 7 驗證 | mattpocock `code-review` 雙軸 + coverage matrix;**執行清單見 `_templates/7-review.md` 頂註** | `7-review.md` + `7-review.html` | **G3** PASS → Exit checklist |

## 3. 鐵則
- **資訊圍欄**(anti-premature-convergence):①討論全盲下游(/dev-talk 不知有後續)。
  ②實作者只准讀 `4-spec`+`5-tasks`+`6-notes`+`CONTEXT.md`+living spec,**禁讀 1/2/3**;
  需要翻討論記錄才寫得出來 = spec 不完整 → 停,回 G2 補 spec。③reviewer 先自建
  coverage matrix,才准看 6 的 Self-Review(防錨定)。
- **ID 鏈**:R→S→T→D→F;測試名含 S-id;reviewer 用鏈機械對 coverage。
- **執行清單**:Stage 2/3/4/6/7 開場把模板頂註清單建成 todo,逐步達成「完成 =」才勾,
  交審前過自檢步;禁跳項併項(四原則見 README §3)。
- **實作不打斷**(Anthropic field-guide 模式):檢查點 = 一 T 一 commit(Verify 綠才 commit,Progress Log 附 hash);spec 未載明的自由選擇 → 自己選、記 6-notes 的 Decisions 節、繼續。
- **Scope guard**:改動檔案 ⊆ 5-tasks Files 聯集,超出依 L1/L2 判。G3 的綠 = 本次 S 全綠 + 既有測試全綠(回歸)。
- **html 重生**:gate 必產;草稿期分歧點隨時重生,「⚠️ 待裁決」置頂(per-stage 規格見 README §6;圖 ASCII 優先)。
- **偏差**:L1(不動 R/S)→ 保守方案 + 記 D-n + 繼續。L2(動 R/S / 翻 decision)→ 停 → 修 4-spec → 重 G2。禁 silent drift。
- **Quiz gate**:不可逆改動 merge 前**必做** —— AI 出 3-5 題考 approver(改了什麼/為何/邊界),全對才 merge;其餘 full lane 選配,fast lane 免。
- **過 gate 三連動**:frontmatter status + STATUS.md + 同名 html twin(`_templates/html-shell.html` 包);使用者說「上 artifact」→ 先載 artifact-design skill,再用 Artifact 發布該 html。
- **git**:feature branch → develop;禁直上 master。規劃層:起手 `git status`,有無關
  改動先回報使用者;每過 gate 該階段文檔 commit 一次(只含文檔)。
- **模型**:規劃層(2/4 文檔、G1/G2/G3 審查與 verdict)= **opus**;執行層(3/5/6/7 產出與實作)= **sonnet**。
- **author ≠ approver**(G1/G2/G3 四眼原則)。無適格人類第二人 → 派 fresh-context
  reviewer agent(opus)審,身分記 reviewers 欄(產生程序見 README §7)。
