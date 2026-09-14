---
feature: five-station-simplify
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: s7-fresh-reviewer
updated: 2026-09-14
---

# 7. 驗證 —— **不是 G3 PASS**（PRE-REVIEW；F1 only）

> ## Reviewer 閱讀動線(**必留;給看的人,不是給寫的人**)
>
> 以下五步固定,產文件時逐字保留、只換數字:
>
> | 步 | 讀哪節 | 這步問的唯一問題 |
> |---|---|---|
> | 1 | **Verdict** | 判定是什麼?門檻表每一格是不是都有證據? |
> | 2 | **Exit Checklist** | 還缺什麼才能出貨?哪幾項要 owner 親自動? |
> | 3 | **附錄:本輪特有** | 本輪的爭點/分歧在哪,誰對? |
> | 4 | **Known Limits** | 有沒有一條是 owner 不能接受的? |
> | 5 | **抽驗一列** | 本場 twin 第五格鎖 Coverage 中位列 **S-4.3**。打開 `scripts/test-five-station-f1.sh:209`（`test_s_4_3_miss_skips_demo_forced_accepted_fails`）、`scripts/five_station_f1.py:292-295`（`f1-trigger: miss` → `demo_page=False` + RP-12）、`scripts/fixtures/five-station-simplify/rp-12-miss-forced-accepted.md:1-6`。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。
>
> 用途:**G3 出貨關卡** 的交接包，**不是** Human G3 PASS。本檔 `verdict: PRE-REVIEW`。
> 建議 reviewer 路徑：適格人類 owner（rick）在審頁「提交判定」；說「過」／「g3 pass」才准改頂欄。Agent 禁代填 PASS。

## 限制聲明（讀取順序 + 身分）

| | |
|---|---|
| 審查者 | `s7-fresh-reviewer`（fresh-context Cloud Agent；**≠** Stage 6 實作 owner `implementer-A`／#321 實作 session） |
| Stage 6 實作 | `implementer-A`；T Review 原列 implementer-self PRE，#321 獨立授權後記帳 ACCEPTED。**不是** G3 |
| Human G3 | **尚未提交**。本檔不發明 PASS／REQUEST_CHANGES／HOLD |
| 讀取順序（可查） | ①`4-spec.md`（G2 PASS、52 S） ②`5-tasks.md`（T-1…T-12 F1 聯集） ③`scripts/test-five-station-f1.sh` + `scripts/five_station_f1.py` + fixtures／annex ④`git show ace0f9e`（#321 vs `f3f28bd`） ⑤親跑 `test-five-station-f1.sh`／spec-gate／file-map → **之後才** ⑥讀 `6-implementation-notes.md` Self-Review／D-1／D-2 |
| 圍欄 | 本雲端未武裝 `devflow-exec.sh review`（無 session runtime）。讀取順序靠散文紀律：矩陣與實跑先於 Self-Review |
| 本輪性質 | 產品碼已在 `main` tip `#321`=`ace0f9e` + `#322` STATUS companion。審核樹 Source SHA = `75a54b432d51f9cc705e7a10de5fc6e37b73380c`。本 PR **只** 7-review 雙檔。Scope = **F1 only**。不宣稱 F2／F3 完成。不改 STATUS。不 merge |
| 可信／打折 | 機械數字（63 CASE／failed=0／spec-gate 9/9／file-map 208）可信。F-id 分級與「沒想到的事」是本 reviewer 獨立掃，不是作者自評升級。Human 仍可整份退回 |

## Coverage Matrix

