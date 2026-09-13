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

# 5. 任務 — 九缺口教師面（Variant A）

> 把 4-spec（G2 PASS、#278 = `bc627b463fd2e9c85f75b9ebbbdb38dca20f830e`、R-1…R-9／S-1.1…S-9.5）切成可派工縱切。
> 本 hop **只寫任務板**，不落地 Stage 6 守衛碼、不改正本教師、不 bump plugin、不發版、不改 `STATUS.md`／`HISTORY.md`／`4-spec`／`3-prototype`、不發明 G3。
> 模式：sequential（Feature Risk high／方法論教師）。tracer：先讓五份模板看得見新欄，再改 skills 問法與 example 抄本，最後同一三支牙開火。

## 開工前提

Stage 4 已核准。G2 PASS 已在 tip（#278）。本 hop 不改 `4-spec.md`／`4-spec.html`。牙只延 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`，禁止新造 `check-discovery-gaps.sh`。欄位字面鎖定 Decision 1A–8A／DD-1～DD-8，不重開、不發明新 R/S。

### N1 R/S 盤點（9 R／35 S）

| R | S | 本 hop T |
|---|---|---|
| R-1 分辨結果與構想 | S-1.1 模板分欄＋S4-accept | T-1（模板）、T-2（S4-accept） |
| R-1（續） | S-1.2 錯欄對照稿紅；S-1.4 領域詞不黑名單 | T-4 |
| R-1（續） | S-1.3 example Goals 不再鎖通道 | T-3 |
| R-2 發現題不先塞推薦 | S-2.1 N3-probe／指南對稱句 | T-2 |
| R-2（續） | S-2.2 刪一邊前綴紅；S-2.3 裁決附選仍綠 | T-4 |
| R-3 高影響主張回來源或期限 | S-3.1～S-3.5 枚舉／來源／點頭／非高影響 | T-4（牙）；S-3.3 技能句在 T-2 |
| R-4 過期假設擋 G2 | S-4.1／S-4.2／S-4.3 spec-gate | T-5 |
| R-4（續） | S-4.4 模板／範例 Assumption 四欄 | T-1、T-3（地板）；T-4（牙） |
| R-5 verdict 一行寫清角色場景 | S-5.1／S-5.2 殘行紅、完整行綠 | T-4 |
| R-5（續） | S-5.3 不做 Actor Coverage 全表 | T-1、T-3 |
| R-6 痛點列逐條有去向 | S-6.1／S-6.2／S-6.3 spec-gate | T-5 |
| R-6（續） | S-6.4 禁第二鏈 `RW-n` | T-1、T-3、T-5（聯合 `rg`） |
| R-7 出貨留回看四欄 | S-7.1／S-7.3 模板／範例＋history-append | T-1、T-3 |
| R-7（續） | S-7.2 已宣稱回看缺欄紅、舊檔無節不發動 | T-4 |
| R-8 核准後讀得到、方案檔仍禁 | S-8.1／S-8.2／S-8.3 guard Read | T-6 |
| R-8（續） | S-8.4 ticket 解法不當 Observed | T-4（與 R-3 同一主張牙） |
| R-9 Fast 寫規格前收完六問 | S-9.1～S-9.5 spec-gate Fast 項 | T-5（牙）；T-1（4-spec 模板表）；T-2（SKILL 入口） |

### Verify 開工前原樣跑（2026-09-13；教師與牙尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1 | 模板無 `## Requested solution`、Goals 仍寫 `畫面路徑 \| API 端點`、7-review 無回看四欄 → assert 紅 | ③綠不了但方向對 |
| T-2 | N3 仍寫「附推薦答案」當硬規則；S4 仍問畫面／端點；S1 仍把認可清單當已核事實 → assert 紅 | ③方向對 |
| T-3 | example Goals 仍把登入／點擊／一眼可見當目標；無 Requested solution → assert 紅 | ③方向對 |
| T-4 | `scripts/fixtures/discovery-gaps/` 對照稿不存在；`check-realworld.sh` 無「構想在錯欄」字樣 → assert 紅 | ③方向對 |
| T-5 | `check-spec-gate.sh` 尚無 C7／C8／C9；Fast／Assumption fixture 不存在 → assert 紅 | ③方向對 |
| T-6 | `devtalk-guard.sh` 尚無 Read／方案檔分支；Read 2-decision 現況 exit 0 → assert 紅 | ③方向對 |

