---
title: jev-gate W4 — J5 shadow enqueue / evidence-bound pairing / Ship 出口稽核
slug: jev-gate
status: W4 完成（J5 shadow：enqueue→drain→label；無 AUTO、不寫 G3 verdict、不進 main）
date: 2026-09-23
base: research/jev-supermemory d4fc198（W3）→ 本分支 claude/jev-w4-j5-shadow-3aslgp
---

# W4 J5 shadow + evidence-bound pairing

> roadmap §1 W4 = P1-F4、P1-F7 + label binding／dedupe。A1–A7／B1–B5 已鎖（`owner-decisions-pending.md` §0），本波
> **沒改任何門檻**，`questionset_hash` 未變。硬約束：`GRADUATED = False` 仍是唯一一處賦值；雙閘門不鬆；J5 只讀已產生的
> evidence、不產 evidence、不寫 `7-review.md` 任何一個 byte；沒有第二個 HTTP client（`drain` 走本檔既有 `run_ask` →
> `devflow_jev.http_transport`）；不進 main。**作者 ≠ 審查者**：本文件不宣稱任何人 PASS；審核交給另一個 agent／owner。

## 0. 分支與 SHA

| 項 | 值 |
|---|---|
| 基線 | `research/jev-supermemory` `d4fc1983d296079dfa624593d3a2c75cf447fdef`（W3） |
| W4 分支 | `claude/jev-w4-j5-shadow-3aslgp`（commit SHA 見 PR） |
| main | **未動** |

## 1. P1-F4 J5 shadow enqueue（前景不等 HTTP）

**做了什麼**（全部在 `scripts/devflow-jev.py`，散發副本 `docs/dev/tools/devflow-jev.py` 同步）

| 子命令 | 何時 | 做什麼 | 網路 | 寫入 |
|---|---|---|---|---|
| `enqueue --slug S` | S2d-fresh：Gauntlet `--report` 落檔後、進 S2e 前 | 雙閘門 → `bind_evidence` → 組 J5 packet → 序列化到 `.devflow/jev/queue/q_<ULID>.json`；量測 latency | **無** | 只有 queue（gitignored） |
| `drain [--max N]` | N5-verdict 的 Human verdict 落檔**之後**（或任何更晚時間） | 逐筆再查雙閘門 → `run_ask("J5", …)` shadow → replay + durable；失敗只記 shadow failure；item 移到 `queue/done/` | shadow 一次／筆 | replay、state、durable、queue/done |
| `label --slug S --from-review` | verdict 落檔後 | 用**現在**的 evidence 版本重算 `case_id`，只配得上同版本的 evaluation；從 `7-review.md` frontmatter 推 agree／overturn 與 source | 無 | durable feedback record |
| `enqueue-bench` | 隨時 | 實測 enqueue p50／p95（序列化、序列化+寫檔） | 無 | 暫存目錄 |

