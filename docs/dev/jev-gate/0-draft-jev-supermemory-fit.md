---
title: jev × supermemory 接入評估（流程外草稿）
slug: jev-gate
status: draft
date: 2026-09-22
base: origin/main 79b7aab（v3.25.0 之後兩筆 docs）
kind: 0-draft（`skills/dev-flow/SKILL.md:35`：流程外草稿只當 Decide 站原料，不是 Intake 產出）
---

# 0-draft：把「要不要人看」這個決定交給 jev

## 1. 結論

- **jev 接。** 它不是拿來取代 reviewer 或測試，是拿來取代「人在每個 gate 判斷『這樣夠不夠、要不要我親自看』」這一步。dev-flow 現在每站的證據都已經是機器產的（Verify、reviewer findings、Evidence Gauntlet），缺的只是一個便宜、快、有校準機率的路由器。
- **supermemory 先不接。** dev-flow 已有自己的記憶子系統（`memory/agentmem/`，SQLite 快取 + git 追蹤的 `.dev-flow/`），supermemory 會重疊而不是補洞，而且自架版還在 v0.0.8。見 §9。
- **一個 env 就能用**：`TYPESAFE_API_KEY` 沒設 → 所有 jev 接入點自動關閉，行為跟現在一模一樣（fail-closed 到人）。設了 → 先跑影子模式記帳，再逐 gate 放行。

## 2. rick 要的流程，對照現況

| rick 的話 | 現在 dev-flow 怎麼做 | 差距 |
|---|---|---|
| 問答完就開始動 | Intake 出口是「Open Questions 三態全落入」，由人判（`skills/dev-flow/SKILL.md:48`）；接著 G1 走「人 → fresh agent → owner 自審」鏈（`SKILL.md:82-90`） | 沒有人判「夠清楚了嗎」的機器版 |
| 只有 Stage 3 可選擇給人看 | Demo verdict 是全 repo唯一「無 agent 例外」的判定（`hooks/_stage3_impl.py:263-276`）；觸發判定 0 命中或 Owner Call 明示跳過就不用 Demo | 已經是選配，只缺「要不要建議人看」的推薦 |
| 真的不清楚的，前面就定義掉 | dev-talk 蘇格拉底式一次一問，但「問到什麼程度算夠」沒有量化 | 需要一個 clarity 分數 |
| 執行完自動 e2e | dev-flow 自己沒有 e2e；`_templates/7-review.md:54,240` 只是給採用專案掛 e2e spec 的引用格 | e2e 要變成 Verification Profile 的一個正式 layer |
| 驗證結果交 jev 判 | Ship 的證據鏈已齊：回歸、Final Fresh Run、Evidence Gauntlet E1–E13、雙軸審、Walkthrough；最後 verdict 仍由 reviewer 鏈簽（人優先） | 缺的是「證據齊了之後，誰決定要不要人」 |
| 最後才給人回饋 | G3 是預設人類停點（`SKILL.md:8`） | 人從「擋門」變「事後回饋」，而且回饋要記帳供校準 |
| 後面不太需要 human in loop | 沒有任何機制量測「機器判的跟人判的差多少」 | 要有 ledger 才能逐 gate 放手 |

## 3. jev 是什麼（只講接入需要知道的）

