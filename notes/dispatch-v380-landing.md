# 派工單：讓 dev-flow 真的能被人照著用（v3.8.0 發版前最後一輪）

> **觸發句**：`讀 ~/dev/dev-flow/notes/dispatch-v380-landing.md 照它跑，全程不打斷問人`
>
> 本檔是**派工單**，讀完就照做。**十一項都已由 owner 裁決完畢，沒有要回頭問的事。**
>
> 唯一該停下回報的情況：本檔寫的東西與現場實況對不上（指定的行號找不到、
> 指定的檔案不存在、驗收條件互相矛盾）。那種時候停下說清楚，不要自己猜著做。

---

## 這份要解決什麼

上一輪（`notes/dispatch-v380-blockers.md`）把七項必修全部做完了，
主幹是對的：四態判定、八情境、五 mutant、正副本 755、Backlog 10 條、
HISTORY、版號 3.8.0、工作樹乾淨 —— 兩路 fresh review 與跨家族審查都各自確認過。

**問題全部集中在「人真的照著用」那一層**：

- 工具的參數打錯會**卡死終端機**（不是報錯，是掛住）
- 安裝流程的快照拍在散發之前，**下次升級會把官方工具當成本地客製**
- 導覽教的開 branch 方式，**到 Stage 7 一定卡住**（缺錨點）
- 三支守衛有可以被繞過的洞

這一類缺陷母版內部的 143 ＋ 378 ＋ 24 項守衛**全部看不到**，
因為它們驗的是「檔案寫得對不對」，不是「照著做會發生什麼」。

**這就是 dev-flow 還沒落地的真正原因** —— 不是東西沒做完，
是沒有人真的從頭到尾照著文件走過一次。

### 版本號怎麼算

**維持 3.8.0，不要 bump。** v3.8.0 從未推出、沒有 tag、沒有 release，對外它還不存在，
所以繼續編輯它是對的。`.claude-plugin/plugin.json` 與
`hooks/runtime-capabilities.json` 兩處**都不要動**。

---

## 硬約束

0. **開工第一件事**：從 `main` 開一條工作 branch `fix/v380-landing`，
   不要在 `main` 上直接動手。做完 `git merge --no-ff` 回 `main`。
1. **不打 tag、不發 release。push 由 owner 自己跑**（他的設定擋掉了 agent 推 main，
   那是刻意的護欄，不要繞）。**完整的收尾動線見文末「收尾」節，那一節有先後順序，
   照著走**——特別是 `docs/dev/STATUS.md` 只能在 `main` 上改，不准在工作 branch 上碰。
2. **不准動 Stage 1–4 的模板內容**（`_templates/1-discussion.md` ~ `_templates/4-spec.md`）。
   真實 full lane 觀測還沒跑，先動那幾份會污染觀測。
3. **不准放寬任何檢查來讓事情變綠**。本輪明文授權修改守衛的項目是
   **A-1、A-2、A-3、B-1~B-5、C-2**（A 批各自要動 integration wrapper／
   dev-setup discipline guard／STATUS guard；C-2 也要收緊 STATUS guard），
   方向一律是**收緊**，不准放寬。這九項以外的守衛一個字都不要動。
4. **不准 bump 版號**。
5. **不准新增任何腳本檔**。本輪全部是修既有檔 —— 所以
   `scripts/check-file-map.sh` 的 `EXPECTED_MAPPED_FILES = 77` **不用動**。
   如果你發現自己想新增一支 `.sh`／`.py`，**停下回報**，那表示你偏離了本檔的範圍。
6. `docs/dev/HISTORY.md` 只能用 `scripts/history-append.sh` 追加，不准直接編輯。
7. **不要順手修無關的東西**。看到別的問題寫進回報問要不要處理，不要自己動手。

---

# 第一批 · 會咬人的三件（優先做完）

## A-1〔擋發版〕整合回歸工具的參數打錯會卡死終端機

**位置**：`scripts/devflow-integration-regression.sh:34-42`（正本）
＋ `docs/dev/tools/devflow-integration-regression.sh` 同一段（散發副本）

### 現象（已實測；上一版 brief 把範圍寫小了，這是更正後的結果）

`/bin/bash`（3.2）與 homebrew `bash`（5.2）跑出來完全一致，每個案例 5 秒逾時：

```
（無參數）                                    → rc=2      （但不印「用法」，見下）
--integration                                → ⛔ TIMEOUT
--fork-sha                                   → ⛔ TIMEOUT
--integration origin/main --fork-sha         → ⛔ TIMEOUT
--fork-sha abc --integration                 → ⛔ TIMEOUT
--no-fetch --integration                     → ⛔ TIMEOUT
--integration origin/main --fork-sha --no-fetch → rc=2   （但 --no-fetch 被當成值吞掉了）
```

**規律不是「旗標是整條命令唯一參數」** —— 上一版 brief 這樣寫是錯的。
正確的規律是：

> **任何需要值的旗標，只要 parser 處理到它的時候它已經是最後一個參數，就會死迴圈。**

前面有幾個參數、有沒有成功解析過，都不影響。

⚠️ 還有第三種錯：最後一行那個案例雖然 exit 2，但那是**因為 `--no-fetch` 被當成
`--fork-sha` 的值吞掉了**，`FORK_ARG` 變成字串 `--no-fetch` 才在後面被判非法。
「把下一個旗標吞成值」本身就是缺陷 —— 使用者以為自己開了診斷模式，實際上沒有。

### 根因

```bash
while [ $# -gt 0 ]; do
  case "$1" in
    --integration) INTEGRATION_ARG=${2:-}; shift 2 ;;   # ← $#=1 時 shift 2 失敗且不前進
    --fork-sha)    FORK_ARG=${2:-};        shift 2 ;;
```

`shift 2` 在只剩一個參數時**回非零而且不 shift**（實測 `set -- a; shift 2` → rc=1、剩餘=1），
於是 `$1` 永遠是同一個旗標，迴圈原地打轉。

### 第二個問題：無參數不印用法

```
$ devflow-integration-regression.sh          # 無參數
-- 前置檢查(fail-closed,任一不過即 exit 2)--
  ✗ 缺 --fork-sha(必填)。...
$ echo $?
2                    ← exit code 對
$ ... | grep -c "用法"
0                    ← 但訊息不含「用法」
```

而 `skills/dev-setup/SKILL.md` **兩處**斷言「無參數跑 → 訊息含『用法』且 exit 2」
（`:120` install 步 7 驗證①、`:273` check 第 12 項③）。

**失敗情境**：採用專案跑健檢 → 第 12 項不通過 → 把一個完全正常的工具判成 broken →
使用者被導去「走 install 步 7 補」→ 重裝之後還是 broken → 無限迴圈。

跟既有兩支工具的慣例也不一致：

```
build-gate-twin.py（無參數）            → 用法:build-gate-twin.py <專案根目錄> ...
devflow-evidence-gauntlet.sh（無參數）   → usage: devflow-evidence-gauntlet.sh <file.md> ...
devflow-integration-regression.sh（無參數）→ （不印用法）   ← 只有這支不一樣
```

