# Plugin Workstream Result — P1 Execution Runtime

- Base SHA: 24057d5
- Branch: devflow-runtime-vnext/execution
- HEAD: 8895613(功能收尾 commit;本 manifest 為其後一格 commit)
- Modified files:
  - hooks/devflow-lib.py(契約核心:parser / 雙 DAG / waves / 狀態機 / review 驗證 / run_id / spec profile)
  - hooks/_exec_impl.py(start --task、exec-v2、parallel-init/plan/wave-open/close、task-candidate/state/integrate/rework、rebuild-plan、review、candidate、OC-4 拒絕)
  - hooks/_gate_impl.py(**新檔**:Mechanical Gate 14 項,bundle + live 兩模式)
  - hooks/devflow-exec.sh(子命令分派 + event/doctor P3 stub)
  - hooks/_guard_impl.py、hooks/_postbash_impl.py、hooks/_prebash_impl.py(task 模式恆許變更)
  - hooks/selftest.sh(p1 新增 98 案,既有 80 案零改動)
  - skills/dev-run/SKILL.md(並行 wave 派工迴圈;sequential 節一字不動)
- Commits(Base → HEAD):
  1. f6a40d8 parallel 契約核心進 devflow-lib + Mechanical Gate(_gate_impl)
  2. 48bf7b4 start --task task-scoped 守衛 + exec-v2 + wave/狀態機/OC-3 runtime 指令
  3. e125c83 selftest 新增 98 案(p1_ 前綴)
  4. 8895613 dev-run SKILL 並行 wave 派工迴圈

## Added capabilities(P1 清單逐項 → 檔:行)

| 能力 | 落點 |
|---|---|
| 解析 execution.mode / max_parallel_tasks / rebuild_integration_on_rework(fail-closed:未知 key / 非法值拒) | devflow-lib.py:279(parse_5_tasks)+ :233(_parse_execution) |
| 解析 Integrate-after / Task Risk / Review-mode / Semantic-conflicts-with(high+wave 拒、自我引用拒、引用不存在拒;sequential 也驗) | devflow-lib.py:279-370 |
| execution DAG / integration DAG + cycle detection(環路徑入訊息) | devflow-lib.py:373/377/383 |
| Files overlap detection(canonical + 目錄前綴) | devflow-lib.py:185 |
| Semantic conflict handling(對稱禁同 wave) | devflow-lib.py:419(compute_waves 內 conflicts) |
| max parallel tasks | devflow-lib.py:419(greedy 上限) |
| Wave Base 計算(OC-3 三層:feature_initial_base / wave_base_sha / candidate_base_sha) | _exec_impl.py:479(parallel-init)/:545(wave-open 釘 base)/:606(task-candidate 記 candidate_base_sha) |
| Candidate invalidation(INVALIDATED_BY_UPSTREAM 連鎖 + 續審/整合全面拒) | _exec_impl.py:711(task-rework cascade :763)、:653(task-state 拒)、:696(task-integrate 拒)、_gate_impl.py live 模式拒 |
| `start <slug> --task T-n`(scope=單 T Files;--wave/--base/--feature-base;--base 與 HEAD 不符拒;sequential 檔拒 --task) | _exec_impl.py:192-385(task 分支 :344) |
| Task-scoped guard(5-tasks/6-notes 移出恆許;.devflow/task/<T-id>/ 放行;prebash redirect 自身 evidence 放行) | _guard_impl.py:46-59、_postbash_impl.py:16-22、_prebash_impl.py:30-34 |
| Candidate Commit 支援(task 樹 exec-v2 登記 + feature 帳 task-candidate;不可變、rework=新 candidate) | _exec_impl.py:449(candidate)/:606(task-candidate) |
| Mechanical Gate 14 項(devflow-gate-result.v1;bundle 對拍模式 + live git 事實模式,結果落 evidence 區) | _gate_impl.py:57(run_gate)/:140(main;candidate_exists :109、diff_applies :119) |
| Task 狀態機(11 態合法轉移全集 + dedicated/wave 語意閘 + 未整合不得 ACCEPTED + can_tick) | devflow-lib.py:470/484、_exec_impl.py:635(task-state) |
| Wave integration(integration DAG 順序強制 + integration_log 重放帳) | _exec_impl.py:684(task-integrate) |
| Dedicated / Wave Review(review_mode 路由 + devflow-wave-review.v1 驗證,bundle 與 live wave 兩模式) | _exec_impl.py:804(review)、devflow-lib.py:495 |
| fast+high 拒絕(start / parallel-init 時讀 4-spec Profile lane/Risk;Owner Call 例外) | _exec_impl.py:42(spec_gate)、devflow-lib.py:527(spec_profile) |
| Rework 後 integration rebuild 語意(rebuild-plan:base + ordered candidates 重放清單;rebuild=false 走 revert 單 T;上游未變 rework 保原 wave base) | _exec_impl.py:711/783 |
| exec.json v2(schema 鉤子 "exec-v2"、run_id、mode/task/wave/candidate_sha/state/feature_initial_base;v1 檔相容) | _exec_impl.py:361-384;postbash 舊格式分支原樣保留 |
| run_id = "run_"+26 字 Crockford ULID(runtime 產生,未 import 方法論 ids.py) | devflow-lib.py:202 |
| dev-run wave 派工迴圈(Packet / candidate→gate→integration→review→ACCEPTED 記帳 / conflict 不親修 / OC-3 rework) | skills/dev-run/SKILL.md「並行模式」節 |
| sequential regression(零回歸) | 見 Raw outputs:legacy 路徑 byte-identical 實測 |

