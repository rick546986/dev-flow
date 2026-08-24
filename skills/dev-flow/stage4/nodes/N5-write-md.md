# N5-write-md — 定稿落檔

## 進條件

S1／S2／S3a／S3b／S3c／S4 都完成(R 清單經確認、S 逐 R 展開且每 S 有觀測欄、
四小節齊、Profile 與 Design Boundary 有結論、Stage 3 對帳有下落、DD 掃描零殘留)。
游標在 S4-dd。本節點只寫一份 `4-spec.md`。

## 讀什麼

S1–S4 已落檔的內容。執行清單正本仍是 `_templates/4-spec.md` 頂註 1–4;
本檔不抄乘客步原文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/4-spec.md`,不另存。禁止第二份 `4-spec*.md`。
html twin 不在本節點產(N6 才呼叫現有工具)。`write_mode: overwrite`。
本機游標不進 Git。

## 做什麼

把 S1–S4 的內容定稿在同一檔:全節到齊、行為流程圖(R 級)在、frontmatter 補上。
重跑本節點 = 覆寫同一路徑,不是另存一份。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage4-graph.sh --write-cursor N5-write-md`。

## 完成條件

只有一份 `4-spec.md`,全節到齊可送機械關卡。游標在 N5-write-md。

## 下一跳

S5-gate
(步 5 自檢在下一個節點;本節點不跑 `check-spec-gate.sh`)
