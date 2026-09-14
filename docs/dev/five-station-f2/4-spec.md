---
feature: five-station-f2
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 4. 規格 — 五站 F2 change spec（Implementer C：anti-hollow dual-path）

> 基準:`origin/main` `ffbe665`（#334 STATUS G1✅）。Lane = **full**。契約不 bump。
> G1 已核:`docs/dev/five-station-f2/2-decision.md` `status: approved`、`verdict: PASS`、OC-1～OC-12 ✅ Owner PASS（#333；owner chat「可以」）。無 `3-prototype.md`。使用者本 hop：只落 `4-spec.md` + html、`status: draft`、**不發明 G2 PASS**、不改 STATUS／HISTORY／2-decision／模板／graph／scripts 牙。
> Decision 正本:`1A+2C+3A+4A+5A+6A+7A+8A`。C 線主軸：**檔在 ≠ F2 完**。F2 完＝同一電池 NEW5+OLD7 都能獨立紅、也能一起綠。13 具名 CASE 各一條獨立 S，只准加不准減。CASE 極性＝注入壞行為該格紅，不是「拒 hop 算綠」。
> 原文獨立於 A／B：本檔只讀 1-discussion／2-decision／模板／狀態機／F1 annex／RP，不讀他線 4-spec。
> 本 hop 不實作 coordinator。後站 Stage 5–7 Diff Budget **只准 F2 scripts**（電池入口、coordinator、合成 fixture、把 RP-9／10／11 接到 1A 倉）。F3 cut／折 in-flight／刪 token 鎖死 Out of Scope。

## 補助模組生命週期（預覽）

主詞是「F2 coordinator + slug 級只增倉 + 同一電池 dual-path」，不是整份方法論。直式圖，置中。
- 新生（這輪新欄／新表）：slug 級只增倉、hop／latch／cap 紀錄、單一電池入口 `scripts/test-five-station-f2.sh`、13 具名 CASE、檔→五站五桶觸發表
- 改行為（相關一格）：F2 起 coordinator 評謂詞；真則 hop、假則停修；三前置 `2.1.0 ∧ ¬in-flight ∧ F3-cut` 全真才評五站；RP-9／10／11 改讀真計數。本 hop 只把契約寫進本檔
- 退役：沒有
- 不動：七檔名、G1／G2／`ACCEPTED` token、既有 graph／Stage 1–4 模板、本 slug 舊 7、F1 十二群牙、契約 `2.0.0`、`agent-event` schema 1.1、doctor 握手語意

## Real-world Disposition

承接 Stage 2 去向帳。引用 = Stage 1 原文片段，不發第二鏈編號。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 「F1 已鎖 cap 數字與拒收謂詞,但計數落在哪、鍵叫什麼明文交給 F2」 | 本方案處理 | S-3.5、S-3.7、S-7.6 |
| 「現行牙只對 fixture 字樣『第 3 次』正則紅——沒有倉,第三次重寫在 live 裡可以假裝第一次」 | 本方案處理 | S-3.1、S-7.7 |
| 「若三個 cap 寫進 run 級 events.jsonl,新 run 歸零 = 暗改 cap(X5)」 | 本方案處理 | S-3.4、S-3.7 |
| 「marketplace update 換 hops,doctor 仍印 COMPATIBLE」 | 本方案處理 | S-6.5、S-6.6 |
| 「若後續 coordinator 把綠或我已在 plugin cache 當成切五站,舊 7 slug 會被折」 | 本方案處理 | S-6.1、S-6.7、S-5.2 |
| Journey「owner／寫手 chat『可以開下一站』」 | 本方案處理 | S-2.2、S-2.3 |
| Journey「live 第三次重寫假裝第一次」 | 本方案處理 | S-3.1、S-3.5 |
| Workaround「F1 用文案正則擋『doctor 綠所以跟 hops』；擋的是寫出來的謊,不是 coordinator 行為」 | 本方案處理 | S-6.5、S-6.8 |
| Workaround「STATUS／HISTORY 當 hop log」 | 刻意維持 | Out of Scope：本 hop 不改看板；紀錄不住 STATUS |
| Exception「舊 7 與 in-flight 不套三個 cap」 | 本方案處理 | S-5.1、S-5.2 |
| Exception「F2 可以寫 coordinator 碼,但 F3 前預設路線仍舊 7」 | 本方案處理 | S-6.3、S-6.4、S-8.1 |
| Exception「[Assumption] 把 cap 放進 run 級 events = X5」 | 本方案處理 | S-3.7 |
| Exception「[Assumption] dual-path 同一入口兩路都必須能獨立變紅」 | 本方案處理 | S-1.1、S-1.5 |
| Exception「[Assumption] NEW5 試體是合成 fixture,不是本 slug」 | 本方案處理 | S-5.4、S-5.5 |
| 「本 tree 搜過:沒有 F2 coordinator 實作檔」 | 本方案處理 | S-8.4、S-8.6 |
| 「鎖:不刪 G1／G2／ACCEPTED；不做 F3 cut；不把 in-flight 折成五站」 | 本方案處理 | S-8.1、S-8.2、S-8.3 |
| Q9 三個計數器落點 | 本方案處理 | S-3.7、S-7.6 |
| Q10 run 級歸零是否 X5 | 本方案處理 | S-3.4、S-3.7 |
| Q11 hop_id 在 F3 前怎麼認 | 本方案處理 | S-7.1、S-7.5 |
| Q12 初寫 vs 重寫 | 本方案處理 | S-3.5 |
| Q13／Q14／Q18 事件怎麼接 × schema bump | 本方案處理 | S-7.6 |
| Q15 Goal 連帶 Decide 是否一次寫 | 本方案處理 | S-3.6 |
| Q16 T≤4 與 hop 重寫 | 本方案處理 | S-5.1、S-7.3 |
| Q17 三前置 | 本方案處理 | S-6.1、S-6.2、S-6.3、S-6.4 |
| Q19 RP-9／10／11 必須餵真計數 | 本方案處理 | S-7.7 |
| Q20 多份 plugin cache 認哪一份 | 本方案處理 | S-6.7 |
| Q21 F2 完是否=檔在或 F1 綠 | 本方案處理 | S-1.2、S-1.3、S-1.4 |
| Q22 三失敗不得當成功 | 本方案處理 | S-2.3、S-4.1、S-4.2 |
| Q23 事件五問、不鎖鍵 | 本方案處理 | S-7.6 |
| Q24 Backlog A 過期 | 刻意維持 | Out of Scope：本 hop 不改 STATUS |

## CASE → S 對照

13 具名 CASE 各一條獨立 S。減列 = 翻 Decision。4-spec 可加列，不可把「檔在」加成通過條件。極性：標「預期紅」的列＝**注入該壞行為**，該格必須獨立變紅。

| CASE | 路 | 極性 | 本檔 S |
|---|---|---|---|
| NEW5-HOP-OK | NEW5 | 綠：合法 hop 應發生 | S-2.1 |
| NEW5-PRED-STOP | NEW5 | 綠：合法停修 | S-2.2 |
| NEW5-CAP-3 | NEW5 | 綠：合法拒第 3 次 hop 重寫 | S-3.1 |
| NEW5-DECIDE-2 | NEW5 | 綠：合法拒第 2 次 Decide 重開 | S-3.2 |
| NEW5-GOAL-2 | NEW5 | 綠：合法拒第 2 次 Goal 重開 | S-3.3 |
| NEW5-MK-RED | NEW5 | 預期紅：注入 Must-keep 紅仍 hop | S-4.1 |
| NEW5-SHIP-MECH | NEW5 | 預期紅：注入機械綠無人 PASS 卻標 Done | S-4.2 |
| NEW5-WAIT-RED | NEW5 | 預期紅：注入謂詞真 latch 假仍問人 | S-2.3 |
| NEW5-RUN2 | NEW5 | 綠：新 run_id 數字仍在 | S-3.4 |
| OLD7-NO-FIVE | OLD7 | 綠：無五站狀態寫入 | S-5.1 |
| OLD7-FOLD-RED | OLD7 | 預期紅：注入對 in-flight 寫五站狀態 | S-5.2 |
| OLD7-TOKEN | OLD7 | 綠：token 與 F1 牙仍在 | S-5.3 |
| OLD7-SELF | OLD7 | 綠：對本目錄求五站 hop 被拒 | S-5.4 |

## SC → S 對照

| SC | 一句 | 本檔 S |
|---|---|---|
| SC-BATTERY | 單一入口；缺一路即非 0 | S-1.1、S-1.5 |
| SC-NEW5-HOP-OK | 謂詞全真 latch 假 Must-keep 綠 → hop；五問可答 | S-2.1 |
| SC-NEW5-PRED-STOP | 謂詞假 → 不 hop、停修、不問人 | S-2.2 |
| SC-NEW5-CAP-3 | 第 3 次 hop 重寫拒；Escalated；計數仍 2 | S-3.1 |
| SC-NEW5-DECIDE-2 | 第 2 次 Decide 整站重開拒 | S-3.2 |
| SC-NEW5-GOAL-2 | 離開 Intake 後第 2 次 Goal 重開拒 | S-3.3 |
| SC-NEW5-MK-RED | 注入 Must-keep 紅仍 hop → 該格紅 | S-4.1 |
| SC-NEW5-SHIP-MECH | 注入機械綠無人 PASS 卻 Done → 該格紅 | S-4.2 |
| SC-NEW5-WAIT-RED | 注入謂詞真 latch 假仍問人 → 該格紅 | S-2.3 |
| SC-NEW5-RUN2 | 新 run_id 再讀，數字不是 0 | S-3.4 |
| SC-OLD7-NO-FIVE | 已有 1–7 `.md` → 無五站寫入；三 cap 不套 | S-5.1 |
| SC-OLD7-FOLD-RED | 注入對 in-flight 寫五站狀態 → 該格紅 | S-5.2 |
| SC-OLD7-TOKEN | G1／G2／`ACCEPTED` 仍在；F1 十二群可綠 | S-5.3 |
| SC-OLD7-SELF | 對本目錄求五站 hop → 跳不過 | S-5.4 |
| SC-DOCTOR | doctor `COMPATIBLE` 不是五站通行證 | S-6.5、S-6.8 |
| SC-KNIFE | 無 F3 cut；in-flight 仍舊 7；token 仍在 | S-8.1、S-8.2、S-8.3 |
| SC-HOLLOW | 檔在／F1 綠／只跑 NEW5-HOP-OK ≠ F2 綠 | S-1.2、S-1.3、S-1.4 |
| SC-Q-CARRY | Q9–Q24 皆有去向 | S-8.8 |
| SC-PR | 本 hop 只 4-spec 雙檔；draft；無 G2 PASS | S-8.4、S-8.5 |

## Owner Call hang

| OC | 掛到 |
|---|---|
| OC-1 slug 級只增倉 | S-3.4、S-3.7 |
| OC-2 獨立 slug ledger、不 bump | S-7.6 |
| OC-3 五桶觸發表、拒七 stem | S-7.1、S-7.2、S-7.3、S-7.4、S-7.5 |
| OC-4 三前置升格 | S-6.1、S-6.2、S-6.3、S-6.4 |
| OC-5 run 級倉＝X5 | S-3.7 |
| OC-6 RP 讀真計數 | S-7.7 |
| OC-7 cache 只選碼；路線認專案樹 | S-6.7 |
| OC-8 Goal+Decide 一次寫 | S-3.6 |
| OC-9 13 CASE 只准加；極性＝注入紅 | 上表 13 列；S-4.1、S-2.3、S-5.2 |
| OC-10 本 Decision hop 不改 STATUS | S-8.4（本 hop 對稱：不改 STATUS、不發明 G2 PASS） |
| OC-11 第一次 persist＝0 後 +1 | S-3.5 |
| OC-12 F3 前 live 禁評五站 | S-6.3、S-5.4、S-5.5 |

