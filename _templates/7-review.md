---
feature: <slug>
stage: 7-review
status: draft
verdict:             # PRE-REVIEW | REQUEST_CHANGES | PASS(步 0a:自審一律 PRE-REVIEW)
owner:               # reviewer,不可 = 實作 owner
updated:
---

# 7. 驗證

> ## Reviewer 閱讀動線(**必留;給看的人,不是給寫的人**)
>
> 2026-08-13 補。起因:order-intake 的 7-review 長到 95k 字,owner 問「這麼雜我要
> 怎麼審、從哪開始」——**模板原本只有寫作順序(執行清單步 0~5),沒有閱讀順序**,
> 所以文件沒告訴他從哪切入。以下五步固定,產文件時逐字保留、只換數字:
>
> | 步 | 讀哪節 | 這步問的唯一問題 |
> |---|---|---|
> | 1 | **Verdict** | 判定是什麼?門檻表每一格是不是都有證據? |
> | 2 | **Exit Checklist** | 還缺什麼才能出貨?哪幾項要 owner 親自動? |
> | 3 | **附錄:本輪特有** | 本輪的爭點/分歧在哪,誰對? |
> | 4 | **Known Limits** | 有沒有一條是 owner 不能接受的? |
> | 5 | **抽驗一列** | 從 Coverage Matrix / Standards Axis / Spec Axis 任挑一列,照它給的 `檔:行` 去看。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。
>
> 用途:**G3 出貨關卡**。雙軸審(mattpocock):Standards = 通用品質、Spec = 逐條對
> 4-spec。本次 S 全綠 + **既有測試全綠(回歸)** + 無 🔴 才 PASS。
> **出貨樹=審過的樹**:整合回歸(改 HEAD)必須在 Final Fresh 之前;Verdict 後改碼
> 作廢 G3。過 gate 後產 7-review.html 供報告。
> 本階段固定產出:`7-review.md`(本模板全節)+ `7-review.html`(G3 必產;必含
> 變更架構圖、F-id 分級表、現象證據表、全 branch diff 折疊 + 執行記錄表)。
> **就這兩個檔,不多不少。禁止長出 `7-review-<誰>.md`、`7-self-review.md` 這類並存檔**
> —— 兩份同 stage 產物 = gate 讀哪一份沒有定義(2026-08-13 order-intake 實際發生)。
>
> ## G3 twin 是**審查介面**,不是文件視覺版(README §6)
>
> 2026-08-15 補(與 2-decision/4-spec 兩份對齊)。上面那五步是**md 側**的閱讀動線,
> html 側要把它做成可點的 —— **兩邊講同一件事、md 是正本**。三件事缺一不可:
>
> | | 要求 | 這一站的內容 |
> |---|---|---|
> | 1 | **動線頂區五格**,每格一句話 + 可點跳轉 | 判定(frontmatter `verdict:`)/ 出貨(Exit Checklist `x/y`)/ 爭點(「附錄:本輪特有」幾條)/ 風險(Known Limits 幾條)/ 抽驗(Coverage Matrix 中位列 `檔:行`,決定論、可重現)—— **與上面五步一一對應** |
> | 2 | **待審項目逐條可勾**,有進度計數 | 現象證據逐 S、Coverage Matrix 逐列、Exit Checklist 逐項 |
> | 3 | **背景資料摺疊**(`<details>`,預設收合、內容零刪減) | Verification Evidence、雙軸、變更架構圖、Diff |
>
> **Verdict / Known Limits / 限制聲明一律置頂不摺疊** —— 那是判定本身與判定的前提,
> 藏起來等於沒審。產生方式:`docs/dev/tools/build-gate-twin.py <專案根> <slug> 7-review`。
>
> 執行清單(開場第一動建成 todo;逐步達成「完成 =」才勾;禁跳項、禁併項):
> 0. 角色+防錨定起手:審查者依序:適格人類 reviewer → fresh-context reviewer Agent →
>    owner 自審(有記錄的最後手段);前兩者皆須 ≠ 實作 owner。先讀
>    4-spec/5-tasks/diff/測試碼,**此刻禁讀 6-notes 的 Self-Review**。
>    建議跑 `devflow-exec.sh review <slug>` 武裝機械圍欄③(選配但建議;沒有 runtime
>    的環境照本節散文紀律):武裝後 Read 本 feature 的 6-implementation-notes.md
>    (含 .html twin)會被 fail-closed 擋下,直到步 4 執行 review-unlock,防止手滑
>    提早讀到 Self-Review;Write/Edit 同時限縮到 7-review*/evidence/,避免審查者
>    順手改到別的 dev-flow 文檔。
>    ⚠️ **「reviewer ≠ 實作 owner」這條機械上擋不住** —— hook 層沒有身分概念
>    (沒有 session id、沒有作者歸屬),加一個查 `owner` 欄位的守衛只會被
>    「打字改個名字」繞過,那比散文更糟(假保證)。真正有效的是**讀取順序**:
>    先自建矩陣、後讀作者主張。故本步的完成條件是**可查的讀取順序**,
>    不是可宣稱的身分。
>    ⚠️ **走 owner 自審這條路時,必須在本檔最前面獨立一節寫明**:
>    ①審查者 = 實作者 ②因此哪些結論可信(機械數字)、哪些打折(F-id 分級、
>    「沒想到的事」)③建議的補救路徑。**沒有這一節的 owner 自審視同未審。**
>    完成 = 讀取順序聲明在案(+ owner 自審時的限制聲明節)。
> 0a. **自審的落點與交棒**(2026-08-13 補;order-intake 實際踩到):
>    - 自審的**預設家在 `6-implementation-notes.md` 的 Self-Review 節**,不是本檔。
>    - 真的需要用 7-review 的形狀寫自審(例如要留矩陣與實跑證據給下一棒)時,
>      **必須**:①`verdict:` 留 `PRE-REVIEW` 不填 PASS/REQUEST_CHANGES
>      ②標題第一行寫明「不是 G3 PASS」③明列建議的 reviewer 路徑。
>      —— 這三件事做到了,自審就是合格的交接文件,不是違規。
>    - **獨立 reviewer 產出後,直接接管 `7-review.md` 本身**(連同 `.html` 重生),
>      把 pre-review 的獨有內容(發現、Known Limits、架構圖、diff)逐項吸收進去;
>      **不另存 sibling**。pre-review 的舊版留在 git 歷史即可,不需要留在工作樹。
>    - verdict = `REQUEST_CHANGES` 時 **`7-review.md` 仍是 gate-of-record**,
>      只是 `status` 停在 `draft`;下一輪修完就地覆蓋同一個檔,輪次寫進本檔的
>      「重驗範圍」節,不開新檔。
> 0b. **守衛武裝自檢**:同 6-notes 步 0 —— 跑 `devflow-exec.sh status` 確認
>    `.devflow/exec.json` 存在。Stage 7 若在未武裝的樹上做,scope 守衛與契約防篡改
>    同樣沉睡,reviewer 可能在不知情下改到 1/2/3/4。
>    ⚠️ 同時跑 `devflow-doctor.sh`(或 `devflow-exec.sh doctor`),`INCOMPATIBLE` 即
>    **停下回報**——沒有任何 Stage 明文要求跑它就沒有人會被 fail-closed 擋下。
>    完成 = `status` 與 `doctor` 兩份輸出都貼進 6-notes(本站沿用同一份記錄,不另開)。
> 1. 自建 Coverage Matrix:grep 測試檔 S-id ↔ 4-spec S 清單,逐列填(缺漏 ❌),
>    末列固定回歸列。完成 = 矩陣全列填畢(未參考作者主張)。
> 2. 親跑驗證:本次 S 測試+既有全套,結果入矩陣。完成 = 兩輸出在案。
> 2b. **現象複驗**:照 4-spec 每 S 的「觀測方式」**親自實跑一次**(後端打真實請求、
>    前端截圖存 `evidence/`、批次看 log/產出檔),填「現象證據」表。不採信 6-notes
>    貼的文字。完成 = 每 S 有實跑證據且與觀測方式相符(無外部現象者註明理由)。
> 2c. **整合回歸**(條件式;這是最後一次准許改程式碼 / 改 HEAD):跑
>    `docs/dev/tools/devflow-integration-regression.sh --integration origin/<整合分支> --fork-sha <6-notes 步 0 記的 FORK_INTEGRATION_SHA>`
>    (整合分支 = `develop` 或 `main`,依專案;工具自己會 fetch;工作樹必須乾淨,
>    否則它 exit 2 擋你)。⚠️ **一定要在 Final Fresh 之前跑** —— 順序寫死為
>    「跑腳本算交集 → 合併 → 跑全套測試 → 再進 2d Final Fresh」,不是
>    「Final Fresh → Verdict → Exit 才合併」:合併之後 HEAD 變了,核准的樹
>    就不是出貨的樹。依腳本印出的 STATUS 決定:
>    · `N_A_NO_INCOMING` → 記 n-a 即過(分岔後對方零新 commit)
>    · `SYNC_REQUIRED_NO_OVERLAP` → 合併它印的 INTEGRATION_SHA + 跑全套測試,做完才可過
>    · `SYNC_REQUIRED_WITH_OVERLAP` → 上面兩件 + 共同戰場交集逐檔看過,做完才可過
>    · `ALREADY_SYNCED` → 交集證據作廢(你已經合過了,merge-base 被污染)。
>      恢復路徑二選一:①**重跑 Final Fresh** 綁當下 HEAD(下一步 2d;共同戰場必須
>      人工重看,不得用這次輸出當「沒有共同戰場」的證據)②本項 FAIL,停下來從
>      乾淨座標重算。不得只寫「證據不算數」就過。
>    勾/過的時候把腳本最後一行的結論貼進本檔(含三個 SHA 與 canonical ref)。
>    ⚠️ 合併時合的是腳本印出的 **INTEGRATION_SHA**,不是 branch 名 —— branch 名
>    會跑,中間別人再合進來,你實際併進來的內容跟剛才檢查過的就不是同一份。
>    ⚠️ 動手合併之前**無條件再跑一次腳本**(不是「隔了一段時間才跑」—— 那是
>    主觀條件,人一定會說服自己「應該還好」):兩次的 STATUS 與座標必須完全
>    相同才准動手;有任何一項不同 → 停下,照新的重算。
>    完成 = 整合同步已落在 Final Fresh 之前;HEAD 已是送審樹。
> 2d. **Final Fresh Run**:確認 Verification Evidence 節由 4-spec Verification Profile
>    指名的 entry point 一次 fresh run 產出、Source SHA = 當下 HEAD = 送審樹;跑
>    `docs/dev/tools/devflow-evidence-gauntlet.sh 7-review.md --source-sha $(git rev-parse HEAD)
>    --review-file --require-layer <Profile Required 層,逐層一個 flag>` 全綠
>    (Gauntlet 1.3.3 起自己讀 sibling 4-spec 的 Required layers;漏帶旗標不再
>    fail-open;找不到 Profile、缺 Required layers 欄、或該欄空值即 E7 紅(只有
>    「無」/none/n-a 是明示零層)。層名 strip 後全等,不得 substring。
>    `--profile` 只准本 feature 的 4-spec,不得跨份覆寫。旗標只能加嚴,不能把
>    Required 拿掉。`docs/dev/<feature>/7-review.md` 即使帶 `--source-sha` 也必須
>    等於 HEAD。)
>    ⚠️ **開工前先 `test -x docs/dev/tools/devflow-evidence-gauntlet.sh`**。
>    那個路徑是 `dev-setup` 的散發契約(skills/dev-setup/SKILL.md:69 明訂
>    `mkdir -p docs/dev/tools` 後 cp 母版),**不是隨手寫的**。
>    ⚠️ **檔案不在 = `dev-setup` 沒跑完整,不是路徑寫錯** ——
>    正確處置是**補跑 `dev-setup`**(它同時會補上 `docs/dev/devflow-contract.json`
>    等其他受管檔),**不要手動 `cp` 一支了事**:手動裝會繞過受管檔的版本握手,
>    下次 `dev-setup` 比對時看到的是一個來歷不明的複本。
>    補不了 → Required 層改**逐層手動實跑**並在本檔明記「gauntlet 未跑」是**降級**,
>    不得默默當成跑過。
>    **背景案例(佐證,不是本次要照做的事)**:2026-08 order-intake 實測,該專案
>    `docs/dev/tools/` 與 `devflow-contract.json` 兩者皆不存在,`devflow-doctor.sh`
>    實跑直接 `⛔ INCOMPATIBLE(fail-closed)`;但整條 Stage 6→7 走完沒有任何一步
>    要求跑 doctor,所以沒有人被擋。
>    (Required 層以 4-spec 為準,未 pass 由機械擋下,不靠自律)。
>    完成 = gauntlet 輸出在案(或降級聲明在案);Source SHA = 當下 HEAD。
> 2e. **Operational Walkthrough**:以各 S 的 Operational Context 為腳本親自走一遍
>    「人的工作」,逐列檢查六條 —— 技術上通過但人無法完成工作 / 看得到但沒有決策權 /
>    系統把等待誤標為完成 / 系統外動作無法追蹤 / 使用者中斷後無法恢復 / 資訊過期、
>    缺漏或多人同時操作 —— 填 Operational Walkthrough 表(無 Operational Context 的
>    純內部 S 註明不適用)。完成 = 表逐 S 填畢。
> 3. 雙軸審:Standards(F-id 🔴🟡🟢:位置|問題|建議)+ Spec(逐 R 符合/偏離);
>    4-spec 的 Design Boundary Contract 為 `applicable` 時,**併入既有兩軸**(不另立
>    Gate、不另立第三軸):Standards 加查 Dependency Direction／Boundary Leakage／
>    Data Ownership／Interface Stability;Spec 逐條對照實際 diff 是否符合該契約 ——
>    未經 spec 授權的 Boundary 變更至少 🟡,會改變 R/S、資料所有權、公開 Interface
>    或一致性語意者 🔴。**同時過下方「Design Integrity Check」固定清單**(對稱 Test
>    Integrity Check 的設計版,抓「看起來守住邊界、實際被繞過」的手法);命中項併入
>    Standards/Spec Axis 的既有 finding,不另開清單、不另立軸。
>    每 F 標影響 S/T。Agent 審時**兩軸各派一個獨立 fresh reviewer 並行**(互不看
>    對方輸出;人類 reviewer 可自兼雙軸);彙整者只並列兩軸 finding,**禁合併重排、
>    禁降級任一軸**(防一軸失敗被另一軸掩蓋)。每 F 必引 spec 原文或 diff hunk,
>    禁無出處結論。完成 = 每 R 有判定、每 F 有鏈且有出處。
> 4. 對照作者:此刻才讀 6-notes —— 自建矩陣 vs Self-Review 差異逐條裁;Deviations
>    如實?Decisions 有無實為 L2?若步 0 有武裝圍欄③,先跑
>    `devflow-exec.sh review-unlock <slug>` 解鎖才讀得到(Write 仍限縮於
>    7-review*/evidence/,unlock 不解除)。完成 = 差異全裁定入 Spec Axis。
> 5. Verdict:PASS = 本次 S 全綠+既有全綠+**現象證據逐 S 相符**+Evidence 契約全過
>    (G3 錨,八點條件正本 README §7;步 2d 的 gauntlet 全綠 + Required 層全 pass
>    即其機械面)+無 🔴(G3 正本 README §7;無 🔴 是本模板加嚴的出貨門檻,
>    不與 §7 矛盾);否則
>    REQUEST_CHANGES 列 🔴 →
>    author 走 6-notes 的 Review Follow-up(同意改+一句為何對/不同意擺論證,
>    禁 performative fix)→ 回步 1 增量重驗。**重驗迴圈上限 3 輪**;第 3 輪仍
>    REQUEST_CHANGES → **breaker**:逐 F 強制裁決(立即修/park 記入 STATUS 待辦/
>    BLOCKED 停案),裁決表寫入本檔,禁 silent discard、禁無記錄續圈。
>    ⚠️ **Verdict 之後禁止再改程式碼**。任何程式碼 commit **作廢 G3**,必須回
>    步 2c/2d 重跑整合回歸(若 HEAD 又動了)與 Final Fresh。出貨樹必須就是審過的樹。
>    完成 = verdict 落檔(含輪次數;走到 breaker 則含裁決表)。
> 6. Exit:逐勾 Exit Checklist。**本節只准文件／PR／living spec,不准再碰程式。**
>    完成 = 全勾才 shipped;僅 Stage 7 frontmatter 改為
>    `shipped`,上游 artifact 保留 `approved` 作為各自 gate 核准紀錄。

