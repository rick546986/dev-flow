# Plugin Workstream Result

- Workstream: P2 Operational Runtime
- Base SHA: 24057d5
- Branch: devflow-runtime-vnext/operational
- HEAD: 69453cb(功能面;本 manifest commit 為其後一筆)
- Modified files:
  - `hooks/_stage3_impl.py`(新;P2 獨佔)
  - `hooks/selftest.sh`(只增:p2_ 前綴 helpers + 18 案,插於既有案之後、cleanup 之前)
  - `skills/dev-flow/SKILL.md`(P2 獨佔:Stage 1/3/4 列 + 新 §4 + 鐵則④)
  - `manifests/p2-operational.md`(本檔)
- Tests before: selftest 80/80;gate-consistency 13/14(基線紅 1 = 母版 `_templates/4-spec.md` 頂註缺 token,20-runtime-audit 已載明,Phase 3 隨 OC-2 解)
- Tests after: selftest **98/98**(+18 p2_ 案,先 RED 80/98 後 GREEN);gate-consistency 仍 13/14(SKILL.md 4 格全綠,無新紅)
- External dependencies: python3(與既有 selftest 同;由 `hooks/devflow-python-lib.sh` 解析:`DEVFLOW_PYTHON` → `/usr/bin/python3` → PATH,缺直譯器 fail-open);條件正本 = 母版 README §7 + `notes/design/vnext-shared-contract.md` §2
- Status: DONE(P2 範圍);跨檔條文待 Integrator(見下)

## Added capabilities(逐項)

| Capability | 落點(檔:行/節) | 狀態 |
|---|---|---|
| Stage 3 trigger 判斷(記錄解析 + 判定矩陣) | `hooks/_stage3_impl.py`(判定矩陣見檔頭 docstring);SKILL §4 | RUNTIME_PASS(selftest p2 18 案 + 對拍 example 實跑) |
| Human verdict 讀取(佔位/尾註容忍、取最後值) | `_stage3_impl.py` `parse_verdict` | RUNTIME_PASS |
| **Agent 自填 ACCEPTED 拒絕機制** | `_stage3_impl.py` attestation 檢查 + `test-only human fixture` 標記;SKILL §4 | RUNTIME_PASS |
| G2 Demo verdict 條件(OC-2B 全五分支) | `_stage3_impl.py`(exit 0 過/2 拒/1 錯;stdout JSON `stage3-verdict-v1`);SKILL 階段表 G2 格指向正本 | RUNTIME_PASS(機械);SKILL 格 gate-consistency 綠 |
| legacy Feature 相容(不誤殺) | `_stage3_impl.py`:1-discussion 無 RWC 節→legacy 放行;無 1/3 檔→fast-lane N/A;皆明確標示 | RUNTIME_PASS |
| /dev-flow Stage 1 提醒收集 Real-world Context | SKILL §2 表 stage 1 列 | DESIGN_PASS(prompt 層;E2E PENDING) |
| Stage 3 Demo 必要性 | SKILL §4「Demo 必要性」 | DESIGN_PASS(prompt 層) |
| 多 Variant 是否真的需要(六修正 6.2 分離規則) | SKILL §4「Demo 與 Variant 分離」:互動風險→Demo 必要;方案未定→2-4 結構 Variant;已核准 Pattern→1 Demo;禁湊數假 Variant | DESIGN_PASS(prompt 層) |
| 禁完整訪談逐字稿入派工 context | SKILL §3 鐵則 資訊圍欄④ | DESIGN_PASS |
| Task Context Packet 最小 OC 子集 | 條文見下「交 Integrator」1(dev-run SKILL = P1 檔) | PENDING(Integrator) |
| Stage 7 Operational Walkthrough 派工 | 條文見下「交 Integrator」2(dev-run SKILL = P1 檔) | PENDING(Integrator) |

## Attestation 機制(P2 設計定案)

- **形式**:`Human verdict: ACCEPTED` 必須伴隨同節 attestation 行
  `- Verdict attestation: human:<姓名> @ <YYYY-MM-DD>`,由人類親自輸入;
  SKILL 明令 Agent 禁寫/禁改/禁代填該行。缺行或格式不符 → `_stage3_impl.py` exit 2
  拒收(訊息明示「Agent 不得自行填入 ACCEPTED」)。REVISE/NOT_REVIEWED 無需 attestation
  (本就是拒收值,agent 自填屬保守方向)。
