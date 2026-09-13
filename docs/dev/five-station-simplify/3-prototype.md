---
feature: five-station-simplify
stage: 3-prototype
status: draft
owner: rick
reviewers: []
updated: 2026-09-13
---

# 3. 原型 — 假完成 T／Must-keep RP 時，owner 看見什麼？

> Implementer C。Lane = **full**。本 hop **只本檔 + 審頁 html**；不改 `_templates/`／`graph.yaml`／gate token／`scripts/` 牙、不改 STATUS／HISTORY、不改 `2-decision.md`、不填 `ACCEPTED`、不合併。
> 原料：G1 已核的 `2-decision.md`（#303 `verdict: PASS`、OC-1…OC-11 ✅）、`1-discussion.md` M 表、`notes/design/five-station-simplify-brief-v3.md`。未讀他線 Stage 3。
> C 線主軸：**摺掉例行等人之後，Must-keep／RP 被掏空時，人看見的必須是「未完成」，不是綠勾。** 本站用狀態模擬器走假完成 T（缺 Verify、`Verify: 看起來沒問題`、無 RED、reviewer=implementer）與 Agent 代寫判定。
> 本 slug 已 in-flight，出貨仍舊 7。Demo 形式 = 狀態流程模擬器（好卡 vs 壞卡，人依 Demo Script 走）。Human verdict 由參與 Demo 的人類親填；本 hop 留 `NOT_REVIEWED`，Agent 禁代填 attestation。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context：Actors／Journey 步 6 假完成／chat 蓋章／B1 空欄／採用 hop -->
- [ ] 有新的前端流程（本題是方法論任務卡／拒收面，沒有新產品畫面）
- [x] 改變使用者下一步（摺站後 Decide／Spec／Build 不再等人按提交；缺 Verify 的下一步必須是停修，不是問 owner 要不要繼續）
- [x] 涉及角色交接（Build 實作者 → 獨立 T reviewer → Ship 審查者；seam 被偷走就沒有第二人可審）
- [x] 涉及人工核准（Ship 仍唯人寫 `verdict:`；B1 仍人類 `ACCEPTED`+attestation；Agent 代寫 = 未寫）
- [x] 涉及等待/退回/逾時（謂詞假停修；B1 latch；rewrite cap 用盡 Escalated；Q6 過期擋本 slug G2）
- [x] 涉及權限差異（實作者禁讀 1／2／3；coordinator 禁代填判定；未 2.1.0 採用端不得被遠端改線）
- [x] 涉及系統外動作（Cursor chat 蓋章、marketplace update、採用現場口頭中繼）
- [x] 涉及多種可行互動設計（Decision 已鎖 RP-1…RP-16 **要紅**；未鎖 owner **何時、在哪張卡**看見紅）
- [x] Stage 1 尚有操作流程不確定性（假完成 T 的人見面未釘；Q8 欄位名／Q10 計數落點仍移交 F1／F2）

→ 命中 8 條:第 3 站條件式必要,本站執行。2-decision 無流程層 OC 把該站標成跳過。

## Question
2-decision Risk「寫手用『已經五站了』省略 M11／M3／M1」＋ SC-3 對照稿「`Verify: 看起來沒問題` 的假 T」＋ SC-13／RP-1…RP-16＋ OC-10／OC-11：摺掉例行 G1／G2／S3 停之後，**owner 在哪一張卡、哪一步**看出 T 未完成，而不是看見綠勾？

三張結構不同的卡要比的是「人見面」，不是重開 6A／RP 表：

1. **缺欄當下就紅（推薦）**：A8 任務卡上，缺 Covers／Files／Verify／Blocked-by、或 Verify 只寫「看起來沒問題」，checkbox 不得冒充完成。
2. **hop 才出拒收板**：勾選可先綠，離開 Build 才列出 RP。
3. **Ship 才重建**：勾選綠到出貨，coverage 對不上才發現（現況病，棄）。

答案長什麼樣才算回答了：
- owner 能指著一張卡說「缺 Verify 時我看見 RP-1，下一步是停修，不是問我要不要繼續」。
- 同一張假 T 在三個 Variant 的決策點不同（寫卡時／hop 時／Ship 時）。
- 選定（推薦）Variant 寫得清：誰填、等誰、空／錯／權限不足／過期怎麼辦。
- 本 hop **不**改模板、**不**改 2-decision、**不**填 ACCEPTED。