自建（grep `test_s_`／`==== CASE` ↔ 5-tasks F1-owned S；**未先讀** Self-Review）。本表只列 **F1 必須落地的 S** + 回歸末列。F2／F3 S 見附錄 A2，不標 ✅。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `test_s_1_1_aliases_keep_seven_filenames` + `test_s_1_1_tokens_remain`；`scripts/test-five-station-f1.sh:267-274`；`five_station_f1.py:345-362` live_close | ✅ |
| S-1.7 | `test_s_1_7_a5_miss_builds_no_page`；`:217-218`；fixture `rp-12-miss-forced-accepted.md`；`demo_page=False` | ✅ |
| S-1.10 | `test_s_1_10_b4_quiz_only_irreversible` + `test_s_1_10_reversible_forced_quiz_fails`；`:222-225`；RP-7／S-1.10 | ✅ |
| S-2.1 | `test_s_2_1_missing_must_keep_is_brief_violation`；`:194-195`；`brief-missing-must-keep.md` | ✅ |
| S-2.2 | `test_s_2_2_t_fake_missing_cols` + `test_s_2_2_t_fake_red_on_card`；`:168-171`；RP-1 | ✅ |
| S-2.3 | `test_s_2_3_no_red_or_self_review_incomplete` + `test_s_2_3_self_review_incomplete`；`:175-178`；RP-2 | ✅ |
| S-2.4 | `test_s_2_4_vague_or_untestable_s_fails` + `test_s_2_4_untestable_error_fails`；`:184-188`；RP-3；`c4_fail=True` | ✅ |
| S-2.5 | `test_s_2_5_test_name_requires_s_id`；`:189-190`；RP-4 `test_store_half_slot` | ✅ |
| S-2.6 | `test_s_2_6_rp_min_set_rp_1`…`rp_16` + `test_s_2_6_rp_min_set_add_only`；`:231-255`；刪 RP-8 紅 | ✅ |
| S-2.7 | `test_s_2_7_optional_fields_block_this_g2`；`:196-197`；`brief-optional-four-fields.md` | ✅ |
| S-2.8 | `test_s_2_8_files_not_subset_red`；`:198-199`；RP-5 `graph.yaml`／`_stage3_impl.py` | ✅ |
| S-2.9 | `test_s_2_9_no_raw_output_red`；`:179-180`；RP-6 | ✅ |
| S-3.1 | `test_s_3_1_agent_written_verdict_unread` 等 5 CASE；`:117-130`；RP-16；人類頂欄不誤殺 | ✅ |
| S-3.2 | `test_s_3_2_ship_done_without_human_pass_fails`；`:226-227`；RP-8 | ✅ |
| S-3.3 | `test_s_3_3_ship_evidence_eight_points`；`:228-229`；`s-3-3-evidence-omit-eight.md` | ✅ |
| S-4.1 | `test_s_4_1_b1_requires_human_accepted_attestation`；`:203-205`；`hop_spec_build=True` | ✅ |
| S-4.2 | `test_s_4_2_empty_attestation_plus_chat_cannot_leave_spec`；`:206-208`；RP-13；`leave_spec=False` | ✅ |
| S-4.3 | `test_s_4_3_miss_skips_demo_forced_accepted_fails`；`:209-211`；RP-12；`demo_page=False`（本場抽驗列） | ✅ |
| S-4.4 | `test_s_4_4_ask_human_when_latch_false_fails`；`:212-213`；RP-14 | ✅ |
| S-4.5 | `test_s_4_5_negated_skip_is_not_skip_oc`；`:214-216`；S-4.5；`skip_oc=False` | ✅ |
| S-5.1 | `test_s_5_1_inflight_md_stays_old_7`；`:158-159`；RP-15；`in_flight=True` | ✅ |
| S-5.2 | `test_s_5_2_this_slug_five_station_hop_blocked`；`:162-164`；RP-15；`hop_blocked=True` | ✅ |
| S-5.3 | `test_s_5_3_html_only_not_inflight`；`:160-161`；`in_flight=False` | ✅ |
| S-5.4 | `test_s_5_4_old_seven_missing_new_fields_not_red`；`:143-144`；`missing_new5_legal=True` | ✅ |
| S-5.5 | `test_s_5_5_doctor_green_is_not_cut`；`:147-148`；S-5.5 | ✅ |
| S-5.6 | `test_s_5_6_doctor_green_follow_hops_text_fails`；`:145-146`；S-5.6 | ✅ |
| S-5.7 | `test_s_5_7_unupgraded_adopter_stays_old_7`；`:149-151`；S-5.7；`route=old-7` | ✅ |
| S-5.8 | `test_s_5_8_annex_nine_slot_semantics` + `test_s_5_8_missing_slot_red`；`:135-139`；九 SLOT 綠／缺槽紅 | ✅ |
| S-5.9 | `test_s_5_9_contract_vs_marketplace_hops_concurrency`；`:152-154`；`dual-hops-first-then-contract.md`；可觀測碼 S-5.7＋`route=old-7` | ✅ |
| S-6.2 | `test_s_6_2_q6_stays_assumption`；`:277-279`；`q6_open=True` | ✅ |
| S-6.3 | `test_s_6_3_q6_as_fact_blocks_g2`；`:280`；`q6-as-fact.md` | ✅ |
| S-8.1 | live_close + annex 兩檔在；`notes/design/five-station-simplify-f1-dual-read-annex.md`／`f1-rp-min-set.md`；零 `graph.yaml` 切線 | ✅ |
| S-8.5 | `test_s_8_5_this_slug_stage_5_to_7_is_f1_only`；`:275-276`；`files_closed=True` | ✅ |
| S-8.6 | `test_s_8_6_reopen_1b`…`7c` 五張；`:258-266`；`reopen-*.md` | ✅ |
| 既有測試套件(回歸) | `bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md`；`bash scripts/check-file-map.sh` | ✅ |

**回歸末行（reviewer @ `75a54b4`）**：spec-gate `9/9` exit 0（52 S）；file-map `scanned=208` exit 0。F1 牙 `failed=0`、`=== CASE` = 63。

## Verification Evidence

<!-- Final Fresh 在 ALREADY_SYNCED 之後重綁當下 main tip（步 2c 路徑①）。
     產品碼樹 = origin/main after #321/#322。本 PR 後續只加本雙檔，不改牙。 -->