## T-1 讓五份模板長出分欄、四欄、verdict、去向、回看與 Fast 地板
- [ ] 完成
- Covers: R-1 / S-1.1; R-4 / S-4.4; R-5 / S-5.3; R-6 / S-6.4; R-7 / S-7.1, S-7.3; R-9 / S-9.1
- Files: _templates/1-discussion.md, _templates/2-decision.md, _templates/3-prototype.md, _templates/4-spec.md, _templates/7-review.md
- Verify: `python3 -c "from pathlib import Path; t1=Path('_templates/1-discussion.md').read_text(); t2=Path('_templates/2-decision.md').read_text(); t3=Path('_templates/3-prototype.md').read_text(); t4=Path('_templates/4-spec.md').read_text(); t7=Path('_templates/7-review.md').read_text(); assert '## Requested solution' in t1; assert '畫面路徑 | API 端點' not in t1; assert all(x in t1 for x in ['若為假影響什麼','影響級','怎麼驗','何時']); assert 'role=' in t3 and 'scenario=' in t3; assert '本包必填全表' not in t3; assert '## Real-world Disposition' in t2 or '## Real-world Disposition' in t4; assert '## Fast early risk triage' in t4; assert all(x in t7 for x in ['回看日期','回看 owner','資料來源','低於何值重開']); assert 'history-append.sh' in t7; assert 'lookback.md' not in t7; import subprocess; r=subprocess.run(['rg','-n','RW-[0-9]','_templates/2-decision.md','_templates/4-spec.md'],capture_output=True,text=True); assert r.stdout.strip()==''; print('T-1-ok')"`
- Blocked-by: —
- Intent: 日常少一次「空白模板沒地方寫構想／來源／去向／回看」：打開 Stage 1 就能把工作結果和未定案構想分開寫；Assumption 四欄、verdict 角色與哪場、痛點去向、出貨回看、Fast 六問都已經印在紙上。改的是五份空白樣張的欄位地板，不是檢查腳本、也不是範例正文。不會變成 Cursor 擋寫、不會新造檢查家族、不會做 Actor Coverage 全表、不會另造永久 lookback.md。
- Boundaries: 只准改 Files 五份模板的節名／表頭／指令句。禁止新開 `check-discovery-gaps.sh`、禁止改 `STATUS.md`／`HISTORY.md`、禁止發第二鏈編號、禁止把 dashboard／API 寫成 Goals 黑名單、禁止本 hop 落地牙。1-discussion 同檔欄（Goals／Requested solution／Assumption 四欄／Evidence manifest）由模板作者擁有地板字面；2-decision／4-spec disposition 引用必須是 Stage 1 原文片段；7-review Exit 回看結果入口必須是 `history-append.sh`。既有 attestation 牙與 Fast 可跳過 1–3 的七關結構不准拆。Actor=採用者填空白模板；Goal=欄位在、構想不進 Goals；Human decision=把構想寫進 Requested solution；Authority=模板地板，語意仍 G1／G2 抽查；Recovery=缺節就補節名，不要另檔。

