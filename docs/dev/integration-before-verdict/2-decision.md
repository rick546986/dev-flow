---
feature: integration-before-verdict
stage: 2-decision
status: approved
verdict: PASS
owner: rick
reviewers: [user]
updated: 2026-09-12
---

# 2. 收斂 — 整合須在 Fresh／Verdict 之前

> 把 `1-discussion.md` 的發散收成 Decision。G1 已核:`verdict` PASS、`status` approved、OC-1～OC-3 ✅。契約不 bump。不實作模板／守衛碼、不碰 `#196`、不發版。
> owner 2026-09-12 已 lock 方向：整合在 Fresh／雙軸／Verdict 之前；lane full；本 slug 當第一條真實 full lane。1-discussion 留當時「只 Stage 1、不送 G1」原文；本檔才改口成方案決策。

## Approaches Considered

### 決策點：對帳策略
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A | **承認 2c/2d 散文已搬**。本 slug 做三件事：鎖填檔牙、掃仍在教舊序的活教師、用本 slug 真跑 1→7 | 對準 G-out-1/3；不拆已綠的模板順序牙；剩餘缺口就是「牙鎖的是模板字串、不是填好的 7-review」+ 活教師仍教 `2c = Fresh` | 2c 編號肌肉記憶還在；要忍住不重編號 | 中 | `1-discussion.md:23-26` 散文已 2c→2d；`1-discussion.md:93` Q5 假設剩餘=鎖牙／範例／STATUS；`_templates/7-review.md:100-120` 2c 已在 2d 前；`scripts/check-stage67-enforcement.sh:298-322` 與 `scripts/check-integration-regression-guard.sh:484-518` 已釘模板字面順序。成本 `[Assumption]` |
| B | **重編號**整份 Stage 7 清單（新 id，消滅「2c = Fresh」） | 從根挖掉舊編號；範例／manifest 不能再靠「2c」混過去 | 現有牙硬咬 `2c. **整合回歸**`；重編號等於重寫一組守衛＋指南 renderer＋節點鏈；Diff 大、假綠風險高 | 高 | `scripts/check-integration-regression-guard.sh:484-486` 用 `2c.\s*\*\*整合回歸\*\*` 抓段；`skills/dev-flow/stage7/nodes/S2c-integration.md:24-25` 與 `guides/guide-dev-flow.html:1718-1738` 已用 2c→2d。劣的「假綠」`[Assumption]` |
| C | **只改文件／範例**，不加新牙 | 最短；零守衛迴歸 | 誰都能跳過 2c；G-out-2 仍可靠「證據不算數」勾過；違反「現場仍可能走舊序」的高風險假設 | 低 | `1-discussion.md:62` 誰都可跳過 2c、無主機攔截；`1-discussion.md:73` G-out-2 不能只靠「證據不算數」；`1-discussion.md:69` `[Assumption]` 現場仍按舊序 |

### 決策點：ALREADY_SYNCED 牙
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| AS-1 | **填檔牙**：feature 的 7-review 若記 `ALREADY_SYNCED` 卻只有「證據不算數／輸出不算數」、沒有重綁後 Source SHA 或明示 FAIL → 機械紅 | 直接鎖 G-out-2／AC-2；現有模板字串牙可留作地板 | 要定「結論形狀」；可能碰 gate-consistency 錨句（Q6） | 中 | `1-discussion.md:108-111` AC-2；`_templates/7-review.md:110-113` 散文已有恢復二選一；`scripts/check-stage67-enforcement.sh:314-315` 只咬模板有「重跑 Final Fresh」，不咬填好的 7-review。形狀細節 `[Assumption]`（4-spec 再釘） |
| AS-2 | **只靠現行模板字串牙**（`check-stage67`／`test-evidence-gauntlet` 已查「重跑 Final Fresh」） | 零新碼；模板已綠 | 填檔仍可只寫作廢就勾；腳本 GUIDANCE 仍停在「輸出不算數」 | 低 | `scripts/test-evidence-gauntlet.sh:493-497` 模板恢復路徑牙；`scripts/devflow-integration-regression.sh:204-205` GUIDANCE 只說不算數、沒寫重綁或 FAIL |
| AS-3 | **改整合腳本演算法**（例如 `ALREADY_SYNCED` 自動當 FAIL、或腳本自己重綁） | 入口唯一 | 討論 Non-Goals 禁重寫演算法；腳本職責是只算只判、不動樹 | 高 | `1-discussion.md:86`「不重寫整合腳本演算法本身」；`scripts/devflow-integration-regression.sh:9-10` 只算只判、絕不動樹 |

