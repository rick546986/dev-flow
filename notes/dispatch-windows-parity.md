# 派工單（第三輪）：讓 dev-flow 在 Windows 上跑得出全綠

> **狀態：四條根因都已改完，等 Windows 複驗。**
> §2.3a／§2.3b 修於 **v3.9.1**（issue #5，Windows 實測翻綠）；§2.4 修於 **v3.9.2**
> （issue #7，Windows 實測 start 通、恆許通、圍欄②擋得住）；§2.1／§2.2 修於
> **v3.10.0**（本輪，**Mac 上只驗到「注入假 cygpath 時分支確實被走到」與「顯式帶
> bash 後不崩」，真正的 71 案翻綠必須上 Windows 才算數 —— 在那之前不得宣稱已解**）。
> 剩下的是 §3 那句 README 措辭，要等 Windows 複驗全綠才寫得出不過期的說法。
>
> rick 2026-08-19 裁決 5(b)：另立派工單排到第三輪，**不併進當前這輪**
> ——當前這輪在收派工分層第一輪的尾（探針複核、契約註記、發版），混進平台移植會讓
> 「出事時分不出是誰造成的」。
>
> **本檔寫給沒有前情的 session 看。** 每條結論都附實際跑出來的輸出。標「實測」= 有人在
> Windows 機器上真的跑過並貼了原文；標「未驗證」= 還沒有證據，不得當事實用。
>
> 觸發句：`讀 <repo>/notes/dispatch-windows-parity.md 照它跑`

---

## 0. 為什麼這件事非做不可

**發版整條路斷在這裡。** `skills/dev-release/SKILL.md:40` 寫「驗證三道（全綠才准發版）」，
`:184` 又把「以『這條跟本次改動無關』放行」明列為禁止事項。所以在 Windows 機器上
**永遠發不出版**，而且 dev-flow 沒有發版就等於其他機器 `/plugin update` 拉不到東西、
也不會有任何提示（2026-08-19 接手單第 4 件記過同一件事）。

白話就是：這不只是「測試紅紅的很難看」，是**這台機器上做的任何改動都送不出去**。

---

## 1. 現況實測（2026-08-19，Windows 11 + Git Bash + Python 3.13.13）

| 跑什麼 | 這台的結果 | Mac 上的結果（接手單記的） |
|---|---|---|
| `bash hooks/selftest.sh` | 321/392，**失敗 71 項** | 392/392 |
| `bash scripts/devflow-check.sh all` | 四組全紅 | 四組全過 |
| `bash hooks/devflow-exec.sh doctor` | INCOMPATIBLE | COMPATIBLE |
| `env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh` | ✅ 全部一致（14/14） | 14/14 |
| `bash scripts/test-architecture-guards.sh` | ✅ 83/83 全過 | 83/83 |
| `bash scripts/check-model-tiering.sh` | ✅ 全過（good=3 bad=2） | 全過 |
| `bash scripts/check-file-map.sh` | ✅ PASS（83 支） | PASS |
| `bash scripts/check-hooks-accounting.sh` | ✅ 全過 | 全過 |
| `bash scripts/check-version-sync.sh` | ✅ 全過（5 處一致） | 全過 |
| `bash scripts/check-no-stale-paths.sh` | ✅ 全過（284 檔零命中） | 全過 |

### 1.1 這**不是**退步——已經用對照實驗排除

把 2026-08-19 動工前的版本（`5d09b71`）解到暫存目錄跑同一份自測：

```
=== dev-flow 守衛自測(378 案)===
❌ 守衛自測 314/378,失敗 64 項
```

逐條比對兩邊的失敗清單（`sed 's/(期望.*//'` 之後 `comm`）：

- **原本會過、現在失敗的：0 條**
- 多出來的 7 條全部是那一輪新增的案例（`s7` / `s7b` / `s7c` / `pst`）

所以：**平台不相容是長期存在的，不是哪一輪改壞的。**

### 1.2 範圍要講準：紅的是三項，不是全部

⚠️ 本檔早先的說法是「Windows 上跑不出全綠」，容易被讀成「什麼都跑不動」。實跑之後**七道收尾
清單裡只有三項紅**（`selftest.sh`、`devflow-check.sh all`、`doctor`），其餘四項照樣綠 ——
包含 `gate-consistency.sh` 14/14 與 `test-architecture-guards.sh` 83/83 這兩支跨檔靜態釘。

