# S0-scope — 規模、範圍與起點

## 進條件

N1 已完成。MEMORY_SESSION_ID 已在。游標在 S0,或剛從 N1 進來。
不得 talk start。不得寫程式碼。不得 talk end。

## 讀什麼

白名單(長期記憶入口、`docs/specs/`、原始碼)與使用者對起點/範圍的回答。
不讀白名單外的文件類資料夾。

## 寫哪裡

不寫 `1-discussion.md`。不寫程式碼。不直接改長期記憶檔。不得 talk end。
本機游標只留在本機,不進 Git。

## 做什麼

多個需求 → 拆,一 slug 一討論,問使用者先談哪個;
同時問起點:對這塊多熟、想法走到哪 —— 據此校準提問深度(只調深淺,
不放鬆查證與必問)。微型需求(單點小改)→ 徵使用者同意走精簡(步 1 快掃、
步 2 只問 Journey 與 Workarounds、步 5/6 各一輪帶過,骨架照填可短)。
跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor S0-scope "$MEMORY_SESSION_ID"`。

## 完成條件

slug、起點、模式三者定案。本機游標在 S0-scope。

## 下一跳

S1-survey
