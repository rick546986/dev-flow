---
name: dev-setup
description: dev-flow 專案安裝器 — 打「dev-setup」即自動偵測現況並分流(初裝/升級/修復/健檢)。當使用者說「dev-setup」「初始化 dev-flow」「升級模板」「檢查基建」時啟用。
---

# dev-setup — 專案安裝器 + 基建檢查(plugin 版)

方法包根目錄叫 `DEVFLOW_ROOT`（舊名 `CLAUDE_PLUGIN_ROOT` 當別名，不准刪）。找不到就停，不准猜。

## 主機掛整棵(P0)

**開場先解析 DEVFLOW_ROOT。DEVFLOW_ROOT 解析失敗 → setup 大聲停，不准默默略過，不准只散發 docs/dev/ 就當成功。**

掛的技能至少：`dev-setup` / `dev-talk` / `dev-flow` / `dev-run`。
`dev-flow` 的薄殼必須讓 Agent 看得到 `skills/dev-flow/stage2`–`stage7`（整棵 stage 目錄），不能只指到 `SKILL.md`。
不要把節點 MD 複製進採用專案。正本仍在方法包。

依主機掛整棵（連結，不是單檔）：

- Cursor：`mkdir -p .cursor/skills` 後 `ln -s "${DEVFLOW_ROOT}/skills/<名>" .cursor/skills/<名>`（整棵目錄）。
- Codex：`mkdir -p .agents/skills` 後同樣指方法包 `.agents/skills/<名>`。若已有 `.codex/skills/`，兩處都指同一包。
- Grok：技能庫掛整棵，不是單檔。不要假裝能從產品 repo 自動灌進 Grok 技能庫；把 `DEVFLOW_ROOT` 與本節發現清單回報給人，由人把 `${DEVFLOW_ROOT}/skills/<名>` 整棵掛進 `.grok/skills/<名>`。

`AGENTS.md`：沒有就寫入；已有就只補這一行，不准灌流程：
「這專案用 DevFlow。技能在方法包 skills/。開工讀該技能 SKILL.md，下一跳看 graph.yaml。不要把流程規則貼進本檔。」

乘客模板：節點找的正本是相對 DEVFLOW_ROOT 的 `_templates/<檔>`。
採用專案的 `docs/dev/_templates/` 仍是散發副本，不是節點要找的正本。

## 主機探測(P1)

**dev-setup 先探測主機，再選檢查。** 不要一進場就把 Claude 專用核可套到所有主機。

| 主機 | 怎麼認 | 健檢走哪條 |
|---|---|---|
| Claude | 有 `.claude/`、或人明說在 Claude Code。**優先序最低**：多主機目錄並存時不會只因有 `.claude/` 就判 Claude | 舊的 AskUserQuestion／enabledPlugins／hooks.json 仍可走 |
| Cursor | 有 `.cursor/`、或人明說。優先於 agents/codex／grok／claude | 不要把這三個當唯一核可。改查技能目錄在不在、是不是整棵、`DEVFLOW_ROOT` 對不對 |
| Codex | 有 `.agents/` 或 `.codex/`。優先於 grok／claude | 同上 |
| Grok | 人明說／有 `.grok/`／技能庫掛整棵。優先於 claude | 同上。不要假裝能從產品 repo 自動灌 |

`detect_host` 優先序：`.devflow-host` marker → `.cursor/` → `.agents/`／`.codex/` → `.grok/` → `.claude/`。要硬指定就寫專案根 `.devflow-host`（一行：`claude`／`cursor`／`codex`／`grok`）。表裡「有 `.claude/` → Claude」只在沒有更高優先目錄、也沒有 marker 時成立。

兩種用途不要混：
- **方法包自檢（無參數）**：只在方法包 repo 根跑 `scripts/check-host-adapter.sh --probe`（或無 `--probe` 的全檢）。印 `probe: pack-self-check`，不是採用專案通過。
- **採用專案探測（帶樹）**：與 `scripts/test-host-adapter.sh` 的 `run_check()` 契約相同：
  `DEVFLOW_ROOT=<方法包根> scripts/check-host-adapter.sh --probe <採用專案根>`
  Cursor／Grok／Codex 開工用這一條。不帶專案根會 `probe: 未檢查／缺專案根` 並紅（空樹不得假綠）。

綠的時候印該主機下一句安裝／更新指令(Cursor Refresh 在已匯入 repo 那一列;
Codex 是 marketplace add／plugin add;Grok 沒有 marketplace)。
缺技能樹或 `DEVFLOW_ROOT` 不對會印一句掛載句並紅。四邊正本見 `docs/PLUGIN.md`。
三邊都沒有 Claude PreToolUse。**誰開工誰先跑**該站
`scripts/check-devtalk-graph.sh --action` 或 `scripts/check-devstageN-graph.sh --action`。
**不准為了別的主機改鬆 `--action`。**

`.claude/rules/` 不會被 Cursor／Codex 自動吃。架構不變量用 setup 依主機寫對應指標：
- Cursor：寫 `.cursor/rules/` 一行指標（指向架構不變量，不是流程規則）。
- Codex：仍只准 AGENTS.md 一行。流程規則仍不准進 AGENTS.md。
- Claude：維持 `.claude/rules/`。

