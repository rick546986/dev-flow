---
feature: five-station-f3
stage: 3-prototype
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 3. 原型 — cut 之後人還會走錯下一步嗎？（預設五站／空切訊號）

> Lane = **full**。G1 已核（`2-decision.md` `verdict: PASS`、OC-1…OC-12 ✅）。Writer C 獨立評九條；2-decision 內部技術選擇寫「不預先省略第 3 站」，本檔無「Stage 3」與「省略本站」同句的流程層 OC。
> 本 hop **只本檔 + 審頁 html**。不改 `_templates/`／`graph.yaml`／gate／`scripts/` 牙、不改 STATUS／HISTORY、**不改 `2-decision.md`**、不發明 Human ACCEPTED、不發明 G2。
> F3 = **cut／defaults**。1A+2A+3C+4A+5A+6A 已是核准 Pattern → **1 個可操作 Demo（D1）**，不湊假互動 Variant。
> Demo 形式 = **狀態流程模擬器**（人依 Demo Script 點／比對卡）。**PROTOTYPE — not production**。不寫 cut 碼、不 bump 2.1.0。
> Human verdict 由參與 Demo 的人類親填。Agent 禁代填 ACCEPTED／attestation。本檔 `status: draft` 直至人類親裁。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context：Actors／Journey／Workarounds／Exceptions -->
- [ ] 有新的前端流程（誠實：本題是方法論預設路線／契約／doctor CLI，**不是**產品前端。審頁何時出現已由「改變下一步」覆蓋）
- [x] 改變使用者下一步（cut 後、cut 當下無 1–7 `.md` 的新 slug：下一步是五站 hop，不再例行停 `N7-g1`／`N6-g2` 等人按提交；現況 Journey 步 4 仍等人）
- [x] 涉及角色交接（母版 owner 簽可見 cut 紀錄 → coordinator 讀端 → 新 slug 寫手 hop → 採用端 owner 拒遠端改線 → in-flight 執行者仍走舊 7 → Ship 審查者簽 `verdict: PASS`）
- [x] 涉及人工核准（cut SoT＝誰／何時／哪個條件的人類可見紀錄；Ship 仍唯人；本 slug 自己的 G2／G3 仍等人；Agent 禁寫 `ACCEPTED`／Ship `PASS`）
- [x] 涉及等待/退回/逾時（NEW5 不再例行等 G1／G2；OLD7 仍等；SLOT-REJECT／`allow_legacy()` 是退回；NEW5-WAIT-RED＝謂詞真卻仍留下「要不要繼續」）
- [x] 涉及權限差異（Agent／coordinator 禁把 silent `True` 當已切；未宣告 2.1.0 的採用端不得被遠端改線；本目錄禁當活五站；feature branch 禁碰 STATUS）
- [x] 涉及系統外動作（現行痛是 Cursor chat 當 hop 開關；採用端 `marketplace update`＋doctor CLI；指南讀者只看書）
- [ ] 涉及多種可行互動設計（1A–6A 已 lock；切換機制／attestation 檔名交 4-spec，不是「下一步點哪」的第二套互動）
- [ ] Stage 1 尚有操作流程不確定性（Journey 已鎖；Q15–Q27 已在 Decision 有去向；剩下 OPEN 是鍵名／檔名／入口腳本名，不是操作順序）

→ 命中 6 條:第 3 站條件式必要,本站執行。

## Question
引 2-decision **Risks**（silent True 冒充已切；2.1.0 當 cut；只 bump 正本不修 reader；只改用字；doctor 綠當 ticket；本 slug 當白老鼠）＋ **SC-NEW5-CUT-OK／SC-ATTEST-SILENT-RED／SC-PRE-210-NE-CUT／SC-DOCTOR-NE-TICKET／SC-GRAPH-WORD-NE／SC-SELF-OLD7**。

在**不改 graph、不 bump 契約、不重開 1A–6A**的前提下，一張狀態流程模擬器能不能讓人**不靠作者口頭**答完這四問？

