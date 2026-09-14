---
feature: five-station-f2
stage: 2-decision
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 2. 收斂 — 五站 F2（Implementer A：coordinator 自動前進 × Must-keep fail-closed）

> 把 `1-discussion.md` 收成一個選定方案。**不發明 G1 PASS**：頂欄 `status: draft`、`verdict` 空、`reviewers: []`。Lane = **full**。本 hop 只落 `2-decision.md` + 審頁 html。不改 STATUS／HISTORY、不合併、不實作 F1／coordinator、不切 F3、不刪 G1／G2／`ACCEPTED`。
> Stage 1 頂欄仍 `status: draft`、當時寫「不送 G1／不宣稱 Human Stage1 PASS」。Owner Human Stage1 direction OK（chat「ok」2026-09-14）後開本站。1-discussion 留當時說法；改口記本檔。
> F0 十條已鎖，本檔**不重開**：五站別名、殺例行中閘、Ship 唯人、條件 A/B、Must-keep、F1→F3、本 slug 走舊 7。翻任一條 = 新 brief。
> A 線主軸：**coordinator 怎麼 hop，且 Must-keep 紅時 fail-closed**。三失敗不得當成功：(1)謂詞真仍等人；(2)Must-keep 紅仍 hop；(3)機械綠 → Ship Done。事件能答誰／從哪到哪／謂詞／哪只 cap／Escalated，**不鎖鍵名**（OC-3）。獨立於 B／C，未讀他線 Stage 2。

## Real-world 去向
| 引用（Stage 1 原文片段） | 去向 | 理由 |
|---|---|---|
| 「謂詞真仍等人、Must-keep 紅仍 hop、機械綠當 Ship Done，會比舊 7 更快假完成」 | 本方案處理 | 1A＋2A＋3A；G-keep-1／Q22 |
| Journey「chat『可以開下一站』；謂詞真也等人；Must-keep 紅也可被准」 | 本方案處理 | 1A＋2A：不准「要不要繼續」；紅則停修 |
| 「自動前進謂詞必須含完整度；Must-keep 未綠不得 hop」 | 本方案處理 | 2A；不是未定案 |
| 「Runtime:謂詞真 hop、假停修，不准問『要不要繼續』；Ship 無自動前進；代寫 verdict: PASS=違 OC-3」 | 本方案處理 | 1A＋3A；brief §4／狀態機 §2.5 |
| 「前進／latch／cap 觸發都要留機械紀錄…能回答誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated；不鎖定 JSON／YAML 鍵名」 | 本方案處理 | 4A；G-obs-1／Q23。鍵名仍 OPEN |
| 「coordinator 評五站謂詞之前，先問路線…doctor 綠不是這道問的答案」 | 本方案處理 | 5A；Q17 三前置升成本 Decision |
| 「本 slug 自己走到 G1／G2／G3 時仍是舊 7；沒有五站狀態寫入」 | 本方案處理 | 5A＋6A；G-self-1／Q4 |
| 「F2 做完之後，G1／G2／ACCEPTED token 與檔仍在；沒有 F3 cut；沒有 in-flight 被折」 | 本方案處理 | 6A；G-knife-1 |
| 「檔在或 F1 綠 ≠ F2 完」／「同一電池 NEW5+OLD7」 | 刻意維持 | Q21 已解；後站不得標可選。電池形狀不由 A 選定 |
| 「三個計數器的落點在哪」Q9–Q16 | 仍待驗 | A 不選倉／鍵／hop_id／schema bump。B 線 |
| 「run 級 events 新 run_id 歸零是否 X5」Q10 `[~]` | 仍待驗 | 過期不得把 run 級倉當已核。本檔不選倉 |
| 「F2 必須餵真計數給 RP-9／10／11」Q19 `[~]` | 仍待驗 | A 不發明計數倉。過期擋「牙已夠」 |
| 「marketplace update 單獨發生，不足以改採用端路線」 | 仍待驗 | C 線升級陷阱。5A 只鎖 coordinator 不得用綠當通行證 |
| 「採用端更新了 plugin、契約仍 2.0.0」G-trap-1 | 仍待驗 | C 線。SLOT 已在 F1 annex；本檔不寫牙 |
| 「Cursor／Claude／Codex 各一份 plugin cache」Q20 | 仍待驗 | C 線。不是 A 的 hop 規則 |
| 「F2 若 bump agent_event…doctor 變 INCOMPATIBLE」Q18 | 仍待驗 | 與 Q13 綁；A 不 bump schema |
| Workaround「owner 用 chat 當 hop 開關」 | 本方案處理 | 1A：chat 不是 hop 謂詞 |
| Workaround「STATUS／HISTORY 當 hop log」 | 本方案處理 | 4A：看板不是事件正本；Q24 stale |
| Exception「舊 7 與 in-flight 不套三 cap」 | 刻意維持 | Q6 已鎖；5A 放手舊 7 |
| Exception「F2 可以寫 coordinator 碼，但 F3 前預設仍舊 7」 | 本方案處理 | 6A：本 PR 連碼都不寫；預設仍舊 7 |
| Exception「NEW5 試體是合成 fixture，不是本 slug」 | 本方案處理 | 6A／OC-7；過期擋把本目錄當白老鼠 |
| 「本 hop 不改模板、不送 G1」 | 刻意維持 | 6A：本 PR 只 Decision＋html |

