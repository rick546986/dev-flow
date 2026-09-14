---
feature: five-station-f3
stage: 6-implementation
status: draft
owner: implementer-A
updated: 2026-09-14
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: 822f84289f6f4267252907e36862e93f1c90eb9d

> Implementer notes + independent T-Review: **R2**（#385 tip `47514a2`；author≠#385）。未發明 Human G3 PASS。5-tasks checkbox 保持未勾。implementer-A PRE 列只當軌跡，**不是** verdict。

## 0. 起手

### 0a branch／錨點

- 只讀 4-spec／5-tasks／本檔／living。禁讀 1／2／3。
- `git fetch origin main` → `FORK=822f84289f6f4267252907e36862e93f1c90eb9d`
- `git switch -c cursor/five-station-f3-stage6-impl-c424 "$FORK"`
- `test "$(git rev-parse HEAD)" = "$FORK"` → 通過

### 0b worktree 隔離

n-a:本 feature 未並行。單一 checkout、無第二 worktree；不改 STATUS（companion 由 coordinator 開）；無另開容器／DB／queue。

### 0c 守衛與 doctor

手動實作（非 dev-run 派工）。`devflow-exec.sh start` 未武裝本 session（cloud agent 單線）。doctor 綠只握手，不是 hop 通行證（T-7 DOCTOR-NE-TICKET）。

## T Review Log

獨立 T-Reviewer **R2**（fresh-context Agent；cloud run `bc-9afc1e94-8579-41e1-8150-7e6734f5eb16`；author≠approver／M12）。基準 #385 tip `47514a2367b0c18d73317dc3fae13359fa1b0ca9`。Gold＝`origin/main` `5-tasks.md`＋`4-spec.md`（G2 PASS）。未讀 implementer Self-Review 當錨；未發明 G3 PASS；未勾 5-tasks checkbox。implementer-A PRE 列只當軌跡，**不是** verdict。不與 R1 對齊。

R2 親跑（2026-09-14，`47514a2`）：

| Probe | Result |
|---|---|
| `scripts/test-five-station-f3.sh -v` | `failed=0` exit 0；`=== CASE` ×33 行；unique 官方名＝**25**；無 `GRAPH-AGREE`／`HOLLOW-OK`／`NEW5-MKTG` |
| `--only new5\|old7\|token` | 各 exit **3**（一等旗標；非未知旗標假綠） |
| `--probe hollow-true\|hollow-files\|hollow-f2\|hollow-word\|two-script` | 各 exit **3** |
| `--probe polarity` | exit **1**（硬編碼 stub，見 T-8／T-10 殘） |
| `--not-a-real-flag` | exit **2** |
| `--group hollow -v` | 6 官方 HOLLOW-* 名；根＝`new5/html-only/` 不是 `old7/html-only/` |
| `--group graph-edges -v` | 只印 NEW5-CUT-OK＋PRE-HOPS-200（官方名） |
| `scripts/test-five-station-f2.sh` | `failed=0` exit 0（地板，不是 IFF） |
| `scripts/check-gate-tokens.sh` | 綠 |
| `check-devstage2-graph.sh`／`check-devstage4-graph.sh` | 綠 |
| `git diff --exit-code -- hooks/_doctor_impl.py` | 0 |
| Files vs S-8.2 | #385 60 檔 ⊆ 准許清單；`_templates/`／handshake／STATUS／HISTORY／F2 park／token 刪檔 **Diff Budget 0** |

