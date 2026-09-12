---
feature: diagram-ir-gate
stage: 5-tasks
status: approved
owner: rick
updated: 2026-09-12
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — 圖表 IR 閘（Archify absorb wave-1）

> 把 4-spec（G2 PASS、#242 = `5d01a7a`、R/S 來自 #227）切成可派工縱切。
> 本 hop **只寫任務**，不落地 `scripts/diagir.py`／產器接線、不開 Stage 6、不碰 `#196`／`integration-before-verdict`、不 bump plugin、不發版、不改 `STATUS.md` 表列。
> 模式：sequential（Feature Risk high；見 Split Decisions）。tracer：T-1 先讓壞 IR 收據可觀測，T-2 再原子綠交付，T-3 接現況寫檔，T-4 路由表，T-5 Proof Lab，T-6 靜態／範圍牙。

## 開工前提

Stage 4 已核准。G2 PASS 已在 tip（#242）。本 hop 不改 `4-spec.md`／`4-spec.html`。正式入口是 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`；`docs/dev/diagram-ir-gate/proto/diagir_gate.py` 只對照形狀，不得當 ship。牙仍是既有 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree`／`devflow-check`，不是第二套 `check-diagir-lab.sh`。本 hop 不發明新 R/S。

### N1 R/S 盤點（21 S）

| R | S | 本 hop T |
|---|---|---|
| R-1 驗證失敗保住 last-good 並吐穩定 DIAGIR_* | S-1.1 parked → `DIAGIR_KIND`；S-1.2 空標題 → `DIAGIR_EMPTY`；S-1.3 四行 lines → `DIAGIR_LINES` | T-1 |
| R-1（續） | S-1.4 樹當 vbox → `DIAGIR_FAMILY`；S-1.5 短 why → `DIAGIR_WHY`；S-1.6 收據六鍵 + `DIAGIR_ABORT` | T-1 |
| R-2 通過後才原子交付 | S-2.1 綠生命週期整份新靜態 SVG；S-2.2 中斷留 last-good 與截斷 tmp | T-2 |
| R-2（續） | S-2.3 三支現況寫檔 + vbox 呼叫端接同一閘 | T-3 |
| R-3 五列查找路由表 | S-3.1 五列四欄齊；S-3.2 三框當生命週期 → `DIAGIR_FAMILY`；S-3.3 目錄樹當 vbox → `DIAGIR_FAMILY` | T-4 |
| R-3（續） | S-3.4 缺 family 不黑盒猜；S-3.5 五入口一一對上、無第六列 | T-4 |
| R-4 Proof Lab 薄索引 | S-4.1 六列三家族；S-4.2 三正可重放；S-4.3 三負紅且不蓋檔 | T-5 |
| R-4（續） | S-4.4 不得只靠 lifecycle.json；S-4.5 不得另造 Lab 牙語言 | T-5 |
| R-5 預設靜態直式 SVG 且不收 NON-goal | S-5.1 綠交付無 mermaid／動畫；S-5.2 不改 plugin 版號、不收 #196 | T-6 |

### Verify 開工前原樣跑（2026-09-12；閘尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1 | `bash scripts/test-diagir.sh --group validate -v` → `No such file or directory`，exit 127；`n` 計數 0，`test -ge 6` 紅 | ③綠不了但方向對（牙尚未落地）→ 開工條件成立 |
| T-2 | `--group deliver` 同檔不存在，exit 127；`test -ge 2` 紅 | ③方向對 |
| T-3 | `--group wire` 同檔不存在，exit 127；`test -ge 4` 紅 | ③方向對 |
| T-4 | `--group route` 同檔不存在，exit 127；`test -ge 5` 紅 | ③方向對 |
| T-5 | `--group lab` 同檔不存在，exit 127；`scripts/fixtures/diagir-lab.yaml` 亦不存在 | ③方向對 |
| T-6 | `--group static-scope` 同檔不存在，exit 127；`test -ge 2` 紅 | ③方向對 |

