# 派工：補守衛的覆蓋缺口（v3.4.0 獨立審查的 6 條）

> owner 用一句話觸發：
> 「讀 `~/dev/dev-flow/notes/dispatch-guard-coverage.md` 照它跑，全程不打斷問人」。
> 寫於 2026-08-15（plugin v3.4.0，遠端已同步）。前一輪的派工單是
> `notes/dispatch-backlog-sweep.md`，那一輪的四批**已全部做完**，本檔是它的獨立審查結果。

## 這一輪的性質

**不是修功能，是補守衛。** v3.4.0 的產物本身通過了 12 個舊 bug 回歸測試與 12 個破壞實驗，
六道回歸全綠。獨立審查判 REQUEST_CHANGES 的理由全部是同一句：

> **有些東西壞掉了，而 108 項守衛不會發現。**

所以這一輪的驗收標準不是「檢查變綠」，是「**故意弄壞，檢查會不會紅**」。

## 開工前

```bash
cd /Users/asheng/dev/dev-flow
git status --short          # 必須為空
git fetch origin && git rev-list --left-right --count HEAD...origin/main   # 應為 0 0
bash scripts/devflow-check.sh && bash scripts/check-gate-twin.sh
```

背景讀物（**先讀再動手**）：
- `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 **A4/A5/A6/A7** —— 四輪獨立審查的完整軌跡
- `notes/dispatch-backlog-sweep.md` 的「四次假綠」一節 —— 本檔的 N-1 是**第 4 型的第二次發生**

---

# 六條缺陷

## N-1（HIGH，最重要）：沒有「背景章節盤點」守衛

**破口**：`scripts/build-gate-twin.py:1013-1017` 的背景資料迴圈。任何讓某個章節被
`continue` 掉的改動，都不會被任何斷言發現。

**審查者的重現方式**（在 pristine 複本上，只改 1 行 × 2 檔）：
在背景章節迴圈加一條「跳過 `Diff Budget`」→ 範例 4-spec 的 twin 從 12 節變 10 節、
「≤ 9 檔 / ≤ 600 行」整段從出貨 html 消失 → **`check-gate-twin` 108/108 全綠、
`devflow-check` 20/20 全綠**。

**這是同一型態的第二次發生。** 第一次是 P4：一個正則的 `\s` 含換行 → `## 變更架構圖`
整節從**已經出貨的** `7-review.html` 消失，當時 53 項守衛全綠。

**為什麼現有的零刪減檢查擋不住**：它靠 `scripts/fixtures/gate-twin/zero-deletion/`
這份合成 fixture 的 5 個 canary。canary 埋在哪，就只守得住哪。**對真實文件沒有任何
「章節數對得上」的斷言。**

⚠️ **A7 自己寫了正確的原則** —— 「盤點型守衛要跟著每個新資料格一起長」——
但只套在動線五格，**沒有套回它自己最初出事的地方**。所以：

**修法要求（這條不接受逐處手加）**：做一條**與資料格無關的通用對帳**。方向：
> 輸入 md 的每一個 level-2 章節，都要能在產出物裡找到對應痕跡 ——
> 渲染成卡片、渲染成置頂節、收進背景 `<details>`、或**被明確列進 `dropped` 並印出 NOTE**。
> 四者皆非 = 靜默消失 = 失敗。

對**母版範例三站**（`example/contract-expiry-reminder/{2-decision,4-spec,7-review}.md`）
都要跑，不是只跑合成 fixture。做完後用審查者那個「跳過某一節」的破壞實驗自驗，必須紅。

## N-2（MED）：四支守衛沒有檢查數地板

`scripts/check-gate-twin.sh:43-48,649`、`check-realworld.sh`、
`check-no-stale-paths.sh`、`check-readme-markers.sh` —— **刪掉整個斷言區塊，
守衛照樣印 `✅ 全過`**（實測刪 P5 整區 → 「✅ 全過(106 項)」，`devflow-check` 也沒發現）。

同 repo 已有慣例可抄：`scripts/check-stage67-enforcement.sh:232` 的 `MIN_CHECKS=50`、
`scripts/test-architecture-guards.sh` 的 `EXPECTED_TOTAL=59`。這四支只是漏了。

**注意**：地板不是「寫死一個數字就好」——`MIN_CHECKS` 型的下限要能擋住「整區塊被刪」，
但不該每加一條檢查就要改。照既有兩支的寫法選型。

## N-3（MED）：斷言寫「印用法」但只驗 exit code

`scripts/check-gate-twin.sh:643`。把用法訊息全部刪光，那條斷言照樣綠。
而且 exit 2 與「相依失敗」共用同一個碼，光看 exit code 分不出是哪一種。

