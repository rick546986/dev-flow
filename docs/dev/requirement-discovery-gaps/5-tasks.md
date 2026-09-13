---
feature: requirement-discovery-gaps
stage: 5-tasks
status: draft
owner: rick
updated: 2026-09-13
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — 九條需求發現缺口（Variant C：人旅程序）

> 把 4-spec（G2 PASS、#278 = `bc627b463fd2e9c85f75b9ebbbdb38dca20f830e`、R/S 來自 #277）切成可派工縱切。
> 本 hop **只寫任務**，不落地 `_templates/`／`skills/`／`example/`／三支牙正本、不開 Stage 6、不 bump plugin、不發版、不改 `STATUS.md`／`HISTORY.md`／`4-spec.md`、不代填 G3。
> 模式：sequential（Feature Risk high；見 Split Decisions）。tracer：先讓人在討論稿上分得清結果與構想，再依訪談→假設→去向→證據→Fast 六問→Demo 一行加厚；三支既有牙最後才延射程。
> 牙只准延 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`。禁止新造 `check-discovery-gaps.sh`。本 hop 不發明新 R/S，不重開 Decision 1A–8A。

## 開工前提

Stage 4 已核准。G2 PASS 已在 tip（#278）。本 hop 不改 `4-spec.md`／`4-spec.html`。正式入口仍是既有三支牙，不是第二檢查家族。欄位字面鎖在 4-spec DD-1～DD-7。本 hop 不發明新 R/S。frontmatter `status` 維持 draft（owner 尚未定案）。

### N1 R/S 盤點（9 R / 35 S）

| R | S | 本 hop T |
|---|---|---|
| R-1 讀 Stage 1 能分辨結果與構想 | S-1.1 模板分欄且 Goals 不再鎖通道；S-1.3 example Goals 改口 | T-1 |
| R-1（續） | S-1.2 「我要 dashboard」錯欄必紅；S-1.4 領域詞不得黑名單誤殺 | T-8 |
| R-2 發現題不先塞推薦 | S-2.1 N3／指南發現題禁推薦、裁決題可附 | T-2 |
| R-2（續） | S-2.2 刪一邊前綴必紅；S-2.3 裁決附選項仍綠 | T-8 |
| R-3 高影響主張回到來源或期限 | S-3.3 S1-survey 認可不再升格（教師半） | T-3 |
| R-3（續） | S-3.1 缺來源且缺期限紅；S-3.2 有來源或期限綠；S-3.3 點頭獨源紅；S-3.4 枚舉五值；S-3.5 非高影響句不逼貼 | T-8 |
| R-4 過期 Assumption 擋 G2 | S-4.4 模板／範例 Assumption 四欄地板 | T-3（教師）＋ T-8（牙） |
| R-4（續） | S-4.1 過期 open → spec-gate exit 1；S-4.2 resolved 放行；S-4.3 oc-accepted 放行 | T-9 |
| R-5 Human verdict 一行看出角色與場 | S-5.3 模板／範例不加 Actor Coverage 全表 | T-7 |
| R-5（續） | S-5.1 殘行 ACCEPTED+日期紅；S-5.2 完整行綠 | T-8 |
| R-6 Stage 1 痛點到 Stage 4 都有去向 | S-6.4 模板／範例不發第二鏈編號 | T-4 |
| R-6（續） | S-6.1 缺表或去向空白紅；S-6.2 本方案處理必有 R/S；S-6.3 非處理落到 OOS／limit／slug | T-9 |
| R-7 出貨留下回看四欄 | S-7.1／S-7.2 Exit 缺欄紅；S-7.3 結果走 history-append、不另造 lookback.md | T-8 |
| R-8 核准後讀得到事實且方案檔仍禁 | S-8.1 同檔 `## Evidence manifest` 五欄（教師半） | T-5 |
| R-8（續） | S-8.1 核准=是放行 Read；S-8.2 2–7 仍擋；S-8.3 未核禁讀 | T-10 |
| R-8（續） | S-8.4 ticket／SOP 解法建議不得當 Observed | T-8 |
| R-9 Fast 寫規格前收完六問 | S-9.2 等待被顯示成完成必須命中第 3 問 | T-6 |
| R-9（續） | S-9.1 空白六問紅；S-9.3 命中無去向紅；S-9.4 全否純視覺可 Fast；S-9.5 full 缺表不誤殺 | T-9 |

35 條 S 皆被至少一個 T 承接。M-1～M-11 是活教師改口，由上列對應 T 落地，不另切 T。

