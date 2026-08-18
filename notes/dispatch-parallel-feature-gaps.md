# 派工：補多 feature 並行的四個制度空白

> owner 一句話觸發：
> 「讀 `~/dev/dev-flow/notes/dispatch-parallel-feature-gaps.md` 照它跑，全程不打斷問人」。
> 寫於 2026-08-17（plugin v3.7.0，**未推**）。前一份 `notes/dispatch-accounting-symmetry.md`
> 的五部分**已全部完成**（六道全綠、`devflow-check` 從 4:55 降到 48.7 秒），本檔不重複那些。

## 起因

第一次有人**真的跑完一個完整 feature**（26 個任務、Stage 7 G3 已 PASS），
接著要開兩個模組並行，才發現**母版對並行只講了一半**：講了「用 worktree 隔離」，
沒講「隔離之後這四件事怎麼辦」。

**四項的決定已由 owner 端裁定**（理由見各節）。你的工作是**照決定寫進母版該寫的位置**，
不是重新評估選項。

## 已定，不要動

| 既有規定 | 位置 |
|---|---|
| 多 feature 並行用 git worktree 隔離（執行守衛以工作樹為單位上鎖） | `README.md:265,293-301` |
| 起手式「開 feature branch（並行 → worktree）」 | `_templates/6-implementation-notes.md:22-23` |
| `execution.mode: parallel` 是**同一 feature 內**的 T 級並行，與多 feature 並行是兩套機制 | `README.md:302-303` |
| `docs/dev/<slug>/` 各自一份 | `README.md:153` |
| diff 基準 `merge-base(整合分支)..HEAD`；PR → 整合分支，禁直上 master | `_templates/7-review.md:250,277` |

⚠️ **措辭一律用「整合分支」不要寫死 `develop`** —— 模板現在寫 `develop`，但 dev-flow 自己
用 `main`（2026-08-02 owner 裁決「續用 main，不建 develop」）。新寫的段落用
「整合分支（`develop` 或 `main`，依專案）」，**既有那兩行不要改**（改了會動到 parity 區）。

**執行歧義①已澄清 —— 模板裡到底寫哪個詞**：

| 情況 | 寫什麼 |
|---|---|
| 你這一輪**新增**的句子 | 一律「整合分支」，第一次出現時附一次括號說明 `（develop 或 main，依專案）`，同一份檔案後續不必重複附註 |
| 既有句子裡的 `develop`（`_templates/7-review.md:250,277` 等） | **一個字都不要動** |
| 新句子必須舉指令當例子時 | 用 `<整合分支>` 當佔位符，例如 `git log <base>..<整合分支>`，**不要寫 `git log base..develop`** |

判準一句：**這輪新寫的東西不得再引入任何一個寫死的 `develop`。**

---

# 決定 1：STATUS.md 只在整合分支上維護，feature branch 一律不碰

## 空白

`_templates/STATUS.md:3` 說它是「並行開發時的單頁看板，一 feature 一列」，
但兩個 worktree 各 checkout 不同 branch、各自編輯同一個檔案 → **合併必然衝突**。

## 決定

**STATUS.md 是整合分支的檔案，不是 feature branch 的檔案。**

| 時機 | 在哪做 |
|---|---|
| 開工（加一列 Active） | **整合分支**上直接改並推 |
| 過 gate（更新階段/gate 欄） | **整合分支**上直接改並推 |
| ship（移出 Active） | 隨 PR 合併時在整合分支上做 |
| **feature branch / worktree 內** | **完全不碰 STATUS.md** |

**執行歧義③已澄清 —— 「ship 時移出 Active」誰做、在哪做、什麼時候做**：

| 問 | 答 |
|---|---|
| 誰做 | **合併那個 PR 的人**（也就是走完 Stage 7、按下 merge 的人），不是 reviewer |
| 在哪做 | **整合分支上，另一個 commit** —— 不要塞進 feature branch 的 PR 裡（那會讓 PR 的 diff 混進看板變更，也會在多 worktree 下製造衝突） |
| 什麼時候 | **PR 合併之後**，不是之前。合併前那一列還是「進行中」，這是事實 |
| 要不要等 | 不要累積 —— 合併完就順手改掉並推。看板落後一天，下一個人就會照著錯的狀態決策 |

