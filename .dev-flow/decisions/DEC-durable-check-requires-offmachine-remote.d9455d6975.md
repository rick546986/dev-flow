# DEC-durable-check-requires-offmachine-remote — durable-check 採「離開這台機器」的強契約,不放寬成「upstream 有這個 commit」

```dev-flow-decision
schema_version: 1
key: durable-check-requires-offmachine-remote
status: ACCEPTED
decided_at: "2026-08-20T20:22:14Z"
decision_id: dec_01M0GDDAT176PY61AXZSEFS3A6
```

## Decision

remote 的 URL 必須被判定成在別台機器上(網路 transport + 具名非 loopback 主機),判的是 ls-remote --get-url 解析後的 URL;判不出來即 FAIL。要在本機 remote 上放行請明確用 --local-only,那條路回報 remote_observed=false。

## Alternatives

放寬契約並改名欄位與文件(GPT 提的 Option B):被否決,因為那等於承認這一關不再回答它被建立來回答的問題。

## Reason

程式與文件從頭到尾寫的都是「記憶離開這台機器了嗎」。把契約放寬成「upstream 有這個 commit」會讓 W6-4 這一關失去它存在的理由 —— 它正是為了擋「看起來做完了」而存在的。

## Tradeoff

CI 裡沒辦法不連外地建一個真的網路 remote,所以正向路徑的整合測試替換了「這個 remote 的 URL 是什麼」這一個問句;負向路徑(本機 bare、file://、insteadOf 改寫)全部是真的,transport 分類本身也有獨立的表格測試。
