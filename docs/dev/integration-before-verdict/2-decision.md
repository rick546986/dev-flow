---
feature: integration-before-verdict
stage: 2-decision
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-12
---

# 2. 收斂 — 整合須在 Fresh／Verdict 之前

> 把 `1-discussion.md` 的發散收成一個選定方案。**本 hop 只到 Stage 2 落檔，不送 G1、不填 Human PASS。**
> `verdict:` 留空；`status:` 留 `draft`；OC 狀態留「待人審」。1-discussion 仍 draft（#199 明示不宣稱 G1）；owner 2026-09-12 書面 brief + chat「對」核准 Stage 1 方向，本檔才改口成 Decision。
> 本 PR **不實作**模板／守衛／範例改碼（Out of scope = Stage 3+、#196、發版）。Decision 只鎖後續站要鎖什麼。

## Approaches Considered

### 決策點：剩餘工作形態（Q5）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A 鎖牙＋對帳 | 承認現行 `_templates/7-review.md` 2c→2d 已是 SOP。本 slug 不重寫已對散文；把牙、範例、教學殘句、腳本 hint 對到同一序 | 對準 Stage 1 已核事實；不燒已綠的 ST／graph／integration-guard | 現場若仍跳過 2c，散文本身仍擋不住 | 中（對帳面多、模板正文少） | `1-discussion.md:23-25` 模板／指南／節點已是 2c→2d；`:93` Q5 假設「剩餘主要是鎖牙／範例／STATUS」；本 hop 對帳確認該假設（見 Rationale）。成本 `[Assumption]` |
| B 重寫清單 | 當現行 7-review 仍髒，從零重排步號或重寫 2c／2d 正文 | 若散文真的還是舊序，這才治本 | tip 散文已搬；重寫會打到已綠守衛與節點鏈，再造一次編號漂移 | 高 | `1-discussion.md:154-157` CONFIRMED「現行模板散文已是整合→Fresh」；`scripts/check-stage67-enforcement.sh:298-322` 已咬新序。成本 `[Assumption]` |
| C 只改文件 | 只改 example／STATUS 敘事，不加新牙、不碰腳本 hint | 最短；零守衛風險 | 討論假設人會跳過 2c；無牙則 G-out-1/2 仍靠自律 | 低 | `1-discussion.md:62`「誰都可跳過 2c；沒有主機層攔截」；`:73` G-out-2 要可執行下一步，不能只靠「證據不算數」。成本 `[Assumption]` |

### 決策點：牙鎖在哪（Q6）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| T-core 教學面＋既有牙 | 既有 ST／graph／integration-guard **不回退**。本 slug 後續站補「教錯的面」：example 仍寫 `2c = Fresh`、4-spec／manifest／gauntlet 測試文案、整合腳本 GUIDANCE 仍講 Exit Checklist | 對準實際漂移；牙已鎖模板序，缺的是採用者讀到的樣張與 hint | 擋不住「讀對清單仍跳過 2c」的主機層 | 中 | 本 hop 對帳：`example/contract-expiry-reminder/7-review.md:24`、同檔 html、`example/contract-expiry-reminder/4-spec.md:223`、`manifests/p4-gauntlet-gates.md:52`、`scripts/test-evidence-gauntlet.sh:500-511`、`scripts/devflow-integration-regression.sh:203,213`。既有牙：`scripts/check-stage67-enforcement.sh:298-322`、`scripts/check-integration-regression-guard.sh:469-518`、`skills/dev-flow/stage7/nodes/S2c-integration.md:24-25` |
| T-host 主機攔截 | 沒做 2c（無整合結論／游標未過 S2c）就不得進 2d Fresh／Verdict | 對準「誰都可跳過 2c」 | 靠近 host-stack-fit 的 `--action` 收據牙；本 hop 禁實作；易兩 feat 搶同一執法面 | 高 | `1-discussion.md:62` 無主機攔截；host-stack-fit 已鎖 script-minted receipt。成本與碰撞 `[Assumption]` |
| T-none 不加牙 | 只靠已搬的散文 | 零新檢查 | 派工／範例仍教舊編號；人照樣 Fresh→Verdict→Exit 才合 | 低 | `1-discussion.md:42` STATUS／派工仍講舊旅程；`:69` 現場仍按舊序 = `[Assumption]`（期限本站；本 hop 對帳已見教學殘句，假設部分兌現） |

