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
> 審碼(鎖死,不是口味):本檔不能只列函式名＋行號表。每個這輪改過的函式必須
> 自己一塊 hunk:標題帶 T-n、上方一句「改什麼」、底下一行「關聯」、
> 然後才是色碼 hunk(綠 `.ln.add`／`--ok-soft`;舊行未知不准發明 minus)。
> 不要整檔貼上,不要變成第二份正本。產檔器吃 ## Diff:
> `scripts/build-stage6-html.py`(bookkeeping commit 前跑;不要手包 html-shell)。
> 正本:`notes/design/stage5-review-ui-contract.md` §第6站審碼。
> TDD 規則(superpowers):每個 S-id **先寫失敗測試**(RED,貼輸出摘要)→ 最小實作到
> GREEN → refactor 保綠。沒看過測試失敗 = 不知道它測對東西。
> dev-run 引擎案:「執行軌跡」節由 `devflow-obs` 從 ledger 衍生,禁手填;
> 手動實作該節留白照舊。
>
> 執行清單(開場第一動建成 todo;逐步達成「完成 =」才勾;禁跳項、禁併 T):
> 0. 起手式,分三小步(0a 開 branch 與錨點/0b worktree 隔離確認/0c 守衛與 doctor
>    自檢),各自查驗完成才算這步完成:
>    **0a. 開 branch 與錨點**:圍欄自查 —— 只讀 4-spec/5-tasks/6-notes/長期記憶查詢結果/
>    living spec,禁讀 1/2/3(要翻才寫得出 = spec 不完整 → 停,回 G2)。開 feature
>    branch —— **開 branch 與記分岔錨點是同一個動作的兩半,中間不准插別的事**,
>    照下面四步做,不可拆。錨點 `FORK_INTEGRATION_SHA` = 開這條 branch 的當下整合
>    分支(`develop` 或 `main`,依專案)的最新點;Stage 7 的整合回歸工具靠它才算
>    得出「分岔之後對方多了什麼」—— 事後回頭查會查到已經前進過的點,錨點當場
>    失效:
>    ```bash
>    git fetch <remote>
>    FORK=$(git rev-parse --verify "refs/remotes/<remote>/<整合分支>^{commit}")
>    git switch -c <feature-branch> "$FORK"
>    test "$(git rev-parse HEAD)" = "$FORK"   # 不相等 = 中間出過事,停下重來
>    ```
>    並行(多 feature)改用 worktree 時是**另一組四步,不是把上面那組改一個字**:
>    ```bash
>    git fetch <remote>
>    FORK=$(git rev-parse --verify "refs/remotes/<remote>/<整合分支>^{commit}")
>    git worktree add <worktree-path> -b <feature-branch> "$FORK"
>    test "$(git -C <worktree-path> rev-parse HEAD)" = "$FORK"
>    ```
>    ⚠️ 第四步一定要帶 `-C <worktree-path>` —— 少了它,`git rev-parse HEAD` 讀的是
>    你現在站的那個 checkout,不是剛建好的 worktree:驗證會通過,但它驗的是別人,
>    新 worktree 建在錯的點上也照樣放行。`git worktree add` 也要明示 `"$FORK"`,
>    不要讓它預設從當前 HEAD 建。四步跑完,立刻把 `$FORK` 那 40 碼用下面這個
>    逐字欄位寫進本檔(Stage 7 整合回歸工具 `--fork-sha` 吃的就是這個欄位的值):
>    ```
>    FORK_INTEGRATION_SHA: <40 碼>
>    ```
>    之後不管 merge/rebase 幾次都**不准更新它** —— 它記的是「歷史上的那個時刻」,
>    不是「現在的狀態」,一更新就退化成 merge-base,等於沒有。
>    完成 = 讀取清單回報 + branch 就位(或 worktree 建好且 HEAD 驗證通過)+
>    `FORK_INTEGRATION_SHA` 已記進本檔(40 碼全長)。
>    **0b. worktree 隔離確認**:多 feature 並行(多 worktree)另做兩件事:
>    ①STATUS.md 不在 worktree 內改 —— 它只在整合分支(`develop` 或 `main`,依專案)
>    上維護,規則與理由見 STATUS 模板頂註;②確認執行環境已隔離:容器名/對外 port
>    (兩個 worktree 同時起得來嗎?)、**資料庫**(共用同一個 DB 時,migration 版本
>    紀錄表會混進兩個 feature 的版本,導致其中一邊 apply 被拒)、快取/訊息佇列/
>    檔案上傳目錄等有狀態的外部依賴。隔離方式依專案技術棧自理,母版不規定做法 ——
>    母版規定了「並行用 worktree」,就要負責講清楚這個規定的代價,所以檢查項要管;
>    但怎麼隔離是各專案技術棧的事,母版規定做法會變成「規定了但不適用」。
>    **背景案例(佐證,不是本次要照做的事)**:實例 `atlas_schema_revisions`,
>    order-intake T-2 實踩。
>    ⚠️ **worktree 交接(並行動線的最後一步)**:上面兩件事(STATUS 在整合分支上改、
>    執行環境隔離確認)做完後,明確切進新樹:
>    ```bash
>    cd <worktree-path>          # 從這裡開始,後續所有指令都在這棵樹上跑
>    ```
>    後面的 `devflow-exec.sh status` **必須在這個目錄下跑**,它會核對 slug 與 cwd
>    相符 —— 在原 checkout 跑會核對到別的東西。
>    **worktree 合併(預期,不是 bug)**:feat worktree 產的 `docs/dev` html/md
>    會跟著 branch 走。要併回專案真正在用的整合線(常是 `develop` 與 `testing`),
>    不要把雙生頁只留在 worktree。HISTORY 出廠種子列也會跟著走,可能衝突;
>    清種子用 `history-append.sh --action factory-seed-cleanup`(不要每次 upgrade 自動跑),不要手改。
>    完成 = 執行環境隔離結果已貼進本檔:逐項寫容器名/對外 port/資料庫/快取或佇列/
>    檔案上傳目錄各自怎麼隔離的(實際值,不是「已隔離」三個字);單一 worktree、
>    沒有並行 → 寫 `n-a:本 feature 未並行`,理由要寫出來。
>    **0c. 守衛與 doctor 自檢**:⚠️ **守衛武裝自檢(硬關卡,第一動)**:跑
>    `devflow-exec.sh status`,確認 `.devflow/exec.json` **存在**且 slug 正確。
>    **沒武裝就不准開工** —— guard hook 在 `.devflow/exec.json` 不存在時是
>    **靜默沉睡**的(`devflow-lib.py::load_state` → `return None, "", ""`),
>    於是「守衛在擋」與「守衛不在」對執行者長得一模一樣:
>    圍欄②(禁讀上游)、契約防篡改、scope 守衛**三道全部不會觸發**,
>    而每一份產出看起來都一樣完整。
>    武裝不了 → **停下回報**,不要用「我會自己守 scope」代替。
>    ⚠️ **同一動作再跑 `devflow-doctor.sh`(或 `devflow-exec.sh doctor`)**:版本握手
>    fail-closed,回報 `INCOMPATIBLE` 即**停下回報**,不得略過繼續。
>    **背景案例(佐證這兩條為何是硬關卡,不是本次要照做的事)**:2026-08 order-intake
>    實測 —— ①`devflow-exec.sh` 因母版 bug 啟動不了(D-9),26 個 T 全程守衛沉睡,
>    `Files` scope 是人工比對出來的,當下沒人發現,因為沒有任何訊號;
>    ②`dev-setup` 沒散發齊 `devflow-contract.json` 與 `docs/dev/tools/`,doctor 實跑
>    直接 `⛔ INCOMPATIBLE(fail-closed)`,但整條 Stage 6→7 沒有任何一步要求跑它,
>    所以沒有人被擋。
>    完成 = `devflow-exec.sh status` 與 `devflow-doctor.sh` 兩份輸出都貼進本檔。
> 1. 接手核對:4-spec approved?5-tasks 每 T 有 Verify+Covers?缺 → 停回補。
>    建 todo 一 T 一項,照 Blocked-by 拓撲序。完成 = todo 與 5-tasks 一一對應。
> 2. 逐 T 循環,對齊指南 `#five-laws`／`#stage6` 的驗收動線(RED → GREEN → scope check → Verify →
>    independent T review → PASS → commit → 記帳),a–h 逐段對應同一條 seam:
>    a **RED**:照 Covers 先寫失敗測試(名含 S-id)→ RED 輸出貼 TDD Evidence。
>    完成 = RED 輸出已貼。
>    b **GREEN**:最小實作到 GREEN(貼輸出)→ refactor 保綠。完成 = GREEN 輸出
>    已貼且保綠。
>    c **scope check**:git status 改動檔 ⊆ 該 T 自己的 Files,超出 → L1/L2 判
>    (定義見下實作期規則)。完成 = scope 已核對(在界內,或已判 L1/L2)。
>    d **Verify**:跑該 T Verify。完成 = Verify 已跑且結果在案。
>    e **independent T review**:reviewer 必須不同於 T implementer,優先適格
>    人類,否則 fresh-context reviewer Agent;reviewer 親跑 Verify,檢查 Covers、
>    RED→GREEN 證據與該 T 自己的 Files scope,並過 Test Integrity Check 七項
>    (①刪 assertion ②放寬 assertion ③新增 skip/xfail/todo ④同步改測試+實作
>    重新定義正確性 ⑤mock 掉核心邏輯(mock 邊界可以,mock 被測物不行)⑥只追
>    coverage 無有意義 assertion ⑦沒跑的層寫成 PASS;任一命中 → FAIL);4-spec 的
>    Design Boundary Contract 為 `applicable` 時,另過 Design Boundary Check 五問
>    (全文見下方實作期規則)。FAIL → 回 a 修正並重新送審;高風險或 finding 有
>    爭議可加第二 reviewer。完成 = reviewer 給出 verdict。
>    f **PASS**:reviewer 裁決 PASS(FAIL 已在 e 處理,不下推)。完成 = verdict = PASS。
>    g **commit**:PASS 後 commit、讀出 hash。完成 = commit 已建立。
>    h **記帳**:hash 入 Progress Log + 勾 checkbox + review evidence 入
>    T Review Log。完成 = 該 T reviewer PASS + checkbox ✓ + hash 在案 + Covers
>    的每個 T × S 全有該 T 自己的 RED→GREEN 證據。
>
>    **自由選擇與偏差(條件觸發,不是每個 T 都會遇到)**:
>    - **遇到 spec 未載明的自由選擇時**(如內部命名、資料結構)→ 自己選、記一行
>      Decisions、繼續(定義見下實作期規則 Decisions 條)。完成 = 未遇到則免做;
>      遇到則已記一行 Decisions。
>    - **遇到偏差時** → 依 L1/L2 判並處置(定義見下實作期規則偏差條,含 L1 繼續
>      執行 / L2 停 / 分不清一律當 L2)。完成 = 未遇到則免做;遇到則已判級並
>      依級處置。
>
>    順序固定:RED → GREEN → scope check → Verify →
>    independent T review → PASS → commit → Progress Log + checkbox + review evidence。
> 3. 回歸:全 T 後跑既有全套,本次 S 全綠+既有全綠;紅 → 修+依偏差級記。
>    完成 = 全套**全綠**輸出摘要入本檔(紅字摘要不算完成)。
> 4. 自檢(= Self-Review 節逐問作答;Design Boundary Contract applicable 時第⑦問
>    併查邊界 drift):①每個「T × Covers S」都有含 S-id 的測試 +
>    該 T 自己的 RED/GREEN 證據(不得跨 T 共用)?
>    ②每 T 在 T Review Log 有 verdict?③每個 PASS 都早於該 T commit?④每個 FAIL
>    後有較晚 PASS,否則該 T 仍未勾、未 commit?⑤每個已完成 T 一 commit、Progress
>    Log 每列有 hash?⑥git diff --stat 檔案 ⊆ Files 聯集、Diff Budget 內?
>    ⑦Decisions/Deviations 與 diff 對得上(無 silent drift;契約 applicable 時併查:
>    模組依賴、Data Owner、Interface／Transaction／Consistency Boundary 有無未經
>    授權的改變,有則已記 L2 並回 G2)?⑧回歸綠?答不出 →
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
> - **Design Boundary Check(條件式;4-spec 的 Design Boundary Contract 為 `applicable`
>   時,每個 T 的 independent review 必過)**:不新增 Review Stage,只在既有 T Review 加五問 ——
>   ①Diff 是否引入未授權的模組依賴?②是否改變 Data Owner?③是否改變 Interface／
>   Transaction／Consistency Boundary?④是否違反 Design Constraints 的「必須／禁止」,
>   或讓某個 Known design limit 被實作悄悄「修掉」而契約沒改?⑤若①～④任一為是,
>   是否已記為 L2 並回 G2(走既有 L2 路徑,不新增 gate)?
>   ①～④對應設計契約三張表與 Design Constraints 的全部四塊(Architecture Boundaries →①②、
>   Interface & Consistency →③、Software Design 與 Design Constraints →④),不留半邊沒人查。
>   任一為「有改變且未記 L2」→ FAIL。契約為 `n-a` 時本檢查記 `n-a`。
>   Worker 只取得**與該 T 相關的 Design Boundary 子集**(來自 5-tasks 該 T 的
>   `Boundaries:` 欄),**不得因本檢查要求 Worker 回讀 Stage 1～3**(圍欄自查不變)。

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
- Test Integrity finding:<七項檢查結果;任一命中即 FAIL,無命中記 none>
- Design boundary finding:<Design Boundary Check 五問結果;4-spec 契約為 n-a 時記 n-a>
- verdict:PASS | FAIL
- correction + re-review after FAIL:<修正內容 + 後續 round 證據;無 FAIL 則 N/A>
-->

