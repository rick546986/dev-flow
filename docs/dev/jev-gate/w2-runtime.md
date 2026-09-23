---
title: jev-gate W2 — stdlib runtime / replay / manifest 分發
slug: jev-gate
status: W2 完成（shadow／no-op runtime；無 hook 接線、無 AUTO）
date: 2026-09-23
base: research/jev-supermemory baff8d3（W0/W1 squash）→ 本 PR 分支 claude/w0-source-closure-3aslgp
---

# W2 stdlib runtime / replay / manifest 分發

> roadmap §1 W2 = P1-F1、P1-F5、P1-F6、P0-8（C1）。開工前提（owner 2026-09-23）：① A1–A7／B1–B5 已裁「照建議／A B 過」
> （`owner-decisions-pending.md` §0）；② 本 PR **明改** `scripts/test-devflow-jev.sh` 兩條 W1 tripwire。硬約束：仍無正式 AUTO、
> 雙閘門、七守衛行為不得鬆。**這不是 production runtime**：沒有任何 hook 呼叫它（W3／W4），J5 只 shadow，`GRADUATED = False` 寫死。

## 0. 分支與 SHA

| 項 | 值 |
|---|---|
| W0/W1 squash 進 `research/jev-supermemory` | `baff8d3`（tree 與 pre-squash tip `97418a5` 相同；14 commits `e3d29e0..97418a5` 已列在 commit message） |
| W2 開發分支 | `claude/w0-source-closure-3aslgp`（reset 到 `baff8d3` 後續寫；W2 commit SHA 見回報／PR） |
| main | **未動** |

## 1. P1-F1 stdlib runtime

**做了什麼**

- `scripts/devflow-jev.py`（Python 3.9+，只用 stdlib；`scripts/check-py-floor.sh` 已掃）。子命令：

| 子命令 | 做什麼 | 網路 | 寫入 |
|---|---|---|---|
| `status` | 各 gate 生效等級（key 有無 × `.dev-flow/jev.yaml`）、`questionset_hash`、六欄版本、今日 budget、breaker、replay 數、memory lib 位置 | 無 | 無 |
| `pack` | JSON 輸入 → `packet.build_packet` + `self_check`；privacy 命中 = 拒絕（exit 2） | 無 | `--out` packet JSON |
| `ask` | 雙閘門 → 組 request → 一次 `policy.evaluate` → `route_j5/j1/j3` → `route_taken(graduated=False)` → `build_evaluation` + `stamp` → replay store（ok 才有 raw）→ durable | shadow/live 一次 | `.devflow/jev/replay/`、`.devflow/jev/state/`、`.dev-flow/events/…`（經 `agentmem.durable.append_events`） |
| `replay` | stored-response deterministic replay + `verify_evaluation` + `questionset_hash` 重算；對不上 exit 1 | 無 | 無 |
| `reevaluate` | `ReplayStore.reevaluate`：同 sanitized packet/questions 再送；新 `evaluation_id`、`parent_evaluation_id`、同 `case_id`；扣 budget／受 breaker | 一次 | replay + durable |
| `feedback` | agree／overturn label；`provenance.feedback_suspect` 判可疑；`ledger.build_feedback_record`（新增）落 durable；可疑一律留痕但 `counts_toward_n=false` | 無 | durable |
| `report` | replay store 的 evaluation + durable 的 feedback → `report.graduation`（分層、Wilson、任一 overturn 凍結）；`not_replayable` 的 evaluation 只列出不算 | 無 | 無 |

