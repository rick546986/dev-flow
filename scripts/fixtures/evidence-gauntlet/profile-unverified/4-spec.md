# fixture:4-spec Required 層在 sibling 7-review 裡是 unverified

## Verification Profile(G2 一併審)
- lane: full
- Risk: normal
- Required layers:Race/stress、Full test suite
- Conditional layers:Supply chain(dependency set 變動時觸發)
- Explicitly excluded layers:Mutation(本 fixture 不配 mutation 工具)
- Final fresh entry point:`pytest -q`
