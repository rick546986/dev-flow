# 五站簡化 Owner 鎖定 brief v3

> 本檔是 **F0 設計正本**,不是契約、不是模板、不是 gate 條文。
> Owner(tony / rick)已核准。後續 F1–F3 **只准跟本檔**與並列的
> `notes/design/five-station-simplify-f0-state-machine.md`,不跟對話記憶。
> **本輪(F0)零 bump**(plugin / 契約 `2.0.0` 都不動)。
> **本輪不准改** `_templates/`、README §7 錨、各站 `graph.yaml`、既有牙。
> **不准刪** G1 / G2 / `ACCEPTED`(檔案、token、機械錨全部留)。
> 下一刀 = **F1 teeth + dual-read annex**。

## 0. 為什麼摺、摺什麼、不摺什麼

七站(1-discussion → 7-review)加上例行 **G1 / Stage 3 Human verdict=`ACCEPTED` / G2**,
讓「方向、互動、契約」三次都要等人。物質(OC、R/S、Demo、Evidence)該留;
**等人的次數**不該等於站數。

摺的是**預設人類停點**,不是完整度:

| 摺 | 不摺 |
|---|---|
| 例行 G1 人類停 | G1 物質(Decision + OC 全裁決)+ G1 twin 檔 + token |
| 例行 S3-`ACCEPTED` 人類停 | 九條 trigger、Demo、attestation 規則、Agent 禁代填 |
| 例行 G2 人類停 | G2 物質(R/S、DD、Profile、Demo 條件)+ G2 twin 檔 + token |
| 七站名稱當預設路線 | 七份文檔檔名、ID 鏈、圍欄、牙、graph |
| UI twin 當每 feat 必產 | UI/flow 才必要(§3 表 B) |

**第一性**:人握的是方向與出貨,不是每一張中間卡。中間卡改由 coordinator
用謂詞自動前進;謂詞沒過就停,不准假裝過。唯一預設人類必停 = **Ship**。

## 1. Owner 鎖定表

下列十條 **F0 已鎖**。翻任何一條 = 新 brief,不是本檔修辭。

| ID | 鎖定 | 一句 |
|---|---|---|
| OC-1 | 五站 | 預設路線 = **Intake → Decide → Spec → Build → Ship**。不是六站、不是四站。 |
| OC-2 | 殺例行停點 | **例行** G1 / S3-`ACCEPTED` / G2 **不再是人類必停**。機制、檔、token、牙 **全留**。 |
| OC-3 | Ship 唯人 | 預設人類停點 **只有 Ship**(舊 G3 物質)。Coordinator **不得**代寫 Ship `verdict:`。 |
| OC-4 | 條件頁 | 頁分 **表 A(A1–A10)** 與 **表 B**。每列有生成謂詞 + 人類 latch 謂詞。沒命中不准產、不准等人。 |
| OC-5 | UI twin | **只在 UI/flow** 才必要。純後端 / 無互動風險 = 不產 UI twin、不 latch Demo。 |
| OC-6 | Must-keep | §5 清單一項都不能因摺站消失。摺的是停點,不是完整度。 |
| OC-7 | dual-read | 契約 **minor 2.1.0**(F1 annex 寫;F0 不 bump)必須同時讀舊 7 與新 5。 |
| OC-8 | F0→F3 | 切法見 §7。本輪只 F0。下一刀 F1 = teeth + dual-read annex。 |
| OC-9 | in-flight freeze | 已開工 feature **凍結走舊 7** 直到該 slug Ship。不准中途改路線。 |
| OC-10 | 禁刪禁改正本 | F0–F3 **都不刪** G1/G2/`ACCEPTED`。F0 **不改** 模板 / gates / graphs。 |

## 2. 五站產物

五站是**預設路線別名**,不是新檔名家族。舊七份文檔檔名不動
(`1-discussion.md` … `7-review.md`)。