## T-1 讓壞 IR 吐穩定 DIAGIR_* 收據且不蓋 last-good
- [ ] 完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3, S-1.4, S-1.5, S-1.6
- Files: scripts/diagir.py, scripts/test-diagir.sh, scripts/fixtures/diagir/
- Verify: `n=$(bash scripts/test-diagir.sh --group validate -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 6 && bash scripts/test-diagir.sh --group validate`
- Blocked-by: —
- Intent: 日常多一筆機器可讀失敗收據、少一次「打開圖才發現被蓋掉」：開工 agent 餵 parked／空標題／四行／樹當 vbox／短 why 時，終端機看到穩定碼與旋鈕，上一張可審圖還在。改的是正式閘入口與 stdout 收據／stderr 碼行，不是各產器自己印 traceback。不會變成 Cursor 擋寫、不會把 proto 當 ship、不會猜 family、不會在失敗後覆寫目標。
- Boundaries: 只准改 `scripts/diagir.py` 與本 T 牙／信封治具。閘擁有 DIAGIR_* 判定與收據 JSON；請求鍵只有 `family`／`payload`，收據是輸出（鍵 `ok`／`code`／`knob`／`abort`／`delivered`／`target_replaced`），stderr 另印 `FAIL <code>` 與 Q6 該列旋鈕句，且含 `DIAGIR_ABORT`。禁止 import Archify／mermaid／Node、禁止黑盒猜 family、禁止把 `docs/dev/diagram-ir-gate/proto/diagir_gate.py` 當正式入口、禁止驗證失敗後呼叫 `atomic_write`。失敗時目標 sha 必須等於 last-good（Stage 3 sha256 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc` 或測試新寫的同等檔）。入口鎖定 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`。Actor=開工 agent；Goal=壞 IR 不得換掉上一張可審圖；Human decision=依旋鈕改 kind／補欄／改選路由列後重跑；Authority=閘機械拒寫；Recovery=修 IR 再跑，不要 `git checkout` 舊 html。看過 traceback ≠ 已交付。

## T-2 讓綠生命週期原子換成完整靜態 SVG，中斷只留截斷 tmp
- [ ] 完成
- Covers: R-2 / S-2.1, S-2.2
- Files: scripts/diagir.py, scripts/devflow_atomic.py, scripts/test-diagir.sh, scripts/fixtures/diagir/
- Verify: `n=$(bash scripts/test-diagir.sh --group deliver -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-diagir.sh --group deliver`
- Blocked-by: T-1
- Intent: 日常打開的是完整新圖，中斷時舊圖仍打得開：綠生命週期信封通過後目標整份換成靜態 SVG；寫入未 `replace` 時只看得到 last-good 與截斷 `.tmp`。改的是交付原語與成功收據（`ok`／`delivered`／`target_replaced`），不是每支產器各寫一份 tmp 邏輯。不會變成第三支寫檔演算法、不會把截斷 tmp 改名當成功、不會在驗證失敗後呼叫覆寫。
- Boundaries: 原子寫抽出 `scripts/devflow_atomic.py` 的 `atomic_write`，形狀與 `scripts/write-stack-inventory.py` 的 tmp + `os.replace` + 補尾端 newline 相同；inventory 本 slug 可不改。`atomic_write` 擁有寫入原語，不得做驗證，不得在驗證失敗後被呼叫。目標與 tmp 只成功一筆可見：`replace` 前目標全舊。綠交付目標須含 `<svg`、長度大於截斷字串 `<svg viewBox`、不含字面 `mermaid`、sha ≠ last-good；中斷案旁路寫入 `TARGET.tmp` 恰為 `<svg viewBox` 且不呼叫 `replace`。禁止另造第三支幫手。Actor=產檔器；Goal=通過後人打開完整新圖、中斷時審頁仍打得開舊圖；Authority=閘在通過後才 `replace`；Recovery=exit 0 但檔缺 `</svg>` 則本條紅，修原子寫；未 `replace` 視同 `DIAGIR_ABORT`，刪殘 tmp 後重跑綠 IR。

