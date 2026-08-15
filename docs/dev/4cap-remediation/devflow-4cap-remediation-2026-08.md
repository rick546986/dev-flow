# DevFlow 四能力補強執行報告

> 本檔為交付報告,預設不納入 commit(依執行規格 §十三)。

## Source Documents

| Document | Path | SHA-256 | Role |
|---|---|---|---|
| Remediation plan(文件 A) | `notes/remediation/devflow-opus5-remediation-plan.md` | `bbca235f334e6bf8625294c229e3be3b5e6d5a0a6a4089784b4cd8cd1f11455b` | Scope and design decisions |
| Execution prompt(文件 B) | `notes/remediation/claude-opus5-devflow-execution-prompt.md` | `f1104a33a1b013607d40f250fe791428473be9408b4964ac5a98f67a820199f6` | Execution procedure |

兩檔皆位於 repo 內(未追蹤,使用者既有檔),`/mnt/data/` 對應路徑不存在(已實測)。
行數:文件 A 466 行、文件 B 415 行,皆完整讀取至最後一行。

### 兩份文件的分工與本輪偏離

- **來自文件 A** 的裁決:六項本輪執行清單、十項不得破壞的 DevFlow 原則、十二項本輪不執行的
  deferred 清單、P1 的子集合檢查寫法、P4 表格禁粗體、P6 三問格式與規則。
- **來自文件 B** 的執行要求:先對齊 main、先跑基線、每項 RED→實作→GREEN、單一目的 commit、
  兩名 fresh reviewer 分兩軸、完整回歸、報告格式。
- **依 repo 最新現況調整**(文件寫的與實測不符時以實測為準):
  1. 文件 B §八寫「若 `gate-consistency.sh` 基線已有 1 個失敗,只允許維持原失敗」——
     **實測基線 exit 0 / 14 格全過**,因此本輪標準改為必須維持 14/14(已達成)。
  2. 文件 A/B 只點名「資料過期／併發編輯」一場無下落。逐場對帳後**實際有兩場**
     (另一場為「錯誤狀態:expiring 查詢失敗」),兩場皆已處理,詳見 P2。
  3. 文件 A P1 的範例程式碼把子集合檢查寫在腳本尾段;實際插在 `expected_pairs` 建立之後、
     `evidence_pairs` 比對之前(同一資料流上游),語意相同而讀序更合理。
  4. P4 小節原擬編號 `### 7.1`,實測會撞 `_gate_consistency_impl.py` 的 §7 起點 pattern
     `##\s*7\.` 造成 anchor 不唯一(exit 2),改為不帶編號的標題。
- **兩文件無實質矛盾**;唯一落差是上列第 1 點的基線假設,採不擴張範圍的保守處理
  (維持既有全綠標準)。

---

## 1. 版本基線

- Repository:`/Users/asheng/dev/dev-flow`(origin `https://github.com/rick546986/dev-flow.git`)
- Branch:`fix/devflow-4cap-remediation-2026-08`(自 `main` 開出;**已 push 至 origin,未開 PR、未合併 main**,見 §9.9)
- Before SHA:`bf05b598704da088551c4d32334f450133897e74`(= `origin/main`,與文件 A 的基線參考 SHA 相同)
- After SHA:`d51db459f4abc4930d0c6f1055e4a6434b4a86c1`(共 10 個 commit:P1–P6 六個 + 修第一輪 fresh review 的 `10f455d` + P6 文件收尾 `2d33910` + 修 push-readiness review 的 `cfec5ac` + merge-readiness 修正 `d51db45`,見 §10)
- 日期:2026-08-02
- Working tree 既有未追蹤檔(**未動、未 stash、未刪**,全部 commit 皆指名路徑加入;
  `git log --all -- <這三個路徑>` 空輸出,證明從未被 commit 過):
  - `notes/4cap-audit-fixes-2026-08.md`
  - `notes/remediation/`(即兩份輸入文件)
  - `devflow-4cap-remediation-2026-08.md`(本報告)

---

## 2. 執行範圍

| 項目 | 狀態 | Commit | 摘要 |
|---|---|---|---|
| P1 | DONE(原 OPEN) | `fd97f45` | 以 4-spec 的 S 全集當 Covers 聯集的上界,封住追溯鏈頂端恆綠漏洞 |
| P2 | DONE(原 OPEN) | `7fcf2bf` | 模板加 Stage 3 逐場對帳步;範例兩場無下落的 ACCEPTED 場景列入 Out of Scope 並附 known risk |
| P3 | DONE(原 OPEN) | `3752a9b` | E11 補驗 Operational Walkthrough / Coverage Matrix,Gauntlet 1.1.0 → 1.2.0,新增負向 fixture |
| P4 | DONE(原 OPEN) | `71dffc9` | README §7 末尾加「強制力對照(誰在擋)」表,全域無粗體(HEAD 上 19 資料列,含後續兩輪 review 補的列) |
| P5 | DONE(原 OPEN) | `4bc564c` | 5-tasks 模板加反水平切層判準兩處,純文字 |
| P6 | DONE(原 OPEN) | `ab0c41e` + `2d33910` | 4-spec Verification Profile 加 Reliability Triage 三問 + 範例誠實填寫 + 欄位存在檢查;closure commit 補上 README §7 的兩 lane 說明 |
| — | Review 修正(第一輪) | `10f455d` | 修 fresh review 的 1 HIGH + 2 MEDIUM + 2 LOW finding(見 §6) |
| — | P6 文件收尾 | `2d33910` | README §7 G2 錨定義段補非粗體說明:triage 不計入五欄但兩 lane 皆必答(見 §9) |
| — | Review 修正(第二輪) | `cfec5ac` | 修 push-readiness review 的 1 MEDIUM + 2 LOW finding(見 §9) |

六項在 Before SHA 時**全部 OPEN**,無 `ALREADY_FIXED` 項,無重複實作。

---

## 3. 修改明細

### P1 — 封住 4-spec S 到 5-tasks Covers 的追溯漏洞

- **問題**:`scripts/check-methodology-corrections.sh` 的 `expected_pairs` 完全從
  `example/.../5-tasks.md` 的 Covers 欄建立。某個 S 若整條沒被任何 Covers 承接,期望集合會
  跟著縮小,下游 `evidence_pairs == expected_pairs` 的對稱比對仍全綠 —— 追溯鏈頂端無上界。
- **修改檔案**:`scripts/check-methodology-corrections.sh`(+10 行)
- **實際修改**:在 `expected_pairs` 建立後、`evidence_pairs` 比對前,另從
  `example/contract-expiry-reminder/4-spec.md` 解析 `^#### (S-\d+)` 全集,檢查
  `spec_scenarios <= covered_scenarios`,失敗訊息列 `uncovered=[...]`。沿用既有 `check()` 慣例。
- **負向證據(RED,舊腳本)**:負向案例必須**三處同步**移除才是真 RED —— 只拿掉 Covers
  一處會紅在 `evidence_pairs == expected_pairs`,證明不了恆綠漏洞。三處 = `5-tasks.md`
  T-7 的 `- Covers: R-3 / S-6`、`6-implementation-notes.md` 的 `### T-7 / S-6` 區塊、
  T-7 review log 內指向 `T-7 / S-6` 的 RED→GREEN 行;並重生 6-notes HTML twin
  (否則只紅在 renderer stale,不是覆蓋率)。舊腳本原始輸出:

  ```
  EXIT=0
  ✅ methodology correction checks: 80/80 passed
  ```

  佐證同時成立:`grep "Covers:" 5-tasks.md` 七列皆無 S-6,而 `4-spec.md` 仍有 `#### S-6`。
- **正向證據(GREEN,新腳本)**:
  - 合法範例:`EXIT=0 ✅ methodology correction checks: 83/83 passed`(原 82)
  - 同一負向案例:
    ```
    EXIT=1
    ❌ methodology correction checks: 80/81 passed
      - 4-spec 每個 S 都被至少一個 T 的 Covers 覆蓋: uncovered=['S-6']
    ```
  - 負向 fixture 已用 `git checkout --` 完整還原(`git status` 乾淨)。
- **邊界遵守**:只保護 repo 內範例,未建立通用 `check-traceability.sh`。

### P2 — Stage 3 ACCEPTED 場景必須在 Stage 4 有下落

- **問題**:人類已 ACCEPTED 的 Demo 場景可無聲消失 —— 既無 R/S,也無 Out of Scope 理由。
- **修改檔案**:`_templates/4-spec.md`、`guide-dev-flow.html`(parity 同步)、
  `example/contract-expiry-reminder/4-spec.md`、同目錄 `4-spec.html`(手抄 twin)
- **實際修改**:
  1. 模板執行清單步 3「邊界收尾」加入對帳句(逐場核對 3-prototype Demo Script;每個已
     ACCEPTED 的場景必須對應至少一條 R/S,或在 Out of Scope 明列排除理由;沒有 Stage 3
     時記 N/A),並把「完成 =」延伸為「四節齊 + Verification Profile 填畢 + Stage 3
     對帳逐場有下落」。
  2. 該段是 `guide-dev-flow.html` 的 parity 正本(marker `template4-checklist`,抽取器
     `quote_region("_templates/4-spec.md", "執行清單(", "起草前估")`)。本輪是手抄同步的,
     但**更正一句先前的錯誤說法**:renderer 的 4 個 tracked outputs 正是
     `guide-dev-flow.html`、`guide-quickstart.html` 與兩份 example twin,所以 parity 區塊
     其實是機器產物,`render --write` 也能生成;手抄之所以沒出事,是因為結果與 renderer
     輸出 byte-identical(`--check` 4/4 為證)。下次直接跑 renderer 較穩。
  3. 範例逐場對帳七個 Demo Script 場景,兩場確認無下落,列入 Out of Scope 並附理由與
     known risk:錯誤狀態(`GET /contracts/expiring` 失敗的專用呈現與重試按鈕)、
     資料過期／併發編輯(偵測他人已改動後拒絕以過期資料標狀態)。
- **對帳方法與證據**:以三個獨立視角(literal / generous / G2-reviewer)各自枚舉全部
  Demo Script 場景並判定落點,再對每個被指為缺口的場景派三名對抗性反駁者(要求引用
  4-spec 具體行才可判 refuted)。結果:
  - 兩場 0/3 反駁成功 → 確認缺口:錯誤狀態、資料過期。
  - 「AC-4 等待主管 → 已聯絡供應商」2/3 反駁成功 → 由 R-3 SHALL 句與 R 級行為流程圖
    (`4-spec.md` L63、L140-142)承接,**不列入 Out of Scope**(列入會與 Dependencies 的
    六值 enum 與 S-6 的 GIVEN 直接矛盾)。
  - 「AC-2 空狀態」3/3 反駁成功 → S-2 已完整承接。
  - **第三個 0/3 未被推翻的項目,經裁決不列入 Out of Scope**:「中斷恢復(標到一半關頁
    重開)」。它不是 Demo Script 的 `### Scenario`,而是 3-prototype Method 走查條列
    (L41)與 Scenario AC-4 的觀察問題(L76);P2 的規則對象是「Demo Script 場景」。
    行為本身已由 `4-spec.md` L80(S-4 的 `Recovery:` Operational Context 欄)寫死。
    反駁者推不翻,是因為稽核 prompt 明令「Operational Context bullet 不算覆蓋」——
    那是稽核 lens,不是 P2 的判準。此裁決的邊界問題記入 §7。
