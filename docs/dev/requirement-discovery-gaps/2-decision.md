---
feature: requirement-discovery-gaps
stage: 2-decision
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-13
---

# 2. 收斂 — 需求發現九條制度缺口

> 把 `1-discussion.md` 的發散收成 Decision。**本 hop 不宣稱 G1 PASS**：`verdict` 留空、`status` 留 draft，等人類 G1。不實作 `_templates/`／`skills/`／`example/`／守衛，不改 STATUS／HISTORY。
> owner 2026-09-13 已核准 Stage 1 方向並明示進 Stage 2。九條 DO／LIGHT 不重開。1-discussion 留當時「只 Stage 1、不送 G1」原文；本檔才改口成方案決策。本檔自己先照 A-1：Decision 寫落地結果與形狀，不鎖畫面／API／元件通道。

## Approaches Considered

### 決策點：落地形（HOW）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A | **同包落地**：同一 slug 改模板／skill／完整範例，並加只驗形狀的機械牙（欄位在、枚舉合法、disposition 非空、過期擋 G2）。語意留給 G1/G2 | 對準九條 G-out；堵住「指南寫了、範例仍教解法」；B-1 不會變成規定了但讀不到 | 本 slug 後續會動 Stage 1–4 教師，Diff 不小 | 中 | `1-discussion.md:88-97` G-out-1～9；`1-discussion.md:109` 同步改正範例；`1-discussion.md:243-246` 只改散文會走偏。成本 `[Assumption]` |
| B | **no-build／process-only**：不改模板與守衛，只加 G1/G2 審查清單與指南句 | 最短；不動教師，不污染他案觀測 | 範例繼續把 dashboard 寫進 Goal；牙仍只驗字樣；B-1 讀不到未指名事實；owner 已有審核筆記，痛仍在 | 低 | `1-discussion.md:99-110` Requested solution 要改教師；`1-discussion.md:243-246` 最極端＝九條全寫進指南、現場仍照範例走偏；`1-discussion.md:67` 現況就是人工筆記。A-1 仍比較本案：原因不是缺政策，是教師與牙在教錯形 |
| C | **分波／拆 slug**：先做 A-1/A-2，其餘另開 | 單 PR 較薄 | 違反「九條一包」；痛點去向與證據入口會再靜默消失一輪 | 高 | `1-discussion.md:121-122` 不拆九 slug；`1-discussion.md:116` Q2 已裁一包 |

### 決策點：教師與牙怎麼切
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| G | **形狀牙掛既有家族**（延伸 `check-realworld`／`check-spec-gate`／`devtalk-guard`）。A-1 守分欄與「驗收不鎖通道」節存在，不黑名單 dashboard／API。A-2 守 skill 對稱措辭（發現題禁推薦／裁決題可附），不對 Interview Log 做 NLP。完整範例**同 slug Stage 6**一起改 | 對準 Q7；不另造第二套方法論；範例與模板同輪，採用者抄不到舊樣張 | 形狀綠 ≠ 語意對；A-2 誘導仍靠抽查 | 中 | `1-discussion.md:127` Q7 移交；`1-discussion.md:243-246` 機械化＝部分牙＋部分 reviewer；`1-discussion.md:134` Q14 範例是否同 slug。A-1 黑名單誤殺：`notes/review-requirement-discovery-gaps.md:69-73` |
| K | **語意黑名單牙**：Goal 禁 dashboard／API 等詞；發現題用關鍵字猜「有推薦答案」 | 看起來硬 | 誤殺合法領域詞；對話語意無法從最終 md 還原；Stage 1 已標不值得假裝有硬 gate | 高 | `1-discussion.md:243-246`；`notes/review-requirement-discovery-gaps.md:69-73` A-1 只能部分機械化；同檔 `:99-102` A-2 不值得硬 gate |
| P | **只改 skill 散文，範例後開薄刀** | 本包 Diff 較小 | 本 slug 當 full lane 期間，採用者仍抄「dashboard 是最低成本呈現面」；A-1 教師分裂 | 低 | `1-discussion.md:27` 範例已鎖 dashboard／卡片／URL；`1-discussion.md:109` 要同步改正範例；`1-discussion.md:77` `[Assumption]` 採用者照範例走 |

