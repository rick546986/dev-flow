---
feature: integration-before-verdict
stage: 5-tasks
status: approved
owner: rick
updated: 2026-09-12
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — 填檔牙與活教師

> 把 4-spec（G2 PASS、#221 = `8592e13`、R/S 來自 #216）切成可派工縱切。
> 本 hop **只寫任務**，不落地 Stage 6 守衛碼、不碰 diagram-ir-gate／#196、不 bump plugin、不發版、不改 `STATUS.md` 表列、不代填 G3。
> 模式：sequential（見 Split Decisions）。tracer：T-1 先讓填檔牙可觀測，T-2 再改口腳本／manifest，T-3 掃 example 與衍生 fixture。

## 開工前提

Stage 4 已核准。G2 PASS 已在 tip（#221）。本 hop 不改 `4-spec.md`／`4-spec.html`。牙掛進既有 `check-stage67` ST 組，不是第二套 `check-already-synced.sh`。活教師改口只動編號／檔頭；2c 仍叫整合回歸。R-5 真跑（本 slug 自己的 Stage 7 Exit）不在本 hop 切 T。

### N1 R/S 盤點（16 S）

| R | S | 本 hop T |
|---|---|---|
| R-1 拒絕 void-only `ALREADY_SYNCED` 填檔 | S-1.1 void-only 紅；S-1.2 重綁 SHA 綠；S-1.3 本項 FAIL 綠 | T-1 |
| R-1（續） | S-1.4 GUIDANCE 寫重綁／FAIL | T-2 |
| R-2 放過未宣稱 n-a／draft | S-2.1 `N_A_NO_INCOMING` no-fire；S-2.2 draft no-fire | T-1 |
| R-3 清除活教師舊序 | S-3.2 manifest／腳本檔頭 | T-2 |
| R-3（續） | S-3.1 example；S-3.3 衍生 fixture 同一 T；S-3.4 活路徑 `rg` 零 | T-3 |
| R-4 保留 2c 編號與既有牙 | S-4.1 模板序；S-4.2 三支既有牙仍綠 | T-1 Verify（不改模板正文） |
| R-4（續） | S-4.3 整合腳本演算法／exit 碼不變 | T-2 |
| R-5 出貨樹=核准樹 | S-5.1／S-5.2／S-5.3 | 不切 T（Split Decisions） |

### Verify 開工前原樣跑（2026-09-12；牙尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1 | `ST-filled:` 計數 0，`test -ge 5` 紅 | ③綠不了但方向對（牙尚未落地）→ 開工條件成立 |
| T-2 | GUIDANCE 無「重綁」／「FAIL」恢復句，舊檔頭針仍在 → assert 紅 | ③方向對 |
| T-3 | example／fixture 舊針仍命中 → 第一個 `test -eq 0` 紅 | ③方向對 |

