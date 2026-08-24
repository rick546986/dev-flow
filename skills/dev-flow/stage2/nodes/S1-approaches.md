# S1-approaches — 方案生成

## 進條件

N1 已完成。確認紀錄節有一行。游標在 S1。
`1-discussion.md` 仍是 approved。不要寫第二份 `2-decision*.md`。

## 讀什麼

N1 確認過的決策點。`1-discussion.md` 事實與 `[Assumption]`。
步 1 清單正本是 `_templates/2-decision.md` 頂註,本檔不抄乘客步原文。

## 寫哪裡

不另存 `2-decision*.md`。本節點不覆寫整份 `2-decision.md`(寫檔在 N3)。
本機游標只留在 `.devstage2-cursor.json`,不進 Git。

## 做什麼

依模板頂註步 1 產出方案表,給後續 N3 落檔。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage2-graph.sh --write-cursor S1-approaches`。

## 完成條件

模板頂註步 1 的完成條件已達成。本機游標在 S1-approaches。

## 下一跳

S2-stress
