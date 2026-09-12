# diagram-ir-gate Stage 7 — reviewer-1 三包對照

> **不是 G3 PASS。不 merge #252／#253／#254。**
> 本檔是獨立 reviewer-1 對三份 Stage 7 審查包的比較，不是第四份 `7-review.md`。
> gate-of-record 仍只能是 feature 目錄那一份 `7-review.md` + twin。

日期：2026-09-12
審查者：reviewer-1（fresh-context Cloud Agent；`bc-7f09591f`；≠ #250 implementer-C；≠ 三包作者）

| 包 | PR | branch | head | 作者自稱 |
|---|---|---|---|---|
| impl-A | [#252](https://github.com/rick546986/dev-flow/pull/252) | `cursor/diagram-ir-gate-stage7-impl-a-ed7d` | `439b24c` | implementer-A-stage7 |
| impl-B | [#253](https://github.com/rick546986/dev-flow/pull/253) | `cursor/diagram-ir-gate-s7-impl-b-fa44` | `70f0cdd` | implementer-B-stage7 |
| impl-C | [#254](https://github.com/rick546986/dev-flow/pull/254) | `cursor/diagram-ir-gate-stage7-impl-c-b8b6` | `c539d08` | implementer-C-stage7 |

Ground：tip `4-spec` + `5-tasks` + Stage 6 [#250](https://github.com/rick546986/dev-flow/pull/250) 產品樹 `3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`。
現況 `origin/main` = `7dc3645`（#251 STATUS → 7-review；產品碼仍是 `3b22f01`）。

讀取順序（可查）：①`4-spec.md`（21 S）②`5-tasks.md`（T-1..T-6）③`git show 3b22f01` ④`scripts/test-diagir.sh` + 四牙 ⑤本 hop 親跑 Verify／現象 → **之後才** ⑥讀 6-notes Self-Review 與三包主張。

---

## Verdict

**Winner：#254 impl-C。**

三包都守住 `verdict: PRE-REVIEW`，沒有假 G3 PASS。產品碼已在 tip，本 hop 都是 docs-only。

C 是唯一同時滿足這四條的包：

1. Coverage Matrix **21/21 都有 `檔:行`**（B 幾乎沒有）
2. Known Limits **老實寫 docs SHA 會漂**，而且把 twin 罐頭 payload、S-4.2 牙偏弱、Stage 6 self-check 四眼缺口寫進去
3. Fresh Source SHA 綁產品樹 `3b22f01`，且明講本 docs commit 落地後 HEAD ≠ 該 SHA
4. 現象／Verify 數字經本 hop **獨立重跑對得上**（不是只抄 6-notes）

A 獨立性較乾淨（不同字母），矩陣也有 `檔:行`，但 findings 全 🟢、Known Limits 較薄。
B 唯一把雙份路由表打成 🟡，2c 寫得最完整，但矩陣幾乎只有 CASE 名 —— 對「抽驗一列看 `檔:行`」這條不合格。

Human G3 仍空白。全勾不算 PASS。本檔不代填。

---

## 本 hop 獨立 Verify（產品樹 `3b22f01`）

2026-09-12；工作樹 `/tmp/diagir-250` @ `3b22f01`。Fresh 前補裝 `markdown-it-py==4.0.0`（ENV，不計 IMPL）。

| Layer | Result |
|---|---|
| `bash scripts/test-diagir.sh` | 25/25；CASE validate 6 / deliver 2 / wire 4 / route 5（checks 6）/ lab 5 / static-scope 2 |
| `check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md` | 6/6；21 S |
| `check-vbox-fig.sh` | 16/16 |
| `check-dir-tree.sh` | 81/81 |
| `check-gate-twin.sh` | 222 |
| `check-file-map.sh` | scanned=205 |

三包宣稱的這組數字與本 hop 輸出相符。Gauntlet 65／91／67 的差來自 Evidence 表列數，不是假綠。

### 抽驗（第 5 步；對不上就整份退）

| 抽 | 檔:行 | 本 hop 實跑 | 三包是否對得上 |
|---|---|---|---|
| S-1.1 | `scripts/diagir.py:139-140`；`scripts/test-diagir.sh:144-149`；`scripts/fixtures/diagir/parked.json` | rc=1；`code=DIAGIR_KIND`；`target_replaced=false`；sha 仍 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc`；stderr 兩行 FAIL KIND＋ABORT | A／C 列了這些行。B 只有 CASE 名 |
| S-3.3 | `scripts/test-diagir.sh:310-315`；`scripts/fixtures/diagir/dir-as-vbox.json:4-8`；閘 `scripts/diagir.py:183-185`（`looks_like_tree` → `tree-as-vbox`） | rc=1；`code=DIAGIR_FAMILY`；detail=`tree-as-vbox`；sha 不變 | C 指定這列當決定論抽樣，對得上。A 有測試行。B 只有 CASE 名 |
| S-2.1 | `scripts/test-diagir.sh:190-210` | rc=0；len=1158；sha `053bc4df18d902ce9057ce91eb5e31bfe6d78d66128af29f83bbe5f76fc5a321`；四禁詞 0 | 三包數字相同 |
| S-4.5 | `scripts/devflow-check.sh:132` vbox-fig、`:135` dir-tree、`:236` gate-twin；`:137` 只掛 `test-diagir` | 無 `scripts/check-diagir-lab.sh` | **A／B 行號對。C 寫「:132 仍跑三支牙」是錯的**（:132 只有 vbox-fig） |

---

## 自建 Coverage Matrix（21/21；未先讀 Self-Review）

| S-id | 測試（本 hop） | 狀態 |
|---|---|---|
| S-1.1 | `scripts/test-diagir.sh:144-149`；閘 `scripts/diagir.py:139-140`；`scripts/fixtures/diagir/parked.json` | ✅ |
| S-1.2 | `scripts/test-diagir.sh:150-155`；閘 `scripts/diagir.py:141-142`；`empty-title.json` | ✅ |
| S-1.3 | `scripts/test-diagir.sh:156-161`；閘 `scripts/diagir.py:143-147`；`four-lines.json` | ✅ |
| S-1.4 | `scripts/test-diagir.sh:162-167`；閘 `scripts/diagir.py:183-185`；`tree-as-vbox.json` | ✅ |
| S-1.5 | `scripts/test-diagir.sh:168-173`；閘 `scripts/diagir.py:168-171`；`dir-short-why.json` | ✅ |
| S-1.6 | `scripts/test-diagir.sh:174-187`；收據 `scripts/diagir.py:74-88` | ✅ |
| S-2.1 | `scripts/test-diagir.sh:190-210`；`deliver` `scripts/diagir.py:232-258` | ✅ |
| S-2.2 | `scripts/test-diagir.sh:211-226`；原語 `scripts/devflow_atomic.py:13-22` | ✅ |
| S-2.3 | `scripts/test-diagir.sh:229-276`；`build-dir-tree.py:576-578`；`build-gate-twin.py:2351-2356`；`build-stage1-html.py:483-489`；`build-stage2-html.py:556`；`build-stage4-html.py:759` | ✅ |
| S-3.1 | `scripts/test-diagir.sh:279-303`；`notes/design/diagir-route.md:7-12` | ✅ |
| S-3.2 | `scripts/test-diagir.sh:304-309`；閘 `scripts/diagir.py:186-187` | ✅ |
| S-3.3 | `scripts/test-diagir.sh:310-315`；`dir-as-vbox.json:4-8`；閘 `scripts/diagir.py:183-185` | ✅ |
| S-3.4 | `scripts/test-diagir.sh:316-328`；閘 `scripts/diagir.py:156-157` | ✅ |
| S-3.5 | `scripts/test-diagir.sh:329-373`；`route` `scripts/diagir.py:277-283` | ✅ |
| S-4.1 | `scripts/test-diagir.sh:376-401`；`scripts/fixtures/diagir-lab.yaml:1-30` | ✅ |
| S-4.2 | `scripts/test-diagir.sh:402-433`（產器 fixture，**不**直接呼叫三支 `check-*.sh`）＋本 hop Fresh 16/16、81/81、222 | ✅ |
| S-4.3 | `scripts/test-diagir.sh:434-451`；`kind-parked.json` | ✅ |
| S-4.4 | `scripts/test-diagir.sh:452-458`；負向 path ≠ `lifecycle.json` | ✅ |
| S-4.5 | `scripts/test-diagir.sh:459-478`；`devflow-check.sh:132,135,236` 三牙、`:137` 只掛 test-diagir | ✅ |
| S-5.1 | `scripts/test-diagir.sh:481-491` | ✅ |
| S-5.2 | `scripts/test-diagir.sh:493-522`；plugin `3.23.3`；三點 `origin/main...HEAD` | ✅ |
| 既有測試套件(回歸) | 上列四牙 + `test-diagir.sh` 25/25 | ✅ |

---

## 五條評分（使用者指定）

| 條 | A #252 | B #253 | C #254 |
|---|---|---|---|
| 老實 PRE-REVIEW、無假 G3 PASS | 過。標題寫「不是 G3 PASS」。owner 欄卻寫 `rick`（看起來像 owner 自審） | 過。owner=`implementer-B-stage7`。PR 不是 draft | 過。owner=`implementer-C-stage7`。同字母 impl-C 自己寫進 Known Limits ⑪ |
| Coverage 21/21 + `檔:行` | 過。每列有測試行＋多數有閘行 | **不合格**。21 列幾乎只有 CASE 名；有行號的大約 S-3.1、S-4.5 | 過。密度最高（測試＋閘＋信封行） |
| Fresh Source SHA | 綁 `3b22f01`；Known Limit ② 寫 docs commit 會漂 | 同左；並給可重跑的 SHA 對帳指令 | 同左；明寫「不追本 docs commit」 |
| 真 Verify | 數字對。2c 用 6-notes FORK → `ALREADY_SYNCED` 再重綁（模板原文） | 數字對。2c 同時寫本 hop `N_A_NO_INCOMING` 與 S6 `ALREADY_SYNCED`（最完整）。初跑 gate-twin 缺 markdown-it-py 有記 ENV | 數字對。2c 本 hop `N_A_NO_INCOMING`；A1 說明 S6 FORK 會 `ALREADY_SYNCED`。另重跑 stage1/2/4 契約牙 |
| Known Limits 老實（尤其 SHA 漂） | 有 ②。7 條。漏雙份路由、twin 罐頭、S-4.2 牙偏弱 | 有 ②。有 F-2 🟡 雙份路由。漏 twin 罐頭 | 有 ②。11 條。有 twin 罐頭、S-4.2、self-check。**S-4.5 :132 三支牙寫錯** |

---

## 2c / SHA 現況（reviewer-1 補一刀）

三包 fork parent 都是 `3b22f01`（#250），**不含**後來的 #251 STATUS。

Fresh 當時若 `origin/main == 3b22f01`，B／C 的 `N_A_NO_INCOMING` 與 A 的 `ALREADY_SYNCED`（用 S6 FORK `2599787`）都可以成立。

**現在**再跑：`origin/main = 7dc3645`（#251 只改 `STATUS.md`）。從這三支 branch 重跑 2c 會變成 `SYNC_REQUIRED_NO_OVERLAP`（共同戰場不是產品碼）。這不是三包造假，是時間差。Human 若要把 winner 收成 tip 上的 gate-of-record，先 rebase／合併 #251（STATUS-only）再重綁 Fresh，不要把 `3b22f01` 說成當下 HEAD。

---

## 作者對照（N4；後讀）

6-notes：`FORK_INTEGRATION_SHA=2599787`；T-1..T-6 皆「implementer-C self-check」；D-1..D-4 皆 L1（三點 diff／「取代」漢字／filemap 205／heredoc 221）。

三包都裁成「數字相符、T PASS 不當 G3、Deviation 是 L1」。本 hop 同意。沒有漏報 S、沒有 L2 silent drift。

B 多看到的 F-2 🟡（`diagir.py:30-66` `ROUTE` vs `notes/design/diagir-route.md:7-12`）是真的：契約 Data owner 是 md，Python 另有一份。目前字面對得上，會漂。C／A 都看到兩份存在，但打成 🟢／沒立 F。

C 多看到的 twin 罐頭 payload（`build-gate-twin.py:2343-2356`）也是真的：閘驗的是兩步 `behavior-flow`，不是頁 HTML。S-2.3 要的是寫檔路徑經閘，不是內容閘。park 即可，不升 Boundary 🟡。

---

## Must-fix（winner #254 收成 tip 之前）

產品碼 **沒有** merge-blocking 缺陷。要修的是審查包本身：

1. **S-4.5 `檔:行` 寫錯（必修）**  
   把「`devflow-check.sh:132` 仍跑三支牙」改成 `:132` vbox-fig、`:135` dir-tree、`:236` gate-twin。`:137` 只掛 `test-diagir` 那句留著。抽驗對不上就整份退 —— 這一列現在對不上。

2. **吸收 B 的 F-2 🟡（必修，誠實）**  
   雙份路由表（md owner + `diagir.ROUTE`）寫進 Standards，park 到 Known Limits。不要繼續全 🟢。這不是新 R/S。

非阻擋（Should）：

- owner 欄不要讓人以為是 #250 同一實作者在自審 G3。C 已在限制聲明寫了；Human 路徑仍要 ≠ implementer-C。
- rebase #251 後重綁 Source SHA 註記（產品 SHA 仍可寫 `3b22f01`，但不要再寫「= 當下 HEAD」除非真的是）。

#252／#253 **不要**當 gate-of-record。B 若要再比一次，先把 21 列補上 `檔:行`。

---

## 不要做的事

- 不要把任何一包的 `verdict` 改成 PASS。
- 不要 merge #252／#253／#254（本 hop 明確禁令）。
- 不要另存 `7-review-reviewer-1.md` 進 feature 目錄。
- 不要改產品碼。Verdict 後改碼會作廢 G3；產品 G3 還沒開始。
