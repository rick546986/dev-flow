# Real-world Interaction 設計(Workstream B)

> 狀態:設計文件(非規則正本)。規則落地位置=_templates/1-discussion.md、
> _templates/3-prototype.md、_templates/4-spec.md;機械檢查=scripts/check-realworld.sh。
> Stage 5/7/README/Guide 的配套變更已於 VNext 整合輪落地(README §5/§7 與模板現版;
> 2026-08-02);當時清單留存 notes/change-manifests/operational.md 供考古。
> 依據:DevFlow 四軌並行改造 Prompt B(2026-08-02)+ 00-audit.md 護欄。

## 1. 目標與動機

DevFlow 既有文件鏈(R → S → T → test → D → F)描述「系統規則」很強,但對「人在什麼
情境下使用、掌握/缺少哪些資訊、要等誰、有哪些權限、用哪些系統外工具、如何中斷/恢復/
退回/例外」零捕捉(audit:Demo/Actor/Operational/Journey 全 repo 零命中)。後果:
**技術上通過但人無法完成工作**的產出可以一路綠燈出廠。

本設計把真實世界互動塞進三個既有階段,不新增階段、不新增 ID 鏈:

| 階段 | 新增物 | 回答的問題 |
|---|---|---|
| Stage 1 | Real-world Context 節 | 人現在怎麼真的完成這件工作? |
| Stage 3 | 觸發判定 + 可操作 Demo + Human verdict | 人操作得下去嗎?由人說了算 |
| Stage 4 | S 級 Operational Context | 系統做什麼之外,人看到後要做什麼? |

## 2. 原則

1. **單一 ID 鏈**:保留 R → S → T → test → D → F。不發 Journey/Actor/Interaction
   專屬 ID;真實世界資訊在 Stage 1 以文字附著,Stage 4 以 Operational Context 附著於
   S-id,Stage 3 Demo 場景錨定既有 AC-id(4-spec 未生時)或 S-id。
2. **Assumption 與 Evidence 可機械區分**:未有證據的敘述標 `[Assumption]`;不得把推測
   寫成事實;正式 SOP 與實際做法不同時兩者都記;醫療/個資只留去識別化內容。
3. **Human verdict 人類主權**:Demo 的 ACCEPTED/REVISE/NOT_REVIEWED 由參與 Demo 的
   人類親填,Agent 不得代答;NOT_REVIEWED ≠ ACCEPTED;REVISE 必須重新 Demo;
   verdict ≠ ACCEPTED → 4-spec 不得把互動定案。
4. **銜接既有能力,不平行再造**(audit「勿重造」清單):Demo 建在 Stage 3 既有
   2-4 variants 節之上(加「結構不同」判準與 11 必含狀態);操作驗證銜接 Stage 7
   既有現象複驗與 4-spec 觀測欄,不另立 evidence 體系。

## 3. Stage 1:Real-world Context(已落地)

`_templates/1-discussion.md` 新增 `## Real-world Context`,五個子節:

- **Actors 表**:Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具。
  系統外角色(法務、外部窗口)也要列,權限欄寫「系統外」。
- **Current Journey 表**:Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點。
  記「沒有這個功能時」的現況;SOP 與實際做法不同 → 各記一段。
- **Workarounds**:Excel/LINE/Email/紙本/電話/口頭交接;哪些步驟無紀錄。
- **Exceptions**:誰可跳過、資料不完整、對方不回、中斷恢復、重複/撤回/改派/多人同時。
- **Evidence**:實際案例/訪談/SOP/去識別化 log/表單/畫面/客服問題;訪談優先問
  「最近一次真的發生時怎麼處理」。

此節是 Stage 3 觸發判定與 Stage 4 Operational Context 的上游輸入。

## 4. Stage 3:觸發判定 + Demo + Human verdict(已落地)

**觸發判定(條件式必要)**:Stage 3 對純後端、無互動風險 feature 維持選配。
命中九條之一(新前端流程/改變下一步/角色交接/人工核准/等待退回逾時/權限差異/
系統外動作/多種互動設計/操作流程不確定)→ 條件式必要。命中仍要跳過 → 人類明示 +
2-decision Owner Call + 記跳過風險;Agent 不得代決。

**可操作 Demo**:不只產文件。形式六選一(HTML prototype / throwaway route /
Storybook / CLI flow / API mock+UI / 狀態流程模擬器)。鐵則:不直接變 production、
throwaway scope、不污染正式資料、假資料或去識別化、標示非正式 code、使用者實際操作。

**Variant**:互動問題存在時 2-4 個「結構不同」variant(不同操作順序/資訊階層/決策點/
等待交接呈現/錯誤恢復;禁同版面換色)。每 variant 必含 11 狀態:主要角色、真實目標、
入口、關鍵操作、等待狀態、空狀態、錯誤狀態、權限不足、資料過期、中斷恢復、系統外下一步。

**Demo Script**:一場景一段,錨定 AC-id/S-id;逐場確認六問(知道下一步?暗示不存在的
權限?等待清楚?系統外交接可追蹤?資訊不完整知道怎辦?能撤回重試改派恢復?)。

