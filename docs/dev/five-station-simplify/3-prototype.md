---
feature: five-station-simplify
stage: 3-prototype
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 3. 原型 — 鎖定 Decision 人點得完嗎？（五站 vs 舊 7、A/B、假完成）

> Lane = **full**。G1 已核（`2-decision.md` `verdict: PASS`、OC-1…OC-11 ✅）。本 hop **只本檔 + 審頁 html**；不改 `_templates/`／`graph.yaml`／gate／`scripts/` 牙、不改 STATUS／HISTORY、不改 `2-decision.md`、不發明 Human `ACCEPTED`、不合併。獨立於 B／C Stage 3。
> 2-decision 無「Stage 3」+「跳過」流程層 OC → **不跳過**。1A–7A 已是核准 Pattern → **1 個可操作 Demo**，不湊假 Variant。
> Demo 形式 = **狀態流程模擬器**（人依 Demo Script 點／比對卡，不是只看散文）。**PROTOTYPE — not production**。F1 牙／coordinator 不在本站落地。
> Human verdict 由參與 Demo 的人類親填。Agent 禁代填 `ACCEPTED` 與 attestation。本檔 `status: draft` 直至人類 ACCEPTED + attestation。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context：Actors／Journey／Workarounds／Exceptions -->
- [x] 有新的前端流程（owner／coordinator 看到的站序與審頁 latch 面從「七站三次等人」改成 Intake→Decide→Spec→Build→Ship；A1–A10／B1 何時出現會變）
- [x] 改變使用者下一步（Decide／Spec／Build 完成且 latch 未命中 → 下一步是 hop，不是「請按提交判定」；人預設下一動改到 Ship）
- [x] 涉及角色交接（討論 agent → 收斂者 → coordinator → Build 實作者 → 獨立 T reviewer → Ship 審查者 → 採用端 owner）
- [x] 涉及人工核准（Ship `verdict: PASS` 唯人；B1 命中時 `ACCEPTED`+attestation 仍人類親填；Quiz 僅不可逆）
- [x] 涉及等待/退回/逾時（`HumanWait`／`REVISE`／`HOLD`／rewrite cap 用盡 `Escalated`；舊 7 本 slug 仍例行等 G1／G2）
- [x] 涉及權限差異（Agent／coordinator 禁寫 `ACCEPTED`／Ship `PASS`；reviewer ≠ implementer；未 upgrade 採用端不得被遠端改線）
- [x] 涉及系統外動作（現行痛是 Cursor chat 蓋章；採用回報靠口頭／去識別化；`marketplace update` 換 hops）
- [ ] 涉及多種可行互動設計（1A–7A 已 lock；本站只把鎖定面做成可走完的模擬器，不重開 1B／5B／6B）
- [ ] Stage 1 尚有操作流程不確定性（五站怎麼等人已鎖；Q8／Q10／A1–A2 是 annex 鍵名，不是「下一步點哪」）

→ 命中 7 條:第 3 站條件式必要,本站執行。2-decision 內部技術選擇已寫「不預先跳過 Stage 3」。

## Question
引 2-decision **Risks**（寫手用「已經五站了」省 M11；空 attestation 被 chat 帶走；doctor 綠冒充已切；本 slug 被拿去試五站 hop）＋ **SC-1／SC-3／SC-4／SC-6／SC-8／SC-9／SC-10**。

在**不改模板、不重開 1A–7A**的前提下，一張狀態流程模擬器能不能讓人**不靠作者口頭**答完這五問？

1. **舊 7 三次等人 vs 新 5**（SC-1／1A）：新 slug、中間 latch 未命中時，前進紀錄有沒有「請人審 A4／A7／提交判定」？謂詞假時停修理由是該謂詞假，還是「先問 owner 要不要繼續」？
2. **表 A／B 條件頁**（brief §3、Decision 首段）：給一列頁，人能否答「產不產／等不等」？A4／A7 twin 仍產但 latch=否；A10 機械綠仍等；A5 無 trigger → n-a；B1 命中才 Demo latch。
3. **Must-keep 假完成**（SC-2／SC-3／6A／RP-1…3）：`Verify: 看起來沒問題`、缺四欄、無 RED、reviewer=implementer、S 寫「適當／TBD」——勾選能不能冒充完成？「已經五站了所以可省」是不是違 brief？
4. **空 attestation + chat「可以」**（SC-4／SC-6／5A／OC-6）：B1 命中、欄空、owner chat 准開 Stage 4 → 能不能離 Spec？Agent 代寫 `ACCEPTED`／Ship `PASS` 算不算已寫？
5. **freeze × dual-read 誠實**（SC-8／SC-9／SC-10／4A／3A）：本目錄已有 `1-discussion.md` → 五站自動前進能不能跳過本 slug 的 G1／G2？`契約 2.0.0 + marketplace 已換五站 hops + doctor exit 0` 能不能說「已切五站」？

