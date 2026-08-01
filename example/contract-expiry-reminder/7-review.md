---
feature: contract-expiry-reminder
stage: 7-review
status: shipped
owner: <reviewer-a>         # reviewer(≠實作 owner <owner>)
updated: 2026-07-23
---

# 7. 驗證

## Coverage Matrix
| S-id | 測試 | 狀態 |
|---|---|---|
| S-1 | `TestExpiring_S1`(Go) | ✅ |
| S-2 | `ExpiringContractsCard "S2 empty"`(vitest) | ✅ |
| S-3 | `ExpiringContractsCard "S3 navigate"`(vitest) | ✅ |
| S-4 | `TestRenewalStatus_S4`(Go) | ✅ |
| S-5 | `TestRenewalStatus_S5_ViewDoesNotComplete`(Go) | ✅ |
| S-6 | `ExpiringContractsCard "S6 renewed-only-manager"`(vitest) | ✅ |
| 既有測試套件(回歸) | `go test ./... && npm test` | ✅ |

## Verification Evidence
(以下為**示範值** —— 實案由執行清單 2c 的 Final Fresh Run 產出:Source SHA 必須
= 當下 `git rev-parse HEAD`,並跑
`scripts/devflow-evidence-gauntlet.sh 7-review.md --source-sha $(git rev-parse HEAD) --review-file`
全綠才算完成。)
- Source SHA: f92c1d5(示範值 = T-7 commit;實案填 Final Fresh Run 當下 HEAD)
- Final Fresh Run ID: 2026-07-23T1710+08-r1(示範值)
- Entry point: `go test ./... && npm test && npx playwright test`
- Toolchain: go.mod + package-lock.json(pinned;go1.22 / node20)

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Full test suite | `go test ./... && npm test` | pass | 58 passed, 0 failed | |
| e2e | `npx playwright test` | pass | 3 passed(S-1/S-3 flow 含登入) | |
| Types/compile | `tsc --noEmit` | pass | 0 errors in 14 files | |
| Changed-line coverage | `go test -coverprofile` + `vitest --coverage` | pass | 76/76 changed lines covered | |
| Real execution | `curl -s -X PATCH :8080/contracts/C.id/status` | pass | HTTP 200,狀態=等待法務,歷程 1 筆 | |
| Rollback rehearsal | `make migrate-down && make migrate-up`(staging snapshot) | pass | down/up 各 1 步 clean,0 orphan rows | |
| Mutation | | unverified | | 示範案例未跑 mutation 工具;實案依 4-spec Verification Profile 的 Required layers 決定 |
| Race/stress | | n-a | | 無並發寫入路徑變更(狀態更新走單一交易) |

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
| 看過/任何 GET 路徑不得改狀態(S-5;1-discussion Q4) | `TestRenewalStatus_S5_ViewDoesNotComplete`(歷程零新增) | pass |
| 非主管不得標「已續約」(S-6;1-discussion Q5) | `TestRenewalStatus_S4` 權限分支 + vitest `"S6 renewed-only-manager"` | pass |
| 不自動轉移狀態、不逾時升級(Out of Scope) | `grep -rn "cron" internal/` → 0 hits | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)
(本例為手動實作 —— 無 dev-run ledger;依模板規則本節留白,不虛構模型歷史。)

## 現象證據(逐 S,對照 4-spec 的觀測欄)
| S-id | 觀測方式(引 4-spec) | reviewer 實跑證據 | 相符? |
|---|---|---|---|
| S-1 | `<owner>` dashboard 到期卡片；C 與「10 天」；C(`end_date = today + 10d`,未續約) | reviewer 以擁有合約 C 的 `<owner>` 登入 dashboard,卡片顯示 C 與「10 天」 | ✅ |
| S-2 | `<owner>` dashboard 到期卡片；「近期無到期合約」且無錯誤；名下無 30 天內到期未續約合約 | reviewer 以無符合合約的 `<owner>` 登入,看到「近期無到期合約」且無錯誤畫面 | ✅ |
| S-3 | C 那一列與瀏覽器 URL；`/contracts/C.id` 且顯示 C 詳情；S-1 的 C | reviewer 點擊可見的 C,URL 為 `/contracts/C.id` 並顯示 C 詳情 | ✅ |
| S-4 | C 列狀態欄/下一步欄與狀態歷程；標記後顯示「等待法務」「等法務回覆條款」與時間、歷程多一筆；用 S-1 的合約 C | reviewer 以 `<owner>` 對 C 標「等待法務」,列即顯示狀態/下一步/最後動作時間;詳情頁歷程新增一筆(`<owner>`、時間、未處理→等待法務) | ✅ |
| S-5 | C 列狀態欄與狀態歷程;兩次開啟後仍「未處理」且歷程零新增;開 dashboard 兩次不標記 | reviewer 開 dashboard 兩次未做標記,C 仍「未處理」,`CountStatusHistory(C)` 回 0 | ✅ |
| S-6 | C 列狀態選單與狀態欄;「已續約」灰階、提示字樣、狀態仍「已聯絡供應商」;非主管帳號對 S-4 的 C | reviewer 以非主管 `<owner>` 開狀態選單,「已續約」灰階並顯示「已續約僅主管可標」,狀態不變、歷程零新增 | ✅ |

