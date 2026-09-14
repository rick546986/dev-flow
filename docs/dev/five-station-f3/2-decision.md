---
feature: five-station-f3
stage: 2-decision
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 2. 收斂 — 五站 F3（Writer C：獨立 cut 位元／anti-hollow）

> 把 `1-discussion.md` 收成一個選定方案。**本 hop 不送 G1**：`verdict` 空、`status` draft、OC 全「待人審」。不發明 Human G1／G2／G3 PASS。Lane = **full**。本 PR 只落 `2-decision.md` + `2-decision.html`；不改 STATUS／HISTORY、不合併、不 bump 契約、不改 `graph.yaml`／doctor／coordinator。
> Stage 1 頂欄仍 `status: draft`、當時寫「不送 G1」。Owner 2026-09-14 以「ok」開本站。1-discussion 留當時說法；改口記本檔。
> C 線主軸：**函式 `True`／檔在／用字／F2 綠 ≠ F3 完**。F3 完＝同一電池能證明 (a)cut 後新 slug 預設五站、(b)in-flight 仍舊 7、(c)token 仍在；三路都能獨立紅、也能一起綠。繼承 F2 4A **AND**（2.1.0 ∧ ¬in-flight ∧ cut）；**cut 是獨立位元**（2.1.0 ≠ cut；第三位元可單獨為假）。任何 owner 自拍板進 OC ledger。原文只讀 Stage1-C+soft-fix（`origin/main` `ff9b0bc`）。
> Owner 本 hop 必釘：F3 cut 給新 slug；繼承 F2 AND；獨立 cut 位元；禁 hollow；保護 freeze／token；doctor 是約束；SC 含 hollow 失敗格；不發明 G1。

## Real-world 去向
| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| 「F3 該把『之後才開、cut 當下尚無 1–7 `.md`』的 slug 預設改五站」 | 本方案處理 | G-cut-1／6A：新 slug 預設五站 |
| 「只把函式改 `True`、只改 guide 用字、或契約仍 `2.0.0` 就把 hops 當五站預設」 | 本方案處理 | 1A 拒 silent True；3C 拒用語空切；2A 拒 hops-first |
| 「本目錄一有本檔就是 in-flight,拿自己當第一隻活五站 = 污染觀測」 | 本方案處理 | 6A／5A OLD7-SELF；Q4 |
| Journey「新 slug 寫手仍經 `N7-g1` 等人」 | 本方案處理 | 3C：行為切＝不再例行停 |
| Journey「doctor 印 COMPATIBLE…綠只證明握手≠切線」 | 本方案處理 | 4A doctor 約束 |
| Workaround「F2 用恒 `False` 的 `f3_cut_happened` 擋 live 五站」 | 本方案處理 | 1A：改讀可見紀錄，不是 hardcode True |
| Workaround「STATUS／HISTORY 當刀口 log…看板列 ≠ cut」 | 本方案處理 | 1A／OC-9：STATUS ≠ SoT |
| Exception「不准改已經 freeze 的 slug」 | 本方案處理 | 6A；SC-OLD7-FOLD-RED |
| Exception「[Assumption] 只把函式改 True＝空切」 | 本方案處理 | Q15 升格；1B 棄 |
| Exception「[Assumption] 2.0.0+五站 hops＝SLOT-REJECT」 | 本方案處理 | Q16 升格；2C 棄 |
| Exception「[Assumption] 只改 guide＝用語切、行為沒切」 | 本方案處理 | Q21／3C；3B／3D 棄 |
| Exception「[Assumption] NEW5 不是本目錄」 | 本方案處理 | Q25；5A 不發明活 slug 名 |
| 「F2 4A：三前置全要；2.1.0 ≠ cut；第三位元可獨立為假」 | 本方案處理 | Q26 已 `[x]`；不重開形狀 |
| 「live `contract_version()` 讀錯鍵回空字串」 | 本方案處理 | Q27 已核；2A 修讀鍵 |
| Q15 可見紀錄 vs silent True | 本方案處理 | 1A |
| Q16 2.1.0 與 hops 同動 | 本方案處理 | 2A |
| Q17 只 bump 正本鍵 `declared` 仍假 | 本方案處理 | 2A／2B 棄 |
| Q18 bump 後 supported 仍 2.0.0 應誠實紅 | 本方案處理 | 4A |
| Q19 三路電池／hollow | 本方案處理 | 5A |
| Q20 第三位元怎麼被指認 | 本方案處理 | 1A：獨立標記；不是 2.1.0／STATUS／guide |
| Q21 graph 四選項 | 本方案處理 | 3C 兩者都要 |
| Q22 改 doctor 實作 vs 只動清單 | 本方案處理 | 4A：只加 supported，不改握手語意 |
| Q23 guide 用語算哪些檔 | 本方案處理 | OC-11：至少 `guide-dev-flow.html`；≠ cut SoT |
| Q24 STATUS 用語 vs 分支禁令 | 本方案處理 | OC-9 流程層：companion，本 PR 不碰 |
| Q25 第一隻活五站叫什麼 | 本方案處理 | 不發明名字；合成 fixture 或 cut 後才開 |
| Q1–Q14／Q26／Q27 已解 | 刻意維持 | 不重開；去向落 Decision 約束 |
| Q24 Backlog A「下一刀 F1」 | 刻意維持 | 過期看板 ≠ 已切；本 PR 不改 STATUS |
| 「鎖:不刪 G1／G2／`ACCEPTED`；不折 in-flight；不拿本 slug 當白老鼠」 | 本方案處理 | 6A Non-Goals 鎖死 |

## Approaches Considered

