---
feature: host-stack-fit
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-09
baseline: v3.22.1 / dc9f099
contract: 2.0.0
---

# 1. 討論 — 主機執法貼近與堆疊盤點

> 基準:`main` 發版線 `v3.22.1`;本回寫核對 tip `dc9f099`(#150 後)。首稿已合入 `#148` @ `d020913`。契約維持 `2.0.0`。本檔是 Stage 1 討論,不做決定、不改 hooks/skills、不升 plugin。
> 本場是 Cursor Cloud Agent 依 owner 書面 brief 落檔,不是現場一問一答;未核的敘述標 `[Assumption]`。2026-09-09 補寫 H1 遵從實驗、I 軸 lean、Q12 cache 核對與 Q13 schema／深度 lean(lean ≠ Decision)。

## Problem
誰:在 Cursor Agent / Grok Bot(以及讀同一棵 `skills/` 的其他非 Claude 主機)上跑 dev-flow 的開工 agent,與要審方法論母版／產品專案的 owner。
痛:同一棵技能樹讀得到,但 Claude `hooks/hooks.json` 的 PreToolUse 不會跑;gate／graph／`devflow-exec` 是共用腳本卻要人手跑。`devflow-exec start` 之後看起來像已武裝,主機其實沒有 Claude 那層擋,形成假安全感與靜默漂移。第二痛:1→7 整條走完才發現語言／runtime／套件 API 不對(母版自己踩過 Python 地板 vs render 套件)。
現在怎麼繞:人記得就手動跑 `--probe`／`--action`;撞 SyntaxError 或套件載入失敗再回頭查 `docs/PLUGIN.md`;Grok 看起來舊就去 Refresh Cursor 快取。

## Context(已知事實)
- 本討論基準 plugin `3.22.1`、契約 `2.0.0`:.claude-plugin/plugin.json:L3 hooks/runtime-capabilities.json:L2-L4
- guide `#host` 已寫:Cursor／Grok／Codex 沒有 Claude PreToolUse,也沒有 haiku–sonnet–opus dispatch-guard;誰開工誰先跑該站 `--action`;不准為別的主機改鬆 `--action`:guides/guide-dev-flow.html:L2837-L2844
- `start` 把 baseline/scope 寫進 `.devflow/exec.json` 之後,PreToolUse 才有米可炊;沒有 PreToolUse 的主機,這段生命週期因果接不上:guides/guide-dev-flow.html:L1559-L1567
- 一份方法包、三邊薄殼;Grok 沒有獨立 marketplace,吃 Cursor 帳裝好的 `plugins/cache/dev-flow/...`;hooks 規則只在 Claude Code 生效,Cursor／Codex 薄殼不掛 hooks、沒有機械擋寫入;編譯下限 3.9,產圖 `markdown-it-py==4.0.0` 要 Python 3.12+:docs/PLUGIN.md:L5 docs/PLUGIN.md:L59-L64
- host-adapter 第一刀就是因為非 Claude 沒有 AskUserQuestion／enabledPlugins／PreToolUse;探針只驗 `DEVFLOW_ROOT` + 本機技能樹,不是第 2–7 站 `--action`,不准拿它改鬆圍欄:scripts/check-host-adapter.sh:L7-L12 scripts/check-host-adapter.sh:L21-L29
- 三邊共同 runtime 是 `--action` + `devflow-lib.py`;Edit/Write 在 Claude 走 PreToolUse 當場擋,Bash 舊路是先寫再 postbash:scripts/check-write-scope.sh:L4-L8
- Python 地板 3.9 只保語法層,不驗第三方相依在地板版裝不裝得起來;#122 拍板修法 1,render 執行地板另見:scripts/check-py-floor.sh:L13-L18
- 母版 render 釘死 `markdown-it-py==4.0.0`:scripts/requirements-methodology-render.txt:L1
- Stage 1 S1 盤現況:消化 brief、白名單事實、每條帶 `path:L`;沒有「語言／runtime／每個套件版本」這一步:skills/dev-talk/nodes/S1-survey.md:L21-L32
- Stage 1 填 Context + Interview Log,Decision／OC／ADR 不進本 hop:notes/design/stage1-context-chain.md:L21-L35
- Active 空;Backlog 仍寫:完整 normal-risk full lane 觀測跑完前,不動 Stage 1–4 模板內容:docs/dev/STATUS.md:L49
- Claude 端 `hooks.json` 確有 PreToolUse(Edit|Write|Read → devflow-guard):hooks/hooks.json:L3-L10
- Cursor 薄殼只有 `skills: "./skills/"`,沒有 hooks 鍵:.cursor-plugin/plugin.json:L16
- Context 出處語法只有 `path:L起` 或 `path:L起-L迄`:_templates/1-discussion.md:L36-L39
- 探針兩種用途不可混;三邊都沒有 Claude PreToolUse;誰開工誰先跑 `--action`:skills/dev-setup/SKILL.md:L43-L54

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 開工 agent | 把 feature 做完且看起來守流程 | 讀 `skills/`;寫產品樹;不能觸發 Claude PreToolUse | 技能正文、graph、可選跑腳本 | 本主機這次有沒有真的執法;語言／套件地板 | SKILL.md、exec.sh、編輯器 |
| owner | Cursor／Grok dogfood 貼近 Claude,但不造假 hook | 批 G1、改方法論、Refresh 市集 | 主機差異已寫在 `#host` | 選哪條牙;盤點住哪;「每個套件」多深 | GitHub、PR |
| 採用者 | agent 不要用錯語法／錯 API 寫完一條 lane | 本機直譯器與 lockfile | 自己機器上的 python／venv | agent 開場有沒有讀過版本 | 終端機、套件管理員 |

### Current Journey
(無此功能時;正式 SOP=`#host`「誰開工誰先跑 `--action`」;實際常跳過。兩者都記。)
| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 開工 agent | 讀 skills | SKILL.md | — | 無 | 以為已武裝 |
| 2 | 開工 agent | 跑 start | exec.sh | — | exec.json | 無 PreToolUse |
| 3 | 開工 agent | 寫到收尾 | 編輯器 | — | 程式碼 | 晚撞版本 |

正式 SOP(guide `#host` + dev-setup):開工先 `--probe`(帶專案根),再該站 `--action`。實際做法:`[Assumption]` 多數 Cursor／Grok session 只讀技能、偶爾 `devflow-exec start`,不跑 `--action`,也沒有開場堆疊盤點。

### Workarounds
- 人記得就手動跑 `check-host-adapter.sh --probe` 與 `check-devtalk-graph.sh --action`／`check-devstageN-graph.sh --action`。
- 撞 SyntaxError 或 `markdown-it-py` 載入失敗,再回頭讀 `docs/PLUGIN.md` 地板段。
- Grok 行為像舊版 → Dashboard Refresh 已匯入的 rick546986/dev-flow 那一列。
- Step 1–3 若沒跑 `--action`,系統不留「本主機未執法」紀錄;看起來與 Claude 武裝 session 相同。

### Exceptions
- Claude Code: `start` 之後 PreToolUse 真的會擋;同一套 `exec.json` 在 Cursor／Grok 只是檔案。
- fast lane 省略 Stage 1–3:若盤點只掛在 Stage 1,這條 lane 仍會漏。
- 方法包自檢 `--probe`(無專案根)與採用專案探測(帶樹)混用 → 曾出現空樹假綠(#78,已關)。
- agent 可以整段跳過 probe／`--action`,沒有主機層攔截。
- 本 feature 若要改 Stage 1 模板,撞上 STATUS「觀測前不動 Stage 1–4 模板」凍結。

### Evidence
- owner 書面 brief(本 session 2026-09-09):主機執法缺口 + 必須有語言／版本／每個套件版本的早期盤點;禁假 PreToolUse;禁第二套方法論;契約 2.0.0;本 PR 只討論。
- 已核文件:上列 Context 出處(本 working tree 讀過)。
- 已關 issue/PR:https://github.com/rick546986/dev-flow/issues/122 、https://github.com/rick546986/dev-flow/pull/128 、https://github.com/rick546986/dev-flow/issues/129 、https://github.com/rick546986/dev-flow/issues/78
- 2026-09-09 核 cache 落後(Q12):GitHub tip `dc9f099`(合入 #150 後);發版線 v3.22.1。Grok Bot box `plugins/cache/dev-flow/...` 仍 **3.6.1**(本場讀到 hash `aaf68c12a6cec6dbf96ad256bb106dc43f47f3a3`)。Mac Cursor plugin cache 同 hash／**3.6.1**。Claude 快取最高 **3.22.0**;該側本機 checkout 約 `v3.22.0`。對齊 plugin cache **不是每條 feature** 必做;發版時、或行為看起來舊了再做。
- owner lean 2026-09-09(Q13):方法論母版與產品專案 **同一 schema／同一深度**(內容各填;欄位形狀共用;深度 = 宣告 pin + 直接相依)。owner 說一致比較好。lean ≠ Decision。
- `[Assumption]` Cursor／Grok 現場「常」跳過 `--action`:從「沒有 PreToolUse + 共同 runtime 是手動 `--action`」推出,無採用專案 log。
- `[Assumption]` 「整條 1→7 走完才發現版本」是重複痛,不是單次:#122 是母版實例,產品專案頻率未量。
- `#scan-people` 缺什麼只吃 Actors 欄;`parse_people` 不再附加 Evidence Assumption(https://github.com/rick546986/dev-flow/issues/151)。

#### H1 遵從實驗（2026-09-09）

lab harness 在 `/workspace/h1-exp`(Grok Bot 場;不在本 repo working tree)。Cursor = CloudAgent。判定口徑:valid script-minted receipt + DONE(適用時)。本 hop 只記事實,不寫 Decision／OC／ADR。

樣本與遵從(valid script-minted receipt + DONE where applicable):
- Condition A (short soft reminder in prompt):**10/10**(Grok executor)
- Condition B (markdown checklist):**9/10**(B08 noop)
- Condition C (script receipt + verify):**9/10** receipts(C08 empty;some missing DONE)
- Long A (LA, soft rule in long chore brief):**10/10**(Grok executor)
- Diluted A (DA, soft rule buried in long HOST_GUIDE;chores do not spell mint steps):**10/10**(Grok executor)
- Cursor CloudAgent long A (LAC01–10, soft rule + shell snippet explicit in brief):**10/10**

DA caveats(必須記錄 — 削弱「野外只靠軟提醒就夠」):
- brief still required reading of long guide
- report line asked `ran_stage_check=yes|no`(name leak)
- env hints `H1_EXP_ROOT` / `H1_TRIAL_ID`
- not wild diluted product SOP

## Goals
- G1 主機誠實:Cursor／Grok／Codex 開工時,人與 agent 都看得到「本主機沒有 PreToolUse;共同 runtime 是 `--action` + check 腳本」,且不會把 `devflow-exec start` 誤讀成 Claude 同級執法。
- G2 有牙或等價:只靠軟提醒不夠時,要有可觀測的缺口(紀錄或檢查紅),不是假 hook。
- G3 早期堆疊:讀產品專案或方法論母版時,有明確早期步驟寫下語言、語言／runtime 版本、每個套件版本,讓地板／API 落差在進完整 lane 之前就落檔。
- G4 單一方法論:只延伸 Stage 1／talk／setup 既有面,不另造第二套流程。

## Non-Goals(初稿)
- 不在 Cursor／Grok／Codex 發明或模擬 Claude PreToolUse。
- 不另寫第二套方法論、不改鬆既有 `--action` 圍欄。
- 本討論 PR 不改 hooks／skills 正文、不 bump plugin、不改契約 2.0.0。
- 不把新 lockfile 當套件真相、取代專案既有 lock／pin。
- 不在本 hop 選定 H1/H2/H3 或 I1–I4(留給收斂)。
- 不把 Grok marketplace、主機 SKU 表、或 haiku–sonnet–opus dispatch-guard 搬到非 Claude 主機。

## 候選方向(未定案)

本節是討論原料,不是 Decision。Stage 2 才並排壓測。

### 主機貼近
| ID | 方向 | 做什麼 | 利 | 害 |
|---|---|---|---|---|
| H1 | 強制清單 + 牙 | 非 Claude 開工必須留下「已跑該站 `--action`／probe」紀錄;缺則紅或不得宣稱武裝 | 假安全感有對向牙;對準既有共同 runtime | 要定義紀錄形狀與誰執行;可能碰 graph／setup 文字 |
| H2 | 只加硬文件 | 加厚 `#host`／SKILL／N-handoff 的「你沒有 PreToolUse」句 | 最小;不動牙 | 現況 `#host` 已寫過,痛仍在;軟提醒救不了跳過的人 |
| H3 | 擴大 host-adapter probe | probe 除掛載外,印／查「本主機執法食譜」或「本次 session 是否跑過 `--action`」 | 探針已是開工入口;延續 #78 修法 | probe 檔頭已寫「不是 `--action`」; overload 一刀容易再假綠 |

實驗 lean → H1+C形 receipt；非定案。2026-09-09 遵從實驗(見 Evidence)讓討論**偏向** H1,牙形偏條件 C 的 script-minted receipt、fail-closed;A／LA／DA／LAC 高分不改成「只靠軟提醒」,也不把 H2／H3 升成主牙。本節不是 Decision。

### 堆疊盤點
| ID | 方向 | 落點 | 利 | 害 |
|---|---|---|---|---|
| I1 | Stage 1 N 節／S1-survey | Context 或指定小節 | 最早;4-spec 吃得到 | 改 Stage 1 模板／節點,撞 STATUS 凍結;fast lane 無 Stage 1 |
| I2 | `dev-setup` | 安裝／check 寫一份 | 專案級、一次寫多人讀 | setup 不是每條 feature 重跑;`git pull` 後套件漂移 |
| I3 | `STATUS.md` 一節 | Active 旁邊 | 人本來就看 STATUS | 母版 STATUS 禁 feature branch 手改;採用專案也不是每 feature 重寫 |
| I4 | 新 `0-stack.md` 或 lockfile digest | `docs/dev/<slug>/` 或專案根機器可讀摘要 | 與討論檔分離;可對 lock 做 digest | 多一個產物;digest 不是 lock 正本 |

owner lean 2026-09-09 → I2+I4; not I1/I3。I2 當底(專案級、跟 setup 走)、I4 選配(要機器可讀摘要時才加)。I1 要先解凍 Q11 且漏 fast lane,不取;I3 撞 STATUS 寫入窗,不取。方法包 vs 產品專案:同一 schema／同一深度(內容各填;欄位形狀共用;深度 = 宣告 pin + 直接相依)。本節不是 Decision。

組合包 lean(非定案):主機 **H1 fail-closed script receipt(C)** + 堆疊 **I2+I4**。

### 已拒(本討論可寫死,不是方案)
| 已拒 | 理由 |
|---|---|
| 假 PreToolUse／把 `hooks.json` 抄進 Cursor 當會跑 | owner 禁;Cursor 薄殼無 hooks 鍵;guide 禁假裝 |
| 第二套方法論 | owner 禁;host-adapter 也不重寫 1–7 |
| 改鬆 `--action` 遷就無 hook 主機 | `#host` 與 host-adapter 第三刀已釘死 |
| 等 Stage 6／7 才發現版本 | owner 要早期寫下;母版 #122 已證明晚發現成本高 |
| 另造 lockfile 當套件正本 | 與 pip／npm lock 雙源;會漂 |

## Open Questions
- [x] Q1:可不可以發明 Cursor／Grok 的假 PreToolUse?→ 不可(owner + `#host`)
- [x] Q2:可不可以另造第二套方法論?→ 不可;只延伸 Stage 1／talk／setup
- [x] Q3:契約與本 PR 版本?→ 契約 2.0.0;本 PR 不升 plugin
- [x] Q4:堆疊盤點是不是必須納入?→ 必須(owner)
- [~] Q5:slug 用 `host-stack-fit`?→ 暫定;Q10 軟 lean 維持此名(H1+I2/I4 同場)。更短候選 `early-stack` 只蓋盤點,本 lean 不取。
- [~] Q6:主機貼近選 H1、H2 還是 H3?→ 帶假設 lean **H1**(實驗 2026-09-09:A／LA／DA／LAC 高分 ≠ 取代牙;H2 重疊既有 `#host`;H3 有 probe≠action 假綠風險)。非定案。
- [~] Q7:堆疊盤點選 I1、I2、I3、I4,或組合?→ 帶假設 lean **I2 base + I4 optional**。不取 I1(要先解凍 Q11 且漏 fast lane)、不取 I3(STATUS 寫入窗)。非定案。
- [~] Q8:「每個套件的版本」= 宣告 pin、lock 全樹(含 transitive)、還是本次會碰到的直接相依?機器可讀 digest 要不要?→ 帶假設 lean **declared pins + direct deps this work touches**;v1 不做 full transitive lock tree。I4 digest 選配。非定案。
- [~] Q9:主機牙要 fail-closed(沒跑 `--action` 就紅)還是 warning-only?→ 帶假設 lean **fail-closed**;牙形 = **script-minted receipt**(條件 C),不是手填 checklist(B 可偽造)。非定案。
- [~] Q10:主機貼近與堆疊盤點要不要拆成兩個 slug?→ 帶假設 lean 維持**一個 slug** `host-stack-fit`(主機 H1 + 堆疊 I2/I4 同場);除非 owner 之後要拆。軟 lean。
- [~] Q11:本 feature 是否解除「完整 full lane 觀測前不動 Stage 1–4 模板」?若否,I1 出局。→ 帶假設:本 lean 不需要 I1,凍結可先留;I1 延後。非定案。
- [x] Q12:Grok／box cache 落後 tip 是否仍是現況?→ CONFIRMED 仍落後。2026-09-09:tip `dc9f099`(#150 後);發版線 v3.22.1;Grok Bot／Mac Cursor plugin cache 同 hash 仍 3.6.1;Claude 快取至 3.22.0、該側 checkout 約 v3.22.0。對齊 cache 不是每 feature;發版或行為舊了再做。
- [~] Q13:產品專案與方法論母版是否同一份 artifact、同一套深度?→ 帶假設 lean **同一 schema／同一深度**(內容各填;欄位形狀共用;深度 = 宣告 pin + 直接相依)。owner:一致比較好。非定案。

## Constraints
- 契約維持 2.0.0;本討論不 bump `.claude-plugin/plugin.json`。
- 不准為別的主機改鬆 `--action`。
- 不准重寫 1–7 編成。
- feature branch 不改 `docs/dev/STATUS.md` 表列。
- 人看討論用繁中;ID／R／S／T 維持英式。
- 實作若動 Stage 1–4 模板,須先過 Q11。

## 驗收雛形
- AC-1(G1):假設 agent 在 Cursor 或 Grok 開工,當它宣稱「已武裝／可寫碼」,則人能在本次產出裡看到「本主機沒有 PreToolUse、共同 runtime 是 `--action`」,且能指出本次有沒有真的跑過該站檢查。
  - 從哪看:`docs/dev/<slug>/` 開場紀錄,或 owner 指定的 setup／probe 輸出
  - 看到什麼算對:出現「無 PreToolUse」與「`--action`」字樣;有／無本次檢查輸出可分辨,不是只看到 `exec start` 成功
  - 拿什麼試:本母版在 Cursor Cloud Agent session 開一個 draft slug(本檔即樣張)
- AC-2(G2):假設有人只跑 `devflow-exec start`、沒跑該站 `--action`,當流程走到可寫碼的點,則不會只靠「start 過了」就被當成與 Claude 同級執法。
  - 從哪看:同一點的紀錄或檢查出口
  - 看到什麼算對:缺口可見(紅、或明確「未跑 `--action`」);沒有「已與 Claude 同等武裝」的句子
  - 拿什麼試:Cursor 樹上 `start` 但不跑 `--action`(throwaway;本討論不實作)
- AC-3(G3):假設專案宣告語言地板與套件 pin,當 owner 指定的早期步驟做完,則落點寫出語言、runtime 版本、每個套件版本。
  - 從哪看:Q7 選定的落點(1-discussion／setup 產出／STATUS／`0-stack.md` 等)
  - 看到什麼算對:至少含語言名、runtime 版本、套件名+版本;母版樣張能對上 Python 3.9 地板與 `markdown-it-py==4.0.0`
  - 拿什麼試:本 repo `docs/PLUGIN.md` + `scripts/requirements-methodology-render.txt`
- AC-4(G3):假設本機直譯器是 3.9、某套件要 3.12,當盤點做完,則這段落差在進後段 lane 之前就寫在檔上。
  - 從哪看:同上落點的「落差」列
  - 看到什麼算對:同時出現本機 3.9 與套件 3.12+ 需求,不是等 render 爆才補
  - 拿什麼試:母版 #122 情節(3.9 地板 vs `markdown-it-py==4.0.0`)
- AC-5(Non-Goal):假設在 Cursor 寫檔,當工具執行 Write,則系統不假裝有 Claude PreToolUse 攔截。
  - 從哪看:Cursor session 工具軌跡;`.cursor-plugin/plugin.json`
  - 看到什麼算對:沒有新的假 PreToolUse 掛載;薄殼仍無 hooks 鍵
  - 拿什麼試:本 repo `.cursor-plugin/plugin.json`

## 現況圖
```
開工 agent
讀 skills
SKILL.md
以為已武裝
↓
開工 agent
跑 start
exec.sh
無 PreToolUse
↓
開工 agent
寫到收尾
編輯器
晚撞版本
```

## 邏輯圖(ASCII)
```
now
|-- host: read skills, no PreToolUse
|   |-- H1 teeth + checklist
|   |-- H2 docs only
|   |-- H3 expand probe
|   +-- X fake PreToolUse   [reject]
|-- stack: no early inventory
|   |-- I1 Stage1 S1
|   |-- I2 dev-setup
|   |-- I3 STATUS
|   |-- I4 0-stack / digest
|   +-- X wait until 6-7    [reject]
+-- later: pick one host + one stack (not this file)
```

## Interview Log(推理鏈外顯)
- Q:Cursor／Grok 讀得到 skills,為什麼還是沒有 Claude 那層擋?
  - 事實:guides/guide-dev-flow.html:L2837-L2844 hooks/hooks.json:L3-L10 .cursor-plugin/plugin.json:L16 docs/PLUGIN.md:L59-L64
  - 推理:PreToolUse 掛在 Claude `hooks.json`;Cursor 薄殼只有 skills 鍵;PLUGIN 明寫 hooks 只在 Claude 生效。讀同一棵樹 ≠ 跑同一套生命週期。
  - 結論:CONFIRMED 共同 runtime 是手動 `--action`,不是假 hook。
- ⚠️ Q:`devflow-exec start` 之後,非 Claude 主機是否已經武裝?
  - 事實:guides/guide-dev-flow.html:L1559-L1567 scripts/check-write-scope.sh:L4-L8
  - 推理:`start` 寫 `exec.json` 是給 PreToolUse 當米。沒有 PreToolUse,檔在也不會擋 Write。把 start 成功當成 Claude 同級執法,就是假安全感。
  - 結論:CONFIRMED start ≠ 非 Claude 執法;H1／H2／H3 都要處理這層誤讀。
- Q:現有 `--probe` 能不能當「這次已執法」的證明?
  - 事實:scripts/check-host-adapter.sh:L21-L29 skills/dev-setup/SKILL.md:L43-L54
  - 推理:probe 只驗 ROOT + 技能樹;檔頭禁止把它當 `--action`。#78 已證空樹假綠。用 probe 冒充執法會重演第四型假綠。
  - 結論:CONFIRMED probe ≠ session 執法證據;H3 若做只能加輸出,不能讓 probe 變綠就等於 `--action`。
- Q:為什麼要在早期寫語言、runtime、每個套件版本?
  - 事實:scripts/check-py-floor.sh:L13-L18 scripts/requirements-methodology-render.txt:L1 docs/PLUGIN.md:L59-L64
  - 推理:母版已分開「3.9 語法地板」與「3.12+／markdown-it-py 4.0.0 執行地板」。#122 是整組檢查都綠、採用者本機才爆。沒有開場盤點,S1 只收 brief／白名單事實,不會自動寫套件表。
  - 結論:CONFIRMED 堆疊盤點是新缺口,不是 `#host` 已做完的事。
- Q:S1-survey 現在會不會盤語言與套件?
  - 事實:skills/dev-talk/nodes/S1-survey.md:L21-L32 _templates/1-discussion.md:L36-L39
  - 推理:S1 要的是帶出處的已核事實,沒有語言／lockfile 步驟。加 I1 等於改 Stage 1 節點／模板。
  - 結論:CONFIRMED 現況沒有堆疊盤點;I1 會動 Stage 1 文字。
- ⚠️ Q:軟提醒夠不夠當 Cursor／Grok 主機牙?實驗 lean 哪條?
  - 事實:notes/design/stage1-context-chain.md:L21-L35 guides/guide-dev-flow.html:L2837-L2844 scripts/check-host-adapter.sh:L21-L29
  - 推理:2026-09-09 H1 實驗(Evidence):A 10/10、B 9/10(B08 noop)、C 9/10 receipts(C08 empty;some missing DONE)、LA 10/10、DA 10/10、LAC01–10 10/10。軟提醒可見時遵從高,但不取代牙。H2 重疊既有 `#host`。H3 有 probe≠action 假綠風險。B 手填 checklist 可偽造;無 PreToolUse 主機牙應是 fail-closed script-minted receipt(條件 C)。DA caveat(brief 仍要讀長 guide;report 問 ran_stage_check=yes|no name leak;env hints H1_EXP_ROOT／H1_TRIAL_ID;not wild diluted product SOP)削弱「野外只靠軟提醒」。I 軸 owner lean 見下一條。Stage 1 不准做 Decision。
  - 結論:OPEN 實驗 lean H1 + fail-closed script-minted receipt;軟提醒可見時有效,主牙仍要 C 形收據。非定案。
- ⚠️ Q:盤點該住 Stage 1、setup、STATUS,還是新檔?深度先寫到哪?
  - 事實:docs/dev/STATUS.md:L49 skills/dev-talk/nodes/S1-survey.md:L21-L32
  - 推理:owner 2026-09-09 收下 I2 為底、I4 選配。I1 要先解凍 Q11 且漏 fast,不取。I3 撞 STATUS 寫入窗,不取。深度 v1 = 宣告 pin + 本次碰到的直接相依,不是 lock 全樹。Q13 lean:方法包與產品專案同一 schema／同一深度(內容各填;欄位形狀共用)。Q11 凍結可先留,I1 延後。Q10 軟 lean 單一 slug `host-stack-fit`(H1+I2/I4 同場)。組合包 lean:H1 fail-closed script receipt(C)+I2+I4。Stage 1 不准做 Decision。
  - 結論:OPEN owner lean I2 base + I4 optional;同一 schema／同一深度(宣告 pin + 直接相依)。非定案。
- ⚠️ Q:假 hook、第二方法論、拆 slug、cache 落後,哪些已死、哪些還能翻?
  - 事實:docs/PLUGIN.md:L5 docs/PLUGIN.md:L59-L64 notes/design/stage1-context-chain.md:L21-L35 .claude-plugin/plugin.json:L3
  - 推理:假 PreToolUse 與第二方法論與 brief／`#host` 衝突,本討論標已拒。Q10 軟 lean 不拆 slug。2026-09-09 核對:GitHub tip `dc9f099`(#150 後);發版線 v3.22.1。Grok Bot box `plugins/cache/dev-flow/...` 仍 3.6.1(hash `aaf68c12a6cec6dbf96ad256bb106dc43f47f3a3`)。Mac Cursor plugin cache 同 hash／3.6.1。Claude 快取最高 3.22.0;該側本機 checkout 約 v3.22.0。對齊 plugin cache 不是每條 feature;發版時或行為看起來舊了再做。
  - 結論:CONFIRMED cache 仍落後 tip;拆 slug 除非 owner 之後要拆;已拒項不進方案表。
