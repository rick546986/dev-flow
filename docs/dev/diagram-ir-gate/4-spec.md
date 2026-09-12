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

> 基準:main tip `9877652`(#218 Stage 3 Human ACCEPTED)。契約不 bump。本 hop **只 Stage 4**：落 `4-spec.md` + gate-twin html。**不**填 G2 `verdict`、不改 `scripts/` 正本產器、不補正式 fixture 碼、不碰 `#196`、不開 Stage 5、不發版、不改 `STATUS.md` 表列。
> Decision 正本:`docs/dev/diagram-ir-gate/2-decision.md`（A + D + G；OC-1～OC-4 ✅；G1 `verdict` PASS）。Stage 3 Human ACCEPTED（`human:rick @ 2026-09-12`）。本檔把 Q6 信封欄位與 Q7 索引檔名釘死；不翻 A／D／G。
> 本檔是 implementer-C 獨立編碼。`verdict` 留空；全勾不算 PASS；Agent 不得代填 G2。

## 補助模組生命週期（預覽）

主詞是「圖表 IR 閘」,不是整份方法論。直式圖,置中。
- 新生（這輪新模組）：共用 typed IR 信封 → 驗證 → 原子交付；五家族查找路由表；Proof Lab 薄索引。
- 改行為（相關一格）：`build-dir-tree.py`／`build-gate-twin.py`／`build-stage1-html.py` 的 `write_text` 與 vbox-fig 呼叫端改接同一閘；失敗或中斷不得取代 last-good。
- 退役：沒有。
- 不動：#191 WARNING+`<pre>`、既有四支牙、mermaid／Node／動畫預設禁令、`#196`、plugin 版號、`integration-before-verdict`。

## ADDED Requirements

### R-1: 系統 SHALL 在 IR 驗證失敗時保住 last-good 並吐穩定 DIAGIR_* 碼
Decision A／SC-1／SC-5。請求信封見 DD-1。六碼與旋鈕句鎖定在 `2-decision.md` Q6 表；本檔不改碼名。失敗時目標位元組與餵壞 IR 前相同；stdout 印一筆收據 JSON；stderr 含該碼與 Q6 旋鈕句，另含 `DIAGIR_ABORT`。不是只印 traceback。未接閘的產器不得宣稱 wave-1 完成。

**審的時候看什麼**
先寫一張通過驗證的目標檔，再餵 Stage 3 同形壞 IR。看目標 sha 與收據 `code`／`target_replaced`，不是看 Python traceback。

#### S-1.1 parked kind 必須 DIAGIR_KIND 且不蓋檔
- GIVEN 目標 `work/target.svg` 位元組等於 last-good 靜態 SVG（Stage 3 sha256 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc` 或測試新寫的同等檔），且請求信封 `family`=`vbox-lifecycle`、`payload.steps[0].kind`=`parked`、其餘三步 `kind`=`b`、每步 `title` 非空、`lines` 各 1 條非空字串
- WHEN 跑 wave-1 閘（正式入口 `scripts/diagir.py deliver ENVELOPE.json --out work/target.svg`；本 hop 未落地前以 `docs/dev/diagram-ir-gate/proto/diagir_gate.py deliver` 對照形狀）
- THEN exit ≠ 0；stdout 收據 JSON 的 `ok` 為 false、`code` 為 `DIAGIR_KIND`、`target_replaced` 為 false；stderr 含字面 `DIAGIR_KIND` 與 `2-decision.md` Q6 該列旋鈕句；`work/target.svg` 的 sha256 與 GIVEN 相同
- 觀測:從閘 exit、stdout JSON、stderr、目標 sha256 看 | 三個欄位與 sha 都符合上列 THEN 算過 | 用 Stage 3 `kind-parked` 同形信封測
- Operational Context:
  - Actor:開工 agent
  - Goal:壞 IR 不得換掉上一張可審圖
  - Situation:剛產過一張綠的生命週期 SVG，這次誤把 kind 寫成 `parked`
  - Known information:路由列 `vbox-lifecycle`；vbox 允許 kind 只有 `b`／`hl`／`wn`
  - Missing information:無（碼與旋鈕已印出）
  - Human decision:改 kind 或改選路由列後重跑
  - Authority:閘機械拒寫；審查人只看留下的 last-good
  - External dependency:無
  - Out-of-system action:在終端機重跑閘
  - Waiting/timeout behavior:目標停在 last-good，直到下一次通過驗證的交付
  - Recovery:依 Q6 `DIAGIR_KIND` 旋鈕改 IR 再跑；不要 `git checkout` 舊 html
  - Audit/handoff requirement:收據 JSON 留 `code` 與 `knob`
  - Observation:見本條觀測

#### S-1.2 空標題必須 DIAGIR_EMPTY 且不蓋檔
- GIVEN 同一 last-good 目標，信封 `family`=`vbox-lifecycle`、四步 `kind`=`b`、第一步 `title` 為三個空白、`lines`=`["x"]`
- WHEN 跑 S-1.1 同一閘入口
- THEN exit ≠ 0；收據 `code`=`DIAGIR_EMPTY`、`target_replaced`=false；目標 sha256 不變
- 觀測:從 exit、收據 `code`、目標 sha 看 | 碼是 `DIAGIR_EMPTY` 且 sha 不變算過 | 用 Stage 3 `empty-title` 同形信封測
- Operational Context:不適用 — 與 S-1.1 同一交接；本條只換觸發欄位。

#### S-1.3 四行 lines 必須 DIAGIR_LINES 且不蓋檔
- GIVEN 同一 last-good 目標，信封 `family`=`vbox-lifecycle`、第一步 `lines`=`["a","b","c","d"]`（四條非空）、其餘步 1 行
- WHEN 跑 S-1.1 同一閘入口
- THEN exit ≠ 0；收據 `code`=`DIAGIR_LINES`、`target_replaced`=false；目標 sha256 不變
- 觀測:從 exit、收據 `code`、目標 sha 看 | 碼是 `DIAGIR_LINES` 且 sha 不變算過 | 用 Stage 3 `four-lines` 同形信封測
- Operational Context:不適用 — 與 S-1.1 同一交接；本條只換 lines 長度。

#### S-1.4 樹狀當 vbox 必須 DIAGIR_FAMILY 且不蓋檔
- GIVEN 同一 last-good 目標，信封 `family`=`vbox-lifecycle`、`payload.kind`=`tree-ascii`、`payload.text` 含 `|---`
- WHEN 跑 S-1.1 同一閘入口
- THEN exit ≠ 0；收據 `code`=`DIAGIR_FAMILY`、`target_replaced`=false；目標 sha256 不變
- 觀測:從 exit、收據 `code`、目標 sha 看 | 碼是 `DIAGIR_FAMILY` 且 sha 不變算過 | 用 Stage 3 `tree-as-vbox` 同形信封測
- Operational Context:
  - Actor:開工 agent
  - Goal:不要把樹收成單盒 vbox
  - Situation:手邊是樹狀 ASCII，卻選了 `vbox-lifecycle`
  - Known information:路由表「行為流／目錄樹」列
  - Missing information:無
  - Human decision:改呼叫 `behavior-flow` 或 `dir-tree` 產器
  - Authority:閘拒寫
  - External dependency:無
  - Out-of-system action:查 `notes/design/diagir-route.md` 後換入口
  - Waiting/timeout behavior:last-good 留下
  - Recovery:Q6 `DIAGIR_FAMILY` 旋鈕；重跑對的產器
  - Audit/handoff requirement:收據 `code`=`DIAGIR_FAMILY`
  - Observation:見本條觀測

#### S-1.5 dir-tree 短 why 必須 DIAGIR_WHY 且不蓋檔
- GIVEN 同一 last-good 目標，信封 `family`=`dir-tree`、`payload.root` 來自 `scripts/fixtures/dir-tree/missing-why/purpose.yaml`（子節點 `why` 字面 `短`，長度 1 < 12）
- WHEN 跑 S-1.1 同一閘入口
- THEN exit ≠ 0；收據 `code`=`DIAGIR_WHY`、`target_replaced`=false；目標 sha256 不變
- 觀測:從 exit、收據 `code`、目標 sha 看 | 碼是 `DIAGIR_WHY` 且 sha 不變算過 | 用 Stage 3 `dir-short-why` 與該 fixture 測
- Operational Context:不適用 — 與 S-1.1 同一交接；本條只換 dir-tree why 地板。

#### S-1.6 失敗必須同時印 DIAGIR_ABORT 與收據形
- GIVEN S-1.1～S-1.5 任一失敗案例
- WHEN 讀該次 stdout 收據 JSON 與 stderr
- THEN 收據必含鍵 `ok`、`code`、`knob`、`abort`、`delivered`、`target_replaced`；`abort` 字面 `DIAGIR_ABORT`；`delivered` 與 `target_replaced` 皆 false；stderr 另有一行含 `DIAGIR_ABORT` 與 Q6 該列旋鈕句；stderr 不是只有 traceback
- 觀測:從 stdout JSON 六鍵與 stderr 兩碼行看 | 六鍵都在、兩碼都印、無「只 traceback」算過 | 對 S-1.1 一次失敗輸出測
- Operational Context:不適用 — 收據欄位形狀，無新的人員交接。

### R-2: 系統 SHALL 只在驗證通過後做原子交付
Decision A／OC-3／SC-2。寫入形狀沿用 `scripts/write-stack-inventory.py` 的 `tmp + os.replace`（抽出 `scripts/devflow_atomic.py`，見 DD-4）。看見的目標要嘛全新完整檔，要嘛全舊。驗證失敗或寫入未 `replace` 完成 → 目標不是截斷 html／svg。`build-dir-tree.py`、`build-gate-twin.py`、`build-stage1-html.py` 與會持久化 vbox SVG 的呼叫端都必須走同一閘，否則不得宣稱 wave-1 完成。

**審的時候看什麼**
綠 IR 之後目標是完整靜態 SVG。模擬中斷只留截斷 `.tmp`。三支現況 `write_text` 在 diff 裡消失或改呼叫閘。

#### S-2.1 綠生命週期必須整份換新靜態 SVG
- GIVEN 目標先是 last-good SVG，信封由 `scripts/fixtures/vbox-fig/lifecycle.json` 包成 `family`=`vbox-lifecycle`（與 Stage 3 `lifecycle_envelope` 同形）
- WHEN 跑 S-1.1 同一閘 `deliver`
- THEN exit 0；收據 `ok`=true、`delivered`=true、`target_replaced`=true、`code` 為 null；目標檔存在、長度大於截斷字串 `<svg viewBox`、內容含 `<svg` 且不含字面 `mermaid`；目標 sha256 ≠ last-good sha256
- 觀測:從 exit、收據四欄、目標檔頭與 sha 看 | 通過且整份新靜態 SVG 算過 | 用 Stage 3 `pass-lifecycle` 同形測
- Operational Context:
  - Actor:產檔器
  - Goal:通過後人打開的是完整新圖
  - Situation:IR 已通過驗證
  - Known information:last-good 與新 SVG 不同
  - Missing information:無
  - Human decision:接受新圖進審頁
  - Authority:閘在通過後才 `replace`
  - External dependency:無
  - Out-of-system action:用瀏覽器打開目標
  - Waiting/timeout behavior:無；`replace` 同步結束
  - Recovery:若 exit 0 但檔缺 `</svg>` → 本條紅，修原子寫
  - Audit/handoff requirement:收據 `delivered`=true
  - Observation:見本條觀測

#### S-2.2 中斷必須留下 last-good 與截斷 tmp
- GIVEN 目標是 last-good；旁路寫入 `work/target.svg.tmp` 內容恰為 `<svg viewBox`（長度 < 20），且**不**呼叫 `os.replace`
- WHEN 量測目標與 tmp
- THEN 目標 sha256 仍是 last-good；tmp 存在且長度 < 20；目標內容不是該截斷字串
- 觀測:從兩路徑 sha／size 看 | 目標不變、tmp 截斷、目標 ≠ tmp 內容算過 | 用 Stage 3 `INTERRUPT` 同形步驟測
- Operational Context:
  - Actor:產檔器
  - Goal:寫入中斷時審頁仍打得開舊圖
  - Situation:`replace` 尚未發生
  - Known information:tmp 路徑 = 目標路徑 + `.tmp`
  - Missing information:無
  - Human decision:修 IR 或重跑；不要把 `.tmp` 改名當交付
  - Authority:只有 `os.replace` 之後目標才變
  - External dependency:檔案系統
  - Out-of-system action:刪殘 tmp 後重跑
  - Waiting/timeout behavior:未 `replace` 視同 `DIAGIR_ABORT`
  - Recovery:重跑綠 IR；閘不得把截斷 tmp 當成成功
  - Audit/handoff requirement:目標 sha 可對 last-good
  - Observation:見本條觀測

#### S-2.3 三支現況寫檔與 vbox 呼叫端必須接同一閘
- GIVEN tip 現況：`scripts/build-dir-tree.py:574-576` 自寫 `write_text`；`scripts/build-gate-twin.py:2327` `out_local.write_text`；`scripts/build-stage1-html.py:480` `dest.write_text`；`scripts/build-vbox-fig.py` 只寫 stdout
- WHEN 宣告 wave-1 完成並 diff 這四條路徑
- THEN 前三處對**目標產品檔**的覆寫改為呼叫 `scripts/diagir.py`（或同模組函式）→ `devflow_atomic.atomic_write`；vbox-fig 仍可 stdout，但任何把該 stdout 寫進目標檔的呼叫端（`build-stage2-html.py`／`build-stage4-html.py` 持久化 SVG）必須先走同一閘；若任一目標覆寫仍直接 `Path.write_text`／`open(path,'w')` 而不經驗證，則不得勾 wave-1 完成
- 觀測:從這四檔（加兩支審頁呼叫端）的 diff 與閘 import 看 | 目標覆寫都經閘、未接閘不得勾完成算過 | 用實作 hop 的 git diff 對上列行號測
- Operational Context:不適用 — 接線範圍，無現場人員交接。

### R-3: 系統 SHALL 用一張五列查找路由表對到既有產器
Decision D／SC-3。表正本 `notes/design/diagir-route.md`（DD-3）。五個 `family` id：`stage1-now`／`stage2-arch`／`behavior-flow`／`dir-tree`／`vbox-lifecycle`。每列必有「用這條／不用那條／產器／契約」。人／agent **先選** `family`；缺欄或選錯 → `DIAGIR_FAMILY`。不是黑盒猜家族，不是 mermaid，不是一支 API 吃五族。

**審的時候看什麼**
打開路由表數五列。把三框當生命週期、把目錄樹當 vbox，都必須是 `DIAGIR_FAMILY`。沒有 `family` 欄不得被猜成某一列。

#### S-3.1 路由表必須剛好五列且欄位齊
- GIVEN 檔 `notes/design/diagir-route.md`（Stage 6 落地；本 hop 契約以 Decision D 定稿表為準）
- WHEN 數列並讀欄
- THEN 剛好五列，id 集合等於 `{stage1-now, stage2-arch, behavior-flow, dir-tree, vbox-lifecycle}`；每列都有非空「用這條」「不用那條」「產器」「契約」四欄；契約欄分別指回 `stage1-review-ui-contract`、`stage2-review-ui-contract`+vbox 母版、vbox-fig-contract（twin 收口）、`dir-tree-contract`、`vbox-fig-contract`
- 觀測:從該 md 表列數與四欄看 | 五 id 齊、無空欄、契約列指回已核檔算過 | 用 Decision D「選定路由表」五行當對照測
- Operational Context:不適用 — 查找表字面，無人員交接。

#### S-3.2 三框當生命週期必須 DIAGIR_FAMILY
- GIVEN last-good 目標，信封 `family`=`vbox-lifecycle`、`payload`=`{"kind":"stage1-now","boxes":3,"scan_now":true}`
- WHEN 跑 S-1.1 同一閘
- THEN exit ≠ 0；`code`=`DIAGIR_FAMILY`；目標 sha 不變
- 觀測:從 exit、`code`、目標 sha 看 | 與 Stage 3 `stage1-as-lifecycle` 同結果算過 | 用該信封測
- Operational Context:
  - Actor:開工 agent
  - Goal:第 1 站三框不要畫成生命週期四格
  - Situation:剛看過 vbox 產器，順手拿來畫 `#scan-now`
  - Known information:路由表 `stage1-now` 列寫明不用生命週期四格
  - Missing information:無
  - Human decision:改跑 `build-stage1-html.py --action`
  - Authority:閘拒寫
  - External dependency:無
  - Out-of-system action:換產器
  - Waiting/timeout behavior:last-good 留下
  - Recovery:Q6 `DIAGIR_FAMILY` 旋鈕
  - Audit/handoff requirement:收據碼
  - Observation:見本條觀測

#### S-3.3 目錄樹當 vbox 必須 DIAGIR_FAMILY
- GIVEN last-good 目標，信封 `family`=`vbox-lifecycle`、`payload.kind`=`dir-tree`、`payload.root.name`=`demo/`、`payload.root.why` 長度 ≥ 12
- WHEN 跑 S-1.1 同一閘
- THEN exit ≠ 0；`code`=`DIAGIR_FAMILY`；目標 sha 不變
- 觀測:從 exit、`code`、目標 sha 看 | 與 Stage 3 `dir-as-vbox` 同結果算過 | 用該信封測
- Operational Context:不適用 — 與 S-3.2 同一「選錯列」交接。

#### S-3.4 缺 family 不得黑盒猜列
- GIVEN last-good 目標，請求 JSON **沒有** `family` 鍵，只有 `payload.steps` 四步合法 vbox
- WHEN 跑 S-1.1 同一閘
- THEN exit ≠ 0；`code`=`DIAGIR_FAMILY`；目標 sha 不變；輸出不得宣稱已選 `vbox-lifecycle` 或其他列
- 觀測:從收據 `code` 與是否出現「已選／auto／detect」字樣看 | 必須 `DIAGIR_FAMILY` 且無自動選列字樣算過 | 用無 `family` 鍵的 JSON 測
- Operational Context:
  - Actor:開工 agent
  - Goal:先選家族，不要讓機器猜
  - Situation:只丟了步驟列
  - Known information:五個 id
  - Missing information:`family` 欄
  - Human decision:補上 id 再跑
  - Authority:閘拒猜
  - External dependency:無
  - Out-of-system action:打開路由表勾一列
  - Waiting/timeout behavior:不寫檔
  - Recovery:補 `family` 後重跑
  - Audit/handoff requirement:收據 `DIAGIR_FAMILY`
  - Observation:見本條觀測

#### S-3.5 五個現況入口必須對上五列
- GIVEN Decision D 五列與本 repo 五個入口：`build-stage1-html.py --action`、`build-stage2-html.py --action`、`build-gate-twin.py` 行為流、`build-dir-tree.py`、`build-vbox-fig.py` lifecycle
- WHEN 對每列讀「產器」欄
- THEN 上列五入口各出現恰好一列；`stage1-now` 不得指向 `build-vbox-fig.py`；`dir-tree` 不得指向 vbox 或 gate-twin；沒有第六列 mermaid／hosted
- 觀測:從路由表產器欄與五入口字面看 | 一一對上、無第六列算過 | 用 `notes/design/diagir-route.md`（或本檔落地前的 Decision D 表）測
- Operational Context:不適用 — 入口對帳。

### R-4: 系統 SHALL 用薄索引重放三家族各一正一負
Decision G／OC-2／SC-4。索引檔名鎖定 `scripts/fixtures/diagir-lab.yaml`（DD-2）。只點名既有 `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}`（vbox 負向 Stage 6 補 `kind-parked.json`）。牙仍是 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree`／`devflow-check`。不是第二套檢查語言，不是「只有 `lifecycle.json` 綠過」。

**審的時候看什麼**
索引六列。三個負向 exit ≠ 0 且目標 sha 不變。正例可獨立重放。沒有 `scripts/check-diagir-lab.sh` 當唯一牙。

#### S-4.1 索引必須六列三家族
- GIVEN `scripts/fixtures/diagir-lab.yaml`（Stage 6 落地本檔；欄位本 hop 鎖定）
- WHEN 讀 `version: 1` 與 `rows`
- THEN 剛好 6 列；`family` 集合為 `{vbox-fig, gate-twin, dir-tree}` 且各 1 正 1 負；`path` 分別為 `scripts/fixtures/vbox-fig/lifecycle.json`、`scripts/fixtures/vbox-fig/kind-parked.json`、`scripts/fixtures/gate-twin/fig-long-label`、`scripts/fixtures/gate-twin/fig-tree-ascii`、`scripts/fixtures/dir-tree/good`、`scripts/fixtures/dir-tree/missing-why`；負向列帶 `expect_code`：`DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`；`tooth_language` 字面 `existing`
- 觀測:從該 yaml 列數、path、`expect_code` 看 | 六 path 與三碼都符合算過 | 用落地後的索引檔測；本 hop 以本條當契約
- Operational Context:不適用 — 索引檔字面。

#### S-4.2 三正例必須可獨立重放
- GIVEN S-4.1 三列 `polarity: pos`
- WHEN 各用對應牙或閘重放：vbox-fig → `bash scripts/check-vbox-fig.sh` 能吃 `lifecycle.json`；gate-twin → `bash scripts/check-gate-twin.sh` 對 `fig-long-label`；dir-tree → `bash scripts/check-dir-tree.sh` 對 `good`；閘對三個 pos 信封 `ok`=true
- THEN 三支牙對該正例 exit 0（或該牙既有射程內綠）；閘 pos 收據 `ok`=true。允許 pos 覆寫測試目標
- 觀測:從三支牙 exit 與閘 pos 收據看 | 三正皆綠算過 | 用索引 path 測
- Operational Context:不適用 — 牙重放，無人員交接。

#### S-4.3 三負例必須紅且不蓋 last-good
- GIVEN 測試目標已是 last-good；S-4.1 三列 `polarity: neg`（vbox 負向在 `kind-parked.json` 落地前，重放 Stage 3 `kind-parked` 信封，結果必須與該檔落地後相同）
- WHEN 各跑閘 `deliver` 到同一目標
- THEN 三案 exit ≠ 0；`code` 分別 `DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`；三次之後目標 sha256 仍是 last-good
- 觀測:從三案 exit、`code`、目標 sha 看 | 三碼對上且 sha 不變算過 | 用 Stage 3 LAB 三負列測
- Operational Context:
  - Actor:owner／審查人
  - Goal:負向紅了 last-good 還在
  - Situation:Proof Lab 重放
  - Known information:索引六列
  - Missing information:無
  - Human decision:負向紅且檔還在才算 Lab 過
  - Authority:閘拒寫
  - External dependency:既有 fixture 目錄
  - Out-of-system action:跑索引列
  - Waiting/timeout behavior:無
  - Recovery:負向若蓋檔 → wave-1 未完成
  - Audit/handoff requirement:LAB 列印 `neg_held=true`
  - Observation:見本條觀測

#### S-4.4 不得只靠 lifecycle.json 綠過
- GIVEN S-4.1 索引
- WHEN 比對 vbox-fig 正／負 `path`
- THEN 負向 path ≠ `scripts/fixtures/vbox-fig/lifecycle.json`；負向 `expect_code` 必填；缺少 vbox 負向列或負向 path 等於正例 path → 本條紅
- 觀測:從索引兩列 path 看 | 正負不同且負向有碼算過 | 讀 yaml 兩列測
- Operational Context:不適用 — 防 I 方案回流。

#### S-4.5 不得另造 Proof Lab 檢查語言
- GIVEN wave-1 完成宣告
- WHEN 搜新增牙入口
- THEN 不存在以 Lab 為唯一真相的 `scripts/check-diagir-lab.sh`（或同等第二套方法論）被 `scripts/devflow-check.sh` 當成取代 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree` 的入口；索引只准點名，不准發明新 needle 語言
- 觀測:從 `scripts/devflow-check.sh` 仍呼叫既有三支牙、且無「取代」字樣看 | 三支仍在、無第二套 Lab 牙算過 | 對 `devflow-check.sh` 與 `scripts/check-*.sh` 檔名測
- Operational Context:不適用 — Non-Goal 邊界。

### R-5: 系統 SHALL 維持預設靜態直式 SVG 且不收 NON-goal
SC-6／AC-5。預設產出仍是靜態直式 SVG。無 mermaid.js、無自動播放動畫當成功條件、無 Node render／hosted share／WYSIWYG／deep-link／Architecture Delta／themes／Share Card。本 slug 不改 `#196`、不 bump plugin。

**審的時候看什麼**
綠交付檔裡找 mermaid 與 `<animate`。本 PR diff 不含 `#196` 與 `plugin.json` 版號。

#### S-5.1 綠交付不得把 mermaid 或動畫當預設
- GIVEN S-2.1 通過後的目標檔
- WHEN 搜字面 `mermaid`、`mermaid.js`、`<animate`、`animateTransform`
- THEN 零命中；檔含 `<svg`；靜態幀（無動畫）已是完整圖
- 觀測:從目標檔 `rg` 與是否含 `<svg` 看 | 四詞零命中且有 svg 算過 | 用 S-2.1 產出測
- Operational Context:
  - Actor:owner
  - Goal:wave-1 成功條件不是「會動」
  - Situation:打開預設圖
  - Known information:畫法總冊禁 mermaid／外部庫
  - Missing information:無
  - Human decision:看到動畫預設就打回
  - Authority:本 R 與 Non-Goals
  - External dependency:無
  - Out-of-system action:瀏覽器直開
  - Waiting/timeout behavior:無
  - Recovery:可選 trace 屬 Q8 後刀，本 slug 不收
  - Audit/handoff requirement:預設檔可離線打開
  - Observation:見本條觀測

#### S-5.2 本 slug 不得改 plugin 版號與 #196
- GIVEN 本 feature 的 git diff（相對 `9877652`）
- WHEN 列變更檔
- THEN `.claude-plugin/plugin.json` 的 `version` 與 tip 相同；diff 不含 PR `#196` 正在改的檔當本 slug 交付；也不含 Node render／hosted share 新依賴
- 觀測:從 `git diff 9877652 -- .claude-plugin/plugin.json` 與變更清單看 | plugin 空 diff、無 #196 檔算過 | 用本 slug 各 hop 的 PR diff 測
- Operational Context:不適用 — 範圍牙。

## MODIFIED Requirements

本 repo 無 `docs/specs/` living spec。下列是**活產器寫檔行為**；契約「何時不用」原文不改，改由 D 收進路由表。

### M-1: dir-tree 直接覆寫目標
原條文（`scripts/build-dir-tree.py:574-576`）:
> `pathlib.Path(path).write_text(text, encoding="utf-8")`
改成:對產品目標檔改走 R-2 閘 + `atomic_write`；驗證失敗不呼叫覆寫。承接 S-2.3、S-1.5。

### M-2: gate-twin 直接覆寫 feature html
原條文（`scripts/build-gate-twin.py:2327`）:
> `out_local.write_text(ui.local_page(...), encoding="utf-8")`
改成:寫 `docs/dev/<slug>/<stage>.html` 前先走同一閘；失敗保留上一張 html。承接 S-2.3、S-1.4。

### M-3: stage1-html 直接覆寫審頁
原條文（`scripts/build-stage1-html.py:480`）:
> `dest.write_text(html_out, encoding="utf-8")`
改成:寫審頁前先走同一閘。承接 S-2.3、S-3.2。

## REMOVED Requirements

無。不刪 #191 WARNING+`<pre>`、不刪既有四支牙、不刪五個產器入口、不刪 mermaid 禁令。

## 行為流程圖(R 級)

```
[R-1] 驗證失敗保住 last-good
  parked／空題／四行紅
  錯家族／短 why 紅
  收據含碼與旋鈕
[R-2] 通過才原子交付
  tmp 加 replace
  中斷不碰目標
  三支寫檔接同一閘
[R-3] 五家族先查表
  五列用這條不用那條
  錯家族 DIAGIR_FAMILY
  缺欄不黑盒猜
[R-4] Proof Lab 薄索引
  三家族各一正一負
  負向紅且不蓋檔
  牙仍是現有四支
[R-5] 預設靜態直式 SVG
  無 mermaid 無動畫預設
  不碰 196 不 bump
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-5.2）。
- 既有測試全綠：`bash scripts/check-vbox-fig.sh`、`bash scripts/check-dir-tree.sh`、`bash scripts/check-gate-twin.sh` 與 `bash scripts/devflow-check.sh` 回歸。
- 非功能：閘對單份信封在本機同步結束；不新增網路／Node capability。
- 行為不變類（R-5、#191）：golden master — 樹狀 ASCII 仍 WARNING+`<pre>`；預設圖仍是靜態 inline SVG。

## Out of Scope

- B／C／E／F／H／I（見 2-decision Rejected）。
- Mermaid、黑盒自動排版、Node render、hosted share、WYSIWYG。
- 動畫當預設；可選 trace（Q8 後刀）。
- deep-link／Architecture Delta／themes／Share Card（Q9 後刀）。
- 本 hop 改 `scripts/build-*.py` 正本或往 `scripts/fixtures/` 塞負向碼。
- `#196`／`#200`／`#201`。
- `integration-before-verdict`。
- 發版／bump `.claude-plugin/plugin.json`。
- 本 hop 寫 `5-tasks.md`／Stage 6／Stage 7。
- 本 feature branch 改 `docs/dev/STATUS.md` 正本表列（OC-4）。
- 把第 1 站三框併進 vbox-fig；改掃頁產生器充審頁。
- 主機層攔截「硬跑錯產器」（Decision D 標後刀）。
- 代填 G2 `verdict` PASS。

## Diff Budget

本節是**估計**（給後續實作 hop，不是本規格 PR 的檔數）。超支本身非偏差，是停下判 L1/L2 的訊號。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| `scripts/diagir.py` 驗證＋收據 | ≤1 | ≤220 | ≤180 |
| `scripts/devflow_atomic.py` 抽出 tmp+replace | ≤1 | ≤40 | ≤30 |
| 三支產器 + vbox 呼叫端接閘 | ≤5 | ≤120 | ≤80 |
| `notes/design/diagir-route.md` + `scripts/fixtures/diagir-lab.yaml` + vbox 負向 fixture | ≤3 | ≤80 | ≤40 |
| **合計** | **≤10** | **≤460** | **≤330** |

[Assumption] 係數按「一個 S 一到兩條測試」，未加 mutation。本規格 PR 本身只動 `docs/dev/diagram-ir-gate/4-spec.md` 與 twin html。

## Dependencies

- `scripts/write-stack-inventory.py` 的 `atomic_write` 形狀 —— justification:OC-3 沿用 tmp+`os.replace`，不另造第三支演算法。
- `scripts/build-vbox-fig.py` `normalize` —— justification:A 的擋形沿用空步驟／錯 kind／空標題／lines 1–3。
- `scripts/check-vbox-fig.sh`／`check-gate-twin.sh`／`check-dir-tree.sh`／`devflow-check.sh` —— justification:G 的牙，Proof Lab 對齊它們。
- 既有 fixture：`vbox-fig/lifecycle.json`、`gate-twin/fig-tree-ascii`、`gate-twin/fig-long-label`、`dir-tree/good`、`dir-tree/missing-why` —— justification:G 的樣張底。
- `docs/dev/diagram-ir-gate/proto/diagir_gate.py` —— justification:Stage 3 形狀對照；非正式通道。
- 無新外部服務、無新套件、無 migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組（閘被三支產器 + vbox 呼叫端共用）；②新增公開 API（信封／`DIAGIR_*`／收據 JSON）；③跨模組 Interface（`diagir.py` ↔ 產器寫檔）；⑧Filesystem capability（目標檔 `replace`）；⑩三個以上模組；⑪錯誤恢復（last-good／`DIAGIR_ABORT`）
- Design source: 既有 pattern —— inventory `atomic_write`、vbox `normalize`、Decision D 五列表、Stage 3 throwaway 信封；欄位名是 Decision 留給本檔的 local lock

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| `scripts/diagir.py` | 驗信封、發收據、決定是否交付 | **擁有** `DIAGIR_*` 判定與收據 JSON | → route 表、→ `devflow_atomic`、→ 各家族擋形 | 不得 import Archify／mermaid／Node；不得猜 `family` |
| `scripts/devflow_atomic.py` | tmp + `os.replace` | **擁有**寫入原語 | → 檔案系統 | 不得做驗證；不得在驗證失敗後被呼叫 |
| 三支產器 + vbox 呼叫端 | 組 payload、選 family、讀契約 | 各產器擁有自己的產品 html／svg | → diagir | 不得再對目標 `Path.write_text` |
| `notes/design/diagir-route.md` | 五列查找 | **擁有** family id | → 四份已核契約 | 不得發明第六家族 |
| `scripts/fixtures/diagir-lab.yaml` | 點名樣張 | **擁有**正負 path | → 既有 fixture 目錄 | 不得當第二套牙 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| 請求信封 | in:`family`+`payload` JSON；out:收據 JSON | 缺 family／錯家族 → `DIAGIR_FAMILY` | 驗證失敗零寫目標 | 欄位名本檔鎖定；不吃 Archify schema |
| 原子交付 | in:通過後的完整字串；out:目標檔 | 未 `replace` → 目標仍 last-good | 目標與 tmp 只成功一筆可見：`replace` 前目標全舊 | 與 inventory 同一原語 |
| 路由查找 | in:人選的 family id；out:產器＋契約 | 未知 id → `DIAGIR_FAMILY` | 無寫入 | 五 id 凍結；改 id = 回第 2 站 |
| Lab 重放 | in:索引一列；out:牙／閘 exit | 負向必須 ≠ 0 | 負向不得 `replace` 目標 | 牙入口仍是現有四支 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| `validate(envelope)` | 家族碼 + vbox／why 擋形 | ← route id 集合、← `normalize` 規則 | JSON → 碼或 ok | 先碼後停寫 | S-1.1～S-1.6、S-3.2～S-3.4 |
| `deliver` | 先 validate 再 atomic_write | → atomic_write | last-good 位元組對照 | 失敗回收據、不 `replace` | S-2.1、S-2.2 |
| 薄索引讀取 | 列出六列 | ← yaml | path → 重放 | 缺列 → S-4.1 紅 | S-4.1～S-4.4 |
| 產器接線 | 選 family 後呼叫閘 | → diagir | 舊 write_text 刪除 | 未接閘不得完成 | S-2.3 |

### Design Constraints
- 必須:共用一閘；失敗保住 last-good；六碼前綴 `DIAGIR_`；五列查找；Lab 三家族各一正一負；原子寫 = tmp+`os.replace`；預設靜態 SVG。
- 禁止:黑盒猜家族；第二套 Lab 牙；第三支寫檔演算法；mermaid／Node／動畫預設；本 hop 改 STATUS 表列；本 hop 代填 G2；本 hop 落地產器當規格的一部分。
- Extension point:Q8 可選 trace、Q9 deep-link／Delta／themes／Share Card —— 另 slug。
- Known design limit:
  ① vbox-fig 正式負向檔 `kind-parked.json` 本 hop 不造；S-4.3 在落地前用 Stage 3 同形信封。
  ② 主機層不擋「跳過閘硬跑舊 `write_text`」；S-2.3 用 diff 咬接線，不是 OS hook。
  ③ throwaway `proto/diagir_gate.py` 非正式通道；G3 現象以正式 `scripts/diagir.py` 為準。

## Verification Profile(G2 一併審)
- lane: full（判準:新能力、跨模組寫檔契約、agent 面向公開信封。owner 已 lock full；無偏離）
- Risk: high（判準:公開 API＝`DIAGIR_*`／信封；失敗模式會遺失上一張可審圖。模板「公開 API／資料遺失」吃這條）
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得在驗證失敗後覆寫目標（S-1.1～S-1.5）
  - 不得只印 traceback 而無穩定碼（S-1.6）
  - 不得留下半份新目標檔（S-2.2）
  - 不得未接閘就宣稱 wave-1 完成（S-2.3）
  - 不得黑盒猜 `family`（S-3.4）
  - 不得只重放 `lifecycle.json` 當 Lab（S-4.4）
  - 不得另造 Proof Lab 牙語言（S-4.5）
  - 不得把 mermaid／動畫當預設（S-5.1）
  - 不得碰 `#196`、不得 bump plugin（S-5.2）
  - 不得收 Mermaid／Node／hosted／WYSIWYG／Q8／Q9
- Required layers:check-spec-gate／check-vbox-fig／check-dir-tree／check-gate-twin
- Conditional layers:Supply chain — 當實作改到產器寫檔或加新 Python 依賴時，必跑 `devflow-check.sh` 對應段
- Explicitly excluded layers:Mutation（本 hop 只規格）、e2e／Playwright（無產品前端）、Race／stress（wave-1 單 writer）、Windows 真機（Out of Scope）
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md && bash scripts/check-vbox-fig.sh && bash scripts/check-dir-tree.sh && bash scripts/check-gate-twin.sh`
- Reliability triage:
  - Concurrency: n-a — wave-1 單一 writer 對單一目標路徑；無多 writer 鎖契約
  - Idempotency: applicable — 同一綠信封再交付仍是完整檔；同一壞信封再跑目標 sha 仍是 last-good（S-1.*／S-2.1）
  - Timeout/retry: applicable — 中斷或失敗 = `DIAGIR_ABORT`；人修 IR 後重跑；閘不自動重試（S-2.2、S-1.6）

Human verdict: ACCEPTED（Stage 3 CLI Demo；`3-prototype.md` attestation `human:rick @ 2026-09-12`）

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 壞 IR 仍覆寫 | 審查人看到壞圖；#191 類回歸 | 失敗後目標 sha 變了 | Required:S-1.1～S-1.5 | — |
| 失敗只有 traceback | agent 不知道旋鈕 | stderr 無 `DIAGIR_` | Required:S-1.6 | — |
| 半份新檔 | 審頁打不開 | 目標是截斷 `<svg viewBox` | Required:S-2.2 | — |
| 產器繞過閘 | last-good 契約只存在 throwaway | diff 仍有目標 `write_text` | Required:S-2.3 | — |
| 黑盒猜家族 | 三框變生命週期且無法審計 | 無 `family` 仍 exit 0 | Required:S-3.4 | — |
| Lab 只有正例 | 負向不蓋檔測不到 | 索引缺負向或 path 相同 | Required:S-4.4 | — |
| 第二套 Lab 牙 | 與現有牙雙源漂 | 新 `check-diagir-lab.sh` 取代舊牙 | Required:S-4.5 | — |
| 動畫／mermaid 當預設 | 違反畫法總冊 | 交付含 mermaid／`<animate` | Required:S-5.1 | — |
| 跳過閘硬跑舊 CLI | 主機不擋 | 人直接呼叫舊 `write_text` 路徑 | Known limit ② | 本 feat 不新造 OS hook |

## Drafting Decisions(草擬自判,待 G2 人審)

形狀已寫進 R/S。本表只記 Decision／Stage 3 留給本檔鎖定的選擇。不翻 A + D + G。狀態「待人審」= implementer-C 已拍板、等人審；**不是** G2 PASS。

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 請求信封鎖定為 JSON 物件，鍵只有 `family`（五 id 之一）與 `payload`（物件）。收據是**輸出**：stdout 一筆 JSON，鍵 `ok`／`code`／`knob`／`abort`／`delivered`／`target_replaced`。stderr 另印 `FAIL <code> \| knob:`。請求裡不放 `receipt` | Stage 3 已證 `family`／`payload` 夠跑 SC-1／2／5；Decision 把欄位留給 4-spec；收據當輸出才測得到「失敗不寫檔」 | `3-prototype.md:54-56`；`2-decision.md:93`；`proto/diagir_gate.py:126-134` | 改鍵名則 S-1.6／全部信封 fixture 改 | 待人審 |
| DD-2 | Proof Lab 索引檔名 = `scripts/fixtures/diagir-lab.yaml`。六列 path 見 S-4.1。vbox 負向檔名 = `scripts/fixtures/vbox-fig/kind-parked.json`（Stage 6 才新增檔；落地前重放 Stage 3 `parked` 信封）。gate-twin 正例點名已存在的 `fig-long-label` | OC-2 要薄索引、不新建語言；正例優先用已提交 fixture | `2-decision.md:133` OC-2；`scripts/fixtures/gate-twin/fig-long-label/`；`3-prototype.md:101` | 改檔名或改正例 path 則 S-4.1 重寫 | 待人審 |
| DD-3 | 路由表活檔 = `notes/design/diagir-route.md`。五 id 與 Decision D 定稿表逐字同一組。改「何時不用」必須回改本表 | D 要一張先查的表；散契約仍是各家族正本 | `2-decision.md:81-89` | 改 id 或併 API = 回第 2 站 | 待人審 |
| DD-4 | 原子寫抽出 `scripts/devflow_atomic.py`，函式名 `atomic_write`，形狀與 `write-stack-inventory.py:30-37` 相同（tmp + `os.replace` + 補尾端 newline）。inventory 本 slug 可不改 | OC-3 沿用形狀、不另造演算法 | `2-decision.md:134`；`scripts/write-stack-inventory.py:30-37` | 每產器各寫一份 tmp 邏輯 = 已拒的第三支幫手 | 待人審 |
| DD-5 | 正式閘模組 = `scripts/diagir.py`。`docs/dev/diagram-ir-gate/proto/diagir_gate.py` 只當 Stage 3 對照，不得當 ship 入口 | throwaway 標了非正式；G3 要 persisted 命令 | `3-prototype.md:46`；`3-prototype.md:151` | 把 proto 當正式入口則 S-1.1 WHEN 改 | 待人審 |
| DD-6 | vbox-fig 繼續只寫 stdout；持久化由呼叫端走閘。dir-tree／gate-twin／stage1-html 在模組內接閘 | 與「vbox 無寫檔」現況相容，又把 last-good 補到呼叫端 | `scripts/build-vbox-fig.py:11-16`；`2-decision.md:73` | 改成 vbox 自己寫檔要重審呼叫端清單 | 待人審 |
| DD-7 | dir-tree why 地板 = 12 字（`build-dir-tree.py:262`）。短於 12 → `DIAGIR_WHY` | 對齊現有短 why 紅，不另定地板 | `scripts/build-dir-tree.py:262`；`scripts/check-dir-tree.sh:134` | 改地板則 S-1.5 fixture 可能假紅／假綠 | 待人審 |
| DD-8 | Feature Risk = high；本 hop `verdict` 留空，由人類 G2 填。implementer 不得寫 PASS | 公開信封 + last-good 遺失；四眼原則；本 brief 禁止假 G2 | `_templates/4-spec.md` Risk 判準；owner brief「Leave G2 verdict empty」 | 改 normal 則 Failure Model 改選配；代填 PASS = 假綠 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 閘 CLI：`python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`；`route` 印五列。本 hop 不落地該檔。
- 審頁用 `scripts/build-stage4-html.py --action`；G2 twin 用 `scripts/build-gate-twin.py <根> diagram-ir-gate 4-spec`。不手包 html-shell，不把審頁塞進 gate-twin STAGES。本 hop 交付的 `4-spec.html` 是 gate-twin。
- 本 hop 不改 `docs/dev/STATUS.md` 正本表列（OC-4）。
- 本 hop 不 bump plugin、不開 5-tasks。
- why 地板沿用 12，不在本檔重寫 dir-tree 契約短冊。

## Test Skeletons(選配)

- `test_s_1_1_parked_kind_keeps_last_good`
- `test_s_1_2_empty_title_diagir_empty`
- `test_s_1_3_four_lines_diagir_lines`
- `test_s_1_4_tree_as_vbox_diagir_family`
- `test_s_1_5_short_why_diagir_why`
- `test_s_1_6_fail_emits_abort_and_receipt`
- `test_s_2_1_pass_lifecycle_atomic_svg`
- `test_s_2_2_interrupt_keeps_last_good`
- `test_s_2_3_builders_wire_same_gate`
- `test_s_3_1_route_table_five_rows`
- `test_s_3_2_stage1_as_lifecycle_family`
- `test_s_3_3_dir_as_vbox_family`
- `test_s_3_4_missing_family_not_guessed`
- `test_s_3_5_five_entries_map_five_rows`
- `test_s_4_1_lab_index_six_rows`
- `test_s_4_2_three_pos_replay`
- `test_s_4_3_three_neg_hold_last_good`
- `test_s_4_4_not_only_lifecycle_json`
- `test_s_4_5_no_second_lab_tooth`
- `test_s_5_1_default_static_svg_no_mermaid`
- `test_s_5_2_no_plugin_bump_no_196`

## Stage 3 對帳

| Demo 場景 | Human verdict | 下落 |
|---|---|---|
| AC-1 失敗不蓋 last-good（kind／tree／short-why） | ACCEPTED | S-1.1、S-1.4、S-1.5、S-1.6 |
| AC-2 原子交付／中斷 | ACCEPTED | S-2.1、S-2.2；正式三支接線 → S-2.3（本 hop Out of Scope 落地，契約在 R-2） |
| AC-3 五家族路由 | ACCEPTED | S-3.1～S-3.5 |
| AC-4 Proof Lab 薄索引 | ACCEPTED | S-4.1～S-4.5 |
| AC-5 預設靜態 SVG | ACCEPTED | S-5.1、S-5.2 |
| Method 信封 `family`／`payload` | ACCEPTED 形狀 | DD-1；R-1 |
| Method 原子寫 tmp+replace | ACCEPTED | DD-4；R-2 |
| Method 不改正式產器／不塞假 fixture | ACCEPTED | Out of Scope 本 hop；S-2.3／S-4.1 留給 Stage 6 |
| Operational Context Recovery（依旋鈕改 IR，不要 checkout 舊 html） | ACCEPTED | S-1.1 Recovery、S-2.2 Recovery |

無 REVISE／NOT_REVIEWED 場景。3-prototype `Human verdict: ACCEPTED` + `human:rick @ 2026-09-12`。2-decision 無「跳過 Stage 3」OC。EMPTY／LINES 兩碼在 Demo Result 表出現，由 S-1.2／S-1.3 承接（Method 走查）。

## 確認紀錄
- 雙源清點 | 2026-09-12 | 驗收雛形 AC-1～AC-5 共 5 條 → ADDED R-1～R-5。living spec `docs/specs/` 0 條。活產器三處 `write_text` 進 MODIFIED M-1～M-3。Decision 剩餘 = A 閘＋D 路由＋G Lab
- R 範圍 | 2026-09-12 | implementer-C 依 Decision A+D+G 與 dispatch「Encode R/S/DD from Decision A+D+G」編碼 R-1～R-5。範圍 = wave-1 IR／路由／Proof Lab／靜態 SVG；排除 Stage 5+、IBV、#196、發版、Mermaid／Node／動畫
- S 展開 | 2026-09-12 | R-1～R-5 全展開；每 S 有觀測欄；交接／等待／系統外動作的 S 有 Operational Context
- 3a 四節 | 2026-09-12 | AC／Out of Scope／Diff Budget／Dependencies 齊
- 3b Profile | 2026-09-12 | lane full、Risk high、Failure Model、Reliability triage、Design Boundary applicable
- 3c Stage 3 | 2026-09-12 | 五個 ACCEPTED Demo 場景 + Method 走查 + Recovery 逐場有下落
- DD 掃描 | 2026-09-12 | 上層八條已拍板待人審；無「待裁決」殘留；不翻已核 Decision；信封／索引／路由檔名／原子寫／閘模組／why 地板已釘
- G2 verdict | 2026-09-12 | **留空**。不代填 PASS。本 hop 只送審形狀（md + gate-twin html）