## Tests before

- `bash hooks/selftest.sh` @ 24057d5:**80/80 全過**
- `bash hooks/gate-consistency.sh`(DEVFLOW_MASTER=方法論 repo):**基線紅 1/14**(4-spec 頂註 token,20-runtime-audit.md 既載明,屬 P4/Phase 3 範圍,本軌未動)

## Tests after

- `bash hooks/selftest.sh` @ HEAD:**178/178 全過**(80 既有 + 98 p1 新案;新案函數/命名帶 p1 前綴,既有 80 案一案未改)
- gate-consistency:仍 1/14 基線紅(與 before 相同;本軌零影響)
- RED 留痕:把新 selftest 跑在 Base SHA 24057d5 的 hooks 上 → **106/178,失敗 72 項**(全部是 p1 案;raw 見 scratchpad selftest-red-on-base.txt,關鍵行摘錄於下)

## Raw outputs(關鍵行)

```
[baseline]   ✅ 守衛自測 80/80 全過
[RED @base]  ❌ 守衛自測 106/178,失敗 72 項
[GREEN]      ✅ 守衛自測 178/178 全過
[對拍]       對拍結果:37 OK / 0 BAD(fixtures 25 檔 + 真檔 example + 派生行為)
             md 10/10 parse 結構全等;gate 10/10 verdict+failed check id 集合全等;
             wave-review 5/5 錯誤列表全等;waves/task_scope/狀態機/DAG 派生全等
[零回歸]     legacy repo 舊碼 vs 新碼:start stdout diff 空(START-STDOUT-IDENTICAL)、
             exec.json 除 started 時戳外全等且無 v2 欄位、status/stop 輸出全等、
             四類錯誤路徑(缺欄/髒檔/非 approved/雙 start)stdout+rc 全等
```

對拍腳本與原始輸出:session scratchpad `p1/duipai.py`、`p1/duipai-green.txt`、`p1/selftest-red-on-base.txt`、`p1/old-*.out`/`new-*.out`(byte 比對)。

## Known limitations

1. **ACCEPTED→REWORK 不在狀態機轉移全集**:OC-3「上游 Accepted Commit 變更」要求可推翻已接受 T;runtime 以 `task-rework --owner-call "..."` 留痕例外實作(transitions 記 owner-call exception)。契約狀態機表未含此邊 —— 需 Owner/Integrator 確認是否回寫設計文件。
2. **--task 要求 execution.mode: parallel**(sequential 檔拒 --task)——契約未明文,P1 裁決:task-scoped 武裝只屬 wave 派工語意,避免 sequential 使用者誤入半套模式。
3. **start 不帶 --task 一律寫 v1 exec.json**(含 mode: parallel 檔;契約 §7「不帶 --task = v1 語意」),parallel 檔會多印一行 ℹ️ 提示。
4. **legacy 檔(無任何 VNext 欄位)不驗 Blocked-by 引用完整性**——byte-identical 鐵則優先;含任一新欄位即走完整驗證(DD-5)。
5. **live gate 的 diff_applies 需 git ≥ 2.38**(`merge-tree --write-tree`);更舊 git → fail-closed 判 FAIL(不靜默放行)。
6. **4-spec Profile 的 lane token 由 P1 先行定義**:`lane: fast|full` 行、`- Risk:` 首值、Owner Call 例外 = 同行含 owner[- ]call + fast + high(case-insensitive)。4-spec 模板尚無 lane 欄 —— 模板/gate 檢查側需 P4 / 方法論軌 Phase 3 對齊此格式(跨界事項,見下)。
7. Semantic conflict handling = `Semantic-conflicts-with` 欄的排程隔離(對稱禁同 wave)+ review 人審;無自動語意衝突偵測(契約範圍如此)。
8. wave/feature-base 於 task worktree 由派工者以 `--wave/--feature-base` 旗標傳遞(feature 級正本在 coordinator 樹 `.devflow/parallel.json`,task 樹讀不到);未傳時 wave=1、feature_initial_base=wave base。
9. E2E(真 /dev-flow 跑 throwaway repo)未做 —— 屬 Phase 4,非本軌範圍。

