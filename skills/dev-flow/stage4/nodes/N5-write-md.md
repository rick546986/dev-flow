# N5-write-md — 定稿落檔

## 進條件

步 1–4 完成(R 清單經確認、S 逐 R 展開且每 S 有觀測欄、3a-c 收尾、
Drafting Decisions 清點已能落檔)。本節點只寫一份 `4-spec.md`。

## 讀什麼

步 1–4 已能落檔的內容。執行清單正本仍是 `_templates/4-spec.md` 頂註 1–4;
本檔不抄乘客步原文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/4-spec.md`,不另存。禁止第二份 `4-spec*.md`。
html twin 不在本節點產(N6 才呼叫現有工具)。`write_mode: overwrite`。
本機游標不進 Git。

## 做什麼

把步 1–4 的內容寫進同一檔。重跑本節點 = 覆寫同一路徑,不是另存一份。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage4-graph.sh --write-cursor N5-write-md`。

## 完成條件

只有一份 `4-spec.md`。游標在 N5-write-md。

## 下一跳

skill-legacy-5
(步 5 自檢在下一個 hop;本節點不跑 `check-spec-gate.sh`)
