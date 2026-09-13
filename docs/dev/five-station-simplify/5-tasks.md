---
feature: five-station-simplify
stage: 5-tasks
status: draft
owner: rick
updated: 2026-09-14
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — 五站簡化 F1（Implementer B：條件頁＋人主權＋freeze＋doctor 陷阱）

> 基準:`origin/main` tip 含 G2 PASS（#315／#316；`4-spec.md` `status: approved`／`verdict: PASS`）。Lane = **full**。契約不 bump。
> 本 hop **只寫任務 + html twin**。不落地 `scripts/` 牙、不寫 annex 正文、不開 Stage 6、不改 `_templates/`／`graph.yaml`／既有 doctor 握手、不 bump `devflow-contract.json`、不改 `STATUS.md`／`HISTORY.md`、不發明 G3、不合併。
> B 線（獨立於 A／C）：T 按 **條件頁 + 人類主權 + freeze + marketplace×doctor 陷阱** 排。牙集 = RP-12／13／14／15／16 與 SC-4／5／6／8／9／10。**第一刀 tracer** = B1 已 latch 時空 attestation 不得 hop 出 Spec。**第二刀** = annex dual-read 誠實。無 F2／F3 T。Files 聯集只准 `scripts/` 新牙 + 本 slug annex + fixture。
> 模式：sequential（Feature Risk high）。S-8.5：本 slug Stage 5–7 只 F1。

## 開工前提

Stage 4 已核准。G2 是 human owner rick PASS（2026-09-14），不是 Agent 自裁。本 hop 不改 `4-spec.md`／`4-spec.html`。Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。annex 鍵名不鎖（OC-3）。負向 fixture 目錄建議 `scripts/fixtures/five-station-simplify/`（4-spec 下層；本 hop 只點名，Stage 6 才新增檔）。

### N1 R/S 盤點（52 S；本 hop 切 B 線 21 條）

| R | S | 本 hop T |
|---|---|---|
| R-4 拒空 attestation | S-4.1 B1 進 Build 前要人類 ACCEPTED+attestation；S-4.2 欄空+chat 不得離 Spec（RP-13） | T-1（tracer） |
| R-5 dual-read 誠實 | S-5.4 舊七缺新欄不紅；S-5.8 annex 九個 SLOT | T-2 |
| R-5 marketplace×doctor | S-5.5 doctor 綠≠已切；S-5.6 「跟 hops 走」紅；S-5.7 未 upgrade 仍舊 7；S-5.9 兩源並改仍舊 7 | T-3 |
| R-1／R-4 條件頁 | S-1.7 A5 未命中不建頁；S-4.3 未命中卻逼 ACCEPTED（RP-12）；S-4.4 latch 假仍請人審（RP-14） | T-4 |
| R-3 人主權 | S-3.1 Agent 寫 ACCEPTED／Ship PASS=未寫（RP-16）；S-3.2 無人 PASS 卻 Done 紅 | T-5 |
| R-5 freeze | S-5.1 in-flight 已有 md 仍舊 7（RP-15）；S-5.2 本 slug 五站 hop 跳不過（SC-8）；S-5.3 僅 html 不凍 | T-6 |
| R-4 skip 誠實 | S-4.5 否定「跳過」不得當 skip OC | T-7 |
| R-2／R-8 F1 鎖 | S-2.6 本線 RP-12…16 只准加；S-8.1 F1=牙+annex 不准切線；S-8.5 本 slug 後站只 F1；S-8.6 1B／2B／4C／6B／7C 不重開 | T-8 |
| R-1 表 A／B 產頁不 latch | S-1.1…S-1.6、S-1.8…S-1.12 | 本 hop 不切（A 線／F2 coordinator 產頁；B 只咬 RP-12／14 拒收） |
| R-2 假完成／Must-keep | S-2.1…S-2.5、S-2.7…S-2.9 | 本 hop 不切（A／C 線；本線只守 RP-12…16 加列） |
| R-3 Evidence 八點 | S-3.3 | 本 hop 不切（Ship 物質；非 B 牙集） |
| R-6 Q6／Disposition | S-6.1…S-6.3 | 本 hop 不切（已在 4-spec 形狀；非 F1 牙） |
| R-7 rewrite cap | S-7.1…S-7.4 | 本 hop 不切（**F2**；禁 F2 T） |
| R-8 分刀其餘 | S-8.2 F2 coordinator；S-8.3 F3 cut；S-8.4 本 Stage 4 PR 檔集；S-8.7 審頁 builder | 不切 F2／F3 T。S-8.4 已過。S-8.7 由本 hop 產 twin 履行，不另開 T |

