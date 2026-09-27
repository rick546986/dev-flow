---
status: accepted
date: 2026-09-27
source: research/jev-supermemory `docs/dev/jev-gate/v5-owner-direction.md` §3.6 ADR 草稿(吸收 §3.2 轉人條件、§3.3 誤放率記錄);owner 2026-09-27 授權為 L2 契約變更
topics:
  - g2-auto-review
supersedes: []
superseded_by: null
---

# 0004. G2(Stage 4 Spec)改為自動審:fresh-context agent reviewer + 機械檢查;人只審 G1/G3

> 晉升條件(三條件**全中**才立此檔,否則留在 2-decision 就好):
> 難逆轉 + 反直覺 + 真 trade-off。
>
> 本案三條全中:G2 放行一旦改由 agent 做,之後每一份 4-spec 的 provenance 都帶
> `g2_mode: auto`,要退回得連 report 分層與既有 verdict 一起處理(難逆轉);
> 「放行不需要人、但分流器 Jev 又不能放行」與直覺相反(反直覺);
> 換到 G2 不再是日常人類等待,付出的是 G2 漏網風險全部壓給下游 G3 人審(真 trade-off)。
>
> **狀態:Accepted(owner 2026-09-27)。** 本 ADR 只記錄決策;契約句、指南、SKILL、
> `_gate_consistency_impl.py`、模板與腳本的改動另開 PR(見〈實作面〉),
> 在那之前 main 上的 G2 仍照現行契約 §7 人審。

## Context

owner 2026-09-26 裁「**人只參與討論,之後由 agent 完成**」:G1(Decide)是討論的一部分,
維持人審;Owner Calls 永遠人逐條裁決;G3(Review)固定人審。G2 審的是「契約寫得對不對」
—— 4-spec 的形狀大半已有機械檢查可驗,剩下的判斷交給乾淨 context 的 reviewer agent,
而 G3 人審仍在下游當安全網。

現行契約 §7 對 G1/G2/G3 一律同一順序:適格人類 reviewer → fresh-context reviewer Agent →
owner 自審(有記錄的最後手段)。要讓 G2 不再例行等人,必須明文改契約(L2),
不能靠暗中繞過。

## Decision

### 1. G2 審查者順序

G2 改為:**fresh-context reviewer Agent(需機械檢查全過且未命中轉人條件)→
適格人類 reviewer(轉人條件命中時)→ owner 自審(有記錄的最後手段)**。
G1、G3 的審查者順序**逐字不動**。

### 2. 放行條件(全部同時成立才 PASS)

1. **fresh-context agent reviewer PASS**:乾淨 context,只給 4-spec + 基準(契約 §7 G2 錨定義)
   + 回報格式;不給作者結論。
2. **機械檢查全過**:
   - `scripts/check-spec-gate.sh docs/dev/<slug>/4-spec.md`(六項形狀,含 C10 E2E entry point);
   - `hooks/_stage3_impl.py <slug>` 結果為 N/A 或人類 ACCEPTED(Demo verdict 仍 human-only);
   - `scripts/check-verdict-attestation.sh`(provenance 合法,見 §5);
   - author ≠ approver 機械比對(見 §4)。
3. **沒有命中任何轉人條件**(見 §3)。

**Jev `g2_route`(候選 gate 名 `G2R`)只分流,不是放行條件。** 它只負責把「不確定」丟給人:

- 有 `TYPESAFE_API_KEY` 且專案 opt-in(`.dev-flow/jev.yaml`):跑 `g2_route`;判 HUMAN 或信心不足
  → 轉人;判 AUTO → 仍需上面 1 + 2 + 3。
- 沒有 key 或未 opt-in:**只靠 fresh agent + 機械檢查**;零網路;provenance 標 `routed_by: none`。
- Jev 失敗／逾時／breaker open／budget 用完 → 等同沒有 key(no-op),不擋、不放寬,轉人條件照判。

### 3. 一律轉人(任一命中 → G2 回人審,fresh agent 結論只當 reviewer 參考)

