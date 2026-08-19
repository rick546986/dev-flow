# 接手單 — 2026-08-19（白話判斷輪 + 派工分層第一輪）

> 這份是**接手用的交接單**，不是派工單。看完就知道做到哪、下一步做什麼。
> 對應的完整需求正本：`notes/dispatch-agent-dispatch-layer.md`（派工分層那半）。

## 做完了什麼（都在 `main`，`f3d9e4a`）

| 批 | 內容 | 驗證 |
|---|---|---|
| 自判表 | 四張「模型自己拍板、等人核可」的表加「依據」欄；規格那張分上下兩層＋補「若被推翻會怎樣」 | `scripts/check-selfjudgment-tables.sh` 36 項 + 負向 fixture |
| 白話回覆 | 每次送出訊息前提醒模型講人話（`hooks/devflow-plainspeak.sh`，**預設關**，設 `DEVFLOW_PLAINSPEAK=1` 才開）；規則正本 `hooks/plainspeak-rules.md`，程式不自帶副本 | `check-hooks-accounting.sh` 第 ⑤ 節實跑逐字比對 |
| 敘述簡化 | 掃描 20 條全數處置：跨處用詞不一致、巢狀條件、規則與案例混寫、執行清單七處拆步（頂層步號不動） | `devflow-check.sh all` + `check-devtalk-guide-sync.sh` |
| 派工分層 1-5 步 | sequential 三條武裝路徑補 `exec-v4` + `run_id`（守衛原本在最常用那條路整支失效）；`agents/` 兩支唯讀審查者；稽核地板 | `selftest.sh` 392、`test-architecture-guards.sh` 83 |

全綠狀態：`devflow-check.sh all` 4 組全過 / `selftest` 392 / `gate-consistency` 14 /
`test-architecture-guards` 83 / `doctor` COMPATIBLE / `check-file-map` 83 支。

## 沒做完的，接手先處理這四件

1. **第 6 步兩個平台探針只落了樣本檔，結論沒驗過**
   `scripts/fixtures/dispatch-guard/probe-3a-tools-readonly.json`、`pst-real-payload.json`
   已經在 repo 裡，但**執行者在寫收尾報告之前被中止**，探針的實測結果與結論沒有經過第二個人複核。
   接手要：重跑探針、確認結論、補進 `notes/dispatch-agent-dispatch-layer.md` 或另立記錄。

2. **兩支具名審查者的型別字串沒有第二人複核**
   `agents/devflow-reviewer.md` 的說明寫「型別字串是 `dev-flow:devflow-reviewer`，帶命名空間」，
   標成「實測確認」，但**沒有第二個人複核過**。這個字串錯了，未來任何以型別為判準的檢查都會寫錯。
   接手要：裝好 plugin 之後在**別的專案**實際叫一次，確認叫得出來、確認字串長什麼樣。

3. **契約檔表達不了兩種格式並存（要 owner 裁決）**
   `devflow-contract.json` 的 `exec_state` 是單一字串 `"exec-v3"`，只對應「單一任務」那條路；
   其他三條路現在寫的是 `exec-v4`。現在不會壞（相容性檢查已改成印說明、不判失敗），但契約沒反映現實。
   三條路：①拆兩個鍵 ②改成清單 ③先不動、等第二輪一起想。**rick 傾向 ③，但還沒正式拍板。**

4. **還沒發版**
   `.claude-plugin/plugin.json` 還是 `3.8.0`。這輪新增了 hook、agents、檢查腳本，
   照語意應該是 **minor**。發版要走 `/dev-release`，它會同步兩處版本號、跑驗證、打 tag。
   ⚠️ **不發版的話，其他機器 `/plugin update` 什麼都不會拉，而且不會有任何提示。**

## 第二輪（另立派工單，本輪明文禁止碰）

`notes/dispatch-agent-dispatch-layer.md` §11「第二輪」那格：§5 B（分層資料檔）、
§6.2 C′（升階判準從「起過」改「失敗過」）、§8 D（README 與導覽頁鏡像加守衛）。
理由是它們會反轉 `hooks/selftest.sh` 現有的八條釘死案例，跟第一輪的行為變更混在一起就分不出誰造成的。

## 換到另一台機器要注意的三件事

1. **Windows 沒有 `/usr/bin/python3`**：守衛需要 python3。找不到時**只印一行警告就放行** ——
   代價是那次呼叫沒有保護，不是功能壞掉，所以**很容易沒發現**。
   要另外裝 Python 並確認 `python3` 在 PATH 上，或設環境變數 `DEVFLOW_PYTHON` 指向直譯器。
2. **白話回覆預設是關的**：要在 `~/.claude/settings.json` 或專案的 `.claude/settings.json`
   的 `"env"` 區塊加 `"DEVFLOW_PLAINSPEAK": "1"`。
3. **個人帳號的 `plain-language-zh` skill 沒有進 repo**：它住在 `~/.claude/skills/`，
   Mac 上已經改成一行指標指回 plugin 的 `hooks/plainspeak-rules.md`。
   換機器要自己重建一份同樣的指標，或直接靠上面第 2 點的 hook（規則一樣，正本同一份）。
