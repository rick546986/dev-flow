# S4-close — 收尾

## 進條件

S3 已回寫。游標在 S4。不要另存第二份 `3-prototype*.md`。

## 讀什麼

`3-prototype.md` 與 2-decision 回寫痕跡。步 4 清單正本是
相對 DEVFLOW_ROOT 的 `_templates/3-prototype.md` 頂註,本檔不抄乘客步原文。

## 寫哪裡

不新開檔。禁止 `3-prototype-*.md`。本節點不搶寫 `2-decision.md`(回寫在 S3)。
本機游標不進 Git。

## 做什麼

依模板頂註步 4 收尾(frontmatter 與內文零矛盾)。
結構圖必須標出 Method 裡的選定 variant;改 variant 名不改圖不得過。
審頁產檔器 `scripts/build-stage3-html.py --action`(正本
`notes/design/stage3-review-ui-contract.md`):有 `3-prototype.md` 才印頁,
沒有就 n-a,不建 html。不改 twin、不進 gate-twin STAGES。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage3-graph.sh --write-cursor S4-close`。

## 完成條件

模板頂註步 4 的完成條件已達成。本機游標在 S4-close。

## 下一跳

N5-end
