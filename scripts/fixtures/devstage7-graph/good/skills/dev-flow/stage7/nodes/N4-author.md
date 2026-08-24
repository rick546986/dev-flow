# N4-author — 對照作者並落檔

## 進條件

N3-axes 完成。本節點才准讀 6-notes。

## 讀什麼

此刻才讀 `6-implementation-notes.md`(含 Self-Review)—— 對應
`devflow-exec.sh review-unlock`。先自建矩陣、後讀作者主張。
乘客清單正本是 `_templates/7-review.md` 頂註 4,本檔不重抄。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/7-review.md`,不另存。禁止第二份 `7-review*.md`,
禁止 `7-self-review.md`。`write_mode: overwrite`。本機游標不進 Git。

## 做什麼

把 0–3 的內容與對照作者結果寫進同一份 `7-review.md`。重跑 = 覆寫同一路徑。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage7-graph.sh --write-cursor N4-author`。

## 完成條件

只有一份 `7-review.md`。游標在 N4-author。

## 下一跳

N5-verdict
