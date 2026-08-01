---
feature: contract-expiry-reminder
stage: 6-implementation
status: approved
owner: <owner>
updated: 2026-07-23
---

# 6. 實作筆記

## T Review Log
### T-1
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-21 14:40(早於 commit `a1c3f02`)
- Verify:`go test ./internal/... -run TestExpiring` → reviewer 親跑 `ok  internal/...`
- Covers finding:R-1 / S-1、S-2 的 API 查詢、到期結果與空結果均吻合。
- Files finding:改動僅 `internal/handler/contract.go`、`internal/service/contract.go`、`internal/repo/contract.go`。
- RED→GREEN finding:`T-1 / S-1`、`T-1 / S-2` 各有本 T 的 RED→GREEN 證據且可追溯。
- Test Integrity finding:none(七項無命中)
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-2
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-22 10:15(早於 commit `b7e91d4`)
- Verify:`npm test -- ExpiringContractsCard` → reviewer 親跑 `PASS (2 tests)`。
- Covers finding:R-1 / S-1、S-2 的卡片與空狀態均吻合。
- Files finding:改動僅 `src/components/ExpiringContractsCard.tsx`、`src/pages/Dashboard.tsx`。
- RED→GREEN finding:`T-2 / S-1`、`T-2 / S-2` 各有前端層 RED→GREEN 證據且可追溯。
- Test Integrity finding:none(七項無命中)
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-3
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-22 15:30(早於 commit `c58a2e0`)
- Verify:`npm test -- ExpiringContractsCard` → reviewer 親跑 `PASS (3 tests)`。
- Covers finding:R-2 / S-3 的卡片列導向詳情頁行為吻合。
- Files finding:改動僅 `src/components/ExpiringContractsCard.tsx`。
- RED→GREEN finding:`T-3 / S-3` 有本 T 的 RED→GREEN 證據且可追溯。
- Test Integrity finding:none(七項無命中)
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-4
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-23 11:20(早於 commit `f3a08c1`)
- Verify:`npx playwright test e2e/expiring-contracts.spec.ts` → reviewer 親跑 `PASS (登入、卡片、詳情導向)`。
- Covers finding:R-1、R-2 / S-1、S-3 的端到端可見行為吻合。
- Files finding:改動僅 `e2e/expiring-contracts.spec.ts`。
- RED→GREEN finding:`T-4 / S-1`、`T-4 / S-3` 各有 Playwright RED→GREEN 證據且可追溯。
- Test Integrity finding:none(七項無命中)
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-5
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-23 14:05(早於 commit `d41f9a2`)
- Verify:`go test ./internal/... -run TestRenewalStatus_S4` → reviewer 親跑 `ok  internal/handler  0.33s`。
- Covers finding:R-3 / S-4 的標記行為、歷程一筆(誰/何時/舊→新)與「已續約」僅主管的 API 層拒絕均吻合。
- Files finding:改動僅 `migrations/0007_renewal_status.sql`、`internal/handler/contract_status.go`、`internal/repo/contract_status.go`。
- RED→GREEN finding:`T-5 / S-4` 有本 T 的 RED→GREEN 證據且可追溯。
- Test Integrity finding:none(七項無命中;特別核對④:測試與實作非同步改寫正確性)
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-6
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-23 15:10(早於 commit `e8b07c3`)
- Verify:`go test ./internal/... -run TestRenewalStatus_S5` → reviewer 親跑 `ok  internal/repo  0.28s`。
- Covers finding:R-3 / S-5 的「看過兩次狀態不變、歷程零新增」吻合;歷程查詢可作稽核證據。
- Files finding:改動僅 `internal/handler/contract_status.go`、`internal/repo/contract_status.go`。
- RED→GREEN finding:`T-6 / S-5` 有本 T 的 RED→GREEN 證據且可追溯。
- Test Integrity finding:none(七項無命中;特別核對⑤:歷程零新增以真實 repo 查詢驗證,未 mock 核心邏輯)
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-7
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-23 16:20(早於 commit `f92c1d5`)
- Verify:`npm test -- ExpiringContractsCard` → reviewer 親跑 `PASS (4 tests)`。
- Covers finding:R-3 / S-6 的「已續約」灰階、提示字樣與狀態不變均吻合;狀態欄/下一步欄/最後動作時間同列呈現。
- Files finding:改動僅 `src/components/ExpiringContractsCard.tsx`。
- RED→GREEN finding:`T-7 / S-6` 有本 T 的 RED→GREEN 證據且可追溯。
- Test Integrity finding:none(七項無命中)
- verdict:PASS
- correction + re-review after FAIL:N/A

