---
feature: diagram-ir-gate
stage: 5-tasks
status: approved
owner: rick
updated: 2026-09-13
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — 圖表 IR 閘

> 把 4-spec（G2 PASS、#242 = `5d01a7a`、R-1..R-5／S-1.1..S-5.2）切成可派工縱切。
> 本 hop **只寫任務**，不落地 `scripts/diagir.py`、不開 Stage 6、不碰 `#196`／IBV、不 bump plugin、不發版、不改 `STATUS.md` 表列、不發明新 R/S。
> 模式：sequential（4-spec Risk high；owner lock）。tracer：T-1 先讓正式閘對壞 IR 可觀測，T-2 再打通綠交付／中斷，T-3 接三支產器，T-4 落路由表，T-5 建 Lab 索引，T-6 釘 Non-Goal。

## 開工前提

Stage 4 已核准。G2 PASS 已在 tip（#242）。本 hop 不改 `4-spec.md`／`4-spec.html`。正式入口是 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`，不是 `docs/dev/diagram-ir-gate/proto/diagir_gate.py`。原子寫抽出 `scripts/devflow_atomic.py` 的 `atomic_write`（形狀 = `write-stack-inventory.py:30-37`）。Proof Lab 只點名既有牙，不造 `scripts/check-diagir-lab.sh`。

### N1 R/S 盤點（21 S）

| R | S | 本 hop T |
|---|---|---|
| R-1 壞 IR 保住 last-good 並吐 DIAGIR_* | S-1.1 KIND；S-1.2 EMPTY；S-1.3 LINES；S-1.4 FAMILY（樹當 vbox）；S-1.5 WHY；S-1.6 ABORT＋收據六鍵 | T-1 |
| R-2 通過才原子交付 | S-2.1 綠生命週期整份新靜態 SVG；S-2.2 中斷留 last-good＋截斷 tmp | T-2 |
| R-2（續）／M-1..M-3 | S-2.3 三支 `write_text`＋vbox 持久化呼叫端接同一閘 | T-3 |
| R-3 五列查找路由表 | S-3.1 五列四欄；S-3.2 三框當生命週期；S-3.3 目錄樹當 vbox；S-3.4 缺 family 不猜；S-3.5 五入口對五列 | T-4 |
| R-4 Proof Lab 薄索引 | S-4.1 六列三家族；S-4.2 三正可重放；S-4.3 三負不蓋檔；S-4.4 正負 path 不同；S-4.5 不另造 Lab 牙 | T-5 |
| R-5 預設靜態 SVG、不收 NON-goal | S-5.1 無 mermaid／動畫預設；S-5.2 不 bump plugin、不交 #196 檔 | T-6 |

### Verify 開工前原樣跑（2026-09-13；閘／原子寫／索引尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1 | `scripts/test-diagir.sh` 不存在 → 非零 | ③綠不了但方向對（牙尚未落地）→ 開工條件成立 |
| T-2 | 同上，`--group atomic` 不存在 → 非零 | ③方向對 |
| T-3 | 同上，`--group wire` 不存在；現況三處仍是 `write_text` | ③方向對 |
| T-4 | `notes/design/diagir-route.md` 不存在；`--group route` 不存在 → 非零 | ③方向對 |
| T-5 | `scripts/fixtures/diagir-lab.yaml` 與 `kind-parked.json` 不存在 → 非零 | ③方向對 |
| T-6 | `--group nongoal` 不存在 → 非零（S-5.1 尚無綠交付可搜） | ③方向對 |

## T-1 落地正式閘讓壞 IR 吐穩定 DIAGIR_* 且不蓋 last-good
- [ ] 完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3, S-1.4, S-1.5, S-1.6
- Files: scripts/diagir.py, scripts/test-diagir.sh
- Verify: `n=$(bash scripts/test-diagir.sh --group r1 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 6 && bash scripts/test-diagir.sh --group r1`
- Blocked-by: —
- Intent: 日常多一份失敗收據：餵 parked kind、空標題、四行 lines、樹狀當 vbox、dir-tree 短 why 時，終端機看到穩定 `DIAGIR_*` 與旋鈕句，目標檔位元組仍是上一張可審圖。改的是驗證與 stdout 收據／stderr 碼行，不是各產器怎麼畫。不會變成只印 traceback、不會在請求裡放 receipt、不會把 proto 當 ship 入口、不會猜 `family`。
- Boundaries: 只准新建 `scripts/diagir.py`（擁有 `DIAGIR_*` 判定與收據 JSON）與本 T 測試牙。CLI 鎖定 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`。請求信封只有 `family`＋`payload`；收據輸出六鍵 `ok`／`code`／`knob`／`abort`／`delivered`／`target_replaced`；失敗時 `abort` 字面 `DIAGIR_ABORT`、後兩鍵 false；stderr 另有 `DIAGIR_ABORT` 與 Q6 該列旋鈕句。六碼與旋鈕句鎖定 2-decision Q6，本 T 不改碼名。vbox 允許 kind 只有 `b`／`hl`／`wn`；why 地板 12 字。禁止 import Archify／mermaid／Node；禁止黑盒猜 `family`；禁止驗證失敗後寫目標；禁止把 `docs/dev/diagram-ir-gate/proto/diagir_gate.py` 當正式入口。last-good 可用 Stage 3 sha256 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc` 或測試新寫的同等靜態 SVG。Actor=開工 agent；Goal=壞 IR 不得換掉上一張可審圖；Human decision=依旋鈕改 kind／標題／lines／家族後重跑；Authority=閘機械拒寫；Recovery=修 IR 再跑，不要 `git checkout` 舊 html。看過 traceback ≠ 已交付。

