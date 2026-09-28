---
title: jev-gate W6 — J5 eligibility 計算器 / P3-2 契約同步（live 未核准）
slug: jev-gate
status: W6 完成範圍：eligibility 機械已備、live 未核准；P3-2 研究分支可做部分已做、缺口明列；不進 main
date: 2026-09-23
base: claude/jev-w5-eval-3aslgp 883c9a0（W5）→ 本分支 claude/jev-w6-eligibility-3aslgp
---

# W6 J5 eligibility + 契約同步

> **一句話**：eligibility 的計算與 freeze 機械已備；**AUTO live 未核准、也沒有開關**。roadmap §5 的順序修正照做：
> 先算資格 → 契約同步／L2／ADR → 才談 live。本波沒有任何路徑能把 J5 設成 live 或把 AUTO_SHIP 寫進真實 G3。
> **作者 ≠ 審查者**：不宣稱 Grok／owner PASS；不宣稱錯誤率 ≤5%、不宣稱已達 graduation（n=1 的合成 case 只驗機制）。

## 0. 分支與 SHA

| 項 | 值 |
|---|---|
| 基線 | `claude/jev-w5-eval-3aslgp` `883c9a0`（W5，PR #406 → research） |
| W6 分支 | `claude/jev-w6-eligibility-3aslgp`（commit SHA 見 PR） |
| main | **未動** |

## 1. P3-1 eligibility（只計算／展示／freeze；不開關）

- **硬拒 live**：`scripts/devflow_jev/gate.py` 新常數 `J5_LIVE_RATIFIED = False`（測試釘只出現一次）。`effective_level("J5", …)` 算出 live 時**cap 成 shadow**，reason `j5_live_not_ratified(requested …; capped to shadow)` 留痕。這不是旗標：沒有環境變數、CLI 參數、yaml 鍵能翻它；要開 live 只能改常數（= 新 commit，走 P3-2＋L2/ADR）。W2 那條「yaml live → level live，靠 `j5_auto_not_graduated` 擋」的雙保險，W6 把第一道也關上；`optin-matrix.json` 該格 `expect: live → shadow`，W2 測試同步改寫（明改，非靜默）。`GRADUATED = False` 不動。
- **計算器** `report.eligibility(evaluations, metrics, primary_source)`：roadmap §5.1 八條寫成 `rules` 逐條 ok／detail：①真實 Ship 路徑（store-scoped by construction）②unique case dedupe ③same-evidence binding ④**單一 group**（`(gate, questionset_hash, model_resolved)` 多於一組 → blocker）⑤source class ⑥none 排除 ⑦mechanical override 分報 ⑧**primary 層已核定**（B3 leave_unset → 未核定 → blocker）。`floor`：n／Wilson／n_overturn／floor_met／frozen。§5.2 freeze：第一次有效 overturn → `circuit_breaker_state=frozen`、blocker `frozen_after_overturn(n_overturn=1; n stays 31, Wilson recomputed, no manual override)`；**n 不歸零、資料不抹**。函式簽名只有三個參數（測試釘 `{"evaluations","metrics","primary_source"}`），沒有 `wilson_override`／`force`。`live_switch: "absent"` 永遠如此。
- **runtime** `eligibility [--gate J5] [--primary-source …]`：走 `run_report` → `report.eligibility`；輸出帶 `j5_live_ratified=False`、`graduated=False`、`auto_allowed=False`、`live_switch=absent`。`status` 多 `j5_live_ratified`／`j2_window_ratified`。runtime 原文找不到 `--live`（測試釘）。
- 測試：30 筆 agree → `floor_met=True` 但沒 primary → 不 eligible（B3）；指定 primary → `eligible=True` 但 `live_switch=absent`；第 31 筆 overturn → frozen、n=31、Wilson=`wilson_lower(30,31)`；兩個 questionset group → blocker `4_single_group`；n=5 → `floor_not_met`；真實 store n=1 → `floor_not_met(n=1…)`。

## 2. P3-2 契約同步 —— 研究分支做得到的部分

