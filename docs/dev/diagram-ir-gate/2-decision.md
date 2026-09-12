---
feature: diagram-ir-gate
stage: 2-decision
status: approved
verdict: PASS
owner: rick
reviewers: [user]
updated: 2026-09-12
---

# 2. 收斂 — 圖表 IR 閘（Archify absorb wave-1）

> 把 `1-discussion.md` 的發散收成 Decision。G1 已核:`verdict` PASS、`status` approved、OC-1～OC-4 ✅。契約不 bump。不實作產器、不碰 `#196`、不發版。
> owner 2026-09-12 已 lock 方向（Stage 1 口頭「都過」）：wave-1 = typed IR → 驗證 → 原子交付、五家族路由表、Proof Lab；預設靜態直式 SVG。1-discussion 留當時「只 Stage 1、不送 G1」原文；本檔才改口成方案決策。本 Stage 2 的 G1 是 owner chat「可以」，**不是** Stage 1 口頭核准。

## Approaches Considered

### 決策點：IR 閘交付形
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A | **共用 typed IR 信封** → 驗證 → `atomic_write`(tmp + `os.replace`)。失敗給穩定 fail code + 可修旋鈕；目標檔保持 last-good | 對準 G-ir／AC-1／AC-2；他處已有原子寫；產器不必各發明覆寫規則 | 要定信封欄位與碼表；現有 `write_text` 路徑都要改接到同一閘 | 中 | `1-discussion.md:91` G-ir；`1-discussion.md:129-136` AC-1／AC-2；`scripts/write-stack-inventory.py:30-37` 已有 tmp+replace；`scripts/build-dir-tree.py:574-576`／`scripts/build-gate-twin.py:2327`／`scripts/build-stage1-html.py:479-482` 現況直接覆寫。欄位形狀 `[Assumption]`（4-spec 再釘） |
| B | **每支產器各寫各的**檢查與覆寫；不共用 IR 收據 | 最短；vbox-fig 已有 `normalize` 擋空步驟／錯 kind | 沒有機器可讀收據；呼叫端仍可 `write_text` 蓋掉 last-good；三支各一套失敗散文 | 低 | `scripts/build-vbox-fig.py:91-114` 已擋形；`1-discussion.md:188-190` 確認沒有 last-good；`1-discussion.md:38-40` 三支都直接寫檔。收據缺口 `[Assumption]` 維持 |
| C | **整包吸收 Archify** Node／IR／hosted 堆疊，換掉 Python SVG 產器 | 一次拿到對方驗證語言 | 違反 Non-Goals；另開渲染真相；母版已禁外部庫／mermaid | 高 | `1-discussion.md:101-104` Non-Goals；`1-discussion.md:83` 只吸收驗證收據／原子交付；`_templates/diagram-style.md` 禁 mermaid／外部庫（`1-discussion.md:33`） |

### 決策點：圖種路由
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| D | **一張查找路由表**（契約）：五家族各列「用這條／不用那條」對到既有契約／產器。人／agent **先選家族**，再跑對的 API | 對準 G-route／AC-3；不另造畫法散文；與各契約「何時不用」同向 | 表要與四份契約對帳；選錯家族仍可能硬跑，要靠 IR 家族碼擋 | 低 | `1-discussion.md:92` G-route；`1-discussion.md:137-140` AC-3；`1-discussion.md:185-186` 缺口是路由表不是第四套畫法。硬跑攔截 `[Assumption]`（主機層後刀） |
| E | **黑盒自動辨識家族**／自動排版：吃任意輸入，機器猜該走哪條 | agent 少記一張表 | owner 列為 NON-goal；猜錯會把三框當生命週期、樹收成單盒；無法審計「為何走這條」 | 高 | `1-discussion.md:97` 路由表不是黑盒自動排版；`1-discussion.md:103` 不做黑盒自動排版；`notes/design/vbox-fig-contract.md:79-86` 何時不用已是人查表 |
| F | **五家族併進一支 API**（或改走 mermaid） | 表面少入口 | 與 vbox／dir-tree／stage1「不是同一支 API」打架；mermaid 是禁物 | 高 | `notes/design/dir-tree-contract.md:1-5` 與 vbox／三框不是同一 API；`notes/design/stage1-review-ui-contract.md:1-8` 三框不併進 vbox；`1-discussion.md:102` 不做 Mermaid |

