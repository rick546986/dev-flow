---
feature: stage4-review-fixture
stage: 4-spec
status: draft
verdict: PRE-REVIEW
owner: fixture
reviewers: [fixture-reviewer]
updated: 2026-08-28
---

# 4. 規格 — 審頁 R/S fixture

## ADDED Requirements

### R-1: 系統 SHALL 在列表顯示登入者可見、未完成的到期卡片
#### S-1
- GIVEN 登入者名下有件 C,剩餘 10 天,未完成
- WHEN 登入者開啟列表
- THEN 到期卡片列出 C,顯示名稱與「10 天」
- 觀測:從列表到期卡片看 | 看到 C 與「10 天」算對 | 用 C(剩餘 10 天,未完成)測

#### S-2
- GIVEN 登入者名下無到期件
- WHEN 登入者開啟列表
- THEN 卡片顯示空狀態「近期無到期」,不顯示錯誤
- 觀測:從列表到期卡片看 | 看到空狀態且無錯誤算對 | 用名下無到期件的帳號測

### R-2: 卡片中每筆 SHALL 可點擊導向該件詳情
#### S-3
- GIVEN 到期卡片列出件 C
- WHEN 登入者點擊 C 那一列
- THEN 導向該件詳情頁
- 觀測:從 C 那一列與網址看 | 點擊後進入 C 詳情算對 | 用 S-1 的 C 測

## MODIFIED Requirements
(無 —— 不改既有行為)

## REMOVED Requirements
(無)

## 模組生命週期
- 新生:沒有
- 改行為:列表查詢模組(這輪新功能落點:到期卡 + 空狀態)
- 退役:沒有
- 不動:其餘既有模組

主詞是這個 feat 的列表查詢模組。關聯收成一格,不拆檔名。

## Drafting Decisions(草擬自判,待人審)

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據 | 若被推翻會怎樣 | 狀態 |
|---|---|---|---|---|---|
| DD-1 | 空狀態留卡 | 藏卡會被當成壞掉 | [Assumption] | 改文案即可 | ✅ |