| 項目 | 事實 | 來源 |
|---|---|---|
| 形態 | 純雲端 API，閉權重，不能自架；early access（2026-09-15 上線），非 GA | https://typesafe.ai/blog/introducing-system-one-models-and-jev ；https://jevaiguide.com/faq/is-jev-open-source/ |
| Endpoint | `POST https://api.typesafe.ai/v1/systemone`，`Authorization: Bearer $TYPESAFE_API_KEY` | https://docs.typesafe.ai/api |
| 輸入 | `state`（字串、JSON 物件或字串陣列，純文字）+ `questions`（多題並行，加題幾乎不加延遲）。**32k tokens 上限只見於 OpenRouter／Cloudflare／Requesty 的二手清單，官方頁未確認，P0 要實測** | https://docs.typesafe.ai/concepts/system-one （型別）；https://developers.cloudflare.com/ai/models/typesafe/jev/ （上限，二手） |
| 三種題型 | `noul`：是非，回 `noul` 0–1（無 confidence）；`choice`：`criteria` 為「選項→說明」map，回 `choice`+`probabilities`+`confidence`；`score`：`criteria` 為 2–10 級有序陣列，回 `score`+`legend`+`probabilities`+`confidence` | https://docs.typesafe.ai/primitives/noul ；…/primitives/choice ；…/primitives/score |
| 模型名 | `jev-1.13.0`（現行）、`jev-latest`（別名） | https://docs.typesafe.ai/models |
| 價格 | 輸入 $0.042 / M tokens，輸出免費；一個 20k 的證據包約 $0.0008 | 同 blog；獨立佐證 https://requesty.ai/blog/typesafe-jev-explained |
| 官方整合 | Python／JS SDK（讀 `TYPESAFE_API_KEY`）；Claude Code skill `typesafe-ai/skills`（雙用途：設計輔助 + runtime 呼叫 API／SDK）；**沒有官方 MCP** | https://github.com/typesafe-ai ；https://github.com/typesafe-ai/skills |
| 官方 guardrails 模式 | `guard()`：多個 `noul` 危害題 + 一個共用 `score` 嚴重度題；`route()` 門檻設在 noul／score 值上（review 0.35、action 0.70／0.85、block 2.0），**不是設在 confidence 上** | https://docs.typesafe.ai/cookbooks/llm_guardrails |
| 最重要的警語 | 「Calibration is measured across groups of predictions; it does not guarantee that an individual answer is correct.」 | https://docs.typesafe.ai/concepts/system-one |

那句警語決定了整個設計：**jev 的機率只在「一群決定」上可信，單一決定可能錯。** 所以每個接入點都要有門檻、有記帳、有人事後回饋，而且先影子跑再放行。

## 4. 接入點 J1–J6

原則三條：
1. **jev 不產證據，只讀證據。** 證據仍由測試、reviewer、Gauntlet 產。
2. **jev 決定的是路由**：AUTO（agent 簽）／HUMAN（現在的行為）／REWORK。
3. **人的裁決權不動的地方**：Owner Calls（驗證五律 #4 HITL 不可代答，`docs/dev/readme-contract-extract.md:47`）、Demo verdict attestation、不可逆改動的 Quiz gate。jev 只能把這些排在「該不該現在問人」的前面，不能代答。