## Method
- 實驗位置:本檔 Method 節的好卡／壞卡（**PROTOTYPE — not production**；純資料實驗，不進 throwaway code、不改 `scripts/`／`_templates/`）
- Demo 形式:**狀態流程模擬器**（人依 Demo Script 把同一張假 T 放進三張卡，看 owner 何時看見未完成）
- RP／Must-keep 已 lock → **3 個結構不同 Variant 只比人見面**（寫卡時紅／hop 時紅／Ship 才紅；不是換色換字，不重開 6A）
- 驗法:用 2-decision SC-3 對照稿、1-discussion M 表帶走列、dogfood-ping 空 attestation 仍開 Stage 4 各走一遍
- 本站只**推薦**人見面；2-decision 回寫列於 Verdict，本 hop 不落進 Decision 檔

### Variant 對照（必含項）

| 項 | Variant A T 卡上就紅（推薦） | Variant B hop 才出拒收板 | Variant C Ship 才重建（棄） |
|---|---|---|---|
| 主要角色 | Build 實作者寫 T 時；獨立 reviewer 同一張卡 | coordinator 評 Build→Ship；owner 看 hop 板 | Ship 審查者事後對 coverage |
| 真實目標 | 缺欄當下看出未完成 | 離開 Build 才准看洞 | 出貨前才補帳 |
| 入口 | A8 任務卡／A9 該 T 縫 | 站間 hop 拒收板 | A10／7-review coverage |
| 關鍵操作 | 四欄空或 Verify 散文 → 卡上 RP 晶片；勾選無效 | 勾選可先打；hop 列出 RP-n | 自由勾選；Ship 才對 S |
| 等待狀態 | 停在該 T；理由=該 RP 假，不是「先問 owner」 | 顯性「hop 被拒」；中間卡看起來完成 | 無等待面；中閘注意力已花完 |
| 空狀態 | 缺 Verify = 未完成，不是空白可過 | 板不出現 = 還能 hop（直到評謂詞） | 空 Verify 仍可綠勾 |
| 錯誤狀態 | `Verify: 看起來沒問題` 與缺欄同一紅 | 勾選綠、板紅，兩套真相 | checkbox 假完成（C 線主病） |
| 權限不足 | 實作者不能自審；Agent 不能寫 ACCEPTED | hop 板可由機器列 RP，仍不能代填 Ship | Agent 代寫 PASS 看起來像出貨 |
| 資料過期 | Q6 過期擋本 slug G2（卡上能指） | 過期列在 hop 板 | 過期假設仍走到出貨 |
| 中斷恢復 | 卡還在，缺哪欄還在 | 從 hop 板恢復，要回想哪張 T | 靠記憶找哪條 M 被偷 |
| 系統外下一步 | 補四欄／跑 RED／換 reviewer；不要 chat「都過」 | 讀板後回 Build 修；不要把板當蓋章頁 | 口頭說「都過」；正是 dogfood 捷徑 |

### Variant A — T 卡上就紅（推薦；只比人見面，不重開 6A）
操作序:寫 T 立刻填四欄 → RED 輸出貼在同一張 → reviewer ≠ implementer → 缺任一項則 checkbox 無效、卡上點名 RP。owner 看 A8／A9 **當下**看見未完成。謂詞假 = 停該 T 修。

**好卡（對照；不是施工）**

```
## T-1 讓缺 Verify 的 T 被看成未完成
- Covers: S-keep-m11
- Files: scripts/annex/five-station-rp.md
- Verify: 對照稿 T 缺 Verify 時拒絕輸出含 RP-1；本 T 貼該輸出
- Blocked-by: —
RED: FAIL test_s_keep_m11_missing_verify
reviewer: other-session（≠ implementer）
```

**壞卡 1 — SC-3 對照稿（C 線主場）**

```
## T-1 看起來做完了
- Covers: 五站相關
- Files:
- Verify: 看起來沒問題
- Blocked-by: —
[x] 完成
```

owner 在 A 看見：四欄洞＋RP-1（缺欄／散文 Verify）＋RP-2（無 RED、若自審再加 reviewer=implementer）。勾選無效。下一步=停修，不是問人。

**壞卡 2 — 無 RED／自審**

