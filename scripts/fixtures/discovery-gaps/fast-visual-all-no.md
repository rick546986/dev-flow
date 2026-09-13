---
feature: fast-visual-all-no
stage: 4-spec
status: draft
---

# 4. 規格 — 純視覺全否可維持 Fast

## Fast early risk triage

| 問 | 答 |
|---|---|
| 改變下一步？ | 否。只改 CSS 色 |
| 改權限／核准語意？ | 否。只改 CSS 色 |
| 改等待／完成語意？ | 否。只改 CSS 色 |
| 改角色交接？ | 否。只改 CSS 色 |
| 改系統外動作？ | 否。只改 CSS 色 |
| 改中斷恢復？ | 否。只改 CSS 色 |

去向: Fast

## ADDED Requirements

### R-1: 系統 SHALL 顯示剩餘天數
#### S-1 顯示剩餘天數
- GIVEN 合約剩餘 14 天
- WHEN 開頁
- THEN 顯示 14 天
- 觀測:從頁面看 | 看到 14 天算過 | 用剩餘 14 天測

## Verification Profile

- lane: fast
- Risk: normal