| 新站 | 吃進的舊站 | 必產(檔名不動) | 舊 gate 怎麼處理 |
|---|---|---|---|
| **Intake** | Stage 1 | `1-discussion.md`(Real-world Context 仍必填;legacy 無此節的舊檔走既有相容) | Open Questions 全解或明標假設。無人停。 |
| **Decide** | Stage 2(+ 非 UI 的 S3 答案回寫) | `2-decision.md`(Approaches / Decision / OC / Owner Calls) | **G1 物質留下、例行人類停殺掉**。自動前進謂詞 = Decision 非空 + OC 全裁決。 |
| **Spec** | Stage 4(+ UI/flow 時的 Stage 3) | `4-spec.md`(R/S、反模糊三律、Profile、DBC 條件式);UI/flow 才有 `3-prototype.md` | **G2 物質留下、例行人類停殺掉**。Demo 條件改走表 B,不是每 feat 等人。 |
| **Build** | Stage 5 + Stage 6 | `5-tasks.md` + `6-implementation-notes.md` | 每 T:Covers / Files / Verify / Blocked-by;acceptance seam 與獨立 T review 不動。無人停。 |
| **Ship** | Stage 7 | `7-review.md` + 既有 twin / 審頁 | **G3 物質 = 唯一人類必停**。`verdict:` 仍是 md 頂欄(`PASS` / `REQUEST_CHANGES` / `HOLD`)。 |

舊 7 的對照(給 dual-read 與 in-flight):

| 舊 | 新站 | 備註 |
|---|---|---|
| 1-discussion | Intake | 檔名不變 |
| 2-decision | Decide | G1 twin 仍產(A4),例行不等人 |
| 3-prototype | Spec 條件附件 | 無 trigger → 既有 n-a / 跳過,不建頁 |
| 4-spec | Spec | G2 twin 仍產(A7),例行不等人 |
| 5-tasks | Build | 執行板,不是 gate |
| 6-implementation-notes | Build | 審碼頁 A9 |
| 7-review | Ship | A10;人類必停 |

## 3. 條件頁表 A1–A10 + B

頁不是「有站就有頁」。**生成謂詞假 → 不產頁、不算缺。**
**人類 latch 謂詞假 → coordinator 不准問人。**
Latch 一旦為真,停、把該頁給人、等人把判定寫進 **同目錄 md 頂欄**
(正本仍是 `notes/design/gate-verdict-write.md`;本檔不另發明 sidecar)。
狀態機把 latch 指回**本節**。

chrome / 產檔器 / 既有審頁契約 **F0 不改**。表只鎖定
「哪一頁、何時產、何時等人、何時可自動前進」。

### 3.1 表 A — 十張既有頁

| ID | 頁(人看的) | 產檔器(現行,不改) | 生成謂詞 | 人類 latch | 自動前進謂詞(全真才可 hop) |
|---|---|---|---|---|---|
| **A1** | Intake 審頁 | `scripts/build-stage1-html.py` | 有 `1-discussion.md` | 否 | Open Questions 全解或明標假設;Real-world Context 節在(legacy 除外) |
| **A2** | Intake 掃頁 | `scripts/build-scan-html.py` | 同 A1 | 否 | 同 A1;掃頁形狀牙既有者綠 |
| **A3** | Decide 審頁 | `scripts/build-stage2-html.py` | 有 `2-decision.md` | 否 | Decision 非空;Owner Calls / OC 全裁決;無殘留「待裁決」 |
| **A4** | Decide 方向卡(舊 G1 twin) | `scripts/build-gate-twin.py`(2-decision) | 有 `2-decision.md` | **否**(殺例行 G1) | 同 A3。twin 仍產。`verdict:` 不要求人寫才能前進 |
| **A5** | Spec 原型審頁 | `scripts/build-stage3-html.py` | 有 `3-prototype.md` **且** 九條 trigger 至少一條命中 | 否(人類走 B1,不走 A5) | 無檔或全未命中 → 既有 n-a、exit 0、不建頁 |
| **A6** | Spec 規格審頁 | `scripts/build-stage4-html.py` | 有 `4-spec.md` | 否 | `check-spec-gate.sh` 形狀綠;每個 S 有觀測;DD 無「待裁決」;Profile 的 `lane:` / `Risk:` 可解析 |
| **A7** | Spec 契約卡(舊 G2 twin) | `scripts/build-gate-twin.py`(4-spec) | 有 `4-spec.md` | **否**(殺例行 G2) | 同 A6。Demo 條件見 B1,不在 A7 等人 |
| **A8** | Build 任務板 | `scripts/build-stage5-html.py` | 有 `5-tasks.md` | 否 | 每 T 有 Covers / Files / Verify / Blocked-by;`lane: fast`+`Risk: high` 無 Owner Call 例外 → 拒 |
| **A9** | Build 實作審頁 | `scripts/build-stage6-html.py` | 有 `6-implementation-notes.md` | 否 | 每 T 獨立 review PASS;本次 S 全綠;Files ⊆ 5-tasks 聯集 |
| **A10** | Ship 出貨審頁 + G3 twin | `scripts/build-stage7-html.py` + `build-gate-twin.py`(7-review) | 有 `7-review.md` | **是(唯一預設)** | **不得**自動前進。等人寫 md 頂欄 `verdict:`。物質仍是 G3 八點 / Evidence / 雙軸 / Exit |

