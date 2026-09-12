---
feature: diagram-ir-gate
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-12
---

# 4. 規格 — 圖表 IR 閘（Archify absorb wave-1）

> 基準:`main` tip `9877652`（#218 Stage 3 Human ACCEPTED）。契約不 bump。本 hop **只 Stage 4**：`4-spec.md` + gate-twin／審頁 html。`verdict` 留空；**不代填 G2 PASS**。不開 Stage 5、不改 `scripts/` 正本產器、不碰 `#196`、不改 `integration-before-verdict`、不發版、不收 Mermaid／Node／動畫。
> Decision 正本:`docs/dev/diagram-ir-gate/2-decision.md`（A + D + G；OC-1～OC-4 ✅；G1 `verdict` PASS）。Stage 3 Human ACCEPTED（`human:rick @ 2026-09-12`）。本檔把 Decision 留給 4-spec 的信封／索引檔名／寫檔抽點鎖進 R/S/DD。
> IMPLEMENTER B 獨立編碼。不翻已核 Decision。不把 Stage 3 throwaway 當正式產器。

## 補助模組生命週期（預覽）

主詞是「圖表寫路徑上的共用 IR 閘」,不是整份畫法契約。直式圖,置中。
- 新生（這輪沒有）：不加第二套 Proof Lab 檢查語言；不加 mermaid／Node 渲染引擎。
- 改行為（相關一格）：四支圖表寫檔改走 typed IR → 驗證 → `atomic_write`；失敗給 `DIAGIR_*` + 旋鈕；目標停在 last-good。五家族查找路由表。既有 fixture + 薄索引當 Proof Lab。
- 退役：沒有。
- 不動：vbox-fig／dir-tree／stage1／stage2「何時不用」原文；#191 樹狀 WARNING+`<pre>`；`#196`；plugin 版本；Mermaid／Node／動畫預設。

## ADDED Requirements

### R-1: 系統 SHALL 在 IR 驗證失敗時保住 last-good 並輸出穩定碼
承接 AC-1／SC-1／SC-5。目標檔已有一張通過驗證的 html／svg 時，再餵會觸發 `DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`／`DIAGIR_EMPTY`／`DIAGIR_LINES` 的信封，目標位元組必須與餵入前相同。stderr 或收據物件必須含該穩定碼（字面 `DIAGIR_` 前綴）與一句非空旋鈕，且必須另含 `DIAGIR_ABORT`。不得只印 Python traceback 就結束。

**審的時候看什麼**
看目標檔 sha256 與 stderr／收據的碼字面，不是看 exit 非 0。exit 非 0 但檔已被換掉 = 本 R 失敗。

