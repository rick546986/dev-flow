---
feature: five-station-simplify
stage: 2-decision
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-13
---

# 2. 收斂 — 五站簡化（Implementer C：Must-keep 防掏空）

> Lane = **full**。本 hop 只落 `2-decision.md` + 審頁 html；不改 `_templates/`、
> `graph.yaml`、gate token、STATUS、HISTORY、契約版本；不送 G1 `verdict:`；不合併。
> F0 十條已鎖，本檔**不重開**。Goal 維持結果句，不解成「去建五站／寫 coordinator」。
> C 線主軸:Must-keep 與反掏空 Spec／Build 是 **Decision 約束**；F1 拒收謂詞升成
> 本方案要求或 Owner Call。獨立 A／B，不引用他線 Decision。

## Real-world 去向
| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| owner chat「Treat as PASS／都過／可以」落成 `verdict: PASS` | 本方案處理 | 殺的是例行等人，不是審查物質；蓋章不當通過證據 |
| dogfood Demo 欄空仍開 Stage 4 | 本方案處理 | Q11：空 attestation 仍機械拒；chat 准開 ≠ 判定 |
| 摺站省完整度 → 假完成 T（缺四欄／跳 RED／自審） | 本方案處理 | M11＋T 四欄＋seam 鎖成 Decision 約束；缺一項勾選仍算未完成 |
| 採用現場兩案回報的 G1／G2／G3 **物質洞** | 本方案處理 | 物質留下並交 F1 牙；不可用蓋章證據冒充、也不可用物質洞當刪 token 理由 |
| `[Assumption]` 採用現場仍用 chat 蓋章過 G1／G2 | 仍待驗 | Q6；過期擋本 slug G2，不得當已核事實 |
| Fast lane 合法省略 Stage 1–3，仍吃 G2 物質 | 刻意維持 | 不廢 Fast；本包不把 Fast 當掏空借口 |
| in-flight：已有站檔 → 整段舊 7 到 Ship | 刻意維持 | brief OC-9；本 slug 已是 live freeze 樣本（G-out-8） |
| F0–F2 母版新開改版軌仍走舊 7 | 刻意維持 | brief §6；避免雙路線污染觀測 |
| 未 upgrade 到 2.1.0 時 marketplace 可換 hops 而 doctor 仍綠 | 本方案處理 | 採用 hop 身分進約束；doctor 綠 ≠ 路線沒變 |
| `[Assumption]` A1／A2 共寫 `1-discussion.html` | 仍待驗 | 移交 F1 annex；為假則不必為雙檔名加牙 |
| owner 自審是有記錄的最後手段 | 刻意維持 | 不假裝四眼；Agent 書面審不得冒充判定 |
| M1 ID 鏈；測試名含 S-id | 本方案處理 | 去向 `M1 → R/S`；測試名不含 S-id → 紅 |
| M2 圍欄 | 本方案處理 | 去向 `M2 → R/S`；實作者仍禁讀 1／2／3 補洞 |
| M3 反模糊三律 | 本方案處理 | 去向 `M3 → R/S`；S 含 TBD／不可測 → 紅 |
| M4 Real-world→Demo→OC | 本方案處理 | 去向 `M4 → R/S`；對齊 G-out-6／B1 |
| M5 人寫 `ACCEPTED`／Ship `PASS` | 本方案處理 | 去向 `M5 → R/S`；Agent 代填 = 未寫 |
| M6 G3 Evidence 八點 | 本方案處理 | 去向 `M6 → R/S`；只測綠 ≠ 出貨 |
| M7 Profile + `fast`+`high` 拒 | 本方案處理 | 去向 `M7 → R/S` |
| M8 DBC 條件式 | 本方案處理 | 去向 `M8 → R/S`；整節刪 = 違 M |
| M9 Files ⊆ 5-tasks | 本方案處理 | 去向 `M9 → R/S`；缺 Files 或越界 → 紅 |
| M10 驗證五律 | 本方案處理 | 去向 `M10 → R/S`；無原始輸出 → 紅 |
| M11 T seam + 四欄 | 本方案處理 | 去向 `M11 → R/S`；C 線主風險；不可標可選 |
| M12 author≠approver | 本方案處理 | 去向 `M12 → R/S` |
| M13 html 重生 | 本方案處理 | 去向 `M13 → R/S`；本 hop 仍產審頁 |
| M14 不可逆才 Quiz | 本方案處理 | 去向 `M14 → R/S`；Quiz ≠ 預設第三停 |
| M15 token／檔仍在 | 刻意維持 | 去向 `M15 → Non-Goal:本 hop 不刪 token`；刪 = 新 brief |
| M16 F0 不改 graph／牙 | 刻意維持 | 去向 `M16 → Non-Goal:本 hop 零施工` |
| rewrite cap：hop≤2／Decide≤1／Goal reopen≤1 | 本方案處理 | 數字已鎖；計數落點移交 F2（Q10） |
| 本 slug = live freeze 樣本 | 刻意維持 | G-out-8／Q12；不得當新 5 白老鼠 |
| 第二條 Journey／Actor ID 鏈 | Non-Goal | Q9：不另發 ID；去向掛既有 R／S |
| coordinator 碼／event schema | 另開 slug | F2；本 Decision 只鎖行為與 cap，不選 schema |
| dual-read 2.1.0 欄位與舊檔缺省 | 另開 slug | Q8 → F1 annex；本檔只鎖原則 |
| 本 hop 改 `_templates/`／gate／graph | Non-Goal | F0 OC-10；Backlog B 凍 Stage 1–4 模板 |