## ADDED Requirements

### R-1: 系統 SHALL 用同一電池同時證明 NEW5 與 OLD7，並拒把檔在當成 F2 完
SC-BATTERY／SC-HOLLOW／5A。單一入口、同一 process。NEW5 組與 OLD7 組都過才 exit 0。缺一路、跳過一路、兩支互不認識的腳本各綠一次、只轉呼叫 `scripts/test-five-station-f1.sh`、只證明 coordinator 檔存在 → 整電池非 0。5B／5C 已拒。

**審的時候看什麼**
問：是不是同一支入口？缺一路是不是非 0？「檔在」「F1 十二群綠」「只跑 NEW5-HOP-OK」有沒有被標成 F2 綠？有 → 本 R 紅。

#### S-1.1 單一入口跑完整電池；缺一路即非 0
- GIVEN 倉庫裡有一支電池入口 `scripts/test-five-station-f2.sh`；NEW5 合成 fixture 與 OLD7 fixture 都在；兩組具名 CASE 皆可被該入口點名
- WHEN 同一 process 跑該入口且不帶「跳過一組」旗標
- THEN exit 0 當且僅當 NEW5 組全過且 OLD7 組全過；入口 stdout 列出 13 個 CASE 名與各格紅／綠；缺 NEW5、缺 OLD7、或入口只 `exec`／轉呼叫 `scripts/test-five-station-f1.sh` → exit 非 0
- 觀測:從該入口的原始 stdout／exit 看 | 兩組都跑、13 名都出現、缺一組非 0 算過 | n-a:本 hop 不寫腳本。替代：本條 THEN 與 Decision SC-BATTERY 字面；後站檔在後跑 `bash scripts/test-five-station-f2.sh`
- Operational Context:不適用 — 電池入口是 CLI selftest，無新的現場交接。

#### S-1.2 只證明 coordinator 檔存在不得標 F2 綠
- GIVEN 倉庫裡已有 coordinator 模組檔（例如 `scripts/` 下新檔），且 `scripts/test-five-station-f2.sh` 尚未跑完 NEW5 組與 OLD7 組
- WHEN 有人把「檔存在」寫成 F2 完成或讓電池因此 exit 0
- THEN 該完成宣稱被拒；電池 exit 非 0；拒絕理由含「檔在 ≠ F2 完」或同等字面，不是「檔已齊」
- 觀測:從電池 exit 與完成宣稱看 | 僅檔在仍非 0 算過 | n-a:本 hop 無 coordinator 檔。替代：本檔 Out of Scope 第 8 點；`rg -n "檔在 ≠ F2 完" docs/dev/five-station-f2/4-spec.md docs/dev/five-station-f2/2-decision.md`
- Operational Context:
  - Actor:F2 實作／審查者
  - Goal:擋 hollow 完成
  - Situation:coordinator 檔剛落地、電池未跑
  - Known information:Decision 約束 1；5B 已拒
  - Missing information:有沒有人想用 ls 當綠燈
  - Human decision:不得把檔在簽成 G3 綠
  - Authority:本 R；推翻回第 2 站
  - External dependency:無
  - Out-of-system action:不准用 chat「檔有了」繞電池
  - Waiting/timeout behavior:無
  - Recovery:刪該完成宣稱，改跑 S-1.1 入口
  - Audit/handoff requirement:電池 stdout
  - Observation:見本條觀測

#### S-1.3 只跑 F1 十二群綠不得標 F2 綠
- GIVEN `scripts/test-five-station-f1.sh` 十二群 exit 0
- WHEN 有人把該綠燈寫成 F2 完成，或 F2 入口只轉呼叫該腳本
- THEN F2 電池 exit 非 0；F1 綠只當回歸地板，不當 hop 證明
- 觀測:從 F2 入口是否轉呼叫 `test-five-station-f1.sh` 與 exit 看 | 只轉呼叫 → 非 0 算過 | n-a:F2 入口尚未落地。替代：`scripts/test-five-station-f1.sh:L1-L16` 牙自檢不是 hop 電池；Decision SC-HOLLOW (b)
- Operational Context:不適用 — 回歸腳本邊界，無人員交接。

#### S-1.4 只跑 NEW5-HOP-OK 綠而 OLD7 組未跑不得標 F2 綠
- GIVEN NEW5-HOP-OK 一格綠、OLD7 組零格被跑
- WHEN 有人把「NEW5 已 hop」寫成 F2 完成或讓整電池 exit 0
- THEN 整電池 exit 非 0；stdout 標 OLD7 組未跑
- 觀測:從整電池 exit 與 OLD7 組是否出現在 stdout 看 | OLD7 未跑仍 0 → 本條紅 | n-a:電池尚未落地。替代：Decision SC-HOLLOW (c)；本條 THEN
- Operational Context:不適用 — 單路假綠，無人員交接。

#### S-1.5 兩支互不認識的腳本各綠一次不是 dual-path
- GIVEN 一支只打 NEW5 的腳本 exit 0，另一支只打 OLD7 的腳本 exit 0，兩者不是同一 process、沒有單一入口彙總
- WHEN 有人把「兩支都綠」寫成 SC-BATTERY 過
- THEN 該宣稱被拒；SC-BATTERY 仍未過，直到 S-1.1 的單一入口同一 process 跑完兩組
- 觀測:從是否存在單一入口彙總 exit 看 | 兩支分跑各 0 仍不算過 | n-a:後站才有腳本。替代：1-discussion L112；Decision 約束 2
- Operational Context:不適用 — 入口形狀，無人員交接。

### R-2: 系統 SHALL 在 NEW5 上合法 hop／合法停修，並把中途等人注入成獨立紅格
NEW5-HOP-OK／NEW5-PRED-STOP／NEW5-WAIT-RED／6A／A 線拒法。謂詞全真 ∧ latch 假 ∧ Must-keep 綠 → 立刻 hop，不准留下「要不要繼續／請人審／確認一下」。謂詞假 → 停該站修，理由是該謂詞假。注入「仍問人」→ NEW5-WAIT-RED 該格紅；把「coordinator 拒 hop」記成該紅格綠＝極性反了。

**審的時候看什麼**
綠格：hop 有沒有真的發生、停修有沒有寫謂詞假。紅格：有沒有**注入**問人句。用拒 hop 把紅格塗綠 = 本 R 紅。

#### S-2.1 NEW5-HOP-OK：謂詞全真 latch 假 Must-keep 綠 → hop 且五問可答
- GIVEN 合成 NEW5 fixture 路徑是 `scripts/fixtures/five-station-f2/new5/`（不是 `docs/dev/five-station-f2/`、不是 `docs/dev/five-station-simplify/`）；專案樹契約宣告 2.1.0；fixture 目錄開始時零個 1–7 `.md`；專案樹有 F3-cut 標記；當下 hop 的自動前進謂詞全真；latch 列全假；Must-keep 全綠
- WHEN 電池入口跑 NEW5-HOP-OK
- THEN coordinator 發生一次 hop；slug 級紀錄人指得到一筆，且五問有答：誰、從哪 hop 到哪、哪條謂詞為真、哪只 cap 數字、Escalated=否；該筆不是 chat、不是 `attempt_completed`、不是 run 級 `events.jsonl` 冒充
- 觀測:從電池 NEW5-HOP-OK 格與 slug 倉紀錄看 | 格綠＋五問有答＋Escalated=否算過 | n-a:coordinator 尚未落地。替代：Decision SC-NEW5-HOP-OK；本條 GWT
- Operational Context:
  - Actor:coordinator（F2 後）／電池寫手
  - Goal:謂詞真就 hop，不等人
  - Situation:NEW5 合成 fixture、三前置全真
  - Known information:brief §3 謂詞；latch 假
  - Missing information:現場會不會要求「順便問人」
  - Human decision:中間不簽；只在 Ship 簽
  - Authority:coordinator 禁問「要不要繼續」
  - External dependency:無
  - Out-of-system action:不准改問 owner 來繞假謂詞
  - Waiting/timeout behavior:latch 假則不停
  - Recovery:若紀錄出現問人句，改走 S-2.3 注入紅，不得把本格當過
  - Audit/handoff requirement:slug 倉五問
  - Observation:見本條觀測

#### S-2.2 NEW5-PRED-STOP：謂詞假 → 不 hop、停修、不留問人句
- GIVEN 同一 NEW5 fixture；三前置全真；當下至少一條自動前進謂詞為假（例：`4-spec.md` 缺觀測欄）；latch 假
- WHEN 電池入口跑 NEW5-PRED-STOP
- THEN 不 hop；停在該站；拒絕／停修理由寫出那一條謂詞為假；紀錄與 stdout 不含「要不要繼續」「請人審」「確認一下」
- 觀測:從該格 stdout 與 hop 是否發生看 | 無 hop＋理由含謂詞名＋無三句問人算過 | n-a:coordinator 尚未落地。替代：狀態機 §2「一假就停」；Decision SC-NEW5-PRED-STOP
- Operational Context:
  - Actor:下一站寫手
  - Goal:修假謂詞，不是改問人
  - Situation:謂詞假
  - Known information:哪一條假
  - Missing information:無
  - Human decision:不在中間簽放行
  - Authority:coordinator 不得把假謂詞改成問人
  - External dependency:無
  - Out-of-system action:不准 chat「先過」
  - Waiting/timeout behavior:不停 HumanWait（latch 假）
  - Recovery:補齊謂詞後重評 S-2.1
  - Audit/handoff requirement:停修理由
  - Observation:見本條觀測

#### S-2.3 NEW5-WAIT-RED：注入謂詞真 latch 假仍問人 → 該格獨立紅
- GIVEN 同一 NEW5 fixture；謂詞全真；latch 假；Must-keep 綠
- WHEN 測法**注入** coordinator 在 hop 紀錄或 stdout 留下「要不要繼續」或「請人審」或「確認一下」（不是測「coordinator 拒 hop」）
- THEN NEW5-WAIT-RED 該格獨立紅（該格 exit 非 0）；整電池因該格紅而不得標 F2 成功；把「coordinator 拒寫問人句／拒 hop」記成此格綠＝極性反了，本條失敗
- 觀測:從具名格 NEW5-WAIT-RED 的紅／綠看 | 注入問人句 → 該格紅算過；拒 hop 當此格綠 → 本條失敗 | n-a:注入治具尚未落地。替代：Decision 約束 8／15；SC-NEW5-WAIT-RED
- Operational Context:
  - Actor:電池寫手／coordinator
  - Goal:把中途等人做成可獨立紅的格
  - Situation:latch 未命中
  - Known information:A 線拒法；RP-14
  - Missing information:實作會不會把拒 hop 塗成此格綠
  - Human decision:極性翻了回第 2 站
  - Authority:OC-9
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:latch 假禁止 HumanWait
  - Recovery:改注入治具，使壞行為出現時該格紅
  - Audit/handoff requirement:CASE 名 NEW5-WAIT-RED
  - Observation:見本條觀測

### R-3: 系統 SHALL 把三 cap 放進 slug 級只增倉，第一次 persist＝0，新 run 不得歸零
NEW5-CAP-3／NEW5-DECIDE-2／NEW5-GOAL-2／NEW5-RUN2／OC-1／OC-5／OC-8／OC-11。hop≤2／Decide≤1／Goal reopen≤1。某 `hop_id` 第一次成功 persist＝0，其後每一次成功 persist 該桶 +1。Goal 連帶回到 Decide 時兩個計數同一次 mutation。倉不在 `.devflow/runs/<run_id>/`。