#### S-1.1 parked kind 必須保住 last-good
- GIVEN 目標檔 `target.svg` 位元組等於 last-good 靜態 SVG（sha256 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc` 或本測先寫入的同等種子），且信封 `family`=`vbox-lifecycle`、`payload.steps[0].kind`=`parked`、其餘三步 `kind` 為 `b`
- WHEN 把該信封交給 wave-1 IR 閘的 deliver（驗證後才准寫檔）
- THEN 目標檔 sha256 與餵入前相同；stderr 或收據 JSON 含字面 `DIAGIR_KIND`；同一輸出含非空旋鈕句；同一輸出含字面 `DIAGIR_ABORT`；輸出不含 `Traceback (most recent call last)`
- 觀測:從目標檔 `sha256sum` 與 deliver 的 stderr／stdout JSON 看 | 三個字面碼／旋鈕都在且 sha 不變算過 | 用 Stage 3 `kind-parked` 同形信封測
- Operational Context:
  - Actor:開工 agent
  - Goal:壞 IR 不得蓋掉上一張可審圖
  - Situation:剛產過一張綠的生命週期 SVG，又餵了 `parked` kind
  - Known information:路由列 `vbox-lifecycle`；vbox 允許 kind 只有 `b`／`hl`／`wn`
  - Missing information:無
  - Human decision:依旋鈕改 kind 或改選家族後重跑
  - Authority:閘機械拒寫；人改信封
  - External dependency:本機檔案系統
  - Out-of-system action:在終端機重跑 deliver
  - Waiting/timeout behavior:驗證失敗即停；目標停在 last-good，直到下一次通過的 deliver
  - Recovery:把 kind 改回 `b`／`hl`／`wn` 後重跑；不要 `git checkout` 舊 html
  - Audit/handoff requirement:收據留下 `DIAGIR_KIND` + `DIAGIR_ABORT`
  - Observation:見本條觀測

#### S-1.2 樹狀當 vbox 必須保住 last-good
- GIVEN 同一顆 last-good 目標檔，信封 `family`=`vbox-lifecycle`（或 `behavior-flow`），`payload` 含樹狀 ASCII（字面 `|--` 或 `├` 或 `└`，或 `kind`=`tree-ascii`）
- WHEN 把該信封交給同一支 deliver
- THEN 目標 sha256 不變；輸出含字面 `DIAGIR_FAMILY`、非空旋鈕、`DIAGIR_ABORT`；不含 traceback 標頭
- 觀測:從目標 sha 與輸出字面看 | sha 不變且三個字面都在算過 | 用 Stage 3 `tree-as-vbox` 同形信封測
- Operational Context:
  - Actor:開工 agent
  - Goal:選錯家族時停寫，而不是把樹收成單盒
  - Situation:把 gate-twin 樹狀 ASCII 當生命週期／行為流 vbox
  - Known information:路由表「不用那條」寫明樹不收單盒
  - Missing information:無
  - Human decision:改呼叫 `build-gate-twin.py` 的樹狀後備，或改成直式 `[R-n]` 步驟
  - Authority:閘給 `DIAGIR_FAMILY`
  - External dependency:無
  - Out-of-system action:查路由表後改產器
  - Waiting/timeout behavior:同 S-1.1
  - Recovery:改 `family` 或改 payload 形狀後重跑
  - Audit/handoff requirement:收據含 `DIAGIR_FAMILY`
  - Observation:見本條觀測

#### S-1.3 短 why 必須保住 last-good
- GIVEN 同一顆 last-good 目標檔，信封 `family`=`dir-tree`，某個節點 `why` 去掉空白後長度 &lt; 12（對齊 `scripts/build-dir-tree.py` `why_ok` 地板）
- WHEN 把該信封交給同一支 deliver
- THEN 目標 sha256 不變；輸出含字面 `DIAGIR_WHY`、非空旋鈕、`DIAGIR_ABORT`
- 觀測:從目標 sha 與輸出字面看 | sha 不變且 `DIAGIR_WHY` 在算過 | 用 `scripts/fixtures/dir-tree/missing-why/purpose.yaml` 或 Stage 3 `dir-short-why` 測
- Operational Context:
  - Actor:開工 agent
  - Goal:缺 why 的目錄樹不得蓋掉上一張 dir-tree.html
  - Situation:YAML 有節點 why=`短`
  - Known information:地板 = 12 字
  - Missing information:該節點的一句到兩句 why
  - Human decision:在 YAML 補 why 後重跑
  - Authority:閘給 `DIAGIR_WHY`；既有 `check-dir-tree.sh` 短 why 仍紅
  - External dependency:手寫 purpose YAML
  - Out-of-system action:編輯 YAML
  - Waiting/timeout behavior:同 S-1.1
  - Recovery:why 長度 ≥12 後重跑
  - Audit/handoff requirement:收據含 `DIAGIR_WHY`
  - Observation:見本條觀測

#### S-1.4 空標題必須保住 last-good
- GIVEN 同一顆 last-good 目標檔，信封 `family`=`vbox-lifecycle`，某步 `title` 為 `""` 或只含空白
- WHEN 把該信封交給同一支 deliver
- THEN 目標 sha256 不變；輸出含字面 `DIAGIR_EMPTY`、非空旋鈕、`DIAGIR_ABORT`
- 觀測:從目標 sha 與輸出字面看 | sha 不變且 `DIAGIR_EMPTY` 在算過 | 用 Stage 3 `empty-title` 同形信封測
- Operational Context:不適用 — 同 S-1.1 交接；本條只換觸發碼。

#### S-1.5 四行 lines 必須保住 last-good
- GIVEN 同一顆 last-good 目標檔，信封 `family`=`vbox-lifecycle`，某步 `lines` 為四個非空字串
- WHEN 把該信封交給同一支 deliver
- THEN 目標 sha256 不變；輸出含字面 `DIAGIR_LINES`、非空旋鈕、`DIAGIR_ABORT`
- 觀測:從目標 sha 與輸出字面看 | sha 不變且 `DIAGIR_LINES` 在算過 | 用 Stage 3 `four-lines` 同形信封測
- Operational Context:不適用 — 同 S-1.1 交接；本條只換觸發碼。

#### S-1.6 六碼皆須可單獨觸發且帶旋鈕
- GIVEN Decision OC-1 鎖死的六碼：`DIAGIR_KIND`、`DIAGIR_EMPTY`、`DIAGIR_LINES`、`DIAGIR_FAMILY`、`DIAGIR_WHY`、`DIAGIR_ABORT`
- WHEN 分別跑 S-1.1～S-1.5 的失敗信封，以及任一失敗案的 abort 欄
- THEN 六個字面各至少出現一次；每個失敗案的旋鈕句長度 ≥1 且不是 traceback 標頭
- 觀測:從六次輸出的 `code`／`abort` 欄聯集看 | 聯集恰好含這六個字面（可多印 `DIAGIR_ABORT`）算過 | 用 Stage 3 `CODES_SEEN` 同形電池測
- Operational Context:不適用 — 碼表回歸，無新的人員交接。

### R-2: 系統 SHALL 以 tmp 加 os.replace 原子交付通過驗證的產出
承接 AC-2／SC-2／OC-3。驗證通過後的寫入要嘛全新、要嘛全舊。中斷或失敗後目標不是截斷 html／svg。原子原語沿用既有 `tmp + os.replace` 形狀，抽到共用幫手；不另造第三套寫檔演算法。

**審的時候看什麼**
通過時目標變成完整新檔；模擬中斷只留截斷 `.tmp`，目標 sha 仍是 last-good。

#### S-2.1 通過的生命週期 IR 必須整份換新
- GIVEN 目標檔已是 last-good 種子，信封來自 `scripts/fixtures/vbox-fig/lifecycle.json` 且 `family`=`vbox-lifecycle`
- WHEN 把該信封交給 deliver
- THEN 目標檔存在、長度大於種子、內容含 `<svg`；檔內不含字面 `mermaid`；收據 `ok`=true 且 `delivered`=true；目標 sha256 ≠ 種子 sha256
- 觀測:從目標檔原文與收據 JSON 看 | 有 svg、無 mermaid、sha 變了算過 | 用 Stage 3 `pass-lifecycle` 測
- Operational Context:
  - Actor:產檔器
  - Goal:綠 IR 換成可審的靜態直式 SVG
  - Situation:驗證已通過，準備寫檔
  - Known information:信封 family 與 payload 已過閘
  - Missing information:無
  - Human decision:打開新檔審圖
  - Authority:閘在驗證後呼叫共用 `atomic_write`
  - External dependency:本機檔案系統
  - Out-of-system action:瀏覽器打開產出
  - Waiting/timeout behavior:寫入同步結束；無重試迴圈
  - Recovery:寫入失敗走 S-2.2／S-2.3，不把半檔當成功
  - Audit/handoff requirement:收據 `delivered`=true
  - Observation:見本條觀測

#### S-2.2 中斷必須只留截斷 tmp
- GIVEN 目標檔已是 last-good，工作目錄將寫 `target.svg.tmp`
- WHEN 模擬寫入中斷：只把截斷字串 `<svg viewBox` 寫進 `target.svg.tmp`，不呼叫 `os.replace`
- THEN `target.svg` sha256 仍等於 last-good；`target.svg.tmp` 存在且位元組數 &lt; 20；目標檔原文不是截斷 html
- 觀測:從兩路徑的 `sha256sum`／`wc -c` 看 | 目標 sha 不變且 tmp 截斷算過 | 用 Stage 3 `INTERRUPT` 同形步驟測
- Operational Context:
  - Actor:產檔器
  - Goal:看見的要嘛全新、要嘛全舊
  - Situation:寫 tmp 時行程被停
  - Known information:last-good 仍在目標路徑
  - Missing information:無
  - Human decision:修環境後重跑；不要把 `.tmp` 改名當成品
  - Authority:未 `replace` 則目標不變
  - External dependency:OS
  - Out-of-system action:刪截斷 `.tmp` 後重跑
  - Waiting/timeout behavior:無自動重試
  - Recovery:重跑完整 deliver
  - Audit/handoff requirement:目標 sha 可對 last-good
  - Observation:見本條觀測

#### S-2.3 驗證失敗不得留下半份新目標
- GIVEN S-1.1 的失敗信封與已存在的 last-good 目標
- WHEN deliver 回傳失敗
- THEN 目標路徑上的檔案位元組與餵入前逐字相同；不得在目標路徑寫入長度介於 1 與 last-good 長度之間、且開頭為 `<svg` 卻無閉合 `</svg>` 的新內容
- 觀測:從目標檔前後 `cmp` 看 | 位元組全同算過 | 用任一 S-1 失敗案測
- Operational Context:不適用 — 與 S-1.1 同一失敗路徑，只加「不是半檔」斷言。

### R-3: 系統 SHALL 用一張五列查找表路由圖家族
承接 AC-3／SC-3／Decision D。人／agent **先選家族**，再跑該列產器。表不是黑盒自動排版，不是 mermaid，不是一支 API 吃五族。五列必須能指回 Context 已核契約。錯家族 payload 走 `DIAGIR_FAMILY`。

**審的時候看什麼**
表五列都有「用這條／不用那條／產器／契約」。三個錯家族信封都是 `DIAGIR_FAMILY`。五個現況入口只能落到自己那列。

#### S-3.1 路由表必須正好五列且欄位齊
- GIVEN Decision D 定稿五列與 Stage 3 `ROUTE` 五個 `id`：`stage1-now`、`stage2-arch`、`behavior-flow`、`dir-tree`、`vbox-lifecycle`
- WHEN 讀 wave-1 路由表契約（本檔 DD-2 鎖的資料結構，落地後由產器或索引載入）
- THEN 列數 = 5；每個 `id` 出現一次；每列都有非空的 `use`、`dont`、`builder`、`contract` 四欄
- 觀測:從表的列數與四欄字串看 | `len==5` 且無空欄算過 | 用 Stage 3 `ROUTE_ROWS 5`／`ROUTE_COUNT_OK` 同形傾印測
- Operational Context:
  - Actor:開工 agent
  - Goal:先查表再組 IR，不要就近抄最近產器
  - Situation:要畫五族之一
  - Known information:本表五列
  - Missing information:無（表是查找契約）
  - Human decision:選一列 `id`，填進信封 `family`
  - Authority:人／agent 選；機器不猜
  - External dependency:各列契約檔
  - Out-of-system action:打開契約核「何時不用」
  - Waiting/timeout behavior:無
  - Recovery:選錯 → `DIAGIR_FAMILY`，改 `family` 或改產器
  - Audit/handoff requirement:PR 或收據能指出用了哪一列
  - Observation:見本條觀測

#### S-3.2 三框當生命週期必須 DIAGIR_FAMILY
- GIVEN 信封 `family`=`vbox-lifecycle`，`payload` 帶 Stage 1 三框形（`boxes`=3 或 `kind`=`stage1-now` 或 `scan_now`=true）
- WHEN 交給同一支 deliver
- THEN `ok`=false；`code`=`DIAGIR_FAMILY`；目標若已有 last-good 則 sha 不變
- 觀測:從收據 `code` 與目標 sha 看 | 碼字面相符且 sha 不變算過 | 用 Stage 3 `stage1-as-lifecycle` 測
- Operational Context:
  - Actor:開工 agent
  - Goal:不要把第 1 站三框畫成生命週期四格
  - Situation:抄了 vbox-fig 產器去畫 `#scan-now`
  - Known information:路由列 `stage1-now` 的產器是 `build-stage1-html.py --action`
  - Missing information:無
  - Human decision:改呼叫 stage1 產器
  - Authority:閘
  - External dependency:無
  - Out-of-system action:改命令
  - Waiting/timeout behavior:同 S-1.1
  - Recovery:改 `family`=`stage1-now` 或改產器
  - Audit/handoff requirement:收據 `DIAGIR_FAMILY`
  - Observation:見本條觀測