### 決策點：證據與假設契約
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| E | **就地狀態枚舉** Observed／Reported／Inferred／Assumption／Conflict（不另發 Evidence ID）。Evidence 最小欄：來源類型、日期／as-of、角色或範圍、支持哪一段、限制。高影響 Assumption 四欄（若為假影響什麼／級／怎麼驗／何時誰驗）；到期未驗 → 既有 G2 形狀檢查擋。點頭只代表「盤點可當討論起點」 | 對準 A-3／A-4／Q8／Q9；reviewer 抽查可沿引用回去 | 要定「高影響」人工判準；日期解析要防假填 | 中 | `1-discussion.md:91-93` G-out-3／4；`1-discussion.md:128-129` Q8／Q9；`notes/review-requirement-discovery-gaps.md:125-131` 候選枚舉。欄位字面 `[Assumption]`（4-spec 再釘） |
| E2 | **維持 `[Assumption]` 二分**，只加散文期限 | 最短 | 第一因就是二分太粗；點頭仍可升格；牙繼續只驗字樣 | 低 | `1-discussion.md:30-32` 現況二分＋牙只驗字樣；`1-discussion.md:229-230` 點頭不能當來源 |
| E3 | **新 ID 鏈**（Evidence-1、Assumption-1）串 R/S | 對帳看起來機械 | 違反「不新增第二條 Journey／Actor ID 鏈」；兩套編號會漂 | 高 | `1-discussion.md:117` Non-Goals；`notes/review-requirement-discovery-gaps.md:125` 明確不新增第二 ID 鏈 |

### 決策點：去向與回看
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| D | **Stage 2 Real-world Disposition**：逐條引用高影響痛點／workaround／exception 原文片段（不另發 ID），標 addressed／intentionally unchanged／Non-Goal／separate slug／still-unverified。Stage 4：addressed 至少一條 R/S；其餘落到 Out of Scope／Known limit／後續 slug。**lookback 正本**落 7-review Exit 附錄（日期／owner／來源／低於何值重開）；HISTORY 只當 shipped 索引，不當量測本體。Success Criteria 分 Delivery／Outcome | 對準 A-6／A-7／Q10／Q11；有既有維護者；G3 不必等數週結果 | twin 頂區「未處置列」要等產器，本 hop 不改產器 | 中 | `1-discussion.md:94-95` G-out-6／7；`1-discussion.md:130-131` Q10／Q11；`notes/review-requirement-discovery-gaps.md:222-225` 引用原文、不另發 ID；同檔 `:261-262` 不要另造無主檔。產器延後 `[Assumption]` |
| D2 | **另造永久 outcome 檔**（`docs/dev/<slug>/lookback.md` 之類）當正本 | 目錄名對得上「改善回看」 | 無維護者；與 7-review／HISTORY 雙源；Stage 1 已拒 | 中 | `1-discussion.md:131` Q11 候選含 HISTORY 或 7-review 附錄，沒有第三檔；`notes/review-requirement-discovery-gaps.md:261-262` |
| D3 | **只在 G1 審頁列未處置列**，Stage 4 不對帳；lookback 口頭 | 本 hop 零模板 | A-6 第一因就是 2→4 靜默消失；口頭回看＝現況 | 低 | `1-discussion.md:34` Stage 4 不對帳 Stage 1 痛點；`1-discussion.md:235-238` |

