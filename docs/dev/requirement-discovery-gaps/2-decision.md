---
feature: requirement-discovery-gaps
stage: 2-decision
status: in-review
verdict:
owner: rick
reviewers: []
updated: 2026-09-13
---

# 2. 收斂 — 九條制度缺口怎麼落地

> 把 `1-discussion.md` 的發散收成 Decision。本 hop **不宣稱 G1 PASS**：`verdict` 空、`status` in-review、Owner Calls 全「待人審」。不重開九條 DO／LIGHT。不改 `_templates/`／`skills/`／`example/`／STATUS／HISTORY。
> owner 已核 Stage 1 方向（#260）：一包、full、A-5 LIGHT、其餘 DO。本檔只收 Q7–Q14 的落地形，並對帳 Q6 期限。1-discussion 留當時「只 Stage 1、不送 G1」原文。

## Approaches Considered

### 決策點：落地深度（九條共用：牙 vs 散文 vs 語意硬閘）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| DEPTH-A | **形狀牙 + reviewer**。可機械的只守欄位／分欄／枚舉／期限／去向非空；Goal 是否偷帶解法、發現題是否誘導，留給自檢與 G1／G2 人審 | 對準九條「只能部分機械化」；不假裝關鍵字能判語意；既有牙家族可延伸射程 | 人審仍可能放水；形狀綠 ≠ 問題解對 | 中 | `notes/review-requirement-discovery-gaps.md:69-73` A-1 部分機械化；`:98-102` A-2 不值得硬 gate；`:133-136` A-3 欄位可機械、來源是否支持仍是人；`1-discussion.md:243-246` 只改散文現場仍照範例走偏。成本 `[Assumption]` |
| DEPTH-B | **no-build／process-only**：指南／筆記加清單，靠 reviewer 與 owner 記憶執行；不改模板、skill、範例、守衛 | A-1 要求原因仍可能由流程／政策解決時要比較本案；最短；零迴歸 | 現制牙只驗章節／`[Assumption]`／「訪談」字樣；官方範例仍教把 dashboard 寫進 Goal；B-1 會變成「規定了但讀不到」 | 低 | `notes/review-requirement-discovery-gaps.md:22` Stage 2 適用時比 no-build；`1-discussion.md:99-100` 同句；`scripts/check-realworld.sh:88-91` 牙只驗字樣；`example/contract-expiry-reminder/1-discussion.md:62-65` Goals 已鎖登入／點擊；`notes/review-requirement-discovery-gaps.md:293-296` 只改散文不改允許集合 |
| DEPTH-C | **語意硬閘**：Goal 禁 dashboard／API 等詞；從最終 md 還原誘導題；過期假設靠全文關鍵字猜影響級 | 看起來最硬 | A-1 已警告黑名單誤殺領域詞；A-2 對話語意無法從 md 還原；假綠或誤殺都會讓採用者繞開牙 | 高 | `notes/review-requirement-discovery-gaps.md:69-73` 禁 dashboard／API 黑名單；`:98-102` 不值得假裝硬 gate；誤殺率 `[Assumption]` |

### 決策點：落地面與範例時機（Q7＋Q14）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| SURF-A | **同一 slug** 在 G2 後改四層：模板 + `dev-talk`／`dev-flow` skill 節點 + 既有牙家族（`check-realworld`／`check-spec-gate`／`devtalk-guard`）+ 完整範例 `contract-expiry-reminder` | 模板說結果、範例不再教解法；Q7／Q14 一次收口；採用者抄範例不會走偏 | 與 Backlog「觀測實驗前不動 Stage 1–4 模板」打架（見 OC-3）；Diff 較大 | 中 | `1-discussion.md:109` 同步改正完整範例；`:127` Q7；`:134` Q14；`example/contract-expiry-reminder/1-discussion.md:62-65` 與 `:83-103` 仍教 dashboard／卡片／URL；`docs/dev/STATUS.md:50` 觀測實驗禁改 Stage 1–4 模板 |
| SURF-B | **範例另開後片**；本 slug 只改模板／skill／牙 | 本包 Diff 較小；觀測實驗可先看舊範例 | 模板說結果、範例仍教解法的窗口拉長；Q6 的教師還活著 | 低 | `1-discussion.md:126` Q6 假設採用者照範例走；`1-discussion.md:249` 「改模板就夠」不成立。窗口傷害 `[Assumption]` |
| SURF-C | **另造第二套守衛家族**／新入口腳本一次吃九條 | 入口唯一、好講 | 第二套方法論；與現有 `check-realworld`／`check-spec-gate`／`devtalk-guard` 雙源會漂；靠近 DEPTH-C 的過度機械化 | 高 | `scripts/check-realworld.sh:71-91` 與 `scripts/check-spec-gate.sh:16-30` 已是形狀牙入口；`hooks/devtalk-guard.sh:16-21` 已守寫入圍欄。雙源漂 `[Assumption]` |

