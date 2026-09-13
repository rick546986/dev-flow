---
feature: requirement-discovery-gaps
stage: 5-tasks
status: approved
owner: rick
updated: 2026-09-13
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — 九缺口欄位與三支既有牙

> 把 4-spec（G2 PASS、`verdict: PASS`、#278 = `bc627b463fd2e9c85f75b9ebbbdb38dca20f830e`、R/S 來自 #277）切成可派工縱切。
> Decision 1A–8A／OC-1～OC-6 已核，本 hop **不重開、不發明新 R/S**。
> 本 hop **只寫任務**，不落地 Stage 6 守衛碼、不改 `4-spec.md`、不 bump plugin、不發版、不改 `STATUS.md`／`HISTORY.md`、不發明 G3。
> 模式：sequential（Feature Risk high；見 Split Decisions）。
> tracer：T-1 先讓「三支既有牙、沒有第四家族」可觀測並讓 Goals 錯欄對照稿紅；再逐 R 加厚教師與另外兩支牙。

## 開工前提

Stage 4 已核准。G2 PASS 已在 tip（#278）。本 hop 不改 `4-spec.md`／`4-spec.html`。
牙只延伸既有 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`（及它們已掛進的 `devflow-check.sh`），禁止新開 `check-discovery-gaps.sh` 或任何第二檢查家族（OC-1）。
fixture 目錄建議 `scripts/fixtures/discovery-gaps/`（4-spec DD 下層；本 hop 只點名，Stage 6 才新增檔）。
Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。

### N1 R/S 盤點（35 S）

| R | S | 本 hop T |
|---|---|---|
| R-1 分辨工作結果與解法構想 | S-1.2 錯欄紅；S-1.4 不採黑名單 | T-1（OC-1 同一入口） |
| R-1（續） | S-1.1 模板分欄；S-1.3 example 改口 | T-2 |
| R-2 發現題不先塞推薦 | S-2.1、S-2.2、S-2.3 | T-3 |
| R-3 高影響主張回來源或期限 | S-3.1、S-3.2、S-3.3、S-3.4、S-3.5 | T-4 |
| R-8（同主張牙） | S-8.4 ticket／SOP 解法不當事實 | T-4 |
| R-4 過期假設擋 G2 | S-4.1、S-4.2、S-4.3、S-4.4 | T-5 |
| R-5 verdict 一行角色場景 | S-5.1、S-5.2、S-5.3 | T-6 |
| R-6 痛點列逐條有去向 | S-6.1、S-6.2、S-6.3、S-6.4 | T-7 |
| R-7 出貨留下回看四欄 | S-7.1、S-7.2、S-7.3 | T-8 |
| R-8 核准後讀得到且方案檔仍禁 | S-8.1、S-8.2、S-8.3 | T-9 |
| R-9 Fast 寫規格前收完六問 | S-9.1、S-9.2、S-9.3、S-9.4、S-9.5 | T-10 |

### Verify 開工前原樣跑（2026-09-13；牙尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1 | `scripts/fixtures/discovery-gaps/` 不存在；`check-realworld.sh` 無錯欄 fixture 針 | ③綠不了但方向對 |
| T-2 | `_templates/1-discussion.md` 無 `## Requested solution`；L96 仍寫 `畫面路徑 \| API 端點` | ③方向對 |
| T-3 | `N3-probe.md` 仍寫「附推薦答案」；無 `發現｜`／`裁決｜` | ③方向對 |
| T-4 | `S1-survey.md` 仍寫「認可後的清單 = 已核事實」；無點頭／枚舉 fixture | ③方向對 |
| T-5 | `assumption-expired-open.md` 不存在；spec-gate 尚無 Assumption 項 | ③方向對 |
| T-6 | `_templates/3-prototype.md` Human verdict 只有 ENUM，無 `role=`／`scenario=` | ③方向對 |
| T-7 | 模板無 `## Real-world Disposition`；缺表 fixture 不存在 | ③方向對 |
| T-8 | `_templates/7-review.md` 無「回看日期」四欄 | ③方向對 |
| T-9 | 模板無 `## Evidence manifest`；guard 無 Read 分支；`guard-read-1-discussion.md` 不存在 | ③方向對 |
| T-10 | Fast triage fixture 不存在；`fast-wait-shown-as-done.md` 無 S-9.2 表內容 | ③方向對 |

