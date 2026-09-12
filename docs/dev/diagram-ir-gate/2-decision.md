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

> 把 `1-discussion.md` 的發散收成 Decision。**本 hop 不代填 G1**：`verdict` 空、`status` 留 draft、OC 維持待人審。契約不 bump。不實作產器、不碰 `#196`、不發版、不動 `integration-before-verdict`。
> owner 2026-09-12 chat「都過」= Stage 1 方向核准（wave-1 三條 DO；第一刀不是動畫）。1-discussion 留當時「只 Stage 1、不送 G1」原文；本檔才改口成方案決策。本站 G1 與 Stage 1 口頭過是兩件事。

## Approaches Considered

### 決策點：IR 閘與原子交付
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A | **共用 typed IR 信封 → 驗證 → 原子寫**。家族＋既有產器 payload；失敗印穩定 `IR_*` 碼＋一句可修旋鈕；`tmp`+`os.replace`；驗證失敗不碰目標檔，last-good = 目標檔原位元組（無則維持未寫） | 對準 G-ir／AC-1／AC-2；他處已有 `atomic_write`；vbox-fig 已有 normalize 可掛同一驗證縫 | 要抽共用 deliver、把現有 `write_text` 換掉；IR 欄位仍要 4-spec 釘 | 中 | `1-discussion.md:91` G-ir；`1-discussion.md:129-136` AC-1／AC-2；`scripts/write-stack-inventory.py:30-37` 已有 tmp+replace；`scripts/build-dir-tree.py:574-576`、`scripts/build-gate-twin.py:2327`、`scripts/build-stage1-html.py:479-482` 現況直接蓋檔；`scripts/build-vbox-fig.py:91-114` 已擋空步／錯 kind。成本 `[Assumption]` |
| B | **各產器自管 last-good**（各自 `.bak` 或失敗後再寫回），不共用 IR、不共用 fail code | 零新信封；改動可局部 | 無機器可讀收據；fail 文案各寫各的；vbox-fig 只寫 stdout，呼叫端仍可蓋；G-ir「結構碼」落空 | 低 | `1-discussion.md:37` vbox-fig 無寫檔、無 last-good；`1-discussion.md:72` 無 IR 收據；`1-discussion.md:189-190` 呼叫端仍可蓋。劣的「各寫各的」`[Assumption]` |
| C | **進口 Archify Node／render 堆疊當驗證器** | 現成 portable proof | 母版禁外部庫／mermaid；owner 已裁只吸收驗證收據方向、不搬 render；另開渲染真相 | 高 | `1-discussion.md:101-103` Non-Goals；`_templates/diagram-style.md:5-12` 禁 mermaid／外部庫；`1-discussion.md:84` 只吸收驗證／原子交付，不搬堆疊 |

### 決策點：圖種路由
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| R-1 | **一張五列路由表契約**：人／agent **先查家族**再跑對的契約／產器。五列＝Stage1 現況、Stage2 方案架構、行為流、目錄樹、模組生命週期。每列寫「用這條／不用那條」 | 對準 G-route／AC-3；補「何時不用」分散、就近抄產器的缺口；不是黑盒自動排版 | 表要跟人維護；有人仍可硬跑錯產器（主機攔截是後續牙，不是本 hop 碼） | 低 | `1-discussion.md:92` G-route；`1-discussion.md:137-140` AC-3 五個入口；`1-discussion.md:185-186` 缺口是路由表不是第四套畫法散文；`notes/design/vbox-fig-contract.md:79-86`、`notes/design/dir-tree-contract.md:66-73`、`notes/design/stage1-review-ui-contract.md:32-39` 分流已在各契約。攔截時機 `[Assumption]`（4-spec／牙） |
| R-2 | **依輸入形自動猜家族**（JSON 步驟→vbox、YAML 樹→dir-tree、三框→stage1） | 少一步人工選 | 黑盒自動排版／自動路由；JSON 步驟也能被誤收成生命週期；違反 owner NON-goal | 中 | `1-discussion.md:97` 路由表當契約不是黑盒；`1-discussion.md:103` 禁黑盒自動排版；`1-discussion.md:60` agent 就近抄最近產器。誤收 `[Assumption]` |
| R-3 | **五家族併成一支 mega-API** | 表面只記一個入口 | 第 1 站三框會被併進 vbox；目錄樹會被收成單盒；跟各契約「何時不用」打架 | 高 | `1-discussion.md:107` 不把三框併進 vbox-fig；`notes/design/dir-tree-contract.md:1-5` 與 vbox／三框不是同一支 API；`1-discussion.md:137-140` AC-3 要五列分開 |

