---
title: jev-gate W7 — Stage 3 polarity「人要求才 Demo」（P3-4）／J2 遠期軌道 window 未核定（P3-3）
slug: jev-gate
status: W7 完成範圍：P3-4 契約面翻極性、attestation human-only 不動；P3-3 只釘死「window 未核定 → J2 永遠 shadow」；不進 main
date: 2026-09-23
base: claude/jev-w6-eligibility-3aslgp 7695d46（W6）→ 本分支 claude/jev-w7-stage3-j2-3aslgp
---

# W7 Stage 3 polarity + J2 遠期軌道

> **一句話**：Stage 3 觸發判定命中之後，**由人決定要不要 Demo**（人親填 `- Demo request: requested | not requested by human:<姓名> @ <日期>`）；
> Demo verdict／Verdict attestation 的 human-only 規則一個字都沒鬆。J2 沒有任何 AUTO_PASS 路徑：formal rolling window 未核定 → `eligibility` 永遠多一條 blocker、`route_taken` 永遠 HUMAN。
> **作者 ≠ 審查者**：不宣稱 Grok／owner PASS；P3-4 是 owner 2026-09-22 已裁方向（P0-3），本波做的是契約面落地，不是替 owner 決定。

## 0. 分支與 SHA

| 項 | 值 |
|---|---|
| 基線 | `claude/jev-w6-eligibility-3aslgp` `7695d46`（W6，PR #407 → research） |
| W7 分支 | `claude/jev-w7-stage3-j2-3aslgp`（commit SHA 見 PR） |
| main | **未動** |

## 1. P3-4 Stage 3 polarity：「觸發即必要」→「人要求才 Demo」

### 1.1 只翻什麼

| 舊 | 新 |
|---|---|
| 觸發判定任一命中 → Demo **條件式必要**；要跳過只能 2-decision Owner Call | 任一命中 → **人決定**：人親填 `- Demo request: requested \| not requested by human:<姓名> @ <YYYY-MM-DD>`；不要求 → 落檔即 N/A 可過 G2；要求 → 照原路產 Demo + Human verdict |
| — | Agent 不得代填 Demo request、不得代決；J3 只出建議句，不寫這一行 |

**沒翻的**：Human verdict ACCEPTED 必附 `- Verdict attestation: human:<姓名> @ <日期>`（`ATTEST_HUMAN`，同一個 regex 也拿來驗 Demo request 的 `by`）；REVISE 不得過、Owner Call 不得繞 REVISE；ACCEPTED 缺 attestation → 拒；test-only fixture 正式模式拒。既有 selftest p2 全部原句原期望不動。

### 1.2 動了哪些契約面

| 面 | 改動 |
|---|---|
| `hooks/_stage3_impl.py` | 新 `DEMO_REQUEST_LINE`／`DEMO_REQUEST_PLACEHOLDER`／`parse_demo_request()`；結果 JSON 多 `polarity: human_requests_demo`、`demo_request: requested\|not_requested\|implied_by_verdict\|invalid\|null`。判定順序：0 命中 → N/A → **Demo request 行**（非 `human:` 格式 → REJECT「Agent 不得代填」；`not requested` → PASS N/A）→ 原有 ACCEPTED/attestation → REVISE → Owner Call → 拒（分兩句：「人要求了 Demo 但未完成」／「人尚未決定要不要 Demo」）。舊檔相容：沒有 Demo request 行但 ACCEPTED + 人類 attestation → `implied_by_verdict` 放行 |
| `_templates/3-prototype.md` | H1 註「命中觸發判定 → 人要求才 Demo」；節名 `## Stage 3 觸發判定(命中 → 人決定要不要 Demo)`；九條後加 Demo request 行＋填法註解。保留舊牙 needle（純後端／兩檔皆不建／全未勾／選配） |
| `skills/dev-flow/SKILL.md` §4 | 觸發判定、Demo 由人要求、J3 只建議、跳過（舊路徑）、G2 Demo verdict 條件五段改寫 |
| `skills/dev-flow/stage3/nodes/{N1-trigger,N-skip,S0-question}.md` | N1 做什麼＋下一跳（0 命中 → N-skip；命中且不要求 → N-skip；命中且要求 → S0）；N-skip 進條件／做什麼收 not requested；S0 進條件要求 `Demo request: requested`。`graph.yaml` 下一跳順序不變（`check-devstage3-graph` 綠） |
| `notes/design/vnext-shared-contract.md` §2、`docs/dev/readme-contract-extract.md` §7、`guides/guide-dev-flow.html`（階段表 + G2 條件 ×2）、`notes/design/real-world-interaction.md` §4、`_templates/4-spec.md` 執行清單（guide `template4-checklist` parity 正本） | Demo verdict 條件句改成「人要求才 Demo」極性 |
| `scripts/check-realworld.sh` | Stage 3 模板牙 needle 改為 `"人要求才 Demo" in t3 and "Demo request" in t3` |
| `hooks/selftest.sh` p2 | +4 案（人不要求 → 放行／agent 代填 → 拒／人要求 + NOT_REVIEWED 無 OC → 拒／人要求 + ACCEPTED + attestation → 放行，且 JSON `demo_request: requested`）；`MIN_CASES` 469 → **473**，`test-architecture-guards` 靜態釘同步 |
| `scripts/devflow_jev/test_guards.py::W7J2TrackAndStage3Polarity` | 子程序真跑 `_stage3_impl.py` 八個情境（缺行拒／不要求放行／agent 代填拒／要求未完成拒／要求＋ACCEPTED＋attestation 放行／要求＋ACCEPTED 缺 attestation 拒／舊檔 implied_by_verdict／模板佔位視為未填）；契約面五檔都含「人要求才 Demo」＋「Demo request」 |