### 決策點 1：cut attestation（Q15／Q20／Q23／Q24）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 1A | **獨立、人類可見的 cut 紀錄**。人指得到誰／何時／讀哪個條件。`f3_cut_happened` **讀這份紀錄**，禁止 hardcode `True`。紀錄 **不是** 2.1.0、**不是** STATUS、**不是** guide 用字。鍵名／檔路徑交 4-spec（本檔不鎖） | 對準 G-attest-1／AC-4；第三位元可獨立為假；擋 silent flip | 多一份 SoT；後站要寫讀徑 | 中 | `docs/dev/five-station-f3/1-discussion.md:L156` G-attest-1；`:L205` Q15；`:L210` Q20；`:L249-L252` AC-4。路徑形 `[Assumption]`（4-spec） |
| 1B | **silent flip**：只把 `f3_cut_happened` 改 `return True`，不留可見紀錄 | 一行碼 | 人看不見誰准了、讀哪個條件；與 F2 D-1「加列 ≠ cut」同形；Q15 過期擋 | 低 | `scripts/five_station_f2.py:L276-L278` 恒 False；`docs/dev/five-station-f2/7-review.md:L445` 檔案地圖列 ≠ cut；`1-discussion.md:L205` silent flip 不合法 |
| 1C | **契約 2.1.0 本身當 cut 位元** | 少一個開關 | 違 F2 4A／Q26：2.1.0 ≠ cut；第三位元無法獨立為假；AND 塌成兩條 | 低 | `docs/dev/five-station-f2/2-decision.md:L79` 4A；`1-discussion.md:L203` Q26；`:L225` 三前置形狀不重開 |
| 1D | **STATUS／guide 用字當 attestation SoT** | brief §7 本來要切用語 | 看板 ≠ 刀；feature branch 禁碰 STATUS 正本；F2 D-1 已拒「加列＝cut」 | 低 | `docs/dev/STATUS.md:L10-L13` 分支不碰正本；`1-discussion.md:L211-L214` Q23／Q24；`guides/guide-dev-flow.html:L573` 仍寫七站單行 |

### 決策點 2：2.1.0 讀鍵縫（Q16／Q17／Q27）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 2A | **同刀**：bump 正本鍵 `devflow_contract_version`→`2.1.0`，**並且**修 `contract_version()` 讀正本鍵（或 dual-read `devflow_contract_version`／`version`／`contract_version`）。hops 預設五站只准與此次 bump **同刀或之後**。2.1.0 仍 ≠ cut | 擋「bump 了所以已宣告」空切；擋 2.0.0+五站 hops；獨立 cut 位元仍在 | 本刀後站要動契約＋reader；採用端未 upgrade 仍舊 7 | 中 | `scripts/five_station_f2.py:L260-L268` 讀錯鍵回 `""`；`:L286` `startswith("2.1")`；`devflow-contract.json:L1-L2` 正本鍵；`1-discussion.md:L206-L207` Q16／Q17；`:L204` Q27 |
| 2B | **只 bump 正本鍵，不修 reader** | 看起來已 2.1.0 | live `declared` 仍假（空字串）；新 slug 繼續 legacy＝空切 | 低 | `1-discussion.md:L207` Q17 帶假設「仍假」；`five_station_f2.py:L268` 不讀正本鍵 |
| 2C | **先切 hops 預設五站，稍後再 bump 2.1.0** | 現場立刻少停 | SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS；或關牙後遠端改線 | 高 | `notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24`；`1-discussion.md:L206` Q16 過期擋「只切 hops」 |
| 2D | **假寫 `version`／`contract_version`，正本鍵留 2.0.0** | reader 立刻成真 | 對醫生／採用端說謊；正本仍 2.0.0＋五站 hops＝SLOT-REJECT | 中 | `[Assumption]` 雙寫假鍵＝瞞 declared。`devflow-contract.json:L86` 正本是本檔 |

### 決策點 3：graph vs dual-read（Q21）— C 線主縫
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 3A | **只改各站 `graph.yaml` 預設**（拿掉 `N7-g1`／`N6-g2` 當大家的下一步），不 bump 2.1.0 dual-read | 新 slug 不再例行等人 | 未宣告 2.0.0 也被拖進五站；SLOT-REJECT 或遠端改線；in-flight 若吃新預設＝折 freeze | 高 | `1-discussion.md:L211` Q21 選項一；`f1-dual-read-annex.md:L18-L24` 未宣告＝舊 7；`brief-v3.md:L165` freeze |
| 3B | **只宣告 2.1.0 dual-read**，graph 預設仍進 `N7-g1`／`N6-g2` | 採用端未 upgrade 安全 | 新 slug 仍例行等人；G-cut-1／AC-7 失敗＝用語／契約切、行為沒切 | 中 | `skills/dev-flow/stage2/graph.yaml:L53-L57` 預設 N7-g1；`stage4/graph.yaml:L93-L98` N6-g2；`1-discussion.md:L261-L264` AC-7 |
| 3C | **兩者都要**。①契約 2.1.0 dual-read（未宣告仍舊 7）。②cut 後新 slug 預設 hop **不再例行進入** `N7-g1`／`N6-g2`。③這兩個節點**檔與節點留在 repo**，專供 freeze＋未宣告 2.0.0。禁刪節點、禁炸模板 | 對帳 brief「做」與 F2 Out of Scope「graph 用語」；擋空切與折舊 | 後站要同時動宣告與 hop 路徑；graph.yaml 具體改邊交 4-spec | 中 | `brief-v3.md:L180` F3 做＝新 slug 預設五站＋用語；`docs/dev/five-station-f2/4-spec.md:L963` graph 用語捆進 F3；`brief-v3.md:L167` 舊機械不刪；`1-discussion.md:L211` 不得默選 |
| 3D | **只翻 coordinator／`f3_cut_happened`，留下所有人的預設 `N7-g1`／`N6-g2`** | 不動 graph 檔 | 若新 slug 仍進 N7-g1，G-cut-1 失敗；與 1B 疊加＝空切 | 低 | `1-discussion.md:L170` 四選項之四；`:L261` 指南已改五站但 graph 仍停 G1 ≠ 成功 |

