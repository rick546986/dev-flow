---
feature: five-station-f2
stage: 2-decision
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 2. 收斂 — 五站 F2（Implementer B：計數落點／doctor 誠實約束／dual-path）

> 把 `1-discussion.md` 收成一個選定方案。**G1 未送、不宣稱 PASS**。Lane = **full**。本 PR 只落 `2-decision.md` + 審頁 html。不寫 coordinator、不 bump 契約／schema、不改 doctor、不切 `graph.yaml`、不改 STATUS／HISTORY。
> Stage 1 頂欄仍 `status: draft`、當時寫「不送 G1、不宣稱 Human Stage1 PASS」。Owner 2026-09-14 對 Stage 1 回 **「ok」** 後才開本站。1-discussion 留當時說法；本檔記改口。本 hop **不是** G1 核准。
> F0 十條與 F2 刀界已鎖，本檔**不重開**：coordinator + hop／latch／cap 事件；留 token；不 F3；不折 in-flight。cap **數字** hop≤2／Decide≤1／Goal reopen≤1 已鎖。翻任一條 = 新 brief。
> B 線主軸：**Q9–Q16 計數落點收成 Decision**（有證據，不是再移交）；**marketplace × doctor 誠實是約束不是功能**；**F2 完成 = 同一電池 NEW5+OLD7**；**本 slug 凍舊 7**。獨立於 A／C，未讀他線 Stage 2。

## Real-world 去向
| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| 「沒有倉,第三次重寫在 live 裡可以假裝第一次」 | 本方案處理 | 1A：slug 級倉；F1 正則不是計數正本 |
| 「三個 cap 寫進 run 級 events.jsonl,新 run 歸零 = 暗改 cap(X5)」 | 本方案處理 | 1A／Q10：run 級倉不合法 |
| Journey「marketplace 換 hops；契約常未動」 | 本方案處理 | 6A：約束；marketplace 單獨不改線 |
| Journey「doctor COMPATIBLE + exit 0；綠只證明握手」 | 本方案處理 | 6A：doctor 綠 ≠ 切線。不是新功能 |
| Journey「F1 牙對第 3 次字樣紅；live 沒倉可對」 | 本方案處理 | 1A＋7A：RP-9／10／11 必須讀真計數 |
| Journey「chat 可以開下一站；謂詞真也等人」 | 本方案處理 | G-keep-1(1)；SC-10 |
| Workaround「F1 文案牙擋謊,不是 coordinator 行為」 | 本方案處理 | 6A：行為約束在 coordinator 前置，不改 doctor |
| Workaround「STATUS／HISTORY 當 hop log；看板可過期」 | 本方案處理 | 1C 棄；STATUS 不是 cap 正本 |
| Exception「舊 7／in-flight 不套三 cap」 | 本方案處理 | 8A；OLD7 路不套 |
| Exception「[Assumption] run 級 events = X5」 | 本方案處理 | Q10 升成 Decision：是 |
| Exception「[Assumption] 採用端先 update、後(或不)bump」 | 仍待驗 | 不升成已核；過期不得寫「現場都會一起 bump」 |
| Exception「[Assumption] 必須餵真計數給 RP-9／10／11」 | 本方案處理 | 7A：必須。過期擋「牙已夠」 |
| Exception「[Assumption] 同一入口兩路都能紅」 | 本方案處理 | 7A／SC-1 |
| Exception「[Assumption] NEW5 用合成 fixture」 | 本方案處理 | 8A：禁本目錄與 five-station-simplify |
| Q9 三個計數器落點 | 本方案處理 | 1A：slug 級倉。路徑／鍵名 OC-1 不鎖 |
| Q10 run 級歸零是否 X5 | 本方案處理 | 是。1B 棄 |
| Q11 hop_id 在 F3 前怎麼認 | 本方案處理 | 2A：1–7 檔名 stem；不改 graph.yaml |
| Q12 初寫 vs 重寫 | 本方案處理 | 3A：第一次寫該 hop 目標 = 0 |
| Q13 事件怎麼接 | 本方案處理 | 5A：slug 範圍附錄紀錄；F2 不 bump agent-event |
| Q14 stage 正則吃不進 Intake／Decide | 本方案處理 | 5A：不塞進 `stage` 欄 |
| Q15 Goal+Decide 是否同倉一次寫 | 本方案處理 | 4A：是 |
| Q16 T≤4 與 hop 重寫 | 本方案處理 | 3A：T 重試不吃 hop；整站重寫 5-tasks／6-notes 才吃 |
| Q17 三前置 | 本方案處理 | 6A：三條全要；doctor 綠不是第四條 |
| Q18 bump schema × doctor 紅 | 本方案處理 | 5A：F2 避免 bump。若後刀 bump，INCOMPATIBLE = 誠實握手，不是功能 |
| Q19 RP 讀真計數 | 本方案處理 | 7A |
| Q20 多 cache 認哪一份 | 本方案處理 | 6A：認專案樹（契約 + 1–7 md），不認 host cache |
| Q21 F2 完成 ≠ 檔在／F1 綠 | 本方案處理 | 7A／SC-1 |
| Q22 三失敗不得當成功 | 本方案處理 | SC-10 |
| Q23 五問可答、不鎖鍵 | 本方案處理 | 5A＋OC-1 |
| Q24 Backlog A stale | 刻意維持 | 看板 lag 證明 STATUS 不能當 hop／cap 正本；本 PR 不改 STATUS |
| G-self-1／Q4 本 slug 舊 7 | 本方案處理 | 8A |
| G-knife-1 留 token、不 F3、不折 in-flight | 本方案處理 | 8A |
| 「本 hop 不改模板、不送 G1」 | 刻意維持 | 8A：本 PR 只 Decision＋html |