## T-1 鎖定三支既有牙為唯一入口，並讓 check-realworld 指出 Goals 錯欄
- [x] 完成
- Covers: R-1 / S-1.2, S-1.4
- Files: scripts/check-realworld.sh, scripts/fixtures/discovery-gaps/
- Verify: `test ! -e scripts/check-discovery-gaps.sh && test -f scripts/fixtures/discovery-gaps/goals-dashboard-in-wrong-column.md && test -f scripts/fixtures/discovery-gaps/goals-outcome-with-requested-dashboard.md && python3 -c "import pathlib; t=pathlib.Path('scripts/check-realworld.sh').read_text(); assert 'goals-dashboard-in-wrong-column' in t and 'goals-outcome-with-requested-dashboard' in t; assert '構想在錯欄' in t or 'Requested solution' in t; print('T-1-wired')" && bash scripts/check-realworld.sh`
- Blocked-by: —
- Intent: 日常多一次終端機拒絕：有人把「我要 dashboard」寫進 Goals、Requested solution 空著，同一支 `check-realworld.sh` 會紅並留下「構想在錯欄」。合法結果句即使正文出現 dashboard／API 當領域詞，只要構想在 Requested solution，不會只因這兩個詞被誤殺。改的是既有牙的射程與 `scripts/fixtures/discovery-gaps/` 對照稿，不是新發明一套檢查 CLI。不會變成 Cursor 擋寫、不會新開 `check-discovery-gaps.sh`、不會在本 T 改模板正文。
- Boundaries: OC-1：機械牙只延伸既有 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`（及已掛進的 `devflow-check.sh`）。本 T 只准改 realworld 與 discovery-gaps fixture；禁止新增 `scripts/check-discovery-gaps.sh`、禁止新開 `check-evidence-allow.sh`。realworld 擁有教師地板與指定 fixture 判定，不得當過期假設的 G2 Gate（那是 spec-gate）。MIN_CHECKS 必須改成加完後的實際檢查數，不是寬放下限。本 T 不改正本模板、不改 spec-gate、不改 guard。Actor=G1 reviewer；Goal=構想不能混成目標；Authority=形狀檢查擋錯欄，G1 抽查語意；Recovery=把該句搬到 Requested solution 並標未定案後重跑。看過 fixture 路徑 ≠ 已分欄。

## T-2 改口模板與範例，讓 Goals 只寫結果、構想進 Requested solution
- [x] 完成
- Covers: R-1 / S-1.1, S-1.3
- Files: _templates/1-discussion.md, skills/dev-talk/nodes/S4-accept.md, example/contract-expiry-reminder/1-discussion.md, scripts/check-realworld.sh
- Verify: `python3 -c "import pathlib; t=pathlib.Path('_templates/1-discussion.md').read_text(); e=pathlib.Path('example/contract-expiry-reminder/1-discussion.md').read_text(); s=pathlib.Path('skills/dev-talk/nodes/S4-accept.md').read_text(); sec=lambda text,h: (lambda i: '' if i<0 else text[i+len(h):].split(chr(10)+'## ',1)[0])(text.find(h)); assert '## Goals' in t and '## Requested solution' in t; assert '畫面路徑 | API 端點' not in sec(t,'## Goals') and '畫面路徑 | API 端點' not in sec(t,'## 驗收雛形'); assert '從哪裡看出結果發生' in s or '結果發生' in s; g=sec(e,'## Goals'); assert '就能看到' not in g and '點擊可直達' not in g and '一眼可見' not in g; assert '## Requested solution' in e; print('T-2-ok')" && bash scripts/check-realworld.sh`
- Blocked-by: T-1
- Intent: 日常少抄到「Goal = dashboard」：打開模板會看到結果欄與構想欄分開；驗收雛形改問結果在哪被看見，不再預填畫面／API 通道。抄完整範例時，Goals 三句不再把登入／點擊／一眼可見當成目標本身；若仍要提 dashboard／卡片／URL，只出現在 Requested solution 且標未定案。改的是人會抄的那三層指令，不是另寫一份討論指南。不會變成黑名單掃 dashboard 詞、不會在本 T 改 N3 問法、不會把 example Interview「最低成本呈現面」留成已核目標。
- Boundaries: 只准改 Files 四檔。1-discussion 同檔欄擁有 Goals／Requested solution 節名；S4-accept 只改「從哪看」問句，不得把元件／JSON 當 Goal。example 是活教師，必須同期改口（1A／Q14），禁止另開 slug 才改範例。禁止 dashboard／API 黑名單（S-1.4 已由 T-1 守）。realworld 本 T 只准加模板／範例地板 check，不得撤回 T-1 的錯欄 fixture。禁止改 STATUS／HISTORY、禁止 bump plugin。Actor=採用者（會抄 example）；Goal=抄範例時寫結果；Recovery=若 Goals 仍鎖通道，同一 T 改到符合 THEN。

## T-3 讓發現題路徑禁附推薦，刪掉一邊前綴就紅
- [x] 完成
- Covers: R-2 / S-2.1, S-2.2, S-2.3
- Files: skills/dev-talk/nodes/N3-probe.md, skills/dev-talk/SKILL.md, guides/guide-dev-talk.html, scripts/check-realworld.sh, scripts/fixtures/discovery-gaps/, scripts/test-architecture-guards.sh
- Verify: `python3 -c "import pathlib; n=pathlib.Path('skills/dev-talk/nodes/N3-probe.md').read_text(); k=pathlib.Path('skills/dev-talk/SKILL.md').read_text(); assert '發現｜' in n and '裁決｜' in n and '禁附推薦' in n; assert '發現｜' in k or '禁附推薦' in k; assert '連續兩輪無新問題' not in n.split('## 完成條件',1)[-1].split('## ',1)[0] or '輔助' in n; print('T-3-skill')" && test -f scripts/fixtures/discovery-gaps/probe-decision-with-options.md && python3 -c "import pathlib; t=pathlib.Path('scripts/check-realworld.sh').read_text(); assert '發現｜' in t and '裁決｜' in t; print('T-3-wired')" && bash scripts/check-realworld.sh`
- Blocked-by: T-2
- Intent: 日常被問「上次真的怎麼做」時，題目本身不再先塞推薦答案。發現題帶 `發現｜`、禁附推薦；裁決題帶 `裁決｜`、可以附本方案／Non-Goal／另開 slug。有人從 N3 或指南刪掉其中一邊前綴，同一支 realworld 會紅。裁決題附選項不會被當成發現題違規。改的是問句前綴與靜態對稱牙，不是還原整場對話。不會變成從最終 1-discussion 重放訪談、不會把「連續兩輪無新問題」留成唯一完成條件。
- Boundaries: 只准改 Files 六檔。N3-probe 擁有發現／裁決路徑硬規則；`skills/dev-talk/SKILL.md` 入口摘要必須同期改口（指南 `guide-dev-talk.html` 抄的是 SKILL 摘要，只改指南會漂）。指南與 SKILL 不得新造第二份問句正本。realworld 擁有前綴對稱與「發現題附推薦」形，不還原對話（Known limit ①）。S-2.2 隔離複本突變可寫進 `test-architecture-guards.sh`，禁止另開檢查家族。完成條件改為必查面已覆蓋、關鍵反例已問、證據缺口已顯性化；兩輪只標輔助。禁止改 S4-accept（屬 T-2）、禁止改 guard。Actor=訪談對象／討論 agent；Goal=不被錨定；Recovery=若問句已附推薦，重寫為 `發現｜` 開放題再問。

## T-4 讓高影響主張缺來源且缺期限就紅，點頭不得當獨源
- [x] 完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5; R-8 / S-8.4
- Files: skills/dev-talk/nodes/S1-survey.md, scripts/check-realworld.sh, scripts/fixtures/discovery-gaps/
- Verify: `python3 -c "import pathlib; s=pathlib.Path('skills/dev-talk/nodes/S1-survey.md').read_text(); assert '認可後的清單 = 本次「已核事實」' not in s and '認可' in s; print('T-4-skill')" && test -f scripts/fixtures/discovery-gaps/nod-as-only-source.md && test -f scripts/fixtures/discovery-gaps/enum-unknown.md && test -f scripts/fixtures/discovery-gaps/ticket-solution-as-fact.md && python3 -c "import pathlib; t=pathlib.Path('scripts/check-realworld.sh').read_text(); assert '點頭' in t and 'Observed' in t and 'Reported' in t; print('T-4-wired')" && bash scripts/check-realworld.sh`
- Blocked-by: T-3
- Intent: 日常沿一條高影響痛點往回走時，要嘛碰到可重開來源，要嘛碰到 Assumption 加期限。只寫「使用者反映」或「使用者點頭」會紅；狀態寫 Unknown／Fact 會紅。有 Observed+可重開來源，或 Assumption+期限+四欄，會綠。普通已核 path:L 句沒寫「風險=高」不必貼枚舉。ticket／SOP 裡的「建議做 dashboard」不得標 Observed。改的是高影響列形狀與 S1 認可語意，不是每句 Context 都貼標籤。不會變成全句枚舉儀式、不會把點頭升成已核事實。
- Boundaries: 只准改 Files 三檔。高影響抽樣鎖定 4-spec R-3／DD-1（Workarounds／Exceptions／Journey 痛點非空／`[Assumption]` 或 `[~]` 且風險或影響級為高／Interview ⚠️）。狀態 ∈ {Observed, Reported, Inferred, Assumption, Conflict}。來源 XOR Assumption+期限。S-8.4 與 S-3.1 同一支主張牙，不另開入口。S1-survey 改「認可 ≠ 來源升格」，禁止把認可後清單當唯一來源。realworld 擁有枚舉／來源／點頭／ticket 解法判定；不得把過期假設擋點放進來（屬 T-5 spec-gate）。禁止發第二鏈編號。Actor=討論 agent／G1 reviewer；Goal=認可是確認理解不是驗證營運事實；Recovery=改標 Assumption 或補可重開 path 後重跑。

## T-5 讓過期未驗 Assumption 在 spec-gate 被拒，已驗或 OC 放行
- [x] 完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3, S-4.4
- Files: scripts/check-spec-gate.sh, _templates/1-discussion.md, example/contract-expiry-reminder/1-discussion.md, scripts/check-realworld.sh, scripts/fixtures/discovery-gaps/
- Verify: `{ bash scripts/check-spec-gate.sh scripts/fixtures/discovery-gaps/assumption-expired-open.md; test $? -eq 1; } && bash scripts/check-spec-gate.sh scripts/fixtures/discovery-gaps/assumption-resolved.md && bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md && python3 -c "import pathlib; t=pathlib.Path('_templates/1-discussion.md').read_text(); e=pathlib.Path('example/contract-expiry-reminder/1-discussion.md').read_text(); assert all(x in t for x in ['若為假影響什麼','影響級','怎麼驗']); assert all(x in e for x in ['若為假影響什麼','影響級','怎麼驗']); print('T-5-floor')" && bash scripts/check-realworld.sh`
- Blocked-by: T-4
- Intent: 日常送 G2 前，過期還 open 的高影響假設會在同一支 `check-spec-gate.sh` 被拒，人看得見拒絕，不是「模板有欄就綠」。已轉 resolved，或 Owner Call 寫 oc-accepted，該列不擋。模板與範例看得到 Assumption 四欄（若為假影響什麼／影響級／怎麼驗／何時／由誰驗）。改的是既有 G2 Gate 加項與教師地板，不是第二支送審 CLI。不會變成 spec-gate 判語意、不會把過期假設檢查塞進 realworld。
- Boundaries: spec-gate 擁有 4-spec 送審通過／失敗；只讀、不寫 4-spec。新項與 C1–C6 同檔（建議 C7 Assumption refs）；C1–C6 保留，只加項。refs 表三欄：引用／deadline／status∈{open,resolved,oc-accepted}；deadline=`YYYY-MM-DD` 或 `stage-2`／`stage-3`。open + 已過站或過去日且無 oc-accepted → exit 1。禁止新開第二支 G2 CLI。S-4.4 四欄地板走 realworld，不得把過期擋點放到 realworld。本 T 改 1-discussion 只加 Assumption 四欄，不得撤回 T-2 分欄。本 slug 4-spec 三列 oc-accepted 必須仍綠（S-4.3）。Actor=G2 reviewer；Goal=過期高影響假設進不了 G2；Recovery=改 status=resolved 或 oc-accepted 後重跑，不要口頭說「知道有假設」。

## T-6 讓 Human verdict 一行看出驗了哪個角色與哪場
- [x] 完成
- Covers: R-5 / S-5.1, S-5.2, S-5.3
- Files: _templates/3-prototype.md, example/contract-expiry-reminder/3-prototype.md, scripts/check-realworld.sh, scripts/fixtures/discovery-gaps/
- Verify: `python3 -c "import pathlib; t=pathlib.Path('_templates/3-prototype.md').read_text(); e=pathlib.Path('example/contract-expiry-reminder/3-prototype.md').read_text(); assert 'role=' in t and 'scenario=' in t; assert 'role=' in e and 'scenario=' in e; assert '本包必填全表' not in t and 'Actor Coverage' not in t; print('T-6-template')" && test -f scripts/fixtures/discovery-gaps/verdict-accepted-only.md && python3 -c "import pathlib; r=pathlib.Path('scripts/check-realworld.sh').read_text(); assert 'role=' in r and 'scenario=' in r; print('T-6-wired')" && bash scripts/check-realworld.sh`
- Blocked-by: T-5
- Intent: 日常後讀 3-prototype 時，遮住前後文只看 Human verdict 那一行，要答得出驗了誰、驗了哪場。只寫 ACCEPTED 加姓名日期會紅。寫成 `ACCEPTED | role=… | scenario=…` 且 attestation 仍在，會綠。模板與範例不得要求 Actor Coverage 全表。改的是 verdict 一行格式與 realworld 殘行牙，不是新造角色覆蓋表。不會變成 Agent 代填 attestation、不會把 LIGHT 做成全表。
- Boundaries: 格式鎖定 `<ENUM> | role=<Actors 表角色> | scenario=<AC-id 或 Demo Script 場景名>`（DD-7／8A）。既有 attestation 牙（不是 Agent 代填）必須仍在；無 attestation 的 ACCEPTED 仍拒。realworld 在 ENUM=ACCEPTED 時發動 role／scenario 檢查。禁止加 Actor Coverage 全表必填指令（已拒 8B）。本 T 不改 guard、不改 spec-gate。Actor=後讀 3-prototype 的人；Goal=一行內答出驗了誰、驗了哪場；Recovery=改成完整一行後重跑，或改 NOT_REVIEWED。

## T-7 讓 Stage 1 高影響痛點到 Stage 4 每條都有去向
- [x] 完成
- Covers: R-6 / S-6.1, S-6.2, S-6.3, S-6.4
- Files: scripts/check-spec-gate.sh, _templates/2-decision.md, _templates/4-spec.md, example/contract-expiry-reminder/2-decision.md, example/contract-expiry-reminder/4-spec.md, scripts/fixtures/discovery-gaps/
- Verify: `{ bash scripts/check-spec-gate.sh scripts/fixtures/discovery-gaps/disposition-missing.md; test $? -eq 1; } && python3 -c "import pathlib; t2=pathlib.Path('_templates/2-decision.md').read_text(); t4=pathlib.Path('_templates/4-spec.md').read_text(); assert '去向' in t2 and '## Real-world Disposition' in t4; print('T-7-template')" && test "$(rg -n 'RW-[0-9]' _templates/2-decision.md _templates/4-spec.md docs/dev/requirement-discovery-gaps/2-decision.md docs/dev/requirement-discovery-gaps/4-spec.md example/contract-expiry-reminder/2-decision.md example/contract-expiry-reminder/4-spec.md | wc -l | tr -d ' ')" -eq 0 && bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md`
- Blocked-by: T-5
- Intent: 日常對一次 Stage 1 原文片段，後面還看得到去向。full lane 缺 `## Real-world Disposition`、或去向空白，同一支 spec-gate 會紅。標「本方案處理」的下落必須有 `R-` 或 `S-` id；其餘落到 Out of Scope／Known limit／後續 slug。引用欄是原文，不是 RW-1 這種第二鏈編號。改的是 Stage 2／4 對帳表與 Gate 形狀項，不是另發 ID 鏈。不會變成每句 Context 都建帳、不會讓本 slug 已寫好的 disposition 表被誤殺。
- Boundaries: spec-gate 加 disposition 形狀項（建議 C9）；full 必有表，去向五值。本方案處理 → 下落匹配 `R-` 或 `S-`（4A／DD-4）。引用 = Stage 1 原文片段，禁止 `RW-[0-9]` 第二鏈。2-decision／4-spec disposition 擁有去向與下落；不得改 STATUS 寫入口。example 對應檔同一刀改口。Verify 用的 `scripts/fixtures/discovery-gaps/disposition-missing.md` 必須列在 Files（本 T 已含目錄），否則 Stage 6 寫 fixture 會被 scope guard 擋。本 T 不改 1-discussion、不改 Fast 六問（屬 T-10）。S-6.4 的 `rg` 零命中含本 slug 已核准檔；負向對照句只寫「不得發第二鏈」不算發 ID。Actor=收斂者／G2 reviewer；Goal=痛點不能無聲消失；Recovery=按 2-decision 表抄進 4-spec 並填 S-id 或 Out of Scope。

