# docs/dev — 改版流程索引

> 本檔追蹤**方法論母版自身**的改版工作(非採用專案的 feature)。三表:
> Active(進行中)/ Shipped(已落地)/ Backlog(待處理,多數來自採用現場回饋)。

## Active

目前無進行中的改版軌。

## Shipped

| 軌 | 內容 | 落地位置 | 日期 |
|---|---|---|---|
| vnext-runtime | Stage 6 執行層並行改造(P1 執行/P2 operational/P3 observability/P4 gauntlet-gates 四軌) | `manifests/p1-execution.md` ~ `p4-gauntlet-gates.md`、`hooks/_exec_impl.py`/`_obs_impl.py`/`_doctor_impl.py` 等;需求正本 `docs/prompts/devflow-vnext-runtime.md`(指標見 `docs/dev/vnext-runtime/README.md`) | 2026-08-02 |
| 4cap-remediation | 四能力補強執行(執行報告 + 兩份輸入文件 + audit fixes,原載於 `notes/`,本次搬入 `docs/dev/4cap-remediation/`) | `docs/dev/4cap-remediation/` | 2026-08-02 |
| single-plugin-merge | 把 Claude Code plugin(hooks/skills/manifests/.claude-plugin)從 `dev-flow-plugin` repo 併入本 repo,repo 名 = marketplace 名 = plugin 名 統一為 `dev-flow`;`methodology/` 子目錄層收攏進 repo root;導覽 html 收進 `guides/` + 根目錄留 redirect | 本次提交(見 `docs/PLUGIN.md`) | 2026-08-13 |

## Backlog

> 來源:`notes/adoption-findings-2026-08-04.md`(母版待修清單,四個採用專案的現場回饋 +
> 對抗式查證)。**該檔本身未動、留原地**,以下僅摘要尚未處理的項目,每列附來源行號。
> C-1/C-2 已標明「隨 A-1 一併處理」,不重複列為獨立項。原 C-3 已於 2026-08-07
> 查證後升級為 A-12(見下)。B-7 經 2026-08-07 查證為原判錯誤,不列入。

| 級 | 一句 | 來源行號 |
|---|---|---|
| A-0 | `git_dirty_paths()` 帶 `--ignored=traditional`,讓 `start` 在四個 repo 全部啟動不了(至今未修) | `notes/adoption-findings-2026-08-04.md:232` |
| A-1 | `docs/dev/README.md` 是母版根 README 的逐字複本,帶進 23 條死引用 + 一個跑不了的 CI 入口(含 C-2 的三處 gauntlet 路徑,隨此併修) | `notes/adoption-findings-2026-08-04.md:29` |
| A-2 | `_gate_impl.py` 的 `s_id_present` 在實務上恆真,ID 鏈在 gate 上完全失效 | `notes/adoption-findings-2026-08-04.md:117` |
| A-3 | `verify_command_match` 字串全等 + `FIELD_RE` 只吃行尾,但模板沒有任何警告 | `notes/adoption-findings-2026-08-04.md:156` |
| A-4 | gate 的 RED/GREEN/verify 三項無條件必檢,純 migration / infra 型 T 無法通過 | `notes/adoption-findings-2026-08-04.md:182` |
| A-5 | Files scope 不含測試路徑會在寫入當下被 hook 殺掉,模板沒提醒 | `notes/adoption-findings-2026-08-04.md:204` |
| A-6 | `Boundaries:` 欄被解析後直接丟棄,不進 task dict | `notes/adoption-findings-2026-08-04.md:387` |
| A-11 | Stage 7 的「禁讀 6-notes Self-Review」沒接到既有的圍欄機制(⏳ 未修) | `notes/adoption-findings-2026-08-04.md:699` |
| A-12 | `dev-setup` 沒跑完整,而沒有任何 Stage 要求跑 doctor(原 C-3,2026-08-07 升級為 A;⏳ 未修) | `notes/adoption-findings-2026-08-04.md:772` |
| B-1 | 母版自己的 `_templates/5-tasks.md` 過不了 `parse_5_tasks` | `notes/adoption-findings-2026-08-04.md:411` |
| B-2 | `dev-setup` 的 diff 摘要沒讓使用者看見細粒度覆蓋,在地客製被靜默沖掉 | `notes/adoption-findings-2026-08-04.md:421` |
| B-3 | lane 判準與 owner 指示衝突時,母版沒說怎麼辦 | `notes/adoption-findings-2026-08-04.md:436` |
| B-4 | `doctor` 對 gauntlet 只做 `--version` 探測,不驗 ROOT 解析 | `notes/adoption-findings-2026-08-04.md:454` |
| B-5 | `Files` 欄系統性低估(數字更正 8→10),模板沒有判準(待裁決) | `notes/adoption-findings-2026-08-04.md:841` |
| B-6 | Diff Budget 的測試檔估法沒把補償控制算進去(比原判更嚴重;待裁決) | `notes/adoption-findings-2026-08-04.md:881` |
