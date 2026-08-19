# 派工單（草案）：把「派工／執行／審查」從叮嚀變成機制

> **狀態：草案，尚未定案。** owner 會再往本檔加其他要優化的項目。
> 末節「待裁決」全部有答案之後，本檔才算派工單，執行輪才可以動手。
>
> 定案後的觸發句：
> `讀 ~/dev/dev-flow/notes/dispatch-agent-dispatch-layer.md 照它跑，全程不打斷問人`
>
> **本檔寫給沒有前情的 session 看**：所有結論都附 `檔:行` 與實跑證據，
> 不要求讀者先知道任何背景。看到「實查」兩個字就是主線程實際打開檔案看過的，
> 不是推論。

---

## 0. 名詞對照（先讀這節，後面全部用這套詞）

| 本檔用詞 | 指的是什麼 |
|---|---|
| **派工者** | 主對話本身（你）。負責讀規格、派人、收驗、commit、記帳。不寫碼 |
| **執行者** | 被派出去寫程式的 subagent |
| **reviewer** | 被派出去判 PASS/FAIL 的 subagent，唯讀 |
| **adviser** | 三層都失敗時，被派出去診斷「是規格錯還是執行錯」的 subagent，唯讀 |
| **具名型別** | Claude Code 原生機制：`agents/<name>.md` 定義一種 subagent，派工時用 `subagent_type: <name>` 叫它出來。被叫出來的 agent **只看得到那個 `.md` 的內容 + 你寫的 prompt**，主對話講過什麼一概看不到 |
| **ledger／執行軌跡** | `.devflow/` 底下的事件流水帳。記「派了誰、開始了、審完了」 |
| **自陳 vs 觀測** | 自陳＝派工者自己寫進 ledger 的；觀測＝hook 攔截到真實工具呼叫之後記下來的 |
| **武裝中** | `.devflow/exec.json` 存在且 schema 認得，代表正在跑 Stage 6 的某個模組 |

---

## 1. 這份要解決什麼

dev-flow 現在規定「派工者不寫碼、執行者獨立、reviewer 要乾淨 context」，
但**這些規定全部只是寫給主對話看的散文**，沒有任何機械強制。

### 1.1 實查證據（2026-08-19）

| 事實 | 證據 |
|---|---|
| dev-flow **沒有 `agents/` 目錄**，一支具名型別都沒有 | `find . -name "*.md" -path "*agents*"` 零命中 |
| 職責分工只存在於文件 | `skills/dev-run/SKILL.md:30-33` 的職責表（散文） |
| 唯一掛在 `Task\|Agent` 的 hook 只管一件窄事 | `hooks/_dispatch_impl.py:3-5`（檔頭自述「窄版」） |
| ledger 的 `agent_dispatched` / `attempt_started` / `review_started` 全是**派工者自陳** | `_dispatch_impl.py` 只讀 ledger 不寫；`_exec_impl.py` 的 `stop` 分支不驗事件序 |
| `gate-consistency` 只驗「文件都寫了同一套 reviewer 順序」，不驗實際做了沒 | `hooks/_gate_consistency_impl.py:223-244` |

**後果**：派工者可以自己寫碼、自己判 PASS、再補三筆流水帳說「我派了執行者、也派了
reviewer」—— 機械上不會有任何一支守衛紅。

### 1.2 對照組：harness-engineering 怎麼做

路徑：`/Users/asheng/Documents/stork/Harness/harness-engineering-plugin/plugins/harness-engineering/agents/`

| agent | model | maxTurns | 禁再派 agent |
|---|---|---|---|
| `worker`（寫程式） | `claude-sonnet-5` | 150 | 是（`disallowedTools: Agent`） |
| `reviewer`（唯讀審查） | `claude-opus-5` | 50 | 是 |
| `advisor`（診斷卡關） | `claude-opus-5` | 30 | 是 |
| `scaffolder` | `claude-sonnet-5` | 75 | 是 |
| `coordinator`（跑主執行緒，不是 spawn 目標） | `claude-sonnet-5` | 50 | 否 |

差別只有一句話：**它把角色寫成具名型別，dev-flow 只是在文件裡拜託主對話這麼做。**

