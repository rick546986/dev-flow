---
feature: five-station-f3
stage: 2-decision
status: approved
verdict: PASS
owner: rick
reviewers: [user]
updated: 2026-09-14
---
- Human verdict note: Human G1 PASS + OC-1…OC-12 Owner PASS @ 2026-09-14 Asia/Taipei。owner chat「可以」。未發明新 OC 答案。

# 2. 收斂 — 五站 F3（Winner B + owner standing soft-fix：cut 證明／讀鍵縫／graph+dual-read／doctor 誠實／成功≠空切）

> 把 `1-discussion.md`（C+soft-fix）收成一個選定方案。G1 已核:`verdict` PASS、`status` approved、OC-1～OC-12 ✅ Owner PASS。Lane = **full**。本 hop 只落 Human G1 attestation + 審頁重生；不寫 cut 碼、不改 `_templates/`／`graph.yaml`／gate token、不 bump 契約、不改 STATUS／HISTORY（STATUS 另 companion）。
> Stage 1 頂欄仍 `status: draft`、當時寫「不送 G1」。Owner 2026-09-14 以「ok」開本站。1-discussion 留當時說法；改口記本檔。本 Stage 2 的 G1 是 human owner rick PASS（2026-09-14 Asia/Taipei owner chat「可以」），**不是** Agent 自裁。
> Writer B 主軸：**F3 = 新 slug 預設五站的 cut**。繼承 F2 完成樹 **與** 4A 三前置形狀。`2.1.0 ≠ cut`。禁 silent `True`。保護 in-flight／token。doctor 綠 ≠ 路條。成功必須可量測，檔在／用字／函式真 ≠ 完。**Non-Goal 鎖：不重開 F2 park D-1／D-2／D-3／F-c-4。** 不重開「要不要三條」。
> 原文獨立於 A／C（B 線當時未讀他稿）。**本檔含 owner standing soft-fix**（#363 全票勝出後吸收，非 B 線當時已讀他稿）。不換 winner。骨架仍 **1A+2A+3C+4A+5A+6A**。cut SoT＝語意槽（誰／何時／哪個條件），路徑 OPEN 交 4-spec——**不**鎖 A 的 `devflow-contract.json` 兄弟布林。F2 綠是地板，不是第四條 IFF 成功路。G1 依 owner chat「可以」落檔；不發明 G2／G3 PASS。不開 Stage 3／4。

## Real-world 去向
| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| 「F3 該把『之後才開、cut 當下尚無 1–7 `.md`』的 slug 預設改五站」 | 本方案處理 | G-cut-1；5A 電池 NEW5 路 |
| 「只把函式改 `True`、只改 guide 用字、或契約仍 `2.0.0` 就把 hops 當五站預設」 | 本方案處理 | 1A 拒 silent True；3C 拒用語冒充；2A 拒只切 hops |
| 「本目錄一有本檔就是 in-flight,拿自己當第一隻活五站 = 污染觀測」 | 本方案處理 | 6A；SELF-OLD7；Q4／Q25 |
| Journey「新 slug 仍經 `N7-g1` 等人;chat 可蓋章」 | 本方案處理 | 3C：新 slug 行為必須離開例行停點 |
| Journey「doctor 綠只證明 `2.0.0 ∈ supported`≠切線」 | 本方案處理 | 4A；doctor ≠ ticket |
| Journey「coordinator 缺 cut → legacy；理由=`F3 cut 未發生`」 | 本方案處理 | 繼承 4A；1A 第三位元要可見紀錄 |
| Workaround「恒 `False` 擋 live 五站；擋的是行為,不是人看得見的 cut 紀錄」 | 本方案處理 | 1A：函式是讀端，不是 SoT |
| Workaround「STATUS／HISTORY 當刀口 log；看板列 ≠ cut」 | 本方案處理 | 1A；Q14／Q24：用語走 companion，不是 SoT |
| Exception「不准改已經 freeze 的 slug」 | 本方案處理 | 6A；OLD7-FOLD-RED |
| Exception「`[Assumption]` 只把函式改 True、不 bump、不改 hops = 空切」 | 本方案處理 | Q15 升格；ATTEST-SILENT-RED |
| Exception「契約仍 2.0.0 卻把 hops 當五站預設 = SLOT-REJECT」 | 本方案處理 | Q16 升格；2A |
| Exception「只改 guide、graph 仍停 `N7-g1` = 用語切、行為沒切」 | 本方案處理 | Q21；3C；GRAPH-WORD-NE |
| Exception「NEW5 不是本目錄、也不是 `five-station-f2`／`five-station-simplify`」 | 本方案處理 | Q25 不發明名字；合成或 cut 後才開 |
| Q15 silent flip 不合法 | 本方案處理 | 1A；升格為 Decision |
| Q16 2.1.0 必須同動或先於 hops 預設 | 本方案處理 | 2A |
| Q17 只 bump 正本鍵、`declared` 仍假 | 本方案處理 | 2A 修讀鍵 |
| Q18 bump 後 supported 未加 → 誠實紅 | 本方案處理 | 4A |
| Q19 同一電池三路、hollow 不算 | 本方案處理 | 5A |
| Q20 第三位元怎麼被指認 | 本方案處理 | 1A：可見紀錄為 SoT |
| Q21 graph 四選項 | 本方案處理 | 3C 兩者都要；四案並排，不默選 |
| Q22 改 doctor 實作還是只加清單 | 本方案處理 | 4A：只加 supported，不改握手語意 |
| Q23 guide 用語算哪些檔 | 本方案處理 | 1A 附帶：至少 `guide-dev-flow.html` 七站單行；≠ SoT |
| Q24 STATUS 用語 vs feature branch 禁碰 | 本方案處理 | 1A：companion 於整合分支；本 PR 不碰 |
| Q25 第一隻活五站叫什麼 | 本方案處理 | 不發明名字；不是本目錄 |
| Q26 三前置形狀、2.1.0 ≠ cut | 本方案處理 | 繼承；不重開 |
| Q27 live reader 回空字串 | 本方案處理 | 已核事實；2A 修縫 |
| 「鎖:不刪 G1／G2／`ACCEPTED`；不把 in-flight 折成五站；不拿本 slug 當白老鼠」 | 本方案處理 | 6A Non-Goals |
| Q1–Q14／Q3 刀定義 | 本方案處理 | 已解；進 Decision／Non-Goals |
| Q14 Backlog A 過期 | 刻意維持 | 看板 lag ≠ 已切；本 PR 不改 STATUS |

## Approaches Considered

