# 採用現場回饋 — 母版待修清單（2026-08-04）

**來源**：四個既有專案（report-system / python_scheduling_system / CRM icryobank-crm-api-golang /
python-prism）從舊世代模板遷移到 `2c36976`（= `devflow-pilot-v2`，plugin v2.5.0 @ `f924723`）
的實作過程，加上一輪 29 個 agent 的對抗式查證（`wf_13b7a29b-ca5`，2,044,348 subagent tokens）。

**性質**：全部是**採用端撞到的母版問題**，不是專案自己的錯。每一條都附實跑證據與行號。
本檔只記問題與建議修法，**未動任何母版檔**。

**狀態**：待處理。rick 2026-08-04 指示「先寫進母版 repo，之後一起處理」。

> **第二輪追加（2026-08-07）**：CRM order-intake 走完整條 Stage 6→7 之後又撞到五條 A 級、
> 三條 B 級、一條 C 級，見本檔後半的〈第二輪〉。其中 **A-7～A-10 已當場修好並 commit**
> （母版 `bf0b8bf`、plugin `41ca267`），**A-11 未修**，B-5～B-7／C-3 待裁決。
> 第一輪的 **A-0 仍未修**，並在第二輪取得追加實測（見下方追加段）。
>
> **第三輪追加（2026-08-14）**：ivf_platform（`pgs-report-batch-scope`，fast lane）撞到
> 一條 A 級、兩條 B 級 —— **A-13**（`start` 把 gitignore 已忽略的檔也算 scope 外髒檔，
> 有本機開發目錄的專案一律啟動不了，**Stage 6 因此卡住**）、**B-8**（gate twin 沒有審查
> 介面規格，2026-08-13 只修了 7-review 沒推廣到 G1／G2）、**B-9**（「每 S 有觀測欄」是
> 模板明文完成條件卻無機械檢查，實測 16 個 S 中 5 個缺欄仍走到 G2）。三條**皆未修**，
> 見本檔〈第三輪〉。
> owner 2026-08-14 指示「寫進優化項目供後續處理，dev-flow 的修改另開 session 做」。

---

## 分級

| 級 | 意思 |
|---|---|
| **A** | 讓方法論規則在採用專案**失效**（規定了做不到的事，或守衛實際不守） |
| **B** | 讓採用者**踩坑後才發現**（無文件警告、無機械檢查） |
| **C** | 文件層不精確，不影響執行 |

---

## A-1 — `docs/dev/README.md` 是母版根 README 的逐字複本，帶進 23 條死引用 + 一個跑不了的 CI 入口

**兩個專案的 session 獨立踩到同一件事**（report-system 與 python_scheduling_system），
且各自算出證據後**都推薦同一個解法**。

### 最嚴重的一句

母版 `README.md:23`：

```
- `scripts/` = 機械檢查(單一入口 `devflow-check.sh all`;方法論/契約/架構守衛各腳本…)。
  CI 只跑這支 = REPO_REFERENCE
```

而 `README.md:16` 宣告「**本 README = 制度正本**」。

散發後的實況：

```
/Users/asheng/dev/dev-flow/scripts/devflow-check.sh          存在
report-system/scripts/devflow-check.sh                       不存在
python_scheduling_system/scripts/devflow-check.sh            不存在
```

→ **制度正本規定了一個採用專案根本跑不了的 CI 入口。** 這不是美觀問題，是規則失效。

### 死引用 23 條（python_scheduling_system session 逐條列出，行號為散發後的 `docs/dev/README.md`）

| 行號 | 路徑 | 指向 |
|---|---|---|
| L18, L578 | `example/contract-expiry-reminder/` | 母版的完整範例 feature |
| L88 | `example/` | 同上（目錄） |
| L390 | `example/contract-expiry-reminder/5-tasks.md` | 同上 |
| L23 | `scripts/` | 母版機械檢查腳本目錄 |
| L24 | `devflow-evidence-gauntlet.sh` | 母版 `scripts/` 下那份（採用專案在 `docs/dev/tools/`） |
| L112, L389 | `scripts/check-design-contract.sh` | 母版守衛腳本 |
| L356, L398 | `scripts/devflow-evidence-gauntlet.sh` | 同上 |
| L386, L396, L397 | `scripts/check-methodology-corrections.sh` | 同上 |
| L388 | `scripts/check-task-slicing.sh` | 同上 |
| L393 | `scripts/check-adr-integrity.sh` / `check-version-sync.sh` / `check-gate-tokens.sh` | 同上（3 條） |
| L28 | `notes/design/` | 母版設計正本目錄 |
| **L111** | `notes/design/design-boundary-contract.md` | **唯一一條真 markdown `[]()` 連結，點了 404** |
| L389 | `notes/design/design-boundary-contract.md` | 同檔（反引號） |
| L197, L220 | `notes/design/parallel-stage6.md` | 母版設計正本 |
| L447 | `notes/design/agent-attempt-observability.md` | 同上 |
| L26 | `observability/` | 母版 Attempt Ledger 工具 |
| L403 | `observability/devflow-obs.py` | 同上 |
| L27 | `tests/parallel-stage6/` | 母版並行契約測試 |
| L387 | `tests/parallel-stage6/contract_ref.py` | 同上 |
| L290 | `evidence/` | 母版 7-review 截圖目錄慣例 |
| L198, L211 | `guide-quickstart.html` | 母版 HTML 導覽 |
| L177 | `dev-setup-record.html` | 母版說明書 |

**不是死引用、不列入**（該 session 已分層）：

- 層 B（12 條）：`hooks/devflow-exec.sh`、`hooks/selftest.sh`、`hooks/_stage3_impl.py` 等 ——
  真的存在，在 `CLAUDE_PLUGIN_ROOT`（`~/.claude/plugins/cache/dev-flow-plugin/dev-flow/2.5.0/hooks/`），
  只是相對 repo root 解析不到。
- 層 C（2 條）：`docs/adr/NNNN-slug.md`（命名慣例佔位）、`.devflow/exec.json`（runtime 生成）。

### 惡化時點

`91e1f2c`（舊版）散發出去的 README 只有 **2 處**母版自有資產引用（L59、L286）。
母版 8/4 版新增的 §「怎麼逛這個 repo」（L14–29）與 §7「強制力對照(誰在擋)」（L383–404）
**兩節都是母版 repo 的內部導覽** —— 從 2 條放大到 23 條是這次進來的。

### 建議修法

**散發時剝除或改寫 repo-internal 路徑**，而不是要專案端自己加說明。

兩個 session 都明確反對「在專案端加在地說明段」，理由一致且正確：

> 那會讓 `docs/dev/README.md` 與母版 blob 不同，直接破壞 `dev-setup check` 第 6 項的 diff 比對 ——
> 以後每次 upgrade 都會看到假 stale，這代價比死連結高。

具體選項：

1. **散發器改寫**（推薦）：`dev-setup` install/upgrade 在 `cp` README 時，把 §「怎麼逛這個 repo」
   與 §7 表中的 repo-internal 路徑改成絕對路徑 `~/dev/dev-flow/scripts/…`，或整節剝除。
2. **母版拆兩份**：`README.md`（母版 repo 用，含導覽）與 `README-distributed.md`（散發用，
   無 repo-internal 路徑）。代價是兩份要同步。
3. **母版 README 內把 repo-internal 段落標記成可剝除區塊**（如 HTML 註解夾住），散發器按標記剝。

無論選哪個，`scripts/devflow-check.sh` 那句必須處理 —— 採用專案沒有那支腳本，
它們的機械檢查入口是 `docs/dev/tools/devflow-evidence-gauntlet.sh` + 外部 plugin 的 doctor。

---

## A-2 — `_gate_impl.py` 的 `s_id_present` 在實務上恆真，ID 鏈在 gate 上完全失效

python-prism session 的最大發現，我已獨立複驗。

```python
# _gate_impl.py:133-134
def _s_ids_of(covers):
    return re.findall(r"S-\d+", covers)      # ← 帶連字號、只到整數
# :202  "s_ids": _s_ids_of(tdef["covers"])
# :86   "s_id_present": bool(names) and all(_sid_matched(sid, names) for sid in task.get("s_ids", []))
```

但母版模板與實務一律寫**點號無連字號**形式：`S1.1`、`S13.6`、`S1.1–S1.4`。

實跑（python-prism，18 個 T）：

```
T-2 covers='R1 / S1.1–S1.4、R2 / S2.1、S2.5、R3 / S3.1–S3.2'  -> s_ids= []
T-4 covers='R15 / S15.1–S15.4'                                -> s_ids= []
…18 個 T 全部 s_ids=[]
```

空 list 上的 `all()` 恆為 `True` → **只要 `test_names` 非空就 PASS**，等於這個檢查什麼都沒驗。

**後果**：母版模板 `5-tasks.md` 與 `4-spec.md` 都寫「測試名必須含 S-id，否則 7-review 的 coverage
對不起來」。採用者合理相信 gate 會擋 —— **它不會**。

**建議修法**（三選一，需決策）：

1. 放寬正則到 `S-?\d+(?:\.\d+)?`，同時吃 `S-13` 與 `S13.6`。最小改動，但要確認 `_sid_matched`
   對測試名的比對規則也跟著放寬。
2. 母版統一把 Covers 的寫法改成 `S-13.6`。代價：與 4-spec 自己的 `S13.6` 分歧，且要改全部模板與範例。
3. 明文承認「coverage 對帳是人工步驟」，把 `s_id_present` 從 `GATE_CHECK_IDS` 移除，
   README §7 的強制力對照表相應改成「人工」。

⚠️ 選 3 也要動，因為現況是「表上寫機械、實際不機械」—— 那是 README §7 的正確性問題。

---

## A-3 — `verify_command_match` 字串全等 + `FIELD_RE` 只吃行尾，但模板沒有任何警告

```python
# _gate_impl.py:83-84
"verify_command_match": (isinstance(verify, dict)
                         and verify.get("command") == task.get("verify")),   # 字串全等
# devflow-lib.py:258-260  FIELD_RE 以 $ 結尾 → 只吃到行尾，續行不進欄
```

