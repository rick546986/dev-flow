# 現況圖行長守衛（#138 / Agent B）

> 五份審查裡本檔只代表 **B：writer-facing UX**。牙的幾何門檻跟 Interview Log 一樣 fail-loud，但成功條件是撰寫者在寫 md 時就知道上限，而不是產完 html 才用眼睛發現凸框。
> 本檔是 **design note 正本**，不是契約。後續實作另開 PR。
> 本檔用到的 repo 名詞：掃頁產生器 `scripts/build-scan-html.py`（S10）、
> 落檔節點 `skills/dev-talk/nodes/N9-write-md.md`、產頁節點 `S10-html.md`、
> 入口 `skills/dev-talk/SKILL.md` 視覺版、逼問 `N3-probe.md` 3a、複核 `S8-review.md` ⑧。

## 1. Status

本檔只定設計。零行為改動、零 fixture、零版本 bump
（`.claude-plugin/plugin.json`、契約 schema 皆不動）。
不加 hop／gate／審頁解鎖。不改框寬、不改字級、不裁字、不自動換行。

對應 issue：https://github.com/rick546986/dev-flow/issues/138
調查基準：`main` v3.22.0 / `96b999f`。

## 2. Problem

`render_svg` 把解析後的四欄（誰／做什麼／工具／痛點）各輸出一行
`<text text-anchor="middle" x="100">`（`scripts/build-scan-html.py` 約 L576）。
框死寬 `x=20 width=160`、字 11px（`html-shell.html`：`-apple-system,"PingFang TC","Noto Sans TC"`）、檔頭寫「不裁字」。
一行估寬超過框，文字左右凸出、遮框線；產生器仍 `exit 0`、印 `wrote …`。

撰寫者此刻只拿到兩條規則：

- N9／SKILL 視覺版／S10：每框四行、直式三框、不裁字
- 沒有每行字數上限，也沒有「超了會怎樣、改哪一欄」

所以第一次產 html 幾乎必靠人開瀏覽器才發現，再回頭改 md 重生。
同檔對 Interview Log 文法已經 `ValueError` → `exit 1`；現況圖行長是同一支產器裡的靜默洞。

## 3. Thesis

**現況圖是標題卡，不是 Current Journey 整格搬進來。**
上限由框寬決定，不由「產品痛能不能寫長」決定。
撰寫者在 N9 落檔時就看見 N 與公式；S10 是牙，不是發現處。
錯誤必須點名第幾框哪一欄（誰／做什麼／工具／痛點），並列出該欄渲染值與估寬，叫人收成短句再重生。

核心原則：**規則寫在寫 md 的節點；牙只留在產 html 的那一支腳本。**
兩處數字必須同句，禁止第二支 md-lint 跟產器各守一個 N。

## 4. Do（實作時）

- 產器對**渲染值**估寬：`parse_frames` 之後、寫入 `<text>` 之前。標籤
  （`誰:`／`做什麼:`／`工具:`／`痛點:` 及同義，見 `FIELD_LABELS`）已經剝掉，不計入 N。
- `display_width(s) > 13` → `ValueError` → 既有 `die(1, "拒絕:%s" % exc)`。`= 13` 過。
- 一次列完本圖所有超長欄，不准只報第一條讓撰寫者跑四輪 S10。
- 檔頭常數與檔頭一句、N9、SKILL 視覺版、S10 用**同一個 N=13 與同一句公式**。
- N3 3a 改圖時就帶上限（圖常在落檔前改）。S8 ⑧ 只核 Journey 指紋，**不**目測凸框。
- `guides/guide-dev-talk.html` 標「原文」的視覺版 blockquote 必須跟 SKILL.md 逐字同步
  （`check-devtalk-guide-sync.sh`）。
- 牙 fixture 進 `check-devtalk-fig-graph.sh` 的 `check_log_teeth` 同款：good 仍綠、超長 bad `exit 1` 且 stderr 含欄名。

## 5. Don't