**User Demo Feedback**:11 欄 + `Human verdict: ACCEPTED | REVISE | NOT_REVIEWED`。
verdict 語意 = 小型狀態機:未 Demo=NOT_REVIEWED(不得視同 ACCEPTED)→ Demo →
ACCEPTED(可進 Stage 4 定案)或 REVISE(必須修改後重新 Demo)。3-prototype
frontmatter status 只有在 verdict=ACCEPTED(或人類明示中止)才可 approved
(check-realworld.sh 機械驗 status=approved → verdict=ACCEPTED)。

## 5. Stage 4:Operational Context(已落地)

重要 S(涉人員操作/交接/等待/權限)必附 13 欄:Actor / Goal / Situation /
Known information / Missing information / Human decision / Authority /
External dependency / Out-of-system action / Waiting/timeout behavior / Recovery /
Audit/handoff requirement / Observation。純內部行為 S 寫「不適用 + 一句理由」。
GIVEN/WHEN/THEN 照舊保留;每個重要 S 須答得出五問:系統要做什麼?人看到後要做什麼?
誰有權決定?哪些事情不在系統內發生?外部事情沒完成時,系統顯示什麼?

## 6. Stage 5/7:僅契約(已於 VNext 整合輪落地,README §5/§7 與模板現版;2026-08-02。原正文見 manifest)

- Stage 5:Task Context Packet 只帶該 T 相關的最小 Operational Context 子集
  (Actor/Goal/Human decision/Authority/External dependency/Out-of-system action/
  Waiting-recovery/不得誤導使用者事項);禁把訪談逐字稿丟給 Haiku。
- Stage 7:Operational Walkthrough 表(S-id|角色|真實目標|系統操作|系統外步驟|
  等待/例外|結果)+ reviewer 六查(技術過但人做不完/看得到沒決策權/等待誤標完成/
  系統外不可追蹤/中斷無法恢復/資訊過期缺漏並發)。

## 7. 機械檢查:scripts/check-realworld.sh(已落地)

獨立新檔,不動既有 74 檢查。133 條,對應 prompt 十二節:

| 檢查群 | 驗什麼 |
|---|---|
| Real-world Context 欄位 | 模板+範例六節齊、兩表頭欄位齊、範例 ≥3 actor ≥4 步 |
| Assumption/Evidence | 模板有標記規則;範例有 [Assumption] 與訪談證據並存 |
| Stage 3 觸發 | 九條件、Owner Call、禁代決;範例有判定節+命中標記 |
| Demo + verdict | Demo Script 7 欄、六問、六形式、鐵則、variant 規則、11 狀態、UDF 11 欄、枚舉三值;範例 ≥5 場景、7 示範狀態、示範標注 |
| NOT_REVIEWED ≠ ACCEPTED | 規則文字 + 機械:status=approved → verdict=ACCEPTED |
| Operational Context | 模板 13 欄+五問;範例附著形式必在 #### S- 下、≥3 個已填 |
| 無第二 ID 鏈 | 六檔禁 J-/JNY-/ACT-/IX-/AID-/JID- 數字 ID |
| 純後端可跳過 | H1 保留「選配」、「純後端」明示、跳過路徑字樣仍在 |
| 舊模板可渲染 | 委派 renderer --check(4/4 byte-identical) |

## 8. 範例示範重點(contract-expiry-reminder)

敘事鏈:負責人看到到期提醒 → 標「等待法務」(系統外 Email)→ 等待主管口頭核 →
電話已聯絡供應商 → 系統只記目前狀態與下一步(誰/何時/舊→新歷程)→ 看過提醒不改
狀態(S-5)、「已續約」僅主管可標(S-6)。Demo 展示七狀態:等待法務、等待主管、
已聯絡供應商、資料過期、無權限決定、空狀態、錯誤狀態。User Demo Feedback 為
**示範值**(第 1 輪 REVISE → 第 2 輪 ACCEPTED),實案由人類親填。
未附 throwaway HTML prototype 實檔:與既有範例「原型閱後即焚,不留 code」語意一致,
且避免 example 目錄多出易與 twin 混淆的 html;以模板規則完整為優先。

## 9. 邊界與未決(L2/Owner Call,不代答)

1. 3-prototype/4-spec **執行清單步驟增補**(觸發判定、Demo、verdict 收尾入 todo 清單)
   被 guide-dev-flow.html parity 鎖定(Guide 非本 workstream 所有權)→ 條文已備妥於
   manifest,待 integrator 改模板 checklist + renderer --write。
   (已於 VNext 整合輪落地:模板現版清單已含;2026-08-02)
2. example **5/6/7 未同步** S-4~S-6(檔案所有權外)→ manifest 列待整合。
   (已於 VNext 整合輪落地:example 現版已同步 S-4~S-6;2026-08-02)
3. README §3 Stage 3 行、§7 gate 是否納 verdict 條件 → 正本非本 workstream 所有權,
   建議文字在 manifest,由 Owner 裁決。
   (已於 VNext 整合輪落地:README §3/§7 現版已納 Demo verdict;2026-08-02)
4. plugin 側 dev-flow/dev-run SKILL.md 階段動作表同步 → 另 repo,coordinator 另派。
   (已於 VNext 整合輪 P2 落地:plugin _stage3_impl + attestation;2026-08-02)
