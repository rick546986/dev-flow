# 現況圖行長守衛（#138 Agent A brief）

> 對齊 issue #138。本檔是 **design note 正本**，不是契約。後續實作另開 PR。
> 審過 main tip `96b999f`（plugin `3.22.0`、契約 `2.0.0`）：issue 行號仍準。
> 本檔用到的 repo 名詞：掃頁產生器 `scripts/build-scan-html.py`（S10）、
> `#scan-now` SVG、`unicodedata.east_asian_width`、Interview Log 牙
> （`parse_log` → `ValueError` → `die(1, "拒絕:%s")`）。

## 1. Status

本檔是 **design note 正本**，不是契約。後續實作另開 PR。
零版本 bump（`.claude-plugin/plugin.json`、`devflow-contract.json` 皆不動）。
不加 hop／gate／審頁解鎖。**本輪只加 fail-loud 行長牙**，不動 SVG 幾何。

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
框寬鎖死 160。一行超過約 13 個全形字（或約 26 個半形）就左右凸出
`x=20 width=160` 的 rect，遮到框線。

產生器仍 exit 0、印 `wrote …`，沒有警告。文件只說「不裁字」「每框四行」，
沒有每行上限。撰寫者第一次產 html 幾乎必定凸框，要靠人看圖才回頭改 md。

同檔對 Interview Log 文法已經 fail-loud（`ValueError` → `main` 的
`die(1, "拒絕:%s")` → exit 1）。現況圖行長是同一類「形狀壞了還綠」缺口。

## 3. Thesis

**現況圖每一條會畫進 SVG 的字，寬度必須事先算過；超過就跟 Interview Log 一樣
立刻 `ValueError`，不准靜默產凸框圖。**

核心原則：**框寬是契約，字去就框，不是框去就字。**
不換行、不縮字、不拉 viewBox。寫太長 = md 不合格，不是產生器該救。

量的是**畫面上的欄位值**，不是 md 原始行（`誰:`／`做什麼:` 標籤會被剝掉、
不進 `<text>`）。

## 4. Do（實作時）

- 檔頭常數 `NOW_LINE_MAX = 13`，放在 `RECT_*` 旁邊（約 L45）。
- `display_width(s)`：逐字 `unicodedata.east_asian_width`；`W`／`F` = 1.0，其餘 = 0.5。
- `render_svg`（或它呼叫的 helper）在吐 `<text>` 前檢查四欄；`W(s) > 13` → `ValueError`。
- 多欄／多框同時超：框序 1-based、欄序 誰→做什麼→工具→痛點，**第一個超的就 raise**（不用收集全部）。
- 檔頭 docstring 補「每行 ≤ 13 全形單位，超過 exit 1」；`exit:` 那行把「行超長」算進 exit 1。
- N9／SKILL 視覺版／S10／guide 原文各補一句上限。牙進 `check-devtalk-fig-graph.sh`。

## 5. Don't

- 不換行、不自動斷欄、不縮 `font-size`、不拉 `viewBox`／`RECT_W`、不改 `html-shell` CSS。
- 不改 `parse_frames`／一行四欄 vs 四行堆疊的拆法。
- 不檢查 md 原始行（含標籤）、不檢查圖下固定字「痛在最後一步」、不檢查 `<pre>` 退路。
- 不動審頁 `scripts/build-stage1-html.py`（另一支幾何；#138 只點掃頁）。
- 不 bump plugin／契約。不加 hop、不改 graph。
- 不准 warning-only、不准截斷後繼續 `wrote`。

## 6. 寬度公式與訊息形狀

### 6.1 門檻

`NOW_LINE_MAX = 13`（全形單位）。**`W(s) ≤ 13` 綠；`W(s) > 13` 紅。**
13 整剛好過；13.5（27 個半形）紅。

怎麼得出 13（常數寫死，**不要**執行期用 `RECT_W / 11` 反推）：