### 決策點：證據與過期假設（A-3／A-4，Q8／Q9）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| EV-A | **就地狀態標**（Observed／Reported／Inferred／Assumption／Conflict）+ 假設四欄（若為假影響什麼／級／怎麼驗／何時誰驗）+ **既有 G2 形狀檢查延伸**：高影響過期且無 Owner Call → `check-spec-gate` 拒；不新增主張 ID 鏈 | 對準 G-out-3／G-out-4；G1 抽查沿引用回來源；牙延伸現有 Gate 而不是新入口 | 影響級仍是人判；欄位形狀要進 4-spec | 中 | `notes/review-requirement-discovery-gaps.md:123-131` 候選枚舉與點頭不升格；`:155-167` 四欄＋high 必 resolved 或 OC；`1-discussion.md:128-129` Q8／Q9；`1-discussion.md:116-117` 不新增第二 ID 鏈；`scripts/check-spec-gate.sh:32-37` 已是 G2 Gate。欄位字面 `[Assumption]`（4-spec 再釘） |
| EV-B | **主張／Journey 第二 ID 鏈**，每個 claim 有穩定 ID，S 機械引用 | 推翻假設時好列受影響 S | Stage 1 Non-Goals 與審核區都禁第二鏈；討論／規格多一層編號稅 | 高 | `1-discussion.md:117` 不新增第二條 Journey／Actor ID 鏈；`notes/review-requirement-discovery-gaps.md:125` 不新增 Journey／Actor 第二 ID 鏈 |
| EV-C | **只寫 G1／G2 checklist 散文**，不加欄、不加牙 | 最短 | A-4 失效模式原樣：`[~]` 合法走到 G2；牙繼續只驗「有 Evidence 字樣」 | 低 | `_templates/1-discussion.md:82-86` `[~]` 是合法終態；`_templates/2-decision.md:35-37` 接手只核 status 與三態；`scripts/check-realworld.sh:88-91` 只驗字樣 |

### 決策點：去向帳與回看（A-6／A-7，Q10／Q11）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| DISP-A | Stage 2 加 **Real-world Disposition**：高影響痛點／workaround／exception **引原文片段**（不另發 ID）標 addressed／unchanged／Non-Goal／另開 slug／仍待驗。Stage 4：addressed 至少一條 R／S；其餘落到 Out／Known limit／後續 slug。**lookback** 四欄寫進 7-review Exit；回看**結果**只准 `history-append.sh` 追加 HISTORY | 對準 G-out-6／G-out-7；沿用 Stage 3 場景對帳牙的負向 fixture 思路；不另造永久檔族 | G1 twin 頂區「未處置列」是後續產器改動，本 slug 實作站才做 | 中 | `notes/review-requirement-discovery-gaps.md:220-231` ledger 候選；`:253-262` lookback 落 HISTORY 或 7-review 附錄、不要無維護者的新檔；`1-discussion.md:130-131` Q10／Q11；`scripts/check-realworld.sh:215-232` 已有 Stage 3 逐場點名牙；`_templates/7-review.md:316-342` Exit 現無回看四欄；`docs/dev/STATUS.md:36-42` HISTORY 只准 writer |
| DISP-B | **第二條 Journey ID 鏈** + **獨立 lookback 檔族**（例如 `docs/dev/<slug>/8-lookback.md`） | 對帳好寫腳本 | 禁第二鏈；新檔族無維護者；Exit 已超載還再平行一份 | 高 | `1-discussion.md:117` 禁第二鏈；`notes/review-requirement-discovery-gaps.md:261-262` 不要另造永久文件卻沒維護者 |
| DISP-C | **只在審頁頂區提醒**未處置列；Stage 4 不對帳；lookback 口頭／行事曆 | 本包幾乎不改 4／7 | 痛點仍可在 2→4 靜默消失；G3 綠仍不能證明問題改善——現況原樣 | 低 | `_templates/2-decision.md:35-37` 只從 Goals／AC／`[>]` 提煉；`_templates/4-spec.md:72-75` 對帳 Stage 3 不對帳 Stage 1 痛點；`_templates/7-review.md:316-342` Exit 停在 shipped |

