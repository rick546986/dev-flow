# N3-write-md — 定稿落檔

## 進條件

步 1–2 已完成。`1-discussion.md` 仍是 approved。游標準備寫檔。
本節點只寫一份 `2-decision.md`。

## 讀什麼

已確認的決策點、步 1–2 的方案與壓測結果。
定稿清單正本是相對 DEVFLOW_ROOT 的 `_templates/2-decision.md` 頂註步 3,本檔不抄原文。

## 寫哪裡

只覆寫 `docs/dev/<slug>/2-decision.md`,不另存。
禁止第二份 `2-decision*.md`。`write_mode: overwrite`。
本機游標不進 Git。

## 做什麼

按模板定稿節寫同一份 `2-decision.md`。重跑本節點 = 覆寫同一路徑,不是另存一份。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage2-graph.sh --write-cursor N3-write-md`。

## 完成條件

該 slug 目錄只有一份 `2-decision.md`。定稿節齊、無佔位符。

## 下一跳

S4-oc
