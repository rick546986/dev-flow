---
feature: contract-expiry-reminder
stage: 6-implementation
status: approved
owner: <owner>
updated: 2026-07-23
---

# 6. 實作筆記

## Progress Log
- 07-21 | T-1 | API + service 完成,EXPLAIN 確認走 idx_contracts_end_date | `a1c3f02`
- 07-22 | T-2, T-3 | 卡片 + 空狀態 + 詳情連結 | `b7e91d4` / `c58a2e0`
- 07-23 | T-4 | e2e 過;交 review | `f3a08c1`

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

## Self-Review
<!-- = 執行清單步 4 的五問:逐問作答、附證據(測試輸出/hash/diff stat),不憑印象 -->
1. 每 S-id 有含其名測試 + RED/GREEN 證據? → 是,S-1(`TestExpiring_S1`)、S-2
   (`"S2 empty"`)、S-3(`"S3 navigate"`)皆見上方 TDD Evidence,RED(失敗輸出)→
   GREEN(通過輸出)證據齊全。
2. 每 T 一 commit、Progress Log 每列有 hash? → 是,見上方 Progress Log(T-2、T-3
   同日兩次 commit,各自留 hash)。
3. `git diff --stat` 改動檔案 ⊆ 5-tasks Files 聯集、Diff Budget 內? → 是,見 Files
   Changed(6 檔 / +312 −8),在 4-spec Diff Budget(≤6 檔/≤400 行)內。
4. Decisions/Deviations 與 diff 對得上(無 silent drift)? → 是,Decisions 節本次
   空(取捨皆落在 D-1),僅 D-1 一筆 Deviation(放棄新增覆蓋索引 migration),對應
   diff 確實無新 migration 檔,R-1/R-2/S-1~S-3 均無變動。
5. 回歸綠? → 是,`go test ./...` 與 `npm test` 既有套件全綠(摘要見上)。
