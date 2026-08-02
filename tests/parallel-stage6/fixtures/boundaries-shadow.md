---
feature: boundaries-shadow-fixture
stage: 5-tasks
status: approved
owner: <owner>
updated: 2026-08-03
---

# 5. 任務(負向 fixture:`Boundaries:` 續行寫成保留欄名子項)

<!-- 這份 fixture 刻意違反 _templates/5-tasks.md 的「續行禁令」:
     T-1 的 Design Boundary 摘錄被寫成 `- Files:` / `- Verify:` 子項,
     T-2 的 `Intent:` 續行被寫成 `- Risk:` 子項。
     舊行為(last-write-wins)會靜默把 T-1 的 Files 由三個具名檔換成三個整目錄、
     把 Verify 換成一句散文,且 errors 為空 —— scope 被無聲放寬。
     修正後 parse_5_tasks 必須為每一次遮蔽各記一筆「重複保留欄」error(fail-closed),
     並保留首筆值不被覆蓋。 -->

## T-1 API:GET /contracts/expiring
- [x] 完成
- Covers: R-1 / S-1, S-2
- Files: `internal/handler/contract.go`, `internal/service/contract.go`
- Verify: `go test ./internal/... -run TestExpiring`
- Blocked-by: —
- Intent: 系統多了到期查詢 API。
- Boundaries: 查詢邏輯抽在 `service.ListExpiring`。
  Design Boundary(摘自 4-spec Design Boundary Contract):
  - Files: `internal/handler/`, `internal/service/`, `internal/repo/`
  - 禁止新增的依賴方向: 禁 repo → handler 反向
  - Verify: 依賴方向不得反向

## T-2 前端:dashboard 到期卡片
- [ ] 完成
- Covers: R-1 / S-1, S-2
- Files: `src/components/ExpiringContractsCard.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-1
- Risk: normal
- Intent: dashboard 多了到期卡片。
  補充說明:
  - Risk: high