它還把身分綁在工具權限上（worker 只有 Read/Edit/Write/Bash；reviewer 唯讀），
不是靠叮嚀。另有一節專講 context 節省
（`lib/skill-base/coordinator-prompt.md:125`）：subagent 的輸出會回流進派工者
context，連派幾隻就會撞壓縮，所以要求每個派工 prompt 結尾都附回報長度約束。

---

## 2. ⚠️ 驗證結果：「加組內順序」**不能**保證被遵守

> owner 問：加了組內順序（由便宜到貴、依序取）之後，是不是就保證實作會照做？
> **答案是不會。** 這節是實查之後的答覆，下面每一條都指得到行號。

### 2.1 唯一看得到派工的 hook，在判斷之前有六個早退

`hooks/_dispatch_impl.py:115-147`，依序：

| # | 條件 | 行 | 後果 |
|---|---|---|---|
| 1 | 工具不是 `Task`/`Agent` | `:120` | 放行 |
| 2 | `tool_input` 不是 dict | `:123` | 放行 |
| 3 | **`model` 缺席或非字串 → 放行** | `:125-127` | 見 2.2 |
| 4 | **`model` 不含 `opus`/`fable` → 放行** | `:129-130` | 「實作組該用 haiku 卻用了 sonnet」它**根本不看** |
| 5 | 未武裝／`exec.json` 讀不到／schema 不認得 | `:132-141` | 放行 |
| 6 | **本 run 已出現過任何低階 attempt → 放行** | `:144-145` | 見 2.3 |

它唯一會擋的情境：**武裝中 + 顯式帶了 opus/fable + 這個 run 從沒出現過 haiku/sonnet**。
其餘一律通過。它從頭到尾**沒有讀過任何順序**，因為現在根本沒有順序這個概念。

### 2.2 第 3 個早退實務上永遠命中 —— 守衛幾乎是 no-op

`skills/dev-run/SKILL.md:69-76` 的派工三件套，**從沒要求把 `model` 帶給 Task 工具**。
它只要求把 model **寫進 ledger 事件**（`attempt_started(attempt_id / agent_role /
model / prompt / base_sha)`）—— 那是自陳，不是工具參數。

所以正常操作下 `tool_input.model` 是缺席的 → 第 3 個早退命中 → **這支守衛平常等於沒裝**。

### 2.3 第 6 個早退讓「跑過一次 haiku 之後全程不設防」

`_scan_low_tier_attempt()` 一旦在 ledger 掃到任何一筆 haiku/sonnet 的 `attempt_started`
就回 True → 放行。也就是說：**這個 run 只要跑過一次低階，之後派幾次 opus 都不會被擋。**

### 2.4 結論

「組內順序」是**資料**，資料不會自己執行自己。要讓它被遵守，必須同時做到下面四件事。

---

## 3. 什麼樣的設計才真的保證得了（本檔的核心提案）

### 3.1 讓「不做選擇」就是正確答案

把 model 寫進 `agents/*.md` 的 frontmatter，值 = **該組第一順位**。

- 派工者**不帶 model** → 用 agent 定義的預設 → 天然就是第一順位 → 正確。
- 升階時才顯式帶 `model` 覆寫。Claude Code 的 Agent 工具契約明文支援：
  `model` 參數「Takes precedence over the agent definition's model frontmatter」。

這一步把「遵守」從「記得照做」變成「什麼都不做就是對的」。

### 3.2 四條新規則（都在 PreToolUse 可判定）

hook 在 `Task|Agent` 的 PreToolUse 拿得到 `tool_input.subagent_type` 與
`tool_input.model`，也讀得到 ledger。所以下面四條全部可機械判定：

| 規則 | 內容 | 為什麼需要 |
|---|---|---|
| **R1** | 武裝中的 Task 呼叫**必須**帶 `subagent_type` ∈ {executor, reviewer, adviser}，否則擋 | 沒有型別，hook 不知道這件工作該屬哪一組 |
| **R2** | 若顯式帶了 `model`，必須落在該 `subagent_type` 對應的組 | 防「reviewer 卻指名實作組模型」 |
| **R3** | model 不是該組第一順位時，ledger 必須找得到**前一順位在同一個 T 上的失敗紀錄**，否則擋 | 這就是「組內順序」真正被執行的地方 |
| **R4** | **移除或收窄 2.3 那個早退**（本 run 有低階 attempt 就全放行） | 不改的話 R2/R3 一輩子跑不到 |

