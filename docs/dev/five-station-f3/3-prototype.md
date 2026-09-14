---
feature: five-station-f3
stage: 3-prototype
status: approved
owner: rick
reviewers: [user]
updated: 2026-09-14
---

# 3. 原型 — 五站 F3 cut：九條觸發有沒有命中？（0 → Demo N/A）

> Lane = **full**。G1 已核（`2-decision.md` `verdict: PASS`、OC-1…OC-12 ✅）。**Winner A**（#373；R1→A、R2→A、R3→B；多數 A）。本檔含 **owner standing soft-fix**：骨架仍 A，吸收 B（#371）L1，不換 winner、不改寫 Decision 1A–6A。
> Writer A 主軸：**先做觸發判定**，不預先跳過、也不預先當必要。
> Decision 內部技術選擇：「不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。」(`docs/dev/five-station-f3/2-decision.md:L305`)
> 本刀 = 新 slug 預設五站的 **cut**（契約／guide／graph+dual-read／doctor 誠實）。**沒有新前端 UI。** 五站 vs 舊 7 的下一步 UX 已在 `five-station-simplify` Stage 3 D1 ACCEPTED；本站不重做那張模擬器。**不吸收 C（#372）的 6／9 或 D1 四板。**
> 本 hop **只本檔**。N-skip／`_templates/3-prototype.md` 零命中：**不建** `3-prototype.html`（standing 已刪 A 審頁 twin；產檔器若數到反事實 `### Scenario` 會假顯「Demo: 2」）。不改 `_templates/`／`graph.yaml`／gate／契約／doctor／coordinator、不改 STATUS／HISTORY、**不改 `2-decision.md`**、不開 4-spec、不發明 G2 PASS。
> **Demo verdict = N/A**（機械：0／9 無互動風險）。owner chat 2026-09-14 Asia/Taipei「接受」= Human ACCEPTED（scenario=0/9 Demo N/A accepted）。attestation `human:rick @ 2026-09-14`。N-skip 慣例 `status: approved`。**不發明 G2。** coordinator 下一刀才開 Stage 4 writers。

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

**註（AC-8／G-self-1，不是 Demo 欄、不是可操作場）：** 本 hop 落 `3-prototype.md` **不會**把本 slug 切成五站機。SLOT-IN-FLIGHT-DETECT：任一 1–7 `.md` → 整段舊 7（`1-discussion.md:L39`、`:L265` AC-8）。本目錄已有 1-discussion／2-decision（＋本檔）＝ in-flight freeze 樣本，不是第一隻活五站白老鼠（6A／Q4／OC-9）。系統不得暗示「寫了 Stage 3 就可以試五站」。

## 九條判定表（RWC 原因；A 的 `檔:行` 仍掛勾選列）

對照 `1-discussion.md` Real-world Context。命中欄全否。勾選列上的 Decision／1-discussion 行號是 A 骨架，本表不改寫那些引用。

