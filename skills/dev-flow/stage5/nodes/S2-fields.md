# S2-fields — 填欄

## 進條件

S1-slice 完成(T 已切、順序是 tracer bullet)。游標在 S1-slice。
`5-tasks.md` 只有一份。

## 讀什麼

`4-spec.md` 的 R/S id(追溯鏈頂端)、Design Boundary Contract 狀態與該 T 相關的
Operational Context。四必填欄、續行禁令、`Verify` 三律的條文正本是
相對 DEVFLOW_ROOT 的 `_templates/5-tasks.md` 頂註,本檔不重抄。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/5-tasks.md` 的各 T 欄位,不另存。
禁止第二份 `5-tasks*.md`。`write_mode: overwrite`。本機游標不進 Git。

## 做什麼

逐 T 填 Covers(標 R/S id,全 S 都要被至少一個 T 承接)、Files(以 Git repository
root 為相對根,含對應測試檔)、Verify(單行純指令;用 `-run`／`-k`／`--filter`
篩子集時自帶案例數斷言,開工前原樣跑一次並記錄結果),再補 Intent 與 Boundaries
各一句。Design Boundary Contract 為 `applicable` 時,Boundaries 只摘該 T 碰得到的
最小子集,不整份複製。
續行與子項不得以保留欄名開頭 —— 寫成 `- Files:` 之類會被 parser 當同名欄位,把真正
的 `Files:` 換掉。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage5-graph.sh --write-cursor S2-fields`。

## 完成條件

每個 T 的 Covers／Files／Verify 齊備、Verify 已原樣跑過一次並記錄結果、
Intent／Boundaries 各一句到位、續行未踩保留欄名。只有一份 `5-tasks.md`。
本機游標在 S2-fields。

## 下一跳

S3-deps
