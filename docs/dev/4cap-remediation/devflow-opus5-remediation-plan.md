# DevFlow 給 Claude Opus 5 的改造建議與執行規格

- 目標 Repository：`https://github.com/rick546986/dev-flow`
- 來源基線：2026-08-02 的獨立四能力審查、`4cap-audit-fixes-2026-08.md`、`verification-benchmark-2026-08.md`
- 基線參考 SHA：`bf05b598704da088551c4d32334f450133897e74`
- 注意：執行時必須重新取得最新 `main`，不得直接假設上述 SHA 仍是最新版本。

---

## 1. 最終建議

本輪建議分成兩層：

### 本輪直接執行

1. P1：封住 `4-spec → 5-tasks` 追溯鏈頂端恆綠漏洞。
2. P2：建立 Stage 3 ACCEPTED Demo 場景到 Stage 4 的逐場景對帳責任。
3. P3：補齊 Evidence Gauntlet E11 對 `Operational Walkthrough` 與 `Coverage Matrix` 的存在性檢查，並正確升版。
4. P4：在 README 增加「由誰強制」對照表，清楚區分外部 Runtime、本 repo 腳本與人工自律。
5. P5：在 Stage 5 補上反水平切層判準，先以文字與人工審查改善 tracer bullet，不立即增加新 Gate 或複雜 lint。
6. P6：把選配 O-5 提升成本輪項目，在 Stage 4 增加輕量 Reliability Triage，要求對併發、冪等、逾時／重試逐項寫「適用或不適用＋理由」。

### 本輪不直接執行

以下仍列為下一輪設計議題，不應由 Opus 自行擴張：

- 獨立 `architecture.md` 或新的 Architecture Stage。
- 完整 Software Design Contract 大表。
- Stage 5 新增 G1.5 人工 Gate。
- 依檔案路徑推測 DB／Repo／Service／API／UI 的通用分層 lint。
- 將 Runtime 併回方法論 repo。
- 將 `task_tags` 改成 5-tasks 必填欄。
- 強制所有 Feature 填部署拓撲、可用性與威脅模型。
- 用 Gauntlet 判斷 Walkthrough 或架構圖內容「是否正確」。
- 通用追溯腳本、第二個完整範例、真實 Reference App、Living Spec 實體化等較大投資。

這樣做的原因是：目前最急迫的是修正「宣稱有機械閉環，但實際可恆綠或漏接」的缺口；架構與完整軟體設計契約需要另外設計，不能在修補批次中順手擴張。

---

## 2. 必須保留的 DevFlow 原則

Claude Opus 5 修改時不得破壞下列既有設計：

1. **輕量、可讀的 Markdown 是正本**，不把整套 DoD 全面 JSON Schema 化。
2. **證據必須是原始輸出或檔案位置**，不能以「已執行、應該通過」自陳代替。
3. **驗證不自驗**：作者、派工者、Reviewer 的角色隔離仍要保留。
4. **閱讀順序防錨定**：Stage 7 先自建 Coverage Matrix，再讀作者 Self-Review。
5. **派工者不親自修 Finding**，應交回 Worker，再重新審查。
6. **HITL 不可代答**：Human verdict、Owner Call、Gate 核准不得由 Agent 推測。
7. **失敗先分類**：SPEC／ENV／IMPL／UNKNOWN，並保留嘗試上限與 breaker。
8. **Gauntlet 是 Evidence Contract Validator，不是假裝成完整 Runtime**。
9. **方法論 repo 與外部 Runtime 維持分離**，用 contract／doctor／self-test 握手，不合併兩個 repo。
10. `verification-benchmark-2026-08.md` 是歷史設計依據，不是現行規則正本，不應因本輪版本升級而改寫歷史結論。

---

## 3. 修改項目

## P1：封住 4-spec S 到 5-tasks Covers 的追溯漏洞

### 問題

現有範例檢查從 `5-tasks.md` 自己建立 `expected_pairs`。若某個 S 完全沒有出現在 Covers，期望集合也會一起縮小，因此測試仍會綠。

### 修改位置

- `scripts/check-methodology-corrections.sh`

### 最小修改

在解析完範例 `5-tasks.md`、建立 `expected_pairs` 後，另外從 `4-spec.md` 解析全部 S-id，檢查其為 Covers 聯集的子集合：

