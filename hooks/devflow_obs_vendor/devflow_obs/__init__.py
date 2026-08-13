"""devflow_obs — DevFlow Agent Attempt 可觀測性工具(python3 標準庫,無第三方依賴)。

模組:
- ids            執行追溯鏈 ID 生成(run/attempt/review/finding;prefixed ULID)
- event_validate 事件/context manifest/prompt registry schema 驗證(schema JSON 為正本)
- writer         併發安全寫入(atomic temp+rename、單一寫入者鎖、seq)
- ledger         run 目錄讀取(incomplete 判定、restart 恢復、derived 重建)
- stats          跨 Feature 統計聚合 + Recommendation(只建議,不改 Prompt)
- legacy_md      舊 6-notes 執行軌跡 Markdown 讀取(無 Run ID 相容)
"""
