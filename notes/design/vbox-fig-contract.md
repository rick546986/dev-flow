# 直式置中方塊圖(vbox-fig)

> 各站「直式步驟方塊」的共用母版。產圖:`scripts/build-vbox-fig.py`。
> 牙:`scripts/check-vbox-fig.sh`。畫法總冊:`_templates/diagram-style.md`
> (本家族與那份的橫式單列、三走廊生命週期圖不是同一支 API)。
> gate-twin 行為流程圖／方案架構圖的 ASCII→SVG 收口在
> `scripts/devflow_twin_ui.py`(`parse_ascii_fig`／`render_vbox_svg`)。

## 何時用

步驟由上而下、一格一步、框間直線。第 2 站方案架構圖、第 4 站模組生命週期、
以及其他站要畫同類圖,都走這份,不要每站手抄一版。

## 輸入形(ASCII → 直式方塊)

gate-twin／審頁要收成直式 SVG 時,**md 正本必須是直式 `[標籤] 標題`**:

```
[R-1] 短標題
  短步驟一
  短步驟二
[R-2] 另一框
  短步驟
```

| 准 | 不准(會 WARNING 或不可讀) |
|---|---|
| 每行一個 `[R-n]`／`[A]` 當一框 | 樹狀 `|`／`|--`／`├`／`└` 分支 |
| 標題與步驟宜短;長句由產器折行或加寬 | 單行 `[A] --> [B]` 橫串多框 |
| 超過建議 8 框仍畫,但 stderr **WARNING** | 靜默硬裁字／默丟高編號框 |

**樹狀 ASCII**:gate-twin **不**收成單盒硬裁;印 `WARNING` 並改以可讀 `<pre>`
原文(附頁面警告)。要直式 SVG → 改寫成上表「准」的形。
禁靜默裁字(對齊「不裁字」精神;本家族允許折行／量測加寬,不允許無聲 ellipsis)。

## 畫法鎖死

- **直式 SVG 方塊**,不是 mermaid、不是橫 ASCII、不是把 `<pre>` 當預設圖
  (樹狀後備 `<pre>` 是顯式降級,必須帶 WARNING,不是常態)。
- **置中**:預設畫布寬 280;框寬 200、`x=40`;標題／小字 `.nl`／`.sm` 必帶
  `text-anchor="middle"`。長標可多行;量到更長時允許框／畫布加寬(左右 padding
  不變),外層 `max-width` 跟著放寬,避免又被 CSS 擠糊。
- **有限寬**:預設 `<svg viewBox="0 0 280 …">`,外層或 svg 自己通常
  `max-width:360px`;加寬時以量測為準。
- 框間**直線**(同 x,不斷開成橫排)。
- 類名沿用手樣,不准另發明:

| class | 用途 |
|---|---|
| `.b` | 普通格 |
| `.hl` | 強調:這輪新功能落點 |
| `.wn` | 警戒 |
| `.nl` | 置中標題 |
| `.sm` | 置中小字(建議一到三行;超出建議仍畫並 WARNING) |

## 生命週期用法

四格固定、這個順序:**新生 → 改行為 → 退役 → 不動**。

**主詞是這個 feat 的那個模組**,不是整套系統。只帶跟該模組有關聯的東西;
無關模組不要上圖。有關聯的**收成一格**,不要拆成檔名／畫面／函式名好幾格。

這輪新功能畫在**所屬那一格**(通常是改行為的 `.hl`)——那一格就是「相關」
那一塊,不是旁邊另開一欄清單。沒有新生就在新生格寫「沒有」;沒有退役同理。
不准發明 parked／第三態／第五格。不要跟七站 DevFlow 圖混。

## 第 4 站生命週期版面(已拍板)

落在審查頁時,圖與說明**分兩張卡**,不要併進同一張:

1. **圖**是獨立一個 `.r-block`:卡內只放直式 SVG,置中、`max-width:360px`。
2. **底下說明**是另一個獨立 `.r-block`,不要跟圖併在同一張卡。
3. 說明卡內文**撐滿卡寬再折**;不准 `max-width:62ch`,不准硬 `<br>` 斷行。

主詞／四格骨架仍依上一節。本節只鎖版面,不改 twin、不在此產第 3–7 站 HTML。

## 何時不用

| 別用本家族 | 走哪條 |
|---|---|
| 第 1 站現況圖(`#scan-now`,三框／四行卡) | `scripts/build-scan-html.py` |
| 第 1 站審頁三框 | `notes/design/stage1-review-ui-contract.md` + `scripts/build-stage1-html.py` |
| 導覽七站圖／Claude agent 三走廊生命週期 | `fig-lifecycle` + `check-guides-fig-sync.sh` |
| G1／G2／G3 審查介面 | `scripts/build-gate-twin.py` |
| 2／3／4／5／7「圖對文字」指紋 | `scripts/check-devstage-fig-text.sh`(本牙不取代它) |
| 純線性、單層樹 | README §6:ASCII 即可 |

本腳本不產第 3–7 站 HTML,不改 hop graph,不進 `--action` 圍欄。
