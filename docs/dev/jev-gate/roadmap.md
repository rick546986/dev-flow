---
title: jev-gate roadmap（有優先級）
slug: jev-gate
status: draft-v4（draft-v3 + 三輪 Jev 實測 + source/probe closure + W0–W7 整合）；W0 P0-5～P0-9 於 2026-09-22 收閘（見 `w0-source-closure.md`）；W1 七守衛 foundation + P2-1 同日落地（見 `w1-guard-foundation.md`；runtime 仍未寫）
date: 2026-09-22
base: origin/main 79b7aab
inputs: 0-draft-jev-supermemory-fit.md + 四份獨立審查（R1 落地耦合、R2 對抗性風險、R3 流程與 HITL、R4 校準量測）+ 一份出處核對 + v2 四維度 findings 覆核（D1 出處忠實度、D2 可行性、D3 優先級、D4 安全）+ jev-convergence.md owner 裁決 + 2026-09-22 外部 Codex/Jev smoke、rubric 與文件稽核結果（待另行歸檔，不視為 repo 內既存 evidence）
---

# jev-gate roadmap

> **文件狀態**：本檔是 `research/jev-supermemory` 的研究／落地規劃 draft-v4。它不代表 `main` 已改、Jev 已部署、任何 AUTO gate 已核准，也不把 guard pure-function prototype 當成完成產品。**進度**：W0（2026-09-22）、W1（2026-09-22）、W2（2026-09-23）、W3（2026-09-23）、W4（2026-09-23）、W5（2026-09-23）、W6（2026-09-23，資格計算器＋契約部分同步）已在 `research/jev-supermemory` 落地；J5 仍是 shadow（enqueue／drain／label；yaml live 被 cap），J2／J4 只實驗，沒有 AUTO。  
> **基線**：研究分支鎖定 `8a4370ad97d2c842057c281ecf56ead8b94f4a43`，相對 `main@79b7aaba2ee65ba5953873064a8f93962f86d097` 只新增研究文件，沒有 runtime code 變更。

## 0. 不再重投票的 Owner Decisions

draft-v4 以 draft-v3／`jev-convergence.md` 已記錄的 owner 裁決為約束，不重新表決：

1. **落地順序固定：J1 live → J3 recommendation → J5 shadow。** task routing／mixed 分類保留為 rubric research，不強塞進 MVP。
2. **七組守衛 P1-G1～P1-G7 的 foundation 全部完成且負面測試通過，才准寫 `scripts/devflow-jev.py` runtime；shadow 也算 runtime。**
3. **P2-1 executable e2e 檢查要在 J5 shadow 開始前完成。**
4. 出境必須 **`TYPESAFE_API_KEY` + 每專案 `.dev-flow/jev.yaml` opt-in** 雙閘門；預設不建 opt-in。
5. durable ledger **優先沿用 `memory/agentmem/durable.py::append_events()`**；只有 P0-6 證實 full sync/index／資料模型不適合時，才採備選。
6. **J5 graduation floor 保留：Wilson 95% 下界 ≥ 0.85 且 n ≥ 30 個有效、獨立、真實 Ship cases；第一次有效 overturn 立即 freeze。**這是 owner 接受的工程風險門檻，**不是「已證明錯誤率 ≤5%」**。
7. **J2 保留**，先做 P2-8 厚證據包、shadow 與 rolling-window 研究，排在 J5 之後；不刪。
8. **Stage 3 polarity 翻成「人要求才 Demo」**，另走契約變更；Demo verdict／attestation 仍為 human-only，不交給 Jev。
9. **supermemory 現在不接。**只有「現有 `dev-memory.py ask` 檢索已證實不足」且「確實需要跨專案共享記憶」兩條同時成立才重啟評估。
10. G1/G2/G3、scope guard、author≠approver、mechanical gate、risk ceiling、Quiz gate、human attestation 等既有控制，不得因 Jev 接入而被暗中繞過。
11. **2026-09-23（W0/W1 審核後）**：W1 工程候選值 A1–A7（J1 2s 無 retry、daily 500 attempts／500k tokens、J5 .85／.90／risk≤1、J1 .70／.80／.50／ambiguity≤1、J3 .60、breaker 三連敗、risk_paths 預設清單）與設計選擇 B1–B5（`signal.gate` 借 `important_discovery`、shadow 寫 Git + `[jev]` 前綴、graduation 主層 leave_unset、C10 legacy = PASS + approved／shipped／superseded、C10 只強制 full lane）**照建議落檔**；全部標「未校準」，改任一個 = 新 `questionset_hash`。C1 與 W2 同批、C2 另排、C3／C4 已做。正本：`owner-decisions-pending.md`。

### 0.1 draft-v4 相對 draft-v3 的實質修正

以下是 source/probe 或實測已足以要求修正的項目，不是新的 owner 投票：

- **API context limit 修正**：官方 `https://docs.typesafe.ai/models` 現行明示 Jev 1.13 為 **64k tokens per request**，同時另有 **32k tokens for `state` plus the longest question**。2026-09-22 的單題壓測（32,593 tokens 200、約 33,400 tokens 400）只支持 32k 單題路徑附近的行為，**不得再推成全 request 只有 32k**。
- **Score structured criteria 修正**：官方 `https://docs.typesafe.ai/primitives/advanced` 明示 Score `criteria` 的每個 entry 可以是 object。內部可用 `{level,label,description}`，但 API score index 仍由**陣列位置**決定；`level` 不控制 API index。adapter 必須嚴格驗證 `level == array_index`，不一致直接拒絕，**不得偷偷排序**，避免改變 questionset hash／rubric 語義。
- **Stage 7 run 說法修正**：`hooks/_exec_impl.py:981-994` 可沿用 Stage 6 state；`1023-1030` 在 Stage 7 bare review 無 state 時可 new `run_id`、寫 `exec-v4`、`phase=review`。因此刪除「只有 Stage 6 start 才會有 run_id」的絕對說法；但 `_templates/7-review.md:62` 的武裝是建議，不是 runtime 保證，**P0-5 lifecycle 實測仍未完成**。→ 2026-09-22 W0 已實測，結論見 `w0-source-closure.md` §P0-5（同 slug re-arm 會換 `run_id`；`run_id` 只作 provenance，不作 case identity）。
- **durable events 修正**：已在隔離目錄小 probe 證實 `append_events()` 可接受 `kind=jev` 與額外 metadata，且同 `event_id` append 兩次只留一列；但尚未證明 full sync/index roundtrip、custom 欄位經 `sync.py:198-211` 後的保存方式，以及多 writer 無 lost update。`append_events()` 的 read-modify-atomic-replace 也不能自行推成「同 session 多 writer 安全」。→ W0 P0-6 已實測：同 session 檔決定性交錯 lost update 5/10、異 session 檔 0 lost；見 `w0-source-closure.md` §P0-6。
- **label 綁定修正**：目前的 verdict 不能自動當成歷史同一 Jev decision 的 label。必須綁 `feature/gate + artifact/evidence hash + HEAD + evaluation timestamp + reviewer source`；只允許同一證據版本配對。
- **重跑去重修正**：同一次 semantic decision 的 timeout retry、措辭 variants、remote reevaluation、同 feature 同證據重跑都不得增加 graduation `n`。
- **replay 修正**：Git durable 只放 identifier/hash/結構化指標；完整已去識別 packet、questions、raw response 住 gitignored local replay store。replay 分成「stored-response deterministic replay」與「remote reevaluation」兩種，不混為一談。
- **manifest 變版修正**：questions、rubric/schema、packet builder、policy、route formula、normalization 任一變版，都必須產生新的 evaluation manifest／`questionset_hash`，不得延續舊 calibration group。
- **引用污染限制**：`primary_request`／`quoted_context` 分欄、中性措辭、等長、grep/self-check 都只能稱為降低 reference contamination 的控制，**不能宣稱已抗 prompt injection**；負面 fixtures 必須保留。
- **mixed rubric 仍未解**：第二批真實 smoke 中 `feature + tests + docs` 的 `multiple_independent_deliverables.noul = 0.72`，是實際反例。不得因其他 5 case 表現好就宣稱 mixed 已解；也不得自動拆任務。