| J | 站／對應現有決策點 | 餵給 jev 的 state（控制在上限內，上限 P0 實測；摘要不塞逐字稿） | 題目 | 結果怎麼用 | 拿掉的人工步驟 |
|---|---|---|---|---|---|
| **J1** Intake 出口 | `/dev-talk` 結束、`/dev-flow` 路由進 Decide 之前 | `1-discussion.md` 的 Real-world Context 節、Open Questions 三態、Interview Log 的結論欄（不含逐字稿，守資訊圍欄 `SKILL.md:56-62`） | `noul ready`：不再問作者任何問題就能寫出 4-spec？；`score ambiguity` 0–3；`choice next` {START_DECIDE, ASK_MORE, NEEDS_OWNER_DECISION} | ASK_MORE → dev-talk 續問（`probabilities` 指出最弱的是哪一維）；START_DECIDE ≥ θ → 直接進 Decide；NEEDS_OWNER_DECISION → 只問人那一題 | 人判「這樣夠了嗎」 |
| **J2** Decide G1 | 決策點 #2 G1 verdict、#3 Owner Calls | `2-decision.md` 方案比較表 + Owner Calls 清單 + fresh reviewer findings | `choice g1_route` {AUTO_PASS, HUMAN_REVIEW, REQUEST_CHANGES}；每條 OC 一題 `noul owner_only`：這是只有 owner 能做的價值判斷嗎？ | AUTO_PASS ≥ θ → reviewer agent 寫 `verdict: PASS`，`reviewers` 欄記 `jev-routed/agent`，人收事後通知；否則照現在在 chat 問人。**每一條 OC 仍由人逐條裁決**（五律 #4 不可代答、G1 有未裁決 OC 不得過，`docs/dev/readme-contract-extract.md:47,81`）；`owner_only` 只拿來排序與預填建議答案，人一鍵確認或改寫 | G1 預設問人；OC 從「每條從零想」變「逐條確認」 |
| **J3** Spec G2 + Stage 3 | #4 G2 verdict、#5 Demo | `4-spec.md` R/S + Drafting Decisions + Verification Profile + reviewer findings；`3-prototype.md` 觸發判定清單 | `choice g2_route` 同 J2；`noul demo_worth_it`：人親手 Demo 會改變 spec 嗎？ | 同 J2。Demo：**維持人類專屬**（機械層拒收 agent 填的 ACCEPTED，不改）；`demo_worth_it` 只當「建議你看一下」的推薦；人沒要求且有 Owner Call skip → 照現行跳過 | 無新增；正好對上「Stage 3 選擇性給人看」 |
| **J4** Build 每 T + 升階 | #7 T review、#8 失敗分類、#9 adviser | T 定義 + Verify exit code 與輸出 tail + `review_verdict` + findings | `noul consistent`：reviewer 的判定跟原始 Verify 證據一致嗎？；`choice failure_category` {SPEC, ENV, IMPL, UNKNOWN}（**沿用 schema enum**，`observability/schema/agent-event.schema.json:32-50`）；`choice escalate_to` {RETRY_SAME_TIER, ESCALATE_TIER, ADVISER_NOW, STOP_L2} | SPEC ≥ θ → 直接進 adviser／L2，不燒完 sonnet×2+opus×1；ENV → 重跑不計；`consistent` 低 → 重審一次 | 這裡本來就沒有人；省的是升階梯的錢跟時間，加的是對 reviewer 自洽的便宜複核 |
| **J5** Ship G3 | #10 G3 verdict；證據來自 #5 回歸、#6 Final Fresh Run、#7 Gauntlet、#8 雙軸審、#9 Walkthrough，加採用專案的 e2e layer | `7-review.md` coverage matrix 摘要 + Gauntlet E1–E13 結果 + Final Fresh Run 逐 layer 表 + e2e 摘要 + 雙軸審各軸 verdict | `choice g3_route` {AUTO_SHIP, HUMAN_REVIEW, REQUEST_CHANGES}；`score risk` 0–3（cosmetic／contained／touches persisted data or external calls／irreversible or security）；`noul evidence_complete` | AUTO_SHIP ≥ θ **且** risk ≤ 1 → agent 簽 PASS，人收「事後回饋」請求；risk ≥ 2 → 一律 HUMAN_REVIEW（Quiz gate 不動，`SKILL.md:77`） | Ship 預設人類停點，限低風險出貨 |
| **J6** 回饋 ledger | 新增 | 每次 jev 呼叫：gate、題目、機率、採取的路由、模型版本、事後人類回饋（同意／推翻） | — | `.dev-flow/jev/ledger.jsonl`（進 git 的長期記憶）+ observability 事件 `agent_role: verifier`、`model: jev-1.13.0`（`verifier` 目前沒有對應 prompt，剛好留給機械腳本類，見盤點）。門檻只從 ledger 調，不憑感覺 | 讓「後面不太需要人」變成可量測的路徑 |

### 4.1 e2e 怎麼變成正式的一層