## Approaches Considered

### 決策點 1：謂詞真時要不要等人（失敗 1）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 1A | **謂詞全真 ∧ latch 假 → 立刻 hop**。不准留下「要不要繼續」「請人審 A4／A7」。假 → 停該站修，不是改問人。latch 真才進 HumanWait | 對準 G-keep-1(1)／brief §4；殺掉 Journey 的 chat 開關 | 寫手少一次「確認再走」的安全感 | 低 | `notes/design/five-station-simplify-brief-v3.md:L127-L129`；`notes/design/five-station-simplify-f0-state-machine.md:L54-L55`；`docs/dev/five-station-f2/1-discussion.md:L155`；同檔 `:L94` Step 7。成本 `[Assumption]` |
| 1B | **謂詞真仍等人按「繼續」**（把 chat 開關寫進 runtime） | 跟現況 Journey 相容；owner 可在中間攔 | 失敗 1 本身；例行停從 G1 搬家沒消失；G-keep-1 反面 | 低 | `docs/dev/five-station-f2/1-discussion.md:L94`；同檔 `:L256` AC-10(1)；`notes/design/five-station-simplify-f0-state-machine.md:L199` X6 是「latch 未命中卻等人」，1B 就是這條 |
| 1C | **維持七站例行 G1／G2 人停**，F2 不接自動前進 | 零 runtime 風險 | 違 F2 刀；痛原封不動；G-knife-1 的「接自動前進」落空 | 低 | `notes/design/five-station-simplify-brief-v3.md:L176-L179` F2=Coordinator 接自動前進；`docs/dev/five-station-f2/1-discussion.md:L179` Q3 |

### 決策點 2：Must-keep 紅能不能 hop（失敗 2）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 2A | **Must-keep 綠是 hop 謂詞的一部分（fail-closed）**。任一條紅（T 缺 Verify、無 RED、reviewer=implementer、S 含 TBD、Agent 代寫判定…）→ 拒 hop、停該站修。完整度不是 hop 後再查 | 對準 Owner-locked「未綠不得 hop」；擋「已經五站了所以可省」 | 中間站看起來「比較慢」——慢在修完整度，不是等人 | 中 | `docs/dev/five-station-f2/1-discussion.md:L161`；同檔 `:L208`；`notes/design/five-station-simplify-brief-v3.md:L135-L158`；`notes/design/five-station-simplify-f1-rp-min-set.md:L7-L23` RP-1…RP-3／RP-16。成本 `[Assumption]` |
| 2B | **Must-keep 紅仍 hop，只記警告** | hop 看起來快；警告以後再補 | 比舊 7 更快假完成；失敗 2 本身；警告不是 fail-closed | 低 | `docs/dev/five-station-f2/1-discussion.md:L20`；同檔 `:L174`「不把 hop 比較快解讀成 Must-keep 也可以 hop 掉」；同檔 `:L256` AC-10(2) |
| 2C | **五站之後 Must-keep 改可選**（「已經簡化了」） | Build 短；少牙 | 少一條 = 違 brief 不是簡化成功；F1 RP 最小集被掏空 | 高 | `notes/design/five-station-simplify-brief-v3.md:L158`；`notes/design/five-station-simplify-f1-dual-read-annex.md:L36` RP 只准加不准減；`docs/dev/five-station-f2/1-discussion.md:L56` |