## T-8 讓出貨 Exit 留下回看四欄，結果走 HISTORY 追加
- [x] 完成
- Covers: R-7 / S-7.1, S-7.2, S-7.3
- Files: _templates/7-review.md, example/contract-expiry-reminder/7-review.md, scripts/check-realworld.sh, scripts/fixtures/discovery-gaps/
- Verify: `python3 -c "import pathlib; t=pathlib.Path('_templates/7-review.md').read_text(); e=pathlib.Path('example/contract-expiry-reminder/7-review.md').read_text(); assert all(x in t for x in ['回看日期','回看 owner','資料來源','低於何值重開']); assert all(x in e for x in ['回看日期','回看 owner','資料來源','低於何值重開']); assert 'lookback.md' not in t and 'history-append.sh' in t; print('T-8-floor')" && test -f scripts/fixtures/discovery-gaps/lookback-missing-threshold.md && bash scripts/check-realworld.sh`
- Blocked-by: T-6
- Intent: 日常勾 Exit 準備 shipped 時，人看得到誰／何時／用什麼資料回看、低於何值重開。模板或範例缺四欄之一會紅。已宣稱 shipped 且出現回看節卻缺「低於何值重開」會紅；舊 7-review 根本沒回看節不誤殺。結果到期用既有 `history-append.sh` 追加，不另造永久 lookback 檔。改的是 Exit 約定與 realworld 地板，不是新文件種類。不會變成 G3 要等數週結果、不會讓牙去判「指標是否代表改善」。
- Boundaries: 7-review Exit 擁有回看四欄；結果入口鎖定 `scripts/history-append.sh`。禁止新建 `lookback.md` 或永久 lookback 檔（已拒 5C）。填檔牙只在 7-review 已出現回看節或四欄名時發動（DD-6）。指標是否代表問題改善是人判；到期未回看不得把問題寫成已改善。本 T 不改 STATUS 正本表列、不改 history-append.sh 演算法。Actor=owner；Goal=出貨時留下回看約定；Recovery=補缺欄後重跑，不要另造 lookback.md。

