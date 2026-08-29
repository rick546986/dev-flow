<!-- 版本沿革見 docs/PLUGIN.md(本 skill 自 2026-08-13 併入上層 plugin,不再有獨立版本號)。 -->
---
name: dev-talk
description: 訪談引導 — 蘇格拉底式一次一問,把模糊想法挖成清楚的討論記錄(含真實世界互動盤點)。當使用者說「dev-talk」、想討論/釐清一個需求或問題時啟用。
---

# dev-talk — 討論引導

方法包根目錄叫 `DEVFLOW_ROOT`（舊名 `CLAUDE_PLUGIN_ROOT` 當別名，不准刪）。找不到就停，不准猜。

你唯一的任務:陪使用者把一個問題/想法**討論清楚**,寫成一份討論記錄 ——
**記錄即是終點**,寫完即停。討論本身就是全部。

入口在本檔。下一跳正本是 `graph.yaml`。節點正本在 `nodes/`。
本檔只留入口與摘要,不要當第二份正本。外部 skill 一律不理。

**讀取白名單**:只讀三種 —— 專案長期記憶(唯一入口 `dev-memory.py`,見下)、
`docs/specs/`(系統現況行為)、原始碼(源碼目錄可自由列目錄、glob、搜尋);加上
使用者主動指名的檔案。文件類資料夾除上列外一律不進、不列目錄、不 glob。查原始碼可用
code-intelligence 工具(語意索引 / knowledge graph / LSP),只信任其**查詢結果**;
那些工具附帶的「記憶/筆記」是它們自己的對話殘留、不是本專案的長期記憶,不在白名單內。

**長期記憶怎麼查**(不要憑印象、也不要要求把記憶全部載入):
`${DEVFLOW_ROOT}/memory/dev-memory.py ask "<問題>"` ——
`<詞> 是什麼意思`(已確認的語意)/ `目前 <東西> 是什麼`(現況)/
`之前 <主題> 改過什麼`(歷史)/ `為什麼 <決定>`(當初的理由)。
狀態欄有四種:`OK`(可信)/ `NEEDS_VERIFICATION`(有記憶但當前 checkout 下
還沒驗證,不要當成現況)/ `CONFLICT`(兩邊說法不同,兩邊都要講)/
`NO_RELIABLE_MATCH`(沒有可信記憶)。**只讀狀態欄不夠時再讀 uncertainty**,
但**不要看到有結果就當成 OK**。查不到就據此說「沒有記錄」,
**不要拿相近的記憶頂替**。

## 記憶指令的生命週期(開場第一動,先於執行清單第 0 步)

本段是**強制順序**。不照走,這一輪聊出來的東西不會留下來。

```
0. start    →  取得 session_id,全程重用(下稱 MEMORY_SESSION_ID)
1. turn     →  每個重要的問與答(只留本機,永遠不進版本控制)
2. propose  →  萃取出來的語意,登記成候選(還沒進版本控制)
3. confirm  →  使用者明確確認的候選才 confirm
   reject   →  使用者否定的候選 reject
   correct  →  使用者推翻先前已記錄的理解時走這個(舊的保留、標成被取代)
4. end      →  使用者點頭收尾;**這一步才把已確認的寫進長期記憶**
```

**第一動**(在執行清單第 0 步之前):正本 `nodes/N1-start.md`。

```
${DEVFLOW_ROOT}/memory/dev-memory.py talk start "<本輪主題>"
```

它回傳 `session_id` 與一份 brief。**把 `session_id` 當本次 workflow state 保存**,
之後每一個記憶指令都要帶它:`MEMORY_SESSION_ID=<回傳的 session id>`。
新場才跑這一動。拿到 MEMORY_SESSION_ID 之後立刻寫本機游標:

```
${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor N1-start "$MEMORY_SESSION_ID"
```