### Verify 開工前原樣跑（2026-09-13；教師與牙尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1 | `_templates/1-discussion.md` 無 `## Requested solution`；S4-accept 仍寫「畫面/端點/檔案/log」；example Goals 仍有「登入後／點擊／一眼可見」→ assert 紅 | ③綠不了但方向對 |
| T-2 | N3-probe 仍是「一次只問一題、附推薦答案」；無字面 `發現｜`／`裁決｜`／「禁附推薦」→ assert 紅 | ③方向對 |
| T-3 | S1-survey 仍寫「認可後的清單 = 本次已核事實」；模板無四欄字面、4-spec 模板無 `## Assumption refs` → assert 紅 | ③方向對 |
| T-4 | 2-decision／4-spec 模板無 disposition 去向表 → assert 紅；`RW-[0-9]` 本已零命中（守住即可） | ③方向對（表尚未落地） |
| T-5 | 模板／example 無 `## Evidence manifest` → assert 紅 | ③方向對 |
| T-6 | 4-spec 模板無 `## Fast early risk triage`；`scripts/fixtures/discovery-gaps/fast-wait-shown-as-done.md` 不存在 → assert 紅 | ③方向對 |
| T-7 | 3-prototype 模板 Human verdict 無 `role=`／`scenario=` → assert 紅 | ③方向對 |
| T-8 | `scripts/fixtures/discovery-gaps/` 指名 md 0 個，`test -ge 9` 紅；7-review 模板無回看四欄 | ③方向對 |
| T-9 | 指名 spec-gate fixture 0 個，`test -ge 6` 紅 | ③方向對 |
| T-10 | 現況 guard 對非 `skills/dev-talk/` 一律 exit 0；`2-decision` Read 不能 exit 2 → assert 紅 | ③方向對 |

## T-1 讓 Stage 1 分欄：結果進 Goals、構想進 Requested solution
- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.3
- Files: _templates/1-discussion.md, skills/dev-talk/nodes/S4-accept.md, example/contract-expiry-reminder/1-discussion.md
- Verify: `python3 -c "from pathlib import Path; t=Path('_templates/1-discussion.md').read_text(); s=Path('skills/dev-talk/nodes/S4-accept.md').read_text(); e=Path('example/contract-expiry-reminder/1-discussion.md').read_text(); assert '## Goals' in t and '## Requested solution' in t; g=t.split('## Goals',1)[1].split('##',1)[0]; assert '畫面' not in g and 'API' not in g; ac=t.split('驗收雛形',1)[1][:800]; assert '畫面路徑 | API 端點' not in ac; assert '畫面/端點/檔案/log' not in s; assert '結果' in s; goals=e.split('## Goals',1)[1].split('##',1)[0]; assert '登入後' not in goals and '點擊可直達' not in goals and '一眼可見' not in goals; assert '## Requested solution' in e and '未定案' in e.split('## Requested solution',1)[1].split('##',1)[0]; il=e.split('## Interview Log',1)[1]; assert '最低成本的呈現面' not in il; print('T-1-ok')"`
  開工前 2026-09-13：無 `## Requested solution`，S4-accept 仍鎖通道，example Goals 仍把登入／點擊當目標 → AssertionError（③）。
- Blocked-by: —
- Intent: 日常開討論稿時，人先寫「要達成什麼結果」，解法構想另欄且標未定案；抄 example 時不再把「登入就能看到 dashboard」當成 Goal。改的是 Stage 1 模板、S4 問句與完整範例的 Goals／Requested solution／Interview 結，不是畫黑名單、不是新開檢查家族。不會變成「看到 dashboard／API 這兩個詞就紅」、不會改七關編號、不會在本 hop 改 4-spec。
- Boundaries: 只准改 Files 三檔。1-discussion 同檔欄擁有節名 `## Goals`／`## Requested solution`；Goals 指令與 S4-accept 不得再要求畫面／API／元件通道候選。禁止 dashboard／API 字面黑名單（S-1.4 另由 T-8 守）。禁止新造 `check-discovery-gaps.sh`。禁止改 `STATUS.md`／`HISTORY.md`／本 slug `4-spec.md`。example 若仍提 dashboard／卡片／URL，只准出現在 Requested solution 且標未定案。Actor=採用者／G1 reviewer；Goal=構想不能混成目標；Human decision=把構想搬到 Requested solution；Authority=分欄形狀＋G1 抽查；Recovery=搬句後重讀，不要改 Goals 去鎖畫面。

## T-2 讓發現題帶「發現｜」且禁推薦、裁決題帶「裁決｜」且可附選
- [ ] 未完成
- Covers: R-2 / S-2.1
- Files: skills/dev-talk/nodes/N3-probe.md, skills/dev-talk/SKILL.md, guides/guide-dev-talk.html
- Verify: `python3 -c "from pathlib import Path; n=Path('skills/dev-talk/nodes/N3-probe.md').read_text(); k=Path('skills/dev-talk/SKILL.md').read_text(); g=Path('guides/guide-dev-talk.html').read_text(); assert '發現｜' in n and '禁附推薦' in n and '裁決｜' in n; assert '一次只問一題、附推薦答案' not in n; assert '連續兩輪無新問題' in n and ('輔助' in n or '不是完成條件' in n or '只當輔助' in n); assert ('發現｜' in k or '發現｜' in g) and ('裁決｜' in k or '裁決｜' in g); print('T-2-ok')"`
  開工前 2026-09-13：N3 L22–L23 仍把附推薦當硬規則 → assert 紅（③）。
