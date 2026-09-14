---
feature: five-station-f3
stage: 2-decision
status: draft
verdict:             # 空 | PASS | REQUEST_CHANGES | HOLD(Human 判定;全勾不算 PASS)
owner: rick
reviewers: []        # G1 核准者,不可 = owner
updated: 2026-09-14
---

# 2. 收斂 — 五站 F3（Writer A：cut 證明格／三前置 AND／graph+2.1.0 同動）

> 把 `1-discussion.md` 收成一個選定方案。**G1 未核**：`verdict` 空、`status` draft、OC 全「待人審」。Lane = **full**。本 hop 只落 Decision＋html；不實作 cut、不 bump 契約、不改 `graph.yaml`／doctor／token、不改 STATUS／HISTORY。
> Stage 1 頂欄仍 `status: draft`、當時寫「不送 G1」。Owner 2026-09-14 以「ok」開本站。1-discussion 留當時說法；改口記本檔。本 Stage 2 **不發明** Human G1 PASS。
> A 線主軸：**函式 `True` ≠ cut**。Cut 證明＝專案樹一格人指得到、coordinator 讀得到。三前置維持 F2 4A AND；`2.1.0 ≠ cut`。graph 行為與 2.1.0 宣告必須同動。doctor／marketplace 仍是約束不是票。F3 完＝同一電池 NEW 預設五站 + in-flight OLD7 + token 在 + F2 電池仍綠；hollow 探針各自能紅。
> 本 slug dogfood 舊 7（in-flight）。不是第一隻活五站白老鼠。F2 park D-1／D-2／D-3／F-c-4 不准重開成 In。

## Real-world 去向
| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| 「cut 要寫在哪才算『已發生』」 | 本方案處理 | 1A：專案樹兄弟鍵；函式是讀端 |
| 「只把函式改 True、不留紀錄,不算切完」 | 本方案處理 | 1A 拒 1B；SC-HOLLOW-TRUE |
| 「2.1.0 ≠ cut；第三位元可獨立為假」 | 本方案處理 | 2A 繼承 F2 4A；Q26 不重開 |
| 「live reader 錯鍵回空字串」 | 本方案處理 | 2A：改讀 `devflow_contract_version` |
| 「契約仍 2.0.0 且 hops 已當五站預設 → 仍被看成違規」 | 本方案處理 | 2A＋3C；SLOT-REJECT |
| 「graph 四選項不得默選」 | 本方案處理 | 3C：兩者都要 |
| 「只改 guide／STATUS 用字、graph 仍停 N7-g1 = 用語切、行為沒切」 | 本方案處理 | 3C 拒 3B／3D；SC-GRAPH |
| 「doctor 印 COMPATIBLE／exit 0,不足以當 cut」 | 本方案處理 | 4A；約束不是票 |
| 「bump 到 2.1.0 而 supported 仍只有 2.0.0 → 誠實紅」 | 本方案處理 | 4A／Q18 |
| Journey「新 slug 寫手仍經 N7-g1 等人」 | 本方案處理 | 3C：cut 後新 slug 不再例行停 |
| Journey「coordinator 缺 cut → legacy」 | 本方案處理 | 1A 第三位元怎麼被指認 |
| Workaround「STATUS／HISTORY 當刀口 log；看板列 ≠ cut」 | 本方案處理 | 1A 拒 1C；OC-10 用語走 companion |
| Workaround「owner 用 chat 當 hop 開關」 | 本方案處理 | 1A 拒 chat 當 SoT |
| Exception「不准改已經 freeze 的 slug」 | 本方案處理 | 6A；本目錄整段舊 7 |
| Exception「NEW5 不是本目錄」 | 本方案處理 | 6A／OC-11 |
| Exception「[Assumption] 只切 hops 再 bump」 | 本方案處理 | Q16 升格；3C 同動 |
| Exception「[Assumption] 只 bump 正本鍵、declared 仍假」 | 本方案處理 | Q17 升格；2A 改讀鍵 |
| Exception「[Assumption] 用語切 ≠ 行為切」 | 本方案處理 | Q15／G-graph-1；3C |
| Q15 可見紀錄、禁 silent True | 本方案處理 | 1A |
| Q16 2.1.0 必須與 hops 預設同動或先宣告 | 本方案處理 | 2A＋3C；OC-12 |
| Q17 讀鍵縫 | 本方案處理 | 2A／OC-4 |
| Q18 doctor 誠實紅 | 本方案處理 | 4A |
| Q19 三路電池 | 本方案處理 | 5A |
| Q20 attestation 落點 | 本方案處理 | 1A／OC-1／OC-2 |
| Q21 graph 四選項 | 本方案處理 | 3C |
| Q22 doctor 改實作 vs 只加清單 | 本方案處理 | 4A：只加 `supported` 清單 |
| Q23 guide 用語算哪些檔 | 本方案處理 | OC-10：至少 `guide-dev-flow.html`；檔案地圖列 ≠ cut |
| Q24 STATUS 用語 vs 禁碰正本 | 本方案處理 | OC-10：合併後 companion |
| Q25 第一隻活五站叫什麼 | 本方案處理 | OC-11：本 hop 不發明名字；不是本目錄 |
| Q26 三前置形狀不重開 | 刻意維持 | 2A 繼承；後站不得把 2.1.0 當 cut |
| Q27 reader 回空字串已核 | 本方案處理 | 2A 修讀鍵 |
| 「鎖:不刪閘；不折 freeze；不拿本 slug 當白老鼠」 | 本方案處理 | 6A Non-Goals 鎖死 |
| 「不重開 F2 park D-1／D-2／D-3／F-c-4」 | 本方案處理 | 6A |
| F2 D-1 檔案地圖列 ≠ cut | 刻意維持 | 加列不是第三位元 |
| STATUS Backlog A 過期 | 刻意維持 | 看板 lag ≠ 已切；本 PR 不改 STATUS |

## Approaches Considered