### 決策點：Proof Lab 落點
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| G | **延伸既有** `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}` + **薄索引**（Proof Lab 只點名樣張，不另造檢查語言）。每家族至少一正一負；負向紅且不蓋 last-good；牙仍是現有 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree`／`devflow-check` | 對準 G-lab／AC-4／Q7 假設；現況已有分散 fixture 可對齊 | vbox-fig 現在只有正例；索引檔名未釘 | 中 | `1-discussion.md:93` G-lab；`1-discussion.md:116` Q7 對齊現有牙、目錄後定；`scripts/devflow-check.sh:132-138` 牙已分開跑；`scripts/fixtures/vbox-fig/lifecycle.json` 正例；`scripts/fixtures/gate-twin/fig-tree-ascii` 樹狀負向；`scripts/fixtures/dir-tree/good` 與 `missing-why`（短 why 紅，`check-dir-tree.sh:131-134`）。索引檔名 `[Assumption]` |
| H | **另開** `scripts/proof-lab/` 與第二套檢查語言 | 目錄名對得上 Archify「Proof Lab」 | 第二套方法論；牙與 fixture 雙源會漂 | 高 | `1-discussion.md:98` 不是另造第二套檢查語言；`1-discussion.md:197-198` 要對齊這些牙 |
| I | **只重放現有正例**（lifecycle.json 綠過就算 Lab） | 零新樣張 | AC-4 要三家族各一正一負；vbox-fig 無獨立負向；負向不蓋檔測不到 | 低 | `1-discussion.md:141-144` AC-4「不是只有 lifecycle.json 綠過」 |

## 方案架構圖
[A] typed IR→驗證→原子交付(選定)
[D] 五家族路由表先選家族(選定)
[G] 對齊現有牙的 Proof Lab(選定)

## Decision
採 **A + D + G**：在既有 Python SVG 產器上掛 typed IR → 驗證 → 原子交付（穩定 fail code + 可修旋鈕；驗證失敗或寫入中斷都不得取代 last-good）；用一張查找路由表把五個家族對到既有契約／產器（人／agent 先選家族，不是黑盒自動排版、不是 mermaid、不是一支 API 吃全家）；Proof Lab 對齊現有 selftest／`devflow-check` 牙，延伸既有 fixture 目錄加薄索引，vbox-fig／gate-twin／dirmap 各至少一正一負。Q6 本檔命名 fail-code 前綴與 wave-1 碼；JSON 信封欄位進 4-spec。Q7 本檔定落點＝既有 fixture + 薄索引。預設圖維持靜態直式 SVG。G1 已核。本 hop 不實作產器。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| B 每產器各寫各的 | 已有 `normalize` 仍無收據、無 last-good；呼叫端照樣 `write_text` 蓋檔。 |
| C 整包 Archify Node 堆疊 | Non-Goal；另開渲染真相；只吸收驗證收據／原子交付方向。 |
| E 黑盒自動辨識／自動排版 | owner 禁；猜錯家族無法審計；路由表是查找契約。 |
| F 五家族併一支 API／mermaid | 與「不是同一支 API」打架；mermaid 是禁物。 |
| H 另造 Proof Lab 檢查語言 | 第二套方法論；與現有牙雙源。 |
| I 只重放正例 | 不滿足「三家族各一正一負且負向不蓋 last-good」。 |
| Mermaid 當預設圖 | 畫法總冊與 vbox-fig 鎖死直式 SVG。 |
| Node render／hosted share／WYSIWYG | wave-1 NON-goal；不換渲染引擎。 |
| 動畫當預設 | 第一刀不是動畫；可選 trace 是後刀（Q8）。 |
| deep-link／Architecture Delta／themes／Share Card | Q9 移交後刀，本 slug 不收。 |

## Rationale
G-ir 的第一因不是「產器不會擋形」，而是「擋完仍直接覆寫、沒有機器可讀收據」。vbox-fig 的 `normalize` 已擋空步驟／錯 kind／空標題，但只寫 stdout；dir-tree／gate-twin／stage1-html 用 `write_text` 蓋目標。#191 修的是靜默裁字與樹狀單盒，牙咬 WARNING+`<pre>`，不是 IR 閘。A 把已存在的 `atomic_write` 接到圖表寫路徑，失敗先給碼再停寫，last-good 才站得住。B 重複現況。C 把 wave-1 做成換引擎。

G-route 的第一因是分流散在各契約「何時不用」，agent 就近抄最近產器。D 做一張先查的表，五列都寫「用這條／不用那條」，與已核契約同向。E／F 是 owner 已拒的黑盒與併 API。

G-lab 要的是可重放樣張對齊現有牙，不是新語言。G 留下 `lifecycle.json`、`fig-tree-ascii`、`dir-tree/good` 與 `missing-why`（短 why 紅），並要求每家族補齊一正一負且負向不蓋檔。H 另造語言。I 只綠正例，AC-4 落空。

## 既有脈絡
對帳快照（2026-09-12 tip `a59fd22`，#205 之後）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| vbox-fig 契約／產器／牙 | 直式 SVG；`normalize` 擋形；stdout；無寫檔、無 last-good | A 的驗證層沿用擋形；寫檔閘加在呼叫端 |
| gate-twin／stage1-html／dir-tree 寫檔 | `write_text` 直接覆寫 | A 改接到原子交付；失敗不碰目標 |
| 他處 `atomic_write` | `write-stack-inventory.py` tmp+replace | OC-3 沿用，不另造第三支寫檔幫手 |
| 各契約「何時不用」 | 散在 vbox／dir-tree／stage1 三份 | D 收成一張五列路由表 |
| fixture／牙 | 分散；vbox-fig 幾乎只有正例；dir-tree 短 why 已紅；gate-twin 樹狀 ASCII 已 WARNING+pre | G 當 Proof Lab 底；缺口 Stage 6 補 |
| #191 | 禁靜默裁字；不是 IR 收據 | 方向證據；本 slug 另建閘 |
| Active 表列 | `status-update.sh` 只准 main | 本 branch 不改正本（OC-4） |

### 選定路由表（D 定稿）

| 家族 | 用這條 | 不用那條 | 產器 | 契約 |
|---|---|---|---|---|
| Stage1 現況三框 | 第 1 站審頁 `#scan-now` 直式三框 | 掃頁 `build-scan-html.py`；vbox-fig 生命週期四格；gate-twin 五格 | `build-stage1-html.py --action` | `notes/design/stage1-review-ui-contract.md` |
| Stage2 方案架構 | 第 2 站審頁 Decision 後直式 `[標籤] 標題` SVG | mermaid；橫 ASCII；`<pre>` 當圖；手包 html-shell | `build-stage2-html.py --action` | `notes/design/stage2-review-ui-contract.md` + vbox-fig 母版 |
| 行為流 | gate-twin 行為流程；樹狀改 WARNING+`<pre>` | 樹收成單盒 vbox；mermaid | `build-gate-twin.py`／`devflow_twin_ui.py` | vbox-fig-contract（twin 收口） |
| 目錄樹 | 手寫 YAML `why`；產品 `dir-tree.html` | 掃 repo 猜 why；收成單盒 vbox；跟第 1 站三框搶槽 | `build-dir-tree.py` | `notes/design/dir-tree-contract.md` |
| 模組生命週期 | 四格固定：新生 → 改行為 → 退役 → 不動 | 第五格／parked；第 1 站三框；七站三走廊 | `build-vbox-fig.py` | `notes/design/vbox-fig-contract.md` |