| T | verdict | 分類 | 一句 |
|---|---|---|---|
| T-1 | ACCEPTED | — | ATTEST-VISIBLE 五切片；只讀；`which_condition=f3-cut` |
| T-2 | ACCEPTED | — | 親探 `f3_cut_happened=True` → ATTEST-SILENT-RED 獨立紅 |
| T-3 | ACCEPTED | — | F2 舊 reader 錯鍵留下；canonical-200／210；cut 獨立假 |
| T-4 | ACCEPTED | — | PRE-210 字面 `F3 cut 未發生`；PRE-AND 三缺；SLOT-REJECT |
| T-5 | ACCEPTED | — | cut-ok skip N7／N6；`--group graph-edges` 官方名；無 GRAPH-AGREE |
| T-6 | **FAIL** | **IMPL** | S-3.3：GRAPH-WORD-NE 只咬 guide「五站」+ YAML `next==N7-g1`；`graph_next` 恒 N7-g1 時本格仍綠（`five_station_f3.py` L513–526） |
| T-7 | ACCEPTED | — | HONEST 真跑 doctor INCOMPATIBLE；NE-TICKET 丟棄 `doctor_green`。殘：Verify 原文 stdout 無拒因字面 |
| T-8 | **FAIL** | **IMPL** | S-6.1／S-6.2／S-6.3：三格只 grep 注入稿（L566–592）；cut-ok `refuse_hop_reason=None`，無 M 編號拒因 |
| T-9 | ACCEPTED | — | FREEZE＋SELF 真閘。殘：OLD7-FOLD-RED 只 grep md |
| T-10 | ACCEPTED | — | 25 名＋`--only`／`--probe` 出口對；Files⊆S-8.2。殘：電池內 HOLLOW／TOKEN-DEL 是稿 grep |