R4 是關鍵：現行早退的目的是「允許合法升階」，但它的做法是**整個 run 從此不設防**。
改成「逐 T 判定」即可：升階要看的是「同一個 T 前一順位失敗過沒有」，不是「整個 run
有沒有出現過低階」。

### 3.3 fail-open 邊界不變

未武裝、schema 不認得、`model-tiers.json` 讀不到 → **一律放行**。
守衛不得因為自己讀不到設定就擋人派工（這是本 repo 既有慣例，`_dispatch_impl.py:9`
檔頭已寫明「fail-OPEN by design」）。R1 的「必須帶 subagent_type」只在**武裝中**生效。

---

## 4. A〔高〕建 `agents/`，把三個角色變成具名型別

### 4.1 要建的三支

harness 的 `scaffolder` 在 dev-flow 沒有對應角色；`coordinator` 對應主對話本身，
不需要具名型別。所以是三支：

| 檔案 | 角色 | 對應現況 |
|---|---|---|
| `agents/devflow-executor.md` | 寫碼、跑 Verify、貼 RED/GREEN 原文 | `dev-run/SKILL.md:30` 的「執行者(fresh subagent)」 |
| `agents/devflow-reviewer.md` | 依共用 acceptance seam 判 PASS/FAIL，唯讀 | 同上 `:31` 的「reviewer(fresh sonnet)」 |
| `agents/devflow-adviser.md` | 三層皆 FAIL 時診斷是 T 定義問題還是執行問題，唯讀 | 同上 `:51` 的 adviser |

frontmatter 至少要有：`name` / `description` / `model` / `maxTurns` /
`allowedTools` / `disallowedTools`。

**三支都要 `disallowedTools: [Agent]`** —— 執行者與 reviewer 不得再往下派，
否則層級會塌掉（harness 五支裡有四支這樣釘，只有 coordinator 例外）。

**reviewer 與 adviser 必須唯讀**：禁 Edit/Write，禁 `git commit`／`push`／`reset`
類命令。這是「派工者禁親修」（README §5 驗證五律 2）第一次有機械後盾。

⚠️ harness 的經驗（`agents/worker.md:9-13` 註解）：**平台會把 subagent frontmatter 裡
`Bash(pattern)` 這種帶括號的寫法吃掉**，只有裸 `Bash` 有效；真正的 deny 要靠
`.claude/settings.json` 的 permissions。dev-flow 抄的時候別重踩，
`disallowedTools` 裡的 `Bash(...)` 只能當文件訊號，不能當強制力。

### 4.2 連帶要改

1. `skills/dev-run/SKILL.md:30-33`、`:69-76`、`:77`：職責表與派工三件套從
   「派 fresh subagent」改成「用 `subagent_type: devflow-executor` 派」，明寫型別名；
   並補一句「**不要帶 model**，除非是升階（見 R3）」。
2. `.claude-plugin/plugin.json`：確認 `agents/` 會被 plugin 載入（沒載入 = 型別叫不出來）。
   **這一步要實測**：安裝後在別的專案打得出 `subagent_type: devflow-executor` 才算數。
3. 記帳面（第 7 型「不對稱記帳」）：`agents/` 是新的一組列舉對象 ——
   - `docs/PLUGIN.md` 現有 hooks 表與 skills 表，要加 agents 表；
   - `scripts/check-hooks-accounting.sh` 已有「skills 目錄 vs PLUGIN.md」的對帳
     （見該檔 ②' 節），照同一個模式加「agents 目錄 vs PLUGIN.md」；
   - `scripts/check-file-map.sh` 的 `EXPECTED_MAPPED_FILES`（現值 78）與檔案地圖節
     要不要納 `agents/*.md`，見待裁決 3。

---

## 5. B〔高〕模型分層改成「思考／實作」兩組 + 組內順序

### 5.1 這個分類為什麼是對的（不是新發明）

owner 提的兩分法**已經是現況的機械形態**，只是被寫死在程式碼裡：

```python
# hooks/_dispatch_impl.py:42-43
TOP_TIER_MARKERS = ("opus", "fable")      # ← 這就是「思考」
LOW_TIER_MARKERS = ("haiku", "sonnet")    # ← 這就是「實作」
```

