---
feature: <slug>
stage: 3-prototype
status: draft
owner:
updated:
---

# 3. 原型(選配)— <要回答的問題>

> 用途:用 throwaway 實驗回答 2-decision 遺留的技術/UI 疑問。**code 一律進 throwaway
> branch,禁進 main**;純資料實驗(如複製 DB 查驗)→ 產物放 session scratchpad,
> repo 零污染。LOGIC 疑問 → pure module + 最小介面驗證;UI 疑問 → 2-4 個結構
> 不同的 variant(搭 superpowers visual companion 互動挑)。
> 本階段固定產出(跑本階段才適用):`3-prototype.md`(本模板全節)+ `3-prototype.html`
> (終態必產;必含 variant 流程/結構圖、Verdict)。跳過本階段 → 兩檔皆不建,
> 跳過決定記 2-decision 流程層 Owner Call。
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

## Question
<!-- 引 2-decision 哪個 risk / open point -->

## Method
<!-- branch 名;LOGIC: 模組+怎麼驗 / UI: variants 清單 -->

## 結構圖
<!-- variant 流程/結構圖(UI 案每 variant 一張簡圖;LOGIC 案畫模組介面/資料流)。
     判準同 README §6:純線性 → ASCII 半形;方塊+連線 → html 用 SVG(md 留 ASCII 正本) -->

## Result
<!-- 答案 + 證據(輸出摘要/截圖/挑選 events) -->

## Verdict
<!-- 回寫 2-decision 哪一條;branch 處置(封存/刪) -->
