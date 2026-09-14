---
feature: five-station-f3
stage: 3-prototype
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 3. 原型 — F3 cut／defaults：九條觸發是否命中？（Writer B）

> Lane = **full**。G1 已核（`2-decision.md` `verdict: PASS`、OC-1…OC-12 ✅ Owner PASS）。2-decision 內部技術選擇明寫「不預先跳過 Stage 3；觸發判定留給該站」（無「跳過 Stage 3」流程層 OC）。本站**評九條、不預跳**。
> Writer B。F3 = **cut／defaults**：新 slug 預設五站；舊 7 只服務 freeze + dual-read；guide／STATUS 用語切五站。骨架已 lock **1A+2A+3C+4A+5A+6A**。剩餘 OPEN 是 4-spec 鍵名／切換機制／電池檔名，不是「點哪」。
> 本 hop **只本檔 + 審頁 html**。不改 `2-decision.md`、不改 STATUS／HISTORY、不填 Human ACCEPTED、不發明 G2、不開 Stage 4、不寫 cut 碼。
> 對照正本：`1-discussion.md` Real-world Context（Actors／Current Journey／Workarounds／Exceptions）。Decision 只當「已 lock、不重開」的邊界，不重評 1A–6A。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context 逐條判定,命中打 [x]。全未命中 → 本階段維持選配;本節九條全未勾即 G2 機械閘 N/A 記錄。 -->
- [ ] 有新的前端流程（F3 是預設路線位元／契約鍵／graph 預設／doctor 清單／guide 用語，沒有新產品畫面）
- [ ] 改變使用者下一步（新 slug「不等例行 G1／G2」已是 F0–F2 + Decision 3C 的核准 Pattern，不是本刀要試的新「點哪」）
- [ ] 涉及角色交接（角色表沿用 F0–F2；F3 不新增誰把工作遞給誰的交接面）
- [ ] 涉及人工核准（不新增人批關卡；token 不刪；cut SoT 是可見紀錄格，不是新核准畫面）
- [ ] 涉及等待/退回/逾時（等待語意已 lock：新 slug 中間不等、in-flight 仍等、Ship 仍等；本刀不設計新等待面）
- [ ] 涉及權限差異（Agent 禁寫判定、未 upgrade 不得遠端改線＝F1／F2 牙；F3 不新增權限畫面）
- [ ] 涉及系統外動作（marketplace／doctor／chat 語意已鎖：綠≠切線、chat≠判定；F3 不設計新系統外交接）
- [ ] 涉及多種可行互動設計（Q21 四選項已收斂 3C；OPEN 是落點／機制形，不是互動 Variant）
- [ ] Stage 1 尚有操作流程不確定性（Journey 已清；OPEN 不是「下一步點哪」）

→ 命中 **0** 條。本階段維持選配。全未勾清單即「無 trigger + 明確原因」記錄。**Demo = N/A**。不建可操作 Demo、不湊假 Variant。本 hop 仍落完整判定表，讓後站看得見為什麼是 0，不是空白跳過。

## 九條判定表（原因）

對照 `1-discussion.md` Real-world Context。命中欄全否。