## T-2 改 N3／S4／S1／Fast 技能節點的問法與完成條件
- [ ] 完成
- Covers: R-1 / S-1.1; R-2 / S-2.1; R-3 / S-3.3; R-9 / S-9.1, S-9.2
- Files: skills/dev-talk/nodes/N3-probe.md, skills/dev-talk/nodes/S4-accept.md, skills/dev-talk/nodes/S1-survey.md, skills/dev-flow/SKILL.md
- Verify: `python3 -c "from pathlib import Path; n3=Path('skills/dev-talk/nodes/N3-probe.md').read_text(); s4=Path('skills/dev-talk/nodes/S4-accept.md').read_text(); s1=Path('skills/dev-talk/nodes/S1-survey.md').read_text(); sk=Path('skills/dev-flow/SKILL.md').read_text(); assert '發現｜' in n3 and '禁附推薦' in n3 and '裁決｜' in n3; assert '一次只問一題、附推薦答案' not in n3; assert '連續兩輪無新問題' in n3 and ('輔助' in n3 or '不是完成條件' in n3 or '只當輔助' in n3); assert '從哪裡看出結果發生' in s4; assert '畫面/端點/檔案/log' not in s4; assert '認可後的清單 = 本次「已核事實」' not in s1; assert '六問' in sk or 'Fast early risk' in sk; print('T-2-ok')"`
- Blocked-by: T-1
- Intent: 日常少一次被推薦答案錨定：問「上次真的怎麼做」時是開放的發現題；驗收改問結果在哪被看見，不再先塞畫面／API；點頭只代表「你理解了」，不能把清單升成已核事實；Fast 想跳過 1–3 時，寫規格前先答完六問。改的是討論技能四個節點的問法與完成條件。不會變成從最終 1-discussion 還原整場對話當硬 gate，也不會讓討論 agent 去讀 2-decision。
- Boundaries: 只准改 Files 四個節點的做什麼／完成條件與 Fast 入口句。N3 發現路徑必須含字面 `發現｜` 與「禁附推薦」；裁決路徑含 `裁決｜` 且可附選項。S4 改問結果發生處，不鎖通道。S1 認可 ≠ 來源升格（承接 S-3.3）。SKILL Fast 只加進 4 前六問，七關結構不准改（Exception「Fast 合法跳過 1–3」刻意維持）。禁止在這些檔寫入 2-decision／4-spec／5-tasks／G1／G2／G3 下游字眼（既有 `devtalk-guard` 寫入洩漏仍咬）。指南若有「附推薦答案」對稱句，同一 T 改口，不另開檢查家族。游標協定與「不得 talk start／不得寫 1-discussion」維持。Actor=訪談對象／討論 agent；Goal=現況題不被錨定；Human decision=答開放題，不從推薦裡挑；Authority=skill 硬規則；Recovery=已附推薦就重寫成 `發現｜` 再開問。

## T-3 改口完整範例，讓抄本不再把通道當成目標
- [ ] 完成
- Covers: R-1 / S-1.3; R-4 / S-4.4; R-5 / S-5.3; R-6 / S-6.4; R-7 / S-7.1, S-7.3
- Files: example/contract-expiry-reminder/1-discussion.md, example/contract-expiry-reminder/2-decision.md, example/contract-expiry-reminder/3-prototype.md, example/contract-expiry-reminder/4-spec.md, example/contract-expiry-reminder/7-review.md
- Verify: `python3 -c "from pathlib import Path; e1=Path('example/contract-expiry-reminder/1-discussion.md').read_text(); g=e1.split('## Goals',1)[1].split('##',1)[0]; assert '登入後' not in g and '點擊' not in g and '一眼可見' not in g; assert '## Requested solution' in e1; e3=Path('example/contract-expiry-reminder/3-prototype.md').read_text(); assert '本包必填全表' not in e3; e7=Path('example/contract-expiry-reminder/7-review.md').read_text(); assert all(x in e7 for x in ['回看日期','回看 owner','資料來源','低於何值重開']); assert 'history-append.sh' in e7; assert 'lookback.md' not in e7; import subprocess; r=subprocess.run(['rg','-n','RW-[0-9]','example/contract-expiry-reminder/1-discussion.md','example/contract-expiry-reminder/2-decision.md','example/contract-expiry-reminder/4-spec.md'],capture_output=True,text=True); assert r.stdout.strip()==''; print('T-3-ok')"`
- Blocked-by: T-1
- Intent: 日常少抄到一句壞樣張：打開完整範例時，Goals 寫的是「到期前做完續約決定」這類結果，dashboard／卡片／URL 若還要提，只出現在 Requested solution 並標未定案；Exit 看得到誰／何時／用什麼／低於何值重開。改的是 contract-expiry-reminder 五份填好的教師，不是母版檢查腳本。不會把範例重寫成另一個產品，也不會另造 lookback.md。
- Boundaries: 只准改 Files 五份 example md（1／2／3／4／7）。Goals 三句不得再把登入／點擊／一眼可見寫成目標本身；Interview「dashboard 是最低成本的呈現面」不得再當已核目標。3-prototype 不得要求 Actor Coverage 全表；verdict 一行若改口須含 `role=`／`scenario=`，既有 attestation 規則仍在。2-decision／4-spec 引用欄是原文片段，零命中 `RW-[0-9]`。7-review 四欄齊且結果入口是 `history-append.sh`。禁止改 example 的 html twin 當本 T 唯一交付（md 是教師正本）；禁止改 `_templates/`（屬 T-1）與三支牙（屬 T-4～T-6）。Actor=會抄 example 的採用者；Goal=抄結果不抄 Goal=dashboard；Human decision=以改口後範例為抄本；Recovery=Goals 仍鎖通道就同一 T 改到符合。