⚠️ 特別注意 `gate-consistency.sh`：它**只在 doctor 內部失敗**
（`bash: line 1: D:dev-flowhooksgate-consistency.sh: command not found`），
根因是 §2.3 那條 doctor 組路徑把反斜線吃掉，**不是這支腳本本身壞**。直接跑它是綠的。
修 §2.3 的人不要順手去改 `gate-consistency.sh`。

---

## 2. 根因（四條，逐條有實測輸出）

### 2.1 ✅ 兩個 `/tmp` 不是同一個資料夾（失敗數量最大的一條）——**已修於 v3.10.0**

> **採用的修法不是候選 (a)/(b)/(c) 任何一個的原樣，而是 (b) 的最小版**：底下所有
> `mktemp` 本來就已經吃 `${TMPDIR:-/tmp}`，所以只要在**入口**把 `TMPDIR` 正規化一次
> 就全涵蓋，不必動 29 個 `mktemp` 落點。正規化用 `cygpath -m`（產出 `C:/Users/...`，
> 正斜線 + 磁碟機代號，Git Bash 與 Windows 原生 Python 兩邊都認得，與 §2.3b 的
> `--print-root` 同一招）；沒有 `cygpath` 的環境不進那個分支，行為零變化。
> 落點：`hooks/selftest.sh` 與 `scripts/devflow-check.sh` 各一份**逐字副本**（兩支都是
> 可獨立執行的入口），由 `test-architecture-guards.sh` 的 `check_twin_block` 對帳釘住，
> 改一邊必紅（已負向驗過）。selftest 另加 w2 兩案：注入假 `cygpath` 證明分支真的會被
> 走到（不注入的話這條修法在 Mac/CI 上等於從沒被驗過），對照組用**空 PATH**而不是現行
> PATH —— Windows 上 `cygpath` 就在 `/usr/bin`，拿現行 PATH 當對照會在 Windows 假紅。

測試腳本用 Git Bash 的 `/tmp` 建樣本，回頭卻用 Windows 原生 Python 去讀同一個寫法。
兩邊解出來的位置不一樣：

```
$ cygpath -w /tmp
C:\Users\STORKU~1\AppData\Local\Temp        ← Git Bash 認的

$ python3 -c "import glob;print(glob.glob('/tmp/devflow-probe*'))"
[]                                          ← 原生 Python 看不到(它解成 C:\tmp)
$ ls -d /tmp/devflow-probe.fw8vnw
/tmp/devflow-probe.fw8vnw                   ← Git Bash 明明有
```

⚠️ **`C:\tmp` 這個資料夾在這台是存在的**（`os.path.exists('/tmp')` 回 `True`），
所以不會噴「找不到目錄」這種好認的錯，只會安靜地在空目錄裡找不到樣本 → 檢查判失敗。
這是為什麼失敗訊息看起來五花八門（`期望 0,得 1`、`期望 2,得 0`），根其實是同一個。

**被測的程式沒壞，已經手動驗過。** 把失敗的 `s7` 案例搬到暫存 repo 重現：

```
run_id=run_01M0CDWTJ47R0ECCDNHAF21GFF
{"schema": "exec-v4", "run_id": "run_01M0CDWTJ47R0ECCDNHAF21GFF", ...}
```

`schema` 與 `run_id` 都正確寫出來了。失敗純粹是驗的人找錯地方。

**候選修法**（未定案，執行者要自己評估）：
- (a) 測試腳本一律用 `mktemp -d` 之後過一次 `cygpath -w`（或 `-m`）再交給 Python。
- (b) 統一在 selftest 開頭把 `TMPDIR` 設成一個兩邊解讀一致的路徑。
- (c) 把交給 Python 的路徑一律走環境變數傳，不要內插進 Python 字串字面值。
  ⚠️ 現行寫法是 `open('$S7T/.devflow/exec.json')` 這種內插，路徑含反斜線時
  還會被 Python 當轉義字元吃掉，(c) 順便解掉這個。

### 2.2 ✅ Python 直接執行 `.sh`，Windows 不認 —— **已修於 v3.10.0**

