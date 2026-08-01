---
feature: contract-expiry-reminder
stage: 5-tasks
status: approved
owner: <owner>
updated: 2026-07-23
---

# 5. 任務(tracer bullet:T-1→T-2 先打通端到端,再 T-3 加厚)

## T-1 API:GET /contracts/expiring
- [x] 完成
- Covers: R-1 / S-1, S-2
- Files: `internal/handler/contract.go`, `internal/service/contract.go`, `internal/repo/contract.go`
- Verify: `go test ./internal/... -run TestExpiring`
- Blocked-by: —

## T-2 前端:dashboard 到期卡片(含空狀態)
- [x] 完成
- Covers: R-1 / S-1, S-2
- Files: `src/components/ExpiringContractsCard.tsx`, `src/pages/Dashboard.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-1

## T-3 卡片列點擊 → 合約詳情
- [x] 完成
- Covers: R-2 / S-3
- Files: `src/components/ExpiringContractsCard.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-2

## T-4 e2e:登入 → dashboard 看到到期合約 → 點入詳情
- [x] 完成
- Covers: R-1, R-2 / S-1, S-3
- Files: `e2e/expiring-contracts.spec.ts`
- Verify: `npx playwright test e2e/expiring-contracts.spec.ts`
- Blocked-by: T-3

## T-5 建狀態標記 API:renewal_status migration + 歷程表 + 權限檢查
- [x] 完成
- Covers: R-3 / S-4
- Files: `migrations/0007_renewal_status.sql`, `internal/handler/contract_status.go`, `internal/repo/contract_status.go`
- Verify: `go test ./internal/... -run TestRenewalStatus_S4`
- Blocked-by: T-1
- Intent: 系統多了「標記處理狀態」行為:標記後狀態/下一步/最後動作時間更新,歷程新增一筆(誰/何時/舊→新);「已續約」僅主管,非主管在 API 層被拒。
- Boundaries: 狀態值域固定 6 值(4-spec Drafting Decisions);禁任何自動轉移狀態(僅明確標記動作);migration 只加 `renewal_status` enum 欄與歷程表,不動既有欄位。

## T-6 歷程查詢 + 看過零副作用保證(讀取路徑不寫狀態)
- [x] 完成
- Covers: R-3 / S-5
- Files: `internal/handler/contract_status.go`, `internal/repo/contract_status.go`
- Verify: `go test ./internal/... -run TestRenewalStatus_S5`
- Blocked-by: T-5
- Intent: 系統多了狀態歷程查詢(詳情頁時間軸資料源),且「開啟/看過」等一切讀取路徑保證零狀態寫入 —— 歷程零新增本身成為可稽核證據。
- Boundaries: 任何 GET 路徑不得寫入狀態或歷程;不做「已讀」記錄(看過 ≠ 處理,1-discussion Q4);不引入 Out of Scope 的自動提醒。

## T-7 卡片列狀態欄 + 下一步欄 + 標記互動(「已續約」灰階)
- [x] 完成
- Covers: R-3 / S-6
- Files: `src/components/ExpiringContractsCard.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-2, T-5
- Intent: 卡片列多了狀態欄/下一步欄/最後動作時間與列內標記選單;非主管看到「已續約」灰階 + 「已續約僅主管可標」提示,狀態不變。
- Boundaries: 照既有 ExpiringContractsCard pattern,不動 `src/pages/Dashboard.tsx`;提示文案照 4-spec S-6 寫死,不得自創。
