# 派工單：v3.8.0 發版前必修（整合回歸演算法錯誤 ＋ 五條補強）

> **觸發句**：`讀 ~/dev/dev-flow/notes/dispatch-v380-blockers.md 照它跑，全程不打斷問人`
>
> 本檔是**派工單**，讀完就照做。**全部六項都已由 owner 裁決完畢，沒有要回頭問的事。**
> 三個曾經是決策點的東西已經定案，記在末節「owner 已裁決的三件」——
> 那節是**紀錄**不是問題，不要停在那裡等人。
>
> 唯一該停下回報的情況：本檔寫的東西與現場實況對不上（例如指定的行號找不到、
> 指定的檔案不存在、驗收條件互相矛盾）。那種時候停下說清楚，不要自己猜著做。

---

## 這份要解決什麼

上一輪（`notes/dispatch-parallel-feature-gaps.md`）把「多 feature 並行的四個制度空白」寫進了母版，
本機五道檢查全綠、v3.8.0 的 release commit 也建好了。**但東西還沒推上去** ——
`origin/main` 停在 v3.7.1、沒有 `v3.8.0` tag、沒有 GitHub release、這 7 個 commit 從沒跑過 CI。

**這是好事，因為那一版裡面有一條指令是壞的。**

跨家族第二意見（codex）審出 1 高 3 中 1 低，主線程另外抓到 1 條不對稱。
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

```bash
git fetch origin                                # 先把對方的最新狀態抓下來

# ── 動樹之前先定錨（三個都要，缺一不可）──
BASE=$(git merge-base HEAD <整合分支>)          # 分岔點
FEATURE_HEAD=$(git rev-parse HEAD)              # 我這條線的最新點
INTEGRATION_SHA=$(git rev-parse <整合分支>)     # 對方的最新點 —— 釘死成 SHA

# ── 判定要不要跑 ──
git log "$BASE..$INTEGRATION_SHA"               # 為空 = 你是第一個合的 → 記 n-a 即勾

# ── 非空才往下：先算交集（此時工作樹還沒被動過）──
TMPDIR_IR=$(mktemp -d); trap 'rm -rf "$TMPDIR_IR"' EXIT
git diff --name-only --no-renames "$BASE".."$FEATURE_HEAD"    | sort > "$TMPDIR_IR/feature.txt"
git diff --name-only --no-renames "$BASE".."$INTEGRATION_SHA" | sort > "$TMPDIR_IR/integration.txt"
comm -12 "$TMPDIR_IR/feature.txt" "$TMPDIR_IR/integration.txt"   # ← 這才是共同戰場

# ── 交集逐檔看過之後，才動樹。合併的是「剛才檢查過的那個 SHA」，不是會跑的 branch 名 ──
test "$(git rev-parse <整合分支>)" = "$INTEGRATION_SHA" || echo "整合分支已經動了 → 全部重算"
git merge "$INTEGRATION_SHA"                    # 或 git rebase "$INTEGRATION_SHA"
# 然後跑一次全套測試
```

三個容易被忽略、但一定要寫進模板的細節：

| 細節 | 為什麼 |
|---|---|
| **合併的是 `$INTEGRATION_SHA`，不是 branch 名** | 你在第 3 步釘死了 SHA、照它算完交集，但如果第 6 步寫 `git merge <整合分支>`，中間別人又合進來的話，**實際併進來的內容跟你剛才檢查過的不是同一份**。動樹前那行 `rev-parse` 比對就是在攔這件事：對不上就整段重算，不要「反正差不多」 |
| **`--no-renames`** | git 預設會把改名偵測成 rename，兩邊的偵測結果可能不一致（一邊認出來、一邊沒有），交集就會漏。關掉之後改名一律顯示成「舊路徑消失＋新路徑出現」，兩邊口徑一致 |
| **`mktemp -d` ＋ `trap` 清掉** | 不准用 `/tmp/feature-files.txt` 這種固定檔名 —— 兩個 worktree 同時跑就會互相覆蓋，而且**不會有任何錯誤訊息**，兩邊都拿到對方的清單還以為是自己的 |

模板裡除了換掉指令，還要把**順序反轉**寫清楚：
原本是「合併 → 測試 → 算交集」，改成「**算交集 → 合併 → 測試**」，
並加一句警語說明為什麼不能在合併後算（合併後 `HEAD` 已含對方內容，
`merge-base` 也已漂移，兩個座標都被污染）。

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

#### CLI 契約