## Approaches Considered

### 決策點：Must-keep 防掏空綁法
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A 約束+去向+牙 | M1–M16 與 T 四欄／seam 寫進 Decision 約束；高影響列用 Q9 去向；後站用「已五站」省略 = 違規不是簡化 | 對準 C 線假完成；Stage 2 對帳可擋「可選四欄」；Goal 仍是結果句 | 約束面長；F1 才有牙咬 | 中 | `1-discussion.md:L138-L147` G-out-2／3／7；`L195-L215` 帶走表；`L172-L177` Q7／Q9。成本 `[Assumption]` |
| B 只當 brief 備忘 | 摺等待；Must-keep 留在 F0 brief，本檔不升約束 | 文短 | 後站可裝沒看見；Assumption「會偷 M」過期擋不住 Decision 寫可選 | 低 | `1-discussion.md:L15` 假完成；`L107` 後站會偷 M；`L125` 過期擋把可選四欄寫進 Decision；`L307-L310` 偷 M11 = 假完成 T |
| C 另發 Must-keep ID 鏈 | 給 M 新的 R／S 家族 | 機器好追 | 違 Q9 與 Non-Goals；第二條鏈 | 高 | `1-discussion.md:L165` 不新增第二條 ID 鏈；`L177` Q9 不另發 ID |

### 決策點：F1 拒收謂詞落點
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| D 升成本方案要求+OC | Q7＋M 表拒收句＋狀態機 §6 最小咬集合進本方案要求；OC 釘「只准加不准減」 | 後站不能裝沒看見；F1 有對帳清單 | 謂詞形狀細節仍交 annex | 中 | `1-discussion.md:L175` Q7 最小集已鎖；`L199-L215` F1 拒收謂詞欄；狀態機 §6 見 brief 並列檔。成本 `[Assumption]` |
| E 形狀全交 F1 | 本檔只寫「會有牙」 | 本 hop 最短 | 規格／任務可先把四欄寫成可選；牙落地時已晚 | 低 | `1-discussion.md:L175` 最小集**已鎖**不是未定案；`L125` Stage 2 對帳就是擋這招 |
| F 現改 gate／模板 | 把拒收句寫進 `_templates/` 或 gate token | 機械立刻咬 | 違 F0 OC-10 與 Backlog B；本 hop 禁施工 | 高 | `1-discussion.md:L29` F0 不准改模板／graph／牙；`L158` 本 hop 不改 `_templates/`；`L181` 牙只准 scripts／annex |

### 決策點：Q11 空 attestation
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| G 空欄仍機械拒 | B1 命中且 attestation 空 → 不得 hop 出 Spec；五站後同一拒；chat「准開下一站」≠ attestation | 補上 dogfood 洞；對齊 G-out-4／6 | 現場不能再靠口頭章跳 Demo | 低 | `1-discussion.md:L179` Q11 現行牙已拒、五站後要保持；`L85`／`L241` AC-4；`L113` dogfood 空欄仍開 4 |
| H chat 准開可當 attestation | 口頭「可以」視同人簽 | 摩擦低 | 重演 Treat as PASS；蓋章從 G1 搬到 Demo | 低 | `1-discussion.md:L93-L95` workaround 就是 chat 蓋章；`L142` G-out-4 Agent 代寫仍當沒寫 |
| I 只警告不擋 hop | 空欄 warning-only | 不擋前進 | 假完成 hop；違「現行牙已拒」 | 低 | `1-discussion.md:L179` 要保持機械拒，不是降成 warning |

