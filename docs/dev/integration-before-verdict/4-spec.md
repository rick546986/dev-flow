---
feature: integration-before-verdict
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-12
---

# 4. 規格 — 填檔牙與活教師(change spec)

> 基準:main tip `1f8d992`(#211 Stage 3 Human ACCEPTED)。契約不 bump。本 hop **只寫規格**,不改 `scripts/` 正本、不改 example／manifest、不 bump plugin、不改 `STATUS.md` 表列、不碰 `#196`／diagram-ir-gate、不發版。
> Decision 正本:`docs/dev/integration-before-verdict/2-decision.md`(A + AS-1 + T-now;OC-1～OC-3 ✅;G1 `verdict` PASS)。tip 模板／指南／Stage 7 節點鏈**已經**是 2c 整合 → 2d Fresh。本檔只把剩餘缺口釘成可測 R/S:**AS-1 填檔牙** + **活教師掃蕩** + 本 slug 後續真跑時「出貨樹=核准樹」。
> G2 `verdict` 留空,留給人類;Agent 不代填 PASS。

## 補助模組生命週期（預覽）

主詞是「Stage 7 填檔牙 + 活教師」,不是整份方法論。直式圖,置中。
- 新生（這輪沒有）：不加第二套整合工具。
- 改行為（相關一格）：`check-stage67` ST 射程延到填好的 7-review;`ALREADY_SYNCED` 只能重綁 Source SHA 或本項 FAIL;example／manifest／腳本檔頭改口。
- 退役：沒有。
- 不動：2c／2d 編號、整合腳本演算法、`_templates/7-review.md` 已搬散文、`#196`、九條制度缺口、HISTORY／dispatch 當時句、plugin 版本、Stage 1–4 模板正文。

## ADDED Requirements

### R-1: 系統 SHALL 拒絕只寫作廢的 ALREADY_SYNCED 填檔
沿用既有檢查家族(`scripts/check-stage67-enforcement.sh` ST 組,可與 gate-consistency／7-review 形狀檢查同家族;OC-1)。不另造第二套整合工具。不重寫 `scripts/devflow-integration-regression.sh` 的 STATUS／exit 演算法。填好的 7-review 若已宣稱勾過 2c 或送 G3,且正文有 `ALREADY_SYNCED`,則恢復欄必須是「重綁 Final Fresh。Source SHA: <hex≥7>」或「本項 FAIL」。只寫「證據不算數」或「輸出不算數」、沒有重綁 SHA、也沒有本項 FAIL → 指定檢查 exit ≠ 0(SC-2)。

**審的時候看什麼**
看指定檢查對五份對照的 exit,不是看模板裡有沒有「重跑 Final Fresh」那句。void-only 必須紅;重綁 SHA 與本項 FAIL 必須綠。

#### S-1.1 void-only 填檔必須紅
- GIVEN 一份填好的 `7-review.md`:`status: approved`、`verdict: PASS`、正文含 `ALREADY_SYNCED`,恢復欄或結論只寫「證據不算數」或「輸出不算數」,沒有 `Source SHA:` 後接 ≥7 個 hex,也沒有字面「本項 FAIL」
- WHEN 跑本 feat 掛進 `check-stage67` 家族的指定填檔檢查(同一入口,不另開 `check-already-synced.sh`)
- THEN exit ≠ 0;stdout 或 stderr 含 `void-only` 或同等「只寫作廢」字樣
- 觀測:從該檢查的 exit 與 stderr 看 | exit ≠ 0 且含指定字樣算過 | 用 Stage 3 同形 fixture(`ALREADY_SYNCED` + 只寫作廢 + `verdict: PASS`)測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:勾 2c 時不能靠「證據不算數」過關
  - Situation:腳本印 `ALREADY_SYNCED`(已合過、merge-base 被污染)
  - Known information:腳本結論行、模板恢復二選一
  - Missing information:當下 HEAD 是否已重綁進 Fresh Source SHA
  - Human decision:選重綁 Source SHA,或寫本項 FAIL
  - Authority:reviewer 寫 7-review;檢查 exit 擋勾過
  - External dependency:整合腳本只算只判,不動樹
  - Out-of-system action:在終端機跑指定檢查
  - Waiting/timeout behavior:檢查同步結束;無重試契約
  - Recovery:補「重綁 Final Fresh。Source SHA: <hex≥7>」或改寫「本項 FAIL」後重跑;不要進 Verdict
  - Audit/handoff requirement:結論塊留 STATUS + 三 SHA／REF + 恢復欄
  - Observation:見本條觀測

#### S-1.2 重綁 Source SHA 必須綠
- GIVEN 一份已宣稱勾過 2c／送 G3 的 7-review,`STATUS: ALREADY_SYNCED`,恢復欄為「重綁 Final Fresh。Source SHA: def4567890abc」(hex 長度 ≥7)
- WHEN 跑 S-1.1 同一支指定檢查
- THEN exit 0;輸出含該 SHA(`def4567890abc`)
- 觀測:從 exit 與輸出看 | exit 0 且輸出含該 ≥7 hex 算過 | 用 Stage 3 `rebind-sha` 同形 fixture 測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:恢復路徑之一走通,才能進 2d Fresh
  - Situation:已合過,要重綁 Fresh 到當下 HEAD
  - Known information:重綁後的 Source SHA
  - Missing information:無
  - Human decision:接受重綁並進 2d
  - Authority:reviewer 寫 SHA;2d 再驗 SHA = 當時 HEAD
  - External dependency:`git rev-parse HEAD`(2d 對帳,本條只驗填檔形狀)
  - Out-of-system action:把 SHA 寫進恢復欄
  - Waiting/timeout behavior:無
  - Recovery:SHA 短於 7 hex → 當 void-only 紅,補滿再跑
  - Audit/handoff requirement:恢復欄看得見 SHA
  - Observation:見本條觀測

#### S-1.3 本項 FAIL 必須綠
- GIVEN 一份已宣稱勾過 2c／送 G3 的 7-review,`STATUS: ALREADY_SYNCED`,恢復欄字面為「本項 FAIL」
- WHEN 跑 S-1.1 同一支指定檢查
- THEN exit 0;輸出含 `item-FAIL` 或字面「本項 FAIL」
- 觀測:從 exit 與輸出看 | exit 0 且含 FAIL 字樣算過 | 用 Stage 3 `item-fail` 同形 fixture 測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:停在 2c,從乾淨座標重算,而不是整份 G3 默默過
  - Situation:不願重綁、或座標已髒到不能當證據
  - Known information:本項要停
  - Missing information:下一次腳本座標
  - Human decision:寫本項 FAIL,不進 2d
  - Authority:reviewer 寫 FAIL;owner 看 7-review
  - External dependency:無
  - Out-of-system action:從乾淨 FORK 重跑整合腳本
  - Waiting/timeout behavior:停到人重算
  - Recovery:要繼續就重跑腳本,不得把 FAIL 改成只寫「不算數」
  - Audit/handoff requirement:FAIL 寫在恢復欄,不是只在聊天
  - Observation:見本條觀測

#### S-1.4 腳本 GUIDANCE 必須寫出恢復下一步
- GIVEN `scripts/devflow-integration-regression.sh` 印 `結論:STATUS=ALREADY_SYNCED`(exit 仍為既有碼 2;演算法不改)
- WHEN 讀該次 stdout 的 GUIDANCE 句,以及同檔散發副本 `docs/dev/tools/devflow-integration-regression.sh` 的同一句
- THEN 兩份都含「重綁」或「重跑 Final Fresh」,且含「FAIL」;不得只說「輸出不算數」就結束
- 觀測:從兩檔 GUIDANCE 字串看 | 指定兩詞都在、不是只有「輸出不算數」算過 | 對 tip 改口後的兩檔原文測
- Operational Context:不適用 — 檔頭旁的人讀字串,無人員交接。

### R-2: 系統 SHALL 放過未宣稱的 n-a 與 draft
牙只在「宣稱勾過整合項／送 G3」時發動。`N_A_NO_INCOMING` 與未勾 2c 的 draft 不預先紅(Stage 3 發動時機)。

**審的時候看什麼**
n-a 與未勾草稿跑同一支檢查必須 exit 0,reason 為 no-fire。未勾不得被當成已送 G3。

#### S-2.1 N_A_NO_INCOMING 不預先紅
- GIVEN 一份 7-review 記 `N_A_NO_INCOMING`(分岔後對方零新 commit),沒有 `ALREADY_SYNCED` 作廢句
- WHEN 跑 S-1.1 同一支指定檢查
- THEN exit 0;輸出含 `no-fire` 與 `N_A_NO_INCOMING`
- 觀測:從 exit 與輸出看 | exit 0 且含兩個指定字串算過 | 用 Stage 3 `na-incoming` 同形 fixture 測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:零新 commit 記 n-a 即過,直接進 2d
  - Situation:整合腳本 exit 0 / STATUS=`N_A_NO_INCOMING`
  - Known information:對方零新 commit
  - Missing information:無
  - Human decision:記 n-a,不合併
  - Authority:腳本 STATUS;reviewer 轉記
  - External dependency:整合腳本
  - Out-of-system action:無合併
  - Waiting/timeout behavior:無
  - Recovery:若後來對方有新 commit,重跑腳本改 STATUS
  - Audit/handoff requirement:n-a 寫在結論塊
  - Observation:見本條觀測

#### S-2.2 未勾 draft 不預先紅
- GIVEN 一份 `status: draft` 的 7-review,正文可出現 `ALREADY_SYNCED` 或「證據不算數」,但 2c 整合項未勾(`[ ]`)、`verdict` 空白、也沒有 `結論:STATUS=ALREADY_SYNCED`
- WHEN 跑 S-1.1 同一支指定檢查
- THEN exit 0;輸出含 `no-fire` 與 `draft`
- 觀測:從 exit 與輸出看 | exit 0 且含 `no-fire` 與 `draft` 算過 | 用 Stage 3 `draft-unclaimed` 同形 fixture 測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:還沒勾 2c 的草稿不被提前紅擋住
  - Situation:正在填 7-review
  - Known information:檔是 draft、項未勾
  - Missing information:最終 STATUS
  - Human decision:繼續填,不要先送 G3
  - Authority:未宣稱則牙不發動
  - External dependency:無
  - Out-of-system action:繼續編輯
  - Waiting/timeout behavior:無
  - Recovery:勾了 2c 或填 `verdict: PASS` 之後,改走 S-1.1～S-1.3
  - Audit/handoff requirement:draft 未宣稱 ≠ 已送 G3
  - Observation:見本條觀測

### R-3: 系統 SHALL 清除活教師舊序
T-now:一次改完仍在教舊序的活教師。2c 編號仍叫整合回歸,不重編號整份清單(拒 B)。活路徑上 `rg -n '執行清單 2c 的 Final Fresh|Exit Checklist.*整合回歸.*計算工具'` 零命中(SC-3)。

**審的時候看什麼**
對下列活路徑跑指定 `rg`;再看 example 把 Fresh／gauntlet 寫在 2d,腳本檔頭不再自稱 Exit Checklist 工具。

#### S-3.1 example 不再把 2c 寫成 Fresh／gauntlet
- GIVEN 活路徑 `example/contract-expiry-reminder/7-review.md` 與同目錄 `4-spec.md`
- WHEN 搜「執行清單 2c 的 Final Fresh」與「執行清單 2c gauntlet」
- THEN 兩檔都零命中;若仍要指 Final Fresh／gauntlet 命令,序號寫 `2d` 不寫 `2c`
- 觀測:從 `rg -n '執行清單 2c 的 Final Fresh|執行清單 2c gauntlet' example/contract-expiry-reminder/` 看 | 輸出為空算過 | 用改口後的 example 兩檔測
- Operational Context:
  - Actor:採用者(會抄 example)
  - Goal:抄範例時走 2c 整合 → 2d Fresh,不是 2c = Fresh
  - Situation:打開完整範例當樣張
  - Known information:模板頂註已是 2c 整合
  - Missing information:範例是否已改口
  - Human decision:以改口後範例為抄本
  - Authority:example 是教師,不是死紀錄
  - External dependency:無
  - Out-of-system action:人打開 example
  - Waiting/timeout behavior:無
  - Recovery:若 rg 仍命中,同一 T 改到零命中
  - Audit/handoff requirement:2c 仍可出現在「整合回歸」語境,只禁 2c=Fresh／gauntlet
  - Observation:見本條觀測

#### S-3.2 manifest 與整合腳本檔頭不再教舊序
- GIVEN 活路徑 `manifests/p4-gauntlet-gates.md`、`scripts/devflow-integration-regression.sh`、`docs/dev/tools/devflow-integration-regression.sh`
- WHEN 搜「執行清單 2c 的文檔化命令」與「Exit Checklist.*整合回歸.*計算工具」
- THEN 三檔都零命中;manifest 若仍指 gauntlet 命令則寫 2d;兩支腳本檔頭改成「步 2c 整合回歸,Fresh 之前,不是 Exit 程序」(或同等、不含 Exit Checklist 計算工具)
- 觀測:從 `rg -n '執行清單 2c 的文檔化命令|Exit Checklist.*整合回歸.*計算工具' manifests/p4-gauntlet-gates.md scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh` 看 | 輸出為空算過 | 用改口後三檔測
- Operational Context:不適用 — 檔頭／manifest 字面,無人員交接。

#### S-3.3 衍生 fixture 與 example 同一 T 改口
- GIVEN `scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md` 現含「執行清單 2c gauntlet」
- WHEN 改 `example/contract-expiry-reminder/4-spec.md` 的 2c gauntlet 句
- THEN 該 fixture 同一 T 改成 2d(或刪掉舊針);`scripts/check-spec-gate.sh` 對該負向 fixture 仍 exit 1(C5 待裁決牙不因改序號而假綠)
- 觀測:從 fixture 原文與 `bash scripts/check-spec-gate.sh scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md` 看 | 無「2c gauntlet」且檢查仍 exit 1 算過 | 用改口後 fixture 測
- Operational Context:不適用 — 衍生副本同步,無人員交接。

#### S-3.4 活路徑聯合 needle 歸零
- GIVEN S-3.1 與 S-3.2 的活路徑聯集
- WHEN 跑 `rg -n '執行清單 2c 的 Final Fresh|Exit Checklist.*整合回歸.*計算工具'` 於該聯集
- THEN 零命中。`notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/` 不在聯集(OC-2;死紀錄不改)
- 觀測:從該 `rg` 輸出看 | 活路徑空、死紀錄未改算過 | 用本 repo 現檔測
- Operational Context:不適用 — 聯合掃蕩,無人員交接。

### R-4: 系統 SHALL 保留 2c 編號與模板牙
承認 tip 已是 2c 整合 → 2d Fresh。不重編號、不重寫整合腳本演算法。既有模板順序牙必須仍綠(SC-4)。Q6 若加錨,只鎖「整合回歸在 Final Fresh 之前」與「ALREADY_SYNCED 不得只寫證據不算數」,不重寫 `_templates/7-review.md` 已搬的 2c 散文。

**審的時候看什麼**
三支既有腳本仍 exit 0;模板頂註「整合回歸」仍在「Final Fresh Run」之前;整合腳本仍只算只判。

#### S-4.1 模板 2c 仍在 2d 前
- GIVEN `_templates/7-review.md` 頂註執行清單
- WHEN 找字面「整合回歸」與「Final Fresh Run」
- THEN 「整合回歸」出現且位置在「Final Fresh Run」之前;2c 標題仍含「整合回歸」;Exit Checklist 沒有「合併它印的」
- 觀測:從模板頂註與 Exit 節原文看 | 兩詞都在且 integ 偏移 < fresh 偏移算過 | 用 tip 現檔測
- Operational Context:不適用 — 模板字面順序,無人員交接。

#### S-4.2 既有模板牙仍綠
- GIVEN 本 repo tip 的 `scripts/check-stage67-enforcement.sh`、`scripts/check-integration-regression-guard.sh`、`scripts/test-evidence-gauntlet.sh`
- WHEN 分別跑 `bash scripts/check-stage67-enforcement.sh`、`bash scripts/check-integration-regression-guard.sh`、`bash scripts/test-evidence-gauntlet.sh`(P0-1 段)
- THEN 三支皆 exit 0;不得為了填檔牙刪掉或改鬆既有 ST 模板順序項
- 觀測:從三支 exit 看 | 皆 0 算過 | 在本 repo 根跑三支測
- Operational Context:不適用 — 回歸牙,無人員交接。

#### S-4.3 整合腳本演算法不變
- GIVEN `scripts/devflow-integration-regression.sh` 頂註契約:只算只判、絕不動樹;`ALREADY_SYNCED` exit 2
- WHEN 比對本 feat 實作前後的 STATUS 集合與 exit 碼(`0` / `10` / `11` / `2`)
- THEN STATUS 名稱與 exit 碼不變;不新增自動重綁、不把 `ALREADY_SYNCED` 自動當 FAIL、不 merge／rebase
- 觀測:從腳本頂註與 `GUIDANCE` 旁的 `sys.exit(code)` 看 | 四個碼仍是 0／10／11／2,且檔內仍有「絕不動樹」算過 | 用實作 diff 對 `scripts/devflow-integration-regression.sh` 測(只准檔頭／GUIDANCE 字)
- Operational Context:不適用 — Non-Goal 邊界。

### R-5: 系統 SHALL 鎖定出貨樹等於核准樹
本 slug 是第一條真實 full lane 載體(G-out-3／SC-1／SC-5)。後續走到 Stage 7 並勾 Exit 之後,7-review 所記 Source SHA 與 `git rev-parse HEAD` 逐字相同。本 feature 過程檔不得宣告「跳過 2c」或「Exit 才合併」。本 hop 只落本檔;Stage 5+ 另 hop。

**審的時候看什麼**
本 slug 的 7-review Source SHA 對得上 Exit 後 HEAD。故意 Verdict 後才合的對照必須能指出兩 SHA 不同。過程檔搜不到「跳過 2c」「Exit 才合併」。

#### S-5.1 Exit 後 Source SHA 等於 HEAD
- GIVEN 本 slug `docs/dev/integration-before-verdict/7-review.md` 已勾 Exit,且 Verification Evidence 有 `Source SHA`
- WHEN 在同一工作樹跑 `git rev-parse HEAD`,並讀該 Source SHA
- THEN 兩個字串逐字相同(皆 ≥7 hex);不是「應該沒差」
- 觀測:從該 7-review 的 Source SHA 欄與 `git rev-parse HEAD` 輸出看 | 兩字串相等算過 | 拿本 slug 後續真跑到 Stage 7 的產物測(AC-1)
- Operational Context:
  - Actor:owner
  - Goal:Verdict 綁的樹就是出貨的樹
  - Situation:本 slug 已走完 2c→2d→雙軸→Verdict→Exit 文件
  - Known information:7-review Source SHA
  - Missing information:無(HEAD 可現算)
  - Human decision:兩 SHA 不同就不得 ship
  - Authority:owner 簽 G3;merger 合的是 2c 的 `INTEGRATION_SHA`
  - External dependency:git
  - Out-of-system action:Exit 只准文件／PR,不准再合碼
  - Waiting/timeout behavior:無
  - Recovery:HEAD 變了 → 作廢 G3,回 2c／2d 重綁
  - Audit/handoff requirement:Source SHA 寫在 7-review
  - Observation:見本條觀測

#### S-5.2 Verdict 後才合的對照能指出兩 SHA 不同
- GIVEN 一份對照紀錄:先寫下 Verdict Source SHA=`aaa1111`,再合 `INTEGRATION_SHA` 使 `git rev-parse HEAD`=`bbb2222`
- WHEN 比對紀錄裡的 Source SHA 與合完後 HEAD
- THEN 兩字串不同;對照必須把兩個 SHA 都印出來
- 觀測:從對照紀錄兩欄看 | `aaa1111` ≠ `bbb2222` 且兩值都在算過 | 用故意「Verdict 後才合」的文字／git fixture 測(AC-1 對照)
- Operational Context:不適用 — 對照樣本,無真實交接。

#### S-5.3 過程檔不宣告跳過 2c 或 Exit 才合併
- GIVEN 本 slug `docs/dev/integration-before-verdict/` 內已提交的 1～7 過程檔(本 hop 有 1／2／3／4)
- WHEN 搜「跳過 2c」與「Exit 才合併」
- THEN 零命中(引 Decision 拒項的句子不算宣告;本條咬的是「本 slug 要這樣做」的流程指令)
- 觀測:從 `rg -n '跳過 2c|Exit 才合併' docs/dev/integration-before-verdict/` 看 | 若命中,該行必須是在拒項／對照敘事,不得是本 slug 執行指令算過 | 用本目錄現檔測(SC-5)
- Operational Context:不適用 — 過程檔字面。

## MODIFIED Requirements

本 repo 無 `docs/specs/` living spec。下列是**活教師原文**,T-now 改口;不是重寫已搬的 `_templates/7-review.md` 2c 散文。

### M-1: example 7-review 把 2c 當 Final Fresh
原條文(`example/contract-expiry-reminder/7-review.md:24`):
> 實案由執行清單 2c 的 Final Fresh Run 產出
改成:序號改 `2d`;其餘 gauntlet／Source SHA 契約不變。承接 S-3.1。

### M-2: example 4-spec 把 2c 當 gauntlet
原條文(`example/contract-expiry-reminder/4-spec.md:223`):
> (= 7-review 執行清單 2c gauntlet 命令的 `--require-layer` 清單,逐層一個 flag)
改成:`2d gauntlet`。衍生 fixture `scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md:229` 同一句同步。承接 S-3.1／S-3.3。

### M-3: gauntlet manifest 把 2c 當文檔化命令
原條文(`manifests/p4-gauntlet-gates.md:52`):
> 7-review 執行清單 2c 的文檔化命令
改成:2d。承接 S-3.2。

### M-4: 整合腳本檔頭自稱 Exit Checklist 計算工具
原條文(`scripts/devflow-integration-regression.sh:2` 與 `docs/dev/tools/devflow-integration-regression.sh:2`):
> Stage 7 Exit Checklist「(條件式)整合回歸」計算工具
改成:步 2c 整合回歸、Fresh 之前、不是 Exit 程序。演算法與 exit 碼不變。承接 S-3.2／S-4.3。

## REMOVED Requirements

無。不刪 2c 編號、不刪既有 ST 模板牙、不刪整合腳本 STATUS。

## 行為流程圖(R 級)

```
[R-1] 拒絕只寫作廢的 ALREADY_SYNCED 填檔
  宣稱 2c 已勾或送 G3
  void-only → 牙紅
  重綁 SHA 或本項 FAIL → 綠
  GUIDANCE 寫出恢復下一步
[R-2] 放過未宣稱的 n-a 與 draft
  N_A_NO_INCOMING 不紅
  未勾 draft 不紅
[R-3] 清除活教師舊序
  example 2c≠Fresh
  manifest／檔頭改口
  衍生 fixture 同步
  活路徑 needle 歸零
[R-4] 保留 2c 編號與模板牙
  整合回歸仍在 Fresh 前
  既有三支牙仍綠
  演算法只算只判
[R-5] 鎖定出貨樹等於核准樹
  Exit 後 Source SHA = HEAD
  對照能指出兩 SHA 不同
  禁跳過 2c、禁 Exit 才合
```

## Acceptance Criteria

- 全部 S 綠(S-1.1～S-5.3)。
- 既有測試全綠:S-4.2 三支既有牙 + 本 repo 既有 `devflow-check` 回歸。
- 非功能:填檔檢查對單份 7-review 在本機同步跑完;不新增網路 capability。
- 行為不變類(R-4):golden master — 同一 `_templates/7-review.md` 頂註,改動前後「整合回歸」仍在「Final Fresh Run」之前;整合腳本 STATUS／exit 碼集合不變。

## Out of Scope

- B 重編號整份 Stage 7 清單。
- C／AS-2 只改文件、不加填檔牙。
- AS-3 改整合腳本 STATUS／exit 演算法,或讓腳本自己重綁／自動 FAIL。
- T-hist:改寫 `notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/` 當時舊序句。
- `#196`、gate-twin Backlog、diagram-ir-gate。
- 九條制度缺口實作。
- Windows 真機驗證。
- 本 hop 落地守衛碼、改 example／manifest 正本、bump plugin、發版。
- 本 hop 寫 `5-tasks.md`／Stage 6／Stage 7 產物(R-5 的真跑留後續 hop)。
- 本 feature branch 改 `docs/dev/STATUS.md` 正本表列(OC-3)。
- 重寫 `_templates/7-review.md` 已搬的 2c 散文。

## Diff Budget

本節是**估計**(給後續實作 hop,不是本規格 PR 的檔數)。超支本身非偏差,是停下判 L1/L2 的訊號。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| `check-stage67` ST 填檔牙 + 五份對照 fixture | ≤3 | ≤140 | ≤220 |
| 整合腳本檔頭 + GUIDANCE(正本與散發) | ≤2 | ≤30 | ≤40 |
| 活教師(example 兩檔 + manifest + 衍生 fixture) | ≤4 | ≤20 | ≤10 |
| **合計** | **≤9** | **≤190** | **≤270** |

[Assumption] 係數按「一個 S 一到兩條測試」,未加 mutation。本規格 PR 本身只動 `docs/dev/integration-before-verdict/4-spec.md` 與 twin html。

## Dependencies

- `scripts/check-stage67-enforcement.sh` ST 組 —— justification:OC-1 沿用既有家族,把射程從模板字串延到填好的 7-review。
- `scripts/check-integration-regression-guard.sh` —— justification:散發副本與正本檔頭／parity;改檔頭必須兩邊一起過。
- `scripts/test-evidence-gauntlet.sh` P0-1 —— justification:SC-4 回歸,證明模板序牙沒被拆。
- `scripts/devflow-integration-regression.sh` 與 `docs/dev/tools/` 散發副本 —— justification:只改檔頭／GUIDANCE;演算法仍是既有依賴。
- 無新外部服務、無新套件、無 migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ②新增或修改公開 API(填檔檢查對 7-review 的 exit 契約);③跨模組 Interface(2c 結論塊欄位);⑨Feature Risk = high
- Design source: 既有 pattern —— `check-stage67` ST、`_templates/7-review.md` 2c 恢復二選一、Stage 3 throwaway 結論塊;欄位名是 Decision 留給本檔的 local lock

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| `check-stage67` 填檔牙 | 讀填好的 7-review;void-only 紅;重綁／FAIL／n-a／draft 綠 | **擁有**填檔通過／失敗判定 | → 7-review 正文、→ 既有 ST 模板牙 | 不得新開第二套整合 CLI;不得改整合腳本 exit 碼;不得改 STATUS 演算法 |
| 填好的 7-review | 結論塊(STATUS + 三 SHA／REF + 恢復欄) | **擁有**人填的恢復選擇 | ← 整合腳本 stdout | 不得只寫作廢就勾;Verdict 後不得改碼 |
| 整合腳本 | 只算只判;印 STATUS | **擁有**三 SHA 與 STATUS 名稱 | → git fetch／rev-parse | 不得 merge／重綁／自動 FAIL |
| 活教師檔 | example／manifest／檔頭改口 | 各檔擁有自己的字面 | → 模板序(2c 整合、2d Fresh) | 不得改 HISTORY／dispatch;不得重編號 2c |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| 填檔牙讀 7-review | in:一份 md;out:exit 0／≠ 0 + reason | void-only → ≠ 0;`N_A_NO_INCOMING`／draft → 0 | 只讀,不寫 7-review | 既有 ST 模板字串項仍在;只加填檔射程 |
| 2c 結論塊 | in:腳本結論行;out:`STATUS` + FORK／HEAD／INTEGRATION／REF + 恢復欄 | 缺恢復欄且已宣稱 → void-only | 人寫一格恢復,不是腳本覆寫 | 欄位名本檔鎖定;不改腳本 STATUS 集合 |
| 腳本 stdout | in:--integration + --fork-sha;out:結論行 + GUIDANCE | `ALREADY_SYNCED` 仍 exit 2 | 不動工作樹 | GUIDANCE 加恢復句;exit 碼相容 |
| 活教師改口 | in:舊針;out:2d／新檔頭 | 衍生 fixture 不同步 → 該 T 紅 | example 與 fixture 同一 T | 2c 編號保留給整合回歸 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| 填檔牙函式(住 `check-stage67-enforcement.sh` 或同家族一函式) | 判宣稱、判恢復形狀 | ← 7-review 字串 | md → 宣稱? → 恢復二選一? | 未宣稱 no-fire;void-only 紅 | S-1.1～S-2.2 五份 fixture |
| GUIDANCE 字串 | 告訴人下一步 | ← STATUS | 印在結論行後 | 不改 exit | S-1.4 字面 |
| 教師改口 | 換序號／檔頭 | ← example／manifest | 搜舊針 → 改 2d | 漏改 fixture → S-3.3 紅 | S-3.1～S-3.4 `rg` |

### Design Constraints
- 必須:沿用 `check-stage67` 家族;結論塊有 STATUS + 三 SHA／REF + 恢復欄;Source SHA ≥7 hex;牙只在已宣稱時發動;活教師與衍生 fixture 同一 T;既有模板牙仍綠。
- 禁止:第二套整合工具;重編號 2c;改整合腳本演算法;改 HISTORY／dispatch;本 hop 改 STATUS 表列;本 hop 落地碼當規格的一部分;代填 G2 PASS。
- Extension point:本 slug 後續 Stage 5–7 真跑鎖 S-5.1;Q6 若加 renderer 錨,只准兩句(見 DD-5)。
- Known design limit:
  ① 填檔牙讀字面,不重算 git merge-base;腳本座標真偽仍靠人貼結論行。
  ② Cursor／編輯器不能擋人在 Verdict 後改碼;那是 7-review「作廢 G3」契約,本 feat 不新造 hook。
  ③ 本 hop 不產生 7-review;S-5.1 要等本 slug 後續 hop 才有觀測物。

## Verification Profile(G2 一併審)
- lane: full(判準:新能力、改公開檢查契約、高風險人機互動(G3 假綠)。owner 已 lock full;無偏離)
- Risk: high(判準:公開檢查 exit 契約 + G3 假綠會讓未審樹出貨。模板「公開 API／不可逆契約副作用」吃這條)
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得只寫「證據不算數／輸出不算數」就讓已宣稱的 `ALREADY_SYNCED` 過關(S-1.1)
  - 不得誤殺 `N_A_NO_INCOMING` 或未勾 draft(S-2.1／S-2.2)
  - 不得重編號 2c、不得拆既有模板順序牙(S-4.1／S-4.2)
  - 不得改整合腳本 STATUS／exit 演算法(S-4.3)
  - 不得改 HISTORY／dispatch／stage7-loop 當時句(S-3.4、OC-2)
  - 不得在本 slug 過程檔宣告跳過 2c 或 Exit 才合併(S-5.3)
  - 不得碰 `#196`／diagram-ir-gate／九條缺口／本 hop bump plugin
- Required layers:check-spec-gate／check-stage67-enforcement／check-integration-regression-guard／test-evidence-gauntlet
- Conditional layers:Supply chain — 當實作改到 example／manifest／腳本檔頭時,必跑 S-3.4 的 `rg` 聯集
- Explicitly excluded layers:Mutation(本 hop 只規格;方法包未把 mutation 列為本 feat 必跑)、e2e／Playwright(無產品前端)、Race／stress(單檔字面檢查,無新併發契約)、Windows 真機(Out of Scope)
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/integration-before-verdict/4-spec.md && bash scripts/check-stage67-enforcement.sh && bash scripts/check-integration-regression-guard.sh && bash scripts/test-evidence-gauntlet.sh`
- Reliability triage:
  - Concurrency: n-a — 單一 reviewer 寫一份 7-review;檢查只讀;無多 writer 契約
  - Idempotency: applicable — 同一份 fixture 再跑指定檢查,exit 與 reason 相同(S-1.1～S-2.2)
  - Timeout/retry: n-a — 本機檔案／本機 git;檢查同步結束,不自動重試

Human verdict: ACCEPTED(Stage 3 CLI Demo;`3-prototype.md` attestation `human:rick @ 2026-09-12`)

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| void-only 仍綠 | G3 假過;核准樹可在 Exit 後被換 | 指定檢查對作廢句 exit 0 | Required:S-1.1 | — |
| n-a／draft 被誤殺 | 零新 commit 或未填完就被擋 | n-a 或 draft fixture exit ≠ 0 | Required:S-2.1／S-2.2 | — |
| 活教師仍教 2c=Fresh | 採用者抄舊序,第一條 full lane 自己帶偏 | SC-3 `rg` 在活路徑仍命中 | Required:S-3.4 | — |
| example 改了 fixture 沒改 | spec-gate 負向針漂,C5 假綠或假紅 | fixture 仍寫 2c gauntlet | Required:S-3.3 | — |
| 重編號拆既有牙 | ST／guard 紅或改錨 | S-4.2 任一支 exit ≠ 0 | Required:S-4.2 | — |
| 另造第二套整合 CLI | 兩套方法論 | 出現 `check-already-synced.sh` 當唯一入口 | Required:S-1.1 觀測「同一入口」 | — |
| 腳本自己重綁或自動 FAIL | 違反只算只判 | 腳本開始 merge 或改 exit 語意 | Required:S-4.3 | — |
| Verdict 後才合 | 出貨樹 ≠ 核准樹 | Exit 後 Source SHA ≠ HEAD | Required:S-5.1／S-5.2 | — |
| 編輯器仍能在 Verdict 後改碼 | 人跳過「作廢 G3」 | 工作樹出現 Verdict 後 commit | 明示 Known limit ② | 本 feat 不新造 editor hook |

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記 Decision／Stage 3 留給本檔鎖定的選擇。不翻 A + AS-1 + T-now。狀態留待人審;G2 由人類裁決,Agent 不代填 ✅、不代填 PASS。

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 2c 結論塊欄位鎖定為:`STATUS`、`FORK`／`HEAD`／`INTEGRATION`／`REF`、恢復欄二選一「重綁 Final Fresh。Source SHA: <hex≥7>」或「本項 FAIL」。標題用 `## 2c 整合結論` | Stage 3 throwaway 已鎖形狀;Decision 把欄位名留給 4-spec | `3-prototype.md:49-57`;`2-decision.md` 內部技術選擇 Q6 形狀 | 改欄名則 S-1.1～S-1.3 fixture 全改 | 待人審 |
| DD-2 | 發動條件=正文有 `ALREADY_SYNCED` **且**已宣稱(2c 項 `[x]`、或 `結論:STATUS=ALREADY_SYNCED`、或 `verdict: PASS`、或 `status: approved`)。n-a 與未勾 draft 不發動 | Stage 3 發動時機;避免誤殺草稿 | `3-prototype.md:59`;`2-decision.md` Risk「n-a 與 draft」 | 改成見字就紅則 S-2.2 翻案 | 待人審 |
| DD-3 | 填檔牙掛進 `check-stage67-enforcement.sh` ST 組(同家族可加 gate-consistency／7-review 形狀檢查)。不新開 `check-already-synced.sh` 當唯一入口 | OC-1 禁止第二套家族 | `2-decision.md` OC-1 | 改獨立腳本要重審「不另造方法論」 | 待人審 |
| DD-4 | 重綁 SHA 地板 = **≥7 hex**(Stage 3 用 `def4567890abc`)。短於 7 當 void-only | 與 gauntlet Source SHA 地板對齊,避免 `abc` 這種過短值 | `3-prototype.md:140`;`_templates/7-review.md` Source SHA ≥7 慣例 | 改 40 或 64 則 S-1.2 地板句重寫 | 待人審 |
| DD-5 | Q6 錨句只准這兩句:「整合回歸在 Final Fresh 之前」「ALREADY_SYNCED 不得只寫證據不算數」。不重寫已搬的 2c 散文 | Decision In 收窄 Q6 | `2-decision.md:100`;`2-decision.md:115` | 加第三句或重寫 2c 正文 = 回第 2 站 | 待人審 |
| DD-6 | 活教師改口只動編號／檔頭:Fresh／gauntlet 從 2c 改 2d;2c 仍叫整合回歸。衍生 `spec-gate-dd-subsection` 與 example 同一 T | T-now + Stage 3 觀察「沒有重編號整份清單」 | `2-decision.md` T-now;`3-prototype.md:123` | 改成整表重編號 = 採 B,已拒 | 待人審 |
| DD-7 | Feature Risk = high;`verdict` 本 hop 留空,由人類 G2 填 | 公開檢查契約 + G3 假綠;四眼原則 | `_templates/4-spec.md` Risk 判準;本 hop brief「Leave G2 verdict empty」 | 改 normal 則 Failure Model 改選配;代填 PASS = 假綠 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 指定檢查入口字面沿用 `bash scripts/check-stage67-enforcement.sh`,不在本 hop 發明新 CLI 名。
- GUIDANCE 加恢復句,不動 `sys.exit(code)` 與 STATUS 名稱。
- 審頁用 `scripts/build-stage4-html.py --action`;G2 twin 用 `scripts/build-gate-twin.py <根> integration-before-verdict 4-spec`。不手包 html-shell,不把審頁塞進 gate-twin STAGES。
- 本 hop 不改 `docs/dev/STATUS.md` 正本表列(OC-3)。
- 本 hop 不落地 Stage 6 守衛碼;形狀以 R/S 為準。

## Test Skeletons(選配)

- `test_s_1_1_void_only_filled_already_synced_fails`
- `test_s_1_2_rebind_source_sha_passes`
- `test_s_1_3_item_fail_passes`
- `test_s_1_4_guidance_names_rebind_or_fail`
- `test_s_2_1_na_no_incoming_no_fire`
- `test_s_2_2_draft_unclaimed_no_fire`
- `test_s_3_1_example_drops_2c_fresh_needle`
- `test_s_3_2_manifest_and_headers_drop_old_teacher`
- `test_s_3_3_spec_gate_fixture_stays_red`
- `test_s_3_4_live_path_rg_zero`
- `test_s_4_1_template_integ_before_fresh`
- `test_s_4_2_existing_teeth_still_green`
- `test_s_4_3_integration_script_exit_codes_unchanged`
- `test_s_5_1_source_sha_equals_head_after_exit`
- `test_s_5_2_post_verdict_merge_contrast_differs`
- `test_s_5_3_no_skip_2c_process_order`

## Stage 3 對帳

| Demo 場景 | Human verdict | 下落 |
|---|---|---|
| AC-2 void-only 必須紅 | ACCEPTED | S-1.1 |
| AC-2 重綁 SHA 或本項 FAIL | ACCEPTED | S-1.2、S-1.3 |
| AC-2 n-a／draft 不預先紅 | ACCEPTED | S-2.1、S-2.2 |
| AC-3 意圖序 + 活教師改口 | ACCEPTED | S-3.1～S-3.4、S-4.1;正本改口 Out of Scope(本 hop)→ Stage 6 做,契約在 R-3 |
| AC-1 出貨樹=核准樹(對照敘事) | ACCEPTED | S-5.1、S-5.2、S-5.3 |
| Method 結論塊欄位 | ACCEPTED 形狀 | DD-1；R-1 恢復欄 |
| Method 發動時機 | ACCEPTED | DD-2；R-2 |
| Operational Context Recovery(重綁或 FAIL;n-a 進 2d;draft 繼續填) | ACCEPTED | S-1.1 Recovery、S-2.1、S-2.2 |

無 REVISE／NOT_REVIEWED 場景。3-prototype `Human verdict: ACCEPTED` + `human:rick @ 2026-09-12`。2-decision 無「跳過 Stage 3」OC。

## 確認紀錄
- 雙源清點 | 2026-09-12 | 驗收雛形 AC-1／AC-2／AC-3 共 3 條;living spec `docs/specs/` 0 條可引 → 行為全數 ADDED;活教師四句進 MODIFIED。Decision 剩餘 = AS-1 填檔牙 + 活教師掃蕩(tip 已 2c→2d Fresh)
- R 範圍 | 2026-09-12 | implementer-A 依 Decision A+AS-1+T-now 與 owner brief「remaining AS-1 ALREADY_SYNCED filled-file tooth + live-teacher sweep」編碼 R-1～R-5。G2 留給人審,不代確認為 PASS
- S 展開 | 2026-09-12 | R-1～R-5 全展開;每 S 有觀測欄;交接／核准／系統外動作的 S 有 Operational Context
- 3a 四節 | 2026-09-12 | AC／Out of Scope／Diff Budget／Dependencies 齊
- 3b Profile | 2026-09-12 | lane full、Risk high、Failure Model、Reliability triage、Design Boundary applicable
- 3c Stage 3 | 2026-09-12 | 五個 ACCEPTED Demo 場景逐場有 R/S 下落
- DD 掃描 | 2026-09-12 | 上層七條待人審;無「待裁決」殘留;不翻已核 Decision
- G2 verdict | 2026-09-12 | 留空,留給人類,不代填 PASS
