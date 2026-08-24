# S2d-fresh — Final Fresh

## 進條件

S2c-integration 完成:整合回歸已落在 Final Fresh 之前。游標在 S2c-integration。
整合回歸還沒做就 Fresh = 出貨樹不是審過的樹,退回 S2c-integration。
不要讀 6-notes。

## 讀什麼

`4-spec.md` 的 Verification Profile,以及已落檔的 `7-review.md`。
禁讀 `6-implementation-notes.md` 的 Self-Review。
步 2d 正本是 `_templates/7-review.md` 頂註,本檔不抄乘客步原文、不重寫 Gauntlet。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/7-review.md` 的 Verification Evidence,不另存。
禁止第二份 `7-review*.md`。`write_mode: overwrite`。
本機游標不進 Git。不准改 `docs/dev/tools/devflow-evidence-gauntlet.sh`、
Evidence 契約、空欄擋、層名全等、「出貨樹=審過的樹」、Final Fresh 綁 SHA。

## 做什麼

呼叫現有 `docs/dev/tools/devflow-evidence-gauntlet.sh`(或
`scripts/devflow-evidence-gauntlet.sh`)。Source SHA = 當下 HEAD = 送審樹。
不重寫 Gauntlet,不另寫通過條件。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage7-graph.sh --write-cursor S2d-fresh`。

## 完成條件

gauntlet 輸出在案(或降級聲明在案)。Source SHA = 當下 HEAD。
只有一份 `7-review.md`。本機游標在 S2d-fresh。

## 下一跳

S2e-walkthrough