**母版為什麼抓不到**：`check-integration-regression-guard.sh:228` 斷言的是
`"缺 --fork-sha" in out`，`SKILL.md` 斷言的是「訊息含『用法』」——
兩邊對同一件事寫了不同的話，而且沒有任何守衛在比對它們。第 7 型不對稱記帳。

### 修法

1. **抽一個 `usage()` 函式**，所有用法輸出都走它（>&2）、統一 exit 2。
2. **參數解析先驗值再 shift**，不要靠 `shift 2` 的回傳值：

```bash
usage() {
  cat >&2 <<USAGE
用法:$0 --integration <remote-tracking ref> --fork-sha <FORK_INTEGRATION_SHA>
        [--no-fetch(僅診斷,一律 exit 2)]
USAGE
  exit 2
}

[ $# -eq 0 ] && usage                      # ← 無參數也要印用法（dev-setup 在驗這件事）

while [ $# -gt 0 ]; do
  case "$1" in
    --integration|--fork-sha)
      # 三件一起擋:①後面沒東西 ②值是空字串 ③值長得像另一個旗標(被吞掉)
      [ $# -ge 2 ] || { echo "⛔ $1 後面缺值" >&2; usage; }
      case "${2:-}" in
        ""|--*) echo "⛔ $1 的值不合法:'${2:-}'(不得為空,也不得是另一個旗標)" >&2; usage ;;
      esac
      case "$1" in
        --integration) INTEGRATION_ARG=$2 ;;
        --fork-sha)    FORK_ARG=$2 ;;
      esac
      shift 2 ;;
    --no-fetch) NO_FETCH=1; shift ;;
    *) echo "⛔ 不認得的參數:$1" >&2; usage ;;
  esac
done
```

寫法自訂，但**四件必須成立**：①任何參數排列都不會無限迴圈 ②無參數印用法且 exit 2
③旗標缺值印用法且 exit 2 ④**旗標的值不得是空字串、也不得是另一個 `--*` 旗標**
（否則 `--fork-sha --no-fetch` 會把診斷旗標吞成錨點值，使用者以為開了診斷模式其實沒有）。

⚠️ **正本改完要重新散發到 `docs/dev/tools/`**，parity 守衛會抓（但不要等它抓，自己做）。

⚠️ **不要動 `-- 前置檢查 --` 那段的訊息內容** ——
`check-integration-regression-guard.sh:228` 的 H① 斷言 `"缺 --fork-sha" in out`
還要繼續成立。用法訊息是**追加**，不是取代。

### 驗收（wrapper 新增情境 I）

在 `scripts/check-integration-regression-guard.sh` 新增情境 **I**（用法／參數錯）。
**每一個子案都要帶 5 秒逾時**，逾時即判失敗：

| 子案 | 指令 | 必須得到 |
|---|---|---|
| I① | （無參數） | exit 2 **且訊息含「用法」** |
| I② | `--integration` | exit 2 ＋ 含「用法」 |
| I③ | `--fork-sha` | exit 2 ＋ 含「用法」 |
| I④ | `--integration origin/main --fork-sha` | exit 2 ＋ 含「用法」 |
| I⑤ | `--fork-sha abc --integration` | exit 2 ＋ 含「用法」 |
| I⑥ | `--no-fetch --integration` | exit 2 ＋ 含「用法」 |
| I⑦ | `--integration origin/main --fork-sha --no-fetch` | exit 2 ＋ 含「用法」（**值不得是另一個旗標**） |
| I⑧ | `--bogus` | exit 2 ＋ 含「用法」 |
| I⑨ | `--integration "" --fork-sha "$VALID_FORK_SHA"` | exit 2 ＋ 含「用法」（**空字串不得當值**；SHA 取 fixture 內有效值） |
| I⑩ | `--integration origin/main --fork-sha ""` | exit 2 ＋ 含「用法」（**空字串不得當值**） |

⚠️ **十個子案全部都要，不能只挑兩三個** —— 上一版 brief 只列了「旗標是唯一參數」
那兩種，是因為主線程當時測錯；真正的規律是「**任何需要值的旗標，處理到它時
若已是最後一個參數**」，所以要把 trailing-missing-value 的排列**全部**列進來。

⚠️ **逾時是驗收條件的一部分**（用 `subprocess` 的 `timeout=5` 之類）。
沒有逾時的話，這個 bug 回歸時是**整條 CI 掛住**，不是紅字 —— 比原本更難查。

**破壞實驗（三個 mutant）**：

| mutant | 怎麼改壞 | 哪個子案要抓到 |
|---|---|---|
| M-f · 死迴圈回歸 | 把參數解析換回舊版 `shift 2` 寫法 | **I②~I⑥ 每一個都要因逾時而紅** |
| M-g · 吞旗標 | 只拿掉「值不得是 `--*`」那道檢查 | **I⑦** |
| M-h · 吞空值 | 把空字串錯當成可用預設值（fixture 其餘 ref/SHA 都有效），繞過空值拒絕 | **I⑨、I⑩都要紅** |

任何一個子案沒紅，就是那個排列沒被真的驗到，重做。

---

## A-2〔擋發版〕安裝流程的基準快照拍在散發之前

**位置**：`skills/dev-setup/SKILL.md:49-53`（install 步驟 1 的「基準快照」）

### 錯在哪

步驟 1 的快照包含「**整個 `docs/dev/tools/`**」，但那個目錄要到
**步驟 6**（`:106` evidence gauntlet 散發）和**步驟 7**（`:114` 整合回歸工具散發）
才建立與填內容。

照文件順序執行，步驟 1 拍快照時 `docs/dev/tools/` **還是空的或不存在** →
baseline 沒有任何工具 → 下次 `upgrade` 的三方比對讀到「上游舊 = 沒有這個檔」，
會把官方散發的工具判成**本地客製**，然後跑去問使用者「要不要覆蓋你的自訂內容」。

**上一輪才剛把「tools/ 從來不在 baseline 裡」當既有缺口修掉，結果修出了一個時序上的新洞。**

### 同一段還有第二個 fresh install 故障：目錄根本還沒建

```
:57   cp …/history-append.sh        → docs/dev/tools/history-append.sh
:68   （build-gate-twin.py / devflow_twin_ui.py 兩支也散發到 docs/dev/tools/）
:106  6. evidence gauntlet 散發:`mkdir -p docs/dev/tools` 後 cp …     ← 目錄到這裡才建
```

**照文件順序做 fresh install，前面三支 `cp` 會直接失敗**（parent directory 不存在）。
這不是「以後可能出事」，是**現在照著做就會炸**。

### 修法（四件一起做）

1. **`mkdir -p docs/dev/tools` 移到第一支工具散發之前**（步驟 1 那段），
   步驟 6 那句 `mkdir -p docs/dev/tools` 可以留著（冪等，不會壞），
   但不能只留在那裡。