SC → T：SC-4→T-5；SC-5→T-2／T-6；SC-6→T-1／T-4；SC-8→T-6；SC-9→T-2／T-3；SC-10→T-3。RP-12→T-4；RP-13→T-1；RP-14→T-4；RP-15→T-6；RP-16→T-5。

### Verify 開工前原樣跑（2026-09-14；F1 牙尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1 | `bash scripts/test-five-station-f1.sh --group hop-empty-attest -v` → `No such file or directory`，exit 127；`n` 計數 0，`test -ge 3` 紅 | ③綠不了但方向對（牙尚未落地）→ 開工條件成立 |
| T-2 | `--group dual-read` 同檔不存在，exit 127；`test -ge 4` 紅 | ③方向對 |
| T-3 | `--group doctor-trap` 同檔不存在，exit 127；`test -ge 4` 紅 | ③方向對 |
| T-4 | `--group cond-page` 同檔不存在，exit 127；`test -ge 4` 紅 | ③方向對 |
| T-5 | `--group human-sovereign` 同檔不存在，exit 127；`test -ge 3` 紅 | ③方向對 |
| T-6 | `--group freeze` 同檔不存在，exit 127；`test -ge 3` 紅 | ③方向對 |
| T-7 | `--group skip-neg` 同檔不存在，exit 127；`test -ge 2` 紅 | ③方向對 |
| T-8 | `--group rp-add-only` 同檔不存在，exit 127；`test -ge 3` 紅 | ③方向對 |

## T-1 拒絕空 attestation 在 B1 已 latch 時 hop 出 Spec
- [ ] 完成
- Covers: R-4 / S-4.1, S-4.2
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/hop-empty-attest/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group hop-empty-attest -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f1.sh --group hop-empty-attest`
- Blocked-by: —
- Intent: 日常多一次機械拒絕：九條 trigger 已勾、Human verdict 空或只有 ACCEPTED 卻沒有 `Verdict attestation: human:` 行時，即使 owner chat 寫「可以開 Stage 4／准開下一站」，系統也不得 hop 出 Spec，chat 文字不會被抄進頂欄。改的是 F1 hop 拒收牙與 `hop-empty-attest` 對照稿，不是改 Stage 3 模板、也不是再請人按提交判定。不會變成 Cursor 擋寫、不會把本 slug 已有的 `human:rick @ 2026-09-14` 誤殺、不會把未命中 B1 的 feat 也逼填 ACCEPTED。
- Boundaries: F1 scripts／annex 可讀 3-prototype 的 Human verdict 與 attestation 兩行、九條 trigger 勾選。禁止改 `_templates/` 1–4、禁止改 `hooks/_stage3_impl.py` 當本 T 的修法、禁止把 chat 當判定正本、禁止 Agent 代寫 attestation。鍵名不鎖（OC-3）。Test seam = fixture 目錄三案：欄空+chat 必紅（RP-13）；ACCEPTED 無 attestation 必紅；兩行齊備則不得因本條紅。本 T 不准寫 coordinator、不准改本 slug 既有 3-prototype 頂欄。Actor=母版 owner；Goal=chat 不能替代 attestation；Authority=空欄就卡 Spec；Recovery=人類補行後重評。

## T-2 讓 dual-read annex 九個 SLOT 誠實且舊七缺欄不紅
- [ ] 完成
- Covers: R-5 / S-5.4, S-5.8
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, docs/dev/five-station-simplify/annex-dual-read.md, scripts/fixtures/five-station-simplify/dual-read/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group dual-read -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-five-station-f1.sh --group dual-read`
- Blocked-by: T-1
- Intent: 日常多一份可核對的 annex：打開文本能指到九個 SLOT- id（能讀舊 7、能讀新 5、舊檔缺新欄合法不紅、未宣告 2.1.0 仍舊 7、2.0.0+五站 hops 紅、doctor 綠只握手、in-flight 看 md、RP 只准加、否定跳過不是 skip）。舊 7 站檔少新五欄時這次檢查不紅。改的是本 slug annex 與 dual-read 對照稿，不是鎖 JSON／YAML 鍵名、不是 bump 契約到 2.1.0。不會變成舊檔一次全紅、不會把「能解析兩套」寫成「已經切五站」。
- Boundaries: 允許修改的模組 = 本 slug annex + F1 scripts／fixture。禁止鎖欄位鍵名（OC-3）。禁止改 living 契約句、禁止 bump `devflow-contract.json`、禁止改 doctor 握手語義、禁止舊檔缺欄就紅（2B）。九個 SLOT- id 必須各有對應欄或等效句，少一槽 = F1 未完成。Test seam = 舊七缺欄 fixture 不紅；缺 SLOT-MISSING-NEW5-DEFAULT 的 annex 必紅；未宣告 2.1.0 → 路線=舊 7。Actor=採用專案 owner／F1 寫手；Goal=dual-read 誠實；Authority=缺槽不得勾本 T。

