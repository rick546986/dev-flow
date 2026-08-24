# N2-handoff — 接手核對

## 進條件

已武裝:`6-implementation-notes.md` 有 `FORK_INTEGRATION_SHA`(40 碼)且
5-tasks status=approved。缺任何一項 → 本節點不是入口,退回 N1-arm 或第 5 站。
不要寫 `6-implementation-notes.md`。

## 讀什麼

只讀 `4-spec.md`(R/S 與 Verification Profile)與 `5-tasks.md`(每 T 的
Verify／Covers／Files／Blocked-by)。禁讀 1/2/3(圍欄②)。
乘客清單正本是 `_templates/6-implementation-notes.md` 頂註步 1,本檔不重抄。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `6-implementation-notes.md`。禁止第二份 `6-implementation-notes*.md`。
本機游標只留在 `.devstage6-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

核前站:4-spec／5-tasks 是否齊(每 T 有 Verify+Covers)。缺 → 停回補。
建 todo 一 T 一項,照 Blocked-by 拓撲序 —— 這是盤點,不是一 T 一 hop。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage6-graph.sh --write-cursor N2-handoff`。

## 完成條件

todo 與 5-tasks 一一對應。本機游標在 N2-handoff。

## 下一跳

S2-tdd
