---
feature: integration-before-verdict
stage: 3-prototype
status: draft
owner: rick
updated: 2026-09-12
---

# 3. 原型 — 填檔牙與 Stage 7 序長什麼樣？

> Stage 3 依 2-decision「不預先跳過」**執行、不跳過**。Decision A + AS-1 + T-now 已是核准 Pattern → 1 個可操作 CLI Demo，不湊 UI Variant。
> tip（#202／#207）模板／指南／節點鏈**已經**是 2c 整合 → 2d Fresh。本站不重編號、不重寫整合腳本演算法、不落地 Stage 6 守衛碼。
> 正式牙延伸（`check-stage67` ST 射程到填好的 7-review）**不**在本站寫進 `scripts/`；本站只用 throwaway 證明結論形狀。
> Human verdict 由參與 Demo 的人類親填；Agent 禁代填 ACCEPTED／attestation。不送 G2／G3、不發版、不碰 `#196`／diagram-ir-gate。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context -->
- [ ] 有新的前端流程（本題是清單／CLI 牙，無新前端）
- [x] 改變使用者下一步（reviewer 見 `ALREADY_SYNCED` 必須重綁 SHA 或本項 FAIL，不能只寫「證據不算數」就勾；Fresh 只能在整合之後）
- [x] 涉及角色交接（reviewer 寫 7-review ↔ merger 合 `INTEGRATION_SHA` ↔ owner 簽 G3）
- [x] 涉及人工核准（重綁 vs FAIL 是人裁；G3 Human verdict 綁送審樹）
- [x] 涉及等待/退回/逾時（等整合分支座標；兩次腳本座標不同就退回重算）
- [x] 涉及權限差異（reviewer 改 HEAD 僅限 2c；Verdict 後禁改碼；merger 才合整合分支）
- [x] 涉及系統外動作（git merge、GitHub PR、終端機跑整合腳本／gauntlet）
- [ ] 涉及多種可行互動設計（A + AS-1 + T-now 已 lock；單一路徑 CLI）
- [ ] Stage 1 尚有操作流程不確定性（Journey 已是 2c→2d→雙軸→Verdict→Exit 文件；剩欄位名進 4-spec）

→ 命中 6 條:Stage 3 條件式必要,執行(不跳過)。2-decision 無「跳過 Stage 3」流程層 OC。

## Question
2-decision Risk「填檔牙形狀未釘」＋ SC-2／SC-3：在**不實作 Stage 6 守衛碼**的前提下，throwaway CLI 能否鎖住這三個答案？

1. **AS-1 結論形狀**：填好的 7-review 若宣稱 2c 已勾／送 G3，且記 `ALREADY_SYNCED`，則只能「重綁 Final Fresh 的 Source SHA（≥7 hex）」或「本項 FAIL」；只寫「證據不算數／輸出不算數」必須紅。
2. **發動時機**：`N_A_NO_INCOMING` 與未勾 2c 的 draft **不預先紅**。
3. **Stage 7 序／活教師改口**：意圖序是 2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 只准文件；example／manifest／腳本檔頭的舊「2c = Fresh／gauntlet／Exit Checklist 工具」句，改口後 needle 必須歸零。

答案長什麼樣才算回答了：
- 五份 scratchpad 填檔對照的 exit 碼符合上表（void-only=1；rebind／FAIL／n-a／draft=0）。
- 現樹活教師路徑 needle > 0；意圖改口副本 needle = 0。
- 正式 `scripts/` 守衛**沒有**因本站被改。

## Method
- 實驗位置:session scratchpad `/tmp/ibv-stage3-proto/`（**PROTOTYPE — not production code**；不進 Git；正式射程延伸留 Stage 6，沿用 OC-1 的 `check-stage67` 家族）
- Demo 形式:**可執行 CLI flow**（使用者實際跑 throwaway，不是只看靜態說明）
- Pattern 已核准（A + AS-1 + T-now）→ **1 個 Demo**，不做假 Variant
- 驗法:`python3 /tmp/ibv-stage3-proto/as1-filled-tooth.py <fixture.md>`；對活教師加 `--teacher <path>…`
- 本站**不**改 `example/`、`manifests/`、`scripts/devflow-integration-regression.sh` 正本（只讀、只掃）