實測：python-prism 18 個 T 有 **17 個** 的 `Verify:` 欄被中文說明汙染（同一行寫指令 + 說明），
例如 `'pytest -k "S4_ or S3_4"`；S4.1 需實檔（3.9 GB BAM），'`。
CRM order-intake 26 個 T 原本則是把 Verify 寫成多行 ` ```sh ` fenced block，
`FIELD_RE` 一個字都抓不到。

**兩種寫法都是採用者的自然直覺，而且母版 `_templates/5-tasks.md` 沒有任何一句警告。**

建議修法：

1. `_templates/5-tasks.md` 的欄位說明加一條硬性紀律：
   「`Verify:` 必須是**單行、可原樣貼進 shell 的純指令**；說明、期望輸出、前置動作一律寫在下一行。」
2. 加一個機械檢查（可放進 `scripts/devflow-check.sh` 或 gauntlet）：掃 5-tasks 的每個
   `Verify:` 欄，若含非 ASCII 字元或以 ` ``` ` 開頭則 FAIL。
3. 順帶提醒 `#` 會吞掉單行其後全部內容 —— 壓成單行時的已知陷阱。

---

## A-4 — gate 的 RED/GREEN/verify 三項無條件必檢，純 migration / infra 型 T 無法通過

```python
# _gate_impl.py:26  GATE_CHECK_IDS 含 red_present_failing / green_present_passing / verify_exit_zero
# :78-85 三者無任何 task 型別判斷、無 per-task 豁免
"red_present_failing":   isinstance(red, dict) and red.get("exit_code") not in (0, None),
"green_present_passing": isinstance(green, dict) and green.get("exit_code") == 0,
"verify_exit_zero":      isinstance(verify, dict) and verify.get("exit_code") == 0,
```

python-prism 的 T-1（純 alembic migration，Verify 原本是
`alembic upgrade head && psql -c "\d+ ngs_backup_file"`）**產不出 RED→GREEN 證據，第一個 T 就卡死**。

現場解法是給 T-1 補一支驗 schema 形狀的 pytest（`5cdca37`），可行，
但**母版完全沒說 infra 型 T 該怎麼辦**，每個採用專案都會自己撞一次。

建議修法：`_templates/5-tasks.md` 或 README §5 明文規定
「每個 T 都必須有一個能 RED→GREEN 的測試；純 migration / infra 型 T 要配一支驗形狀的測試
（表存在、欄位型別、索引、約束），不能只寫執行指令」，並在範例裡放一個 infra 型 T 示範。

---

## A-5 — Files scope 不含測試路徑會在**寫入當下**被 hook 殺掉，模板沒提醒

```python
# _guard_impl.py:92-98
if L.in_pool(rel, state):
    sys.exit(0)
_obs_deny("guard-write", "scope", rel)
L.die(... "⛔ scope 外寫入:{rel} 不在 5-tasks Files 聯集" ...)
# in_pool / in_scope 規則：exact match，或結尾 `/` 才做 prefix match
```

python-prism 18/18、CRM order-intake 26/26 的 `Files:` 欄**都不含測試路徑**，
而幾乎每個 T 的 Verify 都是跑測試（必然要寫測試檔）。

失敗點**不在 gate，在 PreToolUse hook** —— worker 一 `Write tests/…` 就 die，
走不到產 candidate、更走不到 gate。

`extra_allowed` 有兩套逃生門，但**都要逐項配置且不持久**：

- gate 側 `_gate_impl.py:204`：來自每次呼叫的 `--extra` 旗標
- 寫入側 `devflow-exec.sh allow <file> --reason "..."`（`_exec_impl.py:444-470`）：逐檔追加進 `exec.json`

建議修法：`_templates/5-tasks.md` 的 `Files:` 欄說明加一句
「**測試檔路徑也要列進來** —— worker 寫測試就是寫檔，不在 Files 聯集內會被 guard 擋死」，
並在範例的每個 T 都示範。

---

## A-0 — `git_dirty_paths()` 帶 `--ignored=traditional`，讓 `start` 在**四個 repo 全部**啟動不了

**最嚴重的一條。** CRM order-intake 的 Stage 6 執行者撞到，我實測確認**四個採用 repo 全中**。

```python
# devflow-lib.py:47-51
def git_dirty_paths(root):
    """Return every changed repo-root-relative path from porcelain v1, including rename sources."""
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "-uall", "--ignored=traditional"],
        cwd=root, capture_output=True, text=True)
```

`--ignored=traditional` 把**所有 gitignored 檔案**列出來，`-uall` 再逐檔展開。
這些檔案定義上就不是「未提交的工作」，卻全被當成 scope 外髒檔而 fail-closed。

實測（2026-08-05，四個 repo 全掃）：

| repo | `git status --short` | 帶 `--ignored=traditional -uall` | 主要來源 |
|---|---|---|---|
| **python-prism** | 0 | **62,597** | — |
| **python_scheduling_system** | 1 | **17,698** | — |
| **CRM icryobank-crm-api-golang** | 0 | **16,202** | `.claude/worktrees` 15,983 筆 |
| **report-system** | 6 | **3,771** | — |

CRM 的實際錯誤訊息：

```
⛔ 拒絕啟動:工作樹已有 16130 個 scope 外未提交改動(前 10):
  .claude/.harness-template-versions.json
  .claude/skills/generated/app/SKILL.md   …
```

而該 repo 的 `git status --short` 是 **0 行**。

**這代表 Stage 6 的寫入 scope guard 在這四個 repo 全部無法啟動** ——
不是「守衛太嚴」，是守衛根本進不了門。CRM 的 T-3 只能靠
「14 檔清單當派工硬約束 + 人工逐筆核 + reviewer 獨立再核」守住，機制是人工的不是工具的。

### 為什麼不能靠「清乾淨 gitignored 檔」繞過

- 那些檔案是**刻意 ignore 的產物**（harness 產生的 skills、gitnexus parse-cache、
  worktree 目錄、build 產物）。刪掉會弄壞工具鏈。
- 即使 CRM 清掉那 15,983 筆孤兒 worktree 目錄，剩下 219 筆仍 > 0，一樣 fail-closed。
- python-prism 的 62,597 筆更不可能清。

### 這行為看起來是刻意的，但代價不成比例

推測意圖：防止 worker 把產物寫進 gitignored 路徑來規避 scope 檢查。
但代價是**任何有正常 `.gitignore` 的 repo 都啟動不了**。

### ⚠️ 2026-08-05 實測：**選項 1（拿掉 flag）行不通，有兩個永久測試守著**

rick 核准後我實際改了 `git_dirty_paths()`（兩處副本同步），跑 plugin 自帶 selftest：

```
❌ 守衛自測 292/294,失敗 2 項:
   - 開跑前 ignored parent 有 meaningful sibling → 拒啟
     (期望 exit 1 且含 'ignored/nested/pre.txt',得 exit 0)
   - postbash ignored parent 的 meaningful sibling 仍擋
     (期望 exit 2 且含 'ignored/cache/source.py',得 exit 0)
```

測試出處 `hooks/selftest.sh:243-248`：

```bash
mkdir -p ignored/cache
echo "ds" > ignored/.DS_Store; echo "apple" > ignored/cache/._finder; echo "thumb" > ignored/cache/Thumbs.db
ck "postbash ignored parent 僅 ambient leaves 不擋" 0 "$(post)"
echo "meaningful" > ignored/cache/source.py
ck_msg "postbash ignored parent 的 meaningful sibling 仍擋" 2 "ignored/cache/source.py" ...
```

**已還原，selftest 回到 294/294 全過。** 兩份副本（cache 與 marketplaces checkout）都已還原、
marketplaces repo `git status` 乾淨。

### 這兩個測試揭露的真正設計意圖

設計不是「忽略 ignored」也不是「全擋 ignored」，而是**分兩類**：

- **ambient metadata**（`is_ambient_path()`：`.DS_Store` / `._*` / `Thumbs.db` / `*.pyc` / `__pycache__`）
  → 即使在 ignored 目錄下也放行
- **有意義的檔** → 即使在 ignored 目錄下也擋

問題在於 `is_ambient_path()` 的清單**只涵蓋 OS 與 Python 的噪音**，涵蓋不了真實專案的
gitignored 內容：`.claude/skills/generated/*.md`、`.gitnexus/parse-cache/*.json`、
`_local/erp-scripts/*.sh`、`.env`、`docker-compose.*.yml`、`ent/migrate/*` ——
這些按現行定義全是「有意義的檔」，但它們是**專案既有的正當檔案**，不是 worker 寫的。

### 修正後的建議修法（原選項 1 作廢）

1. ~~拿掉 `--ignored=traditional`~~ —— **實測會打破兩個永久測試，作廢**。
2. **只展開 scope 路徑底下的 ignored 檔**（原選項 2）—— 但實測發現它也過不了測試：
   測試的 `ignored/cache/source.py` 不在 scope（scope 是 `src/a.py` / `src/lib/`），
   所以這個修法會讓該測試也變成放行。**除非同時改測試。**
3. **✅ 推薦：把「已知噪音」變成可設定的**。`is_ambient_path()` 之外再加一層
   repo 級白名單（例如 `.devflow/ambient-globs` 或讀 `.gitignore` 中被明確標記的段落），
   讓專案宣告「這些 gitignored 路徑是既有產物，不是 worker 的產出」。
   selftest 的兩個案例不受影響（`ignored/cache/source.py` 不在白名單內 → 照樣擋）。
4. **或：把「開跑前既有的 ignored 檔」記進 baseline（只記路徑不記 hash）**，
   postbash 只擋「執行期間**新出現**的」。這能區分「既有噪音」與「worker 寫的」，
   但會讓 selftest 的第一個案例（開跑前拒啟）失效 → **要一併改測試**，
   而那些測試是守衛自我保護的一部分（2026-08-03 F-2 那輪刻意加的），
   動它要有明確理由。

**現況**：維持原行為。採用專案的 Stage 6 走**手動模式**
（Files 清單當派工硬約束 + 人工逐筆核 + reviewer 獨立再核），已在 CRM order-intake
的 T-1~T-4 驗證可行且抓到三個真問題（D-4 執行者繞過、D-11 新增邏輯零測試覆蓋、
`is_active` 檢查過寬）。加速靠**批次派工**（一次跑完一整條支線再 review）而非關掉守衛。

⚠️ 目前的錯誤訊息會誤導 —— 它說「未提交改動」，但列出來的是 gitignored 檔，
使用者第一反應是「這些不是我的，可以刪嗎」（實際案例）。無論選哪個修法，
訊息都該分辨這兩類。

### 追加實測（2026-08-07，CRM 走完 Stage 6+7 之後回頭查證）

**A-0 至今未修，且「清乾淨」這條路已被實測否定。**

CRM 那 15,983 筆孤兒 worktree 目錄後來清掉了，數字從 16,202 掉到 180 —— **仍然啟動不了**：

