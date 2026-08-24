---
name: dev-flow
description: 開發流程 SOP 的唯一對外入口(7 階段路由器,SDD 為主、TDD 驗證;定位到 Stage 6 自動載入 dev-run 引擎)。當使用者說「dev-flow」「繼續 <feature>」「開新 feature」「初始化開發流程」,或對進行中 feature 說「繼續做」「跑下一階段」時啟用。方法論內建於本 plugin repo 根目錄。
---

# dev-flow 路由器

方法包根目錄叫 `DEVFLOW_ROOT`（舊名 `CLAUDE_PLUGIN_ROOT` 當別名，不准刪）。找不到就停，不准猜。

方法論:`${DEVFLOW_ROOT}/`(`README.md` = 完整規則;`_templates/` = 模板;
`example/contract-expiry-reminder/` = 填好的完整範例)。細節疑義**先讀方法論 README**,以它為準。
乘客清單正本一律相對 DEVFLOW_ROOT 的 `_templates/<檔>`。採用專案的 `docs/dev/_templates/` 是散發副本，不是正本。

## 0. 定位與自動路由
讀專案 `docs/dev/STATUS.md` + feature 資料夾各檔 frontmatter → 判斷目前 stage 與 lane。
專案沒有 `docs/dev/` → 初始化:複製方法論 `README.md`、`_templates/` 進 `docs/dev/`,
從 `_templates/STATUS.md` 建 STATUS。**業務語言不再靠 repo root 的 `CONTEXT.md`**——
已確認的語意住可 Git 同步的長期記憶,由 dev-setup 建置、`dev-memory.py ask` 查詢。

**定位後直接接手該 stage 的動作,不要求使用者記第二個指令**:
- stage 1~5、7 → 按 §2 表執行對應階段。
- stage = 6(5-tasks approved、實作未完)→ **讀 `skills/dev-run/SKILL.md`**
  （Claude 別名：Skill tool 載入 `dev-run`）接手逐 T 執行;使用者只需說
  「/dev-flow 繼續 <slug>」。dev-run 是內部引擎,對外文件不要求使用者學它;
  使用者直接喊「dev-run <slug>」仍相容。
- 模型與 effort 依 README §9 對照表自動採用,**不因使用者一句「換個模型」就偏離**:
  偏離(表內建升降階除外)需使用者明示同意,並記入該階段文檔。

**文檔歸位**(init 與全程強制):living → `docs/specs/`、feature 過程 →
`docs/dev/<slug>/`、決策 → `docs/adr/`;散檔徵同意 `git mv` 歸位 + 全引用同步;
流程外草稿收編 `0-draft-<名>.md` 只當 Stage 2 原料。細則見 README §1。

## 1. Lane 判準
- **full**(預設):新能力 / 不可逆改動(schema、API 契約、跨模組介面)→ 1-7 全套(3 選配)。
- **fast**:bugfix / ≤2 檔小改 / 行為已有 spec 條目(可逆的跨模組小改也算)→ 4-spec(補 bug scenario) → 5-tasks(mini) → 6-implementation-notes → 7-review(mini)。Stage 1–3 省略;5-tasks 仍用同一模板,可只有一個 T,但 Covers/Files/Verify/Blocked-by 必填,供 `devflow-exec.sh start <slug>` 解析 scope。起手 = **診斷迴圈**(重現→最小化→假設→定位→修→回歸),bug scenario 從重現步驟長出。
- **大案與切片**:訊號與可切判準一律看 README §13(要不要切)與 §14(切點在哪),本檔不重述 —— 這兩節條件多且互相牽動,摘要過就會與正本分歧。

## 2. 階段動作