## T-9 讓 owner 核准後的事實路徑讀得到，方案檔與未核路徑仍禁
- [x] 完成
- Covers: R-8 / S-8.1, S-8.2, S-8.3
- Files: hooks/devtalk-guard.sh, hooks/selftest.sh, _templates/1-discussion.md, example/contract-expiry-reminder/1-discussion.md, scripts/fixtures/discovery-gaps/
- Verify: `python3 -c "import json,os,pathlib,subprocess; t=pathlib.Path('_templates/1-discussion.md').read_text(); e=pathlib.Path('example/contract-expiry-reminder/1-discussion.md').read_text(); assert '## Evidence manifest' in t and 'owner 核准' in t; assert '## Evidence manifest' in e; man=pathlib.Path('scripts/fixtures/discovery-gaps/guard-read-1-discussion.md'); assert man.is_file(); mt=man.read_text(); assert '## Evidence manifest' in mt and '_templates/1-discussion.md' in mt and '是' in mt; assert '2-decision' in mt; assert 'notes/review-requirement-discovery-gaps.md' in mt and ('未核' in mt or '空白' in mt); root=pathlib.Path('.').resolve(); guard=str(root/'hooks/devtalk-guard.sh'); cur=root/'.devtalk-cursor.json'; old=cur.read_text() if cur.is_file() else None; cur.write_text(json.dumps({'node':'N3-probe','MEMORY_SESSION_ID':'t9-verify'})+'\n'); env=os.environ.copy(); env['DEVTALK_MANIFEST']=str(man.resolve()); run=lambda rel: subprocess.run(['bash',guard],input=json.dumps({'tool_name':'Read','tool_input':{'file_path':str(root/rel)}}),text=True,capture_output=True,env=env); ps=[('S-8.1',run('_templates/1-discussion.md'),0,()), ('S-8.2',run('docs/dev/requirement-discovery-gaps/2-decision.md'),2,('2-decision','4-spec','方案檔')), ('S-8.3',run('notes/review-requirement-discovery-gaps.md'),2,())]; cur.write_text(old) if old is not None else cur.unlink(missing_ok=True); bad=[(tag,p.returncode,(p.stdout or '')+(p.stderr or '')) for tag,p,want,need in ps if not ((p.returncode==want) and (not need or any(x in ((p.stdout or '')+(p.stderr or '')) for x in need)))]; assert not bad, bad; print('T-9-read-ok')"`
- Blocked-by: T-5
- Intent: 日常討論期，owner 在 1-discussion 同檔的 Evidence manifest 把核准格寫成「是」之後，Read 該擬路徑不再被圍欄擋下。有人把 2-decision／4-spec 列進去且誤寫核准=是，Read 仍 exit 2。核准=未核或空白的路徑不得當已授權 evidence，Read 會擋。改的是同一支 `devtalk-guard.sh` 的 Read 允許集合，不是另開 evidence CLI。不會變成主機層 OS hook、不會讓核准格覆寫 2–7 禁令、不會另造永久 manifest 檔。Verify 必須真的餵 `tool_name=Read` 跑三案 exit，不准只數 selftest 字樣。
- Boundaries: guard 擁有討論期擋讀。talk 游標在時才發動 Read 分支；游標不在維持今日只掃 `skills/dev-talk/*` 寫入洩漏。放行核准=是；仍禁 2-decision／3-prototype／4-spec／5-tasks／6-implementation-notes／7-review（含 html twin）。核准 ∈ {是, 未核, 禁}；是不能覆寫 2–7 禁令。manifest 節名 `## Evidence manifest`，住 1-discussion 同檔，五欄：想找哪類／為什麼／擬路徑或來源／owner 核准／已讀（DD-5／6A）。測試縫：fixture `scripts/fixtures/discovery-gaps/guard-read-1-discussion.md` 列出三列（核准=是的 `_templates/1-discussion.md`、核准即使為是的 `2-decision`、核准=未核的 `notes/review-requirement-discovery-gaps.md`）；Verify 寫 ephemeral `.devtalk-cursor.json` 並設 `DEVTALK_MANIFEST` 指向該 fixture，再對三條路徑跑 Read。禁止新開 `check-evidence-allow.sh`、禁止另檔 evidence-manifest.md。selftest 可加 Read 回歸，但 Verify 不靠 `grep -c`。S-8.4 已由 T-4 同一主張牙承接，本 T 不改 realworld。Known limit ②：人跳過 hook 硬讀方案檔，本 feat 不新造 OS hook。Actor=討論 agent；Goal=核准後讀得到事件／行為／結果，方案檔仍進不去；Recovery=先列「想找哪類＋為什麼」等 owner 核；方案檔從擬路徑刪掉。

