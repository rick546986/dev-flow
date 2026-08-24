# S4-selfcheck — 自檢四必填欄

## 進條件

N4-write-md 完成:`docs/dev/<slug>/5-tasks.md` 已落檔,而且只有一份。
游標在 N4-write-md。

## 讀什麼

已落檔的 `5-tasks.md`。四必填欄與續行禁令的條文正本是 `_templates/5-tasks.md`
頂註,本檔不重抄。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/5-tasks.md` 把缺欄補回去,不另存。
禁止第二份 `5-tasks*.md`。`write_mode: overwrite`。本機游標不進 Git。

## 做什麼

呼叫既有 `contract_ref.py` 的 `parse_5_tasks` 逐 T 判四必填欄
(Covers／Files／Verify／Blocked-by):`errors` 非空就是缺欄,或續行踩了保留欄名
把真欄位遮蔽掉 —— 兩種都會讓 `start` fail-closed 拒啟。回頭補 `5-tasks.md`,
不改那支 parser,也不在本站另寫第二套解析。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage5-graph.sh --write-cursor S4-selfcheck`。

## 完成條件

`parse_5_tasks` 的 `errors` 為空(逐 T 零缺欄、零保留欄遮蔽)。
只有一份 `5-tasks.md`。本機游標在 S4-selfcheck。

## 下一跳

N5-twin
