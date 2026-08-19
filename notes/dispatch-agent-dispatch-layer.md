# 派工單（草案）：把「派工／執行／審查」從叮嚀變成機制

> **狀態：草案，尚未裁決。** owner 會再往本檔加其他要優化的項目，加完才排執行輪。
> 執行輪不得直接照本檔動手 —— 先看「待裁決」那節，全部有答案了才算派工單。
>
> 觸發句（等本檔定案後才用）：
> `讀 ~/dev/dev-flow/notes/dispatch-agent-dispatch-layer.md 照它跑，全程不打斷問人`

---

## 這份要解決什麼

現在 dev-flow 規定「派工者不寫碼、執行者獨立、reviewer 要乾淨 context」，但**這些規定
全部只是寫給主對話看的散文**（`skills/dev-run/SKILL.md` 的職責表），沒有任何機械強制。

實查（2026-08-19）：

| 事實 | 證據 |
|---|---|
| dev-flow **沒有** `agents/` 目錄，一支具名 subagent 型別都沒有 | `find . -name "*.md" -path "*agents*"` 零命中 |
| 唯一掛在 `Task\|Agent` 的 hook 只管一件窄事：本 run 沒出現過低階模型就直接指名最高階 → 擋 | `hooks/_dispatch_impl.py:3-5`、`:129-157` |
| 執行軌跡（`agent_dispatched` / `review_started` / `review_completed`）全是**派工者自陳**，沒有任何機械觀測在核對 | `hooks/_dispatch_impl.py` 只讀 ledger 不寫；`_exec_impl.py` 的 `stop` 不驗事件序 |
| `gate-consistency` 只驗「README／SKILL／模板都寫了同一套 reviewer 順序」，不驗實際有沒有照做 | `hooks/_gate_consistency_impl.py:223-244` |

**後果**：主對話可以自己寫碼、自己判 PASS、再補三筆流水帳說「我派了執行者、也派了
reviewer」，機械上不會有任何一支守衛紅。

### 對照組：harness-engineering 怎麼做

`/Users/asheng/Documents/stork/Harness/harness-engineering-plugin/plugins/harness-engineering/agents/`

| agent | model | maxTurns | 禁再派 agent |
|---|---|---|---|
| `worker`（寫程式） | `claude-sonnet-5` | 150 | 是（`disallowedTools: Agent`） |
| `reviewer`（唯讀審查） | `claude-opus-5` | 50 | 是 |
| `advisor`（診斷卡關） | `claude-opus-5` | 30 | 是 |
| `scaffolder` | `claude-sonnet-5` | 75 | 是 |
| `coordinator`（派工者，跑主執行緒） | `claude-sonnet-5` | 50 | 否 |

差別只有一句話：**它把角色寫成 Claude Code 原生的具名 subagent 型別，dev-flow 只是在
文件裡拜託主對話這麼做。** 被具名型別叫出來的 agent，context 只有「那個 `.md` 的內容
＋派工者寫的 prompt」，主對話講過什麼一概看不到 —— 這正是「乾淨 agent」的機制來源。

它還把身分綁在工具權限上（worker 只有 Read/Edit/Write/Bash，reviewer 唯讀），
**不是靠叮嚀**。另外有一節專講 context 節省（`lib/skill-base/coordinator-prompt.md:125`）：
subagent 的輸出會回流進派工者 context，連續派幾隻就會撞壓縮，所以要求每個 spawn 的
prompt 結尾都附回報長度約束。

---

## A〔高〕建 `agents/`，把三個角色變成具名 subagent 型別

### 要建的三支

dev-flow 的 `dev-run` 只有三個角色（harness 的 `scaffolder` 在 dev-flow 沒有對應物；
`coordinator` 對應主對話本身，不需要具名型別）：

| 檔案 | 角色 | 對應現況 |
|---|---|---|
| `agents/devflow-executor.md` | 寫碼、跑 Verify、貼 RED/GREEN 原文 | `dev-run/SKILL.md:30` 的「執行者(fresh subagent)」 |
| `agents/devflow-reviewer.md` | 依共用 acceptance seam 判 PASS/FAIL，唯讀 | 同上 `:31` 的「reviewer(fresh sonnet)」 |
| `agents/devflow-adviser.md` | 三層皆 FAIL 時診斷是 T 定義問題還是執行問題，唯讀 | 同上 `:51` 的 adviser |