### 決策點：事實入口與 Fast 分診（A-2／B-1／B-2，Q12／Q13）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| TALK-A | **發現題禁推薦、裁決題可附**（skill／guide 對稱措辭 + 靜態牙防一邊漂移，不對 Interview Log 做硬 gate）。**事實型 evidence allowlist**：owner 先核准來源／路徑才讀；**改 `dev-talk` 讀取允許集合**（及對等圍欄），下游 2／3／4／5／6／7 仍禁。**lane 選擇前**六問（下一步／權限／等待語意／交接／系統外／中斷恢復）；全否且已有 approved spec 才可 fast；命中由 owner 裁升 full／mini real-world delta／OC 接受；純視覺不改語意維持 fast | 對準 G-out-2／8／9；B-1 不會「規定了但讀不到」；B-2 把分診移到選 lane 之前 | 允許集合形狀未釘；mini delta 欄位進 4-spec | 中 | `skills/dev-talk/nodes/N3-probe.md:22-23` 現況每題附推薦；`:41` 完成條件=兩輪無新問題；`skills/dev-talk/SKILL.md:17-21` 讀取白名單擋未指名文件；`hooks/devtalk-guard.sh:16-21` 只掃寫入洩漏、不管事實入口；`skills/dev-flow/SKILL.md:34-36` Fast 從 4-spec 起跑；`_templates/4-spec.md:266-269` 高風險人機互動寫在 4-spec、lane 已選完；`1-discussion.md:132-133` Q12／Q13；`notes/review-requirement-discovery-gaps.md:284-296` 核准後才讀。允許集合字面 `[Assumption]` |
| TALK-B | **只改 skill 句子**、不改允許集合；分診**只寫進 4-spec**（lane 已選定後補填） | 最短碼；Fast 模板已有 Operational Context | B-1 讀不到未指名 SOP／ticket；B-2 順序病仍在——檔數少已進 fast，六問變成事後補紙 | 低 | `1-discussion.md:244-246` 只改散文會「規定了但讀不到」；`docs/dev/engine-fence-masking/4-spec.md:11-12` 本 repo 已有 Fast 省略 1–3。現場漏判 `[Assumption]`（Q6 姊妹條） |
| TALK-C | **整夾文件可列可搜**；六問任一命中**強制升 full** | 證據最多；互動風險零漏網 | 拆掉 anti-premature-convergence 的上游圍欄；小修全拖進訪談，違反 B-2「純視覺可維持 fast」 | 高 | `skills/dev-talk/SKILL.md:17-21` 圍欄擋住下游方案是合理的；`notes/review-requirement-discovery-gaps.md:316-319` 命中不必一律 full；`:319` 純視覺可維持 fast |

## 方案架構圖
[DEPTH-A] 形狀牙+人審(選定)
[SURF-A] 同slug改四層(選定)
[EV-A] 就地狀態+G2牙(選定)
[DISP-A] ledger+Exit回看(選定)
[TALK-A] 核准入口+六問(選定)

