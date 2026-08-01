---
feature: <slug>
stage: 6-implementation
status: draft
owner:
updated:
---

# 6. 實作筆記

> 用途:實作期唯一日誌。TDD 證據 + 偏差記錄。reviewer 審之前先讀這份。
> 本階段固定產出:`6-implementation-notes.md`(本模板全節)+ `6-implementation-notes.html`
> (全 T 完成、bookkeeping commit 前必產;必含 T Review Log、Decisions+Deviations 表、
> 每 T diff 折疊條)。
> TDD 規則(superpowers):每個 S-id **先寫失敗測試**(RED,貼輸出摘要)→ 最小實作到
> GREEN → refactor 保綠。沒看過測試失敗 = 不知道它測對東西。
>
> 執行清單(開場第一動建成 todo;逐步達成「完成 =」才勾;禁跳項、禁併 T):
> 0. 起手式:圍欄自查 —— 只讀 4-spec/5-tasks/6-notes/CONTEXT.md/living spec,
>    禁讀 1/2/3(要翻才寫得出 = spec 不完整 → 停,回 G2)。開 feature branch
>    (並行 → worktree)。完成 = 讀取清單回報+branch 就位。
> 1. 接手核對:4-spec approved?5-tasks 每 T 有 Verify+Covers?缺 → 停回補。
>    建 todo 一 T 一項,照 Blocked-by 拓撲序。完成 = todo 與 5-tasks 一一對應。
> 2. 逐 T 循環:a 照 Covers 先寫失敗測試(名含 S-id)→ RED 輸出貼
>    TDD Evidence;b 最小實作到 GREEN(貼輸出)→ refactor 保綠;c scope check:
>    git status 改動檔 ⊆ 該 T 自己的 Files,超出 → L1/L2 判(定義見下);d 跑該 T
>    Verify;e independent T review:reviewer 必須不同於 T implementer,優先適格人類,
>    否則 fresh-context reviewer Agent;reviewer 親跑 Verify,檢查 Covers、RED→GREEN
>    證據與該 T 自己的 Files scope。FAIL → 回同一 T 修正並重新送審;高風險或
>    finding 有爭議可加第二 reviewer;f PASS → commit;g hash 入 Progress Log +
>    勾 checkbox + review evidence 入 T Review Log;h 自由選擇 → Decisions 一行續走,
>    偏差 → L1/L2。完成 = 該 T reviewer PASS + checkbox ✓ + hash 在案 + Covers
>    的每個 T × S 全有該 T 自己的 RED→GREEN 證據。順序固定:RED → GREEN → scope check → Verify →
>    independent T review → PASS → commit → Progress Log + checkbox + review evidence。
> 3. 回歸:全 T 後跑既有全套,本次 S 全綠+既有全綠;紅 → 修+依偏差級記。
>    完成 = 全套**全綠**輸出摘要入本檔(紅字摘要不算完成)。
> 4. 自檢(= Self-Review 節逐問作答):①每個「T × Covers S」都有含 S-id 的測試 +
>    該 T 自己的 RED/GREEN 證據(不得跨 T 共用)?
>    ②每 T 在 T Review Log 有 verdict?③每個 PASS 都早於該 T commit?④每個 FAIL
>    後有較晚 PASS,否則該 T 仍未勾、未 commit?⑤每個已完成 T 一 commit、Progress
>    Log 每列有 hash?⑥git diff --stat 檔案 ⊆ Files 聯集、Diff Budget 內?
>    ⑦Decisions/Deviations 與 diff 對得上(無 silent drift)?⑧回歸綠?答不出 →
>    回步 2/3 補。完成 = 八答落檔。
> 5. 收尾:Files Changed 填(對照 Diff Budget)、全節齊無佔位、status 更新。
>    完成 = 節齊 + frontmatter status 已更新。
>
> 實作期規則(實作中**不打斷問人**,自主推進):
> - **檢查點**:每個 T 都要先經不同 implementer 的 reviewer 獨立審查 PASS,才可
>   commit、記 Progress Log、勾 checkbox;FAIL 回同一 T 修正並重新送審。
> - **Scope guard**:改動檔案 ⊆ 5-tasks 全部 T 的 Files 聯集;超出依 L1/L2 判。
> - **Decisions**(spec 未載明的自由選擇,如內部命名、資料結構):自己選、記一行、繼續。
> - **偏差**:
>   - **L1**(不動 R/S 的計畫內偏差)→ 選**保守方案**、記 D-n、**繼續執行**。
>   - **L2**(要改 R/S 或推翻 2-decision)→ **停**,修 4-spec → 重新 G2 → 才續。
>     禁止 silent drift。(L1 = Anthropic field-guide 原版;L2 為本 SOP 加嚴)
>   - 分不清 L1/L2 → **一律當 L2**,不留自由心證。

## T Review Log
<!-- 每 T 一筆,逐 round 留痕:
### T-1
- reviewer identity:<姓名或 Agent 身分>
- reviewer kind:human | fresh-context Agent
- reviewed-at:<時間,須早於該 T commit>
- Verify:<原指令> → <reviewer 親跑的觀測結果>
- Covers finding:<涵蓋是否吻合>
- Files finding:<改動是否位於該 T 自己的 Files scope>
- RED→GREEN finding:<證據是否完整、可信>
- verdict:PASS | FAIL
- correction + re-review after FAIL:<修正內容 + 後續 round 證據;無 FAIL 則 N/A>
-->

## Progress Log
<!-- 日期 | T-id | 一行;只記 T Review PASS 後做的 commit,每列含 commit hash -->

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
<!-- 每 T 一列:T-id | 失敗分類(SPEC/ENV/IMPL/UNKNOWN,README §5 驗證五律 5;
     全程無失敗填 —)| 模型升階史(如 haiku→sonnet)| 回合數 | 升階原因一句。
     ENV 失敗的重跑不計升階回合。升階本身 = spec 品質訊號,7-review.html 以表呈現 -->

## TDD Evidence
<!-- 每個「T × Covers S」各一筆;同一 S 在不同 T/層次的 RED→GREEN 不得共用。 -->
### T-1 / S-1
- RED: `<test cmd>` → <失敗輸出摘要>
- GREEN: `<test cmd>` → <通過輸出摘要>

## Decisions(spec 未載明的自由選擇)
<!-- 一行一個:選了什麼 + 為何;不屬偏差,不需回審 -->

## Deviations
### D-1(L1|L2)
- 現象:
- 保守選擇:
- 理由:
- 影響:T-? / R-? / S-?

## Files Changed
<!-- 對照 4-spec Diff Budget -->

## Diff(各 T commit,逐檔折疊)
<!-- README §6 要求每檔一個 details。summary 的 title/文字列 +N/-N 與函式;
     內容放 HTML-escaped 完整 diff,刪行 class="del"、增行 class="add"。 -->

## Self-Review
<!-- = 執行清單步 4 的八問:逐問作答、附證據(review 時間/verdict/測試輸出/hash/diff stat),不憑印象 -->

## Review Follow-up(G3 打回時才用)
<!-- 逐 F:同意 → 改+一句為何對;不同意 → 擺論證,不盲改(禁 performative fix) -->
