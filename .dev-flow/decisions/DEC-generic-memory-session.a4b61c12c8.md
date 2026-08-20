# DEC-generic-memory-session — session/checkpoint 抽成通用原語,dev-run 不必假裝是 dev-talk

```dev-flow-decision
schema_version: 1
key: generic-memory-session
status: ACCEPTED
decided_at: "2026-08-20T11:32:24Z"
decision_id: dec_01M0FF365Q99PJXGK5MHKCV3XJ
```

## Decision

session.py 提供 start/observe/checkpoint/end/abort 原語,understanding(dev-talk)與 implementation(dev-run)兩種模式共用;sync.consolidate() 仍是唯一 durable writer。

## Alternatives

①讓 dev-run 直接呼叫 talk_* 指令:語意錯(那是對話模式),而且 transcript 概念套不上實作期。②給 dev-run 另一套獨立的固化路徑:兩份實作必然漂移,而且會出現兩個 durable writer。③每個 tool event 自動 persist:違反 Signal Gate,.dev-flow 會被雜訊塞爆。

## Reason

缺陷是「只有 dev-talk 那條路能固化記憶」,不是「dev-talk 的模型不對」。抽共用原語同時修掉缺陷又不製造第二套實作。

## Tradeoff

observe() 需要 agent 主動呼叫 —— 工具無法強迫,只能靠 SKILL 明訂 + contract test 釘住 SKILL 有寫。這條限制在 PR body 誠實列出。