- Blocked-by: T-1
- Intent: 日常被問「上次真的怎麼做」時，問句本身不再先塞一個答案讓人挑；要做取捨時才看到 `裁決｜` 和選項。改的是 N3 硬規則與指南／SKILL 入口摘要的對稱句，不是事後從 1-discussion 還原整場對話。不會變成發現題也要附推薦、不會把「連續兩輪無新問題」繼續當唯一完成條件、不會新開牙家族。
- Boundaries: 只准改 Files 三檔（N3 正本＋兩處指南對稱句）。發現題路徑必須含字面 `發現｜` 與「禁附推薦」；裁決題路徑必須含字面 `裁決｜` 且可附選項／差異／推薦。完成條件改為必查面已覆蓋、關鍵反例已問、證據缺口已顯性化；「連續兩輪無新問題」只標輔助。禁止要求從最終 md 還原對話（Known limit ①）。禁止本 T 改 `check-realworld.sh`（前綴對稱牙屬 T-8）。禁止改七關結構。Actor=訪談對象／討論 agent；Goal=現況題不被錨定；Human decision=答開放題，不從推薦裡挑；Recovery=重寫為 `發現｜` 開放題再問。

## T-3 讓高影響主張回到來源或 Assumption 四欄，且 4-spec 看得到 refs 表
- [ ] 未完成
- Covers: R-3 / S-3.3; R-4 / S-4.4
- Files: skills/dev-talk/nodes/S1-survey.md, _templates/1-discussion.md, _templates/2-decision.md, _templates/4-spec.md, example/contract-expiry-reminder/1-discussion.md
- Verify: `python3 -c "from pathlib import Path; s=Path('skills/dev-talk/nodes/S1-survey.md').read_text(); t1=Path('_templates/1-discussion.md').read_text(); t2=Path('_templates/2-decision.md').read_text(); t4=Path('_templates/4-spec.md').read_text(); e=Path('example/contract-expiry-reminder/1-discussion.md').read_text(); assert '認可後的清單 = 本次「已核事實」' not in s; assert any(x in s for x in ['認可 ≠','認可不等於','不是來源','不得當來源']); cols=['若為假影響什麼','影響級','怎麼驗']; assert all(c in t1 or c in t2 for c in cols); assert all(c in e for c in cols); assert ('何時' in t1 or '由誰驗' in t1 or '何時' in t2); assert '## Assumption refs' in t4 and 'oc-accepted' in t4 and 'deadline' in t4.lower(); print('T-3-ok')"`
  開工前 2026-09-13：S1-survey L28–L29 仍把認可當已核事實；模板無四欄、無 refs 表 → assert 紅（③）。
- Blocked-by: T-2
- Intent: 日常點頭之後，清單不能自動變成「已核事實」；高影響假設要寫得出「若為假會怎樣／多痛／怎麼驗／誰在何時驗」，Stage 4 用一張 refs 表讓腳本看得見引用、期限與 status。改的是 S1-survey 升格句、討論／決策模板地板與 4-spec 模板的 `## Assumption refs`，不是在本 T 擋 G2。不會變成每一句 Context 都要貼枚舉、不會另造 G2 CLI、不會把過期假設放進 realworld 當唯一 Gate。
- Boundaries: 只准改 Files 五檔。S1-survey 擁有「認可 ≠ 來源升格」；1-discussion／2-decision 擁有 Assumption 四欄字面（若為假影響什麼／影響級／怎麼驗／何時／由誰驗）；4-spec 模板擁有 `## Assumption refs` 三欄（引用／deadline／status∈{open,resolved,oc-accepted}），deadline=`YYYY-MM-DD` 或 `stage-2`／`stage-3`。高影響抽樣只鎖 R-3 四條（DD-1）；已核 `path:L` 且無「風險=高」不要求枚舉。禁止本 T 改 `check-spec-gate.sh`（過期 open 擋點屬 T-9）。禁止全句枚舉。禁止新造檢查家族。Actor=討論 agent／G1 reviewer；Goal=點頭不是驗證營運事實；Human decision=補可重開 path 或改標 Assumption+期限；Recovery=改標或補 path，不要把「使用者點頭」寫進來源欄。

## T-4 讓 Stage 2／4 用原文片段對帳痛點去向，且不發第二鏈編號
- [ ] 未完成
- Covers: R-6 / S-6.4
- Files: _templates/2-decision.md, _templates/4-spec.md, example/contract-expiry-reminder/2-decision.md, example/contract-expiry-reminder/4-spec.md
- Verify: `python3 -c "from pathlib import Path; import re; paths=['_templates/2-decision.md','_templates/4-spec.md','example/contract-expiry-reminder/2-decision.md','example/contract-expiry-reminder/4-spec.md']; t2=Path('_templates/2-decision.md').read_text(); t4=Path('_templates/4-spec.md').read_text(); blob=''.join(Path(p).read_text() for p in paths); assert '本方案處理' in t2 or '本方案處理' in t4; assert '## Real-world Disposition' in t4; assert all(x in t4 for x in ['引用','去向','下落']); assert re.search(r'RW-[0-9]', blob) is None; print('T-4-ok')"`
  開工前 2026-09-13：4-spec 模板無 `## Real-world Disposition` → assert 紅（③）。`RW-[0-9]` 現已零命中，落地後仍須為空。
