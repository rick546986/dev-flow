---
feature: dogfood-ping
stage: 2-decision
status: approved
verdict: PASS
owner: rick-dev-flow
reviewers: [user]
updated: 2026-09-10
baseline: tip 0a89ec8 (含 #160 Stage6 牙 + #162 主機分流)
contract: 2.0.0
---

# 2. 收斂 — dogfood-ping（整套模板試跑）

> 把 `1-discussion.md` 的 lean 收成 Decision。G1 已核:`verdict` PASS、`status` approved、OC-1～OC-4 ✅。契約維持 `2.0.0`。本 hop 不升 plugin、不碰 `#163`／host-stack-fit 正本、不做假 PreToolUse。
> Stage 1 lean（方向 A + 跑 Stage 3 + 合 main 當 Example）由 owner 2026-09-10 口述；本檔改口成 Decision，不回改正本討論。
> Stage 3 已跑（CLI throwaway Demo）；答案見下方確認紀錄。正式 `scripts/dogfood-ping.sh` 仍留 Stage 6。

## Approaches Considered

### 決策點：產物形狀
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A | 單檔 `scripts/dogfood-ping.sh`：印 `dogfood-ok`、exit 0 | 極小可觀測；能走 Stage 6 寫碼／審核分流 | 新增 `scripts/*.sh` 必碰 file-map 地板 | 低 | `1-discussion.md` Goals 首條；Approaches A；Context file-map `EXPECTED_MAPPED_FILES`。成本 `[Assumption]` |
| B | 只寫 docs／報告，不交可執行腳本 | 零地板、零 CI 風險 | 測不到 Stage 6「執行者 ≠ reviewer」；Goals 的可觀測題落空 | 低 | `1-discussion.md` Approaches B 劣「測不到 Stage 6」；Goals「走完 1→7」含 Stage 6 |
| C | 另開 scratch repo 隔離試跑 | 不污染本包地板 | 測不到本包收據牙／主機分流／file-map | 高 | `1-discussion.md` Approaches C 劣「測不到本包牙」；Context tip 能力都在本包 |

### 決策點：Stage 3
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| S3-run | **跑 Stage 3**，不跳過 | 整套 1→7 真實過閘；對準 dogfood 目的 | 多一站產物與審視時間 | 中 | `1-discussion.md` HISTORY「不跳過 Stage 3」；Q2 owner：**不跳過**；Goals「含 Stage 3」 |
| S3-skip | 宣告跳過 Stage 3，直接進 4 | 較短 | 測不到 Stage 3 模板／閘門卡點；違反 owner lock | 低 | `1-discussion.md` Q2 已否決跳過；HISTORY 明示不跳 |

### 決策點：落地位置
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| Ex | 合 main，落點 **Example**（`example/dogfood-ping`） | 之後可當樣張；對準「合 main 當 Example」 | 要整理進 example 樹，勿與進行中 feat 混 | 中 | `1-discussion.md` Q1 owner：合 main，Example；Goals 末條 |
| Branch-only | 只留 feature branch／PR，不合 main | 不佔 example 槽 | 沒有可引用樣張；違反 Q1 | 低 | `1-discussion.md` Q1 已選合 main；Non-Goals 不取代 `#163` 但本 dogfood 仍要落 Example |

## 方案架構圖
```
[A] 單檔 dogfood-ping.sh 印 dogfood-ok(選定)
[S3-run] 跑 Stage 3 不跳過(選定)
[Ex] 合 main 落 example/dogfood-ping(選定)
```

## Decision
採 **A + S3-run + Ex**：本包新增極小腳本 `scripts/dogfood-ping.sh`（印 `dogfood-ok`、exit 0），**跑完 Stage 3（不跳過）**，走完 1→7；Stage 6 寫碼 agent ≠ 審核 agent、預設 Auto；加腳本時同步 file-map／相關地板；完工產物合 main，落點 `example/dogfood-ping`。契約維持 `2.0.0`。不碰 `#163`、不升 plugin、不做假 PreToolUse、不改生產業務邏輯。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| B 只寫 docs | 測不到 Stage 6 執行／審核分流與可觀測 exit；dogfood 目的落空。 |
| C 另開 scratch repo | 隔離後測不到本包收據牙／主機分流／file-map。 |
| S3-skip 跳過 Stage 3 | owner 2026-09-10 已 lock 不跳過；會漏 Stage 3 模板卡點。 |
| Branch-only 不合 main | Q1 已選合 main 當 Example；只留 branch 沒有可引用樣張。 |

## Rationale
dogfood 要證明的是「模板／產器／閘門」能不能整套走完，不是業務功能。A 最小但仍是可執行產物，才能逼 Stage 6 真的寫碼與分流審核；B／C 要麼測不到碼、要麼測不到本包牙。Stage 3 是整套的一環，owner 已明確不跳；落地合 main 進 `example/`，之後才有可指的樣張，而不是另一條永遠開著的 preview branch。

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 加 `scripts/*.sh` 漏同步 file-map／`EXPECTED_MAPPED_FILES` → CI 紅 | Stage 4／6 明確列同步步驟；SC 含地板綠 |
| 與 `#163` 並行攪線 | 本 feat 分線；Decision／Non-Goals 釘死不碰 host-stack-fit 正本與 G3 |
| 本機 `gh` 未登入，遠端節奏斷 | PR／閘門走 CloudAgent／已登入主機；本機只寫稿 |
| Q3 Verify 掛點未定，後期各寫各的 | OC-1 先收窄「至少一條可自動跑」；是否進 selftest 可在 4-spec 再釘 |
| 把 #159 Stage 5 模板欄一併塞進來變大 | OC-2：Intent 白話先寫，模板欄另票 |
| Stage 2 審頁「方案依據」超寬橫表（手機裁切） | 另開 `#165`；本 dogfood 不修產器，只記 DOGFOOD-NOTES |

## Success Criteria
- SC-1：`scripts/dogfood-ping.sh` 執行印出 `dogfood-ok` 且 exit 0。
- SC-2：本 feat 留下 Stage 1→7 產物（**含 Stage 3**），無「跳過 Stage 3」流程宣告。
- SC-3：Stage 6 紀錄可指出寫碼 agent ≠ 審核 agent，且執行側預設 Auto。
- SC-4：新增腳本後 `scripts/check-file-map.sh`（或等價地板檢查）綠。
- SC-5：有一份「模板試跑報告」（哪站卡、哪句難懂），可被人讀。
- SC-6：合 main 後可在 `example/dogfood-ping` 找到對應樣張（或等價 Example 落點）。
- SC-7(Non-Goal)：未改 `#163`／host-stack-fit 正本；契約仍 `2.0.0`；無假 PreToolUse；無生產業務邏輯變更。

## Scope & Non-Goals(定稿)
- In：A 單檔腳本；跑 Stage 3；1→7 全走；file-map／地板同步；試跑報告；合 main → `example/dogfood-ping`。
- Out：`#163` G3／PF-0；升契約／bump plugin；假 PreToolUse；生產業務邏輯；另開 scratch repo；只寫 docs 不交腳本；固化 #159 Stage 5 模板欄（Intent 白話除外，見 OC-2）；修 `#165` Stage2 方案依據超寬表（另票）。

## Owner Calls(自判裁決,已核)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | Verify **至少一條可自動跑**（腳本本身或最小測試）；是否掛進 `devflow-check`／selftest 本輪可後置到 4-spec。使用者只被問到 Q3 未定；「至少可自動跑」是 owner 對 `[~]` 的收窄 | dogfood 要可觀測；純手動無法當回歸牙 | `1-discussion.md` Q3 `[~]` 假設句；Goals 可觀測題 | 改成純手動；SC-1／回歸入口要重寫 | ✅ |
| OC-2 | Stage 5 **Intent 白話本輪先寫**；#159 模板欄位固化另票。承接 Q4 `[>]` | 避免本 dogfood 變模板基建大包 | `1-discussion.md` Q4 建議句；Non-Goals 不順便升契約 | Scope 加上改 Stage 5 模板；與試跑纏在一起 | ✅ |
| OC-3 | 腳本路徑固定 `scripts/dogfood-ping.sh`，並同步 file-map／相關地板。使用者 Goals 寫「建議」；路徑鎖定是 owner 延伸 | 路徑不定 → Stage 4／6 各自發明；地板必碰已是已知事實 | `1-discussion.md` Goals 首條「建議」；Context file-map 地板 | 改名／改目錄；SC-1／file-map 對照跟著變 | ✅ |
| OC-4 | 本 dogfood **不**把產出塞進進行中的 `docs/dev/host-stack-fit/`，Example 落點獨立 `example/dogfood-ping`。使用者已選 Ex；「不混 host-stack-fit 樹」是收窄 | 避免與 `#163` 未結 G3 攪線 | `1-discussion.md` Non-Goals「不解決 #163」；Q1 Example 路徑 | 改塞進既有 feat 樹；審查與 merge 邊界糊掉 | ✅ |

### 內部技術選擇(下層,告知即可)
- 契約維持 `2.0.0`；本 hop 不 bump plugin。
- `1-discussion.md` 保留 lean／「非定案」原文；本檔才改口成 Decision。
- feature branch 不改 `docs/dev/STATUS.md` 表列（除非本站流程另要求）。
- 正式腳本 `scripts/dogfood-ping.sh` 留 Stage 6；Stage 3 只用 throwaway CLI Demo 驗證輸出形狀。
- Stage 2 審頁超寬「方案依據」表另開 `#165`，本 PR 不修。

## ADR 晉升檢查
- 難逆轉:否（腳本可刪；Example 可搬；G3 前可改 Decision／OC）
- 反直覺:否（極小腳本 + 整套閘門是字面 dogfood）
- 真 trade-off:是（碰 file-map 地板 vs 只寫 docs 測不到 Stage 6）
→ 晉升:**否**（三條件未全中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-10 | owner lean 鎖：產物 A、Stage 3 = S3-run、落地 = Ex；本檔三個決策點對應該鎖板
- Stage 1 改口 | 2026-09-10 | 1-discussion 仍 in-review、Q3 `[~]`／Q4 `[>]`；本檔改口為 Decision。不回改正本討論
- G1 | 2026-09-10 | owner 在 chat 明示 Treat G1 as PASS（locked package A + S3-run + Ex）；OC-1～OC-4 ✅。owner 自審(有記錄)；reviewers: [user]
- prototype 回寫 | 2026-09-10 | Stage 3 已行使：throwaway CLI Demo 印出 `dogfood-ok`、exit 0；**CLI Demo 足夠**（方向 A 已核准 Pattern，無 UI Variant）。SC-1 輸出形狀確認；正式腳本仍 Stage 6。見 `3-prototype.md`。Human Demo Feedback／Human verdict 待 owner 親填（Agent 未代填）。
