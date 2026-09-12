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

# 5. 任務 — AS-1 填檔牙 + 活教師掃蕩

> 把 #216 的 4-spec R/S 切成可勾選的實作單。本 hop **只寫任務 + 執行板**,不落地 Stage 6 碼、不碰 diagram-ir-gate／`#196`、不發版、不改 `STATUS.md` 表列、不代填 G3。
> G2:tip `6b49d95` 的 `4-spec.md` frontmatter 仍 `status: draft`、`verdict` 空。owner 口頭 G2 PASS 2026-09-12,本站不擋、也不回寫 4-spec PASS。
> 切片只接 **AS-1 填檔牙**(R-1／R-2)+ **活教師**(R-3)+ 改完必須仍綠的既有牙(R-4)。R-5「出貨樹=核准樹」真跑留給本 slug Stage 7,見 Split Decisions。
> `execution.mode: sequential`(tip 缺省)。T-1～T-3 同改 `check-stage67-enforcement.sh`;T-4／T-5 經 S-3.4 活路徑聯集碰到同一對整合腳本。唯一能平行的是 T-1∥T-4,不值得改 parallel。

## 開工前提

- 指定檢查入口仍是 `bash scripts/check-stage67-enforcement.sh`,不新開 `check-already-synced.sh`。
- 五份對照形狀跟 Stage 3 throwaway:`void-only` 紅;`rebind-sha`／`item-fail`／`na-incoming`／`draft-unclaimed` 綠。
- 活教師只改編號／檔頭:Fresh／gauntlet 從 2c 改 2d;2c 仍叫整合回歸。HISTORY／dispatch／stage7-loop 不改。
- 整合腳本 STATUS／exit 仍是 `0`／`10`／`11`／`2`;只算只判,絕不動樹。
- 本 slug 過程檔不得寫成「跳過 2c」或「Exit 才合併」的執行指令(S-5.3 禁令,每個 T 都守;不是本切片的實作項)。

## T-1 拒絕只寫作廢的已宣稱 ALREADY_SYNCED 填檔
- [ ] 未完成
- Covers: R-1 / S-1.1
- Files: scripts/check-stage67-enforcement.sh, scripts/test-already-synced-filled.sh, scripts/fixtures/already-synced-filled/void-only.md
- Verify: `n=$(bash scripts/test-already-synced-filled.sh --group void-only -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 1 && bash scripts/test-already-synced-filled.sh --group void-only`
  期望:void-only fixture(`status: approved`、`verdict: PASS`、`ALREADY_SYNCED`、只寫「證據不算數／輸出不算數」、無 `Source SHA:` ≥7 hex、無「本項 FAIL」)經同一入口檢查 exit ≠ 0,輸出含 `void-only` 或同等「只寫作廢」。開工前原樣跑:缺 `scripts/test-already-synced-filled.sh` → exit 127。③綠不了但方向對。
- Blocked-by: —
- Intent: 勾過 2c 或已送 G3 的人,不能再靠「證據不算數」過關 —— 檢查會紅,必須回頭補重綁 SHA 或寫本項 FAIL。改的是既有 check-stage67 對填好 7-review 的射程,不是新 CLI。不會變成 Cursor 鎖鍵盤,也不會改整合腳本 exit 碼。
- Boundaries: 牙掛進 `check-stage67-enforcement.sh` ST 組;入口字面仍是那一支。禁第二套整合 CLI。禁改整合腳本 STATUS／exit。既有 ST 模板順序項必須留下。結論塊欄位鎖定 STATUS + 三 SHA／REF + 恢復欄。只讀 7-review,不寫回。本 T 只釘 void-only 紅;重綁／FAIL／no-fire 留給後續 T。過程檔禁寫「跳過 2c」「Exit 才合併」。
  Design Boundary(最小子集):可改 check-stage67 填檔牙模組;該模組擁有通過／失敗判定。禁依賴新 CLI、禁改腳本演算法。Interface = 同一入口讀一份 md、exit 0／≠ 0 + reason。Test seam = void-only fixture。