### 決策點：Must-keep 去向語法
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| J 採 Q9 種子 | `M11 → R-x/S-y \| Non-Goal:<reason>`；不另發 ID；每條高影響 M 必有去向 | 與討論種子一致；Stage 4 可對帳 | 要人維護去向表 | 低 | `1-discussion.md:L177` Q9 種子；`L252` AC-7 |
| K 新 ID 家族 | 另發明 M-R／M-S | 看起來更「規格化」 | 第二條鏈；違 Q9／Non-Goals | 中 | `1-discussion.md:L165`；`L177` |
| L 只敘事不去向表 | 散文說「Must-keep 都要留」 | 寫起來快 | AC-7 對不到列；條目可無聲消失 | 低 | `1-discussion.md:L145` G-out-7；`L250-L253` AC-7 要形去向 |

### 決策點：Q8 dual-read 本檔鎖到哪
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| M 原則鎖、欄位交 F1 | 鎖：`2.0.0` 舊 7 不因 2.1.0 一次變紅；未 upgrade = 舊 7；doctor 綠 ≠ 路線沒變。欄位名／缺省不在本檔發明 | 不偷做 F1 annex；帶走 hop 身分 | annex 仍要寫欄位 | 低 | `1-discussion.md:L177` Q8 移交 F1；`L187` 採用 hop 身分；`L160-L167` brief 遷移（討論 L34／L57） |
| N 本檔寫死 annex 欄位名 | Decision 先發明 dual-read 欄位 | F1 少爭一次 | F0 寫明 annex 才寫；本 hop 會偷刀 | 中 | `1-discussion.md:L154` F1 才釘牙與 dual-read annex；`L177` Q8 `[>]` |
| O doctor 綠=路線沒變 | 用握手綠當「沒被遠端改線」 | 現場好記 | 討論已證 marketplace 可換 hops 而 doctor 仍綠 | 低 | `1-discussion.md:L187`；`L327-L330` |

## 方案架構圖
```
[A] Must-keep 當約束(選定)
[D] 拒收謂詞升 OC(選定)
[G] 空 attestation 拒(選定)
[J] Q9 去向語法(選定)
[M] dual-read 原則交 F1(選定)
```

## Decision
採 **A + D + G + J + M**。Goal 維持結果、不解成施工：人預設只在出貨停下來寫判定，中間謂詞假 = 停在該站修、不是改問人（G-out-1）；摺站之後 M1–M16 每一項仍成立，少一項是違規不是簡化成功（G-out-2）；後來寫規格／切任務的人，不能把「已經五站了」當成省略 ID 鏈、反模糊、T 四欄或 RED→獨立審查 seam 的理由，省略後的勾選仍看得出是未完成（G-out-3）；殺掉的是例行等人，Agent 代寫 `ACCEPTED`／Ship `PASS`、無 attestation 的 `ACCEPTED` 仍當沒寫（G-out-4）；已開工 slug 與舊契約讀舊 7 不一次變紅（G-out-5）；命中互動 trigger 時人仍親做 Demo 並寫 attestation，沒命中不產頁、不等第二次人（G-out-6）；本討論列出的 Must-keep 與現場痛點每條都有去向（G-out-7）；本 slug 自己出貨路徑仍是舊 7 直到 Ship，不拿自己當新 5 白老鼠（G-out-8）。

範圍：本 Decision 鎖定**怎麼綁** Must-keep／拒收謂詞／去向／Q11／dual-read 原則，供後站 4-spec 寫 R／S。F0 十條（五站別名、殺例行停、Ship 唯人、條件頁、UI twin 條件、Must-keep、dual-read 2.1.0、F0–F3 切刀、in-flight 凍舊 7、禁刪 G1／G2／`ACCEPTED`）**不重開**。本 hop 不改模板／graph／gate、不寫 coordinator、不 bump 契約。