## T-4 延 check-realworld：錯欄、前綴、主張、verdict 與回看填檔都從同一入口開火
- [ ] 完成
- Covers: R-1 / S-1.2, S-1.4; R-2 / S-2.2, S-2.3; R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5; R-4 / S-4.4; R-5 / S-5.1, S-5.2; R-7 / S-7.2; R-8 / S-8.4
- Files: scripts/check-realworld.sh, scripts/fixtures/discovery-gaps/
- Verify: `python3 -c "import pathlib,subprocess; rw=pathlib.Path('scripts/check-realworld.sh').read_text(); assert '構想在錯欄' in rw or 'Requested solution' in rw; assert '發現｜' in rw and '裁決｜' in rw; root=pathlib.Path('scripts/fixtures/discovery-gaps'); need=['goals-dashboard-in-wrong-column.md','goals-outcome-with-requested-dashboard.md','probe-decision-with-options.md','nod-as-only-source.md','enum-unknown.md','lookback-missing-threshold.md','ticket-solution-as-fact.md']; assert all((root/n).is_file() for n in need), need; r=subprocess.run(['bash','scripts/check-realworld.sh'],capture_output=True,text=True); assert r.returncode==0, r.stdout+r.stderr; print('T-4-ok')"`
- Blocked-by: T-1, T-2
- Intent: 日常多一步同一條指令：跑 `check-realworld.sh` 時，把「我要 dashboard」寫進 Goals、刪掉發現或裁決其中一邊前綴、高影響列只寫「使用者反映」或「使用者點頭」、狀態寫 Unknown、只寫 ACCEPTED 加日期、已宣稱回看卻缺「低於何值重開」、把 ticket 裡的解法標成 Observed，都會紅。合法結果句裡出現 dashboard 當領域詞、裁決題附三個選項、普通 Context 不貼枚舉，不會紅。改的是這支檢查的射程和 `discovery-gaps` 對照稿，不是新 CLI。不會拿它擋 G2 過期假設（那是 spec-gate），也不會做 dashboard／API 黑名單。
- Boundaries: 只准改 `check-realworld.sh` 的 `check()` 與 `MIN_CHECKS`（必須改成加完後的實數，不是寬放下限）以及 `scripts/fixtures/discovery-gaps/` 對照稿。入口字面必須仍是 `bash scripts/check-realworld.sh`，禁止新開 `check-discovery-gaps.sh`。本牙擁有教師地板與有條件填檔（錯欄／前綴／枚舉／verdict 一行／lookback 四欄）；不得當唯一填檔 G2 Gate（過期假設不放這裡）。舊 7-review 無回看節不發動。隔離複本刪一邊前綴必須紅（S-2.2）。禁止改 spec-gate 演算法（屬 T-5）與 guard Read（屬 T-6）。Actor=G1 reviewer／討論 agent；Goal=錯欄與假 Observed 當場現形；Human decision=搬構想、補來源或改 Assumption；Authority=形狀檢查擋，語意仍人抽查；Recovery=對照稿修欄後重跑同一入口。看過「構想在錯欄」≠ 已搬欄。

