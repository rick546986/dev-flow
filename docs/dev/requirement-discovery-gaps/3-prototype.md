---
feature: requirement-discovery-gaps
stage: 3-prototype
status: draft
owner: rick
updated: 2026-09-13
---

# 3. 原型 — 分欄／題標／去向列／六問長什麼樣？

> Stage 3 依 2-decision「不預先跳過」**執行、不跳過**。Decision 1A–8A 已是核准 Pattern → **1 個可操作 Demo**，不湊 UI Variant。
> 本站只鎖 Stage 2 留下的**填法形狀**：Goals vs Requested 兩節、發現／裁決題標、disposition 三欄列、Fast 六問清單、A-5 LIGHT 一行角色／場景。
> **不**改 `_templates/`／`skills/`／守衛／範例正本（那是 Stage 6）。不開 4-spec。不送 G2／G3。不發明 G2。不重開 OC-1…OC-6。
> Human verdict 由參與 Demo 的人類親填。本 hop Agent **不代填** ACCEPTED、不寫 attestation。frontmatter 留 `draft`。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context -->
- [ ] 有新的前端流程（本題是方法論填檔形，沒有產品畫面）
- [x] 改變使用者下一步（討論 agent 發現題不得先塞推薦；Fast 實作者進 4-spec 前要填六問；Goals 把構想挪到 Requested）
- [x] 涉及角色交接（訪談對象 → 討論 agent → 收斂者 → owner → Fast 實作者 → G2 reviewer）
- [x] 涉及人工核准（evidence manifest 要 owner 核准路徑；Fast 命中由 owner 裁 full／mini／OC；Human verdict 人類親填；disposition 空列 G1 人指）
- [x] 涉及等待/退回/逾時（過期高影響 Assumption 退回擋 G2；lookback 等到約定日；等 owner 核准事實路徑）
- [x] 涉及權限差異（討論 agent 未核准路徑不得讀；2／3／4／5／6／7 仍禁；Fast 實作者只能寫 4-spec）
- [x] 涉及系統外動作（訪談在口頭／Email；owner 用 GitHub／審核筆記；lookback 用系統外資料來源）
- [ ] 涉及多種可行互動設計（1A–8A 已 lock；單一路徑填檔，不湊 Variant）
- [x] Stage 1 尚有操作流程不確定性（Journey 序已清；未清的是人怎麼填分欄／題標／去向列／六問——本站要答的就是這個）

→ 命中 7 條:Stage 3 條件式必要,執行(不跳過)。2-decision 無「跳過 Stage 3」流程層 OC。

## Question
2-decision 內部技術選擇「4-spec 再釘」＋ Risk「新欄被灌水／Fast 六問變儀式／B-1 manifest 形狀未釘」：在**不改模板正本**的前提下，throwaway 能否鎖住這四個答案？（A-5 LIGHT 一併示形，不重開 8A）

1. **Goals vs Requested（SC-1／AC-1）**：兩節並存。Goals 只寫工作結果；構想進 Requested 並標未定案。把「我要 dashboard」寫進 Goals 的對照稿，人（或形狀檢查）能指出「構想在錯欄」。**不是** dashboard／API 黑名單（A-1 已拒）。
2. **發現 vs 裁決題標（SC-2／AC-2）**：發現題前綴「發現｜」、問句不附推薦／選項；裁決題前綴「裁決｜」、可附選項／差異／推薦。
3. **disposition 列（SC-6／AC-6）**：一列 = 引用 Stage 1 原文片段 + 去向（本方案處理／刻意維持／Non-Goal／另開 slug／仍待驗）+ 一句理由。空去向 = 未處置。不另發 RW-id。
4. **Fast 六問（SC-9／AC-9）**：進 4-spec 前六列（下一步／權限／等待語意／交接／系統外／中斷恢復），每列 命中 + 一句。命中必有去向（升 full／fast+mini／OC 接受風險）。全否 + 已有 spec + 不改語意純視覺 → 維持 Fast（OC-6）。「只改狀態字、把等待顯示成完成」必須命中等待語意。空白不得當已分診。

