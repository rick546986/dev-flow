# 派工單（草案 v3）：把「派工／執行／審查」從叮嚀變成機制

> **狀態：v4 —— 三隻 opus reviewer 審查 + 主線程裁決 + owner 已答完十題。
> 這份現在是可以執行的派工單，但只執行「第一輪」（見 §13）。**
>
> **執行輪只做 §13 的第一輪：§7 前置修復 + §4 A′ + §6.1 一行地板。**
> §5（B）與 §6.2（C′ 判準）留給第二輪，不要在本輪動 —— 它們會反轉八條既有測試，
> 混在同一輪風險太集中。
>
> **v3 相對 v2 變化很大**：三隻審查各自帶回阻斷級發現，原設計的 R1／R2 已**撤回**，
> A 從三支具名型別縮成兩支，C 從「hook 寫 ledger」降級成「補強既有的事後稽核」。
> 逐條處置見 §3 裁決表。v2 原案留在 git 歷史（`b32907c`），本檔不重述。
>
> 定案後的觸發句：
> `讀 ~/dev/dev-flow/notes/dispatch-agent-dispatch-layer.md 照它跑，全程不打斷問人`
>
> **本檔寫給沒有前情的 session 看**：結論都附 `檔:行`。標「實查」= 有人實際打開檔案
> 看過；標「未驗證」= 還沒有證據，不得當事實用。

---

## 0. 名詞對照（先讀這節）

| 本檔用詞 | 指的是什麼 |
|---|---|
| **派工者** | 主對話本身。讀規格、派人、收驗、commit、記帳。不寫碼 |
| **執行者 / worker** | 被派出去寫程式的 subagent |
| **reviewer** | 被派出去判 PASS/FAIL 的 subagent，唯讀 |
| **adviser** | 三層都失敗時診斷「是規格錯還是執行錯」的 subagent，唯讀 |
| **具名型別** | Claude Code 原生機制：`agents/<name>.md` 定義一種 subagent，派工時用 `subagent_type` 叫它。被叫出來的 agent 只看得到那個 `.md` + 你寫的 prompt，主對話講過什麼一概看不到 |
| **ledger／執行軌跡** | `.devflow/` 底下的事件流水帳 |
| **自陳 vs 觀測** | 自陳＝派工者自己寫進 ledger；觀測＝hook 攔到真實工具呼叫後記下的 |
| **武裝中** | `.devflow/exec.json` 存在。⚠️ 但「守衛認不認得它」另有條件，見 §2.1 |

### 角色詞彙已經有兩本正本，**不要造第三本**

| 正本 | 值 |
|---|---|
| `observability/schema/agent-event.schema.json:32` | `agent_role` enum = `["worker", "reviewer", "adviser", "verifier"]` |
| `hooks/prompt-registry.json:3,24,45` | `stage6-adviser` / `stage6-reviewer` / `stage6-worker` |

v2 曾提議把執行者命名為 `devflow-executor` —— **撤回**，一律沿用 `worker`。
理由：`scripts/check-model-tiering.sh:140` 靠 `agent_role != "worker"` 過濾，
誰日後為了對齊改成 executor，那支守衛的兩條紅線會**靜默死掉**（worker 事件變空 →
零違規 → PASS）。這是第 7 型（不對稱記帳）的教科書復發形態。

---

## 1. 現況：規定只在文件裡，但**不是完全沒有機械面**

### 1.1 實查（2026-08-19）

| 事實 | 證據 |
|---|---|
| dev-flow **沒有** `agents/` 目錄 | `ls agents` → No such file |
| 職責分工只存在於散文 | `skills/dev-run/SKILL.md:30-33` |
| 唯一掛在 `Task\|Agent` 的 hook 自稱「窄版」 | `hooks/_dispatch_impl.py:3` |
| `gate-consistency` 只做文字 token 比對，不驗實際執行 | `hooks/_gate_consistency_impl.py:223-254` |
| ledger 的 `agent_dispatched` / `attempt_started` 是**派工者自陳**；`stop` 不驗事件序 | `_exec_impl.py:421-442` |

### 1.2 ⚠️ v2 說「機械上不會有任何一支守衛紅」—— **這句是錯的，已修正**

`scripts/check-model-tiering.sh`（18KB，2026-08-17）**已經在做事後稽核**：從 ledger 掃
`agent_role == "worker"` 的 `attempt_started`，釘兩條紅線（首派最高階、跳級），
檔頭 `:11` 誠實寫明稽核邊界。

