# Evidence Gauntlet — old-coder 驗證原則吸收設計(Workstream D)

> 目的:把 old-coder(github.com/AmazingAng/old-coder)的 Gauntlet/Evidence 驗證原則
> 吸收進 DevFlow 的 Stage 4/6/7 與 Agent Ledger,**不建立第二套競爭流程**。
> 本檔 = Evidence 契約與 Gauntlet 方法論的設計正本;模板/README 的實際修改建議
> 全部住 `notes/change-manifests/gauntlet.md`(本 workstream 不改共享模板)。
> 研究材料:old-coder README.md、skills/old-coder/SKILL.md、
> skills/old-coder/references/gauntlet.md、demo-rate-limiter/{spec.md, evidence.md,
> tools/gauntlet.sh, tools/mutants.py, tools/source_state.sh}、
> .github/workflows/gauntlet.yml(2026-08-02 clone 實讀)。

## 0. 定位與邊界(先立不變量)

1. **4-spec 是唯一 Spec;7-review 是唯一最終 Evidence/Verdict。**
   不新建 old-coder 式的獨立 spec.md/evidence.md;Verification Profile 住 4-spec,
   Evidence Matrix 住 7-review(節,不是檔)。
2. **Gauntlet 不取代 Stage 7 code review。**
   Standards Axis、Spec Axis、架構審查、現象複驗(reviewer 親跑)、Operational
   Walkthrough、fresh reviewer 鐵則、G3 重驗迴圈全部保留。
   正確關係:**Gauntlet Evidence + Code Review + Operational Walkthrough = G3 信心**。
3. **在既有地基上加層,不重造**:DevFlow 已有 TDD Evidence(RED/GREEN 貼輸出)、
   現象證據表、Coverage Matrix、驗證五律(README §5 正本)、失敗分類與升階鏈。
   本設計只補「證據新鮮度與層級紀律」這一層。
4. **風險分級共用 Workstream A 的 `Risk: normal | high` 二值。**
   不引入 old-coder Tier 1/2/3(與 lane(Full/Fast)× Risk 疊成第三套分級)。
   對映:Tier 1/2 的裁量已由 lane 承擔;Tier 3 觸發條件(金流、auth、資料遺失、
   併發、公開 API)= `Risk: high` 的判準來源。

## 1. Adoption Audit(逐項分類,出處為 old-coder 實際檔案)

### 1a. DevFlow 已有(不重造,僅對齊措辭)

| old-coder 項 | 出處 | DevFlow 既有位置 |
|---|---|---|
| RED→GREEN→REFACTOR、watch-it-fail、立即通過的測試要證明非 vacuous | SKILL.md §2-4 | 6-notes TDD 規則 + TDD Evidence(每 T×S 貼 RED/GREEN 輸出) |
| Spec→Test mapping(scenario 1:1 測試、測試名含 scenario) | gauntlet.md Gherkin 節、evidence.md mapping 表 | README §4 ID 追溯鏈(S-id 入測試名)+ 7-review Coverage Matrix |
| Real execution「測試綠 ≠ 系統能動」 | SKILL.md gauntlet 表 Real execution | 7-review 現象證據表(reviewer 照 4-spec 觀測欄親跑)|
| 證據 = 貼原始數字非自陳 | evidence.md「pasted numbers, not adjectives」 | 驗證五律 1(原始輸出/檔案:行號);本次再機械化(E4 數字規則) |
| Human approves spec(唯一 yes/no) | SKILL.md §1 | G2 gate;HITL 不可代答(驗證五律 4) |
| spec append-only、修訂必須可見 | SKILL.md §1 | L2 契約偏差 → 停、修 4-spec、重 G2(禁 silent drift) |
| Failing gauntlet blocks done | SKILL.md anti-gaming 6 | G3 PASS 條件(README §7);本次擴及 Evidence 層(E6) |
| 回歸零新失敗(baseline note) | SKILL.md §5 baseline note | G3「既有測試全綠」(更嚴:不只零新增,是全綠) |
| 同作者相關性要靠獨立審查打破 | SKILL.md 開場「correlation」段 | author≠approver、fresh-context reviewer 鐵則(README §7/§9) |
| git checkpoint、逐步可回滾 | SKILL.md Setup | 一 T 一 commit(README §5 seam)、gate 文檔 commit |