> 全 repo 掃過同型寫法，實際有三處（不是一處）：
> `scripts/check-methodology-corrections.sh`（renderer）、`scripts/check-realworld.sh`
> （同一支 renderer）、`hooks/selftest.sh` 的 `c_plan()`（直接 exec `devflow-exec.sh`）。
> 三處都改成 `["bash", <script>, ...]`。`hooks/_doctor_impl.py` 那幾處在 v3.9.1 修
> §2.3a 時已經帶 bash，本輪不動。
> ⚠️ 順帶記一筆**沒有修**的東西：`check-methodology-corrections.sh` 用
> `os.access(renderer, os.X_OK)` 判可執行 —— Windows 的 Python 對這個旗標基本上
> 「檔案存在就回 True」，所以那條斷言在 Windows 上等於恆過。它不會崩、也不會假綠到
> 放行壞東西（後面緊接著真的去跑那支腳本），但它**不是**一道有效的檢查，別把它算進
> Windows 的覆蓋率。

`scripts/check-methodology-corrections.sh` 整支崩掉：

```
File "<stdin>", line 339, in <module>
  ...
OSError: [WinError 193] %1 不是有效的 Win32 應用程式。
```

原因：用 `subprocess.run([...".sh"...])` 直接 exec 一支 shell 腳本。Windows 沒有
shebang 機制，必須明確用 `["bash", "<script>"]` 起。

**候選修法**：那一處（及全 repo 同型寫法）改成顯式帶 `bash`。要順手掃一遍有沒有別處同型。

### 2.3 🔴 doctor 兩項紅——**兩個不同成因，兩套修法互不覆蓋**

```
✗ gauntlet-root: 散發副本解析根 D:\d\dev-flow\docs\dev ≠ 受測專案 docs/dev D:\dev-flow\docs\dev
✗ gate-consistency: exit 127(bash: line 1: D:dev-flowhooksgate-consistency.sh: command not found)
```

⚠️ **本節原本把這兩項寫成同一條「Windows 路徑塞進 shell 字串沒有轉義」，那是錯的**
（見 issue #5）。只有第二項是轉義問題；第一項既不是「少了東西」、也跟轉義無關——
整條路徑在傳遞過程中**沒有經過任何 shell**，而且是**多一層**不是少東西。
照舊版敘述只修轉義，`gauntlet-root` 會照樣紅；doctor 是 fail-closed 的總判定，
一項紅就整體 INCOMPATIBLE，§5 的驗收條件會直接落空。兩項要分開修。

⚠️ **這兩條在動工前的版本上一模一樣**（同樣跑 `5d09b71` 的解出副本，同樣兩項紅），
所以確定是舊帳不是新帳。

#### 2.3a 🔴 `gate-consistency`：Windows 路徑當成一整句命令交給 `bash -c`

