# S1-slice — 切 T

## 進條件

N1-handoff 完成(G2 過、4-spec 的 R/S 全集已清點回報)。游標在 N1-handoff。
`docs/dev/<slug>/4-spec.md` status=approved。缺 → 退回第 4 站,不要在這裡補。

## 讀什麼

`4-spec.md` 的 R/S 原文與 Verification Profile。
步 1 的完成條件正本是 `_templates/5-tasks.md` 頂註第 1 步,本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/5-tasks.md` 的 T 標題與順序,不另存。
禁止第二份 `5-tasks*.md`。`write_mode: overwrite`。
本機游標只留在 `.devstage5-cursor.json`,不進 Git。

## 做什麼

按 tracer bullet 排:先打通最薄的端到端縱切,再逐層加厚。每個 T 都要答得出
「完成後使用者或系統多了什麼可觀測行為」—— 答不出就是水平切層的徵兆,與相鄰 T
合併或重新界定,不得整份按 DB→Repo→Service→API→UI 逐層分。
機械提示 `scripts/check-task-slicing.sh` 是 warning-only、永不 exit 1,本節點只
呼叫、不改它的退出碼,也不拿它取代 reviewer 判斷。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage5-graph.sh --write-cursor S1-slice`。

## 完成條件

每個 T 皆答得出可觀測行為、無按架構層整份切分。只有一份 `5-tasks.md`。
本機游標在 S1-slice。

## 下一跳

S2-fields
