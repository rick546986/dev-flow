---
title: jev-gate W10 — G2 誤放行（P2-10）只記錄：g2-misrelease record／report
slug: jev-gate
status: （歷史）W10 第一刀：誤放行定義 + 記錄指令（record／release）+ 誤放行率 report（shadow，只記錄；分母 = agent 放行紀錄，shadow 期間恆 insufficient_data）；不抽查、不自動 revert、不改任何 gate 判定、不動 G2R 門檻；~~7-review `root_cause: spec` 欄未進模板~~（2026-10-12 校對：已被取代，模板已有該欄；見下方現況對照表）
date: 2026-09-27
base: research/jev-supermemory 7e105df（W9 G2R 分流 shadow）
---

> **合進 main 後的現況(2026-09-28)**:G2 已由 main #418 上線(ADR 0004)。本檔「綁 g2r-shadow AUTO 紀錄」的綁定對象已由 `devflow-jev.py g2r`(`.devflow/jev/g2r.jsonl`)取代;沒有 Jev = no-op、`routed_by: none`,轉人條件照 ADR §3 全表。本檔保留為研究紀錄,規則正本是契約 §7。

# W10 G2 誤放行（只記錄）

> **現況對照表（2026-10-12 校對；以程式為準。以下內文是 2026-09-27 研究紀錄，舊說法保留並標「已被取代」）**
>
> | 本檔內文的舊說法 | 現況（已被取代，見…） |
> |---|---|
> | 綁 `.devflow/jev/g2r-shadow.jsonl` 的 AUTO 紀錄（`route_recommended=AUTO`） | 已被取代：綁 `.devflow/jev/g2r.jsonl`（`g2auto.G2R_LOG`）的 `route=AUTO` 紀錄；`devflow-jev.py g2r`（`_g2r_auto_index`） |
> | 「現在 G2 還是人審、沒有任何 agent 放行紀錄」「shadow 期間恆 `insufficient_data`」 | 已被取代：G2 已由 main #418 上線；`insufficient_data`（分母 0、不是 0%）仍是「還沒有任何 agent 放行紀錄」時的行為 |
> | 「7-review 模板的 `root_cause: spec` 欄也還沒加」「`root_cause` 欄未進模板」 | **已被取代（舊說法錯誤／過時）**：`_templates/7-review.md` frontmatter 第 8 行已有 `root_cause:`（空｜spec｜other；只准 G3 人類 reviewer 勾；勾 spec 且 4-spec 是 `g2_mode: auto` → 記 `g2-misrelease record --stage G3`）。「從 7-review 自動帶出 `G3` 事件」仍待做 |
> | 「main 的契約、SKILL、guide、hooks 都沒改」 | 已被取代：ADR 0004 accepted 後均已改 |
> | 分母 = agent 放行數；事件含實作階段三種 | **2026-10-12 owner 拍板**：①**事件**照程式現況，除 G3 退件外另收實作階段三種事件（只改文件）；②**分母**改成 v5 §3.3／ADR 0004 §6 的口徑 ——「已走到 G3 的 agent 自動放行 G2」（已改程式；證據 = `docs/dev/<slug>/7-review.md` 人簽 verdict，判不出 fail-closed 不進分母；見本檔 §4） |

> **一句話**：一份 spec 被 G2R 分流判 `AUTO`、G2 由 fresh-context agent reviewer + 機械檢查放行，之後在 **G3 人審**或
> **實作階段**被發現 spec 本身有問題 → 用 `devflow-jev.py g2-misrelease record` 記一筆到
> `.devflow/jev/g2-misrelease.jsonl`（gitignored）；G2 真的由 fresh agent reviewer 放行時用 `g2-misrelease release`
> 記一筆到 `.devflow/jev/g2-agent-release.jsonl`（gitignored）；`g2-misrelease report` 算誤放行數 ÷ **agent 放行數**。
> ~~現在 G2 還是人審、沒有任何 agent 放行紀錄~~（已被取代：G2 已上線）→ 沒有任何 agent 放行紀錄時，誤放行率是 `null`／`insufficient_data`，不是 0%。
> 只記錄：`gate_effect` 恆 `none`，率不接任何阻擋、抽查或退回。
> **作者 ≠ 審查者**：本檔是實作者的落檔，不宣稱任何 reviewer PASS。

## 1. 定義

**誤放行** = 下面三件事同時成立：

1. **G2R 判 AUTO**：~~`.devflow/jev/g2r-shadow.jsonl`~~（已被取代：現為 `.devflow/jev/g2r.jsonl`）有一筆同 `slug`、同 `case_hash`、AUTO 的紀錄（W9；原 `route_recommended=AUTO`，現為 `route=AUTO`）。
   紀錄綁的就是這個 `case_hash`；`g2r_reasons` 從那筆 shadow 紀錄**抄過來**，不收呼叫端自己給的。