## Progress Log
<!-- 日期 | T-id | 一行;只記 T Review PASS 後做的 commit,每列含 commit hash -->

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run: <run_id>
<!-- 節首固定一行 `Run: <run_id>`;dev-run 案本節由 devflow-obs 從 ledger 衍生,禁手填。
     每 T 一列:T-id | 失敗分類(SPEC/ENV/IMPL/UNKNOWN,指南 `#five-laws` 驗證五律 5;
     全程無失敗填 —)| 模型升階史(如 haiku→sonnet)| 回合數 | 升階原因一句。
     ENV 失敗的重跑不計升階回合。升階本身 = spec 品質訊號,7-review.html 以表呈現。
     parallel 模式加記:wave 編號 | candidate SHA | gate verdict(devflow-gate-result.v1
     的 verdict)| review 途徑(wave n / dedicated);sequential 留白照舊 -->

## TDD Evidence
<!-- 每個「T × Covers S」各一筆;同一 S 在不同 T/層次的 RED→GREEN 不得共用。 -->
### T-1 / S-1
- RED: `<test cmd>` → <失敗輸出摘要>
- GREEN: `<test cmd>` → <通過輸出摘要>

## Decisions(spec 未載明的自由選擇)
<!-- 一行一個:選了什麼 + 為何 + 依據;不屬偏差,不需回審。
     「依據」寫得出出處就寫 `檔:行` 或指令輸出;寫不出就寫 `[Assumption]`
     (同 1-discussion 的 [Assumption] 規則,四份自判表同一套寫法)。 -->

