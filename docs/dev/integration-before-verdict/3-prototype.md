---
feature: integration-before-verdict
stage: 3-prototype
status: draft
owner: rick
updated: 2026-09-12
---

# 3. 原型 — Stage 7 順序與 AS-1 填檔牙長什麼樣?

> 用途:用 throwaway CLI 狀態機回答 2-decision 留下的形狀疑問。**非正式碼**,
> 不進 main、不改 `check-stage67`／整合腳本演算法／`_templates/7-review.md`。
> Decision A+AS-1+T-now 已是核准 Pattern → **1 個可操作 CLI Demo**,不湊 UI Variant。
> Human verdict 由參與 Demo 的人類親填;Agent 禁代填 ACCEPTED／attestation。
> 本站不送 G2、不送 G3、不發版、不碰 `#196`／diagram-ir-gate。
> 審頁:`scripts/build-stage3-html.py --action`(有命中才印頁)。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context 逐條判定 -->
- [ ] 有新的前端流程（本題是 Stage 7 清單／填檔牙／活教師,無新前端）
- [x] 改變使用者下一步（reviewer 到站必須先 2c 整合再 2d Fresh;`ALREADY_SYNCED` 下一步是重綁 SHA 或 FAIL,不能只寫「證據不算數」）
- [x] 涉及角色交接（reviewer ↔ merger ↔ owner;Current Journey 等整合分支）
- [x] 涉及人工核准（G3 Verdict;`ALREADY_SYNCED` 選 FAIL 是人裁）
- [x] 涉及等待/退回/逾時（等整合分支;`ALREADY_SYNCED` 是退回重算／重綁路徑）
- [x] 涉及權限差異（reviewer 只在整合步准改 HEAD;merger 合 INTEGRATION_SHA;owner 簽閘）
- [x] 涉及系統外動作（git merge、GitHub PR、終端機跑整合腳本）
- [ ] 涉及多種可行互動設計（A+AS-1+T-now 已 lock;單一路徑 CLI／清單,不湊 Variant）
- [ ] Stage 1 尚有操作流程不確定性（Journey 已是 2c→2d;剩餘是填檔欄位名,交 4-spec）

→ 命中 6 條:Stage 3 條件式必要,執行(不跳過)。2-decision 無「跳過 Stage 3」流程層 OC。

## Question
引 2-decision Risks 第 1 條（填檔牙形狀未釘）+ Decision 剩餘交付（活教師 + AS-1）+ AC-1/AC-2/AC-3。
tip `#207`（`630cd41`）模板／節點鏈**已經**是 2c 整合 → 2d Fresh;本站不問「要不要搬散文」。

答案長什麼樣才算回答了:
1. **序**:throwaway 狀態機走出 `2c-integrate → 2d-fresh → dual-axis → verdict → exit-docs-only`;Fresh-first／跳過 2c／Verdict 後再合,都印 `BLOCKED` + 原因。
2. **牙**:六份填檔 fixture 對上預期 exit —— void-only 與 skip-2c-claim-G3 為 2;重綁 SHA、明示 FAIL、`N_A_NO_INCOMING`、draft 未宣稱為 0。
3. **教師**:活路徑掃描仍命中舊序句（本站只列、不改;改口是 Stage 6 T-now）。

## Method
- 實驗位置:session scratchpad `/tmp/ibv-stage3-proto/`（**PROTOTYPE — not production code**;不進 Git;正式牙／檔頭改口 Stage 6 才寫進既有檢查家族）
- Demo 形式:**可執行 CLI flow**（使用者實際跑狀態機 + 填檔 fixture,不是只看靜態說明）
- Pattern 已核准 → **1 個 Demo**,不做假 Variant
- 驗法:
  1. `python3 /tmp/ibv-stage3-proto/proto-stage7-order-tooth.py all`
  2. `rg -n '執行清單 2c 的 Final Fresh|Exit Checklist.*整合回歸.*計算工具'` 打活教師路徑
  3. 對 `_templates/7-review.md` 頂註確認 integ 位移 < fresh 位移（散文已對,當對照地板）
- Demo 鐵則:不變成 production;`/tmp` throwaway;只用假 fixture SHA;檔頭標非正式;允許人真的跑。

每個場景必含:主要角色、真實目標、入口、關鍵操作、等待、空／錯誤、權限、過期、中斷恢復、系統外下一步 —— 見下方 Demo Script。

## 結構圖
- throwaway CLI 狀態機 Demo（選定）
- 正確序：2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 只准文件
- AS-1：void-only 紅；重綁 SHA 或明示 FAIL 綠
- n-a／draft 未宣稱：牙沉默（不預先紅）
- 活教師掃描（example／manifest／腳本檔頭）只列不改
- 正式牙 Stage 6 才寫進既有檢查家族（OC-1）