- `scripts/devflow_jev/http_transport.py`：**套件唯一**准 import `urllib`／`socket` 的檔。POST 一次、收 raw JSON、任何失敗 → `TransportError(kind)`（400/401/422/429/529 各自、其它狀態碼歸 `network`、timeout、`malformed_json`）。無 retry。endpoint 用 `urllib.parse.urlsplit` 拆（不手拆；`#@localhost`／`?x=@localhost`／userinfo 一律拒），只准 https（loopback http 僅測試，`DEVFLOW_JEV_ENDPOINT`）；loopback endpoint 一律繞過環境 proxy（否則 `http_proxy` 在、`no_proxy` 不在時「閉埠零網路」會把 key 送去 proxy）。socket timeout = policy deadline（J1 2s，不會在線上卡 30s）。key 只住物件內：`__repr__` 不印、錯誤 detail 只帶狀態碼不帶 body。
- `scripts/devflow_jev/state.py`：P1-F5 落盤（§2）。
- `scripts/devflow_jev/ledger.py`：新增 `build_feedback_record`、`FEEDBACK_ALLOWED_KEYS`、`FEEDBACK_VERDICTS`；`assert_durable_safe` 對 `record_type=feedback` 用 feedback 白名單，evaluation record 白名單**不變**。
- `scripts/devflow_jev/policy.py::route_taken`：J1／J3 在 live 時把 `next`／`recommendation` 原樣交回流程（`("HUMAN","noop_fallback_to_current_flow")` 給 None）；**J5 分支一字未改**（shadow → HUMAN；未畢業 → HUMAN）。`policy_fingerprint()` 只涵蓋常數，未變 → `questionset_hash` 未變。
- 雙閘門在 runtime 的落點：`run_ask` **第一步**就 `gate.effective_level`；`off` → 回 `noop/no_api_key|no_project_optin|min(...)=off`，**不驗輸入、不建 transport、不讀 questions、不寫任何檔**（`transport_factory` 在測試中是「呼叫即 AssertionError」）。`http_transport` 是延遲 import，off 路徑連 urllib 都不載入。
- shadow/live 路徑的順序（審查後定案）：gate → `validate_evidence`（sha256 小寫 hex、head_sha 7–40 hex、slug 無空白）→ `validate_packet`（schema／gate 對得上、**重算 `packet_hash`**、`privacy_scan` 零命中、`self_check` 全過、header 的 slug/head_sha/artifact_hash/evidence_hash 與 evidence 同值）→ **先解析 memory/agentmem**（缺 → exit 2，此時尚未送出、未寫任何檔）→ deadline（argv 只能收緊）→ state → transport → 送一次 → state 落盤 → replay → durable。
- 無 AUTO 的三道：`GRADUATED = False` 模組常數（測試釘只出現一次、沒有 `--graduated`）；`policy.route_taken(..., graduated=GRADUATED)`；`_taken()` 在 `route_taken == "AUTO"` 時 raise 拒寫（測試用 monkeypatch 偽造 policy 驗證 tripwire 會咬）。
- `run_id` 來自 `.devflow/exec.json`，只進 provenance；同 slug 不同 run_id 的 `case_id` 相同（P0-5 結論）。

**tripwire 明改**（owner 前提 ②）—— `scripts/test-devflow-jev.sh`：

| W1 原文 | W2 改為 |
|---|---|
| ① 套件內不得 import 任何網路模組 | ① 網路 import **白名單只有** `http_transport.py`；其餘模組與 `scripts/devflow-jev.py` 本身零網路 import（`test_*.py` 不掃；測試只打假 opener 與 loopback 閉埠） |
| ② repo 內不得存在 `scripts/devflow-jev.py` | ② runtime **必須存在、可執行、`GRADUATED = False`**；並實跑：未設 key 的 `ask` → exit 0、`no_api_key`、`.devflow/`／`.dev-flow/` 都沒被建 |
| — | ⑤ 新增：key + opt-in 但 endpoint 是 `http://127.0.0.1:9/` → exit 0、`transport:network|timeout`、`route_taken=HUMAN`、key 不出現在輸出 |
| ③ 地板 127（只算 `test_guards.py`） | ③ 地板 168（三份 `test_*.py` 合計）**且** `test_guards.py` 仍 ≥ 127 |