### 決策點 3：機械綠能不能當 Ship Done（失敗 3）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 3A | **Ship 沒有自動前進**。機械全綠仍必須 HumanWait（A10 latch=是）。coordinator／Agent 代寫 `verdict: PASS` = 未寫（RP-8／RP-16）。人寫頂欄 `PASS` 才准 Done | 對準 brief OC-3／狀態機 §2.5；擋偷章 | Ship 仍等人——這是唯一預設人停，不是回歸 | 低 | `notes/design/five-station-simplify-brief-v3.md:L39`；同檔 `:L119-L120`；`notes/design/five-station-simplify-f0-state-machine.md:L110-L120`；`notes/design/five-station-simplify-f1-rp-min-set.md:L14` RP-8；`:L23` RP-16 |
| 3B | **機械全綠自動標 Done** | 無人停；F2 看起來「全自動」 | 失敗 3 本身；偷 OC-3；出貨樹≠審過的樹 | 低 | `docs/dev/five-station-f2/1-discussion.md:L155`；同檔 `:L256` AC-10(3)；`notes/design/five-station-simplify-f0-state-machine.md:L189-L193` X1 |
| 3C | **coordinator 機械綠時代寫 `verdict: PASS`** | 頂欄有字；檢查看起來過 | 代寫=未寫；違「誰准寫判定=人」；RP-16 必紅 | 低 | `notes/design/five-station-simplify-brief-v3.md:L127-L128`；`notes/design/five-station-simplify-f0-state-machine.md:L187`；`docs/dev/five-station-f2/1-discussion.md:L71` coordinator **禁**寫判定 |

### 決策點 4：事件記什麼、能不能鎖鍵（G-obs-1／Q23）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 4A | **五語意槽必須可答**：誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated。前進、latch 開火、cap 觸發各至少一筆人指得到的機械紀錄。**不鎖** JSON／YAML 鍵名、`event_type`、sidecar 路徑、schema 版本（OC-3） | 對準 Q23／F1 OC-3；後站能驗「指得到」而不偷做 annex | 落點（倉／鍵／hop_id）仍 OPEN；本檔驗不了 live 第三次 | 低 | `docs/dev/five-station-f2/1-discussion.md:L152`；同檔 `:L199` Q23；同檔 `:L210`；`notes/design/five-station-simplify-brief-v3.md:L133`；`notes/design/five-station-simplify-f1-dual-read-annex.md:L1-L3` |
| 4B | **本檔鎖鍵名**（例如 `event_type=hop_advanced`、寫進 run 級 `events.jsonl`） | 後站少一次收斂 | 偷做 annex／Q13；可能把 run 級倉升成已核（Q10）；違 OC-3 | 高 | `docs/dev/five-station-f2/1-discussion.md:L189` Q13 `[>]`；同檔 `:L186` Q10 `[~]`；`notes/design/five-station-simplify-f1-dual-read-annex.md:L36` 計數落點不在 F1 鎖定 |
| 4C | **不留機械紀錄**；chat／STATUS／HISTORY 當 hop log | 零 schema 風險 | 看板可過期（Q24 Backlog A 仍寫下一刀 F1）；人指不到五問；G-obs-1 落空 | 低 | `docs/dev/five-station-f2/1-discussion.md:L101`；同檔 `:L244-L247` AC-7「不是只靠 chat；不是 attempt_completed 冒充」；同檔 `:L200` Q24 |

### 決策點 5：何時准評五站謂詞（Q17＋本 slug freeze）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 5A | **三前置全要**：契約已宣告 2.1.0 ∧ 非 in-flight ∧ 預設路線只在 F3 後。任一假 → 放手舊 7，**不建立五站機**。doctor `COMPATIBLE`／exit 0 **不是**這道問的答案。本目錄已有 `1-discussion.md` = in-flight，對自己求五站 hop 必須拒 | 對準 Q17 過期期限=F2 Decision；擋把本 slug 折成五站；SLOT-DOCTOR-GREEN-MEANS 變成行為不只文案 | 採用升級細節（多 cache、2.0.0+五站 hops 牙形）仍交 C；本檔不寫牙 | 中 | `docs/dev/five-station-f2/1-discussion.md:L193` Q17；同檔 `:L160`；同檔 `:L180` Q4；`notes/design/five-station-simplify-f0-state-machine.md:L49-L50`；`notes/design/five-station-simplify-f1-dual-read-annex.md:L26-L32`；`hooks/_doctor_impl.py:L193-L202`。牙形 `[Assumption]`（C／後站） |
| 5B | **doctor 綠即可開火五站謂詞** | 最少一問；跟「更新後 hops 已換」的直覺一致 | 綠只證明握手；SLOT 變成裝飾；舊 7 slug 會被折 | 低 | `docs/dev/five-station-f2/1-discussion.md:L147` G-honest-1；同檔 `:L42` SLOT-DOCTOR-GREEN-MEANS；`hooks/_doctor_impl.py:L193-L202` |
| 5C | **本 slug 當 NEW5 白老鼠**（對自己建五站機驗 hop） | 立刻看到 1A–3A 活著 | 違 G-self-1／X4／RP-15；觀測被自己污染；Assumption「NEW5=合成 fixture」過期擋 | 高 | `docs/dev/five-station-f2/1-discussion.md:L170`；同檔 `:L217`；`notes/design/five-station-simplify-f0-state-machine.md:L196` X4；`notes/design/five-station-simplify-f1-rp-min-set.md:L22` RP-15 |

