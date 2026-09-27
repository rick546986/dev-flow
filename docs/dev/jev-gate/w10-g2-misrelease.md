---
title: jev-gate W10 — G2 誤放行（P2-10）只記錄：g2-misrelease record／report
slug: jev-gate
status: W10 第一刀：誤放行定義 + 記錄指令 + 誤放行率 report（shadow，只記錄）；不抽查、不自動 revert、不改任何 gate 判定、不動 G2R 門檻；7-review `root_cause: spec` 欄未進模板
date: 2026-09-27
base: research/jev-supermemory 7e105df（W9 G2R 分流 shadow）
---

# W10 G2 誤放行（只記錄）

> **一句話**：一份 spec 被 G2R 分流判 `AUTO`、G2 由 fresh-context agent reviewer + 機械檢查放行，之後在 **G3 人審**或
> **實作階段**被發現 spec 本身有問題 → 用 `devflow-jev.py g2-misrelease record` 記一筆到
> `.devflow/jev/g2-misrelease.jsonl`（gitignored）；`g2-misrelease report` 算誤放行數 ÷ AUTO 總數。
> 只記錄：`gate_effect` 恆 `none`，率不接任何阻擋、抽查或退回。
> **作者 ≠ 審查者**：本檔是實作者的落檔，不宣稱任何 reviewer PASS。

## 1. 定義

**誤放行** = 下面三件事同時成立：

1. **G2R 判 AUTO**：`.devflow/jev/g2r-shadow.jsonl` 有一筆同 `slug`、同 `case_hash`、`route_recommended=AUTO` 的紀錄（W9）。
   紀錄綁的就是這個 `case_hash`；`g2r_reasons` 從那筆 shadow 紀錄**抄過來**，不收呼叫端自己給的。
2. **G2 實際由 fresh-context agent reviewer + 機械檢查放行**：`g2_released_by=fresh_agent_reviewer`。
3. **之後發現 spec 本身有問題**，而且是下表其中一種事件（`discovered_stage` × `discovered_via`）：

| 發現階段 `discovered_stage` | 發現來源 `discovered_via` | 算數的事件 | 判定來源（`evidence_ref` 指這裡） | 誰能記 |
|---|---|---|---|---|
| `G3` | `g3_request_changes` | G3 人審判 REQUEST_CHANGES，且 7-review 退件理由由人勾 `root_cause: spec` | `docs/dev/<slug>/7-review.md` | **只准 `human:`**（v5 §3.3：agent 不得代勾） |
| `G3` | `g3_hold` | G3 人審判 HOLD，同上勾 `root_cause: spec` | 同上 | 只准 `human:` |
| `implementation` | `spec_amended` | 實作中發現 spec 錯漏，回頭改 4-spec（R/S、DD、Verification Profile）才能繼續 | 改 4-spec 的 commit sha／PR | `human:` 或 `agent:` |
| `implementation` | `spec_returned` | 實作中 spec 被退回 Stage 4 重審 | 退回紀錄（5-tasks／dispatch 記錄路徑、PR） | `human:` 或 `agent:` |
| `implementation` | `reverted` | 依這份 spec 做的實作因 spec 本身的問題被 revert | revert commit sha／PR | `human:` 或 `agent:` |

**不算**：

- 追不到規格的退件或 revert（實作 bug、測試不穩、環境問題）——跟 v5 §3.3「追不到規格的 G3 退件不算」一致。
- G2R 判 `HUMAN` 的 case（那是人放行的，不是 G2R 自動軌道的誤放）。`record` 對不到 AUTO 紀錄會直接拒絕、不落盤。
- 抽查發現的問題：C1 抽查已移除，沒有 `spot_check` 這個來源。

**shadow 反事實**：W9／W10 期間 G2R 只跑 shadow，G2 實際上還是人審。這種「G2R 會判 AUTO、但實際由人放行、之後發現 spec 有問題」的案子
用 `g2_released_by=human` 記，report 另列成 `shadow_counterfactual`，**不算進誤放行數、也不算進誤放行率**。

**與 v5 §3.3 的差別**：v5 只把「G3 退件 + `root_cause: spec`」算誤放；本檔依 owner 2026-09-27 的 W10 指示多收「實作階段」三種事件。
report 用 `misreleased_by_stage` 分開列，要回到 v5 的口徑只看 `G3` 那格即可。

## 2. 記錄格式（`.devflow/jev/g2-misrelease.jsonl`，schema `devflow-g2-misrelease/1`）

每行一筆，必填欄（`policy.validate_g2_misrelease`，寫入前和 report 讀回時都驗）：

| 欄 | 規則 |
|---|---|
| `slug` | `[A-Za-z0-9._-]`，首字英數 |
| `case_hash` | `sha256:<64 小寫 hex>`，要對到 g2r-shadow 的 AUTO 紀錄 |
| `g2r_reasons` | 非空字串 list，從 shadow 紀錄抄 |
| `discovered_stage` | `G3`／`implementation` |
| `discovered_via` | 要屬於該階段（見上表） |
| `evidence_ref` | 單行、非空、無前後空白、≤ 200 字 |
| `g2_released_by` | `fresh_agent_reviewer`／`human` |
| `reported_by` | `human:<名>`／`agent:<id>`；`G3` 只准 `human:` |
| `recorded_at` | `YYYY-MM-DDTHH:MM:SSZ`（UTC，自動填） |