- Source SHA: 75a54b432d51f9cc705e7a10de5fc6e37b73380c
- Final Fresh Run ID: f1-s7-fresh-75a54b4-20260914
- Entry point: `bash scripts/test-five-station-f1.sh`（F1 Conditional：牙列入 Required）然後 `bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md`
- Toolchain: system bash + python3 + repo scripts（無新套件）

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate（本 hop 形狀）。文件層：本 PR 檔集（S-8.4） | `bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md` | pass | exit 0; 9/9; 52 S | |
| Disposition C9 | `bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md` | pass | C9 ✅; 52 S 去向形狀 | |
| Assumption 用詞（S-6.2） | `bash scripts/check-five-station-f1.sh --live` | pass | q6_open=True; S-6.3 not in red_codes; exit 0 | |
| test-five-station-f1 | `bash scripts/test-five-station-f1.sh` | pass | failed=0; CASE=63; exit 0 | |
| F1 落地 → 該刀牙列入 Required 並重跑對照稿 | `bash scripts/test-five-station-f1.sh -v` | pass | 12 group 全綠; CASE=63; failed=0 | |
| file-map regression | `bash scripts/check-file-map.sh` | pass | exit 0; scanned=208; table_rows=218 | |
| Mutation（本 hop 只規格） | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| e2e／Playwright（無產品前端） | | n-a | | Explicitly excluded；F1 無產品 UI |
| Race／stress（無多 writer runtime） | | n-a | | Explicitly excluded |
| Windows 真機 | | n-a | | Explicitly excluded |
| 本 hop 跑 coordinator（F2 Out of Scope） | | n-a | | F2 未做；本場不跑 coordinator |

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得刪 G1／G2／`ACCEPTED`（S-1.1、1B） | `test_s_1_1_tokens_remain`；live `token_G1/G2/ACCEPTED=True` | pass |
| 不得把假完成 T 當簡化成功（S-2.1、S-2.2） | `--group brief-files` + `--group rp1` | pass |
| 不得把四欄／seam／Must-keep 標可選（S-2.7） | `test_s_2_7_optional_fields_block_this_g2` | pass |
| 不得讓 Agent 代寫判定算已寫（S-3.1） | `--group rp16`；Agent `unread=True` | pass |
| 不得讓空 attestation + chat 離 Spec（S-4.2） | `test_s_4_2_*`；`leave_spec=False` | pass |
| 不得把本 slug 折成五站（S-5.2、4C） | `test_s_5_2_*`；`hop_blocked=True` | pass |
| 不得把 doctor 綠說成已切五站（S-5.5、S-5.6） | `--group dual-read` | pass |
| 不得把 Q6 升成已核事實（S-6.3） | `test_s_6_3_*` | pass |
| 不得暗改 cap 或套到舊 7（S-7.1、S-7.4） | F1 只對照稿紅 RP-9／10／11；計數器未落地見 KL #2 | n-a |
| 不得在本 slug Stage 5–7 做 F2／F3（S-8.5） | `files_closed=True`；diff 零 coordinator／graph 切線 | pass |
| 不得重開 1B／2B／4C／6B／7C（S-8.6） | `--group f1-close` 五張 reopen | pass |
| 不得本 hop 改 STATUS／模板／graph／既有牙／契約 bump | #321 diff 無 `_templates/`／`graph.yaml`／`devflow-contract.json`；本 PR 不改 STATUS | pass |
| 不得鎖 annex 欄位鍵名或 event schema（S-5.8、OC-3） | annex 只 SLOT- id／RP 語意；牙讀正文不讀 JSON schema | pass |
| 不得把 Q6 標 oc-accepted 或 DD 草擬自判（S-6.2） | `q6_open=True`；4-spec Assumption refs status=open | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

（#321 為 Cloud Agent 手動／非 dev-run ledger。本節留白，不虛構模型歷史。）

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

> **s7-fresh-reviewer 2026-09-14 親跑** `bash scripts/test-five-station-f1.sh -v`（不採信 6-notes 貼文）。長輸出見附錄 A4。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | ls／token 掃描；七舊名在、新家族不在、token 仍在 | live: `seven_old_count=6`（尚無本 7-review.md 時）、`new_family=False`、`token_G1/G2/ACCEPTED=True` | ✅ |
| S-1.7 | 未命中不建頁 | CASE `test_s_1_7_*`；`demo_page=False`；RP-12 同 fixture | ✅ |
| S-1.10 | 不可逆無 Quiz 紅；可逆強制 Quiz 紅 | CASE 兩張；RP-7／S-1.10 | ✅ |
| S-2.1 | 少 Must-keep 點名違 brief | `RED S-2.1 少 Must-keep 違 brief` | ✅ |
| S-2.2 | T 卡上就紅 | `RED RP-1` 缺欄／Verify 無鑑別力 | ✅ |
| S-2.3 | 無 RED 或 reviewer=implementer → 未完成 | `RED RP-2` 兩張 | ✅ |
| S-2.4 | 未定事項三詞／不可測紅 | `RED RP-3`；`c4_fail=True` | ✅ |
| S-2.5 | 測試名無 S-id 紅 | `RED RP-4 測試名無 S-id: test_store_half_slot` | ✅ |
| S-2.6 | RP-1…16 各紅一次；刪列紅 | 16+1 CASE；`annex 少 RP: RP-8` | ✅ |
| S-2.7 | 可選四欄擋 G2 | `RED S-2.7 可選句擋 G2` | ✅ |
| S-2.8 | Files 超出聯集紅 | `RED RP-5` `hooks/_stage3_impl.py`／`graph.yaml` | ✅ |
| S-2.9 | 無原始輸出紅 | `RED RP-6 只有摘要無原始輸出` | ✅ |
| S-3.1 | Agent 寫入 = 未寫；人親寫不誤殺 | 3 Agent `unread=True`；2 human `unread=False` | ✅ |
| S-3.2 | 無人 PASS 卻 Done 紅 | `RED RP-8` | ✅ |
| S-3.3 | Evidence 八點不齊或摺站省略紅 | `RED S-3.3` | ✅ |
| S-4.1 | 人 ACCEPTED+attestation 才 hop Spec→Build | `hop_spec_build=True`；red=False | ✅ |
| S-4.2 | 欄空+chat 不得離 Spec | `leave_spec=False`；RP-13 | ✅ |
| S-4.3 | 未命中不產 Demo；強迫 ACCEPTED 紅 | `demo_page=False`；RP-12 | ✅ |
| S-4.4 | latch=否卻請人審紅 | `RED RP-14` | ✅ |
| S-4.5 | 否定跳過 ≠ skip OC | `skip_oc=False`；`RED S-4.5`（牙收；`_stage3_impl.py` 未改＝KL） | ✅ |
| S-5.1 | 有 md → 凍舊 7 | `in_flight=True`；RP-15 | ✅ |
| S-5.2 | 本資料夾五站 hop 跳不過 | `hop_blocked=True` | ✅ |
| S-5.3 | 僅 html ≠ in-flight | `in_flight=False` | ✅ |
| S-5.4 | 舊七缺新五欄不紅 | `missing_new5_legal=True`；red=False | ✅ |
| S-5.5 | doctor 綠 ≠ 已切 | `RED S-5.5 doctor 綠 ≠ 已切` | ✅ |
| S-5.6 | 「跟 hops 走」文案紅 | `RED S-5.6 doctor 綠不得跟 hops` | ✅ |
| S-5.7 | 2.0.0+五站 hops → 仍舊 7 | `route=old-7`；`doctor_not_arbiter=True` | ✅ |
| S-5.8 | 九 SLOT 可指到；少一槽紅 | 完整 annex `slots_ok=True`；缺 `SLOT-DOCTOR-GREEN-MEANS` 紅 | ✅ |
| S-5.9 | 兩源任一順序仍舊 7 | hops-first fixture；`route=old-7`；可觀測碼 S-5.7 | ✅ |
| S-6.2 | Q6 仍 Assumption／open | `q6_open=True` | ✅ |
| S-6.3 | Q6 寫成已核事實擋 G2 | `RED S-6.3 Q6 升格擋 G2` | ✅ |
| S-8.1 | teeth+annex；不准切預設路線 | annex 兩檔在；`new_family=False`；無 graph 切線 | ✅ |
| S-8.5 | Stage 5–7 只 F1 | `files_closed=True` | ✅ |
| S-8.6 | 重開已拒案紅 | 1B／2B／4C／6B／7C 五張 `RED S-8.6` | ✅ |