| 條件 | 判定來源 | 備註 |
|---|---|---|
| Jev `g2_route` = HUMAN | `policy.route_g2` | 只在有 key + opt-in 時存在 |
| Jev 信心不足 | `p(AUTO_PASS) < 0.85` | owner 定案 C3:≥ 0.85 才走自動審 |
| 命中 `risk_paths` | `policy.RISK_PATHS_DEFAULT` 對 4-spec 宣告的 changed paths／R 列檔案 | 機械 ceiling,不看任何分數 |
| 4-spec **沒宣告任何檔案路徑** | 同上來源為空 | G2 階段還沒有 diff 可推 changed paths,無從判定 → **視同命中 `risk_paths`**(fail-closed,不當成「沒命中」) |
| risk ≥ 2 | 有 Jev:`risk` Score(0–3,與 J5 同刻度);無 Jev:4-spec `- Risk:` 映射 | owner 定案 C4:無 Jev 時 `Risk: high` 視同 ≥ 2;`medium`／`low` 視同 < 2 |
| 有未裁決的 Owner Call | `check-spec-gate.sh`／2-decision Owner Calls 無殘留 | Owner Calls 永遠人裁 |
| 需要 Demo verdict | `_stage3_impl.py` 回 `demo_request=requested`,或 Stage 3 觸發命中但人尚未填 Demo request | Demo verdict human-only 不動 |
| 當次修改 Jev runtime／questions／config | 既有 P1-G6 規則 | 同 J5 |
| 缺 `authored_by` | 4-spec 頂欄 | 無法證明四眼 → 轉人 |
| provenance 不合法或 author == approver | §4／§5 | fail-closed:**不是 unverified 放行,是不過** |

### 4. author ≠ approver

- 寫 4-spec 的 agent 與審 G2 的 agent **必須不同**。
- 4-spec 頂欄新增 `authored_by: agent:<id>`(或 `human:<名>`);G2 verdict 的 `attested_by: agent:<id>`
  必須 ≠ `authored_by`,且不得是本 feature Stage 6 實作者(沿用 `gate-verdict-write.md` 鎖死 6)。
- 格式比對是 **provenance tripwire,不是身份驗證**;換 session／換 id 字串不能證明真的是不同 agent,
  補強靠下游 G3 固定人審。

### 5. G2 verdict provenance

自動 G2 的 4-spec 頂欄:

```yaml
verdict: PASS
verdict_source: fresh_agent_reviewer      # 既有 source class,不新增
attested_by: agent:<reviewer-id>          # 必須 ≠ authored_by
authored_by: agent:<author-id>            # 新增
g2_mode: auto                             # 新增:auto | human(命中轉人條件 → human)
routed_by: jev:<evaluation_id>            # 新增:jev-routed;無 key／未 opt-in／no-op → none
mechanical: sha256:<check 輸出摘要>       # 新增:check-spec-gate / stage3 / attestation 結果摘要 hash
```

1. `verdict_source` 沿用既有三類(`human_attested`／`fresh_agent_reviewer`／`owner_self_review`),
   **不為 Jev 新增 source**;Jev 永遠不是 verdict source、不寫 `verdict:`、不填 `attested_by`。
2. `routed_by` 只記「誰分流」,與「誰核准」分欄。
3. `g2_mode: auto` 而 `verdict_source ≠ fresh_agent_reviewer` 或 `attested_by` 不是 `agent:*`
   → **不合法,G2 不過**(auto 路徑沒有人可以兜底,所以 fail-closed)。
4. 轉人後的 G2 照現行:`g2_mode: human`,人類 verdict 經 `devflow_gate.py` 寫 `human_attested`;
   `routed_by` 仍記當次 Jev evaluation(若有)。
5. report 分層:`g2_mode × verdict_source × routed_by`,不把 auto 與 human G2 混成同一率。

### 6. 放行後不需人工介入;G2 誤放率只記錄

- **不做人工抽查、不因誤放率自動退回人審**(owner 2026-09-26 移除原 C1 抽查、C2 自動退回設計);
  沒有模式切換、沒有 `g2_auto_state=reverted`。
- **G2 誤放**:G3 退件(REQUEST_CHANGES／HOLD),且退件原因追得到規格(R/S 錯漏、DD 判錯、
  Verification Profile 漏層、spec 自相矛盾)→ 記一筆 `g2_misrelease`,綁同 feature 的 G2
  evaluation／verdict hash;追不到規格的 G3 退件不算。
- 「追得到規格」由 **G3 的人類 reviewer** 在 7-review 退件理由勾 `root_cause: spec`;agent 不得代勾。
  這是 G3 本來就由人做的退件判斷,不是 G2 放行後的額外人工步驟。
- **G2 誤放率** = `g2_misrelease` 筆數 ÷ 已走到 G3 的自動 G2 筆數。**只進 report**:
  不阻擋任何 G2、不自動退回、不觸發抽查。要不要因數字改規則,由 owner 另行裁決。

### 7. 不變