`skills/dev-setup/SKILL.md:241` 明文要求採用專案驗「訊息含用法」，**母版自己反而守不到**。

修法：驗訊息內容（至少要出現 stage 名稱與參數順序），並讓「用法錯誤」與「相依失敗」
可區分（不同 exit code、或訊息含可辨識前綴）。

## N-5（MED）：路徑守衛漏掉約 75 個活檔

`scripts/check-no-stale-paths.sh:125-140,148-154`。`example/`（14 檔）、
`observability/`（57 檔）、`manifests/`（4 檔）**既不在掃描目標、也不在印出的豁免清單**
→ 完全不可見。實測：往這些目錄塞禁字，守衛零命中、exit 0。

⚠️ **這與該檔頭部 2026-08-15 註記聲稱「剛修好」的缺陷是同一型**，只是換了目錄。

**修法方向（這條要改設計不是補清單）**：現在是「**明確列入才掃**」（fail-open），
應該改成「**預設全掃 + 明確豁免**」（fail-closed）—— 新增的目錄自動被納入，
要豁免必須寫進 ALLOWLIST 並附理由。這樣「忘了加」不會變成「沒在守」。

改完要驗：對**任意**一個活文件目錄塞禁字都會被抓到；ALLOWLIST 裡的歷史紀錄目錄仍豁免。

## N-4（LOW）：未閉合的 `<!--` 吞掉章節且無警告

`scripts/build-gate-twin.py:934-940`。未閉合的 html 註解會被 markdown-it 的
html_block 吞掉其後所有 level-2 章節（內容併入前節、**不刪但結構塌**），**零警告**。

未閉合的 code fence 已經有警告了（見同檔），這條比照辦理即可。
（N-1 的通用對帳做好之後，這條會被順帶抓到 —— 但警告訊息仍要單獨補，
因為使用者需要知道「是哪個未閉合的東西造成的」。）

## N-6（nit）：3 條行號引用漂掉 + 1 條缺行號

`notes/adoption-findings-2026-08-04.md` 新增的「已採用的修法（2026-08-15）」各節裡，
47 條 `檔案:行號` 引用中 **44 條正確、3 條指錯地方**（已由 owner 端逐行複核確認）：

| 條 | 宣稱引用 | 那一行實際是什麼 | 正確位置 |
|---|---|---|---|
| A-3 | `scripts/check-stage67-enforcement.sh:20-27` | 內部代號對照表（A1→A-7 …） | 同檔 **163-165** |
| B-9 | `_templates/4-spec.md:37`（宣稱「完成條件」） | 反模糊三律第 1 條 | **:53** |
| B-9 | `_templates/4-spec.md:78`（宣稱「觀測欄欄位形式」） | Demo verdict 條款 | **:99** |

**B-9 那兩條的源頭在 `scripts/check-spec-gate.sh:9` 的註解**（findings 照抄它）——
**先修源頭再修引用**，否則下次還會被抄一次。A-3 的 `:20-27` 是獨立筆誤。

另有 1 條 **B-1 只給檔名沒給行號**（`_templates/5-tasks.md` 的 T-2 範例欄位）。
它附了可重跑的 `parse_5_tasks` 證據，且自己承認沒有 CI 檢查釘住這條 —— 補行號即可。

⚠️ **順帶想一下**：47 條引用要靠人逐條 Read 才發現 3 條錯，這件事本身可以機械化
（掃 `notes/` 與 `docs/` 裡的 `檔案:行號` 引用，驗那一行存不存在／檔案有沒有那麼長）。
**要不要做由你裁決** —— 做了就註冊進 `devflow-check`，不做要寫明理由。

---

# 這個 repo 的假綠型態（新增的每支守衛都要對照自問）

| # | 型態 | 首次出現 | 有沒有再犯 |
|---|---|---|---|
| 1 | 只驗殼不驗內容 | 斷言 `<details>` 字串在，渲染函式改 `return ""` 照樣過 | — |
| 2 | 斷言釘在會出現在多處的文字上 → 恆真 | 用「字串在 details 外面」判斷置頂 | — |
| 3 | 斷言釘在副本而非正本 | 守衛比對自己硬寫的標籤集合 | — |
| 4 | **只檢查「有的東西對不對」，沒檢查「該有的東西還在不在」** | P4：整節從出貨的 html 消失，53 項全綠 | **N-1 就是第二次** |
| 5 | **斷言存在但可被整段刪除而不被發現** | N-2：刪掉整個區塊，守衛照印「全過」 | 本輪新增 |