## External dependencies

- /usr/bin/python3(stdlib only;與既有 hooks 相同)
- git ≥ 2.38(僅 live gate diff_applies;本機 2.43.2 實測)
- 無新第三方依賴;未 import 方法論 repo 任何程式(run_id 依 §7 重寫)

## 跨界事項(交 Integrator)

- **devflow-exec.sh `event`/`doctor`**:P1 裁決採「預留分派 stub」(擇一記錄):兩子命令現印 fail-closed 訊息並 exit 3,P3 落地 `_obs_impl.py`/`_doctor_impl.py` 時把該 case 行改為實分派即可(單行 patch,無結構衝突)。
- 4-spec `lane:` 欄格式對齊(見 Known limitations 6)→ P4(模板檢查/gate)與方法論軌 Phase 3。
- gate-consistency 基線紅 1/14 未動,屬 OC-2 條文落地(Phase 3)。

## Status(能力逐項)

| Capability | Status |
|---|---|
| execution.mode / 新欄位解析(fail-closed) | RUNTIME_PASS(selftest p1 parser 9 案 + 對拍 10/10 md) |
| 雙 DAG + cycle / overlap / max | RUNTIME_PASS(p1 dag/waves 6 案 + 對拍派生全等) |
| Wave Base 計算(OC-3 三層) | RUNTIME_PASS(p1 wave-open/cand-base 案:wave_base 釘 HEAD、candidate_base_sha=wave base) |
| Candidate invalidation(INVALIDATED_BY_UPSTREAM) | RUNTIME_PASS(p1 invalidation 連鎖 4 案:標記/拒審/拒整合/新 wave 重建) |
| start --task task-scoped guard | RUNTIME_PASS(p1 13 案:scope/恆許變更/雙 start/--base/evidence 區) |
| Candidate Commit 支援 | RUNTIME_PASS(p1 candidate 3 案 + gate live 真 commit) |
| Mechanical Gate 14 項(devflow-gate-result.v1) | RUNTIME_PASS(p1 gate 10 案 + live 3 案;對拍 10/10 全等) |
| Task 狀態機 | RUNTIME_PASS(p1 statemachine + 轉移閘 6 案;對拍 STATES/TRANSITIONS 全等) |
| Wave integration(DAG 順序) | RUNTIME_PASS(p1 integrate 順序 3 案) |
| Dedicated / Wave Review | RUNTIME_PASS(p1 dedicated 閘 2 案 + review 驗證 7 案;對拍 5/5) |
| fast+high 拒絕(OC-4) | RUNTIME_PASS(p1 2 案:拒 + owner-call 例外) |
| rework 後 integration rebuild | RUNTIME_PASS(p1 rebuild-plan 2 案 + rework 語意案) |
| exec.json v2 + v1 相容 | RUNTIME_PASS(p1 exec-v2 / v1-exec 案 + postbash 舊分支保留) |
| run_id ULID | RUNTIME_PASS(p1 run-id 案 + exec-v2 格式斷言) |
| dev-run SKILL wave 迴圈 | RUNTIME_PASS(文檔落地;流程指令全部對應已實測 CLI)|
| sequential 零回歸 | RUNTIME_PASS(既有 80/80 一案未改全綠 + 舊/新碼 byte 比對:stdout、exec.json、錯誤路徑全等) |
| 真實 E2E | PENDING(Phase 4 範圍:throwaway repo 走完整 /dev-flow 正負向) |