答案長什麼樣才算回答了：
- 每張好卡／壞卡人能指出**下一步**、**等不等**、**誰准寫判定**、**空／錯／權限不足怎麼辦**。
- 壞卡（假完成 T、空 attestation、doctor 綠=已切、本 slug 當新 5 白老鼠）一眼是拒絕，不是「簡化成功」。
- 選定 Demo 只有 D1；不另選互動方案。本 hop **不**改 2-decision 正文（回寫列名留給 Human ACCEPTED 之後）。

## Method
- 實驗位置:本檔 Method 節的操作盤（**PROTOTYPE — not production**；純資料／紙上狀態機；不進 throwaway code、不改 `_templates/`／`scripts/`／`graph.yaml`）
- Demo 形式:**狀態流程模擬器**（人依 Demo Script 走同一條 slug 的好卡 vs 壞卡）
- 1A–7A 已 lock → **Demo D1 狀態流程模擬器（選定）**；不做假 Variant（同流程換字不算）
- 驗法:用 Stage 1 AC-1／AC-3／AC-4／AC-6／AC-8 + SC-9 對照各走一遍；壞卡當負向
- 本站**不**回寫 2-decision（獨立於 B；Human verdict 未出）。確認紀錄「prototype 回寫」等人類 ACCEPTED

### Demo D1 — 狀態流程模擬器（選定）

| 項 | D1（選定；鎖定 Decision 的操作面） |
|---|---|
| 主要角色 | 母版 owner；coordinator（F2 後）；Build 實作者；獨立 T reviewer；Ship 審查者；採用端 owner |
| 真實目標 | 摺例行等人，但不丟完整度；Ship 仍由人出貨 |
| 入口 | 新 slug（F3 後五站）vs 本目錄（已有 md = 舊 7 freeze） |
| 關鍵操作 | 評表 A／B 謂詞 → 真則 hop／假則停修；latch 真才把頁給人 |
| 等待狀態 | 預設只 Ship；B1 命中才第二次人停；本 slug 仍例行 G1／G2 |
| 空狀態 | 無 `3-prototype.md` 或九條全未勾 → A5 n-a，不建頁 |
| 錯誤狀態 | 謂詞假停該站修；Agent 代寫判定 = 未寫；假完成 T checkbox 仍未完成 |
| 權限不足 | coordinator 禁問「要不要繼續」；未 upgrade 不得遠端改線 |
| 資料過期 | Q6 Assumption 過期擋**本 slug G2**（不是擋本 Stage 3） |
| 中斷恢復 | 檔名家族不動（`1-discussion.md`…`7-review.md`）；從該站 md 接著評謂詞 |
| 系統外下一步 | chat 不是判定；marketplace update 換 hops ≠ 已切五站 |

#### 盤 1 — 舊 7 三次等人 vs 新 5（SC-1）

| 步 | 舊 7（現行 Journey） | 等誰 | 新 5（F3 後新 slug） | 等誰 |
|---|---|---|---|---|
| Intake／1 | 寫 1-discussion | 無人（人可看 A1） | 同左；OQ 解完或標假設 → hop | 否 |
| Decide／2 | 寫 2-decision → **G1 等人按提交** | owner | Decision+OC 全裁決 → hop；**A4 twin 仍產** | **否**（殺例行） |
| Spec 條件／3 | trigger 命中 → 等人寫 `ACCEPTED`；現場可 chat 繞 | owner | 未命中 → 不產 Demo；命中 → **B1 latch** | 僅 B1 |
| Spec／4 | 寫 4-spec → **G2 等人按提交** | owner | 形狀綠 + B1 已熄 → hop；**A7 twin 仍產** | **否**（殺例行） |
| Build／5–6 | 切 T、seam、等人審每個 T | 獨立 reviewer（T 級，不是例行閘） | 同左；A8／A9 **不准**因「想給人看任務板」停 | T 級 seam，不是第三閘 |
| Ship／7 | G3 等人 | owner | **唯一預設人停**；機械綠仍 `HumanWait` | **是** |

