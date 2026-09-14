---
feature: five-station-f3
stage: 3-prototype
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 3. 原型 — 五站 F3 cut：九條觸發有沒有命中？（0 → Demo N/A）

> Lane = **full**。G1 已核（`2-decision.md` `verdict: PASS`、OC-1…OC-12 ✅）。Writer A 主軸：**先做觸發判定**，不預先跳過、也不預先當必要。
> Decision 內部技術選擇：「不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。」(`docs/dev/five-station-f3/2-decision.md:L305`)
> 本刀 = 新 slug 預設五站的 **cut**（契約／guide／graph+dual-read／doctor 誠實）。**沒有新前端 UI。** 五站 vs 舊 7 的下一步 UX 已在 `five-station-simplify` Stage 3 D1 ACCEPTED；本站不重做那張模擬器。
> 本 hop **只本檔 + 審頁 html**。不改 `_templates/`／`graph.yaml`／gate／契約／doctor／coordinator、不改 STATUS／HISTORY、**不改 `2-decision.md`**、**不發明 Human ACCEPTED**、不開 Stage 4、不發明 G2 PASS。
> Human verdict 由人類親填。本 hop 留 `NOT_REVIEWED`；attestation 空。Agent 禁代填 ACCEPTED。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context：Actors／Journey／Workarounds／Exceptions；
     與 2-decision 1A–6A 鎖定面。命中打 [x]。本刀九條皆未中。 -->
- [ ] 有新的前端流程（誠實：本刀是契約鍵／cut 紀錄／graph 預設 hop／doctor `supported` 清單。派工明文「No new frontend UI」。guide 改七站單行＝用語交付物，不是產品畫面。`five-station-simplify` 已把方法論審頁判成**不是**本條。`1-discussion.md:L23` F3 刀＝新 slug 預設五站 + 用語；`2-decision.md:L108` Decision 正文無新畫面）
- [ ] 改變使用者下一步（新 slug 不再例行停 `N7-g1`／`N6-g2` 是 **3C 已鎖的 observable**，不是本刀新發明的下一步 UX。該 hop vs 等人面已在 `five-station-simplify` Stage 3 D1 走完。本刀操作者下一步仍是寫可見紀錄、修讀鍵、加 `2.1.0` 進 supported、跑三路電池——檔／碼／測，沒有新的「點哪」。`2-decision.md:L73` 3C；`:L305` 機制交 4-spec；`1-discussion.md:L94` Journey 步 4 是**現況痛**，不是待挑的互動稿）
- [ ] 涉及角色交接（Actors 表已有 owner／實作 agent／coordinator／採用端／in-flight／doctor 操作者／Ship 審查者。`1-discussion.md:L69-L79`。本刀不新增交接畫面、不改誰准寫 `ACCEPTED`／Ship `PASS`。cut SoT＝檔上的誰／何時／哪個條件，路徑交 4-spec，不是角色交接 UI。`2-decision.md:L57` 1A）
- [ ] 涉及人工核准（不刪 G1／G2／`ACCEPTED`；不新增核准 UI。6A 鎖 token 仍在。cut 可見紀錄是 SoT，**不是**新閘。`2-decision.md:L93` 6A；`:L261-L262` Out #2；`1-discussion.md:L196` Q7 不刪閘）
- [ ] 涉及等待/退回/逾時（摺的是新 slug **例行**停點，等待語意已由五站 Pattern 鎖死：預設只 Ship、B1 才第二次人停。本刀不設計新的等待／逾時面。4A 不改 doctor 握手，操作者仍看 `COMPATIBLE`／`INCOMPATIBLE` 一行。in-flight 仍舊 7 等人。`2-decision.md:L79` 4A；`:L108` 摺停點不是新 UX；`1-discussion.md:L109` 舊 7 不套三 cap）
- [ ] 涉及權限差異（Agent／coordinator 仍禁寫 `ACCEPTED`／Ship `PASS`；未宣告 2.1.0 不得遠端改線——這是既有牙／前置，不是新權限畫面。`2-decision.md:L79` doctor ≠ ticket；`:L116` hops 不得早於宣告；`1-discussion.md:L75` 採用端系統外）
- [ ] 涉及系統外動作（Journey 步 2 `marketplace update`、步 3 跑 doctor、GitHub／chat 已存在。本刀不設計新的系統外步驟面，也不把 marketplace／cache 寫成 ticket。STATUS 用語走整合分支 companion＝看板政策，不是新的系統外 UX。`1-discussion.md:L91-L93`；`2-decision.md:L79` 4A；`:L289` OC-2）
- [ ] 涉及多種可行互動設計（1A+2A+3C+4A+5A+6A 已 lock。剩餘 OPEN＝attestation 檔名／graph 切換機制／電池入口檔名——4-spec 釘實作形，不是 2–4 個結構不同的互動 Variant。禁湊假 Variant。`2-decision.md:L108`；`:L307-L309` 內部技術選擇）
- [ ] Stage 1 尚有操作流程不確定性（Q15–Q19 已升格進 Decision；Q20–Q25 本站選定。Journey 八步已清。剩下的是鍵名／檔名／切換機制，不是「下一步點哪、等不等、誰准寫」。`2-decision.md:L326-L327`；`1-discussion.md:L86-L98`）

