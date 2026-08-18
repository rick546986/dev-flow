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
   **A-1、A-2、A-3、B-1~B-5**（A 批各自要動 integration wrapper／dev-setup discipline
   guard／STATUS guard），方向一律是**收緊**，不准放寬。
   這八項以外的守衛一個字都不要動。
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

⚠️ **八個子案全部都要，不能只挑兩三個** —— 上一版 brief 只列了「旗標是唯一參數」
那兩種，是因為主線程當時測錯；真正的規律是「**任何需要值的旗標，處理到它時
若已是最後一個參數**」，所以要把 trailing-missing-value 的排列**全部**列進來。

⚠️ **逾時是驗收條件的一部分**（用 `subprocess` 的 `timeout=5` 之類）。
沒有逾時的話，這個 bug 回歸時是**整條 CI 掛住**，不是紅字 —— 比原本更難查。

**破壞實驗（兩個 mutant）**：

| mutant | 怎麼改壞 | 哪個子案要抓到 |
|---|---|---|
| M-f · 死迴圈回歸 | 把參數解析換回舊版 `shift 2` 寫法 | **I②~I⑥ 每一個都要因逾時而紅** |
| M-g · 吞旗標 | 只拿掉「值不得是 `--*`」那道檢查 | **I⑦** |

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

2. **baseline 的落地時機從步驟 1 移到「五支工具全部散發並驗證成功之後」**：
   - 步驟 1 只留「等一下要拍哪些東西」的宣告（`README.md` 已剝除版、`_templates/*`、
     `devflow-contract.json`、整個 `docs/dev/tools/`），並明寫**實際落地在最後**。
   - 新增一個收尾步驟（編號接在步驟 7 之後），把上述四項快照到
     `docs/dev/.devflow-baseline/`，並註明理由：tools/ 要到步驟 6、7 才有內容，
     拍早了會讓 upgrade 的三方比對把官方工具誤判成本地客製。
   - 「五支」是指 `history-append.sh`、`build-gate-twin.py`、`devflow_twin_ui.py`、
     `devflow-evidence-gauntlet.sh`、`devflow-integration-regression.sh`。
     **不要把這個數字寫進文件**（第 7 型），用「`docs/dev/tools/` 底下全部」表述。
3. **upgrade 的 baseline 來源要講清楚**：`upgrade` 段（`:143-150` 附近）講
   「上游舊 blob 的來源」那段要改成 —— 快照的內容必須來自**這次覆蓋下去的上游新內容**，
   **不准把可能已被本地改過的 `docs/dev/` 現況直接抄成 baseline**。
   抄現況的話，本地客製會被記成「上游舊」，下次三方比對就分不出誰改的。

### 驗收

`scripts/check-dev-setup-discipline.sh` 新增**三條**（授權改這支守衛，見硬約束 3）：

| # | 斷言 | 破壞實驗 |
|---|---|---|
| 1 | `mkdir -p docs/dev/tools` 出現在**第一支工具 `cp` 之前**（字元位置比） | 把 mkdir 搬回步驟 6 → 必須紅 |
| 2 | baseline 快照段落出現在**最後一支工具散發段落之後** | 把 baseline 段搬回步驟 1 → 必須紅 |
| 3 | baseline 段落**內部**必須同時出現 `docs/dev/tools/`（這條同時解掉 B-5） | 把段落裡的 `docs/dev/tools/` 拿掉 → 必須紅 |

⚠️ **新增檢查之後兩處數字要同步改**，否則刪掉新檢查照樣綠（第 7 型）：

- `scripts/check-dev-setup-discipline.sh:120` 的 `MIN_CHECKS = 9`
- `scripts/test-architecture-guards.sh:1533` 的靜態互釘
  `check_static_pin "scripts/check-dev-setup-discipline.sh" "MIN_CHECKS = 9" ...`
  —— 它是**逐字比對**，上面不改這裡就會紅；兩處同一個 commit 一起改。

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

### 為什麼 renderer 6/6 還是綠

這段是**手寫區**，不在 `scripts/render-methodology-corrections.sh` 的抽取範圍裡
（`fragments` 字典沒有對應的 key）。所以模板怎麼改，這裡都不會自動同步、也不會紅。

### 修法

1. Stage 6 那段指令改成與 `_templates/6-implementation-notes.md:29-38` **同一組四步**
   （單線一組、worktree 一組，worktree 那組的驗證要帶 `git -C <worktree-path>`），
   並加上「把 `$FORK` 那 40 碼寫進 6-notes 步 0」這一步。