- **未做**:未新增 R/S(見下方裁決)、未改 README §7 G2 粗體錨、未新增第二套 Scenario ID、
  未做語意 parser。
- **裁決記錄(為何兩場走 Out of Scope 而非新增 S)**:新增 S 會被既有檢查
  `evidence_pairs == expected_pairs` 機械地逼出連鎖 —— 該 S 必須進某個 T 的 Covers,
  6-notes 必須有對應 `### T-n / S-m` 的 RED→GREEN 證據。但 6-notes 的 T-2 diff fold
  (`b7e91d4`)裡沒有錯誤處理程式碼,T-5 亦無樂觀鎖程式碼,補 S 等於捏造 TDD 證據與 commit
  內容,違反「不假裝 demonstration fixture 是可執行產品」與文件 A「不得自行發明未經原資料
  支持的新行為」。Out of Scope 沒有這個連鎖,且正是 P2 的目的:讓場景**顯性化**而非消失。
- **正向證據**:`check-realworld.sh` 133/133、`check-methodology-corrections.sh` 83/83、
  `render-methodology-corrections.sh --check` 4/4 byte-identical、`gate-consistency.sh` 14/14,
  全部 exit 0。

### P3 — Evidence Gauntlet E11 補齊 review-file 存在性檢查

- **問題**:README §7 G3 第 8 點列了五項(Standards Axis / Spec Axis / Operational
  Walkthrough / Coverage Matrix / 真實現象複驗),E11 只驗其中三節。
- **修改檔案**:`scripts/devflow-evidence-gauntlet.sh`、`scripts/test-evidence-gauntlet.sh`、
  新增 `scripts/fixtures/evidence-gauntlet/bad-review-missing-walkthrough.md`、
  `scripts/fixtures/evidence-gauntlet/good-review.md`、`devflow-contract.json`、`README.md`、
  `notes/design/evidence-gauntlet.md`
- **實際修改**:
  1. E11 heading tuple 由三節擴為五節(只驗 heading 存在,不驗內容)。
  2. `good-review.md` 補最小合法 `## Operational Walkthrough` 節。
  3. `GAUNTLET_VERSION` 1.1.0 → 1.2.0;`devflow-contract.json` 的
     `schema_versions.gauntlet` 同步 1.2.0。
  4. 腳本檔頭 E 清單:改寫 E11 敘述,補上已實作但漏敘的 **E13**。
  5. `README.md` §7 非粗體版本敘述 1.1.0 → 1.2.0(粗體 Gate 錨未動)。
  6. `notes/design/evidence-gauntlet.md`(設計正本)E11 兩處敘述同步標註「1.2.0 起五節」。
  7. **未改**歷史記錄:`notes/verification-benchmark-2026-08.md`、
     `notes/change-manifests/gauntlet.md`(「1.1.0 起增 E13」仍是當時事實)、
     `notes/change-manifests/20-runtime-audit.md`。
- **負向證據(RED)**:新增 fixture 後直接跑舊 E11:
  ```
  EXIT=0
  ✅ evidence gauntlet: 17 checks passed — .../bad-review-missing-walkthrough.md
  ```
  測試套件同步轉紅:`31/32 passed`,失敗列為
  `❌ review 檔雙軸俱在但缺 Operational Walkthrough(E11): exit 0(預期 1)`。
- **正向證據(GREEN)**:
  - `scripts/test-evidence-gauntlet.sh` → `EXIT=0 ✅ 32/32 passed`(原 31)
  - `scripts/devflow-evidence-gauntlet.sh --version` → `devflow-evidence-gauntlet 1.2.0`,exit 0
  - 負向 fixture → `EXIT=1`,訊息
    `E11: review 檔缺「## Operational Walkthrough」…`
  - `example/contract-expiry-reminder/7-review.md --review-file` → `EXIT=0 ✅ 46 checks passed`
- **版本握手**:外部 plugin 的 `hooks/runtime-capabilities.json` **未宣告** gauntlet 版本
  (`schema_versions` 只有 agent_event / context_manifest / prompt_registry / exec_state /
  wave_review),故升版不會製造新的握手不相容;已用升版前後兩份契約分別跑 doctor 對照,
  見 §5。

### P4 — README 增加「強制力對照(誰在擋)」

- **問題**:README 以肯定語氣寫規則,讀者容易把人工紀律誤讀成 Runtime 機械閘門。
- **修改檔案**:`README.md`(§7 末尾、§8 之前,+32 行)
- **實際修改**:新增不帶編號的 `### 強制力對照(誰在擋)` 小節,含三句界線宣告與表格(本 commit 16 列,經兩輪 review 補列後 HEAD 上為 19 列),
  每列標「條件 | 主要強制者 | 對應位置」,分外部 plugin / 本 repo 腳本 / 人工或 fresh
  reviewer 三類。三句界線:①repo reference test 全綠 ≠ external Runtime pass(兩者靠
  `devflow-contract.json` 對版握手,不共用實作);②Gauntlet 只驗 Evidence 契約,自己不跑
  專案測試、也不會發現你根本沒跑;③Coverage Matrix 與 Operational Walkthrough 的內容正確性
  永遠是 Reviewer 的判斷,E11 只驗這兩節在不在。
- **涵蓋**:G1、G2、gate 摘要一致性、Stage 3 verdict、Stage 4 對帳、Stage 5 欄位與 scope、
  Stage 5 反水平切層、Stage 6 guard、Task 獨立 review、S→Covers 追溯、T×S RED→GREEN、
  G3 Evidence、Coverage/Walkthrough 內容、Final Fresh Run、Attempt Ledger、doctor 相容性。
  檔名與 hook 路徑照最新 repo 與 plugin 實況(如 `hooks/_stage3_impl.py`、
  `tests/parallel-stage6/contract_ref.py`、`observability/devflow-obs.py`),未照抄不存在的檔案。
- **負向證據**:小節原編號 `### 7.1 強制力對照(誰在擋)`,`gate-consistency.sh` 立刻
  `EXIT=2 ⛔ README §7 的起點 pattern 命中 2 次,anchor 不唯一` ——
  `_gate_consistency_impl.py` 的 `slice_section(readme_text, r'##\s*7\.', ...)` 會把
  `### 7.1` 也算一次。改為不帶編號的標題後恢復 `EXIT=0 ✅ 全部一致(14/14 通過)`。
- **正向證據**:表內程式化自查 `bold hits: []`、`Gn = hits: []`;§7 全段
  「G1 =」「G2 =」「G3 =」各恰好 1 次(anchor 唯一性未破)。全套 repo checks 與
  gate-consistency 皆 exit 0。

### P5 — Stage 5 補反水平切層判準

- **問題**:模板雖寫 tracer bullet,但純 DB→Repo→Service→API→UI 的水平任務仍可完全通過
  reference parser;加上「Files 超過 ~5 檔就拆」的規則,反而可能推 Agent 按架構層拆分。
- **修改檔案**:`_templates/5-tasks.md`(+4 行)
- **實際修改**:①tracer bullet 後加「禁整份按 DB→Repo→Service→API→UI 逐層分 T。每個 T
  必須能回答:『完成後,使用者或系統多了什麼可觀測行為?』答不出即為水平切層徵兆,應與
  相鄰 T 合併或重新界定。」②「一個 T 一個關注點」後加「超標拆分優先按子行為拆,例如
  讀/寫路徑、成功/例外路徑;不得優先按架構層拆。」
- **未做**:未新增 G1.5 Gate、未加路徑猜 layer 的 lint、未動必填四欄、未加 Slice/Enabler
  schema。本檔不在任何 parity marker 範圍內,guide HTML 無須同步(已確認 renderer 4/4 綠)。
- **正向證據**:`check-parallel-stage6.sh` 97/97、`check-methodology-corrections.sh` 83/83、
  renderer 4/4,皆 exit 0;`git diff` 僅 4 行新增,無其他改動。

### P6 — Stage 4 增加輕量 Reliability Triage

- **問題**:完整 Software Design Contract 過重,但完全不問併發、冪等、逾時/重試的適用性,
  會讓可靠性語意拖到 Stage 6 才由 Agent 自行決定。
- **修改檔案**:`_templates/4-spec.md`、`example/contract-expiry-reminder/4-spec.md`、
  同目錄 `4-spec.html`、`scripts/check-methodology-corrections.sh`
- **實際修改**:
  1. 模板 Verification Profile 末尾加 `- Reliability triage:` 三問
     (`Concurrency` / `Idempotency` / `Timeout/retry`,格式 `applicable | n-a — <理由>`),
     Full 與 Fast lane 都必答;規則以同節註解寫明(n-a 必附具體理由;applicable 不等於本輪
     必實作但必須落到 R/S、Failure Model、Negative Constraints、Required/Conditional 層、
     Out of Scope 或 Known limit 至少一處;本欄只顯性化風險,不得據此新增產品行為)。
  2. Lane 規則同步註明三問不在 fast lane 五欄之內但兩 lane 皆必答。
  3. 範例依現有 Decision / Demo / Spec 誠實填寫:
     - **Concurrency: applicable** — 指向 P2 新列的 Out of Scope「資料過期/併發編輯」
       known risk,並寫明本節 Explicitly excluded 的 Race/stress 排除的是「新增併發寫入
       路徑」的壓力驗證層,與此處的 stale read 缺口不是同一件事、不得互相抵充。
     - **Idempotency: n-a** — 具體理由:狀態標記是 enum 的 set-to-value 寫入(六值,見
       Drafting Decisions),重送同一標記最終狀態值相同;本次不新增對外副作用(自動寄信、
       email/LINE 通知皆在 Out of Scope)。誠實記殘留:歷程可能多一筆同值記錄,屬稽核軌
       雜訊,不改變狀態值。
     - **Timeout/retry: applicable** — 後端不外呼(聯絡法務與供應商皆為系統外動作),唯一
       相關面向是 `GET /contracts/expiring` 失敗時前端的重試互動,已列 Out of Scope 並附
       known risk。
  4. `check-methodology-corrections.sh` 加輕量欄位存在檢查:模板三個欄名存在 + 範例三項各有
     結論(`applicable|n-a`)與 ≥20 字非空理由。**不做語意判斷**,理由寫得對不對仍是 G2
     reviewer 的責任。
- **負向證據**:兩案實測皆轉紅 ——
  ①把範例 `Idempotency` 理由清空 → `EXIT=1 ❌ 89/90`,
  `example Reliability triage「Idempotency」有結論與非空理由: 缺欄或格式不符`;
  ②整條刪除 `Concurrency` 欄 → `EXIT=1 ❌ 89/90`,對應訊息。兩案皆已還原。
- **正向證據**:`check-methodology-corrections.sh` 83 → 90/90(P6 當時);push-readiness
  review 再補一條抽取非空斷言後為 **91/91**;全套 checks 與
  renderer、gate-consistency 皆 exit 0。未新增 Gate、未改 README §7 粗體錨。

