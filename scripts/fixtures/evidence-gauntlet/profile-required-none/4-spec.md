# fixture:Required layers 欄在,值為「無」—— 明示零層,不是缺欄

## Verification Profile(G2 一併審)
- lane: full
- Risk: normal
- Required layers:無
- Conditional layers:Supply chain(dependency set 未變,未觸發)
- Explicitly excluded layers:Mutation(本 fixture 不配 mutation 工具)
- Final fresh entry point:`pytest -q`