### 決策點 1：cut attestation SoT（Q15／Q20／Q23／Q24／G-attest-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 1A | **專案樹一格＝SoT**。`devflow-contract.json` 兄弟鍵 `f3_cut_happened`（布林；缺席或假＝未切）。`f3_cut_happened()` **讀這格**，不是 `return True`。正本鍵 `devflow_contract_version` 不是這格。chat／STATUS／guide 用字／檔案地圖加列都不是這格。人指得到檔:鍵；git blame＝誰／何時 | 對準 F2 簽名已收 `project_root`、註解「Reading the tree is allowed」；7A 路線認專案樹；marketplace 改不了別人 repo；2.1.0 與 cut 可獨立為假；F2 fixture 無此鍵 → 仍假 → F2 電池不必為了「函式恒假」改口 | 同一檔兩鍵，人會以為 bump 版本＝cut（用 AND＋對照擋）；`dev-setup` 升級要不要順便寫這鍵交 4-spec | 中 | `scripts/five_station_f2.py:L276-L278` 讀樹被允許、F2 不發明 cut；`:L260-L268` 讀的是契約檔；`docs/dev/five-station-f2/2-decision.md:L79` 4A 第三位元；`:L100` 7A 認專案樹；`docs/dev/five-station-f3/1-discussion.md:L205` Q15 `[~]`；`:L210` Q20 `[>]`；`:L52` 錯鍵回 `""`。路徑形鎖定本檔；JSON 其餘欄 `[Assumption]`（4-spec） |
| 1B | **silent flip**：`f3_cut_happened()` 改 `return True`，不留樹格 | 一行；F3 看起來「切了」 | 人指不到誰准、讀哪個條件；F2 D-1 同形（布林／加列 ≠ 出貨證明）；Q15 過期不得當已核 | 低 | `1-discussion.md:L249-L252` AC-4；`:L205` Q15；`docs/dev/five-station-f2/7-review.md:L445` 檔案地圖列 ≠ cut；`scripts/five_station_f2.py:L276-L278` |
| 1C | **chat／STATUS 用語／guide 用字／契約 2.1.0 本身當 attestation** | 看板或 bump 就能宣稱已切 | 看板 ≠ 刀（#359 已開 Active ≠ 已切）；2.1.0 ≠ cut（Q26）；用語切 ≠ 行為切；feature branch 禁碰 STATUS 正本 | 低 | `1-discussion.md:L47` Backlog A stale ≠ 已切；`:L79` 4A；`:L207` Q16；`:L216` Q24；`docs/dev/STATUS.md:L10-L13` 禁碰正本 |

### 決策點 2：三前置關係與讀鍵縫（Q16／Q17／Q26／Q27／G-pre-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 2A | **繼承 F2 4A AND**：宣告 2.1.0 ∧ ¬in-flight ∧ cut 已發生。缺一 → `allow_legacy()`。**2.1.0 ≠ cut**（兩位元獨立）。`contract_version()` **改讀正本鍵** `devflow_contract_version`；**不認** `version`／`contract_version` 當已宣告（錯鍵 bump ≠ declared）。2.1.0 必須與「hops 預設五站」同刀或先宣告 | 擋 SLOT-REJECT；擋「bump 了所以已宣告」；Q26／Q27 不重開形狀只修讀端 | 舊測試若只寫錯鍵會從「看起來像 2.1」變成未宣告——本 tree fixture 沒寫那兩鍵，現況已是 `""` | 低 | `docs/dev/five-station-f2/2-decision.md:L79` 4A；`docs/dev/five-station-f2/4-spec.md:L757-L761` S-7.1；`scripts/five_station_f2.py:L260-L268` 讀錯鍵；`:L286-L293` 三前置 AND；`devflow-contract.json:L1-L2` 正本鍵＝`2.0.0`；`1-discussion.md:L203-L204` Q26／Q27；`:L206-L207` Q16／Q17；`notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24` SLOT-REJECT |
| 2B | **2.1.0 就是 cut**（摺成兩前置） | 少一格 | 翻 Q26；第三位元不能獨立為假；只 bump 版本＝空切 | 低 | `1-discussion.md:L203` Q26 `[x]` 不重開；`docs/dev/five-station-f2/2-decision.md:L79` |
| 2C | **只 bump 正本鍵、不改 reader** | 契約檔看起來 2.1.0 | live `declared` 仍假（讀錯鍵回 `""`）；Q17 具名陷阱 | 低 | `scripts/five_station_f2.py:L260-L268`；`1-discussion.md:L207` Q17 `[~]` |
| 2D | **先切 hops 預設五站，再 bump 2.1.0** | 現場少停比較快 | 2.0.0+五站 hops＝SLOT-REJECT 或遠端改線；Q16 過期擋 | 高 | `notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24`；`1-discussion.md:L206` Q16 |

### 決策點 3：graph vs dual-read（Q21／G-graph-1／G-cut-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 3A | **只改 `graph.yaml` 預設**（新 slug 不再例行進 `N7-g1`／`N6-g2`），不宣告 2.1.0 | 行為看起來切了 | 契約仍 2.0.0 + hops 已五站＝SLOT-REJECT 或遠端改線；採用端未 upgrade 被拖走 | 高 | `notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L24`；`1-discussion.md:L211` Q21 |
| 3B | **只宣告 2.1.0 dual-read**，graph 預設仍進 `N7-g1`／`N6-g2` | 契約／doctor 握手先對 | 新 slug 仍等人；用語／宣告切、行為沒切；G-cut-1 失敗 | 中 | `skills/dev-flow/stage2/graph.yaml:L53-L57`；`skills/dev-flow/stage4/graph.yaml:L93-L98`；`1-discussion.md:L217` Q21 假設；`:L261-L264` AC-7 |
| 3C | **兩者都要**。宣告 2.1.0 dual-read **且** 改各站 `graph.yaml` 預設：cut 後新 slug 不再例行停 `N7-g1`／`N6-g2`。**不刪**這兩節點與 G1／G2 token（in-flight + dual-read 仍走舊路）。guide／STATUS 用語切五站是附加、**不是**本點成功。接線形（條件 next／雙讀 walker）交 4-spec | 唯一同時滿足 G-cut-1 與 SLOT-REJECT；用語與行為分帳 | 動 graph 是 F0 本輪禁令之外的 F3 刀；接線形要後站釘 | 高 | `notes/design/five-station-simplify-brief-v3.md:L180` F3 做＝新 slug 預設五站＋用語；`:L7-L9` 「本輪」不改 graph＝F0 不是 F3 永禁；`docs/dev/five-station-f2/4-spec.md:L963` F2 把 graph 用語捆進 F3；`1-discussion.md:L211` 四選項不得默選。接線形 `[Assumption]`（4-spec） |
| 3D | **只翻 coordinator**（`f3_cut_happened` 讀格為真），留下 `N7-g1`／`N6-g2` 當預設 next | 不動 graph 檔 | 謂詞真仍等人＝G-keep-1 失敗 1；空切；graph 技能仍停 G1 | 中 | `1-discussion.md:L272-L276` AC-10；`notes/design/five-station-simplify-brief-v3.md:L17-L22` 摺的是例行停點 |