---

## 4. 測試結果

| 命令 | 修改前 | 修改後 | 狀態 |
|---|---|---|---|
| `scripts/check-methodology-corrections.sh` | exit 0,82/82 | exit 0,**91/91** | PASS(+9 檢查) |
| `scripts/check-realworld.sh` | exit 0,133/133 | exit 0,133/133 | PASS |
| `scripts/check-parallel-stage6.sh` | exit 0,97/97 | exit 0,97/97 | PASS |
| `scripts/check-vnext-integration.sh` | exit 0,14/14 | exit 0,14/14 | PASS |
| `scripts/test-evidence-gauntlet.sh` | exit 0,31/31 | exit 0,**33/33** | PASS(+2 負向案) |
| `observability/run-tests.sh` | exit 0,125 tests OK | exit 0,125 tests OK | PASS |
| `scripts/render-methodology-corrections.sh --check` | exit 0,4/4 byte-identical | exit 0,4/4 byte-identical | PASS |
| `git diff --check` | — | exit 0(無空白錯誤) | PASS |
| `devflow-evidence-gauntlet.sh --version` | `1.1.0` | `1.2.0` | PASS |
| `devflow-evidence-gauntlet.sh example/…/7-review.md --review-file` | exit 0,44 checks(以 `git show bf05b59:` 的舊腳本實測) | exit 0,**46 checks passed** | PASS(+2 = 新增兩個 heading 檢查) |
| `devflow-evidence-gauntlet.sh …/bad-review-missing-walkthrough.md --review-file` | exit 0(漏接) | **exit 1,E11** | PASS(負向) |

**基線無任何 BASELINE_FAILURE**(七條 repo 命令全綠),因此「新增失敗」與「既有失敗」在
repo 層不需區分 —— 修改後仍全綠。唯一既有失敗在外部 Runtime,見 §5。

---

## 5. 外部 Runtime 檢查

外部 plugin 位置:`~/.claude/plugins/local/dev-flow/`(獨立 repo,本輪一字未動)。

| 檢查 | 修改前 | 修改後 | 判定 |
|---|---|---|---|
| `hooks/gate-consistency.sh` | exit 0,14/14 通過 | exit 0,14/14 通過 | PASS,無新增紅格 |
| `hooks/selftest.sh` | (未於基線跑) | exit 0,**292/292 全過** | PASS |
| `hooks/devflow-doctor.sh` | **exit≠0 INCOMPATIBLE** | exit 1 INCOMPATIBLE(同一項) | **BASELINE_FAILURE,非本次新增** |

- doctor 的失敗原因是**結構性**的:本 repo 是方法論母版,沒有受測專案才會有的
  `docs/dev/devflow-contract.json` 與 `docs/dev/tools/devflow-evidence-gauntlet.sh` 散發副本,
  doctor fail-closed。不帶參數時第一項就死在找不到契約;以 `DEVFLOW_CONTRACT=$PWD/devflow-contract.json`
  指定後可跑完全部項目,其餘皆 ✓,只剩散發副本缺這一項。
- **證明升版未製造新不相容**:以 `git show bf05b59:devflow-contract.json`(升版前,
  gauntlet 1.1.0;1.1.0 只存在於 `bf05b59`,`3752a9b` 起即為 1.2.0)與現行契約(1.2.0)
  分別以 `DEVFLOW_CONTRACT=<該檔> devflow-doctor.sh` 跑,得到**同一條** ✗,只有版本數字
  隨契約改變:
  ```
  ✗ gauntlet: 散發副本缺:…/docs/dev/tools/devflow-evidence-gauntlet.sh 不存在(契約要 gauntlet 1.1.0)
  ✗ gauntlet: 散發副本缺:…/docs/dev/tools/devflow-evidence-gauntlet.sh 不存在(契約要 gauntlet 1.2.0)
  ```
- **無法執行項與原因**:無。gate-consistency / selftest / doctor 三項皆已實跑;doctor 的
  完整綠燈需在**採用專案**內跑 `dev-setup` 重新散發 `docs/dev/tools/`,不屬本 repo 的職責
  範圍,也不在本輪授權內。

---

## 6. Fresh Review Findings

### 方法(防錨定)

兩名 fresh-context reviewer 分兩軸並行,外加一名 completeness critic。強制順序:
**先**從驗收條件與 repo 檔案自建 coverage matrix,**再**讀 `git diff bf05b59..HEAD`;
明令禁止 `git log`、禁讀 commit message、禁讀當時的 intake 暫存檔(已清除)、
禁讀 `notes/remediation/`(作者的計畫)、禁讀本報告。每條 finding 再派 **3 名對抗性
反駁者**,各給不同角度(①實地重現 ②誤讀/其他機制已處理 ③屬 bf05b59 既有或 deferred 項),
過半數推翻才淘汰。共 18 個 agent、537 次工具呼叫。

原始 finding 5 條(Standards 3、Spec 2)+ critic 5 條。淘汰 2 條、存活 3 條、critic 5 條全採。
兩軸 findings 分開保留,未合併、未降級。

### Standards Axis

| 嚴重度 | 位置 | Finding | 反駁票 | 處置 |
|---|---|---|---|---|
| HIGH | `README.md` 強制力表「Stage 4 逐場對帳」列 | 表把該列標成有 repo 腳本驗證(`check-realworld.sh`),但 repo 內完全沒有這個檢查 —— 誠實表自己造出它要防的誤讀 | 1/3 | **已修**(`10f455d`) |
| LOW | `guide-dev-flow.html:221` | fast lane 摘要仍寫「最小五欄」,P6 後不完整 | 2/3 → 第一輪淘汰 | **第二輪(push-readiness)由 Spec 軸重提並採納,已於 `cfec5ac` 修**。第一輪淘汰理由寫的「模板與 README 同語」在當時其實不成立(同一份 §6 的 critic 列就說模板已改、README 未改)—— 這是第一輪的判斷失誤,在此更正,不隱藏 |
| LOW | `README.md` 新表 | 表內重述 G1/G2 gate 條件詞組,形成 gate-consistency 不檢查的第四處 | 3/3 → 淘汰 | 不改(反駁者實測:該詞組非 anchor 比對來源,且此漂移面在 bf05b59 已存在,移除表也不會縮小) |

### Scope／Spec Axis

| 嚴重度 | 位置 | Finding | 反駁票 | 處置 |
|---|---|---|---|---|
| HIGH | `README.md` 同上一列 | 同一問題由 Spec 軸獨立提出(兩軸未互通),並附完整刪段重現 | 0/3 | **已修**(同上) |
| LOW | `README.md` G3 Evidence 列 | 八點全歸 Gauntlet,但第 3 點「已觸發的 Conditional Layer 全 pass」無機制 —— Gauntlet 讀不到 4-spec,不知道觸發了哪些層 | 1/3 | **已修**:拆出獨立一列說明只能靠人把該層寫進 `--require-layer` |

### Completeness Critic(問「漏了什麼」)

| 嚴重度 | 位置 | Finding | 處置 |
|---|---|---|---|
| MEDIUM | `scripts/fixtures/evidence-gauntlet/bad-review-missing-axis.md` | **本輪造成的回歸**:E11 加第四節後該 fixture 同時缺 Spec Axis 與 Walkthrough,而 `run_case` 只 grep「E11」→ Spec Axis 規則被刪掉測試仍綠(base 同樣操作會紅) | **已修**:fixture 補 Walkthrough 使其只缺一節;三個 review 負向案的 pattern 改成「缺「## <節名>」」 |
| MEDIUM | `_templates/4-spec.md:141` | triage 兩 lane 必答,但 fast lane 規則開頭仍是「本節只填五欄」,caveat 埋句尾;README §7 與 `notes/design/vnext-shared-contract.md` 摘要也只列五欄 | **已全修**(跨兩輪):`10f455d` 修模板與 vnext-shared-contract §4;`2d33910` 補 README §7 G2 錨定義段;`cfec5ac` 補 guide-dev-flow.html。四處現在一致 |
| LOW | `scripts/devflow-evidence-gauntlet.sh` Coverage Matrix | 本輪新增規則無負向 fixture,兩個 review fixture 都有該節 → 規則可刪而測試不紅 | **已修**:新增 `bad-review-missing-coverage-matrix.md` |
| LOW | `example/.../4-spec.md:154` | P2 的對帳段無任何檢查釘住,而 P6 三問又引用它(「已列 Out of Scope」)→ 刪掉對帳段後兩處 triage 指向不存在的條目,全綠 | **不加檢查**,改為在強制力表誠實標「無腳本檢查」(HIGH 的修法即涵蓋);文件 A 對 P2 的裁決是維持人工責任、不做 parser。列為 §7 已知限界 |
| LOW | `README.md` 強制力表 | 表宣稱分類「每項條件」,卻漏了 Reliability triage —— 本輪唯一真有腳本檢查的 Stage 4 項目 | **已修**:補一列 |

### 修正後的突變驗證(E11 五節逐一刪除,測試是否轉紅)

| 刪除的 heading | 修正前 | 修正後 | base bf05b59 |
|---|---|---|---|
| Spec Axis | 32/32 綠(回歸) | **32/33 紅** | 紅(30/31) |
| Operational Walkthrough | 31/32 紅 | **32/33 紅** | 不適用(規則不存在) |
| Coverage Matrix | 32/32 綠 | **32/33 紅** | 不適用(規則不存在) |
| Standards Axis | 綠 | 綠 | **綠 31/31(既有缺口)** |
| 現象證據 | 綠 | 綠 | **綠 31/31(既有缺口)** |

「修正前」欄 = `ab0c41e`(該樹只有 32 個測試案),base 欄 = `bf05b59`(31 個案)。
後兩列為 bf05b59 就存在的覆蓋缺口(base tree mutation 實測 31/31 全綠),非本輪造成,
本輪不擴張範圍處理 —— 見 §7。

---

## 7. 未完成與後續建議

以下**皆未完成**,不得描述為已完成(第 3 點例外:它在 push-readiness closure 已完成,
保留條目只為留下軌跡,已標明):

1. **Stage 3 對帳無任何機械檢查**。模板寫了規則、範例照做了,但沒有任何腳本會在範例
   停止對帳時轉紅(已實測:刪掉範例整段對帳,五支 check 全綠)。強制力表已誠實標示
   「人工/fresh reviewer;完全無腳本檢查,連範例都沒有」。這是文件 A 對 P2 的裁決
   (維持人工責任、不做語意 parser)的直接後果,不是疏漏。若下輪要收:最小做法是加一條
   「範例 Out of Scope 節含 Stage 3 對帳段且逐場點名」的存在性檢查,同 P6 風格。
   > → 2026-08-15 處置:**已做**。本棒新增 Stage 3 對帳存在性檢查(見下方四之 1):
   > `scripts/check-realworld.sh` 第 10 節(只驗存在性/結構,不驗場景名字面,依原裁決
   > 不做語意 parser);`scripts/test-architecture-guards.sh` 新增 RW 群組(RW-0 對照組 +
   > RW-1/RW-2 兩個 mutation,含「一條場景保留但拿掉逐場點名引用」的 vacuous-truth 陷阱案)。
