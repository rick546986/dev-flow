# DEC-stage6-durability-chain — Stage 6 收尾是一條有順序的鏈,不是一組並列的動作

```dev-flow-decision
schema_version: 1
key: stage6-durability-chain
status: ACCEPTED
decided_at: "2026-08-20T12:39:25Z"
decision_id: dec_01M0FJXW6TAN6H9JXFD1224HZJ
```

## Decision

dev-run 收尾固定為:W6-1 強制萃取盤點 → W6-2 checkpoint --end → W6-3 memory commit → 最終 push → remote HEAD 驗證 → W6-4 durable-check。萃取是義務、產出一筆紀錄不是(結論可以是沒東西可記)。sequential 與並行兩節用同一條鏈,由 check-status-policy.sh 的順序鏈守衛加上 memory/tests/test_skill_contract.py 雙向釘住。

## Alternatives

①維持原本的寫法「.dev-flow/ 的改動隨 feature branch 一起 commit/push」:那是一句期望而不是步驟,收尾序列裡沒有任何一步真的去 commit 它,而 checkpoint 又排在最終 push 之後。②讓 devflow-exec.sh stop 硬擋未 checkpoint 的 session:那是 runtime 強制,值得做,但屬於獨立一輪(會動到 exec 守衛的相容面)。

## Reason

順序就是正確性。checkpoint 只把檔案寫進工作樹;排在最終 push 之後時 .dev-flow/ 永遠上不了 remote,而且不會有任何錯誤訊息 —— 這是最容易發生、也最不會被發現的一種假完成。

## Tradeoff

收尾步驟從四步變六步,流程變長;代價換的是每一步都有一個可複驗的完成判準,而不是靠回憶。
