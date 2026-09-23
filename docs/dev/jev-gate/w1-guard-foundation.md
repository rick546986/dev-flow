---
title: jev-gate W1 — 七組守衛 foundation + P2-1 executable e2e
slug: jev-gate
status: W1 done（guard foundation；**不是 runtime、不是 production-ready、沒有任何 AUTO gate 核准**）
date: 2026-09-22
base: research/jev-supermemory 6824fa6 → claude/w0-source-closure-3aslgp
inputs: roadmap.md §3.1 P1-G1～G7、§4 P2-1、§8 數值政策、§11–§13；w0-source-closure.md 的 P0-5/P0-6/P0-9 結論
---

# W1 guard foundation

> roadmap §9 W1 完成定義:「P1-G1～G7 schema/pure/fake transport 全部負面測試通過;P2-1 executable e2e gate 完成」。
> No-Go:「任一 guard 缺失;此時禁止寫真 API runtime」。本輪兩者都做,**runtime 一行未寫**:
> `scripts/devflow_jev/` 內零 `urllib`/`http`/`socket` import,`scripts/devflow-jev.py` 不存在,
> 兩條都由 `scripts/test-devflow-jev.sh` 機械釘住(W2 P1-F1 落地時由那次 PR 明改那兩條)。

## 1. 落點

| 守衛 | 模組 | 牙 |
|---|---|---|
| G1 evidence packet + reference isolation | `scripts/devflow_jev/packet.py` | `test_guards.py::G1Packet`(19 案) |
| G2 failure/no-op、deadline、breaker、budget | `policy.py`（Budget／Breaker／evaluate／ShadowQueue） | `G2FailureNoop`（11）+ `TransportSchema`（8） |
| route formula（G2/G6 共用） | `policy.py`（route_j5／route_j1／route_j3／route_taken） | `RouteFormula`（14） |
| G3 雙閘門 | `gate.py` | `G3DualGate`（8；矩陣 fixture `optin-matrix.json`） |
| G4 雙層 ledger／replay | `ledger.py` | `G4Ledger`（16）+ `G4DurableIntegration`（2，真走 `memory/agentmem`） |
| G5 manifest 治理 | `manifest.py` + `jev-questions.json` | `G5Manifest`（10） |
| G6 防造假／derived-only | `provenance.py` | `G6Provenance`（15） |
| G7 verdict provenance tripwire | `attestation.py` | `G7Attestation`（8） |
| report（P2-2 前的最小計算器） | `report.py` | `ReportMinimal`（13） |
| W1 邊界 | — | `W1Boundary`（3）+ `test-devflow-jev.sh` ①②③ |

共 127 案(`MIN_TESTS=127` 釘死等於實際數),`bash scripts/test-devflow-jev.sh` 帶起;已註冊 `devflow-check.sh` methodology 組
`methodology/test-devflow-jev`。負面 fixtures:`scripts/fixtures/devflow-jev/`
(quoted-injection、exit-code-tail-conflict、reference-governance、mixed-072、auto-argmax-036、
score-level-mismatch、optin-matrix、wrong-head-label)。

## 2. 每組守衛對 roadmap 驗收句的對應

**G1**:超大 body → `truncated=true` 且 `route_forced=HUMAN`,header 一字不砍(`test_oversize_body_truncates_body_only_and_forces_human`);
quoted injection／exit_code 與 tail 衝突／reference governance 三組負面 fixture 各有測試;`feature+tests+docs` mixed=.72
反例固定在 `mixed-072.json`,測試斷言它仍是 `unresolved`。`self_check` 與 lint 的模組文件明寫「不構成 prompt-injection immunity」,測試 grep 這句。
privacy(secret／絕對路徑／身分證碼)命中 → 拒絕組包,不遮罩後放行;header 也掃。