2. **baseline 的落地時機從步驟 1 移到「五支工具全部散發且最後一項驗證成功之後」**：
   - 步驟 1 只留「等一下要拍哪些東西」的宣告（`README.md` 已剝除版、`_templates/*`、
     `devflow-contract.json`、整個 `docs/dev/tools/`），並明寫**實際落地在最後**。
   - 新增一個收尾步驟（編號接在步驟 7 的**所有驗證之後**），只有步驟 1、6、7
     每一項散發／權限／diff／用法驗證都成功才把上述四項快照到
     `docs/dev/.devflow-baseline/`，並註明理由：tools/ 要到步驟 6、7 才有內容，
     拍早了會讓 upgrade 的三方比對把官方工具誤判成本地客製。
   - 任一驗證失敗 → 不建立新 baseline；upgrade 時舊 baseline 必須原封不動，不能先污染
     快照再報錯。
   - 「五支」是指 `history-append.sh`、`build-gate-twin.py`、`devflow_twin_ui.py`、
     `devflow-evidence-gauntlet.sh`、`devflow-integration-regression.sh`。
     **不要把這個數字寫進文件**（第 7 型），用「`docs/dev/tools/` 底下全部」表述。
3. **upgrade 的 baseline 來源要講清楚**：`upgrade` 段（`:143-150` 附近）講
   「上游舊 blob 的來源」那段要改成 —— 快照的內容必須來自**這次覆蓋下去的上游新內容**，
   **不准把可能已被本地改過的 `docs/dev/` 現況直接抄成 baseline**。
   抄現況的話，本地客製會被記成「上游舊」，下次三方比對就分不出誰改的。
4. **baseline 要用乾淨的新樹取代舊樹，不准 overlay**：先在暫存目錄用本輪
   upstream-new 正本組好完整 baseline，核對成功後再替換
   `docs/dev/.devflow-baseline/`。這樣上游移除工具時不會在 baseline 留下幽靈檔；
   使用者拒絕覆蓋本地客製時，也只影響 `docs/dev/` 現況，**不能改變 baseline 的來源**。

### 驗收

`scripts/check-dev-setup-discipline.sh` 新增**四條**（授權改這支守衛，見硬約束 3）：

| # | 斷言 | 破壞實驗 |
|---|---|---|
| 1 | `mkdir -p docs/dev/tools` 出現在**第一支工具 `cp` 之前**（字元位置比） | 把 mkdir 搬回步驟 6 → 必須紅 |
| 2 | baseline 快照段落出現在**最後一支工具的最後一項驗證成功之後**；不是只在最後 cp/chmod 後 | 把 baseline 插在最後 cp/chmod 與無參數／mode／diff 驗證之間 → 必須紅 |
| 3 | baseline 段落**內部**必須同時出現 `docs/dev/tools/`（這條同時解掉 B-5） | 把段落裡的 `docs/dev/tools/` 拿掉 → 必須紅 |
| 4 | upgrade 的 baseline 更新段落明確綁定 **upstream-new 正本**，並禁止從可能保留客製的 `docs/dev/` 現況取樣 | 把來源改成「從目前 `docs/dev/` 複製」→ 必須紅 |

⚠️ **新增檢查之後兩處數字要同步改**，否則刪掉新檢查照樣綠（第 7 型）：

- `scripts/check-dev-setup-discipline.sh:120` 的 `MIN_CHECKS = 9`
- `scripts/test-architecture-guards.sh:1533` 的靜態互釘
  `check_static_pin "scripts/check-dev-setup-discipline.sh" "MIN_CHECKS = 9" ...`
  —— 它是**逐字比對**，上面不改這裡就會紅；兩處同一個 commit 一起改。

另外，architecture guard 還要依 B-4 的完整規格，釘住
`check-dev-setup-discipline.sh` **真的會非零失敗的整個地板 block**，不只釘常數或
condition。它必須排除註解／字串命中，並能抓到「condition 保留、body 換成 `pass`」。
這裡的兩個 floor mutant 與 B-4 對 dev-setup 的 ②／③共用同一份證據，不重複計數。

數字填**實跑得到的值**，不要照本檔算 —— 跑 `bash scripts/check-dev-setup-discipline.sh`
看它報幾項。

---

## A-3〔擋發版〕Quickstart 教的開 branch 方式，到 Stage 7 一定卡住

**位置**：`guides/guide-quickstart.html:441-455`（Stage 6 的「完整可複製指令」）

### 錯在哪

那段自稱「完整可複製指令」，實際內容是：

```
git checkout -b feature/<slug>
git worktree add -b feature/<slug> <path> ; cd <path>
```

**四件缺的**：`git fetch`、從遠端整合分支的 `$FORK` 建 branch、驗證 `HEAD` 等於 `$FORK`、
保存 `FORK_INTEGRATION_SHA`。

而同一份導覽的 `:488`（Stage 7）要求
`--fork-sha <6-notes 步 0 記的 FORK_INTEGRATION_SHA>` ——
**照 Quickstart 做的人，到 Stage 7 會發現自己根本沒有那個值。**

### 第二個問題：branch 命名互相矛盾

| 位置 | 寫什麼 |
|---|---|
| `:445` Stage 6 | `git checkout -b feature/<slug>` |
| `:412` STATUS 說明 | `Branch` 欄要填 `origin/feat/<slug>` |

`feature/` vs `feat/` —— 照著做的人會填出一個不存在的 ref。

### renderer 會怎麼反應

Quickstart 的 Stage 6 指令是**手寫區**，不在
`scripts/render-methodology-corrections.sh` 的抽取範圍裡，所以只改那一段不會紅。
但下面要求新增的 `_templates/6-implementation-notes.md` 步 0 固定欄位，落在
`template6-checklist` 的抽取範圍；改了它，renderer **一定要先紅**，再用 `--write` 同步。

### 修法

1. Stage 6 先列共用起手式：`git fetch <remote>` → 用
   `git rev-parse --verify <remote>/<integration>^{commit}` 把 40 碼存成 `$FORK` →
   驗證 `$FORK` 是 commit。**fetch 必須在 capture 前面**，兩步不得拆開或倒置。
2. **單一 checkout 動線要完整寫成以下順序**：
   - 從 `"$FORK"` 建 `feat/<slug>`、驗證目前 `HEAD == "$FORK"`；緊接著把 40 碼寫進
     6-notes 固定欄，**只 commit 這個錨點記錄**，再
     `git push -u <remote> feat/<slug>`。這是「開 branch ＋ 持久化錨點」同一個不可拆動作；
     不准只把值留在 shell 變數裡，也不准等 STATUS 交接完才回來補。
   - 切回本地整合分支，依 STATUS 契約把該列 `Branch` 換成已發布的
     `<remote>/feat/<slug>` 並完成該次 commit/push；再切回 `feat/<slug>`。
   - **確認已回到 feature branch**後，才跑 `devflow-exec.sh start`、`status`、
     `devflow-doctor.sh`。此時錨點早已 commit 並發布；不能把未 commit 的 6-notes 變更
     帶去整合分支，也不能留在整合分支上武裝 Stage 6。
