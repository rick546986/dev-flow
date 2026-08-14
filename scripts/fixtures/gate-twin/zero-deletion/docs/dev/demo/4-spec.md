---
feature: demo
stage: 4-spec
status: draft
---

# 4. 規格(零刪減 fixture)

> 這份 fixture 的每個「不會被做成卡片」的章節都埋了一個獨一無二的字串
> `CANARY-<n>`。守衛檢查它們是不是全部出現在產出的 html 裡 ——
> 少一個就代表「背景資料內容零刪減」這條規格被破壞了。
> 起因(2026-08-15 獨立審查 H2):守衛原本只斷言 `<details>` 這個字串存在,
> 把渲染函式改成 `return ""`(內容全刪光)照樣全綠。

## ADDED Requirements

### R-1: 系統 SHALL 做一件事

#### S-1
- GIVEN 有資料
- WHEN 按下按鈕
- THEN 顯示結果
- 觀測(承接):打 GET /demo | 回 200 | 用 seed.sql

## Acceptance Criteria

CANARY-1 這行必須完整出現在產出的 html 裡。

| 欄 | 值 |
|---|---|
| 表格也要留住 | CANARY-2 |

## Out of Scope

- CANARY-3 清單項也要留住
- 第二項

## Test Skeletons

這一節天生會放程式碼,而程式碼裡的假標題不得被當成真的:

```md
### R-9: 這是程式碼區塊裡的假 R,不得產生幻影卡
#### S-9.1
- GIVEN 假的
```

CANARY-4 在程式碼區塊之後,也必須留住。

## Verification Profile(G2 一併審)
- lane: fast
- Risk: normal
- CANARY-5