### 決策點 4：doctor 誠實（Q18／Q22／G-honest-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 4A | **約束不是功能**。綠／`COMPATIBLE`／exit 0 **只**證明 `契約版本 ∈ supported`，≠ 切線、≠ cut、不是第四條前置。F3 **同刀**把 `2.1.0` 加進 `supported_contract_versions`。**不改** `_doctor_impl.py` 握手語意。若有人 bump 到 2.1.0 而清單仍 `{2.0.0}` → **誠實 INCOMPATIBLE**（Q18 升格）；本刀不得把這種紅當「更新壞了所以改握手」 | 對準 SLOT-DOCTOR-GREEN-MEANS；F2 已棄「綠當路條」 | 採用端必須跟 supported 一起 upgrade | 低 | `hooks/_doctor_impl.py:L193-L202` 綠＝∈ supported；`:L492-L500` 印 COMPATIBLE；`hooks/runtime-capabilities.json:L1-L4` 現只 2.0.0；`f1-dual-read-annex.md:L26-L28`；`1-discussion.md:L208` Q18；`:L212` Q22 |
| 4B | **改 `_doctor_impl.py`**，讓 2.1.0 未列 supported 仍 COMPATIBLE | 少一次清單維護 | 握手說謊；SLOT 變裝飾；人把綠讀成切線 | 中 | `[Assumption]` 放寬握手＝關牙。F2 Out of Scope「不改 doctor 握手語意」`docs/dev/five-station-f2/4-spec.md:L974` |
| 4C | **bump 2.1.0 但不加 supported**，接受現場 doctor 紅 | Q18 字面誠實 | 人以為「更新壞了」；壓力會滑向 4B | 低 | `1-discussion.md:L208` 應 INCOMPATIBLE＝約束，不是出貨目標態 |
| 4D | **把 doctor 綠寫成 cut 或第四條前置** | 跟「我跑過 doctor」直覺合 | F1／F2 已鎖死的謊；marketplace 可單獨換 hops | 低 | `1-discussion.md:L197-L199` Q9／Q10／Q11 `[x]`；`five_station_f2.py:L289-L290` 丟棄 doctor／marketplace／cache |

### 決策點 5：成功判準與第一隻活五站（Q19／Q25／G-success-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 5A | **同一電池、三路都能獨立紅也能一起綠**。(a)cut 後新 slug 預設五站、不等例行 G1／G2；(b)in-flight OLD7 無五站狀態；(c)G1／G2／`ACCEPTED` token 仍在。具名 hollow 任一被標成功 → 整電池非 0。NEW 試體＝合成 fixture 或 **cut 之後才開** 的 slug。**本檔不發明第一隻活五站名字** | 對準 AC-9／Q19；擋四種 hollow | CASE 表後站實作；本 PR 不寫測 | 中 | `1-discussion.md:L161` G-success-1；`:L209` Q19；`:L215` Q25；`:L269-L272` AC-9。入口檔名 `[Assumption]`（4-spec） |
| 5B | **`f3_cut_happened==True` 或「coordinator／cut 檔在」＝ F3 完** | 最快宣告 | 這就是具名 hollow；AC-4／AC-9 反面 | 低 | `1-discussion.md:L184` hollow 清單；`:L161` 檔在／用字／`True` ≠ 完 |
| 5C | **guide／STATUS 用字切五站＝ F3 完**（或只重跑 F2 電池綠） | 零行為改動 | AC-7 用語 ≠ 行為；F2 綠是地板不是 F3 | 低 | `1-discussion.md:L261-L264` AC-7；`:L149` F2 電池地板 ≠ F3 完；`scripts/test-five-station-f2.sh:L1-L11` |

### 決策點 6：F3 刀範圍與 Non-Goals（G-cut／G-freeze／G-token／G-self／G-keep）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 6A | **F3 = Cut**：新 slug 預設五站；舊 7 只服務 freeze + dual-read；guide／STATUS 用語切五站。繼承 F2 AND。Must-keep／三失敗仍在。本 slug／`five-station-f2`／`five-station-simplify` 整段舊 7。**不刪** G1／G2／`ACCEPTED`。**不折** in-flight。**不炸**模板全文。本 PR 只 Decision＋html | 對準 brief §7；本目錄當 freeze 樣本 | 採用端預設痛要等後站落地 | 低 | `brief-v3.md:L180-L182`；`1-discussion.md:L191-L192` Q3／Q4；`:L195` Q7；`:L200` Q12 Must-keep 仍在 |
| 6B | **本刀順便刪 token／折 in-flight**（謂詞比較好寫） | 狀態機短 | X2／X4；新 brief，不是本切法尾巴 | 高 | `five-station-simplify-f0-state-machine.md:L196` X4；`brief-v3.md:L182` 刪閘＝新 brief |
| 6C | **拿本目錄當第一隻活五站**（狗食自己） | 少造 fixture | 本檔已是 `1-discussion.md`＝in-flight；觀測自污染；RP-15 | 高 | `f1-dual-read-annex.md:L30-L32`；`1-discussion.md:L193` Q4；`:L265-L268` AC-8 |

