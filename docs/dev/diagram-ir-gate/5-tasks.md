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

# 5. 任務 — 圖表 IR 閘

> 把 4-spec（G2 PASS、#242 = `5d01a7a`、R/S 來自 #227）切成可派工縱切。
> 本 hop **只寫任務**，不落地 Stage 6 閘碼、不改 `4-spec.md`／`4-spec.html`、不改 `scripts/` 正本、不碰 `#196`／integration-before-verdict、不 bump plugin、不發版、不改 `STATUS.md` 表列、不發明 R/S。
> 模式：sequential（Feature Risk high，見 Split Decisions）。tracer：T-1 先讓 `DIAGIR_*` 失敗可觀測且不蓋 last-good，T-2 再原子交付，T-3 三支 `write_text` 接閘，T-4 五列路由，T-5 Lab 索引 + parked，T-6 靜態 SVG／範圍牙。

## 開工前提

Stage 4 已核准。G2 PASS 已在 tip（#242）。本 hop 不改 `4-spec.md`／`4-spec.html`。正式閘是 `scripts/diagir.py`，不是 `proto/diagir_gate.py`。Proof Lab 牙仍是現有四支，不是第二套 `check-diagir-lab.sh`。本 hop 不改 `STATUS.md` 表列（OC-4）。

### N1 R/S 盤點（21 S）

| R | S | 本 hop T |
|---|---|---|
| R-1 失敗保住 last-good 並吐 `DIAGIR_*` | S-1.1 `DIAGIR_KIND`；S-1.2 `DIAGIR_EMPTY`；S-1.3 `DIAGIR_LINES`；S-1.4 `DIAGIR_FAMILY`（樹當 vbox）；S-1.5 `DIAGIR_WHY`；S-1.6 `DIAGIR_ABORT` + 收據六鍵 | T-1 |
| R-2 通過才原子交付 | S-2.1 綠生命週期整份換新；S-2.2 中斷留下 last-good 與截斷 tmp | T-2 |
| R-2（續）M-1～M-3 | S-2.3 三支 `write_text` + vbox 呼叫端接同一閘 | T-3 |
| R-3 五列查找路由 | S-3.1 五列齊；S-3.2 三框當生命週期；S-3.3 目錄樹當 vbox；S-3.4 缺 `family`；S-3.5 五入口對五列 | T-4 |
| R-4 Proof Lab 薄索引 | S-4.1 六列三家族；S-4.2 三正可重放；S-4.3 三負不蓋檔；S-4.4 不只要 `lifecycle.json`；S-4.5 不另造 Lab 牙 | T-5 |
| R-5 預設靜態 SVG 且不收 NON-goal | S-5.1 無 mermaid／動畫預設；S-5.2 不 bump plugin、不碰 #196 | T-6 |

### Verify 開工前原樣跑（2026-09-12；閘／索引／測試尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1 | `scripts/fixtures/diagir/run_cases.py` 不存在 → `n=0`，`test -ge 6` 紅 | ③綠不了但方向對（六碼案例尚未落地）→ 開工條件成立 |
| T-2 | 同上，`--group r2` → `n=0`，`test -ge 2` 紅 | ③方向對 |
| T-3 | 同上，`--group wire` → `n=0`，`test -ge 1` 紅；三處 `write_text` 仍在 tip 行號 | ③方向對 |
| T-4 | 同上，`--group r3` → `n=0`，`test -ge 5` 紅；`notes/design/diagir-route.md` 尚無 | ③方向對 |
| T-5 | 同上，`--group r4` → `n=0`，`test -ge 5` 紅；`diagir-lab.yaml`／`kind-parked.json` 尚無 | ③方向對 |
| T-6 | 同上，`--group r5` → `n=0`，`test -ge 2` 紅。單獨量 `git diff 9877652 -- .claude-plugin/plugin.json` 已是空 diff（不具鑑別力，斷言放進尚未落地的 `test_s_5_2`） | ③整欄紅、方向對 |