## Approaches Considered

### 決策點 1：三個 cap 的計數落點（Q9／Q10）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 1A | **slug 級只增倉**是 hop≤2／Decide≤1／Goal≤1 的計數正本。新 `run_id`／重開 process 之後數字仍在。現有 run 級 `.devflow/runs/<run_id>/coordinator/events.jsonl` **不得**當唯一倉：新 run 讀空檔 = 計數 0 = X5。STATUS／git 重放也不是正本 | 對準狀態機「slug 級、只增不減」與 G-locus-1／G-locus-2；堵住 live 第三次假裝第一次 | 本檔不鎖路徑／鍵名（OC-1）；F2 才寫倉 | 中 | `notes/design/five-station-simplify-f0-state-machine.md:L124-L138` slug 級只增、按 hop 分桶、同時算；`:L198` X5。`observability/devflow_obs/ledger.py:L3-L6` ledger 按 run_id 分目錄。`docs/dev/five-station-f2/1-discussion.md:L185-L186` Q9／Q10；`:L145-L146` G-locus-1／2。成本 `[Assumption]` |
| 1B | **run 級 `coordinator/events.jsonl` 當計數正本**（沿用現有 ledger） | 零新檔；obs 已有寫者 | 新 run 歸零；違 X5；G-locus-1 反面。Q10 假設已被狀態機＋ledger 路徑撐住，不得再當未核 | 低 | `observability/devflow_obs/ledger.py:L3-L6`；`observability/devflow_obs/writer.py:L5-L6` 跨 worktree 分檔。`1-discussion.md:L186` Q10 期限=F2 Decision |
| 1C | **重放 git／STATUS／HISTORY 當計數** | 不寫 runtime 倉 | 看板已 stale（Backlog A 仍寫下一刀 F1）；人記 hop 會過期；無法機械拒第三次 | 低 | `docs/dev/STATUS.md:L50` Backlog A 仍指 F1；`docs/dev/five-station-f2/1-discussion.md:L200` Q24；`:L100` STATUS 當 hop log |

### 決策點 2：F3 前 hop_id 怎麼認（Q11）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 2A | **hop_id = 既有 1–7 檔名 stem**（`1-discussion`／`2-decision`／`3-prototype`／`4-spec`／`5-tasks`／`6-implementation-notes`／`7-review`）。同一寫檔動作一桶、各桶 hop≤2。F2 **不改** `graph.yaml`。不用舊節點名 `N7-g1` | 對準「同一站內同一寫檔動作」；F3 前五站 hop 還沒有 graph 節點也能分桶 | 檔名 stem 是編碼選擇（使用者沒點名）；3-prototype 與 4-spec 各一桶 | 低 | `notes/design/five-station-simplify-f0-state-machine.md:L129-L136` 同一 hop 或同一寫檔；按 hop 分桶。`docs/dev/five-station-f2/1-discussion.md:L187` Q11。`skills/dev-flow/stage2/graph.yaml:L53-L57` 預設仍經 N7-g1（舊 7）。`notes/design/five-station-simplify-brief-v3.md:L7-L9` F0–F2 不改 graph |
| 2B | **hop_id = 舊 graph 節點**（`N7-g1`／`N6-g2`） | 現成 id | 那些節點是舊 7 例行停，不是五站 hop；in-flight 與新機桶名撞車 | 低 | `1-discussion.md:L187` 舊節點是 N7-g1 這類；五站 hop 還沒有 graph 節點。`notes/design/five-station-simplify-f0-state-machine.md:L10-L15` 本機不管舊 7 hop |
| 2C | **F2 把五站節點寫進 `graph.yaml`** | 路線與 hop_id 同一份 | 偷做 F3 cut；違刀界；污染 F0–F2 仍舊 7 的觀測 | 高 | `notes/design/five-station-simplify-brief-v3.md:L176-L180` F2 不切預設；`:L166` F3 才預設五站。`1-discussion.md:L178` Q3 |