### 0.2 外部 Jev 實測的定位

2026-09-22 外部交付共包含 API smoke、12 個第一批 routing cases、6 個第二批 rubric cases，以及兩次 roadmap 原文明示稽核；均為 HTTP 200、`response.model=jev-1.13.0`。其中：

- 第一批 12 個 routing case 全符合事先合成期待，但它們**不是人工 gold、不是獨立 holdout**。
- 第二批 6 個 case 暴露 `feature-with-supporting-work` 的 mixed `.72` 反例；`primary_request`／`quoted_context` 分欄則把部分引用污染訊號從先前 `.38` 降到 `.04/.05` 左右，值得繼續，但不構成抗注入證明。
- roadmap／整合稿的 Jev 明示稽核只能用來找「文件有沒有寫清楚」，不是 approval、不是 calibration、不是上線依據。
- **這 21 次合成／文件稽核呼叫一律不得進 J5 graduation denominator。**

這些外部結果目前**不假裝是 repo 內既存 evidence 檔**；若日後歸檔，需另走正式 evidence naming／privacy 檢查。

## 1. 優先級與工作包

| 級 | 意思 | 完成才准進下一級？ |
|---|---|---|
| **P0** | 開工前 source closure、實測與 owner 已裁項整理 | 是 |
| **P1** | MVP foundation：七組安全守衛、runtime/replay、J1/J3、J5 shadow 起跑 | 是；七 guard foundation 未完成不得寫 runtime |
| **P2** | 強化與量測：e2e、report、J4、risk ceiling、J2 厚包 | 可部分與後續研究並行；P2-1 例外提前 |
| **P3** | 契約改動／AUTO gate；必須走 dev-flow 自己的 Decide + ADR/L2 | 以真實 shadow 樣本與契約同步為前提 |
| **P4** | 延後／不做 | — |

完整交付切成八個工作包；這是排程包裝，**不取代 P0/P1/P2/P3/P4 原編號**：

| Work package | 範圍 | Go 條件 |
|---|---|---|
| **W0 Source closure** | P0-1～P0-10 的 source/probe closure | P0 未決 source 不再阻塞 guard 設計 |
| **W1 七組守衛 + 提前 e2e** | P1-G1～G7 的 pure/schema/fake-transport foundation + P2-1 | 七組負面測試與 e2e gate 全綠；仍沒有真 runtime |
| **W2 stdlib runtime / replay / manifest 分發** | ✅ 2026-09-23：P1-F1、P1-F5、P1-F6、P0-8（C1）落地，見 `w2-runtime.md`；仍無 hook 接線、無 AUTO | 七 guard foundation 已完成；replay/data boundary 通過 |
| **W3 J1 / J3** | ✅ 2026-09-23：P1-F2、P1-F3，見 `w3-j1-j3.md` | J1 no-op fallback 正確；J3 只 recommendation |
| **W4 J5 shadow** | ✅ 2026-09-23：P1-F4、P1-F7 + label binding/dedupe，見 `w4-j5-shadow.md`；仍 shadow、無 AUTO | J5 不阻塞現有 G3；case provenance 可驗 |
| **W5 評估 / J2 厚包 / J4 實驗** | ✅ 2026-09-23：P2-2、P2-3、P2-4、P2-7、P2-8，見 `w5-eval-j2-j4.md`；P2-5／P2-6 留 AUTO live 之後 | 只 shadow/research；不自動放行 |
| **W6 J5 AUTO + 契約先完成** | 🧪 2026-09-23：P3-1 **只有資格計算器**（`eligibility`；live 開關不存在，`gate.J5_LIVE_RATIFIED=False` 把 yaml live cap 成 shadow）；P3-2 研究分支可做的同步已做，缺口明列（`w6-j5-eligibility-contract.md` §3）；**live 未核准** | eligibility 達標 + L2/ADR + P3-2 全同步後才可 live |
| **W7 獨立 Stage3、後期 J2** | P3-4；之後 P3-3 | Stage3 可獨立 L2；J2 window 未核定前永遠 shadow |

## 2. P0 — 開工前 source closure

| ID | 狀態 | 做什麼 | 驗收 | 量 | 依賴 | 出處 |
|---|---|---|---|---|---|---|
| **P0-1** | ✅ 已完成證據 | 本機 shell 暫設 `TYPESAFE_API_KEY`，跑 Noul／Choice／Score smoke | HTTP 200；`model=jev-1.13.0`；回應欄位與官方 API 一致；已觀察約 0.67s 小包延遲 | S | — | 外部實跑 + TypeSafe API docs |
| **P0-2** | ✅ source-closed；probe 有邊界 | 修正 context limit：官方現行為 request 總 64k；另有 `state + longest question` 32k。保留既有 32k 單題 probe 作實測證據，但不外推總 request | 文件不得再寫「總上限=32k」；packet builder 同時檢查兩條限制；需要 fan-out 壓測時另作 W0 診斷，不改 owner 流程 | S | P0-1 | `docs.typesafe.ai/models` + 外部單題 probe |
| **P0-3** | ✅ Owner 已裁 | Stage 3 polarity 從「觸發即必要」翻成「人要求才看」 | 2026-09-22 owner call 已記；正式落地另走 P3-4 L2/contract change | S | — | R3 + owner |
| **P0-4** | ✅ Owner 已裁 | 出境預設採 key + 每專案 `.dev-flow/jev.yaml` opt-in | 預設不建；`dev-setup` 每專案只在使用者同意後建立 | S | — | R2/R3 + owner |
| **P0-5** | ✅ probe 完成（W0）；結論見 `w0-source-closure.md` §P0-5：run_id 有三個生成點、Stage6→7 同 run、同 slug re-arm／bare 每次新 run、obs 只在武裝期 | 核對 Stage 7 run lifecycle：`_exec_impl.py:981-994` 可沿用 Stage6 state；`1023-1030` bare review 可 new `run_id`/`exec-v4`/`phase=review`；但 `_templates/7-review.md:62` 武裝只是建議 | 跑一個真 Stage6→Stage7 與一個 bare Stage7 review，記錄何時有 `exec.json`、`run_id`、何時 stop；用結果決定 J5 run_id/observability 可用性 | S | — | repo source + `evidence/w0/p0-5-run-lifecycle.json` |
| **P0-6** | ✅ probe 完成（W0）；`append_events()` 可沿用但有四條硬邊界（canonical 欄位／`evt_` id／每 writer 獨立 session／自帶 `signal.gate`），見 `w0-source-closure.md` §P0-6 | 優先驗 `append_events()`：已證 `kind=jev` + extra metadata 可 append，同 event_id 重複只一列；再補 full sync/index roundtrip、custom metadata 保存、多 writer lost-update 測試 | 若 full roundtrip 與 multiwriter 安全滿足需要 → durable metadata 走 `.dev-flow/events`；否則提出最小備選，不直接新開 raw ledger namespace | M | — | `evidence/w0/p0-6-durable-events.json`；`sync.py:198-212` 已驗（自訂欄位被丟、`:210-212` 非法 id 重生） |
| **P0-7** | ✅ 完成（W0）；每支一段限制 + guide parity 14 錨行號，見 `w0-source-closure.md` §P0-7 | 精讀 `_exec_impl.py`、`devflow-lib.py`、`_obs_impl.py`、`memory/agentmem/sync.py`、`durable.py`、`notes/design/gate-verdict-write.md`、file/write-scope 檢查、`skills/dev-setup/SKILL.md` 升級段落、`check-dev-setup-discipline.sh`、guide parity 區塊 | 每支一段「對 jev-gate 的限制」；guide parity 區塊列出實際 section/line | M | — | R1、D3 |
| **P0-8** | ✅ probe 完成（W0）：**不會自動同步**；母版側 `check-ship-manifest.sh` 有牙、採用側零牙 → W2 要 manifest 版本 + doctor 逐列，見 `w0-source-closure.md` §P0-8 → ✅ W2 C1（2026-09-23）落地：契約 `ship_manifest_version` + manifest `version`（列內容指紋）+ `hooks/_doctor_impl.py` 6e 逐列存在性／mode + `check-ship-manifest.sh` ⑥；manifest 自身成散發列 | `dev-setup` 升級模式：既有採用專案遇到 ship-manifest 新增 `devflow-jev.py`／題組／schema 時是否會同步 | 實際 upgrade fixture；若不會自動同步，W2 必須增加 manifest-version 檢查或明列人工 upgrade | S | P0-7 | R3、D1 |
| **P0-9** | ✅ source-closed（W0）：**不算**；J1 ASK_MORE 每輪從 S0–S2 重盤；讀白名單零機械執行，見 `w0-source-closure.md` §P0-9 | dev-talk 讀取白名單：路由層傳入舊 `1-discussion.md` 是否算使用者主動指名 | 一句結論 + source line；若不算，J1 ASK_MORE 每輪文件必須明說會從 S0–S2 重新盤查 | S | — | R3、D3 |
| **P0-10** | ⏸ 落 main 時才做 | 以 `scripts/status-update.sh` 將 jev-gate 登記到 `docs/dev/STATUS.md` Active | `check-status-policy.sh` 綠；feature/research branch 不直接改 main-only Active 表 | S | — | D3 |

