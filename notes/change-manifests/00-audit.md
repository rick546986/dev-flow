# Audit

> DevFlow 四軌並行改造 — 開工前護欄。四個 workstream worker 開工前必讀。
> 產出依據:5 份 reader 回報(templates / renderer / runtime / example-tests / history)+ coordinator 現場覆核(2026-08-02)。
> 路徑為 repo 根相對;plugin 路徑寫全。

- Base SHA: 90d30e88294ab4168871a877ef8ffc398ec3b817(main;coordinator 現場 `git rev-parse HEAD` 覆核。上游模板注入值為 "undefined",為變數未展開,以實測 SHA 為準,見不確定事項)

- 規則正本:
  - `README.md` — 方法論唯一正本。§5 acceptance seam + 驗證五律(:108-186 區)、§7 gate G1/G2/G3 唯一正本(:239-264,粗體詞組是 gate-consistency 機械錨,:256-258)、§6 圖表選用判準(:208-213)、§9 模型分層表(:293-305)、worktree 並行語意(:155-161)、html twin 規則(:199)、殼檔雙副本宣告(:235)。
  - `_templates/` 14 檔 — 七階段模板(1-7)+ adr / arch-invariants / CONTEXT / diagram-style / html-shell.html / living-spec / STATUS。各 Stage 執行清單全文住模板頂註(README.md:93-96)。
  - 升階/失敗分類規則的正本在本 repo README §5/§9;plugin dev-run SKILL.md 只是摘要副本。

