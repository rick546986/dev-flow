# N7-end — 收尾核對

## 進條件

G2 已有 verdict。`4-spec.md` frontmatter 即將是 approved。游標在 N7。

## 讀什麼

`4-spec.md` frontmatter 與內文、`STATUS.md`、`4-spec.html`。
G2 條件正本 README §7。`graph.yaml` 是下一跳正本。

## 寫哪裡

不新開檔。禁止 `4-spec-*.md`。不寫 `5-tasks.md`(第 5 站另有游標)。
本機游標不進 Git。

## 做什麼

核 status=approved 且三連動一致(frontmatter／`STATUS.md`／html twin)。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage4-graph.sh --write-cursor N7-end`。

## 完成條件

status=approved。游標在 N7-end。

## 下一跳

無