### 決策點：活教師掃蕩時機
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| T-now | **本 slug 實作站一次掃完活教師**：example 舊編號、腳本檔頭「Exit Checklist 計算工具」、manifest `2c`=gauntlet、散發副本檔頭 | 第一條真實 full lane 期間不再教舊序；Q7 有著落 | 要改 example／散發檔頭，進 Stage 6 Files | 中 | `1-discussion.md:95` Q7 移交；`example/contract-expiry-reminder/7-review.md:24`「執行清單 2c 的 Final Fresh Run」；`example/contract-expiry-reminder/4-spec.md:223`「2c gauntlet」；`manifests/p4-gauntlet-gates.md:52` 同錯號；`scripts/devflow-integration-regression.sh:2` 與 `docs/dev/tools/devflow-integration-regression.sh:2` 仍寫 Exit Checklist 工具 |
| T-later | 等本 slug **自己跑完 Stage 7** 再改範例 | 先有一份「新序真跑」樣張再改舊樣張 | 真跑期間採用者仍會抄 `2c = Fresh`；G-out-3 的載體自己被舊樣張帶偏 | 低 | `1-discussion.md:74` G-out-3 本 slug 要鎖「出貨樹=核准樹」；帶偏 `[Assumption]` |
| T-hist | 連派工／HISTORY／stage7-loop **一併改口** | 全文搜「舊序」更乾淨 | 把當時紀錄改成現在的說法；審計軌跡斷 | 中 | `notes/dispatch-v380-landing.md:1011-1018` 是當時派工；`docs/dev/HISTORY.md` 只增不改；`_templates/2-decision.md` 頂註：1-discussion 留當時說法 |

## 方案架構圖
[A] 鎖牙+掃教師+真跑(選定)
[AS-1] 填檔牙：重綁或 FAIL
[T-now] 活教師實作站清完
[keep] 2c/2d 不重編號

## Decision
採 **A + AS-1 + T-now**：承認 tip 模板／指南／Stage 7 節點鏈已經是 2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 只准文件；本 slug 不重編號、不重寫整合腳本演算法。剩餘交付是 (1) 填檔牙：`ALREADY_SYNCED` 只能「重綁 Final Fresh 的 Source SHA」或「本項 FAIL」，不能只寫「證據不算數」過關；(2) 一次掃完仍在教舊序的**活教師**（完整範例編號、腳本／散發檔頭、gauntlet manifest）；(3) 用本 slug 自己走完 1→7，把「出貨樹=核准樹」鎖成第一條真實 full lane。歷史派工與 HISTORY 當紀錄保留。G1 已核。本 hop 不改碼。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| B 重編號 | 現有牙硬咬 `2c. **整合回歸**`；重編號是另一場守衛大改，不解決「填檔可跳過／只寫作廢」這兩個真缺口。 |
| C 只改文件 | 無主機攔截；跳過 2c 與「只寫作廢」仍能過；G-out-2 落空。 |
| AS-2 只靠模板字串牙 | 牙已綠、痛仍在：填好的 7-review 與腳本 GUIDANCE 都還能只說「不算數」。 |
| AS-3 改整合腳本演算法 | Non-Goal；腳本契約是只算只判、不動樹。 |
| T-later 等自己跑完再改範例 | 第一條真實 full lane 期間舊樣張繼續教 `2c = Fresh`。 |
| T-hist 改寫派工／HISTORY | 當時紀錄不是活教師；改口會斷審計。 |

## Rationale
owner 要的不是「再搬一次散文」。tip 上 `_templates/7-review.md`、指南 renderer、`S2c-integration`→`S2d-fresh`、以及 `check-stage67`／`check-integration-regression-guard`／`test-evidence-gauntlet` 的模板順序牙，**已經**是整合在 Fresh 前。派工行號 `:94`／`:133`／`:281` 對不上現檔。

還活著的舊序有兩類。第一類是**教師**：example 與 manifest 仍把 2c 當成 Final Fresh／gauntlet；整合腳本檔頭仍自稱 Exit Checklist 工具。採用者抄範例就會走舊編號。第二類是**牙的射程**：現有檢查咬的是模板字串，不是一份填好的 7-review。人可以跳過 2c，或在 `ALREADY_SYNCED` 只抄「證據不算數」後勾過。腳本對 `ALREADY_SYNCED` 的 GUIDANCE 也停在「輸出不算數」，沒把恢復路徑講成可執行下一步。

