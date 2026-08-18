# 派工單：STATUS 寫入紀律拆「動作」與「落點」＋ 第 7 型補實例二

> **觸發句**：`讀 ~/dev/dev-flow/notes/dispatch-status-commit-landing.md 照它跑，全程不打斷問人`
>
> 本檔是**派工單**，讀完就照做。兩項都已裁決完畢，沒有要回頭問的事。
>
> **範圍極窄：只改措辭與一條守衛要點，不碰任何演算法、不動 Stage 1–4 模板結構。**

---

## 這份要解決什麼

母版有三處假設「整合分支可以直接 commit」。這個假設在 owner 這台機器上就不成立 ——
`~/.claude/scripts/git-flow-guard.py`（全域 hook，不是 dev-flow 的）擋掉 `main`/`master`
上的非合併 commit，那是刻意設的護欄、不該拿掉。採用專案裝 branch protection 或
pre-commit hook 的更常見。

實際踩到的樣子（2026-08-18 反證輪）：收尾表寫「第 4 步：在 main 上追加 HISTORY ＋ commit」，
執行輪被擋，只好自己開一條 branch 繞過去 —— `0d1ebe0` commit → `419b957` merge 就是
繞的痕跡。owner 同一輪自己也撞了三次，每次都要重開 branch 再 commit。

**根因不是筆誤，是母版把「手段」寫成了「規則」**：規則真正要的是「窗口最短」
（防兩個 session 靜默互蓋），「直接 commit」只是達成它的手段之一，卻被寫死成規則本身。

母版該規定的是**動作與順序**（改哪一列、什麼時候寫、要不要立刻推），
不該規定 **commit 落在哪條 branch** —— 那是各專案 git 紀律的事。

---

## 硬約束

0. **開工第一件事**：從 `main` 開工作 branch `docs/status-commit-landing`，
   不要在 `main` 上直接動手。做完 `git merge --no-ff` 回 `main`。
1. **不打 tag、不發 release。push 由 owner 自己跑。**
2. **不准 bump 版號**（維持 3.8.0，兩處都不要碰）。理由同前兩輪：v3.8.0 **無 tag、
   無 GitHub release**，對外還不存在，本輪續編進同一版。
   ⚠️ 這條只在「v3.8.0 仍未 tag 未 release」時成立；哪天發了就不能再續編。
3. **`main` 上不准直接 commit**（會被 git-flow-guard 擋）。HISTORY 追加也一樣：
   開一條短命 branch → commit → `merge --no-ff` 回 `main`。這正是本輪要修的東西，
   執行輪自己先照做。
4. **不准新增產品檔**（本檔以外）。
5. `docs/dev/HISTORY.md` 只能用 `scripts/history-append.sh` 追加。
6. **不准為了讓某個檢查變綠而放寬它。**

---

## F-1〔中〕把「動作」與「落點」拆成兩層

### 要改的四處（行號為 2026-08-18 實查值，動手前自己再確認一次）

| # | 檔案:行號 | 現在寫什麼 |
|---|---|---|
| a | `_templates/STATUS.md:32` | `「只改自己那一列 → 立刻 commit → 立刻推」一氣做完,不要改完放著。` |
| b | `docs/dev/STATUS.md:15` | 同一句（母版自套；S-1 的對帳守衛要求兩份要點一致，所以一起改） |
| c | `README.md:529` | `尚未開 feature branch 的規劃階段(1-5),文檔 commit 直接落 develop` |
| d | `guides/guide-dev-flow.html:1217` | 上一條的手寫鏡像卡片：`Stage 1-5 規劃階段文檔可直接落 develop` |

⚠️ **d 很容易漏**：那張卡片是手寫的、不是 renderer 產出的
（`render-methodology-corrections.sh` 只追 README Stage 6 seam 與 7-review Exit Checklist）。
只改 README 不改 guide 就是第 7 型的教科書案例，而且**沒有守衛在比對這兩處**。

### 改成什麼（語意要到，各檔照自己的格式寫，不要硬套同一段文字）

```
【動作】只改自己那一列 → 立刻落地 → 立刻推，不要改完放著
【落點】commit 走哪條路徑依專案 git 紀律：
        · 允許直接 commit 整合分支 → 直接做
        · 有護欄擋直接 commit（branch protection / pre-commit hook）
          → 開一條短命 branch → commit → 立刻 merge --no-ff 回整合分支
        兩種都要滿足「窗口最短」這個真正的要求
```