## T-10 讓 Fast 寫規格前收完六問，空白不是已分診
- [x] 完成
- Covers: R-9 / S-9.1, S-9.2, S-9.3, S-9.4, S-9.5
- Files: scripts/check-spec-gate.sh, _templates/4-spec.md, skills/dev-flow/SKILL.md, scripts/fixtures/discovery-gaps/
- Verify: `{ bash scripts/check-spec-gate.sh scripts/fixtures/discovery-gaps/fast-blank-triage.md; test $? -eq 1; } && { bash scripts/check-spec-gate.sh scripts/fixtures/discovery-gaps/fast-hit-no-dest.md; test $? -eq 1; } && bash scripts/check-spec-gate.sh scripts/fixtures/discovery-gaps/fast-visual-all-no.md && bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md && python3 -c "import pathlib,re; t=pathlib.Path('_templates/4-spec.md').read_text(); s=pathlib.Path('skills/dev-flow/SKILL.md').read_text(); assert '## Fast early risk triage' in t; assert '六問' in s or 'Fast early risk' in s; w=pathlib.Path('scripts/fixtures/discovery-gaps/fast-wait-shown-as-done.md').read_text(); assert '等待被顯示成完成' in w; assert re.search(r'是.+等待被顯示成完成|等待被顯示成完成', w); assert any(x in w for x in ('full','fast+mini','OC')); assert '待裁' not in w; assert re.search(r'去向', w) and not re.search(r'去向\s*[|=:：]\s*Fast\b', w); print('T-10-ok')"`
- Blocked-by: T-7
- Intent: 日常 Fast 想直接開寫 4-spec 時，必須先填六問（改變下一步／權限核准語意／等待完成語意／角色交接／系統外動作／中斷恢復），每問是或否加一句。表空白或六問答欄空，spec-gate 會紅。只改一個狀態字、把等待顯示成完成，第 3 問必須是「是」，去向不得空白也不得是 Fast。命中卻寫「待裁」會紅。六問全否、已有 approved spec、不改語意的純視覺，去向=Fast 仍可 Fast。本檔 lane=full 沒有六問表，不得被 Fast 項誤殺。改的是進 4 前分診與同一支 spec-gate，不是拆掉 Fast 可跳過 1–3。不會變成命中一律升 full、不會新造 triage 卡檔。
- Boundaries: 節名鎖定 `## Fast early risk triage`，必須在 `## ADDED Requirements` 之前（DD-3）。僅 `lane: fast` 發動；full 缺表 no-fire（S-9.5 用本 slug 4-spec）。去向 ∈ {Fast, full, fast+mini, OC}。命中後去向空白或 `待裁` → exit 1。禁止改七關結構、禁止刪「Fast 合法跳過 1–3」（刻意維持）。spec-gate 加 Fast 項（建議 C8），不判「不改語意」（仍是 reviewer 對 diff）。禁止新造 triage 卡或另檔。SKILL Fast 段改「進 4 前六問；命中由 owner 裁」，不得把六問寫成進 4 之後才列。Actor=Fast 實作者／owner；Goal=寫 4-spec 前先收完六問，等待誤標不能當純視覺 Fast；Recovery=填滿六問與去向後重跑。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential，不開 parallel | Feature Risk high；多 T 重疊 `check-realworld.sh`／`check-spec-gate.sh`／`_templates/1-discussion.md`。parallel 須明確啟用，本 hop 選缺省。 | `_templates/5-tasks.md` execution.mode 缺省 sequential；4-spec Verification Profile Risk high | 棄 T-6 ∥ T-7。檔案不重疊可平行，但 sequential 較保守。 |
| T-1 先鎖 OC-1 三牙 + S-1.2／S-1.4 | Variant B：三牙約束若混進教師改口，Verify 會變成「錯欄 fixture」與「改模板」兩套不相干指令。先打通最薄縱切：同一入口指出錯欄、不採黑名單、沒有第四家族。 | 4-spec OC-1／S-1.2「同一入口，不另開 check-discovery-gaps.sh」；模板「Verify 要跑兩套不相干指令 → 拆 T」 | 棄「R-1 九個 S 一 T」（Files 恰 5，但 Verify 兩套不相干）。棄新開 `check-discovery-gaps.sh`。 |
| R-1 其餘教師獨立 T-2 | S-1.1／S-1.3 是人抄的活教師；T-1 若同時改模板，錯欄牙與分欄地板會綁死，T-1 無法單獨 RED→GREEN。 | 4-spec S-1.1／S-1.3；T 自足律 | 棄 T-1 含模板（T-1 Verify 會等 T-2 才綠）。 |
| 其餘一 R 一 T | Variant B 偏置：Files ≤5 且 Verify 同一支牙就合併。R-2…R-7、R-9 各一 T。 | 模板「一個 T 一個關注點」；owner brief 一 T 每 R | 棄按 check-realworld／spec-gate／guard 三層橫切（那是架構層）。 |
| S-8.4 併進 T-4 | S-8.4 明文與 S-3.1 同一支主張牙；拆開會讓兩 T 改同一 realworld 函式、Verify 重複。 | 4-spec S-8.4「跑 S-3.1 同一支主張牙」 | 棄 S-8.4 跟 T-9（T-9 Files 會超過 ~5：guard＋selftest＋兩份 1-discussion＋realworld＋fixture）。 |
| T-9 不含 realworld | Read 圍欄是 guard；S-8.4 已在 T-4。T-9 Files 含 fixture 目錄供 `guard-read-1-discussion.md`。Verify 真跑 Read 三案 exit，不數 selftest 字樣。 | 4-spec S-8.1 觀測「guard 對該 Read 的 exit」；Reviewer must-fix | 棄 `grep -c 'devtalk-guard Read' hooks/selftest.sh`。 |
| T-7 與 T-10 都改 spec-gate，硬順序 T-7→T-10 | 兩 T 加的是不同項（disposition vs Fast），但同一檔。T-10 也改 `_templates/4-spec.md`（T-7 先加 Disposition）。 | 4-spec DD 下層 C8／C9；Files overlap | 棄 T-10 Blocked-by T-5（會與 T-7 搶 4-spec 模板）。 |
| 不切 G3、不切 Stage 6 落地碼 | owner brief：只寫 Stage 5；status 留 draft。 | 本 hop brief；4-spec Out of Scope「本 hop 開 5-tasks／發明 G3」指的是 Stage 4 hop | 棄本 hop 把 status 轉 approved（N6 定案權在 owner；brief 要求 draft）。 |
