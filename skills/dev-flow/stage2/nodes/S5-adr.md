# S5-adr — ADR 晉升檢查

## 進條件

S4 已完成。游標在 S5。同一份 `2-decision.md` 仍在。
不要另存第二份 `2-decision*.md`。

## 讀什麼

已落檔的 `2-decision.md`。步 5 清單正本是相對 DEVFLOW_ROOT 的 `_templates/2-decision.md` 頂註,
本檔不抄乘客步原文。三條件中才抄 `docs/adr/`。

## 寫哪裡

同一份 `docs/dev/<slug>/2-decision.md` 的 ADR 檢查節,不另存。
三條件全中才抄 `docs/adr/`。禁止第二份 `2-decision*.md`。本機游標不進 Git。

## 做什麼

依模板頂註步 5 做 ADR 晉升檢查。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage2-graph.sh --write-cursor S5-adr`。

## 完成條件

模板頂註步 5 的完成條件已達成。本機游標在 S5-adr。

## 下一跳

S6-selfcheck
