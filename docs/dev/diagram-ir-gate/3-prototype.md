---
feature: diagram-ir-gate
stage: 3-prototype
status: draft
owner: rick
updated: 2026-09-12
---

# 3. 原型 — IR 閘／路由表／Proof Lab 長什麼樣？

> Stage 3 依 2-decision「不預先跳過」**執行、不跳過**。Decision A + D + G 已是核准 Pattern → 1 個可操作 CLI Demo，不湊 UI Variant。
> 本站只證明形狀：typed IR → 驗證 → 原子交付、穩定 `DIAGIR_*` + 可修旋鈕、失敗不蓋 last-good、五家族查找路由、Proof Lab 薄索引對齊既有 fixture。
> **不**落地 Stage 6 產器（不改 `build-vbox-fig.py`／`build-gate-twin.py`／`build-dir-tree.py`／`build-stage1-html.py`）。不開 4-spec。不碰 `#196`。不發版。不收 Mermaid／Node／動畫。
> Human verdict 由參與 Demo 的人類親填。本 hop **未**代填 ACCEPTED、**不**送 G2。frontmatter 留 `draft`（verdict ≠ ACCEPTED 不得改 approved）。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context -->
- [ ] 有新的前端流程（本題是 CLI／收據閘，沒有新產品畫面）
- [x] 改變使用者下一步（開工 agent 必須先查路由表再組 IR；失敗看到穩定碼＋旋鈕，不能只 traceback 後直接 `write_text`）
- [x] 涉及角色交接（agent 產 IR → 閘驗證／交付 → 審查人看收據與 last-good 是否還在）
- [ ] 涉及人工核准（IR 閘是機械碼；G1–G3 既有，本站不新增人批關卡）
- [x] 涉及等待/退回/逾時（驗證失敗＝退回修 IR；目標停在 last-good 直到重跑）
- [ ] 涉及權限差異（角色權限與現況相同）
- [x] 涉及系統外動作（終端機跑產器／throwaway；審查人用瀏覽器開審頁）
- [ ] 涉及多種可行互動設計（A + D + G 已 lock；單一路徑 CLI）
- [ ] Stage 1 尚有操作流程不確定性（Journey 已是先選家族 → 驗證 → 交付或退回；信封欄位名進 4-spec）

→ 命中 4 條:Stage 3 條件式必要,執行(不跳過)。2-decision 無「跳過 Stage 3」流程層 OC。

## Question
2-decision Risk「信封欄位未釘／`write_text` 繞過閘／vbox-fig 無獨立負向」＋ SC-1～SC-5：在**不實作 Stage 6 產器**的前提下，throwaway CLI 能否鎖住這四個答案？

1. **G-ir last-good（SC-1）**：先有通過驗證的目標 SVG，再餵 `DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`（以及 `EMPTY`／`LINES`）→ 目標位元組與 last-good 相同；stderr／收據含穩定碼 + 一句旋鈕，不是只 traceback。
2. **G-ir 原子（SC-2）**：通過後寫入要嘛全新、要嘛全舊；模擬中斷只留截斷 `.tmp`，目標不是半份新檔。
3. **G-route（SC-3）**：五列查找表都有「用這條／不用那條」+ 產器 + 契約；樹狀當 vbox、三框當生命週期、目錄樹收單盒 → `DIAGIR_FAMILY`。
4. **G-lab（SC-4）**：薄索引點名既有 fixture（vbox-fig／gate-twin／dir-tree），每家族一正一負可重放；負向 exit ≠ 0 且不蓋 last-good。不是「只有 `lifecycle.json` 綠過」。

答案長什麼樣才算回答了：
- 六個 `DIAGIR_*` 碼都在輸出裡出現，且都帶旋鈕句。
- 所有負向案例 `target_unchanged=True`；中斷後目標 sha 仍是 last-good。
- 路由表 `ROUTE_ROWS 5`；Lab 三家族各一正一負 `got_ok` 對得上。
- 預設交付是靜態 SVG（`has_mermaid=False`）。
- 正式 `scripts/` 產器**沒有**因本站被改。