### 決策點 1：cut attestation SoT（Q15／Q20／Q23／Q24）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 1A | **人類可見獨立紀錄為 SoT**。語意槽：誰／何時／讀哪個條件。`f3_cut_happened()` **只准當讀端**：讀到合格紀錄才回真。函式本體改 `return True` 且紀錄缺＝空切。2.1.0 ≠ cut。STATUS／guide 用語是 F3 **交付物**不是 SoT。STATUS 用語切走整合分支 companion，本 feature branch 不例外、本 PR 不碰 STATUS。guide 至少改 `guides/guide-dev-flow.html` 七站單行。F2 D-1 檔案地圖列仍 ≠ cut。檔名／鍵名 OPEN（4-spec） | 人指得到；擋 silent True；對齊 G-attest-1／AC-4；看板政策不破 | 多一份紀錄；4-spec 才釘形 | 中 | `docs/dev/five-station-f3/1-discussion.md:L156` G-attest-1；`:L205` Q15；`:L210` Q20；`:L249-L251` AC-4；`:L48` `f3_cut_happened` 恒 False；`scripts/five_station_f2.py:L276-L278`；`docs/dev/five-station-f2/7-review.md:L445` D-1；`docs/dev/STATUS.md:L10-L13` feature branch 禁碰。檔形 `[Assumption]`（4-spec） |
| 1B | **契約 2.1.0 本身 = cut** | 少一個位元 | 違 Q26／F2 4A；第三位元無法獨立為假；bump 了就算切 | 低 | `1-discussion.md:L203` Q26；`docs/dev/five-station-f2/2-decision.md:L79` 4A；`scripts/five_station_f2.py:L286-L293` 三 AND |
| 1C | **STATUS／guide 用語 = cut**（只用字，不含 silent True——silent 見 5B） | 最快宣告 | 看板 ≠ 刀；用字 ≠ 行為；#359 已開 Active 仍 `f3_cut=False` | 低 | `1-discussion.md:L202` Q14；`:L213-L214` Q23／Q24；`docs/dev/HISTORY.md:L721-L725` no F3 opened；`guides/guide-dev-flow.html:L573` 仍七站單行 |

### 決策點 2：key／read 縫（Q16／Q17／Q27）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 2A | **同刀或先宣告 + 修讀鍵**。正本鍵 `devflow_contract_version` bump 到 2.1.0 時，`contract_version()` **只讀** `devflow_contract_version`。**禁止** fallback／dual-read `version`／`contract_version`。錯鍵 bump ≠ 已宣告。`supported_contract_versions` **同刀**加 `2.1.0`。hops 預設五站 **不得早於** 2.1.0 已宣告（同刀或先宣告）。**2.1.0 仍 ≠ cut**；缺 cut 位元 → `allow_legacy()` | 擋「bump 了所以已宣告」；擋 SLOT-REJECT；繼承 4A；錯鍵不能冒充 declared | 本 hop 不 bump；後站要動 reader／契約／supported | 中 | `1-discussion.md:L204` Q27 空字串已核；`:L206-L207` Q16／Q17；`scripts/five_station_f2.py:L260-L268` 不讀正本鍵；`devflow-contract.json:L1-L2` 正本鍵=`devflow_contract_version`=`2.0.0`；`notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24` SLOT-REJECT。standing 收 A：只讀正本、錯鍵 ≠ declared |
| 2B | **雙寫兩鍵、不修讀端**（正本 2.1.0 同時寫 `version`） | 現況 reader 立刻看見 | 正本與影子鍵永久分叉；只 bump 正本的人仍空字串；把 bug 當契約 | 中 | `five_station_f2.py:L260-L268`。雙寫當正本 `[Assumption]` 會掩蓋讀縫 |
| 2C | **只 bump 正本鍵，或只切 hops 留 2.0.0** | 看起來「已升級」或「已五站」 | 只 bump → `declared` 仍假（Q17）；只切 hops → SLOT-REJECT 或關牙後遠端改線（Q16） | 低 | `1-discussion.md:L206-L207`；annex `:L18-L24` |

### 決策點 3：graph vs dual-read（Q21；四選項不默選）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 3A | **只改各站 `graph.yaml` 預設**（拿掉新 slug 例行進 `N7-g1`／`N6-g2`），不宣告 2.1.0 dual-read | 現場新 slug 不再等人 | 未宣告採用端被遠端改線；2.0.0+五站 hops＝SLOT-REJECT；in-flight 若共用同一預設會被折 | 高 | `notes/design/five-station-simplify-brief-v3.md:L168` 不得遠端改線；annex `:L18-L24`；`brief-v3.md:L165` freeze |
| 3B | **只宣告 2.1.0 dual-read**，graph 預設仍進 `N7-g1`／`N6-g2` | 採用端路線有契約閘 | 新 slug 仍例行等人；用語／契約切、行為沒切（G-graph-1 反面） | 中 | `1-discussion.md:L159` G-graph-1；`:L211` Q21；`skills/dev-flow/stage2/graph.yaml:L53-L57`；`skills/dev-flow/stage4/graph.yaml:L93-L98` |
| 3C | **兩者都要**。dual-read：未宣告 2.1.0＝舊 7。graph **行為**：cut 後、非 in-flight 的新 slug 預設路 **不再例行進** `N7-g1`／`N6-g2`。graph **節點不刪**（服務 freeze + dual-read；token／牙仍在）。切換機制（條件邊／雙 graph／coordinator 跳過）OPEN，4-spec 釘；observable 本檔鎖死。guide／STATUS 用語必要但不充分 | 對齊 G-cut-1 與 brief §6；擋空切與遠端改線；不刪舊機械 | 後站要同時動契約宣告與 hop 預設；機制未鎖 | 高 | `brief-v3.md:L164-L168` 四條連讀；`:L180` F3 做＝新 slug 預設五站 + 用語；`:L167` 舊機械不刪；`docs/dev/five-station-f2/4-spec.md:L963` F2 把 graph 用語捆進 F3；`1-discussion.md:L231` 不得默選。機制 `[Assumption]`（4-spec） |
| 3D | **只翻 coordinator**（`f3_cut_happened` 變可真），留下 `N7-g1`／`N6-g2` 當新 slug 預設路 | 碼短 | 新 slug 仍等人、chat 仍蓋章＝空切；把 F2 恒 False 翻成真卻不改 hop 預設 | 低 | `1-discussion.md:L94` Journey 步 4；`:L117` 用語切行為沒切；`:L48` 函式恒 False |

### 決策點 4：doctor 誠實（Q18／Q22）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 4A | **不改 `hooks/_doctor_impl.py` 握手語意**。契約 bump 到 2.1.0 時，**只**把 `2.1.0` 寫進 `supported_contract_versions`（與 runtime-capabilities 清單）。漏加 → doctor **誠實 INCOMPATIBLE**（Q18）。`COMPATIBLE`／exit 0 **只證明握手**，≠ cut、≠ 路條、≠ 第四條前置。marketplace／cache 同樣不是 ticket | 繼承 F1 SLOT-DOCTOR-GREEN-MEANS 與 F2 約束；擋「綠所以可 hop」 | bump 當下若漏清單，現場會看見紅——那是誠實，不是切失敗 | 低 | `1-discussion.md:L158` G-honest-1；`:L208` Q18；`:L212` Q22；`hooks/_doctor_impl.py:L193-L202` 版本必須 ∈ supported；`:L492-L500` 綠印 COMPATIBLE；annex `:L26-L28`；`five_station_f2.py:L289-L290` doctor 被丟棄；`docs/dev/five-station-f2/4-spec.md:L974` F2 Out #12 不改握手 |
| 4B | **改 doctor：綠＝路線 OK／已切** | 操作者少記一條 | 這就是 SLOT-DOCTOR-GREEN-MEANS；F1 文案牙變裝飾；doctor ≠ ticket | 中 | `1-discussion.md:L198-L199` Q9／Q10；F1 annex `:L26-L28` |
| 4C | **bump 時放寬握手**（2.1.0 ∉ supported 仍 COMPATIBLE）以免現場紅 | 升級當下不紅 | 隱瞞 supported 沒跟上；綠被讀成切線；Q18 反面 | 中 | `1-discussion.md:L208` 應 INCOMPATIBLE；`_doctor_impl.py:L193-L202` fail-closed |