**審的時候看什麼**
數字住哪：slug 倉還是 run 目錄。第一次寫是 0 還是 1。第 3 次拒完數字是不是還 2。Goal 重開有沒有同一次寫 Decide。

#### S-3.1 NEW5-CAP-3：同一 hop 第 3 次重寫拒；Escalated；計數仍 2
- GIVEN NEW5 fixture 的同一 `hop_id` 桶已有兩次成功 persist（計數＝2；第一次 persist 曾為 0 不計入這 2）
- WHEN 電池入口跑 NEW5-CAP-3，要求該桶第 3 次 hop 重寫
- THEN 第 3 次被拒；狀態 Escalated；拒後該桶數字仍是 2；無人手改小、無 reset 再 hop
- 觀測:從拒絕理由＋slug 倉該桶數字看 | 未 hop＋Escalated＋數字=2 算過 | n-a:倉尚未落地。替代：狀態機 L129；RP-9；Decision SC-NEW5-CAP-3
- Operational Context:
  - Actor:coordinator
  - Goal:cap 用盡 fail-closed
  - Situation:同一 hop 已重寫 2 次
  - Known information:hop≤2；第一次 persist＝0
  - Missing information:有沒有人想 reset
  - Human decision:Escalated 之後由人明示下一手（修 brief／放行一次／停），本條只鎖拒與數字不變
  - Authority:不准暗改 cap（X5）
  - External dependency:無
  - Out-of-system action:不准手改倉數字
  - Waiting/timeout behavior:進 Escalated，不是偷偷 hop
  - Recovery:保持數字 2；另開 Decision 才准改 cap
  - Audit/handoff requirement:倉數字＋Escalated 紀錄
  - Observation:見本條觀測

#### S-3.2 NEW5-DECIDE-2：第 2 次 Decide 整站重開拒
- GIVEN NEW5 已離開 Decide 一次，且已發生 1 次 Decide 整站重開（Decide cap 已用完那 1 次）；站內尚未 hop 出的小改不算
- WHEN 電池入口跑 NEW5-DECIDE-2，要求第 2 次 Decide 整站重開
- THEN 被拒；狀態 Escalated；Decide 計數不因這次被拒而減少
- 觀測:從該格與 Decide 計數看 | 第 2 次重開未發生＋Escalated 算過 | n-a:倉尚未落地。替代：狀態機 L131；RP-10；SC-NEW5-DECIDE-2
- Operational Context:不適用 — 與 S-3.1 同一 cap 家族；本條只換 Decide 桶。

#### S-3.3 NEW5-GOAL-2：離開 Intake 後第 2 次 Goal 重開拒
- GIVEN NEW5 已 hop 出 Intake；Goal／Success Criteria／問題陳述已重開改寫 1 次
- WHEN 電池入口跑 NEW5-GOAL-2，要求第 2 次 Goal 重開（可同時造成第二次 Decide）
- THEN 被拒；若此次會造成第二次 Decide，Decide cap 同時用盡；兩個計數若有寫入則同一次 mutation（見 S-3.6）
- 觀測:從 Goal 計數與是否 hop 看 | 第 2 次 Goal 重開未發生算過 | n-a:倉尚未落地。替代：狀態機 L132／L137；RP-11；SC-NEW5-GOAL-2
- Operational Context:不適用 — 與 S-3.1 同一 cap 家族；本條只換 Goal 桶。

#### S-3.4 NEW5-RUN2：另開新 run_id 再讀，數字不是 0
- GIVEN NEW5 已對某 `hop_id` 寫入過（該桶數字 ≥1，或 Decide／Goal 數字 ≥1）；當下 `run_id` 為 `run-a`
- WHEN 同一 slug 另開新 `run_id`=`run-b` 再讀三個計數
- THEN 該 hop 桶／Decide／Goal 數字與 `run-a` 結束時相同，不是 0；讀取路徑不含 `.devflow/runs/run-b/`
- 觀測:從 slug 倉在兩個 run_id 下的數字看 | 第二個 run 讀到同一數字算過 | n-a:倉尚未落地。替代：Decision SC-NEW5-RUN2；ledger.py L3-L6 是反面（run 級）
- Operational Context:不適用 — 跨 run 持久，無人員交接。

#### S-3.5 第一次成功 persist＝0，其後每一次 +1
- GIVEN NEW5 某 `hop_id` 桶尚無任何成功 persist
- WHEN 第一次成功 persist 該桶對應檔（例：第一次寫入 `1-discussion.md` → Intake），其後同一桶再成功 persist 一次
- THEN 第一次之後倉內該桶數字是 0；第二次之後數字是 1；第一次寫不計入 hop≤2；計數看寫入發生，不看模型名、不看 session
- 觀測:從兩次 persist 前後的倉數字看 | 序列 空→0→1 算過；空→1→2 則本條紅 | n-a:倉尚未落地。替代：Decision 約束 6；狀態機 L129
- Operational Context:不適用 — 計數切點，無人員交接。

#### S-3.6 Goal 連帶回到 Decide 時兩個計數同一次 mutation
- GIVEN NEW5 已 hop 出 Intake；即將發生一次 Goal reopen，且該動作會回到 Decide
- WHEN coordinator 寫入 Goal 計數
- THEN Decide 計數在**同一個**寫入動作裡更新（同一 mutation：要嘛兩數都寫入，要嘛兩數都不寫入）；禁止先寫 Goal 再另一次寫 Decide，也禁止只寫 Goal
- 觀測:從倉寫入次數與兩數是否同時出現看 | 一次寫入見兩數算過；兩次寫入或只見 Goal → 本條紅 | n-a:倉尚未落地。替代：Decision OC-8；狀態機 L137
- Operational Context:不適用 — 寫入原子性，無人員交接。

#### S-3.7 三 cap 不得住 run 級 events.jsonl
- GIVEN 現行 run ledger 路徑是 `.devflow/runs/<run_id>/coordinator/events.jsonl`
- WHEN F2 選定 cap 倉位置
- THEN 三計數器的讀寫路徑是 slug 級只增倉，根目錄為 `.devflow/five-station/<slug>/`（專案樹、不隨 run_id 換目錄）；禁止把 cap 數字的正本寫進 `.devflow/runs/<run_id>/`；JSON／YAML 鍵名仍 OPEN（本條不鎖 `event_type`）
- 觀測:從 cap 讀寫路徑字串看 | 含 `/runs/<run_id>/` → 本條紅；含 `.devflow/five-station/<slug>/` 且新 run 仍在算過 | n-a:倉尚未落地。替代：Decision 1A／1B 棄因；本檔 DD-3
- Operational Context:不適用 — 落點契約，無人員交接。

### R-4: 系統 SHALL 把 Must-keep 紅仍 hop 與機械綠當 Done 做成可獨立紅的注入格
NEW5-MK-RED／NEW5-SHIP-MECH／G-keep-1。Must-keep 未綠不得 hop。Ship 無自動前進。測法是注入壞行為，不是把「拒 hop」記成紅格綠。

**審的時候看什麼**
紅格有沒有真的注入壞行為。T 缺 Verify 仍 hop、無人 `verdict: PASS` 卻 Done —— 這兩格必須能各自紅。

#### S-4.1 NEW5-MK-RED：注入 Must-keep 紅仍 hop → 該格獨立紅
- GIVEN NEW5 fixture 的一份 `5-tasks.md` 裡至少一張 T 缺 Verify（Must-keep 紅）；其他 hop 謂詞可為真
- WHEN 測法**注入** coordinator 仍對該 slug 執行 hop（不是測「coordinator 拒 hop」）
- THEN NEW5-MK-RED 該格獨立紅；整電池不得標 F2 成功；把「coordinator 拒 hop」記成此格綠＝極性反了，本條失敗
- 觀測:從具名格 NEW5-MK-RED 看 | 注入仍 hop → 該格紅算過 | n-a:注入治具尚未落地。替代：Decision SC-NEW5-MK-RED；RP-1；brief M11
- Operational Context:
  - Actor:電池寫手／Build 寫手
  - Goal:完整度未綠不得被 hop 掉
  - Situation:T 缺 Verify
  - Known information:Must-keep 入謂詞（6A）
  - Missing information:實作會不會先 hop 再補欄
  - Human decision:6B 已拒
  - Authority:OC-9 極性
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:停 Build 修 T，不是 HumanWait
  - Recovery:補 Verify 後重評；本格仍只認注入紅
  - Audit/handoff requirement:CASE 名 NEW5-MK-RED
  - Observation:見本條觀測

#### S-4.2 NEW5-SHIP-MECH：注入機械全綠無人寫 PASS 卻標 Done → 該格獨立紅
- GIVEN NEW5 已在 Ship；`7-review.md` 機械項可全綠；頂欄 `verdict:` 不是人寫的 `PASS`
- WHEN 測法**注入** coordinator 或寫手把狀態標 `Done`（或寫入 `verdict: PASS` 且無人類 attestation）
- THEN NEW5-SHIP-MECH 該格獨立紅；Ship 不得自動前進；把「coordinator 拒標 Done」記成此格綠＝極性反了，本條失敗
- 觀測:從具名格 NEW5-SHIP-MECH 與 7-review 頂欄看 | 注入 Done／代寫 PASS → 該格紅算過 | n-a:注入治具尚未落地。替代：狀態機 §2.5；RP-8／RP-16；SC-NEW5-SHIP-MECH
- Operational Context:
  - Actor:Ship 審查者／coordinator
  - Goal:機械綠 ≠ PASS
  - Situation:A10 latch＝是
  - Known information:Ship 唯人
  - Missing information:有沒有人想用 checkbox 冒充頂欄
  - Human decision:只有人寫 `verdict: PASS` 才 Done
  - Authority:brief OC-3
  - External dependency:無
  - Out-of-system action:不准 Agent 代填 PASS
  - Waiting/timeout behavior:必須進 HumanWait
  - Recovery:刪機器判定，留 Ship
  - Audit/handoff requirement:7-review 頂欄
  - Observation:見本條觀測

### R-5: 系統 SHALL 讓 OLD7 不建五站機、折線可獨立紅、token 仍在、本目錄不是白老鼠
OLD7-NO-FIVE／OLD7-FOLD-RED／OLD7-TOKEN／OLD7-SELF／8A。已有 1–7 `.md` → `allow_legacy()`。NEW5 只准合成 fixture。

**審的時候看什麼**
OLD7 fixture 有沒有五站狀態檔。折線是不是注入紅。token 掃描還在不在。有沒有人拿本目錄當 NEW5。

