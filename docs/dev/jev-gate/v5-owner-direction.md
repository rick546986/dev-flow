---
title: jev-gate v5 — owner 裁決（2026-09-26）：人只參與討論，之後由 agent 完成
slug: jev-gate
status: 已記錄 owner 方向；本檔只記錄與規劃，不改程式、不改測試、不改 main 契約面；標「待 owner 核定」的數值都是候選值
date: 2026-09-26
base: research/jev-supermemory a65d78b（W7）
supersedes: roadmap draft-v4 §0 第 6、7、9 條的「上線路徑」語意（見 §7）
---

# jev-gate v5 owner direction

> **一句話**：人只在討論階段參與（G1 人審、Owner Calls 人裁），G2 改成 **fresh-context agent reviewer + 機械檢查自動審**；
> G3 **固定人審**，J5 AUTO_SHIP 退出目標；supermemory 正式放棄，改做「Jev 記憶重排序」。
> **本 PR 只改文件**：roadmap draft-v4 → draft-v5、本檔新增。L2 契約變更（G2 放寬）只寫 **ADR 草稿內容**（§3.6），ADR 本身留 owner 在 `main` 走流程。
> **作者 ≠ 審查者**：本檔是 agent 依 owner 裁決整理的落檔，不宣稱任何 reviewer PASS；候選數值一律「待 owner 核定」。

## 0. 分支與 SHA

| 項 | 值 |
|---|---|
| 基線 | `research/jev-supermemory` `a65d78b`（W7） |
| 本分支 | `claude/roadmap-v5-owner-decisions-g2eenl` |
| 改動 | `docs/dev/jev-gate/roadmap.md`（draft-v4 → draft-v5）、`docs/dev/jev-gate/v5-owner-direction.md`（新增） |
| main | **未動**；契約 §7／guide／SKILL／`_gate_consistency_impl.py` 都沒改 |
| 程式／測試 | **未動**；`GRADUATED=False`、`J5_LIVE_RATIFIED=False`、`J2_WINDOW_RATIFIED=False` 原樣 |

## 1. Owner 裁決原文摘要（2026-09-26）

目標：**人只參與討論，之後由 agent 完成。**

| # | 裁決 | 對 roadmap 的效果 |
|---|---|---|
| 1 | G1 維持人審，是討論的一部分；J2 永遠 shadow；Owner Calls 永遠人逐條裁決 | P3-3 從「遠期 AUTO_PASS」改成「永久 shadow 參考」；§0-7 改寫 |
| 2 | G2 自動審，**直接上線**（不並列影子方案）；放行 = fresh agent reviewer + 機械檢查；Jev `g2_route` 只分流 | 新 P3-5（契約／ADR／live）、P2-9（g2_route 分流）、P2-10（監控）；主線 |
| 3 | G3 固定人審；J5 AUTO_SHIP 從目標移除；J5 保留 shadow 參考 | P3-1 標「不再是上線路徑」；計算器保留；§16 J5 AUTO 驗收清單退役 |
| 4 | supermemory 正式放棄；新增「Jev 記憶重排序」 | §6／§14 改寫；新 P2-11；主線 |
| 5 | 重排優先級與 W8 之後 wave | §1 新增 v5 主線表與 W8–W12 |

硬約束（不變）：`GRADUATED=False`、雙閘門（`TYPESAFE_API_KEY` + `.dev-flow/jev.yaml` opt-in）、J3 不寫 verdict、21 次外部稽核不算 n、Demo verdict／Quiz gate／author≠approver／risk ceiling 不鬆。

## 2. G1：人審、J2 永遠 shadow

- G1 verdict 仍依契約 §7 審查者順序（適格人類 → fresh agent → owner 自審最後手段），v5 **不動 G1**。
- J2 的 `route_taken` 永遠 HUMAN（W5/W7 已實作 `j2_shadow_window_not_ratified`）；v5 把「未來 P3-3 J2 AUTO_PASS」**從路線上拿掉**，`J2_WINDOW_RATIFIED` 維持 False，不再規劃把它翻 True。
- J2 厚包（P2-8）保留作 G1 reviewer 的**參考提示**（哪個方案取捨證據薄），不產 verdict、不替 owner 回答 OC。
- rolling window 候選 50 保留在 `policy.py` 作歷史值，**不再是上線門檻**。

## 3. G2 自動審（主線）

