# N-skip — 全未命中,維持選配

## 進條件

N1 九條全未命中。若其實有命中 → 本節點不是入口,走 `fork_required`。

## 讀什麼

N1 判定結果(九條皆未勾)。不重抄九條條文。`graph.yaml` 是下一跳正本。

## 寫哪裡

不建 `3-prototype.md`、不建 `3-prototype.html`。禁止第二份 `3-prototype*.md`。
本機游標只留在 `.devstage3-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

維持選配、兩檔都不建。人類若要在「必要」時仍跳過 → 必須已有 2-decision
流程層 Owner Call,該行同時含「Stage 3」與「跳過」;Agent 不得代決。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage3-graph.sh --write-cursor N-skip`。

## 完成條件

repo 裡沒有該 slug 的 `3-prototype*.md`。游標在 N-skip。

## 下一跳

無