### 決策點 4：doctor／marketplace（Q18／Q22／G-honest-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 4A | **約束不是票**。不改 `hooks/_doctor_impl.py` 握手語意（綠＝版本 ∈ `supported`）。F3 若 bump 契約到 2.1.0，**必須同時**把 `2.1.0` 寫進 `hooks/runtime-capabilities.json` 的 `supported_contract_versions`。只 bump 契約、清單仍 `{2.0.0}` → doctor **誠實 INCOMPATIBLE**。綠 ≠ cut、≠ 路條。`marketplace update` 單獨 ≠ cut | 對準 F1 SLOT-DOCTOR-GREEN-MEANS 與 F2 4A 約束句；Q22 選「只動清單」 | bump 漏清單時母版 doctor 會紅——那是誠實，不是 bug | 低 | `hooks/_doctor_impl.py:L193-L202` fail-closed；`:L492-L500` 印 COMPATIBLE；`hooks/runtime-capabilities.json:L1-L4` 現況只 `2.0.0`；`1-discussion.md:L208` Q18；`:L212` Q22；`notes/design/five-station-simplify-f1-dual-read-annex.md:L26-L28` |
| 4B | **改 doctor 實作**，讓未列 2.1.0 仍 COMPATIBLE，或把綠當路條 | 升級當下比較好看 | 綠變謊；SLOT 變裝飾；F2 已拒 4B | 高 | `docs/dev/five-station-f2/2-decision.md:L80` 4B 棄；`scripts/five_station_f2.py:L289-L290` |
| 4C | **F3 不管 doctor 清單**（只 bump 契約） | 少一個檔 | 母版自打誠實紅；人或以為「更新壞了」而把 doctor 改軟＝滑向 4B | 低 | `1-discussion.md:L208` Q18 應 INCOMPATIBLE；不管＝把誠實紅當意外 |

### 決策點 5：F3 完的定義（Q19／Q25／G-success-1／G-keep-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 5A | **同一電池、四路都能獨立紅也能一起綠**：(a) cut 後新 slug 預設五站、不等例行 G1／G2；(b) in-flight 仍舊 7、無五站狀態；(c) G1／G2／`ACCEPTED` token 仍在；(d) `scripts/test-five-station-f2.sh` 仍綠。hollow 探針各自能紅。NEW 試體＝合成 fixture 或 **cut 之後才開** 的新 slug；**不是**本目錄、不是 `five-station-f2`、不是 `five-station-simplify`。第一隻活五站名字本 hop 不發明 | 對準 Q19／AC-9；擋 hollow；F2 綠是地板不是完 | CASE 表後站實作；本 PR 不寫測 | 中 | `1-discussion.md:L161` G-success-1；`:L209` Q19；`:L269-L272` AC-9；`scripts/test-five-station-f2.sh:L1-L11` F2 單一入口。入口檔名 `[Assumption]`（4-spec） |
| 5B | **`f3_cut_happened==True` 或檔在或 guide 寫「五站」= 完** | 最快宣告 | 具名 hollow；Q19 反面 | 低 | `1-discussion.md:L184` 具名 hollow；`:L249-L252` AC-4 |
| 5C | **只重跑 F2 電池綠 = F3 完** | 現成綠 | 地板冒充完工；預設路線可以沒切 | 低 | `1-discussion.md:L55` 本 hop F2 綠 ≠ F3 完；`:L161` |

### 決策點 6：刀口與 Non-Goals 鎖（G-self-1／G-token-1／G-freeze-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 6A | **F3 = Cut**。新 slug 預設五站；舊 7 只服務 freeze + dual-read；guide／STATUS 用語切五站。鎖死不准後站改成 In：(1) 不折 in-flight；(2) 不刪 G1／G2／`ACCEPTED`；(3) 不重開 F2 park D-1／D-2／D-3／F-c-4 當本刀 In；(4) 本 slug 不是 NEW5 白老鼠、整段舊 7 到 Ship；(5) 本 hop 不發明 Human G1 PASS。不炸模板全文 | 對準 brief §7；本目錄自保；F2 G3 已 park 的 L1 不借刀重開 | 採用端／新 slug 痛要等本刀落地（本來就該如此） | 低 | `notes/design/five-station-simplify-brief-v3.md:L180-L182`；`1-discussion.md:L175-L186` Non-Goals 初稿；`:L193` Q4；`docs/dev/HISTORY.md:L721-L725` no F3 opened + park；`docs/dev/five-station-f2/7-review.md:L445-L452` D-1…F-c-4 |
| 6B | **順手折 in-flight 或刪 token**，謂詞比較好寫 | 狀態機短 | X2／X4；新 brief；F2 8C 已拒 | 高 | `notes/design/five-station-simplify-f0-state-machine.md:L193-L196`；`brief-v3.md:L182` |
| 6C | **本 slug 當第一隻活五站**，或把 F2 park 重開成 In | 少開一個目錄／少記一筆 L1 | 本檔已是 `1-discussion.md`＝in-flight；污染觀測；翻 G3 park | 高 | `1-discussion.md:L192` Q4；`:L234` 本資料夾已 in-flight；`docs/dev/five-station-f2/7-review.md:L445` |

