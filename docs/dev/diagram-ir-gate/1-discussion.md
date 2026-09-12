---
feature: diagram-ir-gate
stage: 1-discussion
status: draft
owner: tony
reviewers: []
updated: 2026-09-12
baseline: tip 67481d6 / v3.23.3
---

# 1. 討論 — 圖 IR 閘（Archify 吸收 wave-1）

> 用途:發散。**不做決定**。本場依 owner 2026-09-12 書面 brief 落檔,不是現場一問一答。
> Lane = **full**。本 hop **只 Stage 1、不送 G1、不代填 Human PASS**。未核敘述標 `[Assumption]`。
> wave-1 只吸收 Archify 的 IR 驗證／路由／Proof Lab 形,不搬動畫當預設。

## Problem
誰:畫／重生 DevFlow 審頁與 twin 圖的開工 agent,以及打開 html 審圖的 owner／reviewer。
痛:母版已有 vbox-fig／gate-twin／dir-tree 契約與 Python SVG 產器,但沒有 Archify 那種機器可讀 IR 驗證收據、圖種路由表、可重播 Proof Lab。agent 混用圖家族;壞 html 就地覆寫,上次好的圖消失(#191 方向:壞輸出當正本)。
現在怎麼繞:人憑記憶選產器或手包 html-shell;看錯再重跑;各站牙事後紅,沒有 last-good 可回。

## Context(已知事實)
- 本討論基準 plugin `3.23.3`、tip `67481d6`(.claude-plugin/plugin.json:L3 本 working tree `git rev-parse HEAD`)
- 直式方塊母版鎖靜態 SVG、禁 mermaid／橫 ASCII／`<pre>` 當預設圖:notes/design/vbox-fig-contract.md:L36-L39
- vbox-fig 輸入是 JSON 步驟列;產器 `scripts/build-vbox-fig.py`;牙 `scripts/check-vbox-fig.sh`:notes/design/vbox-fig-contract.md:L3-L4 scripts/build-vbox-fig.py:L8-L16
- 生命週期 fixture 已有四格「新生／改行為／退役／不動」JSON:scripts/fixtures/vbox-fig/lifecycle.json:L1-L9
- 第 1 站審頁是另一套三框(`#scan-now` viewBox 200×420),不併進 vbox-fig:notes/design/stage1-review-ui-contract.md:L5-L8 notes/design/stage1-review-ui-contract.md:L21-L26
- 第 1 站審頁產器就地 `write_text` 覆寫同目錄 html,無候補檔、無 last-good:scripts/build-stage1-html.py:L478-L480
- gate-twin 行為／方案圖走 `parse_ascii_fig` → `render_vbox_svg`;樹狀 ASCII 改 WARNING + `<pre>` 後備(#191／#193):scripts/devflow_twin_ui.py:L485-L506 notes/design/vbox-fig-contract.md:L32-L34
- gate-twin 出頁就地寫 `docs/dev/<slug>/<stage>.html`:scripts/build-gate-twin.py:L2317-L2327
- dir-tree 吃手寫 YAML,吐摺疊 `├─` 樹;產器 `write_text` 亦就地覆寫:notes/design/dir-tree-contract.md:L3-L5 notes/design/dir-tree-contract.md:L37-L39 scripts/build-dir-tree.py:L574-L576
- 全站畫法總冊預設靜態 inline SVG,禁 mermaid.js／外部圖檔: _templates/diagram-style.md:L5-L12
- 「何時不用」表散落各契約,沒有一張跨家族路由表:notes/design/vbox-fig-contract.md:L78-L86 notes/design/stage1-review-ui-contract.md:L34-L39 notes/design/dir-tree-contract.md:L68-L73 notes/design/stage2-review-ui-contract.md:L37-L44
- dir-tree 契約把第 1 站 `#scan-now` 指到 `build-scan-html.py`,審頁契約卻鎖 `build-stage1-html.py`:notes/design/dir-tree-contract.md:L70 notes/design/stage1-review-ui-contract.md:L17-L18
- selftest／devflow-check 已掛 vbox-fig／dir-tree／stage1 牙與 gate-twin 牙,fixture 在 `scripts/fixtures/`:scripts/devflow-check.sh:L132-L138 scripts/devflow-check.sh:L234
- Active 目前只有 `integration-before-verdict`;feature branch 禁手改 STATUS 表列:docs/dev/STATUS.md:L10-L26 docs/dev/STATUS.md:L30-L34
- owner 2026-09-12:第一刀不是動畫;預設圖維持靜態直式 SVG;本 slug 只吸收 Archify wave-1(IR 驗證＋路由＋Proof Lab)

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 開工 agent | 依站產對的圖,html 可審 | 跑產器、寫 `docs/dev/<slug>/` | 各站契約與產器檔名 | 這張圖該走哪份契約;壞輸出有沒有蓋掉好的 | 終端機、編輯器 |
| owner | 審頁圖可讀、家族不漂;吸收 Archify 只到 wave-1 | 裁 G1、禁假 PASS | brief、#191 方向 | IR 形／fail code 目錄尚未定 | GitHub、Archify 公開頁 |
| reviewer | 打開 twin／審頁就能看懂圖 | 讀 html;不代填 Human PASS | 產器 stdout／牙紅 | 失敗碼對哪一格、怎麼修 | 瀏覽器 |
| 採用專案 agent | 不要用手包 html-shell 或 mermaid 充圖 | 產品樹寫檔 | 模板頂註 | 混家族時沒有機器收據 | Cursor／Claude |

### Current Journey
正式 SOP:第 1 站審頁走 `build-stage1-html.py --action`;步驟方塊走 vbox-fig;行為／方案圖走 gate-twin ASCII→SVG;目錄樹走 dir-tree。實際常混用或手包。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 開工 agent | 憑記憶選產器或手抄 html | 編輯器 | — | 可能錯家族的 html | 契約對不上 |
| 2 | 產器 | 解析後就地覆寫 twin | `write_text` | — | 新 html 蓋舊檔 | 壞的取代好的 |
| 3 | reviewer | 打開 html 審 | 瀏覽器 | owner | 無 IR 收據 | 看不懂或以為正本 |

### Workarounds
- 人記得就對契約「何時不用」表手動選產器;選錯再重跑。
- #191 後樹狀 ASCII 靠 WARNING + `<pre>` 降級,不是 IR 驗證收據。
- 牙紅了就整頁重產;沒有 last-good 檔可回。
- 手包 html-shell 或貼跨家族 SVG。這些步驟常不留「這次走哪份契約」紀錄。

### Exceptions
- 第 1 站掃頁六件仍走 `build-scan-html.py`(html-shell);與審頁不是同一支。混用是已知例外,不是 wave-1 要合併兩支。
- 樹狀 ASCII:gate-twin 顯式降級 `<pre>`;第 4 站審頁仍要求改成直式 `[R-n]`。
- 可選 dir-tree 不進 gate、不進 1-discussion.html。
- agent 可整段跳過產器、手寫 html;沒有主機層攔截。`[Assumption]` 野外仍常手包或混家族(無採用專案 log;風險=高;期限=Stage 2,過期擋 G2)。

### Evidence
- owner 書面 brief(本 session 2026-09-12):slug `diagram-ir-gate`;full lane;只 Stage 1;wave-1 = IR 驗證收據＋原子交付、圖種路由表、vbox-fig／gate-twin／dirmap Proof Lab;第一刀不是動畫;預設靜態直式 SVG;禁 Mermaid／黑盒自動排版／Node 渲染棧／hosted share／WYSIWYG;深鏈／Architecture Delta／主題／Share Card 留後刀;不代填 PASS;不碰 #196／#200／#201。
- Archify 公開能力(IR → validate → atomic deliver;失敗帶 rule code／supportedFixes;Proof Lab):https://github.com/tt-a1i/archify
- #191 現象與方向(已合 #193,本討論不重做那刀):https://github.com/rick546986/dev-flow/issues/191
- 已核本 tree:上列 Context 出處。
- `[Assumption]` 採用現場仍混家族／手包 html:無 log;從 #191 採用端回報 + 產器就地覆寫推出。

## Goals
- G1 IR 閘:圖源先成可驗證 IR,通過才原子換成目標檔;失敗給穩定 fail code + 可修旋鈕;壞輸出不得取代 last-good。
- G2 路由表:Stage1 現況、Stage2 方案架構、行為流程、dir-tree、模組生命週期各對到唯一契約／產器,agent 不再混家族。
- G3 Proof Lab:vbox-fig／gate-twin／dirmap 各有可重播樣張,與 selftest／既有牙對齊,失敗可 replay。

## Requested solution（候選，未定案）
- 吸收 Archify wave-1 形:typed IR → validate → atomic deliver;結構化失敗;last-good 保留。
- 一張圖種路由表,對齊既有 DevFlow 家族,不新開 Node 渲染棧。
- Proof Lab 掛既有 fixture 目錄與 selftest,不當獨立網站。
- 本 hop 不選定 IR 語法、也不實作產器。

## Non-Goals(初稿)
- 不把 Mermaid、黑盒自動排版、Node 渲染棧、hosted share、WYSIWYG 引進母版。
- 不把動畫當預設(可選 trace 是後刀,不是本刀)。
- 不做深鏈 `#focus`／`#route`、Architecture Delta、主題切換、Share Card。
- 本 hop 不實作產器、不寫 Stage 2+、不送 G1、不代填 Human PASS。
- 不動 integration-before-verdict 的 #200／#201、不動 #196、不發版。
- 不重開 #191 已合的「禁靜默裁字／樹狀改 pre」那刀。

## Open Questions
- [x] Q1:第一刀是不是動畫?→ owner:不是;預設維持靜態直式 SVG
- [x] Q2:本 slug 是否吸收完整 Archify(含 Node／Mermaid／hosted／WYSIWYG／深鏈／Delta／主題／Share Card)?→ 否,只 wave-1
- [x] Q3:lane?→ owner:full
- [x] Q4:本 hop 是否送 G1／代填 PASS?→ 否,只 Stage 1;status 留 draft
- [~] Q5:IR 起手形?(帶假設:先包現有輸入——vbox JSON、dir-tree YAML、gate-twin 直式 ASCII——不當本波發明跨家族 mega-schema;期限=Stage 2,過期擋 G2)
- [~] Q6:原子寫入先罩哪些寫手?(帶假設:就地 `write_text` 的 html 產器——stage1／gate-twin／dir-tree;vbox-fig 目前吐 stdout,另議;期限=Stage 2)
- [~] Q7:Proof Lab 落點?(帶假設:延伸 `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}` 並對齊 selftest,不造 Node gallery;期限=Stage 2)
- [>] Q8:fail code 目錄與 repair knobs 的穩定字串 → 移交 Stage 2
- [>] Q9:可選 trace／深鏈／Delta／主題／Share Card → 移交後續 slug
- [>] Q10:Archify schema 原文搬 vs DevFlow 形 IR → 移交 Stage 2

## Constraints
- 契約維持現況;本討論不 bump `.claude-plugin/plugin.json`。
- 預設圖 = 靜態直式 SVG;禁 mermaid 當預設。
- 表列只准 `scripts/status-update.sh`;feature branch 上腳本拒改正本。
- 不與 #196／#200／#201 搶檔。
- 本 PR 不宣稱 G1 PASS;status 留 draft。
- 人看討論用繁中;ID 維持英式。

## 驗收雛形
- AC-1(G1):假設產器拿到不合法 IR／壞輸入,當它結束這次交付,則目標 html 仍是上次通過的那份,且 stdout／檔上有穩定 fail code。
  - 從哪看:目標 html 的內容雜湊或 mtime;產器 JSON／stderr 的 code 欄
  - 看到什麼算對:html 位元與 last-good 相同;出現機器可讀 code(不是只印 Python traceback);沒有「壞頁已寫入」
  - 拿什麼試:故意壞的 vbox／gate-twin／dir-tree fixture(可重用 `scripts/fixtures/` 負向樣)
- AC-2(G1):假設同一目標已有 last-good,當合法 IR 通過驗證,則新檔原子取代舊檔。
  - 從哪看:目標路徑;過程中的候補檔(若有)
  - 看到什麼算對:結束後只見一份完整新 html;中斷／失敗時仍是舊好檔
  - 拿什麼試:先產一張通過的審頁,再餵合法改稿
- AC-3(G2):假設 agent 要畫「Stage1 現況／Stage2 方案架構／行為流程／dir-tree／模組生命週期」其中一種,當它查路由表,則只得到一個契約＋一個產器。
  - 從哪看:wave-1 路由表(落點後續定;本 hop 只定要有表)
  - 看到什麼算對:五個家族各一列,契約路徑與產器檔名唯一;沒有「兩支都能用」的空白
  - 拿什麼試:本 tree 既有五個家族名 + 上列契約「何時不用」列
- AC-4(G3):假設 CI／本機跑 selftest 或對應牙,當 Replay Proof Lab 樣張,則 vbox-fig／gate-twin／dirmap 各至少一正一負可重播。
  - 從哪看:`scripts/fixtures/` 樣張 + `check-vbox-fig`／`check-gate-twin`／`check-dir-tree` 輸出
  - 看到什麼算對:正樣 exit 0 且形狀鎖死;負樣 exit ≠0 且帶可對的 fail code／既有 `[FAIL]` 標籤
  - 拿什麼試:現成 `lifecycle.json`、gate-twin `fig-tree-ascii`、dir-tree `missing-why`
- AC-5(Non-Goal):假設人打開預設審頁圖,當沒有另開後刀旗標,則圖是靜態直式 SVG,不是動畫／mermaid。
  - 從哪看:產出 html 的 `#scan-now` 或 vbox／行為圖節
  - 看到什麼算對:有 `<svg` + 直式 viewBox;沒有 mermaid.js、沒有預設 `animation:trace`
  - 拿什麼試:本檔經 `build-stage1-html.py --action` 產出的 `1-discussion.html`

## 現況圖
誰:開工 agent
做什麼:混用圖家族
工具:手抄 html
痛點:契約對不上
↓
誰:產器
做什麼:就地覆寫 twin
工具:write_text
痛點:壞的蓋好的
↓
誰:reviewer
做什麼:打開 html 審
工具:瀏覽器
痛點:壞圖當正本

## 邏輯圖(ASCII)
```
now
|-- families exist (contract + python SVG)
|   |-- stage1 #scan-now
|   |-- stage2 option arch
|   |-- behavior flow (gate-twin)
|   |-- dir-tree
|   +-- module lifecycle (vbox)
|-- missing
|   |-- typed IR + receipt
|   |-- atomic last-good
|   +-- one routing table
+-- wave-1 (this slug)
    |-- IR gate + route + proof lab
    +-- X animation / mermaid / node   [reject]
```

## Interview Log(推理鏈外顯)
- Q:既有契約與產器都在,為什麼還會混用圖家族?
  - 事實:notes/design/vbox-fig-contract.md:L78-L86 notes/design/dir-tree-contract.md:L70 notes/design/stage1-review-ui-contract.md:L17-L18
  - 推理:「何時不用」散在各契約,且 dir-tree 把 `#scan-now` 指到掃頁產器、審頁卻鎖另一支。agent 沒有一張可查的路由表,只能憑記憶或抄錯殼。
  - 結論:CONFIRMED 缺口是跨家族路由,不是缺單一契約正文。
- ⚠️ Q:壞 html 為什麼能蓋掉上次好的?
  - 事實:scripts/build-stage1-html.py:L478-L480 scripts/build-gate-twin.py:L2317-L2327 scripts/build-dir-tree.py:L574-L576
  - 推理:三支寫手都是就地 `write_text`。驗證若在寫後、或寫前只紅 stderr,目標檔已經被壞頁取代。Archify 的 atomic deliver + last-good 正是這層沒有的閘。
  - 結論:CONFIRMED 就地覆寫是 G1 的現況痛;本 hop 不實作,只定要有閘。
- Q:#191 合入後,IR 閘是不是已經有了?
  - 事實:scripts/devflow_twin_ui.py:L485-L506 notes/design/vbox-fig-contract.md:L32-L34
  - 推理:#193 修的是樹狀 ASCII 靜默裁字 → WARNING + `<pre>`。這是單一家族的降級,不是 typed IR、不是 fail code 收據、不是原子交付。
  - 結論:CONFIRMED #191 方向仍在(壞輸出不得當正本),但 wave-1 要補的是閘,不是重做裁字刀。
- ⚠️ Q:為什麼第一刀不是動畫?
  - 事實:_templates/diagram-style.md:L5-L12 notes/design/vbox-fig-contract.md:L36-L39
  - 推理:母版畫法與 vbox 已鎖靜態 inline SVG。Archify 預設可開 `animation:trace`,但 owner 2026-09-12 明說第一刀不是動畫。動畫當預設會換審查介面與 a11y,超出 wave-1。
  - 結論:CONFIRMED 預設維持靜態直式 SVG;trace 移交後刀。
- Q:為什麼不直接搬 Archify 的 Node 渲染棧?
  - 事實:scripts/build-vbox-fig.py:L8-L16 scripts/devflow-check.sh:L132-L138
  - 推理:現況產器與牙都是 Python,已進 `devflow-check`。Node 棧是 owner 明文 Non-Goal,也會另開 runtime 地板。wave-1 要的是閘的形(IR／收據／原子寫／路由／樣張),不是換渲染引擎。
  - 結論:CONFIRMED 不引 Node／Mermaid;吸收的是驗證與交付紀律。
- Q:現有 fixture 能不能當 Proof Lab?
  - 事實:scripts/fixtures/vbox-fig/lifecycle.json:L1-L9 scripts/check-vbox-fig.sh:L98-L105 scripts/devflow-check.sh:L132-L138
  - 推理:牙已能重跑 lifecycle 與若干 gate-twin／dir-tree 負向樣,但沒有「IR → 收據 → 可對 fail code」的 Lab 形,也沒有跨家族同一套 replay 入口。
  - 結論:CONFIRMED 樣張在、Lab 形不在;G3 是對齊與補收據,不是從零造圖。
- ⚠️ Q:IR 起手該不該先發明跨家族 mega-schema?
  - 事實:scripts/build-vbox-fig.py:L8-L16 notes/design/dir-tree-contract.md:L37-L39 scripts/devflow_twin_ui.py:L485-L506
  - 推理:三個家族輸入形已經不同(JSON／YAML／ASCII)。先發明第四種總 schema 會拖垮 wave-1,也容易逼人改既有牙。帶假設:先包現有輸入,Stage 2 再裁是否對齊 Archify schema。
  - 結論:OPEN 假設先包現有輸入;非定案,過期擋 G2。
- Q:本 hop 要不要產出 G1 核准或改 STATUS?
  - 事實:docs/dev/STATUS.md:L10-L26 docs/dev/STATUS.md:L30-L34
  - 推理:owner 明示只 Stage 1、不送 G1、不代填 PASS。STATUS 表列只准整合分支走 `status-update.sh`。本檔 status 留 draft。
  - 結論:CONFIRMED 本 PR 不改 approved、不填 G1 PASS;Active 列留給 main 上的腳本。
