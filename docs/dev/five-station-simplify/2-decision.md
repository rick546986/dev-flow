---
feature: five-station-simplify
stage: 2-decision
status: in-review
verdict:
owner: rick
reviewers: []
updated: 2026-09-13
---

# 2. 收斂 — 五站簡化（Implementer B：dual-read 誠實 + 採用端陷阱）

> 把 `1-discussion.md` 收成一個選定方案。Lane = **full**。本 hop **只本檔 + 審頁 html**；不實作 F1、不改 `_templates/`／`graph.yaml`／gate token、不改 STATUS／HISTORY、不填 G1 `verdict: PASS`、不合併。
> Stage 1 頂欄仍 `status: draft`、當時寫「不送 G1」。使用者 2026-09-13 標 **Human PASS** 後才開本站。1-discussion 留當時說法；改口記本檔。
> F0 十條已鎖，本檔**不重開**：五站別名、殺例行中閘、Ship 唯人、條件 A/B、Must-keep、F1→F3、本 slug 走舊 7。翻任一條 = 新 brief。
> B 線主軸：**dual-read 必須誠實**（舊檔不紅 ≠ 路線已切）；**marketplace update × doctor 綠** 是採用端陷阱，不是「已經五站了」的證據。獨立於 A／C，未讀他線 Stage 2。

## Real-world 去向
| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| 「例行 G1／S3-ACCEPTED／G2 讓方向、互動、契約三次都要等人」 | 本方案處理 | 1A：摺預設人停，物質與 token 留 |
| 「Treat as PASS／都過／可以落成 verdict: PASS，審查物質沒進人腦」 | 本方案處理 | 殺例行停；Ship 仍唯人；Agent 代寫 = 未寫 |
| 「摺站若只殺等待、卻讓 Spec／Build 拿掉 ID 鏈、反模糊、T 四欄、acceptance seam」 | 本方案處理 | 6A：Must-keep 去向；四欄＋seam Owner-locked |
| Journey「owner chat 蓋章；方向卡沒被讀完也過」 | 本方案處理 | 1A + 5A：中閘不再等人按提交；空 attestation 仍拒 |
| Journey「Demo 欄空、chat 仍准開 Stage 4」 | 本方案處理 | Q11→5A；B1 命中無 attestation 不得離 Spec |
| Journey「實作者若省四欄／seam，勾選假完成」 | 本方案處理 | G-out-3／AC-3；缺欄 checkbox 不得冒充完成 |
| Journey「採用現場踩洞靠口頭中繼」 | 刻意維持 | 本包不建回報口；痛是物質洞，不是蓋章證據 |
| Workaround「Agent 把口頭章落進 md 頂欄」 | 本方案處理 | M5／OC-6：頂欄才是判定；chat 不是判定 |
| Workaround「採用洞進 dispatch-accounting-symmetry，不進 public issue」 | 刻意維持 | public repo 禁收公司路徑；Q6 保持 Assumption |
| Exception「Fast 仍吃 G2 物質」 | 刻意維持 | 不廢 Fast；G2 物質不因摺站消失 |
| Exception「in-flight 整段舊 7」 | 本方案處理 | 4A + G-out-8；本資料夾已存在 = 已凍結 |
| Exception「F0–F2 母版新開改版軌仍舊 7」 | 本方案處理 | brief §6；避免雙路線污染觀測 |
| Exception「[Assumption] 採用現場仍 chat 蓋章」 | 仍待驗 | Q6；過期擋本 slug G2；本 G1 不升成已核事實 |
| Exception「後站會用『已經五站了』省略 M11／M3／M1」 | 本方案處理 | Stage 2 對帳：Decision 把三者標不可選 |
| Exception「A1／A2 共寫 1-discussion.html」 | 仍待驗／F1 annex | 本 slug F1 annex 核對產檔器 dest；本檔不選定分檔。不是另開 slug |
| 「marketplace 可換 hops，doctor 仍可因 2.0.0 握手綠」 | 本方案處理 | 3A：doctor 綠 ≠ 路線沒變／已切 |
| 「本 slug = live freeze 樣本」 | 本方案處理 | 4A／7A：自己出貨路徑仍舊 7 |
| Q8 dual-read 2.1.0 欄位與舊檔不紅缺省 | 本方案處理 | 誠實定義本檔鎖（2A／OC-1）；欄位名仍待驗／本 slug F1 annex。不是另開 slug |
| Q10 coordinator event 與 rewrite cap 計數落點 | 本方案處理 | cap 數字已鎖；計數落點仍待驗／本 slug F2。不是另開 slug |
| Q11 空 attestation 五站後是否仍機械拒 | 本方案處理 | 5A：仍拒；chat 准開不構成判定 |
| M1–M16 帶走表 | 本方案處理 | 每條高影響 M 必有去向；見下 Disposition |
| rewrite cap hop≤2／Decide≤1／Goal reopen≤1 | 本方案處理 | Constraints 已鎖；計數落點仍本 slug F2 |
| 「本 hop 不改模板、不送 G1」 | 刻意維持 | 7A：本 PR 只 Decision＋html |

## Approaches Considered

