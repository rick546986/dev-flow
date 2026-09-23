# fixture:4-spec Required 層在 sibling 7-review 裡皆 pass

## Verification Profile(G2 一併審)
- lane: full
- Risk: normal
- Required layers:Full test suite、Real execution
- Conditional layers:Supply chain(dependency set 未變,未觸發)
- Explicitly excluded layers:Mutation(本 fixture 不配 mutation 工具)
- Final fresh entry point:`pytest -q`
- E2E entry point:無 — 純後端批次,無使用者互動、無對外 API(fixture)