**所以缺的不是「零守衛」，是「守衛看不到的地方太多」。** 這改變整份提案的定位：
從「無中生有蓋一套」變成「補完既有機制的洞」。

⚠️ 它內含**第二份寫死的分層表**：`check-model-tiering.sh:89-100` 的 `tier_of()`，
三層（HAIKU / SONNET / TOP）。§5 的資料檔化必須同時改這裡，只改
`_dispatch_impl.py` 就是又留一份會漂的副本。

### 1.3 對照組：harness-engineering

路徑 `/Users/asheng/Documents/stork/Harness/harness-engineering-plugin/plugins/harness-engineering/`

⚠️ **`agents/*.md` 那張表是歷史參考檔，不是 live dispatch 契約**
（`agents/README.md:137`、`team-composition.md:19-22` 明寫「可用工具欄位是 derived
view，非真值」；`worker.md` 自列為「不可 dispatch 的 runtime target」）。
照那張表推論設計＝照廢契約設計。真正的契約在
`lib/contracts/subagent-frontmatter-rules.md`，見 §2.2。

---

## 2. 三個阻斷級事實（審查帶回來的，動工前必讀）

### 2.1 🔴 守衛在**最常見的 sequential 模式**整支失效

`_dispatch_impl.py:140-141`：`state.get("schema") not in EXEC_SCHEMAS` → 放行。
`EXEC_SCHEMAS = ("exec-v2", "exec-v3")`（`:37`）。

實查四條武裝路徑，**只有一條寫 `schema`**：

| 路徑 | 寫出的 exec.json | 有 schema？ |
|---|---|---|
| `start <slug> --task T-n`（parallel） | `_exec_impl.py:389-400` | ✅ `exec-v3` + `run_id` |
| legacy sequential start | `:323-328` | ❌ 無 |
| VNext feature-scope start | `:352-359` | ❌ 無 |
| Stage 7 `review` 自建 | `:977-983` | ❌ 無 |

**後果**：sequential（預設、最常用的那條路）全程不設防。而且 exec-v3 那份住在 task
worktree，派工者坐在 integration／主樹，hook 的 `ROOT` 取 session cwd —— parallel 的
派工者也讀不到。

**這件事比整份提案都優先**：不修它，A／B／C 全部落地即 no-op，犯的正是本提案在指責
的那個病。修法見 §7。

### 2.2 🔴 plugin 出貨的 subagent **拿不到 Bash**

`harness .../lib/contracts/subagent-frontmatter-rules.md:7-13`、實測表 `:19-26`：

| subagent 型別 | frontmatter 宣告 | 實測 Bash | 實測 Agent |
|---|---|---|---|
| plugin 出貨的 worker/reviewer/advisor | `Bash(pattern)` 22 條 | ❌ tool not available | ❌ ABSENT |
| 同上 | **裸 `Bash`** | ❌ ABSENT | ❌ ABSENT |
| `general-purpose`（第一方） | `*` | ✅ 全 SUCCESS | ❌ ABSENT |
| `claude-code-guide`（內建） | 裸 `Bash` | ✅ | — |

三條衍生規則（同檔 Rule 1–4）：

1. **兩種寫法都無效**。v2 寫「只有裸 Bash 有效」是引到 `worker.md:9-13` 那則已被同
   repo 契約檔推翻的舊註解 —— 已更正。
2. **`Agent` 工具對所有 subagent 全域 block**，寫不寫 `disallowedTools: [Agent]` 一樣。
   v2 說「不寫層級會塌掉」是空頭支票 —— 已更正為「doc signal」。
3. **`disallowedTools` 裡的 `Bash(pattern)` 不 enforce**，真正的 deny 在
   `.claude/settings.json` 的 `permissions.deny`。任何安全保證都要假設那些條目 inert。

**這對 executor 是壞消息，對 reviewer／adviser 是好消息** —— 本輪最關鍵的裁決依據：

- executor 要跑測試 → 需要 Bash → **只能用 `general-purpose`**，不能是具名型別。
- reviewer／adviser 本來就該唯讀 → **plugin 具名型別天生沒有 Bash，正好就是真唯讀**，
  而且是平台層強制，比任何 prompt 叮嚀都硬。

⚠️ **probe 日期是 2026-05-19，今天 08-19，平台行為可能已變。**
契約檔 `:28` 自附複現法。執行輪的**第 0 步**就是重跑（§7-3）。