## 方案架構圖
```
[1A] 專案樹兄弟鍵證明cut(選定)
[2A] 三前置AND+讀正本鍵(選定)
[3C] graph行為+2.1.0同動(選定)
[4A] doctor誠實約束只加清單(選定)
[5A] 同一電池四路+hollow(選定)
[6A] 不折不刪不重開park(選定)
```

## Decision
採 **1A+2A+3C+4A+5A+6A**：F3 把「cut 已發生」收成專案樹可指的一格——`devflow-contract.json` 兄弟鍵 `f3_cut_happened`（真／假／缺席）。`scripts/five_station_f2.py` 的 `f3_cut_happened()` **讀這格**，禁止改成無紀錄的 `return True`。`devflow_contract_version` 不是這格；chat、STATUS、guide 用字、檔案地圖加列都不是這格。

三前置維持 F2 4A／S-7.1：**宣告 2.1.0 ∧ ¬in-flight ∧ cut**，缺一 `allow_legacy()`。**2.1.0 ≠ cut**。`contract_version()` 改讀正本鍵 `devflow_contract_version`；只 bump `version`／`contract_version` ≠ 已宣告。2.1.0 必須與 hops 預設五站同刀或先宣告；先切 hops 再 bump＝SLOT-REJECT。

graph 四選項選 **兩者都要**：宣告 2.1.0 dual-read，**且**改各站 `graph.yaml` 讓 cut 後新 slug 不再例行停 `N7-g1`／`N6-g2`。不刪這兩節點、不刪 G1／G2／`ACCEPTED` token。只翻 coordinator、只改用字、或只改 graph 不 bump，皆拒。

doctor／marketplace 仍是約束不是票。不改 `_doctor_impl.py` 握手。bump 2.1.0 時同步把 `2.1.0` 列入 `supported_contract_versions`；漏列則誠實紅。綠 ≠ cut。

**F3 完＝同一電池**能證明 (a) cut 後新 slug 預設五站 (b) in-flight 仍舊 7 (c) token 仍在 (d) F2 電池仍綠。hollow（silent True／檔在／只用字／只 F2 綠／錯鍵 bump／2.1.0 無 cut 鍵卻當已切）各自能紅。

本 slug 整段舊 7。不折 in-flight、不刪 token、不重開 F2 park D-1／D-2／D-3／F-c-4、不發明本 hop G1 PASS。不選 1B／1C／2B／2C／2D／3A／3B／3D／4B／4C／5B／5C／6B／6C。

## Decision 約束（後站不准改成可選）
1. **函式 `True` ≠ cut。** 1B 已拒。後站若把 `f3_cut_happened()` 改 `return True` 且不讀 1A 格 → 回本站。
2. **SoT 是專案樹格，不是看板／chat／用字。** STATUS 列、HISTORY 句、guide「五站」、F2 D-1 檔案地圖加列、owner chat「可以」都不是第三位元。
3. **2.1.0 ≠ cut。** 兩鍵獨立。契約 `2.1.0` 而 `f3_cut_happened` 缺席或假 → 仍 `allow_legacy()`，理由含「F3 cut 未發生」。
4. **三前置 AND。** 缺宣告、或 in-flight、或未切 → 舊 7。不准改成兩前置。
5. **讀正本鍵。** `contract_version()` 必須讀 `devflow_contract_version`。只寫 `version`／`contract_version` ≠ 已宣告。Q17 不得再用「bump 了所以 declared」。
6. **2.1.0 與 hops 預設同動或先宣告。** 契約仍 2.0.0 且 hops 已當五站預設 → 紅、不得改線（SLOT-REJECT）。2D 已拒。
7. **graph 行為與 2.1.0 都要。** 3A／3B／3D 已拒。cut 後新 slug 預設不再例行停 `N7-g1`／`N6-g2`；in-flight 仍停。節點與 token **不刪**。只改 guide 用字 ≠ 本約束過關。
8. **doctor 綠 ≠ 路條。** 不改握手語意。清單未列 2.1.0 而契約已 2.1.0 → 誠實紅。marketplace／cache 不是第四前置。
9. **F3 完 ≠ hollow。** `f3_cut_happened==True`、檔在、guide 用字、只 F2 綠，任一被標「F3 綠」→ 必須非 0。
10. **同一電池。** (a)(b)(c)(d) 走同一入口；缺一路即整電池紅。兩支腳本各綠一次 ≠ 完。
11. **NEW 試體不是本目錄。** 也不是 `five-station-f2`、不是 `five-station-simplify`。對本目錄建五站機＝RP-15／X4。
12. **三把刀口鎖 + F2 park。** 不折 in-flight；不刪 G1／G2／`ACCEPTED`；不重開 D-1／D-2／D-3／F-c-4 當 In。把其中一項標可選＝翻 Decision。
13. **本 hop 零 runtime。** 本 PR 只 `2-decision.md`＋`2-decision.html`。不 bump、不改 graph、不改 doctor、不改 STATUS、不填 G1 PASS、不合併。
14. **CASE 極性**：列寫「→ 紅」＝**注入該壞行為**，該格必須獨立變紅。把「coordinator 拒 hop」記成該紅格綠＝極性反了，已拒。

## 本方案要求（F3 電池最小 CASE；4-spec 只准加不准減）
極性：標「→ 紅」的列＝**注入該壞行為**，該格必須獨立變紅。

