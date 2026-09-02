# 0003. Agent Memory 分兩層:`.dev-flow/` 進 Git、本機索引不進 Git

- Status: accepted
- Date: 2026-08-20
- Source: docs/prompts(Agent Memory v3 需求正本);落地見指南 `#memory`

> 晉升條件(三條件**全中**才立此檔,否則留在 2-decision 就好):
> 難逆轉 + 反直覺 + 真 trade-off。
>
> 本案三條全中:記憶的儲存分界一旦鋪開就有既存資料要遷(難逆轉);
> 「把記憶存進 Git 卻刻意不存索引與向量」與直覺相反(反直覺);
> 換到跨機器可攜與乾淨的 Git 樹,付出的是 clone 後必須先跑一次 dev-setup(真 trade-off)。

## Context

舊架構的 agent 記憶載體有兩個,都是人工維護的 Markdown:repo root `CONTEXT.md`
(業務詞彙表)與 `docs/dev/HISTORY.md`(改版歷史索引)。三個問題:

1. **沒有 identity**:記憶靠 filesystem path 定位。Mac 的 `/Users/…`、Windows 的
   `D:\…`、Linux 的 `/home/…` 是三份不同的東西,而它們其實是同一個專案。
2. **沒有狀態**:詞條寫下去就永遠是真的。程式碼改了、業務規則改了,詞條不會變,
   而且**腐化時沒有任何機制會發現**。
3. **沒有分層**:「程式現在怎麼運作」「這個詞什麼意思」「我們打算怎麼走」
   「當初為什麼選」全混在同一份文字裡,回答時分不出哪句是現況、哪句是願景。

## Decision

記憶分成兩層,分界的判準只有一句:**刪掉之後跑一次 `dev-setup` 能不能還原?**

| | 位置 | 進 Git | 放什麼 |
|---|---|---|---|
| durable | `.dev-flow/` | ✅ | 七類結構化高訊號記憶(implementation truth / domain / intent / event / decision / skill / unknown) |
| local runtime | 記憶家目錄下的 `projects/<project_id>/` | ❌ | SQLite 索引、FTS、embedding 向量、原始逐字稿、候選知識、本機失效 overlay、檢索指標 |

配套的三個硬條件:
- **identity 是 path-independent 的 ULID**,住 `.dev-flow/project.yaml` 並 commit 進 Git;
  不由路徑推導、不依賴 git remote(remote 只當 provenance)。
- **durable 內的檔案引用一律 repo-root-relative POSIX 路徑**;寫入時有守衛擋,
  `doctor` 複驗命中即 FAIL。
- **唯一 setup 入口仍是 `dev-setup`**;不新增第二個安裝器。

## Considered Options

**①全部進 Git(含 SQLite 與向量)。** 換到「clone 完就能用,不必重建」。
否決理由:二進位檔每次 pull 都衝突且無法人工裁決;更嚴重的是原始逐字稿與
執行期資料會被 push 出去 —— 一旦進了 commit,砍檔案不等於砍歷史。

**②全部只留本機。** 換到「零 Git 噪音」。否決理由:那就沒有跨機器記憶,
等於回到每台機器各自失憶,也是這次要解的問題本身。

**③記憶存在外部服務。** 換到「集中管理、可做真語意檢索」。否決理由:多一個相依、
一個要顧的機密、一個離線就不能用的失敗模式;而 dev-flow 的 runtime 面明文
「python3 標準函式庫,無第三方依賴」。

**④保留 `CONTEXT.md` 當 domain 層,只新增其他層。** 換到「不動既有習慣」。
否決理由:那等於留著一份沒有 authority、沒有 status、沒有證據的正本,
與新的 `knowledge/domain/` 形成雙正本,而雙正本必然漂移。

## Consequences

**換到:**
- 同一個專案在 Mac / Windows / Linux 是同一個 `project_id`,記憶內容相同。
- 本機索引可以整包刪掉重建;砍掉不損失 durable 記憶(有 integration test 釘住)。
- Git 樹裡的記憶是人看得懂、review 得動的結構化文字,不是二進位 blob。
- secret 與絕對路徑在固化前被擋下,不會因為記憶而被 push 出去。

**付出:**
- clone 之後必須先跑一次 `dev-setup` 才有檢索能力(空索引時查詢會回
  `NO_RELIABLE_MATCH`,不會假裝有答案)。
- **`.dev-flow/`(進 Git)與既有的 `.devflow/`(本機執行期暫存、gitignored)
  只差一個連字號** —— 這是本決策已知且刻意接受的命名風險。緩解:指南 `#memory`
  的三目錄對照表、`check-memory-architecture.sh` 機械驗 `.gitignore` 兩邊的狀態、
  以及 `DEVFLOW_MEMORY_DIR` 這個單點覆寫通道供採用專案改名。
- 記憶的寫入變得吝嗇(低訊號一律不進 Git),代價是「什麼算高訊號」這份清單
  住在程式碼裡,要擴充就要改碼並經 review —— 這是刻意的,不讓 runtime 自行決定。
