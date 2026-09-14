---
feature: five-station-f2
stage: 2-decision
status: approved
verdict: PASS
owner: rick
reviewers: [user]
updated: 2026-09-14
---
- Human verdict note: Human G1 PASS + OC-1…OC-12 Owner PASS @ 2026-09-14 Asia/Taipei。owner chat「可以」。未發明新 OC 答案。

# 2. 收斂 — 五站 F2（Winner C + owner standing soft-fix：anti-hollow dual-path）

> 把 `1-discussion.md` 收成一個選定方案。G1 已核:`verdict` PASS、`status` approved、OC-1～OC-12 ✅ Owner PASS。Lane = **full**。本 hop 只落 Human G1 attestation + 審頁重生；不實作 coordinator、不改 `_templates/`／`graph.yaml`／gate token、不改 STATUS／HISTORY（STATUS 另 companion）。
> Stage 1 頂欄仍 `status: draft`、當時寫「不送 G1」。Owner 2026-09-14 以「ok」開本站。1-discussion 留當時說法；改口記本檔。本 Stage 2 的 G1 是 human owner rick PASS（2026-09-14 Asia/Taipei owner chat「可以」），**不是** Agent 自裁。
> C 線主軸：**檔在 ≠ F2 完**。F2 完＝同一電池 NEW5+OLD7 都能獨立紅、也能一起綠。Non-Goals 鎖死 F3 cut／in-flight 折五站／刪 G1／G2／`ACCEPTED`。任何 owner 自拍板進 OC ledger。原文獨立於 A／B；**本檔含 owner standing soft-fix**（#330 全票勝出後吸收，非 C 線當時已讀他稿）。
> Owner standing 2026-09-14 必釘：檔→五站 `hop_id` 觸發表（五桶，拒 B 七 stem）；7A 從屬專案樹路線 SoT；Q12 persist=0 後 +1 進約束正文；CASE 極性＝注入壞行為該格紅；吸收 B marketplace×doctor 約束句、A 中途等人拒法。C 線長處全留（13 具名 CASE 只准加、slug 倉、Must-keep 入謂詞、OC-1…12）。G1 依 owner chat「可以」落檔；不發明 G2／G3 PASS。

## Real-world 去向
| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| 「F1 已鎖 cap 數字與拒收謂詞,但計數落在哪、鍵叫什麼明文交給 F2」 | 本方案處理 | 1A：選 slug 級只增倉；鍵名仍不鎖 |
| 「現行牙只對 fixture 字樣『第 3 次』正則紅——沒有倉,第三次重寫在 live 裡可以假裝第一次」 | 本方案處理 | 1A + 6A：RP-9／10／11 必須讀真計數 |
| 「若三個 cap 寫進 run 級 events.jsonl,新 run 歸零 = 暗改 cap(X5)」 | 本方案處理 | 1A 拒 1B；OC-5 升格 Q10 |
| 「marketplace update 換 hops,doctor 仍印 COMPATIBLE」 | 本方案處理 | 4A：綠 ≠ 切線 |
| 「若後續 coordinator 把綠或我已在 plugin cache 當成切五站,舊 7 slug 會被折」 | 本方案處理 | 4A + 7A + 8A |
| Journey「owner／寫手 chat『可以開下一站』」 | 本方案處理 | 5A／6A：謂詞真仍等人 = 失敗；不准問要不要繼續 |
| Journey「live 第三次重寫假裝第一次」 | 本方案處理 | 1A + SC-NEW5-CAP-3 |
| Workaround「F1 用文案正則擋『doctor 綠所以跟 hops』；擋的是寫出來的謊,不是 coordinator 行為」 | 本方案處理 | 4A：行為牙是 F2 的 |
| Workaround「STATUS／HISTORY 當 hop log；看板可以停在過期的下一刀 F1」 | 本方案處理 | 2C：紀錄不住看板 |
| Exception「舊 7 與 in-flight 不套三個 cap」 | 本方案處理 | 5A OLD7 路；8A 不折 |
| Exception「F2 可以寫 coordinator 碼,但 F3 前預設路線仍舊 7」 | 本方案處理 | 4A 第三前置 + 8A |
| Exception「[Assumption] 把 cap 放進 run 級 events = X5」 | 本方案處理 | Q10 升格；過期不得當已核已消 |
| Exception「[Assumption] dual-path 同一入口兩路都必須能獨立變紅」 | 本方案處理 | 5A；SC 具名 CASE |
| Exception「[Assumption] NEW5 試體是合成 fixture,不是本 slug」 | 本方案處理 | 8A；本目錄不是白老鼠 |
| 「本 tree 搜過:沒有 F2 coordinator 實作檔」 | 本方案處理 | F2 才寫碼；本 PR 零碼 |
| Q9 三個計數器落點 | 本方案處理 | 1A；不是另開 slug |
| Q10 run 級歸零是否 X5 | 本方案處理 | 是；1B 棄 |
| Q11 hop_id 在 F3 前怎麼認 | 本方案處理 | 3A 別名圖＋檔→五站觸發表（五桶，不是七 stem） |
| Q12 初寫 vs 重寫 | 本方案處理 | 約束正文：第一次成功 persist＝0，其後 +1；OC-11 只是延伸帳 |
| Q13／Q14／Q18 事件怎麼接 × schema bump | 本方案處理 | 2C 不 bump；語意槽可答 |
| Q15 Goal 連帶 Decide 是否一次寫 | 本方案處理 | OC-8 |
| Q16 T≤4 與 hop 重寫 | 本方案處理 | 狀態機已鎖；進 Decision 約束 |
| Q17 三前置 | 本方案處理 | 4A |
| Q19 RP-9／10／11 必須餵真計數 | 本方案處理 | 6A |
| Q20 多份 plugin cache 認哪一份 | 本方案處理 | 7A：cache 只選本 process 讀哪份 hops **碼**；路線 SoT＝專案樹 |
| Q21 F2 完是否=檔在或 F1 綠 | 本方案處理 | 否。5A |
| Q22 三失敗不得當成功 | 本方案處理 | 6A |
| Q23 事件五問、不鎖鍵 | 本方案處理 | 2C |
| Q24 Backlog A 過期 | 刻意維持 | 看板 lag 不是 F1 沒出貨；本 PR 不改 STATUS |
| 「鎖:不刪 G1／G2／ACCEPTED；不做 F3 cut；不把 in-flight 折成五站」 | 本方案處理 | 8A Non-Goals 鎖死 |

## Approaches Considered