1. **下一步變了沒**（SC-NEW5-CUT-OK／NEW5-WAIT-RED）：cut 後新 slug，中間 latch 未命中時，前進紀錄有沒有「請人審 G1／G2」？
2. **誰說已切**（SC-ATTEST-VISIBLE／ATTEST-SILENT-RED）：只把 `f3_cut_happened` 改 `return True`、tree 裡沒有誰／何時／哪個條件 → 算不算切完？
3. **假綠能不能當票**（SC-PRE-210-NE-CUT／SC-DOCTOR-NE-TICKET／SC-GRAPH-WORD-NE）：2.1.0、doctor `COMPATIBLE`、guide 寫「五站」——哪一張能讓新 slug 改下一步？
4. **本目錄會不會被折**（SC-SELF-OLD7）：對 `docs/dev/five-station-f3/` 求五站自動前進，下一步是 hop 還是拒？

答案長什麼樣才算回答了：
- 每張好卡／壞卡人能指出**現在下一步**、**等不等人**、**誰有權寫「已切」**、**空／錯／權限不足怎麼辦**。
- 壞卡（silent True、doctor 綠、只改用字、本 slug 當 NEW5）一眼是拒絕，不是「F3 完了」。
- 選定 Demo 只有 D1。本 hop **不**回寫 2-decision 正文、**不**代填 Human ACCEPTED。

## Method
- 實驗位置:本檔 Method 節的操作盤（**PROTOTYPE — not production**；純資料／紙上狀態機；不進 throwaway code、不改 `_templates/`／`scripts/`／`graph.yaml`）
- Demo 形式:**狀態流程模擬器**（人依 Demo Script 走好卡 vs 壞卡）
- 1A–6A 已 lock → **Demo D1 狀態流程模擬器（選定）**；不做假互動 Variant
- 驗法:用 Stage 1 AC-1／AC-2／AC-4／AC-6／AC-7／AC-8 + Decision 具名 CASE 對照各走一遍；壞卡當負向。現況證據取自本 tree `b772da2`（`origin/main` G1 PASS 後）
- 本 hop **不**回寫 2-decision（確認紀錄「prototype 回寫」不在本 hop）。

### Demo D1 — 狀態流程模擬器（選定）

| 項 | D1（選定；鎖定 Decision 的操作面） |
|---|---|
| 主要角色 | 母版 owner；coordinator；新 slug 寫手；採用端 owner；in-flight 執行者；doctor 操作者 |
| 真實目標 | 切新 slug 預設五站，但不把空切訊號當成「已切」、不折舊 slug |
| 入口 | cut 後才開、當下無 1–7 `.md` 的新 slug vs 本目錄（已有 md = 舊 7 freeze） |
| 關鍵操作 | 看三前置 ∧ 可見 cut 紀錄 → 真則 NEW5 hop／缺一則 `allow_legacy()` |
| 等待狀態 | NEW5 中間不等例行 G1／G2；本 slug 仍例行等；Ship 仍等人 |
| 空狀態 | 無可見 cut 紀錄 → 第三位元假 → 仍舊 7；九條全未勾才是 A5 n-a（本檔不是） |
| 錯誤狀態 | silent `True`、2.0.0+五站 hops、只改用字卻標完 → 該格紅 |
| 權限不足 | Agent 代寫「已切」＝未切；未宣告採用端不得被改線 |
| 資料過期 | Q15–Q19 已升格進 Decision；過期不得把假設當已核 |
| 中斷恢復 | 從該 slug 目錄 1–7 `.md` 接著走；本目錄有 md 就恢復舊 7 |
| 系統外下一步 | chat 不是 cut；`marketplace update` ≠ 已切；doctor 綠 ≠ 路條 |

#### 盤 1 — 下一步：現況仍等人 vs cut 後 NEW5（AC-1）

