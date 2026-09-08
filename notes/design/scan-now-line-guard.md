# 現況圖行長守衛（#138 Agent C brief）

> 五份審查裡本檔只代表 **C：skeptical review**。先審 issue 提議的修法，再定採用項。
> 本檔是 **design note 正本**，不是契約。後續實作另開 PR。
> 審過 main tip `96b999f`（plugin `3.22.0`、契約 `2.0.0`）：issue 行號仍準。
> 本檔用到的 repo 名詞：掃頁產生器 `scripts/build-scan-html.py`（S10）、
> `#scan-now` SVG、`unicodedata.east_asian_width`、Interview Log 牙
> （`parse_log` → `ValueError` → `die(1, "拒絕:%s")`）。

## 1. Status

本檔是 **design note 正本**，不是契約。後續實作另開 PR。
零版本 bump（`.claude-plugin/plugin.json`、`devflow-contract.json` 皆不動）。
不加 hop／gate／審頁解鎖。本輪只定「行長牙怎麼咬」，不動 SVG 幾何。

核過的 issue 行號（`96b999f`）：

| issue 寫 | 現況 |
|---|---|
| `build-scan-html.py:576` 逐行 `<text>` | 仍是 `render_svg` 輸出 `<text text-anchor="middle" x="100">` |
| `:45` 框寬 160、viewBox 200 | `VB_W = 200`；`RECT_X, RECT_W, RECT_H = 20, 160, 88` |
| `:15` 「不裁字」 | 檔頭仍只寫不裁，無每行上限 |
| `SKILL.md:156-161` | 視覺版仍「每框四行」「不裁字」，無字數上限 |
| `N9-write-md.md` / `S10-html.md:29` | N9 只管從 Journey 長圖；S10 只寫四行形狀 |

## 2. Problem

`render_svg` 把解析後的四欄（誰／做什麼／工具／痛點）各畫成置中 `<text>`，
框寬鎖死 160。一行超過約 13 個全形字就左右凸出 `x=20 width=160` 的 rect，
遮到框線。產生器仍 exit 0、印 `wrote …`。

文件只說「不裁字」「每框四行」，沒有每行上限。撰寫者第一次產 html
幾乎必定凸框，要靠人看圖才回頭改 md。同檔對 Interview Log 文法已經
fail-loud；現況圖行長是同一類「形狀壞了還綠」缺口。

issue 修法 = 估寬超過就 `ValueError`。這是合理預設，但不是唯一解，
也不是可以不審就抄的契約。本檔先把替代方案否決完，再把採用項寫成實作契約。

## 3. Thesis

**框寬是契約，字去就框。超過就跟 Interview Log 一樣立刻 `ValueError`，
不准靜默產凸框圖，也不准產生器偷偷改圖來救長句。**

核心原則：**fail-loud 守的是「這一行畫得下」，不是「這一句產品痛寫得完」。**
現況圖是標題卡。寫太長 = md 不合格。

量的是**畫面上的欄位值**，不是 md 原始行（`誰:`／`做什麼:` 標籤會被剝掉、
不進 `<text>`）。

對 issue 公式的修正（C 與 A／B 的分歧）：**Ambiguous（`A`）算 1，不算 0.5。**
理由見 §4、§7.2。其餘仍採 fail-loud、N=13、不動幾何。

## 4. Alternatives（A–F 否決表）

每一項：一句利、一句弊、採用或否決。採用項只有一個。

