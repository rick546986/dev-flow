---
feature: requirement-discovery-gaps
stage: 3-prototype
status: draft
owner: rick
updated: 2026-09-13
---

# 3. 原型 — 九缺口欄位／分診／ledger 長什麼樣？

> Stage 3 依 2-decision「不預先跳過」**執行、不跳過**。1A–8A 已是落地策略；本站只答
> 2-decision 留給第 3／4 站的**形狀**（欄名、表頭、六問、ledger、manifest、verdict 一行）。
> 輕量方法論原型：column mocks／triage checklist／ledger shape。**不**改 `_templates/`、
> `skills/`、守衛、範例、STATUS、HISTORY。**不**當 Stage 6 施工。**不**發明 G2／G3、
> **不**代填 Human ACCEPTED。
> Demo 形式 = 狀態流程模擬器（填好的欄位卡 vs 故意壞卡，人實際走 Demo Script）。
> 互動形尚未 lock → 3 個結構不同 Variant。Human verdict 留 NOT_REVIEWED。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context：Actors／Journey／核准／期限／圍欄／Fast -->
- [ ] 有新的前端流程（本題是方法論文檔欄位與清單，沒有新產品畫面）
- [x] 改變使用者下一步（Fast 寫 4-spec 前必須先收六問；討論者未獲 owner 核准不得讀事實路徑）
- [x] 涉及角色交接（訪談對象 → 討論 agent → 收斂者 → owner → Fast 實作者 → G2 reviewer）
- [x] 涉及人工核准（evidence manifest 要 owner 核；Fast 命中要 owner 裁 full／mini／OC；過期假設擋 G2）
- [x] 涉及等待/退回/逾時（等 owner 核准才讀；Assumption 期限；lookback 到期；G2 退回）
- [x] 涉及權限差異（討論者禁讀 2–7；owner 才能放行路徑；G2 才能擋過期假設）
- [x] 涉及系統外動作（訪談、GitHub、審核筆記、日曆回看）
- [x] 涉及多種可行互動設計（欄位就地填／先過核准卡再開寫／審查時才重建，操作序不同）
- [x] Stage 1 尚有操作流程不確定性（2-decision 內部技術選擇：欄位名／檔名／抽樣規則尚未釘）

→ 命中 8 條:Stage 3 條件式必要,執行(不跳過)。2-decision 無「跳過 Stage 3」流程層 OC。

## Question
2-decision Risk「B-1 manifest 形狀未釘」＋內部技術選擇「4-spec 再釘」＋ SC-3～SC-9：
在**不改模板正本**的前提下，三張結構不同的欄位卡能否鎖住這六個形狀？

1. **高影響主張欄（2A／SC-3）**：狀態枚舉 ∈ {Observed, Reported, Inferred, Assumption, Conflict}；來源類型、as-of、角色或範圍、支持哪一段、限制。來源 XOR Assumption+期限。點頭不得當唯一來源。
2. **Assumption 四欄（3A／SC-4）**：若為假影響什麼／影響級／怎麼驗／何時由誰驗。過期 + 未 resolved + 無 OC 接受 → 進不了 G2。
3. **disposition 表頭（4A／SC-6）**：引用 Stage 1 原文片段 + 去向 ∈ {本方案處理, 刻意維持, Non-Goal, 另開 slug, 仍待驗} + 一句理由。不另發 RW-id。
4. **lookback 四欄字面（5A／SC-7）**：回看日期／回看 owner／資料來源／低於何值重開。結果走 HISTORY，不另造永久檔。
5. **evidence manifest（6A／SC-8）**：想找哪類／為什麼／擬路徑／owner 核准／已讀。未核准不得當已授權。仍禁 2–7。
6. **Fast 六問 + A-5 一行（7A／8A／SC-5／SC-9）**：下一步／權限／等待語意／交接／系統外／中斷恢復，每問是／否＋一句。命中必須有 full／mini／OC。Human verdict 一行內有角色與場景。

答案長什麼樣才算回答了：
- 每張卡能用本 slug 自己的 Journey／Exception 列填滿，壞卡（只寫「使用者反映」、空白六問、無去向）一眼看出缺哪欄。
- 「只改狀態字、把等待顯示成完成」在六問卡上必須命中等待語意。
- 選定 Variant 的操作序與決策點寫得清：誰填、等誰、空／錯／過期／權限不足怎麼辦。
- 本 hop **不**改 2-decision 正文、**不**改模板；形狀只落在本檔，供後續回寫。