## Decision
採 **DEPTH-A + SURF-A + EV-A + DISP-A + TALK-A**：九條一包、不重開 DO／LIGHT；落地是「形狀牙延伸既有家族 + 人審語意」，不是 no-build 備忘、也不是語意硬閘。G2 後同一 slug 改模板、skill 節點、既有牙（`check-realworld`／`check-spec-gate`／`devtalk-guard` 讀取允許集合）、以及完整範例；不另造第二套守衛、不新增 Journey／Actor ID 鏈。A-5 停在 Human verdict 一行角色／場景。本 hop 只交本檔 + Stage 2 審頁，不改模板、不宣稱 G1 PASS。

## 九條落地對帳
選定案怎麼接九條（不重開裁決）。審頁 Decision 卡只留上一句；本表給讀 md 的人對帳。

| ID | 裁決（不重開） | 落在哪一案 | 後續站要釘的形 |
|---|---|---|---|
| A-1 | DO | DEPTH-A + SURF-A | Goals／Requested solution 分欄；驗收雛形不鎖畫面／API／元件；Stage 2 模板要求 no-build 適用性判定（不合理須註明）；範例同步改口。**不**做詞黑名單 |
| A-2 | DO | TALK-A | 發現題禁推薦、裁決題可附；完成條件改必查面／反例／證據缺口；靜態牙防一邊漂移。**不**對逐字稿做硬 gate |
| A-3 | DO | EV-A | 就地五態；Evidence 最小欄（來源類型／as-of／範圍／支持哪段／限制）；點頭 ≠ 升格 |
| A-4 | DO | EV-A | 假設四欄；高影響過期且無 OC → 既有 G2 形狀檢查拒；S 引用仍在的假設 |
| A-5 | LIGHT | SURF-A（只一行） | Human verdict 寫清角色／場景。**不做** Actor Coverage 全表 |
| A-6 | DO | DISP-A | Stage 2 disposition ledger 引片段；Stage 4 addressed→R／S |
| A-7 | DO | DISP-A | Exit 四欄 lookback（日期／owner／來源／低於何值重開）；結果 HISTORY 追加 |
| B-1 | DO | TALK-A | owner 核准的事實入口；改允許集合；仍禁 2／3／4／5／6／7；ticket 解法建議不當事實 |
| B-2 | DO | TALK-A | 選 lane 前六問；命中→full／mini／OC；純視覺不改語意可 fast |

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| DEPTH-B no-build | 流程備忘已存在（本審核區）；痛仍在——牙只驗字樣、範例仍教解法、事實入口讀不到。A-1 要比本案，比完不採用 |
| DEPTH-C 語意硬閘 | 黑名單誤殺領域詞；誘導題無法從最終 md 還原；假綠／誤殺 |
| SURF-B 範例另開 | 教師與模板分裂；Q6 的走偏路徑繼續活 |
| SURF-C 第二套牙家族 | 雙源；現有 `check-realworld`／`check-spec-gate`／`devtalk-guard` 已是入口 |
| EV-B 第二 ID 鏈 | Non-Goal；審核區已拒 |
| EV-C 只寫 checklist | `[~]` 與「有 Evidence 字樣」原樣走到 G2 |
| DISP-B 新 ID + 新 lookback 檔 | 禁第二鏈；無維護者的新檔族 |
| DISP-C 只提醒不對帳 | A-6／A-7 失效模式原樣 |
| TALK-B 只改句子 | 「規定了但讀不到」+ 分診仍在 lane 選定之後 |
| TALK-C 開整夾／一律 full | 拆上游圍欄；把小修拖進訪談 |

## Rationale
九條要修的不是「文件沒寫過這句話」。審核區 2026-09-12 已經寫完 Owner Call；Stage 1 也已經用結果句寫 Goals。還活著的病是**教師與牙的射程**：`check-realworld` 綠的是章節表頭與 `[Assumption]` 字樣；`N3-probe` 仍命令「每題附推薦答案」；官方範例 Goals 鎖登入／點擊、AC 鎖 dashboard；Fast 用檔數起跑，互動風險寫在 4-spec。DEPTH-B 重複「備忘已寫所以結束」。DEPTH-C 用關鍵字假裝能判語意，審核區已點名不要。

