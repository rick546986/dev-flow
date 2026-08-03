# Integration Decisions — DevFlow VNext(Coordinator/Integrator)

> 依 Prompt 0 第七/八步:衝突與矛盾記為 Integration Decision;涉核心流程推翻視 L2 停待人類。
> 本輪四 branch merge 零檔案衝突;以下為「語意合流」決策。日期:2026-08-02。
> 需求正本:docs/prompts/devflow-vnext-fourtrack.md(四軌輪)、docs/prompts/devflow-vnext-runtime.md(Runtime 輪,含 Owner 決策)。
> ⚠️ 歷史區(ID-1~ID-12 原文)回答「當時為何這樣決定」,不重寫;**現在真正生效的規則見文末「Current Decisions」**。

## 決策(ID-1 ~ ID-9)

- **ID-1** B 的 verdict gate 句(「3-prototype Human verdict ≠ ACCEPTED → 相關互動 S 不得於 G2 定案;NOT_REVIEWED ≠ ACCEPTED」)落 **README §5 流程規則**,不動 §7 G 粗體錨正本 —— 避免 plugin `_gate_consistency_impl.py` 連動(該 plugin 本輪不可改)。屬保守、單一正本方案。
- **ID-2** D 的「G3 條件納入 Evidence 契約全過(粗體錨升格)」**本輪不採**(D manifest §5.3 亦建議未升格前走模板執行清單步強制)。G3 條件句不動;7-review 執行清單插 Final Fresh Run 步。→ 待 Owner 裁決升格與否。
- **ID-3** `Risk: normal | high` 二值唯一定義落 **4-spec Verification Profile**;5-tasks T 級 `Risk:` 欄沿用同一判準並于頂註標注「判準見 4-spec Verification Profile」。A/D 兩軌合流,不出現第二套分級。
- **ID-4** 5-tasks **不加** Task Type 欄;stats 以 `x_task_type` 選填承接(採 C 提案)。
- **ID-5** A 的 DD-1「同 Wave 同 Base SHA」(取代全 feature 單一 Base)**維持 worker 設計**:Blocked-by 硬依賴與全域單一 Base 互斥,contract/fixtures 已釘。→ 列 Owner 追認項。
- **ID-6** 並行審查單位詞彙統一 **Candidate**(A 已採);D 的 Stage 6 seam 註記同用 Candidate,不另創詞。
- **ID-7** C 的 Retention 三項(歸檔位置/期限/備份)保留「**待 Owner 裁決**」標注原样,不代答。
- **ID-8** example 補 T-4~T-6 覆蓋 R-3/S-4~S-6(B 軌新增而未同步的 5/6/7),additive、維持 check 腳本硬斷言(actor 字串、T×S 配對)綠。7-review 同步加示範 Verification Evidence 節(D §5.4)。
- **ID-9** 既有兩張 SVG 流程圖(seam 流程/worktree 隔離)**不動**:描繪的 sequential seam 仍正確;parallel 為選配變體,是否補圖待 Owner。

## 套用範圍(檔 → 來源 manifest 節)

