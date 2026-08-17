# 派工：清空所有已知待辦（審查 6 條 + Backlog 5 條 + 效能 1 條 + 採用現場 2 條）

> owner 一句話觸發：
> 「讀 `~/dev/dev-flow/notes/dispatch-accounting-symmetry.md` 照它跑，全程不打斷問人」。
> 寫於 2026-08-17（plugin v3.6.1，遠端已同步、tag 與 release 都在）。
> 前一輪任務書 `notes/dispatch-guard-symmetry.md` 的 **X-1~X-7 七條全部做完且實測有牙**。
>
> **這一輪的目標是把所有已知待辦一次清空**，三部分：
> 一、獨立審查的 6 條（F1~F6）　二、`STATUS.md` Backlog 的 5 條　三、效能 1 條
> 　四、**採用現場實際踩到的 2 條母版缺陷**（G1/G2，2026-08-17 回報，owner 端已複驗）。
> 做完之後 owner 會再驗收一次。

## 上一輪的成績（先講清楚，這輪不是打回重做）

獨立審查做了 **23 個自造破壞實驗 + 13 種 hook 邊界情境**，確認：

- **X-1（前輪 blocker）做完**：第 2 層對帳推廣到三站。2 變體 × 3 站 = 6 個破壞實驗全紅
- X-2~X-7 **全部做完**，各有實測證據
- **新 hook 的 fail-open 宣稱成立**：13 種情境（無 `.devflow/`、`exec.json` 壞、model 缺席／非字串／null／list、非 Task 工具、空 stdin、import 期 crash…）**全部放行**；15.9MB 事件檔走攔截路徑 0.56 秒
- 既有守衛零退化（6 個回歸破壞實驗全紅）
- 第 6 型制度要求已進 `README.md:287`
- A9 記帳誠實，**自曝兩條原判有誤並翻案**

---

# 第一部分：獨立審查的 6 條

## F2（第一優先）：守衛在大檔案下靜默失效

**這條審查者標成「既有型態、不列本輪 blocker」，技術上對；但它是這份任務書裡最該先修的一條。**

## 現象（owner 端親測，可直接重跑）

```python
# 1100KB 的 Write payload
{'tool_name':'Write','tool_input':{'file_path':'/tmp/x','content':'A'*1_100_000}}
→ bash hooks/devflow-guard.sh  rc=126
  hooks/devflow-guard.sh: 列 6: /usr/bin/dirname: Argument list too long

# 同一個操作，10KB
→ rc=0
```

## 根因

`HOOK_INPUT=$(cat); export HOOK_INPUT` —— 把整包 payload 塞進**環境變數**，
之後任何 `exec` 系呼叫都要把整個 environ 複製過去，撞 `ARG_MAX`（macOS 約 1MB）。

**影響三支**（`grep -ln 'export HOOK_INPUT' hooks/*.sh`）：
- `hooks/devflow-guard.sh` ← **這支是擋 scope 外寫入的主守衛**
- `hooks/devflow-prebash.sh`
- `hooks/devflow-dispatch-guard.sh`（新的，繼承同一寫法）

## 為什麼嚴重

`devflow-guard.sh` 是 **fail-closed** 的執行守衛。撞 ARG_MAX 之後它回 **rc=126**（shell 執行錯誤），
不是 0 也不是 2 —— **對 hook 宿主而言那是「守衛自己壞了」，通常等同放行**。

也就是說：**寫一個超過約 1MB 的檔案，就能繞過 Stage 6 的範圍守衛，而且不會有任何紅字。**
這是 fail-closed 守衛**靜默降級成 fail-open**，正是這個 repo 反覆在抓的那種病 ——
只是這次不在斷言層，在**傳遞層**。

## 修法要求

不要走環境變數。方向（擇一，你裁決）：
- `cat > "$tmp"` 存暫存檔，把**路徑**傳給 python（記得 `trap` 清理）
- 或直接 `python3 impl.py < <(cat)` / 把 stdin 原封不動 pipe 給 python，shell 層完全不碰內容

**三支一起改**（這就是第 6 型的字面要求：同類要一起長）。

## 驗收