### 決策點：入口與 Fast
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| F | **事實型 evidence manifest**：討論者先列「想找哪類證據與原因」，owner 核准來源／路徑後才讀；`devtalk-guard` 允許集合同步放行這些路徑，**仍禁** 2／3／4／5／6／7 與既有方案檔。ticket／SOP 裡的解法建議不當事實。**Fast** 進 Stage 4 前交六問分診（下一步／權限／等待語意／交接／系統外／中斷恢復）；全否且已有 approved spec 才可直接 fast；命中 → owner 裁升 full、或 fast + mini real-world delta、或 OC 接受風險。純視覺、不改語意的 bug 可維持 fast | 對準 B-1／B-2／Q12／Q13；圍欄不拆；Fast 不必一律拖進訪談 | manifest 形狀與 mini delta 欄位未釘；授權紀錄要防手填冒充 | 中 | `1-discussion.md:96-97` G-out-8／9；`1-discussion.md:132-133` Q12／Q13；`1-discussion.md:137-139` 圍欄仍禁方案檔；`notes/review-requirement-discovery-gaps.md:286-296` 不改允許集合＝讀不到。形狀 `[Assumption]`（4-spec） |
| F2 | **放寬討論白名單**為整個 `docs/`／任意附件；Fast 命中一律升 full | 少一次核准；互動風險零漏網 | 拆掉 anti-premature-convergence；小修全拖進訪談；Stage 1 已拒「規定了但讀不到」的反面——讀到不該讀的方案檔 | 高 | `1-discussion.md:118` 不把 ticket 解法當事實；`1-discussion.md:139` 只開事實入口；`notes/review-requirement-discovery-gaps.md:319` 純視覺可維持 fast |
| F3 | **只改 skill 句子**，不改 `devtalk-guard`；Fast 維持進 4-spec 才看「高風險人機互動」 | 零守衛迴歸 | B-1 重演「規定了但讀不到」；B-2 第一因就是 lane 已選完才分診 | 低 | `1-discussion.md:38-39` Fast 省略 1–3、風險寫在 4-spec；`1-discussion.md:243-246`；`hooks/devtalk-guard.sh` 現況只掃下游字眼（`1-discussion.md:38`） |

### 決策點：A-5 LIGHT
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| L | **Human verdict 一行**寫清角色／場景；ACCEPTED 只對該範圍有效。不做 Actor Coverage 全表。缺角色或場景的 ACCEPTED → 形狀牙紅 | 對準已裁 LIGHT 與 G-out-5；成本低 | 擋不住「錯的人按對的鈕」的代表性，只讓後讀者看得出來驗了誰 | 低 | `1-discussion.md:93` G-out-5；`1-discussion.md:104` 已裁 LIGHT；`1-discussion.md:115` 不做全表；`1-discussion.md:231-234` |
| T | **Actor Coverage 全表**（direct／proxy／not covered） | 代表性較完整 | owner 已裁本包不做；外部角色常無法直 Demo | 高 | `1-discussion.md:115`；`notes/review-requirement-discovery-gaps.md:25` A-5 LIGHT |
| N | **維持現況**只要求人類 attestation | 零改 | 人看不出驗了誰、驗了哪場；G-out-5 落空 | 低 | `1-discussion.md:33` 牙只守不是 Agent 代填；`1-discussion.md:161-164` AC-5 |

## 方案架構圖
[A] 同包教師+形狀牙(選定)
[G] 牙掛既有家族(選定)
[E] 狀態枚舉+擋G2(選定)
[D] 去向帳+回看附錄(選定)
[F] manifest+Fast分診(選定)
[L] verdict一行角色(選定)