```
## T-2 已勾
- Covers: S-keep-m11
- Files: scripts/annex/five-station-rp.md
- Verify: pytest -k test_s_keep_m11
- Blocked-by: —
reviewer: 同一實作者
RED: （無輸出）
[x]
```

owner 在 A 看見：RP-2 T 未完成。勾選無效。

**壞卡 3 — S 含 TBD（M3／RP-3）**

```
## S-keep-m3
觀測: 適當處理即可（TBD）
```

owner 在 A 看見：Spec 卡紅，不得把該 S 當完成、不得靠它綠 T。

### Variant B — hop 才出拒收板（只比時機）
操作序:T 卡允許先勾 → coordinator 評 Build→Ship → 板列出 RP-1… → 停。與 A 的結構差:決策點在 hop，不在寫卡。資訊階層多一塊板。錯誤恢復要從板跳回 T。空狀態「板還沒出」看起來像已完成。2-decision SC-3 要的是「該 T 不得標完成」——B 讓完成標先寫上，再靠 hop 救，晚一步。

### Variant C — Ship 才重建（對照現況，棄）
操作序:作者勾選 → 中閘不再等人 → Ship 才對 coverage／M 表。與 A／B 的結構差:決策點在出貨。Journey 步 6「若四欄／seam 被省，勾選假完成」原樣重演。這是本包要修的病，不當選定。

### owner 看見什麼（RP 面；A 為準）

| RP | 壞卡（人看見的字） | A：owner 看見 | C：太晚看見 |
|---|---|---|---|
| RP-1 | T 缺 Verify／四欄空／`Verify: 看起來沒問題` | A8 卡上紅「RP-1」；勾選無效 | Ship coverage 對不上 S |
| RP-2 | 無 RED 輸出或 reviewer=implementer | A9 縫上紅「T 未完成」 | checkbox 已綠 |
| RP-3 | S 含 TBD／不可測 | Spec 卡紅，不得進 Build | 測試空轉也綠 |
| RP-4 | 測試名不含 S-id | 同 T 卡紅 | 鏈斷，Ship 對不回 |
| RP-5 | 缺 Files 或 Files ⊈ 5-tasks 聯集 | scope 紅 | 任務板說沒改、diff 有改 |
| RP-6 | 無原始輸出 | 摘要不當證據 → 紅 | 審查看摘要當完成 |
| RP-7 | 不可逆無 Quiz；或非不可逆被強制 Quiz | 前者 Ship 紅；後者違 G-out-1 | Quiz 變第三個例行停 |
| RP-8 | Ship 無人 `verdict: PASS` 卻 Done | A10 仍等人 | 機械綠當出貨 |
| RP-9 | hop 重寫第 3 次仍繼續 | Escalated；不准暗改 cap | cap 變裝飾 |
| RP-10 | Decide 重開第 2 次仍繼續 | 同上 | 同上 |
| RP-11 | Goal 離 Intake 後重開第 2 次仍繼續 | 同上 | 同上 |
| RP-12 | B1 未命中卻要求 `ACCEPTED` | 不產 Demo；此要求本身紅 | 假 latch |
| RP-13 | B1 命中、無 attestation，卻 hop 出 Spec | 停 Spec；chat「可以」不是判定 | dogfood 空欄仍開 4 |
| RP-14 | latch 未命中卻留下「請人審」 | 紅「不該問人」 | 等人次數加回 |
| RP-15 | 本 slug 被寫入五站狀態 | hop 拒；仍舊 7 | 觀測被自己污染 |
| RP-16 | Agent 代寫 `ACCEPTED` 或 Ship `PASS` | 當未寫並紅 | 機器出貨 |

M1→RP-4；M3→RP-3；M9→RP-5；M10→RP-6；M11→RP-1＋RP-2；M5／M12→RP-16。少一條 = 違 brief，不是簡化成功。

## 結構圖
- Variant A T卡上就紅（選定）
- Variant B hop才出拒收板
- Variant C Ship才重建（棄）
- 缺Verify不得完成
- Agent代寫=未寫
- 本slug仍舊7

## Demo Script
帶使用者走模擬器:同一張假 T 先放 A，再放 B，再放 C。不要問「喜不喜歡」。逐場確認:看到卡後知道下一步嗎？系統是否暗示勾選=完成？等待是否清楚（停修 vs 問人）？chat／marketplace 是否被當成判定？欄空時知不知道怎麼辦？能否撤回勾選、重跑 RED、改派 reviewer？

