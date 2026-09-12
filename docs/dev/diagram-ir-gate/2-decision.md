---
feature: diagram-ir-gate
stage: 2-decision
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-12
---

# 2. 收斂 — 圖表 IR 閘（Archify absorb wave-1）

> 把 `1-discussion.md` 的發散收成 Decision。**本 hop 不代填 G1**：`verdict` 空、`status` 留 draft、OC 維持待人審。契約不 bump。不實作產器、不碰 `#196`、不發版、不改 `integration-before-verdict`。
> owner 2026-09-12 chat「都過」= **Stage 1 方向核准**（IR／路由／Proof Lab、預設靜態直式 SVG）。**不是**本檔 Stage 2 的 G1。1-discussion 留當時「只 Stage 1、不送 G1」原文；本檔才改口成方案決策。

## Approaches Considered

### 決策點：IR 與原子交付
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A | **共用 typed IR 信封 → 驗證 → 原子交付**。掛在既有 Python SVG 產器上。失敗印穩定 fail code + 一句可修旋鈕；驗證不過則目標檔位元組不變（last-good）。寫檔走 tmp + `os.replace` | 對準 G-ir／AC-1／AC-2；吸收 Archify「驗證收據＋原子交付」而不搬 Node 堆疊；他處已有 `atomic_write` 可沿用 | 要定信封欄位與 fail-code 詞彙（Q6）；vbox-fig 現只寫 stdout，呼叫端仍可能自己蓋檔 | 中 | `1-discussion.md:91` G-ir；`1-discussion.md:129-136` AC-1／AC-2；`1-discussion.md:96` 吸收驗證收據不搬堆疊；`scripts/write-stack-inventory.py:30-37` 已有 tmp+replace；`scripts/build-dir-tree.py:574-576`／`scripts/build-gate-twin.py:2327`／`scripts/build-stage1-html.py:479-482` 現況 `write_text` 直蓋。成本 `[Assumption]` |
| B | **各產器各自加驗證**，不共用信封／收據形 | 改動面窄；不必先發明跨家族 schema | 沒有共用收據可附 PR；agent 仍就近抄最近產器；G-ir「結構化 fail code」會裂成三套詞 | 中 | `1-discussion.md:18` 痛=沒有 IR 收據；`1-discussion.md:187-190` Interview 確認沒有 last-good；`1-discussion.md:43` 牙分開咬、沒有共用收據格式。劣的「三套詞」`[Assumption]` |
| C | **整包吸收 Archify**（Node IR／render／hosted／motion） | 現成驗證＋排版 | owner 已否決整包吸收；母版禁 mermaid／外部庫／手包 html-shell | 高 | `1-discussion.md:111` Q2：不要整包；`1-discussion.md:102-104` Non-Goals；`_templates/diagram-style.md:5-12` 禁 mermaid／外部庫 |

### 決策點：圖種路由
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| R-table | **一張顯式路由表**（人／agent 先選家族）。五列：Stage1 現況三框、Stage2 方案架構、行為流、目錄樹、模組生命週期。每列「用這條／不用那條」對到既有契約＋產器＋牙 | 對準 G-route／AC-3；補「何時不用」散落各契約的缺口；不是黑盒自動排版 | 要選落點檔；表若與各契約「何時不用」漂會雙真相 | 低 | `1-discussion.md:92` G-route；`1-discussion.md:137-140` AC-3；`1-discussion.md:97` 路由表當契約不是自動排版；`1-discussion.md:182-186` Interview：缺口是路由表不是第四套畫法散文。落點 `[Assumption]`（本檔 OC-1） |
| R-auto | **黑盒自動辨家族**，從輸入猜該走哪支產器 | agent 少查一張表 | owner 已拒黑盒自動排版；猜錯比混家族更難審；樹狀 ASCII 當 vbox 會再靜默壞圖 | 高 | `1-discussion.md:102` Non-Goals 不做黑盒自動排版；`1-discussion.md:31-32` 樹狀不得單盒硬裁；`notes/design/vbox-fig-contract.md:32-33` 樹狀改 WARNING+`<pre>` |
| R-prose | **維持現況**：分流只寫在各契約「何時不用」，不另開總表 | 零新檔 | 痛仍在：agent 就近抄最近產器；Goals 的路由表落空 | 低 | `1-discussion.md:19-20` 現在怎麼繞=口頭分流；`1-discussion.md:60-61` 正式 SOP vs 實際混用；`1-discussion.md:186` 結論=缺口是路由表 |

