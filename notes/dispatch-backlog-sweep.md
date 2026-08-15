# 派工：dev-flow 待辦一次做完（自主推進，全程不打斷問人）

> 這份是**可直接執行的派工單**。owner 用一句話觸發：
> 「讀 `~/dev/dev-flow/notes/dispatch-backlog-sweep.md` 照它跑，全程不打斷問人」。
> 寫於 2026-08-15（plugin v3.3.0，本地有未推 commit）。

## 你的角色

你是這次改版的**指揮官與最終驗收者**。你不下場寫大量程式碼 —— 你負責拆解、派工、
裁決、驗收。實際動手交給下層模型（見「模型分層」）。

專案：`/Users/asheng/dev/dev-flow`（Claude Code plugin + 開發流程方法論母版，**公開 repo**）

**這個 repo 的特殊性**：它同時是「方法論的正本」和「執行方法論的程式」。你改的東西
會散發到四個採用專案（`icryobank-crm-api-golang`、`ivf_platform`、`python-prism`、
`report-system`），所以每個改動都要問「這會不會在別人的 repo 炸掉」。

---

## 開工前先做（不要跳過）

```bash
cd /Users/asheng/dev/dev-flow
git status --short          # 必須為空；不為空 → 停下回報，不要自己決定 commit 或 stash
git log --oneline -12
git branch --show-current   # 應為 main
git rev-list --count origin/main..HEAD   # 有未推 commit 是正常的，不要試圖 push
```

任務來源（**不要憑本檔的摘要行事，去讀正本**）：

| 讀哪 | 是什麼 |
|---|---|
| `docs/dev/STATUS.md` 的 Backlog 表 | 待辦看板，14 列（A-1…A-6、A-11、A-12、B-1…B-6）|
| `notes/adoption-findings-2026-08-04.md`（1400+ 行）| **待辦的正本**：每條有現象、查證、建議修法、行號 |
| `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 **A4/A5/A6** | 第一批任務的完整背景（三輪獨立審查的 28 條 finding 與修法）|
| `docs/dev/HISTORY.md` | 做過什麼（12 筆，只增不改）|
| `README.md` §1 文件地圖、§6 twin 規格、§7 角色與 Gate | 方法論本身 |

---

# 第一批（最高優先）：把 gate twin 的解析層換成現成 markdown 解析器

## 為什麼這是第一批

`scripts/build-gate-twin.py` 用**手刻正則**解析 markdown（章節切段、fenced code 遮蔽、
表格、欄位）。三輪獨立審查下來，這一層總共爆了 **28 條 finding**，其中：

- **兩條是「修上一輪時引入的新 HIGH」**（N1 索引錯位讓審查者讀到假內容、P2 未閉合 fence
  把 frontmatter 一起遮掉）
- **一條已經發生在出貨物上**（P4：`\s` 含換行 → 正則跨行吃到檔尾 → `## 變更架構圖`
  整節從產出的 html 消失，而當時 53 項守衛全綠）
- 邊界一個接一個：四反引號巢狀、`~~~`、未閉合 fence、縮排 fence、CRLF、檔尾無換行、
  `R-1` 是 `R-10` 的子字串、正則跨行……

**結論：這類工作靠手刻正則 + 自審不可能收斂。** 每補一個邊界就冒出下一個。

## 要做什麼

把解析層換成 **`markdown-it-py`**，理由：**這個 repo 已經有這個相依**——
`scripts/requirements-methodology-render.txt` 釘死 `markdown-it-py==4.0.0`，
`scripts/render-methodology-corrections.sh:20-27` 已經在用它，而且**有版本檢查**
（版本不符直接報錯，不靜默降級）。當初避開相依的理由（「散發到別人機器會跑不起來」）
在這個 repo 不成立。

範圍：
1. `scripts/build-gate-twin.py` 的解析層（`mask_fenced` / `sections` / `table_rows` /
   `_find` / `parse_*` 的切割部分）改用 markdown-it-py 的 token stream。
   **渲染層與版面（卡片、置頂節、動線五格、兩種殼）不動** —— 那些已經被 60 項守衛守著。
2. **相依必須 fail-loud**：import 失敗或版本不符 → 印出「請跑
   `pip install -r <路徑>/requirements-methodology-render.txt`」並 exit 2，
   **不得吐 traceback、不得靜默降級回正則**。照 `render-methodology-corrections.sh:25-27` 的既有寫法。
3. `skills/dev-setup/SKILL.md` 的散發段要交代這個相依（採用專案要裝得起來）。
4. **既有 60 項守衛必須全過且不得放寬**。守衛是這一批的驗收標準，不是可以配合改動的東西。
   如果某條守衛因為新解析器而失效 → 那是守衛沒守住新的失敗模式，**要加強不是刪掉**。