每支的 frontmatter 至少要有：`name` / `description` / `model` / `maxTurns` /
`allowedTools` / `disallowedTools`。**三支都要 `disallowedTools: [Agent]`** ——
執行者與 reviewer 不得再往下派，否則層級會塌掉（harness 同樣這樣釘）。

`devflow-reviewer` 與 `devflow-adviser` 必須是**唯讀**：禁 Edit/Write，禁
`git commit`／`push`／`reset` 類命令。這是「派工者禁親修」（README §5 驗證五律 2）
第一次有機械後盾。

### 連帶要改

1. `skills/dev-run/SKILL.md`：職責表那幾行從「派 fresh subagent」改成
   「用 `subagent_type: devflow-executor` 派」，明寫型別名。
2. `.claude-plugin/plugin.json`：確認 `agents/` 會被 plugin 載入（沒被載入 = 型別叫不出來）。
3. 記帳面（第 7 型）：`agents/` 是新的一組列舉對象 ——
   `docs/PLUGIN.md` 現在有 hooks 表與 skills 表，要加 agents 表；
   `check-hooks-accounting.sh` 已有「skills 目錄 vs PLUGIN.md」的對帳，照同一個模式加
   「agents 目錄 vs PLUGIN.md」；`check-file-map.sh` 的 `EXPECTED_MAPPED_FILES` 與檔案地圖
   要不要納 `agents/*.md` 一併裁決（見待裁決 3）。

---

## B〔高〕模型分層改成「思考／實作」兩組 + 組內順序（資料檔，不是程式碼）

### 為什麼這個分類是對的

owner 提的兩分法（思考 / 實作）**已經是現況的機械形態**，只是被寫死在程式碼裡：

```python
# hooks/_dispatch_impl.py:42-43
TOP_TIER_MARKERS = ("opus", "fable")      # ← 這就是「思考」
LOW_TIER_MARKERS = ("haiku", "sonnet")    # ← 這就是「實作」
```

而 harness 的做法也是同一個兩分法：worker=sonnet（實作）、reviewer/advisor=opus（思考）。
兩邊各自演化，收斂到同一個切法 —— 這個分類經得起用。

跟鐵律 3（`~/.claude/rules/ironlaws.md`：haiku 機械活、sonnet 分析實作、opus 只做最終
判斷）**沒有衝突**：三個角色收成兩組，組內用順序保留 haiku→sonnet 的先後即可。

### 但兩組不夠，必須加「組內順序」

只有兩組會弄丟一件事：**haiku 優先**。把 haiku 與 sonnet 都丟進「實作」而沒有順序，
派工時可能直接拿 sonnet 去做 grep。所以規則要寫成三句：

1. 一件工作只選**組**（思考 / 實作），不指定某個模型。
2. 組內**由前往後**取，順序 = 由便宜到貴。第一順位就是這組的預設。
3. **升階 = 在組內往後走**；組內走完才跨組。跨到「思考」= 現行的「升 opus」。

這樣既保留現行升階紀律（haiku 錯 1 次 → sonnet；sonnet 錯 2 次 → opus），
又讓「換模型」變成改一個清單。

### 資料檔長什麼樣

新增 `model-tiers.json`（位置見待裁決 2），內容是**比對字串**不是完整模型 id ——
完整 id 會帶日期後綴（`claude-opus-5-20260601`），寫死會漂：

```jsonc
{
  "schema": 1,
  "tiers": {
    "build": ["haiku", "sonnet"],     // 實作:寫碼、跑測試、機械活。由便宜到貴
    "think": ["opus", "fable"]        // 思考:審查、裁決、診斷。由便宜到貴
  }
}
```

加 deepseek 就是往清單裡插字串（例：`build` 加 `"deepseek-chat"`、
`think` 加 `"deepseek-reasoner"`），**不動任何程式碼**。剔除同理。