| CASE | 路 | 紅／綠什麼 |
|---|---|---|
| F3-NEW-DEFAULT | NEW | cut 格真 ∧ 2.1.0 ∧ 無 1–7 `.md` → 預設五站；無例行「請人審 G1／G2」停（綠格） |
| F3-OLD7-FREEZE | OLD7 | 已有 1–7 `.md` → 仍舊 7 到 Ship；無五站狀態寫入（綠格） |
| F3-TOKEN | OLD7 | G1／G2／`ACCEPTED` token 與檔仍在；`check-gate-tokens.sh` 綠（綠格） |
| F3-F2-REGRESS | 地板 | `scripts/test-five-station-f2.sh` 仍 exit 0、`failed=0`（綠格；地板，不是完） |
| F3-SLOT-REJECT | 採用 | 契約仍 2.0.0 且 hops 已被當五站預設 → **該格紅**；不得改線 |
| F3-NO-CUT-KEY | NEW | 契約 2.1.0 但 cut 鍵缺席或假 → 仍 legacy；理由含「F3 cut 未發生」（綠格：合法拒） |
| F3-WRONG-KEY | NEW | **注入**只 bump `version`／`contract_version`、正本鍵仍 2.0.0 或未寫 → 不得當已宣告；若因此放行五站 → **該格紅** |
| F3-HOLLOW-TRUE | hollow | **注入**函式 `return True` 且樹格未真、卻宣稱已切 → **該格紅** |
| F3-HOLLOW-WORD | hollow | **注入**只改 guide／STATUS 用字、graph 仍例行停 `N7-g1`、卻標 F3 成功 → **該格紅** |
| F3-HOLLOW-FILE | hollow | **注入**只證明函式檔在或 `f3_cut_happened==True`（無 1A 格）當完 → **該格紅** |
| F3-HOLLOW-F2 | hollow | **注入**只跑 F2 電池綠、NEW／OLD7／token 未證，卻標 F3 成功 → **該格紅** |
| F3-DOCTOR | 約束 | doctor 印 `COMPATIBLE` 且契約仍 2.0.0 時求五站 hop → 拒；理由是路線，不是「doctor 已綠」（綠格：合法拒） |
| F3-DOCTOR-RED | 約束 | 契約 2.1.0 而 `supported` 仍只有 `2.0.0` → doctor INCOMPATIBLE（綠格：誠實紅） |
| F3-SELF | OLD7 | 對 `docs/dev/five-station-f3/` 求五站自動前進 → 跳不過（綠格：合法拒） |
| F3-GRAPH-WAIT | NEW | **注入**三前置全真，新 slug 仍留下例行 G1／G2 提交判定 → **該格紅** |

減任一列 = 翻本 Decision。4-spec 可加列，不可把「函式真了」加成通過條件。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| 1B silent `return True` | 無人類可見紀錄；Q15 過期不得當已核 cut。 |
| 1C chat／STATUS／guide／2.1.0 當 attestation | 看板 ≠ 刀；2.1.0 ≠ cut；用語 ≠ 行為；STATUS 正本 feature branch 禁碰。 |
| 2B 2.1.0 就是 cut | 翻 Q26；第三位元不能獨立為假。 |
| 2C 只 bump 不改 reader | live `declared` 仍 `""`；Q17 具名縫。 |
| 2D 先切 hops 再 bump | SLOT-REJECT 或遠端改線；Q16 過期擋。 |
| 3A 只改 graph.yaml | 2.0.0+五站 hops 違 annex。 |
| 3B 只宣告 2.1.0 | 新 slug 仍經 `N7-g1`；空切。 |
| 3D 只翻 coordinator 留 N7-g1 | 謂詞真仍等人；G-keep-1 失敗 1。 |
| 4B 改 doctor 握手或綠當路條 | SLOT-DOCTOR-GREEN-MEANS；F2 4B 已拒。 |
| 4C 不管 supported 清單 | 把誠實紅當意外；人會把 doctor 改軟。 |
| 5B 函式真／檔在／用字＝完 | 具名 hollow。 |
| 5C 只 F2 綠＝完 | 地板冒充完工。 |
| 6B 折 in-flight／刪 token | X2／X4；新 brief。 |
| 6C 本 slug 當白老鼠或重開 F2 park | 目錄已 in-flight；翻 G3 park。 |
| 重開 F2 4A 三前置形狀 | Q26 已 `[x]`。 |
| 把 F2 D-1 檔案地圖加列當 cut | F2 G3 已釘 ≠ cut。 |
| 本 PR  bump／改 graph／改 doctor／填 G1 PASS／改 STATUS | 使用者：draft、only 2-decision+html、No G1 PASS。 |

## Rationale
F2 把 cut 做成恒假布林，好測「未切」。F3 若只翻真，tree 裡看不到誰准了、讀哪一格、graph／契約有沒有一起動——跟 D-1「檔案地圖列 ≠ cut」同一形。1A 讓函式變讀端：SoT 是專案樹兄弟鍵，marketplace 改不了別人 repo，F2 fixture 無此鍵仍假，地板不必為了「恒假」改口。

讀鍵縫是另一個空切。正本鍵已是 `devflow_contract_version=2.0.0`，reader 卻讀 `version`／`contract_version` 回 `""`。只 bump 正本鍵，`declared` 仍假。2A 修讀端，並拒絕錯鍵冒充已宣告。2.1.0 仍不是 cut。

Q21 是 C 線主縫。brief「做」列寫 guide／STATUS 用語；現場痛是 graph 預設進 `N7-g1`。四選項各棄一邊都會空切或 SLOT-REJECT。3C 要行為與宣告同動：新 slug 不再例行停，未宣告 2.1.0 的採用端仍舊 7。節點與 token 留下給 freeze。

doctor 綠永遠只握手。F3 動的是 `supported` 清單，不是握手實作。漏清單就紅——誠實，不是失敗。

完成定義沿 F2 反 hollow：同一電池四路，缺一即紅。本目錄已 in-flight，不是白老鼠。

