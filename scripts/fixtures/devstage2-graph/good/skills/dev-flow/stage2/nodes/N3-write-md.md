# N3-write-md

## 進條件

步 1–2 已完成。游標準備寫檔。`1-discussion.md` 仍是 approved。

## 讀什麼

已確認的決策點、步 1–2 的方案與壓測結果。模板頂註步 3 是定稿清單正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/2-decision.md`,不另存。
禁止第二份 `2-decision*.md`。`write_mode: overwrite`。

## 做什麼

按模板寫同一份 `2-decision.md`。重跑覆寫同一路徑。
跑 `scripts/check-devstage2-graph.sh --write-cursor N3-write-md`。

## 完成條件

該 slug 目錄只有一份 `2-decision.md`。定稿節齊、無佔位符。

## 下一跳

S4-oc