3. **worktree 動線也要完整寫成以下順序**：
   - 用 `git worktree add -b feat/<slug> <worktree-path> "$FORK"` 建樹；用
     `git -C <worktree-path> rev-parse HEAD` 驗證那棵樹的 HEAD 等於 `$FORK`；立即在那棵樹
     寫入並只 commit 固定錨點，再從那棵樹
     `git -C <worktree-path> push -u <remote> feat/<slug>`。
   - 回原本的整合 checkout 更新、commit、push STATUS；接著
     `cd <worktree-path>`，確認 cwd/branch，才在 worktree 內跑 start、status、doctor。
4. **`FORK_INTEGRATION_SHA` 要有固定落點**：在
   `_templates/6-implementation-notes.md` 步 0 的輸出區新增逐字欄位
   `FORK_INTEGRATION_SHA: <40 碼>`；Quickstart 也使用同一欄位名，並明說該值就是
   Stage 7 `--fork-sha` 的輸入。不能只把詞藏在說明或註解裡。
5. **branch 命名統一成 `feat/<slug>`**（跟 STATUS 的 `<remote>/feat/<slug>` 對齊）。
   全檔搜一遍 `feature/<slug>`，一併改掉。

### 驗收

renderer 分兩面驗：只改 Quickstart 手寫區時不會紅；新增 template6 固定欄位時**必須紅**，
再跑 `--write` 同步 `guides/guide-dev-flow.html`。最後兩份導覽的 `--check` 都要綠。

由 `scripts/check-status-policy.sh`（它已經在看 quickstart）新增**有作用域、有順序的結構斷言**：

- 先把 Quickstart HTML `html.unescape()`，只解析 Stage 6「完整可複製指令」區塊；
  分別驗單線與 worktree 動線，不准只在全文湊關鍵詞。
- 兩組都要驗 `fetch < capture < 建 branch < 驗 HEAD < 寫錨點 < commit 錨點 < push -u < STATUS 交接 <
  回 feature/worktree < start/status/doctor` 的先後關係。
- 單線的建 branch 命令與 worktree 的 `worktree add` 都必須以 `"$FORK"` 為起點；
  兩路各自的驗證都必須比較 `HEAD == "$FORK"`，其中 worktree 還必須使用
  `git -C <worktree-path>`，不能只跑 rev-parse 卻不比值，也不能驗到原 checkout。
- `_templates/6-implementation-notes.md` 步 0 的輸出區必須有獨立的
  `FORK_INTEGRATION_SHA: <40 碼>` 欄，不接受只在註解或其他段落出現同一字串。
- **unescape 後全檔不得再出現 `feature/<slug>` 這個命名**。

⚠️ **禁字那條要先處理 HTML 轉義**：`guides/guide-quickstart.html` 的原始碼裡
實際存的是 `feature/&lt;slug&gt;`，**不是** `feature/<slug>`。
直接用後者去搜**修之前就會假綠**（搜不到 → 判定通過）。
本輪統一採 `html.unescape()` 後再解析；不要留二選一給執行者。

**破壞實驗（20 個，逐個分開做，不准一次改壞多處互相遮蔽）**：

1. 拿掉 fetch；2. 把 fetch 移到 capture 之後（證明真的比 index，不只驗 presence）。
3. 單線建 branch 拿掉 `"$FORK"`；4. worktree add 拿掉 `"$FORK"`。
5. 只刪單線 `HEAD == "$FORK"` 比較；6. worktree 保留 `git -C ... rev-parse HEAD`、
只刪 `== "$FORK"` 比較；7. worktree HEAD 驗證拿掉 `git -C`。
8. 拿掉 template6 固定欄、只在說明保留同字串；9. 把寫／commit 錨點一起延後到 STATUS 後；
10. 保留寫欄位，只刪 anchor-only commit。
11. 只刪單線 push；12. 只刪 worktree push。
13. 只刪單線 STATUS handoff；14. 只刪 worktree STATUS handoff。
15. 單線不切回 feature 就 start；16. worktree 不 `cd` 就 start。
17. 只刪 start；18. 只刪 status；19. 只刪 doctor。
20. 把 HTML 原始碼某處改回 `feature/&lt;slug&gt;`。

每一個都必須單獨讓守衛紅；尤其 2、9、15、16 是順序 mutant，不能被關鍵詞集合守衛混過去。

---

# 第二批 · 守衛補強（防未來漂移）

## B-1 順序守衛可以被「整段刪掉」繞過

**位置**：`scripts/check-integration-regression-guard.sh:360-366`

```python
i_merge = body.find("合併")
i_test  = body.find("全套測試")
if i_merge >= 0 and i_tool > i_merge: return "..."
if i_test  >= 0 and i_tool > i_test:  return "..."
return None
```

**把「合併」與「全套測試」兩個詞整段刪掉** → 兩個 index 都是 −1 → 兩個判斷都不成立
→ 回 `None` → **綠**。

這是第 4 型假綠：只檢查「有的東西對不對」，沒檢查「**該有的還在不在**」。
這個 repo 已經踩過三次。

**修法**：`i_merge < 0` 或 `i_test < 0` 一律判違規，訊息寫明「條目裡找不到必要動作」。

⚠️ **光這樣還不夠**：那個條目裡有大段解說文字（「合併之後 HEAD 已含對方內容…」
之類），「合併」「全套測試」這些詞在解說裡也會出現，所以**即使把真正的動作刪掉，
`find()` 還是找得到那些詞**，守衛照樣綠。

要定位到**動作本身**，不是隨便哪裡出現的詞：條目裡的
`SYNC_REQUIRED_NO_OVERLAP` / `SYNC_REQUIRED_WITH_OVERLAP` 兩行後面接的就是
「要做什麼」——**在那兩行的範圍內**找「合併」與「全套測試」，找不到就紅。

**破壞實驗（兩個都要）**：
①把那兩行 `SYNC_REQUIRED_*` 後面的「合併…跑全套測試」動作刪掉、**解說文字留著**
→ 必須紅（這一個就是在驗「有沒有真的定位到動作」，只做②會被解說文字騙過去）；
②把整條的順序調換 → 必須紅。

⚠️ ②不能沿用現在那個只有一行的 `BAD_ORDER` fixture。它沒有完整的
`SYNC_REQUIRED_*` 動作行；加完「動作存在」檢查後，就算把順序檢查整段刪掉，它仍會因
缺動作而紅，無法證明順序守衛有效。要把 fixture 補成一個**其餘完全合法、兩個
SYNC_REQUIRED 動作都存在、唯一錯誤只有工具出現在合併／全套測試之後**的完整條目。

## B-2 STATUS 守衛沒釘住「誰做」