2. **`git push -u <remote> feat/<slug>`** 也要在那段裡 ——
   `STATUS.md` 的 `Branch` 欄要填 `origin/feat/<slug>`，**不推的話那個 ref 根本不存在**，
   後面算補修判準會靜默漏掉這個 feature（C-2 講的就是這條線）。
3. **回整合 checkout 更新 STATUS 的動線**要寫出來：`STATUS.md` 只在 `main`／`develop`
   上維護，所以「加列／換 `Branch` 欄」要切回整合分支做，不是在 worktree 裡改。
   照現在的 Quickstart，使用者會在 worktree 裡改 STATUS —— 那正是規則禁止的事。
4. **`FORK_INTEGRATION_SHA` 要有固定的落點**：不能只說「寫進 6-notes」，
   要指名寫進步 0 輸出區的哪一個欄位（例如一行 `FORK_INTEGRATION_SHA: <40 碼>`），
   `_templates/6-implementation-notes.md` 與 Quickstart 兩邊用**同一個欄位名**。
5. **`devflow-doctor.sh` 放進那段「完整可複製指令」** —— 步 0 已經把它列為硬關卡
   （版本握手 fail-closed），Quickstart 自稱完整卻沒有它。
6. **branch 命名統一成 `feat/<slug>`**（跟 `:412` 的 `origin/feat/<slug>` 對齊）。
   全檔搜一遍 `feature/<slug>`，一併改掉。
7. Stage 6 那段加一句指回 Stage 7：「這個 `FORK_INTEGRATION_SHA` 是 Stage 7
   整合回歸要用的，現在不記，到時候會卡住。」

### 驗收

⚠️ **`render-methodology-corrections.sh --check` 不會紅** —— 那段不在抽取範圍，
這是正常的，不要為了讓它紅而去改別的東西。

改成由 `scripts/check-status-policy.sh`（它已經在看 quickstart）新增兩條：

- quickstart 的 Stage 6 指令區塊必須同時含：`git fetch`、`FORK`、`push -u`、
  `FORK_INTEGRATION_SHA`、`doctor`（用關鍵詞組，不要逐字釘整段 —— 會天天假紅）
- **全檔不得再出現 `feature/<slug>` 這個命名**

⚠️ **禁字那條要先處理 HTML 轉義**：`guides/guide-quickstart.html` 的原始碼裡
實際存的是 `feature/&lt;slug&gt;`，**不是** `feature/<slug>`。
直接用後者去搜**修之前就會假綠**（搜不到 → 判定通過）。
做法二選一：讀進來先 `html.unescape()` 再搜，或者直接搜轉義後的字面。
**選哪一種都要做一次破壞實驗證明它真的抓得到。**

**破壞實驗**：①把 `git fetch` 從 quickstart 拿掉 → 必須紅；
②把某處改回 `feature/<slug>`（**寫成 HTML 裡真正的樣子**）→ 必須紅。

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
②把整條的順序調換 → 必須紅（既有的負向 fixture）。

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

要釘的是**那個責任歸屬的句子本身**，兩條路擇一：
①解析交接表的 actor 儲存格（`_templates/STATUS.md` 頂註那張表有「什麼時候｜誰改」兩欄），
斷言 ship 那一列的 actor 格含「合併」且**不含**「owner」；
②釘一個唯一的 actor 片語（例如「合併那個 PR 的人」）—— 但要先確認它在頂註裡
**只出現一次**，否則又是恆真。

**破壞實驗**：把兩份 STATUS 裡 ship 那一列的 actor 從「合併那個 PR 的人」
改成「owner」（**其餘一個字不動**），確認會紅。

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
2. 把兩支加進 `scripts/test-architecture-guards.sh` 的 `check_static_pin` 清單。
3. ⚠️ **除了釘常數，還要釘「真正在用它的那一行」** ——
   只釘 `MIN_CHECKS = N` 的話，把 `if checks < MIN_CHECKS: fail` 整段刪掉，
   常數還在、外部互釘照樣綠，地板等於不存在（第 5 型：斷言可被整段刪除）。
   用 `check_static_pin_sub` 之類把那個**執行判斷式**也釘住。
4. `:1589` 那行摘要寫「七支地板/群組數靜態互釘全過」，**數字與名單要跟著改**
   —— 那句話本身就是第 7 型的實例。