### Q6 命名（wave-1 fail code）

前綴 **`DIAGIR_`**。本檔鎖碼名與觸發；信封欄位（`family`／`payload`／`receipt`）進 4-spec。

| 碼 | 何時 | 可修旋鈕（人看得到的一句） |
|---|---|---|
| `DIAGIR_KIND` | kind 不在該家族允許清單（vbox 只准 b／hl／wn） | 把 kind 改回允許值，或改走路由表上的正確家族 |
| `DIAGIR_EMPTY` | 步驟列空、標題空 | 補上非空標題／至少一步 |
| `DIAGIR_LINES` | vbox `lines` 不是一到三行非空字串 | 收成 1–3 行、刪空行 |
| `DIAGIR_FAMILY` | payload 家族 ≠ 這次選的路由列（樹狀當 vbox、三框當生命週期、目錄樹收單盒） | 查路由表，改呼叫對的產器 |
| `DIAGIR_WHY` | dir-tree 缺 why 或 why 過短（對齊現有短 why 紅） | 在 YAML 補一句到兩句 why |
| `DIAGIR_ABORT` | 驗證失敗或寫入未完成；目標未被新內容取代 | last-good 仍在；先修 IR 再重跑 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 信封欄位未釘，Stage 4 之前各寫各的 | Decision 只鎖「有 family／payload、先驗證再寫、失敗給 `DIAGIR_*`」。欄位進 4-spec；OC-1 收窄「本檔命名碼，不在本 hop 鎖 JSON Schema」 |
| 現有產器仍被直接 `write_text` 繞過閘 | 4-spec 把三支寫檔路徑列進同一 S；未接閘不得宣稱 wave-1 完成。vbox-fig stdout 的呼叫端也算寫檔路徑 |
| vbox-fig 尚無獨立負向樣張 | G 要求 Stage 6 補錯 kind／空步驟負例；本 hop 不實作。I 已拒 |
| 路由表與契約「何時不用」漂 | 五列必須能指回 Context 已核出處；改契約「何時不用」= 回本站改表 |
| 黑盒自動排版誘惑（E）在實作回流 | E／F／C 進 Rejected；翻案回本站 |
| 有人把 Stage 1 口頭「都過」當成 Stage 2 G1 PASS | G1 已按 owner chat「可以」落檔（`verdict` PASS、`status` approved）；翻案回本站 |
| feature branch 手改 STATUS 表列 | 流程層 OC-4：本 branch 不跑 `status-update.sh` 改正本 |