- 框 `RECT_W = 160`、`rx=6`，左右至少留約 6–8 user unit，可用 ≈ 144。
- 文件與殼都寫字 11px。若以 11 user unit／全形估：`144 / 11 ≈ 13.09`。
- issue 目視也是「約 13 全形／26 半形」開始凸框。
- Agent A 取嚴：卡在 13，不賭 14（`14 × 11 = 154`，貼邊、圓角會吃字）。

之後若有人改字級或框寬，必須**同時改這個常數**，不准讓公式 silently 跟著漂。

### 6.2 公式

```python
from unicodedata import east_asian_width

def display_width(s):
    total = 0.0
    for ch in s or "":
        total += 1.0 if east_asian_width(ch) in ("W", "F") else 0.5
    return total
```

| 類 | 權重 | 例子 |
|---|---|---|
| `W`／`F` | 1.0 | 中日韓、全形 `Ａ`、全形標點 `，` |
| 其餘（`Na`／`N`／`H`／`A`…） | 0.5 | ASCII、半形假名、ambiguous `×`／`—` |

- 量 **parse 之後、`esc()` 之前** 的 `who`／`action`／`tool`／`pain`（與 `<text>` 同源）。
- 空字串 `W=0`，本牙放行（痛空仍走既有「痛不准空」牙，不合併）。
- combining mark／ZWJ 各算 0.5（略高估）。fail-loud 可接受，不為它們開例外。
- `A`（ambiguous）本輪也 0.5，跟 issue 公式一字不差。不把 `A` 升成 1。

標籤不計量：`做什麼: 在某作業系統…` 畫面上只有冒號後的值。
守衛若去量含標籤的原始行，會誤殺短值。

`<pre id="scan-now">` 退路（`parse_frames` 抽不到框）沒有 160 寬 rect，**本牙不跑**。

### 6.3 錯誤訊息

`main` 已有 `except ValueError: die(1, "拒絕:%s" % exc)`。本牙只 raise，不另開 exit。

```text
現況圖行超長:第{i}框{field}「{text}」{w}>{N}
（east_asian_width W/F=1 其餘=0.5;見 notes/design/scan-now-line-guard.md）
```

實例：第 2 框做什麼寫了 14 個全形 →

```text
拒絕:現況圖行超長:第2框做什麼「在某作業系統跑某腳本把清單寫進庫」14.0>13
（east_asian_width W/F=1 其餘=0.5;見 notes/design/scan-now-line-guard.md）
```

- `{i}` 從 1。`{field}` 只准 `誰`／`做什麼`／`工具`／`痛點`。
- `{text}` 用欄位原文（未 `esc`）；`{w}` 用 `display_width` 的浮點（一位小數即可）。
- 牙針（needle）固定子字串：`現況圖行超長`。
- 舊單行 Log 會指向 `stage1-context-chain.md`；本牙同樣指向本檔，方便對帳。

## 7. 範圍：要改與不改的檔

「不升 plugin」= 不 bump 版本，不改 graph、不加節點。節點與指南的**文字**可改。

| 檔 | 改什麼（實作 PR，本 brief 不動這些檔） |
|---|---|
| `scripts/build-scan-html.py` | `NOW_LINE_MAX`；`display_width`；`render_svg` 前檢查；檔頭「不裁字」旁補上限；`exit:` 把行超長算進 1 |
| `scripts/check-devtalk-fig-graph.sh` | `TOOTH_CASES` 加 `bad-now-line`；`check_now_line_edges()`（直接 import `display_width`）；檔頭註解補「超長 fail-loud」 |
| `scripts/fixtures/devtalk-html-scan/bad-now-line/1-discussion.md` | 從 good 抄一份，只把一欄改成 14 全形 |
| `scripts/fixtures/devtalk-html-scan/assert-teeth.py` | `BAD` 加 `("bad-now-line", "現況圖行超長")` |
| `skills/dev-talk/nodes/N9-write-md.md` | 補一句：渲染後四欄每行 ≤ 13 全形單位，超過產 html 會 exit 1 |
| `skills/dev-talk/SKILL.md` | 約 L156–161 視覺版「不裁字」旁補「每行 ≤ 13 全形單位（W/F=1 其餘=0.5），超過產生器 exit 1」 |
| `skills/dev-talk/nodes/S10-html.md` | 補一句：產生器對超長行 fail-loud，不是看圖才改 |
| `guides/guide-dev-talk.html` | ⑧ 視覺版「原文」blockquote 必須跟 SKILL 逐字同步（`check-devtalk-guide-sync.sh`）；畫法表「不裁字」旁加上限 |