| # | 觸發 | 命中 | 對照（Actors／Journey／Workaround／Exception） | 原因 |
|---|---|---|---|---|
| 1 | 有新的前端流程 | 否 | Actors 是 owner／coordinator／doctor／寫手／審查者；工具是 git、doctor CLI、graph、看板。無產品畫面 | F3 改的是預設路線與用語。方法論審頁／站檔不是新前端。與 F0 simplify「方法論 UI ≠ 本條」同一刀口 |
| 2 | 改變使用者下一步 | 否 | Journey 步 4：新 slug 寫手現況仍經 `N7-g1` 等人。Decision 3C：cut 後不再例行停 | 「下一步」的**設計**已在 F0–F2 lock，且 simplify Stage 3 已走過舊 7 vs 新 5。F3 只切預設開關讓核准 Pattern 生效。沒有新的「點哪才前進」要試。位元翻轉 ≠ 新互動下一步 |
| 3 | 涉及角色交接 | 否 | Actors 表：owner → 實作 agent → coordinator → 採用 owner → in-flight 執行者 → Ship 審查者 | 交接名單沿用 prior knives。F3 不新增交接畫面或改誰遞給誰。1A 的 who／when／which 是紀錄槽，不是新交接儀式 |
| 4 | 涉及人工核准 | 否 | 鎖：不刪 G1／G2／`ACCEPTED`。Ship 仍唯人。Q15／1A：cut 要可見紀錄 | F3 不新增人批關卡；摺的是新 slug 例行停，不是加核准面。可見紀錄是檔／條件，不是點核准 Demo |
| 5 | 涉及等待/退回/逾時 | 否 | Journey 步 4／6：現況等人；3C observable：新 slug 不等、in-flight 仍停 `N7-g1`／`N6-g2`、Ship 仍等 | 等待語意已是 Decision 約束 7／13／14。本站不設計新的等待／退回／逾時畫面 |
| 6 | 涉及權限差異 | 否 | Exception：未宣告不得遠端改線。F1／F2：Agent 禁寫 `ACCEPTED`／Ship `PASS` | 權限牙已落地。F3 不新增「誰看得到哪一格」的權限畫面 |
| 7 | 涉及系統外動作 | 否 | Journey 步 2–3：marketplace update、doctor `COMPATIBLE`。Workaround：chat 當 hop 開關 | 系統外工具**語意已鎖**（Q9／Q10／4A：綠≠ticket、marketplace≠cut、chat≠判定）。F3 不設計新的系統外交接要人走一遍 |
| 8 | 涉及多種可行互動設計 | 否 | Q21 四選項已在 Decision 選定 3C（兩者都要、節點不刪）。1A 路徑／graph 切換機制 OPEN 交 4-spec | OPEN 的是鍵名、切換機制形、電池檔名——規格落點，不是「操作順序／資訊階層／決策點」的互動分叉。禁湊同流程換字的假 Variant |
| 9 | Stage 1 尚有操作流程不確定性 | 否 | Current Journey 八步已寫現況；Decision 已收 Q15–Q27 | 人怎麼走（cut 後新 slug 五站、本目錄舊 7 到 Ship）已確定。不確定的是實作落點，不是操作流程 |

## Question
引 2-decision **內部技術選擇**「不預先跳過 Stage 3」＋ **Risks**（silent True、只改用字、本 slug 當白老鼠）＋ Real-world Context。

本站要回答的不是「cut 怎麼切」（1A–6A 已 lock），而是：

1. **九條對 F3 cut／defaults 有沒有互動風險命中？**
2. **0 命中時，Demo = N/A 是否仍是合法 Stage 3 記錄**（機械閘可過、不是空白跳過、不是 Agent 代填 ACCEPTED）？

答案長什麼樣才算回答了：
- 九條各有一句對照 Real-world Context 的原因；命中數可數。
- 命中 0 → 九條全未勾 + Demo N/A + 原因表；`_stage3_impl.py` 讀成 N/A PASS。無 Human ACCEPTED、無 attestation。
- 若有命中 → 做最薄 Demo（本評 = 0，不走這路）。
- 本 hop **不**回寫 2-decision 正文（Writer B draft；0 命中無實驗答案要回寫）。

## Method
- 實驗位置:本檔觸發判定節 + 上表（**PROTOTYPE — not production**；紙上對照 1-discussion Real-world Context。無 throwaway code、不進 scratchpad 碼、不改 `_templates/`／`graph.yaml`／doctor／契約）
- Demo 形式:**N/A**（0 命中 = 無真實世界互動風險 → 可操作 Demo 不必要）
- Variant:**無**。互動方案不是未定；禁湊假 Variant
- 驗法:逐條對 Actors／Journey／Workarounds／Exceptions；再對 Decision 1A–6A「已 lock 則本條不重開互動」。跑 `python3 hooks/_stage3_impl.py five-station-f3` 確認 0 命中 → `g2_demo=PASS`（N/A）
- 本 hop **不**回寫 2-decision、**不**填 Human ACCEPTED

## 結構圖
- N/A 路徑（選定；0 命中）
- 九條全未勾
- Demo N/A
- 機械閘 N/A PASS
- 本 hop 不回寫 2-decision

```
RWC nine triggers
|-- 1 frontend          miss
|-- 2 next-step         miss  (Pattern already locked)
|-- 3 handoff           miss
|-- 4 human-approve     miss
|-- 5 wait/timeout      miss
|-- 6 permission        miss
|-- 7 external          miss
|-- 8 multi-interaction miss
+-- 9 flow-uncertain    miss
        |
        v
hit count = 0  (選定 N/A)
        |
        +--> 3-prototype.md checklist all unchecked
        +--> Demo = N/A (no clickable / no CLI flow)
        +--> _stage3_impl.py g2_demo=PASS (N/A)
        +--> no Human ACCEPTED / no attestation
        +--> this hop does not write 2-decision
```

## Demo Script
0 命中 → **不請人點、不跑 throwaway**。本節只把 N/A 寫成可審查的「不走 Demo」腳本，避免後站把「沒有 Demo Script」誤讀成還沒評。