### 2.1 P0 已確認的 API / protocol facts

- Endpoint：`POST https://api.typesafe.ai/v1/systemone`；本案 pin `jev-1.13.0`，不用 alias 當 calibration group identity。
- `Noul` 沒有獨立 confidence；Choice／Score 有 distribution-derived confidence。**confidence 不等於歷史正確率。**
- Score `criteria` 可使用 object entry；但 index 由 ordered array position 決定。內部若使用 `level`，必須要求 `level == index`，不一致 fail validation。
- Jev 不生成自由文字、不能代替長鏈架構 reasoning；J1/J2/J5 問題必須拆 atomic signals，再由 deterministic policy 組合。
- 英文是主要訓練語言；繁中／英文需分 slice 評估，不預設同 threshold。

## 3. P1 — MVP

### 3.1 七組守衛 foundation

> **硬順序**：以下 P1-G1～G7 先以 schema、pure functions、fake transport、fixtures 實作與測試；七組全部通過前，**不建立可對真 API 發送的 `scripts/devflow-jev.py` runtime，包含 shadow**。  
> W1 通過只代表 **guard foundation**，不等於 Jev runtime 完成、production-ready 或已安全上線。

| ID | 狀態 | 做什麼 | 驗收 | 量 | 依賴 |
|---|---|---|---|---|---|
| **P1-G1** | ✅ foundation（W1 2026-09-22；pure/schema/fake transport + 負面測試，**不是 runtime**）：`scripts/devflow_jev/packet.py`；見 `w1-guard-foundation.md` | **Evidence packet + reference isolation**：header 機械事實永不砍；body 才可裁剪。分 `primary_request`、`quoted_context`、`source_facts` 等欄位；選路題維持中性描述、長度差控制、正反證據。self-check/grep 只作形式控制，文件明寫「不構成 prompt-injection immunity」。shadow/eval 可跑 wording variants，但 variants 同 semantic case 不增加 n | 超大 body → `truncated=true` 且 route 強制 HUMAN；quoted injection／exit_code 與 tail 衝突／reference governance fixtures 均有負面測試；`feature+tests+docs` mixed=.72 反例保留 | M | P0-2 |
| **P1-G2** | ✅ foundation（W1 2026-09-22；pure/schema/fake transport + 負面測試，**不是 runtime**）：`policy.py`（2s／500／500k 仍是候選值） | **Failure/no-op、deadline、breaker、budget**：HTTP/JSON/schema/error 一律 no-op 回現況。候選工程值：J1 foreground **總 deadline 2s、無 foreground retry**；這是 v4 新增待核定預設，不冒充 owner 裁決。J5 shadow 不等待 HTTP，只 enqueue；本地 enqueue 成本要量測，不宣稱 0ms。舊 draft「2s + 1 retry」保留為歷史提案，不自動沿用 | mock 400/401/422/429/529/timeout/schema error 均不改現有 route；session/gate breaker 可測；J1 超時立即走原流程；J5 enqueue latency 有測量 | M | W0 |
| **P1-G3** | ✅ foundation（W1 2026-09-22；pure/schema/fake transport + 負面測試，**不是 runtime**）：`gate.py` | **雙閘門**：key + `.dev-flow/jev.yaml`；`mode` 與 `gates[Jn]` 生效等級 = min，`off < shadow < live`。owner default：J1 live、J3 recommendation/live、J5 shadow；專案未 opt-in 零出境 | `mode:off + gates.J5:live` 不呼叫；只有 key 沒 opt-in 不呼叫；只有 opt-in 沒 key no-op | S | P0-4 |
| **P1-G4** | ✅ foundation（W1 2026-09-22；pure/schema/fake transport + 負面測試，**不是 runtime**）：`ledger.py`（依 P0-6 四條邊界；備選未啟用） | **雙層 ledger/replay**：durable 優先 `append_events()`，只存 IDs/hashes/結構化指標；完整 sanitized packet、exact questions、raw response 放 gitignored local replay store。local 缺檔時 durable 記 `not_replayable`，不得假重建。若 P0-6 判定 append_events fullroundtrip/multiwriter 不適合，再提出備選 | Git diff 不含 raw packet/醫療資料/log；stored-response deterministic replay 可離線重算 route；remote reevaluation 產新 evaluation，不覆蓋舊 response；multiwriter 測試結果明確 | M | P0-6 |
| **P1-G5** | ✅ foundation（W1 2026-09-22；pure/schema/fake transport + 負面測試，**不是 runtime**）：`manifest.py` + `jev-questions.json` | **Question/evaluation manifest 治理**：`jev-questions.json` + schema；`questionset_hash` 實際 hash 完整 evaluation manifest：questions、rubric/schema version、packet_builder_version、policy_version、route_formula_version、normalization_version。Score object entries 可用，但 `level==index` 嚴格驗證，不一致拒絕、不排序 | 任一 manifest component 改變 → 新 hash、舊 calibration group 不延續；Score `[level:1,...]` 放在 index0 fixture 必須紅 | M | — |
| **P1-G6** | ✅ foundation（W1 2026-09-22；pure/schema/fake transport + 負面測試，**不是 runtime**）：`provenance.py` | **防造假／derived-only**：`route_recommended`、`route_taken` 只能由核算 policy 導出；gate live 狀態需受控核算／stamp；risk_paths 變窄跨 session 留痕；修改 Jev runtime/questions/config 當次一律 HUMAN。hash 只做完整性，不假裝 identity/auth | 手改 route、偽造 matching hash、縮 risk_paths、同 session 可疑 feedback 各有負面測試；report 能重算不一致 | M | P1-G4、G5 |
| **P1-G7** | ✅ foundation（W1 2026-09-22；pure/schema/fake transport + 負面測試，**不是 runtime**）：`attestation.py`（模板欄位留 P3-2） | **Verdict provenance tripwire**：G1/G2/G3 frontmatter 附 `human_attested`／`fresh_agent_reviewer`／`owner_self_review` 等來源。格式 attestation 是 provenance tripwire，**不是 authentication**；`human:<name>` 或換 session 都不能證明真實身份。P1-G7 前的舊 label = `unverified` | 缺／不合法 attestation → unverified 且不進 graduation；report 分層顯示 human_attested 與 fresh_agent，不把兩者偷偷混成同一主率 | M | P1-G4 |

