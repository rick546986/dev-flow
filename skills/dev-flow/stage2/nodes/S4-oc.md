# S4-oc — Owner Calls 清點

## 進條件

N3 已覆寫同一份 `2-decision.md`。游標在 S4。
不要另存第二份 `2-decision*.md`。

## 讀什麼

已落檔的 `2-decision.md`。步 4 清單正本是相對 DEVFLOW_ROOT 的 `_templates/2-decision.md` 頂註,
本檔不抄乘客步原文。

## 寫哪裡

同一份 `docs/dev/<slug>/2-decision.md` 的 Owner Calls 節,不另存。
禁止第二份 `2-decision*.md`。本機游標不進 Git。

## 做什麼

依模板頂註步 4 清點 Owner Calls。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage2-graph.sh --write-cursor S4-oc`。

## 完成條件

模板頂註步 4 的完成條件已達成。本機游標在 S4-oc。

## 下一跳

S5-adr