## 既有脈絡
對帳快照（2026-09-14 `origin/main` `ff9b0bc`，Stage1-C + standing soft-fix 已合，STATUS Active 已開 `#359`）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| F0 brief＋狀態機 | Owner 已核；F3 刀＝新 slug 預設五站＋用語；不刪閘 | 本檔只收 F3 落點；不重開十條 |
| F1 | Human G3 PASS；dual-read annex；SLOT 牙 | 回歸地板；SLOT-REJECT／doctor 綠語意沿用 |
| F2 | Human G3 PASS；coordinator 在；`f3_cut_happened` 恒 False；park D-1…F-c-4 | 4A 三前置繼承；park 不准重開；電池是 F3 地板 |
| Stage 1 Winner C | 1-discussion status=draft；OQ 全三態 | 留當時說法；Owner「ok」後本檔改口 |
| 契約／reader | `devflow_contract_version=2.0.0`；reader 讀錯鍵 → `""` | 2A 修讀鍵；1A 另開兄弟鍵 |
| doctor | `supported={2.0.0}`；綠＝握手 | 4A：bump 時加清單；不改實作 |
| graph | Stage2 `N7-g1`；Stage4 `N6-g2` | 3C：cut 後新 slug 不再例行停；節點不刪 |
| guide | 「七站單行，只有 G1／G2／G3 會被人擋」 | 用語切是 In（後站）；≠ attestation |
| 本 slug STATUS | Active 在 1-discussion；Gates 全白 | 本 branch **不**改這列（OC-9） |
| 本資料夾 | 已有 1-discussion.md／.html | 已 in-flight；出貨走舊 7 |
| F3 碼 | 無（cut 未切） | 本 PR 仍無；電池在後站 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 後站把函式改 `return True` | 1B 進 Rejected；約束 1；SC-HOLLOW-TRUE；OC-1 |
| 把 2.1.0 當 cut | 約束 3；F3-NO-CUT-KEY；Q26 不重開 |
| 只 bump 正本鍵、reader 仍讀錯鍵 | 2C 棄；約束 5；OC-4 |
| 先切 hops 再 bump | 2D／3A 棄；約束 6；F3-SLOT-REJECT |
| 只宣告 2.1.0 或只改用字 | 3B 棄；F3-HOLLOW-WORD；F3-GRAPH-WAIT |
| 只翻 coordinator 留 N7-g1 | 3D 棄；約束 7 |
| 改 doctor 讓未支持仍綠 | 4B 棄；約束 8；F3-DOCTOR-RED |
| 只跑 F2 電池或只證明函式真 | 5B／5C 棄；約束 9／10；F3-HOLLOW-* |
| 對本目錄開五站機 | 6A／F3-SELF；NEW 合成或 cut 後新開 |
| 重開 F2 park 當 In | 約束 12；6C 棄 |
| feature branch 手改 STATUS | OC-9 流程層；用語走 companion（OC-10） |
| 本 hop 被當成已過 G1 或已落地 cut | 頂欄 draft／verdict 空；約束 13；不發明 PASS |
| Q15–Q19 假設被當「討論已核、Decision 可改口」 | 本檔升格並進 OC；推翻＝回本站 |
| 4-spec 減 CASE 表 | 「只准加不准減」；減列翻 Decision |
| 同一檔兩鍵被讀成一個 | 約束 3；F3-NO-CUT-KEY 具名 |

## Success Criteria
每條都要能用「具名 CASE 輸出／拒絕理由／檔集」核對。7-review 對這張表，不對口頭「cut 看起來切了」。

- **SC-BATTERY**(G-success-1)：存在**單一入口**跑完整電池。exit 0 **當且僅當** NEW 組、OLD7 組、token 組、F2 回歸組都過。缺一組、跳過一組、或入口只轉呼叫 `scripts/test-five-station-f2.sh` → 非 0。觀測：該入口的原始 stdout／exit。
- **SC-NEW-DEFAULT**(G-cut-1)：F3-NEW-DEFAULT 綠。cut 格真 ∧ 已宣告 2.1.0 ∧ 該 slug 無 1–7 `.md` → 預設五站；中間無例行 G1／G2 提交判定。試體不是本目錄。
- **SC-OLD7-FREEZE**(G-freeze-1)：F3-OLD7-FREEZE 綠。cut 當下已有 1–7 `.md` 的 slug 仍舊 7 到 Ship；無五站狀態寫入。
- **SC-TOKEN**(G-token-1)：F3-TOKEN 綠。`scripts/check-gate-tokens.sh` 仍綠；G1／G2／`ACCEPTED` 檔與 token 仍在。
- **SC-F2-REGRESS**：F3-F2-REGRESS 綠。`scripts/test-five-station-f2.sh` exit 0、`failed=0`。這是地板，單獨綠 ≠ F3 完。
- **SC-SLOT-REJECT**(G-pre-1)：F3-SLOT-REJECT 為預期紅。契約 2.0.0 + hops 當五站預設 → 紅、未改線。
- **SC-NO-CUT-KEY**：F3-NO-CUT-KEY 綠。2.1.0 而無 cut 鍵 → legacy；理由含「F3 cut 未發生」。
- **SC-WRONG-KEY**：F3-WRONG-KEY 為預期紅。只 bump 錯鍵卻放行五站／宣稱已宣告 → 該格紅。
- **SC-HOLLOW-TRUE**(G-attest-1)：F3-HOLLOW-TRUE 為預期紅。silent `return True` 無樹格卻宣稱已切 → 該格紅。
- **SC-HOLLOW-WORD**(G-graph-1)：F3-HOLLOW-WORD 為預期紅。只改用字、graph 仍例行停 `N7-g1` 卻標成功 → 該格紅。
- **SC-HOLLOW-FILE**：F3-HOLLOW-FILE 為預期紅。檔在或函式真（無 1A 格）當完 → 該格紅。
- **SC-HOLLOW-F2**：F3-HOLLOW-F2 為預期紅。只 F2 綠當 F3 完 → 該格紅。
- **SC-DOCTOR**(G-honest-1)：F3-DOCTOR 綠。doctor `COMPATIBLE` + 契約 2.0.0 時拒五站 hop；理由是路線，不是「doctor 已綠」。
- **SC-DOCTOR-RED**(Q18)：F3-DOCTOR-RED 綠。2.1.0 ∉ supported → INCOMPATIBLE。
- **SC-SELF**(G-self-1)：F3-SELF 綠。對本目錄求五站自動前進被拒；目錄仍是舊 7 站檔。
- **SC-GRAPH-WAIT**：F3-GRAPH-WAIT 為預期紅。三前置全真的新 slug 仍例行等人 → 該格紅。
- **SC-KEEP**(G-keep-1)：下列任一被標 F3 成功 → 必須非 0：(1) 謂詞真仍等人；(2) Must-keep 紅仍 hop；(3) 機械綠無人寫 `verdict: PASS` 卻標 Ship Done。沿用 F2 三張注入形，不准用「已經 cut 了」省略。
- **SC-Q-CARRY**(G-carry-1)：本檔 Real-world 去向覆蓋 Q15–Q27。後站不得把 Q20／Q21／Q19 標可選。
- **SC-PR**：本 PR 的 `git diff --name-only origin/main` 只含 `docs/dev/five-station-f3/2-decision.md` 與 `docs/dev/five-station-f3/2-decision.html`。頂欄 `status: draft`、`verdict` 空。無 G1 PASS。無 STATUS／HISTORY／模板／graph／scripts／契約 bump。