```
用法：devflow-integration-regression.sh <整合分支>
      （在 feature branch 的工作樹裡跑；<整合分支> 例如 develop 或 main）

exit code：0 = 沒有共同戰場，或不必跑（你是第一個合的）
           1 = 有共同戰場，逐檔看過才可以勾 Exit Checklist
           2 = 環境問題（不在 git repo 裡／參數錯／指定的分支不存在）
```

輸出要包含這幾樣（給人看，也給 7-review 貼證據用）：

- 三個座標的實際 SHA：`BASE` / `FEATURE_HEAD` / `INTEGRATION_SHA`
- 判定結果：`n-a（你是第一個合的）` 或 `需要檢查`
- 共同戰場的檔案清單（一行一個），沒有就明確印「共同戰場：無」
- 最後一行印一句可以直接貼進 7-review 的結論

檔頭照這個 repo 的既有慣例寫成三段式（規格正本引用 ／ 用法 ／ exit code），
本體用 `python3 - <<'PY'` heredoc、`check(cond, label, detail)` 累計、
分組印 `-- 分組名 --` —— 照 `scripts/check-gate-twin.sh` 與
`scripts/check-history-integrity.sh` 的樣子寫，**不要自創一套**。

#### 新增一支散發腳本要動的記帳點（**五處，漏一個就會紅或假綠**）

這個 repo 有「第 7 型假綠：不對稱記帳」的前科 —— 保護長大了、列舉它的清單沒跟著長。
以下每一處都要動：

| # | 落點 | 要做什麼 |
|---|---|---|
| 1 | `skills/dev-setup/SKILL.md` **install** 路徑 | 照 `devflow-evidence-gauntlet.sh` 的散發寫法（104-107 行附近）加一段散發本腳本 |
| 2 | `skills/dev-setup/SKILL.md` **check（健檢）** 路徑 | 加一個編號檢查項：存在 ＋ 與正本 `diff` ＋ **可執行位元**。照第 9 項（232-237 行）的樣子寫。<br>⚠️ **upgrade 路徑不用動** —— 115-116 行已經寫「整個 `docs/dev/tools/` 覆蓋」，新檔自動涵蓋 |
| 3 | 檔案地圖 `guides/guide-dev-flow.html` 的 `id="filemap"` 節（1742 行起） | 加兩列（正本一列、散發副本一列）。**同時** `scripts/check-file-map.sh:102` 的 `MIN_CHECKS = 68` 要 +1 |
| 4 | `scripts/test-architecture-guards.sh:1535` 的靜態互釘 | 那裡有一行 `check_static_pin "scripts/check-file-map.sh" "MIN_CHECKS = 68" ...` 是**逐字比對**。第 3 點改了數字這裡沒跟著改，**這條會直接紅**。兩個一起改 |
| 5 | 新增 parity 對帳 | 正本與散發副本要有守衛比對**內容 ＋ 可執行位元**。照 `scripts/check-history-integrity.sh:119-125`（H5）的寫法 —— 那支是目前唯一有驗可執行位元的，`check-gate-twin.sh` 的 N7 只驗內容 |

再加一處掛載：`scripts/devflow-check.sh` 的 `group_architecture()`（95-135 行），
照既有一行慣例 `run "architecture/<name>" scripts/<name>.sh || return 1` 掛進去。

順手把 `README.md:615` 強制力對照表那一格改掉 —— 它現在寫「沒做成散發腳本：
3 行指令要動散發清單＋檔案地圖＋N7 三處記帳，不成比例」。做完之後那句話整句過期，
改成指向新腳本，並把強制力從「半機械」改成實況。

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

兩個情境（都已在沙盒實測過正確答案）：

| 情境 | 怎麼建 | 正式腳本必須給出 |
|---|---|---|
| A · 零重疊 | feature 改 `a1.txt`/`a2.txt`；整合分支改 `b1.txt`/`b2.txt` | 共同戰場**無**，exit 0 |
| B · 真的有共同檔 | 兩邊都改 `shared.txt`，各自另有獨立檔 | 共同戰場**只有 `shared.txt`**（不可混入 `b1.txt`），exit 1 |

#### ③ 破壞實驗（不做等於前面白做）

破壞的對象是**腳本的臨時複本**，不是正式腳本本身：

1. 複製一份正式腳本到臨時目錄，把裡面的演算法改回舊版（合併之後才算交集）
2. 用同一組情境 A 跑那份壞掉的複本
3. **它必須給出錯誤答案**（把 `b1.txt`/`b2.txt` 誤報成共同戰場）

如果壞掉的複本也給出正確答案，表示情境沒有真的在區分兩種演算法 —— 停下重做情境。

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