#### S-3.3 目錄樹收單盒必須 DIAGIR_FAMILY
- GIVEN 信封 `family`=`vbox-lifecycle`（或 `behavior-flow`），`payload` 是 dir-tree 根物件（含 `why` 子樹）或 `kind`=`dir-tree`
- WHEN 交給同一支 deliver
- THEN `ok`=false；`code`=`DIAGIR_FAMILY`；last-good 保住
- 觀測:從收據與目標 sha 看 | `DIAGIR_FAMILY` 且 sha 不變算過 | 用 Stage 3 `dir-as-vbox` 測
- Operational Context:
  - Actor:開工 agent
  - Goal:目錄樹走 `build-dir-tree.py`，不收成單盒 vbox
  - Situation:把 purpose YAML 當 vbox steps
  - Known information:路由列 `dir-tree`
  - Missing information:無
  - Human decision:改呼叫 dir-tree 產器
  - Authority:閘
  - External dependency:手寫 YAML
  - Out-of-system action:改命令
  - Waiting/timeout behavior:同 S-1.1
  - Recovery:改 `family`=`dir-tree`
  - Audit/handoff requirement:收據 `DIAGIR_FAMILY`
  - Observation:見本條觀測

#### S-3.4 五個現況入口只能落到自己那列
- GIVEN 五個現況入口與對應 `id`：`build-stage1-html.py`→`stage1-now`；`build-stage2-html.py`→`stage2-arch`；`build-gate-twin.py` 行為流→`behavior-flow`；`build-dir-tree.py`→`dir-tree`；`build-vbox-fig.py` lifecycle→`vbox-lifecycle`
- WHEN 查路由表該列的 `builder` 欄
- THEN 每個入口的檔名（或 `--action` 標）出現在自己那列、不出現在其他四列當「用這條」產器
- 觀測:從五列 `builder` 字串看 | 五個檔名各出現一次、無交叉佔「用這條」算過 | 用本檔 DD-2 表與 tip 產器檔名測
- Operational Context:不適用 — 表對帳，無人員交接。

### R-4: 系統 SHALL 用薄索引重放 Proof Lab 且對齊現有牙
承接 AC-4／SC-4／OC-2。Proof Lab = 既有 `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}` + 一份薄索引。vbox-fig／gate-twin／dirmap 各至少一正一負可獨立重放。負向 exit ≠ 0 且不蓋 last-good。不是「只有 `lifecycle.json` 綠過」。不另造第二套檢查語言。

**審的時候看什麼**
索引六列都點名路徑；三個負向紅且 last-good 在；沒有新的 `check-proof-lab.sh` 當唯一牙。