### 決策點 1：計數落點（Q9／Q10／Q12／Q15）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 1A | **slug 級只增倉**。三計數器（`hop_rewrites[hop_id]`／`decide_reopen`／`goal_reopen`）住 slug 範圍、只增不減、新 `run_id`／重開 process 之後仍在。Goal 連帶回到 Decide 時與 Decide 計數**同一次 mutation** 寫入。舊 7 走 `allow_legacy()` 不碰這倉 | 對準狀態機「slug 級、只增不減」；擋 X5；AC-1／AC-2 可量測 | 本檔不鎖檔路徑／鍵名（F1 OC-3）；4-spec 才釘形 | 中 | `notes/design/five-station-simplify-f0-state-machine.md:L122-L155` 偽碼與分桶；`:L17` 狀態在 slug 級；`docs/dev/five-station-f2/1-discussion.md:L31-L36` 計數看寫入；同檔 `:L185-L186` Q9／Q10。路徑形 `[Assumption]`（4-spec） |
| 1B | **寫進現行 run 級** `.devflow/runs/<run_id>/coordinator/events.jsonl` | 現成 writer；不必新倉 | 新 run 讀空檔＝計數 0＝X5；違「只增不減」 | 低 | `observability/devflow_obs/ledger.py:L3-L6` run 級目錄；`five-station-simplify-f0-state-machine.md:L198` X5；`docs/dev/five-station-f2/1-discussion.md:L186` Q10 `[~]` 暫定 run 級不合法 |
| 1C | **重放 git 當計數器**（數該 slug 的站檔 commit） | 零新檔；跨 run 自然在 | 不是機械倉；rebase／amend／空 commit 會漂；無法同 mutation 寫 Goal+Decide；人改歷史＝暗改 cap | 高 | `[Assumption]` git 不是 cap 正本。`1-discussion.md:L100-L102` 這些步驟常不留「已重寫幾次」。狀態機要的是寫入發生,不是 VCS 故事 |

### 決策點 2：hop／latch／cap 紀錄怎麼接（Q13／Q14／Q18／G-obs-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 2A | **新 `event_type` + bump `agent-event` schema**，寫進現有 run ledger | 觀測棧統一；validator 認得 | 未定義型別今日會 `unknown_event_type`；`stage` 正則吃不進 Intake／Decide；bump 讓只 update plugin、契約 schema 仍 1.1 的採用端 doctor 變 INCOMPATIBLE（Q18）；且 run 級倉仍踩 Q10 | 高 | `observability/schema/agent-event.schema.json:L18` stage 正則；`:L81-L103` 無 hop／latch／cap 型別；`observability/devflow_obs/event_validate.py:L499-L503` 未定義拒；`hooks/_doctor_impl.py:L216-L233` schema major.minor 不合 fail-closed |
| 2B | **既有 `stage_*` 加 `x_` 欄**，不 bump schema | 2.0.0 採用端 doctor 可繼續握手綠 | `stage` 仍要 `1-discussion` 形；五站別名塞不進；`x_` 只躲隱私掃描、不是語意正本；仍 run 級 | 中 | `observability/devflow_obs/event_validate.py:L542-L546` 未列欄且無 `x_` 拒；`agent-event.schema.json:L18`。用 `x_` 冒充 hop 紀錄 = 討論已拒的「attempt_completed 冒充」（`1-discussion.md:L246`） |
| 2C | **獨立 slug ledger**（與 1A 同壽命）。前進／latch／cap 各留一筆人指得到的紀錄，能答五問（誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated）。**不鎖 JSON／YAML 鍵名。本刀不 bump `agent-event`。** 看板／chat／`STATUS.md` 不是正本 | 擋 X5；擋 Q18 誤紅；對準 Q23／F1 annex「不鎖鍵」；STATUS 過期已是活證據 | 觀測棧暫時兩套；4-spec 才選檔形 | 中 | `notes/design/five-station-simplify-brief-v3.md:L133` F2 才接 event、F0 只鎖要留；`notes/design/five-station-simplify-f1-dual-read-annex.md:L1-L4` SLOT 不是必填鍵；`docs/dev/five-station-f2/1-discussion.md:L199` Q23；同檔 `:L50` Backlog A 過期。檔形 `[Assumption]`（4-spec） |

### 決策點 3：F3 前 `hop_id` 怎麼認（Q11）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 3A | **別名圖＋檔→五站觸發表、不改 `graph.yaml`**。`hop_id` ∈ {Intake, Decide, Spec, Build, Ship}。寫檔觸發：`1-discussion`→Intake；`2-decision`→Decide；`3-prototype`\|`4-spec`→**同一 Spec 桶**；`5-tasks`\|`6-notes`→**同一 Build 桶**；`7-review`→Ship。無 Stage 3 trigger → 不建 `3-prototype`、也不另開 proto 桶。對準狀態機「同一 hop 節點（或同一站內同一寫檔動作）」。**禁止**七個 stem 各一桶（B 線 2A）——那會把 hop≤2 稀釋成七個獨立 2。舊節點 `N7-g1`／`N6-g2` **不是**五站 hop_id。F2 不長新 graph 節點 | 對準「五站是別名、檔名不動」與「同一寫檔動作」；五桶可測、不稀釋 cap | 寫手可能把舊 7 節點名或七 stem 寫進五站倉 | 低 | `notes/design/five-station-simplify-brief-v3.md:L47-L70` 別名表；`:L7-L9` F0–F3 不改各站 graph；`five-station-simplify-f0-state-machine.md:L129-L136` 同一 hop／同一寫檔、按 hop 分桶；`docs/dev/five-station-f2/1-discussion.md:L187` Q11；`skills/dev-flow/stage2/graph.yaml:L53-L57` 舊路仍經 N7-g1 |
| 3B | **沿用舊 graph 節點當 hop_id**（`N7-g1` 當 Decide） | 現成 id | 舊 7 的例行停點節點 ≠ 五站 hop；in-flight 與 NEW5 會共用 id 污染計數；F2 不該改 graph 卻把舊節點語意偷換 | 高 | `notes/design/five-station-simplify-f0-state-machine.md:L10-L15` 本機不管舊 7 hop；`:L49-L50` 已有舊 7 檔不建立本機 |
| 3C | **coordinator 私自發明新 hop 節點家族**（另寫一份五站 graph） | 看起來「真的五站了」 | 雙 graph；F3 才切預設；本刀偷做 F3；本 slug 若吃新 graph = 白老鼠 | 高 | `notes/design/five-station-simplify-brief-v3.md:L176-L180` F2 不做 F3 cut；`docs/dev/five-station-f2/1-discussion.md:L170` 本 slug 不是新 5 白老鼠 |

