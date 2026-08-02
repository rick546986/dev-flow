---
feature: contract-expiry-reminder
stage: 3-prototype
status: approved
owner: <owner>
updated: 2026-07-23
---

# 3. 原型 — 提醒怎麼呈現?處理狀態怎麼標?

## Stage 3 觸發判定(條件式必要)
- [x] 有新的前端流程(dashboard 新卡片 + 狀態標記)
- [x] 改變使用者下一步(登入第一眼決定今天跟催哪件)
- [x] 涉及角色交接(業務 ↔ 主管 ↔ 法務 ↔ 外部窗口)
- [x] 涉及人工核准(「已續約」僅主管可標)
- [x] 涉及等待/退回/逾時(等待法務/等待主管/供應商不回覆)
- [x] 涉及權限差異(業務與主管可標的狀態不同)
- [x] 涉及系統外動作(電話聯絡供應商、Email 法務)
- [x] 涉及多種可行互動設計(badge / 卡片 / 詳情時間軸)
- [ ] Stage 1 尚有操作流程不確定性(Journey 已以訪談定稿)

→ 命中 8 條:Stage 3 條件式必要,執行(不跳過)。

## Question
2-decision Risks 第 2 條:業務接受哪種呈現?sidebar badge(低調)vs dashboard 卡片(顯眼)。
加上 Real-world Context 帶出的互動疑問:續約處理狀態(等待法務/等待主管/已聯絡供應商)
在哪一層標記與呈現?「看過提醒」會不會被誤當「處理完成」?

## Method
- branch:`proto/expiry-ui-variants`(throwaway,不進 main;每檔檔頭標注 `PROTOTYPE — not production code`)
- Demo 形式:可點擊 HTML prototype(靜態假資料 8 筆合約 fixture:到期/空/錯誤三組;無真實客戶資料)
- UI 3 個結構不同的 variants,superpowers visual companion 互動挑:
  - Variant A:sidebar「合約」項紅色數字 badge → 點開 drawer 清單 → 狀態在 drawer 內下拉標記
    (資訊階層:先數字後清單;決策點在 drawer 第二層)
  - Variant B:dashboard 頂部卡片直接列出到期合約(剩餘天數 + 狀態欄 + 下一步欄),列內直接標狀態
    (資訊階層:登入第一眼全攤開;決策點在卡片列)
  - Variant C:dashboard 卡片只列名稱/天數 → 點進詳情頁,以「處理時間軸」標狀態
    (操作順序:先進詳情再決策;決策點最深,但保留完整歷程)
- 三個 variant 皆以同一組 fixture 走完:等待狀態(等待法務/等待主管)、空狀態、錯誤狀態、
  權限不足(業務標「已續約」被拒)、資料過期(開頁後 end_date 已被他人改)、
  中斷恢復(標到一半關頁重開)、系統外下一步(顯示「下一步:電話聯絡供應商」)。

## 結構圖
```
Variant A: sidebar badge(決策在第二層)
  Sidebar[合約 + 紅色數字 badge] -> click -> Drawer[到期清單 + 狀態下拉]

Variant B: dashboard 卡片(選定, 第 2 輪 Demo ACCEPTED)
  Dashboard 頂部 -> ExpiringContractsCard[
    合約名稱 | 剩餘天數 | 狀態(等待法務/…) | 下一步 | 最後動作時間
  ] -> click 列 -> /contracts/:id
       └ 列內標狀態(業務可標等待類/不續約;「已續約」僅主管,他人灰階)

Variant C: 詳情頁時間軸(決策最深,留歷程)
  Dashboard 卡片[名稱|天數] -> click -> /contracts/:id[處理時間軸 + 狀態標記]
```

## Demo Script

### Scenario AC-1/AC-4(看到提醒 → 標「等待法務」)
- 使用者角色:負責業務 `<owner>`
- 真實目標:今天決定要跟催哪件,不漏約
- 起始狀態:fixture 合約 C(剩 10 天,狀態「未處理」)
- 操作步驟:登入 → 看到期卡片 → 對 C 標「等待法務」
- 系統回應:C 列顯示狀態「等待法務」、下一步「等法務回覆條款」、最後動作時間
- 系統外下一步:Email 合約給法務(系統只記狀態與時間,不代發信)
- 觀察問題:標完後知道下一步嗎?等待狀態是否清楚?

### Scenario AC-4(等待主管 → 已聯絡供應商)
- 使用者角色:負責業務 `<owner>`
- 真實目標:法務回覆後推進續約
- 起始狀態:合約 C 狀態「等待法務」
- 操作步驟:改標「等待主管」→ 主管口頭同意 → 改標「已聯絡供應商」
- 系統回應:狀態逐步更新,每步留誰/何時;下一步隨狀態換(「等主管拍板」→「等供應商回覆」)
- 系統外下一步:電話聯絡供應商窗口(系統外交接,系統顯示「已聯絡供應商 + 時間」供追蹤)
- 觀察問題:系統外交接是否可追蹤?中斷後(關頁重開)狀態是否保留、能否接續?