#### S-4.1 索引檔必須在鎖定路徑且六列齊
- GIVEN 鎖定路徑 `scripts/fixtures/diagir-proof-lab.json`（DD-3）
- WHEN 讀該 JSON 的 `rows` 陣列
- THEN 正好 6 列，`id` 為 `vbox-fig/pos`、`vbox-fig/neg`、`gate-twin/pos`、`gate-twin/neg`、`dir-tree/pos`、`dir-tree/neg`；每列有 `family`、`want`（`pass` 或 `fail`）、`path`
- 觀測:從該 JSON 的 `rows` 長度與 `id` 集合看 | 長度 6 且六個 id 齊算過 | 用 Stage 6 落地後的索引檔測；本 hop 不造該檔
- Operational Context:
  - Actor:owner／審查人
  - Goal:重放樣張時知道去哪裡找
  - Situation:要跑 Proof Lab
  - Known information:三個既有 fixture 目錄
  - Missing information:vbox-fig 正式負例檔（Stage 6 才補 `kind-parked.json`）
  - Human decision:接受薄索引，不另開 `scripts/proof-lab/`
  - Authority:OC-2
  - External dependency:既有牙 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree`
  - Out-of-system action:在終端機重放
  - Waiting/timeout behavior:無
  - Recovery:缺列就補索引，不新寫檢查語言
  - Audit/handoff requirement:索引進 Git
  - Observation:見本條觀測

#### S-4.2 三家族正向必須可重放通過
- GIVEN 索引三列 `want`=`pass`：vbox-fig→`scripts/fixtures/vbox-fig/lifecycle.json`；gate-twin→`scripts/fixtures/gate-twin/fig-long-label`（直式行為流既有樣張）；dir-tree→`scripts/fixtures/dir-tree/good`
- WHEN 各列以對應 `family` 組信封跑 deliver 或該家族既有牙
- THEN 三列皆 `ok`=true 或既有牙 exit 0
- 觀測:從三列 exit／`ok` 看 | 三個都通過算過 | 用索引點名的三個既有路徑測
- Operational Context:不適用 — 正向重放，無新交接。

#### S-4.3 三家族負向必須紅且不蓋 last-good
- GIVEN 目標已有 last-good；索引三列 `want`=`fail`：vbox-fig→`scripts/fixtures/vbox-fig/kind-parked.json`（檔未落地前可用與 Stage 3 相同的 scratch `parked` 信封，但宣稱 Lab 完成前必須有該檔）；gate-twin→`scripts/fixtures/gate-twin/fig-tree-ascii`；dir-tree→`scripts/fixtures/dir-tree/missing-why`
- WHEN 各列跑 deliver
- THEN 三列皆 `ok`=false；vbox-fig 負向 `code`=`DIAGIR_KIND`；gate-twin 負向 `code`=`DIAGIR_FAMILY`；dir-tree 負向 `code`=`DIAGIR_WHY`；三列之後目標 sha256 仍是 last-good
- 觀測:從三列 `ok`／`code` 與目標 sha 看 | 三紅、三碼、sha 不變算過 | 用 Stage 3 `LAB` 六列的三個 `/neg` 同形測
- Operational Context:
  - Actor:審查人
  - Goal:負向紅了檔還在
  - Situation:重放負向樣張
  - Known information:last-good sha
  - Missing information:無
  - Human decision:負向紅且檔在才算 Lab
  - Authority:閘
  - External dependency:既有／Stage 6 負例檔
  - Out-of-system action:跑索引列
  - Waiting/timeout behavior:無
  - Recovery:若負向綠或檔被蓋，本 R 未完成
  - Audit/handoff requirement:Lab 輸出含 `neg_held=true` 或同等 sha 不變
  - Observation:見本條觀測

#### S-4.4 不得另造 Proof Lab 檢查語言
- GIVEN 本 slug wave-1 完成宣稱
- WHEN 搜 `scripts/check-proof-lab.sh` 與 `scripts/proof-lab/`
- THEN 兩路皆不存在；重放入口仍是既有 `scripts/check-vbox-fig.sh`、`scripts/check-gate-twin.sh`、`scripts/check-dir-tree.sh` 加 IR 閘（索引只點名，不發明新 exit 契約家族）
- 觀測:從 `test -e` 與 `rg -l 'Proof Lab' scripts/check-*.sh` 看 | 無新 `check-proof-lab.sh`、無 `scripts/proof-lab/` 目錄算過 | 用本 repo `scripts/` 樹測
- Operational Context:不適用 — 目錄／檔名契約。

### R-5: 系統 SHALL 維持預設圖為靜態直式 SVG
承接 AC-5／SC-6。wave-1 成功條件不是動畫、不是 mermaid.js、不是 Node render／hosted share。本 slug 不改 `#196`、不 bump plugin。

**審的時候看什麼**
綠交付的檔是靜態 `<svg>`；repo 的預設圖路徑沒有 mermaid.js；plugin 版本字面仍是 tip 的 `3.23.3`。

#### S-5.1 綠交付不得含 mermaid
- GIVEN S-2.1 通過後的目標檔
- WHEN 讀該檔全文
- THEN 含 `<svg`；不含字面 `mermaid`；不含 `<script` 指向 mermaid CDN 或 `mermaid.min.js`
- 觀測:從目標檔 `rg -n 'mermaid|<script' ` 看 | `<svg` 在且 mermaid／script 零命中算過 | 用 S-2.1 產出測
- Operational Context:不適用 — 檔案字面。

#### S-5.2 成功條件不得改成要會動
- GIVEN 本 slug `docs/dev/diagram-ir-gate/` 已提交的 1～4 過程檔
- WHEN 搜「動畫當預設」作為本 slug 成功條件、或把 `autoplay`／`animate` 列為 Acceptance Criteria 通過條件
- THEN 零命中（Rejected／Out of Scope／Q8 移交後刀的句子不算成功條件）
- 觀測:從 `rg -n '動畫當預設|autoplay' docs/dev/diagram-ir-gate/` 看 | 若命中，該行必須在拒項／後刀，不得在 Acceptance Criteria 當通過條件算過 | 用本目錄現檔測
- Operational Context:不適用 — 過程檔字面。

#### S-5.3 本 slug 不得改 196 與 plugin 版本
- GIVEN tip `.claude-plugin/plugin.json` 的 `version` 與開著的 `#196`
- WHEN 看本 feature branch 對這兩處的 diff
- THEN `plugin.json` 的 version 字面仍為 `3.23.3`；本 PR 不含對 `#196` 目標檔的行為改動
- 觀測:從 `git diff origin/main -- .claude-plugin/plugin.json` 與本 PR 檔清單看 | plugin diff 空、檔清單無 #196 產物算過 | 用本 branch 對 tip 的 diff 測
- Operational Context:不適用 — Non-Goal 邊界。

