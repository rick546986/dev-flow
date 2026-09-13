---
feature: requirement-discovery-gaps
stage: 3-prototype
status: draft
owner: rick
updated: 2026-09-13
---

# 3. 原型 — 九條缺口的教師／牙長什麼形？

> Stage 3 依 2-decision「不預先跳過」**執行、不跳過**。Decision 1A–8A 已是核准 Pattern → **1 個可操作 CLI Demo**，不湊假 Variant。
> 本站只鎖**形狀**：活教師九張欄位卡 + 既有三家族牙的紅／綠對照。欄位**名字面**仍依 2-decision 留給 4-spec。
> **不**改 `_templates/`／`skills/`／`example/`／守衛正本。**不**改 STATUS／HISTORY。**不**開 4-spec、**不**發明 G2。
> Human verdict 由參與 Demo 的人類親填；Agent 禁代填 ACCEPTED。本 hop 人類尚未親走 → `NOT_REVIEWED`，status 留 draft。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context -->
- [ ] 有新的前端流程（本題是模板教師＋CLI 牙，沒有新產品畫面）
- [x] 改變使用者下一步（討論者要分欄寫結果／構想；發現題不能先塞推薦；Fast 寫 4-spec 前先答六問）
- [x] 涉及角色交接（討論 agent ↔ 訪談對象 ↔ 收斂者 ↔ owner 核准證據 ↔ Fast 實作者 ↔ G2 reviewer）
- [x] 涉及人工核准（owner 核准事實入口；過期高影響 Assumption 要 OC 才准進 G2；Human verdict 人類親填）
- [x] 涉及等待/退回/逾時（Assumption 驗證期限；lookback 回看日；G2 因過期假設退回）
- [x] 涉及權限差異（核准過的事實進得來；2／3／4／5／6／7 方案檔仍進不去）
- [x] 涉及系統外動作（訪談、SOP／ticket、終端機跑牙、GitHub 審頁）
- [ ] 涉及多種可行互動設計（1A–8A 已 lock；教師＋既有牙是同一條路，不另做 UI Variant）
- [ ] Stage 1 尚有操作流程不確定性（Journey 已清；剩欄位名字面進 4-spec）

→ 命中 6 條:Stage 3 條件式必要,執行(不跳過)。2-decision 無「跳過 Stage 3」流程層 OC。

## Question
2-decision 內部技術選擇「4-spec 再釘」＋ Risk「B-1 manifest 形狀未釘」＋ Risk「新欄被填 Unknown」＋ SC-1～SC-9：在**不改模板／守衛、不開 4-spec**的前提下，throwaway CLI 能否鎖住這三個答案？

1. **教師形**：九條落地時，人要填的最小欄長什麼樣（Goals／Requested 分欄、發現題／裁決題、高影響枚舉＋來源 XOR、Assumption 四欄、verdict 角色／場景、disposition 原文片段、lookback 四欄、evidence manifest、Fast 六問＋去向）。
2. **牙形**：同一形狀掛在既有 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh` 時，缺欄／過期／未核准分別紅什麼；不新造檢查家族、不發 RW-id、不掃 dashboard／API 黑名單。
3. **本 hop 邊界**：正式腳本與模板位元組不變；不把本站輸出當成 G2 PASS。

答案長什麼樣才算回答了：
- 印出 `TEACHER_CARDS 9`，A-1…A-7／B-1／B-2 各一張。
- 16 個對照 fixture 的 expect／got 全對（`SHAPE_MATCH True`）。
- `NO_NEW_FAMILY`／`NO_RW_ID`／`NO_G2_INVENTED` 皆 True；正本 `scripts/`／`_templates/` **沒有**因本站被改。

## Method
- 實驗位置:session scratchpad `/tmp/rdg-stage3-proto/rdg_shape.py`（**PROTOTYPE — not production code**；不進 Git；正式射程延伸留 Stage 6，沿用 OC-1 的既有三家族）
- Demo 形式:**可執行 CLI flow**（使用者實際跑 throwaway，不是只看靜態說明）
- Pattern 已核准（1A–8A）→ **1 個 Demo**，不做假 Variant
- 驗法:`python3 /tmp/rdg-stage3-proto/rdg_shape.py`；看 `TEACHER_*`／`FIXTURE`／`SHAPE_MATCH`
- 本站**不** import、不 patch、不改 `scripts/check-realworld.sh`／`scripts/check-spec-gate.sh`／`hooks/devtalk-guard.sh`
- 牙只驗形狀。語意（這句算不算高影響、來源是否真的支持主張、六問是否謊填「否」）留給 G1／G2 人審

意圖中的教師卡（4-spec 再釘字面；本站只鎖形）：

```
## Goals
- <人的結果>                    # 不寫畫面／API／元件通道
## Requested solution（候選，未定案）
- <構想>

發現題: <開放問句>              # 禁推薦
裁決題: <取捨> 選項／推薦       # 事實覆述之後才可

