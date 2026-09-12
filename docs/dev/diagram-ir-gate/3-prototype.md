---
feature: diagram-ir-gate
stage: 3-prototype
status: draft
owner: rick
updated: 2026-09-12
---

# 3. 原型 — IR 閘／路由表／Proof Lab 長什麼樣？

> Stage 3 依 2-decision「不預先跳過」**執行、不跳過**。Decision A + D + G 已是核准 Pattern → 1 個可操作 CLI Demo，不湊 UI Variant。
> 本站證明 **wave-1 形狀**：typed IR → 驗證 → 原子交付／`DIAGIR_*` + last-good、五家族路由表、Proof Lab 薄索引。
> **不**改 `scripts/build-vbox-fig.py`／`build-gate-twin.py`／`build-dir-tree.py`／`build-stage1-html.py` 正本；正式閘接產器留 Stage 6。
> 信封欄位（`family`／`payload`／`receipt`）**不**在本站鎖 JSON Schema（OC-1）。
> Human verdict 由參與 Demo 的人類親填。本 hop **未**經人類 Demo → `NOT_REVIEWED`。Agent 禁代填 ACCEPTED、禁寫 attestation、**不送 G2**、不開 4-spec、不發版、不碰 `#196`／`integration-before-verdict`。
> frontmatter `status: draft`：verdict ≠ ACCEPTED 時不得改 approved（模板 User Demo Feedback）。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context -->
- [ ] 有新的前端流程（本題是產器／CLI 閘，無新前端）
- [x] 改變使用者下一步（IR 失敗後讀 `DIAGIR_*` + 旋鈕，目標留 last-good；不能再靠 git checkout 救壞 html）
- [x] 涉及角色交接（開工 agent 先查路由表 → 產檔器吐收據 → 審查人看審頁／last-good）
- [ ] 涉及人工核准（IR 閘是機器驗；G1–G3 是既有 gate，本刀不加新人裁）
- [x] 涉及等待/退回/逾時（驗證失敗或寫入中斷 → `DIAGIR_ABORT` 退回修 IR 再重跑）
- [ ] 涉及權限差異（誰都能硬跑錯產器；主機層攔截是後刀 `[Assumption]`）
- [x] 涉及系統外動作（瀏覽器開審頁；現況 workaround 是 git checkout 舊 html）
- [ ] 涉及多種可行互動設計（A + D + G 已 lock；單一路徑 CLI）
- [ ] Stage 1 尚有操作流程不確定性（Journey 已是 路由→驗證→原子寫／失敗留 last-good；欄位名進 4-spec）

→ 命中 4 條:Stage 3 條件式必要,執行(不跳過)。2-decision 無「跳過 Stage 3」流程層 OC。

## Question
2-decision Risk「信封欄位未釘／產器仍可 `write_text` 繞閘／vbox-fig 無獨立負向」＋ SC-1～SC-5：在**不實作 Stage 6 產器閘**的前提下，throwaway CLI 能否鎖住這三個答案？

1. **A 閘形狀**：共用信封（本站假設 `family` + `payload`，不鎖 Schema）→ 驗證 → `atomic_write`(tmp + `os.replace`)。六個 `DIAGIR_*` 各能紅一次，stderr 有穩定碼 + 一句旋鈕；失敗與中斷都不得取代 last-good。
2. **D 路由形狀**：五家族查找表先選家族；`mermaid` 與錯家族 payload（三框當生命週期、樹收成單盒）走 `DIAGIR_FAMILY`，不寫檔。
3. **G Lab 形狀**：薄索引點名既有 fixture 牙 + 各一正一負；負向 exit ≠ 0 且不蓋 last-good。不是第二套檢查語言，也不是「只有 `lifecycle.json` 綠過」。

答案長什麼樣才算回答了：
- 六碼 `DIAGIR_KIND`／`EMPTY`／`LINES`／`FAMILY`／`WHY`／`ABORT` 各至少一案，stderr 含該碼 + `KNOB`。
- 失敗案目標 sha256 與 last-good 相同；成功案才換新內容；`--abort` 只留 `.tmp`、目標仍是 last-good。
- 路由表五列可查；`mermaid` 不在表上 → `DIAGIR_FAMILY`。
- Lab 三家族 `pos_ok` + `neg_ok` + `last_good_after_neg`；`second_check_language=false`。
- 正式 `scripts/` 產器**沒有**因本站被改。