## 方案架構圖
```
[1A] 獨立可見cut紀錄(選定)
[2A] bump+修讀鍵同刀(選定)
[3C] dual-read+行為切;節點留(選定)
[4A] doctor清單+誠實紅(選定)
[5A] 三路電池;hollow紅(選定)
[6A] 新slug切;freeze/token鎖(選定)
```

## Decision
採 **1A+2A+3C+4A+5A+6A**：F3 做 Cut——cut 當下沒有 1–7 `.md` 的新 slug 預設走五站，中間不等例行 G1／G2 提交判定。舊 7 只服務 freeze + dual-read。guide／STATUS 用語切五站，但**用語不是 cut SoT、也不是成功**。三前置繼承 F2 4A／S-7.1：**宣告 2.1.0 ∧ ¬in-flight ∧ cut 已發生**；缺一條 → `allow_legacy()`。**cut 是獨立位元**：2.1.0 ≠ cut；第三位元可單獨為假。attestation＝獨立、人類可見的紀錄（誰／何時／讀哪個條件）；`f3_cut_happened` 讀這份紀錄，禁止 silent `True`；2.1.0／STATUS／guide 都不是第三位元。2.1.0 讀鍵縫：同刀 bump 正本鍵 **且** 修 reader 讀 `devflow_contract_version`（或 dual-read 三鍵）；hops 預設五站不得早於此次 bump。graph：**兩者都要**——dual-read 已宣告，且新 slug 預設 hop 不再例行進 `N7-g1`／`N6-g2`；這兩節點檔留著給 freeze／未宣告。doctor：綠只握手；同刀把 2.1.0 列入 `supported_contract_versions`；不改握手語意；清單沒跟上＝誠實紅，不是改 doctor 的理由。F3 完＝同一電池 (a)(b)(c) 都能獨立紅、也能一起綠。hollow（`True`／檔在／只 F2 綠／只用字）標成功 → 失敗。不發明第一隻活五站名字。不選 1B／1C／1D／2B／2C／2D／3A／3B／3D／4B／4C／4D／5B／5C／6B／6C。

## Decision 約束（後站不准改成可選）
1. **函式 `True` ≠ cut。** 1B 已拒。後站若把 `f3_cut_happened` hardcode `True`、或不留可見紀錄就宣稱已切 → 回本站。
2. **2.1.0 ≠ cut。** 獨立位元。宣告真且 cut 假 → 仍 `allow_legacy()`，拒絕理由含「F3 cut 未發生」。1C 已拒。
3. **三前置 AND。** 不重開「要不要三條」。doctor 綠／marketplace update／plugin cache **不是**第四條。
4. **讀鍵縫必須修。** 只 bump 正本鍵、reader 仍回 `""` → `declared` 假＝2B，已拒。不得把「檔案寫了 2.1.0」寫成已宣告。
5. **hops 不得先於 2.1.0。** 契約仍 2.0.0 且 hops 已當五站預設 → SLOT-REJECT，不得改線。2C 已拒。
6. **graph 用語 ≠ graph 行為。** 只改 guide／STATUS 用字、新 slug 仍例行停 `N7-g1`／`N6-g2` → 空切。3B／3D 已拒。
7. **不刪 `N7-g1`／`N6-g2` 節點與檔。** 它們服務 freeze + 未宣告 2.0.0。刪節點＝折舊機械＝6B。
8. **doctor 綠 ≠ 路條。** `COMPATIBLE`／exit 0 只證明握手。把綠寫成 cut 或 hop 許可＝4D，已拒。
9. **F3 完 ≠ 檔在／用字／F2 綠／`True`。** 5B／5C 已拒。同一電池缺一路即非 0。
10. **本 slug 出貨路徑舊 7。** 對 `docs/dev/five-station-f3/`（或 f2／simplify）建五站機＝RP-15／X4。
11. **Must-keep 未綠不得 hop。** 三失敗各自可紅，不得用「已經 cut 了」省略。
12. **STATUS 用語走 companion。** 本 PR／本 feature branch 不改 STATUS 正本。看板列 ≠ cut。
13. **guide 用語至少改** `guides/guide-dev-flow.html` 仍寫「七站單行…」那句。F2 D-1：檔案地圖列 ≠ cut。
14. **不發明第一隻活五站名字。** NEW 路＝合成 fixture 或 cut **之後**才開的 slug。
15. **CASE 極性**：列寫「→ 紅」＝測法是**注入該壞行為**，該格必須獨立變紅。把「coordinator 拒 hop」記成該紅格綠＝極性反了，已拒。

## 本方案要求（F3 電池最小 CASE；4-spec 只准加不准減）
極性：標「→ 紅」的列＝**注入該壞行為**，該格必須獨立變紅。

