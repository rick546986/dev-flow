---
feature: diagram-ir-gate
stage: 3-prototype
status: approved
owner: rick
updated: 2026-09-12
---

# 3. 原型 — IR 閘／路由表／Proof Lab 形狀是否成立？

> Stage 3 依 2-decision「不預先跳過」**執行、不跳過**。Decision **A + D + G** 已是核准 Pattern → 1 個可操作 CLI Demo，不湊 UI Variant。
> 本 hop（IMPLEMENTER C，獨立）只證明形狀：**typed IR → 驗證 → 原子交付**、`DIAGIR_*` + 可修旋鈕、失敗／中斷不蓋 last-good、五家族查找路由表、Proof Lab 薄索引（vbox-fig／gate-twin／dirmap 各一正一負）。
> **不**落地 Stage 6 產器、**不**改 `scripts/build-vbox-fig.py`／`build-dir-tree.py`／`build-gate-twin.py`／`build-stage1-html.py`、**不**另造第二套牙、**不**開 4-spec、**不**送 G2、**不**假 Human ACCEPTED、**不**碰 `#196`／`integration-before-verdict`／發版／Mermaid／Node／動畫。
> Human verdict 由參與 Demo 的人類親填。本檔 **NOT_REVIEWED**（Agent 已代跑 CLI；人尚未親跑）。Stage 3 無 gate：回寫完成 → frontmatter `approved`。G2 Demo 仍拒（未親跑 ≠ ACCEPTED）。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context -->
- [ ] 有新的前端流程（本題是 CLI／IR 閘 + fixture 索引，無新產品前端）
- [x] 改變使用者下一步（開工 agent 必須先查路由表、驗證 IR，不能再就近抄產器直接 `write_text`；失敗要看 `DIAGIR_*` 旋鈕再重跑，不是接受壞圖）
- [x] 涉及角色交接（開工 agent 選家族 → 產檔器驗證／原子寫 → 審查人開審頁看 last-good 或新好圖）
- [x] 涉及人工核准（家族是人／agent 查表選，不是黑盒；審查人仍批 gate；owner 裁 wave-1 範圍）
- [x] 涉及等待/退回/逾時（驗證失敗或寫入中斷 → last-good 留下 → 修 IR 再重跑）
- [x] 涉及權限差異（agent 可跑產器寫 feature 樹；審查人只開審頁；owner 禁假 PASS／裁 slug）
- [x] 涉及系統外動作（終端機跑 throwaway／既有牙；瀏覽器開審頁；壞覆寫現況只能 git checkout）
- [ ] 涉及多種可行互動設計（A + D + G 已 lock；單一路徑 CLI）
- [ ] Stage 1 尚有操作流程不確定性（Journey 已是查表 → 驗證 → 原子交付／失敗退回；信封欄位進 4-spec）

→ 命中 6 條:Stage 3 條件式必要,執行(不跳過)。2-decision 無「跳過 Stage 3」流程層 OC。

## Question
2-decision Risk「信封欄位未釘／`write_text` 仍可繞過／vbox-fig 無獨立負向」＋ SC-1～SC-5：在**不實作 Stage 6 產器**的前提下，throwaway CLI 能否鎖住這四個答案？

1. **IR 閘（SC-1／SC-2／SC-5）**：薄信封只要 `family` + `payload`。驗證通過 → 原子寫入（tmp + `os.replace`），目標要嘛全新、要嘛全舊。`DIAGIR_KIND`／`EMPTY`／`LINES`／`FAMILY`／`WHY`／`ABORT` 失敗時 stderr 含穩定碼 + 一句可修旋鈕，目標位元組 = last-good。
2. **路由表（SC-3）**：五列查找（不是黑盒自動排版）。抽測入口落到該列；樹狀 ASCII 當 vbox → `DIAGIR_FAMILY`。
3. **Proof Lab（SC-4）**：薄索引點名既有 fixture + 一個 throwaway vbox 負向；vbox-fig／gate-twin／dirmap 各一正一負可重放；負向 exit ≠ 0 且不蓋 last-good。不是「只有 `lifecycle.json` 綠過」，也不是第二套檢查語言。
4. **Non-Goal（SC-6 形）**：預設產出仍是靜態直式 SVG；無 mermaid／無自動播放動畫。正式產器碼未改。

答案長什麼樣才算回答了：
- `demo` 表：綠交付改檔；六個 `DIAGIR_*` 紅且 `unchanged=True`；`AC-5-static-svg=True`。
- `routes` 印出恰好五列。
- `lab` 六案全過（三家族 × 正負）。
- 正式 `scripts/` 產器**沒有**因本站被改。