## T-3 把 doctor 綠加 marketplace 五站 hops 點名成未切
- [ ] 完成
- Covers: R-5 / S-5.5, S-5.6, S-5.7, S-5.9
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, docs/dev/five-station-simplify/annex-dual-read.md, scripts/fixtures/five-station-simplify/doctor-trap/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group doctor-trap -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-five-station-f1.sh --group doctor-trap`
- Blocked-by: T-2
- Intent: 日常少一次被遠端改線還以為沒變：契約仍 2.0.0、marketplace 已把 hops 換成五站預設、`hooks/devflow-doctor.sh` 因握手綠（exit 0／COMPATIBLE）時，文案或謂詞若寫「已切五站」或「doctor 綠所以可以跟 hops 走」，F1 必須紅；採用端路線仍是舊 7。兩格誰先寫入都一樣，doctor 綠不得當仲裁。改的是新對照牙與 annex 的 SLOT-DOCTOR-GREEN-MEANS／SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS，不是改 doctor 去讀 hops。不會變成本刀改 doctor 握手集合、不會把 COMPATIBLE 當成路線證明。
- Boundaries: F1 牙可讀契約版本與 hops 是否五站預設（兩源 AND）。禁止改 `hooks/_doctor_impl.py` 握手語義（3B 已拒）。禁止把 marketplace update 當已 upgrade。禁止 coordinator、禁止切 `graph.yaml` 預設。Concurrency：任一寫入順序，2.0.0+五站 hops → 仍舊 7 且紅。Test seam = 四案：doctor 綠當已切必紅；「跟 hops 走」句必紅；未 upgrade 仍舊 7；兩源先後寫入結果相同。Actor=採用專案 owner；Goal=未 2.1.0 不得遠端改線；Authority=契約版本不是 marketplace 包裝。

## T-4 讓未命中條件頁不建頁並紅強迫 ACCEPTED 與請人審
- [ ] 完成
- Covers: R-1, R-4 / S-1.7, S-4.3, S-4.4
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/cond-page/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group cond-page -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-five-station-f1.sh --group cond-page`
- Blocked-by: T-1
- Intent: 日常少第二次等人：純守衛 feat 沒有 `3-prototype.md`、或九條 trigger 全未勾且 n-a 原因可讀時，不建 Demo／原型審頁，也不另開人停。有人仍要求該 feat 必須 ACCEPTED → 紅（RP-12）。A4／A7 latch=否時若留下「請 owner 看一下／要不要繼續」→ 紅（RP-14），不是客氣。改的是條件頁拒收牙，不是 F2 去產 A4／A7 卡。不會變成「想給人看 twin」就 HumanWait、不會把本 slug 已命中的六條 trigger 當成未命中樣本。
- Boundaries: 生成謂詞假 → 不建頁。latch 假 → 禁開審查 widget、禁把 twin URL 當「請簽」。禁止本 T 寫 coordinator 評表 A／B（F2 Out of Scope）。禁止因看板停（A8／A9 不是本 T）。Test seam = 四案：A5 未命中無頁；未命中+強迫 ACCEPTED 紅；latch 假+請人審紅；未命中無第二次人停。Actor=coordinator／母版 owner；Goal=沒命中就不問人；Recovery=刪請人審紀錄、刪假 ACCEPTED。