## T-2 抽出原子寫並讓綠生命週期整份換新靜態 SVG
- [ ] 完成
- Covers: R-2 / S-2.1, S-2.2
- Files: scripts/devflow_atomic.py, scripts/diagir.py, scripts/test-diagir.sh
- Verify: `n=$(bash scripts/test-diagir.sh --group atomic -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-diagir.sh --group atomic`
- Blocked-by: T-1
- Intent: 日常打開通過後的目標，是完整新靜態 SVG（含 `<svg`、不是截斷 `<svg viewBox`、不含字面 `mermaid`），sha 與 last-good 不同。寫到一半還沒 `replace` 時，審頁仍打得開舊圖，旁邊只留長度 < 20 的 `.tmp`。改的是交付原語，不是另造第三套寫檔法。不會把截斷 tmp 改名當成功，也不會在驗證失敗後呼叫覆寫。
- Boundaries: 抽出 `scripts/devflow_atomic.py` 函式 `atomic_write`，形狀與 `scripts/write-stack-inventory.py:30-37` 相同（tmp + `os.replace` + 補尾端 newline）。本模組擁有寫入原語，不得做驗證，不得在驗證失敗後被呼叫。`deliver` 先 validate 再 atomic_write；未 `replace` 視同 `DIAGIR_ABORT`，目標仍 last-good。inventory 本 slug 可不改。禁止每產器各寫一份 tmp 邏輯。綠信封用 `scripts/fixtures/vbox-fig/lifecycle.json` 包成 `family`=`vbox-lifecycle`。中斷案例旁路寫 `target.svg.tmp` 為 `<svg viewBox` 且不呼叫 `os.replace`。Actor=產檔器；Goal=通過後人打開完整新圖、中斷時舊圖仍在；Authority=只有 `os.replace` 之後目標才變；Recovery=exit 0 但檔缺 `</svg>` → 本條紅，修原子寫；殘 tmp 刪掉後重跑綠 IR。

## T-3 把三支產器與 vbox 持久化呼叫端接到同一閘
- [ ] 完成
- Covers: R-2 / S-2.3
- Files: scripts/build-dir-tree.py, scripts/build-gate-twin.py, scripts/build-stage1-html.py, scripts/build-stage2-html.py, scripts/build-stage4-html.py, docs/dev/tools/build-gate-twin.py, scripts/test-diagir.sh
- Verify: `n=$(bash scripts/test-diagir.sh --group wire -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-diagir.sh --group wire`
- Blocked-by: T-2
- Intent: 日常這三支產器覆寫產品 html／svg 前都先走同一閘；vbox-fig 仍只印 stdout，但 stage2／stage4 把該圖寫進審頁時也先走閘。失敗時上一張可審頁留下。改的是寫檔接線，不是重寫各家族畫法。不會讓 vbox-fig 自己改成寫檔，不會未接閘就勾 wave-1，也不會讓 `docs/dev/tools/build-gate-twin.py` 跟正本漂掉。
- Boundaries: 產品目標覆寫改呼叫 `scripts/diagir.py`（或同模組函式）→ `devflow_atomic.atomic_write`。對帳現況行：`build-dir-tree.py` 的 `write_text`、`build-gate-twin.py` 的 `out_local.write_text`、`build-stage1-html.py` 的 `dest.write_text`；另兩支審頁呼叫端凡把 vbox stdout 寫進目標檔都必須先走同一閘。任一目標覆寫仍直接 `Path.write_text`／`open(path,'w')` 而不經驗證 → 不得勾 wave-1。`build-vbox-fig.py` 維持 stdout（DD-6）。`docs/dev/tools/build-gate-twin.py` 必須與 `scripts/build-gate-twin.py` 逐字一致（既有 N7 牙）。承接 M-1／M-2／M-3。禁止新造 OS hook 擋「硬跑舊 CLI」（Known limit ②）。Files 超過五檔是同一刀「產品覆寫都經閘」，不是按產器層切開。本 T 不改路由表正文、不造 Lab 索引。

