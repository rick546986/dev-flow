# S3a-close — 邊界收尾四小節

## 進條件

S2-scenarios 完成:全 R 已展開、每 S 有觀測欄。游標在 S2-scenarios。
S 還沒展開完就收邊界 = 收一個不完整的範圍,退回 S2。

## 讀什麼

已落檔的 R／S、`2-decision.md` 的 Scope 與 Success Criteria。
四小節的內容要求正本是 `_templates/4-spec.md` 頂註第 3a 步與各節頂註
(Diff Budget 的估法、Dependencies 的 justification),本檔不抄乘客步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/4-spec.md` 的 Acceptance Criteria／Out of Scope／
Diff Budget／Dependencies 四節,不另存。禁止第二份 `4-spec*.md`。
`write_mode: overwrite`。本機游標不進 Git。

## 做什麼

四節逐節填齊:驗收打包(全 S 綠 + 回歸 + 非功能;行為不變類走 golden master)、
範圍外、差異預算(按區塊拆估,測試檔與非測試碼分開)、依賴逐項一行理由。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devstage4-graph.sh --write-cursor S3a-close`。

## 完成條件

四節齊,沒有一節留空。只有一份 `4-spec.md`。本機游標在 S3a-close。

## 下一跳

S3b-profile