### 決策點：範例舊編號何時改（Q7）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| E-now 本 slug 改 | Stage 4–6 在本 feat 改 `example/contract-expiry-reminder` 的 2c=Fresh 句、其 4-spec 註、html twin，並一併改 manifest／gauntlet 測試標籤／腳本 GUIDANCE | 第一條真實 full lane 走完時，採用者讀到的樣張與 SOP 同序 | 改已 shipped 樣張要標「示範值更新」，不能假裝當年就是新序 | 中 | `1-discussion.md:95` Q7 移交後續站；`:26` 範例仍把 2c 當 Fresh；`:114` AC-3 看的是人讀到的清單序 |
| E-later 另開薄刀 | 本 slug 只寫 Decision，改樣張另票 | 本票較瘦 | 第一條 full lane 結束後樣張仍教舊編號；G-out-3 載體不完整 | 低 | `1-discussion.md:74` G-out-3 要用本 slug 鎖「出貨樹=核准樹」。另票延後為 `[Assumption]` |
| E-never 留歷史 | 樣張當考古、不改編號 | 零擾動 | 採用者照範例會走舊編號——Stage 1 已 CONFIRMED 的痛 | 低 | `1-discussion.md:166-169` CONFIRMED 範例編號與現行清單不一致 |

## 方案架構圖
[A] 鎖牙＋對帳，不重寫已對 2c 散文（選定）
[T-core] 既有 ST／graph／guard 不回退；補教學面牙（選定）
[E-now] 本 slug 改 example／4-spec／manifest／腳本 hint（選定）

## Decision
採 **A + T-core + E-now**：tip 上 `_templates/7-review.md` 的 2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 只准文件，**已經是 SOP**。本 slug 不重寫這段已對散文，也不改步號。後續站（本 Decision 鎖定、本 PR 不施工）要做的是：既有模板序牙不回退；把仍教「2c = Final Fresh」或「合完記在 Exit」的範例、4-spec 註、manifest、gauntlet 測試標籤、整合腳本 GUIDANCE 對到 2c→2d；`ALREADY_SYNCED` 只能走「重綁 Fresh」或「本項 FAIL」。STATUS 表列只在 `main` 用 `scripts/status-update.sh` 改，不進本 feature branch。本 hop 不填 G1 PASS、不實作、不動 #196、不發版。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| B 重寫清單 | 模板／指南／節點／ST 牙已是 2c→2d；重寫會打綠牙、再造編號漂移。 |
| C 只改文件 | 無牙則跳過 2c 與「只寫證據不算數」仍能過；G-out-1/2 落空。 |
| T-host 主機攔截 | 本輪不選。執法面靠近 host-stack-fit 收據牙；本 hop 禁實作。若 T-core 落地後仍測得到跳過 2c，另開 feat，不塞進本 Decision 預設包。 |
| T-none 不加牙 | 教學殘句還在；人照範例會走舊編號。 |
| E-later 另開薄刀 | 本 slug 被指定當第一條真實 full lane 的載體；樣張不同步則載體不完整。 |
| E-never 留歷史 | Stage 1 已確認採用者照範例會走舊編號。 |

## Rationale
Owner 要的結果是「出貨樹 = 核准樹」，不是「再搬一次 7-review 頂註」。Stage 1 已核、本 hop 覆核：頂註 2c 在 2d 前、Exit 只確認「已在 Fresh 之前完成」、`ALREADY_SYNCED` 已有重綁／FAIL、Verdict 後改碼作廢 G3；指南 renderer 與 `S2c-integration` → `S2d-fresh` 同序；`check-stage67-enforcement.sh` ST 組與 `check-integration-regression-guard.sh` 已咬「工具先於合併、整合先於 Fresh、Exit 不得再合」。