dev-flow 本身沒有 e2e，也不該有（它是方法論 repo）。做法是把 e2e 升格成 4-spec Verification Profile 的一個 **Required layer**：採用專案在 spec 裡宣告 `e2e` layer 的單一入口指令，Final Fresh Run（綁 HEAD SHA，`skills/dev-run/SKILL.md:377-397`）跑它，Evidence Gauntlet 驗它有沒有跑，摘要餵進 J5 的 state。這正是 `_templates/7-review.md:54,240` 那個引用格本來想做的事。

## 5. 題目設計的規矩

- **門檻設在 noul／score 值，不設在 confidence。** 照官方 guardrails cookbook；官方對 `confidence` 沒給任何數字門檻。
- **選項用 dev-flow 既有詞彙**：failure_category 沿用 SPEC/ENV/IMPL/UNKNOWN；gate 路由三選一對映 frontmatter 的 PASS/REQUEST_CHANGES/HOLD（AUTO→PASS、REQUEST_CHANGES→REQUEST_CHANGES、HUMAN→HOLD 待人）。不要再發明第五套 verdict 詞彙（盤點已列出四套互不共用的 enum）。
- **每題的 `criteria` 說明寫成可驗證的句子**，不寫「好／不好」。例如 risk 的四級寫成「改了什麼類型的東西」，不是「低／中／高」。
- **state 是證據包，不是全文**：Verify 只帶 exit code 與最後 N 行；findings 帶 reviewer 的原文條列；不帶 diff 全文；不帶 1-discussion 逐字稿（J1 只讀節，不讀對話）。證據包組裝是真正的工程量。
- **起始門檻**：AUTO 路由 0.90、HUMAN 路由 0.35 以下、其餘 REWORK；risk block 在 2.0。這幾個數字是起點，只准由 J6 ledger 修改。

## 6. 管線：一個 env、一支 script、一個 ledger

```
TYPESAFE_API_KEY   未設 → 全部 J 點 no-op，行為 = 現況
DEVFLOW_JEV=shadow → 呼叫、記帳、不改路由（預設）
DEVFLOW_JEV=live   → 依 ledger 已放行的 gate 改路由
DEVFLOW_JEV=off    → 明確關閉
```

- `scripts/devflow-jev.py`（stdlib only：urllib + json，過 `scripts/check-py-floor.sh` 的版本地板）
  - `pack --gate J5 --slug <slug>` → 從該 slug 的檔案組證據包，砍到上限以內（上限 P0 實測後定值），輸出 JSON。
  - `ask --gate J5 --state-file <packet.json>` → 讀 `hooks/jev-questions.json` 的預設題組（跟 `hooks/prompt-registry.json` 同一種登記方式）→ POST → 印答案 → append ledger → 寫 observability 事件。
  - `feedback --id <ledger-id> --human agree|overturn --note "..."` → 人事後回饋落 ledger。
  - `report --gate J5` → 該 gate 的同意率、樣本數、是否達放行門檻。
- 呼叫位置：`skills/dev-flow/SKILL.md` 的站間路由、`skills/dev-run/SKILL.md` 的 W 步驟，各加一行「若 `TYPESAFE_API_KEY` 有設 → 跑 `devflow-jev.py ask --gate Jn`」。先不掛 hook，跟記憶讀寫一樣由 skill 文字驅動；等 live 模式穩了再考慮 PostToolUse hook 強制。注意：schema 對 `writer: hook` 的事件禁寫 `agent_role`／`prompt`／`model`（`observability/schema/agent-event.schema.json:10`、`observability/event_validate.py:551`），真要掛 hook 那天，J6 事件要改由 skill 端寫，或先改 schema。
- 分發：`docs/dev/ship-manifest.json` 加一列，採用專案的 `docs/dev/tools/` 就會拿到這支 script。
- 後端可換：`DEVFLOW_JEV_BACKEND=typesafe|adapter`。`typesafe-ai/system-one-adapter-python` 提供同介面、LLM 後端的替代品（https://github.com/typesafe-ai/system-one-adapter-python ），萬一 early access 收掉或漲價，題組不用重寫。