### R-6: 系統 SHALL 把圖表產品寫檔接到同一閘
承接 2-decision Risk「`write_text` 繞過閘」與 Stage 3 回寫「正式產器未接」。未接閘不得宣稱 wave-1 完成。vbox-fig 本身只寫 stdout；呼叫端寫檔也要先過閘。

**審的時候看什麼**
四支產品寫檔不再對產品目標直呼 `Path.write_text`／自寫非原子覆寫。wave-1 完成宣稱必須能指出閘入口。

#### S-6.1 四支產品寫檔必須改走閘
- GIVEN 四支產品寫檔：`scripts/build-dir-tree.py`（`write_text`／`Path.write_text`）、`scripts/build-gate-twin.py`（`out_local.write_text`）、`scripts/build-stage1-html.py`（`dest.write_text`）、`scripts/build-stage2-html.py`（`dest.write_text`）
- WHEN wave-1 完成宣稱成立
- THEN 這四個產品目標寫入都先跑同一支 IR 驗證，通過後只經共用 `atomic_write`（DD-4）落地；產品目標路徑上看不到「驗證失敗仍覆寫」的路徑
- 觀測:從四檔寫入點的呼叫圖看 | 產品目標寫入點皆呼叫閘＋`atomic_write`、不再對產品目標直呼 `write_text` 算過 | 用 Stage 6 實作 diff 加 S-1 失敗案打四支 CLI 測
- Operational Context:
  - Actor:產檔器
  - Goal:壞產出不得取代 last-good
  - Situation:正式產器仍是 tip 的 `write_text`（#218 未改 `scripts/`）
  - Known information:四個寫入點行號（dir-tree L574／L654、gate-twin L2327、stage1 L480、stage2 L541）
  - Missing information:Stage 6 接線
  - Human decision:未接線就不簽 wave-1 完成
  - Authority:本 R；owner 簽完成
  - External dependency:共用 `atomic_write`
  - Out-of-system action:跑產器 CLI
  - Waiting/timeout behavior:未接線期間既有 `write_text` 行為仍在（Known limit）
  - Recovery:同一 T 把四支接到閘
  - Audit/handoff requirement:完成宣稱列出四支寫入點
  - Observation:見本條觀測

#### S-6.2 vbox-fig 呼叫端寫檔必須先過閘
- GIVEN `scripts/build-vbox-fig.py` 只寫 stdout（不寫檔）
- WHEN 本 repo 內會把該 stdout 寫成 html／svg 檔的呼叫端（wave-1 要接的那些）執行寫檔
- THEN 寫檔前必須先通過同一支 IR 驗證；失敗不得 `write_text` 蓋目標
- 觀測:從呼叫端寫檔函式看 | 失敗路徑零 `write_text`／零非原子覆寫算過 | 用生命週期負向信封經該呼叫端測
- Operational Context:不適用 — 呼叫端接線，交接同 S-6.1。

#### S-6.3 未接閘不得宣稱 wave-1 完成
- GIVEN 本 slug 過程檔或 PR 正文出現「wave-1 完成」或「IR 閘已落地」
- WHEN 四支產品寫檔仍對產品目標直呼 `write_text`（與 tip `9877652` 相同呼叫）
- THEN 該完成宣稱無效；本 R 未綠
- 觀測:從四檔是否仍有產品目標 `write_text` 與完成宣稱字面看 | 仍有 `write_text` 則完成宣稱必須不存在算過 | 用本 slug 過程檔 + 四支產器原文測
- Operational Context:不適用 — 完成宣稱守衛。

## MODIFIED Requirements

本 repo 無 `docs/specs/` living spec。下列活契約的「何時不用」**不改字**；本 slug 只在上面加路由表與寫檔閘。畫法規則（直式 SVG、四格生命週期、手寫 why、禁 mermaid）維持原文。

無 MODIFIED 條文。若後續要改任一份「何時不用」表，回第 2 站改 Decision D，不准只改本檔。

## REMOVED Requirements

無。不刪 vbox-fig／dir-tree／stage1／#191 牙；不刪既有 fixture。

## 行為流程圖(R 級)

```
[R-1] 驗證失敗保住 last-good
  穩定 DIAGIR 碼加旋鈕
  另印 DIAGIR_ABORT
[R-2] 通過則原子交付
  tmp 加 os.replace
  中斷只留截斷 tmp
[R-3] 五列查找路由表
  先選家族再跑產器
  錯家族 DIAGIR_FAMILY
[R-4] 薄索引 Proof Lab
  三族各一正一負
  負向紅且不蓋檔
[R-5] 預設靜態直式 SVG
  無 mermaid 無動畫預設
  不改 196 不 bump
[R-6] 四支寫檔接同一閘
  未接線不得稱完成
  vbox 呼叫端也要過閘
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-6.3）。
- 既有測試全綠：`scripts/check-vbox-fig.sh`、`scripts/check-gate-twin.sh`、`scripts/check-dir-tree.sh`、`scripts/devflow-check.sh` 回歸。
- 非功能：閘對單份信封在本機同步跑完；不新增網路 capability；不新增 Node 執行期。
- 行為不變類（畫法契約／#191）：golden master — 同一份 `notes/design/vbox-fig-contract.md`「何時不用」表，改動前後列集合不變；樹狀 ASCII 仍是 WARNING+`<pre>`，不是單盒。

## Out of Scope

- B／C／E／F／H／I（2-decision Rejected）。
- Mermaid；黑盒自動排版；一支 API 吃五族。
- Node render／hosted share／WYSIWYG。
- 動畫當預設；可選 trace（Q8 後刀）。
- deep-link／Architecture Delta／themes／Share Card（Q9 後刀）。
- `#196`／`#200`／`#201`。
- `integration-before-verdict`。
- 發版／bump `.claude-plugin/plugin.json`。
- 本 hop 改 `scripts/` 正本產器、補正式負向 fixture 檔、寫 `5-tasks.md`／Stage 6／Stage 7。
- 本 feature branch 改 `docs/dev/STATUS.md` 正本表列（OC-4）。
- 把 `docs/dev/diagram-ir-gate/proto/diagir_gate.py` 當正式產器出貨。
- 主機層攔截「硬跑錯產器」（2-decision 標後刀）。