### 決策點 4：何時准評五站謂詞（Q17／G-honest／G-trap）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 4A | **三前置全要**：契約已宣告 2.1.0 ∧ 非 in-flight ∧ **F3 cut 已發生**。缺一條 → `allow_legacy()`，不建五站機。**marketplace × doctor 誠實是約束不是功能**：`doctor COMPATIBLE`／exit 0 只證明握手（`2.0.0 ∈ supported`），≠ 路線沒變、≠ 已切五站；`marketplace update` 單獨 ≠ cut。本刀不改 `hooks/_doctor_impl.py`、不改 marketplace。「我已在 plugin cache」也不是第四條。F3 前 coordinator 碼可以存在，但 live slug 一律舊 7；NEW5 只打合成 fixture | 對準 brief §6＋Q17；擋採用端升級陷阱；本 slug 自保；約束句比「綠≠切線」更緊 | F3 前現場痛還在（本來就該如此） | 低 | `docs/dev/five-station-f2/1-discussion.md:L193` Q17 `[~]`；`notes/design/five-station-simplify-brief-v3.md:L160-L168`；`notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L28` 三個 SLOT；`hooks/_doctor_impl.py:L193-L202` 綠只握手版本；`:L492-L500` 印 COMPATIBLE；B 線 6A 約束句 |
| 4B | **doctor 綠即可評五站 hop** | 寫手少記一條規則 | 這就是 SLOT-DOCTOR-GREEN-MEANS 要紅的謊；F1 牙已咬文案、F2 若用綠當通行證則文案牙變裝飾 | 低 | `scripts/five_station_f1.py:L60-L62` `DOCTOR_HOP`；`:L217-L224` S-5.5／S-5.6；`docs/dev/five-station-f2/1-discussion.md:L182` Q7 |
| 4C | **plugin cache 版本當路線**（cache 裡 hops 已是五站 → 切） | 跟「我已經更新了」的直覺合 | marketplace 單獨換 hops；契約可仍 2.0.0；多主機各一份 cache（Q20）會讓同一 repo 兩條路 | 中 | `skills/dev-setup/SKILL.md:L16` 節點／graph 不複製進採用專案；`:L62-L71` update 換 cache；`notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24` 2.0.0+五站 hops 紅 |

### 決策點 5：F2 完的定義（Q21／G-dual-1）— C 線主軸
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 5A | **同一電池、兩路都要能獨立紅也能一起綠**。單一入口（一支 selftest／一個 process）。NEW5＝合成 fixture（不是本目錄、不是 `five-station-simplify`）。OLD7＝已有 1–7 `.md` 的 fixture（不折、token 在、三 cap 不套、F1 牙仍綠）。缺一路、跳過一路、只跑 `test-five-station-f1.sh`、只證明「coordinator 檔在」→ 整電池非 0。具名 CASE 見 Success Criteria | 對準 Q21／AC-9；擋 hollow F2 | CASE 表要後站實作；本 PR 不寫測 | 中 | `docs/dev/five-station-f2/1-discussion.md:L154` G-dual-1；`:L197` Q21；`:L252-L255` AC-9；`docs/dev/five-station-simplify/4-spec.md:L828-L832` F1 十二群不證明 hop；`scripts/test-five-station-f1.sh:L1-L16` 牙自檢不是 hop 電池。入口檔名 `[Assumption]`（4-spec） |
| 5B | **coordinator 檔存在 = F2 完** | 最快宣告 | 沒 hop、沒事件、沒雙路；這就是 hollow | 低 | `docs/dev/five-station-f2/1-discussion.md:L173` 不把檔在寫成 F2 完成；`:L20` 檔在或 F1 綠 ≠ F2 完 |
| 5C | **F1 十二群仍綠 = F2 完**（回歸地板冒充完工） | 現成綠 | F1 證明對照稿牙；沒有 live 倉、沒有 hop。只測 NEW5 還會讓 OLD7 被折／token 被刪而電池仍綠 | 低 | `docs/dev/five-station-simplify/5-tasks.md:L66-L72` coordinator 延後 F2；`scripts/test-five-station-f1.sh:L1-L16` |

### 決策點 6：Must-keep vs hop，以及真計數（Q19／Q22）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 6A | **自動前進謂詞含完整度**。Must-keep 未綠不得 hop。三失敗各自要能紅：(1)謂詞真仍留下「要不要繼續」；(2)Must-keep 紅仍 hop；(3)機械綠 → Ship Done。**RP-9／10／11 必須讀 1A 倉**，不得只咬 fixture「第 3 次」字樣。T 重做吃該 T 嘗試上限 4，不另吃 hop cap，除非整份 5-tasks／6-notes 被整站重寫 | 擋比舊 7 更快的假完成；live 第三次重寫牙看得到 | F1 正則牙可留作回歸；F2 要加讀倉路徑 | 中 | `notes/design/five-station-simplify-brief-v3.md:L135-L158` M1–M16；`five-station-simplify-f0-state-machine.md:L110-L120` Ship 無自動前進；`:L107-L108` T≤4；`docs/dev/five-station-f2/1-discussion.md:L194-L198` Q19／Q22；`scripts/five_station_f1.py:L327-L333` 現行咬字樣 |
| 6B | **先 hop 再補 Must-keep**（「已經五站了所以可省」） | Build 看起來短 | 假完成更快；違 brief；G-keep-1 反面 | 低 | `docs/dev/five-station-f2/1-discussion.md:L174` 不把 hop 比較快解讀成 Must-keep 可 hop 掉；`brief-v3.md:L158` 少一條=違 brief |
| 6C | **F2 繼續只靠 fixture 字樣牙，不餵真計數** | 零新接線 | live 第三次重寫牙看不見；Q19 過期擋 G2 | 低 | `notes/design/five-station-simplify-f1-rp-min-set.md:L4` 計數落點交 F2；`docs/dev/five-station-f2/1-discussion.md:L111` 若不餵真計數牙繼續只咬 fixture |

### 決策點 7：多份 plugin cache（Q20）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 7A | **plugin root 從屬於專案樹路線 SoT**。當下行程 host plugin root **只**決定本 process 讀哪一份 hops **碼**，**不是**路線許可。路線仍要 2.1.0 已宣告 ∧ ¬in-flight ∧ F3 cut 已發生（4A）。`doctor COMPATIBLE`／`marketplace update` ≠ cut。認專案樹（契約檔 + `docs/dev/<slug>/` 是否已有 1–7 `.md`），不認「我從哪一份 plugin cache 啟動」。不掃磁碟上「最新」的其他 cache。同一 repo 多 cache 時各行程各讀各的碼；**不得**因 A 機 hops 新就把 B 機舊 7 slug 遠端改線 | 對準「不得遠端改線」；cache 與路線分家，行為可測 | 人會看到「同一 repo 兩台機器 hops 碼不同」——那是升級陷阱,要寫進採用說明,不是用共識掃描或 cache 當路條掩蓋 | 低 | `docs/dev/five-station-f2/1-discussion.md:L196` Q20；`notes/design/five-station-simplify-brief-v3.md:L168` 不得遠端改線；`skills/dev-setup/SKILL.md:L62-L71` plugin root 在 cache、隨版本變；B 線 6A「認專案樹不認 host cache」 |
| 7B | **掃主機上所有 plugin cache，取最新 hops** | 看起來「永遠最新」 | 把未宣告 2.1.0 的舊 7 行程拖進五站；遠端改線的變種 | 中 | 同 4C；`SLOT-UNDECLARED-ROUTE`。共識掃描 `[Assumption]` 會跨過契約宣告 |
| 7C | **F2 不管 Q20**（留給 F3 散文） | 範圍小 | 升級陷阱少一顆牙；coordinator 若預設掃 cache 會靜默 7B | 低 | `docs/dev/five-station-f2/1-discussion.md:L340` 多 cache 是已確認陷阱。不管 = 讓 7B 當預設 |