### 哪些工作派哪一組（這張表要進 `dev-run/SKILL.md`）

| 工作 | 組 | 理由 |
|---|---|---|
| 寫碼、改檔、跑測試、批次替換、機械搜尋 | **實作** | 產出責任，對錯有機械判準（測試綠不綠） |
| T review 判 PASS/FAIL | **思考** | 判斷責任，錯了整條線都髒 |
| 三層皆 FAIL 的診斷（adviser） | **思考** | 要判斷「是規格錯還是執行錯」 |
| G1/G2/G3 gate 裁決 | **思考** | 同上 |
| 派工者本身（主對話） | **思考** | 現況即如此 |

⚠️ **這張表會改變現行行為**：`dev-run/SKILL.md:50` 現在寫 T review 用
**fresh sonnet**，但 sonnet 在新分類裡屬於「實作」。照新規則 review 一律走「思考」組
（首選 opus）。這是成本上升，但 harness 的 reviewer 正是 `claude-opus-5` —— 有前例。
要不要接受見待裁決 1。

### 連帶要改

- `hooks/_dispatch_impl.py:42-43`：兩個寫死的 tuple 改成讀 `model-tiers.json`；
  讀不到 / 解析失敗 → **fail-open**（維持現行行為，守衛不得因為自己讀不到設定就擋人派工）。
- 鐵律 3 的措辭：`~/.claude/rules/ironlaws.md` 與 `doctrine/01-model-dispatch.md` §3
  是**帳號層**的檔，不在本 repo。dev-flow 這邊改完之後，要不要回頭把那兩處也改成
  「兩組 + 組內順序」的講法，見待裁決 4。
- 記帳（第 7 型）：`model-tiers.json` 一旦有人另外抄一份清單到文件裡，就要有守衛對帳。
  最省事的做法是**任何文件都不准再列模型名**，一律指向這個檔。

---

## C〔中〕`dispatch_observed` 對帳：把自陳變成可查核的事實

**必須排在 A 之後。** 沒有具名型別，觀測只能記到「派了一隻不知道是誰的 agent」，
抓不到「實作與審查是不是同一隻」，價值大打折扣。

### 改三個地方

| # | 檔案 | 改什麼 | 量 |
|---|---|---|---|
| 1 | `hooks/_dispatch_impl.py` | 每看到一次**真的**發出的派工呼叫，往 ledger 寫一筆 `dispatch_observed`（帶 `subagent_type` 與 `model`）。它現在只讀不寫，要新增寫入路徑 | ~30 行 |
| 2 | `observability/schema/agent-event.schema.json` | 新事件型別入 schema，否則事件驗證會擋掉 | 小 |
| 3 | `hooks/_exec_impl.py` 的 `stop` | 收尾時比對「自陳的 `agent_dispatched`」vs「觀測到的 `dispatch_observed`」，數量或型別對不上 → 拒絕收尾 | ~50 行 |

### 對帳抓得到什麼

| 情況 | 現在 | 改完 |
|---|---|---|
| 主對話自己寫碼，卻記「派了執行者」 | 沒人管 | 紅：自陳 1、觀測 0 |
| 跳過送審直接補一筆 PASS | 沒人管 | 紅：自陳有 review、觀測無對應派工 |
| 實作與審查是同一次呼叫（沒換 agent） | 沒人管 | 紅：觀測 1 次、自陳 2 次 |
| 派工者偷偷自己修（違反禁親修） | 沒人管 | 部分：重派的觀測筆數會少 |

### 三個代價（要寫進實作註解）

1. **hook 從「只讀」變成「會寫」**。現行四支 PreToolUse hook 都是純判斷。寫入失敗必須
   fail-open —— 不能因為記帳失敗就擋住派工。
2. **只在武裝中的 run 記帳**。未武裝（一般聊天、owner 自己隨手派 agent）完全不寫，
   否則會污染 ledger，也會讓 hook 在每個專案都動作。
3. **觀測不到「agent 做了什麼」**，只觀測到「派出去了、型別是什麼、用哪個模型」。
   它證明不了那隻 agent 的 context 真的乾淨。