- **G3 立刻照走**：`enqueue` 永遠 exit 0，回 `effect=continue_existing_flow`、`g3_blocked=false`、`writes_g3_verdict=false`；off／evidence 未固定／組包失敗 → `noop`，什麼都不寫。S2d 節點寫明「不看它的輸出決定任何事」。
- **順序不可反**：`drain`／`label` 只在 Human verdict 落檔之後跑（N5 節點寫明理由：否則 Jev 的 route 會在判定前被看到）。packet 裡**不含** `7-review.md` 的 `verdict:`（測試釘：frontmatter 已寫 REQUEST_CHANGES 時 packet 全文找不到這個字）。
- **worker 失敗 = shadow failure**：transport 逾時／錯誤／breaker／budget → evaluation `status=noop`、`route_taken=HUMAN`、`replay_status=not_replayable`，仍落 durable 留痕；`7-review.md` 的 sha256 前後相同（測試釘）。drain 時雙閘門已關 → `skipped_gate_off`，零網路。
- **不是 AUTO**：`route_recommended` 照 A3 算（p≥.85、evidence_complete≥.90、risk≤1），`route_taken` 經 `policy.route_taken(..., graduated=GRADUATED)` 在 shadow 恆 `HUMAN/shadow_mode`；`drain` 另有 tripwire：任何 result 出現 `route_taken=AUTO` 立刻 raise 拒寫（測試用 monkeypatch 偽造 `run_ask` 驗證會咬）。
- **evidence 綁定（`bind_evidence`）**：`artifact_hash` = `git ls-tree -r HEAD` 全表的 sha256（出貨樹 = 審過的樹）；`evidence_hash` = `7-review.md`＋`6-implementation-notes.md`（若在）＋gauntlet report 逐檔 sha256 清單的 sha256；`head_sha` = HEAD。缺 `7-review.md` 或缺 gauntlet report（預設 `docs/dev/<slug>/evidence/gauntlet-report.md`，可 `--gauntlet-report`）= evidence 未固定 → noop。J5 header 的 `gauntlet_verdict`／`required_layers_status`／`final_fresh_run_id` 來自 report 的 `- verdict:`／`- checks:`／`- violations:`／`- run-id:`，`e2e_summary` 來自 4-spec 的 `- E2E entry point:`。`run_id` 只作 provenance（P0-5）。
- **enqueue 成本實測**（本容器，n=200，payload 20 KB；`enqueue-bench`）：

| 量測 | p50 | p95 | max |
|---|---|---|---|
| 只序列化（`policy.measure_enqueue_latency`） | 0.060 ms | 0.083 ms | 0.130 ms |
| 序列化 + 寫檔 + `os.replace` | 0.175 ms | 0.226 ms | 0.269 ms |

  這是本機數字，不是 SLA，也**不是「0ms」**。每次 `enqueue` 的實際 `enqueue_latency_s` 都印在輸出。

**證據路徑**：`scripts/devflow-jev.py`（`bind_evidence`／`build_j5_packet`／`run_enqueue`／`run_drain`／`run_label`／`run_enqueue_bench`）、`skills/dev-flow/stage7/nodes/{S2d-fresh,N5-verdict}.md`、`scripts/devflow_jev/test_runtime.py::W4Shadow`（15 案）。

## 2. Same-evidence label binding + unique-case dedupe

- **綁定鍵**：`case_id = sha256(feature, gate, artifact_hash, evidence_hash, head_sha)`（W1 `ledger.case_id`，未改）。evaluation 與 feedback 都帶同一組 `artifact_hash／evidence_hash／head_sha`；`provenance.feedback_suspect` 對三個 hash 逐一比對，不一致 → `evidence_version_mismatch` → 不進 n（W1 既有）。
- **wrong HEAD／evidence 變了 → 拒**：`label` 先用當下 repo 重算 binding；找不到同 `case_id` 的 ok evaluation → `status=refused, reason=no_evaluation_for_this_evidence_version`，**不寫任何 feedback**（測試：改 `7-review.md` 一行 → 拒；還原內容但多一個 code commit → HEAD 變 → 拒）。
- **dedupe**：同 evidence 的 `enqueue --variant-id v0/v1`、`drain` 兩筆、再 `reevaluate` 一筆 → 三筆 evaluation 同一 `case_id`；`label` 落在最新一筆，其餘列 `duplicates_same_case`；`report.graduation` 把同 case 的多筆記 `duplicate_case` → **n=1**（測試釘）。
- **label 來源**（`--from-review`）：讀 `7-review.md` frontmatter 經 `attestation.classify`：`none`／`unverified`（沒有 `verdict_source`／`attested_by`，也就是 P3-2 之前的模板）→ **refused，不落盤**；`owner_self_review` → 記錄但 `counts_toward_n=false`。verdict 映射：AUTO×PASS→agree、AUTO×REQUEST_CHANGES／HOLD→overturn、REQUEST_CHANGES×REQUEST_CHANGES→agree、REQUEST_CHANGES×PASS→overturn；`route_recommended=HUMAN` 不是預測 → `not_labelable`，不進 n（§5.1 第 7 條：mechanical／human route 與 shadow route 分開）。明示 `--verdict --source` 仍可用（測試用）。
- **durable 只放 ID／hash／結構化指標**：沿用 W2 `build_durable_record`／`build_feedback_record`，title `[jev]` 前綴（B2）；raw packet／questions／response 只在 gitignored `.devflow/jev/replay/`；queue 也在 `.devflow/`（gitignored）。
- **21 次外部稽核不進 n**：W0（2026-09-22）的合成／文件稽核只存在 `evidence/w0/` 文件，從未進 replay store 或 durable；`report` 只讀 replay store 的 evaluation 與 durable 的 feedback record，**由構造排除**。本波的 n=1 來自隔離 git repo 的合成 Ship case（`W4Shadow.test_synthetic_ship_case_pairs_to_n_equals_one`），也只是驗配對機制，不是 graduation 樣本；真樣本要真 Ship 路徑（§5.1 第 1 條）。

