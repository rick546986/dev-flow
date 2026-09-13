---
feature: requirement-discovery-gaps
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-13
---

# 4. 規格 — 九條需求發現缺口（change spec）

> 基準:main tip `be808fb`（#270 Stage 3 B + #273 STATUS）。契約不 bump。本 hop **只寫本目錄 `4-spec.md`／`4-spec.html`**。不改 `_templates/`／`skills/`／守衛／範例／STATUS／HISTORY。**不發明 G2／G3**。`verdict` 空到人類寫入。
> Decision 正本:`docs/dev/requirement-discovery-gaps/2-decision.md`（1A–8A；OC-1～OC-6 ✅；G1 `verdict` PASS、`status` approved）。Stage 3 選定 Variant A（同檔就地欄；節名／前綴已回寫 2-decision 內部技術選擇）。
> 派工 brief（2026-09-13 Implementer C）:G1 + Stage 3 ACCEPTED 之後只做 Stage 4。本 tree 的 `3-prototype.md` 在 `be808fb` 仍是 `status: draft`、Human verdict `NOT_REVIEWED`、無 attestation。本 hop **不改** 3-prototype、**不代填** attestation。G2 仍須人類審；本檔不把 frontmatter 標成 approved。
> Lane = full。九條一包。機械牙只延伸既有 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`（OC-1）。不另造檢查家族、不發明 RW-id、不另造 lookback 永久檔。

## 補助模組生命週期（預覽）

主詞是「九缺口活教師 + 既有牙射程」,不是整份方法論。直式圖,置中。
- 新生（這輪沒有）：不加 `check-discovery-gaps.sh`、不加 RW-id、不加每 feature `lookback.md`。
- 改行為（相關一格）：延 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh` 射程；改 Stage 1–4／7 模板、`skills/dev-talk` 發現題路徑、完整範例教師。
- 退役：沒有。
- 不動：七關結構、Fast 合法跳過 Stage 1–3、A-5 LIGHT（不做 Actor Coverage 全表）、STATUS／HISTORY 寫入口、plugin 版號、本 hop 的 G2／G3。

## ADDED Requirements

### R-1: 系統 SHALL 把工作結果與解法構想分欄
G-out-1／SC-1／AC-1／1A。結果節名字面 `## Goals`；構想節名字面 `## Requested solution`。Goals 指令不再要求候選畫面／API／元件通道。構想不寫進 Goals。不同時新增 dashboard／API 黑名單（A-1 已拒）。

**審的時候看什麼**
看分欄字面與對照稿落點,不是看有沒有禁「dashboard」這個詞。好卡兩節分開；把「我要 dashboard」寫進 Goals 的對照稿必須被形狀檢查或 G1 抽查指出「構想在錯欄」。

#### S-1.1 模板 Goals 不再把通道列成從哪看候選
- GIVEN: `_templates/1-discussion.md` 落地後的 `## Goals` 指令與「驗收雛形」觀測三件
- WHEN: 搜字面 `## Goals`、`## Requested solution`、以及「從哪看」候選列
- THEN: `## Requested solution` 節存在；Goals 與雛形「從哪看」不再把「畫面路徑 | API 端點」寫成必填候選；通道只能出現在 Requested solution 或 Stage 2／4 選定解法之後
- 觀測:從兩節標題與「從哪看」那一行看 | 兩節名都在,且「從哪看」行不再列出畫面路徑與 API 端點 | 落地前 n-a:模板正本未改;替代=`rg -n "Requested solution|畫面路徑|API 端點" _templates/1-discussion.md`,現況 L96 仍列通道、無 Requested solution 節;Stage 6 改模板後重跑同一搜尋
- Operational Context:
  - Actor:討論 agent／G1 reviewer
  - Goal:結果在 Goals,構想不混成目標
  - Situation:使用者帶著「我要 dashboard」來討論
  - Known information:1A 節名字面；A-1 拒黑名單
  - Missing information:這句 Goal 是否偷帶解法（人判）
  - Human decision:G1 抽一句 Goal,看構想是否在錯欄
  - Authority:形狀牙擋缺欄；語意留給 G1
  - External dependency:無
  - Out-of-system action:把構想搬到 Requested solution
  - Waiting/timeout behavior:無
  - Recovery:構想在 Goals → 搬欄,不改 Goals 指令去鎖畫面
  - Audit/handoff requirement:兩節名留在 1-discussion 本文
  - Observation:見本條觀測

#### S-1.2 「我要 dashboard」寫進 Goals 的對照稿必須現形
- GIVEN:一份 1-discussion 對照稿,`## Goals` 第一條字面為「我要 dashboard」,`## Requested solution` 為空或缺失
- WHEN:跑本包掛進 `check-realworld.sh` 家族的指定形狀檢查（同一入口,不另開腳本）
- THEN:exit ≠ 0；輸出指出構想在 Goals 或缺 `## Requested solution`
- 觀測:從該檢查 exit 與 stdout／stderr 看 | exit ≠ 0 且含 Goals 或 Requested solution 字樣 | 落地前 n-a:牙射程未延伸;替代=本條 GIVEN 對照稿字面；Stage 6 把稿放進 `scripts/fixtures/discovery-gaps/goals-channel-in-wrong-column/`
- Operational Context:不適用 — 與 S-1.1 同一交接；本條只換對照稿。

#### S-1.3 完整範例 Goals 不再把登入／點擊／一眼可見當成目標本身
- GIVEN:落地後的 `example/contract-expiry-reminder/1-discussion.md`
- WHEN:讀 `## Goals` 與 Interview Log 結「最低成本呈現面」的那條
- THEN:Goals 三條不再指定登入後、點擊直達、一眼可見為目標本身；dashboard／卡片／URL 若仍出現,只在 `## Requested solution` 且標未定案；Interview Log 不得把「dashboard 是最低成本的呈現面」寫成 Goal 結論
- 觀測:從範例 Goals 與 Interview Log 看 | Goals 無「登入後」「點擊」「一眼可見」當目標謂語 | 落地前 n-a:範例未改口;替代=現況 L62–L65、L83–L103、L119；Stage 6 同期改範例後重讀
- Operational Context:
  - Actor:採用專案討論者
  - Goal:抄範例時抄到結果欄,不是抄到通道
  - Situation:完整範例是活教師
  - Known information:Q14 同 slug 改範例；OC-3 本 repo 範例 = Observed 教師
  - Missing information:採用現場是否照抄（Assumption,OC-3）
  - Human decision:無；教師改口是本包義務
  - Authority:check-realworld 地板驗範例分欄
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:範例仍鎖 dashboard → 本包未完成,不得宣稱 SC-1 綠
  - Audit/handoff requirement:範例與模板同 hop 改口
  - Observation:見本條觀測

### R-2: 系統 SHALL 讓發現題不附推薦答案
G-out-2／SC-2／AC-2／1A。發現題前綴字面 `發現｜`（禁附推薦）。裁決題前綴字面 `裁決｜`（可附選項／差異／推薦）。完成條件改覆蓋面（必查面已覆蓋、關鍵反例已問、證據缺口已顯性化）；「連續兩輪無新問題」只當輔助訊號。不要求從最終 1-discussion 還原整場對話。

**審的時候看什麼**
看問句本身有沒有 `發現｜` 卻先給答案。刪掉其中一邊對稱句,靜態牙必須紅。

