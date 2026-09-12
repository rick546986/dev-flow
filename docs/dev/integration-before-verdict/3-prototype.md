---
feature: integration-before-verdict
stage: 3-prototype
status: draft
owner: rick
updated: 2026-09-12
---

# 3. 原型 — Stage 7 順序與 AS-1 填檔牙長什麼樣？

> tip 模板／指南／節點鏈**已經**是 2c 整合 → 2d Fresh（#202／#207）。本站不重編號、不重寫整合腳本演算法、不實作 Stage 6 守衛碼。
> 要回答的是剩餘交付的**形狀**：填檔牙（重綁 SHA 或 FAIL）+ 活教師改口（example／manifest／腳本檔頭）。
> Decision A+AS-1+T-now 已是核准 Pattern → **1 個可操作 CLI Demo**，不湊假 Variant。
> Human verdict 由參與 Demo 的人類親填；Agent 禁代填 ACCEPTED／attestation。本檔 `status` 留 draft，直至 Human verdict = ACCEPTED。
> 不假裝 G2／G3、不發版、不碰 `diagram-ir-gate`／#196。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context -->
- [ ] 有新的前端流程（本題是清單／填檔／腳本檔頭，無新前端）
- [x] 改變使用者下一步（`ALREADY_SYNCED` 後不得只寫「證據不算數」勾過；下一步是重綁 2d Source SHA 或本項 FAIL）
- [x] 涉及角色交接（reviewer ↔ merger ↔ owner；合的是腳本印的 INTEGRATION_SHA）
- [x] 涉及人工核准（G3 Verdict；FAIL 是人停下重算）
- [x] 涉及等待/退回/逾時（`ALREADY_SYNCED` 停住 → 重跑 Fresh 或 FAIL）
- [x] 涉及權限差異（reviewer 只在 2c 准改 HEAD；merger 才合；owner 簽 G3）
- [x] 涉及系統外動作（git merge、GitHub PR、終端機腳本）
- [ ] 涉及多種可行互動設計（A+AS-1+T-now 已 lock；單一路徑 CLI 填檔牙）
- [x] Stage 1 尚有操作流程不確定性（牙何時發動、結論欄位長什麼樣，Decision 留給本站／4-spec）

→ 命中 7 條:Stage 3 條件式必要,執行(不跳過)。2-decision 無「跳過 Stage 3」流程層 OC。

## Question
引 2-decision Risks 第 1–2 條 + SC-2／SC-3 + Decision「剩餘交付是填檔牙與活教師」：

1. **AS-1 填檔牙形狀**：一份填好的 7-review 記 `ALREADY_SYNCED` 時，什麼結論算過、什麼必須機械紅？
2. **發動時機**：如何避免誤殺 `N_A_NO_INCOMING` 與未跑 2c 的 draft？
3. **活教師 intended 改口**：example／manifest／腳本檔頭要改成哪一句，才不再教 `2c = Fresh`／「Exit Checklist 計算工具」？（本站只展示，不改正本）
4. **Stage 7 順序**：活教師必須教的序是否就是 tip 已鎖的 2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 只准文件？

答案長什麼樣才算回答了：
- 有可跑的 throwaway 謂詞：void-only → RED；重綁 SHA → GREEN；明示 FAIL → GREEN；n-a／draft → N/A。
- 發動條件寫成可檢查的句子（宣稱勾過／送 G3／明示 FAIL 才咬）。
- 活教師五條路徑有現況 vs intended 對照，且本 PR **未改**那些正本。
- 順序圖與 tip `_templates/7-review.md` 2c→2d 一致。

## Method
- 實驗位置:`docs/dev/integration-before-verdict/proto/`（**PROTOTYPE — not production**；非正式守衛；不進 CI；正式落地留給 Stage 6、沿用 `check-stage67` 家族，OC-1）
- Demo 形式:**可執行 CLI flow**（使用者實際跑分類器，不是只看靜態說明）
- Pattern 已核准 → **1 個 Demo**，不做假 Variant
- 驗法:
  1. `python3 docs/dev/integration-before-verdict/proto/check-as1-tooth.py`
  2. 五份 fixture 的 expect/got 全對
  3. 活教師掃描仍報 OLD（本站故意不改；證明 T-now 仍有工）
  4. tip 模板仍是 `2c. **整合回歸**` 在 `2d. **Final Fresh Run**` 之前

