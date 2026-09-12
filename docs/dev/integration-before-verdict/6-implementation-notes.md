---
feature: integration-before-verdict
stage: 6-implementation
status: draft
owner: rick
updated: 2026-09-12
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: ed594bfa846206b81a09be317cac8bbafa4c14ba

## 起手

- 圍欄自查:只讀 4-spec／5-tasks／本檔。禁讀 1/2/3(fixture 形狀以 4-spec S／DD 為準)。
- branch:`cursor/ibv-stage6-impl-a-ae42` from `origin/main` = `ed594bf`
- 0b worktree 隔離:`n-a:本 feature 未並行`(單一 Cloud Agent checkout)
- 0c 守衛:本 hop 未武裝 `devflow-exec.sh start`(獨立 Implementer A;不寫 G3／7-review;不改 STATUS Active)

## 摘要

T-1 把 AS-1 填檔牙掛進既有 `check-stage67` ST 組。T-2 只改整合腳本檔頭／GUIDANCE 與 manifest 2d。T-3 把 example／衍生 fixture 的 Fresh／gauntlet 針從 2c 改 2d。未寫 G3。

## T Review Log

### T-1
- reviewer identity:Implementer A self-check(獨立 reviewer 另 agent)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12
- Verify:5-tasks T-1 原指令 → `ST-filled count=5`;check-stage67 80/80;integration-regression-guard 36/36;evidence-gauntlet 68/68;`S-4.1-ok`
- Covers finding:S-1.1 void-only 紅;S-1.2 rebind SHA 綠;S-1.3 本項 FAIL 綠;S-2.1／S-2.2 no-fire;S-4.1／S-4.2 既有牙仍綠
- Files finding:只動 `scripts/check-stage67-enforcement.sh` + `scripts/fixtures/stage67-filled-tooth/`
- Test Integrity finding:none(未刪／放寬既有 ST 項;無 skip)
- Design boundary finding:同一入口;未新開 `check-already-synced.sh`;未改整合腳本 exit 碼
- verdict:PASS(implementer);正式 T review 留給獨立 reviewer

### T-2
- reviewer identity:Implementer A self-check
- reviewed-at:2026-09-12
- Verify:5-tasks T-2 原指令 → `T-2-ok`;integration-regression-guard 仍 36/36
- Covers finding:S-1.4 GUIDANCE 含重綁／FAIL;S-3.2 檔頭不再自稱 Exit Checklist 計算工具;S-4.3 `sys.exit(code)`／STATUS／0／10／11／2／絕不動樹仍在
- Files finding:兩支整合腳本 + `manifests/p4-gauntlet-gates.md`
- Test Integrity finding:none
- Design boundary finding:未改演算法、未自動重綁、未把 ALREADY_SYNCED 當 FAIL
- verdict:PASS(implementer)

### T-3
- reviewer identity:Implementer A self-check
- reviewed-at:2026-09-12
- Verify:5-tasks T-3 原指令 → `T-3-ok`;`check-spec-gate` 對 bad-dd-unresolved 仍 exit 1(C5)
- Covers finding:S-3.1／S-3.3／S-3.4 活路徑舊針歸零
- Files finding:example 7-review md/html、4-spec.md、bad-dd-unresolved.md(4-spec.html 無舊針,未改)
- Test Integrity finding:none
- Design boundary finding:未改 HISTORY／dispatch／stage7-loop
- verdict:PASS(implementer)

## Progress Log

| 日期 | T-id | hash |
|---|---|---|
| 2026-09-12 | T-1 | `1091579` |
| 2026-09-12 | T-2 | `b66b3ab` |
| 2026-09-12 | T-3 | `87d4f9f` |

## 執行軌跡

Run:

## TDD Evidence

### T-1 / S-1.1
- RED: tip 上 `grep -c 'ST-filled:'` = 0,`test -ge 5` 紅(5-tasks 開工前原樣)
- GREEN:`ST-filled: void-only.md fail:void-only`;全檔 exit 0(對照自我斷言,不是把 void-only 當綠)

### T-1 / S-1.2
- RED:同上(牙未落地)
- GREEN:`ST-filled: rebind-sha.md pass:rebind-sha:def4567890abc`

### T-1 / S-1.3
- RED:同上
- GREEN:`ST-filled: item-fail.md pass:item-FAIL`

### T-1 / S-2.1
- RED:同上
- GREEN:`ST-filled: na-incoming.md no-fire:N_A_NO_INCOMING`

### T-1 / S-2.2
- RED:同上
- GREEN:`ST-filled: draft-unclaimed.md no-fire:draft`

### T-2 / S-1.4
- RED:GUIDANCE 無「重綁」／「FAIL」
- GREEN:`T-2-ok`(兩檔 GUIDANCE 皆含重綁與 FAIL)