### 2.3 🟠 `_scan_low_tier_attempt()` 只看「起過」不看「失敗過」

`_dispatch_impl.py:69-73`：掃到任何一筆 `attempt_started` 且 model 含 haiku/sonnet
就 `return True` → 放行。

v2 說它「讓整個 run 不設防」—— **範圍描述不精確**：`run_id` 只在 `--task` 分支生成
（`_exec_impl.py:389`），一個 run 目錄實際上只裝一個 T 的 attempts。

真正的缺陷是**判準**：一筆**成功**的 haiku attempt 也會永久放行後續的 opus。
升階的前提應該是「前一順位**失敗**過」，不是「前一順位起過」。修法見 §6.2。

---

## 3. 裁決表（主線程對三隻審查的逐條處置）

| v2 的提案 | 裁決 | 理由（附證據） |
|---|---|---|
| A：建 executor / reviewer / adviser **三支**具名型別 | **部分採納 → 只建 reviewer / adviser 兩支** | §2.2：executor 需要 Bash，具名型別拿不到 |
| §3.1「model 寫進 frontmatter，不帶 model 就天然是第一順位」 | **撤回** | `general-purpose` 無定義 model → 依工具契約繼承母層（主對話＝opus）→「什麼都不做」拿到的是**思考組**，跟意圖相反。harness v6.5 也已放棄 frontmatter model pin（`subagent-frontmatter-rules.md:55-59`） |
| **R1**「武裝中必須帶 `subagent_type` ∈ 白名單，否則擋」 | **撤回** | ①executor 只能是 `general-purpose`，白名單擋掉唯一可行解 ②會擋掉武裝中一切無關派工（`/code-review`、Explore、查資料），直接推翻 `_dispatch_impl.py:9-12` 的明文承諾「非 dev-flow 用途的一般 Task/Agent 呼叫必須不受影響」 ③fail-closed 押在未證實的欄位名（`subagent_type` vs `agent_type`，plugin 型別還可能帶命名空間），欄位一改名武裝中每一次派工都被擋 |
| **R2**「model 必須落在該型別對應的組」 | **撤回** | 死鎖：executor ↦ 實作組 `{haiku, sonnet}`，但 `README.md:394` 與 `dev-run/SKILL.md:89` 都釘死「同 T 上限 4 = haiku 1 + sonnet 2 + **opus 1**」。第 4 次嘗試會被 R2 擋掉，而五律 5 又要求用滿 4 次才准問 adviser → 該 T 永久卡死 |
| **R3**「跳順位須有前一順位失敗紀錄」 | **改成事後稽核** | 它讀的是自陳 ledger，補一筆假 FAIL 就繞過。`_dispatch_impl.py:14-18` 已明文界定信任邊界「防手滑與紀律漂移，**不防蓄意偽造**」。作為攔阻規則不成立，作為稽核判準正確 → 併進 §6.2 |
| **R4**「收窄 run 級早退」 | **採納但理由重寫** | 原理由（run vs T 範圍）是修一個不存在的缺陷（§2.3）。該改的是判準：從「起過」改成「失敗過」 |
| **C**：hook 寫 `dispatch_observed` 進 ledger | **降級** | ①sequential 無 `run_id`，而 envelope `required` 含 `run_id` → hook 產不出合法事件 ②`_obs_impl.py:294` 按 `attempt_id` 路由落盤，PreToolUse 不知道 attempt_id ③schema 政策禁的正是 hook 做歸屬推測，`x_` 前綴只解決欄位名沒解決歸屬 ④§6.3 那張表用「防偽造」語氣賣它，超出既有信任邊界 |
| C 的 `stop` 對帳不符就「拒絕收尾」 | **撤回** | `stop` 是三處文件指定的唯一復原動作（`_exec_impl.py:449,473`、`README.md:294`）。一次 hook 寫入失敗（唯讀 FS、換 worktree、關掉 plugin）就永久造成計數不符 → stop 拒絕 → exec.json 留著 → devflow-guard 繼續武裝 → 想手動清又被 `_prebash_impl.py:65` 擋掉 `rm .devflow/` → **變磚** |
| B：分層改資料檔 + 組內順序 | **採納，但消費端是兩處不是一處** | v2 只點名 `_dispatch_impl.py:42-43`，漏掉 `check-model-tiering.sh:89-100` 的第二份 `tier_of()` |
| §5.5 T review 一律升思考組 | **保留 owner 裁決，但要補說明** | 成本實算 **1.67x**（opus/sonnet 輸出單價 25/15），只作用在 review 段，不是「幾倍」。但 `dev-run/SKILL.md:50` **本來就有風險分級**（「高風險或爭議時由 opus 作第二 reviewer」）→ 依 `README.md:299-304`（不對稱保護）必須說明「原本的分級為什麼不夠」，否則是無理由的擴大 |