### 3.2 P1 功能

| ID | 狀態 | 做什麼 | 驗收 | 量 | 依賴 |
|---|---|---|---|---|---|
| **P1-F1** | ✅ W2（2026-09-23）：`scripts/devflow-jev.py` stdlib runtime（status／pack／ask／replay／reevaluate／feedback／report）；雙閘門 off → exit 0、零網路、零寫入；`test-devflow-jev.sh` 兩條 W1 tripwire 明改；ship-manifest 分發 runtime + `devflow_jev/` 套件（24 列）。**shadow／no-op runtime，`GRADUATED=False` 寫死，不是 production AUTO**；J1/J3 接線在 W3（見 `w3-j1-j3.md`），J5 仍在 W4。見 `w2-runtime.md` | `scripts/devflow-jev.py` stdlib runtime：`pack`／`ask`／`report`／`feedback`／`replay`；`urllib/json/hashlib`；新增 `scripts/test-devflow-jev.sh` 並在 `devflow-check.sh all` 顯式登記；ship-manifest 分發 | 七 guard foundation 已先全綠；未設 key/opt-in exit 0 且零網路；0.36 AUTO argmax fixture 不得導出 AUTO；`methodology/test-devflow-jev` 在 all 中實際 PASS | M | P0-7、P0-8、P1-G1～G7 |
| **P1-F2** | ✅ W3（2026-09-23）：Decide 入口 `handoff --gate J1`（內部 `ask --gate J1`）；失敗／逾時／off = 照舊流程；ASK_MORE ≤2 輪且從 S0–S2 重開。見 `w3-j1-j3.md` | **J1 live：clarity first**。dev-talk 結束、Decide 前評估；不把 task type/mixed 當 MVP。題組至少拆 `goal_clear`、`scope_clear`、`acceptance_clear`、`owner_call_pending`、`ambiguity`、`next`。`next` 只決定 START_DECIDE／ASK_MORE／NEEDS_OWNER_DECISION，**不能拿 next probabilities 猜缺哪一維**；ASK_MORE 主題由 atomic clarity signals 決定。最多 2 輪，每輪仍是完整 11 步 dev-talk，N13 人類點頭不省 | J1 成功可省略重複「夠清楚嗎」；失敗/timeout 等同未啟用 Jev；最多兩輪後轉 owner question；主題句不抄題組原文；P0-9 白名單結果反映在流程 | M | P1-F1、P0-9 |
| **P1-F3** | ✅ W3（2026-09-23）：`handoff --gate J3` 只顯示建議；不寫 ACCEPTED／attestation／G2。見 `w3-j1-j3.md` | **J3 recommendation**：只顯示「值得人 Demo／不值得」建議；不是 G2 AUTO_PASS，不動 Demo verdict/attestation；與 Stage3 polarity contract change 分離 | `_stage3_impl.py` human attestation selftest 綠；任何 Jev response 都不能寫 ACCEPTED | S | P1-F1 |
| **P1-F4** | ✅ W4（2026-09-23）：S2d-fresh 後 `enqueue`（零網路、實測 p50/p95、G3 照走）→ N5 verdict 之後 `drain`（worker，失敗只記 shadow failure）→ `label --from-review`（same-evidence binding；HEAD／evidence 變了就拒）；variants／retry／reevaluate 同 `case_id`，n 不膨脹；`GRADUATED=False`。見 `w4-j5-shadow.md` | **J5 shadow + automatic evidence-bound pairing**：P2-1 先完成；Final Fresh Run/e2e/Gauntlet/review evidence 固定後 enqueue J5，現有 G3 繼續，不等 HTTP。Jev evaluation 與後續 label 綁 same `feature + gate + artifact_hash + evidence_hash + HEAD + timestamps`；不同 evidence version 不得配對 | 一個真 Ship case 能配成 n=1；J5 API 慢／失敗不延遲 G3；HEAD/evidence 改變後舊 evaluation 不被新 verdict 誤標；同 case variants/retries n 仍是 1 | M | P1-F1、P0-5、P2-1 |
| **P1-F5** | ✅ W2（2026-09-23）：`state.py` 把 `policy.Budget`／`Breaker` 落盤 `.devflow/jev/state/`（UTC 日切；attempts／tokens 先到者停；unknown usage 不退款；reevaluation 也扣）。候選值仍是 A2／A6，未校準 | **節流與 budget**：待核定候選 daily cap = **500 attempts 或 500k input tokens，先到者停**。retry、phrasing variants、remote reevaluation 都算 attempt/usage；未知 usage 不得當 0 再退款，應保守保留該 attempt 的預算上界，只有可信 usage 才 reconcile | 超任何一個 cap 後 no-op／停止新 evaluation；retry/variant 確實扣 budget；unknown usage 不會使帳面下降 | S | P1-F1 |
| **P1-F6** | ✅ W1／W2：`scripts/fixtures/devflow-jev/`（exit_code/tail 衝突、quoted「ignore rules」、reference governance、mixed .72、0.36 argmax）全部由 `test-devflow-jev.sh` 帶起；W2 加 runtime 層 0.36 fixture 實跑不 AUTO。結果只證形式控制，不宣稱抗 injection | **對抗／reference fixtures**：exit_code=1 但 tail 說 pass；tail/quoted_context 含「ignore rules」；quoted governance adopt/no-adopt；feature+tests+docs mixed=.72 反例。primary/reference 分欄只是控制，不宣稱抗 injection | 全部 fixture 由 `test-devflow-jev.sh` 帶起；結果可顯示模型仍受污染，但不得因此繞過 deterministic header/policy | S | P1-G1 |
| **P1-F7** | ✅ 文件（W4 2026-09-23）：commit／push／PR／merge／tag 逐步 `auto|human` + 真實 guard 行號，缺口明列（沒有任何 hook 擋 git commit/push/merge/tag；`_dispatch_impl.py` 只是窄版首派最高階 fail-open）。見 `w4-j5-shadow.md` §3 | **Ship 出口 auto/human 歸屬**：commit/push/PR/merge/tag 逐步 source audit；核 `_guard_impl.py`／`_dispatch_impl.py` 實際保障。特別註明 `_dispatch_impl.py` 只是窄版「首派最高階」fail-open discipline guard，不能寫成完整權限守衛 | 每一步都有 `auto|human` + 真正 guard/source line；找不到實際 guard 的「永遠 human」要明列缺口，不靠文案想像 | M | P0-7 |

### 3.3 Durable event 與 local replay schema

Durable metadata 示意；實際欄位受 P0-6 roundtrip 結果約束：