- Blocked-by: T-3
- Intent: 日常從 Stage 1 抄到 Stage 4 時，每一條高影響痛點還在，去向與下落寫在同一張表，引用用原文不是新編號。改的是 2-decision／4-spec 模板與 example 的 disposition 表頭，不是本 slug 已核准的 4-spec。不會變成發 `RW-1` 這種第二鏈、不會在本 T 改 spec-gate、不會把本方案處理的下落留白。
- Boundaries: 只准改 Files 四檔。2-decision 表：引用 Stage 1 原文片段＋去向五值（本方案處理／刻意維持／Non-Goal／另開 slug／仍待驗）＋一句理由。4-spec 必有 `## Real-world Disposition` 三欄：引用／去向／下落。本方案處理 → 下落至少一條 `R-` 或 `S-`（Decision 4A）；其餘落到 Out of Scope／Known limit／後續 slug。引用欄是原文片段，禁止第二鏈編號（`RW-[0-9]` 對 Files 四檔必須零命中）。禁止改本 slug `4-spec.md`／`2-decision.md`。禁止本 T 改 `check-spec-gate.sh`（缺表／空白去向屬 T-9）。禁止改 1-discussion 另發 Journey／Actor 第二鏈。Actor=收斂者／G2 reviewer；Goal=痛點不能無聲消失；Human decision=補表或標刻意維持／Non-Goal；Recovery=按 2-decision 抄進 4-spec 並填 S-id 或 Out of Scope。

## T-5 讓 1-discussion 同檔出現 Evidence manifest 五欄
- [ ] 未完成
- Covers: R-8 / S-8.1
- Files: _templates/1-discussion.md, example/contract-expiry-reminder/1-discussion.md
- Verify: `python3 -c "from pathlib import Path; t=Path('_templates/1-discussion.md').read_text(); e=Path('example/contract-expiry-reminder/1-discussion.md').read_text(); assert '## Evidence manifest' in t and '## Evidence manifest' in e; headers=['想找哪類','為什麼','擬路徑','owner 核准','已讀']; assert all(h in t for h in headers); assert '是' in t and '未核' in t and '禁' in t; print('T-5-ok')"`
  開工前 2026-09-13：兩檔皆無該節 → assert 紅（③）。本 T 只證節與表頭在；核准=是的 Read 放行屬 T-10。
- Blocked-by: T-4
- Intent: 日常討論要讀一份事實檔之前，先在同一份 1-discussion 列出「想找哪類／為什麼／哪條路徑／owner 有沒有核／讀了沒」。改的是模板與範例的同檔五欄，不是另造 `evidence-manifest.md`。不會變成未核路徑可以先列目錄當已授權、不會讓核准=是覆寫 2–7 禁令、不會在本 T 改 guard。
- Boundaries: 只准改 Files 兩檔。節名字面 `## Evidence manifest`，與 1-discussion **同檔**。表頭五欄鎖定：想找哪類／為什麼／擬路徑或來源／owner 核准／已讀。`owner 核准` ∈ {是, 未核, 禁}。禁止另造永久 `evidence-manifest.md`（已拒 6B）。禁止本 T 改 `hooks/devtalk-guard.sh`（Read 分支屬 T-10）。禁止把 2-decision／3-prototype／4-spec／5-tasks／6-implementation-notes／7-review 標成 Observed。1-discussion 同檔欄擁有列；owner 擁有核准格。Actor=討論 agent；Goal=先列想找什麼再等核准；Human decision=owner 改核准=是之後才讀；Recovery=核准格空白就停，不要往下 Read。看過擬路徑 ≠ 已授權。

## T-6 讓 Fast 進 Stage 4 前填完六問，且等待被顯示成完成必須命中第 3 問
- [ ] 未完成
- Covers: R-9 / S-9.2
- Files: _templates/4-spec.md, skills/dev-flow/SKILL.md, scripts/fixtures/discovery-gaps/fast-wait-shown-as-done.md
- Verify: `python3 -c "from pathlib import Path; t=Path('_templates/4-spec.md').read_text(); s=Path('skills/dev-flow/SKILL.md').read_text(); assert '## Fast early risk triage' in t; assert t.find('## Fast early risk triage') < t.find('## ADDED Requirements'); assert all(q in t for q in ['改變下一步','改權限','改等待','改角色交接','改系統外動作','改中斷恢復']); assert '六問' in s; f=Path('scripts/fixtures/discovery-gaps/fast-wait-shown-as-done.md').read_text(); assert '等待被顯示成完成' in f and '是' in f; assert any(x in f for x in ['full','fast+mini','OC']); dest=f.lower(); assert '去向' in f and '待裁' not in dest.split('去向',1)[-1][:80]; print('T-6-ok')"`
  開工前 2026-09-13：模板無六問節；fixture 檔不存在 → assert 紅（③）。空白表／命中無去向的 spec-gate 屬 T-9。
