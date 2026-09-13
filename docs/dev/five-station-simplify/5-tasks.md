---
feature: five-station-simplify
stage: 5-tasks
status: draft
owner: implementer-A
updated: 2026-09-14
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — F1 牙 + dual-read annex（Implementer A）

> 基準:`4-spec.md` G2 PASS（`verdict: PASS`、`status: approved`、main tip `318ccd9`／#316）。Lane = **full**。契約不 bump。
> 本 hop **只寫任務雙檔**，不落地 `scripts/`／annex、不改 `STATUS.md`／`HISTORY.md`、不發明 G3、不 merge。
> Scope lock（S-8.5／S-8.1）：本 slug Stage 5–7 **只 F1**。Files 聯集只准 `scripts/` 新牙 + 本 slug annex + 本目錄 5／6／7 過程檔。**不准** F2 coordinator、**不准** F3 切 `graph.yaml` 預設路線、**不准**改 `_templates/` Stage 1–4。
> Diff Budget F1：annex ≤2 檔；`scripts/` 新牙 ≤4 檔；F2／F3 = 0。本檔 Files 聯集已收在這格內。
> tracer（A 線）：T-1 先打通 **RP-16**（Agent 代寫 `ACCEPTED`／Ship `PASS` = 未寫並紅）端到端 RED→GREEN selftest；再加厚 dual-read 九個 SLOT annex，再補其餘 RP 牙。
> 執行者只准讀本檔 + `4-spec.md` + living／`CONTEXT.md`。禁讀 1／2／3 補洞。

## 開工前提

Stage 4 已核准。本 slug 自己仍走舊 7（S-5.2）。F1 牙是**新家族** `scripts/check-five-station-f1.sh`（加 `scripts/five_station_f1.py` 實作、`scripts/test-five-station-f1.sh` 自檢），不是改既有 doctor 握手、不是改 `_stage3_impl.py`、不是新開 coordinator。
負向對照稿目錄：`scripts/fixtures/five-station-simplify/`（4-spec DD 下層建議；本 hop 只點名，Stage 6 才新增檔）。
annex 兩檔（OC-3：**不鎖鍵名**，只鎖 SLOT- id 與 RP 列語意）：
- `notes/design/five-station-simplify-f1-dual-read-annex.md`（九個 SLOT）
- `notes/design/five-station-simplify-f1-rp-min-set.md`（RP-1…RP-16 只准加）
Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。
Q6 維持 Assumption／open（S-6.2／S-6.3）。1B／2B／4C／6B／7C 不得重開（S-8.6，T-12 具名對照稿）。

### 本 hop 點名對照稿（Stage 6 才建檔；Verify 必須點到檔名，不是只寫 `-ge N`）

| T | 檔（皆在 `scripts/fixtures/five-station-simplify/`） | 紅什麼 |
|---|---|---|
| T-9 | `rp-13-empty-attestation-plus-chat.md` | 空 attestation + chat「可以開 Stage 4」仍不得離 Spec（RP-13） |
| T-9 | `rp-12-miss-forced-accepted.md` | 未命中卻強迫 ACCEPTED（RP-12）；同時不建 Demo 頁（S-1.7） |
| T-9 | `rp-14-please-review-latch-false.md` | latch=否卻留下請人審（RP-14） |
| T-9 | `skip-negation-as-oc.md` | 「不／無／不得」+「跳過」不得當 skip OC（S-4.5） |
| T-11 | `rp-09-third-hop-rewrite.md` | hop 重寫第 3 次仍繼續（RP-9 超 cap） |
| T-11 | `rp-10-second-decide-reopen.md` | Decide 重開第 2 次仍繼續（RP-10 超 cap） |
| T-11 | `rp-11-second-goal-reopen.md` | Goal 重開第 2 次仍繼續（RP-11 超 cap） |
| T-12 | `reopen-1b-delete-tokens.md` | 正文含「改採」+ 1B（刪 token）→ 紅 |
| T-12 | `reopen-2b-old-file-red.md` | 正文含「改採」+ 2B（舊檔缺欄就紅）→ 紅 |
| T-12 | `reopen-4c-this-slug-as-new5.md` | 正文含「改採」+ 4C（本 slug 當新 5）→ 紅 |
| T-12 | `reopen-6b-must-keep-optional.md` | 正文含「改採」+ 6B（M 可選）→ 紅 |
| T-12 | `reopen-7c-merge-knives.md` | 正文含「改採」+ 7C（併刀）→ 紅 |