**破壞實驗（兩個都要）**：
①把 wrapper 裡任一個情境函式的 `check(...)` 刪掉 → 地板必須紅；
②**把地板的 `if` 判斷整段刪掉、常數留著** → 靜態互釘必須紅
（只做①的話驗不到第 3 點）。

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

**該紅沒紅 → 停下回報，不要自己去改 html。**
（「不會紅」只適用 **A-3 的 Quickstart 手寫區** —— 那一段確實不在 renderer 範圍。
兩者的差別驗收節有一張對照表。）

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

### 修法（三件）

1. **sequential**：判準改成「最新 ACCEPTED 的 commit **是** remote tip 的祖先」
   （`git merge-base --is-ancestor <accepted-sha> <remote-tip>`），**不要求相等**。
   bookkeeping commit 是正常的後代，相等是錯的期望。
2. **parallel**：本輪硬約束不准碰 T 級並行機制，所以**不要**去改 `integration/<slug>`
   的動線。改成：`STATUS.md` Active 表裡**只要有任何一個 feature 是 parallel**，
   「直接補修」就 **fail-closed 停下問人** —— 因為 canonical ref 在 parallel 下是哪一條
   （feature branch 還是 `integration/<slug>`）本輪沒有定義，沒定義就不准算。
   把「定義 parallel 的 canonical integration ref」記進 Backlog。
3. **`skills/dev-run/SKILL.md` 是執行正本，push 紀律要寫在那裡**（不是只寫在
   `STATUS.md` 與 `README.md`）：sequential 的 bookkeeping commit 之後要推、
   或每個 ACCEPTED commit 之後推，擇一寫死。
   ⚠️ 這是**加一條 push 紀律**，不是改並行機制 —— 不要動 `execution.mode` 那套東西。
4. 不論哪一種：**還有未 commit 或未推的 T 時，一律 fail-closed**，
   不准算完宣稱零交集。

### 驗收

`scripts/check-status-policy.sh` 新增一條：`README.md` 的補修判準段落必須同時出現
「祖先」（或 `--is-ancestor`）與 parallel 的 fail-closed 條件 ——
**不得再出現「SHA 相等」這種表述**。

**破壞實驗**：把那段改回「SHA 必須相等」→ 必須紅。

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
| **A-3**（`guides/guide-quickstart.html` 的 Stage 6 手寫區） | ❌ 不會紅，那段不在 renderer 範圍 —— 這是正常的，不要為了讓它紅去改別的東西 |

**C-1 改完 `--check` 沒紅 → 停下回報**，那表示 fragment 範圍跟預期不同，不要自己改 html。
最終狀態是 `--write` 之後 `--check` 全綠。

另外還要確認：

- `diff -q scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh` 靜默
- 兩邊都還是 755
- `git status --short` 為空
- **版號仍是 3.8.0**（兩處都是）
- `git diff --check` 無輸出

### 手動的散發路徑演練（**這一輪必做，不准跳過**）

在拋棄式目錄裡照 `skills/dev-setup/SKILL.md` 的步驟**逐字執行**
（`CLAUDE_PLUGIN_ROOT` 指向本工作樹），至少涵蓋：

1. 步驟 6、7 的散發 ＋ 可執行驗證
2. 新增的 baseline 收尾步驟 —— 確認快照裡**真的有** `docs/dev/tools/` 的內容
3. check 第 12 項的三個子項（存在＋可執行位元一致、與正本 diff、無參數印用法 exit 2）

⚠️ **這一步就是 A-1 那個缺陷被逼出來的方式** ——
母版內部的守衛全綠，照文件實走才會發現。把每一步的實際輸出貼進回報。

### 收尾（**有先後順序，照著走；順序錯會違反 STATUS 自己的契約**）

`docs/dev/STATUS.md:10-19` 現在明文寫著：**本檔只在 `main` 上維護，feature branch
內一律不碰**，而且「只改自己那一列 → 立刻 commit → 立刻推」。
上一輪用過一次性的 bootstrap 例外（規則那時還沒生效），**這一輪不能再用** ——
規則已經在了，本輪自己就要照它走。所以：