## T-4 落下五家族查找路由表並拒錯列與缺欄
- [ ] 完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5
- Files: notes/design/diagir-route.md, scripts/diagir.py, scripts/test-diagir.sh
- Verify: `n=$(bash scripts/test-diagir.sh --group route -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 5 && bash scripts/test-diagir.sh --group route`
- Blocked-by: T-3
- Intent: 日常先打開一張五列表再選 `family`，不再靠機器猜。把第 1 站三框塞進生命週期、把目錄樹當 vbox、或請求沒有 `family` 鍵，一律 `DIAGIR_FAMILY` 且不蓋檔，輸出不得寫「已選／auto／detect」。改的是查找表與閘的家族判定。不會變成一支 API 吃五族，不會加第六列 mermaid／hosted。
- Boundaries: `notes/design/diagir-route.md` 擁有五個 family id，集合必須等於 `{stage1-now, stage2-arch, behavior-flow, dir-tree, vbox-lifecycle}`。每列非空四欄：用這條／不用那條／產器／契約。契約欄分別指回 `stage1-review-ui-contract`、`stage2-review-ui-contract`+vbox 母版、vbox-fig-contract（twin 收口）、`dir-tree-contract`、`vbox-fig-contract`。五入口各恰好一列：`build-stage1-html.py --action`、`build-stage2-html.py --action`、`build-gate-twin.py` 行為流、`build-dir-tree.py`、`build-vbox-fig.py` lifecycle。`stage1-now` 不得指向 `build-vbox-fig.py`；`dir-tree` 不得指向 vbox 或 gate-twin。閘對未知 id／缺欄／錯 payload 家族 → `DIAGIR_FAMILY`，驗證失敗零寫目標。禁止發明第六家族。改 id 或併 API = 回第 2 站。Actor=開工 agent；Goal=先選家族；Human decision=打開表勾一列再跑；Authority=閘拒猜；Recovery=補 `family` 或改呼叫對的產器。