| 同步面 | 做了什麼 | 牙 |
|---|---|---|
| 三份 gate 模板頂欄 | `_templates/{2-decision,4-spec,7-review}.md` 在 `verdict:` 後加 `verdict_source:`／`attested_by:`（註解寫明允許值、Jev 不得填） | `check-gate-verdict-write.sh` 模板缺欄必紅（+mutation） |
| `notes/design/gate-verdict-write.md` | 鎖死 6：verdict 必附出處；缺 = unverified（gate 照關、不進任何 graduation）；**Jev／自動化不得寫 `verdict:`、不得填 `attested_by`**；`agent:*` 只准搭 `fresh_agent_reviewer` | `check-gate-verdict-write.sh` CONTRACT_NEEDLES +4、mutation「刪 verdict_source 必紅」 |
| 寫入器 `scripts/devflow_gate.py` | `patch_md(..., reviewer=)`：有 reviewer 時代填 `verdict_source: human_attested` + `attested_by: human:<reviewer>`；沒 reviewer **不假填**（留 unverified）；reviewer 是 `agent:`／`jev*` → `ValueError` 拒收且不改 md | `check-gate-verdict-write.sh` write 實測 +2（25 項） |
| 「誰寫了 verdict」機械檢查 | 新 `scripts/check-verdict-attestation.sh`：掃 `docs/dev/*`／`example/*` 的 G1/G2/G3 檔；Jev／agent 冒 human／未知 source **必紅**；缺兩欄的舊檔（現況 31 份）只列，`--strict` 才紅；6 個負向 fixtures | 掛 `devflow-check.sh` methodology；8 項 |
| reviewer-selection 5 處＋guide parity＋`_gate_consistency_impl.py` ordered tuple | **未動、驗過綠**（`gate-consistency.sh` 14/14）。Jev 不進 reviewer 順序（它不是 reviewer，只出 shadow recommendation），所以 tuple 不該加 Jev | 既有 |

## 3. P3-2 缺口（研究分支動不了或不該動；AUTO live 前必補）

| 缺口 | 為什麼本波不做 | 誰／何時 |
|---|---|---|
| **L2／ADR accepted** | roadmap P3-2 明寫要走 dev-flow 自己的 Decide＋ADR；ADR 是 owner 的裁決，agent 不自寫自核 | owner／Rick，`research` 合回 main 前 |
| README 公開面／`docs/dev/readme-contract-extract.md` §7 parity 句（verdict 出處） | README 與 extract 有 parity 錨，main 流程的 dev-release 才同步公開面；研究分支改會讓 parity 牙紅 | 隨 ADR 一併 |
| 31 份既有 verdict 的 `verdict_source`／`attested_by` 回填 | 「絕不動 docs/dev/<slug>/ 已產出的 feature 檔」（B4 同一原則）；回填等於代人 attest | owner 決定是否回填；不回填就永遠 unverified、不進 n（合理） |
| `check-verdict-attestation.sh --strict` 進 CI | 現況 31 份 legacy 會紅；strict 要等回填或 owner 決定豁免清單 | 回填後 |
| 「未授權 agent 寫 verdict」的**寫入時**攔截（hook） | 現在是寫入器拒收 + 事後掃描；PreToolUse 層攔 `verdict:` 寫入要動 `_guard_impl.py`／`hooks.json`（W4 P1-F7 已列 Ship 出口沒有 hook） | 與 P1-F7 補牙同批（L2） |

## 4. 驗證

| 套件 | 結果 |
|---|---|
| `scripts/test-devflow-jev.sh` | **239/239**（地板 232→239） |
| `scripts/check-gate-verdict-write.sh` | 25/25（21 → 25：模板欄位、contract mutation、writer stamping、agent 拒收） |
| `scripts/check-verdict-attestation.sh` | 8/8（37 份 gate 文件；31 份 legacy unverified 只列；`--strict` 如預期紅） |
| `hooks/gate-consistency.sh` | 14/14（reviewer-selection 五處未動） |
| 模板相關：`check-spec-gate`×4、stage1–7 contract、devstage2/4/7 graph、design-contract、selfjudgment-tables、gate-tokens、readme-markers、test-spec-gate-e2e、adr-integrity、public-docs、history-integrity、no-stale-paths | 全綠 |
| `check-ship-manifest` 26/26（`devflow_gate.py`／gate／report／runtime 副本回拷；列數與 version 未變）、`check-file-map` 232／235、`test-architecture-guards` 146/146、py-floor（230 heredoc） | 綠 |
| 真 TypeSafe API | 沒有打 |

## 5. 明確沒做

- **沒開 `gates.J5: live`**（反而被 cap）；沒宣稱錯誤率、沒宣稱 graduation；沒用合成／smoke／21 次稽核湊 n≥30（合成 30 筆只在 `test_guards` 驗計算器，不進任何 store）。
- 沒改 A1–A7／B1–B5、題組、policy 常數；正式 `questionset_hash` 未變（gate.py 的常數不在指紋內）。
- §3 列的缺口全部沒做，也沒假裝做完。
- 沒進 main。
