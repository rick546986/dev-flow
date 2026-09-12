---
feature: diagram-ir-gate
stage: 1-discussion
status: draft
owner:
reviewers: []
updated: 2026-09-12
baseline: tip 67481d6
---

# 1. 討論 — 圖 IR 閘(Archify 吸收 wave-1)

> 用途:發散。**不做決定**。本場依 owner 2026-09-12 書面 brief 落檔,不是現場一問一答。
> Lane = **full**(新能力／契約)。本 hop **只 Stage 1、不送 G1**。未核敘述標 `[Assumption]`。
> 第一刀不是動畫;預設圖維持靜態直式 SVG。Owner Call／閘門留給人。

## Problem
痛:DevFlow 已有 vbox-fig／gate-twin／dir-tree 契約與 Python SVG 產器,但沒有機器可讀的 IR 驗證收據、圖種路由與可重放 Proof Lab;agent 混用家族,壞 HTML 會直接蓋掉上次好產出(#191 方向)。
現在怎麼繞:靠人背「何時不用」表、看 #191 之後的 WARNING／`<pre>` 後備、或分家族重跑牙再對眼。

## Context(已知事實)
- 直式步驟方塊(第 2 站方案架構、第 4 站模組生命週期)走 vbox-fig,產器 `scripts/build-vbox-fig.py`,牙 `scripts/check-vbox-fig.sh`:notes/design/vbox-fig-contract.md:L9-L12
- gate-twin 行為／方案圖的 ASCII→SVG 收口在 `parse_ascii_fig`／`render_vbox_svg`;樹狀 ASCII 改 WARNING + `<pre>`,禁靜默裁字／默丟高編號框:notes/design/vbox-fig-contract.md:L6-L7 notes/design/vbox-fig-contract.md:L26-L34
- 第 1 站審頁三框是另一家族(`#scan-now` viewBox 200×420),產器 `build-stage1-html.py`,不准手包 html-shell、不併進 vbox-fig:notes/design/stage1-review-ui-contract.md:L21-L30 _templates/1-discussion.md:L15-L20
- 第 2 站審頁方案架構是 Decision 後直式 SVG(`max-width:360px`),不是 mermaid／橫 ASCII／`<pre>` 當圖:notes/design/stage2-review-ui-contract.md:L23-L25
- 目錄包含樹是第三家族:手寫 YAML、monospace `├─`/`│`/`└─`、預設只露 L1;產器 `build-dir-tree.py`,牙 `check-dir-tree.sh`:notes/design/dir-tree-contract.md:L7-L15
- 全站看圖零依賴:靜態 inline SVG;禁 mermaid／外連圖／canvas: _templates/diagram-style.md:L5-L12
- vbox-fig 牙重放 `scripts/fixtures/vbox-fig/lifecycle.json`(四格:新生→改行為→退役→不動):scripts/check-vbox-fig.sh:L30-L32 scripts/check-vbox-fig.sh:L98-L105 scripts/fixtures/vbox-fig/lifecycle.json:L1-L9
- dir-tree 牙咬產器＋`guides/dir-tree-purpose.yaml` 與 `#dirmap` 同步;另有 `scripts/fixtures/dir-tree/good/purpose.yaml`:scripts/check-dir-tree.sh:L4-L6 scripts/fixtures/dir-tree/good/purpose.yaml:L1-L19
- #191 牙鎖在 `check-gate-twin.sh`:不得再有 `text[:42]`／`steps[:8]`;樹狀走 `mode=pre` 且帶 warnings:scripts/check-gate-twin.sh:L530-L555
- gate-twin 寫 html 是 `Path.write_text` 直接覆寫目標,沒有候選檔／last-good 守衛:scripts/build-gate-twin.py:L2327
- dir-tree 寫檔同樣直接 `write_text`:scripts/build-dir-tree.py:L574-L576
- 本 repo 正本 STATUS 表列只准在 `main` 用 `status-update.sh`;feature branch 拒改:scripts/status-update.sh:L409-L415 docs/dev/STATUS.md:L10-L26
- tip Active 目前只有 `integration-before-verdict`,Gates 仍 G1⬜:docs/dev/STATUS.md:L30-L34
- owner 2026-09-12 書面:本 slug = `diagram-ir-gate` full-lane;wave-1 只吸收 Archify 的 IR→驗證→原子交付、圖種路由表、Proof Lab fixture;第一刀不是動畫;預設靜態直式 SVG;本 hop 只 Stage 1

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 實作者／agent | 產出對家族、可審的圖 | 寫 md／跑產器 | 散落契約與產器 | 該走哪條、失敗碼、修法 | Cursor、終端機 |
| 審查者 | 打開 twin 就能信眼前這張 | 拒／要改;不代填 Human PASS | 產出 html | 候選是否蓋掉 last-good | 瀏覽器、PR |
| owner | wave-1 吸收、不動動畫／Node | 裁 G1／範圍 | 2026-09-12 brief、#191 | IR 形與 last-good 落點 | GitHub、Archify 頁 |
| CI／selftest | 三家族 fixture 可重放且綠 | 紅就擋合 | 各家族 `check-*.sh` | 統一收據／Proof Lab 目錄 | GitHub Actions |

### Current Journey
沒有本功能時的現況。正式 SOP 是各契約「何時用／何時不用」表;實際常憑記憶抄最近一份 html。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | agent | 憑記憶選圖家族、手寫 ASCII／YAML | 散落契約 | — | md 正本 | 家族混用 |
| 2 | agent | 跑對應產器 | `build-*-*.py` | — | html 被 `write_text` 蓋掉 | 壞圖取代好圖 |
| 3 | 牙 | 分家族重放 fixture | `check-vbox-fig`／`check-gate-twin`／`check-dir-tree` | — | 終端 PASS／FAIL | 無機器收據、三套各走各的 |
| 4 | 審查者 | 打開 twin 用眼看 | 瀏覽器 | agent 重產 | 無可對照的 last-good | 不知該信哪一版 |

### Workarounds
- 人背「何時不用」表(vbox-fig 不畫第 1 站三框;dir-tree 不進 `1-discussion.html`)。
- #191 之後:樹狀 ASCII 靠 WARNING + `<pre>` 原文,不再靜默裁 42 字／默丟 R-9+。
- 壞了就重跑產器、對眼;沒有候選檔、沒有 last-good。
- 這幾步常不留「這次失敗碼／修哪個旋鈕」紀錄。

### Exceptions
- 樹狀 ASCII:gate-twin 顯式降級 `<pre>`,不是常態 SVG。
- 第 1 站 dir-tree 可選、另檔,不進審頁三框。
- 手寫 html 或掃頁產器充審頁:契約禁,但產器本身不擋「壞輸出覆寫好檔」。
- `[Assumption]` 採用現場仍有人拿 mermaid／橫 ASCII 充直式圖(無採用 log;期限=Stage 2,過期擋 G2)。

### Evidence
- owner 書面 brief(本 session 2026-09-12):slug `diagram-ir-gate`;wave-1 = IR 驗證原子交付 + 路由表 + Proof Lab;第一刀不是動畫;預設靜態直式 SVG;本 hop 只 Stage 1;不送 G1;不碰 #196／#200／#201。
- 本 tree 已核:上列 Context 出處。
- #191 現象與方向:https://github.com/rick546986/dev-flow/issues/191 (已關;合入 #193)。
- Archify 公開 README(2026-09-12 抓取,非本 repo):https://github.com/tt-a1i/archify — typed JSON IR、validate／deliver `--json` 穩定 rule codes、`supportedFixes`、通過才原子取代 last-good、Proof Lab 重放 checked-in IR。本討論**不**把 Archify 的 Node 渲染棧當本 repo 事實。
- `[Assumption]` 現場仍混家族／手寫 html:無採用 log;期限 Stage 2。

## Goals
- G-out-1:產圖宣告完成時,壞輸出不能取代上次通過的產出;失敗帶穩定碼、主詞、可修旋鈕,不是堆疊或「再試一次」。
- G-out-2:人／agent 能查一張路由表,把 DevFlow 圖種(第 1 站現況、第 2 站方案架構、行為流程、目錄樹、模組生命週期)對到正確契約／產器,而不是抄最近一份。
- G-out-3:vbox-fig／gate-twin／dirmap 各有可重放 sample,重跑結果與現有 selftest 牙對得上(Proof Lab 形,不是另開視覺品味館)。

## Non-Goals(初稿)
- 不引入 Mermaid、黑盒自動排版、Node 渲染棧、hosted share、WYSIWYG。
- 不把動畫當預設(可選 trace 是後刀,不是本刀)。
- 不做 deep-link `#focus`／`#route`、Architecture Delta、主題切換、Share Card。
- 本 hop 不實作產器、不寫 Stage 2+、不送 G1、不 bump plugin／發版。
- 不動 open PR #196、#200、#201。

## Open Questions
- [x] Q1:第一刀是不是動畫?→ owner:不是;預設維持靜態直式 SVG
- [x] Q2:wave-1 做哪三件?→ owner:IR→驗證→原子交付;圖種路由表;三家族 Proof Lab fixture
- [x] Q3:Mermaid／Node 渲染／hosted share／WYSIWYG 進本 slug 嗎?→ owner:否
- [~] Q4:吸收=把 Archify 閘門想法做進現有 Python 產器,不搬 Node schema?(帶假設:是;期限=Stage 2 對帳,過期擋 G2)
- [~] Q5:路由表只鎖上列五個 DevFlow 家族,不把 Archify 的 architecture／sequence／dataflow 當本波必做圖種?(帶假設:是;期限=Stage 2)
- [>] Q6:IR 具體形(既有 JSON fixture 擴、還是新 schema)?→ 移交 Stage 2;Owner Call
- [>] Q7:last-good 存在哪、失敗碼穩定表誰拍板?→ 移交 Stage 2;Owner Call
- [>] Q8:可選 trace、deep-link、Delta、主題、Share Card 何時開刀?→ 移交後續 slug,本討論不解

## Constraints
- 預設圖=靜態直式 SVG;看圖零依賴。
- 表列只准 `scripts/status-update.sh` 在 `main` 寫。本 feature branch 已實跑拒改;合主後再 upsert Active。
- 本 PR 不宣稱 G1／Human PASS;`status` 留 draft;Owner Call／閘門留給人。
- 不改 #196／#200／#201 的檔、不重寫 integration-before-verdict。
- 本 hop 只准 `docs/dev/diagram-ir-gate/1-discussion.md` + 產器吐的 html。

## 驗收雛形
- AC-1(G-out-1):假設上次產出已通過牙,當這次輸入／渲染失敗,則目標檔仍是上次通過的那份,並留下穩定失敗碼與可修旋鈕。
  - 從哪看:產器 stdout／stderr 的機器可讀收據(或同等檔);目標 html 的內容／hash
  - 看到什麼算對:目標 hash 與失敗前相同;收據有穩定碼+主詞+修法;不是「Wrote …」卻換成壞頁
  - 拿什麼試:故意壞 IR／錯家族輸入,對一個已綠的 fixture 目標
- AC-2(G-out-2):假設人要畫「第 1 站現況／第 2 站方案架構／行為流程／目錄樹／模組生命週期」之一,當查路由表,則只對到一個契約+產器,且「何時不用」指向其他家族。
  - 從哪看:本 slug 後續落地的路由表(文件或機械表)
  - 看到什麼算對:五列皆有唯一去處;第 1 站三框不指向 vbox-fig;目錄樹不指向 `#scan-now`
  - 拿什麼試:上列五個圖種名稱各查一次
- AC-3(G-out-3):假設人重放 Proof Lab 的 vbox-fig／gate-twin／dirmap sample,當跑現有對應 `check-*.sh`(或等價入口),則結果與現 selftest 一致。
  - 從哪看:Proof Lab 目錄 + `check-vbox-fig.sh`／`check-gate-twin.sh`／`check-dir-tree.sh` 輸出
  - 看到什麼算對:sample 路徑對得上現 fixture;綠的仍綠、刻意壞的仍紅;不是另做一套對不上牙的展示頁
  - 拿什麼試:現成 `scripts/fixtures/vbox-fig/lifecycle.json`、`scripts/fixtures/gate-twin/fig-tree-ascii`、`scripts/fixtures/dir-tree/good/purpose.yaml`

## 現況圖
誰:agent
做什麼:憑記憶選圖
工具:散落契約
痛點:家族混用
↓
誰:產圖器
做什麼:直接覆寫 html
工具:write_text
痛點:壞圖蓋好圖
↓
誰:審查者
做什麼:打開 twin 對眼
工具:瀏覽器
痛點:無收據可判

## 邏輯圖(ASCII)
```
now
|-- pick family by memory
|-- builder write_text
|-- teeth per family (no receipt)
+-- reviewer eyes only     [bad can replace good]
wave-1 (this slug; not decided how)
|-- typed IR -> validate -> atomic deliver
|-- routing table (5 DevFlow families)
+-- Proof Lab == replay selftest fixtures
later knives (not this)
|-- optional trace
|-- #focus / #route / Delta / theme / share
+-- Node / mermaid / WYSIWYG   [explicit no]
```

## Interview Log(推理鏈外顯)
- Q:為什麼現況已經有契約＋牙,還會「壞圖蓋好圖」?
  - 事實:scripts/build-gate-twin.py:L2327 scripts/build-dir-tree.py:L574-L576 notes/design/vbox-fig-contract.md:L32-L34
  - 推理:#191 修的是靜默裁字／默丟框。寫檔仍是直接覆寫。樹狀降級能保住可讀原文,但不能保住「上次通過的 SVG」不被這次壞跑蓋掉。
  - 結論:CONFIRMED 缺的是驗證後才原子交付,不是再寫一份「不准混用」散文。
- ⚠️ Q:第一刀為什麼不是動畫?
  - 事實:_templates/diagram-style.md:L5-L12 notes/design/stage1-review-ui-contract.md:L23-L26
  - 推理:母版已鎖靜態 inline SVG、直式三框／直式方塊。動畫改的是呈現,不擋混家族與覆寫。owner 書面:第一刀不是動畫,預設維持靜態直式 SVG。
  - 結論:CONFIRMED 本 slug 預設圖維持靜態直式 SVG;可選 trace 移交後刀。
- Q:路由表要對哪些家族,才叫 wave-1 而不是另造圖種?
  - 事實:notes/design/stage1-review-ui-contract.md:L21-L30 notes/design/stage2-review-ui-contract.md:L23-L25 notes/design/vbox-fig-contract.md:L9-L12 notes/design/dir-tree-contract.md:L7-L15
  - 推理:現場痛是五個已存在的 DevFlow 槽位互相搶。Archify 的 architecture／sequence／dataflow 是另一套圖種,owner 沒把它們列入本波必做。
  - 結論:CONFIRMED 路由表主詞是第 1 站現況、第 2 站方案架構、行為流程、目錄樹、模組生命週期。
- Q:Proof Lab 能不能另做展示頁、不對現有牙?
  - 事實:scripts/check-vbox-fig.sh:L98-L105 scripts/check-gate-twin.sh:L530-L555 scripts/check-dir-tree.sh:L4-L6
  - 推理:三家族已有可重放 fixture。另做對不上牙的館,會變成第二套品味,重演「兩套圖、不知信誰」。
  - 結論:CONFIRMED Proof Lab sample 必須對齊現 selftest,不是新視覺館。
- Q:吸收 Archify 是不是等於引入 Node 渲染棧?
  - 事實:_templates/diagram-style.md:L9-L12
  - 推理:母版禁外部庫。owner 把 Mermaid／Node／hosted share／WYSIWYG 列為本 feature 明確不做。公開 README 的 IR／收據／原子交付是想法來源,不是本 tree 依存。
  - 結論:CONFIRMED 本討論不引入 Node 渲染棧;`[Assumption]` 後續用 Python 產器承接閘門想法,Stage 2 對帳。
- ⚠️ Q:哪些題必須留給人,agent 不得代填 PASS?
  - 事實:docs/dev/STATUS.md:L30-L34 scripts/status-update.sh:L409-L415
  - 推理:owner 明示本 hop 只 Stage 1、不送 G1、Owner Call／閘門留給人。IR 形與 last-good 落點會鎖契約,屬難逆轉。
  - 結論:CONFIRMED Q6／Q7 留 Owner Call;本檔 `status: draft`;不寫 G1 PASS。
- Q:本 hop 能不能改 STATUS Active?
  - 事實:scripts/status-update.sh:L409-L415 docs/dev/STATUS.md:L10-L26
  - 推理:腳本在本 branch 實跑 exit 2。手改表列會讓章對不上。
  - 結論:CONFIRMED 本 PR 不改 STATUS;合主後用腳本 upsert `diagram-ir-gate` Active。
- Q:若不管路由、只做原子交付,混家族會不會自己好?
  - 事實:notes/design/vbox-fig-contract.md:L77-L86 notes/design/dir-tree-contract.md:L7-L10
  - 推理:原子交付只擋壞檔覆寫。agent 仍可能拿 vbox-fig 畫第 1 站三框、拿步驟方塊畫目錄樹。#191 就是錯輸入形進錯收口。
  - 結論:CONFIRMED 路由表與原子交付是兩件,wave-1 都要;what-if「只做其中一件」不能收斂本痛。