### 決策點 6：本 PR 與 F2 刀切到哪
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| 6A | **本 PR 只 Decision＋審頁 html**。不實作 coordinator、不寫 F1 牙、不 bump schema、不切 F3、不刪 token、不改 STATUS／HISTORY、**不發明 G1 PASS**。F2 刀（後站）仍是 coordinator＋hop／latch／cap 事件；F3 才切新 slug 預設 | 對準使用者本 hop；本 slug 自己當 freeze 樣本；A／B／C 不互蓋看板 | 自動前進要到後站才有碼；痛暫時還在 | 低 | 本 hop brief；`notes/design/five-station-simplify-brief-v3.md:L176-L180`；`docs/dev/five-station-f2/1-discussion.md:L166-L168`；`docs/dev/STATUS.md:L10-L16` feature branch 不碰看板。本 PR 檔集可 `git diff --name-only` 核對 |
| 6B | **本 PR 順便寫 coordinator 碼** | 少一次 hop；1A–3A 立刻可跑 | 未過 G1 就施工；違「只 Decision」；還可能偷選 Q13 鍵名 | 高 | `docs/dev/five-station-f2/1-discussion.md:L12` 本檔只 Stage 1 時已禁施工；使用者：No F1 implementation／no F3 cut／Produce ONLY 2-decision |
| 6C | **併刀 F3 cut**（新 slug 預設五站＋本檔當第一隻） | 看起來一次做完 | 雙路線、in-flight、採用端同時爆；違「不准併刀」 | 高 | `notes/design/five-station-simplify-brief-v3.md:L173` 不准併刀；同檔 `:L180` F3 才 Cut |

## 方案架構圖
```
[1A] 謂詞真立刻 hop(選定)
[2A] Must-keep 紅拒 hop(選定)
[3A] 機械綠仍 HumanWait(選定)
[4A] 五語意槽不鎖鍵(選定)
[5A] 三前置後才評五站(選定)
[6A] 本 PR 只 Decision(選定)
```

## Decision
採 **1A+2A+3A+4A+5A+6A**：coordinator 讀 brief §3 謂詞，**Must-keep 綠是 hop 謂詞的一部分（fail-closed）**。謂詞全真且 latch 假 → 立刻 hop，不准留下「要不要繼續」。Must-keep 任一條紅 → 拒 hop、停該站修，不准改問人。Ship 機械全綠仍必須 HumanWait；coordinator／Agent 代寫 `verdict: PASS` 或 `ACCEPTED` = 未寫。前進／latch 開火／cap 觸發各留人指得到的機械紀錄，必須能答**誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated**；不鎖 JSON／YAML 鍵名。開火五站謂詞前先問路線：未宣告 2.1.0、或 in-flight、或 F3 前母版新軌 → 放手舊 7、不建立五站機；doctor 綠不是這道問的答案。本 slug 已 in-flight，對自己求五站 hop 必須拒。本 PR 只落 Decision＋審頁，不實作 coordinator、不寫 F1 牙、不切 F3、不改 STATUS、不發明 G1 PASS。不選 1B／1C／2B／2C／3B／3C／4B／4C／5B／5C／6B／6C。