#### S-2.1 發現題路徑不再把附推薦當硬規則
- GIVEN:落地後的 `skills/dev-talk` 發現題路徑（至少 `nodes/N3-probe.md`）
- WHEN:搜「附推薦答案」與前綴 `發現｜`／`裁決｜`
- THEN:發現題指令含 `發現｜` 且含「禁附推薦」或同等「不得附推薦答案」；裁決題指令含 `裁決｜` 且允許附選項／差異／推薦；N3 三律不再把「附推薦答案」套在發現題
- 觀測:從 N3 與對稱句看 | 發現題禁推薦、裁決題可附,兩前綴都在 | 落地前 n-a:skill 未改;替代=`rg -n "附推薦答案|發現｜|裁決｜" skills/dev-talk/nodes/N3-probe.md`,現況 L22 仍要附推薦、無前綴；Stage 6 改節點後重跑
- Operational Context:
  - Actor:訪談對象／討論 agent
  - Goal:被問「上次真的怎麼做」時題目本身不塞答案
  - Situation:N3 逐題逼問
  - Known information:發現題 vs 裁決題詞條（1-discussion Constraints）
  - Missing information:現場是否仍這樣問（Assumption,OC-3）
  - Human decision:無；問句形狀是 skill 硬規則
  - Authority:靜態牙守對稱句；誘導無法從最終 md 還原
  - External dependency:口頭訪談（系統外）
  - Out-of-system action:受訪者回答現況
  - Waiting/timeout behavior:等受訪者答完才覆述
  - Recovery:發現題已附推薦 → 重寫問句,不把推薦提前
  - Audit/handoff requirement:Interview Log 高影響發現題由 Stage 1 自檢抽查
  - Observation:見本條觀測

#### S-2.2 刪掉一邊對稱句必須讓靜態牙紅
- GIVEN:一份隔離複本,只刪 `發現｜` 指令或只刪 `裁決｜` 指令,其餘不變
- WHEN:跑本包掛進既有家族的靜態牙（`check-realworld.sh` 或同等已掛入口,不另開腳本）
- THEN:exit ≠ 0；輸出指出缺失的那一邊前綴
- 觀測:從該檢查 exit 與輸出看 | exit ≠ 0 且點名缺失前綴 | 落地前 n-a:牙未延伸;替代=本條 GIVEN；Stage 6 放 `scripts/fixtures/discovery-gaps/prefix-one-side-deleted/`
- Operational Context:不適用 — 與 S-2.1 同一交接；本條只驗刪一邊。

#### S-2.3 發現題無前綴卻先給答案的對照問句必須現形
- GIVEN:對照問句字面「上次真的怎麼做？建議用 dashboard,你覺得呢？」且無 `發現｜`
- WHEN:人只看問句本身（Stage 3 AC-2 好卡／壞卡）或跑指定形狀檢查
- THEN:該問句不得當已完成的發現題；好卡字面為 `發現｜上次真的怎麼做？` 且問句內無推薦通道
- 觀測:從問句字面看 | 壞卡無 `發現｜` 且含 dashboard 建議；好卡有前綴且無建議 | 用紙上對照或 Stage 6 fixture `discovery-gaps/discover-question-with-recommend/`
- Operational Context:不適用 — 與 S-2.1 同一交接；本條只換問句。

### R-3: 系統 SHALL 要求高影響主張回到來源或 Assumption+期限
G-out-3／SC-3／AC-3／2A／OC-5。高影響列就地標狀態枚舉 ∈ {Observed, Reported, Inferred, Assumption, Conflict}。Evidence 最小欄:來源類型、as-of、角色或範圍、支持哪一段、限制。來源 XOR Assumption+期限。點頭紀錄不得當唯一來源。不要求 Stage 1 每一句 Context 都貼狀態。

**高影響抽樣規則（本檔釘死；OC-5）**
一條主張算高影響,若它為假會改動以下至少一項:Goals／Requested solution 分欄、lane、權限或核准語意、等待／完成語意、G2 能否送審、Journey／workaround／exception 去向、lookback 門檻或回看 owner。G1 抽一條高影響主張沿引用回來源；對不上退回 Stage 1。牙只驗形狀（欄在、枚舉 ∈ 集合、來源 XOR Assumption+期限）。

**審的時候看什麼**
沿一條高影響主張走回來源,或看到 Assumption+期限。只有「使用者反映」四字 = 形狀失敗。點頭不得補欄。

#### S-3.1 高影響列缺來源且缺期限必須紅
- GIVEN:一份 1-discussion 對照稿,高影響列主張為 Journey「發現被錨定」,狀態欄空、來源類型空、亦無 Assumption+期限
- WHEN:跑本包掛進 `check-realworld.sh` 家族的指定檢查
- THEN:exit ≠ 0；輸出指出缺來源或缺期限
- 觀測:從 exit 與輸出看 | exit ≠ 0 且含來源或期限或 Assumption 字樣 | 落地前 n-a:牙只驗「有 Evidence 字」;替代=現況 `scripts/check-realworld.sh` L88–L91；Stage 6 放 `scripts/fixtures/discovery-gaps/claim-no-source-no-deadline/`
- Operational Context:
  - Actor:G2 reviewer／G1 reviewer
  - Goal:主張能重開來源,或標期限
  - Situation:高影響列就地填 2A 欄
  - Known information:枚舉五值；OC-5 只要求高影響列
  - Missing information:這列算不算高影響（人判,規則見上）
  - Human decision:退回 Stage 1 補來源或期限
  - Authority:牙擋形狀；語意留給 G1 抽查
  - External dependency:來源檔或訪談
  - Out-of-system action:重開來源
  - Waiting/timeout behavior:缺欄就停,不得用點頭補
  - Recovery:補來源 XOR 補 Assumption 四欄+期限
  - Audit/handoff requirement:欄留在主張旁邊（Variant A）
  - Observation:見本條觀測

#### S-3.2 有來源或有期限的對照稿必須綠
- GIVEN:同一形狀檢查；對照稿 A:狀態=Observed、來源類型=本 tree skill、as-of=2026-09-13、角色或範圍=討論 agent、支持哪一段=1-discussion Context N3、限制=無採用現場逐字稿；對照稿 B:狀態=Assumption、來源類型為「—」、期限=Stage 2、四欄齊
- WHEN:各跑一次指定檢查
- THEN:兩份都 exit 0
- 觀測:從兩次 exit 看 | 皆 0 | 落地前 n-a:牙未延伸;替代=Stage 3 Method 2A 好卡字面；Stage 6 放 `scripts/fixtures/discovery-gaps/claim-observed/` 與 `claim-assumption-with-deadline/`
- Operational Context:不適用 — 與 S-3.1 同一交接；本條只換綠卡。

#### S-3.3 點頭紀錄不得當唯一來源
- GIVEN:對照稿高影響列來源類型字面為「使用者點頭」或「S1-survey 認可」,無其他來源、亦無 Assumption+期限
- WHEN:跑 S-3.1 同一支指定檢查
- THEN:exit ≠ 0；輸出指出點頭不是來源
- 觀測:從 exit 與輸出看 | exit ≠ 0 且含點頭或認可或來源字樣 | 落地前 n-a:牙未延伸;替代=本條 GIVEN；Stage 6 放 `scripts/fixtures/discovery-gaps/nod-as-only-source/`
- Operational Context:不適用 — 與 S-3.1 同一交接；本條只換來源類型。

#### S-3.4 狀態枚舉必須落在五值集合
- GIVEN:對照稿狀態欄字面為 `Unknown` 或 `Fact`
- WHEN:跑 S-3.1 同一支指定檢查
- THEN:exit ≠ 0；輸出指出枚舉不在 {Observed, Reported, Inferred, Assumption, Conflict}
- 觀測:從 exit 與輸出看 | exit ≠ 0 且列出合法枚舉或點名非法值 | 落地前 n-a:牙未延伸;替代=本條 GIVEN；Stage 6 放 `scripts/fixtures/discovery-gaps/claim-bad-enum/`
- Operational Context:不適用 — 牙只驗 ∈ 集合；亂填但仍 ∈ 集合要靠 G1。

### R-4: 系統 SHALL 拒絕過期未驗的高影響 Assumption 送 G2
G-out-4／SC-4／AC-4／3A。擋點長在既有 `check-spec-gate.sh`（已是 G2 形狀 Gate）。模板／範例地板仍由 `check-realworld.sh` 驗四欄在不在。

