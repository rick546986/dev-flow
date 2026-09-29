---
title: jev-gate W11 — Jev 記憶重排序 MR（P2-11）：mr-rerank + mr-eval 離線評測
slug: jev-gate
status: W11 第一刀：MR 重排本體（確定性、必留、fallback）+ 離線評測指令（Recall@5／MRR／必留保留率，C5 三條）；已併入 main（#420），main #421 起另有 `gates: MR:` + `mr-gate`（只到 shadow、enforced 恆 false）；不接進 dev-memory ask、不寫記憶、不寫 verdict
date: 2026-09-27
base: research/jev-supermemory b519ba9（W10 G2 誤放行只記錄）
---

# W11 Jev 記憶重排序 MR（研究分支、離線）

> **一句話**：`memory/dev-memory.py ask --json --limit 20` 照舊檢索；`devflow-jev.py mr-rerank` 接在它**後面**，
> 拿原檢索的前 20 筆候選重排、回前 5 筆。被標成必留的記憶只要在前 20 筆裡，就一定在前 5 筆裡。
> 預設零網路：雙閘門沒開、或 Jev 打分失敗 → 照原本的順序回前 5 筆，不 crash。
> `devflow-jev.py mr-eval --fixture …` 用一組有標準答案的查詢，比「原本順序的前 5 筆」與「MR 的前 5 筆」。
> **作者 ≠ 審查者**：本檔是實作者的落檔，不宣稱任何 reviewer PASS。fixture 的分數是 synthetic，
> fixture 通過 ≠ MR 可以上線（見 §4.4）。

## 1. 位置：接在原檢索後面，不換掉它

```
dev-memory.py ask "<問題>" --json --limit 20      ← 原檢索（query.py → retrieval.py 多路召回 + RRF），一行不改
        │  envelope：{query, retrieval_status, results[...]}
        ▼
devflow-jev.py mr-rerank --answer <envelope.json | ->
        │  取 results 前 20 筆（C6）→ 重排 → 前 5 筆（C6）
        ▼
{top, results, original_top, mandatory, mode, fallback_reason, retrieval_status(原樣)}
```

- **沒有接線**：`dev-memory.py ask`、`query.py`、`retrieval.py`、hooks 都沒改；MR 只是一支獨立子命令。
  （main #421 起 SKILL、契約 §8、guide 多了 `mr-gate` 的用法說明，但 MR 仍沒有接進任何檢索或 stage。）
  `wired_into` 恆 `null`、`gate_effect` 恆 `none`。
- **不寫記憶**：不呼叫 `remember`／`fact`／`know`／durable append；`writes_memory` 恆 `false`。
  唯一會寫的是 Jev 真的出境時的 budget／breaker 狀態檔（`.devflow/jev/state/`，gitignored，與其他 gate 共用 A2 daily cap）。
- **不改 `retrieval_status`**：原樣帶出；`NO_RELIABLE_MATCH` 不會被 MR 變成 OK（results 空 → top 空）。

## 2. 輸入輸出

### 2.1 輸入（`--answer`，`-` = stdin）

三種形狀都收：

| 形狀 | 取用 |
|---|---|
| `dev-memory.py ask --json` 的 envelope | `query`、`retrieval_status`、`results` |
| `{query, candidates}` | `candidates` |
| 純 list | 當 candidates |

candidates 必須已是**原檢索的順序**；MR 只看前 `MR_POOL_SIZE = 20` 筆。第 21 筆以後不進候選池，也不算必留。

每筆候選要有穩定 id（依序取第一個有值的）：`id`（fixture）→ `item_uid`（retrieval）→ `path:<path>`（knowledge_index）→
`knowledge:<key>`（knowledge）→ `fact:<title>`（CURRENT fast path）。都沒有 → exit 2。id 重複 → exit 2。