### Scenario N/A（0 命中，不走可操作 Demo）
- 使用者角色:G2 reviewer／後站寫 4-spec 的人
- 真實目標:確認 F3 cut／defaults 沒有新互動風險；不要為湊數做假 Demo
- 起始狀態:本檔九條全未勾；2-decision 無「跳過 Stage 3」OC；G1 已 PASS
- 操作步驟:讀上表九行原因；對照 1-discussion Journey 步 1–8 與 Decision 1A–6A；確認沒有「點哪／等誰的新畫面」仍 OPEN
- 系統回應:命中 0。不產可點 HTML／CLI flow／Storybook。機械閘讀全未勾 → Demo verdict N/A
- 系統外下一步:無 Demo 邀約。協調者比稿後才決定要不要開 Stage 4。本 hop 不改 2-decision、不改 STATUS
- 觀察問題:有沒有把「預設路線變了」誤加成「新前端／新下一步」？有沒有 Agent 代填 ACCEPTED？

### Scenario AC-8（對照：本目錄仍舊 7，不是白老鼠）
- 使用者角色:in-flight 執行者／coordinator
- 真實目標:就算本檔多了 `3-prototype.md`，本 slug 仍不是第一隻活五站
- 起始狀態:本目錄已有 `1-discussion.md`／`2-decision.md`（＋本檔）= in-flight
- 操作步驟:問「本 hop 落 3-prototype 會不會把本 slug 切成五站機？」
- 系統回應:SLOT-IN-FLIGHT-DETECT：任一 1–7 `.md` → 整段舊 7。本檔是舊 7 的 Stage 3 記錄，不是五站 hop
- 系統外下一步:無
- 觀察問題:系統有沒有暗示「寫了 Stage 3 就可以試五站」？

## Result
- **命中數 = 0／9**。九條全未勾。Demo = **N/A**（無互動風險，不是還沒 Demo）。
- 證據：上表九行原因 + 1-discussion Real-world Context（Journey 步 1–8、G-cut／G-graph／G-self）+ 2-decision「不預先跳過」且無 skip OC + 1A–6A 已 lock。
- `_stage3_impl.py five-station-f3` 本 hop 實跑（exit 0）：

```
stage3(five-station-f3): PASS — 觸發判定 0/9 命中(全未勾清單即 N/A + 明確原因記錄)→ Demo verdict N/A,可過 G2
trigger=false
trigger_hits=[]
verdict=null
verdict_attestation=null
g2_demo=PASS
prototype_status=draft
```

`owner_call` 欄位掃到 2-decision「不預先跳過 Stage 3」句（同時含「Stage 3」與「跳過」）——與 simplify 盤 4 同型誤匹配。本檔 **0 命中走 N/A 支路**，不靠該句當 skip OC。本 hop 不改 `_stage3_impl.py`。
- 不選「為了看起來有做 Stage 3 而做最薄假 Demo」。那會把 0 命中做成假 hit，G2 反而要 ACCEPTED。
- 本 hop **不**回寫 2-decision。0 命中無實驗答案；Decision 約束不變。

## User Demo Feedback
<!-- 0 命中 → 無 Demo 可走。Human verdict 不得填 ACCEPTED。Agent 禁寫 attestation。 -->
- Demo date: n-a（無 Demo）
- Participants: Writer B（評九條；未邀人點）
- Variant reviewed: n-a（無 Variant）
- Accepted interaction: n-a
- Rejected interaction: 為湊數做的假可操作 Demo（0 命中仍做點擊／CLI）
- Confusions observed: 「預設路線變了」容易被誤讀成「改變使用者下一步」——本表把該條標否，並寫清：設計已 lock，本刀只切開關
- Missing real-world steps: 無（Journey 已清）
- Permission corrections: 無
- External handoffs: 無新交接
- Required changes: 無
- Human verdict: N/A
  （0 命中；未 Demo ≠ NOT_REVIEWED 欠債；機械閘走 N/A，不走 ACCEPTED。Agent 不寫 attestation）

## Verdict
- **本 hop 不回寫 2-decision**（Writer B draft；使用者：only `3-prototype.md` + html）。0 命中無需把實驗答案寫回 Risks／SC。2-decision 內部技術選擇「不預先跳過 Stage 3」已被本檔行使：九條已評、不是預跳。
- Human 判定：**不填 ACCEPTED**。無 attestation。`status: draft`（Writer B 比稿；不是 Human Stage 3 收尾）。
- 實驗產物:判定表留在本檔；無 throwaway branch。審頁由 `scripts/build-stage3-html.py --action` 重生（有檔即印頁，供人讀 0／9；不是可操作 Demo）。
- 第 3 站：已評價、0 命中、Demo N/A。未跳過（無 skip OC）。未發明 G2。