### 決策點 5：成功／hollow（Q19／Q25／G-success-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 5A | **同一電池、三路都能獨立紅也能一起綠**。(a) cut 後新 slug（合成 fixture 或 **cut 之後才開** 的 slug）預設五站、不等例行 G1／G2；(b) in-flight OLD7 仍舊 7、無五站狀態；(c) token 仍在。缺一路、跳過一路、只證明函式 `True`／檔在／F2 綠／guide 用字 → 整電池非 0。**不發明**第一隻活五站名字（Q25）。本目錄／`five-station-f2`／`five-station-simplify` 不是試體。具名 CASE 見下表；極性＝注入壞行為該格紅 | 對齊 AC-9／Q19；擋三種具名 hollow | CASE 表後站才跑；本 PR 不寫測 | 中 | `1-discussion.md:L161` G-success-1；`:L209` Q19；`:L215` Q25；`:L269-L272` AC-9；`scripts/test-five-station-f2.sh:L1-L11` F2 綠是地板。入口檔名 `[Assumption]`（4-spec） |
| 5B | **`f3_cut_happened==True` = F3 完** | 最快宣告 | 無可見紀錄、無三路、無行為；AC-4／hollow | 低 | `1-discussion.md:L184` 具名 hollow；`:L249-L251` AC-4 |
| 5C | **檔在／只 F2 電池綠／只改 guide 用字 = F3 完** | 現成綠 | F2 已證檔在≠完；D-1 檔案地圖≠cut；用字≠行為 | 低 | `1-discussion.md:L161`；`:L184`；F2 4-spec `:L826-L830`；7-review `:L445` |

### 決策點 6：Non-Goals 鎖（G-freeze／G-token／G-self／G-keep）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 6A | **三把鎖 + 繼承鎖寫進 Non-Goals、後站不准改成可選**：(1) 不刪 G1／G2／`ACCEPTED` token 與檔；(2) 不折 in-flight（含本目錄、F2、simplify、任何已有 1–7 `.md`）；(3) 不拿本 slug 當活五站白老鼠。**另鎖（抬高）：不重開 F2 park D-1／D-2／D-3／F-c-4。** 再鎖：不 silent True；2.1.0 ≠ cut；doctor／marketplace／cache ≠ ticket；不炸模板全文；不重開 F0 十條／三 cap／4A 形狀；本 PR 只 Decision＋html | 對齊 brief §7 不做列；本目錄當 freeze 樣本；F2 G3 park 不借刀重開 | 採用端預設痛在 cut 落地前仍在（本來就該如此） | 低 | `brief-v3.md:L180-L182`；`1-discussion.md:L175-L186` Non-Goals 初稿；`:L196-L201` Q7／Q12／Q13；`docs/dev/five-station-f2/7-review.md:L445-L452` D-1…F-c-4 |
| 6B | **本刀順便刪閘或折 in-flight**（謂詞比較好寫） | 狀態機短 | X2／X4；新 brief；dual-read 失去錨 | 高 | `notes/design/five-station-simplify-f0-state-machine.md:L196` X4；`brief-v3.md:L182` 刪閘＝新 brief |
| 6C | **本刀一次大爆炸改模板全文** | 看起來「真的五站了」 | brief §7 明文不做；Backlog B 仍凍 Stage 1–4 模板；偷做另刀 | 高 | `brief-v3.md:L180`；`1-discussion.md:L201` Q13；`docs/dev/STATUS.md:L50` Backlog B |

## 方案架構圖
```
[1A] 可見紀錄為cut SoT;函式只讀(選定)
[2A] 只讀正本鍵;2.1.0同刀或先於hops;≠cut(選定)
[3C] graph行為+dual-read;節點不刪(選定)
[4A] doctor只加清單;綠≠ticket(選定)
[5A] 同一電池三路可獨立紅(選定)
[6A] 不刪閘/不折/不白老鼠/不重開F2 park(選定)
```

## Decision
採 **1A+2A+3C+4A+5A+6A**：F3 做 **Cut**——cut 當下沒有 1–7 `.md` 的新 slug 預設五站；舊 7 只服務 freeze + dual-read；guide／STATUS 用語切五站。**cut attestation SoT＝人類可見獨立紀錄的語意槽**（誰／何時／哪個條件）。鍵名／檔路徑 **OPEN**，交 4-spec 釘——**不是** A 線把 `f3_cut_happened` 布林跟 `devflow_contract_version` 放同一份 JSON。`f3_cut_happened()` 是讀端不是 SoT；silent `return True` 不算切；git blame 不是 who／when。2.1.0 宣告 ≠ cut；三前置形狀繼承 F2 4A／S-7.1（宣告 2.1.0 ∧ ¬in-flight ∧ cut），缺一 → `allow_legacy()`。讀鍵縫必須修：`contract_version()` **只讀**正本鍵 `devflow_contract_version`；禁止 fallback／dual-read 錯鍵；只 bump `version`／`contract_version` ≠ 已宣告。hops 預設五站不得早於 2.1.0 已宣告。graph **與** dual-read **都要**：未宣告採用端仍舊 7；cut 後新 slug 不再例行進 `N7-g1`／`N6-g2`；這兩節點 **不刪**。doctor 不改握手語意，只加 `supported` 清單；漏加則誠實 INCOMPATIBLE；綠 ≠ ticket。F3 完＝同一電池 (a)(b)(c) 都能獨立紅、也能一起綠。F2 綠是地板，不是第四條 IFF 成功路。不選 1B／1C／2B／2C／3A／3B／3D／4B／4C／5B／5C／6B／6C。

