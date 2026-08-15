---
feature: engine-fence-masking
stage: 4-spec
status: approved            # fast lane;規格=Backlog 出處 + 本檔,owner 已於派工單授權
owner: rick(裁決代理:fable5,授權見 notes/dispatch-guard-coverage.md)
updated: 2026-08-16
---

# 4. 規格(fast lane mini)

> lane: fast(判準:bugfix、行為已有 spec 條目 —— twin 側同病已修,引擎側是同一規則的
> 未完成半邊;Risk: normal)。Stage 1-3 依 fast lane 省略;G3 必審。
> 出處:docs/dev/b8-gate-twin-review-ui/7-review.md 附錄 A7 H1、docs/dev/STATUS.md Backlog。

## Bug Scenario

- GIVEN:一份 5-tasks.md,某 T 的 Boundaries 欄含 fenced code block(```),
  區塊內有行首 `## T-99 假任務` 或 `- Files: 假清單`
- WHEN:Stage 6 引擎(`hooks/devflow-lib.py::parse_5_tasks`)解析它
- THEN(現況=錯):`## T-99` 長成一個真任務(自帶 Files scope 的幽靈任務);
  `- Files:` 觸發「重複保留欄」fail-closed 拒啟 —— 而 twin(已修)看到的是另一個世界
- THEN(正確):fence 內容對引擎不可見,與 twin 判定一致

## ADDED Requirements

### R-1: 引擎解析 5-tasks 時遮蔽 fenced code block

#### S-1.1 fence 內的 T 標題不長成任務
- GIVEN: Boundaries 內 fenced 區塊含行首 `## T-99 假任務`
- WHEN: `parse_5_tasks` 解析整份 5-tasks.md
- THEN: tasks 只含真 T,無 T-99,errors 為空
- 觀測: `python3` 以 importlib 載入 `hooks/devflow-lib.py`,對 fixture 跑 `parse_5_tasks`,印 task id 清單

#### S-1.2 fence 內的保留欄位行不觸發重複欄 fail-closed
- GIVEN: 某 T 的 Boundaries fenced 區塊內含 `- Files: 假的`
- WHEN: 解析
- THEN: errors 為空;該 T 的 files 值 = fence 外的真值
- 觀測: 同 S-1.1 的載入法,印 errors 與該 T 的 files

#### S-1.3 fence 外的重複保留欄仍 fail-closed(F-1 回歸)
- GIVEN: 同一 T 在 fence 外有兩行 `- Files:`
- WHEN: 解析
- THEN: errors 含「重複保留欄」
- 觀測: 同上,印 errors

#### S-1.4 reference parser 與引擎逐字同判
- GIVEN: S-1.1/S-1.2/S-1.3 的三種輸入
- WHEN: `tests/parallel-stage6/contract_ref.py::parse_5_tasks` 與引擎各跑一次
- THEN: 兩者 task dict 完全相同(鏡射同步,含遮蔽規則)
- 觀測: `tests/parallel-stage6/run_tests.py` 的 parity 案例(新增 fence 情境)輸出

### R-2: twin 的「幽靈任務」警告退場

#### S-2.1 引擎修復後 twin 不再宣稱過期事實
- GIVEN: `scripts/fixtures/gate-twin/tasks-dup-field/`(fence 內含 `## T-99`)
- WHEN: `build-gate-twin.py` 產 5-tasks 執行板
- THEN: stderr 無「引擎目前不遮蔽 fence…幽靈任務」警告;卡片行為不變;
  守衛斷言改驗「引擎對同輸入不長 T-99」(斷言釘在引擎行為,不釘在過期警告)
- 觀測: 對該 fixture 跑產生器看 stderr;`bash scripts/check-gate-twin.sh`

## Out of Scope

- 引擎遮蔽不追求 CommonMark 完整合規(hooks 不得引入 pip 相依):保守規則
  = ```/~~~、長度 ≥3、縮排 ≤3、收尾同種且不短於開啟、未閉合遮到檔尾。
  與 twin(markdown-it)的已知邊界差異(巢狀四反引號、list 內縮排 fence)寫成
  程式碼註解,不在本輪消除。
- FIELD_RE 本身、續行語意、其他 hooks 不動。

## Diff Budget

≤6 檔(hooks/devflow-lib.py、tests/parallel-stage6/{contract_ref.py,run_tests.py}、
hooks/selftest.sh、scripts/{build-gate-twin.py,check-gate-twin.sh}+fixture)/
非測試 ≤120 行、測試 ≤150 行。超支=停下判 L1/L2。

## Verification Profile

- lane: fast(Risk: normal;判準:行為已有 spec 條目、可逆、無 schema/契約變動)
- Required layers(Final Fresh Run 必跑):selftest / check-parallel-stage6 /
  check-gate-twin / devflow-check
- Verify: `bash hooks/selftest.sh && bash scripts/check-parallel-stage6.sh && bash scripts/check-gate-twin.sh`

## 確認紀錄

- 2026-08-16 fable5(owner 授權代理,notes/dispatch-guard-coverage.md 第二部分):
  規格定稿;fast lane 偏離記錄:無(判準即 fast,無 owner 反向指示)。