### 決策點：Proof Lab 形狀
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| L-align | **對齊現有牙**。樣張仍住 `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}`；薄索引 `scripts/fixtures/proof-lab/` 只點名可重放項。vbox-fig／gate-twin／dirmap 各至少一正一負；負向必須紅且不蓋 last-good。不另造第二套檢查語言 | 對準 G-lab／AC-4／Q7；沿用 `devflow-check` 已掛的牙；現況已有種子（lifecycle.json、fig-tree-ascii、dir-tree/good＋missing-why） | 現況負向不保證「不蓋 last-good」（產器還沒原子交付）；索引與牙清單可能漂 | 中 | `1-discussion.md:93` G-lab；`1-discussion.md:141-144` AC-4；`1-discussion.md:116` Q7 假設：對齊現有牙、目錄形狀 Stage 2 定；`scripts/devflow-check.sh:132-138` 牙已分開掛；`scripts/fixtures/vbox-fig/lifecycle.json`、`scripts/fixtures/gate-twin/fig-tree-ascii/`、`scripts/fixtures/dir-tree/good/`＋`missing-why/`。負向不蓋檔是新牙，現況沒有 `[Assumption]` 已在 Interview `1-discussion.md:196-198` |
| L-newlang | **另造 Proof Lab 檢查語言／新 runner** | 收據形一次到位 | 第二套方法論；與「對齊現有牙」相反；牙雙軌假綠風險 | 高 | `1-discussion.md:98` Proof Lab 不是另造第二套檢查語言；`1-discussion.md:196-198` 要對齊這些牙不是另造語言 |
| L-copy | **新目錄整包複製 fixture**，不掛回現有牙 | 目錄名好看 | 兩份樣張會漂；`devflow-check` 綠 ≠ Proof Lab 綠；AC-4 要對齊 selftest | 中 | `1-discussion.md:141-144` AC-4 從 Proof Lab + `devflow-check` 對應牙看；`1-discussion.md:44` 現況沒有 Proof Lab 目錄名。漂 `[Assumption]` |

## 方案架構圖
[A] IR驗證+原子交付(選定)
[R-table] 五家族路由表
[L-align] Proof Lab對齊牙
[keep] 靜態直式SVG預設

## Decision
採 **A + R-table + L-align**：wave-1 在既有 Python SVG 產器上加共用 typed IR 信封（先驗證、再原子交付）；失敗給穩定 fail code + 一句可修旋鈕，壞產出不得取代 last-good。另立一張五家族路由表，人／agent 先選家族，不是黑盒自動排版。Proof Lab 用薄索引對齊現有 `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}` 與 `devflow-check` 牙，三家族各至少一正一負可重放。預設圖維持靜態直式 SVG。G1 留人審。本 hop 不改碼。

Q6 本檔收口的 fail-code 詞彙（穩定 token；JSON 欄位形進 4-spec）：`IR_EMPTY`、`IR_KIND`、`IR_TITLE`、`IR_LINES`、`IR_FAMILY`、`IR_TREE_AS_VBOX`、`IR_MISSING_WHY`、`DELIVER_SKIPPED`。信封必含 `family`／`version`／`payload`。`family` 枚舉：`stage1-now`｜`stage2-arch`｜`behavior-flow`｜`dir-tree`｜`module-lifecycle`。

Q7 本檔收口：樣張不另搬家；索引落 `scripts/fixtures/proof-lab/`。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| B 各產器自驗 | 沒有共用收據；fail-code 會裂成三套；混家族痛不消。 |
| C 整包 Archify | Q2 已否決；會進口 Node／mermaid／hosted，違反母版看圖零依賴。 |
| R-auto 黑盒猜家族 | Non-Goal；猜錯比口頭混用更難審。 |
| R-prose 只靠「何時不用」 | 現況就是這樣，Goals 的路由表落空。 |
| L-newlang 第二套檢查語言 | 與 G-lab「對齊現有牙」相反。 |
| L-copy 複製不掛牙 | 雙份樣張會漂；selftest 綠 ≠ Proof Lab 綠。 |
| Mermaid／黑盒自動排版／Node render／hosted share／WYSIWYG | Stage 1 Non-Goals；本 Decision 維持拒絕。 |
| 動畫當預設 | Q1／Q8：第一刀不是動畫；可選 trace 是後刀。 |
| deep-link `#focus`／`#route`、Architecture Delta、themes、Share Card | Q9 移交後刀，本 wave 不收。 |