### 決策點 1：摺停點怎麼落地
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 1A | **五個別名、七檔名不動**。例行 G1／S3-`ACCEPTED`／G2 不再是人類必停；token、twin、graph 節點、牙全留。謂詞假 = 停該站修，不准改問人。Ship = 唯一預設人停 | 對準 OC-1…OC-6；dual-read 與 in-flight 仍有錨；等人次數不再等於站數 | coordinator 要到 F2 才有；F3 前新 slug 仍舊 7，痛暫時還在 | 中 | `notes/design/five-station-simplify-brief-v3.md:L30-L45` 十條；`:L47-L58` 別名不是新檔名；`:L13-L28` 摺停點不摺完整度。`skills/dev-flow/stage2/graph.yaml:L53-L57`、`stage4/graph.yaml:L93-L98` 預設路經 N7-g1／N6-g2。成本 `[Assumption]` |
| 1B | **刪 G1／G2／`ACCEPTED` token 與檔**，謂詞比較好寫；中閘直接消失 | 狀態機短；沒有「仍產 twin 卻不等」的雙重語意 | 舊 7 與 dual-read 一次失去錨；違 OC-10／X2；in-flight 無路 | 高 | `1-discussion.md:L160` 不刪 token；`five-station-simplify-f0-state-machine.md:L189-L201` X2；`scripts/check-gate-tokens.sh:L44-L60` token 釘死。刪了就無法 2.1.0 同時讀舊 7 |
| 1C | **維持七站例行停**，只加厚「請認真審五格」散文 | 零路線風險；不碰採用端 hops | 母版 dogfood 已證明散文擋不住 chat 蓋章；等人次數仍綁站數；G-out-1 落空 | 低 | `docs/dev/dogfood-ping/2-decision.md:L110` Treat G1 as PASS；`dogfood-ping/4-spec.md:L14-L16` 同日 G2 PASS；`integration-before-verdict/2-decision.md:L89`「都過」；`diagram-ir-gate/2-decision.md:L112`「可以」。`1-discussion.md:L93-L94` 系統不留「讀過哪五格」 |

### 決策點 2：dual-read 誠實
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 2A | **2.1.0 同時讀舊 7 與新 5**。舊 slug 缺新欄 = 合法缺省、不得一次變紅。未宣告 2.1.0 = 必須仍走舊 7。F0 不 bump。誠實句：能解析兩套 ≠ 已把對方切到五站 | 對準 OC-7／G-out-5；in-flight 與未 upgrade 採用端不被誤殺 | annex 欄位名本檔不鎖（Q8）；F1 才寫牙 | 中 | `notes/design/five-station-simplify-brief-v3.md:L160-L169` dual-read minor=2.1.0、`2.0.0` 繼續讀舊 7；`docs/dev/five-station-simplify/1-discussion.md:L177` Q8 移交 F1；`devflow-contract.json:L1-L3` 現仍 2.0.0。欄位清單 `[Assumption]`（F1 annex） |
| 2B | **一次切 2.1.0 並讓舊檔缺新欄就紅**（「誠實」做成乾淨破裂） | 沒有雙語意；誰沒改立刻看見 | 違「舊檔不紅」；in-flight 與未 upgrade 採用端一次紅；X4 風險 | 高 | `notes/design/five-station-simplify-brief-v3.md:L164` 不得讓舊 slug 一次變紅；`docs/dev/five-station-simplify/1-discussion.md:L143` G-out-5。破裂被叫誠實 = 偷換主詞 |
| 2C | **不 bump，靠 marketplace 換 hops 假裝已切五站** | 最快；doctor 繼續綠 | 採用端被遠端改線而握手仍綠；這就是不誠實；G-out-5 反面 | 低 | `skills/dev-setup/SKILL.md:L16` 節點 MD／graph 不複製進採用專案；`:L62-L68` 更新=`marketplace update`+`plugin update`、單一 entry `./`。`hooks/_doctor_impl.py:L193-L202` 只比對契約版本 ∈ supported，不看 hops 路線 |

### 決策點 3：marketplace × doctor-green 陷阱
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 3A | **寫死：doctor 綠 ≠ 路線沒變，也 ≠ 路線已切**。未 upgrade 到 2.1.0 dual-read 前，marketplace 換 hops 不得把採用端改成五站預設。F1 至少要能紅「契約仍 2.0.0 且 hops 已是五站預設」。未 upgrade = 舊 7，不得遠端改線 | 把 Stage 1 已帶走的採用 hop 身分變成可驗拒絕；對準 Constraints | 本 PR 不寫牙；F1 才落地；採用端何時 upgrade 仍是人 | 中 | `docs/dev/five-station-simplify/1-discussion.md:L187` 採用 hop 身分；同檔 `:L222` 帶走表；`notes/design/five-station-simplify-brief-v3.md:L168` 未 upgrade = 舊 7。`hooks/_doctor_impl.py:L193-L202` 握手只看版本集合。`.claude-plugin/marketplace.json:L9-L15` 單一 `source: ./`。牙形細節 `[Assumption]`（F1） |
| 3B | **本刀改 doctor**：握手加「路線欄」，2.0.0 直接拒五站 hops | 陷阱當場閉環 | 違 F0 禁改既有牙／本 PR 不實作 F1；還可能讓未切的母版自打 | 高 | `notes/design/five-station-simplify-brief-v3.md:L7-L9` F0 不准改既有牙；`docs/dev/five-station-simplify/1-discussion.md:L158` 本 hop 不改契約版本；同檔 `:L191` F1 牙只准 scripts／annex。本刀改 doctor = 偷做 F1 |
| 3C | **相信 marketplace 與契約版本永遠同步**；doctor 綠就可跟 hops 走 | 零新規則 | 現況已經不同步：runtime 3.24.0、契約 2.0.0、hops 隨 pack；相信同步 = 否認已核事實 | 低 | `hooks/runtime-capabilities.json:L1-L4` supported 只有 2.0.0；`devflow-contract.json:L1-L3`；`dev-setup/SKILL.md:L62-L68` hops 住方法包。同步是願望不是事實 |

