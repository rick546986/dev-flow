# Plugin Workstream Result

- Base SHA: 24057d5
- Branch: devflow-runtime-vnext/gauntlet-gates
- HEAD: (本 manifest commit;前三 commit = c0bf60f RED / 0c96948 GREEN / b166b37 dev-setup)
- Modified files:
  - `hooks/selftest.sh`(只增:p4_ fixture helper + 10 新案;既有 80 案含 gate reviewer-selection 8 案未動)
  - `hooks/_gate_consistency_impl.py`(P4 獨佔:`+ **錨**` 串接形抽取 + GATE_TABLE 表驅動比對 + docstring)
  - `skills/dev-setup/SKILL.md`(P4 獨佔:gauntlet 散發 install 步 6 / upgrade 覆蓋清單 / check 第 9 項 / check 8 VNext 錨說明 / check 4「33 案」漂移修正 / check 6 Verification Profile 模板檢查說明)
  - `manifests/p4-gauntlet-gates.md`(本檔,新增)
- Added capabilities: 見下「能力對照」。
- Tests before: selftest 80/80;gate-consistency live 14 格、1 漂移(基線紅:`✗ _templates/4-spec.md 頂註缺 token「R/S、全審、全裁決」`,exit 1)
- Tests after: selftest 90/90(RED commit 時 82/90,8 紅全數轉綠);gate-consistency live 輸出 **byte-identical**(diff 空;仍 1/14 漂移、exit 1 —— 該漂移是方法論模板問題,Phase 3 隨 OC-2 條文一併解,不屬本軌)
- Raw outputs:
  - RED:`❌ 守衛自測 82/90,失敗 8 項`(p4_vnext 錨 8 案紅;2 pin 案綠)
  - GREEN:`✅ 守衛自測 90/90 全過`
  - live 比對:`diff gate-live-before.txt gate-live-after.txt` → 空(exit 1 前後一致)
  - 散發 rehearsal(照 SKILL 命令逐字實跑):`noargs-exit=2`、good-evidence `45 checks passed`+`fixture-exit=0`、bad-fail-layer `bad-fixture-exit=1`、`DIFF-CLEAN`、`EXECUTABLE`
- Known limitations:
  1. gate-consistency 仍為 token 級比對(不驗語序/否定式/多餘過期條件)—— 既有刻意取捨,VNext 未改。
  2. 新錨對 live README 的檢查要等 README §7 新條文落地(Phase 3)才實際生效;目前僅 fixture 證明。
  3. dev-setup 為 prose skill:散發命令序列已實跑驗證,skill 全流程(偵測→分流→check)E2E 屬 Phase 4。
  4. SYNONYMS **未擴充**(決策):共享契約 §1「同步位置缺一即 FAIL」語意 = 錨須逐字覆誦;新錨(Verification Profile / Demo verdict / Evidence 契約全過)無既存異寫,擅自加同義映射反而放鬆檢查。Phase 3 落條文時若正本刻意用異寫,再依需擴充。
- External dependencies: 方法論 repo `~/dev/dev-flow`(gate-consistency 讀 README/模板;dev-setup 散發源 `scripts/devflow-evidence-gauntlet.sh` 與 fixtures;本軌完成當時之狀態 —— 2026-08 併入單一 plugin 後方法論一度內建於 plugin repo 內的子目錄,後又於同月的單一 repo 合併中收攏進 repo 根目錄,該子目錄層不復存在,不再是外部依賴)。無新第三方依賴。
- Status: 見能力對照;selftest 90/90 全綠、`git diff --check` 淨、無生成檔入 git、未 push。

## 能力對照(charter §八 P4 清單 → 落點與狀態)

| 能力 | 落點(檔:行/位置) | 狀態 |
|---|---|---|
| G2 Gate consistency(Verification Profile / Demo verdict 錨) | `hooks/_gate_consistency_impl.py`(extract_tokens 串接形 + GATE_TABLE)+ `hooks/selftest.sh` p4_ 案 | RUNTIME_PASS(fixture 實跑);live 生效 PENDING(README §7 Phase 3) |
| G3 Gate consistency(Evidence 契約全過 錨) | 同上 | RUNTIME_PASS(fixture);live 生效 PENDING(同上) |
| 安裝/散發 evidence gauntlet;setup/installer 更新 | `skills/dev-setup/SKILL.md` install 步 6 / upgrade / check 9 | RUNTIME_PASS(命令序列實跑證據);skill 全流程 E2E_PENDING |
| Fast/Full Profile 驗證、Fast+High 拒絕 | start 時 runtime 檢查歸 **P1**(契約 §10 註);P4 份 = G2 錨 token(fixture 證)+ dev-setup check 6 模板檢查說明 | P4 份 RUNTIME_PASS;runtime 拒絕 PENDING(P1) |
| Plugin 派發 Final Fresh Run;Stage 7 單一入口;清 stale;SHA binding;Required/Conditional/Excluded;Evidence 四值;Gauntlet 不取代雙軸;Changed-line coverage 語意 | 行為正本 = 方法論 `scripts/devflow-evidence-gauntlet.sh` E1–E13(REFERENCE_PASS 既有)+ 本 manifest「dev-run Stage 7 條文」交 Integrator(dev-run = P1 檔) | PENDING(條文就緒,待 Integrator 套用) |
| Test Integrity Review prompt | 本 manifest「Test Integrity Check 七項」交 Integrator(dev-run = P1 檔) | PENDING(素材就緒) |
| Verification Layer events | 本 manifest「事件發射定義」(schema 1.1 對齊;writer 實作 = P3) | PENDING(定義就緒) |