---

## 4. A′〔高〕只建兩支具名型別：reviewer / adviser

### 4.1 為什麼是兩支不是三支

見 §2.2。executor 需要 Bash → 只能 `general-purpose` + prompt 帶 role 規範
（harness v6.5 的做法：prompt 內指示去讀 role 檔取規範）。

### 4.2 這兩支買到什麼（整份提案唯一買得到、事後稽核買不到的東西）

**工具權限**。reviewer／adviser 用 `allowedTools: [Read]`，**完全不給 Bash / Edit /
Write**。這是「派工者禁親修」（`README.md` §5 驗證五律 2）第一次有平台層後盾 ——
不是叮嚀，是它根本沒有那個工具。

⚠️ 對應改法：reviewer 需要的 `git diff` 由**派工者先跑好、當成 prompt 內容餵進去**
（harness `reviewer.md:50` 就是這樣）。

⚠️ 降級代價要寫進文件：`allowedTools` 白名單會同時失去 Grep / Glob / Skill 與採用專案
的 MCP 工具。reviewer 只能看派工者餵的材料 —— 這正好符合「不給執行者結論、只看產物」
的既有規定（`dev-run/SKILL.md:77`），但要明講。

### 4.3 命名

`agents/devflow-reviewer.md`、`agents/devflow-adviser.md`。
**role 值一律沿用 `reviewer` / `adviser`**（§0 的兩本正本），不要用新詞。

### 4.4 連帶要改（比 v2 多兩處）

1. `skills/dev-run/SKILL.md:77`：reviewer 改成用 `subagent_type` 派，明寫型別名。
2. `.claude-plugin/plugin.json`：確認 `agents/` 被 plugin 載入。**要實測**：
   安裝後在別的專案叫得出來才算數；並且**記下實際型別字串長什麼樣**（帶不帶
   `dev-flow:` 命名空間）—— 這決定未來任何以型別為判準的檢查寫不寫得對。
3. `docs/PLUGIN.md:47-53`：那是**一張** `| 目錄 | 用途 |` 表，hooks 與 skills 各佔一列
   （`:49`、`:50`）。加 agents 是**加第三列**，不是加一張表。
4. `scripts/check-hooks-accounting.sh:131-135`：已有「skills 目錄 vs PLUGIN.md」對帳，
   照同一模式加 agents。
5. `scripts/check-file-map.sh`：`PATTERNS`（`:58-63`）目前**完全不含 `.md`**，
   `agents/*.md` 要納入必列檔得先加 pattern。現值 `EXPECTED_MAPPED_FILES = 80`
   （`:107`，實跑 `scanned=80`），並被 `test-architecture-guards.sh:1542` 逐字釘。
   **裁決 3：納入。** 先加 `.md` pattern，再同步常數與逐字釘。

---

## 5. B〔高〕分層改成「思考／實作」兩組 + 組內順序

### 5.1 分類本身是對的（不是新發明）

現況已經是兩分法，只是寫死在程式碼裡：

```python
# hooks/_dispatch_impl.py:42-43
TOP_TIER_MARKERS = ("opus", "fable")      # ← 思考
LOW_TIER_MARKERS = ("haiku", "sonnet")    # ← 實作
```

harness 獨立演化出同一個切法（worker=sonnet、reviewer/advisor=opus）。
跟鐵律 3 不衝突：三個角色收成兩組，組內用順序保留 haiku→sonnet 的先後。

### 5.2 規則三句

1. 一件工作只選**組**，不指定某個模型。
2. 組內**由前往後**取，順序 = 由便宜到貴；第一順位是預設。
3. **升階 = 組內往後走**；組內走完才跨組。跨到「思考」= 現行的「升 opus」。

### 5.3 資料檔

`model-tiers.json`（**裁決 2：放 repo 根目錄，跟 `devflow-contract.json` 同層；
先不散發到採用專案**）。存**比對字串**不是完整 id
（完整 id 帶日期後綴會漂；現行 `_has_marker` 就是 substring 比對）：

```jsonc
{
  "schema": 1,
  "tiers": {
    "build": ["haiku", "sonnet"],     // 實作。由便宜到貴
    "think": ["opus", "fable"]        // 思考。由便宜到貴
  }
}
```