## T-5 建 Proof Lab 薄索引與 kind-parked 負向 fixture
- [ ] 完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3, S-4.4, S-4.5
- Files: scripts/fixtures/diagir-lab.yaml, scripts/fixtures/vbox-fig/kind-parked.json, scripts/test-diagir.sh
- Verify: `n=$(bash scripts/test-diagir.sh --group lab -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 5 && bash scripts/test-diagir.sh --group lab && bash scripts/check-vbox-fig.sh && bash scripts/check-dir-tree.sh && bash scripts/check-gate-twin.sh`
- Blocked-by: T-4
- Intent: 日常重放 Lab 是讀一份六列索引，三家族各一正一負。三正例既有牙綠、閘 `ok`=true；三負例 exit ≠ 0、碼分別 `DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`、目標 sha 仍是 last-good。改的是點名，不是第二套檢查語言。不會只拿 `lifecycle.json` 綠過，不會讓 `devflow-check.sh` 用新 Lab 牙取代現有三支。
- Boundaries: 索引檔名鎖定 `scripts/fixtures/diagir-lab.yaml`；`version: 1`；剛好 6 列；`family` 集合 `{vbox-fig, gate-twin, dir-tree}` 且各 1 正 1 負；`tooth_language` 字面 `existing`。path 鎖定：`scripts/fixtures/vbox-fig/lifecycle.json`、`scripts/fixtures/vbox-fig/kind-parked.json`、`scripts/fixtures/gate-twin/fig-long-label`、`scripts/fixtures/gate-twin/fig-tree-ascii`、`scripts/fixtures/dir-tree/good`、`scripts/fixtures/dir-tree/missing-why`。負向 `expect_code`：`DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`。vbox 負向 path 不得等於正例 path。索引只准點名既有目錄，不准發明新 needle。禁止新增 `scripts/check-diagir-lab.sh`（或同等）被 `scripts/devflow-check.sh` 當成取代 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree` 的入口。牙入口仍是現有四支（含 `devflow-check`）。`kind-parked.json` 結果必須與 Stage 3 `kind-parked` 信封相同。Actor=owner／審查人；Goal=負向紅了 last-good 還在；Human decision=負向紅且檔還在才算 Lab 過；Recovery=負向若蓋檔 → wave-1 未完成。Audit 列印 `neg_held=true`。

## T-6 釘預設靜態 SVG 且本 slug 不碰 plugin 與 #196
- [ ] 完成
- Covers: R-5 / S-5.1, S-5.2
- Files: scripts/test-diagir.sh
- Verify: `n=$(bash scripts/test-diagir.sh --group nongoal -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-diagir.sh --group nongoal`
- Blocked-by: T-5
- Intent: 日常打開 wave-1 預設圖仍是靜態直式 SVG，離線可看，不靠「會動」才算成功。本 slug 的 diff 不升 plugin 版號、不把 #196 正在改的檔當本 feature 交付。不會收 mermaid.js、Node render、hosted share、WYSIWYG、動畫預設、Q8 trace、Q9 deep-link／Delta／themes／Share Card。
- Boundaries: 對 S-2.1 通過後的目標檔搜字面 `mermaid`、`mermaid.js`、`<animate`、`animateTransform` 必須零命中，且檔含 `<svg`。`.claude-plugin/plugin.json` 的 `version` 必須仍是 tip 的 `3.23.3`（對 `5d01a7a` 空 diff）。本 slug 產品 diff 不得包含 PR #196 正在改的檔：`docs/dev/b8-gate-twin-review-ui/7-review.md`、`docs/dev/b8-gate-twin-review-ui/7-review.html`、`docs/dev/b8-gate-twin-review-ui/7-review-review.artifact.html`、`docs/dev/STATUS.md`、`docs/dev/HISTORY.md`、`docs/dev/HISTORY.html`。禁止新 Node／hosted 依賴。禁止本 feature branch 改 `STATUS.md` 正本表列（OC-4）。本 T 只加負向斷言，不改產器畫法。Actor=owner；Goal=wave-1 成功條件不是「會動」；Human decision=看到動畫預設或 plugin bump 就打回。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential，Blocked-by 成 T-1→…→T-6 單鏈 | Feature Risk high（公開信封＋last-good 遺失）。T-2 吃 T-1 的 validate；T-3 吃 T-2 的 `atomic_write`；T-4／T-5 測閘的家族／Lab 重放；T-6 吃綠交付。owner lock sequential。 | 4-spec Verification Profile Risk high；owner Stage 5 brief `execution.mode: sequential` | 棄 T-4∥T-2（檔案幾乎不重疊，可平行，但 brief 要求 sequential）。 |
| T-1 含 S-1.1～S-1.6 同一刀 | 可觀測行為是同一支 `deliver` 對六種壞信封的碼＋不蓋檔，不是六層架構。 | 4-spec S-1.1「同一閘入口」；模板「一個 T 一個關注點」 | 棄「一碼一 T」（同一 Files、同一 CLI）。 |
| S-2.1 與 S-2.2 同 T-2 | 綠交付與中斷是同一原子原語的正／負面；拆開會讓兩 T 改 `devflow_atomic.py`＋`deliver`。 | 4-spec R-2；DD-4 | 棄「綠交付一 T、中斷一 T」。 |
| T-3 列出 6 產器／副本檔 + 測試 | 可觀測行為是「產品覆寫都經閘」。gate-twin 正本一改，N7 牙要求 `docs/dev/tools/` 逐字同步，必須同一 T。 | 4-spec S-2.3、M-1..M-3；`scripts/check-gate-twin.sh` N7 | 棄按產器拆 T（水平切層）。棄漏 tools 副本（合閘後牙紅）。 |
| T-4 接在 T-3 後，不提前 | 路由表測 `DIAGIR_FAMILY` 需要正式閘；sequential 下等接線完成再落表，避免兩 T 同時改 `diagir.py` 家族判定。 | owner suggested split；S-3.2～S-3.4 同一閘 | 棄 T-4 `Blocked-by: T-1`（更誠實的硬依賴，但會與 T-2 搶 `diagir.py`）。 |
| T-5 才造 `kind-parked.json` | DD-2／Known limit ①：正式負向檔 Stage 6 才新增；T-1 用測試內建同形信封即可 RED。 | 4-spec DD-2、S-4.1、S-4.4 | 棄 T-1 就寫 `kind-parked.json`（與「索引六列一起落地」契約拆開）。 |
| T-6 只列測試牙 | S-5.1／S-5.2 是負向回歸，不該為了測「沒改」而把 `plugin.json` 放進 Files（會放寬 scope）。 | 4-spec S-5.2；模板 Files = 預計動的檔 | 棄把 `.claude-plugin/plugin.json` 列入 Files。 |
| Verify 用 `test-diagir.sh --group` + `=== CASE` 計數 | 篩選子集必須自帶案例數斷言；檔尚未落地時整行非零，避免「沒跑也綠」。 | `_templates/5-tasks.md` Verify 三律；host-stack-fit 同形 | 棄只跑 `python3 scripts/diagir.py -h`（無 RED→GREEN）。 |