### N1 R/S 盤點（52 S；本 hop 只承 F1）

| R | F1 必須落地的 S | 本 hop T |
|---|---|---|
| R-3 | S-3.1 Agent 代寫判定 = 未寫（RP-16） | T-1 |
| R-5 | S-5.8 annex 九個 SLOT | T-2 |
| R-5 | S-5.4、S-5.5、S-5.6、S-5.7、S-5.9 dual-read 誠實 | T-3 |
| R-5 | S-5.1、S-5.2、S-5.3 in-flight／本 slug 凍舊 7 | T-4 |
| R-2 | S-2.2 缺四欄或 Verify 看起來沒問題 → 卡上紅（RP-1） | T-5 |
| R-2 | S-2.3 無 RED／自審（RP-2）；S-2.9 無原始輸出（RP-6） | T-6 |
| R-2 | S-2.4 模糊／不可測 S（RP-3）；S-2.5 測試名無 S-id（RP-4） | T-7 |
| R-2 | S-2.1 少 Must-keep 違 brief；S-2.7 可選四欄擋 G2；S-2.8 Files 聯集（RP-5） | T-8 |
| R-4／R-1 | S-4.1…S-4.5 attestation／強迫 ACCEPTED／請人審／否定跳過（RP-12／13／14）；S-1.7 未命中不建頁 | T-9 |
| R-1／R-3 | S-1.10 不可逆無 Quiz（RP-7）；S-3.2 Ship 無人 PASS 卻 Done（RP-8）；S-3.3 Evidence 八點 | T-10 |
| R-2 | S-2.6 RP-1…16 只准加；十六個對照各紅一次（含超 cap 三張具名卡） | T-11 |
| R-1／R-6／R-8 | S-1.1 七檔名＋token 仍在；S-6.2／S-6.3 Q6 不升格；S-8.1／S-8.5 F1 收口；S-8.6 不得重開已拒案 | T-12 |

### Out-of-this-slug 延後表（F2／F3／已綠；不發明 T）

| S | 為什麼本 hop 不開 T | 去向 |
|---|---|---|
| S-1.2、S-1.3、S-1.4、S-1.5、S-1.6、S-1.8、S-1.9、S-1.11、S-1.12 | F2 coordinator 評表 A／B、產頁／latch／HumanWait | 另刀 F2（S-8.2）。S-1.7 未命中不建頁謂詞由 T-9 承接；coordinator 產頁引擎仍交 F2 |
| S-7.1、S-7.2、S-7.3、S-7.4 | 計數落點交 F2；舊 7 不套三 cap | 另刀 F2。F1 只在 T-11 用**對照稿**讓 RP-9／10／11 各紅一次，不選 event 鍵名、不寫計數器 |
| S-8.2 | F2 coordinator + event | 另刀／另 slug |
| S-8.3 | F3 新 slug 預設五站 | 另刀 F3。本 hop Files 零 `graph.yaml` |
| S-8.4 | 本 Stage 4 PR 只 4-spec 雙檔 | 已在 G2 過。不是 Stage 6 工作 |
| S-6.1 | 高影響列去向帳 | 已在本 slug 4-spec 綠（spec-gate C9）。F1 不重做 Disposition |
| S-8.7 | 審頁／執行板由對應 builder 重生 | 本 hop 產 `5-tasks.html`；不是 Stage 6 牙 |

### F1 Files 聯集（S-8.5 可核）

Stage 6 全部 T 的 Files 聯集只准這六條（fixture 目錄當前綴）：

- `scripts/five_station_f1.py`
- `scripts/check-five-station-f1.sh`
- `scripts/test-five-station-f1.sh`
- `scripts/fixtures/five-station-simplify/`
- `notes/design/five-station-simplify-f1-dual-read-annex.md`
- `notes/design/five-station-simplify-f1-rp-min-set.md`

