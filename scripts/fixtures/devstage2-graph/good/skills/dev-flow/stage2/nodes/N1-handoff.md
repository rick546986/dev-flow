# N1-handoff

## 進條件

`docs/dev/<slug>/1-discussion.md` 在,且 frontmatter status=approved。
Open Questions 全三態(`[x]` / `[~]` / `[>]`)。缺 → 退回討論,不要進本節點。

## 讀什麼

只讀 `1-discussion.md` 與長期記憶查詢結果。執行清單正本仍是
`_templates/2-decision.md` 頂註 0–7,本檔不抄乘客步原文。

## 寫哪裡

不寫 `2-decision.md`。禁止第二份 `2-decision*.md`。
本機游標只留在 `.devstage2-cursor.json`,不進 Git。

## 做什麼

從 Goals / 驗收雛形 / `[>]` 移交項提煉決策點清單,給人確認。
跑 `scripts/check-devstage2-graph.sh --write-cursor N1-handoff`。

## 完成條件

確認紀錄節有一行(決策點清單經使用者確認)。本機游標在 N1-handoff。

## 下一跳

S1-approaches