## T-5 把 Agent 代寫 ACCEPTED 或 Ship PASS 當未寫並拒絕無人簽的 Done
- [ ] 完成
- Covers: R-3 / S-3.1, S-3.2
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/human-sovereign/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group human-sovereign -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f1.sh --group human-sovereign`
- Blocked-by: T-1
- Intent: 日常少一次機器出貨：Agent 或 coordinator 寫入 `Human verdict: ACCEPTED` 卻無 `human:` 行，或寫入 `7-review.md` 頂欄 `verdict: PASS`，系統視為未寫（RP-16），不得 hop 出 Spec、不得標 Done。頂欄空／HOLD／REQUEST_CHANGES 即使機械全綠，標 Done 也紅（RP-8 家族，本線咬 SC-4）。改的是判定正本牙，不是改 G3 八點清單。不會變成 Agent 可代填 attestation、不會讓 checkbox 勾選代替頂欄。
- Boundaries: 判定正本 = md 頂欄／attestation，不是 chat、不是勾選。Agent／coordinator 禁寫 ACCEPTED／Ship PASS。兩筆寫入只成功一筆（頂欄 PASS 但 attestation 空）→ 仍未寫。禁止本 T 改 7-review 模板、禁止發明 G3 PASS、禁止本 slug 折五站。Test seam = 三案：Agent ACCEPTED 無 attestation = 未寫；Agent 寫 Ship PASS = 未寫；無人 PASS 卻 Done 紅。Actor=母版 owner／Ship 審查者；Goal=判定只由人寫；Recovery=刪機器寫入，人重寫。

## T-6 凍結已有 md 的 slug 並擋本資料夾五站 hop
- [ ] 完成
- Covers: R-5 / S-5.1, S-5.2, S-5.3
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/freeze/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group freeze -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f1.sh --group freeze`
- Blocked-by: T-2
- Intent: 日常少一次把自己當白老鼠：`docs/dev/<slug>/` 已有 1–7 任一 `.md` 時，要求改走五站自動前進、寫入五站狀態 → 紅（RP-15），整段仍舊 7。本資料夾已有 `1-discussion.md`，五站 hop 想跳過例行 G1／G2 必須跳不過（SC-8）。只有 html、零個 md 的目錄不算 in-flight，不因 html 而凍。改的是 freeze 偵測牙，不是切新 slug 預設路線。不會變成拿本 slug 當新 5、不會把裸 html 誤凍。
- Boundaries: in-flight 偵測只認 1–7 `.md`（OC-5），不認 html。禁止把本 slug 折五站（4C）。禁止 F3 cut、禁止改 `graph.yaml` 預設。本 T 讀目錄布林，不寫五站狀態進本目錄。Test seam = 三案：已有 md → 五站狀態寫入紅、仍舊 7；`docs/dev/five-station-simplify/` hop 跳 G1／G2 被拒；僅 html → in_flight=false。Actor=本 slug 執行者；Goal=觀測不被自己污染；Authority=in-flight 不建立五站機。

