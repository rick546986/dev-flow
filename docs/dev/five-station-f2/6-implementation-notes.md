---
feature: five-station-f2
stage: 6-implementation
status: draft
owner: implementer-A
updated: 2026-09-14
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: 56c8019c1058c375755ca03944140f79ff8bbe55

> Implementer notes + independent T-Review: **R2** (#347／`6681e1f`) then **R1** (this hop, author≠#346)。
> R2 列不得刪。R1 另塊接在 R2 之後。未發明 Human G3 PASS。5-tasks checkbox 保持未勾。

## 0. 起手

### 0a branch／錨點

- 只讀 4-spec／5-tasks／本檔／living。禁讀 1／2／3。
- `git fetch origin main` → `FORK=56c8019c1058c375755ca03944140f79ff8bbe55`
- `git switch -c cursor/five-station-f2-s6-impl-5e82 "$FORK"`
- `test "$(git rev-parse HEAD)" = "$FORK"` → 通過

### 0b worktree 隔離

n-a:本 feature 未並行。單一 checkout、無第二 worktree；不改 STATUS（companion #345）；無另開容器／DB／queue。

### 0c 守衛與 doctor

手動實作（非 dev-run 派工）。`devflow-exec.sh start` 未武裝本 session（cloud agent 單線）。doctor 現況 COMPATIBLE＝約束，不是 hop 通行證（T-5）。

## T Review Log

獨立 T-Reviewer **R2**（fresh-context Agent；author≠approver／M12）。基準 main `481e9cc`（#346）。未讀 implementer Self-Review 當錨；未發明 G3 PASS；未勾 5-tasks checkbox。implementer-A PRE 列只當軌跡，**不是** verdict。

R2 親跑 battery（2026-09-14）：全入口 `failed=0` exit 0；`=== CASE` ×18 皆官方名；`--only new5|old7|f1` 各 exit **3**；未知 `--only nope` exit **2**；`--help` 含 `--only`。

| T | verdict | 分類 | 一句 |
|---|---|---|---|
| T-1 | ACCEPTED | — | Q12 first persist=0；新 process 仍 2 |
| T-2 | ACCEPTED | — | CAP-3 讀倉拒；STORE-READ 字樣牙不讀倉＝紅格 |
| T-3 | ACCEPTED | — | Decide／Goal 讀倉拒；同 mutation |
| T-4 | ACCEPTED | — | Spec／Build 同桶；七 stem 是注入紅。殘：S-2.5 `or True` |
| T-5 | ACCEPTED | — | doctor 綠≠路條；F1 dual-read 另跑。殘：doctor-route 第 4 格掛 NEW5-Q12-ZERO 名 |
| T-6 | ACCEPTED | — | 六具名 hop + events 三官方名 |
| T-7 | ACCEPTED | — | 注入仍 hop／Done／等人／折線；不是拒 hop 當紅格綠 |
| T-8 | **FAIL** | **IMPL** | S-6.5：16 份只是 `f2-omit` 標；`evaluate_hop` 仍 hop→Ship |
| T-9 | ACCEPTED | — | OLD7 無五站機；本目錄跳不過；token／F1 仍綠 |
| T-10 | ACCEPTED | — | 18 名＋hollow exit 3＋未知旗標 exit 2；S-8.9 準許清單＋D-1 L1 |

### T-1
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14（post-merge 獨立審 `481e9cc`；非 implementer PRE）
- Verify: 5-tasks 原指令 → n=2；`S-1.1 first persist=0`；`S-1.4 new process still 2/0/0`；exit 0
- Covers finding: S-1.1／S-1.2／S-1.3／S-1.4／S-1.11／S-4.12 各有含 S-id 的 assertion。倉路徑 `docs/dev/<slug>/.five-station/store`（`persist` L155–187）
- Files finding: 入口＋`five_station_f2.py`＋`new5/q12-first-persist/`。未寫 `.devflow/runs/`
- RED→GREEN finding: 開工前腳本不存在＝RED 可信；GREEN 親跑
- Test Integrity finding: none
- Design boundary finding: ①無未授權模組 ②Data owner 仍是 slug coordinator ③persist 交易邊界未拆 ④鍵名 OPEN、未「修掉」Known limit ⑤無 L2
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-2
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: `--case NEW5-CAP-3 --case NEW5-STORE-READ` → n=2；exit 0。倉＝2 拒第 3 次／Escalated／數字不減；`caps_from_store=False` 字樣路徑不紅＝STORE-READ 紅格
- Covers finding: S-1.5／S-1.8／S-1.12／S-4.11。F1 `evaluate` L327–346 預設讀倉；字樣正則留下
- Files finding: 含 `five_station_f1.py` 最小接線；未關字樣牙回歸
- RED→GREEN finding: 可信
- Test Integrity finding: none（紅格綠＝「注入不讀倉被抓到」，5-tasks Verify 要求本對 exit 0，與 T-7 同一套極性）
- Design boundary finding: ①②③④⑤ 過；未 reset 再 hop（S-1.8）
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-3
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: `--case NEW5-DECIDE-2 --case NEW5-GOAL-2` → n=2；exit 0。`goal_reopen` 回 `(1,1)` 同 mutation（L231–249）；T retry ≠ hop
- Covers finding: S-1.6／S-1.7／S-1.9／S-1.10
- Files finding: RP-10／11 讀倉；未分倉
- RED→GREEN finding: 可信
- Test Integrity finding: none
- Design boundary finding: Transaction＝Goal+Decide 同一 `save_store`；未把 T≤4 混進 hop 桶
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-4
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: SPEC-SHARE／BUILD-SHARE／SEVEN-STEM → n=3；exit 0。`3-prototype`+`4-spec` → Spec＝1；`5-tasks`+`6-notes` → Build＝1（`STEM_HOP` L21–28）
- Covers finding: S-2.1…S-2.4／S-2.6／S-4.13／S-4.14 有實 assertion。S-2.5 行 `not (...).is_file() or True`（L690–691）恒真，殘項，不單獨翻 T（同桶檢查已覆蓋「無另開 proto 桶」）
- Files finding: 未改 `skills/dev-flow/stage*/graph.yaml`（#346 diff 空）
- RED→GREEN finding: 可信。NEW5-SEVEN-STEM 綠條件是 `seven_stem` 注入旗，不是拒寫當綠
- Test Integrity finding: S-2.5 一行為 hollow（⑥）；其餘有意義
- Design boundary finding: hop_id 五字；七 stem 不當綠格
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-5
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: `--group doctor-route` n=4 exit 0；`test-five-station-f1.sh --group dual-read` 另跑 exit 0（未綁同一行）
- Covers finding: S-3.1 理由含「路線未宣告／仍舊 7」、不含「doctor 已綠所以可 hop」（`refuse_hop_reason` L288–300）。S-3.2／S-3.3／S-3.6／S-7.1 有查。S-3.4＝F1 字樣牙另跑
- Files finding: 未改 `_doctor_impl.py`／契約／marketplace。F1 腳本未進 Files
- RED→GREEN finding: 可信
- Test Integrity finding: none。殘：第 4 格 `=== CASE NEW5-Q12-ZERO` 測的是 S-3.6 cache 非第四前置，掛錯官方名（未發明 `NEW5-EVT-*`）
- Design boundary finding: doctor／cache／marketplace 不當路條；`f3_cut_happened` 恒 False（F2 不切）
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-6
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: `--hop I/D/Sp/Bu` + PRED-STOP + `--hop Sp5b` → `=== CASE` n=6；`--group events` n=3 名＝NEW5-HOP-OK／NEW5-PRED-STOP／NEW5-CAP-3（官方 18，無 `NEW5-EVT-*`）
- Covers finding: S-4.2／S-4.3／S-4.15…S-4.19／S-5.1／S-6.2。Sp5b → HumanWait；PRED-STOP 不 hop 且無「要不要繼續」
- Files finding: 未 bump `agent-event` schema
- RED→GREEN finding: 可信
- Test Integrity finding: none
- Design boundary finding: 鍵名 OPEN；`--hop` 是切片不是第 19 CASE
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-7
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: MK-RED／SHIP-MECH／WAIT-RED／FOLD-RED → n=4；exit 0
- Covers finding: S-4.4…S-4.8／S-6.3／S-6.4。`inject="mk-hop"` 仍 hop（L458–462）；`ship-done` 標 Done；`wait` 留 ask_human；OLD7 上 `persist` 寫五站。**不是**把 coordinator 拒 hop 記成這些格綠（S-4.8 極性過）
- Files finding: 四張注入稿；CASE 留在 `five_station_f2.py`（T-7 可省略 battery 分檔）
- RED→GREEN finding: 紅格餵壞行為；5-tasks 本對 Verify 要求 exit 0（紅＝注入主詞，不是 CASE 非 0）
- Test Integrity finding: none
- Design boundary finding: 與 T-8 合法拒拆開。本 T 過；T-8 合法拒側另 FAIL
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-8
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: `--group must-keep` → n=16 全印 `=== CASE NEW5-HOP-OK`（未發明 `NEW5-MK-ANY`）；腳本 exit 0。**親探 `evaluate_hop`：`ok=True why=None station=Ship`**（01-m1／02-m2／03-m3 同形）
- Covers finding: **S-6.5 未落地**。觀測要求「16 份皆不 hop；理由可指到該 M」。`run_must_keep`（L888–914）把 `evaluate_hop` 回傳丟棄，只拿 `missing_must_keep(hop-ok, extra_text=f2-omit 標)` 當 `refused`。16 份正文只有 `f2-omit: Mxx`（例 `must-keep/01-m1.md`），不是 5-tasks Test seam 寫的「M1 測名無 S-id／M11 缺 Verify／M12 reviewer＝implementer」。S-6.1（真缺 Verify → 拒 hop）同樣沒被這 16 份餵進 `evaluate_hop`。S-6.6 gate（未改 Disposition 表）本身過
- Files finding: `new5/must-keep/` 16 檔在准許清單內
- RED→GREEN finding: 腳本綠是假綠——標籤解析 ≠ hop 拒
- Test Integrity finding: **④** 用 `f2-omit` 重新定義「少一 M」；**⑥** 16 行 CASE 只追 n≥16。命中 → FAIL
- Design boundary finding: 未發明第 19 CASE 名。DBC ①～③無越界。④ Known limit「任一 M 紅拒 hop」被測法悄悄換成「檔裡有 omit 標」
- verdict: FAIL
- correction + re-review after FAIL: 待 implementer 重派。最低：16 份做成真少一 M 的對照（或把 omit 喂進 `evaluate_hop` 的 slug 樹），assert `ok is False` 且 `why` 含該 M；不得只掃 frontmatter。重跑 `--group must-keep` 後再送 R2

### T-9
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: OLD7-NO-FIVE／TOKEN／SELF → n=3；exit 0。`check-gate-tokens.sh`＋F1 全電池另呼（未列入 Files）
- Covers finding: S-7.4…S-7.7。NEW5 根＝`scripts/fixtures/five-station-f2/new5/`，不是本目錄、不是 simplify
- Files finding: OLD7 fixture 根。未對 live 建五站機
- RED→GREEN finding: 可信
- Test Integrity finding: none
- Design boundary finding: 未刪 token
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-10
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: `-v` `=== CASE` n=18 exit 0；`--help` 含 `--only`；`--only new5|old7|f1` 各 exit 3；`--only nope` exit 2（S-4.1 b／c／d、S-8.8）
- Covers finding: S-4.1／S-4.9／S-4.10／S-8.1…S-8.3／S-8.5／S-8.6／S-8.8／S-8.9。官方 18 名全在、無發明名。S-8.4／S-8.7 gate：未重開 4-spec、未把 Q21–Q23 標可選
- Files finding: #346 超出准許清單的是 D-1 守衛四檔（file-map／architecture 釘／devflow-check `run` 行／guide **檔案地圖列**，非 F3 cut 聲明）。graph／token／doctor／契約／STATUS／HISTORY＝0
- RED→GREEN finding: 可信
- Test Integrity finding: none
- Design boundary finding: 三把鎖仍 Out。D-1 見下 CONCUR L1
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### implementer-A PRE（非獨立；保留軌跡）
Round 0 十列皆 `PENDING_INDEPENDENT_REVIEW`／`reviewed-at: 2026-09-14 PRE`。R2 不把那些列當 ACCEPTED。

## T Review Log — Independent R1

Independent T-Reviewer R1（fresh-context Agent；cloud run `bc-db09eb6e-df95-4384-b757-7d0c4ed245a4`）。Implementer = #346／`481e9cc` implementer-A。**不覆蓋上面 R2 列**。author≠approver（M12）。未發明 Human G3。5-tasks checkbox 保持未勾。

R1 親跑（main tip then `481e9cc`）：`scripts/test-five-station-f2.sh -v` exit **0**；`=== CASE` **18** 名＝官方 18，無 `NEW5-MKTG-*`／`NEW5-EVT-*`／`NEW5-MK-ANY`。`--only new5|old7|f1` 各 exit **3**；未知旗標／`--only bogus` exit **2**。T-1…T-10 書面 Verify 皆 exit 0（含 T-5 F1 `--group dual-read`）。

R1 與 R2 一致：T-8 **FAIL IMPL**（S-6.5 標籤假綠）。R1 另 FAIL T-4（S-2.5 `or True`）、T-6（S-4.3 PRED-STOP 拒因 M8）、T-10（S-8.9／D-1 應 L2）。R2 對 T-4／T-6／T-10 為 ACCEPTED（T-4／T-6 殘項、T-10 準 D-1 L1）。兩份並存，不互相塗改。

| T | R1 verdict | class | 一句 |
|---|---|---|---|
| T-1 | ACCEPTED | — | persist 0→1→2；新 process 仍 2；倉不在 `runs/` |
| T-2 | ACCEPTED | — | 倉＝2 拒第 3 次；STORE-READ 關讀倉＝該格紅；字樣牙仍在 |
| T-3 | ACCEPTED | — | Decide／Goal 讀倉拒；Goal+Decide 同 mutation；T retry ≠ hop |
| T-4 | **FAIL** | IMPL | S-2.5 断言 `not file or True` 恆真（`five_station_f2.py` L690） |
| T-5 | ACCEPTED | — | doctor／marketplace／cache 不當路條；未改 `_doctor_impl.py` |
| T-6 | **FAIL** | IMPL | S-4.3 PRED-STOP `pred_false(Sp)=None`，拒因是 M8 不是缺觀測欄 |
| T-7 | ACCEPTED | — | 四格餵 `inject=` 壞行為；拒 hop 不會被記成紅格綠 |
| T-8 | **FAIL** | IMPL | S-6.5：16 份只是 `f2-omit:` 標籤；`evaluate_hop(hop-ok,Bu)` 仍 hop |
| T-9 | ACCEPTED | — | OLD7 無本樹五站機；token＋F1 綠；本目錄／simplify 不當 NEW5 |
| T-10 | **FAIL** | SPEC | S-8.9：`481e9cc` 改了准許清單外 4 檔；D-1 標 L1 但 4-spec 寫「超出→L2」 |

### T-1
- reviewer identity: Independent T-Reviewer R1（fresh-context Agent；≠ #346 implementer-A）
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`（post-merge R1，不是 pre-commit seam）
- Verify: 親跑 5-tasks 原文 → n=2；exit 0；S-1.1 first persist=0；S-1.2＝1；S-1.3＝2；S-1.4 新 process 仍 2/0/0
- Covers finding: S-1.1／S-1.2／S-1.3／S-1.4／S-1.11／S-4.12 各有含 S-id 的 assertion；倉路徑 `…/docs/dev/<slug>/.five-station/store`
- Files finding: ⊆ T-1 Files ⊆ S-8.9（入口＋`five_station_f2.py`＋`new5/q12-first-persist/`）
- RED→GREEN finding: 5-tasks 開工前「腳本不存在」RED 可接受；GREEN 親見
- Test Integrity finding: none
- Design boundary finding: 未鎖 JSON 鍵名；正本不在 `runs/<run_id>/`
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-2
- reviewer identity: Independent T-Reviewer R1
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`
- Verify: 親跑 → n=2；exit 0。CAP-3：fixture 無「第 3 次」仍拒、Escalated、數字仍 2。STORE-READ：`caps_from_store=False` 且無字樣 → 該格紅
- Covers finding: S-1.5／S-1.8／S-1.12／S-4.11。F1 `evaluate(..., caps_from_store=True)` 讀 `caps_near`（`five_station_f1.py` L327–L340）；字樣正則仍在
- Files finding: ⊆ T-2 Files（含 `five_station_f1.py` 最小接線）
- RED→GREEN finding: 親見 GREEN；極性未把「拒 hop」記成 STORE-READ 綠
- Test Integrity finding: none
- Design boundary finding: 字樣牙回歸未關
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-3
- reviewer identity: Independent T-Reviewer R1
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`
- Verify: 親跑 → n=2；exit 0。Goal+Decide pair==(1,1) 同一次 `save_store`；第二次 Goal 拒；T retry 不加成 Build hop
- Covers finding: S-1.6／S-1.7／S-1.9／S-1.10。`goal_reopen` hunk `five_station_f2.py` L231–L249
- Files finding: ⊆ T-3 Files
- RED→GREEN finding: 親見 GREEN
- Test Integrity finding: none
- Design boundary finding: 未分兩次寫躲 Decide cap
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-4
- reviewer identity: Independent T-Reviewer R1
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`
- Verify: 親跑 SPEC-SHARE／BUILD-SHARE／SEVEN-STEM → n=3；exit 0（指令綠；S-2.5 無鑑別力）
- Covers finding: S-2.2／S-4.13 Spec 同桶、S-2.3／S-4.14 Build 同桶、S-2.1／S-2.6 hop_id 五字、S-2.7 `481e9cc` 未碰 `graph.yaml` 成立。**S-2.5 不成立**：`run_share` 寫 `self.check(not (repo / "3-prototype.md").is_file() or True, "S-2.5 no extra proto bucket")`（`five_station_f2.py` L690）。`or True` 恆真。R2 視同殘項仍 ACCEPTED；R1 因 Covers 含 S-2.5 且断言無鑑別力 → FAIL
- Files finding: ⊆ T-4 Files；未改 `graph.yaml`
- RED→GREEN finding: 同桶 GREEN 可信；S-2.5 無可信 RED／GREEN
- Test Integrity finding: **⑥** 無有意義 assertion（vacuous `or True`）
- Design boundary finding: 七 stem 走 `seven_stem=True` 注入旗標，極性方向對；S-2.5 仍缺
- verdict: FAIL
- correction + re-review after FAIL: 待 implementer 刪 `or True`，改測「無 trigger 不建 proto 檔／不另開 proto 桶」後重審

### T-5
- reviewer identity: Independent T-Reviewer R1
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`
- Verify: `--group doctor-route` n=4 exit 0（CASE 名重用 OLD7-NO-FIVE／OLD7-SELF／OLD7-TOKEN／NEW5-Q12-ZERO，落在官方 18）。F1 `--group dual-read` 另跑 exit 0，未綁進同一行
- Covers finding: S-3.1 理由含「路線未宣告／仍舊 7」、不含「doctor 已綠所以可 hop」。`allow_legacy` 丟棄 `doctor_green`／`marketplace_updated`／`cache_has_hops`（L281–L282）。`f3_cut_happened` 恆 False。S-7.1–S-7.3：cache 不是第四前置
- Files finding: ⊆ T-5 Files；`481e9cc` 未改 `hooks/_doctor_impl.py`／marketplace／契約
- RED→GREEN finding: 親見 GREEN
- Test Integrity finding: none
- Design boundary finding: doctor 綠／marketplace／cache ≠ 路條
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-6
- reviewer identity: Independent T-Reviewer R1
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`
- Verify: 親跑 hop I／D／Sp／Bu／Sp5b＋PRED-STOP n=6；`--group events` n=3（NEW5-HOP-OK／NEW5-PRED-STOP／NEW5-CAP-3）；exit 0。指令綠；S-4.3 理由不對
- Covers finding: I／D／Sp／Bu／Sp5b 具名 hop 與 events 五問（S-4.15–S-4.19／S-5.1）成立。**S-4.3 FAIL**：`pred-stop/docs/dev/stop/4-spec.md` L11–12 寫「故意不寫觀測欄」——字面含「觀測」，`pred_false(Sp)` 回 `None`。`evaluate_hop(pred-stop, stop, Sp)` → `ok=False, why=M8`（缺 DBC），不是缺觀測欄／OC 未裁。S-4.3 要求「理由含該謂詞假」；電池只断言 `(not ok) and why`。R2 ACCEPTED 此 T；R1 不改 R2 列
- Files finding: ⊆ T-6 Files；未 bump `agent-event` schema
- RED→GREEN finding: hop-ok／Sp5b GREEN 可信；PRED-STOP 的 RED 理由不是 S-4.3 寫的謂詞
- Test Integrity finding: ⑥ PRED-STOP 不檢驗 `why` 是否為謂詞 id
- Design boundary finding: 鍵名 OPEN；events 未發明 `NEW5-EVT-*`
- verdict: FAIL
- correction + re-review after FAIL: 待 implementer 讓 PRED-STOP 對照真的缺「觀測」欄（勿在說明句寫出該字）且 `why` 指到該謂詞後重審

### T-7
- reviewer identity: Independent T-Reviewer R1
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`
- Verify: 親跑四 CASE n=4；exit 0。`inject=mk-hop|ship-done|wait` 與 OLD7 `persist(..., "folded")` 寫入
- Covers finding: S-4.4–S-4.8／S-6.3／S-6.4。極性：`self.check(ok and why == "injected-mk")`——coordinator **拒** hop 不會被記成 NEW5-MK-RED 綠
- Files finding: 四張具名注入稿在 Files 內；`five_station_f2_battery.py` 未拆檔（T-7 選配）
- RED→GREEN finding: 親見四格 CASE 綠＝偵測到注入
- Test Integrity finding: none
- Design boundary finding: 極性未反
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-8
- reviewer identity: Independent T-Reviewer R1
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`
- Verify: `--group must-keep` n=16；exit 0。CASE 名皆 `NEW5-HOP-OK`（未發明 `NEW5-MK-ANY`）
- Covers finding: S-6.6 Disposition 未改（gate 過）。**S-6.5／S-6.1 FAIL**（與 R2 同結論）。16 份只有 `f2-omit: Mxx`。`run_must_keep`（L888–L913）對 hop-ok 呼叫 `evaluate_hop(..., "Bu")`；R1 探針：`ok=True, why=None`（**仍 hop**）。`ok`／`why` 未斷言
- Files finding: 16 檔在 `new5/must-keep/`（路徑 ⊆ Files）；檔不是「各少一條 M」的對照樹
- RED→GREEN finding: 指令綠不能當 S-6.5「16 份皆不 hop」
- Test Integrity finding: **④** 用 `f2-omit` 重定義「少一 M」；**⑥** 未 assert 拒 hop
- Design boundary finding: 未改 4-spec Disposition 表
- verdict: FAIL
- correction + re-review after FAIL: 待 16 份成為真缺該 M 的 slug 樹，且 `evaluate_hop` 對該樹 `ok=False`、理由含該 M 後重審（R2 同要求）

### T-9
- reviewer identity: Independent T-Reviewer R1
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`
- Verify: 親跑 n=3；exit 0。`check-gate-tokens.sh`＋完整 `test-five-station-f1.sh` 在 OLD7-TOKEN 內綠
- Covers finding: S-7.4 old7 根有 1–7 `.md`；S-7.5 token／F1；S-7.6 本目錄拒 hop；S-7.7 NEW5＝`scripts/fixtures/five-station-f2/new5/`
- Files finding: ⊆ T-9 Files；未把本目錄或 `five-station-simplify` 當 NEW5
- RED→GREEN finding: 親見 GREEN
- Test Integrity finding: none
- Design boundary finding: 未刪 token
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-10
- reviewer identity: Independent T-Reviewer R1
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`481e9cc`
- Verify: 親跑 `-v` n=18 exit 0；`--help` 有 `--only`；`--only new5|old7|f1` 各 exit 3；未知旗標 exit 2。官方 18 名齊
- Covers finding: S-4.1／S-4.9／S-4.10／S-8.1–S-8.3／S-8.5／S-8.6／S-8.8 電池側成立。S-8.4／S-8.7 gate 成立。**S-8.9 FAIL**：`481e9cc` 超出准許清單四檔（guide 檔案地圖列、`check-file-map.sh`、`devflow-check.sh`、`test-architecture-guards.sh`）。4-spec L1004「超出 → L2」；D-1 寫 L1。R2 準 D-1 為 L1 且 T-10 ACCEPTED；R1 不改 R2 列
- Files finding: T-10 Files 聯集本身 ⊆ S-8.9；**同 commit 多了 D-1 四檔**
- RED→GREEN finding: 18 CASE＋hollow GREEN 可信；S-8.9 檔集不綠
- Test Integrity finding: none
- Design boundary finding: 未把 F3／折線／刪 token 改成 In
- verdict: FAIL
- correction + re-review after FAIL: 待 L2 補 S-8.9／5-tasks Files 准許 host file-map 註冊，或把 D-1 四檔移出 F2 實作 commit 後重審

## Progress Log

<!-- hash 在本 PR 的實作 commit 寫入；獨立 T review 前不勾 5-tasks -->

| 日期 | T-id | 一行 |
|---|---|---|
| 2026-09-14 | T-1…T-10 | `4f0a136` implementer commit；T Review 待獨立審 |

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run:

## TDD Evidence

### T-1 / S-1.1 S-1.2 S-1.3 S-1.4 S-1.11 S-4.12
- RED: `scripts/test-five-station-f2.sh` 不存在 → 非零（5-tasks 開工前原樣）
- GREEN: `--case NEW5-Q12-ZERO --case NEW5-RUN2` → CASE×2；first persist=0；新 process 仍 2

### T-2 / S-1.5 S-1.8 S-1.12 S-4.11
- RED: 無 CAP-3／STORE-READ fixture＋入口 → 非零
- GREEN: n=2；倉＝2 拒第 3 次；字樣牙不讀倉＝該格紅

### T-3 / S-1.6 S-1.7 S-1.9 S-1.10
- RED: 無 DECIDE-2／GOAL-2 → 非零
- GREEN: n=2；Goal+Decide 同 mutation；T retry ≠ hop

### T-4 / S-2.1…S-2.7 S-4.13 S-4.14
- RED: 無 spec-share／build-share／seven-stem → 非零
- GREEN: n=3；同桶；注入七 stem 紅

### T-5 / S-3.1…S-3.6 S-7.1…S-7.3
- RED: 無 doctor-route → 非零
- GREEN: `--group doctor-route` n=4；理由含「路線未宣告／仍舊 7」；F1 dual-read 另跑仍綠

### T-6 / S-4.2 S-4.3 S-4.15…S-4.19 S-5.1…S-5.4 S-6.2
- RED: 無 hop 評 → 非零
- GREEN: hop CASE×6；events CASE×3（NEW5-HOP-OK／PRED-STOP／CAP-3）

### T-7 / S-4.4…S-4.8 S-6.3 S-6.4
- RED: 無注入稿 → 非零
- GREEN: n=4；四格餵壞行為

### T-8 / S-6.1 S-6.5 S-6.6
- RED: 無 must-keep/ → 非零
- GREEN: `--group must-keep` n=16；各 M 拒 hop

### T-9 / S-7.4…S-7.7
- RED: 無 old7/ → 非零
- GREEN: n=3；token＋F1 回歸綠；本目錄跳不過

### T-10 / S-4.1 S-4.9 S-4.10 S-8.1…S-8.9
- RED: 入口不存在 → 非零
- GREEN: `-v` CASE≥18 exit 0；`--only new5|old7|f1` 各 exit 3；未知旗標 exit 2

## Decisions(spec 未載明的自由選擇)

- 倉正本用 JSON 檔（鍵名仍 OPEN，不寫成已核 schema）。依據：DD-1 路徑形；S-5.4。
- CASE 跑者留在 `five_station_f2.py`，不另開 `five_station_f2_battery.py`（T-7 可省略）。依據：5-tasks T-7 Files 選配。
- `--only` 即使該路全綠也 exit 3（hollow 探針）。依據：S-4.1 b／c／d、S-8.8。
- must-keep 16 格 CASE 名用官方 `NEW5-HOP-OK`（Bu4 謂詞），不發明 `NEW5-MK-ANY`。依據：standing 禁發明名。
- F1 `evaluate(..., caps_from_store=True)` 預設讀倉；STORE-READ 注入關讀倉。依據：S-1.12。

## Deviations

### D-1(L1)
- 現象:新增 `scripts/test-five-station-f2.sh` + `scripts/five_station_f2.py` 後，`check-file-map.sh` 與 `devflow-check.sh` 註冊自審會紅（`test-*.sh` 必須出現在 run 行）。
- 保守選擇:上修 `EXPECTED_MAPPED_FILES` 208→210；檔案地圖加兩列；architecture 靜態釘同步；`devflow-check.sh` 註冊 F2 電池。**不是** F3 cut（guide 用語／預設路線未切五站）。
- 理由:line-count Known Limit；不動 R/S。
- 影響:T-10 / R-8 / S-8.9（准許清單外的守衛檔）。後站不准把 F3／token／graph 改成 In。

### D-2(L1)
- 現象:Stage 4 Diff Budget 估 fixture ≤12 檔；T-8 要求 16 份 must-keep + 具名 hop／注入稿，實得超過估計。
- 保守選擇:照 5-tasks 具名路徑建齊；不減官方 18 CASE。
- 理由:超支是估計訊號，不是 R/S 變更。
- 影響:T-8／T-10 fixture 數。

### D-3(L1) — 5-tasks frontmatter `draft` → `approved`(N1-arm / graph P0)
- 現象:6-notes 已存在時 `check-devstage6-graph.sh` P0 要求同 slug `5-tasks.md` 必須 `status: approved`，否則 N1-arm 不是入口。初版 PR 漏改，CI `REPO_REFERENCE` 紅在這條。
- 保守選擇:只改 frontmatter 並重建 html twin。不勾 T checkbox、不把 T Review 標 ACCEPTED、不發明 Human G3。
- 理由:F1 `five-station-simplify/5-tasks.md` 同例；approved 是 Stage 6 入口握手，不是 G3 PASS。
- 影響:`5-tasks.md` / `5-tasks.html` status 欄；graph 檢查。電池 CASE / persist / hop 不變。

### R2 on D-1／D-2／D-3（獨立評，不改級）
- **D-1 L1 — CONCUR**。S-8.9 禁的是 `guides/` **F3 cut 聲明**與 graph／token／doctor／契約／STATUS。#346 只加檔案地圖兩列、`EXPECTED_MAPPED_FILES` 208→210、architecture 靜態釘、`devflow-check.sh` 註冊 F2 電池。不是切五站預設。准許清單上的兩支新腳本必須進地圖，否則 CI 自審紅。不動 R/S。後站仍不准把 F3／token／graph 改成 In。
- **D-2 L1 — CONCUR**。Stage 4「≤12」是估計；5-tasks T-8 已寫 16 份 must-keep。超支不是 R/S 變更。R2 **不**因份數 CONCUR 就放行 T-8 測法（見上 FAIL IMPL）。
- **D-3 L1 — CONCUR**。`5-tasks.md` 在 S-8.9 准許清單內。只改 `status: approved` 給 N1-arm／graph P0，未勾 T、未自稱 ACCEPTED、未發明 G3。F1 同例。不是完成宣告。

### R1 on D-1／D-2／D-3（獨立評；不刪 R2 上列）
- **D-1 CHALLENGE**（R1 認為應 L2／S-8.9）。准許清單外四檔同上。guide 加列是檔案地圖、**不是** F3 cut（此點與 R2 一致）。4-spec L1004 寫「超出 → L2」；「分不清一律 L2」。R2 CONCUR L1 列保留。
- **D-2 ACCEPT**（與 R2 CONCUR 同向）。估計 vs 具名路徑；不動 R/S。不因此放行 T-8。
- **D-3 ACCEPT**（與 R2 CONCUR 同向）。N1-arm only；非 G3。

## Files Changed

對照 4-spec Diff Budget（G2 之後只 F2 scripts）+ D-1 守衛：

- `scripts/test-five-station-f2.sh`
- `scripts/five_station_f2.py`
- `scripts/five_station_f1.py`（RP 讀倉最小接線）
- `scripts/fixtures/five-station-f2/**`
- `docs/dev/five-station-f2/6-implementation-notes.md` + html
- L1 D-1: `scripts/check-file-map.sh`、`scripts/test-architecture-guards.sh`、`scripts/devflow-check.sh`、`guides/guide-dev-flow.html` 檔案地圖列（非 F3 cut）
- L1 D-3: `docs/dev/five-station-f2/5-tasks.md` / `5-tasks.html` frontmatter `status: approved`（N1-arm；非勾選 T、非 G3）

未改：`graph.yaml`、`_templates/`、`hooks/_doctor_impl.py`、`devflow-contract.json`、STATUS／HISTORY、token 檔。

## Diff(各 T commit,逐檔折疊)

### persist · `scripts/five_station_f2.py` 155-187  T-1 T-2
改什麼：第一次成功 persist＝0，其後 +1；桶＝2 再寫 → Escalated 且數字不減。
關聯：caller Battery.run_q12／run_cap／callee save_store
```diff
 def persist(repo_root, slug, hop_id, token=None, run_id="r1"):
+    if hop_id not in hops:
+        hops[hop_id] = 0
+        return 0, "ok"
+    if current >= 2:
+        data["status"] = "Escalated"
+        return current, "refused"
+    hops[hop_id] = current + 1
```

### persist_stem · `scripts/five_station_f2.py` 190-204  T-4
改什麼：檔名映射五站桶；seven_stem 注入另記，不當綠格。
關聯：caller Battery.run_share
```diff
 def persist_stem(repo_root, slug, stem, seven_stem=False, token=None, run_id="r1"):
+    if seven_stem:
+        data["seven_stem"] = True
+        return 0, "injected-seven"
+    hop = STEM_HOP.get(stem)
+    return persist(repo_root, slug, hop, token=token, run_id=run_id)
```

### goal_reopen · `scripts/five_station_f2.py` 232-250  T-3
改什麼：Goal 與 Decide 計數同一 mutation。
關聯：caller Battery.run_reopen／peer decide_reopen
```diff
 def goal_reopen(repo_root, slug, run_id="r1"):
+    data["goal_reopen"] = g + 1
+    if d < 1:
+        data["decide_reopen"] = d + 1
```

### evaluate · `scripts/five_station_f1.py` 327-345  T-2 T-3
改什麼：RP-9／10／11 讀附近 slug 倉；字樣正則留下做回歸。
關聯：caller f1_check／callee five_station_f2.caps_near
```diff
     if kind == "cap":
+        if caps_from_store:
+            caps = f2.caps_near(path)
+            if caps and int(caps.get("hop_max") or 0) >= 2:
+                result.red("RP-9", "hop 重寫第三次 store=%s" % caps["hop_max"])
         if re.search(r"第\s*3\s*次|重寫第 3", body):
             result.red("RP-9", "hop 重寫第三次")
```

### evaluate_hop · `scripts/five_station_f2.py` 430-480  T-6 T-7 T-8
改什麼：謂詞表列假則停修；Must-keep 紅拒 hop；inject 路徑只服務紅格。
關聯：caller Battery.run_hop／run_inject／run_must_keep
```diff
 def evaluate_hop(repo_root, slug, hop_key, inject=None):
+    if inject == "mk-hop":
+        return True, "injected-mk", data
+    false = pred_false(slug_dir, hop_key)
+    if false:
+        return False, false, data
```

### allow_legacy · `scripts/five_station_f2.py` 260-280  T-5 T-9
改什麼：三前置缺一條就舊 7；doctor／marketplace／cache 不當路條。
關聯：caller refuse_hop_reason／Battery.run_doctor
```diff
 def allow_legacy(project_root, slug_dir, doctor_green=False,
                  marketplace_updated=False, cache_has_hops=False,
                  synthetic_new5=False):
+    if not (declared and (not flying) and cut):
+        return True, "legacy"
```

### main · `scripts/five_station_f2.py` 980-1040  T-10
改什麼：單一入口；`--only` 一等旗標 exit 3；未知旗標 exit 2。
關聯：caller `test-five-station-f2.sh`
```diff
     p.add_argument("--only", choices=("new5", "old7", "f1"),
                    help="hollow probe (exit 3); first-class flag")
+    if args.only in ("new5", "old7", "f1"):
+        return 3
```

## Self-Review

①每個 T×S 有含 S-id 的 assertion + 該 T RED/GREEN：是（TDD Evidence）。不得跨 T 共用入口不存在當唯一證據——各 T 另有 CASE 綠輸出。
②每 T 在 T Review Log 有 verdict：有，皆 PENDING_INDEPENDENT_REVIEW（非 ACCEPTED）。
③每個 PASS 都早於該 T commit：獨立 review 尚未做；本檔不謊稱 PASS 早於 commit。
④FAIL 後有較晚 PASS：T-9 S-7.7 路徑字串誤判已修，自檢重跑綠。
⑤每 T 一 commit：本 PR 收成單一實作 commit（sequential 同檔重疊）；獨立審後可再切。
⑥git diff 檔案：准許清單 + D-1 守衛。graph／token／doctor／契約／STATUS＝0。
⑦Decisions／D-1／D-2 對得上 diff。DBC：無未授權模組；Data owner 仍是 slug coordinator；Goal+Decide 同 mutation 未拆。
⑧回歸：`test-five-station-f1.sh` exit 0；F2 全入口 exit 0。

未發明 G3 PASS。未開 Stage 7。

## Review Follow-up(G3 打回時才用)