**Assumption 四欄機器可讀形（本檔釘死）**
高影響 Assumption 必須能被表或清單解析出這五個鍵（欄名字面可在同一行或表頭）:
`假設`（Stage 1 原文片段）、`若為假影響什麼`、`影響級`（高｜中｜低；牙只擋「高」）、`怎麼驗`、`何時／由誰驗`。
`何時／由誰驗` 必須含 `期限=` 後接下列之一:ISO 日 `YYYY-MM-DD`、或 token `Stage 1`／`Stage 2`／`G1`／`G2`／`G3`；以及 `誰=` 後接角色。
另可有 `resolved=` 值 ∈ {空, Observed, Reported, `OC-accept:<id>`}。
4-spec 用**原文片段**引用該 `假設`（不發 RW-id）。

**過期判準**
ISO 日 < 跑 `check-spec-gate.sh` 的日曆日 → 過期。token `Stage 2` 或 `G1` 且同 slug 的 `2-decision.md` frontmatter `status: approved` → 過期。token `G2` 且同 slug 的 `4-spec.md` `verdict: PASS` → 過期（本 hop 不寫 PASS,本條是落地後契約）。

**審的時候看什麼**
拒絕發生在 G2 送審那一關（`check-spec-gate.sh` exit 1）,不是「模板有欄就綠」。

#### S-4.1 過期 + 未 resolved + 無 OC 必須讓 spec-gate exit 1
- GIVEN:一份 4-spec 引用高影響 `假設` 原文片段「採用現場仍把解法寫進 Goal」；來源列 `影響級`=高、`期限=Stage 2`、`resolved` 空、無 `OC-accept:`；同 slug `2-decision.md` 為 `status: approved`
- WHEN:跑 `bash scripts/check-spec-gate.sh <該 4-spec.md>`
- THEN:exit 1；輸出指出過期 Assumption 或同等「未驗假設」字樣
- 觀測:從 spec-gate exit 與輸出看 | exit 1 且含 Assumption 或過期或期限字樣 | 落地前 n-a:現況 spec-gate 無此項;替代=`bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md` 今日只做 C1–C6；Stage 6 放 `scripts/fixtures/discovery-gaps/expired-assumption-blocks-g2/`
- Operational Context:
  - Actor:G2 reviewer
  - Goal:過期高影響假設進不了 G2
  - Situation:送審前跑 spec-gate
  - Known information:四欄形；OC-3 已收窄本 slug 的 Q6
  - Missing information:無（期限與 resolved 都在列上）
  - Human decision:驗轉 Observed／Reported,或寫 OC-accept
  - Authority:spec-gate 機械拒；人補 resolved 或 OC
  - External dependency:同 slug 2-decision status
  - Out-of-system action:在終端機跑 spec-gate
  - Waiting/timeout behavior:exit 1 即停送審,直到列被驗或 OC 接受
  - Recovery:改 `resolved=Observed` 或 `OC-accept:<id>` 後重跑
  - Audit/handoff requirement:拒絕留在 spec-gate 輸出,不是口頭提醒
  - Observation:見本條觀測

#### S-4.2 已驗轉 Observed／Reported 的對照稿必須 exit 0
- GIVEN:與 S-4.1 同一引用,但 `resolved=Observed` 或 `resolved=Reported`,其餘相同
- WHEN:跑同一支 `check-spec-gate.sh`
- THEN:本項（過期假設）不造成 exit 1；若無其他 C1–C6 失敗則 exit 0
- 觀測:從 exit 看 | 不得只因該列過期而紅 | 落地前 n-a:牙未延伸;替代=本條 GIVEN；Stage 6 放 `scripts/fixtures/discovery-gaps/assumption-resolved-observed/`
- Operational Context:不適用 — 與 S-4.1 同一交接；本條只換 resolved。

#### S-4.3 有 OC-accept 的對照稿必須 exit 0
- GIVEN:與 S-4.1 同一引用,`resolved=OC-accept:OC-3`,其餘相同
- WHEN:跑同一支 `check-spec-gate.sh`
- THEN:本項不造成 exit 1；若無其他 C1–C6 失敗則 exit 0
- 觀測:從 exit 看 | 不得只因該列過期而紅 | 落地前 n-a:牙未延伸;替代=本 slug OC-3 已收窄 Q6；Stage 6 放 `scripts/fixtures/discovery-gaps/assumption-oc-accept/`
- Operational Context:不適用 — 與 S-4.1 同一交接；本條只換 OC-accept。

### R-5: 系統 SHALL 要求 Human verdict 一行寫出角色與場景
G-out-5／SC-5／AC-5／8A LIGHT。一行內有角色與場景。只寫 ACCEPTED + 姓名日期不得當完整 verdict。不做 Actor Coverage 全表。

**verdict 一行字面（本檔釘死）**
`- Human verdict: <ACCEPTED|REVISE|NOT_REVIEWED> | role=<Actors 表角色> | scenario=<Scenario AC-n 或 S-id>`
`role=` 必須對得上同 feature `1-discussion.md` Actors 表某一格,或 Fast 無 1-discussion 時對得上該 4-spec 某條 Operational Context 的 Actor。`scenario=` 必須對得上 `3-prototype.md` 的 `### Scenario AC-n`,或 Fast 無 Stage 3 時對得上一個 S-id。

**審的時候看什麼**
遮住前後文只看該行,要能答「驗了誰、驗了哪場」。有人按過 ≠ 代表性角色驗過。

#### S-5.1 模板必須含 role= 與 scenario= 字面
- GIVEN:落地後的 `_templates/3-prototype.md` User Demo Feedback
- WHEN:搜 `Human verdict`、`role=`、`scenario=`
- THEN:三個字面都在；模板說明只寫 ACCEPTED + 姓名日期 = 不完整
- 觀測:從模板該節看 | 三字面都在 | 落地前 n-a:模板未改;替代=`rg -n "Human verdict|role=|scenario=" _templates/3-prototype.md`；Stage 6 改模板後重跑
- Operational Context:
  - Actor:後讀 3-prototype 的人
  - Goal:一行內答出驗了誰、哪場
  - Situation:Demo 後填 verdict
  - Known information:8A LIGHT；現制已擋 Agent 代填
  - Missing information:簽名的人是不是該角色（人判；本包不擋冒名）
  - Human decision:人類親填 ENUM + attestation；Agent 禁代填
  - Authority:牙擋缺 role／scenario；attestation 仍是人類主權
  - External dependency:真人 Demo
  - Out-of-system action:人走 Demo Script
  - Waiting/timeout behavior:未 Demo = NOT_REVIEWED,不得當 ACCEPTED
  - Recovery:殘行補 role= 與 scenario= 後重填,不把殘行標 ACCEPTED
  - Audit/handoff requirement:attestation 行仍由人類親寫
  - Observation:見本條觀測

#### S-5.2 只寫 ACCEPTED + 姓名日期的對照稿不得當完整 verdict
- GIVEN:對照稿 3-prototype 含 `Human verdict: ACCEPTED` 與 `Verdict attestation: human:rick @ 2026-09-13`,但無 `role=`、無 `scenario=`
- WHEN:跑本包掛進 `check-realworld.sh` 家族的指定檢查（模板地板 + 對照稿）
- THEN:exit ≠ 0；該稿不得被當成完整 verdict
- 觀測:從 exit 與輸出看 | exit ≠ 0 且含 role 或 scenario 字樣 | 落地前 n-a:牙未延伸;替代=本條 GIVEN；Stage 6 放 `scripts/fixtures/discovery-gaps/verdict-accepted-name-only/`
- Operational Context:不適用 — 與 S-5.1 同一交接；本條只換殘行。

