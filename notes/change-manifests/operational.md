# Change Manifest — Workstream B(Real-world Interaction / Stage 3 Demo)

> Branch:`devflow-vnext/operational`(base 90d30e88294ab4168871a877ef8ffc398ec3b817)。
> 設計文件:`notes/design/real-world-interaction.md`。
> 本檔給 Integrator:已落地變更清單 + 檔案所有權外的待整合條文 + 待重生 twin + 測試證據。

## 已落地(本 branch commits)

| SHA | 內容 |
|---|---|
| 573ae58 | scripts/check-realworld.sh 十二節檢查(先測試:RED 10/126) |
| 4514e4e | _templates/1-discussion.md(Real-world Context)、3-prototype.md(觸發判定/Demo/Demo Script/User Demo Feedback)、4-spec.md(Operational Context) |
| bf3c20b | example contract-expiry-reminder Stage 1/3/4 示範 + 檢查附著形式精修(GREEN 133/133) |
| a2b4ea1 | notes/design/real-world-interaction.md |
| (本檔 commit) | notes/change-manifests/operational.md — SHA 見 `git log -1` |

parity 鎖定區(3-prototype 執行清單、4-spec 反模糊三律/執行清單)**零改動**,
guide-*.html 與 README 未觸碰;74/74 與 renderer 4/4 全程維持綠。

## Stage 5 待整合(不動 _templates/5-tasks.md,由 Integrator 加入)

5-tasks 模板「T 格式」註解(或 Context Packet 規則區)加入:

```markdown
Task Context Packet 規則(真實世界互動):
- 每個 Task 只帶與該 T 有關的**最小** Operational Context 子集(從 4-spec 該 T Covers
  的 S 摘錄):Actor、Goal、Human decision、Authority、External dependency、
  Out-of-system action、Waiting/recovery、不得誤導使用者的事項(如:看過 ≠ 完成、
  「已續約」僅主管可標)。
- 禁把 1-discussion 訪談逐字稿 / 完整 Real-world Context 丟給 Haiku;執行層只吃摘錄。
```

## Stage 7 待整合(不動 _templates/7-review.md,由 Integrator 加入)

新增節(建議放現象證據表之後):

```markdown
## Operational Walkthrough
<!-- reviewer 以各 S 的 Operational Context 為腳本,親自走一遍「人的工作」;
     逐列檢查:技術上通過但人無法完成工作 / 看得到但沒有決策權 / 系統把等待誤標為完成 /
     系統外動作無法追蹤 / 使用者中斷後無法恢復 / 資訊過期、缺漏或多人同時操作 -->
| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
```

Reviewer 檢查義務六條(上方註解內文)須同步進 7-review 執行清單或 Exit Checklist——
Exit Checklist 是 renderer 抽取源(template7-exit-quickstart),改後須 renderer --write。

## README 待整合(正本所有權外,建議文字)

- §3 階段表 Stage 3 行:補「命中觸發判定(前端/交接/核准/等待/權限/系統外/多互動設計)
  → 條件式必要,產可操作 Demo + User Demo Feedback(Human verdict 人類親填)」。
- §5 或 §7:一句 gate 級規則「3-prototype Human verdict ≠ ACCEPTED → 相關互動 S 不得於
  G2 定案;NOT_REVIEWED ≠ ACCEPTED」。若入 §7 正本,注意粗體 gate 錨與 gate-consistency
  機械比對(plugin `_gate_consistency_impl.py`),須 coordinator 協調 plugin 側同跑。
- §3 表為 renderer 抽取源(readme-stage-table)→ 改後 renderer --write。

## 執行清單(parity 鎖定區)待整合

3-prototype/4-spec 的執行清單住 guide-dev-flow.html parity 區(Guide 非本 workstream
所有權),故本次未改。建議條文:

- 3-prototype 執行清單:step 0 前加「-1. 觸發判定:對照 1-discussion Real-world Context
  逐條打勾;命中→條件式必要。完成 = 觸發判定節落檔」;step 2 後加「2.5 Demo:依 Method
  的 Demo 形式讓使用者實際操作各 variant,走完 Demo Script;回饋記 User Demo Feedback,
  Human verdict 由人類親填。完成 = verdict 非空且非 Agent 代答」;step 4 收尾補
  「verdict=ACCEPTED(或人類明示中止)才可 status=approved」。
- 4-spec 執行清單 step 2:補「涉人員操作的重要 S 同步填 Operational Context 13 欄」。
- 以上落地後跑 `render-methodology-corrections.sh --write` 重生 guide-dev-flow.html
  對應 parity 區(template3-checklist / template4-checklist)。

## Guide/HTML 待重生

