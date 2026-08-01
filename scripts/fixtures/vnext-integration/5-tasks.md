---
feature: vnext-thin-slice
stage: 5-tasks
status: approved
owner: <owner>
updated: 2026-08-02
execution:
  mode: parallel
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務(vnext 最薄整合案例 fixture:T-1/T-2 可平行)

## T-1 建 API handler:GET /contracts/expiring
- [ ] 完成
- Covers: R-1 / S-1
- Files: `internal/handler/contract.go`, `internal/handler/contract_test.go`
- Verify: `go test ./internal/handler/... -run TestExpiring`
- Blocked-by: —
- Risk: normal

## T-2 前端到期卡片(含空狀態)
- [ ] 完成
- Covers: R-1 / S-2
- Files: `src/components/ExpiringContractsCard.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: —
- Integrate-after: T-1
- Risk: normal
