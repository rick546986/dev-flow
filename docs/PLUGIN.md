# dev-flow plugin — 安裝與 Runtime 說明

> 舊的 `dev-flow-plugin` repo 已併進來,原 repo 已 archive。

`dev-flow` 是一份方法包、三邊 plugin。正本只有 repo 根的 `skills/`、`hooks/`、`_templates/`。Claude／Cursor／Codex 各自一個薄殼 manifest,不要抄三份。Grok 沒有獨立 marketplace。

## 四邊安裝／更新

### Claude

語意不准改:

```
/plugin marketplace add rick546986/dev-flow
/plugin install dev-flow@dev-flow
```

更新:

```
/plugin marketplace update dev-flow
/plugin update dev-flow
```

**順序不能顛倒:先 `marketplace update`、再 `update`。** 單打 `plugin update` 不會先刷新 marketplace 目錄;
本機目錄還是舊的,就會回「already at the latest version」,即使 GitHub 上已發新版。

**升到 3.26.2:** 照上面兩步(`marketplace update` → `plugin update`),重開 session 即可。3.26.2 新增的 `hooks/devflow-find-python.sh`
隨 `hooks/` 整包進 plugin,不需另外散發;ship-manifest 列未變、當時指紋 `v1-8b3e8230958df1be` 不變,所以採用專案的
`docs/dev/tools/` 不必重新散發(不需要跑 dev-setup upgrade;3.26.3 起指紋改 v2,見下)。要核對 manifest 列是否齊全或補齊舊專案缺件,用
`python3 "<plugin 根>/scripts/devflow-upgrade-manifest.py" --root <專案根>`(預設 dry-run,`--apply` 才寫)。

**升到 3.26.3:** 同樣兩步(`marketplace update` → `plugin update`),重開 session。**這版 ship-manifest 指紋由 v1 升 v2**
(`v1-8b3e8230958df1be` → 見 `devflow-contract.json` 的 `ship_manifest_version`;v2 把各散發檔的內容雜湊算進去),所以採用專案要重新散發
`docs/dev/`:`python3 "<plugin 根>/scripts/devflow-upgrade-manifest.py" --root <專案根>` 先 dry-run 看「新增／變更」,確認後 `--apply`
(manifest 列含 `devflow-contract.json`、`ship-manifest.json` 與 `docs/dev/tools/` 都會換成這版;`--apply` 也會把 baseline 對應檔同步成上游新內容,
baseline 目錄不存在則不建立)。沒升 v2 的專案 doctor 照舊不擋,但會印 info 說明 v1 看不出工具檔內容過期、並顯示 plugin 現行指紋;
升 v2 之後 doctor 會在受管檔內容過期時報 `✗ ship-manifest`。doctor 入口是 `<plugin 根>/hooks/devflow-exec.sh doctor`(在 `hooks/`,不是 `scripts/`)。

**升到 3.26.5:** 同樣兩步(`marketplace update` → `plugin update`),重開 session。修 Jev noul 題缺 `criteria`／`instructions` 的 bug(Jev 服務回 HTTP 400,J1~J5 實連全失敗、錯誤原因沒記下):題庫補齊、`gate_questions_for_api` 帶出且缺則本機 raise、`http_transport` 的 400／422 detail(已遮機密、≤500 字)記進 `noop_detail`。`scripts/devflow_jev/` 與 `scripts/devflow-jev.py` 的散發檔內容改變,ship-manifest 指紋 v2 隨之更新:採用專案要重新散發(`dev-setup upgrade`),否則 doctor 會報 `✗ ship-manifest`。兩份題庫內容變了,`questionset_hash` 換新、校準紀錄從新群組重開(預期行為)。旗標、gate 開關與門檻不變(J2／J5／MR 維持 shadow、J4 關閉、GRADUATED 等仍為 False)。