## Method
- 實驗位置:session scratchpad `/tmp/diagir-stage3-proto/`（**PROTOTYPE — not production code**；不進 Git；正式閘接產器留 Stage 6，沿用 OC-3 的 `atomic_write` 形狀）
- Demo 形式:**可執行 CLI flow**（使用者實際跑 throwaway，不是只看靜態說明）
- Pattern 已核准（A + D + G）→ **1 個 Demo**，不做假 Variant
- 具名模組:RouteLookup／IrValidate／AtomicDeliver／ProofLabIndex
- 驗法:`python3 /tmp/diagir-stage3-proto/diagir-gate.py route|deliver|lab`
- 本站**不**改 `scripts/build-*.py` 正本（只讀、對照：現況產器失敗只印散文、**零** `DIAGIR_*`）

意圖中的收據形（4-spec 再釘欄位名；本站只鎖形狀）：

```
FAIL <DIAGIR_*> <detail>
KNOB <一句可修旋鈕>
{"ok": false, "code": "DIAGIR_*", "target_replaced": false}
```

成功：`atomic_write` 後目標要嘛全新、要嘛全舊；中斷只留 `target.tmp`。

## 結構圖
```
RouteLookup 先選家族
        |
        +-- 表上五列 --> IrValidate
        +-- mermaid／錯家族 --> DIAGIR_FAMILY（不寫）
IrValidate
        |
        +-- DIAGIR_KIND／EMPTY／LINES／WHY --> 停、last-good
        +-- 過 --> AtomicDeliver（選定）
AtomicDeliver
        |
        +-- tmp+replace --> 新檔
        +-- 中斷 --> DIAGIR_ABORT、.tmp、last-good
ProofLabIndex 對齊現有牙（各一正一負）
```

- RouteLookup 先選家族
- IrValidate DIAGIR_*
- AtomicDeliver（選定）
- ProofLabIndex 薄索引

## Demo Script

### Scenario AC-1（失敗碼 + last-good）
- 使用者角色:開工 agent
- 真實目標:餵錯 IR 時不要蓋掉上一張好圖，並看到穩定碼與旋鈕
- 起始狀態:scratchpad 目標已寫 `LAST-GOOD`；IR = `fx/kind-parked.json`（lifecycle 四格、kind=`parked`）
- 操作步驟:跑 `python3 /tmp/diagir-stage3-proto/diagir-gate.py deliver --ir fx/kind-parked.json --family lifecycle --target targets/fail-kind.out`；比對目標 sha256 與 stderr
- 系統回應:exit 1；`DIAGIR_KIND`；`KNOB 把 kind 改回允許值，或改走路由表上的正確家族`；目標 sha256 不變
- 系統外下一步:改 kind 或改查路由表；不要 `git checkout` 舊 html
- 觀察問題:看到紅之後是否知道下一步是改 kind 還是換家族？系統有沒有只丟 traceback？

### Scenario AC-1／AC-3（三框當生命週期／樹收單盒）
- 使用者角色:開工 agent
- 真實目標:錯家族在寫檔前被擋
- 起始狀態:`fx/family-threebox-as-lifecycle.json`（三框當 lifecycle）；`fx/tree-as-vbox.json`（樹狀當 flow vbox）
- 操作步驟:各跑一次 deliver；再跑 `route --family mermaid`
- 系統回應:前兩案 `DIAGIR_FAMILY`、last-good 仍在；`mermaid` 查無此家族、`ROUTE_TABLE` 列出五列
- 系統外下一步:查路由表，改呼叫 `build-stage1-html.py` 或接受 gate-twin 的 WARNING+`<pre>`
- 觀察問題:系統是否暗示「隨便一支產器都能畫」？

### Scenario AC-2（原子交付／中斷）
- 使用者角色:產檔器
- 真實目標:寫入要嘛全新、要嘛全舊
- 起始狀態:綠 IR `fx/lifecycle-good.json`；對照 `--abort`（驗證過、replace 前停）
- 操作步驟:先跑成功 deliver；再跑同一 IR + `--abort`；看目標與 `.tmp`
- 系統回應:成功案目標被換成收據正文；中斷案 exit 1、`DIAGIR_ABORT`、目標仍是 `LAST-GOOD`、只留 `target.tmp` 內容 `PARTIAL-TRUNCATED`
- 系統外下一步:先修 IR／重跑；不要把 `.tmp` 當產品
- 觀察問題:中斷後打開目標還是上一張好產出嗎？有沒有半份新檔？

### Scenario AC-4（Proof Lab 一正一負）
- 使用者角色:owner／開工 agent（要重放樣張）
- 真實目標:vbox-fig／gate-twin／dirmap 各一正一負，負向不蓋檔
- 起始狀態:薄索引 `lab/index.json` 點名既有 `scripts/fixtures/{vbox-fig,gate-twin,dir-tree}` 牙；vbox-fig 負例用 scratchpad（生產目錄尚無獨立負向，Stage 6 補）
- 操作步驟:跑 `diagir-gate.py lab --index lab/index.json --repo <root>`
- 系統回應:三家族 `pos_ok`／`neg_ok`／`last_good_after_neg` 皆 true；`second_check_language=false`
- 系統外下一步:Stage 6 才把負向樣張補進 `scripts/fixtures/vbox-fig/` 並把閘接到正本產器
- 觀察問題:Lab 有沒有另造第二套牙？是不是只綠了 `lifecycle.json`？

