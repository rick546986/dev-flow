---
feature: <slug>
stage: 7-review
status: draft
owner:               # reviewer,不可 = 實作 owner
updated:
---

# 7. 驗證

> 用途:**G3 出貨關卡**。雙軸審(mattpocock):Standards = 通用品質、Spec = 逐條對
> 4-spec。本次 S 全綠 + **既有測試全綠(回歸)** + 無 🔴 才 PASS。過 gate 後產
> 7-review.html 供報告。
> 本階段固定產出:`7-review.md`(本模板全節)+ `7-review.html`(G3 必產;必含
> 變更架構圖、F-id 分級表、現象證據表、全 branch diff 折疊 + 執行記錄表)。
>
> 執行清單(開場第一動建成 todo;逐步達成「完成 =」才勾;禁跳項、禁併項):
> 0. 角色+防錨定起手:審查者依序:適格人類 reviewer → fresh-context reviewer Agent →
>    owner 自審(有記錄的最後手段);前兩者皆須 ≠ 實作 owner。先讀
>    4-spec/5-tasks/diff/測試碼,**此刻禁讀 6-notes 的 Self-Review**。
>    完成 = 讀取順序聲明在案。
> 1. 自建 Coverage Matrix:grep 測試檔 S-id ↔ 4-spec S 清單,逐列填(缺漏 ❌),
>    末列固定回歸列。完成 = 矩陣全列填畢(未參考作者主張)。
> 2. 親跑驗證:本次 S 測試+既有全套,結果入矩陣。完成 = 兩輸出在案。
> 2b. **現象複驗**:照 4-spec 每 S 的「觀測方式」**親自實跑一次**(後端打真實請求、
>    前端截圖存 `evidence/`、批次看 log/產出檔),填「現象證據」表。不採信 6-notes
>    貼的文字。完成 = 每 S 有實跑證據且與觀測方式相符(無外部現象者註明理由)。
> 2c. **Final Fresh Run**:確認 Verification Evidence 節由 4-spec Verification Profile
>    指名的 entry point 一次 fresh run 產出、Source SHA = 當下 HEAD;跑
>    `scripts/devflow-evidence-gauntlet.sh 7-review.md --source-sha $(git rev-parse HEAD)
>    --review-file` 全綠。完成 = gauntlet 輸出在案。
> 2d. **Operational Walkthrough**:以各 S 的 Operational Context 為腳本親自走一遍
>    「人的工作」,逐列檢查六條 —— 技術上通過但人無法完成工作 / 看得到但沒有決策權 /
>    系統把等待誤標為完成 / 系統外動作無法追蹤 / 使用者中斷後無法恢復 / 資訊過期、
>    缺漏或多人同時操作 —— 填 Operational Walkthrough 表(無 Operational Context 的
>    純內部 S 註明不適用)。完成 = 表逐 S 填畢。
> 3. 雙軸審:Standards(F-id 🔴🟡🟢:位置|問題|建議)+ Spec(逐 R 符合/偏離);
>    每 F 標影響 S/T。Agent 審時**兩軸各派一個獨立 fresh reviewer 並行**(互不看
>    對方輸出;人類 reviewer 可自兼雙軸);彙整者只並列兩軸 finding,**禁合併重排、
>    禁降級任一軸**(防一軸失敗被另一軸掩蓋)。每 F 必引 spec 原文或 diff hunk,
>    禁無出處結論。完成 = 每 R 有判定、每 F 有鏈且有出處。
> 4. 對照作者:此刻才讀 6-notes —— 自建矩陣 vs Self-Review 差異逐條裁;Deviations
>    如實?Decisions 有無實為 L2?完成 = 差異全裁定入 Spec Axis。
> 5. Verdict:PASS = 本次 S 全綠+既有全綠+**現象證據逐 S 相符**+無 🔴
>    (G3 正本 README §7;無 🔴 是本模板加嚴的出貨門檻,不與 §7 矛盾);否則
>    REQUEST_CHANGES 列 🔴 →
>    author 走 6-notes 的 Review Follow-up(同意改+一句為何對/不同意擺論證,
>    禁 performative fix)→ 回步 1 增量重驗。**重驗迴圈上限 3 輪**;第 3 輪仍
>    REQUEST_CHANGES → **breaker**:逐 F 強制裁決(立即修/park 記入 STATUS 待辦/
>    BLOCKED 停案),裁決表寫入本檔,禁 silent discard、禁無記錄續圈。
>    完成 = verdict 落檔(含輪次數;走到 breaker 則含裁決表)。
> 6. Exit:逐勾 Exit Checklist。完成 = 全勾才 shipped;僅 Stage 7 frontmatter 改為
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
     機械檢查:scripts/devflow-evidence-gauntlet.sh,E1–E12)。四欄非空;
     Status 只能 pass | fail | unverified | n-a;pass 列必有非空 Command 與含數字的
     Result(數字非形容詞);unverified/n-a 必附 Skipped reason;coverage 層 Result
     用 covered/total 分數,禁全域 % 虛榮數字 -->
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

## Operational Walkthrough
<!-- reviewer 以各 S 的 Operational Context 為腳本,親自走一遍「人的工作」;
     逐列檢查:技術上通過但人無法完成工作 / 看得到但沒有決策權 / 系統把等待誤標為完成 /
     系統外動作無法追蹤 / 使用者中斷後無法恢復 / 資訊過期、缺漏或多人同時操作 -->
| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|

## Standards Axis
<!-- F-id 🔴Blocker 🟡Should-fix 🟢Nice-to-have:位置 | 問題 | 建議 -->

## Spec Axis
<!-- 逐 R 檢查符合/偏離;對照 6 的 Deviations 是否如實記錄 -->

## 變更架構圖
<!-- README §6:Markdown 留 ASCII 正本;純線性/單層樹用半形 | - + > < = [ ],
     空間關係複雜才在 HTML 改 SVG。 -->

## Diff(merge-base(develop)..HEAD,逐檔折疊)
<!-- README §6 要求每檔一個 details。summary 的 title/文字列 +N/-N 與函式;
     內容放 HTML-escaped 完整 diff,刪行 class="del"、增行 class="add"。 -->

## Verdict
<!-- PASS / REQUEST_CHANGES(列 🔴) -->

## Exit Checklist(全勾才算 shipped)
- [ ] Quiz(**不可逆改動必做**;其餘 full lane 選配,fast 免):AI 就本次變更出 3-5 題考 approver(改了什麼/為何/邊界),全對才准 merge
- [ ] PR → develop(feature branch,禁直上 master)
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`
- [ ] STATUS.md 已更新為 shipped
- [ ] 7-review frontmatter status: shipped;上游 artifact 可保留 approved(各自 gate 核准紀錄)
- [ ] 7-review.html 已產生(含變更架構圖 + diff 折疊,規格見 README §6)
- [ ] feature branch 已刪 / worktree 已清