- 裁字、自動換行、加寬 `RECT_W`／`viewBox`、改 11px、改置中。
- 把 N 放到 14 或 16「好寫產品痛」——14 貼框線（`14×11=154`，單側 3px），15 已超 160；假綠比假紅更糟。
- 四欄各訂一個 N（痛點並不比較小：掃頁殼 `.cap` 仍是 11px）。
- 另寫一支 N9 md-lint／`--check-only`／編輯器 live lint（N9 本就不得寫程式；雙牙會漂）。
- 把行長檢查塞進 S8 人工掃，或叫 reviewer 開 html 目測。
- 動 `scripts/build-stage1-html.py`、審頁契約、`html-shell.html` 幾何、hop graph。
- 正名 `_templates/1-discussion.md`／example 的「邏輯圖」槽（既有缺口，不是 #138）。
- 守 `<pre id="scan-now">` 後備、守產生器自寫的「痛在最後一步」。
- bump plugin／契約版本。自動改寫作者的句子。

## 6. N 與公式

### 6.1 拍板

| 項 | 值 |
|---|---|
| N | **13** 全形單位 |
| 公式 | `display_width(s) = Σ 1.0 if east_asian_width(ch) in {W,F} else 0.5` |
| 比較 | `display_width(渲染值) > 13` 拒；`== 13` 過 |
| 計數對象 | `parse_frames` 後的 who／action／tool／pain，**剝標籤後** |
| 歧義字 `A`（±、– 等） | 0.5（跟 issue 建議、跟半形同一桶） |

常數放產器檔頭，建議名 `LINE_CAP = 13`，緊鄰 `RECT_W = 160`。

### 6.2 為什麼不是別的 N

幾何（`main` 現況，字 11px、框 160、CJK ≈ 1em）：

| N | `N×11` | 單側空隙 | 判讀 |
|---|---|---|---|
| 13 | 143 | 8.5px | 最後一個安全整數；字級／字重微漂還蓋得住 |
| 14 | 154 | 3.0px | 貼 `stroke`，PingFang 微寬就凸 |
| 15 | 165 | 負 | 必凸 |

13 不是「寫起來舒服的長度」，是「不裁字 + 死框寬」還能成立的上限。
把 N 放寬等於把牙打掉。要容長句，另開 issue 改框，不在本 hop。

### 6.3 實測（`96b999f`，同一支 `parse_frames` + 上式）

可解析的現況圖（fixture + `example/subsidy-3-0-plus`）**全部 ≤ 9.0**。
最長欄都是做什麼：`建補助案、填申請日`（9.0）、`新增附表五、選 A–F`（9.0）。
痛點最長：`PLUS 還不會自動切`（8.5）。N=13 不誤殺任何現有樣張。

`example/contract-expiry-reminder/1-discussion.md` **沒有現況圖**（槽仍叫邏輯圖，產器直接拒）。
它的 Current Journey 才是「真實產品句」樣本。若整格貼進四欄：

| 句子 | 估寬 | vs 13 |
|---|---|---|
| 翻私表（fixture 收法） | 3.0 | 過 |
| 私表更新靠自律,常漏 | 9.5 | 過 |
| 中間過程系統全程不可見 | 11.0 | 過 |
| 電話聯絡供應商窗口談條件 | 12.0 | 過 |
| 談成後改 Excel 標「已續」 | 12.5 | 過 |
| 月初翻 Excel 私表比對到期日 | 13.5 | **拒** |

結論：13 對**標題卡寫法**偏寬（現有圖 ≤9，還有約 4 單位緩衝）；
只對「Journey 整格搬進來」偏緊。偏緊是對的——N9 要的本就是收成後的誰／做什麼／工具／痛點，
不是表格原文。issue 舉的 30 全形示範句剝標籤後估寬 **26.0**，必拒。

## 7. 撰寫者在哪學會上限

只改文字，不新開 hop。用字必須含「≤13 全形」與「超過 S10 exit 1」，避免只寫「不要太長」。