### 1b. 值得吸收(本次採用;落點見 §2-§10)

| old-coder 項 | 出處 | 落點 |
|---|---|---|
| Evidence status 四值 pass/fail/unverified/n-a | gauntlet.md evidence template | Evidence 契約 + E3 |
| 沒跑不能寫 PASS;invented result 毀掉整個信任 | SKILL.md anti-gaming 5 | E4(pass 必有 Command+Result) |
| skipped layer 必附理由,禁靜默跳層 | SKILL.md §5 | E5 |
| Final Fresh Run:一次 fresh run 出全部數字、stale 不得混入 | SKILL.md §6 | Evidence 契約 §6 + E2 |
| source state 綁定(commit SHA / tree hash,可重算) | evidence.md、tools/source_state.sh | E2(SHA 綁定=「run 晚於最後修改」的機械化身) |
| 單一 persisted entry point、起手刪 stale artifacts、pin 工具版本、CI 可重跑 | gauntlet.md entry point 節、tools/gauntlet.sh(`rm -f .coverage`)、gauntlet.yml | 入口設計 §7 + E12 |
| Changed-line coverage(covered/total;全域 % 是虛榮數字) | SKILL.md 表 Coverage 行 | E8 + 層 menu |
| Mutation 四態 killed/survived/equivalent/error;tool error 不算 killed | mutants.py(僅 exit 1 算 kill)、SKILL.md equivalent-mutant note | E9 + §9 |
| 手動 mutation 程序須 script 化並持久化(禁 scratch) | gauntlet.md manual mutation 節 | §9 工具規則 |
| Property 測試與 mutation 的歸因(kill 記在先失敗的測試;單邊 invariant 抓不到 fail-closed) | SKILL.md mutation caveat、evidence.md layer attribution | §10 方法論註 |
| Negative constraints 必須逐條映射到 test/layer/skipped-with-reason | SKILL.md §1 | E10 + 4-spec 建議(manifest) |
| Failure model 先於層選擇 | SKILL.md Calibration Tier 3 | §3(Risk: high 必填,normal 選配) |
| Test Integrity Check(anti-gaming 1-4 操作化) | SKILL.md anti-gaming 1-4 | §5(Stage 6 seam 建議,manifest) |
| Supply chain / capability diff;新依賴回溯 spec 授權 | SKILL.md 表、gauntlet.md extended menu | §11 + 4-spec Dependencies 語意加嚴(manifest) |
| Suite health(隨機順序;flaky suite 使全部 Evidence 失效) | SKILL.md 表 Suite health 行 | 層 menu(Risk-selected) |
| 誠實失敗紀錄(修過的 gauntlet 與一次過的等值;偷弱化才是失敗) | SKILL.md §6、evidence.md Honest notes | Evidence Matrix「Skipped/Honest notes」欄位語意 |

### 1c. 需風險觸發(`Risk: high` 才進 Required;normal 只在 Failure Model 點名時)

Mutation testing、Property-based tests、Fuzzing、Race/stress、API compatibility、
Rollback rehearsal、Performance benchmark、UI visual regression、Accessibility、
Version matrix、Observability assertions、Adversarial pass(敵意輸入自攻)。
(出處:SKILL.md Calibration Tier 3 + gauntlet.md extended layer menu。)
**不要每個 Task 都跑完整 Mutation** —— mutation/property 屬 feature 級 Final Fresh
Run 的層,不進 Stage 6 的 Task-local 快速驗證(§5)。

### 1d. 不適合(不採用 + 原因)

