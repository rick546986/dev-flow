# DEC-agent-memory-v3-layout — durable memory 用 .dev-flow/,local runtime 用記憶家目錄下的 projects/<project_id>/

```dev-flow-decision
schema_version: 1
key: agent-memory-v3-layout
status: ACCEPTED
decided_at: "2026-08-20T10:12:06Z"
decision_id: dec_01M0FAG52KB1AK30W7FYXF4WDW
evidence:
  - ref: README.md
    type: file
  - ref: scripts/check-memory-architecture.sh
    type: file
```

## Decision

兩層分離:.dev-flow/ 進 Git,只放結構化高訊號記憶;本機記憶家目錄(預設家目錄下的 .agentmem,可用 AGENTMEM_HOME 覆寫)不進 Git,放 SQLite、FTS、embedding 向量、原始逐字稿、候選知識、本機失效 overlay。

## Alternatives

①全部進 Git(含 SQLite):跨機器不必重建,但二進位檔每次都衝突,且 secret 與本機路徑會被 push 出去。②全部只留本機:沒有跨機器同步,等於沒有可攜記憶。③記憶存在外部服務:多一個相依、一個要顧的機密、一個離線就不能用的失敗模式。

## Reason

要同時滿足「跨機器可攜」與「不把可重建或敏感的東西 push 出去」,只有分兩層做得到。判準單一:刪掉之後跑一次 dev-setup 能不能還原 —— 能就不進 Git。

## Tradeoff

clone 之後必須跑一次 dev-setup 才有索引(換來 Git 樹乾淨與零二進位衝突);durable 目錄名 .dev-flow 與既有的本機執行期目錄 .devflow 只差一個連字號,是已知的命名風險,靠 README 的目錄對照表與 check-memory-architecture.sh 顧著。