DEPTH-A 把機械力用在「欄在不在、分欄在不在、期限在不在、去向非空、允許集合是否真的放得進核准過的事實」，把「這句 Goal 算不算解法」「這題算不算誘導」留給人。SURF-A 同一 slug 改範例，因為 Stage 1 已確認「改模板就夠」不成立。EV-A／DISP-A 用就地標記與原文片段，避開第二 ID 鏈。TALK-A 同時修三個順序病：發現題錨定、事實被圍欄擋住、Fast 先選 lane 再問互動。

A-1 的 no-build 比較落在 DEPTH-B：原因確實可能是「reviewer 再嚴一點、owner 用筆記盯」。本 tree 對帳後，no-build 不夠——官方範例與現有牙會繼續教舊形。不合理硬塞的是 DEPTH-C，不是 DEPTH-B；DEPTH-B 有比、有棄因。

## 既有脈絡
對帳快照（2026-09-13 tip `bcdfee1`，#260／#263 之後）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| Owner Call 九條 | 2026-09-12 已裁；#260 Stage 1 一包落地 | 不重開；本檔只收落地形 |
| `_templates/1-discussion.md` | Stage 1「不做決定」；驗收雛形「從哪看」列畫面／API／檔／log | A-1 改分欄與觀測通道；本 hop 不動 |
| `skills/dev-talk/nodes/N3-probe.md` | 一次一題、附推薦；完成=兩輪無新問題 | A-2 改發現／裁決分流 |
| Evidence／real-world 牙 | 二分 `[Assumption]`；牙驗字樣 | EV-A 延伸形狀，不另造入口 |
| `check-spec-gate.sh` | G2 形狀 Gate（觀測欄／Profile／模糊詞／DD） | A-4 過期假設掛這裡 |
| Human verdict | 人類 attestation；不守角色／場景 | A-5 LIGHT 加一行 |
| Stage 2／4 對帳 | 只吃 Goals／AC／`[>]`／Stage 3 場景 | DISP-A 補 Stage 1 痛點列 |
| Exit Checklist | 出貨前驗證；無回看四欄 | A-7 加 lookback，結果走 HISTORY writer |
| `dev-talk` 白名單 | 長期記憶／specs／源碼／已指名檔 | B-1 加核准後的事實入口 |
| Fast lane | 省略 1–3；本 repo `engine-fence-masking` 已走 | B-2 把六問移到選 lane 前 |
| 完整範例 | Goals／AC 已鎖解法通道 | SURF-A 同 slug 改口 |
| STATUS Active | 本 slug 在 1-discussion；G1⬜ | 本 branch 不改正本（OC-2） |
| STATUS Backlog | 觀測實驗前不動 Stage 1–4 模板 | OC-3：本 Stage 2 PR 不動；G2 後本 slug 才准改 |

### Q6 與姊妹 Assumption 對帳（期限＝本站）
Stage 1 三條高影響 Assumption 期限都是「Stage 2 對帳，過期擋 G2」。本站能驗／不能驗：

| 假設 | 本站查證 | 狀態 |
|---|---|---|
| 採用現場仍照範例把解法寫進 Goal（Q6） | 無採用專案 log／訪談。**能驗的是教師**：範例 Goals 鎖登入／點擊／一眼可見，AC 鎖 dashboard／卡片／URL | 採用者行為仍是 Assumption（高）。教師＝Observed。接受採用者未驗風險＝OC-1；緩解＝SURF-A 改範例 |
| 現場訪談仍在發現題附推薦 | 無逐字稿。**能驗的是規則**：`N3-probe` 仍命令附推薦 | 現場行為仍 Assumption（高）。規則＝Observed。緩解＝TALK-A |
| Fast 現場因檔數少漏判互動風險 | 採用現場無 log。**能驗的是本 repo**：`engine-fence-masking` 合法省略 1–3；4-spec 才列高風險人機互動 | 採用者漏判仍 Assumption（高）。順序病＝Observed。緩解＝TALK-A |

