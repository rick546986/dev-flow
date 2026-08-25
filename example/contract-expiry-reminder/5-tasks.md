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
- Files: `internal/handler/contract.go`, `internal/service/contract.go`, `internal/repo/contract.go`, `internal/service/contract_test.go`, `internal/handler/contract_test.go`
- Verify: `n=$(go test ./internal/... -run TestExpiring -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: —
- Intent: 系統多了到期查詢 API:`GET /contracts/expiring?days=30` 回傳登入者名下 30 天內到期且未續約的合約;無符合者回 200 + 空列表,不報錯。
- Boundaries: 查詢邏輯抽在 `service.ListExpiring`(2-decision:供未來 cron 複用);複用既有 `idx_contracts_end_date`,不另建索引;`days` 參數化只為測試方便,自訂天數仍 Out of Scope。
  Design Boundary(摘自 4-spec Design Boundary Contract,只取本 T 相關的最小子集):可動 handler／service／read repo 三層;依賴方向單向 handler → service → repo,**禁反向**;本 T 不擁有 `contracts`(唯讀,禁寫任何欄位與歷程);介面為 additive 新端點,無既有呼叫端;Test seam = service 層可注入固定 today 驗剩餘天數。

## T-2 前端:dashboard 到期卡片(含空狀態)
- [x] 完成
- Covers: R-1 / S-1, S-2
- Files: `src/components/ExpiringContractsCard.tsx`, `src/pages/Dashboard.tsx`, `src/components/ExpiringContractsCard.test.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-1
- Intent: dashboard 多了到期卡片:列出合約名稱與剩餘天數「N 天」;零筆時顯示空狀態「近期無到期合約」,不隱藏整卡、不顯示錯誤。
- Boundaries: 空狀態文案照 4-spec S-2 寫死,不得自創;剩餘天數顯示「N 天」不含小時(4-spec Drafting Decisions)。
  Design Boundary(摘自 4-spec Design Boundary Contract,只取本 T 相關的最小子集):Dashboard UI 不擁有任何資料,**禁直接觸 DB**,一律經 Contract API;前端不保存狀態真相,每次以 API 回應為準。

