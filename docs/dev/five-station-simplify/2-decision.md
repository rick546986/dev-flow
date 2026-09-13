---
feature: five-station-simplify
stage: 2-decision
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-13
---

# 2. 收斂 — 五站簡化（Implementer A：謂詞先摺、作者冷凍）

> 把 `1-discussion.md`（Stage 1 winner C on main, Human direction PASS, #295）收成 Decision。
> Lane = **full**。本 hop **只 Stage 2**；`verdict` 留空等人類 G1；不改 STATUS／HISTORY；不合併。
> 獨立於 Stage 2 B／C。不實作 F1 牙、不改 `_templates/`／`graph.yaml`、不刪 G1／G2／`ACCEPTED`。
> 1-discussion 留 draft／「不送 G1」原文；改口記在本檔。

## Real-world 去向

| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| Journey「例行停;人用 chat 蓋章」 | 本方案處理 | 1A 殺例行人停;物質與 token 留 |
| Journey「方向卡沒被讀完也過」 | 本方案處理 | 預設人停只剩 Ship;中間改謂詞 |
| Journey「Demo 欄空仍開 Stage 4」 | 本方案處理 | 3A／OC-1:空 attestation 仍機械拒 |
| Journey「四欄／seam 被省,勾選假完成」 | 本方案處理 | 2A:T 四欄＋seam Owner-locked |
| Journey「中間三次已耗盡注意力」 | 本方案處理 | 1A:等人次數不再等於站數 |
| Journey「沒標準回報口;痛是真的」 | 刻意維持 | 採用逐字稿禁收;物質洞已進 Context |
| Workaround「Treat as PASS／都過／可以」 | 本方案處理 | 殺例行停的現場依據=母版 dogfood |
| Workaround「Agent 把口頭章落進 md」 | 本方案處理 | M5:代寫 `ACCEPTED`／Ship `PASS`=未寫 |
| Workaround「採用現場洞靠 owner 口頭中繼」 | 刻意維持 | public repo 禁收公司路徑 |
| Exception「Fast 仍吃 G2 物質」 | 刻意維持 | 不廢 Fast;Profile／Demo 條件仍在 |
| Exception「Owner Call 可明示跳過 Stage 3」 | 刻意維持 | B1 沒命中本來就不產頁 |
| Exception「in-flight 整段舊 7」 | 本方案處理 | 4A＋OC-10;本資料夾已 in-flight |
| Exception「F0–F2 新開軌仍舊 7」 | 本方案處理 | 4A;F3 前雙路線污染觀測 |
| Exception「owner 自審是最後手段」 | 刻意維持 | brief §8;不准假裝四眼 |
| `[Assumption]`「採用現場也 chat 蓋章」 | 仍待驗 | OC-5:不升格;過期擋本 slug G2 |
| `[Assumption]`「後站會偷 Must-keep」 | 本方案處理 | 2A 對帳;Decision 不准把 M 標可選 |
| `[Assumption]` A1／A2 共寫 `1-discussion.html` | 仍待驗 | OC-6:F1 annex 前不加雙檔名牙 |
| M1 ID 鏈;測試名含 S-id | 本方案處理 | 2A;F1:測試名不含 S-id → 紅 |
| M2 圍欄 | 本方案處理 | 實作者仍禁讀 1／2／3 補洞 |
| M3 反模糊三律 | 本方案處理 | 2A;F1:S 含 TBD／不可測 → 紅 |
| M4 Real-world→Demo→OC | 本方案處理 | 3A;B1 命中才 latch |
| M5 人寫 `ACCEPTED`／Ship `PASS` | 本方案處理 | 3A／OC-1;Agent 代填=未寫 |
| M6 G3 Evidence 八點 | 本方案處理 | Ship 物質不動 |
| M7 Profile+`fast`+`high` 拒 | 本方案處理 | A8 自動前進謂詞已列 |
| M8 DBC 條件式 | 本方案處理 | B5;不是新站 |
| M9 Files ⊆ 5-tasks | 本方案處理 | 2A;缺 Files 或 Files ⊈ 聯集 → 紅 |
| M10 驗證五律 | 本方案處理 | 2A;無原始輸出 → 紅 |
| M11 T seam＋四欄 | 本方案處理 | Owner-locked;缺四欄／無 RED／自審 → 未完成 |
| M12 author≠approver | 本方案處理 | Ship 與任何 latch |
| M13 html 重生 | 本方案處理 | 本 hop 仍用 `build-stage2-html.py --action` |
| M14 不可逆才 Quiz | 本方案處理 | 2A;Quiz ≠ 預設第三停 |
| M15 token／檔仍在 | 本方案處理 | 1A 拒 1B;X2 |
| M16 F0 不改 graph／牙 | 本方案處理 | 5A;本 hop 一字不改 |
| rewrite cap hop≤2／Decide≤1／Goal reopen≤1 | 本方案處理 | 4A;計數落點移交 F2(Q10) |
| 採用 hop 身分:marketplace 可換 hops 而 doctor 仍綠 | 本方案處理 | 4A;未 2.1.0 = 必須舊 7 |
| 本 slug = live freeze 樣本 | 本方案處理 | 4A／OC-10;G-out-8 |
| Q8 dual-read 欄位與舊檔不紅缺省 | 本方案處理 | OC-2;條文進 F1 annex,本檔不鎖 Schema |
| Q10 coordinator event 與 cap 計數落點 | 本方案處理 | OC-3;F2 才接 event schema |
| Q11 空 attestation 五站後是否仍拒 | 本方案處理 | 3A／OC-1;現行牙保持 |