## T-2 接受重綁 Source SHA 與本項 FAIL 兩條恢復
- [ ] 未完成
- Covers: R-1 / S-1.2, S-1.3
- Files: scripts/check-stage67-enforcement.sh, scripts/test-already-synced-filled.sh, scripts/fixtures/already-synced-filled/rebind-sha.md, scripts/fixtures/already-synced-filled/item-fail.md
- Verify: `n=$(bash scripts/test-already-synced-filled.sh --group recovery -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-already-synced-filled.sh --group recovery`
  期望:rebind fixture 恢復欄「重綁 Final Fresh。Source SHA: def4567890abc」→ exit 0 且輸出含該 SHA;item-FAIL fixture 恢復欄字面「本項 FAIL」→ exit 0 且輸出含 `item-FAIL` 或「本項 FAIL」。短於 7 hex 當 void-only,不在本組當綠。開工前原樣跑:缺測試腳本 → exit 127。③綠不了但方向對。
- Blocked-by: T-1
- Intent: 同一支檢查,人寫得出重綁 SHA 或本項 FAIL 就能綠 —— 日常多了兩條可執行下一步:重綁者進 2d,FAIL 者停、從乾淨座標重算。改的是恢復對照,不是「已合過」四個 STATUS 名稱。不會把 ALREADY_SYNCED 自動當 FAIL,也不會讓腳本自己重綁。
- Boundaries: 沿用 T-1 同一入口與宣稱條件。SHA 地板 ≥7 hex(例 `def4567890abc`)。禁改腳本 exit 語意。禁另造恢復第三條(只寫作廢仍紅)。本 T 不處理 n-a／draft。過程檔禁寫「跳過 2c」「Exit 才合併」。
  Design Boundary(最小子集):仍只改 check-stage67 填檔牙;7-review 擁有人填的恢復選擇。Interface 不變。Test seam = rebind-sha 與 item-fail 兩份 fixture。

## T-3 放過未宣稱的 N_A_NO_INCOMING 與未勾 draft
- [ ] 未完成
- Covers: R-2 / S-2.1, S-2.2
- Files: scripts/check-stage67-enforcement.sh, scripts/test-already-synced-filled.sh, scripts/fixtures/already-synced-filled/na-incoming.md, scripts/fixtures/already-synced-filled/draft-unclaimed.md
- Verify: `n=$(bash scripts/test-already-synced-filled.sh --group no-fire -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-already-synced-filled.sh --group no-fire`
  期望:n-a fixture(`N_A_NO_INCOMING`、無 ALREADY_SYNCED 作廢句)→ exit 0 且輸出含 `no-fire` 與 `N_A_NO_INCOMING`;draft fixture(`status: draft`、2c 未勾、`verdict` 空、無 `結論:STATUS=ALREADY_SYNCED`)→ exit 0 且輸出含 `no-fire` 與 `draft`。開工前原樣跑:缺測試腳本 → exit 127。③綠不了但方向對。
- Blocked-by: T-1
- Intent: 零新 commit 記 n-a、或還在填的 draft,不會被這顆牙提前擋住 —— 日常 n-a 可以直接進 2d,draft 可以繼續填。改的是發動時機,不是放寬 void-only。不會「見到 ALREADY_SYNCED 四個字就紅」。
- Boundaries: 發動條件鎖定正文有 `ALREADY_SYNCED` **且**已宣稱(2c `[x]`、或 `結論:STATUS=ALREADY_SYNCED`、或 `verdict: PASS`、或 `status: approved`)。未宣稱不發動。禁把未勾草稿當成已送 G3。禁第二套入口。過程檔禁寫「跳過 2c」「Exit 才合併」。
  Design Boundary(最小子集):同一填檔牙模組加 no-fire 分支;不擁有整合腳本 STATUS 名稱。Error seam = 未宣稱 → `no-fire`。Test seam = na-incoming 與 draft-unclaimed。

## T-4 腳本 GUIDANCE 寫出恢復下一步並改掉 Exit Checklist 檔頭
- [ ] 未完成
- Covers: R-1 / S-1.4; R-3 / S-3.2; R-4 / S-4.3
- Files: scripts/devflow-integration-regression.sh, docs/dev/tools/devflow-integration-regression.sh, scripts/test-already-synced-filled.sh
- Verify: `n=$(bash scripts/test-already-synced-filled.sh --group guidance -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-already-synced-filled.sh --group guidance`
  期望:兩份腳本 GUIDANCE 都含「重綁」或「重跑 Final Fresh」,且含「FAIL」,不得只說「輸出不算數」;兩份檔頭不再自稱 Exit Checklist 計算工具,改成「步 2c 整合回歸,Fresh 之前,不是 Exit 程序」或同等;STATUS 名稱與 exit `0`／`10`／`11`／`2` 不變;檔內仍有「絕不動樹」。開工前原樣跑:缺測試腳本 → exit 127。③綠不了但方向對。
