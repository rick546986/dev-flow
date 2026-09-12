---
feature: integration-before-verdict
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-12
---

# 4. 規格 — 整合須在 Fresh／Verdict 之前(change spec)

> 基準:`main` tip `1f8d992`(#211 Stage 3 Human ACCEPTED)。G1 PASS(#207)。契約不 bump。
> Decision 正本:`docs/dev/integration-before-verdict/2-decision.md`(A + AS-1 + T-now;OC-1～OC-3 ✅)。
> tip 模板／指南／Stage 7 節點鏈**已經**是 2c 整合 → 2d Fresh。本檔只把剩餘交付釘成可測 R/S:
> (1) AS-1 填檔牙 (2) 活教師掃蕩 (3) 本 slug 後續真跑 1→7。
> 本 hop **只寫規格**,不落地守衛碼、不改 example／manifest／腳本正本、不開 Stage 5+、
> 不碰 `#196`／diagram-ir-gate、不發版、不改 `STATUS.md` 表列(OC-3)。
> **G2 `verdict:` 留空**,由人類填;Agent 不代填 PASS。

## 補助模組生命週期（預覽）

主詞:Stage 7 填檔牙與活教師。有關聯的收成一格。
- 新生（這輪沒有）：不加第二套整合工具。
- 改行為（相關一格）：`check-stage67` ST 射程延伸到填好的 7-review;活教師改口。
- 退役：沒有。
- 不動：2c／2d 編號、整合腳本演算法、HISTORY／dispatch、`#196`、Stage 1–4 模板、plugin 版號。

## ADDED Requirements

### R-1: 系統 SHALL 把填好的 7-review 的 ALREADY_SYNCED 鎖成重綁 Source SHA 或本項 FAIL
沿用既有檢查家族(`scripts/check-stage67-enforcement.sh` ST 組;OC-1)。不另造第二套整合工具。
不重寫 `devflow-integration-regression.sh` 的 STATUS 演算法(只算只判、exit 碼不變)。
牙只在**宣稱** 2c 已勾／送 G3、且正文有 `ALREADY_SYNCED` 時發動。

**審的時候看什麼**
指定檢查對五份填檔 fixture 的 exit:void-only ≠ 0;重綁 SHA／本項 FAIL／n-a／draft = 0。

#### S-1.1 只寫作廢必須紅
- GIVEN 一份 7-review fixture,同時滿足:(a) frontmatter `verdict: PASS` 或 `status: approved`,或清單有 `[x]` 且同行含 `整合回歸`;(b) 正文含字串 `ALREADY_SYNCED`;(c) 正文含 `證據不算數` 或 `輸出不算數`;(d) 全文沒有 `重綁 Final Fresh。Source SHA:` 後接 ≥7 個 `[0-9a-fA-F]`;(e) 全文沒有字串 `本項 FAIL`
- WHEN 跑 `bash scripts/check-stage67-enforcement.sh` 的填檔牙(ST 組延伸;入口仍是這一支,可加 fixture 路徑引數)
- THEN exit ≠ 0;stderr 或 stdout 含 `void-only` 或同等「只寫作廢」標記,且不含「已過整合」
- 觀測:從該指令 exit 與輸出看 | exit ≠ 0 且含指定標記算過 | 用 `scripts/fixtures/as1-filled-tooth/void-only.md`(形同 Stage 3 `fx/void-only.md`)測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:勾 2c 時不能靠「證據不算數」過關
  - Situation:`ALREADY_SYNCED`(已合過、merge-base 被污染)
  - Known information:腳本印了 `ALREADY_SYNCED`;模板散文已有恢復二選一
  - Missing information:本份填檔有沒有重綁 SHA 或本項 FAIL
  - Human decision:補重綁 SHA,或改寫本項 FAIL;不要進 Verdict
  - Authority:牙 exit ≠ 0 擋勾過;人改 7-review
  - External dependency:整合腳本只算只判
  - Out-of-system action:在編輯器改恢復欄,或從乾淨座標重算
  - Waiting/timeout behavior:牙同步結束;無自動重試
  - Recovery:補 `重綁 Final Fresh。Source SHA: <hex≥7>` 或改寫 `本項 FAIL` 後重跑同一支檢查
  - Audit/handoff requirement:紅輸出可指回 void-only;不得暗示「寫了作廢就能過」
  - Observation:見本條觀測

#### S-1.2 重綁 Source SHA 必須綠
- GIVEN 一份 7-review fixture,宣稱同 S-1.1(a)(b),且有一行字面 `重綁 Final Fresh。Source SHA: def4567890abc`(≥7 hex),沒有只靠 `證據不算數`／`輸出不算數` 當唯一恢復
- WHEN 跑與 S-1.1 同一支填檔牙
- THEN exit 0;輸出含 `rebind-sha:def4567890abc` 或同等「已重綁」標記與該 hex
- 觀測:從 exit 與輸出看 | exit 0 且能讀回 `def4567890abc` 算過 | 用 `scripts/fixtures/as1-filled-tooth/rebind-sha.md` 測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:恢復路徑之一=重綁後進 2d
  - Situation:已合過;`ALREADY_SYNCED`
  - Known information:當下 `git rev-parse HEAD`
  - Missing information:無(SHA 寫在恢復欄)
  - Human decision:採用重綁,不用本項 FAIL
  - Authority:人填 SHA;牙只驗形狀
  - External dependency:git HEAD
  - Out-of-system action:下一步跑 2d Final Fresh,Source SHA 必須等於當時 HEAD
  - Waiting/timeout behavior:同步
  - Recovery:SHA 少於 7 hex → 當 void-only 紅,補滿再跑
  - Audit/handoff requirement:恢復欄的 hex 可對 `git rev-parse HEAD`
  - Observation:見本條觀測

#### S-1.3 本項 FAIL 必須綠
- GIVEN 一份 7-review fixture,宣稱同 S-1.1(a)(b),且正文含字面 `本項 FAIL`,沒有重綁 SHA
- WHEN 跑與 S-1.1 同一支填檔牙
- THEN exit 0;輸出含 `item-FAIL` 或同等「本項停止」標記;不得把整份 G3 標成已過
- 觀測:從 exit 與輸出看 | exit 0 且含本項停止標記、不含 G3 PASS 暗示算過 | 用 `scripts/fixtures/as1-filled-tooth/item-fail.md` 測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:恢復路徑之二=這一步停
  - Situation:不願用污染後的交集證據
  - Known information:`ALREADY_SYNCED`
  - Missing information:乾淨分岔座標
  - Human decision:選 FAIL,不重綁
  - Authority:人寫 `本項 FAIL`;牙放行形狀
  - External dependency:無
  - Out-of-system action:從乾淨座標重算整合;不要進 Verdict
  - Waiting/timeout behavior:同步
  - Recovery:寫成別的 FAIL 同義詞(例如只寫 `FAIL` 無「本項」)→ 牙當未恢復,走 S-1.1 紅
  - Audit/handoff requirement:FAIL 是「這一步停」,不是整份 G3 默默過
  - Observation:見本條觀測

#### S-1.4 n-a 不預先紅
- GIVEN 一份 7-review fixture,結論 `STATUS: N_A_NO_INCOMING`(或正文含 `N_A_NO_INCOMING`),沒有 `ALREADY_SYNCED`
- WHEN 跑與 S-1.1 同一支填檔牙
- THEN exit 0;輸出含 `no-fire:N_A_NO_INCOMING`
- 觀測:從 exit 與輸出看 | exit 0 且含指定 no-fire 標記算過 | 用 `scripts/fixtures/as1-filled-tooth/na-incoming.md` 測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:對方零新 commit 時直接進 2d
  - Situation:`N_A_NO_INCOMING`
  - Known information:腳本 exit 0、無合併
  - Missing information:無
  - Human decision:記 n-a,進 2d
  - Authority:牙不發動
  - External dependency:整合腳本
  - Out-of-system action:進 2d Fresh
  - Waiting/timeout behavior:無
  - Recovery:不適用 — 無合併、無恢復欄
  - Audit/handoff requirement:n-a 與 ALREADY_SYNCED 可區分
  - Observation:見本條觀測

#### S-1.5 未勾 draft 不預先紅
- GIVEN 一份 7-review fixture,frontmatter `status: draft` 且 `verdict:` 空白或非 `PASS`;清單 2c／整合回歸未勾(`[ ]`);正文可出現 `ALREADY_SYNCED` 或 `證據不算數` 字樣
- WHEN 跑與 S-1.1 同一支填檔牙
- THEN exit 0;輸出含 `no-fire:draft-or-unclaimed`;不得把草稿當成已送 G3
- 觀測:從 exit 與輸出看 | exit 0 且含 draft no-fire 標記算過 | 用 `scripts/fixtures/as1-filled-tooth/draft-unclaimed.md` 測
- Operational Context:
  - Actor:Stage 7 reviewer
  - Goal:還沒勾 2c 的草稿不被提前紅擋住
  - Situation:7-review 仍 draft
  - Known information:未宣稱送 G3
  - Missing information:最終 STATUS
  - Human decision:繼續填,不要被誤殺
  - Authority:牙不發動
  - External dependency:無
  - Out-of-system action:填完再勾
  - Waiting/timeout behavior:無
  - Recovery:一旦勾了 2c 或 `verdict: PASS` 且仍只寫作廢 → 改走 S-1.1
  - Audit/handoff requirement:未勾 ≠ 已送 G3
  - Observation:見本條觀測

#### S-1.6 結論塊欄位名與宣稱條件
- GIVEN 填檔結論塊使用下列鍵(可折行,鍵名字面必須在):`STATUS`、`FORK`、`HEAD`、`INTEGRATION`、`REF`、`恢復`
- WHEN 讀一份宣稱 2c 已勾的 7-review
- THEN 結論塊標題為 `## 2c 整合結論`(2c 仍叫整合回歸,不重編號);`STATUS` 值為腳本印出的四者之一(`N_A_NO_INCOMING`／`SYNC_REQUIRED_NO_OVERLAP`／`SYNC_REQUIRED_WITH_OVERLAP`／`ALREADY_SYNCED`);`FORK`／`HEAD`／`INTEGRATION` 各為腳本三 SHA;`REF` 為 canonical ref;當 `STATUS` 為 `ALREADY_SYNCED` 時,`恢復` 必須是 `重綁 Final Fresh。Source SHA: <hex≥7>` 或 `本項 FAIL`。宣稱=下列任一:清單 `[x]` 同行含 `整合回歸`;或一行含 `STATUS: ALREADY_SYNCED` 或 `結論:STATUS=ALREADY_SYNCED`;或 frontmatter `verdict: PASS` 且正文有 `ALREADY_SYNCED`;或 frontmatter `status: approved` 且正文有 `ALREADY_SYNCED`
- 觀測:從 fixture 結論塊鍵名與宣稱條件看 | 鍵齊且 ALREADY_SYNCED 時恢復二選一算過 | 用 S-1.1～S-1.5 五份 fixture 對帳鍵名;缺鍵的 ALREADY_SYNCED 宣稱案走 S-1.1 紅
- Operational Context:不適用 — 欄位形狀,無新的人員交接(交接已在 S-1.1～S-1.3)。

#### S-1.7 沿用 check-stage67 家族、不另造入口
- GIVEN 本 feat 實作 hop 的 diff 與 `scripts/check-stage67-enforcement.sh`
- WHEN 列出新增檢查入口
- THEN 填檔牙掛在該檔 ST 組(或該檔呼叫的同一家族函式);不得新增 `scripts/check-already-synced-*.sh` 或第二套整合工具;既有模板字串牙(ST:整合在 Fresh 前、恢復路徑散文、Exit 禁改碼)仍綠
- 觀測:從 `git diff --name-only` 與 `bash scripts/check-stage67-enforcement.sh` 看 | 無第二套入口檔、既有 ST 仍 exit 0 算過 | 實作 hop 對本 repo 跑該腳本(SC-4)
- Operational Context:不適用 — 檢查家族邊界,無人員交接。

### R-2: 系統 SHALL 一次掃完仍在教舊序的活教師
T-now:採用者抄 example／manifest／腳本檔頭會看到的句子,不得再把 2c 寫成 Final Fresh／gauntlet,也不得把整合工具寫成 Exit Checklist 程序。歷史派工與 HISTORY 不改(OC-2)。

**審的時候看什麼**
指定 `rg` 在活路徑零命中;改口後 2c 仍叫整合回歸。

#### S-2.1 example 7-review 不再把 2c 當 Fresh
- GIVEN `example/contract-expiry-reminder/7-review.md`(及其 html twin,同一 T 重生)
- WHEN `rg -n '執行清單 2c 的 Final Fresh' example/contract-expiry-reminder/7-review.md example/contract-expiry-reminder/7-review.html`
- THEN 零命中;該檔改口後把 Final Fresh Run 指到執行清單 **2d**(字面含 `2d` 與 `Final Fresh`);不得把 2c 改成別的步名來消滅「2c = 整合回歸」
- 觀測:從 rg exit 與改口句看 | rg 無列、2d+Final Fresh 同在、2c 仍可當整合回歸算過 | 拿現檔 needle(Stage 3 計 1 條)當負向對照,改口後重跑
- Operational Context:
  - Actor:採用者／owner
  - Goal:抄範例時不要走舊編號
  - Situation:第一條真實 full lane 期間
  - Known information:模板 2c 已是整合
  - Missing information:範例是否已改口
  - Human decision:採用者跟範例走
  - Authority:本 feat Stage 6 改 example
  - External dependency:無
  - Out-of-system action:抄範例進自己的 7-review
  - Waiting/timeout behavior:無
  - Recovery:漏改 html twin → 同一 T 紅,重生 twin
  - Audit/handoff requirement:md 與 html 同一 needle
  - Observation:見本條觀測

#### S-2.2 example 4-spec 不再把 2c 當 gauntlet
- GIVEN `example/contract-expiry-reminder/4-spec.md`
- WHEN `rg -n '執行清單 2c gauntlet' example/contract-expiry-reminder/4-spec.md`
- THEN 零命中;改口把 gauntlet 命令指到執行清單 **2d**(字面含 `2d` 與 `gauntlet`)
- 觀測:從 rg 與改口句看 | 零命中且 2d+gauntlet 同在算過 | 拿現檔 `example/contract-expiry-reminder/4-spec.md:223` 當負向對照
- Operational Context:不適用 — 範例編號改口,無人員交接(採用者抄寫已在 S-2.1)。

#### S-2.3 gauntlet manifest 不再把 2c 當文檔化命令
- GIVEN `manifests/p4-gauntlet-gates.md`
- WHEN `rg -n '執行清單 2c 的文檔化命令' manifests/p4-gauntlet-gates.md`
- THEN 零命中;改口把該句的步號改成 **2d**(字面含 `2d` 與 `文檔化命令` 或同等 gauntlet 命令句)
- 觀測:從 rg 與改口句看 | 零命中算過 | 拿現檔 `manifests/p4-gauntlet-gates.md:52` 當負向對照
- Operational Context:不適用 — manifest 改口。

#### S-2.4 整合腳本與散發檔頭不再自稱 Exit Checklist 工具
- GIVEN `scripts/devflow-integration-regression.sh` 與 `docs/dev/tools/devflow-integration-regression.sh`(兩份檔頭必須同一句)
- WHEN `rg -n 'Exit Checklist.*整合回歸.*計算工具' scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh`
- THEN 零命中;檔頭改口含「步 2c 整合回歸」與「Fresh 之前」與「不是 Exit 程序」(三個子字串都要在);STATUS 演算法與 exit 碼(0／10／11／2)不變
- 觀測:從 rg 與檔頭句、腳本 exit 契約看 | 零命中、三子字串在、`scripts/check-integration-regression-guard.sh` 仍 exit 0 算過 | 拿現檔第 2 行當負向對照
- Operational Context:
  - Actor:採用者讀腳本檔頭
  - Goal:不要把整合工具當 Exit 才跑的程序
  - Situation:複製散發副本
  - Known information:腳本只算只判
  - Missing information:何時跑
  - Human decision:在 2c 跑,不在 Exit 跑
  - Authority:檔頭句子;牙不改演算法
  - External dependency:無
  - Out-of-system action:在 2c 呼叫腳本
  - Waiting/timeout behavior:無
  - Recovery:正本改了散發沒改 → parity 牙紅
  - Audit/handoff requirement:兩路徑檔頭同一句
  - Observation:見本條觀測

#### S-2.5 活路徑聯合 needle 歸零
- GIVEN 活路徑集合:`example/contract-expiry-reminder/`(含 md／html)、`manifests/p4-gauntlet-gates.md`、`scripts/devflow-integration-regression.sh`、`docs/dev/tools/devflow-integration-regression.sh`
- WHEN `rg -n '執行清單 2c 的 Final Fresh|Exit Checklist.*整合回歸.*計算工具' <上列活路徑>`
- THEN 零命中(SC-3)。`notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/` 即使仍有舊序句也不在本命令範圍、本 feat 不得改那些檔
- 觀測:從 rg 對活路徑的 exit／列數看 | 活路徑 0 列;對 HISTORY／dispatch 的 `git diff --name-only` 不含那些路徑算過 | 與 Stage 3 現檔 TEACHER_COUNT=5 對照
- Operational Context:不適用 — 聯合掃描。

#### S-2.6 衍生 fixture 與正本 example 同步
- GIVEN `scripts/fixtures/spec-gate-dd-subsection/`(或任何抄了 example 4-spec「2c gauntlet」句的 fixture)
- WHEN 改 `example/contract-expiry-reminder/4-spec.md` 的步號
- THEN 同一 T 內衍生 fixture 一併改到 2d;若 fixture 仍留 `執行清單 2c gauntlet` 則該 T 的 Verify 紅
- 觀測:從 fixture 內文與 example 對看 | 兩處步號相同、舊 needle 不在 fixture 算過 | 改 example 時 `rg -n '執行清單 2c gauntlet' scripts/fixtures/`
- Operational Context:不適用 — fixture 同步。

### R-3: 系統 SHALL 維持 tip 已綠的 2c 整合在 2d Fresh 之前
承認散文與模板順序牙已搬。本 slug 不重編號、不重寫整合腳本演算法。Q6 錨句只鎖兩句,不重寫已對的 2c 散文。

**審的時候看什麼**
既有三支順序／恢復牙仍綠;`_templates/7-review.md` 仍是 2c 整合 → 2d Fresh。

#### S-3.1 模板頂註順序不變
- GIVEN `_templates/7-review.md` 頂註執行清單
- WHEN 找字串 `整合回歸` 與 `Final Fresh Run` 的首次出現位置
- THEN `整合回歸` 的位元偏移小於 `Final Fresh Run`;步驟標號仍是 `2c` 整合、`2d` Fresh;Exit Checklist 正文不含「合併它印的」
- 觀測:從該檔頂註與 Exit 節看 | 兩字串順序與標號仍在、Exit 無合併句算過 | `bash scripts/check-stage67-enforcement.sh`(既有 ST)
- Operational Context:不適用 — 模板回歸,無外部現象以外的人員交接。

#### S-3.2 三支既有牙仍綠
- GIVEN 本 feat 實作 hop 結束後的工作樹
- WHEN 分別跑 `bash scripts/check-stage67-enforcement.sh`、`bash scripts/check-integration-regression-guard.sh`、`bash scripts/test-evidence-gauntlet.sh`
- THEN 三支皆 exit 0;不得為了填檔牙而刪掉或改鬆既有「整合在 Fresh 前」模板字串項
- 觀測:從三支 exit 看 | 全 0 算過 | 實作 hop 終點跑三支(SC-4)
- Operational Context:不適用 — 回歸命令。

#### S-3.3 禁止重編號與改演算法
- GIVEN 本 feat 的 diff
- WHEN 列出對 `_templates/7-review.md` 步驟標號、`skills/dev-flow/stage7/nodes/S2c-integration.md`／`S2d-fresh.md` 檔名、`scripts/devflow-integration-regression.sh` 內 STATUS 分支與 exit 碼的改動
- THEN 不得把 `2c`／`2d` 標號對調或改成新 id;不得改 STATUS 名稱集合或 exit 0／10／11／2 的對應;GUIDANCE 字串與檔頭改口(S-2.4／S-5.1)除外
- 觀測:從 diff 看標號與 `GUIDANCE`／`sys.exit` 區塊 | 標號與 exit 對應未改算過 | `git diff` 對上列路徑
- Operational Context:不適用 — Non-Goal 守衛。

#### S-3.4 Q6 錨句只鎖兩句
- GIVEN `_templates/7-review.md` 與指南 renderer 已含整合在 Fresh 前的散文
- WHEN 本 feat 改 gate-consistency／renderer 錨
- THEN 只准新增或保持這兩句的機械咬合:「整合回歸在 Final Fresh 之前」「ALREADY_SYNCED 不得只寫證據不算數」(字面可拆進既有 ST／填檔牙輸出,但語意必須是這兩句);不得重寫已對的 `2c. **整合回歸**` 段正文來「再搬一次散文」
- 觀測:從新增錨的字面與 `_templates/7-review.md` 2c 段 diff 看 | 兩句可被既有或新 ST 找到;2c 段無重寫搬遷算過 | `git diff _templates/7-review.md` + ST 輸出
- Operational Context:不適用 — 錨句範圍。

### R-4: 本 slug SHALL 自己走完 1→7 並讓出貨樹等於核准樹
G-out-3／SC-1／SC-5:本 slug 是第一條真實 full lane 載體。本 hop 只交 Stage 4;後續 hop 交 5／6／7。本檔禁止寫「跳過 2c」或「Exit 才合併」的流程宣告。

**審的時候看什麼**
本 slug 的 7-review Source SHA 與 Exit 後 HEAD 逐字相同;對照樣本能指出兩 SHA 不同。

#### S-4.1 本 slug Exit 後兩 SHA 相同
- GIVEN 本 slug 已走到 Stage 7 且 Exit Checklist 已勾「整合回歸已在 Final Fresh 之前完成」
- WHEN 比對該份 `docs/dev/integration-before-verdict/7-review.md` 所記 Source SHA 與 `git rev-parse HEAD`
- THEN 兩個值逐字相同(允許 7 hex 前綴對完整 SHA 的 prefix 相符,但 7-review 寫下的字元必須是 HEAD 的前綴)
- 觀測:從 7-review Source SHA 欄與 `git rev-parse HEAD` 看 | 字元逐字為 HEAD 前綴算過 | 用本 slug 後續 Stage 7 產物測(AC-1／SC-1)。本 Stage 4 hop 尚無 7-review → 本條在 5／6／7 hop 才可實跑;本 hop 觀測標記為「契約已寫、產物未到」
- Operational Context:
  - Actor:owner／Stage 7 reviewer
  - Goal:Verdict 綁的樹就是出貨的樹
  - Situation:本 slug 真跑到 Exit
  - Known information:7-review Source SHA
  - Missing information:本 hop 尚無 7-review
  - Human decision:兩 SHA 不同就不得勾 Exit
  - Authority:owner 簽 G3
  - External dependency:git
  - Out-of-system action:比對 SHA
  - Waiting/timeout behavior:等 Stage 7 hop
  - Recovery:若 Exit 才合導致 HEAD 變了 → 作廢 G3,回 2c／2d
  - Audit/handoff requirement:7-review 留下 Source SHA
  - Observation:見本條觀測

#### S-4.2 對照樣本能指出兩 SHA 不同
- GIVEN 一份對照紀錄或 fixture:先寫 Verdict／Source SHA=`aaa1111`,再合併另一個 `INTEGRATION_SHA`,之後 HEAD=`bbb2222`
- WHEN 比對該紀錄的 Source SHA 與合併後 HEAD
- THEN 兩值不同;紀錄必須寫明「Verdict 後才合」;本 slug 正本 7-review 不得用這份對照當過關證據
- 觀測:從對照檔兩欄 SHA 看 | `aaa1111` ≠ `bbb2222` 且標了 Verdict 後才合算過 | 用 `scripts/fixtures/as1-filled-tooth/verdict-then-merge.md`(Stage 6 落地)測
- Operational Context:不適用 — 對照樣本,無現場交接。

#### S-4.3 本 slug 文件無舊序流程宣告
- GIVEN `docs/dev/integration-before-verdict/` 內 4-spec／後續 5-tasks／6-notes／7-review
- WHEN `rg -n '跳過 2c|Exit 才合|Exit 才合併' docs/dev/integration-before-verdict/`
- THEN 零命中於流程宣告句(引用舊序當反例並標「拒」或「對照」的句子除外;若引用必須同行或上一行含 `拒` 或 `對照`)
- 觀測:從 rg 列看 | 無未標反例的舊序宣告算過 | 對本資料夾跑該 rg(SC-5)
- Operational Context:不適用 — 文件掃描。

## MODIFIED Requirements

本 repo `docs/specs/` 無 living spec 條文可引。模板 `_templates/7-review.md` 2c／2d 散文已對,本 feat **不改其步驟標號與順序**(R-3)。唯一改口的活契約是整合腳本對人講的 GUIDANCE(演算法不變)。

### R-5: ALREADY_SYNCED GUIDANCE SHALL 寫出重綁或 FAIL 下一步
原文:`scripts/devflow-integration-regression.sh:204-205`(散發副本同句)

> `ALREADY_SYNCED`:「你已經同步過了,本次輸出不算數 —— 交集必須在動樹之前算,拿同步後的輸出當證據就是原本那個假綠」

改什麼:同一 STATUS 仍 exit 2;字串必須另外含 `重綁 Final Fresh` 或 `本項 FAIL`(至少一個,建議兩個都在),使人讀完知道下一步。不得只留「輸出不算數」而無恢復句。

#### S-5.1 GUIDANCE 含恢復下一步
- GIVEN `scripts/devflow-integration-regression.sh` 與 `docs/dev/tools/devflow-integration-regression.sh` 的 `GUIDANCE["ALREADY_SYNCED"]`
- WHEN 讀該字串
- THEN 含 `重綁 Final Fresh` 或 `本項 FAIL`;兩檔字串相同;STATUS=`ALREADY_SYNCED` 時腳本仍 exit 2
- 觀測:從兩檔 GUIDANCE 字串與 ALREADY_SYNCED 分支的 `sys.exit` 看 | 恢復子字串在、兩檔相同、exit 仍 2 算過 | 讀源碼 + `check-integration-regression-guard.sh`
- Operational Context:不適用 — 腳本文案,演算法不變。

## REMOVED Requirements

無。

## 行為流程圖(R 級)
```
[R-1] 填檔牙鎖成重綁或 FAIL
  宣稱 ALREADY_SYNCED 才發動
  void-only 紅;重綁／FAIL 綠
  n-a 與 draft 不預先紅
[R-2] 一次掃完活教師
  example／manifest／檔頭改口
  聯合 needle 歸零
[R-3] 維持 2c 整合在 2d Fresh 之前
  不重編號、不改演算法
  既有三支牙仍綠
[R-4] 本 slug 走完 1→7 出貨樹等於核准樹
  Source SHA 對 HEAD
  無跳過 2c 宣告
[R-5] GUIDANCE 寫出重綁或 FAIL 下一步
  exit 2 不變
```

## Acceptance Criteria

打包驗收(對 Decision SC-1..6 與討論 AC-1..3):

- 全 S 綠,且既有 `check-stage67-enforcement`／`check-integration-regression-guard`／`test-evidence-gauntlet` 回歸綠。
- SC-1／AC-1 ← S-4.1、S-4.2:本 slug Exit 後 Source SHA 為 HEAD 前綴;對照樣本兩 SHA 不同。
- SC-2／AC-2 ← S-1.1、S-1.2、S-1.3:void-only exit ≠ 0;重綁 SHA 或本項 FAIL exit 0。
- SC-2 誤殺防護 ← S-1.4、S-1.5:n-a 與 draft no-fire。
- SC-2 GUIDANCE ← S-5.1:ALREADY_SYNCED 文案含重綁或 FAIL;exit 仍 2。
- SC-3 ← S-2.1～S-2.5:指定 rg 在活路徑零命中。
- SC-4 ← S-3.1、S-3.2、S-1.7:模板仍 2c→2d;三支既有牙仍綠。
- SC-5 ← S-4.3:本 slug 無「跳過 2c」或「Exit 才合併」流程宣告。
- SC-6 ← Out of Scope:未改 `#196`、未實作九條制度缺口、未重寫整合腳本演算法、未 bump plugin。
- AC-3 ← S-3.1:整合步仍在 Fresh／Verdict 之前。
- 非功能:填檔牙與教師改口不改 STATUS 計算;散發副本與正本檔頭／GUIDANCE 保持同一句。

## Out of Scope

與 Decision Scope & Non-Goals 對齊:

- B 重編號整份 Stage 7 清單(新 id 消滅「2c = Fresh」)。
- C／AS-2 只改文件、不加填檔牙。
- AS-3 改整合腳本 STATUS 演算法或讓腳本自己重綁／自動 FAIL。
- T-later 等本 slug 跑完 Stage 7 再改範例。
- T-hist 改寫 `notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/` 當時舊序句。
- `#196`／gate-twin Backlog;diagram-ir-gate。
- 九條制度缺口(A-1～B-2)實作。
- Windows 真機驗證。
- 本 hop 與本 feat 實作 hop bump plugin。
- 本 Stage 4 hop 落地守衛碼、改 example／manifest／腳本正本(那些是 Stage 6 Files)。
- 本 feature branch 跑 `status-update.sh` 改正本 Active 列(OC-3)。
- 另造第二套整合工具／新的 `check-already-synced-*.sh` 家族(OC-1)。
- 把 `N_A_NO_INCOMING` 或未勾 draft 預先打紅。

## Diff Budget

本節是**估計**(給後續實作 hop,不是本規格 PR 的檔數)。超支本身非偏差,是停下判 L1/L2 的訊號。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| check-stage67 ST 填檔牙 + 五份 fixture | ≤3 | ≤180 | ≤260 |
| 活教師改口(example md／html、manifest、腳本檔頭×2) | ≤6 | ≤80 | ≤40 |
| GUIDANCE 恢復句 + parity | ≤2 | ≤30 | ≤40 |
| 衍生 fixture 同步 | ≤2 | ≤20 | ≤20 |
| Q6 錨(若需加 ST 字面) | ≤2 | ≤40 | ≤40 |
| **合計** | **≤15** | **≤350** | **≤400** |

[Assumption] 係數按「一個 S 一到兩條測試」,未加 mutation。本規格 PR 本身只動 `docs/dev/integration-before-verdict/4-spec.md` 與 twin html。

## Dependencies

- `scripts/check-stage67-enforcement.sh` ST 組 —— justification:OC-1 沿用既有家族,填檔牙掛這裡。
- `scripts/check-integration-regression-guard.sh` —— justification:檔頭／散發 parity、演算法不漂。
- `scripts/test-evidence-gauntlet.sh` —— justification:SC-4 既有 P0-1 模板順序牙。
- `scripts/devflow-integration-regression.sh` 與 `docs/dev/tools/` 散發副本 —— justification:T-now 檔頭 + GUIDANCE;不改 STATUS 演算法。
- `example/contract-expiry-reminder/`、`manifests/p4-gauntlet-gates.md` —— justification:活教師清單。
- `scripts/fixtures/spec-gate-dd-subsection/` —— justification:Decision Risk,與 example 同步。
- 無新外部服務、無新套件、無 migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ②公開檢查契約(check-stage67 ST 射程延伸到填檔);⑨Feature Risk = high;⑪ALREADY_SYNCED 恢復二選一
- Design source: 既有 pattern —— `check-stage67` ST、7-review 2c 結論貼腳本最後一行;填檔結論塊欄位是 Stage 3 throwaway 鎖的形狀,本檔釘名

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| check-stage67 ST(填檔牙) | 讀填好的 7-review;宣稱+ALREADY_SYNCED 時驗恢復二選一 | **擁有**填檔牙 exit／標記 | → 7-review 正文、→ fixture | 不得呼叫整合腳本改樹;不得新開第二家族;不得改 STATUS 演算法 |
| 整合腳本 | 只算只判,印 STATUS 與三 SHA | **擁有** STATUS 名稱與 exit 碼 | → git fetch／rev-parse | 不得 merge;不得因本 feat 改演算法 |
| 活教師(example／manifest／檔頭) | 教 2c=整合、2d=Fresh／gauntlet | 不擁有牙 | → 模板步號 | 不得改 HISTORY／dispatch;不得重編號模板 |
| 本 slug 7-review(後續 hop) | 真跑 1→7 的出貨紀錄 | **擁有**本 slug Source SHA | → 填檔牙、→ 整合腳本 | 不得宣告跳過 2c 或 Exit 才合 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| 填檔牙 | in:7-review md;out:exit 0／≠ 0 + 標記 | void-only → ≠ 0;`N_A_NO_INCOMING`／draft → 0 | 只讀填檔,不寫 repo | 既有模板 ST 字面項仍綠;只加填檔射程 |
| 整合腳本 GUIDANCE | in:STATUS;out:人讀的下一步 | ALREADY_SYNCED 仍 exit 2 | 文案與演算法分開;改字不改 exit | 散發副本與正本同一句 |
| 活教師改口 | in:舊 needle;out:2d Fresh／gauntlet、檔頭新句 | 漏改 html／fixture → 該 T 紅 | 同一 T 改正本+衍生 | 2c 步名保留給整合回歸 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| 填檔牙函式(住 check-stage67) | 解析宣稱、STATUS、恢復欄 | ← 7-review 正文 | md → 宣稱布林 → exit | 缺恢復 → void-only | S-1.1～S-1.5 fixture |
| GUIDANCE 字串 | 告訴人下一步 | ← STATUS 印出 | 只文案 | 演算法失敗仍 exit 2 | S-5.1 讀源碼 |
| 教師改口 | 換步號／檔頭 | ← example／manifest | 搜舊 needle → 替 2d | 漏改 → rg 非 0 | S-2.1～S-2.5 |

### Design Constraints
- 必須:沿用 check-stage67;恢復欄二選一;hex ≥7;n-a／draft no-fire;活教師一次掃完;既有三支牙仍綠。
- 禁止:第二套整合工具;重編號;改 STATUS 演算法;改 HISTORY／dispatch;本 branch 改 STATUS 表列;本 hop 落地碼;bump plugin;碰 `#196`。
- Extension point:後續若要重編號 2c／2d,必須回第 2 站改 Decision(B 已拒)。
- Known design limit:
  ① 填檔牙驗的是結論形狀,不重算 git 交集,也不核對重綁 SHA 是否真等於當時 HEAD(那是 2d／S-4.1 的事)。
  ② 本 Stage 4 hop 不能實跑 S-4.1(尚無本 slug 7-review)。
  ③ Cursor／編輯器不會在勾 checkbox 當下擋人;牙在跑檢查時才紅。

## Verification Profile(G2 一併審)
- lane: full(判準:新能力=填檔牙射程;公開檢查契約;高風險人機互動=重綁 vs FAIL、角色交接。Decision 已 lock full。owner 未要求降 fast;無偏離)
- Risk: high(判準:公開 API=check-stage67 對採用專案的填檔契約;不可逆=填好的 7-review 舊寫法會從綠變紅。不是金流／auth,但模板「公開 API／不可逆改動」吃這條)
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得只寫「證據不算數／輸出不算數」過關(S-1.1)
  - 不得誤殺 `N_A_NO_INCOMING` 或未勾 draft(S-1.4／S-1.5)
  - 不得另造第二套整合工具(S-1.7)
  - 不得重編號 2c／2d、不得改 STATUS 演算法(S-3.3)
  - 不得改 HISTORY／dispatch／stage7-loop(S-2.5)
  - 不得在本 slug 文件宣告跳過 2c 或 Exit 才合(S-4.3)
  - 不得碰 `#196`、九條缺口、bump plugin(Out of Scope)
- Required layers:check-spec-gate／check-stage67-enforcement／check-integration-regression-guard／test-evidence-gauntlet
- Conditional layers:Supply chain — 當實作改到 example 4-spec 步號時,同步 `scripts/fixtures/spec-gate-dd-subsection/`(S-2.6)
- Explicitly excluded layers:Mutation(本 hop 只規格;方法包未把 mutation 列為本 feat 必跑)、e2e／Playwright(無產品前端)、Race／stress(檢查是單程序讀檔,無新併發契約)
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/integration-before-verdict/4-spec.md && bash scripts/check-stage67-enforcement.sh && bash scripts/check-integration-regression-guard.sh && bash scripts/test-evidence-gauntlet.sh`
- Reliability triage:
  - Concurrency: n-a — 填檔牙是單程序讀一份 md;無多 writer 契約
  - Idempotency: applicable — 同一份 fixture 重跑必須得到同一 exit 與同一標記(S-1.1～S-1.5)
  - Timeout/retry: n-a — 本機檔案檢查、無外呼;紅了由人改 7-review 再跑,不自動重試

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 只寫作廢仍綠 | G-out-2 假過 | void-only fixture exit 0 | Required:S-1.1 | — |
| 重綁或 FAIL 被誤殺 | 恢復路徑走不通 | rebind／item-fail exit ≠ 0 | Required:S-1.2／S-1.3 | — |
| n-a／draft 預先紅 | 零新 commit 或草稿被擋 | na／draft exit ≠ 0 | Required:S-1.4／S-1.5 | — |
| 另造第二套工具 | 雙方法論 | 新的 `check-already-synced-*.sh` | Required:S-1.7 | — |
| 活教師仍教 2c=Fresh | 採用者抄舊序 | 指定 rg 仍有列 | Required:S-2.5 | — |
| 改口漏 html／fixture | 雙源漂 | html 或 spec-gate fixture 仍舊 needle | Required:S-2.1／S-2.6 | — |
| 重編號拆既有牙 | 模板 ST 假綠或全紅 | 2c／2d 標號被改 | Required:S-3.3／S-3.2 | — |
| GUIDANCE 仍只說不算數 | 人不知道下一步 | GUIDANCE 無重綁／FAIL | Required:S-5.1 | — |
| Exit 才合 | 核准樹≠出貨樹 | 本 slug 兩 SHA 不同 | Required:S-4.1／S-4.2 | S-4.1 本 hop 尚無產物(Known limit ②) |
| 填檔牙不核 SHA==HEAD | 寫假 hex 仍綠 | 恢復欄 hex ≠ HEAD 但 exit 0 | Known limit ①;S-4.1 補 | 牙只驗形狀,不重算 git |

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記 Decision／Stage 3 留給本檔釘死的選擇。不翻 A + AS-1 + T-now。
G2 `verdict:` 留空,本表狀態維持待人審;Agent 不代填 ✅／PASS。

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 結論塊標題 `## 2c 整合結論`;鍵=`STATUS`／`FORK`／`HEAD`／`INTEGRATION`／`REF`／`恢復`。ALREADY_SYNCED 恢復字面二選一:`重綁 Final Fresh。Source SHA: <hex≥7>` 或 `本項 FAIL`。宣稱四條件見 S-1.6 | Stage 3 throwaway 已鎖形狀,本檔釘名;2c 不重編號 | `3-prototype.md:49-59`;`2-decision.md` Risk「欄位名進 4-spec」 | 改鍵名則五份 fixture 與 S-1.6 全改 | 待人審 |
| DD-2 | 填檔牙掛 `scripts/check-stage67-enforcement.sh` ST 組;fixture 目錄 `scripts/fixtures/as1-filled-tooth/`(`void-only`／`rebind-sha`／`item-fail`／`na-incoming`／`draft-unclaimed`／`verdict-then-merge`) | OC-1 禁止第二家族;Stage 3 五份對照 + SC-1 對照樣本 | `2-decision.md` OC-1;`3-prototype.md:135-143` | 改掛 gate-consistency 獨立入口則 S-1.7 翻 | 待人審 |
| DD-3 | 活教師改口:Final Fresh／gauntlet 步號 2c→**2d**;腳本檔頭改「步 2c 整合回歸,Fresh 之前,不是 Exit 程序」。不改 HISTORY／dispatch | T-now;Stage 3 改口副本 needle=0 | `2-decision.md` Decision／SC-3;`3-prototype.md:150` | 改成重編號模板則回第 2 站(B 已拒) | 待人審 |
| DD-4 | GUIDANCE 可改字、不可改 STATUS 演算法與 exit 碼。ALREADY_SYNCED 仍 exit 2 | AS-3 已拒改演算法;GUIDANCE 是弱教師 | `2-decision.md` Rejected AS-3;`scripts/devflow-integration-regression.sh:204-205` | 若改 exit 碼則整合腳本契約與 guard 全翻 | 待人審 |
| DD-5 | Q6 錨句只鎖「整合回歸在 Final Fresh 之前」「ALREADY_SYNCED 不得只寫證據不算數」;不重寫已對的 2c 散文 | Decision In + 內部技術選擇 | `2-decision.md:100`、`:115` | 再搬 2c 散文會違反「承認已搬」 | 待人審 |
| DD-6 | Feature Risk = high;lane = full。G2 verdict 由人類填,本 hop 留空 | 公開檢查契約 + 填檔舊寫法會從綠變紅;使用者指定不代填 G2 | `_templates/4-spec.md` Risk 判準;本 hop brief | 改 normal 則 Failure Model 可改選配 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 恢復欄 hex 字元集:`[0-9a-fA-F]`,長度 ≥7(Stage 3 樣張 `def4567890abc`)。
- void-only 輸出標記用 `void-only`;重綁用 `rebind-sha:<hex>`;FAIL 用 `item-FAIL`;n-a／draft 用 `no-fire:…`(與 Stage 3 throwaway 對齊,正式碼可加前綴但必須含這些子字串)。
- example html twin 與 md 同一 T 重生。
- 本 hop 產審頁用 `scripts/build-stage4-html.py --action`;G2 五格用 `scripts/build-gate-twin.py`。不手包 html-shell。
- 本 branch 不跑 `status-update.sh`(OC-3)。

## Test Skeletons(選配)

- `test_s_1_1_void_only_exits_nonzero`
- `test_s_1_2_rebind_sha_exits_zero`
- `test_s_1_3_item_fail_exits_zero`
- `test_s_1_4_na_incoming_nofire`
- `test_s_1_5_draft_unclaimed_nofire`
- `test_s_1_7_no_second_tool_family`
- `test_s_2_5_live_teacher_needles_zero`
- `test_s_2_6_spec_gate_fixture_tracks_example`
- `test_s_3_2_existing_teeth_still_green`
- `test_s_3_3_no_renumber_no_algo_change`
- `test_s_5_1_guidance_has_recovery`
- `test_s_4_2_verdict_then_merge_shas_differ`

## Stage 3 對帳

Human verdict = ACCEPTED(`human:rick @ 2026-09-12`)。逐場下落:

| Demo 場景 | 下落 |
|---|---|
| AC-2 void-only 必須紅 | S-1.1;Recovery 在 S-1.1 Operational Context |
| AC-2 重綁 SHA 或本項 FAIL | S-1.2、S-1.3 |
| AC-2 n-a／draft 不預先紅 | S-1.4、S-1.5 |
| AC-3 意圖序 + 活教師改口 | S-2.1～S-2.5、S-3.1、S-3.3;Out of Scope:本 hop 不改 example 正本 |
| AC-1 出貨樹=核准樹(本站只展示序) | S-4.1、S-4.2;本 hop 不真合併(Known limit ②) |
| Method 走查:結論塊形狀 | S-1.6、DD-1 |
| Method 走查:發動時機 | S-1.6 宣稱四條件 |
| Method 走查:正式守衛不在 Stage 3 落地 | Out of Scope「本 Stage 4 hop 落地守衛碼」;實作在 Stage 6 |
| Operational Context Recovery(重綁或 FAIL) | S-1.1／S-1.2／S-1.3 的 Recovery 欄 |

## 確認紀錄
- N1 前站核對 | 2026-09-12 | tip `1f8d992`(#211);G1 PASS(#207);3-prototype status=approved、Human ACCEPTED + attestation。驗收雛形 3 條(AC-1／AC-2／AC-3)。living spec `docs/specs/` 0 條;受影響契約=_templates/7-review.md(散文已對,不改序)+ check-stage67 射程 + 活教師五路徑
- R 範圍確認 | 2026-09-12 | IMPLEMENTER C dispatch:encode R/S/DD from Decision;tip already 2c→2d Fresh;remaining = AS-1 filled-file tooth + live-teacher sweep。R-1 填檔牙、R-2 活教師、R-3 不重編號、R-4 真跑載體、R-5 GUIDANCE
- S 逐段確認 | 2026-09-12 | 同一 dispatch 鎖 Decision／Stage 3 形狀;每 S 有觀測欄
- 3a 四節 | 2026-09-12 | AC／Out of Scope／Diff Budget／Dependencies 齊
- 3b Profile | 2026-09-12 | lane full、Risk high、Failure Model、Reliability triage、Design Boundary applicable
- 3c Stage 3 | 2026-09-12 | 五個 Demo 場景 + Method 走查 + Recovery 皆有 R/S 或 Out of Scope 下落
- DD 掃描 | 2026-09-12 | 上層六條待人審;無「待裁決」殘留;不翻 Decision
- G2 verdict | 2026-09-12 | 留空,留給人類,不代填 PASS