## T-5 延 check-spec-gate：過期假設、痛點去向與 Fast 六問從同一 Gate 擋下
- [ ] 完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3; R-6 / S-6.1, S-6.2, S-6.3, S-6.4; R-9 / S-9.1, S-9.2, S-9.3, S-9.4, S-9.5
- Files: scripts/check-spec-gate.sh, scripts/fixtures/discovery-gaps/
- Verify: `python3 -c "import pathlib,subprocess; sg=pathlib.Path('scripts/check-spec-gate.sh').read_text(); assert all(t in sg for t in ('C7','C8','C9')); root=pathlib.Path('scripts/fixtures/discovery-gaps'); expect=[('assumption-expired-open.md',1),('assumption-resolved.md',0),('fast-blank-triage.md',1),('fast-hit-no-dest.md',1),('fast-visual-all-no.md',0),('fast-wait-shown-done.md',0),('disposition-missing.md',1)]; bad=[n for n,e in expect if not (root/n).is_file() or subprocess.run(['bash','scripts/check-spec-gate.sh',str(root/n)],capture_output=True).returncode!=e]; r=subprocess.run(['bash','scripts/check-spec-gate.sh','docs/dev/requirement-discovery-gaps/4-spec.md'],capture_output=True,text=True); assert r.returncode==0 and not bad, (bad,r.returncode); w=(root/'fast-wait-shown-done.md').read_text() if (root/'fast-wait-shown-done.md').is_file() else ''; assert '等待被顯示成完成' in w; import subprocess as sp; z=sp.run(['rg','-n','RW-[0-9]','_templates/2-decision.md','_templates/4-spec.md','docs/dev/requirement-discovery-gaps/2-decision.md','docs/dev/requirement-discovery-gaps/4-spec.md','example/contract-expiry-reminder/2-decision.md','example/contract-expiry-reminder/4-spec.md'],capture_output=True,text=True); assert z.stdout.strip()==''; print('T-5-ok')"`
- Blocked-by: T-1, T-4
- Intent: 日常送 G2 前少一次假綠：同一支 `check-spec-gate.sh` 會拒絕過期還 open 的 Assumption、full lane 缺 disposition 或去向空白、Fast 六問空白、命中第 3 問卻沒寫 full／fast+mini／OC。已驗 resolved、Owner Call 接受、純視覺六問全否＋去向 Fast、以及本檔這種 full lane 沒有六問表，都不會只因新項被殺。改的是這支 Gate 加項與對照稿。不會讓腳本判斷 R/S 寫得好不好，也不會新開第二支 G2 CLI。
- Boundaries: 只准在 `check-spec-gate.sh` 與 C1–C6 同檔加 C7 Assumption refs、C8 Fast triage、C9 disposition，並把頂註「六項」改成實際項數。exit 碼維持 0／1／2。只讀 4-spec，不寫 4-spec，不判語意。Fast 項僅 `lane: fast` 發動；full 缺六問表 no-fire（S-9.5 用本檔測）。本方案處理的下落必須匹配 `R-` 或 `S-`；非處理必須落到 Out of Scope／Known limit／後續 slug。禁止新開第二支 G2 CLI。禁止改 realworld／guard（屬 T-4／T-6）。對照稿落 `scripts/fixtures/discovery-gaps/`（與 T-4 同家族、sequential 後寫）。Actor=G2 reviewer／Fast 實作者；Goal=過期假設與未分診 Fast 進不了送審；Human decision=驗轉 resolved、寫 oc-accepted、或填六問去向；Authority=spec-gate 機械拒；Recovery=改 status 或補表後重跑，不要口頭說「知道有假設」。空白表 ≠ 已分診。