意圖中的填檔結論塊（4-spec 再釘欄位名；本站只鎖形狀）：

```
## 2c 整合結論
- STATUS: ALREADY_SYNCED
- FORK / HEAD / INTEGRATION / REF: <腳本三 SHA + canonical ref>
- 恢復: 重綁 Final Fresh。Source SHA: <hex≥7>
  或: 本項 FAIL
```

發動：宣稱 2c 已勾（`[x]` 整合／`結論:STATUS=ALREADY_SYNCED`／`verdict: PASS`／`status: approved`）且正文有 `ALREADY_SYNCED`。n-a 與 draft 未宣稱 → no-fire。

## 結構圖
```
2c 整合回歸（腳本只算只判）
        |
        +-- N_A_NO_INCOMING --> 記 n-a --> 2d
        +-- SYNC_REQUIRED_* --> 合 INTEGRATION_SHA + 測 --> 2d
        +-- ALREADY_SYNCED ----+
                               |-- 重綁 Source SHA --> 2d
                               |-- 本項 FAIL --------> 停
                               +-- 只寫「不算數」----> 牙紅
2d Final Fresh（Source SHA = HEAD）
        |
雙軸 + 現象
        |
Verdict（禁再改碼）
        |
Exit 只准文件
```

- 2c 整合回歸（腳本只算只判）
- ALREADY_SYNCED 牙：重綁 SHA 或 FAIL（選定）
- 2d Final Fresh（Source SHA = HEAD）
- 雙軸 + 現象複驗
- Verdict（禁再改碼）
- Exit 只准文件

## Demo Script

### Scenario AC-2（void-only 必須紅）
- 使用者角色:Stage 7 reviewer
- 真實目標:勾 2c 時不能靠「證據不算數」過關
- 起始狀態:scratchpad `fx/void-only.md`（`ALREADY_SYNCED` + 只寫作廢 + `verdict: PASS`）
- 操作步驟:跑 `python3 /tmp/ibv-stage3-proto/as1-filled-tooth.py fx/void-only.md`；看 exit 與 `reason=`
- 系統回應:exit 1；`reason=fail:void-only`
- 系統外下一步:回到 7-review，補重綁 SHA 或改寫本項 FAIL；不要進 Verdict
- 觀察問題:看到紅之後是否知道下一步是重綁還是 FAIL？系統有沒有暗示「寫了作廢就能過」？

### Scenario AC-2（重綁 SHA 或本項 FAIL）
- 使用者角色:Stage 7 reviewer
- 真實目標:恢復路徑二選一都必須綠
- 起始狀態:`fx/rebind-sha.md`（重綁 + `Source SHA: def4567890abc`）；`fx/item-fail.md`（明示本項 FAIL）
- 操作步驟:各跑一次 throwaway；比對 exit
- 系統回應:兩者 exit 0；`pass:rebind-sha:def4567890abc`／`pass:item-FAIL`
- 系統外下一步:重綁者進 2d Fresh（SHA 必須 = 當時 HEAD）；FAIL 者停、從乾淨座標重算
- 觀察問題:SHA 是否看得見、可否對 `git rev-parse HEAD`？FAIL 是否清楚是「這一步停」而不是整份 G3 默默過？

### Scenario AC-2（n-a／draft 不預先紅）
- 使用者角色:Stage 7 reviewer
- 真實目標:牙不要誤殺零新 commit 或還沒勾 2c 的草稿
- 起始狀態:`fx/na-incoming.md`（`N_A_NO_INCOMING`）；`fx/draft-unclaimed.md`（draft、有字但未勾）
- 操作步驟:各跑一次
- 系統回應:兩者 exit 0；`no-fire:N_A_NO_INCOMING`／`no-fire:draft-or-unclaimed`
- 系統外下一步:n-a 直接進 2d；draft 繼續填，不要被提前紅擋住
- 觀察問題:未勾草稿是否被當成已送 G3？

