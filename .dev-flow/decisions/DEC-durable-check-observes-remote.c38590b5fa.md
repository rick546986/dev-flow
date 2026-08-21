# DEC-durable-check-observes-remote — durable-check 用 ls-remote 問遠端本身,問不到即 FAIL

```dev-flow-decision
schema_version: 1
key: durable-check-observes-remote
status: ACCEPTED
decided_at: 2026-08-21
decision_id: dec_01M0G9QW6M2VYZHS04PZK5W74A
```

## Decision

durable-check 的 remote 那一項改用 git ls-remote 直接問遠端,不再用 rev-parse origin/<branch>(本機追蹤 ref 是快取)。remote 與 ref 從 branch.<name>.remote / .merge 讀,不從字串切。問不到遠端一律 FAIL(DURABLE_REMOTE_UNVERIFIED);離線放行需明確 --local-only,該路徑回傳 remote_observed=false。

## Alternatives

(未填)

## Reason

這一關唯一要回答的問句是「記憶離開這台機器了嗎」,而追蹤 ref 是一份沒有離開這台機器的證據 —— 別台機器 force-push 或刪掉 branch 之後它還指著我的 commit。不用 fetch 是因為判定不該順手改本機的 ref:判定改變被判定的狀態,下一次判定就不是獨立的。

## Tradeoff

(未填)