## Method
- 實驗位置:本檔 Method 節的欄位卡（**PROTOTYPE — not production**；純資料實驗，不進 throwaway code、不改 `scripts/`／`_templates/`）
- Demo 形式:**狀態流程模擬器**（人依 Demo Script 把同一列放進三張卡，比較能否重建來源／去向／下一步）
- 互動形未定 → **3 個結構不同 Variant**（不同操作序／資訊階層／決策點；不是換色換字）
- 驗法:用本 feature 已核列（Journey「發現被錨定」「痛點消失」「互動風險晚露」；Exception Q6；AC-9 等待誤標對照）各走一遍；壞卡當負向
- 本站**不**改 2-decision、不寫 STATUS、不落地牙

### Variant 對照（必含項）

| 項 | Variant A 同檔就地欄 | Variant B 先過核准卡再開寫 | Variant C 審查時才重建 |
|---|---|---|---|
| 主要角色 | 討論 agent 寫列時順便填 | owner 先核卡，討論者才能讀 | G1／G2 reviewer 事後補表 |
| 真實目標 | 欄在主張旁邊，後讀者當下能走回來源 | 未核准前零事實讀取 | 送審前看起來像有 Evidence |
| 入口 | 1-discussion／2-decision／Fast 4-spec 本文 | 另開 manifest／triage 卡，過了才開寫 | 4-spec／G2 checklist |
| 關鍵操作 | 高影響列就地選枚舉、貼來源或期限 | 先填「想找哪類」→ 等核准 → 再讀 | 自由散文，審查人重建 |
| 等待狀態 | 期限列在該列；owner 核准格在同節 | 顯性「等 owner」；未核不得往下 | 無等待面，期限可拖到 G2 |
| 空狀態 | 欄空 = 形狀紅；六問空白 ≠ 已分診 | 卡不存在 = 還不能開工 | 空表仍能靠「有 Evidence 字」綠 |
| 錯誤狀態 | 點頭當唯一來源；枚舉亂填（牙只驗 ∈ 集合） | 未核路徑已讀 = 越權 | 痛點列無去向仍可過 |
| 權限不足 | 討論者看不到 2–7；未核路徑不當來源 | 同左，且卡上核准格空白 = 禁讀 | 圍欄在，事實也進不來 |
| 資料過期 | Assumption 四欄 + 過期擋 G2 | 同左，另多一張過期卡 | 過期假設仍合法走到 G2 |
| 中斷恢復 | 列還在原文位置，接著填 | 卡在，從核准格恢復 | 靠記憶找哪條痛點消失 |
| 系統外下一步 | 訪談／日曆回看寫在 lookback 四欄 | 先送核准卡給 owner | reviewer 口頭問 |

### Variant A — 同檔就地欄（推薦）
操作序:寫主張 → 立刻填枚舉與來源欄 → Stage 2 引用原文做 disposition → Fast 在進 4 前填六問（可附在 4-spec 頂，但必須先於 R/S）→ Exit 四欄。不另造檔種類。

**高影響主張欄（2A）** — 只要求高影響列（OC-5），不要求每句 Context 都貼。

| 主張（原文片段） | 狀態 | 來源類型 | as-of | 角色或範圍 | 支持哪一段 | 限制 |
|---|---|---|---|---|---|---|
| Journey「發現被錨定」 | Observed | 本 tree skill | 2026-09-13 | 討論 agent／訪談對象 | 1-discussion Context N3 | 無採用現場逐字稿 |
| Q6 採用者把解法寫進 Goal | Assumption | — | 期限=Stage 2；OC-3 收窄 | 採用現場 | Exceptions／Q6 | 無 log；不捏造訪談 |
| （壞卡）「使用者反映希望 dashboard」 | — | — | — | — | — | 無枚舉、無來源、點頭當事實 → 形狀失敗 |

**Assumption 四欄（3A）**

| 假設 | 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|---|
| Q6 採用現場仍把解法寫進 Goal | 改範例優先級下降；不改「Goals 鎖解法」模板病 | 高 | 對帳本 repo 範例教師 | Stage 2／owner；OC-3 已收窄 |

過期 + 未 resolved + 無 OC → `check-spec-gate.sh` exit 1（牙未落地；本站只鎖「人看得見的拒絕」落在 G2 送審）。