## T-3 把三支現況寫檔與 vbox 呼叫端接到同一閘
- [ ] 完成
- Covers: R-2 / S-2.3
- Files: scripts/build-dir-tree.py, scripts/build-gate-twin.py, scripts/build-stage1-html.py, scripts/build-stage2-html.py, scripts/build-stage4-html.py, docs/dev/tools/build-gate-twin.py, scripts/test-diagir.sh
- Verify: `n=$(bash scripts/test-diagir.sh --group wire -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-diagir.sh --group wire`
- Blocked-by: T-2
- Intent: 日常產目錄樹／審頁／行為流時，失敗不再直接 `write_text` 蓋掉上一張可審檔；wave-1 完成時這幾條覆寫都經同一閘。改的是現況寫檔呼叫端，不是另開一套產器。不會變成 vbox-fig 自己改寫檔、不會跳過驗證就宣稱接線完成、不會把 `docs/dev/tools/` 副本留在舊 `write_text`。
- Boundaries: 產品目標覆寫必須改呼叫 `scripts/diagir.py`（或同模組函式）→ `devflow_atomic.atomic_write`。對帳行：`build-dir-tree.py` 現況 `write_text`、`build-gate-twin.py` 的 `out_local.write_text`、`build-stage1-html.py` 的 `dest.write_text`；vbox-fig 仍只寫 stdout，但 `build-stage2-html.py`／`build-stage4-html.py` 把該 stdout 寫進目標 SVG 的呼叫端必須先走同一閘。gate-twin 正本改完必須 `cp` 同步 `docs/dev/tools/build-gate-twin.py`。產器可組 payload、選 family、讀契約；不得再對目標 `Path.write_text`／`open(path,'w')` 而不經驗證。禁止改 `build-vbox-fig.py` 成自己寫檔、禁止未接閘勾 wave-1 完成、禁止本 T 改 #196 檔或 plugin 版號。Files 超過五檔是因為可觀測行為是「同一閘接上現況覆寫」一刀，不是按產器橫切。Actor=產檔器；Goal=未接閘不得宣稱 wave-1 完成；Authority=S-2.3 用 diff 咬接線，不是 OS hook。

## T-4 落地五列查找路由表並拒錯家族與缺欄
- [ ] 完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5
- Files: notes/design/diagir-route.md, scripts/diagir.py, scripts/test-diagir.sh, scripts/fixtures/diagir/
- Verify: `n=$(bash scripts/test-diagir.sh --group route -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 5 && bash scripts/test-diagir.sh --group route`
- Blocked-by: T-1
- Intent: 日常先打開一張表勾家族，再跑對的產器：三框不會被畫成生命週期四格，目錄樹不會收成單盒 vbox，沒寫 `family` 時機器不得宣稱已選某一列。改的是查找表與閘的家族碼，不是黑盒自動排版、不是一支 API 吃五族。不會變成 mermaid 第六列、不會讓 `stage1-now` 指向 `build-vbox-fig.py`。
- Boundaries: 路由表活檔鎖定 `notes/design/diagir-route.md`。剛好五列，id 集合等於 `{stage1-now, stage2-arch, behavior-flow, dir-tree, vbox-lifecycle}`；每列非空「用這條／不用那條／產器／契約」。契約欄分別指回 `stage1-review-ui-contract`、`stage2-review-ui-contract`+vbox 母版、vbox-fig-contract（twin 收口）、`dir-tree-contract`、`vbox-fig-contract`。產器欄須對上 `build-stage1-html.py --action`、`build-stage2-html.py --action`、`build-gate-twin.py` 行為流、`build-dir-tree.py`、`build-vbox-fig.py` lifecycle，各恰好一列。閘擁有未知 id／缺欄／錯家族 → `DIAGIR_FAMILY`；不得猜 `family`、不得發明第六家族（mermaid／hosted）。`python3 scripts/diagir.py route` 可印五列。改 id 或併 API = 回第 2 站，本 T 不准翻。Actor=開工 agent；Goal=先選家族，不要讓機器猜；Human decision=補上 id 或改跑對的產器；Authority=閘拒猜、拒寫；Recovery=Q6 `DIAGIR_FAMILY` 旋鈕。