`test_guards.py::W1Boundary` 同步明改：`test_no_network_modules_imported` → `test_network_modules_only_in_http_transport`；`test_no_runtime_script_exists_yet` → `test_runtime_script_exists_and_is_network_free_itself`。案數不變（127），其餘 125 案一字未動。

**結論**

- P1-F1 驗收（roadmap `:124`）：「未設 key/opt-in exit 0 且零網路」✅（tripwire ②、`test_runtime.DualGateOffPath` 5 案）；「0.36 AUTO argmax fixture 不得導出 AUTO」✅（`J5ShadowAndNoAuto.test_argmax_036_fixture_never_auto`：`route_recommended=HUMAN`、`route_taken=HUMAN/shadow_mode`）；「`methodology/test-devflow-jev` 在 all 中實際 PASS」✅（見 §5）。
- **沒有對真 API 送過任何請求**：本容器沒有 `TYPESAFE_API_KEY`；所有 HTTP 路徑由假 opener 與 loopback 閉埠覆蓋。真 API smoke 留給 owner 持 key 的機器（`status` → 建 `.dev-flow/jev.yaml` → `ask`），不在 W2 宣稱。
- durable 寫入需要 `memory/agentmem`：runtime 依序找 `<root>/memory` → `$DEVFLOW_MEMORY_LIB` → `$DEVFLOW_ROOT/memory` → 本檔上一層 `memory/`；找不到 → **送出前** exit 2 fail-loud（不扣 budget、不寫 replay）。採用專案照 dev-setup 慣例有 `DEVFLOW_ROOT`；`memory/agentmem` 不在 ship-manifest 內，是 runtime 期的相依，不只 setup 期。

**證據路徑**：`scripts/devflow-jev.py`、`scripts/devflow_jev/{http_transport,state,test_runtime,test_http_transport}.py`、`scripts/test-devflow-jev.sh`、`scripts/devflow_jev/test_guards.py:1175-1200`（W1Boundary）。

## 2. P1-F5 budget / breaker 落盤

- `state.StateStore`：`budget-<UTC day>.json`（`attempts`、`tokens_committed`＝settled+reserved 合計，跨 process 累計，**unknown usage 的保留額不退款**）、`breaker.json`（per gate 連續失敗數）。tmp + `os.replace`。
- `policy.Budget`／`Breaker` 本體未改（候選值 A2／A6 未校準，已落檔）。
- 測試：`FailureNoopAndState`（transport 失敗 no-op 仍留 durable；breaker 三連敗跨 process 後第四次 `breaker_open`；unknown usage 後 `input_tokens` 剩額下降不回升；`budget_exhausted`；J1 超 `J1_DEADLINE_S` → `deadline_exceeded` no-op）。
- 誠實邊界：同機兩個 process 同時寫 state 檔可能 lost update；方向是「多花一次」，不會放行 AUTO；帳本正本是 durable 的 `usage` 欄。

## 3. P1-F6 對抗 fixtures

W1 已落地 `scripts/fixtures/devflow-jev/`（exit_code/tail 衝突、quoted「ignore rules」、reference governance、mixed .72、0.36 argmax、Score level≠index、opt-in 矩陣、wrong-head label），全部由 `test-devflow-jev.sh` 帶起；W2 加 runtime 層實跑 0.36 fixture；對抗審查一輪（§6）。結果只證明 deterministic header／policy 不被繞過，**不宣稱抗 injection**（roadmap §13.5）。

## 4. P0-8 → C1：manifest 版本 + doctor 逐列

**做了什麼**

