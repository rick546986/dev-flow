# Claude Opus 5 執行 Prompt：DevFlow 四能力補強

你現在是 `rick546986/dev-flow` 的主實作者與流程協調者。請直接在 Repository 中完成本 Prompt 的修改與驗證，不要只提供建議。

## 一、總目標

修正 DevFlow 在四能力獨立審查中發現的六項缺口：

1. P1：`4-spec` 的每個 S 必須至少被一個 `5-tasks` Covers 承接，封住追溯檢查恆綠漏洞。
2. P2：Stage 3 已 ACCEPTED 的每個 Demo 場景，在 Stage 4 必須有 R/S 或 Out of Scope 理由。
3. P3：Evidence Gauntlet E11 在 `--review-file` 模式補驗 `Operational Walkthrough` 與 `Coverage Matrix` heading，並正確升版。
4. P4：README 清楚標示每項條件究竟由外部 plugin、本 repo 腳本或人工 Reviewer 強制。
5. P5：Stage 5 補上反水平切層判準，但不新增 G1.5 Gate 或路徑式 layer lint。
6. P6：Stage 4 增加輕量 Reliability Triage，對 Concurrency、Idempotency、Timeout／retry 逐項寫適用性與理由。

本次必須真正修改、測試、Fresh Review，最後建立一份 Markdown 執行報告。

## 二、不可違反的邊界

- 不要新增新的 Stage。
- 不要新增獨立 `architecture.md`。
- 不要建立第二套 Journey／Actor／Interaction ID 鏈。
- 不要把整套 DoD 全面 JSON Schema 化。
- 不要把 Runtime 併回本 repo。
- 不要把 `task_tags` 拉進 5-tasks 必填欄。
- 不要新增 Stage 5 G1.5 Gate。
- 不要做按路徑名稱猜 DB／Repo／Service／API／UI 的通用 lint。
- 不要讓 Gauntlet 判斷 Walkthrough 或架構圖內容是否正確；P3 只驗 heading 存在。
- 不要改寫歷史記錄 `verification-benchmark-2026-08.md` 的結論或版本數字。
- 不要修改 README §7 的 G2／G3 粗體 Gate 定義句，除非現行測試明確要求；本輪應避免觸碰。
- 不得自行捏造 Human verdict、Owner Call 或使用者決策。
- 不 Push、不建立 PR；可以建立本地 branch 與 local commits。
- 最終報告檔預設不納入 commit。

必須保留：原始證據、防錨定閱讀順序、獨立 Reviewer、HITL、失敗分類與 loop budget。

## 三、先對齊最新版本

先執行：

```bash
git fetch origin
git checkout main
git pull --ff-only
git status --short
git rev-parse HEAD
git log --oneline -10
```

記錄 Before SHA。

檢查以下修改是否已在最新 main 完成。已完成項目標為 `ALREADY_IMPLEMENTED`，不得重複插入：

- P1 的 4-spec S 子集合檢查。
- P2 的 Stage 3 場景對帳文字與範例下落。
- P3 E11 五個 heading、Gauntlet 1.2.0 與負向 fixture。
- P4 README 強制力對照。
- P5 反水平切層文字。
- P6 Reliability Triage。

請用實際內容與測試判斷，不依賴舊行號。

工作樹若不乾淨，不要覆蓋既有變更；使用乾淨 worktree 或先清楚隔離本次工作。

建立本地 branch，例如：

```bash
git switch -c fix/devflow-4cap-remediation-2026-08
```

## 四、先跑基線

先跑完整基線，保存原始輸出與 exit code：

```bash
scripts/check-methodology-corrections.sh
scripts/check-realworld.sh
scripts/check-parallel-stage6.sh
scripts/check-vnext-integration.sh
scripts/test-evidence-gauntlet.sh
observability/run-tests.sh
scripts/render-methodology-corrections.sh --check
```

若某命令基線已失敗：

- 記錄為 `BASELINE_FAILURE`。
- 不得把它混稱為本次回歸。
- 本次修改不得增加新的失敗。

如果外部 plugin 存在，先記錄：

```bash
~/.claude/plugins/local/dev-flow/hooks/gate-consistency.sh
```

並依實際 usage 探查 selftest 與 doctor；不要猜不存在的命令。

## 五、P1：追溯鏈頂端

### 先 RED

在不破壞正式 main 的前提下，建立可還原的負向驗證：讓 `example/contract-expiry-reminder/5-tasks.md` 暫時漏掉一個只出現一次的 S Covers，確認現行 `check-methodology-corrections.sh` 仍可能錯誤轉綠或缺乏對應檢查。

保存原始輸出，然後還原 fixture。

### 實作

修改 `scripts/check-methodology-corrections.sh`：