## 截圖槽

本場無產品 UI（F1 = CLI 牙 + fixture 自檢）。目錄無 `shots/`。不准新增、不准發明編輯 URL。缺檔不寫「未掛」。

### 進場
- data-shot: n-a
- src: n-a
- caption: 無畫面；現象 = tooth selftest CASE
- 進場:本場無可從列表打開的既有 UI 紀錄。不准新增。
- hang-point: n-a

## Operational Walkthrough

F1 牙是檢查器，不是現場交接 UI。有 Operational Context 的 S 以「寫手／coordinator 被牙擋住」走一遍；標不適用的純內部 S 不裝成人員旅程。

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | — | — | — | — | — | 不適用（檔名對照） |
| S-1.7 | 母版 owner | 未命中不第二次等人 | 牙讀 miss trigger fixture → 不建頁 | 不補假 Demo | 無第二次人停 | 相符：`demo_page=False` |
| S-1.10 | owner／寫手 | 不可逆才 Quiz | 牙咬無 Quiz／可逆強制 Quiz | 人出 Quiz 只在不可逆 | 可逆強制 = 第三例行停 | 兩張對照紅 |
| S-2.1 | 寫手 | 簡化仍帶 Must-keep | 牙點名違 brief | 補 M 去向 | 停修該句 | `RED S-2.1` |
| S-2.2 | 寫手 | T 卡當下見紅 | 缺欄／假 Verify → RP-1 | 補四欄 | 勾選 ≠ 完成 | 卡上紅 |
| S-2.3 | T reviewer | 禁自審假完成 | reviewer=implementer 或無 RED → RP-2 | 換獨立 reviewer | 該 T 未完成 | 兩張紅 |
| S-2.4 | 寫手 | 禁模糊 S | C4／不可測 → RP-3 | 改可斷言輸出 | 該 S 不得當綠燈 | 紅 |
| S-2.5 | 寫手 | 測試名含 S-id | `test_store_half_slot` → RP-4 | 改名 | — | 紅 |
| S-2.6 | annex 維護 | RP 只准加 | 刪 RP-8 → S-2.6 | 加回該列 | — | 紅 |
| S-2.7 | 後站寫手 | 禁把四欄標可選 | 可選句 → 擋 G2 | 刪可選句 | 本 slug G2 | 紅 |
| S-2.8 | 寫手 | Files ⊆ 聯集 | 寫 graph／_stage3 → RP-5 | 移出 Files | — | 紅 |
| S-2.9 | 寫手 | 完成必附原始輸出 | 只摘要 → RP-6 | 補 `檔:行` | — | 紅 |
| S-3.1 | owner | Ship 唯人 | Agent 頂欄 PASS = 未寫 | 人親寫頂欄 | 機器判定無效 | unread=True／人案不殺 |
| S-3.2 | owner | 無人 PASS 不得 Done | 標 Done 無 PASS → RP-8 | 留 HumanWait | Ship 等人 | 紅 |
| S-3.3 | reviewer | Evidence 八點 | 省略八點或「已五站」→ S-3.3 | 補八點 | 不得摺站省略 | 紅 |
| S-4.1 | owner | B1 命中才 ACCEPTED+attest | 人案 hop_spec_build=True | 人簽 attestation | 空欄不得離 Spec | 綠放行 |
| S-4.2 | owner | chat 不是判定 | 空欄+「可以開 Stage 4」→ RP-13 | 補 attestation 或留下 | 不得離 Spec | leave_spec=False |
| S-4.3 | owner | 未命中不產 Demo | 強迫 ACCEPTED → RP-12 | 不補假 Demo | — | demo_page=False |
| S-4.4 | coordinator | latch=否不問人 | 「請人審」→ RP-14 | 刪問人句 | — | 紅 |
| S-4.5 | G2 機械 | 否定跳過 ≠ skip OC | 牙 `skip_oc=False` | 不把「不得跳過」當已跳 | 舊 `_stage3_impl.py` 仍可能誤讀＝KL | 牙紅；舊牙未改 |
| S-5.1 | 採用端／本 repo | in-flight 舊 7 | 有 md → RP-15 | 不寫五站狀態 | — | in_flight=True |
| S-5.2 | 本 slug owner | 本資料夾跳不過 | 五站 hop → hop_blocked | 繼續舊 7 | — | 紅 |
| S-5.3 | F3 後新人 | 僅 html 不凍 | `in_flight=False` | F3 才開機 | — | 布林對；不切路線 |
| S-5.4 | 採用端 | 舊檔缺欄不紅 | missing_new5_legal | 不升級契約 | — | 不紅 |
| S-5.5 | 採用端 | doctor 綠 ≠ 已切 | 文案「已切」紅 | 不跟 hops | — | 紅 |
| S-5.6 | 採用端 | 禁「跟 hops 走」 | S-5.6 紅 | — | — | 紅 |
| S-5.7 | 未 upgrade 端 | 仍舊 7 | 2.0.0+五站 hops → route=old-7 | 不改線 | 兩源順序無關 | 紅且仍舊 7 |
| S-5.8 | annex 維護 | 九 SLOT 齊 | 缺槽紅 | 補 SLOT- id 句 | 不鎖鍵名 | 齊綠／缺紅 |
| S-5.9 | 採用端 | 兩源並改仍舊 7 | hops-first fixture | — | Concurrency applicable | route=old-7 |
| S-6.2 | 本 slug 寫手 | Q6 保持 open | live q6_open | 不抽公司逐字稿 | deadline 2026-10-31 | open |
| S-6.3 | 本 slug 寫手 | 升格擋 G2 | q6-as-fact 紅 | 改回 Assumption | — | 紅 |
| S-8.1 | F1 交付 | teeth+annex；不切線 | 兩 annex + 三 scripts | 不改 graph | — | 在 |
| S-8.5 | 本 slug 後站 | 只 F1 | Files 閉聯集 | 禁 coordinator | — | files_closed |
| S-8.6 | 寫手 | 已拒案不重開 | 「改採 1B…」紅 | 刪該句 | — | 五張紅 |

