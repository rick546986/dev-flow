---
feature: demo
stage: 4-spec
status: draft
---

# 4. 規格

## ADDED Requirements

### R-1: 系統 SHALL 做一件事

#### S-1
- GIVEN 有一筆資料
- WHEN 使用者按下按鈕
- THEN 畫面顯示結果
- 觀測(承接 1-discussion 驗收雛形):打 GET /demo | 回 200 且 body 有 result | 用種子資料 seed.sql

#### S-2
- GIVEN 有一筆資料
- WHEN 使用者按下按鈕
- 觀測:看 log 有沒有寫入紀錄

## Verification Profile(G2 一併審)
- lane: fast
- Risk: normal
