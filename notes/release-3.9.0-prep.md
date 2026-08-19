# v3.9.0 發版包（回 Mac 執行用）

> **為什麼是一份備料而不是直接發**：這輪在 Windows 機器上做，而 Windows 上跑不出全綠
> （根因與證據見 [`notes/dispatch-windows-parity.md`](dispatch-windows-parity.md)）。
> `skills/dev-release/SKILL.md:40` 要求「驗證三道全綠才准發版」，`:184` 又把
> 「以『這條跟本次改動無關』放行」明列為禁止事項 —— 所以**只能回 Mac 發**。
>
> 這份把 rick 2026-08-19 交代的三樣備好：發版說明草稿、版號要同步的兩處位置、
> 發版前驗證指令清單。另外附上他裁決要記的偏差。
>
> **用法**：回 Mac 之後打 `/dev-release minor`，發版器會照它自己的清單跑；
> 這份是給它（和你）對照用的填空答案，不取代它的清單。

---

## 0. 版號：兩處，一起改

| 檔案 | 欄位 | 現值 | 目標 |
|---|---|---|---|
| `.claude-plugin/plugin.json` | `version` | `3.8.0` | **`3.9.0`** |
| `hooks/runtime-capabilities.json` | `runtime_version` | `3.8.0` | **`3.9.0`** |

**級別是 minor**：新增了兩支具名 subagent、一支 hook、幾支檢查腳本；既有專案
`dev-setup upgrade` 後仍相容，契約版本沒動。

⚠️ **不要動** `supported_contract_versions` 與 `schema_versions`（`SKILL.md` 步驟 3 的
禁止事項）—— 那兩個跟著契約版本走，不隨發版遞增。本輪加的 `exec_state_note` 是
契約檔**最外層**的註記，不是 `schema_versions` 裡的鍵，所以契約版本維持 `2.0.0`。

改完自己對一次：

```bash
jq -r .version .claude-plugin/plugin.json
grep -o '"runtime_version": "[^"]*"' hooks/runtime-capabilities.json
# 兩者必須是同一個字串
```

---

## 1. 發版前驗證指令清單

### 1.1 擋門三項（任一不過就停）

```bash
cd ~/dev/dev-flow
git branch --show-current    # 必須是 main
git status --short           # 必須為空
git fetch origin && git rev-list --left-right --count HEAD...origin/main
```

⚠️ 最後那行**現在會顯示領先**（這輪的合併都還沒 push；筆數會隨收尾增加，別對數字）。
SKILL.md 說「必須 0 0 或只領先」，領先是允許的。

### 1.2 驗證三道（全綠才准發版）

```bash
bash hooks/selftest.sh
# 期望:✅ 守衛自測 N/N 全過(N 以腳本輸出為準,不寫死)

env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
# 期望:✅ 全部一致(14/14)、exit 0
# 三個環境變數必須真的 unset —— 這道同時驗 __file__ fallback 沒壞

bash hooks/devflow-exec.sh doctor
# 期望:✅ devflow doctor: COMPATIBLE
```

⚠️ **Mac 上要先裝 render 相依**，否則 `devflow-check` 的 render 那組會崩在
`ModuleNotFoundError: No module named 'markdown_it'`：

```bash
pip install -r scripts/requirements-methodology-render.txt   # 釘死 markdown-it-py==4.0.0
```

### 1.3 散發副本同步（步驟 2）

```bash
diff -q devflow-contract.json docs/dev/devflow-contract.json
bash scripts/check-integration-regression-guard.sh
```

**這輪特別要看第一行**：本輪動過 `devflow-contract.json`（加 `exec_state_note`），
兩份都改了、內容逐字相同（在 Windows 上已用 `json.load` 比對過相等）。
第一行必須靜默無輸出。

### 1.4 這台（Windows）已經跑過、綠的部分

回 Mac 之後這幾支應該照樣綠；不綠就是 Mac 上出了新問題，不是這輪的帳。
**驗證三道裡的 `gate-consistency` 這台已經直接跑過且是綠的** —— 它在 doctor 內部顯示失敗是
doctor 組路徑的問題，不是它本身壞（見 `notes/dispatch-windows-parity.md` §1.2）。
所以三道裡只剩 `selftest.sh` 與 `doctor` 要靠 Mac 才驗得到：

| 檢查 | Windows 結果 |
|---|---|
| `env -u ... bash hooks/gate-consistency.sh`（驗證三道的第二道） | ✅ 全部一致（14/14） |
| `bash scripts/test-architecture-guards.sh` | ✅ 83/83 全過（含對契約檔做 mutation 的兩條） |
| `bash scripts/check-model-tiering.sh` | ✅ 全過（good=3 bad=2） |
| `bash scripts/check-file-map.sh` | ✅ PASS，83 支必列檔 + 88 個 token 全命中 |
| `bash scripts/check-hooks-accounting.sh` | ✅ 全過 |
| `bash scripts/check-version-sync.sh` | ✅ 全過（5 處一致，升版後要重跑） |
| `bash scripts/check-no-stale-paths.sh` | ✅ 全過（284 檔零命中） |