`hooks/_doctor_impl.py` 把腳本路徑丟給 `subprocess.run(["bash", "-c", cmd])`。
`-c` 收到的是**一整句 shell 命令**，路徑裡的 `\` 於是被 shell 當轉義字元吃掉，
`D:\dev-flow\hooks\gate-consistency.sh` 變成 `D:dev-flowhooksgate-consistency.sh`
→ command not found（exit 127）。實測對照（同一條路徑）：

| 起法 | exit |
|---|---|
| `bash -c "<路徑>"` | 127 |
| `bash "<路徑>"` | 0 |
| `bash -c "'<路徑>'"` | 0 |

**修法**：cmd 是實際存在的檔案時直接當參數帶給 `bash`（`["bash", cmd]`），不走 `-c`。
不能無條件拿掉 `-c` —— `DEVFLOW_GATE_CMD` 允許放非檔案的命令（selftest 就用 `true`），
那些仍須走 `-c`。要順手掃一遍全 repo 有沒有別處同型。

#### 2.3b 🔴 `gauntlet-root`：POSIX 路徑被 Windows Python 當成磁碟機根目錄下的路徑

**與轉義完全無關**，逐條實測的成因：

1. 證據檢查工具用 `ROOT=$(cd "$(dirname "$0")/.." && pwd)` 算自己的根
   （`scripts/devflow-evidence-gauntlet.sh`），`--print-root` 直接 `echo "$ROOT"`。
   Git Bash 上 `pwd` 印的是 POSIX 形式：

   ```
   devflow-evidence-gauntlet.sh --print-root  →  /d/<專案根>/docs/dev
   history-append.sh            --print-root  →  D:/<專案根>          ← 這支是綠的
   ```

2. doctor 拿到字串後用 Windows 原生 Python 的 `os.path.realpath` 解
   （`hooks/_doctor_impl.py`）。Windows 的 Python 看到開頭的 `/` 會當成
   「現行磁碟機根目錄下的路徑」：

   ```
   realpath('/d/<專案根>/docs/dev')  =  D:\d\<專案根>\docs\dev    ← 多出一層 \d\
   realpath('D:/<專案根>/docs/dev')  =  D:\<專案根>\docs\dev      ← 期望值
   ```

3. 期望值那一側由 `os.path.realpath(os.path.join(root, "docs", "dev"))` 算，`root` 是
   Windows 形式 → 兩邊格式不同 → 判不等 → 紅。

`history-append.sh` 同型探針之所以綠，是因為它改用 `git rev-parse --show-toplevel`
取根，git 在 Git Bash 印出來本來就是 `D:/...` 這種 Windows 形式 —— **現成的正確範例
就在同一個 tools 目錄裡**。

**修法**：`--print-root` 輸出前正規化成 Windows 形式（有 `cygpath` 就 `cygpath -m "$ROOT"`，
非 Windows 環境沒有 cygpath 則原樣印出、行為零變化）。正規化放在腳本端而不是 doctor 端，
是因為 `/d/x` 到底是磁碟機路徑還是真的 POSIX 路徑，只有 cygpath 查得到實際 mount 表，
在 Python 端猜是憑臆測。**母版與 `docs/dev/tools/` 散發副本兩份都要改。**

⚠️ **分離性佐證**：把不含反斜線的路徑餵給 doctor（把 `DEVFLOW_GATE_CMD` 設成
plugin 內 `hooks/` 下那支腳本的 POSIX 形式路徑），2.3a 立刻變
`✓ gate-consistency: exit 0`，而 2.3b **紋風不動仍是紅的**。這就是兩者不同源最直接的
證據。另外 doctor 只認三個環境變數（`DEVFLOW_CONTRACT` / `DEVFLOW_RUNTIME_CAPS` /
`DEVFLOW_GATE_CMD`），2.3b 沒有任何覆寫開關可繞。

### 2.4 🔴 路徑分隔符不一致讓 scope 比對全面失準（原列 🟡「未驗證」，2026-08-20 實測後升級）

```
$ cat .devflow/exec.json
{ "scope": ["src\\a.py"], ... }
```

⚠️ **本節原本標「未驗證」並提示不要假設只是長相問題 —— 測了，確實不是**（見 issue #7）。
2026-08-20 在 `ivf_platform`（Windows 11 + Git Bash + Windows 原生 Python，plugin 3.9.1）
實測：**這條是硬失敗 —— Windows 上 Stage 6 開不了工，而且圍欄②靜默失效。**
本節原本寫「出自 `hooks/_exec_impl.py`」也不準確，根在 `devflow-lib.py`。

**現象**：工作樹只有一個髒檔，而且它就寫在該 slug 的 `Files` 裡，仍被拒啟：

```
$ git status --porcelain
 M controllers/backend/report_system.php

$ ... devflow-exec.sh start pgs-report-sync-btn
⛔ 拒絕啟動:工作樹已有 1 個 scope 外未提交改動(前 10):
  controllers/backend/report_system.php
