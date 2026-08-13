# dev-flow plugin — 安裝與 Runtime 說明

> 本檔取代舊 `dev-flow-plugin` repo 的 README。2026-08 該 repo 併入本 repo
> （方法論母版 + runtime plugin 合一，見下），原 repo 已 archive、不再更新。

`dev-flow` 是一個 Claude Code plugin marketplace，**本 repo 本身就是 marketplace 也是
plugin**：`.claude-plugin/marketplace.json` 的 `name` 與 `.claude-plugin/plugin.json`
的 `name` 皆為 `dev-flow`，repo 名亦為 `dev-flow`，三名合一。

安裝：

```
/plugin marketplace add rick546986/dev-flow
/plugin install dev-flow@dev-flow
```

安裝後實際路徑為 `~/.claude/plugins/cache/dev-flow/dev-flow/<version>/`（勿寫死於腳本，
一律用 `${CLAUDE_PLUGIN_ROOT}` 或由自身位置推導）。

## 併入前的分工（歷史脈絡）

併入之前，方法論正本（README §7 gate 條件、`_templates/`、`example/`、`notes/design/`）
與 runtime（實際執行的 hooks/skills/CLI）分屬兩個 repo：母版 `rick546986/dev-flow`
與 runtime plugin `rick546986/dev-flow-plugin`。兩者互不冒充：母版 CI 綠 =
`REPO_REFERENCE_PASS`（模板/範例/fixture/契約檔自洽），plugin CI 綠 =
`EXTERNAL_RUNTIME_PASS`（守衛與 CLI 行為）。2026-08 合併後，`methodology/` 子目錄層
也一併收攏進 repo 根目錄——本 repo 根目錄現在同時是方法論正本與 runtime 來源，
不再是兩個 repo。

## 內容

| 目錄 | 用途 |
|---|---|
| `hooks/` | 執行守衛與 CLI:`devflow-exec.sh`(Stage 6 task-scoped guard)、`devflow-guard.sh`、`devflow-prebash.sh`、`devflow-postbash.sh`、`devtalk-guard.sh`、`gate-consistency.sh`、`devflow-doctor.sh`、`devflow-obs.sh`、`selftest.sh` 與其 `_*_impl.py` |
| `skills/` | `dev-flow`(7 階段路由器)、`dev-run`(Stage 6 執行引擎)、`dev-setup`(專案安裝器)、`dev-talk`(訪談引導) |
| `manifests/` | prompt registry 與版本聲明 |
| `.claude-plugin/` | plugin manifest(marketplace.json + plugin.json) |
| repo 根目錄其餘部分 | 方法論正本:`README.md`(§7 gate 條件)、`_templates/`、`example/`、`guides/`、`docs/`、`scripts/`、`notes/`、`observability/` |

## 跑測試

```bash
# 方法論已內建於本 repo 根目錄,缺省即用內建版本,無需另外 checkout:
bash hooks/selftest.sh     # 期望 294/294

# gate 條件三處摘要是否與 README.md §7 一致
bash hooks/gate-consistency.sh   # 期望 14/14

# 仍可用 DEVFLOW_MASTER 覆蓋(測試/移植用途,指向另一份方法論 checkout):
DEVFLOW_MASTER=/tmp/devflow-master bash hooks/selftest.sh
```

CI(`.github/workflows/selftest.yml`)在每次 push / PR 跑上述 selftest。

## 為什麼曾經拆成兩個 repo、又為什麼合回來

原本 `dev-flow-plugin` 只是本機 local plugin、無 remote。2026-08 的 fresh review 抓到一個
**跨 repo 缺陷(F-1)**:`5-tasks.md` 的 `Boundaries:` / `Intent:` 續行若寫成
`- Files:` 之類的保留欄名子項,`FIELD_RE`(前綴 `\s*` 而非 `^`)會把它當成該 T 的欄位,
配上 last-write-wins 就**靜默覆寫**該 T 真正的 `Files` —— 而 `Files` 是
`task_scope()` 與 gate `files_within_scope` 的唯一依據,Stage 6 的允許寫入範圍因此被無聲放寬。

修正在 `04c9389`(`devflow-lib.py` + `_exec_impl.py` 改 fail-closed、保留首筆值)與
`3d2f5b1`(`selftest.sh` 兩個常設 regression case:`parse-boundshadow` / `parse-boundcont`,
292 → 294)。

沒有 remote 就無法讓 reviewer 直接檢查 commit 與測試,因此 `dev-flow-plugin` repo 當時
上線,讓 `EXTERNAL_RUNTIME` 這一半也能被獨立核對。但兩個同義相似名(`dev-flow` /
`dev-flow-plugin`)造成長期的指令混淆(使用者多次搞混該用哪個名字安裝/更新),
加上 GitHub Pages 本就架在 `rick546986/dev-flow`,2026-08 的 single-plugin-merge
決定把 plugin 併回母版 repo,單一名稱、單一 remote,`dev-flow-plugin` repo 之後 archive。