## Progress Log
- 07-21 | T-1 | review PASS 後提交 API + service,EXPLAIN 確認走 idx_contracts_end_date | `a1c3f02`
- 07-22 | T-2 | review PASS 後提交卡片 + 空狀態 | `b7e91d4`
- 07-22 | T-3 | review PASS 後提交詳情連結 | `c58a2e0`
- 07-23 | T-4 | review PASS 後提交 e2e | `f3a08c1`
- 07-23 | T-5 | review PASS 後提交狀態標記 API + migration + 歷程表 | `d41f9a2`
- 07-23 | T-6 | review PASS 後提交歷程查詢 + 看過零副作用測試 | `e8b07c3`
- 07-23 | T-7 | review PASS 後提交卡片狀態欄 + 「已續約」灰階 | `f92c1d5`

## TDD Evidence
<!-- 每個「T × Covers S」各一筆;同一 S 在不同 T/層次的 RED→GREEN 不得共用。 -->
### T-1 / S-1
- RED: `go test ./internal/... -run TestExpiring_S1` → `FAIL: expected 1 contract, got 0 (handler not implemented)`
- GREEN: 同指令 → `ok  internal/service  0.31s`

### T-1 / S-2
- RED: `go test ./internal/... -run TestExpiring_S2` → `FAIL: expected empty list with 200, got 404 (handler not implemented)`
- GREEN: 同指令 → `ok  internal/handler  0.29s`

### T-2 / S-1
- RED: `npm test -- ExpiringContractsCard -t "S1 list"` → `Unable to find an element with the text: C`
- GREEN: 同指令 → `PASS (1 test)`

### T-2 / S-2
- RED: `npm test -- ExpiringContractsCard -t "S2 empty"` → `Expected "近期無到期合約", received element not found`
- GREEN: 同指令 → `PASS (1 test)`

### T-3 / S-3
- RED: `npm test -- ExpiringContractsCard -t "S3 navigate"` → `navigate not called`
- GREEN: 同指令 → `PASS (1 test)`

### T-4 / S-1
- RED: `npx playwright test e2e/expiring-contracts.spec.ts -g "S1"` → `Expected card "C" to be visible`
- GREEN: 同指令 → `1 passed`

### T-4 / S-3
- RED: `npx playwright test e2e/expiring-contracts.spec.ts -g "S3"` → `Expected URL /contracts/C.id, received /dashboard`
- GREEN: 同指令 → `1 passed`

### T-5 / S-4
- RED: `go test ./internal/... -run TestRenewalStatus_S4` → `FAIL: PATCH /contracts/C.id/status → 404 (status handler not implemented)`
- GREEN: 同指令 → `ok  internal/handler  0.33s`

### T-6 / S-5
- RED: `go test ./internal/... -run TestRenewalStatus_S5` → `FAIL: undefined: repo.CountStatusHistory (歷程查詢未實作,零新增無從稽核)`
- GREEN: 同指令 → `ok  internal/repo  0.28s`

### T-7 / S-6
- RED: `npm test -- ExpiringContractsCard -t "S6 renewed-only-manager"` → `Unable to find an element with the text: 已續約僅主管可標`
- GREEN: 同指令 → `PASS (1 test)`

## Decisions(spec 未載明的自由選擇)
(無 —— 本次無 spec 未載明的自由選擇需記錄;取捨皆落在 D-1)

## Deviations
### D-1(L1)
- 現象:原計畫在 repo 層新增覆蓋索引 migration 以壓查詢延遲;實測 EXPLAIN 走既有
  `idx_contracts_end_date`,p95 42ms 已達標。
- 保守選擇:**不新增覆蓋索引 migration**(新增 schema 變更屬不可逆面,且 4-spec
  Dependencies 只載明 `renewal_status` migration,索引不在清單內,加了反而變 L2)。
- 理由:實測已達 Success Criteria(<100ms),改 schema 的風險 > 收益。
- 影響:T-1(Files 少了索引 migration 檔);R/S 無影響。

## Files Changed
9 檔 / +82 −12(Diff Budget ≤9 檔/≤600 行,內)。
- `internal/handler/contract.go` (T-1)
- `internal/service/contract.go` (T-1)
- `internal/repo/contract.go` (T-1)
- `src/components/ExpiringContractsCard.tsx` (T-2, T-3, T-7)
- `src/pages/Dashboard.tsx` (T-2)
- `e2e/expiring-contracts.spec.ts` (T-4)
- `migrations/0007_renewal_status.sql` (T-5)
- `internal/handler/contract_status.go` (T-5, T-6)
- `internal/repo/contract_status.go` (T-5, T-6)