- **G1、G3 維持人審**;審查者順序逐字不動。J2 永遠 shadow;J5 降為 shadow 參考。
- **Demo verdict human-only**、**Quiz gate**、**risk ceiling**、**author ≠ approver** 不鬆。
- **J3 不寫 verdict**;**Jev 不是 reviewer**(`_gate_consistency_impl.py` 不新增 Jev step)。
- `GRADUATED=False`、`J5_LIVE_RATIFIED=False`、`J2_WINDOW_RATIFIED=False` 原樣;本 ADR 不翻任何 live 開關。

## Considered Options

**①維持 G2 人審。** 換到「每份 spec 都有人看過」。否決理由:違反 owner「人只參與討論,
之後由 agent 完成」的目標;G2 的形狀判斷大半已可機械驗,人審在這裡主要是排隊成本。

**②先並列 shadow 方案、累積 n 再上線。** 換到「上線前有數字」。否決理由:owner 已選直接上線;
G3 固定人審已是下游安全網,且誤放率照樣記錄,不需要再多一段 shadow 過渡。

**③讓 Jev `g2_route` AUTO 直接放行。** 換到「少一個 agent 呼叫」。否決理由:Jev 不是 reviewer、
不寫 verdict 是既有不變量;Jev 只能把不確定的丟給人,不能替人或 reviewer 說 PASS。

**④保留人工抽查／誤放達門檻自動退回人審(原 C1/C2)。** 換到「放行後仍有人看」。否決理由:
owner 2026-09-26 明確移除 —— 放行後需要人工介入就等於 G2 沒有真的交給 agent;誤放風險改由 G3 承接並量化。

## Consequences

**換到:**
- G2 不再是日常人類等待;人只出現在 G1、Owner Calls、G3 與命中轉人條件的 G2。
- 放行門檻有機械面(spec 形狀、Stage 3、provenance、四眼比對)兜底,不只靠一個 agent 的判斷。
- 沒有 Jev key 的採用專案照樣能用(零網路,只靠 fresh agent + 機械檢查)。
- G2 漏網有數字可看(誤放率分層進 report),不是憑感覺。

**付出:**
- G2 漏網的規格錯誤要到 G3 才被人抓到,返工成本比在 G2 擋下高。
- author ≠ approver 只是格式 tripwire,無法證明兩個 id 背後真的是不同 agent;補強只有 G3 人審。
- 誤放率只記錄不阻擋:數字變差時不會自動收緊,要 owner 看 report 再裁。
- 契約 §7 從一句拆成兩句,guide parity、SKILL、gate-consistency 都要跟著改,且要有 selftest 釘住
  「G2 放寬沒有連帶放寬 G1/G3」。

## 實作面(本 ADR 不動;另開 PR)

只放寬 G2,G1/G3 逐字不動:

| 面 | 改法 |
|---|---|
| 契約 `docs/dev/readme-contract-extract.md` §7 | 審查者產生句拆兩句:「審查者產生:G1/G3 一律依序選 適格人類 reviewer → fresh-context reviewer Agent → owner 自審(有記錄的最後手段)。」+「G2 審查者產生:依序選 fresh-context reviewer Agent(需機械檢查全過且未命中轉人條件)→ 適格人類 reviewer → owner 自審(有記錄的最後手段)。」G2 錨定義後新增「G2 轉人條件」與「G2 provenance」列點 |
| 指南 `guides/guide-dev-flow.html#gates` | 逐字抄新兩句;G2 卡補「fresh agent + 機械檢查自動審;命中轉人條件 → 人審」;guide parity 錨同步 |
| `skills/dev-flow/SKILL.md` G2 段 | 同契約拆句;G2 階段格補「自動審(轉人條件見 #gates)」;author ≠ approver 補 `authored_by`／`attested_by` |
| `hooks/_gate_consistency_impl.py` | 新增 G2 審查者子句與步驟序;原子句只涵蓋 G1/G3、不得再含 G2;selftest 加:G2 子句缺 → 紅、G2 子句把 G1 也放寬 → 紅、原子句仍列 G2 → 紅 |
| 連帶 | `_templates/4-spec.md` 頂欄加 `authored_by`／`g2_mode`／`routed_by`／`mechanical`;`check-verdict-attestation.sh` 驗 §5 規則 3;`devflow_gate.py` G2 auto 寫入路徑(只收 `fresh_agent_reviewer` + `agent:<id>` 且 ≠ `authored_by`,Jev 仍拒收);`gate-verdict-write.md` 鎖死 6 補 G2 auto 句;`check-gate-verdict-write.sh`／`check-methodology-corrections.sh` 同步;Jev `policy.route_g2` 與誤放率 report;README 公開面 parity |
