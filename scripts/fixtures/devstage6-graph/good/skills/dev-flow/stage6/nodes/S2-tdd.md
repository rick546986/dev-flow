# S2-tdd — 逐 T(一顆 hop)

## 進條件

N2-handoff 完成:todo 與 5-tasks 一一對應。已武裝
(`6-implementation-notes.md` 有 `FORK_INTEGRATION_SHA` 40 碼)且
5-tasks status=approved。缺任何一項 → 本節點不是入口,退回 N2-handoff
或 N1-arm。游標在 N2-handoff。

## 讀什麼

只讀 `4-spec.md`、`5-tasks.md`、已落檔的 `6-implementation-notes.md`。
禁讀 1/2/3(圍欄②;本節點不改守衛,只遵守)。
逐 T 動線正本是指南 `#five-laws`／`#stage6`,本檔不抄原文。乘客清單步 2 正本是
`_templates/6-implementation-notes.md` 頂註,本檔不重抄。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/6-implementation-notes.md`(TDD Evidence／
T Review Log／Progress Log),不另存。禁止第二份
`6-implementation-notes*.md`。`write_mode: overwrite`。
不准改 `FORK_INTEGRATION_SHA`(寫了不准改)。本機游標只留在
`.devstage6-cursor.json`,不進 Git。不改 `.dev-flow`。
不改 `devflow-exec.sh`、`_guard_impl.py`、Gauntlet、平行引擎。

## 做什麼

逐 T 走現有 `dev-run` 引擎或手動實作,共用指南 `#five-laws`／`#stage6` 動線。
**不是一 T 一 hop** —— 不准為每個 T-id 長一顆 graph 節點;拓撲序
仍由引擎／Blocked-by 跑,本 hop 只是那條動線的入口。
不在這裡另寫第二套執行器。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage6-graph.sh --write-cursor S2-tdd`。

## 完成條件

全 T 已依指南 `#five-laws`／`#stage6` 走完(證據在同一份 `6-implementation-notes.md`)。
只有一份 `6-implementation-notes.md`。錨點未被改寫。本機游標在 S2-tdd。

## 下一跳

N4-selfcheck