**G2**:mock 400/401/422/429/529/timeout/network/malformed JSON/schema error 全部 no-op、不改 route、不 raise;
deadline 用注入時鐘(2.5s > 2s → no-op,且只送一次,無 foreground retry);session/gate breaker 三連敗 open、成功歸零;
budget:每 attempt(含 retry／variant)都 reserve 上界,unknown usage **不退款**,known 才 reconcile;attempts 與 tokens 先到者停。
shadow enqueue latency 真量 p50/p95,測試只斷言「有數字且非 0」。

**G3**:九格矩陣(`optin-matrix.json`)+ 五種壞 yaml fail-loud;`mode:off + gates.J5:live` → off;只有 key 沒 opt-in → off;
只有 opt-in 沒 key → off。owner default 寫死在 `OWNER_DEFAULT_GATES`(J1 live、J3 live、J5 shadow、J2/J4 off)。

**G4**:durable record 只含 canonical 欄位 + 結構化 `jev{}`;`json.dumps(record)` 內不出現 packet 原文、`probabilities`、raw response;
`evt_<ULID>` id;每筆 evaluation 自己的 `session_id`(= 自己的 JSONL 檔,P0-6 的 multiwriter 安全條件);
`write_durable()` 先 `signal.gate("important_discovery", …, extra_texts=[json.dumps(record)])` 再 `append_events()`。
integration test 在暫存 git repo + 隔離 `AGENTMEM_HOME` 真跑 `append_events → rebuild_local → store.events(kind="jev")`,
兩筆 evaluation 落兩檔、id 兩次 rebuild 不變。replay store 在 `.devflow/jev/replay/`(已 gitignored):stored-response
replay 兩次結果相等且 `network=False`;缺檔 `not_replayable`,`read()` 拒絕、不重建;`write()` 不覆蓋既有檔;
remote reevaluation 產新 `evaluation_id`、`parent_evaluation_id` 指回、同 `case_id`、原檔 byte 不變。

**G5**:六欄 manifest 任一欄改 → 新 `questionset_hash`;缺欄 fail-loud;Score `[level:1,…]` 放 index 0 → 紅且不排序;
group key 三欄且驗形狀。題組 J1(六題,§11)、J3(demo_worth_it)、J5(g3_route／risk 0–3／evidence_complete)。

**G6**:`verify_evaluation()` 用 `answers_summary` 重算 route;手改 route → tampered;重算 hash 後仍抓得到(hash 只做完整性);
shadow 下 `route_taken=AUTO` → invalid;J5 live 未 graduated → 仍 HUMAN;risk_paths 縮窄未核准 → `force_human`;
runtime／questions／config 路徑當次改動 → HUMAN;同 session／時間倒置／reviewer=author／evidence 版本不符／`none` 的 feedback → suspect,不進 n。

**G7**:三份模板 frontmatter 現況 → `none`;有 verdict 無 `verdict_source` → `unverified`(P1-G7 前舊 label);
`human_attested` 必須配 `attested_by: human:<name>`、`fresh_agent_reviewer` 必須配 `agent:<x>`,否則 `unverified`;
`owner_self_review` 可辨識但不進 graduation;`layered_counts` 沒有 combined 鍵。模組與測試都明寫「不是 authentication」。
**模板欄位本身沒加**(那是 P3-2 契約同步的事);W1 只提供讀取與分類。

**report**:Wilson 95% 下界(30/30 → 0.8865);n≥30 且 ≥.85 才 `floor_met`;首次 overturn `frozen`;variants／retries 同 case 只算一次;
`unverified`／`synthetic_smoke`／`owner_self_review` 不進 n;wrong-HEAD label fixture 被拒;tampered evaluation 被排除;
report note 明寫「not a proof of accuracy」。

## 3. P2-1 executable e2e(有牙)