| 檔 | 誰在讀 | 用字草稿（實作可微調標點，數字與公式不准漂） |
|---|---|---|
| `skills/dev-talk/nodes/N9-write-md.md`（做什麼 + 完成條件） | **主場**。人在寫 md | 現況圖每框四行（誰／做什麼／工具／痛點）。每行渲染值 ≤13 全形（`east_asian_width` W／F=1、其餘 0.5；行首「誰:」「做什麼:」等標籤不計）。超過會在 S10 產 html 時 exit 1，不裁、不換行。現況圖是標題卡，不要把 Current Journey 整格搬進來（「月初翻 Excel 私表比對到期日」→「翻私表」）。 |
| `skills/dev-talk/SKILL.md` 視覺版第 2 條 + SVG 那句 | 開場就看入口的人 | 在「不裁字」旁接：每行 ≤13 全形（估寬見 N9／產器檔頭），超過產器 exit 1。步 7 入口摘要加半句「每行 ≤13 全形」。 |
| `guides/guide-dev-talk.html` | 指南讀者 | 視覺版「原文」blockquote 與 SKILL 同步。形狀表「不裁字」改「不裁字；每行 ≤13 全形」。 |
| `skills/dev-talk/nodes/S10-html.md`（做什麼 + 完成條件） | 產頁當下 | 產生器對現況圖行長 fail-loud。stderr 點名第幾框哪一欄。改 md 該欄再重生，不要開瀏覽器目測凸框。 |
| `scripts/build-scan-html.py` 檔頭 L15 附近 + `exit:` 那行 | 讀腳本的人／CI | 「不裁字」改「不裁字。每行渲染值 ≤13 全形（W／F=1、其餘 0.5），超過 ValueError → exit 1」。`exit:1` 補「或現況圖行太長」。 |
| `skills/dev-talk/nodes/N3-probe.md` 3a | 落檔前就改圖的人 | 同步改現況圖時每行渲染值 ≤13 全形（公式同 N9）。 |
| `skills/dev-talk/nodes/S8-review.md` ⑧ | 複核者 | 加一句：行長由產器守，⑧ 不目測凸框；超長是 S10 的紅，不是本掃的人工項。 |

不寫進：`_templates/1-discussion.md`（仍叫邏輯圖，正名另案）、審頁契約、vbox-fig。

## 8. 錯誤訊息形狀

必須可執行：哪一框、哪一欄、估寬、上限、渲染原文、怎麼改、數字正本在哪。
一次列全部超長欄，框序 1-based，欄名用中文「誰／做什麼／工具／痛點」（對 `who/action/tool/pain`）。

```text
拒絕:現況圖行太長(每行 ≤13 全形;W/F=1、其餘 0.5;標籤不計):
  第1框「做什麼」估寬 13.5：「月初翻 Excel 私表比對到期日」
  第2框「痛點」估寬 16.0：「法務回覆要等而且進度完全不可見」
請收成標題卡再重生(例:「翻私表」／「進度不可見」)。見 notes/design/scan-now-line-guard.md
```

禁：只說「行太長」、只印 raw md 含標籤的那一行、不報欄名、exit 0 加 warning、
靜默截斷後仍 `wrote …`。

## 9. 牙落點：只在產 html 時 fail-loud

| 時機 | 做什麼 | 為什麼 |
|---|---|---|
| N3／N9 寫 md | **只寫規則**，不跑第二支檢查 | 寫作節點不得寫程式；公式出現在眼前就夠自數 |
| S8 | 不管行長 | ⑧ 是 Journey 指紋；目測凸框正是本 issue 要消滅的流程 |
| S10 `build-scan-html.py` | **唯一的牙** | 跟 Interview Log 同慣例：`ValueError` → `exit 1`、不寫 html |
| CI `check-devtalk-fig-graph.sh` | 跑產器打 good／bad fixture | 防牙被拿掉；mutation 複本可沒有 bad 目錄（既有慣例） |

不在「寫 md 的當下」另做機械檢查。發現處從「開 html」前移到「S10 紅字」，
學習處前移到 N9／N3／SKILL。這兩段缺一不可：只有牙沒有規則，第一次仍紅；
只有規則沒有牙，下一個模型又會靜默凸框。

`<pre>` 後備（`parse_frames` 抽不到框）不走行長牙；那是另一條「抽不到節點」路。

## 10. 範圍：要改與不改的檔

