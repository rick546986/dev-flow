# N1-handoff — 接手盤點

## 進條件

`docs/dev/<slug>/1-discussion.md` 在,且 frontmatter status=approved。
Open Questions 全三態(`[x]` 已解 / `[~]` 帶假設 / `[>]` 移交)。
缺任何一項 → 本節點不是入口,退回討論。不要寫 `2-decision.md`。

## 讀什麼

只讀 `1-discussion.md`(對話不是契約)與長期記憶查詢結果。
執行清單正本仍是相對 DEVFLOW_ROOT 的 `_templates/2-decision.md` 頂註 0–7;本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `2-decision.md`。禁止第二份 `2-decision*.md`。
本機游標(現在節點)只留在 `.devstage2-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

J1（討論已 approved、本節點開始之前；沒有 key、沒有 `.dev-flow/jev.yaml`、失敗、逾時，都當作沒啟用，照下面原文繼續）。
在專案根跑（不要另寫 HTTP client；這支在雙閘門 live 時才呼叫同一個 runtime 的 `ask --gate J1`）：

```
python3 ${DEVFLOW_ROOT}/scripts/devflow-jev.py handoff --gate J1 --slug <slug> \
  --author-ref <session 或人名> --session-ref "$MEMORY_SESSION_ID" \
  --discussion docs/dev/<slug>/1-discussion.md
```

讀 stdout JSON 的 `effect`（`GRADUATED` 仍是 false；本命令不寫 `2-decision.md`、不寫任何 verdict）：

- `continue_existing_flow` → 照下面原文繼續。
- `start_decide` → 不要再問一次「夠清楚嗎」，直接做下面的決策點清點。
- `ask_more` → 停。把 `theme` 唸給人。請人另開一場完整 dev-talk（11 步，收尾仍要人點頭）。
  該場從 S0、S1、S2 重盤。`instruction` 寫明：上一份討論稿不是已核事實，不得靠讀舊討論省一輪，讀取白名單不是機械執行。
  主題句不得改寫成題組原文。不要寫游標，不要進下一跳。
- `needs_owner_decision` → 停。請 owner 做價值或產品選擇。第二輪仍不清楚時，命令自己改成這個，不要再開第三輪。

從 Goals / 驗收雛形 / `[>]` 移交項提煉「待收斂決策點」,連同討論期
owner 已自拍的板一併清點,給人確認。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage2-graph.sh --write-cursor N1-handoff`。

## 完成條件

確認紀錄節留一行(決策點清單經使用者確認)。本機游標在 N1-handoff。

## 下一跳

S1-approaches
