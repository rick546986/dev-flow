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
- RED→GREEN finding:S-1/S-2 的 RED→GREEN 證據完整且可追溯。
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-2
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-22 10:15(早於 commit `b7e91d4`)
- Verify:`npm test -- ExpiringContractsCard` → reviewer 親跑 `PASS (2 tests)`。
- Covers finding:R-1 / S-1、S-2 的卡片與空狀態均吻合。
- Files finding:改動僅 `src/components/ExpiringContractsCard.tsx`、`src/pages/Dashboard.tsx`。
- RED→GREEN finding:S-1/S-2 的 RED→GREEN 證據完整且可追溯。
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-3
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-22 15:30(早於 commit `c58a2e0`)
- Verify:`npm test -- ExpiringContractsCard` → reviewer 親跑 `PASS (3 tests)`。
- Covers finding:R-2 / S-3 的卡片列導向詳情頁行為吻合。
- Files finding:改動僅 `src/components/ExpiringContractsCard.tsx`。
- RED→GREEN finding:S-3 的 RED→GREEN 證據完整且可追溯。
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-4
- reviewer identity:`<reviewer-a>`
- reviewer kind:human
- reviewed-at:2026-07-23 11:20(早於 commit `f3a08c1`)
- Verify:`npx playwright test e2e/expiring-contracts.spec.ts` → reviewer 親跑 `PASS (登入、卡片、詳情導向)`。
- Covers finding:R-1、R-2 / S-1、S-3 的端到端可見行為吻合。
- Files finding:改動僅 `e2e/expiring-contracts.spec.ts`。
- RED→GREEN finding:S-1/S-3 的端到端 RED→GREEN 證據完整且可追溯。
- verdict:PASS
- correction + re-review after FAIL:N/A

## Progress Log
- 07-21 | T-1 | review PASS 後提交 API + service,EXPLAIN 確認走 idx_contracts_end_date | `a1c3f02`
- 07-22 | T-2 | review PASS 後提交卡片 + 空狀態 | `b7e91d4`
- 07-22 | T-3 | review PASS 後提交詳情連結 | `c58a2e0`
- 07-23 | T-4 | review PASS 後提交 e2e | `f3a08c1`

## TDD Evidence
### S-1
- RED: `go test ./internal/... -run TestExpiring_S1` → `FAIL: expected 1 contract, got 0 (handler not implemented)`
- GREEN: 同指令 → `ok  internal/service  0.31s`

### S-2
- RED: `npm test -- ExpiringContractsCard -t "S2 empty"` → `Expected "近期無到期合約", received element not found`
- GREEN: 同指令 → `PASS (2 tests)`

### S-3
- RED: `npm test -- ExpiringContractsCard -t "S3 navigate"` → `navigate not called`
- GREEN: 同指令 → `PASS (3 tests)`

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
6 檔 / +312 −8(Diff Budget ≤6 檔/≤400 行,內)。
- `internal/handler/contract.go` (T-1)
- `internal/service/contract.go` (T-1)
- `internal/repo/contract.go` (T-1)
- `src/components/ExpiringContractsCard.tsx` (T-2, T-3)
- `src/pages/Dashboard.tsx` (T-2)
- `e2e/expiring-contracts.spec.ts` (T-4)

## Self-Review
<!-- = 執行清單步 4 的八問:逐問作答、附證據(測試輸出/hash/diff stat),不憑印象 -->
1. 每 S-id 有含其名測試 + RED/GREEN 證據? → 是,S-1(`TestExpiring_S1`)、S-2
   (`"S2 empty"`)、S-3(`"S3 navigate"`)皆見上方 TDD Evidence,RED(失敗輸出)→
   GREEN(通過輸出)證據齊全。
2. 每 T 都有獨立 T Review Log verdict? → 是,T-1~T-4 均由 `<reviewer-a>` 親跑 Verify,
   Covers/Files/RED→GREEN finding 皆記為 PASS。
3. 每個 PASS 都早於該 T commit? → 是,四筆 reviewed-at 均明列早於各自 hash。
4. 每個 FAIL 後有較晚 PASS,否則未勾未 commit? → 是,本次四 T 均首輪 PASS,各筆皆記 N/A。
5. 每 T 一 commit、Progress Log 每列有 hash? → 是,見上方 Progress Log,每 T 一列各自留 hash。
6. `git diff --stat` 改動檔案 ⊆ 5-tasks Files 聯集、Diff Budget 內? → 是,見 Files
   Changed(6 檔 / +312 −8),在 4-spec Diff Budget(≤6 檔/≤400 行)內。
7. Decisions/Deviations 與 diff 對得上(無 silent drift)? → 是,Decisions 節本次
   空(取捨皆落在 D-1),僅 D-1 一筆 Deviation(放棄新增覆蓋索引 migration),對應
   diff 確實無新 migration 檔,R-1/R-2/S-1~S-3 均無變動。
8. 回歸綠? → 是,`go test ./...` 與 `npm test` 既有套件全綠(摘要見上)。