```json
{
  "event_id": "jev-J5-...",
  "kind": "jev",
  "evaluation_id": "eval_...",
  "case_id": "case_...",
  "gate": "J5",
  "slug": "contract-expiry-reminder",
  "session_id": "...",
  "run_id": "... or null",
  "mode": "shadow",
  "questionset_hash": "sha256:manifest...",
  "model_requested": "jev-1.13.0",
  "model_resolved": "jev-1.13.0",
  "packet": {
    "hash": "sha256:...",
    "ref": "local-replay://...",
    "replay_status": "available",
    "tokens": 18342,
    "truncated": false,
    "truncated_bytes": 0
  },
  "evidence": {
    "feature": "...",
    "gate": "J5",
    "artifact_hash": "sha256:...",
    "evidence_hash": "sha256:...",
    "head_sha": "...",
    "evaluated_at": "..."
  },
  "answers_summary": {
    "g3_route": {
      "choice": "AUTO_SHIP",
      "probability": 0.91
    },
    "risk": {
      "score": 0.8
    },
    "evidence_complete": {
      "noul": 0.97
    }
  },
  "route_recommended": "AUTO",
  "route_taken": "HUMAN",
  "route_reason": "shadow_mode",
  "feedback": {
    "verdict": "agree",
    "source": "human_attested",
    "reviewer_ref": "...",
    "artifact_hash": "sha256:...",
    "evidence_hash": "sha256:...",
    "head_sha": "...",
    "feedback_at": "..."
  },
  "usage": {
    "input_tokens": 0,
    "usage_status": "known|unknown_reserved"
  },
  "error": null,
  "at": "..."
}
```

規則：

1. **Git durable 不存完整 packet/questions/raw response。**完整資料只能進 gitignored local replay store，且 packet builder 必須先套 privacy／去識別規則；醫療原文、secret、logs/diff 全文不得因 Jev ledger 進 Git。
2. `packet_ref` 缺檔 → `replay_status=not_replayable`；不得用現在 repo 狀態「重建一份看起來像的 packet」冒充原輸入。
3. **Stored-response deterministic replay**：完全不呼叫 TypeSafe；讀原 raw response + 原 evaluation manifest，重算 policy/route/report，應具 deterministic 可重現性。
4. **Remote reevaluation**：用已保存的 sanitized packet/questions 對 pinned model 再呼叫；產生新的 `evaluation_id`，保留與原 observation 的 lineage，不覆蓋原 raw response，也不增加同一 semantic case 的 graduation n。
5. `case_id` 必須對應 unique semantic Ship decision。timeout retry、phrasing 三跑、remote reevaluation、同 evidence 重 ask 都共享同一 case_id。
6. 同一 feature 反覆修正若 `artifact_hash/evidence_hash/HEAD` 不同，不代表自動是獨立 Ship case；formal spec 必須定義「獨立 Ship」邊界，避免一個 feature 靠反覆修補灌 n。
7. label 只接受**同 evidence version**：evaluation 與 verdict 的 feature/gate/artifact/evidence/HEAD 必須一致；`none != agree`，unverified 不進 graduation。
8. primary graduation report 應把 `human_attested` 與 `fresh_agent_reviewer` 分層；**待 formal spec 核定**哪一層作 primary，v4 候選建議是 human 作主報表、fresh-agent 作 companion slice。

### 3.4 Evaluation manifest / group key

owner 保留三欄 grouping：

```text
(gate, questionset_hash, model_resolved)
```

不額外加第四欄。但 `questionset_hash` 必須由完整 manifest 產生：

```json
{
  "questions": "...",
  "rubric_schema_version": "...",
  "packet_builder_version": "...",
  "policy_version": "...",
  "route_formula_version": "...",
  "normalization_version": "..."
}
```

任一欄改變 → 新 `questionset_hash` → 新 group、`n=0`。這是「保持三欄 group key」與「policy/packet 改版不沿用 calibration」同時成立的方式。

### 3.5 J1/J5 執行模式不同

**J1 live** 是互動式同步 gate：

- 待核定候選：總 wall-clock deadline 2 秒。
- 不做 foreground retry；失敗直接 no-op 走現況。
- retry 若日後開啟，必須計入 daily attempt/token budget。
- 這個 2 秒是工程候選值，不是 owner 裁決或 TypeSafe SLA。

**J5 shadow**：

- 現有 G3 不等待 TypeSafe HTTP。
- 只允許本地 enqueue/serialize 的小成本在前景，且必須實測 p50/p95；不得寫「0ms」。
- worker API failure 只寫 shadow failure，不改 G3。
- evaluation mode 可跑 phrasing variants；但 `case_id` 去重，graduation n 不膨脹。

## 4. P2 — 強化與可量測

| ID | 狀態 | 做什麼 | 驗收 | 量 | 依賴 |
|---|---|---|---|---|---|
| **P2-1** | ✅ 有牙（W1 2026-09-22）：4-spec `E2E entry point` 欄 + `check-spec-gate.sh` C10（full lane 且未 G2 PASS 必答；legacy 不套）+ Gauntlet 1.4.0 e2e 視同 Required；見 `w1-guard-foundation.md` §3 | **Executable e2e 有牙**：涉互動／對外 API feature 的 Verification Profile 必含 `e2e` 單一入口，或明寫無 + 理由；Final Fresh Run 執行、Gauntlet 驗、J5 header 收摘要 | 缺 e2e 且無理由 → G2 紅；P1-F4 不得在本項前開始累 J5 樣本 | M | P0-7 |
| **P2-2** | ✅ W5（2026-09-23）：`report.eval_metrics`（unique cases／分層 n·agree·overturn·Wilson／labeled_fraction／truncation_rate／Brier／逐題／route_reason 分層／breaker·freeze）；mechanical override 不進 denominator；`report` 子命令走真實 replay store；合成 ledger 只驗計算器 | **report/eval**：unique cases、human/fresh-agent 分層、same-evidence binding、n_agree/n_overturn、Wilson 95%、labeled_fraction、truncation_rate、Brier/逐題 metrics、call breaker/circuit freeze、route_reason 分層；21 次 smoke/audit 永遠不進 J5 n | 合成 ledger 只驗計算器；真實 J5 report 只數 unique valid Ship case；variant/retry 不增 n；wrong HEAD label fixture 被拒 | M | P1-G4、G7 |
| **P2-3** | ✅ W5 實驗（2026-09-23）：`j4-assist`＋`policy.route_j4`／`escalate_to`（只升一層、fable=opus 層）；failure_category 用 agent-event enum；題組在 `jev-questions-experimental.json`（獨立 hash）；assist-only，不動 `_dispatch_impl.py` | **J4 升階路由**：failure_category 沿用既有 enum；escalate_to 不得跳 model tier；SPEC/ENV/IMPL/UNKNOWN 僅作 routing signal | 全程 shadow/assist 起跑；tiering 檢查綠；不把 `_dispatch_impl.py` 說成完整權限守衛 | M | P1-F1 |
| **P2-4** | ✅ W5（2026-09-23）：`enqueue` 自動推 changed_paths（merge-base／HEAD commit）→ `risk_ceiling_hit` → J5 一律 HUMAN、`route_reason=risk_ceiling_override`（fixture `risk-ceiling-migration.json`）；report 把它歸 mechanical override | **機械 risk ceiling**：migrations/auth/payment/secrets/CI 等 `risk_paths` 命中 → J5 一律 HUMAN，不看 Jev 分數；清單縮小受 P1-G6 監控 | migration fixture 一律 HUMAN；route_reason=`risk_ceiling_override` | S | P1-G3 |
| **P2-5** | 🛠，僅 live 後 | **隨機抽查**：AUTO live 後 10–20% 候選範圍（待 formal spec 核定）強制人工看，以維持 fresh labels | report 顯示抽查率與 labeled_fraction；抽查不能被 agent 關閉 | S | P2-2、P3-1 |
| **P2-6** | 🛠，僅 AUTO 後 | **次要回饋**：先讓人看 case 並獨立回答，再顯示 Jev route/risk，避免錨定；none 不算 agree | 作答前 UI/text 不含 Jev judgement；每週提醒頻率仍待正式產品決策 | S | P3-1 |
| **P2-7** | ✅ W5（2026-09-23）形狀：`ledger.audit_note`／`note` 子命令，封閉五欄 `{gate, questionset_hash_prefix, model_resolved, route_recommended, evaluation_id}`；白名單＋privacy negative 測試；貼進 PR／7-review 的動線留 P3-2 | **AUTO 可稽核附註**：PR/7-review 只允許封閉 metadata `{gate, questionset_hash prefix, model_resolved, route_recommended, ledger/evaluation id}`，不外露 raw packet/answers/probabilities | privacy negative fixture；附註不含敏感 evidence | S | P1-F4 |
| **P2-8** | ✅ W5 實驗（2026-09-23）：`j2-shadow` 讀 2-decision.md（方案表／Decision／Rejected／Rationale／Real-world／Owner Calls 人類答案）組厚包；order／phrasing 三 variants 同 case_id 只做 stability（不穩定→`unstable`、永不畢業）；`route_taken` 恆 HUMAN；window=50 只標待核定 | **J2 厚證據包**：方案比較全文、各方案取捨、Real-world Context/Open Questions 結論、Owner Calls 人類答案、fresh reviewer findings；正反論點；order perturbation/phrasing stability 只做 evaluation，不灌 n | 真 feature J2 packet 通過 self-check；不穩定就標 unstable、不得畢業；J2 未核定 rolling window 前永遠 shadow | M | P1-G1、P1-F1 |