- **test fixture 防線**:committed 範例/測試 fixture 必須含 `test-only human fixture`
  字樣;`_stage3_impl.py` 正式模式對含該字樣的 3-prototype 一律拒收,僅 selftest 帶
  `--accept-test-fixture` 可收 → fixture 永遠不可能誤過正式判定。
- **誠實邊界**:tripwire 非密碼學證明 —— 擋的是「agent 照模板順手填 ACCEPTED」的預設
  失敗模式(模板不含 attestation 行);蓄意偽造由 G2 人審 + author≠approver 把關。

## 交 Integrator(跨所有權條文;P2 不改 P1 檔)

1. **dev-run SKILL.md(P1 檔)增補 — Task Context Packet 最小 Operational Context 子集**:
   > 派工 prompt 的 Task Context Packet 只帶該 T 相關之 4-spec Operational Context
   > 最小子集:Actor / Goal / Human decision / Authority / External dependency /
   > Out-of-system action / Waiting-timeout 與 Recovery / 不得誤導使用者事項。
   > 禁引 1-discussion 原文或訪談逐字稿;T 未涉人機互動 → 不帶 Operational Context。
   (語意正本:方法論 `notes/design/real-world-interaction.md` §6。)
2. **dev-run SKILL.md(P1 檔)增補 — Stage 7 Operational Walkthrough 派工**:
   > G3 前對涉互動 feature 派 fresh-context reviewer 做 Operational Walkthrough:
   > 自建表(S-id|角色|真實目標|系統操作|系統外步驟|等待/例外|結果)實走一遍;
   > 六查:技術過但人做不完 / 看得到沒決策權 / 等待誤標完成 / 系統外不可追蹤 /
   > 中斷無法恢復 / 資訊過期缺漏並發;結果記 7-review。
3. **devflow-exec.sh(P1 檔)選配 wiring**(非必要,_stage3_impl.py 可直呼):
   子命令分派處加一行 `stage3) shift; exec "$DEVFLOW_PY" "$H/_stage3_impl.py" "$@" ;;`
   (直譯器經 `hooks/devflow-python-lib.sh` 解析,不寫死路徑)。
4. **方法論模板 follow-up(Owner 裁決;方法論 repo 非 P2 所有權)**:
   `_templates/3-prototype.md` User Demo Feedback 增 `- Verdict attestation:` 欄
   (人類親填註記);`example/contract-expiry-reminder/3-prototype.md` 的示範 ACCEPTED
   加 `test-only human fixture` 標記。現況 runtime 對該 example 判 REJECT
   (ACCEPTED 缺 attestation)—— 屬預期正確行為,因其 verdict 為示範值。
5. **README §7 G2 粗體錨**「Verification Profile」「Demo verdict」屬 Phase 3(OC-2 正本化,
   P4/Integrator);SKILL G2 格已含「Demo verdict」字樣,token 落正本後 containment 即綠。

## Raw outputs(摘錄)

- RED:`❌ 守衛自測 80/98,失敗 18 項`(全部為 p2_ 新案,`_stage3_impl.py` 尚不存在)
- GREEN:`✅ 守衛自測 98/98 全過`
- gate-consistency(DEVFLOW_PLUGIN=本 worktree):`❌ 發現 1/14 處漂移` —
  `✗ _templates/4-spec.md 頂註:缺 token「R/S、全審、全裁決」`(基線紅,非本軌造成);
  SKILL.md 4 格(G1/G2/G3 階段表 + reviewer-selection)全 ✓
- 對拍實跑(方法論 example contract-expiry-reminder):trigger_hits 8 條全解析、
  verdict=ACCEPTED、`g2_demo: REJECT`(缺 attestation)、exit 2 —— 與「示範值不得當
  真人裁決」語意一致

## Known limitations

- attestation 為 tripwire(見上);trigger 九條命中與否的語意判斷仍由人/agent 落檔,
  verifier 驗記錄不驗語意。
- VNext 檔(1-discussion 有 RWC)若無 3-prototype 判定節且無 Owner Call → 一律拒
  (fail-closed);N/A 必須落檔(全未勾清單或 Owner Call),口頭不算。
- RED 狀態未單獨成 commit(「全程綠」與「逐 commit」並存的取捨);RED 證據見上。
- `--accept-test-fixture` 僅 selftest 使用,SKILL 不對使用者宣傳該 flag。