## Rationale
owner 要的 wave-1 是三條能力，不是換渲染引擎。現況已有三套契約＋產器＋牙，缺的是（1）機器可讀驗證收據與「壞圖不得蓋好圖」，（2）給 agent 先查的一張路由表，（3）可重放、對齊現有牙的正負樣張。

A 把 Archify 的「驗證 → 原子交付」掛在本包 Python SVG 上。`write-stack-inventory.py` 已證明 tmp+`os.replace` 在本包可行；圖表產器現在的 `write_text` 直蓋是 #191 方向還沒建的閘，不是「牙綠就等於 last-good」。B 省掉共用信封，收據與 fail-code 會再裂；C 把渲染真相換成 Node，owner 已 lock 不做。

R-table 是契約，不是分類器。五個家族的「何時不用」已經寫在各短冊；缺的是一張入口。R-auto 是被拒的黑盒排版。R-prose 是現況，開這個 slug 就是因為它不夠。

L-align 讓 Proof Lab 當現有 fixture／牙的索引與缺口清單（IR 收據、負向不蓋檔），不是新語言、不是第二份複本。種子已在：`lifecycle.json`、`fig-tree-ascii`、`dir-tree/good`＋`missing-why`。

## 既有脈絡
對帳快照（2026-09-12 tip `630cd41`，含 #205 Stage 1＋#207 他票 G1；本 slug 契約基準仍是 plugin `3.23.3`）：

| 層 | 現況 | wave-1 缺口？ |
|---|---|---|
| vbox-fig 契約＋`build-vbox-fig.py`＋`check-vbox-fig.sh` | 直式 SVG；非法 exit 1；只寫 stdout | 無 IR 收據／無 last-good（呼叫端可蓋） |
| gate-twin `write_text` 覆寫 `docs/dev/<slug>/<stage>.html` | #191 已禁靜默裁字；樹狀 WARNING+`<pre>` | 無 IR 收據；壞 html 仍可蓋好檔 |
| dir-tree `write_text` 覆寫指南或 `--out` | 吃手寫 YAML，不掃 repo 猜 why | 同上 |
| Stage1 審頁 `build-stage1-html.py` | 三框現況圖，不併 vbox-fig | 同上；路由要把它列成獨立家族 |
| `atomic_write` | 只在 stack-inventory 等他處 | 圖表產器沒沿用 |
| fixture／牙 | 分住 vbox-fig／gate-twin／dir-tree／stage1-html | 沒有 Proof Lab 索引；負向不保證不蓋檔 |
| 預設畫法 | 靜態 inline SVG；禁 mermaid／外部庫 | 保持；不是本刀要改的 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| Q6 信封／fail-code 在 Stage 4 之前各寫各的 | Decision 已鎖 token 與信封三欄；JSON 形狀進 4-spec。OC-3 釘死「本站只鎖詞彙，不鎖 JSON」 |
| vbox-fig 只寫 stdout，呼叫端仍 `write_text` 蓋掉 last-good | A 的原子交付約束**寫檔路徑**（dir-tree／gate-twin／stage1／任何把 SVG 落檔的呼叫端）。stdout 產器本身驗證失敗 exit ≠ 0 且不寫檔。OC-2 |
| 路由表與各契約「何時不用」雙真相 | 路由表只做索引：五列指向既有契約，不改寫家族畫法。漂了以家族契約為準、表必改 |
| Proof Lab 索引與 `devflow-check` 清單漂 | 索引只點名已被牙掛住的路徑；新樣張先掛進既有牙再進索引。禁第二套 runner |
| 負向 fixture 在原子交付落地前仍會蓋檔 | 實作順序：先共享寫檔 helper + 驗證閘，再掛「負向不蓋 last-good」牙。SC-1／SC-4 綁在一起 |
| 有人把「都過」當成 Stage 2 G1 PASS | frontmatter `verdict` 空、`status` draft；確認紀錄寫明那是 Stage 1 方向。Agent 不寫 Human PASS |
| feature branch 手改 STATUS 表列 | 流程層 OC-4：本 branch 不跑 `status-update.sh` 改正本；#206 若合入只補 Stage 1 Active。本票 Stage 欄留給 merge 後的 main |
| 實作時把後刀（動畫／deep-link／Delta／themes／Share Card）塞進來 | 上述進 Rejected；要做必須另開薄刀，回本站改 Decision 不算合法 DD |