#### S-5.1 OLD7-NO-FIVE：已有 1–7 `.md` → 無五站狀態寫入；三 cap 不套
- GIVEN OLD7 fixture 路徑 `scripts/fixtures/five-station-f2/old7/` 已有 `1-discussion.md`…`7-review.md`；契約可仍為 2.0.0
- WHEN 電池入口跑 OLD7-NO-FIVE，並對該 fixture 評路線
- THEN coordinator 走 `allow_legacy()`；該 fixture 目錄與 `.devflow/five-station/<該 slug>/` 無五站 hop／latch／cap 狀態寫入；三 cap 不套；T 重做仍走既有嘗試上限 4
- 觀測:從該格與 fixture 目錄／slug 倉是否新增五站狀態看 | 無五站寫入＋cap 不套算過 | n-a:coordinator 尚未落地。替代：狀態機 L49-L50；SC-OLD7-NO-FIVE
- Operational Context:
  - Actor:in-flight slug 執行者
  - Goal:走完手上舊 7
  - Situation:目錄已有 1–7 `.md`
  - Known information:SLOT-IN-FLIGHT-DETECT
  - Missing information:F2 碼會不會誤建機
  - Human decision:不折這條 slug
  - Authority:brief OC-9
  - External dependency:既有 `graph.yaml`
  - Out-of-system action:無
  - Waiting/timeout behavior:舊 7 例行閘照走
  - Recovery:若寫入五站狀態，改走 S-5.2 注入紅並清回
  - Audit/handoff requirement:目錄 ls
  - Observation:見本條觀測

#### S-5.2 OLD7-FOLD-RED：注入對 in-flight 寫五站狀態 → 該格獨立紅
- GIVEN 同一 OLD7 fixture（已有 1–7 `.md`）
- WHEN 測法**注入**對該 fixture 寫入五站狀態或執行五站 hop（RP-15）
- THEN OLD7-FOLD-RED 該格獨立紅；整電池不得標 F2 成功；把「coordinator 拒寫」記成此格綠＝極性反了，本條失敗
- 觀測:從具名格 OLD7-FOLD-RED 看 | 注入寫入／hop → 該格紅算過 | n-a:注入治具尚未落地。替代：Decision SC-OLD7-FOLD-RED；RP-15
- Operational Context:
  - Actor:電池寫手
  - Goal:折 in-flight 必須能獨立紅
  - Situation:RP-15
  - Known information:8A 鎖
  - Missing information:實作會不會把拒寫塗成此格綠
  - Human decision:8C 已拒
  - Authority:OC-9 極性
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:清回舊 7；本格只認注入紅
  - Audit/handoff requirement:CASE 名 OLD7-FOLD-RED
  - Observation:見本條觀測

#### S-5.3 OLD7-TOKEN：G1／G2／ACCEPTED token 與檔仍在；F1 牙回歸仍綠
- GIVEN OLD7 fixture 與本 repo 既有 token 檔
- WHEN 電池入口跑 OLD7-TOKEN，並跑 `scripts/check-gate-tokens.sh`（或同等 token 檢查）與 `scripts/test-five-station-f1.sh`
- THEN token 檢查綠；G1／G2／`ACCEPTED` 檔與 token 仍在；F1 十二群仍可綠；F2 電池此格綠不依賴刪 token
- 觀測:從 token 檢查 exit 與 F1 十二群 exit 看 | 兩支皆 0＋token 檔仍在算過 | 本 hop 可跑 `bash scripts/check-gate-tokens.sh` 與 `bash scripts/test-five-station-f1.sh` 當回歸地板；F2 此格落地後併入電池
- Operational Context:不適用 — token 回歸，無新交接。

#### S-5.4 OLD7-SELF：對本目錄求五站自動前進 → 跳不過
- GIVEN `docs/dev/five-station-f2/` 已有 `1-discussion.md` 與 `2-decision.md`（已 in-flight）
- WHEN 電池入口或 coordinator 被求對這個目錄做五站自動前進
- THEN 被拒；目錄仍是舊 7 站檔；無 `.devflow/five-station/five-station-f2/` 五站狀態寫入；試體不是把本目錄當 NEW5
- 觀測:從拒絕理由與本目錄 ls／slug 倉看 | 拒＋無五站寫入算過 | 本 hop 可 `ls docs/dev/five-station-f2/*.md`：有 1／2、無五站機。後站電池對本路徑求 hop 必須非 0
- Operational Context:
  - Actor:本 slug 寫手
  - Goal:自己走到 G1／G2／G3 仍舊 7
  - Situation:本目錄已 in-flight
  - Known information:G-self-1；OC-12
  - Missing information:有沒有人想省一道閘
  - Human decision:不准把本目錄當 NEW5
  - Authority:Decision 約束 12
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:舊 7 例行閘
  - Recovery:刪誤建的五站狀態
  - Audit/handoff requirement:本目錄站檔
  - Observation:見本條觀測

#### S-5.5 NEW5 試體是合成 fixture，不是本 slug、不是 five-station-simplify
- GIVEN 電池入口的 NEW5 試體清單
- WHEN 列出 NEW5 路徑
- THEN 每一條 NEW5 路徑都在 `scripts/fixtures/five-station-f2/new5/` 之下；清單不含 `docs/dev/five-station-f2/`、不含 `docs/dev/five-station-simplify/`
- 觀測:從電池 NEW5 路徑清單看 | 兩 live 目錄不在清單算過 | n-a:入口尚未落地。替代：本檔 DD-5；Decision 約束 3
- Operational Context:不適用 — 試體路徑，無人員交接。

### R-6: 系統 SHALL 在評五站謂詞之前先問專案樹三前置：2.1.0 ∧ ¬in-flight ∧ F3-cut
4A／7A／SC-DOCTOR。缺一條 → `allow_legacy()`，不建五站機。`doctor COMPATIBLE`／exit 0 只證明握手。`marketplace update` 單獨 ≠ cut。plugin cache 只選本 process 讀哪份 hops **碼**，不是路條。本刀不改 `hooks/_doctor_impl.py`。

**審的時候看什麼**
三個問號：契約是不是 2.1.0、目錄有沒有 1–7 `.md`、專案樹有沒有 F3-cut 標記。綠的 doctor 有沒有被當成通行證。cache 有沒有被當成路條。

#### S-6.1 未宣告 2.1.0 → allow_legacy，不建五站機
- GIVEN 專案樹契約檔（本 repo 為 `devflow-contract.json`）`devflow_contract_version` 不是 `2.1.0`；其餘兩前置可為真或假
- WHEN coordinator 被求評五站謂詞或 hop
- THEN 走 `allow_legacy()`；不建五站機；拒絕理由是路線未宣告／仍舊 7，**不是**「doctor 已綠」
- 觀測:從拒絕理由與是否寫入 `.devflow/five-station/<slug>/` 看 | 理由含未宣告 2.1.0＋無五站寫入算過 | 本 hop 可讀 `devflow-contract.json` L1 現值 `2.0.0`。後站對 2.0.0 樹求 hop 必須走 legacy
- Operational Context:
  - Actor:採用專案 owner／coordinator
  - Goal:未 upgrade 不被遠端改線
  - Situation:契約仍 2.0.0
  - Known information:SLOT-UNDECLARED-ROUTE
  - Missing information:採用端會不會以為 doctor 綠就能切
  - Human decision:要切線先宣告 2.1.0 且等 F3-cut
  - Authority:4A
  - External dependency:採用端契約檔
  - Out-of-system action:marketplace 換包不算宣告
  - Waiting/timeout behavior:無
  - Recovery:保持舊 7
  - Audit/handoff requirement:契約版本字串
  - Observation:見本條觀測

#### S-6.2 in-flight → allow_legacy，不建五站機
- GIVEN `docs/dev/<slug>/` 已有 1–7 任一 `.md`；契約可已是 2.1.0；F3-cut 標記可已在
- WHEN coordinator 被求對該 slug 評五站謂詞
- THEN 走 `allow_legacy()`；不建五站機；僅 html、零個 1–7 `.md` 才不算 in-flight
- 觀測:從 in_flight 判定與是否寫五站狀態看 | 有 md → legacy＋無五站寫入算過 | n-a:coordinator 尚未落地。替代：annex SLOT-IN-FLIGHT-DETECT；S-5.1
- Operational Context:不適用 — 與 S-5.1 同一 freeze；本條只鎖前置合取裡的 ¬in-flight。

#### S-6.3 F3-cut 尚未發生 → allow_legacy，即使碼已在 plugin
- GIVEN 專案樹沒有 F3-cut 標記（標記定義＝專案樹內聲明「新 slug 預設五站」的產物；本 repo 今日不存在該標記；不是 doctor 輸出、不是 marketplace 紀錄、不是 plugin cache）；coordinator 碼可已存在於 plugin
- WHEN coordinator 被求對任一 live slug（含新開、含本目錄）評五站謂詞
- THEN 走 `allow_legacy()`；預設路線仍舊 7；NEW5 只打合成 fixture（該 fixture 可自己種標記，見 S-6.4）
- 觀測:從本 repo 是否存在 F3-cut 標記與 live slug 是否被評五站看 | 無標記＋live 走 legacy 算過 | 本 hop：`rg -n "新 slug 預設五站" guides docs/dev/STATUS.md` 不得被當成已 cut。後站對無標記樹求 hop → legacy
- Operational Context:
  - Actor:母版 owner／coordinator
  - Goal:F2 寫碼卻不偷 F3
  - Situation:F0–F2 母版軌
  - Known information:brief L166；OC-12
  - Missing information:碼合進 plugin 之後會不會對 live 開火
  - Human decision:F3 另刀才切預設
  - Authority:8A
  - External dependency:無
  - Out-of-system action:不准用 marketplace 冒充 cut
  - Waiting/timeout behavior:無
  - Recovery:對 live 的五站寫入當偷 F3，清回
  - Audit/handoff requirement:專案樹標記有無
  - Observation:見本條觀測

#### S-6.4 三前置全真才准評五站謂詞（只打合成 NEW5）
- GIVEN 合成 NEW5 fixture 同時滿足：契約 2.1.0、目錄開始時零個 1–7 `.md`、fixture 專案樹種了 F3-cut 標記
- WHEN coordinator 評該 fixture 的五站謂詞
- THEN 准評；後續 hop／停修／cap 走 R-2／R-3／R-4；這三條少一條就不得進本條
- 觀測:從三前置檢查通過後是否准評看 | 三真才評、少一條走 S-6.1／S-6.2／S-6.3 算過 | n-a:fixture 尚未落地。替代：Decision 4A；本檔 DD-4／DD-5
- Operational Context:不適用 — 合取閘，無人員交接。

#### S-6.5 doctor COMPATIBLE／exit 0 不是五站通行證
- GIVEN 本 tree 契約 `2.0.0` 且 `devflow-doctor.sh` 可印 `COMPATIBLE` 並 exit 0
- WHEN coordinator 被求因「doctor 已綠」而走五站 hop
- THEN 拒絕；理由是路線未宣告／仍舊 7，**不是**「doctor 已綠」；文案「doctor exit 0 所以可以跟 hops」仍紅（F1 S-5.6 回歸）
- 觀測:從 hop 拒絕理由與 F1 文案牙看 | 理由不含「doctor 已綠」當通行證；F1 S-5.6 仍紅該文案算過 | 本 hop 可跑 doctor 見 COMPATIBLE。後站拒絕理由字串不得把綠當路條
- Operational Context:
  - Actor:doctor 操作者／coordinator
  - Goal:綠只當握手
  - Situation:SLOT-DOCTOR-GREEN-MEANS
  - Known information:doctor L193-L202 綠＝`2.0.0 ∈ supported`
  - Missing information:採用端會不會把綠讀成切線
  - Human decision:4B 已拒
  - Authority:本刀不改 doctor
  - External dependency:`devflow-doctor.sh`
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:保持舊 7
  - Audit/handoff requirement:拒絕理由
  - Observation:見本條觀測