```
reviewer
  |
  v
[選定] proto-stage7-order-tooth.py   PROTOTYPE — not production
  |
  +-- order: 2c -> 2d -> dual-axis -> verdict -> exit-docs-only
  |     BLOCKED: Fresh-first / skip-2c / merge-after-verdict
  +-- tooth on filled 7-review fixture
        void-only / skip-2c+G3     -> exit 2
        rebound SHA / item FAIL    -> exit 0
        N_A_NO_INCOMING / draft    -> silent 0
  |
  v
Stage 6: extend check-stage67 family (no second tool; no algorithm rewrite)
T-now: retitle live teachers (example 2c=Fresh, manifest 2c=gauntlet, script headers)
```

## Demo Script

### Scenario AC-3（正確序:2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 文件）
- 使用者角色:Stage 7 reviewer
- 真實目標:在將出貨的那棵樹上做 G3,核准樹=出貨樹
- 起始狀態:scratchpad 有 proto 腳本;feature 工作樹乾淨;FORK_INTEGRATION_SHA 已記
- 操作步驟:跑 `python3 proto-stage7-order-tooth.py order`;走 legal 五步
- 系統回應:`OK start -> 2c-integrate` … `READY-FOR-G3-SHAPE`;exit 0
- 系統外下一步:真站才跑 `docs/dev/tools/devflow-integration-regression.sh`(本 Demo 不 fetch、不合樹)
- 觀察問題:第一步是不是整合?Fresh 是否在合完之後?Exit 還能不能合併?

### Scenario AC-1（Fresh-first / Verdict 後才合 → BLOCKED）
- 使用者角色:Stage 7 reviewer（肌肉記憶仍是舊 2c=Fresh）
- 真實目標:想先 Fresh 再判,或 Verdict 後才合 `INTEGRATION_SHA`
- 起始狀態:同上
- 操作步驟:跑對照 `fresh-first`、`merge-after-verdict`、`exit-then-merge`
- 系統回應:三案皆 `BLOCKED` —— Fresh 會綁合前 HEAD;Verdict 後再合會讓 ship≠approved;Exit 只准文件
- 系統外下一步:退回 2c,合腳本印出的 INTEGRATION_SHA,再進 2d
- 觀察問題:系統是否暗示 Exit 還能改碼?等待整合分支時知不知道不能先 Fresh?

### Scenario AC-2（ALREADY_SYNCED void-only → 牙紅）
- 使用者角色:Stage 7 reviewer
- 真實目標:已合過、merge-base 被污染,想勾整合項送 G3
- 起始狀態:fixture `void-only.md` 只寫「證據不算數／輸出不算數」,無 Source SHA、無 FAIL
- 操作步驟:跑 tooth;對照 `rebound-sha.md` 與 `explicit-fail.md`
- 系統回應:void-only exit 2;重綁 SHA exit 0;明示 FAIL exit 0（牙收形狀;G3 不得因 FAIL 項而 PASS）
- 系統外下一步:①重跑 2d Fresh 綁當下 HEAD,或②本項 FAIL 從乾淨座標重算
- 觀察問題:只寫「不算數」還能不能過?知不知道下一步是重綁還是停?

### Scenario AC-2（空／錯誤:n-a 與 draft 不預先紅）
- 使用者角色:Stage 7 reviewer
- 真實目標:對方零新 commit,或 7-review 仍是 draft 還沒勾 2c
- 起始狀態:fixture `n-a-no-incoming.md`、`draft-no-claim.md`
- 操作步驟:跑 tooth
- 系統回應:兩案 exit 0、`SILENT`（牙只在宣稱勾過 2c／送 G3 時發動）
- 系統外下一步:n-a 可繼續 2d;draft 等真的跑完 2c 再發動
- 觀察問題:空狀態（還沒勾）會不會被誤判成違規?n-a 會不會被 ALREADY_SYNCED 規則誤殺?

### Scenario AC-3（權限／過期:跳過 2c 卻宣稱 G3）
- 使用者角色:reviewer（無權在 Verdict 後改 HEAD）／merger
- 真實目標:想用「沒跑 2c」的 7-review 送 G3
- 起始狀態:fixture `skip-2c-claim-g3.md`（`verdict: PASS` 但無 2c 結論／INTEGRATION_SHA）
- 操作步驟:跑 tooth
- 系統回應:exit 2 `RED skip-2c while claiming G3`
- 系統外下一步:回到 2c;merger 只能合腳本印的 SHA,不能用 branch 名
- 觀察問題:系統是否暗示了不存在的「跳過整合」權限?資料過期（branch 名已跑）時知不知道要重跑腳本?

