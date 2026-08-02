# Runtime Audit

> Runtime 輪 Phase 0(2026-08-02)。需求正本:docs/prompts/devflow-vnext-runtime.md。
> 狀態分類:DESIGN_PASS / REFERENCE_PASS / RUNTIME_PASS / E2E_PASS / PENDING / BLOCKED。
> 佐證:plugin 唯讀深掃(逐檔行號)+ coordinator 現場 git/測試實跑。

## Methodology Repository

- Path: 本 repo(方法論正本 + 參考契約)
- HEAD: c907534(= 四軌 merge fc2bf34 + Phase 0-C 正本化 commit)
- Branch: main
- Dirty files: `?? docs/superpowers/`(使用者既有 plan 檔,不屬本輪管轄,保留 untracked)
- Backup branch: `backup/devflow-vnext-before-runtime-20260802-083654`;snapshot:`devflow-vnext/methodology-snapshot`(皆 @ fc2bf34)
- Existing VNext status: 四軌方法論/模板/參考契約/fixtures/observability 工具/evidence gauntlet 已合併;**未 push**;測試基線 82/82(含新 .serena 防護 2 條)+ renderer 4/4 + parallel 95/95 + realworld 133/133 + observability 94 + gauntlet 30/30 + vnext scenario 14/14

## Plugin Repository