1. 先重現：1100KB payload → rc=126（證明你懂）
2. 修
3. **1100KB payload → 行為與 10KB **完全一致**（該擋的擋、該放的放）
4. **加一條回歸案進 `hooks/selftest.sh`**：大 payload 下守衛行為不變 —— 沒有這條，下次改寫又會退回去
5. 順帶查：`_postbash_impl` / `devtalk-guard` / 其他讀 stdin 的地方有沒有同型問題

---

## F1（第二優先）：第 7 型「不對稱記帳」

## 現象

`hooks/hooks.json` 實際有 **6 條掛載**（本輪新增 `PreToolUse: Task|Agent`）。
但 `skills/dev-setup/SKILL.md`：
- `:169` 寫「hooks.json 壞掉 → **五條掛載**全靜默失效」
- `:176-178` 逐條列舉 **5 條**，漏掉 `devflow-dispatch-guard`
- `:175` 的「hooks/ **七支**可執行」清單也漏掉 `devflow-dispatch-guard.sh`

**本批 13 個 commit 完全沒動這個檔，而且沒有任何守衛釘這個數。**

## 為什麼是 blocker

`dev-setup` 的健檢是**安裝驗證清單** —— 採用專案照它跑，會把線上真實存在的第 6 支 hook
判成「多出來的」。

更難看的是：**同一份檔案自己寫過**「案數以腳本輸出為準，不在本檔寫死 ——
曾因寫死 33 案漂移至 80」，卻把掛載數寫死。

## 這是新的一型（第 7 型）

> **不對稱記帳**：保護機制長大了，所有 runtime 消費端都對，
> **唯獨「為了驗證而列舉它的那份文件」靜默不同步，而且沒有任何檢查在比對兩者。**

跟第 6 型（不對稱**保護**：修法只套一個實例）的差別：這次修法本身是對稱的，
**漏的是記帳**。而且它在**本輪主題（第 6 型）的這一輪自己復發** —— 這正證明
「寫進 README 的制度要求」不夠，**要有機械層**。

## 修法要求（不接受只改文字）

1. 改正 `SKILL.md` 的兩處列舉（掛載數、可執行清單）
2. **加一支守衛**：比對 `hooks/hooks.json` 的實際掛載 ↔ 所有「列舉 hook 的正本文件」
   （至少 `skills/dev-setup/SKILL.md`、`README.md`、`guides/guide-dev-flow.html` 的 hooks 註冊表）。
   數量與名稱都要比，**任一處漏列就紅**。註冊進 `devflow-check`。
3. 順手盤一次：repo 裡還有沒有別的「為了驗證而列舉某個機制」的清單，同樣沒有守衛？
   （例：散發副本清單、REQUIRED_GROUPS 之外的其他列舉）**找到就一起釘，這是第 7 型的通解。**
4. 第 7 型與這條通解要寫進**看得到的地方**（README 第 6 型那段旁邊），不要只留在本檔

---

## 其餘四條

### F3（LOW）：恆真偵測是可枚舉黑名單

`scripts/check-design-contract.sh:510,604`。`check(True` / `check(1 == 1` 擋得住，
但 `check(2 > 1, "poison")` 全綠（審查者實測）。邊界已寫在 `:546`。

**判斷要不要收**：可考慮改成「斷言的第一個參數不得是常數運算式」（用 `ast` 解析而非字面比對）。
不做要寫明理由 —— 這條有明文邊界，接受也是合法選項。

### F4（LOW）：唯讀檔案系統上，持有有效豁免卡仍被擋

`hooks/_dispatch_impl.py:92`。`_consume_exemption` 寫入遇 `OSError` → `return False` → `die()`。
但那支 hook 自稱 **fail-open**，「寫不進去」屬於環境問題，不該變成攔截。
修法：寫入失敗時**放行並印警告**（豁免卡沒能標記已用，下次還會再放行一次 —— 那是可接受的降級）。

### F5（LOW）：README §6 括號內的規格文字無守衛

`scripts/check-gate-twin.sh:205` 的 `re.split(r"[(（]", c)[0]` 在第一個括號截斷。
實測：`狀態(frontmatter)` 改成 `狀態(frontmatter)X` → **全綠**。
標籤本身有守衛，括號內的規格語意沒有。**這條是上一輪就存在的 G′ 缺口，還在。**