start exit=1
```

**根因**：三支函式，兩種路徑形式，一個逐字比對（`hooks/devflow-lib.py`）——
`canonical_scope_path()` L63 的 `os.path.normpath()` 與 `rel_of()` L252 的
`os.path.relpath()` 在 Windows 都吐反斜線，而 git porcelain 一律吐正斜線，
`in_pool()` L244 是 `rel == s` 逐字相等。所以**餵進 `in_pool` 的 `rel` 從哪來，
決定它會不會命中**，三個比對點方向相反：

| 比對點 | `rel` 來源 | 形式 | 結果 |
|---|---|---|---|
| `_exec_impl.py:192` start 前置掃描 | git porcelain | 正斜線 | **False** → 拒絕啟動 |
| `_postbash_impl.py:136` shell 偵測網 | git porcelain | 正斜線 | **False** → shell 改 scope 內的檔被記成越界 |
| `_guard_impl.py:160` Edit/Write 守衛 | `rel_of()` | 反斜線 | True → 唯一配得起來的 |

**同一個根因的其他後果**（都是 `rel.split("/")` 對反斜線路徑切出長度 1 的 list，
靜默判 False，不報錯）：

- 🔴 **圍欄②（執行期禁讀上游 1/2/3）整條失效**。`_guard_impl.py:118` 判
  `is_contract_path(rel, UPSTREAM)` 得 False 之後，L122 直接 `sys.exit(0)` ——
  **Read 這條路沒有 catch-all**。Windows 上 implementer 讀得到 1/2/3。
  README §11 說圍欄②「對換人／fresh subagent 可機械強制」，那句在 Windows 不成立。
- 🟡 **契約防篡改判錯，但被 scope catch-all 遮住**。`_guard_impl.py:125` 判 False
  後仍會掉到 L163「scope 外寫入」把檔案擋下，只是理由與 obs 事件分類都錯。真正的洞
  只剩「契約檔被列進某個 T 的 `Files`」那一種情況 —— 此時 `in_pool` 回 True，
  而本該優先的跨 feature 保護沒觸發。
- 🟡 **未武裝軟擋永不觸發**。`_guard_impl.py:71-73` 的 `_is_exec_doc` 恆為 False。
  諷刺的是該段 L60 的註解寫著「契約防篡改/scope 一次都沒觸發，而每一份產出看起來都
  完整，沒有人在當下發現」—— 它描述的正是自己在 Windows 上的狀態。
- 🟡 **`is_ambient_path()` 失效**（`devflow-lib.py:47` 同款切法）。`.DS_Store`／`._*`／
  `Thumbs.db`／`__pycache__` 判定全落空（只有 `.pyc` 靠 `endswith` 湊巧還活著），
  所以 Windows 上工作樹有 `Thumbs.db` 就會被算進 scope 外髒檔而拒啟。

**修法**：路徑形式挑正斜線當唯一正本，`canonical_scope_path()` 與 `rel_of()`
兩處回傳前各補一次正規化，**必須同時改**（只改一邊會把失敗搬家）。`rel` 變正斜線後，
`is_contract_path`／`is_ambient_path`／未武裝軟擋／恆許前綴會一起修好；scope 那側
同步正規化，`in_pool` 才配得起來。

兩件配套不能漏：①**既有 `exec.json` 的遷移** —— 已落盤的 scope 還是反斜線，升級不會
自動改，要嘛讀取端也正規化，要嘛明文要求升級後 `stop` → `start` 重新武裝。
②**負向測試不需要 Windows** —— Mac/Linux 的 `normpath` 不吐反斜線，自然重現不了，但可
**手造**：寫一份 scope 帶反斜線的 `exec.json` 餵 guard 斷言行為，並對
`canonical_scope_path()`／`rel_of()` 直接餵反斜線輸入做單元級斷言，讓 selftest 與 CI
釘得住，不必等下次上 Windows 才發現又壞了。

---

## 3. 順帶要處理的一件文件事（rick 2026-08-19 點出，明確不准在當輪插隊）

`README.md` 環境需求那段（約 `:12-17`）現在寫：

> **Windows（Git Bash）沒有 `/usr/bin/python3`，要另外裝 Python 並確認 `python3` 在
> PATH 找得到，或設 `DEVFLOW_PYTHON` 指向直譯器**，守衛才會真的生效。

**rick 的判斷：這句承諾多了。** 照它做（裝好 Python）之後，守衛確實會跑，但**整套驗證
依然跑不出全綠**，讀者會以為「裝完就沒事了」。

⚠️ 2026-08-19 已經在同一段**下面**補了一段「已知限制：Windows 上跑不出全綠」
（那是 rick 裁決 5 的第 ② 項，屬當輪範圍）。**但上面引的那句本身沒有動** ——
rick 明講這句要留給本派工單處理，不要在當輪插隊改。

執行本派工單時要決定的是：等 §2 修完之後，這句話要怎麼改才既不承諾過頭、
又不會在修好之後變成過期的警告。

---

## 4. 建議執行順序

| 步 | 做什麼 | 為什麼排這裡 |
|---|---|---|
| **1** | ~~修 §2.2（Python 直接執行 `.sh`）~~ | ✅ v3.10.0。實際三處同型，不是一處 |
| **2** | ~~修 §2.1（兩個 `/tmp`）~~ | ✅ v3.10.0。**「用數字證明有效」這一步還沒做** —— Mac 上這條是 no-op，71 案翻綠要上 Windows 量 |
| **3** | ~~修 §2.3a（`bash -c` 轉義）與 §2.3b（`--print-root` 路徑形式）~~ | ✅ v3.9.1（issue #5，Windows 實測兩項各自從 ✗ 翻 ✓，也實證了兩條是獨立成因） |
| **4** | ~~修 §2.4（路徑分隔符）~~ | ✅ v3.9.2（issue #7）。Windows 實測 start 通、恆許前綴通、圍欄②擋得住 |
| **5** | 全綠之後回頭處理 §3 那句 README | **還沒做,也不該現在做** —— 要先知道 Windows 複驗完長什麼樣,才寫得出不過期的措辭。README §11 圍欄②那句的 Windows 例外也在這步一併收 |

⚠️ **這個順序可以插隊，執行時自己判斷**：§2.1／§2.2／§2.3 擋的是「驗證跑不跑得出全綠」，
**§2.4 擋的是「Windows 上的使用者根本開不了工」** —— 對真實採用專案而言它才是唯一的
blocker。而且 §2.4 的負向測試不需要 Windows（見該節配套②，手造反斜線輸入即可），
不依賴前三步。所以把 §2.4 提到第 1 步、或與前三步並行，都是合理的；排在第 4 是沿用
原派工單的編號，不是依賴關係。

---

## 5. 驗收條件

1. **在 Windows 機器上**跑完 `notes/dispatch-agent-dispatch-layer.md` §13 那份收尾清單，
   七道全綠。**不接受「這條跟 Windows 無關」式的放行** —— 那正是
   `skills/dev-release/SKILL.md:184` 明文禁止的事。
2. **Mac 上不能退步**：同一份清單在 Mac 上跑，結果不得比修改前差（案例數只能增不能減，
   失敗數必須是 0）。跨平台修法最常見的失敗形態就是「修好一邊、弄壞另一邊」。
3. ~~§2.4 那條要有明確結論：測出有實害 → …；測出沒有實害 → …~~
   **已於 2026-08-20 測出有實害（issue #7），本條改為**：§2.4 的修法要同時證明
   ①`in_pool` 三個比對點都對得上（不只修好 start，postbash 與 guard 也要）、
   ②圍欄②在反斜線輸入下確實會擋（那是目前靜默失效的一條）、
   ③既有帶反斜線的 `exec.json` 有明確去向（讀取端正規化，或明文要求重新武裝）。
4. 每一支被改動的檢查腳本都要配**破壞實驗**：把它守的東西改壞，確認真的會紅。
   沒有反證的保護等於沒有保護（`notes/dispatch-v380-counterproof.md`）。

## 6. 回報格式

```
## 修了什麼(逐條對 §2)
| 根因 | 改了哪些檔:行 | 破壞實驗 | 結果 |