| # | 方案 | 利 | 弊 | 裁決 |
|---|---|---|---|---|
| A | 超寬 `ValueError`（issue 提議） | 與 Interview Log 同慣例；CI／S10 立刻紅，不再靠人看圖 | 估寬是 UAX #11 類別、不是 glyph；全形拉丁大寫會低估 | **採用**（公式改 `W/F/A=1`，見 §7） |
| B | 同框軟換行／多行 `<text>`／`<tspan>` | 不裁字、不拒長句 | 框高鎖 88、四行 y 鎖 18／44／64／84；多一行就撞行或破「每框四行」牙 | **否決** |
| C | 加寬 rect／viewBox | 字全留下、產器仍綠 | `viewBox 200`、外層 `width:220px`、`RECT_W=160` 已被 SKILL／殼／`check-devtalk-fig-graph.sh` 鎖死；一條長句會逼整圖變寬，沒有上限 | **否決** |
| D | 自動縮字級 | 幾何不動、長句仍進框 | 「字 11px」是寫死的；縮到看不見仍是靜默假綠 | **否決** |
| E | 截斷加省略號 | 永不凸框 | 檔頭、SKILL、fig-graph 牙都寫「不裁字」；截了作者看不到自己寫了什麼 | **否決** |
| F | 警告但 exit 0 | 不擋產頁 | CI 當綠；`wrote …` 仍出凸框 html；與同檔 Log 牙不一致 | **否決** |

不另開第七案（`wcwidth`、字型量測、拉丁寬度表）：新依賴或新表都會破
「stdlib + 編譯地板 3.9」；本 hop 的洞是 30 個全形字，不是排版引擎。

B／C／D 都是「產生器改圖救長句」。現況圖幾何已經有牙，改圖 = 另開 issue。
E 直接違反「不裁字」。F 把本 issue 的根因（exit 0）留著。
所以只剩 A。

## 5. Do（實作時）

- 檔頭常數 `NOW_LINE_EM = 13`，放在 `RECT_*` 旁邊（約 L45）。常數寫死，
  **不要**執行期用 `RECT_W / 11` 反推。
- `now_line_em(s)`：逐字 `unicodedata.east_asian_width`；`W`／`F`／`A` = 1.0，其餘 = 0.5。
- `render_svg` 在吐 `<text>` 前檢查四欄；`now_line_em(s) > 13` → `ValueError`。
- 多欄／多框同時超：框序 1-based、欄序 誰→做什麼→工具→痛點，**第一個超的就 raise**
  （與 `parse_log` 同：fail-fast，不收集全部）。
- 檔頭 docstring 補「每行 ≤ 13 全形字（W/F/A=1、其餘=0.5），超過 exit 1」；
  `exit:` 那行把「行超長」算進 exit 1。
- N9／SKILL 視覺版／S10／guide 原文各補一句上限。牙進 `check-devtalk-fig-graph.sh`。

## 6. Don't

- 不換行、不自動斷欄、不縮 `font-size`、不拉 `viewBox`／`RECT_W`、不改 `html-shell` CSS。
- 不改 `parse_frames`／一行四欄 vs 四行堆疊的拆法。
- 不檢查 md 原始行（含標籤）、不檢查圖下固定字「痛在最後一步」、不檢查 `<pre>` 退路。
- 不動審頁 `scripts/build-stage1-html.py`（另一支幾何；#138 只點掃頁）。
- 不把行長檢查塞進 N3／S8，不另開 md-write-time linter（寫作節點不得寫程式；雙牙會漂）。
- 不 bump plugin／契約。不加 hop、不改 graph。
- 不准 warning-only、不准截斷後繼續 `wrote`。
- 不准引入 `wcwidth` 或任何非標準庫。
- 不准為拉丁大寫另做第三權重（殘見 §7.3，本 hop 不修）。

## 7. 公式、N、錯誤形狀

### 7.1 門檻

`NOW_LINE_EM = 13`（全形單位）。**`em(s) ≤ 13` 綠；`em(s) > 13` 紅。**
13 整剛好過；13.5（例如 27 個半形，或 13 全形 + 1 半形）紅。

怎麼得出 13（常數寫死）：

| N | `N×11` | 單側空隙 | 判讀 |
|---|---|---|---|
| 13 | 143 | 8.5px | 最後一個安全整數；字級／字重微漂還蓋得住 |
| 14 | 154 | 3.0px | 貼 `stroke`（殼 `.b` stroke-width 1），圓角／微寬就凸 |
| 15 | 165 | 負 | 必凸 |