加 deepseek 就是插字串，不動程式碼。
⚠️ 字串要夠獨特，別放 `"chat"` 這種會誤命中的詞。
⚠️ 「思考組 opus 排在 fable 前面＝由便宜到貴」目前**未驗證**，定案前查一次實際價位。

### 5.4 兩個消費端都要改（v2 只寫了一個）

| 檔案 | 現在寫死什麼 |
|---|---|
| `hooks/_dispatch_impl.py:42-43` | 兩層 marker tuple |
| `scripts/check-model-tiering.sh:89-100` | `tier_of()`，**三層**（HAIKU/SONNET/TOP） |

兩處都改成讀 `model-tiers.json`；讀不到／解析失敗 → **fail-open**（維持現行行為）。
⚠️ `tier_of()` 是三層，它的兩條紅線依賴三層區分（跳級＝haiku 直接跳 TOP）。
改成「兩組＋組內順位」之後，「跳級」的定義要改寫成「跳過組內前面的順位」，
這是行為變更，要配破壞實驗。

### 5.5 哪些工作派哪一組

| 工作 | 組 |
|---|---|
| 寫碼、改檔、跑測試、批次替換、機械搜尋 | 實作 |
| T review 判 PASS/FAIL | 思考（owner 已裁決，見下） |
| adviser 診斷、G1/G2/G3 裁決、派工者本身 | 思考 |

**owner 2026-08-19 裁決：T review 照 harness 走，屬思考組、首選 opus。**

⚠️ 落地前要補一段說明：`dev-run/SKILL.md:50` 現行是**風險分級**（「高風險或爭議時由
opus 作第二 reviewer」），改成一律升級是擴大保護範圍，`README.md:299-304`
（不對稱保護那條制度要求）要求同一個 commit 說明「原本的分級為什麼不夠」。
成本實算 1.67x（只作用在 review 段）。

連帶要改的**兩份**（v2 只寫一份）：`skills/dev-run/SKILL.md:50` 與 `:88-89`，
以及 **`README.md:394`** ——「同 T 總嘗試上限 = 4(haiku 1 + sonnet 2 + opus 1)」
這句**兩個檔都有**。

### 5.6 ⚠️「任何文件都不准再列模型名」這條先不要寫進 README

v2 提過這條。實查發現 `README.md:394`、`:713`、`:729-740`、`:735-736`、`:739`、`:757`
是**完整的七階段 × 模型對照表**，`guides/guide-dev-flow.html` 的模型名還是
**CSS token**（`:10-21`、`:44-46`、`:94-105` 的 `--opus/--sonnet/--haiku`）與
**SVG 節點文字**（`:174-178`），`check-methodology-corrections.sh:234` 另有負向禁字
`"fresh-contextrevieweragent(opus"`。

一條「不准列模型名」會**當場讓一堆既有內容違規**。改成：
「**新增**的機械判準不得寫死模型名，一律讀 `model-tiers.json`；既有敘述性文件不受限」。

---

## 6. C′〔中〕不寫新事件，改為補強既有的事後稽核

v2 的 `dispatch_observed` 撤回（理由見 §3）。改成三件小事，加起來抓到的東西差不多，
但零新增擋人規則、零 schema 變更、零復原路徑風險。

### 6.1 `check-model-tiering.sh` 真實模式補一行地板

它的自測模式已有同型地板，**真實模式沒有**：`worker-tasks == 0` 時只印數字不斷言 →
ledger 是空的也會 PASS。補 `worker-tasks == 0 → exit 2`（比照
`check-integration-regression-guard.sh` 的 `MIN_CHECKS` 慣例）。

### 6.2 修 `_scan_low_tier_attempt()` 的判準

`_dispatch_impl.py:69-73`：從「掃到 `attempt_started` 就放行」改成
「前一順位要有**失敗**事件（`attempt_completed` 且帶 `result`/`failure_category`）」。

⚠️ 這是行為變更，會反轉既有 pinned 測試，見 §6.4。

### 6.3 誠實寫明信任邊界

任何新文件都不得暗示這套防得住蓄意偽造。`_dispatch_impl.py:14-18` 已寫死
「防手滑與紀律漂移，不防蓄意偽造」，新增內容沿用同一句，不得升級措辭。

### 6.4 ⚠️ 會撞到的既有測試（v2 完全沒提測試檔）