- Path: `~/.claude/plugins/local/dev-flow/`(獨立 git repo、**無 remote**)
- HEAD: 24057d5
- Branch: master(樹淨)
- Dirty files: 無
- Unmerged branches: **無**(codex/dev-flow-methodology-corrections 已合併,詳 plugin-unmerged-branch-audit.md)
- Existing tests: `hooks/selftest.sh` **80/80 綠**(未武裝 3/start 前置 28/雙 start 2/PreToolUse 14/prebash 3/allow 3/postbash 14/fail-closed 3/gate reviewer-selection 8/stop 2);`hooks/gate-consistency.sh` 14 格,**基線紅 1/14**:`✗ _templates/4-spec.md 頂註缺 token「R/S、全審、全裁決」`(成因 = 四軌輪 B1 修正把 G2 句改為「條件正本見 README §7」不再覆誦;Phase 3 隨 OC-2 新條文一併解)
- Runtime entry points: skill dev-flow(路由,stage 6 自動載 dev-run)/ skill dev-run(Stage 6 派工迴圈:haiku→sonnet→opus 升階、同 T ≤4 次、fresh reviewer 收驗、派工者 commit)/ skill dev-setup(散發 README+_templates 進專案 docs/dev/)/ `hooks/devflow-exec.sh start|stop|status|allow` → `_exec_impl.py` / hooks.json 4 掛載(guard/prebash/devtalk/postbash)
- Generated files: plugin repo 內**無** installer 產生檔(全手維護);runtime 生成物為專案側 `.devflow/exec.json` + `<git-dir>/devflow-armed`(CLI 專有,agent 被 guard 禁寫);dev-setup 散發的 `docs/dev/README.md` + `_templates/` 屬「母版所有、upgrade 覆蓋」準生成物
- Existing partial implementation: **無 VNext 雛形**(grep `execution.mode|integrate-after|review-mode|task_tags|run_id|gauntlet|attempt|ledger|candidate|wave|profile|parallel` 於 *.py/*.sh/*.json/*.md 零命中,sanity 對照通過)
- Parser 現況:`_exec_impl.py` 只認 `## T-\d+` 與 `Covers|Files|Verify|Blocked-by` 四必填欄;未知 `- X:` 行靜默忽略 → **新選配欄位 additive-safe**
- exec.json 現 schema:`{slug, started, scope[], extra[], baseline{}, contract_hashes{}, contract_hash_scope:"repo-wide-v1"}`;sentinel per-worktree;雙 start 拒絕(異 slug)

## Capability Matrix(2026-08-02 §11-d 更新;Runtime 證據 = plugin integration branch @ 150be0f,selftest 258/258)

| Capability | Design | Reference | Runtime | E2E |
|---|---|---|---|---|
| Parallel scheduler(DAG/wave) | DESIGN_PASS | REFERENCE_PASS(contract_ref+95 檢查) | RUNTIME_PASS(P1:devflow-lib+_exec_impl,對拍 25/25) | PENDING |
| Task-scoped guard | DESIGN_PASS | REFERENCE_PASS(契約 §7;fixtures) | RUNTIME_PASS(P1:start --task+guard 恆許變更,selftest p1) | PENDING |
| Candidate gate(14 項) | DESIGN_PASS | REFERENCE_PASS(run_gate+10 fixtures) | RUNTIME_PASS(P1:_gate_impl.py,gate fixtures verdict 全等) | PENDING |
| Wave review | DESIGN_PASS | REFERENCE_PASS(validate_wave_review+5 fixtures) | RUNTIME_PASS(P1:狀態機+wave review 驗證) | PENDING |
| Operational Stage 3(trigger/Demo/verdict) | DESIGN_PASS | REFERENCE_PASS(realworld 133 檢查) | RUNTIME_PASS(P2:_stage3_impl.py,OC-2B 五分支+attestation) | PENDING |
| Attempt ledger | DESIGN_PASS | REFERENCE_PASS(schema 1.1+devflow_obs+125 案) | RUNTIME_PASS(P3:_obs_impl.py+vendor,對拍 byte-identical) | PENDING |
| Prompt registry | DESIGN_PASS | REFERENCE_PASS(schema+validator) | RUNTIME_PASS(P3:prompt-registry.json,approved_by 待 Owner 簽) | PENDING |
| Final Fresh Run(gauntlet) | DESIGN_PASS | REFERENCE_PASS(E1-E13+30 案) | RUNTIME_PASS(P4:dev-setup 散發+rehearsal;dev-run Stage 7 條文) | PENDING |
| Gate consistency(VNext G2/G3) | DESIGN_PASS(OC-1/2 條文入 §7 正本 @748fa68) | REFERENCE_PASS(P4 fixture tests 10 案) | RUNTIME_PASS(對 integration 版 14/14 全綠;live master 未部署前 2/14 紅 = 安裝面滯後) | PENDING |
| Contract version handshake | DESIGN_PASS(devflow-contract.json 2.0.0) | REFERENCE_PASS(hermetic 契約案) | RUNTIME_PASS(P3:doctor fail-closed;六 capability 聲明) | PENDING |

> E2E 欄待 Phase 4 真實 /dev-flow 端到端(正向+4 負向)後更新;依 doc1 §2,在此之前不得宣稱 E2E_PASS。

## Risks

1. **exec.json 單一扁平 scope + 異 slug 雙 start 拒絕,與 wave 並行正面衝突** — P1 需動 exec.json schema(唯一版本鉤子 `contract_hash_scope`)、`in_pool`、postbash baseline 三處,须自帶遷移/相容。
2. **零觀測面** — run_id/ledger 全部從零;新狀態面若落 `.devflow/` 會撞 guard 禁寫(L46-47),必須走 CLI 落盤通道(W2 契約)。
3. **gate-consistency 脆耦合且基線已紅** — token 動態抽 README §7,VNext 改 gate 措辭會先弄壞檢查本身;P4/Phase 3 須「正本與比對表同步改」;現有 1 漂移待 OC-2 條文落地一併綠。
4. **文檔漂移實例** — dev-setup SKILL 寫「33 案」實為 80;版本握手(§7)就是為堵此類漂移。
5. Plugin 無 remote — 所有備份僅本地 branch;merge 到 master = 立即生效於使用者環境,時點須謹慎(E2E 前用 integration branch checkout,可逆)。

## Safe implementation base

- Plugin Base SHA: **24057d5**
- Methodology Base SHA: **c907534**
