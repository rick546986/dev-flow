# 第 1 站審頁(摘要／三框現況圖／人表)

> 第 1 站給人看的**審頁**版面正本。掃頁臉仍是 `scripts/build-scan-html.py`
> (S10,殼 `html-shell`),不是這份。本檔只鎖審頁樣子。
> 第 1 站三框現況圖是另一套,不併進共用生命週期圖規則
> (`notes/design/vbox-fig-contract.md`)。
> 產檔器:`scripts/build-stage1-html.py`。牙:`scripts/check-stage1-now-contract.sh`。
> 不改 `build-scan-html.py`、不進 `build-gate-twin.py` STAGES、不包 html-shell。

## 何時用

寫或改第 1 站給人看的審頁時。不要拿掃頁產生器充這頁,不要另發明殼。

## 版面鎖死(已拍板)

下列五條是鎖死,不是口味、不是選配。產檔器吃 md 的 Problem／Open Questions／
現況圖／Actors:`scripts/build-stage1-html.py` 吐 `.sum#scan-sum`／
`#scan-now`／`#scan-people`。授權 `--action`。不包 markdown-it + html-shell。
寫法落點:`_templates/1-discussion.md`(本檔是正本,不另開家族)。

1. **頂區摘要**:`.sum#scan-sum` 必須有痛、繞(現在怎麼繞)、徽章
   已解／假設／移交(Open Questions 三態計數)。
2. **直式三框現況圖**:`#scan-now` 是 SVG,`viewBox="0 0 200 420"`,
   每框 `height="88"`,外層 `.now-wrap` 置中 `max-width:360` 這級。
   現況圖吃無標籤四行堆,`|` 是分隔不是第四框;有 `誰:` 標籤的也吃。
   不是珠鏈、不是 mermaid、不是橫 ASCII、不是 `<pre>` 當圖。
3. **人表**:`#scan-people` 表(誰／要什麼／缺什麼)。
4. **chrome**:必須點名 `--ground`、`--panel`、`--accent`,加 `--ok-soft`／
   `--bad-soft`;`.masthead` `.dash` `.cell` `.r-block`。不要白底長文直轉。
5. **不是掃頁**:不准改 `build-scan-html.py` 來充第 1 站審頁。不准只包 html-shell。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| 第 1 站掃頁六件 | `scripts/build-scan-html.py` |
| 直式步驟方塊／生命週期四格 | `notes/design/vbox-fig-contract.md` |
| G1／G2／G3 五格標籤 | README §6 + `scripts/build-gate-twin.py` |
| 第 2／5／7 站審頁 | 各站 `notes/design/stageN-review-ui-contract.md` |

不改 twin、不改 `build-scan-html.py`、不改 `build-stage6-html.py`、
不改 gate-twin STAGES。