### 決策點 8：F2 刀與三把 Non-Goals 鎖（G-knife-1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 8A | **F2 = coordinator + hop／latch／cap 紀錄**。三把鎖寫進 Non-Goals、不准後站改成可選：(1) **不做 F3 cut**（新 slug 仍舊 7）；(2) **不把 in-flight 折成五站**；(3) **不刪** G1／G2／`ACCEPTED` token 與檔。本 slug 自己走到 G1／G2／G3 仍舊 7。本 PR 只 Decision＋html，零碼 | 對準 brief §7；擋偷做 F3；本目錄當 freeze 樣本 | 採用端預設痛留到 F3 | 低 | `notes/design/five-station-simplify-brief-v3.md:L176-L182`；`docs/dev/five-station-f2/1-discussion.md:L168-L170` Non-Goals 初稿鎖；`:L180-L181` Q3／Q4；`:L206` Owner-locked F2 刀 |
| 8B | **本刀順便 F3 cut**（新 slug 預設五站） | 現場立刻少停 | 違「不准併刀」；雙路線污染觀測；本目錄已 in-flight 語意漂 | 高 | `brief-v3.md:L173` 不准併刀；`:L166` F3 cut 之後才預設五站 |
| 8C | **刪 token／折 in-flight，謂詞比較好寫** | 狀態機短 | X2／X4；dual-read 與舊 7 失去錨；hollow 的另一面 | 高 | `five-station-simplify-f0-state-machine.md:L193-L196` X2／X4；`brief-v3.md:L182` 刪 G1／G2／`ACCEPTED` = 新 brief |

## 方案架構圖
```
[1A] slug級只增倉(選定)
[2C] slug ledger不bump schema(選定)
[3A] hop_id=五站桶觸發表(選定)
[4A] 三前置;marketplace×doctor是約束(選定)
[5A] 同一電池NEW5+OLD7(選定)
[6A] Must-keep入謂詞+真計數(選定)
[7A] cache只選碼;路線認專案樹(選定)
[8A] 不F3/不折/不刪token(選定)
```

## Decision
採 **1A+2C+3A+4A+5A+6A+7A+8A**：F2 寫 coordinator，讀 brief §3 謂詞——真則 hop、假則停修、latch 開火進 HumanWait、cap 用盡 Escalated。謂詞全真 ∧ latch 假 → **立刻 hop**，不准留下「要不要繼續／請人審／確認一下」（A 線中途等人＝失敗 1）。三個 cap 計數與 hop／latch／cap 紀錄都住 **slug 級只增倉**（獨立 ledger，與 run 級 `events.jsonl` 分家）。新 `run_id` 不得把數字歸零。Goal reopen 連帶回到 Decide 時，兩個計數**同一次 mutation** 寫入。某 `hop_id` **第一次成功 persist＝0**，其後每一次成功 persist 該桶 +1；第一次寫不算進 hop≤2。`hop_id` 用五站別名＋**檔→五站觸發表**（五桶，不是七 stem），不改 `graph.yaml`，不用舊節點 `N7-g1` 冒充。紀錄必須讓人指得到並回答五問（誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated）；**不鎖鍵名；本刀不 bump `agent-event`**。Coordinator 評五站謂詞之前先問**專案樹**路線：未宣告 2.1.0、或 in-flight、或 F3 cut 尚未發生 → `allow_legacy()`。**marketplace × doctor 誠實是約束不是功能**：`COMPATIBLE`／exit 0 只證明握手；`marketplace update` 單獨 ≠ cut；plugin cache 只選本 process 讀哪份 hops 碼，不是路條。F3 前 live slug（含 `docs/dev/five-station-f2/`）不建五站機；NEW5 只准合成 fixture。**F2 完＝同一電池 NEW5+OLD7 都能獨立紅、也能一起綠。** coordinator 檔在、F1 十二群綠、單路開心 hop、只重跑 `test-five-station-f1.sh` **都不算** F2 綠。Must-keep 未綠不得 hop；RP-9／10／11 讀真計數。Non-Goals 鎖死：不做 F3 cut、不折 in-flight、不刪 G1／G2／`ACCEPTED`。不選 1B／1C／2A／2B／3B／3C／4B／4C／5B／5C／6B／6C／7B／7C／8B／8C；亦不選 B 線七 stem 各一桶。

## Decision 約束（後站不准改成可選）
1. **檔在 ≠ F2 完。** 5B／5C 已拒。後站若把「coordinator 模組存在」或「F1 十二群綠」寫成完成條件 → 回本站。
2. **同一電池。** NEW5 與 OLD7 必須走同一入口；缺一路即整電池紅。兩支互不認識的腳本各綠一次 ≠ dual-path。
3. **NEW5 試體是合成 fixture**，不是本目錄、不是 `five-station-simplify`。
4. **三把 Non-Goals 鎖**：不做 F3 cut；不折 in-flight；不刪 G1／G2／`ACCEPTED`。把其中一把標成「可選簡化」＝翻 Decision。
5. **cap 數字已鎖**：hop≤2／Decide≤1／Goal reopen≤1；用盡 Escalated；不准暗改。舊 7 不套。T 嘗試 ≤4 不與 hop 桶混算，除非整站重寫 5-tasks／6-notes（加的是 **Build** 桶，不是兩個 stem 桶）。
6. **Q12 初寫／重寫（約束正文，不是只寫在 OC）**：某 `hop_id` **第一次成功 persist＝0**；其後每一次成功 persist 該桶 +1。第一次寫不算進 hop≤2。計數看寫入發生，不看模型名／session。
7. **Must-keep 未綠不得 hop。** 三失敗各自可紅，不得用「已經五站了」省略。
8. **latch 未命中不得中途等人（A 線拒法）**。謂詞全真 ∧ latch 假 → 立刻 hop，不准留下「要不要繼續／請人審／確認一下」。謂詞假 → 停該站修，不是改問人。中途等人＝失敗 1，不是客氣。
9. **marketplace × doctor 誠實是約束不是功能。** `COMPATIBLE`／exit 0 只證明握手，≠ 路線沒變、≠ 已切五站。`marketplace update` 單獨 ≠ cut。未宣告 2.1.0 = 舊 7。2.0.0 + 五站 hops 預設 = 違規。本刀不改 doctor。
10. **7A 從屬專案樹路線 SoT。** plugin cache 只選本 process 讀哪份 hops **碼**，不是路線許可。路線仍要 2.1.0 ∧ ¬in-flight ∧ F3 cut。認專案樹（契約 + 該 slug 是否已有 1–7 `.md`），不認啟動 cache。
11. **語意槽可答、鍵名 OPEN。** 後站鎖 `event_type=hop_advanced` 當本 Decision 已核 = 偷做 annex，回本站。
12. **本 slug 出貨路徑舊 7。** 對本目錄建五站機 = RP-15。
13. **RP-9／10／11 必須讀 1A 倉。** 只留 fixture 字樣正則 = 6C，已拒。
14. **檔→五站 hop_id 觸發表**（對準狀態機「同一 hop 節點／同一站內同一寫檔動作」）。五桶，**不是**七個 stem：

