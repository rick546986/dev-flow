# S2-run — 親跑驗證

## 進條件

N1-matrix 完成:coverage matrix 全列填畢(未參考作者主張)。游標在 N1-matrix。
矩陣沒填完就開跑 = 不知道缺哪一列,退回 N1-matrix。不要讀 6-notes。

## 讀什麼

只讀 `4-spec.md` 的 S 清單與測試檔。禁讀 `6-implementation-notes.md` 的 Self-Review。
步 2 完成條件正本是相對 DEVFLOW_ROOT 的 `_templates/7-review.md` 頂註第 2 步,本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/7-review.md` 的驗證結果／矩陣實跑欄,不另存。
禁止第二份 `7-review*.md`。`write_mode: overwrite`。
本機游標只留在 `.devstage7-cursor.json`,不進 Git。

## 做什麼

親跑本次 S 測試 + 既有全套,兩份輸出入同一份 `7-review.md`。
不在這裡讀 Self-Review、不另開檔。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage7-graph.sh --write-cursor S2-run`。

## 完成條件

兩輸出在案。只有一份 `7-review.md`。本機游標在 S2-run。

## 下一跳

S2b-phenomena