超出上列 = L2／違 R-8。禁把 `_templates/`、`graph.yaml`、`hooks/_stage3_impl.py`、`hooks/_doctor_impl.py`、`scripts/check-spec-gate.sh`、`STATUS.md`、`devflow-contract.json`、coordinator 碼寫進任一 T 的 Files。

### Verify 開工前原樣跑（2026-09-14；牙尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1…T-12 | `scripts/test-five-station-f1.sh` 不存在 → 非零 | ③綠不了但方向對 |

## T-1 打通 Agent 代寫 Ship PASS 的 RP-16 拒收縱切
- [ ] 完成
- Covers: R-3 / S-3.1
- Files: scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/, notes/design/five-station-simplify-f1-rp-min-set.md
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group rp16 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f1.sh --group rp16`
- Blocked-by: —
- Risk: high
- Intent: 日常多一次終端機拒絕：有人（或 Agent）把 `7-review.md` 頂欄寫成 `verdict: PASS`、或把 `3-prototype.md` 寫成 `Human verdict: ACCEPTED` 卻沒有 `Verdict attestation: human:` 行，同一支新牙必須當沒寫並紅（RP-16），不得標 Done、不得當已離 Spec。人親寫 attestation／頂欄的對照稿，不得因本條被誤殺。改的是新牙入口與 RP-16 對照稿，不是 Cursor 擋寫、不是改既有 doctor、不是先鋪十六列散文。不會變成 F2 狀態機、不會在本 T 寫完整九個 SLOT。
- Boundaries: F1 模組只准 `scripts/` 新牙與 `notes/design/` 本 slug annex。本 T 只准建立牙骨架＋RP-16 一列＋兩份對照稿（Agent 代寫紅／人類親寫不因本條紅）。禁改 `_templates/` Stage 1–4、禁改 `graph.yaml`、禁寫 coordinator、禁刪 G1／G2／`ACCEPTED` token、禁改 `hooks/_stage3_impl.py` 與 doctor 握手語義、禁鎖 annex 鍵名。Data owner = 母版 scripts／annex 文本。Interface = `check-five-station-f1.sh` 讀 fixture；selftest 印 `=== CASE`。Error seam = Agent／coordinator 寫入 = 未寫。本 T 不掛 file-map／devflow-check 地板（既有牙；紅了停判 L1）。

## T-2 寫齊 dual-read 九個 SLOT 語意槽並讓缺槽變紅
- [ ] 完成
- Covers: R-5 / S-5.8
- Files: notes/design/five-station-simplify-f1-dual-read-annex.md, scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group slots -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f1.sh --group slots`
- Blocked-by: T-1
- Intent: 日常核 annex 時，九個 SLOT- id 都能指到一欄或等效句；少一槽，F1 檢查必須紅、不得宣稱 dual-read 已完成。改的是 dual-read annex 正文與「缺槽對照稿」，不是選定 JSON 鍵名、不是 bump 契約到 2.1.0。不會變成舊檔缺新欄就紅（那是已拒 2B）、不會在本 T 實作 doctor 改線。
- Boundaries: annex 必須同時具備且可用 SLOT- id 指到：SLOT-PARSE-OLD7、SLOT-PARSE-NEW5、SLOT-MISSING-NEW5-DEFAULT、SLOT-UNDECLARED-ROUTE、SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS、SLOT-DOCTOR-GREEN-MEANS、SLOT-IN-FLIGHT-DETECT、SLOT-RP-MIN-SET、SLOT-SKIP-NEGATION。OC-3：本檔與 annex **不鎖欄位鍵名**。Forbidden = 把 SLOT 寫成必填 schema 鍵、把缺槽當 warning-only。Allowed module = 本 slug dual-read annex + 既有牙入口加厚。本 T 不改 RP-16 行為、不寫 coordinator event。

