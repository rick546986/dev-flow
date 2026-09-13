---
feature: five-station-simplify
stage: 3-prototype
status: draft
owner: rick
reviewers: []
updated: 2026-09-13
---

# 3. 原型 — 人走現檔能不能看出「能解析兩套 ≠ 已切五站」？

> Implementer B。G1 已核（`2-decision.md` `verdict: PASS`／`status: approved`，#303）。本 hop **只本檔 + 審頁 html**。不改 `_templates/`／`graph.yaml`／牙／STATUS／HISTORY、不回寫 2-decision 正文、不填 Human `ACCEPTED`、不合併。
> 主軸：**dual-read 誠實**、**marketplace × doctor 綠陷阱**、**本 slug = live freeze 樣本**。2A／3A／4A 方向已 lock；本站只答「人怎麼走、走到哪一步會誤判」。
> Demo 形式 = **狀態流程模擬器 + 可執行 CLI**（對本 tree 現檔實跑，不是只看靜態說明）。**PROTOTYPE — not production**。獨立於 A／C，未讀他線 Stage 3。
> Human verdict 由參與 Demo 的人類親填。Agent 禁代填 `ACCEPTED`／attestation。本檔維持 `draft`／`NOT_REVIEWED`。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context：Actors／Journey／採用 hop／in-flight／chat 蓋章 -->
- [ ] 有新的前端流程（本題是方法論路線身分與採用端握手，沒有新產品畫面）
- [x] 改變使用者下一步（摺停後中閘不再等人按提交；採用端 marketplace 後下一步不該自動跟 hops）
- [x] 涉及角色交接（採用 owner → 母版 owner 中繼；coordinator 與寫手；本 slug 執行者 vs 新 5 寫手）
- [x] 涉及人工核准（Ship 唯人；B1 attestation 仍人類親填；本站 Human verdict 不得 Agent 代寫）
- [x] 涉及等待/退回/逾時（HumanWait／Escalated；Q6 過期擋本 slug G2；in-flight 等到自己的 Ship）
- [x] 涉及權限差異（coordinator 禁寫判定；未 2.1.0 不得遠端改線；Agent 禁代填 ACCEPTED）
- [x] 涉及系統外動作（`marketplace update`、doctor 握手、GitHub、口頭回報）
- [x] 涉及多種可行互動設計（三訊號同走／先看 freeze／doctor 綠當路線；後者是陷阱）
- [x] Stage 1 尚有操作流程不確定性（人何時把 doctor 綠讀成「已切」；本 slug 會不會被拿去試五站 hop）

→ 命中 8 條:第 3 站條件式必要,本站執行。2-decision 無流程層 OC 把該站標成跳過。

## Question
2-decision Risk「採用端 marketplace update 後被遠端改線，doctor 仍綠」＋「有人把 2A 舊檔不紅讀成可以默默切五站」＋「本 slug 被拿去試五站自動前進」＋ OC-1／OC-2／OC-5 ＋ SC-8／SC-9／SC-10：

在**不改模板、不寫 F1 牙、不切 hops**的前提下，人走本 tree 現檔，能不能一次分清這三句？

1. **dual-read 誠實（2A／SC-9）**：2.1.0 能解析舊 7 與新 5 ≠ 採用端已切五站。舊 7 缺新 5 欄 = 合法缺省、不得一次變紅。
2. **marketplace × doctor 綠（3A／SC-10）**：`devflow_contract_version=2.0.0` + marketplace 已換 hops + doctor 對 2.0.0 握手綠 → **不得**解釋成「已切五站」。doctor 綠只證明握手。
3. **本 slug live freeze（4A／SC-8）**：`docs/dev/five-station-simplify/` 已有 1–7 任一 `.md` → 整段舊 7 到 Ship。對本目錄要求五站自動前進、跳過例行 G1／G2 → 必須跳不過。

答案長什麼樣才算回答了：
- 人走完 Demo Script 後，能指出現檔哪一格是契約版本、哪一格是 hops 身分、哪一格是 freeze md；三者不能互相冒充。
- 「doctor exit 0」單獨出現時，系統／文案不得暗示路線已切或路線沒變。
- 本目錄已有 `1-discussion.md`／`2-decision.md` 被標成 in-flight；裸 html 不算開工（OC-5）。
- 本 hop **不**改 2-decision 正文、**不**填 Human ACCEPTED。