```python
spec_scenarios = set(re.findall(
    r"^#### (S-\d+)",
    read("example/contract-expiry-reminder/4-spec.md"),
    re.M,
))
covered_scenarios = {scenario for (_task, scenario) in expected_pairs}
check(
    spec_scenarios <= covered_scenarios,
    "4-spec 每個 S 都被至少一個 T 的 Covers 覆蓋",
    f"uncovered={sorted(spec_scenarios - covered_scenarios)}",
)
```

### TDD 驗收

1. 先建立負向驗證：暫時從 fixture／範例的某個 Task Covers 移除唯一的 S-id，腳本必須轉紅。
2. 還原合法 Covers 後轉綠。
3. 不只記錄通過數，必須貼出負向與正向原始輸出。

### 邊界

- 本輪只保護 repo 內範例。
- 不順手建立通用 `check-traceability.sh`。

---

## P2：Stage 3 ACCEPTED 場景必須在 Stage 4 有下落

### 問題

已被人類 ACCEPTED 的 Demo 場景可以無聲消失。既有範例中的「資料過期／併發編輯」就是實例：Stage 3 已 Demo 且 ACCEPTED，但 Stage 4 沒有 R/S，也沒有 Out of Scope 理由。

### 修改位置

- `_templates/4-spec.md`
- `example/contract-expiry-reminder/4-spec.md`

### 模板修改

在 Stage 4 執行清單的「邊界收尾」步驟加入：

```text
Stage 3 對帳：逐一核對 3-prototype Demo Script 場景。每個已 ACCEPTED 的場景
必須對應至少一條 R/S，或在 Out of Scope 明列排除理由；沒有 Stage 3 時記 N/A。
```

### 範例修正

逐一核對範例 Stage 3 的 Demo Script。對「資料過期／併發編輯」必須做出其中一種誠實處理：

- 形成正式 R/S；或
- 在 Out of Scope 明列本期不處理，附理由及已知風險。

不得默默刪除場景，也不得自行發明未經原資料支持的新行為。

### 邊界

- 不修改 README §7 的 G2 粗體 Gate 定義句。
- 不新增第二套 Scenario ID。
- 本項先維持人工責任，不做語意 parser。

### 驗收

- `scripts/check-realworld.sh`
- `scripts/check-methodology-corrections.sh`
- Renderer parity 檢查

---

## P3：補齊 Evidence Gauntlet E11 的 review-file 存在性檢查

### 問題

E11 目前只檢查：

- `Standards Axis`
- `Spec Axis`
- `現象證據`

但 README 對 G3 的說明還包含：

- `Operational Walkthrough`
- `Coverage Matrix`

### 修改位置

- `scripts/devflow-evidence-gauntlet.sh`
- `scripts/fixtures/evidence-gauntlet/good-review.md`
- 新增 `scripts/fixtures/evidence-gauntlet/bad-review-missing-walkthrough.md`
- `scripts/test-evidence-gauntlet.sh`
- `devflow-contract.json`
- README 中非粗體的 Gauntlet 版本說明
- 其他現行、非歷史性的版本引用

### 程式修改

E11 的 heading tuple 改為：

```python
for heading in (
    "Standards Axis",
    "Spec Axis",
    "現象證據",
    "Operational Walkthrough",
    "Coverage Matrix",
):
```

只檢查 heading 存在，不檢查內容正確性。

### 版本與 Fixture

1. `good-review.md` 補最小合法 `Operational Walkthrough` 節。
2. 新增缺 Walkthrough 的負向 fixture。
3. 測試必確認負向 fixture 被 E11 擋下。
4. Gauntlet 版本由 `1.1.0` 升到 `1.2.0`。
5. `devflow-contract.json` 的 `schema_versions.gauntlet` 同步。
6. 檔頭 E 清單補上已存在但遺漏敘述的 E13。
7. 只更新現行規則與工具版本引用，不改寫歷史 benchmark 記錄。

### 驗收

- `scripts/test-evidence-gauntlet.sh`
- 對 `example/contract-expiry-reminder/7-review.md` 執行 `--review-file`
- `devflow-evidence-gauntlet.sh --version`
- 外部 Runtime 的 doctor／selftest／版本握手（若本機存在）

---

## P4：README 增加「強制力對照（誰在擋）」

### 問題