## T-3 讓舊檔缺新欄不紅且把 doctor 綠說成已切變紅
- [ ] 完成
- Covers: R-5 / S-5.4, S-5.5, S-5.6, S-5.7, S-5.9
- Files: notes/design/five-station-simplify-f1-dual-read-annex.md, scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group dual-read -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 5 && bash scripts/test-five-station-f1.sh --group dual-read`
- Blocked-by: T-2
- Intent: 日常採用端更新 plugin 之後，不能再靠「doctor 印 COMPATIBLE」就以為已切五站。舊 7 站檔缺新 5 欄必須當合法缺席、不紅。文案或謂詞寫「doctor exit 0 所以可以跟 hops 走」必須紅。契約仍 2.0.0 且 hops 已是五站預設必須紅、路線仍舊 7；契約版本與 marketplace hops 哪個先寫入都一樣。改的是 dual-read 讀法與拒收句，不是改 doctor 握手本身、不是遠端改線。不會變成 3B（本刀改 doctor）、不會 bump `devflow-contract.json`。
- Boundaries: SLOT-MISSING-NEW5-DEFAULT／SLOT-DOCTOR-GREEN-MEANS／SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS／SLOT-UNDECLARED-ROUTE 在本 T 必須可測。讀既有 `hooks/devflow-doctor.sh` 與 `_doctor_impl.py` 當證據，**不准寫進 Files、不准改握手語義**。Concurrency：兩源任一順序，2.0.0+五站 hops → 仍舊 7 且紅；doctor 綠不得當仲裁。禁鎖讀檔器欄位鍵名。禁把本 repo 現況 doctor 綠解釋成已切。

## T-4 讓有 md 的 slug 凍在舊 7 且本資料夾五站 hop 跳不過
- [ ] 完成
- Covers: R-5 / S-5.1, S-5.2, S-5.3
- Files: scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/, notes/design/five-station-simplify-f1-dual-read-annex.md
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group inflight -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f1.sh --group inflight`
- Blocked-by: T-3
- Intent: 日常有人要把已有 `1-discussion.md`…`7-review.md` 任一檔的 slug（含本資料夾）改走五站自動前進、跳過例行 G1／G2，必須跳不過，且不得寫入五站狀態（RP-15）。只有 html、零個 1–7 `.md` 的目錄不算 in-flight，F3 後才可開五站機——本 T 只釘偵測布林，不切預設路線。改的是 in-flight 偵測牙，不是折本 slug、不是 F3 cut。不會變成 4C（拿本 slug 當新 5 白老鼠）。
- Boundaries: SLOT-IN-FLIGHT-DETECT = `docs/dev/<slug>/` 已有 1–7 任一 `.md`。本目錄因 md 而凍，不是因 html。Forbidden = 改 `graph.yaml`、寫五站狀態進 `docs/dev/five-station-simplify/`、把僅 html 當凍結。對照稿必須含：有 md → 凍舊 7；僅 html → `in_flight=false`；對本 slug 下五站 hop → 拒。不實作 coordinator hop 引擎。

## T-5 讓缺四欄或 Verify 寫看起來沒問題的 T 卡上就紅
- [ ] 完成
- Covers: R-2 / S-2.2
- Files: scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/, notes/design/five-station-simplify-f1-rp-min-set.md
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group rp1 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f1.sh --group rp1`
- Blocked-by: T-4
- Intent: 日常寫手勾了 done、卡上卻缺 Covers／Files／Verify／Blocked-by，或 Verify 只寫「看起來沒問題」，打開任務卡當下就要看見 RP-1 紅；勾選不得把該 T 標完成。改的是 F1 牙對 T 卡形狀的拒絕，不是等 hop 板或 Ship 才重建紅燈。不會變成改 `_templates/5-tasks.md`、不會把四欄標成可選。
- Boundaries: 人見面時機 = T 卡上就紅（4-spec DD-6）。對照稿輸入用 4-spec 指向的 T-fake 形（缺欄或 `Verify` 無鑑別力句）。Allowed = 加厚既有 F1 牙。Forbidden = 改 Stage 1–4 模板、把紅燈延後到 Ship、把 checkbox 當完成正本。本 T 不咬 RED 輸出／自審（屬 T-6）。

## T-6 讓無 RED、自審、無原始輸出的完成宣稱變紅
- [ ] 完成
- Covers: R-2 / S-2.3, S-2.9
- Files: scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/, notes/design/five-station-simplify-f1-rp-min-set.md
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group seam -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f1.sh --group seam`
- Blocked-by: T-5
- Intent: 日常有人要把一個沒有失敗測試原始輸出、或 reviewer 欄等於實作者、或完成宣稱只附摘要沒有原始輸出／`檔:行` 的 T 標完成，必須紅（RP-2／RP-6），該 T 未完成。改的是 seam／證據物質牙，不是開第二條審查產品。不會變成 Agent 代填 reviewer、不會把摘要當證據。
- Boundaries: RP-2 = 無 RED 或 reviewer=implementer → 未完成。RP-6／M10 = 只有摘要、無原始輸出或 `檔:行` → 紅。Test seam = 6-notes 證據欄對照稿，不是真開第二 session。Forbidden = 把自審寫成可選 seam（6B）、改 author≠approver 正本。本 T 不咬 Files 聯集（屬 T-8）。