- 衍生檔:
  - **renderer 追蹤(共 4 個 tracked outputs,禁手改)**:`guide-dev-flow.html`(9 個 parity marker 區)、`guide-quickstart.html`(4 個 parity marker 區)、`example/contract-expiry-reminder/6-implementation-notes.html`、`example/contract-expiry-reminder/7-review.html`(後兩者全檔生成)。重生:`scripts/render-methodology-corrections.sh --write`。
  - **AI 手工 twin(無腳本覆蓋)**:example 的 1/4/5 三個 .html(檔首有殼註)、2-decision.html(無殼註無 marker,來源未查證)。改對應 md 後須依 README §6 + html-shell.html 手工重生。
  - **手寫正本(非衍生)**:guide-dev-talk.html、dev-setup-record.html、_templates/html-shell.html(是生成輸入)。
  - ⚠️ renderer 抽取靠**錨字串定位**(如「執行清單(」「反模糊三律(」、README `## 3.` 表)。改造若動到錨點措辭,renderer 直接 SystemExit,須同步改 scripts/ 兩支腳本的 fragments/parity 對照表(render 腳本 :112-137)。

- Runtime 所在位置:**不在本 repo**。全部執行引擎住 `~/.claude/plugins/local/dev-flow/`(獨立 git repo、master branch、**無 remote**;coordinator 覆核 hooks/ 目錄 14 檔實存):
  - hooks:`devflow-exec.sh`(15 行薄殼)+ `_exec_impl.py`(209 行,含 5-tasks parser :61-98、guard state :13-45)、`_guard_impl.py` + `devflow-lib.py`(fail-closed :118-139)、`_prebash_impl.py`/`_postbash_impl.py` + 薄殼、`devtalk-guard.sh`、`selftest.sh`(332 行)、`gate-consistency.sh` + `_gate_consistency_impl.py`(303 行)、`hooks.json`(4 條掛載 :3-50)。
  - skills:dev-flow / dev-run / dev-setup 三支 SKILL.md(77/76/130 行)。scheduler、worktree 管理、review runtime 皆為 prompt 層(dev-run SKILL.md:49-63),無獨立程式碼。
  - 本 repo `ls` 實測**無 hooks/ 也無 skills/ 目錄**。本 repo 的 `scripts/` 是文檔校驗工具,非執行引擎。
  - 兩 repo 內容不重疊、**無自動同步機制**;母版→專案同步走 dev-setup skill 複製 README + _templates 進專案 docs/dev/。

- 現有測試(基線 2026-08-02 全綠 @ 90d30e8):
  1. `bash scripts/check-methodology-corrections.sh` → `✅ methodology correction checks: 74/74 passed`(含 parity marker、example T×S evidence 配對 :226-251、actor 字串斷言 :254、renderer fixed point)。
  2. `DEVFLOW_RENDER_PYTHON=python3 bash scripts/render-methodology-corrections.sh --check` → `✅ renderer fixed point: 4/4 tracked outputs byte-identical`(依賴 markdown-it-py==4.0.0,pin 在 scripts/requirements-methodology-render.txt)。
  3. plugin 側:`~/.claude/plugins/local/dev-flow/hooks/selftest.sh`(守衛自測,自建 temp 假 repo,~33 案)、`gate-consistency.sh`(從母版 README §7 動態抽 token 比對 SKILL/模板)。
  - 本 repo 無 pytest/vitest/bats。

- 已存在能力(勿重造):
  - **Evidence 體系(D 的地基)**:TDD Evidence 強制貼 RED/GREEN 輸出(_templates/6-implementation-notes.md:81-84)、T Review Log(:59-69)、Stage 7 現象證據表 reviewer 親跑(_templates/7-review.md:57-66)、Coverage Matrix(:46-52)、check 腳本機械驗 evidence 配對。
  - **執行軌跡節(C 的地基)**:_templates/6-implementation-notes.md:75-78 已有 attempt/model/failure category/escalation 每 T 一列(選配,供 dev-run 引擎);升階上限正本 README.md:184-186(同 T ≤4:haiku1+sonnet2+opus1)。
  - **失敗分類 SPEC/ENV/IMPL/UNKNOWN** + 路由(README §5 驗證五律 5;dev-run SKILL.md:60-63)。
  - **Stage 3 UI variants 互動挑**(_templates/3-prototype.md:13-14,2-4 variants、throwaway branch)——B 的鄰近種子。
  - **Stage 7 現象複驗**(reviewer 照觀測方式親自實跑)——「真實世界互動驗證」的既有種子在 Stage 7 而非 Stage 3。
  - **worktree 級並行 + 守衛隔離**:多 feature 各開 worktree、state per-worktree 天然隔離(`.devflow/exec.json` + git-dir sentinel)、異 slug start 拒絕(README.md:155-161;plugin _exec_impl.py:27-45)。
  - **4-spec 每 S 觀測欄**(從哪看/看到什麼算對/拿什麼資料試,_templates/4-spec.md:59)承接 1-discussion 驗收雛形(:40-46)。
  - **雙軸 fresh reviewer 禁合併**(_templates/7-review.md:30-32)、G3 重驗 3 輪 + breaker(:35-42)。

- 真正缺口(history reader 全 repo grep 證實零命中):
  - **A**:Stage 6 內 T 級並行/wave/candidate 概念完全不存在(parallel/wave/candidate 零命中);5-tasks 無 execution mode/parallel 欄位;README.md:155-160 明文「同一工作樹內硬要並行做不到」。
  - **B**:Demo/Actor/Operational/Journey 零命中;example 亦全缺席(grep demo|actor|operational|等待|權限 零命中);1-discussion 無 Real-world Context 專節(只有 Problem 註的「現在怎麼繞過」);3-prototype 的 Verdict 是「回寫 2-decision」非 user verdict,無 Demo 節。
  - **C**:attempt ledger/observability 零實質命中(notes 的 "ledger" 是別家工具比較表);無獨立 attempt 記錄結構——只有 6-notes 執行軌跡節那一列摘要。
  - **D**:Gauntlet/mutation/verification profile 零命中;4-spec 無 Verification Profile / Operational Context 節。
  - devflow-vnext/* branch 與 worktree 皆不存在;四軌均無雛形已埋。

- 不應重複建立的東西:
  - Evidence 概念(D 在既有 TDD Evidence/現象證據表之上加 Gauntlet 層,勿另起一套 evidence)。
  - 失敗分類法與升階規則(C 引用 README §5/§9 既有定義,勿重定義)。
  - worktree 隔離機制(A 的 Stage 6 內並行須在「守衛 per-worktree、一工作樹一模組」既有前提之上設計,勿另造隔離)。
  - variants 挑選機制(B 的 Demo 應銜接 Stage 3 既有 variants 節與 Stage 7 現象複驗,勿平行再造)。
  - gate 正本(任何新 gate 條件寫進 README §7 唯一正本 + 粗體錨,再同步三處摘要,README.md:239-243;勿在模板側另立正本)。
  - html twin/renderer 機制(新增文檔節時沿用 html-shell.html 殼與 parity 模式,勿發明第二套渲染)。

- 四條 Workstream 的實際可修改範圍:
  - **A(Stage 6 並行執行)**
    - repo 內可真改:`README.md`(§5/§7/§9、worktree/並行語意節)、`_templates/5-tasks.md`(如加並行/wave 欄位)、`_templates/6-implementation-notes.md`、`example/`(示範同步)、`guide-*.html` parity 區(經 renderer --write)。
    - 只能寫 interface contract:5-tasks parser 改動(plugin `_exec_impl.py:61-98` 只解析必填四欄)、scheduler/wave 執行邏輯(dev-run SKILL.md prompt 層)、守衛 scope 語意(_guard_impl.py/devflow-lib.py)、devflow-exec.sh start 語意——這些全在 plugin repo,本 repo worker 只能產 schema/欄位定義/行為契約文檔。
  - **B(真實世界互動)**
    - repo 內可真改:`_templates/1-discussion.md`(Real-world Context/Actor 節)、`_templates/3-prototype.md`(Demo/user verdict 節)、`_templates/4-spec.md`(Operational Context 之類)、`_templates/7-review.md`、`README.md` 對應節、`example/` 全套 md + 手工 twin html。
    - 只能寫 interface contract:dev-flow/dev-run SKILL.md 的階段動作表同步(plugin repo)。⚠️ 改 example 5/6/7 必過 check 腳本硬斷言(actor 字串 :254、T×S evidence 集合 :226-251);改 example 6/7 md 須跑 renderer --write 重產 html。
  - **C(Attempt ledger 可觀測性)**
    - repo 內可真改:`_templates/6-implementation-notes.md` 執行軌跡節擴充(ledger 格式/schema)、`README.md` §5/§9(記錄義務)、`_templates/7-review.md` 執行記錄節(:54-55)、`example/` 示範、ledger 檔案格式 spec(新檔,如 notes/ 或 _templates/)。
    - 只能寫 interface contract:實際寫 ledger 的 runtime(dev-run SKILL.md 派工迴圈、devflow-exec/hook 若要機械記錄)——皆在 plugin repo;本 repo 只能定義 ledger schema + 讀寫契約 + fixture。
  - **D(Gauntlet Evidence 驗證)**
    - repo 內可真改:`_templates/7-review.md`(Gauntlet 層節)、`_templates/4-spec.md`(如加 Verification Profile)、`README.md` §7(G3 條件變更走唯一正本 + 粗體錨 + 三處摘要同步)、`example/7-review.md` + renderer --write、`scripts/check-methodology-corrections.sh`(若加機械檢查——注意此腳本是本 repo 的,可改,但 74 條基線須維持綠)。
    - 只能寫 interface contract:gate-consistency 機械比對邏輯(plugin `_gate_consistency_impl.py`)、review runtime 派工(dev-run SKILL.md)——plugin repo;本 repo 只能定義 Gauntlet 的檢查項清單與 evidence 契約。
  - **全軌共通**:改 README/模板任何被 renderer 錨定的措辭 → 須同步 `scripts/render-methodology-corrections.sh` 與 `check-methodology-corrections.sh` 的對照表(兩支都在本 repo,可改);完工驗收 = 74/74 + fixed point 4/4 全綠。plugin repo 若需配套改動,由 coordinator 另開 plugin repo 的工作,不在本 repo worker 職權內。

## 8 問明答

1. **哪些檔案是規則正本?**
   `README.md`(gate 唯一正本宣告 :239-243;G3 :262-264;驗證五律 :167-186;升階上限 :184-186;§9 :293-305)與 `_templates/` 14 檔(各 Stage 執行清單住模板頂註,README.md:93-96)。notes/verification-benchmark-2026-08.md 明示自己「非規則正本」(:3-5)。plugin 三支 SKILL.md 是摘要副本,回指母版正本(2-decision.md:45、4-spec.md:47、7-review.md:36 皆註「正本 README §7」)。

2. **哪些 HTML 是衍生產物?**
   renderer 追蹤 4 個:guide-dev-flow.html(9 marker 區)、guide-quickstart.html(4 marker 區)、example 6/7 兩個 html(全檔生成)——證據:scripts/render-methodology-corrections.sh:112-137(fragments 表)、:166-182(shell.replace)。AI 手工 twin:example 1/4/5 html(檔首殼註)+ 2-decision.html(來源未查證)。非衍生:guide-dev-talk.html、dev-setup-record.html(grep parity=0、無腳本引用)。

3. **執行引擎是否在此 repo?**
   **否**。本 repo `ls` 實測無 hooks/ 無 skills/ 目錄(coordinator 2026-08-02 覆核)。引擎全在 `~/.claude/plugins/local/dev-flow/`(獨立 repo、無 remote)。本 repo scripts/ 兩支腳本是文檔校驗器,非引擎。

4. **hooks/devflow-exec.sh 是否在此 repo?**
   **否**。位於 `~/.claude/plugins/local/dev-flow/hooks/devflow-exec.sh`(15 行薄殼,case 分派見 :10-14),本體 `_exec_impl.py`(209 行)。coordinator 覆核該目錄 14 檔實存。

5. **若不在,實際位於哪個 plugin/skill/安裝路徑?**
   `~/.claude/plugins/local/dev-flow/`——hooks/(devflow-exec.sh、_exec_impl.py、_guard_impl.py、devflow-lib.py、_prebash_impl.py、_postbash_impl.py、devtalk-guard.sh、selftest.sh、gate-consistency.sh、_gate_consistency_impl.py、hooks.json 等 14 檔)+ skills/{dev-flow,dev-run,dev-setup}/SKILL.md。兩帳號(.claude/.claude-team)的 known_marketplaces.json `local` marketplace 皆指向此目錄。掛載定義 hooks.json:3-50(4 條 PreToolUse/PostToolUse)。

6. **哪些建議只能在本 repo 寫介面契約?**
   凡涉及 runtime 行為者:5-tasks parser 擴充(_exec_impl.py:61-98)、T 排程/wave 執行(dev-run SKILL.md:49)、模型升階執行(SKILL.md:40-47)、守衛 scope/start 語意(_guard_impl.py、_exec_impl.py:27-45)、ledger 實際寫入、gate-consistency 比對邏輯(_gate_consistency_impl.py)、三支 SKILL.md 的任何改動。本 repo worker 對這些只能產:schema、欄位定義、行為契約文檔、fixture。詳見上方四軌範圍表。

7. **現有 renderer/selftest/parity 指令?**
   - parity 檢查(read-only):`bash scripts/render-methodology-corrections.sh --check` → 4/4 byte-identical(基線綠)。
   - 重生衍生檔(寫檔):同腳本 `--write`。
   - 完整驗證:`bash scripts/check-methodology-corrections.sh` → 74/74 passed(基線綠)。
   - python 依賴 markdown-it-py==4.0.0(硬驗版本,render 腳本 :24-32),可 `DEVFLOW_RENDER_PYTHON` 覆寫直譯器。
   - plugin 側(不在本 repo):`~/.claude/plugins/local/dev-flow/hooks/selftest.sh`(守衛自測)、`gate-consistency.sh`(gate 漂移檢查)。

8. **現有 main 是否已有未完成的相關實作?**
   **無**。全 repo 僅 13 commits;history reader 對 parallel/wave/candidate/attempt/gauntlet/journey/operational/demo 全零命中;devflow-vnext/* branch 與 worktree 皆不存在。僅兩個鄰近既有(是地基非半成品):fdb51ff 驗證五律(D 銜接)、4548e5c worktree 並行語意(A 的前提)。另一 worktree `../dev-flow-methodology-corrections`(codex/dev-flow-methodology-corrections @ 4cdd68c)是舊 docs 修正殘留,與四軌無關。

## 主 worktree 髒檔現況

`git status --porcelain` = `?? .serena/` + `?? docs/`(皆 untracked,coordinator 2026-08-02 覆核)。**判定安全**:
- `.serena/` = serena 工具本地設定(project.yml/memories),非改造標的。
- `docs/` = 改造參考材料(「DevFlow 四軌並行改造 Prompt.docx」+ 舊 superpowers plan md),非實作、非 tracked。
- 兩者不影響測試基線(74/74 與 4/4 皆在此狀態下實跑全綠)。worker 不得動這兩個目錄,也不需 stash。

## 不確定事項

1. **Base SHA 注入值為 "undefined"**:上游任務模板的變數未展開。實測 HEAD = 90d30e8(與 history reader 一致),本檔以實測值為準。
2. **example/2-decision.html 的生成來源未查證**(renderer reader 明示):無殼註、無 parity marker、無腳本覆蓋。改 2-decision.md 時此 html 如何重生需現場判斷(建議照 twin 規則以 html-shell 手工重生)。
3. **plugin 載入解析順序未查證**(runtime reader 明示):installed_plugins.json 記的 installPath cache 目錄實際不存在,實際載入走 local directory marketplace;harness fallback 行為未驗。對本 repo 改造無直接影響,但 plugin 側配套改動時需留意。
4. **`.claude-team/plugins/data/dev-flow-local` 與 `.claude/plugins/data/dev-flow-local` 兩空目錄用途不明**(runtime reader 明示)。
5. **commit 數矛盾**:history reader 註明「全 repo 僅 13 commits,非 30」——若上游任務描述稱 30 commits,以 13 為準(git log 可覆核)。
6. **行號小幅出入**:templates reader 稱 G3 正本 README.md:262-264 / gate 宣告 :239-243;runtime reader 稱 §7 在行 237。同一區域的邊界差異,不影響結論(§7 = :237-264 一帶),引用時以「README §7」語意錨為準,勿硬編行號。
7. **並行語意行號**:templates reader 寫 README.md:155-161,history reader 寫 :155-160,差一行,無實質矛盾。
8. **memory 記載「plugin repo 無 remote」與 runtime reader 一致**,但 plugin repo 另有 branch codex/dev-flow-methodology-corrections 未合併 master 與否未查證——plugin 側開工前應先確認其 branch 狀態。
