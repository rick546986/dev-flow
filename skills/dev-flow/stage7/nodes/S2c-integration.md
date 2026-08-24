# S2c-integration — 整合回歸

## 進條件

S2b-phenomena 完成:現象證據已在同一份 `7-review.md`。游標在 S2b-phenomena。
這是最後一次准許改碼／改 HEAD。不要讀 6-notes。

## 讀什麼

現有整合回歸工具的契約與已落檔的 `7-review.md`。
禁讀 `6-implementation-notes.md` 的 Self-Review。
步 2c 正本是 `_templates/7-review.md` 頂註,本檔不抄乘客步原文、不重寫那支腳本。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/7-review.md` 的整合回歸結論(含腳本印出的 SHA),不另存。
禁止第二份 `7-review*.md`。`write_mode: overwrite`。
本機游標不進 Git。不准改 `docs/dev/tools/devflow-integration-regression.sh`。

## 做什麼

呼叫現有 `docs/dev/tools/devflow-integration-regression.sh`(或
`scripts/devflow-integration-regression.sh`)。**必須在 Final Fresh 之前** —
順序寫死為整合回歸 → 再進 S2d-fresh,不是 Fresh 完才合併。
不重寫那支腳本。Verdict 後改碼作廢 G3 由現有工具釘住,本節點不另寫通過條件。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage7-graph.sh --write-cursor S2c-integration`。

## 完成條件

整合回歸結論(含 SHA)已在同一份 `7-review.md`。HEAD 已是送審樹。
只有一份 `7-review.md`。本機游標在 S2c-integration。

## 下一跳

S2d-fresh