## T-6 延 devtalk-guard：核准路徑可讀、方案檔仍禁、未核不得當已授權
- [ ] 完成
- Covers: R-8 / S-8.1, S-8.2, S-8.3
- Files: hooks/devtalk-guard.sh, scripts/fixtures/discovery-gaps/
- Verify: `python3 -c "import json,subprocess,pathlib; t=pathlib.Path('hooks/devtalk-guard.sh').read_text(); assert '方案檔' in t or 'Evidence manifest' in t; run=lambda p: subprocess.run(['bash','hooks/devtalk-guard.sh'],input=json.dumps({'tool_name':'Read','tool_input':{'file_path':str(pathlib.Path(p).resolve())}}),text=True,capture_output=True); r=run('docs/dev/requirement-discovery-gaps/2-decision.md'); assert r.returncode==2 and any(x in (r.stdout+r.stderr) for x in ['2-decision','4-spec','方案檔']); u=run('notes/review-requirement-discovery-gaps.md'); assert u.returncode==2; ok=run('_templates/1-discussion.md'); assert ok.returncode==0; print('T-6-ok')" && bash scripts/check-devtalk-selfclean.sh`
- Blocked-by: T-1, T-4
- Intent: 日常討論期少一次「規定了但讀不到」：owner 在 1-discussion 的 Evidence manifest 把某條路徑核准=是之後，Read 事件／行為／結果檔不再被擋；有人把 2-decision／4-spec 寫進擬路徑，即使核准格誤寫「是」也進不去；未核或空白格的路徑不能當已授權 evidence。改的是同一支 `devtalk-guard.sh` 的 Read 分支。不會新造 `check-evidence-allow.sh`，不會在沒有 talk 游標時改寫入洩漏行為，也不會做作業系統層擋硬讀。
- Boundaries: 只准改 `hooks/devtalk-guard.sh` 加 Read 分支，外加 `scripts/fixtures/discovery-gaps/` 裡與 manifest／未核／方案檔同形的對照。talk 游標在時才發動 Read；游標不在維持今日只掃 `skills/dev-talk/*` 寫入洩漏。放行條件= manifest 核准格字面「是」且路徑不是 2／3／4／5／6／7（含 html twin）。核准=是不能覆寫 2–7 禁令。未核路徑 Read 必須 exit 2；填檔不得把未核當唯一來源（與 T-4 主張牙同一判定，本 T 不改那支腳本）。禁止新開 `check-evidence-allow.sh`。既有 `check-devtalk-selfclean.sh` 必須仍綠。Known limit：人跳過 hook 硬讀方案檔，本 feat 不新造 OS hook。Actor=討論 agent／owner；Goal=核准後讀得到事實且方案檔仍禁；Human decision=owner 改核准格；Authority=guard 硬擋；Recovery=先列「想找哪類＋為什麼」等 owner 核，或維持 Assumption。核准格空白 = 禁讀。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential，不開 parallel | Feature Risk high；方法論教師與三支公開檢查契約。T-4／T-5／T-6 同寫 `scripts/fixtures/discovery-gaps/`，平行只省波次、增加語意衝突。tip 預設 sequential，須明確啟用才改。 | `_templates/5-tasks.md` `execution.mode` 缺省 sequential；4-spec Verification Profile `Risk: high` | 棄 T-1 ∥ T-2。技能與模板檔不重疊，可平行，但本 hop 選保守序：先印地板再改問法。 |
| 六張較厚 T，按教師面切 | Variant A：templates／skills／example／realworld／spec-gate／guard。每張答得出「多了什麼可觀測行為」，不是 DB→UI。Fast+verdict 不另開第七 T：地板在 T-1／T-2，牙在 T-4／T-5，避免三 T 改同一檔。 | owner Stage 5 brief「fewer thicker T ≈6–8, group by teacher surface」；4-spec Diff Budget 六塊 | 棄「一 S 一 T」（35 張過薄）；棄「先 schema 再 UI」；棄把 Fast+verdict 再拆第七 T（會跟 T-1／T-5 搶 `_templates/4-spec.md` 與 spec-gate）。 |
| 三支牙各一 T，不合併 | 可觀測行為是三個入口的開火／不開火。合併成「三牙一 T」會讓 Verify 跑三套不相干指令，違反一 T 一關注點。 | 4-spec Dependencies 三支既有牙；模板「Verify 要跑兩套不相干指令 → 拆 T」 | 棄「三牙一 T」。棄「每條 fixture 一 T」（同一函式、同一目錄）。 |
| example 五份 md 同一 T-3 | 可觀測行為是「抄範例不再學會 Goal=dashboard」。1／2／3／4／7 是同一把改口刀，不是五層架構。 | 4-spec S-1.3、S-4.4、S-5.3、S-6.4、S-7.1；Diff Budget「example 1／3／4／7」+ S-6.4 對應 2-decision | 棄「1-discussion 一 T、7-review 一 T」。 |
| S-8.4 跟 R-3 主張牙同 T-4 | 4-spec 明寫與 S-3.1 同一支主張牙，只釘 ticket 解法。拆開會讓兩 T 改 `check-realworld.sh` 同一函式。 | 4-spec S-8.4「與 A-3 同一主張牙」 | 棄「ticket 解法另 T」。 |
| S-8.3 填檔半邊 Blocked-by T-4 | Read 半邊是 guard；「未核不得當來源」半邊是 T-4 主張牙。T-6 Verify 只跑 guard exit 2，不改 realworld。 | 4-spec S-8.3 觀測「guard exit 與主張牙」 | 棄 T-6 重寫 realworld。 |
| 本 hop 不改 STATUS／HISTORY／4-spec／3-prototype | owner brief；4-spec Out of Scope。5-tasks status 留 draft，不代填 approved、不發明 G3。 | owner Stage 5 brief；N6 定案權在 owner | 棄本 hop 把 5-tasks 轉 approved。 |