## Diff Budget

本節是**估計**（給後續實作 hop，不是本規格 PR 的檔數）。超支本身非偏差，是停下判 L1/L2 的訊號。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| 共用 IR 閘 + 信封／碼表 + `atomic_write` 抽點 | ≤3 | ≤220 | ≤180 |
| 四支產品寫檔接閘（dir-tree／gate-twin／stage1／stage2）+ vbox 呼叫端 | ≤5 | ≤160 | ≤120 |
| 路由表資料 + Proof Lab 索引 + vbox-fig 正式負例 | ≤3 | ≤80 | ≤80 |
| **合計** | **≤11** | **≤460** | **≤380** |

[Assumption] 係數按「一個 S 一到兩條測試」，未加 mutation。本規格 PR 本身只動 `docs/dev/diagram-ir-gate/4-spec.md` 與 twin／審頁 html。

## Dependencies

- `scripts/write-stack-inventory.py` 的 `atomic_write` 形狀 —— justification:OC-3 沿用 tmp+`os.replace`，抽共用幫手，不另造第三套演算法。
- `scripts/build-vbox-fig.py` `normalize`（kind／空步／lines 1–3）—— justification:A 的驗證層沿用既有擋形，不重寫畫法。
- `scripts/build-dir-tree.py` `why_ok` 地板 12 —— justification:`DIAGIR_WHY` 與現有短 why 牙同一條線。
- `scripts/fixtures/vbox-fig/lifecycle.json`、`scripts/fixtures/gate-twin/fig-tree-ascii`、`scripts/fixtures/dir-tree/{good,missing-why}` —— justification:G 的 Lab 底；正負對齊現有牙。
- `scripts/check-vbox-fig.sh`／`check-gate-twin.sh`／`check-dir-tree.sh`／`devflow-check.sh` —— justification:Lab 對齊這些牙，不新開檢查家族。
- 無新外部服務、無新套件、無 migration、無 Node。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ②新增或修改公開 API（信封、`DIAGIR_*` 碼、四支產器寫檔契約）；③新增或修改跨模組 Interface（共用閘）；⑧新增 Filesystem capability（原子寫）；⑩三個以上模組共同參與（vbox／twin／dir-tree／stage1／stage2）；⑪有狀態機或複雜錯誤恢復（驗證失敗 → last-good）
- Design source: 既有 pattern —— `write-stack-inventory.py` tmp+replace、vbox-fig `normalize`、Decision A+D+G、Stage 3 throwaway `family`／`payload`；欄位名是 Decision 留給本檔的 local lock

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| IR 閘 | 讀信封、驗證、印收據、決定寫或不寫 | **擁有** `DIAGIR_*` 通過／失敗判定 | → 路由表、→ 各家族擋形（kind／why／steps） | 不得呼叫 mermaid／Node；不得黑盒猜家族 |
| 共用 `atomic_write` | tmp + `os.replace` | **擁有**落地原語 | → 本機 FS | 不得在驗證前落地產品目標 |
| 四支產品產器 | 組 payload、呼叫閘、吐審頁／樹 | 各產器擁有自己的 html／svg 產品檔 | → 閘、→ 各契約 | 不得對產品目標直呼 `write_text`（wave-1 完成後） |
| 路由表 | 五列查找 | **擁有** family id 清單 | → 已核契約「何時不用」 | 不得自動辨識家族 |
| Proof Lab 索引 | 點名樣張 | **擁有**六列路徑 | → 既有 fixture／牙 | 不得新開 `check-proof-lab.sh` |
| last-good 目標檔 | 上一張通過驗證的位元組 | 目標路徑上的檔 | ← 只接受通過後的 `atomic_write` | 失敗／中斷不得被新內容取代 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| 信封 → 閘 | in:`family`+`payload`；out:收據（`ok`／`code`／`knob`／`abort`／`delivered`） | 六碼見 DD-1／OC-1 | 驗證與寫入同一行程；失敗不寫產品目標 | 碼名鎖定 `DIAGIR_`；4-spec 可同前綴加碼 |
| 閘 → `atomic_write` | in:通過後的全文；out:目標檔整份新或未動 | 寫入中斷 → 目標全舊 + 截斷 tmp | 產品目標與 tmp 兩路徑；只成功 `replace` 才換目標 | 與 inventory 幫手同一原語 |
| 路由表查找 | in:人選的 family id；out:該列產器／契約 | 未知 id 或 payload 跨族 → `DIAGIR_FAMILY` | 無寫入 | 五 id 鎖定（DD-2） |
| Lab 索引重放 | in:一列 path；out:pass／fail + last-good 是否在 | 負向必須 fail | 每列獨立重放，不共用半寫狀態 | 對齊既有牙 exit |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| `validate(envelope)` | 家族／kind／空步／lines／why | ← 路由表、← vbox normalize 規則 | JSON → 碼或通過 | 失敗回收據、不寫檔 | S-1.1～S-1.6、S-3.2～S-3.3 |
| `atomic_write` | tmp+replace | ← 閘（只在通過後） | 全文 → tmp → replace | 中斷留 tmp | S-2.1～S-2.3 |
| 路由表資料 | 五列 | ← Decision D | id → 產器 | 未知 id → `DIAGIR_FAMILY` | S-3.1、S-3.4 |
| Lab 索引 | 六列點名 | → 既有 fixture | path → deliver／牙 | 負向不蓋檔 | S-4.1～S-4.4 |

### Design Constraints
- 必須:信封輸入只有 `family`+`payload`；失敗印穩定碼+旋鈕+`DIAGIR_ABORT`；寫入沿用 tmp+`os.replace`；五列路由先選家族；Lab 對齊既有牙；預設靜態 SVG。
- 禁止:mermaid／Node／動畫預設；黑盒自動排版；第二套 Lab 語言；第三套寫檔演算法；本 hop 改 STATUS 表列；本 hop 落地產器碼當規格的一部分；把 throwaway proto 當出貨。
- Extension point:4-spec 可增列同前綴 `DIAGIR_*` 碼（SC-5）；vbox-fig 正式負例檔 Stage 6 補進索引已點名的路徑；Q8 可選 trace 另刀。
- Known design limit:
  ① 本 hop 不改 `scripts/`；S-6.* 要等 Stage 6 接線才有產品寫入點可觀測。
  ② 誰都可以在閘外硬跑舊 CLI；本 slug 不做主機層攔截（2-decision 後刀）。
  ③ vbox-fig 正式負例檔尚未進 `scripts/fixtures/`；Lab 完成宣稱前必須補上索引已點名的檔。
  ④ 兩行程同時 deliver 同一目標：後成功的 `replace` 勝出；本波不加檔鎖。