### Scenario AC-5（預設仍是靜態直式 SVG）
- 使用者角色:owner
- 真實目標:wave-1 不把動畫／Mermaid／Node 當預設
- 起始狀態:本 Demo 只跑 Python CLI + 現況 `build-vbox-fig.py --fixture lifecycle`
- 操作步驟:看成功收據與現況 SVG；搜 `mermaid.js`／自動播放
- 系統回應:現況產器吐靜態 `<svg viewBox>`；throwaway 收據寫 `static-svg`；路由拒 `mermaid`
- 系統外下一步:可選 trace 是後刀（Q8），本 slug 不收
- 觀察問題:有沒有任何一步暗示要先上動畫才算閘？

## Result
- **2026-09-12 實跑**（CloudAgent scratchpad `/tmp/diagir-stage3-proto/`；tip `1f8d992` = #211 後 main；throwaway sha256 `836efe3b5e006d241e8be9a6568fa3cb6fc8bf2570fab269f1e26b5e23356809`）:

| case | exit | code | last-good kept |
|---|---|---|---|
| `ok-lifecycle` | 0 | — | no（合法取代） |
| `fail-kind` | 1 | `DIAGIR_KIND` | yes `ec3261d0…` |
| `fail-empty` | 1 | `DIAGIR_EMPTY` | yes |
| `fail-lines` | 1 | `DIAGIR_LINES` | yes |
| `fail-family-3box` | 1 | `DIAGIR_FAMILY` | yes |
| `fail-family-tree` | 1 | `DIAGIR_FAMILY` | yes |
| `fail-why` | 1 | `DIAGIR_WHY` | yes |
| `abort-ok` | 1 | `DIAGIR_ABORT` | yes；`.tmp`=`PARTIAL-TRUNCATED` |
| `route mermaid` | 1 | `DIAGIR_FAMILY` | n-a（未寫檔） |

- 路由五列皆可查：`stage1-now`／`stage2-arch`／`flow`／`dir-tree`／`lifecycle`；每列有「用這條／不用那條／產器」。
- Proof Lab：`ok: true`；vbox-fig／gate-twin／dir-tree 皆 `pos_ok` + `neg_ok` + `last_good_after_neg`；`second_check_language: false`。
- 現況產器對照（只讀、未改）：`build-vbox-fig.py --fixture lifecycle` exit 0、有 `<svg>`、**零** `DIAGIR_*`；同產器吃 `parked` exit 1、散文「不准發明 parked」、**零** `DIAGIR_*`；`build-dir-tree.py` + `missing-why` exit 1、散文「缺一句到兩句 why」、**零** `DIAGIR_*`。#191 方向仍在，閘還沒掛上正本。
- 答案:A／D／G **形狀成立**（throwaway）；CLI Demo 足夠；正式產器未落地。信封 Schema 未鎖。
- 回寫對象:2-decision Risk「信封欄位未釘／繞閘／vbox 負向」＋內部技術選擇＋確認紀錄「prototype 回寫」。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填。Agent 禁代填 ACCEPTED，禁寫 attestation。 -->
- Demo date: 2026-09-12（agent 代跑 CLI；人類尚未走 Demo Script）
- Participants: CloudAgent implementer-B（代跑）
- Variant reviewed: CLI-only（無 UI Variant；選定 = AtomicDeliver last-good 或新檔）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED

## Verdict
- 回寫 2-decision：A 閘形狀經 throwaway CLI 確認（六碼皆紅過；失敗／中斷 last-good 位元組不變；成功才 `os.replace`）。D 五列可查、錯家族／`mermaid` → `DIAGIR_FAMILY`。G 薄索引三家族各一正一負可重放，不是第二套牙。**第 3 站已行使**；CLI Demo 足夠，無省略宣告。
- Human verdict = **NOT_REVIEWED**（人類未走 Demo）。Agent 禁代填 ACCEPTED、禁寫 attestation。frontmatter `status: draft`。**不送 G2**、不開 4-spec、不 bump plugin、不改 `#196`。
- throwaway 腳本處置:留在 session `/tmp/diagir-stage3-proto/`，**不進 Git**；形狀已錄於 Question／Method／Result。正式碼 Stage 6 再把閘接到既有產器寫路徑。