未把「採用者一定照抄」升成 Observed。未驗部分不擋本站送審，但必須由 OC-1 明示接受，否則 A-4 對本 slug 自己不成立。

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 形狀牙變「有欄就綠」，Goal 仍偷帶解法 | DEPTH-A 明寫語意留給 G1／G2；禁 DEPTH-C 黑名單。4-spec 可加負向 fixture（故意把 dashboard 寫進 Goals）給 reviewer 抽查，不當硬 gate |
| B-1 只改句子、實作時忘了改允許集合 | TALK-B 進 Rejected；SC-8 要「核准後讀得到 + 方案檔仍擋」。允許集合與圍欄同一 T |
| 過期假設牙誤殺 draft／低影響 `[~]` | 牙只打高影響 + 已過期限 + 無 OC；影響級仍是人標。欄位形狀 4-spec |
| SURF-A 污染 Backlog 觀測實驗 | OC-3：本 PR 零模板改動；G2 後才改 Stage 1–4。觀測可用本 slug 當第一條真實 full lane，或延後 |
| 範例改口牽動 fixture／real-world 牙 | Stage 6 把 `example/contract-expiry-reminder` 與 `check-realworld` 衍生斷言列進同一 T |
| Q6 採用者假設為假（沒人抄範例） | 仍要改範例——教師自己錯是 Observed。OC-1 只接受「現場無 log」這一截 |
| 有人把本 hop 當成已過 G1 | `verdict` 空；OC 待人審；翻案回本站，不在 4-spec 用 DD 覆寫 |
| feature branch 手改 STATUS | OC-2 流程層：不跑 `status-update.sh` |
| Stage 3 被默跳 | 本檔無「跳過 Stage 3」字樣。觸發判定是第 3 站第一動，不在本 hop 代決 |

## Success Criteria
- SC-1(G-out-1／A-1)：落地後，模板與完整範例的 Goals 與 Requested solution 分欄；範例 Goals 不再指定登入／點擊／dashboard。一份故意把「我要 dashboard」寫進 Goals 的對照稿，人能指出它違規；指定形狀檢查不得只靠 dashboard／API 黑名單紅。本 2-decision 含 DEPTH-B no-build 列與棄因。
- SC-2(G-out-2／A-2)：`N3-probe`（或後繼節點）與指南同時有「發現題禁推薦」與「裁決題可附」。單一編輯刪掉其中一邊 → 指定靜態檢查 exit ≠ 0。不要求從 Interview Log 還原誘導題。
- SC-3(G-out-3／A-3)：高影響主張旁要嘛有可重開來源，要嘛有 Assumption + 期限；「使用者點頭」不得單獨當來源。缺欄的 Evidence 形狀檢查 exit ≠ 0。
- SC-4(G-out-4／A-4)：4-spec 含已過期限的高影響 Assumption、且無 Owner Call 接受 → `check-spec-gate.sh`（或明文掛在同一家族的延伸）exit ≠ 0。有 OC 或已驗轉 Observed／Reported 的對照稿 exit 0。
- SC-5(G-out-5／A-5)：ACCEPTED Human verdict 本文一行內可見角色與場景。無 Actor Coverage 全表。本包範例／模板不得新增該全表。
- SC-6(G-out-6／A-6)：Stage 1 高影響痛點／workaround／exception 在 Stage 2 ledger 都有去向；標 addressed 的在 Stage 4 至少一條 R／S。少一條去向的對照稿指定檢查 exit ≠ 0。
- SC-7(G-out-7／A-7)：shipped 的 7-review Exit 有 lookback 四欄（日期／owner／來源／低於何值重開）。缺任一欄不得勾 Exit。回看結果若寫入版本庫，只經 `history-append.sh`。
- SC-8(G-out-8／B-1)：owner 核准的去識別化事實來源讀得到事件／行為／結果；同場讀 `2-decision`／`4-spec` 仍被擋。未改允許集合只改 skill 句子 = 本項未完成。
- SC-9(G-out-9／B-2)：進 Stage 4 前六問都有答。Fast 且六問未收束 → 不得當已完成早期分診。命中卻無 full／mini／OC → 指定檢查拒。純視覺、不改語意的對照案可維持 fast。
- SC-10(Non-Goal)：未重開九條 DO／LIGHT；未新增 Journey／Actor ID 鏈；未混進 `integration-before-verdict`；本 PR 未改 STATUS／HISTORY／`_templates/`；本檔 `verdict` 空（不是 PASS）。