## Decision 約束（後站不准改成可選）
1. **silent `True` ≠ cut。** 5B 已拒（與 1C 用語分列）。後站若把「`f3_cut_happened` 回真」寫成完成條件 → 回本站。
2. **2.1.0 ≠ cut。** 第三位元可獨立為假。把 bump 寫成 cut＝翻 Q26／4A。
3. **可見紀錄為 SoT，函式只讀。** 語意槽（誰／何時／哪個條件）人指得到。鍵名／檔名 OPEN（4-spec）。**禁止**把 cut 鎖成 `devflow-contract.json` 裡跟版本同檔的兄弟布林；**禁止**用 git blame 冒充 who／when。
4. **STATUS／guide 用語 ≠ SoT、≠ 成功充分條件。** STATUS 用語切走整合分支 companion；本 PR、本 feature branch 不碰 STATUS。guide 至少含 `guides/guide-dev-flow.html` 七站單行。F2 D-1 檔案地圖列 ≠ cut。
5. **讀鍵縫。** 本 tree `contract_version()` 讀 `version`／`contract_version`、不讀 `devflow_contract_version`、回 `""`＝已核。F3 落地：`contract_version()` **只讀** `devflow_contract_version`；禁止 fallback／dual-read 錯鍵。只 bump `version`／`contract_version` ≠ 已宣告。正本鍵 2.1.0 → `declared` 真。
6. **hops 預設五站不得早於 2.1.0 已宣告**（同刀或先宣告）。2.0.0 + 五站 hops 預設＝SLOT-REJECT，不得改線。
7. **Q21＝兩者都要，不默選。** 只改 graph、只宣告 dual-read、只翻 coordinator 留下例行停點＝已拒。節點 `N7-g1`／`N6-g2` 不刪。
8. **doctor ≠ ticket。** 不改 `_doctor_impl.py` 握手語意。綠只握手。marketplace／cache 不是第四條前置。
9. **誠實紅。** 契約 2.1.0 且 `supported` 仍只有 `2.0.0` → INCOMPATIBLE。把放寬握手當升級成功＝4C，已拒。
10. **檔在／F2 綠／用字 ≠ F3 完。** 5B／5C 已拒。
11. **同一電池。** (a) cut 後新 slug 預設五站 (b) OLD7 freeze (c) token 在。缺一路即整電池紅。兩支互不認識的腳本各綠一次 ≠ 同一電池。
12. **NEW5 試體**＝合成 fixture 或 cut **之後**才開的 slug。不是本目錄、不是 `five-station-f2`、不是 `five-station-simplify`。不發明活五站名字。
13. **本 slug 出貨路徑舊 7。** 對本目錄建五站機＝X4／RP-15。
14. **Must-keep／三失敗仍在。** 摺的是停點不是完整度。三種失敗各自可紅，不得用「已經 cut 了」省略。
15. **三把 Non-Goals 鎖**：不刪 token；不折 in-flight；不白老鼠。**另鎖（抬高）：不重開 F2 park D-1／D-2／D-3／F-c-4。** 把其中一把標可選＝翻 Decision。
16. **CASE 極性**：列寫「→ 紅」＝測法是**注入該壞行為**，該格必須獨立變紅。把「coordinator 拒 hop／拒寫」記成該紅格綠＝極性反了，已拒。綠格才是合法行為應發生。
17. **本 PR 範圍。** 只 `2-decision.md` + `2-decision.html`。`status: draft`。`verdict` 空。不發明 G1／G2／G3 PASS。不改 STATUS／HISTORY／模板／graph／doctor／契約／coordinator。

## 本方案要求（F3 電池最小 CASE；4-spec 只准加不准減）
極性：標「→ 紅」的列＝**注入該壞行為**，該格必須獨立變紅。不准把「拒 hop」記成紅格綠。

| CASE | 路 | 紅／綠什麼 |
|---|---|---|
| NEW5-CUT-OK | NEW5 | cut 後、cut 當下無 1–7 `.md` → 預設五站；不等例行 G1／G2 提交判定（綠格：合法行為） |
| NEW5-WAIT-RED | NEW5 | **注入** 謂詞真、latch 假，卻仍例行停 `N7-g1`／留下「要不要繼續／請人審」（→ 紅） |
| OLD7-FREEZE | OLD7 | 已有 1–7 `.md` → 整段舊 7；無五站狀態寫入；三 cap 不套（綠格） |
| OLD7-FOLD-RED | OLD7 | **注入** 對 in-flight 寫五站狀態／五站 hop（→ 紅） |
| TOKEN-KEEP | TOKEN | G1／G2／`ACCEPTED` token 與檔仍在；`scripts/check-gate-tokens.sh` 綠（綠格） |
| TOKEN-DEL-RED | TOKEN | **注入** 刪 G1／G2／`ACCEPTED` token 或檔卻標 F3 成功（→ 紅） |
| ATTEST-VISIBLE | ATTEST | 人指得到誰／何時／讀哪個條件（綠格） |
| ATTEST-SILENT-RED | ATTEST | **注入** 只把 `f3_cut_happened` 改 `return True`、無可見紀錄，卻宣稱已切（→ 紅） |
| PRE-210-NE-CUT | PRE | 2.1.0 已宣告、cut 位元假 → `allow_legacy()`；理由含「F3 cut 未發生」（綠格：合法拒） |
| PRE-AND | PRE | 三前置缺一 → `allow_legacy()`（綠格：合法拒；standing 加列，不減原 20） |
| PRE-HOPS-200 | PRE | 契約仍 `2.0.0`、hops 已被當五站預設 → SLOT-REJECT、不得改線（綠格：合法拒） |
| READ-SEAM | PRE | **注入** 只 bump 正本鍵、reader 仍不讀它，卻宣稱「已宣告 2.1.0」（→ 紅） |
| DOCTOR-HONEST | DOC | 契約 2.1.0 且 `supported` 仍 `{2.0.0}` → INCOMPATIBLE（綠格：誠實紅） |
| DOCTOR-NE-TICKET | DOC | doctor 印 `COMPATIBLE`、契約仍 `2.0.0`、求五站 hop → 拒；理由是路線，**不是**「doctor 已綠」（綠格） |
| GRAPH-WORD-NE | GRAPH | **注入** 只改 guide／STATUS 用字、新 slug 仍例行停 `N7-g1`，卻標 F3 成功（→ 紅） |
| SELF-OLD7 | SELF | 對本目錄／`five-station-f2`／`five-station-simplify` 求五站自動前進 → 跳不過（綠格：合法拒） |
| HOLLOW-TRUE | HOLLOW | **注入** 把 `f3_cut_happened==True` 標成 F3 綠（→ 紅） |
| HOLLOW-FILES | HOLLOW | **注入** 把「檔在」標成 F3 綠（→ 紅） |
| HOLLOW-F2 | HOLLOW | **注入** 只跑 `test-five-station-f2.sh` 綠就標 F3 綠（→ 紅） |
| F3-F2-REGRESS | 地板 | `scripts/test-five-station-f2.sh` 仍 exit 0、`failed=0`（綠格：**地板**，不是完，不是 SC-BATTERY 第四條 IFF） |
| KEEP-MK-RED | KEEP | **注入** Must-keep 紅仍 hop（→ 紅） |
| KEEP-SHIP-MECH | KEEP | **注入** 機械全綠、無人寫 `verdict: PASS` 卻標 Ship Done（→ 紅） |

