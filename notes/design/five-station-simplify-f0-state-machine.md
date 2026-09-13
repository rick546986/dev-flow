# 五站簡化 F0 狀態機

> 配 `notes/design/five-station-simplify-brief-v3.md`(下稱 brief)。
> 本檔鎖 **coordinator 自動前進謂詞**、**rewrite cap**、**page-human latch → brief §3**。
> F0 只落設計,不寫 runtime、不改 graph、不改模板。
> Owner 已核准。與 brief 衝突以 brief 為準;本檔只把 brief §4 展成可實作的機。

## 0. 機的邊界

| 本機管 | 本機不管 |
|---|---|
| 五站預設路線上,誰可以 hop | 舊 7 in-flight slug 的 hop(那些仍走既有 `graph.yaml`) |
| 自動前進謂詞真/假 | 謂詞背後的牙怎麼寫(F1) |
| cap 用盡之後 fail-closed | cap 數字本身(已鎖,不准 F2 放寬) |
| latch 開火與熄火 | 頁長什麼樣子(既有審頁契約) |

狀態存在 slug 級(一個 feature 一個機)。不准一個 hop 私自另開第二份機。

## 1. 狀態

```
Idle
  → Intake
  → Decide
  → Spec
  → Build
  → Ship
  → Done

任何站 ──latch──→ HumanWait ──人寫判定──→ 原站(再評謂詞)
任何站 ──rewrite──→ 同站(cap 計數 +1)
cap 用盡 ──→ Escalated(等人;不得暗改 cap)
```

| 狀態 | 意思 | 誰准離開 |
|---|---|---|
| `Idle` | 尚無 `docs/dev/<slug>/` 或尚未選路線 | 新 slug 在 F3 前仍開舊 7,不進本機。F3 後進 `Intake` |
| `Intake` | 寫 / 改 `1-discussion.md` | 自動前進謂詞全真 → `Decide` |
| `Decide` | 寫 / 改 `2-decision.md` | 謂詞全真 → `Spec` |
| `Spec` | 寫 / 改 `4-spec.md`;條件式 `3-prototype.md` | 謂詞全真且 B1 若命中已熄火 → `Build` |
| `Build` | 寫 `5-tasks.md` 然後 `6-implementation-notes.md` | 謂詞全真 → `Ship` |
| `Ship` | 寫 `7-review.md` | **只有人**寫 `verdict: PASS` → `Done` |
| `HumanWait` | latch 開火,等人寫 md | 人寫合法判定且不是 REVISE / REQUEST_CHANGES / NOT_REVIEWED |
| `Escalated` | cap 用盡或 UNKNOWN 連爆 | 人明示下一手(修 brief / 放行一次 / 停) |
| `Done` | Ship `PASS` 已落盤 | 終態。Goal reopen 用盡後不得從這裡回到 Intake |

`HumanWait` 與 `Escalated` **不是站**。離開後回到開火前的那一站,重新評謂詞。

in-flight freeze(brief OC-9):slug 已有舊 7 檔 → **不建立本機**。
Coordinator 看到舊 7 標記就放手給既有 graph。

## 2. Coordinator 自動前進謂詞

評謂詞的人是 coordinator,不是執行 hop 的寫手。
**全真才 hop。一假就停在該站修。不准改問人來繞*(除非該列 latch=是,見 §4)。**

謂詞指 brief §3 表 A/B 的「自動前進」與「命中」欄。下面是機可執行的展開。
檔路徑皆相對 `docs/dev/<slug>/`。

### 2.1 `Intake` → `Decide`

全真:

1. `1-discussion.md` 存在且可解析。
2. Open Questions 全數 `已解` 或明標 `[Assumption]` / 假設(既有三態,不新發明)。
3. 有 `## Real-world Context` 節;**或** brief 承認的 legacy(該節缺失的舊檔)且標了 legacy。
4. A1 / A2 生成謂詞若為真,產檔器既有 exit 0(F0 不改產檔器;F1 才釘「沒產卻 hop」)。

假 → 停 `Intake`。不得 hop、不得進 `HumanWait`(A1/A2 latch=否)。

### 2.2 `Decide` → `Spec`

全真:

1. `2-decision.md` 存在。
2. `## Decision`(或同等置頂 Decision)非空。
3. Owner Calls / OC **全裁決**,無「待裁決」。
4. A3 自動前進謂詞真。A4(G1 twin)已產或可產; **不等** 人寫 G1 `verdict:`。

假 → 停 `Decide`。Decide 重開計入 §3.2,不是另開站。

### 2.3 `Spec` → `Build`

全真:

1. `4-spec.md` 存在。
2. 每個 S 有觀測欄;`lane:` / `Risk:` 可解析。
3. Drafting Decisions 無殘留「待裁決」。
4. 既有 `check-spec-gate.sh` 形狀綠(F1 牙接這支,F0 不改腳本)。
5. **B1 未命中**:無 Stage 3 trigger,或已落檔全未勾 + n-a 原因 → A5 不建頁,本條視為真。
6. **B1 命中**:`3-prototype.md` 在;Human verdict = `ACCEPTED` 且有人類 attestation;不是 `REVISE` / `NOT_REVIEWED`。沒有 attestation 的 `ACCEPTED` = 假(既有機械拒)。
7. B2 若命中:UI twin 已產(F2 才接產線;F0 只鎖「命中卻無 twin 不得 hop」)。
8. A6 / A7 **不等** 人寫 G2 `verdict:`。

5 與 6 互斥。Coordinator 先評 trigger,再走其中一條。
B1 命中但 attestation 未寫 → 進 `HumanWait`(§4),不是偷偷 hop。

### 2.4 `Build` → `Ship`

全真:

1. `5-tasks.md` 在;每 T 有 Covers / Files / Verify / Blocked-by。
2. `6-implementation-notes.md` 在;每 T 有獨立 review PASS(author ≠ 該 T reviewer)。
3. 本次 S 全綠;Files ⊆ 5-tasks Files 聯集。
4. A8 / A9 latch=否 → 不得因「想給人看看任務板」停。

假 → 停 `Build`。T 重做走既有 acceptance seam,計入該 T 嘗試上限(4),
**不**另吃 hop cap,除非整份 5-tasks / 6-notes 被整站重寫(那時吃 hop cap)。

### 2.5 `Ship` → `Done`

**沒有自動前進。**

1. `7-review.md` 在;G3 物質(Evidence 八點、雙軸、coverage、Exit)依既有正本。
2. md 頂欄 `verdict:` 已是人寫的 `PASS`。
3. `REQUEST_CHANGES` → 回可改的上一站(通常 `Build` 或 `Spec`),計入對應 cap。
4. `HOLD` → 留 `Ship`,不得 hop、不得當 `Done`。

Coordinator 看到「機械全綠」仍 **必須** 進 `HumanWait`(A10 latch=是)。
把機械綠寫成 `verdict: PASS` = 違 brief OC-3。

## 3. Rewrite cap

三個計數器,slug 級、只增不減(Done 之後不再動)。
F1 牙釘「超過仍 hop → 紅」。F0 只鎖數字與計法。

| Cap | 數字 | 什麼算一次 | 用盡 |
|---|---|---|---|
| **hop** | **≤ 2** | 同一 hop 節點(或同一站內同一寫檔動作)被要求重寫。第一次寫不算。第 3 次重寫拒 | `Escalated` |
| **Decide** | **≤ 1** | 離開 `Decide` 之後又回到 `Decide` 整站重開(含 Decision 翻案、OC 重裁)。Decide 站內小改、尚未 hop 出去 = 不算 | `Escalated`;不得第三次進 Decide |
| **Goal reopen** | **≤ 1** | Intake 的目標 / Success Criteria / 問題陳述被重開改寫,且該改寫發生在已經 hop 出 Intake 之後 | `Escalated`;不得第二次改 Goal |

補充:

- hop cap **按 hop 分桶**,不是全 slug 共用一個 2。Decide 站內若有多 hop,各桶各 ≤ 2。
- Decide cap 與 hop cap **同時算**。Decide 重開 1 次時,該站被重寫的 hop 仍受 hop≤2。
- Goal reopen 會連帶回到 `Intake` 再走 Decide。若 Decide 已經用過那 1 次重開,Goal reopen 造成的第二次 Decide = 用盡 Decide cap → `Escalated`(不得假裝 Goal 重開可以免 Decide cap)。
- Agent 不得把「換個模型再寫一次」寫成不計數。計數看**寫入發生**,不看模型名。
- in-flight 舊 7 **不套**這三個 cap(它們走既有 T 嘗試上限 4 與既有修迴圈)。