2. **E11 的 Standards Axis 與 現象證據 兩節無負向 fixture**(bf05b59 既有缺口)。刪掉
   規則測試仍綠。補兩個 fixture 即可,但屬本輪目標之外。
   > → 2026-08-15 處置:**已做**。本棒補 E11 Standards Axis 與現象證據兩個負向 fixture
   > (見下方四之 2):`scripts/fixtures/evidence-gauntlet/bad-review-missing-standards-axis.md`、
   > `bad-review-missing-phenomena.md`,並在 `scripts/test-evidence-gauntlet.sh` 註冊。
2b. **P2 對帳的「場景邊界」與「什麼算下落」都還沒定義**。本輪按「Demo Script 的
   `### Scenario` 標題」為對帳對象、按「有 R/S 或 Out of Scope 條目」為下落;但
   3-prototype 的 Method 走查條列也承載已 ACCEPTED 的行為(如「中斷恢復」),而
   Operational Context 的 `Recovery:` 這類欄位算不算「下落」也沒寫死。稽核用嚴格 lens
   跑就會把這類項目撈成缺口(本輪撈到一個,見 §3 P2)。下一輪要收:先在模板把這兩個
   邊界寫清楚,再談要不要機械化。
   > → 2026-08-15 處置:**已做**。本棒在 `_templates/4-spec.md` Stage 3 對帳子項(P2 加的
   > 那段)補兩句(見下方四之 3):「Method 走查條列也算 ACCEPTED 行為的下落來源之一;
   > Operational Context 的 `Recovery:` 欄位內容也算下落。」
3. ~~fast lane 五欄 vs triage 的措辭落差只修了一半~~ —— **本項已於 push-readiness closure
   完成,不再是未完成項**。`2d33910` 在 README §7 G2 錨定義段的「fast lane = 最小 Profile
   (五欄,見 4-spec 模板)」句後補了四行非粗體說明;`cfec5ac` 再把 `guide-dev-flow.html`
   的 lane 摘要一併帶到。文件 B 的禁令是「不得修改粗體 Gate 定義句」,補非粗體說明不違反,
   且 gate token 集合逐字未變(見 §9)。
4. **README / 設計筆記裡的版本字串無守衛**。把 `README.md:342`(HEAD 上的行號)的 1.2.0
   改成 9.9.9,五支 check 與 renderer 全綠。目前無實際漂移,屬缺守衛而非缺陷。
   > → 2026-08-15 處置:**已做**。本棒把 gauntlet 版本字串納入 `check-version-sync.sh`
   > (見下方四之 4):新增第五處比對點 `docs/dev/tools/devflow-evidence-gauntlet.sh` 的
   > `GAUNTLET_VERSION`,並修掉「`len(found)==4` 提前判斷」這個會讓新增第五處比對淪為
   > no-op 的陷阱(此前 4 處全抽到值就直接判「一致」,第 5 處抽到值與否都不影響交叉比對)。
   > `test-architecture-guards.sh` 新增 VS-5 mutation(單獨把 docs/dev/tools 副本改 9.9.9
   > → 紅,驗第五處確實有被比對;既有 VS-1 README 改 9.9.9 → 紅維持不變,兩案分屬不同點)。
5. **本輪 deferred 項全數未做**(獨立 `architecture.md`、完整 Software Design Contract
   大表、Stage 5 G1.5 Gate、路徑式 layer lint、Runtime 併回、`task_tags` 必填、部署拓撲/
   可用性/威脅模型強制、Gauntlet 判斷內容正確性、通用追溯腳本、第二個完整範例、
   真實 Reference App、Living Spec 實體化)。已用 `git diff --stat bf05b59..HEAD` 佐證:
   16 檔、+216/−13 行,新檔只有兩個 gauntlet 負向 fixture;無新 Stage、無新模板、
   無新 Gate、無新頂層腳本。
   > → 2026-08-15 處置:**收攏**(逐項見 `4cap-audit-fixes-2026-08.md` 的 O-1~O-8 裁決節):
   > G1.5/路徑式 layer lint/`architecture.md`/`task_tags` 必填/部署拓撲·可用性·威脅模型
   > 強制/Gauntlet 判斷內容正確性 = 防守清單 1-6 裁定不做;Runtime 併回 = ADR-0001 已翻案
   > 完成;通用追溯腳本 = O-1 不採;Living Spec 實體化 = O-2 不採;第二個完整範例 = O-3
   > 收 Backlog;Software Design Contract 大表/真實 Reference App = 收 Backlog(低優先)。
6. **外部 Runtime 的 doctor 仍 INCOMPATIBLE**(既有失敗)。要全綠須在**採用專案**內跑
   `dev-setup` 重新散發 `docs/dev/tools/`,不屬本 repo 職責,也不在本輪授權內。
   > → 2026-08-15 處置:**結案**。採用端動作,非本 repo 職責;A-12 已修(模板要求跑
   > doctor),觸發點已存在,不需本 repo 再做任何事。
7. ~~未 push、未開 PR~~ —— push 狀態改由 §9 記錄(本輪已授權 push branch,仍不開 PR、
   不合併 main);報告檔 `devflow-4cap-remediation-2026-08.md` 維持不 commit。

---

## 8. 最終判斷

- **是否達成本輪 P1～P6**:是,六項全數落地(含 P6,見下)。**RED 證據只有四項有**:
  P1、P3、P4、P6 各有負向轉紅的原始輸出;**P2 與 P5 沒有 RED,也不可能有** —— 兩者都是
  純文字規則,repo 內沒有任何檢查會在它們被違反時轉紅(P2 見 §7 第 1 點的刪段實測、
  P5 見 §8 的 DOCUMENTED_ONLY 清單)。這正是它們列為 DOCUMENTED_ONLY 的原因,不是漏做測試。
- **是否新增回歸**:本輪一度製造一個回歸(E11 加節後吃掉 Spec Axis 的測試覆蓋),由
  completeness critic 抓到並已修復 + 突變驗證。修正後全套 repo check(91/133/97/14/33/125/4)
  與外部 gate-consistency 14/14、selftest 292/292 皆綠,無殘留回歸。
- **哪些能力仍為 DOCUMENTED_ONLY(有規則、無機械強制)**:
  - Stage 3 → Stage 4 逐場對帳(§7 第 1 點)。
  - Stage 5 反水平切層判準(P5 本就只加判準,無 lint;強制力表已標「人工/fresh reviewer」)。
  - G3 第 3 點「已觸發的 Conditional Layer 全 pass」(強制力表已拆列標示)。
  - Coverage Matrix 與 Operational Walkthrough 的**內容正確性**(E11 只驗 heading 存在)。
  - Final Fresh Run 是否真的跑過(Gauntlet 只驗宣告與 SHA 綁定)。
- **真的有機械強制的**:4-spec S → 5-tasks Covers 追溯(範例層)、T×S RED→GREEN 證據
  (範例層)、E11 五節存在性、Gauntlet E1–E13、Reliability triage 欄位存在與非空理由
  (模板 + 範例層)、gate 摘要三處一致(外部 plugin)、Stage 6 scope guard(外部 plugin)、
  方法論/Runtime 版本握手(外部 doctor,fail-closed)。
- **一句話**:本輪把「宣稱有機械閉環、實際可恆綠或漏接」的四處補上(P1 追溯頂端、
  P3 E11 兩節、P6 triage 欄位、以及 review 抓出的 E11 覆蓋回歸),並把剩下真的只能靠人的
  部分在 README 表裡指名道姓 —— 沒有把人工紀律粉飾成機械閘門。

---

## 9. Push Readiness Closure(2026-08-02 第二輪)

本節記錄「把分支推上 origin」前的收尾:確認報告與實際 diff 一致、補完唯一會讓 P6
產生歧義的文件落差、對最終 diff 做第二次獨立審查、重跑完整驗證。目標**不是**消滅
所有已知限制 —— §7 的 ACCEPTED_LIMITATION 與 FOLLOW_UP_HARDENING 全數保留。

### 9.1 現況驗證(先驗證,不直接改)

| 檢查 | 結果 |
|---|---|
| 當前分支 | `fix/devflow-4cap-remediation-2026-08` |
| 開工時 HEAD | `10f455d`,與前次報告記錄相符,無來源不明的 commit |
| `git fetch origin --prune` 後 `origin/main` | 仍是 `bf05b598704da088551c4d32334f450133897e74`,**未前進** |
| `git merge-base --is-ancestor origin/main HEAD` | 成立 → **不需 rebase**,無 `BLOCKED_BY_REBASE_CONFLICT` |
| 遠端同名 branch | **不存在**(`git ls-remote --heads origin fix/devflow-4cap-remediation-2026-08` 空;遠端僅 `refs/heads/main`)→ 不涉及 force push |
| tracked working tree | 乾淨 |
| 三個未追蹤檔 | 未進 commit,且 `git log --all -- <三路徑>` 空輸出(從未被 commit 過) |
| 兩份輸入文件 SHA-256 | 未變 |

### 9.2 項目重新分類

分類當時另寫在 `/tmp/devflow-push-readiness-classification.md`(交付後已隨中間檔清除;
實質內容如下,並與 §7 的清單一致)。摘要:

- **MUST_FIX_BEFORE_PUSH — 只有一項**:README §7 的 G2 錨定義段只寫「fast lane = 最小
  Profile(五欄)」,同一區域看不到 Reliability triage 三問義務。實測確認這是三處中
  唯一落差(模板與 `notes/design/vnext-shared-contract.md` 都已寫清楚;README 全檔
  `Reliability` 當時只出現在強制力表那一列)。它會讓 P6 完成狀態產生歧義 —— 前次報告
  §2 標 DONE、§8 標「部分達成」,自相矛盾。
- **ACCEPTED_LIMITATION 六項**、**FOLLOW_UP_HARDENING 六項**:見 §7 與分類檔,本輪
  一項都不做,也不因「尚未完成」擴大範圍。

### 9.3 Closure 修改

**`2d33910 docs: clarify fast lane reliability triage requirement`**(只動 `README.md`,+4 行)

在 G2 錨定義「Verification Profile」項的既有句**後方**接一段非粗體說明:triage 不計入
五個最小 Profile 欄位,但 full 與 fast lane 都必須回答三問;fast lane 多半三項皆 `n-a`、
理由仍不得省;並明說本項只有 repo 腳本驗欄位存在與理由非空,理由是否成立仍是 G2
reviewer 判斷,**無 Runtime 機械強制**。

未改五欄定義、未加 Gate/G1.5/schema、未動任何粗體 Gate 錨句、未加標題(避免 `### 7.1`
會被 `##\s*7\.` 誤判的老問題)。驗證:

- `gate-consistency.sh` exit 0,14/14;三個 gate 的正本 token 集合與基線**逐字相同**
  (G1:`Owner Calls / 全裁決`;G2:`R/S / 全審 / Drafting Decisions / 全裁決 /
  Verification Profile / Demo verdict`;G3:`本次 / S / 全綠 / 既有測試套件全綠 /
  現象證據 / Evidence / 契約全過`)。