## Design Integrity Check(Design Boundary Contract 為 `applicable` 時逐項過;`n-a` 時記 n-a)

DBC = applicable（4-spec）。命中項併入雙軸；本清單不另立 Gate。

1. **依賴反向被間接繞過**:未命中。F1 讀 doctor／spec-gate 當證據，Files 聯集不含 `hooks/_doctor_impl.py`／`_stage3_impl.py`，#321 未改握手語義。
2. **資料所有權被繞過寫入**:未命中。牙不寫採用端路線、不寫本 slug 五站狀態（RP-15 紅）。
3. **相容性破壞包成新增**:未命中。契約仍 2.0.0；無新公開 doctor API。
4. **一致性邊界被拆解**:n-a（F1 無 transaction；cap 計數落點 F2）。
5. **宣告的 Test seam 未被使用**:未命中。seam = `check_path`／fixture／`=== CASE`；selftest 走同一 `evaluate`。
6. **Known design limit 被實作悄悄「解決」**:未命中。`_stage3_impl.py` 未改；S-4.5 由 SLOT-SKIP-NEGATION 另收，契約 Known limit 仍在。D-2 是超行數，不是把限制「修掉」。

## Standards Axis

獨立掃（未先採信 Self-Review）。無 🔴。無未授權 Boundary 變更。

- F-s7-1 🟡 `scripts/five_station_f1.py` 420 行 | 超過 4-spec Diff Budget「scripts 新牙非測試 ≤250」 | 作者已記 **D-2(L1)**：不拆第二家族（會撞 ≤4 檔）。不改 R/S。建議 Human 接受或 park（見 Known Limits #1）。本 reviewer 實測 420（作者寫 ≈407）——同一 L1，不升 L2
- F-s7-2 🟢 `five_station_f1.py:106-114` `infer_kind` 檔名前綴／`f1-kind` | 牙靠 fixture 命名分派，不是 live coordinator 事件流 | 誠實 F1 範圍；F2 不得把此前綴當狀態機
- F-s7-3 🟢 `five_station_f1.py:327-333` RP-9／10／11 | 對照稿字面紅，無 live 計數器 | 4-spec DD-3／S-7.4；不鎖 event 鍵。F2 工作
- F-s7-4 🟢 `five_station_f1.py:193-200` RP-16 | `f1-writer`／正文「寫入者是 Agent」辨識，不是 Cursor 擋寫 | S-3.1 觀測是對照稿紅；人親寫頂欄不誤殺已驗
- F-s7-5 🟢 `test-five-station-f1.sh:152-154` S-5.9 | CASE 名 S-5.9，可觀測紅碼是 S-5.7＋`route=old-7` | 與 S-5.9「任一寫入順序仍舊 7」同一訊號；不另開 🔴
- Design Boundary（Dependency Direction／Leakage／Ownership／Interface Stability）:無未授權變更。D-1 CI 地板（file-map 205→208、devflow-check 註冊兩牙）= owner 授權 L1 收口，不進 5-tasks Files 聯集