## Scope & Non-Goals(定稿)
- In：DEPTH-A／SURF-A／EV-A／DISP-A／TALK-A；九條落地對帳；Q7–Q14 收口方向；Q6 對帳 + OC-1 接受未驗採用者行為；本檔自帶 Real-world Disposition（吃自己的 A-6）；本 hop 審頁。
- Out：DEPTH-B／C、SURF-B／C、EV-B／C、DISP-B／C、TALK-B／C；重開 DO／LIGHT；A-5 Actor Coverage 全表；第二 ID 鏈；新 lookback 檔族；整夾掃描；一律升 full；本 hop 改模板／skill／範例／守衛／STATUS／HISTORY；本 hop 實作牙；本 hop 宣稱 G1 PASS；`#196`／gate-twin Backlog；plugin bump。

## Real-world Disposition
本檔先按 A-6 把 Stage 1 高影響列標去向（引片段，不另發 ID）。後續 4-spec 對 addressed 落 R／S。

| 引用（Stage 1 片段） | 去向 | 理由 |
|---|---|---|
| Journey「發現被錨定」 | addressed | TALK-A／A-2 |
| Journey「點頭當證據」 | addressed | EV-A／A-3 |
| Journey「痛點消失」 | addressed | DISP-A／A-6（本節即樣張） |
| Journey「問題沒改善」 | addressed | DISP-A／A-7 |
| Journey「互動風險晚露」 | addressed | TALK-A／B-2 |
| Workaround「人工筆記盯缺口」 | addressed | 本 slug 取代筆記施工 |
| Workaround「證據靠眼前記憶」 | addressed | TALK-A／B-1 |
| Workaround「Fast 直接寫 4-spec」 | addressed | TALK-A 把六問移到選 lane 前；不廢 Fast |
| Exception「Fast 合法跳過 1–3」 | intentionally unchanged | B-2 加分診，不取消 Fast |
| Exception「A-5 不做 Actor Coverage」 | intentionally unchanged | LIGHT 不重開 |
| Exception「`[~]` 可走到 G2」 | addressed | EV-A／A-4 |
| Q6 採用者照範例走 | 仍待驗證 | OC-1 接受；教師本身 Observed→SURF-A |

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | 接受 Q6 與兩條姊妹 Assumption 的**採用者行為**尚未 Observed。本站只把「範例是錯教師／N3 仍命令附推薦／Fast 省略 1–3」升成 Observed。未驗截的落點＝SURF-A 改範例 + DEPTH-A 形狀牙。使用者只被問到九條怎麼落地；「接受無現場 log 繼續」是 A-4 期限到本站的風險門 | 期限＝Stage 2；無採用專案 log 不能假裝已驗。不接受則本 slug 自己被 A-4 擋、G2 開不了 | `1-discussion.md:126` Q6；`:77-79` 三條 Exception；`:251` Q6 過期擋 G2。採用者行為 `[Assumption]` | 停到有現場 log，或改口「採用者假設已 Observed」 | 待人審 |
| OC-2 | 本 feature branch **不**跑 `status-update.sh`／`history-append.sh` 改正本。本 PR 不改 STATUS／HISTORY／`_templates/`。標**流程層** | 母版表列只在整合分支維護；brief 禁本 PR 改 STATUS／模板 | `docs/dev/STATUS.md:10-26`；`1-discussion.md:137`；本 hop brief | 本 PR 帶表列／模板，與並行 session 互蓋 | 待人審 |
| OC-3 | Backlog「觀測實驗前不動 Stage 1–4 模板」：**本 Stage 2 PR 遵守**；**G2 通過後本 slug 實作站才准改那些模板**。觀測實驗可用本 slug 當第一條真實 full lane，或延後。使用者只被問到九條落地；「何時解凍模板」是與 Backlog 的延伸對帳。標**流程層** | SURF-A 必須改模板，否則範例／牙與模板再分裂。本 hop 若先改，等於沒做 Stage 2 | `docs/dev/STATUS.md:50`；`1-discussion.md:41` 受影響面後續才動 | 要嘛本 slug 永不改模板（等於 DEPTH-B），要嘛本 PR 先改模板 | 待人審 |
| OC-4 | 過期高影響假設擋 G2 的牙**掛進既有** `check-spec-gate.sh`（主）＋ `check-realworld.sh` 形狀延伸（輔），不另造 gate 入口、不 bump 成 G4。使用者只被問到「過期擋 G2」；掛哪支腳本是 Q9 延伸 | 該腳本已是 G2 形狀 Gate；另造入口＝SURF-C | `scripts/check-spec-gate.sh:32-37`；`1-discussion.md:129` Q9。主／輔切分 `[Assumption]` | 新腳本當第四道 Gate，或只寫 checklist（EV-C） | 待人審 |
| OC-5 | Fast 六問命中後的菜單＝**升 full／mini real-world delta／Owner Call 接受**，不是自動升 full。mini 至少 Actor、工作影響、權限／等待／例外、代表性驗證。使用者只被問到「Stage 4 前要分診」；菜單是 Q13 延伸 | 審核區已寫命中不必一律 full；純視覺可維持 fast | `notes/review-requirement-discovery-gaps.md:313-319`；`1-discussion.md:133` Q13 | 任一命中強制 full（TALK-C），或菜單刪 mini | 待人審 |