### 擬定填檔牙（Stage 4 再釘欄位／腳本名）
- **輸入**：一份填好的 `docs/dev/<slug>/7-review.md`
- **發動**：文內有 `ALREADY_SYNCED`，且（宣稱勾過整合項 `[x]…整合回歸`、或 frontmatter 已送 G3、或明示本項 FAIL）。`N_A_NO_INCOMING` 與未結論的 draft **不預先紅**。
- **GREEN**：恢復路徑二選一成立——① Rebound Source SHA（≥7 hex）+ 重綁／重跑 Final Fresh 語句；② 明示 `本項 FAIL`（該項不得勾過）。
- **RED**：只寫「證據不算數／輸出不算數」、沒有重綁 SHA、也沒有 FAIL，卻宣稱勾過／送 G3。
- **不改**整合腳本演算法（AS-3 已拒）；腳本仍只算只判。GUIDANCE 改口是活教師，不是新演算法。

## 結構圖
- 2c 整合回歸（選定順序；最後一次准改 HEAD）
- 2d Final Fresh（Source SHA = HEAD）
- 雙軸 + 現象
- Verdict
- Exit 只准文件（禁合併）
- CLI 填檔牙 Demo（選定）

```
reviewer
  |
  v
[2c 整合回歸]  last code/HEAD change
  |  N_A_NO_INCOMING → 記 n-a
  |  SYNC_REQUIRED_* → merge INTEGRATION_SHA + tests
  |  ALREADY_SYNCED  → 重綁 2d SHA 或 本項 FAIL
  |                    只寫「證據不算數」= 牙 RED
  v
[2d Final Fresh]  Source SHA = 當下 HEAD   ← 選定順序
  v
[雙軸 + 現象]
  v
[Verdict]
  v
[Exit 只准文件]  禁再合、禁改碼
```

## Demo Script

### Scenario AC-3（走 intended 順序）
- 使用者角色:Stage 7 reviewer
- 真實目標:在將出貨的那棵樹上做 G3；核准樹=出貨樹
- 起始狀態:tip `_templates/7-review.md` 已是 2c 整合 → 2d Fresh；本 slug 尚未寫 4-spec／守衛碼
- 操作步驟:打開 `proto/live-teacher-intended.md` 與模板頂註；對照 CLI 印出的 `2c → 2d → 雙軸 → Verdict → Exit 只准文件`
- 系統回應:順序與 tip 模板一致；活教師對照表指出 example／manifest／檔頭仍教舊序
- 系統外下一步:本站不改正本；Stage 6 才改活教師
- 觀察問題:看到清單後，下一步是先合還是先 Fresh？系統有沒有暗示 Exit 才准合？

### Scenario AC-2（void-only 必須紅）
- 使用者角色:Stage 7 reviewer
- 真實目標:`ALREADY_SYNCED` 時不能只靠「證據不算數」勾過
- 起始狀態:`proto/filled-void-only.md` 記 `ALREADY_SYNCED` + 「證據不算數／輸出不算數」+ `[x]` 勾過、無重綁 SHA、無 FAIL
- 操作步驟:跑 `python3 docs/dev/integration-before-verdict/proto/check-as1-tooth.py`；看 `filled-void-only.md` 列
- 系統回應:`expect RED / got RED`
- 系統外下一步:正式牙 Stage 6 才掛進既有檢查家族
- 觀察問題:這份填檔看起來能不能送 G3？下一步是重綁還是停？

### Scenario AC-2（重綁 SHA 必須綠）
- 使用者角色:Stage 7 reviewer
- 真實目標:合過之後重跑 2d，把 Source SHA 綁到新 HEAD
- 起始狀態:`proto/filled-rebind.md` 有 Rebound Source SHA `c0ffee1` + 「重跑 Final Fresh 重綁」
- 操作步驟:同一支 CLI；看 `filled-rebind.md` 列
- 系統回應:`expect GREEN / got GREEN`
- 系統外下一步:無
- 觀察問題:重綁後是否看得出 Source SHA 就是送審樹？