## 7. 哪些是純加法，哪一處要改契約

| 改動 | 性質 | 為什麼 |
|---|---|---|
| `devflow-jev.py`、`jev-questions.json`、ledger、observability 事件 | 純加法 | 沒設 key 就不存在 |
| J1 clarity、J3 demo 推薦、J4 升階路由 | 純加法 | 只改 skill 文字裡的「下一步怎麼選」，不動 gate 語意 |
| J2 的 OC 排序與預填 | 純加法 | 人仍逐條裁決，只改呈現順序與預填建議；未裁決 OC 照舊不得過 G1 |
| e2e 升格 Required layer | 模板加法 | 4-spec／7-review 模板加一列，舊票 dual-read |
| **J2／J5 的 AUTO 路由（agent 簽 gate、人事後回饋）** | **L2，改契約** | 契約檔 §7、指南 `#gates`、`SKILL.md:82-90` 三處都寫「適格人類 reviewer → fresh-context reviewer Agent → owner 自審」，且 `hooks/_gate_consistency_impl.py:223-254` 機械驗這個順序沒被否定。AUTO 路由等於把「人優先」改成「人只在 jev 說 HUMAN、risk ≥ 2、或人主動要求時進場」。這一條要走 dev-flow 自己的 Decide 站，開 ADR，三處同步改，hook 的 regex 一起改 |

## 8. 分階段

| 階段 | 做什麼 | 放行條件 |
|---|---|---|
| P0（本分支） | 本草稿 + 用 rick 的 key 跑 §10 煙霧測試，確認回應形狀 | curl 回 200 且三種題型都回對欄位 |
| P1 | `devflow-jev.py` + 題組 + ledger + observability；J4、J5 影子模式；e2e layer 模板 | 影子模式跑完 ≥ 3 個 feature，ledger 有資料 |
| P2 | J1 clarity 路由、J3 demo 推薦（純加法，直接 live） | dev-talk 出口實測「ASK_MORE 指出的維度」人覺得合理 |
| P3 | 契約改動：J2／J5 AUTO 路由 live，逐 gate 放行 | 該 gate 在 ledger 上「jev 判 AUTO 且人事後同意」≥ 90%、樣本 ≥ 20（數字待議） |

## 9. supermemory：評估與結論

| 項目 | 事實 | 來源 |
|---|---|---|
| 形態 | MIT monorepo；雲端 SaaS + 免費自架 Local binary（v0.0.8，免 DB，內嵌 ONNX embedding） | https://github.com/supermemoryai/supermemory ；https://supermemory.ai/docs/self-hosting/overview |
| 整合 | 官方 MCP（8 個工具，OAuth）**只接雲端**；自架要改走 `SUPERMEMORY_API_URL` 的 coding plugins；官方 CLI 與 Claude Code skill | https://supermemory.ai/docs/supermemory-mcp/mcp ；https://github.com/supermemoryai/skills |
| 儲存 | vector + FTS + graph 混合，chunks／memories／profile 三層；**沒有**「事實／決策／不變量」型別 | https://supermemory.ai/docs/concepts/how-it-works |
| 價格 | Free $5 credit／月、Pro $19、Max $100、Scale $399 | https://supermemory.ai/pricing/ |
| 成熟度 | 30.8k star、2026-09-20 仍有 push；自架版未解 bug：#1413 每 10 秒重寫整個 DB、#1336 embedding 設定被忽略、#1695 profile 填不進去 | https://api.github.com/repos/supermemoryai/supermemory ；repo issues |
| 未查證 | 資料中心位置、rate limit 數字、benchmark 獨立覆現 | — |

對照 dev-flow 現況（盤點 (b) 節）：