#### S-6.6 marketplace update 單獨 ≠ cut
- GIVEN 只做了 `marketplace update`／`plugin update`，契約未宣告 2.1.0，專案樹無 F3-cut 標記
- WHEN 有人把 hops 當五站預設或把 update 當 cut
- THEN 該組合被看成違規；路線仍舊 7；coordinator 不 hop
- 觀測:從路線判定看 | 未改線＋2.0.0+五站 hops 當違規算過 | n-a:採用假樹後站才造。替代：annex SLOT-UNDECLARED-ROUTE／SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS；Decision 約束 9
- Operational Context:
  - Actor:採用專案 owner
  - Goal:換包不改線
  - Situation:hops 已換、契約未動
  - Known information:marketplace 單一 entry `./`
  - Missing information:現場是否先 update 後 bump
  - Human decision:要切線走 2.1.0 + F3-cut，不是 update
  - Authority:4A
  - External dependency:marketplace／plugin cache
  - Out-of-system action:update 發生在系統外
  - Waiting/timeout behavior:無
  - Recovery:保持舊 7
  - Audit/handoff requirement:契約版本 vs hops
  - Observation:見本條觀測

#### S-6.7 plugin cache 只選 hops 碼；路線認專案樹
- GIVEN 同一 repo 兩份 plugin cache（主機 A hops 新、主機 B hops 舊）；專案樹契約與 `docs/dev/<slug>/` 站檔相同
- WHEN 兩台機器各啟動一個 process 評路線
- THEN 各 process 只從自己的 plugin root 讀 hops **碼**；路線許可仍只看專案樹：2.1.0 ∧ ¬in-flight ∧ F3-cut；不得因 A 機 hops 新就把 B 機舊 7 slug 改線；不掃磁碟上「最新」的其他 cache
- 觀測:從路線判定是否隨 cache 變看 | 兩機專案樹相同 → 路線相同算過；因 cache 新而改線 → 本條紅 | n-a:多 cache 治具尚未落地。替代：Decision 7A／OC-7
- Operational Context:
  - Actor:多主機採用者
  - Goal:不得遠端改線
  - Situation:Q20
  - Known information:plugin root 在 cache、隨版本變
  - Missing information:有沒有人想掃最新 cache
  - Human decision:7B／7C 已拒
  - Authority:brief L168
  - External dependency:各 process 的 plugin root
  - Out-of-system action:換 cache 不是 cut
  - Waiting/timeout behavior:無
  - Recovery:以專案樹重評
  - Audit/handoff requirement:契約＋該 slug 是否已有 1–7 `.md`
  - Observation:見本條觀測

#### S-6.8 契約 2.0.0 + 五站 hops 預設 = 違規，路線仍舊 7
- GIVEN 契約仍 `2.0.0` 且方法包 hops 已是五站預設；doctor 可因握手綠
- WHEN coordinator 或文案把「跟 hops 走」當已切
- THEN 該組合紅；路線仍舊 7；F1 文案牙對「COMPATIBLE = 五站」仍紅
- 觀測:從路線＋F1 S-5.5／S-5.6 回歸看 | 未改線＋文案牙仍紅算過 | 本 hop F1 牙已在；後站 coordinator 不得把該組當綠
- Operational Context:不適用 — 與 S-6.5／S-6.6 同一升級陷阱；本條鎖 2.0.0+五站 hops 合取。

### R-7: 系統 SHALL 用五桶檔→hop_id 觸發表寫 slug ledger，並讓 RP-9／10／11 讀真計數
3A／2C／6A。五桶不是七 stem。`3-prototype` 與 `4-spec` 同 Spec 桶；`5-tasks` 與 `6-implementation-notes` 同 Build 桶。無 Stage 3 trigger → 不建 proto 桶。舊節點 `N7-g1`／`N6-g2` 不是 hop_id。紀錄答五問；不鎖鍵名；不 bump `agent-event`。

**審的時候看什麼**
寫哪個檔進哪個桶。有沒有七個 stem。RP-9 讀的是倉數字還是「第 3 次」字樣。五問能不能指。

#### S-7.1 檔→五站 hop_id 觸發是五桶，不是七 stem
- GIVEN coordinator 要對一次成功 persist 分桶
- WHEN 寫入檔是下表左欄之一
- THEN hop_id 必須是右欄；禁止為七個 stem 各開一桶

| 寫入檔 | hop_id 桶 |
|---|---|
| `1-discussion.md` | Intake |
| `2-decision.md` | Decide |
| `3-prototype.md` | Spec |
| `4-spec.md` | Spec |
| `5-tasks.md` | Build |
| `6-implementation-notes.md` | Build |
| `7-review.md` | Ship |

- 觀測:從倉內 hop_id 值看 | 只出現五個桶名算過；出現 `3-prototype`／`4-spec` 當兩個 hop_id → 本條紅 | n-a:倉尚未落地。替代：Decision 約束 14
- Operational Context:不適用 — 分桶表，無人員交接。

#### S-7.2 3-prototype 與 4-spec 共用 Spec 桶，合計 hop≤2
- GIVEN NEW5 已對 Spec 桶成功 persist `4-spec.md` 兩次（計數＝2；含第一次 persist＝0 之後的兩次 +1）
- WHEN 再成功 persist 同一 slug 的 `3-prototype.md`
- THEN 該次 persist 被算進 **Spec** 桶第 3 次而拒（與 S-3.1 同一 cap）；不得另開 proto 桶讓這次變成 proto 的第 1 次
- 觀測:從 Spec 桶數字與是否另有 proto 桶看 | 拒＋無 proto 桶算過 | n-a:倉尚未落地。替代：Decision 約束 14；B 線七 stem 已拒
- Operational Context:不適用 — 同桶稀釋測試。

#### S-7.3 5-tasks 與 6-notes 共用 Build 桶；T 嘗試 ≤4 不與 hop 桶混算
- GIVEN NEW5 在 Build；單張 T 重做 3 次（該 T 嘗試計數 3，上限 4）
- WHEN 該 T 再重做 1 次（第 4 次），且整份 `5-tasks.md`／`6-implementation-notes.md` **未被**整站重寫
- THEN 該 T 仍走嘗試上限 4，Build hop 桶數字不因此 +1；只有整份 5-tasks／6-notes 被整站重寫時才 +1 Build 桶（一次，不是兩個 stem 各 +1）
- 觀測:從 T 嘗試計數與 Build hop 桶看 | T 第 4 次仍允許且 Build 桶不變算過；T 重做卻 +1 hop → 本條紅 | n-a:coordinator 尚未落地。替代：狀態機 L107-L108；Decision 約束 5
- Operational Context:不適用 — 兩套上限分家。

#### S-7.4 無 Stage 3 trigger → 不建 3-prototype、也不另開 proto 桶
- GIVEN NEW5 的 Stage 3 觸發判定 0 命中（或已落檔全未勾 + n-a 原因）
- WHEN coordinator 評 Spec
- THEN 不要求存在 `3-prototype.md`；不建立 proto 桶；Spec 只由 `4-spec.md` 觸發
- 觀測:從是否存在 proto 桶與是否因缺 3-prototype 拒 hop 看 | 無 proto 桶＋不因缺 3-prototype 拒算過 | n-a:coordinator 尚未落地。替代：Decision 約束 14 末段；本 slug 自身 Stage 3 對帳 N/A
- Operational Context:不適用 — 桶數，無人員交接。

#### S-7.5 N7-g1／N6-g2 不是五站 hop_id
- GIVEN 舊 7 graph 節點名 `N7-g1`、`N6-g2` 仍存在於 `skills/dev-flow/stage2/graph.yaml` 等
- WHEN coordinator 寫入五站倉的 hop_id
- THEN hop_id ∈ {Intake, Decide, Spec, Build, Ship}；倉內零筆 hop_id 等於 `N7-g1` 或 `N6-g2`
- 觀測:從倉內 hop_id 集合看 | 與五個別名相等算過；出現舊節點名 → 本條紅 | n-a:倉尚未落地。替代：Decision 3B 棄因；graph.yaml L53-L57 仍是舊路
- Operational Context:不適用 — id 命名，無人員交接。

#### S-7.6 slug ledger 答五問；鍵名 OPEN；本刀不 bump agent-event
- GIVEN 一次 hop 成功、一次 latch 開火、一次 cap 用盡（三筆可在 NEW5 fixture 分次造）
- WHEN 人指 slug 倉（`.devflow/five-station/<slug>/` 下人指得到的檔）
- THEN 三類各至少一筆；每筆能答誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated；禁止把 `event_type=hop_advanced`（或任何具體鍵名）寫成本 Decision／本 Spec 已核；`observability/schema/agent-event.schema.json` 的 `agent_event` 仍為 1.1；本刀 diff 不含該 schema bump
- 觀測:從三筆紀錄能否口頭答五問、以及 `devflow-contract.json` schema_versions.agent_event 看 | 五問可答＋鍵名未鎖＋schema 仍 1.1 算過 | 本 hop：`devflow-contract.json` L12 `agent_event`=`1.1`。後站鎖鍵名當已核 = 偷做 annex，回第 2 站
- Operational Context:
  - Actor:審查者
  - Goal:指得到紀錄，不靠 chat
  - Situation:G-obs-1
  - Known information:語意槽不是 JSON key
  - Missing information:實作會不會順手 bump schema
  - Human decision:2A／2B 已拒
  - Authority:OC-2／約束 11
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:刪冒充的 `attempt_completed`；改寫 slug 倉
  - Audit/handoff requirement:人指得到的檔
  - Observation:見本條觀測

#### S-7.7 RP-9／10／11 必須讀 1A 倉，不得只咬 fixture 字樣
- GIVEN live NEW5 已對某 hop 成功 persist 到計數＝2，且 fixture 正文**沒有**字樣「第 3 次」
- WHEN 第 3 次 hop 重寫被要求執行，並跑接上真計數的 RP-9（及對稱的 RP-10／RP-11）
- THEN 因倉數字＝2 而紅／拒；即使正文沒有「第 3 次」字樣；F1 字樣正則牙可留作回歸，但不得替代本條讀倉路徑
- 觀測:從 RP-9 讀取來源與無字樣時是否仍拒看 | 讀 `.devflow/five-station/<slug>/` 且無字樣仍拒算過；只跑 `five_station_f1.py` 正文正則 → 本條紅 | n-a:接線尚未落地。替代：`scripts/five_station_f1.py:L327-L333` 現行咬字樣；Decision OC-6；6C 已拒
- Operational Context:不適用 — 牙讀倉，無人員交接。

### R-8: 系統 SHALL 鎖死 F3 cut／折 in-flight／刪 token，並把本 hop 限在 4-spec 雙檔
SC-KNIFE／SC-PR／SC-Q-CARRY／8A。後站不准把三把鎖改成可選。本 hop `status: draft`、`verdict` 空。後站 Diff Budget 只准 F2 scripts。

**審的時候看什麼**
本 PR diff 是不是只有兩檔。有沒有人寫 G2 PASS。F3／折線／刪 token 有沒有被標可選。Q9–Q24 有沒有下落。

#### S-8.1 本刀不做 F3 cut
- GIVEN F2 宣稱完成之後
- WHEN 人找「新 slug 預設五站」的 cut 聲明（guide／STATUS／graph 預設）
- THEN 無此聲明；新開 live slug 仍舊 7；把 F3 cut 做成了 → F2 失敗，不是簡化成功
- 觀測:從 guide／STATUS／graph 預設路線看 | 無「新 slug 預設五站」cut 算過 | 本 hop `git diff --name-only origin/main` 不得出現 `guides/`、`graph.yaml`、`STATUS.md`
- Operational Context:不適用 — 刀範圍。