| 位置 | 內容 | 會怎樣 |
|---|---|---|
| `hooks/selftest.sh:2006-2057` | dispatch-guard 的 PX 群組八條斷言，payload 是 `{"tool_name":"Agent","tool_input":{"model":"opus"}}`（**無 subagent_type**） | `:2022`「px 已有 haiku attempt → 首派 opus 視為合法升階，放行」正是 §6.2 要改的行為 → 會紅 |
| `hooks/selftest.sh` F4（`:2061-2069`） | 釘豁免卡 fail-open | 動豁免邏輯就會咬 |
| `test-architecture-guards.sh:1536` | `MIN_CASES = 378` 靜態釘 | 增刪 selftest 案例要同步 |

---

## 7. 前置修復〔阻斷〕：先讓守衛看得到 sequential

**這節排在 A′／B／C′ 之前。** 不修，後面全部是 no-op。

1. `_exec_impl.py:323-328`、`:352-359`、`:977-983` 三處寫 exec.json 的路徑補上
   `schema` 欄（**裁決 8：開新代號 `exec-v4`**，不沿用 `exec-v2` —— sequential 與
   parallel 的欄位本來就不同，沿用會讓「認得的 schema」跟「實際欄位」脫鉤）。
   ⚠️ 加了之後 `_dispatch_impl.py` 就會開始在 sequential 生效 —— 那正是目的，
   但它是**行為變更**，要先確認現行守衛在 sequential 下不會誤擋。
2. sequential 要不要也生 `run_id`：不生的話 §6.1 的稽核在 sequential 永遠無資料
   （`dev-run/SKILL.md:55-58` 誠實寫著 sequential 事件步 N/A）。**裁決 9：要生。**
3. **平台探針 —— 記錄用，不阻斷本輪**（R1 撤回之後，這兩件事都不再是前提）：
   - 3a. plugin 出貨的 subagent 現在拿不拿得到 Bash（§2.2 的 probe 已三個月，
     契約檔 `:28` 附複現法）。
     ⚠️ **A′ 不依賴這個結果**：探針說「還是拿不到」→ reviewer／adviser 天生唯讀，
     正合需求；說「現在拿得到了」→ 那就在 `allowedTools` 明確**不給** Bash，
     結果一樣。所以 A′ 可以先做，探針只是把事實記下來。
   - 3b. PreToolUse 的 `tool_input` 有沒有 `subagent_type` 欄位、欄位名是什麼、
     plugin 型別帶不帶命名空間。實查：repo 內**零 fixture**，唯二 payload 樣本
     （`selftest.sh:1979`、`:2055`）都只有 `model`。
     R1 撤回後本輪用不到，但第二輪若要做任何以型別為判準的檢查就會需要 → **順手測、
     測完寫成 selftest fixture 留檔**，不要只寫在回報裡。

---

## 8. D〔中〕README ↔ guide 的手寫鏡像沒有守衛

`guides/guide-dev-flow.html:1223` 的「規劃層 git」卡片是 `README.md:537-541` 的**手寫**
改寫（v2 兩個行號都指錯，已更正）。`check-methodology-corrections.sh:171-198` 的 parity
dict 共 15 條，其中 README 來源是**四**種（`:173` `## 3.` 表、`:191/:194` 審查者產生、
`:196` G1/G2/G3、`:192` fenced seam），其餘段落改了 README、忘了改 guide **不會有訊號**。

**裁決 6：治標** —— 逐段加進 `check-methodology-corrections.sh` 的釘住清單。
治本（改成 renderer 產出）工程量不成比例。**屬第二輪，本輪不做。**

> 同型的成功案例可照抄：2026-08-19 已把兩份導覽的生命週期圖接到 `hooks.json`
> 機械正本（`check-hooks-accounting.sh` ④ 節），雙向 + 內建負向自檢。

---

## 9. E〔低〕`history-append.sh` 沒有 `--amend-last`

追加完才發現要補時沒有官方路徑。2026-08-19 的處置是趁 commit 前
`git checkout -- docs/dev/HISTORY.md` 再重跑 append —— 只在「還沒 commit 且沒有別的
session 同時在寫」時成立。

---

## 10. 裁決結果（owner 2026-08-19 全部答完，這節只留紀錄）

