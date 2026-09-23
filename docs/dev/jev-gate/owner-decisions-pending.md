---
title: jev-gate — 待 owner 裁決清單（W0/W1 收尾）
slug: jev-gate
status: 已落檔 —— owner 2026-09-23 裁「照建議／A B 過」（Rick-dev-flow）；A1–A7、B1–B5 鎖定，W2 開工
date: 2026-09-23
base: claude/w0-source-closure-3aslgp（W0/W1 squash 進 research/jev-supermemory 後續 W2）
---

# owner 裁決清單（W0/W1 收尾）—— 2026-09-23 已落檔

## 0. 2026-09-23 審核結果（owner 轉發的 Jev jev-1.13.0 建議；21 次合成／文件稽核一律不進 J5 n）

owner 對 W0／W1 品質的判定：**可進 research 討論，不可進 main、不可開真 runtime**；七守衛 foundation／127 測／tripwire／C10＋Gauntlet 1.4.0 一致；沒有 Jev 寫 G2／G3 verdict、沒有宣稱 production AUTO。

| 項 | Jev 建議 | 機率／信心 | 本分支狀態 |
|---|---|---|---|
| A1–A7 工程候選 | 暫定全收，標未校準 | noul 0.75 | **已落檔（2026-09-23 owner「照建議／A B 過」）**：全收、標未校準；W2 第一筆 `questionset_hash` 鎖這組值 |
| B1 signal.gate kind | 借 `important_discovery` | 1.00／0.99 | 已是現況；**已落檔（2026-09-23）** |
| B2 shadow durable | 維持寫 Git + `[jev]` 前綴 | 0.86 | 已是現況；**已落檔（2026-09-23）** |
| B3 graduation 主層 | 先 leave_unset（與 human_primary 幾乎打平） | 0.54／0.31 弱 | 已是現況（`primary_source=None`）；**已落檔（2026-09-23）** |
| B4 C10 legacy | 維持 PASS + approved／shipped／superseded | 0.98 | 已是現況；**已落檔（2026-09-23）** |
| B5 C10 fast lane | 只強制 full | 0.83 | 已是現況；**已落檔（2026-09-23）** |
| C1 manifest 版本 | W2 做 | 0.79 | **已落檔**：W2 同批 —— 契約 `ship_manifest_version` + `ship-manifest.json` `version` + doctor 逐列存在性／mode（本 PR） |
| C2 Read matcher | 不要無限等事故，另排 | 0.29＝反對乾等 | **已落檔：另排**（不阻塞 W2；owner 指定時窗後開） |
| C3 Stage 7 selftest | 盡快 P1 L1 | 0.74 | **已做**：`hooks/selftest.sh:2573-2580` s7c 段 +3 案（459→462），靜態釘同步；實跑新三案全綠，11 紅與乾淨 base 同集（環境：printer-python 3.11／root 唯讀） |
| C4 roadmap 筆誤 | 本分支改 | 0.81 | **已做**：`984-994` → `981-994`；P1-F6 註解改寫（它屬 W2 fixtures，不是分發） |
| D W2 | 等 A＋B 確認；PR 明改 tripwire | 0.86 | **已落檔**：A＋B 確認於 2026-09-23 → W2 開工；`scripts/test-devflow-jev.sh` 兩條 tripwire 在 W2 PR 明改（見 `w2-runtime.md`） |
| 合併就緒 | `ready_with_decisions_pending`（0.92）：決策落檔後再 squash 進 `research/jev-supermemory`，現在不進 main | — | **已執行**：W0/W1 squash 進 `research/jev-supermemory`（SHA 見 `w2-runtime.md` §0）；不進 main |

**W2 開工的兩個前提（owner 原話；2026-09-23 前提 ① 已成立）**：① owner 明確認可 A＋B（「照建議」／「A B 過」）—— 沒認就開 W2 會把未校準門檻鎖進第一個 `questionset_hash`；② W2 那支 PR 必須明改 `scripts/test-devflow-jev.sh` 兩條 tripwire（准建 `scripts/devflow-jev.py`、准網路），不可靜默放行；C1 與 W2 同批。仍不進 main；runtime 在本分支或合回 `research/jev-supermemory` 做。


> 這份原本只列**需要你決定**的事；2026-09-23 owner 裁「照建議／A B 過」後，A／B 各表即為**已落檔的裁決**（改任一個 = 新 `questionset_hash`，舊 calibration group 不延續）。已完成的內容在 `w0-source-closure.md`（W0）與 `w1-guard-foundation.md`（W1）。
> 每項給：現在的候選、為什麼這樣選、你可以怎麼改。沒有一項冒充已裁決；roadmap §0 的十條 owner 決策都沒動。

## A. 工程候選值 —— 已落檔 2026-09-23（改任一個都會換 `questionset_hash`，舊 calibration group 不延續）