`RECT_W = 160`。CJK 在 11px 下 ≈ 1em（§7.2）。`160 / 11 ≈ 14.55`，
扣左右各約 6–8 user unit（`rx=6` + stroke），可用 ≈ 144 → `144 / 11 ≈ 13.09`。
issue 目視也是「約 13 全形」。**不賭 14。**

之後若有人改字級或框寬，必須**同時改這個常數**，不准讓公式 silently 跟著漂。

### 7.2 公式（對 issue 的修正）

```python
import unicodedata

def now_line_em(s):
    total = 0.0
    for ch in s or "":
        total += 1.0 if unicodedata.east_asian_width(ch) in ("W", "F", "A") else 0.5
    return total
```

| 類 | 權重 | 例子 |
|---|---|---|
| `W`／`F`／`A` | 1.0 | 中日韓、全形 `Ａ`、全形標點 `，`、歧義 `—`／`–`／`×` |
| 其餘（`Na`／`N`／`H`） | 0.5 | ASCII、半形假名、空白 |

issue 寫「W/F=1、其餘=0.5」，把 `A` 丟進 0.5。C 不採。

- UAX #11 的 `A`（Ambiguous）在 CJK 字型通常當全形畫。
- `—`（EM DASH）與 `–`（EN DASH）在 3.12 `unicodedata` 都是 `A`。
  DejaVu／Liberation 11px：`—` = 11.0px（1em），`–` ≈ 0.5–0.56em。
- 若 `A=0.5`，26 個 `—` 估寬 13、實畫 286px，又是靜默凸框。
  本 issue 要消滅的就是這種洞；N=13 的 17px 空隙是留給拉丁 `Na` 略寬於 0.5em，
  **不是**留給 `A` 少算一倍。
- 現有樣張「新增附表五、選 A–F」：`A=0.5` 時 9.0，`A=1` 時 9.5，仍遠低於 13。
  改權重不誤殺 fixture。

量 **parse 之後、`esc()` 之前** 的 `who`／`action`／`tool`／`pain`（與 `<text>` 同源）。
空字串 `em=0`，本牙放行（痛空仍走既有「痛不准空」牙，不合併）。
combining mark／ZWJ 各算 0.5（略高估）。fail-loud 可接受，不為它們開例外。

標籤不計量：`做什麼: 在某作業系統…` 畫面上只有冒號後的值。
守衛若去量含標籤的原始行，會誤殺短值。

`<pre id="scan-now">` 退路（`parse_frames` 抽不到框）沒有 160 寬 rect，**本牙不跑**。

### 7.3 公式對 11px 實畫準不准

在 `96b999f` 對本機 CJK 字型（Droid Sans Fallback）讀 `hmtx`：
純 `W`／`F` 字（`全`、`、`、`／`）11px 下 **剛好 11.0px = 1em**。
13 個 `全` = 143px、14 個 = 154px，與 §7.1 表一致。
現有可解析現況圖（html-scan good、`example/subsidy-3-0-plus`）最長欄 ≤ 9.5
（`A=1` 後「選 A–F」），N=13 不誤殺。

issue 示範句「做什麼: 在某作業系統跑某腳本, 把某清單寫進某資料庫再搬到某處」
整行估寬 30.0；剝標籤後仍 26.0，必拒。

**殘（本 hop 不修）**：拉丁 `Na` 是比例字。Liberation／DejaVu 11px 下
`i` ≈ 0.22–0.28em（高估）、`A` ≈ 0.67em、`W` ≈ 0.94–0.99em（低估）。
26 個 `W` 估寬 13、實畫 ≈ 270px，公式放行、畫面凸框。
現況圖文類是中文標題卡加短拉丁 token（`PLUS`、`OPU`、`2PN`），不是 26 連發大寫。
不為這個殘加第三權重、不加 `wcwidth`。

結論：對本產器真正會畫的 CJK 行，W/F 與 11px 實畫對得夠準；
把 `A` 升成 1 是為堵 issue 公式自己留的靜默洞。拉丁連發大寫列為已知殘。

### 7.4 Python 3.9 地板