```
cd ~/dev/CRM/icryobank-crm-api-golang        # 唯讀查證，未跑 start
git status --porcelain=v1 -uall                        →   0 筆（工作樹乾淨）
git status --porcelain=v1 -uall --ignored=traditional  → 180 筆
  其中 !! (gitignored) = 180        真正的改動 = 0
  通過 is_ambient_path() 濾網後仍剩 156 筆   ← dirty_scan_and_baseline 只要 outside 非空就 die()
  前幾筆：.claude/skills/gitnexus/*/SKILL.md（6 筆）、.env、.gitleaksignore
```

**降幅 98.9%，結論不變** —— 因為判準是「> 0 就擋」，不是比例。這證明
〈為什麼不能靠清乾淨 gitignored 檔繞過〉那一節的推論成立，且對已經清理過的 repo 依然成立。

**補一條 A-0 原文沒點明的實作細節**（給修的人）：`git_dirty_paths()` 的 parser
**完全沒有讀 status code 的機會去濾 `!!`** ——

```python
# devflow-lib.py::git_dirty_paths
code, path = entry[:2], entry[3:]
paths.append(path)                      # ← 無條件 append
if "R" in code or "C" in code:          # ← code 只在 rename/copy 時被看
    ...
```

`code` 只被用來判斷 rename/copy 的來源路徑，`!!` 從未進入任何條件式。
且該函式的 docstring 寫的是「Return every **changed** repo-root-relative path」——
**實作與自己的契約不符**：`!!` 的項目按定義不是 changed。
修法若選 notes 原本推薦的選項 3（可設定 ambient 白名單），順手把 docstring 一起對齊。

**後果的實測規模**（第二輪新增的資訊）：order-intake 的 **26 個 T 全程守衛未武裝**，
圍欄②／契約防篡改／scope 三道一次都沒觸發。6-notes 與 7-review 裡寫的
「改動檔 ⊆ 5-tasks Files 聯集，零違規」是**人工 `git status --untracked-files=all` 逐筆比對**
得出的結論，不是守衛擋出來的 —— 而兩份文件都讀不出這個差別。這直接催生了 A-7。

---

## A-6 — `Boundaries:` 欄被解析後直接丟棄，不進 task dict

```
FIELD_RE 收：Covers|Files|Verify|Blocked-by|Integrate-after|Risk|Review-mode|
             Semantic-conflicts-with|Intent|Boundaries|Owner
實際 task dict keys：id, title, covers, files, verify, blocked_by,
             integrate_after, semantic_conflicts, risk, review_mode
                     ← Boundaries / Intent / Owner 全部沒進去
```

`_exec_impl.py` 全檔提到 `Boundaries` 只有一處，在 `:286` 的錯誤訊息字串裡（「常見成因：`Boundaries:`
／`Intent:` 續行寫成…」），**零實質使用**。

它只是 `skills/dev-run/SKILL.md:188` 對派工者（人/主模型）的 prompt 紀律。

**但母版文件把它寫得像機械契約**（`_templates/5-tasks.md` 有 7 處提到 `Boundaries:`，
`4-spec.md` 的 Design Boundary Contract 節也預設它會被承接）。
採用者會誤以為「寫成 `Boundaries:` 就會被 runtime 帶進派工」—— 不會。

建議修法：要嘛 runtime 真的把它帶進 task dict 與派工 prompt，要嘛母版文件明說它是人工紀律。
現況兩邊對不上。

---

## B-1 — 母版自己的 `_templates/5-tasks.md` 過不了 `parse_5_tasks`

report-system session 發現：母版 2.5.0 的 `_templates/5-tasks.md` 模板本身丟進
`parse_5_tasks` 會出錯（T-2 範例欄位留空）。

不影響採用（沒人會 parse 模板），但若日後把 parser 拉進 CI 對模板做自檢就會紅。
順手修比較好。

---

## B-2 — `dev-setup` 的 diff 摘要沒讓使用者看見細粒度覆蓋，在地客製被靜默沖掉

python_scheduling_system 實例：`docs/dev/_templates/arch-invariants.md` 的範例句
原本已在地化成排班語境「排班結果會用到舊資料」，被 upgrade **靜默還原**成母版通用版
「計算結果會用到舊資料」。

該 session 掃過全部 11 個受影響檔後確認**只有這 1 處**（其餘 60 條「舊有新無」都是母版自己改寫），
且判定不需救回（`.claude/rules/arch-invariants.md:98` 已有同義的真規則）。
所以本例影響小 —— 但**機制問題是真的**：使用者按下「全部升級」時看不到自己的在地修改要被沖掉。

建議修法：`dev-setup upgrade` 的 diff 摘要要能分辨
「母版改寫」與「本地客製被還原」兩類，後者要單獨列出來徵得同意。

---

## B-3 — lane 判準與 owner 指示衝突時，母版沒說怎麼辦

report-system 開第一個 2.5.0 feature（`test-cleanup-pool-close`）時撞到：

- **按母版判準這題是 fast lane** —— bugfix、production 0 行改動、test 30-40 行。
- **但 owner（rick）指示「開 Stage 1」＝走 full**，而且 owner 釘死的驗收條件裡有兩項
  （`Required layers`、`Design Boundary Contract`）**是 full lane 專有欄位**，
  fast lane 的 4-spec 只有 `Verify:`。

該 session 的處置是照做 full、但把偏離記進 `STATUS.md` 與 `0-draft-owner-constraints.md`。
處置正確，但**母版沒有任何一句規定這種衝突該怎麼記、要不要記、記在哪**。

建議修法：README §5 或 `_templates/4-spec.md` 的 Verification Profile 節加一句
「lane 由判準決定；owner 指示與判準不同時，**必須在 Verification Profile 明記偏離與理由**
（往嚴的方向偏離也要記）」。

---

## B-4 — `doctor` 對 gauntlet 只做 `--version` 探測，不驗 ROOT 解析

母版的 gauntlet 在 `scripts/`（ROOT = repo 根），散發到採用專案的 `docs/dev/tools/`（ROOT 會變成
`docs/dev/`）。`_doctor_impl.py:172` 只比對 `--version` 字串，
發現不了散發副本因目錄深度不同造成的 ROOT 解析差異。

目前無實害（gauntlet 全 19 個 fixture 在 report-system 實跑正常，正負向都對），
但檢查沒覆蓋到這個面向。

---

## C-1 — `skills/dev-setup/SKILL.md:8` 的 plugin 路徑已與實際脫鉤

```
SKILL.md:8  「架構:skills 與 hooks 隨 plugin 全域生效(`~/.claude/plugins/local/{dev-talk,dev-flow}/`,…」
實際生效     ~/.claude/plugins/cache/dev-flow-plugin/dev-flow/2.5.0/
             （2026-08-04 marketplace 轉正，installed_plugins.json 已無 dev-flow@local）
```

其中 **dev-talk 那半句不是錯的** —— `known_marketplaces.json` 的 `local` marketplace source
是 directory `/Users/asheng/.claude/plugins/local`，`dev-talk` 的 source 是 `./dev-talk`，該目錄存在。
所以只有 dev-flow 那半句脫鉤。

**母版範圍更大**：`git grep -n "plugins/local"` 於 `~/dev/dev-flow` 命中 **40+ 行**，含
`README.md:370`、`.github/workflows/devflow-ci.yml:8`、`guide-dev-flow.html:526,680,843,846`、
`guide-quickstart.html:109,362,363,395,532,825`、`dev-setup-record.html` 七行、
`docs/prompts/devflow-vnext-runtime.md:50,369` —— 全部把 dev-flow 指向 `~/.claude/plugins/local/dev-flow/`。

⚠️ **`~/.claude/plugins/local/dev-flow` 不是「過期舊副本」** —— 查證證實它與 cache 版
**原始碼 byte-identical**（`diff -r --brief` 只差兩個 `__pycache__` 條目），
而且它是**唯一帶 `.git` 的那份**（cache 沒有）。當成垃圾刪掉會毀掉 plugin 的 git checkout。

---

## C-2 — `docs/dev/README.md` 的 gauntlet 路徑三處

report-system session 分層：

| 行 | 內容 | 判讀 |
|---|---|---|
| `:24` | 描述母版 repo 自己的 `scripts/` 目錄內容 | **不是 bug** —— 在講母版結構 |
| `:356` | `scripts/devflow-evidence-gauntlet.sh`，但同句已帶「採用專案散發於 `docs/dev/tools/`」 | 輕微，已有註解兜住 |
| `:398` | **G3 強制力對照表，裸寫 `scripts/devflow-evidence-gauntlet.sh` 無任何註解** | **真正會誤導的那處** —— Stage 7 執行者就是看這一列去找腳本 |

隨 A-1 一併處理。

---

# 第二輪 — order-intake 走完 Stage 6→7 的現場回饋（2026-08-07）

**來源**：CRM `icryobank-crm-api-golang` 的 `feature/order-intake`，從 T-13 一路做到 T-26 收尾
＋ Stage 6 Self-Review ＋ Stage 7 產出（`7-review.md` + 2.3MB `7-review.html`）。
規模：**26/26 個 T、109/109 個 S、約 160 刀突變測試、41 個 Deviation（全 L1、零 L2）**。
這是**第一個走完整條 Stage 6→7 的 feature**。

**性質**：同第一輪 —— 採用端撞到的母版問題，每條附實跑證據。
差別是這一輪撞到的多半是**只有走到 Stage 6 尾聲與 Stage 7 才會顯形**的東西：
Stage 1～5 與 Stage 6 前段都跑得很順，問題全在收尾與驗證層。

**與第一輪編號的關係**：沿用 A/B/C 分級與流水號，接在 A-6／B-4／C-2 之後。
（本輪 commit 訊息裡的內部代號 A1/A3/A4/A5 = 本檔的 **A-7/A-8/A-9/A-10**，勿混。）

