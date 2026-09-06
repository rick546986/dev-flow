# Stage 1：相關脈絡進場＋推理鏈路外顯（merged brief）

> 五份獨立審查共識 = **NARROW**。填既有 Context + Interview Log 槽。
> 審頁正本仍是 `notes/design/stage1-review-ui-contract.md`。本檔不動審頁。

## 1. Status

本檔是 **design note 正本**。後續實作另開 PR。本檔不升 plugin、不升契約、不加 hop／gate。

## 2. Problem

S1 已有 Context（已知事實）＋ Interview Log（`Q / 事實 / 推理 / 結論`），但相關脈絡常沒吃 talk-start brief：brief 當裝飾，已核事實不帶檔:行。掃頁 `build-scan-html.py` 把 Log 壓成 `#scan-log` 短 `<p>`，審的人看不到四段鏈路。

## 3. Thesis

**Stage 1 = 強制消化 talk-start brief／`ask()` 作為脈絡線索，經 current repo／spec 驗證後進 Context（可引用路徑）＋ Interview Log 四段外顯。** 跨功能複利只走已確認的 `.dev-flow` 語意，不傾倒他 slug 的 1–7。Stage 2 的 Approaches／Decision／OC／ADR 不進本 hop。

核心原則：**signal ≠ evidence；memory ≠ current fact。** 記得的東西與目前重新驗證為真的東西必須分開。

## 4. Do（實作時）

- N1／S1 **必須消化** talk-start brief（不得當裝飾）。
- Context：只收 current repo／spec 已驗證事實 + `docs/specs` + `檔:行`。可用 brief 的 `repo_signals`、`known_facts`、`known_knowledge` 當線索；讀正文仍守白名單。
- Interview Log：`Q / 事實 / 推理 / 結論` 四段語意。事實欄引用 Context 路徑。高影響可 ⚠️。
- 掃頁 `#scan-log` 四欄結構渲染；窄 viewport 可改為四段堆疊。S10 仍六件。
- 跨 feat：只經 `.dev-flow` 已確認語意 + `ask()` 作為 semantic intake；decision 固化留給 Stage 2／人確認後。
- 每次 Stage 1 rerun 都重新驗證引用是否仍對應 current working tree；stale／missing reference 不算 verified fact。

## 5. Don't

- 傾倒其他 slug 的 1–7 全文、HISTORY 整本、raw CoT、transcript。
- 把 `repo_signals`、memory `known_facts`／`known_knowledge` 未經 current repo／spec 驗證就直接標成 current fact。
- Stage 1 做 Decision／OC／ADR／把 Log 升成契約。
- 新 hop／新 gate／審頁解鎖／第 7 掃頁格。
- 把 Interview Log 整包 promote 進 `.dev-flow`。
- 只改 html 不改 md。
- 將 repository／memory／使用者內容以 raw HTML 注入 `#scan-log`。

## 6. Md 形狀

填既有槽，不新增章節。

**Context（已知事實）**

- 每條 current fact 必須先經 current repo／spec 驗證，並帶出處：`docs/specs/<domain>.md` 與／或 `path:line`。
- brief 的 `known_facts`（`ask()` 狀態 `OK`）是 **Context candidate**，不是自動成立的 current fact；必須再次以 current repo／spec 驗證後才能寫入 Context。
- brief 的 `known_knowledge`（`ask()` 狀態 `OK`）是 **reasoning/context signal**；未經 current repo／spec 獨立驗證，不得標示為 current fact。
- `repo_signals` 只當 discovery clue：讀過、白名單內且內容驗證成立才可引用；沒讀過的路徑不進 Context。
- `NEEDS_VERIFICATION`／`CONFLICT`／`NO_RELIABLE_MATCH`／`OPEN` 不得進 Context 當 current fact。
- Stage 1 rerun 時必須重新驗證 `path:line`／spec 引用；路徑不存在、行號已失效或內容不再支持斷言時，該事實降回待驗證。

### Evidence promotion rules

Stage 1 MUST distinguish signals from verified facts.

- `repo_signals` are discovery clues only. They are never evidence by themselves.
- `known_facts` from `ask()` are candidates and MUST be revalidated against the current repository/spec before entering Context as verified facts.
- `known_knowledge` is reasoning/context input only and MUST NOT be labeled as a current fact without independent current-repo/spec verification.
- `OPEN` / `NEEDS_VERIFICATION` / `CONFLICT` / `NO_RELIABLE_MATCH` states MAY appear in Interview Log but MUST NOT enter Context as current facts or be promoted into semantic memory.

Cross-feature semantic intake is limited to the current talk-start brief and `dev-memory.py ask()`. Verification MAY read whitelisted current-repository files/specs referenced by those signals. 這個限制約束的是 **semantic intake 入口**，不是禁止 Stage 1 讀 current repo 做 evidence verification。