## Approaches Considered

### 決策點 1：摺什麼
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 1A | **謂詞先摺**:預設路線=Intake→Decide→Spec→Build→Ship 別名;殺例行 G1／S3-`ACCEPTED`／G2 **人停**;檔、token、牙、twin **全留**;Ship 唯一人類預設停;條件頁走表 A／B 謂詞 | 對準 G-out-1／F0 OC-1…OC-5;等人次數不再等於站數;dual-read／舊 7 仍有錨 | 中間無人盯卡,寫手可能拿完整度填洞(決策點 2 擋) | 中 | `notes/design/five-station-simplify-brief-v3.md:L13-L28` 摺停點不摺完整度;`L30-L45` OC-1…OC-5;`L47-L58` 別名不是新檔名;`L86-L97` 表 A latch;`1-discussion.md:L138-L146` G-out-1／4／6;`docs/dev/dogfood-ping/2-decision.md:L110` 蓋章。成本 `[Assumption]` |
| 1B | **刪 token 好寫謂詞**:拿掉 G1／G2／`ACCEPTED` 檔或 `check-gate-tokens.sh` 錨,五站謂詞少幾個例外 | coordinator 比較好寫 | 舊 7 與 dual-read 一次紅;in-flight 無錨;違 OC-10／X2;G-out-5 落空 | 高 | `notes/design/five-station-simplify-f0-state-machine.md:L189-L201` X2;`1-discussion.md:L32` 禁刪;`L210-L214` M15;`scripts/check-gate-tokens.sh:L44-L60` token 正本;`docs/dev/readme-contract-extract.md:L7-L17` 現行仍七份+三閘 |
| 1C | **維持七站例行人停**直到 Backlog B 完整 full-lane 觀測做完 | 不碰現況 graph;觀測不被路線污染 | 痛已在:母版 dogfood 同日 chat 簽 G1／G2;等人被站數綁死;F0 已鎖殺例行停,再等觀測=重開十條 | 低 | `skills/dev-flow/stage2/graph.yaml:L53-L57` `N7-g1`;`skills/dev-flow/stage4/graph.yaml:L93-L98` `N6-g2`;`docs/dev/STATUS.md:L50` Backlog B 凍的是**模板**不是 F0 十條;`1-discussion.md:L50-L54` dogfood 蓋章。觀測能治蓋章 `[Assumption]`(為假:等越久蓋章越多) |

### 決策點 2：Must-keep 怎麼防掏空
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 2A | **M 表拒收謂詞 + T 四欄鎖死 + 去向帳**:M1–M16 少一條=違 brief;F1 牙最少咬 Q7(缺四欄→紅;無 RED／reviewer=implementer→T 未完成;S TBD／不可測→紅)以及 M 表已列謂詞(M1 測試名、M9 Files 聯集、M10 原始輸出、M14 Quiz);去向語法見 Q9 種子(R／S 或 Non-Goal 理由);不另發 ID | 對準 G-out-2／3／7;勾選不能冒充完成;C 線主風險有牙 | 牙長在 scripts／annex,形狀仍移交 F1;「高影響」抽樣要人判 | 中 | `notes/design/five-station-simplify-brief-v3.md:L135-L158` M1–M16;`1-discussion.md:L175` Q7;`L177` Q9;`L185` Owner-locked 四欄＋seam;`L198-L215` M 表拒收謂詞;`_templates/5-tasks.md:L50`;`_templates/6-implementation-notes.md:L104-L137`;`docs/dev/readme-contract-extract.md:L28-L34`。形狀細節 `[Assumption]`(F1 annex) |
| 2B | **「已五站」可選省略**:摺站後把 T 四欄／seam／反模糊標成簡化細節,只留精神 | 寫手最短;任務板看起來乾淨 | 假完成 T;Ship coverage 對不上 S;違 G-out-3;Stage 1 已寫過期擋「可選四欄」 | 低 | `1-discussion.md:L107` 後站偷 Must-keep 假設;`L125` 過期擋把可選四欄寫進 Decision;`L141` G-out-3;`L307-L310` 假完成定義。現場真會偷 `[Assumption]`(無未來 log;本檔用 2A 對帳,不把 M 標可選) |
| 2C | **另發 Must-keep ID 鏈**或只寫「精神留下」無拒收謂詞 | 機械對帳看起來乾淨;或零牙 | 第二條 ID 鏈=Stage 1 Non-Goal;無謂詞=F1 不知咬什麼;精神清單擋不住 checkbox | 高 | `1-discussion.md:L165` 不新發第二鏈;`L177` Q9 種子已拒另發 ID;`notes/design/five-station-simplify-f0-state-machine.md:L202-L213` F1 最少要能紅具體行為 |

