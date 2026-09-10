---
feature: dogfood-ping
stage: 4-spec
status: approved
verdict: PASS
owner: rick-dev-flow
reviewers: [user]
updated: 2026-09-10
baseline: tip 0a89ec8
contract: 2.0.0
---

# 4. 規格 — dogfood-ping（極小 CLI）

> Change spec（delta）。G1 鎖定：A + 跑 Stage 3 + Example。正式腳本 Stage 6 才落地；本檔只釘可測契約。
> **G2 PASS**（owner 2026-09-10 chat）。契約維持 `2.0.0`。

## ADDED Requirements

### R-1: 系統 SHALL 在 `scripts/dogfood-ping.sh` 提供一支以 bash 可執行的單檔腳本
#### S-1
- GIVEN repo 工作樹已含本 feat Stage 6 落地後的 `scripts/dogfood-ping.sh`（檔案存在且具可執行位）
- WHEN 在 CI、macOS 或 Linux 上以 `bash scripts/dogfood-ping.sh` 或直接 `./scripts/dogfood-ping.sh` 呼叫（PATH 含系統 bash）
- THEN 行程啟動成功（非「檔案不存在／permission denied」）；shebang 為 `#!/usr/bin/env bash` 或等價可攜形式，不依賴非 POSIX 延伸作為唯一執行路徑
- 觀測:從檔案系統與行程啟動看 | 檔存在、`test -x` 為真、行程能啟動且 shebang 首行符合上列算對 | 在乾淨 clone 對該路徑執行 `head -n1` 與 `bash scripts/dogfood-ping.sh` 測
- Operational Context:不適用 — 純腳本存在性／可攜啟動，無人員交接或權限分流。

### R-2: 執行 `scripts/dogfood-ping.sh` 時 stdout SHALL 恰好為位元組序列 `dogfood-ok\n`
#### S-2
- GIVEN `scripts/dogfood-ping.sh` 已依 R-1 可執行
- WHEN 執行該腳本並擷取 stdout（不併 stderr）
- THEN stdout 位元組恰好為 `dogfood-ok` + 單一換行（`\n`／LF）；無前綴、無後綴空白、無第二行、無 CRLF
- 觀測:從 stdout 原始位元組看 | 與 `printf 'dogfood-ok\n'` 輸出逐位元組相同算對 | 跑 `scripts/dogfood-ping.sh | cmp -n - <(printf 'dogfood-ok\n')`（或等價）測
- Operational Context:不適用 — 純輸出契約，無人員決策。

### R-3: 執行 `scripts/dogfood-ping.sh` 時 process exit code SHALL 為 `0`
#### S-3
- GIVEN 同 S-2 的執行
- WHEN 行程結束
- THEN exit code 為整數 `0`
- 觀測:從 shell `$?`（或 CI 等價）看 | 值為 `0` 算對 | 與 S-2 同一趟執行一併讀 exit code 測
- Operational Context:不適用 — 純 exit 契約。

### R-4: 新增該腳本時 SHALL 同步 file-map／相關地板，使 `scripts/check-file-map.sh`（或等價）綠
#### S-4
- GIVEN Stage 6 已把 `scripts/dogfood-ping.sh` 寫入工作樹，且 file-map／`EXPECTED_MAPPED_FILES`（或等價清單）已按本包慣例更新
- WHEN 在 repo 根執行 `scripts/check-file-map.sh`（或本包文件指名的等價地板檢查）
- THEN 該檢查 exit `0`（不因漏登本腳本而紅）
- 觀測:從該檢查的 exit code 與 stderr 看 | exit `0` 且無「未映射／計數不符」類失敗算對 | 在含本腳本與已更新 file-map 的工作樹上跑該檢查測
- Operational Context:不適用 — 地板機械檢查，無人員交接。

## MODIFIED Requirements
（無 —— 不改既有產品行為）

## REMOVED Requirements
（無）

## 行為流程圖
```
[R-1] 提供可執行腳本
  路徑 scripts/dogfood-ping.sh -> shebang(env bash) -> 可啟動

[R-2] 固定 stdout
  執行腳本 -> stdout 恰好 dogfood-ok\n

[R-3] 成功結束
  執行腳本 -> exit 0

[R-4] 地板同步
  新增腳本 + 更新 file-map -> check-file-map.sh exit 0
```

## 補助模組生命週期（預覽）
- 新生（這輪）：`scripts/dogfood-ping.sh`（單檔 CLI；Stage 6 落地，本站只定契約）
- 改行為：沒有
- 退役：沒有
- 不動：既有 hooks／host-stack-fit 正本／Stage 產器；file-map **檢查邏輯**本體（只加映射列／計數，不改檢查算法）

主詞是本 feat 的 dogfood-ping CLI。關聯收成一格，不拆檔名。

## Acceptance Criteria
- S-1～S-4 對應測試／檢查全綠。
- 行為不變類不適用（本 feat 為新增腳本，無 golden-master 既有輸出可比）。
- 非功能：CI／macOS／Linux 只要有 bash，皆能依 R-1～R-3 觀測欄重現。

