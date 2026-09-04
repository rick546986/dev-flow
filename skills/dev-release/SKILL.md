---
name: dev-release
description: dev-flow 自己的發版器 — 驗證通過才升版、打 tag、建 GitHub release。當使用者說「dev-release」「發版」「release dev-flow」「打 tag」「升版本」,或改完 dev-flow 要讓其他機器拿到新版時啟用。只用於 rick546986/dev-flow 這個 repo 自己,不是給一般專案發版用。
---

# dev-release — dev-flow 的發版器

**為什麼需要這支**:Claude Code 判斷「plugin 有沒有新版」是比對 `plugin.json` 的
`version` **字串**,不是比對 commit。push 了但版本沒動 → 其他機器 `/plugin update`
回 `(no content)`,什麼都不會拉,**而且不會有任何提示**。

本 skill 把三件容易漏的事機械化:
1. 版本號必須同步(`.claude-plugin/plugin.json`、`.cursor-plugin/plugin.json`、`.codex-plugin/plugin.json` 與 `hooks/runtime-capabilities.json`)
2. 發版前必須跑過驗證(2026-08-13 教訓:gate-consistency 壞了九天沒人知道,
   因為沒有任何關卡強制在發版前跑它)
3. `docs/dev/` 的散發副本要與根目錄正本一致(dev-flow repo 自己也是 dogfooding 專案)

## 用法

`/dev-release patch` | `minor` | `major`,或直接說「發版」由本 skill 依改動範圍建議級別。

語意(對齊 semver,但這裡的「相容」指的是**方法論契約**不是 API):
- **patch** — 修 bug、補文件、改 hooks 內部實作。契約與模板結構不變。
- **minor** — 新增 skill / 新增檢查 / 模板加節。既有專案 `dev-setup upgrade` 後仍相容。
- **major** — 目錄結構、契約版本、marketplace/plugin 名稱變動。既有安裝需要人工介入。

## 執行清單(逐項達成「完成 =」才往下,禁跳項)

### 0. 擋門(任一不過就停,不要「先發了再說」)

```bash
cd ~/dev/dev-flow
git branch --show-current          # 必須是 main
git status --short                 # 必須為空
git fetch origin && git rev-list --left-right --count HEAD...origin/main   # 必須 0 0 或只領先
```

完成 = 三項都符合。有未提交改動 → 先問使用者要 commit 還是 stash,**不要自己決定**。

### 1. 驗證四道(全綠才准發版)

```bash
bash hooks/selftest.sh
# 期望:✅ 守衛自測 N/N 全過(N 以腳本輸出為準,不寫死)

env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
# 期望:✅ 全部一致(14/14 通過)、exit 0
# 三個環境變數必須真的 unset —— 這道同時驗 __file__ fallback 沒壞

bash hooks/devflow-exec.sh doctor
# 期望:✅ devflow doctor: COMPATIBLE
# 注意 cwd:在 ~/dev/dev-flow 跑,驗的是本 repo 自己的 docs/dev/ 散發副本

bash scripts/devflow-check.sh all
# 期望:全綠。涵蓋記憶／觀測性／平行執行等子系統,不是只有 hooks 那幾支。
# CI 綠不代表本機綠;兩邊都要跑。runtime-selftest.yml 綠只代表 hooks;
# devflow-ci.yml 綠只代表方法論檢查。本機還要自己跑這一支。
```

任一紅 → **停止發版**,回報實際輸出。不要「這條跟本次改動無關」就放行 ——
那正是 gate-consistency 壞九天的成因。

完成 = 四道輸出原文都貼出來且全綠。

### 2. 散發副本同步檢查

```bash
diff -q devflow-contract.json docs/dev/devflow-contract.json
bash scripts/check-ship-manifest.sh
```

第一行單獨留著是因為 **contract 不住在 `docs/dev/tools/`**,parity 的
expected set(正本 `docs/dev/ship-manifest.json` 裡 destination 落在 tools/ 的列)
涵蓋不到它的獨立比對 —— 併掉這行就沒有人在驗 contract 副本(正本裡仍有
contract 那一列,管的是它也要被記帳,不是取代這行 `diff -q`)。第二行的
parity 對帳**讀 ship-manifest,不是寫死支數,也不得掃 `docs/dev/tools/`**
(舊版在這裡寫死五個 `diff -q`,新增第六支散發工具必漏驗 —— 第 7 型「不對稱記帳」;
掃副本目錄則正副本同刪會假綠 —— 第 4 型);
它同時比對存在性、內容、清單 `mode` 與**可執行位元**,正副本同時被刪也會紅。

有差異 → 用根目錄正本覆蓋 `docs/dev/` 副本(正本方向永遠是 根目錄 → docs/dev/),
覆蓋後重跑步驟 1 的 doctor。

