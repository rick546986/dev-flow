---
feature: dogfood-ping
stage: 1-discussion
status: in-review
owner: rick-dev-flow
reviewers: [user]
updated: 2026-09-10
baseline: tip 0a89ec8 (含 #160 Stage6 牙 + #162 主機分流)
contract: 2.0.0
---

# 1. 討論 — dogfood-ping（整套模板試跑）

> 用途:發散。**不做決定**。本 feat 是 dogfood：用 tip 模板／主機分流／收據牙跑完 Stage 1→7。
> 產出刻意極小，不取代 host-stack-fit `#149`／`#163` 未結 G3。
> **HISTORY(2026-09-10 owner)**：不跳過 Stage 3；合 main 當 Example。

## Problem
痛:剛合上收據牙與 Cursor／Grok「執行者 ≠ reviewer／預設 Auto」，但還沒用極小題把 1→7 整套走一遍，不知道模板／產器／閘門哪裡會卡。
現在怎麼繞:靠 host-stack-fit 大包記憶判斷；或只讀模板不實作。

## Context(已知事實)
- tip `0a89ec8` 含 `mint_host_receipt`。出處:`hooks/devflow-lib.py:961`
- 主機分流①③④已寫進 `skills/dev-run/SKILL.md`。出處:`skills/dev-run/SKILL.md:57-68`
- 新增 `scripts/*.sh` 會碰 file-map 地板 `EXPECTED_MAPPED_FILES = 193`。出處:`scripts/check-file-map.sh:114-119`
- 本機 clone 的 `gh` 未登入。出處:本機 `gh auth status` 實跑
- `#163` 仍等 Human G3；本 dogfood 不取代出貨。出處:對話狀態 `[Assumption]` 以 GitHub 為準若已變

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| owner | 確認 1→7＋閘門可走完 | 簽 G1／G2／G3 | tip 能力 | 本輪實際卡點 | GitHub／Cursor／Grok |
| 派工助手 | 依模板產各站、停在閘門 | 本機寫稿；遠端 CloudAgent | 模板 | owner 裁決 | CloudAgent Auto |
| 獨立 reviewer | Stage 6／7 複審 | 另 agent 唯讀 | PR diff | — | 另一隻 CloudAgent |

### Current Journey
| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | owner | 靠大 feat 記憶判斷 | 聊天／PR | — | 無 dogfood 產物 | 難隔離模板 vs 題目 |
| 2 | 助手 | 想試跑但無極小題 | — | owner | — | 易開太大 |

### Workarounds
口頭回憶；只讀模板。都證明不了完整閘門體驗。

### Exceptions
發現模板洞 → 開 issue／薄刀，不回改已合 host-stack-fit 正本（除非 L2）。本機無 gh → 遠端走 Mac／CloudAgent。

### Evidence
- tip 檔案實讀（主機分流、mint、file-map）
- owner 2026-09-10：用新模板跑 1→7；可人工審；先在助手電腦試

## 現況圖
誰:owner
做什麼:靠大 feat 記憶判斷模板好不好用
工具:聊天／PR
痛點:難隔離模板問題與題目複雜度
↓
誰:助手
做什麼:想整套試跑但沒有極小題
工具:本機／CloudAgent
痛點:容易開太大或半套停住
↓
誰:owner
做什麼:在閘門才第一次看到卡點
工具:G1／G2／G3
痛點:回饋太晚模板洞已混進大 feat

## Goals
- 極小可觀測題：建議 `scripts/dogfood-ping.sh` 印 `dogfood-ok`、exit 0
- 走完 1→7（**含 Stage 3，不跳過**）
- Stage 6：寫碼 agent ≠ 審核 agent；預設 Auto
- 加腳本時同步 file-map／相關地板
- 產出「模板試跑報告」（哪站卡、哪句難懂）
- 合 main 當 Example（`example/dogfood-ping`）

## Non-Goals(初稿)
- 不解決 `#163` G3／PF-0
- 不升契約、不順便 bump plugin
- 不做假 PreToolUse
- 不改生產業務邏輯

## Open Questions
- [x] Q1:dogfood 產物是否合進 main？→ owner：合 main，落點為 **Example**（如 example/dogfood-ping）
- [x] Q2:Stage 3 是否跳過？→ owner：**不跳過**，要跑 Stage 3
- [~] Q3:Verify 要掛進 devflow-check／selftest，還是只手動跑腳本？（假設：至少一條可自動跑的測試）
- [>] Q4:本輪是否同時固化 Stage 5 白話欄位（#159）？→ 建議 Intent 白話先寫，模板欄另票

## Approaches(粗探,不決策)
| 方向 | 一句話 | 優 | 劣 |
|---|---|---|---|
| A. 單檔 dogfood-ping.sh | 印固定字 exit 0 | 最小 | 仍碰 file-map |
| B. 只寫 docs | 純文件 | 零地板 | 測不到 Stage 6 |
| C. 另開 scratch repo | 隔離 | 測不到本包牙 |

## Risks & Open Questions(摘要)
- 地板漏同步 → CI 紅
- 與 `#163` 並行需分線
- 本機無 gh → 遠端節奏依賴 CloudAgent／Mac

## Next
owner lean 2026-09-10：方向 A + **跑 Stage 3** + 合 main 當 Example。進入 Stage 2 寫 Decision／請簽 G1。
