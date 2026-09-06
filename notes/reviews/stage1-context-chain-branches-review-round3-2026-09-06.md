# 審查：Stage 1 context-chain 實作（三輪）

> **收編自** `claude/optimization-brief-review-ki31n6` 的
> `notes/review-stage1-context-chain-branches.md`（2026-09-06）。原路徑已不在 main。
> 第一輪見 [同日審查](stage1-context-chain-branches-review-2026-09-06.md)。

> 第三輪對象：main `291a237`（#136 brief 第三版 + #134 `parser-7d32` 實作已合）、
> 仍開著的 PR #133（`0ded` → main）與 #135（`skills-7f26` → `claude/optimization-brief-review-ki31n6`）。
> 方法：main 開 worktree 跑 `devflow-check.sh` 全套、掃頁守衛、fixture 重生、
> 22 個 `parse_log` 邊界案例、完整產生器 `<script>` 注入。
> 第一、二輪意見在 §4、§5，供對照。

## 0. 第三輪結論

**main 現在的狀態可以收。** 第二輪 §1 要求的順序有照做：brief 先單獨合（#136），
再合實作（#134，squash）。窄 viewport 拍板為 `.tablewrap` 橫向捲動，
結論前綴補了邊界 regex，兩者都寫進 brief §6.3／§7／§10／§12，實作與文件一致。

main 上驗證結果：

| 項目 | 結果 |
|---|---|
| `scripts/devflow-check.sh` 全套 | 綠（methodology／contracts／architecture／render 四組） |
| `check-devtalk-fig-graph.sh`、`check-devtalk-guide-sync.sh`、`check-stage1-now-contract.sh`、`check-gate-tokens.sh` | 綠 |
| good fixture html 雙胞胎 | 與產生器輸出一致 |
| 11 份 bad fixture | 全紅，`check_log_teeth` 有比對訊息 |
| 22 個邊界案例（§3） | 全部符合期望，含第二輪抓到的頂層散文、行段超界、`CONFIRMEDx`、光禿前綴 |
| `<script>` 注入 Q 欄 | escape |
| `html-shell.html` | 自 `0c230b9` 起零改動 |

一個環境註記：`devflow-check.sh` 第一次跑在本容器紅了三組，全是缺 `markdown-it-py`
（`scripts/requirements-methodology-render.txt` 有列）。裝上後全綠，base `0c230b9` 同樣缺，不是這次的回歸。

## 1. 收尾事項（都不擋合，但要處理）

1. **關掉 #133 與 #135。** 兩支都被 #134 取代。#135 的 base 是我的分支
   `claude/optimization-brief-review-ki31n6`，不是 main，本來就合不到正確的地方；
   我的分支現已重設到 main 之上、只剩本審查檔，#135 的 diff 會變成整支 7f26 對 main，直接關即可。
2. **從 `skills-7f26` 搬三個節點檔的文字**（小 docs PR，不動 graph）：
   - `skills/dev-talk/nodes/S1-survey.md`：7f26 把「做什麼」改成六步編號，第 1 步寫進 §6.1 的三軸規則
     （只有 `known_facts` 的 `VERIFIED` 是 Context 候選、`known_knowledge` 的 `CONFIRMED` 只是 signal）。
     main 現在的 S1 只有六行概述，沒有三軸。
   - `skills/dev-talk/nodes/S8-review.md`：7f26 版把「同形不同義、不得互借」與「至少一個 `path:L`」寫進第④條；main 版只有一句。
   - `skills/dev-talk/nodes/N1-start.md`：7f26 版多「三軸狀態不得互借；signal ≠ evidence」一句。
   三個檔都不在 `check-devtalk-guide-sync.sh` 的逐字引用範圍，搬過去不會踩守衛。
3. **補兩份 bad fixture 進 `TOOTH_CASES`**：main 的 parser 已 fail-closed，但沒有 fixture 釘住：
   - 頂層散文（`0ded` 的 `bad-tooth-prose`、`7f26` 的 `bad-tooth-toplevel-prose` 任一份）。
   - Context 只有裸路徑、事實欄有 `:L`（`7f26` 的 `bad-tooth3-bare-path`）。
   `check_log_edges()` 目前也沒測這兩個。