編譯地板是 3.9（`scripts/check-py-floor.sh`、`docs/PLUGIN.md`）。
本牙只用 `unicodedata.east_asian_width`：stdlib、Python 2.4 起就有，
3.9 簽名仍是 `east_asian_width(chr) -> str`，回傳 `F/H/W/Na/A/N`。
**沒有 3.10+ API 約束。**

實作禁令（對齊既有產器風格＋地板）：

- 不准 `match`／`case`（3.10）。
- 不准在 f-string **表達式**裡寫反斜線（3.12 才合法；3.8.0 已踩過）。
  訊息用既有 `%-format`。
- 不准 `from __future__ import annotations` 才寫得動的新標註；本檔本來就幾乎無標註。
- 不准新依賴（`wcwidth` 不在 stdlib，也不在 3.9 地板保證裡）。
- 3.9 與 3.12 的 `unidata_version` 不同（約 Unicode 13 vs 15）。
  BMP 中日韓的 `W`／`F`、以及 `—`／`–` 的 `A`，從 Unicode 1.1 就穩定。
  本 hop 不為新碼點開例外。

### 7.5 錯誤訊息

`main` 已有 `except ValueError: die(1, "拒絕:%s" % exc)`。本牙只 raise，不另開 exit。

```text
現況圖行超過 13 全形字:第{i}框{field}「{text}」
```

實例：第 2 框做什麼寫了 14 個全形 →

```text
拒絕:現況圖行超過 13 全形字:第2框做什麼「在某作業系統跑某腳本把清單寫進庫」
```

- `{i}` 從 1。`{field}` 只准 `誰`／`做什麼`／`工具`／`痛點`。
- `{text}` 用欄位原文（未 `esc`）。
- 牙針（needle）固定子字串：`超過 13 全形字`。
- 一句、fail-fast。不把公式全文塞進 stderr（公式正本是本檔 §7.2）。
- 不一次列完全部超欄：與 `parse_log` 同；作者改完再跑，下一條會再紅。

## 8. 形狀（md／html 本輪不變）

S10 六件不變。`#scan-now` 仍是直式三框、每框四行、
`viewBox="0 0 200 420"`（三步）、`rect x=20 width=160 height=88`、
`text-anchor="middle" x=100`、字 11px、不裁字。

md 現況圖 grammar 不變：仍吃「一行四欄」與「四行堆疊」。
本 hop 不新增章節、不改標籤同義詞。

**不動**：`scripts/build-stage1-html.py`、審頁契約、`skills/dev-talk/html-shell.html`
幾何、`graph.yaml`、vbox-fig。

## 9. 範圍：要改與不改的檔

「不升 plugin」= 不 bump 版本，不改 graph、不加節點。節點與指南的**文字**可改。

| 檔 | 改什麼（實作 PR，本 brief 不動這些檔） |
|---|---|
| `scripts/build-scan-html.py` | `NOW_LINE_EM`；`now_line_em`；`render_svg` 前檢查；檔頭「不裁字」旁補上限；`exit:` 把行超長算進 1 |
| `scripts/check-devtalk-fig-graph.sh` | `TOOTH_CASES` 加 `bad-now-line`；`check_now_line_edges()`（直接 import `now_line_em`）；檔頭註解補「超長 fail-loud」 |
| `scripts/fixtures/devtalk-html-scan/bad-now-line/1-discussion.md` | 從 good 抄一份，只把一欄改成 14 全形 |
| `scripts/fixtures/devtalk-html-scan/assert-teeth.py` | `BAD` 加 `("bad-now-line", "超過 13 全形字")` |
| `skills/dev-talk/nodes/N9-write-md.md` | 補一句：渲染後四欄每行 ≤ 13 全形字，超過產 html 會 exit 1 |
| `skills/dev-talk/SKILL.md` | 約 L156–161 視覺版「不裁字」旁補「每行 ≤ 13 全形字（W/F/A=1 其餘=0.5），超過產生器 exit 1」 |
| `skills/dev-talk/nodes/S10-html.md` | 補一句：產生器對超長行 fail-loud，不是看圖才改 |
| `guides/guide-dev-talk.html` | 視覺版「原文」blockquote 必須跟 SKILL 逐字同步（`check-devtalk-guide-sync.sh`） |