### 決策點 3：初寫 vs 重寫；T 嘗試 vs hop（Q12／Q16）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 3A | **第一次寫出該 hop_id 可解析目標 = 0**（不算重寫）。之後對同一 stem 的寫入 = 重寫 +1；第 3 次重寫拒、Escalated。計數看寫入發生，不看模型名。**T 重試吃該 T 上限 4，不吃 hop cap**；只有整份 `5-tasks.md`／`6-implementation-notes.md` 被整站重寫才加該 stem 的 hop 桶 | 對準狀態機原文；T seam 不被 hop≤2 誤殺 | 「整站重寫」邊界 Stage 4 要寫觀測（本檔鎖規則不鎖腳本） | 中 | `notes/design/five-station-simplify-f0-state-machine.md:L129` 第一次寫不算、第 3 次重寫拒；`:L138` 不看模型名；`:L107-L108` T 上限 4、整站重寫才吃 hop。`1-discussion.md:L188` Q12；`:L192` Q16 |
| 3B | **含初寫的每一次寫都 +1**（第三次寫入就拒） | 謂詞短 | 把「重寫 cap」做成「寫入 cap」；第一次改稿就被誤殺；違「第一次寫不算」 | 低 | `five-station-simplify-f0-state-machine.md:L129` 第一次寫不算。3B 改數字語意 = 暗改 cap |
| 3C | **換模型／換 session 不算；T 重試也算 hop 重寫** | 寫手可換模型逃計數；或 T 假綠更快被 cap | 狀態機已禁「換模型不計」；T≤4 與 hop 混桶會讓 Build 被誤殺或漏殺 | 中 | `five-station-simplify-f0-state-machine.md:L138`；`:L107-L108`。`1-discussion.md:L188` 計數看寫入、不看模型名 |

### 決策點 4：Goal reopen 與 Decide cap（Q15）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 4A | **同一 slug 倉、一次寫入**同時加 `goal_reopen` 與（若已離開過 Decide）`decide_reopen`，外加相關 hop 桶。分倉讓 Goal 重開躲掉 Decide cap = 非法 | 對準「Goal 可連帶用盡 Decide」；G-locus-2 拒絕時數字沒被改小 | 寫入要原子；路徑仍不鎖 | 中 | `notes/design/five-station-simplify-f0-state-machine.md:L137` Goal 連帶回 Decide；已用過那 1 次則 Escalated。偽碼 `:L143-L155`。`1-discussion.md:L191` Q15；`notes/design/five-station-simplify-f1-rp-min-set.md:L18` RP-11 可同時用盡 Decide |
| 4B | **Goal 倉與 Decide 倉分開**，各寫各的 | 實作簡單 | 分兩次寫可只加 Goal、不加 Decide = 躲 cap | 低 | `1-discussion.md:L191` 分倉可能讓 Goal 重開躲掉 Decide cap |
| 4C | **Goal reopen 免 Decide cap** | Goal 修正永遠走得動 | 違狀態機；等於放寬 Decide≤1 | 低 | `five-station-simplify-f0-state-machine.md:L137` 不得假裝 Goal 重開可免 Decide cap。`1-discussion.md:L180` Q5 不得放寬 |

### 決策點 5：hop／latch／cap 紀錄通道（Q13／Q14／Q18／Q23）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 5A | **slug 範圍附錄紀錄**留下前進／latch／cap。要能回答誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated。**不鎖** `event_type` 或 JSON 鍵。F2 **不 bump** `agent-event` 1.1、不把 Intake／Decide 塞進 `stage`。既有 1.1 繼續服務舊 7 生命週期。計數正本是 1A 倉，不是這份附錄、也不是 `attempt_completed` | 避開 schema 握手紅（Q18）；對準 OC-3／Q23；doctor 誠實維持約束 | 觀測暫時兩本；後刀若要併入 1.1 另開 | 中 | `observability/schema/agent-event.schema.json:L18` stage 正則 `^[1-7]-[a-z-]+$`；`:L81-L103` 無 hop／latch／cap 型別。`observability/devflow_obs/event_validate.py:L499-L503` unknown_event_type；`:L542-L546` 未列欄要 `x_`。`hooks/_doctor_impl.py:L216-L233` schema major.minor 不合 fail-closed。`1-discussion.md:L189-L190` Q13／Q14；`:L194` Q18；`:L198` Q23。`notes/design/five-station-simplify-f1-dual-read-annex.md:L34-L36` 不鎖鍵 |
| 5B | **新 `event_type` + bump agent-event**，把 hop／latch／cap 塞進 1.1 家族 | 一本帳 | 採用端只 update plugin、契約仍 1.1 → doctor INCOMPATIBLE。把誠實紅做成 F2 功能，違「doctor 誠實是約束不是功能」 | 高 | `hooks/_doctor_impl.py:L216-L233`；`devflow-contract.json:L11-L12` agent_event 仍 1.1。`1-discussion.md:L194` Q18 與 Q13 綁 |
| 5C | **既有 `stage_*` 加 `x_` 欄**冒充五站 hop | 不 bump | `stage` 正則拒 Intake／Decide；`x_` 只走隱私掃描、不是型別；`attempt_completed` 會冒充 hop 紀錄 | 低 | `agent-event.schema.json:L18`；`event_validate.py:L542-L546`。`1-discussion.md:L247` AC-7 不是 attempt_completed 冒充 |