#### S-5.3 本包不要求 Actor Coverage 全表
- GIVEN:落地後的 `_templates/3-prototype.md` 與本包 4-spec Out of Scope
- WHEN:搜 `Actor Coverage`
- THEN:模板不新增每個關鍵角色的 direct interview／observation／proxy／not covered 全表；本包 Out of Scope 列明不做全表
- 觀測:從模板與本檔 Out of Scope 看 | 無全表欄位,且 Out of Scope 點名 A-5 全表 | 本檔 Out of Scope 節可跑；模板落地前 n-a:現況本就無全表
- Operational Context:不適用 — 範圍禁令,無人員交接。

### R-6: 系統 SHALL 讓 Stage 1 高影響列在 Stage 4 仍有去向
G-out-6／SC-6／AC-6／4A。Stage 2 表引用 Stage 1 原文片段 + 去向 ∈ {本方案處理, 刻意維持, Non-Goal, 另開 slug, 仍待驗} + 一句理由。不另發 RW-id。標「本方案處理」者本 4-spec 至少一條 R／S；其餘落到 Out of Scope／Known limit／後續 slug。

**disposition 表頭（本檔釘死）**
`| 引用（Stage 1 原文片段） | 去向 | 理由 |`

**審的時候看什麼**
用原文片段對一次,不是對 RW-id。去向空白 = SC-6 失敗。散文「痛點有處理」不算。

#### S-6.1 去向空白的對照表必須現形
- GIVEN:一份 2-decision 對照表,列「Journey「痛點消失」」的去向欄為空
- WHEN:跑本包掛進 `check-realworld.sh` 家族的指定檢查,或 G1 審面點名
- THEN:exit ≠ 0 或審面指出該列無去向；不得只靠「痛點有處理」散文過關
- 觀測:從檢查 exit 或審面字樣看 | 該列被點名 | 落地前 n-a:牙未延伸;替代=Stage 3 Method 4A 壞卡；Stage 6 放 `scripts/fixtures/discovery-gaps/disposition-blank/`
- Operational Context:
  - Actor:收斂者／G1 reviewer
  - Goal:Stage 1 痛點到 Stage 4 仍找得到
  - Situation:寫 2-decision disposition
  - Known information:表頭三欄；去向五值
  - Missing information:片段截得是否有意義（人判）
  - Human decision:填五值之一 + 一句理由
  - Authority:牙擋空去向；G1 抽列
  - External dependency:Stage 1 原文
  - Out-of-system action:無
  - Waiting/timeout behavior:空去向不得送 G1
  - Recovery:補去向與理由；中斷後從片段恢復,不靠記憶
  - Audit/handoff requirement:表留在 2-decision 本文（Variant A）
  - Observation:見本條觀測

#### S-6.2 本方案處理的列必須落到至少一條 R／S
- GIVEN:本 slug 2-decision Real-world Disposition 中去向=本方案處理的列
- WHEN:對本 4-spec 的 R／S 標題與 THEN
- THEN:下列列各至少命中一條 R:Journey「發現被錨定」→ R-2；Journey「點頭當證據」→ R-3；Journey「痛點消失」→ R-6；Journey「問題沒改善」→ R-7；Journey「互動風險晚露」→ R-9；Workaround「owner 用審核筆記記缺口」→ R-1；Workaround「現場證據靠記憶轉述」→ R-8；Workaround「Fast 直接寫 4-spec」→ R-9；Workaround「人口頭記先問現況」→ R-2；Exception「`[~]` 可走到 G2」→ R-4
- 觀測:從本檔 R 標題與上列對照看 | 十列皆指向一個 R-id | 本檔可跑,無需等牙
- Operational Context:不適用 — 本檔對帳,無新交接。

#### S-6.3 不得發明 RW-id
- GIVEN:落地後的 `_templates/2-decision.md`、`_templates/4-spec.md`、本檔
- WHEN:搜 `RW-` 後接數字作為第二條 ID 鏈
- THEN:模板與本檔都不要求 R／S 引用 `RW-n`；disposition 只引用原文片段
- 觀測:從三檔搜尋看 | 無「引用 RW-」規則 | `rg -n "RW-[0-9]" docs/dev/requirement-discovery-gaps/4-spec.md _templates/2-decision.md _templates/4-spec.md`；本 hop 本檔必須零命中
- Operational Context:不適用 — 禁令,無人員交接。

### R-7: 系統 SHALL 在出貨 Exit 留下回看四欄
G-out-7／SC-7／AC-7／5A。約定寫在 7-review Exit。結果到期用既有 `history-append.sh` 追加。不另造永久 lookback 檔。G3 不必等數週結果。填了任意數字不得被當成問題已改善。

**lookback 四欄字面（本檔釘死）**
```
- 回看日期:
- 回看 owner:
- 資料來源:
- 低於何值重開:
```

**審的時候看什麼**
四欄都在才算出貨時留下約定。缺任一欄 = 指定檢查 exit ≠ 0。到期未回看不得把問題寫成已改善。

#### S-7.1 Exit 缺四欄之一必須紅
- GIVEN:一份已宣稱 shipped 的 7-review,Exit 缺「回看日期」「回看 owner」「資料來源」「低於何值重開」任一欄
- WHEN:跑本包掛進既有家族的指定檢查（`check-realworld.sh` 地板或與 7-review 同家族的已掛入口,不另開腳本）
- THEN:exit ≠ 0；輸出指出缺失欄名
- 觀測:從 exit 與輸出看 | exit ≠ 0 且點名缺欄 | 落地前 n-a:7-review Exit 現無四欄;替代=`rg -n "回看日期|回看 owner|資料來源|低於何值重開" _templates/7-review.md`；Stage 6 改 Exit 並放 `scripts/fixtures/discovery-gaps/lookback-missing-field/`
- Operational Context:
  - Actor:owner
  - Goal:出貨時留下誰／何時／用什麼／門檻
  - Situation:勾 Exit、準備 shipped
  - Known information:四欄字面；結果走 HISTORY
  - Missing information:門檻數字是否代表問題改善（人判）
  - Human decision:填四欄；到期用 history-append 追加結果
  - Authority:牙驗四欄在；指標語意是人判
  - External dependency:`scripts/history-append.sh`
  - Out-of-system action:日曆到期後回看採用專案 Stage 1 Goals
  - Waiting/timeout behavior:回看日未到,不得把問題寫成已改善
  - Recovery:缺欄先補再勾 shipped；不要另造 lookback.md
  - Audit/handoff requirement:約定在 7-review Exit；結果在 HISTORY 追加列
  - Observation:見本條觀測

#### S-7.2 結果必須走 history-append,不得另造 lookback.md
- GIVEN:落地後的 `_templates/7-review.md` Exit 與本包 Decision 5A
- WHEN:搜 lookback 落點
- THEN:Exit 含 S-7.1 四個欄位名；正文指向 `history-append.sh` 或同等既有 HISTORY 寫入口；不要求每 feature 一份 `lookback.md`
- 觀測:從 Exit 與本檔 Out of Scope 看 | 四欄名在模板,lookback.md 在 Out of Scope | 落地前模板 n-a:Exit 無四欄；本檔 Out of Scope 可跑
- Operational Context:不適用 — 與 S-7.1 同一交接；本條只禁新檔種。

#### S-7.3 任意數字不得被當成問題已改善
- GIVEN:一份 7-review Exit 四欄都填了,但「低於何值重開」為「0」或「之後看」且無資料來源可重開
- WHEN:人讀該 Exit,或跑指定檢查
- THEN:牙若只驗欄在,該稿可以形狀綠；正文與 7-review 指令必須寫明「數字在 ≠ 問題已改善」；到期未用寫下的來源核對真實問題,不得在 HISTORY 把原問題寫成已改善
- 觀測:從 Exit 指令句與 HISTORY 寫法看 | 指令含「已改善」的否定或同等「不得把問題寫成已改善」 | 落地前 n-a:指令未寫;替代=本條 THEN；Stage 6 把該句寫進 7-review Exit
- Operational Context:不適用 — 人判語意,牙不判指標。

