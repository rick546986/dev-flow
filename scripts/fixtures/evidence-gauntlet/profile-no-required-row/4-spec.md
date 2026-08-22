# fixture:Verification Profile 節在,但沒有 Required layers 那列
# 舊實作當「零層必跑」放行;1.3.2 起缺欄 = E7 紅(可寫「無」/none,不能省略)

## Verification Profile(G2 一併審)
- lane: full
- Risk: normal
- Conditional layers:Supply chain(dependency set 未變,未觸發)
- Explicitly excluded layers:Mutation(本 fixture 不配 mutation 工具)
- Final fresh entry point:`pytest -q`