也就是完整動線是：**PR 合併 → 切到整合分支 → 改 STATUS.md 移出該列 → 推**。
這四步是同一個人在同一個時間點做完，不分派給別人。

## 理由（要寫進模板，母版慣例是決定與理由同處）

- 三個候選裡，「隨時更新、衝突手動解」最危險：解衝突時**很容易把對方那一列刪掉**，
  而那是**靜默的資料遺失** —— 沒有紅字、沒有人會發現。
- 「拆成 `STATUS-<slug>.md`」零衝突，但那等於沒有看板 —— 看板的價值就在「一頁看完全部」，
  拆了還是要有人彙整，只是把衝突換成了人工彙整。
- 選「只在整合分支維護」不只是**降低**衝突機率，是讓衝突**結構上消失**：
  同一個檔案永遠只有一個分支在改。
- 代價是「在 worktree 裡看不到最新看板」—— 但**在自己的 worktree 裡本來就不需要看板**
  才知道自己在做什麼。看板是給**別人/別的 session**看的，那些人本來就該看整合分支。

## 要改哪

1. `_templates/STATUS.md` 頂註加這條規則 + 理由（現有頂註第 3 行那段的下面）
2. `_templates/6-implementation-notes.md` 起手式那條旁邊加一句
   「STATUS.md 不在 worktree 內改，見 STATUS 模板頂註」
3. `README.md` 並行那段（`:293-301`）補一句指向模板

---

# 決定 2：合併後回滾一律用 `git revert -m 1`，禁止 `reset --hard` 動整合分支

## 空白

全 repo 搜「回滾/revert/rollback」**零命中**（唯一一處是 `README:247` 講同一 feature 內
「一 T 一 commit 可逐點回滾」，那是**合併前**的事）。user 層鐵律 §9 只有分支流向一行字。

## 決定

| 情況 | 做法 |
|---|---|
| **預設** | `git revert -m 1 <merge commit>`，推到整合分支 |
| **明文禁止** | 對整合分支用 `reset --hard` / `push --force` / `rebase` —— 那會改寫**共享**歷史，其他 worktree 的 base 會消失 |
| **例外：直接補修** | 只有同時滿足兩條才可以：①一個 commit 修得完 ②不動其他 feature 碰過的檔 |

## 理由（要寫進檔案）

- 整合分支是**共享**的：其他 worktree 都從它開分支。改寫它的歷史 = 別人的 base 不見了，
  而且是在他們下次 `git fetch` 才會發現。
- 「直接補修」不是壞選項，但沒有判準就會被濫用成「什麼都在整合分支上修」。
  兩條判準都可機械檢查，不是憑感覺。

## ⚠️ 必須一起寫的坑（這條沒寫會實際踩到）

**`git revert` 一個 merge commit 之後，重新 merge 同一個 branch 不會生效。**
git 看的是祖先關係，revert 只是加一個反向 commit，不改變「那些 commit 已在歷史裡」的事實。

所以 revert 之後要讓那個 feature 回來，只有兩條路：

1. **revert the revert**（`git revert <那個 revert commit>`）後再補修
2. 從整合分支**重新開一個 branch**、把改動重做成新 commit

**兩條都要寫進去**，並說明「不要以為 revert 完再 merge 一次就好」。

## 要改哪

`_templates/7-review.md` 的 Exit Checklist 之後新增一節「合併後出事怎麼辦」，
或另立一段在 `README.md` §7 附近 —— 位置你判斷，但**必須是走完流程的人會讀到的地方**
（不要塞進 notes/）。

---

# 決定 3：整合回歸是**條件式**的，條件可機械判定

## 空白

Stage 7 只保證「各自 branch 對整合分支的 diff 乾淨」，
**沒有任何一關檢查「A 和 B 合在一起會不會互相踩」**。

真實風險（實際發生）：兩個模組都動到依賴組裝（`dependencies.go`）或路由掛載（`routes.go`）
就是共同戰場 —— order-intake 這次就改了那兩個檔。

## 決定

