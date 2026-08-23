# N1-start

## 進條件

新場。沒有 MEMORY_SESSION_ID。0-11 todo 尚未建立。
已有 MEMORY_SESSION_ID 再進本節點,不得呼叫 talk start。

## 讀什麼

本檔、`graph.yaml`、入口檔的盲原則 / 讀寫白名單 / 記憶生命週期。

## 寫哪裡

不寫 `1-discussion.md`。不直接改長期記憶檔。只跑 `talk start` 拿到 session。

## 做什麼

跑 `dev-memory.py talk start`。把 0-11 建成 todo。
跑 `scripts/check-devtalk-graph.sh --write-cursor N1-start "$MEMORY_SESSION_ID"`。

## 完成條件

已有 MEMORY_SESSION_ID。0-11 todo 已建。

## 下一跳

S0-scope
