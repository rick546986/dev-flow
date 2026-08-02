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
>   直接原料;守衛只解析必填四欄,這兩欄不影響 scope。
> - 一個 T 一個關注點:Files 超過 ~5 檔或 Verify 要跑兩套不相干指令 → 拆 T。
>   超標拆分優先按子行為拆,例如讀/寫路徑、成功/例外路徑;不得優先按架構層拆。
>
> **Design Boundary 摘錄規則(條件式;沿用既有 `Boundaries:` 欄,不新增 Task 欄位)**:
> 當 4-spec 的 Design Boundary Contract 為 `applicable` 時,每個相關 T 的 `Boundaries:`
> 必須摘錄**與該 T 有關的最小限制**,涵蓋(該 T 用得到的才寫,用不到的不列):
> - 允許修改的 Module。
> - 禁止新增的依賴方向。
> - 不得跨越的 Data Ownership。
> - 必須維持的 Interface。
> - Transaction／Consistency 限制。
> - Error／State Test Seam。
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