1. 從 `example/contract-expiry-reminder/4-spec.md` 解析所有 `#### S-n`。
2. 從 `expected_pairs` 建立 Covers 的 S 聯集。
3. 檢查 `spec_scenarios <= covered_scenarios`。
4. 失敗訊息列出 `uncovered`。

使用既有 `check()` 慣例，不另建框架。

### GREEN

再重做同一負向案例，必須轉紅；合法範例必須全綠。

P1 單獨 commit。

## 六、P2：Stage 3 ACCEPTED 場景對帳

修改 `_templates/4-spec.md` Stage 4 執行清單的「邊界收尾」步驟，加入：

```text
Stage 3 對帳：逐一核對 3-prototype Demo Script 場景。每個已 ACCEPTED 的場景
必須對應至少一條 R/S，或在 Out of Scope 明列排除理由；沒有 Stage 3 時記 N/A。
```

接著逐場核對 `example/contract-expiry-reminder/3-prototype.md` 與 `4-spec.md`。

已知需處理的場景是「資料過期／併發編輯」。只能選擇有來源支持的處理：

- 建立正式 R/S；或
- 明列 Out of Scope、理由與 known risk。

不要發明新的產品承諾。

不要改 README §7 的 G2 粗體 Gate 定義句。

執行：

```bash
scripts/check-realworld.sh
scripts/check-methodology-corrections.sh
scripts/render-methodology-corrections.sh --check
```

若 renderer 要求重生衍生 HTML，使用既有 renderer 正確重生，不手改機械生成檔。

P2 單獨 commit。

## 七、P3：E11 與 Gauntlet 1.2.0

### 先 RED

新增 `scripts/fixtures/evidence-gauntlet/bad-review-missing-walkthrough.md`，內容除了缺少 `Operational Walkthrough` 外應保持 review-file 最小合法。

先在 `scripts/test-evidence-gauntlet.sh` 註冊此負向案例，確認現行 E11 未擋住或測試轉紅。

### 實作

修改 `scripts/devflow-evidence-gauntlet.sh` E11：

```python
for heading in (
    "Standards Axis",
    "Spec Axis",
    "現象證據",
    "Operational Walkthrough",
    "Coverage Matrix",
):
```

只驗 heading 存在。

同步：

1. `good-review.md` 補最小合法 `Operational Walkthrough`。
2. `GAUNTLET_VERSION`：`1.1.0` → `1.2.0`。
3. `devflow-contract.json` 的 `schema_versions.gauntlet` 同步為 `1.2.0`。
4. 檔頭規則清單補 E13 的現行說明。
5. 搜尋所有 `1.1.0` 引用，只更新現行規則、usage、active guide 或契約引用。
6. 不改寫歷史 benchmark／audit 記錄中的當時版本。
7. README §7 若有非粗體版本敘述，更新為 1.2.0；粗體 Gate 錨不動。

### GREEN

執行：

```bash
scripts/test-evidence-gauntlet.sh
scripts/devflow-evidence-gauntlet.sh --version
scripts/devflow-evidence-gauntlet.sh \
  example/contract-expiry-reminder/7-review.md \
  --review-file
```

負向 fixture 必須被 E11 擋下；合法 review 必須通過。

若外部 plugin 存在，執行 doctor／selftest／gate consistency，確認版本握手沒有新增錯誤。

P3 單獨 commit。

## 八、P4：強制力對照

在 README §7 末尾、§8 之前新增「強制力對照（誰在擋）」小節。

要求：

- 表內不要使用粗體。
- 依最新 repo 實際檔名與外部 plugin 路徑撰寫。
- 清楚分成：外部 plugin、本 repo 腳本、人工／fresh reviewer。
- 明示 Gauntlet 只驗 Evidence Contract，不自行執行專案測試。
- 明示 Coverage Matrix／Operational Walkthrough 的內容正確性仍由 Reviewer 判斷；P3 只驗 heading 存在。
- 明示 repo reference test 通過不等於 external Runtime pass。

至少涵蓋：G1、G2、Stage 3 verdict、Stage 5 欄位／scope、Stage 6 guard、Task review、追溯鏈、G3 Evidence、Final Fresh Run、Coverage／Walkthrough、Attempt Ledger、doctor 相容性。

執行所有受 README／guide parity 影響的 checks。

若 `gate-consistency.sh` 基線已有 1 個失敗，只允許維持原失敗，不得新增紅格。

P4 單獨 commit。

## 九、P5：反水平切層

修改 `_templates/5-tasks.md`：

在 tracer bullet 後加入：

```text
禁整份按 DB→Repo→Service→API→UI 逐層分 T。每個 T 必須能回答：
「完成後，使用者或系統多了什麼可觀測行為？」答不出即為水平切層徵兆，
應與相鄰 T 合併或重新界定。
```

在「一個 T 一個關注點」規則補：

```text
超標拆分優先按子行為拆，例如讀／寫路徑、成功／例外路徑；不得優先按架構層拆。
```

