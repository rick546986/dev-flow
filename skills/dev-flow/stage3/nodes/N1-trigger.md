# N1-trigger — 觸發判定

## 進條件

`docs/dev/<slug>/2-decision.md` 在,且 frontmatter status=approved(G1 過)。
缺 → 本節點不是入口,退回第 2 站。不要寫 `3-prototype.md`。

## 讀什麼

只讀 `1-discussion.md` 的 Real-world Context(對話不是契約)。
九條正本在相對 DEVFLOW_ROOT 的 `_templates/3-prototype.md`「Stage 3 觸發判定」,本檔不重抄條文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `3-prototype.md`。禁止第二份 `3-prototype*.md`。
本機游標(現在節點)只留在 `.devstage3-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

逐條判定九條,命中打 `[x]`(判定紀錄可記在確認紀錄,或本機游標旁的判定結果;
0 命中不在本節點建檔,交 N-skip 落檔最小觸發判定)。

J3 只在判定做完之後、寫任何 Demo 紀錄之前。在專案根跑（不要另寫 HTTP client；
live 時這支才呼叫同一個 runtime 的 `ask --gate J3`。失敗、逾時、沒開雙閘門 → 不顯示，照原流程）：

```
python3 ${DEVFLOW_ROOT}/scripts/devflow-jev.py handoff --gate J3 --slug <slug> \
  --author-ref <session 或人名> --session-ref <session> \
  --stage3-trigger hit|none \
  --discussion docs/dev/<slug>/1-discussion.md
```

`4-spec.md` 或 `3-prototype.md` 已經存在才加 `--spec`／`--prototype`。
只把 stdout 的 `display` 唸給人（值得人親手 Demo，或 Demo 可選）。
這句不改「命中就要 Demo」：極性不在這裡翻。禁止把這句寫進 Human verdict、禁止寫 ACCEPTED、
禁止寫 Verdict attestation、禁止寫 G2。`writes_verdict` 必須是 false；檔案內容維持原樣。

跑 `${DEVFLOW_ROOT}/scripts/check-devstage3-graph.sh --write-cursor N1-trigger`。

## 完成條件

九條都有判定。本機游標在 N1-trigger。

## 下一跳

0 命中 → N-skip;任一命中 → S0-question。