### Scenario AC-3（意圖序 + 活教師改口）
- 使用者角色:owner／採用者（會抄 example）
- 真實目標:活教師不再教 `2c = Fresh`；腳本檔頭不再自稱 Exit Checklist 工具
- 起始狀態:本 tree 現檔（只讀）+ scratchpad 改口副本
- 操作步驟:對現檔跑 `--teacher`；再對改口副本跑一次。另用肉眼確認 `_templates/7-review.md` 頂註「整合回歸」在「Final Fresh Run」之前
- 系統回應:現檔 TEACHER_COUNT=5；改口副本 TEACHER_COUNT=0；模板序 `order_ok=True`
- 系統外下一步:Stage 6 才改 example／manifest／檔頭正本（T-now）；本站不改那些檔
- 觀察問題:改口是否只動編號／檔頭（2c 仍叫整合回歸），沒有重編號整份清單？

### Scenario AC-1（出貨樹=核准樹；對照敘事）
- 使用者角色:owner
- 真實目標:Verdict 綁的 SHA 就是 Exit 後的 HEAD
- 起始狀態:本 Demo 不真合併、不送 G3
- 操作步驟:沿結構圖走 2c→2d→Verdict→Exit；對照「若 Exit 才合，兩 SHA 會不同」
- 系統回應:意圖序把合併留在 2c；Exit 只確認「已在 Fresh 前完成」
- 系統外下一步:本 slug 後續真跑到 Stage 7 才鎖 SC-1；本站只展示序
- 觀察問題:有沒有任何一步暗示 Exit 還能合 `INTEGRATION_SHA`？

## Result
- **2026-09-12 實跑**（CloudAgent scratchpad `/tmp/ibv-stage3-proto/`；tip `630cd41` = #207；throwaway sha256 `e0bcc154c7a9c203aa4de192138a692644327866091377fb8bbdea554dd4455d`）:

| fixture | exit | reason |
|---|---|---|
| `fx/void-only.md` | 1 | `fail:void-only` |
| `fx/rebind-sha.md` | 0 | `pass:rebind-sha:def4567890abc` |
| `fx/item-fail.md` | 0 | `pass:item-FAIL` |
| `fx/na-incoming.md` | 0 | `no-fire:N_A_NO_INCOMING` |
| `fx/draft-unclaimed.md` | 0 | `no-fire:draft-or-unclaimed` |

- 現樹活教師（只讀，未改）：`TEACHER_COUNT 5`
  - `example/contract-expiry-reminder/7-review.md` → `執行清單 2c 的 Final Fresh`
  - `example/contract-expiry-reminder/4-spec.md` → `執行清單 2c gauntlet`
  - `manifests/p4-gauntlet-gates.md` → `執行清單 2c 的文檔化命令`
  - `scripts/devflow-integration-regression.sh` 與 `docs/dev/tools/devflow-integration-regression.sh` → `Exit Checklist.*整合回歸.*計算工具`
- 意圖改口副本：`TEACHER_COUNT 0`（example 2c→**2d** Fresh／gauntlet；腳本檔頭改「步 2c 整合回歸，Fresh 之前，不是 Exit 程序」）
- 模板序未動：`_templates/7-review.md` 頂註 `整合回歸` 仍在 `Final Fresh Run` 之前（`order_ok=True`）
- 答案:AS-1 結論形狀**成立**（throwaway）；CLI Demo 足夠；正式守衛未落地。
- 回寫對象:2-decision Risk「填檔牙形狀未釘」＋內部技術選擇＋確認紀錄「prototype 回寫」。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填；Agent 禁代填 ACCEPTED／attestation -->
- Demo date: 2026-09-12（agent 已代跑 CLI；人類尚未親走 Demo）
- Participants: CloudAgent implementer-A（代跑）；人類 reviewer 未到
- Variant reviewed: CLI-only（無 UI Variant；選定 = AS-1 重綁或 FAIL）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict: NOT_REVIEWED
- Verdict attestation:

## Verdict
- 回寫 2-decision：AS-1 填檔牙形狀經 throwaway CLI 確認（void-only 紅；重綁 SHA／本項 FAIL 綠；n-a 與 draft no-fire）。活教師改口形狀已展示，正本未改。Stage 7 意圖序維持 2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 文件。**第 3 站已行使**；CLI Demo 足夠，無省略宣告。
- 互動判定仍待人類親填（本檔 status 留 draft；Agent 不代填通過，不送 G2）。
- throwaway 腳本處置:留在 session `/tmp/ibv-stage3-proto/`，**不進 Git**；形狀已錄於 Question／Method／Result。正式碼 Stage 6 再把射程伸進既有檢查家族。