原 20 列（極性＝注入壞行為該格紅；合法拒＝綠）減任一列 = 翻本 Decision。standing 只准加：PRE-AND（合法拒綠）、F3-F2-REGRESS（地板綠）。4-spec 可再加列，不可把「函式真／檔在／F2 綠／用字」加成通過條件，也不可把 F2 綠寫進 SC-BATTERY 的 IFF 第四路。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| 1B 2.1.0 本身 = cut | 違 4A／Q26；第三位元無法獨立為假。 |
| 1C 用語／STATUS／guide = cut | 看板 ≠ 刀；用字 ≠ 行為；#359 已開 Active 仍未切。 |
| silent True = cut | 函式真無紀錄 = AC-4。與用語棄因分列，不得併成一格。 |
| 2B 雙寫兩鍵、不修讀端 | 把讀縫當契約；只 bump 正本仍空字串。 |
| 2C 只 bump 正本或只切 hops | Q17 假宣告，或 SLOT-REJECT／遠端改線。 |
| 3A 只改 graph.yaml | 未宣告採用端被改線；in-flight 共預設會被折。 |
| 3B 只宣告 2.1.0 dual-read | 新 slug 仍停 `N7-g1`＝空切。 |
| 3D 只翻 coordinator、留例行停點 | 現場痛（等人、chat 蓋章）還在。 |
| 4B 綠＝路條 | SLOT-DOCTOR-GREEN-MEANS；doctor ≠ ticket。 |
| 4C 放寬握手以免紅 | 隱瞞 supported 沒跟上；Q18 反面。 |
| 出貨態故意 doctor 紅 | 誠實紅是約束，不是出貨目標；故意出貨紅會逼現場滑向 4B。 |
| 5B 函式真＝完 | hollow；無三路。 |
| 5C 檔在／F2 綠／用字＝完 | F2 已拒檔在＝完；D-1；G-graph-1。 |
| 6B 刪閘或折 in-flight | X4；新 brief。 |
| 6C 炸模板全文 | brief §7 不做；另刀。 |
| 重開 F0 十條或放寬三 cap | 翻＝新 brief。 |
| 重開 F2 park D-1／D-2／D-3／F-c-4 或 4A 形狀 | Stage 1 已 `[x]`；重開＝新刀。 |
| 拿本 slug 當第一隻活五站 | 目錄已 in-flight；G-self-1 反面。 |
| 發明活五站 slug 名 | Q25 移交「不發明」；本檔遵守。 |
| 本 PR 寫碼／改 STATUS／填 G1 PASS | 使用者：draft、only 2-decision+html、No G1 invent。 |

## Rationale
F2 把 coordinator 落地，卻把 `f3_cut_happened` 釘死為假——這是測「未切」的地板，不是 F3 已經發生。#359 開了看板 G1⬜，HISTORY 仍寫 no F3 opened。所以現場痛（新 slug 經 `N7-g1` 等人、chat 蓋章、doctor 綠當沒事）還在。

F3 的第一個假綠不是「少寫散文」，是 **silent True**：函式翻成真，tree 裡沒有誰／何時／讀哪個條件。1B 用 2.1.0 冒充 cut，會讓 4A 第三位元永遠不能獨立為假。1C 用看板或指南冒充 cut——本 tree 已經示範過：Active 開了、指南仍寫七站單行、函式仍 False。1A 把 SoT 收成可見紀錄，函式降成讀端。

第二個假綠是讀鍵縫。正本鍵是 `devflow_contract_version`；F2 reader 讀另外兩個鍵，本 tree 回空字串＝已核。只 bump 正本會讓人以為「已宣告 2.1.0」，live 仍 legacy。standing 收 A：`contract_version()` **只讀**正本鍵，禁止 fallback／dual-read 錯鍵；錯鍵 bump ≠ declared。2A 逼同刀修讀端，並鎖 hops 預設不得早於宣告——否則不是 cut，是 SLOT-REJECT 或遠端改線。2.1.0 仍不是 cut。不收 A 的同檔兄弟布林 SoT（cut 跟版本放同一 JSON 會誘發 bump＝cut）。

Q21 是 C 線主縫。brief「做」列寫 guide／STATUS 用語；F2 Out of Scope 把 graph 用語捆進 F3；現場等人是因為 graph 預設進 `N7-g1`／`N6-g2`。四選項任一默選都會偷做或空切。3C 要 **行為 + 宣告** 同時真，且舊節點不刪——摺的是新 slug 的例行停點，不是刪閘、不是折舊 slug。

doctor 綠的定義已經寫在握手：契約版本 ∈ supported。F3 若為了升級好看去改這句，綠就變成 ticket。4A 只加清單；漏加就誠實紅。

成功定義沿 F2 反 hollow：同一電池三路（NEW／OLD7／token）。函式真、檔在、只 F2 綠、只改用字，任一被標 F3 綠 → 該格必須紅（不收 C 的「整電池紅」空心，要 per-cell）。F2 綠是地板（可選 CASE `F3-F2-REGRESS`），不是 SC-BATTERY 第四條 IFF。

## 既有脈絡
對帳快照（2026-09-14 `origin/main` `ff9b0bc`，Stage1-C 討論 + standing soft-fix 已合，STATUS Active 已開 `#359`）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| F0 brief＋狀態機 | Owner 已核；十條與三 cap 鎖死 | 本檔只收 F3 cut 落點；不重開 |
| F1 | Human G3 PASS；SLOT 釘 2.1.0／doctor／in-flight | 回歸地板；SLOT-REJECT／DOCTOR-GREEN 仍咬 |
| F2 | coordinator G3 PASS；`f3_cut_happened` 恒 False；4A 三前置 | 繼承形狀與完成樹；F2 綠 ≠ F3 完 |
| Stage 1 | 1-discussion status=draft；OQ 全三態；C+soft-fix | 留當時說法；Owner「ok」後本檔改口 |
| 契約／reader | 正本鍵 `2.0.0`；reader 回 `""` | 2A 修縫；本 hop 不 bump |
| doctor | 綠＝握手；supported=`{2.0.0}` | 4A：綠 ≠ 切線；漏清單誠實紅 |
| graph／指南 | `N7-g1`／`N6-g2`；七站單行 | 3C：行為要切；節點不刪；用字不充分 |
| 本 slug STATUS | Active 在 1-discussion；Gates 全白 | 本 branch **不**改這列（OC-10） |
| 本資料夾 | 已有 1-discussion.md／.html | 已 in-flight；出貨走舊 7 |
| F3 碼 | 無（cut 未發生） | 本 PR 仍無 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 後站把函式 `True` 寫成 F3 完 | 1C／5B 棄；約束 1；ATTEST-SILENT-RED；HOLLOW-TRUE |
| 把 2.1.0 當 cut | 約束 2；PRE-210-NE-CUT；OC-4 |
| 只 bump 正本、不修 reader | 約束 5；READ-SEAM；2C 棄 |
| hops 先切、契約仍 2.0.0 | 約束 6；PRE-HOPS-200；2C 棄 |
| 只改 guide／STATUS 用字 | 約束 4；GRAPH-WORD-NE；3B 棄 |
| 只改 graph、未宣告 2.1.0 | 3A 棄；遠端改線／SLOT-REJECT |
| 只翻 coordinator、新 slug 仍停 N7-g1 | 3D 棄；NEW5-WAIT-RED |
| 刪 `N7-g1`／`N6-g2` 或刪 token | 約束 7／15；TOKEN-DEL-RED；6B 棄 |
| 改 doctor 握手或放寬綠 | 4B／4C 棄；約束 8／9 |
| 拿本目錄當活五站 | 約束 12／13；SELF-OLD7 |
| 只跑 F2 電池或「檔在」當 F3 完 | HOLLOW-F2／HOLLOW-FILES；約束 10／11 |
| feature branch 手改 STATUS | OC-10 流程層；Q24 companion |
| 本 hop 被當成已過 G1 或已落地 Stage 3／4 | G1 已按 owner chat「可以」落檔（`verdict` PASS、`status` approved、OC-1～OC-12 ✅）；本 PR 只含本目錄 2-decision.md／.html；翻案回本站。不發明 G2／G3。不開 Stage 3／4 |
| Q15–Q19 假設被當「討論已核、Decision 可改口」 | 本檔升格並進 OC；推翻＝回本站 |
| 4-spec 減 CASE 表 | 「只准加不准減」；減列翻 Decision |
| 發明活五站 slug 名 | 約束 12；Q25 |

