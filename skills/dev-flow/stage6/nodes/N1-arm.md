# N1-arm — 起手武裝(0a／0b／0c)

## 進條件

`docs/dev/<slug>/5-tasks.md` 在,且 frontmatter status=approved。
缺 → 本節點不是入口,退回第 5 站。4-spec 也必須已 approved(G2 過)。
沒有 5-tasks 定案不准寫 `6-implementation-notes.md`。

## 讀什麼

只讀 `4-spec.md` 與 `5-tasks.md`。禁讀 1/2/3(圍欄②;本節點不改守衛,只遵守)。
乘客清單正本是 `_templates/6-implementation-notes.md` 頂註 0a／0b／0c,
本檔不重抄步原文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/6-implementation-notes.md`,不另存。
禁止第二份 `6-implementation-notes*.md`。本機游標只留在
`.devstage6-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

0a 開 branch 與錨點、0b worktree 隔離確認、0c 守衛與 doctor 自檢 ——
細節走模板頂註,這裡不重抄。把 `FORK_INTEGRATION_SHA` 以 40 碼小寫 hex
寫進本檔固定欄;寫了不准改。沒武裝(本節點未完成)不准開工。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage6-graph.sh --write-cursor N1-arm`。

## 完成條件

`FORK_INTEGRATION_SHA` 已記進同一份 `6-implementation-notes.md`(40 碼全長);
0b／0c 完成條件見模板。本機游標在 N1-arm。

## 下一跳

N2-handoff
