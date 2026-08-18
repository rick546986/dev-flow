# 派工單：補上兩個守衛的反證（v3.8.0 發版前，最後一件）

> **觸發句**：`讀 ~/dev/dev-flow/notes/dispatch-v380-counterproof.md 照它跑，全程不打斷問人`
>
> 本檔是**派工單**，讀完就照做。三項都已由 owner 裁決完畢，沒有要回頭問的事。
>
> **範圍極窄：只補「證明守衛會紅」的測試，不碰任何產品邏輯。**
> 如果你發現自己想改 `hooks/devflow-python-lib.sh` 的解析式、
> 或 `scripts/devflow-integration-regression.sh` 的參數解析 —— **停下回報**，
> 那兩支現在是對的（下面有實測數據），本輪不准動它們。

---

## 這份要解決什麼

上一輪（`notes/dispatch-v380-landing.md`）十七項全部做完，機械驗收全綠：

```
devflow-check all 全過 ｜ selftest 378/378 ｜ gate-consistency 14/14 ｜ doctor COMPATIBLE
renderer 6/6 ｜ 整合回歸守衛 36 項 ｜ STATUS 對帳 30 項 ｜ dev-setup discipline 15 項
file-map 78 支 ｜ 版號 3.8.0 未 bump ｜ Stage 1–4 零 diff ｜ Backlog 13 條
```

主線程另外做了四個破壞實驗，守衛都真的紅了（CI 靜態禁寫死／順序守衛／actor／地板 AST 外釘）。

**但有兩個守衛「只證明現版是對的，沒證明壞版本會被抓到」** ——
而它們守的正好是這一輪的兩個核心修復：**參數死迴圈**與 **Windows 可攜**。

這個 repo 的整套文化建立在破壞實驗上：**沒有反證的保護等於沒有保護**。
現在不補，下次有人改壞不會有任何人知道。

---

## 硬約束

0. **開工第一件事**：從 `main` 開一條工作 branch `fix/v380-counterproof`，
   不要在 `main` 上直接動手。做完 `git merge --no-ff` 回 `main`。
1. **不打 tag、不發 release。push 由 owner 自己跑**（他的設定擋掉 agent 推 main，
   那是刻意的護欄）。收尾動線見文末。
2. **不准改任何產品邏輯**。本輪只准動這四個檔：
   - `scripts/check-integration-regression-guard.sh`（E-1，加 mutant）
   - `.github/workflows/runtime-selftest.yml`（E-2，加一面檢查）
   - `scripts/check-file-map.sh`（E-3，**只改註解**，常數不准動）
   - `scripts/test-architecture-guards.sh`（E-1 連帶：地板數字同步）
   想動第五個檔就是偏離範圍，**停下回報**。
3. **不准 bump 版號**（維持 3.8.0，兩處都不要碰）。
4. **不准新增任何檔案**。
5. `docs/dev/HISTORY.md` 只能用 `scripts/history-append.sh` 追加。
6. **不准在工作 branch 上碰 `docs/dev/STATUS.md`**（它只在 `main` 上改，見收尾）。

---

## E-1〔高〕整合回歸守衛缺三個 mutant，只驗現版不驗壞版本

**位置**：`scripts/check-integration-regression-guard.sh`

### 現況（主線程實查）

- `grep -n "M-f\|M-g\|M-h"` → **零命中**，三個 mutant 全部缺席
- `MUTANTS` 字典只有上一輪的 `M-a` ~ `M-e`
- 情境 I 的十個子案（`I①`~`I⑩`）寫得很完整，但 `run_usage_case` **硬編碼呼叫真實
  `TOOL`**，從來沒對「改壞的臨時複本」跑過

**後果**：情境 I 只證明「現版行為正確」，不證明「守衛能分辨壞版本」。
guard 自己的判斷式被改壞（例如 `rc == 2 and "用法" in out` 誤成 `or`、
或逾時值被改小到誤判），**沒有任何測試會發現**。

### 現版是對的，不要動它

主線程實測（`/bin/bash` 3.2 與 homebrew `bash` 5.2，每案 5 秒逾時），
九種參數排列**全部 `rc=2` 且訊息含「用法」，零 TIMEOUT**：

```
（無參數） --integration  --fork-sha  --integration origin/main --fork-sha
--fork-sha abc --integration   --no-fetch --integration
--integration origin/main --fork-sha --no-fetch   --integration "" --fork-sha abc   --bogus
```

**所以 E-1 缺的是自動化的反證，不是修 bug。**

### 修法：照既有 `MUTANTS` 的寫法補三個

既有機制是「字串替換造臨時壞複本 → 跑對應情境 → 壞複本必須給出錯誤答案」，
照同一個模式加：

| mutant | 改壞什麼 | 哪些子案必須抓到 |
|---|---|---|
| **M-f · 死迴圈回歸** | 整段參數解析換回舊寫法（`--integration) INTEGRATION_ARG=${2:-}; shift 2 ;;` 那種靠 `shift 2` 回傳值的版本） | **I②、I③ 至少要因逾時而紅** |
| **M-g · 吞旗標** | 只拿掉「值不得是另一個 `--*` 旗標」那道檢查 | **I⑦** |
| **M-h · 吞空值** | 只拿掉「值不得為空字串」那道檢查 | **I⑨ 或 I⑩** |