## Coverage Matrix
<!-- 產 html 時機械對照:grep 測試檔中的 S-id ↔ 4-spec 的 S 清單,缺漏自動標 ❌。
     最後一列固定為回歸列 -->
| S-id | 測試 | 狀態 |
|---|---|---|
| S-1 |  | ✅/❌ |
| 既有測試套件(回歸) | `<全套指令>` | ✅/❌ |

## Verification Evidence
<!-- Final Fresh Run 產出(契約正本:notes/design/evidence-gauntlet.md §6/§8;
     機械檢查:scripts/devflow-evidence-gauntlet.sh,E1–E13)。四欄非空;
     Status 只能 pass | fail | unverified | n-a;pass 列必有非空 Command 與含數字的
     Result(數字非形容詞);unverified/n-a 必附 Skipped reason;coverage 層 Result
     用 changed-line covered/total 分數 —— changed-line coverage = 本次變更的主要
     證據;global coverage % 只是趨勢指標,可與 changed-line 並記,
     禁只靠 global % 宣稱 coverage 充分 -->
- Source SHA:
- Final Fresh Run ID:
- Entry point:
- Toolchain:

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|

## Negative Constraint Mapping
<!-- 4-spec Verification Profile 的 Negative constraints 逐條映射 test/layer;
     skipped 必附理由且不得標 pass -->
