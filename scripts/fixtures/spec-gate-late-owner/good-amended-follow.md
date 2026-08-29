<!-- 正向 fixture:Decision 已回寫,4-spec 跟它。C6 必須綠。
     引 2-decision 當依據不算「4-spec 壓 Decision」。 -->

---
feature: late-owner-amended-follow
stage: 4-spec
status: draft
---

# 4. 規格 — late-owner 已回寫 Decision

## Verification Profile

- lane: fast
- Risk: normal

## S-1 顯示週數

- GIVEN 合約 C 剩餘 14 天 WHEN 開 dashboard THEN 卡片顯示「2 週」
- 觀測:從 dashboard 卡片看 | 看到「2 週」算對 | 用剩餘 14 天的 C 測

## Drafting Decisions

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據 | 若被推翻會怎樣 | 狀態 |
|---|---|---|---|---|---|
| DD-1 | 顯示單位改為「週」 | owner 改口後已回寫 Decision | `2-decision.md` Decision | S-1 THEN 改字樣 | ✅ |

### 內部技術選擇(下層,告知即可)
(無)

## 確認紀錄
- Decision 已回寫;本檔跟 2-decision | 2026-08-29