謂詞假（例：OC 有「待裁決」、S 含 TBD、T 缺 Verify）→ **停在該站修**。禁改問「要不要繼續」。

<details>
<summary>點我：舊 7 人腦消耗（對照，不是選定）</summary>

現行痛（1-discussion Journey 步 2–7）：G1 chat「Treat as PASS」→ Demo 欄空仍開 Stage 4 → 同日 G2 再蓋一次 → 注意力在 Ship 前耗盡。摺的是這三次**例行停**，不是 G1／G2／`ACCEPTED` 檔或 token。
</details>

<details>
<summary>點我：新 5 人只在兩種情況停</summary>

1. **A10 Ship**：永遠 latch。無人 `verdict: PASS` → 不得 Done。Agent 寫 PASS = 未寫（RP-8／RP-16）。
2. **B1 Demo**：九條 trigger 任一命中才 latch。未命中不准產頁、不准問人（RP-12／RP-14）。
B4 Quiz 可與 Ship **同一**人停；不准拆成第三次例行停。
</details>

#### 盤 2 — 表 A／B 條件頁（產不產／等不等）

| ID | 人看的 | 生成？ | latch？ | 人該看見的下一步 |
|---|---|---|---|---|
| A3 | Decide 審頁 | 有 `2-decision.md` → 產 | 否 | 看 Decision／OC 是否全裁決；**不要**等 G1 提交 |
| A4 | 方向卡（舊 G1 twin） | 同上 → **仍產** | **否** | twin 給 dual-read／舊 7；五站不等 `verdict:` |
| A5 | 原型審頁 | 有 `3-prototype.md` **且** trigger≥1 → 產 | 否（人走 B1） | 無檔或全未勾 → n-a、不建頁、不算缺 |
| A7 | 契約卡（舊 G2 twin） | 有 `4-spec.md` → **仍產** | **否** | Demo 條件在 B1，不在 A7 等人 |
| A8 | 任務板 | 有 `5-tasks.md` → 產 | 否 | 每 T 四欄；想給人看板 ≠ 停點 |
| A10 | 出貨審頁 + G3 twin | 有 `7-review.md` → 產 | **是（唯一預設）** | 機械全綠仍等人寫頂欄 |
| B1 | Demo + `ACCEPTED` | 九條任一命中 | **是** | 人類親填 + attestation；chat 准開無效 |
| B2 | UI twin | UI/flow（與 B1 三條重疊） | 與 B1 **同一**次人停 | 純守衛／文件 → 不產 |
| B4 | Quiz | 不可逆才做 | 是；可併 Ship | 非不可逆做 Quiz = 把例行停加回（違 G-out-1） |

<details>
<summary>點我：壞例 — latch 未命中卻問人（RP-14）</summary>

coordinator 在 A4／A7 彈「請 owner 看一下／要不要繼續」→ **紅**。不是客氣，是違 brief §3 出口第 5 步。
</details>

<details>
<summary>點我：好例 — A5 n-a（本盤對「純後端 feat」）</summary>

九條全未勾 → 最小 `3-prototype.md`、不建 html、G2 Demo = N/A + 原因。**本 slug 不是這條**：上面已命中 7 條。
</details>

#### 盤 3 — Must-keep 假完成對照（SC-2／SC-3）

**好卡 T-ok**（四欄 + seam；checkbox 才准勾）

```
T-ok  補 dual-read 誠實句
- Covers: S-dual-read-honest
- Files: hooks/_doctor_impl.py, docs/dev/<slug>/annex.md
- Verify: 契約 2.0.0 + 五站 hops → 牙紅；舊 7 缺新欄 → 不紅
- Blocked-by: F1 annex 欄位名
- RED: test_s_dual_read_honest 先紅（測試名含 S-id）
- reviewer: 另一 session ≠ 實作者
```

**壞卡 T-fake**（1-discussion AC-3 對照稿；C 線主風險）

```
T-fake  五站簡化收尾
- Covers: （缺）
- Files: （缺）
- Verify: 看起來沒問題
- Blocked-by: （缺）
- [x] done
- RED: 無
- reviewer: 實作者自己
- 註: 已經五站了，四欄／seam 可選
```

人該看見：T-fake **未完成**。RP-1 缺四欄 → 紅；RP-2 無 RED 或 reviewer=implementer → 未完成；SC-2 少 M11／M3／M1 = 違 brief，不是簡化成功。勾選 ≠ 完成。

**壞卡 S-fuzzy**

```
S-99  系統應適當處理錯誤（TBD，實作再定）
```