**在 `_templates/7-review.md` 的 Exit Checklist 加一條條件式檢查**，不是每次都跑：

```
- [ ] （條件式）整合回歸：若 `git log <本 branch 的 base>..<整合分支>` 非空
      —— 表示你開分支之後有別的 feature 先合進來了 —— 則：
      1. 把整合分支合進本 branch（或 rebase），先在**本地**解完衝突
      2. 跑一次全套測試
      3. 列出**共同戰場**：`comm -12 <(git diff --name-only <base>..HEAD | sort) \
         <(git diff --name-only <base>..<整合分支> | sort)`
         → 有交集的檔案逐個看過，交集為空才可勾
```

**執行歧義②已澄清 —— `<base>` 是哪一個 commit**：

一律用 **`git merge-base HEAD <整合分支>`** 的結果，**不是「開分支時的那個 commit」**。

| 為什麼 | 說明 |
|---|---|
| 兩者常常不同 | rebase 過、或整合分支往前跑過之後，「當初開分支的點」已經不在共同祖先上 |
| merge-base 才答得對問題 | 要問的是「**我這條線跟整合分支分岔之後，對方多了什麼**」，那正是 merge-base 的定義 |
| 與既有規定一致 | `_templates/7-review.md:250` 的 diff 基準本來就是 `merge-base(整合分支)..HEAD` |

寫進 Exit Checklist 時直接把它嵌進指令，不要讓填的人自己想 `<base>` 是什麼：

```bash
BASE=$(git merge-base HEAD <整合分支>)
git log "$BASE..<整合分支>"          # 非空 = 你開分支後有人先合進來了
```

## 理由（要寫進檔案）

- **不是每次都跑**：你是第一個合的話沒有東西可以踩，強制跑只是浪費。
  條件「開分支之後有別人先合進來」正好是「有東西可能踩」的充要條件。
- **共同戰場用機械算，不靠憑感覺**：兩個 diff 的檔案交集，一行指令就有答案。
  憑感覺會漏掉「我沒想到那也算依賴組裝」的檔案。
- 放在 Exit Checklist 而不是 STATUS 流程：那條清單本來就是「還缺什麼才能出貨」，
  而這正是出貨前的最後一道。

---

# 決定 4：母版**要管**，但只管「檢查什麼」，不管「怎麼隔離」

## 空白

母版叫人用 worktree 並行，但沒提醒 **worktree 之間的執行環境要隔離**。

實際撞到的：docker compose 若把 `container_name`、對外 port、資料庫名寫死，
第二個 worktree 起不來；**更隱蔽的是共用同一個資料庫時，
`atlas_schema_revisions` 那張紀錄表會混進兩個 feature 的 migration 版本**，
導致 apply 直接拒絕執行（B 的目錄裡找不到 A 已套用的版本）。
order-intake 的 T-2 已經踩過一次（作廢的 migration 檔已刪、紀錄還在）。

## 決定

**母版要管，理由是：母版規定了「並行用 worktree」，就要負責講清楚這個規定的代價。**
規定了做法卻不講代價，就是「規定了做不到的事」（A-0/A-13 那一整類的成因）。

但**只加檢查項，不規定實作**：

```
- [ ] 並行前確認執行環境已隔離（多 worktree 才需要）：
      - 容器名／對外 port：兩個 worktree 同時起得來嗎？
      - **資料庫**：共用同一個 DB 時，migration 版本紀錄表會混進兩個 feature 的版本，
        導致其中一邊 apply 被拒（實例：`atlas_schema_revisions`）
      - 快取／訊息佇列／檔案上傳目錄等有狀態的外部依賴
      → 隔離方式依專案技術棧自理，母版不規定做法
```

## 理由（要寫進檔案）

- **管**：這是母版自己的規定帶出來的坑，不提醒等於挖坑給人跳。
- **只管檢查項**：怎麼隔離 docker/db/port 是各專案技術棧的事，母版規定做法會變成
  「規定了但不適用」，那是另一種同型錯誤。
- 資料庫那條要**寫實例**（`atlas_schema_revisions`）：這個坑光講「資料庫要隔離」
  沒人會想到「紀錄表混版本」這一層，寫了實例才擋得住。

## 要改哪