| 寫入檔 | hop_id 桶 |
|---|---|
| `1-discussion.md` | Intake |
| `2-decision.md` | Decide |
| `3-prototype.md` | **Spec**（與 `4-spec.md` 同桶） |
| `4-spec.md` | Spec |
| `5-tasks.md` | **Build**（與 `6-implementation-notes.md` 同桶） |
| `6-implementation-notes.md` | Build |
| `7-review.md` | Ship |

無 Stage 3 trigger → 不建 `3-prototype`、也不另開 proto 桶；Spec 只由 `4-spec.md` 觸發。B 線 2A（七 stem 各 ≤2）已拒：稀釋 hop≤2。舊節點 `N7-g1`／`N6-g2` 不是桶名。
15. **CASE 極性**：列寫「→ 紅」＝測法是**注入該壞行為**，該格必須獨立變紅。把「coordinator 拒 hop／拒寫」記成該紅格綠＝極性反了（A 線「拒 hop 算綠」），已拒。綠格才是合法行為應發生。

## 本方案要求（F2 電池最小 CASE；4-spec 只准加不准減）
極性：標「→ 紅」的列＝**注入該壞行為**，該格必須獨立變紅。不准把「拒 hop」記成紅格綠。

| CASE | 路 | 紅／綠什麼 |
|---|---|---|
| NEW5-HOP-OK | NEW5 | 謂詞全真、latch 假、Must-keep 綠 → hop；紀錄答五問（綠格：合法行為應發生） |
| NEW5-PRED-STOP | NEW5 | 謂詞假 → 不 hop、停修、不留「要不要繼續」（綠格：合法停修） |
| NEW5-CAP-3 | NEW5 | 第 3 次 hop 重寫拒；Escalated；拒後計數仍是 2（綠格：合法拒） |
| NEW5-DECIDE-2 | NEW5 | 第 2 次 Decide 整站重開拒（綠格：合法拒） |
| NEW5-GOAL-2 | NEW5 | 離開 Intake 後第 2 次 Goal 重開拒（可同時用盡 Decide cap）（綠格：合法拒） |
| NEW5-MK-RED | NEW5 | **注入** Must-keep 紅（例：T 缺 Verify）仍 hop → **該格紅**（不是「拒 hop 算綠」） |
| NEW5-SHIP-MECH | NEW5 | **注入** 機械全綠、無人寫 `verdict: PASS` 卻標 Done → **該格紅** |
| NEW5-WAIT-RED | NEW5 | **注入** 謂詞真、latch 假，卻留下「要不要繼續／請人審／確認一下」→ **該格紅** |
| NEW5-RUN2 | NEW5 | 另開新 `run_id` 再讀，該 hop 桶數字仍在、不是 0（綠格） |
| OLD7-NO-FIVE | OLD7 | 已有 1–7 `.md` → 無五站狀態寫入；三 cap 不套（綠格） |
| OLD7-FOLD-RED | OLD7 | **注入** 對 in-flight 寫五站狀態／五站 hop → **該格紅**（RP-15） |
| OLD7-TOKEN | OLD7 | G1／G2／`ACCEPTED` token 與檔仍在；F1 牙回歸仍綠（綠格） |
| OLD7-SELF | OLD7 | 對 `docs/dev/five-station-f2/` 求五站自動前進 → 跳不過（綠格：合法拒） |

減任一列 = 翻本 Decision。4-spec 可加列，不可把「檔在」加成通過條件。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| 1B run 級 events 當 cap 倉 | 新 run 歸零＝X5；ledger 按 `run_id` 分目錄。 |
| 1C git 重放當計數 | 歷史可改；不是只增倉；Goal+Decide 無法一次寫。 |
| 2A bump agent-event | 現行型別接不住；Q18 讓 2.0.0 採用端 doctor 誤紅；且常仍 run 級。 |
| 2B stage_* + x_ | stage 正則拒五站別名；`x_` 不是語意正本；attempt 冒充已拒。 |
| 3B 舊 graph 節點當 hop_id | 舊 7 停點節點 ≠ 五站 hop；污染 in-flight 計數。 |
| 3C 另寫五站 graph | 偷做 F3；雙路線。 |
| 七 stem 各一桶（B 線 2A） | 把 hop≤2 稀釋成七個獨立 2；口稱「同一寫檔動作」卻讓 `3-prototype`／`4-spec`、`5-tasks`／`6-notes` 各一桶。 |
| 4B doctor 綠當通行證 | SLOT-DOCTOR-GREEN-MEANS；F1 文案牙變裝飾。 |
| 4C cache 當路線 | marketplace 可單獨換 hops；多 cache 會遠端改線。cache 不是路條。 |
| 5B 檔在＝完 | hollow F2；Q21 已否。 |
| 5C F1 綠＝完 | 十二群不證明 hop；單路綠會遮 OLD7 被折。 |
| 6B 先 hop 再補完整度 | 比舊 7 更快假完成。 |
| 6C 繼續只咬「第 3 次」字樣 | live 第三次重寫牙看不見；Q19 過期擋 G2。 |
| 7B 掃全機最新 cache | 把未宣告 2.1.0 的行程拖進五站。 |
| 7C 不管 Q20 | coordinator 預設會滑向 7B。 |
| 8B 本刀 F3 cut | 不准併刀；觀測被自己污染。 |
| 8C 刪 token／折 in-flight | X2／X4；新 brief，不是本切法尾巴。 |
| 重開 F0 十條或放寬三 cap | 翻＝新 brief。 |
| 拿本 slug 當 NEW5 白老鼠 | 目錄已 in-flight；G-self-1 反面。 |
| 本 PR 寫 coordinator／改 STATUS／填 G1 PASS | 使用者：draft、only 2-decision+html、No G1 PASS。 |

## Rationale
F1 把數字與拒收謂詞釘死，但把「倉在哪」明文交給 F2。現行牙讀的是 fixture 正文「第 3 次」。沒有 slug 倉，live 第三次重寫可以當第一次——這不是牙不夠嚴，是牙咬錯東西。1B 把計數放進 run 級 `events.jsonl`，看起來接了觀測棧，其實新 run 就是 reset，正好踩 X5。1A 是狀態機偽碼已經寫出來的落點；本檔只是把它從「未選」收成選定，鍵名仍 OPEN。

事件也是同一條縫。2A bump schema 會讓只 update plugin 的採用端被 doctor 因 schema 握手誤紅——那是誠實紅，但 F2 刀不包含「逼所有 2.0.0 採用端一起 bump」。2B 用 `x_` 躲 validator，答不了五問。2C 讓紀錄與計數同壽命、不 bump、不鎖鍵。

