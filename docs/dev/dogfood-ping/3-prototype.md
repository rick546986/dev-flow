---
feature: dogfood-ping
stage: 3-prototype
status: draft
owner: rick-dev-flow
updated: 2026-09-10
---

# 3. 原型 — dogfood-ok CLI 輸出形狀是否成立？

> Stage 3 依 owner lock **執行、不跳過**。方向 A 已是核准 Pattern → 1 個可操作 CLI Demo 即可，不湊 UI Variant。
> 正式 `scripts/dogfood-ping.sh` **不**在本站落地（Stage 6）；本站只用 throwaway 腳本證明輸出契約。
> Human verdict 由參與 Demo 的人類親填；Agent 禁代填。

## Stage 3 觸發判定(條件式必要)
<!-- 對照 1-discussion Real-world Context -->
- [ ] 有新的前端流程（本題是 CLI，無新前端）
- [x] 改變使用者下一步（owner 改以可觀測腳本／Example 驗證模板，不再只靠大 feat 記憶）
- [x] 涉及角色交接（owner ↔ 派工助手 ↔ 獨立 reviewer）
- [x] 涉及人工核准（G1／G2／G3 人類簽核）
- [x] 涉及等待/退回/逾時（閘門等待裁決／退回重做）
- [x] 涉及權限差異（寫碼 agent ≠ 審核 agent；owner 簽閘）
- [x] 涉及系統外動作（GitHub PR／CloudAgent／本機 shell）
- [ ] 涉及多種可行互動設計（方向 A 已 lock；單一路徑 CLI）
- [ ] Stage 1 尚有操作流程不確定性（Journey 已清；Q3 掛點後置 4-spec）

→ 命中 6 條:Stage 3 條件式必要,執行(不跳過)。owner 2026-09-10 亦明示不跳。

## Question
2-decision SC-1／決策點 A：throwaway 最小 shell 能否印出**恰好**一行 `dogfood-ok` 且 exit 0？
附帶：對本 dogfood，**CLI Demo 是否足夠**滿足 Stage 3（無需 UI Variant）？

答案長什麼樣才算回答了：
1. 實跑輸出字串等於 `dogfood-ok`（無多餘空白／前綴）。
2. exit code = 0。
3. 記錄「CLI Demo 足夠／不足」與依據（Pattern 已核准 vs 仍需互動 Variant）。

## Method
- 實驗位置:session scratchpad `/tmp/.../dogfood-ping-proto.sh`（**PROTOTYPE — not production code**；不進 main；正式路徑 Stage 6 才寫 `scripts/dogfood-ping.sh`）
- Demo 形式:**可執行 CLI flow**（使用者實際跑腳本，不是只看靜態說明）
- Pattern 已核准（Decision A）→ **1 個 Demo**，不做假 Variant
- Demo 腳本內容（throwaway）:
  ```bash
  #!/usr/bin/env bash
  # PROTOTYPE — not production code
  set -euo pipefail
  printf '%s\n' 'dogfood-ok'
  exit 0
  ```
- 驗法:`bash dogfood-ping-proto.sh`；比對 stdout 與 `$?`

## 結構圖
```
owner / 派工助手
  |
  v
[throwaway] dogfood-ping-proto.sh  (選定 Demo;非正式碼)
  |
  +--> stdout: dogfood-ok
  +--> exit: 0
  |
  v
Stage 6 才落地 scripts/dogfood-ping.sh + file-map
```

- throwaway CLI Demo(選定)
- 印 dogfood-ok + exit 0
- 正式腳本留 Stage 6

## Demo Script

### Scenario SC-1(跑 throwaway → 見 dogfood-ok)
- 使用者角色:owner（或派工助手代跑給 owner 看）
- 真實目標:確認極小可觀測題的輸出契約成立，作為後續 Stage 6 寫碼基準
- 起始狀態:scratchpad 有 `dogfood-ping-proto.sh`（可執行；標 PROTOTYPE）
- 操作步驟:在 terminal 執行 `./dogfood-ping-proto.sh`；記下 stdout 與 exit code
- 系統回應:stdout 一行 `dogfood-ok`；process exit 0
- 系統外下一步:無（本 Demo 不開 PR、不碰 file-map）
- 觀察問題:輸出是否剛好 `dogfood-ok`（無前綴）？exit 是否 0？是否覺得還需要 UI／多 Variant 才算「跑過 Stage 3」？

### Scenario SC-1(錯誤對照：故意印錯字)
- 使用者角色:派工助手
- 真實目標:確認驗收邊界——錯字不可當 PASS
- 起始狀態:臨時改印 `dogfood-OK` 或加前綴（僅對照，不留檔）
- 操作步驟:跑對照指令；與正確輸出比對
- 系統回應:字串不相等 → 不得宣稱 SC-1 形狀成立
- 系統外下一步:無
- 觀察問題:驗收是否只認精確字串？

## Result
- **2026-09-10 實跑**（CloudAgent session scratchpad）:
  - stdout: `dogfood-ok`
  - exit: `0`
  - `exact_match_dogfood-ok: yes`
- 答案:SC-1 輸出形狀**成立**（throwaway 證明）；**CLI Demo 足夠**——方向 A 已是核准 Pattern，無剩餘互動設計分叉，不必湊 UI Variant。
- 正式 `scripts/dogfood-ping.sh` **尚未**寫入 repo（留給 Stage 6 + file-map 同步）。
- 回寫對象:2-decision 確認紀錄「prototype 回寫」行 + Risks 旁註 `#165`（產器問題另票，與本 Demo 無關）。

## User Demo Feedback
<!-- Human verdict 由參與 Demo 的人類親填；Agent 禁代填 ACCEPTED／attestation -->
- Demo date: 2026-09-10（agent 已代跑 CLI；待 owner 親看輸出／頁面）
- Participants:
- Variant reviewed: CLI-only（無 UI Variant）
- Accepted interaction:
- Rejected interaction:
- Confusions observed:
- Missing real-world steps:
- Permission corrections:
- External handoffs:
- Required changes:
- Human verdict:
- Verdict attestation:

## Verdict
- 回寫 2-decision：SC-1 輸出形狀經 throwaway CLI 確認（`dogfood-ok` + exit 0）；**Stage 3 已行使**；CLI Demo 足夠，無跳過宣告。
- 互動／Human verdict：仍待 owner 親填（本檔 `status: draft` 直至 Human verdict = ACCEPTED + attestation）。
- throwaway 腳本處置:留在 session `/tmp`，**不進 Git**；結構已錄於上方結構圖；正式碼 Stage 6 再寫。