### 決策點 3：條件頁與空 attestation（Q11）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 3A | **表 A／B 謂詞 + 空證仍拒**:生成謂詞假→不產頁;latch 假→不准問人;B1 命中→人類 `ACCEPTED`+attestation 仍機械必要;沒命中→不產 Demo、無第二次人停;Agent 代寫=未寫 | 對準 G-out-4／6、AC-4／6;殺的是例行等、不是 Demo 主權;Q11 收口 | 命中時仍等人(一次,不是例行中閘) | 中 | `notes/design/five-station-simplify-brief-v3.md:L39-L41` OC-4／OC-5;`L101-L117` 表 B;`L187-L198` 誰准寫判定;`notes/design/five-station-simplify-f0-state-machine.md:L82-L96` B1 互斥;`L110-L120` Ship 禁代寫;`1-discussion.md:L179` Q11;`docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9` 空欄仍開 4。現行牙五站後仍在 `[Assumption]`(F1 必須保持,本檔鎖「保持」) |
| 3B | **摺停後空 attestation 可 hop**(複製 dogfood:chat 准下一站) | 最快;中間完全沒人 | 蓋章從 G1 搬到「准開下一站」;AC-4 落空;違 M5 | 低 | `1-discussion.md:L91-L95` Workaround;`L113-L114` dogfood 證據;`L238-L241` AC-4 要擋這型 |
| 3C | **每站都產頁、都等人**(現況) | 審頁齊 | 與 1A 互斥;A4／A7 latch 加回=X8 | 低 | `notes/design/five-station-simplify-brief-v3.md:L86-L99` A4／A7 latch=否;`notes/design/five-station-simplify-f0-state-machine.md:L201` X8 |

### 決策點 4：遷移、freeze、marketplace／doctor、本 slug
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 4A | **dual-read 2.1.0 + 活冷凍**:契約 minor 2.1.0 同時讀舊 7 與新 5,舊檔不一次變紅(欄位 F1 annex);`docs/dev/<slug>/` 已有任一站檔→整段舊 7 到 Ship;本 slug 是第一個 live freeze 樣本;未 upgrade 到 2.1.0 前,`marketplace update` 可換 hops 而 doctor 因 `2.0.0` 仍綠 → **doctor 綠 ≠ 已切五站**;rewrite cap hop≤2／Decide≤1／Goal reopen≤1 用盡 Escalated,不准暗改;舊 7 **不套**這三 cap | 對準 G-out-5／8、AC-5／8;採用端不被遠端改線;本包不污染自己的觀測 | 本 slug 設計五站卻走舊 7,看起來慢;cap 計數落點仍移交 F2 | 中 | `notes/design/five-station-simplify-brief-v3.md:L42-L45` OC-7…OC-9;`L131` cap;`L160-L169` 遷移;`notes/design/five-station-simplify-f0-state-machine.md:L122-L139` cap 計法;`L49-L50` in-flight 不建新機;`1-discussion.md:L180` Q12;`L187` 採用 hop 身分;`L146` G-out-8;`hooks/_doctor_impl.py:L193-L202`;`skills/dev-setup/SKILL.md:L16` `L62-L68`;`devflow-contract.json:L1-L3`。採用現場已被遠端改線 `[Assumption]`(無採用 log;4A 鎖「未 upgrade=舊 7」) |
| 4B | **本 slug 當新 5 第一隻白老鼠**:自己的 G1／G2 改走五站自動前進 | 立刻 dogfood 新機 | 觀測被自己污染;違 OC-9／G-out-8／X4;本資料夾已有站檔=已 in-flight | 高 | `1-discussion.md:L146-L147` G-out-8;`L180` Q12 已鎖不是交接;`L254-L257` AC-8;`notes/design/five-station-simplify-f0-state-machine.md:L196` X4 |
| 4C | **marketplace 一更新就遠端切五站**;或 doctor 綠=路線已變 | 採用端「自動跟上」 | 契約握手仍 `2.0.0` 時 hops 已換;違「未 upgrade=舊 7」;現場無標準回報口 | 高 | `1-discussion.md:L327-L330` marketplace 可改 hops 而 doctor 仍綠;`notes/design/five-station-simplify-brief-v3.md:L168` 不得遠端改別人 repo |

