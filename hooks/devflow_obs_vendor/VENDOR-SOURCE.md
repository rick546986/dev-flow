# VENDOR-SOURCE — hooks/devflow_obs_vendor/

- 來源 repo:方法論 repo dev-flow(本機路徑以使用者環境為準;正本住方法論 repo)
- 來源路徑:`observability/devflow_obs/*.py` + `observability/schema/*.schema.json`
- 來源 SHA:`82f89b7`
- vendor 日期:2026-08-02(初 vendor @9f08c94;schema 1.1 refresh @82f89b7,Integrator)
- 性質:**runtime vendor 副本**。行為正本仍在方法論 repo;此處只為 plugin 免依賴
  外部路徑而複製。自 1.1 refresh 起 .py 與 schema JSON 皆為 **byte-identical 副本**
  (不再前置標頭;schema sha256 見下表)。
- 重新 vendor 流程:方法論正本改動 → byte-identical 複製 + 更新本檔來源 SHA 與
  sha256 表 → 跑 hooks/selftest.sh 全綠 → commit。**禁止**直接改本目錄內容(= 雙正本漂移)。
- 1.1 注意:`event_validate` 的 task_tags 受控 enum 解析自 `devflow-contract.json`
  (`_CONTRACT_DIR` = plugin 根)。plugin runtime 由 `_obs_impl.py` 以解析鏈
  ($DEVFLOW_CONTRACT → 專案 docs/dev/ 散發副本 → plugin 根)預灌 enum;
  找不到契約且事件帶 task_tags → 明確拒收(fail-closed),不靜默跳過。

## schema sha256(byte-identical 驗證)

- `schema/agent-event.schema.json`: 8ab4252fc98bff7eaa71fce58a19cc12c4e9ec137f8d5ff64cc2bd094bc9a31f
- `schema/context-manifest.schema.json`: d06e66a7704856369c76be1baa52982ba5b41979a13307259cbdd184bf674f06
- `schema/prompt-registry.schema.json`: 0ba97473b1ea7a61484cd97357ccf1636fa02cb6b7369b172bea64009ff80b4d