| 本檔編號 | 一句話 | 查證 | 狀態 |
|---|---|---|---|
| **A-7** | 守衛「未武裝」與「沒在用 dev-flow」在系統裡無法區分 | ✅ 確認 | ✅ 已修 |
| **A-8** | `Verify` 用測試篩選器時零匹配也回 exit 0 → 印出 `PASS` | ✅ 確認 | ✅ 已修 |
| **A-9** | gauntlet 缺件時沒有人被擋 | ⚠️ **診斷更正**（見該節） | ✅ 已修（改對方向） |
| **A-10** | 4-spec 的「觀測方式」可以寫成本 repo 做不到的事，而它是 G3 的 PASS 條件 | ✅ 確認 | ✅ 已修 |
| **A-11** | Stage 7 的「禁讀 6-notes Self-Review」沒接到既有的圍欄機制 | ✅ 確認（+1 實作細節） | ⏳ **未修** |
| **A-12** | `dev-setup` 沒跑完整，而**沒有任何 Stage 要求跑 doctor** | ✅ 確認（原 C-3，**升級為 A**） | ⏳ **未修** |
| **B-5** | `Files` 欄系統性低估，模板沒有判準 | ✅ 確認（數字更正 8 → **10**） | 待裁決 |
| **B-6** | Diff Budget 沒有任何估法指引 | ✅ 確認（**比原判更嚴重**） | 待裁決 |
| **B-7** | ~~突變測試不在流程裡~~ | ❌ **原判錯誤，已改寫** | 見該節 |

> **2026-08-07 查證輪**：rick 要求逐條確認 A-11／B-5／B-6／B-7／C-3 是不是真缺陷。
> 結果：**三條確認、一條升級（C-3 → A-12）、一條原判錯誤（B-7）**，
> 並回頭發現 **A-9 的診斷是錯的**（見該節的更正段）。每條的查證指令都在條目內。

**已修的四條**：母版 `bf0b8bf`（模板 + `scripts/check-stage67-enforcement.sh` +
`test-architecture-guards.sh` 36→43 案）、plugin `41ca267`（`_guard_impl.py` 的一次性提醒）。
`scripts/devflow-check.sh all` 由 14 組變 **15 組全過**。

---

## A-7 — 守衛「未武裝」與「沒在用 dev-flow」在系統裡無法區分　✅ 已修

**這是 A-0 的下游後果，但它是獨立的缺陷**：就算 A-0 修好了，只要 `start` 因為任何理由
沒跑成功（忘了跑、跑錯 slug、stop 之後忘記重 start），同樣會靜默退化。

```python
# devflow-lib.py::load_state
if not os.path.exists(execp):
    if armed:
        return None, armed, ("⛔ ... 旗標檔消失但守衛仍武裝中 ...")   # 這條有訊號
    return None, "", ""          # 真的沒在執行 → 沉睡      ← 這條沒有
```

`_guard_impl.py:50` 拿到 `state is None` 就 `sys.exit(0)`。
對非 dev-flow 工作這是正確的（不能誤傷），但它讓兩種狀態產生**同一個可觀測結果**。

**實測後果**：order-intake 的 26 個 T 全程無守衛，而 6-notes／7-review 讀起來像有守衛。
**到 Stage 7 才被發現**，而且是因為有人去查 `.devflow/` 目錄是不是空的。

### 已採用的修法（2026-08-07）

**兩層，都刻意做窄**：

1. **模板層**（`_templates/6-implementation-notes.md`、`_templates/7-review.md` 的步 0）：
   加「守衛武裝自檢」硬關卡 —— 跑 `devflow-exec.sh status`、確認 `.devflow/exec.json` 存在、
   輸出貼進 6-notes；武裝不了就**停下回報**，不准用「我會自己守 scope」代替。
2. **hook 層**（`_guard_impl.py` 的 `state is None` 分支）：**一次性軟擋**。

```
觸發條件（刻意極窄）：tool ∈ {Write, Edit} 且 path 是
                      docs/dev/<slug>/{5-tasks,6-implementation-notes}.md
第一次 → exit 2，印出完整說明 + 三條出路，並寫 .git/devflow-unarmed-notified
第二次 → exit 0（放行，不再打擾）
非 dev-flow 檔 → 從不觸發
```

**⚠️ 為什麼是 exit 2 而不是 exit 0 + stderr**：PreToolUse 在 exit 0 時 stderr
**不保證送到模型或使用者眼前**。一個看不見的警告比沒有警告更糟 —— 它讓人以為有守衛。
這條在設計時被明確權衡過，寫進了 hook 的行內註。

實測（暫存 repo）：第一次 `rc=2` 訊息完整、第二次 `rc=0`、`main.go` 恆 `rc=0`。
`hooks/selftest.sh` **294/294 全過**（無回歸）。

**⚠️ 尚未生效**：改的是 `~/dev/dev-flow-plugin/hooks/`（源碼），
跑的是 `~/.claude/plugins/marketplaces/dev-flow-plugin/hooks/` 與各帳號的 cache。
**要重裝或同步 plugin 才會生效** —— 而「改了源碼、跑的還是舊的、沒有訊號」
正好是同一類問題的第三個實例（前兩個是 A-0 與 A-7 本身）。

---

## A-8 — `Verify` 用測試篩選器時零匹配也回 exit 0，於是印出 `PASS`　✅ 已修

**本輪最普遍的一條** —— 它影響**每一個** `Verify` 欄用 `-run` / `-k` / `--filter` 的 T。

`go test -run 'Test_X'` 在**沒有任何測試匹配**時回 `exit 0` 並印
`testing: warning: no tests to run` —— 於是「一個測試都沒跑」與「全部通過」
在 exit code 上完全一樣，而 `Verify` 欄是 `<指令> && echo 'T-n PASS'` 的形狀。

**實測（order-intake T-25，在還沒寫任何測試的 HEAD 上原樣跑該欄）**：

```
go test -tags=integration -p 2 ./internal/modules/laborder/order/... -run 'Test_S_18_2_' -v
  → === RUN 行數：0
  → exit code：0
  → 兩條 grep（pgconn.PgError / ConstraintName）本來就通過（既有程式碼就有）
  → 整條 Verify 印出「T-25 PASS」
```

**那一欄在補測試之前完全不具鑑別力。** 這不是實作者偷懶 —— 是欄位的形狀本身沒有牙齒。
（同一個 feature 另有三次「Verify 欄本身有問題」：D-26 欄位不可能成立、
D-33 照它做會製造真的 swagger 撞名、D-40 反向 grep 被自己的 swagger 註解命中。
三次都靠人在開工前原樣跑一次才發現。）

### 已採用的修法（2026-08-07）

`_templates/5-tasks.md` 加兩條**強制**條款：

1. **用篩選器就要自帶案例數斷言**，並給出可照抄的骨架：
   ```
   n=$(<測試指令> -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge <期望案例數> && <其餘檢查>
   ```
   期望案例數**開工前先寫下來**；`-ge 1` 是下限不是免死金牌。
2. **`Verify` 開工前必須原樣跑一次**（還沒動任何碼時），三種結果各有處置：
   ①已經綠 → 這欄不具鑑別力，補計數或改條件 ②不可能綠 → 停、修欄位、記 L1
   ③綠不了但方向對 → 正常開工。

**範例一併改正**：`example/contract-expiry-reminder/5-tasks.md` 的三條 `-run` Verify
全部換成帶計數的形狀 —— **範例才是實際被抄的東西**，只改模板註解沒有用。

守衛 `scripts/check-stage67-enforcement.sh` 逐行掃 `example/*/5-tasks.md`，
凡 `- Verify:` 用了篩選器卻沒有 `=== RUN` / `grep -c` 即紅。

---

## A-9 — gauntlet 缺件時沒有人被擋　✅ 已修（⚠️ 診斷經 2026-08-07 更正）

### ⚠️ 原始診斷（2026-08-07 上午）—— **錯了，留著當記錄**

> 「模板步 2c 把路徑寫死成 `docs/dev/tools/devflow-evidence-gauntlet.sh`，
> 而該目錄在採用專案不存在 → 路徑寫錯。」

### 更正後的診斷（2026-08-07 下午查證）

**那個路徑是對的，是 `dev-setup` 的散發契約**：

```
skills/dev-setup/SKILL.md:69
  6. **evidence gauntlet 散發**:`mkdir -p docs/dev/tools` 後 cp 母版
```

所以模板寫 `docs/dev/tools/...` **完全正確** —— 錯的是我。
**真正的缺陷是**：`docs/dev/tools/` 在 CRM 不存在（`dev-setup` 沒跑完整，見 **A-12**），
而**沒有任何一步會因此被擋**。

**後果**：Evidence 層**靜默跳過** —— 而 7-review 的其他節照樣填得完、verdict 照樣寫得出來。
E1–E13 的機械檢查完全沒把關，沒有任何地方會說「你少跑了一層」。

### 已採用的修法（2026-08-07，含當日更正）

- 路徑**維持** `docs/dev/tools/devflow-evidence-gauntlet.sh`（那是散發契約，不是隨手寫的）
- 加「開工前 `test -x` 確認」
- ⚠️ **補救方向由「手動 cp」改成「補跑 `dev-setup`」** —— 這是更正的核心：
  手動 `cp` 一支會**繞過受管檔的版本握手**，下次 `dev-setup` 比對時看到的是
  一個來歷不明的複本；而且它只補了 gauntlet，沒補 `devflow-contract.json`（A-12）
- **補不了 → Required 層改逐層手動實跑，並在 7-review 明記「gauntlet 未跑」是降級**
- 守衛（`check-stage67-enforcement.sh`）檢查四項：模板**必須**寫出正式散發路徑、
  必須有 `test -x`、**補救必須指向「補跑 `dev-setup`」**、必須有「降級」條款
  （needle 用補救那句話而非裸的 `dev-setup` —— 後者會被出處引用滿足，測不出補救被改掉）

---

## A-10 — 4-spec 的「觀測方式」可以寫成本 repo 做不到的事，而它是 G3 的 PASS 條件　✅ 已修

4-spec 的每條 S 都有「觀測」欄，7-review 步 2b 要求 reviewer **照那個方式親自實跑一次**，
而 G3 的 PASS 定義明列「**現象證據逐 S 相符**」。

**order-intake 的觀測欄絕大多數寫的是前端畫面**（例 S-15.1：「訂單列表（勾『顯示已作廢』）｜
該單標為已作廢並顯示理由與操作者」），而**前端屬另一個 repo 且本 feature 尚未實作**
（4-spec 自己的 Out of Scope 就寫了「前端（CRM 後台與院所端皆屬另一 repo）」）。

**於是整個「現象證據」節結構上做不到，而它是 PASS 條件之一** ——
G2 當時沒有任何機制會發現這個矛盾，一路到 G3 才撞上。

**這比「沒做」更糟的地方**：它讓 verdict 只剩兩種選擇 —— 誠實標 ❌ 永遠過不了 G3，
或睜一隻眼當作做過。兩種都不對，而根因在 G2。

### 已採用的修法（2026-08-07）