## Operational Walkthrough
(reviewer 以各 S 的 Operational Context 為腳本親自走一遍「人的工作」;逐列檢查六條:
技術上通過但人無法完成工作 / 看得到但沒有決策權 / 系統把等待誤標為完成 /
系統外動作無法追蹤 / 使用者中斷後無法恢復 / 資訊過期、缺漏或多人同時操作)

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1 | 負責業務 | 登入第一眼決定今天跟催哪件 | 開 dashboard 看到期卡片 | — | 多件同時到期逐列可見,含狀態與下一步 | ✅ 人能完成工作 |
| S-2 | 負責業務 | 確認今天不需跟催 | 開 dashboard 見空狀態 | — | 空狀態與錯誤呈現可區分 | ✅ |
| S-3 | —(純導覽) | — | — | — | — | 不適用(無 Operational Context,理由見 4-spec S-3) |
| S-4 | 負責業務 | 把「進行到哪、在等誰」移進系統 | 對 C 標「等待法務」 | Email 合約給法務 | 狀態停「等待法務」持續顯示,系統不自動轉移、不視為完成;標到一半關頁重開,狀態為最後成功標記值 | ✅ 等待未被誤標完成;中斷可恢復 |
| S-4 | 負責業務 | 法務回覆後推進續約 | 改標「等待主管」→「已聯絡供應商」 | 電話聯絡供應商窗口 | 系統外動作以「已聯絡供應商 + 誰 + 時間」留痕;改派後新業務讀歷程即可接手 | ✅ 系統外動作可追蹤、交接不斷線 |
| S-5 | 負責業務(下游:主管/接手業務) | 看過提醒不背「已處理」 | 開 dashboard 兩次,不標記 | — | 「未處理」持續顯示直到明確標記;歷程零新增即為證據 | ✅ 無「已讀即處理」假象 |
| S-6 | 負責業務(嘗試者)/業務主管(有權者) | 結案定案權留在主管 | 嘗試標「已續約」被拒(灰階 + 提示) | LINE/口頭通知主管來標 | 狀態停「已聯絡供應商」直到主管動作 | ✅ 不暗示不存在的權限;被拒後知道找誰 |

## Standards Axis
- F-1 🟡 `internal/handler/contract.go:41` | handler 未設 context timeout,慢查詢會掛住
  dashboard | 建議:`context.WithTimeout(ctx, 2s)`,下個 fast-lane 補。

## Spec Axis
- R-1 符合(S-1/S-2 綠;空狀態文案同 spec)。
- R-2 符合(S-3 綠)。
- R-3 符合(S-4/S-5/S-6 綠;歷程含誰/何時/舊→新,「已續約」僅主管與看過零變更行為同 spec)。
- D-1 已如實記錄,判定正確(不動 R/S,屬 L1;避開的是覆蓋索引 migration,
  `renewal_status` migration 為 4-spec Dependencies 明載的計畫內變更)。

## 變更架構圖

```text
[Dashboard.tsx]
       |
       v
[ExpiringContractsCard.tsx] -- click --> [/contracts/:id 詳情 + 歷程時間軸]
       |         |
       |         +-- mark status --> [PATCH /contracts/:id/status]
       v                                |
[GET /contracts/expiring]               v
       |                         [status handler] -- 權限檢查:已續約僅主管
       v                                |
[handler] --> [service] --> [repo]      v
                              |  [status repo] --> [renewal_status 欄 + 歷程表]
                              +--> [idx_contracts_end_date]
```

## Diff(merge-base(develop)..HEAD,逐檔折疊)

