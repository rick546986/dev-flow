# 派工：`_templates/HISTORY.md` 兩個出廠缺陷（採用現場回報，2026-08-19）

> owner 用一句話觸發：
> 「讀 `~/dev/dev-flow/notes/dispatch-history-template-defects.md` 照它跑，全程不打斷問人」。
> 寫於 2026-08-19（plugin v3.8.0，**已推、已 tag**）。
> 來源：一個採用 dev-flow 的前端 repo 在 v3.8.0 fresh install 當下踩到，兩缺陷都在
> **install 後的第一輪 check 與第一筆歷史追加時**現形。
> 這不是既有派工單的續集，是新的採用現場回饋。
>
> ⚠️ **本檔所有行號以本開發 clone 現況（`main` = `b4d07dc`）為準**，不是以已發布的
> v3.8.0 為準 —— `README.md` 與 `skills/dev-setup/SKILL.md` 兩檔在這個 clone 裡已比
> v3.8.0 多了改動，行號會差。`_templates/HISTORY.md`、`_templates/STATUS.md`、
> `hooks/history-guard.sh`、`scripts/check-history-integrity.sh` 兩邊逐字相同（實測 diff）。

## 為什麼值得一份派工單：兩件都是「每個新採用專案必踩一次」

`_templates/HISTORY.md` 是 dev-setup install 步 1 建立採用專案 `docs/dev/HISTORY.md`
的唯一來源。它出廠帶著兩個問題，而 v3.8.0 的**全部既有機械檢查都是綠的** ——
`check-history-integrity.sh`、`check-dev-setup-discipline.sh`、`selftest.sh`（378/378）、
`gate-consistency.sh`（14/14）、doctor（`COMPATIBLE`）沒有一項會紅。

級別我按「現場已踩到 + 修法一行級 + 每個新採用專案必踩」判 **A**（Backlog 目前只有
B/C，A 列是新開的）。不同意就改 B，但請在 Backlog 留一句理由。

---

## D-1（A）：模板教的寫入口路徑在採用專案不存在；同套另兩處都寫對了

**位置與現況**（行號依本 clone 現況，見頂註）：

```
_templates/HISTORY.md:11  > scripts/history-append.sh --slug <代號> --what <做了什麼> --why <為什麼> --where <落在哪>
_templates/HISTORY.md:17  每筆的格式(由 scripts/history-append.sh 產生,不要手打):
```

`skills/dev-setup/SKILL.md:66` 明定散發目的地是 `docs/dev/tools/history-append.sh`。
所以採用專案照散發後的 `docs/dev/HISTORY.md` 頂註打指令 → 檔案不存在。

**同套已經寫對的兩處，直接當修法範本**：

```
_templates/STATUS.md:82        docs/dev/tools/history-append.sh --slug <代號> ...
hooks/history-guard.sh:42-43   採用專案  → docs/dev/tools/history-append.sh(dev-setup 散發)
                               方法論母版 → scripts/history-append.sh
```

`hooks/history-guard.sh` 那兩行是完整解：分兩行標明採用專案側與母版側，不假設讀者在哪一側。

**重現**（母版檔案，最小輸入）：

1. `grep -n "history-append.sh" _templates/HISTORY.md` → 兩筆都是 `scripts/…`
2. `grep -n "history-append.sh" _templates/STATUS.md` → `docs/dev/tools/…`
3. `grep -n "history-append.sh" skills/dev-setup/SKILL.md` → 散發目的地
4. 對任一乾淨 repo 跑 dev-setup install，在該專案根執行模板教的那條指令：
   `scripts/history-append.sh --slug <代號> --what a --why b --where c`
   → `No such file or directory`

**影響**：同一套方法論的兩份出廠模板對同一支腳本給出不同路徑，而寫錯那份正好是使用者
要寫紀錄時第一眼會讀到的檔案本身。照它走會失敗；失敗後最可能的下一步是改用 Edit/Write
直接編輯 —— 那正是 `history-guard` 要防的並發覆寫行為。**缺陷把使用者推向守衛要防的行為。**

**不在範圍**：`README.md:109` 同樣寫 `scripts/history-append.sh`，但位於
`<!-- devflow:master-only:start -->` 區塊內（起始標記 `README.md:54`、結束標記 `README.md:114`），install 步 1 的
剝除管線會移除，不散發給採用專案。母版自身視角下該行正確，**不要順手改它**。

---

## D-2（A）：出廠模板在檔尾留了一筆種子紀錄，而清掉它需要手改一個受守衛攔截的檔案

**位置與現況**：`_templates/HISTORY.md:34-37` 是一筆**可見的**種子紀錄（不在註解區塊內）：

```
34  ## YYYY-MM-DD · <第一筆的代號>
35  - 做了什麼:<可觀測的結果>
36  - 為什麼:<當初的痛點>
37  - 落在哪:<檔案或目錄>
```

同檔 `:16-32` 已有一段 `<!-- ... -->` 註解在示範同一件事（逐筆格式）。**那段是正確做法**
—— 兩段內容重疊，但只有後者會被散發成可見文字。

**重現**：

1. 對任一乾淨 repo 跑 dev-setup install
2. 用唯一寫入口追加第一筆真實紀錄：
   `docs/dev/tools/history-append.sh --slug <代號> --what <一句> --why <一句> --where <一句>`
   → 回傳碼 0