## Decision
採 **A + G + E + D + F + L**：九條用同一 slug 落到既有模板／skill／完整範例，並用既有檢查家族的形狀牙守欄位與對稱措辭；不另造方法論、不拆包、不靠 no-build 清單假裝已修。結果是人能分辨工作結果與未定案解法、發現題不被錨定、主張有來源或帶期限、過期假設擋 G2、verdict 看得出角色／場景、痛點有去向、出貨後有回看、事實入口經核准、Fast 先做六問分診。欄位字面進 4-spec。本 hop 不改碼、不發明 G1 PASS。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| B no-build／只改指南 | 現況已是人工筆記；Stage 1 已寫「九條進指南、範例仍教解法」。原因是教師與牙，不是缺一張 checklist。 |
| C 拆 slug／分波 | Q2 已裁一包；拆開會讓 A-6／B-1 再漏一輪。 |
| K 語意黑名單牙 | 誤殺領域詞；A-2 對話無法從 md 還原。 |
| P 範例另開薄刀 | 本包當教師期間舊範例繼續教 dashboard-in-Goals。 |
| E2 維持二分+散文期限 | 第一因就是二分太粗；牙繼續只驗字樣。 |
| E3 新 Evidence ID 鏈 | Non-Goal；第二套編號。 |
| D2 另造 lookback 正本檔 | 無維護者；與 7-review／HISTORY 雙源。 |
| D3 只審頁列未處置、Stage 4 不對帳 | A-6 的消失發生在 2→4，不是發生在審頁。 |
| F2 放寬整棵 docs／命中一律 full | 拆圍欄；小修全拖進訪談。 |
| F3 只改句子、不改 guard、Fast 仍到 4 才分診 | 「規定了但讀不到」＋ B-2 原順序。 |
| T Actor Coverage 全表 | 已裁 LIGHT，本包不做。 |
| N 只留 attestation | G-out-5 落空。 |

## Rationale
九條的共同第一因不是「owner 不知道該問什麼」。owner 已經用 `notes/review-requirement-discovery-gaps.md` 人工記過缺口，模板卻繼續把通道寫進 Goal、把推薦答案寫進發現題、把痛點留在 Stage 1 自生自滅。B（process-only）重複這條已失敗的路，只是把筆記搬進 G1 清單。A 改的是採用者會抄的教師：模板、skill、完整範例。

牙必須停在形狀。K 用關鍵字猜「這句是不是解法／是不是誘導」，Stage 1 已標會誤殺、也還原不了訪談。G 延伸既有 `check-realworld`／`check-spec-gate`／`devtalk-guard`，守「欄位在、枚舉合法、過期紅、發現題措辭沒單邊漂」；主張是否真被來源支持，仍是 reviewer 的事。

證據層 E 比 E2 貴，但 E2 就是現況。不另發 ID（E3）是為了不養第二條鏈。去向用原文片段引用（D），lookback 掛在 7-review 這份本來就有人寫的 Exit，不新開無主檔。入口 F 保留圍欄、只開 owner 核准的事實路徑，並把 Fast 的六問移到選 lane 之前——命中不必一律 full，這是為了不把純視覺小修拖進訪談。A-5 停在一行角色／場景，因為代表性全表已被裁出本包。

## 既有脈絡
對帳快照（2026-09-13 tip `bcdfee1`，#260／#263 之後）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| Owner Call 九條 | A-1…A-4／A-6／A-7／B-1／B-2 = DO，A-5 = LIGHT；不重開 | 本檔只收 **HOW**；DO／LIGHT 當已核事實 |
| Stage 1 本 slug | `1-discussion.md` 仍 draft；Q4 寫不送 G1；Q7–Q14 `[>]` | 1-discussion 留當時說法；本檔改口。不回改正本討論 |
| 驗收雛形「從哪看」 | 模板／S4-accept 列畫面／端點／檔案／log；範例已鎖 dashboard | A-1：分欄＋不鎖通道；範例同 slug 改 |
| 發現題附推薦 | N3-probe 硬規則；完成＝兩輪無新問題 | A-2：題型分流；完成條件改覆蓋面 |
| Evidence／點頭 | `[Assumption]` 二分；認可＝已核事實；牙驗字樣 | E：就地枚舉＋來源欄；點頭不升格 |
| `[~]` 到 G2 | 合法終態；接手不看影響級 | E／A-4：四欄＋過期擋 G2 |
| Human verdict | 人類 attestation；不守角色／場景 | L：一行角色／場景 |
| Disposition | Stage 2 只收 Goals／AC／`[>]`；Stage 3 場景已有逐場牙 | D：Stage 1 高影響列同級保護 |
| Exit／lookback | shipped 即終點 | D：7-review 附錄四欄 |
| 討論白名單 | 長期記憶／specs／原始碼／已指名檔；guard 只掃下游字眼 | F：核准 manifest 放行事實；方案檔仍拒 |
| Fast lane | 省略 1–3；本 repo 有實例；互動風險寫在 4-spec | F：六問在選 lane 前 |
| STATUS Backlog「觀測前不動 Stage 1–4 模板」 | 他案觀測實驗用 | 不擋**本包**後續 Stage 6（本包就是九條落地）。本 PR 仍不改模板 |

