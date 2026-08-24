# S2-scenarios — 逐 R 展開 S

## 進條件

S1-requirements 完成:R 清單在檔、範圍經確認。游標在 S1-requirements。
R 清單還沒確認就展開 S = 在未定範圍上寫測試契約,退回 S1。

## 讀什麼

已落檔的 R 清單、`1-discussion.md` 該條驗收雛形的觀測方式。
GWT 精度要求與觀測欄的正本是 `_templates/4-spec.md` 頂註第 2 步與 S-1 樣板,
本檔不抄乘客步原文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/4-spec.md` 的 S 條目與確認紀錄,不另存。
禁止第二份 `4-spec*.md`。`write_mode: overwrite`。本機游標不進 Git。

## 做什麼

一次一個 R 展開 S,每 S 的觀測欄承接雛形;雛形沒寫就在此補齊,
純內部行為註明「無外部現象」。涉人員操作／交接／等待／權限的重要 S 補
Operational Context。段段給使用者確認,確認紀錄節逐段留一行。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage4-graph.sh --write-cursor S2-scenarios`。

## 完成條件

全 R 已展開、每 S 有觀測欄、每段有確認紀錄。只有一份 `4-spec.md`。
本機游標在 S2-scenarios。

## 下一跳

S3a-close
