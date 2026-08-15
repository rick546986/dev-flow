#!/bin/bash
# Stage 6/7 執行期強制條款守衛(Repo-local,REPO_REFERENCE only)。
#
# 起因(2026-08 order-intake 真實執行,26 個 T 全程):四條「寫在散文裡、沒有任何
# 機械檢查」的規則同時失效,而每一份產出看起來都完整:
#
#   A1 守衛沉睡  `.devflow/exec.json` 不存在時 guard hook 直接 sys.exit(0)
#                (devflow-lib.py::load_state 註解原文「真的沒在執行 → 沉睡」)。
#                該 feature 因 devflow-exec.sh 啟動失敗(D-9)從未武裝 →
#                圍欄②/契約防篡改/scope 三道全程沒觸發,沒有任何訊號。
#   A3 Verify 假綠 `-run '<pattern>'` 沒匹配到測試時 runner 回 exit 0。實測 T-25 的
#                Verify 在還沒寫任何測試的 HEAD 上跑出 `=== RUN` 0 行、exit 0、
#                並印出 `T-25 PASS`。
#   A4 gauntlet 路徑 模板寫死 `docs/dev/tools/...`,該目錄在採用專案不存在 →
#                Evidence 層靜默跳過,7-review 照樣填得完。
#   A5 觀測不可執行 4-spec 的觀測欄可以寫「前端畫面」,而前端在另一 repo 且未實作 →
#                7-review 步 2b 的「現象證據逐 S 相符」(PASS 條件之一)結構上做不到,
#                到 G3 才發現。
#
# ⚠️ 上面 A1/A3/A4/A5 是**本檔內部代號**,不是 notes/adoption-findings-2026-08-04.md
# 的條號——那份 findings 檔的對照是 A1→A-7、A3→A-8、A4→A-9、A5→A-10(findings 檔本身
# 已註明過這個對照,勿混)。以下兩組是後續追加,**改用不同前綴避免二次混淆**:
#
#   VF Verify 單行純指令  findings A-3。`verify_command_match` 字串全等 + `FIELD_RE`
#                只吃行尾,模板原本沒有任何一句警告「Verify 必須單行」。實測:採用
#                專案 18 個 T 有 17 個 Verify 欄被中文說明汙染同一行,另有把 Verify
#                寫成多行 fenced code block、解析器一個字都抓不到的案例。
#   DOC doctor 必跑    findings A-12(原 C-3)。`dev-setup` 沒散發齊時 doctor 實跑
#                fail-closed 沒問題,但沒有任何 Stage 要求跑它,於是這個 fail-closed
#                檢查從未被觸發,缺件靜默通過整條 Stage 6→7。
#
# 本守衛不判斷內容好壞,只驗「模板與範例有沒有把這幾條變成可查的硬條款」。
# 邊界:本檔只掃**本 repo 的模板與範例**;採用專案的 runtime 強制屬外部 plugin。
#
# 用法:
#   scripts/check-stage67-enforcement.sh [root]   # 缺省 = repo root
#
# 退出碼:0 = 全過;1 = 有條款缺失(逐條列出);2 = 用法錯誤。

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  case "$1" in
    -h|--help|help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) ROOT=$(cd "$1" 2>/dev/null && pwd) || { echo "找不到 root: $1" >&2; exit 2; } ;;
  esac
fi

python3 - "$ROOT" <<'PY'
import os
import re
import sys

root = sys.argv[1]
fails = []
checks = 0


def read(rel):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def need(cond, msg):
    """cond 為 False 即記一條失敗。每呼叫一次算一項檢查。"""
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


# ── A1:守衛武裝自檢必須寫進 Stage 6 與 Stage 7 的步 0 ────────────────────────
#
# needle 選「守衛武裝自檢」與 `.devflow/exec.json` 兩個字面:前者是條款名(人找得到),
# 後者是**它為什麼存在的根因**(拿掉根因就只剩一句沒有牙齒的提醒)。
for rel in ("_templates/6-implementation-notes.md", "_templates/7-review.md"):
    src = read(rel)
    need(src is not None, f"A1:{rel} 不存在")
    if src is None:
        continue
    need("守衛武裝自檢" in src,
         f"A1:{rel} 的執行清單缺「守衛武裝自檢」硬關卡 —— "
         f"守衛沒武裝與沒在用 dev-flow 在系統裡長得一模一樣")
    need(".devflow/exec.json" in src,
         f"A1:{rel} 沒寫出根因 `.devflow/exec.json`(guard 靠它判斷要不要醒)")
    need("devflow-exec.sh status" in src,
         f"A1:{rel} 沒給可執行的自檢指令 `devflow-exec.sh status`")