## T-3 卡片列點擊 → 合約詳情
- [x] 完成
- Covers: R-2 / S-3
- Files: `src/components/ExpiringContractsCard.tsx`, `src/components/ExpiringContractsCard.test.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-2
- Intent: 卡片每筆合約列可點擊,導向該合約詳情頁 `/contracts/:id`。
- Boundaries: 照既有 ExpiringContractsCard pattern,不動 `src/pages/Dashboard.tsx`。
  Design Boundary(摘自 4-spec Design Boundary Contract,只取本 T 相關的最小子集):同 T-2 —— UI 層禁直接觸 DB;本 T 為導覽,不產生任何寫入。

## T-4 e2e:登入 → dashboard 看到到期合約 → 點入詳情
- [x] 完成
- Covers: R-1, R-2 / S-1, S-3
- Files: `e2e/expiring-contracts.spec.ts`
- Verify: `npx playwright test e2e/expiring-contracts.spec.ts`
- Blocked-by: T-3
- Intent: 系統多了可重複執行的端到端證據:真瀏覽器走完「登入 → dashboard 看到到期合約 C 與『10 天』→ 點擊導向 `/contracts/C.id`」全鏈路。
- Boundaries: 只新增 `e2e/expiring-contracts.spec.ts`,不動實作碼;斷言取值照 4-spec S-1/S-3 觀測欄。
  Design Boundary(摘自 4-spec Design Boundary Contract,只取本 T 相關的最小子集):純驗證層:不新增任何模組依賴、不改任何 Data owner、不動介面與交易邊界。

## T-5 建狀態標記 API:renewal_status migration + 歷程表 + 權限檢查
- [x] 完成
- Covers: R-3 / S-4
- Files: `migrations/0007_renewal_status.sql`, `internal/handler/contract_status.go`, `internal/repo/contract_status.go`, `internal/handler/contract_status_test.go`
- Verify: `n=$(go test ./internal/... -run TestRenewalStatus_S4 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Risk: high
- Intent: 系統多了「標記處理狀態」行為:標記後狀態/下一步/最後動作時間更新,歷程新增一筆(誰/何時/舊→新);「已續約」僅主管,非主管在 API 層被拒。
- Boundaries: 狀態值域固定 6 值(4-spec Drafting Decisions);禁任何自動轉移狀態(僅明確標記動作);migration 只加 `renewal_status` enum 欄與歷程表,不動既有欄位。
  Design Boundary(摘自 4-spec Design Boundary Contract,只取本 T 相關的最小子集):`repo.ContractStatus` 是 `contracts.renewal_status` 與狀態歷程表的**唯一寫入點**(Data owner),**禁**由 UI 或 service 繞過直呼;狀態更新與歷程追加**必須同一交易**(不得只成功一筆);「已續約」授權在 API handler 層強制,UI 灰階只是呈現不是防線;migration 為 additive(只加欄加表),既有讀取路徑相容;Test seam = 權限分支 `TestRenewalStatus_S4` + migration down/up 演練驗 orphan rows。

## T-6 歷程查詢 + 看過零副作用保證(讀取路徑不寫狀態)
- [x] 完成
- Covers: R-3 / S-5
- Files: `internal/handler/contract_status.go`, `internal/repo/contract_status.go`, `internal/repo/contract_status_test.go`
- Verify: `n=$(go test ./internal/... -run TestRenewalStatus_S5 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-5
- Intent: 系統多了狀態歷程查詢(詳情頁時間軸資料源),且「開啟/看過」等一切讀取路徑保證零狀態寫入 —— 歷程零新增本身成為可稽核證據。
- Boundaries: 任何 GET 路徑不得寫入狀態或歷程;不做「已讀」記錄(看過 ≠ 處理,1-discussion Q4);不引入 Out of Scope 的自動提醒。
  Design Boundary(摘自 4-spec Design Boundary Contract,只取本 T 相關的最小子集):讀取路徑**禁進入寫入分支**(Contract status store 的 Forbidden dependency 之一);不改 Data owner、不改交易邊界;Test seam = `TestRenewalStatus_S5_ViewDoesNotComplete` 以歷程筆數零新增斷言。

## T-7 卡片列狀態欄 + 下一步欄 + 標記互動(「已續約」灰階)
- [x] 完成
- Covers: R-3 / S-6
- Files: `src/components/ExpiringContractsCard.tsx`, `src/components/ExpiringContractsCard.test.tsx`
- Verify: `npm test -- ExpiringContractsCard`
- Blocked-by: T-2, T-5
- Intent: 卡片列多了狀態欄/下一步欄/最後動作時間與列內標記選單;非主管看到「已續約」灰階 + 「已續約僅主管可標」提示,狀態不變。
- Boundaries: 照既有 ExpiringContractsCard pattern,不動 `src/pages/Dashboard.tsx`;提示文案照 4-spec S-6 寫死,不得自創。
  Design Boundary(摘自 4-spec Design Boundary Contract,只取本 T 相關的最小子集):UI 灰階與提示是呈現,**授權正本在 API handler 層**,前端不得自行推導授權結論以外的狀態;禁直接觸 DB;查詢失敗無專用錯誤畫面是 4-spec 已列的 Known design limit,本 T 不擅自補。

## T 依賴 DAG(Blocked-by,機械導出)
```
T-1 --> T-2 --> T-3 --> T-4
 |       |
 v       +---------------+
T-5 --> T-6              |
 |                       v
 +---------------------> T-7
```

<section class="dag" id="dag">
Wave 1: T-1
Wave 2: T-2 ←(T-1)、T-5 ←(T-1)
Wave 3: T-3 ←(T-2)、T-6 ←(T-5)、T-7 ←(T-2,T-5)
Wave 4: T-4 ←(T-3)
</section>
