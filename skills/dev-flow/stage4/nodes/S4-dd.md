# S4-dd — Drafting Decisions 清點

## 進條件

S3a／S3b／S3c 都完成:四小節齊、Profile 與 Design Boundary 有結論、
Stage 3 對帳逐場有下落。游標在 S3c-stage3。

## 讀什麼

全份已落檔內容(R／S／四小節／Profile／Design Boundary／對帳結果)。
兩層分級判準與「依據」欄的寫法正本在相對 DEVFLOW_ROOT 的 `_templates/4-spec.md` Drafting Decisions
節頂註,本檔不抄乘客步原文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/4-spec.md` 的 Drafting Decisions 兩層,不另存。
禁止第二份 `4-spec*.md`。`write_mode: overwrite`。本機游標不進 Git。

## 做什麼

草擬時自己拍的板逐條進上層表(決定了什麼|為什麼|依據|若被推翻會怎樣|狀態),
純內部技術選擇進下層清單,拿不準放哪層一律放上層。
全文掃 TBD／之後再說／實作再定 —— 命中即轉 DD 或退回提問,不准留在正文。
推翻已核 Decision 的條目不是合法 DD,回第 2 站。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage4-graph.sh --write-cursor S4-dd`。

## 完成條件

掃描零殘留,每條 DD 的「依據」欄寫得出出處或標 `[Assumption]`。
推翻已核 Decision 不是合法 DD。只有一份 `4-spec.md`。本機游標在 S4-dd。

## 下一跳

N5-write-md
