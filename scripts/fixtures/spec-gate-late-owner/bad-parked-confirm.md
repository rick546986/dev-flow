<!-- 負向 fixture:確認紀錄宣稱「不採 2-decision / 兩份並存」。
     期望:check-spec-gate.sh exit 1,且 ❌ C6。DD 本身沒寫覆寫句。 -->

---
feature: late-owner-parked-confirm
stage: 4-spec
status: draft
---

# 4. 規格 — late-owner parked 確認紀錄

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
| DD-1 | 顯示單位用「週」 | 對齊已回寫的 Decision | `2-decision.md` Decision | S-1 THEN 改字樣 | ✅ |

### 內部技術選擇(下層,告知即可)
(無)

## 確認紀錄
- 不採 2-decision,兩份並存,產品跟 4-spec | 2026-08-29