### 決策點 6：marketplace × doctor 誠實（約束，不是功能）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 6A | **維持約束、不開功能**。doctor `COMPATIBLE`／exit 0 只證明握手（`2.0.0 ∈ supported`），≠ 路線沒變、≠ 已切五站。`marketplace update` 單獨不能改線。coordinator 評五站謂詞前三前置全要：契約已宣告 2.1.0 ∧ 非 in-flight ∧ 預設五站只在 F3 後。認**專案樹**（契約檔 + `docs/dev/<slug>/` 1–7 `.md`），不認「我從哪一份 plugin cache 啟動」。本刀不改 `hooks/_doctor_impl.py`、不改 marketplace | 對準 F1 SLOT 與 B 線 brief；綠當通行證會讓 SLOT 變裝飾 | 多 cache 現場仍可能兩機 hops 不同；靠專案樹擋改線，不靠改 doctor | 低 | `notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L28` SLOT-UNDECLARED／REJECT／DOCTOR-GREEN。`hooks/_doctor_impl.py:L193-L202` 握手只看版本集合；`:L492-L500` 綠印 COMPATIBLE。`skills/dev-setup/SKILL.md:L65-L71` 單一 entry、update 換 cache。`.claude-plugin/marketplace.json:L9-L16` source `./`。`1-discussion.md:L182-L184` Q7／Q8；`:L193` Q17；`:L196` Q20。`notes/design/five-station-simplify-brief-v3.md:L168` 未 upgrade = 舊 7 |
| 6B | **F2 改 doctor**：握手加路線欄，2.0.0 直接拒五站 hops | 陷阱當場閉環 | 把約束做成功能；違本 hop「不改 doctor」；可能讓未切母版自打 | 高 | `1-discussion.md:L166-L167` 本 hop 不改契約／既有牙。使用者 B 線：honesty stays constraint not feature |
| 6C | **doctor 綠 = 可跟 hops 走**；或「我已在 plugin cache」= 切五站 | 零新規則 | F1 已紅這句文案；coordinator 若用綠當通行證，SLOT 變謊 | 低 | `scripts/five_station_f1.py` 文案牙（1-discussion `:L44` 引 L217-L224）。`1-discussion.md:L147-L149` G-honest-1／2／G-trap-1 |

### 決策點 7：F2 完成判準與真計數牙（Q19／Q21／Q22）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 7A | **同一電池** NEW5 + OLD7：兩路都能獨立變紅、也能一起綠，才算 F2 完。NEW5 讀 1A 真計數（第三次 hop／第二次 Decide／第二次 Goal 拒且數字沒被改小）。OLD7：不折、不寫五站狀態、不套三 cap、token 在、F1 十二群仍綠。三失敗各自可紅：(1)謂詞真仍等人 (2)Must-keep 紅仍 hop (3)機械綠 → Ship Done。檔在／只重跑 F1／單路開心 hop ≠ 完 | 對準 G-dual-1／Q21／AC-9；堵住空心 F2 | 電池要後造；本 hop 不跑 | 中 | `docs/dev/five-station-f2/1-discussion.md:L154` G-dual-1；`:L155` G-keep-1；`:L197` Q21；`:L195` Q19；`:L248-L257` AC-9／AC-10。`scripts/five_station_f1.py:L327-L333` 現行牙咬字樣。`scripts/test-five-station-f1.sh:L1-L16` 十二群不證明 hop |
| 7B | **coordinator 檔在或 F1 十二群綠 = F2 完** | 最快宣稱 | 沒 hop 也能綠；in-flight 被折、token 被刪、舊 7 被三 cap 誤殺，電池仍綠 | 低 | `1-discussion.md:L173` 不把檔在／F1 綠寫成完成；`:L197` Q21 否 |
| 7C | **只測 NEW5 開心 hop**；OLD7／三失敗／真計數以後再說 | 看起來有自動前進 | 空心；違 dual-path；live 第三次牙仍只咬字 | 低 | `1-discussion.md:L111` 同一入口兩路；`:L195` 過期擋「牙已夠」 |