## Success Criteria
- SC-1(G-ir last-good)：先產一張通過驗證的 vbox-fig／gate-twin／dir-tree 目標檔，再餵會失敗的 IR（錯 kind、樹狀 ASCII 當 vbox、缺 why）。目標檔位元組與餵毒前相同；stderr（或收據）含上列穩定 fail code 之一＋一句可修旋鈕。不是「exit ≠ 0 但檔已被截斷或換掉」。
- SC-2(G-ir atomic)：IR 通過時，目標路徑要嘛全新、要嘛全舊。中斷或寫失敗不得留下截斷 html。對照：現況 `write_text` 路徑在 throwaway 可重現半寫；落地後不可再重現。
- SC-3(G-route)：路由表五列齊（Stage1 現況三框／Stage2 方案架構／行為流／目錄樹／模組生命週期），每列有「用這條／不用那條」，且與 Context 已核的「何時不用」不打架。用本 repo 五個入口對帳：`build-stage1-html.py`、gate-twin 方案架構、gate-twin 行為流、`build-dir-tree.py`、vbox-fig lifecycle。
- SC-4(G-lab)：`scripts/fixtures/proof-lab/` 索引點名的樣張，vbox-fig／gate-twin／dirmap 各至少一正一負可獨立重放；正例走既有牙綠；負例紅且不蓋 last-good。不是「只有 `lifecycle.json` 綠過」。
- SC-5(Non-Goal)：wave-1 預設產出仍是靜態直式 SVG；無 mermaid.js、無自動播放動畫當成功條件、無 Node render 堆疊、無 deep-link／Architecture Delta／themes／Share Card 當本 slug 交付。
- SC-6(本 hop)：本 PR 只有 Stage 2 文檔＋審頁 html；`verdict` 不是 Agent 代填的 PASS；未改 `#196`、未改 `integration-before-verdict`、未 bump plugin、未在本 branch 改正本 `STATUS.md` 表列。

## Scope & Non-Goals(定稿)
- In：A（typed IR → 驗證 → 原子交付；fail-code 詞彙如上；last-good）；R-table（五家族路由表，落點見 OC-1）；L-align（Proof Lab 薄索引＋對齊現有牙）；Q6／Q7 收口；本檔＋`2-decision.html` 送人審 G1。
- Out：B／C／R-auto／R-prose／L-newlang／L-copy；Mermaid；黑盒自動排版；Node render／hosted share／WYSIWYG；動畫當預設（Q8 後刀）；deep-link／Architecture Delta／themes／Share Card（Q9 後刀）；Stage 3+ 產器實作（本 hop 不改碼）；`#196`；release；plugin bump；`integration-before-verdict`；本 hop 代填 G1 PASS。

路由表五列（Decision 鎖內容；檔案落點 OC-1）：

