# 圖表風格 spec(dev-flow 全站)

> 目的:讓**任何人、任何工具**照本規範畫出與母版 guide 同風格的圖 —— 不依賴
> 特定 skill、不依賴 draw.io/Graphviz 等本機軟體(有工具可加速,沒工具照樣手刻)。
> 「看圖」零依賴:全部圖都是靜態 inline SVG,瀏覽器直開。
> ASCII vs SVG 的選用判準在 README §6(純線性/單層樹 → ASCII;方塊+連線的
> 空間關係 → SVG;拿不準 → SVG),本檔只管「畫出來長什麼樣」。

## 硬規則(違反即改)

1. **inline SVG,自足**:禁外部庫(mermaid.js/CDN)、禁外部圖檔(png/jpg)、禁 canvas。
   md 正本永遠留 ASCII 版;SVG 只住 html twin。
2. **顏色一律用 CSS 變數**,禁 hardcode 色碼 —— 圖必須在深淺兩主題都可讀:
   文字 `var(--fg)` 或各色系變數;禁「深底深字/亮底亮字」組合(歷史教訓:
   主題切換會改底色,hardcode 的字色會消失)。
3. **文字**:`svg text` 統一 11px 系統字(頁面 CSS 已定);節點標籤 ≤6 字,
   說明文字用 `.cap`(muted 色)放框外,不塞框內。
4. **座標整數**、`viewBox` 寬 ≤1260;圖寬超過容器靠頁面 `svg{max-width:100%}`
   縮放與 `.tablewrap` 式水平捲動,禁縮小字級硬塞。

## class 約定(定義在各 guide/html-shell 的 `<style>`,直接複用)

| class | 用途 |
|---|---|
| `.b` | 一般節點(card 底 + line 邊) |
| `.hl` | 強調節點(acc 藍系) |
| `.m-opus` / `.m-sonnet` | 模型分層色(紫/青;haiku 用 warn 黃) |
| `.flow` + `marker-end="url(#arrow)"` | 主流程連線(muted 1.6px) |
| `.cap` | 框外說明字(muted) |
| `.session` | 「另開 session」虛線框(acc 藍,4 3 虛線) |
| `.fenceline` | 守衛/圍欄紅虛線(bad 紅,6 4 虛線) |
| `.note` | 註記框(warn 黃虛線) |

## 佈局紀律

- 主流程**左 → 右單列**,節點同 y、等高(44px);gate 用菱形 `<polygon>`;
  選配節點加 `stroke-dasharray="5 3"`。
- 迴圈/例外路徑走**上方或下方弧線**(`<path C …>`),不與主列交叉;
  跨節點跳線(如「跳 3」)標籤放弧頂。
- 區間標示(如守衛武裝)用底部括號線 + `.cap` 兩行字;範圍框(如 session)
  用 `.session` 圓角虛線框 + 框頂標籤。
- 節點間距 ≥26px 留給箭頭;箭頭統一 `#arrow` marker,一張圖一個 defs。

## 直式生命週期版式(2026-08-16 入典)

橫式單列(上面①-④)裝不下「一條主幹 + 多個旁支事件 + 巢狀範圍」這種生命週期圖;
這節記的是 `guide-dev-flow.html` ⑥ `fig-lifecycle`(與其在 `guide-quickstart.html` ③
的雙生版 `fig-lifecycle-qs`)實際採用的直式版式,供同類圖(任何「主幹事件 + 掛靠旁支」
的生命週期/狀態機)照抄。

1. **三走廊佈局**(直式,由上而下讀主幹):**左**走廊放灰虛線掛靠事件小框(旁支,
   由外部觸發但不在主幹上);**中**走廊放主幹節點(等寬、垂直堆疊);**右**走廊放
   `.dc` 文字 + 短引線(`.tick`,無 `class="edge"`,不進 lint 的 edge 驗證)做的
   掛載註記,沒東西可標的格留白(留白本身就是資訊,不必每格硬填)。
2. **範圍框**:雙層虛線框 + 框角標籤,顏色語意固定 ——**藍**(沿用既有 `.sessionbox`)
   = 一個回合(turn)的範圍,**橘**(新增 `.loopscope` + `--orange` 變數)= 回合內
   會反覆繞的迴圈(loop)。框角標籤(如「EACH TURN」「AGENTIC LOOP」)用 `.dk`
   (藍)/ 新增的 `.dk-o`(橘)放在框內左上角、主幹節點外側,不得壓進主幹節點的
   文字或框體。範圍框本身的 `<g>` class 必含 `cluster`(如
   `class="cluster loopbox"`),lint 才會把它當裝飾框跳過、不誤判成需要端點對齊
   的 node。
