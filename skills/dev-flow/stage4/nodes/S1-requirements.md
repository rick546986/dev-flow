# S1-requirements — 雙源列 R

## 進條件

N1-handoff 完成(G1 過、第 3 站若必要已收尾、雙源清點已回報)。游標在 N1-handoff。
`docs/dev/<slug>/2-decision.md` status=approved。缺 → 退回第 2 站,不要在這裡補。

## 讀什麼

`1-discussion.md` 的驗收雛形逐條、living spec 受本次變更影響的條文原文。
步 1 的完成條件正本是相對 DEVFLOW_ROOT 的 `_templates/4-spec.md` 頂註第 1 步,本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/4-spec.md` 的 ADDED／MODIFIED／REMOVED 三節與確認紀錄一行,
不另存。禁止第二份 `4-spec*.md`。`write_mode: overwrite`。
本機游標只留在 `.devstage4-cursor.json`,不進 Git。

## 做什麼

驗收雛形逐條升 ADDED;living spec 受影響條文升 MODIFIED／REMOVED 並引原條文。
R 清單的範圍要拿給使用者確認,確認紀錄節留一行。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage4-graph.sh --write-cursor S1-requirements`。

## 完成條件

R 清單範圍經使用者確認且確認紀錄有一行。只有一份 `4-spec.md`。
本機游標在 S1-requirements。

## 下一跳

S2-scenarios