## T-7 讓模糊 S 與不含 S-id 的測試名變紅
- [ ] 完成
- Covers: R-2 / S-2.4, S-2.5
- Files: scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/, notes/design/five-station-simplify-f1-rp-min-set.md
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group spec-name -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f1.sh --group spec-name`
- Blocked-by: T-6
- Intent: 日常一份 S 寫了 `check-spec-gate.sh` C4 `VAGUE_ALL` 三詞之一、或只寫「系統應處理錯誤」且無可斷言輸出，F1 必須紅（RP-3），該 S 不得當 T 的 Covers 綠燈。測試函數名像 `test_store_half_slot`（不含 `s_`／`S-` 與 S-id）必須紅（RP-4）；對照名 `test_s_2_5_test_name_requires_s_id` 不因本條紅。改的是接上既有 spec-gate C4 的對照、加上測試名牙，不是另造規格檢查家族、不是改 `check-spec-gate.sh` 檔。
- Boundaries: S-2.4 明寫 F1 **接**既有 `scripts/check-spec-gate.sh` C4，不另造家族；該檔只准呼叫、不准列入 Files、不准改 C4 詞表。RP-4 只咬測試名是否含對應 S-id。Forbidden = 新開 `check-spec-vague.sh` 第二家族、把模糊詞牙改成 warning-only。正向對照：名含 `s_` 與 S-id 的測試不因本條紅。

## T-8 讓少 Must-keep 宣稱、可選四欄句、Files 超出聯集變紅
- [ ] 完成
- Covers: R-2 / S-2.1, S-2.7, S-2.8
- Files: scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/, notes/design/five-station-simplify-f1-rp-min-set.md
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group brief-files -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f1.sh --group brief-files`
- Blocked-by: T-7
- Intent: 日常有人寫「五站已簡化」卻拿掉 T 的 Verify（少 M11），或在本 slug 後站寫「四欄可選／seam 可選／已五站故省 Must-keep」，或一個 T 缺 Files、或 Files 路徑超出同份 5-tasks 聯集，都必須紅；少 M 的簡化宣稱要被點名違 brief，可選句要擋本 slug G2，缺／超 Files 的 T 不得標完成（RP-5）。改的是 brief／scope 牙，不是重寫 Must-keep 正本。不會變成 6B（把 M 標可選）。
- Boundaries: S-2.7 對本 slug `4-spec.md`／後續 `5-tasks.md` 掃「可選四欄｜可選 seam｜已五站故省」；本檔正文必須維持零命中。RP-5／M9 = 缺 Files 或 Files ⊈ 聯集 → 紅。Forbidden = 把四欄／seam／Must-keep 標可選、把本 T 拿去改 `_templates/`。本 T 不重開 Disposition 表（S-6.1 已綠）。