A4 / A7 的 twin **繼續產**,給 dual-read 與 in-flight 舊 7。
「殺例行」= 預設路線 **不等** 人按「提交判定」。不是刪 twin、不是刪 `verdict:` 欄。

### 3.2 表 B — 條件附件(命中才存在)

| ID | 物 | 命中謂詞 | 人類 latch | 沒命中 |
|---|---|---|---|---|
| **B1** | Demo + 舊 S3-`ACCEPTED` | Stage 3 九條 trigger 任一命中(新前端流程 / 改變下一步 / 角色交接 / 人工核准 / 等待退回逾時 / 權限差異 / 系統外動作 / 多種互動設計 / 操作流程不確定) | **是**。`ACCEPTED` / `REVISE` / `NOT_REVIEWED` 仍由人類親填 + attestation。Agent **禁寫禁改** attestation 行 | 不產 Demo、不 latch;A5 n-a |
| **B2** | UI twin | 本次變更是 **UI/flow**(B1 的前端/下一步/多種互動 三條任一,或 feat 自己改了人點的流程) | **是**,與 B1 同一 latch,不另開第二次人停 | 不產 UI twin。純腳本 / API / 守衛 / 文件 feat 走這裡 |
| **B3** | Variant 比較(2–4 個結構不同) | B1 且互動方案**尚未**被既有核准 Pattern 決定 | 併 B1,不另停 | 已有 Pattern → 1 個可操作 Demo 即可,不准湊假 Variant |
| **B4** | Quiz gate | 不可逆(schema / 公開 API / 權限 / 金流 / 資料遺失面) | **是**。可與 Ship 同一次人停,不准拆成第三次例行停 | 非不可逆 → 不做 Quiz |
| **B5** | Design Boundary 顯性化 | `notes/design/design-boundary-contract.md` §1 觸發任一 | 否。物質寫進 4-spec 該節;人在 Ship 一併看 | 合法 `n-a` + 具體理由 |

**page-human latch 唯一出口**(狀態機引用本句):

1. 表 A 的 latch 欄 = 是,或表 B 的 latch 欄 = 是。
2. Coordinator **停**、把該頁 URL / 路徑給人、**不准**代填判定。
3. 人把判定寫進同目錄 md 頂欄(Demo 走 3-prototype Human verdict + attestation;Ship / Quiz 走 `verdict:`)。
4. 寫入後才准離站。`REVISE` / `REQUEST_CHANGES` / `NOT_REVIEWED` → 不得前進。
5. 沒命中 latch 卻問人 = 違 brief,F1 牙要紅。

## 4. Runtime

F0 **不寫** coordinator 碼。本節鎖行為,落地從 F2 起。
狀態機細則(謂詞偽碼、cap、latch 指標)住
`notes/design/five-station-simplify-f0-state-machine.md`。