| 面 | 改動 |
|---|---|
| 4-spec 模板 | Verification Profile 新增 `- E2E entry point:`(涉互動／對外 API 必填單一 persisted 命令;不適用寫「無 — 理由」);Lane 規則 full 欄位清單加 E2E Entry Point |
| G2 機械關卡 | `scripts/check-spec-gate.sh` C10:full lane 缺欄／空值／寫「無」無理由 → FAIL;fast lane 選配但不可留空。**legacy 不套**:frontmatter `verdict: PASS`(G2 已關)的 4-spec 不打紅 —— 七個已出貨 feature(`docs/dev/{five-station-f2,five-station-f3,five-station-simplify,requirement-discovery-gaps,integration-before-verdict,host-stack-fit,diagram-ir-gate}`)都是 full lane、都無此欄,依「絕不動 docs/dev/<slug>/ 已產出的 feature 檔」不回填;三個 five-station-f2 draft fixture 已補「無 — fixture」 |
| Gauntlet 1.4.0 | 4-spec `E2E entry point` 是命令 → `e2e` 層併入 Required(E7,旗標同樣只能加嚴);「無 — 理由」不要求。散發副本 `docs/dev/tools/` 同步;五處版本同步守衛綠 |
| fixtures／tests | Gauntlet:`scripts/fixtures/evidence-gauntlet/profile-e2e-{declared,pass,none}/`,`test-evidence-gauntlet.sh` +4 案(含散發副本)。G2 紅路:`scripts/fixtures/spec-gate-e2e/`(bad-missing／bad-bare-none／bad-empty 必紅、good-command／good-none-reason 綠、legacy-pass-no-field 不套),由 `scripts/test-spec-gate-e2e.sh` 帶起並註冊 `methodology/test-spec-gate-e2e` |
| 契約文字 | `docs/dev/readme-contract-extract.md` §7 G2 full lane 欄位清單 + G3 Evidence 契約段落補 1.4.0 e2e 規則;`notes/design/evidence-gauntlet.md` 版本與 E7 說明 |
| 流程 | `skills/dev-run/SKILL.md` Final Fresh Run 步 4 補「E2E entry point 是命令就必跑並列 e2e 層」 |
| 範例 | `example/contract-expiry-reminder/4-spec.md`(命令;其 7-review 已有 e2e pass 列)、`example/subsidy-3-0-plus/4-spec.md`(無 + 理由) |
| J5 header | `packet.HEADER_REQUIRED["J5"]` 含 `e2e_summary`,缺即拒絕組包 |

「涉互動／對外 API」的判準沒有機械化(它是語意判斷);W1 的機械規則是 **full lane 且尚未 G2 PASS 的 4-spec 必答**
(命令或無+理由),fast lane 因為 Verification Profile 只有五欄而不強制。這是刻意的收窄,不是把判準交給 Jev。

## 3.1 第一輪對抗審查後的修正(同日;36 findings → 19 存活 → 全部修)