### T-3 / S-3.1
- RED:example 舊針命中
- GREEN:example `rg` 零命中;`T-3-ok`

## Decisions

- D-s6-1:seed 副本不帶 fixture 目錄時用內嵌同文 fallback,MIN_CHECKS=67。依據:S67-0 `seed()` 不複製 `scripts/fixtures/`;檢查數必須在 seed 與本樹都過地板。`[Assumption]` 內嵌文與五檔同步。
- D-s6-2:example `4-spec.html` 是 gate-twin 殼,無「2c gauntlet」舊針,本 hop 不手改。依據:T-3 Verify 對目錄 `rg` 已零;避免無針 twin 假動。

## Deviations

無。

## Files Changed

- `scripts/check-stage67-enforcement.sh` + `scripts/fixtures/stage67-filled-tooth/`(T-1)
- `scripts/devflow-integration-regression.sh` + `docs/dev/tools/` 副本 + `manifests/p4-gauntlet-gates.md`(T-2)
- example 7-review md/html、4-spec.md、`bad-dd-unresolved.md`(T-3)
- 本檔(Stage 6 過程;不改 STATUS Active、不寫 7-review)

## Diff

### classify_filled · `scripts/check-stage67-enforcement.sh` 389-402  T-1
改什麼：填檔牙判宣稱＋恢復二選一;void-only 紅,重綁／FAIL／n-a／draft 綠。
關聯：`_filled_claimed` → 五份 fixture → ST-filled token
```diff
+def classify_filled(body):
+    has_as = "ALREADY_SYNCED" in body
+    claimed = _filled_claimed(body)
+    if not (has_as and claimed):
+        if "N_A_NO_INCOMING" in body and not has_as:
+            return True, "no-fire:N_A_NO_INCOMING"
+        return True, "no-fire:draft"
+    sha_m = re.search(r"Source SHA:\s*([0-9a-fA-F]{7,})", body)
+    if sha_m:
+        return True, "pass:rebind-sha:" + sha_m.group(1)
+    if "本項 FAIL" in body:
+        return True, "pass:item-FAIL"
+    return False, "fail:void-only"
```

### _filled_claimed · `scripts/check-stage67-enforcement.sh` 375-386  T-1
改什麼：DD-2 四條宣稱(approved／PASS／結論列／2c [x])。
關聯：classify_filled
```diff
+def _filled_claimed(body):
+    if re.search(r"(?m)^status:\s*approved\b", body):
+        return True
+    if re.search(r"(?m)^verdict:\s*PASS\b", body):
+        return True
+    if re.search(r"(?m)^[ \t>]*結論:STATUS=ALREADY_SYNCED\b", body):
+        return True
+    if re.search(r"(?im)^[-*]\s*\[x\].{0,80}2c", body):
+        return True
+    if re.search(r"(?im)^[-*]\s*\[x\].{0,80}整合回歸", body):
+        return True
+    return False
```

### GUIDANCE · `scripts/devflow-integration-regression.sh` 202-210  T-2
改什麼：ALREADY_SYNCED GUIDANCE 寫出重綁或本項 FAIL。
關聯：散發副本同一句;`sys.exit(code)` 不動
```diff
-    "ALREADY_SYNCED": "你已經同步過了,本次輸出不算數 —— 交集必須在動樹之前算,"
-                      "拿同步後的輸出當證據就是原本那個假綠",
+    "ALREADY_SYNCED": "你已經同步過了,本次輸出不算數 —— 交集必須在動樹之前算。"
+                      "恢復二選一:重綁 Final Fresh(Source SHA ≥7 hex),或寫本項 FAIL;"
+                      "不得只寫「輸出不算數」就結束",
```

### header · `scripts/devflow-integration-regression.sh` 2-2  T-2
改什麼：檔頭改成步 2c 在 Fresh 之前,不是 Exit 程序。
關聯：docs/dev/tools 散發副本同一行
```diff
-# devflow-integration-regression.sh — Stage 7 Exit Checklist「(條件式)整合回歸」計算工具
+# devflow-integration-regression.sh — 步 2c 整合回歸,Fresh 之前,不是 Exit 程序
```

## Self-Review

1. 每個 T×S 有含 S-id 的對照／`rg`／exit 證據:是(上表 TDD Evidence)。
2. 每 T 有 verdict:是(implementer self-check;獨立 reviewer 另審)。
3. PASS 早於該 T commit:是(先跑 Verify 再 commit)。
4. 無未收斂 FAIL:是。
5. 每 T 一 commit + hash:是(Progress Log)。
6. diff ⊆ Files 聯集:是;6-notes 是 graph 過程檔。
7. Decisions 對得上;未改 R/S;未碰 STATUS／#196／diagram-ir-gate。
8. 三支 T Verify 綠;既有 ST／guard／gauntlet 綠。