目前 README 容易讓讀者把所有肯定語句都理解成已被 Runtime 機械阻擋，實際上有些只是 repo 腳本驗範例、有些由外部 plugin 執行、有些仍是人工審查。

### 修改位置

- `README.md` §7 末尾、§8 之前

### 建議表格

表格不得使用粗體，避免被 gate-consistency 錨點誤收。

| 條件 | 主要強制者 | 對應位置 |
|---|---|---|
| G1 方向與 Owner Calls | 人類／fresh reviewer；外部 plugin 負責流程 Gate | README §7、外部 dev-flow plugin |
| G2 R/S、Drafting Decisions、Profile | 人類／fresh reviewer；外部 plugin 負責流程 Gate | README §7、4-spec、外部 plugin |
| Stage 3 Human verdict | 人類輸入；外部 plugin 應拒絕 Agent 假冒 | 3-prototype、外部 Stage 3 runtime |
| Stage 5 必填欄與 scope | 外部 runtime；本 repo reference parser 驗 fixture | 5-tasks、contract_ref.py、外部 exec |
| Stage 6 scope guard | 外部 plugin hooks | devflow-exec／guard／prebash／postbash |
| Task independent review | 人類或 fresh Agent；外部 dev-run 編排 | 6-notes、dev-run |
| 4-spec S 到 5-tasks Covers | 本 repo 腳本只驗範例；下游仍需 runtime／CI 或人工 | check-methodology-corrections.sh |
| T×S RED／GREEN 與範例追溯 | 本 repo 腳本驗範例；外部 runtime／Reviewer 驗實案 | 6-notes、repo checks、dev-run |
| G3 Evidence Contract | 本 repo Gauntlet 腳本 | devflow-evidence-gauntlet.sh |
| Coverage Matrix／Walkthrough 內容 | Reviewer 人工判斷；Gauntlet 只驗 heading 存在 | 7-review、E11 |
| Final Fresh Run 實際執行 | 專案命令／Runtime／Reviewer；Gauntlet只驗 Evidence 宣告 | Verification Profile、7-review |
| Attempt Ledger 寫入與驗證 | 外部 runtime 寫入；本 repo observability CLI 驗證／衍生 | devflow-obs、外部 plugin |
| 方法論／Runtime 相容性 | 外部 doctor + `devflow-contract.json` | contract、runtime-capabilities、doctor |

Claude 應根據最新 repo 的實際命名與路徑調整，不可照抄不存在的檔案。

### 驗收

- 所有 repo check scripts
- Renderer parity
- 外部 `gate-consistency.sh`：不得新增紅格
- 若基線已有失敗，必須分開標示「既有失敗」與「本次新增失敗」

---

## P5：Stage 5 補反水平切層判準

### 問題

模板雖寫 tracer bullet，但純 DB→Repo→Service→API→UI 的水平任務仍可完全通過 reference parser。加上「Files 超過約 5 檔就拆」的規則，反而可能推動 Agent 按架構層拆分。

### 修改位置

- `_templates/5-tasks.md`

### 修改一

在 tracer bullet 說明後加入：

```text
禁整份按 DB→Repo→Service→API→UI 逐層分 T。每個 T 必須能回答：
「完成後，使用者或系統多了什麼可觀測行為？」答不出即為水平切層徵兆，
應與相鄰 T 合併或重新界定。
```

### 修改二

在「一個 T 一個關注點」後補：

```text
超標拆分優先按子行為拆，例如讀／寫路徑、成功／例外路徑；不得優先按架構層拆。
```

### 邊界

- 不新增 G1.5 Gate。
- 不新增按路徑猜測 layer 的 lint。
- 不更動 5-tasks 必填四欄。
- 不立即增加 Slice／Enabler 新 schema。

### 驗收

- `scripts/check-parallel-stage6.sh`
- `scripts/check-methodology-corrections.sh`
- Renderer parity

---

## P6：Stage 4 增加輕量 Reliability Triage

### 為何本輪提升此項

獨立審查中最弱的是 Software Design。完整 Software Design Contract 會過重，但完全不要求併發、冪等與逾時／重試的適用性判斷，又容易讓重要可靠性語意到 Stage 6 才由 Agent 自行決定。

因此本輪只做三問，不新增 Stage、不新增 Gate、不要求所有 Feature 撰寫完整技術設計。

### 修改位置