### R-8: 系統 SHALL 只放行 owner 核准的事實路徑
G-out-8／SC-8／AC-8／6A。本輪 evidence manifest 在 `1-discussion.md` 的 `## Evidence manifest`（不另造永久檔種類）。欄:`想找哪類`／`為什麼`／`擬路徑或來源`／`owner 核准`／`已讀`。`owner 核准` ∈ {是, 未核, 禁}。未核准不得當已授權 evidence。仍禁 2／3／4／5／6／7。ticket／SOP 裡的解法建議不當事實。

**審的時候看什麼**
核准過的事實路徑讀得到事件／行為／結果。讀 `2-decision`／`4-spec` 仍被擋。未指名資料夾不得先列目錄。

#### S-8.1 未核准路徑不得當已授權 evidence
- GIVEN:manifest 一列「採用現場逐字稿」、擬路徑空、`owner 核准`=未核、`已讀`=否；1-discussion 高影響列卻把該路徑當來源
- WHEN:跑本包掛進 `devtalk-guard.sh` 或 `check-realworld.sh` 家族的指定檢查（改允許集合,仍是既有入口）
- THEN:exit ≠ 0（或 hook exit 2）；該列不得當已授權 evidence
- 觀測:從該檢查／hook 的 exit 與輸出看 | 非 0 且含核准或未核字樣 | 落地前 n-a:guard 只管 skill 寫入洩漏;替代=`rg -n "2-decision|4-spec" hooks/devtalk-guard.sh` 現況 L21 只掃洩漏字;Stage 6 放 `scripts/fixtures/discovery-gaps/manifest-unapproved-cited/`
- Operational Context:
  - Actor:討論 agent
  - Goal:owner 核准後才讀事實
  - Situation:想引用未指名 SOP／逐字稿
  - Known information:manifest 五欄；圍欄仍禁 2–7
  - Missing information:owner 是否會核這條路徑
  - Human decision:owner 填核准格
  - Authority:未核 = 禁讀；owner 才能改「是」
  - External dependency:外部 connector 仍靠權限＋人
  - Out-of-system action:列「想找哪類＋為什麼」送 owner
  - Waiting/timeout behavior:核准格空白就停,不得往下讀
  - Recovery:從核准格恢復,不必重寫主張
  - Audit/handoff requirement:核准痕跡留在同檔 manifest
  - Observation:見本條觀測

#### S-8.2 讀 2-decision／4-spec 仍被擋
- GIVEN:manifest 或 1-discussion 引用 `docs/dev/*/2-decision.md` 或 `docs/dev/*/4-spec.md` 當事實來源,即使有人把核准格寫成「是」
- WHEN:跑 S-8.1 同一圍欄／檢查
- THEN:exit ≠ 0（或 hook exit 2）；方案檔仍禁,核准格不能覆寫這條禁令
- 觀測:從 exit 與輸出看 | 非 0 且含 2-decision 或 4-spec 或方案檔字樣 | 落地前 n-a:guard 未管事實入口;替代=本條 GIVEN；Stage 6 放 `scripts/fixtures/discovery-gaps/manifest-solution-file-cited/`
- Operational Context:不適用 — 與 S-8.1 同一交接；本條只換禁檔。

#### S-8.3 ticket／SOP 解法建議不得當事實
- GIVEN:高影響列來源類型字面為「ticket 建議做 dashboard」或「SOP 規定要 API」,無事件／行為／結果出處
- WHEN:跑 S-8.1 同一檢查,或 G1 抽查
- THEN:該來源不得當事實；要嘛改成事件／行為／結果,要嘛改 Assumption+期限
- 觀測:從檢查輸出或 G1 抽查紀錄看 | 該列被拒或被改欄 | 落地前 n-a:牙未延伸;替代=本條 GIVEN；Stage 6 放 `scripts/fixtures/discovery-gaps/ticket-solution-as-fact/`
- Operational Context:不適用 — 與 S-8.1 同一交接；本條只換來源類型。

### R-9: 系統 SHALL 在 Fast 寫 4-spec 前收完六問
G-out-9／SC-9／AC-9／7A／OC-6。進 Stage 4 **之前**六問:下一步／權限／等待語意／交接／系統外／中斷恢復。每問是／否＋一句。空白 ≠ 已分診。全否且已有 approved spec 且不改語意的純視覺／文案 → 維持 Fast,不必 mini。命中不一律升 full:owner 裁升 full、fast+mini、或 Owner Call 接受風險。命中列無去向 → 擋進 Stage 4（與 3A 同走 `check-spec-gate.sh`）。

**Fast 六問欄位名（本檔釘死）**
Fast-lane 4-spec 在 `## ADDED Requirements` **之前**必須有節 `## Fast triage`:
`| # | 問 | 答（是／否＋一句） | 命中 |`
六問字面:
1. 改變下一步？
2. 改權限／核准語意？
3. 改等待／完成語意？
4. 改角色交接？
5. 改系統外動作？
6. 改中斷恢復？
末列 `去向` 值 ∈ {Fast, 升 full, fast+mini, OC 接受風險}。
本 slug 本檔 lane=full,不填這張表；空白表不得被抄成「已分診」。

**審的時候看什麼**
「只改狀態字、把等待顯示成完成」必須命中第 3 問。六問寫在 Verification Profile（lane 已選完）= 晚了。

#### S-9.1 Fast 4-spec 六問未收束不得當已分診
- GIVEN:一份 `lane: fast` 的 4-spec,無 `## Fast triage`,或六問任一「答」欄為空
- WHEN:跑 `bash scripts/check-spec-gate.sh <該 4-spec.md>`
- THEN:exit 1；輸出指出 Fast triage 未收束或空白
- 觀測:從 spec-gate exit 與輸出看 | exit 1 且含 Fast 或六問或 triage 字樣 | 落地前 n-a:現況 spec-gate 無此項;替代=本條 GIVEN；Stage 6 放 `scripts/fixtures/discovery-gaps/fast-triage-blank/`
- Operational Context:
  - Actor:Fast 實作者
  - Goal:寫 R／S 前先看互動風險
  - Situation:檔數少、已有 spec、想走 Fast
  - Known information:六問字面；OC-6 純視覺可維持 Fast
  - Missing information:「不改語意」是否成立（reviewer 對 diff）
  - Human decision:全否且純視覺 → Fast；命中 → owner 裁三擇一
  - Authority:spec-gate 擋未收束；owner 裁去向
  - External dependency:已有 approved spec（OC-6 條件之一）
  - Out-of-system action:owner 回去向
  - Waiting/timeout behavior:六問空白不得開寫 R／S
  - Recovery:從六問表接著填,不靠記憶
  - Audit/handoff requirement:表在 4-spec 頂、先於 ADDED
  - Observation:見本條觀測

#### S-9.2 等待顯示成完成必須命中第 3 問
- GIVEN:對照案六問答:1 否「只改狀態字顯示」；2 否；3 是「等待被顯示成完成」；4–6 否
- WHEN:把該表放進 `## Fast triage`
- THEN:`命中` 欄第 3 問為是；去向不得為空,必須 ∈ {升 full, fast+mini, OC 接受風險}；不得把去向填 Fast
- 觀測:從該表第 3 列與去向列看 | 第 3 問命中且去向是三擇一 | 落地前用紙上 Stage 3 AC-9 對照案；Stage 6 放 `scripts/fixtures/discovery-gaps/fast-wait-shown-as-done/`
- Operational Context:不適用 — 與 S-9.1 同一交接；本條只換對照案。

#### S-9.3 命中無去向必須擋進 Stage 4
- GIVEN:一份 Fast 4-spec,第 3 問命中,去向欄空
- WHEN:跑 `check-spec-gate.sh`
- THEN:exit 1；輸出指出命中無去向
- 觀測:從 exit 與輸出看 | exit 1 且含去向或命中字樣 | 落地前 n-a:牙未延伸;替代=本條 GIVEN；Stage 6 放 `scripts/fixtures/discovery-gaps/fast-hit-no-disposition/`
- Operational Context:不適用 — 與 S-9.1 同一交接；本條只換去向空。