C 線要擋的 hollow 不是「少寫幾段散文」，是三種假綠：(1) 檔在；(2) F1 回歸綠；(3) 只打 NEW5 開心 hop。5A 把完成定義收成同一電池兩路。OLD7 路必須能獨立紅（折 in-flight、刪 token），否則五站機可以靠犧牲舊 7 換綠。

4B／4C 是採用端陷阱的實作版。doctor 綠只證明 `2.0.0 ∈ supported`。hops 住方法包，`marketplace update` 就能換。三前置少「F3 cut 已發生」這條，F2 會在母版改版軌上提前切線，違反 brief §6。

8B／8C 把後兩刀偷進本刀。摺的是停點，不是完整度，也不是「把舊閘檔刪掉比較好寫謂詞」。

## 既有脈絡
對帳快照（2026-09-14 `origin/main` `838e20a`，Stage1-B `#325` 已合，STATUS Active 已開 `#328`）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| F0 brief＋狀態機 | Owner 已核；十條與三 cap 鎖死 | 本檔只收 F2 落點；不重開 |
| F1 | Human G3 PASS；牙咬字樣與 doctor 文案 | 回歸地板，不是 F2 完成條件 |
| Stage 1 `#325` | 1-discussion status=draft；OQ 全三態 | 留當時說法；Owner「ok」後本檔改口 |
| 契約／doctor | `2.0.0`；綠＝握手；schema 1.1 | 4A：綠 ≠ 五站；2C：本刀不 bump |
| ledger | run 級 `coordinator/events.jsonl` | 1B 棄；1A／2C 另倉 |
| 本 slug STATUS | Active 在 1-discussion；Gates 全白 | 本 branch **不**改這列（OC-10） |
| 本資料夾 | 已有 1-discussion.md／.html | 已 in-flight；出貨走舊 7 |
| F2 碼 | 無 | 本 PR 仍無；電池在後站 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 後站把「coordinator 檔在」寫成 F2 完 | 5B 進 Rejected；約束 1；SC-HOLLOW；OC-9 具名 CASE |
| 只跑 NEW5 或只重跑 F1 十二群 | 5A 同一入口；SC-BATTERY 缺一路即非 0 |
| 把 cap 寫進 run 級 events「先接上再說」 | 1B 棄；OC-5；SC-NEW5-RUN2 |
| bump schema 當唯一事件路，採用端 doctor 誤紅 | 2C；Q18 去向＝避免 bump，不是接受誤紅 |
| 對本目錄或 `five-station-simplify` 開五站機 | 8A／OLD7-SELF；NEW5 合成 fixture |
| 後站把 F3 cut／折 in-flight／刪 token 標可選 | 約束 4；OC-12；8B／8C 棄因 |
| RP-9／10／11 繼續只咬字樣 | 6A／OC-6；6C 棄 |
| 多 cache 掃最新 hops | 7A／OC-7 |
| feature branch 手改 STATUS | OC-10 流程層 |
| 本 hop 被當成已過 G1 或已落地 Stage 3／4 | G1 已按 owner chat「可以」落檔（`verdict` PASS、`status` approved、OC-1～OC-12 ✅）；本 PR 只含本目錄 2-decision.md／.html；翻案回本站。不發明 G2／G3。不開 Stage 3／4 |
| Q17／Q10／Q19 假設被當「討論已核、Decision 可改口」 | 本檔升格並進 OC-4／5／6；推翻＝回本站 |
| 4-spec 減 CASE 表 | 「只准加不准減」；減列翻 Decision |
| hop_id 改七 stem 或另開 3-proto 桶 | 約束 14；稀釋 hop≤2；無 trigger 不建 proto 桶 |
| 把 Q12 只留在 OC、後站當可選 | 約束 6 正文；第一次 persist＝0 |

## Success Criteria
每條都要能用「具名 CASE 輸出／拒絕理由／檔集」核對。7-review 對這張表，不對口頭「coordinator 看起來有了」。

- **SC-BATTERY**(G-dual-1)：存在**單一入口**跑完整電池。exit 0 **當且僅當** NEW5 組與 OLD7 組都過。缺一組、跳過一組、或入口只轉呼叫 `scripts/test-five-station-f1.sh` → 非 0。觀測：該入口的原始 stdout／exit。
- **SC-NEW5-HOP-OK**：NEW5-HOP-OK 綠。謂詞全真、latch 假、Must-keep 綠 → 發生 hop；人指得到一筆紀錄且五問有答（誰／從哪到哪／謂詞／cap／Escalated）。不是 chat、不是 `attempt_completed` 冒充。
- **SC-NEW5-PRED-STOP**：NEW5-PRED-STOP 綠。謂詞假 → 不 hop；理由是該謂詞假；無「要不要繼續」。
- **SC-NEW5-CAP-3**：NEW5-CAP-3 綠。同一 hop 已重寫 2 次後第 3 次被拒；狀態 Escalated；拒後該桶數字仍是 2（無人手改小、無 reset）。
- **SC-NEW5-DECIDE-2**：NEW5-DECIDE-2 綠。第 2 次 Decide 整站重開被拒。
- **SC-NEW5-GOAL-2**：NEW5-GOAL-2 綠。離開 Intake 後第 2 次 Goal 重開被拒；Decide cap 可被連帶用盡。
- **SC-NEW5-MK-RED**：NEW5-MK-RED 為**預期紅**。測法＝**注入**「Must-keep 紅仍 hop」。該格必須獨立變紅。把「coordinator 拒 hop」記成此格綠＝極性反了，已拒。不得標 F2 成功。
- **SC-NEW5-SHIP-MECH**：NEW5-SHIP-MECH 為預期紅。測法＝**注入**「機械全綠、無人寫 `verdict: PASS` 卻標 Done」。該格紅。
- **SC-NEW5-WAIT-RED**：NEW5-WAIT-RED 為預期紅。測法＝**注入**「謂詞真、latch 假，仍留下要不要繼續／請人審／確認一下」。該格紅。中途等人不是客氣。
- **SC-NEW5-RUN2**：NEW5-RUN2 綠。同一 slug 另開新 `run_id` 後，已寫過的 hop 桶／Decide／Goal 數字仍在，不是 0。
- **SC-OLD7-NO-FIVE**：OLD7-NO-FIVE 綠。已有 1–7 `.md` 的 fixture 無五站狀態寫入；三 cap 不套（可走既有 T 上限 4）。
- **SC-OLD7-FOLD-RED**：OLD7-FOLD-RED 為預期紅。對該 fixture 寫五站狀態或五站 hop → 紅（RP-15）。
- **SC-OLD7-TOKEN**：OLD7-TOKEN 綠。`scripts/check-gate-tokens.sh`（或同等 token 檢查）仍綠；G1／G2／`ACCEPTED` 檔與 token 仍在；F1 十二群回歸仍可綠。
- **SC-OLD7-SELF**：對 `docs/dev/five-station-f2/` 要求五站自動前進 → 被拒；目錄仍是舊 7 站檔。試體不是把本目錄當 NEW5。
- **SC-DOCTOR**：契約仍 `2.0.0` 且 doctor 可印 `COMPATIBLE` 時，coordinator 拒五站 hop；拒絕理由是路線未宣告／仍舊 7，**不是**「doctor 已綠」。文案「doctor exit 0 所以可以跟 hops」仍紅（F1 S-5.6 回歸）。
- **SC-KNIFE**(G-knife-1)：在 F2 **宣稱完成**之後：無 F3 cut 聲明把新 slug 預設改五站；in-flight fixture 仍舊 7；token 仍在。三把鎖任一被實作成「做了」→ F2 失敗，不是簡化成功。
- **SC-HOLLOW**：下列任一被標「F2 綠」→ 必須非 0／必須被拒：(a) 僅證明 coordinator 檔存在；(b) 僅 `test-five-station-f1.sh` 十二群綠；(c) 僅 NEW5-HOP-OK 綠而 OLD7 組未跑。
- **SC-Q-CARRY**(G-carry-1)：本檔 Real-world 去向覆蓋 Q9–Q24。後站不得把 Q21／Q22／Q23 標可選。
- **SC-PR**：本 PR 的 `git diff --name-only origin/main` 只含 `docs/dev/five-station-f2/2-decision.md` 與 `docs/dev/five-station-f2/2-decision.html`。頂欄 `status: draft`、`verdict` 空。無 G1 PASS。無 STATUS／HISTORY／模板／graph／scripts 新牙／契約 bump。

