# 第 7 站審查頁(截圖槽／進場)

> 第 7 站給人看的 html **版面**正本。`7-review.md` 仍是 **twin／執行板**
> (G3 五格見 `_templates/7-review.md` 頂註),不是這份審查頁。
> 本檔只鎖**頁面樣子**(分組槽／檔名／進場／lightbox／chrome)。
> 直式步驟方塊見並列的 `notes/design/vbox-fig-contract.md`(不改那份)。
> 產檔器:`scripts/build-stage7-html.py`。牙:`scripts/check-stage7-shot-contract.sh`。
> 不改 twin 執行板、不進 `build-gate-twin.py` STAGES。

## 何時用

寫或改第 7 站給人看的審查頁(截圖槽)時。chrome 跟第 2／4／5／6 站同一套,
不要另發明殼、不要另發明 class 名。

## 版面鎖死(已拍板)

下列七條是鎖死,不是口味、不是選配。產檔器吃 md 的 `## 截圖槽`,
沒有該標題時改吃 md 內 `shots/`／`data-shot`／`![](shots/…)` 定名;
再沒有就掃同目錄 `shots/` 七個定名,收成**五組**(不是七個散框):
`plus-two-cells`＋`v30-two-cells`、`manual-keep`、`age-lock`、`opu-note`、
`plan-split-c`＋`plan-split-def`。
`scripts/build-stage7-html.py` 吐分組槽／`data-shot`／`.lb` lightbox／`.e2e` 掛點。
不要只認字面 `lightbox`／`hang-point`。授權 `--action`。不包 markdown-it + html-shell。
寫法落點:`_templates/7-review.md`(本檔是正本,不另開家族、不進 README 第一屏)。

1. **同型分組**:同類型畫面收進槽,不要一坨傾倒。定名七張收成五組。
2. **檔名鎖定**:每個槽有 `data-shot` + `img src="shots/<name>.png"`。
   缺檔顯示佔位,檔案在了就不得再留過期「未掛」句。
   七個定名:`plus-two-cells` `v30-two-cells` `manual-keep` `age-lock`
   `opu-note` `plan-split-c` `plan-split-def`。
3. **進場**:從列表打開**已存在**紀錄。不准發明編輯 URL。
   **不准新增**只為了截一張圖。進場是打開已生成紀錄,不是新增一張。
4. **lightbox／點圖放大**:截圖可點開放大。
5. **e2e 掛點**:槽旁邊點名 hang-point(提示,不是完整 runner)。
6. **chrome 同一套**:跟第 2／4／5 站一樣,必須點名 `--ground`、`--panel`、
   `--accent`,加 `--ok-soft`／`--bad-soft`;`.masthead` `.dash` `.cell` `.r-block`。
   外層撐滿卡寬。mermaid 禁。寬 ASCII 禁。
7. **Human verdict**:正本是同目錄 md 頂欄 `verdict:`。只「提交判定」才寫。
   接 `notes/design/gate-verdict-write.md`(#60),不要重做 sidecar。

`7-review.md` 是 twin;本檔鎖的是給人看的審查頁。正本住 `notes/design/`。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| 直式步驟方塊 | `notes/design/vbox-fig-contract.md` |
| G3 twin 執行板 | `_templates/7-review.md` + `scripts/build-gate-twin.py` |
| Human verdict 寫入 | `notes/design/gate-verdict-write.md` |
| 第 5 站 chrome／任務總表 | `notes/design/stage5-review-ui-contract.md` |
| 第 6 站審碼 hunk | 同上 §第6站審碼 |

不改 twin、不改 gate-twin STAGES、不改 #60 verdict 正本。
