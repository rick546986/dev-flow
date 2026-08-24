# S2e-walkthrough — 操作走查

## 進條件

S2d-fresh 完成:Final Fresh 已綁當下 HEAD。游標在 S2d-fresh。
不要讀 6-notes。

## 讀什麼

各 S 的 Operational Context,以及已落檔的 `7-review.md`。
禁讀 `6-implementation-notes.md` 的 Self-Review。
步 2e 正本是 `_templates/7-review.md` 頂註,本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/7-review.md` 的 Operational Walkthrough 表,不另存。
禁止第二份 `7-review*.md`。`write_mode: overwrite`。
本機游標不進 Git。

## 做什麼

以各 S 的 Operational Context 為腳本親自走一遍「人的工作」,表入同一份
`7-review.md`。無 Operational Context 的純內部 S 註明不適用。
不在這裡讀 Self-Review。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage7-graph.sh --write-cursor S2e-walkthrough`。

## 完成條件

表逐 S 填畢(或不適用)。只有一份 `7-review.md`。本機游標在 S2e-walkthrough。

## 下一跳

N3-axes
