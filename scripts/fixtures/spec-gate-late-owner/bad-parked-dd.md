<!-- 負向 fixture(勿當範例照抄):DD 把「不採 Decision, follow 4-spec」停成自判。
     用途:釘住 check-spec-gate.sh C6 必須擋「4-spec 壓未改 Decision」。
     期望:exit 1,且 C6 那列為 ❌。C1–C5 應仍綠,證明是 C6 在咬。 -->

---
feature: late-owner-parked-dd
stage: 4-spec
status: draft
---

# 4. 規格 — late-owner parked DD

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
| DD-1 | 不採 Decision, follow 4-spec | 產品跟 4-spec 不跟 Decision | [Assumption] | 兩份並存 | ✅ |

### 內部技術選擇(下層,告知即可)
(無)

## 確認紀錄
- R 範圍確認 | 2026-08-29
