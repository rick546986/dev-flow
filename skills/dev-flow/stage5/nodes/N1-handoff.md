# N1-handoff — 接手盤點

## 進條件

`docs/dev/<slug>/4-spec.md` 在,且 frontmatter status=approved(G2 過)。
缺 → 本節點不是入口,退回第 4 站。不要寫 `5-tasks.md`。

## 讀什麼

只讀 `4-spec.md` 的 R/S 全集(含 Verification Profile 與 Design Boundary
Contract 狀態)。對話不是契約,不讀 1/2/3。
乘客清單正本是 `_templates/5-tasks.md` 頂註 0–6,本檔不重抄步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `5-tasks.md`。禁止第二份 `5-tasks*.md`。
本機游標(現在節點)只留在 `.devstage5-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

核前站:G2 是否過(4-spec status=approved),再把 R/S 全集清點回報 —— 建 todo
一 T 一項的盤點基礎在這裡打底,不是在切 T 的時候邊想邊補。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage5-graph.sh --write-cursor N1-handoff`。

## 完成條件

G2 過(approved 已核對)+ R/S 全集清點回報過。本機游標在 N1-handoff。

## 下一跳

S1-slice
