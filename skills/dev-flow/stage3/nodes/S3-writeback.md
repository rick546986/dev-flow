# S3-writeback — 回寫 2-decision

## 進條件

N3 已覆寫同一份 `3-prototype.md`。游標在 S3。
不要另存第二份 `2-decision*.md` 或 `3-prototype*.md`。

## 讀什麼

已落檔的 `3-prototype.md`。步 3 清單正本是 `_templates/3-prototype.md` 頂註,
本檔不抄乘客步原文。

## 寫哪裡

只准改同一份 `docs/dev/<slug>/2-decision.md` 的確認紀錄行 + 對應條,
`write_mode: overwrite`,不另存。禁止第二份 `2-decision*.md`。
本機游標不進 Git。

## 做什麼

依模板頂註步 3 回寫同一份 `2-decision.md`。本節點不搶寫整份決策檔。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage3-graph.sh --write-cursor S3-writeback`。

## 完成條件

確認紀錄留一行,對應條已更新。本機游標在 S3-writeback。

## 下一跳

S4-close