## Deviations
### D-1(L1|L2)
- 現象:
- 保守選擇:
- 理由:
- 影響:T-? / R-? / S-?

## Files Changed
<!-- 對照 4-spec Diff Budget -->

## Diff(各 T commit,逐檔折疊)
<!-- 產檔器吃本節。每個這輪改過的函式自己一塊(可重複),產檔器
     `scripts/build-stage6-html.py` 解析後吐 details.hunk。schema:

     ### <fn> · `<file>` <lines>  T-n
     改什麼：<一句,這輪改了什麼,不是複述整函式>
     關聯：<對語函式／誰叫它／它叫誰;沒有就寫 —;不傾倒呼叫圖>
     ```diff
      context
     +added
     -deleted-only-if-known
     ```

     審碼(鎖死,正本 notes/design/stage5-review-ui-contract.md §第6站審碼):
     每個這輪改過的函式自己一塊,不是只列名＋行號表。標題含 T-n。
     一塊 hunk 真的同時服務兩個 T 才准帶兩個 T。
     然後才是色碼 hunk(綠 .ln.add／--ok-soft;上下文淡;舊行未知不准發明 minus)
     不要整檔貼上、不要當第二份正本。chrome 跟 2／4／5 站同一套。 -->

## Self-Review
<!-- = 執行清單步 4 的八問:逐問作答、附證據(review 時間/verdict/測試輸出/hash/diff stat),不憑印象 -->

## Review Follow-up(G3 打回時才用)
<!-- 逐 F:同意 → 改+一句為何對;不同意 → 擺論證,不盲改(禁 performative fix) -->
