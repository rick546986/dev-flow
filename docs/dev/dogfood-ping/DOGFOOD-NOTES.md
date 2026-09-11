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

## 2026-09-11

- **Stage 7 author pack（Agent A）**：寫了 `7-review.md` + `7-review.html`（`build-gate-twin.py`）；frontmatter 曾為 **`verdict: PRE-REVIEW`**。
- Author 親跑現象：stdout hex `64 6f 67 66 6f 6f 64 2d 6f 6b 0a`、exit 0；`check-file-map.sh` exit 0（`scanned=194`）。
- 整合回歸腳本：`STATUS=N_A_NO_INCOMING`（FORK=INTEGRATION=`0a89ec8…`）。
- Example 最小鏡像已落 `example/dogfood-ping/`（SC-6 packing；含 1–7 + DOGFOOD-NOTES）。
- 獨立 **reviewer B ≠ A**：建議 PASS（`7-reviewer-B-notes.md` @ `36c68db`）。
- **Human G3 PASS** by owner 2026-09-11 (Asia/Taipei)；`7-review.md` `verdict: PASS`。**Merging #164 → main as Example.**
- 已知摩擦：#165（Stage2 超寬表，**保持 open**，本 PR 不修）；KL#3 Gauntlet 明示降級。
- CI：`example/dogfood-ping/5-tasks.md` 進 TF_SKIP（POSIX `test -x` 誤觸 `\btest\b`；無測試套件手樣，同 subsidy）。