4. **example 的 html 雙胞胎過時。** #134 改了 `example/contract-expiry-reminder/1-discussion.md` 的 Log，
   html 仍是舊的 `explore:`／`grill-with-docs:` 列。掃頁產生器拒絕這份 md（現況圖槽叫「邏輯圖」，main 上一直如此），
   所以無法重生；`skills-7f26` 有一份手改同步的 html 可直接搬，或另開 issue 把 example 正名成現況圖再重生。
5. **`notes/reviews/stage1-context-chain-branches-review-2026-09-06.md` 的結論過時。**
   它寫「CHANGES REQUIRED、不要直接 merge」，而 P0-1 到 P1-4 在 #136／#134 已全部處理。
   建議在檔頭加一段「已於 #136／#134 解決」的註記，或移到歷史區，避免下一個讀的人以為還有阻擋項。
6. **產品 repo 遷移提醒**（#134 PR 說明已寫，這裡再記一次）：既有 `1-discussion.md` 的 Context 若只有裸路徑、
   Log 若是舊單行格式，重生掃頁 html 會被產生器拒絕。這是 §6.2／§6.3 的本意，不是 bug，但要讓使用者知道。

## 2. 三支分支最終狀態

| 分支 | 狀態 | 處置 |
|---|---|---|
| `parser-7d32` | 已合 main（#134） | 分支可刪 |
| `0ded` | PR #133 開著，落後 main 3 commit | 關。`check_log_edges()` 已在 #134 移植；只剩 prose fixture 值得搬（§1-3） |
| `skills-7f26` | PR #135 開著，base 錯 | 關。搬節點文字、bare-path fixture、example html（§1-2／3／4） |
| `design-2259` | 已合 main（#136） | 分支可刪 |

## 3. 第三輪邊界測試（main `291a237`）

| 案例 | 結果 | 期望 |
|---|---|---|
| Q 文字含 `\|` | 綠 | 綠 |
| 推理欄含 `\|` | 綠 | 綠 |
| 反引號包路徑 | 綠 | 綠 |
| 全形括號包路徑 | 綠 | 綠 |
| 事實欄零 citation | 紅 | 紅 |
| 子項續行 | 併入上一欄 | 併入 |
| 子項 4 空白 | 紅 | 紅 |
| tab 縮排 | 紅 | 紅 |
| 重複標籤 | 紅 | 紅 |
| 第 9 條（含合法） | 紅 | 紅 |
| 舊單行 `\|` | 紅 | 紅 |
| 舊結論詞 `已解` | 紅 | 紅 |
| `- ⚠️ Q:` | 綠 | 綠 |
| Q 與子項間空行 | 綠 | 綠 |
| 路徑只在 Context 註解 | 紅 | 紅 |
| 無 Context 節 | 紅 | 紅 |
| 事實行段 ⊆ Context 行段 | 綠 | 綠 |
| 事實行段超出 Context 行段 | 紅 | 紅 |
| Context 只有裸路徑 | 紅 | 紅（§6.2） |
| 頂層散文 | 紅 | 紅 |
| 頂層 `###` 小標 | 跳過 | 跳過 |
| Q 續行 | 併入 Q | 併入 |
| `CONFIRMEDx` | 紅 | 紅 |
| 只有 `CONFIRMED` 無句子 | 紅 | 紅 |
| `<script>` 注入（完整產生器） | escape | escape |

## 4. 第二輪意見（2026-09-06 下午，已處理）

當時 main 的 brief 是第二版、三支各帶不同版本的第三版；要求先單獨合 brief、再合實作，
並拍板窄 viewport。`parser-7d32` 可合但缺結論前綴邊界；`0ded`／`skills-7f26` 頂層散文會接進前一條結論欄，
且牙 3 只比路徑不比行段。以上在 #136／#134 全部處理，結果見 §0、§3。

## 5. 第一輪意見（2026-09-06 上午，已處理）

三支當時各有一個必修：`0ded` 任何 Q 含 `|` 都紅；`parser-7d32` 的 `assert-teeth.py` 沒接進守衛；
`skills-7f26` 先截 8 條再驗。共同缺口：續行靜默丟、路徑 token 黏標點、Context 註解內路徑算過、
example html 雙胞胎不一致、brief 沒寫 2 空白規則。第二輪 commit 全部修掉。