| 卡 | 事實（本 tree `b772da2`） | 人該看見的下一步 |
|---|---|---|
| 現況新 slug | `f3_cut_happened()=False`；`contract_version()=''`；空目錄拒因=`路線未宣告 仍舊 7` | **仍舊 7**；例行停 `N7-g1`／`N6-g2` |
| 好卡 NEW5 | 假設 cut 已有可見紀錄 ∧ 2.1.0 已宣告 ∧ 該 slug cut 當下無 1–7 `.md` | **預設五站 hop**；中間沒有「請人審 G1／G2」 |
| 壞卡 WAIT | 謂詞真、latch 假，卻彈「要不要繼續／請人審」 | **紅**（NEW5-WAIT-RED）。不是客氣 |

<details>
<summary>點我：現況實跑（2026-09-14；地板，≠ F3 完）</summary>

```
f3_cut_happened False
contract_version ''
has_old7 docs/dev/five-station-f3 True
refuse this-dir 路線未宣告 仍舊 7
refuse empty-slug 路線未宣告 仍舊 7
```

讀縫已核：正本鍵 `devflow_contract_version=2.0.0`，reader 讀 `version`／`contract_version` → 空字串。空目錄與本目錄拒因都先停在「未宣告」，還沒輪到「cut 未發生」。這就是 2A 要修的縫，不是 cut 已發生。
</details>

#### 盤 2 — 誰說已切：可見紀錄 vs silent True（AC-4）

| 卡 | 頂欄／訊號 | 人該判定 |
|---|---|---|
| 好卡 ATTEST | tree 裡指得到誰／何時／讀哪個條件；函式只讀該紀錄 | 第三位元真；**仍要**另外兩條前置 |
| 壞卡 SILENT | 只改 `return True`；無可見紀錄 | **未切**（ATTEST-SILENT-RED／HOLLOW-TRUE） |
| 壞卡 BLAME | 用 git blame 冒充 who／when | **未切**（Decision 約束 3） |
| 壞卡 BOARD | STATUS Active 已開／guide 改「五站」 | **未切**（用語 ≠ SoT） |

人該看見：函式是讀端。chat「可以切了」不是紀錄。

#### 盤 3 — 假綠不能當票（AC-6／AC-7）

| 卡 | 本 tree 觀測 | 人該判定 |
|---|---|---|
| 好卡 誠實綠 | `hooks/devflow-doctor.sh` → `COMPATIBLE`／exit 0；句=`2.0.0 ∈ supported ['2.0.0']` | 只證明握手。**下一步仍舊 7** |
| 壞卡 TICKET | 「doctor 已綠，所以可 hop 五站」 | **拒**；理由是路線，不含「doctor 已綠」（DOCTOR-NE-TICKET） |
| 壞卡 210 | 只 bump 正本鍵到 2.1.0、cut 位元仍假 | `allow_legacy()`；理由應含「F3 cut 未發生」（PRE-210-NE-CUT）。現況 reader 還回 `''`，連 declared 都假（READ-SEAM） |
| 壞卡 WORD | 只改 `guide-dev-flow.html` 七站單行、graph 仍進 `N7-g1` | **不得**標 F3 成功（GRAPH-WORD-NE） |
| 好卡 TOKEN | `scripts/check-gate-tokens.sh` exit 0 | token 仍在＝地板，不是完 |

<details>
<summary>點我：doctor／token 原始摘要 2026-09-14</summary>

```
✅ devflow doctor: COMPATIBLE
doctor_exit=0
# 握手句: 2.0.0 ∈ supported ['2.0.0']
# supported_contract_versions=['2.0.0']；runtime_version=3.24.0
✅ Gate Token 釘死守衛:全過
tokens_exit=0
```

`hooks/_doctor_impl.py` 握手不讀 `hops`／`graph.yaml`／`marketplace`／cut 紀錄。反事實：hops 換成五站預設、契約仍 2.0.0，doctor 仍可綠 → 那是 SLOT-REJECT，不是「已切」。
</details>

#### 盤 4 — 本目錄仍舊 7（AC-2／AC-8）