**disposition ledger（4A）** — 表頭三欄，引用原文，不發 RW-id。

| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| Journey「發現被錨定」 | 本方案處理 | 1A 改 N3：發現題禁推薦 |
| Journey「痛點消失」 | 本方案處理 | 4A：本表即去向帳 |
| Journey「互動風險晚露」 | 本方案處理 | 7A：六問在進 4 前 |
| Exception「A-5 只 LIGHT」 | 刻意維持 | Owner Call；不做全表 |
| Exception／Q6「採用現場仍把解法寫進 Goal」 | 仍待驗 | OC-3；不捏造現場 |
| （壞卡）Journey「痛點消失」 | （空白） | — → SC-6 失敗 |

**lookback（5A）** — Exit 四欄字面；結果另用 `history-append.sh`。

```
- 回看日期:
- 回看 owner:
- 資料來源:
- 低於何值重開:
```

本包自測填法（非正式約定，等 Stage 7）:日期=shipped+一個觀測窗；owner=rick；來源=採用專案 Stage 1 Goals 是否仍把通道寫進目標；門檻=抽樣仍見「Goal = dashboard」→ 重開。

**evidence manifest（6A）** — 一節、同檔；guard 讀「已核准路徑」。檔名建議:`1-discussion.md` 的 `## Evidence manifest`（不另造永久檔種類）。

| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| 本 tree 模板／skill／範例 | 核「Goal 鎖通道」教師 | `_templates/1-discussion.md` 等已指名 | 是（本 slug 原料） | 是 |
| 採用現場逐字稿 | 收 Q6 | （無） | 未核 | 否 — 不得當已授權 |
| 2-decision／4-spec | — | `docs/dev/*/2-decision.md` | 禁 | 禁（方案檔） |

**Fast 六問（7A）** — 進 Stage 4 **之前**；空白 ≠ 已分診。全否且已有 approved spec 且不改語意（OC-6）→ 維持 Fast。

| # | 問 | 答（是／否＋一句） | 命中 |
|---|---|---|---|
| 1 | 改變下一步？ | | |
| 2 | 改權限／核准語意？ | | |
| 3 | 改等待／完成語意？ | | |
| 4 | 改角色交接？ | | |
| 5 | 改系統外動作？ | | |
| 6 | 改中斷恢復？ | | |
| 去向 | 全否 → Fast；命中 → owner 裁升 full／fast+mini／OC 接受風險 | | |

對照案（必須命中 #3）:

| # | 問 | 答 | 命中 |
|---|---|---|---|
| 1 | 改變下一步？ | 否。只改狀態字顯示 | 否 |
| 2 | 改權限／核准語意？ | 否 | 否 |
| 3 | 改等待／完成語意？ | 是。等待被顯示成完成 | **是** |
| 4–6 | … | 否 | 否 |
| 去向 | 命中等待語意 → 不可空白開寫；owner 裁 full／mini／OC | | 待裁 |

**Human verdict 一行（8A LIGHT）**

```
- Human verdict: <ENUM> | role=<Actors 表角色> | scenario=<AC-id>
- Participants: 對應 Actor: <角色>（實際操作 Demo 的人）
```

只寫 `ACCEPTED` + 姓名日期 = 不完整（SC-5）。本 hop 不填 ACCEPTED。

### Variant B — 先過核准卡再開寫
操作序:另開 `docs/dev/<slug>/evidence-manifest.md` 與 Fast `triage` 卡 → owner 核准 → 才准讀事實／才准開 4-spec。disposition 改成 append-only 日誌（日期｜片段｜去向｜落點）。

與 A 的結構差:決策點前移、資訊不在主張旁邊、多一個「卡不存在就不能開工」的空狀態。2-decision 已拒 lookback 永久檔；B 把同一成本加到 manifest／triage。欄位集合與 A 相同，只是分檔＋閘門。

等候面:討論者停在「擬路徑已列、核准格空白」。權限不足:核准空白仍去讀 = 越權。中斷:從核准格恢復，不必重寫主張。

### Variant C — 審查時才重建（對照現況，棄）
操作序:作者自由散文 → G1／G2 才補枚舉與去向。Fast 六問寫在 4-spec Verification Profile（lane 已選完）。