## T-9 讓空 attestation、強迫 ACCEPTED、請人審與否定跳過變紅
- [ ] 完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3, S-4.4, S-4.5; R-1 / S-1.7
- Files: scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/, notes/design/five-station-simplify-f1-dual-read-annex.md
- Verify: `test -f scripts/fixtures/five-station-simplify/rp-13-empty-attestation-plus-chat.md && test -f scripts/fixtures/five-station-simplify/rp-12-miss-forced-accepted.md && test -f scripts/fixtures/five-station-simplify/rp-14-please-review-latch-false.md && test -f scripts/fixtures/five-station-simplify/skip-negation-as-oc.md && n=$(bash scripts/test-five-station-f1.sh --group attest -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 5 && bash scripts/test-five-station-f1.sh --group attest`
- Blocked-by: T-8
- Intent: 日常 B1 已命中時，沒有人類 `ACCEPTED`+`Verdict attestation: human:<名> @ <日>` 就不得進 Build；欄空加上 chat「可以開 Stage 4」仍不得離 Spec（RP-13，對照稿 `rp-13-empty-attestation-plus-chat.md`）。未命中卻被要求 `ACCEPTED` 必須紅（RP-12，`rp-12-miss-forced-accepted.md`），且不建 Demo 頁（S-1.7）。A4／A7 latch=否卻留下「請 owner 看一下／要不要繼續」必須紅（RP-14，`rp-14-please-review-latch-false.md`）。「不／無／不得」加上「跳過」不得再被讀成 skip OC（SLOT-SKIP-NEGATION／S-4.5，`skip-negation-as-oc.md`）。改的是 F1 新牙謂詞，不是修既有 `_stage3_impl.py`（該檔不進 Files）。不會變成 5B／5C（chat 繞或取消 attestation）。
- Boundaries: SLOT-SKIP-NEGATION 本 T 必須可測。讀 `_stage3_impl.py` 只當 Known limit 證據，**不准改、不准列入 Files**。chat 文字不得寫入 Human verdict。Forbidden = 把否定跳過句當 skip OC、把 chat 當 attestation、未命中仍產 Demo 頁。S-1.7／S-4.3：trigger 未命中 → 不建頁且強迫 ACCEPTED 紅。S-4.1 正向：兩行都在才准 hop（對照稿，不是真跑 F2 coordinator）。