| stage | 呼叫技能 | 產出 | gate |
|---|---|---|---|
| 1 討論 | **本 skill 不執行**。討論由 `/dev-talk` 專職(資訊隔離:討論 agent 不知道有後續階段,防直奔結論;最好開獨立 session)。使用者在此要求討論 → 請他改跑 `/dev-talk`,並提醒:討論須收集 **Real-world Context**(人怎麼真的完成這件工作) | `1-discussion.md`(接手時**只讀此檔**,對話不是契約);必含 Real-world Context 節(Actors/Current Journey/Workarounds/Exceptions/Evidence)—— Stage 3 觸發判定與 4-spec Operational Context 的輸入;接手時缺此節 = legacy 檔(§4) | Open Questions 全解或明標假設 |
| 2 收斂 | 2-3 方案並排比較 + 壓測定案(方法內建;可搭 mattpocock `grill-me`);**執行清單見 `_templates/2-decision.md` 頂註**;節點鏈見 `skills/dev-flow/stage2/` | `2-decision.md`;三條件中→抄 `docs/adr/` | **G1** 方向核准 + OC 全裁決(全文見 README §7) |
| 3 原型(選配;命中觸發判定 → 條件式必要) | 開場第一動先做**觸發判定**(§4);throwaway 實驗(code 進 throwaway branch,禁進 main;純資料實驗 → scratchpad);Demo 必要性與 Variant 數量規則見 §4;**執行清單見 `_templates/3-prototype.md` 頂註**;節點鏈見 `skills/dev-flow/stage3/` | `3-prototype.md`(涉互動 → 含可操作 Demo + User Demo Feedback,Human verdict 人類親填 + attestation,見 §4) | 答案回寫 2-decision + frontmatter 收尾同步 |
| 4 規格 | openspec delta 格式,**step-by-step 生成** + **反模糊三律**(S 可轉單一測試、禁模糊詞、禁 TBD);**執行清單與三律見 `_templates/4-spec.md` 頂註**;節點鏈見 `skills/dev-flow/stage4/` | `4-spec.md`(含 Drafting Decisions) | **G2** R/S 全審 + DD 全裁決 + Verification Profile(依 lane 正確填寫)+ Demo verdict 條件(全文見 README §7;Demo verdict 語意正本見 §4 所引,機械檢查 `hooks/_stage3_impl.py`) |
| 5 任務 | `to-tickets` 概念:tracer-bullet 順序 + Covers/Verify/Blocked-by;節點鏈見 `skills/dev-flow/stage5/` | `5-tasks.md` | 每 T 有 Verify |
| 6 實作 | **`dev-run` 引擎**(haiku 執行→sonnet 審→錯誤升階;守衛 `devflow-exec.sh` start/stop,詳其 SKILL;5-tasks 明寫 `execution.mode: parallel` 時走並行引擎(選配))或手動逐 T;兩者共用 README §5 的 T acceptance seam:RED→GREEN→scope check→Verify→獨立 T review→PASS→commit→記 Progress Log/checkbox/review evidence;**執行清單見 `_templates/6-implementation-notes.md` 頂註**;節點鏈見 `skills/dev-flow/stage6/` | `6-implementation-notes.md`(含 T Review Log;執行軌跡只供 dev-run) | 每 T review PASS + 全 S 綠 |
| 7 驗證 | 雙軸審(Standards + Spec)+ 自建 coverage matrix(可搭 mattpocock `code-review`);整合回歸在 Final Fresh 之前(出貨樹=審過的樹);4-spec Required layers 欄必須在(可寫「無」/none/n-a;空值不算零層;層名全等);**執行清單見 `_templates/7-review.md` 頂註**;節點鏈見 `skills/dev-flow/stage7/` | `7-review.md` + `7-review.html` | **G3** 本次 S 全綠 + 回歸綠 + 現象證據 + Evidence 契約全過(全文見 README §7);PASS → Exit Checklist(PR 是其中一項) |

gate 條件唯一正本 = 母版 README §7;本表 gate 欄是摘要,衝突以 §7 為準。

