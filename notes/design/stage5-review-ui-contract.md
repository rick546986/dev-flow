# 第 5 站審查頁(chrome／任務總表)

> 第 5 站給人看的 html **版面**正本。5-tasks twin 仍是**執行板**(四件事見
> `_templates/5-tasks.md` 頂註),不是 G1／G2／G3 審查介面;本檔只鎖**頁面樣子**。
> 直式步驟方塊見並列的 `notes/design/vbox-fig-contract.md`(不改那份)。
> 本輪不產第 3–7 站 HTML、不改 twin。

## 何時用

寫或改第 5 站給人看的頁(執行板／任務總表)時。chrome 跟第 2／4 站同一套,
不要另發明殼、不要另發明 class 名。

## 版面鎖死(已拍板)

1. **chrome 同一套**:必須點名 `--ground`、`--panel`、`--accent`,加 `.r-block`
   (灰底／卡片底／強調色／區塊卡)。不要白底長文直轉。
2. **任務總表**:T 編號欄、狀態欄同一行,`white-space:nowrap`。
   表太寬就橫滑(`.tablewrap`／`overflow-x:auto`),不要擠窄前兩欄。
3. **頂區摘要卡若是連結**:標題／數字／小字都不要底線,也不要繼承成強調色底線字
   (`a.cell{text-decoration:none;color:inherit}`)。hover 只改邊框,不加底線。
4. **內文撐滿卡寬再折**:不要 `max-width:62ch` 卡住,也不要硬 `<br>` 斷行。

類名沿用既有審查介面(`.r-block`、`.cell`、`a.cell`、`.tablewrap`),
不准另發明一套。

## 第 6 站審碼(還沒拍完整樣子,只鎖這條)

`6-implementation-notes` 不能只列函式名＋行號。每個這輪改過的函式,要帶
「實際改到的那段」(hunk／關鍵分支),讓人審得到內容。不要整檔貼上,
不要變成第二份正本。產檔器這輪不做。

寫法落點:`_templates/6-implementation-notes.md`(本檔只鎖這一句,不另開家族)。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| 直式步驟方塊 | `notes/design/vbox-fig-contract.md` |
| 第 1 站掃頁 | `scripts/build-scan-html.py` |
| G1／G2／G3 五格標籤 | README §6 + `scripts/check-gate-twin.sh` |
| 5-tasks 執行板四件事 | `_templates/5-tasks.md` 頂註 |

本輪不改 twin、不產第 3–7 站 HTML、不進 `--action` 圍欄。