# ── DOC:doctor 必跑(findings A-12,原 C-3)────────────────────────────────────
#
# needle 選 `devflow-doctor.sh`(可執行指令本身)、`INCOMPATIBLE`(doctor fail-closed
# 時的回報字面,拿掉就變成一句沒有判準的提醒)、`停下回報`(處置動作本身,不能只是
# 「注意一下」)。三者缺一,doctor 這個 fail-closed 檢查就又會回到「存在但沒人跑」。
for rel in ("_templates/6-implementation-notes.md", "_templates/7-review.md"):
    src = read(rel)
    need(src is not None, f"DOC:{rel} 不存在")
    if src is None:
        continue
    need("devflow-doctor.sh" in src,
         f"DOC:{rel} 的守衛武裝自檢旁沒有要求跑 `devflow-doctor.sh`(或 "
         f"`devflow-exec.sh doctor`)—— fail-closed 版本握手檢查存在,但沒有觸發點")
    need("INCOMPATIBLE" in src,
         f"DOC:{rel} 沒寫出 doctor 的 fail-closed 回報字面 `INCOMPATIBLE`")
    need("停下回報" in src,
         f"DOC:{rel} 沒把 `INCOMPATIBLE` 的處置釘死成「停下回報」,少了它會被自由心證略過")

# ── A3:Verify 的篩選器假綠 ──────────────────────────────────────────────────
src = read("_templates/5-tasks.md")
need(src is not None, "A3:_templates/5-tasks.md 不存在")
if src:
    need("=== RUN" in src,
         "A3:_templates/5-tasks.md 沒給「數案例數」的具體做法(缺 `=== RUN` 骨架)")
    need(re.search(r"-run.{0,40}(沒匹配|零匹配|沒有匹配)", src, re.S) is not None
         or "篩選器" in src,
         "A3:_templates/5-tasks.md 沒說明「篩選器沒匹配也回 exit 0」這個假綠來源")
    need("原樣跑一次" in src,
         "A3:_templates/5-tasks.md 缺「Verify 開工前原樣跑一次」的條款 —— "
         "少了它,不可能綠/已經綠的 Verify 欄要到做完才發現")

# ── A3 的範例承接:範例必須示範正確做法,不能自己違規 ─────────────────────────
#
# 這一項是「守衛跑得過 ≠ 擋得住」的關鍵:條款只寫在模板註解裡沒人照做,
# 範例才是實際被抄的東西。
for base, _dirs, files in os.walk(os.path.join(root, "example")):
    if "5-tasks.md" not in files:
        continue
    rel = os.path.relpath(os.path.join(base, "5-tasks.md"), root)
    with open(os.path.join(base, "5-tasks.md"), encoding="utf-8") as fh:
        body = fh.read()
    for line in body.splitlines():
        if not line.startswith("- Verify:"):
            continue
        # 只管真的用了篩選器的行
        if not re.search(r"(?<![\w-])(-run|-k|--filter)(?![\w-])", line):
            continue
        need("=== RUN" in line or "grep -c" in line,
             f"A3:{rel} 的 Verify 用了測試篩選器卻沒有案例數斷言 —— "
             f"沒匹配到測試時 runner 回 exit 0,該欄退化成「測試不存在也算過」:\n"
             f"        {line.strip()}")

# ── VF:Verify 必須單行純指令(findings A-3;不要跟上面的內部代號 A3 搞混,
#    A3 = findings A-8 的篩選器假綠,VF = findings A-3 的單行純指令紀律)───────
#
# needle 挑「可原樣貼進 shell 的純指令」與「會吞掉同行其後全部內容」:兩句都是
# A-3 這條紀律**獨有**的字面,不跟 A-8(=== RUN / 原樣跑一次)的 needle 重疊,
# 才能證明這裡新加的檢查、不是誤觸別條舊檢查。
src = read("_templates/5-tasks.md")
need(src is not None, "VF:_templates/5-tasks.md 不存在")
if src:
    need("可原樣貼進 shell 的純指令" in src,
         "VF:_templates/5-tasks.md 沒有「Verify 必須是單行、可原樣貼進 shell 的純指令」"
         "這條硬紀律")
    need("會吞掉同行其後全部內容" in src,
         "VF:_templates/5-tasks.md 沒提醒「# 會吞掉同行其後全部內容」這個已知陷阱")