## T-1 落地閘驗證讓壞 IR 吐 DIAGIR_* 且不蓋 last-good
- [ ] 完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3, S-1.4, S-1.5, S-1.6
- Files: scripts/diagir.py, scripts/test-diagir.sh, scripts/fixtures/diagir/
- Verify: `n=$(python3 scripts/fixtures/diagir/run_cases.py --group r1 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 6 && python3 scripts/fixtures/diagir/run_cases.py --group r1`
- Blocked-by: —
- Intent: 日常餵壞 IR 時，系統多了穩定收據：stdout 一筆 JSON（鍵 `ok`／`code`／`knob`／`abort`／`delivered`／`target_replaced`），stderr 印該 `DIAGIR_*` 與 Q6 旋鈕句另含 `DIAGIR_ABORT`，目標檔 sha 仍是上一張可審圖。改的是驗證與收據，不是各產器怎麼畫。不會變成只印 traceback，也不會在缺 `family` 時猜列。
- Boundaries: 只准新寫 `scripts/diagir.py` 的 validate／deliver 失敗路徑，以及 `scripts/test-diagir.sh` 與 `scripts/fixtures/diagir/`（案例名對齊 4-spec Test Skeletons：`test_s_1_1`～`test_s_1_6`）。正式入口是 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`（DD-5）；`docs/dev/diagram-ir-gate/proto/diagir_gate.py` 只當對照，不得當 ship。閘擁有 `DIAGIR_*` 判定與收據 JSON；不得 import Archify／mermaid／Node；不得猜 `family`。驗證失敗零寫目標（`target_replaced`=false；last-good 可對 Stage 3 sha256 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc` 或測試新寫的同等檔）。本 T 尚未抽出 `atomic_write`，不得新造第三支寫檔演算法，也不得用 `Path.write_text` 蓋目標。錯誤碼鎖定 R-1：`DIAGIR_KIND`／`DIAGIR_EMPTY`／`DIAGIR_LINES`／`DIAGIR_FAMILY`／`DIAGIR_WHY`，失敗另印 `DIAGIR_ABORT`。信封鍵只有 `family`+`payload`（DD-1）。Diff Budget（4-spec 估計）：本 T 落在 `scripts/diagir.py` 列（≤1 檔、非測試 ≤220、測試 ≤180）；超支本身非偏差，是停下判 L1/L2 的訊號。禁碰 `#196`、integration-before-verdict、plugin 版號、`STATUS.md` 表列、mermaid／Node／動畫預設。作業脈絡（S-1.1）：Actor=開工 agent；Goal=壞 IR 不得換掉上一張可審圖；Human decision=改 kind 或改選路由列後重跑；Authority=閘機械拒寫；Recovery=依 Q6 旋鈕改 IR 再跑，不要 `git checkout` 舊 html。看過收據 ≠ 已修好。

## T-2 抽出 atomic_write 讓綠 IR 整份換新、中斷只留截斷 tmp
- [ ] 完成
- Covers: R-2 / S-2.1, S-2.2
- Files: scripts/devflow_atomic.py, scripts/diagir.py, scripts/fixtures/diagir/
- Verify: `n=$(python3 scripts/fixtures/diagir/run_cases.py --group r2 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 2 && python3 scripts/fixtures/diagir/run_cases.py --group r2`
- Blocked-by: T-1
- Intent: 綠生命週期通過後，人打開的是完整新靜態 SVG（檔含 `<svg`、長度大於截斷字串 `<svg viewBox`、不含字面 `mermaid`、sha ≠ last-good，收據 `ok`／`delivered`／`target_replaced` 皆 true、`code` 為 null）；寫到一半尚未 `replace` 時舊圖還在，旁邊只留長度 < 20 的 `.tmp`。改的是寫入原語與 deliver 成功路徑。不會每支產器自寫一套 tmp 邏輯，也不會把截斷 tmp 改名當交付。
- Boundaries: 只准新寫 `scripts/devflow_atomic.py` 的 `atomic_write`，並讓 `diagir.deliver` 在 validate 通過後才呼叫。形狀必須與 `scripts/write-stack-inventory.py:30-37` 相同（tmp + `os.replace` + 補尾端 newline）；inventory 本 slug 可不改（DD-4）。`atomic_write` 擁有寫入原語：不得做驗證，不得在驗證失敗後被呼叫。一致性：目標與 tmp 只成功一筆可見，`replace` 前目標全舊；未 `replace` 視同 `DIAGIR_ABORT`。vbox-fig 本 T 仍不寫檔。案例名 `test_s_2_1_pass_lifecycle_atomic_svg`／`test_s_2_2_interrupt_keeps_last_good`；綠信封由 `scripts/fixtures/vbox-fig/lifecycle.json` 包成 `family`=`vbox-lifecycle`。Diff Budget：`devflow_atomic.py` ≤1 檔、非測試 ≤40、測試 ≤30；diagir 成功路徑吃 T-1 同一份 ≤220 預算的剩餘。禁第三支寫檔演算法、禁 `#196`／IBV／plugin／STATUS／mermaid。作業脈絡（S-2.1／S-2.2）：Actor=產檔器；Goal=通過後人打開完整新圖，中斷時審頁仍打得開舊圖；Human decision=接受新圖進審頁，或修 IR 重跑且不要把 `.tmp` 改名當交付；Authority=只有 `os.replace` 之後目標才變。