| # | 題目 | 裁決 |
|---|---|---|
| 1 | T review 升思考組 | ✅ 照 harness 走，屬思考組首選 opus。**但要在同一個 commit 補一段「原本的風險分級為什麼不夠」** —— `dev-run/SKILL.md:50` 現行是「高風險或爭議時由 opus 作第二 reviewer」，改成一律升級是擴大保護，`README.md:299-304` 要求說明 |
| 2 | `model-tiers.json` 放哪、要不要散發 | **放 repo 根目錄**（跟 `devflow-contract.json` 同層）；**先不散發**到採用專案 —— 讓採用專案能自己改分層等於多一份會漂的副本 |
| 3 | `agents/*.md` 納不納入檔案地圖必列檔 | **納入**（不納入的話新增 agent 沒人記帳）。要先在 `check-file-map.sh:58-63` 的 `PATTERNS` 加 `.md`，並同步 `EXPECTED_MAPPED_FILES` 與 `test-architecture-guards.sh:1542` 的逐字釘 |
| 4 | 鐵律 3 要不要跟著改措辭 | **本輪不動**。那是帳號層檔案（`~/.claude/rules/ironlaws.md`、`doctrine/01-model-dispatch.md`），要另外一輪 |
| 5 | 要不要接受 A′-only | **接受，但加做 §7**。第一輪 = §7 前置修復 + A′ + §6.1；B／C′／D 留第二輪。詳見 §13 |
| 6 | D 治標還治本 | **治標** —— 逐段加進 `check-methodology-corrections.sh` 的釘住清單。治本（改成 renderer 產出）工程量不成比例。**第二輪做** |
| 7 | `tier_of()` 三層改兩層 | **要做，但屬於 B** → 第二輪。不能只改 `_dispatch_impl.py` 那一份，兩份要同一個 commit 一起改 |
| 8 | 新的 exec schema 代號 | **開 `exec-v4`**。sequential 與 parallel 的 exec.json 欄位本來就不同，沿用 `exec-v2` 會讓「認得的 schema」與「實際欄位」脫鉤 |
| 9 | sequential 要不要生 `run_id` | **要**。不生的話 §6.1 的事後稽核在 sequential 永遠空手，等於白做 |
| 10 | 版號拆幾版 | **拆兩版**：§7 單獨發（行為變更 —— 守衛開始在最常用的那條路生效），A′ + §6.1 再一版 |

### 本輪執行時仍要當場判斷的事（不是待裁決，是實作細節）

- `exec-v4` 要不要沿用 `EXEC_SCHEMAS` 這個 tuple，還是分「認得的」與「會擋的」兩張表。
- sequential 的 `run_id` 要不要沿用 `L.new_run_id()`（parallel 用的那支）。
- §7-1 之後現行守衛會不會在 sequential 誤擋 —— **這條一定要實跑驗證**，不能推論。

---

## 11. 執行順序（本輪只做「第一輪」）

### 第一輪 —— 本派工單的範圍

| 步 | 做什麼 | 為什麼排這個位置 |
|---|---|---|
| **1** | **§7-1** 三處寫 `exec.json` 的路徑補 `schema: "exec-v4"`（`_exec_impl.py:323-328`、`:352-359`、`:977-983`），並把 `exec-v4` 加進 `EXEC_SCHEMAS` | 這是**獨立的 bug**：守衛在最常用的 sequential 路徑上整支失效。跟這份提案綁不綁都該修 |
| **2** | **§7-2** sequential 也生 `run_id` | 不生的話第 5 步的稽核在 sequential 永遠空手 |
| **3** | 實跑驗證：加了 schema 之後，現行守衛在 sequential 下**不會誤擋** | 第 1 步是行為變更，這一步是它的安全網。誤擋就退回重想 |
| **4** | **§4 A′** 建 `agents/devflow-reviewer.md`、`agents/devflow-adviser.md`（`allowedTools: [Read]`，完全不給 Bash / Edit / Write）＋ §4.4 的五項連帶記帳 | A′ **不依賴任何探針結果**（§7-3a 的說明），可以獨立完成 |
| **5** | **§6.1** `check-model-tiering.sh` 真實模式補 `worker-tasks == 0 → exit 2` 地板 | 一行，補完既有稽核的最後一個洞 |
| **6** | §7-3a／3b 兩個探針（記錄用），結果寫成 selftest fixture | 不阻斷前面五步，但要留檔給第二輪用 |

**發版**：第 1–3 步（守衛開始在 sequential 生效）**單獨發一版**，第 4–6 步再一版。

### 第二輪 —— 另立派工單，本輪不要碰