## 3. 鐵則
- **資訊圍欄**(anti-premature-convergence):①討論全盲下游(/dev-talk 不知有後續)。
  ②實作者只准讀 `4-spec`+`5-tasks`+`6-notes`+長期記憶查詢結果+living spec,**禁讀 1/2/3**;
  需要翻討論記錄才寫得出來 = spec 不完整 → 停,回 G2 補 spec。③reviewer 先自建
  coverage matrix,才准看 6 的 Self-Review(防錨定)。④任何派工 context(含 Task
  Context Packet)**禁塞完整訪談逐字稿**;操作脈絡只帶 4-spec Operational Context
  的最小子集,不回引 1-discussion 原文。
- **ID 鏈**:R→S→T→D→F;測試名含 S-id;reviewer 用鏈機械對 coverage。
- **執行清單**:Stage 2/3/4/6/7 開場把模板頂註清單建成 todo,逐步達成「完成 =」才勾,
  交審前過自檢步;禁跳項併項(四原則見 README §3)。
- **實作不打斷**(Anthropic field-guide 模式):手動實作與 `dev-run` 共用 README §5 /
  6-notes 的逐 T acceptance seam;T reviewer 必須不同於 T implementer,review PASS
  才 commit,之後才記 Progress Log / checkbox / review evidence。spec 未載明的自由
  選擇 → 自己選、記 6-notes 的 Decisions 節、繼續。Stage 7 G3 仍另行執行。
- **Scope guard**:改動檔案 ⊆ 5-tasks Files 聯集,超出依 L1/L2 判。G3 的綠 = 本次 S 全綠 + 既有測試全綠(回歸)。
- **驗證五律**(README §5 全文):①完成宣稱必附原始輸出或 檔案:行號;②派工者不
  親修 finding(重派+重審);③派工 prompt 禁預判 reviewer 判斷;④需要人裁決的
  問題禁代答;⑤失敗先分類(SPEC→L2/ENV→重跑不計/IMPL、UNKNOWN→升階),
  同 T 總嘗試 ≤4,用盡強制 adviser。
- **html 重生**:gate 必產;草稿期分歧點隨時重生,「⚠️ 待裁決」置頂(per-stage 規格見 README §6;圖 ASCII 優先)。
- **偏差**:L1(不動 R/S)→ 保守方案 + 記 D-n + 繼續。L2(動 R/S / 翻 decision)→ 停 → 修 4-spec → 重 G2。禁 silent drift。
- **Quiz gate**:不可逆改動 merge 前**必做** —— AI 出 3-5 題考 approver(改了什麼/為何/邊界),全對才 merge;其餘 full lane 選配,fast lane 免。
- **過 gate 三連動**:frontmatter status + STATUS.md + 同名 html twin(`_templates/html-shell.html` 包);使用者說「上 artifact」→ 先載 artifact-design skill,再用 Artifact 發布該 html。
- **git**:feature branch → develop;禁直上 master。規劃層:起手 `git status`,有無關
  改動先回報使用者;每過 gate 該階段文檔 commit 一次(只含文檔)。
- **模型與 effort**:一律照 README §9 對照表自動採用(規劃/派工 opus/fable5、
  T 執行 haiku 起步升階、T review sonnet fresh、其他執行活 sonnet;effort 按判斷密度
  low/medium/high)。偏離表格(內建升降階除外)需使用者明示同意並記入該階段文檔。
- **G1/G2/G3 審查與 verdict**:依 README §7 的人類→fresh-context reviewer Agent→
  有記錄的 owner 自審順序；Agent 只要求乾淨 context、審核對象、基準與回報格式,不指定模型。
- **author ≠ approver**(G1/G2/G3 四眼原則)。審查者依序:適格人類 reviewer →
  fresh-context reviewer Agent → owner 自審(有記錄的最後手段);身分記 reviewers 欄
  (產生程序見 README §7)。

## 4. Stage 3 操作面(觸發判定/Demo/verdict)

行為正本 = 母版 `_templates/3-prototype.md` + `notes/design/vnext-shared-contract.md` §2
(G2 Demo verdict 條件);本節是執行摘要,衝突以正本為準。