#### S-8.2 本刀不把 in-flight 折成五站
- GIVEN 任一已有 1–7 `.md` 的 slug（含本目錄、含 OLD7 fixture）
- WHEN F2 結束
- THEN 該 slug 仍舊 7；無五站狀態寫入；把折線標成「可選簡化」＝翻 Decision
- 觀測:從 in-flight 目錄與 Out of Scope 是否把折線標可選看 | 仍舊 7＋鎖死不算可選算過 | 見 S-5.1／S-5.2；本檔 Out of Scope 第 2 點
- Operational Context:不適用 — 刀範圍。

#### S-8.3 本刀不刪 G1／G2／ACCEPTED token 或檔
- GIVEN 既有 token 與閘檔
- WHEN F2 結束（含本 hop）
- THEN `scripts/check-gate-tokens.sh` 仍綠；G1／G2／`ACCEPTED` 檔仍在；刪 token 當「謂詞比較好寫」＝翻 Decision（8C）
- 觀測:從 token 檢查與 diff 是否刪 token 檔看 | 檢查綠＋無刪檔算過 | 本 hop 可跑 `bash scripts/check-gate-tokens.sh`
- Operational Context:不適用 — 刀範圍。

#### S-8.4 本 Stage 4 hop 只含 4-spec 雙檔
- GIVEN 本 branch 相對 `origin/main`
- WHEN 跑 `git diff --name-only origin/main`
- THEN 輸出只含 `docs/dev/five-station-f2/4-spec.md` 與 `docs/dev/five-station-f2/4-spec.html`。零 `_templates/`、零 `graph.yaml`、零 `scripts/` 新牙、零 `STATUS.md`、零 `HISTORY.md`、零 `devflow-contract.json`、零 `2-decision.md`
- 觀測:從該指令 stdout 看 | 恰好兩檔算過 | 在本 branch 跑 `git diff --name-only origin/main`
- Operational Context:不適用 — 本 PR 檔集。

#### S-8.5 本 hop 頂欄 draft、verdict 空、不發明 G2 PASS
- GIVEN 本檔 frontmatter
- WHEN 讀 `status:` 與 `verdict:`
- THEN `status` 是 `draft`；`verdict` 為空；`reviewers` 是 `[]`；無人（含 Agent）把本 hop 寫成 G2 PASS／approved
- 觀測:從本檔 L4–L7 看 | draft＋空 verdict＋reviewers [] 算過 | 讀本檔 frontmatter
- Operational Context:
  - Actor:本 hop 寫手
  - Goal:四眼；author ≠ approver
  - Situation:G2 尚未送審
  - Known information:使用者：draft、No G2 PASS
  - Missing information:無
  - Human decision:G2 由適格人類或 fresh reviewer 另 hop
  - Authority:模板 §7
  - External dependency:無
  - Out-of-system action:不准自填 PASS
  - Waiting/timeout behavior:本 hop 停在 draft
  - Recovery:若誤寫 PASS，刪回空
  - Audit/handoff requirement:frontmatter
  - Observation:見本條觀測

#### S-8.6 後站 Stage 5–7 Diff Budget 只准 F2 scripts
- GIVEN 本 slug G2 已過，進入 5-tasks
- WHEN 列 Files 聯集
- THEN 只准：`scripts/test-five-station-f2.sh`、coordinator 實作檔（`scripts/` 下）、`scripts/fixtures/five-station-f2/**`、把 RP-9／10／11 接到 1A 倉的最小改動（可改 `scripts/five_station_f1.py` 讀倉，不改字樣牙回歸）、本目錄 5／6／7 過程檔。不准 `_templates/`、不准各站 `graph.yaml`、不准 `hooks/_doctor_impl.py` 握手語意、不准 bump 契約、不准 F3 cut、不准改 STATUS／HISTORY
- 觀測:從後續 5-tasks Files 聯集看 | 超出上列 → L2／違本 R 算過 | n-a:5-tasks 尚未寫。替代：本檔 Diff Budget 與 Out of Scope
- Operational Context:
  - Actor:Stage 5 寫手
  - Goal:只施工 F2 scripts
  - Situation:G2 剛過
  - Known information:8A 刀範圍
  - Missing information:有沒有人想順便切 graph
  - Human decision:F3 另開 slug
  - Authority:本 R
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:把 F3／模板／doctor 檔從 Files 刪掉
  - Audit/handoff requirement:5-tasks Files
  - Observation:見本條觀測

#### S-8.7 已拒方案不得被 Stage 5 重開
- GIVEN Decision Rejected Alternatives 列 1B、1C、2A、2B、3B、3C、七 stem、4B、4C、5B、5C、6B、6C、7B、7C、8B、8C
- WHEN Stage 5 寫 T 或 Stage 6 做選擇
- THEN 不得把上列方案當成可選實作。點名：5B 檔在＝完；5C F1 綠＝完；七 stem 各一桶；1B run 級倉；2A bump schema；8B 本刀 F3 cut；8C 刪 token／折 in-flight
- 觀測:從 5-tasks／6-notes 是否出現「改採 5B／5C／七 stem／1B／2A／8B／8C」看 | 出現 → 違本 Spec，回第 2 站 | 讀本檔 Out of Scope
- Operational Context:
  - Actor:Stage 5 寫手
  - Goal:不重開已拒案
  - Situation:實作時覺得檔在比較快宣告
  - Known information:Rejected 表
  - Missing information:無
  - Human decision:停，回第 2 站才准翻案
  - Authority:推翻 Decision 不是合法 DD
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:刪該 T
  - Audit/handoff requirement:Non-Goals
  - Observation:見本條觀測

#### S-8.8 Q9–Q24 每條都有 Real-world Disposition 下落
- GIVEN 1-discussion Q9–Q24 與本檔 Real-world Disposition 表
- WHEN 逐條對帳
- THEN Q9–Q23 去向＝本方案處理且下落至少一條 R-／S-；Q24 去向＝刻意維持且下落指向 Out of Scope；無一題消失
- 觀測:從本檔 Disposition 表列看 | Q9–Q24 皆有列算過 | 讀本檔 Real-world Disposition
- Operational Context:不適用 — 對帳表，無人員交接。

## MODIFIED Requirements

本 hop 與本 slug Stage 5–7 **不改** living 契約句。現行正本仍是七份文檔 + 例行 G1／G2／G3：

原條文（`docs/dev/readme-contract-extract.md` L7–L17）：七份檔各一 Gate；G1／G2／G3 物質句仍在。

改什麼（**F3 才改預設路線**；本檔用 ADDED 定義 F2 必須滿足的行為）：coordinator 評五站謂詞，但 F3 前 live 仍舊 7。本 hop 不改正文。

無本 hop 要落地的 MODIFIED 條文。

## REMOVED Requirements

無。不刪 G1／G2／`ACCEPTED` 檔或 token。不刪 Fast。不刪七檔名。不刪 F1 十二群牙。不刪第二條 ID 鏈禁令。

## 行為流程圖(R 級)

