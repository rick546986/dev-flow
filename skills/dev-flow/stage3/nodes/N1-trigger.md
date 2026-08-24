# N1-trigger — 觸發判定

## 進條件

`docs/dev/<slug>/2-decision.md` 在,且 frontmatter status=approved(G1 過)。
缺 → 本節點不是入口,退回第 2 站。不要寫 `3-prototype.md`。

## 讀什麼

只讀 `1-discussion.md` 的 Real-world Context(對話不是契約)。
九條正本在 `_templates/3-prototype.md`「Stage 3 觸發判定」,本檔不重抄條文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `3-prototype.md`。禁止第二份 `3-prototype*.md`。
本機游標(現在節點)只留在 `.devstage3-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

逐條判定九條,命中打 `[x]`(判定紀錄可記在確認紀錄,或本機游標旁的判定結果;
0 命中不准建 `3-prototype.md`)。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage3-graph.sh --write-cursor N1-trigger`。

## 完成條件

九條都有判定。本機游標在 N1-trigger。

## 下一跳

0 命中 → N-skip;任一命中 → S0-question。