### 內部技術選擇(下層,告知即可)
- Evidence 五態採用審核區候選字：Observed／Reported／Inferred／Assumption／Conflict。欄位字面 4-spec 再釘。
- Disposition 引用＝原文片段，不另發 ID（已在 DISP-A）。
- lookback 結果只走 `history-append.sh`，不開 `8-lookback.md`。
- A-5 不擴成 Actor Coverage；本檔 Disposition 已標 intentionally unchanged。
- 本 hop 產審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。
- 第 3 站觸發判定不在本 hop 代決；Owner Calls 沒有「跳過 Stage 3」字樣。
- 本 hop 不 bump plugin、不改守衛碼。

## ADR 晉升檢查
- 難逆轉:否（G3 前可改本檔 Decision／OC；牙與模板尚未落地）
- 反直覺:是（Owner Call 與 Stage 1 備忘已寫完，仍要改牙／範例；no-build 看起來夠、對帳後不夠）
- 真 trade-off:是（散文備忘 vs 形狀牙 vs 語意硬閘；同 slug 改範例 vs 另開後片）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-13 | 本 hop brief：比較落地九條 Owner Call 的方案、不重開 DO／LIGHT、適用處比 no-build。五決策點＝落地深度／落地面與範例／證據與過期假設／去向帳與回看／事實入口與 Fast 分診。對應 Q7–Q14。
- Stage 1 改口 | 2026-09-13 | 1-discussion 仍 draft、Q4 寫「只 Stage 1 不送 G1」、Q7–Q14 仍 `[>]`。本檔改口為推薦 Decision。不回改正本討論。
- Q6 對帳 | 2026-09-13 | 教師／規則／本 repo Fast 實例升 Observed；採用者行為維持 Assumption，OC-1 待人審。
- G1 | 未核 | `verdict` 空、OC-1～OC-5 待人審。禁止把 Stage 1 方向核准寫成 Stage 2 G1 PASS。
- 自檢七掃 | 2026-09-13 | ①每案優劣有依據欄；②G-out-1…9 進 Decision 對帳表，漏項進 Non-Goals；③Q7–Q14 皆有著落；④SC-1～10 可量測；⑤Rejected 無空棄因；⑥五決策點由 brief 確認，OC-1 承接 Q6 期限、OC-4／OC-5 承接 Q9／Q13 延伸、OC-2／OC-3 流程層；⑦既有脈絡表是對帳不是外移 schema。圖上五選定案標選定，Rejected 未上圖。