3. `tail -8 docs/dev/HISTORY.md`，實際長相（種子紀錄末行與真實紀錄標題行**直接相鄰，
   中間無空行**）：
   ```
   - 落在哪:<檔案或目錄>
   ## <日期> · <代號>
   - 做了什麼:<真實內容>
   ```
4. 嘗試用 Edit/Write 清掉種子紀錄 → `hooks/history-guard.sh` 命中
   （`hooks/hooks.json` PreToolUse matcher `Edit|Write`，case 分支 `*/docs/dev/HISTORY.md`）
   → exit 2 擋回

**影響**：該檔是 append-only 索引，頂註明文「只增不改」「不要直接編輯本檔」，設計上不容許
事後改寫，種子紀錄因此**無法用符合設計的手段移除**。結果只有兩種：

- 留著一筆填空假資料永久卡在歷史最前面（人工考古與 `check-history-integrity.sh` 的
  日期順序／欄位完整性檢查都要面對這筆非真實資料）
- 繞過守衛手改（而守衛存在的理由是防靜默覆寫，繞過的代價高於留著）

**這是出廠狀態自我矛盾**：一個禁止手改的檔案，不應該在建立時就帶著非手改不能清的內容。

**修法方向**（二選一，不含實作）：

- (a) 把 `:34-37` 移入既有的 `<!-- ... -->` 區塊（與 `:16-32` 同一段即可，內容本來重疊），
  或整段刪掉
- (b) 由 `scripts/history-append.sh` 在首次追加時偵測並移除種子區塊 —— 這條要同時處理
  「使用者已經照種子格式手填過內容」的情況，複雜度高於 (a)

我建議 (a)：兩段內容本來重疊，刪一段不損失資訊，而且不動腳本邏輯就沒有回歸風險。

---

## D-3（A）：現有檢查對這兩件事零覆蓋 —— 不補就會漂回去

兩缺陷在 v3.8.0 通過全部既有檢查的情況下存在。這是第 7 型「不對稱記帳」的同型風險：
**修好一次但沒有守衛釘住，下一棒重寫模板時會靜默漂回去。**

`scripts/check-history-integrity.sh` 加兩項斷言：

1. `_templates/HISTORY.md` 內出現的寫入口路徑字串，必須含採用專案側路徑
   （不得只有母版側路徑）—— 對帳來源用 `skills/dev-setup/SKILL.md` 的散發目的地，
   **不要在 script 裡寫死路徑字串**（寫死等於讓 script 變成第四份會漂移的複本）
2. `_templates/HISTORY.md` 內不得有任何位於 `<!-- ... -->` 區塊之外的 `## ` 條目

兩項都要有「弄壞會紅」的證據：把路徑改回母版側 → 第 1 項紅；把種子紀錄搬出註解 →
第 2 項紅。

---

# 硬約束（沿用母版既有八條）

1. **不 push**、不繞過 deny 規則。做完把「請你自己跑 `git push origin main`」列在回報。
2. 不直接 commit `main`：feature branch → `git merge --no-ff` 回 main，一個 commit 一件事。
3. **不得為了讓檢查變綠而放寬檢查本身。**
4. 改 `_templates/*.md` 要跑 `render-methodology-corrections.sh --write`，收工 `--check` 要 `6/6`。
5. 散發副本要一致（`docs/dev/tools/` vs 正本）。
6. `docs/dev/HISTORY.md` **只能用 `scripts/history-append.sh` 追加**。
7. 不動歷史紀錄類文件的內容（只能加註）。
8. 不在活文件裡寫死會腐化的數字。

⚠️ **這一輪特有的約束**：

- 改 `_templates/HISTORY.md` 會改變 dev-setup 的比對基準。採用專案側已建立
  `.devflow-baseline/` 的，會把這次修改正確歸類成「上游改寫」直接覆蓋；
  **尚未建立基準的採用專案（過渡態）會被要求逐檔徵同意** —— 這是既有設計，不用為它改什麼，
  但回報時要提一句，讓 owner 知道採用現場會看到什麼。
- 已存在的採用專案的 `docs/dev/HISTORY.md` 裡那筆種子紀錄，**這次修改不會回頭清掉**
  （upgrade 只覆蓋受管檔，不動已產出的 HISTORY）。要不要提供一次性清理路徑，
  是獨立裁決，不要塞進本輪。

# 完成之後

- `docs/dev/STATUS.md` 的 Backlog 移除 D-1/D-2/D-3 三列（本輪處置完）
- `docs/dev/HISTORY.md` 用 `scripts/history-append.sh` 追加一筆
- 屬「修 bug + 新增檢查」→ 走 `/dev-release` **patch 或 minor**（由 owner 裁決），
  **停在 push 前交給 owner**

# 禁止

- 不 push
- 不改 `README.md:109`（那行在母版視角下正確，見 D-1 末段）
- 不因為「全過」就宣稱修好 —— D-3 兩項檢查各要有「弄壞會紅」的證據
- 不在 `check-history-integrity.sh` 裡寫死路徑字串（要從 `skills/dev-setup/SKILL.md`
  動態取散發目的地）
- 判斷不該做或級別該降 → 直說並寫明理由，不要硬湊