## Success Criteria
每條都要能用「具名 CASE 輸出／拒絕理由／檔集」核對。7-review 對這張表，不對口頭「cut 看起來有了」。

- **SC-BATTERY**(G-success-1)：存在**單一入口**跑完整電池。exit 0 **當且僅當** NEW5 組、OLD7 組、TOKEN 組都過。缺一組、跳過一組、或入口只轉呼叫 `scripts/test-five-station-f2.sh` → 非 0。**F2 綠不是第四條 IFF。** 觀測：該入口的原始 stdout／exit。
- **SC-F2-REGRESS**：F3-F2-REGRESS 綠。`scripts/test-five-station-f2.sh` exit 0、`failed=0`。這是地板；單獨綠 ≠ F3 完，也不得寫進 SC-BATTERY 的 IFF。
- **SC-NEW5-CUT-OK**：NEW5-CUT-OK 綠。cut 後新 slug（cut 當下無 1–7 `.md`）預設五站；沒有例行「請人審」G1／G2 停。
- **SC-NEW5-WAIT-RED**：NEW5-WAIT-RED 為預期紅。測法＝**注入**「謂詞真仍例行停 `N7-g1`／要不要繼續」。該格獨立紅。
- **SC-OLD7-FREEZE**：OLD7-FREEZE 綠。已有 1–7 `.md` 的 fixture 無五站狀態；仍走舊 7。
- **SC-OLD7-FOLD-RED**：OLD7-FOLD-RED 為預期紅。對該 fixture 寫五站狀態或五站 hop → 紅。
- **SC-TOKEN-KEEP**：TOKEN-KEEP 綠。`scripts/check-gate-tokens.sh` 仍綠；G1／G2／`ACCEPTED` 檔與 token 仍在。
- **SC-TOKEN-DEL-RED**：TOKEN-DEL-RED 為預期紅。注入刪 token 卻標 F3 成功 → 紅。
- **SC-ATTEST-VISIBLE**：ATTEST-VISIBLE 綠。人指得到誰／何時／讀哪個條件。不是 chat 口頭、不是函式回傳值本身。
- **SC-ATTEST-SILENT-RED**：ATTEST-SILENT-RED 為預期紅。注入 silent `True` 無可見紀錄卻宣稱已切 → 紅。
- **SC-PRE-210-NE-CUT**：PRE-210-NE-CUT 綠。2.1.0 已宣告、cut 假 → `allow_legacy()`；理由含「F3 cut 未發生」，不是「已宣告所以切了」。
- **SC-PRE-AND**：PRE-AND 綠。三前置缺一 → `allow_legacy()`（合法拒）。
- **SC-PRE-HOPS-200**：PRE-HOPS-200 綠。2.0.0 + 五站 hops 預設 → 違規、未改線（F1 SLOT-REJECT 回歸）。
- **SC-READ-SEAM**：READ-SEAM 為預期紅。注入「只 bump 正本、reader 仍舊、卻稱已宣告」→ 紅。落地後：正本鍵 2.1.0 → `contract_version()` 以 `2.1` 開頭。
- **SC-DOCTOR-HONEST**：DOCTOR-HONEST 綠（誠實紅）。2.1.0 ∉ supported → INCOMPATIBLE。
- **SC-DOCTOR-NE-TICKET**：DOCTOR-NE-TICKET 綠。`COMPATIBLE` + 2.0.0 求五站 hop → 拒；理由是路線，不含「doctor 已綠」。
- **SC-GRAPH-WORD-NE**：GRAPH-WORD-NE 為預期紅。只改用字、新 slug 仍停 `N7-g1`、卻標 F3 成功 → 紅。
- **SC-SELF-OLD7**：對本目錄／`five-station-f2`／`five-station-simplify` 求五站自動前進 → 被拒；仍是舊 7 站檔。
- **SC-HOLLOW**：下列任一被標「F3 綠」→ 必須非 0／必須被拒：(a) 僅 `f3_cut_happened==True`；(b) 僅檔在；(c) 僅 `test-five-station-f2.sh` 綠；(d) 僅 guide／STATUS 用字。
- **SC-KEEP**(G-keep-1)：KEEP-MK-RED／KEEP-SHIP-MECH 為預期紅。三失敗不得因「已經 cut 了」變綠。謂詞真仍等人＝NEW5-WAIT-RED。
- **SC-Q-CARRY**(G-carry-1)：本檔 Real-world 去向覆蓋 Q15–Q27。後站不得把 Q15／Q16／Q17／Q19／Q21 標可選。
- **SC-PR**：本 PR 的 `git diff --name-only origin/main` 只含 `docs/dev/five-station-f3/2-decision.md` 與 `docs/dev/five-station-f3/2-decision.html`。頂欄 `status: draft`、`verdict` 空。無 G1 PASS。無 STATUS／HISTORY／模板／graph／doctor／契約／coordinator。