| # | 項目 | 目前候選 | 位置 | 說明 |
|---|---|---|---|---|
| A1 | J1 前景 deadline | **2s、無 foreground retry** | `scripts/devflow_jev/policy.py` `J1_DEADLINE_S` | roadmap §8.2 候選值。超時 = no-op 走現況。 |
| A2 | daily cap | **500 attempts／500k input tokens，先到者停** | `policy.DAILY_ATTEMPTS_CAP` / `DAILY_INPUT_TOKENS_CAP` | retry、variants、remote reevaluation 都算 attempt；unknown usage 不退款。 |
| A3 | J5 AUTO 門檻 | **p(AUTO_SHIP) ≥ 0.85、evidence_complete ≥ 0.90、risk ≤ 1** | `policy.THRESHOLDS["J5"]` | 門檻設在 noul/score 值不設 confidence（0-draft §4）。數字是 W1 工程候選，未經任何真實 case 校準。J5 現在只 shadow，這組值只影響 `route_recommended`。 |
| A4 | J1 門檻 | **clarity ≥ 0.70、START ≥ 0.80、owner_call ≥ 0.50、ambiguity ≤ 1** | `policy.THRESHOLDS["J1"]` | 同上。 |
| A5 | J3 門檻 | **demo_worth_it ≥ 0.60** | `policy.THRESHOLDS["J3"]` | 只出 recommendation，不寫 verdict。 |
| A6 | breaker | **同 key 三連敗 open** | `policy.BREAKER_THRESHOLD` | — |
| A7 | risk_paths 預設清單 | migrations/、auth/、payment、billing/、secrets、.github/workflows/、ci/、Dockerfile、infra/ | `policy.RISK_PATHS_DEFAULT` | P2-4 正式化前的候選；縮窄會被 G6 留痕並強制 HUMAN。 |

## B. 設計選擇 —— 已落檔 2026-09-23（W1 採用欄即裁決）

| # | 問題 | W1 採用 | 替代 |
|---|---|---|---|
| B1 | durable 寫入時 `signal.gate` 的 kind 參數 | (a) 借既有 HIGH kind `important_discovery`；record 的 `kind` 仍是 `jev` | (b) 把 `jev` 加進 `memory/agentmem/signal.py` 的 `HIGH_SIGNAL_KINDS`（memory 模組 L2 變更） |
| B2 | J5 shadow 評估要不要進 durable（Git） | 是（roadmap decision 5：durable 是 ID/hash 正本）；`title` 固定前綴 `[jev]` 讓 HISTORY／context 一眼認得 | — （P0-6 結論：`kind=jev` 會混進 `ask` HISTORY 與 context 預載；`durable-check` 會常報 UNCOMMITTED） |
| B3 | graduation report 的 primary 層 | **未定**：`report.graduation()` 預設 `floor_met=None`，human_attested 與 fresh_agent_reviewer 各算各的 | roadmap §3.3-8 候選：human 主報表、fresh-agent companion；要你核定 |
| B4 | C10（E2E entry point）legacy 判準 | `verdict: PASS` **且** `status ∈ {approved, shipped, superseded}` 的 4-spec 不套 | 回填七份已出貨 4-spec（`docs/dev/{five-station-f2,five-station-f3,five-station-simplify,requirement-discovery-gaps,integration-before-verdict,host-stack-fit,diagram-ir-gate}`）；目前依「絕不動 docs/dev/<slug>/ 已產出的 feature 檔」沒回填 |
| B5 | C10 只強制 full lane | fast lane 選配（Profile 只有五欄） | 也強制 fast lane |

## C. W0 發現的缺口 —— 裁決狀態見 §0（C1 W2 同批、C2 另排、C3／C4 已做）

| # | 缺口 | 出處 | 建議 |
|---|---|---|---|
| C1 | ship-manifest 新增列**不會**同步到既有採用專案；契約沒有 manifest 版本欄，doctor 不逐列驗 | `w0-source-closure.md` §P0-8 | W2 P1-F1 一併：契約加 `ship_manifest_version` + doctor 逐列存在性（L2） |
| C2 | dev-talk 讀取白名單零機械執行（devtalk-guard 的 Read 分支沒掛在 Read matcher） | §P0-9 | 若 J1 落地後出現偷讀 `docs/dev/*`，補 `hooks.json` matcher 加 Read（要驗 Cursor/Codex 相容） |
| C3 | Stage 7 三條拒絕路徑 selftest 零案例；bare re-arm 文案誤導 | §P0-5 結論 7、判定第三點 | P1 期 L1 小修 |
| C4 | roadmap §1 W2 列的 P1-F6 疑為筆誤（P1-F6 是對抗 fixtures，ship 分發屬 P1-F1）；§0.1 的 `984-994` 行號實為 `981-994` | `w0-source-closure.md` §P0-8、§P0-5 | 已改（2026-09-23） |

## D. W2 開工條件 —— 2026-09-23 成立

- W2 = P1-F1 `scripts/devflow-jev.py` stdlib runtime。依 roadmap §0 第 2 條，開工那次 PR 必須**明改** `scripts/test-devflow-jev.sh` 的兩條 tripwire（零網路 import、runtime 檔不存在），不得靜默放行。
- A1–A7、B1–B5 已於 2026-09-23 核定；W2 寫出去的第一筆 `questionset_hash` 鎖住這組值。硬約束不變：仍無正式 AUTO（`route_taken` 的 J5 AUTO 需 graduated，W6 前恆 False）、雙閘門、七守衛行為不得鬆。

## 審核入口

- 分支：`claude/w0-source-closure-3aslgp`（基於 `research/jev-supermemory` 6824fa6）
- W0：`docs/dev/jev-gate/w0-source-closure.md` + `evidence/w0/`
- W1：`docs/dev/jev-gate/w1-guard-foundation.md`、`scripts/devflow_jev/`、`scripts/test-devflow-jev.sh`、`scripts/test-spec-gate-e2e.sh`
- roadmap 狀態列：`docs/dev/jev-gate/roadmap.md` P0-5～P0-9、P1-G1～G7、P2-1