`--scores <json>`（選填）：`{candidate_id: 數字}`，stored scores 重放，**零網路**（重現用）。等級規則與送 Jev **完全相同**（§2.4）：只是把打分來源從 Jev 換成檔案 —— off → 原順序、不記錄；shadow → 只記進 `shadow_top`，回傳仍是原順序。要離線比「原順序 vs MR 排序」請用 `mr-eval`（§4，它直接評 MR 排序，不看等級）。

### 2.2 輸出（schema `devflow-jev-mr/1`）

| 欄 | 意思 |
|---|---|
| `top` / `results` | 回傳的前 5 筆 id／原始列（列內容原封不動）。等級 < live（今天一律如此）= 原順序 fallback |
| `original_top` | 原檢索順序的前 5 筆 id（對照用） |
| `mode` | `scored`（採用了分數；只有 live，今天走不到）／`fallback`（照原順序） |
| `fallback_reason` | `no_api_key`、`no_project_optin`、`mode=off`、`privacy_blocked`、`jev:<noop 原因>`、`scores_invalid:…`、`nothing_to_score`、`shadow_mode`（打分成功但只記錄） |
| `shadow_mode` | `recorded_only`（shadow 打分成功、只記錄）／`null`（沒打分、打分失敗或已採用） |
| `shadow_top` / `shadow_scores` | shadow 時 MR 會排出的前 5 筆 id 與各非必留候選的分數（必留照樣釘最前）；其餘情況 `null` |
| `scorer` | `stored_scores`／`jev`／`none` |
| `status` | `ok`／`mandatory_overflow`（§3.3） |
| `mandatory` | `in_pool`、`kept`、`dropped`、`reasons`（每筆必留的理由） |
| `retrieval_status` | 原 envelope 的值，原樣 |
| `network` | 這次有沒有真的出境 |
| `mr_policy` | `mr+<指紋>`：C5／C6 常數 + 題目刻度的 hash；改任一個指紋就變 |

exit code：`0` = ok（含 fallback——Jev 從不阻塞）／`1` = `mandatory_overflow`／`2` = 輸入錯（fail-loud）。

### 2.3 排序規則（確定性）

同樣的輸入一定得到同樣的輸出（dict 插入順序也不影響）。

- **有分數（scored）**：必留項**不送打分**、依原排名釘在最前面；其餘依分數排，tie-break =
  **分數高 → 原排名前 → id 字典序**。前 5 = 必留（最多 5 筆）+ 分數最高的非必留補滿。
- **沒分數（fallback）**：**照原本的順序**回前 5 筆。唯一例外：必留項排在第 5 名之後時，擠掉排最後的非必留項；
  輸出仍按原排名排。沒有這種情形時，fallback 的前 5 筆 = 原檢索前 5 筆，逐列相同。
- **分數壞掉**：任一非必留候選缺分數、或分數不是有限數字（NaN／inf／bool／字串）→ **整批 fallback**
  （`scores_invalid:missing=…`／`non_numeric=…`），不部分採用、不 crash。

### 2.4 Jev 打分（選用，預設不出境）

- **雙閘門沿用既有兩個輸入**：`TYPESAFE_API_KEY` 有值 **且** `.dev-flow/jev.yaml` 存在
  （`gate.has_api_key` + `gate.load_optin`）。沒寫 `gates: MR:` → 原行為：`mode: off` → off；`shadow`／`live` → `shadow`。
  **（main #421 起）** `gate.parse_optin` 認得 `gates: MR:`（格式見 §4.7）：寫了就用 min(mode, gates.MR.level)，
  live 仍 cap 成 shadow（`gate.MR_LIVE_RATIFIED = False`）；`gates.MR: off` → 不打分、照原順序。
  所以 **MR 要生效，`mode` 至少要 `shadow`**：`mode: off` 時 `MR: shadow` 也是 off（照原順序、零網路；`mr-gate` 回 `off`、exit 0）。