harness 獨立演化出同一個切法（worker=sonnet 實作、reviewer/advisor=opus 思考）。
兩套系統收斂到同一條線。

跟鐵律 3（`~/.claude/rules/ironlaws.md`：haiku 機械活、sonnet 分析實作、
opus 只做最終判斷）**不衝突**：三個角色收成兩組，組內用順序保留 haiku→sonnet 的先後。

### 5.2 規則三句話

1. 一件工作只選**組**（思考／實作），不指定某個模型。
2. 組內**由前往後**取，順序 = 由便宜到貴。第一順位就是這組的預設。
3. **升階 = 組內往後走**；組內走完才跨組。跨到「思考」= 現行的「升 opus」。

### 5.3 資料檔

新增 `model-tiers.json`（位置見待裁決 2）。存**比對字串**不是完整模型 id ——
完整 id 帶日期後綴（`claude-opus-5-20260601`），寫死會漂：

```jsonc
{
  "schema": 1,
  "tiers": {
    "build": ["haiku", "sonnet"],     // 實作:寫碼、跑測試、機械活。由便宜到貴
    "think": ["opus", "fable"]        // 思考:審查、裁決、診斷。由便宜到貴
  }
}
```

加 deepseek 就是往清單插字串（例：`build` 加 `"deepseek-chat"`、
`think` 加 `"deepseek-reasoner"`），**不動任何程式碼**。剔除同理。

⚠️ 比對用 substring：`"opus" in model.lower()`，這是現行做法
（`_dispatch_impl.py:46-48` 的 `_has_marker`），為的就是吃得下日期後綴。
代價是字串要夠獨特，別放 `"chat"` 這種會誤命中的詞。

### 5.4 哪些工作派哪一組（這張表要進 `dev-run/SKILL.md`）

| 工作 | 組 | 理由 |
|---|---|---|
| 寫碼、改檔、跑測試、批次替換、機械搜尋 | **實作** | 產出責任，對錯有機械判準（測試綠不綠） |
| T review 判 PASS/FAIL | **思考** | 判斷責任，錯了整條線都髒 |
| 三層皆 FAIL 的診斷（adviser） | **思考** | 要判斷「是規格錯還是執行錯」 |
| G1/G2/G3 gate 裁決 | **思考** | 同上 |
| 派工者本身（主對話） | **思考** | 現況即如此 |

### 5.5 ✅ 已裁決：T review 照 harness 走

`dev-run/SKILL.md:50` 現在寫 T review 用 **fresh sonnet**，但 sonnet 在新分類裡
屬於「實作」組。

**owner 2026-08-19 裁決：照 harness 的規則走 —— reviewer 屬「思考」組，首選 opus。**
成本上升是已知且接受的（harness 的 reviewer 正是 `claude-opus-5`）。

連帶要改：`dev-run/SKILL.md:50` 的「**sonnet**(fresh context)」與 `:82` 的
「同 T 總嘗試上限 4(haiku 1+sonnet 2+opus 1)」要一起重寫成用「組 + 順位」表達，
不再寫死模型名。

### 5.6 連帶要改

- `hooks/_dispatch_impl.py:42-43`：兩個寫死的 tuple 改成讀 `model-tiers.json`；
  讀不到／解析失敗 → **fail-open**。
- **任何文件都不准再列模型名**，一律指向 `model-tiers.json` ——
  否則就是又生一份會漂的清單（第 7 型）。這條要寫進 README §7。
- 鐵律 3 的措辭在帳號層（`~/.claude/rules/ironlaws.md`、
  `doctrine/01-model-dispatch.md` §3），不在本 repo，見待裁決 4。

---

## 6. C〔中〕`dispatch_observed` 對帳：把自陳變成可查核的事實

**必須排在 A 之後。** 沒有具名型別，觀測只能記到「派了一隻不知道是誰的 agent」，
抓不到「實作與審查是不是同一隻」。

### 6.1 改三個地方

