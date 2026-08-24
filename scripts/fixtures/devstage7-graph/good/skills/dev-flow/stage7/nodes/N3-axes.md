# N3-axes — 雙軸審

## 進條件

skill-legacy-2(模板 2／2b／2c／2d／2e)完成:親跑驗證、現象複驗、
整合回歸在 Final Fresh 之前、Final Fresh 綁 SHA。不要寫 `7-review.md`。

## 讀什麼

已落檔的驗證輸出與 4-spec。禁讀 6-notes Self-Review。
雙軸條文正本是 `_templates/7-review.md` 頂註 3,本檔不重抄。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `7-review.md`。禁止 `7-review-*.md`／`7-self-review.md`。本機游標不進 Git。

## 做什麼

做 Standards + Spec 雙軸審。整合回歸／Verdict 後改碼作廢 G3 由現有工具釘住,不重寫。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage7-graph.sh --write-cursor N3-axes`。

## 完成條件

每 R 有判定、每 F 有鏈且有出處。游標在 N3-axes。

## 下一跳

N4-author