- **觸發判定**:Stage 3 開場第一動 —— 對照 1-discussion「Real-world Context」逐條判定
  模板九條觸發條件(新前端流程/改變下一步/角色交接/人工核准/等待退回逾時/權限差異/
  系統外動作/多種互動設計/操作流程不確定),命中打 [x] **落檔**於 3-prototype
  「Stage 3 觸發判定」節。0 命中 → 全未勾清單落檔即為「無 trigger,N/A + 原因」記錄,
  Stage 3 維持選配。命中任一條 → 本階段條件式必要。
- **Demo 必要性**:存在真實世界互動風險(觸發判定命中)→ **可操作 Demo 必要**
  (使用者實際點/跑,不是只看靜態說明;形式六選一與鐵則見模板)。
- **Demo 與 Variant 分離**(兩者條件不同,勿混):
  - 互動方案**尚未決定** → 2-4 個**結構不同** Variant(不同操作順序/資訊階層/決策點/
    等待交接呈現/錯誤恢復),搭可操作 Demo 供人挑。
  - 互動方式**已由既有核准 Pattern 明確決定** → 1 個可操作 Demo 即可,不必多 Variant。
  - **禁**為湊數製作無結構差異的假 Variant(同版面換色、同流程換字不算 Variant)。
- **Human verdict 人類主權**:ACCEPTED/REVISE/NOT_REVIEWED 由參與 Demo 的人類親填;
  未 Demo = NOT_REVIEWED ≠ ACCEPTED;REVISE → 修改後重新 Demo。ACCEPTED 必須伴隨
  人類 attestation 行:`- Verdict attestation: human:<姓名> @ <YYYY-MM-DD>`(緊隨
  Human verdict 行;**由人類親自輸入,Agent 禁寫/禁改/禁代填此行**)。無 attestation
  的 ACCEPTED 會被機械拒收 —— Agent 不得自行填入 ACCEPTED。committed 範例/測試
  fixture 的 verdict 必須含 `test-only human fixture` 字樣(正式判定一律拒收該字樣)。
- **跳過**:命中觸發仍要跳過 → 人類明示,記 2-decision「Owner Calls」節流程層 OC,
  該行同時含「Stage 3」與「跳過」字樣(供機械比對);Agent 不得代決跳過。
- **G2 送審前先跑 spec 形狀檢查**(B-9;Stage 4 步驟 6 送審的前置動作):
  `bash <master>/scripts/check-spec-gate.sh docs/dev/<slug>/4-spec.md`。它查五項,
  一項一條、五項都要過:
  1. 每個 S 有觀測欄。
  2. Verification Profile 節在,且 `- lane:` 與 `- Risk:` 兩行可解析
     (runtime `devflow-exec.sh start` 讀的就是這兩行)。
  3. 若 `lane: fast` 配 `Risk: high` —— 有 `- Owner Call 例外:` 才放行,沒有就拒。
  4. 無模糊詞(全文掃 TBD、之後再說、實作再定;另逐 S 掃反模糊三律清單)。
  5. Drafting Decisions 無殘留「待裁決」。

  **exit 1 = 不得送審**(這支是 Gate,不是 warning-only);exit 0 只代表**形狀**齊,
  R/S 寫得對不對、DD 決策合不合理仍是 reviewer 的事,機械不判語意。
- **G2 Demo verdict 條件**(條件正本 README §7;語意全文 vnext-shared-contract §2):
  無 trigger → N/A + 明確原因可過;有 trigger 完成 Demo → 須 ACCEPTED(+attestation);
  REVISE / NOT_REVIEWED → 不得過;有 trigger 但跳過 → 須 Owner Call 明示。機械檢查:
  `python3 <plugin>/hooks/_stage3_impl.py <slug>`(專案根執行;exit 0 可過 / 2 拒 /
  1 錯誤;stdout JSON `stage3-verdict-v1`)。**legacy 相容**:1-discussion 無
  Real-world Context 節的舊 feature(或 fast lane 無 1/3 檔)→ 明確判 legacy/N-A
  放行,不誤殺、不要求回頭補作業。