### F6（LOW）：導覽新增的 hooks 註冊表寫死 6 個 `timeout=15`

`guides/guide-dev-flow.html`，無守衛對 `hooks.json`。**F1 的守衛做好就順帶涵蓋它**
（那份表就是「列舉 hook 的正本文件」之一）。

---

# 第二部分：STATUS.md Backlog 的 5 條

正本在 `docs/dev/STATUS.md` 的 Backlog 表（每條附出處，**先讀出處再決定做法**）。
這些是前幾輪判斷過「當輪不做」而留下的，**這輪要處理掉或給出最終裁決**。

| 級 | 一句 | 這輪要做什麼 |
|---|---|---|
| **B** | **第二個範例 feature**，破「唯一範例自證循環」（4cap O-3） | 備註已更新：`docs/dev/engine-fence-masking/` 已是母版第一份真實走完 fast lane 的流程，**可清洗成第二個範例**。現在所有機械檢查都對著同一個範例跑 —— 範例本身錯了沒人會知道。**這條工作量最大，你裁決做或不做，不做要寫明理由** |
| C | 審查圍欄的寫入白名單（`7-review*`/`evidence/`）**guard 側有、postbash 偵測網側沒有** —— review 期間產 `7-review.md` 會被當 scope 外改動（已實測） | **這是第 6 型（不對稱保護）的又一個實例**：同一條白名單只加在一側。修法照第 6 型的要求做 |
| C | **tier-exempt 豁免卡是 repo 級不是 run 級**，`devflow-exec.sh stop` 不清卡 → 未消耗的豁免可能跨 run 存活 | 決定：改成 run 級、或 stop 時清卡、或維持並寫明為何可接受 |
| C | `bad-skip-level` 缺一條比照 MT-1 的 real-mode 外部案例（目前只在自測模式內驗） | 補案例 |
| C | SDC 大表、Reference App（4cap §7 收攏的低優先 deferred） | 低優先，**判斷不值得做就寫明理由留在 Backlog**，不要硬做 |

**做掉的移出 Backlog、沒做的留著並補上「本輪不做的理由」。不要為了清空而硬做。**

---

# 第三部分：`devflow-check` 跑一次要 5 分鐘

owner 端實測（2026-08-17）：

```
bash scripts/devflow-check.sh  →  23.33s user  22.79s system  15% cpu  4:55.20 total
```

24 組全過，但 **CPU 只用了 15%** —— 大部分時間在等，不是在算。
檢查數每輪都在長（18 → 20 → 21 → 24 組），現在還能忍，但**再長下去沒人會想在本機跑**，
而「沒人跑的檢查」等於沒有檢查。

**這是時間問題不是正確性問題**，所以要求很寬：

1. 先**量出時間花在哪**（逐組計時，把數字貼進回報）—— 沒量就改是瞎改
2. 依量測結果決定做法。可能的方向（你裁決，不必全做）：
   - 平行跑互不相依的組
   - 分快慢兩檔（`devflow-check.sh --fast` 給本機、完整版給 CI）
   - 找出單一最慢的那組，看它為什麼慢（例如反覆 `cp -R` 整個 repo、反覆起 python）
3. **硬約束：不得為了變快而少跑任何一組或放寬任何斷言。** 快慢兩檔的話，
   CI 一定要跑完整版，且要有守衛擋住「快檔悄悄變成唯一被跑的那檔」。

做不到或判斷不值得做 → 寫明理由，這條可以不做。

---

# 第四部分：採用現場實際踩到的 2 條母版缺陷

**這兩條的來源跟前面都不同** —— 不是審查者在母版 repo 裡找出來的，是**採用專案升級到
plugin 3.6.1 之後真的踩到的**。owner 端已逐條複驗，兩條都屬實。

## G1（HIGH）：`history-append.sh` 散發後把歷史寫到巢狀路徑

**位置**：`scripts/history-append.sh:34`
```bash
REPO_ROOT=$(cd "$SELF_DIR/.." && pwd)
```
這行假設腳本住在 `<專案根>/scripts/`。但 `dev-setup` 規定散發到 **`docs/dev/tools/`**，
於是 `REPO_ROOT` 變成 `<專案根>/docs/dev`，`:85` 的預設 target 就成了：