- **shadow = 真 shadow，不改回傳順序**（owner 2026-09-29）：MR 生效等級是 `shadow` 且有 key 時，`mr-rerank` 仍送 Jev 打分，
  但 `top`／`results` 一律是原順序 fallback（必留規則照舊），`mode: fallback`、`fallback_reason: shadow_mode`、
  `shadow_mode: recorded_only`；Jev 排出的順序只記在 `shadow_top`（ids）與 `shadow_scores`。打分失敗（Jev noop、
  `scores_invalid`）照舊 fallback，不記 shadow。**live 才採用分數**（`policy.mr_rerank_at_level(..., apply_live=gate.MR_LIVE_RATIFIED)`）；
  `MR_LIVE_RATIFIED = False`、live 已 cap 成 shadow，所以今天沒有任何路徑會把 Jev 分數套到回傳順序上。
  （#423 當時照舊行為記的「shadow 會照 Jev 分數重排」已由本條取代。）
  yaml 壞掉照 gate.py 的規矩 fail-loud（exit 2），不當成 off。
- **只經 `http_transport`**：runtime 延遲 import，off 路徑連 urllib 都不載入（`test-devflow-jev.sh` ① 照舊只放行
  `http_transport.py`）。一次 request、每筆非必留候選一題 Score（`mr_c01`…）：0 unrelated／1 topical／2 partial／3 direct；
  候選分數 = Σ level × p（同一份 response 永遠同一個數）。
- **去識別**：送出的只有 `query` 與每筆的 `item_type` + 標題／內文前 280 字；不送 id／uid／path／evidence。
  整包先過 `packet.privacy_scan`（絕對路徑、secret、PHI）→ 命中就**不送**，`fallback_reason=privacy_blocked`。
- **失敗一律 fallback**：deadline（`policy.J1_DEADLINE_S` = 2s，`--deadline` 只能收緊）、transport 錯誤、
  回應 schema 錯、budget 用完、breaker open（key `MR`）、建 transport 例外 → `jev:<原因>`，照原順序回前 5，exit 0。
  budget 照 P1-F5 規則扣（每次出境一個 attempt；未知用量不退款）。

## 3. 必留規則

### 3.1 現有資料怎麼標

agentmem 現在**沒有**「必留」欄位。roadmap P2-11／v5 §6 列了不可移除的類別（開場必讀 context、current truth、
invariants、conflicts、exact hits），其中會出現在 `ask` results 裡的四類，可以從既有欄位推出來。

### 3.2 本 PR 定義的欄位與推導

候選列上的 **`mandatory: true`**（bool；其他型別 → exit 2）= 明確標必留。另外四類從既有欄位推：

| 理由 | 條件（既有欄位） |
|---|---|
| `explicit` | `mandatory: true`（本 PR 新定義） |
| `current_truth` | `fast_path: true`（CURRENT fast path） |
| `invariant` | `item_type: knowledge` 且 `kind: invariant` |
| `conflict` | `status: CONFLICT` |
| `exact_hit` | retrieval `channels` 含 `exact_symbol` |

任一條成立就是必留。`mandatory: false` 不會蓋掉推導出來的理由。context.py 開場必讀段落本來就不在 ask results 裡，
MR 碰不到它，自然不會移除它。

### 3.3 保證與溢出

- 必留項只要在前 20 筆候選裡，就一定在輸出的前 5 筆裡，不管分數多低（它根本不送打分）。scored 與 fallback 都一樣，`shadow_top` 也一樣。
- **必留 > 5 筆**：前 5 筆放原排名最前的 5 筆必留，其餘列在 `mandatory.dropped`，`status=mandatory_overflow`，
  CLI **exit 1**。不默默丟掉。評測裡這會讓必留保留率 < 100%，那一組就不通過。
- 必留剛好 5 筆 → 前 5 全是必留，`status=ok`。

## 4. 離線評測：`mr-eval`

### 4.1 用法

```
python3 scripts/devflow-jev.py mr-eval --fixture scripts/fixtures/devflow-jev/mr-eval-pass.json
```