## Scope & Non-Goals(定稿)
- **In**：1A 可見紀錄為 cut SoT（語意槽 who／when／which condition；函式只讀；路徑 OPEN 交 4-spec；用語／2.1.0／看板 ≠ SoT）；2A `contract_version()` **只讀** `devflow_contract_version` + 2.1.0 同刀或先於 hops 預設（仍 ≠ cut）；3C graph 行為 + dual-read、節點不刪；4A doctor 只加清單、綠 ≠ ticket、誠實紅；5A 同一電池三路與具名 CASE（極性＝注入壞行為該格紅）；6A Non-Goals 鎖。Q15–Q27 全有去向。本 PR 只 Decision＋html。
- **Out（鎖死，後站不准改成 In）**：
  1. **不重開 F2 park D-1／D-2／D-3／F-c-4。** 後站不得改成 In。
  2. **刪 G1／G2／`ACCEPTED` token 或檔**。
  3. **把 in-flight 折成五站**（含本目錄、含 `five-station-f2`、含 `five-station-simplify`、含任何已有 1–7 `.md` 的 slug）。
  4. **拿本 slug 當活五站白老鼠**；發明第一隻活五站名字。
  5. **silent `True` 當 cut**；把 `f3_cut_happened==True` 當 F3 完。
  6. **2.1.0 當 cut**；重開 4A 三前置形狀。
  7. **doctor 綠／marketplace update／plugin cache 當 cut 或路條**；出貨態故意 doctor 紅當目標。
  8. **只改 guide／STATUS 用字當 F3 完**；本 PR／本 feature branch 改 STATUS 正本表列。
  9. **只改 graph、不宣告 2.1.0**；**只宣告 dual-read、新 slug 仍停 `N7-g1`**；**只翻 coordinator 留例行停點**。
  10. **刪 `N7-g1`／`N6-g2` 節點**；一次大爆炸改模板全文。
  11. 放寬 hop≤2／Decide≤1／Goal reopen≤1；重開 F0 十條。
  12. 把「檔在」或「F2 綠」當 F3 完成；把 F2 綠寫成 SC-BATTERY 第四條 IFF。
  13. 本 PR 實作 cut／改 `graph.yaml`／bump 契約／改 doctor／改 coordinator、填 G1 PASS。
  14. 選定 attestation 的 JSON 鍵名或檔名（4-spec）；把 cut 鎖成與版本同檔的兄弟布林。
  15. 改已經 freeze 的 slug 的路線。
  16. fallback／dual-read 錯鍵當 `contract_version()` 正讀；錯鍵 bump 當已宣告。

## Owner Calls(自判裁決,已核)

<!-- Writer B OC ledger：使用者只說 Stage1 OK「ok」+ 鎖 inherit F2／前置、2.1.0≠cut、
     禁 silent True、保護 in-flight／token、doctor≠ticket、measurable SC、no G1 invent。
     SoT 落點、讀鍵修法、graph 四選項選定、doctor 清單、CASE 名、本 PR 範圍
     都是 owner 自拍。延伸／收窄／升格／流程層逐條標。 -->

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | **cut SoT＝人類可見獨立紀錄；`f3_cut_happened()` 只讀不寫判定**（1A）。使用者只移交 Q20「怎麼被指認」；選「獨立紀錄＋讀端」是 owner 延伸 | 不選則後站可滑回 silent True 或 2.1.0＝cut | `1-discussion.md:L210` Q20；`:L205` Q15；`five_station_f2.py:L276-L278`。延伸 `[Assumption]` | AC-4 失效；函式真冒充已切 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-2 | **guide／STATUS 用語是 F3 交付物，不是 SoT**。STATUS 用語切走整合分支 companion，本 feature branch 不例外。guide 至少 `guides/guide-dev-flow.html` 七站單行。F2 D-1 檔案地圖列 ≠ cut。使用者只問 Q23／Q24 算哪些檔／誰寫看板；「用語≠SoT + companion」是延伸 | 看板政策禁 feature branch 碰 STATUS；#359 已證明看板開 ≠ 刀切 | `1-discussion.md:L213-L214`；`docs/dev/STATUS.md:L10-L13`；7-review `:L445`。延伸 `[Assumption]` | 本 PR 改 STATUS 互蓋；或用字被當成 cut | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-3 | **讀端只讀正本鍵 `devflow_contract_version`**。禁止 fallback／dual-read `version`／`contract_version`。錯鍵 bump ≠ 已宣告。使用者只帶 Q17「仍假」；「只讀正本、殺 fallback」是 standing 收 A 後的延伸 | 不修則 bump 正本仍 `""`；fallback 會讓錯鍵冒充 declared | `1-discussion.md:L204` Q27；`:L207` Q17；`five_station_f2.py:L260-L268`。standing 收 A。延伸 `[Assumption]` | READ-SEAM 無法紅；假宣告 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-4 | **Q16 升格：hops 預設五站不得早於 2.1.0 已宣告**（同刀或先）。使用者在討論標 `[~]`；本檔升格 | 過期不得把「只切 hops」當已核 | `1-discussion.md:L206`；annex `:L22-L24`。升格 | SLOT-REJECT 變可選；遠端改線 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-5 | **Q21 選定 3C（兩者都要）；節點不刪；切換機制交 4-spec**。使用者只要求四選項對帳、不得默選；選 3C 是本站收斂。機制 OPEN 是收窄（不鎖實作形） | 3A 遠端改線；3B／3D 空切；刪節點＝刪舊機械 | `1-discussion.md:L211`；`brief-v3.md:L167`；`:L180`。選定＋收窄 `[Assumption]` | 新 slug 仍等人，或 in-flight 被折，或 token 被刪 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-6 | **Q22＝不改 `_doctor_impl.py` 握手語意，只加 `supported` 清單**（4A）。使用者只移交落點；「不改實作」是延伸（繼承 F2 Out #12） | 改握手會讓綠變 ticket | `1-discussion.md:L212`；F2 4-spec `:L974`。延伸 `[Assumption]` | doctor 綠被讀成切線 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-7 | **Q18 升格：2.1.0 ∉ supported → 誠實 INCOMPATIBLE**。使用者帶假設「應紅」 | 不升格則 4C 可假裝升級成功 | `1-discussion.md:L208`；`_doctor_impl.py:L193-L202`。升格 | 放寬握手；綠掩蓋漏清單 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-8 | **把 AC-9 收成具名 CASE 表＋同一入口**（原 20 列只准加不准減；standing 加 PRE-AND、F3-F2-REGRESS）。使用者要 measurable SC；CASE 名與「預期紅」格子是延伸。極性：注入壞行為 → **該格**紅（不收 C 的整電池空心）。F3-F2-REGRESS 是地板綠，不是 SC-BATTERY 第四路 | 不具名則後站可把紅格改可選或拆兩支腳本 | `1-discussion.md:L269-L272` AC-9。延伸 `[Assumption]` | CASE 消失；SC-HOLLOW 對不到 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-9 | **Q25 不發明第一隻活五站名字**。試體＝合成 fixture 或 cut 之後才開的 slug。這是對「要有活五站證明」的收窄 | 本討論明文不發明；本目錄已 in-flight | `1-discussion.md:L215` Q25；`:L118`。收窄 `[Assumption]` | 本目錄被當白老鼠 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-10 | 本 Decision 檔 **不**跑 `status-update.sh`、不改 HISTORY、不改 1-discussion 頂欄、**不發明 G1 PASS**、不寫 cut 碼。STATUS Stage→`2-decision`、Gates 仍 G1⬜ 走合併後 companion。標**流程層** | 母版 STATUS 只在整合分支維護；使用者：draft、No G1 invent、ONLY 2-decision+html；standing 合稿後另 companion | `docs/dev/STATUS.md:L10-L26`；本 hop brief | PR 帶 STATUS 或自填 PASS，與並行 session 互蓋 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-11 | **Q15 升格：silent flip 不合法＝Decision 正文**（不得只寫在 OC）。使用者帶假設「必須可見」 | 只寫 OC 會被後站當可選帳 | `1-discussion.md:L205`；`:L229` 過期擋 G2。升格 | 函式 True 被當已核 cut | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-12 | **Q19 升格：同一電池三路缺一即紅**；`f3_cut_happened==True`／檔在／只 F2 綠都不算。使用者帶假設「是」 | 不升格則 5B／5C 可假裝完 | `1-discussion.md:L209`；`:L161` G-success-1。升格 | hollow 當完 | ✅ Owner PASS human:rick @ 2026-09-14 |

