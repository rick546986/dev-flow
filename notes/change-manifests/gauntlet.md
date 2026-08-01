# Change Manifest — Workstream D:Evidence Gauntlet(old-coder 吸收)

> Branch:`devflow-vnext/gauntlet`(base 90d30e8)。
> 設計正本:`notes/design/evidence-gauntlet.md`(本檔引其節號)。
> 本 workstream 依附錄所有權**未改**:_templates/4-spec.md、
> _templates/6-implementation-notes.md、_templates/7-review.md、README.md、
> guide/HTML twin、example/ —— 對它們的全部修改建議在本檔,交 Integrator。
> plugin repo(/Users/asheng/.claude/plugins/local/dev-flow/)一字未動 → 外部待辦。

## 1. old-coder 已採用內容(出處 = 實讀檔案;完整對照表見設計 §1b)

- Evidence status 四值 pass/fail/unverified/n-a(references/gauntlet.md evidence template)
- 沒跑不能寫 PASS、skipped 必附理由(SKILL.md anti-gaming 5、§5)
- Final Fresh Run + source SHA 綁定 + stale artifact 機械清除
  (SKILL.md §6;demo tools/gauntlet.sh 的 `rm -f .coverage`;tools/source_state.sh)
- 單一 persisted entry point、pin 工具版本、CI 可重跑(references/gauntlet.md
  entry point 節;.github/workflows/gauntlet.yml)
- Changed-line coverage covered/total,禁全域 % 虛榮數字(SKILL.md gauntlet 表)
- Mutation 四態 killed/survived/equivalent/error;tool error 不算 killed;
  manual mutation 必 script 化持久(demo tools/mutants.py;references/gauntlet.md)
- Verification Profile / Failure Model 先於層選擇(SKILL.md Calibration Tier 3
  → 改嫁接到 `Risk: normal | high`)
- Negative constraints 必逐條映射 test/layer/skipped-with-reason(SKILL.md §1)
- Test Integrity Check(SKILL.md anti-gaming 1-4 操作化,設計 §5 七項)
- Supply chain / capability diff;新依賴回溯 spec justification(SKILL.md 表、
  references/gauntlet.md extended menu)
- 「數字非形容詞」機械化(demo evidence.md)、property/mutation 歸因誠實
  (SKILL.md mutation caveat、evidence.md layer attribution)

## 2. 不採用內容與原因(完整表見設計 §1d)

- **Tier 1/2/3**:與 lane + `Risk: normal|high` 撞第三套分級;Tier 3 判準折入 Risk。
- **獨立 spec.md/evidence.md**:4-spec 唯一 Spec、7-review 唯一 Evidence/Verdict。
- **/old-coder 獨立流程入口**:不建競爭流程。
- **「human 不讀 code」**:Stage 7 雙軸 code review 是硬要求,Gauntlet 只加層。
- **autonomous「spec 未核准降信心續走」**:違反 G2 gate 與驗證五律 4(HITL)。
- **spec 一步授權環境變更機制**:與 devflow-exec 守衛/allow 職責重疊,只吸收
  Dependencies justification 語意。
- **git init 提案/commit cadence 協商、Gherkin 格式、tree hash**:DevFlow 已有
  更嚴或等價機制。

## 3. Stage 4 待整合(_templates/4-spec.md;Integrator 執行)

1. 新節 `## Verification Profile`(欄位見設計 §2:Risk / Failure model /
   Negative constraints / Required layers / Conditional layers / Explicitly
   excluded layers / Final fresh entry point)。`Risk` 欄與 Workstream A 合流,
   **一個欄位一份定義**,整合時對齊 A 的措辭。
2. Failure Model 表(設計 §3;`Risk: high` 必填、normal 選配):
   `| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |`
3. `## Dependencies` 節註解加嚴:每個新依賴/新工具一行 justification,G2 審;
   未授權的新 capability 屬 7-review finding(設計 §11)。
