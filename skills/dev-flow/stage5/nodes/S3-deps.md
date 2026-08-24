# S3-deps — 依賴

## 進條件

S2-fields 完成(Covers／Files／Verify 已填,Intent／Boundaries 各一句)。
游標在 S2-fields。`5-tasks.md` 只有一份。

## 讀什麼

已填欄的各 T,以及 `4-spec.md` 的 Verification Profile —— `Risk` 判準同一正本,
本站不另設第二套分級。並行選配欄位的契約正本是 `_templates/5-tasks.md` 頂註與
`notes/design/parallel-stage6.md`,本檔不重抄。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/5-tasks.md` 的依賴欄位,不另存。
禁止第二份 `5-tasks*.md`。`write_mode: overwrite`。本機游標不進 Git。

## 做什麼

逐 T 填 `Blocked-by`(硬執行依賴:前置 T 未達安全狀態,本 T 不得開始實作),核拓撲序
不成環、不指向不存在的 T。`execution.mode: parallel` 才補
`Integrate-after`(軟整合依賴)／`Risk`／`Review-mode`／`Semantic-conflicts-with`;
Wave 由既有引擎從 `Blocked-by` + Files overlap 自動派生,不在本檔手排,也不動平行引擎。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage5-graph.sh --write-cursor S3-deps`。

## 完成條件

每個 T 的 `Blocked-by` 已核對、拓撲序無誤(無自指、無環、無指向不存在的 T)。
只有一份 `5-tasks.md`。本機游標在 S3-deps。

## 下一跳

N4-write-md
