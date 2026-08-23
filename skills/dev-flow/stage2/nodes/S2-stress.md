# S2-stress — 壓測定案

## 進條件

S1 已完成。游標在 S2。`1-discussion.md` 仍是 approved。
不要寫第二份 `2-decision*.md`。

## 讀什麼

S1 的方案表。步 2 清單正本是 `_templates/2-decision.md` 頂註,本檔不抄乘客步原文。

## 寫哪裡

不另存 `2-decision*.md`。本節點不覆寫整份 `2-decision.md`(寫檔在 N3)。
本機游標只留在 `.devstage2-cursor.json`,不進 Git。

## 做什麼

依模板頂註步 2 壓測定案,給後續 N3 落檔。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage2-graph.sh --write-cursor S2-stress`。

## 完成條件

模板頂註步 2 的完成條件已達成。本機游標在 S2-stress。

## 下一跳

N3-write-md
