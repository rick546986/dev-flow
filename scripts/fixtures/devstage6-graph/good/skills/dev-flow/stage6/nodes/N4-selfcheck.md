# N4-selfcheck — 自檢

## 進條件

逐 T 循環(README §5 動線)已走完,回歸全綠摘要已在案。不要寫
`6-implementation-notes.md`(本刀寫檔只在 N1-arm)。

## 讀什麼

已落檔的 `6-implementation-notes.md` 與 `5-tasks.md`。
自檢八問正本是 `_templates/6-implementation-notes.md` 頂註步 4,本檔不重抄。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不覆寫 `6-implementation-notes.md`。禁止第二份 `6-implementation-notes*.md`。
本機游標不進 Git。不改 `.dev-flow`。不改 `devflow-exec.sh`。

## 做什麼

對模板步 4 的八問逐項核對。答不出 → 退回 skill-legacy-T(README §5 動線),
不是在這裡發明第二套引擎。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage6-graph.sh --write-cursor N4-selfcheck`。

## 完成條件

八答能對上已落檔內容。游標在 N4-selfcheck。

## 下一跳

N5-end