另帶：`counts_as_misrelease`、`g2r_policy`（抄自 shadow 紀錄）、`gate_effect=none`、`writes_verdict=false`、`auto_revert=false`、
`spot_check=false`、`graduated`／`j5_live_ratified`／`j2_window_ratified`（全 false）、`network=false`。
同一事件（slug + case_hash + stage + via + evidence_ref 全同）重記 → 拒絕。
`reported_by` 的格式比對是 tripwire，不是身份驗證（同 P1-G7）。

## 3. 用法與 exit code

```bash
python3 scripts/devflow-jev.py --root <專案根> g2-misrelease record \
  --slug demo-feature --case-hash sha256:… --stage G3 --via g3_request_changes \
  --evidence-ref docs/dev/demo-feature/7-review.md --released-by fresh_agent_reviewer --reported-by human:<名>
python3 scripts/devflow-jev.py --root <專案根> g2-misrelease report
```

| 指令 | exit 0 | exit 1 | exit 2 |
|---|---|---|---|
| `record` | 已 append | — | 欄位不合、via 不屬於 stage、對不到 AUTO 紀錄、重複事件、缺參數（都不落盤） |
| `report` | 資料一致（含「資料不足」） | 有壞行、欄位不合的紀錄、對不到 AUTO 的孤兒紀錄 | 參數錯 |

## 4. 誤放行率

- **誤放行數** = 有 `g2_released_by=fresh_agent_reviewer` 紀錄的相異 `(slug, case_hash)` 數（同一 case 被發現多次只算一次）。
- **AUTO 總數** = g2r-shadow 裡 `route_recommended=AUTO` 的相異 `(slug, case_hash)` 數（同一 case 重跑 shadow 不重算）。
- **誤放行率** = 誤放行數 ÷ AUTO 總數。
- **資料不足要明講，不能算成 0%**：沒有 g2r-shadow 紀錄檔，或 AUTO 總數 = 0 → `misrelease_rate=null`、
  `rate_status=insufficient_data`；有壞行／不合法紀錄／孤兒紀錄 → 也不算率（`consistent=false`，exit 1）。
  AUTO 總數 > 0 且沒有誤放行 → 這時才是真的 `0.0`。
- 分母用「所有 AUTO shadow 紀錄」，比 v5 的「已走到 G3 的自動 G2」大（有些還沒走到 G3），所以這個率偏低、是下界。
- 樣本數門檻 owner 未定；report 只附 `n`，不自己判「夠不夠」。

## 5. 順手修：`policy.spec_risk_of`（W9 留下的）

W9 版的 regex 是 `[a-z]+`，`- Risk: High` 整行不匹配，被當成沒寫（還會往下撿到 T-n 的 `Risk: normal`）。現在：

- 第一條 `- Risk:` 行就是答案；值大小寫都認，正規化成小寫。
- 值是空的（`- Risk:`、`—`）→ `None`（模板缺省 normal）。
- 首字不是 `high|medium|normal|low` → `JevError`，不默默當成 normal。
- `route_g2` 的 case 仍只收正規化後的小寫值（呼叫端先過 `spec_risk_of`）。

**跟 `hooks/devflow-lib.py` `spec_profile` 不一致（hooks 本刀不改）**：

| 4-spec 內容 | hooks `spec_profile()["risk"]` | `policy.spec_risk_of` |
|---|---|---|
| `- Risk: high`／`normal`、沒寫、模板占位 `normal \| high(…)` | 同值 | 同值（測試釘住） |
| `- Risk: High`／`HIGH` | `None`，或撿到後面 T-n 的值 | `high` |
| `- Risk: bogus`／`critical` | 原樣回傳 `bogus`（沒有報錯；不是 `high` → OC-4 不擋） | `JevError` |
| `- Risk: 高` | `None` | `JevError` |

影響：hooks 的 OC-4（`lane: fast` + `Risk: high` 拒絕啟動）遇到 `Risk: High` 不會擋。修 hooks 屬於 main 面，留給 owner 決定。

## 6. 沒動的東西

- 不抽查、不自動 revert、不改任何 gate 判定、不動 `G2R_THRESHOLDS`（C3 0.85、risk ≥ 2）；`g2r_fingerprint()` 不變。
- `GRADUATED=False`、`gate.J5_LIVE_RATIFIED=False`、`policy.J2_WINDOW_RATIFIED=False`；每筆紀錄和 report 都帶這三個值。
- 雙閘門不動：`g2-misrelease` 零網路、不建 transport、不建 `.dev-flow/jev.yaml`、不寫 Jev durable ledger。
- 不讀也不寫 `docs/dev/<slug>/` 的 `verdict:`；Jev 不寫 verdict。
- main 的契約、SKILL、guide、hooks 都沒改；7-review 模板的 `root_cause: spec` 欄也還沒加（那是 main 模板面）。

## 7. 留給後面

- 7-review 模板加 `root_cause: spec`（人勾），之後從 7-review 自動帶出 `G3` 事件，不必手動 `record`。
- 實作階段三種事件的自動偵測（改 4-spec 的 commit、退回 Stage 4、revert）。
- G2R 從 shadow 走到實際放行後，`g2_released_by` 改由 route_taken 紀錄帶出，不再由呼叫端給。
- hooks `spec_profile` 的大小寫／非法值處理（見 §5）。
