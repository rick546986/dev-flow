# S5-diverge — 發散推演

## 進條件

S4 已完成。MEMORY_SESSION_ID 仍在。游標在 S5。
不得 talk start。不得寫程式碼。不得 talk end。

## 讀什麼

Goals、驗收雛形、已核事實。不讀白名單外的文件類資料夾。

## 寫哪裡

不寫 `1-discussion.md`。不寫程式碼。不直接改長期記憶檔。不得 talk end。
結果只記入 Interview Log 發散段。本機游標只留在本機,不進 Git。

## 做什麼

至少一輪 what-if(「往 X 走會怎樣?」「限制 Y 不存在呢?」
「最極端情境?」),純發散、不收斂,結果記入 Interview Log 發散段。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devtalk-graph.sh --write-cursor S5-diverge "$MEMORY_SESSION_ID"`。

## 完成條件

Log 有發散段。本機游標在 S5-diverge。

## 下一跳

S6-blind