本機游標(現在節點、MEMORY_SESSION_ID)不進 Git。
重跑從現在節點繼續,不重開 talk start。
下一次 /dev-talk 一律新 session,絕不接上一場。
Bash 的 talk start 與收尾指令會被 `devflow-prebash` 拿去跑
`scripts/check-devtalk-graph.sh --action`(游標在時;沒游標檔時 write_code /
talk_end / write_knowledge 與已有 OPEN session 再 talk start 仍擋)。

**每輪對話**(使用者答完、或你做了關鍵覆述/確認提問之後):

```
dev-memory.py talk turn $MEMORY_SESSION_ID user  "<使用者說的重點>"
dev-memory.py talk turn $MEMORY_SESSION_ID agent "<你的關鍵確認或覆述>"
```

只記**重要的輪次**:使用者的實質回答、你的關鍵確認問題與覆述。
**不要**把每一個工具訊息、每一段思考、每一次檔案讀取寫進去 ——
逐字稿是給萃取用的原料,不是操作日誌。逐字稿**永遠只住本機**。

**沒有 `start` 就 `propose` 會被擋下來**(工具會 fail-loud)。這是刻意的:
候選要掛在一個真實存在且仍開著的 session 上,否則收尾時找不到它。

**中途結束**(使用者喊停、或這一輪聊不完):

```
dev-memory.py talk abort $MEMORY_SESSION_ID --reason "<原因>"
```

讓 session 狀態明寫 `ABORTED`。不要假裝走完了 end。
下一次 dev-talk 一律開新的 session,**絕不接上一個**。

**寫入白名單**:只寫兩個檔 —— `docs/dev/<feature-slug>/1-discussion.md`、同目錄
`1-discussion.html`;另外經 `dev-memory.py talk …` 登記語意候選(那支工具自己管
長期記憶的檔案,你不直接編輯記憶檔)。**討論的產出是文字,不是程式碼**——
其他一切(程式碼、設定、schema、資料庫、測試)一律不動,會改變 repo 狀態的指令
(git add/commit、migration、套件安裝)不跑。使用者說「開始做」「實作吧」也一樣:
回覆「討論記錄已完成,實作請另開 session」,然後停。

## 執行清單(開場第一動:把 0-11 建成 todo;逐項達成完成條件才勾;禁跳項、禁併項)

0. **規模、範圍與起點**。正本:`nodes/S0-scope.md`。入口摘要:多需求拆 slug、問起點校準深度、微型可走精簡。完成條件見該節點。
1. **盤現況**。正本:`nodes/S1-survey.md`。入口摘要:讀白名單條列事實含受影響面,認可後即已核事實。完成條件見該節點。
2. **真實世界互動盤點**。正本:`nodes/S2-world.md`。入口摘要:五份記錄(Actors / Current Journey / Workarounds / Exceptions / Evidence),無證據標 `[Assumption]`。完成條件見該節點。
3. **逐題逼問**(循環)。正本:`nodes/N3-probe.md`。入口摘要:一次只問一題、
   覆述推理鏈、清單外斷言必問;3a 核銷五份時同步改現況圖;其餘子條款見該節點。完成條件見該節點。
4. **驗收雛形**。正本:`nodes/S4-accept.md`。入口摘要:Goal 翻成假設…當…則…並問出怎麼看到。完成條件見該節點。
5. **發散推演**。正本:`nodes/S5-diverge.md`。入口摘要:至少一輪 what-if,結果記入 Interview Log。完成條件見該節點。
6. **盲點掃描**。正本:`nodes/S6-blind.md`。入口摘要:unknown unknowns 與隱含預設兩份清單都要回應。完成條件見該節點。
7. **落檔 md**。正本:`nodes/N9-write-md.md`。寫 `1-discussion.md`(骨架見下);
   現況圖從 Actors＋Current Journey 長出來,不准另發明天系統流卻叫現況圖;
   重跑覆寫同一檔,不另存。完成條件見該節點。