### 3.1 放行條件（全部同時成立才 PASS）

1. **fresh-context agent reviewer PASS**：乾淨 context，只給 4-spec＋基準（契約 §7 G2 錨定義）＋回報格式；不給作者結論。
2. **機械檢查全過**：
   - `scripts/check-spec-gate.sh docs/dev/<slug>/4-spec.md`（六項形狀，含 C10 E2E entry point）；
   - `hooks/_stage3_impl.py <slug>` 結果為 N/A 或人類 ACCEPTED（Demo verdict 仍 human-only）；
   - `scripts/check-verdict-attestation.sh`（provenance 合法，§3.5）；
   - author≠approver 機械比對（§3.4）。
3. **沒有命中任何轉人條件**（§3.2）。

**Jev `g2_route` 不是放行必要條件**：它只負責把「不確定」丟給人。
- 有 `TYPESAFE_API_KEY` 且專案 opt-in：跑 `g2_route`，判 HUMAN 或信心不足 → 轉人；判 AUTO → 仍需上面 1+2+3。
- 沒有 key 或未 opt-in：**只靠 fresh agent + 機械檢查**；零網路；provenance 標 `routed_by: none`（§3.5）。
- Jev 失敗／逾時／breaker open／budget 用完 → 等同沒有 key（no-op），不擋、不放寬，轉人條件照判。

### 3.2 一律轉人（任一命中 → G2 回人審，fresh agent 結論只當 reviewer 參考）

| 條件 | 判定來源 | 備註 |
|---|---|---|
| Jev `g2_route` = HUMAN | `policy.route_g2`（P2-9 新增） | 只在有 key + opt-in 時存在 |
| Jev 信心不足 | `p(AUTO_PASS) < 門檻` | 門檻候選見 §5 C3，**待 owner 核定** |
| 命中 `risk_paths` | `policy.RISK_PATHS_DEFAULT`（A7）對 4-spec 宣告的 changed paths／R 列檔案 | 同 P2-4 機械 ceiling，不看任何分數 |
| risk score ≥ 2 | 有 Jev：`risk` Score（0–3，與 J5 同刻度）；無 Jev：4-spec `- Risk:` 映射（§5 C4） | 映射**待 owner 核定** |
| 有未裁決的 OC | `check-spec-gate.sh`／2-decision Owner Calls 無殘留 | OC 永遠人裁 |
| 需要 Demo verdict | `_stage3_impl.py` 回 `demo_request=requested`，或 Stage 3 觸發命中但人尚未填 Demo request | Demo verdict human-only 不動 |
| 修改 Jev runtime／questions／config 當次 | P1-G6 既有規則 | 同 J5 |
| provenance 不合法或 author==approver | §3.4／§3.5 | fail-closed：**不是 unverified 放行**，是不過 |

### 3.3 監控：只記錄、不擋單一 gate

| 監控 | 定義 | 動作 |
|---|---|---|
| (a) 隨機抽查 | 自動通過的 G2，依 `case_id` 雜湊決定性抽樣給人看（沿用 P2-5；agent 不能挑、不能關） | 人看完記 `audit_verdict: agree|disagree`；不回溯撤銷已過的 G2，disagree 走一般修迴圈 |
| (b) G2 放錯 | G3 退件（REQUEST_CHANGES／HOLD），且退件原因追得到規格（R/S 錯漏、DD 判錯、Verification Profile 漏層、spec 自相矛盾） | 記一筆 `g2_misrelease`，綁同 feature 的 G2 evaluation／verdict hash；追不到規格的 G3 退件不算 |
| (c) 退回人審 | rolling 放錯比例超過門檻 | 自動把 G2 模式切回人審（`g2_auto_state=reverted`）；**只有人**能再開（ratchet，不自動恢復） |

「只記錄不擋門」的意思是：監控本身不擋任何一次 G2；只有 (c) 的**模式切換**會讓之後的 G2 回人審。抽查比例與門檻見 §5 C1／C2。

G3 退件「原因追得到規格」由 **G3 的人類 reviewer** 在 7-review 退件理由勾 `root_cause: spec`（P2-10 新增欄），agent 不得代勾；這是監控資料正確性的前提。

### 3.4 author ≠ approver