主張: <句>
狀態: Observed|Reported|Inferred|Assumption|Conflict
來源類型 / as-of / 角色或範圍 / 支持哪一段 / 限制
# 來源 XOR Assumption+期限；點頭紀錄不得當唯一來源

[Assumption] <句>
- 若為假會影響:  / 影響級:  / 怎麼驗:  / 何時／由誰驗:
- 狀態: open | resolved | oc-accepted

- Human verdict: ACCEPTED
- 角色: <Actor>    - 場景: <AC-id>
- Verdict attestation: human:<名> @ <YYYY-MM-DD>

| 引用（Stage 1 原文片段） | 去向 | 理由 |
| Journey「…」 | 本方案處理|刻意維持|Non-Goal|另開 slug|仍待驗 | … |

- 回看日期:  / 回看 owner:  / 資料來源:  / 低於何值要重開:

## Evidence manifest（本輪）
| 想找哪類 | 原因 | 路徑／來源 | 核准 |
| SOP／案例 | … | path | human:<名> @ <date> | 未核准 |

## Early risk triage（進 Stage 4 前）
下一步 / 權限／核准 / 等待語意 / 交接 / 系統外 / 中斷恢復
命中去向: 升 full | fast+mini | Owner Call
全否 + 已有 approved spec + 不改語意 → 維持 Fast
```

## 結構圖
- throwaway CLI 先印九張教師卡再咬牙（選定）
- realworld 地板：分欄／來源 XOR／verdict／disposition／lookback
- spec-gate：過期假設／Fast 六問
- devtalk-guard：核准入口、方案檔仍禁
- 不新造檢查家族、不發 RW-id
- 正本模板／守衛未改、不開 4-spec

## Demo Script

### Scenario AC-1（教師：結果與構想分欄）
- 使用者角色:討論 agent／G1 reviewer
- 真實目標:人能分辨「要達成的工作結果」與「帶來的解法構想」
- 起始狀態:scratchpad 兩份對照：`goal-mixed`（Goals 寫「我要 dashboard」、Requested 空）／`goal-split`（Goals 寫結果、構想在 Requested）
- 操作步驟:跑 throwaway；看 `goal-mixed`／`goal-split` 兩行
- 系統回應:`goal-mixed` fail（缺 Requested 欄，不是因為寫了 dashboard）；`goal-split` pass
- 系統外下一步:正本模板本站不改；落地時才把分欄寫進 1-discussion 教師
- 觀察問題:看到紅之後知道要補的是「另欄」嗎？系統有沒有暗示「不准寫 dashboard 這個詞」？（不該有；黑名單已拒）

### Scenario AC-4（牙：過期 Assumption 擋 G2 形）
- 使用者角色:G2 reviewer
- 真實目標:高影響假設到期仍未驗時，人進不了 G2
- 起始狀態:`assum-expired`（high、期限 2026-09-01、open、無 OC）／`assum-oc`（同樣過期但有 OC 接受風險）；旁掛 `claim-bare`／`claim-src`（地板：來源 XOR）
- 操作步驟:跑 throwaway；看 spec-gate 兩行與 realworld 主張兩行
- 系統回應:`assum-expired` fail；`assum-oc` pass；`claim-bare` fail；`claim-src` pass。家族名是 `check-spec-gate`／`check-realworld`，不是新腳本
- 系統外下一步:退回補驗證或寫 Owner Call；不要當警告繼續送 G2
- 觀察問題:拒絕是否看得見？有沒有暗示「模板有欄就綠、填檔仍過」？等待／過期狀態清不清楚？

### Scenario AC-5（教師：verdict 一行角色場景）＋ AC-6／AC-7
- 使用者角色:Demo 參與者／後讀者
- 真實目標:一眼看出驗了誰、哪場；痛點有去向；出貨時留下回看四欄
- 起始狀態:`verdict-name`（只有 ACCEPTED）／`verdict-role-scene`（角色=訪談對象、場景=AC-2）；`disp-empty`／`disp-cited`；`lookback-3`／`lookback-4`
- 操作步驟:跑 throwaway；逐對看 fail／pass
- 系統回應:缺角色／場景、去向空、回看缺門檻 → fail；三組補齊 → pass。不做 Actor Coverage 全表；不發 RW-id；不另造 lookback 檔
- 系統外下一步:人類親填 verdict＋attestation（本 hop 未填）。disposition「本方案處理」落到 R/S 是 Stage 4 的事
- 觀察問題:只寫姓名日期會不會被當成已驗過代表角色？空 disposition 能不能 silently 過？權限上誰能代填 attestation？（不能；Agent 禁寫）

### Scenario AC-8（牙：核准證據 vs 方案檔）＋ AC-9
- 使用者角色:討論 agent／Fast 實作者
- 真實目標:owner 核准的事實讀得到；方案檔仍打不開；Fast 六問未收束不能開寫 4-spec
- 起始狀態:`ev-unapproved`（路徑在、未核准）／`ev-ok-block-spec`（核准 SOP + 試圖讀 4-spec）；`fast-blank`／`fast-all-no`
- 操作步驟:跑 throwaway；看 `devtalk-guard` 與 `check-spec-gate` 四行
- 系統回應:未核准 fail；核准事實 pass 且 4-spec 仍標記 blocked；六問空白 fail；六問全否＋維持 Fast pass
- 系統外下一步:先列「想找哪類＋原因」等 owner 核准；命中六問則等 owner 裁升 full／mini／OC。本站不寫 4-spec
- 觀察問題:系統有沒有暗示「規定了但讀不到」或「空白六問也能 Fast」？中斷後（沒核准、沒去向）能不能恢復？系統外的 SOP 是否可追蹤到核准行？

## Result
- **2026-09-13 實跑**（CloudAgent Implementer C；tip `77ccb52` = origin/main #269 之後；scratchpad sha256 `b7f8703a35bf01f70c123e3de42dc4dfba1fd010679d09b6e52785e2087fa932`）。回寫對象:2-decision 內部技術選擇「4-spec 再釘」＋ Risk「B-1 manifest 形狀未釘」＋ Risk「新欄被填 Unknown」＋ SC-1～SC-9 形狀。本 hop 依 brief **只落本目錄 3-prototype**，不改正本 2-decision 正文（人類 Demo 後再回寫確認紀錄）。

| fixture | 家族 | expect | got |
|---|---|---|---|
| `goal-mixed` | check-realworld | fail | fail |
| `goal-split` | check-realworld | pass | pass |
| `claim-bare` | check-realworld | fail | fail |
| `claim-src` | check-realworld | pass | pass |
| `verdict-name` | check-realworld | fail | fail |
| `verdict-role-scene` | check-realworld | pass | pass |
| `disp-empty` | check-realworld | fail | fail |
| `disp-cited` | check-realworld | pass | pass |
| `lookback-3` | check-realworld | fail | fail |
| `lookback-4` | check-realworld | pass | pass |
| `assum-expired` | check-spec-gate | fail | fail |
| `assum-oc` | check-spec-gate | pass | pass |
| `fast-blank` | check-spec-gate | fail | fail |
| `fast-all-no` | check-spec-gate | pass | pass |
| `ev-unapproved` | devtalk-guard | fail | fail |
| `ev-ok-block-spec` | devtalk-guard | pass | pass |

- `TEACHER_CARDS 9`；`FIXTURE_ROWS 16`；`SHAPE_MATCH True`；`NO_NEW_FAMILY True`；`NO_RW_ID True`；`NO_G2_INVENTED True`
- `goal-mixed` 紅在「Requested 欄空」，**不是** dashboard 字黑名單（Decision 已拒誤殺領域詞）
- throwaway 零 import 正式檢查腳本；`git status` 於實驗當下未改 `scripts/`／`_templates/`／`hooks/`
- 答案:教師／牙形狀**成立**（throwaway）；CLI Demo 足夠；正式教師與牙未落地。**不是 G2**。
- `hooks/_stage3_impl.py` 對本檔可能印 `g2_demo=PASS`：那是誤咬 2-decision「不預先跳過／無跳過 Stage 3」同時含「Stage 3」+「跳過」字樣，**不是**本 hop 的 G2，也不是 ACCEPTED。本檔 Human verdict 仍是 NOT_REVIEWED。本 hop 不改正本 2-decision 去消誤咬。

## User Demo Feedback
- Demo date: 2026-09-13（agent 代跑 CLI；人類尚未親走）
- Participants: CloudAgent Implementer C（代跑）
- Variant reviewed: CLI-only（無 UI Variant；選定 = 教師卡＋既有三家族牙）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps: 人類尚未按 Demo Script 走完四場
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED

## Verdict
- 回寫 2-decision：內部技術選擇「4-spec 再釘」的**形狀**已由 throwaway 鎖住（九張教師卡＋三家族 16 對照）。欄位名字面、高影響抽樣規則仍待 4-spec，本站不開 4-spec、不發明 G2。Risk「B-1 manifest 形狀未釘」→ 本輪清單四欄（想找／原因／路徑／核准）+ 方案檔仍禁。Risk「新欄被填 Unknown」→ 牙只驗形狀；語意留給人審。
- 本 hop brief：只落 Stage 3 原型文件；不改 2-decision 正文、不改 STATUS／模板。確認紀錄一行等人類 Demo 後再寫。
- Human verdict = NOT_REVIEWED → frontmatter status 留 **draft**（≠ ACCEPTED 不得改 approved）。機械閘若因既有「不預先跳過」句印 PASS，視為誤咬，**不得當 G2**。
- throwaway 腳本處置:留在 session `/tmp/rdg-stage3-proto/`，**不進 Git**；形狀已錄於 Question／Method／Result。正式碼 Stage 6 再把射程伸進既有檢查家族。
