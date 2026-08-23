# N8-end — 過 G1 後三連動

## 進條件

已過 G1。游標在 N8。N7 的 verdict 已在。

## 讀什麼

G1 verdict。`2-decision.md` frontmatter。`docs/dev/STATUS.md`。同名 html twin。
三條件中 → `docs/adr/`。

## 寫哪裡

三連動:frontmatter / STATUS / twin。不另存第二份 `2-decision*.md`。
三條件全中才抄 `docs/adr/`。本機游標不進 Git。

## 做什麼

過 G1 後做三連動(frontmatter / STATUS / twin)。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage2-graph.sh --write-cursor N8-end`。

## 完成條件

三連動齊。本場第 2 站結束。

## 下一跳

無
