# N4-write-md — 定稿落檔

## 進條件

步 1–3 完成(T 已按 tracer bullet 切、四必填欄已填、`Blocked-by` 拓撲序已核)。
本節點只寫一份 `5-tasks.md`。

## 讀什麼

步 1–3 已能落檔的內容。執行清單正本仍是 `_templates/5-tasks.md` 頂註 1–3;
本檔不抄乘客步原文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/5-tasks.md`,不另存。禁止第二份 `5-tasks*.md`。
html twin 不在本節點產(N5-twin 才呼叫現有工具)。`write_mode: overwrite`。
本機游標不進 Git。

## 做什麼

把步 1–3 的內容寫進同一檔。重跑本節點 = 覆寫同一路徑,不是另存一份。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage5-graph.sh --write-cursor N4-write-md`。

## 完成條件

只有一份 `5-tasks.md`。游標在 N4-write-md。

## 下一跳

S4-selfcheck
(四必填欄自檢在下一個節點;本節點不跑 `contract_ref.py`、不改它)