| Constraint | Test/Layer | Status |
|---|---|---|

## 執行記錄(dev-run 引擎案;手動實作留白)
<!-- dev-run 案由 `devflow-obs stats --run <run_dir>` 衍生(禁手填),欄位:
     run_id | 模型分佈 | 升階次數 | first-pass rate | 失敗分類分佈 |
     Prompt Version 清單 | allow/D-n 清單(維持既有三欄,加 prompt/run 兩欄);
     html 以表呈現。parallel 模式加列 wave 分佈與 gate FAIL 重工次數 -->

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)
<!-- 測試綠 ≠ 看得到它動起來。每條 S 貼「照觀測方式實跑」的真實輸出:
     後端 → 實際 request/response(curl 或等效,含 status code);
     前端 → 截圖存 evidence/ 並在此引用;批次/排程 → log 或產出檔片段。
     reviewer **親自重跑**一次比對(不採信 6-notes 貼的文字),對不上即 FAIL。
     無法觀測的 S(純內部重構)→ 註明「無外部現象,以測試為準」並說明理由 -->

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1 |  |  | ✅/❌ |

⚠️ **觀測方式指向本 repo 之外(前端在另一 repo、尚未實作、需真人操作外部系統)時,
本節結構上做不到,而它又是 PASS 條件** —— 這種情況必須在 **4-spec 定稿當下**就標
`n-a` 並寫理由(見 4-spec 的觀測欄規則),不是留到 G3 才發現整節跑不了。
若 4-spec 沒標而 G3 才撞到:①逐條標 `n-a` 並記為 spec 缺口 ②**至少對本 repo 內
可執行的代表性路徑實跑**(通常是打真實 HTTP request 驗回應形狀)③verdict 不得
因為「做不到」就當成做過。