---

## D〔中〕README ↔ guide 的手寫鏡像沒有守衛

`guides/guide-dev-flow.html` 有多段是 `README.md` 的**手寫**改寫（例：`:1217` 的
「規劃層 git」卡片抄自 `README.md:535`）。`check-methodology-corrections.sh` 只釘三處
（`## 3.` 那張表、「審查者產生」、「G1/G2/G3 審查與 verdict」），其餘段落改了 README、
忘了改 guide，**不會有任何訊號**。

2026-08-19 的實例：改「規劃層 git」那段時是人工比對發現的，機械沒幫上忙。

修法二選一（見待裁決 5）：
- 把需要鏡像的段落逐一加進 `check-methodology-corrections.sh` 的釘住清單（治標，清單會漏）；
- 或改成「guide 不得手寫改寫 README 段落，一律由 renderer 產出」（治本，工程量大）。

---

## E〔低〕`history-append.sh` 沒有「改上一筆」的路徑

`docs/dev/HISTORY.md` 規定只能用 `scripts/history-append.sh` 追加、不得手改。但追加完
才發現內容要補時，沒有官方路徑。2026-08-19 的處置是趁 commit 前
`git checkout -- docs/dev/HISTORY.md` 再重跑一次 append —— **只有在「還沒 commit 且沒有
別的 session 同時在寫」時才成立**。

修法：給腳本加 `--amend-last`（取同一把鎖、只重寫最後一個區塊、拒絕在已 commit 的
狀態下動作），或明文寫「追加後發現要改就重跑一次 append 補一筆修正條目」。

---

## 待裁決（owner 回答之後本檔才算派工單）

1. **T review 從 sonnet 升到「思考」組（首選 opus）**，成本上升 —— 接受嗎？
   還是「實作」組保留 sonnet 給 review 用（等於承認 review 是實作）？
2. **`model-tiers.json` 放哪**：repo 根目錄（跟 `devflow-contract.json` 同層）、
   `hooks/`（離消費端最近）、還是 `.claude-plugin/`？
   要不要散發到採用專案的 `docs/dev/tools/`（採用專案要不要能自己改分層）？
3. **`agents/*.md` 要不要納入 `check-file-map.sh` 的必列檔**（現值
   `EXPECTED_MAPPED_FILES = 78`，只掃 `hooks/`、`scripts/`、`observability/`、
   `tests/parallel-stage6/` 的 `.sh`/`.py`）？納入的話要同步改常數與檔案地圖節。
4. **鐵律 3 要不要跟著改**：`~/.claude/rules/ironlaws.md` 與
   `doctrine/01-model-dispatch.md` §3 現在寫「haiku 機械活、sonnet 分析實作、opus 只做
   最終判斷」。改成「兩組 + 組內順序」之後，帳號層那兩處要不要同步改措辭？
   （那是帳號層的檔，不在本 repo，動它要另外一輪。）
5. **D 項走治標還是治本。**
6. **要不要 bump 版號**：A + B 會改 `dev-run/SKILL.md` 與新增 `agents/`，
   採用專案 `dev-setup upgrade` 後相容 → minor（v3.9.0）。C 只動 hooks 內部 → patch。
   要合成一版發還是分兩次？

---

## 不要做

- 不要在 owner 回答「待裁決」之前動手 —— 本檔目前是草案不是派工單。
- 不要讓 hook 去「發起」派工。Claude Code 的 hook 只有放行／擋下／塞 context 三種出口，
  **技術上不能生 agent**。派工只能由主對話發 Task 呼叫。
- 不要把模型名寫進任何文件或程式碼 —— 一律指向 `model-tiers.json`。
- 不要為了讓某個檢查變綠而放寬它。

## 已知的落點紀律（本 repo）

`main` 有全域 hook（`~/.claude/scripts/git-flow-guard.py`，鐵律 9）擋直接 commit，
所以每一段收尾都走：短命 branch → commit → `merge --no-ff` 回 `main`。
`git push origin main` 由 owner 自己跑（agent 會被擋，那是刻意的護欄）。