### 決策點 4：in-flight freeze
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 4A | **F3 cut 當下 `docs/dev/<slug>/` 已有 1–7 任一 `.md` → 整段舊 7 到 Ship**（含例行 G1／條件 S3／G2／G3）。本資料夾已有 `1-discussion.md` = 已 in-flight，是第一個 live freeze 樣本。F0–F2 母版新開改版軌也舊 7。舊 7 不套 rewrite 三 cap | 對準 OC-9／G-out-8／Q12；觀測不被自己污染；偵測規則可指到檔 | 本 slug 自己仍要等人過 G1／G2；看起來「沒吃到藥」 | 低 | `notes/design/five-station-simplify-brief-v3.md:L160-L167`；`notes/design/five-station-simplify-f0-state-machine.md:L49-L50` 已有舊 7 檔則不建立五站機；`docs/dev/five-station-simplify/1-discussion.md:L181` Q12 `[x]`；同檔 `:L223` 本 slug = live freeze。只認 md、不認裸 html = OC-5 |
| 4B | **F3 當下把 in-flight 折成五站** | 全樹同一路線；少一套 graph | 違 X4／OC-9；進行中 feat 中途改 hop；G1 已簽的包語意漂 | 高 | `notes/design/five-station-simplify-f0-state-machine.md:L196` X4 禁 in-flight 套新機；`docs/dev/five-station-simplify/1-discussion.md:L161` 不把 in-flight 折五站 |
| 4C | **本 slug 當新 5 第一個白老鼠**（吃自己的藥） | 立刻驗證五站謂詞 | 觀測被自己污染；F0–F2 禁雙路線；G-out-8 反面 | 中 | `docs/dev/five-station-simplify/1-discussion.md:L146-L147` G-out-8；同檔 `:L192` 本資料夾已存在 = 已 in-flight；`notes/design/five-station-simplify-brief-v3.md:L166` F0–F2 新開軌仍舊 7 |

### 決策點 5：Q11 空 attestation
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 5A | **B1 命中且 attestation 空 = 機械拒**。owner chat「准開下一站／可以」不得寫入 Human verdict，也不得當 attestation 替代。五站後保持。沒命中 → 不產 Demo、不 latch | 對準 M5／AC-4／狀態機 2.3 條 6；堵住 dogfood 捷徑 | 有人會覺得「都摺站了還卡 Demo」 | 低 | `docs/dev/five-station-simplify/1-discussion.md:L179` Q11 移交本站；`notes/design/five-station-simplify-f0-state-machine.md:L90-L96` 無 attestation 的 ACCEPTED = 假；`_templates/3-prototype.md` 頂註 Agent 禁代填；`docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9` 欄空仍開 Stage 4。現行牙已拒，五站後要保持 = 討論已寫 |
| 5B | **chat 准開可繞 attestation**（記一筆「owner 口頭 ACCEPTED」） | 跟現況 dogfood 相容；少一次人停 | 把蓋章從 G1 搬到 Demo；G-out-4 落空；md 頂欄不再是正本 | 低 | `notes/design/gate-verdict-write.md`（1-discussion `:L48` 引 L8-L11）：判定正本 = 同目錄 md 頂欄，勾選 ≠ PASS。口頭替代 = 正本被 sidecar／chat 取代 |
| 5C | **五站後取消 attestation**（已殺例行 S3 停） | 少一個欄 | 混淆「例行停」與「B1 latch」；違 OC-2（機制全留）與表 B；Agent 可代填 ACCEPTED | 中 | `brief-v3.md:L101-L117` B1 latch 仍是、人類親填+attestation；`:L21` 不摺九條 trigger／Agent 禁代填。殺停 ≠ 殺 latch |

### 決策點 6：Must-keep 去向與 F1 牙落點
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 6A | **每條高影響 M 用 `M11 → R-x/S-y` 或 `Non-Goal:<reason>`**，不另發 ID 鏈。T 四欄與 RED→獨立審查 seam **不可選**。F1 牙只准長在 `scripts/` 與 annex（Backlog B 凍 Stage 1–4 模板）。本 PR 連牙都不寫 | 對準 Q7／Q9／G-out-3；後站掏空會被看成違規；不污染觀測 | 4-spec 才把 M 落到具體 R/S；本檔只鎖語法與不可選 | 中 | `docs/dev/five-station-simplify/1-discussion.md:L175` Q7 最小拒收謂詞；同檔 `:L177` Q9 種子語法；`:L185` Owner-locked 四欄+seam；`:L191` 牙只 scripts／annex；`docs/dev/STATUS.md:L50` Backlog B 凍模板。`_templates/5-tasks.md:L50` 四欄必填；`_templates/6-implementation-notes.md:L104-L137` seam |
| 6B | **把 M1／M3／M11 當可選「簡化細節」**，五站先跑起來再補 | Build 看起來短 | 假完成 T；少一條 = 違 brief 不是簡化成功；C 線主風險被放行 | 低 | `notes/design/five-station-simplify-brief-v3.md:L135-L158` 少一條=違規；`docs/dev/five-station-simplify/1-discussion.md:L125` 若把 M 標可選則過期擋 G2；同檔 `:L210` M11 假完成定義 |
| 6C | **F1 改 Stage 1–4 模板把 M 釘進欄位** | 寫手抄模板就看見 | 撞 Backlog B 與 F0 禁改模板；污染「下一輪才跑」的 full-lane 觀測 | 高 | `notes/design/five-station-simplify-brief-v3.md:L7-L9` F0 不准改 `_templates/`；`docs/dev/STATUS.md:L50` 觀測前不動 Stage 1–4；`notes/dispatch-parallel-feature-gaps.md`（1-discussion `:L57` 引 L279-L285） |

### 決策點 7：本 PR 與 F0→F3 切刀
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 7A | **四刀不併**。本 PR 只 `2-decision.md` + 審頁 html。不實作 F1 牙／annex、不寫 coordinator、不切預設路線、不改 STATUS、不宣稱 G1 PASS。F1=teeth+dual-read annex；F2=coordinator+event；F3=新 slug 才預設五站 | 對準 OC-8／使用者本 hop；本 slug 自己當 freeze 樣本 | 採用端痛要等到 F3 才從預設消失 | 低 | `notes/design/five-station-simplify-brief-v3.md:L171-L182` 四刀表；`docs/dev/five-station-simplify/1-discussion.md:L154` F1 才釘牙；本 hop brief：Stage2-B、no merge、no STATUS。本 PR 檔集可 `git diff --name-only` 核對 |
| 7B | **本 PR 順便寫 F1 牙**（scripts／annex 最小拒收） | 少一次 hop；Q7 謂詞立刻可紅 | 違「不准 F0／本 Decision 偷做 F1」；本 slug 尚未過 G1；牙沒有 4-spec | 高 | `notes/design/five-station-simplify-brief-v3.md:L173` F0 不加牙；同檔 `:L178` F1 才 teeth；使用者：「No F1 implementation in this PR」 |
| 7C | **併刀 F1+F2+F3**（一次切五站+coordinator+刪等待） | 看起來一次做完 | 雙路線、in-flight、採用端握手同時爆；違「不准併刀」 | 高 | `notes/design/five-station-simplify-brief-v3.md:L173` 不准併刀；`notes/design/five-station-simplify-f0-state-machine.md:L215` F0 交卷沒有腳本、沒有 fixture |

