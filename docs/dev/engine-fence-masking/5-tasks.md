---
feature: engine-fence-masking
stage: 5-tasks
status: approved
owner: rick(裁決代理:fable5)
updated: 2026-08-16
---

# 5. 任務

## T-1 引擎解析 5-tasks 時遮蔽 fenced code block,reference parser 同步
- [ ] 完成
- Covers: R-1 / S-1.1、S-1.2、S-1.3、S-1.4
- Files: hooks/devflow-lib.py, tests/parallel-stage6/contract_ref.py, tests/parallel-stage6/run_tests.py, hooks/selftest.sh
- Verify: `bash hooks/selftest.sh && bash scripts/check-parallel-stage6.sh`
- Blocked-by: —
- Intent: 引擎對 5-tasks 的 fence 內容視而不見,與 twin 判定一致 —— 幽靈任務與 fence 內假重複欄兩種誤讀消失,fence 外的 F-1 fail-closed 不變
- Boundaries: 只准動 Files 四檔;遮蔽規則=保守 stdlib(```/~~~、≥3、縮排 ≤3、同種收尾不短於開啟、未閉合遮到檔尾),與 CommonMark 的已知差異寫註解;不動 FIELD_RE 與續行語意;selftest 的 MIN_CASES 地板隨新案例同步;contract_ref 的遮蔽函式與引擎逐字鏡射

## T-2 twin 幽靈任務警告退場,守衛斷言改釘引擎行為
- [ ] 完成
- Covers: R-2 / S-2.1
- Files: scripts/build-gate-twin.py, scripts/check-gate-twin.sh, scripts/fixtures/gate-twin/tasks-dup-field/docs/dev/demo/5-tasks.md, docs/dev/tools/build-gate-twin.py
- Verify: `bash scripts/check-gate-twin.sh`
- Blocked-by: T-1
- Intent: 引擎修好後,twin 不再宣稱「引擎不遮蔽 fence」這個過期事實;守衛改驗「引擎對同輸入不長幽靈任務」,斷言釘行為不釘警告文字
- Boundaries: 只動幽靈警告相關段、對應 fixture 斷言與其 MIN_CHECKS/心跳名單;不放寬其他任何斷言;渲染層不動;docs/dev/tools 副本收尾 cp 同步