### 決策點：Proof Lab 落點
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| L-1 | **延伸現有** `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}`。薄索引列出「樣張→牙→期望（綠／紅且不蓋 last-good）」。vbox-fig／gate-twin／dirmap 各至少一正一負；對齊現有 selftest／`devflow-check`，不另造檢查語言 | 對準 G-lab／AC-4／Q7 假設；牙已咬分散 fixture；負向可掛同一批牙 | 現況正負不齊（vbox 缺專用負向；gate-twin 樹狀是 WARNING+`<pre>`，還不是 last-good 拒寫） | 中 | `1-discussion.md:93` G-lab；`1-discussion.md:116` Q7 對齊現有牙、目錄形狀本站定；`1-discussion.md:141-144` AC-4；`scripts/devflow-check.sh:132-139` 已分跑 vbox／dir-tree／stage 牙；`scripts/fixtures/vbox-fig/lifecycle.json` 正；`scripts/fixtures/dir-tree/good`＋`missing-why` 正負；`scripts/fixtures/gate-twin/fig-tree-ascii` 樹狀負向。補齊成本 `[Assumption]` |
| L-2 | **新建頂層 Proof Lab 目錄**，把樣張複製過去當第二棵樹 | 名字對得上 Archify「lab」 | 兩棵 fixture 會漂；牙仍咬舊路則 lab 變展覽；另造語言則 G-lab 落空 | 高 | `1-discussion.md:98` 不是另造第二套檢查語言；`1-discussion.md:197-198` 要對齊現有牙。漂 `[Assumption]` |
| L-3 | **只做截圖／目視 lab**，不掛 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree` | 看起來像證明 | 牙綠 ≠ 可重放 IR 失敗；負向不蓋檔無法機械驗；AC-4 要跑牙 | 低 | `1-discussion.md:61` 牙綠 ≠ 家族對、≠ 沒蓋 last-good；`1-discussion.md:143` 負向會紅且不蓋 last-good |

## 方案架構圖
[A] 共用 IR 原子寫(選定)
[R-1] 五列路由表(選定)
[L-1] 延伸現有牙(選定)
[keep] 靜態直式 SVG

## Decision
採 **A + R-1 + L-1**：wave-1 在既有 Python SVG／html 產器上加 typed IR 信封（`family` + 該家族既有 payload），先驗證再原子交付。失敗輸出穩定 `IR_*` 碼與一句可修旋鈕；目標檔保持上一張好產出（或從未寫過）。一張五列路由表讓人／agent 先選家族，再落到對的契約／產器，不自動猜、不併 API。Proof Lab 延伸現有 `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}`，用薄索引對齊現有牙與 `devflow-check`；三家族各至少一正一負可重放。預設圖維持靜態直式 SVG。本 hop 只交 Stage 2 文檔與審頁；不實作產器、不代填 G1。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| B 各產器自管 last-good | 沒有共用 IR 收據與穩定 fail code；vbox 呼叫端仍可蓋檔；G-ir 落空。 |
| C 進口 Archify Node／render | Non-Goal；母版禁外部庫；只吸收驗證／原子交付方向。 |
| R-2 自動猜家族 | 黑盒自動排版／自動路由；owner 已禁。 |
| R-3 五家族 mega-API | 會把三框併進 vbox、把目錄樹收成單盒；跟「何時不用」打架。 |
| L-2 新建第二棵 fixture 樹 | 與現有牙脫鉤、樣張會漂；G-lab 要對齊 selftest，不是另開展覽。 |
| L-3 只做截圖 lab | 負向不蓋檔與 IR 失敗無法機械重放。 |
| Mermaid／黑盒自動排版／Node render／hosted share／WYSIWYG | Stage 1 Non-Goals；本刀不翻案。 |
| 動畫當預設 | owner 2026-09-12：第一刀不是動畫；可選 trace 移交後刀（Q8）。 |
| deep-link `#focus`／`#route`、Architecture Delta、themes、Share Card | Q9 移交後刀，本 wave 不收。 |