答案長什麼樣才算回答了：
- 十三份 fixture 的 `want`＝`got`（錯欄／發現附推薦／空去向／六問空白／命中無去向／只剩 attestation → 紅；對欄／發現開問／裁決可薦／有去向／純視覺／等待當完成有去向／LIGHT 一行 → 綠）。
- `WAIT_AS_DONE_HITS True`；`NO_BLACKLIST True`；`DESTS 5`；`FAST_Q 6`。
- 可點擊 HTML 能走完 AC-1／2／6／9／5，每場先勾觀察才能下一場。
- 正式 `_templates/`／`skills/`／守衛／範例**沒有**因本站被改。
- OC-1…OC-6 本文與 ✅ 狀態未改。

## Method
- 實驗位置:本 feature branch `docs/dev/requirement-discovery-gaps/proto/`（**PROTOTYPE — not production code**）。
  - 可執行 CLI：`proto/shape_lab.py`
  - 可點擊 HTML：`proto/shape-lab.html`（狀態流程模擬器；不是產品 UI）
- Demo 形式:**可點擊 HTML prototype** + **可執行 CLI flow**（人實際點／跑，不是只看靜態表）
- Pattern 已核准（1A–8A）→ **1 個 Demo**，不做假 Variant
- 驗法:`python3 proto/shape_lab.py demo`；瀏覽器打開 `proto/shape-lab.html`，五場各勾觀察後往下
- 本站**不**改 `_templates/`、`skills/`、`example/`、`scripts/check-*.sh`、`hooks/devtalk-guard.sh`
- 錯欄偵測只認**對照稿標籤**（fixture `want=wrong-column`），不掃描全域禁詞
- 次要形（4-spec 仍再釘檔名／字面）：lookback 四欄、evidence 五枚舉、manifest 建議檔名 `docs/dev/<slug>/evidence-manifest.md`

意圖中的填檔塊（非正式欄位名；4-spec 再釘）：

```
## Goals
- <工作結果，不指定畫面／API／元件>

## Requested solution（未定案）
- <構想>

發現｜<開放問，無推薦>
裁決｜<已核事實上的取捨；可附選項／差異／推薦>

| 引用（Stage 1 原文片段） | 去向 | 理由 |
| Journey「…」 | 本方案處理｜刻意維持｜Non-Goal｜另開 slug｜仍待驗 | <一句> |

| 問 | 命中 | 一句 | 去向 |
| 下一步／權限／等待語意／交接／系統外／中斷恢復 | 是／否 | <必填> | 命中→升 full｜fast+mini｜OC 接受風險；全否純視覺→維持 Fast |

- 角色／場景: 角色:<Actor>；場景:<AC-id 一句>
```

## 結構圖
- 填 Goals／Requested 兩節（選定）
- 發現題標「發現」、裁決題標「裁決」
- disposition 引用｜去向｜理由
- Fast 六問清單
- Human verdict 一行角色／場景

## Demo Script

### Scenario AC-1（Goals vs Requested 分欄）
- 使用者角色:討論 agent
- 真實目標:人讀 Stage 1 能分辨工作結果與解法構想
- 起始狀態:左卡 = 範例教師「Goal = dashboard」；右卡 = 「到期前有人處理續約」+ Requested「站內卡片（未定案）」
- 操作步驟:打開 `proto/shape-lab.html` 走 AC-1；或跑 `python3 proto/shape_lab.py demo` 看 `goals-wrong`／`goals-right`
- 系統回應:錯欄 `got=wrong-column`；對欄 `got=ok`。HTML 不把 dashboard 當禁詞，只並排放對照
- 系統外下一步:Stage 6 才改 `_templates/1-discussion.md` 與範例 Goals。本站不改
- 觀察問題:看到左卡後知道構想該搬去哪一節嗎？系統有沒有暗示「不准寫 dashboard」？