- **§5 B** 分層資料檔 + 組內順序（含 §5.4 的 `tier_of()` 三層改兩層）
- **§6.2 C′** 修 `_scan_low_tier_attempt()` 的判準（「起過」→「失敗過」）
- **§8 D** README ↔ guide 鏡像段落逐段加進釘住清單（治標）

⚠️ 為什麼分兩輪：B 與 C′ 都會反轉 `hooks/selftest.sh:2006-2057` 的 pinned 案例
（§6.4），還會撞 `test-architecture-guards.sh:1536` 的 `MIN_CASES` 靜態釘。
跟第一輪的行為變更混在同一輪，出事時分不出是誰造成的。

### 第三輪以後（尚未排程）

- §9 E `history-append.sh --amend-last`
- 鐵律 3 的措辭（帳號層檔案，不在本 repo）
- **Windows 上跑不出全綠**（rick 2026-08-19 裁決 5b：另立派工單）→ `notes/dispatch-windows-parity.md`。四條根因都有實測輸出；連帶處理 README 環境需求那句「裝好 Python 守衛就生效」承諾過頭的問題

---

## 12. 不要做

- **不要在本輪做第二輪的東西**（§5 B、§6.2 C′、§8 D）—— 它們會反轉八條既有
  pinned 測試，跟第一輪的行為變更混在一起，出事時分不出是誰造成的。
- **不要恢復 R1／R2**（撤回理由見 §3；恢復前先解決死鎖與無關派工誤擋）。
- **不要讓 hook 去「發起」派工。** hook 只有放行／擋下／塞 context 三種出口，
  技術上不能生 agent。
- **不要把執行者做成具名型別**，除非 §7-3a 的探針證明平台行為已改。
- **不要靠 `disallowedTools: Bash(...)` 當安全保證** —— 它 inert，真正的 deny 在
  `settings.json`。唯讀要靠 `allowedTools` 白名單（不給 Bash），不是靠 deny。
- **不要造第三套角色詞彙**（§0）。
- **不要讓 `stop` 拒絕收尾** —— 那是唯一的復原路徑（§3）。
- **不要在文件裡寫「這能防偽造」** —— 超出既有信任邊界。
- 每一支新守衛都要配**破壞實驗**：把它守的東西改壞，確認真的會紅。
  沒有反證的保護等於沒有保護（`notes/dispatch-v380-counterproof.md`）。

---

## 13. 本 repo 的落點紀律（執行輪必讀）

- `main` 有全域 hook（`~/.claude/scripts/git-flow-guard.py`，鐵律 9）擋直接 commit。
  每段收尾走：**短命 branch → commit → `merge --no-ff` 回 `main`**。
- `git push origin main` **由 owner 自己跑**，agent 會被擋。
- `docs/dev/HISTORY.md` 只能用 `scripts/history-append.sh` 追加。
- 收尾至少要跑：
  ```bash
  bash scripts/devflow-check.sh all
  bash hooks/selftest.sh
  env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
  bash hooks/devflow-exec.sh doctor
  bash scripts/test-architecture-guards.sh
  bash scripts/check-model-tiering.sh
  bash scripts/render-methodology-corrections.sh --check
  ```

---

## 附錄：v2 被查出的事實錯誤（已更正，留檔避免重犯）

| v2 寫的 | 正確值 |
|---|---|
| `_dispatch_impl.py` 只讀不寫 | 會寫 `.devflow/tier-exempt.json`（`:90`）；`_guard_impl.py:78` 也會寫檔 |
| 六個早退 | **八個**（漏 `:115-116` payload 讀不到、`:151-152` 豁免卡消耗） |
| 「唯一會擋」三個條件 | **四個**（多一個「無未消耗豁免卡」） |
| 跑過一次 haiku → 整個 run 不設防 | run≈T；真缺陷是判準只看「起過」不看「失敗過」 |
| `EXPECTED_MAPPED_FILES = 78` | **80** |
| guide `:1217` ← README `:535` | guide `:1223` ← README `:537-541` |
| corrections 只釘三處 | 四種 README 來源 + 八處模板來源，parity dict 共 15 條 |
| 四支 PreToolUse hook 都是純判斷 | 已有兩支會寫檔 |
| `dev-run/SKILL.md:82` 是嘗試上限句 | 上限句在 `:88-89`；`README.md:394` 另有第二份 |
| PLUGIN.md 有 hooks 表與 skills 表 | 是**同一張**目錄表的兩列（`:49`、`:50`） |
| 「機械上不會有任何一支守衛紅」 | `scripts/check-model-tiering.sh` 已在做事後稽核 |
