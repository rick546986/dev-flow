---
feature: host-stack-fit
stage: 4-spec
status: approved
verdict: PASS
owner: rick
reviewers: [user]
updated: 2026-09-10
baseline: v3.22.1 / ff6049a
contract: 2.0.0
issue: 149
---

# 4. 規格 — 主機執法貼近與堆疊盤點(change spec)

> 基準:`main` tip `ff6049a`(#156 G1 PASS)。契約維持 `2.0.0`。本 hop **只寫規格**,不改 hooks／skills、不 bump plugin、不改 `STATUS.md` 表列。
> Decision 正本:`docs/dev/host-stack-fit/2-decision.md`(H1+C、I2 底 + I4 選配、OC-1～OC-4 ✅)。本檔把 Stage 2 留下的形狀釘成可測 R/S,不翻案。
> 追蹤:[#149](https://github.com/rick546986/dev-flow/issues/149)。
>
> **HISTORY(2026-09-10)**:多代理人審查收斂三處,owner 核准,不翻 H1+C／I2+I4 Decision。① DD-1 stamp 輸入綁專案 `root`;核對必須 `receipt.slug`==路徑 slug==`--action` slug、`receipt.station`／`script` 對上呼叫腳本、`receipt.root`==核對時專案根。② DD-2 只認可選布林 `verify_receipt:true`(true=只核對不鑄;缺欄=舊 graph);不認 `action:"verify_receipt"` 當第二把鑰匙。③ DD-3 深度 = 專案級宣告 pin + pin／requirements 第一層 `direct_deps`(不是 per-slug「這次 feat 碰到的檔」;不是 lock 全樹)。同日 owner 簽 G2 PASS;`verdict: PASS`、`status: approved`、DD-1～DD-5 ✅。

## Stage 3 跳過(owner 明示)

Owner 於 2026-09-09 明示跳過 Stage 3 原型,直接進 Stage 4。理由:**Decision 已夠清楚,不需原型。** 本資料夾無 `3-prototype.md`。2-decision 定稿時寫「不預先跳過、觸發留給第 3 站」;本 hop 以 owner 後續明示為準,不回改正本 Decision 組合包。

Human verdict: N/A

## 補助模組生命週期（預覽）

只畫本 feat 碰到的兩塊:主機收據與堆疊盤點／setup。有關聯的收成一格,不拆檔名。直式圖,置中。
- 新生（這輪沒有）：不加欄。
- 改行為（相關一格）：該站 `--action` 鑄收據;dev-setup 寫 I2;選配 I4。
- 退役：沒有。
- 不動：PreToolUse、`--action` 圍欄、Stage 1–4 模板、plugin 版本、lock 正本。

## ADDED Requirements

### R-1: 系統 SHALL 鑄出該站 `--action` 收據
非 Claude 開工跑該站 `--action` 且結果為 allow(exit 0)時,既有腳本必須在正規路徑寫出 `devflow-host-receipt/v1` JSON。`--probe`、`devflow-exec start`、`--write-cursor`、`check-write-scope.sh --action` 都不鑄。不另造第二套檢查家族(OC-1)。

**審的時候看什麼**
看 `.devflow/host-receipt/<slug>/<station>.json` 是不是腳本寫出來的、欄位齊不齊。只看到 `exec.json` 或探針綠不算鑄造。

#### S-1.1 七支該站腳本 allow 後鑄檔
- GIVEN 專案根存在、slug=`host-stack-fit`、`.devflow/host-receipt/host-stack-fit/` 尚無任何 `.json`
- WHEN 下列任一腳本以 `--action FILE` 跑完且 exit 0:`scripts/check-devtalk-graph.sh`、`scripts/check-devstage2-graph.sh`、`scripts/check-devstage3-graph.sh`、`scripts/check-devstage4-graph.sh`、`scripts/check-devstage5-graph.sh`、`scripts/check-devstage6-graph.sh`、`scripts/check-devstage7-graph.sh`
- THEN 對應路徑寫出一個 UTF-8 JSON 物件:talk → `talk.json`;stage2 → `stage2.json`;stage3 → `stage3.json`;stage4 → `stage4.json`;stage5 → `stage5.json`;stage6 → `stage6.json`;stage7 → `stage7.json`
- 觀測:從 `.devflow/host-receipt/host-stack-fit/<station>.json` 看 | 檔存在、`json.load` 得到 object、`schema`=`devflow-host-receipt/v1` 算過 | 用暫存專案根跑該站 `--action` fixture(allow)測
- Operational Context:
  - Actor:開工 agent(Cursor／Grok／Codex)
  - Goal:留下「已跑該站 `--action`」的腳本鑄收據
  - Situation:讀得到 skills,但沒有 Claude PreToolUse
  - Known information:該站腳本路徑、slug、`--action` JSON
  - Missing information:本主機這次有沒有真的跑過 `--action`
  - Human decision:要不要在宣稱可寫碼之前先跑該站 `--action`
  - Authority:開工 agent 可跑腳本;owner 看收據在或不在
  - External dependency:無網路;本機 shell
  - Out-of-system action:在終端機跑 `--action`
  - Waiting/timeout behavior:腳本同步結束;無重試契約
  - Recovery:deny(exit 1)或契約缺失(exit 2)不鑄檔;修好 payload 後重跑 allow 才鑄
  - Audit/handoff requirement:收據留在 `.devflow/host-receipt/<slug>/`(本機,不進 Git)
  - Observation:見本條觀測

#### S-1.2 收據必填欄與 stamp
- GIVEN S-1.1 鑄出的檔
- WHEN 讀該 JSON
- THEN 恰好含這些鍵且型別如下:`schema`(字串 `devflow-host-receipt/v1`)、`station`(字串,值為 `talk` 或 `stage2`…`stage7`)、`slug`(字串)、`node`(字串,缺游標則 `""`)、`script`(字串,相對 repo 根,例如 `scripts/check-devstage4-graph.sh`)、`argv`(陣列,第一個元素為 `--action`)、`action_result`(字串 `allow`)、`minted_at`(UTC ISO-8601,含 `T` 與 `Z`)、`root`(本次鑄檔所用專案根的絕對路徑)、`payload_sha256`(64 個小寫 hex)、`DONE`(JSON 布林 `true`,不是字串)、`stamp`(64 個小寫 hex)。`root` 必須等於該次呼叫的專案根。`stamp` 輸入必須含 `root`:`stamp` = SHA-256(UTF-8,無多餘空白)的 `devflow-host-receipt/v1|{station}|{slug}|{node}|{script}|{root}|{action_result}|{minted_at}|{payload_sha256}|true`
- 觀測:用 `json.load` 印鍵集合與 `DONE` 的 `type` | 鍵齊、`DONE is True`、自算 stamp 與檔內相同算過 | 拿 S-1.1 產出檔測
- Operational Context:不適用 — 純欄位形狀,無人員交接。

#### S-1.3 probe／start／write-cursor／write-scope 不鑄
- GIVEN 同一專案根,`.devflow/host-receipt/` 為空
- WHEN 分別跑:`scripts/check-host-adapter.sh --probe <root>`、`scripts/devflow-exec.sh start`(若本樹有此入口)、該站 `--write-cursor NODE`、`scripts/check-write-scope.sh --action FILE`
- THEN `.devflow/host-receipt/` 仍不存在任何 `.json`;上述指令的既有 exit 契約不變
- 觀測:從 `.devflow/host-receipt/` 看 | 目錄不存在或零個 `.json` 算過 | 用空收據樹分別跑四種入口測
- Operational Context:不適用 — 負向鑄造邊界,無人員交接。

#### S-1.4 deny 與 exit 2 不鑄、allow 覆寫同路徑
- GIVEN slug=`host-stack-fit`、station=`stage4`、已有一份有效 `stage4.json`
- WHEN 先跑 `check-devstage4-graph.sh --action` 且 exit 1 或 2,再跑一次 exit 0
- THEN 第一次之後檔內容與時間戳不變;第二次之後同路徑被覆寫,`minted_at` 與 `payload_sha256` 換成第二次、`DONE` 仍為 `true`
- 觀測:比對兩次前後的 `minted_at` 與 `payload_sha256` | deny／exit 2 後哈希不變、allow 後哈希變且檔仍一份算過 | 用同一 slug 連跑 deny 再 allow 測
- Operational Context:不適用 — 覆寫規則,無人員交接。

### R-2: 系統 SHALL 核對收據並 fail-closed
核對走**同一支**該站 `--action` 腳本,不新開 `check-host-receipt.sh`。核對開關**只有**一個可選欄:`verify_receipt`(JSON 布林)。值為 `true` 時只核對、不鑄檔。缺此欄 = 舊行為(只做 graph 裁決,不核收據)。不接受 `action:"verify_receipt"` 當第二把鑰匙,也不因該字串 fail-open。缺檔／空檔／手填／缺 `DONE:true`／stamp 不符／`receipt.slug` ≠ 路徑 slug 或 ≠ `--action` slug／`receipt.station` 或 `receipt.script` 對不上呼叫中的腳本／`receipt.root` ≠ 本次核對的專案根／只跑過 `start` → exit ≠ 0,stderr 含 `未跑 --action`,且不得出現 `已與 Claude 同等武裝`。fail-closed 發生在宣稱「已武裝／可寫碼」之前,也發生在非 Claude 第一次寫入本站 feature 檔之前。`start` 單獨成功 ≠ 已武裝。不是密碼學防偽。

**審的時候看什麼**
看核對指令的 exit 與 stderr。人要能指著收據檔說在或不在,而且文案同時有「無 PreToolUse」與「`--action`」。

#### S-2.1 有效收據核對 exit 0
- GIVEN S-1.2 形狀的 `stage4.json` 已在 `.devflow/host-receipt/host-stack-fit/stage4.json`
- WHEN `scripts/check-devstage4-graph.sh --action FILE`,FILE 為 `{"cursor":{"node":"S5-gate","slug":"host-stack-fit"},"action":"write_spec","slug":"host-stack-fit","verify_receipt":true}`(`action` 仍是 graph 動詞;`verify_receipt` 是唯一核對開關)
- THEN exit 0;不改寫該收據檔;`schema`／`stamp` 仍與核對前相同;且 `receipt.slug`==路徑 slug `host-stack-fit`==`--action` slug、`receipt.station`=`stage4`、`receipt.script`=`scripts/check-devstage4-graph.sh`、`receipt.root` 等於本次核對的專案根
- 觀測:看指令 exit 與核對前後檔的 `stamp` | exit 0 且 stamp 不變算過 | 用 S-1.1 鑄好的 stage4 檔測
- Operational Context:
  - Actor:開工 agent
  - Goal:證明本站已有腳本鑄收據,才能宣稱可寫碼
  - Situation:非 Claude session,準備寫 `4-spec.md` 或產品檔
  - Known information:收據路徑、該站腳本
  - Missing information:無(檔在就可核)
  - Human decision:核對綠了才准宣稱武裝
  - Authority:腳本 exit 0／≠ 0;人看 stderr
  - External dependency:無
  - Out-of-system action:跑同一支 `--action`
  - Waiting/timeout behavior:同步
  - Recovery:紅了先重跑該站 `--action` 鑄檔,再核對
  - Audit/handoff requirement:核對不另造家族
  - Observation:見本條觀測

#### S-2.2 缺檔、空檔、空白檔皆紅
- GIVEN 三種輸入:(1)路徑不存在;(2)零位元組檔;(3)只含空白字元(space／tab／newline)的檔,放在 `.devflow/host-receipt/host-stack-fit/stage4.json`
- WHEN 對每種輸入跑 S-2.1 同一條 `verify_receipt:true`
- THEN 每次 exit ≠ 0;stderr 含字串 `未跑 --action`;stdout／stderr 都不含 `已與 Claude 同等武裝`
- 觀測:看 exit 與 stderr 原文 | 三案皆紅且含指定字串、不含武裝句算過 | 用三種暫存檔測
- Operational Context:不適用 — 核對失敗形狀,無人員交接。

#### S-2.3 手填與缺 DONE 皆紅
- GIVEN 四份放在正規路徑的檔:(1)Markdown 清單,內文 `DONE` 與 `--action`;(2)JSON 物件缺 `stamp`;(3)JSON `DONE` 為字串 `"true"`;(4)JSON `DONE` 為 `false` 或鍵不存在
- WHEN 各跑一次 S-2.1 的 `verify_receipt:true`
- THEN 四次皆 exit ≠ 0;stderr 含 `未跑 --action`;不含 `已與 Claude 同等武裝`
- 觀測:看四次 exit 與 stderr | 全紅且咬指定字串算過 | 用手寫 md／殘缺 JSON fixture 測
- Operational Context:不適用 — 真偽核對,無人員交接。

#### S-2.4 stamp 不符、slug／station／script／root 對不上則紅
- GIVEN 五份其餘欄位齊的 JSON,分別:(1)`stamp` 改成 64 個 `0`;(2)`station` 改成 `stage7`;(3)`script` 改成 `scripts/check-host-adapter.sh`;(4)`slug` 改成 `other-slug`(路徑仍為 `.devflow/host-receipt/host-stack-fit/stage4.json`,`--action` slug 仍為 `host-stack-fit`);(5)`root` 改成另一個絕對路徑
- WHEN 用 `check-devstage4-graph.sh` 對該專案根跑 S-2.1 同一條 `verify_receipt:true`
- THEN 五次皆 exit ≠ 0;stderr 含 `未跑 --action`。核對必須同時成立:`receipt.slug` == 路徑 slug == `--action` slug;`receipt.station` 與 `receipt.script` 對上呼叫中的腳本;`receipt.root` 等於本次核對的專案根。任一不合即紅
- 觀測:看 exit 與 stderr | 五案皆紅算過 | 用改過欄位的 JSON 測
- Operational Context:不適用 — stamp／身分／root 核對。

#### S-2.5 只跑 start 不得宣稱武裝
- GIVEN `.devflow/exec.json` 因 `devflow-exec start` 存在,且 `.devflow/host-receipt/` 無任何收據
- WHEN 對 `stage4` 跑 `verify_receipt:true`,或 session 輸出宣稱「已武裝／可寫碼／已與 Claude 同等武裝」
- THEN `verify_receipt:true` exit ≠ 0 且 stderr 含 `未跑 --action`;任何「已武裝／可寫碼」宣稱在本 session 產出裡必須同時能指出一份核對過的收據路徑,否則該宣稱不算數。文案若提到主機限制,必須同時出現 `無 PreToolUse`(或 `沒有 PreToolUse`)與 `--action`
- 觀測:從核對 exit、stderr、session 開場紀錄看 | start 後核對紅;有宣稱則能指出收據檔,且文案含兩個指定詞算過 | 用 throwaway Cursor／本機 session:先 start、不跑 `--action` 測(AC-1／AC-2／SC-1／SC-2)
- Operational Context:
  - Actor:開工 agent 與 owner
  - Goal:不要把 start 成功讀成 Claude 同級執法
  - Situation:`exec.json` 在,PreToolUse 不跑
  - Known information:start 已寫 baseline
  - Missing information:該站 `--action` 收據
  - Human decision:owner 看到核對紅就否決「已武裝」
  - Authority:核對腳本;owner 批 G2／開工
  - External dependency:無
  - Out-of-system action:人指出收據在或不在
  - Waiting/timeout behavior:無
  - Recovery:補跑該站 `--action` 鑄檔後再核對
  - Audit/handoff requirement:開場紀錄或 setup 輸出可分辨有／無本次檢查
  - Observation:見本條觀測

#### S-2.6 fail-closed 時點:宣稱武裝與第一次寫檔之前
- GIVEN 非 Claude session,本站尚無有效收據
- WHEN agent 要輸出「可寫碼／已武裝」,或要對本站 feature 檔做第一次 Write／Edit(例:`docs/dev/host-stack-fit/4-spec.md`)
- THEN 必須先有該站 `verify_receipt:true` exit 0;若核對未跑或 exit ≠ 0,不得把該次寫入標成已武裝。Claude Code 既有 PreToolUse 擋寫規則不變;Claude 不要求人指收據才能寫,但同一支 `--action` 仍在 allow 時鑄檔
- 觀測:從本 repo 可跑的核對指令與「核對前／後」兩次呼叫看 | 核對前 exit ≠ 0,鑄檔並核對後 exit 0 算過;Claude PreToolUse 行為用既有 `hooks/hooks.json` 與 `.cursor-plugin/plugin.json` 對照(薄殼仍無 hooks 鍵) | 用暫存樹:無收據核對 → 鑄 → 再核對。n-a:Cursor 編輯器 Write 工具本身無 hook,改用本 repo 核對指令當替代觀測
- Operational Context:
  - Actor:開工 agent
  - Goal:在寫第一個 feature 檔之前先有牙
  - Situation:Cursor／Grok 沒有 PreToolUse
  - Known information:本站腳本與 slug
  - Missing information:收據
  - Human decision:紅就不准宣稱可寫碼
  - Authority:核對 exit;owner 看檔
  - External dependency:無
  - Out-of-system action:跑 `--action`
  - Waiting/timeout behavior:無
  - Recovery:鑄檔後重核
  - Audit/handoff requirement:收據路徑可指
  - Observation:見本條觀測

#### S-2.7 不認 `action:"verify_receipt"` 當核對開關
- GIVEN 專案根與 slug=`host-stack-fit`;`--action` JSON **沒有** `verify_receipt:true`(鍵缺席,或值不是 JSON 布林 `true`)
- WHEN `scripts/check-devstage4-graph.sh --action FILE`,FILE 為 `{"cursor":{"node":"S5-gate","slug":"host-stack-fit"},"action":"verify_receipt","slug":"host-stack-fit"}`
- THEN 腳本不得因 `action` 字串進入只核對、不鑄模式;缺 `verify_receipt:true` = 舊 graph 裁決。不得把 `action:"verify_receipt"` 當成第二把鑰匙或 fail-open 核對。graph 依既有規則處理這個 `action` 值(未知動詞 → 既有 deny／exit ≠ 0,既有字面)
- 觀測:看 exit、是否鑄檔、stderr | 未進入 verify-only;沒有只因該 `action` 字串而核對綠算過 | 用無布林鍵的 payload 測
- Operational Context:不適用 — 開關鍵邊界,無人員交接。

### R-3: 系統 SHALL 寫出 I2 堆疊盤點
`dev-setup` 的 install／upgrade／check 必須在專案級寫 `docs/dev/0-inventory.json`,schema=`devflow-stack-inventory/v1`。深度綁在**專案級**:宣告 pin + 來自 pin／requirements 的第一層 `direct_deps`。不是 per-slug「這次 feat 碰到／改到的檔」;不是 lock 全樹／transitive。Decision D1「宣告 pin + 直接相依、不做全樹」在本檔收成專案第一層,不是 feature-scoped。方法包與產品專案同一欄位形狀(R-5)。落差列必須在進 Stage 4 之前就在這個檔上。

**審的時候看什麼**
打開 `docs/dev/0-inventory.json`。母版樣張要看得到 Python 地板 3.9 與 `markdown-it-py==4.0.0`,以及 3.9 vs 3.12+ 的落差列。

#### S-3.1 I2 路徑與必填欄
- GIVEN 一份剛跑完 `dev-setup` install 或 check 的專案樹(方法包或產品)
- WHEN 讀 `docs/dev/0-inventory.json`
- THEN 檔為 UTF-8 JSON 物件,必填鍵:`schema`(值 `devflow-stack-inventory/v1`)、`written_by`(值 `dev-setup`)、`written_at`(UTC ISO-8601,含 `Z`)、`project_kind`(值 `methodology-pack` 或 `product`)、`languages`(非空陣列)、`declared_pins`(陣列)、`direct_deps`(陣列)、`gaps`(陣列,可空)。每個 `languages[]` 必填:`language`(字串,例 `Python`)、`runtime_version`(字串,例 `3.9.6`)、`runtime_cmd`(字串,值 `python3 --version`)。每個 `declared_pins[]` 與 `direct_deps[]` 必填:`name`、`version`、`source`(相對 repo 根的 pin／requirements 路徑)。每個 `gaps[]` 若存在必填:`local_runtime`、`requirement`、`pin`、`source`
- 觀測:從 `docs/dev/0-inventory.json` 看 | `json.load` 後上列鍵齊、陣列元素欄位齊算過 | 對本 repo 跑 setup check 或對 fixture 樹跑同等寫入測
- Operational Context:
  - Actor:owner／採用者／開工 agent
  - Goal:進完整 lane 之前看見語言、runtime、套件版本
  - Situation:setup 剛做完或依賴剛變
  - Known information:pin 檔、本機 `python3 --version`
  - Missing information:間接套件與 per-slug「這次碰到的檔」(本 v1 都不寫)
  - Human decision:看到落差要不要換直譯器／venv
  - Authority:`dev-setup` 寫檔;人讀檔
  - External dependency:本機直譯器
  - Out-of-system action:裝 venv 或設 `DEVFLOW_PYTHON`
  - Waiting/timeout behavior:setup 同步寫完
  - Recovery:缺檔 = setup 未完成,重跑 check
  - Audit/handoff requirement:檔在 `docs/dev/`,進 Git,fast lane 也讀得到
  - Observation:見本條觀測

#### S-3.2 母版樣張對上 3.9 與 markdown-it-py
- GIVEN 本方法包(`project_kind`=`methodology-pack`),pin 來源含 `scripts/requirements-methodology-render.txt` 的 `markdown-it-py==4.0.0`,以及 `scripts/check-py-floor.sh`／`docs/PLUGIN.md` 宣告的 Python 3.9 編譯地板
- WHEN `dev-setup` 寫完 I2
- THEN `declared_pins` 至少有一列 `name`=`markdown-it-py` 且 `version`=`4.0.0` 且 `source`=`scripts/requirements-methodology-render.txt`;`languages` 至少有一列 `language`=`Python`;`direct_deps` 至少含同一顆 `markdown-it-py` `4.0.0`(專案 pin／requirements 第一層,不含 transitive,也不是本 feat 碰到的檔清單)。不把 lock 全樹寫進任一陣列
- 觀測:從 I2 JSON 三個陣列看 | 指定 pin 列存在、無第二層套件列算過 | 拿本 repo `docs/PLUGIN.md` + `scripts/requirements-methodology-render.txt` 當輸入(AC-3／SC-4)
- Operational Context:不適用 — 欄位對帳,無人員交接。

#### S-3.3 落差列在進 Stage 4 之前
- GIVEN 本機 `python3 --version` 主次版為 `3.9`,且 I2 已寫入 `markdown-it-py` `4.0.0`(該套件執行地板為 Python 3.12+)
- WHEN 讀 `gaps`
- THEN 至少一列同時含 `local_runtime` 以 `3.9` 開頭、`requirement` 含 `3.12`、`pin`=`markdown-it-py==4.0.0`;此列在任何人開始寫該專案 `docs/dev/<slug>/4-spec.md` 之前就已在檔上
- 觀測:從 `gaps` 列看 | 三個指定子字串同列出現,不是等 render 爆才補算過 | 用 #122 情節(3.9 地板 vs `markdown-it-py==4.0.0`)測(AC-4／SC-5)
- Operational Context:
  - Actor:owner／開工 agent
  - Goal:地板落差提早落檔
  - Situation:檢查全綠、本機 3.9 裝不出 4.x
  - Known information:PLUGIN 地板段、render pin
  - Missing information:無
  - Human decision:換 3.12+ venv 或接受不能產圖
  - Authority:人改環境;setup 只寫落差
  - External dependency:本機 Python
  - Out-of-system action:建 venv
  - Waiting/timeout behavior:無
  - Recovery:換直譯器後重跑 setup check 改寫 I2
  - Audit/handoff requirement:gaps 列可指
  - Observation:見本條觀測

#### S-3.4 依賴變了要重寫 I2
- GIVEN `docs/dev/0-inventory.json` 的 `written_at` 早於 `scripts/requirements-methodology-render.txt`(或產品樹的 `requirements*.txt`／`pyproject.toml`／`package.json`)的 mtime,或 `python3 --version` 字串已不等於檔內 `runtime_version`
- WHEN 再跑 `dev-setup` check(或 install／upgrade 的盤點步)
- THEN 腳本覆寫同一路徑 `docs/dev/0-inventory.json`;新檔 `written_at` 較新;`declared_pins` 反映當前 pin 檔。只做 `git pull`、不跑 setup → 檔不自動改;`dev-setup` 指引必須有一句「依賴變了要重跑」
- 觀測:從 I2 `written_at` 與 pin 檔 mtime、setup 說明句看 | check 後時間戳更新;只 pull 則時間戳不變;說明句存在算過 | 改 pin 檔 mtime 後跑 check,對照不跑 setup 的對照組
- Operational Context:
  - Actor:採用者
  - Goal:pull 之後盤點不要默默過期
  - Situation:套件 pin 剛變
  - Known information:舊 I2
  - Missing information:新 pin
  - Human decision:要不要立刻重跑 setup
  - Authority:人觸發 setup
  - External dependency:無
  - Out-of-system action:跑 `dev-setup`
  - Waiting/timeout behavior:無
  - Recovery:check 當 broken／stale 並列出要重寫
  - Audit/handoff requirement:同一路徑覆寫,不另存
  - Observation:見本條觀測

#### S-3.5 setup 未寫 I2 則未完成
- GIVEN 專案已有 `docs/dev/` 但沒有 `docs/dev/0-inventory.json`
- WHEN 跑 `dev-setup` check
- THEN exit ≠ 0,或狀態列為 broken／stale,且輸出點名缺 `docs/dev/0-inventory.json`
- 觀測:看 check exit 與輸出 | 缺檔不得當 current／成功算過 | 刪掉 I2 後跑 check 測
- Operational Context:不適用 — setup 完成條件。

### R-4: 系統 SHALL 選配寫出 I4 摘要
I4 不是每專案強制(OC-3)。只有人要機器可讀 lock digest 或散文堆疊頁時才建立。預設路徑只有專案級 `docs/dev/0-stack.md`(OC-2),不是 `docs/dev/<slug>/0-stack.md`。I2 是盤點欄位正本;I4 是投影。digest 不是 lock 正本。

**審的時候看什麼**
沒有 `0-stack.md` 仍可過 I2。有的話,版本列要抄 I2,digest 只當指紋。

#### S-4.1 預設不建 I4
- GIVEN 新專案跑完 `dev-setup` install,且沒有人要求 digest 或散文摘要
- WHEN 列 `docs/dev/`
- THEN 有 `0-inventory.json`;沒有 `0-stack.md`;setup 仍 exit 0(在 I2 已寫的前提下)
- 觀測:從 `docs/dev/` 檔名清單看 | I2 在、I4 不在算過 | 對 fresh fixture 跑 install 測
- Operational Context:
  - Actor:採用者
  - Goal:不要每專案多一個強制產物
  - Situation:只需要盤點欄位
  - Known information:I2 已寫
  - Missing information:無
  - Human decision:要不要後來再加 I4
  - Authority:人決定加不加
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:之後要摘要再加檔
  - Audit/handoff requirement:缺 I4 不是 broken
  - Observation:見本條觀測

#### S-4.2 建立 I4 的時機與內容
- GIVEN I2 已存在,且人明確要求 lock digest 或散文堆疊頁
- WHEN 寫入 `docs/dev/0-stack.md`
- THEN 檔為 UTF-8 Markdown;必須有一節列出與 I2 相同的 `language`／`runtime_version`／每個 `declared_pins` 的 `name`+`version`;必須有一句「盤點正本是 `docs/dev/0-inventory.json`」;若含 digest,格式為一行 `` `<filename>` sha256:<64 hex> ``,`<filename>` 為既有 lock／pin 檔(例 `package-lock.json` 或 `scripts/requirements-methodology-render.txt`),hex 為該檔位元組的 SHA-256;檔內必須有一句「digest 不是 lock 正本」
- 觀測:從 `docs/dev/0-stack.md` 與 I2 JSON 對看 | 版本列與 I2 逐列相同、兩句指定文案在、digest 行(若有)對得回檔位元算過 | 先寫 I2 再按人要求加 I4 測
- Operational Context:
  - Actor:owner／開工 agent
  - Goal:給機器或人一份摘要,但不另造套件正本
  - Situation:需要對 lock 做指紋或給人讀
  - Known information:I2、lock／pin 檔
  - Missing information:無
  - Human decision:要不要 digest
  - Authority:人要求才寫
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:I2 與 I4 版本列不一致 → 重寫 I4 或重跑 setup 再投影
  - Audit/handoff requirement:只有這一個預設路徑
  - Observation:見本條觀測

#### S-4.3 digest 不是 lock 正本、不寫每 slug 一份
- GIVEN 已有 `docs/dev/0-stack.md` 含 digest 行
- WHEN 比對 pip／npm lock(或本 repo 的 pin 檔)與 I4
- THEN 套件版本爭議以 lock／pin 檔為準,不以 digest 行覆寫 I2 或 lock;不得出現 `docs/dev/<slug>/0-stack.md` 作為本 feat 的預設或第二落點
- 觀測:搜產品樹 `0-stack.md` 路徑與衝突規則句 | 只見 `docs/dev/0-stack.md`;規則句寫明 lock／pin 勝 digest 算過 | 用本 repo 搜尋與 I4 樣張測
- Operational Context:不適用 — 正本層級,無人員交接。

### R-5: 系統 SHALL 共用同一盤點 schema
方法論母版與產品專案使用同一個 `devflow-stack-inventory/v1` 必填鍵集合與同一深度(宣告 pin + 第一層直接相依)。內容各填。不另造第二份 artifact 形狀。

#### S-5.1 兩種 project_kind 鍵集合相同
- GIVEN 一份 `project_kind`=`methodology-pack` 的 I2 與一份 `project_kind`=`product` 的 I2
- WHEN 比較頂層鍵集合,以及 `languages[]`／`declared_pins[]`／`direct_deps[]`／`gaps[]` 的元素鍵集合
- THEN 兩份頂層鍵集合相等;四個陣列的元素鍵集合分別相等;`schema` 都是 `devflow-stack-inventory/v1`;深度都只含專案級宣告 pin 與 pin／requirements 第一層直接相依,都沒有 transitive 全樹,也都不是 per-slug「這次碰到的檔」
- 觀測:對兩份 JSON 做鍵集合 diff | diff 為空、schema 字串相同算過 | 用本 repo 一份 + 產品 fixture 一份測(SC-6)
- Operational Context:不適用 — schema 對帳。

### R-6: 系統 SHALL 維持 Non-Goal 邊界
本 feat 不發明假 PreToolUse、不另寫第二套方法論、不改鬆既有 `--action` 圍欄、不另造 lockfile 當正本、不解凍 Stage 1–4 模板、不 bump plugin、不修 plugin cache、不把 dispatch-guard 搬到非 Claude。契約仍 `2.0.0`。

**審的時候看什麼**
看 `.cursor-plugin/plugin.json` 仍無 `hooks` 鍵;看七支該站腳本仍接 `--action`;看 `.claude-plugin/plugin.json` 版本列與契約字串。

#### S-6.1 不掛假 PreToolUse
- GIVEN 本 repo `.cursor-plugin/plugin.json` 與 Cursor session 工具軌跡
- WHEN 本 feat 的實作 hop 結束(本規格 hop 不改這些檔;本條鎖定實作後仍須成立)
- THEN `.cursor-plugin/plugin.json` 仍無 `hooks` 鍵;沒有新檔把 `hooks/hooks.json` 抄進 Cursor 薄殼;Write 工具在 Cursor 不假裝被 Claude PreToolUse 攔截
- 觀測:從 `.cursor-plugin/plugin.json` 鍵名看 | `hooks` 鍵不存在算過 | 讀本 repo 該檔(AC-5／SC-7)。n-a:Cursor 工具軌跡在本 repo 外,以 JSON 鍵為替代觀測
- Operational Context:
  - Actor:owner
  - Goal:不造假 hook
  - Situation:Cursor 薄殼只有 skills 鍵
  - Known information:現況 JSON
  - Missing information:無
  - Human decision:發現有人加 hooks 鍵就打回
  - Authority:owner
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:刪掉假掛載
  - Audit/handoff requirement:diff 不含新 hooks 鍵
  - Observation:見本條觀測

#### S-6.2 不改鬆 `--action`、契約仍 2.0.0
- GIVEN 七支該站腳本與 `.claude-plugin/plugin.json`、`hooks/runtime-capabilities.json`
- WHEN 搜各腳本是否仍含 `[ "${1:-}" = "--action" ]`,並讀契約欄
- THEN 七支都仍接 `--action`;本 feat 不刪、不改成可選、不讓 probe 代替;契約字串仍為 `2.0.0`;本 hop 與後續實作 hop 都不改 `.claude-plugin/plugin.json` 的 version 欄來「順便升版」
- 觀測:從七支腳本檔頭與契約 JSON 看 | 七處仍有 `--action` 字面、契約 `2.0.0` 算過 | `scripts/check-host-adapter.sh` 既有「不准改鬆」段 + 本 repo 契約檔
- Operational Context:不適用 — 圍欄回歸。

#### S-6.3 不修 cache、不解凍模板、不改 STATUS 表列
- GIVEN 本 feat 的 diff
- WHEN 列出變更檔
- THEN 不含現場 plugin cache 對齊(OC-4);不含 `_templates/1-discussion.md`／`2-decision.md`／`3-prototype.md`／`4-spec.md` 正文解凍改寫(本規格檔是 feature 產出,不是模板);feature branch 不含 `docs/dev/STATUS.md` 表列改動
- 觀測:從本 PR diff 檔名清單看 | 上列路徑不在實作範圍算過 | `git diff --name-only` 對本 branch
- Operational Context:不適用 — 範圍守衛。

## MODIFIED Requirements

本 repo `docs/specs/` 無 living spec 條文可引。guide `#host` 既有句(無 PreToolUse、誰開工誰先跑 `--action`、不准改鬆)本 feat **不改其禁令**,只要求 `--action` 增加鑄收據副作用;該副作用是 ADDED,不是改掉圍欄。故本節無條。

## REMOVED Requirements

無。

## 行為流程圖(R 級)
```
[R-1] 鑄出該站 --action 收據
[R-2] 核對收據並 fail-closed
[R-3] 寫出 I2 堆疊盤點
[R-4] 選配寫出 I4 摘要
[R-5] 共用同一盤點 schema
[R-6] 維持 Non-Goal 邊界
```

## Acceptance Criteria

打包驗收(對 SC-1..7 與討論 AC-1..5):

- 全 S 綠,且既有 `scripts/devflow-check.sh`／host-adapter／七站 `--action` 自檢回歸綠。
- SC-1／AC-1 ← S-2.5、S-2.6:非 Claude 宣稱可寫碼時,人能指出本次 script-minted receipt 在或不在;文案含「無 PreToolUse」與「`--action`」;不是只看到 start 成功。
- SC-2／AC-2 ← S-2.2、S-2.5:只跑 start、不跑該站 `--action` → 核對 exit ≠ 0 且含「未跑 `--action`」;不得出現「已與 Claude 同等武裝」。
- SC-3 ← S-2.3、S-2.4、S-2.7:手填／空白／缺 DONE／stamp 不符／slug 或 root 或 station／script 對不上不得算有效收據;`action:"verify_receipt"` 不是核對開關。
- SC-4／AC-3 ← S-3.1、S-3.2:I2 寫出語言名、runtime 版本、宣告 pin、直接相依;母版樣張對上 Python 3.9 地板與 `markdown-it-py==4.0.0`。
- SC-5／AC-4 ← S-3.3:本機 3.9、套件要 3.12+ 時,落差列在進 Stage 4 之前就在 I2。
- SC-6 ← S-5.1:方法包與產品專案同一 schema／同一深度。
- SC-7／AC-5 ← S-6.1、S-6.2、S-6.3:無假 PreToolUse;薄殼無 hooks 鍵;`--action` 未改鬆;契約 `2.0.0`;不修 cache;不解凍 Stage 1–4 模板。
- 非功能:收據與 I2 寫入用 `os.replace` 或同等原子覆寫;`.devflow/host-receipt/` 維持 gitignore(已在 `.gitignore` 的 `.devflow/` 下)。

## Out of Scope

與 Decision Scope & Non-Goals 對齊:

- 假 PreToolUse;把 `hooks.json` 抄進 Cursor／Grok／Codex。
- 第二套方法論;新的 `check-host-receipt.sh` 家族。
- 改鬆既有 `--action` 圍欄;讓 `--probe` 冒充執法。
- 另造 lockfile 當套件正本;I4 digest 當 lock 正本。
- 解凍並改 Stage 1–4 模板(I1)。
- 本 hop 與本 feat 實作 hop bump plugin。
- Grok marketplace／主機 SKU 表。
- 把 haiku–sonnet–opus dispatch-guard 搬到非 Claude。
- 本 feat 對齊現場 3.6.1 plugin cache(OC-4)。
- lock 全樹／transitive 盤點(D2)。
- per-slug／feature-scoped「這次 feat 碰到的檔」當 I2 深度(D1 在本檔收成專案第一層)。
- 把 `action:"verify_receipt"` 當成核對開關(只認布林 `verify_receipt:true`)。
- 每 slug 一份 `0-stack.md`。
- 在 Cursor Write 工具上發明機械擋(那是假 hook);本 feat 的牙是收據 + 核對。
- 密碼學防偽(stamp 防的是空檔／手填清單／改欄,不是對抗讀過規格的偽造者)。

## Diff Budget

本節是**估計**(給後續實作 hop,不是本規格 PR 的檔數)。超支本身非偏差,是停下判 L1/L2 的訊號。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| 七站 `--action` 鑄／核 + 共用 mint 函式 | ≤8 | ≤280 | ≤450 |
| I2 `dev-setup` 寫 `0-inventory.json` + 過期重寫 | ≤3 | ≤200 | ≤220 |
| I4 選配寫入(只在有人要求時) | ≤2 | ≤80 | ≤80 |
| 說明(`#host`／PLUGIN／setup 指引一句) | ≤3 | ≤80 | 0 |
| **合計** | **≤16** | **≤640** | **≤750** |

[Assumption] 係數按「一個 S 一到兩條測試」,未加 mutation。本規格 PR 本身只動 `docs/dev/host-stack-fit/4-spec.md` 與 twin html。

## Dependencies

- 既有該站 `--action` 腳本與 `--action` JSON(`cursor`／`action`／`slug`)—— justification:OC-1 沿用,不另造家族。核對只加可選布林 `verify_receipt`,不改 graph `action` 詞彙。
- `dev-setup` install／check／upgrade —— justification:I2 落點。
- `docs/PLUGIN.md`、`scripts/requirements-methodology-render.txt`、`scripts/check-py-floor.sh` —— justification:母版樣張與 #122 落差。
- 無新外部服務、無新 pip 套件、無 migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組(該站 `--action`／收據檔／`dev-setup`);③跨模組 Interface(收據 schema 與 I2 schema);⑧新增 Filesystem 寫入(`.devflow/host-receipt/`、`docs/dev/0-inventory.json`);⑨Feature Risk = high;⑩三個以上模組共同參與
- Design source: 既有 pattern —— 該站 `--action` allow／deny、`.devflow/` 本機狀態、`dev-setup` 寫 `docs/dev/`;收據與 I2 schema 是 new local design(Decision 只鎖「腳本鑄、缺則紅、I2 底 + I4 選配」)

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| 該站 `--action` 腳本(talk + stage2–7) | allow 時鑄收據;`verify_receipt:true` 時核對;既有 graph 圍欄不變 | **擁有**收據 JSON 的鑄造與 stamp | → `--action` payload、→ `.devflow/host-receipt/` | 不得呼叫 probe 冒充鑄造;不得改鬆 deny 規則;不得寫 lockfile;不得把 `action:"verify_receipt"` 當核對開關 |
| 主機收據檔(`.devflow/host-receipt/`) | 本機 session 證據;不進 Git | **擁有**當次 station+slug 的收據位元 | ← 該站腳本 | 產品碼與 I2 不得當收據正本 |
| `dev-setup` I2 | 寫／覆寫 `docs/dev/0-inventory.json` | **擁有**盤點欄位正本 | → pin／requirements 檔、→ `python3 --version` | 不得讀 I4 digest 回填版本;不得改 Stage 1–4 模板 |
| I4 `0-stack.md`(選配) | 投影 I2 + 可選 lock 指紋 | 不擁有套件版本 | → I2、→ lock／pin 檔位元 | 不得當 lock 正本;不得每 slug 一份 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| `--action` allow → mint | in:既有 `--action` JSON;out:正規路徑一份收據 | deny／exit 2 不鑄 | 單檔 `os.replace`;allow 與鑄檔同一次成功,鑄失敗則該次不得只回 allow 卻無檔 | 既有 allow／deny 字面與 exit 0／1／2 不變;只加副作用 |
| `--action` + `verify_receipt:true` | in:同腳本 JSON(graph `action` 仍為既有動詞);out:exit 0／≠ 0 | 缺檔／空／手填／stamp 錯／slug 三方不一／station／script 對不上／root ≠ 核對專案根 → exit ≠ 0 + `未跑 --action` | 只讀收據,不寫 | 唯一可選核對欄;缺欄=舊行為(只做 graph,不核收據)。不認 `action:"verify_receipt"` |
| `dev-setup` → I2 | in:pin 檔 + runtime;out:`0-inventory.json` | 缺 I2 → check 不得當成功 | 單檔覆寫;不與收據同交易 | 方法包／產品同一 schema |
| 選配 I4 | in:人要求 + I2;out:`docs/dev/0-stack.md` | 無 I2 不得先寫 I4 | I4 失敗不影响 I2 | 可缺席 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| mint 函式(七支腳本共用,住既有 check 檔或 `devflow-lib` 一函式) | allow 後寫收據 + stamp(輸入含 `root`) | ← graph evaluate;→ 收據路徑 | payload bytes → sha256 → JSON → replace | 寫失敗 → 該次不得假裝已鑄 | 暫存根跑 `--action` allow,斷言檔與 stamp(S-1.1／S-1.2) |
| verify 函式(同一支腳本) | 讀檔、重算 stamp(含 `root`)、咬 DONE、三方 slug、station／script、root | ← `--action` JSON 的 `verify_receipt:true` | 只讀 | 任何失敗 exit ≠ 0 | S-2.2～S-2.4／S-2.7 fixture |
| I2 writer(`dev-setup`) | 組 `languages`／pins／deps／gaps | ← pin 檔、`python3 --version` | 讀 pin → 寫 JSON | 缺來源就列 gap 或讓 check 紅 | S-3.2／S-3.3 母版樣張 |
| I4 writer(選配) | 抄 I2 + 可選 digest | ← I2、lock 檔 | 只投影 | 無 I2 拒絕寫 I4 | S-4.1／S-4.2 |

### Design Constraints
- 必須:沿用既有該站 `--action`;空檔 ≠ 有效;start 單獨 ≠ 武裝;stamp 含 `root`;核對只認 `verify_receipt:true`;I2 專案級 pin + 第一層 `direct_deps`;I4 選配且只有 `docs/dev/0-stack.md`;同一 schema。
- 禁止:假 PreToolUse;第二套檢查家族;改鬆 `--action`;I1 解凍模板;I3 寫 STATUS;digest 當 lock 正本;本 feat 修 cache;本 hop 升 plugin。
- Extension point:後續 feat 若要解凍 Stage 1 模板做 I1,須另開 slug 並先過 Q11。
- Known design limit:
  ① Cursor Write 工具沒有 hook,本 feat 不在編輯器層擋寫,只靠收據核對與「不得宣稱武裝」。
  ② stamp 不是對抗已讀規格者的密碼學防偽。
  ③ I2 不每條 feature 自動重跑;`git pull` 後套件可漂,直到人重跑 setup。
  ④ 間接相依仍可能晚爆(D1;本檔深度 = 專案級 pin + 第一層 `direct_deps`,不是 per-slug 碰到的檔)。

## Verification Profile(G2 一併審)
- lane: full(判準:新能力、新 schema、跨模組、新增 filesystem 寫入、改 `--action` 副作用契約;命中自動升 Full 的 filesystem／公開契約。owner 未要求降 fast;無偏離)
- Risk: high(判準:公開 `--action` 契約加鑄檔副作用;fail-closed 擋「已武裝」宣稱;新增 filesystem 寫入。不是金流／auth,但模板「公開 API／不可逆契約副作用」吃這條,故 high 不是 normal)
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得用 probe／start／write-cursor／write-scope 冒充鑄造(S-1.3)
  - 不得把空檔／手填／缺 DONE／slug 或 root 對不上當有效收據(S-2.2／S-2.3／S-2.4)
  - 不得把 `action:"verify_receipt"` 當核對開關(S-2.7)
  - 不得出現「已與 Claude 同等武裝」(S-2.2／S-2.5)
  - 不得強制每專案 I4(S-4.1)
  - 不得把 digest 當 lock 正本(S-4.3)
  - 不得加假 PreToolUse、不得改鬆 `--action`、不得解凍 Stage 1–4 模板、不得修 cache、不得 bump plugin(S-6.1～S-6.3)
- Required layers:check-spec-gate／check-host-adapter／七站 graph `--action` 自檢／devflow-check
- Conditional layers:Supply chain — 當本 feat 實作改到 pin／requirements 檔時,重跑 I2 寫入並對帳 S-3.4
- Explicitly excluded layers:Mutation(本 hop 只規格,實作後方法包也未把 mutation 列為本 feat 必跑)、e2e／Playwright(無產品前端)、Race／stress(單 writer 覆寫,無新併發契約)
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/host-stack-fit/4-spec.md && bash scripts/check-host-adapter.sh && bash scripts/devflow-check.sh`
- Reliability triage:
  - Concurrency: n-a — 單一 session 對同一 station+slug 寫一份收據;後鑄覆寫前鑄;無多 writer 契約
  - Idempotency: applicable — 同一 station+slug 再 allow 覆寫同一路徑;再 `verify_receipt` 仍接受最新有效 stamp(S-1.4／S-2.1)
  - Timeout/retry: n-a — 本機檔案、無外呼;核對紅了由人重跑 `--action`,不自動重試

Human verdict: N/A

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 只跑 start 卻宣稱已武裝 | 假安全感,非 Claude 靜默漂移 | `verify_receipt` 綠或文案含「同等武裝」 | Required:host-adapter + S-2.5 | — |
| 空檔／手填被當成收據 | 條件 C 牙沒了(C08／B) | 空檔或 md 清單核對 exit 0 | Required:S-2.2／S-2.3 | — |
| 換 slug／換 root 仍核對綠 | 收據可搬到別專案或別 feat 冒充 | `receipt.slug` 或 `receipt.root` 對不上仍 exit 0 | Required:S-2.4 | — |
| `action:"verify_receipt"` 被當成核對 | 雙鍵／fail-open,缺布林仍進 verify | 無 `verify_receipt:true` 卻 verify-only | Required:S-2.7 | — |
| probe 鑄收據或代替 `--action` | 重演 #78 第四型假綠 | `--probe` 後出現 host-receipt JSON | Required:S-1.3 | — |
| `--action` 圍欄被改鬆 | 無 hook 主機可跳過 graph | 七支腳本不再接 `--action` | Required:host-adapter 第三刀 + S-6.2 | — |
| I2 漏 pin 或漏落差 | #122 再現,進 Stage 4 才爆 | 母版 I2 無 `markdown-it-py==4.0.0` 或 3.9 vs 3.12 gap | Required:S-3.2／S-3.3 | — |
| I4 digest 被當成 lock 正本 | 雙源漂 | 實作把 digest 寫回 pin | Required:S-4.3 | — |
| Cursor Write 無 hook 仍寫入 | 人跳過核對仍能改檔 | 編輯器寫入成功 | 明示 Known limit ①;用 S-2.6 核對指令替代 | 不在編輯器層擋(禁假 hook) |

## Drafting Decisions(草擬自判,已核)

形狀已寫進 R/S,本表只記 Stage 2 沒釘死、由本檔綁定的選擇。不翻 Decision。2026-09-10 多代理人審查收斂 DD-1／DD-2／DD-3 三處(見頂註 HISTORY),owner 核准。G2 PASS by owner on 2026-09-10 (UTC+8);DD-1～DD-5 ✅。

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | KEEP 路徑 = `.devflow/host-receipt/<slug>/<station>.json`、schema = `devflow-host-receipt/v1`、七站 `--action` allow 才鑄。TIGHTEN:stamp 輸入必須含專案 `root`;核對必須 `receipt.slug`==路徑 slug==`--action` slug、`receipt.station`／`script` 對上呼叫腳本、`receipt.root`==核對時專案根。仍非密碼學防偽;不新開 `check-host-receipt.sh` | Decision 只鎖腳本鑄、可核對、不可手填;路徑與 schema 沿用。多代理人審查要求 stamp／核對綁 `root` 與三方 slug,避免收據搬家仍綠 | `2-decision.md` Risks「欄位／檔名進 4-spec」;`.gitignore` 已忽略 `.devflow/`;owner 2026-09-10 核准包 | 改路徑則 S-1.1／SC-1 觀測點全改;拿掉 root 綁定則 S-1.2／S-2.4 紅案消失 | ✅ |
| DD-2 | 核對開關**只有**可選欄 `verify_receipt:true`(布林)。true = 只核對不鑄;缺欄 = 舊 graph。不接受 `action:"verify_receipt"` 當第二把鑰匙。不新開腳本 | OC-1 禁止第二套檢查家族。雙鍵會 fail-open(有人只寫 `action` 字串就當核對)。多代理人審查收斂為布林唯一 | `2-decision.md` OC-1;owner 2026-09-10 核准包 | 若改獨立 `check-*.sh` 要重審 G4／第二方法論;若再加第二把鑰匙,S-2.7 要重寫 | ✅ |
| DD-3 | I2 路徑 = `docs/dev/0-inventory.json`;schema = `devflow-stack-inventory/v1`;深度 = **專案級**宣告 pin + 來自 pin／requirements 的第一層 `direct_deps`。不是 per-slug「這次 feat 碰到的檔」;不是 lock 全樹／transitive | 要進 Git、fast 也看得到、與選配 I4 `0-stack.md` 分開。Decision D1 鎖「宣告 pin + 直接相依、不做全樹」;「本次碰到」若讀成 feature-scoped 會漂,本檔把深度釘在專案第一層 | `2-decision.md` I2 專案級、D1;OC-2 只鎖 I4 檔名;owner 2026-09-10 核准包 | 改檔名則 SC-4／SC-5 觀測點改;改成 per-slug 或 lock 全樹則 S-3.1／S-3.2／S-5.1 與 D2 邊界翻 | ✅ |
| DD-4 | Stage 3 由 owner 2026-09-09 跳過,記在本檔;不回改正本 Decision 組合包 | 使用者本 hop 明示;Decision 組合包(H1+C／I2+I4)不因此翻案 | 本 hop owner 指示;2-decision 下層「不預先跳過」是 Stage 2 當時句 | 若改要補 3-prototype,本節對帳改寫 | ✅ |
| DD-5 | Feature Risk = high;`verdict: PASS` 由 owner G2 填入,非 agent 代填 | `--action` 契約副作用 + fail-closed + filesystem;G2 是人審 | `_templates/4-spec.md` Risk 判準;owner G2 PASS 2026-09-10 (UTC+8) | 改 normal 則 Failure Model 可改選配 | ✅ |

### 內部技術選擇(下層,告知即可)
- station 檔名:`talk.json`／`stage2.json`…`stage7.json`,對應七支既有 graph 腳本。
- stamp 輸入用 `|` 串接且必須含專案 `root`,小寫 hex;防空檔、手填與改欄,不是密碼學防偽。
- 核對只認 `verify_receipt:true`;不認 `action:"verify_receipt"`。
- I2 `direct_deps` = 專案 pin／requirements 第一層,不是 per-slug「這次改到的檔」,也不是 lock 全樹。
- 本 hop 不改 hooks／skills 正文。
- 審頁 html 用 `scripts/build-stage4-html.py --action`(生命週期直式 SVG);與本 feat Stage 2 的 `build-stage2-html.py` 同一家族。

## Test Skeletons(選配)

- `test_s_1_1_station_action_mints_receipt`
- `test_s_1_2_receipt_fields_and_stamp`
- `test_s_1_3_probe_start_cursor_scope_do_not_mint`
- `test_s_2_2_missing_empty_blank_receipt_fails`
- `test_s_2_3_handfilled_or_string_done_fails`
- `test_s_2_4_stamp_slug_station_script_root_mismatch_fails`
- `test_s_2_5_start_only_not_armed`
- `test_s_2_7_action_verify_receipt_is_not_a_switch`
- `test_s_3_2_pack_pins_markdown_it_py`
- `test_s_3_3_gap_39_vs_312_before_stage4`
- `test_s_4_1_setup_does_not_require_i4`
- `test_s_5_1_pack_and_product_same_keys`
- `test_s_6_1_cursor_plugin_has_no_hooks_key`

## Stage 3 對帳

整節 N/A。無 `3-prototype.md`,無 ACCEPTED Demo 場景。Owner 2026-09-09 跳過 Stage 3,理由:Decision 已夠清楚,不需原型。操作下落寫在各重要 S 的 Operational Context(S-1.1、S-2.1、S-2.5、S-2.6、S-3.1、S-3.3、S-3.4、S-4.1、S-4.2、S-6.1)。S-2.7 為開關鍵邊界,無人員交接。

## 確認紀錄
- 雙源清點 | 2026-09-09 | 驗收雛形 AC-1..5 共 5 條;living spec `docs/specs/` 0 條可引 → 全數 ADDED。1-discussion 雛形觀測欄已升進對應 S
- R 範圍 | 2026-09-09 | owner Stage 4 brief 鎖:收據形狀、I2 欄位與刷新、I4 選配、Non-Goal、SC-1..7。本 hop 雲端一次落檔,對應該鎖板
- S 展開 | 2026-09-09 | R-1..R-6 全展開;每 S 有觀測欄;重要 S 有 Operational Context
- 3a 四節 | 2026-09-09 | AC／Out of Scope／Diff Budget／Dependencies 齊
- 3b Profile | 2026-09-09 | lane full、Risk high、Failure Model、Reliability triage、Design Boundary applicable
- 3c Stage 3 | 2026-09-09 | N/A + owner 跳過(Decision 已夠清楚,不需原型)
- DD 掃描 | 2026-09-09 | 上層五條當時待人審;形狀綁在 R/S
- G2 verdict | 2026-09-09 | 當時留空,留給人類,不代填 PASS
- 多代理人收斂 | 2026-09-10 | owner 核准三處,不翻 H1+C／I2+I4 Decision:DD-1 stamp 綁 `root` + 核對三方 slug／station+script／root;DD-2 只認布林 `verify_receipt:true`;DD-3 深度 = 專案級 pin + 第一層 `direct_deps`
- G2 PASS | 2026-09-10 | G2 PASS by owner on 2026-09-10 (UTC+8). DD-1～DD-5 ✅。owner 自審(有記錄);reviewers: [user]
