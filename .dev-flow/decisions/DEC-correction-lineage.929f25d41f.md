# DEC-correction-lineage — 修正歷史用 current view + append-only revision event,不引入 event sourcing

```dev-flow-decision
schema_version: 1
key: correction-lineage
status: ACCEPTED
decided_at: "2026-08-20T11:32:24Z"
decision_id: dec_01M0FF365VEWNQCW0F4945W2Y5
```

## Decision

現況檔仍是唯一物化視圖;每次 supersede 另外寫一筆 knowledge_corrected / fact_superseded / decision_superseded 事件進 .dev-flow/events/。

## Alternatives

①每個版本一個檔(knowledge/domain/registration/v1.yaml…):目錄會爆,而且讀取端得自己挑現行版。②獨立 .dev-flow/revisions/ 樹:多一套佈局要顧,而 events/ 的 per-session 分檔已經解決了 Git 衝突。③導入 event sourcing framework:外部相依 + 沒網路就不能用。

## Reason

「現在是什麼」與「以前怎麼理解」是兩種問句,分別由現況檔與事件流回答就夠;不需要把整個記憶改成事件溯源。

## Tradeoff

修正歷史只查得到、不能自動重播出任意時間點的完整快照(as_of 只做到過濾,不做時光機)。