## Rework round 2(E2E findings F1-F3;integration branch)

- Base: aebfe1d → HEAD: 8403eff(commits b6ce235 F3 / 6ebbfb4 F1 / 8403eff F2)
- selftest:前 260/260 → 後 **271/271**(新增 11 案,全 p1 前綴;RED 留痕:
  F3 260/262 敗 2、F1 261/264 敗 3、F2 265/271 敗 6 —— F1/F2 的 RED 即 E2E
  原故障重現:未 cherry-pick 竟 INTEGRATED、review 未登記竟 ACCEPTED)
- **F1 方案(裁決記錄)**:blob 比對 —— candidate_sha 必須 rev-parse 為 commit,
  其 diff-tree 每個變更路徑 HEAD blob == candidate blob(刪除檔則 HEAD 必無);
  cherry-pick 產物 commit 不同但 blob 相同,故不比 commit ancestry / patch-id。
  檢查在 preds 之後、狀態轉移之前(fail-closed 不動狀態);拒絕訊息附
  cherry-pick + Verify 指引。時點語意:驗「integrate 當下」——同 wave 無檔案
  重疊(排程保證),cross-wave 重疊只會發生在更早已整合的 wave,故 blob 比對
  在該時點無誤判面。_exec_impl.py task-integrate 段。
- **F2**:review live 驗證通過才登記 parallel.json `reviews[wave]`(wave 編號
  不符拒登記;--bundle 模式維持純驗證);ACCEPTED 三重前置(已登記 / 該 T
  verdict=PASS / integration_verdict=PASS)。dedicated 成員同受 wave review
  覆蓋(schema 要求每 T 獨立 verdict),同一道閘;dedicated 的整合前
  IN_REVIEW→QUEUED 仍屬派工者責任(未加獨立登記,超出 finding 範圍,如需
  另立 dedicated review 登記面待 Owner 裁決)。
- **F3**:Owner Call 例外只認結構化專用欄 `- Owner Call 例外:<非空理由>`
  (Owner-Call/半形冒號/大小寫可;雜訊行、空理由不觸發);devflow-lib.py
  spec_profile + 拒絕訊息指引同步。
- 既有案零改動聲明:所有既有 ck 名稱與期望值不變;為使 F1 可驗,fixture
  candidate 由假 SHA 升級為真 commit(3 處 glue + 1 處 ck 的 SHA 引數改用變數)、
  F3 例外行改用新結構格式(1 處 glue)—— 均為 fixture 輸入升級,非斷言弱化。

## Rework round 3(終審 R1 MAJOR-C:shadow-hash 竄改偵測)

- **修法裁決**:fail-closed 偵測(不追求 prevention)。CLI(_exec_impl)每次合法寫
  `.devflow/{exec,parallel}.json` 後把兩檔 hash 記進 git-dir `devflow-armed-shadow`
  (檔名刻意含 devflow-armed 子字串 → prebash 既有「cmd 含 devflow-armed 即擋」
  規則連帶封鎖 shell 指名觸碰,零新 regex);postbash 武裝時逐檔比對現檔 hash vs
  shadow,不符/檔在而 shadow 缺 → tamper alarm exit 2 指明檔名;CLI 亦拒建立在
  遭竄改狀態上(load_parallel / allow / candidate / gate live 先驗),復原 = 重新
  start / parallel-init --reset。heredoc/python 直寫的 prebash regex 軍備競賽不跟
  (治標),以 postbash 偵測為主;guard(Edit/Write 工具面)原樣。
- 已知界限:①shadow 住 git-dir,bash 以字串拼接混淆路徑直寫 .git 可雙點竄改 ——
  屬「蓄意雙點」,超出本輪目標(無知情繞過已封);②守衛沉睡(未武裝)期間竄改
  不偵測 —— 與 guard 家族 armed-only 語意一致;③重新 start 重建 shadow 會信任
  當下檔案內容(重建即重釘,與 re-arm 重建 scope 同語意)。
- selftest:283/287 敗 4(RED:heredoc 直改 exec.json scope / 偽造 parallel.json
  ACCEPTED 均無人攔、allow 照樣擴 scope)→ 287/287 全綠;legacy start/status/stop
  stdout 重驗 byte-identical;gate-consistency 14/14。