### Scenario AC-2（發現 vs 裁決題標）
- 使用者角色:訪談對象
- 真實目標:被問「上次真的怎麼做」時，題目本身不先塞答案
- 起始狀態:錯問「上次怎麼追到期？推薦：做 dashboard」；對問前綴「發現｜」／「裁決｜」
- 操作步驟:HTML AC-2；CLI `discover-wrong`／`discover-right`／`adjudge-right`
- 系統回應:發現附推薦 → `recommend-on-discover`；發現開問與裁決可薦 → `ok`
- 系統外下一步:Stage 6 改 `N3-probe` 硬規則與指南對稱句。本站不改 skill
- 觀察問題:題目前綴看不看得出來這題能不能附推薦？有沒有暗示受訪者該選 dashboard？

### Scenario AC-6（disposition 列）
- 使用者角色:收斂者
- 真實目標:Journey 痛點不能無聲消失
- 起始狀態:本 slug 2-decision 已有去向帳；Demo 加一列空去向
- 操作步驟:HTML AC-6 看第四列空去向；CLI `disp-empty`／`disp-ok`
- 系統回應:空去向 `empty-dest`；三欄齊且去向 ∈ 五態 → `ok`
- 系統外下一步:G1 人指未處置列；Stage 4 才把「本方案處理」接到 R/S。不發明 RW-id
- 觀察問題:空去向一眼看不看得出？會不會以為散文「有處理」就算數？

### Scenario AC-9（Fast 六問）
- 使用者角色:Fast 實作者
- 真實目標:進 4-spec 前看過六種互動風險；等待誤標不能靠檔數少混過
- 起始狀態:三份對照——空白、純改底色、只改狀態字把等待顯示成完成
- 操作步驟:HTML AC-9 走「等待當完成」表；CLI `fast-blank`／`fast-visual`／`fast-wait-as-done`／`fast-hit-no-dest`
- 系統回應:空白 `blank`；命中無去向 `hit-no-dest`；純視覺 `ok`＋維持 Fast；等待當完成 `等待語意=是` 且去向「升 full」，`WAIT_AS_DONE_HITS True`
- 系統外下一步:Stage 6 把六問接到 `check-spec-gate.sh` 射程。本站不改守衛
- 觀察問題:看到「已完成」時知道這是等待語意被改、不是換色嗎？空白六問能不能開寫規格？

### Scenario AC-5（A-5 LIGHT 一行）
- 使用者角色:後讀者／owner
- 真實目標:一行內能答「驗了誰、驗了哪場」
- 起始狀態:左卡只 ACCEPTED + attestation；右卡加「角色／場景」
- 操作步驟:HTML AC-5；CLI `verdict-attest-only`／`verdict-light`
- 系統回應:缺角色場景 `missing-role-scene`；有「角色:…；場景:…」→ `ok`。本頁不讓人按 ACCEPTED
- 系統外下一步:人類走完 Demo 後，在本檔填 Human verdict + attestation + 角色／場景。Agent 不代填
- 觀察問題:只看到姓名日期，能不能答驗了哪個 Actor、哪條 AC？

## Result
- **2026-09-13 實跑**（CloudAgent Implementer A；tip `77ccb52` = origin/main #269 後）。CLI `python3 proto/shape_lab.py demo` exit 0。throwaway sha256 `568fe0b16f21c27c03abe5a91c51b2a14298bbdcb880a0b200f5c0c00b88d7e4`（`shape_lab.py`）；HTML `493e92c653b2a8c5a4887a8b4b821d636d89bc9bc58c3460fe81b953cfffa46a`。回寫對象:2-decision「4-spec 再釘」形狀＋確認紀錄「prototype 回寫」。**不重開 OC**。