# ── VF 的範例承接:掃 example/*/5-tasks.md 每個 `- Verify:` 值 ────────────────
#
# 裁決(2026-08-15,寫進本檔供日後查對):採用專案的 Verify 欄含中文 grep 字串
# (例如 `grep -c '訂單已核准'`)是合法用法,**runtime 不加這道檢查**——會誤殺。
# 本檔只掃**母版自己的範例**,母版範例的 Verify 值本就該是純英文/程式碼指令,
# 出現 CJK 字元幾乎必然是「指令 + 中文說明混寫成一行」(findings A-3 的原始成因);
# 以 ``` 開頭則是「多行 fenced code block 誤當單行欄位」的另一種成因。
_CJK_RE = re.compile(r"[一-鿿　-〿＀-￯]")
for base, _dirs, files in os.walk(os.path.join(root, "example")):
    if "5-tasks.md" not in files:
        continue
    rel = os.path.relpath(os.path.join(base, "5-tasks.md"), root)
    with open(os.path.join(base, "5-tasks.md"), encoding="utf-8") as fh:
        body = fh.read()
    for line in body.splitlines():
        if not line.startswith("- Verify:"):
            continue
        value = line[len("- Verify:"):].strip()
        need(not _CJK_RE.search(value),
             f"VF:{rel} 的 Verify 值含 CJK/全形字元,疑似指令與說明混寫成單行:\n"
             f"        {line.strip()}")
        need(not value.startswith("```"),
             f"VF:{rel} 的 Verify 值以 fenced code block(```)開頭 —— "
             f"解析器只吃單行,寫成多行 fence 一個字都抓不到:\n"
             f"        {line.strip()}")

# ── TF:測試檔路徑必須列進 Files(D-39 紀律的機械檢查)────────────────────────
#
# needle 挑「測試檔路徑也要列進」+ backtick 包住的「Files」:這是模板既有的紀律句
# 本身(worker 寫測試就是寫檔,測試檔不在 Files 聯集內會被 Stage 6 scope guard
# 當場擋死)。沿用上面 VF 段已讀過的 `src`(同一份 _templates/5-tasks.md),不重覆
# 存在性檢查。
if src:
    need("測試檔路徑也要列進 `Files`" in src,
         "TF:_templates/5-tasks.md 沒有「測試檔路徑也要列進 Files」這條紀律句 —— "
         "worker 寫測試卻沒把測試檔列進 Files,會被 Stage 6 scope guard 當場擋死"
         "卻找不到原因")

# ── TF 的範例承接:example 逐 T,Verify 是跑測試的 T,Files 必含至少一個測試路徑 ──
#
# 起因:D-39(order-intake 實測歸納)—— 幾乎每個 T 的 Verify 都在跑測試,對應的
# 測試檔(`*_test.go`／`*.test.tsx`／`*.spec.ts` 等)必須跟業務碼一起列進本 T 的
# Files,否則 candidate 產出前就被 PreToolUse scope guard 擋死。這裡把提醒句變成
# 對母版範例的機械檢查。pattern 依 example 實況定(不是題目字面三選項的子集)——
# e2e 用 `.spec.ts`、go 用 `_test.go`、前端用 `.test.tsx`,三者都要認得到,否則
# T-4(純 e2e 測試檔的 T)會被誤判違規。
# 用同一個 need() 承接全部 T(不逐 T 各自計數)以維持 MIN_CHECKS +2 的精確地板;
# 但同時釘 examined>=1,避免「## T-n 形狀被改、parser 一個 T 都沒解析到」時
# violations 恆空、看起來像全過的 vacuous-truth 陷阱(同檔 RW-2 案的教訓)。
_TEST_VERIFY_RE = re.compile(r"\btest\b", re.I)
_TEST_FILE_RE = re.compile(r"(_test\.\w+|\.test\.\w+|\.spec\.\w+|(^|/)tests?/)", re.I)
for base, _dirs, files in os.walk(os.path.join(root, "example")):
    if "5-tasks.md" not in files:
        continue
    rel = os.path.relpath(os.path.join(base, "5-tasks.md"), root)
    with open(os.path.join(base, "5-tasks.md"), encoding="utf-8") as fh:
        body = fh.read()
    blocks = re.split(r"(?m)^## (T-\d+)", body)[1:]
    examined = 0
    violations = []
    for i in range(0, len(blocks), 2):
        tid, block = blocks[i], blocks[i + 1]
        verify_m = re.search(r"^- Verify:\s*(.+)$", block, re.M)
        files_m = re.search(r"^- Files:\s*(.+)$", block, re.M)
        if not verify_m or not files_m:
            continue
        if not _TEST_VERIFY_RE.search(verify_m.group(1)):
            continue
        examined += 1
        if not _TEST_FILE_RE.search(files_m.group(1)):
            violations.append(f"{tid}(Files={files_m.group(1).strip()})")
    detail = ("\n".join(f"        {v}" for v in violations) if violations
              else "        (examined=0 —— 一個跑測試的 T 都沒解析到,"
                   "parser 對不上模板形狀,比條款失效更嚴重)")
    need(examined >= 1 and not violations,
         f"TF:{rel} 有跑測試的 T 但 Files 欄缺測試路徑"
         f"(examined={examined},缺 tests/ 或 *_test.* 或 *.test.* 或 *.spec.* pattern):\n"
         f"{detail}")

