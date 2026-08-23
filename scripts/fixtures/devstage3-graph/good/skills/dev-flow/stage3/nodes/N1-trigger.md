# N1-trigger

## 進條件

`2-decision.md` status=approved(G1 過)。缺 → 退回第 2 站。不要寫 `3-prototype.md`。

## 讀什麼

只讀 `1-discussion.md` 的 Real-world Context。九條正本在模板,本檔不重抄條文。

## 寫哪裡

不寫 `3-prototype.md`。游標只留 `.devstage3-cursor.json`。

## 做什麼

逐條判定九條。0 命中不准建 `3-prototype.md`。
跑 `scripts/check-devstage3-graph.sh --write-cursor N1-trigger`。

## 完成條件

九條都有判定。本機游標在 N1-trigger。

## 下一跳

0 命中 → N-skip;任一命中 → S0-question。