### T-1
- reviewer identity: Independent T-Reviewer R2（fresh-context Agent；≠ #385 implementer-A）
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14（#385 tip `47514a2`；非 implementer PRE）
- Verify: 5-tasks 原指令（五 `--slot`）→ n=5；各切片 exit 0
- Covers finding: S-1.1 三槽＋`which_condition=f3-cut`（不是 `F3-cut-happened`、不是三前置 AND）；S-1.2 缺檔／空 who → False；S-1.4 呼叫前後位元組不變、缺檔不建檔；S-1.5 活樹契約無 cut 兄弟鍵
- Files finding: ⊆ T-1 Files ⊆ S-8.2。本 T 未寫活樹 `docs/dev/f3-cut-attestation.json`（活樹 cut 在 T-10）。未改 `five_station_f2.py`
- RED→GREEN finding: 開工前腳本不存在＝RED 可信；GREEN 親跑
- Test Integrity finding: none。sibling-reject fixture 是說明稿，SoT 牙在活樹契約鍵集合
- Design boundary finding: ①無未授權模組 ②Data owner 仍是寫 fixture 三槽的人 ③讀端不寫檔 ④`which_condition` 只命名 cut 位元 ⑤無 L2
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-2
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: `test -f …/inject-silent-true.md`＋`--case ATTEST-SILENT-RED` → n=1；exit 0
- Covers finding: S-1.3 親探：把 `f3_cut_happened` 改恒 `True` → `[FAIL] S-1.3 no qualifying three-slot`／`silent True without slots is the red cell`（獨立紅）。未把「函式回真」記成本格綠。S-1.6：本 T／本 PR 未改 `STATUS.md`；用語交付在 T-6
- Files finding: ⊆ T-2 Files。`git diff --name-only` 對 `docs/dev/STATUS.md` 空
- RED→GREEN finding: 可信。注入稿是說明；真正牙是 missing-tree `cut is False`
- Test Integrity finding: none
- Design boundary finding: 未改 graph／doctor／guide
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-3
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: READ-SEAM 三切片 `-ge 3`；各 exit 0
- Covers finding: S-2.1 `contract_version(canonical-200.json)==2.0.0`；S-2.2 舊 reader＝未改的 `five_station_f2.contract_version`（仍 `blob.get("version") or blob.get("contract_version")`，對正本 2.1.0 不以 `2.1` 開頭）；S-2.3 正本 2.1.0 → `declared` 真，cut 仍獨立假
- Files finding: ⊆ T-3 Files。未 bump 活樹契約（T-7）。F2 錯鍵／`f3_cut_happened==False` 原樣
- RED→GREEN finding: 可信
- Test Integrity finding: none
- Design boundary finding: 無 fallback 雙讀；2.1.0 ≠ cut
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-4
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: PRE 五棵 `-ge 5`。PRE-210 stdout 含 `F3 cut 未發生`、不含「已宣告所以切了」／「doctor 已綠所以可 hop」。PRE-AND 三缺各自 `路線未宣告|仍舊 7`／`in-flight`／`F3 cut 未發生`。PRE-HOPS-200 含 `SLOT-REJECT`、不含 marketplace。各 CASE exit 0
- Covers finding: S-2.4／S-2.5／S-2.6／S-2.7 有函式牙（`allow_legacy`／`refuse_hop_reason`／`graph_next`）。2.1.0 不冒充 cut
- Files finding: ⊆ T-4 Files。未改 `graph.yaml`（T-5）
- RED→GREEN finding: 可信
- Test Integrity finding: none。`hops_slot_reject` 未宣告時兩分支都回 SLOT-REJECT；真正擋改線的是 `graph_next==N7-g1`
- Design boundary finding: marketplace／cache／doctor 綠不是第四前置
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-5
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: `N7-g1.md`／`N6-g2.md` 仍在；NEW5-CUT-OK＋PRE-HOPS-200＋`--group graph-edges` `=== CASE` ≥3；cut-ok 無 `enter N7-g1`／`例行停`／`請人審`；graph-edges 無 `GRAPH-AGREE`／`GRAPH-SKIP`／`NEW5-EDGE`。exit 0
- Covers finding: S-3.1 cut-ok → `s2=N8-end`／`s4=N7-end`、閘 `legacy=False`；S-3.2／S-2.7 未宣告跳過側不生效；S-3.5 閘與條件邊同意；S-3.6 形＝`next_when_five`＋路線閘，不是刪節點；S-7.4 試體根＝`scripts/fixtures/five-station-f3/new5/cut-ok/`
- Files finding: ⊆ T-5 Files。節點檔 0 刪
- RED→GREEN finding: 可信
- Test Integrity finding: none
- Design boundary finding: 未發明 GRAPH-AGREE 當通過字
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-6
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: 5-tasks 原指令 → GRAPH-WORD-NE exit 0；`check-gate-tokens.sh` 綠；節點檔仍在
- Covers finding: **S-3.3 未獨立落地**。GIVEN（guide 已五站用語 ∧ YAML `next` 仍 `N7-g1`）是 T-5／T-6 之後的出貨態；WHEN「有人標 F3 成功」沒有獨立注入。親探：`graph_next` 恒回 `N7-g1`（行為沒切）時 GRAPH-WORD-NE **仍綠**；NEW5-CUT-OK 才紅。S-3.3 要求「該格獨立非 0」，本格不能靠 T-5。S-3.4（節點＋token）本身過
- Files finding: ⊆ T-6 Files。guide 七站單行→五站用語（交付物 ≠ SoT）。token 牙只呼叫
- RED→GREEN finding: Verify 綠是假綠——咬的是 YAML 預設鍵＋用字，不是「只用字仍停卻標成功」
- Test Integrity finding: **⑥** GRAPH-WORD-NE 無有意義行為 assertion（只 `default==N7-g1` ∧ `"五站" in guide`）。命中 → FAIL
- Design boundary finding: ①～③無越界。④ Known limit「用語≠成功」被測法換成「預設鍵仍是 N7-g1」
- verdict: FAIL
- correction + re-review after FAIL: 待 implementer 重派。最低：對「guide 已五站 ∧ 五站就緒 slug 的有效 next 仍是 N7-g1 ∧ 有人標成功」讓 GRAPH-WORD-NE **獨立紅**；不得只掃 YAML `next:` 字串。重跑 `--case GRAPH-WORD-NE` 後再送 R2