## Scope & Non-Goals(定稿)
- **In**：1A 專案樹兄弟鍵 SoT（函式是讀端）；2A 三前置 AND＋讀正本鍵＋2.1.0 ≠ cut；3C graph 行為與 2.1.0 同動（節點不刪）；4A doctor 約束＋只加 supported 清單＋誠實紅；5A 同一電池四路＋具名 CASE（極性＝注入壞行為該格紅）；6A 刀口與 park 鎖。Q15–Q25 全有去向。本 PR 只 Decision＋html。
- **Out（鎖死，後站不准改成 In）**：
  1. **把 in-flight 折成五站**（含本目錄、含 `five-station-f2`、含 `five-station-simplify`、含任何已有 1–7 `.md` 的 slug）。
  2. **刪 G1／G2／`ACCEPTED` token 或檔**；刪 `N7-g1`／`N6-g2` 節點。
  3. **重開 F2 park D-1／D-2／D-3／F-c-4 當本刀 In**。
  4. 拿本 slug 或已 freeze 母軌當第一隻活五站白老鼠。
  5. silent `return True`、chat、STATUS、guide 用字、檔案地圖加列、錯鍵 bump 當 cut。
  6. 把 2.1.0 當 cut；先切 hops 再 bump 2.1.0。
  7. 只改 graph 不宣告、只宣告不改 graph、只翻 coordinator 留例行停。
  8. 改 `_doctor_impl.py` 握手語意，或讓未支持的 2.1.0 仍 COMPATIBLE。
  9. 把「函式真了」「檔在」「只 F2 綠」「只用字」當 F3 完成。
  10. 一次大爆炸改 `_templates/` 全文（brief §7 明文不是 F3）。
  11. 本 PR 實作 cut、bump 契約、改 `graph.yaml`、改 doctor、改 STATUS／HISTORY、填 G1 PASS、合併。
  12. 本 hop 發明第一隻活五站 slug 名，或發明 Human G1 PASS。

## Owner Calls(自判裁決,待人審)