### 決策點 5：本 hop 切刀
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 5A | **本 hop 只落 Decision**:md＋`build-stage2-html.py --action` 審頁;F1=牙＋dual-read annex;F2=coordinator;F3=cut;本 PR 不改模板／graph／token／STATUS,不寫 F1 碼 | 對準 OC-8／OC-10;Backlog B 凍 Stage 1–4 模板;N7 審頁契約 | F1 牙本 hop 還不紅;只靠 Disposition／OC 約束後站 | 低 | `notes/design/five-station-simplify-brief-v3.md:L7-L9` F0 禁改;`L171-L181` 四刀;`docs/dev/STATUS.md:L50` 凍模板;`L34` Active 在 1-discussion、Gates 仍白;`1-discussion.md:L158-L166` Non-Goals;`notes/design/stage2-review-ui-contract.md:L17-L25` 直式 SVG。本 hop brief:只 Stage 2、不改 STATUS |
| 5B | **本 PR 開始寫 F1 牙**(scripts／annex 或改模板) | 謂詞立刻可紅 | 偷做 F1;若改模板=違 Backlog B＋F0;本 hop 範圍爆炸 | 高 | `notes/design/five-station-simplify-brief-v3.md:L173` F0 不准偷做 F1;`1-discussion.md:L191` F1 牙只准 scripts／annex |
| 5C | **跳過 Stage 2 直接 F1** | 少一份 Decision | 無 Adopted／Rejected／OC 帳;後站可裝沒看見 M 表;違 full lane | 中 | `_templates/2-decision.md:L13` G1 後才寫規格;`docs/dev/readme-contract-extract.md:L12` G1=方向＋OC 全裁決 |

## 方案架構圖
[1A] 五站殺例行停(選定)
[2A] M表牙+T四欄(選定)
[3A] 空attestation仍拒(選定)
[4A] 2.1.0+本slug舊7(選定)
[5A] 本hop只Decision(選定)

## Decision
採 **1A+2A+3A+4A+5A**:新世代預設路線是五站別名 Intake→Decide→Spec→Build→Ship,檔名家族不換;例行 G1／S3-`ACCEPTED`／G2 不再是人類必停,機制／檔／token／牙全留;Ship 是唯一預設人類停點,coordinator 禁代寫 `verdict:`。條件頁走表 A／B:生成謂詞假不產頁,latch 假不准問人;B1 命中時人類 attestation 仍機械必要,空欄或 Agent 代寫=未寫。M1–M16 一項都不能因「已經五站了」消失;T 四欄(Covers／Files／Verify／Blocked-by)與 RED→獨立審查 seam 是 Owner-locked,不是可選簡化;F1 牙咬 Q7 最小集＋M 表已列拒收謂詞;去向用 `M11 → R-x/S-y | Non-Goal:<reason>`,不另發 ID。契約 minor 2.1.0 dual-read(欄位 F1 annex);in-flight 與本 slug 整段舊 7 直到 Ship;未 upgrade 時 marketplace 換 hops 而 doctor 仍綠 ≠ 已切五站;rewrite cap 已鎖,舊 7 不套。本 hop 只落本 Decision;F1→F2→F3 分刀。不選刪 token、不選可選省略 Must-keep、不選空證可 hop、不選本 slug 當新 5 白老鼠、不選本 PR 寫 F1 碼。G1 尚未人類裁決;本檔 `verdict` 空。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| 1B 刪 G1／G2／`ACCEPTED` token | 舊 7 與 dual-read 失去錨;X2;不是簡化成功。 |
| 1C 維持七站例行人停 | F0 已鎖殺例行停;dogfood 已證中閘被蓋章;再等觀測=重開十條。Backlog B 凍的是模板。 |
| 2B 「已五站」可選省略四欄／seam | 假完成 T;G-out-3 落空;過期擋把可選四欄寫進 Decision。 |
| 2C 另發 Must-keep ID 或只留精神 | 第二鏈已禁;無拒收謂詞 F1 不知咬什麼。 |
| 3B 空 attestation 可 hop | 複製 dogfood 捷徑;AC-4 要擋。 |
| 3C 每站產頁都等人 | 把 A4／A7 例行停加回;X8。 |
| 4B 本 slug 當新 5 白老鼠 | 本資料夾已 in-flight;G-out-8／X4。 |
| 4C marketplace 遠端切五站 | doctor 綠只證明契約 `2.0.0` 握手,不證明路線沒變。 |
| 5B 本 PR 寫 F1 牙 | 偷做 F1;違四刀與本 hop brief。 |
| 5C 跳過 Stage 2 | 無 OC／Rejected 帳;full lane 要求 G1 後才寫規格。 |
| 六站／四站／改檔名家族 | OC-1:五站別名;七份檔名不動。 |
| 機械綠自動 Done | OC-3／X1;Agent 寫 `PASS`=未寫。 |
| 暗改或 reset cap | X5;舊 7 不套這三 cap,不是放寬。 |
| 本 hop 改 STATUS／發明 G1 PASS | 流程層 OC-4;Gates 仍白。 |