→ 命中 **0** 條:本階段維持選配。Demo verdict = **N/A** + 上表各條原因。不建可操作 Demo、不湊假互動原型。2-decision 無「跳過 Stage 3」流程層 OC——本站**做了判定**，不是跳過。

## Question
引 2-decision **內部技術選擇**「不預先跳過 Stage 3；觸發判定留給該站」(`2-decision.md:L305`)＋ **Risks**「本 hop 被當成已落地 Stage 3／4」(`:L227`)＋ 1-discussion Journey 步 4／7（新 slug 仍經 `N7-g1`；指南仍寫七站單行）(`1-discussion.md:L94`、`:L97`)。

在**不重開 1A–6A、不重做 five-station-simplify D1**的前提下，本站只答這一問：

**THIS knife（F3 cut：契約／guide／graph+dual-read／doctor 誠實）有沒有 Stage 3 互動風險？**

答案長什麼樣才算回答了：
1. 九條各有 YES／NO + 引用 Decision／1-discussion；不得用「方法論所以全中」或「後端所以全空」一句帶過。
2. **0 命中** → Demo verdict = N/A + 原因落檔；**不**發明可點／可跑的互動原型。
3. 反事實寫清：若某條當時被判中，最薄 Demo 會是哪一條、驗證什麼——本站**不執行**。
4. Human verdict 留 `NOT_REVIEWED`；不發明 ACCEPTED；不改 2-decision 正文；不改 STATUS。

## Method
- 實驗位置:本檔觸發表（**PROTOTYPE — not production**；紙上對照；不進 throwaway code、不改 `_templates/`／`scripts/`／`graph.yaml`／契約／doctor）
- Demo 形式:**無**。0 命中 → 不建可操作 Demo。下節 Demo Script 是**反事實紀錄**（若命中才走），不是給人點的模擬器。
- 驗法:逐條對 1-discussion Real-world Context（Actors／Journey／Workarounds／Exceptions）+ Decision 1A–6A／OC-1…OC-12。已核准 Pattern（五站 hop vs 舊 7 等人）不重開。
- 本 hop **不**回寫 2-decision（只擬記「prototype 回寫」行文；確認紀錄不在本 hop）。不開 Stage 4。

### 反事實：若當時有命中，最薄 Demo 只走該條

| 若命中的條 | 最薄路徑（不執行） | 不走什麼 |
|---|---|---|
| 有新的前端流程 | 不適用；本刀無畫面可 Prototype | 不發明審頁／產品 UI |
| 改變使用者下一步 | 一張紙卡：cut 後新 slug「現在等誰？」vs 舊 7 三次等人——**已由 simplify D1 答過**，本刀再做＝假原型 | 不重做五站狀態機模擬器 |
| 角色交接 | 一張誰→誰表：紀錄誰寫、誰讀 `f3_cut_happened`；函式只讀 | 不新造交接畫面 |
| 人工核准 UI | 一張可見紀錄卡：誰／何時／哪個條件 vs `return True`（對齊 AC-4／ATTEST-SILENT-RED） | 不新增閘、不代填 ACCEPTED |
| 等待／逾時 UX | 對照「例行停已摺、Ship 仍等」——已是 3C／五站 Pattern | 不設計新 timeout 面 |
| 權限 UX | 對照「未 2.1.0 不得改線；Agent 禁寫判定」——已是牙／前置 | 不新造權限畫面 |
| 系統外動作 UX | 對照 Journey 步 2–3：`marketplace update` ≠ cut；doctor 綠 ≠ ticket | 不新造升級精靈 |
| 多種互動設計 | 不適用；1A–6A 已 lock | 不湊假 Variant |
| 操作流程不確定 | 不適用；Q15–Q25 已收進 Decision | 不把檔名 OPEN 當互動未定 |

0 命中 → 上表**全部不執行**。沒有 throwaway branch、沒有 CLI Demo、沒有狀態流程模擬器。

## 結構圖
- 對照 RWC／Decision 九條
- 全未勾 → Demo N/A（選定）
- 不建可操作原型
- 反事實最薄紙卡（不執行）
- 擬回寫 2-decision（本 hop 不改）

