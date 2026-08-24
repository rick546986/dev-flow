# S5-gate — 自檢(機械關卡先跑)

## 進條件

N5-write-md 完成:步 1–4 的內容全在同一份 `4-spec.md`。游標在 N5-write-md。
還沒落檔就跑機械關卡 = 沒有檔可讀,退回 N5-write-md。

## 讀什麼

已落檔的 `docs/dev/<slug>/4-spec.md`。C1–C5 五關的判準正本在
`scripts/check-spec-gate.sh` 本身與 `_templates/4-spec.md` 頂註第 5 步,
本檔不抄乘客步原文,也不重述關卡條文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/4-spec.md` —— 關卡紅了在原檔修,不另存修正版。
禁止第二份 `4-spec*.md`。`write_mode: overwrite`。
不改 `scripts/check-spec-gate.sh`,那支腳本只呼叫、不修。
本機游標不進 Git。

## 做什麼

先跑既有機械關卡 `scripts/check-spec-gate.sh <本檔路徑>`,紅了先修再往下。
機械過了才做人工部分:鏈檢每條驗收雛形 ≥1 個 S 承接、每 MODIFIED 有原文引用;
任一否就重寫該 S。修完重跑本節點 = 覆寫同一份,不是另存一份修正版。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage4-graph.sh --write-cursor S5-gate`。

## 完成條件

`check-spec-gate.sh` exit 0 + 逐 S 打勾 + 鏈檢清零。只有一份 `4-spec.md`。
本機游標在 S5-gate。

## 下一跳

N6-g2