## 方案架構圖
```
[1A] 五個別名殺例行停(選定)
[2A] 2.1.0 dual-read舊檔不紅(選定)
[3A] doctor綠≠路線已切(選定)
[4A] 已有md整段舊7(選定)
[5A] 空attestation仍拒(選定)
[6A] M去向+牙只scripts/annex(選定)
[7A] 本PR只Decision不實作F1(選定)
```

## Decision
採 **1A+2A+3A+4A+5A+6A+7A**：預設路線用五個別名 Intake→Decide→Spec→Build→Ship，舊七份檔名不動。摺的是例行人類停點，不是完整度。G1／S3-`ACCEPTED`／G2 的物質、token、twin、牙留下，預設不再等人按提交判定；謂詞假就停在該站修。Ship（舊 G3 物質）是唯一預設人類必停；coordinator／Agent 代寫 `verdict: PASS` 或 `ACCEPTED` = 未寫。條件頁走表 A／B：生成謂詞假不產頁，latch 假不准問人。契約 minor 2.1.0（F1 annex 寫；F0 不 bump）必須同時讀舊 7 與新 5，舊檔缺新欄不得一次變紅。**dual-read 誠實** = 能解析兩套格式，不得把「doctor 因 2.0.0 握手綠」或「marketplace 已換 hops」說成採用端已切五站；未 upgrade = 舊 7，不得遠端改線。`docs/dev/<slug>/` 已有 1–7 任一 `.md` 的 slug 整段舊 7 到 Ship；本 slug 是第一個 live freeze 樣本，自己的 G1／G2／G3 仍走舊 7。B1 命中且 attestation 空仍機械拒；chat 准開不是判定。Must-keep M1–M16 少一條 = 違 brief；T 四欄與 RED→獨立審查 seam 不可選；去向語法用 Q9 種子；F1 牙只長 scripts／annex。**Decision 約束 + RP-1…RP-16** 是後站不准改成可選的最小拒收集（Q7＋M 表＋狀態機 §6）；F1 annex 只准加牙、不准減。本 PR 只落 Decision＋審頁，不實作 F1。不選 1B／2B／2C／3C／4B／4C／5B／5C／6B／6C／7B／7C。

## Decision 約束（後站不准改成可選）
1. **Must-keep M1–M16 少一條 = 違 brief**，不能寫成「已經五站了所以可省」。
2. **T 四欄（Covers／Files／Verify／Blocked-by）與 RED→獨立審查 seam 不可選。** Owner-locked。缺欄、無 RED 輸出、reviewer=implementer → 勾選仍算未完成。
3. Spec 的 S 仍吃反模糊三律；TBD／不可測／測試名不含 S-id 不得當完成。
4. 去向語法採 Q9：`M11 → R-x/S-y | Non-Goal:<reason>`。不另發 ID 鏈。禁刪 token／禁改 graph／牙是**約束**，不得寫成 `M15 → Non-Goal`／`M16 → Non-Goal`。
5. rewrite cap 已鎖：hop≤2／Decide≤1／Goal reopen≤1；用盡 Escalated；不准暗改。舊 7 不套這三 cap。
6. 採用 hop 身分：未 2.1.0 dual-read 前，marketplace 可換 hops 而 doctor 仍可綠；未 upgrade = 必須仍走舊 7。
7. dual-read 誠實三句（OC-1）與本 slug live freeze（4A）維持已鎖；後站不得改成可選。

## 本方案要求（F1 拒收謂詞；annex 只准加不准減）
| # | 拒收謂詞 | 來源 |
|---|---|---|
| RP-1 | T 缺 Covers／Files／Verify／Blocked-by → 紅 | Q7、M11 |
| RP-2 | 無 RED 輸出或 reviewer=implementer → T 未完成 | Q7、M11 |
| RP-3 | S 含 TBD／不可測 → 紅 | Q7、M3 |
| RP-4 | 測試名不含 S-id → 紅 | M1 |
| RP-5 | 缺 Files 欄或 Files ⊈ 5-tasks 聯集 → 紅 | M9 |
| RP-6 | 無原始輸出 → 紅 | M10 |
| RP-7 | 不可逆且無 Quiz → 紅；非不可逆被強制 Quiz 當例行停 → 違 G-out-1 | M14 |
| RP-8 | Ship 無人寫 `verdict: PASS` 卻標 Done → 紅 | 狀態機 §6.1、G-out-4 |
| RP-9 | hop 重寫第 3 次仍繼續 → 紅 | 狀態機 §6.2 |
| RP-10 | Decide 重開第 2 次仍繼續 → 紅 | 狀態機 §6.3 |
| RP-11 | Goal 離開 Intake 後重開第 2 次仍繼續 → 紅 | 狀態機 §6.4 |
| RP-12 | B1 未命中卻要求 `ACCEPTED` → 紅 | 狀態機 §6.5 |
| RP-13 | B1 命中、無 attestation，卻 hop 出 Spec → 紅 | 狀態機 §6.6、Q11、5A |
| RP-14 | latch 未命中卻留下「請人審」紀錄 → 紅 | 狀態機 §6.7 |
| RP-15 | 舊 7 in-flight slug 被寫入五站狀態 → 紅 | 狀態機 §6.8、G-out-5／8 |
| RP-16 | Agent 代寫 `ACCEPTED` 或 Ship `PASS` → 視為未寫並紅 | G-out-4、M5 |