## Method
- 實驗位置:本 throwaway branch 的 `docs/dev/diagram-ir-gate/proto/`（**PROTOTYPE — not production code**；禁進 main 當產器；正式閘／產器接線留 Stage 6，沿用 OC-3 的 `atomic_write` 形狀）
- Demo 模組:`diagir_proto.py`（選定；可執行 CLI flow，不是只看靜態說明）
- Pattern 已核准（Decision A + D + G）→ **1 個 Demo**，不做假 Variant
- 驗法:
  - `python3 docs/dev/diagram-ir-gate/proto/diagir_proto.py routes`
  - `python3 docs/dev/diagram-ir-gate/proto/diagir_proto.py demo --workdir /tmp/diagir-stage3-c`
  - `python3 docs/dev/diagram-ir-gate/proto/diagir_proto.py lab --index docs/dev/diagram-ir-gate/proto/proof-lab-index.json --out-dir /tmp/diagir-stage3-c/lab`
- 本站**不**改 `scripts/build-*.py` 正本（只讀既有 fixture／契約）

薄信封（4-spec 再釘欄位；本站只鎖形狀）:

```
{"family": "<route-row>", "payload": {…}}
```

路由列（D 定稿，查找）:`stage1-scan`／`stage2-arch`／`behavior-flow`／`dir-tree`／`lifecycle`。

## 結構圖
- diagir_proto.py(選定)
- 查路由表選家族
- IR 驗證
- 原子交付或 DIAGIR
- last-good 不蓋
- Proof Lab 薄索引

```
開工 agent
  |
  v
diagir_proto.py(選定)
  |
  +-- routes: 五列查找
  +-- validate family+payload
  +-- ok  → atomic_write(tmp+replace) → 靜態直式 SVG
  +-- fail → DIAGIR_* + knob；目標 = last-good
  |
  v
Proof Lab 薄索引（既有 fixture + 1 個 throwaway 負向）
  正式產器／牙留 Stage 6
```

## Demo Script

### Scenario AC-1（驗證失敗 → last-good + 穩定碼）
- 使用者角色:開工 agent
- 真實目標:壞 IR 不得蓋掉上一張好圖；人看得到碼與旋鈕
- 起始狀態:`demo` 已先寫入一張綠的 lifecycle SVG（last-good sha `30dcd1e8…`）
- 操作步驟:對同一 `--out` 餵 `parked` kind／空步驟／空 lines；看 exit、stderr、目標 sha
- 系統回應:exit 1；`DIAGIR_KIND`／`DIAGIR_EMPTY`／`DIAGIR_LINES`；`knob:` 一句；目標 sha 不變
- 系統外下一步:依旋鈕改 IR 再重跑；不要 git checkout 當正常路徑
- 觀察問題:看到紅之後是否知道改 kind／補標題／收 lines？系統有沒有暗示「exit 非 0 但檔已換」？

### Scenario AC-2（原子交付／中斷仍全舊）
- 使用者角色:產檔器
- 真實目標:看見的要嘛全新、要嘛全舊；半寫不得留下截斷 html
- 起始狀態:目標先是 `LAST-GOOD-SEED`；再跑綠交付；再跑 `--abort-after-tmp`
- 操作步驟:`demo` 的 `AC-2-atomic-good` 與 `AC-2-DIAGIR_ABORT`
- 系統回應:綠交付 exit 0、sha 從 seed 換成完整 `<svg>`；ABORT exit 1、`DIAGIR_ABORT`、目標仍是綠 SVG（不是 `PARTIAL`）
- 系統外下一步:Stage 6 才把三支 `write_text` 接到同一閘
- 觀察問題:中斷後目標是不是截斷檔？`.tmp` 是否取代了目標？

### Scenario AC-3（五列路由；樹不當 vbox）
- 使用者角色:開工 agent
- 真實目標:先選家族再跑對的 API；不能把目錄樹／樹狀 ASCII 收成單盒生命週期
- 起始狀態:`routes` 表；`fig-tree-ascii` 當 lifecycle／behavior-flow 負向
- 操作步驟:跑 `routes` 數五列；再餵樹狀 ASCII
- 系統回應:`count=5`；樹狀 → `DIAGIR_FAMILY` + 旋鈕「查路由表，改呼叫對的產器」
- 系統外下一步:查 2-decision 選定路由表，改 `--family`／產器
- 觀察問題:有沒有任何一步在「猜」家族？有沒有 mermaid 入口？

### Scenario AC-4（Proof Lab 三家族各一正一負）
- 使用者角色:審查人／owner
- 真實目標:可重放樣張對齊現有牙，不是只綠 `lifecycle.json`
- 起始狀態:薄索引 `proto/proof-lab-index.json` 點名既有 fixture + throwaway `vbox-bad-kind.json`
- 操作步驟:跑 `lab`
- 系統回應:lifecycle 正／`DIAGIR_KIND` 負；behavior-flow 正／樹狀 `DIAGIR_FAMILY` 負；dir-tree 正／短 why `DIAGIR_WHY` 負。負向 `last_good_kept=True`
- 系統外下一步:Stage 6 把 vbox 負向補進 `scripts/fixtures/vbox-fig/`，牙仍是現有 `check-*`
- 觀察問題:索引是否另造檢查語言？負向有沒有寫檔？