| CASE | 路 | 紅／綠什麼 |
|---|---|---|
| NEW-DEFAULT-FIVE | NEW | cut 後、cut 當下無 1–7 `.md` → 預設五站；不等例行 G1／G2（綠格：合法行為） |
| NEW-WAIT-RED | NEW | **注入** 謂詞真、latch 假，仍留下「要不要繼續／請人審」→ **該格紅** |
| NEW-MK-RED | NEW | **注入** Must-keep 紅仍 hop → **該格紅** |
| NEW-SHIP-MECH | NEW | **注入** 機械全綠、無人寫 `verdict: PASS` 卻標 Done → **該格紅** |
| OLD7-FREEZE | OLD7 | 已有 1–7 `.md` → 仍舊 7 到 Ship；無五站狀態寫入（綠格） |
| OLD7-FOLD-RED | OLD7 | **注入** 對 in-flight 寫五站狀態／五站 hop → **該格紅** |
| OLD7-TOKEN | TOKEN | G1／G2／`ACCEPTED` token 與檔仍在；`check-gate-tokens.sh` 綠（綠格） |
| OLD7-SELF | OLD7 | 對本目錄／`five-station-f2`／`five-station-simplify` 求五站自動前進 → 跳不過（綠格：合法拒） |
| ATTEST-VISIBLE | CUT | 人指得到誰／何時／讀哪個條件（綠格） |
| ATTEST-SILENT-RED | CUT | **注入** 只 `return True`、無可見紀錄卻宣稱已切 → **該格紅** |
| PRE-AND | PRE | 三前置缺一 → `allow_legacy()`（綠格：合法拒） |
| PRE-CUT-INDEPENDENT | PRE | 2.1.0 已宣告、cut 仍假 → 仍 legacy；理由含「cut 未發生」（綠格：獨立位元） |
| PRE-HOPS-20-RED | PRE | **注入** 契約 2.0.0 + hops 已當五站預設 → **該格紅**（SLOT-REJECT） |
| KEY-READER-RED | PRE | **注入** 只 bump 正本鍵、reader 仍回空字串卻當已宣告 → **該格紅** |
| DOCTOR-LIST | DOC | 2.1.0 不在 supported → INCOMPATIBLE（綠格：誠實紅是對的） |
| DOCTOR-NOT-CUT | DOC | 印 `COMPATIBLE` 仍不足當 cut／五站 hop；理由是路線，不是「doctor 已綠」（綠格） |
| HOLLOW-TRUE | HOLLOW | 只證明 `f3_cut_happened==True` 被標 F3 綠 → 整電池非 0 |
| HOLLOW-FILE | HOLLOW | 只證明檔在被標 F3 綠 → 整電池非 0 |
| HOLLOW-F2 | HOLLOW | 只重跑 F2 電池綠被標 F3 綠 → 整電池非 0 |
| HOLLOW-WORDING | HOLLOW | 只改 guide／STATUS 用字被標 F3 綠 → 整電池非 0 |

減任一列 = 翻本 Decision。4-spec 可加列，不可把「檔在／`True`／用字」加成通過條件。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| 1B silent True | 無可見紀錄；Q15 過期不得當已核 cut。 |
| 1C 2.1.0 當 cut | 塌掉獨立位元；違 4A／Q26。 |
| 1D STATUS／guide 當 SoT | 看板／用字 ≠ 刀；D-1 已拒加列＝cut。 |
| 2B 只 bump 不修 reader | live `declared` 仍 `""`。 |
| 2C hops 先於 2.1.0 | SLOT-REJECT 或遠端改線。 |
| 2D 假寫 version 鍵 | 正本仍 2.0.0；對醫生說謊。 |
| 3A 只改 graph、不 dual-read | 未宣告也被拖走；可折 freeze。 |
| 3B 只宣告、graph 仍停 N7-g1 | 用語／契約切、行為沒切。 |
| 3D 只翻函式、大家仍進 N7-g1 | 空切；與 1B 同形。 |
| 4B 改 doctor 握手 | 綠變謊；SLOT 變裝飾。 |
| 4C 出貨態故意 doctor 紅 | 逼現場滑向 4B。 |
| 4D 綠當 cut／第四條 | Q9／Q10／Q11 已否。 |
| 5B True／檔在＝完 | 具名 hollow。 |
| 5C 用字／F2 綠＝完 | AC-7；地板冒充完工。 |
| 6B 刪 token／折 freeze | X2／X4；新 brief。 |
| 6C 本目錄當白老鼠 | 已 in-flight；G-self-1 反面。 |
| 重開 F0 十條或放寬三 cap | 翻＝新 brief。 |
| 重開 F2 4A 形狀或 park D-1／D-2／D-3／F-c-4 | Stage 1 已鎖不重開。 |
| 本 PR 改 STATUS／填 G1 PASS／合併／bump／改 graph／改 doctor | 使用者：only 2-decision+html、No G1、No STATUS。 |

## Rationale
F2 把 coordinator 寫進樹，但把 cut 做成永遠假的布林，好測「未切」。F3 若只翻真，人在 tree 裡看不到誰准了——這跟 D-1「檔案地圖列 ≠ cut」同一形。1A 把第三位元收成**可指出的紀錄**；2.1.0 繼續當宣告位元，兩位元才能 AND。

讀鍵縫是前置主縫。正本鍵已是 `devflow_contract_version`，live reader 卻讀 `version`／`contract_version` 回空字串（Q27 已核）。2B 會讓「我們 bump 了」變成現場仍 legacy。2A 同刀修讀＋bump，hops 不得搶跑（2C＝SLOT-REJECT）。

Q21 是 C 線主縫。brief「做」寫 guide／STATUS 用語；F2 Out of Scope 把 graph 用語捆進 F3；現場痛是新 slug 仍進 `N7-g1`。只選一邊都會空切或折舊。3C 要**宣告與行為**同時真，節點檔留下。

doctor 綠的定義已經是「∈ supported」。F3 若 bump 卻不改清單，誠實紅是對的——但出貨必須把 2.1.0 寫進清單，而不是改握手讓它假綠。

完成定義沿 F2 anti-hollow：同一電池三路。hollow 四格（True／檔在／F2 綠／用字）是預期紅，不是可選散文。