| 家族 | 用 | 產器 | 不用 |
|---|---|---|---|
| Stage1 現況三框 | `notes/design/stage1-review-ui-contract.md` | `scripts/build-stage1-html.py` | vbox-fig；拿 `build-scan-html.py` 充審頁；手包 html-shell |
| Stage2 方案架構 | `notes/design/stage2-review-ui-contract.md` | `scripts/build-stage2-html.py` | mermaid；ASCII `<pre>` 當圖；手包 html-shell；塞進 `build-gate-twin.py` STAGES |
| 行為流 | `notes/design/vbox-fig-contract.md`（ASCII→直式 SVG） | `scripts/build-gate-twin.py`／`scripts/devflow_twin_ui.py` | 樹狀當單盒 vbox；mermaid |
| 目錄樹 | `notes/design/dir-tree-contract.md` | `scripts/build-dir-tree.py` | vbox-fig；掃 repo 猜 why；跟 Stage1 三框搶槽 |
| 模組生命週期 | `notes/design/vbox-fig-contract.md` 四格固定 | `scripts/build-vbox-fig.py` | 發明第五格；跟七站三走廊／fig-lifecycle 混 |

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | 路由表正本落 `notes/design/diagram-route.md`（短冊，只索引）。使用者只被問到「要一張路由表」；「落在 notes/design、不寫進 `_templates/diagram-style.md`」是 owner 延伸 | 畫法總冊管長什麼樣，不管走哪支 API；寫進總冊會把「選家族」跟「畫風格」混成一檔 | `_templates/diagram-style.md:1-7` 管風格不是 API；`notes/design/vbox-fig-contract.md:79-86` 各家族已有「何時不用」。落點本身 `[Assumption]` | 表改掛 diagram-style 或某模板頂註；4-spec 引用路徑全改 | 待人審 |
| OC-2 | 原子交付約束**所有會覆寫目標檔的圖表寫路徑**（dir-tree／gate-twin／stage1-html／把 vbox-fig stdout 落檔的呼叫端）。vbox-fig 本體保持 stdout。使用者只被問到「壞產出不得取代 last-good」；「stdout 產器本身不改寫檔契約」是收窄 | vbox-fig 契約是吐 stdout；改它寫檔會動另一條牙。last-good 的真正風險在 `write_text` 覆寫 | `scripts/build-vbox-fig.py:11-16` 只寫 stdout；`1-discussion.md:78` 呼叫端仍可蓋檔；`scripts/write-stack-inventory.py:30-37` 已有 helper 可抽 | 要改 vbox-fig 改成寫檔 API；`check-vbox-fig.sh` 與所有呼叫端一起動 | 待人審 |
| OC-3 | 本站只鎖 fail-code **token 集合**與信封三欄；JSON schema／收據檔路徑進 4-spec。使用者 brief 要「有結構碼＋可修旋鈕」；「本站枚舉 token、不鎖 JSON」是收窄 | Stage 1 Q6 帶假設：不定死 schema、Stage 2 命名。過期擋 G2，所以本檔必須給詞彙，但不該在 G1 前發明完整 schema | `1-discussion.md:115` Q6；`1-discussion.md:99` 本 hop 不選定 IR schema。收窄本身 `[Assumption]` | 4-spec 前就有人當 schema 用；或 G2 因「未命名」被擋 | 待人審 |
| OC-4 | 本 feature branch **不**跑 `status-update.sh` 改正本 Active 列。標**流程層**。merge 後由整合分支補／改 `diagram-ir-gate` 列（Stage 改 `2-decision`，Gates 仍 G1⬜，除非人已核 G1） | 母版 STATUS 只在整合分支維護；腳本在 feature branch 拒改正本表列。#206 若先合入只是 Stage 1 Active | `docs/dev/STATUS.md:10-26`；`scripts/status-update.sh:408-415`；`1-discussion.md:121` 表列只准腳本且必須在 main | 本 PR 帶 STATUS 列改動，與 #206／並行 session 互蓋 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 本 hop 不 bump plugin、不改各家族契約正文（路由表只索引）。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口成 Decision。
- 共享寫檔 helper 沿用 `atomic_write`（tmp + `os.replace`）形狀；4-spec 再釘模組落點，不另造第三種寫法。
- 失敗輸出：stderr 必含 fail code + 可修旋鈕；收據檔是否落地由 4-spec 定，但收據失敗不得改 dest。
- Stage 3 不預先跳過；觸發判定留給第 3 站（本檔無「跳過 Stage 3」流程層 OC）。
- 本 hop 產審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES，不用 mermaid／ASCII `<pre>` 當圖。
- scan-now 掃頁、七站三走廊／fig-lifecycle、html-shell 不進這五列。

## ADR 晉升檢查
- 難逆轉:否（G3 前可改本檔 Decision／OC；產器尚未落地）
- 反直覺:是（吸收 Archify 原則卻明確不搬 Archify 堆疊；「牙綠」仍不是 last-good）
- 真 trade-off:是（共用 IR 信封 vs 各產器自驗；顯式路由表 vs 黑盒猜家族；薄索引 vs 第二套檢查語言）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-12 | owner chat「都過」核准 Stage 1 方向（wave-1 = IR 驗證＋原子交付／五家族路由表／Proof Lab；預設靜態直式 SVG）。本 hop brief 指定只做 Stage 2 收斂。三決策點：IR 與原子交付／圖種路由／Proof Lab 形狀。
- Stage 1 改口 | 2026-09-12 | 1-discussion 仍 draft、Q6／Q7 `[~]`、Q8／Q9 `[>]`；本檔改口為 Decision 並收口 Q6／Q7。不回改正本討論。
- 後刀 | 2026-09-12 | Q8 動畫可選 trace、Q9 deep-link／Delta／themes／Share Card 維持移交，不進本 Decision 範圍。
- G1 | 2026-09-12 | **未送／待人審**。`verdict` 空。Agent 不代填 Human PASS。本檔 Stage 2 G1 ≠ Stage 1 口頭方向核准。審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審(有記錄的最後手段)。
- STATUS | 2026-09-12 | `scripts/status-update.sh` 在本 branch 拒改正本（`只能在整合分支 main 上改`）。現況 Active 尚無本 slug 列（#206 開著、尚未合入）。merge 後於 main 用腳本 upsert：`2-decision`／G1⬜。不准手改表列。