```
[R-1] 同一電池拒 hollow
  單一入口 NEW5+OLD7
  檔在不是完
  F1 綠不是完
  只跑 NEW5-HOP-OK 不是完
[R-2] NEW5 hop 停修與問人紅
  HOP-OK 五問可答
  PRED-STOP 停修
  WAIT-RED 注入問人
[R-3] slug 倉三 cap
  persist 先 0 後加 1
  第 3 次拒數字仍 2
  新 run 不歸零
[R-4] 注入 Must-keep 與 Ship 紅
  MK-RED 仍 hop 該格紅
  SHIP-MECH 代寫 Done 該格紅
[R-5] OLD7 freeze 與本目錄
  無五站寫入
  折線注入紅
  本目錄不是 NEW5
[R-6] 三前置 2.1.0 非 inflight F3cut
  缺一條 allow_legacy
  doctor 綠不是路條
  cache 只選碼
[R-7] 五桶觸發與真計數
  不是七 stem
  ledger 答五問不鎖鍵
  RP-9 讀倉不咬字樣
[R-8] 三把鎖與本 hop 兩檔
  不 F3 不折不刪 token
  draft 空 verdict
  後站只准 F2 scripts
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-8.8）。本 hop 能綠的是形狀與對照：`check-spec-gate.sh`、本 PR 檔集、本目錄 freeze md、契約仍 2.0.0、Disposition／CASE 表。F2 行為 S 的綠發生在後站電池落地之後，不在本 PR。
- 既有測試全綠：`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`；`python3 scripts/build-stage4-html.py --action docs/dev/five-station-f2/4-spec.md` 後審頁可解析 R/S。不回歸改既有牙（本 hop 禁改 `scripts/`）。F1 十二群可另跑當地板，不當 F2 完。
- 非功能：本 slug 自己仍走舊 7（S-5.4）。契約不 bump。`agent-event` 仍 1.1。
- 無 golden master（可見路線行為在 F3 才變；本 hop 不改 runtime）。

### Stage 3 對帳

N/A — 本目錄無 `3-prototype.md`。2-decision 無「Stage 3」+「跳過」流程層 OC。本站對 1-discussion Real-world Context 做觸發判定，九條皆未命中（清單如下）。可操作 Demo = 後站 dual-path 電池，不是 Stage 3 UI Variant。不發明 skip OC 進 2-decision（本 hop 不改 2-decision）。

Stage 3 觸發判定（0 命中）：

- 新前端流程：否 — 無新畫面；電池是 CLI selftest
- 改變下一步：否 — 下一步已由 F0 狀態機 + Decision 4A／5A／6A 鎖定；本刀不新發明人機流程
- 角色交接：否 — 不新增角色；coordinator 禁問人
- 人工核准：否 — Ship 唯人已鎖；本刀不改核准 UI
- 等待退回逾時：否 — latch 條件已鎖；無新等待畫面
- 權限差異：否 — 路線認專案樹，不是多角色 UI
- 系統外動作：否 — marketplace 是約束輸入，本刀不改 marketplace
- 多種互動設計：否 — 已選定 1A–8A
- 操作流程不確定：否 — Decision 已核

驗收雛形下落（無 Demo 場景可對；雛形直接掛 S）：

- AC-1 新 run 數字仍在 → S-3.4
- AC-2 第 3 次拒且數字不改小 → S-3.1
- AC-3 doctor 綠仍拒五站 hop → S-6.5
- AC-4 marketplace 單獨不改線 → S-6.6、S-6.8
- AC-5 本 slug 仍舊 7 → S-5.4
- AC-6 token 在、無 F3 cut、in-flight 未折 → S-5.3、S-8.1、S-8.2、S-8.3
- AC-7 三筆紀錄五問可答 → S-7.6、S-2.1
- AC-8 Q9–Q24 有去向 → S-8.8
- AC-9 同一電池兩路可獨立紅也可一起綠 → S-1.1、CASE 表 13 列
- AC-10 三失敗不得當成功 → S-2.3、S-4.1、S-4.2

## Out of Scope

鎖死，後站不准改成 In：

1. **F3 cut**（新 slug 預設五站；guide／STATUS／graph 用語切五站）。
2. **把 in-flight 折成五站**（含本目錄、含任何已有 1–7 `.md` 的 slug）。
3. **刪 G1／G2／`ACCEPTED` token 或檔**。
4. 放寬 hop≤2／Decide≤1／Goal reopen≤1。
5. 拿本 slug 或 `five-station-simplify` 當 NEW5 白老鼠。
6. 把 run 級 `events.jsonl` 當 cap 倉。
7. 把 doctor 綠／marketplace update／他份 cache 當路線許可。
8. 把「檔在」或「F1 綠」或「只跑 NEW5-HOP-OK」當 F2 完成。
9. 本 hop 實作 coordinator、改 STATUS／HISTORY、填 G2 PASS、合併、改 `_templates/`／`graph.yaml`／既有牙（除後站准許的 RP 讀倉最小接線）、bump 契約、改 doctor 握手。
10. 選定 event／倉的 JSON 鍵名或 schema 版本號。
11. 七個 stem 各一桶（B 線 2A）。
12. 改 `hooks/_doctor_impl.py` 握手語意。
13. 重開 F0 十條；廢 Fast；第二條 Journey／Actor／M ID 鏈。
14. 本 hop 改 2-decision 頂欄或 OC 狀態。

## Diff Budget

本節是**估計**。超支本身非偏差，是停下判 L1/L2 的訊號。

**本 Stage 4 hop（立即、本 PR）= 只文件**

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| `4-spec.md` | 1 | ≤1600 | 0 |
| `4-spec.html`（產檔器） | 1 | ≤1500（生成） | 0 |
| `_templates/`／`graph.yaml`／`scripts/`／STATUS／HISTORY／契約／2-decision | 0 | 0 | 0 |

**G2 之後、本 slug Stage 5–7（只 F2 scripts）**［Assumption：coordinator 形未鎖］

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| `scripts/test-five-station-f2.sh`（單一入口） | 1 | ≤200 | 0 |
| coordinator 實作（`scripts/` 下，不含 doctor／模板） | ≤4 | ≤600 | 0 |
| `scripts/fixtures/five-station-f2/new5/` + `old7/` | ≤12 | ≤400 | 0 |
| RP-9／10／11 讀 1A 倉的最小接線（可改 `scripts/five_station_f1.py`） | ≤2 | ≤80 | ≤80 |
| 電池／CASE 測試（與非測試分開） | ≤6 | 0 | ≤800 |
| `_templates/`／`graph.yaml`／doctor 握手／契約 bump／F3 cut／STATUS／HISTORY | 0 | 0 | 0 |

測試與非測試分開估。若用突變補 CASE 極性，測試行可能到天真估法的 3 倍 —— 超支就停、判 L1/L2。F2／F3 以外的母版檔 = 0。

## Dependencies

- 已核 Decision G1 PASS（#333／#334）。無新外部系統。
- F2 依賴 F1 annex（cap 數字、RP-9／10／11、dual-read SLOT）與 F0 狀態機。
- F3 依賴本 slug G3 之後另刀；本檔只定義「尚未 cut」。
- 單一電池入口依賴本檔 DD-2 檔名 `scripts/test-five-station-f2.sh`。
- slug 倉依賴本檔 DD-3 路徑類 `.devflow/five-station/<slug>/`。
- 不新增套件、不新增網路 capability。未經本節授權的新 capability 屬 7-review finding。
- 本 hop 不改 doctor；doctor 只當 S-6.5 的握手對照。

## Design Boundary Contract(條件式;G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組（coordinator × F1 牙 × slug 倉 × 採用端 hops／契約）⑦計數只增與跨 run 讀寫 ⑧slug 倉走 filesystem ⑨Feature Risk = high ⑪五站狀態機 + latch／cap／Escalated 恢復
- Design source: `notes/design/five-station-simplify-brief-v3.md`；`notes/design/five-station-simplify-f0-state-machine.md`；2-decision 1A–8A

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| 本檔 4-spec（契約） | 定義電池／CASE／三前置／五桶／倉位置類 | 本 slug md | 讀 1／2 過程檔 | 改 living 契約句（F3 才動） |
| F2 coordinator（後站 scripts） | 評謂詞、hop／停修、cap、latch | `.devflow/five-station/<slug>/` | 讀 brief §3、本檔 R-2…R-7、專案樹契約與站檔 | 折 in-flight；代寫判定；讀 cache 當路條 |
| F1 scripts／annex | 咬 RP 與 dual-read；F2 後讀真計數 | 母版 scripts | 讀 slug 倉數字 | 用字樣牙替代倉；改 Stage 1–4 模板 |
| 既有 graph／token | 服務舊 7 | 方法包 graph | 被 F3 改**新 slug 預設** | F2 改 graph；刪 token |
| 採用端專案樹 | 路線 SoT：2.1.0 ∧ ¬in-flight ∧ F3-cut | 採用專案契約檔 + `docs/dev/<slug>/` | marketplace 換包（只換碼） | 遠端在 2.0.0 改線 |
| plugin cache | 只選本 process hops 碼 | 該 process 的 plugin root | 被 7A 讀碼 | 當 cut／路條；掃最新 cache |
| run ledger | 既有 attempt／stage 事件 | `.devflow/runs/<run_id>/` | 被 obs 寫 | 當 cap 正本 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| 三前置閘 | 契約版本、是否有 1–7 `.md`、F3-cut 標記 → legacy 或准評 | 缺一條 → `allow_legacy()` | 只讀專案樹，不寫採用端路線 | 2.0.0 採用端仍舊 7 |
| slug 倉 persist | hop_id 桶 + Decide + Goal | 超限 → Escalated | 只增不減；Goal+Decide 同一次 mutation；兩數只成功一筆 → 整次失敗重試 | 舊 7 不套 |
| 電池入口 | 無旗標跑兩組 / 可點名 CASE | 缺一組 → 非 0 | 同一 process 彙總 exit | F1 十二群不是入口 |
| Ship `verdict:` | 人寫 PASS | Agent 寫入 = 未寫 | 頂欄與 checkbox 不是同一筆 | 舊 7 in-flight 仍等人 |
| doctor 握手 | `COMPATIBLE`／exit 0 | 版本∉supported → INCOMPATIBLE | 與路線閘不是同一筆寫入 | 本刀不改握手 |

兩筆寫入只成功一筆：Goal 計數寫入但 Decide 未寫 → 整次 mutation 失敗，不得當 Goal 已重開（S-3.6）。cap 寫入但狀態已 hop 且超限 → Escalated 優先，不得當已過。

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| 本 4-spec | 可測契約 | Decision | 只文件 | DD 待人審 | spec-gate C1–C9 |
| `test-five-station-f2.sh` | 單一入口彙總 13 CASE | NEW5／OLD7 fixture | fixture → 具名格紅綠 → 一顆 exit | 缺一路非 0 | 點名 CASE；注入壞行為 |
| coordinator（後站） | 評三前置與謂詞 | slug 倉、專案樹 | 讀樹 → 准評或 legacy → hop／停 | Escalated；禁問人 | 合成 fixture；倉檔 |
| slug 倉 | 三計數 + 五問紀錄 | coordinator | `.devflow/five-station/<slug>/` | 拒 reset | 換 run_id 再讀 |
| F1 讀倉接線 | RP-9／10／11 真數字 | 倉、既有字樣牙 | 倉優先，字樣牙留回歸 | 無倉仍咬字樣 → 本 R 紅 | 無「第 3 次」字樣的 live 重寫 |

### Design Constraints

- 必須:同一電池；13 CASE 只准加；三前置合取；第一次 persist＝0；五桶；鍵名 OPEN；本 slug 舊 7；本 hop 只兩檔
- 禁止:5B／5C／1B／2A／七 stem／8B／8C；doctor 綠冒充已切；cache 當路條；本 hop 改 STATUS／模板／graph；Agent 代寫 G2 PASS
- Extension point:後站可加 CASE 列；F1 牙加讀倉；F3 另刀加 cut 標記
- Known design limit:本 hop 無 coordinator runtime，行為 S 的現象證據在後站電池；倉內檔名／鍵名未鎖；F3-cut 標記的具體檔名由後站在專案樹內選定（必須可被測試種進 NEW5 fixture）；採用升級逐字稿禁收

## Verification Profile(G2 一併審)

- lane: full（判準:新能力、coordinator 狀態機、跨 run 計數、採用端遠端改線風險。owner 指示 full；與判準相同，無偏離）
- Risk: high（判準:資料遺失／暗改 cap（X5）、併發讀寫（新 run_id 與多 cache）、不可逆若偷 F3 cut、公開方法論路線。模板「資料遺失／併發／不可逆」吃這條）
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得把檔在或 F1 綠或只跑 NEW5-HOP-OK 當 F2 完（S-1.2、S-1.3、S-1.4）
  - 不得把兩支互不認識腳本各綠當 dual-path（S-1.5）
  - 不得把「拒 hop」記成預期紅格綠（S-2.3、S-4.1、S-4.2、S-5.2）
  - 不得把 cap 放進 run 級 events（S-3.7）
  - 不得新 run 歸零（S-3.4）
  - 不得第一次 persist 就計 1（S-3.5）
  - 不得 Goal／Decide 分兩次寫（S-3.6）
  - 不得用 doctor 綠／marketplace／cache 當路條（S-6.5、S-6.6、S-6.7）
  - 不得少一條前置就評五站（S-6.1、S-6.2、S-6.3）
  - 不得七 stem 各一桶（S-7.1、S-7.2）
  - 不得 bump `agent-event` 或鎖鍵名（S-7.6）
  - 不得只咬「第 3 次」字樣（S-7.7）
  - 不得 F3 cut／折 in-flight／刪 token（S-8.1、S-8.2、S-8.3）
  - 不得本 hop 改 STATUS／模板／graph／scripts／契約／2-decision（S-8.4）
  - 不得本 hop 發明 G2 PASS（S-8.5）
  - 不得後站 Files 超出 F2 scripts（S-8.6）
- Required layers:check-spec-gate（本 hop 形狀）。文件層：本 PR 檔集（S-8.4）、frontmatter draft（S-8.5）、Disposition C9、CASE 13 列齊
- Conditional layers:F2 落地 → 電池入口列入 Required 並重跑 13 CASE；改 RP 讀倉 → 重跑無字樣的 NEW5-CAP-3；改 doctor 文案 → 重跑 `hooks/devflow-doctor.sh` + S-6.5
- Explicitly excluded layers:Mutation（本 hop 只規格）、e2e／Playwright（無產品前端）、Race／stress（無多 writer runtime；Concurrency 契約用 S-3.4／S-6.7 對照，不跑壓力）、Windows 真機、本 hop 跑 coordinator（碼 Out of Scope）
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md && python3 scripts/build-stage4-html.py --action docs/dev/five-station-f2/4-spec.md`
- Reliability triage:
  - Concurrency: applicable — 新 `run_id` 與多份 plugin cache 是兩個可獨立出現的更新源；落到 S-3.4、S-6.7
  - Idempotency: applicable — 同一電池再跑、同一對照再評 freeze／檔集／draft 頂欄，結果相同（S-1.1、S-5.4、S-8.4、S-8.5）；倉只增不減（S-3.1、S-3.4）
  - Timeout/retry: n-a — 機械檢查同步結束；HumanWait 是 latch 不是重試（S-2.3、S-4.2）