### 內部技術選擇(下層,告知即可)
- 本 hop 不 bump `devflow-contract.json`／`runtime-capabilities.json`／`agent-event`。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口（Owner「ok」）。
- 審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。G1 經 `scripts/devflow_gate.py write` 落頂欄；審頁重生。不產 G1 勾選 twin。
- 不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。
- 原文獨立收斂（Writer B）；standing soft-fix 才讀 A／C 吸收：A＝`contract_version()` 只讀正本鍵＋「F3 cut 未發生」拒因＋可選 F3-F2-REGRESS 地板；C＝Rejected 拆 silent True／用語＋可選「出貨態故意 doctor 紅」＋可選 PRE-AND。不採 A 的同檔兄弟布林 SoT／blame-as-who-when；不採 A 的四路 IFF；不採 C 的整電池空心。
- attestation 檔路徑／鍵名交 4-spec，本檔只鎖語意槽「誰／何時／哪個條件、函式只讀」。不鎖 `devflow-contract.json` 兄弟鍵。
- graph 切換機制交 4-spec，本檔只鎖 observable：新 slug 不再例行停；in-flight 仍停；節點不刪。
- 單一電池入口的腳本名交 4-spec，本檔只鎖「同一 process、缺一路即非 0」。
- 舊 7 in-flight 仍走既有 `graph.yaml` 與 T 嘗試上限 4。
- F2 電池可留作回歸地板（F3-F2-REGRESS）；不得替代 F3 三路電池，不得寫進 SC-BATTERY IFF。
- Backlog A「下一刀 F1」保持 stale 事實，本 PR 不改看板。
- **不重開 F2 park D-1／D-2／D-3／F-c-4**（Non-Goal 抬高句；後站不准改成 In）。

## ADR 晉升檢查
- 難逆轉:否（G3 未過可改 Decision／OC；本 hop 零 runtime；cut 落地前路線未變）
- 反直覺:是（F3 寫 cut 卻對本 slug 仍舊 7；2.1.0 不是 cut；函式真不是完；doctor 綠不是 ticket；用語不是 SoT）
- 真 trade-off:是（可見紀錄 vs silent True；修讀鍵 vs 雙寫；graph+dual-read vs 單邊空切；誠實紅 vs 放寬握手；三路電池 vs 假綠）
→ 晉升:**否**（難逆轉未中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-14 | Owner Stage1 OK「ok」+ Writer B dispatch：cut attestation SoT／key-read seam／graph vs dual-read／doctor honesty／success-hollow／Non-Goals。六點對 1A／2A／3C／4A／5A／6A。Inherit F2＋4A 前置；2.1.0≠cut；禁 silent True；保護 in-flight／token；doctor≠ticket；measurable SC；no G1 invent。
- Stage 1 改口 | 2026-09-14 | 1-discussion 仍 draft、當時寫不送 G1；Owner「ok」後開本站。不回改正本討論。
- 獨立於他線 Stage 2 | 2026-09-14 | Writer B 只讀金本 `1-discussion.md`（C+soft-fix）＋ brief §6–§7＋狀態機＋F1 annex＋F2 Decision／4-spec／7-review／coordinator／doctor／模板。當時無他線 F3 Stage 2 PR。
- Owner standing soft-fix | 2026-09-14 | Winner B 全票 #363（R1→B、R2→B、R3→B）。不換 winner。骨架 1A+2A+3C+4A+5A+6A。釘：cut SoT＝語意槽（誰／何時／哪個條件），路徑 OPEN 交 4-spec。收 A：`contract_version()` 只讀 `devflow_contract_version`、殺 fallback／錯鍵 dual-read、錯鍵 bump ≠ declared、拒因「F3 cut 未發生」、可選 F3-F2-REGRESS 地板。收 C：Rejected 拆 silent True vs 用語、可選「出貨態故意 doctor 紅」、可選 PRE-AND。抬高 Non-Goal：不重開 F2 park D-1／D-2／D-3／F-c-4。不收 A 的同檔兄弟布林 SoT／blame-as-who-when；不收 A 的四路 IFF；不收 C 的整電池空心。20 CASE 極性＝注入→該格紅。`status: draft`、`verdict` 空。**不發明 G1 PASS**。
- Q15／Q16／Q17／Q18／Q19 對帳 | 2026-09-14 | 五條 `[~]` 到期收進 Decision（OC-11／4／3／7／12），不再當「仍待驗可改口」。
- Q20–Q25 對帳 | 2026-09-14 | `[>]` 本站選定：SoT＝可見紀錄；graph＝3C；doctor＝清單；成功＝三路電池；活五站名不發明；STATUS 用語＝companion。
- 自檢七掃 | 2026-09-14 | ①每案優劣有依據欄（空格標 `[Assumption]`）。②Goals G-cut／freeze／token／attest／pre／honest／graph／self／success／keep／carry 進 Decision／SC；漏項進 Non-Goals。③`[>]` Q20–Q25 皆本方案處理。④SC 皆具名 CASE／exit／檔集；紅格極性＝注入。⑤Rejected 無空棄因（含 Q21 其餘三選項）。⑥六決策點由 Writer B dispatch 確認；OC-1／2／3／5／6／8 延伸、OC-4／7／11／12 升格、OC-5 機制收窄＋OC-9 收窄、OC-10 流程層，皆可回溯決策點。⑦既有脈絡是對帳不是外移 schema。圖上 1A–6A 標選定，Rejected 未上圖。
- 本 hop 不送 G1 | 2026-09-14 | Decision hop：`verdict` 空；OC 全「待人審」；不跑 N8 三連動。standing 合稿後仍不發明 PASS。coordinator 下一問才是人審 G1。
- G1 | 2026-09-14 | Human G1 PASS + OC-1…OC-12 Owner PASS @ 2026-09-14 Asia/Taipei。owner chat「可以」。未發明新 OC 答案；看板依 Decision 原文標 Owner PASSed。基準 #366（`35e0f47`）／#367 STATUS Stage2（`6ab48b3`）。owner 自審(有記錄)；reviewers: [user]；operator tony 經 `scripts/devflow_gate.py write` 落頂欄。未發明 G2／G3 PASS。不開 Stage 3／4。
