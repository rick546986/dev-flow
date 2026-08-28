---
feature: stage4-subsidy-shape
stage: 4-spec
status: draft
verdict:
owner: fixture
updated: 2026-08-28
---

# 4. 規格 — 補助生命週期標題寫法

## ADDED Requirements

### R-1: 系統 SHALL 在查詢入口列出登入者可看的件
#### S-1
- GIVEN 登入者名下有一筆可查件
- WHEN 開啟查詢入口
- THEN 列表出現該件名稱
- 觀測:從查詢入口列表看 | 看到該件名稱算對 | 用名下有件的帳號測

## MODIFIED Requirements
(無)

## REMOVED Requirements
(無)

## 補助模組生命週期（預覽）
- 新生（這輪沒有）：不加欄。
- 改行為（相關一格）：PLUS 切表／兩格／OPU 小字。
- 退役：形成金額第三格。
- 不動：3.0 兩格、主目錄、27004、191。

說明:只畫這個 feat 那一個模組。有關聯的收成改行為那一格,不拆檔名。

## Drafting Decisions(草擬自判,待人審)

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據 | 若被推翻會怎樣 | 狀態 |
|---|---|---|---|---|---|
| DD-1 | 本期只改查詢入口 | 範圍最小 | [Assumption] | 再加一張 R | ✅ |