## Method
- 實驗位置:本檔 Method／Result（**PROTOTYPE — not production**；純資料實驗，對本 tree 現檔實跑；不進 throwaway 產品碼、不改 `scripts/`／`_templates/`／`graph.yaml`）
- Demo 形式:**狀態流程模擬器 + 可執行 CLI**（人依 Demo Script 跑 `hooks/devflow-doctor.sh`、讀契約／marketplace／本 slug md 清單）
- 2A／3A／4A 已 lock → **3 個結構不同 Variant 只比操作序與決策點**（不是換色換字，不重開選定方案）
- 驗法:2026-09-13 對 `origin/main` tip `a01d929` 實跑；壞走法（只看 doctor 綠就跟 hops）當負向
- 本 hop 不回寫 2-decision 正文（使用者：只產 3-prototype.md + 審頁）；意圖回寫落 Verdict

### Variant 對照（必含項）

| 項 | Variant A 三訊號同走（選定） | Variant B 先看 freeze md | Variant C doctor 綠當路線（棄＝陷阱） |
|---|---|---|---|
| 主要角色 | 採用專案 owner／母版維護者 | 本 slug 執行者（in-flight） | 被 marketplace 更新的採用 owner |
| 真實目標 | 判定「現在走哪條路」而不被單一綠燈騙 | 手上 slug 不被中途改線 | 少停、跟著新 hops 走 |
| 入口 | 契約版本 ∧ hops 身分 ∧ 目錄 md | `docs/dev/<slug>/*.md` 是否已有 1–7 | `devflow-doctor.sh` exit code |
| 關鍵操作 | 三格都讀完才下結論；缺一格 = 未判定 | 有 md → 立刻舊 7，不再看 doctor／hops | doctor 綠 → 跟 pack hops |
| 等待狀態 | 未 upgrade 到 2.1.0 = 必須舊 7；等人寫 attestation 仍只在 B1／Ship | 等到自己的 Ship；中間例行 G1／G2 仍在 | 無等待面；綠了就 hop |
| 空狀態 | 三格有一格空 = 不得宣稱已切 | 無 md、只有 html = 尚未開工（不凍） | doctor 無輸出仍當綠 |
| 錯誤狀態 | 把「舊檔不紅」寫成「已切五站」 | 把本 slug 寫入五站狀態 | 2.0.0 + 五站 hops + doctor 綠 → 當已切 |
| 權限不足 | 未 2.1.0 不得遠端改線 | coordinator 不得把舊 7 折五站 | Agent／marketplace 可改 hops |
| 資料過期 | Q6 過期擋本 slug G2；契約仍 2.0.0 過期後仍是舊 7 | freeze 到該 slug Ship，不因 F3 過期解凍 | 握手綠被當成永遠有效的路線證明 |
| 中斷恢復 | 從三格卡恢復，不必重跑全樹 | 目錄還在，從已有 md 恢復 | 靠記憶「上次 doctor 綠」 |
| 系統外下一步 | marketplace update 後重走三格，不跟口頭「已經五站了」 | 口頭要求五站 hop → 拒，回舊 7 graph | 口頭「doctor 都綠了」當準許改線 |

### Variant A — 三訊號同走（選定）
操作序:先讀契約 `devflow_contract_version` → 再讀 hops 住哪（方法包 `skills/dev-flow/stage*/graph.yaml`，marketplace 單一 `./`）→ 再讀目標 slug 是否已有 1–7 `.md`。三格 AND 之後才准說「路線」。任何一格綠都不能代表另外兩格。

與 B／C 的結構差:決策點在「三格齊」；資訊階層是並列，不是單一綠燈。空狀態=缺格。錯誤=冒充。

### Variant B — 先看 freeze md
操作序:先 `ls docs/dev/<slug>/*.md`。命中 1–7 任一 md → 整段舊 7，doctor／hops 對**這個 slug** 失去改線權。沒有 md 才去看契約與 hops。

與 A 的結構差:決策點前移到目錄存在性；本 slug 執行者不需要先懂 dual-read 才能自保。劣:採用端「尚未開工的空目錄」若 hops 已被換，B 看不見陷阱（那格要靠 A／SC-10）。

### Variant C — doctor 綠當路線（棄）
操作序:`hooks/devflow-doctor.sh` → exit 0 → 跟方法包 hops。這是 2C／3C，也是今天就能走通的陷阱。本 Demo 用它當負向對照，不當選定。