| old-coder 項 | 出處 | 不採原因 |
|---|---|---|
| Tier 1/2/3 分級 | SKILL.md Calibration | 與 lane(Full/Fast)+ `Risk: normal|high` 撞出第三套分級;Tier 判準已折入 Risk 判準 |
| 獨立 spec.md / evidence.md 檔 | demo-rate-limiter/ | 4-spec 唯一 Spec、7-review 唯一 Evidence/Verdict(§0) |
| /old-coder 式獨立 skill 入口 | README Installation | 不建第二套流程;吸收進七文檔管線 |
| 「human 不讀 code」前提 | README The idea、SKILL.md 開場 | DevFlow Stage 7 雙軸 code review 是硬要求;Gauntlet 是加層不是替代(§12) |
| autonomous mode「spec approval: not obtained,降信心續走」 | SKILL.md §1 | 違反 G2 gate 與驗證五律 4(HITL 不可代答);未過 G2 不得進 Stage 6,無降級續走路徑 |
| 「approve spec = 一步授權環境變更」機制 | SKILL.md §1 setup plan | 與 devflow-exec 守衛/allow 機制職責重疊;僅吸收其輕量語意(Dependencies 需逐條 justification,見 manifest),不搬授權機制 |
| git init 提案 / commit cadence 協商 | SKILL.md Setup | DevFlow git 紀律更嚴且已固定(worktree、一 T 一 commit),無協商空間需求 |
| Gherkin Feature/Scenario 格式 | gauntlet.md 模板 | 4-spec 已有 GWT + S-id + 觀測欄,換格式零增益 |
| tree hash 替代 SHA(無 git 情境) | tools/source_state.sh | DevFlow 前提是 git repo(branch/worktree 是流程一部分),無無-git 情境 |

## 2. Verification Profile(Stage 4 嵌入;模板修改建議 → manifest)

4-spec 新節(G2 一併審):

```markdown
## Verification Profile
- Risk: normal | high            ← 判準:金流/auth/資料遺失/併發/公開 API/不可逆 → high
- Failure model:(high 必填,normal 選配;表見下)
- Negative constraints:(本次變更「不得」做的事,逐條;來源:4-spec Out of Scope、
  living spec 不變量、回歸義務)
- Required layers:(Final Fresh Run 必跑;Baseline 全部 + Failure Model 點名的層)
- Conditional layers:(條件觸發;註明觸發條件,如「dependency set 變動 → Supply chain」)
- Explicitly excluded layers:(明示排除 + 一句理由;禁默排)
- Final fresh entry point:(單一命令,persisted;見 §7)
```

規則:
- `Risk` 與 Workstream A 共用同一欄位、同一二值;不另設值。
- Required 層在 Evidence 裡只能 pass 或 fail;unverified/n-a 不滿足 Required(E7)。
- Excluded 層在 Evidence 裡記 n-a + 理由,維持「層清單全量可稽核」。

## 3. Failure Model(Risk: high 的 Requirement 先回答「怎麼傷人」)

先答:**這個改動可能如何傷害使用者、資料、權限、流程或系統?** 再選層:

```markdown
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
```

候選 failure mode(提示清單,非窮舉):重複提交、部分寫入、權限繞過、資料遺失、
競態、外部 timeout、錯誤 rollback、API 不相容、效能退化、UI 無法操作、
生產環境靜默失敗。
- 每個 mode 必須指到一個「真能抓到它」的層;mutation/coverage 不能替代
  專用層(競態→race/stress、解析→fuzzing、migration→rollback rehearsal、
  靜默失敗→observability assertions)。
- 蓄意不覆蓋的 mode → 「未覆蓋原因」欄明寫,並轉載到 Evidence 的 known limits
  (old-coder demo 對 concurrency 的處理即此模式:明示 not covered — known limit)。

## 4. 驗證層與工具選擇規則

**Baseline(每個 feature 的 Final Fresh Run 至少考慮;不適用記 n-a+理由)**:
Full test suite、Types/compile、Lint/format、Real execution(= 現象證據表的機械前哨)、
Secret scan、Dependency diff(依賴集變動時)、Suite health。

**Risk-selected**:§1c 清單,由 Failure Model 逐 mode 點名。