## Scope & Non-Goals(定稿)
- **In**：1A slug 級只增倉（Q12 persist=0 後 +1 在約束正文、Q15 一次寫）；2C slug ledger＋五問可答、不 bump schema、不鎖鍵；3A 五站桶觸發表（五桶，拒七 stem）；4A 三前置＋marketplace×doctor 約束不是功能；5A 同一電池 dual-path 與具名 CASE（極性＝注入壞行為該格紅）；6A Must-keep 入謂詞＋真計數＋三失敗；7A cache 只選碼、路線認專案樹；8A F2 刀範圍。Q9–Q24 全有去向。本 PR 只 Decision＋html。
- **Out（鎖死，後站不准改成 In）**：
  1. **F3 cut**（新 slug 預設五站；guide／STATUS 用語切五站）。
  2. **把 in-flight 折成五站**（含本目錄、含任何已有 1–7 `.md` 的 slug）。
  3. **刪 G1／G2／`ACCEPTED` token 或檔**。
  4. 放寬 hop≤2／Decide≤1／Goal reopen≤1。
  5. 拿本 slug 或 `five-station-simplify` 當 NEW5 白老鼠。
  6. 把 run 級 `events.jsonl` 當 cap 倉。
  7. 把 doctor 綠／marketplace update／他份 cache 當路線許可（cache 不是 cut）。
  8. 把「檔在」或「F1 綠」當 F2 完成。
  9. 本 PR 實作 coordinator、改 STATUS／HISTORY、填 G1 PASS、合併、改 `_templates/`／`graph.yaml`／既有牙、bump 契約。
  10. 選定 event／倉的 JSON 鍵名或 schema 版本號。

## Owner Calls(自判裁決,已核)

<!-- C 線 OC ledger：使用者只說 Stage1 OK「ok」+ 鎖 Non-Goals 三把／dual-path 可量測／拒檔在＝完。
     落點、事件接法、hop_id、三前置升格、真計數升格、多 cache、一次寫、CASE 名、本 PR 範圍
     都是 owner 自拍。延伸／收窄／升格／流程層逐條標。 -->

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | **計數落點＝slug 級只增倉**（1A）。使用者只把 Q9 移交本站、未選倉；選 slug 倉是 owner 延伸 | 不選則後站可滑回 1B，X5 復活 | `docs/dev/five-station-f2/1-discussion.md:L185` Q9 `[>]`；`five-station-simplify-f0-state-machine.md:L122-L124`。延伸本身 `[Assumption]` | SC-NEW5-RUN2 改觀測點；1B 回流 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-2 | **事件＝獨立 slug ledger，本刀不 bump `agent-event`**（2C）。使用者只鎖「要留＋五問＋不鎖鍵」；「不 bump」是延伸 | 2A 會把 Q18 變成採用端誤紅；本刀不含強迫 bump | `1-discussion.md:L189-L194` Q13／Q14／Q18；`hooks/_doctor_impl.py:L216-L233`。延伸 `[Assumption]` | 改走 2A；採用端 schema 紅被當成誠實成功 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-3 | **`hop_id`＝五站別名＋檔→五站觸發表（五桶），不改 `graph.yaml`**（3A）。使用者只問 F3 前怎麼認；選別名圖＋同站同桶是延伸。standing 釘：拒 B 七 stem | 3B 污染舊 7；3C 偷 F3；七 stem 稀釋 hop≤2 | `1-discussion.md:L187` Q11；`brief-v3.md:L47-L58`；`state-machine.md:L129-L136`。延伸 `[Assumption]` | hop 桶改掛 N7-g1 或七 stem；in-flight 計數互踩；cap 被稀釋 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-4 | **Q17 三前置升格為 Decision**（4A）。使用者在討論標 `[~]`；本檔升格是把假設收成選定 | 少「F3 已 cut」會在 F0–F2 母版軌提前切線 | `1-discussion.md:L193` 期限=F2 Decision；`brief-v3.md:L166`。升格 `[Assumption]` 已到期必須收 | 改成兩前置；F2 期間 live 可評五站 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-5 | **Q10 升格：run 級倉不合法＝X5**。使用者帶假設「是」；本檔選定 1A、棄 1B | 過期不得把 run 級倉當已核——本檔正面選定「不合法」 | `1-discussion.md:L186`；`ledger.py:L3-L6`。升格 | 允許 run 級；SC-NEW5-RUN2 失效 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-6 | **Q19 升格：RP-9／10／11 必須讀真計數**（6A）。使用者帶假設「必須」 | 不升格則 6C 可假裝牙已夠 | `1-discussion.md:L194`；`five_station_f1.py:L327-L333`。升格 | F2 可只留字樣牙；live 第三次仍假第一次 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-7 | **plugin root 從屬專案樹路線 SoT**（7A）。cache 只選本 process 讀哪份 hops 碼，不是路線許可。使用者只移交 Q20；「碼／路分家」是延伸。standing 吸收 B「認專案樹不認 host cache」 | 7B 是遠端改線變種；把 cache 當 cut 會讓 4A 變空 | `1-discussion.md:L196` Q20；`brief-v3.md:L168`。延伸 `[Assumption]` | 改掃最新 cache 或把 marketplace／COMPATIBLE 當 cut；同一 repo 被他機 hops 拖走 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-8 | **Goal+Decide 兩個計數同一次 mutation 寫入**。使用者只問是否必須同一落點；「一次寫」是延伸 | 分兩次寫可讓 Goal 重開躲掉 Decide cap | `1-discussion.md:L191` Q15；`state-machine.md:L137`。延伸 `[Assumption]` | 分倉；NEW5-GOAL-2 可綠而 Decide 被躲 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-9 | **把 AC-9 收成具名 CASE 表＋同一入口**（上表 13 列，只准加不准減）。使用者要「measurable SC for dual-path」；CASE 名與「預期紅」格子是延伸。standing 釘極性：注入壞行為 → 該格紅，不是「拒 hop 算綠」 | 不具名則後站可把紅格改成可選或拆成兩支腳本；極性反了會把壞行為測成綠 | `1-discussion.md:L252-L255` AC-9；使用者 C-line brief。延伸 `[Assumption]` | CASE 改名消失；SC-HOLLOW 對不到；紅格被改成拒 hop 綠 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-10 | 本 Decision hop **不**跑 `status-update.sh`、不改 HISTORY、不改 1-discussion 頂欄、**不發明 G1 PASS**、不合併、不寫 coordinator。標**流程層** | 母版 STATUS 只在整合分支維護；使用者：draft、No G1 PASS、ONLY 2-decision+html | `docs/dev/STATUS.md:L10-L26`；本 hop brief | PR 帶 STATUS 或自填 PASS，與並行 A／B session 互蓋 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-11 | **Q12 已進 Decision 約束正文**：某 `hop_id` **第一次成功 persist＝0**；之後每一次 persist 該桶 +1。第一次寫不算進 hop≤2。使用者只鎖「計數看寫入、不看模型名」；切在 persist 是延伸。standing：不得只寫在本 OC | 不切則「開檔就算一次」或「換模型再寫不算」都會漂；只寫 OC 會被後站當可選帳 | `1-discussion.md:L188` Q12；`state-machine.md:L129` 第一次寫不算。延伸 `[Assumption]` | 初寫被算進 cap，或換模型可無限重寫 | ✅ Owner PASS human:rick @ 2026-09-14 |
| OC-12 | **F2 coordinator 準存在、但 F3 前對 live slug 禁評五站謂詞**（只打合成 fixture）。這是對 4A 的收窄：碼可以合進 plugin，預設路線仍舊 7 | 使用者鎖「F2 寫 coordinator」又鎖「F3 前新軌舊 7」；不收窄會被讀成 8B | `brief-v3.md:L176-L180` F2 做／不做；`:L166` F0–F2 新開軌仍舊 7。收窄 `[Assumption]` | 碼一合進就對 live 切五站＝偷 F3 | ✅ Owner PASS human:rick @ 2026-09-14 |

