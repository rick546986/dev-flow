# 派工：把保護做對稱（v3.5.0 獨立審查的 4 條）

> owner 用一句話觸發：
> 「讀 `~/dev/dev-flow/notes/dispatch-guard-symmetry.md` 照它跑，全程不打斷問人」。
> 寫於 2026-08-16（plugin v3.5.0，**未推、未 tag**）。前一輪任務書是
> `notes/dispatch-guard-coverage.md`，三部分**大部分做完且實測有牙**，本檔是它的獨立審查結果。

## 先講清楚：上一輪做得不錯

獨立審查（18 個自造破壞實驗）確認：

- 第一部分 6 條 → **4 條做完有牙**（N-2 地板、N-3 訊息內容、N-4 未閉合註解、N-6 行號），2 條不完整
- 第二部分 5 條 → **3 條做完有牙**（引擎 fence 遮蔽、devtalk-guard obs、圍欄③），2 條沒做但**理由寫在 STATUS**
- 既有守衛**零退化**（背景清空、五格全指同一錨點、改 README 規格、模板改回舊值 —— 四個破壞實驗全部照樣變紅）
- 紀律面全過：防守清單原封不動、歷史紀錄零改動、HISTORY 只增不改、散發副本逐位元相同、
  三行被刪的斷言**逐條核對皆改成更嚴**
- 新增的 `guard-selfpin`（守衛的守衛）實測有牙

**判 REQUEST_CHANGES 的理由只有一個**，而它是這個 repo 的老毛病第三次發作。

---

# 第 6 型假綠：不對稱保護

> **修法只套在「觸發它的那一個實例」上，沒有推廣到同類的其他實例。**

這已經是第三次：

| 次 | 病灶 | 只修了 | 漏掉 |
|---|---|---|---|
| 1 | `PINNED_PAT` 缺 `Decision` | 7-review 一站 | 2-decision |
| 2 | 「盤點型守衛要跟著每個新資料格一起長」（A7 自己寫的原則） | 動線五格 | 背景章節 |
| 3 | **X-1（本輪）**：第 2 層對帳的獨立重算 | **4-spec 一站** | **2-decision / 7-review** |

**所以本輪追加一條制度要求**（做完要寫進 `README` 或守衛檔頂註，讓下一棒看得到）：

> 新增任何「只對某個 stage／某個檔／某個群組」的保護時，**必須在同一個 commit 裡說明
> 為什麼其他同類不需要**。說不出來就是不對稱，要嘛推廣、要嘛寫明限制並列進 Backlog。

---

# 四條缺陷

## X-1（HIGH，blocker）：第 2 層對帳只對 4-spec 獨立重算

**位置**：`scripts/check-gate-twin.sh:933`（三站都跑的 `missing` 斷言）與 `:935`
（`if st == "4-spec":` 才跑的獨立重算）。

**機制**：`:933` 那條把「產生器自報的 dropped NOTE」當成合法下落之一
（`t not in dropped_notes`）。所以**產生器只要假報一筆 dropped，那一節就算「有下落」**。
`:935` 的獨立重算（不信自報清單、雙向比對）**只對 4-spec 跑**。

⚠️ **這個風險是它自己寫在註解裡的**（`:936-939`）：
> 「下落若是『產生器聲稱 dropped』而產生器自己算錯，第 2 層直接信那份自報清單，
> 兩層一起綠、章節被真的丟掉卻印假 NOTE」

**它知道，但只修了三站裡的一站。**

**審查者的重現**（改 2 行：背景迴圈 `continue` + 假 `dropped.append(title)`）：
- 7-review 的 `Operational Walkthrough` 在出貨 html 出現 **0 次**（檔案 49908→47332 bytes）
- `✅ gate twin 產生器守衛:全過(133 項)`、`devflow-check rc=0`
- 2-decision 同法（`Risks & Mitigations`）亦全綠
- 換成 `Rejected Alternatives` 才紅，但**紅的是「T7 每個錨點都有對應目標」——
  偶然被錨點檢查接到，不是通用對帳**

**修法要求**：把 `:935` 的獨立重算**推廣到三站**。`independent_droppable_l2()` 目前的
可 drop 判準是針對 4-spec 的 R/S 結構，2-decision 與 7-review 的「合法可 drop」是什麼
要各自定義清楚 —— **定義不出來就代表那兩站不該有任何 dropped，那更好辦：
直接斷言 `gen_dropped == set()`。**

做完用審查者那個 2 行破壞實驗自驗（三站各一次），全部必須紅。

## X-2（MED）：路徑守衛的掃描來源沒有數量地板

**位置**：`scripts/check-no-stale-paths.sh:171-181` 的 `tracked_files`。

上一輪把它改成 fail-closed（`git ls-files` 全量 − 印出的豁免）——**方向對，但清單上游沒守**：
把 `["git","-C",root,"ls-files","-z"]` 加一個 `"--","README.md"`（**1 行**）→
`活文件掃描:1 個檔案`、禁字塞進 `hooks/devflow-lib.py` 零命中、`✅ 全過` rc=0。