- Blocked-by: —
- Intent: 人跑到 `ALREADY_SYNCED` 時,螢幕上的下一步是「重綁或 FAIL」,檔頭也不再把這支腳本講成 Exit 程序。日常少一次「以為寫了不算數就能勾」。改的是兩份腳本的人讀字(正本與散發必須一起改,parity 才綠)。不會改演算法、不會自動 merge／重綁、不會把 ALREADY_SYNCED 改成自動 FAIL。
- Boundaries: 只准改檔頭與 GUIDANCE 字串。禁動 `sys.exit(code)` 與 STATUS 集合。禁在腳本裡 merge／rebase／checkout。S-3.2 的 manifest 句留給 T-5。HISTORY／dispatch 不改。過程檔禁寫「跳過 2c」「Exit 才合併」。
  Design Boundary(最小子集):整合腳本擁有三 SHA 與 STATUS 名稱,仍只算只判。活教師檔頭改口不得重編號 2c。Compatibility = GUIDANCE 加恢復句、exit 碼相容。

## T-5 改口 example、manifest 與衍生 fixture 並讓活路徑 needle 歸零
- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4
- Files: example/contract-expiry-reminder/7-review.md, example/contract-expiry-reminder/4-spec.md, manifests/p4-gauntlet-gates.md, scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md, scripts/test-already-synced-filled.sh
- Verify: `n=$(bash scripts/test-already-synced-filled.sh --group live-teacher -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-already-synced-filled.sh --group live-teacher`
  期望:example 兩檔無「執行清單 2c 的 Final Fresh」與「執行清單 2c gauntlet」(若仍指 Fresh／gauntlet 則寫 2d);manifest 無「執行清單 2c 的文檔化命令」(改 2d);衍生 fixture 無「2c gauntlet」且 `bash scripts/check-spec-gate.sh scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md` 仍 exit 1;活路徑聯集 `rg -n '執行清單 2c 的 Final Fresh|Exit Checklist.*整合回歸.*計算工具'` 零命中。開工前原樣跑:缺測試腳本 → exit 127。③綠不了但方向對。
- Blocked-by: T-4
- Intent: 採用者打開完整範例或 gauntlet manifest,抄到的是 2c 整合 → 2d Fresh,不是 2c = Fresh。日常少一次被舊樣張帶偏。改的是教師編號與那根衍生針,不是整份 Stage 7 清單重編號。不會改 HISTORY／dispatch／stage7-loop,也不會讓 spec-gate 負向 fixture 因改序號而假綠。
- Boundaries: Fresh／gauntlet 只從 2c 改 2d;2c 仍叫整合回歸。example 與 `spec-gate-dd-subsection` fixture 必須同一 T 改口。死紀錄路徑不在聯集。S-3.2 腳本檔頭已由 T-4 改;本 T 腳本只准被 S-3.4 聯集掃到、不再改演算法。過程檔禁寫「跳過 2c」「Exit 才合併」。
  Design Boundary(最小子集):活教師各檔擁有自己的字面;example 與 fixture 同一 T。禁改 HISTORY／dispatch。禁重編號 2c。Test seam = 指定 `rg` + spec-gate 負向仍 exit 1。

## T-6 保留 2c 編號並讓既有模板牙三支仍綠
- [ ] 未完成
- Covers: R-4 / S-4.1, S-4.2
- Files: scripts/test-already-synced-filled.sh
- Verify: `n=$(bash scripts/test-already-synced-filled.sh --group existing-teeth -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-already-synced-filled.sh --group existing-teeth`
  期望:三案皆在 —— `_templates/7-review.md` 頂註「整合回歸」偏移 <「Final Fresh Run」、2c 標題仍含「整合回歸」、Exit 無「合併它印的」;`bash scripts/check-stage67-enforcement.sh`、`bash scripts/check-integration-regression-guard.sh`、`bash scripts/test-evidence-gauntlet.sh` 皆 exit 0;既有 ST 模板順序項未被刪。開工前原樣跑:缺測試腳本 → exit 127。③綠不了但方向對(本組落地後才有鑑別力;tip 上三支牙本身已綠,見下確認紀錄)。