零網路、不寫檔。exit：`0` = 通過／`1` = 不通過或資料不足／`2` = fixture 形狀錯。
（`mr-eval` 的資料不足也是 exit 1；要把資料不足跟不通過分開，用 `mr-gate`：資料不足 exit 3，見 §4.7。）

### 4.2 fixture 格式（schema `devflow-jev-mr-eval/1`）

```json
{"schema": "devflow-jev-mr-eval/1", "name": "…", "score_source": "synthetic | stored_jev",
 "queries": [{"id": "q01", "query": "…",
              "candidates": [{"id": "q01-m01", "title": "…", "mandatory": true}, "…原檢索順序…"],
              "relevant": ["q01-m03"],
              "scores": {"q01-m01": 2.8, "…": 0}}]}
```

- `relevant`：標準答案（非空、不重複；可以包含不在候選池的 id —— 那代表原檢索就漏了，recall 分母照算）。
- `scores`：這條查詢的 stored scores；省略 → MR 走 fallback（= 原順序）。
- `score_source`：`synthetic`（手工設計）或 `stored_jev`（Jev 真回應存下來的分數）。報表照印。

**新專案的最小 fixture（手寫範例）**：從自己專案挑幾條真的會問的問題，把 `dev-memory.py ask "<問題>" --json --limit 20`
回的前幾筆 id／標題抄進 `candidates`（**保持原檢索順序**），人標 `relevant` 與 `mandatory`，分數先手給（`synthetic`）：

```json
{"schema": "devflow-jev-mr-eval/1", "name": "my-project-first-queries", "score_source": "synthetic",
 "queries": [
  {"id": "q01", "query": "合約到期提醒要提前幾天?",
   "candidates": [{"id": "m01", "title": "提醒排程的 cron 設定"},
                  {"id": "m02", "title": "到期前 30 天寄信的決策", "mandatory": true},
                  {"id": "m03", "title": "寄信模板的欄位"},
                  {"id": "m04", "title": "時區換算的坑"},
                  {"id": "m05", "title": "舊版提醒下線紀錄"},
                  {"id": "m06", "title": "提前天數改成可設定(ADR)"}],
   "relevant": ["m06", "m02"],
   "scores": {"m01": 1, "m03": 0, "m04": 0.5, "m05": 0, "m06": 3}}
 ]}
```

- 存成專案裡的檔（例如 `docs/dev/<slug>/mr-eval.json`），跑 `mr-eval --fixture <檔>`。exit 2 = 形狀錯（照錯誤訊息修）；
  只有一條查詢時一定是 `insufficient_data`（exit 1），這是**預期的**：它只證明形狀對，不是通過。
- 至少要有一筆 `mandatory` 在候選池裡，否則必留保留率無從證明、也是 `insufficient_data`。
- 查詢數補到地板以上才有 `pass`／`fail` 可看；synthetic 分數通過仍然 ≠ MR 可以上線（§4.4）。

### 4.3 指標與通過條件（C5，owner 2026-09-26 定案）

每條查詢：**Recall@5** = |relevant ∩ 前 5| ÷ |relevant|；**RR** = 1 ÷ 前 5 內第一筆 relevant 的名次（沒有 → 0）。
整組取平均（MRR = RR 平均）。**baseline = 原本順序的前 5 筆**（候選前 5，不做任何必留調整）；**MR = `mr_rerank` 的前 5 筆**。
**必留保留率** = 各查詢候選池內必留項出現在 MR 前 5 的數量合計 ÷ 必留項合計。

三個都成立才 `pass`：

| 條件 | 判定 |
|---|---|
| `recall_at_5_not_lower` | MR Recall@5 − baseline Recall@5 ≥ 0 |
| `mrr_gain_at_least_0.05` | MR MRR − baseline MRR ≥ 0.05 |
| `mandatory_retention_100pct` | 必留保留率 = 1.0 |

