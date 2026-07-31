---
feature: <slug>
stage: 5-tasks
status: draft
owner:
updated:
---

# 5. 任務

> 用途:把 4-spec 切成可勾選、可驗證的實作單。
> 順序 = **tracer bullet**:先打通最薄的端到端縱切,再逐層加厚。
> 每個 `## T-n` 必填 Covers、Files、Verify、Blocked-by;Covers 標 R/S id(追溯鏈)。
> Files 一律以 Git repository root 為相對根(例:`src/api/export.ts`);可寫 `./src/a.py`(會正規化),禁絕對路徑、`..` 與 root 條目。

## T-1 <標題>
- [ ] 完成
- Covers: R-1 / S-1
- Files: <預計動的檔>
- Verify: `<指令>`
- Blocked-by: —
- Owner:(多人才填)

## T-2 <標題>
- [ ] 完成
- Covers:
- Files:
- Verify: `<指令>`
- Blocked-by: T-1

## Split Decisions(拆分自判,選配)
<!-- 拆分/排序不顯然時記:決策 | 理由 | 棄項;顯然就整節留白 -->