| 卡 | 事實 | 人該判定 |
|---|---|---|
| 好卡 freeze | 本目錄已有 `1-discussion.md`／`2-decision.md`（本 hop 再加 `3-prototype.md`） | **in-flight**。對本目錄求五站自動前進 → **跳不過**（SELF-OLD7） |
| 壞卡 白老鼠 | 「先拿 five-station-f3 試五站 hop」 | 已拒。污染觀測 |
| 好卡 同伴 | `five-station-f2`／`five-station-simplify` 已有 1–7 `.md` | 同樣 OLD7；不是 NEW5 試體 |

NEW5 試體只准合成 fixture，或 **cut 之後才開** 的 slug。本 hop 不發明名字。

## 結構圖
- Demo D1 狀態流程模擬器（選定）
- 現況：三前置缺 → 仍舊 7、等人
- 好卡 NEW5：可見紀錄 ∧ 2.1.0 ∧ 非 in-flight → hop
- 壞卡：silent True／doctor 綠／只用字 → 紅
- 本目錄：已有 md → OLD7 到 Ship

```
now:   cut=False reader="" doctor=COMPATIBLE
       new slug wait N7-g1
good:  visible-record + 2.1.0 + not-inflight -> NEW5 hop
bad:   silent True | doctor ticket | wording-only -> red
self:  this dir has md -> OLD7 (selected freeze)
D1 selected: cards above; 1A-6A not reopened
```

## Demo Script
帶使用者走 D1。不要問「喜不喜歡」。逐場確認:看到畫面後知道下一步嗎？系統是否暗示了不存在的權限？等待狀態是否清楚？系統外交接是否可追蹤？資訊不完整時是否知道怎麼辦？能否撤回、重試、改派或恢復？

### Scenario AC-1（cut 後新 slug 下一步）
- 使用者角色:新 slug 寫手／coordinator
- 真實目標:cut 後、當下無 1–7 `.md` 時，中間不等例行 G1／G2
- 起始狀態:盤 1 三張卡；現況實跑 `f3_cut_happened False`
- 操作步驟:先看現況卡「現在等誰？」；再看好卡 NEW5；最後看壞卡 WAIT 彈「要不要繼續」
- 系統回應:現況仍舊 7。好卡中間無「請人審」。WAIT → 紅
- 系統外下一步:不准改問 owner 來繞假謂詞
- 觀察問題:下一步是 hop 還是等人？有沒有暗示「G1 twin 產了 = 要按提交」？

### Scenario AC-4（silent True 不算切）
- 使用者角色:母版 owner
- 真實目標:無可見紀錄不得宣稱已切
- 起始狀態:盤 2 四張卡
- 操作步驟:遮住作者說明，只看「函式 True／無誰何時哪個條件」；再對照 blame／看板
- 系統回應:SILENT／BLAME／BOARD 皆未切。好卡才讓第三位元真，且仍要另外兩條
- 系統外下一步:人類寫可見紀錄；不要叫 Agent 把函式改 True
- 觀察問題:chat「可以切了」有沒有被當成 attestation？系統是否暗示 Agent 有權簽 cut？

### Scenario AC-6（doctor 綠 ≠ 路條）
- 使用者角色:採用專案 owner／doctor 操作者
- 真實目標:拒絕「COMPATIBLE + marketplace 已更新 = 已切五站」
- 起始狀態:盤 3 證據；契約 `2.0.0`；doctor exit 0
- 操作步驟:跑 `hooks/devflow-doctor.sh`；讀握手句；問「綠了能不能 hop 五站」
- 系統回應:今天綠。綠的原因是握手，**不是**已切。求五站 hop → 拒；理由是路線
- 系統外下一步:`marketplace update` 後仍核契約版本與 cut 紀錄
- 觀察問題:系統是否暗示握手綠=路線沒變或已經五站？

### Scenario AC-7（只用字 ≠ 成功）
- 使用者角色:指南讀者／Ship 審查者
- 真實目標:guide／STATUS 改「五站」但新 slug 仍停 `N7-g1` → 不得標完
- 起始狀態:盤 3 壞卡 WORD；現況 `guides/guide-dev-flow.html` 仍七站單行、`stage2/graph.yaml` 仍進 `N7-g1`
- 操作步驟:只改用字、不改 hop 預設；問「F3 完了嗎」
- 系統回應:GRAPH-WORD-NE 紅。用語是交付物，不是 SoT
- 系統外下一步:3C 要行為 + 宣告同時真；節點不刪
- 觀察問題:看到「五站」二字時，知道下一步仍可能等人嗎？