## Decision 約束（後站不准改成可選）
1. **Must-keep M1–M16 少一條 = 違 brief**，不能寫成「已經五站了所以可省」。
2. **T 四欄（Covers／Files／Verify／Blocked-by）與 RED→獨立審查 seam 不可選。** Owner-locked。缺欄、無 RED 輸出、reviewer=implementer → 勾選仍算未完成。
3. Spec 的 S 仍吃反模糊三律；TBD／不可測／測試名不含 S-id 不得當完成。
4. 去向語法採 Q9：`M11 → R-x/S-y | Non-Goal:<reason>`。不另發 ID 鏈。
5. rewrite cap 已鎖：hop≤2／Decide≤1／Goal reopen≤1；用盡 Escalated；不准暗改。舊 7 不套這三 cap。
6. 採用 hop 身分：未 2.1.0 dual-read 前，marketplace 可換 hops 而 doctor 仍可綠；未 upgrade = 必須仍走舊 7。

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
| RP-13 | B1 命中、無 attestation，卻 hop 出 Spec → 紅 | 狀態機 §6.6、Q11、方案 G |
| RP-14 | latch 未命中卻留下「請人審」紀錄 → 紅 | 狀態機 §6.7 |
| RP-15 | 舊 7 in-flight slug 被寫入五站狀態 → 紅 | 狀態機 §6.8、G-out-5／8 |
| RP-16 | Agent 代寫 `ACCEPTED` 或 Ship `PASS` → 視為未寫並紅 | G-out-4、M5 |

F1 牙長在 `scripts/` 與 annex，不准改 Stage 1–4 模板。形狀欄位名交 F1 annex；本表是最小集合。

## Rejected Alternatives
- B:只把 Must-keep 當 brief 備忘，後站可裝沒看見；擋不住「可選四欄」寫進 Decision。
- C:另發 Must-keep ID 鏈，違 Q9 與「不新增第二條鏈」。
- E:拒收謂詞形狀全交 F1，本檔不升約束，規格可先把四欄寫成可選。
- F:現改 gate／模板把謂詞寫進去，違 F0 OC-10 與 Backlog B。
- H:chat「准開」當 attestation，重演 dogfood 蓋章，違 G-out-4。
- I:空 attestation 只警告不擋 hop，把已鎖的機械拒降成軟提醒。
- K:新 ID 家族，第二條鏈。
- L:只敘事不去向表，G-out-7／AC-7 對不到列。
- N:本檔寫死 dual-read 欄位名，偷做 F1 annex。
- O:把 doctor 綠當成路線沒變，忽略 marketplace 可換 hops。

## Rationale
C 線的第一因不是「五站別名還沒取好」，而是摺掉例行等人之後，Spec／Build 最容易用完整度填那個洞。Goal 是結果（人只在出貨停、M 全留、勾選看得到未完成），不是施工單。A 把 M 表與四欄／seam 升成 Decision 約束，讓後站省略必須留下去向或被看成違規。D 把已鎖的 F1 拒收謂詞寫進本方案要求＋OC「只准加不准減」，避免 E 把牙推成「形狀全交後刀、本檔不鎖」。G 守住 dogfood 已踩過的空 attestation 洞，不讓 H／I 把蓋章搬到 Demo。J 用討論已給的 Q9 種子，不另發明鏈。M 只鎖 dual-read 原則與 hop 身分，欄位留給 F1，避免 N 偷刀、O 誤讀 doctor。

F0 已鎖的五站路線、殺例行停、Ship 唯人、條件頁、禁刪 token，本檔當約束引用，不當再比一次的方案。重比那些 = 新 brief。

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 後站仍把 M11／M3／M1 寫成可選 | OC-2：出現「可選四欄／可選 seam／已五站故省反模糊」→ 本 slug G2 擋；Assumption「會偷 M」在本站按「會偷」處理 |
| F1 annex 減掉本表 RP | OC-1：最小集只准加不准減；減項 = 翻本 Decision，回本站 |
| Q6「採用現場也蓋章」為假 | 殺例行停的現場理由變弱，Must-keep 仍在；過期擋本 slug G2，不得把該假設當已核事實 |
| 本檔約束面長，被看成已施工 | 正文反覆寫「F0 不重開、本 hop 零模板／零牙／零 coordinator」；施工落 F1–F3 |
| 把本 slug 當新 5 白老鼠 | G-out-8＋OC-6；目錄已有站檔 = in-flight 舊 7 到 Ship |
| Quiz 被加回每次例行第三停 | RP-7＋OC-10；Quiz 只綁不可逆，可與 Ship 同一次人停 |
| dual-read 欄位在 4-spec 被先發明 | OC-7：欄位名／舊檔缺省只准 F1 annex；4-spec 只准引用原則 |
| 空 attestation 被 chat 蓋過 | 方案 G：口頭准開 ≠ attestation；RP-13 |