不要：

- 新增 G1.5 Gate。
- 新增 layer path lint。
- 改必填四欄。
- 新增 Slice／Enabler schema。

執行：

```bash
scripts/check-parallel-stage6.sh
scripts/check-methodology-corrections.sh
scripts/render-methodology-corrections.sh --check
```

P5 單獨 commit。

## 十、P6：Reliability Triage

在 `_templates/4-spec.md` 的 Verification Profile 中，讓 Full／Fast lane 都回答：

```text
- Reliability triage:
  - Concurrency: applicable | n-a — <理由；適用時指向 S／Failure Model／Out of Scope／Known limit>
  - Idempotency: applicable | n-a — <理由；適用時指向契約或未覆蓋風險>
  - Timeout/retry: applicable | n-a — <理由；適用時指向契約、驗證層或未覆蓋風險>
```

規則：

1. `n-a` 必須附具體理由。
2. `applicable` 必須至少指向 R/S、Failure Model、Negative Constraints、Required／Conditional layer、Out of Scope 或 Known limit 之一。
3. 不要求本輪實作所有 applicable 項。
4. 不得因此自動發明新產品行為或 API 保證。
5. 不新增新 Gate，不修改 README §7 粗體錨。

同步更新 `example/contract-expiry-reminder/4-spec.md`，根據現有資料誠實填寫三問。特別注意：Stage 3 已存在資料過期／併發編輯場景；若 P2 將它列 Out of Scope，Concurrency triage 必須明確指向該 Out of Scope／known risk，而不是寫成完全無關。

在現有最合適的 repo check 中加入最小檢查：

- 模板三個欄名存在。
- 範例三項均不是空白，且包含理由文字。

不要建立複雜 parser 或語意判斷器。

執行相關 checks 與 renderer。

P6 單獨 commit。

## 十一、完整回歸

完成 P1～P6 後執行：

```bash
scripts/check-methodology-corrections.sh
scripts/check-realworld.sh
scripts/check-parallel-stage6.sh
scripts/check-vnext-integration.sh
scripts/test-evidence-gauntlet.sh
observability/run-tests.sh
scripts/render-methodology-corrections.sh --check
git diff --check
```

再執行 P3 的合法與負向 Gauntlet 案。

若外部 plugin 可用，執行：

- gate consistency
- plugin selftest
- doctor

命令需從實際 usage／help 探查，不要猜。

## 十二、Fresh Review

使用兩個獨立 fresh-context Reviewer；Reviewer 不得看到作者的結論，只提供：

- 本 Prompt 的 P1～P6 驗收條件。
- 修改 diff。
- 相關模板／README／scripts。
- 原始測試輸出。

Reviewer A：Standards／回歸／過度設計

- 是否新增重複正本。
- 是否不小心改 Gate 粗體錨。
- 是否更新了歷史文件。
- 是否把存在性檢查擴張成內容正確性判斷。
- 是否破壞 renderer parity 或版本握手。

Reviewer B：Spec／Scope

- P1 是否真的能抓到未 Covers 的 S。
- P2 每個 ACCEPTED Demo 場景是否有下落。
- P3 是否有正負向證據且版本一致。
- P4 是否誠實區分強制者。
- P5 是否只加判準、不新增未授權機制。
- P6 是否只做顯性 triage，未偷偷新增產品行為。

保留兩軸 findings，不要合併或降級。

修正後重新跑完整回歸。

## 十三、產出報告

在 repo 根目錄建立：

```text
devflow-4cap-remediation-2026-08.md
```

預設不要把報告檔 commit。

報告內容：

```markdown
# DevFlow 四能力補強執行報告

## 1. 版本基線
- Repository:
- Branch:
- Before SHA:
- After SHA:
- 日期:

## 2. 執行範圍
| 項目 | 狀態 | Commit | 摘要 |
|---|---|---|---|
| P1 | | | |
| P2 | | | |
| P3 | | | |
| P4 | | | |
| P5 | | | |
| P6 | | | |

## 3. 修改明細
每項包含：問題、修改檔案、實際修改、負向證據、正向證據。

## 4. 測試結果
| 命令 | 修改前 | 修改後 | 狀態 |
|---|---|---|---|

## 5. 外部 Runtime 檢查
- gate-consistency:
- plugin selftest:
- doctor:
- 無法執行項與原因:

## 6. Fresh Review Findings
### Standards Axis
### Scope／Spec Axis

## 7. 未完成與後續建議

## 8. 最終判斷
- P1～P6 是否完成
- 是否新增回歸
- 哪些能力仍為 DOCUMENTED_ONLY
```

最後在回覆中提供：

1. Before／After SHA。
2. 六個 local commit。
3. 報告檔路徑。
4. 完整測試摘要。
5. 外部 Runtime 未能驗證的部分。
6. 明確聲明沒有 Push、沒有 PR。