**「窗口最短」這四個字要逐字出現在 a、b 兩處**（見 F-1-e，守衛會釘它）。

c、d 兩處同理：把「文檔 commit 直接落 develop」改成「文檔 commit 落在整合分支
（`develop`）上；該分支有護欄擋直接 commit 時，走短命 branch → `merge --no-ff`
回去，不要因此把文檔混進 feature branch」。

### F-1-e 守衛：`scripts/check-status-policy.sh` 的 POINTS 補一條

**⚠️ 先更正一個假設**：owner 原本以為 POINTS 釘了「只改自己那一列 → 立刻 commit → 立刻推」，
改措辭會讓它紅。**實查不是**（`scripts/check-status-policy.sh:97-102` 原文）：

```python
POINTS = [
    ("只在整合分支維護", ["只在整合分支", "不碰本檔"]),
    ("改前 pull --ff-only", ["pull --ff-only"]),
    ("push 被拒走 rebase 重放並核對列集合", ["rebase", "列集合"]),
    ("禁 force push / reset --hard", ["push --force", "reset --hard"]),
]
```

四條裡**沒有任何一條**指向「立刻 commit」或寫入窗口。所以：

- 好消息：改措辭不會讓守衛紅。
- 壞消息：**owner 最在意、說「一定要留著」的那個要求，現在一個守衛都沒有**——
  今天有人把「立刻推」整句刪掉，`check-status-policy.sh` 全綠。

所以本輪補一條：

```python
    ("寫入窗口最短", ["窗口最短"]),
```

放在既有四條之後。它會要求 `_templates/STATUS.md` 與 `docs/dev/STATUS.md`
**兩份頂註**都含「窗口最短」四個字。

**連帶（這個 repo 每次都在這裡咬人）**：

1. 補 POINTS 會讓 `check-status-policy.sh` 的檢查數增加 → 它自己的 `MIN_CHECKS` 要調高。
2. `scripts/test-architecture-guards.sh:1541` 逐字互釘那一行（現為 `"MIN_CHECKS = 30"`）
   要同一個 commit 一起改。
3. **數字以實跑輸出為準**，不要照本檔算。
4. 既有 POINTS 有沒有配對的負向案例？照既有寫法給新這條也補一個
   （把兩份頂註之一的「窗口最短」拿掉 → 必須紅）。**沒有負向的守衛一律當成沒做。**

### F-1 驗收

- `bash scripts/check-status-policy.sh` 全過，項數比 30 多
- **破壞實驗**：`_templates/STATUS.md` 頂註的「窗口最短」拿掉 → 必須紅；
  `docs/dev/STATUS.md` 那份拿掉 → 也必須紅（兩份各試一次，做完還原）
- `bash scripts/test-architecture-guards.sh` 全過（地板互釘同步了）

---

## F-2〔低〕README 第 7 型補實例二

**位置**：`README.md:302-312`（`- **不對稱記帳(第 7 型)**:` 那一整條）

**不做守衛**，理由（owner 已裁決）：

| 為什麼不做 | |
|---|---|
| 機械判定不出來 | 什麼算「分解式」？`# 22 + 17 + 36 + 2` 算，那 `# 見 A、B、C 三處` 算不算？訂窄了沒用，訂寬了天天假陽性 |
| 通則早就有了 | 該節已寫著「沒有守衛釘著的清單不得寫死數字」—— 註解裡的分解正是這條的實例，不是新規則 |
| 成本不對等 | 為一個「只會誤導人、不會讓檢查變綠」的問題做守衛，投資比損害大 |

**修法**：在該條現有的實例（hooks 掛載 6 條 vs 健檢清單 5 條）之後補第二個實例。
內容語意如下，措辭可依 README 行文微調：

> 實例二：`check-file-map.sh` 的註解寫過「77 = hooks 22 + observability 17 +
> scripts 36 + tests 2」，常數從 77 調到 78 時分解沒跟著改，而且那個分解在調整之前
> 就已經算錯（hooks 實際 25、scripts 實際 34）。守衛比的是常數不是註解，錯的分解
> 照樣全綠，但下一個做同樣記帳的人會照著它算。通則的延伸：**註解裡的分解式也是
> 「為了驗證而列舉的清單」，同樣受本條約束 —— 沒有守衛釘著就不要寫，要數字就跑一次。**