- 新增段落程式化自查:`bold hits: []`;§7 內「G1 =」「G2 =」「G3 =」各恰好 1 次;
  §7 起點 pattern 全檔恰好命中 1 次。

### 9.4 Fresh Push-Readiness Review(第二輪,兩軸 + 報告對帳)

方法:兩名 fresh-context reviewer(Spec/Scope、Standards/Regression)先自建判準、
再讀 `git diff origin/main...HEAD`;**禁止**先讀本報告、intake、分類檔、commit message
與 `notes/remediation/`。產出自己的 findings 後,才各自讀本報告做對帳(報告與實際
不符一律至少 MEDIUM)。

**程序上的誠實揭露**:對抗性反駁階段跑到 53 票時,使用者要求把某個 verify agent 的
`rm -rf "$V/$slug"` 改成 fail-closed 才可繼續,我據此**中止了該 workflow**。中止發生在
彙總之前,票數無法對回個別 finding,因此下列處置改由我**逐條直接重現**判定,而不是
用三票制淘汰。這比第一輪弱,如實記錄。正式 repo 全程未被動到(中止後
`git status` 與 `git rev-parse HEAD` 皆確認)。使用者指定的三項 base-tree mutation
已用加了七道護欄(`set -euo pipefail`、非空檢查、目標必須嚴格在 `$V/` 底下、禁刪 `$V`
本身與父目錄、`rm -rf --`、刪前印出完整 target、只在 scratchpad 操作)的腳本重跑,
並對 `..`、空 slug、逃逸路徑做過護欄自我測試(4/4 全部 BLOCKED)。

#### Spec/Scope 軸

| 嚴重度 | 位置 | Finding | 處置 |
|---|---|---|---|
| LOW | `guide-dev-flow.html:221` | lane 摘要仍寫「fast = 最小五欄」,三份使用者文件中唯一沒帶到 triage 的地方 | **已修**(`cfec5ac`)。該行經程式化確認在手寫區、不在任何 parity marker 內 |

#### Standards/Regression 軸

| 嚴重度 | 位置 | Finding | 處置 |
|---|---|---|---|
| MEDIUM | `scripts/check-methodology-corrections.sh:241` | **P1 的守衛自己 fail-open**:`spec_scenarios` 未斷言非空,抽取失敗時 `set() <= X` 恆真,檢查靜默變 no-op 卻報綠 | **已修**(`cfec5ac`)。自驗重現:把範例 4-spec 的 `#### S-n` 全降級為 `### S-n`,修正前 exit 0 / 90-90;加斷言後同一案 exit 1 / 90-91 |
| MEDIUM | `scripts/test-evidence-gauntlet.sh:57` | E4「pass 但 Command 空」規則可刪而測試全綠(fixture 同時觸發兩個 E4,斷言只 grep 規則碼);另有四條規則無任何 fixture | **降為 FOLLOW_UP**:reviewer 自己附了可重現證據證明 `bf05b59` 完全相同、非本分支引入。與本輪為 E11 修的是同一種缺陷,但把它擴到全部 E 規則會重寫大量 fixture,超出本輪範圍 |
| LOW | `README.md` G3 Evidence 列 | 只把第 3 點列為例外,但第 2、5 點(Required Layer 全 pass / 不得 unverified) 同樣要人補 `--require-layer` 才會擋 | **已修**(`cfec5ac`)。實測:`good-evidence.md` 不帶旗標 exit 0、帶 `--require-layer "Race/stress"` exit 1。表改為第 2、3、5 點例外並拆兩列說明難度差異 |
| LOW | `example/contract-expiry-reminder/5-tasks.html:48` | 手寫 twin 漂移:HTML 有「T 依賴 DAG」ASCII 圖,md 沒有,違反 README §6「md 永遠留 ASCII 正本」 | **降為 FOLLOW_UP**:該對 md/html 在 `bf05b59..HEAD` 之間 byte 未變(不在 `--name-status` 內),既有缺陷非回歸 |

#### 報告對帳(兩名 reviewer 各自讀報告後提出,共 15 條,合併去重後 10 個獨立問題)

全部**已在本報告修正**,逐條列出不隱藏:

| 問題 | 報告原本寫的 | 實際 |
|---|---|---|
| After SHA / commit 數 | `10f455d`,7 個 commit | 報告寫於 closure commit 之前;實際 9 個 commit,tip `cfec5ac` |
| §7 第 3 點 | 「fast lane 落差只修了一半…README §7 未動」 | `2d33910` 已補;條目改標已完成 |
| §6 critic 列處置 | 「部分修…README §7 G2 錨定義段未動」 | 已全修(跨三個 commit) |
| §8 P6 判定 | 「部分達成」 | HEAD 上完全達成 |
| diffstat | `+206/−12` | HEAD 上 `+216/−13` |
| 突變表「修正前」欄 | `32/33`、`33/33` | `ab0c41e` 只有 32 案:應為 `31/32 紅`、`32/32 綠`(紅綠方向原本就對) |
| §8「每項皆有 RED」 | 六項皆有 RED 與 GREEN | 只有 P1/P3/P4/P6 有 RED;P2、P5 是純文字規則,沒有也不可能有 |
| §5 doctor 對照命令 | `git show HEAD:devflow-contract.json`(稱 1.1.0) | 該命令現在給 1.2.0;1.1.0 只在 `bf05b59`,已改寫成可重現的命令 |
| §3 P2 renderer 說明 | 「renderer 只管 4 個 tracked outputs,不含兩份 guide HTML」 | **錯**:那 4 個正是兩份 guide + 兩份 example twin。已更正並註明手抄之所以沒出事是因為與 renderer 輸出 byte-identical |
| §7 第 4 點行號 | `README.md:338` | HEAD 上是 `README.md:342`(實質結論不變,已複驗) |
| §6 Standards 列淘汰理由 | 「模板與 README 同語」 | 當時不成立,是第一輪的判斷失誤;已在表內更正並標明第二輪重提後採納 |

**剩餘 HIGH:0。剩餘未處理 MEDIUM:0**(兩條 MEDIUM 一條已修、一條附可重現證據降為
FOLLOW_UP)。

### 9.5 最終完整驗證(HEAD = `cfec5ac`)

| 命令 | 結果 | 門檻 |
|---|---|---|
| `scripts/check-methodology-corrections.sh` | exit 0,**91/91** | ≥ 90 ✔(+1 為本輪新增的抽取非空斷言) |
| `scripts/check-realworld.sh` | exit 0,133/133 | ✔ |
| `scripts/check-parallel-stage6.sh` | exit 0,97/97 | ✔ |
| `scripts/check-vnext-integration.sh` | exit 0,14/14 | ✔ |
| `scripts/test-evidence-gauntlet.sh` | exit 0,33/33 | ✔ |
| `observability/run-tests.sh` | exit 0,125 tests OK | ✔ |
| `scripts/render-methodology-corrections.sh --check` | exit 0,4/4 byte-identical | ✔ |
| `git diff --check` | exit 0 | ✔ |
| `hooks/gate-consistency.sh` | exit 0,14/14 | ✔ |
| `hooks/selftest.sh` | exit 0,292/292 | ✔ |
| `devflow-evidence-gauntlet.sh --version` | `1.2.0` | ✔ |
| `devflow-evidence-gauntlet.sh example/…/7-review.md --review-file` | exit 0,46 checks | ✔ |

無任何數字下降。

### 9.6 Doctor 等價性(不要求假綠)

| 跑法 | 結果 |
|---|---|
| `devflow-doctor.sh`(不帶契約) | exit 1,✗ 1 項:找不到 `docs/dev/devflow-contract.json` |
| `DEVFLOW_CONTRACT=$PWD/devflow-contract.json devflow-doctor.sh` | exit 1,**✗ 恰好 1 項、✓ 8 項**:散發副本 `docs/dev/tools/devflow-evidence-gauntlet.sh` 不存在(契約要 gauntlet 1.2.0) |

- 失敗項與 §5 記錄的 BASELINE_FAILURE **同一項**,**沒有第二個不相容項**。
- 1.2.0 本身未造成新的握手失敗:以 `bf05b59` 的 1.1.0 契約跑,得到同一條 ✗,只有版本
  數字不同。
- **未**把採用專案的散發副本硬塞回母版 repo,**未**修改外部 plugin
  (`~/.claude/plugins/local/dev-flow/` working tree 乾淨、HEAD 仍 `522569a`)。
- 判定:非 `BLOCKED_BY_NEW_DOCTOR_INCOMPATIBILITY`。

### 9.7 base-tree mutation(使用者要求以 fail-closed 版重跑)

`bf05b59` 匯出樹,逐一從 E11 heading tuple 刪一節後跑測試:

| 刪除的 heading | base(`bf05b59`)結果 |
|---|---|
| Standards Axis | 綠 31/31 —— 無負向覆蓋(既有缺口) |
| Spec Axis | **紅 30/31** —— 有負向覆蓋 |
| 現象證據 | 綠 31/31 —— 無負向覆蓋(既有缺口) |

與 §6 突變表的 base 欄一致。三棵測試樹已用同一組護欄清除;背景 agent 留下的
`wt-ab0c41e` worktree 以 `git worktree remove` 移除(非 `rm -rf`)。

### 9.8 Push 判準逐項

| 條件 | 結果 |
|---|---|
| branch = `fix/devflow-4cap-remediation-2026-08` | ✔ |
| `origin/main` 是 HEAD 祖先 | ✔ |
| tracked working tree 乾淨 | ✔ |
| 只有已知未追蹤檔(三個) | ✔ |
| 未追蹤輸入文件未被 commit | ✔(`git ls-files` 三路徑皆空;`git log --all` 亦空) |
| P1～P6 實際落地 | ✔ |
| P6 README 說明已無歧義 | ✔(`2d33910` + `cfec5ac`) |
| repo 完整測試全綠 | ✔ |
| gate-consistency 14/14 | ✔ |
| selftest 292/292 | ✔ |
| doctor 無新增不相容項 | ✔(1 ✗ = 既有) |
| Fresh Review 無 HIGH / 未處理 MEDIUM | ✔ |
| `git diff --check` | ✔ |
| Remote 無未知同名 branch | ✔(遠端只有 `main`) |

全部成立 → 已執行 `git push -u origin fix/devflow-4cap-remediation-2026-08`。
**未建立 PR、未合併 main、未 force、未改 branch protection、未跳過 hooks。**

### 9.9 Push 後驗證

| 項目 | 值 |
|---|---|
| Result | **PUSHED** |
| Local branch | `fix/devflow-4cap-remediation-2026-08`(tracking `origin/fix/devflow-4cap-remediation-2026-08`) |
| Remote ref | `refs/heads/fix/devflow-4cap-remediation-2026-08` |
| Local HEAD | `cfec5ac9c5ae602fa035bc1e8e9ce1b68fd342b9`(§10 後為 `d51db45`) |
| Remote SHA | `cfec5ac9c5ae602fa035bc1e8e9ce1b68fd342b9` |
| 一致 | 是(逐字相同) |
| `origin/main` | 仍是 `bf05b598704da088551c4d32334f450133897e74`,未被推動 |
| PR | 未建立(`gh pr list --head fix/devflow-4cap-remediation-2026-08` 空輸出) |
| 未追蹤檔 | 三個仍在本機、未 commit、未 push |