**不做的**：README 公開面（main-only parity）；既有 `docs/dev/<slug>/3-prototype.md`／`example/*` 產出檔的節名不回改（legacy heading 對 parser 無差，`section(proto, "Stage 3 觸發判定")` 前綴比對）；`scripts/fixtures/devstage3-graph`／`stage3-html` 舊節名 fixture 保留當 legacy 相容輸入。

## 2. P3-3 J2 遠期軌道：window 未核定 → 永遠 shadow

- `policy.J2_WINDOW_CANDIDATE = 50`（roadmap §4.1 候選值，**只是候選**）、`policy.J2_WINDOW_RATIFIED = False`（單一賦值；測試釘 `report`／`policy` 兩邊皆 False）。
- `report.eligibility(...)`：evaluations 含 gate J2 → 多一條 blocker `j2_window_not_ratified(candidate=50; formal rolling window pending; J2 stays shadow)`，`eligible=False`。
- runtime `eligibility --gate J2`：**空 store 也會**帶這條 blocker（不是「沒資料所以沒事」）；`status` 露出 `j2_window_ratified=False`。
- `policy.route_taken("J2", "live", …)` 維持 W5 的 `("HUMAN", "j2_shadow_window_not_ratified")`：yaml 把 J2 設 live 也走 HUMAN。
- **沒有** AUTO_PASS 分支、沒有 formal window／floor／source mix 進 spec；候選值不當門檻用。J2 thick packet（P2-8）與 experimental 題組 hash 不動。

## 3. 驗證

| 套件 | 結果 |
|---|---|
| `scripts/test-devflow-jev.sh` | **243/243**（地板 239 → 243） |
| `hooks/selftest.sh` | 460/473；13 紅 = 基線 W6 同一組環境紅（p3/pw/p4 doctor：Python 3.11 printer-python、docs/dev 副本；f4 唯讀 fail-open ×2）；新增 p2 四案全綠；基線 456/469 同一 13 紅 |
| `scripts/check-devstage3-graph.sh`、`test-devstage3-graph.sh` 33/33、`test-devstage4-graph.sh` 63/63、`check-stage3-proto-contract.sh` 27/27 | 綠 |
| `scripts/check-realworld.sh` | 173/174；唯一紅 = renderer `markdown_it` 缺（環境；基線同） |
| `scripts/check-methodology-corrections.sh` | 127/128；唯一紅 = renderer fixed point `markdown_it` 缺（環境；基線同）。`template4-checklist` parity 由 `_templates/4-spec.md` 同步後回綠 |
| `check-gate-verdict-write.sh` 25/25、`check-verdict-attestation.sh` 8/8、`check-gate-tokens`、`check-readme-markers`、`check-design-contract`、`hooks/gate-consistency.sh` 14/14 | 綠 |
| `check-ship-manifest` 26/26（report／runtime 副本回拷；列數與 version 未變）、`check-file-map` 232／235、`test-architecture-guards` 146/146、py-floor 230 heredoc | 綠 |
| 真 TypeSafe API | 沒有打 |

## 4. 明確沒做

- 沒開 J5 live（`J5_LIVE_RATIFIED=False` 不動）、沒開 J2 AUTO_PASS、`GRADUATED=False` 不動。
- 沒改 A1–A7／B1–B5、題組、正式 `questionset_hash`、policy 門檻／route formula。
- 沒動 Verdict attestation 規則、沒動 `devflow_gate.py` 寫入器、沒讓 Jev／agent 能寫 Demo request 或 verdict。
- 沒改 README 公開面、沒回改既有產出檔／example 的 Stage 3 節名。
- 沒進 main。