偽碼:

```
on_rewrite(slug, hop_id, kind):
  if route(slug) == old_7: return allow_legacy()
  if kind == "goal" and already_left(Intake):
    slug.goal_reopen += 1
    if slug.goal_reopen > 1: escalate("Goal reopen≤1")
  if kind == "decide_reenter" and slug.left_decide_once:
    slug.decide_reopen += 1
    if slug.decide_reopen > 1: escalate("Decide≤1")
  slug.hop_rewrites[hop_id] += 1
  if slug.hop_rewrites[hop_id] > 2: escalate("hop≤2")
  return allow
```

## 4. page-human latch → brief §3

Latch 的**條件表正本 = brief §3**(表 A 的「人類 latch」欄 + 表 B 的「人類 latch」欄 + 節末「唯一出口」五步)。
本檔不重抄那兩張表。F1 牙比對 brief §3,不比對本節的摘要。

本機只鎖**何時進出 `HumanWait`**:

```
on_eval(slug):
  hits = brief_§3_latch_rows_true(slug)   # A10 永遠在 Ship;B1/B2/B3/B4 條件式
  if hits == []:
    if someone_asked_human(): fail("latch 未命中卻問人")
    try_auto_advance()
    return
  enter HumanWait(pages=hits)
  # 停。把 hits 對應頁給人。不准代填。
  wait until md_verdict_written(hits) and attestation_ok(hits)
  if verdict in {REVISE, REQUEST_CHANGES, NOT_REVIEWED, HOLD}:
      stay_or_loop_rewrite()   # HOLD 留 Ship;其餘回原站,吃 cap
      return
  leave HumanWait
  re_eval_predicates()
```

硬規則:

1. Latch 列假 → coordinator **禁**問人、禁開審查 widget、禁「請 owner 看一下」。
2. Latch 列真 → **必須**進 `HumanWait`,即使機械項全綠(A10 就是這樣)。
3. 寫入路徑 = brief §3 點名的 md 頂欄 / Human verdict 行。HTML / localStorage / sidecar 不是正本。
4. B1+B2+B3 命中 = **一次** `HumanWait`,不是三次。B4 可與 A10 合併成一次 Ship 人停。
5. Agent 寫 `ACCEPTED` 或 Ship `PASS` → 機視為未寫,F1 牙紅。

## 5. 禁則(F0 就鎖,F1 牙咬)

| # | 禁 | 為什麼 |
|---|---|---|
| X1 | 自動前進 Ship | OC-3 |
| X2 | 刪 G1/G2/`ACCEPTED` 讓謂詞比較好寫 | OC-10 |
| X3 | 改 `graph.yaml` / 模板當 F0「順便」 | 本輪只設計 |
| X4 | in-flight slug 套本機 | OC-9 |
| X5 | cap 用盡後 reset 計數再 hop | 暗改 cap |
| X6 | latch 未命中卻等人 | brief §3 出口第 5 步 |
| X7 | 用 fresh-context Agent 的書面審冒充 Ship / Demo 判定 | brief §8 |
| X8 | 把 A4/A7 twin 當例行人類停點加回來 | OC-2 |

## 6. F1 要咬的最小集合

本檔不寫牙。F1 至少要能紅這些(annex 可加,不准減):

1. `Ship` 在無人 `verdict: PASS` 時被標 `Done`。
2. hop 重寫第 3 次仍繼續。
3. Decide 重開第 2 次仍繼續。
4. Goal 在離開 Intake 後重開第 2 次仍繼續。
5. B1 未命中卻要求 `ACCEPTED`。
6. B1 命中、無 attestation,卻 hop 出 `Spec`。
7. latch 未命中卻留下「請人審」紀錄。
8. 舊 7 in-flight slug 被寫入五站狀態。

F0 交卷 = 本檔 + brief 落盤。沒有腳本、沒有 fixture。