ALLOWLIST 釘了字面，但 `len(all_files)` / `len(candidates)` 沒釘
（只有 `if not candidates` 才 exit 2 —— 掃到 1 個檔不算空）。

**另一件事**：`git ls-files` 看不到**未追蹤檔**（實測未 `git add -N` 的禁字檔零命中）。
新檔在 commit 前不受保護 —— 判斷要不要處理（例如改用 `git ls-files --others --exclude-standard`
一併納入），不處理要寫明理由。

## X-3（MED）：群組數這條軸沒有地板也沒有靜態釘

**位置**：`scripts/check-gate-twin.sh:58-83`（`REQUIRED_GROUPS`）、
`scripts/test-architecture-guards.sh:990-1000`（GS-9 靜態互釘）。

檢查數這條軸**兩者都有**（`MIN_CHECKS` 地板 + GS-9 釘死 4 個數字字面），
群組數只有 `:1019` 的 `print(f"  • heartbeat:{len(REQUIRED_GROUPS)} 個必跑區塊…")`——
**只列印，不斷言**。

審查者實測：刪掉 `n4-unclosed-comment` 整個區塊 + 刪 `REQUIRED_GROUPS` 裡對應條目 +
補 3 條填充檢查 → `✅ 全過(133 項)`、`heartbeat:23 個必跑區塊全部有執行`、
GS-9 全過、arch 65/65、`devflow-check rc=0` —— **所有「守衛的守衛」都同意**。

修法：群組數比照檢查數，補地板 + 進 GS-9 的靜態釘。**這條就是「對稱」的字面意思。**

## X-4（LOW）：`check(True` 規則只自掃兩個檔，而本輪剛好新增了一條

`scripts/check-realworld.sh:191` 有一條真的 `check(True, "舊模板/衍生檔仍可渲染…")`。
而「原始碼不得出現 `check(True`」的規則只掃 `check-gate-twin.sh`（`:1001`）與
`check-design-contract.sh`（`:514`）**自己那一檔**。

修法二選一（你裁決）：
- 把該規則推廣成**跨檔掃描**（掃 `scripts/*.sh` 全部），然後修掉 `check-realworld.sh:191`
  那條（讓它真的驗一件事，或改成明確的 skip 記號）
- 或維持自掃，但在 `check-realworld.sh:191` 就地把恆真改掉，並寫明為何不推廣

**注意**：`check-design-contract.sh:510` 的正則只掃**敘述開頭**（`^\s*check(True`），
所以 `check(1 == 1, …)` 繞得過（審查者實測 E4 全綠）。這是既有弱點不是本輪引入的 ——
一併處理或寫明理由。

---

# 兩件記帳問題

1. **第三部分的逐條分類沒有落檔**：上一輪要求對 11 條做行為層補驗、分三類回報
   （①有守衛且會紅 ②有守衛但不會紅 ③沒有守衛）。三件補強實測**都有牙**，
   抽驗的「①」也屬實，但**逐條分類只存在於附錄 A8 的彙總句，repo 內沒有逐條記錄**，
   審查者無法核對其餘各條 → 判「未查證」。
   **要做**：把 12 條的逐條歸類與證據落成表（放 `7-review.md` 附錄或 findings 對應節）。
2. **數字不一致**：任務書寫 **11 條**，commit `2046d69` 與附錄 A8 寫 **12 條**。查出哪個對並統一。