### Scenario AC-8（本目錄仍舊 7）
- 使用者角色:in-flight 執行者／coordinator
- 真實目標:對本目錄要求五站自動前進 → 跳不過
- 起始狀態:盤 4；本資料夾已有 1／2 站 md（本 hop 再加 3）
- 操作步驟:嘗試把本 slug 寫進五站狀態；對照「僅有 html、無 md」
- 系統回應:已有 1–7 任一 `.md` → 整段舊 7。裸 html 不凍。白老鼠已拒
- 系統外下一步:本 slug 自己的 G2／G3 仍走舊 7 等人
- 觀察問題:有沒有暗示「Decision 過了就可以改走五站」？中斷後能否從目錄裡的 md 恢復舊路？

## Result
Agent 依 D1 走完各場（**不是** Human Demo）。答案:鎖定 Decision **點得完**——人只靠卡面就能分開「下一步／誰准切／握手／freeze」。回寫 2-decision 的條目見 Verdict；**本 hop 不改 2-decision**、**不**代填 Human ACCEPTED。

| 問 | 模擬器證據 | 壞卡一眼拒絕 |
|---|---|---|
| 1 下一步 | 盤 1：現況 `cut=False`／reader=`''` → 仍舊 7；好卡 NEW5 中間無「請審」 | 謂詞真仍問「要不要繼續」 |
| 2 誰准切 | 盤 2：可見紀錄才是 SoT；函式只讀 | silent True／blame／看板當已切 |
| 3 假綠 | 盤 3：doctor **COMPATIBLE／exit 0** 只握手；token 綠是地板 | doctor 綠當票；2.1.0 當 cut；只用字當完 |
| 4 freeze | 盤 4：本目錄已有 md → OLD7 | 本 slug 當 NEW5 白老鼠 |

選定互動 = **D1**（無第二互動方案）。未改模板、未寫 cut 碼、未切預設路線。Human verdict = `NOT_REVIEWED`（待人類親 Demo）。STATUS 本 hop **不改**。

附記（不修牙）：2-decision 內部技術選擇有一句同時含「Stage 3」與「跳過」字樣（「不預先跳過…無跳過 Stage 3」）。`hooks/_stage3_impl.py` 會把否定句讀成 skip OC——與 five-station-simplify 同型。本 hop 不改該牙、不改 2-decision。人審本 Demo 時不要把機械誤 PASS 當成 Human ACCEPTED。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填；Agent 禁代填 ACCEPTED／attestation -->
- Demo date: 2026-09-14（agent 已走 D1 卡面；Human Demo 未做）
- Participants:
- Variant reviewed: D1 狀態流程模擬器（選定；無第二互動 Variant）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED

## Verdict
- **擬回寫 2-decision**（本 hop 仍不動該檔）:確認紀錄加一行「prototype 回寫 \| 2026-09-14 \| Stage3-C D1：六條命中；下一步／可見紀錄／假綠／本目錄 freeze 可走完；不重開 1A–6A」。Risks「silent True」「doctor 綠冒充已切」「只用字」「本 slug 試五站 hop」旁註「D1 已給人點的對照卡」。內部技術選擇維持「第 3 站要評九條、不預先省略」。
- Human 判定 **NOT_REVIEWED**。無 attestation。本檔 `status: draft`。**不發明 ACCEPTED、不送 G2、不開 4-spec**。
- 實驗產物:操作盤留在本檔 Method；doctor／reader／token 輸出摘要在盤 1／3；無 throwaway branch、無正式碼。審頁由 `scripts/build-stage3-html.py --action` 重生。第 3 站已行使，未省略。
- 本 PR 檔集只准 `3-prototype.md` + `3-prototype.html`。不改 STATUS。不發明 G2。
