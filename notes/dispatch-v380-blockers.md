# 派工單：v3.8.0 發版前必修（整合回歸演算法錯誤 ＋ 六條補強）

> **觸發句**：`讀 ~/dev/dev-flow/notes/dispatch-v380-blockers.md 照它跑，全程不打斷問人`
>
> 本檔是**派工單**，讀完就照做。**全部七項都已由 owner 裁決完畢，沒有要回頭問的事。**
> 三個曾經是決策點的東西已經定案，記在末節「owner 已裁決的三件」——
> 那節是**紀錄**不是問題，不要停在那裡等人。
>
> 唯一該停下回報的情況：本檔寫的東西與現場實況對不上（例如指定的行號找不到、
> 指定的檔案不存在、驗收條件互相矛盾）。那種時候停下說清楚，不要自己猜著做。

---

## 這份要解決什麼

上一輪（`notes/dispatch-parallel-feature-gaps.md`）把「多 feature 並行的四個制度空白」寫進了母版，
本機五道檢查全綠、v3.8.0 的 release commit 也建好了。**但東西還沒推上去** ——
`origin/main` 停在 v3.7.1、沒有 `v3.8.0` tag、沒有 GitHub release、這些 commit 從沒跑過 CI。

**這是好事，因為那一版裡面有一條指令是壞的。**

⚠️ **不要拿「本機領先幾個 commit」當開工前的檢查條件** —— 那個數字會隨著這份派工單
自己的 commit 一起變動（產品改動 ＋ 派工單文件），寫死就會在開工第一步誤判成「現況不符」。
要確認的是這三件（都不是數字）：`origin/main` 還在 v3.7.1、沒有 `v3.8.0` tag、
本機版號是 3.8.0。

跨家族第二意見（codex）分三輪審出的問題與主線程自己抓到的合併成本檔六項。
其中那條「高」的根源不在實作者抄錯，而在**上一份派工單寫的演算法本身就算錯**，
所以六輪審查全部沒抓到 —— 大家都在檢查「有沒有照抄」，沒有人檢查「原文對不對」。

### 版本號怎麼算（重要，不要弄錯）

**這一輪的修正全部併進 v3.8.0，不要 bump 成 v3.8.1。**

理由：v3.8.0 從來沒推出去、沒有 tag、沒有 release —— 對外它**還不存在**，
所以它是可以繼續編輯的。發一個「上線就馬上被 v3.8.1 蓋掉」的版本沒有意義，
只會讓採用專案的升級紀錄多一段雜訊。

`.claude-plugin/plugin.json` 與 `hooks/runtime-capabilities.json` 兩處**維持 3.8.0，不要動**。

---

## 硬約束

0. **開工第一件事**：從 `main` 開一條工作 branch `fix/v380-blockers`，
   不要在 `main` 上直接動手。做完 `git merge --no-ff` 回 `main`。
   （本檔已經 commit 在 `main` 上了，你從 `main` 開 branch 就看得到它。）
1. **不 push、不打 tag、不發 release**。全部做完回報，由 owner 決定何時推。
1.5 **一次性的 bootstrap 例外（S-1 專用，只此一次）**：
   本輪要新增的規則是「`STATUS.md` 只在整合分支維護，feature branch 一律不碰」，
   而 S-1 要做的事**就是修改 `docs/dev/STATUS.md` 本身** —— 照新規則，這件事該在
   `main` 上直接做；但硬約束 0 又要求所有改動走工作 branch。兩條在這一輪必然打架。
   **本輪的做法：`docs/dev/STATUS.md` 的改動照樣放在 `fix/v380-blockers` 上，
   跟其他五項一起 merge 回 main。** 理由：規則要到本輪 merge 之後才生效，
   而且本輪只有一條 branch 在跑，不存在它要防的那種衝突。
   **這個例外只適用本輪**，下一輪起一律照新規則走。
   把這段理由寫進本輪的 HISTORY 條目，不要只寫在 commit message 裡 ——
   否則下一個人讀到 git 歷史會以為規則可以隨便破。
2. **不准動 Stage 1–4 的模板內容**（`_templates/1-discussion.md` ~ `_templates/4-spec.md`）。
   下一輪要拿 dev-flow 自己跑一次完整七站當觀測實驗，先動那幾份會讓觀測分不出
   「流程本來就有問題」還是「這輪改出來的問題」。本檔要修的全在 Stage 6/7 與 README。
3. **不准放寬任何檢查本身**來讓事情變綠（`scripts/check-*.sh`、`hooks/*.sh`
   只有在本檔明文要求時才准動）。
4. **不准 bump 版號**（理由見上）。
5. `docs/dev/HISTORY.md` 只能用 `scripts/history-append.sh` 追加，不准直接編輯。
6. **不要順手修無關的東西**。看到別的問題寫進回報問要不要處理，不要自己動手。

---

## H-1〔高·擋發版〕整合回歸的「共同戰場」算錯，而且會產生假綠

**位置**：`_templates/7-review.md:281`（Exit Checklist「（條件式）整合回歸」那條）
**根源**：`notes/dispatch-parallel-feature-gaps.md:149`（上一輪派工單的原演算法就是錯的）

### 現在寫的順序

```
1. BASE=$(git merge-base HEAD <整合分支>)
2. git log "$BASE..<整合分支>" 為空 → 記 n-a 即勾；非空 → 往下
3. ①把整合分支合進本 branch（或 rebase），先在本地解完衝突
4. ②跑一次全套測試
5. ③comm -12 <(git diff --name-only "$BASE"..HEAD | sort) \
             <(git diff --name-only "$BASE"..<整合分支> | sort)
```

### 錯在哪

第 5 步是在第 3 步的合併**之後**才算的。合併完之後 `HEAD` 已經含有整合分支的內容，
所以 `"$BASE"..HEAD` 這個範圍**同時包含**「我這條線改的檔」跟「對方改的檔」。
交集算出來就變成「對方改的全部檔案」，而不是「兩邊都動到的檔案」。

兩種走法、兩種後果，第二種是這個 repo 反覆定名過的**假綠**：

| 怎麼走 | 會發生什麼 | 型態 |
|---|---|---|
| 照順序跑一次 | 交集灌水成「整合分支改的所有檔案」，明明兩邊毫無重疊也會列出一堆 → 人看幾次就開始無視這條 | 檢查失去鑑別力 |
| 合併完之後重跑整段 | `git merge-base` 已經漂到整合分支的最新點，`git log "$BASE..<整合分支>"` 變成空 → **判 n-a 直接勾掉** | **假綠**（檢查全綠，東西沒被檢查） |

**白話就是：這條檢查照著跑，要嘛吵到你不想理它，要嘛安靜地放你過關 —— 兩種都等於沒有檢查。**

### 已在拋棄式 repo 實測確認（不是推論）

情境一：`feat/a` 只改 `a1.txt`/`a2.txt`，`trunk` 只改 `b1.txt`/`b2.txt`，**兩邊零重疊**：

```
git diff --name-only $BASE..HEAD | sort   → a1.txt a2.txt b1.txt b2.txt
git diff --name-only $BASE..trunk | sort  → b1.txt b2.txt
comm -12 ...                              → b1.txt
                                             b2.txt        ← 正確答案應該是「空」
```

合併之後重跑第 1 步：

```
git merge-base HEAD trunk  → 8fb6c190cde7bb28929a56fdf484fcd82748fdae
git rev-parse trunk        → 8fb6c190cde7bb28929a56fdf484fcd82748fdae   ← 同一個
git log $NEWBASE..trunk    → （空）                                      ← 誤判 n-a
```

情境二：兩邊都改 `shared.txt`（真的有共同戰場）：

```
模板演算法 → b1.txt, shared.txt      ← b1.txt 是 merge 帶進來的，feat/a 從沒碰過
正確答案   → shared.txt              ← 只有這一個
```

修正版演算法在兩個情境各跑一次：情境一交集為**空**、情境二交集**只有 `shared.txt`**，都正確。

### 修法

**在動樹之前，先把三個座標與兩邊的檔案清單抓下來**，算完真正的交集，**然後才**合併與跑測試：

⚠️ **模板裡不要再內嵌整套演算法。** 那是這一輪最容易做錯的地方 ——
演算法同時存在於模板文字與散發腳本裡，就變成**兩份正本**，
下次只改一邊，兩邊講的話不一樣，而且沒有任何檢查在比對它們。

模板那一條改成「跑腳本 → 看狀態字串 → 照狀態做事」，長這樣（意思要到，字句自訂）：