- Blocked-by: T-5
- Intent: 日常 Fast 想直接開寫 4-spec 時，先答完六題「這次有沒有改下一步／權限／等待完成語意／交接／系統外／中斷恢復」；只改一個狀態字、把等待顯示成完成，第 3 題必須是「是」，去向不能再寫 Fast。改的是 4-spec 模板節、SKILL Fast 分診句，以及 AC-9 同形對照稿。不會變成一律升 full、不會改七關「Fast 可跳 1–3」、不會在本 T 改 spec-gate。
- Boundaries: 只准改 Files 三檔。節名字面 `## Fast early risk triage`，必須出現在 `## ADDED Requirements` 之前（DD-3）。六問字面鎖定：改變下一步？／改權限／核准語意？／改等待／完成語意？／改角色交接？／改系統外動作？／改中斷恢復？每問答 `是` 或 `否` 加一句。去向 ∈ {Fast, full, fast+mini, OC}。全否且已有 approved spec 且不改語意的純視覺 → 去向=`Fast`（OC-6）。任一「是」→ 去向 ∈ {full, fast+mini, OC}，不可空白開寫。禁止改成 7B（一律升 full）。禁止本 T 改 `check-spec-gate.sh`（空白／無去向擋點屬 T-9）。禁止改七關編號。fixture 第 3 問必須含「等待被顯示成完成」，去向不得是 `Fast` 或空白／待裁。Actor=Fast 實作者／owner；Goal=等待誤標不能當純視覺 Fast；Human decision=owner 裁 full／mini／OC；Recovery=填六問與去向後才開寫 R/S。

## T-7 讓 Human verdict 一行含 role 與 scenario，且不加 Actor Coverage 全表
- [ ] 未完成
- Covers: R-5 / S-5.3
- Files: _templates/3-prototype.md, example/contract-expiry-reminder/3-prototype.md
- Verify: `python3 -c "from pathlib import Path; t=Path('_templates/3-prototype.md').read_text(); e=Path('example/contract-expiry-reminder/3-prototype.md').read_text(); assert 'role=' in t and 'scenario=' in t; assert 'Human verdict:' in t; assert '本包必填全表' not in t and '本包必填全表' not in e; assert 'Actor Coverage' not in t or '必填' not in t.split('Actor Coverage',1)[-1][:80]; print('T-7-ok')"`
  開工前 2026-09-13：模板只有 `ACCEPTED | REVISE | NOT_REVIEWED`，無 `role=`／`scenario=` → assert 紅（③）。殘行牙屬 T-8。
- Blocked-by: T-6
- Intent: 日常後讀 3-prototype 時，只看 Human verdict 那一行就能答「驗了誰、驗了哪場」，不必翻前後文，也不必填一張角色覆蓋全表。改的是 3-prototype 模板與 example 的 verdict 指令。不會變成 Agent 代填 attestation、不會加 Actor Coverage 全表、不會在本 T 改 realworld 牙。
- Boundaries: 只准改 Files 兩檔。Human verdict 本文格式鎖定 `<ENUM> | role=<Actors 表角色> | scenario=<AC-id 或 Demo Script 場景名>`（DD-7）。既有 attestation 規則（人類親填、`test-only human fixture` 拒收）必須仍在。禁止加「本包必填」的 Actor Coverage 全表（已拒 8B）。禁止 Agent 寫／改 attestation 行。禁止本 T 改 `check-realworld.sh`（殘行牙屬 T-8）。Actor=後讀 3-prototype 的人；Goal=一行內看出角色與場景；Human decision=補 role／scenario 或改 NOT_REVIEWED；Authority=牙擋殘行、人填 attestation；Recovery=改成 `ACCEPTED | role=… | scenario=…` 後重跑。

## T-8 把 Goals／前綴／主張／verdict／lookback 形狀掛進 check-realworld.sh
- [ ] 未完成
- Covers: R-1 / S-1.2, S-1.4; R-2 / S-2.2, S-2.3; R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5; R-4 / S-4.4; R-5 / S-5.1, S-5.2; R-7 / S-7.1, S-7.2, S-7.3; R-8 / S-8.4
- Files: scripts/check-realworld.sh, _templates/7-review.md, example/contract-expiry-reminder/7-review.md, scripts/fixtures/discovery-gaps/
- Verify: `n=$(python3 -c "from pathlib import Path; p=Path('scripts/fixtures/discovery-gaps'); need=['goals-dashboard-in-wrong-column.md','goals-outcome-with-requested-dashboard.md','probe-decision-with-options.md','nod-as-only-source.md','enum-unknown.md','lookback-missing-threshold.md','ticket-solution-as-fact.md','verdict-accepted-date-only.md','verdict-complete-line.md']; print(sum(1 for x in need if (p/x).is_file()))"); test "$n" -ge 9 && python3 -c "from pathlib import Path; t=Path('_templates/7-review.md').read_text(); e=Path('example/contract-expiry-reminder/7-review.md').read_text(); assert all(c in t and c in e for c in ['回看日期','回看 owner','資料來源','低於何值重開']); assert 'lookback.md' not in t and 'history-append.sh' in t" && bash scripts/check-realworld.sh`
  開工前 2026-09-13：指名 fixture 0 個，`test -ge 9` 紅；7-review 無四欄（③）。落地後主樹 `check-realworld.sh` 必須 exit 0，且 `MIN_CHECKS` 等於加完後實數。負向 fixture 仍走同一入口，exit ≠ 0 且含各 S 指定字樣（錯欄／點頭／枚舉／role|scenario／低於何值重開／不當事實）；正向 fixture exit 0。舊 7-review 無回看節不發動。