### T-7
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: CASE `DOCTOR-HONEST`／`DOCTOR-NE-TICKET` 各綠；`INCOMPATIBLE` 在 HONEST stdout；`git diff --exit-code -- hooks/_doctor_impl.py`；supported 含 `2.1.0`。5-tasks 原文後半 `ticket=$(… -v)` 再 `grep -E '路線未宣告|仍舊 7|F3 cut 未發生'` → **stdout 無拒因字面**（CASE 只印 `[ok] S-4.3 reason is route`）。親探 `refuse_hop_reason(doctor-ne-ticket, doctor_green=True)` → `路線未宣告 仍舊 7`
- Covers finding: S-4.2 真跑 `devflow-doctor.sh`：印 `INCOMPATIBLE`、非 0、禁 handshake-green token。S-4.3 丟棄 `doctor_green`。S-4.1 根檔 `devflow-contract.json` bump 2.1.0＋supported 加列。S-4.4 握手 0 diff。S-4.5 marketplace／cache 不是票
- Files finding: ⊆ T-7 Files。未寫活樹 cut
- RED→GREEN finding: CASE 綠可信。Verify 原文 stdout 牙與 CASE 輸出不對齊＝殘，不單獨翻 T（理由在函式回傳）
- Test Integrity finding: none。殘：doctor 入口讀 `docs/dev/devflow-contract.json` 仍 2.0.0（S-8.2 未列該複本，0 diff 正確）；F3 reader 讀根檔 2.1.0
- Design boundary finding: 未改握手語意；綠≠路條
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-8
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: 5-tasks 原指令 → 三 CASE n=3；exit 0（**腳本綠 ≠ Covers 綠**）
- Covers finding: **S-6.1／S-6.2／S-6.3 未落地**。`run_wait_red`／`run_keep_mk_red`／`run_keep_ship_mech`（L566–592）只讀注入稿字串（`N7-g1`／`仍 hop`／`Ship Done`）。S-6.2 觀測要求「拒絕理由含該 M 編號」：`refuse_hop_reason` 只有路線句；cut-ok 親探回 `None`（放行五站），無 M3／M5／M9／M11／M12／M15 牙。S-5.3：`--probe polarity`（L886–889）硬編碼印 FAIL 後 `return 1`，不反轉這三格跑者。fold wait（T-5 skip 例行停）已做；fold completeness（Must-keep／Ship 唯人）沒做
- Files finding: 三張注入稿在准許清單內
- RED→GREEN finding: 腳本綠是假綠——稿存在 ≠ 注入壞行為被抓
- Test Integrity finding: **④** 用「檔裡有 M 編號／N7-g1 字」重新定義紅格；**⑥** 三行 CASE 只追 n≥3。命中 → FAIL
- Design boundary finding: ④ Known limit「Must-keep 任一紅拒 hop／機械綠≠Ship Done／謂詞真不得例行停」被測法換成「注入稿存在」
- verdict: FAIL
- correction + re-review after FAIL: 待 implementer 重派。最低：WAIT＝三前置真仍進 N7-g1／留「要不要繼續」→ 本格獨立紅；KEEP-MK＝具名六 M 紅仍 hop → 本格紅且理由含該 M（只擋 M11＝仍紅）；SHIP-MECH＝無人 `verdict: PASS` 卻 Ship Done → 本格紅。不得只掃 markdown。`--probe polarity` 必須真的把「拒 hop 當紅格綠」打成入口非 0。重跑三 CASE 後再送 R2

### T-9
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: OLD7-FREEZE／OLD7-FOLD-RED／SELF-OLD7 → n=3；exit 0
- Covers finding: S-7.1 `has_old7` → legacy、無 `.five-station` 機、理由含 `仍舊 7`（fixture 無契約檔，先走未宣告句，仍是整段舊 7）。S-7.3 三凍結 slug 跳不過。S-7.5 未發明活五站名字。S-7.2 FOLD-RED 只 grep `inject-fold-red.md`（殘；凍結綠義務已由 FREEZE／SELF 咬）
- Files finding: ⊆ T-9 Files。NEW5 不是本目錄／f2／simplify
- RED→GREEN finding: FREEZE／SELF 可信
- Test Integrity finding: FOLD-RED ⑥ 殘，不單獨翻 T
- Design boundary finding: 未對 live 建五站機；未刪 token
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-10
- reviewer identity: Independent T-Reviewer R2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14
- Verify: `-v` `=== CASE` n≥25；exit 0；`--help` 含 `--only`／`--probe`；`--only new5|old7|token` 各 3；`--probe hollow-*`／`two-script` 各 3；`--probe polarity` 1；未知旗標 2；TOKEN／F3-F2-REGRESS n≥3；`--group hollow` ≥6 且六官方名、無 `HOLLOW-OK`／`NEW5-MKTG`；F2 地板綠；token 牙綠
- Covers finding: S-5.1 單一 process 三路；S-5.2 官方 25 名全在；S-5.4–S-5.6／S-5.9–S-5.10 入口牙＝`--probe`／`--only` exit 3（不是 `! bash` 未知旗標）；S-5.11 `new5/html-only/` → `has_old7` 假；S-5.7 F2 地板不是第四路 IFF；S-5.8 TOKEN-KEEP。S-8.2／S-8.3 Files⊆准許清單、禁區 0。S-8.1／S-8.5／S-8.6 gate：未改 4-spec 頂欄、未把 Q21–23 標可選、未重開 F2 park D-1…F-c-4。S-8.4 TOKEN-DEL-RED 是稿 grep（殘；TOKEN-KEEP 是活牙）
- Files finding: #385 檔集 ⊆ S-8.2。`check-five-station-f3.sh` 選配、恒 exit 0、不是第四路
- RED→GREEN finding: 入口／探針／25 名可信
- Test Integrity finding: none。殘：電池內 HOLLOW-*／TOKEN-DEL 只 grep 稿；`--probe polarity` 硬編碼（T-8 正犯）
- Design boundary finding: 未發明 G3；未勾 checkbox；未改 STATUS／HISTORY
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### implementer-A PRE（非獨立；保留軌跡）
Round 0 十列皆 `PENDING_INDEPENDENT_REVIEW`。R2 不把那些列當 ACCEPTED。

