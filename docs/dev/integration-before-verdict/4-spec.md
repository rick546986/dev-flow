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

> 基準:main tip `1f8d992`(#211 Stage 3 Human ACCEPTED)。G1 已核(`2-decision.md` `status: approved` / `verdict: PASS`)。Decision 正本:`docs/dev/integration-before-verdict/2-decision.md`(A + AS-1 + T-now;OC-1～OC-3 ✅)。
> tip 模板／指南／Stage 7 節點鏈**已經**是 2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 只准文件。本檔不重編號、不重寫整合腳本演算法。剩餘可測契約 = **AS-1 填檔牙** + **T-now 活教師掃蕩** + 本 slug 自己走完時 Source SHA 對 HEAD。
> 本 hop **只寫規格**。不改 `scripts/` 正本、不落地守衛碼、不開 Stage 5、不碰 `#196`／diagram-ir-gate、不發版、不 bump plugin、不改正本 `STATUS.md` 表列。
> **G2 留給人類**:frontmatter `verdict` 空、`status` 留 draft。Agent 不代填 PASS。

## 補助模組生命週期（預覽）

主詞是 Stage 7 填檔檢查與活教師。有關聯的收成一格,不拆檔名。
- 新生（這輪沒有）：不加欄
- 改行為（相關一格）：`check-stage67` ST 射程伸到填好的 7-review;example／manifest／腳本檔頭改口;整合腳本 GUIDANCE 補恢復句
- 退役：沒有
- 不動：2c／2d 編號、整合腳本只算只判演算法、`_templates/7-review.md` 已對散文、HISTORY／dispatch／stage7-loop、`#196`、plugin 版號、STATUS 表列

## ADDED Requirements

### R-1: 系統 SHALL 對宣稱 2c 已勾或已送 G3、且正文記 ALREADY_SYNCED 的填好 7-review，只接受重綁 Final Fresh Source SHA 或本項 FAIL
指定檢查是 `scripts/check-stage67-enforcement.sh` 既有 ST 組的射程延伸(OC-1),不新開第二套整合工具、不改整合腳本演算法與 exit code。只寫「證據不算數」或「輸出不算數」、沒有重綁 SHA、也沒有「本項 FAIL」→ 該檢查 exit ≠ 0。`N_A_NO_INCOMING` 與未宣稱的 draft 不發動。

**審的時候看什麼**
拿五份填檔 fixture 跑指定檢查,對 exit。再讀兩份整合腳本的 `ALREADY_SYNCED` GUIDANCE 是否寫出恢復下一步。

#### S-1.1 只寫作廢必須紅
- GIVEN 一份填好的 7-review,frontmatter 含 `verdict: PASS` 與 `status: approved`,正文含 `ALREADY_SYNCED`,恢復欄只寫「證據不算數」與「輸出不算數」,沒有 `Source SHA:` 後接至少 7 個連續 hex,也沒有獨立一行「本項 FAIL」
- WHEN `bash scripts/check-stage67-enforcement.sh` 掃到該檔(ST 填檔射程;fixture 落在 `scripts/fixtures/as1-filled-tooth/void-only.md` 或同等被掃路徑)
- THEN exit ≠ 0;stdout 或 stderr 含 `ALREADY_SYNCED`,且含 `證據不算數` 或 `void-only`
- 觀測:從該次指令的 exit 與 stderr 原文看 | exit ≠ 0 且指定字串出現算過 | 用 void-only fixture 測(AC-2／SC-2;Stage 3 Demo void-only)
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:勾 2c 時不能靠「證據不算數」過關
  - Situation:腳本印 `ALREADY_SYNCED`;人想繼續勾整合項並送 G3
  - Known information:腳本結論字、現行模板恢復二選一
  - Missing information:重綁後的 HEAD SHA,或是否裁 FAIL
  - Human decision:重綁 Final Fresh,或寫本項 FAIL
  - Authority:reviewer 改 7-review 與(僅限 2c)HEAD;指定檢查決定紅／綠
  - External dependency:整合腳本座標;git
  - Out-of-system action:終端機跑指定檢查;要對 HEAD 時另跑 `git rev-parse HEAD`
  - Waiting/timeout behavior:檢查同步結束;無自動重試
  - Recovery:紅了補「重綁 Final Fresh。Source SHA: <hex≥7>」或改寫「本項 FAIL」,再跑同一檢查
  - Audit/handoff requirement:紅的 stderr 必須讓下一手看得出是作廢句被拒,不是不明失敗
  - Observation:見本條觀測

#### S-1.2 重綁 Source SHA 必須綠
- GIVEN 一份填好的 7-review,宣稱與 S-1.1 相同(`verdict: PASS`、`status: approved`、正文 `ALREADY_SYNCED`),恢復欄寫「重綁 Final Fresh。Source SHA: def4567890abc」(至少 7 個連續 hex)
- WHEN 對該檔跑與 S-1.1 同一支指定檢查
- THEN exit 0
- 觀測:從該次指令 exit 看 | exit 0 算過 | 用 `scripts/fixtures/as1-filled-tooth/rebind-sha.md`(SHA=`def4567890abc`)測(AC-2／SC-2;Stage 3 Demo rebind)
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:作廢舊 Fresh 證據後,把 Source SHA 綁到合完後 HEAD
  - Situation:`ALREADY_SYNCED`;已重跑 2d 並寫入新 SHA
  - Known information:重綁後 SHA 字串
  - Missing information:無(SHA 已寫)
  - Human decision:確認 SHA 等於當時 `git rev-parse HEAD` 再進雙軸
  - Authority:reviewer 寫 Source SHA;2d 之後 Verdict 前仍可改碼
  - External dependency:git
  - Out-of-system action:跑 Final Fresh;把 SHA 貼進 7-review
  - Waiting/timeout behavior:檢查同步
  - Recovery:SHA 少於 7 hex 當 S-1.1 形紅;補滿再跑
  - Audit/handoff requirement:7-review 看得到 `Source SHA:` 與 hex
  - Observation:見本條觀測

#### S-1.3 明示本項 FAIL 必須綠
- GIVEN 一份填好的 7-review,宣稱與 S-1.1 相同,正文有獨立一行「本項 FAIL」,沒有重綁 `Source SHA:` hex
- WHEN 對該檔跑與 S-1.1 同一支指定檢查
- THEN exit 0
- 觀測:從該次指令 exit 看 | exit 0 算過 | 用 `scripts/fixtures/as1-filled-tooth/item-fail.md` 測(AC-2／SC-2;Stage 3 Demo FAIL)
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:無法重綁時把整合項停住,不默默送 G3
  - Situation:座標髒、不能當證據
  - Known information:腳本印 `ALREADY_SYNCED`
  - Missing information:乾淨 FORK／HEAD 座標
  - Human decision:寫「本項 FAIL」並從乾淨座標重算,不進 Verdict
  - Authority:reviewer 寫 FAIL;owner 看 G3 未送
  - External dependency:整合分支
  - Out-of-system action:重算腳本座標
  - Waiting/timeout behavior:檢查同步
  - Recovery:FAIL 是這一步停,不是整份 G3 默過
  - Audit/handoff requirement:7-review 看得到「本項 FAIL」
  - Observation:見本條觀測

#### S-1.4 N_A_NO_INCOMING 不發動
- GIVEN 一份 7-review 記 `N_A_NO_INCOMING`,沒有 `verdict: PASS`,沒有 `status: approved`,沒有已勾(`[x]`)的整合項
- WHEN 對該檔跑與 S-1.1 同一支指定檢查
- THEN exit 0;stdout／stderr 若提到本檔,含 `N_A_NO_INCOMING` 或 `no-fire`,不得把該檔當 S-1.1 的 void-only 紅
- 觀測:從 exit 與輸出看 | exit 0 且無 void-only 紅算過 | 用 `scripts/fixtures/as1-filled-tooth/na-incoming.md` 測(Stage 3 Demo n-a)
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:對方零新 commit 時記 n-a 並進 2d,不被填檔牙誤殺
  - Situation:整合腳本 exit 0、`N_A_NO_INCOMING`
  - Known information:腳本三 SHA／REF 與 n-a 結論
  - Missing information:無
  - Human decision:記 n-a,進 2d Fresh
  - Authority:reviewer 寫 n-a
  - External dependency:整合腳本
  - Out-of-system action:跑整合腳本
  - Waiting/timeout behavior:無
  - Recovery:若後來對方有新 commit,重跑腳本,不再走 n-a
  - Audit/handoff requirement:結論塊看得到 `N_A_NO_INCOMING`
  - Observation:見本條觀測

#### S-1.5 未宣稱的 draft 不發動
- GIVEN 一份 7-review,`status: draft`,正文出現 `ALREADY_SYNCED` 與「證據不算數」,沒有 `verdict: PASS`,沒有已勾(`[x]`)的整合項,也沒有 `結論:STATUS=ALREADY_SYNCED`
- WHEN 對該檔跑與 S-1.1 同一支指定檢查
- THEN exit 0(不因該 draft 檔紅)
- 觀測:從 exit 看 | exit 0 算過 | 用 `scripts/fixtures/as1-filled-tooth/draft-unclaimed.md` 測(Stage 3 Demo draft)
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:還沒勾 2c／未送 G3 的草稿可繼續填
  - Situation:草稿裡先貼了腳本輸出
  - Known information:檔仍是 draft
  - Missing information:人尚未宣稱 2c 完成
  - Human decision:繼續填,或勾 2c 並走 S-1.1／S-1.2／S-1.3
  - Authority:draft 未送 G3
  - External dependency:無
  - Out-of-system action:繼續編輯
  - Waiting/timeout behavior:無
  - Recovery:一宣稱 2c 或送 G3,同一份若仍只寫作廢 → 改走 S-1.1
  - Audit/handoff requirement:frontmatter 仍是 draft
  - Observation:見本條觀測

#### S-1.6 GUIDANCE 必須寫出恢復下一步
- GIVEN `scripts/devflow-integration-regression.sh` 與 `docs/dev/tools/devflow-integration-regression.sh` 兩份檔頭後的 `ALREADY_SYNCED` GUIDANCE 字串(正本與散發副本)
- WHEN 讀兩份檔內 `GUIDANCE["ALREADY_SYNCED"]`(或同等印到「結論:STATUS=ALREADY_SYNCED」後面的那句)
- THEN 兩份同一句都同時含「重綁」或「重跑 Final Fresh」,以及「本項 FAIL」或「FAIL」;不得只剩「輸出不算數」而沒有這兩個恢復詞。腳本演算法、exit 0／10／11／2 對照表不變
- 觀測:從兩檔 GUIDANCE 字串看 | 兩個恢復詞都在、兩檔字串相同、exit 對照表未改算過 | 用 `rg -n 'ALREADY_SYNCED' scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh` 對出那句測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:看到 `ALREADY_SYNCED` 就知道下一步是重綁或 FAIL
  - Situation:剛跑完整合腳本
  - Known information:腳本 stdout 結論行
  - Missing information:若 GUIDANCE 只說不算數,人不知道要做什麼
  - Human decision:重綁或 FAIL
  - Authority:腳本只印指導,不動樹
  - External dependency:無
  - Out-of-system action:讀 stdout
  - Waiting/timeout behavior:無
  - Recovery:S-1.1 牙仍擋只寫作廢;GUIDANCE 是給人看的下一步
  - Audit/handoff requirement:正本與散發副本 GUIDANCE 同一句
  - Observation:見本條觀測

### R-2: 系統 SHALL 在活教師路徑停止把 2c 教成 Final Fresh 或 gauntlet，並停止把整合腳本教成 Exit Checklist 工具
T-now。改口只動編號與檔頭:2c 仍叫整合回歸;Fresh／gauntlet 改稱 2d。不重編號整份清單。歷史派工／HISTORY／stage7-loop 不改(OC-2)。

**審的時候看什麼**
對 Decision 點名的活路徑跑指定 `rg`;現檔必須零命中。再抽一眼 example 把 Fresh／gauntlet 寫在 2d。

#### S-2.1 完整範例不再把 2c 當 Fresh／gauntlet
- GIVEN 現樹 `example/contract-expiry-reminder/7-review.md` 與 `example/contract-expiry-reminder/4-spec.md`(含已提交的同名 html,若 html 含相同 needle 也要改)
- WHEN 跑 `rg -n '執行清單 2c 的 Final Fresh|執行清單 2c gauntlet' example/contract-expiry-reminder/`
- THEN 命中數為 0;7-review 把 Final Fresh／gauntlet 命令寫成執行清單 **2d**;4-spec Verification Profile 把 gauntlet 命令寫成執行清單 **2d**
- 觀測:從該 `rg` 的命中數與兩檔編號句看 | 零命中且兩處改稱 2d 算過 | 用現樹 example 兩檔測(SC-3;Stage 3 Demo 活教師)
- Operational Context:
  - Actor:採用者／owner(會抄 example)
  - Goal:抄範例時走 2c 整合 → 2d Fresh,不是 2c = Fresh
  - Situation:打開完整範例當樣張
  - Known information:模板頂註已是 2c→2d
  - Missing information:若畫面仍寫 2c Fresh,會以為模板錯
  - Human decision:照範例編號做 Stage 7
  - Authority:example 是教師,不是牙
  - External dependency:無
  - Out-of-system action:讀 example
  - Waiting/timeout behavior:無
  - Recovery:Stage 6 改正本 example;本規格不在 Stage 4 改那些檔
  - Audit/handoff requirement:改口 commit 與 fixture 同步見 S-2.5
  - Observation:見本條觀測

#### S-2.2 gauntlet manifest 不再把 2c 當文檔化命令
- GIVEN 現樹 `manifests/p4-gauntlet-gates.md`
- WHEN 跑 `rg -n '執行清單 2c 的文檔化命令' manifests/p4-gauntlet-gates.md`
- THEN 命中數為 0;該句改成執行清單 **2d** 的文檔化命令
- 觀測:從該 `rg` 命中數與改口句看 | 零命中且改稱 2d 算過 | 用現樹該 manifest 測(SC-3)
- Operational Context:不適用 — 文件編號對帳,無人員交接。

#### S-2.3 整合腳本檔頭不再自稱 Exit Checklist 計算工具
- GIVEN `scripts/devflow-integration-regression.sh` 與 `docs/dev/tools/devflow-integration-regression.sh` 檔頭註解
- WHEN 跑 `rg -n 'Exit Checklist.*整合回歸.*計算工具' scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh`
- THEN 命中數為 0;兩份檔頭改寫成步 2c 整合回歸、Fresh 之前、不是 Exit 程序。`scripts/check-integration-regression-guard.sh` 的正本／副本 parity 仍綠
- 觀測:從該 `rg` 命中數與兩檔頭句、parity 檢查 exit 看 | 零命中、兩檔頭同義、parity exit 0 算過 | 用現樹兩檔頭 + `bash scripts/check-integration-regression-guard.sh` 測(SC-3／SC-4)
- Operational Context:
  - Actor:採用者讀散發副本檔頭
  - Goal:不要把整合工具當成 Exit 才跑的計算程序
  - Situation:複製 `docs/dev/tools/` 腳本
  - Known information:模板 Exit 只確認「已在 Fresh 前完成」
  - Missing information:若檔頭仍寫 Exit Checklist 工具,會在 Exit 才跑
  - Human decision:在 2c 跑腳本,不在 Exit 才跑
  - Authority:檔頭是教師;parity 牙鎖兩份相同
  - External dependency:無
  - Out-of-system action:讀檔頭
  - Waiting/timeout behavior:無
  - Recovery:改檔頭後重跑 parity
  - Audit/handoff requirement:兩份檔頭同一句
  - Observation:見本條觀測

#### S-2.4 活路徑聯合 needle 歸零
- GIVEN 活路徑集合:`example/contract-expiry-reminder/`、`manifests/p4-gauntlet-gates.md`、`scripts/devflow-integration-regression.sh`、`docs/dev/tools/devflow-integration-regression.sh`
- WHEN 跑 `rg -n '執行清單 2c 的 Final Fresh|Exit Checklist.*整合回歸.*計算工具' example/contract-expiry-reminder/ manifests/p4-gauntlet-gates.md scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh`
- THEN 命中數為 0(SC-3 原句)
- 觀測:從該 `rg` 命中數看 | 零命中算過 | 用 SC-3 那條指令測
- Operational Context:不適用 — 聯合掃蕩,無人員交接。

#### S-2.5 衍生 fixture 與 example 同改
- GIVEN `scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md` 現含「執行清單 2c gauntlet」句(抄自 example 4-spec)
- WHEN Stage 6 改 example 4-spec 的 2c gauntlet 編號
- THEN 同一 T 把該 fixture 同步改成 2d gauntlet(或刪掉這句抄本);不得只改 example 而留下 fixture 舊句
- 觀測:從 example 4-spec 與該 fixture 的 gauntlet 編號句看 | 兩處同號(皆 2d)或 fixture 已無該抄本算過 | 用這兩個檔對帳測
- Operational Context:不適用 — fixture 同步,無人員交接。

### R-3: 系統 SHALL 維持 tip 已搬的 2c 整合 → 2d Fresh 模板序與既有模板字串牙
承認散文已搬。不重編號 `2c. **整合回歸**`。不重寫整合腳本只算只判演算法。既有三支模板牙必須仍綠。

**審的時候看什麼**
打開 `_templates/7-review.md` 頂註看 2c 在 2d 前。再跑三支已綠的檢查。

#### S-3.1 模板仍是 2c 整合在 2d Fresh 前
- GIVEN `_templates/7-review.md` 頂註執行清單
- WHEN 搜「整合回歸」與「Final Fresh Run」
- THEN 「整合回歸」出現在「Final Fresh Run」之前;Exit Checklist 只確認整合已在 Final Fresh 之前完成,正文沒有「Exit 才合併 `INTEGRATION_SHA`」的步驟
- 觀測:從頂註兩詞相對位置與 Exit 段看 | 整合在 Fresh 前、Exit 無合併步驟算過 | 用現樹 `_templates/7-review.md` 測(AC-3／SC-4)
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:按清單先整合再 Fresh
  - Situation:打開模板做本 slug 或採用專案
  - Known information:本檔 R-1／R-2 是牙與教師,不是再搬散文
  - Missing information:無
  - Human decision:不跳過 2c
  - Authority:模板是清單正本
  - External dependency:無
  - Out-of-system action:讀模板
  - Waiting/timeout behavior:無
  - Recovery:若有人提重編號,回 2-decision(B 已拒)
  - Audit/handoff requirement:2c 標題仍是整合回歸
  - Observation:見本條觀測

#### S-3.2 三支既有模板牙仍綠
- GIVEN 現樹 `scripts/check-stage67-enforcement.sh`、`scripts/check-integration-regression-guard.sh`、`scripts/test-evidence-gauntlet.sh`
- WHEN 分別跑 `bash scripts/check-stage67-enforcement.sh`、`bash scripts/check-integration-regression-guard.sh`、`bash scripts/test-evidence-gauntlet.sh`(P0-1 段含在內)
- THEN 三支皆 exit 0;ST 組「出貨樹=審過的樹」仍過
- 觀測:從三支指令 exit 看 | 皆 0 算過 | 在本 repo 根跑這三支測(SC-4)
- Operational Context:不適用 — 回歸牙,無人員交接。

#### S-3.3 不重編號、不重寫演算法
- GIVEN `scripts/check-integration-regression-guard.sh` 現用 `2c.\s*\*\*整合回歸\*\*` 抓段,且 `scripts/devflow-integration-regression.sh` 檔頭寫「只算與只判,絕不動樹」
- WHEN 本 slug Stage 6 落地 R-1／R-2
- THEN 該抓段 regex 仍能命中 `_templates/7-review.md`;整合腳本仍不 merge／rebase／checkout／寫入工作樹;exit 0＝`N_A_NO_INCOMING`、10／11＝SYNC_REQUIRED、2＝fail-closed 的對照不變
- 觀測:從 regex 命中與腳本檔頭／exit 對照表看 | regex 仍命中、演算法不動樹、exit 對照未改算過 | 用現樹模板 + 腳本檔頭 + `check-integration-regression-guard.sh` 測
- Operational Context:不適用 — Non-Goal 邊界,無人員交接。

### R-4: 本 slug 走到 Stage 7 並勾 Exit 之後，7-review 所記 Source SHA SHALL 與 git rev-parse HEAD 逐字相同
本 slug 是第一條真實 full lane 載體(G-out-3)。本 hop 只交 4-spec;SHA 對帳在後續真跑到 Stage 7 時驗。禁止在本 slug 流程文宣告「跳過 2c」或「Exit 才合併」。

**審的時候看什麼**
本 slug 自己的 7-review Source SHA 對 `git rev-parse HEAD`。另備一份「Verdict 後才合」的對照,兩 SHA 必須不同。

#### S-4.1 Exit 後兩 SHA 逐字相同
- GIVEN 本 slug `docs/dev/integration-before-verdict/7-review.md` 已勾 Exit,且 Verification Evidence 寫了 Source SHA
- WHEN 在同一工作樹跑 `git rev-parse HEAD` 並與該 Source SHA 逐字比
- THEN 兩個字串相同
- 觀測:從 7-review Source SHA 欄與 `git rev-parse HEAD` 輸出看 | 逐字相同算過 | 用本 slug 後續真跑到 Stage 7 的那份 7-review 測(AC-1／SC-1)
- Operational Context:
  - Actor:owner／Stage 7 reviewer
  - Goal:核准樹就是出貨樹
  - Situation:Exit 勾完、準備 ship
  - Known information:7-review 寫下的 Source SHA
  - Missing information:若 Exit 後還合過碼,HEAD 會漂
  - Human decision:兩 SHA 不同就不得宣稱 G3 shipped
  - Authority:owner 簽 G3;merger 只合腳本印出的 INTEGRATION_SHA 且必須發生在 2c
  - External dependency:git、GitHub PR
  - Out-of-system action:`git rev-parse HEAD`
  - Waiting/timeout behavior:無
  - Recovery:合完後必須重綁 Fresh(S-1.2)再審;不得在 Verdict 後補碼
  - Audit/handoff requirement:Source SHA 留在 7-review
  - Observation:見本條觀測

#### S-4.2 對照樣本 Verdict 後才合則兩 SHA 不同
- GIVEN 一份對照 7-review,Source SHA 寫在 Verdict 當下,之後才合併 `INTEGRATION_SHA`(工作樹 HEAD 因此改變)
- WHEN 比對該 Source SHA 與合併後的 `git rev-parse HEAD`
- THEN 兩個字串不同;紀錄必須指出「核准 SHA ≠ 出貨 SHA」
- 觀測:從對照檔 Source SHA 與合併後 HEAD 看 | 兩字串不同且紀錄寫出不相等算過 | 用 throwaway repo 或 fixture 對照測(AC-1／SC-1)
- Operational Context:
  - Actor:owner
  - Goal:證明舊序會讓核准≠出貨
  - Situation:刻意走 Fresh→Verdict→Exit 才合
  - Known information:Verdict 時 SHA
  - Missing information:合併帶進來的未審 commit
  - Human decision:拒絕把這份當 shipped
  - Authority:對照不得當本 slug 正本
  - External dependency:git
  - Out-of-system action:在 throwaway 樹合併
  - Waiting/timeout behavior:無
  - Recovery:對照只作反例,不送 G3
  - Audit/handoff requirement:對照標明不是本 slug 正本
  - Observation:見本條觀測

#### S-4.3 本 slug 流程文不宣告跳過 2c 或 Exit 才合併
- GIVEN 本 slug `docs/dev/integration-before-verdict/` 內 1-discussion／2-decision／3-prototype／本 4-spec,以及後續 5-tasks／6-notes／7-review
- WHEN 搜「跳過 2c」與「Exit 才合併」作為**本 slug 要執行的流程宣告**
- THEN 找不到把這兩句當本 slug SOP 的句子;1-discussion 裡描述舊序痛點的當時句可留(當時說法),不得改寫成現行步驟
- 觀測:從本 slug 資料夾全文搜那兩句看 | 無「本 slug 請跳過 2c／請 Exit 才合」的指令句算過 | 用 `rg -n '跳過 2c|Exit 才合' docs/dev/integration-before-verdict/` 並逐命中判讀測(SC-5)
- Operational Context:不適用 — 文件宣告邊界;舊序痛點句是紀錄不是 SOP。

## MODIFIED Requirements

本 repo 無 `docs/specs/` living 條文。受影響的是方法論活路徑,原句如下;行為改寫進上方 ADDED,不另發第二組 R。

| 活路徑原句 | 改什麼 | 承接 |
|---|---|---|
| `scripts/check-stage67-enforcement.sh:314-315` 只咬**模板**有「重跑 Final Fresh」,不掃填好的 7-review | ST 射程延伸到宣稱 2c／送 G3 的填檔 | R-1 |
| `scripts/devflow-integration-regression.sh:204-205`(散發副本同句)GUIDANCE 只說「本次輸出不算數」 | 同一句補上重綁或 FAIL;演算法不動 | S-1.6 |
| `example/contract-expiry-reminder/7-review.md:24`「執行清單 2c 的 Final Fresh Run」 | 2c→**2d** | S-2.1 |
| `example/contract-expiry-reminder/4-spec.md:223`「執行清單 2c gauntlet」 | 2c→**2d** | S-2.1 |
| `manifests/p4-gauntlet-gates.md:52`「執行清單 2c 的文檔化命令」 | 2c→**2d** | S-2.2 |
| `scripts/devflow-integration-regression.sh:2` 與散發副本檔頭「Exit Checklist…計算工具」 | 改成 2c 整合、Fresh 之前 | S-2.3 |
| `scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md:229` 抄了 2c gauntlet | 與 example 同 T 改 2d | S-2.5 |

`_templates/7-review.md` 2c／2d 散文**不改**(已對;S-3.1)。`notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/` **不改**(OC-2)。

## REMOVED Requirements

(無 —— 不刪既有模板步驟,不刪既有模板牙。)

## 行為流程圖(R 級)
```
[R-1] 填檔牙強制恢復二選一
  宣稱 2c／送 G3 且記 ALREADY_SYNCED
  只寫作廢紅;重綁 SHA 或 FAIL 綠
  n-a 或 draft 未宣稱則不發動
[R-2] 活教師停止教舊序
  example 與 manifest 的 Fresh／gauntlet 改稱 2d
  腳本檔頭不再自稱 Exit Checklist 工具
[R-3] 維持 2c 整合到 2d Fresh
  模板序與三支模板牙仍綠
  不重編號、不重寫演算法
[R-4] 本 slug Exit 後 SHA 相同
  7-review Source SHA 對 git rev-parse HEAD
  對照樣本 Verdict 後才合則兩 SHA 不同
```

## Acceptance Criteria
- S-1.1～S-4.3 對應測試全綠。
- 既有 `check-stage67-enforcement.sh`／`check-integration-regression-guard.sh`／`test-evidence-gauntlet.sh` 全綠(回歸;S-3.2)。
- 非功能:指定檢查對單份 7-review 在本機同步結束;不新增網路外呼;不新增背景 job。
- 行為不變類(模板序、整合腳本演算法、exit 對照):golden master —— 同輸入,改動前後 S-3.1／S-3.3 輸出一致。

## Out of Scope
- B 重編號整份 Stage 7 清單。
- C／AS-2 只改文件、不加填檔牙。
- AS-3 改整合腳本演算法(自動把 `ALREADY_SYNCED` 當 FAIL,或腳本自己重綁／動樹)。
- T-hist 改寫 `notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/` 當時句。
- `#196`、gate-twin Backlog、diagram-ir-gate。
- 九條制度缺口(A-1～B-2)實作。
- Windows 真機驗證。
- 本 hop／本 feat 實作 hop bump plugin。
- 本 hop 落地守衛碼(Stage 4 只釘契約;碼在 Stage 6)。
- 本 hop 開 Stage 5+ 檔、代填 G2／G3 PASS。
- feature branch 跑 `status-update.sh` 改正本 Active 列(OC-3)。
- 解凍並改 Stage 1–4 模板正文(除本檔自己)。
- 另造 `check-as1-*.sh` 第二套整合工具家族。

## Diff Budget

本節是**估計**(給後續 Stage 6,不是本規格 PR 的檔數)。超支本身非偏差,是停下判 L1/L2 的訊號。本規格 PR 只動本目錄 `4-spec.md` 與 twin／審頁 html。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| `check-stage67` ST 填檔射程 + fixture 五份 | ≤3 | ≤180 | ≤260 |
| GUIDANCE 正本＋散發副本恢復句 | ≤2 | ≤40 | ≤40 |
| example 7-review／4-spec／html 編號 | ≤4 | ≤40 | 0 |
| `manifests/p4-gauntlet-gates.md` | ≤1 | ≤10 | 0 |
| 腳本檔頭兩份 | ≤2 | ≤20 | 0 |
| `spec-gate-dd-subsection` fixture 同步 | ≤1 | ≤10 | ≤20 |
| **合計** | **≤13** | **≤300** | **≤320** |

[Assumption] 係數按「一個 S 一到兩條測試」,未加 mutation。html 重生列進 example 檔數。

## Dependencies
- `scripts/check-stage67-enforcement.sh` ST 組 —— justification:OC-1 沿用既有檢查家族,填檔牙是射程延伸。
- `scripts/check-integration-regression-guard.sh` —— justification:檔頭／副本 parity 與「不重寫演算法」回歸。
- `scripts/test-evidence-gauntlet.sh` —— justification:SC-4 模板恢復路徑牙不得回潮。
- `scripts/devflow-integration-regression.sh` 與 `docs/dev/tools/` 散發副本 —— justification:GUIDANCE 與檔頭是活教師／恢復句落點;parity 已有牙。
- `example/contract-expiry-reminder/`、`manifests/p4-gauntlet-gates.md` —— justification:T-now 活教師清單。
- 無新外部服務、無新 pip 套件、無 schema migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組(ST 填檔牙／整合腳本 GUIDANCE／example／manifest);②公開檢查 exit 契約(`check-stage67` 對填檔由綠變可紅);⑩三個以上模組共同參與;⑪ ALREADY_SYNCED 恢復二選一(錯誤恢復)
- Design source: 既有 pattern —— `check-stage67` ST、整合腳本只算只判、7-review 2c／2d 散文;填檔結論形狀來自 Stage 3 throwaway(已 ACCEPTED)

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| `check-stage67-enforcement.sh` ST | 模板序牙 + 填檔牙;exit ≠ 0 擋 void-only | **擁有**填檔紅／綠判定 | → 填好的 7-review 字串、→ 模板 | 不得改整合腳本演算法;不得新開第二套 check 家族 |
| 整合腳本正本／散發副本 | 只算只判;GUIDANCE 印恢復下一步 | **擁有** STATUS／三 SHA／REF 輸出 | → git fetch／rev-parse | 不得 merge／rebase／寫工作樹;不得自動 FAIL 或自動重綁 |
| 活教師(example／manifest／檔頭) | 教 2c 整合 → 2d Fresh | 不擁有牙 | → 模板編號 | 不得改 HISTORY／dispatch;不得重編號 2c 整合段 |
| 本 slug 7-review | 真跑 1→7 後綁 Source SHA | **擁有**本 feat 的 Source SHA 字 | → gauntlet／git | 不得在 Verdict 後改碼;不得 Exit 才合 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| ST 填檔牙 | in:宣稱 2c／送 G3 且含 `ALREADY_SYNCED` 的 7-review;out:exit 0／≠ 0 | void-only → ≠ 0;n-a／draft → 0 | 只讀填檔,不改該 7-review | 既有模板 ST 字面檢查仍綠;只加填檔射程 |
| 整合腳本 stdout | in:`--integration` + `--fork-sha`;out:STATUS + 三 SHA + GUIDANCE | `ALREADY_SYNCED` 仍 exit 2 | 腳本不動樹;GUIDANCE 與 exit 同一次印出 | exit 0／10／11／2 對照不變;只改 GUIDANCE 字 |
| 活教師改口 | in:舊 2c Fresh／檔頭句;out:2d／新檔頭 | 漏改 fixture → S-2.5 紅 | example 與 fixture 同一 T | 2c 整合段標題不變 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| ST 填檔掃描 | 認宣稱 + `ALREADY_SYNCED` + 恢復二選一 | ← 7-review 字串 | 讀檔 → 判紅綠 | void-only ≠ 0 | S-1.1～S-1.5 fixture |
| GUIDANCE 字串 | 告訴人重綁或 FAIL | ← STATUS=`ALREADY_SYNCED` | 只印 | 不改 exit | S-1.6 `rg` |
| 教師改口 | 2c Fresh／檔頭句歸零 | ← T-now 路徑清單 | 編輯文字 | 漏路徑 → S-2.4 紅 | S-2.1～S-2.5 `rg` |

### Design Constraints
- 必須:沿用 `check-stage67` 家族;填檔牙只在宣稱 2c／送 G3 時發動;SHA ≥7 hex 或「本項 FAIL」;活教師聯合 needle 歸零;模板 2c→2d 仍綠。
- 禁止:第二套整合工具;重編號;重寫演算法;改 HISTORY／dispatch;本 hop 代填 G2 PASS;feature branch 改正本 STATUS 表列;碰 `#196`／diagram-ir-gate。
- Extension point:後續若要重編號 2c,必須回 2-decision 推翻 B。
- Known design limit:
  ① 填檔牙讀字串形狀,不驗證 SHA 真的等於當時 HEAD(那是 S-4.1 本 slug 真跑時對)。
  ② 誰都仍可跳過 2c;本輪牙在「宣稱已勾／送 G3」之後發動,不在編輯器層擋跳步。
  ③ Stage 3 throwaway 不進 Git;正式碼以本檔 R/S 為準。

## Verification Profile(G2 一併審)
- lane: full(判準:新能力、改公開檢查 exit 契約、跨模組教師／牙;owner 已 lock full。無偏離)
- Risk: high(判準:公開 API／不可逆 —— `check-stage67` 對填檔由「不咬」改「可紅」;假綠會讓未審樹出貨。不是金流／auth,但模板「公開 API／不可逆改動」吃這條)
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得只靠「證據不算數／輸出不算數」讓已宣稱的 `ALREADY_SYNCED` 過關(S-1.1)
  - 不得誤殺 `N_A_NO_INCOMING` 或未宣稱 draft(S-1.4／S-1.5)
  - 不得重編號 2c 整合段、不得重寫整合腳本演算法(S-3.3)
  - 不得改 HISTORY／dispatch／stage7-loop 當時句(OC-2;Out of Scope)
  - 不得新開第二套整合檢查家族(OC-1)
  - 不得在本 slug SOP 宣告跳過 2c 或 Exit 才合併(S-4.3)
  - 不得本 hop 代填 G2 PASS、不得 bump plugin、不得改正本 STATUS 表列
- Required layers:check-spec-gate／check-stage67-enforcement／check-integration-regression-guard／test-evidence-gauntlet
- Conditional layers:Supply chain — 本 feat 實作若改 pin／requirements 才重跑;本契約不改 pin
- Explicitly excluded layers:Mutation(本 hop 只規格;方法包未把 mutation 列為本 feat 必跑)、e2e／Playwright(無產品前端)、Race／stress(填檔牙是同步讀檔,無新併發契約)、Windows 真機(Out of Scope)
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/integration-before-verdict/4-spec.md && bash scripts/check-stage67-enforcement.sh && bash scripts/check-integration-regression-guard.sh && bash scripts/test-evidence-gauntlet.sh`
- Reliability triage:
  - Concurrency: n-a — 指定檢查同步讀一份 7-review;無多 writer 契約
  - Idempotency: applicable — 同一份 fixture 再跑指定檢查,exit 必須與第一次相同(S-1.1～S-1.5)
  - Timeout/retry: n-a — 本機檔案、無外呼;紅了由人改 7-review 再跑,不自動重試

Human verdict: ACCEPTED

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| void-only 仍綠 | G-out-2 假過,核准樹可漂 | 指定檢查對 void-only fixture exit 0 | Required:S-1.1 | — |
| n-a／draft 被預先紅 | 合法 n-a 與未勾草稿做不下去 | na-incoming／draft-unclaimed exit ≠ 0 | Required:S-1.4／S-1.5 | — |
| 短於 7 hex 當重綁 | 假 SHA 混過 | `Source SHA: abc` 仍 exit 0 | Required:S-1.2(≥7 hex) | — |
| GUIDANCE 仍只說不算數 | 人不知道下一步 | GUIDANCE 無重綁／FAIL 詞 | Required:S-1.6 | — |
| example／manifest／檔頭仍教 2c=Fresh | 採用者抄舊序 | SC-3 `rg` 仍有命中 | Required:S-2.1～S-2.4 | — |
| 只改 example 漏 fixture | 衍生教師繼續教舊號 | fixture 仍寫 2c gauntlet | Required:S-2.5 | — |
| 重編號拆掉 2c 錨 | 既有牙假綠或全紅 | `2c.**整合回歸**` 抓不到 | Required:S-3.3 | — |
| 改演算法讓腳本動樹 | 違反只算只判 | 腳本出現 merge／寫檔 | Required:S-3.3 | — |
| Verdict 後才合仍當 shipped | 核准≠出貨 | Exit 後 Source SHA ≠ HEAD | Required:S-4.1／S-4.2 | — |
| 人跳過 2c 且不宣稱 | 牙不發動 | 未勾 draft 仍 exit 0 | Known limit ②;S-1.5 明示 no-fire | 不在編輯器層擋跳步 |

## Drafting Decisions(草擬自判,送 G2 人審)

形狀已寫進 R/S。本表只記 Stage 2／3 留給本檔綁定的選擇。不翻 Decision。狀態留待人審;Agent 不打 ✅、不代填 G2。

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 指定檢查 = `scripts/check-stage67-enforcement.sh` 的 ST 組射程延伸。不新開 `check-as1-*.sh` | OC-1 沿用既有家族;ST 已咬模板恢復句,缺的是填檔 | `2-decision.md` OC-1; `scripts/check-stage67-enforcement.sh:298-322` | 若改獨立腳本,要重審第二方法論與 SC-2 觀測點 | 待人審 |
| DD-2 | 填檔結論塊欄位:`STATUS`、`FORK`／`HEAD`／`INTEGRATION`／`REF`、恢復二選一「重綁 Final Fresh。Source SHA: <hex≥7>」或「本項 FAIL」 | Stage 3 Demo 已 ACCEPTED 此形;Decision 只鎖「有重綁 SHA 或明示 FAIL」 | `3-prototype.md:49-59`; `2-decision.md` Decision 第(1)點 | 改欄名則 S-1.1～S-1.3 fixture 全改 | 待人審 |
| DD-3 | 發動條件:正文有 `ALREADY_SYNCED`,且出現下列任一宣稱 —— 已勾(`[x]`)整合項、`結論:STATUS=ALREADY_SYNCED`、`verdict: PASS`、`status: approved`。n-a 與未宣稱 draft 不發動 | 避免誤殺;與 Stage 3 Method 發動句同一把尺 | `3-prototype.md:59`; `2-decision.md` Risks 誤殺列 | 改成「檔內有字就紅」會打破 S-1.4／S-1.5 | 待人審 |
| DD-4 | 活教師路徑 = example 7-review／4-spec(含 html)、`manifests/p4-gauntlet-gates.md`、整合腳本與散發副本檔頭。改口規則:Fresh／gauntlet 的 2c→2d;2c 仍叫整合回歸 | T-now 清單;B 重編號已拒 | `2-decision.md` 既有脈絡表; `3-prototype.md:145-150` | 少一條路徑則 S-2.4 聯合 `rg` 仍會紅 | 待人審 |
| DD-5 | GUIDANCE 正本與散發副本同一句補恢復詞;exit 對照與只算只判不變 | G-out-2 要可執行下一步;AS-3 已拒改演算法 | `2-decision.md` Rationale GUIDANCE 弱句;腳本 `:204-205` | 若連 exit 2 都改,S-3.3 與 guard 要重寫 | 待人審 |
| DD-6 | `scripts/fixtures/spec-gate-dd-subsection/` 與 example 4-spec 同一 T 改 gauntlet 編號 | Decision 已點名這份抄本;不同步 = 衍生教師 | `2-decision.md` Risks fixture 列 | 漏改則 S-2.5 紅 | 待人審 |
| DD-7 | Q6 錨句只鎖兩句:「整合回歸在 Final Fresh 之前」「ALREADY_SYNCED 不得只寫證據不算數」。不重寫已對的 2c 散文 | Decision Scope Q6;散文已搬 | `2-decision.md` Scope;內部技術選擇 Q6 候選 | 多鎖舊錨會逼重編號 | 待人審 |
| DD-8 | Feature Risk = high;本檔 `verdict` 空、`status` draft,G2 由人類填 | 公開檢查契約 + 假綠出貨;任務禁止假 G2 PASS | `_templates/4-spec.md` Risk 判準;本 hop brief | 改 normal 則 Failure Model 可改選配 | 待人審 |

### 內部技術選擇(下層,告知即可)
- fixture 目錄名 `scripts/fixtures/as1-filled-tooth/`;五檔對齊 Stage 3:`void-only`／`rebind-sha`／`item-fail`／`na-incoming`／`draft-unclaimed`。
- 重綁樣張 SHA 用 Stage 3 已跑過的 `def4567890abc`(≥7 hex)。
- 審頁 html 用 `scripts/build-stage4-html.py --action`;G2 twin 用 `scripts/build-gate-twin.py`(或 `docs/dev/tools/build-gate-twin.py`)。不手包 html-shell。
- 本 hop 不改 `_templates/7-review.md` 正文。
- 本 feature branch 不跑 `status-update.sh` 改正本表列(OC-3)。

## Test Skeletons(選配)
- `test_s_1_1_void_only_already_synced_fails`
- `test_s_1_2_rebind_source_sha_passes`
- `test_s_1_3_item_fail_passes`
- `test_s_1_4_na_no_incoming_no_fire`
- `test_s_1_5_draft_unclaimed_no_fire`
- `test_s_1_6_guidance_has_rebind_or_fail`
- `test_s_2_1_example_2c_fresh_needle_zero`
- `test_s_2_2_manifest_2c_gauntlet_needle_zero`
- `test_s_2_3_script_header_not_exit_checklist_tool`
- `test_s_2_4_live_path_joint_rg_zero`
- `test_s_2_5_spec_gate_fixture_tracks_example`
- `test_s_3_1_template_integrate_before_fresh`
- `test_s_3_2_existing_template_teeth_still_green`
- `test_s_3_3_no_renumber_no_algorithm_rewrite`
- `test_s_4_1_slug_exit_source_sha_equals_head`
- `test_s_4_2_contrast_verdict_then_merge_differs`
- `test_s_4_3_no_skip_2c_or_exit_merge_sop`

## Stage 3 對帳

Stage 3 Human verdict: ACCEPTED。Verdict attestation: human:rick @ 2026-09-12(`3-prototype.md`)。CLI Demo,無 UI Variant。逐場下落:

| Demo 場景 | 下落 |
|---|---|
| AC-2 void-only 必須紅 | S-1.1 |
| AC-2 重綁 SHA 或本項 FAIL | S-1.2、S-1.3 |
| AC-2 n-a／draft 不預先紅 | S-1.4、S-1.5 |
| AC-3 意圖序 + 活教師改口 | S-2.1～S-2.4、S-3.1;正本改口留 Stage 6(Out of Scope:本 hop 改碼) |
| AC-1 出貨樹=核准樹(對照敘事) | S-4.1、S-4.2;本站只展示序,真跑在後續 Stage 7 |
| Method 走查:結論塊 STATUS + 三 SHA／REF + 恢復二選一 | DD-2;S-1.2／S-1.3 觀測 |
| Method 走查:發動=宣稱 2c／送 G3 | DD-3;S-1.4／S-1.5 |
| Method 走查:正式牙進 `check-stage67` 家族 | DD-1;R-1 |
| Operational Context Recovery(void-only 紅了補 SHA 或 FAIL) | S-1.1 Recovery |
| 結構圖 2c→2d→Verdict→Exit 文件 | S-3.1、S-4.3 |

## 確認紀錄
- 雙源清點 | 2026-09-12 | 驗收雛形 AC-1／AC-2／AC-3 共 3 條;living spec `docs/specs/` 0 條可引 → 行為升 ADDED R-1～R-4;活路徑原句列 MODIFIED 表。1-discussion 雛形觀測欄已升進對應 S
- R 範圍 | 2026-09-12 | IMPLEMENTER B brief + 已核 Decision:tip 已 2c→2d Fresh;剩餘 AS-1 填檔牙 + 活教師掃蕩 + 本 slug SHA 對帳。本 hop 雲端一次落檔,對應該鎖板
- S 展開 | 2026-09-12 | R-1～R-4 全展開;每 S 有觀測欄;重要 S 有 Operational Context
- 3a 四節 | 2026-09-12 | AC／Out of Scope／Diff Budget／Dependencies 齊
- 3b Profile | 2026-09-12 | lane full、Risk high、Failure Model、Reliability triage、Design Boundary applicable
- 3c Stage 3 | 2026-09-12 | 五個 ACCEPTED Demo 場景 + Method 走查 + Recovery 皆有 R/S 或 Out of Scope 下落
- DD 掃描 | 2026-09-12 | 上層八條送 G2 人審;DD 節無未決標籤;不翻 Decision
- G2 verdict | 2026-09-12 | **留空**。Agent 不代填 PASS。審查者依序:適格人類 reviewer → fresh-context reviewer Agent → owner 自審(有記錄的最後手段)
- html | 2026-09-12 | `build-gate-twin.py` 解析 17 條 S、13 節背景;審頁 `build-stage4-html.py --action` 寫 `4-spec.html`(與本 slug Stage 2／3 審頁同一家族)。不手包 html-shell