### Scenario AC-3
- 使用者角色:owner／Ship 審查者（先當 A8 讀者）
- 真實目標:缺 Verify 或 `Verify: 看起來沒問題` 的 T 不得標完成
- 起始狀態:Method 好卡 vs 壞卡 1（SC-3 對照稿）
- 操作步驟:只看該 T 四欄與勾選；對照 A（卡上 RP-1、勾選無效）／B（勾選綠、hop 板才紅）／C（勾選綠到 Ship）
- 系統回應:A 當下未完成。B 有兩套真相。C 重演 Journey 步 6 假完成
- 系統外下一步:補 Verify 為可跑命令＋貼輸出；不要 chat「都過」
- 觀察問題:看到綠勾時，知不知道它不算完成？系統有沒有暗示「已經五站了所以可省 Verify」？

### Scenario AC-3（seam／自審）
- 使用者角色:獨立 T reviewer
- 真實目標:無 RED 或 reviewer=implementer → T 未完成（RP-2／M11 seam）
- 起始狀態:壞卡 2（有 Verify 字、無 RED、自審）
- 操作步驟:要 RED 輸出與 reviewer 欄；A 同卡拒絕；B hop 才列 RP-2；C Ship 才問誰審的
- 系統回應:A 縫上紅。B 中間看起來已勾。C 四眼只剩欄位名
- 系統外下一步:另開 session 審；實作者不得自簽；重跑 RED 並貼原始輸出
- 觀察問題:系統是否暗示「有 Verify 字就等於跑過」？權限不足（自審）時下一步清不清楚？

### Scenario AC-2
- 使用者角色:owner
- 真實目標:宣稱「五站已簡化」但 M 表少 M11／M3／M1 → 看成違規，不是簡化成功
- 起始狀態:一份 4-spec／5-tasks 把四欄標「可選（已五站）」
- 操作步驟:對照 brief §5 與 Decision 約束 1–2、OC-11；A 在該列就紅；C 到 Ship 才點名
- 系統回應:少項被點名。不得寫成簡化成功。後站標可選 → 擋本 slug G2
- 系統外下一步:收回「可選」；去向維持 `M11 → R-x/S-y`，不另發 ID
- 觀察問題:「已經五站了」這句出現時，下一動作是停修還是繼續摺？

### Scenario AC-4
- 使用者角色:Ship 審查者
- 真實目標:Agent 寫入 `ACCEPTED` 或 Ship `PASS` = 未寫（RP-16／RP-8／M5）
- 起始狀態:md 頂欄被 Agent 填了 PASS；無人類 attestation
- 操作步驟:只看頂欄與 attestation 行；嘗試 hop 出 Spec／標 Done
- 系統回應:A／B 當沒寫並紅。C 看起來已出貨。chat「Treat as PASS」不得入欄（OC-6）
- 系統外下一步:人親寫頂欄；Agent 禁改 attestation。本 hop 不示範填 ACCEPTED
- 觀察問題:系統有沒有暗示「欄位有字=人審過」？

### Scenario AC-1
- 使用者角色:coordinator（F2 後）／owner
- 真實目標:謂詞假 = 停該站修，不是改問人（G-out-1）
- 起始狀態:新 slug Decide／Spec／Build 完成、中間 latch 未命中；另有一 T 缺 Verify
- 操作步驟:看前進紀錄有沒有「請人審 A4／A7」；缺欄時看停修理由
- 系統回應:中間無人停。缺 Verify 的停因是 RP-1 假，不是「先問 owner 要不要繼續」。A 在 T 卡；B 在 hop 板；C 沒停
- 系統外下一步:修該 T。不要開審查 widget
- 觀察問題:等待狀態是「停修」還是「等人蓋章」？