## 換完之後必須自己驗這些（三輪審查累積的失敗模式，逐條實測）

| 案例 | 期望 |
|---|---|
| 四個反引號包三個反引號 | 內層不被當成真標題 |
| `~~~` 圍欄 | 同上 |
| 未閉合的 fence | 其後內容不進待審區，**且印出明確警告**（不得靜默）|
| ```` ```python ```` 帶語言標籤、最多三格縮排 | 正常遮蔽 |
| CRLF 行尾、檔尾無換行 | 不錯位 |
| 章節整節只有一個 code fence | **該節仍要出現在背景資料**（P4 的回歸）|
| 背景章節內文提到 `R-1`、`R-10` | 整節不得消失（N3）|
| fence 內寫 `verdict: REJECTED`、`\| OC-9 \| 待裁決 \|` | 不得污染動線格與計數（N2）|
| 每個非卡片章節埋 canary | 全部要出現在產出物（C3 內容零刪減）|

現成 fixture 在 `scripts/fixtures/gate-twin/`（`missing-obs`、`zero-deletion`），
守衛 `scripts/check-gate-twin.sh` 內也有自造材料，直接沿用並擴充。

## 這一批的 Definition of Done

- 60 項守衛全過（不得放寬任一條）
- 上表案例逐條實測通過，輸出貼進回報
- **派一個 fresh-context sonnet 做破壞實驗**：把新解析器改壞（每次改一處），
  確認守衛真的變紅；改一行仍全綠 = 那條守衛沒用，要補
- `docs/dev/b8-gate-twin-review-ui/7-review.md` 追加附錄 A7 記錄這次替換
- 重產本 repo 自己的 twin，確認章節數與 md 對得上

---

# 第二批：Backlog 14 條

`docs/dev/STATUS.md` 的 Backlog 逐條處理。每條在
`notes/adoption-findings-2026-08-04.md` 都有完整的現象/查證/建議修法，**先讀正本再決定做法**。

⚠️ 幾條要注意：

- **A-1**：講的是 `dev-setup` 散發出去的 `docs/dev/README.md` 帶 23 條死引用。
  本 repo 自己**沒有**那個檔（實測），要修的是 `skills/dev-setup/SKILL.md` 的散發邏輯。
- **A-2 ~ A-6**：都動到 `hooks/` 的 runtime 程式碼。改完 `bash hooks/selftest.sh` 必須全過
  （**案數以當下輸出為準，不要寫死在任何文件裡** —— 有寫死 33 案漂移到 80 的前科）。
- **B-5 / B-6** 標「待裁決」：**你就是裁決者**（owner 已授權「照 fable5 的建議執行」）。
  裁決結果與理由寫進 `notes/adoption-findings-2026-08-04.md` 對應節，
  格式照該檔既有的「已採用的修法（日期）」段落。

# 第三批：散落的過期狀態（六件）

1. **`docs/dev/4cap-remediation/` 結案**
   - `4cap-audit-fixes-2026-08.md` 開頭寫「待 rick 裁決，未動工」，但主體五項 P1~P5
     **已全部落地**（證據：`scripts/check-methodology-corrections.sh:270-278`、
     `scripts/check-realworld.sh:107,119,127-130`、
     `scripts/devflow-evidence-gauntlet.sh:235-240`、`README.md:430`、
     `_templates/5-tasks.md:18-20`）。狀態標註要改正。
   - 同檔 **8 項選配 O-1~O-8 未裁決** → 你裁決，逐項給採/不採 + 理由。
   - `devflow-4cap-remediation-2026-08.md` §7 有 **6 件真的沒做完**（第 1、2、2b、4、5、6 點），
     **目前不在任何待辦清單裡** → 逐條判斷，做掉或寫明理由並收進 Backlog。
   - ⚠️ 同檔的**「防守清單」7 條是「明確裁定不要做」的紀錄**，用途是防止未來誤補。
     **不得刪除、不得執行那 7 條。**（第 7 條「外掛不要併回本 repo」已於 2026-08-13
     被推翻，翻案紀錄在 `docs/adr/0001-merge-plugin-into-methodology-repo.md`。）

2. **56 處過期的外掛路徑**：`~/.claude/plugins/local/dev-flow/` 是舊位置，正確是
   `~/.claude/plugins/cache/dev-flow/dev-flow/<版本>/`（`docs/PLUGIN.md:17` 與
   `skills/dev-setup/SKILL.md:15` 都明寫「勿寫死」）。三份導覽網頁、README、
   `scripts/devflow-check.sh:10`、`tests/parallel-stage6/contract_ref.py:4` 都還寫舊的
   → **照導覽走的人會找不到檔**。統一寫法並註明 Windows 對應（`%USERPROFILE%\.claude\...`）。
   ⚠️ `/Users/asheng/...` 那 21 處全在歷史文件裡（`docs/prompts/`、`4cap-remediation/`、
   `adoption-findings`）→ **歷史紀錄不要改**，改了等於竄改紀錄。

3. **新增一支路徑守衛**：`scripts/` 底下沒有任何一支在擋「又寫死絕對路徑」。
   加一支、註冊進 `scripts/devflow-check.sh`、要有負向 fixture。

4. **五處「外部外掛待辦」核對**：`notes/change-manifests/execution.md:136`（8 項）、
   `observability.md:125`（6 項）、`gauntlet.md:134`、`10-integration-decisions.md:51`、
   `notes/design/parallel-stage6.md:453`。這五處都寫「外部 plugin 待辦」「runtime 不在本 repo」
   —— **前提已於 2026-08-13 失效**（外掛已併入，`hooks/` 就在這裡），
   而且抽查顯示多數項目其實已落地。逐項核對真實狀態，做完的標掉、真的沒做的收進 Backlog。

5. **一組打架的數字**：`notes/adoption-findings-2026-08-04.md` 第三輪 B-9 寫
   「16 個 S 裡有 **5 個**缺觀測欄」，v3.1.0 release notes 寫「**13 個**」。查出哪個對。

6. **兩條過期的狀態標記**：`adoption-findings` 裡 A-13 與 B-9 仍標「⏳ 未修」，
   但兩條都已在 v3.1.0 修掉。比照該檔既有的「✅ 已修（日期）」格式更新。

# 第四批：收尾文檔

- `docs/dev/STATUS.md`：Backlog 反映真實剩餘。
- `docs/dev/HISTORY.md`：**只能用 `scripts/history-append.sh` 寫**
  （直接 Edit/Write 會被 `history-guard` hook 擋下，因為多 session 並行會靜默覆蓋）。
- `README.md`：動到規則就同步；文件地圖有新檔要補。
- `docs/adr/`：符合「難逆轉 + 反直覺 + 真 trade-off」的裁決 → 立 ADR
  （格式見 `_templates/adr.md`，編號唯一性由 `scripts/check-adr-integrity.sh` 驗）。
- **不要在文件裡寫死會腐化的數字**（測試案數、檢查組數、檔案數）—— 有前科（commit `bada41a`）。

---

## 模型分層（硬規則）

| 層 | 模型 | 做什麼 |
|---|---|---|
| 執行 | **haiku** | 機械改動：字串替換、路徑統一、格式修正、照既有 pattern 加檢查、跑指令收集輸出 |
| 審查 | **sonnet** | 每個產出都要 fresh-context sonnet 審過才算數。審查者不看實作者的解釋，只看產物 |
| 裁決與驗收 | **你（fable5）** | 拆解、設計改法、裁決待裁決項、最終驗收 |

**升降級**：haiku 同一件事錯一次 → 升 sonnet；sonnet 同一件事錯兩次（帶完整失敗軌跡）→ 你接手。

**派工三件套**（缺一不派）：目標與動機 / 驗收條件 / 回報格式。
審查型派工要明寫「你的角色是試著讓它不過，不是幫它說話」。

---

## 這個 repo 的守衛四次「假綠」—— 你會遇到同一類問題

三輪獨立審查抓到四次「檢查全綠但東西是壞的」，型態各不相同：

| # | 型態 | 具體 |
|---|---|---|
| 1 | **只驗殼不驗內容** | 守衛斷言 `<details>` 這個字串在，把渲染函式改成 `return ""`（內容全刪）照樣全過 |
| 2 | **斷言釘在會出現在多處的文字上** | 用「字串出現在 `<details>` 外面」判斷置頂節，但動線頂區的註解也含同樣的字 → 恆真 |
| 3 | **斷言釘在副本而非正本** | README 寫「標籤逐字釘死，由守衛驗」，但守衛比對的是它自己硬寫的一份 → 改 README 照樣綠 |
| 4 | **只檢查「有的東西對不對」，沒檢查「該有的東西還在不在」** | 整個章節從產出物消失，60 項斷言沒有一條會發現 |

**你新增的每一支守衛都要問這四個問題。** 另外：

- **新增檢查必須有負向 fixture**，而且要**實測「故意弄壞被檢查的東西，守衛會不會真的變紅」**
  —— 改一行仍全綠 = 這支守衛沒用。
- **先看計數再看 exit code**：輸出若顯示「掃到 0 個項目」卻回 exit 0，那是沒解析到，不是沒問題。
- **守衛要有一條是「盤點」型的**：產出物的章節數/內容量要對得上輸入。

---

## 全域硬約束

1. **`_templates/*.md` 的執行清單多半在 parity 區內**（三份導覽 html 逐字同步）。
   改模板前先 `grep -n "parity" guides/*.html`，改完跑
   `bash scripts/render-methodology-corrections.sh --write`，**不要手改 html**。
   收工前 `--check` 必須回 `6/6 byte-identical`。
2. **散發副本五份要一致**（正本方向永遠是 根目錄 → `docs/dev/`）：
   ```bash
   diff -q devflow-contract.json docs/dev/devflow-contract.json
   diff -q scripts/devflow-evidence-gauntlet.sh docs/dev/tools/devflow-evidence-gauntlet.sh
   diff -q scripts/history-append.sh docs/dev/tools/history-append.sh
   diff -q scripts/build-gate-twin.py docs/dev/tools/build-gate-twin.py
   diff -q scripts/devflow_twin_ui.py docs/dev/tools/devflow_twin_ui.py
   ```
3. **git 流向**：不直接 commit 到 `main`。每一批走 feature branch → `git merge --no-ff` 回 main。
   commit message 用中文、講清楚「為什麼」而不只是「改了什麼」。一個 commit 一件事。
4. **絕對不 push**。owner 的設定有 `permissions.deny: Bash(*git push*main*)`，
   這是他刻意設的護欄。**不要試圖繞過**（改指令形狀、改設定、用別的工具都不行）。
   全部做完後把「請你自己跑 `git push origin main`」列在最終回報。
5. **不動歷史紀錄**：`notes/verification-benchmark-2026-08.md`（自註「結論不隨後續改造改寫」）、
   `4cap-remediation/` 的執行報告本文、`docs/prompts/` 的需求正本 —— 只能加註「後續狀態見 X」。
6. **`docs/dev/HISTORY.md` 只能用腳本追加**（見第四批）。

---

## 驗收（每一批做完都跑，最後再跑一次）

```bash
bash scripts/devflow-check.sh            # 期望 REPO_REFERENCE_PASS(N 組全過)
bash scripts/check-gate-twin.sh          # 期望全過（項數以輸出為準）
env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
                                         # 期望 14/14、exit 0（三個環境變數必須真的 unset）
bash hooks/selftest.sh                   # 期望全過（案數以輸出為準）
bash hooks/devflow-exec.sh doctor        # 期望 COMPATIBLE
bash scripts/render-methodology-corrections.sh --check   # 期望 6/6 byte-identical
```

**任一紅就停下修，不要以「這條跟本次改動無關」放行** —— 那正是這個 repo 的
`gate-consistency` 壞了九天沒人發現的成因。

**每一批做完，派一個 fresh-context sonnet 獨立審查**（不看你的解釋，只看產物，
要它做破壞實驗）。三輪經驗：**每一輪都會找到東西，而且兩次是「修上一輪時引入的新 HIGH」。**

---

## 自主推進的規則（owner 不在線上）

- **遇到需要裁決的事，你自己裁決**，理由寫進對應文件。owner 已授權。
- **不要停下來問人**。真的遇到「做了不可逆且無法判斷」的事（刪大量歷史紀錄、改寫 git 歷史、
  動遠端狀態）→ **跳過並列進最終回報的「待 owner 裁決」**，繼續做其他項。
- 做不到或判斷不該做 → 在 Backlog 保留該列，並在 findings 對應節寫明「本輪不做的理由」。
  **不要為了清空 Backlog 而硬做。**
- 每批之間可以自行決定順序，但**第一批要先做完**（其他批會動到同一批檔案）。

---

## 最終回報格式

```
## 做完了什麼
| 項 | 做法一句 | 落在哪（檔案:行號） | 驗證 |

## 沒做的與理由
| 項 | 為什麼不做 | 留在哪 |

## 待 owner 裁決（如果有）
| 項 | 卡在哪 | 我的建議 |

## 每批的獨立審查結果
| 批 | 審查者找到幾條 | 修了幾條 | 剩下什麼 |

## 驗證輸出（貼原文關鍵行）
六道全貼

## 下一步（給 owner）
- 未推 commit N 個，請自己跑：git push origin main
- 是否需要發版（新增檢查/工具 → minor），發版走 /dev-release
```

---

## 禁止

- 不 push、不改 owner 的設定、不繞過任何 deny 規則
- 不刪「明確裁定不要做」的防守清單
- 不改寫歷史紀錄類文件的內容（只能加註）
- 不在文件裡寫死會腐化的數字
- **不為了讓檢查變綠而放寬檢查本身**
- 不順手重構與待辦無關的程式碼
- 宣稱「完成」前必須有實跑輸出當證據，不接受「應該可以了」