本輪**不改**：`html-shell.html`、`build-stage1-html.py`、`graph.yaml`、
`_templates/1-discussion.md`（無現況圖節）、S8、example、plugin／契約版本。

## 8. 牙與判準

**牙**（住 `scripts/build-scan-html.py`，fail-closed）：

1. 任一框四欄 `display_width(s) > NOW_LINE_MAX` → `ValueError`，訊息含 `現況圖行超長` 與框號／欄名／原文／`w>N`。
2. 不准截斷、不准換行、不准縮字後繼續寫檔。

**邊界（`check_now_line_edges`，直接餵 `display_width`，不必整份 md）**：

| 輸入 | `W` | 期望 |
|---|---|---|
| `""` | 0 | 0 |
| 13 個 `字` | 13.0 | ≤13 |
| 14 個 `字` | 14.0 | >13 |
| 26 個 `A` | 13.0 | ≤13 |
| 27 個 `A` | 13.5 | >13 |
| 12 個 `字` + `AB` | 13.0 | ≤13 |
| 12 個 `字` + `ABC` | 13.5 | >13 |
| 全形 `Ａ`（`F`） | 1.0 | 與半形 `A`=0.5 不同 |

**整檔牙**：`bad-now-line` 必須 exit 1 且 stderr 含 `現況圖行超長`。
既有 `good/1-discussion.md`（最長約「建補助案、填申請日」≈ 8.5）必須仍綠。

**無牙、靠人**：句子好不好讀、能不能再短；只保證不凸框。

**後續實作 PR 過關**＝下列全真（本檔本身不算過關）：

1. §7 表列檔全部改到；`check-devtalk-fig-graph.sh`／`check-devtalk-guide-sync.sh` 綠。
2. 牙 1 + 邊界表 + `bad-now-line` 都掛上；good 仍綠。
3. SVG 幾何不變：`viewBox 200×420`（三步）、`rect x=20 width=160 height=88`、`text-anchor=middle x=100`、字 11px。
4. 超長輸入 exit 1，不寫 html（或寫了也會被測完刪；重點是 rc≠0 且有針）。
5. 版本零 bump。

## 9. Agent A 立場

| 焦點 | VERDICT | ONE_LINE |
|---|---|---|
| A | NARROW | 嚴守 fail-loud、N=13、量渲染欄位；不換行、不縮字、不拉畫布 |

寬鬆替代（本檔不採）：N=14、warning-only、只量 md 原始行、自動 wrap。
那些跟 Interview Log 慣例或「框寬是契約」衝突，要另開 brief。

## 10. 已拍板、可翻的選項

以下由本次 brief 拍板，翻任一項請同步改對應章節：

- `NOW_LINE_MAX = 13`，`>` 才紅（§6.1）。
- `W`／`F`=1、其餘（含 `A`）=0.5（§6.2）。
- 量 parse 後四欄，不量原始行、不量 caption、不量 `<pre>`（§6.2）。
- 訊息形狀與針 `現況圖行超長`（§6.3）；第一個超欄即 raise。
- 幾何本輪凍結（§5、§8）。
- 零版本 bump（§1、§7）。
- 審頁產生器本輪不動（§5）。