### 4.1 J2 rolling window — 待核定候選

owner 已裁 **J2 保留**，但沒有核定 rolling-window 長度。draft-v4：

- 保留 draft-v3 的「J2 要有 Wilson floor」研究方向，不視為 live 核准。
- **候選 window = 50 個 unique、有效 labeled cases**，明確標為待核定設計值（W5：`policy.J2_WINDOW_CANDIDATE=50`、`J2_WINDOW_RATIFIED=False`，沒有旗標能改）。
- 20／30／50 的比較只能在 development set 做 sensitivity study；**不能拿 locked holdout 看完後挑最好數字**。
- window 未正式核定前，J2 永遠 shadow。
- J2 的 synthetic/rubric smoke 不可補 live/shadow graduation denominator。

## 5. P3 — 契約改動與遠期 AUTO

> **重要順序修正**：編號保留 P3-1/P3-2，但 live enable 的工程順序是 **先達成 P3-1 eligibility evidence → 完成 P3-2 契約同步／L2/ADR → 才允許 P3-1 AUTO live switch**。  
> 不得先把 `gates.J5: live` 打開，再補契約。

| ID | 狀態 | 做什麼 | 驗收／放行條件 | 量 | 依賴 |
|---|---|---|---|---|---|
| **P3-1** | 🧪 W6（2026-09-23）資格計算器已備、**live 未核准**：`report.eligibility`（§5.1 八條機械化、floor、first-overturn freeze、n 不歸零、無覆寫參數）+ `eligibility` 子命令；`gate.J5_LIVE_RATIFIED=False` 讓 `gates.J5: live` 只到 shadow（硬拒，非旗標）；`GRADUATED=False` 不動 | **J5 AUTO_SHIP candidate**：risk≤1、mechanical gate 全綠、author≠approver、Quiz gate/risk ceiling 不動。先只計算 eligibility；真正 live 開關受 P3-2 阻擋 | **Wilson 95% lower ≥ .85、n≥30 個 unique valid real Ship shadow cases**；source unverified 不算；同 evidence label；一次有效 overturn 立即 freeze；這是工程接受門檻，**不是錯誤率≤5%證明**。freeze 後仍按最新 unique cases 重算 Wilson，不人工覆寫通過 | L | P1/P2 必要項 + P3-2 before live |
| **P3-2** | 🛠 W6 部分（2026-09-23）：三模板頂欄加 `verdict_source`／`attested_by`；`gate-verdict-write.md` 鎖死 6（verdict 必附出處、Jev 不得寫）；`check-gate-verdict-write.sh` 25 項；`devflow_gate.py` 有 reviewer 時代填 human_attested、agent/Jev 拒收；新 `check-verdict-attestation.sh`。**缺口**：L2/ADR、README 公開面 parity、`_gate_consistency_impl.py` 不動（Jev 不是 reviewer）—— 見 w6 doc §3；**AUTO live 前仍必完成** | **契約同步**：reviewer-selection 5 處 + guide parity + `_gate_consistency_impl.py` ordered tuple + `notes/design/gate-verdict-write.md` 契約族 10 檔 + `check-gate-verdict-write.sh`；完整版「誰寫 verdict」機械檢查。需走 dev-flow 自己 Decide、L2/ADR | ADR accepted；`gate-consistency.sh`、`check-methodology-corrections.sh`、verdict-write checks 全綠；未授權 agent verdict 會紅。**完成前 P3-1 live 不可 enable** | L | P3-1 eligibility report、P1-G7 |
| **P3-3** | ⏸ 遠期；J2 保留 | **J2 AUTO_PASS**：排在 J5 後；P2-8 厚包 + formal rolling window + shadow evidence；Owner Calls 仍逐條人裁 | window 未核定 → no-go；正式 floor/window/source mix 必須進 formal spec，不沿用 dev-set 調參結果偷上線 | L | P2-8、P3-2 |
| **P3-4** | ✅ owner 已裁方向；🛠 可獨立 L2 | **Stage 3 polarity**：改成「人要求才 Demo」；動 `SKILL.md`、`_templates/3-prototype.md`、vnext shared contract、`_stage3_impl.py` 等實際契約面 | 只翻「預設要不要 Demo」；Demo verdict/attestation human-only 規則完全不動；可獨立排進 P1/P2 時窗，不等 J5 n≥30 | M | P0-3 |

### 5.1 J5 case eligibility

一筆 J5 case 要進 P3-1 denominator，至少同時滿足：

1. 來自真實 dev-flow Ship/G3 路徑，不是合成 routing／文件稽核／人工重播樣本。
2. `case_id` 是 unique semantic Ship decision；同 decision 的 retry、phrasing variants、remote reevaluation 不增加 n。
3. Jev evaluation 與 feedback 綁定同一 `feature + gate + artifact_hash + evidence_hash + HEAD`。
4. model_resolved、questionset/evaluation manifest group 一致；manifest 變版後舊 group 不延續。
5. reviewer provenance 可驗為已允許的 source class；`unverified` 排除。
6. `none` 排除，不當 agree。
7. `route_reason` 的 mechanical override（truncated/config_changed/risk_ceiling 等）與純 shadow route 分開報表，不偷混 denominator。
8. human 與 fresh-agent slice 分層；formal spec 必須核定 primary graduation source。v4 **候選建議** human 作 primary、fresh-agent companion，但尚未 owner 核定。

### 5.2 Freeze 語意

- 第一次有效 overturn → `circuit_breaker_state=frozen`，立即停止新 AUTO，回 HUMAN。
- freeze **不等於抹掉舊資料，也不等於 n 歸零**。
- model／evaluation manifest 改變本來就形成新 group；人工 `manual_regression` 是否重置另走 formal policy。
- 人工標「恢復」不能覆寫 Wilson。比如 30/30 通過後一筆 overturn 變 30/31，仍依公式重算；直到真實新樣本把下界重新拉回門檻才具 eligibility。
- `.85/30` 是接受風險政策，不是個別回答保證，也不是「錯誤率≤5%」證明。