## Operational Walkthrough
<!-- reviewer 以各 S 的 Operational Context 為腳本,親自走一遍「人的工作」;
     逐列檢查:技術上通過但人無法完成工作 / 看得到但沒有決策權 / 系統把等待誤標為完成 /
     系統外動作無法追蹤 / 使用者中斷後無法恢復 / 資訊過期、缺漏或多人同時操作 -->
| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|

## Design Integrity Check(Design Boundary Contract 為 `applicable` 時逐項過;`n-a` 時記 n-a)
<!-- 對稱 skills/dev-run/SKILL.md 的 Test Integrity Check(T review 七項):那七項抓
     「測試被做成看起來驗證過,實際沒驗到」;本清單抓「實作被做成看起來守住設計邊界,
     實際被繞過」。**不是第三軸**——命中項併入既有 Standards/Spec Axis 的 finding,
     不另開清單、不另立 Gate(同執行清單步 3)。素材與語意正本:
     notes/design/design-boundary-contract.md。 -->

1. **依賴反向被間接繞過**:沒有直接違反宣告的依賴方向,但透過共用 util／event bus／
   全域狀態等中介層,讓被禁止依賴的模組間接取得對方效果——依賴圖看起來乾淨,實際反向。
2. **資料所有權被繞過寫入**:非 owner 模組不經宣告的 Interface,直接觸底層儲存
   (直連 DB、共享 struct 直改欄位、繞過 owner 提供的寫入路徑)。