| # | 觸發 | 命中 | 對照（Actors／Journey／Workaround／Exception） | 原因（A 引用見上列） |
|---|---|---|---|---|
| 1 | 有新的前端流程 | 否 | Actors 是 owner／coordinator／doctor／寫手／審查者；工具是 git、doctor CLI、graph、看板。無產品畫面 | F3 改的是預設路線與用語。方法論審頁／站檔不是新前端。與 F0 simplify「方法論 UI ≠ 本條」同一刀口 |
| 2 | 改變使用者下一步 | 否 | Journey 步 4：新 slug 寫手現況仍經 `N7-g1` 等人。Decision 3C：cut 後不再例行停 | 「下一步」的**設計**已在 F0–F2 lock，且 simplify Stage 3 已走過舊 7 vs 新 5。F3 只切預設開關讓核准 Pattern 生效。沒有新的「點哪才前進」要試。位元翻轉 ≠ 新互動下一步 |
| 3 | 涉及角色交接 | 否 | Actors 表：owner → 實作 agent → coordinator → 採用 owner → in-flight 執行者 → Ship 審查者 | 交接名單沿用 prior knives。F3 不新增交接畫面或改誰遞給誰。1A 的 who／when／which 是紀錄槽，不是新交接儀式 |
| 4 | 涉及人工核准 | 否 | 鎖：不刪 G1／G2／`ACCEPTED`。Ship 仍唯人。Q15／1A：cut 要可見紀錄 | F3 不新增人批關卡；摺的是新 slug 例行停，不是加核准面。可見紀錄是檔／條件，不是點核准 Demo |
| 5 | 涉及等待/退回/逾時 | 否 | Journey 步 4／6：現況等人；3C observable：新 slug 不等、in-flight 仍停 `N7-g1`／`N6-g2`、Ship 仍等 | 等待語意已是 Decision 約束。本站不設計新的等待／退回／逾時畫面 |
| 6 | 涉及權限差異 | 否 | Exception：未宣告不得遠端改線。F1／F2：Agent 禁寫 `ACCEPTED`／Ship `PASS` | 權限牙已落地。F3 不新增「誰看得到哪一格」的權限畫面 |
| 7 | 涉及系統外動作 | 否 | Journey 步 2–3：marketplace update、doctor `COMPATIBLE`。Workaround：chat 當 hop 開關 | 系統外工具**語意已鎖**（Q9／Q10／4A：綠≠ticket、marketplace≠cut、chat≠判定）。F3 不設計新的系統外交接要人走一遍 |
| 8 | 涉及多種可行互動設計 | 否 | Q21 四選項已在 Decision 選定 3C（兩者都要、節點不刪）。1A 路徑／graph 切換機制 OPEN 交 4-spec | OPEN 的是鍵名、切換機制形、電池檔名——規格落點，不是「操作順序／資訊階層／決策點」的互動分叉。禁湊同流程換字的假 Variant |
| 9 | Stage 1 尚有操作流程不確定性 | 否 | Current Journey 八步已寫現況；Decision 已收 Q15–Q27 | 人怎麼走（cut 後新 slug 五站、本目錄舊 7 到 Ship）已確定。不確定的是實作落點，不是操作流程 |

## Question
引 2-decision **內部技術選擇**「不預先跳過 Stage 3；觸發判定留給該站」(`2-decision.md:L305`)＋ **Risks**「本 hop 被當成已落地 Stage 3／4」(`:L227`)＋ 1-discussion Journey 步 4／7（新 slug 仍經 `N7-g1`；指南仍寫七站單行）(`1-discussion.md:L94`、`:L97`)。

在**不重開 1A–6A、不重做 five-station-simplify D1**的前提下，本站只答這一問：

**THIS knife（F3 cut：契約／guide／graph+dual-read／doctor 誠實）有沒有 Stage 3 互動風險？**

答案長什麼樣才算回答了：
1. 九條各有 YES／NO + 引用 Decision／1-discussion；不得用「方法論所以全中」或「後端所以全空」一句帶過。
2. **0 命中** → Demo verdict = N/A + 原因落檔；**不**發明可點／可跑的互動原型。
3. 反事實寫清：若某條當時被判中，最薄 Demo 會是哪一條、驗證什麼——本站**不執行**。下列反事實 **不是 Demo**（產檔器不得把它們數成 Demo 場）。
4. Human verdict 由人類親裁。本 hop 落 `ACCEPTED` + attestation（owner chat「接受」；scenario=0/9 Demo N/A accepted）。不改 2-decision 正文；不改 STATUS（另伴 PR）。

## Method
- 實驗位置:本檔觸發表（**PROTOTYPE — not production**；紙上對照；不進 throwaway code、不改 `_templates/`／`scripts/`／`graph.yaml`／契約／doctor）
- Demo 形式:**N/A**。0 命中 → 不建可操作 Demo。下節是**非 Demo 反事實紀錄**（若命中才走），不是給人點的模擬器。
- 驗法:逐條對 1-discussion Real-world Context（Actors／Journey／Workarounds／Exceptions）+ Decision 1A–6A／OC-1…OC-12。已核准 Pattern（五站 hop vs 舊 7 等人）不重開。跑 `python3 hooks/_stage3_impl.py five-station-f3`。
- 本 hop **不**回寫 2-decision（只擬記「prototype 回寫」行文；確認紀錄不在本 hop）。不開 Stage 4。

