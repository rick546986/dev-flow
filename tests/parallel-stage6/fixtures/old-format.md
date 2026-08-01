---
feature: old-format-fixture
stage: 5-tasks
status: approved
owner: <owner>
updated: 2026-08-02
---

# 5. 任務(舊格式:無 execution 區塊、無任何新欄位)

## T-1 API:GET /contracts/expiring
- [x] 完成
- Covers: R-1 / S-1, S-2
- Files: `internal/handler/contract.go`, `internal/service/contract.go`
- Verify: `go test ./internal/... -run TestExpiring`
- Blocked-by: —

## T-2 前端:dashboard 到期卡片
- [ ] 完成
- Covers: R-1 / S-1, S-2
- Files: `src/components/ExpiringContractsCard.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-1

## T-3 卡片列點擊 → 合約詳情
- [ ] 完成
- Covers: R-2 / S-3
- Files: `src/components/ExpiringContractsCard.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-2