| 規則 | 鎖定 |
|---|---|
| 誰前進 | **Coordinator** 讀 §3 謂詞,真則 hop 下一站,假則停。不准問「要不要繼續」。 |
| 誰准寫判定 | 人。Agent / coordinator **不得**寫 Ship `verdict:`、不得寫 `ACCEPTED`、不得寫 attestation。 |
| 中間站 | Intake / Decide / Spec / Build 例行 **無人停**。沒過謂詞 = 停在該站修,不是改問人。 |
| Latch | 只准 §3 表 A/B 的 latch 列開火。開火後行為見 §3 末「唯一出口」。 |
| Rewrite cap | **hop ≤ 2**(同一 hop 重寫次數);**Decide ≤ 1**(Decide 整站重開);**Goal reopen ≤ 1**(Intake 目標 / Success Criteria 重開)。用盡 → fail-closed,升給人,不准暗改 cap。 |
| 舊 7 執行面 | in-flight 與 dual-read 仍跑既有 graph / 模板 / 牙。Coordinator 不得把舊 7 slug 強折成五站。 |
| 觀測 | 前進 / latch / cap 觸發都要留機械紀錄(F2 才接 event schema;F0 只鎖「要留」)。 |

## 5. Must-keep 完整度

摺站之後下列 **仍必須成立**。F1 牙對這張表,不准用「已經五站了」當省略理由。

| # | 必須留下 | 現行正本(不重抄) |
|---|---|---|
| M1 | ID 鏈 R→S→T→test→D→F;測試名含 S-id | README / 4-spec / 5-tasks |
| M2 | 資訊圍欄:討論盲下游;實作者只准讀 4-spec+5-tasks+6-notes+CONTEXT+living spec;reviewer 先自建 coverage | plugin `dev-flow` SKILL §3 |
| M3 | 反模糊三律(S 可轉單一測試、禁模糊詞、禁 TBD) | `_templates/4-spec.md` |
| M4 | Real-world Context →(條件)Demo → S 級 Operational Context | `notes/design/real-world-interaction.md` |
| M5 | Human 主權:Agent 禁代填 `ACCEPTED` / Ship `PASS`;無 attestation 的 `ACCEPTED` 機械拒 | `_stage3_impl.py` + `gate-verdict-write.md` |
| M6 | G3 Evidence 契約八點物質(現象、回歸、出貨樹=審過的樹…) | README §7 G3 錨 |
| M7 | Verification Profile + lane 規則(`fast`+`high` 拒) | `_templates/4-spec.md` + README §7 G2 |
| M8 | Design Boundary Contract 條件式(不是新站、不新 ID) | `notes/design/design-boundary-contract.md` |
| M9 | Scope guard:改動檔 ⊆ 5-tasks Files 聯集 | README §5 |
| M10 | 驗證五律(證據=原始輸出、派工者不下場修、反預判、HITL 不代答、失敗先分類) | README §5 |
| M11 | 逐 T acceptance seam:RED→GREEN→scope→Verify→獨立 T review→PASS→commit | `_templates/6-implementation-notes.md` |
| M12 | author ≠ approver(Ship 與任何 latch) | README §7 |
| M13 | html 重生;Pages 掛真 html 不是倉庫原始碼 | `notes/design/pages-hosting.md` |
| M14 | 不可逆才 Quiz;其餘 full 選配、fast 免 | README §7 |
| M15 | G1 / G2 / `ACCEPTED` **token 與檔案都在**,供 dual-read 與舊 7 | 本檔 OC-2、OC-10 |
| M16 | 既有牙、各站 `graph.yaml`、gate-consistency 錨 **F0 一字不改** | 本檔 OC-10 |

少一條 = 本 brief 被違反,不是「簡化成功」。

## 6. 遷移

