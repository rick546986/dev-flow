# N5-twin — 產執行板

## 進條件

S4-selfcheck 完成:`parse_5_tasks` 的 `errors` 為空 —— 逐 T 四必填欄
(Covers／Files／Verify／Blocked-by)齊、續行未踩保留欄名。
`5-tasks.md` 已落檔。不要寫 `5-tasks.md`。

## 讀什麼

已落檔的 `5-tasks.md`。執行板四要求(動線頂區五格／任務卡逐條可勾／Boundaries
摺疊／依賴 DAG)正本在 `_templates/5-tasks.md` 頂註,本檔不重抄條文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不覆寫 `5-tasks.md`(產 html twin 用現有工具,輸出 `5-tasks.html`)。
禁止第二份 `5-tasks*.md`。本機游標不進 Git。

## 做什麼

只呼叫現有 `docs/dev/tools/build-gate-twin.py`(母版在 `scripts/`)產
`5-tasks.html` —— 不改那支腳本。它讀 md 逐條解析,解析不到任何一個 T 會直接
失敗,那就是回頭修 `5-tasks.md`、不是改工具。切 T 的機械提示
`scripts/check-task-slicing.sh` 是 warning-only、永不 exit 1,本節點照舊只呼叫,
不改它的退出碼;四必填欄的機器判準仍是既有 `hooks/contract_ref.py`,一併不改。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage5-graph.sh --write-cursor N5-twin`。

## 完成條件

`5-tasks.html` 在,四件事(五格／可勾／摺疊／DAG)逐項核對過。游標在 N5-twin。

## 下一跳

N6-end
