---
title: jev-gate W9 — G2R 分流（P2-9）shadow：policy.route_g2 + g2r-shadow 記錄
slug: jev-gate
status: （歷史）W9 第一刀：G2R 分流函式 + shadow 記錄；不改任何 gate 實際判定、不上線；~~G2R 題組（jev-questions.json）~~ 與 P3-5 其餘面未做 ——【2026-10-12 校對：已被 main #418 取代，G2 已上線；G2R 題組實際住在 policy.py 的 G2R_QUESTIONS，不在 jev-questions.json，manifest.py 未收錄；見下方現況對照表】
date: 2026-09-27
base: research/jev-supermemory 278dda8（W8 補 + G2R／MR 名稱核准）
---

> **合進 main 後的現況(2026-09-28)**:G2 已由 main #418 上線(ADR 0004)。本檔的 `g2r-shadow` 子命令已由 `devflow-jev.py g2r`(`.devflow/jev/g2r.jsonl`)取代;沒有 Jev = no-op、`routed_by: none`,轉人條件照 ADR §3 全表。本檔保留為研究紀錄,規則正本是契約 §7。

# W9 G2R 分流（shadow）

> **現況對照表（2026-10-12 校對；以程式為準。以下內文是 2026-09-27 研究紀錄，舊說法保留並標「已被取代」）**
>
> | 本檔內文的舊說法 | 現況（已被取代，見…） |
> |---|---|
> | `devflow-jev.py g2r-shadow` → `.devflow/jev/g2r-shadow.jsonl`，`gate_effect` 恆 `none` | 已被取代：`devflow-jev.py g2r --slug <slug>` → `.devflow/jev/g2r.jsonl`（`g2auto.G2R_LOG`、schema `devflow-g2r/1`）；AUTO = 交給 fresh agent reviewer，`write-g2-auto` 才寫 verdict（`devflow_gate.py`） |
> | 「G2R 題組（`jev-questions.json`）進 manifest」 | 已被取代：題組在 `policy.G2R_QUESTIONS`（繁體中文，#425），用自己的 `g2r_fingerprint()`（`e68b6aa6dad6`）；`jev-questions.json`／`manifest.py` 沒有收錄 |
> | case「六欄全必填」 | 已被取代：`policy.G2R_CASE_KEYS` 八欄（多 `authored_by_present`、`jev_status`） |
> | 轉人條件 ①–⑤ | 已擴充：另有「當次改到 Jev runtime」與「缺 `authored_by`」；provenance／author≠approver 在 `write-g2-auto` 重判（ADR 0004 §3 全表） |
> | 風險路徑來源「spec 宣告的 path」 | 程式現況只看 4-spec Diff Budget 的 `- Paths:` 一行；ADR 0004 原寫「宣告的路徑／R 列檔案」—— **以何者為準待 owner 決定**（見 ADR 0004 §3） |
> | 「G2 還是人審」「main 的契約、SKILL、guide、hooks 都沒改」 | 已被取代：ADR 0004 accepted、契約 §7／guide／SKILL／hooks 已改、`G2_AUTO_LIVE = True` |
> | 風險 `normal` 未提 | 補充：`G2R_SPEC_RISK_SCORE = {high:2, medium:1, normal:0, low:0}`，`normal` 算 < 2 |

> **一句話**：`policy.route_g2(case)` 依 `v5-owner-direction.md` §3.2（C3／C4 owner 2026-09-26 定案、G2R 名稱 owner 2026-09-27 核准）
> 把一份 spec 的 G2 案子分成 `AUTO` 或 `HUMAN`，附**全部**命中的理由；~~`devflow-jev.py g2r-shadow` 只把結果 append 到
> `.devflow/jev/g2r-shadow.jsonl`~~（已被取代：現為 `devflow-jev.py g2r` → `.devflow/jev/g2r.jsonl`）（gitignored），`gate_effect` 恆 `none`。
> **作者 ≠ 審查者**：本檔是實作者的落檔，不宣稱任何 reviewer PASS。

## 1. 分流規則（任一成立 → HUMAN）

