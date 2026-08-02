---
feature: fixture-infra
stage: 5-tasks
status: draft
---

# 5. 任務(fixture:合法純 Migration/Infrastructure,期望不警告)

## T-1 Migration
- [ ] 完成
- Covers: R-1 / S-1
- Files: `migrations/0007_renewal_status.sql`
- Verify: `make migrate && make migrate-down && make migrate`
- Blocked-by: —
- Intent: 資料庫多了 `renewal_status` 欄與狀態歷程表,既有 8k 筆合約可標狀態且 down/up 演練後零 orphan row。
- Boundaries: 只加欄與加表,不動既有欄位。

## T-2 Schema
- [ ] 完成
- Covers: R-1 / S-2
- Files: `internal/model/contract.go`
- Verify: `go build ./...`
- Blocked-by: T-1
- Intent: 模型層多了 renewal_status 欄位,查詢回傳的合約物件可觀測到目前狀態值。
- Boundaries: 不改既有欄位語意。
