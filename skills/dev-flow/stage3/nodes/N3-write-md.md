# N3-write-md — 定稿落檔

## 進條件

N1 任一命中,且步 0–2 完成(Question／Method／Result 已能落檔)。
本節點只寫一份 `3-prototype.md`。

## 讀什麼

步 0–2 已能落檔的內容。執行清單正本仍是相對 DEVFLOW_ROOT 的 `_templates/3-prototype.md` 頂註 0–2;
本檔不抄乘客步原文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/3-prototype.md`,不另存。禁止第二份 `3-prototype*.md`。
code 進 throwaway branch,禁進 main。`write_mode: overwrite`。
本機游標不進 Git。

## 做什麼

把 0–2 的內容寫進同一檔。重跑本節點 = 覆寫同一路徑,不是另存一份。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage3-graph.sh --write-cursor N3-write-md`。

## 完成條件

只有一份 `3-prototype.md`。游標在 N3-write-md。

## 下一跳

S3-writeback
(本節點不搶寫 2-decision;回寫在 S3、收尾在 S4)