## 結構圖
- Variant A 三訊號同走(選定)
- Variant B 先看 freeze md
- Variant C doctor 綠當路線(棄)
- AC-5 dual-read 舊檔不紅≠已切
- AC-8 本 slug 已有 md=舊7
- SC-10 2.0.0+五站 hops doctor 仍可綠

```
contract 2.0.0 ──┐
hops in pack  ──┼── AND → 路線判定
slug *.md     ──┘
        \
         doctor exit 0  ≠  已切五站
```

## Demo Script
帶使用者走模擬器:同一組現檔先走 A，再走 B，再走 C。不要問「喜不喜歡」。逐場確認:看到畫面後知道下一步嗎？系統是否暗示了不存在的權限（例如 doctor 綠 = 可以跟 hops）？等待是否清楚？系統外交接（marketplace）能否追蹤？資訊不完整時知不知道怎麼辦？能否撤回、重試、改派或恢復？

### Scenario AC-5
- 使用者角色:採用專案 owner／母版維護者
- 真實目標:看出「能解析兩套 ≠ 已切五站」；舊 7 缺新欄不紅
- 起始狀態:契約 `2.0.0`；runtime `supported_contract_versions=['2.0.0']`；尚無 2.1.0 annex
- 操作步驟:讀 `devflow-contract.json` 的 `devflow_contract_version`；讀 `hooks/runtime-capabilities.json` 的 supported；問「現在能同時讀舊 7 與新 5 嗎？」；再問「舊 slug 缺新 5 欄該不該紅？」
- 系統回應:今天只能讀舊 7（契約未 bump）。缺新欄不該紅（2A）。能解析兩套是未來 2.1.0 的能力，不是「已經切了」的證據
- 系統外下一步:不要把「舊檔不紅」寫進採用說明當「可以默默切五站」
- 觀察問題:看到「不紅」時，知道那是合法缺省、不是已切嗎？系統有沒有暗示你已經在五站上？

### Scenario AC-8
- 使用者角色:in-flight slug 執行者（本目錄）
- 真實目標:本 slug 不被五站自動前進跳過例行 G1／G2
- 起始狀態:`docs/dev/five-station-simplify/` 已有 `1-discussion.md` 與 `2-decision.md`（G1 PASS）；尚無 4-spec
- 操作步驟:`ls docs/dev/five-station-simplify/*.md`；套 OC-5（只認 md）；對本目錄要求「五站 hop、跳過 G1／G2」
- 系統回應:任一 1–7 md 已在 → 整段舊 7 到 Ship。G1 已過仍要走條件 S3／G2／G3。五站狀態寫入必須被拒（RP-15／SC-8）
- 系統外下一步:口頭「吃自己的藥」不得改本目錄路線
- 觀察問題:看到本目錄已有 md，知道自己是 freeze 樣本嗎？裸 html 會不會被誤凍？有沒有人暗示可以跳過本 slug 的 G2？

### Scenario 採用 hop 身分
- 使用者角色:採用專案 owner（marketplace 剛更新）
- 真實目標:marketplace update 之後，不要把 doctor 綠當成「可以跟 hops 走」
- 起始狀態:本 tree 實測 doctor **COMPATIBLE／exit 0**；契約仍 `2.0.0`；marketplace 單一 `source: ./`；doctor 源碼**不讀** hops／`graph.yaml`／marketplace
- 操作步驟:跑 `hooks/devflow-doctor.sh`；讀握手段（`_doctor_impl.py` L193–L202）；讀 `.claude-plugin/marketplace.json` 的 `source`；讀 `skills/dev-flow/stage2/graph.yaml` 的 `N7-g1`（現行 hops 仍是舊 7 例行停）；做反事實：若 marketplace 把 hops 換成五站預設、契約仍 2.0.0，doctor 會不會仍綠？
- 系統回應:今天 doctor 綠。綠的原因是 `2.0.0 ∈ ['2.0.0']`，**不是**路線沒變。hops 住方法包，`marketplace update` 換整包。反事實成立：hops 變了，握手仍可綠。這就是陷阱（3A／SC-10）
- 系統外下一步:未 upgrade 到 2.1.0 → 必須仍走舊 7，不得遠端改線。F1 牙要紅「2.0.0 + 五站 hops」（本 hop 不寫牙）
- 觀察問題:doctor 印 `COMPATIBLE` 時，你會不會以為路線沒變、或已經五站了？等待／權限是否清楚（未 upgrade 不准跟新 hops）？

## Result
2026-09-13 對 tip `a01d929` 實跑（session scratchpad，非正式產品碼）：