F1 牙長在 `scripts/` 與 annex，不准改 Stage 1–4 模板。形狀欄位名交本 slug F1 annex；本表是最小集合。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| 1B 刪 token | 舊 7 與 dual-read 失去錨；X2／OC-10；in-flight 無路。 |
| 1C 只加厚散文 | dogfood 三案已用 chat 蓋過例行中閘；等人次數仍綁站數。 |
| 2B 舊檔缺欄就紅 | 把「誠實」做成乾淨破裂；違「舊 slug 不得一次變紅」。 |
| 2C marketplace 假裝已切 | doctor 只握手版本；hops 隨 pack。這是陷阱本身，不是方案。 |
| 3B 本刀改 doctor | 偷做 F1；F0 禁改既有牙；本 PR 不准實作。 |
| 3C 相信版本與 hops 同步 | 現況已不同步（契約 2.0.0、runtime 3.24.0、hops 住方法包）。 |
| 4B F3 折 in-flight | X4；進行中 feat 中途改路線。 |
| 4C 本 slug 當新 5 白老鼠 | 觀測被自己污染；G-out-8 反面。 |
| 5B chat 繞 attestation | 判定正本離開 md 頂欄；蓋章從 G1 搬到 Demo。 |
| 5C 取消 attestation | 殺停被偷換成殺 B1 latch；違表 B。 |
| 6B M 可選 | 假完成 T；少一條 = 違 brief。過期擋本 slug G2。 |
| 6C F1 改 1–4 模板 | 撞 Backlog B 與 F0 禁令；污染觀測。 |
| 7B 本 PR 寫 F1 牙 | 使用者禁令 + brief 不准 F0／Decision 偷做 F1。 |
| 7C 併刀 F1+F2+F3 | brief 不准併刀；in-flight 與採用端同時爆。 |
| 重開 F0 十條 | 翻任一條 = 新 brief，不是本檔修辭。 |
| 改七份文檔檔名 | 五站是別名；檔名家族不動。 |
| 廢 Fast | Fast 仍吃 G2 物質；不是本包要廢的。 |
| 第二條 Journey／Actor／M ID 鏈 | Stage 1 Non-Goal；去向引用原文。 |

## Rationale
痛有兩層，不能互相冒充。採用兩案 2026-08-17 回報的是 G1／G2／G3 **物質洞**（散發路徑、守衛自打），證明現場真的在走這些閘。母版 dogfood 三案回報的是 **蓋章**：同一日 chat 把 G1 與 G2 簽成 PASS，Demo 欄可空著先開 Stage 4。摺的是第二層的例行等待；第一層的物質（OC、R/S、Demo、Evidence、T 四欄、seam）要留，而且要有牙。

1C 重複已經失敗的散文。1B 為了謂詞好寫拆掉 dual-read 與 in-flight 的錨。1A 分開「停點」與「完整度」：預設不再請人按提交判定，檔與 token 仍在。

B 線要把「看起來已經切了」這句話拆開。doctor 只問契約版本 ∈ `supported_contract_versions`。graph／hooks 住方法包，`marketplace update` 就能換 hops。兩件事今天就可以同時成立：doctor 綠、路線已被遠端改。2C／3C 把這當成方案；2A＋3A 把它當成必須紅的陷阱。2B 用「舊檔變紅」冒充誠實——誠實是舊 7 繼續合法，不是一次破裂。

4C 拿自己當新 5 白老鼠，會讓「F0–F2 仍舊 7」的觀測禁令失效。4A 讓本資料夾當 freeze 樣本：後面若有人用五站自動前進跳過本 slug 的 G1／G2，必須跳不過。

5B／5C 會把 dogfood 捷徑寫進新機。5A 只做一件事：B1 命中時，空 attestation 仍是假，chat 不是判定。

6B 是摺站之後最便宜的偷法。6A 把 M11／M3／M1 從「簡化細節」拿出來，標成不可選；牙的形狀進 F1，本 PR 不寫。7B／7C 把尚未過 G1 的方向核准偷做成施工。

## 既有脈絡
對帳快照（2026-09-13 tip `894960f`，Stage 1 C 已合 `#295`，STATUS Active 已開 `#298`）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| F0 brief＋狀態機 | Owner 已核；十條鎖死 | 本檔只收怎麼落地；不重開 |
| Stage 1 `#295` | 1-discussion status=draft；Must-keep 帶走表齊 | 留當時說法；Human PASS 後本檔改口 |
| 契約／runtime | `2.0.0`／plugin `3.24.0`；doctor 只握手版本 | 2A＋3A：綠 ≠ 五站 |
| marketplace | 單一 entry `./`；更新換整包 hops | 3A 陷阱正本 |
| Gate token | G1=OC 全裁決；G2=R/S+DD+Profile+Demo；G3=S 全綠+回歸+現象+Evidence 八點 | 物質留下；例行停殺掉 |
| 模板凍結 | Backlog B：完整 full-lane 觀測前不動 Stage 1–4 | 6A／7A：F1 牙只 scripts／annex；本 PR 不動模板 |
| 本 slug STATUS | Active 在 1-discussion；Gates 全白 | 本 branch **不**改這列（OC-4） |
| 本資料夾 | 已有 1-discussion.md／.html | 已 in-flight；出貨走舊 7 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 寫手用「已經五站了」省略 M11／M3／M1 | Decision＋SC-3 標不可選；4-spec 每條高影響 M 必有去向；缺 Verify 的 T 不得完成。6B 進 Rejected |
| 採用端 marketplace update 後被遠端改線，doctor 仍綠 | 3A＋SC-9／SC-10：F1 牙紅「2.0.0 + 五站 hops」。本檔禁止把 doctor 綠當成路線證據 |
| 有人把 2A「舊檔不紅」讀成「可以默默切五站」 | 誠實句寫進 Decision 首段；2C／3C 進 Rejected。綠＋不紅 ≠ 已切 |
| Q6 採用蓋章為假，殺例行停的現場理由變弱 | 不升成已核事實（OC-8）。母版 dogfood 三案仍夠撐「殺等待」。Must-keep 不依賴 Q6。過期擋本 slug G2 |
| 本 slug 被拿去試五站自動前進 | 4A／SC-8：目錄已存在 = freeze。五站 hop 必須被拒 |
| F1 欄位名未釘，Stage 4 前各寫各的 | OC-3：本檔只鎖誠實定義與陷阱謂詞，不鎖 annex 鍵名。Q8／Q10 落本 slug F1／F2，不是另開 slug |
| 後站把 M11／M3／M1 或四欄／seam 標成可選 | OC-11：4-spec／5-tasks 出現「可選四欄／可選 seam／已五站故省 Must-keep」→ 擋本 slug G2 |
| F1 annex 減掉 RP-1…RP-16 | OC-10：最小集只准加不准減；減項 = 翻本 Decision，回本站 |
| 本 PR 被當成已過 G1 或已落地 F1 | 頂欄 `verdict` 空；status=in-review；SC-11 檔集可核。7B 進 Rejected |
| 空 attestation 被 chat「可以」帶走 | 5A／OC-6：chat 不是判定。對照 dogfood-ping DOGFOOD-NOTES L9 |
| rewrite cap 被暗改或套到舊 7 | cap 數字已鎖；舊 7 不套。落點 F2。X5 進後站禁則 |
| A1／A2 其實已分檔，F1 白做雙檔名牙 | 保持 Assumption；期限 F1 annex。不進本 Decision 選定 |
| feature branch 手改 STATUS 互蓋 | OC-4 流程層：本 PR 不跑 `status-update.sh` |