## Success Criteria
- SC-1(G-ir last-good)：先有一張通過驗證的目標 html／svg，再餵會觸發 `DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY` 的 IR → 目標檔位元組與 last-good 相同；stderr 或收據含該穩定碼（不是只 traceback）+ 一句可修旋鈕。
- SC-2(G-ir 原子)：驗證通過後的寫入要嘛全新、要嘛全舊；中斷或失敗後目標不是截斷 html。對照現有 `write_text` 路徑，失敗不得留下半份新檔。
- SC-3(G-route)：路由表五列都有「用這條／不用那條」+ 產器 + 契約；抽測五個現況入口（`build-stage1-html.py`、gate-twin 方案架構、gate-twin 行為流、`build-dir-tree.py`、vbox-fig lifecycle）只能落到該列，不能把 Stage 1 三框當生命週期、也不能把目錄樹收成單盒 vbox。
- SC-4(G-lab)：Proof Lab 索引點名的樣張，vbox-fig／gate-twin／dirmap 各至少一正一負可獨立重放；負向 exit ≠ 0 且不蓋 last-good。不是「只有 `lifecycle.json` 綠過」。
- SC-5(Q6 碼)：失敗輸出含上表六個碼之一（或 4-spec 增列的同前綴碼）；人能指出對應旋鈕句。
- SC-6(Non-Goal)：預設產出仍是靜態直式 SVG；無 mermaid.js、無自動播放動畫當成功條件、無 Node render／hosted share／deep-link／Delta／themes／Share Card。未改 `#196`、未 bump plugin、未開 Stage 3 檔。本檔 `verdict` PASS 來自 owner chat「可以」，不是 Agent 自裁。

## Scope & Non-Goals(定稿)
- In：A 共用 IR 閘＋原子交付＋`DIAGIR_*` 碼名；D 五家族路由表（上表）；G Proof Lab＝既有 fixture + 薄索引，三家族各一正一負；Q6／Q7 在本檔收口。
- Out：B／C／E／F／H／I；Mermaid；黑盒自動排版；Node render／hosted／WYSIWYG；動畫當預設（Q8 後刀）；deep-link／Architecture Delta／themes／Share Card（Q9 後刀）；本 hop 實作產器或補負向 fixture 碼；`#196`／`#200`／`#201`；`integration-before-verdict`；發版／bump plugin；本 hop 不開 Stage 3 檔。