## Decision 約束（後站不准改成可選）
1. **三失敗各自可紅，不得當 F2 成功**：(1)謂詞全真且 latch 假，卻仍留下「要不要繼續」；(2)Must-keep 紅（例如 T 缺 Verify）仍 hop；(3)機械全綠且無人寫 `verdict: PASS` 卻標 Ship Done。
2. **Must-keep M1–M16 少一條 = 違 brief**。自動前進謂詞必須含完整度。不得寫「已經五站了所以可省」。
3. **Ship 無自動前進**。A10 latch=是 → 機械綠仍 HumanWait。代寫頂欄判定 = 未寫（RP-8／RP-16）。
4. **事件五語意槽鎖定、鍵名不鎖**（OC-3）。本檔不選定 `event_type`、sidecar、schema 版本、計數倉。
5. **三前置全要**才准評五站謂詞：2.1.0 已宣告 ∧ 非 in-flight ∧ 預設只在 F3 後。doctor 綠 ≠ 路線許可。
6. **本 slug live freeze**：目錄已有 1–7 `.md` → 整段舊 7 到 Ship；不得寫入五站狀態（RP-15）。
7. **計數落點 Q9–Q16／Q10／Q19 維持未鎖**。A 線不選倉。不得把 run 級倉寫成已核。
8. **dual-path（Q21）不得標可選**。檔在／F1 綠／單路開心 hop ≠ F2 完。電池形狀不由本檔選定。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| 1B 謂詞真仍等人 | 失敗 1 本身；chat 開關寫進 runtime；X6。 |
| 1C 不接自動前進 | 違 F2 刀；痛原封不動。 |
| 2B 紅了仍 hop＋警告 | 比舊 7 更快假完成；警告不是 fail-closed。 |
| 2C Must-keep 可選 | 少一條=違 brief；掏空 F1 RP 最小集。 |
| 3B 機械綠自動 Done | 失敗 3；偷 OC-3；X1。 |
| 3C coordinator 代寫 PASS | 誰准寫判定=人；RP-16 視為未寫。 |
| 4B 本檔鎖鍵名 | 偷做 annex／Q13；可能把 Q10 升成已核。 |
| 4C chat／STATUS 當 hop log | 看板可 stale；五問指不到；AC-7 反面。 |
| 5B doctor 綠就開火 | 綠只證明握手；舊 7 會被折。 |
| 5C 本 slug 當 NEW5 | X4／RP-15；觀測自污；過期擋。 |
| 6B 本 PR 寫 coordinator | 未過 G1 就施工；違「只 Decision」。 |
| 6C 併刀 F3 | brief 不准併刀；in-flight 與採用端同時爆。 |
| 重開 F0 十條 | 翻任一條 = 新 brief。 |
| 等人在 hop 中間「確認一下」 | 1B 的客氣說法；latch 未命中卻問人。 |
| 選定 run 級 `events.jsonl` 當 cap 倉 | Q10 仍是假設；A 不選倉。 |

## Rationale
F2 的痛不是「沒有檔」，是 **hop 規則與完整度脫鉤**。現況 Journey 用 chat 當下一站開關：謂詞真也等、Must-keep 紅也可被准。若 F2 只接「比較快的 hop」而不把 Must-keep 寫進謂詞，假完成會比舊 7 更快——這是失敗 2。若接了 hop 卻仍在中間問「要不要繼續」，失敗 1 原封不動。若機械綠就標 Ship Done，失敗 3 偷走 OC-3。

1A＋2A＋3A 是同一條規則的三面，不能拆開只做最快的那面。latch 未命中 → 禁問人；latch 命中（A10／B1…）→ 必須 HumanWait，即使機械全綠。Must-keep 紅 → 停修，不是警告、不是可選。

4A 把「要留」收成可驗的五問，但不鎖鍵——鎖鍵就是偷做 F1 annex／Q13。4C 已被 Q24 證偽：STATUS Backlog A 仍寫「下一刀 F1」，而 F1 已 G3 PASS。

5A 是 hop 規則的前門。沒有這扇門，1A 會被讀成「對本 slug、對未 upgrade 採用端也自動前進」。doctor 綠不是前門的鑰匙。5C 拿自己當白老鼠會讓「F0–F2 仍舊 7」的觀測禁令失效。

6A 把本 hop 停在方向核准之前。A 線不選計數倉、不寫升級牙、不施工，讓 B／C 獨立收斂 Q9–Q16／Q18／Q20。

## 既有脈絡
對帳快照（2026-09-14 tip `838e20a`，Stage 1-B＋soft-fix 已合 `#325`，STATUS Active 已開 `#328`）：