```
- [ ] （條件式）整合回歸：跑
      `docs/dev/tools/devflow-integration-regression.sh \
         --integration origin/<整合分支> --fork-sha <6-notes 步 0 記的那 40 碼>`
      （工具自己會 fetch；工作樹必須乾淨，否則它 exit 2 擋你）
      依它印出的 STATUS 決定：
      · N_A_NO_INCOMING            → 記 n-a 即勾（分岔後對方零新 commit）
      · SYNC_REQUIRED_NO_OVERLAP   → 合併它印的 INTEGRATION_SHA ＋ 跑全套測試才可勾
      · SYNC_REQUIRED_WITH_OVERLAP → 上面兩件 ＋ 交集逐檔看過才可勾
      · ALREADY_SYNCED             → 你已經合過了，這次輸出不算數（見下）
      勾的時候把它最後一行的結論貼進本檔（含三個 SHA）。
      ⚠️ **一定要在動樹之前跑。** 合併之後 HEAD 已含對方內容、merge-base 也已漂移，
      兩個座標都被污染 —— 那時候跑出來的「沒有共同戰場」是假的。
      ⚠️ 合併時合的是腳本印出來的 **INTEGRATION_SHA**，不是 branch 名。
      branch 名會跑，中間別人再合進來的話，你實際併進來的內容
      跟剛才檢查過的不是同一份。
      ⚠️ **動手合併之前無條件再跑一次腳本**（不是「隔了一段時間才跑」——
      那是主觀條件，人一定會自己說服自己「應該還好」）。兩次的 STATUS
      與四個座標必須完全相同才准動手；有任何一項不同 → 停下，照新的重算。
```

順序也要在模板寫死：**跑腳本算交集 → 合併 → 跑全套測試**，
不是舊版的「合併 → 測試 → 算交集」。

#### 演算法規格（給寫腳本的人，不要寫進模板）

```bash
# FORK 來自 --fork-sha（必填）；REF 來自 --integration（必填，且必須是 refs/remotes/…）
FORK=$(git rev-parse --verify "${FORK_ARG}^{commit}") || exit 2
FEATURE_HEAD=$(git rev-parse HEAD)
INTEGRATION_SHA=$(git rev-parse --verify "${REF}^{commit}") || exit 2

# fail-closed：錨點必須同時是「整合分支現況」與「本 branch 現況」的祖先。
# 任一不成立 = 錨點給錯了，或歷史被改寫過 → 不准往下算。
git merge-base --is-ancestor "$FORK" "$INTEGRATION_SHA" || exit 2
git merge-base --is-ancestor "$FORK" "$FEATURE_HEAD"    || exit 2

# 判定（照上面那張表；注意兩邊的比較基準都是 FORK，不是 merge-base）
git merge-base --is-ancestor "$INTEGRATION_SHA" "$FEATURE_HEAD"   # 成立 → ALREADY_SYNCED

# 需要算交集時：
TMPD=$(mktemp -d); trap 'rm -rf "$TMPD"' EXIT
git diff --name-only --no-renames "$FORK".."$FEATURE_HEAD"    | sort > "$TMPD/feature.txt"
git diff --name-only --no-renames "$FORK".."$INTEGRATION_SHA" | sort > "$TMPD/integration.txt"
comm -12 "$TMPD/feature.txt" "$TMPD/integration.txt"
```

⚠️ **`git merge-base` 只准用在 `--is-ancestor` 這種祖先判定上，
不准再用它算分岔點。** 分岔點一律用持久化的 `FORK`。

三個容易被忽略的細節：

| 細節 | 為什麼 |
|---|---|
| **`--no-renames`** | git 預設會偵測改名，兩邊的偵測結果可能不一致（一邊認出來、一邊沒有），交集就會漏。關掉之後改名一律顯示成「舊路徑消失＋新路徑出現」，兩邊口徑一致 |
| **`mktemp -d` ＋ `trap` 清掉** | 不准用 `/tmp/feature-files.txt` 這種固定檔名 —— 兩個 worktree 同時跑就會互相覆蓋，而且**不會有任何錯誤訊息**，兩邊都拿到對方的清單還以為是自己的 |
| **腳本不動工作樹，但會自己 fetch** | 「不動樹」指的是 merge / rebase / checkout / 寫檔 —— 那些一律由人做。**`git fetch` 不算動樹**（它只更新遠端追蹤 ref），而且必須由工具自己跑，否則「忘記 fetch」就是一個沒有人在守的洞。完整的 fetch 責任分工見下一節 |

#### fetch 責任分工（**定案，全檔以此為準**）

| 什麼時候 | 誰 fetch | 為什麼 |
|---|---|---|
| Stage 6 開 feature branch **之前** | **人**（步 0 的不可拆動作，見 M-1） | 錨點要記的是「當下整合分支的最新點」，沒 fetch 記到的是舊點 |
| Stage 7 跑整合回歸工具時 | **工具自己，每次都跑** | 忘記 fetch 是人必犯的錯，交給人守等於沒守 |

工具**會更新遠端追蹤 ref**（`refs/remotes/…`），這是它唯一會改動的 git 狀態，
不影響工作樹與任何本地分支 —— 檔頭要寫明這一點，不要讓人以為它是純唯讀。

`--no-fetch` **只能用來診斷**：帶了它就一律 **exit 2**，
輸出標記「未 fetch，本次結果不得用於勾 Exit Checklist」。
不准讓它產出一個看起來可以勾的結果 —— 那正是 fail-open。

### 也要改的第二個位置

`notes/dispatch-parallel-feature-gaps.md:149` 那段原演算法要**加註更正**。
那份是已完成輪次的紀錄檔，上一輪的硬約束是「不動歷史文件內容」，所以
**不要把原文改掉** —— 在那段下面加一個明顯的更正框：

```
> ⚠️ **2026-08-18 更正**：本節的演算法是錯的（在合併之後才算交集，兩個座標都已被污染）。
> 正確版本見 `notes/dispatch-v380-blockers.md` H-1。本段保留原文以留痕，**不要照本段實作**。
```

不加這個註記，未來某個 session 讀到 `:149` 會把 bug 原樣搬回來。

### H-1 附帶：這條檢查要做成散發腳本（owner 已裁決，不是選項）

owner 已裁定把它做成腳本，理由見末節 D-1。以下是規格，照著做。

#### 檔名與位置

| | 路徑 | 權限 |
|---|---|---|
| 正本 | `scripts/devflow-integration-regression.sh` | 755 |
| 散發副本 | `docs/dev/tools/devflow-integration-regression.sh` | 755 |

命名說明：codex 原本建議叫 `check-integration-regression.sh`，**這裡改名**。
理由：`scripts/check-*.sh` 在這個 repo 是**母版自檢**（檢查母版自己有沒有壞），
而這支是**給採用專案在自己的 feature branch 上跑的工具**，跟
`devflow-evidence-gauntlet.sh`、`history-append.sh` 同一類。沿用 `check-` 開頭會讓
下一個人以為它是母版守衛，然後把它掛進錯的地方。

#### 這支腳本做什麼、不做什麼

**只算與只判，絕不動樹。** 合併／rebase／跑測試全部由人做。

理由：一支會 `git merge` 的腳本，一旦在有未提交改動、或處在 rebase 中途的樹上被跑，
會把現場弄得更糟；而它要防的問題（順序錯、座標被污染）只靠「算」就解決了。
唯讀的腳本可以放心在任何時候重跑。

#### 這支腳本需要一個「分岔錨點」，而且那個東西 git 算不出來

**這是整份派工單最關鍵的一段，先把它讀懂再往下。**

上一版的設計想用 `git merge-base HEAD <整合分支>` 當分岔點。**那是算不出正確答案的**，
理由是純圖論的：只要整合分支的最新點是 `HEAD` 的祖先，`merge-base` 就**必然**等於它。
於是這三種完全不同的處境，在 git 圖上長得一模一樣：

- 你剛從最新的整合分支開分支（你是第一個合的）
- 你已經把整合分支合進來了
- 你 rebase 到最新的整合分支之上（rebase 完更是完全線性，連 merge commit 都沒有）

**沒有任何一組 runtime 座標能區分它們**，因為區分它們需要的資訊是「歷史上的某個時刻」，
而那個資訊在圖上已經被抹掉了。上一版寫「腳本要盡力區分、區分不出來要問人」——
那是把一個算不出來的東西交給人猜，等於沒解。

**解法：把分岔點在 feature 開工的當下記下來。**

| 名字 | 是什麼 | 誰記、什麼時候記 |
|---|---|---|
| `FORK_INTEGRATION_SHA` | **開這條 feature branch 的當下，整合分支的最新點** | Stage 6 步 0 開 branch 的同一動，寫進 `6-implementation-notes.md` 步 0 的輸出區 |

