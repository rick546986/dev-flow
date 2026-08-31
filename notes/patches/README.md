# 跨 repo patch 暫存區（歷史）

> 現況：plugin 已併進本 repo（ADR-0001）。runtime 在 `hooks/`，
> `tests/parallel-stage6/` 只住方法包。下面各 patch 是 2026-08 兩 repo
> 時期的落盤紀錄，不要再當成現行裝法。

這裡放**當時**本 repo 修不掉、必須由外部 plugin repo 落地的修正。
每個 patch 都對應一條 fresh review finding，且都是 **merge prerequisite**：
patch 未在 runtime 落地前，本 repo 的對應修正只擋得住 repo-local reference parser，
擋不住真正在跑的 Stage 6 scope guard。

## 為什麼是 patch 檔而不是一張 PR

外部 plugin 的正式 git repository 在
`~/.claude/plugins/local/dev-flow`（`git rev-parse --show-toplevel` 實測），
但 **`git remote -v` 為空** —— 沒有任何可 push 的 remote，因此無法開 plugin PR。
在 remote 建立之前，patch 檔是唯一能讓修正進版本控制、被 review、且不混進本 repo commit 的形式。

## plugin-reject-duplicate-task-fields.patch

| | |
|---|---|
| 對應 finding | **F-1**（`Boundaries:`／`Intent:` 續行遮蔽保留欄 → 靜默覆寫 Files/Verify） |
| 目標 repo | `~/.claude/plugins/local/dev-flow`（無 remote） |
| 目標 base | `master` @ `522569a` |
| 本機分支 | `fix/reject-duplicate-task-fields`（2 個 commit：`04c9389`、`3d2f5b1`） |
| **落地狀態** | **已 merge 進安裝來源 `master`，merge commit `71e452d`（2026-08-03）** —— 該目錄就是 Claude Code 實際載入的 plugin，故本機 runtime 已修好 |
| 改動檔 | `hooks/devflow-lib.py`、`hooks/_exec_impl.py`、`hooks/selftest.sh` |
| 套用驗證 | `git -C ~/.claude/plugins/local/dev-flow apply --check <本檔案>` → OK |
| runtime regression test | `hooks/selftest.sh` 新增 `parse-boundshadow`、`parse-boundcont` 兩案（292 → **294** 全過） |

套用方式：

```bash
cd ~/.claude/plugins/local/dev-flow
git checkout -b fix/reject-duplicate-task-fields master
git am /path/to/dev-flow/notes/patches/plugin-reject-duplicate-task-fields.patch
bash hooks/selftest.sh        # 期望 294/294
```

### 這個 patch 修什麼

`FIELD_RE` 的前綴是 `\s*`（不是 `^`），所以任何縮排層級的 `- <保留欄名>:`
都會被當成該 T 的欄位；賦值是 last-write-wins 且無重複偵測。
`Boundaries:` 續行若寫成 `  - Files: …` 子項，該 T 真正的 `Files` 會被**靜默換掉**、
`errors` 為空 —— 而 `Files` 是 `task_scope()` 與 gate `files_within_scope` 的唯一依據。

修正前 master 的實測（同一份 fixture）：

```text
errors     : []
T-1 files  : ['internal/handler/', 'internal/service/', 'internal/repo/']   ← 原本是兩個具名 .go 檔
T-1 verify : '依賴方向不得反向'                                              ← 原本是 go test 指令
task_scope : ['internal/handler/', 'internal/repo/', 'internal/service/']
```

patch 把 `devflow-lib.py` 的 `parse_5_tasks` 與 `_exec_impl.py` 的 legacy scope 解析
都改成 fail-closed（記 error／`die`），並保留首筆值。

### 本 repo 這一側已經做了什麼

- `tests/parallel-stage6/contract_ref.py`：同一條 fail-closed 規則（可執行契約正本）。
- `_templates/5-tasks.md`：新增「續行禁令」，列出全部 11 個保留欄名。
- `tests/parallel-stage6/fixtures/boundaries-shadow.md`：負向 fixture（必須報錯）。
- `tests/parallel-stage6/fixtures/boundaries-continuation.md`：相容性對照組（合法續寫不得誤判）。
- `tests/parallel-stage6/run_tests.py`：+20 檢查（97 → 117）。

### 落地與尚未關閉的部分

**已落地（本機可驗證）**：patch 已 merge 進 `~/.claude/plugins/local/dev-flow` 的 `master`
（merge commit `71e452d`，parents = `522569a` + `3d2f5b1`）。安裝來源重跑：
`hooks/selftest.sh` **294/294**、`hooks/gate-consistency.sh` **14/14**；
直接對安裝中的 `devflow-lib.py` 餵遮蔽 fixture，已回報「重複保留欄」且 `task_scope`
維持兩個具名檔（未被放寬成整目錄）。

**尚未關閉**：該 repo 仍**無 remote**，因此

- 沒有可供他人取得的 commit URL，`71e452d` 只在本機可驗證；
- **沒有發布／安裝流程** —— 換一台機器或重裝 plugin，拿到的仍是未修正的版本；
- GitHub CI 不執行 plugin，`REPO_REFERENCE` 綠與這件事無關。

因此 pilot 前仍須擇一：①替 plugin 建 remote 並 push `master`（讓 `71e452d` 可取得）；
或②建立可重現的散發流程（例如把 plugin 納入 dev-setup 的版本化散發），
讓 pilot 用到的 runtime 確實含此修正。在那之前，**F-1 只在本機關閉，不算流程上關閉。**
