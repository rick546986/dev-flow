# DEC-endpoint-attestation-stays-out-of-remote-is-offmachine — 主機名解析後的位址攻擊(GPT-P0-REMOTE-ATTESTATION)修在 sync._observe_remote,不修進 identity.remote_is_offmachine

```dev-flow-decision
schema_version: 1
key: endpoint-attestation-stays-out-of-remote-is-offmachine
status: ACCEPTED
decided_at: "2026-08-20T21:15:23Z"
decision_id: dec_01M0GGENC32NDR8868W5NF0NYW
```

## Decision

identity.remote_is_offmachine(url) 維持純函式、只判 URL 形狀,不新增任何連網解析。新增的 DNS 解析與位址比對(resolve_host_ips / ip_is_offmachine / _local_machine_ips)放在 sync._observe_remote 裡,在 remote_is_offmachine 通過之後才呼叫。

## Alternatives

把解析邏輯直接塞進 remote_is_offmachine:被否決。test_identity.py 的 RemoteIsOffMachineTest 有兩張純函式表格測試(合計 30 條 URL、含刻意不可解析的假網域),它們的存在價值正是不連網、不用 mock 就能驗形狀判定。把 DNS 解析塞進同一支函式會強迫這兩張表格測試變成需要 mock 網路解析,而且會讓一個純粹的形狀 predicate 背上網路 I/O 與失敗模式。

## Reason

identity.remote_is_offmachine 回答的是 URL 長得像不像別台機器,sync._observe_remote 回答的是這個 remote 現在到底是不是離開了這台機器——後者本來就已經做網路 I/O,加一次 DNS 解析是同一類操作,加在同一個地方;前者維持零 I/O、零 mock 需求,是更便宜、更常被呼叫的第一道篩選。

## Tradeoff

CI 裡沒辦法用真的 DNS 重映到本機位址(改本機解析設定需要權限、不 portable),所以新的位址攻擊面測試全部替換 identity.resolve_host_ips 這一個問句——URL 形狀判定、ls-remote 問到的 SHA、與 HEAD 的比對全部是真的,同一條紀律。正向路徑的既有測試也因此需要同步替換 resolve_host_ips,否則會因為 CI 沒有網路而假紅。