### 反事實：若當時有命中，最薄 Demo 只走該條（非 Demo；不執行）

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

0 命中 → 上表**全部不執行**。沒有 throwaway branch、沒有 CLI Demo、沒有狀態流程模擬器。**在 0 命中硬做可點 Demo = 假 hit，會製造 Human ACCEPTED 欠債**（有 trigger 才要 ACCEPTED+attestation；本刀沒有 trigger）。

## 結構圖
- 對照 RWC／Decision 九條
- 全未勾 → Demo N/A（選定）
- 不建可操作原型；不建 html（N-skip）
- 反事實最薄紙卡（非 Demo；不執行）
- 擬回寫 2-decision（本 hop 不改）

```
RWC + Decision 1A-6A
        |
        v
九條觸發判定
        |
        +-- 0 命中 --> Demo verdict N/A（選定）
        |                 不建可操作 Demo
        |                 不建 3-prototype.html
        |                 Human = ACCEPTED (0/9 N/A)
        +-- 若命中 --> 只走該條最薄紙卡（本站不執行）
```

## Demo Script
0 命中，**本站不帶人走可操作 Demo**。下列標題刻意不用 `### Scenario`，避免產檔器把反事實數成「Demo: 2」。都是**非 Demo** 紀錄。不要問「喜不喜歡」。本 hop 不跑、不產 throwaway。

### 非 Demo（反事實紀錄）：N/A 路徑（本站實際判定，不是可點場）
- 使用者角色:母版 owner／G2 reviewer
- 真實目標:確認本刀九條是否有互動風險；0 命中則 Demo = N/A，不是「忘了做 Stage 3」
- 起始狀態:G1 PASS；2-decision 無「跳過 Stage 3」OC；本目錄已有 `1-discussion.md`／`2-decision.md`（in-flight，出貨仍舊 7）
- 操作步驟:讀上表九條＋引用；數勾選；對照 simplify D1 是否已答「下一步／等人」
- 系統回應:0／9 未勾。機械閘 `_stage3_impl.py` 讀全未勾 → Demo verdict N/A，可過後續 G2 的 Demo 條件（仍須 R/S／DD／Profile；本 hop **不**送 G2）
- 系統外下一步:無 Demo 可做。不要叫 Agent 填 ACCEPTED。不要把 Demo N/A 寫成 Human ACCEPTED，也不要把 Human `NOT_REVIEWED` 改成 N/A 字串
- 觀察問題:有沒有哪一條被「方法論所以全中」誤勾？有沒有把 cut 本身當成新前端？

### 非 Demo（反事實紀錄）：若「人工核准 UI」命中才走
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
| 九條有沒有中？ | 上表 0／9；各條附 Decision／1-discussion 行 | 「方法論所以全中」；把 cut 當新前端；C 的 6／9 |
| Demo 要不要做？ | 0 命中 → **Demo verdict = N/A** + 各條原因 | 為湊 Stage 3 發明可點原型（假 hit → ACCEPTED 欠債） |
| 若命中最薄是什麼？ | Method 反事實表（非 Demo）；只該條紙卡；不重做 simplify D1 | 重開 1A–6A；假 Variant；C 的 D1 四板 |
| Human？ | owner chat「接受」→ `ACCEPTED` + `human:rick @ 2026-09-14`；scenario=0/9 Demo N/A accepted。Demo N/A ≠ Human 寫成 N/A 字串 | Agent 代填 ACCEPTED（無 chat「接受」） |

回寫對象:2-decision 內部技術選擇「觸發判定留給該站」——判定已做、結果＝0 命中 N/A。**本 hop 不改 2-decision 正文。**

`python3 hooks/_stage3_impl.py five-station-f3` 本 hop 實跑（exit 0）。0 命中走 **N/A 支路**（`hooks/_stage3_impl.py` 全未勾即 PASS），**不**走「有命中 + Owner Call 跳過」。`2-decision.md:L305`「不預先跳過 Stage 3」同時含「Stage 3」與「跳過」字樣，會被 `find_owner_call_skip` 掃進 `owner_call` 欄——**那不是 skip-OC 命中**。本檔不靠該句當跳過。本 hop 不改 `_stage3_impl.py`。