## Success Criteria
每條都要能用「對照稿／拒絕輸出／檔集」核對。7-review 對這張表，不對口頭「看起來簡化了」。

- SC-1(G-out-1 殺例行停)：F3 之後的新 slug，Decide／Spec／Build 完成且中間 latch 未命中 → 前進紀錄沒有「請人審 A4／A7／提交判定」。謂詞假時，停修理由是該謂詞假，不是「先問 owner 要不要繼續」。本 hop 不跑 coordinator；對照稿後續造。
- SC-2(G-out-2 Must-keep)：一份宣稱「五站已簡化」但 M1–M16 少任一項的規格／任務／牙輸出 → 被點名違 brief，不得寫成簡化成功。
- SC-3(G-out-3 不可選四欄＋seam＋反模糊＋ID 鏈)：T 缺 Covers／Files／Verify／Blocked-by，或無 RED 輸出，或 reviewer=implementer → 該 T 不得標完成。S 含 TBD／不可測 → 紅。測試名不含 S-id → 紅。對照稿：`Verify: 看起來沒問題` 的假 T。
- SC-4(G-out-4 人主權)：Agent 寫入 `ACCEPTED` 或 Ship `PASS`（無人類 attestation／無人類頂欄）→ 系統當沒寫；不得離 Spec、不得 Done。
- SC-5(G-out-5＋dual-read 舊檔)：F3 cut 當下已有 1–7 `.md` 的 slug → 仍走舊 7（仍有例行 G1／G2）。2.1.0 讀這些舊檔缺新 5 欄 → 不紅。對照：本 repo 任一已有站檔的 slug，不是後續造的假目錄。
- SC-6(G-out-6 B1)：命中九條 trigger 之一 → 進 Build 前已有人類 `ACCEPTED`+attestation。未命中 → 無 Demo 頁、無第二次人停、n-a 有原因不是空白。
- SC-7(G-out-7 去向帳)：本檔 Constraints／Must-keep／Journey 高影響列，到本 slug 的 4-spec／5-tasks 時每條有 `M… → R-x/S-y` 或 `Non-Goal:<reason>`。本檔 Real-world 去向表先吃 Stage 1 高影響列。
- SC-8(G-out-8 本 slug freeze)：對 `docs/dev/five-station-simplify/` 要求五站自動前進、跳過例行 G1／G2 → 跳不過。目錄仍走舊 7 直到自己的 Ship。
- SC-9(dual-read 誠實)：2.1.0 annex 對「舊 7 檔、新 5 欄缺省」→ 綠／不紅。對照「契約仍 2.0.0、hops 已被 marketplace 換成五站預設、doctor exit 0」→ **不得**解釋成「已切五站」；F1 牙紅或同等拒絕。doctor 綠只能證明握手，不能證明路線。
- SC-10(marketplace × doctor-green)：固定對照：`devflow_contract_version=2.0.0` + marketplace 已更新使 hops 預設五站 + doctor 對 2.0.0 握手綠 → 採用端仍必須走舊 7；把「doctor 綠」寫成「可以跟 hops 走」的文案／謂詞 → 紅。未 upgrade 不得遠端改線。
- SC-11(本 PR 範圍)：本 PR 的 `git diff --name-only origin/main` 只含 `docs/dev/five-station-simplify/2-decision.md` 與 `docs/dev/five-station-simplify/2-decision.html`。無 `_templates/`、`graph.yaml`、`scripts/` 新牙、`STATUS.md`、`HISTORY.md`、`devflow-contract.json` bump。頂欄 `verdict` 空。
- SC-12(Q6 不升格)：本檔任何「採用現場也 chat 蓋章」句仍標 Assumption 或「仍待驗」。把 Q6 寫成已核事實 → 本 G1 應打回。
- SC-13(C 線 anti-hollow／F1 最小集)：F1 牙能紅 RP-1…RP-16；annex 新增謂詞可以，刪本表任一列不行。後站 4-spec／5-tasks 把 Must-keep 或 T 四欄／seam 標成可選 → 擋本 slug G2（OC-10／OC-11）。