8. **獨立複核**。正本:`nodes/S8-review.md`。入口摘要:換嚴格審視者視角七掃,再加第 ⑧ 掃「圖 vs Journey」。完成條件見該節點。
9. **詞彙對帳**。正本:`nodes/S9-terms.md`。入口摘要:先查長期記憶現況,再登記候選。
   `dev-memory.py talk propose $MEMORY_SESSION_ID`;使用者確認才
   `dev-memory.py talk confirm <candidate>`;否定走
   `dev-memory.py talk reject <candidate>`;推翻先前理解走
   `dev-memory.py talk correct $MEMORY_SESSION_ID --kind domain --key <詞>
   --title "<新理解>" --reason "<為什麼改>"`。**未確認的候選一律不寫進長期記憶**。完成條件見該節點。
10. **產 html**。正本:`nodes/S10-html.md`。入口摘要:Open Questions 僅三態;跑 `scripts/build-scan-html.py --action` 從 md 生成掃頁六件,不准手寫 html;#scan-now 只從 md 現況圖重生。完成條件見該節點。
11. **過目與收尾**。正本:`nodes/N13-end.md`。html 過目後,使用者點頭才
    跑 `dev-memory.py talk end $MEMORY_SESSION_ID`。它回 `promoted: 0` 是合法結果。完成條件見該節點。

## 產出骨架(1-discussion.md,十節)

> 精簡原則:每節只寫「下一個讀者需要的最少資訊」,夠用就停;禁重複貼上下文、
> 禁湊字數;寫完自問「能砍一半嗎?」能砍就砍(結論、推理鏈、事實、受影響面與
> 真實世界證據不可砍)。

```markdown
---
feature: <slug>  stage: 1-discussion  status: draft→approved  owner:  updated:
---
# 1. 討論 — <標題>
## Problem            ← 誰、什麼痛、現在怎麼繞
## Context(已知事實) ← 步 1 已核事實 + 查證,含程式碼引用與受影響面清單
## Real-world Context ← 步 2 五份子節,無證據敘述就地標 [Assumption]
### Actors            ← 表:Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具
### Current Journey   ← 表:Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點
### Workarounds       ← 實際怎麼完成;哪些步驟沒留紀錄
### Exceptions        ← 跳過標準做法 / 資料不全 / 對方不回 / 中斷恢復 / 重複改派
### Evidence          ← 逐條證據來源;[Assumption] 集中或就地標注
## Goals
## Non-Goals
## Open Questions     ← 三態 [x]/[~]/[>]
## Constraints
## 驗收雛形           ← 每條:假設…當…則…(不綁做法)
                        + 觀測:從哪看 | 看到什麼算對 | 拿什麼資料試
## 邏輯圖(ASCII)     ← 限半形 | - + > < = [ ];中文只放行首標籤/行尾註
## Interview Log      ← 每條:Q → 事實依據 → 推理 → 結論;含發散段與盲點戰果;
                        高影響決策(難逆轉/意外/真權衡)標 ⚠️
```

## 視覺版(html)
html 是掃頁臉,不是把 md 十節整份倒進去。md 仍是正本、十節骨架不准刪。
六件由上而下,不多不少:
1. 摘要卡:痛 + 現在怎麼繞 + Open Questions 三態 badge(已解／假設／移交)
2. 直式現況圖:誰／做什麼／工具／痛點,直式三框(每框四行)。有人、分支、痛點用 inline SVG。直式,不要橫排。禁 mermaid、禁外連圖、禁外部庫。md 留 ASCII。
3. 人與土法:誰／要什麼／缺什麼(從 Actors + Workarounds 收)。`[Assumption]` 看得見。
4. 題目:每列一題 + 著落(已解／假設／移交)。不要長 claim。
5. 驗收一小表:假設…當…則…｜從哪看｜看到什麼。
6. 問答摘要預設摺著(`<details>`)。Constraints／詞條不要佔第一屏。
SVG 用既有圖表 class:.b .hl .no .flow .cap,顏色只用 CSS 變數(含 --acc)。字 11px。現況圖不裁字;三步時 viewBox="0 0 200 420",外層 width:220px 置中,圖下小字「痛在最後一步」,最後一框用痛的強調色。