- 寫 4-spec 的 agent 與審 G2 的 agent **必須不同**。
- 4-spec 頂欄新增 `authored_by: agent:<id>`（或 `human:<名>`）；G2 verdict 的 `attested_by: agent:<id>` 必須 ≠ `authored_by`，且不得是本 feature Stage 6 實作者（沿用 `gate-verdict-write.md` 鎖死 6「fresh agent 不得是實作者」）。
- 缺 `authored_by` → 不能證明四眼 → 轉人。
- 格式比對是 **provenance tripwire，不是身份驗證**（同 P1-G7）；換 session／換 id 字串不能證明真的是不同 agent，所以抽查（§3.3a）是補強。

### 3.5 G2 verdict provenance（對齊 P1-G7）

自動 G2 的 4-spec 頂欄：

```yaml
verdict: PASS
verdict_source: fresh_agent_reviewer      # P1-G7 既有 source class，不新增
attested_by: agent:<reviewer-id>          # 必須 ≠ authored_by
authored_by: agent:<author-id>            # v5 新增（§3.4）
g2_mode: auto                             # v5 新增：auto | human（轉人或已 reverted → human）
routed_by: jev:<evaluation_id>            # v5 新增：jev-routed；無 key / 未 opt-in / no-op → none
mechanical: sha256:<check 輸出摘要>       # v5 新增：check-spec-gate / stage3 / attestation 結果摘要 hash
```

對齊規則：

1. `verdict_source` 沿用 P1-G7 三類（`human_attested`／`fresh_agent_reviewer`／`owner_self_review`），**不為 Jev 新增 source**；Jev 永遠不是 verdict source、不寫 `verdict:`、不填 `attested_by`。
2. `routed_by` 只記「誰分流」，與「誰核准」分欄：`jev:<evaluation_id>` 讓 report 能回查 durable ledger 的 route；`none` 代表沒有 Jev 參與。
3. `g2_mode: auto` 而 `verdict_source ≠ fresh_agent_reviewer` 或 `attested_by` 不是 `agent:*` → **不合法**，G2 不過（fail-closed；與現行「人類 verdict 缺 provenance = unverified 但 gate 照關」不同，因為 auto 路徑沒有人可以兜底）。
4. 轉人後的 G2 照現行：`g2_mode: human`，人類 verdict 經 `devflow_gate.py` 寫 `human_attested`；`routed_by` 仍記當次 Jev evaluation（若有），供 report 分層。
5. report 分層：`g2_mode × verdict_source × routed_by`，不把 auto 與 human G2 混成同一率；G2 沒有 graduation n，這裡的分層只服務監控 (b)(c)。

### 3.6 ADR 草稿內容（L2；**本 PR 不改 main 契約面**，由 owner 在 main 走流程）

> 標題候選：`ADR-XXXX G2 自動審：fresh-context agent reviewer + 機械檢查；人只審 G1／G3`
> 狀態：proposed（agent 草擬，owner 決定是否送 Decide／L2）

**Context**：owner 2026-09-26 裁「人只參與討論，之後由 agent 完成」。G2 是契約寫得對不對；G3 仍人審可作下游安全網；Jev 不寫 verdict。

**Decision**：G2 的審查者順序對 G2 改為 **fresh-context reviewer Agent（+機械檢查）→ 適格人類 reviewer（轉人條件命中時）→ owner 自審（有記錄的最後手段）**；G1、G3 順序不變。

**要改的四個面（只放寬 G2，G1／G3 逐字不動）**：