Push 為新分支建立(遠端先前只有 `main`),非 force、非覆寫。

下一步建議:由獨立 Reviewer 檢查遠端 branch,確認後再建立 Draft PR。


---

## 10. Merge-Readiness 修正(Draft PR #1 開出後,2026-08-02)

Draft PR:https://github.com/rick546986/dev-flow/pull/1(base `main`,仍 Draft,未合併)。
極小範圍三項,`d51db45 docs: correct enforcement and idempotency claims`,3 檔 +9/−4。

| # | 問題 | 修法 |
|---|---|---|
| 1 | README §7 同時宣稱「八點由 Gauntlet 機械驗證」與(強制力表)「第 2、3、5 點要人補旗標才擋」,自相矛盾 | 該句改為「八點中的 **Evidence 文件契約**由 gauntlet(1.2.0,E1–E13)機械驗證;第 2、3、5 點仍須依 Verification Profile 正確傳入 Required／Conditional layer(旗標漏帶會 fail-open),並由 Reviewer 核對」。**未動 G3 粗體錨的條件語意**;三個 gate 的正本 token 集合逐字未變 |
| 2 | 範例 Idempotency 標 `n-a` 分類錯誤 —— 狀態值收斂不等於完整操作冪等 | 改 `applicable`:保留「狀態值會收斂」「歷程可能重複」「因此完整操作不保證冪等」「本期不新增 idempotency key 或歷程去重,列 known limit」四點,明寫不新增產品行為。md 與 html twin 同步 |
| 3 | 兩場排除場景只有理由,無裁決人留痕 | Stage 3 對帳段末補一行 Owner confirmation(rick 確認明示排除於本期交付範圍)。**不新增 R/S、不產生任何 TDD Evidence** |

驗證(全部 exit 0,無任何數字下降):methodology **91/91**、realworld 133/133、
parallel-stage6 97/97、vnext 14/14、gauntlet tests 33/33、observability 125 OK、
renderer 4/4 byte-identical、`git diff --check` 0、gate-consistency 14/14、
selftest 292/292。doctor 帶契約仍為 **✗ 1 項 / ✓ 8 項** 的同一條 baseline failure,
**無新增不相容項**。

PR 狀態:Draft、OPEN、base `main`、10 commits、`MERGEABLE` / `CLEAN`;
`origin/main` 仍 `bf05b59` 未被推動;未合併、未 force、未建立第二個 PR。


---

## 11. Merge Closure(2026-08-02)

PR #1 已以 **Squash merge** 合併進 `main`。

| 項目 | 值 |
|---|---|
| PR | https://github.com/rick546986/dev-flow/pull/1 — **MERGED** |
| PR head(合併時) | `d51db459f4abc4930d0c6f1055e4a6434b4a86c1` |
| Squash commit | **`96f01e9a2fa2688966c888e870b68255ab38b4dd`** |
| `main` | `bf05b59` → `96f01e9`(parent 恰為 `bf05b59`,線性接上) |
| Merged by / at | rick546986 @ 2026-08-02T13:16:40Z |
| 合併方式 | `gh pr merge 1 --squash --match-head-commit d51db45`(head SHA 防漂移) |

未 force、未 rebase merge、未改 branch protection(該 repo `main` 本就無保護規則,唯讀查證後未動)。
遠端 feature branch `fix/devflow-4cap-remediation-2026-08` 保留未刪。

### Final Approval Record

已於合併前留在 PR:https://github.com/rick546986/dev-flow/pull/1#issuecomment-5158138406
記錄三輪審查、完整測試全綠、剩餘 HIGH 0 / MEDIUM 0、Owner 四項裁決,以及**驗證來源**
—— 本 repo 無使用者定義 CI workflow(兩個 ref 皆無 `.github/workflows/`;Actions 清單
唯一的 `pages-build-deployment` 是 GitHub 為 Pages 自動註冊的動態 workflow,不在 PR 上跑),
本 PR check-runs 0、commit status 0,所有綠燈都來自本機執行 repo 內 persisted commands。

審查者產生方式:無第二位適格人類 reviewer → 採 README §7 降級順序的第二順位
**fresh-context reviewer Agent fallback**,已在 PR 留痕,不假裝有四眼。

### 合併後複驗(直接對 `origin/main` 的樹重跑)

methodology **91/91**、realworld 133/133、parallel-stage6 97/97、vnext 14/14、
gauntlet tests 33/33、observability 125 OK、renderer 4/4 byte-identical、
`devflow-evidence-gauntlet.sh --version` = 1.2.0。全部 exit 0。

抽驗 `origin/main` 內容:README 有「強制力對照(誰在擋)」與 Reliability triage;
`check-methodology-corrections.sh` 有「4-spec 每個 S 都被至少一個 T 的 Covers 覆蓋」;
範例 4-spec 有 Owner confirmation;三個 `bad-review-missing-*` fixture 皆在;
`GAUNTLET_VERSION` 與 `devflow-contract.json` 皆為 1.2.0。

### 合併後仍然成立(不得因為合併就描述為已完成)

Stage 3 → Stage 4 逐場對帳無機械檢查;P2 的場景邊界與「什麼算下落」未定義;
Stage 5 反水平切層是人工判準;G3 第 2、3、5 點需人補 `--require-layer`;
Coverage Matrix / Operational Walkthrough 的內容正確性;Final Fresh Run 是否真的跑過;
E11 的 Standards Axis / 現象證據 兩節仍無負向 fixture;版本字串無守衛;
外部 doctor 在母版 repo 仍為既有 baseline failure(需在採用專案跑 `dev-setup`)。


---

## 12. 採用現場發現的母版缺口 — html twin 產出鏈(2026-08-05 追記)

本節與 §1–§11 的 P1–P6 無關,是**採用端**回報的母版問題:四個既有專案遷到
`2c36976`(= `devflow-pilot-v2`)之後,**python-prism 產 html twin 的實戰**撈出四條。
姊妹檔 `notes/adoption-findings-2026-08-04.md` 記同一批採用回饋的其他面向
(A-0～A-6 / B-1～B-4 / C-1～C-2);本節四條**不重複該檔內容**,重疊處以交叉引用標明。

寫法沿用 §3 的四段式(現象 / 證據 / 影響 / 建議修法)。所有行號與數字皆於 2026-08-05
逐條開檔複驗:母版側對工作樹 `2c36976`,python-prism 側對 `5a0eb81`,
plugin 側對 `~/.claude/plugins/cache/dev-flow-plugin/dev-flow/2.5.0/`。
**複驗範圍的界線**:本輪複驗的是**現象與成因**(F-2 三個 bug 皆以原碼實跑重現);
F-2 的**修法**為原回報所附(稱已在 scratchpad 驗過、回歸零副作用),**本輪未複驗修法**
—— 依 §9.4 的規矩,報告不得把未驗的事寫成已驗。
**F-1～F-4 全是建議,本輪未動任何母版檔** —— 工作樹唯一被改的是本報告(未追蹤)。

| # | 級 | 一句話 |
|---|---|---|
| F-1 | HIGH | README §6 把 twin 訂成每階段終態的硬義務,母版卻只給殼檔、不給轉換器 |
| F-2 | HIGH | 現場撈回來的那支轉換器有三個真 bug,母版若要散發須先修 |
| F-3 | MEDIUM | `_templates/diagram-style.md`(畫法正本)在採用專案缺件,且無守衛會發現 |
| F-4 | MEDIUM | `_templates/html-shell.html` 缺 `diagram-style.md` 引用的**全部**圖表 CSS |

### F-1(HIGH)— SOP 要求每階段終態都有 twin,母版卻沒有散發用的 md→html 轉換器

- **現象**:README §6 把 twin 訂成硬義務,但指定的產法是「殼檔 + 模型手寫」。
  規格文件長到兩千行時手寫不現實,採用專案只好自製腳本;而它唯一想得到的擺放位置是
  母版覆蓋區,於是被正確地刪掉,twin 隨即停更。
- **證據**:
  1. 義務句 `README.md:263-265`(§6 重生規則):
     ```
     gate 時必產;**Stage 5 於 tasks 定稿(供 start 解析/派工)時必產、
     Stage 6 於全 T 完成(bookkeeping commit 前)必產 —— 1~7 每階段終態皆有 twin,
     不因「本階段無 gate」省略**
     ```
     另 `README.md:270` 加碼「每站 html 至少一張圖」。
  2. 母版**沒有**產生器:`find _templates -name '*.py' | wc -l` = **0**
     (該目錄 14 檔 = 13 份 `.md` + 1 份 `.html` 殼);全 repo 唯一的 md→html 是
     `scripts/render-methodology-corrections.sh`,它只重生 4 個 tracked outputs
     (兩份 guide + 兩份 example twin)的 parity 引用區,不是通用 twin 產生器
     —— 這 4 個 output 的身分在 §9.4 報告對帳表已更正過一次。
  3. 現場規模:python-prism `docs/dev/run-backup-inventory/4-spec.md` 在缺口被撈到當時是
     **2342 行**(`e621e6c`),現行 `5a0eb81` 上是 **2360 行**。
  4. 該專案自製 `docs/dev/_templates/md2html.py`(183 行),於
     `87c45c0 chore(dev-flow): 刪除 docs/dev/_templates/md2html.py(全樹零引用)` 刪除。
     **刪得對**:`docs/dev/_templates/` 是 dev-setup 的覆蓋區
     (`skills/dev-setup/SKILL.md:73`「只覆蓋 `docs/dev/README.md`、`docs/dev/_templates/`、
     `docs/dev/tools/`」),專案自有腳本放那裡必被 upgrade 沖掉。
  5. 後果:該 feature 的 twin 從 2026-07-31 起停更,直到 agent 以
     `git show 87c45c0^:docs/dev/_templates/md2html.py` 從 history 撈回才重產。
- **影響**:制度正本規定了一個**採用專案沒有手段履行**的義務 —— 與姊妹檔 A-1
  「制度正本規定了採用專案根本跑不了的 CI 入口」是同一族的規則失效,只是這次失效的是
  §6 而非 §1/§7。且每個採用專案都會各自撞一次,各自的解法又都會落進覆蓋區
  (唯一乾淨的留法是 repo root 的 `scripts/`,見姊妹檔附錄第 1 條)。
- **建議修法**:比照 `devflow-evidence-gauntlet.sh` 的形狀 —— 轉換器住母版 `scripts/`,
  由 dev-setup 散發到專案 `docs/dev/tools/`。這條路已經鋪好:install 步 6 就是
  `mkdir -p docs/dev/tools` 後 cp 母版 `scripts/devflow-evidence-gauntlet.sh`
  (`SKILL.md:62-69`),upgrade 覆蓋清單已含 `docs/dev/tools/`(`SKILL.md:73`),
  check 第 9 項還附了「存在 + 可執行 + 與母版 diff 無差異 + 對 fixture 實跑」四道驗證
  (`SKILL.md:143-148`)。放在這一側,它就在「母版可管、專案不自己維護」的正確位置。
