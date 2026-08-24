# N0-role — 角色與閱讀順序

## 進條件

`docs/dev/<slug>/4-spec.md` 在,且 frontmatter status=approved(G2 過)。
缺 → 本節點不是入口,退回第 4 站。不要寫 `7-review.md`。

## 讀什麼

先讀 `4-spec.md`／`5-tasks.md`／diff／測試。
**此刻禁讀** `6-implementation-notes.md` 的 Self-Review。
owner 自審必須有獨立「限制聲明」節;沒有這一節的 owner 自審視同未審。
乘客清單正本是相對 DEVFLOW_ROOT 的 `_templates/7-review.md` 頂註 0,本檔不重抄步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `7-review.md`。禁止 `7-review-*.md` 與 `7-self-review.md`。
本機游標只留在 `.devstage7-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

核前站 G2、聲明閱讀順序、若走 owner 自審則寫限制聲明節。不要讀 6-notes。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage7-graph.sh --write-cursor N0-role`。

## 完成條件

閱讀順序聲明在案(+ owner 自審時的限制聲明節)。本機游標在 N0-role。

## 下一跳

N1-matrix