## 3. P1-F7 Ship 出口 auto|human 歸屬稽核

方法：對 commit／push／PR／merge／tag 逐步找「真的會 exit 2 擋下」的機械守衛（`hooks/*.py`、`hooks.json`），找不到就明列缺口；散文與 checklist 只算 discipline，不算 guard。行號以本分支 HEAD 為準。

| 步 | 歸屬 | 真正的機械守衛（file:line） | 缺口／備注 |
|---|---|---|---|
| **code commit（Stage 6/7）** | human／agent 皆可 | **沒有**任何 hook 攔 `git commit`。相關但非等價：寫入 scope 守衛 `hooks/_guard_impl.py:143-149`（Edit/Write 走 `devflow-lib.write_scope_verdict:390`）、`hooks/_prebash_impl.py:680`（Bash 寫入 prevent-before，`deny_write_command:440`）、`hooks/_postbash_impl.py:98-155`（Bash 後掃 dirty paths，scope 外 exit 2）、契約防篡改 `_postbash_impl.py:80-91`、守衛狀態檔 `_prebash_impl.py:634-646` | 這些擋的是**寫哪些檔**，不是 commit 本身。「Verdict 之後禁止再改程式碼、任何 code commit 作廢 G3」只在 `_templates/7-review.md:176` 散文與 Exit Checklist `:334`；沒有 hook 比對 verdict 時間與 HEAD |
| **Stage 7 review 期間讀 6-notes／上游** | 機械 | `_guard_impl.py:124-135`（圍欄③ Read、圍欄② upstream）、`_prebash_impl.py:649`（shell 讀上游）、`:668`（shell 讀 6-notes）；`_exec_impl.py:990` 寫 `phase=review` | 防錨定，與出口無關，列出只為對照「有牙的長什麼樣」 |
| **push feature branch** | human／agent（散文） | **沒有** hook。`skills/dev-flow/SKILL.md:79`「feature branch → develop；禁直上 master」是散文；`guides/guide-dev-flow.html:1574` 只是範例指令 | 缺口：agent 可 push 任何分支，repo 內無守衛 |
| **PR → develop** | human 開／merge（散文） | **沒有** hook。`_templates/7-review.md:334` Exit Checklist 條目；`SKILL.md:79` | 缺口：沒有東西檢查 PR base 不是 master |
| **merge（不可逆改動）** | human | **沒有** hook。Quiz gate 是人工步驤：`guides/guide-dev-flow.html:2756-2758`「非 hook —— Stage 7 G3 merge 前的人工步驟」；`SKILL.md:77`；`_templates/7-review.md:329` | 明文非 hook。合併後回滾規則 `guide:2038`（`git revert -m 1`）也是散文 |
| **push main（方法論 repo 發版）** | **human only** | 不是 repo 內守衛，是使用者本機 `~/.claude/settings.json` `permissions.deny: Bash(*git push*main*)`（`skills/dev-release/SKILL.md:149-160`，鐵律 9） | 缺口：採用專案沒有這條 deny 就沒有牙；deny 只認字面 `git push … main`（本檔不擴黑名單） |
| **tag + release** | agent 可跑（散文核准後） | **沒有** hook。`skills/dev-release/SKILL.md:162-181`（`git tag -a`／`git push origin vX`／`gh release create`）；tag 名不含 main 所以連本機 deny 也不擋 | 缺口 |
| **派工分層（順帶）** | 機械但 **fail-open** | `hooks/_dispatch_impl.py:133-162`：只在「exec-v2/v3/v4 武裝中 + 顯式指名 opus/fable + 本 run 無低階 attempt + 無豁免卡」這一窄口徑 deny；未武裝／缺 model／schema 不認得一律放行（檔頭明文） | **不是權限守衛**：它防手滑與紀律漂移，不防蓄意偽造（檔頭信任模型 X-5b）；不能拿來補上面任何一格的空白 |