⚠️ **M-f 的實測注意**：主線程手動造過這個 mutant，`--integration` 與 `--fork-sha`
兩個排列確實會 TIMEOUT，但 `--integration origin/main --fork-sha` 在壞複本上是
`rc=1` 而不是逾時。**所以 M-f 的判定不要寫成「所有子案都必須逾時」**，
寫成「**I② 與 I③ 必須逾時**」即可；其餘子案在壞複本上的行為不穩定，別當斷言。

⚠️ 情境 I 現在是「一個 scenario 跑十個子案」，而既有 `mutant_case()` 的介面是
單一情境單一判定。要嘛擴充 `mutant_case()` 讓它能吃多子案，要嘛為情境 I 另寫一個
對應的 mutant 迴圈 —— **做法自訂，但不准為了好寫而放寬斷言**。

### E-1 連帶：地板要跟著長

補完 mutant 之後 `check-integration-regression-guard.sh` 的檢查數會增加，
所以兩處要同步（不同步的話，把新 mutant 刪掉不會有任何訊號）：

1. 該檔自己的 `MIN_CHECKS` 地板常數
2. `scripts/test-architecture-guards.sh` 釘它的那一行**逐字互釘**

**數字以實跑輸出為準**，不要照本檔算。

### E-1 驗收

- `bash scripts/check-integration-regression-guard.sh` 全過，項數比 36 多
- **反證的反證**：把 M-f 的替換字串改成一個「其實沒改壞」的內容（例如替換成原文），
  確認守衛會報「mutant 沒有被抓到」之類的失敗 —— 證明 mutant 機制本身有在運作，
  不是永遠印綠。做完把它改回來
- `bash scripts/test-architecture-guards.sh` 全過（地板互釘同步了）

---

## E-2〔中〕CI 沒有驗「解析會退回 PATH」，Windows 的修復被拿掉也不會紅

**位置**：`.github/workflows/runtime-selftest.yml` 的「直譯器解析回歸」那一步

### 錯在哪

現在三面檢查是：

1. 靜態禁寫死：`grep -rn "/usr/bin/python3" hooks/ … | grep -v "devflow-python-lib.sh"`
2. 缺直譯器 fail-open：`DEVFLOW_PYTHON=/nonexistent/python3 …` → rc=0 ＋ 警告
3. 覆寫通道跑自測：`DEVFLOW_PYTHON=$(command -v python3) bash hooks/selftest.sh`

**第 2、3 面都顯式設了 `DEVFLOW_PYTHON`**，直接短路 `${DEVFLOW_PYTHON:-…}` 的預設值 ——
**從來沒走到 `[ -x /usr/bin/python3 ] || command -v python3` 這個 fallback 分支**。

而那一步自己的註解寫著「證明解析邏輯會退回 PATH」，實際上沒驗。

### 主線程實測：三面全綠，一個都沒抓到

把解析退化成下面這樣（**正是 Windows 上會壞的形態** —— 只找系統路徑、沒有 PATH fallback）：

```sh
DEVFLOW_PY="${DEVFLOW_PYTHON:-/usr/bin/python3}"
```

結果：

```
CI 第 1 面（靜態禁寫死）  ✅ 綠 ← 抓不到（字面只在被排除的解析正本裡）
CI 第 2 面（fail-open）    ✅ 綠 ← 抓不到（顯式設了覆寫，沒碰 fallback）
CI 第 3 面（覆寫跑自測）   ✅ 綠 ← 抓不到（同上）
```

**整批 D 要修的東西被拿掉，CI 完全放行。**

### 修法：加第 4 面

**owner 已裁決：在現有 ubuntu job 加一面，不改成 `windows-latest`。**

要驗的是：**不設 `DEVFLOW_PYTHON`、且 `/usr/bin/python3` 不可用時，解析要退回 PATH 上的 python3**。

做法（細節自訂，語意要到）：

- 用臨時 `PATH` ／ 臨時目錄擋掉 `/usr/bin/python3`（例如把一個假的、不可執行的
  `python3` 放在前面，或用 `-x` 判定會失敗的路徑），**但保證 PATH 上仍有一個可用的 python3**
- **不要設 `DEVFLOW_PYTHON`**（設了就短路，等於沒驗）
- 跑一個會用到直譯器的 hook（例如 `hooks/devflow-prebash.sh`），
  確認它**成功走完**而不是印「找不到 python3」

⚠️ 這一面要跟第 2 面明確區分開：
第 2 面驗的是「**真的沒有任何 python3** → fail-open」，
第 4 面驗的是「**系統路徑沒有、但 PATH 上有** → 要退回 PATH 用起來」。
兩者混在一起就會像現在這樣互相掩護。

### E-2 驗收（**反證是這一項的重點**）