## Rationale
Stage 1 已核：缺口不是再抄第四套畫法，而是（1）沒有 typed IR 收據與 last-good、（2）分流散在各契約「何時不用」、（3）fixture 能重放但不是 Proof Lab。#191 修的是靜默裁字與樹狀單盒，牙咬 WARNING+`<pre>`，不是本閘。

A 把 Archify 的「驗證收據 + 原子交付」掛在現有 Python 產器上：驗證失敗就不寫，成功才 `tmp`+replace，所以壞產出無法取代 last-good。B 只補備份檔，收據與結構碼仍缺。C 換渲染引擎，已被裁掉。

R-1 讓路由成為先查的契約表，五列對準 AC-3 現況入口。R-2／R-3 不是「比較省」，是把家族判斷藏進機器或併掉契約邊界。

L-1 承認牙已經會跑 `lifecycle.json`、`fig-tree-ascii`、`dir-tree/good` 與 `missing-why`。Proof Lab 要的是把它們編成可點名的正負樣張，並補齊「紅且不蓋檔」。L-2／L-3 要麼複製漂移，要麼變成目視展覽。

## 既有脈絡
寫檔現況（#205 tip `a59fd22`）：dir-tree／gate-twin／stage1-html 用 `write_text` 直接覆寫；vbox-fig 只寫 stdout；`write-stack-inventory.py` 已有 `atomic_write`。分流現況：vbox-fig／dir-tree／stage1-now／stage2-card 各有契約與牙，沒有一張先查的路由表，也沒有 IR 收據。#191 方向（禁靜默壞圖）在，閘還沒建。詳 `1-discussion.md` Context／Interview Log。

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| IR schema／fail-code 枚舉未釘，Stage 4 之前各寫各的 | Decision 只鎖信封形（`family` + 既有 payload）與 `IR_*` 前綴＋下列 starter。完整枚舉進 4-spec；OC-1 承接 Q6 |
| 有人把 last-good 做成旁路 `.bak`，失敗仍先截斷目標檔 | OC-3：last-good = 目標路徑原位元組；失敗不寫 dest。SC-1 咬的是 dest 不變，不是多一個備份 |
| vbox-fig 只寫 stdout，呼叫端仍 `write_text` | OC-2：共用 deliver 包「驗證後才寫檔」；vbox 本身維持 stdout，寫檔縫在呼叫端／共用 helper |
| 路由表寫了仍硬跑錯產器 | 本 hop 不實作攔截。4-spec／牙再釘「錯家族 → `IR_FAMILY_MISMATCH`」。R-2 自動猜已拒 |
| Proof Lab 變成第二套檢查語言 | L-2／L-3 已拒；索引只點名現有牙。新牙只能延伸 `check-vbox-fig`／`check-gate-twin`／`check-dir-tree`／`devflow-check` |
| 把動畫／deep-link／themes 當本刀成功條件 | Rejected + Non-Goals；SC-6 咬預設靜態直式 SVG |
| feature branch 手改 STATUS 表列 | 流程層 OC-5：本 branch 不跑 `status-update.sh` 改正本；merge 後由整合分支更新 Stage |
| 本 hop 被當成已過 G1 | frontmatter `verdict` 空、`status` draft；Agent 不寫 Human PASS |