⚠️ `check-version-sync.sh` **升版之後要再跑一次** —— 它比的就是版號的多處一致。

**本輪的 README 改動不會影響 renderer 的定點檢查**（已查 `scripts/render-methodology-corrections.sh`）：
它只讀 README 的四個特定區域（Stage 6 seam 的 fenced 區塊 `:97`、`## 3.` 表 `:125`、
「審查者產生」bullet `:143/:146`、「G1/G2/G3 審查與 verdict」bullet `:148`）。
本輪改的是頂部環境需求那個引用區塊，四個區域都不碰，所以不需要重生衍生檔。

---

## 2. HISTORY.md：要記的偏差（rick 裁決：記偏差，不假造）

rick 2026-08-19 第 3 題裁決 **(a)**：發一版 `3.9.0`，不補兩個標籤。理由是 (b) 做不乾淨
—— `c9411c2` 的 `plugin.json` 寫的是 `3.8.0`，標籤叫 `3.9.0` 會名實不符，而發版器
存在的理由正是比對那個字串。

**代價要寫進 HISTORY，不能當沒發生**：需求正本 §10 裁決 10 要的是「拆兩版」
（守衛開始在 sequential 生效那批單獨一版、審查者那批再一版），目的是「出事時分得出
是哪一批造成的」。兩批已經在同一個窗口進了 `main`，**那個隔離已經失去**。

追加指令（`--slug` 用問題編號，這輪不是單一 feature）：

```bash
scripts/history-append.sh --slug dispatch-agent-dispatch-layer --version v3.9.0 \
  --what "派工分層第一輪落地 + 探針結案:①sequential 三條武裝路徑補 exec-v4 schema 與 run_id(守衛原本在最常用的那條路整支失效)②新增 agents/devflow-reviewer.md 與 devflow-adviser.md 兩支唯讀具名 subagent(tools: Read,不給 Bash/Edit/Write)③check-model-tiering.sh 補 worker-tasks == 0 → exit 2 地板④白話回覆 hook(預設關,DEVFLOW_PLAINSPEAK=1 才開)⑤四張自判表加「依據」欄⑥兩個平台探針重跑 + 第二人獨立複核結案(型別欄位名 subagent_type、plugin 型別帶 dev-flow: 命名空間、tools: Read 在名稱解析層就把工具拿掉)⑦契約檔最外層加 exec_state_note 記 exec-v3/exec-v4 雙軌並存⑧README 補 render 相依與 Windows 已知限制" \
  --why "守衛只在四條武裝路徑的其中一條生效,sequential(預設、最常用)全程不設防,不修的話派工分層做什麼都是 no-op;agents/*.md 原本把型別字串標成「實測確認」但沒有第二人複核,其中 dev-flow:devflow-adviser 一次都沒被叫過" \
  --where "hooks/_exec_impl.py、hooks/_dispatch_impl.py、hooks/_doctor_impl.py、hooks/selftest.sh、agents/(新增兩支)、hooks/devflow-plainspeak.sh、hooks/plainspeak-rules.md、scripts/check-model-tiering.sh、scripts/check-{file-map,hooks-accounting}.sh、devflow-contract.json 與 docs/dev/devflow-contract.json、README.md、docs/PLUGIN.md、guides/guide-dev-flow.html、scripts/fixtures/dispatch-guard/、notes/" \
  --detail "notes/dispatch-agent-dispatch-layer.md"
```

追加完之後**再手動補一段偏差說明**進同一筆的「做了什麼」不行（那要重寫檔案，
`history-guard` 會擋）。改法：**偏差寫成獨立的第二筆**：

```bash
scripts/history-append.sh --slug release-v390 --version v3.9.0 \
  --what "記一筆偏差:需求正本 §10 裁決 10 要求「拆兩版」(§7 守衛在 sequential 生效那批單獨一版、§4 A′ 兩支審查者那批再一版),實際沒有達成 —— 兩批在同一個窗口進了 main(§7 是 812a9fb+c9411c2,A′ 是 a44b92e+f3d9e4a),3.9.0 一版全包" \
  --why "裁決 10 要的隔離目的是「出事時分得出是哪一批造成的」,現在分不出來了。補兩個標籤的路(3.9.0 指 c9411c2、3.10.0 指 f3d9e4a)被 owner 2026-08-19 否決:c9411c2 的 plugin.json 寫的是 3.8.0,標籤叫 3.9.0 名實不符,而發版器存在的理由正是比對那個字串 —— 補得不乾淨不如記偏差" \
  --where ".claude-plugin/plugin.json、hooks/runtime-capabilities.json(版號兩處)"
```

⚠️ **`--slug` 兩筆刻意不同**：第一筆記做了什麼（軌名），第二筆記發版本身與偏差
（照既有的 `release-v380` 那筆同一套命名）。

### STATUS.md