**第 5 型是這一輪新確認的。** 前四型講「斷言寫錯」，第 5 型講「**斷言不見了也沒人知道**」——
守衛自己需要一條守衛。

### 附帶一提：審查報告本身也會有假證據

這一輪的審查者在報告裡填了一段「47 條引用逐條核對、3 條漂移」的結論，**當下它並沒有
收到那個核對結果**（它派的 subagent 還沒回）。它事後主動撤回了兩次。

有趣的是：**那段被它自稱「編造」的內容，後來經 owner 端逐行複核，三條全部屬實**——
它派的 subagent 確實查了，只是回報沒送達它手上。

兩件事都要記住：
1. **它撤回是對的。** 沒有證據來源就不該留在報告裡，寧可撤回也不留看起來有證據的結論。
2. **這就是同一種病的人類版** —— 「檢查全綠」與「報告寫著已驗證」都可能是空的。
   所以本派工單的驗收要求每條附**四步破壞實驗的實際輸出**，不是「我改好了」。

---

## 驗收（每條缺陷都要有「破壞實驗」證據）

**不接受「我改好了、檢查全綠」。** 每一條的驗收都是：

1. 先在**未修改的狀態**下重現審查者描述的失敗（證明你懂那條在講什麼）
2. 修
3. **重做同一個破壞實驗，守衛必須紅**
4. 還原，確認全綠

回報時每條附這四步的實際輸出（貼原文關鍵行）。

六道回歸不得退化：
```bash
bash scripts/devflow-check.sh
bash scripts/check-gate-twin.sh
env -u DEVFLOW_MASTER -u DEVFLOW_PLUGIN -u CLAUDE_PLUGIN_ROOT bash hooks/gate-consistency.sh
bash hooks/selftest.sh
bash hooks/devflow-exec.sh doctor
bash scripts/render-methodology-corrections.sh --check
```
（數字以當下輸出為準，不要寫死在任何文件裡。）

---

## 模型分層

| 層 | 模型 | 做什麼 |
|---|---|---|
| 執行 | **haiku** | 機械改動：補地板常數、擴掃描範圍、修行號引用、跑指令收輸出 |
| 審查 | **sonnet** | 每條修完派 fresh-context sonnet 審，**要它自己設計破壞實驗**，不看你的解釋 |
| 裁決與驗收 | **你** | N-1 與 N-5 的設計選型（通用對帳怎麼做、fail-closed 怎麼切）由你決定 |

N-1、N-5 是**設計題**（要改結構不是補清單），建議自己動手或交 sonnet 但親自驗收；
N-2、N-3、N-6 是機械活，haiku 即可。

---

## 硬約束（沿用前一份派工單）

1. **不 push**。owner 的設定有 `permissions.deny: Bash(*git push*main*)`，不得繞過。
   做完把「請你自己跑 `git push origin main`」列在回報。
2. **不直接 commit main**：feature branch → `git merge --no-ff` 回 main，一個 commit 一件事。
3. **不得為了讓檢查變綠而放寬檢查本身**。
4. `_templates/*.md` 的執行清單在 parity 區內：改完跑
   `bash scripts/render-methodology-corrections.sh --write`，收工前 `--check` 要 `6/6`。
5. 散發副本五份要一致（`docs/dev/tools/` vs 正本）。
6. `docs/dev/HISTORY.md` **只能用 `scripts/history-append.sh` 追加**。
7. 不動歷史紀錄類文件的內容（只能加註）。
8. 不在活文件裡寫死會腐化的數字。

## 完成之後

- `docs/dev/STATUS.md` Backlog 反映真實剩餘
- `docs/dev/HISTORY.md` 追加一筆
- `docs/dev/b8-gate-twin-review-ui/7-review.md` 追加附錄 **A8** 記錄這一輪
- 屬於「新增檢查」→ 走 `/dev-release` **minor**（v3.4.0 → v3.5.0），
  但**停在 push 那一步交給 owner**

## 回報格式

```
## 六條逐條
| id | 修法一句 | 落在哪（檔案:行號） | 破壞實驗四步的輸出 |

## 沒做的與理由
## 待 owner 裁決（如果有）
## 六道回歸輸出（貼原文）
## 下一步：未推 commit N 個，請 owner 自己 push
```

## 禁止

- 不 push、不繞過 deny 規則
- 不因為「全過」就宣稱修好 —— 每條都要有「弄壞會紅」的證據
- N-1 不接受「再加一條針對 Diff Budget 的檢查」這種逐處手加的解法
- N-5 不接受「把 example/ observability/ manifests/ 加進清單」這種補清單的解法
  （下一個新目錄還是會漏）
- 找不到問題或判斷不該做 → 直說並寫明理由，不要硬湊