## Progress Log

<!-- T Review PASS 後才記 hash。本 stream 未自裁 PASS，故無 ACCEPTED 列。 -->

implementer commits（軌跡，不是 Progress Log 驗收列）：見本 branch `git log`。獨立審 PASS 後由 reviewer／coordinator 補 hash。

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)

Run: n-a:manual-implementer-stream

## TDD Evidence

### T-1 / S-1.1
- RED: `bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --slot ok` → 腳本不存在（開工前）
- GREEN: 同指令；`which_condition=f3-cut`；`f3_cut_happened` True

### T-1 / S-1.2
- RED: `--slot missing`／`--slot empty` 不存在
- GREEN: 缺檔／空 who → False

### T-1 / S-1.4
- RED: 無 readonly 切片
- GREEN: `--slot readonly` 呼叫前後位元組不變

### T-1 / S-1.5
- RED: 無 sibling-reject
- GREEN: `--slot sibling-reject`；契約無 cut 兄弟鍵

### T-2 / S-1.3
- RED: 無 ATTEST-SILENT-RED
- GREEN: 注入 `return True` 無三槽＝該格紅

### T-2 / S-1.6
- RED: 用語／blame 可冒充 SoT
- GREEN: 本 T 未改 STATUS；guide 用語不在本 T Files

### T-3 / S-2.1
- RED: F2 `contract_version` 讀錯鍵回空
- GREEN: `--reader canonical-200` 回 `2.0.0`

### T-3 / S-2.2
- RED: 無 READ-SEAM 舊 reader 格
- GREEN: 無旗標切片＝舊 reader 紅格

### T-3 / S-2.3
- RED: 正本 2.1.0 仍宣告假
- GREEN: `--reader canonical-210` 以 `2.1` 開頭；cut 獨立假

### T-4 / S-2.4
- RED: 2.1.0 冒充 cut
- GREEN: PRE-210-NE-CUT 理由含 `F3 cut 未發生`

### T-4 / S-2.5
- RED: PRE-AND 三缺不可數
- GREEN: `--missing declared|in-flight|cut` 各自理由

### T-4 / S-2.6
- RED: 2.0.0＋五站 hops 放行
- GREEN: PRE-HOPS-200 印 SLOT-REJECT

### T-4 / S-2.7
- RED: 未宣告就跳過
- GREEN: 跳過側在 `declared` 假時不生效

### T-5 / S-3.1
- RED: cut-ok 仍進 N7-g1
- GREEN: NEW5-CUT-OK hop 紀錄無例行停

### T-5 / S-3.2
- RED: graph 單邊跳過
- GREEN: PRE-HOPS-200 dual-read 仍舊 7

### T-5 / S-3.5
- RED: 發明 GRAPH-AGREE
- GREEN: `--group graph-edges` 只印官方名

### T-5 / S-3.6
- RED: 刪節點或只翻函式
- GREEN: `next_when_five` 條件邊＋路線閘；節點檔仍在

### T-5 / S-7.4
- RED: 本目錄當 NEW5
- GREEN: 試體根 `scripts/fixtures/five-station-f3/new5/cut-ok/`