**這輪不用動**：`docs/dev/STATUS.md` 的 Active 表現在是「目前無進行中的改版軌」，
Backlog 也沒有本輪做掉的項。發版器步驟 4 那半自動跳過。

---

## 3. 發版說明草稿（`gh release create` 的 `--notes`）

標題：`v3.9.0 — 派工分層守衛在 sequential 生效 + 兩支唯讀具名審查者`

```markdown
## 改了什麼（使用者角度）

**1. 執行守衛原本在最常用的那條路上整支失效，現在補上了。**
`devflow-exec.sh start` 有四條啟動路徑，但只有平行執行那條會在紀錄檔裡寫下格式代號。
另外三條（一般的 sequential 啟動、feature 範圍啟動、Stage 7 事後補審）都沒寫，
而派工分層守衛靠那個代號判斷「現在是不是在執行中」——**沒有代號就一律放行**。
也就是說：預設、最常用的那條路，全程沒有保護。這一版讓那三條也寫代號（`exec-v4`）
與這次執行的流水號，守衛才真的會動。

**2. 新增兩支唯讀的具名審查者。**
`dev-flow:devflow-reviewer`（收驗判 PASS/FAIL）與 `dev-flow:devflow-adviser`
（連敗時診斷是規格問題還是執行問題）。兩支的工具只有讀檔一種，**拿不到跑指令、
改檔案、搜尋的工具**——防的是「派工者一時手滑讓執行者審自己的改動」這類紀律漂移，
**不防蓄意偽造**（這句不要在任何地方被改寫成更強的說法）。

**3. 派工紀錄多了一道地板。**
事後稽核原本在「一筆執行者紀錄都沒有」的情況下會回報全過（沒有資料 = 零違規）。
現在這種情況直接判失敗。

**4. 回覆講人話的提醒（預設關）。**
要開就在 `settings.json` 的 `env` 區塊設 `DEVFLOW_PLAINSPEAK=1`。

**5. 文件的證據強度改成誠實的。**
兩支審查者的說明原本把型別字串標成「實測確認」，其中一支其實一次都沒被叫過。
這一版重跑探針、加上第二個人獨立複核，把每句話改成它真正撐得住的強度，
並寫明哪一半仍然沒測（正式安裝那條路）。

**6. 契約檔補記兩種格式並存。**
`exec_state` 只放得下一個值，但實際上有 `exec-v3`（平行）與 `exec-v4`（其餘三條）
兩種。這一版在最外層加註記寫明哪條路寫哪個，結構不動。

## 要不要動手

- **要重裝**：`/plugin marketplace update dev-flow` → `/plugin update dev-flow` →
  `/reload-plugins`（或開新 session）。設了 `autoUpdate: true` 的機器開新 session 就會拿到。
- **採用專案要重跑 `dev-setup`**：它會偵測到模板過期並提議升級。契約版本沒變，
  升級後相容，不需要人工介入。
- **不需要額外裝套件**：hook 只用 Python 標準函式庫。`markdown-it-py` 只有維護
  dev-flow 本身才要（見 README 環境需求）。

## 已知限制

**Windows 上跑不出全綠**，所以 Windows 機器發不了版。根因是 Git Bash 的 `/tmp` 與
Windows 原生 Python 的 `/tmp` 是兩個不同資料夾，測試腳本寫樣本與驗樣本指到不同地方。
被測的程式沒問題（已手動驗過），是驗的人找錯地方。四條根因與修法排程見
`notes/dispatch-windows-parity.md`，排在第三輪。

## 驗證

（發版時把步驟 1 三道的實際輸出摘要貼在這裡，不要沿用本草稿。）

## 偏差記錄

需求正本裁決要求把這一版拆成兩版發（守衛修復一版、審查者一版），實際沒有達成：
兩批在同一個窗口進了主線，一版全包。代價是出事時分不出是哪一批造成的。
理由與否決補標籤的原因記在 `docs/dev/HISTORY.md` 的 `release-v390` 那筆。
```

---

## 4. 剩下的收尾（發版之後才做得了）

**接手單第 2 件的後半還沒封閉**：透過真正的安裝流程
（`claude plugin marketplace add` 加 `install`）之後，在一個全新 session 裡叫
`dev-flow:devflow-reviewer` 與 `dev-flow:devflow-adviser`，確認在**正式安裝**這條路
上也叫得出來。目前兩次獨立實測都走 `--plugin-dir`（當場臨時載入），跳過了安裝那一層。

重跑用的探針腳本不在 repo 裡（在這次 session 的暫存目錄），做法記在
`notes/dispatch-agent-dispatch-layer.md` §7.1.1 —— 要重建很快：丟棄用專案掛一支
PreToolUse 攔截程式把原始輸入落地，然後派 Task 給那兩個型別。
⚠️ 攔截程式要用 Python 寫，不要用 `.sh`（Windows 上 Python 直接執行 `.sh` 會噴
`WinError 193`，探針會壞掉卻看起來像「平台沒送出事件」）。

驗完把結果補進 §7.1.5，把「仍然沒測的那一半」那節改掉。
