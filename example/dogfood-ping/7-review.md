---
feature: dogfood-ping
stage: 7-review
status: approved
verdict: PASS
owner: rick-dev-flow
updated: 2026-09-11
---

# 7. 驗證 —— **G3 PASS**

> ## Reviewer 閱讀動線(**必留;給看的人,不是給寫的人**)
>
> | 步 | 讀哪節 | 這步問的唯一問題 |
> |---|---|---|
> | 1 | **Verdict** | 判定是什麼?門檻表每一格是不是都有證據? |
> | 2 | **Exit Checklist** | 還缺什麼才能出貨?哪幾項要 owner 親自動? |
> | 3 | **附錄:本輪特有** | 本輪的爭點/分歧在哪,誰對? |
> | 4 | **Known Limits** | 有沒有一條是 owner 不能接受的? |
> | 5 | **抽驗一列** | 從 Coverage Matrix / Standards Axis / Spec Axis 任挑一列,照它給的 `檔:行` 去看。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步**。Author A 證據包 → 獨立 reviewer B 建議 PASS（`7-reviewer-B-notes.md`）→ **Human G3 PASS**（owner，2026-09-11 Asia/Taipei）。

## 人讀摘要（給 owner）

- 產品：`scripts/dogfood-ping.sh` 印恰好 `dogfood-ok`+LF、exit 0；file-map 地板 194 綠。
- Stage 1–6 已過（G1 lean PASS、G2 PASS、Stage6 implementer + **獨立 Stage6 review PASS** on PR [#164](https://github.com/rick546986/dev-flow/pull/164)）。
- 落地決策：合 main → Example `example/dogfood-ping`；feat 正本仍 `docs/dev/dogfood-ping/`。
- **本檔狀態 = G3 PASS**：獨立 reviewer B 建議 PASS；**Human G3 PASS by owner 2026-09-11 (Asia/Taipei)**。准 merge #164 → main 當 Example。
- #165（Stage2 方案依據超寬表）**本 PR 不修**（仍 open）。

## ⚠️ 限制聲明（G3 密封後；作者／B／Human 角色）

| | |
|---|---|
| Author A | Stage 7 彙整／交接（曾為 PRE-REVIEW pack） |
| Reviewer B | 獨立建議 PASS（`7-reviewer-B-notes.md`）；**未**代填 Human `verdict:` |
| Human G3 | owner `rick-dev-flow` → **PASS** 2026-09-11 (Asia/Taipei) |
| 讀取順序（稽核） | `4-spec`／`5-tasks`／diff／現象表／B notes；勿只信作者主張 |

## Coverage Matrix

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1 | T-1 Verify（`test -x` + shebang `head -n1`）+ Stage6 獨立審同項；標的 `scripts/dogfood-ping.sh:1` | ✅（author 複驗；待 B 親簽） |
| S-2 | T-1 Verify `cmp` vs `printf 'dogfood-ok\n'`；stdout hex `64 6f 67 66 6f 6f 64 2d 6f 6b 0a` | ✅（author 複驗；待 B 親簽） |
| S-3 | 同趟 exit code `0` | ✅（author 複驗；待 B 親簽） |
| S-4 | `bash scripts/check-file-map.sh` → exit 0；`scanned=194`=`EXPECTED_MAPPED_FILES`；靜態釘 `scripts/test-architecture-guards.sh:2417`；指南列 `guides/guide-dev-flow.html:3961` | ✅（author 複驗；待 B 親簽） |
| 既有測試套件(回歸) | 本 feat Verify 指名入口 = `scripts/check-file-map.sh`（fast／極小 CLI；非全 repo selftest） | ✅ exit 0（見下） |

**回歸末行（author @ HEAD 當時）**：`scanned=194 exempted=13` … `✅ PASS:forward 194 支…`；`filemap_exit=0`。

## Verification Evidence

> Author pack 記錄；**Final Fresh／Gauntlet 全綠仍屬獨立 reviewer B 職權**。4-spec Verification Profile **未寫 `Required layers` 欄**（見 Known Limits #3）——`--review-file` 可能 fail-closed；B 須裁決補欄（L2）或明示降級。

- Source SHA: a940b4dfe38cffe9e3d597c88fe5e85c05aeb53b（Stage6 HEAD；本 author 開寫前；Example／本檔 commit 後 B 須重綁當下 HEAD）
- Final Fresh Run ID: n-a — author pack；留給 reviewer B
- Entry point: `scripts/dogfood-ping.sh` 然後 `bash scripts/check-file-map.sh`（對齊 4-spec Verify）
- Toolchain: system bash + repo scripts（無第三方套件）

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Real execution | `scripts/dogfood-ping.sh > /tmp/dogfood-ping.out; echo exit=$?; od -An -tx1 /tmp/dogfood-ping.out; cmp /tmp/dogfood-ping.out <(printf 'dogfood-ok\n')` | pass | exit=0; bytes `64 6f 67 66 6f 6f 64 2d 6f 6b 0a`; CMP_OK | |
| File-map regression | `bash scripts/check-file-map.sh` | pass | exit 0; scanned=194 = EXPECTED_MAPPED_FILES | |
| Full test suite | | n-a | | 4-spec Verify 未要求全 repo selftest；本 feat 回歸入口為 check-file-map |
| Mutation | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| Race/stress | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| Gauntlet `--review-file` | | unverified | | 留給 B；且 4-spec 缺 Required layers 欄（KL #3） |

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得改 host-stack-fit／#163 正本 | diff 範圍 = dogfood 腳本 + file-map／指南列／靜態釘 + feat docs／example | pass（author 目視；B 抽 `git diff origin/main...HEAD --stat`） |
| 不得引入 HTTP／npm | `scripts/dogfood-ping.sh` 僅 shebang+printf+exit | pass |
| 不得在本 PR 修 #165 | 無產器／Stage2 表寬改動 | pass |
| 不得手填假 PreToolUse | 無 hooks 行為偽造成品 | pass |
| 正式腳本不得提早塞進 Stage 4／5 | 腳本於 Stage6 commit `a940b4d` 落地 | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

（手動／Cloud Agent 實作 —— 無 dev-run ledger；本節留白。）

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

> **Author A 2026-09-11 親跑**（不採信 6-notes 貼文當唯一證據）。獨立 reviewer B 必須再跑一次。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1 | 檔存在、`test -x`、shebang 首行；`head -n1` + `bash scripts/dogfood-ping.sh` | `test -x` ✅；`head -n1` → `#!/usr/bin/env bash`（`scripts/dogfood-ping.sh:1`）；行程可啟動 | ✅ |
| S-2 | stdout 與 `printf 'dogfood-ok\n'` 逐位元組相同 | `od -An -tx1` → `64 6f 67 66 6f 6f 64 2d 6f 6b 0a`；`cmp` → CMP_OK | ✅ |
| S-3 | shell `$?` = 0 | 同趟 `exit=0` | ✅ |
| S-4 | `scripts/check-file-map.sh` exit 0、無未映射／計數不符 | exit 0；`scanned=194`；PASS forward/reverse | ✅ |

## 截圖槽

（無 UI —— CLI／地板檢查。本節無 shots。）

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1～S-4 | — | — | — | — | — | 不適用（4-spec 各 S Operational Context = 不適用；純腳本／地板） |

## Design Integrity Check(Design Boundary Contract 為 `applicable` 時逐項過;`n-a` 時記 n-a)

n-a — 4-spec Design Boundary Contract Applicability = n-a（單檔本機 shell）。

## Standards Axis

> Author 初掃（非正式獨立 Standards reviewer）。B 應重做雙軸。

- （無 🔴／無未授權 Boundary）腳本 ≤5 行；shebang／printf 對齊 DD-1／DD-2。
- F-s7a-1 🟢 `docs/dev/dogfood-ping/4-spec.md` Verification Profile | 缺 `Required layers` 明示欄（可寫「無」）——Gauntlet `--review-file` 可能 fail-closed | 建議：owner／B 裁決是否 L2 回補一行，或本 dogfood 接受降級聲明（見 KL #3）

## Spec Axis

| R | 判定 | 證據 |
|---|---|---|
| R-1 | 符合（author） | `scripts/dogfood-ping.sh:1-5`；S-1 現象 ✅；Stage6 獨立審 PASS |
| R-2 | 符合（author） | stdout hex + cmp；S-2 ✅ |
| R-3 | 符合（author） | exit 0；S-3 ✅ |
| R-4 | 符合（author） | `check-file-map.sh:114` = 194；指南 `guide-dev-flow.html:3961`；guards `:2417`；S-4 ✅ |
| D-s6-1 | 已吸收 | Example 本輪已落地 `example/dogfood-ping/`（author packing）；合 main 後滿足 SC-6 |
| Design Boundary | n-a | 無未經授權 Boundary 變更 |

## 變更架構圖

```text
[caller: bash / ./scripts/dogfood-ping.sh]
        |
        v
[scripts/dogfood-ping.sh] --printf--> stdout "dogfood-ok\n"
        |                         `--exit--> 0
        +-- file-map floor --> [check-file-map.sh EXPECTED=194]
        +-- guide row -------> [guides/guide-dev-flow.html #filemap]
        +-- static pin ------> [test-architecture-guards.sh]
        +-- feat canon ------> [docs/dev/dogfood-ping/]
        +-- Example mirror --> [example/dogfood-ping/]
```

## Diff(merge-base(main)..HEAD,逐檔折疊)

<details>
<summary title="+5/-0; dogfood-ping CLI"><code>scripts/dogfood-ping.sh</code> (+5/-0)</summary>
<pre><span class="add">+#!/usr/bin/env bash</span>
<span class="add">+# dogfood-ping — minimal observable CLI (Stage 6).</span>
<span class="add">+printf '%s\n' 'dogfood-ok'</span>
<span class="add">+exit 0</span></pre>
</details>

<details>
<summary title="+1/-1; EXPECTED_MAPPED_FILES"><code>scripts/check-file-map.sh</code> (+1/-1)</summary>
<pre><span class="del">-EXPECTED_MAPPED_FILES = 193</span>
<span class="add">+EXPECTED_MAPPED_FILES = 194</span></pre>
</details>

<details>
<summary title="+1/-1; static pin"><code>scripts/test-architecture-guards.sh</code> (+1/-1)</summary>
<pre><span class="del">-... EXPECTED_MAPPED_FILES = 193 ...</span>
<span class="add">+check_static_pin "scripts/check-file-map.sh" "EXPECTED_MAPPED_FILES = 194" "..."</span></pre>
</details>

<details>
<summary title="filemap row"><code>guides/guide-dev-flow.html</code> (filemap +dogfood-ping.sh)</summary>
<pre><span class="add">+&lt;code&gt;dogfood-ping.sh&lt;/code&gt; — dogfood-ping 極小可觀測 CLI...</span></pre>
</details>

<details>
<summary title="feat docs + Example"><code>docs/dev/dogfood-ping/*</code> · <code>example/dogfood-ping/*</code></summary>
<pre>Stage 1–7 過程檔（含本 7-review）+ Example 最小鏡像；合 main 滿足 SC-6。</pre>
</details>

## Verdict

**PASS** —— **Human G3 PASS by owner（rick-dev-flow）on 2026-09-11 (Asia/Taipei)。**

依據：Author A 證據包 + 獨立 reviewer B（`7-reviewer-B-notes.md`，@ `36c68db`）親跑 S-1～S-4 全綠、建議 PASS；owner 採納並提交本檔 `verdict: PASS`。准 squash-merge PR [#164](https://github.com/rick546986/dev-flow/pull/164) → `main` 落 Example。

| 門檻 | 證據 | 簽署 |
|---|---|---|
| 本次 S 全綠 | Coverage Matrix S-1～S-4 ✅；B 複驗 hex／exit／file-map 194 | Human G3 |
| 既有回歸綠 | `check-file-map.sh` exit 0 | Human G3 |
| 現象證據逐 S | 本檔現象表 + B notes | Human G3 |
| Evidence／Gauntlet | KL #3：缺 `Required layers` → Gauntlet 明示**降級**（不默認跑過）；不擋產品 PASS | Human G3 |
| 無 🔴 | Author／B 無產品行為 🔴 | Human G3 |

整合回歸（author @ Stage6）：`STATUS=N_A_NO_INCOMING FORK=0a89ec85ae2cf3ee0c555b82441caa323e77c10f HEAD=a940b4dfe38cffe9e3d597c88fe5e85c05aeb53b INTEGRATION=0a89ec85ae2cf3ee0c555b82441caa323e77c10f(refs/remotes/origin/main)`。B @ `36c68db` 重跑腳本綠；其後僅文件／Example／G3 密封，無產品行為碼變更。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | Stage2 審頁「方案依據」超寬橫表／手機裁切 | 🟡（dogfood 摩擦；非本產品行為） | park → [#165](https://github.com/rick546986/dev-flow/issues/165)；本 PR 不修 |
| 2 | Cloud／部分 VM 跑全套 `test-architecture-guards.sh` 可能撞環境 PF-0（無 Python 3.9–3.11）——Stage6 獨立審已標 **outside** T-1/T-2 Verify | 🟢 | 維持；本 feat 回歸入口以 `check-file-map.sh` 為準；全 guards 另環境 |
| 3 | 4-spec Verification Profile **無 `Required layers` 欄**（契約允許寫「無」/none/n-a，但缺欄 ≠ 零層）→ Gauntlet `--review-file` 可能紅 | 🟡（流程／文件形狀；G2 已 PASS） | **G3 明示降級**（不默認跑過）；另票 L2 補欄可選 |
| 4 | Example 鏡像與 feat 正本可能短暫漂移（B 改 7-review 後須同步 `example/dogfood-ping/7-review.*` 或 merge packing 再刷） | 🟢 | Exit 勾 Example 同步；合 main 前核對 |
| 5 | （已關閉）曾為 author PRE-REVIEW／待 B＋Human | — | B 建議 PASS + Human G3 PASS 2026-09-11 |

## Exit Checklist(全勾才算 shipped — 多數留給 Human／merge 後)

- [x] **Design Boundary finding 全數處置**: n-a（契約 n-a）
- [x] Quiz: n-a（fast lane 免；非不可逆 schema／API）
- [x] (條件式)整合回歸已在 Final Fresh **之前**記錄: author 已貼 `N_A_NO_INCOMING` + 三 SHA（見 Verdict）；B @ `36c68db` 重跑綠；G3 後禁改產品行為碼
- [ ] PR → main: PR [#164](https://github.com/rick546986/dev-flow/pull/164)；**Human G3 PASS 已簽 → merge in progress**
- [x] 4-spec delta 已併入 `docs/specs/<domain>.md`: n-a（本 repo 無對應 living domain spec 要併；極小 CLI dogfood）
- [ ] STATUS.md 已更新為 shipped: **merge 後由 merger 在 main 做**（feature branch 禁改 STATUS 表列）
- [x] 7-review frontmatter `verdict: PASS`（Human G3）；`status: approved`（`shipped` 留 merge 後）
- [x] 7-review.html 已產生／G3 密封後重生
- [x] Example `example/dogfood-ping/` 最小鏡像已落地（SC-6 packing；合 main 後可指）
- [ ] feature branch 已刪 / worktree 已清: merge 後再做

### Owner G3 出手清單（短）

1. ~~確認獨立 reviewer B ≠ A~~ → 見 `7-reviewer-B-notes.md`（建議 PASS）。
2. ~~抽驗 Coverage~~ → owner 採納 B／現象證據。
3. ~~提交判定~~ → **Human G3 PASS 2026-09-11 (Asia/Taipei)**；本檔 `verdict: PASS`。
4. merge #164 → main（Example）；合併後更新 STATUS／必要時刷 Example。

## 附錄:本輪特有

### A1　角色鏈：Author → B → Human G3

Author pack（PRE-REVIEW）→ 獨立 B notes（建議 PASS，未代填 frontmatter）→ **Human G3 PASS** 寫入本檔 `verdict: PASS`（2026-09-11 Asia/Taipei）。

### A2　Stage6 獨立審索引（證據鏈，非 Stage7 替代）

- URL: https://github.com/rick546986/dev-flow/pull/164#pullrequestreview-5168696526
- Commit: `a940b4d`
- 結論: Stage6 **PASS**；stdout hex／exit 0／file-map 194 與其複驗一致；Example 當時 deferred（本 author 已補鏡像）

### A3　Author／B 現象原始輸出（摘要）

```
#!/usr/bin/env bash          # head -n1
exit=0
 64 6f 67 66 6f 6f 64 2d 6f 6b 0a
CMP_OK
T1_VERIFY_OK
scanned=194 … ✅ PASS … filemap_exit=0
```

### A4　#165 與 DOGFOOD 摩擦

Stage2 方案依據超寬表 → [#165](https://github.com/rick546986/dev-flow/issues/165)。試跑筆記見 `DOGFOOD-NOTES.md`。不阻擋本 CLI 出貨判定，但阻擋「審頁體驗完美」宣稱。**#165 保持 open。**

### A5　Human G3 確認紀錄

- G3 | 2026-09-11 (Asia/Taipei) | owner（rick-dev-flow）明示 **G3 PASS**；`verdict: PASS`、`status: approved`；准 merge #164 → main 當 Example。