### 決策點 8：本 slug 路線與本 PR 切刀（Q4／刀界）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 8A | **本 slug 整段舊 7 到 Ship**。目錄已有 `1-discussion.md` = in-flight，不建立五站機。NEW5 只准合成 fixture，不是本目錄、也不是 `five-station-simplify`。本 PR 只 `2-decision.md` + 審頁 html；`status: draft`；`verdict` 空；不宣稱 G1 PASS；不改 STATUS／HISTORY；不寫 coordinator | 對準 OC-9／G-self-1／使用者本 hop；觀測不被自己污染 | 自己仍走例行 G1／G2；看起來沒吃到藥 | 低 | `notes/design/five-station-simplify-brief-v3.md:L165-L166`；`five-station-simplify-f0-state-machine.md:L49-L50` 已有舊 7 檔則不建機。`1-discussion.md:L179` Q4；`:L150` G-self-1；`:L217` 本資料夾已 in-flight。本 hop brief：Stage2-B、draft、no G1 PASS、no STATUS。檔集可 `git diff --name-only` 核對 |
| 8B | **本 slug 當新 5 第一個白老鼠** | 立刻跑真 hop | 觀測被自己污染；違 G-self-1／Q4；RP-15 活體 | 中 | `1-discussion.md:L172` 不把本 slug 當白老鼠；`:L114` NEW5 不是本目錄 |
| 8C | **本 PR 順便寫 coordinator／切預設／改 STATUS／填 G1 PASS** | 少一次 hop | 違四刀不併、違 feature branch 不碰看板、違本 hop 禁令 | 高 | `notes/design/five-station-simplify-brief-v3.md:L171-L180` 不准併刀。`docs/dev/STATUS.md:L10-L16` feature branch 不碰本檔。使用者：No G1 PASS、No STATUS／merge |

## 方案架構圖
```
[1A] slug級只增倉(選定)
[2A] 檔名stem當hop_id(選定)
[3A] 初寫0且T不吃hop(選定)
[4A] Goal+Decide同倉一次寫(選定)
[5A] slug紀錄不bump schema(選定)
[6A] doctor綠是約束不是功能(選定)
[7A] NEW5+OLD7同一電池(選定)
[8A] 本slug舊7本PR只Decision(選定)
```

## Decision
採 **1A+2A+3A+4A+5A+6A+7A+8A**：F2 的 hop≤2／Decide≤1／Goal reopen≤1 計數正本是 **slug 級只增倉**。新 run 之後數字仍在。run 級 `coordinator/events.jsonl` 當唯一倉 = X5（Q10 從假設升成 Decision）。hop_id = 既有 1–7 檔名 stem，各桶 ≤2；F2 不改 `graph.yaml`、不用 `N7-g1` 當五站 hop。第一次寫出該 stem 的可解析目標 = 0；其後寫入 = 重寫；第 3 次重寫拒。計數看寫入，不看模型名。T 重試 ≤4 不吃 hop；整站重寫 `5-tasks.md`／`6-implementation-notes.md` 才加該 stem。Goal reopen 與 Decide 重開必須同一倉一次寫入。hop／latch／cap 留 slug 範圍附錄紀錄，五問可答；不鎖鍵名；F2 不 bump agent-event、不把 Intake／Decide 塞進 `stage`。**marketplace × doctor 誠實是約束不是功能**：綠 ≠ 切線；update 單獨不改線；三前置全要；認專案樹不認 host cache；本刀不改 doctor。F2 完成 = 同一電池 NEW5+OLD7 都能獨立紅、也能一起綠；RP-9／10／11 必須讀真計數。本 slug 凍舊 7 到 Ship；NEW5 只准合成 fixture。本 PR 只 Decision＋html，draft，不送 G1。不選 1B／1C／2B／2C／3B／3C／4B／4C／5B／5C／6B／6C／7B／7C／8B／8C。

## Decision 約束（後站不准改成可選）
1. **slug 級只增倉**是三 cap 正本。run 級 events 當唯一倉 = X5。STATUS／git 重放不是正本。
2. **cap 數字不放寬**：hop≤2／Decide≤1／Goal reopen≤1；用盡 Escalated；不准暗改。舊 7／in-flight 不套。
3. **hop_id** = 1–7 檔名 stem；F2 不改 `graph.yaml`。
4. **初寫 = 0**；重寫看寫入不看模型；T≤4 不與 hop 混桶。
5. **Goal+Decide 同倉一次寫**；分倉躲 Decide = 非法。
6. **語意槽**（誰／從哪到哪／謂詞／哪只 cap／Escalated）不可少；鍵名不可鎖成已核。
7. **doctor 綠／marketplace update 不是路線許可。** 三前置全要。不改 doctor 當 F2 功能。
8. **Must-keep 未綠不得 hop。** 三失敗不得當成功。
9. **F2 完 = 同一電池 NEW5+OLD7。** 檔在／F1 綠／單路 hop ≠ 完。RP-9／10／11 讀真計數。
10. **本 slug 舊 7 到 Ship。** 不建五站機。NEW5 不是本目錄。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| 1B run 級 events 當倉 | 新 run 歸零 = X5；ledger 按 run_id 分目錄。 |
| 1C git／STATUS 當倉 | Backlog A 已證明看板會 stale；不能機械拒第三次。 |
| 2B 舊 graph 節點當 hop_id | N7-g1 是舊 7 例行停，不是五站 hop。 |
| 2C F2 改 graph.yaml | 偷做 F3；F0–F2 新軌仍舊 7。 |
| 3B 初寫也計次 | 改「第一次寫不算」= 暗改 cap。 |
| 3C 換模型不計／T 重試當 hop | 違「看寫入」；混桶誤殺 Build 或漏殺整站重寫。 |
| 4B 分倉 | Goal 重開可躲 Decide cap。 |
| 4C Goal 免 Decide | 放寬 Decide≤1。 |
| 5B bump agent-event | 把 doctor INCOMPATIBLE 做成 F2 功能。 |
| 5C stage_* + x_ | stage 正則拒別名；x_ 不是型別。 |
| 6B F2 改 doctor | 約束被做成功能；本 hop 禁改既有牙。 |
| 6C 綠 = 可跟 hops | F1 已紅；SLOT 變謊。 |
| 7B 檔在／F1 綠 = 完 | 空心 F2。 |
| 7C 只測 NEW5 開心 hop | 折舊 7／刪 token／誤套三 cap 仍綠。 |
| 8B 本 slug 當新 5 白老鼠 | 觀測自污；G-self-1 反面。 |
| 8C 本 PR 施工／改 STATUS／填 G1 | 違刀界與本 hop 禁令。 |
| 重開 F0 十條或放寬三 cap | 翻 = 新 brief。 |
| 刪 G1／G2／`ACCEPTED` | X2；dual-read／舊 7 失去錨。 |
| 折 in-flight | X4。 |