- `_templates/4-spec.md`
- `example/contract-expiry-reminder/4-spec.md`
- 視現行測試結構，於 `scripts/check-methodology-corrections.sh` 或最小適合位置加入欄位存在檢查

### 建議格式

放在 Verification Profile 內，Full 與 Fast lane 都要回答：

```text
- Reliability triage:
  - Concurrency: applicable | n-a — <理由；適用時指向 S／Failure Model／Out of Scope／Known limit>
  - Idempotency: applicable | n-a — <理由；適用時指向契約或未覆蓋風險>
  - Timeout/retry: applicable | n-a — <理由；適用時指向契約、驗證層或未覆蓋風險>
```

### 規則

1. `n-a` 必須附一句具體理由，不能只寫「不適用」。
2. `applicable` 不等於本輪一定要實作；但必須明確落到以下至少一處：
   - R/S
   - Failure Model
   - Negative Constraints
   - Required／Conditional verification layer
   - Out of Scope／Known limit
3. 本項不得自行新增產品行為或可靠性保證；只把已存在或確實相關的風險顯性化。
4. 範例內容必須依現有 Decision、Demo、Spec 誠實填寫，不可為了讓表格好看而創造不存在的能力。

### 驗收

- 模板含三問。
- 範例三問均有實質理由與引用位置。
- 現有 renderer／check suite 全綠。
- 不修改 README §7 Gate 粗體錨。

---

## 4. 建議執行順序

1. 重新同步最新 `main`，記錄 SHA 與最近 10 筆提交。
2. 檢查 P1～P6 是否已有部分或全部落地；已落地項不得重複新增。
3. 建立乾淨 branch／worktree。
4. 先跑完整基線，保存原始輸出。
5. P1：先 RED，再 GREEN，單獨 commit。
6. P2：模板＋範例對帳，單獨 commit。
7. P3：先新增負向 fixture 看到 RED，再實作 E11 與版本升級至 GREEN，單獨 commit。
8. P4：README 強制力表，單獨 commit。
9. P5：Stage 5 文字規則，單獨 commit。
10. P6：Reliability Triage 模板、範例與最小檢查，單獨 commit。
11. 跑所有 repo suites。
12. 若本機外部 plugin 存在，跑 gate consistency、plugin selftest、doctor。
13. 使用 fresh-context Reviewer 進行兩個獨立 Review：
    - Standards／回歸與過度設計檢查。
    - Spec／P1～P6 完整性檢查。
14. 修正 Finding 後重新執行全套測試。
15. 產生最終 Markdown 報告。
16. 不 Push、不開 PR，除非使用者另外明確要求。

---

## 5. 統一驗收

執行前先取得當下基線，不要把以下歷史數量當作絕對值。完成後至少執行：

```bash
scripts/check-methodology-corrections.sh
scripts/check-realworld.sh
scripts/check-parallel-stage6.sh
scripts/check-vnext-integration.sh
scripts/test-evidence-gauntlet.sh
observability/run-tests.sh
scripts/render-methodology-corrections.sh --check
```

對 P3 額外執行：

```bash
scripts/devflow-evidence-gauntlet.sh --version
scripts/devflow-evidence-gauntlet.sh \
  example/contract-expiry-reminder/7-review.md \
  --review-file
```

若外部 plugin 存在：

```bash
~/.claude/plugins/local/dev-flow/hooks/gate-consistency.sh
# 再依實際 plugin usage 執行 selftest 與 doctor
```

驗收報告必須包含：

- 執行命令。
- Exit code。
- 原始結果摘要。
- 修改前基線。
- 修改後結果。
- 既有失敗與新增失敗的區分。
- 未能執行的外部檢查及原因。

---

## 6. 最終報告格式

Claude Opus 5 完成後，請在 repo 根目錄建立：

```text
devflow-4cap-remediation-2026-08.md
```

此檔只作交付報告，預設不要放入 commit。內容至少包括：

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
### P1
- 問題
- 修改檔案
- 實際修改
- 負向證據
- 正向證據

（P2～P6 同格式）

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
- 不得把 deferred 項目描述成已完成。

## 8. 最終判斷
- 是否達成本輪 P1～P6
- 是否新增回歸
- 是否有 DOCUMENTED_ONLY 項仍未受 Runtime 強制
```

---

## 7. 可直接交給 Claude Opus 5 的完整 Prompt

完整 Prompt 另存於：`claude-opus5-devflow-execution-prompt.md`。