**工具選擇規則**(吸收 gauntlet.md 首則):
1. **先用專案既有工具**(看 package.json / pyproject.toml / Makefile / CI config),
   不存在才引預設(py: pytest/mypy/ruff/coverage/mutmut/hypothesis;
   ts: vitest/tsc/eslint/Stryker/fast-check;go: go test -race/vet+staticcheck/
   manual mutation/rapid;rust: cargo test/clippy/llvm-cov/cargo-mutants/proptest)。
2. 新工具 = 新依賴 = 4-spec Dependencies 條目(justification 必填,G2 審)。
3. 無成熟工具的層 → 手動程序必須 **script 化持久在 repo**(如 manual mutation
   script),禁一次性 scratch —— Evidence 的可重跑性以檔案存在為準。
4. 工具版本 pin 或記錄(requirements-dev.txt / devDependencies 精確版),
   rerun 才是同一套 gauntlet。

## 5. Stage 6:Task Verify 邊界 + Test Integrity Check

Stage 6 Worker 只跑**快速、Task-local** 驗證,重層留給 feature 級 Final Fresh Run:

```text
RED → GREEN → Task Verify(該 T 的 Verify 欄)→ Test Integrity Check → Candidate
```

(對照既有 seam「RED → GREEN → scope check → Verify → independent T review →
PASS → commit」:Test Integrity Check 是 T review 的檢查清單擴充,不是新階段;
「Candidate」= 送 T review 的狀態,命名對齊 Workstream A。落點建議見 manifest。)

**Test Integrity Check**(T reviewer 至少檢查;吸收 anti-gaming 1-4 並操作化):
1. 是否刪掉 assertion
2. 是否放寬 assertion(容忍度、範圍、型別放鬆)
3. 是否新增 skip/xfail/todo 化測試
4. 是否同一步同時改測試與實作以重新定義正確性(diff 內測試檔+實作檔同動 → 逐一問)
5. 是否 mock 掉核心邏輯(mock 邊界可以,mock 被測物不行)
6. 是否只追求 coverage(只碰行數、無有意義 assertion 的測試)
7. 是否把沒跑的 layer 寫成 PASS(對 6-notes 的宣稱抽查原始輸出)

任一命中 → T review FAIL,回同一 T 修正(走既有 seam 的 FAIL 路徑,失敗分類照
驗證五律 5)。

## 6. Final Fresh Run(Stage 7 前置)

Stage 7 送審前必須:
1. 所有程式修改完成(其後任何 code 改動 → 重跑,無例外)。
2. 清除 stale artifacts(舊 coverage/report;由入口腳本機械執行,非靠紀律)。
3. 綁定當下 source SHA(Evidence 的 `Source SHA` = 跑當下的 HEAD;
   reviewer 以 E2 對照,不符即 stale)。
4. 用 persisted entry point 一條命令跑完整驗證。
5. 所有 Evidence 數字來自這一次 run;中途舊結果不得混入。
6. run 產出 run-id,Evidence 與 Ledger 事件都引它(同 run 同 id,可對帳)。

「Final Fresh Run 晚於最後一次修改」的機械檢查 = SHA 綁定:code 改動必然推進
SHA,宣告 SHA ≠ 當下 SHA ⇒ run 之後又改過 ⇒ E2 擋下。

## 7. Entry point 設計(兩層,職責不同)

**專案層(概念 `./tools/devflow-gauntlet.sh`;實際名稱/位置依採用專案架構)**:
跑真驗證層的單一命令。必須:起手刪舊 coverage/report(保留累積型工具庫,如
hypothesis example store)、逐層執行、fail fast 或明確保存每層狀態、記工具版本、
可由 CI 重跑、可由人一條命令重跑。4-spec Verification Profile 的
`Final fresh entry point` 欄指名它。**runtime 派工(dev-run 引擎叫它)在 plugin
repo,本 repo 只定義此契約 → 外部待辦(manifest)。**