機械 JSON 的 `verdict=null` 是 0-hit 短路（未讀 Human 列），**不是**把 Human 寫成 N/A。檔內 Human 列已是 `ACCEPTED` + attestation。`owner_call` 欄掃到 L305 否決句本身——見上；`reason` 仍是 0/9 N/A，不是 `SKIPPED_OWNER_CALL`。

```
stage3(five-station-f3): PASS — 觸發判定 0/9 命中(全未勾清單即 N/A + 明確原因記錄)→ Demo verdict N/A,可過 G2
{
  "schema": "stage3-verdict-v1",
  "slug": "five-station-f3",
  "legacy": false,
  "trigger": false,
  "trigger_hits": [],
  "trigger_source": "3-prototype-checklist",
  "verdict": null,
  "verdict_attestation": null,
  "owner_call": "- 不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。",
  "prototype_status": "draft",
  "g2_demo": "PASS",
  "reason": "觸發判定 0/9 命中(全未勾清單即 N/A + 明確原因記錄)→ Demo verdict N/A,可過 G2"
}
```

- 不選「為了看起來有做 Stage 3 而做最薄假 Demo」。那會把 0 命中做成假 hit，G2 反而要 Human ACCEPTED。
- 本 hop **不**回寫 2-decision。0 命中無實驗答案；Decision 約束不變。

## User Demo Feedback
<!-- owner chat 2026-09-14 Asia/Taipei「接受」= Human ACCEPTED Stage 3 N/A。
     Demo verdict N/A ≠ Human verdict N/A。0 命中＝無 Demo 可點；人裁的是觸發表。
     attestation 按該裁決落檔。不送 G2、不寫 4-spec。 -->
- Demo date: 2026-09-14（owner chat 同日「接受」；0/9 無 Demo 可點）
- Participants: owner rick（chat「接受」= Stage 3 Human ACCEPTED for N/A）
- Variant reviewed: 無（0/9 Demo N/A；不建可操作 Demo、不建 html）
- Accepted interaction: Demo N/A（0/9 無互動風險）
- Rejected interaction: 為湊 Stage 3 發明可點原型（假 hit）
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: ACCEPTED | role=母版 owner | scenario=0/9 Demo N/A accepted
- Verdict attestation: human:rick @ 2026-09-14

## Verdict
- **Demo verdict = N/A**（觸發判定 0／9 + 上表原因）。不是 REVISE。未 Demo ≠ 失敗；本刀無互動風險可點。
- **Human verdict = `ACCEPTED`**（owner chat 2026-09-14 Asia/Taipei「接受」；scenario=0/9 Demo N/A accepted）。attestation `human:rick @ 2026-09-14`。**不是**把 Human 寫成 N/A 字串。
- **擬回寫 2-decision**（本 hop 仍不動該檔；不寫 4-spec）:確認紀錄加一行「prototype 回寫 \| 2026-09-14 \| Stage3-A+standing：九條 0 命中，Demo N/A；N-skip 不建 html；Human ACCEPTED」。內部技術選擇維持「不跳過 Stage 3；觸發判定留給該站」——該站已行使判定。
- 本檔 `status: approved`（N-skip 慣例；人類已裁觸發表）。**不送 G2、不寫 4-spec。** coordinator 下一刀才開 Stage 4 writers。
- 實驗產物:觸發表＋RWC 原因表留在本檔；無 throwaway branch、無正式碼。**不建 `3-prototype.html`**：母版 N-skip／模板零命中「不建 html」。A 原 twin 會讓產檔器把兩段反事實腳本數成「Demo: 2」——假 Demo 計數。無 htmlpreview。
- 本 PR 檔集只准 `3-prototype.md`。不改 STATUS（另伴 PR：Active Stage → `4-spec`，Gates 仍 `G1✅ G2⬜ G3⬜`）。不發明 G2。第 3 站已做判定，未跳過、未做互動實驗。