## Out of Scope
- HTTP 服務、網頁 UI、npm／Node 工具鏈。
- 修復 `#165`（Stage2 審頁「方案依據」超寬表）—— 另票。
- 改動 `host-stack-fit`／`#163` 正本、假 PreToolUse、升契約／bump plugin。
- 生產業務邏輯、另開 scratch repo、只交 docs 不交腳本。
- Stage 5 模板欄固化（#159）；本輪若寫 Intent 白話另見任務站，不進本 delta。

## Diff Budget
- 非測試：`scripts/dogfood-ping.sh` 1 檔 / ≤20 行；file-map／相關地板列 1～2 檔 / ≤30 行。[Assumption]
- 測試：可為 1 個 shell／自測條或掛既有 selftest 入口 / ≤80 行。[Assumption]
- 文件：本 feat 過程檔與（合 main 後）`example/dogfood-ping` 樣張；不計入實作 Diff 硬頂，但 Stage 6／7 須能指到。
- 超支 → 停判 L1／L2；分不清當 L2。

## Dependencies
- 系統 bash（CI／mac／linux）；不新增第三方套件。
- 本包既有 `scripts/check-file-map.sh`（或等價）地板 —— 不另造檢查家族（對齊 Decision OC-3）。

## Design Boundary Contract(條件式;G2 一併審)

- Applicability: n-a — 單檔本機 shell；不跨模組／不新增公開 API／無 schema／無 queue／無外部服務／無新 network·filesystem·subprocess·credential capability（腳本本身即被呼叫的 subprocess 產物，不對外開 capability）／Feature Risk = normal／無狀態機。觸發條件①–⑪皆未命中。
- Trigger(s): —
- Design source: Decision A（`2-decision.md`）；Stage 3 throwaway CLI 已證實輸出形狀。

## Verification Profile(G2 一併審)
- lane: fast
- Risk: normal
- Verify: 執行 `scripts/dogfood-ping.sh`；斷言 stdout 位元組 = `dogfood-ok\n` 且 exit 0；再跑 `scripts/check-file-map.sh`（或等價）exit 0
- Negative Constraints: 不得改 host-stack-fit／#163 正本；不得引入 HTTP／npm；不得在本 PR 修 #165；不得手填假 PreToolUse；不得把正式腳本提早塞進 Stage 4／5（正式碼 Stage 6）
- Advanced verification excluded: mutation／race／load／security scan
- Exclusion reason: 單檔 print＋exit，無併發、無 I/O 契約面、無 auth；重驗證層無對應 failure surface
- Reliability triage:
  - Concurrency: n-a — 無共享狀態、無平行寫入；單行程印字即結束
  - Idempotency: n-a — 重複執行只重複印同一行，無寫入／無副作用累積；不另立冪等鍵
  - Timeout/retry: n-a — 同步瞬間結束；無網路／無等待；不定義重試
- lane 判準: Risk normal、無 schema／權限／金流／對外 API／新 capability → **fast**（與判準一致，無偏離）

## Drafting Decisions(草擬自判,待人審)

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | shebang 固定 `#!/usr/bin/env bash`（不用寫死 `/bin/bash`） | CI／mac／linux bash 路徑不一致；`env` 較可攜 | `2-decision.md` OC-3 路徑鎖在 `scripts/`；可攜 `[Assumption]` | S-1 觀測改認絕對路徑 shebang；部分環境可能找不到 bash | ✅ |
| DD-2 | 換行政策 = 單一 LF；實作用 `printf '%s\n' 'dogfood-ok'`（或位元組等價），不用依賴 echo 的實作差異 | 要與 `dogfood-ok\n` 位元組契約一致；echo 在不同 shell 可能加旗標或吃跳脫 | Stage 3 Result 實跑；POSIX printf 行為 `[Assumption]` | S-2 改允許 CRLF 或無換行；觀測指令跟著改 | ✅ |

### 內部技術選擇(下層,告知即可)
- 正式檔名／路徑：`scripts/dogfood-ping.sh`（G1／OC-3 已鎖）。
- 測試形態：最小 shell 斷言或掛 selftest 入口；是否進 `devflow-check` 主線留 Stage 5／6 任務拆（OC-1：至少一條可自動跑）。
- Example 落點：`example/dogfood-ping`（合 main 後）；過程正本仍 `docs/dev/dogfood-ping/`。

## Test Skeletons(選配)
```bash
# test_s2_s3_stdout_exit.sh — 名含 S-2／S-3
set -euo pipefail
out=$(scripts/dogfood-ping.sh)
ec=$?
test "$out" = "dogfood-ok"
test "$ec" -eq 0
printf 'dogfood-ok\n' | cmp -n - <(scripts/dogfood-ping.sh)
```

## 確認紀錄
- R 範圍草稿 | 2026-09-10 | R-1～R-4 對齊 G1 鎖板（路徑／stdout／exit／file-map）；待 G2 人審
- S 展開草稿 | 2026-09-10 | S-1～S-4 各含觀測；純內部行為 Operational Context = 不適用
- Stage 3 對帳 | 2026-09-10 | throwaway CLI Demo 對應 R-2／R-3；owner chat 准開 Stage 4；Human Demo 正式 attestation 仍待頁面親填
- G2 | 2026-09-10 | owner chat 明示 **G2 PASS**；`verdict: PASS`、`status: approved`；DD-1／DD-2 ✅。准開 Stage 5；正式腳本仍 Stage 6