#### S-9.4 純視覺全否維持 Fast
- GIVEN:六問皆否＋一句「只改 CSS 顏色／文案錯字」；同 slug 已有 approved 4-spec；diff 不改權限／等待／交接語意
- WHEN:讀 `## Fast triage` 去向
- THEN:去向可以是 Fast；不必 mini、不必升 full
- 觀測:從去向列與 OC-6 看 | 去向=Fast | 本條是 OC-6 收窄；Stage 6 放 `scripts/fixtures/discovery-gaps/fast-visual-only/` 且 spec-gate exit 0（無其他 C 失敗時）
- Operational Context:不適用 — 與 S-9.1 同一交接；本條只換 OC-6 綠路。

## MODIFIED Requirements

本 repo 無 `docs/specs/` living spec。下列是活教師／牙的現況條文,落地後被上列 ADDED 取代。引原文,不另發第二套 R 號。

### M-1: 1-discussion 雛形「從哪看」鎖通道 → 改由 R-1 分欄
原條文:`_templates/1-discussion.md` L94–L96「從哪看:<畫面路徑 | API 端點 | log | 產出檔>」。落地後該行不再把畫面路徑／API 端點列為必填候選。觀測見 S-1.1。

### M-2: N3「附推薦答案」硬規則 → 改由 R-2 限裁決題
原條文:`skills/dev-talk/nodes/N3-probe.md` L22「一次只問一題、附推薦答案」。落地後此句不得套在發現題。觀測見 S-2.1。

### M-3: Evidence／Assumption 二分 + 牙只驗字樣 → 改由 R-3 枚舉與來源欄
原條文:`_templates/1-discussion.md` L72–L73；`scripts/check-realworld.sh` L88–L91 只驗 Assumption／「訪談」字樣。落地後高影響列要枚舉 + 來源 XOR 期限。觀測見 S-3.1。

### M-4: `[~]` 可走到 G2 → 改由 R-4 過期擋 spec-gate
原條文:`_templates/1-discussion.md` L82–L86；`scripts/check-spec-gate.sh` 現只做 C1–C6。落地後加過期高影響 Assumption 項。觀測見 S-4.1。

### M-5: Human verdict 只守人類親填 → 改由 R-5 加 role／scenario
原條文:`_templates/3-prototype.md` Participants 自由文字；`scripts/check-realworld.sh` L137–L138 守不是 Agent 代填。落地後一行內要有 role= 與 scenario=。觀測見 S-5.1。

### M-6: Stage 2 只收 Goals／AC／`[>]` → 改由 R-6 disposition
原條文:`_templates/2-decision.md` 頂註步 0／步 6。落地後加原文片段去向表。觀測見 S-6.1。

### M-7: 7-review Exit 勾到 shipped 即止 → 改由 R-7 回看四欄
原條文:`_templates/7-review.md` L316–L342 Exit 無回看四欄。落地後四欄字面進 Exit。觀測見 S-7.1。

### M-8: 討論白名單不管事實入口 → 改由 R-8 manifest + 圍欄射程
原條文:`hooks/devtalk-guard.sh` L16–L21 只掃 `skills/dev-talk/*` 寫入洩漏；`skills/dev-talk/SKILL.md` L17–L21 未指名不得列目錄。落地後核准清單可讀,方案檔仍禁。觀測見 S-8.1。

### M-9: Fast 省略 1–3、人機風險寫在 4-spec → 改由 R-9 進 4 前六問
原條文:`skills/dev-flow/SKILL.md` L34–L36；`_templates/4-spec.md` L266–L269。落地後 Fast 4-spec 頂節 `## Fast triage` 先於 ADDED。觀測見 S-9.1。

### M-10: 範例 Goal／AC／Interview 鎖 dashboard → 改由 R-1 同期改口
原條文:`example/contract-expiry-reminder/1-discussion.md` L62–L65、L83–L103、L119。落地後 Goals 不再把登入／點擊／一眼可見當目標本身。觀測見 S-1.3。

## REMOVED Requirements

無。七關結構、Fast 合法跳過 Stage 1–3、A-5 LIGHT、既有三支腳本家族名,一律保留。

## 行為流程圖(R 級)

```
[R-1] 分欄結果與構想
Goals 只寫工作結果
構想進 Requested solution

[R-2] 發現題不附推薦
問句加 發現｜
裁決題才可附選項

[R-3] 主張回到來源
高影響列選五值枚舉
來源 XOR Assumption+期限

[R-4] 拒絕過期假設
四欄可被 spec-gate 看見
過期未驗 exit 1

[R-5] 寫出角色與場景
verdict 一行含 role= scenario=
殘行不得當完整

[R-6] 痛點仍有去向
引用原文填五值去向
本方案處理對到 R/S

[R-7] 留下回看四欄
Exit 日期 owner 來源 門檻
結果走 HISTORY 追加

[R-8] 放行核准事實
manifest 同檔五欄
方案檔仍禁讀

[R-9] 收完六問
Fast 頂節先於 ADDED
等待當成完成必須命中
```

## Acceptance Criteria

- 本檔全部 S 的指定檢查（落地後）與本 hop 可跑的替代觀測都綠。
- 既有 `bash scripts/check-realworld.sh`、`bash scripts/check-spec-gate.sh`（對本檔）、`bash hooks/devtalk-guard.sh` 既有洩漏掃描回歸綠（本 hop 不改它們；落地後延伸射程不得拆掉 C1–C6 與現況 137 項地板,地板數字隨新增 check 上調）。
- 非功能:不新造檢查家族；不發明 RW-id；不另造 lookback.md；本 hop 不改 STATUS／模板正本。
- 本 hop 不宣稱 G2 PASS。frontmatter `verdict` 空；`status` 留 draft。

## Out of Scope

- 1B／1C／2B／2C／3B／3C／4B／4C／5B／5C／6B／6C／7B／7C／8B／8C（2-decision Rejected）。
- 新造 `check-discovery-gaps.sh` 或其他第二套牙家族。
- RW-id、Journey／Actor 第二鏈、每 feature `lookback.md`、Actor Coverage 全表。
- dashboard／API 黑名單。
- 拆成九個 slug；重開九條 DO／LIGHT；重開 1A–8A。
- 本 hop 改 `_templates/`／`skills/`／`example/`／守衛正本／STATUS／HISTORY。
- 本 hop 發明 G2／G3、代填 3-prototype ACCEPTED／attestation、把本檔 `verdict` 寫成 PASS。
- 把 Fast 合法跳過 Stage 1–3 改成必須跑 1–3（Exception「刻意維持」）。
- 外部 connector 自動拉票／自動讀未授權 Drive／GitHub（仍靠權限＋人）。
- 從最終 1-discussion 還原整場對話的硬 gate（A-2 已拒假裝）。

### Stage 3 對帳

派工 brief 稱 Stage 3 ACCEPTED。本 tree `3-prototype.md` 在 `be808fb` 仍為 NOT_REVIEWED。本 hop 不改該檔。下列把 Demo Script／Method 走查逐場落到 R／S；G2 仍須人類確認 3-prototype attestation 後才能把本檔 `verdict` 寫成 PASS。