## Scope & Non-Goals(定稿)
- In：1A 摺停點留物質；2A dual-read 誠實定義；3A 採用端陷阱與 F1 最少拒收謂詞（契約 2.0.0 + 五站 hops → 紅／拒改線）；4A in-flight 偵測（任一 1–7 `.md`）+ 本 slug 活樣本；5A Q11 空 attestation 仍拒；6A Must-keep 去向語法 + 四欄／seam 不可選 + F1 牙落點；7A 本 PR 只 Decision＋html、四刀不併。Decision 約束 + RP-1…RP-16 最小拒收集（只准加不准減）。Q8／Q10／A1–A2 落本 slug F1／F2，不是另開 slug。Q9 種子語法。rewrite cap 數字維持已鎖。
- Out：1B／1C；2B／2C；3B／3C；4B／4C；5B／5C；6B／6C；7B／7C；重開 F0 十條；刪 G1／G2／`ACCEPTED`；改七檔名；廢 Fast；第二條 ID 鏈；本 PR 實作 F1 牙／annex／doctor 路線欄；本 PR 寫 coordinator；本 PR 切預設路線；本 PR 改 STATUS／HISTORY／模板／graph／既有牙；本 PR 填 G1 PASS；本 PR 合併；拿本 slug 當新 5 白老鼠；把 Q6 升成已核事實；選定 dual-read 欄位名或 event schema。

## Must-keep Disposition（給 Stage 4 用的種子，不另發 ID）
| M | 去向種子 | 本檔落點 |
|---|---|---|
| M1 ID 鏈；測試名含 S-id | 本方案處理 → 後續 R/S | SC-3 |
| M2 圍欄 | 刻意維持 | 實作者禁讀 1／2／3 補洞 |
| M3 反模糊 | 本方案處理 → 後續 S | SC-3；TBD → 紅 |
| M4 Real-world→Demo→OC | 本方案處理 | SC-6；去向表 |
| M5 人寫 ACCEPTED／Ship PASS | 本方案處理 | 5A、SC-4 |
| M6 G3 Evidence 八點 | 本方案處理 → Ship | 不因摺站省略 |
| M7 Profile + fast+high 拒 | 刻意維持 | Fast 仍吃 |
| M8 DBC 條件式 | 刻意維持 | 不是新站 |
| M9 Files ⊆ 5-tasks | 本方案處理 → 後續 T | SC-3 |
| M10 驗證五律 | 本方案處理 → 後續 T | 無原始輸出 → 紅 |
| M11 T seam + 四欄 | 本方案處理 → 後續 T | Owner-locked；SC-3 |
| M12 author≠approver | 刻意維持 | Ship 與任何 latch |
| M13 html 重生 | 本方案處理 | 本 hop 產審頁 |
| M14 不可逆才 Quiz | 刻意維持 | Quiz ≠ 預設第三停 |
| M15 token／檔仍在 | 本方案處理 | 1A；拒 1B。禁刪 token 是**約束**，不是 Non-Goal |
| M16 F0 不改 graph／牙 | 本方案處理 | 7A；本 PR 不動。禁改 graph／牙是**約束**，不是 Non-Goal |

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | **dual-read 誠實**定義成三句：(1) 2.1.0 可解析舊 7 與新 5；(2) 舊 7 缺新欄不紅；(3) 未宣告 2.1.0 的採用端，即使 marketplace 已換 hops，仍必須走舊 7。使用者／F0 只鎖「dual-read 2.1.0」；「doctor 綠不得冒充路線已切」是 owner 延伸 | 少第 3 句，2A 會被讀成 2C | `notes/design/five-station-simplify-brief-v3.md:L160-L169`；`docs/dev/five-station-simplify/1-discussion.md:L187`。延伸本身 `[Assumption]` | SC-9／Decision 首段改寫；F1 annex 不必咬「2.0.0+五站 hops」 | 待人審 |
| OC-2 | F1 最少採用端拒收謂詞 = **契約仍 2.0.0 且 hops 已是五站預設 → 紅／不得改線**。使用者只被問到「採用 hop 身分」；具體拒收形是延伸 | 沒有這條牙，3A 只是散文，陷阱還在 | `docs/dev/five-station-simplify/1-discussion.md:L222`；`hooks/_doctor_impl.py:L193-L202`。牙掛哪支腳本 `[Assumption]`（F1） | 改咬別的訊號（例如只警告）；SC-10 觀測點變 | 待人審 |
| OC-3 | 本 Stage 2 **不選定** dual-read 欄位名、缺省鍵、coordinator event schema。Q8／Q10 落**本 slug** F1／F2 annex，不是另開 slug。這是對「把 dual-read 誠實寫進 Decision」的收窄 | 本 PR 不實作 F1；鎖鍵名 = 偷做 annex | `docs/dev/five-station-simplify/1-discussion.md:L177-L178` Q8／Q10 `[>]` | Scope 膨脹進 annex 欄位表；與 7A 衝突 | 待人審 |
| OC-4 | 本 Decision hop **不**跑 `status-update.sh`、不改 HISTORY、不改 1-discussion 頂欄、不把本檔 `verdict` 寫成 PASS、**不發明 G1 PASS**、本 Decision hop **不合併**。標**流程層** | 母版 STATUS 只在整合分支維護；使用者禁發明 G1 PASS | `docs/dev/STATUS.md:L10-L26`；本 hop brief | PR 帶 STATUS 列或自填 PASS，與並行 A／C session 互蓋 | 待人審 |
| OC-5 | in-flight 偵測 = `docs/dev/<slug>/` **已有 1–7 任一 `.md`**。僅有 html、無 md 不算開工。使用者 brief 寫「任一站檔」；「只認 md」是收窄 | html 可被產檔器誤生；md 才是站正本 | `notes/design/five-station-simplify-brief-v3.md:L165`「任一站檔」；`docs/dev/five-station-simplify/1-discussion.md:L192` 寫任一 md。收窄本身 `[Assumption]` | 裸 html 也會凍結；或空目錄被誤凍 | 待人審 |
| OC-6 | owner chat「可以／准開下一站／Treat as PASS」**不得**寫入 Human verdict，也不得當 attestation 替代。使用者只把 Q11 交給 Stage 2；「chat 不是判定」是延伸 | dogfood 捷徑就是這樣開 Stage 4 的 | `docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9`；`notes/design/gate-verdict-write.md`（1-discussion `:L48`）。延伸 `[Assumption]` | 5B 回流；空欄可被口頭帶走 | 待人審 |
| OC-7 | 本 PR **連 `scripts/`／annex 也不寫**。F1 牙落點維持 scripts／annex，但本 hop 零碼。這是對 6A「牙長在 scripts／annex」的收窄 | 使用者：No F1 implementation in this PR | 本 hop brief；`notes/design/five-station-simplify-brief-v3.md:L178` | 7B 回流；未過 G1 就長牙 | 待人審 |
| OC-8 | Q6 與「採用現場仍蓋章」保持 `[Assumption]`。**不**因無採用逐字稿擋本 G1；**仍**過期擋本 slug G2。這是對「期限 = F1 annex 前抽一案」的收窄（本 G1 放行、本 G2 仍咬） | 沒有採用逐字稿；捏造現場 = 自己犯 A-3 病。母版 dogfood 已夠撐殺等待 | `docs/dev/five-station-simplify/1-discussion.md:L174` Q6 `[~]`；同檔 `:L193` 過期擋 G2。收窄 `[Assumption]` | 要補現場訪談才准 G1；或把 Q6 升成已核 | 待人審 |
| OC-9 | Success Criteria 用「對照稿 + 可觀察拒絕／檔集」量測；本檔不寫測試檔或 fixture。量測形是對「可量測 SC」的延伸 | 本 PR 不實作 F1；fixture 進 F1／後站 | 模板頂註步 2；使用者強調 measurable SC。延伸 `[Assumption]` | SC 改成口頭「看起來對」；7-review 對不到 | 待人審 |
| OC-10 | RP-1…RP-16 是 F1 牙**最小集**：annex 只准加、不准減。使用者只鎖 Q7 三句＋「牙對 M 表」；把狀態機 §6 與 M1／M9／M10／M14 一併釘死是 owner 延伸 | 減項會讓「已五站」再次變成省略理由 | `docs/dev/five-station-simplify/1-discussion.md:L175` Q7；同檔 `:L199-L215` 拒收欄；`notes/design/five-station-simplify-f0-state-machine.md:L202-L213` §6。延伸本身 `[Assumption]` | F1 可刪 RP；SC-13 與 4-spec 對帳清單要重寫 | 待人審 |
| OC-11 | 本 slug 後站文檔（4-spec／5-tasks）若把 Must-keep（尤其 M1／M3／M11）或 T 四欄／seam 標成可選，擋本 slug G2。這是對 Assumption「後站會偷 M」的 Stage 2 對帳，不是新 Goal | 討論已寫過期擋「可選四欄」寫進 Decision；本檔選 6A 之後，後站再寫可選 = 違本 Decision | `docs/dev/five-station-simplify/1-discussion.md:L107`；同檔 `:L125` | 可選四欄可進 4-spec；假完成 T 變合法簡化 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 契約維持 `2.0.0`；本 hop 不 bump plugin／`devflow-contract.json`。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口。
- 審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。
- 不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。
- 未讀 A／C 線 Stage 2；本檔獨立收斂。
- A1／A2 共寫 `1-discussion.html` 保持 Assumption，落本 slug F1 annex（不是另開 slug）。
- rewrite cap 數字不重開；計數落點仍本 slug F2。
- 4-spec 再釘：每條高影響 M 的具體 R/S id、dual-read 欄位名、F1 牙腳本名。
- 吸收 C 線 anti-hollow：Decision 約束 + RP-1…RP-16 + OC-10／OC-11。M15／M16 維持約束，不抄 Non-Goal 種子。