## 既有脈絡
對帳快照（2026-09-14 `origin/main` `ff9b0bc`，Stage1-C+soft-fix 已合）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| F0 brief＋狀態機 | Owner 已核；十條與三 cap 鎖死 | 本檔只收 F3 落點；不重開 |
| F1 | Human G3 PASS；dual-read annex 九 SLOT | 回歸地板；SLOT-REJECT／DOCTOR／IN-FLIGHT 當約束 |
| F2 | Human G3 PASS；coordinator 在；`f3_cut_happened` 恒 False；4A AND | 繼承 AND 與獨立 cut 位元；F2 綠 ≠ F3 完 |
| Stage 1 `#` gold | 1-discussion status=draft；OQ 全三態；soft-fix 在 main | 留當時說法；Owner「ok」後本檔改口 |
| 契約／reader | 正本 `2.0.0`；reader 回 `""` | 2A：bump+修讀；2.1.0 ≠ cut |
| doctor | 綠＝握手；supported 只 2.0.0 | 4A：加清單、不改握手 |
| graph | Stage2→N7-g1；Stage4→N6-g2 | 3C：行為切、節點留 |
| guide | 「七站單行,只有 G1 / G2 / G3 會被人擋」 | 用語 In；≠ 成功 |
| 本 slug STATUS | Active 在 1-discussion；Gates 全白 | 本 branch **不**改這列（OC-9／OC-10） |
| 本資料夾 | 已有 1-discussion.md／.html | 已 in-flight；出貨走舊 7 |
| F3 碼 | 無；cut 未發生 | 本 PR 仍無；電池在後站 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 後站 silent flip `True` 當已切 | 1B 棄；約束 1；ATTEST-SILENT-RED；OC-1 |
| 把 2.1.0 寫成 cut | 約束 2；PRE-CUT-INDEPENDENT；OC-2 |
| 只 bump 正本鍵、不修 reader | 2B 棄；KEY-READER-RED；OC-3 |
| hops 先切、契約仍 2.0.0 | 2C 棄；PRE-HOPS-20-RED |
| 只改 guide／STATUS、graph 仍停 N7-g1 | 3B／3D 棄；約束 6；HOLLOW-WORDING |
| 刪 N7-g1／N6-g2 或折 in-flight | 約束 7；6B 棄；OLD7-FOLD-RED |
| 改 doctor 握手讓 2.1.0 假綠 | 4B 棄；4A 只動清單 |
| 把本目錄當 NEW 白老鼠 | 6C 棄；OLD7-SELF；約束 10 |
| 後站把 hollow 標成功 | SC-HOLLOW；HOLLOW-* 四格；約束 9 |
| feature branch 手改 STATUS | OC-9／OC-10 流程層 |
| 本 hop 被當成已過 G1 | `verdict` 空；不跑 N8 三連動；不發明 PASS |
| 4-spec 減 CASE 表 | 「只准加不准減」；減列翻 Decision |
| Q15–Q19 假設被當「仍待驗可改口」 | 本檔升格並進 OC；推翻＝回本站 |

## Success Criteria
每條都要能用「具名 CASE 輸出／拒絕理由／檔集」核對。7-review 對這張表，不對口頭「cut 看起來切了」。

- **SC-BATTERY**(G-success-1)：存在**單一入口**跑完整電池。exit 0 **當且僅當** NEW 組、OLD7 組、TOKEN 組都過。缺一組、跳過一組、或入口只轉呼叫 `scripts/test-five-station-f2.sh` → 非 0。觀測：該入口的原始 stdout／exit。
- **SC-NEW-DEFAULT-FIVE**：NEW-DEFAULT-FIVE 綠。cut 後新 slug（cut 當下無 1–7 `.md`）預設五站；沒有例行「請人審 A4／A7」。
- **SC-NEW-WAIT-RED**：NEW-WAIT-RED 為預期紅。測法＝**注入**「謂詞真仍等人」。該格必須獨立變紅。
- **SC-NEW-MK-RED**：NEW-MK-RED 為預期紅。注入 Must-keep 紅仍 hop → 該格紅。
- **SC-NEW-SHIP-MECH**：NEW-SHIP-MECH 為預期紅。注入機械綠→Done → 該格紅。
- **SC-OLD7-FREEZE**：OLD7-FREEZE 綠。已有 1–7 `.md` 的 fixture 仍舊 7；無五站狀態。
- **SC-OLD7-FOLD-RED**：OLD7-FOLD-RED 為預期紅。對該 fixture 寫五站狀態 → 紅。
- **SC-OLD7-TOKEN**：OLD7-TOKEN 綠。`scripts/check-gate-tokens.sh` 仍綠；G1／G2／`ACCEPTED` 檔與 token 仍在。
- **SC-OLD7-SELF**：對本目錄／f2／simplify 求五站自動前進 → 被拒。
- **SC-ATTEST-VISIBLE**：人指得到 cut 紀錄的誰／何時／哪個條件。不是 chat 口頭、不是函式回傳值本身。
- **SC-ATTEST-SILENT-RED**：只 `return True` 無紀錄卻宣稱已切 → 紅。
- **SC-PRE-AND**：三前置缺一 → legacy。
- **SC-PRE-CUT-INDEPENDENT**：2.1.0 真、cut 假 → legacy；理由含 cut 未發生。
- **SC-PRE-HOPS-20-RED**：2.0.0+五站 hops → 紅、未改線。
- **SC-KEY-READER-RED**：只 bump 正本鍵、reader 仍空、卻當已宣告 → 紅。
- **SC-DOCTOR-LIST**：2.1.0 ∉ supported → INCOMPATIBLE。
- **SC-DOCTOR-NOT-CUT**：`COMPATIBLE` 時求五站 hop／當 cut → 拒；理由是路線，不是「doctor 已綠」。
- **SC-HOLLOW**：下列任一被標「F3 綠」→ 必須非 0：(a) 僅 `f3_cut_happened==True`；(b) 僅檔在；(c) 僅 F2 電池綠；(d) 僅 guide／STATUS 用字。
- **SC-Q-CARRY**(G-carry-1)：本檔 Real-world 去向覆蓋 Q15–Q25。後站不得把 Q20／Q21／Q22 標可選。
- **SC-PR**：本 PR 的 `git diff --name-only origin/main` 只含 `docs/dev/five-station-f3/2-decision.md` 與 `docs/dev/five-station-f3/2-decision.html`。頂欄 `status: draft`、`verdict` 空。無 G1 PASS。無 STATUS／HISTORY／模板／graph／scripts／契約 bump。