## T-3 把三支 write_text 與 vbox 呼叫端改接同一閘
- [ ] 完成
- Covers: R-2 / S-2.3
- Files: scripts/build-dir-tree.py, scripts/build-gate-twin.py, scripts/build-stage1-html.py, scripts/build-stage2-html.py, scripts/build-stage4-html.py, scripts/fixtures/diagir/
- Verify: `n=$(python3 scripts/fixtures/diagir/run_cases.py --group wire -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1 && python3 scripts/fixtures/diagir/run_cases.py --group wire`
- Blocked-by: T-2
- Intent: 日常產樹圖／gate-twin／第 1 站審頁時，目標產品檔不再被 `Path.write_text` 直接蓋掉；驗證失敗留下上一張 html／svg。改的是三處覆寫，以及把 vbox stdout 寫進目標檔的呼叫端。不會讓 vbox-fig 自己寫檔，不會另造寫檔演算法，也不會未接閘就勾 wave-1 完成。
- Boundaries: 只准改 M-1 `scripts/build-dir-tree.py:574-576`、M-2 `scripts/build-gate-twin.py:2327`、M-3 `scripts/build-stage1-html.py:480`，以及把 vbox stdout 持久化的 `scripts/build-stage2-html.py`／`scripts/build-stage4-html.py` 呼叫端。目標覆寫必須 `scripts/diagir.py`（或同模組函式）→ `devflow_atomic.atomic_write`。產器組 payload、選 family；不得再對目標 `Path.write_text`／`open(path,'w')`。vbox-fig 仍只寫 stdout（DD-6），本 T 不把它改成自己寫檔，故不列入 Files。主機層不擋「跳過閘硬跑舊 write_text」（4-spec Known limit ②）；本 T 用 diff 咬接線，不是 OS hook。案例名 `test_s_2_3_builders_wire_same_gate`。Diff Budget：三支產器 + vbox 呼叫端 ≤5 檔、非測試 ≤120、測試 ≤80；本 T Files 多一列測試目錄是為了 scope guard，不算第六個產品檔。禁改既有四支牙、禁 `#196`／IBV／plugin／STATUS／mermaid。接線範圍無現場人員交接。

