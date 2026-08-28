# 第 5 站審查頁(chrome／任務總表)

> 第 5 站給人看的 html **版面**正本。5-tasks twin 仍是**執行板**(四件事見
> `_templates/5-tasks.md` 頂註),不是 G1／G2／G3 審查介面;本檔只鎖**頁面樣子**。
> 第 6 站審碼 hunk 顯示也鎖在本檔 §第6站審碼(不另開家族)。
> 直式步驟方塊見並列的 `notes/design/vbox-fig-contract.md`(不改那份)。
> 本輪不產第 3–7 站 HTML、不改 twin。

## 何時用

寫或改第 5 站給人看的頁(執行板／任務總表)時。chrome 跟第 2／4 站同一套,
不要另發明殼、不要另發明 class 名。
寫或改第 6 站給人看的審碼頁時,看 §第6站審碼。

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

## 第 6 站審碼(鎖死)

`6-implementation-notes` 給人看的頁,**每個這輪改過的函式**必須自己一塊 hunk,
不是只列函式名＋行號表。下列七條是鎖死,不是口味、不是選配。
產檔器這輪不做。寫法落點:`_templates/6-implementation-notes.md`
(本檔是正本,不另開家族)。不要整檔貼上,不要變成第二份正本。

1. **一函式一塊**:每個這輪改過的函式自己一個 hunk 區塊。不得用「名＋行號表」充數。
2. **改什麼**:程式碼上方一句,只寫這輪改了什麼,不是複述整函式。
3. **色碼 diff**:新增／改到的行綠(`.ln.add`／`--ok-soft`),上下文淡,刪行紅且
   **只有舊行已知才畫**。不准發明 minus 行。
4. **標題帶 T-n**:標題寫造成這次改動的第 5 站 task id。一塊 hunk 真的同時服務
   兩個 T 才准帶兩個 T。
5. **關聯一行**:「改什麼」底下一個單行:對語函式(若有,例如 PHP↔JS)、誰叫它、
   它叫誰。不傾倒整張呼叫圖。
6. **不是第二份正本**:不要整檔貼上。hunk 只給人審這輪改到的那段。
7. **chrome 同一套**:跟第 2／4／5 站一樣,必須點名 `--ground`、`--panel`、
   `--accent`,加 `.r-block`。內文撐滿卡寬再折。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| 直式步驟方塊 | `notes/design/vbox-fig-contract.md` |
| 第 1 站掃頁 | `scripts/build-scan-html.py` |
| G1／G2／G3 五格標籤 | README §6 + `scripts/check-gate-twin.sh` |
| 5-tasks 執行板四件事 | `_templates/5-tasks.md` 頂註 |

本輪不改 twin、不產第 3–7 站 HTML、不進 `--action` 圍欄。
