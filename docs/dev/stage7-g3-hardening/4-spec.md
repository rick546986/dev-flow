---
feature: stage7-g3-hardening
stage: 4-spec
status: draft
owner: claude/stage7-g3-hardening
updated: 2026-08-22
---

# 4. 規格(迴圈實作紀錄;未重開 Stage 1–3)

> owner 已同意兩刀,本檔只把完成條件寫成可測契約。正本裁決見
> `docs/dev/STATUS.md` Backlog「整合回歸移到 Verdict 之前」與第 7 站迴圈種子清單。
> 不重開 1-discussion / 2-decision。

## ADDED Requirements

### R-1: 審過的樹 = 出貨的樹

#### S-1.1 整合回歸在 Final Fresh 之前
- GIVEN: `_templates/7-review.md` 頂註執行清單
- WHEN: 讀步驟順序
- THEN: 「整合回歸」出現在「Final Fresh Run」之前;Exit Checklist 不再合併
  `INTEGRATION_SHA`
- 觀測: `bash scripts/check-stage67-enforcement.sh`(ST 組)與
  `bash scripts/test-evidence-gauntlet.sh` P0-1 段

#### S-1.2 ALREADY_SYNCED 有恢復路徑;Verdict 後改碼作廢 G3
- GIVEN: 同上模板
- WHEN: 搜「重跑 Final Fresh」「作廢 G3」「不得再改程式碼」
- THEN: 三句都在;Exit 只准文件／PR／living spec
- 觀測: 同上

### R-2: Required 層從 4-spec 讀,漏帶即紅

#### S-2.1 sibling 4-spec Required unverified → E7 紅
- GIVEN: `scripts/fixtures/evidence-gauntlet/profile-unverified/`
- WHEN: gauntlet `--review-file` 不帶 `--require-layer`
- THEN: exit 1,輸出含 E7
- 觀測: `bash scripts/test-evidence-gauntlet.sh`

#### S-2.2 sibling 4-spec Required 皆 pass → 漏旗標仍綠
- GIVEN: `scripts/fixtures/evidence-gauntlet/profile-pass/`
- WHEN: 同上
- THEN: exit 0
- 觀測: 同上

#### S-2.3 已觸發 Conditional 未 pass → E7 紅
- GIVEN: profile-unverified 的 Supply chain = unverified
- WHEN: 同上
- THEN: exit 1,輸出含 E7
- 觀測: 同上

#### S-2.4 --review-file 找不到 Profile → E7 紅
- GIVEN: 無 sibling 4-spec、無 `--profile`,或 4-spec 沒有 Verification Profile 節
- WHEN: gauntlet `--review-file`
- THEN: exit 1,輸出含 E7;不得退回 1.2.0 漏帶即綠
- 觀測: `bash scripts/test-evidence-gauntlet.sh` 1230-P0

### R-3: --review-file 漏帶 --source-sha 綁 HEAD

#### S-3.1 宣告 SHA ≠ HEAD → E2 紅
- GIVEN: `good-review.md`(Source SHA=abc1234)
- WHEN: `--review-file` 不帶 `--source-sha`
- THEN: exit 1,輸出含 E2
- 觀測: `bash scripts/test-evidence-gauntlet.sh` P0-3

#### S-3.2 docs/dev/<feature>/7-review 顯式 SHA 也必須 = HEAD
- GIVEN: `docs/dev/<feature>/7-review.md`(排除 example/ 與 scripts/fixtures/)
- WHEN: `--review-file --source-sha <與宣告相符但 ≠ HEAD>`
- THEN: exit 1,輸出含 E2
- 觀測: `bash scripts/test-evidence-gauntlet.sh` 1230-P1

## Verification Profile
- lane: fast
- Risk: normal
- Required layers:test-evidence-gauntlet / check-stage67-enforcement / gate-consistency / check-gate-tokens / check-version-sync
- Explicitly excluded layers:Mutation(本輪不改 mutation 工具鏈)
- Final fresh entry point:`bash scripts/test-evidence-gauntlet.sh && bash scripts/check-stage67-enforcement.sh && bash hooks/gate-consistency.sh`

## Out of Scope
Windows 真機、STATUS 單寫者、第二個範例、記憶系統、merge、重開 Stage 1–3、
把 T review 與 G3 併層、拿掉現象證據或 Operational Walkthrough。