這件事併進 M-1 —— 步 0 的「完成 =」本來就要改（見 M-1），把 fork 錨點一起加進去，
不用另外開一個機制、也不用動 runtime。

#### CLI 契約

```
用法：devflow-integration-regression.sh --integration <remote-tracking ref> \
                                        --fork-sha <FORK_INTEGRATION_SHA>
例：devflow-integration-regression.sh --integration origin/main \
                                      --fork-sha 3f2a1c9...
（在 feature branch 的工作樹裡跑）
```

⚠️ **`--fork-sha` 是必填，缺了就 exit 2**，錯誤訊息要指回 6-notes 步 0 說明去哪裡拿。
**絕對不准在缺錨點時退回用 `merge-base` 猜，更不准判成 `N_A_NO_INCOMING`。**
這是 fail-closed，對齊 G1 的教訓：守衛在狀態檔不存在時**靜默沉睡**，
「守衛在擋」與「守衛不在」對執行者長得一模一樣。

⚠️ **`--integration` 必須解析到 `refs/remotes/...`，否則 exit 2。**
不要只看參數裡有沒有 `/`（`feat/x` 也有 `/`），要實際用
`git rev-parse --symbolic-full-name <ref>` 確認它落在 `refs/remotes/` 底下。
理由：`git fetch` **不會更新本地的 `main`** —— 它更新的是 `origin/main`。
收本地 ref 會在「沒有 checkout 過 main 的工作樹」（並行時的常態）拿到過時好幾天的點。
上一版寫「警告後照樣算」是 fail-open，改掉。

⚠️ **腳本自己要跑 `git fetch <remote>`**（不動工作樹，只更新遠端追蹤 ref）。
上一版說「交給人決定」——「忘記 fetch」就成了一個沒有任何人在守的洞。
`--no-fetch` **不是逃生口，是診斷開關**：帶了它一律 exit 2，
輸出標記「未 fetch，本次結果不得用於勾 Exit Checklist」。詳見上面的 fetch 責任分工。

#### 四種判定結果

有了錨點之後，判定變成純粹的圖關係查詢，沒有猜的成分：

| 狀態字串 | 判定式 | exit | 人要做什麼 |
|---|---|---|---|
| `N_A_NO_INCOMING` | `INTEGRATION_SHA == FORK_INTEGRATION_SHA` | 0 | 真的可以跳過，Exit Checklist 記 n-a |
| `ALREADY_SYNCED` | 整合分支往前跑了，**而且它的最新點已經是 `HEAD` 的祖先** | 2 | **你已經同步過了，這次輸出不算數**。交集必須在動樹之前算 —— 拿同步後的輸出當證據就是原本那個假綠 |
| `SYNC_REQUIRED_NO_OVERLAP` | 整合分支往前跑了、不是 `HEAD` 的祖先，交集為空 | 10 | **仍要**合併 `INTEGRATION_SHA` ＋ 跑全套測試。沒有共同戰場不代表不會壞（介面沒改、行為改了一樣會炸） |
| `SYNC_REQUIRED_WITH_OVERLAP` | 同上，但交集非空 | 11 | 合併 ＋ 全套測試 ＋ **交集逐檔看過** |
| （fail-closed） | 缺 `--fork-sha`／錨點不是 `INTEGRATION_SHA` 的祖先（錨點不合法或歷史被改寫過）／`--integration` 不是遠端追蹤 ref／不在 git repo／**工作樹髒**／**merge 或 rebase 進行中** | 2 | 先處理，再重跑。**不准帶著算** |

**exit 0 只有 `N_A_NO_INCOMING` 一種。** 這是整條修法的重點 ——
舊寫法讓「有東西可能踩、只是這次沒撞到」也走 exit 0，人就會跳過合併與測試。

⚠️ **工作樹髒或處在合併／rebase 中途一律 exit 2**：未提交與未追蹤的改動
**不會**進入 `FEATURE_HEAD` 的計算，算出來的「我這邊改了哪些檔」會少掉正在改的那些。

#### 輸出格式

- 第一行：`STATUS: <四個狀態字串之一>`
- **三個 40 碼全長 SHA**：`FORK_INTEGRATION_SHA` / `FEATURE_HEAD` / `INTEGRATION_SHA`
- **一個 canonical ref**：`INTEGRATION_REF`（就是 `--integration` 解析後的完整
  `refs/remotes/…` 路徑，不是 SHA）
- 共同戰場的檔案清單（一行一個），沒有就明確印 `共同戰場：無`
- fetch 有沒有跑（`--no-fetch` 時要標記「本次結果不得用於勾 Exit Checklist」）
- 最後一行印一句可以直接貼進 7-review 的結論，內含狀態字串、三個 SHA 與 canonical ref

檔頭照這個 repo 的既有慣例寫成三段式（規格正本引用 ／ 用法 ／ exit code），
本體用 `python3 - <<'PY'` heredoc、`check(cond, label, detail)` 累計、
分組印 `-- 分組名 --` —— 照 `scripts/check-gate-twin.sh` 與
`scripts/check-history-integrity.sh` 的樣子寫，**不要自創一套**。

#### 本輪一共新增三支腳本（**定案，不是選項**）

後面每一處記帳都要照這個拓撲算，所以先定死：

| # | 檔案 | 是什麼 | 要散發嗎 |
|---|---|---|---|
| 1 | `scripts/devflow-integration-regression.sh` | 給採用專案跑的正式工具 | ✅ 散到 `docs/dev/tools/` |
| 2 | `scripts/check-integration-regression-guard.sh` | H-1 的母版自檢 wrapper。**情境、mutant、模板順序守衛、正副本 parity 全部併進這一支** | ❌ 母版自用 |
| 3 | `scripts/check-status-policy.sh` | S-1 的守衛（兩份 STATUS 對帳 ＋ `Branch` 欄 ＋ quickstart 範例列） | ❌ 母版自用 |

**不要另立第四支 parity 腳本** —— parity 就住在 #2 裡。

#### 新增散發腳本要動的記帳點（**八處，漏一個就會紅或假綠**）

這個 repo 有「第 7 型假綠：不對稱記帳」的前科 —— 保護長大了、列舉它的清單沒跟著長。
**以下每一處都已經實地查過行號，不是推測的**：

| # | 落點 | 要做什麼 |
|---|---|---|
| 1 | `skills/dev-setup/SKILL.md` **install** 散發段 | 照 `devflow-evidence-gauntlet.sh` 的寫法（104-110 行附近）加一段散發本腳本，含設 755 |
| 2 | 同檔 **check（健檢）** 路徑 | 加一個編號檢查項：存在 ＋ 與正本 `diff` ＋ **可執行位元**。照第 9 項（232-237 行）或第 11 項（245-254 行）的樣子寫 |
| 3 | 同檔 **baseline**（`:49-51`） | ⚠️ **這一處最容易漏**。`docs/dev/.devflow-baseline/` 是 install 時建的快照，upgrade 拿它當「上游舊版」做三方比對。它現在**只列** `README.md`、`_templates/*`、`devflow-contract.json`，**完全不含 `docs/dev/tools/` 的任何一支**。<br>**要納入的不只新工具** —— `docs/dev/tools/` 底下**現有的四支也全都不在 baseline 裡**，這是既有缺口。本輪把整個 `docs/dev/tools/` 一起納入（用目錄，不要逐檔列，否則下一支又會漏） |
| 4 | 同檔 **upgrade 後的可執行驗證**（`:115-116` 指回 install 步 6，`:104-110`） | 「覆蓋整個 `docs/dev/tools/`」這句**不夠** —— 步 6 只驗 gauntlet 一支。新工具要加進 upgrade 成功後的可執行位元驗證 |
| 5 | `skills/dev-release/SKILL.md:63-67` | 那裡**寫死五個 `diff -q`**（contract、gauntlet、`history-append.sh`、`build-gate-twin.py`、`devflow_twin_ui.py`），是靜態列舉不是掃目錄 → 新增第六支**必漏驗**。<br>**改法：`docs/dev/tools/` 那四行改成呼叫第 8 點的 parity 守衛；但 `diff -q devflow-contract.json docs/dev/devflow-contract.json` 這一行要留著。**<br>⚠️ contract **不住在 `docs/dev/tools/`**，parity 守衛的 expected set 涵蓋不到它 —— 一起刪掉就會變成沒有人在驗 contract 副本，是拿一個假綠換另一個假綠 |
| 6 | 檔案地圖 `guides/guide-dev-flow.html` 的 `id="filemap"` 節（1742 行起） | 每支母版腳本各一列；有散發雙生的，**在同一列的生命週期格附註「散發面：`docs/dev/tools/`」**（現成例子見該檔 209/213/227/230 行），**不要為散發副本另開一列** |
| 7 | `scripts/check-version-sync.sh:65-88` | 同樣是寫死的版本錨清單。**只有在新腳本裡帶版本字串時才要動**；不帶版本字串就不動，並在回報裡說明你選了哪一種 |
| 8 | parity 對帳（**併進 `check-integration-regression-guard.sh`，不另立腳本**） | 見下面那節 —— 這一點的清單怎麼來，決定了它會不會又是一個假綠 |