2. **G2 實際由 fresh-context agent reviewer + 機械檢查放行**：`g2_released_by=fresh_agent_reviewer`，**而且**
   `.devflow/jev/g2-agent-release.jsonl` 有同 `slug` + `case_hash` 的放行紀錄（`g2-misrelease release` 寫的）。
   說是 agent 放行、卻對不到放行紀錄的誤放行紀錄 → report 判不一致（`consistent=false`，exit 1）。
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
用 `g2_released_by=human` 記，report 另列成 `shadow_counterfactual`／`shadow_counterfactual_rate`（見 §4），
**不算進誤放行數、也不算進誤放行率**。

**與 v5 §3.3 的差別（2026-10-12 owner 拍板照程式現況）**：v5 原文只把「G3 退件 + `root_cause: spec`」算誤放；本檔依 owner 2026-09-27 的 W10 指示多收「實作階段」三種事件，
2026-10-12 owner 確認事件範圍就是「G3 退件且 `root_cause: spec`，**另**收實作階段 `spec_amended`／`spec_returned`／`reverted`」。
report 用 `misreleased_by_stage` 分開列；只想看 v5 原口徑就看 `G3` 那格。實作階段事件發生時該 case 通常還沒走到 G3，
所以它列在 `misreleased`、**不進誤放率**（見 §4）。

## 2. 記錄格式（`.devflow/jev/g2-misrelease.jsonl`，schema `devflow-g2-misrelease/1`）

每行一筆，必填欄（`policy.validate_g2_misrelease`，寫入前和 report 讀回時都驗）：

| 欄 | 規則 |
|---|---|
| `slug` | `[A-Za-z0-9._-]`，首字英數 |
| `case_hash` | `sha256:<64 小寫 hex>`，要對到 ~~g2r-shadow~~（現為 g2r.jsonl）的 AUTO 紀錄 |
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

### 2.1 agent 放行紀錄（`.devflow/jev/g2-agent-release.jsonl`，schema `devflow-g2-agent-release/1`）

誤放行率的分母。只在 G2 **真的**由 fresh agent reviewer + 機械檢查放行時記；shadow 期間（G2 仍人審）不該有任何一筆。
G2 live 的 PR 會在放行當下呼叫 `g2-misrelease release`。這支指令只記錄，不放行任何東西、不改任何 gate 判定。

必填欄（`policy.validate_g2_agent_release`，寫入前和 report 讀回時都驗）：`slug`、`case_hash`（要對到 g2r-shadow 的 AUTO 紀錄）、
`g2r_reasons`（從 shadow 紀錄抄）、`evidence_ref`（agent reviewer 報告路徑／PR 連結；規則同上表）、`reported_by`（`human:`／`agent:`）、
`recorded_at`。另帶 `g2_released_by=fresh_agent_reviewer`、`g2r_policy` 與同一組 false 旗標。
同一 `(slug, case_hash)` 只准記一次，重記 → 拒絕。

## 3. 用法與 exit code

```bash
python3 scripts/devflow-jev.py --root <專案根> g2-misrelease record \
  --slug demo-feature --case-hash sha256:… --stage G3 --via g3_request_changes \
  --evidence-ref docs/dev/demo-feature/7-review.md --released-by fresh_agent_reviewer --reported-by human:<名>
python3 scripts/devflow-jev.py --root <專案根> g2-misrelease release \
  --slug demo-feature --case-hash sha256:… --evidence-ref <agent reviewer 報告或 PR> --reported-by agent:<id>
python3 scripts/devflow-jev.py --root <專案根> g2-misrelease report
```

| 指令 | exit 0 | exit 1 | exit 2 |
|---|---|---|---|
| `record` | 已 append | — | 欄位不合、via 不屬於 stage、對不到 AUTO 紀錄、重複事件、缺參數（都不落盤） |
| `release` | 已 append | — | 欄位不合、對不到 AUTO 紀錄、同 case 重複放行、缺參數（都不落盤） |
| `report` | 資料一致（含「資料不足」） | 有壞行、欄位不合的紀錄、對不到 AUTO 的孤兒紀錄（誤放行或放行紀錄都算）、`fresh_agent_reviewer` 誤放行對不到放行紀錄、已有 agent 放行卻記成 `human` | 參數錯 |

## 4. 誤放行率與 shadow 反事實率

**誤放行率**（`misrelease_rate`，`rate_status=ok|insufficient_data`）