## Rationale
第一因不是「站太多」,是「等人的次數被站數綁死,而蓋章已經發生」。graph 把人類停寫進預設 hop(`N7-g1`／`N6-g2`)。物質(OC 全裁決、R/S、Profile、Demo 條件、Evidence 八點)與「按提交判定」不是同一物。1A 摺停點、留物質。1B 刪錨,in-flight 無路。1C 假裝 F0 沒鎖。

摺完之後,洞會被完整度填上。Build 謂詞靠四欄＋seam。若 Spec 寫 TBD(偷 M3)或 Build 讓 Verify 變成「看起來沒問題」、跳 RED、實作者自審(偷 M11／M10／M12),checkbox 仍可勾。2A 把這標成未完成,不是簡化。2B 是 C 線主風險本身。2C 另造方法論或把牙變成散文。

Q11 選 3A:殺例行停之後,B1 命中仍是一次 HumanWait。空 attestation 可 hop(3B)只是把蓋章搬家。3C 把例行停加回。

遷移選 4A,因為 hops 住方法包。`marketplace update`＋`plugin update` 換的是 hops,doctor 只查契約版本 ∈ `supported_contract_versions`。現在正本仍 `2.0.0`,所以 doctor 可綠、路線可已被遠端改。這不是 F1 才發現的驚喜。4B 拿自己當白老鼠,污染觀測。4C 把 doctor 綠當成切線證明。

本 hop 選 5A:F0 只落設計;下一刀才是牙。本 PR 若寫 F1 碼或改模板,就是違 brief 與 Backlog B。Decision 的工作是把 Stage 1 帶走項寫成不可無聲消失的帳。