#### 第 8 點的 expected set 要從哪裡來（**不能只掃 `docs/dev/tools/`**）

先講清楚為什麼不能只掃副本目錄：**正本與副本被同時刪掉時，掃出來的清單就少一項，
兩邊都不存在、比對零筆、守衛全綠。** 這正是第 4 型假綠（只檢查「有的東西對不對」，
沒檢查「該有的還在不在」）—— 這個 repo 已經踩過三次。

也不能改成掃整個 `scripts/`：那會把母版自用的檢查腳本（`check-*.sh` 那一票）
全部誤判成「缺散發副本」。

**定案（本輪不做完整的散發清單正本，那件事列 Backlog）**：
拿**檔案地圖裡標了「散發面：`docs/dev/tools/`」的那些列**當 expected set，
然後**雙向**檢查每一項：

| 檢查什麼 | 不通過代表 |
|---|---|
| 正本存在 | 正本被刪了 |
| 副本存在 | 忘記散發，或副本被刪了 |
| 內容逐字相同 | 改了正本沒重新散發 |
| **正本與散發副本的可執行位元相同** | 散發時掉了執行權限（實際發生過） |
| 反向：`docs/dev/tools/` 底下有檔案**不在** expected set 裡 | 散發了但沒記進檔案地圖 |

⚠️ 可執行位元只比**正副本兩邊一不一致**，**不要拿檔案地圖當 mode 的正本** ——
檔案地圖現在沒有 mode 欄位，也沒有任何 mode 規格，硬要比就是拿一個不存在的東西當基準。
（既有的 `devflow_twin_ui.py` 是 644，因為它只供 import；`history-append.sh` 等是 755。
沒有一份文件在管這件事，那是完整散發清單正本要解的問題，**已列 Backlog，本輪不做**。）

本輪新增的 `devflow-integration-regression.sh`，正本與散發副本**兩邊都固定 755**，
直接寫死在守衛裡（檔名 ＋ 位置 ＋ 期望 mode 三件一組），不依賴任何外部 schema。

最後那條反向檢查是關鍵 —— 有了它，正副本同時消失會讓 expected set 少一項，
而檔案地圖那一列還在，所以**照樣會紅**。

⚠️ 順帶記住：**`check-file-map.sh` 根本不掃 `docs/dev/tools/`**
（掃描範圍只有 `hooks/`、`scripts/`、`observability/`、`tests/parallel-stage6/`），
散發副本從來就不在它的盤點裡。第 8 點是唯一在管這件事的東西。

### 掛進 `devflow-check` 要多一層 wrapper（不能直接掛）

`scripts/devflow-check.sh` 的 `run()`（47-58 行）**純粹看 exit code：非 0 就算失敗**，
沒有任何例外邏輯。而正式工具「有共同戰場 → exit 11」是**正常結果不是失敗**，
而且它需要一個 ref 參數 —— 直接掛進聚合器一定紅。

做法：另寫一支**無參數的母版自檢 wrapper**（例如 `scripts/check-integration-regression-guard.sh`），
掛進 `group_architecture()`（95-135 行，照既有一行慣例
`run "architecture/<name>" scripts/<name>.sh || return 1`）。它做的事是：

1. 跑上面八個情境（A–H），確認正式工具在每個情境給出正確的狀態字串與 exit code
2. 跑五個 mutant（M-a~M-e），確認每個都被對應情境抓到
3. 跑模板順序守衛（③-2）
4. 跑正本／副本 parity（expected set 的算法見上面那節，
   含「正副本同時被刪也必須紅」那個 mutant）

**wrapper 自己的 exit 契約（明寫，不要靠猜）**：

| 情況 | exit |
|---|---|
| 全部 assertion 通過 | **0** |
| 情境／mutant／parity／模板順序 任一條不對 | **1** |
| 環境問題或用法錯（缺 `python3`、不在 repo 裡、正式工具檔不存在） | **2** |

⚠️ **受測工具吐出來的 10 / 11 是測試資料，不是 wrapper 的退出碼。**
wrapper 要做的是「比對正式工具在情境 A 是不是真的吐 10」——
比對成功 → wrapper 自己 exit 0。把 10/11 直接往聚合器傳就會紅，那是最容易犯的錯。

（既有的 `check-task-slicing.sh` 就是靠「自己承諾絕不非零退出」達成 warning-only，
不是 `run()` 給的豁免。照同一個做法。）

**這支 wrapper 也是一支新腳本**，所以第 6 點的檔案地圖要一起加它的列。

### 順手改掉一句過期的話

`README.md:615` 強制力對照表現在寫「沒做成散發腳本：3 行指令要動散發清單＋檔案地圖＋
N7 三處記帳，不成比例」。做完之後這句整句過期 —— 改成指向新工具，
並把強制力從「半機械」改成實況。

### H-1 的驗收

#### ① renderer 這一關，哪個檔會紅要先講清楚（不要用猜的）

**改之前先跑一次 `bash scripts/render-methodology-corrections.sh --check`，確認它是綠的**
（拿基線；不是綠的表示工作區本來就髒，停下回報）。

改完之後，各項各自會讓哪個檔紅是**確定的**，已經對照 renderer 的
`fragments` 表查過，不要靠猜：

