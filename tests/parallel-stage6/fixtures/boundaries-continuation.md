---
feature: boundaries-continuation-fixture
stage: 5-tasks
status: approved
owner: <owner>
updated: 2026-08-03
---

# 5. 任務(相容性 fixture:合法的 `Boundaries:` 多行續寫)

<!-- 對照組。續行以純文字開頭(不是 `- <保留欄名>:`),即 example/contract-expiry-reminder
     的寫法。重複保留欄偵測**不得**誤傷這種合法續寫:errors 必須為空,
     且 Files / Verify 必須維持該 T 自己宣告的值。 -->

## T-1 API:GET /contracts/expiring
- [x] 完成
- Covers: R-1 / S-1, S-2
- Files: `internal/handler/contract.go`, `internal/service/contract.go`
- Verify: `go test ./internal/... -run TestExpiring`
- Blocked-by: —
- Intent: 系統多了到期查詢 API。
- Boundaries: 查詢邏輯抽在 `service.ListExpiring`。
  Design Boundary(摘自 4-spec Design Boundary Contract,只取本 T 相關的最小子集):
  可動 handler／service／read repo 三層;依賴方向單向 handler → service → repo,**禁反向**;
  本 T 不擁有 `contracts`(唯讀,禁寫任何欄位與歷程);介面為 additive 新端點;
  Test seam = service 層可注入固定 today 驗剩餘天數。

## T-2 前端:dashboard 到期卡片
- [ ] 完成
- Covers: R-1 / S-1, S-2
- Files: `src/components/ExpiringContractsCard.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-1
- Intent: dashboard 多了到期卡片。
- Boundaries: 空狀態文案照 4-spec S-2 寫死。
  Design Boundary:Dashboard UI 不擁有任何資料,**禁直接觸 DB**,一律經 Contract API。