- `_templates/4-spec.md` 的觀測欄加**強制**條款：**觀測方式必須在本 repo 可執行**
  （後端 = 打得出 request、批次 = 看得到 log/產出檔）。指向本 repo 之外的東西
  → **當場**標 `n-a:<理由>` 並補一條本 repo 內可執行的替代觀測。
- `_templates/7-review.md` 的現象證據節呼應：G3 才撞到時的三步處置
  （逐條標 n-a 記為 spec 缺口／至少對本 repo 內可執行的代表性路徑實跑／
  verdict 不得因為「做不到」就當成做過）。

**順帶記一個本輪暴露的覆蓋空洞**（不是母版問題，但值得寫進 4-spec 的思考清單）：
handler 測試 = 真路由 + fake service，integration 測試 = 真 DB + 無 HTTP，
**兩者的交集（真 HTTP + 真 DB）零覆蓋**。這正是「現象證據」本來要接住的那一段。

---

## A-11 — Stage 7 的「禁讀 6-notes Self-Review」沒接到既有的圍欄機制　⏳ 未修

`_templates/7-review.md` 步 0 明文「**此刻禁讀 6-notes 的 Self-Review**」，
步 4 才「此刻才讀」。這是防錨定的核心機制。

**而 Stage 6 有一條結構完全相同的規則，且它是被機械強制的**：

```python
# _guard_impl.py:63-68   圍欄②
if tool == "Read":
    if L.is_contract_path(rel, L.UPSTREAM):        # UPSTREAM = 1-discussion/2-decision/3-prototype
        L.die("⛔ 圍欄②:執行期禁讀 ... 要翻上游 = spec 不完整")
```

**機制在，只是沒接到 Stage 7。**

### 為什麼不能只加一個 path 到 UPSTREAM 集合

1. `is_contract_path()` 只看**檔名前綴**，而 Stage 7 要擋的是
   `6-implementation-notes.md` 的**一個節**（Self-Review），不是整個檔 ——
   hook 只拿得到 `file_path`，擋不到「節」。
   務實解：Stage 7 期間禁讀整個 `6-implementation-notes.md`，步 4 再解鎖。
2. `exec.json` **沒有 stage 概念**。sequential `start` 寫的欄位只有
   `slug`／`started`／`scope`／`extra`／`baseline`／`contract_hashes`／`contract_hash_scope`
   （`_exec_impl.py:311-316`）。要分辨「現在是 Stage 6 還是 7」得加欄位
   → `devflow-contract.json` 的 `schema_versions.exec_state`（現為 `exec-v2`）要升版。

   ⚠️ **給實作者的地雷（2026-08-07 查證新增）**：`"mode"` 這個 key **已經被佔用了** ——
   parallel/task 模式的 `start` 會寫 `"mode": parsed["execution"]["mode"]`
   （`_exec_impl.py:385`），值是 5-tasks frontmatter 的 `sequential` / `parallel`。
   **review 模式不可複用 `mode` key**，否則會與並行執行的判斷（`:354`／`:362`／`:516`／`:554`
   四處 `execution.mode != "parallel"` 的閘門）互相污染。建議另開 `"phase": "review"`。

3. `7-review.md` **完全不在任何守衛的視野內** —— 全 plugin 搜尋 `7-review` 只有兩處命中：
   `_gate_consistency_impl.py:61` 的 G3 token 對照表，以及 `_guard_impl.py:86`
   我 2026-08-07 新加的那句提醒文字。既不受契約防篡改保護、也不在 scope 判斷裡。
   （這對 Stage 7 是合理的 —— 那正是 reviewer 要寫的檔；記在這裡只是讓實作者不必再查一次。）

### 建議修法（未動工，需 rick 裁決）

```
devflow-exec.sh review <slug>          → exec.json 加 {"mode": "review"}
  guard 圍欄③：mode == review 時
      Read  docs/dev/<slug>/6-implementation-notes.md  → 擋（訊息指向步 4）
      Write 限縮到 docs/dev/<slug>/7-review.*  與 evidence/
devflow-exec.sh review-unlock <slug>   → 步 4 解鎖，之後可讀
```

代價：`exec_state` schema 升版（`exec-v2` → `exec-v3`）、`selftest.sh` 要補案例、
`devflow-contract.json` 對版握手要同步。**這是 live hook repo 的真功能改動，
不建議在 context 快用完時硬做。**

### ⚠️ 順帶把一件事講死：「reviewer ≠ 實作 owner」機械上擋不住

`_templates/7-review.md:5` 寫 `owner: # reviewer,不可 = 實作 owner`。
**hook 層沒有身分概念**（沒有 session id、沒有作者歸屬、沒有任何可信的作者訊號），
加一個查 `owner` 欄位的守衛只會被「打字改個名字」繞過 ——
**那比散文更糟，因為它產生假保證**。

**可執行的替代品只有兩個**：
1. **讀取順序**（= A-11 的圍欄③）—— 這才是防錨定真正有效的那一半
2. **走 owner 自審時強制寫限制聲明節**（已於 2026-08-07 寫進模板步 0）：
   必須在 7-review 最前面獨立一節寫明「審查者 = 實作者」、哪些結論可信（機械數字）、
   哪些打折（F-id 分級、「沒想到的事」）、建議的補救路徑。
   **沒有這一節的 owner 自審視同未審。**

order-intake 的 7-review 就是走這條路產出的（verdict 標 **PRE-REVIEW 而非 PASS**），
可當範例。根因是本輪 session 同時被要求「繼續到全部完成」與「不派 subagent」，
與鐵律 4「驗證不自驗」直接衝突 —— **兩個約束無法同時滿足時，方法論該說怎麼辦，
而目前沒說。**

---

## A-12 — `dev-setup` 沒跑完整，而**沒有任何 Stage 要求跑 doctor**　⏳ 未修

> **原編號 C-3。2026-08-07 查證後由 C 升 A** —— 原本判「不影響執行」，
> 實跑 `devflow-doctor.sh` 直接 **fail-closed**，且它同時是 A-9 的根因。

### 查證（全部唯讀）

**① `dev-setup` 明文要散發這兩樣，CRM 兩樣都沒有**

```
skills/dev-setup/SKILL.md:38-39
   `_templates/` → `docs/dev/_templates/`、**`devflow-contract.json` →
   `docs/dev/devflow-contract.json`**(版本握手契約;doctor 無 --contract/...)
skills/dev-setup/SKILL.md:69
   6. **evidence gauntlet 散發**:`mkdir -p docs/dev/tools` 後 cp 母版
```

CRM 的 `docs/dev/` 實況：`_templates/`✅、`README.md`✅、`STATUS.md`✅、
`.gitignore:111` 有 `.devflow/`✅ —— **但沒有 `devflow-contract.json`、沒有 `tools/`**。
也就是 `dev-setup` **跑過但沒跑完**。

**② doctor 是 fail-closed 的，實跑直接紅**

```
$ cd ~/dev/CRM/icryobank-crm-api-golang && devflow-doctor.sh
=== devflow doctor(版本握手,共享契約 §9)===
✗ methodology-contract: 找不到 devflow-contract.json(找過:.../docs/dev/devflow-contract.json)。
  dev-setup 散發副本應在受測專案 docs/dev/,或以 DEVFLOW_CONTRACT/--contract 指定。
  無契約 = 無法握手,fail-closed。
⛔ devflow doctor: INCOMPATIBLE(fail-closed —— 不靜默退回舊行為;...)
```

`_doctor_impl.py:9` 的註本來就寫「找不到 → 明確報,**fail-closed**」。**機制是對的。**

**③ 但整條 Stage 6→7 走完，沒有任何一步要求跑 doctor**

```
$ grep -rn 'doctor' _templates/*.md
（零命中）
```

**四個模板（4-spec／5-tasks／6-notes／7-review）沒有任何一處提到 doctor。**
於是一個 fail-closed 的握手檢查，因為沒人被要求跑它而完全不發生作用。

### 這條的真正形狀

**不是「dev-setup 有 bug」，是「setup 完整性沒有任何 gate」**：

| 環節 | 狀態 |
|---|---|
| `dev-setup` 該散發什麼 | 明文寫了（SKILL.md:38-39、:69） |
| `dev-setup` 自己有沒有檢查 | 有（SKILL.md:158 第 9 項 gauntlet 散發檢查、:164 第 10 項版本握手） |
| `doctor` 缺件時的行為 | fail-closed ✅ |
| **有沒有人被要求跑 doctor** | ❌ **沒有** |
| 缺件時 Stage 6/7 會不會被擋 | ❌ **不會** —— 走完 26 個 T + 完整 Stage 7 都沒撞到 |

這與 **A-7** 是同一個病：**檢查存在、fail-closed 也對，但沒有觸發點。**

### 建議修法（未動工，需裁決）

1. **最小**：`_templates/6-implementation-notes.md` 與 `_templates/7-review.md` 的
   步 0「守衛武裝自檢」旁邊加一句 `devflow-doctor.sh` 必跑，輸出貼進 6-notes。
   —— 與 A-7 的修法同一個位置，成本近乎零。
2. **較強**：`devflow-exec.sh start` 內建跑一次 doctor，`INCOMPATIBLE` 即拒絕啟動。
   （但這會讓 A-0 之外再多一個啟動障礙，需一併考慮。）
3. **順手**：CRM 那個專案直接補跑 `dev-setup` 把兩樣散發齊 —— 那是專案端動作，不是母版改動。

---

## B-5 — `Files` 欄系統性低估，而模板沒有判準

**✅ 2026-08-07 查證確認，且數字要更正：不是 8 次，是 10 條。**

```bash
$ grep -oE '^### D-[0-9]+\(L1 — \*\*[^*]{0,40}(擴 Files|Files)' 6-implementation-notes.md
D-25 D-28 D-30 D-31 D-32 D-34 D-36 D-37 D-39 D-41        # 10 條
$ grep -c 'Files [0-9]* → [0-9]* 檔\|Files 欄' 5-tasks.md
9                                                          # 5-tasks 內 9 處自裁註
```

order-intake 的 T-13～T-25 有 **10 條 Deviation 動到 `Files` 欄**，
大多是同一個形狀：**規則寫在 SQL 的 WHERE／SET 裡，而 `Files` 只列了 service 層的測試檔**。
fake repository 之下那些規則完全看不出來（突變測試每次都全綠）。

執行者花了**四個 T** 才自己歸納出判準，寫在 D-34：

> 凡是「規則寫在 SQL 的 WHERE／SET 裡」的 T，`Files` 就該含 `repository_test.go`。

到 D-39 又細化成四象限（本輪最有用的一條方法論產出）：

