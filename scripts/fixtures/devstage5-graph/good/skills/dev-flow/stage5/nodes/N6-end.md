# N6-end — owner 自定案

## 進條件

`5-tasks.html` 已產出且四件事核對過。第 5 站不是 gate 站(無 G 編號、免
reviewer 核准),定案權在 owner 自己。

## 讀什麼

`5-tasks.md` frontmatter 與內文、`5-tasks.html`。無 G 條文可引 —— 通過條件
就是「每 T 有 Verify」,正本在 `skills/dev-flow/SKILL.md` 第 5 站那列。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不新開檔。禁止 `5-tasks-*.md`。不寫 `6-implementation-notes.md`
(第 6 站另有游標與武裝步)。本機游標不進 Git。

## 做什麼

owner 自行定案:frontmatter status 由 draft 轉 approved,並核 twin 與 md 一致。
定案前不得動工 —— `devflow-exec.sh start` 的 fail-closed 由既有守衛負責,本節點
只核形狀、不重寫那支工具。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage5-graph.sh --write-cursor N6-end`。

## 完成條件

status=approved,且 twin 與 md 一致。游標在 N6-end。

## 下一跳

無
