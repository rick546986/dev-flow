# F1 RP 最小集（five-station-simplify）

> OC-10：只准加不准減。編號與 4-spec／Decision 表同義，不另發明。
> 本檔是語意清單，不是 event schema。超 cap 三列的計數落點交 F2。

| id | 紅什麼 | 人見面 |
|---|---|---|
| RP-1 | T 缺 Covers／Files／Verify／Blocked-by，或 Verify 只寫「看起來沒問題」 | T 卡上就紅；勾選不算完成 |
| RP-2 | 無 RED 輸出，或 reviewer = implementer | 該 T 未完成 |
| RP-3 | S 含 C4 `VAGUE_ALL` 三詞或「系統應處理錯誤」且無可斷言輸出 | 該 S 不得當 Covers 綠燈 |
| RP-4 | 測試名不含 `s_`／`S-` 與對應 S-id（如 `test_store_half_slot`） | 該測試紅；`test_s_2_5_test_name_requires_s_id` 不因本條紅 |
| RP-5 | 缺 Files，或 Files ⊈ 同份 5-tasks Files 聯集 | 該 T 不得標完成 |
| RP-6 | 完成宣稱只有摘要，無原始輸出或 `檔:行` | 摘要不得當證據 |
| RP-7 | 不可逆（schema／公開 API／權限／金流／資料遺失）無 Quiz | 可逆強制 Quiz 當第三例行停也紅 |
| RP-8 | `7-review.md` 頂欄無人類 `verdict: PASS` 卻標 Done | 狀態留 Ship／HumanWait |
| RP-9 | 同一 hop 重寫第 3 次仍繼續 | Escalated；不准暗改計數。舊 7 不套 |
| RP-10 | Decide 整站重開第 2 次仍繼續 | 站內未 hop 出的小改不算 |
| RP-11 | 離開 Intake 後 Goal 重開第 2 次仍繼續 | 可同時用盡 Decide cap |
| RP-12 | trigger 未命中卻強迫 `ACCEPTED` | 不建 Demo 頁 |
| RP-13 | Human verdict／attestation 空 + chat「可以開 Stage 4」 | 不得離 Spec |
| RP-14 | A4／A7 latch=否卻留下「請人審／要不要繼續」 | 不是客氣 |
| RP-15 | in-flight（已有 1–7 `.md`）被寫入五站狀態或五站 hop | 清回舊 7 |
| RP-16 | Agent／coordinator 寫入 `ACCEPTED` 或 Ship `PASS` 且無人類 attestation／頂欄 | 視為未寫；人親寫不因本條誤殺 |
