---
feature: <slug>
stage: 3-prototype
status: draft
owner:
updated:
---

# 3. 原型(選配;命中觸發判定 → 條件式必要)— <要回答的問題>

> 用途:用 throwaway 實驗回答 2-decision 遺留的技術/UI 疑問。**code 一律進 throwaway
> branch,禁進 main**;純資料實驗(如複製 DB 查驗)→ 產物放 session scratchpad,
> repo 零污染。LOGIC 疑問 → pure module + 最小介面驗證;UI 疑問 → 2-4 個結構
> 不同的 variant(搭 superpowers visual companion 互動挑)。
> 選配的邊界:純後端、無互動風險的 feature 照舊可跳過;命中下方「Stage 3 觸發判定」
> 任一條 → 本階段**條件式必要**。此時仍要跳過 → 必須由人類明示、記 2-decision 流程層
> Owner Call、記錄跳過風險;Agent 不得自行替人決定跳過。
> 涉互動的案子不只產文件:須產**可操作 Demo**(使用者實際點/跑,不是只看靜態說明),
> 以 Demo Script 帶使用者走過,回饋記入 User Demo Feedback,Human verdict 由人類親填。
> Human verdict 即 G2「Demo verdict」錨的輸入(條件正本 README §7):ACCEPTED 必須由
> 人類親填並伴隨 Verdict attestation 行;REVISE / NOT_REVIEWED 不得過 G2;Agent 不得
> 代填,Runtime 拒絕 Agent 自產的 ACCEPTED。
> 本階段固定產出(跑本階段才適用):`3-prototype.md`(本模板全節)+ `3-prototype.html`
> (終態必產;必含 variant 流程/結構圖、Demo Script、User Demo Feedback、Verdict)。
> 跳過本階段 → 兩檔皆不建,跳過決定記 2-decision 流程層 Owner Call。
>
> 執行清單(開場第一動建成 todo;逐步達成「完成 =」才勾;禁跳項、禁併項):
> 0. 定義疑問:引 2-decision 的哪個 Risk/open point;寫清「答案長什麼樣才算回答了」。
>    完成 = Question 節落檔。
> 1. 實驗:code → throwaway branch;純資料實驗 → scratchpad。完成 = Method 節記
>    branch 名/實驗位置與驗法。
> 2. 收證:Result 記答案+證據(輸出摘要/截圖/挑選 events)。完成 = 每個 Question
>    有證據背書。
> 3. 回寫:Verdict 記回寫 2-decision 哪一條 + branch/實驗產物處置(封存/刪),
>    並在 2-decision「確認紀錄」節留一行(prototype 回寫 | 日期)。
>    完成 = 2-decision 對應處已實際更新+留痕。
> 4. 收尾:結構圖節補齊;frontmatter status 改 **approved**(Stage 3 無 gate,
>    回寫完成即終態)、註解**同步為最新事實**(內文說已回寫,註解不得還寫待回寫)。
>    完成 = status=approved 且 frontmatter 與內文零矛盾。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context 逐條判定,命中打 [x]。全未命中且無互動風險 →
     本階段維持選配,可跳過(舊純後端 feature 照舊)。命中任一條 → 條件式必要;
     仍要跳過 → 人類明示 + 2-decision Owner Call + 記跳過風險,Agent 不得代決 -->
- [ ] 有新的前端流程
- [ ] 改變使用者下一步
- [ ] 涉及角色交接
- [ ] 涉及人工核准
- [ ] 涉及等待/退回/逾時
- [ ] 涉及權限差異
- [ ] 涉及系統外動作
- [ ] 涉及多種可行互動設計
- [ ] Stage 1 尚有操作流程不確定性

## Question
<!-- 引 2-decision 哪個 risk / open point -->

## Method
<!-- branch 名;LOGIC: 模組+怎麼驗 / UI: variants 清單 + Demo 形式。
     Demo 形式依功能擇一:可點擊 HTML prototype / 現有前端框架 throwaway route /
     Storybook 或 component demo / 可執行 CLI flow / API mock + 簡易 UI / 狀態流程模擬器。
     Demo 鐵則:不直接變成 production implementation;位於 throwaway branch/prototype
     scope;不污染正式資料;只用假資料或去識別化資料;清楚標示非正式產品程式碼;
     允許使用者實際操作,而不是只看靜態說明。
     Variant 規則(互動問題存在時):至少 2-4 個「結構不同」的 variant ——
     比較不同操作順序 / 不同資訊階層 / 不同決策點 / 不同等待與交接呈現 /
     不同錯誤恢復方式;不能只是同版面換顏色、同流程換字。
     Demo/Variant 分離:有互動風險 → Demo 必要;方案未定(互動設計仍有多個可行
     方向)→ 做 2-4 個結構不同 Variant 供挑選;已有核准 Pattern(互動形已定)→
     1 個 Demo 即可,不必湊 Variant;禁湊數假 Variant(同版面換顏色、同流程換字
     不算 Variant)。
     每個 variant 必含:主要角色、真實目標、入口、關鍵操作、等待狀態、空狀態、
     錯誤狀態、權限不足、資料過期、中斷恢復、系統外下一步 -->

## 結構圖
<!-- variant 流程/結構圖(UI 案每 variant 一張簡圖;LOGIC 案畫模組介面/資料流)。
     判準同 README §6:純線性 → ASCII 半形;方塊+連線 → html 用 SVG(md 留 ASCII 正本) -->

## Demo Script
<!-- 帶使用者走 Demo 的腳本,一個場景一段;場景錨定既有 ID(Stage 3 時通常引
     1-discussion 的 AC-id;4-spec 已存在才用 S-id),不另發新 ID。
     Demo 時不要只問「喜不喜歡」,逐場確認:看到畫面後知道下一步嗎?系統是否暗示了
     不存在的權限?等待狀態是否清楚?系統外交接是否可追蹤?資訊不完整時是否知道
     怎麼辦?能否撤回、重試、改派或恢復? -->

### Scenario <AC-id 或 S-id>
- 使用者角色:
- 真實目標:
- 起始狀態:
- 操作步驟:
- 系統回應:
- 系統外下一步:
- 觀察問題:

## Result
<!-- 答案 + 證據(輸出摘要/截圖/挑選 events) -->

## User Demo Feedback
<!-- Human verdict 規則:
     - Human verdict 不得由 Agent 代答(值由參與 Demo 的人類親自給)。
     - NOT_REVIEWED 不得被 Agent 當成 ACCEPTED;未 Demo = NOT_REVIEWED。
     - REVISE 必須修改後重新 Demo,直到 ACCEPTED 或人類明示中止。
     - ACCEPTED 必須伴隨下方 Verdict attestation 行,由人類親自輸入姓名與日期;
       Agent 禁寫/禁改/禁代填該行 —— 缺行或格式不符,runtime 機械拒收,不得過 G2。
     - committed 範例/測試 fixture 必須含 `test-only human fixture` 字樣;正式判定
       對含該字樣的檔一律拒收(fixture 永遠不可能誤過正式判定)。
     - 互動不確定性未解決(verdict ≠ ACCEPTED)→ 不得偷偷在 Stage 4(4-spec)把互動
       定案;本檔 frontmatter status 不得改 approved -->
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
- Verdict attestation: human:<姓名> @ <YYYY-MM-DD>

## Verdict
<!-- 回寫 2-decision 哪一條;branch 與 Demo 產物處置(封存/刪) -->
