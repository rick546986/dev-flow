# S0-question — 定義疑問

## 進條件

N1 任一命中。游標在 S0。不要寫 `3-prototype.md`(寫檔在 N3)。
不要另存第二份 `3-prototype*.md`。

## 讀什麼

`2-decision.md` 的 Risk / open point。步 0 清單正本是
相對 DEVFLOW_ROOT 的 `_templates/3-prototype.md` 頂註,本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不覆寫 `3-prototype.md`(寫檔在 N3)。禁止第二份 `3-prototype*.md`。
本機游標只留在 `.devstage3-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

依模板頂註步 0 定義疑問,給後續 N3 落檔。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage3-graph.sh --write-cursor S0-question`。

## 完成條件

模板頂註步 0 的完成條件已達成。本機游標在 S0-question。

## 下一跳

S1-experiment