與 A／B 的結構差:決策點在審查、不在書寫。空狀態可被「有 Evidence 字」蓋過。Journey「痛點消失」與等待誤標可以無聲進規格。這是本包要修的病，不當選定。

## 結構圖
- Variant A 同檔就地欄（選定）
- Variant B 先過核准卡再開寫
- Variant C 審查時才重建（棄）
- Fast 六問未收束不得進 4
- disposition 引用原文去向
- Exit 回看四欄

## Demo Script
帶使用者走模擬器:同一列先放 A，再放 B，再放 C。不要問「喜不喜歡」。逐場確認:看到欄位後知道下一步嗎？系統是否暗示了不存在的權限？等待是否清楚？系統外交接能否追蹤？欄空時知不知道怎麼辦？能否撤回、重試、改派或恢復？

### Scenario AC-3
- 使用者角色:G2 reviewer
- 真實目標:沿高影響主張走回來源，或看到 Assumption+期限；點頭不當來源
- 起始狀態:Method 的 2A 好卡（「發現被錨定」= Observed）與壞卡（「使用者反映希望 dashboard」）
- 操作步驟:先讀好卡六欄；再讀壞卡；問能否重開來源、枚舉是否 ∈ 集合
- 系統回應:好卡能回到本 tree skill；壞卡無枚舉、無來源 → 形狀失敗。Variant C 把兩張壓成同一句「事實」
- 系統外下一步:退回 Stage 1 補來源或期限；不要用點頭紀錄補欄
- 觀察問題:看到壞卡是否知道缺的是枚舉還是來源？系統有沒有暗示「寫了 Evidence 就算數」？

### Scenario AC-4
- 使用者角色:G2 reviewer
- 真實目標:過期高影響假設進不了 G2
- 起始狀態:3A 四欄已填、期限=Stage 2、OC-3 已收窄；對照一張過期且無 OC 的假卡
- 操作步驟:核四欄是否都在；對照卡是否仍能宣稱送 G2
- 系統回應:有 OC-3 的列可走；過期+未驗+無 OC 必須是人看得見的拒絕（落點=`check-spec-gate.sh`，本站不寫腳本）
- 系統外下一步:驗轉 Observed／Reported，或 owner 明示接受風險
- 觀察問題:拒絕是否發生在送審那一關，還是只在模板有欄就綠？等待期限清不清楚？

### Scenario AC-5
- 使用者角色:後讀 3-prototype 的人
- 真實目標:一行內答出「驗了誰、驗了哪場」
- 起始狀態:完整行 `Human verdict: NOT_REVIEWED | role=Fast 實作者 | scenario=AC-9` vs 只寫 `ACCEPTED` + 姓名日期
- 操作步驟:遮住前後文，只看該行
- 系統回應:完整行能答角色與場景；殘行不能。本 hop 不把殘行或完整行標 ACCEPTED
- 系統外下一步:人類 Demo 後親填 ENUM + attestation；Agent 禁代填
- 觀察問題:有沒有暗示「有人按過 = 代表性角色驗過」？

### Scenario AC-6
- 使用者角色:收斂者
- 真實目標:Stage 1「痛點消失」到 Stage 4 仍有去向
- 起始狀態:4A 表已有「痛點消失 → 本方案處理」；壞卡去向空白
- 操作步驟:用原文片段（不是 RW-id）對一次；再看 Variant C 散文「痛點有處理」
- 系統回應:A／B 能指出該列去向；C 與壞卡無法證明列還在
- 系統外下一步:標「本方案處理」者 Stage 4 至少一條 R/S；其餘落到 Out of Scope／Known limit／後續 slug
- 觀察問題:中斷後能否從片段恢復，還是要靠記憶？

### Scenario AC-7
- 使用者角色:owner
- 真實目標:出貨時留下回看四欄，到期能重開，不另造 lookback 檔
- 起始狀態:5A 四個欄位名；結果入口 = `history-append.sh`
- 操作步驟:嘗試只填「之後再看」或只寫 HISTORY、Exit 無約定
- 系統回應:缺任一欄 = 形狀失敗（SC-7）。5B／5C 已在 2-decision Rejected
- 系統外下一步:shipped 當時填四欄；到期用 HISTORY 追加結果
- 觀察問題:填了任意數字會不會被當成問題已改善？