| 性質 | 用什麼測 | 為什麼 |
|---|---|---|
| **缺席**（沒發出某句 SQL） | sqlmock / 白箱 | 真 DB 分不出「發了但 WHERE 沒命中」與「根本沒發」 |
| **順序**（有沒有 ORDER BY） | sqlmock / 白箱 | 小資料量下 DB 幾乎總是回插入順序，真 DB 斷言**恆綠** |
| **可觀測的結果**（讀回來有沒有那筆） | integration | 白箱佈置多句 eager-load 成本高又脆弱 |
| **單句 SQL 的 WHERE／綁定值** | sqlmock / 白箱 | 便宜、精確、不需要 Docker |

**模板側查證**：`_templates/5-tasks.md` 對 `Files` 欄的全部指引是
「Files 超過 ~5 檔或 Verify 要跑兩套不相干指令 → 拆 T」與
「`Files` 正是 Stage 6 scope guard 的唯一依據」——
**只講「不要太多」與「它很重要」，沒有一個字講「該含哪些檔」**。

**建議**：把上面四象限寫進 `Files` 欄指引。
**不建議加守衛** —— 這是判斷校準，機械檢查會變成 false positive 工廠。
真正的機械補償是 A-7 的 scope guard（它會在寫第 N+1 個檔的當下擋下來），
前提是**它要醒著**。

---

## B-6 — Diff Budget 的測試檔估法沒把補償控制算進去

| 區塊 | 4-spec Budget | 實得 | 偏差 |
|---|---:|---:|---:|
| 非測試碼 | 24 檔 / ~7,200 行 | 24 檔 / 9,633 行 | 檔數 **完全一致**、行數 +34% |
| **測試檔** | ~15 檔 / ~5,800 行 | 20 檔 / **18,458 行** | **+218%** |
| 合計 | ≈58 檔 / ≈15,500 行 | 63 檔 / ≈30,068 行 | +94% |

**超支幾乎全在測試檔，而且是紀律的直接後果**：每個 T 跑突變測試（合計約 160 刀），
首輪全綠的每一刀都補了測試 —— 那些補的測試就是超支的來源。
**砍測試會砍掉抓到 D-41 與 D-38 的能力**（見 B-7）。

**✅ 2026-08-07 查證確認，且比原判更嚴重 —— 母版模板連「怎麼估」都沒說。**

`_templates/4-spec.md` 的 Diff Budget 節**全文只有兩行**：

```markdown
## Diff Budget
<!-- 預期 ≤N 檔 / ≤M 行。超支本身非偏差,是停下判 L1/L2 的訊號;分不清一律當 L2 -->
```

**沒有分區塊、沒有測試/非測試的區分、沒有任何係數或參考值。**
CRM 那張「ent/schema｜order｜specimen｜catalog｜migration｜測試檔」的分區塊表格
是**採用端自己長出來的** —— 而正因為沒有母版指引，它把測試估成
「各子 package 4-5 檔」（＝「一個 S 一條測試」的直覺估法），
沒有把「突變補洞」這種補償控制算進去。

**建議**：`_templates/4-spec.md` 的 Diff Budget 節補兩句 ——
①建議按區塊拆（採用端已自發這麼做，把它變成模板）
②**測試檔與非測試碼分開估**；若計畫用突變測試／對抗式驗證當補償控制，
測試的估法要用不同係數（本輪實測約為天真估法的 **3 倍**）。
超支判定的措辭（「超支本身不是偏差，是停下判 L1／L2 的訊號」）本身是對的，維持。

---

## B-7 — ~~突變測試不在流程裡~~　❌ **原判錯誤（2026-08-07 查證後改寫）**

### 原始判斷（錯的，留著當記錄）

> 「母版完全沒提突變測試。order-intake 是執行者自己加的紀律。」

### 查證結果：母版**有**講，而且講得比採用端做的**更嚴**

```
README.md:151-152
  mutation/property 等重驗證層屬 feature 級 Final Fresh Run,**不逐 T 跑**。

notes/design/evidence-gauntlet.md:79
  **不要每個 Task 都跑完整 Mutation** —— mutation/property 屬 feature 級 Final Fresh

notes/design/evidence-gauntlet.md:64
  手動 mutation 程序須 **script 化並持久化(禁 scratch)**
```

**所以偏離的是採用端，不是母版。order-intake 兩條都違反了**：

| 母版規則 | order-intake 實況 |
|---|---|
| mutation 屬 feature 級 Final Fresh Run，**不逐 T 跑** | **逐 T 跑**（26 個 T，合計約 160 刀） |
| 手動 mutation 程序須 script 化並持久化，**禁 scratch** | runner 放在 `<scratchpad>/mutate.py`，6-notes 自己註明「**非交付物，新 session 需重建**」 |

⚠️ 第二條特別值得記：`evidence-gauntlet.md:64` **明文禁止**的事，
被 6-notes 寫成一條交接注意事項（「新 session 需重建，四個必要條件是…」），
**而沒有任何人指出那本身就違規**。

### 但這裡確實有一個母版缺口（B 級，重新定義後）

**「mutation 屬 feature 級 Final Fresh Run」這條規則在 4-spec 沒有落點。**

`_templates/4-spec.md` 的 Verification Profile 只有一行
`- Required layers:(Final Fresh Run 必跑)` —— **自由文字，沒有任何提示說
「若採用 mutation，它該列在這裡」**。於是：

- order-intake 的 Required layers 實際列了六層（build/vet、unit、integration、
  migration、swagger drift、ID 鏈檢）—— **沒有 mutation 層**
- 而它逐 T 跑了 160 刀 mutation，**那些證據沒有任何一個欄位收得到**
- 7-review 的 Evidence 表因此也沒有 mutation 那一列

**結果是最壞的組合**：規則說「要在 feature 級跑」→ 沒有欄位承接 →
執行者改成逐 T 跑（違反規則但至少跑了）→ 產出的證據無處可放 →
**只能塞在 6-notes 的 Progress Log 裡，reviewer 要自己翻**。

### 建議修法（未動工，需裁決）

1. `_templates/4-spec.md` 的 `Required layers` 補一句提示：
   「若採用 mutation／property 等重驗證，**列在此處**（feature 級，不逐 T 跑，
   見 README §…）；runner 須 script 化並持久化進 repo（禁 scratch）」。
2. `_templates/7-review.md` 的 Verification Evidence 表天然就吃得下那一列，不必改。
3. **順帶回頭看規則本身**：order-intake 逐 T 跑的代價是測試量 +218%（B-6），
   換到 **D-41 與 D-38 兩個真缺陷**，以及三條方法論級發現
   （「兩道防線互相掩護」×3、「跑了 goroutine ≠ 測到併發」、
   「地板留餘裕 = 地板沒有牙齒」）。
   **這不足以推翻「不逐 T 跑」的規則**（樣本 n=1，且該 feature 的 Risk 是 high），
   但足以支持在 `Risk: high` 時把它列為**建議**而非禁止。這是 rick 的決定。

---

# 第三輪（2026-08-14，ivf_platform / pgs-report-batch-scope）

**來源**：ivf_platform（CI2 舊系統，PHP）走 fast lane 到 G2 送審時，owner 打開 `4-spec.html`
第一句話是「這份給人看得有點雜亂」。追下去發現兩條 B 級，**兩條互相獨立**：
B-8 是**形狀**（gate twin 沒有審查介面規格），B-9 是**內容**（明文要求的欄位缺了沒人擋）。

**性質**：同 A/B/C 分級。兩條皆**未動母版**，只記問題與建議修法。

---

## B-8 — gate twin 的「審查動線」規格只綁了 7-review，G1／G2 的 twin 沒有形狀規格　✅ 已修（2026-08-15）

### 現象

owner 打開 `4-spec.html`（22KB md 直轉、單欄長文件、一張 R 級流程圖、DD 表在底部），
反應是「有點雜亂」——**與 order-intake 那次 7-review 95k 字的反應是同一句話**。

### 查證（全部唯讀）

母版 `README.md` §6 的 per-stage 規格表，4-spec 那列只有三欄要求：

| twin | 必含圖 | 分歧/自判區 | diff |
|---|---|---|---|
| 4-spec | 行為流程圖(R 級) | Drafting Decisions(待裁決置頂) | — |

`_templates/4-spec.md` 頂註第 18-19 行同樣只列「必含什麼元素」：

```
> 本階段固定產出:`4-spec.md`(本模板全節)+ `4-spec.html`(G2 必產;必含 R 級
> 行為流程圖、Drafting Decisions 待裁決置頂)。
```

**採用端完全合規**（兩個元素都有），產出仍然難審。因為規範管的是「必含什麼」，
不管「長什麼形狀」。

而同一份 README §6 下方有一整段獨立規格 ——

> **審查動線頂區**(7-review 的 html **必含**,2026-08-13 補):twin 不只是給人查的參考檔,
> 它是給人**審**的。頂部固定五格,每格一句話 + 一個跳轉,審完五格才決定要不要往下讀
> …
> 起因:order-intake 的 7-review 長到 95k 字,owner 問「這麼雜要怎麼審、從哪開始」。

**同一個病 2026-08-13 修過一次，但只修了 7-review 那一站。** G1（2-decision）與
G2（4-spec）一樣是要人逐條審的 gate，一樣會長到 owner 不知道從哪開始，規格沒跟上。

### 這條的真正形狀

不是「4-spec twin 少了五格」，是**規範沒有「gate twin = 審查介面」這個分類**。
現行 §6 把 1～7 的 twin 一視同仁當「md 的視覺版」，只在 7-review 破例加了動線頂區。
實際上兩類用途不同：

| 類 | twin | 用途 | 該長的形狀 |
|---|---|---|---|
| gate twin | 2-decision（G1）、4-spec（G2）、7-review（G3） | 給人**審**，逐條過 | 審查介面：動線頂區 + 待審項目逐條可勾 + 背景資料摺疊 |
| 紀錄 twin | 1-discussion、3-prototype、5-tasks、6-notes | 給人**查**，找得到就好 | 現行的文件形狀就夠 |

### 建議修法（未動工，需裁決）

1. `README.md` §6：把「審查動線頂區」從 7-review 專屬**升格成所有 gate twin 通用**，
   格數與內容依 stage 調整（4-spec 建議五格：狀態／Gate／lane+Risk／DD 進度／Demo verdict）。
