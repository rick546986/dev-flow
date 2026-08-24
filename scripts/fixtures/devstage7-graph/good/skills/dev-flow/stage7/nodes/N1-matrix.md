# N1-matrix — 自建 coverage matrix

## 進條件

N0-role 完成。本節點不寫 `7-review.md`(寫檔在 S2-* 與 N4-author)。

## 讀什麼

只讀 `4-spec.md` 的 S 清單與測試檔 S-id。禁讀 6-notes Self-Review。
乘客清單正本是 `_templates/7-review.md` 頂註 1,本檔不重抄。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `7-review.md`。禁止第二份 `7-review*.md`。本機游標不進 Git。

## 做什麼

自建 Coverage Matrix(未參考作者主張)。內容先備著,落檔從 S2-run 起覆寫同一份。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage7-graph.sh --write-cursor N1-matrix`。

## 完成條件

矩陣全列填畢。游標在 N1-matrix。

## 下一跳

S2-run