人該看見：RP-3 紅（TBD／不可測／模糊詞）。測試名若不含 S-id → RP-4 紅。

<details>
<summary>點我：權限／空／中斷</summary>

- 權限不足：實作者自審自己的 T → 縫不存在，不得標完成。
- 空狀態：四欄空白的 T 卡 = 還沒開工，不是「五站比較乾淨」。
- 中斷恢復：從 5-tasks 該 T 四欄接著補；不要另寫「已簡化」散文當完成。
- 系統外：沒有 RED 輸出貼在 6-notes → M10／RP-6，摘要不能當證據。
</details>

#### 盤 4 — 空 attestation 與 chat 蓋章（SC-4／SC-6）

| 卡 | 頂欄／欄位 | chat | 人該判定 |
|---|---|---|---|
| 好卡 B1 | `Human verdict: ACCEPTED` + `Verdict attestation: human:rick @ 2026-09-14` | （無關） | 可離 Spec（B1 熄火） |
| 壞卡 dogfood | Human verdict 空；attestation 空 | 「可以開 Stage 4」 | **不得離 Spec**（RP-13／OC-6）。chat 不是判定 |
| 壞卡 Agent | Agent 寫入 `ACCEPTED` 或 Ship `PASS` | 「Treat as PASS」 | **視為未寫**（RP-16）。本 hop **不**示範填 ACCEPTED |

本檔自己就是壞卡 dogfood 的**反面練習**：trigger 已命中、Human verdict = `NOT_REVIEWED`、attestation 空 → **語意上** G2 應拒，直到人類親填。Agent 不得把這段改成 ACCEPTED。

**實跑假完成（本 hop 證據，不改牙）**：`python3 hooks/_stage3_impl.py five-station-simplify` 把 2-decision 內部技術選擇「不預先跳過 Stage 3…（本檔無「跳過 Stage 3」流程層 OC）」讀成 skip OC（同一行同時命中 `Stage 3` 與「跳過」）。句子的意思是**不准跳**。勾選綠、語意紅——與 T-fake 同型。本 hop 不改 `_stage3_impl.py`（F0／Backlog B；牙形交 F1）。人審本 Demo 時不要把這次誤 PASS 當成 Human ACCEPTED。

```
# 原始輸出摘要 2026-09-14
g2_demo=PASS
trigger_source=owner-call
verdict=NOT_REVIEWED
verdict_attestation=null
owner_call="- 不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。"
```

#### 盤 5 — 本 slug freeze × doctor 綠（SC-8／SC-9／SC-10）

| 卡 | 事實 | 人該判定 |
|---|---|---|
| 好卡 freeze | `docs/dev/five-station-simplify/` 已有 `1-discussion.md` | 整段**舊 7**到自己的 Ship。五站 hop 跳 G1／G2 → **跳不過**（RP-15） |
| 壞卡 白老鼠 | 「本 slug 先吃五站藥驗證謂詞」 | 4C 已拒；觀測被自己污染 |
| 好卡 舊檔 | 2.1.0 讀舊 7、新 5 欄缺省 | **不紅**（誠實句第 2 句） |
| 壞卡 陷阱 | 契約仍 `2.0.0` + marketplace 已換五站 hops + doctor exit 0 | **不得**說「已切五站」。doctor 綠 = 握手，≠ 路線。未 upgrade = 舊 7（OC-1 第 3 句／SC-10） |

僅有 html、無 md ≠ in-flight（OC-5）。本 hop 不鎖 annex 鍵名（OC-3）。

## 結構圖
- Demo D1 狀態流程模擬器（選定）
- 舊7 三次例行等人（對照）
- Decide／Spec 殺例行停
- 表 A／B 產頁≠latch
- 假完成 T 仍紅
- Ship 唯一人停

```
old7:  wait G1 → wait S3 → wait G2 → wait G3
new5:  Intake → Decide → Spec → Build → Ship[human]
         |         |        |       |
         no wait   A4 no    B1?     A8/A9 no latch
                   latch    only    T seam stays
D1 selected: cards above; 1A-7A not reopened
```

## Demo Script
帶使用者走 D1。不要問「喜不喜歡」。逐場確認:看到畫面後知道下一步嗎？系統是否暗示了不存在的權限？等待狀態是否清楚？系統外交接是否可追蹤？資訊不完整時是否知道怎麼辦？能否撤回、重試、改派或恢復？1A–7A 已 lock；比的是人點不點得完。