3. **回邊走外側走廊,不穿框**:迴圈/回合的回邊(如「跑完最後一步繞回第一步」)走
   主幹**右側**、範圍框邊界內外的專屬車道(每層巢狀範圍框各自一條車道,由內而外
   疊放,如迴圈回邊車道在主幹右緣 +10px、回合回邊車道再往外 +20px),垂直走完
   整段後用直角轉進目標節點的框邊,不得穿越任何主幹節點內部。跨越更大範圍(如
   「session 結束後 resume 回開頭」)的回邊可走整張圖最外側的專屬車道,配黑色
   `.edge-resume`(`var(--fg)`、虛線)以區別於回合/迴圈回邊的實色線。
4. **掛靠框**用灰虛線框(新增 `.att`:`stroke:var(--muted);stroke-dasharray`)+
   灰虛線箭頭(新增 `.edge-att`,marker 可沿用主色 arrowhead),框內兩行文字:
   主標(`.dt`)+ 副標小字括號(`.dc`,如「(Async)」「(MCP input)」)。掛靠框允許
   跨越範圍框的虛線邊界指向框內節點(這是預期行為,不是缺陷,因為範圍框已排除在
   lint 的 node 判定外)。無旁支可掛的獨立事件(不指向主幹任何節點)可整排放在圖
   最下方,同樣用 `.att` 樣式,但不畫箭頭。
5. **主幹配色語意**(全部用既有或新增的 CSS 變數表達,禁 hardcode,沿用硬規則 2):
   **綠**(`.go`,`var(--ok)`)= 生命週期起點;**藍**(`.hl`,`var(--acc)`)= 實際
   執行動作的節點;**紅**(`.no`,`var(--bad)`)= 停止/終止節點;**黃**(新增 `.hk`,
   `var(--warn)`,實色非虛線,與虛線的 `.note` 區分)= harness 會在此觸發、
   dev-flow(或任何掛客)可掛 hook 的節點;**灰**(`.b`,既有)= harness 內部無
   hook 語意、純狀態推進的節點。這五色只描述**節點本身的性質**,節點是否已被
   實際掛上東西是右走廊的註記負責的另一件事,兩者不要混為一談。

## 直式置中方塊圖(另一家族)

第 2 站方案架構、第 4 站模組生命週期、以及其他「直式步驟方塊」走
`notes/design/vbox-fig-contract.md` + `scripts/build-vbox-fig.py`。
那是 280 畫布、框寬 200、`max-width:360px` 的直式 SVG,不是上面「直式生命週期
版式」的三走廊圖,也不是第 1 站 `#scan-now` 三框。不要手抄、不要 mermaid。
生命週期主詞是這個 feat 的那個模組:關聯收一格,新功能畫在所屬那一格。
第 4 站落頁時圖與說明各一個 `.r-block`,說明撐滿卡寬再折。

## 可摺疊目錄樹(另一家族)

人要看「資料夾怎麼疊 + 每列用途」走 `notes/design/dir-tree-contract.md` +
`scripts/build-dir-tree.py`。monospace `├─` `│` `└─`、巢狀摺疊、每列 why、
預設只露 L1。不是 mermaid、不是橫 ASCII、不是 vbox-fig 步驟方塊、不是第 1 站
三框現況圖、也不是本檔的橫式／三走廊圖。母版頁 `guides/guide-dir-map.html`;
產品有需要才畫,落 `docs/dev/<slug>/dir-tree.html`。

## 第 5 站審查頁 chrome(另一家族)

第 5 站給人看的頁(`--ground`／`--panel`／`--accent`、`.r-block`、任務總表 nowrap、
`a.cell` 無底線且 `color:inherit`、內文撐滿卡寬)走
`notes/design/stage5-review-ui-contract.md`。不是上面的直式步驟方塊,也不是本檔
的橫式／三走廊圖。本輪不改 twin。審頁產檔器 `scripts/build-stage5-html.py`。

## 範本

抄現成的最快:七階段全程圖 `guides/guide-quickstart.html` ⑥(單列+gate+區間+session 框
全部齊)、資訊圍欄圖 `guides/guide-dev-flow.html`(圍欄紅線用法)、直式生命週期全還原圖
`guides/guide-dev-flow.html` ⑥ `fig-lifecycle`(三走廊+雙層範圍框+多色主幹,上面「直式
生命週期版式」整節即以此圖定案)。新圖先挑最像的抄結構,再改節點。
直式步驟方塊另見 `notes/design/vbox-fig-contract.md`。
可摺疊目錄樹另見 `notes/design/dir-tree-contract.md`。
第 5 站審查頁 chrome 另見 `notes/design/stage5-review-ui-contract.md`。
