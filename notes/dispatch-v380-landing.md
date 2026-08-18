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
1. **不 push、不打 tag、不發 release**。全部做完回報，由 owner 決定何時推。
2. **不准動 Stage 1–4 的模板內容**（`_templates/1-discussion.md` ~ `_templates/4-spec.md`）。
   真實 full lane 觀測還沒跑，先動那幾份會污染觀測。
3. **不准放寬任何檢查來讓事情變綠**。本輪只有 B-1~B-5 明文授權改守衛，
   而且方向一律是**收緊**，不准放寬。
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

### 現象（已實測，不是推論）

```
devflow-integration-regression.sh --integration      → ⛔ 無限迴圈，掛住不會回來
devflow-integration-regression.sh --fork-sha         → ⛔ 無限迴圈，掛住不會回來
```

其餘漏值變體（`--integration origin/main --fork-sha`、`--fork-sha abc --integration`、
`--no-fetch --integration`）實測都正常 exit 2 —— **只有「旗標是唯一參數」那兩種會掛**，
而那正好是最自然的手殘打法（打了旗標忘記貼值）。

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
      [ $# -ge 2 ] || { echo "⛔ $1 後面缺值" >&2; usage; }
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

寫法自訂，但**三件必須成立**：①任何情況都不會無限迴圈 ②無參數印用法且 exit 2
③旗標缺值印用法且 exit 2。

⚠️ **正本改完要重新散發到 `docs/dev/tools/`**，parity 守衛會抓（但不要等它抓，自己做）。

⚠️ **不要動 `-- 前置檢查 --` 那段的訊息內容** ——
`check-integration-regression-guard.sh:228` 的 H① 斷言 `"缺 --fork-sha" in out`
還要繼續成立。用法訊息是**追加**，不是取代。

### 驗收（wrapper 補三個反例）

在 `scripts/check-integration-regression-guard.sh` 新增情境 **I**（用法／參數錯）：

| 子案 | 指令 | 必須得到 |
|---|---|---|
| I① | 無參數 | exit 2 **且訊息含「用法」** |
| I② | 只給 `--integration` | exit 2 **且訊息含「用法」**、**且在 5 秒內結束** |
| I③ | 只給 `--fork-sha` | 同 I② |
| I④ | `--bogus` | exit 2 且訊息含「用法」 |

⚠️ **I②/I③ 必須帶逾時**（例如用 `subprocess` 的 `timeout=5`），
逾時就算失敗 —— 沒有逾時的話，回歸發生時是整條 CI 掛住，不是紅字。

**破壞實驗（mutant M-f）**：把修好的參數解析換回舊版 `shift 2` 寫法，
確認 I② 會**因逾時而紅**。不紅就是逾時沒生效，重做。

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

### 修法

把 baseline 的**落地時機**從步驟 1 移到**步驟 7 全部散發並驗證成功之後**：

- 步驟 1 只留「等一下要拍哪些東西」的宣告（`README.md` 已剝除版、`_templates/*`、
  `devflow-contract.json`、整個 `docs/dev/tools/`），並明寫「**實際落地在步驟 7 之後**」。
- 新增一個收尾步驟（編號接在步驟 7 之後），內容是「把上述四項快照到
  `docs/dev/.devflow-baseline/`」，並註明理由：**tools/ 要到步驟 6、7 才有內容，
  拍早了會讓 upgrade 的三方比對把官方工具誤判成本地客製**。
- `upgrade` 段（`:143-150` 附近）講「上游舊 blob 的來源」那段也要跟著改：
  說明每次 install/upgrade **成功之後**才更新快照，不是動作之前。

### 驗收

`scripts/check-dev-setup-discipline.sh` 新增一條：
**baseline 快照的落地步驟編號必須大於 tools/ 散發的步驟編號**。

做不到精確解析步驟編號的話，退而求其次：斷言 baseline 段落**出現在**
「整合回歸工具散發」段落**之後**（用字元位置比，跟 A-1 的順序守衛同一個手法）。

**破壞實驗**：把 baseline 段搬回步驟 1，確認這條會紅。

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
2. **branch 命名統一成 `feat/<slug>`**（跟 `:412` 的 `origin/feat/<slug>` 對齊）。
   全檔搜一遍 `feature/<slug>`，一併改掉。
3. Stage 6 那段加一句指回 Stage 7：「這個 `FORK_INTEGRATION_SHA` 是 Stage 7
   整合回歸要用的，現在不記，到時候會卡住。」

### 驗收

⚠️ **`render-methodology-corrections.sh --check` 不會紅** —— 那段不在抽取範圍，
這是正常的，不要為了讓它紅而去改別的東西。

改成由 `scripts/check-status-policy.sh`（它已經在看 quickstart）新增兩條：

- quickstart 的 Stage 6 指令區塊必須含 `git fetch`、`FORK`、`--fork-sha` 對應的錨點字樣
  （用關鍵詞組，不要逐字釘整段 —— 會天天假紅）
- **全檔不得再出現 `feature/<slug>`**（命名統一）

**破壞實驗**：①把 `git fetch` 從 quickstart 拿掉 → 必須紅；
②把某處改回 `feature/<slug>` → 必須紅。

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

**破壞實驗**：把模板那條裡的「合併」與「全套測試」刪掉，確認會紅。

## B-2 STATUS 守衛沒釘住「誰做」

**位置**：`scripts/check-status-policy.sh:64`

```python
("ship 移出 Active 由 merger 在合併後做", ["移出", "Active", "合併"]),
```

關鍵詞裡**沒有任何一個指向 actor** —— 把「由合併那個 PR 的人做」改成
「由 owner 做」，三個關鍵詞照樣全中，守衛全綠。

而「誰做」正是 M-2 那一輪要解的核心（owner→merger 交接），釘不住等於沒釘。

**修法**：關鍵詞組加上 actor 相關的字（例如同時要求「合併」與「PR」出現，
或要求「不是 reviewer」這種區辨詞）。**不要逐字釘整句**，釘得住 actor 即可。

**破壞實驗**：把兩份 STATUS 裡的 actor 改成 owner，確認會紅。

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
3. `:1589` 那行摘要寫「七支地板/群組數靜態互釘全過」，**數字要跟著改**
   —— 那句話本身就是第 7 型的實例。

**破壞實驗**：把 wrapper 裡任一個情境函式的 `check(...)` 刪掉，確認地板會紅。

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

## C-2 STATUS 的遠端 ref 會過期，導致補修判準算出假的「零交集」

**位置**：`_templates/STATUS.md:41-46`（`Branch` 欄填法）
＋ `README.md:631-640`（用那個 ref 算「其他 feature 碰過的檔」）

`Branch` 欄只規定「branch 推上去之後換成遠端 ref」，
**沒規定後續每個 T commit 什麼時候 push**。而 README 拿那個 remote ref 算聯集。

**失敗情境**：某個 feature 本地有三個已 ACCEPTED 但沒推的 T commit，
它們改的檔不在 remote ref 的 diff 裡 → 聯集少算 → 補修被判成「零交集、可以直接補修」
→ 補修撞上那個 feature 正在改的檔。

**修法**（兩件都要）：

1. `_templates/STATUS.md` 的 `Branch` 欄填法補一句：**每個 T 的 ACCEPTED commit
   都要推上去**（一 T 一 commit 本來就是既有規則，這裡只是補「而且要推」），
   讓遠端 ref 始終代表這個 feature 的最新狀態。
2. `README.md` 的算法補一道 fail-closed：算聯集之前，**對每個 feature 核對
   remote ref 的 SHA 與該 feature 最新 ACCEPTED commit 一致**；
   對不上 → **停下問人**，不要拿過期的 ref 算完就宣稱零交集。
   （怎麼知道最新 ACCEPTED commit：6-notes 的 TDD Evidence 有記；
   對不上時人去問那個 feature 的 owner 就好，母版不需要機械解。）

## C-3 sentinel 的冒號正本定案

**owner 已裁決：用半形 `n-a:尚未建立 branch`。**

實作已經全面使用半形、全庫一致；`notes/dispatch-v380-blockers.md:687` 寫的是全形，
**改那一份的那一行**（那是規格檔，要跟實作對齊），其餘不動。

⚠️ 這是本輪唯一准許修改 `notes/dispatch-v380-blockers.md` 的地方。

---

## 做完之後的驗收（全部都要跑，輸出貼進回報）

```bash
bash scripts/devflow-check.sh all                          # REPO_REFERENCE_PASS 全過
bash scripts/render-methodology-corrections.sh --check     # 綠（本輪不該讓它紅，見 A-3）
bash hooks/selftest.sh                                     # 全過（項數以輸出為準）
env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
bash hooks/devflow-exec.sh doctor                          # COMPATIBLE
bash scripts/check-gate-twin.sh                            # 全過
bash scripts/check-integration-regression-guard.sh         # 全過（項數會比 24 多）
bash scripts/check-status-policy.sh                        # 全過（項數會比 6 多）
bash scripts/check-file-map.sh                             # scanned=77 不變（本輪不新增腳本）
```

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

### 收帳

- `scripts/history-append.sh` 追加一筆，`--version` 帶 **`v3.8.0`**
  （這一輪修的仍是一個還沒發布出去的版本，不是後續 patch）
- **`docs/dev/STATUS.md` 的 Backlog 加一條 B 級**：

  > 把「整合回歸與同步」移到 Final Fresh Run／雙軸審查／Verdict **之前**。
  > 現在的節序是 Final Fresh（`_templates/7-review.md:94`）→ Verdict（`:133`）
  > → Exit Checklist 的整合同步（`:281`），所以**審過並核准的那棵樹，
  > 不是最後出貨的那棵樹** —— Exit 階段合併 `INTEGRATION_SHA` 之後 HEAD 就變了。
  > 而且 `ALREADY_SYNCED`（`:291`）只說「證據不算數」，沒有給恢復路徑。
  > **owner 已裁決：獨立成 feature 走完整七站，並拿它當第一個真實 full lane 的題目**
  > —— 它動的是模板節序，是母版最核心的結構，而且會影響 gate-consistency 的機械錨點，
  > 不該塞進發版前的補丁。

- Backlog 補完後應該是 **11 條**（原 10 ＋ 這一條）。整張表貼進回報。
- **不要 push、不要 tag、不要發 release**

---

## 不要做

- 不要 bump 版號到 3.8.1
- 不要動 Stage 1–4 模板
- **不要新增任何腳本檔**（本輪全是修既有檔；想新增就是偏離範圍，停下回報）
- 不要動 `_templates/7-review.md` 的**節序**（那是 Backlog 那條的事，本輪只改
  Exit Checklist 條目**內部**的文字）
- 不要碰 `notes/dispatch-v380-blockers.md` 除了 C-3 那一行以外的任何內容
- 不要順手收 `docs/dev/engine-fence-masking/7-review.md` 的文書
- 不要動 `execution.mode: parallel` 那套 T 級並行機制
- 不要為了讓某個檢查變綠而放寬它

---

## 回報格式

1. 十一項（A-1~A-3 / B-1~B-5 / C-1~C-3）各一段：改了哪些檔（`檔案:行號`）、
   實際跑了什麼指令、輸出原文。
2. 驗收那九道的輸出原文全貼。
3. **手動散發路徑演練**的每一步輸出原文 —— 這一項不能用「照做了」帶過。
4. 破壞實驗逐個列（A-1 的 M-f、A-2、A-3 兩個、B-1~B-5 各一）：
   弄壞什麼 → 有沒有真的變紅。**沒做破壞實驗的守衛一律當成沒做**。
5. `docs/dev/STATUS.md` 的 Backlog 整張表貼出來，說明是幾條（預期 11）。
6. 有沒有發現本檔沒提到的問題 —— 列出來問要不要處理，**不要自己動手**。

**每一個結論都要對應到你自己實際跑過的指令與看到的輸出。**
沒跑過的就寫「未驗證」，不准用推論代替。