### Scenario AC-6
- 使用者角色:owner
- 真實目標:B1 命中且 attestation 空 → 不得 hop 出 Spec（RP-13）；chat「可以」不是判定
- 起始狀態:本檔 Human verdict=`NOT_REVIEWED`；attestation 空（本 hop 真實狀態）；對照 dogfood-ping 空欄仍開 Stage 4
- 操作步驟:嘗試用 chat「准開 Stage 4」帶走；看 A 是否仍拒
- 系統回應:A 停 Spec。B 若把 chat 當 hop 准許 = 5B 回流（已拒）。未 Demo = NOT_REVIEWED ≠ ACCEPTED
- 系統外下一步:人類親做 Demo、親填 ENUM＋attestation。Agent 禁代填
- 觀察問題:系統是否暗示「有 3-prototype.md 就能進 4」？

### Scenario AC-8
- 使用者角色:本 slug 執行者
- 真實目標:對 `docs/dev/five-station-simplify/` 要求五站自動前進、跳過例行 G1／G2 → 跳不過（RP-15）
- 起始狀態:本目錄已有 1／2／3 的 md = in-flight
- 操作步驟:要求五站 hop 跳過本 slug 的 G1／G2
- 系統回應:拒。仍舊 7 直到自己的 Ship。A 在 hop 當下拒；C 會拿自己當新 5 白老鼠
- 系統外下一步:本 slug 繼續走舊 7 閘。不要改 STATUS 假裝已切五站
- 觀察問題:doctor 綠或 marketplace 已換 hops，會不會被讀成「本目錄已經五站了」？

### Scenario AC-7
- 使用者角色:後站規格者
- 真實目標:M 表每條高影響列有 `M11 → R-x/S-y | Non-Goal:<reason>`；禁把 M15／M16 寫成 Non-Goal
- 起始狀態:2-decision Must-keep Disposition 種子表
- 操作步驟:抽 M11／M3／M1／M15；看 A 是否能從種子恢復；C 散文「有處理」
- 系統回應:A／B 指得到列。C 與去向空白無法證明列還在。M15／M16 是約束
- 系統外下一步:4-spec 落具體 R/S id（本 hop 不發 id）
- 觀察問題:中斷後能否從 M 編號恢復，還是要靠記憶？

## Result
回寫 2-decision 的預定答案（本 hop **不**改 Decision 檔）：推薦 **Variant A**（T 卡上就紅）。B 讓完成標先寫上、hop 再救，違反 SC-3「該 T 不得標完成」。C 重演假完成，棄。RP 人見面見 Method 表。Risk「已五站故省 M11／M3／M1」的人對面 = A8／A9 當下紅，不是 Ship 才重建。2-decision OC 表不改。

| 場 | 選定人見面（A） | 負向 |
|---|---|---|
| AC-3 缺 Verify | 卡上 RP-1；勾選無效 | `Verify: 看起來沒問題` 仍綠 |
| AC-3 seam | 卡上 RP-2；自審無效 | 無 RED 仍勾 |
| AC-2 少 M | 少項=違 brief | 「已五站」當省略理由 |
| AC-4 代寫 | Agent PASS=未寫 | 頂欄有字算出貨 |
| AC-1 停修 | 理由=謂詞假 | 改問 owner |
| AC-6 B1 | 空 attestation 不得離 Spec | chat「可以」帶走 |
| AC-8 freeze | 本 slug hop 拒 | 當新 5 白老鼠 |
| AC-7 去向 | `M11 → R-x/S-y` | M15／M16 標 Non-Goal |

證據:用 SC-3 壞卡走完 A／B／C；只有 A 讓 owner 在勾選當下看見未完成。正式模板／牙未改。本 hop Human verdict 留 NOT_REVIEWED。

## User Demo Feedback
- Demo date:
- Participants:
- Variant reviewed: A（推薦）／B／C（棄）；待人類親走
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED | role=owner | scenario=AC-3
- Verdict attestation:

## Verdict
- 預定回寫 2-decision：內部技術選擇加一行「第 3 站推薦 Variant A（T 卡上就紅）；不重開 6A／RP」。確認紀錄預定留「prototype 回寫 | 2026-09-13 | C 線模擬器推薦 A；Human verdict 仍 NOT_REVIEWED」。**本 hop 不改 2-decision.md**（獨立、draft、待人類 Demo）。
- 實驗產物:好卡／壞卡留在本檔 Method；無 throwaway branch、無正式碼。
- frontmatter `status: draft`。未 Demo = NOT_REVIEWED ≠ ACCEPTED。Agent 未代填 attestation。不送 G2、不開 4-spec、不改 STATUS、不合併。