| 面 | 現況 | 草稿改法 |
|---|---|---|
| 契約 `docs/dev/readme-contract-extract.md` §7 | 「審查者產生:G1/G2/G3 一律依序選 適格人類 reviewer → fresh-context reviewer Agent → owner 自審(有記錄的最後手段)」 | 拆兩句：「審查者產生:G1/G3 一律依序選 適格人類 reviewer → fresh-context reviewer Agent → owner 自審(有記錄的最後手段)。」＋「G2 審查者產生:依序選 fresh-context reviewer Agent(需機械檢查全過且未命中轉人條件)→ 適格人類 reviewer → owner 自審(有記錄的最後手段)。」G2 錨定義後新增「G2 轉人條件」列點（§3.2 表）與「G2 provenance」列點（§3.5） |
| 指南 `guides/guide-dev-flow.html#gates` | 「規則正本 · 審查者產生順序」逐字抄 §7 單句；G2 物質卡「新工作不例行等人」 | 逐字抄新兩句；G2 卡補「fresh agent + 機械檢查自動審；命中轉人條件 → 人審」；guide parity 錨同步 |
| `skills/dev-flow/SKILL.md` G2 段（:82-90 審查與 verdict、:88 author≠approver、階段表 G2 格） | G1/G2/G3 同一順序 | 同契約拆句；G2 階段格補「自動審（轉人條件見 #gates）」；author≠approver 補「G2 的 spec 作者 agent ≠ 審查 agent（`authored_by`／`attested_by`）」 |
| `hooks/_gate_consistency_impl.py` | `REVIEWER_SELECTION_CLAUSE = re.compile(r'審查者(?:產生|依序)[^。！？]*')` 要求唯一子句；`reviewer_selection_error()` 要求 human → agent → owner 位置遞增 | 新增 `G2_REVIEWER_SELECTION_CLAUSE = re.compile(r'G2審查者(?:產生|依序)[^。！？]*')`（在 flattened 文字上比對）與 `G2_REVIEWER_SELECTION_STEPS`（fresh-context reviewer Agent → 適格人類 → owner 自審）；原 `REVIEWER_SELECTION_CLAUSE` 改成 `(?<!G2)審查者(?:產生|依序)` 並要求原子句涵蓋 **G1/G3**、**不得**再含 G2；owner 自審「有記錄的最後手段」與否定詞檢查兩個子句都套；`4-spec.md` 頂註走 G2 子句、`2-decision.md`／`7-review.md` 頂註走原子句。selftest p4_ 加：G2 子句缺 → 紅；G2 子句把 G1 也放寬 → 紅；原子句仍列 G2 → 紅 |

**連帶實作面（ADR accepted 後才動；本 PR 不動）**：`_templates/4-spec.md` 頂欄加 `authored_by`／`g2_mode`／`routed_by`／`mechanical`；`scripts/check-verdict-attestation.sh` 驗 §3.5 規則 3；`scripts/devflow_gate.py` 新增 G2 auto 寫入路徑（只收 `fresh_agent_reviewer` + `agent:<id>` 且 ≠ `authored_by`，Jev 仍拒收）；`notes/design/gate-verdict-write.md` 鎖死 6 補 G2 auto 句；`check-gate-verdict-write.sh`／`check-methodology-corrections.sh` 同步；README 公開面 parity。

**Consequences**：G2 不再是日常人類等待；下游 G3 人審承接 G2 漏網風險，監控 (b)(c) 量化並可自動退回。**不變**：Demo verdict human-only、Quiz gate、risk ceiling、author≠approver、J3 不寫 verdict、Jev 不是 reviewer（`_gate_consistency_impl.py` 不新增 Jev step）。

**Alternatives considered**：維持人審 G2（違反 owner 目標）。owner 已選直接上線，本 ADR 不列 shadow 過渡方案。

## 4. G3 固定人審；J5 降為 shadow 參考

- G3 verdict 永遠人類親寫；J5 AUTO_SHIP 從目標移除。
- J5 shadow（enqueue／drain／label）保留，定位改為**提示人注意哪裡**（例如 `evidence_complete` 低、risk 高的層）；不產 verdict、不縮短人審。
- `gate.J5_LIVE_RATIFIED=False`、`GRADUATED=False` 維持；v5 **不規劃**把它們翻 True。
- P3-1 的 `n≥30`／Wilson `≥.85` 改標「**不再是上線路徑**」；`report.eligibility` 計算器保留（shadow 參考品質的量尺），但其結果不連到任何 live 開關。
- 21 次外部稽核仍不算 n。

## 5. 待 owner 核定的候選值