| 層 | 現況 | 本 Decision 怎麼用 |
|---|---|---|
| F0 brief＋狀態機 | Owner 已核；十條鎖死；§4 runtime 從 F2 落地 | 本檔只收 hop 規則；不重開、不寫碼 |
| F1 annex／RP | SLOT 九槽＋RP-1…16 只准加；計數落點明文交 F2 | 4A 不鎖鍵；2A 引用 RP 當完整度牙，不減列 |
| Stage 1 `#325` | 1-discussion status=draft；winner B soft-fixed | 留當時說法；chat「ok」後本檔改口 |
| 契約／runtime | `2.0.0`；doctor 只握手版本 | 5A：綠 ≠ 准評五站 |
| 現行事件 | `stage` 正則舊 7；無 hop／latch／cap 型別；ledger 是 run 級 | 4A 只鎖五問；不選 Q13／Q14 接法 |
| F1 cap 牙 | 咬 fixture 字樣「第 3 次」，不是倉 | A 不選倉；Q19 仍待驗 |
| 本 slug STATUS | Active 在 1-discussion；Gates 全白 | 本 branch **不**改這列（OC-4） |
| 本資料夾 | 已有 `1-discussion.md` | 已 in-flight；出貨走舊 7 |

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 後站把三失敗標成可選，或只測「檔在」當 F2 完 | Decision 約束 1／8；SC-1…3；4-spec 出現「可選 Must-keep／可選等人」→ 擋本 slug G2（OC-2） |
| coordinator 實作時 hop 先走、Must-keep 後查 | 2A：完整度在謂詞裡，不是 hop 後警告。2B 進 Rejected |
| 本檔鎖了 `event_type` 或 run 級倉 | 4A／OC-3／OC-6：鍵名與倉維持 OPEN。出現選定鍵名 → 本 G1 應打回 |
| 有人用 doctor 綠當 5A 的通行證 | 5A＋SC-5：拒絕理由必須是路線未宣告／仍舊 7，不是「doctor 已綠」 |
| 本 slug 被拿去試五站 hop | 5A／SC-6：目錄已存在 = freeze。五站機寫入 = RP-15 |
| Q10 被升成「F2 已決定用／不用 run 級倉」 | OC-6：本檔不選倉。過期不得當已核 |
| 本 hop 被當成已過 G1 或已落地 coordinator | 頂欄 draft／verdict 空；SC-10／SC-7。不發明 PASS |
| A／B／C 互蓋 STATUS | OC-4 流程層：本 PR 不跑 `status-update.sh` |
| 客氣問「請 owner 看一下任務板」 | 1A：A8／A9 latch=否 → 不得因想給人看而停（狀態機 §2.4） |

## Success Criteria
每條都要能用「對照稿／拒絕理由／檔集」核對。7-review 對這張表，不對口頭「已經會自動前進了」。本 hop 不跑 coordinator；對照稿後續造。

- SC-1(失敗 1／G-keep-1.1)：五站試體謂詞全真、latch 假、Must-keep 綠 → 前進紀錄**沒有**「要不要繼續」「請人審 A4／A7／提交判定」。對照：1B 那種「謂詞真仍等人」稿必須紅。
- SC-2(失敗 2／G-keep-1.2)：Must-keep 紅（對照 F1 `rp-01`：T 缺 Verify）仍求 hop → 被拒；狀態留在該站；沒有下一站檔被寫出。
- SC-3(失敗 3／G-keep-1.3)：機械全綠、7-review 頂欄無人類 `verdict: PASS` → 不得標 Done；必須 HumanWait。coordinator 寫入的 `PASS` 視為未寫（RP-8／RP-16）。
- SC-4(G-obs-1)：一次 hop 成功、一次 latch 開火、一次 cap 用盡 → 三筆都能指出，且能答誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated。不要求特定鍵名。`attempt_completed` 或 chat 不得冒充。
- SC-5(G-honest-1／5A)：契約仍 `2.0.0` 且 doctor 印 `COMPATIBLE`，求五站 hop → 拒。理由是路線未宣告／仍舊 7，**不是**「doctor 已綠」。
- SC-6(G-self-1)：對 `docs/dev/five-station-f2/` 求五站自動前進 → 跳不過。目錄無五站狀態寫入；仍是舊 7 站檔。
- SC-7(G-knife-1＋本 PR)：本 PR 的 `git diff --name-only origin/main` 只含 `docs/dev/five-station-f2/2-decision.md` 與 `docs/dev/five-station-f2/2-decision.html`。token 仍在；無 F3 cut；無 coordinator 實作檔。
- SC-8(G-carry-1)：本檔 Real-world 去向覆蓋 Stage 1 高影響 Goal／`[>]`／`[~]`。Q9–Q16／Q10／Q18–Q20／Q19 有「仍待驗」，沒有消失、沒有被 A 偷選。
- SC-9(鍵名不鎖)：本檔 Decision／OC **沒有**把某個 `event_type=`、JSON key、sidecar 路徑、schema 版本號標成選定。出現選定鍵名 → 本 G1 應打回。
- SC-10(不發明 G1 PASS)：本檔頂欄 `status: draft`、`verdict` 空。把本 hop 寫成 G1 PASS → 違 OC-4。
- SC-11(Q10／Q19 不升格)：本檔任何「計數倉選哪一種」句仍標仍待驗或 `[Assumption]`。把 run 級倉或「牙已夠不必倉」寫成已核 → 本 G1 應打回。
- SC-12(dual-path 不標可選)：後站文檔若把 Q21「同一電池兩路可獨立紅」標成可選，或把「檔在／F1 綠」寫成 F2 完 → 擋本 slug G2。

