---
feature: integration-before-verdict
stage: 1-discussion
status: draft
owner: tony
reviewers: []
updated: 2026-09-12
---

# 1. 討論 — 整合回歸必須發生在 Fresh／雙軸／Verdict 之前

> 本場是 Cursor Cloud Agent 依 owner 書面 brief 落檔，不是現場一問一答。未核敘述標 `[Assumption]`。本 hop 不做決定、不改 `_templates/7-review.md`、不送 G1。A-1 已裁：Goals 只寫結果；做法另見 Requested solution。

## Problem
誰:Stage 7 reviewer 與要批 G3 的 owner。
痛:2026-08 派工所見節序是 Final Fresh → Verdict → Exit 才合併 `INTEGRATION_SHA`，審過並核准的樹不是最後出貨的樹；`ALREADY_SYNCED` 當時只說「證據不算數」，沒有恢復路徑。
現在怎麼繞:hardening 迴圈已把模板步 2c 挪到 Final Fresh 前，但看板直到本落地才把舊故事移出 Backlog；腳本檔頭仍寫 Exit Checklist。人可以跟新模板，也可以跟過期敘事。

## Context(已知事實)
- 2026-08 派工寫死舊節序 Fresh(`7-review.md:94`)→ Verdict(`:133`)→ Exit 整合同步(`:281`)；核准樹在 Exit 合併後就不是出貨樹；`ALREADY_SYNCED`(`:291`)只說證據不算數；owner 裁獨立 full lane，不當發版前補丁:notes/dispatch-v380-landing.md:L1011-L1018
- 當下模板頂註已寫「出貨樹=審過的樹」；整合回歸改 HEAD 必須在 Final Fresh 之前；Verdict 後改碼作廢 G3:_templates/7-review.md:L30-L31
- 當下執行清單步 2c 是整合回歸，寫死「算交集 → 合併 → 全套測試 → 再進 2d Final Fresh」，並點名舊順序「Fresh → Verdict → Exit 才合併」是錯的:_templates/7-review.md:L100-L120
- 步 2d 才是 Final Fresh Run，Source SHA = 當下 HEAD = 送審樹:_templates/7-review.md:L121-L122
- Verdict 定義在步 5；PASS 條件之後才寫禁止改碼:_templates/7-review.md:L167-L177
- Verdict 之後禁止再改程式碼；任何程式碼 commit 作廢 G3，須回 2c/2d:_templates/7-review.md:L176-L177
- Exit 只准文件／PR／living spec，不准再碰程式:_templates/7-review.md:L179
- Exit Checklist 條件式條只確認「整合回歸已在 Final Fresh 之前完成」，並禁在本節補碼或合併 `INTEGRATION_SHA`:_templates/7-review.md:L330-L333
- `ALREADY_SYNCED` 恢復路徑已寫：重跑 Final Fresh 綁當下 HEAD，或本項 FAIL；不得只寫「證據不算數」就過:_templates/7-review.md:L110-L113
- hardening 4-spec 檔頭自承迴圈實作、未重開 Stage 1–3:docs/dev/stage7-g3-hardening/4-spec.md:L9-L13
- hardening 規格已把「整合在 Fresh 前／Exit 不再合併／ALREADY_SYNCED 有恢復路徑／Verdict 後改碼作廢 G3」寫成 R-1:docs/dev/stage7-g3-hardening/4-spec.md:L17-L31
- 機械牙 ST 組驗頂註「整合回歸」字面位置在「Final Fresh Run」之前，且 Exit 不得再合併 INTEGRATION_SHA:scripts/check-stage67-enforcement.sh:L298-L322
- 整合回歸正本檔頭仍自稱 Stage 7 Exit Checklist「(條件式)整合回歸」計算工具:scripts/devflow-integration-regression.sh:L2
- 指南複本與模板同序：2c 在 Fresh 前，ALREADY_SYNCED 有恢復路徑:guides/guide-dev-flow.html:L1718-L1731
- 本落地後 Active 已有本 slug、full、1-discussion、G1 空格:docs/dev/STATUS.md:L34
- gate-twin Backlog 列仍在；本場不碰:#196 仍開:docs/dev/STATUS.md:L50
- 九條制度缺口已裁決，實作另開 feature，不得混進本 slug:notes/review-requirement-discovery-gaps.md:L9-L11 notes/review-requirement-discovery-gaps.md:L21-L35
- owner 本場書面 brief（2026-09-12）:本 slug 只做 Stage 1；lane = full；整合在 Fresh／雙軸／Verdict 之前；不送 G1 PASS；來源限 dispatch 收尾與 7-review 模板

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| reviewer | 在送審樹上核准，出貨樹仍是那棵 | 跑整合腳本、合併 `INTEGRATION_SHA`、寫 7-review | 當下模板步 2c／2d | 別人是否仍照 2026-08 舊節序做 | 7-review、終端機 |
| owner | 批的 PASS 對上最後出貨的 SHA | G3／merge | 派工原痛、本場 brief | hardening 之後現場是否還有人 Exit 才合 | GitHub、PR |
| author | 要 PASS 然後出貨 | 改 feature 樹，Verdict 後不該再改碼 | 6-notes `FORK_INTEGRATION_SHA` | 何時准動 HEAD | git |