| 守衛 | 修了什麼 |
|---|---|
| G1 | `truncated` 改由「原 body 是否超過上限」決定,不由「裁掉幾 bytes」決定;`_truncate_body` 也裁 options 描述／多餘 pros-cons;短 primary_request + 超大 quoted_context、options-only 超大兩個新負面測試 |
| G2 | `evaluate()` 的 `est_input_tokens` 改為**必填正整數**(缺／0／負 → fail-loud),不再預設 1;ok outcome 帶 `raw` 只給 replay store |
| G5 | `policy_version`／`route_formula_version`／`packet_builder_version` 綁機械指紋(`<semver>+<sha256[:12]>`,涵蓋 THRESHOLDS／deadline／caps／breaker／RISK_PATHS／packet 常數):改常數不 bump 版本,`questionset_hash` 仍會變 |
| G4 | `assert_durable_safe` 改為逐層掃禁鍵 + 每個字串葉節點 ≤200 字 + `jev{}`／`evidence`／`answers_summary`／`usage` 白名單 + 8000 bytes 上限;durable 不放整個 `probabilities` 分布;`build_durable_record` 不再與 evaluation 共用 `evidence` dict 引用;remote reevaluation 用**子代自己的 raw**(拿不到就 `not_replayable`,絕不借父代),且扣 budget／受 breaker |
| G6 | evaluation 記 `packet_consistency_flags`／`risk_ceiling_hit`／`runtime_changed`／`author_ref`／`session_ref`／`occurred_at`／`variant_id`／`parent_evaluation_id`,全部進 `INTEGRITY_FIELDS`;`route_reason`(policy)與 `route_taken_reason` 分欄;`verify_evaluation` 重算輸入預設取自記錄本身(呼叫端不能靠「不傳」讓旗標消失),並比對 `route_reason`;`answers_summary` 不四捨五入(0.8496 不會變 0.85);`feedback_suspect` 對缺 `reviewer_ref`／`session_ref`／`feedback_at` 一律 suspect(fail-closed) |
| G7／report | `graduation()` 每層各算 n／agree／overturn／Wilson／floor／frozen,**頂層 `floor_met`/`frozen` 在未指定 `primary_source` 前是 `None`**;同 case 多筆 feedback 先分組,任一 overturn 即 overturn(不看順序),並列出 `conflicting_label_cases` |
| P2-1 | C10 加 legacy 規則(見上);新增 `test-spec-gate-e2e.sh` 釘紅路;`test-architecture-guards.sh` 的 version-sync mutation 字面跟到 1.4.0 |

## 3.2 第二輪 recheck 後的修正(同日;15 findings → 全部修)

| 面 | 修了什麼 |
|---|---|
| G1 | `self_check` 的 truncation 判準改成「原 body 是否超過上限」(packet 記 `body_bytes_before`／`max_body_bytes`);裁 options 描述／primary_request 只在真的會變短時才做(不再把 body 裁大、不再多算 dropped);`builder_fingerprint` 納入 PASS_WORDS／NEUTRAL_LABEL／secret／PHI／絕對路徑**正則本文**;packet 自帶的 `packet_builder_version` 與 route 的 `policy_version`／`route_formula_version` 都改成與 manifest 相同的 `<semver>+<fp>` |
| G5／G6 | `RISK_PATHS_DEFAULT` 只剩 policy.py 一份,`risk_ceiling_hit` 呼叫時才讀(provenance 不再有可被單獨改掉的複本) |
| G4 | `MAX_DURABLE_TEXT` 400→600、reason 欄限 80 字:有旗標／低於門檻的 shadow 評估不再因 body 超長而寫不進 durable(第一輪修法引入的回歸);`assert_durable_safe` 也掃**鍵名**(長度 ≤64、qid 必須是識別字、privacy 掃描含鍵);`packet_consistency_flags`／`usage` 改複本;`reevaluate` 先設 lineage／`replay_status` 再蓋 integrity hash、再寫檔 |
| G6 | `verify_evaluation` 的三個布林只能加嚴(記錄為 True 的,呼叫端傳 False 不放鬆);`feedback_suspect` 對 evaluation 缺 `session_ref`／`occurred_at` 也 suspect |
| report | 每筆用**它自己記錄的 mode** 重算(live 的 REQUEST_CHANGES 不再被 shadow 級 level 誤判為不一致) |
| P2-1 C10 | 「無」的同義形(無／沒有／不適用／none／n-a／n/a／na／not applicable)後接任何標點都算「只寫了無」;括號起頭的模板佈局字 = 沒填;legacy 條件改成 `verdict: PASS` **且** `status` 非 draft;fixtures +5(punct／synonym／english／placeholder／draft-with-PASS),`test-spec-gate-e2e.sh` 11 案 |

## 3.3 第三輪 recheck 後的修正(2026-09-23;15 findings 全 minor/major-wording → 全部修)