- Blocked-by: T-1, T-2, T-3, T-4, T-5
- Intent: 填檔牙與活教師改完之後,舊的模板順序牙還在、還綠 —— 日常回歸不會因為這次射程延伸而被拆掉。改的是確認,不是重寫已搬的 2c 散文。不會為了新牙刪 ST 項,也不會重編號。
- Boundaries: 本 T 只加測試組、不改 `_templates/7-review.md` 正文、不改三支既有守衛的通過條件去「改鬆」。禁重編號。禁把 ALREADY_SYNCED 自動當 FAIL。過程檔禁寫「跳過 2c」「Exit 才合併」。
  Design Boundary(最小子集):純驗證層。不新增模組依賴、不改 Data owner。必須維持既有 ST／guard／gauntlet Interface。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential,不啟 parallel | tip 缺省 sequential;parallel 須明示。T-1～T-3 同檔 `check-stage67-enforcement.sh`;T-5 的 S-3.4 聯集含 T-4 改的腳本。唯一能平行的是 T-1∥T-4,不值得開 parallel 引擎 | `_templates/5-tasks.md` execution.mode;4-spec Dependencies | 為 T-1∥T-4 開 parallel |
| T-2 合併 S-1.2+S-1.3 | 同一支檢查、同一種可觀測行為(恢復路徑綠),兩份 fixture。分開會變成按案例切層 | 4-spec S-1.2／S-1.3 同一入口 | 各 S 一 T |
| T-3 合併 S-2.1+S-2.2 | 同一發動時機、同一 `no-fire` 語意 | 4-spec R-2 | 各 S 一 T |
| T-4 合併 GUIDANCE+檔頭+演算法不變 | 可觀測行為是「腳本這份教師」:人讀字對、exit 碼仍舊。三個 S 碰同一對檔 | 4-spec S-1.4／S-3.2 腳本側／S-4.3 | GUIDANCE 與檔頭拆 T(Files 重疊) |
| T-5 一次改 example+manifest+fixture | DD-6:衍生 fixture 與 example 同一 T;S-3.4 聯集要等檔頭先改(Blocked-by T-4) | 4-spec S-3.3／DD-6 | fixture 另 T(不同步假綠) |
| R-5 不進本站 T | owner brief「AS-1 tooth + live-teacher only」;4-spec 寫明 R-5 真跑留後續 hop,S-5.1 要等本 slug 7-review。S-5.3 降成每個 T 的 Boundaries 禁令 | 4-spec:221,329,393;本 hop brief | 現在寫 S-5.1／S-5.2 實作 T(沒有 7-review 可測) |

## 確認紀錄
- G2 | 2026-09-12 | tip `6b49d95`(#216)4-spec 仍 draft／verdict 空。owner 口頭 G2 PASS 2026-09-12,本站不擋、不回寫 4-spec。
- R/S 盤點 | 2026-09-12 | R-1 S-1.1～S-1.4;R-2 S-2.1～S-2.2;R-3 S-3.1～S-3.4;R-4 S-4.1～S-4.3 由 T-1～T-6 承接。R-5 S-5.1～S-5.3 不進本切片(見 Split Decisions)。
- 切 T | 2026-09-12 | tracer = T-1 void-only 端到端;T-2／T-3 加厚牙;T-4／T-5 第二條縱切(腳本教師→文件教師);T-6 回歸。無 DB→Repo→UI 切層。
- Verify 開工前原樣跑 | 2026-09-12 | 六條 Verify 皆 `bash: scripts/test-already-synced-filled.sh: No such file or directory`(exit 127)。③綠不了但方向對。tip 上既有三支牙本身已綠(`check-stage67` 73 項 exit 0;`check-integration-regression-guard` exit 0),所以 T-6 落地後才有鑑別力。
- sequential | 2026-09-12 | 明示 `execution.mode: sequential`,理由見 Split Decisions。
- twin | 2026-09-12 | `scripts/build-stage5-html.py --action` 後 `scripts/build-gate-twin.py` 產執行板。頂區五格／6 張可勾卡／Boundaries `<details>`／`#dag` 三波(T-1∥T-4 → T-2·T-3·T-5 → T-6)皆在。`parse_5_tasks` errors 空;`check-task-slicing` 6 T、0 可疑。
- 定稿 | 2026-09-12 | frontmatter status=approved(第 5 站非 gate;owner 預核中間站至 Stage 7)。不代填 G3。