## 6. P4 — 延後／不做

| 項目 | 結論 | 重啟條件 |
|---|---|---|
| **supermemory** | **不接** | 現有 `dev-memory.py ask` 已有可重現的檢索不足，**且**有真實跨專案共享需求，兩者同時成立才重開 0-draft |
| **J1–J3 observability 強耦合** | 先不把它當必要條件 | P0-5 lifecycle 與 P0-6 event roundtrip 先證實；需要時再調整 observability contract |
| **PostToolUse hook 強制 Jev** | 不做 | live 長期穩定，且 writer/schema/side-effect 邊界另審 |
| **第三方 Jev MCP** | 不採 | 有官方、可稽核且比 stdlib HTTP runtime 更合適的正式介面再評估 |
| **memory rerank / supermemory backend** | P4 optional，不進近期 MVP | 現有 query/retrieval 已多路召回；只有證實 retrieval 品質不足才做 optional rerank，而且 mandatory startup/current truth/invariants/NO_RELIABLE_MATCH 不得被 rerank 刪除 |
| **task routing / mixed 自動化** | 保留 research suite，不進 J1 MVP | mixed rubric（含 `.72` 反例）有人工 gold + locked holdout 後再議 |

## 7. 依賴圖

```text
research/jev-supermemory draft-v4
            │
            ▼
W0 Source closure
  P0-1..P0-10
            │
            ▼
W1 Guard foundation + P2-1 executable e2e
  P1-G1..G7 pure/schema/fake transport
  （此時仍沒有 production runtime）
            │
            ▼
W2 stdlib runtime + dual replay/ledger + manifest distribution
  P1-F1/F5/F6 + P0-8
            │
        ┌───┴────────────┐
        ▼                ▼
W3 J1 live          W3 J3 recommendation
P1-F2               P1-F3
        │                │
        └───────┬────────┘
                ▼
W4 J5 shadow
P1-F4/F7
same-evidence label + unique-case dedupe
                │
                ▼
W5 evaluation / J2 thick pack / J4 experiment
P2-2..P2-8
                │
                ▼
J5 eligibility:
Wilson lower >= .85
n >= 30 valid unique real Ship cases
                │
                ▼
L2 / ADR
                │
                ▼
P3-2 CONTRACT SYNC FIRST
                │
                ▼
W6 / P3-1 J5 AUTO live enable

旁路：
P0-3 ──▶ W7 / P3-4 Stage3 polarity（獨立 L2，可提前）
P2-8 ──▶ W7 / P3-3 J2 future track（window 未核定前 shadow）
```

## 8. Budget、deadline 與數值政策

### 8.1 Owner 已裁的數值

- J5：Wilson 95% lower ≥ **0.85** 且 **n≥30** valid unique real Ship cases。
- J5：第一次有效 overturn → freeze。

### 8.2 待核定候選工程值（未實作、不是 owner 裁決）

| 項目 | 候選值 | 限制 |
|---|---:|---|
| Daily Jev attempts | **500/day** | retry、variants、remote reevaluation 都算 |
| Daily input budget | **500k input tokens/day** | 與 attempts 取先到者停止 |
| J1 foreground total deadline | **2s** | 不做 foreground retry；失敗 no-op |
| J5 shadow HTTP wait | **0 前景等待** | 只是不等 HTTP；local enqueue 仍要實測，不宣稱 0ms |
| J2 rolling window | **50 unique labeled cases** | 待核定；未核定前 shadow |
| AUTO random audit | **10–20% 候選** | 只在 live 後，需 formal spec |

Budget accounting：

1. 每次 HTTP attempt 在發送前先 reserve 保守 input 上界。
2. server 回可靠 `usage.input_tokens` 才 reconcile。
3. timeout／斷線／未知 usage **不能當 0 用量退款**。
4. phrasing variants 與 retries 同樣扣 attempt/token budget。
5. daily cap 只控制成本／風險，不是模型 quality threshold。

## 9. 每階段完成定義與 Go/No-Go

| 工作包 | 完成定義 | No-Go |
|---|---|---|
| **W0** | P0-5 lifecycle、P0-6 fullroundtrip/index/multiwriter、P0-8 upgrade、P0-9 whitelist 有 source/probe 結論；API limit/Score 說法已修正 | 仍有會改資料模型或 runtime lifecycle 的未知 source |
| **W1** | P1-G1～G7 schema/pure/fake transport 全部負面測試通過；P2-1 executable e2e gate 完成 | 任一 guard 缺失；此時禁止寫真 API runtime |
| **W2** | stdlib runtime、dual durable/local replay、budget、manifest、ship distribution 全綠；stored-response replay deterministic | raw sensitive data 進 Git、replay 不可重現、manifest 升級漏發 |
| **W3** | ✅ 2026-09-23（`w3-j1-j3.md`）：J1 失敗等同現況、最多兩輪完整 dev-talk、N13 保留；J3 recommendation 不得寫 verdict | J1 找弱點維度不穩或 J3 能繞 human attestation |
| **W4** | J5 shadow 不阻塞 G3；same-evidence label binding、unique case dedupe 正確；一個真 feature 完整配對 | wrong HEAD/verdict 能誤標、variants 能灌 n、worker failure 影響 G3 |
| **W5** | report 可分 human/fresh/unverified、Wilson/dedupe 正確；J2/J4 仍 shadow | 用 synthetic/文件稽核充 graduation、holdout 被拿來調 window |
| **W6** | P3-1 eligibility 達標；L2/ADR accepted；**P3-2 先完整同步**；所有 mechanical/risk/Quiz/author≠approver 控制仍在 | 任一契約未同步、一次有效 overturn 後仍 AUTO、J5 floor 未達 |
| **W7** | Stage3 polarity 獨立 contract change 綠；J2 只在正式 window/source policy 核定後考慮 live | Demo attestation 被改成 agent/Jev；J2 window 未核定就 live |

## 10. P0-1／P0-2 已有 probe 記錄

### P0-1 API smoke

2026-09-22 外部實跑：HTTP 200、約 0.67s、`model=jev-1.13.0`、`usage=555 input / 84 output`。Noul 無 confidence；Choice／Score 有 distribution/confidence。此 smoke 只驗 protocol/shape，不驗 production quality。

### P0-2 context probe 與 source correction

既有單題壓測：

- `usage.input_tokens ≈ 32,593`：HTTP 200，約 1.4s。
- 約 `33,400`：HTTP 400 `max_tokens_exceeded`。

**正確解讀**：這個 probe 支持「state + 最長單題」在 32k 附近的限制；官方 models page 現行另明示整 request 64k。不得再寫「32,768 含所有 questions 是全局上限」。

Packet builder 必須同時驗：

```text
state + all questions <= 64k
state + longest single question <= 32k
```

正式程式應保留 headroom，不以剛好卡 64k/32k 為正常營運目標；實際 reserve/headroom 值屬待核定工程參數。

## 11. J1 atomic clarity 題組方向

J1 的目的只有：**省掉討論後又問一次「夠清楚嗎」**。不是 task router。

至少拆：

- `goal_clear`（Noul）：主要想達成的 outcome 是否清楚？
- `scope_clear`（Noul）：本次改動邊界是否足以進 Decide？
- `acceptance_clear`（Noul）：是否有足夠可驗收條件，或能在後續 spec 明確化？
- `owner_call_pending`（Noul）：是否存在必須由 owner 做的價值／產品選擇？
- `ambiguity`（Score）：使用 ordered levels 描述可執行歧義程度。
- `next`（Choice）：`START_DECIDE | ASK_MORE | NEEDS_OWNER_DECISION`。