### Scenario AC-8
- 使用者角色:討論 agent
- 真實目標:owner 核准後讀得到事件／行為／結果；打不開 2-decision／4-spec
- 起始狀態:6A 表：本 tree 路徑已核；採用現場逐字稿未核；2-decision 列為禁
- 操作步驟:A = 同節核准格；B = 另檔卡空白就不能讀；嘗試把 ticket 解法當事實
- 系統回應:未核路徑不得引用。方案檔仍禁。ticket 解法建議不當事實。B 多一次「等 owner」空狀態
- 系統外下一步:列「想找哪類＋原因」送 owner；核准後才讀
- 觀察問題:系統是否暗示未指名資料夾可以先列目錄？權限不足時下一步清不清楚？

### Scenario AC-9
- 使用者角色:Fast 實作者
- 真實目標:寫 4-spec 前收完六問；「等待顯示成完成」必須命中
- 起始狀態:7A 空白表 vs 對照案（#3 = 是）
- 操作步驟:把對照案填進 A；再想像 C（lane 已選 Fast，六問寫在 Verification Profile）
- 系統回應:A／B 在進 4 前就標命中，去向必須是 full／mini／OC。C 會等規格寫完才看到風險。空白表 ≠ 已分診
- 系統外下一步:owner 裁去向；純視覺不改語意（OC-6）才可維持 Fast
- 觀察問題:全打「否」有沒有被當成儀式？中斷後能否從六問表恢復？

## Result
回寫 2-decision 內部技術選擇「4-spec 再釘」與 Risk「B-1 manifest 形狀未釘」：本站用紙上模擬器走完 AC-3～AC-9，**推薦 Variant A**（同檔就地欄）。B 把核准決策點前移但另造檔種類，與 5A「不另造永久檔」同型成本；C 重演痛點消失與 Fast 晚露。欄位字面見 Method；本 hop 不改 2-decision 正文。

| 形狀 | 選定字面（A） | 負向 |
|---|---|---|
| 2A 主張欄 | 狀態／來源類型／as-of／角色或範圍／支持哪一段／限制 | 只有「使用者反映」 |
| 3A 假設 | 若為假影響什麼／影響級／怎麼驗／何時由誰驗 | 過期仍送 G2 |
| 4A ledger | 引用（原文片段）／去向／理由 | 去向空白或 RW-id |
| 5A lookback | 回看日期／回看 owner／資料來源／低於何值重開 | 另造 lookback.md |
| 6A manifest | 想找哪類／為什麼／擬路徑／owner 核准／已讀；節名 `## Evidence manifest` | 未核當已授權；讀 2–7 |
| 7A 六問 | 上表六問＋去向；進 4 前 | 空白當已分診；等待誤標未命中 |
| 8A verdict | `ENUM \| role=… \| scenario=…` | 只寫 ACCEPTED + 姓名日期 |

證據:用本 slug 已核列填滿 A 的好卡；壞卡與 C 無法指出「痛點消失」去向，也無法在進 4 前攔住等待誤標。正式模板／牙未改。
`hooks/_stage3_impl.py` 對本檔會印 `g2_demo=PASS`，那是誤咬 2-decision「不預先跳過／無跳過 Stage 3」含「Stage 3」+「跳過」字樣，**不是**本 hop 的 G2、也不是 ACCEPTED。本檔 verdict 仍是 NOT_REVIEWED。

## User Demo Feedback
<!-- Agent 禁代填 ACCEPTED／attestation。未 Demo = NOT_REVIEWED。本 hop 不送 G2。 -->
- Demo date:
- Participants:
- Variant reviewed: A / B / C（紙上模擬器；人類尚未走）
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
- 回寫 2-decision（**本 hop 不改該檔**，只鎖定回寫對象）:內部技術選擇「4-spec 再釘」改為 Stage 3 推薦 Variant A 字面（上表）；Risk「B-1 manifest 形狀未釘」改為同檔 `## Evidence manifest` 五欄 + 核准後才讀。B／C 不選。確認紀錄擬留「prototype 回寫 \| 2026-09-13」，等人類 Demo 後由後續 hop 寫入。
- Human verdict = NOT_REVIEWED（無人親走 Demo；Agent 不代填 ACCEPTED、不寫 attestation）。frontmatter 留 **draft**。不送 G2、不開 4-spec、不改 STATUS。
- 實驗產物:欄位卡留在本檔 Method；無 throwaway branch、無正式碼。第 3 站已行使，未省略。