## 兩個平台的數字對照
| 檢查 | Windows 修前 | Windows 修後 | Mac 修前 | Mac 修後 |

## §2.4 的三項證明(見 §5 條件 3)
三個比對點都對得上 / 圍欄②在反斜線輸入下會擋 / 既有 exec.json 的去向

## §3 那句 README 改成什麼
改動前後對照

## 沒做完的、或做不到的
（沒有就寫「無」。有的話寫明為什麼）
```

---

## 7. 不要做

- **不要把當前這輪的東西混進來**（探針複核、契約註記、發版）。
- **不要為了讓測試變綠而放寬被測的行為** —— 要修的是「驗的人找錯地方」，
  不是「把檢查改鬆」。改鬆檢查會讓 Mac 上原本抓得到的缺陷變成抓不到。
- **不要在 Windows 上發版**（§0）。修完全綠之後才談發版。
- ~~不要假設 §2.4 只是長相問題~~ —— **這條的教訓已經兌現了**：§2.4 原本被標「未驗證、
  可能只是長相問題」，2026-08-20 實測發現是硬失敗（issue #7），跟 §2.1、§2.3 同一個
  形態。留著這行當紀錄：**「看起來只是長相」在這個 repo 已經三次都是真失效**，
  下次再遇到同類猜測，預設當它會失效，先測再說。