## T-1 讓 check-stage67 對已宣稱 void-only 填檔紅、對重綁／FAIL／n-a／draft 綠
- [ ] 完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3; R-2 / S-2.1, S-2.2; R-4 / S-4.1, S-4.2
- Files: scripts/check-stage67-enforcement.sh, scripts/fixtures/stage67-filled-tooth/
- Verify: `n=$(bash scripts/check-stage67-enforcement.sh 2>&1 | grep -c 'ST-filled:'); test "$n" -ge 5 && bash scripts/check-stage67-enforcement.sh && bash scripts/check-integration-regression-guard.sh && bash scripts/test-evidence-gauntlet.sh && python3 -c "import pathlib; t=pathlib.Path('_templates/7-review.md').read_text(); h=t.split('\n## ')[0]; i,f=h.find('整合回歸'),h.find('Final Fresh Run'); assert 0<=i<f; print('S-4.1-ok')"`
- Blocked-by: —
- Intent: 日常多一步：勾 2c／送 G3 之前，同一支 `check-stage67` 會讀填好的 7-review。只寫「證據不算數」的已宣稱 `ALREADY_SYNCED` 會紅；重綁 `Source SHA`（≥7 hex）或寫「本項 FAIL」會綠；零新 commit 的 n-a 與未勾 draft 不會被提前擋住。改的是檢查射程（從模板字串延到填檔），不是新發明一套整合工具。不會變成 Cursor 擋寫、不會改整合腳本 exit 碼、不會重寫模板已搬的 2c 散文。
- Boundaries: 只准改 `check-stage67-enforcement.sh` 的 ST 組與 `scripts/fixtures/stage67-filled-tooth/` 五份對照（void-only／rebind-sha／item-fail／na-incoming／draft-unclaimed，形狀對齊 Stage 3）。入口字面必須仍是 `bash scripts/check-stage67-enforcement.sh`，禁止新開 `check-already-synced.sh` 當唯一入口。填檔牙擁有通過／失敗判定；整合腳本仍擁有 STATUS 名稱與三 SHA，本 T 不得改它的演算法或 exit 碼（0／10／11／2）。既有 ST 模板順序項、`check-integration-regression-guard.sh`、`test-evidence-gauntlet.sh` P0-1 必須仍綠；`_templates/7-review.md` 頂註「整合回歸」必須仍在「Final Fresh Run」之前。Actor=Stage 7 reviewer；Goal=勾 2c 時不能靠作廢句過關；Human decision=選重綁 SHA 或本項 FAIL；Authority=reviewer 寫恢復欄、檢查 exit 擋勾過；Recovery=補「重綁 Final Fresh。Source SHA: <hex≥7>」或改寫「本項 FAIL」後重跑，不要進 Verdict。看過 `ALREADY_SYNCED` ≠ 已恢復。

## T-2 改整合腳本 GUIDANCE 與檔頭、改口 manifest，且演算法不變
- [ ] 完成
- Covers: R-1 / S-1.4; R-3 / S-3.2; R-4 / S-4.3
- Files: scripts/devflow-integration-regression.sh, docs/dev/tools/devflow-integration-regression.sh, manifests/p4-gauntlet-gates.md
- Verify: `python3 -c "import pathlib,re,sys; a=pathlib.Path('scripts/devflow-integration-regression.sh').read_text(); b=pathlib.Path('docs/dev/tools/devflow-integration-regression.sh').read_text(); m=pathlib.Path('manifests/p4-gauntlet-gates.md').read_text(); ga=a[a.find('GUIDANCE'):]; gb=b[b.find('GUIDANCE'):]; assert '重綁' in ga and 'FAIL' in ga and '重綁' in gb and 'FAIL' in gb; assert '執行清單 2c 的文檔化命令' not in m; assert re.search(r'Exit Checklist.*整合回歸.*計算工具', a) is None; assert re.search(r'Exit Checklist.*整合回歸.*計算工具', b) is None; assert '絕不動樹' in a and 'sys.exit(code)' in a; assert all(x in a for x in ['N_A_NO_INCOMING','ALREADY_SYNCED','SYNC_REQUIRED_NO_OVERLAP','SYNC_REQUIRED_WITH_OVERLAP']); assert ', 2' in a and ', 10' in a and ', 11' in a; print('T-2-ok')"`
- Blocked-by: T-1
- Intent: 日常少一句誤導、多一句下一步：腳本印 `ALREADY_SYNCED` 時，GUIDANCE 要告訴人重綁 Final Fresh 或寫本項 FAIL，不能只說「輸出不算數」就結束。檔頭改成「步 2c 整合回歸，Fresh 之前，不是 Exit 程序」；manifest 若仍指 gauntlet 命令則寫 2d。不會變成腳本自己 merge／重綁／自動 FAIL，也不會改 STATUS 名稱或 exit 碼。
- Boundaries: 兩支整合腳本只准改檔頭與 `GUIDANCE` 字串；正本與 `docs/dev/tools/` 散發副本必須一起改（parity 仍由既有 guard 咬）。禁止改 `sys.exit(code)`、禁止新增自動重綁、禁止把 `ALREADY_SYNCED` 自動當 FAIL、禁止 merge／rebase。manifest 只准把「執行清單 2c 的文檔化命令」改成 2d，不准重編號整份 Stage 7 清單。本 T 不改 example、不改 HISTORY／dispatch／stage7-loop。

