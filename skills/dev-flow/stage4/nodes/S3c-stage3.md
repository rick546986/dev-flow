# S3c-stage3 — Stage 3 對帳

## 進條件

S3b-profile 完成:Verification Profile 與 Design Boundary Contract 有結論。
游標在 S3b-profile。沒有 Stage 3 的 feature 也要走本節點,記 N/A,不准跳過。

## 讀什麼

`3-prototype.md` 的 Demo Script 場景與 verdict、Method 走查條列、
Operational Context 的 `Recovery:` 欄位;以及已落檔的 R／S 與 Out of Scope。
對帳判準正本是相對 DEVFLOW_ROOT 的 `_templates/4-spec.md` 頂註第 3c 步,本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/4-spec.md` 裡對帳的下落(補 R／S,或在 Out of Scope
明列排除理由),不另存。不寫 `3-prototype.md` —— 那是第 3 站的產物。
禁止第二份 `4-spec*.md`。`write_mode: overwrite`。本機游標不進 Git。

## 做什麼

逐一核對每個 ACCEPTED 場景:對應至少一條 R／S,或在 Out of Scope 明列排除理由。
Human verdict ≠ ACCEPTED 的互動 S 不得定案 —— 列 Drafting Decisions 待裁決,
或退回第 3 站重新 Demo。沒有 Stage 3 時整節記 N/A。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage4-graph.sh --write-cursor S3c-stage3`。

## 完成條件

Stage 3 對帳逐場有下落(或整節 N/A)。只有一份 `4-spec.md`。
本機游標在 S3c-stage3。

## 下一跳

S4-dd