**升到 3.26.4:** 同樣兩步(`marketplace update` → `plugin update`),重開 session。只改 `scripts/devflow-upgrade-manifest.py` 的 baseline 同步:「需同意:baseline 沒有此檔」而被跳過(沒加 `--include-custom`)的列,`--apply` 不再把上游新內容新增進 baseline(否則下一輪 dry-run 會把沒客製的檔誤判成「本地客製」),輸出會逐列標出原因。ship-manifest 列與指紋不變,採用專案不必重新散發;之前因此被誤判的專案,若 baseline 已被塞入新版,照 dry-run 看到的「本地客製」逐檔確認即可(該檔本地若是舊版就是被誤判,同意後加 `--include-custom` 覆蓋)。

實測(2026-10-15,Claude Code 2.1.296,拋棄式隔離環境 + 本機 git 假 marketplace,**shell 形式**):

| 動作 | 結果 |
| --- | --- |
| 上游已升版,直接 `plugin update` | `already at the latest version (<舊版>)`,版本沒動 ← 這就是「更新前 3.25.0 卻回 already at the latest」可重現的成因 |
| `marketplace update`(有名稱或不帶名稱都一樣) | 只刷新 marketplace 目錄;`plugin list` 的已裝版本**不變** |
| 再 `plugin update` | `updated from <舊> to <新> … Restart to apply changes.`,磁碟上已換新版 |

官方文件(`code.claude.com/docs/en/plugins/install`〈Update plugins now〉、`plugins/loading`〈Versions and updates〉)與實測一致:shell 的 `claude plugin marketplace update` 只刷新目錄、不升已裝 plugin;plugin 版本以 `plugin.json` 的 `version` 字串判斷(所以每次發版必須改版號,見 dev-release)。

**未證實**(不要當結論引用):
- session 內打 `/plugin marketplace update dev-flow` 會不會連已裝 plugin 一起升。官方說 `/plugin` 的 Marketplaces 分頁選「Update marketplace」會一併更新該市集已裝的 plugin;但該 slash 指令帶名稱時只寫「在那裡刷新」,兩者是否等同文件未載明,非互動環境也測不到。保險做法仍是兩步都打。
- SpaceS 那次的實際成因。上表是可重現的一種;另一種可能是該 marketplace 開了 auto-update(官方:第三方 marketplace 預設關,可手動開),磁碟先升了、正在跑的 session 仍載入舊版。查證要看他當時的 `plugin list` 與 `~/.claude/plugins/installed_plugins.json`。

怎麼確認目前版本(三處,以前兩處為準):
1. shell:`command claude plugin list`,看 `dev-flow@dev-flow` 底下的 `Version:`(磁碟上已裝的版本)。
2. 檔案:`~/.claude/plugins/installed_plugins.json` 裡 `dev-flow@dev-flow` 的 `version`,與 `~/.claude/plugins/cache/dev-flow/dev-flow/<version>/` 目錄名。
3. 正在跑的 session 載入的版本可能比磁碟舊:`plugin update` 完要 `/reload-plugins` 或開新 session 才換(官方:「Restart to apply changes」)。

要在 shell 裡打(不進 Claude session)時,照這樣打:

```
command claude plugin marketplace update dev-flow
command claude plugin update dev-flow@dev-flow
command claude plugin list
```

為什麼寫 `command claude`:部分使用者的 zsh 把 `claude` 定義成會跳互動選單的 function,直接打 `claude plugin ...` 會被它攔走;`command` 會跳過 function 直接跑執行檔。session 內的 `/plugin ...` 不經 shell,不受影響,不用加。