本輪**不改**：`html-shell.html`、`build-stage1-html.py`、`graph.yaml`、
`_templates/1-discussion.md`（無現況圖寫作節）、N3、S8、example、plugin／契約版本。

## 10. 牙與判準

**牙**（住 `scripts/build-scan-html.py`，fail-closed）：

1. 任一框四欄 `now_line_em(s) > NOW_LINE_EM` → `ValueError`，訊息含 `超過 13 全形字` 與框號／欄名／原文。
2. 不准截斷、不准換行、不准縮字後繼續寫檔。

**邊界（`check_now_line_edges`，直接餵 `now_line_em`，不必整份 md）**：

| 輸入 | `em` | 期望 |
|---|---|---|
| `""` | 0 | 0 |
| 13 個 `字` | 13.0 | ≤13 |
| 14 個 `字` | 14.0 | >13 |
| 26 個 `A`（拉丁、`Na`） | 13.0 | ≤13 |
| 27 個 `A` | 13.5 | >13 |
| 12 個 `字` + `AB` | 13.0 | ≤13 |
| 12 個 `字` + `ABC` | 13.5 | >13 |
| 全形 `Ａ`（`F`） | 1.0 | 與半形 `A`=0.5 不同 |
| `—`（EM DASH、`A`） | 1.0 | 與 issue 原式 0.5 不同；C 採 1 |
| 13 個 `—` | 13.0 | ≤13 |
| 14 個 `—` | 14.0 | >13 |

**整檔牙**：`bad-now-line` 必須 exit 1 且 stderr 含 `超過 13 全形字`。
既有 `good/1-discussion.md` 必須仍綠。

**無牙、靠人**：句子好不好讀、能不能再短；只保證不凸框。
拉丁 26 連發大寫的殘（§7.3）本 hop 無牙。

**後續實作 PR 過關**＝下列全真（本檔本身不算過關）：

1. §9 表列檔全部改到，`check-devtalk-fig-graph.sh`／`check-devtalk-guide-sync.sh` 綠。
2. 牙 1 + 邊界表 + `bad-now-line` 都掛上；good 仍綠。
3. SVG 幾何不變：`viewBox 200×420`（三步）、`rect x=20 width=160 height=88`、`text-anchor=middle x=100`、字 11px。
4. 超長輸入 exit 1，不印 `wrote …`。
5. 版本零 bump。`check-py-floor.sh` 仍綠（3.9 可 parse）。

## 11. Five-review table

| # | 焦點 | VERDICT | ONE_LINE |
|---|---|---|---|
| A | fail-loud | ADOPT | 超寬 `ValueError`；N=13；量渲染欄位；第一個超欄即 raise |
| B | wrap | REJECT | 四行 y 與框高 88 鎖死，換行即破「每框四行」 |
| C | widen | REJECT | viewBox／220px／RECT_W 已有牙；加寬沒上限 |
| D | shrink | REJECT | 11px 寫死；縮字是另一種靜默假綠 |
| E | ellipsis | REJECT | 直接違反「不裁字」 |
| F | warn-0 | REJECT | 根因就是 exit 0；警告過不了 CI |

## 12. 已拍板、可翻的選項

以下由本次 brief 拍板，翻任一項請同步改對應章節：

- 採用 A、否決 B–F（§4、§11）。
- `NOW_LINE_EM = 13`，`>` 才紅（§7.1）。
- `W`／`F`／`A`=1、其餘=0.5（§7.2）。這是對 issue 原式的修正。
- 量 parse 後四欄，不量原始行、不量 caption、不量 `<pre>`（§7.2）。
- 訊息形狀與針 `超過 13 全形字`（§7.5）；第一個超欄即 raise。
- 幾何本輪凍結（§6、§8）。
- 不改 N3／S8、不另開 md-lint（§6、§9）。
- 零版本 bump（§1、§9）。
- 審頁產生器本輪不動（§6）。
- 拉丁 `Na` 連發大寫低估列已知殘，本 hop 不修（§7.3）。