## 交 Integrator:dev-run SKILL 條文(P1 檔 `skills/dev-run/SKILL.md`,P4 不得動)

### Stage 7 Final Fresh Run 派發(送審前置;順序固定)

1. **改動凍結**:所有程式修改完成;其後任何 code 改動 → 全部重跑,無例外。
2. **清 stale artifacts**:入口腳本起手刪舊 coverage/report(機械執行,非靠紀律;
   gauntlet `--report` 模式先刪後寫)。
3. **綁 source SHA**:起跑時 `git rev-parse HEAD`;Evidence 的 `Source SHA` = 該值;
   gauntlet 呼叫必帶 `--source-sha $(git rev-parse HEAD)`(兩端 ≥7 hex;宣告 ≠ 當下
   = stale,E2 機械擋)。
4. **單一入口**:用 4-spec Verification Profile `Final fresh entry point` 指名的
   persisted 一條命令跑完整驗證;所有 Evidence 數字出自這一次 run,禁混入舊結果。
5. **`--require-layer` 逐層**:Profile Required layers 逐層一個 flag 帶入(同
   7-review 執行清單 2c 的文檔化命令;Required 層 unverified/n-a/缺席 = E7 機械擋)。
6. **Evidence 節驗證**:送審前跑
   `bash docs/dev/tools/devflow-evidence-gauntlet.sh <7-review.md> --source-sha $(git rev-parse HEAD) --review-file --require-layer <Required 層,逐層>`
   全綠;`--review-file` 驗 Standards Axis / Spec Axis / 現象證據 三節在場
   (E11:Gauntlet PASS 不取代雙軸審與現象複驗 —— G3 信心 = Gauntlet + Code Review
   + Operational Walkthrough)。
7. **run-id 對帳**:run 產 run_id;Evidence header 與 ledger 事件同 id 同 SHA
   (經 P3 CLI 通道);對不上 = stale 訊號,依 E2 精神擋。

### Test Integrity Check 七項(Stage 6 T-review prompt 增補)

1. 刪 assertion?2. 放寬 assertion(容忍度/範圍/型別)?3. 新增 skip/xfail/todo?
4. 同一步同時改測試與實作以重新定義正確性?5. mock 掉被測物(mock 邊界可,被測物不行)?
6. 只追 coverage(無有意義 assertion)?7. 沒跑的 layer 寫 PASS(對 6-notes 宣稱抽查原始輸出)?
任一命中 → T review FAIL 回同一 T,失敗分類照驗證五律 5。

## 交 Integrator:README §7 新條文安裝需求(Phase 3,方法論 repo)

1. §7 G2 句加 **Verification Profile** 與 **Demo verdict** 錨、G3 句加
   **Evidence 契約全過** 錨;串接寫 `+ **錨**` 或 `**+ 錨**` 皆可(runtime 兩形都抽,
   selftest p4_ 混寫案為證);錨後的定義(G3 八點、G2 Demo verdict 條件式)放非粗體
   說明或後續列點即可,不進機械比對面。
2. 同步五處缺一即 FAIL:README §7 句、README §3 表、plugin dev-flow SKILL 階段表
   (P2 檔)、模板頂註(2-decision / 4-spec / 7-review)、gate-consistency tests
   (plugin 側已就緒,無須再改碼)。
3. 現有 1/14 漂移(4-spec 頂註缺「R/S、全審、全裁決」)隨 OC-2 條文落地一併解:
   4-spec 頂註須覆誦 G2 關鍵條件含新錨。
4. 專案安裝面:新模板經 dev-setup upgrade 覆蓋散發;gauntlet 腳本經 install 步 6 /
   check 9 散發與驗證(本軌已落地)。

## Verification Layer 事件發射定義(schema 1.1;writer 實作 = P3,P4 不實作)

通道:P3 CLI 子命令(agent 禁直寫 `.devflow/`);envelope 必帶
schema/seq/timestamp/run_id/event_type/writer;本組事件 writer = `verifier`。
同一 run 全事件 `run_id`/`source_sha` 必同值(= Evidence header 的 Final Fresh Run
ID / Source SHA);Evidence Matrix 與 ledger 對不上(run_id/SHA/status 任一)= stale。
`status` 四值為正式欄,新事件**只寫 status 不寫 result**(契約 §6)。

| 時機 | event_type | 必帶 | 建議帶 |
|---|---|---|---|
| 入口腳本完成 stale 清除、起跑當下 | `final_fresh_run_started` | `source_sha` | `profile`(lane/Risk 摘要)、`layers_total` |
| 每層命令執行前 | `verification_layer_started` | `layer` | `source_sha` |
| 每層結束 | `verification_layer_completed` | `layer` + `status`(四值) | `command_ref`(≤300)、`result_summary`(一行 ≤200,如 `17 passed, 0 failed`;禁完整輸出/敏感內容)、`artifact_ref`(report/coverage 路徑或 7-review 節錨)、`exit_code`、`source_sha` |
| 被跳過的層(unverified/n-a,未實跑) | 只發 `verification_layer_completed`(無 started) | 同上;skipped 理由放 envelope `note`(≤500) | — |
| 全層結束 | `final_fresh_run_completed` | `verdict`(PASS/FAIL)、`layers_total`、`layers_failed`、`source_sha` | — |

`layer` 值須符 schema pattern `^[a-z0-9][a-z0-9-]*$`:Evidence Matrix 的 Layer 名
slug 化(`Full test suite` → `full-test-suite`);slug 映射由發射端一次定義、
Evidence 與事件共用,禁兩套命名。