```
docs/dev/docs/dev/HISTORY.md      ← owner 端實跑複現,真的建出這個巢狀目錄
```

**而且是靜默的** —— 不報錯、不警告，只是寫到錯的地方。採用端是在跑 happy path
記錄一筆真實升級時才發現。

### 同型盤查（owner 端已做，結果如下 —— 你不用重做，但要確認我沒看漏）

| 散發到 `docs/dev/tools/` 的檔 | 怎麼定專案根 | 有沒有同樣的問題 |
|---|---|---|
| `build-gate-twin.py` | **從參數傳入**（`args[0]`），`_SCRIPT_DIR` 只用來找相依與 import | **沒有** |
| `devflow-evidence-gauntlet.sh` | 也有 `ROOT=$(dirname "$0")/..`，**但不用 ROOT 決定輸出**（吃 `<file.md>` 參數），且 B-4 已加 `--print-root` 讓 doctor 探測 ROOT 解析 | **沒有**（已知並已處理） |
| `devflow_twin_ui.py` | 純 UI 模組，不碰路徑 | 沒有 |
| **`history-append.sh`** | **用 `REPO_ROOT` 決定預設輸出位置** | **就是它** |

**所以 repo 裡已經有兩個正確做法可抄。**

### 修法要求

1. 不要用 `$SELF_DIR/..` 推專案根。建議 `git rev-parse --show-toplevel`
   （HISTORY.md 一定在 git repo 裡；解析失敗就要求 `--file` 必填並印清楚訊息）。
   **母版與散發副本都要對** —— 同一支腳本在兩個位置都要能跑出正確的預設路徑。
2. **加回歸案**：在 `scripts/fixtures/` 或 selftest 裡造一個「假採用專案」
   （`<root>/docs/dev/tools/history-append.sh`），不帶 `--file` 跑一次，
   斷言寫到 `<root>/docs/dev/HISTORY.md` **而不是** `<root>/docs/dev/docs/dev/HISTORY.md`。
   沒有這條，下次改寫又會退回去。
3. **比照 `gauntlet` 的 `--print-root`**：給 `history-append.sh` 加一個診斷旗標印出它
   解析到的根，並讓 `doctor` 探測它（第 6 型的字面要求：同類保護要一起長）。
4. 順帶查 `dev-setup` 的散發段有沒有需要補一句「這支的預設路徑依賴 X」。

⚠️ **這條在採用端已有 workaround**（一定要帶 `--file docs/dev/HISTORY.md`），
但那是把正確性押在人記得帶參數上 —— **不算修好**。

## G2（MED）：母版自己的 `dev-talk` SKILL 過不了母版自己的守衛

**位置**：`skills/dev-talk/SKILL.md:1`
```html
<!-- 原 dev-talk plugin 5.4.0,2026-08-13 併入 dev-flow;此後 dev-talk 不再有獨立版本號… -->
```
含 `dev-flow` 字眼 → `hooks/devtalk-guard.sh` 的盲原則掃描判 FAIL。owner 端實跑：

```
⛔ devtalk-guard:盲原則洩漏 —— 剛寫入的 dev-talk 檔案含下游階段字眼(不得出現):
1:<!-- 原 dev-talk plugin 5.4.0,2026-08-13 併入 dev-flow;… -->
```

**現況不影響運作**（guard 只在寫入 `skills/dev-talk/` 底下的檔時觸發），
但**只要有人改那個檔就會被自己的守衛擋死**。

⚠️ **這是「母版自己的產物過不了母版自己的守衛」的第二次** ——
第一次是 B-1（母版自己的 `_templates/5-tasks.md` 過不了 `parse_5_tasks`）。
**同一型出現兩次，代表需要的是機械層不是逐次修文字。**

### 修法要求（你裁決走哪條，但要說明理由）

- (a) 改那行註解，把版本沿革移到不受掃描的位置（例如 `docs/PLUGIN.md`）
- (b) 讓 guard 豁免 html 註解行或 frontmatter 之前的行 —— **但要小心這等於開了一個洞**
     （真的洩漏也可以藏在註解裡）
- (c) 兩者都做：改註解 + 加一條守衛，**對母版自己的 `skills/dev-talk/` 全部檔案跑一次
     devtalk-guard，必須全過** —— 這條是通解，能擋住 B-1/G2 這一整型