還在教舊序或舊編號的是**採用者會抄的面**，不是模板頂註：完整範例把「執行清單 2c」寫成 Final Fresh；同套 4-spec 把 gauntlet 掛在 2c；`manifests/p4-gauntlet-gates.md` 與 `test-evidence-gauntlet.sh` M2 標籤仍說「模板 2c」；`devflow-integration-regression.sh` 的 `N_A_NO_INCOMING`／`--no-fetch` hint 仍指向 Exit Checklist。Q5 假設因此從「待 Stage 2 對帳」收成：**剩餘主軸是鎖與對帳，不是重寫 2c**。A 承認現況；T-core 補教錯的牙；E-now 讓第一條 full lane 走完時樣張不再唱反調。

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 模板已對，人以為本 slug 無工可做 | Decision／SC 釘教學面清單；Q5 過期擋 G2 的條件改為「對帳清單未清」才擋，不是「散文還沒搬」 |
| 改 shipped 樣張被讀成篡改歷史 | 示範值旁加「編號已對現行 2d，原 2c=Fresh 是舊編號」；1-discussion 留當時說法 |
| T-core 擋不住跳過 2c 的 agent | 記為本輪 Known limit；T-host 進 Rejected，翻案回本站另開 feat |
| 獨立 Implementer 雙 PR 撞同一 Decision | 本 PR 只交 2-decision；不搶 #196、不改模板碼 |
| 腳本 GUIDANCE 改字打到 integration-guard 字面錨 | Stage 4 先對 `check-integration-regression-guard.sh` 咬的是模板 2c 不是 GUIDANCE；改 hint 前重跑該牙 |
| feature branch 手改 STATUS | OC-4：本 branch 不碰表列；stage 推進留給 `main` 上 `status-update.sh` |
| 把 #196／九條缺口／發版塞進來 | Non-Goals 釘死；SC-6 可觀測 |

## Success Criteria
- SC-1（G-out-1／AC-3）：人按執行清單做 Stage 7 時，整合步出現在 Fresh、雙軸、Verdict **之前**。對照：`_templates/7-review.md` 頂註步序 + 本 slug 自己的 `7-review.md`。看到：整合步序號／位置在 Fresh／Verdict 前；Exit 不再出現「合併 INTEGRATION_SHA」動作。
- SC-2（G-out-2／AC-2）：腳本印 `ALREADY_SYNCED` 時，7-review 整合項只能「重綁 Fresh（Source SHA = 當下 HEAD）」或「本項 FAIL」。看到：沒有只寫「證據不算數」卻勾過。試：已合過、merge-base 被污染的 fixture／實例。
- SC-3（AC-1）：本 slug 走到 Stage 7 且人寫下 Verdict 後，`7-review` 所記 Source SHA 與 Exit 之後 `git rev-parse HEAD` **逐字相同**。
- SC-4：`example/contract-expiry-reminder/7-review.md`（及 html twin）不再把「執行清單 2c」寫成 Final Fresh Run；對應 4-spec 註改指 2d／gauntlet，不指 2c。
- SC-5：既有 ST／graph／integration-guard 仍綠；本 slug 補的教學面牙（或等價檢查）能紅「2c=Fresh」或「Exit 才合」突變。
- SC-6（Non-Goal）：本 Decision 落地過程未改 open PR #196 範圍、未 bump plugin／打 tag、本檔 `verdict:` 不是 Human PASS（空或 pending）。

