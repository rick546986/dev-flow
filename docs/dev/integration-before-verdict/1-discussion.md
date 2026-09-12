---
feature: integration-before-verdict
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-12
---

# 1. 討論 — 整合回歸須在 Fresh／Verdict 之前

> 用途:發散。**不做決定**。本場依 owner 2026-09-12 書面 brief 落檔,不是現場一問一答。
> Lane = **full**。本 hop **不送 G1**。未核敘述標 `[Assumption]`。
> A-1 已裁:Goals 只寫結果;Requested solution 另節。

## Problem
痛:Stage 7 若 Fresh→Verdict→Exit 才合 `INTEGRATION_SHA`,核准樹不是出貨樹;`ALREADY_SYNCED` 只寫「證據不算數」就能過。
現在怎麼繞:人記得先合再 Fresh;或 Exit 才合;或只記一句作廢。

## Context(已知事實)
- v3.8.0 收尾把「整合移到 Fresh／雙軸／Verdict 之前」列成獨立 full-lane 題,並禁在該輪改 `_templates/7-review.md`:notes/dispatch-v380-landing.md:L1011-L1018 notes/dispatch-v380-landing.md:L1039-L1040
- 派工寫的舊節序是 Fresh(`:94`)→ Verdict(`:133`)→ Exit 同步(`:281`),且 `ALREADY_SYNCED`(`:291`)只說證據不算數:notes/dispatch-v380-landing.md:L1011-L1018
- 本 working tree 的 7-review 頂註已寫「出貨樹=審過的樹」、2c 整合在 2d Fresh 之前、`ALREADY_SYNCED` 有恢復路徑、Verdict 後禁改碼: _templates/7-review.md:L30-L31 _templates/7-review.md:L100-L120 _templates/7-review.md:L110-L113 _templates/7-review.md:L176-L177
- Exit 條已寫「整合回歸已在 Final Fresh 之前完成」、Verdict 後不得在 Exit 補碼或合併: _templates/7-review.md:L330-L333
- 指南 renderer 抄本與 Stage 7 節點鏈也是 2c→2d,不是 Fresh 完才合:guides/guide-dev-flow.html:L1718-L1738 skills/dev-flow/SKILL.md:L49 skills/dev-flow/stage7/nodes/S2c-integration.md:L24-L25 skills/dev-flow/stage7/nodes/S2d-fresh.md:L5-L6
- 完整範例仍把「執行清單 2c」寫成 Final Fresh Run(舊編號):example/contract-expiry-reminder/7-review.md:L24
- 本 landing 把此題列入 Active(Stage 1、G1 未過);九條 Backlog 改為已裁決指標:docs/dev/STATUS.md:L34 docs/dev/STATUS.md:L52
- owner 2026-09-12:本 slug 走 full;整合在 Fresh／雙軸／Verdict 之前;本 hop 只 Stage 1、不送 G1

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| owner | 第一條真實 full lane;出貨樹=核准樹 | 裁 lane／G1–G3 | 派工裁決、本 tree 模板 | 機械錨是否真鎖節序 | GitHub、PR |
| Stage 7 reviewer | 在將出貨的那棵樹上做 G3 | 寫 7-review;可改 HEAD 僅限整合步 | 清單與腳本輸出 | 合完後 Fresh 是否重綁 | 終端機、整合腳本 |
| 實作者 | 照清單順序做完、不被事後合進未審 commit | 改 feature 樹 | 6-notes 錨點 | 別人是否在整合分支繼續合 | git |
| merger | 合的是腳本印出的 INTEGRATION_SHA | 合整合分支進 feature | 腳本三 SHA | 兩次腳本是否同一座標 | git |

### Current Journey
正式 SOP(現行模板頂註):2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 只准文件。
STATUS／派工仍講舊旅程(Fresh → Verdict → Exit 才合)。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | reviewer | 派工舊序:先 Fresh | gauntlet | — | Source SHA=當時 HEAD | 之後合會換 HEAD |
| 2 | reviewer | 雙軸＋Verdict | 7-review | owner | PASS 綁舊樹 | 核准≠出貨 |
| 3 | reviewer | Exit 才合 INTEGRATION_SHA | 整合腳本 | 整合分支 | HEAD 變了 | 未審內容進出貨樹 |
| 4 | reviewer | `ALREADY_SYNCED` 只寫作廢 | 7-review | — | 無恢復 | 假過或停住無路 |

現行模板旅程(本 tree 已寫、尚未用本 slug 跑完):Step 1 改為先整合,Fresh 綁合完後 HEAD。

### Workarounds
- 人口頭記「先合再 Fresh」;系統不擋顛倒。
- Exit 才合;Verdict 綁的 SHA 與出貨 SHA 不同。
- `ALREADY_SYNCED` 只抄「證據不算數」,不重跑 Fresh、也不 FAIL。
- 這些步驟常不留「兩次腳本座標相同」紀錄。