| 檔 | 內容 | 來源 |
|---|---|---|
| README.md §5 | T 級並行段(以 ACCEPTED 收尾,防 fenced_seam 第二匹配)+ 守衛條目補句 + B verdict gate 句(ID-1)+ D seam 註記(Task-local 驗證/Final Fresh Run 不逐 T) | A §5.1/5.2、B、D §4.2 |
| README.md §3 表 | Stage 3 行補條件式必要+Demo(renderer readme-stage-table → --write) | B |
| README.md §9 表 | +2 列:Wave review(sonnet fresh/high)、Mechanical Gate(機械) | A §5.3 |
| _templates/4-spec.md | +## Verification Profile(Risk 唯一定義,ID-3)+ Failure Model 表(high 必填)+ Dependencies 註解加嚴 + 執行清單步 3 補「Profile 填畢」+ G2 範圍句(勿動「執行清單(」「起草前估」錨) | D §3 |
| _templates/5-tasks.md | +Task Context Packet 規則(真實世界互動,最小 OC 子集/禁逐字稿)+ Risk 欄註「判準見 4-spec」(ID-3) | B、ID-3 |
| _templates/6-implementation-notes.md | 執行軌跡節:首行 `Run: <run_id>`(五欄不變)+ 頂註「dev-run 案由 devflow-obs 衍生,禁手填」+ parallel 加記(wave/candidate SHA/gate verdict/review 途徑)+ T review 檢查項追加 Test Integrity Check 七項 + T Review Log 加 `- Test Integrity finding:`(勿動 template6-checklist/rules 錨字串本身) | C §4、A §5.4、D §4.1 |
| _templates/7-review.md | +## Verification Evidence + ## Negative Constraint Mapping(Coverage Matrix 後、現象證據前)+ ## Operational Walkthrough(現象證據表後,含 reviewer 六查註解)+ 執行清單插 Final Fresh Run 步(gauntlet 呼叫)+ reviewer 六查入執行清單 + 執行記錄節:改由 devflow-obs stats 衍生註 + 欄位(run_id/模型分佈/升階/first-pass/失敗分類/Prompt Version)+「parallel 加列 wave 分佈與 gate FAIL 重工次數」 | D §5、B、C §5、A §5.5 |
| example/contract-expiry-reminder/{5-tasks,6-notes,7-review}.md | T-4~T-6 覆蓋 S-4~S-6(ID-8)+ 7-review 示範 Verification Evidence/Negative Constraint/Operational Walkthrough | B、D §5.4 |
| guide-*.html + example 6/7 html | 一律 renderer --write 重生,禁手改 | 全部 |
| example {1,4}-discussion/spec html + 3-prototype.html(新) | AI 手工 twin 依 README §6 + html-shell.html 重生/新建 | B |
| scripts/check-vnext-integration.sh(新) | 最薄整合案例(Step 10):T-1/T-2 平行→Candidate→Gate→integration DAG→per-task verdict→Final Fresh Gauntlet→Stage 7 PASS,串 A contract_ref + C schema/events + D gauntlet | Prompt 0 第十步 |

## 補充決策(Step 11 review 後;2026-08-02)

- **ID-10** D/C 事件契約合流(R2 Major-3):`agent-event.schema.json` 擴 `final_fresh_run_started/completed` 兩事件;`verification_layer_*` 欄位支持 Evidence 四值 `status`(pass/fail/unverified/n-a)+ `command_ref/result_summary/artifact_ref/source_sha`,與既有 `result(PASS|FAIL)` 的相容方案由 C 實作定案並以測試釘住;D 設計文件同步引用最終欄名。單一正本 = schema JSON。
- **ID-11** `notes/verification-benchmark-2026-08.md` 為 2026-08 對標的**歷史紀錄**,不因四軌改寫結論;檔首加一行 vnext 指引即可(R2 Minor-1 處置)。
- **ID-12** 消除第二套 G2 定義(R1 Blocker B1):`_templates/4-spec.md` 步 6 與 README §5「Demo verdict gate」句改寫為「審查範圍/流程規則」措辭,明示 gate 條件正本唯 README §7;「Verification Profile 審查」與「Stage 3 Demo verdict」**是否升格為 G2 正式條件(加粗入 §7 + plugin gate-consistency 連動)**列 Owner Call。

## Owner Call 彙整(待 rick,不代答)

1. (D)G3 條件是否升格納「Evidence 契約全過」粗體錨(連動 plugin gate-consistency)。
1b. (ID-12)G2 條件是否升格納「Verification Profile 審查」「Demo verdict ACCEPTED」(同樣連動 gate-consistency;未升格前以階段執行清單強制)。
2. (D)Verification Profile:Full lane 必填/Fast lane 選配?(D 建議:Full 必填、Fast 僅 Risk: high 填)
3. (A)DD-1「同 Wave 同 Base SHA」追認。
4. (C)Retention:歸檔位置(user 層 vs repo docs/dev/…)/保存期限(提案 180 天)/是否納備份。
5. (ID-9)parallel 模式是否補流程圖。

## 外部 Runtime 待辦(plugin repo,本輪一字未動)