## Success Criteria
- SC-1（G-out-1）：F3 之後，新 slug 中間 latch 未命中時，前進紀錄沒有「請人審 A4／A7 提交判定」；謂詞假的停點理由是謂詞假，不是「先問 owner 要不要繼續」。
- SC-2（G-out-2）：任一次「五站已簡化」宣稱若 M1–M16 少一項，對帳輸出點名該項；不得出現「已經五站了」當省略理由。
- SC-3（G-out-3）：任一個 T 只看該卡，仍看得到非空 Covers（含 S-id）、Files、Verify、Blocked-by，以及 RED 輸出與不同於實作者的 reviewer；缺任一項不得標完成。
- SC-4（G-out-4）：Agent 寫入的 `ACCEPTED` 或 Ship `PASS`（無人類 attestation／無人頂欄）被系統當沒寫；不得離 Spec／不得 Done。
- SC-5（G-out-5）：F3 cut 當下已有站檔的 slug 仍走舊 7 到 Ship；`2.0.0` 讀檔不因 2.1.0 一次變紅；未 upgrade 的採用端不得被遠端改線。
- SC-6（G-out-6）：命中 B1 → 有人類 `ACCEPTED`+attestation 才准進 Build；未命中 → 無 Demo 頁、無第二次人停，n-a 有原因不是空白。
- SC-7（G-out-7）：本檔去向表每條高影響列（假完成 T、chat 蓋章、Demo 空欄開 4、M1–M16、rewrite cap、hop 身分）在 4-spec 能指到 `M → R-x/S-y | Non-Goal:<reason>`，沒有「Stage 1 寫過、後面消失」。
- SC-8（G-out-8）：本 slug 走到自己的 G1／條件 S3／G2／G3 時，五站自動前進跳不過；目錄沒有五站狀態寫入。
- SC-9（F1 最小集）：F1 牙能紅 RP-1…RP-16；annex 新增謂詞可以，刪本表任一列不行。
- SC-10（Q11）：B1 命中且 attestation 空、即使 chat 寫「准開下一站」，hop 出 Spec 仍紅。