2. §6 per-stage 規格表加一欄「審查形狀」，gate twin 三列填「審查介面」，其餘填「文件」。
3. `_templates/{2-decision,4-spec}.md` 頂註各補一行，與 7-review 模板的「Reviewer 閱讀動線」
   對齊（md 是正本、html 做成可點的，這個分工 7-review 已經確立，照抄即可）。
4. **可直接複用的範本**：本輪產出的 4-spec 審查介面原型已存進
   `notes/patches/spec-review-ui-prototype.py`（見下方 B-8 附錄）。

### 已採用的修法（2026-08-15）

owner 拍板形狀 = **先寫規格、再做工具**（其餘三個選項的問題：只做工具 → 產出物沒有規格可對；
只寫規格 → 就是 B-9 修好之前的老毛病；做進 skill → 沒有獨立工具就沒辦法單獨測）。

1. **規格**：`README.md` §6 per-stage 表加「審查形狀」欄，gate 三站標「審查介面」、其餘標「文件」；
   〈審查動線頂區〉從 7-review 專屬升格成三站通用，並列出各站的五格內容。
   三件必含寫死：動線頂區五格 / 待審項目逐條可勾且缺欄紅底 / 背景資料摺疊且內容零刪減。
2. **模板**：`_templates/{2-decision,4-spec}.md` 頂註各補一節「G1（G2）twin 是審查介面」，
   含該站的五格內容與待審項目定義，與 7-review 模板的「Reviewer 閱讀動線」對齊。
3. **工具**：`scripts/build-gate-twin.py` + `scripts/devflow_twin_ui.py`（共用 UI 與兩種殼），
   三站共用一支，讀 md 逐條解析不手抄。原型的寫死值（專案根、slug、期望條數、章節清單、
   R 的嚴重度表）全部拿掉：標題 pattern 放寬到 `^#{2,6}` 與 `check-spec-gate.sh` 對齊，
   期望條數改成設了 `DEVFLOW_EXPECT_ITEMS` 才檢查，未列到的章節自動收進背景資料。
4. **守衛**：`scripts/check-gate-twin.sh`（21 項，含負向案：缺觀測欄要紅底、空 spec 要
   exit 1 且不產空殼、artifact 片段不得含 doctype/html/head/body），註冊進 devflow-check
   （17 → 18 組），三站都對母版範例實跑 = 自帶回歸。

**尚未做**：附錄追加提到的第三種形狀「執行板」（5-tasks）沒有納入本輪，
`notes/patches/gate-twin-ui-prototype/build_tasks.py` 仍是唯一實作。

---

### B-8 附錄：本輪的審查介面原型（owner 2026-08-14 指定收錄）

owner 評語：「這次審查介面不錯」。做法與可移植的部分：

- **輸入是 `4-spec.md` 本身**，R/S 逐條 regex 解析（`### S-x.y` + `- **GIVEN/WHEN/THEN/觀測**`），
  **不手抄**，所以不會與正本漂移；解析數不符預期（16）直接 exit 1，避免默默少一條。
- **每個 S 一張卡**：checkbox + S-id chip + 標題 + 「回歸基準線／主案例」標籤；
  GIVEN/WHEN/THEN 用 58px 標籤欄對齊；**「觀測」欄獨立標色**（審查判準就是它）。
- **缺欄直接紅底現形**：解析不到「觀測」的 S 渲染成紅色「缺『觀測』欄」卡
  —— 這正是 B-9 在本輪被抓到的方式。
- **頂部 sticky 進度條**：已審 N/16 + 百分比 bar + 清除鈕；勾選狀態存 `localStorage`
  （純前端，不送出），關掉再開還在。
- **背景資料全部收進 `<details>`**：Bug Scenario／AC／Out of Scope／Diff Budget／
  Verification Profile／DD／Test Skeletons／Known limits 八節，預設收合、內容零刪減。
- **動線五格**在頁首：狀態／Gate／lane+Risk／DD 進度／Demo verdict。
- 三態主題（bare `:root` / `prefers-color-scheme` 加 `:not([data-theme="light"])` 守衛 /
  `[data-theme="dark"]`）、表格 `overflow-x:auto`、`prefers-reduced-motion` 全按母版
  html-shell 的既有規矩。

**要注意的一點**：Artifact 片段不得含 `<!doctype>/<html>/<head>/<body>`（發布時外層會自動包），
本機 twin 則需要完整文件外殼 —— **同一份內容，兩種殼**。

### B-8 附錄追加（2026-08-14 稍晚）：原型已改成單一產生器、兩種輸出

第一版是兩份分開產（本機 twin 走 md 直轉、Artifact 走審查介面），owner 隨即反映
「本機的 html 也更新成這個版本」+「Stage 5 不好閱讀」——**兩件事都是同一個缺口的下游症狀**：
沒有共用 UI 層，所以每加一站就多一份會漂移的樣式。已改成三支：

| 檔（`notes/patches/gate-twin-ui-prototype/`） | 職責 |
|---|---|
| `devflow_ui.py` | 共用 CSS（tokens + 動線格 + 區塊卡 + 摺疊 + 圖）與**兩種輸出殼**：`local_page()` 完整文件、`artifact_page()` 片段 |
| `build_review.py` | 4-spec：R/S → 可勾選 S 卡、觀測欄標色、缺欄紅底 |
| `build_tasks.py` | 5-tasks：T → 任務卡（Intent 突出、四欄表、**Boundaries 摺疊**）、DAG 用 inline SVG |

`build_tasks.py` 額外驗證的東西（B-9 的同類機械檢查，可直接抄進母版腳本）：
逐 T 檢查 Covers／Files／Verify／Blocked-by／Intent／Boundaries 六欄非空，缺 → exit 1；
T 數不符預期 → exit 1；md 出現未收錄的 `## ` 章節 → exit 1（防新增章節被靜默丟掉，
第一版就發生過：新加的「G2 審查記錄」節差點沒進 html）。

**5-tasks 那頁「不好閱讀」的具體成因**（md 直轉時）：Boundaries 是每個 T 最長的欄位
（本例最長 1,461 字），直轉後五個 T 的禁區全部攤平在頁面上，把 Covers／Files／Verify
這些一眼要看到的欄位擠掉。改成摺疊後，預設看到的是「這個 T 做完多了什麼 + 四個關鍵欄」，
禁區要動工前才展開。**這是 gate twin 與紀錄 twin 之外的第三種形狀：執行板**，
若採納 B-8 的分類表，`5-tasks` 應歸到「執行板」而非「紀錄 twin」。

⚠️ `notes/patches/spec-review-ui-prototype.py` 是**第一版單支腳本**（已被上表三支取代），
本檔已於 `e940267` commit，本輪未刪 —— **由 dev-flow 這邊的 session 決定要不要移除**，
採用端不代為處置。

---

## A-13 — `devflow-exec.sh start` 把 **.gitignore 已忽略的檔**也算成「scope 外未提交改動」，有本機開發目錄的專案一律啟動不了　⏳ 未修

### 現象

ivf_platform 走到 Stage 6，`devflow-exec.sh start pgs-report-batch-scope` 回：

```
⛔ 拒絕啟動:工作樹已有 56 個 scope 外未提交改動(前 10):
  .gitignore
  config/development/config.php
  ...
→ 請先 commit、還原或使用乾淨 worktree，再重新 start。
```

56 個的實際組成（`git status --porcelain=v1 -uall --ignored=traditional | awk '{print $1}' | sort | uniq -c`）：

| 狀態 | 數量 | 內容 |
|---|---|---|
| `!!`（**已被 .gitignore 忽略**） | **44** | `.DS_Store`、`.serena/`、`_localdev_mysql/`（本機 MySQL 容器 + 11 支 relay 腳本 + init SQL + mock） |
| `??`（untracked） | 25 | `docs/dev/` 全部（含本 feature 的 4-spec/5-tasks）、`CONTEXT.md`、`.claude/rules/` |
| `M`（tracked modified） | 4 | `.gitignore`、`config/development/{config,database}.php`、`controllers/backend/login.php` |

### 查證（唯讀）

`hooks/devflow-lib.py:47-51`：

```python
def git_dirty_paths(root):
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "-uall", "--ignored=traditional"], ...)
```

`--ignored=traditional` 把**專案自己明確宣告要忽略的檔**一起撈出來。
`hooks/_exec_impl.py:139-178` 的 `dirty_scan_and_baseline()` 只豁免三種：
`.git/`、`is_ambient_path()`（僅 `.DS_Store`／`._*`／`Thumbs.db`／`*.pyc`／`__pycache__`）、
`.devflow/` 前綴，以及「唯一差異是 `.devflow/` 行」的 `.gitignore`。
**gitignore 的其餘內容完全不在豁免內。**

### 這條的真正形狀

不是「這個專案太髒」。**任何在 repo 內放本機開發環境的專案都啟動不了** ——
本機 DB 容器、mock server、`.venv/`、`node_modules/`、IDE 目錄、editor 快取。
這些正是 `.gitignore` 存在的理由，開發者不會、也不該為了跑 Stage 6 把它們刪掉。

守衛的目的是「防止 scope 外的**版本控制內容**被改動」。已被 gitignore 的路徑
**在定義上不會進 diff**，把它們算進去是誤判，而且是**無法排除的誤判**——
使用者唯一的出路是刪檔或整個換乾淨 worktree（那樣本機環境也一起沒了）。

對照 `dev-run` SKILL「前置(缺一不啟;順序不可調)」：規則要求必啟守衛，
守衛在這類專案必拒 → **規定了做不到的事**，A 級。

### 建議修法（未動工，需裁決）

1. `git_dirty_paths()` 拿掉 `--ignored=traditional`（或另加參數只在需要時開）。
   理由：ignored 路徑不會進 commit，不構成 scope 汙染風險。
2. 若仍要看 ignored（例如防止 build 產物混淆），改成**只警告不拒啟**，
   並在訊息裡分開列「tracked modified / untracked / ignored」三類，
   讓使用者知道哪些是真的要處理、哪些是雜訊 —— 現行訊息把三類混在一起，
   前 10 筆剛好全是前兩類，使用者根本不知道另外 44 筆是 gitignore 的東西。
3. `untracked` 的 `docs/dev/<slug>/` 應比照 `extra_skip_shared` 豁免：
   feature 自己的規劃文檔本來就是 Stage 6 期間會被派工者改的（記帳），
   現行只豁免 `5-tasks` 與 `6-implementation-notes` 兩個前綴，
   `4-spec.html`／`5-tasks.html` 等 twin 反而會擋住 re-arm。