### Scenario AC-2（明示 FAIL 必須綠）
- 使用者角色:Stage 7 reviewer
- 真實目標:merge-base 污染時停下，不假裝過關
- 起始狀態:`proto/filled-fail.md` 寫「本項 FAIL」，2c 未勾
- 操作步驟:同一支 CLI；看 `filled-fail.md` 列
- 系統回應:`expect GREEN / got GREEN`（牙承認合法停，不是假過）
- 系統外下一步:從乾淨座標重算（系統外 git）
- 觀察問題:FAIL 會不會被當成「沒勾所以沒牙」而漏掉？能否撤回／重算？

### Scenario AC-2（n-a 與 draft 不預先紅）
- 使用者角色:Stage 7 reviewer
- 真實目標:零 incoming 或還沒跑 2c 時不被誤殺
- 起始狀態:`proto/filled-n-a.md`（`N_A_NO_INCOMING`）；`proto/filled-draft.md`（draft、未勾）
- 操作步驟:同一支 CLI；看這兩列
- 系統回應:兩列皆 `N/A`
- 系統外下一步:n-a 可繼續 2d；draft 先跑腳本
- 觀察問題:空狀態／未跑是否被當成壞掉？

## Result
- **2026-09-12 實跑**（本 branch `cursor/ibv-stage3-prototype-58f2`，base tip `630cd41` / #207）:
  ```
  intended Stage 7 order:
    2c 整合回歸 → 2d Final Fresh → 雙軸 + 現象 → Verdict → Exit 只准文件
  fixture                expect   got      ok
  filled-void-only.md    RED      RED      yes
  filled-rebind.md       GREEN    GREEN    yes
  filled-fail.md         GREEN    GREEN    yes
  filled-n-a.md          N/A      N/A      yes
  filled-draft.md        N/A      N/A      yes
  live-teacher scan:
    OLD example/contract-expiry-reminder/7-review.md:24
    OLD example/contract-expiry-reminder/4-spec.md:223
    OLD manifests/p4-gauntlet-gates.md:52
    OLD scripts/devflow-integration-regression.sh:2
    OLD docs/dev/tools/devflow-integration-regression.sh:2
  tooth-shape demo: fixtures match intended AS-1 predicate
  ```
- 答案:
  1. 填檔牙形狀成立（throwaway）：void-only 紅；重綁 SHA 或明示 FAIL 綠。
  2. 發動時機成立：n-a／未結論 draft 不預先紅；FAIL 即使未勾也算合法結論。
  3. 活教師五條路徑仍教舊序／舊檔頭（T-now 工還在）；intended 改口見 `proto/live-teacher-intended.md`。本 PR **未改**那些正本。
  4. 順序 = tip 已鎖的 2c→2d；本站不重編號。
- **CLI Demo 足夠**：互動形已由 Decision lock；剩餘是結論形狀，不是第二套 UI。
- 正式守衛／example 改寫 **尚未**寫入 production 路徑（留給 Stage 6 + 5-tasks Files）。
- 回寫對象:2-decision Risks 第 1–2 條 + 確認紀錄「prototype 回寫」行。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填；Agent 禁代填 ACCEPTED／attestation -->
- Demo date: 2026-09-12（agent 已代跑 CLI；待人類親走 Demo Script）
- Participants:
- Variant reviewed: CLI-only（無 UI Variant；Pattern A+AS-1+T-now）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED
- Verdict attestation:

## Verdict
- 回寫 2-decision Risks 第 1 條：填檔牙擬定形狀 = `ALREADY_SYNCED` 時必須「Rebound Source SHA」或「本項 FAIL」，只寫「證據不算數／輸出不算數」→ 紅。欄位／掛進哪一支既有檢查，仍進 4-spec（OC-1）。
- 回寫 2-decision Risks 第 2 條：牙只在宣稱勾過／送 G3／明示 FAIL 時發動；`N_A_NO_INCOMING` 與未結論 draft 不預先紅。已用 fixture 跑過。
- 回寫活教師：T-now 清單確認五條活路徑仍舊；intended 改口已展示、**未改正本**。
- 互動／Human verdict：仍待 owner 親填（本檔 `status: draft`）。
- proto 產物處置:留在 `docs/dev/integration-before-verdict/proto/` 當本站 Demo 證據；Stage 6 正式碼另寫，不把本目錄當 production 入口。