## Success Criteria
- SC-1(G-ir／AC-1)：先有一張通過驗證的目標檔；再餵會失敗的 IR（錯 kind、樹狀 ASCII 當 vbox、缺 why）。目標檔位元組與失敗前相同；stderr／收據含穩定 `IR_*` 碼與一句可修旋鈕。不是「exit ≠ 0 但檔已被截斷或換掉」。
- SC-2(G-ir／AC-2)：IR 通過後的寫入是原子的：看見的要嘛全新、要嘛全舊。中斷或非法 IR 不得留下半份新 html／svg。
- SC-3(G-route／AC-3)：路由表五列都有「用這條／不用那條」，且對到 `build-stage1-html.py`、Stage2 方案架構（`build-stage2-html.py` 審頁 + gate-twin 方案架構）、gate-twin 行為流、`build-dir-tree.py`、vbox-fig lifecycle。不准把 Stage 1 三框當生命週期，不准把目錄樹收成單盒 vbox。
- SC-4(G-lab／AC-4)：vbox-fig／gate-twin／dirmap 各至少一正一負可經現有牙或 `devflow-check` 重放；負向紅且不蓋 last-good。不是「只有 `lifecycle.json` 綠過」。
- SC-5(Q6／Q7)：fail-code 以 `IR_` 開頭、穩定 token；Proof Lab 索引指到現有 `scripts/fixtures/*`，沒有第二套檢查語言、沒有脫鉤複本樹。
- SC-6(Non-Goal／AC-5)：預設產出仍是靜態直式 SVG；無 mermaid.js、無自動播放動畫當成功條件；無 deep-link／Delta／themes／Share Card 當本 wave 交付。
- SC-7(本 hop)：本 PR 只有 Stage 2 文檔＋`build-stage2-html.py --action` 審頁；`verdict` 不是 Agent 代填的 PASS；未改 `#196`、未 bump plugin、未在本 branch 改正本 `STATUS.md` 表列。