## Verification Profile(G2 一併審)
- lane: full(判準:新能力、改四支產器公開寫檔契約、審查產物資料遺失。owner 已 lock full；無偏離)
- Risk: high(判準:公開寫檔／收據 API + last-good 被蓋 = 審查產物遺失。模板「公開 API／資料遺失／不可逆改動」吃這條)
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得在驗證失敗後覆寫產品目標（S-1.*／S-2.3）
  - 不得只印 traceback 當失敗輸出（S-1.6）
  - 不得黑盒猜家族或把五族併一支 API（S-3.1）
  - 不得另造 `scripts/proof-lab/` 或 `check-proof-lab.sh`（S-4.4）
  - 不得把 mermaid／動畫當預設成功條件（S-5.1／S-5.2）
  - 不得改 `#196` 或 bump plugin（S-5.3）
  - 不得在四支產品寫檔未接閘時宣稱 wave-1 完成（S-6.3）
  - 不得本 hop 改 `STATUS.md` 表列（OC-4）
- Required layers:check-spec-gate／check-vbox-fig／check-gate-twin／check-dir-tree
- Conditional layers:Supply chain — 當實作改到四支產器寫入點時，必跑 S-6.1 呼叫圖 + S-1 失敗案打 CLI
- Explicitly excluded layers:Mutation(本 hop 只規格)、e2e／Playwright(無新產品前端)、Race／stress(Known limit ④ 明示不加檔鎖)、Windows 真機(Out of Scope)、Node 執行期(Non-Goal)
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md && bash scripts/check-vbox-fig.sh && bash scripts/check-dir-tree.sh`
- Reliability triage:
  - Concurrency: applicable — 單一目標路徑的 `os.replace` 是本波隔離；兩 writer 同路徑不加鎖（Known limit ④）
  - Idempotency: applicable — 同一失敗信封再跑，碼與目標 sha 與第一次相同（S-1.*）
  - Timeout/retry: n-a — 本機檔案同步結束；失敗即停，由人修 IR 後重跑，不自動重試

Human verdict: ACCEPTED(Stage 3 CLI Demo；`3-prototype.md` attestation `human:rick @ 2026-09-12`)

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 失敗仍覆寫 last-good | 審查人打開壞圖；上一張可讀產出消失 | 失敗後目標 sha 變了 | Required:S-1.1～S-1.5 | — |
| 只印 traceback | agent 不知道改哪一欄 | 輸出無 `DIAGIR_` 字面 | Required:S-1.6 | — |
| 寫入中斷留下半檔 | 審頁截斷、像 #191 方向的壞 html | 目標開頭 `<svg` 無閉合 | Required:S-2.2／S-2.3 | — |
| 黑盒猜錯家族 | 三框當生命週期、樹收單盒 | 錯家族信封 `ok`=true | Required:S-3.2／S-3.3 | — |
| Lab 只綠正例 | 負向不蓋檔測不到 | 只有 `lifecycle.json` 被跑 | Required:S-4.3 | — |
| 另造 Lab 語言 | 與現有牙雙源漂 | 出現 `check-proof-lab.sh` | Required:S-4.4 | — |
| 預設改 mermaid／動畫 | 違反畫法總冊 | 綠檔含 mermaid 或成功條件寫動畫 | Required:S-5.1／S-5.2 | — |
| 產器仍 `write_text` 卻稱完成 | 閘只活在 throwaway | 四支仍直寫且過程檔稱完成 | Required:S-6.3 | — |
| 閘外硬跑舊 CLI | 仍可蓋檔 | 人直接呼叫未接閘的 tip CLI | 明示 Known limit ② | 主機層攔截是後刀 |
| 雙 writer 競態 | 後寫勝出 | 兩 deliver 同時 replace | 明示 Known limit ④ | 本波不加檔鎖 |

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記 Decision／Stage 3 留給本檔鎖定的選擇。不翻 A + D + G。G2 未核；`verdict` 留空。狀態欄「待人審」= 等人填 G2。

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 輸入信封鎖定為 JSON 物件，恰好兩個輸入欄：`family`（字串）+ `payload`（物件）。輸出收據鎖定為：`ok`（bool）、`code`（`PASS` 或 `DIAGIR_*`）、`knob`（非空字串）、`abort`（失敗時字面 `DIAGIR_ABORT`，通過時可省略）、`delivered`（bool）。`receipt` 是輸出物件名，不是第三個輸入欄 | OC-1 把 Schema 留給本檔；Stage 3 已證這兩個輸入欄夠跑 SC-1／2／5 | `2-decision.md` OC-1；`3-prototype.md:54-56`；`proto/diagir_gate.py:181-189` | 改欄名或把 Schema 做成第三輸入欄則 S-1／S-2 fixture 全改 | 待人審 |
| DD-2 | 五個 `family` id 鎖定為：`stage1-now`、`stage2-arch`、`behavior-flow`、`dir-tree`、`vbox-lifecycle`。列內容對齊 2-decision「選定路由表」五列 | Stage 3 #218 ACCEPTED 已用這五個 id；與 Decision D 表同向 | `2-decision.md:84-89`；`proto/diagir_gate.py:40-80` | 改 id（例如 `flow`／`lifecycle`）則信封與 Lab 列全改 | 待人審 |
| DD-3 | Proof Lab 薄索引檔名鎖定為 `scripts/fixtures/diagir-proof-lab.json`。六列 id 見 S-4.1。索引只點名，不發明新牙。vbox-fig 負向路徑點名 `scripts/fixtures/vbox-fig/kind-parked.json`（Stage 6 補檔） | OC-2 把檔名留給本檔；JSON 與 vbox fixture 同語系，不必新 parser | `2-decision.md` OC-2；`3-prototype.md:101` | 改成 `scripts/proof-lab/` = 採 H，已拒 | 待人審 |
| DD-4 | 原子寫抽到 `scripts/devflow_atomic_write.py` 的 `atomic_write(path, text)`，形狀與 `write-stack-inventory.py:30-37` 相同（tmp + `os.replace` + 補尾端 newline）。inventory 改 import 同一函式。不另寫第三套演算法 | OC-3 抽函式落點是 `[Assumption]`；抽出模組才能讓四支產器共用而不互相 import 一支 inventory 腳本 | `2-decision.md` OC-3；`scripts/write-stack-inventory.py:30-37` | 每支產器各寫一份 tmp+replace，或改用別的原語 | 待人審 |
| DD-5 | vbox 允許 `kind` 只有 `b`／`hl`／`wn`。dir-tree `why` 地板 = 去掉空白後 ≥12 字（與 `why_ok` 相同）。本檔不增第七個 fail code | 沿用 vbox `normalize` 與 dir-tree 牙，避免兩套擋形 | `2-decision.md:97-101`；`scripts/build-dir-tree.py:262-263`；`proto/diagir_gate.py:36-37` | 改地板或加 kind 則 S-1.3／S-1.1 重寫 | 待人審 |
| DD-6 | gate-twin Lab 正向點名既有 `scripts/fixtures/gate-twin/fig-long-label`；負向點名既有 `fig-tree-ascii`。不在本 hop 造假 fixture | 現況已有直式長標與樹狀負向；少造檔 | `scripts/fixtures/gate-twin/fig-long-label`；`3-prototype.md:100` | 改點名則 S-4.2／S-4.3 路徑句重寫 | 待人審 |
| DD-7 | Feature Risk = high；本 hop `verdict` 留空，由人類 G2 填。Agent 不寫 PASS | 公開寫檔契約 + last-good 遺失；四眼原則 | `_templates/4-spec.md` Risk 判準；本 hop brief「Leave G2 verdict empty」 | 改 normal 則 Failure Model 改選配；代填 PASS = 假綠 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 審頁用 `scripts/build-stage4-html.py --action`；G2 twin 用 `scripts/build-gate-twin.py <根> diagram-ir-gate 4-spec`。不手包 html-shell，不把審頁塞進 gate-twin STAGES。
- 本 hop 不改 `docs/dev/STATUS.md` 正本表列（OC-4）。
- 本 hop 不落地 Stage 6 產器碼；形狀以 R/S 為準。
- throwaway `docs/dev/diagram-ir-gate/proto/diagir_gate.py` 只供人重跑 Demo，不是 ship。
- 旋鈕句正本留在 2-decision Q6 表；S 只斷言「非空且非 traceback」，避免把「正確」寫進 S 區塊觸發反模糊掃描。

## Test Skeletons(選配)

- `test_s_1_1_parked_kind_holds_last_good`
- `test_s_1_2_tree_as_vbox_holds_last_good`
- `test_s_1_3_short_why_holds_last_good`
- `test_s_1_4_empty_title_holds_last_good`
- `test_s_1_5_four_lines_holds_last_good`
- `test_s_1_6_six_codes_each_with_knob`
- `test_s_2_1_pass_lifecycle_replaces_whole_file`
- `test_s_2_2_interrupt_keeps_truncated_tmp`
- `test_s_2_3_fail_leaves_no_half_target`
- `test_s_3_1_route_table_five_complete_rows`
- `test_s_3_2_stage1_as_lifecycle_family_code`
- `test_s_3_3_dir_as_vbox_family_code`
- `test_s_3_4_five_entries_map_to_own_row`
- `test_s_4_1_proof_lab_index_six_rows`
- `test_s_4_2_three_family_positives_pass`
- `test_s_4_3_three_family_negatives_hold`
- `test_s_4_4_no_second_lab_language`
- `test_s_5_1_green_delivery_has_no_mermaid`
- `test_s_5_2_animation_not_success_criterion`
- `test_s_5_3_no_issue_196_or_plugin_bump`
- `test_s_6_1_four_writers_go_through_gate`
- `test_s_6_2_vbox_callers_validate_before_write`
- `test_s_6_3_unwired_writers_cannot_claim_done`

## Stage 3 對帳

| Demo 場景 | Human verdict | 下落 |
|---|---|---|
| AC-1 失敗不蓋 last-good（kind-parked／tree-as-vbox／dir-short-why + ABORT） | ACCEPTED | S-1.1、S-1.2、S-1.3、S-1.6 |
| AC-1 空標題／四行 lines | ACCEPTED（同電池） | S-1.4、S-1.5 |
| AC-2 原子交付／中斷 | ACCEPTED | S-2.1、S-2.2、S-2.3 |
| AC-3 五家族路由 + 錯家族 FAMILY | ACCEPTED | S-3.1～S-3.4 |
| AC-4 Proof Lab 薄索引三族各一正一負 | ACCEPTED | S-4.1～S-4.4 |
| AC-5 預設仍是靜態 SVG | ACCEPTED | S-5.1、S-5.2 |
| Method「正式產器沒有因本站被改」 | ACCEPTED | S-6.3（本 hop 仍未接線）；S-5.3 |
| Method 信封 `family`／`payload` | ACCEPTED 形狀 | DD-1 |
| Operational Context Recovery（改 IR／改路由列後重跑；不要 git checkout） | ACCEPTED | S-1.1 Recovery、S-1.2、S-3.2 |

無 REVISE／NOT_REVIEWED 場景。3-prototype `Human verdict: ACCEPTED` + `human:rick @ 2026-09-12`。2-decision 無「跳過 Stage 3」OC。

## 確認紀錄
- 雙源清點 | 2026-09-12 | 驗收雛形 AC-1～AC-5 共 5 條 → 全數 ADDED（R-1～R-5）；living spec `docs/specs/` 0 條可引。寫檔接閘是 Decision Risk／Stage 3 回寫，升 R-6。無 MODIFIED／REMOVED。
- R 範圍 | 2026-09-12 | IMPLEMENTER B 依 owner brief「Encode R/S/DD from Decision A+D+G」編碼 R-1～R-6。範圍 = IR 閘 + 五家族路由 + Proof Lab + 靜態 SVG + 寫檔接閘。
- S 展開 | 2026-09-12 | R-1～R-6 全展開；每 S 有觀測欄；交接／等待／系統外動作的 S 有 Operational Context
- 3a 四節 | 2026-09-12 | AC／Out of Scope／Diff Budget／Dependencies 齊
- 3b Profile | 2026-09-12 | lane full、Risk high、Failure Model、Reliability triage、Design Boundary applicable
- 3c Stage 3 | 2026-09-12 | 五個 ACCEPTED Demo 場景 + Method／Recovery 逐場有 R/S 或 DD 下落
- DD 掃描 | 2026-09-12 | 上層七條待人審；掃描零殘留；不翻已核 Decision
- G2 verdict | 2026-09-12 | **留空**。不代填 PASS。不跑 N7 三連動。