### Scenario AC-1（新 slug 中間不停）
- 使用者角色:coordinator（F2 後）／母版 owner
- 真實目標:Decide／Spec／Build 完成且中間 latch 未命中時，不在 A4／A7 等人按提交
- 起始狀態:盤 1 新 5 欄；假想新 slug、OC 已裁決、B1 未命中、T 四欄+seam 齊
- 操作步驟:從 Intake 走到 Ship 前；每站問「現在等誰？」；對照舊 7 欄的三次等人
- 系統回應:中間前進紀錄沒有「請人審 A4／A7」。謂詞假 → 停修理由寫該謂詞，不彈「要不要繼續」
- 系統外下一步:無（不准改問 owner 來繞假謂詞）
- 觀察問題:下一步是 hop 還是等人？有沒有暗示「twin 產了 = 要按提交」？

### Scenario AC-6（表 A／B：產不產／等不等）
- 使用者角色:母版 owner
- 真實目標:對 A4／A5／A7／A10／B1 各答生成與 latch
- 起始狀態:盤 2 表；另開一張「純守衛 feat、九條未勾」
- 操作步驟:遮住作者說明，只看「有沒有檔／有沒有命中」；對 A4 說出「twin 仍產、不等」；對 A5 未命中說 n-a；對 A10 說機械綠仍等
- 系統回應:A4／A7 latch=否；A10 latch=是；B1 未命中不產 Demo；latch 未命中卻問人 → 紅
- 系統外下一步:把頁 URL 只在 latch=是時丟給人
- 觀察問題:等待清不清楚？A4 還在會不會被當成「G1 仍要簽」？Quiz 有沒有被當成每次必停？

### Scenario AC-3（假完成 T）
- 使用者角色:獨立 T reviewer／Ship 審查者
- 真實目標:缺四欄或無 RED／自審的 T 不得完成；「已五站故可省」是違規
- 起始狀態:盤 3 好卡 T-ok vs 壞卡 T-fake、S-fuzzy
- 操作步驟:只看該 T；數四欄是否非空；找 RED 輸出與 reviewer 是否別人；讀 S-fuzzy 有無 TBD
- 系統回應:T-fake 即使 `[x] done` 仍未完成（RP-1／RP-2）。S-fuzzy 紅（RP-3）。少 M11 = 違 brief（SC-2）
- 系統外下一步:退回補欄／補 RED／換 reviewer；不要用 chat「看起來可以」勾完
- 觀察問題:系統有沒有暗示勾選=完成？空欄時知不知道怎麼辦？能否拒絕自審？

### Scenario AC-4（空 attestation + Agent 代寫）
- 使用者角色:母版 owner
- 真實目標:B1 命中時無 attestation 不得離 Spec；Agent 寫 `ACCEPTED`／Ship `PASS` = 未寫
- 起始狀態:盤 4 三張卡；對照 dogfood-ping DOGFOOD-NOTES L9
- 操作步驟:先看好卡完整行；再看「欄空 + chat 可以開 Stage 4」；最後看 Agent 代填
- 系統回應:壞卡不得 hop 出 Spec（RP-13）。代寫視為未寫（RP-16）。本檔現況 = NOT_REVIEWED，**正該**卡在本站
- 系統外下一步:人類親做 Demo、親寫 attestation；不要叫 Agent 代填
- 觀察問題:chat「可以」有沒有被當成 attestation？系統是否暗示 Agent 有權簽？

### Scenario AC-8（本 slug 仍舊 7）
- 使用者角色:in-flight slug 執行者／coordinator
- 真實目標:對本目錄要求五站自動前進、跳過例行 G1／G2 → 跳不過
- 起始狀態:盤 5 好卡 freeze；本資料夾已有 `1-discussion.md`／`2-decision.md`
- 操作步驟:嘗試把本 slug 寫進五站狀態；對照「僅有 html、無 md」
- 系統回應:已有 1–7 任一 `.md` → 整段舊 7（仍有例行 G1／條件 S3／G2／G3）。裸 html 不凍（OC-5）。4C 白老鼠已拒
- 系統外下一步:本 slug 自己的 G1 已過；自己的 G2／G3 仍走舊 7 等人
- 觀察問題:有沒有暗示「Decision 過了就可以改走五站」？中斷後能否從目錄裡的 md 恢復舊路？