<details>
<summary title="+6/-1; Expiring handler"><code>internal/handler/contract.go</code> (+6/-1; <code>Expiring</code>)</summary>
<pre><span class="del">-func (h *Handler) ListContracts(w http.ResponseWriter, r *http.Request) {</span>
<span class="add">+func (h *Handler) Expiring(w http.ResponseWriter, r *http.Request) {</span>
<span class="add">+    ownerID := auth.OwnerID(r.Context())</span>
<span class="add">+    contracts, err := h.contracts.ListExpiring(r.Context(), ownerID, time.Now())</span>
<span class="add">+    if err != nil { h.errors.Write(w, err); return }</span>
<span class="add">+    writeJSON(w, http.StatusOK, contracts)</span>
<span class="add">+}</span></pre>
</details>

<details>
<summary title="+6/-1; ListExpiring service"><code>internal/service/contract.go</code> (+6/-1; <code>ListExpiring</code>)</summary>
<pre><span class="del">-func (s *ContractService) List(ctx context.Context, ownerID string) ([]Contract, error) {</span>
<span class="add">+func (s *ContractService) ListExpiring(ctx context.Context, ownerID string, today time.Time) ([]Contract, error) {</span>
<span class="add">+    cutoff := today.AddDate(0, 0, 30)</span>
<span class="add">+    rows, err := s.repo.FindExpiring(ctx, ownerID, today, cutoff)</span>
<span class="add">+    if err != nil { return nil, fmt.Errorf("find expiring contracts: %w", err) }</span>
<span class="add">+    return rows, nil</span>
<span class="add">+}</span></pre>
</details>

<details>
<summary title="+5/-1; FindExpiring query"><code>internal/repo/contract.go</code> (+5/-1; <code>FindExpiring</code>)</summary>
<pre><span class="del">-const listContracts = `SELECT * FROM contracts WHERE owner_id = $1`</span>
<span class="add">+const findExpiring = `SELECT * FROM contracts</span>
<span class="add">+  WHERE owner_id = $1 AND renewed_at IS NULL</span>
<span class="add">+    AND end_date &gt;= $2 AND end_date &lt;= $3</span>
<span class="add">+  ORDER BY end_date ASC`</span>
<span class="add">+func (r *ContractRepo) FindExpiring(ctx context.Context, ownerID string, from, to time.Time) ([]Contract, error)</span></pre>
</details>

<details>
<summary title="+12/-1; card list, empty state, navigation, status cell"><code>src/components/ExpiringContractsCard.tsx</code> (+12/-1; <code>ExpiringContractsCard</code>)</summary>
<pre><span class="del">-export const ExpiringContractsCard = () =&gt; null</span>
<span class="add">+export function ExpiringContractsCard({ contracts, viewer, navigate }: Props) {</span>
<span class="add">+  if (contracts.length === 0) return &lt;p&gt;近期無到期合約&lt;/p&gt;</span>
<span class="add">+  return &lt;section aria-label="近期到期合約"&gt;</span>
<span class="add">+    {contracts.map((contract) =&gt; (</span>
<span class="add">+      &lt;row key={contract.id}&gt;</span>
<span class="add">+        &lt;button onClick={() =&gt; navigate(`/contracts/${contract.id}`)}&gt;</span>
<span class="add">+          {contract.name} · {contract.daysRemaining} 天&lt;/button&gt;</span>
<span class="add">+        &lt;StatusCell status={contract.status} nextStep={contract.nextStep}</span>
<span class="add">+          lastActionAt={contract.lastActionAt}</span>
<span class="add">+          canMarkRenewed={viewer.isManager} /&gt; {/* 非主管:「已續約」灰階+提示 */}</span>
<span class="add">+      &lt;/row&gt;))}</span>
<span class="add">+  &lt;/section&gt; }</span></pre>
</details>

<details>
<summary title="+2/-1; dashboard card mount"><code>src/pages/Dashboard.tsx</code> (+2/-1; <code>Dashboard</code>)</summary>
<pre><span class="del">-return &lt;main&gt;&lt;/main&gt;</span>
<span class="add">+return &lt;main&gt;</span>
<span class="add">+  &lt;ExpiringContractsCard contracts={expiringContracts} navigate={navigate} /&gt;&lt;/main&gt;</span></pre>
</details>

<details>
<summary title="+8/-1; S-1/S-3 browser flow"><code>e2e/expiring-contracts.spec.ts</code> (+8/-1; S-1/S-3)</summary>
<pre><span class="del">-test.todo('contract expiry reminder')</span>
<span class="add">+test('S-1 S-3 owner sees and opens an expiring contract', async ({ page }) =&gt; {</span>
<span class="add">+  await loginAs(page, ownerWithContractC)</span>
<span class="add">+  await page.goto('/dashboard')</span>
<span class="add">+  await expect(page.getByText('C')).toBeVisible()</span>
<span class="add">+  await expect(page.getByText('10 天')).toBeVisible()</span>
<span class="add">+  await page.getByText('C').click()</span>
<span class="add">+  await expect(page).toHaveURL('/contracts/C.id')</span>
<span class="add">+})</span></pre>
</details>

<details>
<summary title="+10/-0; renewal_status enum + history table"><code>migrations/0007_renewal_status.sql</code> (+10/-0; <code>renewal_status</code>)</summary>
<pre><span class="add">+CREATE TYPE renewal_status AS ENUM</span>
<span class="add">+  ('未處理','等待法務','等待主管','已聯絡供應商','已續約','不續約');</span>
<span class="add">+ALTER TABLE contracts</span>
<span class="add">+  ADD COLUMN renewal_status renewal_status NOT NULL DEFAULT '未處理';</span>
<span class="add">+CREATE TABLE contract_status_history (</span>
<span class="add">+  contract_id  UUID REFERENCES contracts(id),</span>
<span class="add">+  actor_id     UUID NOT NULL,</span>
<span class="add">+  changed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),</span>
<span class="add">+  from_status  renewal_status NOT NULL,</span>
<span class="add">+  to_status    renewal_status NOT NULL);</span></pre>
</details>

<details>
<summary title="+14/-0; MarkStatus + StatusHistory handlers"><code>internal/handler/contract_status.go</code> (+14/-0; <code>MarkStatus</code>, <code>StatusHistory</code>)</summary>
<pre><span class="add">+func (h *Handler) MarkStatus(w http.ResponseWriter, r *http.Request) {</span>
<span class="add">+    actor := auth.Actor(r.Context())</span>
<span class="add">+    req := decodeStatusRequest(r) // to_status(值域固定 6 值)</span>
<span class="add">+    if req.To == "已續約" &amp;&amp; !actor.IsManager {</span>
<span class="add">+        h.errors.Write(w, ErrManagerOnly) // S-6:已續約僅主管可標</span>
<span class="add">+        return</span>
<span class="add">+    }</span>
<span class="add">+    result, err := h.status.Mark(r.Context(), req.ContractID, actor.ID, req.To)</span>
<span class="add">+    if err != nil { h.errors.Write(w, err); return }; writeJSON(w, http.StatusOK, result) }</span>
<span class="add">+func (h *Handler) StatusHistory(w http.ResponseWriter, r *http.Request) {</span>
<span class="add">+    // GET 路徑:唯讀,零狀態寫入(S-5:看過 ≠ 處理)</span>
<span class="add">+    rows, err := h.status.History(r.Context(), pathParam(r, "id"))</span>
<span class="add">+    if err != nil { h.errors.Write(w, err); return }</span>
<span class="add">+    writeJSON(w, http.StatusOK, rows) }</span></pre>
</details>

<details>
<summary title="+16/-0; Mark 交易 + 歷程查詢"><code>internal/repo/contract_status.go</code> (+16/-0; <code>Mark</code>, <code>CountStatusHistory</code>)</summary>
<pre><span class="add">+const markStatus = `UPDATE contracts SET renewal_status = $2,</span>
<span class="add">+  last_action_at = now() WHERE id = $1 RETURNING renewal_status`</span>
<span class="add">+const insertHistory = `INSERT INTO contract_status_history</span>
<span class="add">+  (contract_id, actor_id, from_status, to_status) VALUES ($1,$2,$3,$4)`</span>
<span class="add">+const countHistory = `SELECT COUNT(*) FROM contract_status_history</span>
<span class="add">+  WHERE contract_id = $1`</span>
<span class="add">+func (r *ContractStatusRepo) Mark(ctx context.Context, id, actorID string,</span>
<span class="add">+    to Status) (StatusResult, error) {</span>
<span class="add">+    // 單一交易:更新狀態 + 歷程一筆(誰/何時/舊→新)</span>
<span class="add">+    return r.inTx(ctx, func(tx Tx) (StatusResult, error) {</span>
<span class="add">+        prev := tx.CurrentStatus(id)</span>
<span class="add">+        return tx.MarkAndLog(id, actorID, prev, to) }) }</span>
<span class="add">+func (r *ContractStatusRepo) CountStatusHistory(ctx context.Context,</span>
<span class="add">+    id string) (int, error)</span>
<span class="add">+func (r *ContractStatusRepo) History(ctx context.Context,</span>
<span class="add">+    id string) ([]StatusEvent, error)</span></pre>
</details>

## Verdict
**PASS**(F-1 為 🟡,開 fast-lane follow-up,不擋出貨)

## Exit Checklist
- [x] Quiz(不可逆改動必做;其餘 full lane 選配,fast 免):本次新增對外 API endpoint(`GET /contracts/expiring`、`PATCH /contracts/:id/status`)與 `renewal_status` migration,shipped 後即成對外契約/schema,移除屬破壞性變更 → 不可逆,Quiz 必做 —— AI 出 5 題(30 天定義來源/為何不做 email/D-1 為何不加索引/空狀態行為/「已續約」為何僅主管),`<reviewer-a>` 全對
- [x] PR #142 → develop
- [x] 4-spec delta 已併入 `docs/specs/contracts.md`(R-1~R-3 貼入,標 source)
- [x] STATUS.md 已更新為 shipped
- [x] 7-review frontmatter status: shipped;上游 artifact 保留 approved(各自 gate 核准紀錄,依 7-review 模板 Exit 規則)
- [x] 7-review.html 已產生(含變更架構圖 + diff 折疊)
- [x] feature branch 已刪
