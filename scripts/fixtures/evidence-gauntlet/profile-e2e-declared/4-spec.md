# fixture:4-spec Required 層在 sibling 7-review 裡皆 pass

## Verification Profile(G2 一併審)
- lane: full
- Risk: normal
- Required layers:Full test suite、Real execution
- Conditional layers:Supply chain(dependency set 未變,未觸發)
- Explicitly excluded layers:Mutation(本 fixture 不配 mutation 工具)
- Final fresh entry point:`pytest -q`
- E2E entry point:`npx playwright test`(fixture:宣告命令但 Evidence 沒列 e2e 層 → E7 紅)
