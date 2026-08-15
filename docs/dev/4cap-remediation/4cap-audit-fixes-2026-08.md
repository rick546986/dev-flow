# 四能力審查補強工單(2026-08)

> 來源:2026-08-02 四能力獨立審查(基線 main @ `bf05b59`,= origin/main)。
> 狀態:**P1~P5 已全部落地(2026-08 執行,證據見下方註);O-1~O-8 已於 2026-08-15
> 裁決(見文末新節)**。本檔只列「要改什麼、改哪裡、怎麼驗」;完整審查報告見審查 session。
> 五項缺口皆有第一手實測證據(非文件推論):追溯鏈頂端恆綠、ACCEPTED 場景流失個案、
> 水平切層 5-tasks 通過 contract_ref.py 零錯誤、E11 實際只驗 3/8、docs/specs/ 零實體。
> 落地證據(2026-08-15 覆核,行號已重新核實,非原稿舊行號):
> P1 `scripts/check-methodology-corrections.sh:270-278`(spec_scenarios 上界檢查,封住
> 追溯鏈頂端恆綠);P2 人工審查項,依原裁決不做語意 parser(見該節「驗收」行;2026-08-15
> 另補一條存在性檢查,見 `devflow-4cap-remediation-2026-08.md` §7 第 1 點註);
> P3 `scripts/devflow-evidence-gauntlet.sh:236-242`(E11 五節 heading tuple);
> P4 `README.md:548` 起(§7「強制力對照(誰在擋)」三欄表);
> P5 `_templates/5-tasks.md:42`、`:85`(反水平切層判準兩處)。

---

## P1 封追溯鏈頂端:4-spec S 全集 ⊆ 5-tasks Covers 聯集

- **問題**:`scripts/check-methodology-corrections.sh` 的 `expected_pairs` 從
  `example/.../5-tasks.md` 自己的 Covers 建立,4-spec 從未被抽 S 清單——Stage 5 漏掉
  一個 S,期望集同步縮小,檢查**永遠綠**。README §4「機械檢查每條需求都有測試」
  對「每條 S 都有 T」這段不成立。
- **改哪裡**:`scripts/check-methodology-corrections.sh`,`expected_pairs` 建立完成之後
  (約 :225-240 區塊,`tasks = read("example/.../5-tasks.md")` 迴圈後、
  `check(evidence_pairs == expected_pairs, ...)` 之前)。
- **建議修改**(約三行,沿用既有 `check()` 慣例):

  ```python
  spec_scenarios = set(re.findall(r"^#### (S-\d+)", read("example/contract-expiry-reminder/4-spec.md"), re.M))
  covered_scenarios = {s for (_t, s) in expected_pairs}
  check(spec_scenarios <= covered_scenarios, "4-spec 每個 S 都被至少一個 T 的 Covers 覆蓋",
        f"uncovered={sorted(spec_scenarios - covered_scenarios)}")
  ```

- **連動與注意**:通過數 82 → 83;此檢查仍只保護本 repo 範例——若要保護下游專案,
  另議通用化(`check-traceability.sh <feature-dir>`,列入選配 O-1)。
- **驗收**:`scripts/check-methodology-corrections.sh` 全綠;手測負向——暫時從範例
  5-tasks 拿掉一個 Covers 的 S,腳本必須轉紅。

## P2 Stage 3 ACCEPTED 場景對帳(封 Stage 3→4 接縫)

- **問題**:經人類 ACCEPTED 的 Demo 場景可無聲消失。真實個案:範例 3-prototype 的
  「資料過期(併發編輯)」場景經兩輪驗收 ACCEPTED,4-spec 既無對應 R/S、Out of Scope
  也未列,Stage 7 照樣 PASS。沒有任何步驟的職責是核對「每個已驗收場景都有下落」。
- **改哪裡**:`_templates/4-spec.md` 頂註執行清單(:27 起),**第 3 步「邊界收尾」**
  內加一個子項(Out of Scope 在該步定稿,對帳放這裡才有東西可對)。
- **建議修改**(一行,措辭可調):

  ```
  Stage 3 對帳:逐一核對 3-prototype Demo Script 場景 —— 每個 verdict=ACCEPTED 的
  場景必須對應一條 R/S,或在 Out of Scope 明列排除理由;無 Stage 3 則記 N/A。
  ```

- **連動與注意**:**禁動 README §7 的 G2 gate 定義句**——gate-consistency 動態抽
  §7 粗體錨(外部 plugin,基線已紅 1/14,脆耦合),本項只落模板執行清單,屬 G2
  審查時自然涵蓋,不改 gate 措辭。範例 4-spec 若同步補(把資料過期場景列入
  Out of Scope 附理由),順手消掉已知流失個案。
- **驗收**:人工審查項(不機械化);跑 `check-realworld.sh` 與
  `check-methodology-corrections.sh` 確認模板改動未破壞既有字串斷言。

## P3 E11 補 Operational Walkthrough / Coverage Matrix 存在性檢查

