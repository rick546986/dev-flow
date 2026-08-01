# Integration Decisions — DevFlow VNext(Coordinator/Integrator)

> 依 Prompt 0 第七/八步:衝突與矛盾記為 Integration Decision;涉核心流程推翻視 L2 停待人類。
> 本輪四 branch merge 零檔案衝突;以下為「語意合流」決策。日期:2026-08-02。

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