**建議 (c)**：沒有 (c) 的話，下次有人在那個檔寫下 `4-spec` 三個字又會重演。

---

# 這一輪之後**還會剩下什麼**（給你參考，不是任務）

即使上面三部分全部清空，以下仍未被驗證過 —— **不要在回報裡宣稱「完整工作流已無缺陷」**：

- **採用專案端的實際行為**：所有審查都在母版 repo 內做。安裝到真實專案後 hook 的觸發、
  `dev-setup` doctor 的消費路徑、四個採用專案升級後的相容性 —— 每一輪的審查者都在
  「沒審什麼」裡寫這條。
- **dev-flow 自己從來沒完整走過七站**：`b8-gate-twin-review-ui` 的 verdict 是
  `REQUEST_CHANGES`（自審 + 事後補）、`engine-fence-masking` 是 fast lane。
  完整 full lane（1-discussion → 7-review、過 G1/G2/G3）**一次都沒有**。

---

---

# 驗收（每條四步）

1. 先在**未修改狀態**下重現（證明你懂那條在講什麼）
2. 修
3. **重做同一個破壞實驗，守衛必須紅**（F2 是「行為必須與小 payload 一致」）
4. 還原，確認全綠

回報時每條附四步的實際輸出。**三部分都要回報**，格式：

```
## 第一部分：6 條  | id | 修法一句 | 落在哪(檔案:行號) | 破壞實驗四步的輸出 |
## 第二部分：Backlog 5 條  | 條 | 做了/沒做 | 做法或不做的理由 | 驗證 |
## 第三部分：效能  | 逐組計時原始數字 | 做法 | 改後時間 | 有沒有少跑任何一組 |
## 第四部分：採用現場 2 條  | id | 修法 | 回歸案落在哪 | 破壞實驗四步的輸出 |
## 待 owner 裁決(如果有)
## 六道回歸輸出(貼原文)
## 下一步：未推 commit N 個,請 owner 自己 push
```六道回歸不得退化（數字以當下輸出為準，不寫進活文件）：

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
| 執行 | **haiku** | F1 的文字改正、F6、跑指令收輸出 |
| 審查 | **sonnet** | 每條修完派 fresh-context sonnet 審，**要它自己設計破壞實驗** |
| 裁決與驗收 | **你** | **F2 的傳遞層改法**（三支 hook 一起動，是 live runtime）、F1 的守衛設計、F3 收不收 |

**F2 是 runtime 改動且影響三支主守衛 —— 自己動手或交 sonnet 但親自驗收。**

---

# 硬約束（沿用）

1. **不 push**、不繞過 deny 規則。做完把「請你自己跑 `git push origin main`」列在回報。
2. 不直接 commit `main`：feature branch → `git merge --no-ff` 回 main，一個 commit 一件事。
3. **不得為了讓檢查變綠而放寬檢查本身**。
4. 改 `_templates/*.md` 要跑 `render-methodology-corrections.sh --write`，收工 `--check` 要 `6/6`。
5. 散發副本要一致。
6. `docs/dev/HISTORY.md` **只能用 `scripts/history-append.sh` 追加**。
7. 不動歷史紀錄類文件的內容（只能加註）。
8. 不在活文件裡寫死會腐化的數字 —— **F1 就是這條被違反的實例，改的時候別再犯**。

# 完成之後

- `docs/dev/STATUS.md` Backlog 反映真實剩餘
- `docs/dev/HISTORY.md` 追加一筆
- `7-review.md` 追加附錄 **A10**
- **第 7 型「不對稱記帳」+ 通解寫進 README**（第 6 型那段旁邊）
- 發版：F2 是修既有缺陷、F1 新增守衛 → 由你判斷 `patch` 還是 `minor`，走 `/dev-release`，
  **停在 push 前交給 owner**

# 禁止

- 不 push
- 不因為「全過」就宣稱修好 —— 每條都要有「弄壞會紅」的證據
- **F2 不接受「只改新的那支 dispatch-guard」** —— 三支同型的要一起改
- **F1 不接受「只改文字不加守衛」** —— 沒有機械層，下次加第 7 支 hook 還會再漏一次
- 找不到問題或判斷不該做 → 直說並寫明理由，不要硬湊