⚠️ **不需要動 `guides/guide-dev-flow.html`**：實查該檔只有一處提到「第 7 型」，
而且是在檔案地圖表格裡描述某支守衛，**不是** README §7 這節的鏡像。加這段不會造成正副本不一致。
（動手前自己再 `grep -c "第 7 型" guides/guide-dev-flow.html` 確認一次，實查值 = 1。）

---

## 做完之後的驗收（全部都要跑，輸出貼進回報）

```bash
bash scripts/check-status-policy.sh                    # 全過,項數比 30 多
bash scripts/test-architecture-guards.sh               # 全過(地板互釘同步)
bash scripts/devflow-check.sh all                      # REPO_REFERENCE_PASS 全過
bash hooks/selftest.sh                                 # 378/378(本輪不該動到它)
env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
bash hooks/devflow-exec.sh doctor                      # COMPATIBLE
bash scripts/render-methodology-corrections.sh --check  # 綠(本輪不動被追蹤的兩個來源,不該紅)
bash scripts/check-no-stale-paths.sh                   # 綠
```

另外確認：

- `git status --short` 為空（破壞實驗都還原了）
- **版號仍是 3.8.0**（`.claude-plugin/plugin.json` 與 `hooks/runtime-capabilities.json` 兩處）
- `git diff --stat` 只含：`_templates/STATUS.md`、`docs/dev/STATUS.md`、`README.md`、
  `guides/guide-dev-flow.html`、`scripts/check-status-policy.sh`、
  `scripts/test-architecture-guards.sh`（＋收尾的 `docs/dev/HISTORY.md`）
- **`docs/dev/STATUS.md` 的 Active 表與 Backlog 一列都沒動**（本輪只改頂註的規則段）

### ⚠️ 本輪要動 `docs/dev/STATUS.md`，跟「STATUS 只在整合分支維護」的規則相衝

處理方式（比照 v380-blockers 輪的 bootstrap 例外，並在 HISTORY 寫明）：

- 本輪只改**頂註的規則段**，**不碰 Active 表**——該規則要防的是 Active 表的靜默互蓋，
  頂註不是那個競爭資源。
- 目前只有一條 branch 在跑，不存在該規則要防的衝突。
- HISTORY 那筆要寫一句「本輪在 feature branch 上改了 docs/dev/STATUS.md 頂註，
  理由同上，僅限頂註規則段」。

---

## 收尾（有先後順序）

| # | 做什麼 | 在哪條 branch |
|---|---|---|
| 1 | 完成 F-1、F-2 ＋ 所有破壞實驗 | `docs/status-commit-landing` |
| 2 | 切回 `main`，`git fetch origin` ＋ `git pull --ff-only origin main`；不通過就停 | `main` |
| 3 | `git merge --no-ff docs/status-commit-landing` | `main` |
| 4 | 用 `scripts/history-append.sh` 追加一筆，`--version` 帶 **`v3.8.0`**；**commit 那一步走短命 branch → `merge --no-ff`**（`main` 上直接 commit 會被 git-flow-guard 擋） | 短命 branch → `main` |
| 5 | **從最終的 `main` HEAD 重跑一次上面全套驗收** | `main` |
| 6 | **停下回報，請 owner 跑 `git push origin main`** | — |

---

## 不要做

- 不要改任何守衛的演算法（本輪只加一條 POINTS 要點）
- 不要為「註解分解式」做守衛（owner 已裁決不做，只補 README 實例）
- 不要 bump 版號、不要打 tag、不要發 release
- 不要動 `docs/dev/STATUS.md` 的 Active 表或 Backlog
- 不要回頭改 `notes/dispatch-v380-counterproof.md`（歷史檔沒有讀者，教訓已併進本檔）
- 破壞實驗**一定要還原**，收工前工作區必須乾淨

## 回報格式

1. F-1 / F-2 各一段：改了哪些檔（`檔案:行號`）、改前改後原文對照。
2. 驗收那八道的輸出原文全貼。
3. **破壞實驗逐個列**：F-1-e 的兩個（兩份頂註各拿掉「窗口最短」一次）。
   每個寫「弄壞什麼 → 有沒有真的變紅」。**沒做破壞實驗的守衛一律當成沒做。**
4. `check-status-policy.sh` 的 `MIN_CHECKS` 從幾改到幾，兩處（守衛自己＋靜態互釘）都貼證據。
5. 有沒有發現本檔沒提到的問題 —— 列出來問，**不要自己動手**。

**每一個結論都要對應到你自己實際跑過的指令與看到的輸出。**
沒跑過的就寫「未驗證」，不准用推論代替。
