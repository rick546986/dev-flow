# N-skip

## 進條件

N1 九條全未命中。若其實有命中 → 本節點不是入口,走 fork_required。

## 讀什麼

N1 判定結果。不重抄九條條文。

## 寫哪裡

只覆寫 `docs/dev/<slug>/3-prototype.md`,不另存。禁止第二份 `3-prototype*.md`。
不建 `3-prototype.html`。

## 做什麼

寫最小 `3-prototype.md`:status approved + 九條全未勾。不建 html。
Agent 不得代決跳過。
跑 `scripts/check-devstage3-graph.sh --write-cursor N-skip`。

## 完成條件

該 slug 有一份最小 `3-prototype.md`。游標在 N-skip。

## 下一跳

無