### Exceptions
- `N_A_NO_INCOMING`:對方零新 commit,記 n-a 即過,無合併。
- 已合過、merge-base 被污染:`ALREADY_SYNCED`。現行模板給恢復:重跑 Fresh 綁當下 HEAD,或本項 FAIL。派工當時沒這條。
- 誰都可跳過 2c;沒有主機層攔截。`[Assumption]` 現場仍有人走舊序或跳過(無採用專案 log;風險=高;期限=Stage 2 對帳,過期擋 G2)。

### Evidence
- owner 書面 brief(本 session 2026-09-12):問題=Fresh→Verdict→Exit 同步;ALREADY_SYNCED 弱;裁決=整合在 Fresh／雙軸／Verdict 之前;lane full;只 Stage 1。
- 派工收尾:notes/dispatch-v380-landing.md:L1011-L1018 notes/dispatch-v380-landing.md:L1039-L1040
- 本 tree 已核:上列 Context 出處。
- 範例漂移:example/contract-expiry-reminder/7-review.md:L24
- `[Assumption]` 採用現場仍按舊序或跳過 2c:無 log;期限 Stage 2。

## Goals
- G-out-1:人宣稱 G3／shipped 時,Verdict 綁的樹就是出貨的樹(合完再審,或合完後重綁 Fresh)。
- G-out-2:`ALREADY_SYNCED` 時人有可執行的下一步(重綁 Fresh 或 FAIL),不能只靠「證據不算數」過關。
- G-out-3:本 slug 成為第一條真實 full lane 的載體,用來鎖住「出貨樹=核准樹」。

## Requested solution（候選，未定案）
- 清單與機械錨把整合放在 Fresh／雙軸／Verdict 之前。
- 加強 `ALREADY_SYNCED` 恢復,並對帳範例／STATUS／gate-consistency。
- 本 hop 不選定改哪些守衛、是否重寫已存在的 2c 散文。

## Non-Goals(初稿)
- 不在本 slug 實作九條制度缺口(A-1~B-2);那批另開 feature。
- 本 hop 不送 G1、不改 Stage 1–4 模板、不 bump plugin。
- 不動 open PR #196、不刪 gate-twin Backlog(若 main 仍在)。
- 不做 Windows 真機驗證。
- 不重寫整合腳本演算法本身。

## Open Questions
- [x] Q1:lane 是否 full?→ owner:full
- [x] Q2:整合是否必須在 Fresh／雙軸／Verdict 之前?→ owner:是
- [x] Q3:是否當第一條真實 full lane?→ owner:是
- [x] Q4:本 hop 是否送 G1?→ owner:否,只 Stage 1
- [~] Q5:本 tree 2c 散文已在 Fresh 前,剩餘是否主要是鎖牙／範例／STATUS?(帶假設:是;期限=Stage 2 對帳,過期擋 G2)
- [>] Q6:gate-consistency／renderer 錨點怎麼鎖、鎖哪幾句?→ 移交 Stage 2+
- [>] Q7:範例 `2c = Fresh` 與其他舊編號何時改?→ 移交後續站

## Constraints
- 表列只准 `scripts/status-update.sh`;HISTORY 只准 `history-append.sh`。
- 不與 #196 搶刪 gate-twin 列。
- 本 PR 不宣稱 G1 PASS;status 留 draft。
- 若後續命中 Stage 3:Human verdict 一行寫角色／場景(A-5 LIGHT),不在本 hop 做。

## 驗收雛形
- AC-1(G-out-1):假設 reviewer 已寫下 Verdict,當人對照「審過的 HEAD」與「出貨的 HEAD」,則兩者相同。
  - 從哪看:該 feature 的 7-review 所記 Source SHA,對 `git rev-parse HEAD`(Exit 之後)
  - 看到什麼算對:兩個 SHA 逐字相同;不是「應該沒差」
  - 拿什麼試:本 slug 後續自己走到 Stage 7;或一份故意「Verdict 後才合」的對照紀錄
- AC-2(G-out-2):假設腳本印 `ALREADY_SYNCED`,當人要勾整合項,則只能走「重綁 Fresh」或「本項 FAIL」。
  - 從哪看:同一份 7-review 的整合結論＋Fresh Source SHA
  - 看到什麼算對:有重綁後的 SHA,或明確 FAIL;沒有只寫「證據不算數」卻勾過
  - 拿什麼試:已合過、merge-base 被污染的 fixture／實例
- AC-3(G-out-1):假設人按執行清單做 Stage 7,當讀到整合那一步,則它出現在 Fresh、雙軸、Verdict 之前。
  - 從哪看:7-review 執行清單(或同等節點鏈)的步驟序
  - 看到什麼算對:整合步的序號／位置在 Fresh／Verdict 之前;不是 Exit 才出現合併
  - 拿什麼試:本 repo `_templates/7-review.md` 與本 slug 後續產出