比較帶 1e-9 浮點容忍（差值剛好 0.05 算過）。**不管過或不過**，報表都列 baseline／MR 兩邊的 Recall@5、MRR、差值、
必留保留率，以及每條條件的 `actual`／`threshold`／`pass`，和每條查詢的明細（`per_query`）。

**資料不足**（`verdict=insufficient_data`，exit 1，不算通過）：

- 查詢數 < `min_queries`（預設 `MR_EVAL_MIN_QUERIES = 20`，**未校準的暫定值**；owner 沒給數字；可設定，見 §4.6）；或
- 整組沒有任何必留項在候選池 → 100% 保留無從證明。

數字照列，`insufficient` 欄寫原因。

**資料不足時怎麼辦**：補查詢，不要降地板。

1. 從 locked eval set（或專案真的會問的問題）再抄查詢進 fixture，直到查詢數 ≥ `min_queries`，而且至少一筆必留在候選池。
2. **不要**為了讓 `insufficient_data` 變成 `pass`／`fail` 而調低 `--min-queries`／`gates.MR.min_queries` —— 地板還沒校準（§4.6），
   調低只是換一個同樣沒根據的數字。報表的 `min_queries_source` 會照實寫 `cli`／`jev.yaml`／`default`，審的人看得到。
3. 真的補不到（專案記憶太少）→ 就維持 `insufficient_data`，照實回報；MR 本來就不擋任何東西（`enforced` 恆 false）。

### 4.4 fixture 的界線

`scripts/fixtures/devflow-jev/mr-eval-*.json` 的分數是 **synthetic**（手工設計的情境），驗的是**評測器與重排規則**，
不是 Jev 的品質。報表 `live_eligible` 恆 `false`：C5 要在 `dev-memory.py eval` 同一 locked eval set、用真的 Jev 分數成立，
而且 MR 目前不接任何 gate —— 那是之後的事（§6）。

### 4.5 內附 fixture 與實際結果

| fixture | 情境 | verdict |
|---|---|---|
| `mr-eval-pass.json` | 25 條；答案被往前拉、原前 5 看不到的答案被拉進來、必留全留、有同分 tie-break | `pass` |
| `mr-eval-neg-recall-drop.json` | MRR 大升，但兩個答案被擠掉一個 → Recall@5 −0.3 | `fail`（只有 recall 條件不過） |
| `mr-eval-neg-mrr-small.json` | 只有一條查詢從第 5 名拉到第 1 → MRR +0.04 | `fail`（只有 MRR 條件不過） |
| `mr-eval-neg-mandatory-overflow.json` | 一條查詢有 6 筆必留 → 保留率 5/6 | `fail`（只有必留條件不過） |
| `mr-eval-neg-insufficient.json` | 只有 5 條查詢，數字都過 | `insufficient_data` |

### 4.6 資料量地板 `min_queries`：可設定、未校準

- **可設定**：`mr-eval --min-queries N`、`mr-gate --min-queries N`，或 `.dev-flow/jev.yaml` 的 `gates.MR.min_queries`。
  優先序：CLI > jev.yaml > 預設 `MR_EVAL_MIN_QUERIES = 20`。必須是正整數（0、負數、小數、bool、字串 → exit 2）。
  報表帶 `min_queries`、`min_queries_source`（`cli`／`jev.yaml`／`default`）與 `min_queries_calibrated: false`。
- **20 不是校準過的數字**：W11 研究分支自訂的地板，owner 沒給值，也沒有任何統計推導。本 PR 沒有改它、也沒有定新數字。
- **之後怎麼校準**（需要真資料，現在做不到）：
  1. **資料**：`dev-memory.py eval` 同一組 locked eval set 產出的 MR fixture —— `score_source: stored_jev`（真的 Jev 分數，
     不是 synthetic）、每條查詢有人標的 `relevant` 與必留標記；最好有數個時間點／版本各一份，才看得到變異。
  2. **量變異**：對 locked set 重抽樣（例如 bootstrap，抽 n 條查詢重算 Recall@5 差值、MRR 差值、保留率與 verdict），
     看 n 由小到大時 verdict 在重抽樣之間翻轉的比例、MRR 差值區間是否穩定地落在 0.05 的同一側。
  3. **決定**：取「verdict 穩定」的最小 n 當地板。「多穩算穩」（可接受的翻轉比例、區間的信賴水準）由 **owner 裁決**，
     本 repo 不代定；裁決後在 2-decision／ADR 留紀錄，再改 `MR_EVAL_MIN_QUERIES`（會換 `mr_policy` 指紋）與範本
     `_templates/jev.yaml` 的註解，並把 `min_queries_calibrated` 的語意一起更新。