- 3-prototype「Scenario AC-1」→ R-1／S-1.1／S-1.2（分欄；壞卡 dashboard 在 Goals）
- 3-prototype「Scenario AC-2」→ R-2／S-2.1／S-2.3（發現題前綴；壞卡先給答案）
- 3-prototype「Scenario AC-3」→ R-3／S-3.1／S-3.2／S-3.3（來源欄；點頭不當來源）
- 3-prototype「Scenario AC-4」→ R-4／S-4.1／S-4.2／S-4.3（過期擋 G2）
- 3-prototype「Scenario AC-5」→ R-5／S-5.1／S-5.2（verdict 一行角色／場景）
- 3-prototype「Scenario AC-6」→ R-6／S-6.1／S-6.2（痛點消失有去向）
- 3-prototype「Scenario AC-7」→ R-7／S-7.1／S-7.2／S-7.3（回看四欄；不另造檔）
- 3-prototype「Scenario AC-8」→ R-8／S-8.1／S-8.2／S-8.3（核准後才讀；方案檔仍禁）
- 3-prototype「Scenario AC-9」→ R-9／S-9.1／S-9.2／S-9.3（六問在進 4 前；等待誤標命中）
- Method 走查「Variant A 同檔就地欄」→ 各 R 的「欄在同檔」；Variant B 另造檔種 → Out of Scope（與 5A 同型成本）；Variant C 審查時重建 → Rejected,由 R-3／R-6／R-9 負向卡覆蓋
- Operational Context Recovery:各重要 S 的 Recovery 欄即下落（搬欄／重寫問句／補來源或期限／補 resolved 或 OC／補 role=scenario=／補去向／補四欄／從核准格恢復／從六問表恢復）

## Diff Budget

本節是估計,不是承諾。[Assumption]