## Rationale
B 線要解的不是「五站好不好」，是「數字住哪、綠能不能當路條、怎樣才算做完」。

F1 牙對「第 3 次」這句話紅，對 live 重寫沒倉。狀態機寫明三個計數器是 slug 級、只增不減；現有 ledger 卻按 `run_id` 分目錄。1B 把現成檔當倉，新 run 讀 0，就是 X5。1C 已被本 tree 的過期 Backlog A 證偽。1A 只鎖**種類**：slug 級倉。路徑與鍵名留給後站，避免 Stage 2 偷做 annex。

hop_id 在 F3 前不能問 graph。2B 借用舊 7 停點名，桶會與 in-flight 撞。2C 改 graph 就是切預設。2A 用已經凍結的七個檔名 stem：同一寫檔動作一桶，不必動 `graph.yaml`。

3B／3C 會改 cap 語意或讓 T seam 被 hop≤2 誤傷。3A 照抄狀態機：初寫不算、看寫入、T≤4 另桶。4B／4C 讓 Goal 重開變成 Decide 逃生口。4A 一次寫死。

5B 為了統一 obs 去 bump schema，採用端只換 plugin 就會 doctor 紅——那是握手誠實，但做成 F2 功能就違 B 線「doctor 誠實是約束」。5C 塞不進 `stage` 正則。5A 讓紀錄可答五問，鍵名仍 OPEN。

6B／6C 是同一枚硬幣的兩面：改 doctor，或信綠。6A 兩面都不做。路線問專案樹與三前置，不問 cache、不問 COMPATIBLE。

7B／7C 是空心完成。7A 把 Stage 1 已鎖的 dual-path 與三失敗寫成可量測 SC，並強制真計數餵 RP-9／10／11。8B／8C 拿自己當白老鼠或偷施工。8A 讓本目錄繼續當 freeze 樣本。

## 既有脈絡
對帳快照（2026-09-14 tip `838e20a`，Stage 1 B `#325` 已合，STATUS companion `#328` 已開 Active）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| F0 brief＋狀態機 | Owner 已核；cap 數字與 X5 已鎖 | 本檔收落點，不重開數字 |
| F1 牙／annex | G3 PASS；RP-9／10／11 咬 fixture 字樣；SLOT 已寫 doctor 綠 ≠ 切線 | 7A 改讀真計數；6A 不改 doctor |
| Stage 1 `#325` | 1-discussion status=draft；Q9–Q16 仍 `[>]`／`[~]` | Owner「ok」後本檔把落點收成 Decision；1-discussion 留當時 OPEN |
| 契約／runtime | `2.0.0`；agent_event 1.1；doctor 只握手版本＋schema mm | 5A 不 bump；6A 綠 ≠ 路 |
| ledger | `.devflow/runs/<run_id>/coordinator/events.jsonl` | 1A：不得當 cap 正本 |
| marketplace | 單一 entry `./`；update 換 cache | 6A 約束 |
| 本 slug STATUS | Active 在 1-discussion；Gates 全白 | 本 branch **不**改這列（OC-2） |
| 本資料夾 | 已有 1-discussion.md／.html | 已 in-flight；出貨走舊 7 |
| Backlog A | 仍寫下一刀 F1 | stale；證明看板不是 hop 正本 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 後站把 run 級 events 又寫回計數正本 | 1A／SC-2：新 run 後計數變 0 → 本 Decision 被翻，回本站 |
| hop_id 被改成 N7-g1 或新 graph 節點 | 2A／約束 3；2B／2C 已 Rejected |
| 初寫被計次，或 T 重試吃 hop | 3A／SC-4 |
| Goal 分倉躲 Decide | 4A／SC-5 |
| F2 bump schema 讓採用端 doctor 紅，卻當「功能完成」 | 5A／6A：不 bump；若後刀 bump，紅只表示握手失敗 |
| coordinator 用 doctor 綠或 host cache 當切線 | 6A／SC-7／SC-8 |
| 宣稱 F2 完但只測 NEW5 或只證明檔在 | 7A／SC-1 |
| 本 slug 被拿去跑五站 hop | 8A／SC-9 |
| 採用「先 update 後 bump」為假，陷阱變窄 | 保持 Assumption（OC-4）。SLOT 與 6A 不依賴該假設為真 |
| 本 hop 被當成已過 G1 或已落地 coordinator | OC-2／SC-11：verdict 空、draft、檔集只有 Decision＋html |
| 後站把 dual-path／三失敗／slug 倉標可選 | OC-5：擋本 slug G2 |
| feature branch 手改 STATUS | OC-2 流程層 |