`_templates/6-implementation-notes.md` 起手式那條（`:22-23`）旁邊，
與決定 1 的那句話同一處。

---

# 驗收

1. **四項各自的檔案改動都要有「決定 + 理由」同處**（母版慣例），
   不是只改結論。改完貼出每處的 `檔案:行號` 與內容。
2. **改模板要跑 parity 同步**：`bash scripts/render-methodology-corrections.sh --write`，
   收工前 `--check` 必須 `6/6 byte-identical`。
3. **跑一次 dev-setup 健檢**，確認模板與 README 沒有互相矛盾（owner 明確要求這一步）。
4. 六道回歸不得退化（數字以當下輸出為準，不寫進活文件）：
```bash
bash scripts/devflow-check.sh
bash scripts/check-gate-twin.sh
env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
bash hooks/selftest.sh
bash hooks/devflow-exec.sh doctor
bash scripts/render-methodology-corrections.sh --check
```
5. **這四項是散文規則，沒有機械層** —— 逐項判斷「能不能機械化」，
   能的就補守衛（例如決定 3 的共同戰場指令可以做成腳本），不能的**寫明為什麼不能**。
   ⚠️ 這個 repo 的歷史教訓：散文規則的失效是靜默的。
   但**不要為了機械化而硬做** —— 判斷不值得就寫理由。

# 硬約束（沿用）

0. **開工第一件事：從 `main` 開一個工作 branch**（例如 `feat/parallel-feature-gaps`），
   所有改動都在那條 branch 上做，最後 `git merge --no-ff` 回 `main`。
   **不要在 `main` 上直接動手** —— 這輪要改的是模板與 README，改到一半的狀態留在 `main`
   會讓別的 session 讀到半成品。
1. **不 push**、不繞過 deny 規則。做完把「請你自己跑 `git push origin main`」列在回報。
2. 不直接 commit `main`：feature branch → `git merge --no-ff` 回 main，一個 commit 一件事。
3. 不得為了讓檢查變綠而放寬檢查本身。
4. 散發副本要一致。
5. `docs/dev/HISTORY.md` 只能用 `scripts/history-append.sh` 追加。
6. 不動歷史紀錄類文件的內容（只能加註）。
7. 不在活文件裡寫死會腐化的數字。

# 不要做

- **不要改 `execution.mode: parallel` 那套 T 級並行機制**（規定完整、運作正常）
- **不要動採用專案的 repo**（決定下放是之後的事）
- 不要改 `_templates/7-review.md:250,277` 那兩行既有的 `develop` 措辭（會動到 parity 區）
- 不要把這四項當成「選項還沒定」重新評估 —— **決定已定，你的工作是寫進去**

# 這一輪之後的下一步（不是你的任務，寫在這裡是為了讓你知道邊界）

owner 已排定：這四項做完之後，**拿 dev-flow 自己跑一次完整 normal-risk full lane**
（1-discussion → 7-review、過 G1/G2/G3），把那次當成**觀測實驗** ——
用實際走過的經驗去對照 `notes/review-requirement-discovery-gaps.md` 的九條，
再決定哪幾條是真痛點。

**所以這一輪不要順手改 Stage 1–4 的模板內容**（除了本檔四項明確要求的那幾處）。
改多了會污染那次觀測 —— 到時候分不出「流程本來就有問題」還是「這輪改出來的問題」。

# 完成之後

- `docs/dev/STATUS.md` Backlog 反映真實剩餘
- `docs/dev/HISTORY.md` 追加一筆
- 屬「模板/規則變更」→ 走 `/dev-release`，級別自己判（模板加節通常是 minor），
  **停在 push 前交給 owner**

---

# 本輪範圍外：需求討論的九條制度缺口

2026-08-17 另有一份盤點，列出 `dev-talk` 與 Stage 1–4 的九條制度缺口（A-1~A-7、B-1、B-2）。
**那九條不在本派工單範圍，也不要在本輪處理** —— owner 已裁定暫緩，等 dev-flow 自己
跑完一次完整 full lane 之後再逐條裁決。

全文在 `notes/review-requirement-discovery-gaps.md`。**讀到這裡就停，不要打開那份照做。**
