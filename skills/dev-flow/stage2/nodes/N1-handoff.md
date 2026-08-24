# N1-handoff — 接手盤點

## 進條件

`docs/dev/<slug>/1-discussion.md` 在,且 frontmatter status=approved。
Open Questions 全三態(`[x]` 已解 / `[~]` 帶假設 / `[>]` 移交)。
缺任何一項 → 本節點不是入口,退回討論。不要寫 `2-decision.md`。

## 讀什麼

只讀 `1-discussion.md`(對話不是契約)與長期記憶查詢結果。
執行清單正本仍是相對 DEVFLOW_ROOT 的 `_templates/2-decision.md` 頂註 0–7;本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `2-decision.md`。禁止第二份 `2-decision*.md`。
本機游標(現在節點)只留在 `.devstage2-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

從 Goals / 驗收雛形 / `[>]` 移交項提煉「待收斂決策點」,連同討論期
owner 已自拍的板一併清點,給人確認。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage2-graph.sh --write-cursor N1-handoff`。

## 完成條件

確認紀錄節留一行(決策點清單經使用者確認)。本機游標在 N1-handoff。

## 下一跳

S1-approaches