**位置**：`scripts/check-status-policy.sh:64`

```python
("ship 移出 Active 由 merger 在合併後做", ["移出", "Active", "合併"]),
```

關鍵詞裡**沒有任何一個指向 actor** —— 把「由合併那個 PR 的人做」改成
「由 owner 做」，三個關鍵詞照樣全中，守衛全綠。

而「誰做」正是 M-2 那一輪要解的核心（owner→merger 交接），釘不住等於沒釘。

**修法**：⚠️ **不要用「加一個 `PR` 關鍵詞」了事** —— 頂註裡別的句子也有 `PR`
（例如「不塞進 feature branch 的 PR」），加了照樣恆真。

兩個受測面結構不同，必須**分開做 scoped assertion**，不能二選一：

1. `_templates/STATUS.md`：解析頂註交接表的 actor 儲存格，斷言 ship 那一列的 actor
   是「合併那個 PR 的人」這個角色，且不含 `owner`。
2. `docs/dev/STATUS.md`：它沒有 actor table，要只取頂註裡「ship 後移出 Active」那一句，
   驗證責任片語；不能在整份頂註找散落的「移出／Active／合併／PR」。

**破壞實驗要分成兩個**：①只把 template 的 actor 改成 `owner`，docs 不動 → 必須紅；
②只把 docs 的責任片語改成 `owner`，template 不動 → 必須紅。不能同時改兩份，否則一面
變紅會遮住另一面仍是假綠。

## B-3 sentinel 是全檔搜尋，不是驗儲存格

**位置**：`scripts/check-status-policy.sh:113`

```python
if "n-a:尚未建立 branch" not in template_text:
```

在**整份模板全文**搜尋 —— 只要檔案任何角落（含頂註的說明文字）有這串字就過，
**Active 範例列那一格根本沒被驗到**。

**修法**：定位到 Active 表的範例列、取 `Branch` 欄那一格，斷言那一格逐字等於 sentinel。
`active_table()` 已經解析出 header/sep/sample 三列了，接著用 header 找 `Branch` 的欄位
index，再取 sample 同 index 的儲存格。

**破壞實驗**：把範例列的 `Branch` 格改成別的字（但頂註說明裡的 sentinel 留著），
確認會紅 —— 舊版在這個情況下是綠的。

## B-4 兩支新守衛自己沒有防砍地板，也不在靜態互釘清單裡

**這條是主線程盤點時發現的，不在 codex 的清單裡。**

`scripts/check-integration-regression-guard.sh` 與 `scripts/check-status-policy.sh`
**都沒有 `MIN_CHECKS` 之類的檢查數地板**（實查：兩個檔都搜不到），
而 `scripts/test-architecture-guards.sh:1533-1542` 的靜態互釘清單也**沒有涵蓋它們**
—— 那份清單目前釘七支，兩支新的沒進去。

**失敗情境**：有人把 wrapper 裡的情境或 mutant 整段刪掉（例如覺得太慢），
檢查數從 24 掉到 5，**沒有任何訊號**；`devflow-check` 照樣全綠。
第 5 型（斷言可被整段刪除而不被發現）＋ 第 7 型（保護長大了、列舉它的清單沒跟著長）。

**修法**：

1. 兩支各加一個檢查數地板常數（照 `check-gate-twin.sh` 的 `MIN_CHECKS` 寫法），
   值設成**本輪做完之後的實得數**（不要憑本檔寫的數字，以實跑輸出為準）。
2. 把兩支加進 `scripts/test-architecture-guards.sh` 的 `check_static_pin` 清單；A-2 那支
   `check-dev-setup-discipline.sh` 既有常數 pin 也要同步更新。
3. ⚠️ **除了釘常數，還要釘「真的會失敗的完整地板 block」** ——
   只釘 `MIN_CHECKS = N` 的話，把 `if checks < MIN_CHECKS: fail` 整段刪掉，
   常數還在、外部互釘照樣綠，地板等於不存在（第 5 型：斷言可被整段刪除）。
   反過來，只釘 `if` condition 也不夠：保留 `if checks < MIN_CHECKS:`、把 body 換成
   `pass`，還是一樣假綠。三支（integration wrapper、STATUS guard、dev-setup discipline）
   都要外釘同一個 scoped block 的三件事：非註解 condition、其縮排 body 會記錄 failure，
   最後確實非零退出。不能用會命中註解／字串的 `check_static_pin_sub` 裸 grep；用逐行
   exact pin／anchored regex 加相鄰與縮排關係，或解析 heredoc 內 Python AST，確定 effect
   真在該 condition 的 body 裡，不是檔案別處剛好有 `exit 1`。
4. `:1589` 那行摘要寫「七支地板/群組數靜態互釘全過」，**數字與名單要跟著改**
   —— 那句話本身就是第 7 型的實例。

**破壞實驗（每支各自做三個，不能一次改三支）**：
①把該守衛裡任一個計數中的 `check(...)`／`need(...)` 刪掉 → 自己的地板必須紅；
②保留常數，只把該守衛的地板 `if` 註解掉或停用 → architecture 靜態互釘必須紅；
③保留 condition，將 body 換成 `pass`／空操作 → architecture 靜態互釘必須紅。
三支各跑①＋②＋③；只刪整段或一次改多支，不能證明每一支真的有被保護。

## B-5 `check-dev-setup-discipline.sh` 只驗字串存在，不驗綁定

**位置**：`scripts/check-dev-setup-discipline.sh:80`

```python
need("docs/dev/.devflow-baseline/" in src, "...")
```

只驗這個字串**有沒有出現在 SKILL.md 全文**，不驗它跟本輪新增的
「整個 `docs/dev/tools/`」有沒有綁在一起。

**失敗情境**：把 baseline 段改回舊版三項列舉（漏掉 `docs/dev/tools/`），
這支守衛仍全綠 —— 因為同一字串在「過渡態」等其他段落還在。

**修法**：斷言改成「baseline 段落內必須同時出現 `docs/dev/tools/`」，
不是全文任一處出現即可。與 A-2 的順序檢查放在一起做。

**破壞實驗**：把 baseline 段裡的 `docs/dev/tools/` 拿掉，確認會紅。

---

# 第三批 · 模板與文件的三個缺口

## C-1 worktree 建好之後沒說要切進去

**位置**：`_templates/6-implementation-notes.md:33-38`

四步用 `git -C <worktree-path>` 驗證（這是對的），但**後面沒有 `cd <worktree-path>`**。
接下來的 `devflow-exec.sh status`、`devflow-doctor.sh` 可能還在**原 checkout** 執行，
而 `status` 正是用來確認「slug 與 cwd 相符」的 —— 在錯的目錄跑，它驗的是別人。

有趣的是 `guides/guide-quickstart.html` 那邊反而寫了「建完務必 cd 進去」——
**模板缺、導覽有**，兩邊不一致。

**修法**：四步之後加一個明確的交接動作：

```bash
cd <worktree-path>          # 從這裡開始,後續所有指令都在這棵樹上跑
```