### Failure Model(Risk: high 必填)

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 檔在當 F2 完 | hollow 出貨 | ls 有檔、電池未跑仍標綠 | Required:S-1.2 | 後站電池才跑 |
| 只跑 F1 十二群 | 無 hop 證明 | 入口轉呼叫 test-five-station-f1.sh | Required:S-1.3 | — |
| 只跑 NEW5-HOP-OK | OLD7 被折仍綠 | OLD7 組未出現 | Required:S-1.4 | — |
| 兩支腳本各綠 | 假 dual-path | 無單一入口彙總 | Required:S-1.5 | — |
| 中途等人 | 比舊 7 更快假完成 | 紀錄含要不要繼續 | Required:S-2.3 | 後站注入 |
| 紅格極性反了 | 壞行為測成綠 | 「拒 hop」當 MK-RED 綠 | Required:S-4.1、S-2.3、S-5.2 | — |
| Must-keep 紅仍 hop | 完整度被掏空 | T 缺 Verify 仍 hop 且該格綠 | Required:S-4.1 | 後站注入 |
| 機械綠當 Done | 出貨是機器的 | 無 PASS 卻 Done | Required:S-4.2 | 後站注入 |
| cap 住 run 級 | 新 run 歸零＝X5 | 第二個 run_id 讀到 0 | Required:S-3.4、S-3.7 | — |
| 第一次 persist 計 1 | 初寫吃掉 hop≤2 | 序列空→1 | Required:S-3.5 | — |
| Goal／Decide 分寫 | Goal 重開躲 Decide cap | 只見 Goal 數 | Required:S-3.6 | — |
| 對 in-flight 建機 | 舊 7 被折 | 五站狀態寫入 OLD7 | Required:S-5.2、S-8.2 | — |
| 本目錄當 NEW5 | 觀測被污染 | 本目錄出現五站 hop | Required:S-5.4、S-5.5 | — |
| doctor 綠冒充已切 | 採用端被遠端改線 | 理由寫 doctor 已綠 | Required:S-6.5 | — |
| marketplace／cache 當 cut | 未宣告 2.1.0 被改線 | update 後路線變五站 | Required:S-6.6、S-6.7 | — |
| 少 F3-cut 仍評五站 | 母版軌提前切線 | live slug 被 hop | Required:S-6.3 | — |
| 七 stem 稀釋 hop≤2 | 3-proto 與 4-spec 各 2 | 出現 proto 桶 | Required:S-7.1、S-7.2 | — |
| bump agent-event | 2.0.0 採用端 doctor 誤紅 | schema 1.1→新版 | Required:S-7.6 | — |
| RP 只咬字樣 | live 第三次假第一次 | 無「第 3 次」字仍過 | Required:S-7.7 | 後站接線 |
| 本 hop 改 STATUS／模板 | 並行 session 互蓋 | diff 出現 STATUS | Required:S-8.4 | — |
| 本 hop 自填 G2 PASS | 假綠 | verdict PASS | Required:S-8.5 | — |

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| slug ledger 的具體路徑／檔名交 4-spec | stage-2 | resolved |
| 單一電池入口的腳本名交 4-spec | stage-2 | resolved |
| F3-cut 標記的具體檔名由後站在專案樹內選定 | 2026-12-31 | open |
| 採用端典型升級=先 marketplace update、後(或不)bump 契約 | 2026-12-31 | open |

路徑與入口檔名已由 DD-2／DD-3 收束，故 resolved。F3-cut 檔名與採用升級逐字稿無現場稿，保持 open，期限未過。升格成「現場都會一起 bump」仍擋（S-6.6）。

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記本檔鎖定的選擇。不翻 1A–8A。推翻 Decision 不是合法 DD。本 hop 不發明 G2 PASS；狀態留待人審。

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 13 具名 CASE 各一條獨立 S；另加電池／hollow／三前置／五桶／本 hop 檔集 S；S 數 45，留在本檔、不另切開新 slug | C 線 anti-hollow；Decision「只准加不准減」 | `2-decision.md` OC-9／CASE 表；本 hop brief | 漏 CASE 或把檔在加成通過條件 = 翻 Decision | 待人審 |
| DD-2 | 單一電池入口檔名＝`scripts/test-five-station-f2.sh`；同一 process；缺一路即非 0 | Decision 把腳本名交 4-spec | `2-decision.md` L309；SC-BATTERY | 改兩支腳本各綠 = 違 S-1.5 | 待人審 |
| DD-3 | cap／紀錄根目錄＝`.devflow/five-station/<slug>/`（專案樹、不隨 run_id 換目錄）；鍵名仍 OPEN；禁止 `.devflow/runs/<run_id>/` | Decision 把路徑交 4-spec；擋 X5 | `2-decision.md` L308；ledger.py L3-L6 反面 | 改回 run 級 = 1B | 待人審 |
| DD-4 | F3-cut 謂詞只讀專案樹「新 slug 預設五站」標記；本 repo 今日無標記＝假；不是 doctor／marketplace／cache；NEW5 fixture 可自己種標記 | 三前置要可測 | `2-decision.md` 4A／OC-12 | 用 doctor 綠當 cut = 4B | 待人審 |
| DD-5 | NEW5 fixture 根＝`scripts/fixtures/five-station-f2/new5/`，開始時零個 1–7 `.md`；OLD7＝`scripts/fixtures/five-station-f2/old7/` 已有 1–7 `.md` | Decision 鎖合成 fixture、不是本目錄 | `2-decision.md` 約束 3 | 拿本 slug 當 NEW5 = RP-15 | 待人審 |
| DD-6 | Feature Risk = high；本檔 `verdict` 空、`status: draft`；implementer 不寫 G2 PASS | 暗改 cap＋遠端改線＋狀態機；四眼 | `_templates/4-spec.md` Risk 判準；本 hop brief | 改 normal 則 Failure Model 變選配；代填 PASS = 假綠 | 待人審 |
| DD-7 | 行為圖 8 框對 8 個 R；審頁產器硬切 8 框 | 產器 `steps[:8]`；本 hop 不改 scripts | `scripts/build-stage4-html.py` L450 | 增 R-9 則圖丟框 | 待人審 |
| DD-8 | Stage 3 對帳 N/A：九條人機觸發 0 命中；Demo = 後站電池 | 使用者 No Stage 3；互動已由 F0＋Decision 鎖定 | 1-discussion Real-world Context；2-decision L306 | 改有 trigger 則須補 Stage 3 或 skip OC | 待人審 |
| DD-9 | 後站 Diff Budget 只准 F2 scripts（入口／coordinator／fixture／RP 讀倉）；模板／graph／doctor／契約／F3＝0 | 使用者 C-line：Diff Budget for F2 scripts only | 本 hop brief；8A | 後站改 graph = 偷 F3 | 待人審 |
| DD-10 | 本 hop 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell；不把審頁塞進 `build-gate-twin.py` STAGES | 與本 slug Stage 2 審頁對稱 | `scripts/build-stage4-html.py`；2-decision L305 | 手包 shell = md／html 分叉 | 待人審 |

### 內部技術選擇(下層,告知即可)

- 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell。
- 本 hop 不改 `STATUS.md`、不 bump plugin、不開 5-tasks、不改 2-decision。
- 原文獨立於 A／B；不讀他線 4-spec。
- 本檔不寫 C4 未定事項三詞字面，改指 `check-spec-gate.sh` `VAGUE_ALL`。
- F1 字樣正則牙留回歸；F2 加讀倉。
- 負向注入 CASE 的治具目錄建議 `scripts/fixtures/five-station-f2/`（後站才新增檔）。

## Test Skeletons(選配)

- `test_s_1_1_single_entry_both_paths`
- `test_s_1_2_files_exist_is_not_f2_done`
- `test_s_1_3_f1_twelve_group_is_not_f2_done`
- `test_s_1_4_new5_hop_ok_alone_is_not_f2_done`
- `test_s_1_5_two_scripts_are_not_dual_path`
- `test_s_2_1_new5_hop_ok`
- `test_s_2_2_new5_pred_stop`
- `test_s_2_3_new5_wait_red_inject`
- `test_s_3_1_new5_cap_3`
- `test_s_3_2_new5_decide_2`
- `test_s_3_3_new5_goal_2`
- `test_s_3_4_new5_run2`
- `test_s_3_5_first_persist_is_zero`
- `test_s_3_6_goal_decide_same_mutation`
- `test_s_3_7_store_not_run_level_events`
- `test_s_4_1_new5_mk_red_inject`
- `test_s_4_2_new5_ship_mech_inject`
- `test_s_5_1_old7_no_five`
- `test_s_5_2_old7_fold_red_inject`
- `test_s_5_3_old7_token`
- `test_s_5_4_old7_self`
- `test_s_5_5_new5_is_synthetic_fixture`
- `test_s_6_1_missing_2_1_0_allow_legacy`
- `test_s_6_2_inflight_allow_legacy`
- `test_s_6_3_no_f3_cut_allow_legacy`
- `test_s_6_4_three_preconditions_then_eval`
- `test_s_6_5_doctor_green_is_not_route`
- `test_s_6_6_marketplace_update_is_not_cut`
- `test_s_6_7_cache_selects_code_not_route`
- `test_s_6_8_2_0_0_plus_five_hops_stays_old_7`
- `test_s_7_1_five_buckets_not_seven_stems`
- `test_s_7_2_proto_and_spec_share_spec_bucket`
- `test_s_7_3_t_retries_not_build_hop`
- `test_s_7_4_no_proto_bucket_without_trigger`
- `test_s_7_5_old_graph_nodes_not_hop_id`
- `test_s_7_6_ledger_five_questions_keys_open`
- `test_s_7_7_rp_reads_true_counts`
- `test_s_8_1_no_f3_cut`
- `test_s_8_2_no_inflight_fold`
- `test_s_8_3_tokens_remain`
- `test_s_8_4_this_pr_two_files`
- `test_s_8_5_draft_no_g2_pass`
- `test_s_8_6_diff_budget_f2_scripts_only`
- `test_s_8_7_rejected_cannot_reopen`
- `test_s_8_8_q9_q24_disposition`

## 確認紀錄

- 接手盤點 | 2026-09-14 | G1 PASS（2-decision approved／verdict PASS／OC-1…12 ✅；#333／#334）。無 `3-prototype.md`。無「Stage 3」+「跳過」OC。living `docs/specs/` 0 條。驗收雛形 AC-1…AC-10 + Decision 13 CASE + SC-BATTERY／DOCTOR／KNIFE／HOLLOW／Q-CARRY／PR。使用者本 hop 明示 No Stage 3、draft、No G2 PASS、只 4-spec+html。
- 雙源清點 | 2026-09-14 | 雛形 10 條 + CASE 13 + 其餘 SC → ADDED R-1…R-8。living 契約句 L7–L17 列 MODIFIED 說明（本 hop 不改正文）。REMOVED 無。
- R 範圍 | 2026-09-14 | Implementer C brief：每具名 CASE 一 S；檔在≠完；三前置 2.1.0∧¬in-flight∧F3-cut；Out of Scope 鎖；Verification Profile；Diff Budget 只 F2 scripts。使用者本指令 = 範圍確認。
- S 展開 | 2026-09-14 | R-1…R-8 全展開；每 S 有觀測欄；交接／核准／等待／權限 S 有 Operational Context。S 數 45。
- CASE／SC 鏈 | 2026-09-14 | 完整表見「CASE → S 對照」「SC → S 對照」。13 CASE 無漏列。
- 3a 四節 | 2026-09-14 | AC／Out of Scope／Diff Budget／Dependencies 齊。
- 3b Profile | 2026-09-14 | lane full、Risk high、Failure Model、Reliability Concurrency=applicable（S-3.4／S-6.7）、DBC applicable。
- 3c Stage 3 | 2026-09-14 | N/A + 九條觸發 0 命中；AC-1…AC-10 逐條掛 S。
- DD 掃描 | 2026-09-14 | 上層十條待人審；DD 節無未決殘留；不翻已核 Decision；無 ✅ 草擬自判；不發明 G2 PASS。
- 機械關卡 | 2026-09-14 | `scripts/check-spec-gate.sh` 須 9/9。審頁 `scripts/build-stage4-html.py --action`。
- 獨立於 A／B | 2026-09-14 | 不讀他線 4-spec。
- 本 hop 不送 G2 | 2026-09-14 | `verdict` 空；`status: draft`；DD 全「待人審」。