## Spec Axis

逐 R。F2／F3 條標「本場不宣稱符合」。Deviations：D-1／D-2 如實，無隱藏 L2。

| R | 判定 | 證據 |
|---|---|---|
| R-1 | **部分符合（F1 子集）** | S-1.1／S-1.7／S-1.10 ✅。S-1.2…S-1.6／S-1.8／S-1.9／S-1.11／S-1.12 = F2 coordinator，本場不宣稱 |
| R-2 | 符合（F1） | S-2.1…S-2.9 全綠；RP-1…16 最小集可紅 |
| R-3 | 符合（F1） | S-3.1／S-3.2／S-3.3 CASE 綠 |
| R-4 | 符合（F1） | S-4.1…S-4.5 CASE 綠 |
| R-5 | 符合（F1） | S-5.1…S-5.9 CASE 綠；annex 九 SLOT |
| R-6 | 符合（本場責任） | S-6.1 已在 G2 spec-gate C9；S-6.2／S-6.3 F1 綠；Q6 仍 open |
| R-7 | **未做（F2）** | 只對照稿紅 RP-9／10／11。計數落點／event 未選。不得當 coordinator 已交付 |
| R-8 | **部分符合** | S-8.1／S-8.5／S-8.6 ✅。S-8.2 = F2；S-8.3 = F3；S-8.4 已 G2（Stage 4 PR）。S-8.7 = 本 hop 用 builder 產 7-review.html（不是 F1 牙） |
| D-1(L1) | 如實；已收口 | file-map 208；devflow-check 註冊兩牙；聯集仍六條 |
| D-2(L1) | 如實；未收口 | 420 > 250；不拆家族。見 F-s7-1／KL #1 |
| Design Boundary | 符合契約 | 無未授權 Boundary；未偷偷修掉 Known design limit |

## 變更架構圖

必須對上 #321 basename（本 PR 只加 `7-review.md`／`7-review.html`）。

```text
[check-five-station-f1.sh] ----exec----> [five_station_f1.py]
[test-five-station-f1.sh]  --import-->        |
                                              +-- evaluate(path)
                                              |     fixtures/five-station-simplify/*.md
                                              |     kind: verdict/slots/dual/inflight/...
                                              +-- live_close(root)
                                                    docs/dev/five-station-simplify/*.md
[notes/design/five-station-simplify-f1-dual-read-annex.md]  9 SLOT
[notes/design/five-station-simplify-f1-rp-min-set.md]       RP-1..16
D-1 floor (not Files union):
  check-file-map.sh  EXPECTED=208
  devflow-check.sh   architecture 註冊兩牙
  test-architecture-guards.sh  靜態釘
  guide-dev-flow.html          filemap 列
NOT in this knife:
  graph.yaml / _templates/1-4 / coordinator / doctor handshake
```

## Diff(merge-base(main)..HEAD,逐檔折疊)

審核的產品碼 = `f3f28bd..ace0f9e`（#321）。#322 只 STATUS（本場不改 STATUS）。本 Stage 7 PR 只新增本雙檔。共同戰場已是送審樹本身（見 2c）。

<details>
<summary title="+420/-0; evaluate + live_close"><code>scripts/five_station_f1.py</code> (+420/-0)</summary>
<pre><span class="add">+SLOTS = (SLOT-PARSE-OLD7 … SLOT-SKIP-NEGATION)</span>
<span class="add">+RPS = RP-1 … RP-16</span>
<span class="add">+F1_UNION = 六條 Files</span>
<span class="add">+def evaluate(...)  # kind 分派咬 RP／S</span>
<span class="add">+def live_close(...)  # 七檔名／token／Files 閉／Q6</span></pre>
</details>

<details>
<summary title="+9/-0; 入口"><code>scripts/check-five-station-f1.sh</code> (+9/-0)</summary>
<pre><span class="add">+exec python3 five_station_f1.py --root "$ROOT" "$@"</span></pre>
</details>

<details>
<summary title="+284/-0; 63 CASE"><code>scripts/test-five-station-f1.sh</code> (+284/-0)</summary>
<pre><span class="add">+# groups: rp16 slots dual-read inflight rp1 seam spec-name</span>
<span class="add">+#         brief-files attest ship-quiz rp-min-set f1-close</span>
<span class="add">+# print === CASE; failed=%d; exit 1 if failures</span></pre>
</details>

<details>
<summary title="+40/-0; 九 SLOT"><code>notes/design/five-station-simplify-f1-dual-read-annex.md</code> (+40/-0)</summary>
<pre><span class="add">+SLOT-PARSE-OLD7 … SLOT-SKIP-NEGATION（語意槽，不鎖鍵名）</span></pre>
</details>

<details>
<summary title="+23/-0; RP 最小集"><code>notes/design/five-station-simplify-f1-rp-min-set.md</code> (+23/-0)</summary>
<pre><span class="add">+| RP-1 … RP-16 | 紅什麼 | 人見面 |</span></pre>
</details>

