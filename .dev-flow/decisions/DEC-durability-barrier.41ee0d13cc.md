# DEC-durability-barrier — 耐久性屏障:先寫進 .dev-flow,寫成功了才動 local 狀態

```dev-flow-decision
schema_version: 1
key: durability-barrier
status: ACCEPTED
decided_at: "2026-08-20T12:39:25Z"
decision_id: dec_01M0FJXW6G3GSE0N312NBC6PZM
```

## Decision

durable 寫入與 local 狀態變更之間有固定順序:先寫檔,寫成功才 supersede / 標 durable。三個落點各自修正:devtalk.correct() 不再於 consolidation 成功前把舊值標 SUPERSEDED;revision 的 mark_durable 移到 durable.append_events 之後,且只標真的寫進去的那幾筆(其餘留在 pending 等重試);consolidate 的 knowledge/decision/skill 分支改成寫檔在前、DB 變更在後。另加 sync.durable_check() 與 dev-memory.py durable-check,把 Stage 6 收尾的 memory commit 與 remote HEAD 驗證變成可複驗的判定。

## Alternatives

①維持原狀,靠 SKILL 文字提醒 agent 記得 commit:文字提醒擋不住「checkpoint 回 promoted 三筆而 remote 上一個字都沒有」這種無聲失敗。②把整個 consolidate 包進單一 SQLite transaction:檔案系統的寫入不在 transaction 裡,包了也不是 atomic。③被守衛擋掉的 revision 直接標成 local_only 結案:那還是「沒寫進去卻被結案」,只是換個欄位名。

## Reason

三個缺陷同一個病灶:在耐久性真正建立之前就把狀態推進到「已經建立」。它們都不會讓任何測試變紅,因為 local DB 自己是自洽的;要到另一台機器 clone 後 rebuild 才會發現記憶不見了。最惡性的一種是寫檔失敗後重跑,會把「新值 supersede 新值」記成 lineage,真正的轉折永久消失 —— 歷史從缺變成假。

## Tradeoff

①寫檔在前意味著寫成功但 DB 變更失敗時,durable 會多一份沒有 local 鏡射的記錄;那是可以靠 rebuild 收斂的方向,反過來不行。②永遠固化不了的 revision(例如舊值裡有 secret)會在每次 checkpoint 被重新回報;刻意如此,不結案比安靜結案好。③durable-check 需要 upstream 存在,沒有 remote 的專案會一律 FAIL。