## Scope & Non-Goals(定稿)
- **In**：1A 獨立可見 cut 紀錄（Q15／Q20）；2A bump+修讀鍵、hops 同刀或之後（Q16／Q17）；3C dual-read **且** 新 slug 不再例行停 N7-g1／N6-g2、節點留（Q21）；4A doctor 清單+誠實紅、不改握手（Q18／Q22）；5A 三路電池+hollow 失敗格+不發明活 slug 名（Q19／Q25）；6A F3 刀範圍。Q15–Q25 全有去向。guide 用語（至少 `guide-dev-flow.html`）與 STATUS 用語（companion）屬**本刀後站**，不是本 PR。本 PR 只 Decision＋html。
- **Out（鎖死，後站不准改成 In）**：
  1. **刪 G1／G2／`ACCEPTED` token 或檔**。
  2. **把 in-flight 折成五站**（含本目錄、含 `five-station-f2`、含 `five-station-simplify`、含任何已有 1–7 `.md` 的 slug）。
  3. **拿本 slug 當第一隻活五站白老鼠**。
  4. 一次大爆炸改模板全文（brief §7 明文不是 F3）。
  5. 放寬 hop≤2／Decide≤1／Goal reopen≤1。
  6. 把 2.1.0／STATUS／guide／doctor 綠／marketplace／cache 當 cut 或第四條前置。
  7. silent flip `f3_cut_happened==True` 當已切。
  8. 把「檔在」或「用字」或「只 F2 綠」當 F3 完成。
  9. 重開 F0 十條、F2 4A 形狀、或 park 的 D-1／D-2／D-3／F-c-4。
  10. 本 PR 實作 cut、改 STATUS／HISTORY、填 G1 PASS、合併、改 `_templates/`／`graph.yaml`／doctor／coordinator、bump 契約。
  11. 選定 cut 紀錄的 JSON／檔名鍵（4-spec 才鎖形）。
  12. 發明第一隻活五站 slug 名。

## Owner Calls(自判裁決,待人審)
<!-- C 線 OC ledger：使用者只說 Stage1 OK「ok」+ 鎖 F3 cut／inherit F2 AND／獨立 cut 位元／禁 hollow／保護 freeze／token／doctor 約束／SC 含 hollow 失敗／不發明 G1。
     attestation 落點、讀鍵怎麼修、graph 四選項、doctor 落點、電池 CASE 名、本 PR 範圍
     都是 owner 自拍。延伸／收窄／升格／流程層逐條標。 -->

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | **attestation＝獨立可見紀錄**（1A）。`f3_cut_happened` 讀它。使用者只移交 Q20 五選；選獨立標記、拒 2.1.0／STATUS／guide／silent True 是 owner 延伸 | 不選則後站可滑回 1B／1C／1D | `1-discussion.md:L210` Q20 `[>]`；`:L205` Q15。延伸 `[Assumption]` | 第三位元塌進 2.1.0 或函式 True；獨立位元消失 | 待人審 |
| OC-2 | **Q15 升格：silent True 不合法**。使用者帶假設「必須可見」；本檔選定 1A、棄 1B | 過期不得把函式 True 當已核 cut | `1-discussion.md:L205` 期限=F3 Decision。升格 | AC-4 失效；空切可過 G2 | 待人審 |
| OC-3 | **Q16／Q17 升格＝2A**。同刀 bump 正本鍵＋修 reader；hops 不得先於 bump。使用者兩條都 `[~]`；選 2A 是升格 | 2B／2C 過期擋 G2 | `1-discussion.md:L206-L207`；`five_station_f2.py:L260-L268`。升格 | declared 空切或 SLOT-REJECT | 待人審 |
| OC-4 | **Q21 選 3C（兩者都要）**。使用者只列四選項、未選；選 3C 是延伸。standing：節點檔留下、禁刪 | 3A 折未宣告／freeze；3B／3D 空切 | `1-discussion.md:L211` 不得默選；`brief-v3.md:L167`。延伸 `[Assumption]` | 用語切或遠端改線 | 待人審 |
| OC-5 | **Q18／Q22＝4A**。加 `2.1.0` 進 supported；不改 `_doctor_impl.py` 握手。使用者 Q22 `[>]`；「只動清單」是延伸 | 4B 關牙；4C 逼現場改握手 | `1-discussion.md:L208` Q18；`:L212` Q22。延伸 `[Assumption]` | 綠變路條或出貨故意紅 | 待人審 |
| OC-6 | **Q19 升格＝5A 三路電池＋hollow 失敗格**。使用者帶假設「是」；CASE 名與預期紅是延伸 | 不具名則後站可把 hollow 改成可選 | `1-discussion.md:L209`；`:L269-L272` AC-9。升格＋延伸 `[Assumption]` | HOLLOW-* 消失；檔在＝完 | 待人審 |
| OC-7 | **Q25：不發明第一隻活五站名字**。NEW＝合成 fixture 或 cut 後才開。使用者只禁本目錄／已 freeze 母軌；「不取名」是延伸 | 取名會把未開 slug 寫進 Decision 當已核 | `1-discussion.md:L215`。延伸 `[Assumption]` | 本目錄或虛構 slug 當白老鼠 | 待人審 |
| OC-8 | **Q23：guide 用語至少 `guides/guide-dev-flow.html` L573 那句**；檔案地圖列 ≠ cut。使用者只問「算哪些檔」；「至少這一句、≠ SoT」是延伸 | 不釘檔則用語 In 會漂；釘成 SoT 則變 1D | `1-discussion.md:L213`；`five-station-f2/7-review.md:L445`。延伸 `[Assumption]` | 用語漏改或冒充 cut | 待人審 |
| OC-9 | **Q24：STATUS 用語走整合分支 companion**；本 feature branch 不碰 STATUS 正本。看板 ≠ cut。標**流程層** | 與 STATUS 政策對帳；使用者：No STATUS | `docs/dev/STATUS.md:L10-L13`；`1-discussion.md:L214` | PR 帶 STATUS 與並行 session 互蓋；或看板被當已切 | 待人審 |
| OC-10 | 本 Decision hop **不**跑 `status-update.sh`、不改 HISTORY、不改 1-discussion 頂欄、**不發明 G1 PASS**、不合併、不 bump、不改 graph／doctor／coordinator。標**流程層** | 使用者：draft、No G1、ONLY 2-decision+html | 本 hop brief；`1-discussion.md:L190` Q2 | PR 自填 PASS 或夾帶碼 | 待人審 |
| OC-11 | **獨立 cut 位元寫進 Decision 約束正文**（約束 2＋PRE-CUT-INDEPENDENT）。使用者鎖「inherit F2 AND + independent cut bit」；「具名 CASE」是延伸 | 只寫 OC 會被後站當可選帳 | `1-discussion.md:L203` Q26；本 hop brief。延伸 `[Assumption]` | AND 塌成兩條；2.1.0 被當 cut | 待人審 |
| OC-12 | **本刀後站才落地 cut／bump／graph 行為／doctor 清單**；本 PR 零碼。這是對 6A 的收窄：Decision 選定範圍 ≠ 本 PR 施工 | 使用者鎖「Create ONLY 2-decision+html」 | 本 hop brief。收窄 `[Assumption]` | 本 PR 偷 bump／改 graph＝超 scope | 待人審 |