A 留下已綠的 2c/2d 與模板牙，把力氣放在填檔牙與活教師。B 為消滅肌肉記憶去拆已鎖的錨，成本高、不補填檔缺口。C 與 AS-2 重複「文件已搬所以結束」的陷阱。T-now 讓這條 full lane 自己不再被舊樣張帶偏；T-hist 不碰，因為派工與 HISTORY 是當時事實。

## 既有脈絡
對帳快照（2026-09-12 tip `67481d6`，#199 之後）：

| 層 | 現況 | 舊序？ |
|---|---|---|
| `_templates/7-review.md` 頂註 2c/2d、Exit 只確認「已在 Fresh 前完成」、Verdict 後禁改碼 | 已搬 | 否 |
| `guides/guide-dev-flow.html`、`skills/dev-flow/stage7/nodes/S2c*`／`S2d*` | 已 2c→2d | 否 |
| `check-stage67-enforcement.sh` ST、`check-integration-regression-guard.sh` 模板順序、`test-evidence-gauntlet.sh` P0-1 | 咬模板字面 | 否（牙在；射程=模板） |
| `example/contract-expiry-reminder/7-review.md:24`、同檔 html、`4-spec.md:223` | `2c` = Final Fresh／gauntlet | **是（活教師）** |
| `manifests/p4-gauntlet-gates.md:52` | `2c` = gauntlet 命令 | **是（活教師）** |
| `scripts/devflow-integration-regression.sh:2` 與散發副本檔頭 | 自稱 Exit Checklist 工具 | **是（活教師）** |
| 同腳本 `ALREADY_SYNCED` GUIDANCE | 只說輸出不算數 | **弱（無恢復句）** |
| `notes/dispatch-v380-landing.md`、HISTORY、stage7-loop | 當時派工／紀錄 | 否（死紀錄，不改） |
| `docs/dev/STATUS.md` Active | 本 slug 在 Stage 1；feature branch 禁改正本表列 | 列已在 Active，不是舊序教師 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 填檔牙形狀未釘，Stage 4 之前各寫各的 | Decision 只鎖「有重綁 SHA 或明示 FAIL，否則紅」。欄位／腳本名進 4-spec；OC-1 先收窄「沿用既有檢查家族，不另造第二套整合工具」 |
| 咬填檔時誤殺 `N_A_NO_INCOMING` 或未跑 2c 的 draft | 牙只在宣稱勾過整合項／送 G3 時發動；n-a 與 draft 不預先紅。細節 4-spec |
| 掃 example 編號牽動 fixture（`spec-gate-dd-subsection` 抄了 4-spec 的 2c gauntlet 句） | Stage 6 把衍生 fixture 與正本 example 列進同一 T；改編號不同步 = 該 T 紅 |
| 重編號誘惑（B）在實作時回流 | B 進 Rejected；要重編號必須回本站改 Decision |
| 有人把歷史派工改口當「對帳完成」 | T-hist 進 Rejected；OC-2 釘死不改 HISTORY／dispatch 當時句 |
| feature branch 手改 STATUS 表列 | 流程層 OC-4：本 branch 不跑 `status-update.sh` 改正本；merge 後由整合分支更新 Stage |
| 本 hop 被當成已過 G1 | G1 已按 owner chat「都過」落檔（`verdict` PASS、`status` approved）；翻案回本站 |

## Success Criteria
- SC-1(G-out-1)：本 slug 後續走到 Stage 7 並勾 Exit 之後，7-review 所記 Source SHA 與 `git rev-parse HEAD` 逐字相同。對照樣本（故意 Verdict 後才合）必須能指出兩 SHA 不同。
- SC-2(G-out-2)：一份 7-review 記 `ALREADY_SYNCED` 且只寫「證據不算數／輸出不算數」、沒有重綁後 Source SHA、也沒有本項 FAIL → 指定檢查 exit ≠ 0。有重綁 SHA 或明示 FAIL 的對照樣本 exit 0。
- SC-3(活教師)：`example/contract-expiry-reminder/` 的 7-review／4-spec、`manifests/p4-gauntlet-gates.md`、整合腳本與散發副本檔頭，不再把 2c 寫成 Final Fresh／gauntlet，也不再把整合工具寫成 Exit Checklist 程序。`rg -n '執行清單 2c 的 Final Fresh|Exit Checklist.*整合回歸.*計算工具'` 在這些活路徑上零命中。
- SC-4(不回潮)：`scripts/check-stage67-enforcement.sh`、`scripts/check-integration-regression-guard.sh`、`scripts/test-evidence-gauntlet.sh` 的模板順序／恢復路徑項仍綠；`_templates/7-review.md` 仍是 2c 整合 → 2d Fresh。
- SC-5(G-out-3)：本 slug 留下 Stage 1→7 產物（本 hop 只交 Stage 2），無「跳過 2c」或「Exit 才合併」的流程宣告。
- SC-6(Non-Goal)：未改 `#196`、未實作九條制度缺口、未重寫整合腳本演算法、未 bump plugin、未開 Stage 3 檔。本檔 `verdict` PASS 來自 owner chat「都過」，不是 Agent 自裁。

