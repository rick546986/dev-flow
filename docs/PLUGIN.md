# dev-flow plugin — 安裝與 Runtime 說明

> 舊的 `dev-flow-plugin` repo 已併進來,原 repo 已 archive。

`dev-flow` 是一個 Claude Code plugin marketplace。這個 repo 本身就是 marketplace,也是 plugin。三個名字都叫 `dev-flow`。

## 安裝

```
/plugin marketplace add rick546986/dev-flow
/plugin install dev-flow@dev-flow
```

裝完實際路徑是 `~/.claude/plugins/cache/dev-flow/dev-flow/<version>/`。
不要把版本路徑寫死在腳本裡。用 `${CLAUDE_PLUGIN_ROOT}`,或從自己的位置推。
Windows 同構,在 `%USERPROFILE%\.claude\plugins\cache\dev-flow\dev-flow\<version>\`。

**環境**:hooks 要 python3(只吃標準函式庫)。找直譯器的順序是 `DEVFLOW_PYTHON` → `/usr/bin/python3` → PATH 上的 `python3`。找不到就印警告後放行 —— 那次呼叫沒有守衛,不是功能壞掉。

Windows(Git Bash)沒有 `/usr/bin/python3`。另外裝 Python,或設 `DEVFLOW_PYTHON`(例:`setx DEVFLOW_PYTHON "C:/Python312/python.exe"`)。裝好之後 hook 會生效,但本 repo 的驗證套件在 Windows 上仍跑不全綠。見 `notes/dispatch-windows-parity.md`。

細節見母版 README「環境需求」。

新專案裝好後,進專案打 `dev-setup`。它會建 `.dev-flow/`(進 Git 的記憶正本)與本機快取。之後 `git pull` 不必重跑 setup;下一句 ask / context 會核對 generation。見 README §16。

## 沿革(維護者才需要)

以前方法論與 runtime 拆兩個 repo,名字還很像,安裝常裝錯。後來合回來。

`dev-talk` 也曾是獨立 plugin,2026-08-13 併入。它不再有自己的版本號。沿革寫在這裡,不寫進 `skills/dev-talk/SKILL.md`(那邊受盲原則掃描,寫下游詞會過不了自己的守衛)。

## 內容

| 目錄 | 用途 |
|---|---|
| `hooks/` | 執行守衛與 CLI:`devflow-exec.sh`(Stage 6 task-scoped guard)、`devflow-guard.sh`、`devflow-prebash.sh`、`devflow-postbash.sh`、`devflow-dispatch-guard.sh`、`devtalk-guard.sh`、`devflow-report-guard.sh`、`devflow-plainspeak.sh`、`history-guard.sh`、`gate-consistency.sh`、`devflow-doctor.sh`、`devflow-obs.sh`、`selftest.sh` 與其 `_*_impl.py`(本表由 `scripts/check-hooks-accounting.sh` 對帳) |
| `skills/` | `dev-flow`(7 階段路由器)、`dev-run`(Stage 6 執行引擎)、`dev-setup`(專案安裝器)、`dev-talk`(訪談引導)、`dev-release`(母版發版器)、`dev-report`(缺陷回報產生器)(本表由 `scripts/check-hooks-accounting.sh` 對帳) |
| `agents/` | `devflow-reviewer`(role=reviewer,唯讀收驗)、`devflow-adviser`(role=adviser,唯讀連敗診斷)——兩者 frontmatter 皆 `tools: Read`,不給 Bash/Edit/Write;plugin 載入後型別字串帶命名空間:`dev-flow:devflow-reviewer` 與 `dev-flow:devflow-adviser` **兩支都實測叫得出來**(臨時載入兩次 + v3.9.0 正式安裝一次;證據鏈與「本輪拿不到什麼」見 `agents/devflow-reviewer.md` 的「型別字串」與「正式安裝那條路」兩節;本表由 `scripts/check-hooks-accounting.sh` 對帳) |
| `manifests/` | prompt registry 與版本聲明 |
| `.claude-plugin/` | plugin manifest(marketplace.json + plugin.json) |
| repo 根目錄其餘部分 | 方法論正本:`README.md`(§7 gate 條件)、`_templates/`、`example/`、`guides/`、`docs/`、`scripts/`、`notes/`、`observability/` |

## 跑測試

```bash
# 用本 repo 內建的方法論,不必另外 checkout:
bash hooks/selftest.sh     # 期望全過(案數以腳本輸出為準,不在本檔寫死)

# gate 條件三處摘要是否與 README.md §7 一致
bash hooks/gate-consistency.sh   # 期望全過(項數以輸出為準)

# 測試時要指向另一份方法論 checkout,才設這個:
DEVFLOW_MASTER=/tmp/devflow-master bash hooks/selftest.sh
```

CI(`.github/workflows/selftest.yml`)在每次 push / PR 跑 selftest。