### 內部技術選擇(下層,告知即可)
- 契約維持 `2.0.0` 直到後站 2A；本 hop 不 bump plugin／`devflow-contract.json`／`supported_contract_versions`。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口（Owner「ok」）。
- 審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。不產 G1 勾選 twin。不跑 `devflow_gate.py write`。
- 不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。
- cut 紀錄的具體路徑／檔名交 4-spec，本檔只鎖「獨立、可指、誰／何時／哪個條件、function 讀它」。
- 單一電池入口的腳本名交 4-spec，本檔只鎖「同一 process、缺一路即非 0」。
- graph.yaml 具體改哪一條邊交 4-spec，本檔只鎖 3C 不變量（行為切＋節點留＋dual-read）。
- reader 修成「只讀正本鍵」或「三鍵 dual-read」交 4-spec，本檔只鎖「讀完能讓 2.1.0 正本鍵讓 `declared` 為真」。
- 舊 7 in-flight 仍走既有 `graph.yaml` 與 T 嘗試上限 4。
- Backlog A「下一刀 F1」保持 stale 事實，本 PR 不改看板。
- 不重開 F2 park D-1／D-2／D-3／F-c-4。

## ADR 晉升檢查
- 難逆轉:否（G3 未過可改 Decision／OC；本 hop 零 runtime；後站才切預設）
- 反直覺:是（F3 切新 slug 卻對本目錄仍舊 7；2.1.0 ≠ cut；doctor 綠不是通行證；函式 True 不是完）
- 真 trade-off:是（獨立紀錄 vs 少一個開關；dual-read+行為切 vs 只改用字；誠實 doctor 紅 vs 假綠）
→ 晉升:**否**（難逆轉未中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-14 | Owner Stage1 OK「ok」+ C-line dispatch：Decide attestation／2.1.0 key seam／graph-dual-read／doctor／success／Non-Goals。六點對 1A／2A／3C／4A／5A／6A。
- Stage 1 改口 | 2026-09-14 | 1-discussion 仍 draft、當時寫不送 G1；Owner「ok」後開本站。不回改正本討論。Gold＝Stage1-C+soft-fix on main（`ff9b0bc`）。
- 獨立原文 | 2026-09-14 | C 線只讀 1-discussion＋brief §6–§7＋狀態機＋F1 annex＋F2 4A／S-7.1／D-1＋模板。不讀並行 A／B Stage 2 稿。
- Q15／Q16／Q17／Q18／Q19 對帳 | 2026-09-14 | 五條 `[~]` 到期收進 Decision（OC-2／3／5／6），不再當「仍待驗可改口」。
- Q20–Q25 對帳 | 2026-09-14 | 六條 `[>]` 本檔選定去向（OC-1／4／5／7／8／9），後站不得假裝 Stage 1 已選。
- 自檢七掃 | 2026-09-14 | ①每案優劣有依據欄（空格標 `[Assumption]`）。②Goals G-cut／freeze／token／attest／pre／honest／graph／self／success／keep／carry 進 Decision／SC；漏項進 Non-Goals。③`[>]` Q20–Q25 皆本方案處理。④SC 皆具名 CASE／exit／檔集；紅格極性＝注入。⑤Rejected 無空棄因。⑥六決策點由 C-line brief 確認；OC-1／4／5／6／7／8／11 延伸、OC-2／3 升格、OC-12 收窄、OC-9／10 流程層，皆可回溯決策點。⑦既有脈絡是對帳不是外移 schema。圖上 1A／2A／3C／4A／5A／6A 標選定，Rejected 未上圖。
- 本 hop 不送 G1 | 2026-09-14 | `verdict` 空；OC 全「待人審」；不跑 N8 三連動；不發明 PASS。
