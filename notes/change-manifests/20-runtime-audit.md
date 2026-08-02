# Runtime Audit

> Runtime 輪 Phase 0(2026-08-02)。需求正本:docs/prompts/devflow-vnext-runtime.md。
> 狀態分類:DESIGN_PASS / REFERENCE_PASS / RUNTIME_PASS / E2E_PASS / PENDING / BLOCKED。
> 佐證:plugin 唯讀深掃(逐檔行號)+ coordinator 現場 git/測試實跑。
> 本檔數字為當輪(Phase 0)快照,現值以各腳本當次輸出與 Capability Matrix 為準。

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

## Capability Matrix(2026-08-02 終版;Runtime=plugin integration @ 5a4cef7 selftest 292/292;E2E=round-2 真實 /dev-flow 全鏈 @ 最終 runtime)

| Capability | Design | Reference | Runtime | E2E |
|---|---|---|---|---|
| Parallel scheduler(DAG/wave) | DESIGN_PASS | REFERENCE_PASS(contract_ref+97 檢查) | RUNTIME_PASS(P1,對拍 25/25) | E2E_PASS(r2:plan/wave-open/雙 T 整合) |
| Task-scoped guard | DESIGN_PASS | REFERENCE_PASS(契約 §7+fixtures) | RUNTIME_PASS(P1:start --task) | E2E_PASS(r2:雙武裝樹零誤攔+scope 拒他檔) |
| Candidate gate(14 項) | DESIGN_PASS | REFERENCE_PASS(run_gate+10 fixtures) | RUNTIME_PASS(P1:_gate_impl,verdict 全等) | E2E_PASS(r2:14/14 ×2) |
| Wave review | DESIGN_PASS | REFERENCE_PASS(validate_wave_review+6 fixtures) | RUNTIME_PASS(P1:登記+F2 前置) | E2E_PASS(r2:F2 拒未登記實證→登記→ACCEPTED) |
| Operational Stage 3 | DESIGN_PASS | REFERENCE_PASS(realworld 133) | RUNTIME_PASS(P2:_stage3_impl+attestation) | E2E_PASS(正向 PASS+N1 拒) |
| Attempt ledger | DESIGN_PASS | REFERENCE_PASS(schema 1.1+125 案) | RUNTIME_PASS(P3:_obs_impl+vendor 對拍) | E2E_PASS(事件即時落盤;KL-1:sequential v1 無 run_id) |
| Prompt registry | DESIGN_PASS | REFERENCE_PASS(schema+validator) | RUNTIME_PASS(P3;approved_by 待 Owner 簽) | E2E_PASS(真 hash 1.1.0 入事件) |
| Final Fresh Run(gauntlet) | DESIGN_PASS | REFERENCE_PASS(E1-E13+31 案) | RUNTIME_PASS(P4:散發+--version) | E2E_PASS(fresh 22 checks;run 事件僅 task-armed=KL-1) |
| Gate consistency(VNext G2/G3) | DESIGN_PASS(§7 正本 @748fa68) | REFERENCE_PASS(P4 fixture 10 案) | RUNTIME_PASS(live 14/14) | E2E_PASS(e2e doctor gate 行 ✓) |
| Contract version handshake | DESIGN_PASS(contract 2.0.0) | REFERENCE_PASS(hermetic 案) | RUNTIME_PASS(P3 doctor fail-closed) | E2E_PASS(e2e COMPATIBLE;fail-closed 三情境) |

> E2E 欄依 round-2(最終 runtime 5a4cef7)實跑更新;負向 N1~N4 全數正確拒絕。KL-1 = 已知限制(見最終報告)。

## Risks

1. **exec.json 單一扁平 scope + 異 slug 雙 start 拒絕,與 wave 並行正面衝突** — P1 需動 exec.json schema(唯一版本鉤子 `contract_hash_scope`)、`in_pool`、postbash baseline 三處,须自帶遷移/相容。
2. **零觀測面** — run_id/ledger 全部從零;新狀態面若落 `.devflow/` 會撞 guard 禁寫(L46-47),必須走 CLI 落盤通道(W2 契約)。
3. **gate-consistency 脆耦合且基線已紅** — token 動態抽 README §7,VNext 改 gate 措辭會先弄壞檢查本身;P4/Phase 3 須「正本與比對表同步改」;現有 1 漂移待 OC-2 條文落地一併綠。
4. **文檔漂移實例** — dev-setup SKILL 寫「33 案」實為 80;版本握手(§7)就是為堵此類漂移。
5. Plugin 無 remote — 所有備份僅本地 branch;merge 到 master = 立即生效於使用者環境,時點須謹慎(E2E 前用 integration branch checkout,可逆)。

## Safe implementation base

- Plugin Base SHA: **24057d5**
- Methodology Base SHA: **c907534**
