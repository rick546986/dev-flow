<!-- 凍結樣本:#175 wrap continuation —— 真實採用專案 CONTEXT 常見形狀。
     第一行定義後換行寫表名/邊界;parser 必須併入 body,不得進 unparsed。 -->
# prism — CONTEXT(詞彙表 / Ubiquitous Language)

> 用途:團隊 + AI 共用的業務語言。

## Language

**Run(上機/定序批次)**:一次晶片上機的定序批次,PGS 與 ECS 各有獨立 run 表
(`ngs_pgs_lab_run` / `ngs_ecs_lab_run`)。
_Avoid_:批次、sequencing batch

**Contract(合約)**:客戶與本公司簽署的服務協議,一筆 = contracts 表一列。
_Avoid_:Agreement、協議書