### 選定落地圖（九 ID）

| ID | 裁決 | 教師落點（後續 Stage 6） | 牙（形狀，非語意） | 本 Decision 鎖定的結果 |
|---|---|---|---|---|
| A-1 | DO | `_templates/1-discussion.md` Goals／Requested solution 分欄；驗收雛形不鎖畫面／API／元件；`_templates/2-decision.md` 要求 no-build 適用性判定；`skills/dev-talk` S4-accept 不再把「從哪看」鎖成通道；完整範例同改 | 分欄與「未定案」節存在；不黑名單領域詞 | 人讀 Stage 1 能分開結果與構想 |
| A-2 | DO | `skills/dev-talk` N3-probe／S2-world：發現題禁推薦、裁決題可附；完成條件改必查面／反例／證據缺口，兩輪無新問題只當輔助 | skill／guide 對稱措辭不得單邊漂移 | 發現題出口本身無推薦答案 |
| A-3 | DO | Evidence 最小欄＋就地枚舉；S1-survey：點頭 ≠ 已核事實 | 重要列有來源或 Assumption；枚舉值合法 | 主張可重開來源或帶期限 |
| A-4 | DO | `[Assumption]`／`[~]` 四欄；4-spec 引用未驗假設 | 高影響且過期未驗 → G2 形狀檢查 exit ≠ 0 | 過期高影響假設擋 G2 |
| A-5 | LIGHT | `_templates/3-prototype.md` Human verdict 一行角色／場景 | ACCEPTED 缺角色或場景則紅；不做全表 | 後讀者答得出驗了誰、哪場 |
| A-6 | DO | Stage 2 Disposition 表；Stage 4 對帳 addressed→R/S | 高影響列 disposition 非空；addressed 有 R/S 落點 | 痛點不能無聲消失 |
| A-7 | DO | Stage 1 Problem 最小 baseline；Stage 2 Success 分 Delivery／Outcome；7-review Exit 附錄 lookback | 四欄都在才算留下回看 | 出貨後知道何時、用何來源、低於何值重開 |
| B-1 | DO | 事實 manifest ＋ skill 白名單；`devtalk-guard` 允許集合同步 | 核准路徑可讀；2／3／4／5／6／7 仍拒 | 事實進得來、方案檔仍進不去 |
| B-2 | DO | lane 選擇前六問；命中 → full／mini／OC | Fast 4-spec 無分診或命中無去向則紅 | 寫規格前已看過互動風險 |

### Q6 三條現場假設（Stage 2 對帳）

期限到本站。本 hop **不捏造**採用現場數字；對帳結果如下。過期未對帳才擋**本 slug 的 G2**；已對帳則設計當作為真，若為假，改範例仍正確（範例本身已示範舊病）。

| 假設 | 對帳 | 去向 |
|---|---|---|
| 採用現場仍照範例把解法寫進 Goal | 仍無採用專案 log；本 tree 範例 `example/contract-expiry-reminder/1-discussion.md` 已示範該形。**維持 Assumption**，風險=高 | 當作為真 → 範例同 slug 改（P 已拒）。若為假，改範例仍對齊 A-1 教師 |
| 現場訪談仍在發現題附推薦答案 | 仍無逐字稿；skill 現況仍要求附推薦。**維持 Assumption**，風險=高 | 當作為真 → 改 N3 題型分流。牙主要防未來漂移 |
| Fast 現場因檔數少而漏判互動風險 | 本 repo 已有省略 1–3 的實例（`docs/dev/engine-fence-masking/4-spec.md`）。採用現場是否踩過權限／等待誤標 = 仍無 log。**部分 Observed（本 repo）＋部分 Assumption（採用現場）** | 當作為真 → B-2 六問。本 repo 實例夠啟動，不依賴現場 log |