並加一句：**後面的 `devflow-exec.sh status` 必須在這個目錄下跑**，
它會核對 slug 與 cwd 相符 —— 在原 checkout 跑會核對到別的東西。

⚠️ **C-1 改的是 renderer 管轄範圍內的區塊，一定要跑 `--write`。**
`scripts/render-methodology-corrections.sh:136` 的 `template6-checklist` 抽的是
`_templates/6-implementation-notes.md` 的「執行清單(」到「實作期規則(」之間
（步 0 在 `:22-71`，落在這個範圍裡）。所以流程是：

```
改模板 → --check 必須變紅（紅的是 guides/guide-dev-flow.html）
      → --write 同步 → --check 回綠
```

**C-1 或 A-3 固定欄改完後該紅沒紅 → 停下回報，不要自己去改 html。**
（「不會紅」只適用 **A-3 的 Quickstart 手寫區** —— 那一段確實不在 renderer 範圍。
三個面的差別在驗收節有一張對照表。）

## C-2 STATUS 的遠端 ref 會過期，導致補修判準算出假的「零交集」

**位置**：`_templates/STATUS.md:41-46`（`Branch` 欄填法）
＋ `README.md:631-640`（用那個 ref 算「其他 feature 碰過的檔」）

`Branch` 欄只規定「branch 推上去之後換成遠端 ref」，
**沒規定後續每個 T commit 什麼時候 push**。而 README 拿那個 remote ref 算聯集。

**失敗情境**：某個 feature 本地有三個已 ACCEPTED 但沒推的 T commit，
它們改的檔不在 remote ref 的 diff 裡 → 聯集少算 → 補修被判成「零交集、可以直接補修」
→ 補修撞上那個 feature 正在改的檔。

### ⚠️ 「SHA 要相等」這個寫法不成立，不要照它做

本檔上一版寫「核對 remote ref 的 SHA **與最新 ACCEPTED commit 一致**」，
那在真實流程裡永遠對不上，三個實查到的理由：

| 事實 | 位置 |
|---|---|
| hash 記在 **Progress Log**，不是 TDD Evidence（上一版寫錯了） | `_templates/6-implementation-notes.md:147-148` |
| sequential 在最後一個 T 之後**還有一個 bookkeeping commit** → remote tip 正常就是 T commit 的**後代**，不會相等 | `skills/dev-run/SKILL.md:36`、`:112` |
| parallel 的 commit 先進 `integration/<slug>`，**最後才合回 feature branch** | `skills/dev-run/SKILL.md:122`、`:132`、`:215-217` |

還有一件更根本的：**`skills/dev-run/SKILL.md` 全文沒有任何 `git push`**
（實查零命中）。所以「只改 `STATUS.md` 與 `README.md`」**不會讓 dev-run 真的去推** ——
規則寫了也沒人執行。

### 修法（六件；判準已寫死，不留二選一）

1. README 逐列判定的順序寫死：**Stage 1–5 且 Branch 是 canonical sentinel 就跳過；
   Stage 6 一律 fail-closed；只有 Stage 7 才進 mode／ref／SHA 驗證**。Active 表只要
   還有另一個 feature 的 `Stage` 是
   `6-implementation`（或同義的 Stage 6 值），就不准用「直接補修」判準；此時本地可能
   還有未 commit／未發布工作，remote 天生不能證明完整戰場。不要嘗試靠猜最新 T 補洞。
2. Stage 7 先 fetch，將該列 `Branch` remote ref 用 `rev-parse --verify` 釘成單一
   `<remote-tip>`；後續 mode、Progress Log 與 diff **全部讀這個 SHA，不准讀目前 main
   checkout 裡可能尚未合併的舊副本**。`Feature` 連結只用來導出該 feature 的相對路徑；
   兩份文件分別用 `git show <remote-tip>:docs/dev/<slug>/5-tasks.md` 與
   `git show <remote-tip>:docs/dev/<slug>/6-implementation-notes.md`（或同等的 pinned-tree
   讀法）取得。任一路徑不存在、逃出 feature 目錄或讀取失敗都 fail-closed。
3. **sequential 到 Stage 7 才可計算**：從上一步 pinned remote tree 的 6-notes
   **Progress Log** 讀出每個 ACCEPTED T 的 commit；每一個都必須通過
   `git merge-base --is-ancestor <accepted-sha> <remote-tip>`。remote tip 可以是
   bookkeeping commit 的後代，**不要求 SHA 相等**。Progress Log 缺失、SHA 解析失敗、
   任一 SHA 未包含於 remote tip，都 fail-closed。
4. **parallel 一律 fail-closed**：本輪不碰 T 級並行機制，也不猜
   `integration/<slug>` 與 feature branch 哪個才是補修計算的 canonical ref。
   判斷 Stage 7 列的 mode，唯一資料源不是 STATUS 的 `Lane` 欄（full/fast 跟
   sequential/parallel 是兩件事），而是：從上一步 pinned remote tree 讀該 feature 的
   `5-tasks.md` frontmatter `execution.mode`；整塊缺省視為 `sequential`，明寫
   `parallel` 就停，連結／檔案／frontmatter 無法解析也停。把「定義 parallel 的
   canonical integration ref」記進 Backlog。
5. **`skills/dev-run/SKILL.md` 是發布紀律的執行正本**，本輪明定：
   - sequential：最後 bookkeeping commit 完成後、`stop`／回報 Stage 7 **之前**，
     push feature branch，fetch 後驗遠端 tip 等於當下 feature HEAD；失敗就停，不得宣稱
     Stage 6 完成。
   - parallel：integration branch 依既有動線合回 feature branch後、回報 Stage 7
     **之前**，push feature branch並做同一個 remote-tip 驗證。
   這只是補「Stage 6 最終成果何時發布」，不改 execution mode、wave 或 T 整合機制。
6. `_templates/STATUS.md` 的 `Branch` 說明要同步交代：Stage 6 開始時先發布 ref 是為了
   建立可查座標，**不代表執行中的 remote 已完整**；Stage 6 收尾由 dev-run 再發布最終
   feature tip。README 的直接補修算法負責用 Stage 6 fail-closed 與 Stage 7 的
   ancestor 證據封住其他 feature 的未發布窗口；執行補修者自己的 checkout 也必須
   clean、無 ahead 未推 commit，任一條無法觀測就不准算完宣稱零交集。

### 驗收

`scripts/check-status-policy.sh` 要對三個正本分別做 scoped assertion，不能只驗 README：

1. README 的直接補修算法必須同時釘住：Stage 1–5 sentinel 才跳過 → Stage 6
   fail-closed → Stage 7 才讀 mode/ref 的順序；Stage 7 先把 Branch ref 釘成 SHA，
   再從**同一個 pinned remote tree**讀 `5-tasks.md` 與 6-notes（不得讀 main checkout，
   也不得把 `Lane` 當 mode）；parallel fail-closed；
   sequential 對 Progress Log 的**每一個** ACCEPTED SHA 用 `--is-ancestor`；補修者自己的
   checkout clean 且無 ahead 未推 commit；不得只查最新一個，也不得要求 SHA 相等。
2. `skills/dev-run/SKILL.md` 的 sequential 收尾必須在 bookkeeping 後、stop／回報前
   發布並驗 remote tip；parallel 收尾必須在 integration 合回 feature 後、回報前做同一件事。
   兩邊都要驗「push 的位置」與「fetch 後 remote tip 等於 feature HEAD」，不是只找 `push` 字。
3. `_templates/STATUS.md` 的 Branch 段必須同時說明「起手發布座標」與「Stage 6 收尾再發布
   最終 tip」，不能只有第一次 push。

**破壞實驗（20 個分開做）**：

1. 拿掉 Stage 1–5 的 sentinel 等值條件，讓異常 Branch 也被跳過。
2. 拿掉 Stage 6 fail-closed；3. 把 Stage 6／Stage 7 判定段倒序。
4. 拿掉 fetch；5. 只把 `5-tasks.md` 改成從 main checkout 讀；
6. 只把 6-notes 改成從 main checkout 讀；7. 讀第二份文件前重新 resolve ref，
讓兩份可能來自不同 SHA。
8. 把 mode 資料源改成 STATUS `Lane`；9. 只刪 parallel fail-closed；
10. 把「每個 ACCEPTED」弱化成只查最新一個；11. 把 ancestor 改回 SHA 相等。
12. 只刪 sequential 最終 push；13. 把 sequential push 搬到 bookkeeping 之前；
14. 只刪 sequential 的 remote-tip 驗證。
15. 只刪 parallel 最終 push；16. 把 parallel push 搬到 integration 合回 feature 之前；
17. 只刪 parallel 的 remote-tip 驗證。
18. 只刪補修者 checkout clean 檢查；19. 只刪 ahead／未推檢查。
20. 只刪 STATUS Branch 段的 Stage 6 最終 tip 發布說明。

每次只改一件並恢復後再做下一件；每個 mutation 都必須單獨讓守衛紅。

## C-3 sentinel 的冒號正本定案

**owner 已裁決：用半形 `n-a:尚未建立 branch`。**

實作已經全面使用半形、全庫一致；`notes/dispatch-v380-blockers.md:687` 寫的是全形，
**改那一份的那一行**（那是規格檔，要跟實作對齊），其餘不動。

⚠️ 這是本輪唯一准許修改 `notes/dispatch-v380-blockers.md` 的地方。

---

## 做完之後的驗收（全部都要跑，輸出貼進回報）

```bash
bash scripts/devflow-check.sh all                          # REPO_REFERENCE_PASS 全過
bash scripts/render-methodology-corrections.sh --check     # 見下面那段,分兩階段
bash hooks/selftest.sh                                     # 全過（項數以輸出為準）
env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
bash hooks/devflow-exec.sh doctor                          # COMPATIBLE
bash scripts/check-gate-twin.sh                            # 全過
bash scripts/check-integration-regression-guard.sh         # 全過（項數會比 24 多）
bash scripts/check-status-policy.sh                        # 全過（項數會比 6 多）
bash scripts/check-file-map.sh                             # scanned=77 不變（本輪不新增腳本）
bash scripts/check-dev-setup-discipline.sh                 # 全過（項數會比 9 多，見 A-2）
```

⚠️ **renderer 那道要分兩階段看，不是一句「必須綠」**：

| 改了什麼 | `--check` 該不該紅 |
|---|---|
| **C-1**（`_templates/6-implementation-notes.md` 步 0） | ✅ **必須先紅**（`template6-checklist` 抽的就是那一段），跑 `--write` 同步 `guides/guide-dev-flow.html` 後回綠 |
| **A-3 的 template6 固定欄位**（`_templates/6-implementation-notes.md` 步 0） | ✅ **必須先紅**，它與 C-1 同屬 `template6-checklist`；同一輪 `--write` 後回綠 |
| **A-3 的 Quickstart 指令**（`guides/guide-quickstart.html` Stage 6 手寫區） | ❌ 單改這一面不會紅，那段不在 renderer 範圍 —— 由 STATUS guard 驗，不要為了讓 renderer 紅去改別處 |

**C-1／A-3 template 欄改完 `--check` 沒紅 → 停下回報**，那表示 fragment 範圍跟預期不同，不要自己改 html。
最終狀態是 `--write` 之後 `--check` 全綠。

另外還要確認：

- `diff -q scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh` 靜默
- 兩邊都還是 755
- `git status --short` 為空
- **版號仍是 3.8.0**（兩處都是）
- `git diff --check` 無輸出

### 手動的散發路徑演練（**這一輪必做，不准跳過**）

建立一個**全新的拋棄式 git repo**，起手先證明 `docs/dev/tools/` 不存在；
`CLAUDE_PLUGIN_ROOT` 指向本工作樹。這是工具散發路徑 fixture，**不是完整 install 演練**：
逐字、依原順序執行 `skills/dev-setup/SKILL.md` install 步驟 1 內的所有命令，再執行
步驟 6、7 與新增的 baseline 收尾；步驟 2–5 與本缺陷無關且含 AskUserQuestion，fixture
明文跳過，不得在這輪臨時問 owner。步驟 6/7 需要的前置檔由 fixture 預先建好並在回報
列出，不能靠跑步驟 6 自己的 mkdir 遮掉步驟 1 故障。至少留下以下證據：

1. 第一支工具 cp 前 parent 已建立；步驟 1 裡的三支工具與步驟 6、7 的工具都成功散發。
2. 散發完成後，`docs/dev/tools/` 與 baseline 的 tools 樹在**檔名集合、內容、可執行位元**
   三面完全一致；不能只證明「裡面至少有一支」。驗證必須動態掃描，不把工具數寫死。
3. check 第 12 項的三個子項（存在＋可執行位元一致、與正本 diff、無參數印用法 exit 2）。
4. 再做一個 upgrade fixture：準備 upstream-old baseline、修改一支本地工具形成 local-custom、
   再提供 upstream-new；選擇「保留本地客製」後，確認 `docs/dev/` 仍是 local-custom，
   但新 baseline 取自 upstream-new、不是本地現況。接著再模擬下一次 upgrade，證明三方比對
   仍把 local-custom 辨識為客製。
5. 模擬 upstream-new 移除一支工具，確認 baseline 是乾淨替換而非 overlay，舊工具不殘留。
6. 做一個 failure-path fixture：故意讓步驟 7 的最後一項驗證失敗；fresh install 不得建立
   baseline，upgrade 則舊 baseline 的 tree hash 必須前後相同。修好 fixture 再重跑才可落地。

⚠️ **這一步就是 A-1 那個缺陷被逼出來的方式** ——
母版內部的守衛全綠，照文件實走才會發現。把每一步的實際輸出貼進回報。

### 收尾（**有先後順序，照著走；順序錯會違反 STATUS 自己的契約**）

`docs/dev/STATUS.md:10-19` 現在明文寫著：**本檔只在 `main` 上維護，feature branch
內一律不碰**，而且「只改自己那一列 → 立刻 commit → 立刻推」。本 repo 又有一條
owner 明定且 agent 不得繞過的 push 護欄，因此本輪採用**唯一、窄範圍的 owner-push
handoff 例外**：agent 在 `main` 完成 STATUS commit 與最終驗收後立刻停下，owner 接手
唯一的 push。handoff 窗口內不得有第二個 session 修改 STATUS／main；這是明文例外，
不是假裝已符合「agent 立刻推」。

| # | 做什麼 | 在哪條 branch |
|---|---|---|
| 1 | 完成 A/B/C 十一項的實作 ＋ 所有破壞實驗 | `fix/v380-landing`（**不准碰 `docs/dev/STATUS.md`**） |
| 2 | 切回 `main`，先 `git fetch origin` ＋ `git pull --ff-only origin main`；不通過就停，不准在 stale main 上 merge | `main` |
| 3 | `git merge --no-ff fix/v380-landing` 回 `main` | `main` |
| 4 | 用唯一 writer 追加 HISTORY ＋ 改 STATUS Backlog，立刻 commit | `main` |
| 5 | **從最終的 `main` HEAD 重跑一次全套驗收**（第 1 步跑過的不算，樹已經變了） | `main` |
| 6 | **停下回報，請 owner 立刻跑 `git push origin main`** | — |

⚠️ 第 6 步不要自己推 —— owner 的設定擋掉了 agent 推 main，那是刻意的護欄。
在 HISTORY 那筆裡寫明本輪使用 owner-push handoff。若 owner push 被拒，**不要 force、
不要 rebase 整合分支**（README §7 明文禁止）：把執行 session 叫回來，
`git fetch origin` 後在本地 `main` 用一般 merge 把新的 `origin/main` 合進來；不得 reset、
force-push 或改寫既有歷史。若有衝突，HISTORY 保留兩邊 append-only 條目，STATUS 取兩邊
Backlog／Active 列集合的聯集並逐列核對。從這個新的 merge HEAD 重跑第 5 步；全綠後
owner 才重試 push。若重試前 origin 又前進，就重複 fetch → merge → 核對 → 全套，
push 成功前不准宣稱本輪已發布。

⚠️ **不打 tag、不發 release。** push 成功之後才輪到 dogfood。

具體要寫的東西：

- `scripts/history-append.sh` 追加一筆，`--version` 帶 **`v3.8.0`**
  （這一輪修的仍是一個還沒發布出去的版本，不是後續 patch）
- **`docs/dev/STATUS.md` 的 Backlog 加兩條 B 級**（第 4 步、在 `main` 上做）：

  > 定義 parallel feature 供「直接補修」計算的 canonical integration ref，並把它變成
  > 可由 STATUS／runtime 提供的單一座標；在這件事完成前，Active 裡只要有
  > `execution.mode: parallel` 就 fail-closed，不宣稱零交集。
  > 來源：本派工單 C-2。

  > 把「整合回歸與同步」移到 Final Fresh Run／雙軸審查／Verdict **之前**。
  > 現在的節序是 Final Fresh（`_templates/7-review.md:94`）→ Verdict（`:133`）
  > → Exit Checklist 的整合同步（`:281`），所以**審過並核准的那棵樹，
  > 不是最後出貨的那棵樹** —— Exit 階段合併 `INTEGRATION_SHA` 之後 HEAD 就變了。
  > 而且 `ALREADY_SYNCED`（`:291`）只說「證據不算數」，沒有給恢復路徑。
  > **owner 已裁決：獨立成 feature 走完整七站，並拿它當第一個真實 full lane 的題目**
  > —— 它動的是模板節序，是母版最核心的結構，而且會影響 gate-consistency 的機械錨點，
  > 不該塞進發版前的補丁。

- Backlog 補完後應該是 **12 條**（原 10 ＋ 上面兩條）。整張表貼進回報；
  如果不是 12，先逐列找出少了／重複了哪一條，不准硬改預期數字配合現場。

---

## 不要做

- 不要 bump 版號到 3.8.1
- 不要動 Stage 1–4 模板
- **不要新增任何腳本檔**（本輪全是修既有檔；想新增就是偏離範圍，停下回報）
- **本輪不要修改 `_templates/7-review.md`**。B-1 改的是既有條目的守衛；節序調整是
  Backlog 那條獨立 feature 的事
- **不准在工作 branch 上碰 `docs/dev/STATUS.md`** —— 它只在 `main` 上改，
  動線見「收尾」節。上一輪的 bootstrap 例外**不適用本輪**；本輪唯一例外只有收尾明文
  定義的 owner-push handoff，且不改變「STATUS 只在 main 編輯」
- 不要碰 `notes/dispatch-v380-blockers.md` 除了 C-3 那一行以外的任何內容
- 不要順手收 `docs/dev/engine-fence-masking/7-review.md` 的文書
- 不要動 `execution.mode: parallel` 那套 T 級並行機制
- 不要為了讓某個檢查變綠而放寬它

---

## 回報格式

1. 十一項（A-1~A-3 / B-1~B-5 / C-1~C-3）各一段：改了哪些檔（`檔案:行號`）、
   實際跑了什麼指令、輸出原文。
2. 驗收那十道的輸出原文全貼，renderer 要貼**改完（紅）與 `--write` 之後（綠）兩次**。
3. **手動散發路徑演練**的每一步輸出原文 —— fresh install／exact tree parity／
   check 12／保留 local-custom 的 upgrade／上游移除工具／最後驗證失敗不污染 baseline，
   這六面都要交代。它們是行為 fixture，不是「預期變紅」的 mutant，不能用「照做了」帶過。
4. 破壞實驗逐個列，一個都不能少：
   A-1 的 M-f（**I②~I⑥ 每個都要因逾時而紅**）／M-g／M-h；A-2 四個 scoped
   斷言 mutant；
   A-3 20 個；B-1 兩個；B-2 兩個；B-3 一個；B-4 三支守衛各三個；
   B-5 併入 A-2 第 3 條；C-2 20 個。A-2 提到的 dev-setup 地板實驗與 B-4 的
   dev-setup ②／③是同一份證據，可交叉引用，不要重跑後假裝成兩個不同 mutant。
   每個都要寫「弄壞什麼 → 有沒有真的變紅」。**沒做破壞實驗的守衛一律當成沒做**。
5. `docs/dev/STATUS.md` 的 Backlog 整張表貼出來，說明是幾條（預期 12）。
6. 有沒有發現本檔沒提到的問題 —— 列出來問要不要處理，**不要自己動手**。

**每一個結論都要對應到你自己實際跑過的指令與看到的輸出。**
沒跑過的就寫「未驗證」，不准用推論代替。