## Scope & Non-Goals(定稿)
- In：A 共用 IR→驗證→原子交付；R-1 五列路由表契約（落點見 OC-4）；L-1 Proof Lab 延伸現有 fixture＋薄索引；Q6／Q7 在本站收口方向（枚舉／欄位進 4-spec）；Q8／Q9 維持移交後刀。
- Out：B／C／R-2／R-3／L-2／L-3；Mermaid；黑盒自動排版；Node render；hosted share；WYSIWYG；動畫當預設；deep-link／Architecture Delta／themes／Share Card；本 hop 實作產器或牙；Stage 3+ 碼；`#196`；發版；`integration-before-verdict`；本 hop 代填 G1 PASS。

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | Fail-code **前綴 `IR_`**。wave-1 starter：`IR_EMPTY`、`IR_BAD_KIND`、`IR_FAMILY_MISMATCH`、`IR_MISSING_WHY`、`IR_TREE_AS_VBOX`、`IR_DELIVER_REFUSED`。每筆失敗＝碼＋一句可修旋鈕。完整枚舉／欄位 4-spec 再釘。使用者只被問到「要有結構碼」；具體詞彙是 owner 對 Q6 的延伸 | 不定前綴 → Stage 6 各發明字串，收據無法對；AC-1 試的三種失敗要對得上碼 | `1-discussion.md:115` Q6；`1-discussion.md:132` 穩定 fail code。延伸本身 `[Assumption]` | 改前綴或 starter；SC-1／SC-5 要重寫 | 待人審 |
| OC-2 | **共用 Python deliver helper**（沿用 `atomic_write` 的 tmp+replace），包在現有產器寫檔縫。`build-vbox-fig.py` 維持 stdout；呼叫端／helper 才寫檔。不新開 Node CLI。使用者要 IR 閘；「共用 helper、vbox 仍 stdout」是延伸 | 圖表產器沒沿用已有原子寫；vbox 無寫檔，只改三支 `write_text` 會漏呼叫端 | `scripts/write-stack-inventory.py:30-37`；`1-discussion.md:37` vbox 無寫檔；`1-discussion.md:189` 呼叫端仍可蓋 | 改成各產器自寫或另開 CLI；與拒 C／拒 B 要重審 | 待人審 |
| OC-3 | last-good **就是目標路徑原位元組**。失敗不寫 dest、不要求旁路 `.bak`／`.last-good`。首次失敗且檔不存在 → 維持未寫。使用者要「壞產出不得取代 last-good」；「不另做 sidecar」是收窄 | sidecar 仍可能先截斷 dest 再 copy；AC-1 看的是目標檔本身 | `1-discussion.md:129-131` 目標檔位元組與 last-good 相同。收窄 `[Assumption]` | Scope 加上備份檔協議；SC-1 對照物變兩個路徑 | 待人審 |
| OC-4 | 路由表正本落 `notes/design/diagram-family-route.md`（五列，每列用這條／不用那條）。各家族「何時不用」只加反向指標，不把表抄五份。使用者要「一張表」；路徑鎖定是延伸 | 路徑不定 → 模板頂註與 agent 又各抄各的 | `1-discussion.md:92` 一張圖種路由表；現有契約都在 `notes/design/`。路徑 `[Assumption]` | 改掛 `_templates/` 或 README；SC-3 落點跟著變 | 待人審 |
| OC-5 | 本 feature branch **不**跑 `status-update.sh` 改正本 Active 列。merge 後由整合分支把 `diagram-ir-gate` 列成 Stage 2（若 #206 先合入 Stage 1 列則改 Stage 欄）。標**流程層** | 母版 STATUS 只在整合分支維護；腳本在 feature branch 拒改正本表列 | `docs/dev/STATUS.md:10-26`；`scripts/status-update.sh:408-415`；`1-discussion.md:121` | 本 PR 帶 STATUS 列改動，與並行 session／#206 互蓋 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 本 hop 不 bump plugin、不改現有家族契約正文（路由表是新短冊 + 反向指標，留給 Stage 6）。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口成 Decision。
- IR 信封方向：`family` ∈ `stage1-now`｜`stage2-arch`｜`behavior-flow`｜`dir-tree`｜`module-lifecycle`；payload = 該家族現有輸入（JSON 步驟／YAML purpose／md 節）。欄位 4-spec 再釘。
- Stage 3 不預先跳過；觸發判定留給第 3 站（本檔無「跳過 Stage 3」流程層 OC）。
- 本 hop 產審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES，不用 mermaid／ASCII `<pre>` 當圖。
- 人看決策用繁中；ID／fail-code／family token 維持英式。

## ADR 晉升檢查
- 難逆轉:否（G3 前可改本檔 Decision／OC；產器尚未落地）
- 反直覺:是（已有三套契約仍要再開 IR 閘；#191 ≠ 本閘）
- 真 trade-off:是（共用 IR 包裝 vs 各產器自管 vs 搬 Node）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-12 | owner chat「都過」核准 Stage 1 方向（wave-1 = IR 閘／路由表／Proof Lab；第一刀不是動畫）。本 hop brief 指定 Stage 2 收斂這三點。三決策點：IR 閘與原子交付／圖種路由／Proof Lab 落點。
- Stage 1 改口 | 2026-09-12 | 1-discussion 仍 draft、Q6／Q7 `[~]`、Q8／Q9 `[>]`；本檔改口為 Decision。不回改正本討論。N1 機械「status=approved」未寫入 1-discussion（Stage 1 未送 G1）；口頭方向核准 ≠ 本站 G1。
- G1 | 2026-09-12 | **未送**。`verdict` 空。Agent 不代填 Human PASS。審查者依序：適格人類 reviewer → fresh-context reviewer Agent → owner 自審(有記錄的最後手段)。