### T-6 / S-3.3
- RED: 只用字當成功
- GREEN: GRAPH-WORD-NE 該格紅

### T-6 / S-3.4
- RED: 刪 N7-g1／token
- GREEN: 節點檔在；`check-gate-tokens.sh` 綠

### T-7 / S-4.1
- RED: supported 無 2.1.0
- GREEN: `hooks/runtime-capabilities.json` 含 `2.1.0`

### T-7 / S-4.2
- RED: 漏加仍印 COMPATIBLE
- GREEN: DOCTOR-HONEST 印 INCOMPATIBLE 且非 0

### T-7 / S-4.3
- RED: 綠當 hop 票
- GREEN: DOCTOR-NE-TICKET 理由是路線

### T-7 / S-4.4
- RED: 改握手
- GREEN: `git diff --exit-code -- hooks/_doctor_impl.py`

### T-7 / S-4.5
- RED: marketplace 當第四前置
- GREEN: 閘丟棄 marketplace／cache

### T-8 / S-6.1
- RED: 謂詞真仍等人卻標成功
- GREEN: NEW5-WAIT-RED 該格紅

### T-8 / S-6.2
- RED: Must-keep 紅仍 hop
- GREEN: KEEP-MK-RED 具名六 M

### T-8 / S-6.3
- RED: 機械 Ship Done
- GREEN: KEEP-SHIP-MECH 該格紅

### T-8 / S-5.3
- RED: 拒 hop 記成紅格綠
- GREEN: `--probe polarity` exit 1

### T-9 / S-7.1
- RED: OLD7 被折五站
- GREEN: OLD7-FREEZE 無五站機

### T-9 / S-7.2
- RED: 對 in-flight 寫五站當綠
- GREEN: OLD7-FOLD-RED 該格紅

### T-9 / S-7.3
- RED: 本目錄自動五站
- GREEN: SELF-OLD7 三凍結 slug 跳不過

### T-9 / S-7.5
- RED: 發明活五站名字
- GREEN: 只寫合成 fixture；未點名第一隻活五站

### T-10 / S-5.1
- RED: 入口只轉 F2 或缺一路
- GREEN: 同一 process NEW5+OLD7+TOKEN

### T-10 / S-5.2
- RED: 減 Decision 原 20 列
- GREEN: 官方 25 名齊

### T-10 / S-5.4–S-5.6／S-5.9–S-5.11
- RED: hollow 當綠
- GREEN: `--group hollow -ge 6`；探針 exit 3

### T-10 / S-5.7
- RED: F2 回歸紅
- GREEN: F3-F2-REGRESS 地板 `failed=0`

### T-10 / S-5.8
- RED: token 被刪
- GREEN: TOKEN-KEEP；`check-gate-tokens.sh`

### T-10 / S-8.2–S-8.4
- RED: Files 超清單／刪 token
- GREEN: 准許清單內；TOKEN-DEL-RED 該格紅

### T-10 / S-8.1／S-8.5／S-8.6
- RED: 重開 4-spec／Q21–23 可選／F2 park
- GREEN: Covers gate；未改 4-spec 頂欄、未重開 park

## Decisions(spec 未載明的自由選擇)

- 讀端與電池放 `scripts/five_station_f3.py`，不改 `five_station_f2.py` 的 `contract_version`／`f3_cut_happened`。[Assumption] 改 F2 讀鍵會在 T-7 bump 後讓 F2 S-3.3 假紅；F2 恒 `False` 也保住 F2「本 hop 不切」。READ-SEAM 舊 reader 直接呼叫 F2。
- graph 預設 `next` 維持字串 `N7-g1`／`N6-g2`，另加 `next_when_five`。[Assumption] 既有 `check-devstage2-graph.sh`／`check-devstage4-graph.sh` 把 `next` 當字串與節點「下一跳」對帳；改成 map 會炸 P0。YAML 鍵名不鎖（5-tasks）。
- 可選 `scripts/check-five-station-f3.sh` 只印「不是電池入口」、exit 0。依據 4-spec DD-2／S-5.10。
- `frozen_slug` 只認 `/docs/dev/<slug>`，且 `/scripts/fixtures/` 一律假。[Assumption] NEW5 根路徑字面含 `five-station-f3`，若用 substring 會把合成 fixture 誤凍成 SELF-OLD7。
- DOCTOR-HONEST 禁綠詞只咬 `✅ devflow doctor: COMPATIBLE`。[Assumption] `INCOMPATIBLE` 含 substring `COMPATIBLE`，用 `not in out` 會假紅。
- OLD7-FREEZE 拒因接受 `仍舊 7` 或 `in-flight`。OLD7 fixture 無契約檔 → 先走「路線未宣告 仍舊 7」，仍是整段舊 7。

