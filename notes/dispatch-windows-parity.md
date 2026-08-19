# 派工單（第三輪）：讓 dev-flow 在 Windows 上跑得出全綠

> **狀態：待執行。** rick 2026-08-19 裁決 5(b)：另立派工單排到第三輪，**不併進當前這輪**
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

---

## 2. 根因（四條，逐條有實測輸出）

### 2.1 🔴 兩個 `/tmp` 不是同一個資料夾（失敗數量最大的一條）

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

### 2.2 🔴 Python 直接執行 `.sh`，Windows 不認

`scripts/check-methodology-corrections.sh` 整支崩掉：

```
File "<stdin>", line 339, in <module>
  ...
OSError: [WinError 193] %1 不是有效的 Win32 應用程式。
```

原因：用 `subprocess.run([...".sh"...])` 直接 exec 一支 shell 腳本。Windows 沒有
shebang 機制，必須明確用 `["bash", "<script>"]` 起。

**候選修法**：那一處（及全 repo 同型寫法）改成顯式帶 `bash`。要順手掃一遍有沒有別處同型。

### 2.3 🔴 doctor 組路徑時反斜線被當轉義字元吃掉

```
✗ gauntlet-root: 散發副本解析根 D:\d\dev-flow\docs\dev ≠ 受測專案 docs/dev D:\dev-flow\docs\dev
✗ gate-consistency: exit 127(bash: line 1: D:dev-flowhooksgate-consistency.sh: command not found)
```

第一行的 `D:\d\dev-flow` 少了東西、第二行的 `D:dev-flowhooksgate-consistency.sh`
整條反斜線消失 —— 典型的「Windows 路徑塞進 shell 字串沒有轉義」。

⚠️ **這兩條在動工前的版本上一模一樣**（同樣跑 `5d09b71` 的解出副本，同樣兩項紅），
所以確定是舊帳不是新帳。

### 2.4 🟡 程式寫出的檔案清單帶反斜線（真的是程式行為，不只測試）

```
$ cat .devflow/exec.json
{ "scope": ["src\\a.py"], ... }
```

出自 `hooks/_exec_impl.py`。**這一條跟前三條不同**：前三條只影響「在 Windows 上驗不驗得過」，
這條是**程式真的寫出跨平台不一致的內容**。

⚠️ **未驗證**：這會不會讓 Windows 上的採用專案實際踩到問題（例如守衛比對範圍時
`src\a.py` 對不上 `src/a.py` 而誤放行或誤擋），**本輪沒有測**。執行這份派工單時要補測，
不要直接假設「只是長相不同」。

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
| **1** | 修 §2.2（Python 直接執行 `.sh`）| 最小、最獨立，一處寫法問題，修完 `devflow-check.sh` 的 methodology 那組就會動 |
| **2** | 修 §2.1（兩個 `/tmp`）| 失敗數量最大的一條。修完再量一次 `selftest.sh`，用數字證明有效 |
| **3** | 修 §2.3（doctor 組路徑）| 前兩步修完才看得清 doctor 還剩什麼紅 |
| **4** | 補測 §2.4（反斜線 scope 有沒有實害）| **先測再決定要不要改** —— 沒有實害就只加註解，有實害才動程式 |
| **5** | 全綠之後回頭處理 §3 那句 README | 要先知道修完長什麼樣，才寫得出不過期的措辭 |

---

## 5. 驗收條件

1. **在 Windows 機器上**跑完 `notes/dispatch-agent-dispatch-layer.md` §13 那份收尾清單，
   七道全綠。**不接受「這條跟 Windows 無關」式的放行** —— 那正是
   `skills/dev-release/SKILL.md:184` 明文禁止的事。
2. **Mac 上不能退步**：同一份清單在 Mac 上跑，結果不得比修改前差（案例數只能增不能減，
   失敗數必須是 0）。跨平台修法最常見的失敗形態就是「修好一邊、弄壞另一邊」。
3. §2.4 那條要有**明確結論**：測出有實害 → 附修法與破壞實驗；測出沒有實害 → 附
   「怎麼測的、看了什麼」的原始輸出，並在 `_exec_impl.py` 留一行註解說明為什麼容許。
4. 每一支被改動的檢查腳本都要配**破壞實驗**：把它守的東西改壞，確認真的會紅。
   沒有反證的保護等於沒有保護（`notes/dispatch-v380-counterproof.md`）。

## 6. 回報格式

```
## 修了什麼(逐條對 §2)
| 根因 | 改了哪些檔:行 | 破壞實驗 | 結果 |

## 兩個平台的數字對照
| 檢查 | Windows 修前 | Windows 修後 | Mac 修前 | Mac 修後 |

## §2.4 的結論
有實害/沒實害 + 原始輸出

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
- **不要假設 §2.4 只是長相問題**（§2.1、§2.3 都是「看起來只是長相」但實際讓檢查
  整支失效的例子）。
