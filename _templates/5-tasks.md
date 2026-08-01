---
feature: <slug>
stage: 5-tasks
status: draft
owner:
updated:
---

# 5. 任務

> 用途:把 4-spec 切成可勾選、可驗證的實作單。
> 本階段固定產出:`5-tasks.md`(本模板全節)+ `5-tasks.html`(tasks 定稿供派工時
> 必產;必含 T 依賴 DAG,ASCII 天生適合)。
> 順序 = **tracer bullet**:先打通最薄的端到端縱切,再逐層加厚。
> 每個 `## T-n` 必填 Covers、Files、Verify、Blocked-by;Covers 標 R/S id(追溯鏈)。
> Files 一律以 Git repository root 為相對根(例:`src/api/export.ts`);可寫 `./src/a.py`(會正規化),禁絕對路徑、`..` 與 root 條目。
>
> **T 自足律(為了丟給 agent 不辨識不清)**:每個 T 單獨拿出來,搭配它 Covers 的
> S 原文,執行者就能動工 —— 不需翻其他 T、不需讀 1/2/3。寫法紀律:
> - 標題 = 動詞開頭的一句完成式(「建 ent schema 十二張」,不是「schema 相關」)。
> - Intent 一句話寫「這個 T 做完,系統多了什麼可觀測行為」;Boundaries 寫硬約束/
>   禁區(照哪個既有 pattern、不准動什麼),無則寫「—」。兩欄是派工 prompt 的
>   直接原料;守衛只解析必填四欄,這兩欄不影響 scope。
> - 一個 T 一個關注點:Files 超過 ~5 檔或 Verify 要跑兩套不相干指令 → 拆 T。

## T-1 <標題:動詞開頭一句完成式>
- [ ] 完成
- Covers: R-1 / S-1
- Files: <預計動的檔>
- Verify: `<指令>`
- Blocked-by: —
- Intent: <做完系統多了什麼可觀測行為,一句>
- Boundaries: <硬約束/禁區;無則 —>
- Owner:(多人才填)

## T-2 <標題>
- [ ] 完成
- Covers:
- Files:
- Verify: `<指令>`
- Blocked-by: T-1
- Intent:
- Boundaries: —

## Split Decisions(拆分自判,選配)
<!-- 拆分/排序不顯然時記:決策 | 理由 | 棄項;顯然就整節留白 -->
