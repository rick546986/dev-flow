---
title: jev-gate W5 — 評估計算器 / risk ceiling / 可稽核附註 / J2 厚包 / J4 實驗
slug: jev-gate
status: W5 完成（P2-2／P2-3／P2-4／P2-7／P2-8；全部 shadow／assist；無 AUTO、無 verdict 寫入、不進 main）
date: 2026-09-23
base: research/jev-supermemory 521ef47（W4）→ 本分支 claude/jev-w5-eval-3aslgp
---

# W5 評估 / J2 厚包 / J4 實驗

> roadmap §1 W5 = P2-2～P2-8（P2-5／P2-6 要 AUTO live 之後，本波不做）。A1–A7／B1–B5 鎖定：**沒改任何門檻、題組、policy 常數、packet builder 常數**；
> 正式 `questionset_hash` 未變。J2／J4 的題組住**另一個檔** `jev-questions-experimental.json`，各自 manifest 與 hash，不碰 J1/J3/J5 的 calibration group。
> `GRADUATED = False` 仍是唯一賦值；J2／J4 的 `route_taken` 不看 level，恆 HUMAN。**作者 ≠ 審查者**：本文不宣稱任何人 PASS。

## 0. 分支與 SHA

| 項 | 值 |
|---|---|
| 基線 | `research/jev-supermemory` `521ef47f522ec703a1435f4369e2f90514395255`（W4 已合） |
| W5 分支 | `claude/jev-w5-eval-3aslgp`（commit SHA 見 PR） |
| main | **未動** |

## 1. P2-2 report／eval 計算器

**做了什麼**（`scripts/devflow_jev/report.py` 新增；`scripts/devflow-jev.py report` 接上）

- `route_class(evaluation)`：`noop`／`mechanical_override`（route_reason 以 `runtime_modified_this_session`、`risk_ceiling_override`、`packet_truncated`、`header_body_conflict` 開頭）／`model_route`。**override 不進 graduation denominator**（roadmap §5.1 第 7 條），另列 `unique_cases_mechanical_override`。
- `eval_metrics(evaluations, feedbacks_by_layer, breaker_failures)`：`evaluations_total`、`unique_cases_all`／`_model_route`／`_mechanical_override`、`route_class_counts`、`route_reason_counts`、`truncation_rate`、每層（human_attested／fresh_agent_reviewer）`n`／`n_agree`／`n_overturn`／`wilson_lower_95`／`floor_met`／`frozen`／`labeled_fraction`（= n ÷ unique model-route cases）／`brier_chosen_route`（被選 route 的機率對 agree=1／overturn=0；只算 AUTO／REQUEST_CHANGES 的預測，HUMAN 不是預測）／`excluded`、`question_metrics`（noul 平均、score 直方、choice 分布；只用 `answers_summary`，沒有 raw）、`circuit_breaker_state`（任一層 frozen → `frozen`）、`transport_breaker_failures`、`floors`。
- `run_report`：分層 graduation 改只餵 model-route evaluation；輸出多 `metrics` 與 `circuit_breaker_state`；原 `layers`／`excluded_by_layer`／`not_replayable` 欄位不變。

**結論／邊界**

- 真實 report 只讀 **replay store 的 evaluation** 與 **durable 的 feedback record**；2026-09-22 的 21 次合成／文件稽核從未進這兩處，**由構造排除**（測試：空 store → 全 0／None，不填假數）。
- variant／retry／reevaluate 同 `case_id` → `graduation` 記 `duplicate_case`，n 不膨脹（測試）；wrong HEAD label → `evidence_version_mismatch` 排除（測試用 `wrong-head-label.json`）。
- 合成 ledger（`test_guards.W5EvalMetrics`）只驗計算器；真實路徑測試（`test_runtime.W5EvalAndExperiments.test_report_exposes_p2_2_metrics_on_real_store`）用隔離 repo 一條合成 Ship case，n=1 只驗機制。
- Brier 是「被選 route 機率 vs 人類 agree/overturn」，不是校準證明；n 極小時數字沒有統計意義，report 不做任何「準確率」翻譯。

**證據路徑**：`scripts/devflow_jev/report.py`（`route_class`／`brier`／`question_metrics`／`eval_metrics`）、`scripts/devflow-jev.py::run_report`、`test_guards.py::W5RiskCeilingAndRouteClass／W5EvalMetrics`、`test_runtime.py::W5EvalAndExperiments`。

## 2. P2-4 機械 risk ceiling

- W1 已有 `provenance.risk_ceiling_hit`＋`route_j5(risk_ceiling_hit=True) → HUMAN/risk_ceiling_override`；W5 補的是**輸入從哪來**：`enqueue` 沒給 `--changed-paths` 時，`derive_changed_paths` 從 git 推（`--base-ref`／develop／main／master／origin 的 merge-base..HEAD；都沒有 → HEAD 那個 commit 的檔）；推不出 → `[]`＋`source=unavailable`，不猜。queue item 記 `changed_paths`／`changed_paths_source`／`risk_ceiling_hit`，`drain` 原樣帶進 `run_ask`。
- fixture `scripts/fixtures/devflow-jev/risk-ceiling-migration.json`：滿分答案＋`db/migrations/…` → `HUMAN`／`risk_ceiling_override`；同答案沒命中 → `AUTO`（對照）。runtime 測試：commit 含 migration → enqueue 自動命中 → drain 得 HUMAN／`risk_ceiling_override` → report 歸 mechanical override、model-route denominator 為 0。
- 清單只有一份（`policy.RISK_PATHS_DEFAULT`，在 policy 指紋內）；縮窄由 W1 G6 `risk_paths_change` 留痕（未動）。

## 3. P2-7 AUTO 可稽核附註（形狀）