3. **相容性破壞包成新增**:對外 Interface 的簽章或回應形狀實際改變,卻包裝成
   「新增可選欄位」或「附加端點」,讓 Compatibility 欄看起來仍是 additive。
4. **一致性邊界被拆解**:契約宣告同一 transaction 的多筆寫入,實作拆成兩次獨立
   commit(或反過來,把宣告獨立的操作揉進同一 transaction 掩蓋副作用)。
5. **宣告的 Test seam 未被使用**:契約指名的可觀測/可注入點,測試實際繞過去用更深
   或更淺的仿造驗證,讓「聲稱驗過邊界」與「實際驗過的東西」不是同一個東西
   (鏡像 Test Integrity Check 的「mock 掉被測物」)。
6. **Known design limit 被實作悄悄「解決」**:契約明列的已知限制被實作意外或取巧
   繞過,但契約未同步更新為已解決——限制與實作對不上,沒人發現。

任一命中 → 至少 🟡(未經 spec 授權的邊界變更);會改變 R/S、資料所有權、公開 Interface
或一致性語意者 → 🔴。每條 finding 一律引 spec 原文或 diff hunk,不得無出處。

## Standards Axis
<!-- F-id 🔴Blocker 🟡Should-fix 🟢Nice-to-have:位置 | 問題 | 建議。
     Design Boundary Contract 為 applicable 時,本軸另查四項(仍屬本軸,不另立 Gate):
     Dependency Direction(有無反向或新增未授權依賴)、Boundary Leakage(內部型別/
     資料結構是否漏出邊界)、Data Ownership(有無非 owner 直接寫入)、
     Interface Stability(公開介面變更是否符合契約宣告的相容策略) -->