### Scenario SC-9（doctor 綠 ≠ 已切五站）
- 使用者角色:採用專案 owner
- 真實目標:拒絕「doctor 綠 + marketplace 已更新 = 可以跟 hops 走」
- 起始狀態:盤 5 壞卡陷阱：`devflow_contract_version=2.0.0`、hops 已被換成五站預設、doctor exit 0
- 操作步驟:只看這三件事實，回答「現在走哪條路？」
- 系統回應:未 upgrade = 舊 7，不得遠端改線。2.1.0 舊檔缺新欄不紅。綠+不紅 ≠ 已切（OC-1）
- 系統外下一步:`marketplace update` 後仍核契約版本；F1 牙紅「2.0.0+五站 hops」（本站不寫牙）
- 觀察問題:系統是否暗示握手綠=路線沒變？權限上採用端能否拒絕被改線？

### Scenario RP-14（否定「跳過」被牙當成已跳）
- 使用者角色:G2 reviewer／F1 寫牙的人
- 真實目標:「無跳過 Stage 3」不得被讀成 Owner Call 跳過
- 起始狀態:2-decision 內部技術選擇該行；本檔 `NOT_REVIEWED`、attestation 空
- 操作步驟:跑 `python3 hooks/_stage3_impl.py five-station-simplify`；對照該行中文
- 系統回應:2026-09-14 實跑 stdout `g2_demo=PASS`、`trigger_source=owner-call`，引用的正是「不預先跳過／無跳過」句。語意應 REJECT
- 系統外下一步:F1 收緊 skip 謂詞（須同時否定「不／無／不得」）；本 hop 不改牙
- 觀察問題:機械綠有沒有被當成「Stage 3 已跳過、可以開 Stage 4」？

## Result
Agent 依 D1 走完七場（**不是** Human Demo）。答案:鎖定 Decision **點得完**——人只靠卡面就能分開「停點／完整度／握手／freeze」。回寫 2-decision 的條目見 Verdict；**本 hop 不改 2-decision**（獨立於 B；等 Human ACCEPTED）。

| 問 | 模擬器證據 | 壞卡一眼拒絕 |
|---|---|---|
| 1 舊7 vs 新5 | 盤 1：新 5 中間無「請審 A4／A7」；謂詞假停修 | 舊 7 三次等人被當成選定 |
| 2 表 A／B | 盤 2：A4／A7 產且不等；A10 必等；A5 未命中 n-a | latch 未命中卻問人 |
| 3 假完成 | 盤 3：T-fake 缺欄+自審+「看起來沒問題」= 未完成 | 「已五站故可省四欄」 |
| 4 空 attestation | 盤 4：chat 准開 ≠ 判定；本檔 NOT_REVIEWED **應**卡本站 | Agent 代填 ACCEPTED |
| 5 freeze×doctor | 盤 5：本目錄有 md → 舊 7；2.0.0+綠 ≠ 已切 | 本 slug 當新 5；doctor 綠當路線證據 |
| 6 跳過 OC 誤匹配 | 實跑 `_stage3_impl.py`：否定句「無跳過 Stage 3」被當成 skip | `g2_demo=PASS` 冒充已 Demo |

選定互動 = **D1**（無第二方案）。未改模板、未寫 F1 牙、未切預設路線。Human verdict 仍 `NOT_REVIEWED`；**語意**不得過 G2。現行牙把否定跳過句讀成 skip（原始輸出見盤 4）——記給 F1，本 hop 不修。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填；Agent 禁代填 ACCEPTED／attestation -->
- Demo date:
- Participants:
- Variant reviewed: D1 狀態流程模擬器（選定；無第二 Variant）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED | role=母版 owner | scenario=AC-1
- Verdict attestation:

## Verdict
- **擬回寫 2-decision**（Human ACCEPTED 之後才動；本 hop 不動該檔）:確認紀錄加一行「prototype 回寫 \| 2026-09-14 \| Stage3-A D1：SC-1／A-B／假完成／空 attestation／freeze×doctor 可走完；不重開 1A–7A」。Risks「寫手省 M11」「chat 帶走 attestation」「doctor 綠冒充已切」「本 slug 試五站 hop」旁註「D1 已給人點的對照卡」。內部技術選擇維持「不跳過 Stage 3」。
- 互動／Human verdict：**NOT_REVIEWED**。本檔 `status: draft`。Agent 不發明 ACCEPTED、不填 attestation。
- 實驗產物:操作盤留在本檔 Method；無 throwaway branch、無正式碼。審頁由 `scripts/build-stage3-html.py --action` 重生。第 3 站已行使，未跳過。
- 本 PR 檔集只准 `3-prototype.md` + `3-prototype.html`。不改 STATUS。不合併。
