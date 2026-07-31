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
- verdict:PASS
- correction + re-review after FAIL:N/A

## Progress Log
- 07-21 | T-1 | review PASS 後提交 API + service,EXPLAIN 確認走 idx_contracts_end_date | `a1c3f02`
- 07-22 | T-2 | review PASS 後提交卡片 + 空狀態 | `b7e91d4`
- 07-22 | T-3 | review PASS 後提交詳情連結 | `c58a2e0`
- 07-23 | T-4 | review PASS 後提交 e2e | `f3a08c1`

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

## Decisions(spec 未載明的自由選擇)
(無 —— 本次無 spec 未載明的自由選擇需記錄;取捨皆落在 D-1)

## Deviations
### D-1(L1)
- 現象:原計畫在 repo 層新增覆蓋索引 migration 以壓查詢延遲;實測 EXPLAIN 走既有
  `idx_contracts_end_date`,p95 42ms 已達標。
- 保守選擇:**不新增 migration**(新增 schema 變更屬不可逆面,且 4-spec Dependencies
  聲明「不需 migration」,加了反而變 L2)。
- 理由:實測已達 Success Criteria(<100ms),改 schema 的風險 > 收益。
- 影響:T-1(Files 少了 migration 檔);R/S 無影響。

## Files Changed
6 檔 / +35 −6(Diff Budget ≤6 檔/≤400 行,內)。
- `internal/handler/contract.go` (T-1)
- `internal/service/contract.go` (T-1)
- `internal/repo/contract.go` (T-1)
- `src/components/ExpiringContractsCard.tsx` (T-2, T-3)
- `src/pages/Dashboard.tsx` (T-2)
- `e2e/expiring-contracts.spec.ts` (T-4)

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

## Self-Review
<!-- = 執行清單步 4 的八問:逐問作答、附證據(測試輸出/hash/diff stat),不憑印象 -->
1. 每個「T × Covers S」有含 S-id 的測試 + 該 T 自己的 RED/GREEN 證據? → 是,
   `T-1/S-1`、`T-1/S-2`、`T-2/S-1`、`T-2/S-2`、`T-3/S-3`、
   `T-4/S-1`、`T-4/S-3` 七筆皆見上方 TDD Evidence,且未跨 T 共用證據。
2. 每 T 都有獨立 T Review Log verdict? → 是,T-1~T-4 均由 `<reviewer-a>` 親跑 Verify,
   Covers/Files/RED→GREEN finding 皆記為 PASS。
3. 每個 PASS 都早於該 T commit? → 是,四筆 reviewed-at 均明列早於各自 hash。
4. 每個 FAIL 後有較晚 PASS,否則未勾未 commit? → 是,本次四 T 均首輪 PASS,各筆皆記 N/A。
5. 每 T 一 commit、Progress Log 每列有 hash? → 是,見上方 Progress Log,每 T 一列各自留 hash。
6. `git diff --stat` 改動檔案 ⊆ 5-tasks Files 聯集、Diff Budget 內? → 是,見 Files
   Changed(6 檔 / +35 −6),在 4-spec Diff Budget(≤6 檔/≤400 行)內。
7. Decisions/Deviations 與 diff 對得上(無 silent drift)? → 是,Decisions 節本次
   空(取捨皆落在 D-1),僅 D-1 一筆 Deviation(放棄新增覆蓋索引 migration),對應
   diff 確實無新 migration 檔,R-1/R-2/S-1~S-3 均無變動。
8. 回歸綠? → 是,`go test ./...` 與 `npm test` 既有套件全綠(摘要見上)。