### Current Journey
正式 SOP = 當下 `_templates/7-review.md` 步 2c→2d→雙軸→Verdict→Exit（只文件）。下面三步是 **2026-08 派工／過期看板所描述的痛路徑**（人若跟舊故事仍會走）。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | reviewer | Fresh Run | 7-review | — | Verification Evidence 綁分岔 HEAD | 審的是舊樹 |
| 2 | owner | 批 Verdict | 7-review | reviewer 的 Fresh | verdict PASS | 核准舊樹 |
| 3 | reviewer | Exit 合併 | git merge | 整合分支新 commit | HEAD 變成合併後 SHA | 出貨樹已變 |

當下模板 SOP（對照，不是現況圖）:reviewer 先跑整合腳本 → 需要時合併印出的 `INTEGRATION_SHA` → 再 Final Fresh → 雙軸 → Verdict → Exit 不再合併。

### Workarounds
- 跟當下模板 2c：Fresh 前先合。系統有 7-review 正文，但腳本檔頭仍寫 Exit。
- 跟 2026-08 故事：Verdict 後才合。`[Assumption]` 採用現場若只讀過期 Backlog 句子，仍可能這樣走。
- `ALREADY_SYNCED` 時只寫「證據不算數」仍勾過 —— 舊字；當下模板已禁，恢復路徑要另跑 Fresh 或 FAIL。
- hardening 未開 Stage 1，用 4-spec 迴圈把節序寫進模板。無討論檔可對帳「人怎麼走」。

### Exceptions
- `N_A_NO_INCOMING`：分岔後對方零新 commit，記 n-a，不必合併。
- `ALREADY_SYNCED`：已合過，交集證據作廢；要重跑 Fresh 或 FAIL，不得當沒有共同戰場。
- Verdict 後任何程式碼 commit → G3 作廢，回 2c/2d。
- fast lane 仍有 Stage 7；節序規則不因 lane 消失。
- 本 PR 明示不送 G1，status 停 draft。

### Evidence
- owner 書面 brief（2026-09-12 session）:slug、full、Stage 1 only、無 G1 PASS、整合在 Fresh／雙軸／Verdict 前。
- 已核文件:上列 Context 出處（本 working tree 讀過）。
- hardening 迴圈種子:`docs/dev/stage7-loop/` 與 `docs/dev/stage7-g3-hardening/4-spec.md`（未重開 1–3）。
- `[Assumption]` 採用者「仍有人 Exit 才合併」:從過期看板＋腳本檔頭推出，無採用專案 log。期限:本 slug G2 前用一次真實 Stage 7 走訪核銷，否則維持 Assumption。
- `[Assumption]` 雙軸若在未同步樹上做，finding 可能綁錯 SHA。期限:同上。

## Goals
- G1 核准即出貨:人批 PASS 時認定的那棵樹，就是之後 ship 的樹。
- G2 已同步可恢復:`ALREADY_SYNCED` 時人知道下一步是重跑 Fresh 或停，不會只寫「證據不算數」就過。
- G3 後段都看同一棵樹:Fresh、雙軸、Verdict 都發生在整合同步之後。
- G4 看板不再教舊序:進行中列指向本 slug；Backlog 不再把 Fresh→Verdict→Exit 合併寫成「現在的節序」。