在本機用同樣手法跑一次，並做**兩個**破壞實驗：

| 破壞什麼 | 第 4 面必須 |
|---|---|
| 把解析改成 `DEVFLOW_PY="${DEVFLOW_PYTHON:-/usr/bin/python3}"`（拿掉 PATH fallback） | **紅** |
| 把解析改成 `DEVFLOW_PY="${DEVFLOW_PYTHON:-$(command -v python3)}"`（拿掉系統優先） | 綠或紅都可以，**但要在回報裡說明你的判斷** —— 這一種不是 Windows 缺陷，是優先序改變 |

第一個不紅 = 這一面沒用，重做。

⚠️ 兩個實驗都要**改完立刻還原**，收工前 `git status --short` 必須是空的。

---

## E-3〔低〕`check-file-map.sh` 的說明註解過期

**位置**：`scripts/check-file-map.sh:99` 附近（`EXPECTED_MAPPED_FILES = 78` 上方的註解）

註解還寫著「現值 77 = hooks 22 + observability 17 + scripts 36 + tests/parallel-stage6 2」，
但常數已經是 **78**，而且**那個加總本身在這一輪之前就已經是錯的**（hooks 實際是 25 不是 22）。

守衛比的是常數不是註解，所以照樣過 —— 但下一個做同樣記帳的人會照著錯的分解去算。

**修法**：把註解改成與現值一致，或者**乾脆不寫分解**、只說「數字以
`bash scripts/check-file-map.sh` 的 `scanned=` 輸出為準」。
⚠️ **常數 78 不准動**，這一項只改註解。

---

## 做完之後的驗收（全部都要跑，輸出貼進回報）

```bash
bash scripts/check-integration-regression-guard.sh    # 全過，項數比 36 多
bash scripts/test-architecture-guards.sh              # 全過（地板互釘同步）
bash scripts/check-file-map.sh                        # scanned=78 不變
bash scripts/devflow-check.sh all                     # REPO_REFERENCE_PASS 全過
bash hooks/selftest.sh                                # 378/378（本輪不該動到它）
env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
bash hooks/devflow-exec.sh doctor                     # COMPATIBLE
bash scripts/render-methodology-corrections.sh --check # 綠（本輪不動模板，不該紅）
```

另外確認：

- `git status --short` 為空（所有破壞實驗都還原了）
- **版號仍是 3.8.0**（兩處）
- `git diff --stat` 只含硬約束 2 列的那四個檔
- **整合回歸工具與其散發副本零 diff**（本輪不該動到它們）：
  `diff -q scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh`

## 收尾（有先後順序）

| # | 做什麼 | 在哪條 branch |
|---|---|---|
| 1 | 完成 E-1~E-3 ＋ 所有破壞實驗 | `fix/v380-counterproof`（**不准碰 `docs/dev/STATUS.md`**） |
| 2 | 切回 `main`，`git fetch origin` ＋ `git pull --ff-only origin main`；不通過就停 | `main` |
| 3 | `git merge --no-ff fix/v380-counterproof` | `main` |
| 4 | 用 `scripts/history-append.sh` 追加一筆，`--version` 帶 **`v3.8.0`** | `main` |
| 5 | **從最終的 `main` HEAD 重跑一次上面全套驗收** | `main` |
| 6 | **停下回報，請 owner 跑 `git push origin main`** | — |

**`docs/dev/STATUS.md` 的 Backlog 本輪不用改**（13 條維持不變）——
這一輪補的是上一輪的反證，不產生新的待辦。

---

## 不要做

- 不要改 `hooks/devflow-python-lib.sh` 的解析式（它現在是對的）
- 不要改 `scripts/devflow-integration-regression.sh` 的參數解析（九種排列實測全過）
- 不要 bump 版號、不要新增檔案、不要動 Stage 1–4 模板
- 不要改成 `windows-latest` job（owner 已裁決用 ubuntu 加一面）
- 不要為了讓某個檢查變綠而放寬它
- 破壞實驗**一定要還原**，收工前工作區必須乾淨

## 回報格式

1. E-1 / E-2 / E-3 各一段：改了哪些檔（`檔案:行號`）、實際跑了什麼、輸出原文。
2. 驗收那八道的輸出原文全貼。
3. **破壞實驗逐個列**：E-1 的三個 mutant（各自被哪些子案抓到）＋ 反證的反證、
   E-2 的兩個。每個寫「弄壞什麼 → 有沒有真的變紅」。
   **沒做破壞實驗的守衛一律當成沒做。**
4. E-1 的地板數字從幾改到幾，兩處（守衛自己＋靜態互釘）都貼證據。
5. E-2 你怎麼擋掉 `/usr/bin/python3` 而又保證 PATH 上有 python3 —— 貼實際做法。
6. 有沒有發現本檔沒提到的問題 —— 列出來問，**不要自己動手**。

**每一個結論都要對應到你自己實際跑過的指令與看到的輸出。**
沒跑過的就寫「未驗證」，不准用推論代替。