## 現況圖
誰:reviewer
做什麼:Fresh 後再判
工具:7-review
痛點:核准樹會變
↓
誰:reviewer
做什麼:Verdict 後才合
工具:Exit 清單
痛點:出貨樹不同
↓
誰:owner
做什麼:把核准當出貨
工具:G3 / PR
痛點:HEAD 已換過

## 邏輯圖(ASCII)
```
now
|-- old order (dispatch / STATUS backlog)
|   |-- Fresh
|   |-- Verdict
|   +-- Exit merge   [approved != ship]
|-- current template prose
|   |-- 2c integrate
|   |-- 2d Fresh
|   +-- Verdict      [text already moved]
+-- this slug (full lane)
    |-- lock teeth / examples
    +-- no G1 this hop
```

## Interview Log(推理鏈外顯)
- Q:為什麼 Fresh→Verdict→Exit 才合,會讓核准樹≠出貨樹?
  - 事實:notes/dispatch-v380-landing.md:L1011-L1018 _templates/7-review.md:L176-L177
  - 推理:Verdict 綁當下 HEAD。Exit 再合 `INTEGRATION_SHA` 會改 HEAD。核准的 commit 不再是出貨的 commit。
  - 結論:CONFIRMED 合併必須發生在 Fresh／Verdict 之前,或合完後作廢並重綁。
- ⚠️ Q:本 tree 的 7-review 現在還是派工寫的舊節序嗎?
  - 事實:_templates/7-review.md:L100-L120 _templates/7-review.md:L330-L333 guides/guide-dev-flow.html:L1718-L1738 skills/dev-flow/stage7/nodes/S2c-integration.md:L24-L25
  - 推理:2c 已在 2d 前;指南與節點鏈同序。派工行號 `:94`／`:133`／`:281` 對不上現檔。散文可能已搬,不代表牙與範例已鎖。
  - 結論:CONFIRMED 現行模板散文已是整合→Fresh;舊序仍活在派工／STATUS／範例敘事。
- Q:`ALREADY_SYNCED` 現在是不是仍「只說證據不算數」?
  - 事實:_templates/7-review.md:L110-L113 notes/dispatch-v380-landing.md:L1011-L1018
  - 推理:派工當下沒恢復路徑。現檔已寫重跑 Fresh 或 FAIL。弱點是否還在,要看機械是否仍放行「只寫作廢」。
  - 結論:NEEDS_VERIFICATION 散文已有恢復;是否被牙強制,Stage 2 對帳。
- Q:為什麼這題要走完整 full lane,不能當發版前補丁?
  - 事實:notes/dispatch-v380-landing.md:L1011-L1018 notes/dispatch-v380-landing.md:L1039-L1040
  - 推理:owner 寫明它動模板節序與 gate-consistency 錨,不該塞進 v3.8.0 補丁。本 hop 只開討論,不送 G1。
  - 結論:CONFIRMED 本 slug 是那條獨立 full lane 的 Stage 1,不是補丁。
- Q:範例有沒有還在教「2c = Final Fresh」?
  - 事實:example/contract-expiry-reminder/7-review.md:L24 _templates/7-review.md:L100-L120
  - 推理:範例把 2c 當 Fresh;模板 2c 已是整合。採用者照範例會走舊編號。
  - 結論:CONFIRMED 範例編號與現行清單不一致;改範例是後續站,不是本 hop。
- ⚠️ Q:本 hop 範圍與「九條已裁」是否混成同一施工?
  - 事實:docs/dev/STATUS.md:L34 docs/dev/STATUS.md:L52
  - 推理:owner 把九條實作另開;本 slug 只處理整合節序。Active 已有本列,九條列已改裁決指標。
  - 結論:CONFIRMED 本討論不解九條實作;STATUS 已把此題移進 Active 並改裁決指標。
- ⚠️ Q:若散文已搬,後續還要鎖什麼?
  - 事實:skills/dev-flow/SKILL.md:L49 _templates/7-review.md:L30-L31 example/contract-expiry-reminder/7-review.md:L24
  - 推理:技能摘要已寫「整合在 Fresh 前」。剩餘是牙、範例、STATUS、以及用本 slug 真的跑完一次。`[Assumption]` 現場仍可能跳過 2c。
  - 結論:OPEN 假設剩餘主軸是鎖與跑通;Stage 2 驗證,過期擋 G2。
- Q:本 hop 要不要產出 G1 核准?
  - 事實:docs/dev/STATUS.md:L34
  - 推理:owner 明示只 Stage 1、不送 G1。Active Gates 仍是 G1⬜;討論檔 status 留 draft。
  - 結論:CONFIRMED 本 PR 不改 status 為 approved,也不填 G1 PASS。
