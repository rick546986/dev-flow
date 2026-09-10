# DOGFOOD-NOTES — dogfood-ping

模板／閘門試跑筆記（人讀）。feat 正本仍在 `docs/dev/dogfood-ping/`；合 main 後樣張落 `example/dogfood-ping`。

## 2026-09-10

- **G1 PASS**（owner chat）：locked package = Direction A（`scripts/dogfood-ping.sh` → `dogfood-ok` + exit 0）+ **跑 Stage 3** + 合 main 當 Example `example/dogfood-ping`。OC-1～OC-4 ✅。見 `2-decision.md` 確認紀錄。
- 開了 **#165**（Stage2 審頁「方案依據」超寬橫表／手機裁切）。本 PR **不修** #165；只引用。https://github.com/rick546986/dev-flow/issues/165
- **Stage 3**：throwaway CLI Demo 已跑（`dogfood-ok` / exit 0）；`3-prototype.md` + html 已產。owner 2026-09-10 chat 准開 Stage 4；Human verdict／attestation 頁面欄仍留空待親填。
- **Stage 4 / G2 PASS**（owner chat 2026-09-10）：`4-spec.md` `verdict: PASS`、`status: approved`；DD-1／DD-2 ✅。
- **Stage 5**：`5-tasks.md` + html（T-1 CLI → T-2 file-map）；owner 准開 Stage 6 後標 `approved`，T 勾完成。
- **Stage 6（implementer）**：
  - T-1：`scripts/dogfood-ping.sh` 落地；Verify exit 0（stdout=`dogfood-ok\n`）
  - T-2：`EXPECTED_MAPPED_FILES` 193→194 + 指南列 + 靜態釘；`check-file-map.sh` exit 0
  - `6-implementation-notes.md` + html 已產
  - host-receipt：本機鑄／核對 stage6 收據成功（`.devflow/` 不進 Git）
  - Example 樣張未複製（留給合 main／Stage 7）
  - **等獨立 reviewer**；**未開 Stage 7**