| fixture | want | got | 對應 |
|---|---|---|---|
| `goals-wrong` | wrong-column | wrong-column | AC-1 錯欄 |
| `goals-right` | ok | ok | AC-1 分欄 |
| `discover-wrong` | recommend-on-discover | recommend-on-discover | AC-2 發現附推薦 |
| `discover-right` | ok | ok | AC-2 發現開問 |
| `adjudge-right` | ok | ok | AC-2 裁決可薦 |
| `disp-empty` | empty-dest | empty-dest | AC-6 空去向 |
| `disp-ok` | ok | ok | AC-6 三欄 |
| `fast-blank` | blank | blank | AC-9 空白 |
| `fast-visual` | ok | ok | AC-9／OC-6 純視覺 |
| `fast-wait-as-done` | ok | ok | AC-9 等待當完成 |
| `fast-hit-no-dest` | hit-no-dest | hit-no-dest | AC-9 命中無去向 |
| `verdict-attest-only` | missing-role-scene | missing-role-scene | AC-5 只有 attestation |
| `verdict-light` | ok | ok | AC-5 LIGHT |

- `WAIT_AS_DONE_HITS True`；`NO_BLACKLIST True`；`DESTS 5`；`FAST_Q 6`；`SHAPE_ROWS 13`；`ALL_MATCH True`。
- 次要形（未當主問、只示形）：lookback = 回看日／owner／資料來源／低於何值重開；evidence 枚舉 = Observed／Reported／Inferred／Assumption／Conflict + 來源 XOR Assumption+期限，點頭≠來源；manifest 檔名建議 `docs/dev/<slug>/evidence-manifest.md`。高影響抽樣仍是人判（OC-5），本站不機器抽。
- 已知機械噪音：2-decision 原句「無跳過 Stage 3」同時含「Stage 3」與「跳過」，`hooks/_stage3_impl.py` 會把 NOT_REVIEWED 誤報成 `SKIPPED_OWNER_CALL`。回寫時把該**內部技術選擇**句改成不含這對共現（語意不變：命中仍要跑原型）。不改 OC 表、不修守衛、不把誤報當 G2 PASS。
- 答案:1A–8A **填法形狀成立**（throwaway）；HTML+CLI Demo 足夠；正式模板／牙未落地。

## User Demo Feedback
<!-- 人類走完 proto/shape-lab.html 後親填。Agent 禁寫 ACCEPTED、禁填 attestation。 -->
- Demo date: 2026-09-13（agent 代跑 CLI；HTML 待人類點）
- Participants: CloudAgent implementer-A（代跑 CLI）；owner rick（待走 HTML）
- Variant reviewed: 單一路徑填檔（無 UI Variant；選定 = Goals／Requested 兩節 + 發現／裁決標籤 + disposition 三欄 + Fast 六問）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- 角色／場景: （人類親填；建議形 `角色:<Actor>；場景:<AC-id 一句>`）
- Human verdict: NOT_REVIEWED
- Verdict attestation: （人類親填；Agent 不代填）

## Verdict
- 回寫 2-decision：內部技術選擇「4-spec 再釘」改註 Stage 3 原型建議形（非正式欄位名，不升成 OC）：Goals／Requested 兩節；題目前綴「發現｜」「裁決｜」；disposition 引用｜去向｜理由（五態）；Fast 六列問／命中／一句／去向；A-5 加「角色／場景」一行；lookback 四欄字面與 manifest 建議檔名如上。Risk「新欄被灌水」維持牙只驗形狀、語意 G1 抽；Risk「Fast 六問變儀式」維持空白／命中無去向紅；Risk「manifest 形狀未釘」改為原型建議檔名、4-spec 再釘。確認紀錄留「prototype 回寫」行。**OC-1…OC-6 不重開、不改 ✅。**
- Human verdict 本 hop = NOT_REVIEWED；frontmatter status=draft。不送 G2、不開 4-spec、不發明 G2／G3。
- throwaway 處置:本 branch 封存 `proto/shape_lab.py` 與 `proto/shape-lab.html` 供人重跑 Demo。非正式產品程式碼；Stage 6 才接到模板／既有牙。