policy 不把多題風險機率相乘成「總風險」。atomic signals 各自進 deterministic routing rule。

ASK_MORE：

1. 由 clarity atomic signals 找最弱維度，不從 `next` distribution 逆推。
2. 產生一個不抄 rubric 原文的人話主題。
3. 開完整 dev-talk 11 步，N13 仍需人點頭。
4. 最多兩輪；超過轉 `NEEDS_OWNER_DECISION`。
5. TypeSafe failure/no-op → 現有 dev-flow 流程。

## 12. J3、J5、J2 的權限邊界

### J3

J3 只回答「人親手 Demo 是否值得」，是 recommendation：

```text
Jev says demo_worth_it
        ↓
顯示建議
        ↓
人是否要求 Demo
        ↓
若 Demo，verdict/attestation 仍 human-only
```

J3 **不是 G2 AUTO_PASS**。

### J5 shadow

J5 只讀已產生的 evidence，不產 evidence：

```text
Final Fresh Run
+ executable e2e
+ Gauntlet
+ coverage/reviewer evidence
        ↓
J5 shadow enqueue
        ├─ 現有 G3 立即照常走
        └─ background evaluation → replay/local → durable metadata
```

### J2

J2 保留但排後：

```text
P2-8 thick evidence
  ↓
order/phrasing study
  ↓
shadow
  ↓
正式 rolling-window/source policy
  ↓
未來 P3-3
```

Owner Calls 永遠仍由人逐條裁決；J2 不得替 owner 回答。

## 13. Security / privacy / injection 邊界

1. **Jev 不得讀 secret、credential、原始醫療資料或不必要全文。**
2. durable Git events 只存 metadata/hash/結構化指標，不存 raw packet。
3. local replay store 必須 gitignored；仍需 sanitized，不能因「不進 Git」就無限制收 PHI/secret。
4. `primary_request`、`quoted_context`、`source_facts` 分欄；quoted content 預設資料，不是 instruction。
5. 中性措辭／等長／grep/self-check 是形式控制，不是 prompt injection proof。
6. mixed `.72` 反例固定留在 negative/adaptation suite，直到人工 gold/holdout 證明 rubric 改善；不得為了提高「文件明示稽核」分數反覆改文案。
7. 不把不同 atomic risk probabilities 相乘；除非未來另有經驗證的統計模型與 formal spec。

## 14. Supermemory

結論維持 **P4 deferred**。

目前 dev-flow 已有：

- `.dev-flow/decisions`、knowledge/invariants/intents、implementation truth、events、skills 等 typed durable memory；
- local SQLite/embedding/retrieval metrics；
- `memory/agentmem/context.py` 七段 startup context；
- `query.py`／`retrieval.py` 多路召回；
- `NO_RELIABLE_MATCH` 與 current-truth/invariant 等保護。

所以近期不能把 memory 畫成「embedding → topK → Jev」白紙流程。若未來做 Jev rerank，也只能放在既有 retrieval **之後**，且 mandatory startup/current truth/invariants/conflicts/authoritative exact hits 不得被 rerank 移除。

supermemory 重啟條件：

```text
dev-memory.py ask 已被真實 eval 證明檢索不足
AND
存在跨專案共享記憶的真需求
```

只有兩者同時成立才開新 0-draft。

## 15. 實作前剩餘 source 驗證

在 W1/W2 之前仍需完成（**P0-5／P0-6／P0-8／P0-9 已於 2026-09-22 W0 收閘，證據與結論在 `w0-source-closure.md` 與 `evidence/w0/`；下列 1–4 保留原文供對照**）：

1. **P0-5**：真 Stage6→Stage7 / bare Stage7 lifecycle；確認 run_id/exec state/stop 的實際生命週期。
2. **P0-6**：`append_events()` custom Jev metadata 的 durable → sync/index → read/report roundtrip；測同 session multiwriter 是否可能 lost update。若 custom metadata 在 sync.py 被丟棄，要決定是擴 schema/index 還是 durable event 只留 canonical payload。
3. **P0-8**：既有專案 `dev-setup` upgrade 對新增 ship-manifest items 的實際同步。
4. **P0-9**：dev-talk 舊 discussion path 在 read whitelist 的實際定義。
5. **P1-F7 source audit** → ✅ W4 2026-09-23 已做（`w4-j5-shadow.md` §3）：結論是 repo 內**沒有任何 hook 擋 git commit/push/merge/tag**，這些步驟靠散文、Exit Checklist 與使用者本機 `permissions.deny`；`_dispatch_impl.py` 只算 fail-open tier discipline guard，不能拿來補不存在的權限保證。

## 16. 遠期 AUTO 的正式驗收

J5 AUTO live 之前，以下全部同時成立才 Go：

- [ ] 真實 J5 shadow unique valid Ship cases `n >= 30`
- [ ] Wilson 95% lower `>= .85`
- [ ] 沒有未解除的有效 overturn freeze
- [ ] 同 evidence/artifact/HEAD label binding 全部可機械驗
- [ ] retry／variants／remote reevaluation 不會灌 n
- [ ] `human_attested`／`fresh_agent`／`unverified` 分層報表完成，primary source 已在 formal spec 核定
- [ ] evaluation manifest 改版會自動形成新 group
- [ ] P2-1 executable e2e 已是 J5 packet 的固定前置
- [ ] P2-4 risk ceiling 生效
- [ ] mechanical gate 不被 Jev 取代
- [ ] author≠approver 不被 Jev 取代
- [ ] Quiz gate／不可逆操作的人類控制不變
- [ ] L2/ADR accepted
- [ ] **P3-2 contract sync 先完整完成並全綠**
- [ ] 每專案雙閘門 opt-in 存在
- [ ] privacy/replay/budget/breaker tests 全綠

`.85/30` 只代表本專案選擇的工程接受門檻；不應在 README、report 或 UI 中翻譯成「95% 準確」、「≤5% 錯誤率」或其他未被統計設計證明的敘述。

## 17. 本階段明確不做的事

- 不修改 `main` runtime。
- 不開 J5 AUTO。
- 不讓 J3 寫 G2 verdict。
- 不讓 Jev 取代 Mechanical Gate。
- 不把 task routing 當唯一或必要 MVP。
- 不宣稱 mixed rubric 已解。
- 不把 synthetic smoke／roadmap audit 轉成 J5 標籤。
- 不把格式 attestation 宣稱成身份 authentication。
- 不把 guard pure functions／fake transport 宣稱成 completed product。
- 不接 supermemory。
- 不把 raw Jev packets、醫療資料或 logs 直接寫進 Git durable memory。

## 18. 外部交付待歸檔附錄

以下證據來自本次對話中 Codex 的外部執行結果，**目前不宣稱已存在於 repository evidence 路徑**。正式歸檔前應先決定 privacy、命名與是否值得保留：

- TypeSafe `/v1/models` 與 `/v1/systemone` smoke responses。
- 第一批 12 routing smoke cases。
- 第二批 6 rubric/reference isolation cases；包含 `feature-with-supporting-work` mixed `.72` 反例。
- roadmap draft-v3 九題「原文明示」稽核。
- 本地整合稿十二題「原文明示」稽核。
- context 單題 32k 附近 probe。
- `append_events(kind=jev)` custom metadata + duplicate event_id idempotency 小 probe。
- Stage7 `_exec_impl.py` source lines 的靜態核對。

這些材料的功能是幫 source closure 與 rubric adaptation；除非未來另有人工 gold／locked holdout 或真實 Ship provenance，否則不能被升格為 production calibration evidence。