## Scope & Non-Goals(定稿)
- In：1A 謂詞真立刻 hop；2A Must-keep 納入 hop 謂詞 fail-closed；3A Ship 機械綠仍 HumanWait、代寫=未寫；4A 五語意槽可答、不鎖鍵；5A 三前置＋doctor 綠不是通行證＋本 slug freeze；6A 本 PR 只 Decision＋html。Decision 約束 1–8。三失敗不可選。Q17 升成本 Decision。Q21／Q22／Q23 保持已解、不得標可選。
- Out：1B／1C；2B／2C；3B／3C；4B／4C；5B／5C；6B／6C；重開 F0 十條；刪 G1／G2／`ACCEPTED`；本 PR 實作 coordinator／F1 牙／F3 cut；本 PR 改 STATUS／HISTORY／模板／graph／既有牙／契約版本；本 PR 填 G1 PASS；本 PR 合併；拿本 slug 當 NEW5；選定計數倉／event 鍵名／schema bump；選定 dual-path 電池腳本；選定 marketplace 多 cache 認哪一份（Q20）；把 Q10／Q19 升成已核。

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | **Must-keep 綠寫進 hop 謂詞**（fail-closed），不是 hop 後再查、不是警告。使用者已鎖「未綠不得 hop」；「謂詞本身含完整度、紅則停修不准問人」是 owner 延伸 | 少這句，2A 會被實作成 2B | `docs/dev/five-station-f2/1-discussion.md:L161`；同檔 `:L208`。延伸本身 `[Assumption]` | SC-2 變警告；失敗 2 回流 | 待人審 |
| OC-2 | 三失敗（Q22）寫進 Decision 約束，後站標可選 → 擋本 slug G2。使用者只把 Q22 標已解；「後站不得改可選」是延伸 | 討論已寫後站不得把三失敗標可選 | `docs/dev/five-station-f2/1-discussion.md:L199`；同檔 `:L216`。延伸 `[Assumption]` | 只測檔在也可稱 F2 完 | 待人審 |
| OC-3 | 事件**五語意槽鎖定、鍵名不鎖**。不選定 `event_type`、sidecar、schema 版本。這是對「事件要留」的收窄（能答五問 ≠ 已選 Q13） | 鎖鍵=偷做 annex；與 4A／6A 衝突 | `docs/dev/five-station-f2/1-discussion.md:L199` Q23；同檔 `:L210`；`notes/design/five-station-simplify-f1-dual-read-annex.md:L1-L3` | Scope 膨脹進 schema；SC-9 要重寫 | 待人審 |
| OC-4 | 本 Decision hop **不**跑 `status-update.sh`、不改 HISTORY、不改 1-discussion 頂欄、不把本檔 `verdict` 寫成 PASS、**不發明 G1 PASS**、**不合併**、不實作 F1／coordinator／F3。標**流程層** | 母版 STATUS 只在整合分支維護；使用者禁發明 G1 PASS | `docs/dev/STATUS.md:L10-L16`；本 hop brief | PR 帶 STATUS 或自填 PASS，與並行 B／C 互蓋 | 待人審 |
| OC-5 | Q17 `[~]` **升成本 Decision**：三前置全要才准評五站謂詞；doctor 綠不是第四條。使用者只被問到假設；「三條全要」是把過期期限收到本站 | 期限=F2 Decision；不收會讓 1A 誤套舊 7／本 slug | `docs/dev/five-station-f2/1-discussion.md:L193`；同檔 `:L160`。升格本身 `[Assumption]`（採討論暫定值） | 5B 回流；本 slug 可被折 | 待人審 |
| OC-6 | Q9–Q16／Q10／Q19 **維持未鎖**（仍待驗）。A 線不選計數倉、不餵真計數、不宣告 X5 已核。這是對 4A「要留紀錄」的收窄 | 落點是 B 線；本檔若選倉就不是獨立 A | `docs/dev/five-station-f2/1-discussion.md:L185-L192`；同檔 `:L214`。收窄 `[Assumption]` | A 偷選 run 級倉；與 B 衝突 | 待人審 |
| OC-7 | NEW5 只准**合成 fixture**；本目錄與 `five-station-simplify` 不得當 hop 試體。使用者 Non-Goal 已寫；「Files 路徑不含本目錄站檔」是收窄 | Assumption 過期擋把本目錄當白老鼠 | `docs/dev/five-station-f2/1-discussion.md:L113`；同檔 `:L170`。收窄 `[Assumption]` | 5C 回流；觀測自污 | 待人審 |
| OC-8 | Success Criteria 用「對照稿 + 可觀察拒絕／檔集」量測；本檔不寫測試檔或 fixture。量測形是對「可量測 SC」的延伸 | 本 PR 不實作 coordinator；fixture 進後站 | 模板頂註步 2；使用者強調 measurable。延伸 `[Assumption]` | SC 改成口頭「看起來會 hop」 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 契約維持 `2.0.0`；本 hop 不 bump plugin／`devflow-contract.json`／`agent-event` schema。
- `1-discussion.md` 保留 draft／「不送 G1」原文；本檔才改口（Owner chat「ok」= Stage1 direction OK，不是本檔 G1 PASS）。
- 審頁用 `scripts/build-stage2-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。
- 不預先跳過 Stage 3；觸發判定留給該站（本檔無「跳過 Stage 3」流程層 OC）。
- 未讀 B／C 線 Stage 2；本檔獨立收斂。
- rewrite cap 數字不重開（hop≤2／Decide≤1／Goal reopen≤1）；落點仍 OPEN。
- 4-spec 再釘：三失敗的具體 R/S、事件五問落到哪種紀錄、coordinator 模組名。
- dual-path 電池腳本、marketplace 多 cache、schema bump × doctor 紅，交 B／C／後站。

## ADR 晉升檢查
- 難逆轉:否（本 hop 零 runtime；G3 未過；Decision／OC 仍可改；F3 才切預設路線）
- 反直覺:是（摺等待卻讓 Must-keep 紅擋 hop；事件要留卻不鎖鍵；本 slug 不吃自己的五站藥）
- 真 trade-off:是（hop 快 vs 假完成；鎖鍵省事 vs 偷做 annex；自己當白老鼠 vs freeze 觀測）
→ 晉升:**否**（難逆轉未中；留在本檔。不抄 `docs/adr/`）

## 確認紀錄
- 決策點清單確認 | 2026-09-14 | Implementer A brief：coordinator auto-advance × Must-keep fail-closed（討論三失敗）；event 五語意槽不鎖鍵（OC-3）；拒 1B 中間等人、拒 2B／2C 紅了仍 hop。Owner Human Stage1 direction OK（chat「ok」2026-09-14）。六點對 1A…6A。
- Stage 1 改口 | 2026-09-14 | 1-discussion 仍 draft、當時寫不送 G1／不宣稱 Human Stage1 PASS；owner chat「ok」後開本站。不回改正本討論。
- 獨立於 B／C | 2026-09-14 | 未讀他線 Stage 2 產出；只讀 1-discussion＋brief §4／§7 F2＋狀態機＋F1 annex／RP＋模板。
- 自檢七掃 | 2026-09-14 | ①每案優劣有依據欄（空格標 `[Assumption]`）。②G-keep-1／G-obs-1／G-self-1／G-knife-1／G-honest-1 進 Decision／SC；G-locus／G-trap／Q9–Q16 進仍待驗。③`[>]` Q9–Q16／Q18／Q20=仍待驗；Q17=5A；Q11–Q16 不由 A 選 hop_id。④SC 皆對照稿／拒絕／檔集。⑤Rejected 無空棄因。⑥六決策點由 A brief＋Stage1 ok 確認；OC-1／2 延伸、OC-3／6／7 收窄、OC-4 流程層、OC-5 升格 Q17、OC-8 延伸量測形，皆可回溯決策點。⑦既有脈絡是對帳不是外移 schema。圖上 1A–6A 標選定，Rejected 未上圖。
