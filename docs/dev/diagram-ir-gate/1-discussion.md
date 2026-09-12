---
feature: diagram-ir-gate
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-12
---

# 1. 討論 — 圖表 IR 閘（Archify absorb wave-1）

> 用途:發散。**不做決定**。本場依 owner 2026-09-12 書面 brief 落檔,不是現場一問一答。
> Lane = **full**。本 hop **只 Stage 1、不送 G1**。未核敘述標 `[Assumption]`。
> 第一刀**不是動畫**;預設圖維持**靜態直式 SVG**。基準:`main` tip `67481d6`(v3.23.3)。

## Problem
誰:寫／重生審頁與指南圖的開工 agent,以及要審「這張圖是不是對的家族、會不會蓋掉上一張好圖」的 owner／reviewer。
痛:DevFlow 已有 vbox-fig／gate-twin／dir-tree 契約與 Python SVG 產器,但沒有 Archify 式機器可讀 IR 驗證收據、圖種路由表、與對齊 selftest 的 Proof Lab 樣張。agent 會把 Stage 1 三框、方案架構、行為流、目錄樹、模組生命週期混進同一支 API;壞 html 仍可 `write_text` 蓋掉上一張可讀產出(#191 方向:禁靜默壞圖)。
現在怎麼繞:人靠契約「何時不用」表口頭分流;產器各自 fixture／牙綠了就算過;壞了就重跑或手改 md 再重生。沒有 IR 收據,也沒有「壞產出不得取代 last-good」。

## Context(已知事實)
- 本討論基準 plugin `3.23.3`:.claude-plugin/plugin.json:L3
- 直式方塊家族正本是 `vbox-fig-contract`;產器 `build-vbox-fig.py`、牙 `check-vbox-fig.sh`;gate-twin 行為流／方案架構 ASCII→SVG 收口在 `devflow_twin_ui.py`:notes/design/vbox-fig-contract.md:L1-L7
- vbox-fig 準用:步驟由上而下、一格一步;第 2 站方案架構、第 4 站模組生命週期走這份,不要每站手抄:notes/design/vbox-fig-contract.md:L9-L12
- vbox-fig 鎖死直式 SVG,不是 mermaid、不是橫 ASCII、不是把 `<pre>` 當預設圖;樹狀後備 `<pre>` 必須帶 WARNING:notes/design/vbox-fig-contract.md:L32-L39
- 模組生命週期四格固定:新生 → 改行為 → 退役 → 不動;不准發明第五格:notes/design/vbox-fig-contract.md:L56-L65
- vbox-fig 何時不用:第 1 站 `#scan-now`、審頁三框、七站三走廊、G1/G2/G3 審查介面各走別條:notes/design/vbox-fig-contract.md:L79-L86
- 目錄樹家族正本 `dir-tree-contract`;產器 `build-dir-tree.py`、牙 `check-dir-tree.sh`;與 vbox-fig、第 1 站三框、七站三走廊不是同一支 API:notes/design/dir-tree-contract.md:L1-L5
- dir-tree 吃手寫 YAML,不准掃 repo 猜 why:notes/design/dir-tree-contract.md:L39-L40
- 產品輸出 `docs/dev/<slug>/dir-tree.html`;不要跟 1-discussion 掃頁三框搶槽:notes/design/dir-tree-contract.md:L61-L64
- 第 1 站審頁三框是另一套,不併進 vbox-fig;產檔器 `build-stage1-html.py`,牙 `check-stage1-now-contract.sh`;不准手包 html-shell、不准改掃頁產生器充審頁:notes/design/stage1-review-ui-contract.md:L1-L8 notes/design/stage1-review-ui-contract.md:L21-L30
- 第 1 站審頁何時不用:掃頁六件走 `build-scan-html.py`;直式步驟方塊走 vbox-fig;G1/G2/G3 走 gate-twin:notes/design/stage1-review-ui-contract.md:L32-L39
- 全站畫法總冊:看圖零依賴,全部圖都是靜態 inline SVG;禁 mermaid／外部庫／外部圖檔:_templates/diagram-style.md:L5-L7 _templates/diagram-style.md:L9-L12
- Stage 1 模板頂註指定審頁走 `build-stage1-html.py --action`,不要手包 html-shell:_templates/1-discussion.md:L14-L20
- `build-vbox-fig.py` 吃 JSON 步驟列、吐 stdout SVG;不合法 exit 1、用法錯 exit 2;沒有寫檔、沒有 last-good:scripts/build-vbox-fig.py:L1-L17 scripts/build-vbox-fig.py:L183
- vbox-fig `normalize` 會擋空步驟、錯 kind、空標題、lines 不是一到三行:scripts/build-vbox-fig.py:L91-L114
- `build-dir-tree.py` 用 `Path.write_text` 直接覆寫指南或 `--out`:scripts/build-dir-tree.py:L574-L576 scripts/build-dir-tree.py:L654
- `build-gate-twin.py` 用 `out_local.write_text(...)` 直接覆寫 `docs/dev/<slug>/<stage>.html`:scripts/build-gate-twin.py:L2327
- `build-stage1-html.py` 同樣 `dest.write_text(html_out)`:scripts/build-stage1-html.py:L479-L482
- 他處已有 `atomic_write`(tmp + `os.replace`),圖表產器沒有沿用:scripts/write-stack-inventory.py:L30-L37
- gate-twin 樹狀 ASCII 改 WARNING + `<pre>` 原文,禁單盒硬裁:scripts/devflow_twin_ui.py:L485-L506
- #191 靜默裁字已在 v3.23.2 補牙 `fig-ascii-191`;HISTORY 記的是「禁靜默裁字／樹狀改 pre」,不是 IR 收據或 last-good:docs/dev/HISTORY.md:L488-L491 scripts/check-gate-twin.sh:L92
- 方法論檢查已分開跑 vbox-fig／dir-tree／stage1-now,各咬自己的契約句與 fixture:scripts/devflow-check.sh:L132-L138 scripts/check-vbox-fig.sh:L31 scripts/check-dir-tree.sh:L1-L6
- 現況 fixture 分住 vbox-fig／dir-tree／gate-twin／stage1-html,由各牙點名;本 tree 沒有「Proof Lab」目錄名或 IR 收據格式:scripts/check-vbox-fig.sh:L31 scripts/check-dir-tree.sh:L1-L6 scripts/check-gate-twin.sh:L92
- Stage 1 只填 Context + Interview Log;Decision／OC／ADR 不進本 hop:notes/design/stage1-context-chain.md:L21-L26
- Active 目前是 `integration-before-verdict`;表列只准在 main 走 `status-update.sh`;feature branch 拒改正本:docs/dev/STATUS.md:L10-L26 docs/dev/STATUS.md:L34 scripts/status-update.sh:L408-L415
- Context 出處語法只有 `path:L起` 或 `path:L起-L迄`:_templates/1-discussion.md:L36-L39

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 開工 agent | 給對的家族產出可審圖 | 跑產器、寫 feature 樹 | 各契約「何時用／不用」散文 | 這次該走哪條 API;IR 過了沒 | 編輯器、終端機 |
| 產檔器 | 從 md／JSON／YAML 吐 html／svg | 覆寫目標檔 | 本支輸入形與 exit 碼 | 上一張好產出還能不能留 | 無(系統內) |
| 審查人 | 在對的家族上看可讀圖再批 gate | 開審頁、批 G1–G3 | 契約與牙是否綠 | 這張是不是靜默壞圖蓋過好圖 | 瀏覽器、GitHub |
| owner | wave-1 只收 IR／路由／Proof Lab,不收動畫預設 | 裁 slug／G1、禁假 PASS | 2026-09-12 澄清 | 後續刀的接縫 | GitHub、Archify 公開頁 |

### Current Journey
正式 SOP:各契約「何時用／不用」分流;產器各自 `--fixture`／牙綠才算過。
實際:agent 常就近抄最近看過的產器;牙綠 ≠ 家族對、≠ 沒蓋掉 last-good。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 開工 agent | 混用圖家族,就近抄最近產器 | 三支產器 | — | 錯家族 html／svg | 家族對不上 |
| 2 | 產檔器 | 直接覆寫目標 html | write_text | — | 新檔蓋舊檔 | 壞圖蓋好圖 |
| 3 | 審查人 | 打開審頁看圖 | html twin | owner | 綠牙或可讀/不可讀圖 | 無驗證收據 |

### Workarounds
- 人翻「何時不用」表,口頭告訴 agent 別用 mermaid／別把三框當生命週期。
- #191 類壞圖:改 md 成 `[R-n]` 直式或接受 `<pre>` 後備,再重生。
- 牙綠就當過;沒有機器可讀 IR 收據可附在 PR。
- 壞覆寫發生後,只能 git checkout 舊 html。這些步驟常不留「為何這次該走哪一家族」紀錄。

### Exceptions
- 樹狀 ASCII:gate-twin 顯式 WARNING + `<pre>`,不是常態圖。
- dir-tree 第 1 站可選,不進 gate、不改 hop。
- vbox-fig 吐 stdout,呼叫端才決定寫哪;呼叫端仍可直接蓋檔。
- 誰都可以跳過契約表、硬跑錯產器;沒有主機層攔截。
- `[Assumption]` 採用現場仍常混家族(無採用專案 log;風險=高;期限=Stage 2 對帳,過期擋 G2)。

### Evidence
- owner 書面 brief(本 session 2026-09-12):slug `diagram-ir-gate`;Archify absorb **wave-1 only**;第一刀不是動畫,預設靜態直式 SVG;DO = IR 驗證＋原子交付、圖種路由表、Proof Lab;NON-goals = Mermaid／黑盒自動排版／Node render／hosted share／WYSIWYG、動畫當預設、deep-link／Architecture Delta／themes／Share Card;本 hop 只 Stage 1;不假人 PASS;不動 #196、#200、#201。
- Archify 公開原則(外站,非正式本 repo 契約):https://github.com/tt-a1i/archify `PRODUCT.md` — portable proof、deterministic validation、motion 不得承載靜態幀消失的意義;本討論只吸收「驗證收據／原子交付」方向,不搬 render 堆疊。
- 已核文件:上列 Context 出處(本 working tree 讀過)。
- #191 現象與方向:https://github.com/rick546986/dev-flow/issues/191 ;合入 #193,記在 docs/dev/HISTORY.md:L488-L491
- 開著、本 slug 不動:https://github.com/rick546986/dev-flow/pull/196 https://github.com/rick546986/dev-flow/pull/200 https://github.com/rick546986/dev-flow/pull/201
- `[Assumption]` 採用現場仍混家族:無 log;期限 Stage 2。

## Goals
- G-ir:typed IR → 驗證 → 原子交付;失敗給結構化 fail code + 可修旋鈕;壞產出不得取代 last-good。
- G-route:一張圖種路由表,把 DevFlow 五個家族(Stage1 現況、Stage2 方案架構、行為流、目錄樹、模組生命週期)對到對的契約／產器。
- G-lab:Proof Lab 可重放樣張,至少覆蓋 vbox-fig／gate-twin／dirmap,並對齊現有 selftest／`devflow-check` 牙。

## Requested solution（候選，未定案）
- 吸收 Archify 的「驗證收據 + 原子交付」,掛在既有 Python SVG 產器上;不進口 Archify 的 Node／動畫／hosted 堆疊。
- 路由表當契約(人與 agent 先選家族),不是黑盒自動排版。
- Proof Lab = 可重放樣張 + 與現有牙對齊,不是另造第二套檢查語言。
- 本 hop 不選定 IR schema、fail-code 枚舉、或 fixture 目錄形狀。

## Non-Goals(初稿)
- 不做 Mermaid、黑盒自動排版、Node render 堆疊、hosted share、WYSIWYG。
- 動畫不當預設;可選 trace 是後刀,不是本刀。
- 不做 deep-link `#focus`／`#route`、Architecture Delta、themes、Share Card。
- 本 hop 不實作產器、不寫 Stage 2+、不 bump plugin。
- 不動開著的 #196、#200、#201;不在本 PR 宣稱 G1 PASS。
- 不把第 1 站三框併進 vbox-fig,不改掃頁產生器來充審頁。

## Open Questions
- [x] Q1:第一刀是不是動畫?→ owner 2026-09-12:不是;預設維持靜態直式 SVG
- [x] Q2:要不要整包吸收 Archify(Mermaid／Node／hosted／WYSIWYG／motion-first)?→ 不要;只 wave-1 三條 DO
- [x] Q3:lane 是否 full?→ owner:full
- [x] Q4:本 hop 是否送 G1、是否實作產器?→ owner:只 Stage 1;不送 G1;不實作
- [x] Q5:可否動 #196／#200／#201?→ 不可
- [~] Q6:IR schema 與 fail-code 詞彙本討論是否定死?(帶假設:不定死;Stage 2 命名。wave-1 只要「有結構碼 + 可修旋鈕」。期限=Stage 2,過期擋 G2)
- [~] Q7:Proof Lab 是新目錄還是延伸現有 `scripts/fixtures/*`?(帶假設:對齊現有牙即可;目錄形狀後定。期限=Stage 2)
- [>] Q8:動畫當可選 trace → 移交後刀
- [>] Q9:deep-link／Architecture Delta／themes／Share Card → 移交後刀

## Constraints
- 表列只准 `scripts/status-update.sh` 且必須在 `main`;本 feature branch 不改 `docs/dev/STATUS.md`。
- HISTORY 只准 `history-append.sh`;本 hop 不追加。
- 本 PR 不宣稱 G1 PASS;status 留 draft;Owner Call／gates 留給人。
- 契約維持現況;本討論不 bump `.claude-plugin/plugin.json`。
- 預設圖 = 靜態直式 SVG;禁把動畫當本刀成功條件。
- 人看討論用繁中;ID／R／S／T 維持英式。

## 驗收雛形
- AC-1(G-ir):假設產器已有上一張通過驗證的產出,當這次 IR 驗證失敗,則目標檔仍是上一張好產出,且人看得到結構化 fail code 與可修旋鈕。
  - 從哪看:產器 stderr／收據檔 + 目標 html／svg 內容(或 git diff)
  - 看到什麼算對:目標檔位元組與 last-good 相同;輸出含穩定 fail code(不是只印 traceback);有一句可修旋鈕。不是「exit 非 0 但檔已被截斷或換掉」
  - 拿什麼試:先產一張綠的 vbox-fig／gate-twin／dir-tree,再餵會失敗的 IR(錯 kind、樹狀 ASCII 當 vbox、缺 why)
- AC-2(G-ir):假設 IR 通過,當產器交付,則寫入是原子的(看見的要嘛全新、要嘛全舊)。
  - 從哪看:目標路徑;半寫失敗時的殘檔
  - 看到什麼算對:沒有截斷 html;失敗留下舊檔或乾淨未寫,不是半份新檔
  - 拿什麼試:對既有 `write_text` 路徑做中斷／非法 IR 對照(throwaway;本 hop 不實作)
- AC-3(G-route):假設 agent 要畫五個家族之一,當它查路由表,則只能落到該家族契約／產器,不能把 Stage 1 三框當生命週期、也不能把目錄樹收成單盒 vbox。
  - 從哪看:路由表(後續契約或模板頂註)逐列
  - 看到什麼算對:五列都有「用這條／不用那條」;與 Context 已核的「何時不用」不打架
  - 拿什麼試:本 repo 五個現況入口:`build-stage1-html.py`、gate-twin 方案架構、gate-twin 行為流、`build-dir-tree.py`、vbox-fig lifecycle
- AC-4(G-lab):假設人要重放 Proof Lab,當跑對齊 selftest／`devflow-check` 的樣張,則 vbox-fig／gate-twin／dirmap 各至少一正一負可重放。
  - 從哪看:Proof Lab 樣張目錄 + `devflow-check` 對應牙輸出
  - 看到什麼算對:三家族都能獨立重放;負向會紅且不蓋 last-good。不是「只有 lifecycle.json 綠過」
  - 拿什麼試:現有 `scripts/fixtures/vbox-fig/lifecycle.json`、`gate-twin/fig-tree-ascii`、`dir-tree/good` 當對照,後續再補齊
- AC-5(Non-Goal):假設本 slug 做完 wave-1,當人打開預設圖,則仍是靜態直式 SVG,沒有把動畫、Mermaid、hosted share 當預設。
  - 從哪看:預設產出 html／svg;本討論 Non-Goals
  - 看到什麼算對:無 mermaid.js、無自動播放動畫當成功條件;靜態幀已完整
  - 拿什麼試:本 hop 審頁(靜態三框)與既有 vbox-fig fixture

## 現況圖
誰:開工 agent
做什麼:混用圖家族
工具:三支產器
痛點:家族對不上
↓
誰:產檔器
做什麼:直接覆寫
工具:write_text
痛點:壞圖蓋好圖
↓
誰:審查人
做什麼:打開審頁
工具:html twin
痛點:無驗證收據

## 邏輯圖(ASCII)
```
now
|-- families exist (vbox / twin / dir-tree / stage1)
|   |-- each has contract + builder + tooth
|   +-- no shared IR receipt
|-- write path
|   |-- write_text overwrite
|   +-- X silent bad html   [#191 direction]
+-- wave-1 (this slug)
    |-- typed IR -> validate -> atomic deliver
    |-- routing table
    |-- Proof Lab fixtures
    +-- no animation default
```

## Interview Log(推理鏈外顯)
- Q:為什麼已經有三套契約還會混家族?
  - 事實:notes/design/vbox-fig-contract.md:L79-L86 notes/design/dir-tree-contract.md:L1-L5 notes/design/stage1-review-ui-contract.md:L32-L39
  - 推理:分流寫在各契約「何時不用」,沒有一張給 agent 先查的路由表。最近看過哪支產器,就容易拿那支畫別的家族。
  - 結論:CONFIRMED 缺口是路由表,不是再抄第四套畫法散文。
- Q:產器現在失敗時,上一張好 html 還在嗎?
  - 事實:scripts/build-dir-tree.py:L574-L576 scripts/build-gate-twin.py:L2327 scripts/build-stage1-html.py:L479-L482 scripts/write-stack-inventory.py:L30-L37
  - 推理:`write_text` 直接蓋檔。vbox-fig 只寫 stdout,呼叫端仍可蓋。他處已有 tmp+replace,圖表產器沒沿用。中斷或「exit 0 但圖已壞」都會丟 last-good。
  - 結論:CONFIRMED 沒有「壞產出不得取代 last-good」;原子交付是新牙,不是現況。
- ⚠️ Q:#191 修完是否已經等於 IR 閘?
  - 事實:docs/dev/HISTORY.md:L488-L491 scripts/devflow_twin_ui.py:L485-L506 scripts/check-gate-twin.sh:L92
  - 推理:#191 修的是靜默裁字與樹狀單盒。牙咬的是 WARNING+`<pre>`。沒有 typed IR、沒有收據、沒有 last-good。方向(禁靜默壞圖)還在,閘還沒建。
  - 結論:CONFIRMED #191 是方向證據,不是本 slug 已做完。
- Q:現有 fixture／牙能不能當 Proof Lab?
  - 事實:scripts/check-vbox-fig.sh:L31 scripts/devflow-check.sh:L132-L138 scripts/check-dir-tree.sh:L1-L6
  - 推理:牙能重放各家族好樣本,但分散、沒有統一 IR 收據,也沒保證負向失敗不蓋檔。Proof Lab 要的是對齊這些牙的可重放樣張,不是另造語言。
  - 結論:CONFIRMED 現況有分散 fixture,沒有 Proof Lab。
- ⚠️ Q:為什麼第一刀不是動畫?Archify 不是強調 motion 嗎?
  - 事實:_templates/diagram-style.md:L5-L7 notes/design/vbox-fig-contract.md:L32-L39
  - 推理:owner 2026-09-12 裁:第一刀不是動畫;預設靜態直式 SVG。Archify 自己也寫 motion 不得承載靜態幀消失的意義。本 repo 現況圖全是靜態 inline SVG。先閘 IR,再談可選 trace。
  - 結論:CONFIRMED 動畫非本刀;預設靜態是約束,不是待裁決口味。
- Q:為什麼只吸收 wave-1,不搬 Archify 堆疊?
  - 事實:_templates/diagram-style.md:L9-L12 notes/design/stage1-review-ui-contract.md:L21-L30
  - 推理:母版已禁 mermaid／外部庫／手包 html-shell。搬 Node／hosted／WYSIWYG 會另開渲染真相。owner 把那些列成 NON-goals。
  - 結論:CONFIRMED wave-1 = 驗證／路由／樣張,不是換渲染引擎。
- ⚠️ Q:IR schema 與 Proof Lab 目錄要不要本檔定案?
  - 事實:notes/design/stage1-context-chain.md:L21-L26
  - 推理:Stage 1 不准 Decision。owner 要的是能力(結構碼、原子交付、可重放),不是本 hop 鎖 schema。帶假設交 Stage 2。
  - 結論:OPEN Q6／Q7 帶假設;過期擋 G2。
- Q:本 hop 要不要產出 G1 核准或改 STATUS Active?
  - 事實:docs/dev/STATUS.md:L10-L26 scripts/status-update.sh:L408-L415 notes/design/stage1-context-chain.md:L21-L26
  - 推理:owner 明示只 Stage 1、不送 G1、不假人 PASS。腳本在 feature branch 拒改 Active。討論檔 status 留 draft。
  - 結論:CONFIRMED 本 PR 不改 status 為 approved,不填 G1 PASS,不改 STATUS 表列。