**文檔方法論層(本 repo 實作,已落地)**:`scripts/devflow-evidence-gauntlet.sh`
—— 驗一份 7-review(或任何含 Verification Evidence 節的 md)是否遵守 Evidence
契約:E1 header 四欄、E2 SHA 綁定(比對取宣告值前導 hex token,兩端 **≥7 字元**
才可比對,過短拒絕 —— 防「`f` 對任何 f 開頭 SHA 互為前綴即過」)、E3 四值、
E4 沒跑不寫 PASS+數字非形容詞、E5 skipped 理由、E6 fail 擋 PASS、
E7 required 層須實跑、E8 changed-line 分數、E9 mutation survivor/error、
E10 negative mapping、E11 雙軸不可替代、E12 stale report 清除+run-id/版本/SHA
落 report、E13 malformed 表列 fail-closed(欄數 ≠ 預期 = 明確 error,禁靜默丟列;
儲存格內勿用原生 `|`)。
exit 碼:0 = 契約全過;1 = 有違規;2 = 用法/檔案錯誤(含值型 flag 缺值)。
**E7 的文檔化強制(review 退回 M2 的修正,採方案①)**:7-review 執行清單 2c 的
文檔化命令**本身逐層帶 `--require-layer <Profile Required 層>`**(example 示範
命令同步帶具體層)—— Required 層標 unverified/n-a 或缺席時,照抄文檔命令即紅,
機械執行、非靠紀律。單一正本化(`--profile 4-spec.md` 自動抽 Required layers)
留為後續選項,前提是 example 4-spec 先補 Verification Profile 節。
測試:`scripts/test-evidence-gauntlet.sh` + `scripts/fixtures/evidence-gauntlet/`
(案數與 fixture 數以腳本輸出為準,不在文檔寫死)。本身即依 gauntlet 原則建:
單一命令、可 CI、report 先刪後寫。

## 8. Evidence Status(四值,全域規則)

每層只能是:`pass`、`fail`、`unverified`、`n-a`。
- 沒跑不能寫 pass(E4)。
- 工具不存在/沒跑成 → `unverified` + 理由(E5)。
- 真正不適用(如無 migration 的 rollback rehearsal)→ `n-a` + 理由(E5)。
- 每個 skipped layer 必須有理由;禁默排(E5、Profile 的 Explicitly excluded)。
- 任何 fail → 不得宣告 Stage 7 PASS(E6;對齊 G3「本次 S 全綠+既有全綠」)。

## 9. Changed-line Coverage 與 Mutation

**Coverage**:不看全域 %。Evidence 必列:changed lines covered/total、未覆蓋行
清單、每行未覆蓋理由、branch coverage(工具支援時)。不要求全專案全域 100%。
機械面:E8 —— coverage 層 pass 的 Result 必含 `N/M` 分數。

**Mutation**(Risk: high 或 Failure Model 點名才跑;適用區域:日期/時間邊界、
金額、權限、狀態轉換、重試、錯誤處理、核心業務規則、複雜條件、曾出 bug 區域):
- 結果四態:killed / survived / equivalent / error。
- tool error 不算 killed(吸收 mutants.py:僅「測試跑了且失敗」算 kill;
  collection error/usage error = 什麼都沒驗證)。E9 機械擋。
- survivor 僅兩出路:補測試殺掉,或標 `equivalent + 理由`(為殺 equivalent
  mutant 而加無意義測試 = 違反 anti-gaming)。手寫 mutants 無 equivalent 藉口
  (自己挑的,就挑真 bug)。
- 成熟工具優先;沒有就持久化 manual mutation script(§4 規則 3)。

## 10. Property-based Testing(方法論註)

適用:解析、序列化、排序、日期數學、狀態 invariant、round-trip、idempotency。
- **Property 不能取代具體邊界 Scenario**(4-spec 的 S 仍是主體;property 是
  Risk-selected 加層)。
- 歸因誠實(吸收 evidence.md layer attribution 教訓):mutation kill 記在最先
  失敗的測試上,總分驗證的是整個 suite;要宣稱 property 本身有效,需對 property
  子集單獨重跑 mutants。單邊 invariant(「不超過上限」)抓不到 fail-closed bug,
  要配反向界。stochastic kill 不可靠 → 確定性行為配確定性測試。