## T-3 改口 example 與衍生 fixture，活路徑舊針歸零
- [ ] 完成
- Covers: R-3 / S-3.1, S-3.3, S-3.4
- Files: example/contract-expiry-reminder/7-review.md, example/contract-expiry-reminder/7-review.html, example/contract-expiry-reminder/4-spec.md, example/contract-expiry-reminder/4-spec.html, scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md
- Verify: `test "$(rg -n '執行清單 2c 的 Final Fresh|執行清單 2c gauntlet' example/contract-expiry-reminder/ | wc -l | tr -d ' ')" -eq 0 && test "$(rg -n '執行清單 2c gauntlet' scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md | wc -l | tr -d ' ')" -eq 0 && { bash scripts/check-spec-gate.sh scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md; test $? -eq 1; } && test "$(rg -n '執行清單 2c 的 Final Fresh|Exit Checklist.*整合回歸.*計算工具' example/contract-expiry-reminder/ manifests/p4-gauntlet-gates.md scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh | wc -l | tr -d ' ')" -eq 0`
- Blocked-by: T-2
- Intent: 日常抄範例時走 2c 整合 → 2d Fresh，不再把 2c 當成 Final Fresh 或 gauntlet。example 兩檔與衍生 `spec-gate-dd-subsection` fixture 同一刀改口；`check-spec-gate.sh` 對該負向 fixture 仍要紅（C5 待裁決牙不因改序號假綠）。活路徑聯合 `rg` 歸零。不會改 HISTORY／dispatch／stage7-loop 當時句，也不會重編號整份清單。
- Boundaries: Fresh／gauntlet 序號從 2c 改 2d；2c 仍只准出現在「整合回歸」語境。example 4-spec 與 `bad-dd-unresolved.md` 必須同一 T 改（DD-6）。7-review.html／4-spec.html 是同目錄 twin，舊針在 html 也要清。禁止改 `notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/`（OC-2 死紀錄）。本 T 不改整合腳本演算法（屬 T-2）。Files 五檔是同一刀「活教師 + 衍生副本」，不是按架構層切開。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential，不開 parallel | T-2／T-3 檔案與 S-3.4 聯合 `rg` 有硬順序；T-1 是公開檢查契約（Feature Risk high）。三個 T 開 parallel 只省一波，tip 預設 sequential、須明確啟用才改。 | `_templates/5-tasks.md` `execution.mode` 缺省 sequential；4-spec Verification Profile Risk high | 棄 T-1 ∥ T-2。兩 T 檔案不重疊，可平行，但本 hop 選保守序：先打通牙再改口教師。 |
| T-1 含五份 fixture 當一刀 | 可觀測行為是同一支檢查的開火／不開火，不是五層架構。目錄一條算進 Files，避免按 fixture 橫切。 | 4-spec S-1.1「同一入口」；Stage 3 五份 scratchpad 對照；模板「一個 T 一個關注點」 | 棄「void-only 一 T、恢復一 T、no-fire 一 T」（同一函式、同一 Files）。 |
| GUIDANCE + 檔頭 + manifest 同 T-2 | S-1.4 與 S-3.2 腳本半部落在同一兩支檔；S-4.3 是這兩檔的 Non-Goal。拆開會讓兩 T 改同一檔。 | 4-spec S-1.4／S-3.2／S-4.3；DD-6 檔頭改口 | 棄「GUIDANCE 一 T、檔頭一 T」。 |
| example + 衍生 fixture 同 T-3 | DD-6／S-3.3 明寫同一 T。S-3.4 聯合 `rg` 含 T-2 路徑，故 Blocked-by T-2。 | 4-spec S-3.3、S-3.4、DD-6 | 棄把 S-3.4 再拆成第四 T。 |
| R-5 不切 T | owner brief：本 hop 只切 AS-1 填檔牙 + 活教師。S-5.1 要等本 slug 自己的 Stage 7 Exit 才有 7-review Source SHA；4-spec Known limit ③。S-5.3 由本目錄過程檔禁寫「跳過 2c」「Exit 才合併」約束，不另開 T。 | owner Stage 5 brief；4-spec R-5「真跑留後續 hop」、Known limit ③；`[Assumption]` R-5 另 hop | 棄現在就寫 S-5.1 Verify（現檔沒有 7-review，會變成恆紅或假綠）。 |