**修法**：`:48` 的完成條件加第四件 ——

> ＋ **執行環境隔離結果已貼進本檔**：逐項寫容器名／對外 port／資料庫／快取或佇列／
> 檔案上傳目錄各自怎麼隔離的（實際值，不是「已隔離」三個字）。
> 單一 worktree、沒有並行 → 寫 `n-a：本 feature 未並行`，理由要寫出來。

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

   - **指定單一 updater**：每個 feature 的 STATUS 列由**它自己的 owner** 改
     （欄位就在表裡），別人不要代改。多數競爭在這一步就沒了。
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
的抽取範圍裡。不要為了讓它變紅而去改別的東西。驗收改看：頂註實際內容（人讀一遍，
確認「分支之間」的限定詞、單一 updater、rebase 那條路徑、以及「這不算改寫共享歷史」
的區別都寫進去了），加上 `bash scripts/devflow-check.sh all` 仍全綠。

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

   - Active 表**新增一欄 `Branch`**，填該 feature 的正式 ref（例如 `feat/order-intake`），
     worktree 也照樣填它 checkout 的那條。這一欄**開工加列時就要填**，不是事後補。
   - 算聯集之前先 `git fetch`，然後把每一條 branch 各自 `git rev-parse` **釘成 SHA** 再算，
     理由跟 H-1 同一個：branch ref 在你算的過程中會動。
   - 對每個 feature：
     `git diff --name-only --no-renames $(git merge-base <該SHA> <整合分支>)..<該SHA>`
   - 表裡列著但 branch 已經不存在（打錯字、branch 被刪）→ **停下問人**，
     不要當成空集合略過 —— 當成空集合會讓「沒有交集」這個結論建立在漏算上面。

   表頭改了之後，`_templates/STATUS.md` 頂註那句「開工加列」也要跟著提到新欄位。
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
2. **加一支守衛對帳兩份**：確認 `_templates/STATUS.md` 頂註裡的規則要點在
   `docs/dev/STATUS.md` 也存在。**不要比對逐字**（兩份用途不同，硬釘逐字會天天假紅），
   釘「規則要點都在」即可。掛進 `scripts/devflow-check.sh`。
3. **破壞實驗**：把 `docs/dev/STATUS.md` 的規則段刪掉，確認守衛會紅。不紅就是白做。

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

- `scripts/history-append.sh` 追加一筆（做了什麼／為什麼／落在哪）
- `docs/dev/STATUS.md` 的 Backlog 反映剩下什麼
- **不要 push、不要 tag、不要發 release**

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

## 這一輪不做、但欠著的事（給 owner 看，不要動手）

| 級 | 一句話 | 位置 |
|---|---|---|
| A | v3.8.0 推上去 ＋ 打 tag ＋ 發 release ＋ 確認 CI 綠 —— **等本輪修完才做** | 發版流程第 6–8 步 |
| B | 拿 dev-flow 自己跑一次完整七站當觀測實驗 | `docs/dev/STATUS.md:51` |
| B | owner 親自打開 gate twin 產出的 html 驗收「好不好審」，b8 的 verdict 才能從 `REQUEST_CHANGES` 改掉 | `docs/dev/b8-gate-twin-review-ui/7-review.md:5,180,181` |
| C | `engine-fence-masking` 功能早就合進 main，收尾文書沒關（狀態還是 `draft`，Exit Checklist 5 項沒勾） | `docs/dev/engine-fence-masking/7-review.md:4,106-111` |
| C | 用 Bash 寫檔只有「事後偵測」沒有「當場攔下」，文中說要開 ticket 或記 STATUS —— 兩件都沒做 | `docs/dev/engine-fence-masking/7-review.md:100` |

---

## 回報格式

1. 每一項（H-1 / M-1 / M-2 / M-3 / L-1 / S-1）各一段：改了哪些檔（`檔案:行號`）、
   實際跑了什麼指令、輸出原文。
2. 驗收那六道的輸出原文全貼。
3. 破壞實驗的結果（H-1 的兩個情境、H-1 的壞掉複本、S-1 的守衛）：
   弄壞什麼、有沒有真的變紅。**這三個缺一不可**。
4. 五個記帳落點逐一交代做了什麼（含 `MIN_CHECKS` 從幾改到幾、
   `test-architecture-guards.sh` 的靜態互釘有沒有跟著改）。
5. 有沒有發現本檔沒提到的問題 —— 列出來問要不要處理，**不要自己動手**。

**每一個結論都要對應到你自己實際跑過的指令與看到的輸出。**
沒跑過的就寫「未驗證」，不准用推論代替。
