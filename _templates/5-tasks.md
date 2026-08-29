---
feature: <slug>
stage: 5-tasks
status: draft
owner:
updated:
execution:                              # 選配;整塊刪除 = 舊 sequential 行為,一字不變
  mode: sequential                      # sequential(缺省)| parallel(並行須明確啟用,不自動套用)
  max_parallel_tasks: 3                 # 選配;parallel 時同一 Wave 的 T 數上限(缺省 3)
  rebuild_integration_on_rework: true   # 選配;rework 後重建 integration branch(缺省 true)
---

# 5. 任務

> 用途:把 4-spec 切成可勾選、可驗證的實作單。
> 本階段固定產出:`5-tasks.md`(本模板全節)+ `5-tasks.html`(tasks 定稿供派工時
> 必產;必含 T 依賴 DAG,ASCII 天生適合)。
>
> ## 5-tasks twin 是**執行板**,不是審查介面(README §6)
>
> 不是 gate 站,但要讓人照著動工,不是 md 直轉攤平。四件事缺一不可,**產 html
> 時逐項對照,缺一項就是沒做完**:
>
> | | 要求 | 這一站的內容 |
> |---|---|---|
> | 1 | **動線頂區五格**,每格一句話 + 可點跳轉 | 狀態(frontmatter)/ 任務(幾個 T + 幾條缺必填欄)/ 模式(execution.mode,未標=sequential)/ 依賴(幾條 Blocked-by 邊)/ 進度(可勾計數) |
> | 2 | **任務卡逐條可勾**,缺必填欄直接在卡上現形 | 每個 T 一張卡(Covers/Files/Verify/Blocked-by 對齊、Intent 獨立標色);**六欄必填**(Covers/Files/Verify/Blocked-by/Intent/Boundaries)缺任一即紅底,格式同 K-7;Owner 選配 |
> | 3 | **Boundaries 摺疊**(`<details>`,預設收合、內容零刪減) | 每張 T 卡內建 `<details>`,原文零刪減 |
> | 4 | **依賴 DAG 由 Blocked-by 自動衍生**(ASCII 波次,拓撲分波) | `#dag` 區塊;引用不存在的 T 或成環一律 fail-loud(stderr 警告),不擋產出 |
>
> ⚠️ twin 的「六欄必填」是**審查提示**(紅底現形),不是 Stage 6 scope guard 的機器
> gate——機器(`contract_ref.py`)仍只吃 Covers/Files/Verify/Blocked-by 四欄
> (下面「T 自足律」講的就是這四欄);Intent/Boundaries 缺欄不會被 Stage 6 拒絕,
> 但 twin 仍標紅底,因為這兩欄是動工前必讀的資訊,不是機器判準。
>
> 產生方式:`docs/dev/tools/build-gate-twin.py <專案根> <slug> 5-tasks`
> (母版在 `scripts/`)。它讀 md 逐條解析,不手抄;解析不到任何一個 T 會直接失敗。
>
> 審查頁 chrome／任務總表版面正本:`notes/design/stage5-review-ui-contract.md`
> (與 `notes/design/vbox-fig-contract.md` 並列;本輪不改 twin)。
> 審頁產檔器:`scripts/build-stage5-html.py`(--action 授權;`.r-block` 卡、
> 標題不要底線、T-n＋標題＋未完成同一 `.r-head` nowrap、任務總表前兩欄
> nowrap、有前提節就出前提卡、卡文全寬 wrap)。不要在 5-tasks
> 加「提交判定」,不要手包 html-shell。
>
> 順序 = **tracer bullet**:先打通最薄的端到端縱切,再逐層加厚。
> 禁整份按 DB→Repo→Service→API→UI 逐層分 T。每個 T 必須能回答:
> 「完成後,使用者或系統多了什麼可觀測行為?」答不出即為水平切層徵兆,
> 應與相鄰 T 合併或重新界定。
> 每個 `## T-n` 必填 Covers、Files、Verify、Blocked-by;Covers 標 R/S id(追溯鏈)。
> Files 一律以 Git repository root 為相對根(例:`src/api/export.ts`);可寫 `./src/a.py`(會正規化),禁絕對路徑、`..` 與 root 條目。
>
> **T 自足律(為了丟給 agent 不辨識不清)**:每個 T 單獨拿出來,搭配它 Covers 的
> S 原文,執行者就能動工 —— 不需翻其他 T、不需讀 1/2/3。寫法紀律:
> - 標題 = 動詞開頭的一句完成式(「建 ent schema 十二張」,不是「schema 相關」)。
> - Intent 一句話寫「這個 T 做完,系統多了什麼可觀測行為」;Boundaries 寫硬約束/
>   禁區(照哪個既有 pattern、不准動什麼),無則寫「—」。兩欄是派工 prompt 的
>   直接原料;守衛只解析必填四欄,這兩欄**本身**不影響 scope —— 但見下一條的續行禁令。
> - **續行禁令(保留欄名不得被遮蔽)**:`Intent:`／`Boundaries:` 的續行與子項
>   **不得**以保留欄名開頭 —— `- Covers:`、`- Files:`、`- Verify:`、`- Blocked-by:`、
>   `- Integrate-after:`、`- Risk:`、`- Review-mode:`、`- Semantic-conflicts-with:`、
>   `- Intent:`、`- Boundaries:`、`- Owner:`(縮排幾層都算)。
>   parser 認欄位是「行內任意縮排 + `- <欄名>:`」,寫成子項會被當作該 T 的同名欄位,
>   把真正的 `Files:`／`Verify:` 換掉 —— `Files` 正是 Stage 6 scope guard 的唯一依據。
>   續行請用純文字或非保留字開頭(例:`  Design Boundary(…):…`)。
>   違反時 `contract_ref.py` 會回報「重複保留欄」並 fail-closed(start 拒啟),不再靜默覆蓋。
> - 一個 T 一個關注點:Files 超過 ~5 檔或 Verify 要跑兩套不相干指令 → 拆 T。
> - ⚠️ **規則:`Verify:` 必須是單行、可原樣貼進 shell 的純指令**。說明、期望輸出、
>   前置動作一律寫在下一行,不得混進同一行。
>   **為什麼**:`#` 會吞掉同行其後全部內容(shell 註解語法),把「指令 + 中文說明」
>   硬塞成一行,輕則說明文字混進指令,重則 `#` 之後原本要跑的檢查被整段吃掉、從未執行。
>   **背景案例(佐證,不是要照做的事)**:2026-08 python-prism 實測 18 個 T 有 17 個
>   `Verify:` 欄被中文說明汙染,如 `` `pytest -k "S4_ or S3_4"`;S4.1 需實檔(3.9 GB BAM) ``;
>   另有專案把 `Verify:` 寫成多行 fenced code block,解析器只吃單行,一個字都抓不到。
> - ⚠️ **規則:`Verify` 用 `-run`/`-k`/`--filter` 這類「篩選子集」的參數時,必須自帶
>   案例數斷言**,且期望案例數**開工前就先寫下來**(`-ge 1` 是下限,不是免死金牌)。
>   **強制形狀**(語言不同照抄同一個骨架:先數、再比、再跑真檢查):
>   ```
>   n=$(<測試指令> -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge <期望案例數> && <其餘檢查>
>   ```
>   **為什麼**:篩選器沒匹配到任何測試時 runner 回 exit 0,於是「一個測試都沒跑」與
>   「全部通過」在 exit code 上完全一樣。這欄本來要證明「這個 T 做完了」,
>   沒有計數就退化成「這個 T 的測試不存在也算過」。
>   **背景案例(佐證,不是要照做的事)**:2026-08 order-intake 實測,T-25 的 Verify
>   在**還沒寫任何測試**的 HEAD 上跑出 `=== RUN` 0 行、exit 0、印出 `T-25 PASS`。
> - ⚠️ **`Verify` 開工前必須原樣跑一次**(還沒動任何碼時)。三種結果各有處置:
>   ①**已經綠** → 這欄不具鑑別力,補計數或改條件,別直接開工;
>   ②**不可能綠**(要求的零命中在正確實作下必然命中)→ 停,修欄位,記 L1;
>   ③**綠不了但方向對** → 正常,開工。
> - 超過上面「一個 T 一個關注點」的門檻(Files >~5 檔,或 Verify 要跑兩套不相干指令)
>   而要拆 T 時:優先按子行為拆,例如讀/寫路徑、成功/例外路徑;不得優先按架構層拆。
> - ⚠️ **每個 T 必須有一個能 RED→GREEN 的測試,不得只寫執行指令**——純 migration／infra
>   型 T(建表、加欄、建索引這類無業務邏輯可斷言的 T)一樣要有測試,只是測的是**形狀**:
>   表/欄位是否存在、型別是否正確、索引/約束是否建立,而不是「migrate 指令 exit 0 就算過」。
>   範例(僅供閱讀對照欄位形狀,非真實任務):一個「建 `orders_status` 表」的 infra 型 T,
>   `Files: migrations/0007_orders_status.sql, internal/repo/orders_status_schema_test.go`、
>   `Verify: n=$(go test ./internal/repo/... -run TestOrdersStatusSchema_S5 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
>   (該測試斷言:`orders_status` 表存在、`status` 欄位為 `text` 型別、
>   `idx_orders_status` 索引存在、`orders_status_check` 約束存在——四項缺一即 FAIL)。
> - ⚠️ **測試檔路徑也要列進 `Files`**——worker 寫測試就是寫檔,測試檔不在 `Files` 聯集內
>   會被 Stage 6 scope guard 當場擋死(PreToolUse hook 在 candidate 產出前就擋,不會等到
>   T review 或 gate 才發現)。幾乎每個 T 的 Verify 都在跑測試,對應的測試檔
>   (`*_test.go`／`*.test.tsx`／`*.spec.ts` 等)必須跟業務碼一起列進本 T 的 `Files`。
> - **`Files` 該含哪些測試檔的判準(D-39 四象限,order-intake 實測歸納)**:
>
>   | 規則性質 | 用什麼測 | 為什麼 |
>   |---|---|---|
>   | 缺席(沒發出某句 SQL) | sqlmock／白箱 | 真 DB 分不出「發了但 WHERE 沒命中」與「根本沒發」 |
>   | 順序(有沒有 ORDER BY) | sqlmock／白箱 | 小資料量下 DB 幾乎總是回插入順序,真 DB 斷言恆綠 |
>   | 可觀測的結果(讀回來有沒有那筆) | integration | 白箱佈置多句 eager-load 成本高又脆弱 |
>   | 單句 SQL 的 WHERE／綁定值 | sqlmock／白箱 | 便宜、精確、不需要 Docker |
>
>   例:規則寫在 SQL 的 `WHERE`／`SET` 裡 → `Files` 該含 repository 層測試檔
>   (如 `internal/repo/xxx_test.go`)——service 層之下用 fake repository 時,
>   這類規則完全看不出來,突變測試會一路全綠。
>
> **Design Boundary 摘錄規則(條件式;沿用既有 `Boundaries:` 欄,不新增 Task 欄位)**:
> 當 4-spec 的 Design Boundary Contract 為 `applicable` 時,每個相關 T 的 `Boundaries:`
> 必須摘錄**與該 T 有關的最小限制**,涵蓋:
> - 允許修改的 Module。
> - 禁止新增的依賴方向。
> - 不得跨越的 Data Ownership。
> - 必須維持的 Interface。
> - Transaction／Consistency 限制。
> - Error／State Test Seam。
>
> 「最小」是指**只挑與該 T 相關的那幾條**,不是「可以省略負向約束」——
> `Forbidden dependencies`、「不得跨越」「必須維持」這類**禁區恰恰是本欄的重點**:
> 它們正是該 T 最可能誤踩、而 Stage 6 的 Design Boundary Check ①～④要拿來對照的基準。
> 該 T 真的碰不到的條目才略過,碰得到就必須寫進來,否則 reviewer 只能回頭讀 4-spec 全文
> (那就違反 T 自足律)。
>
> 上列六項是**要涵蓋的內容**,不是要照抄的 bullet 標題 —— 摘錄請寫成續行純文字,
> **不得**把「允許修改的 Module」寫成 `- Files:`、把「Test Seam」寫成 `- Verify:`
> 之類的保留欄名子項(理由與完整清單見上方「續行禁令」)。
>
> **不得把完整 Design Boundary Contract 複製進每個 T**,只摘錄該 T 的最小子集 ——
> 執行者靠這一欄就知道自己的禁區,不必回頭讀 4-spec 全文。契約為 `n-a` 時本規則不適用,
> `Boundaries:` 照舊(有硬約束就寫,無則 `—`)。語意正本:`notes/design/design-boundary-contract.md`。
>
> **Task Context Packet 規則(真實世界互動)**:
> - 每個 Task 只帶與該 T 有關的**最小** Operational Context 子集(從 4-spec 該 T Covers
>   的 S 摘錄):Actor、Goal、Human decision、Authority、External dependency、
>   Out-of-system action、Waiting/recovery、不得誤導使用者的事項(如:看過 ≠ 完成、
>   「已續約」僅主管可標)。
> - 禁把 1-discussion 訪談逐字稿 / 完整 Real-world Context 丟給 Haiku;執行層只吃摘錄。
>
> **並行選配欄位(僅 `execution.mode: parallel` 有執行效果;全部有缺省,舊檔零欄位
> 行為完全不變;完整契約見母版 `notes/design/parallel-stage6.md`)**:
> - `Integrate-after: T-n`(缺省 —)= **軟整合依賴**:可平行實作,但 candidate 整合
>   順序必須在指定 T 之後。`Blocked-by:` 仍是**硬執行依賴**(前置 T 未達安全狀態,
>   本 T 不得開始實作)。
> - `Risk: normal|high`(缺省 normal;判準見 4-spec Verification Profile,不另設第二套
>   分級)。本欄 = Task Risk(scope 限單一 T):Task high → 該 T 一律 dedicated review,
>   PASS 才進 integration;4-spec 的 Feature Risk = high 只升 Profile 深度與 lane,
>   不強制全部 T dedicated(兩 scope 判準同一正本,語意見母版
>   `notes/design/vnext-shared-contract.md` §3)。
> - `Review-mode: wave|dedicated`(缺省:normal→wave、high→dedicated;high 明寫 wave 非法)。
> - `Semantic-conflicts-with: T-n`(缺省 —)= 檔案不重疊但語意衝突,禁排同一 Wave。
> - **不必手排 wave**:Wave 由引擎從 Blocked-by + Files overlap 自動派生(runtime
>   資料,不回寫本檔);Files 重疊由 Scheduler 自動判,毋須人工維護 Conflicts 清單。
> - parallel 模式下 checkbox 只在該 T **ACCEPTED**(獨立 review 通過)後由派工者勾,
>   Worker 不碰本檔。
>
> 執行清單(開場第一動建成 todo;逐步達成「完成 =」才勾;禁跳項併項、禁一發全生):
> 0. 前置:4-spec 須 status=approved(G2 過);讀 4-spec 全部 R/S 建立盤點基礎,
> 建 todo 一 T 一項。完成 = approved 已核對 + R/S 全集清點回報。
> 1. 切 T:順序 = tracer bullet(先打通最薄端到端縱切,再逐層加厚);判準見上方
>    「一個 T 一個關注點」與「T 自足律」——
>    每個 T 必須答得出「完成後系統/使用者多了什麼可觀測行為」,答不出即水平切層
>    徵兆,應與相鄰 T 合併或重界定,不得整份按 DB→Repo→Service→API→UI 逐層分
>    (機械提示見 `scripts/check-task-slicing.sh`,warning-only、永不 exit 1,
>    不能取代 reviewer 判斷);每個 T 必須有一個能 RED→GREEN 的測試,純
>    migration／infra 型 T 一樣要測,只是測形狀(見上「T 自足律」)。
>    完成 = 每個 T 皆答得出可觀測行為、無按架構層整份切分。
> 2. 填欄:Covers 標 R/S id 且全 S 皆被至少一個 T 承接(追溯鏈頂端);Files 以 Git
>    repository root 相對路徑列出,含對應測試檔(D-39 四象限判準見上「Files 該含
>    哪些測試檔」節);Verify 單行純指令,`-run`/`-k`/`--filter` 篩選器須帶案例數
>    斷言(強制形狀見上方「篩選子集必須自帶案例數斷言」那條的骨架),開工前先原樣跑一次,
>    依「①已經綠→補計數或改條件
>    ②不可能綠→停,修欄位,記 L1③綠不了但方向對→正常開工」三種結果處置;Intent
>    一句寫可觀測行為,Boundaries 寫硬約束/禁區,Design Boundary Contract 為
>    `applicable` 時比照「Design Boundary 摘錄規則」摘錄該 T 最小子集;續行不得
>    以保留欄名開頭(見上方「續行禁令」)。
>    完成 = 四必填欄齊備、Verify 已原樣跑過一次並記錄結果、Intent/Boundaries 各
>    一句到位。
> 3. 依賴:填 `Blocked-by`(硬執行依賴,拓撲序不成環);parallel 模式選配填
>    `Integrate-after`(軟整合依賴)/`Risk`/`Review-mode`/`Semantic-conflicts-with`,
>    不必手排 wave——Wave 由引擎從 Blocked-by + Files overlap 自動派生(見上「並行
>    選配欄位」)。完成 = 每個 T 的 Blocked-by 已核對、拓撲序無誤。
> 4. 自檢:逐 T 核對四必填欄(Covers/Files/Verify/Blocked-by)齊全、續行未踩保留
>    欄名——缺一欄或踩中,`contract_ref.py` 的 `parse_5_tasks` 即判為 parse
>    error,`start` fail-closed 拒啟(見上「續行禁令」)。完成 = 逐 T 核對零缺欄、
>    零保留欄遮蔽。
> 5. 產執行板 twin 看一眼:`docs/dev/tools/build-gate-twin.py <專案根> <slug>
>    5-tasks`(母版在 `scripts/`)產 `5-tasks.html`;它讀 md 逐條解析,不手抄,
>    解析不到任何一個 T 會直接失敗。核對動線頂區五格、任務卡逐條可勾(缺必填欄
>    紅底現形)、Boundaries 摺疊、依賴 DAG 四件事皆在(見上「5-tasks twin 是執行
>    板」節)。完成 = twin 產出且四件事逐項核對過。
> 6. 定稿:frontmatter status 由 draft 轉 approved(5-tasks 不是 gate 站,無 G
>    編號、免 reviewer 核准,owner 自行定案即可)。完成 = status 已更新 + twin
>    與 md 一致。

## T-1 <標題:動詞開頭一句完成式>
- [ ] 完成
- Covers: R-1 / S-1
- Files: <預計動的檔>
- Verify: `<指令>`
- Blocked-by: —
<!-- 改 Blocked-by 必須重產 html #dag。圖對文字牙比的是各 T-id＋Blocked-by 邊集合
     對 #dag 裡的 T-n／←(T-n),不比手畫的 T-1 連到 T-2。 -->
- Intent: <做完系統多了什麼可觀測行為,一句>
- Boundaries: <硬約束/禁區;無則 —>
- Owner:(多人才填)

## T-2 <標題>
- [ ] 完成
- Covers: R-1 / S-2
- Files: <預計動的檔>
- Verify: `<指令>`
- Blocked-by: T-1
- Intent: <做完系統多了什麼可觀測行為,一句>
- Boundaries: —

## Split Decisions(拆分自判,選配)
<!-- 拆分/排序不顯然時記:決策 | 理由 | 依據 | 棄項;顯然就整節留白。
     「依據」寫得出出處就寫 `檔:行` 或指令輸出;寫不出就寫 `[Assumption]`
     (同 1-discussion 的 [Assumption] 規則,四份自判表同一套寫法)。 -->