## Success Criteria
每條都要能用「對照稿／拒絕輸出／檔集」核對。7-review 對這張表，不對口頭「coordinator 寫了」。

- SC-1(G-dual-1／Q21)：同一入口電池。NEW5 具名案至少一條正向綠、一條缺行為紅；OLD7 亦然。整電池 exit 0 當且僅當兩路都過。只重跑 `test-five-station-f1.sh`、或只證明 coordinator 檔在 → 不得標 F2 完。NEW5 試體路徑不含 `docs/dev/five-station-f2/` 與 `docs/dev/five-station-simplify/`。
- SC-2(G-locus-1／Q9／Q10)：合成五站 slug 某 hop 重寫 1 次後，另開新 `run_id` 再讀 → 該 hop 桶仍是 1，Decide／Goal 未被清零。把 run 級 `events.jsonl` 當唯一倉且新 run 變 0 → 本 SC 紅。
- SC-3(G-locus-2／Q19)：同一 hop 已重寫 2 次，第 3 次被求執行 → 拒、Escalated、倉上數字仍是 2、無人手改小。RP-9／10／11 對這次 live 倉紅，不是只對 fixture 字樣「第 3 次」。
- SC-4(Q12／Q16)：該 hop 目標第一次寫出可解析檔 → 桶仍 0。同一 stem 其後寫入 → +1。單一 T 重試（未整份重寫 5-tasks／6-notes）→ hop 桶不變、該 T 嘗試 +1 且 ≤4。
- SC-5(Q15)：已離開 Decide 後的 Goal reopen，一次寫入後 `goal_reopen` 與 `decide_reopen` 都加；若 Decide 已用過那 1 次 → Escalated。兩個數字分檔、一次只加一邊 → 紅。
- SC-6(G-obs-1／Q23)：一次 hop 成功、一次 latch 開火、一次 cap 用盡 → 三筆都能指出，且能回答誰／從哪到哪／謂詞／哪只 cap／Escalated。不是 chat、不是 `attempt_completed` 冒充。鍵名可改，槽不能少。
- SC-7(G-honest-1／Q7)：契約仍 `2.0.0`、doctor 剛印 `COMPATIBLE`，求五站 hop → 拒。理由是路線未宣告／仍舊 7，不是「doctor 已綠」。
- SC-8(G-honest-2／G-trap-1／Q8／Q17／Q20)：只做 marketplace update、未宣告 2.1.0 → 路線仍舊 7；2.0.0+五站 hops 預設紅。兩份 plugin cache 不一致時，仍以專案契約 + 該 slug 是否已有 1–7 `.md` 為準，不以啟動 cache 為準。
- SC-9(G-self-1／Q4)：對 `docs/dev/five-station-f2/` 求五站自動前進 → 拒；無五站狀態寫入；本目錄仍走舊 7 到 Ship。
- SC-10(G-keep-1／Q22)：下列任一標 F2 成功 → 失敗：(1)謂詞全真且 latch 假，仍留下「要不要繼續」；(2)Must-keep 紅（如 T 缺 Verify）仍 hop；(3)機械全綠、無人寫 `verdict: PASS` 卻標 Ship Done。
- SC-11(G-knife-1／本 PR)：`git diff --name-only origin/main` 只含 `docs/dev/five-station-f2/2-decision.md` 與 `docs/dev/five-station-f2/2-decision.html`。無 `_templates/`、`graph.yaml`、`scripts/` 新牙、`STATUS.md`、`HISTORY.md`、`devflow-contract.json`、`hooks/_doctor_impl.py`、`observability/schema/`。頂欄 `status: draft`、`verdict` 空。
- SC-12(Q6 類不升格)：本檔任何「採用端先 update、契約仍 2.0.0」句仍標 Assumption 或「仍待驗」。把該句寫成已核事實 → 本 G1 應打回。