- Blocked-by: T-7
- Intent: 日常跑同一支 `check-realworld.sh` 時，錯欄構想、單邊前綴、點頭當來源、殘行 verdict、已宣稱 shipped 卻缺回看門檻、把 ticket 解法標成 Observed 會紅；合法結果句出現 dashboard、裁決題附選項、非高影響 Context 不貼枚舉、完整 verdict 行、齊全四欄則綠。改的是既有牙射程、7-review Exit 四欄與 fixture，不是新 CLI。不會變成過期 Assumption 的 G2 Gate（那是 T-9）、不會另造 lookback.md、不會用黑名單誤殺領域詞、不會把 MIN_CHECKS 寬放下限。
- Boundaries: 只准改 Files 所列。入口字面必須仍是 `bash scripts/check-realworld.sh`（可選第一參數 = 隔離 root，與現況相同；fixture 檔可放進隔離複本或由同支腳本加讀 `scripts/fixtures/discovery-gaps/`，禁止新開 `check-discovery-gaps.sh`）。realworld 擁有教師地板＋有條件填檔（Goals 錯欄、前綴對稱、高影響枚舉／來源 XOR 期限、verdict 一行、lookback 四欄、ticket 解法不當事實）。禁止把過期 Assumption 擋點放進本牙（屬 spec-gate）。`MIN_CHECKS` 必須改成加完後實際檢查數，不是寬放下限。S-7.2 只在 7-review 已出現回看節或四欄名時發動；舊檔無節不誤殺（DD-6）。S-7.3：活教師（7-review 模板／指南 lookback 句／example）零命中「另造 lookback.md」，且含 `history-append.sh`。S-3.5／OC-5：非高影響 Context 句不貼枚舉不得紅。S-2.2 用隔離複本刪掉 `發現｜` 或 `裁決｜` 其中一邊，同一入口必紅。禁止改 `check-spec-gate.sh`／`devtalk-guard.sh`。禁止改本 slug 4-spec。Actor=G1 reviewer／owner；Goal=教師地板與填檔形狀同一入口可紅可綠；Authority=牙驗形狀、語意仍是人抽查；Recovery=搬構想／補來源或期限／補 role+scenario／補四欄後重跑。

## T-9 把 Assumption refs／disposition／Fast 六問掛進 check-spec-gate.sh
- [ ] 未完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3; R-6 / S-6.1, S-6.2, S-6.3; R-9 / S-9.1, S-9.3, S-9.4, S-9.5
- Files: scripts/check-spec-gate.sh, scripts/fixtures/discovery-gaps/assumption-expired-open.md, scripts/fixtures/discovery-gaps/assumption-resolved.md, scripts/fixtures/discovery-gaps/fast-blank-triage.md, scripts/fixtures/discovery-gaps/fast-hit-no-dest.md, scripts/fixtures/discovery-gaps/fast-visual-all-no.md, scripts/fixtures/discovery-gaps/disposition-blank.md
- Verify: `n=$(python3 -c "from pathlib import Path; p=Path('scripts/fixtures/discovery-gaps'); need=['assumption-expired-open.md','assumption-resolved.md','fast-blank-triage.md','fast-hit-no-dest.md','fast-visual-all-no.md','disposition-blank.md']; print(sum(1 for x in need if (p/x).is_file()))"); test "$n" -ge 6 && python3 -c "import subprocess; gate=lambda path: (lambda r: (r.returncode, r.stdout+r.stderr))(subprocess.run(['bash','scripts/check-spec-gate.sh',path],capture_output=True,text=True)); c,o=gate('scripts/fixtures/discovery-gaps/assumption-expired-open.md'); assert c==1 and any(x in o for x in ['Assumption','過期','open']); c,o=gate('scripts/fixtures/discovery-gaps/assumption-resolved.md'); assert c==0; c,o=gate('docs/dev/requirement-discovery-gaps/4-spec.md'); assert c==0; c,o=gate('scripts/fixtures/discovery-gaps/fast-blank-triage.md'); assert c==1 and any(x in o for x in ['Fast','六問','triage']); c,o=gate('scripts/fixtures/discovery-gaps/fast-hit-no-dest.md'); assert c==1 and any(x in o for x in ['去向','full','mini','OC']); c,o=gate('scripts/fixtures/discovery-gaps/fast-visual-all-no.md'); assert c==0; c,o=gate('scripts/fixtures/discovery-gaps/disposition-blank.md'); assert c==1 and any(x in o for x in ['Disposition','去向']); print('T-9-ok')"`
  開工前 2026-09-13：fixture 不存在，`test -ge 6` 紅（③）。落地後本 slug 4-spec（full、有 refs oc-accepted、有 disposition、無六問表）必須仍 exit 0（S-4.3／S-6.2／S-6.3／S-9.5）。resolved／visual-all-no fixture 須先滿足既有 C1–C6，避免「別項紅」假冒本項綠。