## 既有脈絡
對帳快照(2026-09-13 tip `894960f`,#295／#298 之後):

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| F0 brief＋狀態機 | Owner 已核;十條鎖死 | 1A–5A 只跟這兩檔,不跟對話記憶 |
| Stage 1 winner C | `1-discussion.md` status=draft;Human direction PASS(#295) | 1-discussion 留當時說法;本檔改口 |
| STATUS Active | five-station-simplify @ 1-discussion;G1⬜ G2⬜ G3⬜ | 本 branch 不改正本(OC-4) |
| STATUS Backlog B | 完整 full-lane 觀測前不動 Stage 1–4 模板 | F1 牙只准 scripts／annex;不解凍 |
| 現行契約 | 七份文檔＋G1／G2／G3;`2.0.0`;plugin `3.24.0` | dual-read 2.1.0 進 F1;本 hop 不 bump |
| graph 預設停 | Stage 2 `N7-g1`;Stage 4 `N6-g2` | 殺的是例行人停,不是節點／token |
| T 四欄／seam | `_templates/5-tasks.md`／`6-implementation-notes.md` 已必填 | Owner-locked;省略=未完成 |
| doctor／marketplace | 握手看契約版本;hops 隨 plugin 更新 | 4A:綠 ≠ 五站 |
| 本目錄 | 已有 `1-discussion.md` | in-flight;整段舊 7 到 Ship |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 後站用「已五站」省略 M11／M3／M1 | 2A:Decision 把四欄／seam／反模糊標 Owner-locked。F1 牙紅缺欄／TBD／無 S-id 測試名。本檔若出現「可選四欄」=違 Decision |
| Agent 代寫 Ship `PASS` 或 `ACCEPTED` | 3A／OC-1:當未寫。F1 最少咬狀態機 §6 第 1／6 條 |
| marketplace 更新後採用端被遠端改線 | 4A:未 2.1.0 dual-read = 必須舊 7。doctor 綠不得當切線證據。F1 annex 寫缺省 |
| 本 slug 被當成新 5 白老鼠 | OC-10:本目錄 hop 仍走舊 7 的 G1／條件 S3／G2／G3。五站自動前進寫入=違 |
| cap 用盡後 reset 再 hop | X5;數字本檔重申;計數落點 F2,不准本 hop 發明 schema 來「先寬鬆」 |
| Q6「採用也蓋章」被升格成已核事實 | OC-5:維持 Assumption;過期擋本 slug G2。殺例行停的現場依據只引用母版 dogfood |
| A1／A2 其實已分檔,F1 白做雙檔名牙 | OC-6:本檔不加牙;F1 annex 先讀兩支產檔器 dest |
| 本 PR 被當成已過 G1 或已改模板 | `verdict` 空;`status` draft;檔清單只有本目錄 2-decision.md／.html |
| 並行 B／C 文案互蓋 | 獨立 PR;不讀、不抄 B／C;winner 另裁 |
| 條件 Demo 與「chat 准下一站」並存 | OC-1:attestation 空仍拒;不得用 chat 繞 B1 |

## Success Criteria
- SC-1(G-out-1):F3 cut 之後,一條**新** slug 走完 Decide／Spec／Build 且中間 latch 未命中 → 前進紀錄沒有「請人審 A4／A7」;謂詞假時停在該站修,理由不是「先問 owner 要不要繼續」。對照:本 slug 自己**不得**用這條當已切五站的證據(見 SC-8)。
- SC-2(G-out-2):一份宣稱「五站已簡化」但 M1–M16 少一項的對照稿,對 brief §5 被點名違規;不得出現「已經五站了」當省略理由。
- SC-3(G-out-3／T 四欄):一個 T 缺 Covers／Files／Verify／Blocked-by 任一,或無 RED 輸出,或 reviewer=implementer → 不得當完成。對照稿「Verify: 看起來沒問題」必須紅或標未完成。
- SC-4(G-out-4／Q11):Agent 寫入 `ACCEPTED` 或 Ship `PASS`,或 B1 命中但無人類 attestation → 系統當沒寫;不得離 Spec／不得 Done。B1 未命中 → 無 Demo 頁、無第二次人停。
- SC-5(G-out-5):F3 cut 當下已有任一 1–7 檔的 slug 仍走舊 7(含例行 G1／G2);2.1.0 dual-read 讀舊檔不一次變紅。
- SC-6(marketplace／doctor):未 upgrade 到 2.1.0 的採用專案,`marketplace update` 之後 doctor 仍可因契約 `2.0.0` 綠;該綠不得被寫成「已切五站」。未 upgrade = 必須舊 7。
- SC-7(rewrite cap):新 5 路線 slug,同一 hop 第 3 次重寫、Decide 第 2 次整站重開、離開 Intake 後第 2 次改 Goal → Escalated,不得暗改數字。舊 7 slug(含本 slug)不套這三 cap。
- SC-8(G-out-8):本 slug 走到自己的 G1／G2／G3 時,五站自動前進跳不過;目錄無五站狀態寫入;仍有例行 G1／條件 S3／G2／G3。
- SC-9(G-out-7):本檔 Real-world 去向表列的每一條高影響 M／Journey／cap／採用 hop 身分,到 4-spec 都有 `M11 → R-x/S-y | Non-Goal:<reason>` 形著落;標「本方案處理」者至少一條 R／S。
- SC-10(本 hop Non-Goal):本 PR 檔清單 ⊆ `docs/dev/five-station-simplify/2-decision.md` 與同目錄 `2-decision.html`;未改 `_templates/`／`graph.yaml`／gate token／STATUS／HISTORY;未刪 G1／G2／`ACCEPTED`;未寫 F1 腳本。`verdict` 仍空,直到人類 G1。

## Scope & Non-Goals(定稿)
- In:1A 五站別名＋殺例行人停＋留 token;2A M 表拒收謂詞＋T 四欄／seam Owner-locked＋Q9 去向語法;3A 表 A／B 謂詞＋Q11 空證仍拒;4A dual-read 2.1.0(版本鎖、欄位不鎖)＋in-flight／本 slug 凍舊 7＋marketplace／doctor 陷阱＋rewrite cap 數字;5A 本 hop 只 Decision＋審頁;Q6 維持 Assumption;Q8／Q10 移交落點。
- Out:1B／1C;2B／2C;3B／3C;4B／4C;5B／5C;六／四站;改檔名家族;刪 G1／G2／`ACCEPTED`;本 PR 寫 F1 牙／coordinator／cut;本 PR 改 `_templates/`／`graph.yaml`／README §7 錨／STATUS／HISTORY;發明 G1 PASS;把本 slug 折成五站;另發 Journey／Actor／Must-keep ID;把 Quiz 當每次例行停;遠端改採用端路線。

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | Q11 收口:**五站之後** B1 命中且 attestation 空,或 Agent 代寫 `ACCEPTED`／Ship `PASS`,仍機械拒。B1 未命中不要求 `ACCEPTED`、不產頁。使用者把 Q11 交給 Stage 2;「保持現行牙、不放寬」是本檔收口 | 3B 複製 dogfood 捷徑;殺例行停不是殺 Demo 主權 | `1-discussion.md:L179` Q11;`docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9`;`notes/design/five-station-simplify-f0-state-machine.md:L90-L96` `L187`。五站後牙仍接同一支 `[Assumption]`(F1 接,本 hop 不改腳本) | 空證可 hop;或未命中也要 `ACCEPTED`(3C 變種) | 待人審 |
| OC-2 | Q8 收窄:dual-read **版本**鎖 2.1.0;欄位名／舊檔缺省／不紅規則**不**進本檔,進 F1 annex。使用者只鎖「必須 dual-read」;「本 hop 不發明 Schema」是收窄 | 本 hop 假鎖欄位會逼 F1 跟 Decision 打架 | `1-discussion.md:L176` Q8;`notes/design/five-station-simplify-brief-v3.md:L164`。annex 欄位 `[Assumption]` | 本檔鎖 JSON 欄;或把 2.1.0 改成別的 minor | 待人審 |
| OC-3 | Q10 收窄:cap **數字**已鎖;event schema／計數落點留給 F2。不准本 hop 用「先寫寬鬆計數器」暗改 cap | 狀態機已鎖數字與計法;落地從 F2 | `1-discussion.md:L178`;`notes/design/five-station-simplify-f0-state-machine.md:L122-L155`。schema `[Assumption]` | 本檔發明 event;或放寬 hop≤2 | 待人審 |
| OC-4 | 本 feature branch **不**跑 `status-update.sh`、不改 HISTORY、不把本檔 `verdict` 寫成 PASS。1-discussion 保持 draft。標**流程層** | 母版 STATUS 只在整合分支維護;G1 人類後裁;使用者禁發明 PASS | `docs/dev/STATUS.md:L10-L26` `L34`;`1-discussion.md:L153`;本 hop brief | 本 PR 帶 STATUS 列或自填 PASS,與並行 session 互蓋 | 待人審 |
| OC-5 | Q6 與「採用現場也蓋章」:**不**升格成已核事實。殺例行停的現場依據只引用母版 dogfood 三案。過期仍擋本 slug G2。這是對「現場都蓋章」的收窄 | 無採用逐字稿;升格=用假設當 G1 背書 | `1-discussion.md:L105` `L123` `L174`;`docs/dev/dogfood-ping/2-decision.md:L110`。採用是否同手勢 `[Assumption]` | 把 Q6 當已核;或因無 log 擋本 G1 | 待人審 |
| OC-6 | A1／A2 共寫 `1-discussion.html` 維持 Assumption。本 Decision **不加**雙檔名拒收謂詞。F1 annex 先核兩支產檔器 dest | 若已分檔,F1 不必為雙檔名加牙 | `1-discussion.md:L108` `L61`;`scripts/build-stage1-html.py` 與 `scripts/build-scan-html.py` 現況同 dest。是否已分檔 `[Assumption]` | Scope 變成 F1 必做雙檔名牙 | 待人審 |
| OC-7 | F1 牙**只准**長在 `scripts/` 與 annex,不准改 `_templates/` 1–4。本 Stage 2 **不解凍** Backlog B。使用者只鎖 Must-keep 與 Q7;「牙的落點＋不解凍」是延伸 | 觀測前改模板=污染;requirement-discovery-gaps 曾解凍是另一 slug 的 OC,不套用 | `docs/dev/STATUS.md:L50`;`1-discussion.md:L191`。本 slug 不解凍 `[Assumption]`(owner 可另裁,須回本站) | 本包改 Stage 1–4 模板;或另造第三套牙家族 | 待人審 |
| OC-8 | 本檔 Real-world 去向表=Q9 帳本。Stage 4 標「本方案處理」者至少一條 R／S;不另發 M-id。使用者只給種子語法;「本表就是帳、後站必接」是延伸 | 無帳=Stage 1 帶走項可無聲消失(G-out-7) | `1-discussion.md:L177` `L145` `L250-L253`。哪些列算高影響本表已列;漏列 `[Assumption]` | 改用第二鏈;或 Stage 4 只寫「有處理」散文 | 待人審 |
| OC-9 | F1 拒收謂詞**不得少於** Q7 最小集＋Stage 1 M 表已列項(M1 測試名不含 S-id;M3 TBD／不可測;M9 Files 缺或不 ⊆ 聯集;M10 無原始輸出;M11 缺四欄或無 RED 或 reviewer=implementer;M14 不可逆無 Quiz)。使用者只鎖「Must-keep 留下」;「這些謂詞不可標可選」是延伸 | 2B 的入口就是把謂詞寫成可選 | `1-discussion.md:L175` `L198-L215`;`notes/design/five-station-simplify-f0-state-machine.md:L202-L213`。F1 可加、不准減 `[Assumption]` | F1 只咬精神;或把 M14 Quiz 當每次例行停 | 待人審 |
| OC-10 | 本 slug 自己的 G1／條件 S3／G2／G3 **仍依舊 7 開火**。本 Decision 不得在本目錄寫入五站自動前進狀態。Q12 已鎖;「連本 Stage 2 也不切自己」是延伸 | 資料夾已存在=in-flight;拿自己 dogfood 新機=X4 | `1-discussion.md:L180` `L254-L257`;`notes/design/five-station-simplify-brief-v3.md:L165`。本 hop 無人誤切 `[Assumption]` | 本 slug 改走五站 hop;SC-8 失效 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 本 hop 不 bump plugin／契約;正本仍 `2.0.0`。
- `1-discussion.md` 保留 draft／「不送 G1」原文;本檔才改口成 Decision。
- 審頁用 `scripts/build-stage2-html.py --action`,不手包 html-shell,不把審頁塞進 `build-gate-twin.py` STAGES,不用 `build-scan-html.py`。
- 方案架構圖直式 `[標籤] 標題(選定)`;Decision 置頂後 SVG。
- 第 3 站維持條件式;本檔無流程層 OC 把 Stage 3 標成跳過。本 slug 走舊 7,G1 人類後才評 Stage 3 觸發。
- F1 annex 再釘:dual-read 欄位、舊檔缺省、A1／A2 dest、牙腳本檔名。F2 再釘:event schema、cap 計數落點。
- 獨立於 Stage 2 B／C;不抄並行稿。

## ADR 晉升檢查
- 難逆轉:否(本 hop 只落 Decision;F3 才切路線;G3 前可改本檔)
- 反直覺:是(殺等待卻留 token;doctor 綠 ≠ 改線;設計五站的 slug 自己走舊 7)
- 真 trade-off:是(摺停 vs 假完成;freeze vs 自我 dogfood;本 hop 不寫牙 vs 後站可裝沒看見)
→ 晉升:**否**(三條件未全中;留在本檔。不抄 `docs/adr/`)

## 確認紀錄
- 決策點清單確認 | 2026-09-13 | Stage 2 brief(Implementer A):覆蓋五站＋殺例行停;M 表拒收謂詞;採用 marketplace／doctor 陷阱;rewrite cap;freeze;T 四欄鎖死;本 hop 不實作 F1。五決策點對應該鎖板。Human direction PASS = Stage 1 winner C 合 main(#295),不是 1-discussion frontmatter approved。
- Stage 1 改口 | 2026-09-13 | 1-discussion 仍 draft、Q6 `[~]`、Q8／Q10 `[>]`、Q11 原移交 Stage 2。本檔改口為 Decision,並收口 Q11(OC-1)、收窄 Q8／Q10(OC-2／OC-3)。不回改正本討論。
- 自檢七掃 | 2026-09-13 | ①優劣皆有依據欄;②G-out-1…8 進 Decision／SC,漏項進 Non-Goals;③Q8／Q10／Q11 與 M 表／cap／freeze／四欄皆有選定或 Rejected;④SC-1…10 可量測;⑤Rejected 無空棄因;⑥五決策點由 brief 確認,OC-1…3／5／6／8／9／10 承接移交或延伸／收窄,OC-4／OC-7 流程層;⑦既有脈絡是對帳不是外移 schema。圖上 1A–5A 標選定,Rejected 未上圖。
- G1 | 未送人類裁決 | `verdict` 空;`status` draft;OC 全列待人審。不得把本 PR 當 G1 PASS。