4. ⚠️ 採用端**不得**用 `git update-index --skip-worktree` 或刪本機目錄來繞過 ——
   前者會讓後續真實改動被靜默忽略，後者毀掉開發環境。這條沒有安全的採用端 workaround，
   只能改母版。

---

## B-9 — 「每 S 有觀測欄」是模板明文的完成條件，卻沒有任何機械檢查　⏳ 未修

### 查證

`_templates/4-spec.md` 頂註執行清單步 2 寫得很清楚：

```
> 2. 逐 R 展開 S:…**每 S 承接 1-discussion 該條驗收雛形的「觀測方式」**(從哪看/
>    看到什麼算對/拿什麼資料試;雛形沒寫就在此補齊,純內部行為註明「無外部現象」)。
>    段段給使用者確認。完成 = 全 R 展開、**每 S 有觀測欄**、每段有確認…
```

實測：ivf_platform 的 `4-spec.md` 走到 G2 送審時，16 個 S 裡有 **5 個缺「觀測」欄**：

| S | 缺什麼 |
|---|---|
| S-1.6 | 缺觀測 |
| S-2.3 | 缺觀測 |
| S-3.2 | 缺觀測 |
| S-3.3 | 缺觀測，**同時缺 GIVEN** |
| S-4.3 | 缺觀測 |

而同一份 spec 的 Acceptance Criteria 自己寫著「**每個 S 的『觀測』由驗收者親自實跑一次**
並記錄現象證據（不接受『程式碼看起來對』）」—— 缺觀測欄的 S 滿足不了這條，
G3 的「現象證據逐 S 相符」也就無從驗起。

### 為什麼會漏

步 2 的「完成 =」只靠寫的人自覺打勾。README §7 的〈強制力對照〉自己承認過：
Gauntlet 只驗 Evidence 契約（一份 markdown 有沒有照規矩填），不驗 4-spec 的欄位完整性。
**在 md 直轉的長文件裡，缺一行只是「少一行」，肉眼掃不出來**；結構化成卡片之後 5 個立刻現形
（B-8 的原型就是這樣抓到的）。這兩條因此互相放大：形狀不好審 → 內容缺漏更難發現。

### 建議修法（未動工，需裁決）

1. 新增 `scripts/check-spec-scenarios.sh <slug>`：解析 `4-spec.md` 的 `### S-x.y`，
   逐條驗 GIVEN／WHEN／THEN／觀測四欄非空，缺 → exit 2 並列出 S-id。
   接進 `devflow-check.sh all`，並在 G2 送審步（模板頂註步 6）列為前置。
2. 同一支順帶做**反模糊三律的機械部分**：模糊詞掃描（適當/正確/合理/必要時/妥善/
   robust/等等/視情況）與 TBD 殘留掃描 —— 目前這兩項也只寫在頂註步 5，同樣無檢查。
3. ⚠️ 寫這支腳本時注意母版自己的教訓（本檔〈第二輪查證方法〉附錄）：
   **先看計數再看 exit code**。解析到 0 個 S 卻回 exit 0 = 假綠，
   與「`go test -run` 沒匹配也回 rc=0」同類。本輪原型的做法是硬比對預期條數，可照抄。

---

## 附錄：第二輪的查證方法（可複用）

```bash
# ── 守衛到底有沒有醒（A-0 / A-7）────────────────────────────────────
ls -la <repo>/.devflow/                    # 空目錄 = 從未 start 成功
git -C <repo> status --porcelain=v1 -uall                        # 真髒檔數
git -C <repo> status --porcelain=v1 -uall --ignored=traditional  # 守衛看到的數
# 兩者差距 = A-0 的曝險；後者 > 0 就啟動不了

# ── Verify 欄有沒有鑑別力（A-8）─────────────────────────────────────
git stash && <原樣跑該 T 的 Verify>; echo "rc=$?"   # 在「還沒實作」的樹上跑
# rc=0 → 該欄不具鑑別力。務必同時數 '^=== RUN' 行數，不要只看 rc

# ── swagger 之類生成檔「有沒有改到既有東西」───────────────────────────
# ⚠️ 不要看 diff 行數：純插入會被 git 的行 diff 放大成看起來像重寫
#    （本輪 swagger textual diff 24k 行，實際是 64 個新 schema 依字母插入造成的位移）
python3 -c "把前後各 parse 成 dict，逐 operation/schema 比對"

# ── S-id 鏈檢要雙向（不能只比數字）────────────────────────────────────
comm -23 <測試檔側 S-id> <4-spec 側 S-id>   # 錯字型 S-id（測試有、spec 沒有）
comm -13 <測試檔側 S-id> <4-spec 側 S-id>   # 未覆蓋
# 只比總數會被「一個錯字 + 一個漏掉」互相抵銷

# ── dev-setup 完整性 / doctor（A-12）───────────────────────────────
ls <repo>/docs/dev/devflow-contract.json <repo>/docs/dev/tools/   # 兩者皆為 dev-setup 散發契約
cd <repo> && <plugin>/hooks/devflow-doctor.sh                     # fail-closed，但沒人被要求跑
grep -rn 'doctor' <dev-flow>/_templates/*.md                      # 零命中 = 沒有觸發點

# ── 「母版到底有沒有講過這件事」（B-7 的教訓：先查再說）──────────────
grep -rniE '突變|mutation' <dev-flow>/_templates/ <dev-flow>/README.md <dev-flow>/notes/design/
# 我原本斷言「母版完全沒提突變測試」→ 實查 README:151 與 evidence-gauntlet.md:79 都有，
# 而且講得比採用端做的更嚴。**下判斷前先 grep 母版全文，不要憑印象說「沒有」。**

# ── 守衛自己有沒有牙齒（本輪實測抓到自己寫的守衛的漏洞）──────────────
# check-stage67-enforcement.sh 的 MIN_CHECKS 原本填 16（「抓個下限」），
# 而 A-7 那組恰好 8 項（24-8=16）→ 刪掉整組後剛好等於地板，守衛照樣 exit 0。
# **地板留餘裕 = 地板沒有牙齒。** 一律填「等於當下實際檢查數」。
scripts/test-architecture-guards.sh        # 每加一道守衛就配一個會紅的 mutation
```

---

## 附錄：採用端已自行吸收、母版不用改的事

記下來避免日後誤判成母版問題。

- **`docs/dev/tools/` 也是母版覆蓋區** —— 專案自訂腳本不能放 `_templates/` 也不能放 `tools/`，
  唯一乾淨的留法是 repo root 的 `scripts/`。這個界線是對的，只是 SKILL.md 沒明說。
- **html twin 的產法是「`html-shell.html` 殼檔 + 模型手寫」，不是腳本** —— 母版 `_templates/`
  底下零 `.py`、全 repo 無 twin 產生器。python-prism 自製的 `md2html.py` 是加速器，
  刪掉沒有移除任何母版能力。（但採用者容易誤以為母版該提供產生器。）
- **缺 `devflow-contract.json` 不擋 Stage 6 start** —— `_exec_impl.py` 全檔無 doctor / 無
  `devflow-contract` 呼叫；`protected_contract_hashes()` 讀的是 `docs/dev/<slug>/` 底下 feature
  契約檔的內容 hash，與 `devflow-contract.json` 同名不同物。只有主動跑 `doctor` 才會報 INCOMPATIBLE。
- **`docs/dev/` 底下有進行中 feature 的專案，應等它出貨再 upgrade** —— 中途換模板會讓
  同一 feature 的 4-spec（舊形狀）與 7-review（新形狀）對不上。這條值得寫進 SKILL.md 的
  upgrade 段當使用建議。
- **Stage 1 的資訊隔離規則運作正常，不是缺陷** —— report-system 的 session 被要求「開 Stage 1」時
  **正確拒寫 `1-discussion.md`**，理由引 dev-flow 路由表 stage 1 那列：「本 skill 不執行。
  討論由 `/dev-talk` 專職（資訊隔離：討論 agent 不知道有後續階段，防直奔結論；最好開獨立 session）」。
  它還補了一句對的觀察：該 session 已經知道根因與 7 個檔，自己寫 Stage 1 等於拿結論反推討論。
  它改把 owner 釘死的技術結論落成 `0-draft-owner-constraints.md`（依 §1「流程外草稿收編」）
  並標「Stage 1 討論者禁讀」，等 Stage 2 收斂時再撈。**這是方法論按設計運作的實例，值得寫進範例。**
- **CRM 的 `ON COMMIT DROP` 事件是專案端問題，不是母版問題** —— `atlas migrate diff/validate`
  replay 到 dev DB 時逐句 autocommit，`CREATE TEMPORARY TABLE … ON COMMIT DROP` 建完就消失。
  已獨立驗證：`-- atlas:txmode file` 指示**不能**修好 replay（實測仍同樣報錯），
  刪掉 `ON COMMIT DROP` 後 `validate --dev-url` rc=0。與 dev-flow 無關，記在此處只為避免日後誤判。

---

## 附錄：查證方法（可複用）

```bash
# 5-tasks parser 實跑
python3 -c "
import importlib.util
s=importlib.util.spec_from_file_location('d','$HOME/.claude/plugins/cache/dev-flow-plugin/dev-flow/2.5.0/hooks/devflow-lib.py')
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
r=m.parse_5_tasks(open('docs/dev/<slug>/5-tasks.md',encoding='utf-8').read())
print('tasks=',len(r['tasks']),'errors=',len(r['errors']))
[print(' -',e) for e in r['errors'][:20]]
print(m.spec_profile(open('docs/dev/<slug>/4-spec.md',encoding='utf-8').read()))"

# 受管檔是否與母版一致（blob 身分比對，零判斷）
git hash-object <專案檔>
git -C ~/dev/dev-flow rev-parse HEAD:<母版路徑>

# gauntlet 正負向（負向不紅 = 守衛失效）
bash docs/dev/tools/devflow-evidence-gauntlet.sh ~/dev/dev-flow/scripts/fixtures/evidence-gauntlet/good-evidence.md; echo $?
bash docs/dev/tools/devflow-evidence-gauntlet.sh ~/dev/dev-flow/scripts/fixtures/evidence-gauntlet/bad-pass-no-run.md; echo $?
# 注意 bad-review-* 三個要帶 --review-file 才會紅（見 scripts/test-evidence-gauntlet.sh:105,108,110）

# doctor（rc 不要經 pipe，會被吃掉）
bash ~/.claude/plugins/cache/dev-flow-plugin/dev-flow/2.5.0/hooks/devflow-exec.sh doctor > /tmp/d.txt 2>&1; echo rc=$?
```