- **與姊妹檔的關係(重要,不是重複)**:姊妹檔附錄把「twin 產法是殼檔 + 模型手寫,
  python-prism 的 `md2html.py` 是加速器,刪掉沒有移除任何母版能力」列為**母版不用改**。
  本條**不推翻那句事實描述**(母版確實從來沒有產生器,所以刪掉沒有移除母版能力),
  但把它的**結論**從「母版不用改」改判為「母版該補」—— 理由是 §6 的義務是硬性的,
  而手寫在 2000+ 行的規格上不可行。附錄那條的括號註「(但採用者容易誤以為母版該提供
  產生器)」在本條之後應視為已被現場推翻。
- **一併注意(不在本條範圍,但會影響散發假設)**:python-prism **連 `docs/dev/tools/`
  目錄都不存在**(`ls: No such file or directory`),代表 install 步 6 從未在該專案跑過。
  散發器必須能在 upgrade 時補建目錄,不能假設它已存在。

### F-2(HIGH)— 那支撈回來的轉換器有三個真 bug,母版若要散發須先修

- **現象**:三個 bug 全都讓**內容靜默塌掉**(表變一行純文字、code fence 變一段落),
  不報錯、不 exit 非零;而 twin 正是給人看的那一份。
- **取得方式**:`git -C ~/dev/python-prism show 87c45c0^:docs/dev/_templates/md2html.py`
  (183 行)。以下行號均指這份原碼,實跑對象為 python-prism `5a0eb81` 的檔案。