- Blocked-by: T-8
- Intent: 日常送 G2 時，過期還標 open 的假設、full 卻沒 disposition、Fast 六問空白或命中卻沒去向，會在同一支 `check-spec-gate.sh` 被擋下來；已驗 resolved、Owner Call 接受、純視覺全否、以及本檔這種 full lane，不會被新項誤殺。改的是既有 G2 形狀 Gate 加項與 fixture，不是第二支 G2 CLI、不是語意審查。不會判斷「這條假設合不合理」、不會讓 Fast 項打到 full、不會動 C1–C6 舊契約。
- Boundaries: 只准改 Files 所列。入口字面必須仍是 `bash scripts/check-spec-gate.sh <4-spec.md>`。spec-gate 擁有 4-spec 送審通過／失敗；新項與 C1–C6 同檔（建議 C7 Assumption refs、C8 Fast triage、C9 disposition；頂註「六項」改成加完後實數）。只讀、不寫 4-spec、不判語意。Fast 項僅 `lane: fast` 發動；full 缺六問表 no-fire（S-9.5）。status=open 且期限已過（過去日或 `stage-N` 而本檔已在第 4 站）且無 oc-accepted → exit 1。resolved／oc-accepted 不得只因該列 exit 1。full 缺 `## Real-world Disposition` 或去向空白 → exit 1；本方案處理下落必須有 `R-` 或 `S-` 開頭 id；非處理下落必須有 Out of Scope／Known limit／slug。禁止新開第二支 G2 CLI。禁止改 `check-realworld.sh`／`devtalk-guard.sh`。禁止改本 slug 4-spec 正文（本 T 只拿它當正向）。Actor=G2 reviewer；Goal=過期假設／未分診 Fast／痛點消失進不了送審；Human decision=驗轉 resolved、寫 oc-accepted、補表或去向；Authority=spec-gate 機械拒送審；Recovery=改 status 或補表後重跑，不要口頭說「知道有假設」。

## T-10 讓 talk 期 Read 放行核准路徑、仍禁方案檔與未核路徑
- [ ] 未完成
- Covers: R-8 / S-8.1, S-8.2, S-8.3
- Files: hooks/devtalk-guard.sh
- Verify: `python3 -c "import json,subprocess,pathlib; g='hooks/devtalk-guard.sh'; run=lambda path: (lambda r: (r.returncode, r.stderr))(subprocess.run(['bash',g],input=json.dumps({'tool_name':'Read','tool_input':{'file_path':str(pathlib.Path(path).resolve())}}),text=True,capture_output=True)); c1,e1=run('_templates/1-discussion.md'); c2,e2=run('docs/dev/requirement-discovery-gaps/2-decision.md'); c3,e3=run('notes/review-requirement-discovery-gaps.md'); assert c1==0; assert c2==2 and any(x in e2 for x in ['2-decision','4-spec','方案檔']); assert c3==2; print('T-10-ok')"`
  開工前 2026-09-13：guard 對非 `skills/dev-talk/` 一律 exit 0，第二段 assert `c2==2` 紅（③）。落地後必須在 talk 游標在時才發動 Read 分支；游標不在則維持今日只掃 `skills/dev-talk/*` 寫入洩漏。S-8.1 的核准=是列以當下 slug（或測試複本）1-discussion `## Evidence manifest` 為準。