## T-4 落五列路由表讓錯家族與缺 family 都 DIAGIR_FAMILY
- [ ] 完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5
- Files: notes/design/diagir-route.md, scripts/diagir.py, scripts/fixtures/diagir/
- Verify: `n=$(python3 scripts/fixtures/diagir/run_cases.py --group r3 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 5 && python3 scripts/fixtures/diagir/run_cases.py --group r3`
- Blocked-by: T-3
- Intent: 日常先打開路由表勾一列再跑；把第 1 站三框當生命週期、把目錄樹當 vbox、或 JSON 漏掉 `family` 鍵，收據都是 `DIAGIR_FAMILY` 且不蓋檔。改的是一張五列表與閘的查找。不會黑盒猜列，不會長出第六列 mermaid／hosted。
- Boundaries: 只准新寫 `notes/design/diagir-route.md`，並讓 `diagir` 按人選的 family 查找（可加 `route` 印五列）。五 id 凍結：`stage1-now`／`stage2-arch`／`behavior-flow`／`dir-tree`／`vbox-lifecycle`。每列都有非空「用這條」「不用那條」「產器」「契約」；契約欄分別指回 `stage1-review-ui-contract`、`stage2-review-ui-contract`+vbox 母版、vbox-fig-contract（twin 收口）、`dir-tree-contract`、`vbox-fig-contract`。路由表擁有 family id；不得發明第六家族；不得 import mermaid／Node。缺欄或未知 id → `DIAGIR_FAMILY`；輸出不得宣稱已選／auto／detect。五入口各恰好一列：`build-stage1-html.py --action`、`build-stage2-html.py --action`、`build-gate-twin.py` 行為流、`build-dir-tree.py`、`build-vbox-fig.py` lifecycle。`stage1-now` 不得指向 `build-vbox-fig.py`；`dir-tree` 不得指向 vbox 或 gate-twin。改 id = 回第 2 站。案例名 `test_s_3_1`～`test_s_3_5`。Diff Budget：與 T-5 共用 route+lab+parked ≤3 檔、非測試 ≤80、測試 ≤40；本 T 只消耗 `diagir-route.md` 那一檔。禁 `#196`／IBV／plugin／STATUS。作業脈絡（S-3.2／S-3.4）：Actor=開工 agent；Goal=先選家族，不要讓機器猜；Human decision=補上 id 或改跑對的產器；Authority=閘拒猜。

## T-5 落 Proof Lab 薄索引與 parked fixture 讓三正三負可重放
- [ ] 完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3, S-4.4, S-4.5
- Files: scripts/fixtures/diagir-lab.yaml, scripts/fixtures/vbox-fig/kind-parked.json, scripts/fixtures/diagir/
- Verify: `n=$(python3 scripts/fixtures/diagir/run_cases.py --group r4 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 5 && python3 scripts/fixtures/diagir/run_cases.py --group r4`
- Blocked-by: T-4
- Intent: 日常重放 Lab 時，六列索引點名既有 fixture：三正可獨立綠（牙 + 閘 `ok`=true），三負紅且 last-good sha 不變。改的是薄索引與 vbox 負向樣張。不會另造 `check-diagir-lab.sh` 當第二套牙，也不會只靠 `lifecycle.json` 綠過就算 Lab。
- Boundaries: 只准新寫 `scripts/fixtures/diagir-lab.yaml` 與 `scripts/fixtures/vbox-fig/kind-parked.json`。索引 `version: 1`、剛好 6 列、`family` 集合為 `{vbox-fig, gate-twin, dir-tree}` 且各 1 正 1 負；`path` 鎖定為 `scripts/fixtures/vbox-fig/lifecycle.json`、`scripts/fixtures/vbox-fig/kind-parked.json`、`scripts/fixtures/gate-twin/fig-long-label`、`scripts/fixtures/gate-twin/fig-tree-ascii`、`scripts/fixtures/dir-tree/good`、`scripts/fixtures/dir-tree/missing-why`；負向 `expect_code`：`DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`；`tooth_language` 字面 `existing`。索引擁有正負 path：只准點名既有 fixture 目錄，不准發明新 needle 語言。牙入口仍是 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree`／`devflow-check`（S-4.2 三正必須能被這三支牙吃到）。禁止 `scripts/check-diagir-lab.sh`（或同等）被 `scripts/devflow-check.sh` 當成取代三支牙的入口。負向不得 `replace` 目標。`kind-parked.json` 落地前重放須與 Stage 3 `kind-parked` 信封同結果（DD-2）。案例名 `test_s_4_1`～`test_s_4_5`。Diff Budget：與 T-4 共用 ≤3 檔的剩餘兩檔。禁 `#196`／IBV／plugin／STATUS／mermaid。作業脈絡（S-4.3）：Actor=owner／審查人；Goal=負向紅了 last-good 還在；Human decision=負向紅且檔還在才算 Lab 過。