### 本檔 Real-world Disposition（A-6 狗糧；引用 Stage 1 原文片段）

| 引用 | 來源 | 去向 | 理由 |
|---|---|---|---|
| 發現被錨定 | Journey step 1 | addressed | A-2 題型分流 |
| 點頭當證據 | Journey step 2 | addressed | A-3 點頭不升格 |
| 痛點消失 | Journey step 3 | addressed | 本表即 D 的形狀 |
| 問題沒改善 | Journey step 4 | addressed | A-7 lookback |
| 互動風險晚露 | Journey step 5 | addressed | B-2 六問在 Stage 4 前 |
| owner 用審核筆記記缺口 | Workaround | addressed | 改教師，不再只靠筆記 |
| 現場證據靠記憶轉述 | Workaround | addressed | B-1 manifest |
| Fast 直接寫 4-spec | Workaround | addressed | B-2；不廢 Fast |
| 人口頭記「先問現況」但 N3 仍附推薦 | Workaround | addressed | A-2 |
| Fast 合法跳過 1–3 | Exception | intentionally unchanged | 保留 Fast；用分診補洞，不強制每案 full |
| A-5 不做 Actor Coverage 全表 | Exception | Non-Goal | 已裁 LIGHT |
| `[~]` 可把 Stage 1 標 approved | Exception | addressed | A-4 過期擋 G2 |
| Q6 三條現場假設 | Exception／Evidence | still-unverified | 上表已對帳；不捏造現場 log |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 欄位字面未釘，Stage 4 之前各寫各的 | 本檔只鎖枚舉名、四欄意圖、六問、disposition 五態、lookback 四欄。Markdown 標題／腳本掛載點進 4-spec（OC-1） |
| 形狀牙假綠（填了任意數字／任意來源句） | SC 寫明：牙只守存在與枚舉；「來源是否支持主張」「指標是否代表改善」是 reviewer。不把填數字當有效 outcome |
| A-1 黑名單誘惑回流 | K 進 Rejected；翻案回本站 |
| no-build 誘惑（「先出清單再改模板」） | B 進 Rejected；本包就是改教師 |
| 拆包誘惑 | C 進 Rejected；Q2 已裁 |
| B-1 只改散文、guard 未改 | F 綁定允許集合同步；F3 已拒 |
| Fast 命中被做成一律 full | F 明寫三去向；F2 已拒 |
| 本 hop 被當成已過 G1 | `verdict` 空、`status` draft；確認紀錄不寫 PASS |
| feature branch 手改 STATUS／HISTORY | 流程層 OC-3：本 PR 不碰表列 |
| Backlog「觀測前不動模板」被拿來擋本包 Stage 6 | OC-4：該凍結不適用本 slug 的後續實作站；本 PR 仍不改模板 |
| Q6 假設永遠無現場 log | 已對帳；設計當作為真；G2 不因「沒有採用者訪談」再擋，因本 tree 範例與 skill 已足夠啟動 |

