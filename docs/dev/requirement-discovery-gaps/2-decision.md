---
feature: requirement-discovery-gaps
stage: 2-decision
status: in-review
verdict:
owner: rick
reviewers: []
updated: 2026-09-13
---

# 2. 收斂 — 九條需求發現缺口怎麼進方法論

> 把 `1-discussion.md` 的發散收成 Decision。本 hop **只交 Stage 2 決策包**，不改 `_templates/`／`skills/`／守衛／範例／STATUS／HISTORY。**不宣稱 G1 PASS**（`verdict` 空、OC 待人審）。
> Stage 1 原文仍寫「只討論、不送 G1、status 留 draft」；owner 2026-09-13 已說方向可、進 Stage 2。改口記在本檔，不回改正本討論。
> Lane = full。九條 DO／LIGHT 不重開。A-1 要求：原因仍可能由流程解決時，比較 no-build。

## Approaches Considered

### 決策點 1 落地策略
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 1A | **同一 slug 改活教師 + 延既有牙**：模板／dev-talk 節點／指南對稱句、`example/contract-expiry-reminder` 同期改口；機械牙接到既有 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`，不另造檢查家族。Q7／Q14 一併收在這裡 | 對準 G-out-1～9；範例不再教「Goal = dashboard」；B-1 不會「規定了但讀不到」；一包、不拆 slug | 會動 Stage 1–4 模板，撞 Backlog「觀測前不動模板」；Diff 中偏大；A-2 誘導仍不能只靠最終 md 硬擋 | 中 | `1-discussion.md:88-97` 九條結果；`1-discussion.md:116,127` 不拆 slug、Q7 移交牙落點；`1-discussion.md:243-246` 只改散文會走偏；`notes/review-requirement-discovery-gaps.md:293-296` 不改允許集合 = 讀不到；`example/contract-expiry-reminder/1-discussion.md:62-65,83-103,119` 活教師已鎖通道（Goals／AC；Interview「最低成本呈現面」在 L119）。成本 `[Assumption]` |
| 1B | **只改指南／skill 散文**，模板欄位、範例、守衛不動 | 最短；零守衛迴歸；不碰觀測凍結 | 模板仍要「從哪看」列畫面／端點；範例仍教解法；牙仍只驗章節字樣；G-out-1／2／8 落空 | 低 | `_templates/1-discussion.md:12,91-96` 不做決定 vs 通道骨架；`skills/dev-talk/nodes/N3-probe.md:22-23` 仍要附推薦；`scripts/check-realworld.sh:88-91` 只驗 Assumption／訪談字樣；`docs/dev/STATUS.md:50` 凍結省得到、痛留著 |
| 1C | **no-build／process-only**：口頭清單 + 試算表記痛點去向 + 日曆回看。本 repo 零改 | 可逆；滿足 A-1「至少比一個 no-build」；不污染觀測 | 現況就是靠審核筆記與記憶轉述在繞；Fast 合法跳過 1–3；沒有教師與牙，下一場討論仍照範例走 | 低 | `1-discussion.md:20,66-71` 現在怎麼繞；`notes/review-requirement-discovery-gaps.md:65-66,70-73` A-1 要比 no-build、不合理可註明；`1-discussion.md:73-74` Fast 無 1/3 檔機械放行。現場會遵守口頭清單 = `[Assumption]`（無採用 log） |

### 決策點 2 Evidence 狀態（Q8）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 2A | 高影響主張就地標 `Observed`／`Reported`／`Inferred`／`Assumption`／`Conflict`；Evidence 最小欄：來源類型、as-of、角色或範圍、支持哪一段、限制。點頭不升格。枚舉只加在高影響列，不要求每句都貼 | 對準 A-3 候選與 G-out-3；牙可驗「欄在 + 枚舉 ∈ 集合 + 來源 XOR Assumption+期限」，不再只認「有 Evidence 字」 | 枚舉仍可亂填；「這條算不算高影響」要人判 | 中 | `1-discussion.md:91,128` G-out-3、Q8 移交；`notes/review-requirement-discovery-gaps.md:124-136` 候選枚舉 + 不另發 ID 鏈；`scripts/check-realworld.sh:88-91` 現況只驗字樣。哪些列算高影響 `[Assumption]`（4-spec 再釘抽樣規則） |
| 2B | 只要來源或 Assumption+期限，**不**設枚舉 | 較短；少一個可被灌水的下拉 | 「查到的／聽說的／推論的／互相打的」又壓回同一格；A-3 點名二分太粗 | 低 | `1-discussion.md:30-31,128` 現況二分 + Q8 問的就是要不要枚舉；`notes/review-requirement-discovery-gaps.md:119-121` 失效模式就是壓成一種「事實」 |
| 2C | 維持 Evidence／`[Assumption]` 二分 | 零改欄 | G-out-3 落空；Stage 2 仍可用「1-discussion 事實」替方案背書 | 低 | `_templates/2-decision.md` 頂註步 1 准引 1-discussion 事實；`1-discussion.md:32` 接手不看假設強度 |

### 決策點 3 過期 Assumption 牙（Q9）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 3A | **擋 G2 的牙長在既有 `check-spec-gate.sh`**（它已是 G2 形狀 Gate）。4-spec 若仍引用高影響、已過期限、未 resolved／無 Owner Call 接受風險的 Assumption → exit 1。模板／範例地板仍由 `check-realworld.sh` 驗「四欄在不在」 | 對準 G-out-4／AC-4「人看得見的拒絕」；不另造腳本家族；G2 送審前本來就要跑這支 | 要定義「高影響列怎麼被腳本看見」（4-spec 引用形狀）；語意仍是人審 | 中 | `1-discussion.md:92,129,159-160` 過期擋 G2、Q9 移交；`scripts/check-spec-gate.sh:1-14,32-37` 已是 Gate 不是 warning；`_templates/1-discussion.md:82-86` `[~]` 今可 approved。引用形狀 `[Assumption]`（4-spec 再釘） |
| 3B | 只加厚 `check-realworld.sh`（模板／範例有欄即綠），填好的 feature 不擋 | 改動面小 | AC-4 要的是「這份 4-spec 過不了 G2」，不是「模板有欄」。重演「牙綠、填檔仍過」 | 低 | `1-discussion.md:159-160` 從哪看 = G2 被擋；`scripts/check-realworld.sh:71-91` 射程 = 模板+範例字樣，不是填檔 |
| 3C | 只寫 G2 checklist 散文，不延伸腳本 | 零碼 | `[~]` 仍合法走到 G2；過期假設若為假，測試會綠 | 低 | `1-discussion.md:32,76,229-230` `[~]` 合法 + 接手不看影響級 |

### 決策點 4 disposition 引用（Q10）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 4A | Stage 2 表：**引用 Stage 1 高影響痛點／workaround／exception 原文片段** + 去向（本方案處理／刻意維持／Non-Goal／另開 slug／仍待驗）+ 一句理由。不另發 RW-id。Stage 4：標「處理」者至少一條 R/S，其餘落到 Out of Scope／Known limit／後續 slug | 對準 A-6 與 G-out-6；沿用「不另發第二鏈」；G1 看得到未處置列 | 「哪些算高影響」仍要人判；引用片段要防截到無意義 | 中 | `1-discussion.md:94,117,130` G-out-6、禁第二鏈、Q10；`notes/review-requirement-discovery-gaps.md:221-231` 候選即引用原文；`_templates/2-decision.md` 頂註步 0／步 6 今只覆蓋 Goals／`[>]`。高影響抽樣 `[Assumption]` |
| 4B | 發明 `RW-1`… 第二條 ID 鏈，R/S 引用 RW-id | 機械對帳最乾淨 | Stage 1 Non-Goal 與 ID 規則已禁；靠近第二套方法論 | 高 | `1-discussion.md:117`；`_templates/1-discussion.md:50-51` 不另發 Journey/Actor ID |
| 4C | 散文寫「痛點有處理」，無逐條表 | 最短 | 正是現況失效：Journey 列可無聲消失 | 低 | `1-discussion.md:34,62-63,235-238` 收斂只吃 Goals／AC；Stage 3 場景有牙、Stage 1 痛點沒有 |

### 決策點 5 lookback 落點（Q11）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 5A | **約定**寫在 7-review Exit（日期／owner／資料來源／低於何值重開）；**結果**到期用既有 `history-append.sh` 追加。不另造永久 lookback 檔。G3 不必等數週結果 | 對準 A-7／G-out-7；兩個落點都已有維護者與寫入口；不新造文件類型 | 採用專案若沒用 HISTORY 寫入口，結果列會漂；「低於何值」亂填仍要人抓 | 中 | `1-discussion.md:95,131,169-172`；`notes/review-requirement-discovery-gaps.md:257-262` 候選即 HISTORY 或 7-review 附錄、禁無主檔；`_templates/7-review.md:316-342` Exit 今無回看四欄；`docs/dev/STATUS.md:36-42` HISTORY 只准 append 腳本 |
| 5B | 只寫 HISTORY，7-review 不留約定 | 少改 Exit | 出貨當時沒有「誰／何時／用什麼／門檻」；到期才補等於沒約 | 低 | `1-discussion.md:169-172` AC-7 要出貨時留下四欄 |
| 5C | 另造每 feature 一份永久 `lookback.md` | 名稱對得上 A-7 | 無維護者；違反「不要另造一套永久文件」 | 高 | `notes/review-requirement-discovery-gaps.md:261-262` |

### 決策點 6 事實入口（Q12）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 6A | **本輪 evidence manifest**：討論者先列「想找哪類證據與原因」；owner 核准路徑／來源後才讀。`devtalk-guard`（或同等讀取圍欄）放行該清單，**仍禁** 2／3／4／5／6／7 與既有方案檔。ticket／SOP 裡的解法建議不當事實 | 對準 G-out-8；改允許集合，不是只改句子；圍欄③仍在 | 要定 manifest 形狀與「核准」痕跡；外部 connector 仍靠權限＋人 | 中 | `1-discussion.md:96,132,173-177`；`notes/review-requirement-discovery-gaps.md:285-296` 候選 + 不改允許集合會讀不到；`hooks/devtalk-guard.sh:16-21` 今只管 skill 寫入洩漏、不管事實入口；`skills/dev-talk/SKILL.md:17-21` 未指名不得列目錄。manifest 欄位 `[Assumption]`（4-spec 再釘） |
| 6B | skill 寫「先問 owner 再讀」，守衛允許集合不動 | 最短 | 規定了但讀不到；重演 A-0／A-13 同型 | 低 | `1-discussion.md:244-246`；`notes/review-requirement-discovery-gaps.md:293-296` |
| 6C | 放寬白名單到整個 `docs/`／`notes/`，不必逐輪核准 | 少一次核准 | 無邊界掃描；把方案筆記與事實一起打開 | 高 | `1-discussion.md:139` 圍欄仍禁方案檔；`1-discussion.md:118` 不把 ticket 解法當事實 |

### 決策點 7 Fast 命中後（Q13）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 7A | 進 Stage 4 **之前**六問（下一步／權限／等待語意／交接／系統外／中斷恢復）。全否且已有 approved spec → 可 Fast。**命中不一律升 full**：owner 裁升 full、fast+mini real-world delta、或 Owner Call 接受風險。純視覺、不改語意的 bug 維持 Fast | 對準 G-out-9／AC-9；不把小修全拖進訪談；有去向不是空白開寫 | mini 的最小欄要另釘；「不改語意」仍是人看 diff | 中 | `1-discussion.md:97,133,177-180`；`notes/review-requirement-discovery-gaps.md:313-324` 候選即三擇一；`skills/dev-flow/SKILL.md:34-36` Fast 今省略 1–3；`_templates/4-spec.md:266-269` 高風險人機互動寫在 4-spec、lane 已選完；`docs/dev/engine-fence-masking/4-spec.md:11-12` 本 repo 已有省略實例 |
| 7B | 六問任一命中 → **必須**升 full | 規則簡單；互動風險不會留在 Fast | 一個狀態字也可能命中「等待語意」；把小修拖進整套 1–3，owner 候選已拒「一律 full」 | 高 | `notes/review-requirement-discovery-gaps.md:317-319` 命中不必一律 full |
| 7C | 命中一律 fast+mini，不給升 full／不給 OC | 保 Fast 速度 | 權限／核准語意被改時，mini 可能不夠；owner 要的是可裁 | 中 | `1-discussion.md:133` Q13 問的是三擇一，不是鎖死 mini |

### 決策點 8 A-5 Human verdict
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 8A | **一行角色／場景（LIGHT）**：Human verdict 本文寫清驗了哪個角色、哪個場景。不做 Actor Coverage 全表 | 對準 G-out-5／Owner Call LIGHT；後讀者一眼看出驗了誰、驗了哪場；現制已擋 Agent 代填 | 擋不住「錯的人寫對的角色字」；代表性仍是人判 | 低 | `1-discussion.md:93,104,114` G-out-5、Requested 寫清角色／場景、Non-Goal 不做全表；`notes/review-requirement-discovery-gaps.md:25,187-194` A-5 LIGHT vs 全表候選 |
| 8B | **Actor Coverage 全表**：每個關鍵角色標 direct interview／observation／proxy／not covered，proxy 必寫限制 | 代表性缺口顯性化 | Owner 已裁 LIGHT；本包成本越級；外部角色常無法直接 Demo | 高 | `notes/review-requirement-discovery-gaps.md:187-194` 候選全表；`1-discussion.md:114` 本包不做 |
| 8C | **只留 attestation**：ACCEPTED + 姓名日期即過（現況） | 零改；runtime 已認 human attestation | G-out-5 落空；只證明有人按過，看不出驗了誰、哪場 | 低 | `_templates/3-prototype.md` Participants 自由文字 + attestation；`scripts/check-realworld.sh:121-151` 只守不是 Agent 代填；`1-discussion.md:33,161-164` AC-5 要一行內能答角色與場景 |

## 方案架構圖
[1A] 同slug改教師+延既有牙(選定)
[2A] 高影響主張枚舉+來源欄(選定)
[3A] 過期高影響假設進不了G2(選定)
[4A] 引用原文做disposition(選定)
[5A] Exit約回看、HISTORY記結果(選定)
[6A] 本輪owner核准的事實入口(選定)
[7A] Fast六問後owner裁full/mini/OC(選定)
[8A] Human verdict一行角色場景(選定)

## Decision
採 **1A+2A+3A+4A+5A+6A+7A+8A**：人讀 Stage 1 能分辨「要達成的工作結果」與「帶來的解法構想」；被問「上次真的怎麼做」時，題目本身不先塞推薦答案；高影響 Assumption 到期仍未驗，人進不了 G2。九條一包、同一 slug 改活教師（模板／dev-talk 節點／指南對稱句／完整範例）與對帳形狀，不另造檢查家族、不發明第二條 ID 鏈。高影響主張用 Observed／Reported／Inferred／Assumption／Conflict + 來源欄；Stage 2→4 用原文片段做 disposition；出貨時 7-review Exit 留下回看四欄，結果走 HISTORY 追加；事實入口用本輪 owner 核准清單，方案檔仍禁讀；Fast 在寫 4-spec 前做六問，命中由 owner 裁升 full、fast+mini 或接受風險。Human verdict 一行寫清角色／場景（A-5 LIGHT）。腳本家族名見決策點 1 與 OC-1。不選 no-build、不選只改散文、不選 Actor Coverage 全表、不選只留 attestation。本 hop 不改模板正本、不宣稱 G1 PASS。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| 1B | 只改指南／skill 散文。模板與範例仍教通道，牙仍只驗字樣；G-out-1／2／8 落空。 |
| 1C | no-build／口頭清單。現況已是審核筆記＋記憶轉述；Fast 可合法跳過 1–3；下一場仍照範例走。A-1 比過、不合理故不硬塞。 |
| 2B | 不設枚舉。A-3 要拆的就是「查到／聽說／推論／衝突」被壓成一種事實。 |
| 2C | 維持二分。G-out-3 落空；點頭仍能當背書。 |
| 3B | 只加厚 realworld 模板牙。擋不到填好的 4-spec；AC-4 要人看得見的 G2 拒絕。 |
| 3C | 只寫 G2 散文。`[~]` 仍合法走到 G2。 |
| 4B | RW-id 第二鏈。Stage 1 Non-Goal 已禁。 |
| 4C | 散文「有處理」。正是痛點靜默消失。 |
| 5B | 只寫 HISTORY。出貨當時沒有四欄約定。 |
| 5C | 另造 lookback 永久檔。無維護者。 |
| 6B | 只改 skill 句子。規定了但讀不到。 |
| 6C | 放寬整個 docs／notes。打開方案筆記，圍欄破。 |
| 7B | 命中一律升 full。owner 候選已拒；小修被拖進訪談。 |
| 7C | 命中一律 mini。權限／核准被改時不夠；Q13 要的是可裁。 |
| 8B | Actor Coverage 全表。Owner Call 是 LIGHT；本包不做。 |
| 8C | 只留 attestation。只證明有人按過；G-out-5 落空。 |
| 新造檢查家族 | 1A／OC-1 已拒第二套牙；沿用既有 Gate／圍欄延伸射程。 |
| dashboard／API 黑名單 | A-1 已拒誤殺合法領域詞；靠分欄形狀 + G1 人審。 |
| 拆成九個 slug | Stage 1 Non-Goal。 |
| 假現場 log 收 Q6 | 沒有 log；對帳止於本 repo 範例教師。 |

## Rationale
第一因不是「訪談的人不知道該問什麼」。母版已經能七關全綠：Goals 骨架把「從哪看」寫成畫面／端點，N3 發現題也要附推薦，牙只認章節與「訪談」字樣，完整範例把 dashboard 寫進 Goal／AC。採用者抄範例，就複製這條路。

1C 把解法放在口頭與試算表。Stage 1 已寫出現況 workaround 就是 owner 筆記與記憶轉述；那條路沒擋住「Goal = dashboard」。1B 加厚指南，活教師不動，下一場討論仍照範例寫。1A 改的是人會抄的那三層：模板、範例、會紅的牙。牙不新造家族——`check-spec-gate.sh` 已是 G2 Gate，`check-realworld.sh` 已守模板／範例地板，`devtalk-guard` 已是討論圍欄；缺的是射程，不是第二套方法論。

Q8 選 2A：A-3 的病是粒度，不是「少一個來源欄」。枚舉可灌水，所以牙只驗形狀，語意留給 G1 抽一條高影響主張往回走。Q9 選 3A：擋點必須是 G2 送審那一關，不是模板有欄就綠。Q10 選 4A：要逐條去向，但不發明 RW-id。Q11 選 5A：約定跟結果分開寫，兩邊都用已有寫入口。Q12 選 6A：允許集合不改，B-1 就是假規則。Q13 選 7A：六問要在 lane 選定前，命中給 owner 裁，避免「改一個狀態字 = 整套訪談」。A-5 選 8A：Owner 已裁 LIGHT；全表是另一層成本；只留 attestation 擋不住「錯的人按對的鈕」，後讀者仍看不出驗了誰、哪場。

觀測凍結（STATUS Backlog：完整 full lane 觀測前不動 Stage 1–4 模板）與本 slug 相撞。2026-09-12 Owner Call 已裁九條並開本 feature；再等一次「舊模板觀測」會把已裁的缺口繼續教出去。本 slug 後續 1→7 當**新規則的第一次觀測**，比再拍一次舊病更有用。這是 OC-2，不是默認解凍。

## 既有脈絡
對帳快照（2026-09-13 tip `bcdfee1`，#260／#263 之後）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| Owner Call 2026-09-12 | A-1…A-4／A-6／A-7／B-1／B-2 = DO，A-5 = LIGHT | 不重開；本檔只收怎麼落地 |
| Stage 1 #260 | `1-discussion.md` status=draft、不送 G1；Goals 已分欄 | 1-discussion 留當時說法；本檔改口 |
| 模板 1／驗收骨架 | 「不做決定」+「從哪看」列畫面／端點／檔／log | 1A 改 Goals／Requested solution／雛形觀測句 |
| N3-probe | 一次一題、附推薦；兩輪無新問題可停 | 1A 發現題禁推薦；完成條件改覆蓋面，兩輪只當輔助 |
| realworld 牙 | 章節／`[Assumption]`／「訪談」字樣 | 2A／4A／A-5 的地板；不把它當填檔 Gate |
| spec-gate | 六項形狀，已是 G2 Gate | 3A／7A 的擋點 |
| devtalk-guard | 只掃 `skills/dev-talk/*` 寫入洩漏 | 6A 延伸允許集合，仍禁方案檔 |
| 完整範例 | Goal／AC／Interview 已鎖 dashboard | 1A 同期改口，不當後 slug |
| Fast | 省略 1–3；無檔 = legacy/N-A；人機風險寫在 4-spec | 7A 把六問移到進 4 之前 |
| STATUS Backlog 觀測凍結 | 完整 full lane 前不動 Stage 1–4 模板 | OC-2：本 slug 取代「先觀測舊模板」 |
| STATUS 寫入 | 只准整合分支 + `status-update.sh` | 本 branch 不改正本（OC-4） |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 新欄被填 Unknown／亂選枚舉，牙仍綠 | 牙只驗形狀（欄在、枚舉 ∈ 集合、來源 XOR Assumption+期限、disposition 非空）。G1 抽一條高影響主張沿引用回來源；對不上退回 Stage 1。禁止 dashboard／API 黑名單 |
| A-2 誘導無法從最終 md 還原 | 不假裝有對話硬 gate。skill／指南釘死對稱句；靜態牙防其中一邊被刪。Interview Log 高影響發現題由 Stage 1 自檢抽查 |
| 觀測凍結被默默解掉 | OC-2 明示：只解凍本包要動的 Stage 1–4 列。本 slug 當新規則第一次 full-lane 觀測，不假裝舊觀測還排在前面 |
| Q6 採用現場無 log，期限卻是 Stage 2 | OC-3：本 repo 範例教師 = 已核 Observed；採用者是否照抄仍是 Assumption。對帳 = 同期改範例。不捏造現場訪談 |
| Fast 六問變儀式、全打「否」 | 7A 要結構化答，不接受空白。命中無 full／mini／OC → 擋進 Stage 4（與 3A 同走 spec-gate）。「不改語意」由 reviewer 對 diff |
| B-1 manifest 形狀未釘，Stage 4 前各寫各的 | 本檔只鎖「本輪清單 + owner 核准後才讀 + 仍禁 2–7」。欄位／檔名進 4-spec（OC-1） |
| 第二套牙或 RW-id 在實作回流 | 1A／4A 進 Decision；新家族與第二鏈進 Rejected。要翻案回本站 |
| 本 hop 被當成已過 G1 或已改模板 | `verdict` 空；OC 待人審；本 PR 只含本目錄 2-decision.md／.html |
| lookback 數字亂填被當成已有有效 outcome | 牙驗四欄在；指標是否代表問題改善是人判。到期未回看不得把問題寫成已改善 |

## Success Criteria
- SC-1(G-out-1)：落地後，模板 Goals 指令不再要求候選畫面／API／元件通道；`Requested solution` 分欄存在。一份把「我要 dashboard」寫進 Goals 的對照稿，形狀檢查或 G1 抽查能指出「構想在錯欄」。`example/contract-expiry-reminder/1-discussion.md` 的 Goals 不再指定登入／點擊／一眼可見為目標本身。
- SC-2(G-out-2)：`skills/dev-talk` 發現題路徑不再把「附推薦答案」當硬規則；裁決題才可附選項／差異／推薦。刪掉其中一邊對稱句 → 靜態牙紅。不要求從最終 1-discussion 還原整場對話。
- SC-3(G-out-3)：高影響主張缺來源且缺 Assumption+期限 → 指定檢查 exit ≠ 0。有來源或有期限的對照稿 exit 0。點頭紀錄不得當唯一來源。
- SC-4(G-out-4)：4-spec 仍引用已過期限、未 resolved、無 Owner Call 接受風險的高影響 Assumption → `check-spec-gate.sh` exit 1。已驗轉 Observed／Reported、或有 OC 接受的對照稿 exit 0。
- SC-5(G-out-5)：Human verdict 模板／牙要求一行內有角色與場景。只寫 ACCEPTED + 姓名日期的對照稿不得當完整 verdict。不做 Actor Coverage 全表。
- SC-6(G-out-6)：Stage 1 高影響痛點／workaround／exception 在 Stage 2 disposition 無去向 → G1 審面或指定檢查能指出來。標「本方案處理」的列，Stage 4 至少有一條 R/S；其他狀態有 Out of Scope／Known limit／後續 slug。本檔 Disposition 節先吃本討論 Journey 三痛。
- SC-7(G-out-7)：7-review Exit 缺回看日期／owner／來源／門檻四欄之一 → 指定檢查 exit ≠ 0。本包自己 shipped 時四欄都在；到期結果走 HISTORY 追加，不另造 lookback 檔。
- SC-8(G-out-8)：owner 核准的事實路徑讀得到事件／行為／結果；讀 `2-decision`／`4-spec` 仍被擋。未核准路徑不得當已授權 evidence。ticket 解法建議不當事實。
- SC-9(G-out-9)：Fast 4-spec 六問未收束 → 不得當已完成早期分診（指定檢查 exit ≠ 0）。命中列有升 full／mini／OC 去向。「只改狀態字、把等待顯示成完成」的對照案必須命中等待語意問。
- SC-10(Non-Goal)：未新造 Journey／Actor／RW ID 鏈；未做 A-5 全表；未拆九個 slug；本 PR 未改 STATUS／HISTORY／模板正本；本檔 `verdict` 不是 Agent 自填的 PASS。

## Scope & Non-Goals(定稿)
- In：1A 落地策略（Q7 延既有牙、Q14 同 slug 改範例）；2A 高影響枚舉 + Evidence 最小欄；3A 過期假設擋 G2；4A 原文片段 disposition；5A Exit 約定 + HISTORY 結果；6A 本輪 evidence manifest + 改允許集合；7A Fast 六問 + owner 三擇一；8A Human verdict 一行角色／場景（A-5 LIGHT）；Q6 以範例教師對帳。腳本家族落點見決策點 1／OC-1。
- Out：1B／1C；2B／2C；3B／3C；4B／4C；5B／5C；6B／6C；7B／7C；8B／8C；新造檢查家族；RW-id；lookback 永久檔；Actor Coverage 全表；拆 slug；本 hop 改模板／守衛／範例正本；本 hop 改 STATUS／HISTORY；本 hop 宣稱 G1 PASS；本 hop 跳過 Stage 3；重開九條 DO／LIGHT；dashboard／API 黑名單。

## Real-world Disposition
本檔先做 A-6 要求的去向帳（引用 Stage 1 原文，不另發 ID）。實作落地後，後續 feature 的 2-decision 用同一形。

| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| Journey「發現被錨定」 | 本方案處理 | 1A 改 N3：發現題禁推薦 |
| Journey「點頭當證據」 | 本方案處理 | 2A：點頭 ≠ 來源 |
| Journey「痛點消失」 | 本方案處理 | 4A：本表即去向帳 |
| Journey「問題沒改善」 | 本方案處理 | 5A：Exit 約回看 |
| Journey「互動風險晚露」 | 本方案處理 | 7A：六問在進 4 前 |
| Workaround「owner 用審核筆記記缺口」 | 本方案處理 | 本 slug 取代筆記當制度 |
| Workaround「現場證據靠記憶轉述」 | 本方案處理 | 6A：核准後的事實入口 |
| Workaround「Fast 直接寫 4-spec」 | 本方案處理 | 7A；全否且已有 spec 仍可 Fast |
| Workaround「人口頭記先問現況」 | 本方案處理 | 1A 把口頭改成 skill 硬規則 |
| Exception「Fast 合法跳過 1–3」 | 刻意維持 | 七關結構不改；只加進 4 前六問 |
| Exception「A-5 只 LIGHT」 | 刻意維持 | Owner Call；不做全表 |
| Exception「`[~]` 可走到 G2」 | 本方案處理 | 3A 過期擋 G2 |
| Exception／Q6「採用現場仍把解法寫進 Goal」 | 仍待驗 | 本 repo 範例 = Observed 教師，1A 同期改。採用者是否照抄無 log → OC-3 |
| Exception「現場發現題仍附推薦」 | 仍待驗 | 無逐字稿；1A 改未來問法。殘餘 OC-3 |
| Exception「Fast 因檔數少漏判互動」 | 仍待驗 | 本 repo 有省略實例；採用現場是否踩過權限／等待誤標無 log → OC-3 |

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | 機械牙**只延伸既有** `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`（及它們已掛進的 `devflow-check`）。不新造 `check-discovery-gaps.sh`。使用者 brief 只鎖「九條怎麼進方法論」；「沿用既有家族」是 owner 延伸 | 另造家族靠近第二套方法論；現有 G2 Gate 與討論圍欄已在，缺的是射程 | `1-discussion.md:127` Q7 未選定改哪支；`scripts/check-spec-gate.sh:32-37` 已是 Gate；`1-discussion.md:243-246` 要部分牙。延伸本身 `[Assumption]` | 要新入口／新腳本；與「不另造家族」重審 | 待人審 |
| OC-2 | 本 slug **取代**「完整 full lane 觀測前不動 Stage 1–4 模板」那條凍結，範圍僅限本包要動的列。後續用本 slug 真跑 1→7 當新規則第一次觀測。使用者只被問到 Stage 2 收斂；「解凍並改觀測對象」是延伸 | 2026-09-12 已裁九條並開本 feature；再拍舊模板會繼續教 Goal = dashboard | `docs/dev/STATUS.md:50` 凍結原文；`notes/review-requirement-discovery-gaps.md:16-18` 實作另開即本 slug；`1-discussion.md:23-24` 裁決與本 feature 已分開記 | 改回 1B／1C，或另等一次舊模板觀測才動模板 | 待人審 |
| OC-3 | Q6 與三條現場 `[Assumption]`：**不**用假訪談收尾。本 repo 範例教師當 Observed 對帳；採用現場是否照抄維持 Assumption。不因無 log 擋本 G1。這是對「期限 = Stage 2 對帳」的收窄 | 沒有採用專案逐字稿；捏造現場 = A-3 自己犯的病 | `1-discussion.md:126,77-79,86` Q6 + 三條期限 Stage 2；`example/contract-expiry-reminder/1-discussion.md:62-65` 教師在本 tree。收窄本身 `[Assumption]` | 要補現場訪談才准 G1；或把 Q6 升成已核「採用者一定照抄」 | 待人審 |
| OC-4 | 本 feature branch **不**跑 `status-update.sh` 改正本 Active 列；不改 HISTORY；`1-discussion.md` 保持 draft／「不送 G1」原文。本檔 `verdict` 空到人類寫入。標**流程層** | 母版 STATUS 只在整合分支維護；使用者禁發明 G1 PASS | `docs/dev/STATUS.md:10-26`；`1-discussion.md:136-137`；本 hop brief | 本 PR 帶 STATUS 列或自填 PASS，與並行 session 互蓋 | 待人審 |
| OC-5 | 2A 枚舉**只要求高影響主張**，不要求 Stage 1 每一句 Context 都貼狀態。這是對 A-3「主張→來源」的收窄 | 全句枚舉會變成另一種字樣儀式，重演「有 Evidence 字就綠」 | `notes/review-requirement-discovery-gaps.md:125` 「重要主張就地標」；`1-discussion.md:128` Q8。何謂高影響 4-spec 再釘 | Scope 變成每句都貼；牙誤殺普通 Context | 待人審 |
| OC-6 | Fast：六問全否 + 已有 approved spec + **不改語意的純視覺／文案** → 維持 Fast，不必 mini。這是對 B-2 的收窄 | 候選已寫「純視覺不改語意可維持 Fast」；不收窄會把 CSS 錯字拖進訪談 | `notes/review-requirement-discovery-gaps.md:319`；`1-discussion.md:180` 對照案是等待誤標不是換色 | 每個 Fast 都要 mini；或視覺 bug 被 7B 拖去 full | 待人審 |

### 內部技術選擇(下層,告知即可)
- 本 hop 不 bump plugin、不改 `_templates/`／`skills/`／`example/`／守衛正本。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口成 Decision。
- 審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。
- Stage 3 不預先跳過；觸發判定留給第 3 站（訪談問法、證據核准、Fast 六問都可能改下一步／核准／交接）。本檔無「跳過 Stage 3」流程層 OC。
- 4-spec 再釘：Assumption 四欄機器可讀形、disposition 表頭、evidence manifest 檔名、Fast 六問欄位名、lookback Exit 四欄字面、高影響抽樣規則。
- A-2 完成條件：必查面已覆蓋、關鍵反例已問、證據缺口已顯性化；「連續兩輪無新問題」只當輔助訊號。

## ADR 晉升檢查
- 難逆轉:否（G3 前可改本檔 Decision／OC；模板尚未落地；落地後欄位仍可再版）
- 反直覺:是（A-1 要比 no-build，卻不選它；Fast 反而多一道六問；觀測凍結被本 slug 取代）
- 真 trade-off:是（改活教師 vs 先觀測舊模板；部分牙 vs 假裝對話可硬擋；Fast 摩擦 vs 等待誤標）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-13 | Stage 2 brief（Implementer C）：為九條進方法論寫方案、選定、駁回原因；適用時比 no-build；不發明 G1 PASS；不改 STATUS／模板。原七點對 Q7–Q14 + A-1 no-build。
- Reviewer 1 必改 | 2026-09-13 | Decision 首句改人的結果；A-5 補 8A／8B／8C 並排；Rejected 改表。範例「最低成本呈現面」改引 L119。仍不填 G1 PASS。
- Stage 1 改口 | 2026-09-13 | 1-discussion 仍 draft、Q6 `[~]`、Q7–Q14 `[>]`；owner 已說方向可、進 Stage 2。本檔改口為 Decision。不回改正本討論。
- Q6 對帳 | 2026-09-13 | 本 tree 範例 Goals／AC／Interview 鎖定 dashboard = Observed 教師（「最低成本呈現面」=`example/contract-expiry-reminder/1-discussion.md:119`）。採用現場是否照抄 = 仍 Assumption，見 OC-3。未捏造現場 log。
- 自檢七掃 | 2026-09-13 | ①優劣皆有依據欄；②G-out-1～9 進 Decision／SC，漏項進 Non-Goals；③Q7–Q14 與 A-5 皆有選定或 Rejected；④SC 可量測；⑤Rejected 無空棄因；⑥八決策點由 brief + Reviewer 1 A-5 補點確認，OC-1～3／5／6 承接延伸或收窄，OC-4 流程層；⑦既有脈絡是對帳不是外移 schema。圖上 1A–8A 標選定，Rejected 未上圖。
- G1 | 未寫入 | `verdict` 空。全勾不算 PASS。等人類或 fresh-context reviewer 寫入。