| 改哪裡 | `--check` 會不會紅 | 紅的是哪個檔 |
|---|---|---|
| **H-1**：`_templates/7-review.md` 的 Exit Checklist | ✅ 會 | **只有 `guides/guide-quickstart.html`**（對應 `template7-exit-quickstart`）。`guide-dev-flow.html` 的 `template7-checklist` 抽的是「執行清單(」那一節，**不含** Exit Checklist，所以它不會紅 |
| **M-1**：`_templates/6-implementation-notes.md` 的執行清單步 0 | ✅ 會 | `guides/guide-dev-flow.html`（對應 `template6-checklist`） |
| **M-2**：`_templates/STATUS.md` | ❌ 不會 | STATUS 模板**不在** renderer 的 `fragments` 表裡。**不要要求它變紅**，那是正常的 |
| **M-3**：`README.md` §7「合併後出事怎麼辦」 | ❌ 不會 | renderer 只抽 README 的三段（`## 3.` 表格、「審查者產生」、「G1/G2/G3 審查與 verdict」），§7 不在其中 |

該紅的沒紅 → **停下回報，不要自己去改 html**。那表示導覽裡那段是手抄的舊副本、
不在自動同步範圍內，而 `renderer fixed point 6/6` 在改與不改的情況下都會過（假綠）。

確認該紅的都紅了之後跑 `--write` 同步，再 `--check` 回綠。

#### ② 測試必須打正式腳本，不准自己重寫一份演算法

⚠️ **這條是這一輪最容易踩的坑**：如果測試檔裡自己寫一份「正確演算法」再去驗證它，
那驗的是測試自己的副本，**正式腳本壞掉測試照樣全綠** ——
這正是這個 repo 記過的**第 3 型假綠：斷言釘在副本而不是正本**。

所以：**測試一律呼叫 `scripts/devflow-integration-regression.sh`**，
在拋棄式的臨時 git repo（`mktemp -d`，跑完 `trap` 清掉）裡建情境，然後看它的輸出與退出碼。

**八個情境**（A、B 已在沙盒實測過正確答案，其餘對應四態與各項防護）。
每個情境都要記下建圖當下的 `FORK_INTEGRATION_SHA`，用 `--fork-sha` 傳給腳本：

| 情境 | 怎麼建 | 正式腳本必須給出 |
|---|---|---|
| A · 有 incoming、零重疊 | feature 改 `a1.txt`/`a2.txt`；整合分支改 `b1.txt`/`b2.txt` | `SYNC_REQUIRED_NO_OVERLAP`、共同戰場**無**、**exit 10** |
| B · 有 incoming、有共同檔 | 兩邊都改 `shared.txt`，各自另有獨立檔 | `SYNC_REQUIRED_WITH_OVERLAP`、共同戰場**只有 `shared.txt`**（不可混入 `b1.txt`）、**exit 11** |
| C · 對方零新 commit | 開分支後整合分支完全沒動 | `N_A_NO_INCOMING`、**exit 0** |
| D · 已經 merge 過了 | 用情境 A 的圖，**先手動 merge**，再跑腳本 | `ALREADY_SYNCED`、**exit 2** —— **不准輸出 `N_A_NO_INCOMING`** |
| **G · 已經 rebase 過了** | 用情境 A 的圖，**先 `git rebase` 到整合分支最新點**，再跑腳本 | `ALREADY_SYNCED`、**exit 2`**。⚠️ **這個情境比 D 更狠** —— rebase 完的圖是**完全線性的**，連 merge commit 都沒有，任何靠「找 merge commit」的判法在這裡都會失效。只有持久化的 fork 錨點救得了 |
| E · 工作樹髒 | 情境 A 的圖，另外留一個未提交的改動 | **exit 2**，不准帶著算 |
| F · 改名 | feature 把 `x.txt` 改名成 `y.txt`；整合分支改 `x.txt` 的內容 | 共同戰場必須含 `x.txt` —— 這條在驗 `--no-renames` 真的有加 |
| **H · 缺錨點 / 錨點不合法** | ①完全不給 `--fork-sha` ②給一個不是 `INTEGRATION_SHA` 祖先的 SHA ③`--integration` 給本地 ref（不是 `refs/remotes/`） | 三種都必須 **exit 2**，**不准退回用 `merge-base` 猜**，更不准判成 `N_A_NO_INCOMING` |

#### ③ 破壞實驗：五個精確的 mutant（不做等於前面白做）

破壞的對象是**腳本的臨時複本**，不是正式腳本本身。複製到臨時目錄改壞，
再用對應情境跑那份壞的，**它必須給出錯誤答案**；如果壞掉的複本也給出正確答案，
表示情境沒有在區分好壞 —— 停下重做情境。

| mutant | 具體怎麼改壞 | 哪個情境要抓到它 |
|---|---|---|
| M-a · 兩態退化 | 把 `SYNC_REQUIRED_NO_OVERLAP` 的回傳改成 `N_A_NO_INCOMING` / exit 0 | **A** |
| **M-b · 座標污染（原始 bug 本人）** | 把持久化的 `FORK` 換回動態的 `BASE=$(git merge-base HEAD "$REF")`，其餘不動 | **D 與 G 兩個都要抓到**。⚠️ 上一版把 M-b 寫成「`"$BASE".."$FEATURE_HEAD"` 改成 `"$BASE"..HEAD`」是**無效的 mutant** —— 唯讀腳本裡這兩者行為相同，改了等於沒改 |
| M-c · 改名偵測 | 拿掉 `--no-renames` | **F** |
| M-d · 髒樹放行 | 拿掉工作樹乾淨的檢查 | **E** |
| **M-e · fail-open 退化** | 缺 `--fork-sha` 時退回用 `merge-base` 算，而不是 exit 2 | **H** —— 這條在驗 fail-closed 沒有被寫成 fail-open |

#### ③-2 另外一支守衛：釘住模板裡的順序

演算法搬進腳本之後，模板剩下的責任是「**用對的順序叫它**」——
而順序寫反正是原始 bug 的形狀，所以要有東西釘著。

**定案：這個檢查併進 H-1 的 wrapper（`scripts/check-integration-regression-guard.sh`），
不另立腳本。** 內容：在 `_templates/7-review.md` 的 Exit Checklist 那一條裡，
**「跑 `devflow-integration-regression.sh`」這段文字必須出現在「合併」與「跑全套測試」之前**。
順序被寫反 → 紅。

破壞實驗：把模板那條的順序調換，確認這支守衛會紅。

#### ④ 全套回歸

`bash scripts/devflow-check.sh all` 仍全綠（新掛的檢查也在裡面）。

---

## M-1〔中〕環境隔離「有寫要檢查，但不檢查也算完成」

**位置**：`_templates/6-implementation-notes.md`，步 0 的檢查內容在 `:23` 附近，
完成條件在 `:48`。

現在步 0 的敘述要求並行時確認容器名／對外 port／資料庫／快取等有沒有隔離
（還附了 `atlas_schema_revisions` 的實例），但「完成 =」那一行只寫：

> 完成 = 讀取清單回報 + branch 就位 + `devflow-exec.sh status` 與 `devflow-doctor.sh` 兩份輸出都貼進本檔

**隔離檢查不在完成條件裡** → 執行者可以完全不做隔離檢查，照樣勾完步 0 往下走。
這正是這個 repo 自己命名過的老毛病：**宣稱得出來、落點寫不進去**
（`_templates/7-review.md` Known Limits 節的註解就記著同一型的前科）。

**修法**：`:48` 的完成條件加**兩件**（第二件是 H-1 要用的，一起做）——

> ＋ **執行環境隔離結果已貼進本檔**：逐項寫容器名／對外 port／資料庫／快取或佇列／
> 檔案上傳目錄各自怎麼隔離的（實際值，不是「已隔離」三個字）。
> 單一 worktree、沒有並行 → 寫 `n-a：本 feature 未並行`，理由要寫出來。
>
> ＋ **`FORK_INTEGRATION_SHA` 已記進本檔**（40 碼全長）。

**步 0 的敘述要把「開 branch」寫成一個不可拆的四步動作**，不是「開好 branch 之後
再去查一下當時的 SHA 是多少」—— 事後回頭查就會查到已經前進過的點，錨點當場失效：

**一般 checkout**：

```bash
git fetch <remote>
FORK=$(git rev-parse --verify "refs/remotes/<remote>/<整合分支>^{commit}")
git switch -c <feature-branch> "$FORK"
test "$(git rev-parse HEAD)" = "$FORK"        # 不相等 = 中間出過事，停下重來
```

**用 worktree 的時候是另一組四步，不是把上面那組改一個字**：

```bash
git fetch <remote>
FORK=$(git rev-parse --verify "refs/remotes/<remote>/<整合分支>^{commit}")
git worktree add <worktree-path> -b <feature-branch> "$FORK"
test "$(git -C <worktree-path> rev-parse HEAD)" = "$FORK"
```

⚠️ **第四步一定要帶 `-C <worktree-path>`。** 少了它，`git rev-parse HEAD` 讀的是
**你現在站的那個 checkout**，不是剛建好的 worktree —— 那個驗證會通過，
但它驗的是別人。新 worktree 就算建在錯的點上也照樣放行。

⚠️ `git worktree add` 一定要明示 `"$FORK"`，不要讓它預設從當前 HEAD 建。

四步跑完，把 `$FORK` 那 40 碼寫進本檔。**開 branch 與記錨點是同一個動作的兩半**，
中間不准插別的事。

⚠️ **第二件是 H-1 的地基，不是附帶的小事。** 沒有這個持久化的錨點，
整合回歸那支腳本**在數學上就算不出正確答案**（理由見 H-1 開頭那節）——
它會 fail-closed 直接 exit 2，整條 Exit Checklist 卡死。

錨點要用**跑一次就固定下來的值**：開 branch 的當下記一次，
之後不管 merge 幾次、rebase 幾次都**不准更新它**。它記的是「歷史上的那個時刻」，
不是「現在的狀態」—— 一更新就退化成 `merge-base`，等於沒有。

**驗收**：`--check` 會讓 `guides/guide-dev-flow.html` 變紅（對應 `template6-checklist`），
`--write` 之後回綠。詳見 H-1 驗收①的對照表。

---

## M-2〔中〕STATUS「衝突結構上消失」講得太滿，而且漏了另一種競爭

**位置**：`_templates/STATUS.md:7`（規則本體）與 `:15`（「衝突是**結構上消失**，不是機率降低」）

那條規則消滅的是**分支之間**的合併衝突 —— 這部分是對的，成立。
但它沒有消滅**同一條整合分支上多個人／多個 session 同時改 STATUS** 的競爭：

- 兩個 session 各自 `git pull` → 各自改 STATUS → 先推的成功，後推的被拒（要重來）
- 更糟：兩個 session 在**同一個 checkout** 上用編輯工具各寫一次 —— 後寫的直接蓋掉先寫的，
  **沒有任何紅字**。這個 repo 自己很清楚這件事，`scripts/history-append.sh` 的目錄鎖
  就是為了 `HISTORY.md` 的同一個問題而做的；STATUS 沒有同型的保護。

**修法**（兩件都做）：

1. **措辭改準**：把「衝突是結構上消失」限定成「**分支之間的合併衝突**結構上消失」，
   並明說「同一分支上多個 writer 的競爭沒有被消滅，規則見下」。
2. **補一條寫入紀律**，寫進同一個頂註。⚠️ 不要寫成「push 被拒就重新 `pull --ff-only`」——
   **那個指令在這個情境下必然失敗**：push 被拒表示本地與遠端已經分岔，
   `--ff-only` 正是分岔時會拒絕的那個模式。正確寫法：

   - **誰改哪一列，以及責任什麼時候交接**（這兩件要一起寫，只寫前面會跟 ship 那條打架）：

     | 什麼時候 | 誰改 |
     |---|---|
     | 開工加列、階段推進、gate 更新 | 該 feature 的 **owner**（`Owner` 欄那個人） |
     | ship 移出 Active | **合併那個 PR 的人** —— 他不一定是 owner |

     交接點就是 PR 被合併的那一刻：在那之前責任在 owner，在那之後在 merger。
     **只寫「owner 改自己的列」會跟 ship 那條直接打架**，因為 merger 常常不是 owner。

   - **把窗口縮到最小**：改 STATUS 這件事要「拉最新 → 只改自己那一列 → 立刻 commit → 立刻推」
     一氣做完，不要改完放著。真正會弄丟資料的不是 git，是**兩個 session 在同一個
     checkout 上先後寫同一個檔**，後寫的直接蓋掉先寫的、**沒有任何紅字**。
     窗口越短，撞上的機會越小 —— 這是機率問題，不像分支衝突那樣可以結構上消除，
     頂註要老實這樣寫，不要再宣稱「消失」。
   - 改 STATUS 之前 `git fetch` 再 `git pull --ff-only`（**這時還沒分岔，會過**）。
   - `push` 被拒 → `git fetch` 後 **`git rebase origin/<整合分支>`**，
     只把自己那個還沒發布出去的 STATUS commit 重放上去，解完衝突再推。
     重放完**要核對整張表的列集合**，確認別人的列沒有在解衝突時被自己刪掉。
   - **這不算改寫共享歷史** —— 重放的是自己本地還沒推出去的 commit，
     跟 §7 禁止的「對整合分支 `reset --hard` / `push --force` / `rebase`」
     （那是改寫**已經推出去、別人已經拿到**的歷史）是兩件事。頂註要把這個區別講明白，
     否則照著 §7 的禁令讀，會以為連自己沒推的 commit 都不能 rebase。
   - **不准**用 `push --force` 或 `reset --hard` 解決 STATUS 的推送衝突。
   - 一句理由：看板遺失一列是**靜默**的，沒有紅字、下一個人會照著錯的狀態決策。

不要為此新增鎖腳本 —— STATUS 是「改既有的列」不是「往後追加」，
`history-append.sh` 那種追加鎖套不上來，硬套會做出一個看起來有保護、實際沒有的東西。

**驗收**：⚠️ **`--check` 不會紅，那是正常的** —— `_templates/STATUS.md` 不在 renderer
的抽取範圍裡。不要為了讓它變紅而去改別的東西。驗收改看頂註實際內容（人讀一遍），
確認這四件都寫進去了：①「分支之間」的限定詞 ②owner→merger 的交接 ③push 被拒走
`fetch` ＋ `rebase` 重放 ④「這不算改寫共享歷史」的區別。加上
`bash scripts/devflow-check.sh all` 仍全綠。

⚠️ **不准在頂註寫「已經有單一寫入者」之類的話。** 本輪做的是把窗口縮小、
把交接講清楚 —— **真正的單寫入者（或帶鎖的更新器）列在 Backlog 沒做**。
寫成「已經有」就是新的過度宣稱，跟這一項要修的毛病同一型。

首次拿 dev-flow 自己 dogfood 時，額外加一條臨時紀律並寫進當次的 6-notes：
**同一時間只准一個人改 STATUS，禁止兩個 session 共用同一個 checkout 編輯它。**

---

## M-3〔中〕「直接補修」這條例外照著做不出來

**位置**：`README.md:626`（§7「合併後出事怎麼辦」的例外欄）

現在寫：

> **例外：直接補修** | 只有同時滿足兩條才可以：①一個 commit 修得完；②不動其他 feature 碰過的檔

兩個洞：

1. **沒說補修走哪條路**。是直接 commit 到整合分支，還是開一條短命 branch 走 PR？
   同一份 README 的 Exit Checklist 又寫著「PR → develop（feature branch，禁直上 master）」，
   這個 repo 自己的實務也是每一次都走 branch + `merge --no-ff`。
   照現在的文字，兩種解讀都說得通 —— 而它們的風險差很多。
2. **沒定義「其他 feature 碰過的檔」要跟什麼比**。跟最近幾個 merge 比？
   跟所有還在 Active 的 feature branch 比？跟整合分支的全部歷史比？
   沒有範圍就沒辦法算，也就沒辦法機械檢查 —— 而這一段自己聲稱「兩條判準都可機械檢查」。

**修法**：

1. 補修**一律走短命 hotfix branch + PR**，不直接 commit 整合分支。
   一個 commit 修得完的東西開一條 branch 成本很低，換到的是有 review 與可回滾。
2. 「其他 feature 碰過的檔」定義成：**目前列在 `STATUS.md` Active 表裡的每一個 feature
   各自改過的檔的聯集**。補修的 diff 與這個聯集有交集 → 不適用「直接補修」，走正常回滾。

   ⚠️ **這個定義現在算不出來，要先補一個欄位**。`_templates/STATUS.md` 的 Active 表頭是：

   ```
   | Feature | Lane | Stage | Owner | Gates | Updated |
   ```

   **沒有任何一欄記得住 branch 或 ref**，所以「那個 feature 的 branch 是哪一條」無從得知。
   要做的事：

   - Active 表**新增一欄 `Branch`**，填**已發布的遠端 ref**（`origin/feat/order-intake`），
     **不要填 `feat/order-intake` 這種本地名** —— 本地分支只存在於某一台機器上，
     換一個 clone 就不存在，算出來的聯集會靜默少掉那個 feature。

   ⚠️ **這一欄在 Stage 1–5 填不出來**：`README.md:521-522` 明寫「尚未開 feature branch
   的規劃階段（1-5），文檔 commit 直接落 develop；**Stage 6 起手式才開 feature branch**」。
   所以規則要分階段寫，不能一句「開工加列時就要填」：

   | 階段 | `Branch` 欄填什麼 |
   |---|---|
   | Stage 1–5 | 固定填 `n-a:尚未建立 branch`（**逐字這個字串**，方便機械判定） |
   | Stage 6 起，branch 建立並推上去之後 | 換成 `origin/feat/<slug>` |

   - 算聯集時**跳過**填著那個 sentinel 的列（它們還沒有程式碼改動，本來就沒有戰場）。
   - **Stage 6 之後**那一欄還是 sentinel 或空的 → **fail-closed 停下問人**，
     不要當成「跳過」處理 —— 那會讓一個真的有改動的 feature 從聯集裡消失。
   - 算聯集之前先 `git fetch`，然後**兩端一起釘成 SHA**：每一條 feature ref 各自
     `git rev-parse`，**整合分支也要 `git rev-parse` 釘一次**（上一版只釘了 feature 那端，
     整合分支還是活的 ref，算到一半被別人推新東西就前後不一致）。
   - 對每個 feature：
     `git diff --name-only --no-renames $(git merge-base <該SHA> <整合分支SHA>)..<該SHA>`
   - **要排除正在評估的補修自己** —— 如果補修本身也有一條 branch 列在 Active 表裡，
     它一定會跟自己 100% 交集，不排除就永遠算出「不適用直接補修」。
   - 表裡列著但 ref 已經不存在（打錯字、branch 被刪）→ **停下問人**，
     不要當成空集合略過 —— 當成空集合會讓「沒有交集」這個結論建立在漏算上面。

   表頭改了之後，`_templates/STATUS.md` 頂註那句「開工加列」也要跟著提到新欄位。

   ⚠️ **表頭多一欄會讓別處的範例列過期，而且那些地方不會自動同步**（已實查）：

   | 位置 | 要不要改 |
   |---|---|
   | `_templates/STATUS.md:22` 表頭 ＋ `:24` 範例列 | ✅ 要（正本） |
   | `guides/guide-quickstart.html:409-411` 的範例列 | ✅ **要，而且要手改** —— 那段是手寫的，**不在** renderer 的抽取範圍裡（`fragments` 字典裡沒有任何 STATUS 相關的 key），所以 `--check` 不會提醒你 |
   | `README.md` 約 703 行 | ❌ 不用 —— 實查那裡只有文字提到「STATUS.md 要更新」，**沒有表格範例列** |

   另外實查到：**全 repo 沒有任何守衛在檢查 STATUS 的表頭欄位名稱**。
   所以這次改完不會有東西紅給你看，也表示下次有人改壞了同樣不會有人知道。
   **已裁決：本輪就補** —— 併進 S-1 的 `scripts/check-status-policy.sh`
   （表頭含 `Branch`、範例列欄數對得上、quickstart 範例列也跟著改），不另立腳本。

   `README.md` 約 703 行雖然沒有表格，但文字提到 STATUS 要填什麼的地方
   **也要補上 `Branch` 欄**，不要讓文字跟表頭講的不一樣。
3. 順手把 §7 那句「兩條判準都可機械檢查」改成實話：現在是**可算但沒做成腳本**，
   誰要算、用哪個指令算，寫清楚。

**驗收**：⚠️ **`--check` 不會紅，那是正常的** —— renderer 只從 README 抽三段
（`## 3.` 的表格、「審查者產生」、「G1/G2/G3 審查與 verdict」），§7 不在裡面。
不用猜、也不用去找。驗收改看：`_templates/STATUS.md` 的 Active 表頭確實多了 `Branch` 欄、
README §7 的兩個洞都補上了、`bash scripts/devflow-check.sh all` 全綠。

⚠️ 表頭多一欄可能會踩到別的檢查（有守衛在對 STATUS 的欄位做文章的話）。
`devflow-check` 紅了就照它的訊息修，**不要為了讓它綠而把欄位改回去** ——
真的卡住就停下回報。

---

## L-1〔低〕拆出來的九條審核檔還留著舊上下文

**位置**：`notes/review-requirement-discovery-gaps.md:22-24`

那段是從舊派工單原地搬過來的，還寫著「本區」「上面『已定的四項』」「本派工單授權範圍」
「上面的觸發句」—— 這些東西在拆出來的獨立檔裡**一個都不存在**，
讀到的 agent 會去找一個不存在的上文，判斷可能歪掉。

**修法**：那三句換成不依賴上文的一句話：

> **本檔不是派工單。未經 owner 逐條裁決，不得實作本檔的任何一條。**

檔案開頭已經有 `⛔ 這份不是派工單，不要照著做` 的完整說明（含暫緩理由與處理順序），
不要重複，只要把 `:22-24` 這段殘留清乾淨。

---

## S-1〔中〕新規則只寫進給別人用的模板，母版自己那份沒套

這條不是 codex 找到的，是主線程盤點時抓到的。

上一輪定的規則是「STATUS.md 只在整合分支維護，feature branch 一律不碰」，
寫進了 `_templates/STATUS.md:6-19`（給採用專案的模板）。

但**母版自己那份 `docs/dev/STATUS.md` 沒有這條規則**，也沒有任何一支守衛在對帳兩份。
結果是：寫下規則的那一輪，下一個 commit 就自己破了例 ——

```
dcca20a docs(status): 並行制度空白輪收帳      ← 在 feature branch 上改 docs/dev/STATUS.md
2c98d25 docs(parallel): 補四個制度空白        ← 規則就是這個 commit 寫進去的
```

這是這個 repo 已經定名過的**第 6 型假綠：不對稱保護 —— 修法只套觸發它的那一個實例**，
只是這次不對稱的兩端變成「散發給別人的模板」與「母版自己在用的那份」。
這次沒出事只是因為當時只有一條分支在跑。

**修法**：

1. `docs/dev/STATUS.md` 的頂註加上同一條規則（可以精簡，但**必須包含**：
   只在整合分支維護、feature branch 不碰、ship 移出 Active 由合併 PR 的人在合併後做）。
   M-2 補的寫入紀律也要一起帶過去，兩份不要有第二種說法。
2. **加一支守衛 `scripts/check-status-policy.sh`**，做三件事：
   - 確認 `_templates/STATUS.md` 頂註裡的規則要點在 `docs/dev/STATUS.md` 也存在。
     **不要比對逐字**（兩份用途不同，硬釘逐字會天天假紅），釘「規則要點都在」即可。
   - 確認 `_templates/STATUS.md` 的 Active 表頭含 `Branch` 欄，且範例列的欄數對得上。
   - 確認 `guides/guide-quickstart.html:409-411` 的範例列欄數也跟著改了
     （那段是手寫的，renderer 不會幫你同步 —— 見 M-3）。
   掛進 `scripts/devflow-check.sh` 的 `group_architecture()`。
3. **破壞實驗**（三個都要）：①把 `docs/dev/STATUS.md` 的規則段刪掉 ②把表頭的
   `Branch` 欄拿掉 ③只改模板不改 quickstart 範例列 —— 三種都必須紅。不紅就是白做。

---

## S-2〔中〕防「不對稱記帳」的那支守衛，自己就是不對稱記帳的活標本

實查 `scripts/check-file-map.sh` 發現的，兩個 codex 版本說法不同，實情是兩邊各對一半：

```python
# 註解（第 96-101 行）：
#   「一律等於當下實際值，不是『大概抓個下限』；新增/刪除必列檔時同步改這個常數
#     ……還要同步改 test-architecture-guards.sh 的靜態互釘清單那一行」
MIN_CHECKS = 68
if scanned < MIN_CHECKS:      # ← 但程式碼只比「小於」
```

實跑：

```
✅ PASS：forward 74 支必列檔 …… scanned=74
```

**註解說「一律等於當下實際值」，程式碼只驗地板，實際值早就漂到 74 —— 差了 6 支，
而且一路綠燈。** 這支守衛存在的目的就是防第 7 型（清單沒跟著長），結果它自己
就是一個活體標本，而且沒有任何東西在看它。

**修法**：

1. 常數改名 **`EXPECTED_MAPPED_FILES`**（它數的是「必須列進檔案地圖的檔案數」，
   叫 `CHECKS` 會讓人以為是檢查項數），比較改成 `!=`（精確值，不是地板）。
   數字設成**本輪做完之後的實際值** —— 現況 74 ＋ 本輪新增三支 = **77**。
   不要憑這裡寫的數字，**以實跑輸出為準**（做完跑一次 `bash scripts/check-file-map.sh`
   看 `scanned=` 是多少就填多少）。
2. `scripts/test-architecture-guards.sh:1535` 的靜態互釘釘的是 `MIN_CHECKS = 68`
   這串字 —— **改名 ＋ 改值 = 那串字兩處都變**，同一個 commit 一起改，否則它會紅。
   （它紅是設計如此，不是壞了 —— 但要在改的當下就處理掉。）
3. 保留「真實刪檔時要下修」的錯誤訊息，把它擴成雙向：多了要上修、少了要下修。
4. **破壞實驗**：⚠️ 「丟一個沒列進地圖的 `.sh`」**是無效的 mutant** ——
   舊版的 forward 檢查（每支必列檔都要在地圖裡找得到）本來就會紅，
   驗不出新的精確計數有沒有生效。

   **正確的 mutant：同時新增腳本「和」它的檔案地圖列，但故意不更新
   `EXPECTED_MAPPED_FILES`。** 這種情況下 forward 與 reverse 兩個方向都對得上，
   **只有精確計數抓得到**；舊的地板版在這裡是綠的。驗完把三樣都還原。

---

## 做完之後的驗收（全部都要跑，輸出貼進回報）

```bash
bash scripts/render-methodology-corrections.sh --check     # 必須綠（--write 之後）
bash scripts/devflow-check.sh all                          # 必須 REPO_REFERENCE_PASS 全過
bash hooks/selftest.sh                                     # 全過（項數以腳本輸出為準，不寫死）
env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
bash hooks/devflow-exec.sh doctor                          # COMPATIBLE
bash scripts/check-gate-twin.sh                            # 全過
```

另外還要確認：

- `diff -q devflow-contract.json docs/dev/devflow-contract.json` 靜默
- **散發副本與正本逐一相同** —— ⚠️ 不要在任何文件裡寫「四支」或「五支」這種數字。
  本輪新增一支之後，凡是**寫死支數**的地方立刻就過期了，而過期的清單正是
  這個 repo 命名過的**第 7 型假綠**（照著清單健檢的人，會把真實存在的檔判成多餘）。
  做法：對帳靠**掃目錄**得出，或靠第 5 個記帳點新增的那支 parity 守衛，
  數字由腳本輸出，不寫進活文件。回報時貼腳本輸出，不要自己打數字。
- `git status --short` 為空
- **版號仍是 3.8.0**（`.claude-plugin/plugin.json` 與 `hooks/runtime-capabilities.json` 兩處都是）

### 收帳

- `scripts/history-append.sh` 追加一筆（做了什麼／為什麼／落在哪）。
  **`--version` 要帶 `v3.8.0`** —— 這一輪修的是一個**還沒發布出去的版本**，
  不是修一個已上線版本的後續 patch。條目文字要講清楚這件事，
  否則往後看歷史會以為 v3.8.0 上線過又被修
- 硬約束 1.5 那個一次性的 bootstrap 例外（在 feature branch 上改 `docs/dev/STATUS.md`）
  的理由**要寫進這筆 HISTORY**，不要只寫在 commit message 裡
- **不要 push、不要 tag、不要發 release**

#### 收帳的重頭戲：把「還欠什麼」收攏成一份，別再散在三個地方

現在要知道 dev-flow 還欠什麼，得同時看三個地方：`docs/dev/STATUS.md` 的 Backlog、
本檔尾節那張表、`notes/review-requirement-discovery-gaps.md`。
**而 `docs/dev/STATUS.md` 自己開頭就寫著它的職責是回答「現在誰在做什麼、還有什麼沒做」**——
現在它答不全，這是同一型的記帳不一致，只是規模小。

**定案：`docs/dev/STATUS.md` 的 Backlog 是待辦的唯一正本。**
本檔是一次性派工單，做完就過期，不該當長期清單。

本輪收帳時，把下面這幾條**補進 `docs/dev/STATUS.md` 的 Backlog**
（現在只活在本檔尾節，STATUS 裡沒有）：

| 級 | 一句話 | 來源 |
|---|---|---|
| A | v3.8.0 推上去 ＋ 打 tag ＋ 發 release ＋ 確認 CI 綠 —— 本輪修完就該做，是目前唯一的 A 級 | 發版流程第 6–8 步 |
| B | owner 親自打開 gate twin 產出的 html 驗收「好不好審」，b8 的 verdict 才能從 `REQUEST_CHANGES` 改掉 —— **這件事只有 owner 做得了** | `docs/dev/b8-gate-twin-review-ui/7-review.md:5,180,181` |
| B | 散發清單收斂成一份正本（source／destination／mode），讓 dev-setup 的 install／check／baseline、dev-release、parity、檔案地圖全部讀同一份 | 本檔 H-1 的八個記帳點 |
| B | STATUS 真正的單寫入者（或帶鎖的更新器）—— 本輪只縮小了窗口，沒消除同 checkout 的靜默互蓋 | `_templates/STATUS.md` 頂註、本檔 M-2 |
| C | `engine-fence-masking` 功能早就合進 main，收尾文書沒關（狀態還是 `draft`，Exit Checklist 尚未收尾，見該檔第 106–111 行）。**不要寫死未勾的項數** —— 數字會漂 | `docs/dev/engine-fence-masking/7-review.md:4,106-111` |
| C | 用 Bash 寫檔只有「事後偵測」沒有「當場攔下」（Edit 那條路有擋），文中說要開 ticket 或記 STATUS —— 兩件都沒做 | `docs/dev/engine-fence-masking/7-review.md:100` |

STATUS 裡**已經有的四條不要動**（full lane 觀測、九條需求缺口裁決、第二個範例 feature、
SDC 大表／Reference App），它們的裁決與理由都還有效。

⚠️ **只是「記」進去，不是「做」**。上面六條**沒有一條**是本輪要動手的
（其中兩條根本只有 owner 做得到）。補完之後 STATUS 的 Backlog 應該是 **10 條**：
原有 4 ＋ 新補 6。

⚠️ 順序照 A → B → C 排，同級之間把「擋住別人」的放前面。
`notes/review-requirement-discovery-gaps.md` 那九條**不要搬全文**，
STATUS 裡已經有一行指標指過去了，那樣就夠。

---

## 不要做

- 不要 bump 版號到 3.8.1
- 不要動 Stage 1–4 模板
- 不要重新評估上一輪那四項決定本身（決定是對的，錯的只有 H-1 的**執行演算法**）
- 不要碰 `notes/review-requirement-discovery-gaps.md` 除了 L-1 那三行以外的任何內容
- 不要順手收 `docs/dev/engine-fence-masking/7-review.md` 的文書（那是另一件事，見下）
- 不要動 `execution.mode: parallel` 那套 T 級並行機制
- 新腳本**不准動樹**（不准 `git merge` / `rebase` / `checkout` / 寫任何檔到 repo 裡），
  它只算與只判；合併與跑測試是人的事
- 不要自創腳本的參數形式與輸出格式，照 `scripts/check-gate-twin.sh` 與
  `scripts/check-history-integrity.sh` 的既有慣例
- 不要在任何文件裡寫死散發副本的支數（第 7 型假綠）

---

## owner 已裁決的三件（**紀錄，不是問題** —— 不要停在這裡等人）

這三件曾經是決策點，2026-08-18 已由 owner 全部拍板。寫在這裡是為了讓你知道
「為什麼要這樣做」，不是要你回頭確認。

### D-1 · 整合回歸做成散發腳本 —— **已裁決：做**

`README.md:615` 的強制力對照表現在還寫著：

> Exit Checklist 整合回歸(條件式) | 半機械 —— **沒做成散發腳本：3 行指令要動散發清單＋檔案地圖＋N7 三處記帳，不成比例**

**這個成本判斷已經被推翻。** 當初判「不成比例」的前提是「不過是 3 行指令，人照著打就好」——
結果它不只 3 行、而且是錯的，六輪審查沒抓到。修正版要先釘死三個 SHA、
存兩份檔案清單、順序不能錯、還要防 ref 漂移。這種東西寫成文字讓人照打，
每一次都是一個出錯機會。

規格見上面「H-1 附帶」那節。那段 README 的文字本輪一併改掉。

### D-2 · 上一輪派工單的錯誤演算法怎麼標 —— **已裁決：原文保留＋加更正框**

`notes/dispatch-parallel-feature-gaps.md:149` 是已完成輪次的紀錄，
「不動歷史文件內容」是上一輪的硬約束。裁決是**保留原文、在下面加更正框**，
留痕完整，看得到「當初錯在哪、後來怎麼修」。做法見上面「也要改的第二個位置」。

**不要把原文改掉。**

### D-3 · 本檔怎麼進版本控制 —— **已裁決：branch commit，不 push**

本檔已經由主線程走 branch → `merge --no-ff` 回 `main` 的流程 commit 進去了，
**沒有 push**。所以你從 `main` 開 `fix/v380-blockers` 就看得到它。

---

## 這一輪不做、但欠著的事

**清單不放在這裡** —— 放在「收帳」那節，而且收帳的動作就是把它們寫進
`docs/dev/STATUS.md` 的 Backlog（待辦的唯一正本）。

同一份清單抄兩個地方，下次只改一邊就開始漂移 —— 這正是本檔 S-1 在修的病，
不要在同一份派工單裡再犯一次。

兩件事在這裡補充，收帳節沒講：

- **本輪不做散發清單收斂與 STATUS 單寫入者的理由**：前者是既有債的重構，
  不擋 v3.8.0 正確，硬塞進來會讓這一輪再開一輪；後者是 v3.8.0 之前就存在的風險，
  不是這一版帶進來的，而且做帶鎖更新器等於新開一支工具。
- **`docs/dev/STATUS.md` 裡已經有的四條**（full lane 觀測、九條需求缺口裁決、
  第二個範例 feature、SDC 大表／Reference App）**本輪一個字都不要動** ——
  它們的裁決與理由都還有效。

---

## 回報格式

1. 每一項（H-1 / M-1 / M-2 / M-3 / L-1 / S-1 / S-2）各一段：改了哪些檔（`檔案:行號`）、
   實際跑了什麼指令、輸出原文。
2. 驗收那六道的輸出原文全貼。
3. 破壞實驗的結果，逐個列：H-1 的八個情境（A–H）、五個 mutant（M-a~M-e）、
   模板順序守衛、正副本同時刪除、S-1 的三個、S-2 的一個。
   每個都要寫「弄壞什麼 → 有沒有真的變紅」。**沒做破壞實驗的守衛一律當成沒做**。
4. 八個記帳落點逐一交代做了什麼（特別是第 3 點 baseline 與第 5 點
   `dev-release` 的寫死五個 diff —— 這兩處最容易漏），加上 wrapper 掛進聚合器的結果。
5. **`docs/dev/STATUS.md` 的 Backlog 補完之後貼出來**（整張表），並說明是幾條 ——
   預期 10 條（原有 4 ＋ 新補 6）。不是 10 條就說明為什麼。
6. 有沒有發現本檔沒提到的問題 —— 列出來問要不要處理，**不要自己動手**。

**每一個結論都要對應到你自己實際跑過的指令與看到的輸出。**
沒跑過的就寫「未驗證」，不准用推論代替。