- **問題**:README §7 宣稱 G3 八點「由 devflow-evidence-gauntlet.sh 機械驗證」,
  E11 實際只查 `Standards Axis` / `Spec Axis` / `現象證據` 三個 heading;
  「Walkthrough」只出現在失敗訊息文字裡。OW 與 Coverage Matrix 全 repo 零機械檢查。
- **改哪裡**:`scripts/devflow-evidence-gauntlet.sh` E11 區塊(:225-229),heading tuple:

  ```python
  for heading in ("Standards Axis", "Spec Axis", "現象證據",
                  "Operational Walkthrough", "Coverage Matrix"):
  ```

  只驗 heading 存在,**不驗內容**(驗內容 = 過度設計,見防守清單)。
- **連動與注意**(這項連動最多,照順序做):
  1. `scripts/fixtures/evidence-gauntlet/good-review.md`:已有 `## Coverage Matrix`
     (line 3),**缺 `## Operational Walkthrough`** → 補一節(最小一列即可),否則自測轉紅。
  2. 新增負向 fixture `bad-review-missing-walkthrough.md`,並在
     `scripts/test-evidence-gauntlet.sh` 註冊(31 → 32+)。
  3. **版本 bump**:`GAUNTLET_VERSION` 1.1.0 → 1.2.0 + `devflow-contract.json`
     `schema_versions.gauntlet` 同步(自測有兩者一致性斷言,漏改必紅);檔頭註解
     E 清單順手把漏寫的 E13 補進去(既有的內部文件漂移)。
  4. README §7 G3 錨段落中提及 gauntlet 版本/八點的**非粗體**敘述同步改;粗體 gate
     定義句不動(同 P2 注意事項)。
- **驗收**:`test-evidence-gauntlet.sh` 全綠含新 fixture;對範例
  `example/.../7-review.md` 跑 `--review-file` 模式仍 PASS(該檔兩節都有)。

## P4 README §7 尾補「由誰強制」三欄對照表

- **問題**:12 條文件/Runtime 對照有 5 條 DOCUMENTED_ONLY,README 對它們用同樣的
  肯定語氣(「Runtime 必須拒絕」「不靠肉眼」「機械強制」)。採用者無法分辨哪些
  Gate 真的有東西在擋——會據此降低人工把關密度,兩頭落空。
- **改哪裡**:`README.md` §7 末尾(§8「每階段呼叫的技能」之前,約 :345)。
- **建議修改**:新增小節(標題建議「強制力對照(誰在擋)」),三欄表:
  條件名 | 由誰強制(外部 plugin / 本 repo 腳本 / 純人類自律)| 對應檔案或腳本。
  內容直接取審查報告第 8 節 12 列壓縮。**表內全程避免粗體**(防 gate-consistency
  錨掃描誤收)。
- **連動與注意**:改完須跑外部 plugin 的 `gate-consistency.sh` 確認 14 格沒有新紅
  (基線已紅 1/14:4-spec 頂註 token,屬既有問題,別混入本次);
  `render-methodology-corrections.sh --check` 若涵蓋 README 錨區段需重跑確認。
- **驗收**:文件項;四支 check 腳本 + renderer --check 全綠、gate-consistency 無新紅。

## P5 5-tasks 頂註補反水平切層判準

- **問題**:tracer bullet 是 Stage 5 唯一技術主張,強制力為零(實測純水平切層
  5-tasks 通過 `contract_ref.py` 零錯誤;Stage 5 無人工 gate,guide-quickstart 自陳)。
  「Files >~5 檔 → 拆 T」的反向壓力與 tracer bullet 之間無取捨指引,最直觀的拆法
  就是按架構層拆。
- **改哪裡**:`_templates/5-tasks.md` 頂註兩處:
  1. tracer bullet 句(:17)後接:

     ```
     禁整份按 DB→Repo→Service→API→UI 逐層分 T;每個 T 自問「完成後使用者或系統
     多了什麼可觀測行為」,答不出即水平切層徵兆 —— 與相鄰 T 合併或重新界定。
     ```

  2. 「一個 T 一個關注點」bullet(:27)補尾:

     ```
     超標拆分優先按子行為拆(讀/寫路徑、成功/例外路徑),不按架構層拆。
     ```

- **連動與注意**:純模板文字,不動 frontmatter、不動必填四欄(`contract_ref.py` :145
  只解析 Covers/Files/Verify/Blocked-by,不受影響);guide-dev-flow.html ④ 自陳
  Stage 5 頂註「不在逐字收錄之列」,理論上不觸發 renderer 斷言,仍以驗收確認。
- **驗收**:`check-parallel-stage6.sh` 97 全綠、`check-methodology-corrections.sh`
  全綠、`render-methodology-corrections.sh --check` byte-identical。

---

## 統一驗收(每項改完跑,全套過才算收工)