## Success Criteria
- SC-1(G-out-1／A-1)：一份把「我要 dashboard」寫進 Goals、沒有 Requested solution 分欄的 Stage 1 對照稿，指定形狀檢查 exit ≠ 0。本 slug 自己的 1-discussion 與改後範例：Goals 不指定畫面／API／元件，構想在未定案欄。不是靠 dashboard 詞黑名單。
- SC-2(G-out-2／A-2)：落地後的 skill／guide，發現題規則含「禁推薦」、裁決題規則含「可附選項／推薦」；刪掉其中一邊的對照稿，靜態守衛 exit ≠ 0。不要求從最終 md 還原整場訪談。
- SC-3(G-out-3／A-3)：高影響主張列能指出 Observed／Reported／Inferred／Assumption／Conflict 之一，以及來源摘要或 Assumption 期限。只有「使用者點頭」當來源的對照稿不得當已核事實。
- SC-4(G-out-4／A-4)：一份 4-spec 引用高影響 Assumption、驗證期限已過且未改 Observed／Reported、也無 OC 接受風險 → G2 形狀檢查 exit ≠ 0。未過期或已驗的對照稿 exit 0。
- SC-5(G-out-5／A-5)：一筆 ACCEPTED 缺角色或場景 → 形狀檢查 exit ≠ 0。有角色＋場景的對照稿 exit 0。不要求 Actor Coverage 全表。
- SC-6(G-out-6／A-6)：Stage 1 高影響痛點／workaround／exception 在 Stage 2 Disposition 都有非空去向；標 addressed 者在 Stage 4 至少落到一條 R/S。本檔上表九列不得在後續 4-spec 消失（消失＝該 S 紅或回本站）。
- SC-7(G-out-7／A-7)：本 slug shipped 時，7-review Exit 附錄有日期／owner／來源／「低於何值重開」。缺任一欄不得勾 shipped。不要求 G3 當日已量到結果下降。
- SC-8(G-out-8／B-1)：owner 核准的去識別化事實路徑，討論 session 讀得到事件／行為／結果；同場讀 `2-decision.md`／`4-spec.md` 仍被擋。未改 `devtalk-guard` 允許集合不得宣稱 B-1 完成。
- SC-9(G-out-9／B-2)：Fast 4-spec 缺六問分診，或六問有命中卻無 full／mini／OC → 指定檢查 exit ≠ 0。六問全否且已有 approved spec 的純視覺對照稿可 fast。
- SC-10(Non-Goal)：無第二條 Journey／Actor ID 鏈；無 A-5 全表；九 ID 仍同一 slug；本 PR 未改 `_templates/`／`skills/`／`example/`／STATUS／HISTORY；本檔 `verdict` 不是 PASS。

## Scope & Non-Goals(定稿)
- In：A 同包落地形；G 形狀牙掛既有家族＋範例同 slug；E 就地枚舉＋過期擋 G2；D Disposition 引用原文＋ lookback 落 7-review 附錄；F manifest＋Fast 六問三去向；L verdict 一行；Q6 對帳；Q7–Q14 在本檔收口到「層」與「形狀意圖」（字面進 4-spec）；本檔 Disposition 狗糧。
- Out：B／C／K／P／E2／E3／D2／D3／F2／F3／T／N；重開九條 DO／LIGHT；Actor Coverage 全表；新 ID 鏈；另造 lookback 正本檔；本 hop 改 `_templates/`／`skills/`／`example/`／守衛；本 hop 改 STATUS／HISTORY；本 hop 發明 G1 PASS；本 hop 開 4-spec；`integration-before-verdict`；發版／bump plugin。

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | 形狀牙**沿用既有家族**（`check-realworld`／`check-spec-gate`／`devtalk-guard` 之一或其延伸），不另造第二套發現缺口工具。使用者 brief 只鎖「落到模板／skill／範例／守衛」；「沿用既有家族」是 owner 延伸。欄位字面／檔名本 hop 不鎖 | 另造家族靠近第二套方法論；現況已有 real-world／spec-gate／devtalk 牙，缺的是射程 | `1-discussion.md:127` Q7；`1-discussion.md:243-246` 部分牙。掛哪一支的精確函式 `[Assumption]`（4-spec） | 要新入口／新腳本；與「不另造方法論」重審 | 待人審 |
| OC-2 | 本 Stage 2 **先填** Disposition 表（上列），當作 A-6 選定形狀的狗糧。使用者只被問到「要有 ledger」；「本決策檔就先引用 Stage 1 原文」是延伸 | AC-6 點名本檔 Journey 三列；空著等模板改＝本包自己先消失 | `1-discussion.md:168` AC-6；`1-discussion.md:130` Q10。五態中文標籤 `[Assumption]` | 刪表或改成等 Stage 6 才出現 ledger | 待人審 |
| OC-3 | 本 feature branch **不**改 `docs/dev/STATUS.md` 表列、**不**跑 `history-append.sh`。Stage 欄留 main 現況。標**流程層** | 母版表列只在整合分支維護；brief 明示本 PR 不改 STATUS／HISTORY | `docs/dev/STATUS.md:10-26`；`1-discussion.md:137`；本 hop brief | 本 PR 帶表列改動，與並行 session 互蓋 | 待人審 |
| OC-4 | 本 slug **後續 Stage 6** 被授權改 Stage 1–4 模板／skill／範例／牙。STATUS Backlog「觀測實驗前不動 Stage 1–4 模板」**不適用本包**（本包就是那九條落地）。本 PR 仍不改那些檔。使用者只被問到「進 Stage 2」；「觀測凍結不擋本包實作站」是延伸。標**流程層** | 若不收這條，Stage 6 會跟 Backlog 句互斥，九條無法落地 | `docs/dev/STATUS.md:50` 觀測凍結；`docs/dev/STATUS.md:51` 九條已指向本 slug；`1-discussion.md:41` 受影響面＝後續才動 | 本包變成只能改指南＝B，已拒 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 本 hop 不 bump plugin、不改產器、不手包 html-shell。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口成 Decision。不把 owner「進 Stage 2」寫回 1-discussion `status: approved`。
- 第 3 站依 Decision 執行；本檔 Owner Calls **沒有**「跳過 Stage 3」紀錄。觸發判定留給第 3 站開場。
- 審頁用 `scripts/build-stage2-html.py --action`，不把第 2 站審頁塞進 `build-gate-twin.py` STAGES。
- Evidence 枚舉五值與 disposition 五態的英文 key 進 4-spec；本檔中文標籤只鎖意圖。
- Fast mini real-world delta 至少含 Actor、實際工作影響、權限／等待／例外、代表性驗證方式（Requested solution 已列；欄位字面 4-spec）。