### Scenario SC-3（活教師仍教舊序;本 Demo 只掃不改）
- 使用者角色:採用者／本 slug 實作者
- 真實目標:確認第一條真實 full lane 期間舊樣張還在教 `2c = Fresh`
- 起始狀態:tip `630cd41`
- 操作步驟:對活路徑跑 Decision SC-3 那條 `rg`;打開命中行
- 系統回應:example 7-review md/html:24／:105、4-spec:223、manifest:52、兩支整合腳本檔頭:2 仍命中;HISTORY／dispatch 不掃（OC-2 死紀錄）
- 系統外下一步:Stage 6 T-now 改口;衍生 fixture `spec-gate-dd-subsection` 與正本同一 T
- 觀察問題:抄範例的人會不會把 2c 做成 Fresh／gauntlet?腳本檔頭會不會讓人以為這是 Exit 才跑的工具?

## Result
- **2026-09-12 實跑**（CloudAgent session `/tmp/ibv-stage3-proto/`,HEAD `630cd41`）:
  - 順序機 5 案全對:legal 走出 2c→2d→雙軸→Verdict→Exit;`fresh-first`／`skip-2c-to-verdict`／`merge-after-verdict`／`exit-then-merge` 皆 BLOCKED。
  - 填檔牙 6 fixture 全對:

    | fixture | exit | 含義 |
    |---|---|---|
    | `void-only.md` | 2 | ALREADY_SYNCED + 只寫不算數 → 紅 |
    | `rebound-sha.md` | 0 | 重綁 Source SHA（`630cd41…`）→ 綠 |
    | `explicit-fail.md` | 0 | 明示本項 FAIL → 牙收形狀;不得當 G3 PASS |
    | `n-a-no-incoming.md` | 0 | 牙沉默 |
    | `draft-no-claim.md` | 0 | 牙沉默 |
    | `skip-2c-claim-g3.md` | 2 | 宣稱 G3 卻無 2c 結論 → 紅 |

  - 對照地板:模板頂註 integ 位移 929 < fresh 5616,且有「重跑 Final Fresh」散文;`check-stage67` ST 仍只咬模板字面。整合腳本 GUIDANCE 仍停在「輸出不算數」（`scripts/devflow-integration-regression.sh:204-205`）。
- **活教師（只列不改）**:
  - `example/contract-expiry-reminder/7-review.md:24` 與 `.html:105`:`執行清單 2c 的 Final Fresh Run`
  - `example/contract-expiry-reminder/4-spec.md:223`:`2c gauntlet`
  - `manifests/p4-gauntlet-gates.md:52`:`執行清單 2c 的文檔化命令`
  - `scripts/devflow-integration-regression.sh:2` 與 `docs/dev/tools/devflow-integration-regression.sh:2`:`Exit Checklist「(條件式)整合回歸」計算工具`
  - 衍生:`scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md:229` 抄了 4-spec 的 2c gauntlet 句（Risks 已點名,Stage 6 同一 T）
- 答案:擬定 Stage 7 序與 AS-1 填檔牙形狀**成立**(throwaway 證明);CLI Demo 足夠 —— Pattern 已核准,無剩餘互動設計分叉。正式守衛／檔頭改口**尚未**寫入 repo。
- 回寫對象:2-decision Risks「填檔牙形狀未釘」+ 確認紀錄「prototype 回寫」行。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填;Agent 禁代填 ACCEPTED／attestation -->
- Demo date: 2026-09-12（agent 已代跑 CLI;非正式 Demo attestation）
- Participants:
- Variant reviewed: CLI-only（無 UI Variant;選定 throwaway 狀態機）
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
- 回寫 2-decision Risks 第 1 條:填檔牙形狀已由 throwaway 釘成「宣稱 2c／送 G3 時,`ALREADY_SYNCED` 必須重綁 Source SHA 或明示本項 FAIL,否則紅;`N_A_NO_INCOMING` 與未宣稱的 draft 沉默」。欄位名／掛進哪一支既有檢查（OC-1:`check-stage67`／gate-consistency／7-review 形狀之一）仍交 4-spec。
- 回寫 Decision 剩餘交付:序不重編號（B 仍拒）;活教師清單上列五處 + 衍生 fixture,T-now 進 Stage 6 Files;本站不改那些檔。
- 互動／Human verdict:仍待人類親填。本檔 `status: draft` 直至 Human verdict = ACCEPTED + attestation。未 Demo ≠ ACCEPTED。不送 G2。
- throwaway 腳本處置:留在 session `/tmp/ibv-stage3-proto/`,**不進 Git**;結構已錄於上方結構圖;正式碼 Stage 6 再寫。