- **校準結果落在哪**（一次改齊，同一個 PR）：
  - 裁決紀錄：`docs/dev/jev-gate/` 的 2-decision 或 `docs/adr/` 新 ADR（寫資料來源、重抽樣方法、選的 n、owner 裁決）。
  - 程式：`scripts/devflow_jev/policy.py` 的 `MR_EVAL_MIN_QUERIES`，以及散發副本 `docs/dev/tools/devflow_jev/policy.py`
    （兩份必須一致，`check-ship-manifest` 會比）。
  - 文件：本節、`_templates/jev.yaml` 的 `min_queries` 註解、`devflow-jev.py` docstring 的「預設 20」。
  - 測試：`test_mr_gate.py`／`test_guards.py` 裡釘預設值的案例。
- **專案自己的 `gates.MR.min_queries`**：專案有自己的校準結果才寫；沒有就不要寫（範本裡是註解），讓它走預設、報表記 `default`。
- fixture 分數仍是 synthetic，`live_eligible` 恆 `false`；校準前後都一樣，校準只決定「幾條才算資料夠」。

### 4.7 MR gate：`gates: MR:` + `mr-gate`

設定（`.dev-flow/jev.yaml`，範本 `_templates/jev.yaml`）：

```yaml
mode: shadow
gates:
  # 簡寫
  MR: shadow
# 或
mode: shadow
gates:
  MR:
    # 必填 off|shadow|live
    level: shadow
    # 選填,正整數(見 §4.6);沒校準前不要寫,不寫 = 預設
    # min_queries: <N>
```

- **註解一律自成一行**：解析器不剝行尾 `#`。寫成 `MR: shadow  # 簡寫` 會被讀成值 `'shadow  # 簡寫'` → exit 2。
- **MR 生效要 `mode` ≥ `shadow`**：等級 = min(mode, gates.MR.level)。`mode: off` → MR 也是 off（`mr-gate` 回 `gate_result: off`、exit 0，
  `mr-rerank` 照原順序、零網路）。
- **只開 MR、J gate 全 off 的最小設定**：把 `mode` 拉到 `shadow` 會讓沒寫的 J gate 走 owner default
  （J1 live→shadow、J3 live→shadow、J5 shadow），**有 key 時就會出境**；所以要明寫 off（J2／J4 預設本來就 off）：

  ```yaml
  mode: shadow
  gates:
    J1: off
    J3: off
    J5: off
    MR: shadow
  ```

  G2R 不在 `gates:`、只看 `mode:`：`mode: shadow` 且有 key 時 `g2r` 仍會送一次 Jev，但回答只記錄、分流當作沒有 Jev（ADR 0004）。
- **關掉 MR**：寫 `MR: off`（或區塊 `level: off`）。**不要只刪掉 `MR` 那行**：沒寫 `gates.MR` 時 `mr-rerank` 退回照 `mode` 走
  （`mode: shadow` → MR shadow，有 key 就會出境打分；回傳順序不變，只多記 `shadow_top`），`mr-gate` 則 exit 2。全部關：刪 `.dev-flow/jev.yaml` 或不設 `TYPESAFE_API_KEY`。