- `docs/dev/ship-manifest.json`：新增 `version`＝列內容（source/destination/mode）canonical JSON 的 sha256 前 16 hex，前綴 `v1-`（`devflow_ship_manifest.compute_version`；`--version` 子命令）。**不是人手 bump 的標籤**：任何列增刪改，值必變。
- 新增 15 列：`scripts/devflow-jev.py → docs/dev/tools/devflow-jev.py 755`；`scripts/devflow_jev/{__init__,attestation,gate,http_transport,ledger,manifest,packet,policy,provenance,report,state,transport}.py` 與 `jev-questions.json` → `docs/dev/tools/devflow_jev/… 644`；`docs/dev/ship-manifest.json` 自身（source == destination 第三類列）。共 24 列。`test_*.py` 不散發。
- `devflow-contract.json`（正本 + `docs/dev/` 副本）：頂層 `ship_manifest_version` 同值。契約版號 2.1.0 **不 bump**（additive 欄；舊 runtime 的 doctor 不認識就略過）。
- `scripts/check-ship-manifest.sh` ⑥：`version_failures`（manifest.version 與重算一致、兩份契約同值）+ 負向 fixture 三案（加列沒重算 → 紅；副本契約漂移 → 紅；基線綠）。`schema_problems` 新增：缺 `version`／頂層未知鍵 → 紅。parity 反向改走整棵 `tools/`（含子目錄）比對 destination 相對路徑。MIN_CHECKS 21→26。
- `hooks/_doctor_impl.py` 6e：契約無 `ship_manifest_version` → info「逐列驗證略過」不擋（舊契約）；有 → 讀採用樹 `docs/dev/ship-manifest.json`，缺檔 fail-closed；三值（契約／manifest 自稱／依列重算）不一致 fail-closed；逐列 destination 存在（絕對／`..`／反斜線一律不合法）、posix 上 `755` 缺可執行位元 fail-closed、`644` 多了 x 位元只 info（FAT/DrvFs 常態）、Windows 只驗存在。演算法在 hooks 內複製一份（hooks 不 import scripts），兩邊同值由 selftest p3「三值一致」案釘（doctor 端用正本 `--version` 算值餵 doctor）。
- `hooks/selftest.sh` p3 +7 案（462→**469**；含 destination `..` 穿越必紅）；`skills/dev-setup/SKILL.md` upgrade 段補「本地缺、baseline 缺 = 母版新增，直接散發且必列摘要；manifest 自身是散發列；doctor 不一致不得手改 version 轉綠」（`check-dev-setup-discipline.sh` 38/38 仍綠）。

**結論**：P0-8 的兩個要求（manifest-version 檢查 + 明列人工 upgrade）都落地；採用側從「零牙」變成「契約升級後 doctor 逐列 fail-closed」。既有採用專案在跑 `dev-setup upgrade` 前契約無此欄 → doctor 明示略過，不假綠、不誤紅。

**證據路徑**：`scripts/devflow_ship_manifest.py`（`compute_version`／`version_failures`）、`scripts/check-ship-manifest.sh`、`hooks/_doctor_impl.py`（`_ship_manifest_version`、6e）、`hooks/selftest.sh`（p3 ship-manifest 六案）、`docs/dev/ship-manifest.json`、`devflow-contract.json`。

## 5. 驗證

| 套件 | 結果 |
|---|---|
| `scripts/test-devflow-jev.sh` | ①②⑤③④ 全過；unittest 180/180（guards 127 + runtime 44 + http_transport 9）；⑤ 的 packet 走真 `pack`、子程序清 proxy 環境 |
| `scripts/check-ship-manifest.sh` | 26/26（含反向掃 tools/ 子目錄負向） |
| `scripts/check-file-map.sh` | forward 231 + reverse 233 全過（226→231：runtime、http_transport、state、test_runtime、test_http_transport） |
| `scripts/test-architecture-guards.sh` | 146/146（靜態釘：selftest 469、ship-manifest 26、file-map 231、heredoc 229） |
| `hooks/selftest.sh` | 456/469；13 紅 = 乾淨 base 同集的 11 條環境紅（doctor printer-python 3.11、f4 root 唯讀）+ 本輪兩條**正向** doctor 案（同一 printer-python 原因讓 rc=1；輸出文字「✓ ship-manifest: 版本 v1-…」與「逐列驗證略過」都實際出現，五條負向案全綠） |
| `check-py-floor` / `check-version-sync` / `test-spec-gate-e2e` / `test-evidence-gauntlet` / `check-dev-setup-discipline` | 綠（py-floor 只驗到 3.11） |