```
RWC + Decision 1A-6A
        |
        v
九條觸發判定
        |
        +-- 0 命中 --> Demo verdict N/A（選定）
        |                 不建可操作 Demo
        |                 Human = NOT_REVIEWED
        +-- 若命中 --> 只走該條最薄紙卡（本站不執行）
```

## Demo Script
0 命中，**本站不帶人走可操作 Demo**。下列是「若命中才走」的反事實腳本，供後讀看見本站沒偷省略紀錄。不要問「喜不喜歡」。本 hop 不跑、不產 throwaway。

### Scenario 反事實-N/A（本站實際路徑）
- 使用者角色:母版 owner／G2 reviewer
- 真實目標:確認本刀九條是否有互動風險；0 命中則 Demo = N/A，不是「忘了做 Stage 3」
- 起始狀態:G1 PASS；2-decision 無「跳過 Stage 3」OC；本目錄已有 `1-discussion.md`／`2-decision.md`（in-flight，出貨仍舊 7）
- 操作步驟:讀上表九條＋引用；數勾選；對照 simplify D1 是否已答「下一步／等人」
- 系統回應:0／9 未勾。機械閘 `_stage3_impl.py` 讀全未勾 → Demo verdict N/A，可過後續 G2 的 Demo 條件（仍須 R/S／DD／Profile；本 hop **不**送 G2）
- 系統外下一步:無 Demo 可做。不要叫 Agent 填 ACCEPTED。不要把 N/A 寫成「已 Demo」
- 觀察問題:有沒有哪一條被「方法論所以全中」誤勾？有沒有把 cut 本身當成新前端？

### Scenario AC-4（反事實：若「人工核准 UI」命中才走）
- 使用者角色:母版 owner
- 真實目標:人指得到誰／何時／讀哪個條件；`return True` 無紀錄不得當切
- 起始狀態:Decision 1A／AC-4／ATTEST-SILENT-RED 已 lock；檔名未釘
- 操作步驟:（不執行）看好卡「可見紀錄三槽」vs 壞卡「只改函式 True」
- 系統回應:（不執行）壞卡應拒；好卡人指得到三槽。本站不造這張可點卡
- 系統外下一步:4-spec 釘檔名／鍵名；Stage 6 才寫紀錄與讀端
- 觀察問題:若本條被判中，紙卡是否已夠、還是真的需要核准 UI？本站判定＝不夠構成 trigger

## Result
Agent 依九條對完 RWC／Decision（**不是** Human Demo）。答案:

| 問 | 證據 | 一眼拒絕 |
|---|---|---|
| 九條有沒有中？ | 上表 0／9；各條附 Decision／1-discussion 行 | 「方法論所以全中」；把 cut 當新前端 |
| Demo 要不要做？ | 0 命中 → **Demo verdict = N/A** + 各條原因 | 為湊 Stage 3 發明可點原型 |
| 若命中最薄是什麼？ | Method 反事實表；只該條紙卡；不重做 simplify D1 | 重開 1A–6A；假 Variant |
| Human？ | `NOT_REVIEWED`；attestation 空 | Agent 代填 ACCEPTED |

回寫對象:2-decision 內部技術選擇「觸發判定留給該站」——判定已做、結果＝0 命中 N/A。**本 hop 不改 2-decision 正文。**

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填。0 命中＝無 Demo 可做。Agent 禁代填 ACCEPTED／attestation。 -->
- Demo date:
- Participants:
- Variant reviewed:
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
- **Demo verdict = N/A**（觸發判定 0／9 + 上表原因）。不是 REVISE，不是 ACCEPTED。未 Demo ≠ 失敗；本刀無互動風險可點。
- **擬回寫 2-decision**（本 hop 仍不動該檔；不開 Stage 4）:確認紀錄加一行「prototype 回寫 \| 2026-09-14 \| Stage3-A：九條 0 命中，Demo N/A；不建可操作原型；Human NOT_REVIEWED」。內部技術選擇維持「不跳過 Stage 3；觸發判定留給該站」——該站已行使判定。
- Human 判定 **NOT_REVIEWED**。attestation 空。**不發明 ACCEPTED。** 本檔 `status: draft` 直至人類親裁觸發表（0 命中無 Demo 可接受）。**不送 G2、不開 4-spec。**
- 實驗產物:觸發表留在本檔；無 throwaway branch、無正式碼。審頁由 `scripts/build-stage3-html.py --action` 重生（讓人看見 0／9 與反事實卡；**不是**可操作 Demo）。N-skip 契約「零命中不建 html」指最小清單檔；本 hop 依 Writer A 派工仍產頁，方便人審判定，不表示有 trigger。
- 本 PR 檔集只准 `3-prototype.md` + `3-prototype.html`。不改 STATUS。不發明 G2。第 3 站已做判定，未跳過、未做互動實驗。
