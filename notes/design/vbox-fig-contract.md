# 直式置中方塊圖(vbox-fig)

> 各站「直式步驟方塊」的共用母版。產圖:`scripts/build-vbox-fig.py`。
> 牙:`scripts/check-vbox-fig.sh`。畫法總冊:`_templates/diagram-style.md`
> (本家族與那份的橫式單列、三走廊生命週期圖不是同一支 API)。

## 何時用

步驟由上而下、一格一步、框間直線。第 2 站方案架構圖、第 4 站模組生命週期、
以及其他站要畫同類圖,都走這份,不要每站手抄一版。

## 畫法鎖死

- **直式 SVG 方塊**,不是 mermaid、不是橫 ASCII、不是 `<pre>` 當圖。
- **置中**:畫布寬 280;框寬 200、`x=40`;標題／小字 `.nl`／`.sm` 必帶
  `text-anchor="middle"`(字在 140)。
- **有限寬**:`<svg viewBox="0 0 280 …">`,外層或 svg 自己 `max-width:360px`。
- 框間**直線**(同 x,不斷開成橫排)。
- 類名沿用手樣,不准另發明:

| class | 用途 |
|---|---|
| `.b` | 普通格 |
| `.hl` | 強調:這輪新功能落點 |
| `.wn` | 警戒 |
| `.nl` | 置中標題 |
| `.sm` | 置中小字(每格一到三行) |

## 生命週期用法

四格固定、這個順序:**新生 → 改行為 → 退役 → 不動**。

這輪新功能畫在**所屬那一格**(通常是改行為的 `.hl`),不是旁邊另開一欄清單。
沒有新生就在新生格寫「沒有」;沒有退役同理。不准發明 parked／第三態／第五格。

## 何時不用

| 別用本家族 | 走哪條 |
|---|---|
| 第 1 站現況圖(`#scan-now`,三框／四行卡) | `scripts/build-scan-html.py` |
| 導覽七站圖／Claude agent 三走廊生命週期 | `fig-lifecycle` + `check-guides-fig-sync.sh` |
| G1／G2／G3 審查介面 | `scripts/build-gate-twin.py` |
| 2／3／4／5／7「圖對文字」指紋 | `scripts/check-devstage-fig-text.sh`(本牙不取代它) |
| 純線性、單層樹 | README §6:ASCII 即可 |

本腳本不產第 3–7 站 HTML,不改 hop graph,不進 `--action` 圍欄。