### Scenario AC-4(權限不足:業務標「已續約」)
- 使用者角色:負責業務 `<owner>`(非主管)
- 真實目標:談成後想直接結案
- 起始狀態:合約 C 狀態「已聯絡供應商」
- 操作步驟:嘗試標「已續約」
- 系統回應:拒絕,顯示「已續約僅主管可標」,選項灰階,狀態不變
- 系統外下一步:LINE 通知主管來標定案
- 觀察問題:系統是否暗示了不存在的權限?被拒後知道找誰嗎?

### Scenario AC-2(空狀態)
- 使用者角色:名下無到期合約的業務
- 真實目標:確認今天不用跟催
- 起始狀態:fixture 空組
- 操作步驟:登入 → 看卡片
- 系統回應:「近期無到期合約」,無錯誤
- 系統外下一步:無
- 觀察問題:空狀態會不會被誤讀成「壞掉了」?

### Scenario AC-1(錯誤狀態:expiring 查詢失敗)
- 使用者角色:負責業務 `<owner>`
- 真實目標:照常確認到期清單
- 起始狀態:fixture 錯誤組(API 回 500)
- 操作步驟:登入 → 看卡片
- 系統回應:卡片顯示查詢失敗與重試按鈕,不顯示空狀態(避免誤判為無到期)
- 系統外下一步:失敗期間回退 Excel 私表(workaround 仍在,系統不得假裝沒事)
- 觀察問題:錯誤與空狀態是否可區分?能否重試?

### Scenario AC-1(資料過期)
- 使用者角色:負責業務 `<owner>`
- 真實目標:憑卡片資訊聯絡對方
- 起始狀態:卡片開著隔夜,期間主管已把 C 的 end_date 展延
- 操作步驟:直接在昨日畫面上操作 C
- 系統回應:偵測資料已變,提示重新整理後再操作,拒絕以過期資料標狀態
- 系統外下一步:無(避免拿舊資訊誤聯絡對方)
- 觀察問題:資訊不完整/過期時,使用者知道怎麼辦嗎?

### Scenario AC-5(看過 ≠ 完成)
- 使用者角色:負責業務 `<owner>`
- 真實目標:確認系統不會替我「已讀即處理」
- 起始狀態:合約 C 狀態「未處理」
- 操作步驟:開 dashboard 看過卡片兩次,不做任何標記
- 系統回應:C 狀態仍「未處理」;不存在任何因「看過」而改變狀態的行為
- 系統外下一步:無
- 觀察問題:參與者是否理解「看過提醒 ≠ 完成續約」?

## Result
- UI 形式:業務主管 + 2 位業務實測選 **B**(companion events:B 被選 3/3)。
  理由:badge 要多點一層才看得到,「登入第一眼」是需求本體;C 的時間軸降級為詳情頁補充,不做主入口。
- 狀態互動:7 個狀態場景(等待法務/等待主管/已聯絡供應商/權限不足/空/錯誤/資料過期)三 variant 全走過,
  第 1 輪發現三處修正(見 User Demo Feedback),修正後第 2 輪 Demo 通過。
- 「看過 ≠ 完成」:AC-5 場景 3/3 參與者確認看過卡片狀態不變,符合預期。

## User Demo Feedback
(以下為**示範值** —— 實案由參與 Demo 的人類親填,Agent 不得代答)
- Demo date: 2026-07-23(第 1 輪上午 REVISE;修正後下午第 2 輪)
- Participants: 業務主管、業務 ×2(皆實際操作 prototype,非旁觀)
- Variant reviewed: A / B / C 全部,各走完 7 個狀態場景
- Accepted interaction: B(卡片列內標狀態 + 下一步欄 + 最後動作時間)
- Rejected interaction: A(badge 多一層,違背「登入第一眼」);C(標個狀態要先進詳情,太深)
- Confusions observed: 「等待法務」與「等待主管」圖示太像,2/3 分不清 → 等待對象改用文字不用圖示;下一步文案「等回覆」太模糊 → 改「等法務回覆條款」
- Missing real-world steps: 實務會記「何時聯絡過供應商」→ 狀態需帶最後動作時間(第 1 輪 prototype 缺此欄)
- Permission corrections: 第 1 輪 B 讓業務標「已續約」直接成功 —— 暗示了不存在的權限;修正為僅主管可標,業務見灰階 + 提示
- External handoffs: 「下一步:電話聯絡供應商」為系統外動作;系統只記「已聯絡供應商 + 誰 + 時間」,參與者確認可追蹤、改派後接得起來
- Required changes: 等待對象文字化、加最後動作時間欄、「已續約」權限灰階(三項均已修正並於第 2 輪複驗)
- Human verdict: ACCEPTED(第 2 輪;第 1 輪為 REVISE,修正上列三項後重新 Demo)
- Verdict attestation: human:業務主管 @ 2026-07-23(test-only human fixture;示範值 —— 實案由人類親填姓名與日期,檔內不得含此標記)

## Verdict
- 回寫 2-decision Risks:UI 形式已定 → dashboard 卡片(列內標狀態 + 下一步 + 最後動作時間);
  「已續約」僅主管可標、看過不改狀態 → 帶入 4-spec(R-3 / Operational Context)。
- 互動不確定性:已由第 2 輪 Demo ACCEPTED 解除,4-spec 可據此定案。
- branch `proto/expiry-ui-variants` 已刪;HTML prototype 為 throwaway,閱後即焚,
  結構已錄於上方結構圖節(原型不留 code)。
