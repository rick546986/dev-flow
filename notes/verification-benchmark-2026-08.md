# 驗證機制對標記錄(2026-08-01)

> 2026-08-02 註:本檔為 2026-08 對標的歷史紀錄,結論不隨後續改造改寫;四軌(並行/真實互動/ledger/gauntlet)落地現況見 notes/change-manifests/(ID-11)。

> 目的:回答「dev-flow 的驗證環節為什麼長這樣」。本檔是**設計依據記錄**,不是規則
> 正本 —— 規則正本在 README §5「驗證五律」、§9、`_templates/6/7` 與 dev-run SKILL。
> 對標對象:openspec(Fission-AI)、superpowers(obra)、mattpocock/skills、
> harness-engineering-plugin(rick546986)。調查方法:各專案原始碼逐檔讀 +
> 交叉比對,每項結論附 檔案:行號(細節在調查 session,此處只留結論)。

## 四家比較(六維度)

| 維度 | openspec | superpowers | mattpocock/skills | harness-engineering |
|---|---|---|---|---|
| DoD 載體 | zod schema(SHALL/MUST+≥1 scenario) | Iron Law 文字紀律(貫穿式) | SKILL 內嵌 checklist,判準可操作化 | worker-report JSON Schema v3 |
| 證據要求 | checkbox 字串比對,無執行輸出 | 證據型態表(輸出 0 failures 等) | 強制 paste output + quote spec/hunk | evidence 欄 minLength:1,截圖強制 artifact_path |
| 驗證者隔離 | 無(同 agent 自評);人類 PR 唯一隔離 | 雙層 reviewer + Do Not Trust Report + 閱讀順序防錨定 | 雙軸平行子代理禁合併;HITL 不可代答 | 平台層工具集隔離(reviewer 只有 Read)+ finalizer 時序/身份交叉驗證 |
| 機械強制 | 結構驗證硬擋;完成度可 --yes 繞過 | 幾乎全文字紀律 | ~5% 機械(僅危險 git 攔截) | 最高:schema+finalizer+runtime check |
| 失敗路徑 | 擋下+印訊息,二元結局 | fix-loop 上限 5 輪+breaker+ledger | 無法建 loop 強制停下求助 | failure enum 三路由+loop budget(上限 4) |
| 防錨定 | 未見 | 反預判禁令+controller 不親修 | 多假說+雙軸不合併 | 工具隔離+時序驗證(無閱讀順序設計 —— dev-flow 此點領先) |

## 採納(9 項,已落地)

| # | 採納項 | 源 | 落點 |
|---|---|---|---|
| 1 | 證據 = 原始輸出/檔案:行號,禁自陳 | superpowers+mattpocock | README §5 五律 1;7-review 步 3 |
| 2 | 派工者不下場修 finding | superpowers | README §5 五律 2;dev-run SKILL |
| 3 | 反預判禁令 | superpowers | README §5 五律 3;dev-run SKILL |
| 4 | HITL 不可代答 | mattpocock | README §5 五律 4 |
| 5 | 失敗分類 SPEC/ENV/IMPL/UNKNOWN + 路由 | harness-engineering | README §5 五律 5;dev-run 收驗;6-notes 執行軌跡 |
| 6 | 同 T 總嘗試上限 4,用盡強制 adviser | harness-engineering | README §5 五律 5;dev-run |
| 7 | G3 重驗迴圈上限 3 輪 + breaker 裁決表 | superpowers | 7-review 步 5 |
| 8 | 雙軸各派獨立 fresh reviewer,禁合併重排 | mattpocock | 7-review 步 3 |
| 9 | 大材料檔案路徑交接 | superpowers | dev-run SKILL |

## 不採納(4 項,附理由)

- **openspec `--yes` 繞過未完成任務照樣 archive**:弱化「完成 = 有證據」,方向相反。
- **openspec `/opsx:verify` 同 agent 自評 + 接受「大概率推斷」**:違反驗證不自驗。
- **harness-engineering 整套 JSON Schema 化 DoD**:與本 SOP「輕量 markdown、人類可讀」
  哲學衝突;只借鑑證據格式與失敗分類,不整套 schema 化。
- **reviewer 平台層工具白名單(只給 Read)**:方向正確但需平台配合(自訂 agent type),
  目前以 prompt 明令唯讀代替;**列為未來工作**,平台支援時應升級為機械強制。

## dev-flow 原有領先點(對標中確認,保留)

- 閱讀順序防錨定(7-review 步 0/4:先自建 Coverage Matrix 才准讀 Self-Review)——
  四家中僅 superpowers 有近似設計,harness-engineering 亦無。
- 執行守衛四 hook(PreToolUse/PostToolUse 真攔截)—— 比 superpowers/mattpocock 的
  純文字紀律更硬;現象複驗(親跑,不採信作者文字)比 openspec 的 checkbox 強。