「不升 plugin」= 不 bump `.claude-plugin/plugin.json`，不改 graph，不加節點。
節點與指南的**文字**可改。

| 檔 | 改什麼 |
|---|---|
| `scripts/build-scan-html.py` | `LINE_CAP`；檔頭一句；`render_svg`（或 `parse_frames` 之後）估寬；一次列完的 `ValueError` |
| `scripts/check-devtalk-fig-graph.sh` | `check_log_teeth` 加一行長 bad；頂註「不裁字」補「超長行 exit 1」 |
| `scripts/fixtures/devtalk-html-scan/assert-teeth.py` | 同步加該 bad 與 stderr 針 |
| `scripts/fixtures/devtalk-html-scan/bad-<name>/1-discussion.md` | 十節齊、現況圖有一行 >13（建議做什麼欄 26 全形示範句）；其餘欄合法 |
| `skills/dev-talk/nodes/N9-write-md.md` | §7 主場句 |
| `skills/dev-talk/nodes/S10-html.md` | fail-loud、改 md 再重生 |
| `skills/dev-talk/nodes/N3-probe.md` | 3a 半句 |
| `skills/dev-talk/nodes/S8-review.md` | ⑧ 不目測 |
| `skills/dev-talk/SKILL.md` | 視覺版 + 步 7 入口 |
| `guides/guide-dev-talk.html` | 原文 blockquote + 形狀表 |

**不動**：`build-stage1-html.py`、`notes/design/stage1-review-ui-contract.md`、
`skills/dev-talk/html-shell.html` 幾何、`html-shell` 字級、hop `graph.yaml`、
`_templates/1-discussion.md` 標題、example 正名、plugin／契約版本。
既有 html-scan good 行長 ≤9，不必為 N=13 改圖。

## 11. 牙與判準

**牙**（住 `scripts/build-scan-html.py`，fail-closed）：

1. 任一框四欄渲染值 `display_width > 13` → `ValueError`，訊息含框序、中文欄名、估寬、渲染原文、N=13、收成提示。
2. 多欄同時超 → 一則訊息列完，仍 `exit 1`、不寫 html。
3. `display_width == 13` 過（含 13.0 的純 13 全形、或 26 個半形）。
4. 標籤不計：`做什麼: ` + 12 全形值必須過；同值若沒剝標籤會誤殺。
5. 不准 `[:N]` 截斷、不准 warning-only。

**無牙、靠文件**：撰寫者是否真的收成標題卡（語意對不對仍是 S8 ⑧）。

**後續實作 PR 過關**＝下列全真（本檔本身不算過關）：

1. §10 表列檔全部改到；`check-devtalk-fig-graph.sh`／`check-devtalk-guide-sync.sh` 綠。
2. 現有 html-scan good 與 fig-journey good 仍 `exit 0`。
3. 至少一份超長 bad：`exit 1`、不產（或產出也被測到不該留下）html、stderr 含「做什麼」或對應欄名、含「13」、含渲染原文片段。
4. 一份剛好 13 全形的欄必須綠（邊界）。
5. 一份「標籤 + 短值、合計 >13、值本身 ≤13」必須綠（證明剝標籤）。
6. S10 對超長 md 不得印 `wrote …`。
7. 掃頁六件、三框四行、框 160×88、不裁字、置中，其餘契約不變。
8. 版本零 bump。審頁產生器零 diff。

## 12. 已拍板、可翻的選項

以下由本 brief 拍板。翻任一項請同步改對應章節：

- N=13、`>` 才拒、W／F=1 其餘 0.5、剝標籤後再數（§6）。
- 學習處 = N9 主場 + SKILL／指南 + N3 3a；牙只在產器；S8 不目測（§7–§9）。
- 錯誤一次列完全部超長欄，欄名用中文四字（§8）。
- 不另開 md-write-time 機械檢查（§5、§9）。
- 不改框、不換行、不裁、不動審頁（§5）。
- 「不升 plugin」= 不 bump 版本，節點文字可改（§10）。

可另開、不在本 hop：加寬框／改字級；正名模板與 `contract-expiry-reminder` 的邏輯圖槽；審頁 `build-stage1-html.py` 是否抄同一顆牙。
