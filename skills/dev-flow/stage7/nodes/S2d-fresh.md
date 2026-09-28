# S2d-fresh — Final Fresh

## 進條件

S2c-integration 完成:整合回歸已落在 Final Fresh 之前。游標在 S2c-integration。
整合回歸還沒做就 Fresh = 出貨樹不是審過的樹,退回 S2c-integration。
不要讀 6-notes。

## 讀什麼

`4-spec.md` 的 Verification Profile,以及已落檔的 `7-review.md`。
禁讀 `6-implementation-notes.md` 的 Self-Review。
步 2d 正本是相對 DEVFLOW_ROOT 的 `_templates/7-review.md` 頂註,本檔不抄乘客步原文、不重寫 Gauntlet。
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
Gauntlet 用 `--report docs/dev/<slug>/evidence/gauntlet-report.md` 把結果落檔(J5 shadow 的
evidence 綁定讀這一份)。
evidence 落檔之後、進 S2e 之前,跑一次(W4 P1-F4;零網路、不等 HTTP、失敗 exit 0 照走):
`python3 ${DEVFLOW_ROOT}/scripts/devflow-jev.py enqueue --slug <slug> --author-ref <實作 agent> --session-ref <本 session>`
它只把 J5 shadow evaluation 序列化進 gitignored queue;沒 key／沒 opt-in／evidence 未固定一律 noop。
不看它的輸出決定任何事;G3 照原路走。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage7-graph.sh --write-cursor S2d-fresh`。

## 完成條件

gauntlet 輸出在案(或降級聲明在案)。Source SHA = 當下 HEAD。enqueue 已跑過一次(結果不影響本節點完成)。
只有一份 `7-review.md`。本機游標在 S2d-fresh。

## 下一跳

S2e-walkthrough