彙整自四 manifest:A §6(8 項)、C §11(6 項)、D §8(4 項)、B(SKILL 階段動作表)。
前置:plugin repo 未合併 branch `codex/dev-flow-methodology-corrections` 狀態先確認。

---

## 決策狀態更新(2026-08-02 Runtime 輪;Owner 已於 docs/prompts/devflow-vnext-runtime.md 裁決)

| ID | Status | Superseded by / Replacement | Effective date |
|---|---|---|---|
| ID-1 | **superseded** | OC-2B:Demo verdict 依 trigger 條件正式納入 G2 正本 | 2026-08-02 |
| ID-2 | **superseded** | OC-1:Evidence 依 8 點精確條件正式納入 G3 正本 | 2026-08-02 |
| ID-3 | **refined** | 六修正 6.1:Risk rubric 單一正本,但分 Feature Risk(Stage 4)/ Task Risk(Stage 5)兩個 scope | 2026-08-02 |
| ID-4 | **refined** | 六修正 6.3:改用受控 `task_tags` enum(多選),仍不進 5-tasks 必填欄 | 2026-08-02 |
| ID-5 | **accepted** | OC-3:以 feature_initial_base / wave_base_sha / candidate_base_sha 三層語意正式採用,含 INVALIDATED_BY_UPSTREAM | 2026-08-02 |
| ID-6 | **accepted** | Candidate 詞彙維持 | 2026-08-02 |
| ID-7 | **resolved** | OC-5:Git 外保存(DEVFLOW_LEDGER_HOME,macOS 預設 ~/Library/Application Support/DevFlow/ledger/),raw 180 天/aggregate 365 天,prune 手動 | 2026-08-02 |
| ID-8 | **accepted** | example T-5~T-7 維持 | 2026-08-02 |
| ID-9 | **refined** | OC-6:保留 sequential 圖,立即新增 parallel 圖 ×2(Stage 6 + 跨階段),不等 OC-1/2 | 2026-08-02 |
| ID-10 | **refined** | 六修正 6.4:`result` 只留到 schema 1.x(deprecated),schema 2.0 移除;新事件一律只寫 `status` | 2026-08-02 |
| ID-11 | **accepted** | benchmark 歷史紀錄註維持 | 2026-08-02 |
| ID-12 | **superseded** | OC-1/OC-2:G2、G3 正式升格(含 plugin gate-consistency 同步),不再用「備審材料」過渡措辭 | 2026-08-02 |

## Current Decisions(歷史決策紀錄 —— **不是執行期正本**)

> ⚠️ **正本歸屬(2026-08 fresh review F-7 校正)**:本節原本的標題是
> 「現在真正生效的規則」,那個措辭讓它讀起來像規則正本 —— 但它是 **2026-08-02 那一輪
> integration 的決策快照**,沒有任何腳本讀它、也沒有任何守衛盯它,而它**已經漂了**:
> 下方第 4 條的「升級清單」少了正本裡的「資料刪除」一項
> (正本 `_templates/4-spec.md`「Lane 規則」節是 11 項,這裡是 10 項)。
>
> 本節保留是為了回答「**當時為何這樣決定**」,不得拿來反推現行規則。
> 逐條的執行期正本:
>
> | 本節條目 | 執行期正本 |
> |---|---|
> | 1 G3 正式條件(OC-1) | `README.md` §7「G3 錨定義」八點(由 `scripts/check-gate-tokens.sh` 釘死條數與必含片語) |
> | 2 G2 正式條件(OC-2A/2B) | `README.md` §7「G2 錨定義」 |
> | 3 Wave Base 語意(OC-3) | `notes/design/parallel-stage6.md` |
> | 4 Profile lane 規則(OC-4) | `_templates/4-spec.md`「Lane 規則」節 + `README.md` §7「G2 錨定義」 |
> | 5 Ledger Retention(OC-5) | `notes/design/vnext-shared-contract.md` §8「Ledger 落盤與 Retention(OC-5)」+ `observability/`(schema 與 CLI 實作) |
> | 6-11(Risk/Demo/tags/status/coverage/欄位限制) | 各對應模板與 `notes/design/` 機制正本（Risk 二值 → `_templates/4-spec.md` Verification Profile;事件 schema 與欄位限制 → `notes/design/agent-attempt-observability.md` + `observability/schema/`） |
> | 12 契約握手 | `devflow-contract.json` |
>
> 兩邊有出入一律以正本為準。**要改規則請改正本,不要改本節**——
> 改本節不會有任何測試變紅,那正是它不該被當正本的原因。