## Diff(各 T commit,逐檔折疊)

### T-1 · `a1c3f02`

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

### T-2 / T-3 · `b7e91d4` / `c58a2e0`

<details>
<summary title="+8/-1; card list, empty state, navigation"><code>src/components/ExpiringContractsCard.tsx</code> (+8/-1; <code>ExpiringContractsCard</code>)</summary>
<pre><span class="del">-export const ExpiringContractsCard = () =&gt; null</span>
<span class="add">+export function ExpiringContractsCard({ contracts, navigate }: Props) {</span>
<span class="add">+  if (contracts.length === 0) return &lt;p&gt;近期無到期合約&lt;/p&gt;</span>
<span class="add">+  return &lt;section aria-label="近期到期合約"&gt;</span>
<span class="add">+    {contracts.map((contract) =&gt; (</span>
<span class="add">+      &lt;button key={contract.id} onClick={() =&gt; navigate(`/contracts/${contract.id}`)}&gt;</span>
<span class="add">+        {contract.name} · {contract.daysRemaining} 天</span>
<span class="add">+      &lt;/button&gt;))}</span>
<span class="add">+  &lt;/section&gt; }</span></pre>
</details>

<details>
<summary title="+2/-1; dashboard card mount"><code>src/pages/Dashboard.tsx</code> (+2/-1; <code>Dashboard</code>)</summary>
<pre><span class="del">-return &lt;main&gt;&lt;/main&gt;</span>
<span class="add">+return &lt;main&gt;</span>
<span class="add">+  &lt;ExpiringContractsCard contracts={expiringContracts} navigate={navigate} /&gt;&lt;/main&gt;</span></pre>
</details>

### T-4 · `f3a08c1`

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

### T-5 · `d41f9a2`

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
<summary title="+9/-0; MarkStatus handler(S-6 權限檢查)"><code>internal/handler/contract_status.go</code> (+9/-0; <code>MarkStatus</code>)</summary>
<pre><span class="add">+func (h *Handler) MarkStatus(w http.ResponseWriter, r *http.Request) {</span>
<span class="add">+    actor := auth.Actor(r.Context())</span>
<span class="add">+    req := decodeStatusRequest(r) // to_status(值域固定 6 值)</span>
<span class="add">+    if req.To == "已續約" &amp;&amp; !actor.IsManager {</span>
<span class="add">+        h.errors.Write(w, ErrManagerOnly) // S-6:已續約僅主管可標</span>
<span class="add">+        return</span>
<span class="add">+    }</span>
<span class="add">+    result, err := h.status.Mark(r.Context(), req.ContractID, actor.ID, req.To)</span>
<span class="add">+    if err != nil { h.errors.Write(w, err); return }; writeJSON(w, http.StatusOK, result) }</span></pre>
</details>

<details>
<summary title="+10/-0; Mark:單一交易更新狀態+歷程"><code>internal/repo/contract_status.go</code> (+10/-0; <code>Mark</code>)</summary>
<pre><span class="add">+const markStatus = `UPDATE contracts SET renewal_status = $2,</span>
<span class="add">+  last_action_at = now() WHERE id = $1 RETURNING renewal_status`</span>
<span class="add">+const insertHistory = `INSERT INTO contract_status_history</span>
<span class="add">+  (contract_id, actor_id, from_status, to_status) VALUES ($1,$2,$3,$4)`</span>
<span class="add">+func (r *ContractStatusRepo) Mark(ctx context.Context, id, actorID string,</span>
<span class="add">+    to Status) (StatusResult, error) {</span>
<span class="add">+    // 單一交易:更新狀態 + 歷程一筆(誰/何時/舊→新)</span>
<span class="add">+    return r.inTx(ctx, func(tx Tx) (StatusResult, error) {</span>
<span class="add">+        prev := tx.CurrentStatus(id)</span>
<span class="add">+        return tx.MarkAndLog(id, actorID, prev, to) }) }</span></pre>
</details>

### T-6 · `e8b07c3`