## 11. Real Execution 與 Supply Chain / Capability Diff

**Real execution**:Stage 7 必須依 4-spec 每 S 的觀測欄實跑(HTTP request/response、
CLI、UI walkthrough/Playwright、實際產出檔、log/metric)——這就是既有現象證據表,
Gauntlet 只把它同時列為 Evidence 的一層(Baseline),雙處引同一次實跑。
測試全綠不等於系統真的能動。

**Supply chain**(dependency 變動時):dependency audit(pip-audit/npm audit/
govulncheck/cargo-audit)、license check、lockfile diff、每個新依賴回指 4-spec
Dependencies 的 justification。
**Capability diff(所有改動都查,零成本)**:是否新增 network / filesystem /
subprocess / env access / credential capability?**未在 Spec 授權的新 capability
= finding**(進 7-review F-id,不是進 Evidence 就完事)。

## 12. 與 Stage 7 的關係(Gauntlet 不取代什麼)

保留不動:Standards Axis、Spec Axis、架構審查、現象複驗(reviewer 親跑)、
Operational Walkthrough、fresh reviewer 鐵則、G3 重驗 3 輪+breaker。
- Evidence Matrix(見 manifest 模板)是 7-review 的**一節**,供 reviewer 稽核;
  reviewer 仍可(高風險時應)用 entry point 親自重跑 Final Fresh Run 比對。
- E11 機械保底:evidence 全 pass 的 review 檔仍必須有雙軸與現象證據節。
- G3 信心 = Gauntlet Evidence + Code Review + Operational Walkthrough,三者缺一
  不成 PASS。

## 13. Ledger 事件介面(契約 only;實作屬 Workstream C,勿在本軌落地)

> **欄名以 `observability/schema/agent-event.schema.json` 為準**(ID-10 合流:
> `ts`→envelope `timestamp`;status 為正式欄,舊 `result` 為相容別名)。

事件四種(append 進 C 的 ledger 流;命名沿 C 的 snake_case 慣例):

| event | 時機 |
|---|---|
| `verification_layer_started` | 入口腳本開始跑某一層 |
| `verification_layer_completed` | 該層結束(帶 status) |
| `final_fresh_run_started` | 入口腳本起跑(已完成 stale 清除後) |
| `final_fresh_run_completed` | 全層結束(帶 verdict) |

共通欄位(全事件必帶):
- `run_id`:本次 Final Fresh Run 唯一 id(= Evidence 的 Final Fresh Run ID)
- `source_sha`:起跑時 HEAD(= Evidence 的 Source SHA)
- `ts`:ISO-8601 時間戳

layer 級事件另帶:
- `layer`:層名(與 Evidence Matrix 的 Layer 欄同字串)
- `status`(completed 才有):四值 pass/fail/unverified/n-a
- `command_ref`:跑的命令(引用形式;一行)
- `result_summary`:一行摘要(如 `17 passed, 0 failed`)——**禁塞完整輸出/
  敏感內容**;完整輸出住 artifact
- `artifact_ref`:產物引用(report 路徑、coverage 檔路徑、或 7-review 節錨)

run 級 completed 另帶:`verdict`(PASS/FAIL)、`layers_total`、`layers_failed`。
一致性約定:同一 run 的全部事件 `run_id`/`source_sha` 必同值;Evidence Matrix
與 ledger 對不上(run_id/SHA/status 任一)= stale 訊號,依 E2 精神擋。

## 14. 本 repo 落地物清單

- `scripts/devflow-evidence-gauntlet.sh` — 文檔層 gauntlet 入口(E1–E13)
- `scripts/test-evidence-gauntlet.sh` — 測試(案數以輸出為準)
- `scripts/fixtures/evidence-gauntlet/` — fixtures(1 good evidence、1 good
  review,其餘 bad-* 違規類各一;數量以目錄為準)
- 本檔(設計正本)
- `notes/change-manifests/gauntlet.md` — 模板/README/plugin 的待整合清單