## T-7 讓否定跳過句不得被讀成 skip Owner Call
- [ ] 完成
- Covers: R-4 / S-4.5
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, docs/dev/five-station-simplify/annex-dual-read.md, scripts/fixtures/five-station-simplify/skip-neg/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group skip-neg -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f1.sh --group skip-neg`
- Blocked-by: T-2
- Intent: 日常少一次被「不准跳」讀成「已跳」：Decision 寫「不預先跳過 Stage 3」且同行有「本檔無『跳過 Stage 3』流程層 OC」時，F1 不得把同時帶否定詞（不／無／不得）與「跳過」的句子當 skip OC。現行 `_stage3_impl.py` 曾誤綠（`trigger_source=owner-call`）記在 4-spec；本 T 用新牙收緊，不修那支舊牙。改的是 annex SLOT-SKIP-NEGATION 與對照稿。不會變成本 T 改 hooks 握手、不會把真的「Stage 3＋跳過」流程層 OC 誤殺。
- Boundaries: F1 新牙咬否定跳過；禁止改 `hooks/_stage3_impl.py`（Files 聯集不含 hooks；S-8.5）。annex 必須能指到 SLOT-SKIP-NEGATION，鍵名不鎖。Test seam = 兩案：否定句 fixture 不得當 skip；真流程層 OC（同時含「Stage 3」與「跳過」且無否定）仍可被既有規則認。Actor=G2 reviewer／F1 寫牙的人；Goal=「不准跳」不被讀成「已跳」；Recovery=F1 謂詞收緊後重跑應拒假 skip。

## T-8 鎖 F1 檔集並紅 annex 刪 RP-12 到 RP-16
- [ ] 完成
- Covers: R-2, R-8 / S-2.6, S-8.1, S-8.5, S-8.6
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, docs/dev/five-station-simplify/annex-rp-b.md, scripts/fixtures/five-station-simplify/rp-add-only/
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group rp-add-only -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f1.sh --group rp-add-only`
- Blocked-by: T-3
- Intent: 日常少一次後站偷做 F2／減牙：annex 列出 RP-12…16 後若刪掉 RP-13（空 attestation 離 Spec）或任一本線 RP，對照必紅。Files 聯集若出現 coordinator、改預設 `graph.yaml`、改 Stage 1–4 `_templates/`、或把 1B／2B／4C／6B／7C 當可選實作，本 T 紅。改的是本線最小拒收集與檔集牙，不是一次實作 RP-1…11。不會變成減列仍綠、不會順便寫 coordinator 或切新 slug 預設。
- Boundaries: 本 slug Stage 5–7 只准 `scripts/` 新牙、本 slug annex、本目錄 5／6／7 過程檔。禁止 coordinator 碼、禁止改預設 graph 路線、禁止改 Stage 1–4 模板、禁止折本 slug。禁止重開 1B 刪 token、2B 舊檔缺欄就紅、4C 本 slug 當新 5、6B Must-keep 可選、7C 併刀。OC-10：本線 RP-12…16 只准加不准減。Test seam = 三案：刪 RP-13 的 annex 紅；Files／diff 點名 coordinator 或 graph 切線或 `_templates/` 1–4 紅；文案「改採 1B／2B／4C／6B／7C」紅。Actor=本 slug Stage 5／6 寫手；Goal=只施工 F1；Recovery=把 F2／F3 檔與已拒案從 Files／正文刪掉。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential，不開 parallel | Feature Risk high（判定主權＋採用端遠端改線＋本 slug freeze）。T-1／T-2／T-3 共享同一 F1 CLI，硬序大於省一波。 | `_templates/5-tasks.md` `execution.mode` 缺省 sequential；4-spec Verification Profile `Risk: high` | 棄 T-4 ∥ T-3。檔案幾乎不重疊，可平行，但本 hop 選保守序。 |
| 八個 T 不是二十一刀、也不是 52 刀 | B 線可觀測行為是「空欄不得離 Spec → annex 誠實 → doctor 陷阱 → 條件頁拒收 → 人主權 → freeze → skip 否定 → F1 檔集」。一 S 一 T 會讓同一 CLI 被切碎。 | 使用者 Stage5-B brief；4-spec SC-4／5／6／8／9／10、RP-12…16；模板「一個 T 一個關注點」 | 棄「每個 S 一 T」。棄按 annex→scripts→fixture 水平切層。 |
| T-1 當 tracer，不先寫 annex | 最薄端到端 = B1 latch 時空欄+chat 被拒。annex 誠實是第二刀加厚，不是第一刀。 | 使用者「First tracer T = empty attestation cannot hop」；S-4.2／RP-13 | 棄「先建 annex 再掛牙」（annex 本身不可觀測 hop）。棄「T-1 順便做完九 SLOT」（Verify 會混兩套）。 |
| T-2 與 T-3 分開 | 舊檔不紅／九 SLOT 是讀檔誠實；doctor 綠≠已切是採用端陷阱。同一 annex、兩條可觀測拒絕。 | 4-spec S-5.4／S-5.8 vs S-5.5…S-5.9；OC-1 三句 | 棄「dual-read + doctor 同一 T」（Verify 要跑兩套不相干對照）。 |
| T-4 Blocked-by 只掛 T-1 | 條件頁拒收（RP-12／14、A5 不建頁）沿 hop 牙，不依賴 doctor 陷阱。 | 4-spec SC-6；S-1.7／S-4.3／S-4.4 | 棄等 T-3。棄本 hop 實作 A4／A7 產頁（那是 F2）。 |
| T-5 Blocked-by T-1 | Agent 代寫與空 attestation 同一判定正本家族；Ship Done 是加厚，不是新 CLI。 | 4-spec SC-4、RP-16；S-3.1 與 S-4.2 共用「未寫」 | 棄併入 T-1（T-1 Verify 只咬 hop 出 Spec，再跑 Ship Done 是第二套指令）。 |
| T-6 Blocked-by T-2 | freeze 偵測用 annex SLOT-IN-FLIGHT-DETECT；本 slug 是 live 樣本。 | 4-spec S-5.1／S-5.2／S-5.3、SC-8 | 棄等 T-3（doctor 綠與目錄 md 是不同源）。棄 F3 cut T。 |
| T-7 Blocked-by T-2 | SLOT-SKIP-NEGATION 住 annex；收緊在新牙不在 `_stage3_impl.py`。 | 4-spec S-4.5 Known limit；S-8.5 Files 不含 hooks | 棄本 T 改 `hooks/_stage3_impl.py`。棄併入 T-1（skip 謂詞 ≠ hop 空欄）。 |
| T-8 最後、Blocked-by T-3 | 加列／檔集牙要在 annex 與 doctor SLOT 都有之後才有東西可減。 | 4-spec S-2.6（本線 RP-12…16）、S-8.1／S-8.5／S-8.6 | 棄本 hop 實作 RP-1…11（A／C）。棄 F2／F3 T。 |
| 本 hop 不切表 A 產頁、Must-keep 假完成、Q6、cap、F2／F3 | 使用者 B-line 牙集 + S-8.5 + 禁 F2／F3 T。 | 4-spec Out of Scope；本 hop brief | 棄把 S-7.*／S-8.2／S-8.3 寫成 T。棄改 STATUS。 |