| # | 檔案 | 改什麼 | 量 |
|---|---|---|---|
| 1 | `hooks/_dispatch_impl.py` | 每看到一次**真的**發出的派工呼叫，往 ledger 寫一筆 `dispatch_observed`。它現在只讀不寫，要新增寫入路徑 | ~30 行 |
| 2 | `observability/schema/agent-event.schema.json` | 新事件型別入 schema，否則事件驗證會擋掉 | 小 |
| 3 | `hooks/_exec_impl.py` 的 `stop` 分支 | 收尾時比對「自陳的 `agent_dispatched`」vs「觀測到的 `dispatch_observed`」，數量或型別對不上 → 拒絕收尾 | ~50 行 |

### 6.2 ⚠️ schema 有一條會擋路的規則（實查，設計前必讀）

`observability/schema/agent-event.schema.json:10`：

```json
"hook_forbidden_fields": ["agent_role", "prompt", "model"]
```

執行者是 `observability/devflow_obs/event_validate.py:248-254`，
錯誤訊息寫著「hooks 不得**推測** Agent Role / Prompt / model（七節）；
歸屬由 Coordinator 在 derive 時關聯」。

也就是說：**`writer: "hook"` 的事件不准帶 `model` 或 `agent_role` 這兩個欄位名。**
`dispatch_observed` 若照直覺寫 `{"model": "...", "agent_role": "..."}` 會被驗證擋下。

**解法（不必改政策）**：同一支 validator 允許 `x_` 前綴的擴充欄位
（`:240` 註解「擴充欄位:只受隱私掃描約束」、`:242` 錯誤訊息「擴充請用 x_ 前綴」）。
所以用 `x_observed_model` / `x_observed_subagent_type`。

這也**符合原本的立法意旨**：禁的是 hook「推測」，而 `x_observed_*` 記的是
hook 從 `tool_input` **literally 看到的字串**，不是推測。

### 6.3 對帳抓得到什麼

| 情況 | 現在 | 改完 |
|---|---|---|
| 派工者自己寫碼，卻記「派了執行者」 | 沒人管 | 紅：自陳 1、觀測 0 |
| 跳過送審直接補一筆 PASS | 沒人管 | 紅：自陳有 review、觀測無對應派工 |
| 實作與審查是同一次呼叫（沒換 agent） | 沒人管 | 紅：觀測 1 次、自陳 2 次 |
| 派工者偷偷自己修（違反禁親修） | 沒人管 | 部分：重派的觀測筆數會少 |

### 6.4 三個代價（要寫進實作註解）

1. **hook 從「只讀」變成「會寫」**。現行四支 PreToolUse hook 都是純判斷。
   寫入失敗必須 fail-open —— 不能因為記帳失敗就擋住派工。
2. **只在武裝中的 run 記帳**。未武裝（一般聊天、owner 自己隨手派 agent）完全不寫，
   否則污染 ledger，也會讓 hook 在每個專案都動作。
3. **觀測不到「agent 做了什麼」**，只觀測到「派出去了、型別是什麼、用哪個模型」。
   它證明不了那隻 agent 的 context 真的乾淨。

---

## 7. D〔中〕README ↔ guide 的手寫鏡像沒有守衛

`guides/guide-dev-flow.html` 有多段是 `README.md` 的**手寫**改寫
（例：`:1217` 的「規劃層 git」卡片抄自 `README.md:535`）。
`scripts/check-methodology-corrections.sh` 只釘三處（`## 3.` 那張表、
「審查者產生」、「G1/G2/G3 審查與 verdict」），其餘段落改了 README、忘了改 guide，
**不會有任何訊號**。

2026-08-19 實例：改「規劃層 git」那段時是人工比對發現的，機械沒幫上忙。

修法二選一（見待裁決 5）：
- 把需要鏡像的段落逐一加進釘住清單（治標，清單自己會漏）；
- 或改成「guide 不得手寫改寫 README 段落，一律由 renderer 產出」（治本，工程量大）。

> 同型的成功案例可以照抄：2026-08-19 已經把兩份導覽的生命週期圖接到 `hooks.json`
> 這個機械正本上（`scripts/check-hooks-accounting.sh` 的 ④ 節），
> 雙向比對 + 內建負向自檢。D 項要治本的話就是同一個手法。

---

## 8. E〔低〕`history-append.sh` 沒有「改上一筆」的路徑

