# 現況圖行長守衛（#138 merged brief）

> Owner 合成 A／B／C。本檔是 **design note 正本**，不是契約。後續實作另開 PR。
> 本檔 supersede 來源 brief：[#139](https://github.com/rick546986/dev-flow/pull/139)（A）、
> [#140](https://github.com/rick546986/dev-flow/pull/140)（B）、
> [#141](https://github.com/rick546986/dev-flow/pull/141)（C）。實作只跟本檔，不跟三份草稿。
> 對應 issue：https://github.com/rick546986/dev-flow/issues/138
> 調查基準：`main` `96b999f`（plugin `3.22.0`、契約 `2.0.0`）。
> 本檔用到的 repo 名詞：掃頁產生器 `scripts/build-scan-html.py`（S10）、
> `#scan-now` SVG、`unicodedata.east_asian_width`、Interview Log 牙
> （`ValueError` → `die(1, "拒絕:%s")`）。

## 1. Status

本檔是 **design note 正本**，不是契約。後續實作另開 PR。
零版本 bump（`.claude-plugin/plugin.json`、契約 schema 皆不動）。
不加 hop／gate／審頁解鎖。**本輪只加 fail-loud 行長牙**，不動 SVG 幾何。

本 PR 本身不算修 #138。不要把本 brief merge 當修法。

核過的 issue 行號（`96b999f`）：

| issue 寫 | 現況 |
|---|---|
| `build-scan-html.py:576` 逐行 `<text>` | 仍是 `render_svg` 輸出 `<text text-anchor="middle" x="100">` |
| `:45` 框寬 160、viewBox 200 | `VB_W = 200`；`RECT_X, RECT_W, RECT_H = 20, 160, 88` |
| `:15` 「不裁字」 | 檔頭仍只寫不裁，無每行上限 |
| `SKILL.md:156-161` | 視覺版仍「每框四行」「不裁字」，無字數上限 |
| `N9-write-md.md` / `S10-html.md:29` | N9 只管從 Journey 長圖；S10 只寫四行形狀 |

## 2. Problem

`scripts/build-scan-html.py` 的 `render_svg` 把 md 現況圖每一框的四欄
（誰／做什麼／工具／痛點）各畫成置中 `<text text-anchor="middle" x="100">`
（約 L576）。框寬鎖死 `x=20 width=160`、viewBox 200、字 11px（約 L45；檔頭 L15
明寫「不裁字」）。一行超過約 13 個全形字就左右凸出 rect，遮到框線。

產生器仍 exit 0、印 `wrote …`，沒有任何警告。

撰寫者此刻只拿到「每框四行」「不裁字」，沒有每行字數上限。照
`skills/dev-talk/nodes/N9-write-md.md`、`skills/dev-talk/SKILL.md:156-161`、
`skills/dev-talk/nodes/S10-html.md:29` 寫出來的 md，第一次產 html 幾乎必定凸框，
要靠人看圖才回頭改 md 重生。

同檔對 Interview Log 文法已經 fail-loud（`ValueError` → `die(1, "拒絕:%s")` →
exit 1）。現況圖行長是同一類「形狀壞了還綠」缺口。

## 3. Thesis

**現況圖每一條會畫進 SVG 的欄位值，寬度必須事先算過；超過就跟 Interview Log 一樣立刻 `ValueError`，不准靜默產凸框圖，也不准產生器改圖來救長句。**

核心原則：**框寬是契約，字去就框，不是框去就字。**
現況圖是標題卡，不是 Current Journey 整格搬進來。寫太長 = md 不合格。

## 4. Do（實作時）

- 檔頭常數 `NOW_LINE_MAX = 13`，放在 `RECT_*` 旁邊。常數寫死，**不要**執行期用 `RECT_W / 11` 反推。
- `display_width(s)`：逐字 `unicodedata.east_asian_width`；`W`／`F`／`A` = 1.0，其餘 = 0.5（§6）。
- 量 **parse 之後、`esc()` 之前** 的 `who`／`action`／`tool`／`pain`。標籤已剝，不計入 N。
- `display_width(s) > 13` → 一則 `ValueError` 列完本圖所有超長欄 → 既有 `die(1, "拒絕:%s")`。`= 13` 過。
- 牙只住 S10 `scripts/build-scan-html.py`。不另開 md-write-time linter。
- 檔頭 docstring「不裁字」旁補上限；`exit:` 那行把行超長算進 exit 1。
- 作者文件（實作 PR 才改，本 brief 不動）：N9 主場；SKILL 現況圖節；S10；guide 若 guide-sync 要求；N3 3a 半句。S8 不目測凸框。
- 既有 good fixture 必須仍綠。加 `display_width` 邊界表 + `bad-now-line` 牙（§10）。

## 5. Don't

- 不 soft wrap、不多行 `<text>`／`<tspan>`、不縮 `font-size`、不拉 `viewBox`／`RECT_W`、不加省略號、不 warn-but-exit-0。
- 不改 `parse_frames`／一行四欄 vs 四行堆疊的拆法。
- 不檢查 md 原始行（含標籤）、不檢查圖下固定字「痛在最後一步」、不檢查 `<pre>` 退路。
- **不動** `scripts/build-stage1-html.py`（審頁產生器；#138 只點掃頁）。
- 不 bump plugin／契約。不加 hop、不改 `graph.yaml`。
- 不准引入 `wcwidth` 或任何非標準庫。不准 `match`／`case`（3.10）。訊息用既有 `%-format`。
- 不准為拉丁大寫 `Na` 另做第三權重（殘見 §6.3，本 hop 不修）。

## 6. 寬度公式與量測對象

### 6.1 門檻

`NOW_LINE_MAX = 13`（全形單位）。**`display_width(s) ≤ 13` 綠；`> 13` 紅。**
13 整剛好過；13.5 紅。

怎麼得出 13（常數寫死）：

| N | `N×11` | 單側空隙 | 判讀 |
|---|---|---|---|
| 13 | 143 | 8.5px | 最後一個安全整數；字級／字重微漂還蓋得住 |
| 14 | 154 | 3.0px | 貼 `stroke`，圓角／微寬就凸 |
| 15 | 165 | 負 | 必凸 |

`RECT_W = 160`。CJK 在 11px 下 ≈ 1em。扣 `rx=6` + stroke，可用 ≈ 144 →
`144 / 11 ≈ 13.09`。issue 目視也是「約 13 全形」。**不賭 14。**

之後若有人改字級或框寬，必須**同時改這個常數**，不准讓公式 silently 跟著漂。

### 6.2 公式（採 C；覆寫 A／B 與 issue 的 `A=0.5`）

```python
import unicodedata

def display_width(s):
    total = 0.0
    for ch in s or "":
        total += 1.0 if unicodedata.east_asian_width(ch) in ("W", "F", "A") else 0.5
    return total
```

| 類 | 權重 | 例子 |
|---|---|---|
| `W`／`F`／`A` | 1.0 | 中日韓、全形 `Ａ`／`Ｆ`、全形標點 `，`、歧義 `—`／`–`／`×` |
| 其餘（`Na`／`N`／`H`） | 0.5 | ASCII、半形假名、空白 |

issue 與 A／B 把 `A`（Ambiguous）丟進 0.5。本檔不採。

- UAX #11 的 `A` 在 CJK 字型通常當全形畫。`—`（EM DASH）11px 常畫 ≈ 1em。
- 若 `A=0.5`，26 個 `—` 估寬 13、實畫遠超 160，又是靜默凸框。本 issue 要消滅的就是這種洞。
- `unicodedata.east_asian_width` 是 stdlib、Python 2.4 起就有，**3.9 地板安全**
  （`scripts/check-py-floor.sh`）。不准新 API、不准 `wcwidth`。
- 現有 html-scan good 最長欄「新增附表五、選 A–F」在 `A=1` 後 = **9.5**（EN DASH 升 0.5），仍遠低於 13。改權重不誤殺 fixture。

量 **parsed SVG field values**：`parse_frames` 之後、寫入 `<text>` 之前的
`who`／`action`／`tool`／`pain`。與畫面同源。

不量：

- md 原始行（`誰:`／`做什麼:` 等標籤已被 `_strip_field_label` 剝掉，不進 `<text>`）
- 圖下固定 caption「痛在最後一步」
- `<pre id="scan-now">` 退路（`parse_frames` 抽不到框；沒有 160 寬 rect）

空字串 `display_width=0`，本牙放行（痛空仍走既有「痛不准空」牙，不合併）。
combining mark／ZWJ 各算 0.5（略高估）。fail-loud 可接受，不為它們開例外。

### 6.3 已知殘（本 hop 不修）

拉丁 `Na` 是比例字。26 個全大寫 `W`（`Na`）估寬 13、實畫可接近 1em／字，公式放行、畫面可能凸框。
現況圖文類是中文標題卡加短拉丁 token（`PLUS`、`OPU`、`2PN`），不是 26 連發大寫。
不為這個殘加第三權重。

## 7. 錯誤訊息形狀（採 B；覆寫 A／C 的 fail-fast-first）

`main` 已有 `except ValueError: die(1, "拒絕:%s" % exc)`。本牙只 raise，不另開 exit。

一則 `ValueError` 列完本圖**所有**超長欄。框序 1-based；欄名用中文
`誰`／`做什麼`／`工具`／`痛點`（對 `who`／`action`／`tool`／`pain`）。
每列含：估寬、渲染原文、短改寫提示。

```text
現況圖行超長(每行 ≤13 全形;W/F/A=1、其餘=0.5;標籤不計):
  第1框「做什麼」估寬 13.5：「月初翻 Excel 私表比對到期日」
  第2框「痛點」估寬 16.0：「法務回覆要等而且進度完全不可見」
請收成標題卡再重生(例:「翻私表」／「進度不可見」)。見 notes/design/scan-now-line-guard.md
```

實作可微調標點與提示句，但必須同時滿足：

- 牙針（needle）子字串：**`現況圖行超長`**
- 訊息必須出現數字上限 **`13`**
- 每條超欄含框號、中文欄名、估寬、渲染原文（未 `esc`）
- 不准只報第一條讓撰寫者跑四輪 S10

禁：只說「行太長」、只印 raw md 含標籤的那一行、exit 0 加 warning、靜默截斷後仍 `wrote …`。

## 8. Reject 表（採 C）

| # | 方案 | 裁決 | 理由 |
|---|---|---|---|
| Soft wrap／多行 SVG | **REJECT** | 框高鎖 88、四行 y 鎖 18／44／64／84；多一行就撞行或破「每框四行」 |
| Widen rect／viewBox | **REJECT** | `viewBox 200`、外層 `width:220px`、`RECT_W=160` 已被 SKILL／殼／fig-graph 牙鎖死；幾何本輪已收縮，加寬沒上限 |
| Auto-shrink font | **REJECT** | 「字 11px」寫死；縮到看不見仍是靜默假綠 |
| Truncate ellipsis | **REJECT** | 檔頭／SKILL／牙都寫「不裁字」 |
| Warn-but-exit-0 | **REJECT** | 根因就是 silent success／exit 0；CI 當綠 |

採用項只有 fail-loud `ValueError`。B／C／D 都是「產生器改圖救長句」——幾何已有牙，改圖 = 另開 issue。

## 9. 範圍：要改與不改的檔

「不升 plugin」= 不 bump 版本，不改 graph、不加節點。節點與指南的**文字**可改。
下表是**後續實作 PR** 的範圍。本 brief 只新增本檔。

| 檔 | 改什麼 |
|---|---|
| `scripts/build-scan-html.py` | `NOW_LINE_MAX`；`display_width`；`render_svg` 前檢查；檔頭「不裁字」旁補上限；`exit:` 把行超長算進 1；一次列完的 `ValueError` |
| `scripts/check-devtalk-fig-graph.sh` | `TOOTH_CASES` 加 `bad-now-line`（與 `check_log_teeth` 同款：bad 必須紅、stderr 含針）；另加 `check_now_line_edges()` 直接 import `display_width`；檔頭註解補「超長 fail-loud」 |
| `scripts/fixtures/devtalk-html-scan/bad-now-line/1-discussion.md` | 從 good 抄一份，只把一欄改超（建議做什麼欄 14 全形，或 issue 示範句剝標籤後 26.0） |
| `scripts/fixtures/devtalk-html-scan/assert-teeth.py` | `BAD` 加 `("bad-now-line", "現況圖行超長")` |
| `skills/dev-talk/nodes/N9-write-md.md` | **主場**。補：渲染後四欄每行 ≤ 13 全形（W／F／A=1、其餘 0.5；標籤不計）；超過 S10 exit 1；現況圖是標題卡，不要把 Current Journey 整格搬進來 |
| `skills/dev-talk/SKILL.md` | 現況圖節（約 L156–161）「不裁字」旁補上限與 exit 1 |
| `skills/dev-talk/nodes/S10-html.md` | 產生器對超長行 fail-loud；改 md 該欄再重生，不要開瀏覽器目測凸框 |
| `skills/dev-talk/nodes/N3-probe.md` | 3a「同步改現況圖」加半句：每行渲染值 ≤13 全形（公式同 N9） |
| `skills/dev-talk/nodes/S8-review.md` | ⑧ 加一句：行長由產器守，不目測凸框 |
| `guides/guide-dev-talk.html` | 若 `check-devtalk-guide-sync.sh` 要求：視覺版「原文」blockquote 與 SKILL 逐字同步 |

本輪**不改**：`html-shell.html` 幾何、`scripts/build-stage1-html.py`、
`notes/design/stage1-review-ui-contract.md`、`graph.yaml`、
`_templates/1-discussion.md`（仍叫邏輯圖，正名另案）、example 正名、
plugin／契約版本。既有 html-scan good 最長欄 9.5，不必為 N=13 改圖。

## 10. 牙與判準

**牙**（住 `scripts/build-scan-html.py`，fail-closed）：

1. 任一框四欄 `display_width(s) > NOW_LINE_MAX` → `ValueError`，訊息含 `現況圖行超長`、數字 `13`、框號、中文欄名、估寬、渲染原文、短改寫提示。
2. 多欄同時超 → 一則訊息列完，仍 exit 1、不印 `wrote …`。
3. 不准截斷、不准換行、不准縮字後繼續寫檔。

現況牙慣例（實作時對齊）：`check-devtalk-fig-graph.sh` 的 `TOOTH_CASES` +
`check_log_teeth()` 對每份 `scripts/fixtures/devtalk-html-scan/bad-*/1-discussion.md`
跑產器，要求 exit ≠ 0 且 stderr 含針；`assert-teeth.py` 的 `BAD` 表同步。
`bad-now-line` 掛同一條鏈。另加 `check_now_line_edges()` 直接餵 `display_width`，
不必整份 md（對齊既有 `check_log_edges` 直接餵 `parse_log`）。

**邊界（`check_now_line_edges`，公式已重算：`A=1`）**

ASCII 26／27 **仍相關**：拉丁 `A` 是 `Na`，不是 Ambiguous，權重仍 0.5。

| 輸入 | `display_width` | 期望 |
|---|---|---|
| `""` | 0 | 0 |
| 13 個 `字`（`W`） | 13.0 | ≤13 |
| 14 個 `字` | 14.0 | >13 |
| 26 個拉丁 `A`（`Na`） | 13.0 | ≤13 |
| 27 個拉丁 `A` | 13.5 | >13 |
| 12 個 `字` + `AB` | 13.0 | ≤13 |
| 12 個 `字` + `ABC` | 13.5 | >13 |
| 全形 `Ｆ`（`F`） | 1.0 | 與半形 `F`=`Na`=0.5 不同 |
| 全形 `Ａ`（`F`） | 1.0 | 與半形 `A`=0.5 不同 |
| `—`（EM DASH、`A`） | 1.0 | 與 issue／A／B 原式 0.5 不同；本檔採 1 |
| 13 個 `—` | 13.0 | ≤13 |
| 14 個 `—` | 14.0 | >13 |

**整檔牙**：`bad-now-line` 必須 exit 1 且 stderr 含 `現況圖行超長` 與 `13`。
既有 `good/1-discussion.md` 必須仍綠。

**無牙、靠文件**：句子好不好讀、能不能再短；只保證不凸框。
S8 ⑧ 仍只核 Journey 指紋，不目測溢位。拉丁 26 連發大寫的殘（§6.3）本 hop 無牙。

## 11. 後續實作 PR 過關

本檔本身不算過關。實作 PR 必須下列全真：

1. §9 表列檔全部改到；`check-devtalk-fig-graph.sh`／`check-devtalk-guide-sync.sh` 綠。
2. 牙 1–3 + 邊界表 + `bad-now-line` 都掛上；既有 good fixture 仍綠。
3. SVG 幾何不變：`viewBox 200×420`（三步）、`rect x=20 width=160 height=88`、`text-anchor=middle x=100`、字 11px。不 wrap、不縮字、不加寬、不裁。
4. 超長輸入 exit 1，不印 `wrote …`。
5. 一份剛好 13 全形的欄必須綠；一份「標籤 + 短值、合計 >13、值本身 ≤13」必須綠（證明剝標籤）。
6. 版本零 bump。`check-py-floor.sh` 仍綠（3.9 可 parse）。
7. `scripts/build-stage1-html.py` 零 diff。

## 12. 來源 brief 取捨

本檔 supersede 下列三份。實作衝突以本檔為準。

| 來源 | 採 | 棄 |
|---|---|---|
| [#139](https://github.com/rick546986/dev-flow/pull/139) **A** | N=13、`≤` 過；量 parsed field；fail-loud `ValueError` → exit 1；針 `現況圖行超長`；不動幾何；零 bump；good 仍綠 + `display_width` 邊界表 + `bad-now-line` 掛 `check-devtalk-fig-graph.sh`／`assert-teeth.py`；不動審頁產生器 | `A=0.5`；fail-fast 只報第一條超欄；針不含強制數字 13 |
| [#140](https://github.com/rick546986/dev-flow/pull/140) **B** | 一則訊息列完所有超欄（框 1-based + 誰／做什麼／工具／痛點 + 估寬 + 渲染原文 + 短改寫提示）；牙只在 S10，不另開 md-write-time linter；N9 主場、SKILL 現況圖節、S10、guide-sync、N3 3a 半句；S8 不目測凸框 | `A=0.5`；常數名 `LINE_CAP`（改採 `NOW_LINE_MAX`）；針用「行太長」而非 `現況圖行超長` |
| [#141](https://github.com/rick546986/dev-flow/pull/141) **C** | `W`／`F`／`A`=1、其餘=0.5 與理由；Python 3.9-safe；Reject 表 B–F；`NOW_LINE_MAX` 寫死在 `RECT_*` 旁；拉丁 `Na` 連發大寫列已知殘 | fail-fast-first；針 `超過 13 全形字`（改採 A 的 `現況圖行超長`，另強制訊息含 `13`）；常數名 `NOW_LINE_EM`；不改 N3／S8 |

共識（三份皆採，本檔鎖定）：N=13；fail-loud；量剥標籤後的 SVG 欄位值；幾何本輪凍結；零版本 bump；實作另 PR。

## 13. 已拍板、可翻的選項

以下由本次合成拍板，翻任一項請同步改對應章節：

- `NOW_LINE_MAX = 13`，`>` 才紅（§6.1）。
- `W`／`F`／`A`=1、其餘=0.5（§6.2）。這是對 issue／A／B 原式的修正。
- 量 parse 後四欄，不量原始行、不量 caption、不量 `<pre>`（§6.2）。
- 一則 `ValueError` 列完所有超欄；針 `現況圖行超長` 且訊息含 `13`（§7）。
- 牙只在產 html 時；N9 是作者主場；S8 不目測（§4、§9）。
- Reject 表：wrap／widen／shrink／ellipsis／warn-0（§8）。
- 幾何本輪凍結（§5、§11）。
- 零版本 bump（§1、§9）。
- 審頁產生器本輪不動（§5、§11）。
- 拉丁 `Na` 連發大寫低估列已知殘，本 hop 不修（§6.3）。

## 14. Non-goals

- 本 brief PR：**不實作守衛、不 bump 版本、不 merge 當修法。**
- 不改 `scripts/build-stage1-html.py` 審頁產生器（本輪零 diff）。
- 不加寬框、不改字級、不換行、不裁字、不改 html-shell 幾何。
- 不正名 `_templates/1-discussion.md`／example 的「邏輯圖」槽（既有缺口，不是 #138）。
- 不為審頁抄同一顆牙（若要抄，另開 issue）。
- 不修拉丁全大寫 `Na` 低估。