## T-6 釘預設靜態 SVG 且本 slug 不碰 plugin 與 #196
- [ ] 完成
- Covers: R-5 / S-5.1, S-5.2
- Files: scripts/fixtures/diagir/, scripts/test-diagir.sh
- Verify: `n=$(python3 scripts/fixtures/diagir/run_cases.py --group r5 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 2 && python3 scripts/fixtures/diagir/run_cases.py --group r5`
- Blocked-by: T-5
- Intent: 綠交付打開仍是靜態直式 SVG（含 `<svg`，零命中 `mermaid`／`mermaid.js`／`<animate`／`animateTransform`）；本 slug 的 diff 不改 plugin 版號、不帶 #196 正在改的檔、不加 Node render／hosted share 新依賴。改的是範圍牙與綠交付內容檢查。不會把「會動」當成功條件，也不會收 Q8／Q9。
- Boundaries: 本 T 不改產品產器，只准在 `scripts/fixtures/diagir/` 與 `scripts/test-diagir.sh` 加 S-5.1／S-5.2 斷言。S-5.1 吃 T-2 的綠目標（`test_s_5_1_default_static_svg_no_mermaid`）。S-5.2（`test_s_5_2_no_plugin_bump_no_196`）對本 feature git diff（4-spec 寫相對 `9877652`）：`.claude-plugin/plugin.json` 的 `version` 與 tip 相同、該路徑空 diff；變更清單不含 PR `#196` 正在改的檔當本 slug 交付，也不含 Node render／hosted share 新依賴。禁 bump plugin、禁碰 `#196`／`#200`／`#201`、禁 IBV、禁改 `STATUS.md` 表列、禁 mermaid／動畫預設。Diff Budget：本 T 不新增產品檔，測試行吃 diagir 列剩餘；合計產品檔仍應對齊 4-spec ≤10／非測試 ≤460／測試 ≤330。作業脈絡（S-5.1）：Actor=owner；Goal=wave-1 成功條件不是「會動」；Human decision=看到動畫預設就打回。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential，不開 parallel | Feature Risk high（公開 `DIAGIR_*`／信封；失敗會遺失上一張可審圖）。T-1～T-4 都碰 `scripts/diagir.py`，T-1～T-6 都碰 `scripts/fixtures/diagir/`，Files 重疊。tip 預設 sequential，須明確啟用才改。 | `_templates/5-tasks.md` `execution.mode` 缺省 sequential；4-spec Verification Profile Risk high | 棄 T-1 ∥ T-4。家族碼與路由都碰 `DIAGIR_FAMILY`，檔重疊且語意相依。 |
| T-1 六碼同一刀 | 可觀測行為是同一閘的失敗不蓋檔，不是六層架構。S-1.6 吃任一失敗案的收據形。 | 4-spec R-1「審的時候看什麼」；S-1.6 GIVEN | 棄「一碼一 T」（同一函式、同一 Files）。 |
| T-2 與 T-1 分開 | 失敗路徑與原子寫是兩件可觀測事；DD-4 要抽出 `atomic_write`。 | 4-spec R-2／DD-4／S-2.1／S-2.2 | 棄「validate+write 同一 T」（會把 atomic 與六碼測試綁死）。 |
| M-1～M-3 同 T-3 | S-2.3 明寫三支現況 `write_text` + vbox 呼叫端同一閘；拆開會讓三 T 改同一接線契約。 | 4-spec S-2.3、M-1～M-3、DD-6 | 棄「一產器一 T」。 |
| 路由與 Lab 分開 | 五列表與六列索引是兩件可觀測事。Diff Budget 把它們列在同一 ≤3 檔列，仍是兩關注點。 | 4-spec R-3／R-4；Diff Budget 第 4 列 | 棄併成一 T。 |
| S-5.1／S-5.2 同 T-6 | 範圍牙：預設靜態 + 不碰 plugin／#196；無新產品檔。plugin 空 diff 開工前已綠，不得單獨當 Verify。 | 4-spec R-5／S-5.1／S-5.2 | 棄把 S-5.2 散進每個 T 的 Verify（會讓已綠的 plugin 空 diff 假綠整 T）。 |
| 不發明 R/S | Covers 只承接 4-spec 已核 R-1～R-5／S-1.1～S-5.2。M-1～M-3 是活產器寫檔改口，掛在 T-3，不另造 S。 | #242 G2 PASS；4-spec「不發明新 R/S」 | 棄補「S-6.*」或把 IBV 的 R 寫進來。 |