**結論**：Ship 出口五步（commit／push／PR／merge／tag）在 repo 內**全部沒有 hard guard**，目前的保障是 Exit Checklist、SKILL 散文、Quiz gate 人工步驟，以及只在方法論 repo 使用者本機生效的 `permissions.deny`。這與 roadmap §15 第 5 點的擔心一致；J5 AUTO（P3-1）若要落地，這些缺口是**先決條件**，不是 J5 的事。本波只稽核不補牙（補牙是 L2 契約變更）。

## 4. 驗證

| 套件 | 結果 |
|---|---|
| `scripts/test-devflow-jev.sh` | ①②⑤③④ 全過；unittest **209/209**（guards 132、runtime 68、http_transport 9；地板 194→**209**） |
| `scripts/check-devstage7-graph.sh` | 10 真節點，failures=0（S2d-fresh／N5-verdict 各加一段，`--write-cursor` 與寫入限制未動） |
| `scripts/check-ship-manifest.sh` | 26/26（`devflow-jev.py` 已回拷 `docs/dev/tools/`；列數與 `version` 未變 `v1-50dce597421a238b`） |
| `scripts/check-file-map.sh` | forward 231 + reverse 233（沒有新增必列檔） |
| `scripts/test-architecture-guards.sh` | 146/146（釘值未變：heredoc 229、selftest 469、ship-manifest 26、file-map 231） |
| `check-py-floor`／`check-no-stale-paths`／`check-version-sync`／`check-dev-setup-discipline` | 綠 |
| 真 TypeSafe API | **沒有打**。沒有 key；HTTP 路徑仍是 FakeTransport 與 tripwire ⑤ loopback 閉埠 |
| `hooks/selftest.sh` 全檔 | 沒有整檔重跑；本波沒改 hooks/ |

驗收對照（PR body checklist 同步）：雙閘門 off → enqueue 零網路不擋 G3 ✅（`test_off_enqueue_is_noop_zero_network_nothing_written`）；假 transport 慢／失敗 → G3 不變只見 shadow failure ✅（`test_drain_transport_failure_is_only_a_shadow_failure`）；wrong HEAD／換 evidence_hash → pairing 拒 ✅（`test_label_refuses_when_head_or_evidence_moved`）；variants／retry → 同 case_id、n=1 ✅（`test_variants_retry_reevaluate_share_case_and_n_stays_one`）；合成 Ship case n=1 ✅（`test_synthetic_ship_case_pairs_to_n_equals_one`）。

## 5. 明確沒做

- 沒開 AUTO；`GRADUATED = False`；`route_taken` 在 shadow 恆 HUMAN。
- 沒改 A1–A7／B1–B5、沒改 `jev-questions.json`／policy 常數（`questionset_hash` 不變）。
- 沒補 Ship 出口的任何 hard guard（§3 只稽核；補牙是 L2）。
- 沒做 C2 Read matcher、P3-4 Stage 3 極性、P3-1 AUTO live、P2-2 完整 report（`report` 仍是 W2 的分層最小版）、supermemory。
- 沒對真 TypeSafe API 送過請求；沒建任何 `.dev-flow/jev.yaml`；沒拿真 graduation 樣本充 n。
- 沒改 `_templates/7-review.md`（`verdict_source`／`attested_by` 是 P3-2）；因此真實 review 在 P3-2 之前 `label --from-review` 會 `refused: review_unverified`，這是預期，不是 bug。
- 沒進 main。
