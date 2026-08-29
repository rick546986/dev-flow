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
晚改可見行為先改本檔 Decision / Owner Call,不准只讓 4-spec 改口。
跑 `scripts/check-devstage2-graph.sh --write-cursor N3-write-md`。

## 完成條件

該 slug 目錄只有一份 `2-decision.md`。定稿節齊、無佔位符。
晚改可見行為:G3 未過先改 Decision / Owner Call,再走 4→5→6→7;
G3 已過另開薄刀;純文字走 HISTORY。1-discussion 留當時說法加改口。

## 下一跳

S4-oc