- dev-flow 的記憶**已經是型別化的**：`.dev-flow/decisions/DEC-*.md`、`knowledge/{intents,invariants}`、`state/implementation`、`events/`、`skills/`，全進 git，跨機器靠 git 就同步；本機 SQLite 只是可丟棄快取，裡面已有 `embeddings` 與 `retrieval_metrics` 表。supermemory 給的是「無型別的語意檢索」，正好是 dev-flow 刻意不要的形狀。
- session 開場只讀 7 段、4000 字元預算、其餘 on-demand `ask`（`memory/agentmem/context.py`）。接 supermemory 改不了這個預算，只會多一個外部依賴、多一個資料出境點（位置未查證）。
- rick 自己的鐵律 6 寫明記憶走 autoMemory + `.dev-flow/`。
- jev 的 ledger 不需要它。

**結論：不接。** 唯一值得回頭看的時機：`dev-memory.py ask` 的語意檢索不夠用、而且要跨專案共享記憶時，可以評估把 supermemory 當 `ask` 的可換後端。到時再開一張 0-draft。

## 10. 煙霧測試（P0，需要 rick 的 key）

```bash
export TYPESAFE_API_KEY=...   # 只在本機 shell 設，不進任何檔

curl -sS https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "model": "jev-latest",
  "state": {
    "task": "T3: add retry to fetchUser (max 3 attempts, 200ms backoff)",
    "verify": {"cmd": "pytest tests/test_fetch.py -q", "exit_code": 0, "tail": "3 passed in 0.41s"},
    "reviewer": {"review_verdict": "PASS", "findings": []}
  },
  "questions": {
    "consistent": {
      "type": "noul",
      "instructions": "Does the reviewer verdict agree with the raw verify evidence?"
    },
    "route": {
      "type": "choice",
      "instructions": "What should the dispatcher do next?",
      "criteria": {
        "ACCEPT": "commit this task and move to the next one",
        "REWORK": "send back to the same model tier with the findings",
        "ESCALATE": "raise the model tier",
        "STOP_L2": "the task definition itself is wrong; stop and return to G2"
      }
    },
    "risk": {
      "type": "score",
      "instructions": "How risky is merging this change?",
      "criteria": [
        "cosmetic or test-only change",
        "contained logic change with tests",
        "touches persisted data or external calls",
        "irreversible or security-relevant change"
      ]
    }
  }
}
JSON
```

預期：`answers.consistent.noul` 接近 1、`answers.route.choice == "ACCEPT"`、`answers.risk.score` 落在 1 附近，`model` 回 `jev-1.13.0`。任何一個欄位名對不上，就回頭改 §3 的表，不要硬接。

## 11. 未查證與已知風險

- early access 的 rate limit（搜尋結果說 250k tokens/s、1,200 req/min）與是否要信用卡，兩個 pricing 頁都 404，沒有一手來源。
- 速度倍數（70–500ms、40–200x）全是廠商數字，無第三方覆現。
- `jev-latest` 別名會漂；ledger 一律記回應裡的 `model` 實際版本，校準只在同版本內比較。
- 官方沒有 PR review／test triage 的 cookbook；J4／J5 的題組是我們自己設計的，P1 影子模式就是在驗它。
- 閉權重、API-only：靠 §6 的可換後端降風險，不靠祈禱。
- 「不會 hallucinate」是行銷語；官方自承單一答案可能錯。設計上已用門檻 + ledger + 人事後回饋對沖，不要在文件或 prompt 裡把 jev 寫成「可信的裁判」。

## 12. 這份草稿沒做的事

- 沒讀 `hooks/_exec_impl.py`、`hooks/devflow-lib.py`、`hooks/_obs_impl.py`、`memory/agentmem/sync.py`、`durable.py` 全文；P1 實作前要精讀這幾支決定 ledger 與 observability 事件怎麼寫。
- 沒讀 `notes/design/gate-verdict-write.md`；J2／J5 的「agent 簽 verdict」要對它。
- 沒跑煙霧測試（key 不在這個 session 的環境裡）。