| 規則 | 鎖定 |
|---|---|
| 契約 | **dual-read minor = 2.1.0**。`2.0.0` 繼續讀舊 7;`2.1.0` 加五站別名 / 自動前進欄,不得讓舊 slug 一次變紅。F0 **不 bump**。條文進 F1 annex。 |
| in-flight freeze | `docs/dev/<slug>/` 在 F3 cut 當下**已有任一站檔** → 該 slug **整段走舊 7**(含例行 G1 / 條件 S3 / G2 / G3)直到 Ship。不准中途切五站。 |
| 新 slug | F3 cut 之後才預設五站。F0–F2 期間新開的母版改版軌仍走舊 7,避免雙路線並行污染觀測。 |
| 舊 7 機械 | 模板、graph、G1/G2/`ACCEPTED` 牙、`_stage3_impl.py` **不刪**。Cut 之後它們服務 in-flight + dual-read。 |
| 採用專案 | `dev-setup` upgrade 到 2.1.0 之後才看五站。未 upgrade = 舊 7。不得遠端改別人 repo 的路線。 |
| STATUS / HISTORY | 母版看板加 Backlog 列指本檔。F0 不寫 HISTORY(還沒落地)。 |

## 7. F0–F3 切法

四刀,不准併刀、不准 F0 偷做 F1 牙。

| 刀 | 做 | 不做 |
|---|---|---|
| **F0**(本輪) | 本 brief + 狀態機落 `notes/design/`;STATUS Backlog 指向這兩檔;下一刀寫明 F1 | 改模板 / gates / graphs;刪 G1/G2/`ACCEPTED`;加牙;bump;動 in-flight slug |
| **F1** | **teeth**:機械釘 §1–§5 與狀態機 cap / latch。**dual-read annex**:2.1.0 怎麼同時讀 7 與 5(欄位、缺省、舊檔不紅) | 改預設路線;寫 coordinator;刪舊 gate;bump plugin(契約 2.1.0 是否本刀落地由 annex 定,F0 不先 bump) |
| **F2** | Coordinator / runtime 接自動前進;event 留前進 / latch / cap;仍不刪舊 token | 把 in-flight 折成五站;拿掉 G1/G2/`ACCEPTED` 檔 |
| **F3** | **Cut**:新 slug 預設五站;舊 7 只服務 freeze + dual-read;guide / STATUS 用語切五站 | 刪 G1/G2/`ACCEPTED`;改已經 freeze 的 slug;一次大爆炸改模板全文(模板改寫若要做,另開刀,不叫 F3 偷做) |

F3 之後 G1/G2/`ACCEPTED` **仍在 repo**。刪它們 = 新 brief,不是本切法的尾巴。

## 8. 審查 verdict

| 場合 | 合法值 | 誰寫 | 沒寫 |
|---|---|---|---|
| **Ship**(A10 / 舊 G3) | `PASS` / `REQUEST_CHANGES` / `HOLD` | **人**。md 頂欄 `verdict:`。勾選 ≠ 判定 | 停在 Ship。Coordinator 不得前進、不得代填 `PASS` |
| **B1 Demo**(舊 S3) | `ACCEPTED` / `REVISE` / `NOT_REVIEWED` | **人** + `Verdict attestation: human:<名> @ <日>`。Agent 禁寫該行 | `NOT_REVIEWED` ≠ `ACCEPTED`;不得進 Spec 把互動定案 |
| **B4 Quiz** | 全對才准與 Ship 一起過 | **人**(approver) | 不可逆不得 merge |
| **A1–A9 例行** | 不要求人類 verdict | Coordinator 只看 §3 自動前進謂詞 | 謂詞假 = 停修,不是改問人 |
| **A4 / A7 dual-read** | 舊欄位可空、可留 in-flight 的人寫值 | 預設五站不等人填 | 舊 7 in-flight 仍依 README §7 等人 |
| **REQUEST_CHANGES / REVISE** | 既有修迴圈 | 人 | 不得用「自動前進」跳過 |
| **owner 自審** | 仍是有記錄的最後手段 | 人,記 reviewers | 不准假裝四眼 |

**Fresh-context reviewer Agent** 仍可對中間產物做書面審(找洞),
但 **不構成** G1/G2 人類停點,也 **不得** 把 Agent 結論寫成 `verdict: PASS` / `ACCEPTED`。
Ship 的四眼順序不變:適格人類 → fresh Agent → owner 自審(最後手段)。

---

**F0 收尾**:本檔 + 狀態機 = 鎖定面。沒有牙、沒有路線切換、沒有刪除。
誰在 F0 改 `_templates/` 或 `graph.yaml` 或刪 G1,就是違 brief。