| 區塊 | 檔（估） | 非測試行（估） | 測試／fixture 行（估） |
|---|---|---|---|
| 模板 1／2／3／4／7 | 5 | 220 | 0 |
| skills/dev-talk 節點 + SKILL + 指南對稱句 | 6 | 160 | 0 |
| 範例 contract-expiry-reminder | 2 | 80 | 0 |
| check-realworld／check-spec-gate／devtalk-guard 射程 | 3 | 180 | 0 |
| scripts/fixtures/discovery-gaps/* | 12 | 0 | 700 |
| 既有測試掛鉤（architecture-guards／selftest 等） | 2 | 40 | 120 |
| **合計** | **≤30 檔** | **≤680 行** | **≤820 行** |

本 hop:2 檔（`4-spec.md`／`4-spec.html`）,不計入上表落地預算。超支本身非偏差,停下判 L1／L2；分不清當 L2。

## Dependencies

- `scripts/check-realworld.sh` — 已有模板／範例地板；本包延射程,不另造家族。
- `scripts/check-spec-gate.sh` — 已是 G2 形狀 Gate；本包加過期假設與 Fast triage 項。
- `hooks/devtalk-guard.sh` — 已有討論圍欄；本包改允許集合,仍禁方案檔。
- `scripts/history-append.sh` — lookback **結果**唯一寫入口。
- `example/contract-expiry-reminder/1-discussion.md` — 活教師,Q14 同 slug 改口。
- 無新外部服務、無 schema、無 plugin bump、無新腳本檔名。

## Design Boundary Contract(條件式;G2 一併審)

- Applicability: applicable
- Trigger(s): ③修改跨模組 Interface（模板欄位 ↔ 牙射程）；⑧討論讀取允許集合（近 credential／權限圍欄）；⑩模板、skill、三支腳本、範例共同參與；⑪Fast 六問／過期假設／核准格的等待與恢復
- Design source: 2-decision 1A–8A + Stage 3 Variant A；沿用既有三支腳本,new local design 只限欄位字面與過期／triage 判準

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| `_templates/` Stage 1–4／7 | 人抄的欄位與節名 | 方法論母版 | 被 realworld／spec-gate 讀 | 新腳本家族、RW-id |
| `skills/dev-talk` | 發現題／裁決題問法 | 方法論母版 | 白名單；本輪 manifest | 讀 2–7；未核路徑 |
| `scripts/check-realworld.sh` | 模板／範例地板 + 本包對照稿 | 該腳本 | 模板、範例、fixture | 取代 spec-gate 當 G2 擋點 |
| `scripts/check-spec-gate.sh` | G2 形狀 + 過期假設 + Fast triage | 該腳本 | 4-spec、同 slug 2-decision status | 新入口檔名 |
| `hooks/devtalk-guard.sh` | 討論圍欄 + 事實入口允許集合 | 該 hook | 1-discussion manifest | 放寬整個 docs／notes |
| `example/contract-expiry-reminder` | 活教師 | 該範例 | 與模板同 hop 改口 | 另開 slug 才改範例 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| spec-gate 讀 4-spec + 引用的 Assumption 列 | 4-spec 路徑 → exit 0／1／2 | 過期未驗 → 1；用法錯 → 2 | 同一 run 內讀 4-spec 與同 slug 2-decision；只成功讀一檔不得綠 | 保留 C1–C6；本包加項 |
| realworld 讀模板／範例／對照稿 | repo root → exit 0／1 | 缺欄／缺前綴／殘行 verdict → 1 | 單次行程讀齊模板+範例；地板數字隨 check 上調 | 保留既有 137 項語意,數字可增 |
| devtalk-guard 讀寫入 + manifest | hook JSON → exit 0／2 | 未核路徑或方案檔 → 2 | 核准格與禁檔同一判定；核准不能覆寫 2–7 禁令 | 既有洩漏掃描仍在 |
| Fast triage → lane | 六問表 → 去向 | 空白或命中無去向 → spec-gate 1 | 表必須先於 ADDED；與 Verification Profile `lane:` 同一檔 | 不改 Fast 可跳過 1–3 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| 高影響列解析器 | 抽出枚舉／來源／期限／resolved | spec-gate、realworld | 原文片段 → 列 dict | 缺鍵 → 該檢查紅 | `scripts/fixtures/discovery-gaps/*` |
| 過期判準 | ISO 日或 Stage／G token | spec-gate、2-decision status | token + 已記錄 PASS → 過期 | 無 resolved／OC → exit 1 | S-4.1／S-4.2／S-4.3 fixture |
| Fast triage 解析器 | 六問答與去向 | spec-gate | 表 → hit 集合 + 去向 | 空答或命中無去向 → exit 1 | S-9.1／S-9.3 fixture |
| manifest 允許集合 | 核准路徑 vs 禁檔 | devtalk-guard | 列 → allow／deny | 未核引用 → exit 2 | S-8.1／S-8.2 fixture |

### Design Constraints
- 必須:沿用三支既有腳本家族；Variant A 同檔就地欄；disposition 引用原文；lookback 結果走 HISTORY。
- 禁止:新檢查家族、RW-id、lookback.md、Actor Coverage 全表、dashboard／API 黑名單、本 hop 改 STATUS／模板、本 hop 寫 G2 PASS。
- Extension point:Stage 6 才把 fixture 放進 `scripts/fixtures/discovery-gaps/` 並延牙射程。
- Known design limit:A-2 誘導無法從最終 md 還原；枚舉可灌水（牙只驗 ∈ 集合）；「這列算不算高影響」與「不改語意」是人判；採用現場是否照抄仍是 Assumption（OC-3）；3-prototype 在 tip 仍 NOT_REVIEWED,本 hop 不代填。

## Verification Profile(G2 一併審)

- lane: full
- Risk: high
- Failure model:見下表
- Negative constraints:
  - 不得新造檢查家族或 RW-id 或 lookback.md
  - 不得用 dashboard／API 黑名單代替分欄
  - 不得把點頭當唯一來源
  - 不得把未核路徑或 2–7 方案檔當已授權 evidence
  - 不得把 Fast 六問空白當成已分診
  - 不得在本 hop 寫 G2 PASS 或代填 Stage 3 attestation
  - 不得改 STATUS／HISTORY／模板正本（本 hop）
- Required layers:check-realworld / check-spec-gate / spec-gate-C1-C6-regression
- Conditional layers:architecture-guards — 當 Stage 6 把 discovery-gaps fixture 掛進 `scripts/test-architecture-guards.sh`（或同等已有掛鉤）時必跑
- Explicitly excluded layers:Mutation（本包改方法論文檔與檢查射程,不改 mutation 工具鏈）；金流／schema（無）
- Final fresh entry point:`bash scripts/check-realworld.sh && bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md`
- Reliability triage:
  - Concurrency: n-a — 本包改文件欄位與同步檢查腳本,無並行寫入契約
  - Idempotency: applicable — 同一份對照稿重跑指定檢查必須得到同一 exit；落到 S-4.1／S-9.1 與 Design Boundary spec-gate 列
  - Timeout/retry: n-a — 檢查同步結束,無重試契約；Assumption 期限是人的日曆／stage token,不是系統 timeout
- Demo verdict:派工 brief 稱 Stage 3 ACCEPTED。本 tree `3-prototype.md` 在 `be808fb` 仍為 Human verdict NOT_REVIEWED、無 attestation。本 hop 不改該行、不發明 G2。G2 審查者須核 3-prototype 人類 attestation 後才能把本檔 `verdict` 標 PASS。
- lane 由判準決定:命中權限圍欄（R-8）與高風險人機互動（R-2／R-9 等待語意）→ 不得 fast；本檔 full 與判準一致,無偏離。

### Failure Model(Risk: high 必填)

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 過期高影響假設仍送進 G2 | 測試綠、方向錯 | spec-gate 對 S-4.1 fixture 仍 exit 0 | check-spec-gate | — |
| 已驗／OC-accept 列被誤擋 | 合法稿進不了 G2 | S-4.2／S-4.3 fixture exit 1 | check-spec-gate | — |
| 未核路徑被當已授權 | 方案或聽說混進事實 | S-8.1 fixture 綠 | devtalk-guard／check-realworld | 外部 connector 仍靠權限＋人 |
| Fast 六問全打「否」當儀式 | 等待誤標晚露 | S-9.2 對照案去向=Fast | check-spec-gate + reviewer 對 diff | 「不改語意」人判 |
| 範例仍教 Goal=dashboard | 採用者抄通道 | S-1.3 Goals 仍含登入／點擊／一眼可見 | check-realworld 範例地板 | 採用現場照抄=OC-3 Assumption |
| 新造第二套牙或 RW-id | 第二套方法論 | diff 出現 `check-discovery-gaps.sh` 或 `RW-1` | G2 審 Diff／Out of Scope | — |

## Drafting Decisions(草擬自判,待人審)

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 高影響 = 為假會改動分欄／lane／權限／等待語意／G2 送審／去向／lookback 門檻或 owner 至少一項；G1 抽一條回走 | OC-5 要 4-spec 釘抽樣,避免每句都貼 | `2-decision.md` OC-5；本檔 R-3 規則框 | 牙誤殺普通 Context,或高影響列漏標 | 待人審 |
| DD-2 | Assumption 機器形用 `期限=` ISO 日或 Stage／G token + `resolved=` 空／Observed／Reported／`OC-accept:<id>`；`Stage 2`／`G1` + 2-decision approved = 過期 | 期限常是關卡不是日曆；要讓 spec-gate 看得見 | `2-decision.md` 內部技術選擇「四欄機器可讀形」；`3-prototype.md` 3A 表 | 改用純 ISO 日或改 token 集合 | 待人審 |
| DD-3 | evidence manifest 節名 `## Evidence manifest`,檔=同 slug `1-discussion.md`,不另造 `evidence-manifest.md` | Variant A；5A 已拒另造永久檔 | `3-prototype.md` Result 6A 列；`2-decision.md` 5A／6A | 改回 Variant B 分檔 | 待人審 |
| DD-4 | Fast 節名 `## Fast triage`,必須先於 `## ADDED Requirements`；本 slug 本檔 full 不填表 | 7A 要在進 4 前；空白表 ≠ 已分診 | `3-prototype.md` 7A；`2-decision.md` 7A | 改節名或改掛 Verification Profile | 待人審 |
| DD-5 | 過期假設與 Fast 未收束都掛進既有 `check-spec-gate.sh`；模板／範例／verdict 殘行／disposition 空去向掛 `check-realworld.sh`；事實入口掛 `devtalk-guard.sh` | OC-1 只准延這三支 | `2-decision.md` OC-1、決策點 1／3／6 | 要新入口檔名,與「不另造家族」重審 | 待人審 |
| DD-6 | Feature Risk = high（權限圍欄 + 等待語意人機互動 + G2 誤綠）;lane = full,與判準一致 | 模板 Risk 判準含權限與高風險人機；自動升 Full 同款 | `_templates/4-spec.md` Lane 規則；本檔 R-8／R-9 | 改 normal 則 Failure Model 變選配 | 待人審 |
| DD-7 | 本 hop 把 AC-1～AC-9 寫成可測 R／S,但不改 3-prototype、不寫 attestation、不把本檔 verdict 標 PASS | 派工稱 Stage 3 ACCEPTED；tip 檔仍 NOT_REVIEWED；author ≠ approver | 本 hop brief；`3-prototype.md` User Demo Feedback；N6／N7 禁發明 G2 | 有人先在 3-prototype 親寫 ACCEPTED+attestation,G2 才可過 | 待人審 |
| DD-8 | lookback 四欄字面用「回看日期／回看 owner／資料來源／低於何值重開」；結果只准 `history-append.sh` | 5A 已選；Stage 3 已釘字面 | `3-prototype.md` 5A；`2-decision.md` 5A | 改欄名或改落 HISTORY 本文 | 待人審 |

### 內部技術選擇(下層,告知即可)

- 對照稿目錄名建議 `scripts/fixtures/discovery-gaps/<case>/`；本 hop 不建該目錄。
- 行為流程圖用 vbox 直式,一 R 一盒,不畫樹狀分支。
- 審頁用 `scripts/build-stage4-html.py --action`,不手包 html-shell。
- 本檔不 bump plugin、不改 `.dev-flow`、不寫 `.devstage4-cursor.json` 進 Git。
- S 的落地前觀測標 `n-a:牙射程未延伸` 並給本 repo 可讀的現況行號,避免 G3 才發現觀測指向尚未存在的 fixture。

## Test Skeletons(選配)

- `test_s_1_2_goals_dashboard_in_wrong_column`
- `test_s_2_2_prefix_one_side_deleted`
- `test_s_3_1_claim_no_source_no_deadline`
- `test_s_3_3_nod_as_only_source`
- `test_s_4_1_expired_assumption_blocks_g2`
- `test_s_5_2_verdict_accepted_name_only`
- `test_s_6_1_disposition_blank`
- `test_s_7_1_lookback_missing_field`
- `test_s_8_1_manifest_unapproved_cited`
- `test_s_8_2_solution_file_still_blocked`
- `test_s_9_1_fast_triage_blank`
- `test_s_9_2_wait_shown_as_done_hits_q3`

## 確認紀錄

- 雙源清點 | 2026-09-13 | 驗收雛形 AC-1～AC-9 共 9 條 → ADDED R-1～R-9。living 無 `docs/specs/`；活教師／牙 10 條 → MODIFIED M-1～M-10。REMOVED 0。
- R 範圍 | 2026-09-13 | 派工 brief:Stage 4 only、nine-gap package、G1+Stage3 ACCEPTED。範圍=SC-1～SC-9 落地契約,不含模板正本與 G2 PASS。
- S 逐段 | 2026-09-13 | R-1 3S、R-2 3S、R-3 4S、R-4 3S、R-5 3S、R-6 3S、R-7 3S、R-8 3S、R-9 4S。每 S 有觀測欄。
- 3a 四節 | 2026-09-13 | AC／OOS／Diff Budget／Dependencies 齊。
- 3b Profile + Boundary | 2026-09-13 | lane=full、Risk=high、Failure Model 6 列、Reliability triage 三問、Design Boundary applicable。
- 3c Stage 3 對帳 | 2026-09-13 | AC-1～AC-9 + Variant A／B／C + Recovery 皆有下落。
- DD 掃描 | 2026-09-13 | 上層 DD-1～DD-8；未定事項三詞與 DD 未決標籤零命中。
- 本 hop 邊界 | 2026-09-13 | 只新增 4-spec.md／html。不改 STATUS／模板。不發明 G2。