4. 執行清單步 3(邊界收尾)追加「Verification Profile 填畢」為完成條件之一;
   G2 審查範圍句補「+ Verification Profile 審查」。
   ⚠️ renderer 錨:`template4-checklist` parity 區間 = 「執行清單(」→「起草前估」,
   改清單措辭必跑 `render-methodology-corrections.sh --write` 重生 guide,
   且勿動錨字串本身。

## 4. Stage 6 待整合(_templates/6-implementation-notes.md + README §5)

1. T review 檢查項(執行清單步 2e / T Review Log 欄)追加 **Test Integrity
   Check** 七項(設計 §5):刪 assertion / 放寬 assertion / 新增 skip/xfail /
   同步改測試+實作重定義正確性 / mock 核心邏輯 / 只追 coverage / 沒跑寫 PASS。
   建議 T Review Log 加一行 `- Test Integrity finding:`。
2. seam 語意註記(README §5 或 6-notes 頂註):Stage 6 只跑快速 Task-local 驗證
   (RED → GREEN → Task Verify → Test Integrity Check → Candidate);mutation/
   property 等重層屬 feature 級 Final Fresh Run,**不逐 T 跑**。
   「Candidate」命名與 Workstream A 對齊,若 A 未採 Candidate 詞則沿用現行
   「送 T review」措辭,不強推新詞。
   ⚠️ renderer 錨:`template6-checklist`(「執行清單(」→「實作期規則(」)、
   `template6-rules`(「實作期規則(」起)兩區間都在 parity 比對內。

## 5. Stage 7 待整合(_templates/7-review.md + README §7 + example)

1. 新節 `## Verification Evidence`(Evidence Matrix;Coverage Matrix 之後、
   現象證據之前):

   ```markdown
   ## Verification Evidence
   - Source SHA:
   - Final Fresh Run ID:
   - Entry point:
   - Toolchain:

   | Layer | Command | Status | Result | Skipped reason |
   |---|---|---|---|---|

   ## Negative Constraint Mapping
   | Constraint | Test/Layer | Status |
   |---|---|---|
   ```

   契約 = 設計 §6/§8;機械檢查 = `scripts/devflow-evidence-gauntlet.sh`(E1–E12)。
2. 執行清單插步(建議 2c,在現象複驗後):「Final Fresh Run:確認 evidence 節
   由 entry point 一次 fresh run 產出、SHA = 當下 HEAD;跑
   `scripts/devflow-evidence-gauntlet.sh 7-review.md --source-sha $(git rev-parse HEAD)
   --review-file` 全綠。完成 = gauntlet 輸出在案」。
3. **G3 條件變更走 README §7 唯一正本**(Integrator/Owner Call,本軌不代答):
   若把「Gauntlet evidence 契約全過」升為 G3 正式條件,須在 §7 G3 定義句加粗體
   錨(如 **Evidence 契約全過**)+ 同步三處摘要(SKILL 階段動作表 / §3 表 /
   7-review 模板頂註),並更新 plugin `_gate_consistency_impl.py` 的 token
   比對(plugin repo → 外部待辦)。未升格前,evidence gauntlet 以模板執行清單
   步強制,G3 條件句不動。
4. example 同步(example/contract-expiry-reminder/7-review.md 加示範 evidence
   節)→ 必跑 renderer `--write` 重生 7-review.html(tracked,禁手改),
   再跑 74/74 確認 check 腳本硬斷言(actor 字串、details 數量)未破。
5. ⚠️ renderer 錨:`template7-checklist` = 7-review.md 的「執行清單(」quote 區;
   `exit_checklist()` 抓 `## Exit Checklist` 的 `- [ ]` 連續列 —— 新節放在既有
   節之間不影響,改清單/Exit 措辭必 `--write`。

## 6. Ledger 事件介面(契約 only;實作 = Workstream C,本軌零落地)

設計 §13 全文為準。摘要:`verification_layer_started` /
`verification_layer_completed` / `final_fresh_run_started` /
`final_fresh_run_completed`;共通欄 `run_id`(= Evidence 的 Final Fresh Run ID)、
`source_sha`(= Evidence 的 Source SHA)、`ts`;layer 級加 `layer` /
`status`(四值)/ `command_ref` / `result_summary`(一行,禁完整敏感輸出)/
`artifact_ref`;run completed 加 `verdict` / `layers_total` / `layers_failed`。
Evidence 與 ledger 的 run_id/SHA 對不上 = stale 訊號。
交接:C 定 ledger 檔案格式/寫入時序,欄位名以本契約為準;衝突時兩軌 Integrator 對齊。

## 7. Entry point 設計(設計 §7)

- **專案層**(概念 `./tools/devflow-gauntlet.sh`,名稱位置依採用專案):跑真驗證
  層;起手刪 stale artifacts、逐層執行、fail fast 或保存每層狀態、記工具版本、
  CI/人類皆一條命令重跑。4-spec `Final fresh entry point` 欄指名。
- **文檔方法論層**(本 repo 已落地):`scripts/devflow-evidence-gauntlet.sh`
  驗 Evidence 契約(E1–E12,詳設計 §7/腳本頂註);
  `scripts/test-evidence-gauntlet.sh`(21 案)+
  `scripts/fixtures/evidence-gauntlet/`(14 fixtures)。
  先測試後實作:RED commit f0c77bd → GREEN commit b84acea。

## 8. 外部待辦(plugin repo,本軌不得動)

1. dev-run SKILL.md:Stage 7 派工含 Final Fresh Run 步 + evidence gauntlet 呼叫;
   Stage 6 T review prompt 加 Test Integrity Check 七項。
2. `_gate_consistency_impl.py`:若 G3 條件句新增粗體錨(§5 第 3 點)須同步比對表。
3. dev-setup:採用專案如需把 `devflow-evidence-gauntlet.sh` 隨模板散發,走
   dev-setup 複製清單(母版→專案同步機制)。
4. Ledger 寫入 runtime(C 軌 + plugin)。

## 9. 測試輸出(原文)

基線(開工前,worktree @ 90d30e8):

```
✅ methodology correction checks: 74/74 passed
✅ renderer fixed point: 4/4 tracked outputs byte-identical
```

收工(HEAD = 本 manifest 前一 commit;新增測試含入):

```
✅ methodology correction checks: 74/74 passed
✅ renderer fixed point: 4/4 tracked outputs byte-identical
✅ evidence gauntlet tests: 21/21 passed
✅ evidence gauntlet: 45 checks passed — scripts/fixtures/evidence-gauntlet/good-evidence.md
```

RED 證據(工具實作前,commit f0c77bd 當下):

```
❌ evidence gauntlet tests: tool 不存在或不可執行:.../scripts/devflow-evidence-gauntlet.sh
```

## 10. Commit SHA

- `f0c77bd` RED:evidence gauntlet 失敗測試 + 14 fixtures
- `b84acea` GREEN:scripts/devflow-evidence-gauntlet.sh 實作,21/21 過
- `03dd653` 設計正本 notes/design/evidence-gauntlet.md
- 本 manifest 為其後一 commit(= branch HEAD,見完工回報)

## 11. L2 / Owner Call 停在此、不代答

1. **G3 條件是否納入「Evidence 契約全過」粗體錨**(§5 第 3 點)—— gate 正本
   變更 + gate-consistency 連動,Owner 裁決。
2. **Verification Profile 是否設為 Full lane 必填 / Fast lane 選配** —— 流程
   負擔取捨,Owner 裁決(建議:Full 必填、Fast 僅 Risk: high 時填)。
3. **Risk 欄位判準措辭與 Workstream A 的最終合流版本** —— 兩軌各自起草,
   Integrator 合併時裁決唯一措辭。