<!-- A 線 OC ledger：使用者只說 Stage1 OK「ok」+ 鎖六件 must-decide。
     落點（哪一格）、讀鍵怎麼修、graph 四選項選 3C、doctor 只加清單、
     CASE 名、STATUS companion、活五站不命名、本 PR 範圍
     都是 owner 自拍。延伸／收窄／升格／流程層逐條標。 -->

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | **cut SoT＝專案樹可讀格，函式是讀端**（1A）。使用者只鎖「可見、不是 silent True／看板／用字」；選「讀樹格」是延伸 | 不選則後站可滑回 1B；Q15 過期擋 G2 | `1-discussion.md:L205` Q15 `[~]`；`:L210` Q20 `[>]`；`five_station_f2.py:L276-L278`。延伸 `[Assumption]` | SC-HOLLOW-TRUE 改觀測點；silent True 回流 | 待人審 |
| OC-2 | **格＝`devflow-contract.json` 兄弟鍵 `f3_cut_happened`**（布林；缺席／假＝未切）。使用者未選路徑；鎖檔:鍵是延伸。正本版本鍵不是這格 | 不鎖則後站可把 cut 寫進 STATUS 或 plugin 函式體，遠端改線或無痕 | `1-discussion.md:L210` Q20；`devflow-contract.json:L1-L2` 正本鍵已佔用。路徑 `[Assumption]` | SoT 漂到 chat／plugin `return True`／版本鍵 | 待人審 |
| OC-3 | **Q26 維持：三前置 AND、2.1.0 ≠ cut**（2A）。使用者討論已 `[x]`；本檔寫進 Decision 是確認不是重開 | 後站若摺成兩前置，只 bump 就算切 | `1-discussion.md:L203` Q26；`five-station-f2/2-decision.md:L79`。確認 | 第三位元不能獨立為假 | 待人審 |
| OC-4 | **Q17 升格：`contract_version()` 改讀 `devflow_contract_version`；錯鍵 ≠ 已宣告**。使用者帶假設「仍假除非改讀鍵」；本檔選定修讀端、拒 2C | 不升格則 bump 正本鍵仍 `declared==""` | `1-discussion.md:L207` Q17；`:L204` Q27；`five_station_f2.py:L260-L268`。升格 | 空字串當「未宣告」被誤讀成「沒 bump」 | 待人審 |
| OC-5 | **Q21 選 3C（graph 行為 + 2.1.0 都要）**。使用者只移交四選項；選兩者是延伸。不刪 `N7-g1`／`N6-g2` 是收窄（摺停點不刪節點） | 3A 踩 SLOT-REJECT；3B／3D 空切 | `1-discussion.md:L211` Q21；`brief-v3.md:L180`；`stage2/graph.yaml:L53-L57`。延伸+收窄 `[Assumption]` | 新 slug 仍等人，或未 upgrade 被遠端改線 | 待人審 |
| OC-6 | **Q18／Q22：doctor 只加 `supported` 清單，不改握手；漏列誠實紅**（4A）。使用者帶假設「應 INCOMPATIBLE」；「只動清單」是延伸 | 改實作會讓綠變路條；不管清單會把誠實紅當意外 | `1-discussion.md:L208` Q18；`:L212` Q22；`_doctor_impl.py:L193-L202`。升格+延伸 | doctor 被改軟，或母版紅被當 bug 修掉 | 待人審 |
| OC-7 | **把 AC-9 收成具名 CASE 表＋同一入口**（上表 15 列，只准加不准減）。使用者要 measurable SC；CASE 名與「預期紅」是延伸。極性＝注入壞行為該格紅 | 不具名則後站可把 hollow 改可選或只跑 F2 | `1-discussion.md:L269-L272` AC-9；`:L209` Q19。延伸 `[Assumption]` | CASE 消失；SC-HOLLOW 對不到 | 待人審 |
| OC-8 | **Non-Goals 鎖死折／刪／重開 park／白老鼠**（6A）。使用者 must-decide #6；把 F2 D-1…F-c-4 寫進 Out 是延伸（討論已禁重開，本檔升格成後站禁 In） | 不鎖則後站可借 F3 重開 F2 L1 或拿本目錄當 NEW | `1-discussion.md:L181`；`five-station-f2/7-review.md:L445-L452`。延伸 | park 被當未修缺陷重開；本目錄變白老鼠 | 待人審 |
| OC-9 | 本 Decision hop **不**跑 `status-update.sh`、不改 HISTORY、不改 1-discussion 頂欄、**不發明 G1 PASS**、不合併、不 bump、不改 graph／doctor。標**流程層** | 母版 STATUS 只在整合分支維護；使用者：draft、No G1 PASS、ONLY 2-decision+html | `docs/dev/STATUS.md:L10-L26`；本 hop brief | PR 帶 STATUS 或自填 PASS | 待人審 |
| OC-10 | **Q23／Q24：guide 用語切至少含 `guides/guide-dev-flow.html` 七站單行句；STATUS 用語切走合併後 companion，本刀不開 STATUS 正本例外。檔案地圖列 ≠ 用語切 ≠ cut**。使用者只移交；落點是延伸 | feature branch 禁碰 STATUS；D-1 已釘加列 ≠ cut | `1-discussion.md:L213-L214` Q23／Q24；`guide-dev-flow.html:L573`；`STATUS.md:L10-L13`；`docs/dev/five-station-f2/7-review.md:L445`。延伸 `[Assumption]` | 本 PR 改 STATUS 互蓋；或把加列當 F3 成功 | 待人審 |
| OC-11 | **Q25：第一隻活五站名字本 hop 不發明**。只鎖「不是本目錄、不是 F1／F2 母軌、不是 `five-station-simplify`」。名字交 cut 之後或 4-spec | 討論禁止本 hop 發明名字；發明＝偷開白老鼠 | `1-discussion.md:L215` Q25；`:L192` Q4。收窄 `[Assumption]` | 本目錄或已 freeze 軌被當 NEW 試體 | 待人審 |
| OC-12 | **Q16 升格：2.1.0 與 hops 預設五站同刀或先宣告**（2A＋3C）。使用者帶假設「必須」；本檔選定、棄 2D／3A | 過期不得把「只切 hops」寫進 Decision | `1-discussion.md:L206` Q16；annex `:L22-L24`。升格 | 採用端 2.0.0 被遠端改線或 SLOT 被關牙 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 本 hop 不 bump `devflow-contract.json`／`runtime-capabilities.json`；不改 `five_station_f2.py`／`graph.yaml`／`_doctor_impl.py`。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口（Owner「ok」）。
- 審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。不產 G1 勾選 twin。不跑 `devflow_gate.py write`。
- 不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。
- 兄弟鍵以外的 JSON 形／`dev-setup` 升級要不要順便寫 cut 鍵，交 4-spec。本檔只鎖「兩鍵獨立、只 bump 版本 ≠ cut」。
- graph 條件 next／雙讀 walker 的接線形交 4-spec。本檔只鎖「新 slug 不再例行停、in-flight 仍停、節點不刪」。
- 單一電池入口的腳本名交 4-spec，本檔只鎖「同一 process、缺一路即非 0」。
- 本 slug 出貨路徑舊 7。對本目錄建五站機 = RP-15。
- F2 電池入口維持 `scripts/test-five-station-f2.sh`；F3 不得把它改成「只跑 F2 就算 F3 完」。
- Backlog A「下一刀 F1」保持 stale 事實，本 PR 不改看板。
- F2 park D-1／D-2／D-3／F-c-4 維持 Owner accepted；本刀不當缺陷重開。

## ADR 晉升檢查
- 難逆轉:否（G3 未過可改 Decision／OC；本 hop 零 runtime；cut 落地前可翻案）
- 反直覺:是（cut 鍵 ≠ 2.1.0；doctor 可誠實紅；本 slug 仍舊 7；graph 節點留下卻不再例行停）
- 真 trade-off:是（樹格 vs silent True；graph+2.1.0 同動 vs 空切或 SLOT-REJECT；companion STATUS vs 本刀例外）
→ 晉升:**否**（難逆轉未中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-14 | Owner Stage1 OK「ok」+ Writer A dispatch：鎖 attestation SoT／三前置 AND＋讀鍵／graph 四選一＋SC／doctor 約束＋誠實紅／measurable SC／Non-Goals（不折、不刪 token、不重開 F2 park、本 slug 非白老鼠、本 hop 不發明 G1）。六點對 1A／2A／3C／4A／5A／6A。
- Stage 1 改口 | 2026-09-14 | 1-discussion 仍 draft、當時寫不送 G1；Owner「ok」後開本站。不回改正本討論。
- 自檢七掃 | 2026-09-14 | ①每案優劣有依據欄。②Goals G-cut／freeze／token／attest／pre／honest／graph／self／success／keep／carry 進 Decision／SC；漏項進 Non-Goals。③`[>]` Q20–Q25 皆本方案處理。④SC 皆具名 CASE／exit／檔集；紅格極性＝注入。⑤Rejected 無空棄因。⑥六決策點由 Writer A brief 確認；OC-1／2／5／7／8／10 延伸、OC-4／6／12 升格、OC-5 兼收窄、OC-3 確認、OC-11 收窄、OC-9 流程層，皆可回溯決策點。⑦既有脈絡是對帳不是外移 schema。圖上 1A／2A／3C／4A／5A／6A 標選定，Rejected 未標選定。
- 本 hop 不送 G1 | 2026-09-14 | Decision hop：`verdict` 空；OC 全「待人審」；不跑 N8 三連動。不發明 Human G1 PASS。