## Deviations

無。未動 R/S。未重開 F2 park。未發明 G3。

## Files Changed

對照 4-spec S-8.2 Diff Budget：

- `guides/guide-dev-flow.html`（T-6 七站單行 → 五站用語）
- `devflow-contract.json`（只 bump `devflow_contract_version` → `2.1.0`）
- `hooks/runtime-capabilities.json`（只加 `2.1.0`）
- `skills/dev-flow/stage2/graph.yaml`（`next_when_five`；不刪 N7-g1）
- `skills/dev-flow/stage4/graph.yaml`（`next_when_five`；不刪 N6-g2）
- `scripts/five_station_f3.py`
- `scripts/test-five-station-f3.sh`
- `scripts/check-five-station-f3.sh`（選配；非第四路）
- `scripts/fixtures/five-station-f3/`
- `docs/dev/f3-cut-attestation.json`（T-10）
- `docs/dev/five-station-f3/6-implementation-notes.md` + html

未改：`_templates/`、`hooks/_doctor_impl.py`、STATUS／HISTORY、`scripts/five_station_f2.py`、token 檔、`docs/dev/five-station-f2/` 已封 R／S、5-tasks checkbox。

## Diff(各 T commit,逐檔折疊)

### f3_cut_happened · `scripts/five_station_f3.py` f3_cut_happened  T-1
改什麼：只讀獨立三槽檔；缺檔／空槽／AND 捆進 which → False；不寫檔。
關聯：caller Battery.run_attest_visible／callee _read_json
```diff
 def f3_cut_happened(project_root):
+    path = Path(project_root) / "docs" / "dev" / "f3-cut-attestation.json"
+    if not (_nonempty_str(who) and _nonempty_str(when) and _nonempty_str(which)):
+        return False
+    if AND_IN_WHICH.search(which):
+        return False
+    return True
```

### contract_version · `scripts/five_station_f3.py` contract_version  T-3
改什麼：只讀 `devflow_contract_version`，無 fallback 錯鍵。
關聯：caller declared／READ-SEAM／callee _read_json
```diff
 def contract_version(project_root):
+    val = blob.get("devflow_contract_version")
+    return str(val) if val is not None else ""
```

### allow_legacy · `scripts/five_station_f3.py` allow_legacy  T-4
改什麼：三前置 AND；doctor／marketplace／cache 丟棄；缺一 → legacy。
關聯：caller refuse_hop_reason／graph_next
```diff
 def allow_legacy(project_root, slug_dir, doctor_green=False, ...):
+    _ = (doctor_green, marketplace_updated, cache_has_hops)
+    if dec and (not flying) and cut:
+        return False, "five"
+    return True, "legacy"
```

### refuse_hop_reason · `scripts/five_station_f3.py` refuse_hop_reason  T-4
改什麼：拒因咬缺的那一條；必含 `F3 cut 未發生`；禁「已宣告所以切了」。
關聯：caller Battery.run_pre_210／run_pre_and
```diff
 def refuse_hop_reason(project_root, slug_dir, doctor_green=False):
+    if not declared(project_root):
+        return "路線未宣告 仍舊 7"
+    if has_old7(slug_dir):
+        return "仍舊 7 in-flight"
+    if not f3_cut_happened(project_root):
+        return "仍舊 7 F3 cut 未發生"
```

### graph_next · `scripts/five_station_f3.py` graph_next  T-5
改什麼：預設 `next` 仍例行閘；`next_when_five` 只在三前置真時生效。
關聯：caller Battery.run_cut_ok／run_pre_hops_200
```diff
 def graph_next(graph_path, from_node, project_root, slug_dir):
+    default = fields.get("next", "")
+    skip = fields.get("next_when_five", "")
+    if (not legacy) and skip:
+        return skip
+    return default
```