## Requested solution（候選，未定案）
把「整合回歸與同步」移到 Final Fresh、雙軸審查、Verdict **之前**；Exit 不再改 HEAD。owner lean 走完整 full lane。本 PR 只落 Stage 1。hardening 已改模板正文是否算做完，留給 Stage 2 壓測，不在本檔定案。

## Non-Goals(初稿)
- 不在本 slug 實作九條制度缺口（A-1~B-2）；見 Owner Call，另開 feature。
- 本 PR 不送 G1、不改 7-review 模板、不 bump 版號、不 merge。
- 不碰 #196 gate-twin STATUS 列。
- 不做 SDC；不做已移除的 Windows 真機列。
- 不把 hardening 已落地的 2c/2d 文字默默改回去。

## Open Questions
- [x] Q1:lane？→ full（owner brief）
- [x] Q2:整合要在 Fresh／雙軸／Verdict 之前？→ 是（owner brief；做法仍是候選）
- [x] Q3:本 PR 是否送 G1 PASS？→ 否；status 留 draft
- [x] Q4:slug？→ `integration-before-verdict`（owner 指定）
- [~] Q5:hardening 已把 2c 挪到 Fresh 前，本 slug 還要改模板嗎？→ 帶假設:先當「關看板＋走完整 1–7＋清剩餘漂移（檔頭／過期敘事）」；若 Stage 2 查出模板仍有洞再改文。暫定值=不在 Stage 1 重寫 2c
- [>] Q6:九條 DO/LIGHT 的模板與守衛 → 另開 feature，本討論不解
- [>] Q7:SDC／Reference App → 維持 C 級暫緩

## Constraints
- 本 hop 只准 `1-discussion.md` + `1-discussion.html`；STATUS／HISTORY 走腳本，不手改表列。
- 不動 Stage 1–4 模板正文（本討論不施工）。
- 動 7-review 節序會碰 gate-consistency／ST 牙；後段才做。
- feature branch 的 STATUS 表列相對 `origin/main` 會被 ⑰ 旗到合併前，與 #196 同型。
- 人看討論用繁中。

## 驗收雛形
- AC-1(G1):假設 reviewer 已批 PASS，當有人指出出貨 SHA，則該 SHA 就是批 PASS 時的 HEAD，中間沒有「再合併一次才出貨」。
  - 從哪看:該次 7-review 的 Verdict／Exit 文字與當下 git HEAD
  - 看到什麼算對:Verdict 後沒有合併 `INTEGRATION_SHA` 的步驟；Source SHA = HEAD
  - 拿什麼試:本母版下一輪真實 Stage 7（本 PR 不跑）
- AC-2(G2):假設腳本印 `ALREADY_SYNCED`，當 reviewer 要繼續，則文件出現「重跑 Fresh」或「本項 FAIL」，沒有「只寫證據不算數」就過。
  - 從哪看:7-review 該步結論
  - 看到什麼算對:兩條恢復路徑之一落檔
  - 拿什麼試:已合過整合分支的 feature 樹（throwaway）
- AC-3(G3):假設整合同步尚未做，當人要做雙軸或 Verdict，則還沒到那一步。
  - 從哪看:執行清單順序與實際留下的 SHA
  - 看到什麼算對:雙軸／Verdict 記錄的樹已含整合結果，或明確停在 2c
  - 拿什麼試:分岔後整合分支有新 commit 的樹
- AC-4(G4):假設有人只看 STATUS 進行中／Backlog，當他找「現在的節序」，則看不到「Fresh→Verdict→Exit 才合併」被寫成現況。
  - 從哪看:`docs/dev/STATUS.md` Active／Backlog
  - 看到什麼算對:Active 有本 slug；Backlog 無該舊節序句
  - 拿什麼試:本 working tree 的 STATUS（本落地後已然）

## 現況圖
```
reviewer
Fresh Run
7-review
審的是舊樹
↓
owner
批 Verdict
7-review
核准舊樹
↓
reviewer
Exit 合併
git merge
出貨樹已變
```