| # | 項目 | 候選值 | 理由 |
|---|---|---|---|
| **C1** | G2 自動通過抽查比例 | **20%**，依 `sha256(case_id)` 決定性抽樣（agent 不能挑）；前 **10** 筆自動 G2 **100%** 人看（burn-in） | P2-5 原候選 10–20% 取上緣：G2 是文件審，人看一份 4-spec 成本遠低於 G3 實跑；上線初期沒有 human-G2 baseline，burn-in 10 筆可快速暴露系統性盲點（例如 fresh agent 對 Verification Profile 的理解偏差），之後 20% 在每月十來個 feature 的量下仍約每週一筆，維持 fresh labels |
| **C2** | 退回人審門檻 | rolling **最近 20 筆**自動 G2 中 `g2_misrelease ≥ 3`（>10%）→ reverted；小樣本保護：前 10 筆內 `≥ 2` 即 reverted；抽查 `disagree` 且人確認為 spec 缺陷也計入 misrelease | G3 仍人審，G2 放錯的代價是返工而非出貨事故，容忍度可高於 J5 的 .85 floor；但 3/20 已代表系統性問題；小樣本規則避免前期連錯仍等滿 20 筆；計入抽查 disagree 讓 (a)(b) 用同一分子，不必等 G3 才發現。window 20 與 C1 的抽查節奏同量級，約一個月可滾完一輪 |
| **C3** | Jev `g2_route` 信心門檻 | `p(AUTO_PASS) ≥ 0.85`，低於即轉人 | 沿用已落檔 A3（J5 `.85`）同一數字，避免新增一組未校準常數；`g2_route` 只分流不放行，門檻偏嚴只會多轉人，不會多放行 |
| **C4** | 無 Jev 時的 risk 映射 | 4-spec `- Risk: high` → 視同 risk ≥2（轉人）；`medium`／`low` → <2 | 無 key 時沒有 Jev risk Score；spec 已有 `Risk:` 欄且 runtime 會讀；high 對應 Score 刻度 2–3（persisted/external、irreversible/security）最接近 |
| **C5** | 記憶重排序上線 eval 門檻 | 同一 locked eval set 上 **Recall@5 不降** 且 **MRR 提升 ≥ 0.05**，mandatory 項保留率 **100%** | 重排只該讓對的更前面，不該掉召回；0.05 是 `dev-memory.py eval` 既有指標可量出的最小有意義差；mandatory 100% 是硬約束不是統計目標 |
| **C6** | 記憶重排序候選池 | 原檢索 top **20** 送 Jev，回傳 top **5** | 候選池夠大才有重排空間，又不讓 packet 超 32k 單題限制（P0-2） |

每一項都**未校準**；改任一個（C3、C5、C6 會進 Jev manifest）= 新 `questionset_hash`，舊 group 不延續。

## 6. Jev 記憶重排序（主線，P2-11）

| 規則 | 內容 |
|---|---|
| 位置 | 既有 `memory/dev-memory.py ask` → `memory/agentmem/query.py`／`retrieval.py` 多路召回**之後**；Jev 只重新排序與挑選，**不寫記憶**（不呼叫 `remember`／`fact`／`know`／durable append） |
| 雙閘門 | 沒有 `TYPESAFE_API_KEY` 或專案未 opt-in（`.dev-flow/jev.yaml` 新 gate 名，候選 `MR`）→ **原樣回傳原檢索結果，零網路**；Jev 失敗／逾時／budget 用完同樣原樣回傳 |
| 不可移除 | `memory/agentmem/context.py` 開場必讀 context（identity／verified_truths／invariants／intents／conflicts／events／instructions）、current truth、invariants、conflicts、exact hits；`NO_RELIABLE_MATCH` 不得被重排成 OK。這些項**不送去重排**，直接釘在結果前段 |
| 去識別 | 送出的只有候選記憶的去識別摘要（沿用 P1-G1 packet builder privacy 規則）；不送 secret、credential、原始醫療資料；local replay store 同 gitignored 規則 |
| 預算 | 算進既有 daily cap（A2）；同一 query 重跑不重扣以外的 variant 照扣 |
| 上線條件 | `dev-memory.py eval` 檢索品質 eval 證明重排序優於原檢索（C5）；未達 → 保持 off，不做 shadow 以外的放行 |
| 不做 | 不引入 supermemory、不引入新 embedding backend、不改 SQLite schema |

## 7. 對 draft-v4 §0 的修訂關係

draft-v4 §0 寫「不再重投票」；v5 是 **owner 本人**的新裁決，覆蓋以下條目的上線語意，其餘條目不動：

| draft-v4 §0 | v5 |
|---|---|
| 6 J5 graduation floor | floor 保留作計算器定義，**不再是任何 live 路徑**；G3 固定人審 |
| 7 J2 保留、排在 J5 之後 | J2 **永遠 shadow**，沒有 AUTO_PASS 路徑 |
| 9 supermemory 現在不接（有重啟條件） | supermemory **正式放棄**，無重啟條件；改做 Jev 記憶重排序 |
| 10 既有控制不得被繞過 | 不變；G2 自動審是**明文 L2 契約變更**（§3.6），不是暗中繞過 |