## Scope & Non-Goals(定稿)
- In：1A slug 級倉為三 cap 正本、run 級唯一倉=X5；2A 檔名 stem hop_id；3A 初寫 0＋T 不吃 hop；4A Goal+Decide 同倉一次寫；5A slug 範圍紀錄、不 bump、五問可答；6A doctor／marketplace 誠實為約束（三前置＋認專案樹）；7A 同一電池 NEW5+OLD7＋真計數牙＋三失敗可紅；8A 本 slug 凍舊 7、本 PR 只 Decision＋html。Q9–Q16／Q17–Q20 本方案處理。
- Out：1B／1C；2B／2C；3B／3C；4B／4C；5B／5C；6B／6C；7B／7C；8B／8C；重開 F0 十條；放寬三 cap；刪 token；F3 cut；折 in-flight；本 PR 寫 coordinator；本 PR 改 doctor／marketplace／schema／graph／模板；本 PR 改 STATUS／HISTORY；本 PR 填 G1 PASS；本 PR 合併；本 slug 當 NEW5 白老鼠；鎖 event／倉路徑鍵名；把「採用端都會一起 bump」升成已核。

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | 本檔選定倉的**種類**（slug 級只增）與紀錄的**語意槽**，**不選定**磁碟路徑、JSON／YAML 鍵名、`event_type` 字面。這是對「把 Q9／Q13 收成 Decision」的收窄 | 鎖鍵名 = 偷做 annex／schema；F1 OC-3 同型 | `1-discussion.md:L209` OC-3 不鎖鍵；`:L198` Q23；`five-station-simplify-f1-dual-read-annex.md:L1-L4` SLOT 不是必填鍵 | 後站提前鎖 `caps.json` 或 `event_type=hop_advanced`；與 5A 衝突 | 待人審 |
| OC-2 | 流程層：本 PR `status: draft`、`verdict` 空、不宣稱 G1 PASS、不改 STATUS／HISTORY、不合併 | 使用者本 hop 明文；feature branch 禁碰看板 | 本 hop brief：draft、No G1 PASS、No STATUS／merge。`docs/dev/STATUS.md:L10-L16` | 被當成已過 G1 或看板已進 Stage 2 | 待人審 |
| OC-3 | 本 PR 不實作 coordinator、不 bump 契約／agent-event、不改 doctor。6A 的約束等到後站牙，不在本 hop 改碼 | 收窄：使用者要 Decision 不是施工 | `1-discussion.md:L166-L167`；`notes/design/five-station-simplify-brief-v3.md:L176-L178` F2 碼在後刀 | 本 PR 長出 scripts／hooks → 違 SC-11 | 待人審 |
| OC-4 | 「採用端典型先 marketplace update、後(或不)bump 契約」維持 Assumption，不升成已核事實 | 無採用逐字稿；6A 不依賴它為真 | `1-discussion.md:L108`；`:L123` Assumption 四欄 | 把現場同步寫成事實 → SC-12 紅 | 待人審 |
| OC-5 | 後站 4-spec／5-tasks 不得把 slug 級倉、dual-path 同一電池、三失敗、語意槽五問、本 slug freeze 標成可選 | 延伸：使用者要這些進 Decision／SC；後站掏空 = 假完成 | `1-discussion.md:L215` Q21／Q22／Q23 後站不得標可選 | 空心 F2 仍能過 G2 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell。
- 方案架構圖只上選定案，Rejected 不上圖。
- hop_id 字面用檔名 stem（2A）；Station 別名（Intake／Decide）只當路線名，不當桶名。
- 本機 Stage 2 游標 `.devstage2-cursor.json` 不進 Git。

## ADR 晉升檢查
- 難逆轉:否（G3 未過；本檔與後站在 G3 前可改 Decision／OC；本 hop 零 runtime）
- 反直覺:是（現成 run 級 ledger 看起來像倉，新 run 卻是 X5；doctor 綠看起來像路條）
- 真 trade-off:是（slug 倉 vs 現有 ledger；不 bump vs 統一 obs）
→ 晉升:否（難逆轉=否；本 hop 禁寫 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-14 | Owner Stage2-B brief：Resolve counting-locus OQs（hop≤2／Decide≤1／Goal≤1）as Decision choices with evidence；marketplace×doctor honesty stays constraint not feature；dual-path NEW5+OLD7 selftest as Success Criteria；this slug freeze old 7。八點：倉／hop_id／計次／Goal+Decide／紀錄通道／doctor 約束／完成判準／本 slug+PR。
- Stage 1 改口 | 2026-09-14 | 1-discussion 仍 draft、Q9–Q16 當時 `[>]`／`[~]`。Owner Stage1 OK「ok」後本檔收斂。不改 1-discussion 頂欄。
- 自檢七掃 | 2026-09-14 | ①每案優劣有依據欄。②G-locus／honest／trap／self／knife／obs／carry／dual／keep 進 Decision／SC；漏項進 Non-Goals。③`[>]` Q9–Q16／Q18／Q20 本方案處理；Q10／Q17／Q19 假設升成或維持 Decision／OC-4。④SC 皆對照稿／拒絕／檔集。⑤Rejected 無空棄因。⑥八決策點由 B brief 確認；OC-1／3／5 收窄或延伸、OC-2 流程層、OC-4 不升格，皆可回溯決策點。⑦既有脈絡是對帳不是外移 schema。圖上 1A–8A 標選定，Rejected 未上圖。