## Spec Axis
<!-- 逐 R 檢查符合/偏離;對照 6 的 Deviations 是否如實記錄。
     Design Boundary Contract 為 applicable 時,逐條對照實際 diff 是否符合該契約
     (Architecture Boundaries / Interface & Consistency / Software Design / Design Constraints)。
     分級:未經 spec 授權的 Boundary 變更**至少 🟡**;若該變更改到 R/S、資料所有權、
     公開 Interface 或一致性語意 → **🔴**。Known design limit 被實作悄悄「修掉」也算偏離,
     須列 F 並回頭修契約(L2 路徑),不得默默接受 -->

## 變更架構圖
<!-- README §6:Markdown 留 ASCII 正本;純線性/單層樹用半形 | - + > < = [ ],
     空間關係複雜才在 HTML 改 SVG。 -->

## Diff(merge-base(develop)..HEAD,逐檔折疊)
<!-- README §6 要求每檔一個 details。summary 的 title/文字列 +N/-N 與函式;
     內容放 HTML-escaped 完整 diff,刪行 class="del"、增行 class="add"。 -->

## Verdict
<!-- PASS / REQUEST_CHANGES(列 🔴)。PASS ≠ shipped —— shipped 看下面的 Exit Checklist。
     建議附一張門檻表逐格給證據(本次 S 全綠 / 既有全綠 / 現象證據 / Evidence 契約 / 無 🔴)。 -->

## Known Limits
<!-- 2026-08-13 補入節序:Exit Checklist 第 1 條的 park 分支明文指定「STATUS 待辦或
     7-review known limits,擇一」,但這一節原本不在模板的節清單裡 —— 於是 park
     宣稱得出來、落點寫不進去(order-intake 實際發生,F-1 宣稱 park 但 Known Limits
     九列裡沒有它)。逐條四欄:# | 限制 | 嚴重度 | 建議處置(park 的須寫出 owner
     與追蹤位置)。已解除的用 ~~刪除線~~ 保留,不刪列 —— 讓下一輪看得到歷程。 -->
| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|

## Exit Checklist(全勾才算 shipped)
<!-- 合併之後才發現壞了 → 回滾規則見母版 README §7「合併後出事怎麼辦(整合分支回滾)」:
     預設 `git revert -m 1 <merge commit>`;禁止對整合分支 reset --hard / force push /
     rebase(改寫共享歷史);revert 過的 feature 不能直接重 merge 回來(祖先關係還在),
     兩條復原路徑見該節。 -->
- [ ] **Design Boundary finding 全數處置**(契約 `applicable` 時必勾;`n-a` 時記 n-a):
      未經授權的 Boundary 變更**不論 🔴 或 🟡 都不得帶著出貨** —— 逐條落在下列三種之一:
      ①已修正(diff 已回到契約內);②記 **L2** 回 G2 改契約後重審;
      ③**Owner 明示接受或 park**:寫下 owner、理由、追蹤位置
      (STATUS 待辦或 7-review known limits,擇一,須寫得出實際落點)。
      無記錄的 🟡 = 未處置,不得勾。理由:PASS 門檻只寫「無 🔴」,
      而未授權 Boundary 變更的預設分級是 🟡 —— 沒有這一條它就會靜默出貨
      (2026-08 fresh review F-5)
- [ ] Quiz(**不可逆改動必做**;其餘 full lane 選配,fast 免):AI 就本次變更出 3-5 題考 approver(改了什麼/為何/邊界),全對才准 merge
- [ ] (條件式)整合回歸已在 Final Fresh **之前**完成:步 2c 的結論(含三個 SHA 與
      canonical ref)貼在本檔;Source SHA 仍等於當下 HEAD。Verdict 之後若有任何
      程式碼 commit → G3 已作廢,回步 2c/2d 重跑,**不得再改程式碼**、不得在本節
      補碼或合併 INTEGRATION_SHA。
- [ ] PR → develop(feature branch,禁直上 master)
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`
- [ ] STATUS.md 已更新為 shipped(這一步在整合分支上、PR 合併後由合併那個 PR 的人
      做,不塞進本 branch 的 PR —— 動線與理由見 STATUS 模板頂註)
- [ ] 7-review frontmatter status: shipped;上游 artifact 可保留 approved(各自 gate 核准紀錄)
- [ ] 7-review.html 已產生(含變更架構圖 + diff 折疊,規格見 README §6)
- [ ] feature branch 已刪 / worktree 已清

## 附錄:本輪特有
<!-- 2026-08-13 補,2026-08-15 加 Design Integrity Check 後節數同步更新。**模板固定
     15 節之外的內容,一律收在本節之下,不得在節序中間新開 ## 節。**
     起因:order-intake 的 7-review 在模板 12 節外自行長出 7 個 ## 節、順序也被打亂
     (Negative Constraint Mapping 從第 3 位掉到第 12 位),結果
     ①owner 看不出骨架、每個 feature 形狀都不同 ②`devllow` 系機械檢查讀不到 ——
     `scripts/devflow-evidence-gauntlet.sh` 是照固定節名與固定表格欄位解析的,
     欄位一改就整組失效(該檔正規化前 24 checks 有 16 violation,正規化後 69 checks 全過)。

     所以規則是「骨架釘死、內容自由」:
     - 節名、節序、三張表的欄位(Coverage Matrix 3 欄 / Verification Evidence header 四欄
       + Layer 表 5 欄 / Negative Constraint Mapping 3 欄)不得改;
     - 本輪特有的東西(逐條分歧、Deviation 複核、額外觀測、原始輸出全文…)開 ### 放這裡;
     - 上面三張表**只放索引**(結論 + 出處指標),長證據原文放本節,表格才維持可掃可機檢。

     ⚠️ 表格儲存格內不得有原生 `|`(gauntlet 以 split("|") 切欄,E13 fail-closed);
     含 pipeline 的指令寫 `&#124;` —— markdown 渲染成 `|`,仍可複製貼上。 -->

### A1　<本輪爭點/分歧>
### A2　<…>