## Scope & Non-Goals(定稿)
- In：A 對帳策略；AS-1 填檔牙契約（形狀進 4-spec）；T-now 活教師清單；本 slug 後續真跑 1→7；Q6 錨句只鎖「整合在 Fresh 前」與「ALREADY_SYNCED 必重綁或 FAIL」，不重寫已正確的 2c 散文。
- Out：B 重編號；C／AS-2 只改文件；AS-3 改整合腳本演算法；T-hist 改寫派工／HISTORY；`#196`／gate-twin Backlog；九條制度缺口實作；Windows 真機驗證；本 hop bump plugin；本 hop 實作守衛碼；本 hop 不開 Stage 3 檔。

## Owner Calls(自判裁決,已核)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | 填檔牙**沿用既有檢查家族**（`check-stage67`／gate-consistency／7-review 形狀檢查之一），不另造第二套整合工具。使用者只被問到「整合在 Fresh 前」；「沿用既有家族」是 owner 延伸 | 另造家族靠近第二套方法論；現有模板順序牙已綠，缺的是射程延伸到填檔 | `1-discussion.md:78-79` 未選定改哪些守衛；`scripts/check-stage67-enforcement.sh:298-322` 已有 ST 組。延伸本身 `[Assumption]` | 要新入口／新腳本；與「不重寫演算法／不重編號」要重審 | ✅ |
| OC-2 | **不改** `notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/` 的當時舊序句。使用者 brief 要對帳模板 vs 腳本／守衛／範例／文件；「歷史當死紀錄」是收窄 | 那些句子是當時派工事實；改口 = 假裝第一次裁決本來就是新序 | `1-discussion.md` Interview「1-discussion 留當時說法」慣例；`docs/dev/HISTORY.md` 只增不改；T-hist 已拒 | Scope 加上改寫歷史；審計斷、對帳變假 | ✅ |
| OC-3 | 本 feature branch **不**跑 `status-update.sh` 改正本 Active 列。Stage 欄留 main 上的 `1-discussion`，merge 後由整合分支更新。標**流程層** | 母版 STATUS 只在整合分支維護；腳本在 feature branch 拒改正本表列 | `docs/dev/STATUS.md:10-26`；`1-discussion.md:98` 表列只准 `status-update.sh`；本 hop brief「only if needed」 | 本 PR 帶 STATUS 列改動，與並行 session 互蓋 | ✅ |

### 內部技術選擇(下層,告知即可)
- 本 hop 不 bump plugin、不改 `_templates/7-review.md` 正文（散文已對）。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口成 Decision。
- Q6 錨句候選（4-spec 再釘確切字）：「整合回歸在 Final Fresh 之前」「ALREADY_SYNCED 不得只寫證據不算數」。
- Stage 3 不預先跳過；觸發判定留給第 3 站（本檔無「跳過 Stage 3」流程層 OC）。
- 本 hop 產審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。

## ADR 晉升檢查
- 難逆轉:否（G3 前可改本檔 Decision／OC；牙尚未落地）
- 反直覺:是（散文已搬仍要開 full lane；「2c」在活教師裡仍是 Fresh）
- 真 trade-off:是（重編號挖肌肉記憶 vs 留 2c 錨、把力氣放填檔牙）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-12 | owner chat「對」核准 Stage 1 方向（整合在 Fresh／雙軸／Verdict 前、full lane）。本 hop brief 指定 Stage 2 收斂並對帳模板 vs 腳本／守衛／範例／文件。三決策點：對帳策略／ALREADY_SYNCED 牙／活教師時機。
- Stage 1 改口 | 2026-09-12 | 1-discussion 仍 draft、Q5 `[~]`、Q6／Q7 `[>]`；本檔改口為 Decision。不回改正本討論。
- G1 | 2026-09-12 | owner 在 chat 說「都過」（G1 / Owner Calls passed）。3 位 reviewer 一致選 #202（已合為 `0afc1fd`）。OC-1～OC-3 隨 Decision 一併視為接受。owner 自審(有記錄)；reviewers: [user]