## Method
- 實驗位置:throwaway CLI `docs/dev/diagram-ir-gate/proto/diagir_gate.py`（**PROTOTYPE — not production code**；本 feature branch 供人重跑 Demo）。同檔副本 `/tmp/diagram-ir-gate-stage3-proto/`（session scratchpad）。
- Demo 形式:**可執行 CLI flow**（使用者實際跑 throwaway，不是只看靜態說明）
- Pattern 已核准（A + D + G）→ **1 個 Demo**，不做假 Variant
- 驗法:`python3 proto/diagir_gate.py demo --root <repo> --work <dir>`
- 原子寫形狀沿用 OC-3：`tmp + os.replace`（對齊 `scripts/write-stack-inventory.py`），不另造第三支寫檔幫手
- 本站**不**改 `scripts/build-*.py`、不往 `scripts/fixtures/` 塞假負例（vbox-fig 負向用 scratch `parked` kind；正式負例留 Stage 6）
- 信封形狀（4-spec 再釘 Schema；本站只鎖「有 family／payload、先驗證再寫」）:

```
{ "family": "<route-id>", "payload": { ... } }
```

## 結構圖
- 先查五家族路由表
- 組 typed IR
- validate＋DIAGIR_*（選定）
- pass: atomic_write
- fail: last-good 留下
- Proof Lab 薄索引重放

## Demo Script

