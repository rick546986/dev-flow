# 跨 repo patch 暫存區（merge prerequisite）

這裡放**本 repo 修不掉、必須由外部 plugin repo 落地**的修正。
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
| 本機分支 | `fix/reject-duplicate-task-fields`（2 個 commit，已 commit 未 push） |
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

**這些只讓 repo-local reference parser 與模板規則正確；真正在跑的 runtime 仍是舊行為，直到上面的 patch 落地。**