完成 = contract diff 靜默(無輸出)+ parity 守衛全過(✅)。

### 3. 升版號(兩處,一起改)

讀 `.claude-plugin/plugin.json` 現值,依級別算出新版號,然後**同時**改:

| 檔案 | 欄位 |
|---|---|
| `.claude-plugin/plugin.json` | `version` |
| `.cursor-plugin/plugin.json` | `version` |
| `.codex-plugin/plugin.json` | `version` |
| `hooks/runtime-capabilities.json` | `runtime_version` |

**不要動** `supported_contract_versions` 與 `schema_versions` —— 那兩個跟著
`devflow-contract.json` 的契約版本走,不隨發版遞增。契約真的要改版時,
`devflow-contract.json` 的 `devflow_contract_version` 與 runtime 的
`supported_contract_versions` 要一起改,那是 major。

改完驗證:

```bash
jq -r .version .claude-plugin/plugin.json
jq -r .version .cursor-plugin/plugin.json
jq -r .version .codex-plugin/plugin.json
grep -o '"runtime_version": "[^"]*"' hooks/runtime-capabilities.json
# 四處必須是同一個字串
```

完成 = 兩處值相同且等於目標版號。

### 4. 更新 `docs/dev/STATUS.md` 與 `docs/dev/HISTORY.md`

**做完的事寫進 HISTORY.md,不留在 STATUS.md** —— 後者只回答「現在誰在做什麼、
還有什麼沒做」。

```bash
scripts/history-append.sh --slug <代號> --version vX.Y.Z \
  --what "<可觀測的結果,一句話>" \
  --why  "<當初的痛點,一句話>" \
  --where "<改動落在哪些檔/目錄>" \
  [--adr NNNN] [--detail <release 連結>]
```

**不要用 Edit/Write 直接改 `HISTORY.md`** —— 多 session 並行時會靜默覆蓋,
`history-guard` hook 會擋下。純修 bug 沒有對應 feature 時,`--slug` 用問題編號
(例 `a13-start-ignored-dirty`)。

`STATUS.md` 這邊只要:本次做完的 feature 從 **Active** 移除;**Backlog** 有項目
在本次做掉 → 一併移除。

完成 = HISTORY.md 多一筆(`bash scripts/check-history-integrity.sh` 綠);
STATUS.md 的 Active 沒有留下已完成項。

### 5. Commit

```bash
git add .claude-plugin/plugin.json .cursor-plugin/plugin.json \
        .codex-plugin/plugin.json hooks/runtime-capabilities.json \
        docs/dev/STATUS.md docs/dev/HISTORY.md
# 若步驟 2 有覆蓋副本,一併 add docs/dev/
git commit -m "release: vX.Y.Z — <一句話說明本次改了什麼>"
```

完成 = commit 建立,`git status --short` 為空。

### 6. Push main —— **這步交給使用者自己跑**

使用者的 `~/.claude/settings.json` 有 `permissions.deny: Bash(*git push*main*)`,
這是他刻意設的護欄(對應鐵律 9)。**不要試圖繞過**(改指令形狀、改設定、用別的工具都不行)。

請他在輸入框打:

```
! cd ~/dev/dev-flow && git push origin main
```

完成 = 使用者回報 push 成功,或你確認 `git rev-list --count origin/main..HEAD` 為 0。

### 7. Tag + GitHub Release

tag 名稱不含 `main`/`master`,所以這步不會被 deny 規則擋,可以直接跑:

```bash
cd ~/dev/dev-flow
git tag -a vX.Y.Z -m "vX.Y.Z — <一句話>"
git push origin vX.Y.Z

gh release create vX.Y.Z \
  --title "vX.Y.Z — <一句話>" \
  --notes "<release notes>"
```

release notes 內容(不要只貼 commit 標題):
- **改了什麼** — 使用者角度,不是檔案清單
- **要不要動手** — 既有安裝需不需要重跑 `dev-setup`、要不要重新 install
- **驗證** — 貼步驟 1 四道的實際輸出摘要

完成 = `gh release view vX.Y.Z` 查得到。

### 8. 告訴使用者其他機器怎麼拿

```
/plugin marketplace update dev-flow
/plugin update dev-flow
/reload-plugins            # 當前 session 立刻生效;或開新 session
```

到專案目錄再跑 `dev-setup`(它會偵測 stale 並提議 upgrade)。

設了 `autoUpdate: true` 的機器不用打前兩行,開新 session 自動更新。

## 禁止

- 驗證沒過就發版,或以「這條跟本次改動無關」放行
- 只改一處版本號
- 繞過 push main 的 deny 規則
- 自己決定要不要 commit 使用者的未提交改動
- 把 `supported_contract_versions` 跟著版號一起改