<details>
<summary title="fixtures 目錄"><code>scripts/fixtures/five-station-simplify/*</code> （約 40 檔）</summary>
<pre>對照稿：rp-01…16、dual-*、inflight-*、reopen-*、brief-*、slots-missing-one、q6-as-fact、s-3-3、s-4-1、skip-negation。完整 diff 在 #321。</pre>
</details>

<details>
<summary title="D-1 CI 地板"><code>scripts/check-file-map.sh</code> · <code>scripts/devflow-check.sh</code> · <code>scripts/test-architecture-guards.sh</code> · <code>guides/guide-dev-flow.html</code></summary>
<pre><span class="del">-EXPECTED_MAPPED_FILES = 205</span>
<span class="add">+EXPECTED_MAPPED_FILES = 208</span>
<span class="add">+architecture 組註冊 check-five-station-f1.sh / test-five-station-f1.sh</span></pre>
</details>

<details>
<summary title="過程檔"><code>docs/dev/five-station-simplify/6-implementation-notes.md</code> · html twin · 5-tasks frontmatter</summary>
<pre>6-notes + twin；5-tasks 小幅同步。#322 STATUS 不在本 PR。</pre>
</details>

## Verdict

**PRE-REVIEW** —— **不是 G3 PASS。** 本 reviewer 建議：F1 牙機械面可交人審；Human 說「過」／「g3 pass」之前頂欄維持 PRE-REVIEW。不發明 Human 判定。

| 門檻 | 證據 | 簽署 |
|---|---|---|
| 本次 F1 S 全綠 | Coverage 34 列 ✅；63 CASE failed=0 | reviewer 實跑；**待 Human G3** |
| 既有回歸綠 | spec-gate 9/9；file-map 208 | reviewer 實跑；**待 Human G3** |
| 現象證據逐 F1 S | 上表＋附錄 A4 | reviewer 親跑 selftest；**待 Human G3** |
| Evidence 契約 | 本節四欄＋層表；gauntlet 見附錄 A5 | 機械面交給本檔；**待 Human G3** |
| 無 🔴 | 無產品行為 🔴；F-s7-1 🟡 = D-2 行數 L1 | **待 Human 接受／park D-2** |
| F2／F3 | 明確未做 | 不得當五站已切 |

### 步 2c 整合回歸（Final Fresh 之前）

Stage 6 `FORK_INTEGRATION_SHA=f3f28bdb183c3d0e1ccbecd7e6cde261e7679c62`。本工作樹開工 = 已合入的 `origin/main`。

```
STATUS: ALREADY_SYNCED
FORK_INTEGRATION_SHA: f3f28bdb183c3d0e1ccbecd7e6cde261e7679c62
FEATURE_HEAD: 75a54b432d51f9cc705e7a10de5fc6e37b73380c
INTEGRATION_SHA: 75a54b432d51f9cc705e7a10de5fc6e37b73380c
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=ALREADY_SYNCED FORK=f3f28bdb183c3d0e1ccbecd7e6cde261e7679c62 HEAD=75a54b432d51f9cc705e7a10de5fc6e37b73380c INTEGRATION=75a54b432d51f9cc705e7a10de5fc6e37b73380c(refs/remotes/origin/main)—— 你已經同步過了,本次輸出不算數
```

路徑①：**重綁 Final Fresh** 到當下 HEAD = `75a54b4`（本檔 Source SHA）。共同戰場 = #321／#322 本身，已當審核對象逐檔看過，不得用此次腳本輸出當「沒有共同戰場」。**不 merge**（產品碼已在 main；本 PR 只文件）。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | D-2(L1)：`five_station_f1.py` 420 行 > Diff Budget 非測試 ≤250。作者不拆第二家族（會撞 ≤4 檔格）。不改 R/S | L1／🟡 | **park 待 Human 接受**。落點=本表。owner=rick。不在本 PR 拆檔 |
| 2 | F2 coordinator／event／三 cap 計數器未落地（R-7、S-1.2…中間 latch、S-7.1…S-7.4）。F1 只對照稿讓 RP-9／10／11 各紅一次 | 範圍 | 另刀 F2。本場不宣稱完成 |
| 3 | F3 新 slug 預設五站未切（S-8.3）。`graph.yaml` 未改 | 範圍 | 另刀 F3 |
| 4 | `_stage3_impl.py` 仍可能把否定跳過讀成 skip OC（4-spec Known design limit）。F1 只另收 SLOT-SKIP-NEGATION | 🟢／已知 | 維持；不在本場改舊牙 |
| 5 | Q6 採用現場 chat 蓋章仍 Assumption／open（deadline 2026-10-31）。無採用逐字稿 | 已知 | 升格句已由 S-6.3 擋；抽案仍欠 |
| 6 | A1／A2 dest 未核；annex 鍵名未鎖（OC-3） | 已知 | F1 刻意不鎖；勿當 schema 已定 |
| 7 | RP-16／多數 RP 是 fixture 牙，不是 Cursor 擋寫或 live hop 引擎 | 誠實 | F2 才接 coordinator |
| 8 | 步 2c `ALREADY_SYNCED`（F1 已合 main）。交集輸出不作「無共同戰場」證據 | 流程 | 已走路徑① 重綁 Fresh |
| 9 | 本檔 `verdict: PRE-REVIEW`。全勾 ≠ PASS。Human 未簽 | 流程 | 建議路徑：owner 開審頁提交判定 |

## Exit Checklist(全勾才算 shipped)

- [x] **Design Boundary finding 全數處置**:無未授權 Boundary 變更（DIC 六項未命中；D-2 是行數 L1 不是 Boundary）。DBC applicable 下無 🟡 Boundary 待處置
- [ ] Quiz（不可逆改動必做；其餘 full lane 選配）:F1 不 bump 契約、不切 `graph.yaml` 預設。Quiz 留給 Human 若認為本刀仍算不可逆；本 reviewer **不代考、不代答**
- [x] (條件式)整合回歸已在 Final Fresh **之前**記錄:ALREADY_SYNCED 三 SHA＋canonical ref 貼於 Verdict；Fresh 重綁 `75a54b4`。Verdict 後禁改產品碼
- [ ] PR → main:本 hop 開 Stage 7 PR；**禁直上 master；未 merge**
- [x] 4-spec delta 已併入 `docs/specs/<domain>.md`: n-a（F1 不改 living 契約句；F3 才動）
- [ ] STATUS.md 已更新為 shipped:**merge 後由 merger 在 main 做**。本 branch **不改 STATUS**
- [ ] 7-review frontmatter status: shipped:維持 `draft`；`verdict: PRE-REVIEW` 直到 Human
- [x] 7-review.html 已產生:先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py /workspace five-station-simplify 7-review`（twin 覆寫同檔；抽驗格 S-4.3）
- [ ] feature branch 已刪 / worktree 已清:merge 後再做

回看約定
| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| F2 開工前 | rick | 本檔 Coverage／KL #2；`test-five-station-f1.sh` 仍 failed=0 | F1 CASE 變紅或有人把本 slug 當新 5 |
| 2026-10-31 | rick | Q6 Assumption；採用現場抽案 | 仍零抽案且有人把 Q6 寫成 Observed |

## 附錄:本輪特有

### A1　本輪爭點

1. **G3 主權**：機械全綠 ≠ Human PASS。本檔停 PRE-REVIEW。
2. **D-2 行數**：420 vs 250。L1 已記；Human 要不要接受。
3. **Scope**：只 F1。把 R-1 中間 latch 或 R-7 cap 當成已交付 = 錯。
4. **2c ALREADY_SYNCED**：F1 已在 main。不重 merge。Fresh 綁 `75a54b4`。
5. **作者 vs 本場**：Self-Review 主張 F1 牙群組全綠＋未發明 G3 —— 與本場實跑一致。作者 T 列原為 implementer-self PRE；#321 獨立授權 ACCEPTED。本場不把那份授權升級成 G3。

### A2　本場不宣稱的 S（F2／F3／已綠他站）

S-1.2、S-1.3、S-1.4、S-1.5、S-1.6、S-1.8、S-1.9、S-1.11、S-1.12、S-7.1、S-7.2、S-7.3、S-7.4、S-8.2 → F2。S-8.3 → F3。S-8.4／S-6.1 → 已 G2。S-8.7 → 本 hop builder，不是 F1 牙行為。

### A3　建議 Human 路徑

1. 開 Pages／本機審頁（路徑見 PR）。
2. 抽驗 S-4.3 三個 `檔:行`。
3. 看 Known Limits #1（D-2）能不能接受。
4. 提交判定：過／g3 pass → PASS；要改 → REQUEST_CHANGES；停 → HOLD。
5. **不要**叫 Agent 把頂欄改成 PASS。

### A4　Final Fresh 原始輸出（索引）

```
$ git rev-parse HEAD
75a54b432d51f9cc705e7a10de5fc6e37b73380c

$ bash scripts/test-five-station-f1.sh -v
… 63 × === CASE … [ok] …
failed=0
exit 0

group CASE: rp16=5 slots=2 dual-read=5 inflight=3 rp1=2 seam=3
spec-name=3 brief-files=3 attest=6 ship-quiz=4 rp-min-set=17 f1-close=10

$ bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md
✅ C1…C9
✅ G2 spec gate:9/9 全過
exit 0

$ bash scripts/check-file-map.sh
scanned=208 exempted=13
✅ PASS:forward 208 …
exit 0

$ bash scripts/check-five-station-f1.sh --live
INFO files_closed=True new_family=False q6_open=True
INFO seven_old_count=6 token_G1/G2/ACCEPTED=True
exit 0
```

`seven_old_count=6`：Fresh 當下尚無 `7-review.md`（本檔即第 7 個舊家族名）。`>=5` 通過。本檔落地後應為 7。

### A5　Gauntlet

```
$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-simplify/7-review.md \
    --source-sha 75a54b432d51f9cc705e7a10de5fc6e37b73380c \
    --review-file --require-layer test-five-station-f1
✅ evidence gauntlet: 69 checks passed — docs/dev/five-station-simplify/7-review.md
exit 0
```

`7-review.html`：先 `scripts/build-stage7-html.py --action`（截圖槽頁），再 `docs/dev/tools/build-gate-twin.py`（G3 五格 twin 覆寫同檔；無 shots 時 twin 較完整）。Pages 掛 twin。

### A6　作者對照（N4；矩陣之後才讀）

- Self-Review ①–⑧：F1 CASE 名含 S-id、未發明 G3、D-1／D-2 對得上、DBC 未偷偷修 limit —— 與獨立實跑一致。
- 差異：作者寫 py ≈407；本場 `wc -l` = 420。仍 D-2 L1。
- Decisions（單一家族／fixture 目錄／T-11 一次寫齊 16 RP／Q6 掃描跳過 4-spec 例句／Ship PASS 只認頂欄作者）不構成 L2。
- 不另存 `7-review-*.md`。
