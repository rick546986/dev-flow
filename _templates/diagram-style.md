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

## 範本

抄現成的最快:七階段全程圖 `guide-quickstart.html` ⑥(單列+gate+區間+session 框
全部齊)、資訊圍欄圖 `guide-dev-flow.html`(圍欄紅線用法)。新圖先挑最像的抄結構,
再改節點。
