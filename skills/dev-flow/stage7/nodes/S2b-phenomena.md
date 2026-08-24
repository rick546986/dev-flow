# S2b-phenomena — 現象複驗

## 進條件

S2-run 完成:本次 S 測試與既有全套的輸出已在同一份 `7-review.md`。
游標在 S2-run。不要讀 6-notes。

## 讀什麼

只讀 `4-spec.md` 每 S 的觀測方式,以及已落檔的測試輸出。
禁讀 `6-implementation-notes.md` 的 Self-Review;不採信 6-notes 貼的文字。
步 2b 正本是 `_templates/7-review.md` 頂註,本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/7-review.md` 的現象證據表,不另存。
禁止第二份 `7-review*.md`。`write_mode: overwrite`。
本機游標不進 Git。

## 做什麼

照每 S 的觀測方式親自實跑一次,證據入同一份 `7-review.md`。
無外部現象的 S 註明理由。不在這裡讀 Self-Review。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage7-graph.sh --write-cursor S2b-phenomena`。

## 完成條件

每 S 有實跑證據(或無外部現象的理由)。只有一份 `7-review.md`。
本機游標在 S2b-phenomena。

## 下一跳

S2c-integration
