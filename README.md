# dev-flow — 開發流程 SOP

> AI 協作的開發流程。這個 repo 同時是方法論母版,也是 Claude Code plugin。
> marketplace、plugin、repo 都叫 `dev-flow`。裝法見 [`docs/PLUGIN.md`](docs/PLUGIN.md)。
>
> 新專案:裝好 plugin,進專案打 `dev-setup`。它會把模板、本 README、契約檔與
> gauntlet 腳本放到 `docs/dev/`,建 `STATUS.md`,並建 Agent Memory
> (`.dev-flow/` 進 Git;本機 SQLite 是快取,見 [§16](#16-agent-memorydev-flow))。
> 不必手抄,也不必把這個 repo 放在你機器上。
>
> **環境**:hook 要 python3(只吃標準函式庫,最低 3.9)。找直譯器的順序是
> `DEVFLOW_PYTHON` → `/usr/bin/python3` → PATH 上的 `python3`。找不到就印警告後放行
> —— 那次呼叫沒有守衛,不是功能壞掉。Windows(Git Bash)沒有 `/usr/bin/python3`,
> 要另外裝 Python,或設 `DEVFLOW_PYTHON`。
>
> 維護本 repo 才要多裝 `markdown-it-py==4.0.0`
> (`pip install -r scripts/requirements-methodology-render.txt`)。hook 不 import 它。
>
> **Windows 已知限制**:本 repo 的 selftest / `devflow-check.sh all` 在 Windows 上
> 跑不全綠(Git Bash 的 `/tmp` 與原生 Python 看到的路徑不是同一個)。發版不要在
> Windows 上做。細節見 [`notes/dispatch-windows-parity.md`](notes/dispatch-windows-parity.md)。

**這是什麼**:討論 → 決策 → 規格 → 實作 → 驗證,全程留檔。每個 feature 走 7 份文檔、
過 3 道 gate。AI 寫,人拍板。

本檔是**入口／索引**。細節跟下面四層的鏈走,不要在這裡再抄一遍。

## 你是誰,該讀哪裡

本檔是入口。先認四層,再按下表跳,不要從頭讀。

去哪:[quickstart](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html) · [七階段圖](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#flow)

| 層 | 做什麼 | 去哪 |
|---|---|---|
| **本檔** | 入口。契約句留這裡 | 下表跳 |
| **quickstart** | 怎麼走、守衛怎麼辦 | [guide-quickstart](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html) |
| **flow guide** | 各站清單、Gate、檔案地圖 | [guide-dev-flow](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html) |
| **talk guide** | 第 1 站 12 步、白名單 | [guide-dev-talk](https://rick546986.github.io/dev-flow/guides/guide-dev-talk.html) |
| **`skills/dev-flow/SKILL.md`** | 執行入口,不是手冊 | plugin 裡那份 |

| 你是誰 | 從這裡開始 | 先別讀 |
|---|---|---|
| **第一次用** | [quickstart](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html) · [七階段圖](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#flow) · [§0](#0-一張圖) | §5 之後的契約句 |
| **要查一條規則** | 下表跳 | 從頭順讀 |
| **要改 dev-flow 本身** | [§17](#17-附錄跨-repo-與非-feature-入口) 結構圖 → [§7](#7-角色與-gate) | 不看 guide 就改 §7 |

**想知道什麼**:

- G1/G2/G3 各要什麼條件才過 → [§7](#7-角色與-gate)
- 這件事該走 full 還 fast → [§2](#2-兩軌lane)
- 七份文檔各放什麼 → [§3](#3-七份文檔用途一句話骨架見-_templates填好範例見-example)
- 哪個檔給人看、哪個給 Agent → [§1](#1-文件地圖四象限-status-看板)
- 實作期怎麼推進、偏差怎麼判 → [flow `#stage6`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage6)
- 守衛擋我了怎麼辦 / 並行怎麼開 → [quickstart ③](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html#guardcheat)
- 哪一站用哪個模型 → [quickstart ④](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html#models)
- 哪些階段要另開 session → [quickstart](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html)
- 為什麼討論不能知道下游 → [flow `#fence`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#fence)
- html twin 每站要放什麼圖 → [§6](#6-html-twin可視化-artifact)
- 案子太大要不要切 → [flow `#large-work`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#large-work)
- R/S/T/D/F 這些 id 怎麼串 → [§4](#4-id-追溯鏈)
- 某條規則到底誰在擋 → [flow `#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates)
- Agent 的長期記憶怎麼運作 → [§16](#16-agent-memorydev-flow)
- 跨 repo / 非 feature 的事怎麼辦 → [§17](#17-附錄跨-repo-與非-feature-入口)

母版 `dev-flow/` ASCII 目錄樹在 [§17 附錄](#17-附錄跨-repo-與非-feature-入口)(手機可跳;樹內路徑字串沒改)。

線上看:[quickstart](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html)、
[七階段圖](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html)、
[dev-talk](https://rick546986.github.io/dev-flow/guides/guide-dev-talk.html)、
[決策列表](https://rick546986.github.io/dev-flow/docs/adr/)、
[改版歷史](https://rick546986.github.io/dev-flow/docs/dev/HISTORY.html)。
repo 內任一 html 都可把路徑接在 `rick546986.github.io/dev-flow/` 後打開。

**採用方式**:最低配是把模板複製進專案、人工照本 README 走流程;裝 plugin 後可用
`/dev-talk`、`/dev-flow`、`dev-setup`、`/dev-release` 指令自動導引與守衛。

## 0. 一張圖

七站一條路,三道閘。3 是選配。

去哪:[七階段 SVG](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#flow)

```text
想法
  ↓
1 討論
  ↓
2 決策  → G1
  ↓
3 原型(選配)
  ↓
4 規格  → G2
  ↓
5 任務
  ↓
6 實作
  ↓
7 驗證  → G3
  ↓
PR
```

## 1. 文件地圖(四象限 + STATUS 看板)

人看的跟 Agent 看的是兩套出口。同一個意思不要抄兩份。

去哪:[flow `#filemap`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#filemap)

| 給誰 | 放哪 | 幹嘛 |
|---|---|---|
| **人** | `docs/dev/<slug>/1–7`、`STATUS.md`、`HISTORY.md`、`docs/adr/`、`docs/specs/` | 討論、拍板、考古、看現況 |
| **Agent** | `.dev-flow/`(進 Git)+ 本機 SQLite 快取 | 長期記憶。禁手改。細節 [§16](#16-agent-memorydev-flow) |

可點的人頁:[決策列表](https://rick546986.github.io/dev-flow/docs/adr/) · [改版歷史](https://rick546986.github.io/dev-flow/docs/dev/HISTORY.html)。
`*.md` 才是 git 正本。html 用 `python3 scripts/build-public-docs.py` 重生。
不要把 ADR 正文抄進 `.dev-flow/decisions`,也不要把 yaml 當成人頁。

| 檔 | 回答什麼 | 生命週期 | 誰寫 / 誰讀 |
|---|---|---|---|
| `.dev-flow/`(repo root) | **Agent Memory**:這個詞是什麼意思(domain)、現在實際怎麼運作(implementation truth)、打算往哪走(intent)、當初為何這樣選(decision)、怎麼做某件事(skill)、以前發生過什麼(event) | 永生,可 Git 同步 | dev-talk 確認後由 `dev-memory.py` 寫入(**禁手改**)/ 全隊 + 每個 AI session(見 [§16](#16-agent-memorydev-flow)) |
| `docs/specs/<domain>.md` | 系統**現在**的行為(唯一真相) | 永生,只由階段7出口併入 | 7-Exit / 動這塊前必讀 |
| `docs/adr/NNNN-slug.md` | 當初**為何**這樣選。人頁見 [決策列表](https://rick546986.github.io/dev-flow/docs/adr/) | 永生,可 superseded | 2-decision 晉升 / 想翻案的人 |
| `docs/dev/STATUS.md` | 誰正在做什麼、還有什麼沒做 | 常駐看板,做完的移出 | 每過 gate 更新 / 全隊 |
| `docs/dev/HISTORY.md` | **做過什麼、當初為什麼做**。人頁見 [改版歷史](https://rick546986.github.io/dev-flow/docs/dev/HISTORY.html) | 永生,只增不改(append-only) | ship 時由 `history-append.sh` 追加(**禁手改**)/ 想知道某件事怎麼變成現在這樣的人 |
| `docs/dev/<feature>/1-7` | 這次變更的完整生命週期 | ship 後封存 | 流程產出 / reviewer + 考古 |
| `.claude/rules/*.md` | 架構不變量/技術慣例/坑(Claude Code 官方規則路徑,無 `paths` frontmatter 者每 session 自動載入) | 永生 | setup 產草稿 / 全員+執行引擎;**只放 gotchas,禁流程規則(§11),spec 不重抄**;CLAUDE.md 對應段改指標避免雙正本;檔案長大(>~100 行)或多技術棧時可用 `paths:` frontmatter 做 path-scoped 按需載入(判準見模板頂註) |

`.devflow/`(少一個連字號)是執行期暫存,不進 Git。本機 SQLite 是快取,不是第二份正本。

**歸位規則**(init 與全程):文檔不散落 `docs/` 根。

| 這種東西 | 歸到哪 |
|---|---|
| living 規格 / 規則 / 資料字典 | `docs/specs/` |
| feature 過程檔(1–7) | `docs/dev/<slug>/` |
| 長命決策 | `docs/adr/` |
| 流程外草稿 | `docs/dev/<slug>/0-draft-<名>.md` —— **只當 Stage 2 原料,不得跳關當 spec** |

既有散檔由 /dev-flow init 偵測,徵得同意後 `git mv` + 同步全部引用(code 註解/文檔/
CLAUDE.md;舊路徑 grep 歸零才算完)。

## 2. 兩軌(lane)

拿不準就走 Full。Fast 省的是 Stage 1–3,不是 Stage 5。

去哪:[flow `#flow`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#flow)

> **契約**
>
> **Full**:新能力 / 不可逆改動 → 1→7 全套(3 選配),過 G1 G2 G3。
> **Fast**:bugfix / ≤2 檔小改 / 行為已有 spec → `4-spec` → `5-tasks` → `6-notes` → `7-review`,過 G3(spec 改動大再補 G2)。

| | Full lane | Fast lane |
|---|---|---|
| 判準 | 新能力 / 不可逆改動(schema、API 契約、跨模組介面) | bugfix / ≤2 檔小改 / 行為已有 spec 條目(可逆的跨模組小改也算) |
| 文檔 | 1→7 全套(3 選配) | `4-spec`(補 bug scenario) → `5-tasks`(mini) → `6-implementation-notes` → `7-review`(mini) |
| Gate | G1 G2 G3 | G3(spec 改動大再補 G2) |
| 起手式 | Stage 1 討論(`/dev-talk`) | **診斷迴圈**(mattpocock×superpowers 聯集):重現 → 最小化 → 假設 → 驗證定位 → 修 → 回歸測試 |
| bug scenario 從哪來 | — | 從「重現步驟」直接長出:GIVEN=重現前置 / WHEN=觸發 / THEN=正確行為。**修根因,禁 symptom patch** |
| Stage 5 | 兩軌同一份 `_templates/5-tasks.md` | **不省略**;可只有一個 T,但 `Covers`/`Files`/`Verify`/`Blocked-by` 四欄必填 |

拿不準 → Full。Fast 省的是 Stage 1–3,不是 Stage 5:`devflow-exec.sh start` 少一欄就開不了工。

## 3. 七份文檔(用途一句話;骨架見 `_templates/`,填好範例見 `example/`)

七份檔,各卡一道閘。表是摘要;Gate 條件全文在 §7。

去哪:[flow `#checklists`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#checklists) · [flow `#stage2`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage2)–[`#stage7`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage7)

| # | 檔 | 用途 | Gate |
|---|---|---|---|
| 1 | `1-discussion.md` | 發散:把「不知道自己不知道」變成可收斂的問題清單。不做決定 | Open Questions 全解或明標假設 |
| 2 | `2-decision.md` | 收斂:2-3 方案比較 → 選定 + rejected + 理由 | **G1** 方向核准 + OC 全裁決(全文見 §7) |
| 3 | `3-prototype.md` | 選配:throwaway 實驗回答技術/UI 疑問,答案回寫 2-decision。 | 答案回寫 2-decision + frontmatter 收尾同步(終態 approved) |
| 4 | `4-spec.md` | 本次變更的可測契約(delta + GIVEN/WHEN/THEN)。SDD 真相 | **G2** R/S 全審 + DD 全裁決 + Verification Profile + Demo verdict(全文見 §7) |
| 5 | `5-tasks.md` | 切成可勾選任務,tracer-bullet 順序,每 T 有 Covers/Files/Verify/Blocked-by | 每 T 欄位完整 |
| 6 | `6-implementation-notes.md` | 實作日誌:TDD 證據 + 偏差記錄 | 每 T review PASS + 全 S 綠 |
| 7 | `7-review.md` + `.html` | 雙軸審 + coverage matrix + Exit checklist;出貨樹=審過的樹。 | **G3** 本次 S 全綠 + 回歸綠 + 現象證據 + Evidence 契約全過(全文見 §7);PASS → Exit Checklist(PR 是其中一項) |

**執行清單四原則**正本在 [flow guide 清單章](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#checklists)(①todo ②自檢 ③禁跳併 ④達不成回上游)。清單全文住各模板頂註。Stage 1 同款機制內建於 `/dev-talk`,下一跳看 `graph.yaml`,見 [§8](#8-每階段呼叫的技能ai-對照表)。

**Design Boundary Contract**(4-spec 內的條件式章節,不是第八份文檔):補的是
4-spec(可測契約)到 5-tasks(可勾選任務)之間缺的設計邊界。
**十一條觸發條件任一命中即必填,全未命中才可 `n-a` + 具體理由(Fast lane 不豁免)**;
條件全文與判準**不在此重抄** ——
操作用清單在 `_templates/4-spec.md` 該節頂註,
語意判準與好壞範例在 `notes/design/design-boundary-contract.md`(母版 repo,唯一語意正本);
兩份由 `scripts/check-design-contract.sh` 機械比對。由既有 G2 一併審(gate 條件正本仍是 §7)。

## 4. ID 追溯鏈

每張票用同一個 id 串起來,裁決用的 OC/DD 不進這條鏈。

去哪:[flow `#filemap`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#filemap)

`R-n`(requirement,4-spec)→ `S-n`(scenario,4-spec)→ `T-n`(task,5-tasks,標 Covers)
→ 測試名含 S-id(6 實作)→ `D-n`(deviation,6)→ `F-n`(finding,7,標影響的 S/T)。

裁決用 ID **不入鏈**:`OC-n`(2-decision)、`DD-n`(4-spec)不被 T 實作。

## 5. 實作期鐵則

每個 T 同一條路:紅 → 綠 → 審查 PASS 才算做完。

去哪:[flow `#stage6`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage6)
· [quickstart Stage 6](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html#walkthrough)
· 守衛怎麼辦見 [quickstart ③](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html#guardcheat)。

契約 / 檢查器抽(Stage 6 seam):

```text
RED → GREEN → scope check → Verify
→ independent T review
→ PASS
→ commit
→ Progress Log + checkbox + review evidence
```

T 在獨立審查 PASS 前一律未完成。分不清 L1/L2 → 一律當 L2。

契約 / 檢查器抽(七支掛載 hook 名):

掛載中的 hook 必須被點名:`devflow-guard`、`devflow-prebash`、
`devflow-dispatch-guard`、`devtalk-guard`、`devflow-report-guard`、
`devflow-postbash`、`devflow-plainspeak`(另有 `history-guard` 守 HISTORY,不受旗標影響)。
L1 出口 = `devflow-exec.sh allow`;L2 = `stop`。

**驗證五律**(適用 T 執行、T review 與各 gate):
1. **證據 = 原始輸出**:完成/通過必附原始指令輸出或 檔案:行號。
2. **派工者不下場修**:修復一律重派執行者、重新送審。
3. **反預判禁令**:派工 prompt 禁止預先框定 reviewer 判斷。
4. **HITL 不可代答**:gate / Owner Call / L2 不得由 agent 代答。
5. **失敗先分類再路由**:SPEC → L2;ENV → 修環境不計升階;IMPL/UNKNOWN → [§9](#9-模型分層與-effortai-執行時) 升階。同 T 上限 4(haiku 1 + sonnet 2 + opus 1)。

**自判分層**:
| 名 | 誰拍 | 住哪 |
|---|---|---|
| Decision(方案決策) | **人** | 2-decision |
| Owner Calls(自判裁決) | owner,G1 全裁決 | 2-decision |
| Drafting Decisions(草擬自判) | 模型,G2 全裁決 | 4-spec |
| Split Decisions(拆分自判,選配) | 模型 | 5-tasks |
| Decisions(實作自判) | 模型,7 審對照 | 6-notes |

**不對稱保護(第 6 型)**:新增只對某個 stage/檔/群組的保護時,同一個 commit 必須說明為什麼其他同類不需要。
**不對稱記帳(第 7 型)**:任何「為了驗證而列舉某個機械事實」的清單,必須有守衛對著機械正本對帳;沒有守衛釘著的清單不得寫死數字。

## 6. HTML twin(可視化)+ Artifact

md 是 git 正本,html twin 是給人審的殼。gate 時必產。

去哪:[flow `#filemap`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#filemap)
· 各站審查形狀見 [flow `#stage2`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage2)–[`#stage7`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage7)
· 討論站視覺版見 [talk `#visual`](https://rick546986.github.io/dev-flow/guides/guide-dev-talk.html#visual)。

契約 / 檢查器抽(審查動線頂區五格;標籤逐字釘死,由 `check-gate-twin.sh` 驗):

| 站 | 五格內容(標籤逐字釘死,由 `check-gate-twin.sh` 驗) |
|---|---|
| **2-decision(G1)** | 判定(`## Decision` 首句)/ Owner Calls(已裁決 `x/y`)/ 方案(幾項待審)/ 駁回理由(幾條)/ 狀態(frontmatter) |
| **4-spec(G2)** | 狀態(frontmatter)/ 待審 S(幾條 + **幾條缺觀測欄**)/ lane · Risk / DD 進度 `x/y` / Demo verdict(承接 3-prototype) |
| **7-review(G3)** | 判定(frontmatter `verdict:`)/ 出貨(Exit Checklist `x/y`)/ 爭點(「附錄:本輪特有」幾條)/ 風險(Known Limits 幾條)/ 抽驗(Coverage Matrix 中位列 `檔:行`,決定論、可重現)|
| **5-tasks(執行板)** | 狀態(frontmatter)/ 任務(幾個 T + 幾條缺必填欄)/ 模式(execution.mode,未標=sequential)/ 依賴(幾條 Blocked-by 邊)/ 進度(可勾計數) |

## 7. 角色與 Gate

三道閘。粗體詞是過關條件,檢查器在抽,不要改字。

去哪:[flow `#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates)

> **本節 = gate 條件(G1/G2/G3)的契約句**。各一句過關條件在下;全文、強制力對照、回滾導覽見
> [flow `#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates)。
> 改任何 gate 條件先改這裡的粗體 token 與錨定義,再同步三處摘要:①plugin `dev-flow`
> SKILL.md 階段動作表 ②本 README §3 七份文檔表 ③對應模板頂註。衝突以本節為準。

契約 / 檢查器抽(四眼與 reviewer 選法;下列第一條 `- ` 原文勿改):

- **author ≠ approver**:G1/G2/G3 的核准者不可以是該文檔的 owner(四眼原則)。
- **審查者產生**:G1/G2/G3 一律依序選 **適格人類 reviewer → fresh-context reviewer
  Agent → owner 自審(有記錄的最後手段)**。Agent 必須是乾淨 context,只給審核對象+基準+回報格式,不給
  作者結論;verdict 與審者身分記 reviewers 欄(如 `[independent-fresh-context-reviewer]`)
  + 檔內留 round 紀錄。owner 自審僅能作為**有記錄的最後手段**,不假裝有四眼。
- **規劃層 git**:每過一個 gate,把該階段文檔 commit 一次,只含文檔。Stage 1–5 落在整合分支;Stage 6 才開 feature branch。細節見 [flow `#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates)。
- 機械錨點註記:以下 G1/G2/G3 定義句內的粗體詞組是 gate-consistency 機械比對錨;增改 gate 條件務必加粗。

 ### G1

方向對不對。2-decision 過了才能往規格走。

去哪:[flow `#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates)

契約 / 檢查器抽:

G1 = 方向對不對(2-decision:方向核准 + **Owner Calls 全裁決**,有未裁決 OC
  不得過;下層內部技術項告知即可,但 reviewer **須抽查下層清單有無該上未上的
  誤放** —— 抽查是規則要求,不是 reviewer 自由心證)。

 ### G2

契約寫得對不對。4-spec 的 R/S、DD、Profile、Demo 都要過。

去哪:[flow `#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates)

契約 / 檢查器抽:

G2 = 契約寫得對不對
  (4-spec:**R/S 全審 + Drafting Decisions 全裁決** + **Verification Profile**
  + **Demo verdict**,有未裁決項不得過;兩錨的條件式定義見下方「G2 錨定義」)。

- G2 錨定義(錨句在上;此處為條件式全文):
  - 「Verification Profile」:G2 必須確認 4-spec Verification Profile 已依 lane 正確
    填寫 —— full lane = 完整 Profile(Feature Risk/Failure Model/Negative Constraints/
    Required/Conditional/Explicitly Excluded/Final Fresh Entry Point);fast lane =
    最小 Profile(五欄,見 4-spec 模板);命中「自動升 Full」清單(見 4-spec 模板)
    仍寫 fast → 不得過。`lane: fast` 配 `Risk: high` → Runtime(start 時)、模板檢查
    與 Gate 一律拒絕,例外僅限 Owner Call 明示。
    Reliability triage 不計入上述五個最小 Profile 欄位,但 full 與 fast lane 都必須回答
    Concurrency、Idempotency、Timeout/retry 三問(格式與規則見 4-spec 模板);fast lane
    多半三項皆 `n-a`,理由仍不得省。本項由本 repo 腳本驗欄位存在與理由非空,理由是否
    成立仍是 G2 reviewer 的判斷,無 Runtime 機械強制。
  - 「Demo verdict」(條件式):無 Stage 3 trigger → N/A + 明確原因,可過 G2;
    有 trigger 且完成 Demo → 必須 `Human verdict: ACCEPTED`;REVISE → 不得過 G2,
    必須重做 Demo;NOT_REVIEWED → 不得過 G2;有 trigger 但跳過 → 必須有 Owner Call
    明示。Agent 不得自行填入 ACCEPTED;Runtime 必須拒絕 Agent 自產的 ACCEPTED。

 ### G3

做出來的對不對。測試綠不夠,還要現象證據跟 Evidence 八點。

去哪:[flow `#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates)

契約 / 檢查器抽:

G3 = 做出來的對不對(7-review:**本次 S 全綠** **+ 既有測試套件全綠**(回歸義務)
  **+ 現象證據逐 S 相符** + **Evidence 契約全過**(八點定義見下方「G3 錨定義」)——
  reviewer 照 4-spec 的「觀測方式」親自實跑,測試綠不等於看得到它動起來)。

契約 / 檢查器抽(G3 錨定義八點;Gauntlet 版本句原文勿改):

- G3 錨定義:「Evidence 契約全過」= 以下八點全部成立:
  1. Final Fresh Run 綁定目前受審的 source SHA,且該 SHA 必須等於送審當下 HEAD;之後任何程式碼 commit 作廢 G3,必須重跑 Final Fresh。
  2. 所有 Required Layer = pass。
  3. 所有已觸發的 Conditional Layer = pass。
  4. 不得存在任何 fail。
  5. Required Layer 不得為 unverified 或 n-a。
  6. Explicitly Excluded Layer 可為 n-a,但必須附理由。
  7. Optional Layer 可為 unverified,但必須誠實標示。
  8. Gauntlet PASS 不取代 Standards Axis / Spec Axis / Operational Walkthrough /
     Coverage Matrix / 真實現象複驗。

  八點中的 Evidence 文件契約由 `scripts/devflow-evidence-gauntlet.sh`(1.3.3,E1–E13;
  採用專案散發於 `docs/dev/tools/`)機械驗證;第 2、5 點由 Gauntlet 讀 4-spec
  Verification Profile 的 Required layers(旗標 `--require-layer` 只能加嚴,不能拿掉
  Required;漏帶不再 fail-open;`--review-file` 找不到 Profile 亦不得退回 1.2.0;
  Profile 必須有 Required layers 欄,可寫「無」/none/n-a;缺欄或空值都紅;層名
  strip 後全等,不得 substring;`--profile` 只准本 feature
  的 4-spec,不得跨份覆寫)。
  第 3 點:Evidence 表已列且非 n-a 的 Conditional
  必須 pass;未列入視為未觸發,仍由 Reviewer 核對 Profile 條件。第 1 點的 HEAD
  綁定:`--review-file` 漏帶 `--source-sha` 時預設當下 HEAD;`docs/dev/<feature>/7-review.md`
  即使顯式傳 `--source-sha` 也必須等於 HEAD(example/ 與 scripts/fixtures/ 不套)。
- frontmatter 是狀態機:`draft → in-review → approved → superseded/shipped`。

### 強制力對照(誰在擋)

「規則存在」不等於「Runtime 會擋」。

去哪:[flow `#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates)

本 repo 的 reference test 全綠 ≠ 外部 Runtime pass。Gauntlet 只驗 Evidence 契約,
自己不跑專案測試。

### 合併後出事怎麼辦(整合分支回滾) · 機械契約,可跳

合併後出事,預設 revert,不要硬補。下面算法只在「直接補修」例外才用,可跳。

去哪:[flow `#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates)

> **契約 / 檢查器抽**
>
> 預設 `git revert -m 1 <merge commit>`;禁對整合分支 `reset --hard` /
> `push --force` / `rebase`。例外「直接補修」必須同時滿足:①一個 commit 修得完;
> ②補修 diff 與「其他 feature 碰過的檔」零交集。

契約 / 檢查器抽(直接補修算法;順序與原文勿改):

「其他 feature 碰過的檔」的定義(判準②用):**目前列在 `docs/dev/STATUS.md` Active
表裡的每個 feature 各自改過的檔的聯集**。逐列判定順序**寫死如下,不得跳步、不得倒序**:

1. `git fetch` 後先把**整合分支**釘成 SHA(它是活的 ref,算到一半被人推新東西
   就前後不一致)。
2. **Stage 1–5 且 `Branch` 欄逐字等於 `n-a:尚未建立 branch` 才跳過**(還沒有程式碼
   改動,本來就沒有戰場);Stage 1–5 但那欄不是這個 sentinel(或空)→ fail-closed
   停下問人,不當「跳過」。
3. **Stage 6 一律 fail-closed**:Active 表只要還有另一個 feature 的 `Stage` 是
   `6-implementation`(或同義的 Stage 6 值),就**不准用「直接補修」判準** ——
   執行中的 feature 本地可能還有未 commit/未發布的工作,remote 天生不能證明完整
   戰場。不要嘗試靠猜最新 T 補洞;走上面的預設回滾,或等它到 Stage 7。
4. **只有 Stage 7 的列才進 mode/ref/SHA 驗證**,而且全部讀 pinned remote tree:
   - 該列 `Branch` 的 remote ref 用 `git rev-parse --verify` 釘成單一
     `<remote-tip>`;後續 mode、Progress Log 與 diff **全部讀這個 SHA,不准讀目前
     main checkout 裡可能尚未合併的舊副本**。
   - `Feature` 連結只用來導出該 feature 的相對路徑;兩份文件分別用
     `git show <remote-tip>:docs/dev/<slug>/5-tasks.md` 與
     `git show <remote-tip>:docs/dev/<slug>/6-implementation-notes.md` 取得。
     任一路徑不存在、逃出 feature 目錄或讀取失敗 → fail-closed 停下問人。
   - **mode 的唯一資料源是上面 pinned tree 讀出的 `5-tasks.md` frontmatter
     `execution.mode`**,不是 STATUS 的 `Lane` 欄(full/fast 跟
     sequential/parallel 是兩件事)。整塊缺省視為 `sequential`;明寫 `parallel`
     一律 fail-closed 停下(本輪未定義 parallel 供補修計算的 canonical
     integration ref);連結/檔案/frontmatter 無法解析也停。
   - **sequential**:從 pinned tree 的 6-notes **Progress Log** 讀出**每一個**
     ACCEPTED T 的 commit SHA,逐個通過
     `git merge-base --is-ancestor <accepted-sha> <remote-tip>` 才算發布完整
     (remote tip 可以是 bookkeeping commit 的後代,**不要求 SHA 相等**;
     也**不得只查最新一個**)。Progress Log 缺失、SHA 解析失敗、任一 SHA 未包含
     於 remote tip → fail-closed。
   - 全部通過後才對該列取
     `git diff --name-only --no-renames $(git merge-base <remote-tip> <整合分支SHA>)..<remote-tip>`,
     全部取聯集;補修 diff 與聯集有交集 → 不適用「直接補修」,走上面的預設回滾。
5. 排除正在評估的補修自己 —— 它跟自己必然 100% 交集,不排除永遠算出「不適用」。
6. 表裡列著但 ref 不存在(打錯字、branch 被刪)→ 停下問人,不當空集合略過 ——
   「沒有交集」的結論不能建立在漏算上面。
7. **執行補修者自己的 checkout 也必須 clean、無 ahead 未推的 commit**;上面任何
   一條無法觀測(fetch 失敗、表解析不了、狀態看不到)就**不准宣稱零交集**。

⚠️ revert 之後的坑:**revert 一個 merge commit 之後,重新 merge 同一個 branch 不會
生效** —— git 看的是祖先關係,revert 只是加一個反向 commit,不改變「那些 commit
已在歷史裡」的事實。不要以為 revert 完再 merge 一次就好;要讓那個 feature 回來,
只有兩條路:

- **revert the revert**:`git revert <那個 revert commit>`,再補修。
- 從整合分支**重新開一個 branch**,把改動重做成新 commit。

## 8. 每階段呼叫的技能(AI 對照表)

每站一句。節點鏈正本是 `graph.yaml`,不要在這裡列整條鏈。

去哪:[talk `#map`](https://rick546986.github.io/dev-flow/guides/guide-dev-talk.html#map) · [flow `#stage2`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage2)–[`#stage7`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage7)

| 階段 | 一句 | graph.yaml | guide |
|---|---|---|---|
| 1 討論 | `/dev-talk`:盲下游,12 步,走錯重跑那一節 | `skills/dev-talk/graph.yaml` | [talk `#map`](https://rick546986.github.io/dev-flow/guides/guide-dev-talk.html#map)(含 write_code) · [白名單](https://rick546986.github.io/dev-flow/guides/guide-dev-talk.html#whitelist) |
| 2 收斂 | 2-3 方案比較 + 壓測定案,過 G1 | `skills/dev-flow/stage2/graph.yaml` | [flow `#stage2`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage2) |
| 3 原型 | throwaway 實驗,答案回寫 2;選配 | `skills/dev-flow/stage3/graph.yaml` | [flow `#stage3`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage3) |
| 4 規格 | openspec delta,過 G2 | (main 尚無獨立 graph,不要假造) | [flow `#stage4`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage4) |
| 5 任務 | tracer-bullet + 四欄,執行板 | — | [flow `#stage5`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage5) |
| 6 實作 | `/dev-flow` 接執行引擎;TDD 紅綠 + 守衛 | — | [flow `#stage6`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage6) |
| 7 驗證 | 雙軸審 + coverage + G3 | — | [flow `#stage7`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage7) · [`#gates`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#gates) |
| 隨時 | `dev-report` 產出去識別化缺陷回報 | — | `devflow-report-guard` |

> **外部 skill 依賴原則**:方法一律內建於模板執行清單,外部 skill 只當**選配加分**(叫不到不影響流程)。

## 9. 模型分層與 effort(AI 執行時)

預設照表;要偏離(表內建的升降階除外)須使用者明示同意。

去哪:[quickstart ④](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html#models)
· [flow `#flow`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#flow)。

契約 / 檢查器抽:

- **G1/G2/G3 審查與 verdict**:依 §7 的人類→fresh-context reviewer Agent→有記錄的
  owner 自審順序;Agent 只要求乾淨 context、審核對象、基準與回報格式,不指定模型。

## 10. 新 feature 快速上手

從 `/dev-talk` 開一張討論,再用 `/dev-flow` 走完全程。

去哪:[quickstart](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html)

1. `/dev-talk 我想做 <想法>` → 只覆寫一份 `1-discussion.md`。
2. `STATUS.md` 加一列;`/dev-flow 繼續 <feature>` 走完全程。
3. 每過 gate:frontmatter + STATUS + html twin。
4. G3 過:Exit checklist。

細節、Session 邊界、Stage 6 三步順序見 [quickstart](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html)。

## 11. 資訊隔離(anti-premature-convergence)

討論不能偷看下游,否則答案會被下游形狀帶跑。

去哪:[flow `#fence`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#fence)
· [talk `#whitelist`](https://rick546986.github.io/dev-flow/guides/guide-dev-talk.html#whitelist)

四道圍欄(討論盲下游 / 實作盲討論 / 審查防錨定 / Quiz gate)全文見上。

⚠️ **禁把流程規則寫進專案 CLAUDE.md / AGENTS.md**(每 session 自動注入 = 盲全滅)。
規則只住 `docs/dev/README.md`,由 /dev-flow 需要時自己讀。

## 12. SDD × TDD 雙迴圈(V 對應)

SDD 是脊椎,TDD 是右側驗證。每個 S 先寫失敗的驗收測試再打綠。

去哪:[flow `#stage6`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#stage6) · [§7](#7-角色與-gate)

回歸義務見 §7(G3 定義)。

## 13. 大案與切片

找不到合法接縫就不切,保留單一 `4 → 5 → 6 → 7`。

去哪:[flow `#large-work`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#large-work)

## 16. Agent Memory(`.dev-flow/`)

長期記憶進 Git。不要手改記憶檔。

去哪:本節各小標。安裝與重建入口只有 `dev-setup`。查詢與寫入只有
`${CLAUDE_PLUGIN_ROOT}/memory/dev-memory.py`。

### 16.1 三個目錄,不要搞混

| 目錄 | 是什麼 | 進 Git? |
|---|---|---|
| `docs/dev/` | 給人看的七階段文檔、STATUS、HISTORY | 是 |
| `.dev-flow/` | Agent 要帶走的長期記憶。這才是正本 | 是 |
| `.devflow/` | 執行期暫存(旗標、runs、reports) | 否 |

本機 SQLite 快取不進 Git。不要把 `docs/dev/` 抄進 `.dev-flow/`。
人看 ADR / HISTORY 走 html 人頁,不要把正文抄進 `.dev-flow/decisions`。

### 16.2 專案身分不是路徑

`.dev-flow/project.yaml` 的 `project_id` 是 ULID。Mac / Windows / Linux 路徑不同,
仍是同一個專案。remote 只當出處,不拿來推 id。
`.dev-flow/` 裡的檔案引用一律是 repo 相對路徑(`src/services/db.ts`),不是
`/Users/…`。寫進去會擋; `dev-memory.py doctor` 抓到就是 FAIL。

### 16.3 七種記憶

| 類型 | 回答什麼 | 住哪 | 誰說了算 |
|---|---|---|---|
| Implementation truth | 程式現在怎麼跑 | `state/implementation/` | 當前程式碼 / schema / 實跑證據 |
| Domain | 這個詞在真實世界是什麼意思 | `knowledge/{domain,entities,…}/` | 人確認過的業務語意 |
| Intent | 打算往哪走(不是現況) | `knowledge/intents/` | 核可過的計畫 |
| Event | 以前發生過什麼 | `events/YYYY/MM/` | 只增不改 |
| Decision | 當初為什麼這樣選 | `decisions/DEC-*.md` | ADR / PR / 明確討論 |
| Skill | 怎麼做某件事 | `skills/*.yaml` | 驗證過的流程 |
| Unknown / Conflict | 不知道,或兩邊說法不同 | 各類的 status | 合法答案,不是缺陷 |

程式碼不能覆寫已確認的業務語意。對不上就標 CONFLICT,兩邊都留著。

### 16.4 現況會過期

只管 implementation truth:

```
VERIFIED + 依賴檔沒變          → 直接用,不重讀原始碼
依賴檔改了或工作樹 dirty      → 本機標 STALE(Git 側不動)
查到 STALE                    → 必須重看當前原始碼
  一樣 → 回 VERIFIED
  不一樣 → 舊筆作廢,寫新的
  判不出 → 留 STALE,不寫新值
```

feature branch 改了依賴檔,不能拿 main 上的舊 VERIFIED 當這棵樹的答案。

### 16.5 先問意圖,再查

契約 / 檢查器抽(四個 retrieval status 名):

`dev-memory.py ask "<問題>"` 先分類再走路徑。每個答案都帶狀態。上層 agent 通常只看 `retrieval_status`:

| 狀態 | 意思 |
|---|---|
| `OK` | 可信,而且在當前 checkout 下仍對得上 |
| `NEEDS_VERIFICATION` | 有舊值,但依賴改了。**不是 OK**,要重驗 |
| `CONFLICT` | 兩邊打架,不挑邊 |
| `NO_RELIABLE_MATCH` | 沒有可信命中。這是合法答案,不要拿低分記憶頂替 |

多筆取最嚴重的:`CONFLICT` > `NEEDS_VERIFICATION` > `OK`。
generation 對不上時,舊的 VERIFIED 也不能當現況(見 16.12)。

### 16.6 開場只帶一小包

開場只注入:專案身分、當前 branch/HEAD、關鍵已驗證事實、不變量、未做的 intent、
未解衝突、近期大事、怎麼查記憶。其餘用時再問。
**現在沒有 `CONTEXT.md`。** 詞彙住 `.dev-flow/knowledge/domain/`。

### 16.7 兩條路,同一個收尾

`/dev-talk` 與 Stage 6 用同一組 session。沒走到 end / checkpoint 的場保持 OPEN,
或明寫 ABORTED。下一次開新場,不接上一場。

```
/dev-talk
  talk start → turn / propose(只留本機) → 你確認
            → talk end    ← 長期記憶只在這裡寫進 .dev-flow/
            ↘ talk abort

Stage 6
  session start → observe(高訊號才成候選)
               → checkpoint --end  ← 寫進工作樹
               → commit → push → durable-check
               ↘ abort
```

`promoted: 0` 是合法結果。沒東西可記就不要硬記一筆。

### 16.8 改過的還看得到

現況檔只留「現在是什麼」。每次更正另外寫一筆事件。砍掉本機快取再重建,兩邊都在。

### 16.9 寫進工作樹 ≠ 已保存

`checkpoint` 回數字只代表檔案落到這棵工作樹。Stage 6 收尾順序是:盤點 →
checkpoint → memory commit → push → `durable-check`。離線要放行,明確加 `--local-only`。

### 16.10 少寫

讀檔、grep、列目錄、一般成功指令不進 Git。
疑似 secret、或內容含絕對路徑 → 拒絕固化,不做遮罩後放行。

### 16.11 `/dev-talk` 怎麼記

`/dev-talk` 讀當前 `.dev-flow/`(經 `dev-memory.py ask`),不讀一份過期的 `CONTEXT.md`。
逐字稿只留本機;N13 `talk end` 才把已確認的寫進長期記憶。已有 OPEN 場不要再 `talk start`。

### 16.12 換機器,跟 `git pull`

**新 clone / 新機器**:打一次 `dev-setup`。它讀當前 checkout 的 `.dev-flow/`,
重建這棵樹的 SQLite 快取。

**已經在用的機器**:`git pull` 把 `.dev-flow/` 卡片拉下來就夠。不必再跑
`dev-setup`。generation 對不上時,舊的 VERIFIED 不能當現況。

沒有 generation 戳時,只有兩邊都空才能只蓋章。樹裡已經有 knowledge / fact /
decision / skill / event 時,即使 DB 是空的也要重建。
重建綁同一個快照:before / after 必須來自同一批載入的位元組。

### 16.13 從舊架構遷移

- 舊的 `CONTEXT.md` → `dev-memory.py migrate-legacy`,落地是候選,不是已確認。
- `docs/dev/HISTORY.md` 留在原地。memory 只索引它。不要抄進 `.dev-flow/events/`。
- 舊的以路徑當鍵的本機資料會對到新的 `project_id`,一列都不刪。

---

## 17. 附錄:跨 repo 與非 feature 入口

跨 repo 只建一份 feature 檔;非 feature 也走 `/dev-talk`。母版目錄樹在本節末(手機可跳)。

去哪:[flow `#large-work`](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#large-work) · [quickstart](https://rick546986.github.io/dev-flow/guides/guide-quickstart.html)

**跨 repo feature**(如前後端成對 repo):feature 資料夾住**主 repo**(通常後端),
配對 repo 的 `docs/dev/STATUS.md` 加一列連結過去,不重複建檔。

**非 feature 入口**:架構巡檢/償債機會 → 一樣開 `/dev-talk` 討論,產物同格式。

疑義以本 README 契約句為準;細節跟 guide 鏈走。範例看 `example/contract-expiry-reminder/`。

<!-- devflow:master-only:start -->
圖在 `guides/`,不在這裡 —— 本檔是索引,要圖請點上表的導覽連結。

**怎麼逛這個 repo**(手機可跳):每個目錄後面標的是「誰在讀它」——那就是它不能被刪的依據。
想刪任何東西前先跑 `grep -rn "<路徑>" hooks/ skills/ scripts/ _templates/ README.md`,
零命中才考慮。

```text
dev-flow/
│
├── ── 制度正本(改這裡等於改規則)──────────────────────────────
│   README.md                本檔。入口／索引。Gate 契約句在 §7,全文見 guide #gates
│                            └ 讀者:gate-consistency.sh 每次動態抽 token 比對四處
│   devflow-contract.json    方法論 ↔ runtime 的版本握手
│                            └ 讀者:devflow-exec.sh doctor,缺件 fail-closed
│   _templates/               七階段模板 + STATUS/ADR/living-spec/html-shell
│                            └ 讀者:dev-setup 散發進每個專案;parity 檢查比對 guides
│   notes/design/ (6)        各機制設計正本(並行/觀測/gauntlet/real-world/boundary)
│                            └ 讀者:dev-setup SKILL 指 evidence-gauntlet.md 為契約正本
│   docs/prompts/ (2)        改造 dev-flow 本身的需求正本
│                            └ 讀者:notes/ 底下 8 處寫「需求正本: docs/prompts/…」
│
├── ── Claude Code plugin(裝進使用者機器的部分)────────────────
│   .claude-plugin/          plugin.json(版本字串=更新判斷依據)+ marketplace.json
│   hooks/                    守衛與執行引擎
│     ├ hooks.json           掛載清單,壞了守衛全靜默失效
│     ├ devflow-guard.sh     PreToolUse 讀寫守衛(未武裝時對 Stage 6 文件軟擋一次)
│     ├ devflow-exec.sh      執行引擎 + doctor 版本握手
│     ├ gate-consistency.sh  從 README §7 抽 gate token,比對 SKILL/README §3/三模板
│     ├ selftest.sh          守衛自測(案數以腳本輸出為準)
│     └ devflow_obs_vendor/  observability/ 的 vendored 副本(hooks 不能依賴 repo 相對路徑)
│   skills/ (5)              dev-flow(路由器)/ dev-run(Stage 6 引擎)/ dev-setup(安裝器)
│                            / dev-release(發版器)/ dev-talk(訪談引導)
│
├── ── 機械檢查(CI 與本機都跑這些)─────────────────────────────
│   scripts/                  單一入口 devflow-check.sh all,全過 = REPO_REFERENCE_PASS
│                            devflow-evidence-gauntlet.sh 是 Stage 7 證據檢查的母版
│   observability/            Attempt Ledger 工具(devflow-obs)+ agent_event schema
│                            └ 讀者:selftest.sh:1539 直接讀它,刪了 p3 段就壞
│   tests/parallel-stage6/   T 級並行的可執行契約(contract_ref + fixtures)
│   .github/workflows/       devflow-ci(REPO_REFERENCE)+ runtime-selftest(EXTERNAL_RUNTIME)
│                            兩層不互相代表,一邊綠不代表另一邊綠
│
├── ── 給人看的 ────────────────────────────────────────────
│   example/contract-…/ (14) 一個 feature 走完七階段的真實形狀(md + html twin 各 7 份)
│                            └ 讀者:renderer fixed-point 檢查逐位元組比對那四份 html
│   guides/ (4)              圖解導覽 html(GitHub Pages 指這裡;根目錄舊 redirect stub
│                            已移除,舊 Pages 網址直接改指 guides/,見 README 上方連結)
│   docs/PLUGIN.md           plugin 安裝與更新說明
│   manifests/ (4)           四軌改造的工單記錄
│   notes/ (其餘)            稽核、導入回饋、驗證對標
│
└── ── 本 repo 自己的改版流程(dogfooding)──────────────────────
    docs/dev/                本 repo 用自己的流程管自己
      ├ STATUS.md            Active / Backlog 兩張表(做完的不留這裡)
      ├ HISTORY.md           改版歷史索引(只增不改;唯一寫入口 scripts/history-append.sh)
      ├ HISTORY.html         人頁(衍生,scripts/build-public-docs.py 重生)
      ├ devflow-contract.json + tools/  dev-setup 的散發副本(doctor 在這裡找)
      └ <slug>/              各次改版的七階段文檔
    docs/adr/                長期決策 md 正本 + 人頁 html(index.html;重生同上)
```
<!-- devflow:master-only:end -->