```bash
scripts/check-methodology-corrections.sh   # 基線 82(P1 後 83+)
scripts/check-realworld.sh                 # 基線 133
scripts/check-parallel-stage6.sh           # 基線 97
scripts/check-vnext-integration.sh         # 基線 14
scripts/test-evidence-gauntlet.sh          # 基線 31(P3 後 32+)
observability/run-tests.sh                 # 基線 125
scripts/render-methodology-corrections.sh --check   # 基線 4/4 byte-identical
# 外部(P3/P4 涉及時):
#   ~/.claude/plugins/local/dev-flow/hooks/gate-consistency.sh(基線紅 1/14,不得新增紅格)
#   plugin selftest + doctor(P3 bump 契約版本後必跑握手)
```

## 選配(審查建議、本輪未列優先,逐項待裁決)

| # | 項目 | 落點 |
|---|---|---|
| O-1 | T×S 追溯配對邏輯抽成通用 `check-traceability.sh <feature-dir>`,下游專案可用 | scripts/ 新檔 |
| O-2 | 產一份真實合併出的 `docs/specs/contracts.md`(範例 4-spec delta),living spec 迴路首次有實體 | docs/specs/ 新檔 |
| O-3 | 第二個範例(合法跳過 Stage 3 的純後端案或 fast-lane bugfix),破自證循環 | example/ 新資料夾 |
| O-4 | 7-review 加「Design Integrity Check」固定清單(仿 Test Integrity Check 形式) | _templates/7-review.md |
| O-5 | Failure Model 之外全 feature 輕量可靠度三問(併發/冪等/逾時:適用或不適用+理由) | _templates/4-spec.md |
| O-6 | 技術債集中:D-n / Failure Model 未覆蓋原因 / breaker park 匯入 STATUS「Known Debt」欄 | _templates/STATUS.md |
| O-7 | 「方案架構圖」補進 gate-consistency 錨;或修正 evidence-gauntlet.md「架構審查」措辭與模板不一致 | README §7 / notes |
| O-8 | Wave 觀察性警訊(非阻斷):全 T 檔案互斥且各覆蓋單一 S → 提示疑似水平切層 | contract_ref.py + plugin |

## 防守清單(審查明確裁定「不要做」,防未來誤補)

1. Stage 5 新增 G1.5 人工 gate(要的是判準句,不是關卡)。
2. 通用「分層偵測」lint 按檔案路徑判層(假警報 → 被整團隊關掉)。
3. 常駐 docs/specs/architecture.md 架構正本(owner 未決定投資前;雙正本必漂移)。
4. task_tags 拉進 5-tasks 必填欄(推翻 10-integration-decisions ID-4 既有裁決)。
5. 對所有 feature 強制部署拓撲/可用性/威脅模型(與 Fast/Full lane 分級矛盾)。
6. Gauntlet 驗 Walkthrough/架構圖「內容正確性」(存在性划算,內容檢查是過度設計線)。
7. 外部 plugin 併回本 repo(握手機制的前提就是兩邊獨立演進)。

> ⚠️ 2026-08-15 註:第 7 條已於 2026-08-13 被推翻,翻案紀錄
> `docs/adr/0001-merge-plugin-into-methodology-repo.md`;其餘 6 條仍有效。
> 本清單原文保留,用途不變(防未來誤補)。

## O-1~O-8 裁決(2026-08-15,owner 授權 fable5)

- **O-1 不採**:P1 已封母版自己的洞;通用化(`check-traceability.sh <feature-dir>`)
  = 新工具 + 新守衛 + 散發面,等採用現場真的要對帳再做(YAGNI)。
- **O-2 不採**:與防守清單第 3 條同邏輯 —— owner 未決定投資前雙正本必漂移;
  目前只有一個 example feature,產實體 = 空殼。
- **O-3 不採本輪,收 Backlog**:價值真(破自證循環)但是整組 1-7 檔的工程,超出本輪範圍。
- **O-4 已採並落地**(2026-08-15 第二批):`_templates/7-review.md:207` 起的
  「Design Integrity Check」節(仿 Test Integrity Check 形式;行號實查)。
- **O-5 已由 P6 落地**:README §7 G2 錨(`README.md:519`)已含 Reliability triage 三問
  (Concurrency/Idempotency/Timeout-retry),`scripts/check-methodology-corrections.sh:298-308`
  機械驗欄位存在與理由非空(行號實查);重複項結案。
- **O-6 已採並落地**(第二批):`_templates/STATUS.md:13` 起的「Known Debt」節
  (行號實查)。
- **O-7 採窄版**:只修 `notes/design/evidence-gauntlet.md:24,273` 的「架構審查」
  措辭不一致(對齊 `README.md:535-536` 的 Standards Axis / Spec Axis / Operational
  Walkthrough / Coverage Matrix / 真實現象複驗五項用語),不加 gate-consistency 錨
  (錨集合刻意窄)。
- **O-8 不採**:母版已有 warning-only 的 `check-task-slicing.sh`;塞進 runtime 增
  面積,收益邊際。