- **證據(逐條實跑,非推論)**:
  1. **縮排的 code fence 被段落分支吃掉**。原碼 `:56` `if ln.startswith("```")` 與收尾
     `:60` 都只認第 0 欄。實跑 `4-spec.md`(2360 行)產出的 `<p>`:
     ````
     <p>``` estimated_item_count(run, scan) = 1                                     -- run_root（Drive 第一層，每個 run 一個） + Σ over folders in run: 1                                   -- 該 folder 的 report_root + [ 該 scan 觀測到、upload_form=&#x27;single&#x27; 的檔數 ]     -- (a) …</p>
     ````
     (原始輸出為**單一行**,此處原樣貼上、僅在末尾截斷;開頭那三個反引號就是被當成內文
     的 fence 標記。)來源 `4-spec.md:780-792`(S13.6 的額度估算公式,fence 縮排 2 空白)。
     整塊塌成一個
     `<p>`,`--` SQL 註解與其後被併進同一行的程式碼連在一起 —— 讀起來整條公式被註解掉。
  2. **縮排的表格整張塌**。原碼 `:69` `if ln.startswith("|")` 與續列 `:73` 同樣只認第 0 欄。
     實跑同一檔,`4-spec.md:1597-1605`(S23.10 於 `:1562`,縮排 2 空白的七格表,
     格為 ①/①'/②/③/③'/④/④')整張塌成單一段落,連分隔列都變成內文:
     `<p>| 格 | 當前 package 列 | 其 <code>drive_file_id</code> | Drive 查詢結果 | 處置 | |---|---|---|---|---| | <strong>①</strong> | 有 | … |</p>`。
  3. **分隔列有尾隨空白時整張表塌**。原碼 `:69` 的
     `re.match(r"^\|[\s:\-|]+\|$", lines[i+1])` 比對前未 `strip()`,`$` 前必須緊接 `|`,
     分隔列尾隨任何空白即不匹配。合成最小案(`| A | B |` / `|---|---|` 後接三個空白 /
     `| 1 | 2 |`)實跑輸出三行獨立 `<p>`,表消失。
  4. **共同成因**:段落 slurp `:152-154` 的停止條件
     `not lines[i].startswith(("#","|",">","```"))` 只認第 0 欄;而清單續行分支 `:132`
     的 `lines[i].startswith("   ")` 要求 **3** 空白。於是**縮排 2 空白的區塊兩邊都不接**,
     一律落進段落分支被 `.strip()` 後以空白 join。markdown 清單項底下的縮排區塊極常見,
     4-spec 這種「`- **THEN** …` 之下掛公式/表格」的寫法正是模板鼓勵的形狀。
- **⚠️ 對原始回報的一處更正**:原回報把「分隔列尾隨空白」記為 3-prototype E4 對照表塌掉的
  成因。**實測不是** —— `3-prototype.md:247-251` 的 E4 對照表是**縮排 3 空白**,分隔列
  `:248` 無尾隨空白(`grep -cE "^[ ]*\|[ :|-]+\|[ \t]+$"` 對該檔全部 5 個 commit 皆為 0,
  對該 feature 現行 5 份 md 也皆為 0)。它塌掉(實跑確認塌成單一 `<p>| | 1-discussion 的
  估算 | E4 實測推算 | |---|---|---| | 上傳速率 | …`)是上列第 2 點的**縮排**成因。
  尾隨空白 bug 本身確實存在(合成案已證),但 git 史裡查不到它的實例 —— 兩個 bug 都要修,
  歸因要分開記。
- **影響**:若照 F-1 直接把這支腳本搬進母版散發,等於把三個靜默資料遺失 bug 一起散發到
  每個採用專案;而塌掉的表與 fence 正是 4-spec/5-tasks 承載規格的主要載體。
  README §6 也沒有任何「twin 內容須與 md 等價」的檢查可以接住它。
- **建議修法**:
  1. fence 允許縮排,並依 fence 自身的縮排量 dedent body(否則 body 會多帶縮排)。
  2. 表格允許縮排;分隔列比對前 `strip()`。
  3. 段落 slurp 的停止條件改成對 `lstrip()` 後的行判斷,不得吞縮排的 fence 與表格。
  4. **配負向 fixture 再散發**:縮排 fence / 縮排表 / 尾隨空白分隔列各一,放母版
     `scripts/fixtures/`,比照 gauntlet 的負向 fixture 紀律(§3 P3 與 §6 critic 的教訓:
     沒有負向 fixture 的規則可以被刪掉而測試不紅)。否則這三個 bug 修完沒有守衛,
     下一輪編修會照 §7 第 2 點同樣的方式平移回來。

### F-3(MEDIUM)— `diagram-style.md` 是 pilot 新增的畫法正本,但採用專案拿不到且無人發現

- **現象**:README §6 把 `_templates/diagram-style.md` 指定為圖表畫法正本,採用專案的
  `docs/dev/_templates/` 卻沒有這一份;而 dev-setup 的 check 只講「diff」,不講「缺件」,
  所以沒有任何一道檢查會報。
- **⚠️ 對原始回報的一處措辭更正**:原回報寫「採用專案**拿不到**」。實測散發**通道是通的**
  —— upgrade 的覆蓋清單本來就含 `docs/dev/_templates/`(`SKILL.md:73`),跑一次就會到位。
  真正的缺口是兩件事:①該專案自 `90d30e8` 後未再 upgrade,②**缺件沒有任何守衛會報**。
  這個更正會換掉修法:要補的不是散發器,是 check 的**存在性判定**(見下)。
- **證據**:
  1. 母版 `_templates/diagram-style.md` **48 行**,由 `90d30e8`(2026-08-01
     「圖表風格 spec + 兩張新 SVG 圖解」)新增 —— 確實是 pilot 這一輪才進母版的。
     內容:硬規則 4 條(inline SVG 自足 / 顏色一律 CSS 變數 / 11px 字與 `.cap` 說明 /
     整數座標與 `viewBox` ≤1260)、class 約定表、佈局紀律 4 條、範本指引。
  2. **class 約定表實為 9 個**,原回報列的 7 個之外還有 `.m-opus` / `.m-sonnet`
     (模型分層色):`.b`(`:25`)、`.hl`(`:26`)、`.m-opus`/`.m-sonnet`(`:27`)、
     `.flow`(`:28`)、`.cap`(`:29`)、`.session`(`:30`)、`.fenceline`(`:31`)、
     `.note`(`:32`)。
  3. README 的指定句 `README.md:277-278`:「畫法規範(顏色變數/class 約定/佈局紀律,
     不依賴任何 skill 或本機軟體)見 `_templates/diagram-style.md`;新圖先抄現成範本結構
     再改節點。」
  4. python-prism `docs/dev/_templates/` 只有 13 檔,缺 `diagram-style.md`。逐檔
     `git hash-object` 對母版 `HEAD:_templates/*` 比對:**3 檔相同**(`adr.md` /
     `living-spec.md` / `STATUS.md`)、**10 檔漂移**、**1 檔缺件** —— 該專案的模板整體
     早於 `90d30e8`,**至少自 2026-08-01 起未跑過 upgrade**(hash 只證落後,不證從未跑過)。
  5. **散發機制在,偵測不在**:upgrade 覆蓋 `docs/dev/_templates/`(`SKILL.md:73`),
     所以只要跑 upgrade 就會到位;但 check 第 6 項的敘述只有「docs/dev/README 與模板版本
     vs 母版 diff」(`SKILL.md:119-120`),是模型執行的散文條目、無腳本保證,
     對「母版有、專案沒有」這種缺件沒有明確判定 —— 實測結果就是沒人發現。
     對照 gauntlet 的 check 第 9 項①明寫「存在且可執行(缺件 = broken)」
     (`SKILL.md:144-145`),模板這一側少了同級的存在性判定。
- **影響**:專案要畫圖時沒有規範可循、只能各自發揮,正是該檔存在要解決的問題;
  更糟的是就算專案自己去抄母版那份,它引用的 class 在專案殼檔裡也不存在(見 F-4)。
  與姊妹檔 A-1 是同一個散發面的兩個相反症狀:A-1 是「散發了不該散發的(母版內部路徑)」,
  F-3 是「該散發的沒到位、而且沒有守衛會發現」。
- **建議修法**:
  1. check 第 6 項補**檔名集合比對**:母版 `_templates/` 有而專案 `docs/dev/_templates/`
     沒有的檔一律列 broken(同第 9 項①的存在性判定強度),不能只報 diff ——
     新增模板檔是往後每次母版演進都會發生的事,缺件必須是可偵測的。
  2. `diagram-style.md` 是**規範**、`html-shell.html` 是**載體**,兩者必須同一輪散發到位,
     否則規範到了也用不了 —— 見 F-4。

### F-4(MEDIUM)— 散發用的 `html-shell.html` 缺圖表所需的 CSS 變數與 class

- **現象**:`diagram-style.md` 說 class「定義在各 guide/`html-shell` 的 `<style>`,
  直接複用」,但 `_templates/html-shell.html` **一個都沒定義**,連色變數與 `svg text`
  基礎樣式都沒有。
- **⚠️ 對原始回報的一處成因更正(結論不變,問題更嚴重)**:原回報以 python-prism 的
  副本為證。實測該副本(`git hash-object` = `11816e77`)與母版
  (`HEAD:_templates/html-shell.html` = `dabc8b32`)只差 4 行 —— 專案側少了
  `details` / `details>summary` / `.del` / `.add` 四條規則(母版 `:39-42`),
  **`:root` 逐字相同**。也就是說這**不是散發 stale 造成的,是母版殼檔本身就缺**。
  修專案端沒用,要修母版。
- **證據**:
  1. 母版 `_templates/html-shell.html` 共 **50 行**(`wc -l`)。`:root`(`:10-11`)只有八個變數
     `--bg/--fg/--muted/--line/--card/--ok/--warn/--bad`,深色組(`:12-15`)同樣八個。
     **無** `--acc` / `--opus` / `--sonnet`;全檔**無** `.b` / `.hl` / `.m-opus` /
     `.m-sonnet` / `.flow` / `.cap` / `.session` / `.fenceline` / `.note`,
     **無** `svg{max-width:100%}`、**無** `svg text{…11px…}`、**無** `#arrow` marker defs。
     (順帶:它也沒有 `:root[data-theme="dark"|"light"]` 覆寫,只有
     `prefers-color-scheme`。)
  2. 母版 `guide-quickstart.html` **全部都有**:`:8-10` 亮色組
     `--acc:#2563eb;--opus:#7c3aed;--sonnet:#0d9488`、`:11-14` 深色組
     `--acc:#6ea8ff;--opus:#a78bfa;--sonnet:#2dd4bf`(另 `:16-21` 有 `data-theme`
     兩向覆寫);`:47` `svg{max-width:100%;height:auto}`、`:48`
     `svg text{fill:var(--fg);font:11px …}`、`:49-61` 九個 class 全在
     (`.b` `:49`、`.hl` `:50`、`.m-opus`/`.m-sonnet` `:51-52`、`.cap` `:53`、
     `.note` `:54`、`.flow` `:55`、`.fenceline` `:56`、`.session` `:61`)、
     `:697` `<marker id="arrow" …>`。
  3. 落差句在 `_templates/diagram-style.md:21`:「class 約定(定義在各 guide/html-shell
     的 `<style>`,直接複用)」—— **guide 那半句成立,html-shell 那半句不成立**。
  4. **兩處殼檔副本也已不同步**:README.md:298 規定「殼檔有兩處副本
     (`_templates/html-shell.html` 與 dev-talk skill 目錄內),改殼須同步兩處」。實測
     `~/.claude/plugins/local/dev-talk/skills/dev-talk/html-shell.html` 的 hash 是
     `11816e77`,與母版 `dabc8b32` 不同(少同樣那 4 行),**與 python-prism 的副本反而
     byte-identical**。成因可定位到單一 commit:`git show 4cdd68c -- _templates/html-shell.html`
     的 index 行正是 `11816e7..dabc8b3`、+4/−0 —— 即 `4cdd68c`(2026-07-31
     "docs: resolve final methodology review findings")改了母版殼檔,沒同步 dev-talk 那份。
  5. **母版自己的 example twin 也沒有** —— 這點推翻了「照範例抄就好」這條退路:
     `example/contract-expiry-reminder/` 七份 html **每一份的 `--` 變數集合都與
     `html-shell.html` 逐字相同的那八個**(`--bad --bg --card --fg --line --muted --ok
     --warn`),`grep -c '<svg'` 全部 **0**,圖一律走 ASCII `<pre>`
     (1/2/3/5-discussion~tasks 各 1 個 `<pre>`、4-spec 2 個、6-notes 12 個、7-review 10 個)。
     全 repo 帶那批圖表 CSS 的只有兩份 guide(`guide-quickstart.html`、
     `guide-dev-flow.html`)。也就是說 `diagram-style.md` 要人「先抄現成範本結構」
     (`:44-48`)時,唯二可抄的來源是兩份 guide,而它們不是 twin、不吃殼檔。
- **影響**:任何照 `diagram-style.md` 畫圖的人(**除了兩份 guide 以外的所有 html**,
  含母版自己的七份 example twin)會發現引用的 class 在自己的殼裡不存在。
  結果不是「圖畫得不好看」,是**完全沒有樣式**:
  `.b` 無底色、`.flow` 無線寬、箭頭沒有 marker、`svg text` 沒有 `11px` 也沒有
  `fill:var(--fg)` → 落回瀏覽器預設黑字,深色主題下直接違反 `diagram-style.md` 硬規則 2
  (禁深底深字)與硬規則 3(11px)。而 README §6 規定「每站 html 至少一張圖」+ 每階段終態
  皆須有 twin,等於**每個階段的 twin 都會撞到**。
- **建議修法**:
  1. 把 `guide-quickstart.html:8-14` 的三個色變數(深淺兩組)與 `:47-61` 的
     `svg` / `svg text` 基礎樣式 + 九個 class 併進 `_templates/html-shell.html`,
     讓「規範」(F-3)與「載體」同步散發。
  2. `#arrow` marker 依 `diagram-style.md:42`「一張圖一個 defs」本就由圖自帶,殼檔只需
     補 CSS;若要更省事,可在殼檔留一份 defs 範例並在 `diagram-style.md` 註明可複用。
  3. 改殼必**同步 dev-talk 那份副本**(README.md:298),否則 `1-discussion.html`
     會與其餘六站不同風格 —— 而該副本現在就已經落後母版 4 行,建議一併補平。
  4. 補完 CSS 後,**至少讓一份 example twin 真的放一張 SVG** —— 現在七份全是 ASCII、
     零 `<svg>`,`diagram-style.md:44-48`「先抄現成範本結構再改節點」在 twin 這一側
     沒有範本可抄(兩份 guide 不吃殼檔,結構不能直接搬)。
  5. 這條與 F-3 應**同一輪處理**:規範與載體分開散發,採用者仍然畫不出圖。

---

### F-5(MEDIUM) — `diagram-style.md` 沒有「圖表必須可放大」的要求,但母版自己有做

**現象**

`_templates/diagram-style.md` 全文 48 行,`grep -niE "放大|zoom|pan|全螢幕|檢視"` **零命中**。
規範第 4 條只寫「`viewBox` 寬 ≤1260;圖寬超過容器靠頁面 `svg{max-width:100%}` 縮放與
`.tablewrap` 式水平捲動,禁縮小字級硬塞」——**縮放不等於可放大**。

**證據**

| 檔 | `zoom|pan|fullscreen|全螢幕|放大` 命中數 |
|---|---|
| `_templates/diagram-style.md`(規範正本) | **0** |
| `guide-quickstart.html`(母版自己的產出) | **37** |

母版自己知道要做 pan-zoom,但**沒有把它寫進散發給採用專案的規範**。

**影響**

`viewBox` 上限 1260,而散發用 `_templates/html-shell.html` 的 `main{max-width:880px}`。
一張接近上限的圖(如本輪 python-prism 的系統 block 圖 14 框 / T 依賴 DAG 19 節點)
在 880px 容器內會被壓到約 0.70 倍,11px 的節點標籤實際渲染約 7.7px。
採用專案照規範畫,得到的是一張**符合規範但讀不了**的圖;要補救只能自己想辦法,
而規範第 4 條還明文禁止「縮小字級硬塞」,等於把唯一的土法也堵掉。

**建議修法**

1. `diagram-style.md` 增一條硬規則:「**圖表必須可放大檢視**(點擊全螢幕 / pan-zoom);
   實作限 inline JS/CSS,不得引外部庫(與硬規則 1 一致)」。
2. 把 `guide-quickstart.html` 既有的那套 pan-zoom 抽成可抄的最小範本,
   隨 `html-shell.html` 一起散發(與 F-4 同一輪處理——規範、載體、範本三者要一起到)。

> 交叉引用:本條與 **F-4**(殼檔缺圖表 CSS)是同一個成因的兩面——
> 母版把「規範」散發出去,但「載體」與「範本」留在自己的 guide 裡。

---

### F-6(MEDIUM) — `diagram-style.md` 定了風格但沒定驗證,而採用專案已經出過三類幾何缺陷

**現象**

`_templates/diagram-style.md` 有硬規則、class 約定、佈局紀律、範本四段,
但 `grep -niE "lint|驗證|檢查|verify"` **零命中** ——
**畫完之後沒有任何機械檢查要求**。

**證據(一手來源在使用者的全域規則,不在本 repo)**

`~/.claude/rules/artifact-diagram.md` 第 4 條「手寫 inline SVG 圖必過幾何檢查
(2026-08-01 教訓)」原文:

> draw.io 系 skill(diagram-pro / clean-routed-diagrams)的 verify 迴圈只在 draw.io 流程觸發;
> Artifact 內嵌的手寫 SVG 是守備空窗——曾發生 **12 表架構圖邊線懸空、穿框、壓字三類缺陷同時存在**
> (腦算座標、無驗證迴圈,**且缺陷會被後續編修者平移繼承**)。

那張 12 表架構圖就是 **CRM `icryobank-crm-api-golang` 的 `docs/dev/order-intake/2-decision.html`**
——一個走 dev-flow 的採用專案、照 dev-flow 的規範畫圖,出了三類幾何缺陷。

該規則同時記載了已存在的工具:`~/.claude/scripts/svg-diagram-lint.py`(7,020 bytes),
檢查 ENDPOINT(端點落框邊)/ THRU-BOX(線不穿框)/ THRU-TEXT(線不壓字)/
TEXT-TEXT(文字不互疊)/ TEXT-BOX(框外標註不壓框)/ OVERFLOW(欄位不溢框)/
VIEWBOX(全部落在 viewBox 內),report-only 不改檔。

**本輪實證有效**:python-prism 的 `_review-overview.html` 八張 inline SVG
(fig1 / fig2 / fig3 / fig4a / fig4b / fig4c / fig5 / fig6)逐張跑該工具,
全部 `ALL CHECKS PASS` / exit 0(boxes 5–19、paths 4–22、texts 10–40 皆非零,
證明檢查確實跑到)。若沒有這道閘,上述三類缺陷不會有任何機制擋下。

**影響**

這條與 **F-1** 是同一個形狀:**母版定了要求,但沒給工具**。
差別在 F-1 的缺件會讓人發現(twin 產不出來),本條的缺件**不會**——
畫出來的圖照樣能看,缺陷要有人逐張比對座標才抓得到,
而規範明文承認「缺陷會被後續編修者平移繼承」。

**建議修法**

1. `diagram-style.md` 增一條收尾規則:「**畫完或編修 SVG 圖後必跑幾何檢查,exit 0 才算畫完**;
   編修既有圖先跑一次拿基線(既有圖可能本來就有缺陷,別當正確範本照抄);
   90° 直角十字交叉不算缺陷」。
2. 工具比照 `devflow-evidence-gauntlet.sh` 的形狀散發:住母版 `scripts/`,
   由 dev-setup 複製到專案 `docs/dev/tools/` 並 `chmod +x`,
   doctor 的散發檢查一併涵蓋(現行第 9 項只檢 gauntlet)。
3. ⚠️ 移植時注意工具目前的啟發式限制(其 `--help` 自述):文字寬度為估算值、
   只驗 M/L 直線段、曲線以整體 bbox 保守判定。散發前應在母版既有的
   `guide-*.html` 上跑一次取得基線,確認不會對母版自己的圖產生大量偽陽性。

> 交叉引用:**F-1 / F-5 / F-6 同屬「母版定了要求但沒給工具/範本」**這一類,
> 建議合併成一個 remediation 批次處理:轉換器(F-1)、pan-zoom 範本(F-5)、
> 幾何 lint(F-6)三者都走 `scripts/` → dev-setup 散發 → `docs/dev/tools/` 的同一條通道。