## Scope & Non-Goals(定稿)
- In:A+D+G+J+M 收斂；Must-keep／四欄／seam 當 Decision 約束；RP-1…RP-16 當本方案要求；Q9 去向；Q11 空 attestation 仍拒；dual-read 原則＋hop 身分；Q6／Q8／Q10 著落；本 slug live freeze。
- Out:重開 F0 十條；改 `_templates/`／`graph.yaml`／gate token／既有牙；刪 G1／G2／`ACCEPTED`；寫 coordinator 或 event schema（F2）；發明 dual-read 欄位名（F1 annex）；把 in-flight／本 slug 折成五站；第二條 ID 鏈；把「蓋章很煩」解成「物質可省」；本 hop 改 STATUS／HISTORY；本 hop 宣稱 G1 PASS；本 hop merge。

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | RP-1…RP-16 是 F1 牙**最小集**：annex 只准加、不准減。使用者只鎖 Q7 三句＋「牙對 M 表」；把狀態機 §6 與 M1／M9／M10／M14 一併釘死是 owner 延伸 | 減項會讓「已五站」再次變成省略理由 | `1-discussion.md:L175` Q7；`L199-L215` 拒收欄；狀態機 §6。延伸本身 `[Assumption]`（§6 八條與 M 表對齊是本檔對帳） | F1 可刪 RP；SC-9 與 4-spec 對帳清單要重寫 | 待人審 |
| OC-2 | 本 slug 後站文檔若把 M1／M3／M11 或四欄／seam 標成可選，擋本 slug G2。這是對 Assumption「後站會偷 M」的 Stage 2 對帳，不是新 Goal | 討論已寫過期擋「可選四欄」寫進 Decision；本檔選 A 之後，後站再寫可選 = 違本 Decision | `1-discussion.md:L107`；`L125` | 可選四欄可進 4-spec；假完成 T 變合法簡化 | 待人審 |
| OC-3 | F1 牙只准長在 `scripts/` 與 annex，不准改 Stage 1–4 模板。使用者 Backlog B 已凍模板；「本 slug F1 也遵守」是收窄到本 feat | 觀測實驗還沒跑完；改模板污染觀測 | `1-discussion.md:L181`；`L29`；`L36` STATUS Backlog B | F1 可改 4-spec 模板句；與 F0 OC-10／觀測凍結衝突 | 待人審 |
| OC-4 | Q6 過期仍擋**本 slug G2**；不得把「採用現場都蓋章」寫成已核事實。使用者已鎖期限；本檔只收進 OC | 蓋章證據目前只有母版 dogfood 三案 | `1-discussion.md:L104`；`L123`；`L183` | 可把採用蓋章當 G2 事實；殺等待的現場理由被誇大 | 待人審 |
| OC-5 | Q8 欄位名與舊檔不紅缺省**不在本 Decision 發明**，只准 F1 annex。使用者把 Q8 標 `[>]`；「本檔連候選欄位名都不寫」是收窄 | 避免 N 偷刀；4-spec 只能引用原則 | `1-discussion.md:L177` Q8 | 4-spec／本檔先發明欄位；F1 annex 變追認 | 待人審 |
| OC-6 | 本 slug 整段舊 7 到 Ship，禁止當新 5 第一個白老鼠。使用者 Q12 已鎖；寫進 OC 是流程層複述，防後站「順便試五站 hop」 | 目錄已有站檔 = in-flight | `1-discussion.md:L181` Q12；`L146` G-out-8 | 本 slug 可被寫入五站狀態；觀測被自己污染 | 待人審 |
| OC-7 | Q10 coordinator event 與 cap **計數落點**移交 F2；本檔不選 event schema。cap 數字本身已鎖，不准暗改。使用者標 `[>]`；「schema 不在本檔」是收窄 | F0 寫明 F2 才接 event；暗改 cap = X5 | `1-discussion.md:L178` Q10；`L186` rewrite cap | 本檔或 F1 先發明 schema／放寬 cap | 待人審 |
| OC-8 | 不可逆才 Quiz；不准把 Quiz 加回每次例行第三個人停。使用者 Goal 是少等人；「Quiz ≠ 預設第三停」是對 M14 的收窄複述 | 每次 Quiz = 把例行人停加回，違 G-out-1 | `1-discussion.md:L213` M14；`L139` G-out-1 | Quiz 變每 feat 必停；或不可逆無 Quiz 也能合 | 待人審 |
| OC-9 | 本 hop **不**寫「跳過 Stage 3」。觸發判定留給第 3 站開場。無「Stage 3」+「跳過」流程層放行 | 互動 Pattern 已由 F0 表 A／B 鎖，但是否命中九條 trigger 仍要落檔；Agent 不得代決跳過 | `_templates/3-prototype.md` 觸發判定（討論 L47 引用）；模板跳過須人類明示 | 本檔先跳過 Stage 3；有 trigger 也無 Demo 紀錄 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 契約維持 `2.0.0`；本 hop 不 bump plugin／契約。
- `1-discussion.md` 保留 draft／當時計法；本檔才把 Requested solution 收成 Decision。不回改正本討論。
- feature branch 不改 `docs/dev/STATUS.md`、不改 HISTORY。
- 方案 token 用單字母 A–O，避免審頁／fig-text 把 H1／H2 收成同一 key。
- 獨立 A／B：本檔不讀、不引他線 `2-decision.md`。
- 審頁走 `scripts/build-stage2-html.py --action`；不手包 html-shell；不把本 hop 的 html 當成 G1 `verdict:` 正本。

## ADR 晉升檢查
- 難逆轉:否（G3 前可改本檔 Decision／OC；F0 鎖定面已在 `notes/design/`，不是本 hop 才變成難逆）
- 反直覺:是（少等人卻把更多完整度升成約束；「已五站」不是省略理由）
- 真 trade-off:是（等待↓ vs 假完成 T；本檔釘謂詞 vs 偷做 F1）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-13 | 使用者指派 Implementer C、lane full、Must-keep／anti-hollow Spec-Build 當 Decision 約束、F1 拒收謂詞進 OC 或本方案要求、Goal 純度、F0 不重開。五個決策點：防掏空綁法／拒收謂詞落點／Q11／去向語法／dual-read 鎖到哪
- 1-discussion 接手 | 2026-09-13 | 正本 frontmatter 仍 draft；以 Human PASS + 本 hop 指派為入口。OQ 三態齊（`[x]`／`[~]`／`[>]`）。不回改正本討論
- `[>]` 著落 | 2026-09-13 | Q8→方案 M＋OC-5；Q10→OC-7；Q11→方案 G＋RP-13＋SC-10
- 本 hop 不送 G1 verdict、不改 STATUS、不合併 | 2026-09-13