# ── A4:gauntlet 路徑不得寫死成採用專案不存在的路徑 ──────────────────────────
src = read("_templates/7-review.md")
need(src is not None, "A4:_templates/7-review.md 不存在")
if src:
    # ⚠️ 2026-08-07 更正:`docs/dev/tools/` 是 dev-setup 的散發契約
    # (skills/dev-setup/SKILL.md:69),路徑本身**沒有錯**。原本這裡檢查
    # 「不得出現該路徑」是誤診 —— 真正的缺陷是「檔案不在時沒有人被擋」。
    # 故改成:必須寫出正確路徑,且必須把補救指向**補跑 dev-setup**。
    need("docs/dev/tools/devflow-evidence-gauntlet.sh" in src,
         "A4:_templates/7-review.md 沒寫出 gauntlet 的正式散發路徑 "
         "`docs/dev/tools/devflow-evidence-gauntlet.sh`(dev-setup 的散發契約)")
    # needle 用**補救動作那句話**而不是裸的 "dev-setup":後者會被
    # 「skills/dev-setup/SKILL.md:69」這種出處引用滿足,測不出補救被改掉。
    need("補跑 `dev-setup`" in src,
         "A4:_templates/7-review.md 沒把「檔案不在」的補救指向**補跑 dev-setup** —— "
         "手動 cp 會繞過受管檔的版本握手")
    need("test -x" in src,
         "A4:_templates/7-review.md 沒要求開工前確認 gauntlet 真的存在(缺 `test -x`)")
    need("降級" in src,
         "A4:_templates/7-review.md 沒規定「裝不了就明記為降級」—— "
         "沒有這條就會默默當成跑過")
    # 母版必須真的在 scripts/,否則上面那句安裝指引也是空的
    need(os.path.exists(os.path.join(root, "scripts/devflow-evidence-gauntlet.sh")),
         "A4:母版 scripts/devflow-evidence-gauntlet.sh 不存在,安裝指引指向空氣")

# ── A5:觀測方式必須在本 repo 可執行 ─────────────────────────────────────────
spec = read("_templates/4-spec.md")
need(spec is not None, "A5:_templates/4-spec.md 不存在")
if spec:
    need("觀測方式必須在本 repo 可執行" in spec,
         "A5:_templates/4-spec.md 的觀測欄沒規定「必須在本 repo 可執行」—— "
         "寫下做不到的觀測 = 在 G2 就種下一個 G3 必然的 ❌")
    need(re.search(r"觀測[^\n]{0,80}n-a", spec) is not None
         or "標 `n-a:" in spec,
         "A5:_templates/4-spec.md 沒給「做不到時當場標 n-a 並補替代觀測」的出口")
rev = read("_templates/7-review.md")
if rev:
    need("結構上做不到" in rev,
         "A5:_templates/7-review.md 的現象證據節沒呼應「觀測指向本 repo 之外時」的處置")

# ── 檢查數地板:防止有人把上面整段刪成空迴圈仍然 exit 0 ──────────────────────
# ⚠️ 這個數字必須**等於當下的實際檢查數**,不是「大概抓個下限」。
# 負向測試 S67-6 實測:原本填 16(A1 那組恰好 8 項,24-8=16)→ 刪掉整組 A1 之後
# 剛好等於地板,守衛照樣 exit 0。地板留餘裕 = 地板沒有牙齒。
# 新增檢查時把這個數字一起往上調(同 test-architecture-guards.sh 的 EXPECTED_* 體例)。
# 2026-08-16 補 TF 群組(測試檔路徑必須列進 Files):+2(模板 needle 1 + 範例承接 1)。
MIN_CHECKS = 52
if checks < MIN_CHECKS:
    fails.append(f"⛔ 實際只跑了 {checks} 項檢查(地板 {MIN_CHECKS})—— "
                 f"檢查本身被刪掉或迴圈跑了零圈,這比條款失效更嚴重")

if fails:
    print(f"⛔ check-stage67-enforcement: {len(fails)} 條失敗(共跑 {checks} 項)")
    for f in fails:
        print(f"  ❌ {f}")
    raise SystemExit(1)

print(f"✅ check-stage67-enforcement: Stage 6/7 強制條款齊({checks} 項檢查全過)")
print("   A1 守衛武裝自檢 / A3 Verify 案例數斷言 / A4 gauntlet 路徑 / A5 觀測可執行性 / "
      "VF Verify 單行純指令 / DOC doctor 必跑 / TF 測試檔路徑必列 Files")
PY