- `MR` 不是 J1–J5：不進 `GATES`、不進 J-gate 的 `gates` dict（J1–J5 的解析與 `effective_level` 一行不變），結果在 `optin["mr"]`。
- **fail-loud**：區塊缺 `level`、未知鍵、`level` 不在 off/shadow/live、`min_queries` 不是正整數、`MR` 重複、
  鍵重複、縮排不是 4 格、tab → exit 2。
- `python3 scripts/devflow-jev.py --root . mr-gate --fixture <mr-eval fixture> [--min-queries N]`：
  - 零網路（只讀 fixture 的 stored/synthetic 分數，不建 transport，不看 key）。
  - 缺 `.dev-flow/jev.yaml`、沒寫 `gates: MR:`、格式錯 → **exit 2**（fail loud，不當成 off 或通過）。
  - 生效等級 = min(mode, gates.MR.level)，live cap 成 shadow；`off` → `gate_result: off`（不評，exit 0）。
  - 其餘照 `mr_eval` **同一判定**（§4.3）：`pass` → exit 0；`fail` → exit 1（`failed_conditions` 列出沒過的條件）；
    `insufficient_data` → **exit 3**（與 fail 分開，`insufficient` 列原因）。
  - `enforced` 恆 `false`、`live_eligible` 恆 `false`、`gate_effect: none`：MR live 未核准，devflow-check／任何 stage 都不拿它擋東西。

## 5. 測試

`scripts/devflow_jev/test_guards.py`（`W11MRRerank`、`W11MREval`，pure）與 `test_runtime.py`（`W11MRRuntime`）：
確定性（重跑、dict 順序）、tie-break、必留（最低分也在前 5、fallback 也保留、池外不算）、必留剛好 5／超過 5、
fallback（無 key、無 opt-in、mode off、transport 錯、逾時、budget 用完、建 transport 例外、privacy 命中不送、分數缺／壞）、
三個通過條件的邊界值（MRR 差值剛好 0.05 過、1/21 不過；Recall 差值 0 過、−0.025 不過；保留率 1.0 過、6/7 不過）、
資料不足（19 條 vs 20 條、0 條、無必留）、fixture 形狀錯、`NO_RELIABLE_MATCH` 不升級、接在真的
`dev-memory.py ask --json --limit 20` 之後、CLI exit code（mr-rerank 0／1／2、mr-eval 0／1／2）。
`test-devflow-jev.sh` 地板 330 → 376（研究分支當時）。main #421 另加 `test_mr_gate.py`（`gates: MR:` 解析、mr-gate exit 0／1／2／3、
範本與文件範例可解析、行尾註解 fail-loud）。

## 6. 沒動的東西／留給後面

- `GRADUATED`、`gate.J5_LIVE_RATIFIED`、`policy.J2_WINDOW_RATIFIED` 維持 `False`；`GATES` 不含 MR。
  （main #421：`gate.py` 加了 `gates: MR:` 解析與 `MR_LIVE_RATIFIED = False`，J1–J5 的雙閘門語意不變；
  `scripts/devflow_jev/test_mr_gate.py` 釘住。）
- Jev 不 review、不寫 verdict；G2R 門檻（`G2R_THRESHOLDS`）不動；hooks 不動。
  （本檔最初寫於研究分支時「契約／SKILL／guide／main 不動」；W11 已併入 main（#420），#421 起 SKILL、契約 §8、guide
  與 `_templates/jev.yaml` 多了 `mr-gate` 的用法說明 —— 只有說明，MR 沒有接進任何 stage 或檢索，`enforced` 恆 false。）
- MR 常數與題目刻度**沒進** `jev-questions*.json`，現有 J1–J5 的 `questionset_hash` 不變；MR 自己的指紋在 `mr_policy`。
- 待做：~~`gate.py` 認 `gates.MR`~~（已做，見 §4.7）；`min_queries` 校準（§4.6）；MR 題組進 manifest（新 `questionset_hash`）；
  `dev-memory.py eval` 的 locked set 產出 MR fixture（`score_source: stored_jev`）；接進 `dev-memory.py ask`（C5 在
  locked set 上成立之後才談）。
