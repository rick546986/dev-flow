---
feature: <slug>
stage: 1-discussion
status: draft        # draft | in-review | approved | superseded | shipped
owner:
reviewers: []
updated:
---

# 1. 討論 — <feature 標題>

> 用途:發散。把「還不知道自己不知道什麼」變成一張可收斂的問題清單。**不做決定**。
> 產生方式:由 `/dev-talk` 盲產。本階段固定產出:`1-discussion.md` +
> `1-discussion.html`。不多不少。
> 掃頁六件仍走 `scripts/build-scan-html.py`(S10,html-shell)。審頁另一支:
> `scripts/build-stage1-html.py`(--action 授權;吐 `.sum#scan-sum`／`#scan-now`
> 直式三框 viewBox 200×420／`.now-wrap` 置中／`#scan-people`;現況圖吃無標籤
> 四行堆＋`|` 分隔)。正本
> `notes/design/stage1-review-ui-contract.md`。不要改掃頁產生器來充審頁,
> 不要手包 html-shell。
> 可選目錄樹:專案大、接手、跨模組、或人要看檔案脈絡時,才用方法包
> `scripts/build-dir-tree.py` 畫可摺疊目錄樹(契約
> `notes/design/dir-tree-contract.md`)。落在本 feat 的
> `docs/dev/<slug>/dir-tree.html`,不要寫進 `1-discussion.html`、
> 不要跟掃頁三框搶槽。不是每案必跑,不進 gate、不改 hop。

## Problem
<!-- 1-3 句:誰、遇到什麼痛、現在怎麼繞過 -->

## Context(已知事實)
<!-- 現況行為引用 docs/specs/<domain>.md;相關程式碼位置;數據。事實查了寫這,不留在腦裡 -->

## Real-world Context
<!-- 捕捉「人怎麼真的完成這件工作」:誰、在什麼情境用、掌握/缺少哪些資訊、要等誰、
     有哪些權限、用哪些系統外工具、如何中斷/恢復/退回/例外。
     此節是 Stage 3 觸發判定(見 3-prototype 模板)與 4-spec Operational Context 的輸入。
     訪談規則:
     - 優先問「最近一次真的發生時怎麼處理」,不只問理想流程。
     - 正式 SOP 與實際做法不同時,兩者都記。
     - 未有證據的內容標 [Assumption];不得把推測寫成事實。
     - 涉及醫療/個資 → 只保存去識別化內容。
     ID 規則:單一 ID 鏈 R → S → T → test → D → F 不變;不另發 Journey/Actor/Interaction
     專屬 ID,真實世界資訊以本節文字附著,後續由 4-spec Operational Context 附著於 S-id -->

### Actors
<!-- 系統外角色(如外部窗口、不進系統的審核者)也要列,權限欄寫「系統外」 -->
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|

### Current Journey
<!-- 沒有這個功能時的現況旅程,一步一列;正式 SOP 與實際做法不同 → 各記一段,都留 -->
| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|

### Workarounds
<!-- 沒有這個功能時,實際怎麼完成?是否使用 Excel、LINE、Email、紙本、電話或口頭交接?
     哪些步驟沒有留下紀錄? -->

### Exceptions
<!-- 哪些情況不走標準流程?誰可以跳過?資料不完整怎麼辦?對方不回覆怎麼辦?
     操作中斷怎麼恢復?是否可能重複、撤回、改派或多人同時處理? -->

### Evidence
<!-- 逐條列證據來源:實際案例 / 訪談 / SOP / 去識別化 log / 表單 / 畫面 / 客服或使用者問題。
     沒有證據支撐的敘述標 [Assumption] 列於此節或就地標注,與有證據項可機械區分 -->

## Goals
<!-- 條列,可驗證的「想達成」 -->

## Non-Goals(初稿)
<!-- 明確不做,防範圍蔓延;4-spec 定稿 -->

## Open Questions
<!-- 三態:[x] 已解 / [~] 帶假設(使用者明說先這樣)/ [>] 移交(本討論不解,留待後續)。
     全數落入三態之一才算討論完成 -->
- [x] Q1:…(已解,推理見 Interview Log)
- [~] Q2:…(帶假設:使用者明說先這樣,暫定值=…)
- [>] Q3:…(移交後續,本討論不解)

## Constraints
<!-- 技術/時程/法規限制 -->

## 驗收雛形
<!-- 每條 Goal 翻成 1-3 條可驗證敘述(假設…當…則…),使用者視角、不綁實作方式。
     需求層判準;方案層驗收由後續階段補。這裡的敘述是 4-spec Scenario 的種子。
     每條附「觀測方式」三件 —— 從哪看 / 看到什麼算對 / 拿什麼資料試:
     - AC-1:假設<前置>,當<動作>,則<結果>
       - 從哪看:<畫面路徑 | API 端點 | log | 產出檔>
       - 看到什麼算對:<具體值/字樣/狀態,不是「正常顯示」這種模糊詞>
       - 拿什麼試:<現成真實資料識別;無則註明需造資料> -->

## 邏輯圖(ASCII)
<!-- 核心邏輯/分支的 ASCII 圖(code block);簡單案這張就夠,html 視覺版直接 <pre> 收錄。
     限半形字元(| - + > < = [ ]);全形框線與中文不參與欄位對齊(瀏覽器 pre 會歪) -->

## Interview Log(推理鏈外顯)
<!-- 每條:Q → 事實依據 → 推理 → 結論。不只記結論,要能驗證推理 -->
<!-- 層1 盤現況確認的事實、層3 what-if 推演與盲點戰果也記於此 -->
- Q:… | 事實:… | 推理:… | 結論:…