> ⚠️ 勘誤（2026-08-17）：正確為 **12 條**。任務書這裡的「11 條」沿用了
> `notes/dispatch-guard-coverage.md` 第三部分「其餘 11 條」那句話的字面，但那句話
> 本身宣稱排除 3 條、逐字卻只點名 2 條（A-2、A-1）—— 14 − 2 = 12，與
> commit `2046d69`、附錄 A8「12 條」一致。逐條歸類表與 B-2 更正紀錄見
> `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 A9。

---

# 驗收（每條都要「四步」）

1. 先在**未修改狀態**下重現審查者描述的失敗（證明你懂那條在講什麼）
2. 修
3. **重做同一個破壞實驗，守衛必須紅** —— X-1 要三站各做一次
4. 還原，確認全綠

回報時每條附這四步的實際輸出。

六道回歸不得退化（數字以當下輸出為準，不要寫死進活文件）：
```bash
bash scripts/devflow-check.sh
bash scripts/check-gate-twin.sh
env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
bash hooks/selftest.sh
bash hooks/devflow-exec.sh doctor
bash scripts/render-methodology-corrections.sh --check
```

---

# 模型分層

| 層 | 模型 | 做什麼 |
|---|---|---|
| 執行 | **haiku** | X-3 補地板與靜態釘、X-4 就地修、記帳問題、跑指令收輸出 |
| 審查 | **sonnet** | 每條修完派 fresh-context sonnet 審，**要它自己設計破壞實驗**，不看你的解釋 |
| 裁決與驗收 | **你** | X-1 的三站推廣（2-decision/7-review 的「合法可 drop」怎麼定義）、X-2 的未追蹤檔要不要納入 |

**X-1 是設計題**：先想清楚三站的可 drop 語意，再動手。

---

# 追加項（2026-08-16,owner 指示補入,同批做）

## X-5（MED,owner 裁定=固化模型分層）：先低階再高階目前只有 prompt 紀律,零機械層

**現況**：分層規則住在 dev-run SKILL(haiku 寫碼→sonnet 審→錯誤升階)與 owner 的
doctrine —— 全是 prompt 級。prompt 紀律的失效是**靜默的**(沒遵守不會有紅字,與
「守衛沒武裝」同型);obs 事件其實記錄了每次派工的 model,但沒有任何檢查在看。

**要做（兩層,a 必做、b 窄版）**：
1. **a. 稽核型**：新檢查掃 observability ledger —— ①同一 task 的第一次 attempt
   就用最高階模型 → 紅 ②跳級升階(低階無失敗紀錄直上兩級)→ 紅。
   註冊進 devflow-check;負向 fixture;照家規先印計數、掃到 0 筆事件 exit 2。
2. **b. 攔截型（窄版+豁免）**：PreToolUse 看得到派工參數的 model —— 擋「首派即
   最高階」一種就好(升降級全邏輯需要狀態與判斷,hook 不硬做);
   **必須有豁免通道**(allow --reason 型,例:G3 仲裁首派高階是合法的),豁免要留痕。
3. prompt 紀律不拆(它管「該怎麼做」);機械層只管「沒照做會現形」。
4. 驗收照本檔四步;b 的 selftest 案例含「豁免後放行+留痕」與「舊 state 行為不變」。

## X-6（MED）：兩份導覽各嵌一張生命週期圖 = 雙副本,零同步守衛

`guides/guide-dev-flow.html` 的 `fig-lifecycle` 與 `guides/guide-quickstart.html` 的
`fig-lifecycle-qs` 是複製體 —— 改一張另一張靜默漂移。**這正是本檔第 6 型
(不對稱保護)的預防案例**:要嘛補同步守衛(兩張 svg 正規化後比對,id/class 前綴差異
白名單),要嘛宣告單正本+另一張改成縮減版並寫明取捨。不接受「先放著」。

## X-7（LOW）：artifact 載體上錨點不跳,裁決 JS 要不要進正式檔

guides 的頁內錨點在本機正常,在 artifact/iframe 載體點了不跳(fragment 導航被當
新網址)。目前的捲動修正 JS 只注入在預覽產物。裁決:要不要把那段 ~8 行的
scrollIntoView 處理進正式 guides(利:任何 iframe 載體都能用;弊:四份 html 各加一段)。
做或不做都要寫明理由。

---

# 硬約束（沿用）

1. **不 push**、不繞過 deny 規則。做完把「請你自己跑 `git push origin main`」列在回報。
2. 不直接 commit `main`：feature branch → `git merge --no-ff` 回 main，一個 commit 一件事。
3. **不得為了讓檢查變綠而放寬檢查本身**。
4. 改 `_templates/*.md` 要跑 `render-methodology-corrections.sh --write`，收工 `--check` 要 `6/6`。
5. 散發副本要一致（`docs/dev/tools/` vs 正本）。
6. `docs/dev/HISTORY.md` **只能用 `scripts/history-append.sh` 追加**。
7. 不動歷史紀錄類文件的內容（只能加註）。
8. 不在活文件裡寫死會腐化的數字。

⚠️ **目前 repo 狀態**（開工前先確認）：
- `main` = v3.5.0 的 release commit，**未推、未 tag、未建 GitHub release**
- 另有分支 `feature/guides-lifecycle` 帶一個導覽重寫的 commit **未 merge** ——
  **那不是你的任務，不要動它，也不要 merge 它**
- 你的工作一樣走新的 feature branch，從 `main` 開出來

# 完成之後

- `docs/dev/STATUS.md` Backlog 反映真實剩餘
- `docs/dev/HISTORY.md` 追加一筆
- `7-review.md` 追加附錄 **A9**
- 第 6 型「不對稱保護」與那條制度要求要寫進**看得到的地方**（README 或守衛檔頂註），
  不要只留在本檔
- 屬「新增檢查」→ 走 `/dev-release` **minor**（v3.5.0 → v3.6.0），**停在 push 前交給 owner**
  （若判斷 v3.5.0 尚未推出、應合併為同一版，說明理由後照做）

# 禁止

- 不 push、不動 `feature/guides-lifecycle`
- 不因為「全過」就宣稱修好 —— 每條都要有「弄壞會紅」的證據
- **X-1 不接受「再幫 7-review 加一條」這種逐站手加**：要嘛推廣獨立重算到三站，
  要嘛對那兩站直接斷言「不得有任何 dropped」
- **X-3 不接受「把群組數寫進註解」**：要真的斷言
- 找不到問題或判斷不該做 → 直說並寫明理由，不要硬湊