- **分母 = 已走到 G3 的 agent 自動放行 G2 數**（**2026-10-12 owner 拍板**，已改程式 `policy.g2_misrelease_rate`、`run_g2_misrelease_report`）：
  `g2-agent-release.jsonl` 裡對得到 g2r.jsonl AUTO 紀錄的相異 `(slug, case_hash)`，再篩出「已走到 G3」者。
  **「已走到 G3」的證據** = `docs/dev/<slug>/7-review.md` 頂欄有人簽的 G3 verdict（`g2auto.g3_reached`）：
  `verdict` ∈ PASS｜REQUEST_CHANGES｜HOLD，`verdict_source` ∈ human_attested｜owner_self_review，`attested_by: human:<名>`。
  **fail-closed**：檔案不存在、讀不到、頂欄缺、verdict 空或 PRE-REVIEW、來源不是人簽（含 `fresh_agent_reviewer`／`agent:*`）→ 判不出，**不進分母**。
  不採信 misrelease 紀錄自己說的「G3 階段」—— 只認檔案證據。已知限制：以 slug 為單位，不比對 verdict 與放行的先後。
  只有 G2 **真的**由 fresh agent reviewer 放行的 case 才可能被 agent 誤放；拿全部 AUTO 紀錄當分母會把「還沒開始」算成 0%。
- **分子 = 分母內的誤放行數**：有 `g2_released_by=fresh_agent_reviewer` 紀錄、對得到放行紀錄、**且在分母內**的相異 `(slug, case_hash)` 數
  （同一 case 被發現多次只算一次）。還沒走到 G3 就被發現的（實作階段事件）照樣計入 `misreleased`、`misreleased_by_stage`，
  另以 `misreleased_not_reached_g3` 列出，**不進率**（避免分子大於分母）。
- **誤放行率** = `misreleased_g3_reached` ÷ `g3_reached_agent_released`；report 另附 `agent_released`（全部 agent 放行）、
  `agent_released_not_reached_g3`、`misrelease_denominator`（= `g3_reached_agent_released`）、`g3_evidence`（證據來源說明）。
- **資料不足要明講，不能算成 0%**：沒有放行檔，或 agent 放行數 = 0 → `misrelease_rate=null`、`rate_status=insufficient_data`，
  note 寫「目前沒有任何由 fresh agent reviewer 放行的紀錄，不是 0%」；**有 agent 放行但沒有任何一筆已走到 G3** → 同樣 `null`／`insufficient_data`，
  note 寫「有 N 筆 agent 放行，但沒有任何一筆已走到 G3 …；分母為 0，不是 0%」（`policy.G2M_NO_G3_REACHED_NOTE`）。
  有壞行／不合法紀錄／孤兒紀錄／對不到放行紀錄的 agent 誤放行 → 也不算率（`consistent=false`，exit 1）。
  分母 > 0 且分子 = 0 → 這時才是真的 `0.0`。
- 與舊口徑（分母 = 全部 agent 放行數）比：G2 live 初期還沒走到 G3 的 case 不再稀釋誤放率。
- 樣本數門檻 owner 未定；report 只附 `n`，不自己判「夠不夠」。

**shadow 反事實率**（`shadow_counterfactual_rate`，`shadow_counterfactual_status=counterfactual|insufficient_data`）

- = 由人放行（`g2_released_by=human`）但後來發現 spec 有問題的 AUTO case 數 ÷ AUTO 總數（g2r-shadow 裡 AUTO 的相異 `(slug, case_hash)`）。
- 意思是「如果這些 AUTO case 當初交給 agent 放行，至少會有這麼多出事」的參考值；它**不是**誤放行率，不能跟 `misrelease_rate` 混用或相加。
- AUTO 總數 = 0（含沒有 shadow 紀錄檔）→ `null`、`insufficient_data`；資料不一致時也不算。
- 同一 case 已有 agent 放行紀錄、卻又記成 `human` → 判不一致，不讓同一 case 同時落在兩個率裡。

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
- ~~main 的契約、SKILL、guide、hooks 都沒改；7-review 模板的 `root_cause: spec` 欄也還沒加（那是 main 模板面）。~~（已被取代：ADR 0004 accepted 後契約面已改；`_templates/7-review.md` 已有 `root_cause` 欄。）

## 7. 留給後面

- ~~7-review 模板加 `root_cause: spec`（人勾）~~（已完成：模板已有 `root_cause` 欄），之後從 7-review 自動帶出 `G3` 事件，不必手動 `record`（仍待做）。
- 實作階段三種事件的自動偵測（改 4-spec 的 commit、退回 Stage 4、revert）。
- G2 live 的 PR 在 agent 放行當下呼叫 `g2-misrelease release`；之後 `g2_released_by` 改由放行紀錄帶出，不再由呼叫端給。
- hooks `spec_profile` 的大小寫／非法值處理（見 §5）。