## ADR 晉升檢查
- 難逆轉:否（G3 前可改本檔 Decision／OC；教師尚未落地）
- 反直覺:是（七關全綠仍可能解錯問題；只改指南不夠；不另發 ID 反而比較能對帳）
- 真 trade-off:是（同包改教師 vs process-only vs 拆包；形狀牙 vs 語意黑名單）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-13 | owner 核准 Stage 1 方向並明示進 Stage 2。brief 指定：比較 2–3 落地 HOW、含 no-build、覆蓋九 ID、A-5 可薄、不重開 DO／LIGHT、不改模板／STATUS。六個決策點對應該鎖板（落地形／教師與牙／證據假設／去向回看／入口 Fast／A-5）。
- Stage 1 改口 | 2026-09-13 | 1-discussion 仍 draft、Q4 寫「只 Stage 1 不送 G1」、Q7–Q14 仍 `[>]`。本檔改口為 Decision，並為 Q6 做對帳、為 Q7–Q14 收口到層與形狀意圖。不回改正本討論。
- Q6 對帳 | 2026-09-13 | 三條現場假設仍無採用者 log；本 tree 範例與 skill 已足夠當作為真。見「Q6 三條現場假設」。不擋本站送審；本 slug G2 不再以「沒對帳」為由擋這三條。
- 自檢七掃 | 2026-09-13 | ①優劣皆有依據欄；②G-out-1～9 進 Decision／落地圖，漏項進 Non-Goals；③Q7–Q14 `[>]` 皆有著落；④SC-1～10 可量測；⑤Rejected 無空棄因；⑥六決策點由 owner Stage 2 brief 確認，OC-1／OC-2 承接牙家族與本檔 ledger，OC-3／OC-4 流程層；lookback 落 7-review 是 Decision D 不是自判；⑦既有脈絡表是對帳不是外移 schema。圖上 A／G／E／D／F／L 標選定，Rejected 未上圖。
- G1 | 待人審 | `verdict` 空。全勾不算 PASS。審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審（有記錄的最後手段）。
