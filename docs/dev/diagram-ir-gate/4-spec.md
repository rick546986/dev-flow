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

> 基準:main tip `9877652`(#218 Stage 3 Human ACCEPTED)。契約不 bump。本 hop **只 Stage 4**：`4-spec.md` + gate-twin html。`verdict` 留空，**不代填 G2**、不開 Stage 5、不落地產器、不碰 `#196`、不發版。
> Decision 正本:`docs/dev/diagram-ir-gate/2-decision.md`（A + D + G；OC-1～OC-4 ✅；G1 `verdict` PASS）。Stage 3 Human ACCEPTED（`human:rick @ 2026-09-12`）。本檔把 Decision 留給 4-spec 的信封欄位、路由表落點、Proof Lab 索引檔名鎖進 R/S／DD。
> 預設圖維持**靜態直式 SVG**。不收 Mermaid／Node／hosted／WYSIWYG／動畫預設。

## 補助模組生命週期（預覽）

主詞是「圖表 IR 閘 + 五家族路由 + Proof Lab 薄索引」，不是整份畫法總冊。直式圖，置中。
- 新生（這輪有）：typed IR 信封＋`DIAGIR_*` 收據；五家族查找路由表；Proof Lab 薄索引。
- 改行為（相關一格）：`build-dir-tree.py`／`build-gate-twin.py`／`build-stage1-html.py` 寫檔從 `write_text` 改接共用 `atomic_write`；vbox-fig 呼叫端寫檔同閘；驗證失敗不取代 last-good。
- 退役：沒有。
- 不動：各家族「不是同一支 API」、mermaid 禁令、#191 牙、`#196`、plugin 版本、Node／hosted／動畫預設、integration-before-verdict。

## ADDED Requirements

### R-1: 系統 SHALL 保留 last-good 並輸出 DIAGIR
沿用 Decision A：共用 typed IR 信封 → 驗證 → 失敗停寫。目標檔位元組與驗證前 last-good 相同。stderr 或收據含穩定 `DIAGIR_*` 碼（六碼之一）＋ Decision 該碼旋鈕句，不是只 traceback。失敗輸出同時含 `DIAGIR_ABORT`。正式產器未接閘不得宣稱 wave-1 完成（S-2.3）。

**審的時候看什麼**
先種一張綠 SVG，再餵會紅的 IR。看目標 sha 有沒有變，以及 stderr／收據是不是穩定碼＋旋鈕，不是 traceback。

#### S-1.1 parked kind 觸發 DIAGIR_KIND 且不蓋檔
- GIVEN 目標檔已是通過驗證的靜態 SVG（位元組記為 last-good）；信封 `family`=`vbox-lifecycle`，`payload.steps[0].kind`=`parked`，其餘三步 `kind` 為 `b`／`hl`／`wn` 之一、標題非空、`lines` 各 1–3 行非空字串
- WHEN 跑 IR 閘 deliver（驗證後才准寫目標）
- THEN exit ≠ 0；目標檔位元組與 last-good 逐位元組相同；stderr 或 JSON 收據 `code`=`DIAGIR_KIND`；旋鈕句與 `2-decision.md` Q6 表 `DIAGIR_KIND` 列原文相同；同一次輸出含 `DIAGIR_ABORT`
- 觀測:從目標檔 sha256 + stderr／收據看 | sha 不變且兩碼都在、不是只 traceback 算過 | 用 Stage 3 `kind-parked` 同形信封測
- Operational Context:
  - Actor:開工 agent
  - Goal:壞 IR 不得換掉上一張可審圖
  - Situation:上一張綠 SVG 已在目標路徑
  - Known information:路由列是 vbox-lifecycle；vbox 只准 kind `b`／`hl`／`wn`
  - Missing information:這次 payload 有沒有夾到禁 kind
  - Human decision:依旋鈕改 kind 或改選路由列，再重跑
  - Authority:閘機械擋寫；審查人只看收據與檔是否仍是 last-good
  - External dependency:無網路；本機檔案
  - Out-of-system action:在終端機跑閘／產器
  - Waiting/timeout behavior:失敗即停寫；目標停在 last-good 直到人重跑
  - Recovery:改 kind 為 `b`／`hl`／`wn` 或改 `family` 後重跑；不要 `git checkout` 舊 html
  - Audit/handoff requirement:收據留下 `code`＋旋鈕句，可供 PR 附上
  - Observation:見本條觀測

#### S-1.2 樹狀當 vbox 觸發 DIAGIR_FAMILY 且不蓋檔
- GIVEN 目標檔已有 last-good；信封 `family`=`vbox-lifecycle`，`payload.kind`=`tree-ascii` 或 `payload.text` 含 `|--`
- WHEN 跑同一支 IR 閘 deliver
- THEN exit ≠ 0；目標位元組與 last-good 相同；`code`=`DIAGIR_FAMILY`；旋鈕句與 Q6 表 `DIAGIR_FAMILY` 列原文相同；同一次輸出含 `DIAGIR_ABORT`
- 觀測:從目標 sha + stderr／收據看 | sha 不變且 `DIAGIR_FAMILY`＋`DIAGIR_ABORT` 都在算過 | 用 Stage 3 `tree-as-vbox` 同形信封測
- Operational Context:
  - Actor:開工 agent
  - Goal:不要把目錄樹／樹狀 ASCII 收成單盒 vbox
  - Situation:手上是樹狀輸入，卻呼叫了 vbox-lifecycle
  - Known information:路由表「行為流／生命週期不用樹收單盒」
  - Missing information:無
  - Human decision:改呼叫 `build-dir-tree.py` 或改寫成直式 `[標籤] 標題`
  - Authority:閘給 `DIAGIR_FAMILY`；人改呼叫
  - External dependency:無
  - Out-of-system action:查 `notes/design/diagram-family-route.md` 後換產器
  - Waiting/timeout behavior:停寫至重跑
  - Recovery:查路由表，改呼叫對的產器
  - Audit/handoff requirement:收據含 `DIAGIR_FAMILY`
  - Observation:見本條觀測

#### S-1.3 短 why 觸發 DIAGIR_WHY 且不蓋檔
- GIVEN 目標檔已有 last-good；信封 `family`=`dir-tree`，`payload.root` 某列 `why` 去掉空白後長度少於 12（對齊 `scripts/build-dir-tree.py` `why_ok` 地板）
- WHEN 跑同一支 IR 閘 deliver
- THEN exit ≠ 0；目標位元組與 last-good 相同；`code`=`DIAGIR_WHY`；旋鈕句與 Q6 表 `DIAGIR_WHY` 列原文相同；同一次輸出含 `DIAGIR_ABORT`
- 觀測:從目標 sha + stderr／收據看 | sha 不變且 `DIAGIR_WHY`＋`DIAGIR_ABORT` 都在算過 | 用 `scripts/fixtures/dir-tree/missing-why` 同形測
- Operational Context:
  - Actor:開工 agent
  - Goal:缺 why 的目錄樹不得蓋掉上一張好樹
  - Situation:YAML 有列 why 過短
  - Known information:why 地板 = 12 字元
  - Missing information:無
  - Human decision:在 YAML 補一句到兩句 why
  - Authority:閘擋寫
  - External dependency:無
  - Out-of-system action:編 YAML 後重跑
  - Waiting/timeout behavior:停寫至重跑
  - Recovery:補 why 使 `len(strip(why)) ≥ 12`
  - Audit/handoff requirement:收據含 `DIAGIR_WHY`
  - Observation:見本條觀測

#### S-1.4 空標題觸發 DIAGIR_EMPTY 且不蓋檔
- GIVEN 目標檔已有 last-good；信封 `family`=`vbox-lifecycle`，某步 `title` 為空或只含空白
- WHEN 跑同一支 IR 閘 deliver
- THEN exit ≠ 0；目標位元組與 last-good 相同；`code`=`DIAGIR_EMPTY`；旋鈕句與 Q6 表 `DIAGIR_EMPTY` 列原文相同；同一次輸出含 `DIAGIR_ABORT`
- 觀測:從目標 sha + stderr／收據看 | sha 不變且 `DIAGIR_EMPTY`＋`DIAGIR_ABORT` 都在算過 | 用 Stage 3 `empty-title` 同形信封測
- Operational Context:不適用 — 形狀擋空字串，無人員交接。

#### S-1.5 四行 lines 觸發 DIAGIR_LINES 且不蓋檔
- GIVEN 目標檔已有 last-good；信封 `family`=`vbox-lifecycle`，某步 `lines` 為 4 個非空字串
- WHEN 跑同一支 IR 閘 deliver
- THEN exit ≠ 0；目標位元組與 last-good 相同；`code`=`DIAGIR_LINES`；旋鈕句與 Q6 表 `DIAGIR_LINES` 列原文相同；同一次輸出含 `DIAGIR_ABORT`
- 觀測:從目標 sha + stderr／收據看 | sha 不變且 `DIAGIR_LINES`＋`DIAGIR_ABORT` 都在算過 | 用 Stage 3 `four-lines` 同形信封測
- Operational Context:不適用 — 形狀擋行數，無人員交接。

#### S-1.6 六碼皆 DIAGIR_ 前綴且人指得到旋鈕
- GIVEN 一次 demo／測試電池涵蓋 KIND／EMPTY／LINES／FAMILY／WHY 各至少一案，外加每案伴隨的 ABORT
- WHEN 收集全部失敗輸出的 `code` 欄
- THEN 集合正好是 `DIAGIR_KIND`、`DIAGIR_EMPTY`、`DIAGIR_LINES`、`DIAGIR_FAMILY`、`DIAGIR_WHY`、`DIAGIR_ABORT` 六個；每個碼旁邊有對應旋鈕句（Q6 表原文）；無人只看到 Python traceback 而沒有碼
- 觀測:從彙總輸出 `CODES_SEEN` 或同等集合看 | 六碼齊、皆 `DIAGIR_` 前綴算過 | 重跑 `python3 docs/dev/diagram-ir-gate/proto/diagir_gate.py demo` 或 Stage 6 正式閘同形電池
- Operational Context:
  - Actor:審查人
  - Goal:PR 附得上機器可讀收據，不是一疊 traceback
  - Situation:負向樣張剛跑完
  - Known information:Q6 六碼表
  - Missing information:無
  - Human decision:收據碼對得上表才往下審圖
  - Authority:碼表在 2-decision；本檔不改碼名
  - External dependency:無
  - Out-of-system action:把收據貼進 PR
  - Waiting/timeout behavior:無
  - Recovery:缺碼 → 當 S-1.6 紅，補閘輸出
  - Audit/handoff requirement:六碼可重放
  - Observation:見本條觀測

### R-2: 系統 SHALL 原子寫交付通過驗證的產出
沿用 Decision A + OC-3：驗證通過後寫入要嘛全新、要嘛全舊。原子原語 = 既有 `atomic_write` 形狀（tmp + `os.replace`），抽到圖表寫路徑共用，不另造第三支寫檔幫手。中斷只准留下截斷 `.tmp`，目標不是半份新 html／svg。

**審的時候看什麼**
綠 IR 是否整檔換成新靜態 SVG；模擬中斷後目標 sha 是否仍是 last-good。三支現況 `write_text` 路徑是否已接同一閘。

#### S-2.1 綠 lifecycle 整檔交付靜態 SVG
- GIVEN 目標檔是 last-good 靜態 SVG；信封為 `scripts/fixtures/vbox-fig/lifecycle.json` 包成 `family`=`vbox-lifecycle` 且四步 kind ∈ {`b`,`hl`,`wn`}
- WHEN 跑 IR 閘 deliver
- THEN exit 0；目標被整檔取代（sha ≠ last-good）；新檔是靜態 inline SVG（含 `<svg`）；檔內無 `mermaid` 字串；無截斷（目標可當 XML／SVG 打開，結尾不是半個 tag）
- 觀測:從 exit、目標 sha、檔頭／檔尾字串看 | exit 0、sha 變、`<svg` 在、`mermaid` 不在、檔尾完整算過 | 用 `lifecycle.json` 測
- Operational Context:
  - Actor:產檔器
  - Goal:看見的要嘛全新、要嘛全舊
  - Situation:IR 已通過
  - Known information:last-good sha、新 SVG 內容
  - Missing information:無
  - Human decision:接受新檔為下一張 last-good
  - Authority:閘在驗證通過後才 `os.replace`
  - External dependency:本機檔案系統
  - Out-of-system action:打開新 SVG／html
  - Waiting/timeout behavior:寫入同步結束
  - Recovery:寫入失敗走 S-2.2；不要用手改半檔
  - Audit/handoff requirement:成功收據 `ok=true`、`delivered=true`
  - Observation:見本條觀測

#### S-2.2 寫入中斷只留截斷 tmp、目標仍全舊
- GIVEN 目標檔是 last-good；閘已通過驗證、已開始寫 `目標路徑 + ".tmp"`，在 `os.replace` 之前行程被停（測試縫：只寫截斷 `.tmp`、不呼叫 `replace`）
- WHEN 檢查目標路徑與 `.tmp`
- THEN 目標位元組與 last-good 相同；`.tmp` 存在且長度小於完整新檔；目標不是半份新 html／svg
- 觀測:從目標 sha + `.tmp` 是否截斷看 | `target_unchanged=True` 且 `tmp_truncated=True` 算過 | 用 Stage 3 `INTERRUPT` 同形測
- Operational Context:
  - Actor:產檔器
  - Goal:中斷後目標仍能當 last-good 打開
  - Situation:寫一半被殺
  - Known information:last-good 仍在目標路徑
  - Missing information:無
  - Human decision:修完再重跑；不要把 `.tmp` 改名當成品
  - Authority:未 `replace` 則目標不變
  - External dependency:本機檔案系統
  - Out-of-system action:刪殘 `.tmp` 後重跑
  - Waiting/timeout behavior:無自動重試
  - Recovery:先修 IR 或重跑同一綠信封
  - Audit/handoff requirement:失敗／中斷收據 `target_replaced=false`
  - Observation:見本條觀測

#### S-2.3 正式寫檔路徑未接閘不得宣稱 wave-1 完成
- GIVEN 現況寫檔點：`scripts/build-dir-tree.py:576` `Path.write_text`、`scripts/build-gate-twin.py:2327` `out_local.write_text`、`scripts/build-stage1-html.py:480` `dest.write_text`；vbox-fig 只寫 stdout，呼叫端若寫檔也算本條
- WHEN 有人宣稱本 slug wave-1 完成（G3 送審或 HISTORY 寫「IR 閘落地」）
- THEN 上列每一條寫檔（含 vbox 呼叫端）都改呼叫共用 `atomic_write`（DD-3），且寫前先跑同一支 IR 驗證；任一點仍直接 `write_text` 覆蓋目標 → 本條 FAIL，wave-1 未完成
- 觀測:從四條寫路徑原始碼看 | 零處殘留「驗證前／閘外 `write_text` 蓋目標」算過 | `rg -n 'write_text' scripts/build-dir-tree.py scripts/build-gate-twin.py scripts/build-stage1-html.py` 對照閘呼叫
- Operational Context:
  - Actor:owner／審查人
  - Goal:正式產器不能繞過閘
  - Situation:throwaway 已證形狀，scripts／ 尚未接
  - Known information:三支現況行號；OC-3 沿用 atomic_write
  - Missing information:Stage 6 是否已改完
  - Human decision:未接閘就拒收「完成」宣稱
  - Authority:本條是完成門檻，不是可選
  - External dependency:無
  - Out-of-system action:讀 diff 對行號
  - Waiting/timeout behavior:未接閘則 G3 不得 PASS
  - Recovery:把寫檔改接閘後重跑 S-1／S-2
  - Audit/handoff requirement:Files 列必須含這三支產器（加 vbox 呼叫端若有寫檔）
  - Observation:見本條觀測

### R-3: 系統 SHALL 用五家族查找路由表擋錯家族
沿用 Decision D：一張查找表，人／agent **先選家族**，再跑對的產器。不是黑盒自動排版，不是 mermaid，不是一支 API 吃全家。錯家族（三框當生命週期、樹收單盒、目錄樹當 vbox）→ `DIAGIR_FAMILY`。

**審的時候看什麼**
表是不是五列、每列有「用這條／不用那條／產器／契約」。錯家族是碼還是機器猜完還是畫出來。

#### S-3.1 路由表五列欄位齊
- GIVEN 檔案 `notes/design/diagram-family-route.md`（本檔 DD-4 鎖的落點）已提交
- WHEN 讀該檔唯一一張五列表
- THEN 列集合正好是 Stage1 現況三框、Stage2 方案架構、行為流、目錄樹、模組生命週期；每列都有非空「用這條」「不用那條」「產器」「契約」四欄；內容與 `2-decision.md`「選定路由表」五行同向（不與 `vbox-fig-contract`／`dir-tree-contract`／`stage1-review-ui-contract`「何時不用」打架）
- 觀測:從該 md 表列數與四欄是否空白看 | 五列四欄皆非空、且能指回 Decision 表算過 | 打開 `notes/design/diagram-family-route.md` 對 `2-decision.md` 選定路由表
- Operational Context:
  - Actor:開工 agent
  - Goal:先查表再選產器
  - Situation:要畫五家族之一
  - Known information:五個現況入口檔名
  - Missing information:這次該走哪一列
  - Human decision:選家族（查找，不是讓機器猜）
  - Authority:表是契約；改「何時不用」要回第 2 站改表
  - External dependency:無
  - Out-of-system action:打開路由表 md
  - Waiting/timeout behavior:無
  - Recovery:選錯 → S-3.2～S-3.4 紅碼，改列再跑
  - Audit/handoff requirement:表在 notes／design，不只活在聊天
  - Observation:見本條觀測

#### S-3.2 三框當生命週期 → DIAGIR_FAMILY
- GIVEN 信封 `family`=`vbox-lifecycle`，`payload` 為 Stage1 三框形（`kind` ∈ {`stage1-now`,`scan-now`,`three-box`} 或 `boxes`=3 或 `scan_now`=true）
- WHEN 跑 IR 閘 deliver
- THEN exit ≠ 0；`code`=`DIAGIR_FAMILY`；目標若已有 last-good 則位元組不變
- 觀測:從收據 `code` + 目標 sha 看 | `DIAGIR_FAMILY` 且不蓋檔算過 | 用 Stage 3 `stage1-as-lifecycle` 同形測
- Operational Context:
  - Actor:開工 agent
  - Goal:不要把第 1 站三框畫成生命週期四格
  - Situation:誤把 scan-now 三框餵給 vbox-lifecycle
  - Known information:路由表「三框不用生命週期」
  - Missing information:無
  - Human decision:改呼叫 `build-stage1-html.py --action`
  - Authority:閘擋
  - External dependency:無
  - Out-of-system action:換產器
  - Waiting/timeout behavior:停寫
  - Recovery:查路由表改呼叫
  - Audit/handoff requirement:收據 `DIAGIR_FAMILY`
  - Observation:見本條觀測

#### S-3.3 目錄樹收單盒 vbox → DIAGIR_FAMILY
- GIVEN 信封 `family`=`vbox-lifecycle` 或 `behavior-flow`，`payload` 為 dir-tree 根（`kind`=`dir-tree` 或含 `root.name`+`why` 樹）
- WHEN 跑 IR 閘 deliver
- THEN exit ≠ 0；`code`=`DIAGIR_FAMILY`；last-good 不變
- 觀測:從收據 + 目標 sha 看 | `DIAGIR_FAMILY` 且不蓋檔算過 | 用 Stage 3 `dir-as-vbox` 同形測
- Operational Context:
  - Actor:開工 agent
  - Goal:目錄樹走 `build-dir-tree.py`，不收成單盒
  - Situation:誤把 YAML 樹當 vbox steps
  - Known information:dir-tree 契約「不是同一支 API」
  - Missing information:無
  - Human decision:改呼叫 dir-tree 產器
  - Authority:閘擋
  - External dependency:無
  - Out-of-system action:換產器
  - Waiting/timeout behavior:停寫
  - Recovery:查路由表
  - Audit/handoff requirement:收據 `DIAGIR_FAMILY`
  - Observation:見本條觀測

#### S-3.4 抽測五個現況入口只落到對列
- GIVEN 五個現況入口：`build-stage1-html.py --action`、`build-stage2-html.py --action`（方案架構）、`build-gate-twin.py` 行為流、`build-dir-tree.py`、`build-vbox-fig.py` lifecycle
- WHEN 對每個入口查路由表「產器」欄
- THEN 每個入口只對到一列；沒有一列把 Stage1 三框寫成生命週期產器，也沒有一列把 `build-dir-tree.py` 寫成 vbox 單盒；表上不出現 mermaid 或「機器猜家族」句
- 觀測:從路由表五列「產器」欄對五個檔名看 | 一對一、零 mermaid、零自動辨識句算過 | 讀 `notes/design/diagram-family-route.md`
- Operational Context:不適用 — 表對表核對，無即時交接。

### R-4: 系統 SHALL 以薄索引重放 Proof Lab
沿用 Decision G + OC-2：延伸既有 `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}`，加一份薄索引。不另開 `scripts/proof-lab/`，不另造第二套檢查語言。牙仍是 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree`／`devflow-check`。vbox-fig／gate-twin／dirmap 各至少一正一負可獨立重放；負向 exit ≠ 0 且不蓋 last-good。不是「只有 `lifecycle.json` 綠過」。

**審的時候看什麼**
索引是不是點名既有目錄。三家族負向紅了目標 sha 有沒有動。有沒有第二套牙。

#### S-4.1 薄索引檔存在且點名六個樣張
- GIVEN 檔案 `scripts/fixtures/diagir-proof-lab.json`（DD-2）
- WHEN 讀該 JSON
- THEN 頂層 `kind`=`diagir-proof-lab`；`families` 長度 = 3，id 為 `vbox-fig`、`gate-twin`、`dir-tree`；每項有 `pos` 與 `neg` 路徑字串；`pos`／`neg` 都落在 `scripts/fixtures/vbox-fig/` 或 `scripts/fixtures/gate-twin/` 或 `scripts/fixtures/dir-tree/` 之下（vbox-fig `neg` 在 Stage 6 補 `scripts/fixtures/vbox-fig/kind-parked.json`；該檔未提交前，重放允許 scratch `kind=parked` 同形，但 wave-1 完成仍要這檔進 Git）
- 觀測:從 JSON 欄位與路徑前綴看 | 三家族、六條路徑、前綴落在既有 fixture 目錄算過 | 打開 `scripts/fixtures/diagir-proof-lab.json`
- Operational Context:
  - Actor:owner／審查人
  - Goal:知道要重放哪六張，不用另學一套語言
  - Situation:要跑 Proof Lab
  - Known information:現有 fixture 目錄
  - Missing information:vbox-fig 正式負例是否已補
  - Human decision:未補正式負例則 wave-1 未完成（與 S-2.3 同門檻）
  - Authority:索引是契約；牙仍是舊牙
  - External dependency:現有 check-*.sh
  - Out-of-system action:開索引再跑牙
  - Waiting/timeout behavior:無
  - Recovery:缺列就補索引，不新開檢查 CLI
  - Audit/handoff requirement:索引進 Git
  - Observation:見本條觀測

#### S-4.2 vbox-fig 一正一負可重放
- GIVEN 索引 `vbox-fig.pos`=`scripts/fixtures/vbox-fig/lifecycle.json`；`vbox-fig.neg`=`scripts/fixtures/vbox-fig/kind-parked.json`（未落地時用 scratch parked 同形）
- WHEN 正例走 IR 閘 deliver；負例走同一閘，目標已有 last-good
- THEN 正例 exit 0 且交付靜態 SVG；負例 exit ≠ 0、`code`=`DIAGIR_KIND`、目標 sha 不變
- 觀測:從兩次 exit／code／目標 sha 看 | 正綠負紅且負向不蓋檔算過 | 對照 `check-vbox-fig.sh` 正例 + 本條負例
- Operational Context:不適用 — fixture 重放，無人員交接。

#### S-4.3 gate-twin 一正一負可重放
- GIVEN 索引 `gate-twin.pos` 指向既有直式行為流樣張（現況可先用 scratch 直式 steps，Stage 6 收成 `scripts/fixtures/gate-twin/` 下一份直式 fixture）；`gate-twin.neg`=`scripts/fixtures/gate-twin/fig-tree-ascii`
- WHEN 正例 deliver；負例把樹狀 ASCII 當 vbox-lifecycle 或 behavior-flow
- THEN 正例 exit 0；負例 exit ≠ 0、`code`=`DIAGIR_FAMILY`、last-good 不變
- 觀測:從 exit／code／sha 看 | 正綠負紅且負向不蓋檔算過 | 負例對齊 `fig-tree-ascii`（#191 樹狀 WARNING+pre 仍在；本條加 IR 碼）
- Operational Context:不適用 — fixture 重放，無人員交接。

#### S-4.4 dir-tree 一正一負可重放
- GIVEN 索引 `dir-tree.pos`=`scripts/fixtures/dir-tree/good`；`dir-tree.neg`=`scripts/fixtures/dir-tree/missing-why`
- WHEN 正例／負例各跑 IR 閘 deliver，負例前目標已有 last-good
- THEN 正例 exit 0；負例 exit ≠ 0、`code`=`DIAGIR_WHY`、目標 sha 不變
- 觀測:從 exit／code／sha 看 | 正綠負紅且負向不蓋檔算過 | 對齊 `check-dir-tree.sh` 短 why 紅
- Operational Context:不適用 — fixture 重放，無人員交接。

#### S-4.5 不是只有 lifecycle.json 綠過、且無第二套牙
- GIVEN S-4.2～S-4.4 都跑過
- WHEN 宣稱 Proof Lab 通過
- THEN 三個負向都曾 exit ≠ 0；禁止只提交 `lifecycle.json` 正例綠就當 Lab 過；repo 內不新增第二套檢查語言入口（不出現 `scripts/check-proof-lab.sh` 當唯一 Lab 牙；Lab 重放呼叫既有 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree` 或同一 IR 閘）
- 觀測:從 Lab 六列結果 + `scripts/check-*.sh` 清單看 | 三負向皆紅、無新唯一 Lab CLI 算過 | 對照 Stage 3 `LAB_INDEX_ROWS 6` 形狀
- Operational Context:
  - Actor:owner
  - Goal:Lab 是對齊舊牙的樣張，不是新方法論
  - Situation:有人想另開 proof-lab 牙
  - Known information:OC-2 拒 H
  - Missing information:無
  - Human decision:拒收第二套牙
  - Authority:Decision G
  - External dependency:既有牙
  - Out-of-system action:讀 scripts／ 檔名
  - Waiting/timeout behavior:無
  - Recovery:刪第二套入口，改掛舊牙
  - Audit/handoff requirement:索引＋舊牙名寫在 5-tasks Files
  - Observation:見本條觀測

### R-5: 系統 SHALL 維持預設靜態直式 SVG
沿用 Non-Goal／SC-6／Q1：wave-1 預設圖仍是靜態直式 SVG。動畫、Mermaid、Node render、hosted share、deep-link、Architecture Delta、themes、Share Card 不是本 slug 成功條件。

**審的時候看什麼**
綠交付裡有沒有 mermaid.js 或自動播放動畫。本 PR 有沒有改 `#196` 或 bump plugin。

#### S-5.1 綠交付不含 mermaid 也不以動畫當成功
- GIVEN S-2.1 剛交付的目標 SVG／html
- WHEN 搜檔案本文
- THEN 無 `mermaid.js`、無 `mermaid` 初始化呼叫；無自動播放 `<animate` 被當成交付成功條件（靜態幀已完整；沒有 animate 也能審）
- 觀測:從目標檔字串看 | 無 mermaid 腳本、靜態幀完整算過 | 用 `lifecycle.json` 交付檔 + `rg -n 'mermaid|<animate' <目標>`
- Operational Context:
  - Actor:owner
  - Goal:第一刀不是動畫
  - Situation:看預設產出
  - Known information:diagram-style 禁外部庫
  - Missing information:無
  - Human decision:看到 mermaid／動畫預設就打回
  - Authority:Q1／SC-6
  - External dependency:無
  - Out-of-system action:瀏覽器直開 html
  - Waiting/timeout behavior:無
  - Recovery:改回靜態 SVG 產器
  - Audit/handoff requirement:預設產出可離線打開
  - Observation:見本條觀測

#### S-5.2 本 slug 不碰 196、不 bump plugin、不發版
- GIVEN 本 feature 的 diff
- WHEN 列變更檔
- THEN 不含 `#196` 目標檔的行為改動；不含 `.claude-plugin/plugin.json` 版本 bump；不含 release tag／CHANGELOG 發版段；不含 `docs/dev/integration-before-verdict/` 過程檔
- 觀測:從 `git diff --name-only` 對 main 看 | 上列路徑不在變更集合算過 | 對本 PR 檔清單
- Operational Context:不適用 — 範圍守衛，無人員交接。

## MODIFIED Requirements

本 repo 無 `docs/specs/` living spec。下列是**現況寫檔行為**（Decision 既有脈絡表），本 feat 改成 R-2。契約「何時不用」原文不改，收成 R-3 路由表。

### M-1: dir-tree／gate-twin／stage1-html 直蓋目標
原條文（現況碼，不是 SHALL 散文）:
- `scripts/build-dir-tree.py:576`：`pathlib.Path(path).write_text(text, encoding="utf-8")`
- `scripts/build-gate-twin.py:2327`：`out_local.write_text(...)`
- `scripts/build-stage1-html.py:480`：`dest.write_text(html_out, encoding="utf-8")`

改成:寫前先跑同一支 IR 驗證；通過才走共用 `atomic_write`（tmp + `os.replace`）。失敗或中斷不取代目標。承接 S-2.2／S-2.3。

vbox-fig 原條文（`scripts/build-vbox-fig.py` 頂註）:只吐 stdout、不寫檔。維持 stdout；**呼叫端**若寫檔，同 M-1 接閘。

## REMOVED Requirements

無。不刪 vbox-fig／dir-tree／stage1「何時不用」、不刪 #191 `fig-ascii-191` 牙、不刪 mermaid 禁令、不刪既有 fixture。

## 行為流程圖(R 級)

```
[R-1] 保留 last-good 並輸出 DIAGIR
  驗 IR 失敗不蓋檔
  stderr 穩定碼加旋鈕
  伴隨 DIAGIR_ABORT
[R-2] 原子寫交付
  通過才 tmp-replace
  中斷目標仍全舊
  產器寫檔接同一閘
[R-3] 五家族查找路由表
  先選家族再呼叫
  五列用這條不用那條
  錯家族 DIAGIR_FAMILY
[R-4] 薄索引重放 Proof Lab
  點名既有 fixture
  三家族各一正一負
  負向不蓋 last-good
[R-5] 維持預設靜態直式 SVG
  無 mermaid.js
  無動畫當成功條件
  不碰 196 不 bump
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-5.2）。
- 既有測試全綠：`check-vbox-fig`／`check-gate-twin`／`check-dir-tree`／`devflow-check` 回歸（#191 樹狀 WARNING+pre 仍綠）。
- 非功能：閘對單份信封在本機同步跑完；不新增網路 capability；預設產出離線可開。
- 行為不變類（畫法鎖死）：golden master — 同一份 `lifecycle.json`，改動前後仍是靜態直式 SVG；mermaid 禁令字面仍在 `_templates/diagram-style.md`。

## Out of Scope

- B／C／E／F／H／I（見 2-decision Rejected）。
- Mermaid 當預設圖；黑盒自動排版；五家族併一支 API。
- Node render／hosted share／WYSIWYG。
- 動畫當預設（Q8 後刀）；deep-link／Architecture Delta／themes／Share Card（Q9 後刀）。
- 本 hop 落地 `scripts/build-*.py` 產器碼、補正式 vbox-fig 負向 fixture 檔（契約在 S-4.2，碼留 Stage 6）。
- `#196`、`#200`、`#201`。
- `integration-before-verdict`。
- 發版／bump `.claude-plugin/plugin.json`。
- 本 hop 寫 `5-tasks.md`／Stage 6／Stage 7。
- 本 feature branch 改 `docs/dev/STATUS.md` 正本表列（OC-4）。
- 把 throwaway `proto/diagir_gate.py` 當成正式產器出貨。

## Diff Budget

本節是**估計**（給後續實作 hop，不是本規格 PR 的檔數）。超支本身非偏差，是停下判 L1/L2 的訊號。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| 抽出 `atomic_write` + IR 閘（驗證／收據／六碼） | ≤3 | ≤220 | ≤180 |
| 三支產器＋vbox 呼叫端接閘 | ≤4 | ≤80 | ≤60 |
| 路由表 `notes/design/diagram-family-route.md` | ≤1 | ≤50 | ≤20 |
| Proof Lab 索引 + vbox-fig `kind-parked.json` + gate-twin 正例收編 | ≤3 | ≤40 | ≤80 |
| **合計** | **≤11** | **≤390** | **≤340** |

[Assumption] 係數按「一個 S 一到兩條測試」，未加 mutation。本規格 PR 本身只動 `docs/dev/diagram-ir-gate/4-spec.md` 與 twin html。

## Dependencies

- `scripts/write-stack-inventory.py` 的 `atomic_write` 形狀 —— justification:OC-3 沿用 tmp+`os.replace`，不另造第三支寫檔幫手。
- `scripts/build-vbox-fig.py` `normalize`（空步驟／錯 kind／空標題／lines 1–3）—— justification:A 的驗證層沿用已擋形，不重寫畫法。
- `scripts/build-dir-tree.py` `why_ok` 地板 12 —— justification:`DIAGIR_WHY` 對齊現有短 why 紅。
- `scripts/check-vbox-fig.sh`／`check-gate-twin.sh`／`check-dir-tree.sh`／`scripts/devflow-check.sh` —— justification:G 對齊現有牙，不另造語言。
- `scripts/fixtures/vbox-fig/lifecycle.json`、`gate-twin/fig-tree-ascii`、`dir-tree/good`、`dir-tree/missing-why` —— justification:Proof Lab 底樣。
- 無新外部服務、無新套件、無 migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ②新增或修改公開 API（產器失敗碼＋寫檔契約）；③跨模組 Interface（IR 信封 `family`／`payload`／收據）；⑧既有 filesystem 寫檔改接閘（capability 持有者是閘，產器不得直蓋）；⑨Feature Risk = high；⑩四支產器＋閘＋索引＋舊牙共同參與；⑪驗證失敗→last-good 直到重跑
- Design source: 既有 pattern —— inventory `atomic_write`、vbox `normalize`、dir-tree `why_ok`、各契約「何時不用」；信封欄位與索引檔名是 Decision 留給本檔的 local lock

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| IR 閘 | 驗信封、發 `DIAGIR_*` 收據、決定寫或不寫 | **擁有**通過／失敗判定與收據欄位 | → 路由表 id、→ 各家族擋形（normalize／why_ok） | 不得猜家族；不得在驗證失敗後寫目標 |
| `atomic_write` | tmp + `os.replace` | **擁有**位元組落盤原語 | → 本機 filesystem | 不得在驗證前被產器呼叫；不得另寫第二份 replace 實作 |
| 路由表 | 五列查找「用這條／不用那條」 | **擁有**家族→產器對照 | → 既有四份契約 | 不得改成黑盒辨識；不得併一支 API |
| 既有產器 | 組 payload、呼叫閘、吐 SVG／html | 各產器擁有家族畫法 | → 閘 → atomic_write | 不得 `write_text` 直蓋；不得 import mermaid／Node |
| Proof Lab 索引 | 點名既有 fixture | **擁有**六條路徑 | → `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}` | 不得新開 `scripts/proof-lab/` 檢查語言 |
| 既有牙 | 重放各家族契約 | 各牙擁有 exit 契約 | → 既有 fixture | 不得被第二套 Lab CLI 取代 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| IR 信封 | in:`family` + `payload`；out:收據 JSON + stderr 兩行 `FAIL` | 六碼見 DD-1；未知 family → `DIAGIR_FAMILY` | 驗證與寫入同一臨界：失敗則目標位元組不變 | 碼名前綴 `DIAGIR_` 鎖定；payload 內形沿用各產器現況 |
| atomic 寫 | in:目標路徑 + 全文；out:目標整檔或未變 | 中斷 → 目標舊、`.tmp` 截斷 | 兩筆「新檔／舊檔」只成功一筆；不准半檔 | 形狀與 inventory 幫手相同 |
| 路由表查找 | in:人選家族；out:產器＋契約路徑 | 選錯 → 閘 `DIAGIR_FAMILY` | 無寫入 | 五列與 Decision 表同向 |
| Proof Lab 重放 | in:索引六路徑；out:三正綠三負紅 | 負向必須 ≠ 0 | 負向不得 replace 目標 | 牙入口仍是舊 check-*.sh |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| `validate(envelope)` | 家族碼＋擋形 | ← payload、← 路由 id | envelope → family 合？→ 家族規則 | 失敗回收據、不寫 | S-1.1～S-1.5、S-3.2～S-3.3 |
| `deliver` | 先驗再寫 | → validate、→ atomic_write | last-good 讀入 → 驗 → replace 或停 | 失敗 `target_replaced=false` | S-2.1／S-2.2 |
| 路由表 md | 人查五列 | ← Decision D | 只讀 | 改表回第 2 站 | S-3.1／S-3.4 |
| 薄索引 JSON | 點名樣張 | ← 既有 fixture | 只讀 | 缺檔 → Lab 未完成 | S-4.1～S-4.5 |
| 產器接縫 | 呼叫閘 | → deliver | 舊 write_text 刪 | 繞閘 = S-2.3 FAIL | `rg write_text` |

### Design Constraints
- 必須:共用閘；六碼前綴 `DIAGIR_`；原子寫 tmp+`os.replace`；路由五列查找；Lab 薄索引點既有目錄；預設靜態直式 SVG。
- 禁止:每產器各寫各的覆寫規則；整包 Archify Node 堆疊；黑盒自動排版；mermaid；第二套 Proof Lab 牙；本 hop 改 STATUS 表列；本 hop 代填 G2 PASS。
- Extension point:Q8 可選 trace／Q9 deep-link 另開 slug；vbox-fig 正式負例檔名已鎖，Stage 6 補檔。
- Known design limit:
  ① 本 hop 不改 `scripts/` 產器；S-2.3／S-4.2 正式負例要等 Stage 6 才有觀測物落地。
  ② 兩行程並寫同一目標無鎖契約（wave-1 假設單 writer）。
  ③ 閘讀信封欄位，不重跑瀏覽器視覺對圖；圖好不好看仍靠人。
  ④ throwaway `proto/diagir_gate.py` 只證形狀，不是出貨碼。

## Verification Profile(G2 一併審)
- lane: full（判準:新能力、改產器公開寫檔／失敗碼契約。owner 已 lock full；無偏離）
- Risk: high（判準:公開 API（失敗碼＋寫檔契約）+ 壞圖蓋掉 last-good 等於審查資料遺失。模板「公開 API／資料遺失」吃這條）
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得在驗證失敗或寫入中斷後取代 last-good（S-1.1～S-1.5、S-2.2）
  - 不得只印 traceback 而無 `DIAGIR_*`（S-1.6）
  - 不得黑盒猜家族、不得 mermaid、不得一支 API 吃五家族（S-3.4）
  - 不得只綠 `lifecycle.json` 就當 Lab 過（S-4.5）
  - 不得另造 Proof Lab 檢查語言（S-4.5、OC-2）
  - 不得把動畫／Node／hosted 當本 slug 成功條件（S-5.1）
  - 不得碰 `#196`／IBV／bump plugin／發版（S-5.2）
  - 不得在本 feature branch 改 STATUS 正本表列（OC-4）
  - 正式產器未接閘不得宣稱 wave-1 完成（S-2.3）
- Required layers:check-spec-gate／check-vbox-fig／check-gate-twin／check-dir-tree／devflow-check
- Conditional layers:Supply chain — 當實作改到 `scripts/build-*.py` 寫檔路徑時，必跑 S-2.3 的 `rg write_text` 對照
- Explicitly excluded layers:Mutation（本 hop 只規格；方法包未把 mutation 列為本 feat 必跑）、e2e／Playwright（無新產品前端）、Race／stress（單 writer，無新併發契約）、Windows 真機（Out of Scope）
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md && bash scripts/devflow-check.sh`
- Reliability triage:
  - Concurrency: n-a — wave-1 假設單一 agent 寫單一目標；無多 writer 鎖（Known limit ②）
  - Idempotency: applicable — 同一失敗信封再跑，`code` 與目標 last-good 位元組相同（S-1.1～S-1.5）
  - Timeout/retry: n-a — 本機檔案、驗證同步結束；失敗不自動重試，人修 IR 再跑（S-1.x Recovery）

Human verdict: ACCEPTED（Stage 3 CLI Demo；`3-prototype.md` attestation `human:rick @ 2026-09-12`）

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 驗證失敗仍蓋檔 | 審查人打開壞圖；last-good 沒了 | 負向後目標 sha 變 | Required:S-1.1～S-1.5 | — |
| 只 traceback 無碼 | PR 無法附收據；人不知旋鈕 | 輸出無 `DIAGIR_` | Required:S-1.6 | — |
| 半份新 html | 目標打不開 | 檔尾半 tag；sha ≠ last-good 且非整檔 | Required:S-2.2 | — |
| 產器繞過閘 | throwaway 綠、正式仍直蓋 | `write_text` 仍蓋目標 | Required:S-2.3 | — |
| 錯家族仍畫出 | 三框當生命週期、樹收單盒 | 錯家族 exit 0 | Required:S-3.2／S-3.3 | — |
| 只綠 lifecycle.json | Lab 假過 | 另兩家族無負向 | Required:S-4.5 | — |
| 第二套 Lab 牙 | 雙源漂 | 新 `check-proof-lab.sh` 當唯一入口 | Required:S-4.5 | — |
| mermaid／動畫當預設 | 違反畫法總冊與 Q1 | 交付含 mermaid.js 或 animate 當成功條件 | Required:S-5.1 | — |
| 兩行程並寫同檔 | 無鎖可能互蓋 | 兩 writer | 明示 Known limit ② | wave-1 不保證 |
| 閘不判「好不好看」 | 人仍可能審到醜但合法圖 | 視覺差、碼仍 PASS | 明示 Known limit ③ | 不新增視覺牙 |

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記 Decision／Stage 3 留給本檔鎖定的選擇。不翻 A + D + G。狀態留「待人審」——**G2 未核，本 hop 不代填 ✅／PASS**。

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 輸入信封鎖定 `{family, payload}`。`family` ∈ {`stage1-now`,`stage2-arch`,`behavior-flow`,`dir-tree`,`vbox-lifecycle`}。`payload` 必為 object。輸出收據鎖定 `{ok, code, knob, abort, abort_knob, delivered, target_replaced}`；失敗另可有 `detail`。stderr 兩行：`FAIL <CODE> \| knob: <旋鈕>` 與 `FAIL DIAGIR_ABORT \| knob: <ABORT 旋鈕>` | OC-1 把欄位留給本檔；Stage 3 已用這組跑通 SC-1／2／5 | `2-decision.md` OC-1；`3-prototype.md:54-56`；`proto/diagir_gate.py` `fail()`／`validate()` | 改欄名則 S-1／S-2 fixture 全改 | 待人審 |
| DD-2 | Proof Lab 薄索引檔名鎖定 `scripts/fixtures/diagir-proof-lab.json`。頂層 `kind`=`diagir-proof-lab`；`families` 三列（vbox-fig／gate-twin／dir-tree）各 `pos`／`neg` | OC-2 把檔名留給本檔；不另開 `scripts/proof-lab/` | `2-decision.md` OC-2；`3-prototype.md:101` | 改路徑則 S-4.1 觀測點變 | 待人審 |
| DD-3 | 共用寫檔函式名 `atomic_write`，形狀 = tmp + `os.replace`，從 `scripts/write-stack-inventory.py` 抽到 `scripts/devflow_atomic_write.py`；inventory 改 import 同一支。圖表寫路徑只准走這支 | OC-3 抽函式落點留給本檔；避免產器各複製一份 | `2-decision.md` OC-3；`scripts/write-stack-inventory.py:30-37` | 落點改回內嵌各產器 = 靠近 B | 待人審 |
| DD-4 | 路由表落點鎖定 `notes/design/diagram-family-route.md`。五列四欄與 Decision「選定路由表」同向。不把表只寫在 4-spec | agent 要有可查契約檔；D 要與四份「何時不用」對帳 | `2-decision.md` 選定路由表；`1-discussion.md:185-186` | 改檔名則 S-3.1 觀測點變 | 待人審 |
| DD-5 | vbox `payload.steps[].kind` 只准 `b`／`hl`／`wn`；`title` 非空；`lines` 1–3 行非空字串。`vbox-lifecycle` 的 `steps` 長度必須 = 4。dir-tree `why` 地板 = 12 字元 | 沿用 vbox normalize 與 dir-tree `why_ok`；生命週期四格是契約 | `scripts/build-vbox-fig.py` normalize；`notes/design/vbox-fig-contract.md:56-65`；`scripts/build-dir-tree.py:262-263` | 改准 kind 或地板要回契約 | 待人審 |
| DD-6 | Feature Risk = high；本檔 `verdict` 留空，由人類 G2 填。DD 狀態留待人審，不代填核可 | 公開寫檔／失敗碼契約 + last-good 遺失；四眼原則；本 hop brief 禁假 G2 | `_templates/4-spec.md` Risk 判準；本 hop「Leave G2 verdict empty」 | 改 normal 則 Failure Model 改選配；代填 PASS = 假綠 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 審頁用 `scripts/build-stage4-html.py --action`；G2 twin 用 `scripts/build-gate-twin.py <根> diagram-ir-gate 4-spec`。不手包 html-shell，不把審頁塞進 gate-twin STAGES。本 hop 以 gate-twin 的 `4-spec.html` 為送審介面。
- 本 hop 不改 `docs/dev/STATUS.md` 正本表列（OC-4）。
- 本 hop 不落地 Stage 6 產器碼；形狀以 R/S 為準。
- `proto/diagir_gate.py` 留作 Demo 重跑，非正式出貨。
- vbox-fig 正式負例檔名 `scripts/fixtures/vbox-fig/kind-parked.json`（Stage 6 補）；未補前重放允許 scratch parked。

## Test Skeletons(選配)

- `test_s_1_1_parked_kind_keeps_last_good`
- `test_s_1_2_tree_as_vbox_family_keeps_last_good`
- `test_s_1_3_short_why_keeps_last_good`
- `test_s_1_4_empty_title_keeps_last_good`
- `test_s_1_5_four_lines_keeps_last_good`
- `test_s_1_6_six_diagir_codes_with_knobs`
- `test_s_2_1_pass_lifecycle_atomic_static_svg`
- `test_s_2_2_interrupt_tmp_target_unchanged`
- `test_s_2_3_official_write_paths_use_gate`
- `test_s_3_1_route_table_five_rows`
- `test_s_3_2_stage1_as_lifecycle_family`
- `test_s_3_3_dir_as_vbox_family`
- `test_s_3_4_five_entries_map_one_to_one`
- `test_s_4_1_proof_lab_index_shape`
- `test_s_4_2_vbox_fig_pos_neg`
- `test_s_4_3_gate_twin_pos_neg`
- `test_s_4_4_dir_tree_pos_neg`
- `test_s_4_5_lab_not_only_lifecycle_no_second_tooth`
- `test_s_5_1_default_static_svg_no_mermaid`
- `test_s_5_2_no_196_no_plugin_bump`

## Stage 3 對帳

| Demo 場景 | Human verdict | 下落 |
|---|---|---|
| AC-1 失敗不蓋 last-good（kind-parked／tree-as-vbox／dir-short-why） | ACCEPTED | S-1.1、S-1.2、S-1.3；EMPTY／LINES 補 S-1.4、S-1.5；六碼 S-1.6 |
| AC-2 原子交付／INTERRUPT | ACCEPTED | S-2.1、S-2.2；正式產器接閘 S-2.3 |
| AC-3 五家族路由（ROUTE_ROWS、錯家族 FAMILY） | ACCEPTED | S-3.1～S-3.4 |
| AC-4 Proof Lab 薄索引六列 | ACCEPTED | S-4.1～S-4.5 |
| AC-5 預設仍是靜態 SVG | ACCEPTED | S-5.1、S-5.2 |
| Method 信封 `family`／`payload`、先驗證再寫 | ACCEPTED 形狀 | DD-1；R-1／R-2 |
| Method 原子寫 tmp+replace | ACCEPTED | DD-3；S-2.1／S-2.2 |
| Operational Context Recovery（改 IR／改路由列再重跑；不要 checkout 舊 html） | ACCEPTED | S-1.1～S-1.3 Recovery |

無 REVISE／NOT_REVIEWED 場景。3-prototype `Human verdict: ACCEPTED` + `human:rick @ 2026-09-12`。2-decision 無「跳過 Stage 3」OC。

## 確認紀錄
- 雙源清點 | 2026-09-12 | 驗收雛形 AC-1～AC-5 共 5 條 → 全數 ADDED（R-1～R-5）。living `docs/specs/` 0 條。現況三支 `write_text` 進 MODIFIED M-1。Decision 剩餘 = 信封欄位／索引檔名／atomic 落點／路由表落點
- R 範圍 | 2026-09-12 | implementer-A 依 Decision A+D+G 與 owner brief「Wave-1: IR gate + route + Proof Lab; static SVG」編碼 R-1～R-5。本 hop 不代填 G2
- S 展開 | 2026-09-12 | R-1～R-5 全展開；每 S 有觀測欄；交接／等待／系統外動作的 S 有 Operational Context
- 3a 四節 | 2026-09-12 | AC／Out of Scope／Diff Budget／Dependencies 齊
- 3b Profile | 2026-09-12 | lane full、Risk high、Failure Model、Reliability triage、Design Boundary applicable
- 3c Stage 3 | 2026-09-12 | 五個 ACCEPTED Demo 場景逐場有 R/S 下落
- DD 掃描 | 2026-09-12 | 上層六條狀態「待人審」（不代填核可）；無「待裁決」殘留；不翻已核 Decision
- G2 verdict | 2026-09-12 | **留空**；status 留 draft。本 hop 不宣稱 G2 PASS