## ADR 晉升檢查
- 難逆轉:否（F3 才切新 slug 預設路線；本檔與 F1／F2 在 G3 前可改 Decision／OC；本 hop 零 runtime）
- 反直覺:是（殺等待卻留 token；doctor 綠不是路線證據；本 slug 不吃自己的五站藥）
- 真 trade-off:是（少等人 vs 假完成；舊檔不紅 vs 乾淨破裂；freeze 觀測 vs 立刻驗證五站）
→ 晉升:**否**（難逆轉未中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-13 | Implementer B brief：dual-read honesty、adopter marketplace×doctor-green trap、in-flight freeze、measurable SC、OC ledger、每點 2–3 approach+reject evidence；F0 十條已鎖；本 slug 舊 7；本 PR 不實作 F1、不改 STATUS、不合併。七點對 1A…7A。
- Stage 1 改口 | 2026-09-13 | 1-discussion 仍 draft、當時寫不送 G1；使用者標 Human PASS 後開本站。不回改正本討論。
- 獨立於 A／C | 2026-09-13 | 未讀他線 Stage 2 產出；只讀 1-discussion＋brief＋狀態機＋模板。
- Q6 對帳 | 2026-09-13 | 母版 dogfood 三案蓋章 = Observed。採用現場是否同一手勢 = 仍 Assumption（OC-8）。未捏造採用逐字稿。
- 自檢七掃 | 2026-09-13 | ①每案優劣有依據欄（空格標 `[Assumption]`）。②G-out-1…8 進 Decision／SC-1…8；漏項進 Non-Goals。③`[>]` Q8／Q10 本方案處理（本 slug F1／F2 annex，不是另開 slug）＋OC-3；A1／A2=仍待驗／F1 annex；Q11=5A。④SC 皆對照稿／拒絕／檔集。⑤Rejected 無空棄因。⑥七決策點由 B brief 確認；OC-1／2／6／9 延伸、OC-3／5／7／8 收窄、OC-4 流程層、OC-10／OC-11 吸收 C 線 anti-hollow（最小拒收只准加、後站標可選擋 G2），皆可回溯決策點。⑦既有脈絡是對帳不是外移 schema。圖上 1A–7A 標選定，Rejected 未上圖。
- R2／R3 收斂修 | 2026-09-13 | R2 must-fix：Q8／Q10／A1–A2 去向不再寫「另開 slug」（本 slug F1／F2）。R3 吸收 C：Decision 約束＋RP-1…RP-16＋OC-10／OC-11；M15／M16 禁刪／禁改標約束不標 Non-Goal。A 線流程鎖留在 OC-4（不發明 G1 PASS、Decision hop 不合併）。不重開 dual-read／OC-1／SC-9／SC-10。