## Owner Calls(自判裁決,已核)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | wave-1 fail code 前綴 **`DIAGIR_`**，本檔鎖上表六碼。JSON 信封欄位留給 4-spec，本 hop 不鎖 Schema。使用者只被問到「有結構碼 + 可修旋鈕」；「前綴與六碼」是 owner 延伸 | Q6 期限＝Stage 2 必須命名；不定死全 Schema 才不會在本 hop 假鎖欄位 | `1-discussion.md:115` Q6；`1-discussion.md:129-131` AC-1 要穩定碼不是 traceback。六碼清單 `[Assumption]` | 改前綴或把 Schema 提前鎖進本檔；SC-5 觀測點變 | ✅ |
| OC-2 | Proof Lab **不**另開檢查語言。落點＝既有 `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}` + 一份薄索引（檔名 4-spec 再釘）。使用者 brief 要 Lab；「延伸既有目錄、不新建語言」是 Q7 收口 | 另造目錄＋語言＝H，已拒 | `1-discussion.md:116` Q7；`1-discussion.md:98` 對齊現有牙。索引檔名 `[Assumption]` | Scope 改成 `scripts/proof-lab/` 或第二套牙 | ✅ |
| OC-3 | 原子寫**沿用**既有 `atomic_write`(tmp + `os.replace`) 形狀，抽到圖表寫路徑共用；不另造第三支寫檔幫手。使用者只鎖「原子交付」；「沿用 inventory 幫手」是延伸 | 他處已綠；另造幫手靠近第二套寫檔真相 | `scripts/write-stack-inventory.py:30-37`；`1-discussion.md:40` 圖表產器沒沿用。抽函式落點 `[Assumption]` | 每支產器各寫一份 tmp+replace，或改用別的原子原語 | ✅ |
| OC-4 | 本 feature branch **不**跑 `status-update.sh` 改正本 Active 列。Stage 欄留 main 現況，merge 後由整合分支更新。標**流程層** | 母版 STATUS 只在整合分支維護；腳本在 feature branch 拒改正本表列 | `docs/dev/STATUS.md:10-26`；`scripts/status-update.sh:408-415`；`1-discussion.md:121` | 本 PR 帶 STATUS 列改動，與並行 session 互蓋 | ✅ |

### 內部技術選擇(下層,告知即可)
- 本 hop 不 bump `.claude-plugin/plugin.json`（仍 3.23.3）、不改產器碼。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口成 Decision。不把 Stage 1 口頭「都過」寫進 1-discussion `status: approved`。
- Stage 3 不預先跳過；觸發判定留給第 3 站（本檔無「跳過 Stage 3」流程層 OC）。
- 本 hop 產審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。
- vbox-fig 負向樣張（錯 kind／空步驟）列為 Stage 6 必補，不在本 hop 造假 fixture。

## ADR 晉升檢查
- 難逆轉:否（G3 前可改本檔 Decision／OC；閘尚未落地）
- 反直覺:是（#191 已修仍不是 IR 閘；現有 fixture ≠ Proof Lab；`write_text` 看起來像交付、中斷才露出半檔）
- 真 trade-off:是（共用 IR 閘摩擦 vs 每產器各寫；延伸 fixture vs 新 Lab 語言）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-12 | owner chat「都過」核准 Stage 1 方向（wave-1 三條 DO、預設靜態直式 SVG）。本 hop brief 指定 Stage 2 必須覆蓋 IR 閘／五家族路由表／Proof Lab，並駁回 Mermaid、黑盒自動排版、Node、動畫預設、後刀 deep-link／Delta／themes／Share Card。三決策點對應該鎖板。
- Stage 1 改口 | 2026-09-12 | 1-discussion 仍 draft、Q4 寫「只 Stage 1 不送 G1」、Q6／Q7 仍 `[~]`。本檔改口為 Decision，並為 Q6 命名 `DIAGIR_*`、為 Q7 定既有 fixture + 薄索引。不回改正本討論。
- G1 | 2026-09-12 | owner 在 chat 說「可以」（G1 / Decision approved）。基準 #212（`b7c285d`）。OC-1～OC-4 隨 Decision 一併視為接受。本 Stage 2 G1 與 Stage 1 口頭「都過」分開。owner 自審(有記錄)；reviewers: [user]
- 自檢七掃 | 2026-09-12 | ①優劣皆有依據欄；②G-ir／G-route／G-lab 進 Decision，漏項進 Non-Goals；③Q8／Q9 `[>]` 進 Rejected＋Out；④SC-1～6 可量測；⑤Rejected 無空棄因；⑥三決策點由 owner brief 確認，OC-1～3 承接 Q6／Q7／原子寫延伸，OC-4 流程層；⑦既有脈絡表是對帳不是外移 schema。圖上 A／D／G 標選定，Rejected 未上圖。