## Scope & Non-Goals(定稿)
- In：選定 A + T-core + E-now；後續站對帳並改：example 舊 2c 編號、4-spec 示範註、manifests/p4、gauntlet 測試標籤、整合腳本 GUIDANCE／`--no-fetch` hint；維持既有模板序牙；`ALREADY_SYNCED` 恢復路徑保持可執行。
- Out：本 PR 實作任何模板／腳本／範例改碼；重寫已對的 7-review 2c／2d 正文；T-host 主機攔截；#196；九條制度缺口（A-1~B-2）；發版／bump plugin；Windows 真機；重寫整合腳本演算法；本 hop 填 G1 PASS；feature branch 改 `docs/dev/STATUS.md` 表列。

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | 不重寫已對的 `_templates/7-review.md` 2c／2d 散文與步號。使用者 Q5 只假設「剩餘是鎖牙」；「散文凍結、只對帳」是 owner 延伸 | 重寫 = 走 B，打已綠牙 | `1-discussion.md:93` Q5；本 hop 對帳 `_templates/7-review.md:100-120`。延伸本身 `[Assumption]` 直到 G1 | 變 B：Scope 加上重寫頂註；ST／graph／guard 要重錨 | 待人審 |
| OC-2 | 整合腳本 `GUIDANCE` 與 `--no-fetch` 仍講 Exit Checklist，算教學漂移，納入本 slug T-core 對帳面。使用者 Q6 只移交「gate-consistency／renderer 錨」；收進腳本 hint 是延伸 | hint 會把 reviewer 導回 Exit 才記 n-a | `scripts/devflow-integration-regression.sh:203,213`；`1-discussion.md:95` Q6。延伸 `[Assumption]` | GUIDANCE 改字移出本 feat；SC-5 觀測點變少 | 待人審 |
| OC-3 | 本 PR／本 hop **不施工**（不改模板、守衛、範例碼）。使用者 brief 寫「Stage 2 only」；「Decision 只鎖方向」是收窄 | 本票是獨立 Implementer 的 Stage 2 產物，不是 Stage 6 | 本 hop 任務 Out of scope。收窄依據 = 書面 brief | Scope 加上本 PR 改 example／腳本；與「只交 2-decision」衝突 | 待人審 |
| OC-4 | feature branch **不改** `docs/dev/STATUS.md` 表列（含不把 Stage 推進到 2）。流程層。stage 列留給 `main` 上 `status-update.sh` | 母版 STATUS 禁 feature branch 寫入；腳本在非 main 會拒 | `_templates/STATUS.md` 頂註；`docs/dev/STATUS.md:10-16`；`scripts/status-update.sh` 正本限 `main` | 本 PR 含 STATUS 列；與寫入窗衝突，merger 還要再收一次 | 待人審 |

### 內部技術選擇(下層,告知即可)
- `1-discussion.md` 保留 draft／「本 hop 不送 G1」原文；本檔才改口成 Decision。
- 審頁只准 `scripts/build-stage2-html.py --action` 產 `2-decision.html`；不手包 html-shell、不走 mermaid、不用 ASCII `<pre>` 當圖。
- `scripts/fixtures/` 裡複製「2c gauntlet」的測試夾具：僅當某牙仍斷言舊編號時才改；不當採用者樣張。
- Stage 3 不預先跳過；觸發判定留給第 3 站（本檔無「跳過 Stage 3」流程層 OC）。
- 契約／plugin 版號本 hop 不動。

## ADR 晉升檢查
- 難逆轉:否（G3 前可改本檔 Decision／OC；真正改牙在 4→6）
- 反直覺:是（模板散文已對，仍要開 full lane 鎖教學面）
- 真 trade-off:是（重寫 vs 鎖牙 vs 只改文件；T-host 摩擦 vs 跳過 2c）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-12 | owner Stage 1 方向已核（chat「對」）：整合在 Fresh／雙軸／Verdict 之前；lane full；本 hop 只 Stage 2。本檔三決策點=剩餘工作形態／牙鎖面／範例編號何時改
- Stage 1 改口 | 2026-09-12 | 1-discussion 仍 draft、Q5 `[~]`／Q6–Q7 `[>]`；本檔把 Q5 收成 A、Q6 收成 T-core、Q7 收成 E-now。不回改正本討論
- G1 | 2026-09-12 | **未送審、未填 PASS**。`verdict:` 空；OC-1～OC-4 待人審。禁止 Agent 代填 Human verdict
