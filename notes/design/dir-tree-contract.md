# 可摺疊目錄樹(dir-tree)

> 人看「資料夾怎麼疊、每一列幹嘛」。產圖:`scripts/build-dir-tree.py`。
> 牙:`scripts/check-dir-tree.sh`。畫法總冊:`_templates/diagram-style.md`
> (本家族與 vbox-fig 直式步驟方塊、第 1 站三框現況圖、七站三走廊生命週期圖
> 不是同一支 API)。

## 何時用

專案大、要接手、跨模組、或人要快速看檔案結構跟脈絡。畫的是**那個產品
repo 的結構**,不是母版 `scripts/`／`hooks/` 九十支盤點。

母版自己的示範頁是 `guides/guide-dir-map.html`(由本產器吐,不准手抄第二份)。

## 何時不用／不要畫

| 別用本家族 | 走哪條 |
|---|---|
| 步驟由上而下、一格一步 | `notes/design/vbox-fig-contract.md` + `build-vbox-fig.py` |
| 第 1 站現況圖(三框／四行卡、`#scan-now`) | `scripts/build-scan-html.py` |
| 第 1 站審頁三框 | `notes/design/stage1-review-ui-contract.md` + `build-stage1-html.py` |
| 導覽七站圖／三走廊生命週期 | `fig-lifecycle` + `check-guides-fig-sync.sh` |
| 母版腳本盤點(每支 hooks／scripts 一句職責) | `guides/guide-dev-flow.html#filemap` |

不是每案必跑。不新增 gate、不新增必跑 hop、不改 graph 逼每案走這一跳。
產品有需要才畫;產器留在方法包 `scripts/`,需要的專案從方法包跑,不進
`ship-manifest` 散發。

## 畫法鎖死

- **monospace 樹**:`├─` `│` `└─` 接層。摺疊時仍是一棵樹,不是卡片、不是步驟圖。
- **巢狀 `<details>`**:資料夾名可點;預設**全部摺疊,只露 L1**。不准
  `<details open>`。
- **每一列都有 why**:同一列右邊 `<span class="why">`,一句到兩句 —— 這是什麼、
  什麼時候用、跟旁邊誰有關。資料夾跟檔案都要。不要另開說明卡,不要成長文。
- **禁**:mermaid、橫 ASCII 充圖、`<pre>` 當圖、vbox-fig 步驟方塊、第 1 站三框
  現況圖、把九十支 scripts／hooks 灌進樹。
- 腳本很多時只列關鍵入口,其餘一句指向 `#filemap`(母版)或「其餘不列」(產品)。

## 輸入／輸出

產器吃**目錄 + 用途表**(JSON):

- 用途表列出要畫的列(名、why、子列)。`--root` 核對列上路徑在目錄裡真的在
  (合成列 `…` 除外)。
- 產品也可 `--walk`:按目錄長樹,但**每一列仍要有 why**;缺 why 就紅。prune
  掉 `.git`／`node_modules` 與用途表標 omit 的路徑。
- 吐 HTML:共用 guide token,樹在 `.treewrap` > `.tree`,列是 `.tline`。

產品落檔:`docs/dev/<slug>/dir-tree.html`。不要寫進 `1-discussion.html`,
不要跟掃頁六件／審頁三框搶槽。

## 母版頁

`guides/guide-dir-map.html` 必須是本產器產出。手改會漂:
`scripts/build-dir-tree.py --check` 必須紅。