| # | 條件 | reason 字串 | 來源 |
|---|---|---|---|
| ① | Jev 判的不是 `AUTO_PASS`（`HUMAN_REVIEW`／`REQUEST_CHANGES`／缺） | `jev_g2_route=<choice>` | §3.2；Jev 不是 reviewer，`REQUEST_CHANGES` 也只轉人、不退件 |
| ① | Jev 信心 `p(AUTO_PASS) < 0.85`（缺值也算） | `jev_p_auto_pass_below_threshold(p<0.85)` | C3；**剛好 0.85 = 不轉人** |
| ② | spec 沒宣告任何 path | `spec_declares_no_paths` | §3.2 fail-closed，不當成「沒命中」 |
| ② | 宣告的 path 命中 `policy.RISK_PATHS_DEFAULT` | `risk_paths_hit:<paths>` | 同 P2-4 `provenance.risk_ceiling_hit`，清單只有一份 |
| ③ | 有 Jev：`risk` Score ≥ 2；Jev 沒給 Score | `risk>=2(jev=n)`／`jev_risk_missing` | §3.2 |
| ③ | 沒有 Jev：4-spec `- Risk: high`（映射成 2） | `risk>=2(spec_risk=high)` | C4；`normal`／`medium`／`low`／未寫 → < 2 |
| ④ | 有未裁決 Owner Call | `owner_calls_unresolved=n` | OC 永遠人裁 |
| ⑤ | 需要 Demo verdict | `demo_verdict_required` | Demo verdict human-only |

都沒命中 → `AUTO`，`reasons=["no_human_condition_hit"]`，`auto_means="handoff_to_fresh_agent_reviewer_and_mechanical_checks_not_a_pass"`。
**AUTO 不是通過**：結果恆帶 `is_pass=false`、`writes_verdict=false`、`jev_role=router_only`。

## 2. 輸入（case JSON，六欄全必填）

```json
{"slug": "demo-feature", "declared_paths": ["src/app/handler.py"], "spec_risk": "normal",
 "owner_calls_unresolved": 0, "demo_verdict_required": false, "jev": null}
```

- `jev`：`null` = 沒有 Jev（無 key／未 opt-in／失敗），其餘條件照判；有 Jev 時形狀 `{"g2_route": {"choice", "probabilities"}, "risk": {"score"}}`。
- 缺欄、未知欄、型別錯、`spec_risk` 不認得 → `JevError`（CLI exit 2），**不猜、不落盤**。
- `policy.spec_risk_of(text)` 讀 4-spec 的 `- Risk:` 首值。（W10 改：值大小寫都認、非法值報錯，已不再與 `hooks/devflow-lib.py` 同一條 regex，差異見 `w10-g2-misrelease.md` §5。）

用法（~~`g2r-shadow --case case.json`~~，已被取代）：現為 `python3 scripts/devflow-jev.py --root <專案根> g2r --slug <slug> [--no-record]`（case 由 4-spec／2-decision／`_stage3_impl.py` 自動組，不再手給 case.json）。原寫法：`python3 scripts/devflow-jev.py --root <專案根> g2r-shadow --case case.json [--no-record]`

## 3. 沒動的東西

- `GRADUATED=False`、`gate.J5_LIVE_RATIFIED=False`、`policy.J2_WINDOW_RATIFIED=False`；每筆 shadow 紀錄也帶這三個值。
- 雙閘門（`TYPESAFE_API_KEY` + `.dev-flow/jev.yaml`）：`G2R` 不進 `GATES`，`gate.py` 沒改；`g2r-shadow` 零網路、不建 transport、不寫 Jev durable ledger（不灌任何 n）。
- 不讀也不寫 `docs/dev/<slug>/` 的 `verdict:`；沒有 `route_taken`、沒有 live 開關。
- ~~main 的契約、SKILL、guide、hooks 都沒改。~~（歷史；已被取代：ADR 0004 accepted 後均已改，見頂部對照表。）
- G2R 常數**不進** `policy_fingerprint()`：G2R 題組還沒進 `jev-questions.json`，放進去會換掉 J1/J3/J5 既有 group 的 `questionset_hash`。G2R 用自己的 `g2r_fingerprint()`，寫進每筆紀錄的 `g2r_policy`。

## 4. 留給後面

- ~~G2R 題組（`g2_route` Choice + `risk` Score）進 `jev-questions.json` → 新 `questionset_hash`；那時再決定 C3 進 manifest 的方式。~~（**已被取代**：實際放在 `policy.G2R_QUESTIONS`、不進 `jev-questions.json`／manifest，各自 `g2r_fingerprint()`。）
- ~~從 4-spec／2-decision／`_stage3_impl.py` 自動組 case（本刀由呼叫端給 case）。~~（已完成：`g2auto.build_case`。）
- ~~P3-5 其餘面（`authored_by`／provenance、author≠approver 比對）；live 仍受 ADR 阻擋。~~（已完成並上線：ADR 0004 accepted、`G2_AUTO_LIVE = True`。）