裝完實際路徑是 `~/.claude/plugins/cache/dev-flow/dev-flow/<version>/`。
不要把版本路徑寫死在腳本裡。用 `${DEVFLOW_ROOT}`（舊名 `${CLAUDE_PLUGIN_ROOT}` 當別名）,或從自己的位置推。
Windows 同構,在 `%USERPROFILE%\.claude\plugins\cache\dev-flow\dev-flow\<version>\`。

### Cursor

官方格式:`.cursor-plugin/plugin.json`（`skills` 指整棵 `./skills/`）。市集:`.cursor-plugin/marketplace.json`,`source` 指本 repo 根。鍵名對 `docs.cursor.com/docs/reference/plugins`,不要發明。

安裝（`docs.cursor.com/docs/plugins`）:

1. Dashboard → Plugins → Import from Repo → `rick546986/dev-flow`
2. Customize → 找到 `dev-flow` → Install（user 或 project）

更新:Refresh 在 Dashboard → Plugins **已匯入的 rick546986/dev-flow 那一列**,不是 plugin 詳情卡。或開 Auto Refresh。
本機試裝:`ln -s <clone> ~/.cursor/plugins/local/<name>`（`<name>` = plugin.json 的 `name`）

產品 repo 技能樹仍可掛整棵 `.cursor/skills`(dev-setup)。流程規則不准灌進 AGENTS.md。Cursor 只准 `.cursor/rules/` 一行架構不變量指標。

### Codex

官方格式:`.codex-plugin/plugin.json`,`skills: "./skills/"`(整棵真目錄,不是 symlink)。Codex 安裝會跳過 symlink,不准只丟 SKILL.md。

市集走 Codex 官方也認的 legacy 路徑 `.claude-plugin/marketplace.json`（`source: "./"`）。不另造第三套假目錄。

實測（本機跑 `@openai/codex@0.150.1 plugin --help`,2026-08）:**沒有** `codex plugin install`、**沒有** `codex plugin update`（兩個都是 `unrecognized subcommand`）。不要抄 Claude 的 `/plugin`。

```
codex plugin marketplace add rick546986/dev-flow
codex plugin add dev-flow@dev-flow
codex plugin marketplace upgrade dev-flow
```

更新已裝 plugin:再跑一次 `codex plugin add dev-flow@dev-flow`。TUI 用 `/plugins`。

### Grok

不要發明 Grok marketplace。Grok Bot 吃 Cursor 帳裝好的同一包（已見過 `plugins/cache/dev-flow/...`）。本機 Grok 技能庫仍可掛整棵 `.grok/skills`。不要假裝能從產品 repo 自動灌進 Grok。

**環境**:以下 hooks 規則只在 Claude Code 生效。Cursor／Codex 薄殼不掛 hooks,沒有機械擋寫入。非 Claude 主機**沒有 PreToolUse**；共同 runtime 是該站 `--action`（allow 鑄 `.devflow/host-receipt/<slug>/<station>.json`；`verify_receipt:true` 只核對不鑄）。`devflow-exec start` 單獨成功 ≠ 已武裝。不准為了別的主機改鬆 `--action`。hooks 要 python3(只吃標準函式庫,編譯下限 3.9)。hook 找直譯器:`DEVFLOW_PYTHON` → `/usr/bin/python3` → PATH。找不到就印警告後放行 —— 那次呼叫沒有守衛,不是功能壞掉。
gate-twin／產圖要 `markdown-it-py==4.0.0`(Python **3.12+**)。macOS 系統 python 常是 3.9,裝不出 4.x。用專案 venv 或設 `DEVFLOW_PYTHON` 指向 3.12+,**不要覆寫** Apple 系統 Python。doctor 的 `printer-python` 會查。手動跑 `devflow-doctor.sh`／`hooks/selftest.sh` 且沒設 `DEVFLOW_PYTHON` 時,會自動在 PATH 與 Homebrew 等目錄找 3.12+(共用 `hooks/devflow-find-python.sh`,與 Stop hook 同一份;候選要 `--version` 跑得起來才採用,Apple Silicon 上 Bad CPU type 的 x86 版 python／bash 會被跳過);找不到時 selftest exit 2 並說明怎麼裝,doctor 報 `printer-python` ✗。

Windows(Git Bash)沒有 `/usr/bin/python3`。另外裝 Python 3.12+,或設 `DEVFLOW_PYTHON`(例:`setx DEVFLOW_PYTHON "C:/Python312/python.exe"`)。裝好之後 hook 會生效,但本 repo 的驗證套件在 Windows 上仍跑不全綠。見 `notes/dispatch-windows-parity.md`。

本檔上一節即環境規則。不要覆寫 `/usr/bin/python3`。

feat worktree 產的 `docs/dev` html/md 併回整合線(常是 `develop`／`testing`)是預期,不是污染;HISTORY 種子列也會跟著走。不要把雙生頁只留在 worktree。

新專案裝好後,進專案打 `dev-setup`。它會建 `.dev-flow/`(進 Git 的記憶正本)與本機快取。之後 `git pull` 不必重跑 setup;下一句 ask / context 會核對 generation。見 [guide #memory](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#memory)。

## 沿革(維護者才需要)

以前方法論與 runtime 拆兩個 repo,名字還很像,安裝常裝錯。後來合回來。

`dev-talk` 也曾是獨立 plugin,2026-08-13 併入。它不再有自己的版本號。沿革寫在這裡,不寫進 `skills/dev-talk/SKILL.md`(那邊受盲原則掃描,寫下游詞會過不了自己的守衛)。

## 內容

| 目錄 | 用途 |
|---|---|
| `hooks/` | 執行守衛與 CLI:`devflow-exec.sh`(Build（Stage 6）task-scoped guard)、`devflow-guard.sh`、`devflow-prebash.sh`、`devflow-postbash.sh`、`devflow-dispatch-guard.sh`、`devtalk-guard.sh`、`devflow-report-guard.sh`、`devflow-plainspeak.sh`、`devflow-stop-selftest.sh`(Stop:改完跑守衛自測,需 Python 3.12+)、`history-guard.sh`、`gate-consistency.sh`、`devflow-doctor.sh`、`devflow-obs.sh`、`selftest.sh` 與其 `_*_impl.py`(本表由 `scripts/check-hooks-accounting.sh` 對帳) |
| `skills/` | `dev-flow`(五站路由器 Intake→Decide→Spec→Build→Ship;in-flight 可 dual-read 舊七檔)、`dev-run`(Build 執行引擎)、`dev-setup`(專案安裝器)、`dev-talk`(訪談引導)、`dev-release`(母版發版器)、`dev-report`(缺陷回報產生器)(本表由 `scripts/check-hooks-accounting.sh` 對帳) |
| `agents/` | `devflow-reviewer`(role=reviewer,唯讀收驗)、`devflow-adviser`(role=adviser,唯讀連敗診斷)——兩者 frontmatter 皆 `tools: Read`,不給 Bash/Edit/Write;plugin 載入後型別字串帶命名空間:`dev-flow:devflow-reviewer` 與 `dev-flow:devflow-adviser` **兩支都實測叫得出來**(臨時載入兩次 + v3.9.0 正式安裝一次;證據鏈與「本輪拿不到什麼」見 `agents/devflow-reviewer.md` 的「型別字串」與「正式安裝那條路」兩節;本表由 `scripts/check-hooks-accounting.sh` 對帳) |
| `manifests/` | prompt registry 與版本聲明 |
| `.claude-plugin/` | Claude plugin manifest(marketplace.json + plugin.json);Codex 官方也讀這份 marketplace 當 legacy 市集 |
| `.cursor-plugin/` | Cursor 薄殼:`plugin.json` + `marketplace.json`;`source` 指本 repo 根,`skills` 整棵 `./skills/` |
| `.codex-plugin/` | Codex 薄殼:`plugin.json`;`skills: "./skills/"`(整棵,不是 symlink) |
| repo 根目錄其餘部分 | 方法論正本:`guides/guide-dev-flow.html`(人看)、`docs/dev/readme-contract-extract.md`(檢查器抽)、`_templates/`、`example/`、`guides/`、`docs/`、`scripts/`、`notes/`、`observability/` |

## 跑測試

```bash
# 用本 repo 內建的方法論,不必另外 checkout:
bash hooks/selftest.sh     # 期望全過(案數以腳本輸出為準,不在本檔寫死)

# gate 條件三處摘要是否與契約檔 §7 一致
bash hooks/gate-consistency.sh   # 期望全過(項數以輸出為準)

# 測試時要指向另一份方法論 checkout,才設這個:
DEVFLOW_MASTER=/tmp/devflow-master bash hooks/selftest.sh
```

CI 分兩層,不要混:
- `.github/workflows/runtime-selftest.yml` — hooks 行為(`hooks/selftest.sh` + `gate-consistency.sh`)
- `.github/workflows/devflow-ci.yml` — 方法論／契約／模板(`scripts/devflow-check.sh all`)
一邊綠不代表另一邊綠。