## T-5 用薄索引重放三家族各一正一負且不另造 Lab 牙
- [ ] 完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3, S-4.4, S-4.5
- Files: scripts/fixtures/diagir-lab.yaml, scripts/fixtures/vbox-fig/kind-parked.json, scripts/test-diagir.sh, scripts/fixtures/diagir/
- Verify: `n=$(bash scripts/test-diagir.sh --group lab -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 5 && bash scripts/test-diagir.sh --group lab`
- Blocked-by: T-2
- Intent: 日常重放 Lab 時三個負向會紅、上一張圖還在；三個正例可獨立再跑一次。改的是點名既有 fixture 的薄索引，外加 vbox 缺的那張負向樣張。不會變成第二套檢查語言、不會只拿 `lifecycle.json` 綠過就算 Lab、不會讓 `devflow-check` 改走新 Lab 牙取代現有三支。
- Boundaries: 索引檔名鎖定 `scripts/fixtures/diagir-lab.yaml`，`version: 1`，剛好 6 列；`family` 集合 `{vbox-fig, gate-twin, dir-tree}` 且各 1 正 1 負。path 分別為 `scripts/fixtures/vbox-fig/lifecycle.json`、`scripts/fixtures/vbox-fig/kind-parked.json`、`scripts/fixtures/gate-twin/fig-long-label`、`scripts/fixtures/gate-twin/fig-tree-ascii`、`scripts/fixtures/dir-tree/good`、`scripts/fixtures/dir-tree/missing-why`。負向 `expect_code`：`DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`；`tooth_language` 字面 `existing`。vbox 負向本 T 才新增 `kind-parked.json`（落地前形狀須與 Stage 3 parked 信封相同）。索引只准點名，不准發明新 needle。禁止新增 `scripts/check-diagir-lab.sh`（或同等）被 `scripts/devflow-check.sh` 當成取代 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree` 的入口；三支既有牙與 `devflow-check` 仍在。負向三次之後目標 sha 仍是 last-good。本 T 不改那三支牙的演算法。Actor=owner／審查人；Goal=負向紅了 last-good 還在；Human decision=負向紅且檔還在才算 Lab 過；Authority=閘拒寫；Recovery=負向若蓋檔 → wave-1 未完成。

## T-6 釘預設靜態直式 SVG 且本 slug 不碰 plugin 與 #196
- [ ] 完成
- Covers: R-5 / S-5.1, S-5.2
- Files: scripts/test-diagir.sh, scripts/fixtures/diagir/
- Verify: `n=$(bash scripts/test-diagir.sh --group static-scope -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-diagir.sh --group static-scope`
- Blocked-by: T-2
- Intent: 日常打開預設圖仍是可離線看的靜態直式 SVG，成功條件不是「會動」。本 feature 的 diff 也不會順便改 plugin 版號或搶 #196 正在改的檔。改的是範圍牙與綠交付內容斷言，不是新畫法。不會變成 mermaid／Node render／hosted share／WYSIWYG／動畫預設，也不會在本 slug 改 `STATUS.md` 表列或收 IBV。
- Boundaries: 以 T-2 綠交付檔為準，`rg` 字面 `mermaid`、`mermaid.js`、`<animate`、`animateTransform` 必須零命中，且檔含 `<svg>`、靜態幀已是完整圖。`.claude-plugin/plugin.json` 的 `version` 必須與 tip 相同（現況 `3.23.3`）；本 slug diff 不得含 PR #196 正在改的檔（`docs/dev/b8-gate-twin-review-ui/`、`docs/dev/STATUS.md`、`docs/dev/HISTORY.md`、`docs/dev/HISTORY.html`），也不得含 `docs/dev/integration-before-verdict/`、不得新增 Node render／hosted share 依賴。可選 trace（Q8）與 deep-link／Delta／themes／Share Card（Q9）另 slug。本 T 只加牙，不准為了綠而改 plugin 或 #196 檔。Actor=owner；Goal=wave-1 成功條件不是「會動」、範圍不漂；Human decision=看到動畫預設或 plugin bump 就打回；Authority=本 R 與 Non-Goals。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential，不開 parallel | Feature Risk high（公開信封 + last-good 遺失）。T-1／T-2／T-3 都碰 `scripts/diagir.py` 或現況寫檔，硬順序大於省一波。tip 預設 sequential，須明確啟用才改 parallel。 | `_templates/5-tasks.md` `execution.mode` 缺省 sequential；4-spec Verification Profile `Risk: high` | 棄 T-4 ∥ T-3。兩 T 檔案幾乎不重疊，可平行，但本 hop 選保守序：先打通閘與接線再加厚表／Lab。 |
| 六個 T 不是二十一刀 | 可觀測行為是「同一閘入口的失敗碼／原子寫／接線／查表／Lab／範圍」，不是一 S 一 T。21 刀會讓 Files 重複、Verify 碎片。 | 4-spec R-1～R-5 五條行為；模板「一個 T 一個關注點」；owner brief ~5–7 T | 棄「每個 S 一 T」（同一 CLI、同一 last-good 契約被切二十一刀）。 |
| T-1 六個失敗碼當一刀 | 六案共用 `deliver`、同一 last-good、同一收據形；差的是觸發欄。拆開會讓多 T 改同一 `validate()`。 | 4-spec S-1.1～S-1.6「同一閘入口」；S-1.6 對任一失敗案測收據 | 棄「KIND 一 T、EMPTY 一 T、LINES 一 T」。 |
| T-2 與 T-1 分開 | 失敗不寫與成功原子寫是兩條可觀測路徑；T-2 才抽出 `devflow_atomic.py`。先收據後交付 = tracer。 | 4-spec R-1 vs R-2；DD-4／DD-5 | 棄「validate + deliver 同一 T」（Diff Budget 已分子模組，Verify 會混兩套不相干指令）。 |
| T-3 三支產器 + 兩支 vbox 呼叫端 + tools 副本同一刀 | S-2.3 的完成宣稱是「這些覆寫都經同一閘」，不是五層架構。tools 副本與正本必須同一 T 以免 parity 漂。 | 4-spec S-2.3、M-1～M-3、DD-6；`docs/dev/tools/build-gate-twin.py` 散發副本 | 棄「dir-tree 一 T、gate-twin 一 T、stage1 一 T」（同一完成條件、同一閘）。 |
| T-4 Blocked-by 只掛 T-1 | 錯家族／缺欄是驗證碼，不依賴原子寫或產器接線。表檔與 T-3 Files 不重疊。 | 4-spec S-3.2～S-3.4 跑 S-1.1 同一閘；S-3.1／S-3.5 是表字面 | 棄 T-4 等 T-3（會讓查表假依賴接線）。 |
| T-5 Blocked-by T-2 | 三正要 `ok`=true 覆寫測試目標，三負要 last-good；兩者都要正式 `deliver`。索引與 `kind-parked.json` 是 Lab 一刀。 | 4-spec S-4.1～S-4.5、DD-2 | 棄「索引一 T、重放一 T」（同一 yaml、同一完成條件）。棄把 S-4.5 再拆第四 T。 |
| T-6 獨立、Blocked-by T-2 | S-5.1 吃的是 T-2 綠交付檔；S-5.2 是本 slug 範圍牙。併進 T-2 會讓原子寫 Verify 再跑一套不相干的 plugin／#196 斷言。 | 4-spec R-5、S-5.1「用 S-2.1 產出」、S-5.2「本 slug 各 hop 的 PR diff」 | 棄併入 T-2。棄「S-5.2 不切 T」（範圍牙沒有 RED→GREEN 會漏 #196／plugin）。 |
| 本 hop 不切 IBV／#196／STATUS／發版 | owner brief 與 4-spec Out of Scope。本 PR 只准 `5-tasks.md` + twin html。 | 4-spec Out of Scope；本 hop brief | 棄現在寫 Stage 6 notes 或改 `STATUS.md` 表列（OC-4）。 |