架構:skills 與 hooks 隨 plugin 全域生效(單一正本,**專案不需要裝任何 hook**);
本 skill 負責把「文檔面」裝進專案並保持可升級。
散發方式:`dev-flow` 單一 plugin,內含 `dev-talk` skill 與方法論(repo 根目錄即方法論母版)
(repo `rick546986/dev-flow`,`marketplace.json` 一個 entry:`./`)。
安裝 = `/plugin marketplace add rick546986/dev-flow` 後
`/plugin install dev-flow@dev-flow`(裝一次,dev-talk 隨附,不再是獨立 plugin);
更新 = `/plugin marketplace update dev-flow` + `/plugin update dev-flow`。
Cursor／Codex／Grok 各自怎麼裝見 `docs/PLUGIN.md`（不要抄 Claude 的 `/plugin`）。
**實際 plugin root = `~/.claude/plugins/cache/dev-flow/dev-flow/<version>/`**
——會隨版本改變,腳本與檢查一律用 `${DEVFLOW_ROOT}` 或由自身位置推導,禁寫死。
說明書:[dev-setup 安裝紀錄](https://rick546986.github.io/dev-flow/guides/dev-setup-record.html)。本機路徑 `${DEVFLOW_ROOT}/guides/dev-setup-record.html`。

## 開場第一動:偵測 → 分流(使用者只打「dev-setup」時的預設行為)

不需要參數。依序偵測,判定狀態後**直接執行對應動作**(破壞性步驟仍先摘要+徵得同意):

| 偵測 | 狀態 | 動作 |
|---|---|---|
| 無 `docs/dev/` | **fresh** | 跑 install(見下);完成後跑 check 回報 |
| 有 `docs/dev/`,但 README/模板與方法論母版 `${DEVFLOW_ROOT}/` 有差異 | **stale** | 跑 upgrade(先列 diff 摘要徵同意)→ check |
| 有 `docs/dev/` 且與母版一致 | **current** | 只跑 check |
| check 抓到異常(缺件/殘留/陳年旗標/盲掃命中) | **broken** | 列異常+修法,**徵得同意後**跑 fix |

回報格式固定:①判定狀態一句 ②做了什麼(逐條)③check 結果表 ④還需要你決定的事(可空)。
使用者若明講子命令(`dev-setup check` / `upgrade` / `install` / `refresh` / `fix` /
`uninstall`),照該子命令走,跳過偵測。`refresh` = 重掃並比對 rules(見下),
自動分流**不會**主動跑它(重掃有成本,且結果需要人裁決)。

## install(fresh)

> **前提**:hooks 需要 python3(解析順序 `DEVFLOW_PYTHON` → `/usr/bin/python3` → PATH;
> **編譯下限 3.9**;詳見母版 README「環境需求」)——Windows Git Bash 環境安裝前先確認
> `python3` 找得到(或設 `DEVFLOW_PYTHON`),否則守衛會**靜默跳過**:不是壞掉,但等於
> 沒有保護,而「守衛沉睡」與「守衛在擋」從外面看長得一樣(G1 同型風險)。
> gate-twin／產圖另要 `markdown-it-py==4.0.0`,該套件要 **Python 3.12+**。
> macOS `/usr/bin/python3` 常是 3.9,裝不出 4.x。用**專案 venv**或設
> `DEVFLOW_PYTHON` 指向 3.12+,**不要覆寫** Apple／系統 Python。
> doctor 的 `printer-python` 項會查;不夠就停,不准默默留 markdown-it-py 3.x。

0. **解析 DEVFLOW_ROOT + 掛整棵(P0，先於散發)**：先完成本檔「主機掛整棵」節，並先探測主機（見「主機探測」）。
   `DEVFLOW_ROOT` 解析失敗 → setup 大聲停，不准進入步 1。
   不准只散發 docs/dev/ 就當成功。不要把節點 MD 複製進採用專案。
   **1:1 散發列正本**:`${DEVFLOW_ROOT}/docs/dev/ship-manifest.json`
   (每列 `source` / `destination` / `mode`)。install / check / baseline / upgrade
   的 1:1 檔都讀這一份,不得另抄清單,也**不得掃 `docs/dev/tools/` 當 expected set**
   (正副本同刪 = 第 4 型假綠)。對每一列:
   `cp "${DEVFLOW_ROOT}/<source>" <destination>` 後 `chmod <mode>`。
   `devflow-contract.json` 的 destination 是 `docs/dev/devflow-contract.json`,
   **不住在 `docs/dev/tools/`**,不得把它塞進 tools/ 清單再刪掉第 10 項獨立比對。
   README 剝除與 `_templates/` 整目錄複製不是 1:1 mode 列,仍按本步既有手續。
1. `docs/dev/` 建立:cp 方法論 `${DEVFLOW_ROOT}/README.md` 後**剝除 master-only 區塊**
   再落地為 `docs/dev/README.md`(不得直接 cp 未剝除版 —— 母版 README 內
   `<!-- devflow:master-only:start -->` / `<!-- devflow:master-only:end -->` 之間是純母版
   repo 導覽,對散發專案是死引用):
   ```
   sed -n '/<!-- devflow:master-only:start -->/,/<!-- devflow:master-only:end -->/!p' \
     "${DEVFLOW_ROOT}/README.md" | tr -d '\r' > docs/dev/README.md
   ```
   **行尾一律正規化成 LF 落地(結尾那道 `tr -d '\r'`,不得省略)**:MSYS/Git Bash 的
   GNU sed 以文字模式讀檔、輸出時會把 CR 拿掉,平台不同就寫出不同行尾 —— 讓平台決定
   寫出什麼,等於在安裝當下就種下與比對端對不起來的不一致(upgrade/check 兩處比對
   同步一律兩側 `tr -d '\r'` 後再比,見下方 upgrade 段與 check 第 6 項)。
   `_templates/` → `docs/dev/_templates/`、**`devflow-contract.json` →
   `docs/dev/devflow-contract.json`**(版本握手契約;doctor 無 `--contract`/
   `$DEVFLOW_CONTRACT` 明示時在此找,缺件必 fail-closed);從模板建 `STATUS.md`。
   **不再建 repo root `CONTEXT.md`**(v3.10.0 起):業務語言的正本改為
   `.dev-flow/knowledge/domain/`,由步 1b 建置;既有專案的 `CONTEXT.md` 由
   步 1b 的遷移處理,**不刪、不重新產生**。
   **基準快照(此步只宣告,不落地)**:清單 = `docs/dev/README.md`(已剝除版)、
   `_templates/*`、以及 `${DEVFLOW_ROOT}/docs/dev/ship-manifest.json` **每一列的
   destination**(含 `devflow-contract.json` 與整個 `docs/dev/tools/`)。
   `docs/dev/tools/` 按目錄整包存,不逐檔列。**實際落地在步 8**(工具還沒散發完,
   拍早了 upgrade 會誤判)。
   `mkdir -p docs/adr`、`docs/dev/HISTORY.md` 不存在則從 `_templates/HISTORY.md`
   建;再 `mkdir -p docs/dev/tools`(第一支工具 cp 之前);然後
   `${DEVFLOW_ROOT}/scripts/history-append.sh` → `docs/dev/tools/history-append.sh`
   並 `chmod +x`(HISTORY.md 唯一寫入口;`history-guard` 擋直接 Edit/Write)。
   散發後跑 `bash docs/dev/tools/history-append.sh --print-root` → 專案根且
   exit 0(git toplevel,與散發位置無關);不符即 broken。doctor 項
   `history-append-root`。
   **gate twin**:`${DEVFLOW_ROOT}/scripts/build-gate-twin.py` 與
   `devflow_twin_ui.py` → `docs/dev/tools/`(同目錄)。stage:
   `2-decision | 4-spec | 7-review | 5-tasks`。
   `docs/dev/tools/build-gate-twin.py <專案根> <slug> <stage>`。
   相依:`markdown-it-py==4.0.0`(缺或版本不符 → exit 2,不降級)。
   缺相依:`pip install 'markdown-it-py==4.0.0'`(不代裝)。
   驗證:①無參數 → 含「用法」且 exit 2;②
   `python3 -c "import markdown_it, sys; sys.exit(0 if markdown_it.__version__ == '4.0.0' else 3)"`
   → exit 0。
   **pages**:`${DEVFLOW_ROOT}/scripts/publish-pages.sh` →
   `docs/dev/tools/publish-pages.sh` 並 `chmod 755`。無 `.gitlab-ci.yml` /
   `.gitea/workflows/pages.yml` 才抄,已有不覆蓋。本機
   `python3 scripts/devflow_gate.py serve --root .`。驗證:`--help`/`-h`/`help`/未知參數 →
   用法且 exit 2(量測勿經 pipe);無參數 = 以 git toplevel 當預設根並實際組
   `public/`(exit 0),健檢不得用無參數呼叫。
1b. **Agent Memory 建置**(v3.10.0 起;`dev-setup` 是唯一入口,**不得新增
   `dev-flow init` 之類的第二個安裝器**)。跑:
   ```
   python3 "${DEVFLOW_ROOT}/memory/dev-memory.py" --path <專案根> setup
   ```
   它做九件事,全部冪等(輸出是 JSON,直接鋪進回報表):
   ①找 repository root;②`.dev-flow/project.yaml` 不存在 → 建 `project_id`
   (ULID,**path-independent**:不含任何檔案路徑成分、不依賴 GitHub remote)
   + 最低限度 `.dev-flow/` 結構(lazy-create,不鋪空目錄);③已存在 →
   **reuse 既有 `project_id`**;④註冊本機 workspace(local path / OS / branch /
   HEAD / worktree —— 這些是**本機 metadata**,住本機 SQLite,不進 Git);
   ⑤initialize/migrate 本機 DB;⑥從 `.dev-flow/` 重建本機索引;⑦重建 FTS;
   ⑧需要時 re-index embeddings(換 model 會被偵測出來,不會靜默失效);
   ⑨掛既有 legacy 資料的 `project_path → project_id` 對照。
   **重複執行不得產生新的 `project_id`** —— 這條有測試釘住
   (`memory/tests/test_setup_legacy.py`)。
   `.dev-flow/` **要 commit 進 Git**(它是可攜的長期記憶);
   `.devflow/`(無連字號)是本機執行期暫存,已在 `.gitignore`,兩者不要混。
   **既有專案的 legacy 遷移**(有 repo root `CONTEXT.md` 時):先跑
   `dev-memory.py migrate-legacy`(預設 dry-run,只回報會做什麼),把詞條數與
   目標分類回報給使用者;使用者同意後跑 `--apply --promote`,詞條會以
   **CANDIDATE + documentation authority** 落地(不標成已確認 —— 沒有人在遷移
   那一刻重新確認過那些詞條)。遷移完成且使用者確認後才可刪 `CONTEXT.md`,
   **dev-setup 不自動刪別人的檔**。
   `docs/dev/HISTORY.md` 只被**索引**進本機記憶(查得到「之前發生過什麼」),
   不複製進 `.dev-flow/events/` —— 同一份內容兩個 durable 正本必然漂移。
2. `.claude/rules/arch-invariants.md`:從 `_templates/arch-invariants.md` 建檔,**並自動產草稿**
   (不留空殼):
   - 先收割既有素材:使用者指名的外部 workflow artifacts 中的架構指引
     (架構不變量/技術慣例類搬入,流程類丟棄)、專案 `CLAUDE.md` 的技術規則段、
     `docs/specs/` 裡屬慣例而非行為的敘述。未經使用者指名的外部目錄不掃描;
     原 artifacts 不移動、不覆蓋、不刪除。
   - 再派 **執行層 subagent 掃 codebase 產候選**(Claude 對照 sonnet;派工三件套;不逐檔讀全庫,採樣:
     入口/資料層/錯誤處理/測試設定 + grep 反覆出現的 pattern)。要它回報格式:
     `分類 | 規則一句 | 證據(檔:行)| 信心(高/中/低)`。
   - 落檔時**每條標 `【待確認】`**,且**每一條都要經使用者明確裁決**(採/砍/改),
     不得一句「其餘都 OK」帶過 —— 這檔錯一條會長期誤導每個 session,值得逐條看。
     問法:用 AskUserQuestion **按 `##` 分節、每題 ≤4 條 multiSelect**(勾選 = 收錄,
     沒勾 = 砍),節與節之間停;使用者明說「這節全收/全砍」可整節裁決。
     **僅 Claude 走 AskUserQuestion**。其他主機見「主機探測」。
     裁決後拿掉標記;**未經裁決的條目一律保留標記**(有標記 = 不可當事實引用),
     check 第 7 項會計數殘留並提醒回頭補裁。
   - **去重(避免雙正本)**:收割來源若是專案 `CLAUDE.md`,把該段落**改成一行指標**
     (如「架構不變量見 `.claude/rules/arch-invariants.md`」),不要兩處都留全文 ——
     否則改一條規則要同步兩處,漂移是遲早的事。
   - 判準提醒:只收「錯了會出事、但看 repo 不會馬上知道」的;看目錄就懂的結構描述、
     系統現況行為(→`docs/specs/`)、流程規則(→ 盲禁令)一律不收。
   - **預設單檔常駐**(無 `paths` frontmatter = 每 session 自動載入)。只有在
     rules 超過 ~100 行、或前後端等多技術棧同 repo 時,才建議拆多檔 + `paths:`
     frontmatter 做 path-scoped 按需載入(判準見模板頂註);一開始就分是過度工程。
3. `.gitignore` 加 `.devflow/`。
4. 文檔歸位(散檔 git mv 進 specs/dev/adr,引用 sed 歸零)照 README §1。
5. 未識別的既有外部 workflow artifacts 與目錄**一律保留**:不移動、
   不覆蓋、不刪除。dev-setup 只安裝 dev-flow 的文檔面,不轉換也不接管外部 workflow。
6. **evidence gauntlet 散發**:`mkdir -p docs/dev/tools` 後 cp 方法論
   `${DEVFLOW_ROOT}/scripts/devflow-evidence-gauntlet.sh` →
   `docs/dev/tools/devflow-evidence-gauntlet.sh` 並 `chmod +x`(Stage 7 Final Fresh
   Run 的文檔層機械檢查 E1–E13;契約正本 = 方法論 `notes/design/evidence-gauntlet.md`)。
   散發後**可執行驗證**(兩道都跑,任一不符即列 broken,不得靜默):
   ①無參數跑 → 預期印 usage 且 exit 2;
   ②`bash docs/dev/tools/devflow-evidence-gauntlet.sh ${DEVFLOW_ROOT}/scripts/fixtures/evidence-gauntlet/good-evidence.md`
   → 預期 exit 0(checks 數以輸出為準)。
7. **整合回歸工具散發**:cp 方法論
   `${DEVFLOW_ROOT}/scripts/devflow-integration-regression.sh` →
   `docs/dev/tools/devflow-integration-regression.sh` 並 `chmod 755`(Stage 7 Exit
   Checklist「(條件式)整合回歸」的計算工具:只算與只判、絕不動樹;分岔點用
   6-notes 步 0 持久化的錨點 FORK_INTEGRATION_SHA,缺錨點 fail-closed 直接擋,
   不退回用 merge-base 猜)。散發後**可執行驗證**(任一不符即列 broken,不得靜默):
   ①無參數跑 → 預期印用法且 exit 2;
   ②正副本**可執行位元一致(兩邊都 755)** —— 散發時掉執行權限實際發生過;
   母版側由 `check-integration-regression-guard.sh` 的 parity 對帳釘住同一件事。
8. **基準快照落地(收尾步;只有全部驗證成功才做)**:確認步 1、6、7 的每一項
   散發/權限/diff/用法驗證**全部成功**之後,才把步 1 宣告的 ——
   `docs/dev/README.md`(已剝除版)、`_templates/*`、以及
   `docs/dev/ship-manifest.json` **每一列的 destination**(含
   `devflow-contract.json` 與**整個 `docs/dev/tools/`**) —— 快照到
   `docs/dev/.devflow-baseline/`。
   放在最後的理由:`docs/dev/tools/` 要到步 6、7 才有內容,拍早了會讓 upgrade 的
   三方比對把官方散發的工具誤判成本地客製。**任一驗證失敗 → 不建立新 baseline**;
   upgrade 情境下舊 baseline 必須原封不動 —— 不能先污染快照再報錯。
   落地方式:先在暫存目錄把完整 baseline 新樹組好、核對成功後才整棵替換
   `docs/dev/.devflow-baseline/`(**乾淨替換,不准 overlay** —— overlay 會在
   上游移除工具時於 baseline 留下幽靈檔)。

## upgrade(stale)

- 只覆蓋 `docs/dev/README.md`、`docs/dev/_templates/`、以及
  `${DEVFLOW_ROOT}/docs/dev/ship-manifest.json` **每一列的 destination**
  (`docs/dev/tools/` 仍**整個 tools/ 目錄**整包覆蓋,以便清掉上游已移除的檔;
  覆蓋後重跑 install 步 6 **與步 7** 的可執行驗證 ——
  步 6 只驗 gauntlet 一支,整合回歸工具的可執行位元驗證在步 7,兩道都要;各列
  `mode` 以正本為準)與
  `docs/dev/devflow-contract.json`(版本握手契約,正本列已在 ship-manifest;
  覆蓋後重跑 check 第 10 項,**不得**因它進了正本就刪掉這項獨立比對)——
  先 diff 摘要給使用者過目。
- **出廠殘件刪除**(覆蓋受管檔與換 baseline **之前**):跑
  `${DEVFLOW_ROOT}/scripts/devflow-upgrade-leftovers.sh --root <專案根> --pack ${DEVFLOW_ROOT} --apply`
  刪掉目前 pack **不再出貨**、但採用樹還留著的受管殘件(例:`docs/dev/_templates/CONTEXT.md`
  與 `.devflow-baseline/_templates/CONTEXT.md`)。**不准刪**專案根 `CONTEXT.md`,
  也不准刪採用專案正在用的 `docs/dev/CONTEXT.md`。沒 baseline 時只刪已知退役
  模板名;有 baseline 時另刪「在舊 baseline、不在新 pack」的 `_templates/` 檔。
  **先刪殘件再換 baseline**,否則退役檔會被看成本地客製。預設 dry-run;upgrade
  帶 `--apply`。這一步不是每次 upgrade 重寫 HISTORY,也不是掃整個專案亂刪。
- **diff 摘要必須分兩類,不得只給一份「新舊不同」清單**(否則使用者按下「全部
  升級」時看不到自己的在地修改要被沖掉):
  ①**母版改寫**(上游更新):本地內容 = 上次 install/upgrade 留下的原樣,使用者
  沒碰過 —— 可隨 upgrade 直接覆蓋,列摘要即可。
  ②**本地客製將被還原**(受管檔在地內容 ≠ 上游舊版 = 使用者自己改過):
  **逐檔單獨列出「本地現況」與「即將覆蓋成的新內容」,徵得使用者明確同意**
  才可覆蓋該檔,不得併入①的摘要一筆帶過。
  **判別法(三方比對)**:上游舊 blob(見下)、上游新 blob(這次
  `${DEVFLOW_ROOT}/README.md` 剝除 master-only 區塊後的內容,或
  `_templates/`/gauntlet 腳本/`devflow-contract.json` 原始內容)、本地現況
  (`docs/dev/` 對應檔案現況)——**本地現況 ≠ 上游舊 blob ⇒ 判定客製**,即使本地
  現況恰好與上游新 blob 相同也要列出(可註記「與新版一致,覆蓋無影響」,
  但仍需在②分類下出現,不得靜默歸進①)。
  **上游舊 blob 的來源**:每次 install/upgrade 成功覆蓋後,快照的內容必須來自
  **這次覆蓋下去的上游新內容**(upstream-new 正本:`${DEVFLOW_ROOT}` 側
  已剝除 master-only 區塊的 README、`_templates/*`、`devflow-contract.json`,
  加上這次散發的整套工具 —— 對應 `docs/dev/tools/` 按目錄整包,不逐檔列,
  逐檔列的話下一支新工具又會漏),另存一份到 `docs/dev/.devflow-baseline/`。
  **不准把可能已被本地改過的 `docs/dev/` 現況直接抄成 baseline** —— 抄現況的話,
  本地客製會被記成「上游舊」,下次三方比對就分不出誰改的。快照一律先在暫存目錄
  用本輪 upstream-new 正本組好完整新樹,核對成功後才整棵替換舊 baseline(乾淨
  替換不 overlay,上游移除工具時才不會留幽靈檔);使用者拒絕覆蓋本地客製時,
  只影響 `docs/dev/` 現況,**不改變 baseline 的來源**(baseline 仍取 upstream-new)。
  下次 upgrade 讀這份快照當「上游舊」,不得拿本地現況去猜。首次 install 無快照
  可比,全部視為①;install 收尾步也要建立這份快照(見 install 步 8)。
  **過渡態**:`docs/dev/.devflow-baseline/` 不存在但 `docs/dev/` 已存在(= 本規則
  生效之前裝的既有安裝,四個採用專案的真實現況)⇒ 不得套用「無快照=全部視為①」
  的首次 install 分支 —— 本次 upgrade **全部受管檔視為②本地客製,逐檔徵同意**,
  完成後才建立快照,下次 upgrade 起才回到正常的三方比對。
- **check 第 6 項的 diff 比對基準同步套用剝除規則**:比對母版時一律先對
  `${DEVFLOW_ROOT}/README.md` 跑與 install 步 1 相同的 sed 剝除管線再 diff,
  且**兩側都要過同一道行尾正規化**,即
  `diff <(sed -n '/<!-- devflow:master-only:start -->/,/<!-- devflow:master-only:end -->/!p' "${DEVFLOW_ROOT}/README.md" | tr -d '\r') <(tr -d '\r' < docs/dev/README.md)`
  ——不得直接對未剝除的母版原檔跑 diff,否則 master-only 區塊本身的存在
  就會被判定成「每次都 stale」的假漂移;**也不得只對母版側跑管線、採用專案側直接拿原檔比**,
  否則 Windows 上母版側被 sed 剝掉 CR、採用專案側是 CRLF,每一行都差一個 CR、
  整份被判全不同 —— check 第 6 項恆紅、每次健檢都走 upgrade 覆蓋一次,
  把「開工前工作樹要乾淨」的前提直接弄壞。
- **產圖 Python 地板**:upgrade／doctor 必須查 `printer-python`(3.12+ 專案 venv
  或 `DEVFLOW_PYTHON`)。系統 python 是 3.9 時不准默默 `pip install` 出
  markdown-it-py 3.x,也**不要覆寫** Apple／系統 Python。
- **HISTORY 出廠種子清理是選配**:`docs/dev/tools/history-append.sh --action factory-seed-cleanup`
  只刪可見的出廠四行。認不出種子 vs 真紀錄 → fail-closed。**不准每次 upgrade 自動跑**。
- **絕不動 `docs/dev/<slug>/` 已產出的 feature 檔**與 STATUS/CONTEXT/rules。

## refresh(使用者說「重掃 rules」「rules 過期了」「更新架構規則」)

codebase 會演進,rules 會腐化(規則指的檔案沒了、行為變了、新慣例沒收錄)。
本模式**只比對與建議,不自動覆蓋**:

1. 重掃 codebase 產候選(同 install 步驟 2 的採樣方法)。
2. 與現有 `.claude/rules/*.md` 逐條三向比對,輸出三張表:
   - **新候選**:rules 沒有的慣例/坑 → 標 `【待確認】` 附證據,問使用者要不要收。
   - **疑似過期**:既有條目的證據**失效**(引用的檔/行不存在、內容已變、grep 命中數
     與描述不符)→ 附「當初說什麼 vs 現在是什麼」,問使用者要改、刪、還是保留。
   - **仍成立**:證據複驗過的,不動也不列(只回報數量)。
3. 使用者裁決後才落檔;裁決方式同 install 步驟 2(AskUserQuestion 分節逐條,
   未裁決者保留【待確認】)。**禁止整檔重產** —— 核可過的條目是人工判斷的成果,
   重掃不得沖掉。
4. 同場加映:掃 `CLAUDE.md` 與 rules 是否又出現重複段落(雙正本),有則提議把
   CLAUDE.md 那段改回指標。

⚠️ **不要用 `/init` 來「更新」已導入的專案**:`/init` 會覆蓋整份 CLAUDE.md,
沖掉收斂過的指標句與專案特有段落,且它重新寫的架構描述會與 rules 形成雙正本。
真要重掃 CLAUDE.md:先備份 → `/init` 產出後**人工挑**要保留的段落 → 再跑本 refresh 去重。

## check(每種分流結尾都跑)

逐項驗證列表回報,異常附建議、不自動修(fresh/stale 流程末尾自動跑;broken 才問要不要 fix):
**先探測主機，再選檢查**（見「主機探測」）。Claude：下列 1–3 與 AskUserQuestion 核可仍可走。
其他主機：不要把這三個當唯一核可；改查技能目錄在不在、是不是整棵、DEVFLOW_ROOT 對不對
（第 15／16 項）。
1. **三份 JSON**(僅 Claude；其他主機不要把本項當唯一核可) jq 過:`<root>/.claude-plugin/plugin.json`(dev-flow;dev-talk 併入後
   不再有獨立 plugin.json)、`<root>/.claude-plugin/marketplace.json`(**一份、一 entry**:
   `./`)、**`<root>/hooks/hooks.json`**。hooks.json 壞掉 → 八條掛載全靜默失效,而自測
   照樣全綠 → 必驗。另比對 plugin.json 的 `version` 與 installed_plugins.json 記錄的
   版本一致(不一致 = 有人改了檔沒 bump,或裝的不是最新)。
2. 兩帳號 settings `enabledPlugins`(僅 Claude；其他主機不要把本項當唯一核可):`dev-flow@dev-flow` 為 true(dev-talk 已
   併入,不再是獨立 enabledPlugins 項;舊值 `@local` 或 `@dev-flow-plugin` =
   尚未遷到現行 marketplace 名稱散發,應改;`known_marketplaces.json` 的 `dev-flow`
   須為 github source)。
3. **hooks/ 10 支可執行**:devtalk-guard、devflow-guard、**devflow-prebash**、
   devflow-postbash、devflow-exec、selftest、**history-guard**、**devflow-dispatch-guard**、
   **devflow-report-guard**、**devflow-plainspeak**。
   **hooks.json 應有 8 條掛載**:
   PreToolUse `Edit|Write|Read`→devflow-guard、PreToolUse `Edit|Write`→history-guard、
   PreToolUse `Bash`→devflow-prebash、PreToolUse `Task|Agent`→devflow-dispatch-guard、
   PostToolUse `Edit|Write`→devtalk-guard、PostToolUse `Edit|Write`→devflow-report-guard、
   PostToolUse `Bash`→devflow-postbash、UserPromptSubmit `*`→devflow-plainspeak。
   (本項的支數/掛載數/逐條列舉由 `scripts/check-hooks-accounting.sh` 對
   `hooks/hooks.json` 對帳 —— 第 7 型「不對稱記帳」教訓:曾在 hooks 長到 6 條掛載
   後,本清單靜默停在 5 條,採用專案照本清單健檢會把真實存在的 hook 判成多餘。)
   (實作為 shell 薄殼 + `devflow-lib.py` 與 `_*_impl.py`,改動時兩層都要在。)
4. **功能自測(可重跑)**:①執行守衛跑 `hooks/selftest.sh`(自建 temp 假 repo 後自清;
   **案數以腳本輸出為準,不在本檔寫死** —— 曾因寫死「33 案」漂移至實際 80)→ 需全過;
   ②devtalk-guard pipe 三案(非 dev-talk 放行 / 現行 SKILL 放行 /
   洩漏假檔 exit 2)。⚠️ **自測只證 script 邏輯,不證掛載** —— 掛載靠第 1、3 項。
5. dev-talk 盲掃:掃**整個 `skills/dev-talk/` 目錄**(含 SKILL.md frontmatter 的
   description —— 使用者在 skill 清單直接看到,洩漏槓桿最高;dev-talk 併入單一
   plugin 後不再有自己的 plugin.json/marketplace entry,description 洩漏風險全落在
   這份 SKILL.md 本身):
   `grep -rniE "<字詞表見 devtalk-guard.sh>" "${DEVFLOW_ROOT}/skills/dev-talk/"` 零命中
   (`CLAUDE_PLUGIN_ROOT` 未設時用 dev-flow plugin root 的 `skills/dev-talk/` 子目錄;
   **不寫死舊版拆分 plugin 時代 dev-talk 專屬的 local marketplace 路徑** —— 併入單一
   plugin 後該路徑與獨立 marketplace entry 皆不存在)。
6. 專案面(在專案內跑時):docs/dev/README 與模板版本 vs 母版 diff——**README 比對
   基準是剝除 master-only 區塊後的母版內容,不是母版原檔**(比對管線同 upgrade
   段:`diff <(sed -n '/<!-- devflow:master-only:start -->/,/<!-- devflow:master-only:end -->/!p' "${DEVFLOW_ROOT}/README.md" | tr -d '\r') <(tr -d '\r' < docs/dev/README.md)`;
   對原檔直接 diff 會把 master-only 區塊本身的存在誤判成假 stale;兩側的 `tr -d '\r'`
   同樣不得省略 —— 只有母版側過管線的話,Windows 上 sed 會吃掉 CR 而採用專案側是 CRLF,
   內容逐字相同也會判全不同、恆報 stale);`.devflow/exec.json`
   陳年旗標(>24h 警告);舊 skills 目錄殘留(`~/.claude*/skills/dev-{talk,flow,setup}`)。
   模板檢查說明:4-spec 模板含 Verification Profile 節後(VNext),lane 依規則填 ——
   Full 完整 Profile、Fast 最小 Profile(`Risk: normal`/`Verify:`/`Negative
   Constraints:`/`Advanced verification excluded:`/`Exclusion reason:`);
   `lane: fast` + `Risk: high` 的**拒絕屬 runtime start 檢查(devflow-exec)與 G2
   gate**,本項 diff 只驗模板未漂移,不代驗個別 feature 填寫內容。
7. **rules 未核可殘留**(在專案內跑時):`grep -c '【待確認】' .claude/rules/*.md`
   非 0 → 回報「N 條未核可,該檔每 session 自動注入,未核可條目不得當事實引用」,
   並提議**按 `##` 分節批次核可**(逐條問不現實)。
8. **gate 摘要 vs §7 正本一致性**(手動跑,非掛載 hook,不計入第 3 項可執行清單):
   跑 `hooks/gate-consistency.sh` —— 從母版 README §7(G1/G2/G3 唯一正本)動態抽取
   每個 gate 的關鍵 token,比對 plugin `dev-flow` SKILL.md 階段表、README §3 表、
   三份模板(2-decision/4-spec/7-review)頂註送審步是否都含該 token(同義詞如
   OC/Owner Calls、DD/Drafting Decisions、回歸綠/既有全綠,靠小型映射表正規化)。
   **不把 gate 條件字串寫死在 script 裡**——寫死等於讓 script 自己變成第四份會漂移
   的複本,必須每次從正本動態重新抽取才驗得住漂移。exit 0 = 一致;非 0 = 有漂移
   或抽取失敗(anchor 不見,需人工檢查)。只做 token 級比對,不驗語序/否定式。
   G2/G3 新錨落入 §7 後動態抽取自動涵蓋。
9. **evidence gauntlet 散發檢查**(在專案內跑時):
   `docs/dev/tools/devflow-evidence-gauntlet.sh` ①存在且可執行(缺件 = broken,
   走 install 步 6 補);②與方法論 `${DEVFLOW_ROOT}/scripts/devflow-evidence-gauntlet.sh`
   diff 無差異(有差異 = stale,走 upgrade 覆蓋 —— 專案側不得自改此腳本,要改改方法論);
   ③無參數跑 exit 2(usage);④對方法論 fixture `good-evidence.md` 跑 exit 0
   (同 install 步 6 的兩道可執行驗證)。任一不符 → broken,列異常+修法。
   ⚠️ 本項與第 11/12 項只是**逐支的行為面**驗證,**不是散發集合的全集** ——
   全集由第 13 項從 `docs/dev/ship-manifest.json` 動態取,別拿這三項的名字當清單。
10. **版本握手**(在專案內跑時):①`docs/dev/devflow-contract.json` 存在
    (缺件 = broken,走 install 步 1 補 —— doctor 無明示指定時就在這裡找契約,
    缺件必 fail-closed)且與方法論 `${DEVFLOW_ROOT}/devflow-contract.json` diff
    無差異(有差異 = stale,走 upgrade 覆蓋);②在專案內跑
    `hooks/devflow-exec.sh doctor` 可執行並看 verdict。doctor 報 `INCOMPATIBLE`
    時的指引:fail-closed 是刻意行為,不得繞過或改綠 —— 修復它列出的不相容項、
    或升級 runtime/方法論後重跑,不靜默退回舊行為。
11. **gate twin 產生器散發檢查**(在專案內跑時):`docs/dev/tools/build-gate-twin.py`
    與 `docs/dev/tools/devflow_twin_ui.py` ①兩支皆存在(缺件 = broken,走 install
    步 1 補),且 `build-gate-twin.py` 可執行(前者為 CLI 入口;`devflow_twin_ui.py`
    僅供 import,不要求可執行位元);②與方法論 `${DEVFLOW_ROOT}/scripts/build-gate-twin.py`、
    `${DEVFLOW_ROOT}/scripts/devflow_twin_ui.py` diff 逐字無差異(有差異 = stale,
    走 upgrade 覆蓋 —— 專案側不得自改這兩支腳本,要改改方法論);③無參數跑
    `python3 docs/dev/tools/build-gate-twin.py` → 訊息含「用法」且 exit 2;④相依探測:
    `python3 -c "import markdown_it, sys; sys.exit(0 if markdown_it.__version__ == '4.0.0' else 3)"`
    → exit 0(非 0 時把 `pip install 'markdown-it-py==4.0.0'` 回報給使用者,不代裝)。
    任一不符 → broken,列異常+修法。
12. **整合回歸工具散發檢查**(在專案內跑時):
    `docs/dev/tools/devflow-integration-regression.sh` ①存在且**可執行,且正副本
    可執行位元一致(兩邊都 755)**(缺件 = broken,走 install 步 7 補;掉執行權限
    實際發生過);②與方法論 `${DEVFLOW_ROOT}/scripts/devflow-integration-regression.sh`
    diff 無差異(有差異 = stale,走 upgrade 覆蓋 —— 專案側不得自改此腳本,
    要改改方法論);③無參數跑 → 訊息含「用法」且 exit 2。
    任一不符 → broken,列異常+修法。
13. **散發副本 parity 總表**(在專案內跑時)——**比對集合一律取自
    `${DEVFLOW_ROOT}/docs/dev/ship-manifest.json` destination 落在
    `docs/dev/tools/` 的列,不得自己枚舉,也不得照第 9/11/12 項那幾支硬列的
    名字當全集,更不得掃 docs/dev/tools/ 當 expected set**:
    讀正本每一列,對其中**每一支**驗:①專案側 destination 存在;②可執行位元與
    清單 `mode` 一致、且與 source 一致;③與 `${DEVFLOW_ROOT}/<source>` diff
    逐字無差異(有差異 = stale,走 upgrade 覆蓋 —— 專案側不得自改任何一支,
    要改改方法論)。任一不符 → broken。
    掃 `docs/dev/tools/` 當 expected set = 第 4 型假綠(正副本同刪全綠)。
    `history-append.sh` 是 HISTORY 唯一寫入口,本項必須涵蓋。
    行為面:`bash docs/dev/tools/history-append.sh` 無參數 → 含「拒絕:缺
    `--slug`」且 exit 2;`--print-root` 印專案根且 exit 0。
    **`devflow-contract.json` 不住在 `docs/dev/tools/`,第 10 項單獨驗**。
14. **Agent Memory 健檢**(在專案內跑時):跑
    `python3 "${DEVFLOW_ROOT}/memory/dev-memory.py" --path <專案根> doctor`
    並照它的 verdict 分流(`PASS` / `WARN` / `FAIL`;exit 1 = FAIL)。它逐項回報:
    `project-identity`(`.dev-flow/project.yaml` 在不在、`project_id` 合不合法 ——
    缺件 = broken,走 install 步 1b 補)、`local-schema`(本機 DB schema 版本)、
    `capability/fts5` 與 `capability/fts5_trigram`(不可用 = WARN:retrieval 少一個
    通道,**不影響正確性**,不要當成壞掉)、`embedding-version`(與當前 signature
    不符的筆數 → 跑 `dev-memory.py reindex`)、`durable-relative-paths`
    (**`.dev-flow/` 內出現絕對路徑 = FAIL**,那份記憶換一台機器就對不上,要人工修)、
    `current-truth-overlay`(本機有幾筆事實處於 STALE/CONFLICT —— 這是**預期行為**
    不是故障:依賴檔在本機改過,查詢時會要求重新確認)。
    另外跑 `dev-memory.py eval` 可用內建的小型確定性 dataset 驗檢索沒退步
    (非必跑;它不需要大型 benchmark,exit 1 = 有指標掉到門檻以下)。
15. **主機掛整棵**(在專案內跑時):對照本檔「主機掛整棵」。`DEVFLOW_ROOT` 仍解析得到。
    `AGENTS.md` 只有一行指標 +「不要把流程規則貼進本檔」。
    只散發 docs/dev/、技能連結只有 SKILL.md → broken。
16. **主機探測與 --action**:對照本檔「主機探測」。先探測主機再選 1–3。
    採用專案探測（帶樹）開工跑
    `DEVFLOW_ROOT=<方法包根> scripts/check-host-adapter.sh --probe <專案根>`。
    方法包自檢才可無參數。
    不准為了別的主機改鬆 `--action`。

## fix / uninstall

- fix:缺件按 install/upgrade 對應步驟補;陳年旗標 → 問使用者後 `devflow-exec.sh stop`。
- uninstall:兩帳號 enabledPlugins 設 false(hooks 隨停);專案文檔面留給使用者決定。

## 注意

- 改 plugin 後執行中 session 要 `/reload-plugins`。
- devtalk-guard = 內容硬檢;devflow 守衛 = 旗標期硬擋+偵測網;讀寫白名單其餘部分
  仍是 prompt 圍欄 —— 界線見 record html「誠實聲明」。