## 邏輯圖(ASCII)
```
old story
|-- Fresh on fork HEAD
|-- Verdict PASS
+-- Exit merge INTEGRATION_SHA   [pain: SHA changed]
now template
|-- 2c integrate then test
|-- 2d Fresh = submit tree
|-- dual-axis + Verdict
+-- Exit docs only
leftover
|-- script header still says Exit
|-- board told old story until this landing
+-- no Stage 1 before hardening
later
+-- pick remaining holes (not this file)
```

## Interview Log(推理鏈外顯)
- Q:2026-08 為什麼說核准樹不是出貨樹？
  - 事實:notes/dispatch-v380-landing.md:L1011-L1018
  - 推理:Fresh 與 Verdict 綁 feature HEAD；Exit 才合 `INTEGRATION_SHA`，HEAD 變了。審的 SHA ≠ ship 的 SHA。
  - 結論:CONFIRMED 這是原痛，不是口味。
- Q:當下 7-review 還是 Fresh→Verdict→Exit 才合嗎？
  - 事實:_templates/7-review.md:L100-L120 _templates/7-review.md:L176-L177 _templates/7-review.md:L179 _templates/7-review.md:L330-L333
  - 推理:步 2c 已在 2d 前；Exit 禁再合併。派工行號 `:94/:133/:281` 已過期。
  - 結論:CONFIRMED 模板正文已改；舊行號不能當現況。
- Q:沒開 Stage 1 怎麼改到模板的？
  - 事實:docs/dev/stage7-g3-hardening/4-spec.md:L17-L31
  - 推理:hardening 用 4-spec 迴圈落地 R-1，明文不重開 1–3。人的旅程沒被討論檔接住。
  - 結論:CONFIRMED 本 slug 是補上被跳過的 full-lane 討論，不是假裝模板沒動過。
- ⚠️ Q:`ALREADY_SYNCED` 現在有沒有恢復路徑？
  - 事實:_templates/7-review.md:L110-L113 scripts/devflow-integration-regression.sh:L2
  - 推理:模板已寫重跑 Fresh 或 FAIL。腳本檔頭仍掛 Exit，人可能從錯入口讀到「輸出不算數」。
  - 結論:CONFIRMED 模板有路徑；檔頭漂移是剩餘洞。
- Q:為什麼還要獨立 full lane，而不是改完模板就關單？
  - 事實:notes/dispatch-v380-landing.md:L1016-L1018 docs/dev/STATUS.md:L34
  - 推理:owner 要的是完整七站與機械錨點一起走。模板先改 ≠ 討論／決策／規格鏈完整。
  - 結論:CONFIRMED 本場只開 Stage 1；關單要走完 lane，不是本 PR。
- ⚠️ Q:Fresh／雙軸／Verdict 是否都必須在整合之後？
  - 事實:_templates/7-review.md:L100-L120 _templates/7-review.md:L121-L122 _templates/7-review.md:L167-L177
  - 推理:整合改 HEAD。Fresh 若先跑，證據綁舊樹。雙軸與 Verdict 若先做，finding 也綁舊樹。owner 要三者都在整合後。
  - 結論:CONFIRMED 方向；具體節次微調留給 Stage 2。
- Q:what-if 若維持 Exit 才合併？
  - 事實:_templates/7-review.md:L30-L31 scripts/check-stage67-enforcement.sh:L298-L322
  - 推理:回到原痛，且 ST 牙會紅。what-if 只證明舊序走不通，不選方案。
  - 結論:OPEN 發散:Exit 合併不可恢復為 SOP。
- ⚠️ Q:沒說出口的預設是「模板已改就等於做完」嗎？
  - 事實:docs/dev/stage7-g3-hardening/4-spec.md:L9-L13 notes/review-requirement-discovery-gaps.md:L9-L11
  - 推理:hardening 自己說未重開 1–3。九條實作也禁混進本 slug。本場若把「已改 2c」寫成 Goal，會把結果與做法鎖死。
  - 結論:OPEN 帶假設 Q5:本 Stage 1 不重寫 2c；剩餘是看板、檔頭、完整 lane。