| 訊號 | 現檔 | 觀測 |
|---|---|---|
| 契約 | `devflow-contract.json` | `devflow_contract_version=2.0.0` |
| runtime | `hooks/runtime-capabilities.json` | `supported_contract_versions=['2.0.0']`；`runtime_version=3.24.0` |
| doctor | `hooks/devflow-doctor.sh` | `✅ COMPATIBLE`；**exit 0**。握手句:`2.0.0 ∈ supported ['2.0.0']` |
| doctor 讀什麼 | `hooks/_doctor_impl.py:L193-L202` | 只比對契約版本 ∈ supported。源碼**不含** `hops`／`graph.yaml`／`marketplace`／`Intake` |
| marketplace | `.claude-plugin/marketplace.json` | 單一 plugin、`source: ./`。更新 = 換整包 hops |
| 現行 hops | `skills/dev-flow/stage2/graph.yaml` `N7-g1`；`stage4/graph.yaml` `N6-g2` | 仍是舊 7 例行停節點。F0 禁改。反事實:若這兩點被換成五站預設，doctor 仍可綠 |
| freeze | `docs/dev/five-station-simplify/` | `1-discussion.md` EXISTS；`2-decision.md` EXISTS；`3-prototype.md` 本 hop 才寫；`4-spec`…`7-review` absent。**in_flight=True**（任一 1–7 md） |
| 裸 html | 同目錄 `1-discussion.html`／`2-decision.html` | OC-5:只認 md。html 在不算開工；本目錄因 md 已凍，不是因 html |
| `_stage3_impl.py` 誤讀 | 本 hop 實跑 | 命中 8、`NOT_REVIEWED`、無 attestation。腳本卻因 2-decision 內部技術選擇句「不預先跳過 Stage 3」同時含「Stage 3」+「跳過」而標 `g2_demo=PASS`／`SKIPPED_OWNER_CALL`。該句是否定跳過，不是跳過。**本 hop 不把這次機械綠當成 Demo 已過。** Human verdict 仍是 `NOT_REVIEWED`。牙形交 F1，本 hop 不改 `_stage3_impl.py` |

答案（回寫 2-decision 2A／3A／4A 的意圖，本 hop 不改正文）:
1. **dual-read 誠實可走通**:人用現檔能分開「握手綠／舊檔不紅」與「已切五站」。今天甚至還不能 dual-read（契約仍 2.0.0）。不紅 ≠ 已切。
2. **marketplace × doctor 陷阱可復現**:doctor 綠 + marketplace 可換 hops，兩件事今天同時成立。C 走法（綠 → 跟 hops）必須當錯。F1 最少牙 = `2.0.0 ∧ 五站 hops → 紅`（OC-2；本 hop 不寫）。
3. **本 slug 已是 live freeze 樣本**:已有 1／2 的 md。對本目錄五站自動前進必須跳不過。本站自己出貨仍走舊 7（條件 S3 → G2 → G3）。

選定 **Variant A**（三訊號同走）。B 留給「只問這個 slug 凍了沒」。C 棄。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親自給。Agent 已代跑 CLI／讀檔；未 Demo ≠ ACCEPTED。Agent 禁寫 attestation。 -->
- Demo date: 2026-09-13（agent 代跑 CLI／讀檔；人類尚未走完 Demo Script）
- Participants:
- Variant reviewed: A／B／C（agent 代跑模擬器；人類尚未選）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED | role=採用專案 owner | scenario=AC-5
- Verdict attestation:

## Verdict
- **意圖回寫 2-decision**（本 hop **未**改正文，使用者禁令:只產 3-prototype.md + 審頁）:
  - 2A／SC-9:現檔證明「doctor 綠／舊檔不紅」不能冒充已切；2.1.0 才能 dual-read。
  - 3A／SC-10:現檔證明握手不讀 hops；marketplace `./` 可換 hops 而 doctor 仍可綠。
  - 4A／SC-8:本目錄已有 1–7 md = live freeze；五站 hop 必須拒。
  - 確認紀錄應留一行:`prototype 回寫 | 2026-09-13 | B 線 Stage 3：三訊號同走；Human verdict 仍 NOT_REVIEWED`。
- 互動未 ACCEPTED → 不得在 Stage 4 把互動定案；本檔 `status: draft`。
- throwaway 處置:指令與輸出摘要留在本檔 Result；無 scratchpad 碼進 Git；不改母版。
- 審頁:`scripts/build-stage3-html.py --action`（不手包 html-shell）。
