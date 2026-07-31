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
- Verify: `npx playwright test expiring-contracts`
- Blocked-by: T-3