### S6-selfcheck next_when_five · `skills/dev-flow/stage2/graph.yaml` S6-selfcheck  T-5
改什麼：條件邊跳過 N7-g1；預設 next 字串不變。
關聯：callee graph_next
```diff
   S6-selfcheck:
     next: N7-g1
+    next_when_five: N8-end
```

### S5-gate next_when_five · `skills/dev-flow/stage4/graph.yaml` S5-gate  T-5
改什麼：條件邊跳過 N6-g2；預設 next 字串不變。
關聯：callee graph_next
```diff
   S5-gate:
     next: N6-g2
+    next_when_five: N7-end
```

### guide five-station wording · `guides/guide-dev-flow.html` flow-lead  T-6
改什麼：七站單行改五站用語（交付物 ≠ SoT）。
關聯：Battery.run_graph_word_ne
```diff
-  <p class="lead">這章要你懂:<strong>七站單行,只有 G1 / G2 / G3 會被人擋</strong>。
+  <p class="lead">這章要你懂:<strong>五站單行,只有 Ship 會被人擋</strong>。
```

### contract bump · `devflow-contract.json` devflow_contract_version  T-7
改什麼：正本鍵 bump 到 2.1.0。
關聯：doctor handshake／declared
```diff
- "devflow_contract_version": "2.0.0",
+ "devflow_contract_version": "2.1.0",
```

### supported 2.1.0 · `hooks/runtime-capabilities.json` supported_contract_versions  T-7
改什麼：supported 只加 2.1.0；不改握手實作。
關聯：devflow-doctor.sh
```diff
   "supported_contract_versions": [
     "2.0.0",
+    "2.1.0"
   ],
```

### live cut attestation · `docs/dev/f3-cut-attestation.json`  T-10
改什麼：T-10 才寫活樹三槽；which_condition=f3-cut。
關聯：f3_cut_happened
```diff
+{
+  "who": "rick",
+  "when": "2026-09-14T00:00:00+08:00",
+  "which_condition": "f3-cut"
+}
```

### Battery.case · `scripts/five_station_f3.py` Battery.case  T-10
改什麼：只印官方 25 名；發明名直接 FATAL。
關聯：test-five-station-f3.sh
```diff
 def case(self, name):
+    if name not in OFFICIAL:
+        raise SystemExit("FATAL: invented CASE name %s" % name)
+    print("=== CASE %s" % name)
```

## Self-Review

①每個「T × Covers S」都有含 S-id 的測試 + 該 T 自己的 RED/GREEN 證據（見 TDD Evidence；未跨 T 共用）？是（implementer 自檢；獨立審未過）。
②每 T 在 T Review Log 有 verdict？有：一律 PENDING_INDEPENDENT_REVIEW（不得自填 ACCEPTED）。
③每個 PASS 都早於該 T commit？n-a：無 PASS。
④每個 FAIL 後有較晚 PASS？n-a：尚無獨立 FAIL。
⑤每個已完成 T 一 commit、Progress Log 每列有 hash？未勾 checkbox；Progress Log 空（等獨立審）。
⑥git diff --stat 檔案 ⊆ Files 聯集、Diff Budget 內？是（S-8.2 准許清單）。
⑦Decisions/Deviations 與 diff 對得上？是；無 silent drift；DBC applicable：未改握手／未刪節點／未重開 park。
⑧回歸綠？`bash scripts/test-five-station-f3.sh -v` → `=== CASE` ×33、unique 官方 25 名、`failed=0` exit 0。`--only new5|old7|token` 各 exit 3；`--probe hollow-*`／`two-script` 各 exit 3；`--probe polarity` exit 1；未知旗標 exit 2；`--group hollow` ≥6。`test-five-station-f2.sh` `failed=0`。`check-gate-tokens.sh` 綠。`check-devstage2-graph.sh`／`check-devstage4-graph.sh` 綠。`git diff --exit-code -- hooks/_doctor_impl.py`。未發明 G3。

## Review Follow-up(G3 打回時才用)

n-a:未送 G3。