1. **G3 正式條件**(OC-1):Final Fresh Run 綁定受審 source SHA;Required Layer 全 pass(不得 unverified/n-a);已觸發 Conditional Layer 全 pass;不得存在 fail;Excluded 可 n-a 但附理由;Optional 可 unverified 但誠實標示;Gauntlet PASS 不取代雙軸 Review/Operational Walkthrough/Coverage Matrix/現象複驗。
2. **G2 正式條件**(OC-2A/2B):Verification Profile 依 lane 正確填寫;Stage 3 trigger 成立時 Human verdict 必須 ACCEPTED(無 trigger → N/A+原因可過;REVISE/NOT_REVIEWED → 不得過;跳過需 Owner Call);Agent 不得自填 ACCEPTED。
3. **Wave Base 語意**(OC-3):feature_initial_base / wave_base_sha / candidate_base_sha;同 Wave 共用 wave_base_sha;下一 Wave 以已 ACCEPTED integration HEAD 為 Base;上游變更 → 下游未整合 Candidate = INVALIDATED_BY_UPSTREAM,須從新 Wave Base 重建;integration branch 可由 wave_base_sha + ordered candidate list 重現。
4. **Profile lane 規則**(OC-4):Full lane 填完整 Profile;Fast lane 填最小 Profile(Risk/Verify/Negative Constraints/排除聲明+理由);命中升級清單(high/migration/權限/不可逆/金流/醫療核心/並發/新 capability/對外 API/高風險互動)自動升 Full;`lane: fast` + `Risk: high` 必須拒絕(除非 Owner Call 例外)。
5. **Ledger Retention**(OC-5):Git 外 DEVFLOW_LEDGER_HOME;raw 180 天、去識別化 aggregate 365 天、transcript/prompt body/source body 不保存;manifest 必含 repo_id/run_id/schema_version/created_at/expires_at/source_sha;`devflow-obs retention status|prune --dry-run|prune`;禁背景自動刪除、預設不雲端同步。
6. **Risk 兩 scope**(6.1):rubric 單一正本;Feature Risk 決定 Profile 深度,Task Risk 決定 review-mode(Task high → Dedicated;Feature high 不強制全 T Dedicated)。
7. **Demo/Variant 分離**(6.2):有互動風險 → Demo 必要;互動方案未定 → 2~4 個結構 Variant;方案已由核准 Pattern 決定 → 1 個 Demo 即可;禁湊數假 Variant。
8. **task_tags**(6.3):受控 enum(api/ui/database/integration/infrastructure/test/documentation/security/authorization/migration/workflow/other),多選,禁自由字串。
9. **status/result**(6.4):新事件只寫 status;result = deprecated since 1.x, removed in 2.0;需 migration tests。
10. **Coverage 語意**(6.5):changed-line coverage 是本次變更的主要證據;global coverage 是趨勢指標,兩者並記,不得只靠 global % 宣稱充分。
11. **Ledger 欄位級限制**(6.6):prompt_id≤100/prompt_version≤40/model≤100/failure_reason≤500/finding_summary≤1000/command_reference≤500/artifact_reference≤1000/result_summary≤2000/task_tag≤50;禁載欄位黑名單照舊;artifact/transcript 只存 reference+hash。
12. **契約握手**(§7):devflow_contract_version 2.0.0 + required capabilities;plugin 聲明 supported versions/capabilities;doctor 指令 fail-closed;legacy 相容模式須明示。
13. **Push 規則**(補充 §1):Runtime+E2E 完成前不更新 origin/main;遠端備份僅限 snapshot branch 且需使用者明示;一切 push 等使用者明示。