## 6. 對抗審查（2026-09-23，4 維度 → 22 raw → 14 confirmed／0 refuted／8 未驗）

Workflow：runtime-bypass／transport-privacy／c1-doctor-manifest／docs-accuracy 四個 reviewer，每條 finding 一個獨立 refuter（預設 refuted）。14 條 confirmed 全部修掉並補測：

| # | 發現 | 修法 |
|---|---|---|
| 1 | `ask` 對 pack 之後被改的 packet（塞 secret、hash 留舊、gate/header 對不上）照送 | `validate_packet`：schema/gate、重算 `packet_hash`、privacy、self_check、header↔evidence 同值，全在建 transport 前 |
| 2／14 | memory lib 在送出、扣 budget、寫 replay 之後才解析 → 缺 lib 的採用樹留孤兒 replay | 送出前 `_require_memory_dir` |
| 3 | evidence 大小寫／尾空白／非 hex 讓同一 case 裂成多個 `case_id` | 嚴格 regex（小寫 hex、head 7–40、slug 無空白） |
| 4 | `--deadline 999` 放寬 G2 的 J1 2s | `_deadline` = min(policy, argv) |
| 5 | J1 線上等 30s 才量 deadline | transport `timeout_s` = deadline |
| 6 | `report` 一個 evaluation 只留一票，跨層互蓋、可疑 overturn 蓋掉有效 agree | 依 (層, evaluation) 分桶、落盤已標 suspect 先剔除、每層各跑一次 graduation |
| 7 | 壞形狀 packet 走 KeyError → exit 1 撞 replay 不一致碼 | 先驗形狀；main 收 KeyError/TypeError → exit 2 |
| 8 | `validate_endpoint` 手拆 host，`http://192.0.2.1#@localhost` 過 | 改 `urllib.parse.urlsplit`、拒 userinfo；測試加壞例 |
| 9 | loopback「零網路」測試在 `http_proxy` 在、`no_proxy` 不在時把 key 送去 proxy | loopback endpoint 用 `ProxyHandler({})`；tripwire ⑤ 子程序清 proxy 環境 |
| 10 | tripwire ① regex 漏 `import os, socket`／`__import__("socket")` | 三處 regex 同步擴（逗號串、`__import__`/`import_module`） |
| 11 | `state._atomic_write` 共用 `.tmp` 名，同日兩個 ask 可撞出壞 JSON | mkstemp 每 writer 自己的 tmp |
| 12 | doctor 6e 在 Windows 上每條 755 列都紅 | `os.name=="nt"` 只驗存在；644 多 x 位元降為 info；destination 穿越判不合法 |
| 13 | parity 反向只掃 `tools/` 頂層，`devflow_jev/` 子目錄裡沒記帳的檔綠 | `os.walk` 比對 destination 相對路徑；負向 fixture +1 |

未驗的 8 條（低嚴重）也順手處理：`compute_version` docstring 改指 selftest p3 為同步牙；SKILL.md 補 `mkdir -p "$(dirname <destination>)"`；本檔的 roadmap 行號、memory lib 時序、validate 順序、endpoint 說法已改正。filemap basename 正規化保留（check-file-map 的 reverse 對路徑 token 查 isfile，兩支守衛各管一維）。

## 7. 明確沒做（W3 以後）

- 沒有任何 hook 呼叫 runtime（J1 dev-talk 接線 = W3 P1-F2；J5 evidence-bound pairing 與 shadow worker = W4 P1-F4）。`policy.ShadowQueue` 仍只是量測用。
- 沒對真 TypeSafe API 送過請求；沒建任何專案的 `.dev-flow/jev.yaml`。
- 沒動 G1/G2/G3 模板（P3-2）、`skills/dev-flow`、`skills/dev-talk`、`hooks.json`。
- C2（dev-talk Read matcher）另排。
- 沒進 main。