## T-10 讓不可逆無 Quiz 與無人 PASS 的 Ship Done 變紅
- [ ] 完成
- Covers: R-1 / S-1.10; R-3 / S-3.2, S-3.3
- Files: scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/, notes/design/five-station-simplify-f1-rp-min-set.md
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group ship-quiz -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-five-station-f1.sh --group ship-quiz`
- Blocked-by: T-9
- Risk: high
- Intent: 日常改了 schema／公開 API／權限／金流／資料遺失卻沒 Quiz，必須紅（RP-7）；可逆改動被強制 Quiz 當第三例行停也必須紅。`7-review.md` 頂欄沒有人類 `verdict: PASS`（空／HOLD／REQUEST_CHANGES）卻標 Done，必須紅（RP-8），狀態留 Ship。宣稱 G3 可過或 Done 但 Evidence 八點少一點，或用「已經五站了」當省略理由，必須未過（S-3.3）。改的是 Quiz／Ship／八點對照牙，不是 F2 狀態機、不是本 hop 跑 G3。不會變成可逆也加人停、不會讓機械綠自動 Done。
- Boundaries: B4 僅不可逆；可與 A10 同一人停，不准第三次例行停。RP-8 對照稿即可，不實作 coordinator HumanWait。S-3.3 八點對 `docs/dev/readme-contract-extract.md` G3 錨，摺站不得省略。Forbidden = 放寬 Quiz 到每次 feat、Agent 寫 PASS 當已寫（已由 T-1 咬）、本 T 改 7-review 模板。Files 不列 `7-review.md` 正本。

## T-11 釘 RP-1 到 RP-16 只准加並讓十六個對照各紅一次
- [ ] 完成
- Covers: R-2 / S-2.6
- Files: notes/design/five-station-simplify-f1-rp-min-set.md, scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/
- Verify: `test -f scripts/fixtures/five-station-simplify/rp-09-third-hop-rewrite.md && test -f scripts/fixtures/five-station-simplify/rp-10-second-decide-reopen.md && test -f scripts/fixtures/five-station-simplify/rp-11-second-goal-reopen.md && n=$(bash scripts/test-five-station-f1.sh --group rp-min-set -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 17 && bash scripts/test-five-station-f1.sh --group rp-min-set`
- Blocked-by: T-10
- Intent: 日常有人從 annex 刪掉 RP-8（Ship 無人 PASS 卻 Done），這份殘缺 annex 必須紅。完整集必須能對 T-fake、S-fuzzy、Agent 代寫、超 cap、空 attestation、in-flight 寫五站狀態各紅至少一次；十六列各自至少一張對照稿紅。超 cap 三張具名卡只證明謂詞在：`rp-09-third-hop-rewrite.md`（RP-9）、`rp-10-second-decide-reopen.md`（RP-10）、`rp-11-second-goal-reopen.md`（RP-11）；不實作 F2 計數器、不鎖 event 鍵名。改的是最小集對照，不是加第十七個必刪 RP、不是把 RP 集縮成 12–16。不會變成減列仍綠。
- Boundaries: OC-10／SLOT-RP-MIN-SET = 只准加不准減。annex 必須列出 RP-1…RP-16 語意（與 4-spec／Decision 表同義，不另發明編號）。超 cap 對照稿是上列三張具名 fixture，計數落點仍交 F2（S-7.4 不在本 T 落地）。Forbidden = 刪列、把最小集縮到 RP-12…16、把 cap 數字改鬆、把舊 7 slug 套這三 cap。Files 超過五檔是因為可觀測行為是「最小集 + 十六紅 + 減列紅」同一刀，不是按 RP 水平切十六個 T。

## T-12 收口 F1：七檔名與 token 仍在、Files 不越界、Q6 不升格、已拒案不得重開
- [ ] 完成
- Covers: R-1 / S-1.1; R-6 / S-6.2, S-6.3; R-8 / S-8.1, S-8.5, S-8.6
- Files: scripts/five_station_f1.py, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/, notes/design/five-station-simplify-f1-dual-read-annex.md
- Verify: `test -f scripts/fixtures/five-station-simplify/reopen-1b-delete-tokens.md && test -f scripts/fixtures/five-station-simplify/reopen-2b-old-file-red.md && test -f scripts/fixtures/five-station-simplify/reopen-4c-this-slug-as-new5.md && test -f scripts/fixtures/five-station-simplify/reopen-6b-must-keep-optional.md && test -f scripts/fixtures/five-station-simplify/reopen-7c-merge-knives.md && python3 -c "import pathlib,re; t=pathlib.Path('docs/dev/five-station-simplify/5-tasks.md').read_text(); assert not re.search(r'改採\\s*[12467][BC]', t); print('T-12-no-reopen')" && n=$(bash scripts/test-five-station-f1.sh --group f1-close -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 9 && bash scripts/test-five-station-f1.sh --group f1-close`
- Blocked-by: T-11
- Intent: 日常 F1 結束時，目錄仍是七個舊檔名、G1／G2／`ACCEPTED` token 仍在，沒有 `intake.md` 家族；本 slug Stage 5–7 的 Files 聯集沒有 coordinator、沒有 `graph.yaml` 切線、沒有 Stage 1–4 模板；任何「採用現場也 chat 蓋章」句仍帶 Assumption 或仍待驗，寫成已核事實必須擋。五張具名對照稿（`reopen-1b-delete-tokens.md`…`reopen-7c-merge-knives.md`）若把已拒案寫成可選實作，同一支牙必須紅；本份 5-tasks 自己也不能出現「改採」接上那些已拒代號。改的是收口對照（檔名／token／diff 聯集／Q6 用詞／已拒案守門），不是 F3 切新 slug 預設、不是抽採用逐字稿。不會變成 bump 契約、不會改 STATUS。
- Boundaries: S-8.1 THEN = 有 annex／scripts 牙；無 graph 預設切線；無 coordinator 碼；不刪 token。S-8.5 Files 聯集 = 本檔「F1 Files 聯集」六條。S-8.6 對照稿只准新牙讀 `scripts/fixtures/five-station-simplify/reopen-*.md`，禁把 hooks／guides／`check-file-map.sh`／`check-spec-gate.sh` 寫進 Files。S-1.1 本 T 只釘「七舊名在、新家族名不在、token 仍在」；F3 才切新 slug 預設（延後表）。S-6.2／S-6.3：Q6 status 不是 resolved；升格句擋。Forbidden = 把 1B／2B／4C／6B／7C 當可選實作、折本 slug、併刀、把 Q6 標 oc-accepted。若新檔讓 file-map 紅 → 停、判 L1，不得把既有地板檔預先寫進 Files。

## Split Decisions

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| `execution.mode: sequential`；Blocked-by 成 T-1→…→T-12 單鏈 | Feature Risk high；A 線指定先 tracer 再加厚 annex 再補 RP。前置牙入口不存在時後 T 不該開工 | 4-spec Verification Profile Risk high；使用者 A-line brief | parallel 讓 T-5 與 T-2 同時改同一支牙。棄：Files 重疊、review 吵 |
| T-1 選 RP-16 不當 RP-1 | 最薄端到端是「機器寫判定 → 當沒寫並紅」；卡上缺欄是加厚，不是第一刀可觀測主權 | 4-spec S-3.1／RP-16；使用者 e.g. RP-16 或 RP-1 | T-1 先做 RP-1。棄：那是形狀牙，還沒打通判定主權縱切 |
| 單一檢查家族 `check-five-station-f1` | Diff Budget `scripts/` 新牙 ≤4；S-2.4 接既有 spec-gate、不另造模糊詞家族 | 4-spec Diff Budget；S-2.4；S-8.1 | 每 RP 一支 `check-rp-N.sh`。棄：爆檔數、水平切層 |
| annex 拆兩檔、不鎖鍵名 | Budget annex ≤2；S-5.8 與 S-2.6 兩份語意；OC-3 禁鎖鍵 | 4-spec S-5.8／S-2.6／OC-3 | 一份 JSON schema。棄：2B／鎖鍵 |
| S-7.1…S-7.4 不開 T | 計數落點交 F2；使用者禁發明 F2 T。T-11 只用對照稿讓 RP-9／10／11 紅 | 4-spec S-7.4／S-8.2；本檔延後表 | 本 slug 寫 coordinator 計數器。棄：違 S-8.5 |
| 表 A／B latch S 不開 T；S-1.7 未命中不建頁掛 T-9 | F2 coordinator 才評產頁／latch／HumanWait。T-9 Intent 已寫不建 Demo 頁，Covers 補上 S-1.7 | 4-spec S-1.2…S-1.6／S-1.8…S-1.12 n-a:F2；S-1.7 與 S-4.3 同刀 | 為 A4／A7 寫假 coordinator。棄：7C 味道 |
| S-8.6 收進 T-12，不另開 T-13 | 收口刀已禁 1B／4C／7C；C 線 T-19 的可紅對照改成五張具名 fixture，掛同一支 `--group f1-close` | 4-spec S-8.6；3-review absorb C T-19 | 另開 T-13。棄：拆開收口。棄：C 把 hooks／selftest／check-spec-gate／guide 寫進 Files |
| T-9／T-11 Verify 點具名檔 | 空欄+chat、強迫 ACCEPTED、請人審、否定跳過、RP-9／10／11 超 cap 三卡必須是檔名，不是只寫 `-ge N` | 3-review soft-fix；A 線新牙 selftest | 只留散文 case 數。棄：B 把 RP 最小集縮成 12–16 |
| 不改 `_stage3_impl.py`／doctor | S-8.5 Files 聯集不含 hooks；Out of Scope 既有牙；S-4.5 由新牙 SLOT-SKIP-NEGATION 收緊 | 4-spec S-4.5 Known limit；S-8.5 | F1 直接改 skip 舊牙。棄：越 Diff Budget 與 Files 圍欄 |
| file-map／devflow-check 不進 Files | 既有牙／地板；S-8.5 只准新牙＋annex。紅了是 L1 訊號不是本 hop 預授權 | 4-spec S-8.5；`scripts/check-file-map.sh` | T-12 順便改 EXPECTED_MAPPED_FILES。棄：把既有牙寫進 F1 Files |
| Verify 開工前實跑（2026-09-14） | `scripts/test-five-station-f1.sh` 不存在 → 十二欄皆非零 | 模板 Verify 三律 ③ | 用已綠的 doctor exit 0 當 T-3 牙。棄：無鑑別力且違 S-5.5 |