### 內部技術選擇(下層,告知即可)
- 契約維持 `2.0.0`；本 hop 不 bump plugin／`devflow-contract.json`／`agent-event`。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口（Owner「ok」）。
- 審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。G1 經 `scripts/devflow_gate.py write` 落頂欄；審頁重生。不產 G1 勾選 twin。
- 不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。
- 原文獨立收斂；standing soft-fix 才讀 A／B 吸收：A＝中途等人拒法；B＝marketplace×doctor 約束句＋認專案樹。不採 B 七 stem。
- slug ledger 的具體路徑／檔名交 4-spec，本檔只鎖「slug 級、只增、可指、五問可答」。
- 單一電池入口的腳本名交 4-spec，本檔只鎖「同一 process、缺一路即非 0」。
- 舊 7 in-flight 仍走既有 `graph.yaml` 與 T 嘗試上限 4。
- F1 字樣正則牙可留作回歸；不得替代 1A 倉。
- Backlog A「下一刀 F1」保持 stale 事實，本 PR 不改看板。

## ADR 晉升檢查
- 難逆轉:否（G3 未過可改 Decision／OC；本 hop 零 runtime；F3 才切新 slug 預設）
- 反直覺:是（F2 寫 coordinator 卻對 live 仍舊 7；檔在不是完；doctor 綠不是通行證；不 bump 事件 schema）
- 真 trade-off:是（slug 倉 vs run ledger／X5；不 bump vs 觀測統一；雙路電池 vs 假綠；freeze 觀測 vs 立刻切五站）
→ 晉升:**否**（難逆轉未中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-14 | Owner Stage1 OK「ok」+ C-line anti-hollow dispatch：鎖 Non-Goals F3 cut／in-flight fold／token delete；measurable SC for dual-path selftest green；OC ledger for owner extensions；reject files-exist=F2-done。八點對 1A…8A。
- Stage 1 改口 | 2026-09-14 | 1-discussion 仍 draft、當時寫不送 G1；Owner「ok」後開本站。不回改正本討論。
- 獨立於 A／B（原文） | 2026-09-14 | C 線當時未讀他線 Stage 2；只讀 1-discussion＋brief §7 F2＋狀態機＋F1 annex／RP＋模板。
- Owner standing soft-fix | 2026-09-14 | Winner C 全票 #330。釘：檔→五站觸發表（五桶，拒 B 2A 七 stem）；7A 從屬專案樹 SoT（cache 只選碼）；Q12 persist=0/+1 進約束正文；CASE 極性＝注入壞行為該格紅；吸收 B marketplace×doctor 約束句、A 中途等人拒法。C 線長處全留。不發明 G1 PASS。
- Q10／Q17／Q19 對帳 | 2026-09-14 | 三條 `[~]` 到期收進 Decision（OC-4／5／6），不再當「仍待驗可改口」。
- 自檢七掃 | 2026-09-14 | ①每案優劣有依據欄（空格標 `[Assumption]`）。②Goals G-locus／honest／trap／self／knife／obs／carry／dual／keep 進 Decision／SC；漏項進 Non-Goals。③`[>]` Q9–Q16／Q18／Q20 皆本方案處理（本 slug 後站，不是另開 slug）。④SC 皆具名 CASE／exit／檔集；紅格極性＝注入。⑤Rejected 無空棄因（含七 stem）。⑥八決策點由 C-line brief 確認；OC-1／2／3／7／8／9／11 延伸、OC-4／5／6 升格、OC-12 收窄、OC-10 流程層，皆可回溯決策點。⑦既有脈絡是對帳不是外移 schema。圖上 1A–8A 標選定，Rejected 未上圖。
- 本 hop 不送 G1 | 2026-09-14 | Decision hop：`verdict` 空；OC 全「待人審」；不跑 N8 三連動。standing 合稿後仍不發明 PASS。
- G1 | 2026-09-14 | Human G1 PASS + OC-1…OC-12 Owner PASS @ 2026-09-14 Asia/Taipei。owner chat「可以」。未發明新 OC 答案；看板依 Decision 原文標 Owner PASSed。基準 #330（`dbf3d86`）／#332 STATUS Stage2（`3036eda`）。owner 自審(有記錄)；reviewers: [user]；operator tony 經 `scripts/devflow_gate.py write` 落頂欄。未發明 G2／G3 PASS。不開 Stage 3／4。