- Blocked-by: T-9
- Intent: 日常討論期要核一份教師或原始碼時，owner 在 manifest 勾「是」就能 Read 到事件／行為／結果；有人把 2-decision／4-spec 寫進擬路徑，即使核准格誤寫「是」也進不去；未核或空白的路徑不能當已授權 evidence。改的是同一支 `devtalk-guard.sh` 加 Read 分支，不是新開 `check-evidence-allow.sh`。不會變成主機層 OS hook、不會放行 2–7、不會拿掉既有寫入洩漏掃描。
- Boundaries: 只准改 `hooks/devtalk-guard.sh`。guard 擁有討論期擋讀。talk 期判定 = 既有 talk 游標檔存在（`check-devtalk-graph.sh --write-cursor` 已寫的那種，不新造 session 格式）。放行：manifest 核准=是的路徑。仍禁 2-decision／3-prototype／4-spec／5-tasks／6-implementation-notes／7-review（含 html twin）；核准=是不能覆寫這條禁令。未核或格空白 → Read exit 2；該路徑也不得當 S-3.1 主張牙的已授權來源。寫入洩漏掃描保留；Read 只在 talk 游標在時發動。游標不在 → 維持今日非 `skills/dev-talk/` 靜默放行。禁止新開 `check-evidence-allow.sh`。禁止本 feat 新造 OS hook（Known limit ②）。禁止改 `check-realworld.sh`／`check-spec-gate.sh`。S-8.4 不在本 T（屬 T-8 主張牙）。Actor=討論 agent／owner；Goal=核准後讀得到、方案檔仍進不去；Human decision=owner 才能改核准=是；Authority=guard 硬擋；Recovery=先列「想找哪類＋為什麼」等 owner 核，或從擬路徑刪掉方案檔。核准格空白 = 禁讀。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential，不開 parallel | Feature Risk high（公開檢查 exit 契約＋討論期讀取權限＋過期假設假綠）。T-1／T-3／T-5 都改 `_templates/1-discussion.md`，硬順序大於省一波。tip 預設 sequential，須明確啟用才改 parallel。 | `_templates/5-tasks.md` `execution.mode` 缺省 sequential；4-spec Verification Profile `Risk: high` | 棄 T-8 ∥ T-9 ∥ T-10 平行。三支牙檔案不重疊，可平行，但本 hop 選保守序：先教師再牙。 |
| 十個 T 不是三十五刀 | 可觀測行為是「人旅程上一格多了什麼」加「同一支牙多咬哪種錯稿」，不是一 S 一 T。35 刀會讓 Files 重複、Verify 碎片。 | 4-spec R-1～R-9；模板「一個 T 一個關注點」；Variant C brief ~8–10 T | 棄「每個 S 一 T」。 |
| 序 = 人旅程，牙最後 | Variant C：Goals／Requested solution → 發現／裁決前綴 → Assumption refs → disposition → evidence manifest → Fast 六問 → Stage 3 verdict 一行 → 牙延射程最後。 | owner brief Variant C；4-spec 行為流程圖 R-1→R-9 | 棄「先三支牙再改教師」（IBV 那序）。棄按腳本家族橫切整份（會變成 DB→牙→模板的水平切）。 |
| T-1 分欄教師與 T-8 錯欄牙分開 | S-1.1／S-1.3 的可觀測是模板／example 改口；S-1.2／S-1.4 的可觀測是同一支 realworld 對 fixture 的紅／綠。併一刀會讓 Verify 同時跑兩套不相干指令。 | 4-spec S-1.1 觀測「三檔原文」vs S-1.2 觀測「檢查 exit」；模板「Verify 兩套不相干指令 → 拆 T」 | 棄「R-1 四條 S 同一 T」。 |
| T-3 含 S-3.3 教師半 + S-4.4 地板 | 人旅程「Assumption refs」這一格：認可不再升格、四欄地板、refs 表頭是同一關注點（假設怎麼被看見）。G2 擋點仍留 T-9。 | 4-spec R-3／R-4；DD-2 refs 表形；M-5／S-4.4 | 棄「S1-survey 一 T、四欄一 T、refs 表一 T」（同一假設旅程、Files 重疊 1-discussion）。 |
| T-5 只切 manifest 教師半 | S-8.1 的 THEN 是 guard Read exit 0，但人旅程先要同檔五欄才有核准格可讀。教師與 Read 牙拆開，避免 Verify 混「節在不在」與「hook exit」。 | 4-spec S-8.1 觀測「guard exit」；DD-5 節名同檔；Variant C「evidence → … → teeth last」 | 棄「manifest + guard 同一 T」（Files 會同時改模板與 hook，Verify 兩套指令）。 |
| lookback 折進 T-8 | brief 人旅程沒有獨立「Exit 回看」格；S-7.* 的完成宣稱是 realworld 地板＋history-append 入口，與 T-8 同一支牙。 | 4-spec S-7.1／S-7.2 觀測「check-realworld」；S-7.3 觀測 rg＋append；DD-6 | 棄獨立 T-lookback（會超過 ~10 T，且 Verify 仍是同一支 realworld）。 |
| T-8／T-9／T-10 按牙拆、不按 S 拆 | 九缺口牙只這三支。同一入口的開火／不開火是一個關注點。T-8 Files 含 7-review 是因為 lookback 地板與牙同一刀。 | 4-spec Required layers；Dependencies 三支 justification；「不得新造第二家族」 | 棄「S-1.2 一 T、S-3.1 一 T、S-5.1 一 T」（同一 `check()` 家族）。棄 T-9 與 T-10 合併（Verify 會跑 spec-gate 與 guard 兩套不相干指令）。 |
| T-9 Blocked-by T-8、T-10 Blocked-by T-9 | sequential 硬鏈。T-9 正向吃本 slug 4-spec（不改它）與 T-3／T-4／T-6 落地後的模板形；T-10 吃 T-5 的 manifest 形。 | 本檔 Blocked-by 拓撲；4-spec S-9.5 用本檔測 | 棄 T-9 只掛 T-6（忽略 disposition／refs 教師）。棄 T-10 與 T-8 平行（本 hop 不開 parallel）。 |
| 本 hop 不切 G3／STATUS／Stage 6／4-spec 改文 | owner brief：只寫 Stage 5 任務板；status=draft；不發明 G3。 | owner Stage 5 brief；4-spec Out of Scope | 棄現在寫 `6-implementation-notes.md` 或改 `STATUS.md` 表列。棄 N6 把 status 轉 approved（本 hop 交 draft）。 |