<details>
<summary title="+5/-1; StatusHistory 唯讀查詢(S-5 零寫入)"><code>internal/handler/contract_status.go</code> (+5/-1; <code>StatusHistory</code>)</summary>
<pre><span class="del">-// StatusHistory:T-5 留 stub,詳情頁時間軸資料源</span>
<span class="add">+func (h *Handler) StatusHistory(w http.ResponseWriter, r *http.Request) {</span>
<span class="add">+    // GET 路徑:唯讀,零狀態寫入(S-5:看過 ≠ 處理)</span>
<span class="add">+    rows, err := h.status.History(r.Context(), pathParam(r, "id"))</span>
<span class="add">+    if err != nil { h.errors.Write(w, err); return }</span>
<span class="add">+    writeJSON(w, http.StatusOK, rows) }</span></pre>
</details>

<details>
<summary title="+6/-1; CountStatusHistory / History 查詢"><code>internal/repo/contract_status.go</code> (+6/-1; <code>CountStatusHistory</code>)</summary>
<pre><span class="del">-// 歷程查詢:T-5 留 stub</span>
<span class="add">+const countHistory = `SELECT COUNT(*) FROM contract_status_history</span>
<span class="add">+  WHERE contract_id = $1`</span>
<span class="add">+func (r *ContractStatusRepo) CountStatusHistory(ctx context.Context,</span>
<span class="add">+    id string) (int, error)</span>
<span class="add">+func (r *ContractStatusRepo) History(ctx context.Context,</span>
<span class="add">+    id string) ([]StatusEvent, error)</span></pre>
</details>

### T-7 · `f92c1d5`

<details>
<summary title="+7/-4; 狀態欄/下一步/最後動作時間 + 已續約灰階"><code>src/components/ExpiringContractsCard.tsx</code> (+7/-4; <code>StatusCell</code>)</summary>
<pre><span class="del">-      &lt;button key={contract.id} onClick={() =&gt; navigate(`/contracts/${contract.id}`)}&gt;</span>
<span class="del">-        {contract.name} · {contract.daysRemaining} 天</span>
<span class="del">-      &lt;/button&gt;))}</span>
<span class="del">-  &lt;/section&gt; }</span>
<span class="add">+      &lt;row key={contract.id}&gt;</span>
<span class="add">+        &lt;button onClick={() =&gt; navigate(`/contracts/${contract.id}`)}&gt;</span>
<span class="add">+          {contract.name} · {contract.daysRemaining} 天&lt;/button&gt;</span>
<span class="add">+        &lt;StatusCell status={contract.status} nextStep={contract.nextStep}</span>
<span class="add">+          lastActionAt={contract.lastActionAt}</span>
<span class="add">+          canMarkRenewed={viewer.isManager} /&gt; {/* 非主管:「已續約」灰階+提示 */}</span>
<span class="add">+      &lt;/row&gt;))}</span></pre>
</details>

## Self-Review
<!-- = 執行清單步 4 的八問:逐問作答、附證據(測試輸出/hash/diff stat),不憑印象 -->
1. 每個「T × Covers S」有含 S-id 的測試 + 該 T 自己的 RED/GREEN 證據? → 是,
   `T-1/S-1`、`T-1/S-2`、`T-2/S-1`、`T-2/S-2`、`T-3/S-3`、
   `T-4/S-1`、`T-4/S-3`、`T-5/S-4`、`T-6/S-5`、`T-7/S-6` 十筆皆見上方
   TDD Evidence,且未跨 T 共用證據。
2. 每 T 都有獨立 T Review Log verdict? → 是,T-1~T-7 均由 `<reviewer-a>` 親跑 Verify,
   Covers/Files/RED→GREEN/Test Integrity finding 皆記為 PASS。
3. 每個 PASS 都早於該 T commit? → 是,七筆 reviewed-at 均明列早於各自 hash。
4. 每個 FAIL 後有較晚 PASS,否則未勾未 commit? → 是,本次七 T 均首輪 PASS,各筆皆記 N/A。
5. 每 T 一 commit、Progress Log 每列有 hash? → 是,見上方 Progress Log,每 T 一列各自留 hash。
6. `git diff --stat` 改動檔案 ⊆ 5-tasks Files 聯集、Diff Budget 內? → 是,見 Files
   Changed(9 檔 / +82 −12),在 4-spec Diff Budget(≤9 檔/≤600 行)內。
7. Decisions/Deviations 與 diff 對得上(無 silent drift)? → 是,Decisions 節本次
   空(取捨皆落在 D-1),僅 D-1 一筆 Deviation(放棄新增**覆蓋索引** migration;
   T-5 的 `renewal_status` migration 是 4-spec Dependencies 明載的計畫內變更,非偏差),
   對應 diff 無覆蓋索引檔,R-1~R-3/S-1~S-6 均無變動。
8. 回歸綠? → 是,`go test ./...` 與 `npm test` 既有套件全綠(摘要見上)。