| # | 做什麼 | 在哪條 branch |
|---|---|---|
| 1 | 完成 A/B/C 十一項的實作 ＋ 所有破壞實驗 | `fix/v380-landing`（**不准碰 `docs/dev/STATUS.md`**） |
| 2 | `git merge --no-ff` 回 `main` | — |
| 3 | 在 **`main` 上**追加 HISTORY ＋ 改 STATUS Backlog，commit | `main` |
| 4 | **從最終的 `main` HEAD 重跑一次全套驗收**（第 1 步跑過的不算，樹已經變了） | `main` |
| 5 | **停下回報，請 owner 自己跑 `git push origin main`** | — |

⚠️ 第 5 步不要自己推 —— owner 的設定擋掉了 agent 推 main，那是刻意的護欄。
STATUS 契約說的「立刻推」在本 repo 由 owner 執行，**在 HISTORY 那筆裡寫一句
說明這個落差**（本 repo 的 push 護欄），免得下一個人以為規則被違反了。

⚠️ **不打 tag、不發 release。** push 成功之後才輪到 dogfood。

具體要寫的東西：

- `scripts/history-append.sh` 追加一筆，`--version` 帶 **`v3.8.0`**
  （這一輪修的仍是一個還沒發布出去的版本，不是後續 patch）
- **`docs/dev/STATUS.md` 的 Backlog 加一條 B 級**（第 3 步、在 `main` 上做）：

  > 把「整合回歸與同步」移到 Final Fresh Run／雙軸審查／Verdict **之前**。
  > 現在的節序是 Final Fresh（`_templates/7-review.md:94`）→ Verdict（`:133`）
  > → Exit Checklist 的整合同步（`:281`），所以**審過並核准的那棵樹，
  > 不是最後出貨的那棵樹** —— Exit 階段合併 `INTEGRATION_SHA` 之後 HEAD 就變了。
  > 而且 `ALREADY_SYNCED`（`:291`）只說「證據不算數」，沒有給恢復路徑。
  > **owner 已裁決：獨立成 feature 走完整七站，並拿它當第一個真實 full lane 的題目**
  > —— 它動的是模板節序，是母版最核心的結構，而且會影響 gate-consistency 的機械錨點，
  > 不該塞進發版前的補丁。

- Backlog 補完後應該是 **11 條**（原 10 ＋ 這一條）。整張表貼進回報。

---

## 不要做

- 不要 bump 版號到 3.8.1
- 不要動 Stage 1–4 模板
- **不要新增任何腳本檔**（本輪全是修既有檔；想新增就是偏離範圍，停下回報）
- 不要動 `_templates/7-review.md` 的**節序**（那是 Backlog 那條的事，本輪只改
  Exit Checklist 條目**內部**的文字）
- **不准在工作 branch 上碰 `docs/dev/STATUS.md`** —— 它只在 `main` 上改，
  動線見「收尾」節。上一輪的 bootstrap 例外**不適用本輪**（規則已經生效了）
- 不要碰 `notes/dispatch-v380-blockers.md` 除了 C-3 那一行以外的任何內容
- 不要順手收 `docs/dev/engine-fence-masking/7-review.md` 的文書
- 不要動 `execution.mode: parallel` 那套 T 級並行機制
- 不要為了讓某個檢查變綠而放寬它

---

## 回報格式

1. 十一項（A-1~A-3 / B-1~B-5 / C-1~C-3）各一段：改了哪些檔（`檔案:行號`）、
   實際跑了什麼指令、輸出原文。
2. 驗收那十道的輸出原文全貼，renderer 要貼**改完（紅）與 `--write` 之後（綠）兩次**。
3. **手動散發路徑演練**的每一步輸出原文 —— 這一項不能用「照做了」帶過。
4. 破壞實驗逐個列，一個都不能少：
   A-1 的 M-f（**I②~I⑥ 每個都要因逾時而紅**）與 M-g、A-2 三個、A-3 兩個、
   B-1 兩個、B-2 一個、B-3 一個、B-4 兩個、B-5（併入 A-2 第 3 條）、C-2 一個。
   每個都要寫「弄壞什麼 → 有沒有真的變紅」。**沒做破壞實驗的守衛一律當成沒做**。
5. `docs/dev/STATUS.md` 的 Backlog 整張表貼出來，說明是幾條（預期 11）。
6. 有沒有發現本檔沒提到的問題 —— 列出來問要不要處理，**不要自己動手**。

**每一個結論都要對應到你自己實際跑過的指令與看到的輸出。**
沒跑過的就寫「未驗證」，不准用推論代替。
