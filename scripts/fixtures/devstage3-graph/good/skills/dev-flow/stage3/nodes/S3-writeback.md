# S3-writeback

## 進條件

N3 已覆寫同一份 `3-prototype.md`。不要另存第二份 `2-decision*.md`。

## 讀什麼

已落檔的 `3-prototype.md`。步 3 正本是模板頂註,本檔不抄原文。

## 寫哪裡

同一份 `docs/dev/<slug>/2-decision.md` 的確認紀錄行 + 對應條,overwrite。

## 做什麼

依模板頂註步 3 回寫同一份 `2-decision.md`。
跑 `scripts/check-devstage3-graph.sh --write-cursor S3-writeback`。

## 完成條件

確認紀錄留一行。本機游標在 S3-writeback。

## 下一跳

S4-close