`docs/dev/HISTORY.md` 規定只能用 `scripts/history-append.sh` 追加、不得手改。
但追加完才發現內容要補時，沒有官方路徑。

2026-08-19 的處置是趁 commit 前 `git checkout -- docs/dev/HISTORY.md` 再重跑一次
append —— **只有在「還沒 commit 且沒有別的 session 同時在寫」時才成立**。

修法：給腳本加 `--amend-last`（取同一把鎖、只重寫最後一個區塊、拒絕在已 commit 的
狀態下動作），或明文寫「追加後發現要改就重跑一次 append 補一筆修正條目」。

---

## 9. 待裁決（全部答完本檔才算派工單）

1. ~~T review 要不要從 sonnet 升到「思考」組~~ → **✅ 2026-08-19 已裁決：照 harness 走，
   reviewer 屬思考組、首選 opus。** 見 §5.5。
2. **`model-tiers.json` 放哪**：repo 根目錄（跟 `devflow-contract.json` 同層）、
   `hooks/`（離消費端最近）、還是 `.claude-plugin/`？
   要不要散發到採用專案的 `docs/dev/tools/`（採用專案能不能自己改分層）？
3. **`agents/*.md` 要不要納入 `check-file-map.sh` 的必列檔**？現值
   `EXPECTED_MAPPED_FILES = 78`，只掃 `hooks/`、`scripts/`、`observability/`、
   `tests/parallel-stage6/` 的 `.sh`/`.py`。納入的話要同步改常數與檔案地圖節，
   還要改 `scripts/test-architecture-guards.sh` 的逐字互釘。
4. **鐵律 3 要不要跟著改措辭**：`~/.claude/rules/ironlaws.md` 與
   `doctrine/01-model-dispatch.md` §3 現在寫「haiku 機械活、sonnet 分析實作、
   opus 只做最終判斷」。改成「兩組 + 組內順位」之後要不要同步？
   （那是帳號層的檔，不在本 repo，動它要另外一輪。）
5. **D 項走治標還是治本。**
6. **版號**：A + B 會改 `dev-run/SKILL.md` 與新增 `agents/`，採用專案
   `dev-setup upgrade` 後相容 → minor（v3.9.0）。C 只動 hooks 內部 → patch。
   合成一版發，還是分兩次？
7. **R4（§3.2）要不要一起做**。不做的話 R2/R3 永遠跑不到，B 等於只改了文件。
   做的話會改變現行 `_dispatch_impl.py` 的放行條件 —— 是行為變更，要配破壞實驗。

---

## 10. 不要做

- **不要在待裁決全部答完之前動手** —— 本檔目前是草案不是派工單。
- **不要讓 hook 去「發起」派工。** Claude Code 的 hook 只有放行／擋下／塞 context
  三種出口，**技術上不能生 agent**。派工只能由主對話發 Task 呼叫。
- **不要把模型名寫進任何文件或程式碼**，一律指向 `model-tiers.json`。
- **不要在 `dispatch_observed` 用 `model` / `agent_role` 欄位名** —— 會被 schema 擋
  （§6.2），用 `x_` 前綴。
- 不要為了讓某個檢查變綠而放寬它。
- 每一支新守衛都要配**破壞實驗**：把它守的東西改壞，確認真的會紅。
  沒有反證的保護等於沒有保護（本 repo 的既有文化，見
  `notes/dispatch-v380-counterproof.md`）。

---

## 11. 本 repo 的落點紀律（執行輪必讀）

- `main` 有全域 hook（`~/.claude/scripts/git-flow-guard.py`，鐵律 9）擋直接 commit。
  每一段收尾都走：**短命 branch → commit → `merge --no-ff` 回 `main`**。
  這條規則本身已經寫進母版（`_templates/STATUS.md` 頂註的「落點」段）。
- `git push origin main` **由 owner 自己跑**，agent 會被擋，那是刻意的護欄。
- `docs/dev/HISTORY.md` 只能用 `scripts/history-append.sh` 追加。
- 收尾驗收至少要跑：
  ```bash
  bash scripts/devflow-check.sh all
  bash hooks/selftest.sh
  env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
  bash hooks/devflow-exec.sh doctor
  bash scripts/test-architecture-guards.sh
  bash scripts/render-methodology-corrections.sh --check
  ```