| 檔 | 原因 | 重生方式 |
|---|---|---|
| example/contract-expiry-reminder/1-discussion.html | 1-discussion.md 大改(Real-world Context/AC-4/AC-5)| AI 手工 twin,依 README §6 + html-shell.html 重寫 |
| example/contract-expiry-reminder/4-spec.html | 4-spec.md 大改(OC/R-3/S-4~S-6)| 同上 |
| example/contract-expiry-reminder/3-prototype.html | **原本就不存在**(模板要求終態必產);3-prototype.md 已大改 | 新建 AI 手工 twin(必含 variant 圖、Demo Script、User Demo Feedback、Verdict) |
| guide-dev-flow.html(template3/template4 parity 區) | 僅當上節執行清單條文落地後 | renderer --write(非手改) |
| plugin skills/dev-flow、dev-run SKILL.md | 階段動作表含 Stage 3 新義務 | 另 repo(/Users/asheng/.claude/plugins/local/dev-flow/),coordinator 另派 |

## 範例變更(example/contract-expiry-reminder)

- `1-discussion.md`:+Real-world Context(4 Actors 含系統外法務/外部窗口;5 步 Journey;
  Workarounds;6 Exceptions 含「SOP=先法務後簽 vs 實際=急件先口頭續」並記;Evidence 含
  2 條 [Assumption]);+Goal 3、Non-Goal(不做 workflow 引擎)、Q4(看過≠處理)、
  Q5(已續約僅主管)、AC-4/AC-5、邏輯圖狀態分支、Interview Log real-world 段。
- `3-prototype.md`:觸發判定命中 8/9 → 條件式必要;3 個結構不同 variant(A badge 二層
  /B 卡片列內/C 詳情時間軸);Demo=可點擊 HTML prototype(throwaway、假資料、已刪);
  Demo Script 7 場景錨定 AC-id(等待法務/等待主管+已聯絡供應商+中斷恢復/權限不足/空
  /錯誤/資料過期/看過≠完成);User Demo Feedback 標注**示範值**:第 1 輪 REVISE
  (圖示混淆、缺最後動作時間、權限誤導)→ 修正後第 2 輪 ACCEPTED。
- `4-spec.md`:S-1/S-2 附 13 欄 Operational Context,S-3 註不適用+理由;+R-3
  (S-4 標記狀態+歷程、S-5 看過不改狀態、S-6 已續約僅主管)各附 OC;流程圖+R-3、
  AC 擴至 S-6、Out of Scope+3 項、Diff Budget ≤9 檔/≤600 行、Dependencies 改「需
  migration(renewal_status enum+歷程表)」、DD+3 條、Skeleton+S-5、確認紀錄+1 行。
- **未同步(所有權外,Integrator 處理)**:example 5-tasks/6-notes/7-review 未涵蓋
  S-4~S-6(現 T×S 檢查仍綠,因其只比對 5-tasks Covers ↔ 6-notes evidence);7-review
  的 S 級現象表僅至 S-3。同步時注意 check 腳本硬斷言(actor 字串、T×S 集合)僅可
  additive 修改。

## 測試原始輸出

基線(開工,@ 90d30e8):

```
✅ methodology correction checks: 74/74 passed
✅ renderer fixed point: 4/4 tracked outputs byte-identical
```

RED(check-realworld.sh 首跑,模板未改,@ 573ae58;完整 117 行存 session scratchpad):

```
❌ real-world interaction checks: 10/126 passed
  - template 1-discussion 含 ## Real-world Context
  - template 3-prototype 含條件式必要語意
  - template Operational Context 欄位「Actor:」
  …(共 116 條失敗,涵蓋十二節全部檢查群)
```

GREEN(實作後;附著檢查精修 +7 條 → 133):

```
✅ real-world interaction checks: 133/133 passed
✅ methodology correction checks: 74/74 passed
✅ renderer fixed point: 4/4 tracked outputs byte-identical
```

收工複跑(最終 HEAD)輸出同上三行(見 Workstream B 完工回報)。

## 不採用的建議(附理由)

1. **example 附 throwaway HTML prototype 實檔**:不採。與既有範例「原型閱後即焚,不留
   code」語意一致,且 example 目錄多 html 易與 twin 機制混淆;以模板規則完整為優先
   (Prompt B 邊界允許)。
2. **Demo Script 用 `### Scenario S-?` 原字**:調整為「AC-id 或 S-id」。Stage 3 時
   4-spec 尚未存在,S-id 是時代錯置;AC 是 1-discussion 既有種子 ID,非第二鏈。
3. **直接改 3-prototype/4-spec 執行清單**:不採(本輪)。該區是 guide-dev-flow.html
   parity 抽取源,Guide 在本 workstream 禁改清單上;條文備妥於上方待整合節。

## Commit SHA

- Base:90d30e88294ab4168871a877ef8ffc398ec3b817
- 573ae58 → 4514e4e → bf3c20b → a2b4ea1 → 本檔 commit(HEAD,見完工回報)