### Scenario AC-5（預設仍是靜態直式 SVG）
- 使用者角色:owner
- 真實目標:wave-1 不把動畫／Mermaid／Node 當成功條件
- 起始狀態:綠交付後的 `target.svg`
- 操作步驟:讀檔頭；搜 `mermaid`／`<animate`
- 系統回應:直式 `<svg viewBox="0 0 280 …">`；註記 `PROTOTYPE — not production code`；無 mermaid／無 animate
- 系統外下一步:本 slug 後續 Stage 6 仍鎖靜態直式 SVG
- 觀察問題:成功條件有沒有變成「要會動」？

## Result
- **2026-09-12 實跑**（IMPLEMENTER C；tip `1f8d992` = origin/main after #214／#215／#211；throwaway `diagir_proto.py` sha256 `7ad48ee737c83db74367c50ad1bc22b67db803ac81a25d9483795b6e2ca70115`；workdir `/tmp/diagir-stage3-c`）:

| name | exit | code | unchanged | sha_after |
|---|---|---|---|---|
| `AC-2-atomic-good` | 0 | ok | False | `30dcd1e817f488251f76d893b915f891b3e9a3d8b00420571b07ab3ab5528ad2` |
| `AC-1-DIAGIR_KIND` | 1 | `DIAGIR_KIND` | True | 同上（last-good） |
| `AC-1-DIAGIR_EMPTY` | 1 | `DIAGIR_EMPTY` | True | 同上 |
| `AC-1-DIAGIR_LINES` | 1 | `DIAGIR_LINES` | True | 同上 |
| `AC-3-DIAGIR_FAMILY` | 1 | `DIAGIR_FAMILY` | True | 同上 |
| `AC-2-DIAGIR_ABORT` | 1 | `DIAGIR_ABORT` | True | 同上 |
| `AC-4-dir-pos` | 0 | ok | False | `58a3431184130ea8be57477416ba13f11763ee0af562ea6d3cfb52f3155527be` |
| `AC-4-dir-DIAGIR_WHY` | 1 | `DIAGIR_WHY` | True | 同上（dir last-good） |

- seed sha（`LAST-GOOD-SEED`）:`f07882ce4b622ebd834e713058a33515b394f58218b78d04e572940482e8fd3b` → 綠交付後換成完整 SVG。
- 失敗 stderr 樣張（`vbox-bad-kind.json`）:
  ```
  DIAGIR_KIND 第 1 步 kind='parked' 只能是 b／hl／wn
  knob: 把 kind 改回允許值，或改走路由表上的正確家族
  ```
- `routes`: `count=5`；`stage1-scan,stage2-arch,behavior-flow,dir-tree,lifecycle`
- Proof Lab `lab_pass=True cases=6 fail=0`（既有 `lifecycle.json`／`fig-tree-ascii`／`dir-tree/good`／`missing-why` + throwaway `vbox-bad-kind.json`／`behavior-flow-good.json`）
- `AC-5-static-svg=True`；`demo_pass=True`
- G2 Demo 機械閘（刻意紅，禁止假過）:`python3 hooks/_stage3_impl.py diagram-ir-gate` → exit 2；`g2_demo=REJECT`；`Human verdict=NOT_REVIEWED`；無 skip OC。
- 答案:IR 閘／路由表／Proof Lab **形狀成立**（throwaway）；CLI Demo 足夠；正式產器未落地。
- 回寫對象:2-decision Risks「信封欄位未釘／write_text 繞過／vbox 無獨立負向」＋確認紀錄「prototype 回寫」。**不送 G2**。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填；Agent 禁代填 ACCEPTED／attestation -->
- Demo date: 2026-09-12（agent 已代跑 CLI；人類尚未親跑）
- Participants: CloudAgent implementer-C（代跑）
- Variant reviewed: CLI-only（無 UI Variant；選定 = `diagir_proto.py`）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED

## Verdict
- 回寫 2-decision：A 的 IR 閘形狀經 throwaway 確認（綠交付原子換檔；六碼紅且不蓋 last-good；旋鈕可見）。D 的五列查找表可印可擋 `DIAGIR_FAMILY`。G 的 Proof Lab 薄索引可重放三家族各一正一負，負向不蓋檔。**第 3 站已行使**；CLI Demo 足夠，無跳過宣告。
- Human verdict = **NOT_REVIEWED**（人未親跑）→ **不得過 G2**，不開 4-spec，不假 attestation。frontmatter `approved` 只表示本站回寫收尾（N5），不是 Demo ACCEPTED。
- throwaway 處置:`proto/diagir_proto.py` 留在本 feature branch 供人重跑；標非正式碼；**不**當 Stage 6 產器。session 產物在 `/tmp/diagir-stage3-c/`，不進 Git。正式碼 Stage 6 再接到既有產器寫路徑與現有牙。
