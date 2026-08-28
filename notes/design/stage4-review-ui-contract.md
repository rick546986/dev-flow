# 第 4 站審頁(R/S 卡／生命週期直式圖)

> 第 4 站給人看的**審頁**版面正本。G2 twin 仍是五格審查介面
> (`scripts/build-gate-twin.py` STAGES 的 4-spec),不是這份。
> 本檔只鎖審頁樣子。直式步驟方塊母版見
> `notes/design/vbox-fig-contract.md`(四格:新生 → 改行為 → 退役 → 不動)。
> 產檔器:`scripts/build-stage4-html.py`。牙:`scripts/check-stage4-rs-contract.sh`。
> 不進 `build-gate-twin.py` STAGES、不包 html-shell。
> Human verdict 接 #60:正本是同目錄 md 頂欄 `verdict:`,只「提交判定」才寫。
> 不要重做 sidecar。第 1 站三框現況圖是另一套,不併進這份共用規則。

## 何時用

寫或改第 4 站給人看的審頁時。chrome 跟第 2／5／7 站同一套 token
(`--ground` `--panel` `--accent`、`.masthead` `.dash` `.r-block`),
不要另發明殼、不要另發明 class 名。

## 版面鎖死(已拍板)

下列七條是鎖死,不是口味、不是選配。產檔器吃 md 的 R/S 與生命週期節:
`scripts/build-stage4-html.py` 吐 R/S 卡 + 直式生命週期 SVG + 提交判定。
授權 `--action`。不包 markdown-it + html-shell。
寫法落點:`_templates/4-spec.md`(本檔是正本,不另開家族)。

1. **R／S 卡**:每個 R 一個 `.r-block`,內各 S 一張卡。
   卡上有 **審的時候看什麼**(觀測)、**GIVEN／WHEN／THEN**。
   缺 GIVEN／WHEN／THEN 任一欄要看得見,不要只攤 md。
2. **生命週期只畫該 feat 那一個模組**:有關聯的收成一格,不拆檔名。
   骨架固定四格、這個順序:**新生 → 改行為 → 退役 → 不動**。
   這輪新功能畫在所屬那一格(通常是改行為的 `.hl`)。
   沒有新生就寫「沒有」;沒有退役同理。不准發明 parked／第五格。
3. **直式 SVG 置中**:圖是獨立一個 `.r-block`,卡內只放 SVG,
   置中、`max-width:360px`。底下說明另張 `.r-block`,不要跟圖併卡,
   說明撐滿卡寬再折,不准 `max-width:62ch`。
   不是 mermaid、不是橫 ASCII、不是 `<pre>` 當圖。
4. **補助標題也要吃**:`## 補助模組生命週期（預覽）` 四條要能印成那張圖,
   不要只認自創 fixture 標題。括號全形／半形都算。
5. **chrome 同一套**:必須點名 `--ground`、`--panel`、`--accent`,加
   `--ok-soft`／`--bad-soft`;`.masthead` `.dash` `.cell` `.r-block`。
6. **提交判定**:正本是同目錄 md 頂欄 `verdict:`。只「提交判定」才寫。
   接 `notes/design/gate-verdict-write.md`(#60),不要重做 sidecar。
7. **不是 twin**:不准把第 4 站審頁塞進 `build-gate-twin.py` STAGES。
   不准只包 html-shell。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| G2 twin 五格／勾選卡 | `_templates/4-spec.md` 頂註 + `scripts/build-gate-twin.py` |
| 直式步驟方塊母版 | `notes/design/vbox-fig-contract.md` |
| 第 1 站三框現況圖 | `notes/design/stage1-review-ui-contract.md`(不併進生命週期) |
| Human verdict 寫入 | `notes/design/gate-verdict-write.md` |
| 第 3 站選配審頁 | `notes/design/stage3-review-ui-contract.md` |

不改 twin、不改 gate-twin STAGES、不改 #60 verdict 正本、
不改已合的 1／2／5／6／7 產器。