- `ledger.audit_note(evaluation)` → 封閉五欄 `{gate, questionset_hash_prefix(16 hex), model_resolved, route_recommended, evaluation_id}`；`assert_audit_note_safe` 釘鍵集合**恰等於**這五個、值是 ≤64 字的字串或 None、privacy 零命中；`audit_note_markdown` 產一行 HTML 註解，明寫「recommendation only; not a verdict; no AUTO」。
- `note --evaluation-id` 子命令。測試：note 全文找不到 `probab`／`answers`／`packet`／`0.97`／`AUTO_SHIP`／`route_taken`／`session`；多一鍵或值含 secret 都拒。
- **沒做**：把附註自動貼進 PR／7-review 的動線（那是 P3-2 契約面的事；7-review 模板本波未動）。

## 4. P2-3 J4 升階路由（實驗；assist-only）

- `policy.J4_FAILURE_CATEGORIES = ("SPEC","ENV","IMPL","UNKNOWN")` —— 測試釘與 `hooks/devflow_obs_vendor/schema/agent-event.schema.json` 的 enum 逐字相同；題組 `J4.failure_category` 的 criteria 也釘同一組。
- `MODEL_TIERS = (haiku, sonnet, opus)`，`fable` 與 opus 同層；`escalate_to` **只升一層**，最高層／認不得 → None（測試：haiku→sonnet、sonnet→opus、opus/fable→None、mystery→None）。
- `route_j4`：UNKNOWN → `human_triage`；`retry_same_tier_useful ≥ .5` → `retry_same_tier`；否則升一層，升不了 → `human_triage`。`assist_only=True`、`writes_dispatch=False`。`route_taken` 恆 `HUMAN/j4_assist_only`（就算 yaml 把 J4 設 live）。
- `j4-assist --slug --task-id --current-model --failure-summary FILE`：quoted_context 帶失敗摘要（privacy 掃描），evidence = 摘要 sha256＋HEAD；輸出建議，**不寫** `.devflow/exec.json`、不建豁免卡、不碰 `_dispatch_impl.py`（測試斷言兩個檔都不存在）。`_dispatch_impl.py` 仍是窄版首派最高階 fail-open，本波沒把它說成、也沒改成權限守衛。

## 5. P2-8 J2 厚證據包（實驗；永遠 shadow）

- `parse_decision_doc`：只抽 2-decision.md 的結構 —— Approaches Considered 表（方案／摘要／優／劣／成本／依據）、Decision（抓「採 **X**」字母）、Rejected Alternatives、Rationale、Real-world 去向、Owner Calls 表（狀態欄有 ✅／✗／已裁 → 視為有人類答案）。不判斷內容。
- `build_j2_packet`：options 用**固定等長** description（形式控制），pros／cons 從表格拆（各需 ≥2，不夠 → `packet_unbuildable`，不補寫）；方案原文、Rationale、Rejected、Real-world、Open Questions、每條 Owner Call（含人類答案）全放 `quoted_context`（資料不是指令），Owner Call 的 source 明寫「human answer recorded; data, not a question for the model」；header 帶 `option_identities`（標籤↔方案名對照）。J2 header 不進 `packet.HEADER_REQUIRED`（那會轉正式 hash），驗證在 runtime。
- `j2-shadow`：三個 variants —— v0 原順序、v1 方案順序反轉（標籤重排、對照表跟著換）、v2 primary_request 換措辭；**同一 `case_id`**（evidence = decision 全文 sha256＋HEAD）；`policy.j2_stability` 對回原方案身分：不一致或任一 `NONE_CLEAR` → `unstable=True`，`graduation_eligible` 永遠 False。`route_taken` 恆 `HUMAN/j2_shadow_window_not_ratified`；`auto_pass=False`；`window_candidate=50`、`window_ratified=False`，沒有旗標能改。J2 不回答 Owner Calls（`answers_owner_calls=False`；packet 標明）。
- 測試：三 variants 一個 case、report `unique_cases_all=1`；順序反轉但模型固定選標籤 A → identity 變 → `unstable`；方案優點只剩一條 → `packet_unbuildable`；off／J2 預設 off → noop；缺 2-decision → noop。

## 6. 驗證

| 套件 | 結果 |
|---|---|
| `scripts/test-devflow-jev.sh` | ①②⑤③④ 全過；unittest **232/232**（guards 147、runtime 76、http_transport 9；地板 209→**232**） |
| `scripts/check-ship-manifest.sh` | 26/26（新增 `jev-questions-experimental.json` 列 → 25 列；`version` v1-50dce597421a238b → **v1-9bc5fa700e6d26e1**，契約正副本同步；policy／report／ledger／runtime 副本回拷） |
| `scripts/check-file-map.sh` | forward 231 + reverse 234（json 不在必列集，guide 加了散發面列） |
| `scripts/test-architecture-guards.sh` | 146/146 |
| `check-gate-verdict-write` 21/21、`check-devstage7-graph` 0 failures、py-floor（229 heredoc）、stale-paths、version-sync、dev-setup-discipline | 綠 |
| 真 TypeSafe API | **沒有打**；J2／J4 都走 FakeTransport |

## 7. 明確沒做

- P2-5 隨機抽查、P2-6 次要回饋（要 AUTO live 之後）。
- 沒開任何 AUTO；J2 沒有 AUTO_PASS 路徑；J4 不派工。
- 沒改 A1–A7／B1–B5、`jev-questions.json`、policy 常數、packet builder 常數（正式 `questionset_hash` 未變）。
- 沒對真 API 送請求、沒拿真樣本充 n；21 次外部稽核不在任何 store。
- 沒把 P2-7 附註接進 PR／7-review 模板（P3-2）。
- supermemory 不接；不進 main。