### Scenario AC-1（失敗不蓋 last-good）
- 使用者角色:開工 agent
- 真實目標:壞 IR 不得取代上一張好圖
- 起始狀態:work 目錄已有 last-good 靜態 SVG（sha256 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc`）
- 操作步驟:跑 `demo`；看 `kind-parked`／`tree-as-vbox`／`dir-short-why` 的 `unchanged` 與 stderr 碼
- 系統回應:三案皆 `ok=False`；碼分別 `DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`；另印 `DIAGIR_ABORT`；`LAST_GOOD_HELD True`
- 系統外下一步:依旋鈕句改 IR 或改選路由列，再重跑。不要 `git checkout` 舊 html
- 觀察問題:看到碼之後知道下一步嗎？系統有沒有暗示「exit 非 0 但檔已換掉」？

### Scenario AC-2（原子交付／中斷）
- 使用者角色:產檔器
- 真實目標:看見的要嘛全新、要嘛全舊
- 起始狀態:同一 last-good 目標檔
- 操作步驟:先看 `pass-lifecycle`（綠 IR 交付）；再看 `INTERRUPT`（只寫截斷 `.tmp`、不 `replace`）
- 系統回應:通過時 `delivered=True`、`sha_changed=True`、`static_svg=True`、`has_mermaid=False`。中斷時 `target_unchanged=True`、`tmp_truncated=True`、目標不是半份新檔
- 系統外下一步:正式產器 Stage 6 才把三支 `write_text` 接到同一閘
- 觀察問題:失敗或中斷後目標還能不能當 last-good 打開？

### Scenario AC-3（五家族路由）
- 使用者角色:開工 agent
- 真實目標:先選對家族，不要把三框當生命週期、樹收成單盒
- 起始狀態:Decision D 定稿五列
- 操作步驟:看 `ROUTE_ROWS`；再餵 `stage1-as-lifecycle`、`tree-as-vbox`、`dir-as-vbox`
- 系統回應:`ROUTE_COUNT_OK True`（五列皆有用這條／不用那條／產器／契約）。三個錯家族都是 `DIAGIR_FAMILY` + 旋鈕「查路由表，改呼叫對的產器」
- 系統外下一步:改呼叫對的產器；不要發明第六家族或 mermaid
- 觀察問題:表是查找還是機器猜？有沒有暗示黑盒自動排版？

### Scenario AC-4（Proof Lab 薄索引）
- 使用者角色:owner／審查人
- 真實目標:三家族各一正一負可重放；負向不蓋 last-good
- 起始狀態:既有 `scripts/fixtures/vbox-fig/lifecycle.json`、`gate-twin/fig-tree-ascii`、`dir-tree/good` 與 `missing-why`
- 操作步驟:看 `LAB` 六列
- 系統回應:vbox-fig 正=`lifecycle.json`／負=scratch `parked`→`DIAGIR_KIND`；gate-twin 正=直式行為流 scratch／負=樹狀 ASCII→`DIAGIR_FAMILY`；dir-tree 正=`good`／負=`missing-why`→`DIAGIR_WHY`。三個負向 `neg_held=True`
- 系統外下一步:Stage 6 才把 vbox-fig 正式負例補進既有 fixture 目錄；索引檔名 4-spec 再釘。不另造檢查語言
- 觀察問題:是不是只有 `lifecycle.json` 綠過？負向紅了會不會仍覆寫目標？

### Scenario AC-5（預設仍是靜態 SVG）
- 使用者角色:owner
- 真實目標:wave-1 預設圖不是動畫／Mermaid／Node
- 起始狀態:throwaway 交付路徑
- 操作步驟:看 `pass-lifecycle` 的 `static_svg`／`has_mermaid` 與 `NO_MERMAID_DEFAULT`
- 系統回應:三者皆證明預設是靜態直式 SVG
- 系統外下一步:可選 trace 仍是後刀（Q8）；本 slug 不收
- 觀察問題:成功條件有沒有變成「要會動」？

## Result
- **2026-09-12 實跑**（CloudAgent；tip `1f8d992` = origin/main；throwaway sha256 `90f04ae487197c148139527b6d8037ef92fae9fa5e2b81aa253f4615e3c55621`）。回寫對象:2-decision Risk「信封／write_text 繞閘／vbox 負向」＋ SC-1～5 形狀。

| case | ok | code | last-good |
|---|---|---|---|
| `pass-lifecycle` | True | PASS | 允許換成新靜態 SVG |
| `kind-parked` | False | `DIAGIR_KIND` | 保住 |
| `empty-title` | False | `DIAGIR_EMPTY` | 保住 |
| `four-lines` | False | `DIAGIR_LINES` | 保住 |
| `tree-as-vbox` | False | `DIAGIR_FAMILY` | 保住 |
| `stage1-as-lifecycle` | False | `DIAGIR_FAMILY` | 保住 |
| `dir-as-vbox` | False | `DIAGIR_FAMILY` | 保住 |
| `dir-short-why` | False | `DIAGIR_WHY` | 保住 |

- `LAST_GOOD_HELD True` sha256=`8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc`；`INTERRUPT` 目標不變、`.tmp` 截斷。
- `CODES_SEEN DIAGIR_ABORT,DIAGIR_EMPTY,DIAGIR_FAMILY,DIAGIR_KIND,DIAGIR_LINES,DIAGIR_WHY`（六碼齊；皆 `DIAGIR_` 前綴 + 旋鈕句）。
- `ROUTE_ROWS 5`；`LAB_INDEX_ROWS 6` 三家族各一正一負，負向 `neg_held=True`。
- `NO_MERMAID_DEFAULT True`。正式 `scripts/` 產器未改。
- 答案:A + D + G **形狀成立**（throwaway）；CLI Demo 足夠；正式閘未落地。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填。Agent 禁代填 ACCEPTED／禁寫 attestation。 -->
- Demo date: 2026-09-12（agent 代跑 CLI；人尚未親跑）
- Participants: CloudAgent implementer-A（代跑）；owner rick（待親填）
- Variant reviewed: CLI-only（無 UI Variant；選定 = typed IR → validate → atomic deliver）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED
- Verdict attestation: human:<姓名> @ <YYYY-MM-DD>

## Verdict
- 回寫 2-decision：Risk「信封欄位未釘」改為 throwaway 已證 `family`／`payload` + `DIAGIR_*` 收據夠跑 SC-1／2／5，Schema 仍進 4-spec；Risk「`write_text` 繞閘」改為閘內 last-good 成立、正式產器未接；Risk「vbox 無負向」改為 scratch `parked` 已證形狀、正式 fixture 仍 Stage 6。確認紀錄留「prototype 回寫」行。
- Human verdict = **NOT_REVIEWED**（人未親跑、未親填 attestation）。frontmatter `status: draft`。**不送 G2**、不開 4-spec、不假 ACCEPTED。
- throwaway 處置:本 branch 封存 `docs/dev/diagram-ir-gate/proto/diagir_gate.py` 供人重跑 Demo；session 副本 `/tmp/diagram-ir-gate-stage3-proto/`。非正式產品程式碼；Stage 6 才接到既有產器寫檔路徑。
