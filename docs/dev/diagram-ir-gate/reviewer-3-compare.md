---
feature: diagram-ir-gate
stage: 7-review
role: reviewer-3-compare
status: draft
verdict: PRE-REVIEW
owner: reviewer-3
updated: 2026-09-12
---

# reviewer-3 比對 — #252 / #253 / #254

> **不是 G3 PASS。不合併。** 本檔只挑一份給 Human 當 G3 正本。
> 判準（owner brief）：最清楚的 Human G3 路徑 + 可核對 `檔:行` + 不發明 PASS。一名贏家。

## 贏家

**#254（impl-C）**  
https://github.com/rick546986/dev-flow/pull/254  
`7-review.md` `verdict: PRE-REVIEW`。Human 仍要自己填判定。

下一動：Human 只讀 #254 → 走它寫死的五步 → 頁尾「提交判定」。不要把本檔或機械綠當成 PASS。#252／#253 當對照，不要並存三份 gate。

## 為什麼是 #254

| 判準 | #252 A | #253 B | **#254 C** |
|---|---|---|---|
| Human G3 路徑 | Verdict → A1 2c → **S-3.2 或 S-1.1**（兩條） | Verdict → S-1.1 → S-2.1／S-4.3 | **Verdict → 中位列 S-3.3 → 16/16・81/81・222 → KL ②／③／⑪ → Quiz A6** |
| Coverage 每列 `檔:行` | 有 | 多數只寫 CASE 名；銷在 A4 | **有；A2 四錨一張卡** |
| 發明 PASS | 無（`PRE-REVIEW`） | 無 | **無；A6 末句鎖「必須由人類寫入」** |
| twin「抽驗」對中位列 | 否（建議 S-3.2／S-1.1） | 否（建議 S-1.1） | **是（S-3.3 = 第 11／21 列）** |

C 的路徑是唯一一條「只做一步就做第 5 步」且對上模板 twin 契約（Coverage Matrix **中位列** `檔:行`）的。

抽驗卡（C 附錄 A2；本 hop 獨立核過）：

| 錨 | 宣稱 | 本 hop 核對 |
|---|---|---|
| 測試 | `scripts/test-diagir.sh:310-315` `S-3.3_dir_as_vbox_family` | `#250` 該段 `want_fail(..., dir-as-vbox.json, DIAGIR_FAMILY)` |
| 信封 | `scripts/fixtures/diagir/dir-as-vbox.json:4-8` `kind=dir-tree`、`why` ≥ 12 | 字面相符 |
| 閘 | `scripts/diagir.py:183-185` `looks_like_tree` → `fail("DIAGIR_FAMILY","tree-as-vbox")` | `:99` 把 `dir-tree` 當 tree；vbox-lifecycle 先擋 tree |
| 現象 | rc=1；`code=DIAGIR_FAMILY`；sha 不變 | 本 hop 親跑：exit 1、`detail=tree-as-vbox`、sha 仍 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc` |

## 本 hop 獨立抽驗（先於採信三包）

產品樹 `#250` = `3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`。未代填 PASS。

**S-1.1**（三包都引用；B 當主抽驗）親跑：

```
exit=1
code=DIAGIR_KIND
target_replaced=false
sha=8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc（不變）
stderr: FAIL DIAGIR_KIND | knob: 把 kind 改回允許值，或改走路由表上的正確家族
```

對得上 `scripts/diagir.py:139-140`（`kind not in VBOX_KINDS`）。

**S-3.3** 見上表。對得上才信 C 其餘 20 列。

**S-2.1** 本 hop **沒有**在完整樹上重跑綠交付（隔離 archive 缺 `build-vbox-fig.py`，`_render_vbox` 紅）。不把三包的 `053bc4df…`／len=1158 當本 hop 親證。Human 走 C 路徑時用 Fresh 三牙數字，不要只信 CASE 名。

三包共用、本 hop 核過的銷：

- `scripts/diagir.py:74-88` 失敗六鍵 + 兩行 FAIL
- `scripts/diagir.py:156-157` 缺 family
- `scripts/devflow_atomic.py:13-22` tmp+`os.replace`
- `scripts/build-dir-tree.py:576-578`／`build-gate-twin.py:2351-2356`／`build-stage1-html.py:483-489`／`:556`／`:759`
- `notes/design/diagir-route.md` 五 id 在 **:8-12**（三包寫 `:7-12`；:7 是表頭分隔列，小不準，共用）
- last-good sha 與 plugin `3.23.3` 相符

## 為什麼不是另外兩包

### #253 B — 最接近的第二名

優點：身分乾淨（≠ Stage 6 `implementer-C`）；閱讀動線頂就釘 `diagir.py:139-140`；A4 是好用的 `檔:行` 索引；唯一把雙份路由表標 **🟡 F-2** 並 park（`scripts/diagir.py:30-66` `ROUTE` vs `diagir-route.md`，本 hop 核過兩份現在對得上）；2c 用本 hop fork → `N_A_NO_INCOMING`，比 A 好讀。

落敗：Coverage Matrix 多數列沒有 `檔:行`（只寫 CASE）。Human 若「只做第 5 步、從矩陣點一列」會踩空，要跳去 A4。沒有寫好的 Quiz。抽驗不是中位列。

### #252 A — 矩陣密、路徑分叉

優點：21 列都有 `檔:行`；A4 有 S-1.1 原文；不發明 PASS。

落敗：建議抽 **S-3.2 或 S-1.1** —— 不是一條路。2c 主敘是 6-notes FORK 的 `ALREADY_SYNCED`，Human 要先懂恢復路徑 ①。沒標 B 的 🟡 雙表、也沒標 C 的 twin 罐頭 payload。圍欄寫「exec 未武裝」。

## C 的折扣（不改贏家）

1. **身分**：`implementer-C-stage7` 與 Stage 6 同標。C 自己寫「不保證四眼被 hook 擋住」。session 不同（`bc-e842c9ff` ≠ `#250` `bc-5ab0653d`）。owner brief 沒把身分當選包條件；若 Human 要最乾淨四眼，改用 #253，但矩陣 `檔:行` 較弱。
2. **2c**：C／B 用本 hop fork = `N_A_NO_INCOMING`。A 用 Stage 6 FORK = `ALREADY_SYNCED`。兩邊都合法；C 附錄 A1 有講清楚，不要拿 6-notes 錨當「沒有共同戰場」。
3. **Gauntlet 次數** A 65／B 91／C 67：表列數不同，不是誰造假。Gauntlet 綠 ≠ G3 PASS。

## Human 最短路徑（用贏家包）

1. 打開 #254 `7-review.md` **Verdict** 門檻表。確認 `verdict:` 仍是 `PRE-REVIEW`。
2. 抽驗 **S-3.3**：`scripts/test-diagir.sh:310` + `scripts/fixtures/diagir/dir-as-vbox.json:4` + `scripts/diagir.py:183-185`。對不上整份退回。
3. 看 Fresh 三牙：vbox-fig 16/16、dir-tree 81/81、gate-twin 222。不要只信 `test-diagir` S-4.2 CASE（C F-3／KL ④）。
4. 讀 Known Limits **②**（Source SHA 綁產品樹、docs commit 會漂）、**③**（twin `require_write` 驗罐頭兩步，不是頁 HTML；`build-gate-twin.py:2343-2356`）、**⑪**（Stage 6 T review 是 self-check）。
5. 答附錄 A6 五題。全對才准把 `verdict:` 改成 Human PASS，且必須人類寫入。

全勾 Exit ≠ PASS。不要 merge #252／#253／#254，直到 Human 在贏家包上簽名。