| 面 | 修了什麼 |
|---|---|
| G1 | 裁剪改以 **bytes** 判「會不會變短」(suffix 的 … 是 3 bytes;213–216 字邊界逐一測);`self_check` 對缺 size 欄位的舊 packet 回 False 而不是 KeyError;`builder_fingerprint` 連正則 **flags** 一起 hash(拿掉 `re.I` 也換 hash) |
| G4／G5 | qid 規則兩邊同一條:`^[a-z_][a-z0-9_]{0,63}$`(manifest 收的,durable 一定寫得進) |
| C10 | 同義形加字尾邊界(`nats` 不是 `na`)並補 n.a.／暫無／不需要;理由 = 去掉所有標點／符號後 ≥4 個字母或數字(`無!!!!`、`無，，，，` 都不是理由);沒填 = 含模板佈局字、佔位詞(command／cmd／todo／tbd／待補／待定／略／命令)或整個值沒有字母數字;**拿掉「括號起頭 = 沒填」**(子 shell／test-bracket 命令是合法值);legacy 改成明列 `status ∈ {approved, shipped, superseded}`(in-review／draft 打 PASS 不算);fixtures +9,`test-spec-gate-e2e.sh` 20 案 |
| 文件 | §4 的 risk_paths 位置改為 `policy.RISK_PATHS_DEFAULT` |

## 4. 仍是候選值、待 owner 核定(未冒充裁決)

| 值 | 位置 | 出處 |
|---|---|---|
| J1 foreground deadline 2s、無 retry | `policy.J1_DEADLINE_S` | roadmap §8.2 |
| daily 500 attempts／500k input tokens | `policy.DAILY_*_CAP` | roadmap §8.2 |
| J5 AUTO 門檻 p≥0.85、evidence_complete≥0.90、risk≤1 | `policy.THRESHOLDS["J5"]` | 0-draft §4「門檻設在 noul/score 值」;數字是 W1 工程候選 |
| J1 clarity≥0.70、START≥0.80、owner_call≥0.50、ambiguity≤1 | `policy.THRESHOLDS["J1"]` | 同上 |
| J3 demo_worth_it≥0.60 | `policy.THRESHOLDS["J3"]` | 同上 |
| breaker 三連敗 open | `policy.BREAKER_THRESHOLD` | 工程候選 |
| durable gate 借 `important_discovery` 當 `signal.gate` 的 kind | `ledger.write_durable` | P0-6 結論 5 的選項 (a);選項 (b) 加 `jev` 進 `HIGH_SIGNAL_KINDS` 是 memory 模組 L2 |
| C10 legacy 判準 = frontmatter `verdict: PASS` 且 `status ∈ {approved, shipped, superseded}` | `check-spec-gate.sh` C10 | 工程候選;若 owner 要回填七份已出貨 4-spec 另議 |
| risk_paths 預設清單 | `policy.RISK_PATHS_DEFAULT`(唯一一份,進 policy 指紋) | P2-4 正式化前的候選 |

任何一個改動都會改 `POLICY_VERSION`／`ROUTE_FORMULA_VERSION` → 新 `questionset_hash` → 新 calibration group(G5)。

## 5. 明確沒做（W2 以後）

- 沒寫 `scripts/devflow-jev.py`、沒有任何 HTTP;沒碰 `TYPESAFE_API_KEY`。
- 沒建任何專案的 `.dev-flow/jev.yaml`(預設不 opt-in)。
- 沒改 G1/G2/G3 模板的 frontmatter(G7 欄位是 P3-2)。
- 沒改 `hooks/`、`memory/agentmem`、`skills/dev-flow`、`skills/dev-talk`。
- 沒把 W0 的 21 次外部 smoke／audit 歸檔或算進任何 n。
- 沒把 ship-manifest 加列(P1-F1 才散發 runtime;P0-8 結論的 manifest 版本欄留 W2)。
- `devflow-check.sh all` 的 render／gate-twin／methodology-corrections 三處紅是本容器缺 markdown-it-py（Python 3.11）的既有環境因素,與本輪無關;其餘組綠。