**Interview Log（推理鏈外顯）**

md 不使用單行 `|` delimiter 當 parser grammar，避免 shell pipe、TypeScript union 等內容破壞解析。建議既有槽內每條採 nested fields：

```text
- Q: 為什麼這裡需要讀取 memory？
  - 事實: talk-start 已提供 repo signal [scripts/foo.py:L31-L44]
  - 推理: signal 本身不是證據，因此仍需讀取目前 repository 驗證。
  - 結論: CONFIRMED — Stage 1 應將已驗證內容寫入 Context。
```

- 四段齊才算一條。事實欄引用 Context 已列路徑，不另造無出處斷言。
- 結論狀態至少允許：`CONFIRMED`、`NEEDS_VERIFICATION`、`OPEN`。不得為了填滿四段硬下結論。
- `NEEDS_VERIFICATION`／`OPEN` 可留在 Interview Log，但不得進 Context current fact，也不得 promote 成 semantic memory。
- 高影響（難逆轉／意外／真權衡）標 ⚠️。推理是可核對的短句，不是 raw CoT。

## 7. Html 形狀（只動掃頁 `#scan-log`）

S10 六件不變：摘要卡／現況圖／人表／題目／驗收表／問答摘要。

`#scan-log` 從壓扁 `<p>` 改成四個 semantic fields（`Q / 事實 / 推理 / 結論`），與 md 同形。不是新格、不是第七件。

- wide viewport：可呈現 `Q | 事實 | 推理 | 結論` 四欄。
- narrow viewport：允許依序堆疊 `Q → 事實 → 推理 → 結論`，不得因四欄要求犧牲可讀性。
- 所有 Q／事實／推理／結論／source reference 在 render 前 MUST HTML-escape；repository、memory、使用者輸入不得 raw HTML injection。
- Constraints／詞條仍不佔第一屏。

**不動**：`scripts/build-stage1-html.py`、審頁 `#scan-sum`／`#scan-now`／`#scan-people`、html-shell、gate-twin STAGES。

## 8. 記憶規則

- S1 的跨功能 semantic intake 只吃本場 talk-start brief + `dev-memory.py ask()`；但可讀白名單 current repo／spec 做 verification。推理留在本 slug 的 Interview Log。
- 跨 feat 複利：只把 `.dev-flow` **已確認**語意當 signal／candidate；即使 `ask()` 狀態 `OK`，要成為 current fact 仍需 current repo／spec 驗證。
- `NEEDS_VERIFICATION`／`CONFLICT`／`NO_RELIABLE_MATCH` 不當現況；`OPEN` 亦同。
- **不讀** 其他 `docs/dev/<slug>/`。不把 Log 整包 promote 進 `.dev-flow`。transcript 只住本機。
- 語意候選仍走 propose → 人 confirm → end 才固化。Stage 1 不代 Stage 2 做 decision 固化。

## 9. 契約／版本

零 bump。不加 G0。不放寬 `docs/dev/**` 白名單。不加 hop／gate。本檔不是契約。

## 10. Later PR success criteria

後續實作 PR 過關＝下列全真（本檔本身不算過關）：

1. Context 在 md 有 current repo／spec 驗證後的 `檔:行`／specs 引用；memory signal 不會未驗證直接成 current fact。
2. Interview Log 事實欄用**同一批**引用，並有 `Q / 事實 / 推理 / 結論` 四段語意。
3. Interview Log parser 不依賴裸 `|` split；shell pipe／TypeScript union 等內容不會破壞解析。
4. `NEEDS_VERIFICATION`／`OPEN` 可留 Log，但不進 Context current fact／semantic memory。
5. 掃頁 `#scan-log` wide viewport 渲染四欄鏈路；narrow viewport 可讀地四段堆疊，不壓成短段落。
6. `#scan-log` 所有外部內容 HTML-escaped，不允許 raw HTML injection。
7. Stage 1 rerun 會重新驗證 stale／missing source reference。
8. S10 仍六件。
9. 審頁不變。
10. 不升 plugin／契約。

## 11. Five-review table

| # | 焦點 | VERDICT | ONE_LINE |
|---|---|---|---|
| A | intake | NARROW | 強制消化 talk-start brief；不傾倒他 slug；Stage 2 決策鏈不進 S1 hop |
| B | loci | NARROW | 槽位＝Context + Interview Log；Approaches／Decision 留 Stage 2 |
| C | memory | NARROW | S1 semantic intake 只 brief + `ask()`；memory 是 signal，current fact 需 repo/spec 再驗證 |
| D | adversarial | NARROW | 不新 section／gate／hop；不 raw CoT；不只改 html；填既有槽 |
| E | delivery | INCLUDE | 後續 PR 必帶：evidence promotion、四段 parser、unresolved state、HTML escape、stale ref revalidation；S10／審頁／版本不動 |
