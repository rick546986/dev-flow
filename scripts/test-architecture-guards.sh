#!/bin/bash
# 架構守衛的**負向回歸測試**(常設,進 CI)。
#
# 為什麼存在:守衛「跑得過」不代表「擋得住」。一次性的 mutation 結果寫在 PR 說明裡,
# 下一個人改壞守衛時沒有任何東西會紅。本檔把最關鍵的負向案例釘成 repo 內的常設測試,
# 每次 PR 由 GitHub Actions 重跑。
#
# 涵蓋(每案都是「變異 → 守衛必須失敗」;另有未變異對照組必須通過):
#   Design Contract  DC-0 對照組 / DC-1 Risk high→normal / DC-2 applicable→n-a
#                    DC-3 刪 Data owner 欄 / DC-4 canon 壞例(Forbidden「無」+ 模糊詞)
#                    DC-5 刪 Template Applicability / DC-6 刪 Stage 7 承接
#                    DC-7 finding 全改 n-a / DC-8 只填① / DC-9 finding 留空
#   Gate Token       GT-0 對照組 / GT-1 刪 G2 一個 token / GT-2 G3 token 去粗體
#                    GT-3 刪 G3 錨定義八點中的一點 / GT-4 憑空新增 G4
#                    GT-5a~d 八點極性反轉 / GT-6a 同句 decoy / GT-6b 片語搬到別點
#   Version Sync     VS-0 對照組 / VS-1 README 9.9.9 / VS-2 contract 9.9.9
#                    VS-3 design doc 9.9.9 / VS-4 版本錨被刪
#   Guard Source     GS-0a/0b 對照組 / GS-1~GS-8 變異**守衛本體**(含 co-edit 守衛+資料)
#
# 案例數是**斷言**不是裝飾:EXPECTED_CONTROLS / EXPECTED_NEGATIVES / EXPECTED_TOTAL
# 由 expect()/expect_local() 實際累計後比對,刪任何一案(含對照組)都會非零退出。
#
# 安全(fail-closed,正式 working tree 全程唯讀):
#   - set -euo pipefail;所有變數非空檢查
#   - 暫存根目錄由 mktemp -d 產生,且必須落在 /tmp 或 /private/tmp 前綴內才動它
#   - 刪除前印出完整 target;拒絕刪除空值、根目錄、或前綴外路徑
#   - 只複製守衛會讀到的**資料檔**;守衛本體仍從正式 repo 執行,以 root 參數指向暫存副本
#   - 結束時比對正式 repo 的檔案指紋,證明未被污染
#
# 用法:scripts/test-architecture-guards.sh        (由 devflow-check.sh architecture 呼叫)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${ROOT:?ROOT is empty}"
[[ -f "$ROOT/README.md" ]] || { echo "ROOT 不像 dev-flow repo:$ROOT" >&2; exit 2; }

# 動手前的正式 repo 指紋(結束比對用)
fingerprint() {
  find "$ROOT/README.md" "$ROOT/devflow-contract.json" "$ROOT/_templates" \
       "$ROOT/example" "$ROOT/notes/design" "$ROOT/scripts" \
       -type f -exec shasum {} + 2>/dev/null | shasum | awk '{print $1}'
}
FP_BEFORE=$(fingerprint)
: "${FP_BEFORE:?fingerprint failed}"

WORK=$(mktemp -d "${TMPDIR:-/tmp}/devflow-guard-regression.XXXXXX")
: "${WORK:?mktemp failed}"
[[ "$WORK" == /tmp/* || "$WORK" == /private/tmp/* || "$WORK" == /var/folders/* ]] || {
  echo "暫存目錄不在允許的前綴內:$WORK" >&2; exit 1; }

safe_rm() {
  local target="${1:-}"
  : "${target:?safe_rm: target is empty}"
  [[ "$target" == /tmp/* || "$target" == /private/tmp/* || "$target" == /var/folders/* ]] || {
    echo "safe_rm 拒絕:目標不在允許前綴內:$target" >&2; exit 1; }
  [[ "$target" != "/" && "$target" != "/tmp" && "$target" != "/private/tmp" ]] || {
    echo "safe_rm 拒絕:不得刪除根或前綴本身:$target" >&2; exit 1; }
  rm -rf -- "$target"
}
cleanup() { safe_rm "$WORK"; }
trap cleanup EXIT

PASS=0
FAIL=0
RESULTS=()
# ── 精確案例數地板(2026-08 final verdict M-2)────────────────────────────────
# 舊版只有 PASS/FAIL 兩個計數,尾聲的「5 對照組」是硬編字串、從不參與比對。
# 實測(fresh reviewer 重現):刪掉整個 GS-8 負向案 → 仍印「30/30 全過(5 對照組…)」、exit 0;
# 只刪 GS-0b 對照組一行 → 仍印「5 對照組」、exit 0。也就是那行摘要是裝飾,不是斷言。
# 改法:由 expect()/expect_local() 依 want 實際累計 control 與 negative,尾聲與釘死值比對。
CONTROL_RUN=0     # 實際跑過的「未變異必須 pass」對照組
NEGATIVE_RUN=0    # 實際跑過的「變異必須 fail」負向案
EXPECTED_CONTROLS=7
EXPECTED_NEGATIVES=43
EXPECTED_TOTAL=50

count_case() { # count_case <pass|fail>
  if [ "$1" = "pass" ]; then CONTROL_RUN=$((CONTROL_RUN + 1)); else NEGATIVE_RUN=$((NEGATIVE_RUN + 1)); fi
}

# seed <name> → 在 $WORK/<name> 建一份「守衛會讀到的資料檔」副本,印出完整路徑
seed() {
  local name="${1:?seed: name is empty}"
  local dst="$WORK/$name"
  [[ "$dst" == "$WORK/"* ]] || { echo "seed: 目標逃逸 $dst" >&2; exit 1; }
  safe_rm "$dst"
  mkdir -p "$dst/_templates" "$dst/example/contract-expiry-reminder" \
           "$dst/notes/design" "$dst/scripts"
  cp "$ROOT/README.md" "$dst/README.md"
  cp "$ROOT/devflow-contract.json" "$dst/devflow-contract.json"
  cp "$ROOT"/_templates/{4-spec,5-tasks,6-implementation-notes,7-review}.md "$dst/_templates/"
  cp "$ROOT"/example/contract-expiry-reminder/{4-spec,5-tasks,6-implementation-notes,7-review}.md \
     "$dst/example/contract-expiry-reminder/"
  cp "$ROOT"/notes/design/{design-boundary-contract,evidence-gauntlet}.md "$dst/notes/design/"
  cp "$ROOT/scripts/devflow-evidence-gauntlet.sh" "$dst/scripts/"
  echo "$dst"
}

# expect <pass|fail> <guard-script> <root> <label>
expect() {
  local want="${1:?}" guard="${2:?}" target="${3:?}" label="${4:?}"
  [[ "$target" == "$WORK/"* ]] || { echo "expect: root 逃逸 $target" >&2; exit 1; }
  count_case "$want"
  local out rc got
  out=$("$ROOT/scripts/$guard" "$target" 2>&1)
  rc=$?
  got=pass; [ "$rc" -ne 0 ] && got=fail
  if [ "$got" = "$want" ]; then
    RESULTS+=("  ✅ $label — 預期 $want,實得 $got")
    PASS=$((PASS + 1))
  else
    RESULTS+=("  ❌ $label — 預期 $want,實得 $got (exit $rc)")
    RESULTS+=("       $(printf '%s' "$out" | tail -3 | tr '\n' ' ')")
    FAIL=$((FAIL + 1))
  fi
}

# seed_guard <name> <guard-script…> → 同 seed(),外加把指名的**守衛本體**複製進
# $WORK/<name>/scripts/。用於「守衛自己被改弱」這一類負向案 —— 這是原本整個缺的一類:
# 舊版本檔只變異資料檔(見檔頭「只複製守衛會讀到的資料檔」),因此
# 「co-edit 守衛 + 資料讓兩邊自洽」可以全綠通過。fresh review F-2。
seed_guard() {
  local name="${1:?seed_guard: name is empty}"; shift
  local dst; dst=$(seed "$name")
  local guard
  for guard in "$@"; do
    cp "$ROOT/scripts/$guard" "$dst/scripts/$guard"
    chmod +x "$dst/scripts/$guard"
  done
  echo "$dst"
}

# expect_local <pass|fail> <guard-script> <root> <label>
# 與 expect() 的差別:跑的是 **$root/scripts/ 底下那份複本**,不是正式 repo 的守衛。
expect_local() {
  local want="${1:?}" guard="${2:?}" target="${3:?}" label="${4:?}"
  [[ "$target" == "$WORK/"* ]] || { echo "expect_local: root 逃逸 $target" >&2; exit 1; }
  [[ -x "$target/scripts/$guard" ]] || { echo "expect_local: 找不到守衛複本 $target/scripts/$guard" >&2; exit 1; }
  count_case "$want"
  local out rc got
  out=$("$target/scripts/$guard" "$target" 2>&1)
  rc=$?
  got=pass; [ "$rc" -ne 0 ] && got=fail
  if [ "$got" = "$want" ]; then
    RESULTS+=("  ✅ $label — 預期 $want,實得 $got")
    PASS=$((PASS + 1))
  else
    RESULTS+=("  ❌ $label — 預期 $want,實得 $got (exit $rc)")
    RESULTS+=("       $(printf '%s' "$out" | tail -3 | tr '\n' ' ')")
    FAIL=$((FAIL + 1))
  fi
}

# mutate <root> <<'PY' … python 片段,sys.argv[1] = root
mutate() { python3 - "$1"; }

echo "=== 架構守衛負向回歸測試 ==="
echo "ROOT(唯讀)= $ROOT"
echo "WORK(暫存)= $WORK"
echo

# ───────────────────────────── Design Contract ─────────────────────────────
D=$(seed dc0); expect pass check-design-contract.sh "$D" "DC-0 對照組(未變異)"

D=$(seed dc1); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Risk: high", "- Risk: normal", t, count=1, flags=re.M)
assert n != t, "DC-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-1 example Risk high→normal(單一編輯,舊版會靜默略過整組)"

D=$(seed dc2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
t = p.read_text(encoding="utf-8")
n = t.replace("- Applicability: applicable",
              "- Applicability: n-a — 本次僅調整前端文案,不跨模組、不動 API 與 schema", 1)
assert n != t, "DC-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-2 example applicable→n-a(附合理理由)"

D=$(seed dc3); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
hit = False
for i, line in enumerate(lines):
    if line.startswith("| Boundary / Module |") and "Data owner" in line:
        lines[i] = line.replace(" Data owner |", " ")
        hit = True
        break
assert hit, "DC-3 mutation 沒生效:找不到 Architecture Boundaries 表頭"
p.write_text("".join(lines), encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-3 example 刪 Data owner 欄"

D=$(seed dc4); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/4-spec.md"
t = p.read_text(encoding="utf-8")
n = t.replace("不得直接觸 DB;不得自行推導權限結論以外的狀態(權限正本在 API 層)", "無", 1)
n = re.sub(r"- Known design limit:\n(  ①.*?\n)+.*?本期不新增樂觀鎖、idempotency key、重試 UI、新 API 或新 schema。\n",
           "- Known design limit:併發情況可能有問題,後續評估。\n", n, count=1, flags=re.S)
assert n != t, "DC-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-4 example 填成 canon 明列的壞例(Forbidden「無」+ 模糊詞)"

D=$(seed dc5); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "_templates/4-spec.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Applicability: applicable \| n-a — <理由>\n", "", t, count=1, flags=re.M)
assert n != t, "DC-5 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-5 刪 Template 的 Applicability 欄"

D=$(seed dc6); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "_templates/7-review.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Dependency Direction", "XXX").replace("Data Ownership", "XXX")
n = n.replace("Interface Stability", "XXX").replace("Design Boundary Contract", "XXX")
assert n != t, "DC-6 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-6 刪 Stage 7 承接規則"

# DC-7/8/9(2026-08 final verdict M-3):Stage 6 的 Design boundary finding 內容檢查。
# 舊版只比「行數 == Test Integrity finding 行數」,填 n-a、只填①、留空都過。
D=$(seed dc7); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Design boundary finding:.*$", "- Design boundary finding:n-a", t, flags=re.M)
assert n != t, "DC-7 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-7 example 七筆 Design boundary finding 全改 n-a"

D=$(seed dc8); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Design boundary finding:.*$", "- Design boundary finding:①無。",
           t, count=1, flags=re.M)
assert n != t, "DC-8 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-8 某一筆只有①、缺②～⑤"

D=$(seed dc9); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^- Design boundary finding:.*$", "- Design boundary finding:",
           t, count=1, flags=re.M)
assert n != t, "DC-9 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-design-contract.sh "$D" "DC-9 某一筆冒號後留空"

# ─────────────────────────────── Gate Token ────────────────────────────────
D=$(seed gt0); expect pass check-gate-tokens.sh "$D" "GT-0 對照組(未變異)"

D=$(seed gt1); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace(" + **Demo verdict**", "", 1)
assert n != t, "GT-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-1 刪 G2 的一個粗體 token(Demo verdict)"

D=$(seed gt2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("**本次 S 全綠**", "本次 S 全綠", 1)
assert n != t, "GT-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-2 G3 的一個 token 被去掉粗體(外部 gate-consistency 抓不到)"

D=$(seed gt3); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = re.sub(r"^  7\. Optional Layer[^\n]*\n", "", t, count=1, flags=re.M)
assert n != t, "GT-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-3 刪 G3 錨定義八點中的一點"

# GT-4(fresh review F-3):憑空多一道 gate。措辭刻意避開會被別的守衛誤觸的字串
# (例如 "Forbidden dependencies" 會撞 check-design-contract 的 readme-canonical 規則),
# 確保紅燈是 check-gate-tokens 抓到的,不是別人順手擋下的。
D=$(seed gt4); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("- G2 錨定義(錨句在上;此處為條件式全文):",
              "- G4 = 設計邊界對不對(4-spec:**設計契約三表全填**,未過不得進入 Stage 5;\n"
              "  核准者不得為該文檔 owner)。\n"
              "- G2 錨定義(錨句在上;此處為條件式全文):", 1)
assert n != t, "GT-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-4 §7 憑空新增第四道 gate 標籤(G4)"

# GT-5(fresh review F-4):八點的**極性**被反轉。編號仍 1–8、原本的寬鬆關鍵詞仍在,
# 舊版守衛對這四種 mutation 全部 exit 0 —— 規則語意反過來而測試不紅。
D=$(seed gt5a); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Gauntlet PASS 不取代 Standards Axis", "Gauntlet PASS 取代 Standards Axis", 1)
assert n != t, "GT-5a mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-5a 第 8 點極性反轉(Gauntlet PASS「不」取代雙軸)"

D=$(seed gt5b); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Required Layer 不得為 unverified", "Required Layer 得為 unverified", 1)
assert n != t, "GT-5b mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-5b 第 5 點極性反轉(Required Layer「不得」為 unverified)"

D=$(seed gt5c); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Optional Layer 可為 unverified,但必須誠實標示",
              "Optional Layer 可為 unverified", 1)
assert n != t, "GT-5c mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-5c 第 7 點刪掉「必須誠實標示」義務"

D=$(seed gt5d); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("Explicitly Excluded Layer 可為 n-a,但必須附理由",
              "Explicitly Excluded Layer 可為 n-a", 1)
assert n != t, "GT-5d mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-5d 第 6 點刪掉「必須附理由」義務"

# GT-6(2026-08 final verdict M-1):逐編號完整比對必須擋住 decoy 與片語搬家。
# 舊版是在整個八點 body 做子字串搜尋,這兩種都繞得過(fresh reviewer 實測重現)。
D=$(seed gt6a); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("  5. Required Layer 不得為 unverified 或 n-a。",
              "  5. Required Layer 得為 unverified 或 n-a(reviewer 自行判斷即可,"
              "不需要 Required Layer 不得為 unverified 的機械檢查)。", 1)
assert n != t, "GT-6a mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-6a 第 5 點反義 + 同句保留原片語當 decoy"

D=$(seed gt6b); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("  5. Required Layer 不得為 unverified 或 n-a。\n"
              "  6. Explicitly Excluded Layer 可為 n-a,但必須附理由。",
              "  5. 由 reviewer 依 Verification Profile 判斷即可。\n"
              "  6. Explicitly Excluded Layer 可為 n-a,但必須附理由;"
              "Required Layer 不得為 unverified 或 n-a。", 1)
assert n != t, "GT-6b mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-gate-tokens.sh "$D" "GT-6b 第 5 點必要句被搬到第 6 點(片語仍在 body 內)"

# ────────────────────────────── Version Sync ───────────────────────────────
D=$(seed vs0); expect pass check-version-sync.sh "$D" "VS-0 對照組(四處一致)"

D=$(seed vs1); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("devflow-evidence-gauntlet.sh`(1.2.0,", "devflow-evidence-gauntlet.sh`(9.9.9,", 1)
assert n != t, "VS-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-version-sync.sh "$D" "VS-1 README 版本改 9.9.9"

D=$(seed vs2); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "devflow-contract.json"
t = p.read_text(encoding="utf-8")
n = t.replace('"gauntlet": "1.2.0"', '"gauntlet": "9.9.9"', 1)
assert n != t, "VS-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-version-sync.sh "$D" "VS-2 devflow-contract.json 版本改 9.9.9"

D=$(seed vs3); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "notes/design/evidence-gauntlet.md"
t = p.read_text(encoding="utf-8")
n = t.replace("**現行 Gauntlet 版本:1.2.0**", "**現行 Gauntlet 版本:9.9.9**", 1)
assert n != t, "VS-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-version-sync.sh "$D" "VS-3 notes/design 版本改 9.9.9"

D=$(seed vs4); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "notes/design/evidence-gauntlet.md"
t = p.read_text(encoding="utf-8")
n = t.replace("**現行 Gauntlet 版本:1.2.0**\n", "", 1)
assert n != t, "VS-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-version-sync.sh "$D" "VS-4 版本錨整行被刪(fail-closed,不得靜默略過)"

# ─────────────────── 守衛本體被改弱(Guard Source;fresh review F-2)───────────────────
# 這一整類原本零覆蓋:上面所有案例都只變異資料檔,守衛本體始終從正式 repo 執行。
# 於是「co-edit 守衛 + 資料,讓兩邊互相自洽」可以端到端全綠。以下每一案都是
# **改守衛自己的原始碼**,並斷言守衛必須因此變紅。

D=$(seed_guard gs0 check-design-contract.sh check-gate-tokens.sh)
expect_local pass check-design-contract.sh "$D" "GS-0a 對照組(守衛複本未變異)"
expect_local pass check-gate-tokens.sh     "$D" "GS-0b 對照組(守衛複本未變異)"

# GS-1:單行把 TRIGGER_KEYWORDS 由 21 條砍成 1 條。
# 修正前:檢查數 127→107,heartbeat 仍報 trigger-parity>0,MIN_CHECKS=100 也還在 → 全綠。
D=$(seed_guard gs1 check-design-contract.sh); mutate "$D" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-design-contract.sh"
t = p.read_text(encoding="utf-8")
n = re.sub(r"TRIGGER_KEYWORDS = \[.*?\n\]\n", 'TRIGGER_KEYWORDS = [\n    "跨模組",\n]\n',
           t, count=1, flags=re.S)
assert n != t, "GS-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-1 守衛的 TRIGGER_KEYWORDS 被砍成 1 條"

# GS-2:兩行 —— 停掉 handoff-example 群組 + 刪它的 REQUIRED_GROUPS 條目。
# 修正前:116/116 全綠(heartbeat 看不到不存在的群組,總數仍 > MIN_CHECKS)。
D=$(seed_guard gs2 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-design-contract.sh"
t = p.read_text(encoding="utf-8")
n = t.replace('    "handoff-example",\n', "", 1)
assert n != t, "GS-2 mutation(刪 REQUIRED_GROUPS 條目)沒生效"
marker = 'CURRENT_GROUP = "handoff-example"'
i = n.index(marker)
j = n.index("if True:", i)
n = n[:j] + "if False:" + n[j + len("if True:"):]
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-2 守衛停掉 handoff-example 群組並同步刪註冊條目"

# GS-3:守衛與資料 co-edit —— 從 DESIGN_COLUMNS 刪掉 Test seam,同時把模板與 example
# 的該欄一起刪掉,讓兩邊互相自洽。canon 交叉核對必須抓到(canon §2.4 仍列該欄)。
D=$(seed_guard gs3 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1])
g = root / "scripts" / "check-design-contract.sh"
t = g.read_text(encoding="utf-8")
n = t.replace('"State / Data flow", "Error handling", "Test seam"]',
              '"State / Data flow", "Error handling"]', 1)
assert n != t, "GS-3 mutation(守衛端)沒生效"
g.write_text(n, encoding="utf-8")
for rel in ("_templates/4-spec.md", "example/contract-expiry-reminder/4-spec.md"):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    s = s.replace(" | Error handling | Test seam |", " | Error handling |")
    p.write_text(s, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-3 守衛與資料 co-edit 刪掉必填欄 Test seam(canon 交叉核對接住)"

# GS-4:把 MIN_CHECKS 由 100 調到 10(讓次級 backstop 形同虛設)。
D=$(seed_guard gs4 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-design-contract.sh"
t = p.read_text(encoding="utf-8")
n = t.replace("MIN_CHECKS = 100", "MIN_CHECKS = 10", 1)
assert n != t, "GS-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-4 守衛的 MIN_CHECKS 被調低"

# GS-5:守衛與資料 co-edit —— 把 Stage 6 的承接 needle「Design Boundary Check」
# 從 handoffs 清單刪掉,同時把模板裡的該檢查也刪掉。needle 數量釘死必須接住。
D=$(seed_guard gs5 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1])
g = root / "scripts" / "check-design-contract.sh"
t = g.read_text(encoding="utf-8")
n = t.replace('("_templates/6-implementation-notes.md", ["Design Boundary Check"],',
              '("_templates/6-implementation-notes.md", [],', 1)
assert n != t, "GS-5 mutation(守衛端)沒生效"
g.write_text(n, encoding="utf-8")
p = root / "_templates" / "6-implementation-notes.md"
p.write_text(p.read_text(encoding="utf-8").replace("Design Boundary Check", "邊界檢查"),
             encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-5 守衛與資料 co-edit 刪掉 Stage 6 承接 needle"

# GS-6:gate-tokens 的守衛與資料 co-edit —— 從 EXPECTED["G3"] 刪一個 token,
# 同時把 README §7 的該 token 也去掉粗體。兩邊自洽,靠長度釘死才抓得到。
D=$(seed_guard gs6 check-gate-tokens.sh); mutate "$D" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1])
g = root / "scripts" / "check-gate-tokens.sh"
t = g.read_text(encoding="utf-8")
n = t.replace('        "+ 現象證據逐 S 相符",\n', "", 1)
assert n != t, "GS-6 mutation(守衛端)沒生效"
g.write_text(n, encoding="utf-8")
p = root / "README.md"
p.write_text(p.read_text(encoding="utf-8").replace(
    "**+ 現象證據逐 S 相符**", "+ 現象證據逐 S 相符", 1), encoding="utf-8")
PY
expect_local fail check-gate-tokens.sh "$D" "GS-6 守衛與 README co-edit 刪掉一個 G3 token"

# GS-7:gate-tokens 的 G3_POINTS 被縮短(八點守衛被改弱),資料不動。
D=$(seed_guard gs7 check-gate-tokens.sh); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-gate-tokens.sh"
t = p.read_text(encoding="utf-8")
n = t.replace('    "8": "Gauntlet PASS 不取代 Standards Axis / Spec Axis / Operational Walkthrough / "\n'
              '         "Coverage Matrix / 真實現象複驗。",\n', "", 1)
assert n != t, "GS-7 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-gate-tokens.sh "$D" "GS-7 守衛的 EXPECTED_G3_POINTS 被縮短(第 8 點守衛消失)"

# GS-8:把一條斷言改成恆真(`check(rows >= 1, …)` → `check(True, …)`)。
# 檢查數不變、群組還在、長度釘死也全過 —— 長度類的釘死本質上防不到這一類。
# 這是 2026-08 驗收實測抓到的殘留,補上 guard-selfpin 的 `check(True` 掃描後才擋得住。
D=$(seed_guard gs8 check-design-contract.sh); mutate "$D" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "scripts" / "check-design-contract.sh"
t = p.read_text(encoding="utf-8")
n = t.replace('        check(rows >= 1, f"{EXAMPLE}「{heading}」表至少一列已填內容", f"資料列數={rows}")',
              '        check(True, f"{EXAMPLE}「{heading}」表至少一列已填內容", f"資料列數={rows}")', 1)
assert n != t, "GS-8 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-design-contract.sh "$D" "GS-8 守衛的一條斷言被改成恆真(check(True))"

# ── S67 群組:Stage 6/7 執行期強制條款(check-stage67-enforcement.sh)──────────
#
# 起因是 2026-08 order-intake 的真實執行:四條散文規則同時失效而所有產出看起來完整。
# 這一組把「條款有沒有被刪掉」變成會紅的測試 —— 條款寫在模板裡沒人守,
# 只有這裡的負向案能證明「守衛真的擋得住」。

D=$(seed s67-control)
expect pass check-stage67-enforcement.sh "$D" "S67-0 對照組(模板與範例未變異)"

D=$(seed s67-a1)
mutate "$D" <<'PY'
import pathlib, sys, re
p = pathlib.Path(sys.argv[1]) / "_templates/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = t.replace("守衛武裝自檢", "起手提醒")
assert n != t, "S67-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-1 Stage 6 步 0 的「守衛武裝自檢」被改名(條款名消失)"

D=$(seed s67-a3-template)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/5-tasks.md"
t = p.read_text(encoding="utf-8")
n = t.replace("=== RUN", "測試輸出")
assert n != t, "S67-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-2 5-tasks 模板的「數 === RUN」骨架被抽掉"

D=$(seed s67-a3-example)
mutate "$D" <<'PY'
import pathlib, sys, re
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/5-tasks.md"
t = p.read_text(encoding="utf-8")
# 把範例的 Verify 退回「只有 -run、沒有案例數斷言」的舊形狀
n = re.sub(r"- Verify: `n=\$\(go test ([^)]*?) -run (\w+) -v 2>&1 \| grep -c '\^=== RUN'\); test \"\$n\" -ge \d+`",
           r"- Verify: `go test \1 -run \2`", t)
assert n != t, "S67-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-3 範例的 Verify 退回沒有案例數斷言的形狀(-run 假綠)"

D=$(seed s67-a4)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/7-review.md"
t = p.read_text(encoding="utf-8")
n = t.replace("補跑 `dev-setup`", "自己想辦法裝一支")
assert n != t, "S67-4 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-4 gauntlet 缺件的補救不再指向補跑 dev-setup(手動 cp 會繞過版本握手)"

D=$(seed s67-a5)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/4-spec.md"
t = p.read_text(encoding="utf-8")
n = t.replace("觀測方式必須在本 repo 可執行", "觀測方式盡量具體")
assert n != t, "S67-5 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-5 4-spec 觀測欄的「必須在本 repo 可執行」被弱化成建議"

# S67-6/7/8(2026-08-15 追加,findings A-3 = VF、findings A-12 = DOC):
# 三案的 needle 都刻意挑**新條款獨有**的字面,不重疊 A1/A3/A4/A5 既有 needle,
# 才能證明是新檢查抓到的,不是誤觸舊檢查(同檔頭「VF 不要跟內部代號 A3 搞混」)。

D=$(seed s67-vf-template)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/5-tasks.md"
t = p.read_text(encoding="utf-8")
n = t.replace("可原樣貼進 shell 的純指令", "盡量簡潔的指令")
assert n != t, "S67-6 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-6 5-tasks 模板的「Verify 必須單行純指令」硬紀律被弱化"

D=$(seed s67-vf-example)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "example/contract-expiry-reminder/5-tasks.md"
t = p.read_text(encoding="utf-8")
# 保留 grep -c / === RUN(不觸發舊 A3 例子檢查),只在同一行尾端混進中文說明——
# 這正是 findings A-3 的原始成因(指令 + 說明混寫成單行)。
old = ("- Verify: `n=$(go test ./internal/... -run TestExpiring -v 2>&1 "
       "| grep -c '^=== RUN'); test \"$n\" -ge 1`")
new = old + ";需先啟動測試用資料庫"
n = t.replace(old, new, 1)
assert n != t, "S67-7 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-7 範例 T-1 的 Verify 值尾端混進中文說明(指令+說明同一行)"

D=$(seed s67-doc)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "_templates/6-implementation-notes.md"
t = p.read_text(encoding="utf-8")
n = t.replace("devflow-doctor.sh", "devflow-check.sh")
assert n != t, "S67-8 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-stage67-enforcement.sh "$D" "S67-8 6-notes 步 0 的 doctor 必跑要求被抽掉(devflow-doctor.sh 消失)"

D=$(seed_guard s67-guard check-stage67-enforcement.sh)
mutate "$D" <<'PY'
import pathlib, sys, re
p = pathlib.Path(sys.argv[1]) / "scripts/check-stage67-enforcement.sh"
t = p.read_text(encoding="utf-8")
# 把 A1 整組 need() 拿掉(但不動 MIN_CHECKS)—— 應由檢查數地板接住
n = re.sub(r'for rel in \("_templates/6-implementation-notes\.md".*?f"A1:\{rel\} 沒給可執行的自檢指令 `devflow-exec\.sh status`"\)\n',
           'for rel in ():\n    pass\n', t, flags=re.S)
assert n != t, "S67-9 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect_local fail check-stage67-enforcement.sh "$D" "S67-9 守衛自己的 A1 整組被刪(檢查數地板接住)"

# ── MM 群組:README master-only 標記平衡(check-readme-markers.sh;MED-4)──────
#
# 起因:skills/dev-setup/SKILL.md 的 install/upgrade/check 全靠 sed 抽
# `<!-- devflow:master-only:start/end -->` 之間的區塊。這對標記若不對稱(數量不等、
# 或巢狀/交錯),sed range 會靜默抽到檔尾或抽出錯誤內容,沒有任何報錯。

D=$(seed mm-control)
expect pass check-readme-markers.sh "$D" "MM-0 對照組(README 標記未變異)"

D=$(seed mm-missing-end)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("<!-- devflow:master-only:end -->\n", "", 1)
assert n != t, "MM-1 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-readme-markers.sh "$D" "MM-1 刪掉一個 end marker(start/end 數量不對稱,sed 會跑到檔尾)"

D=$(seed mm-nested-start)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("<!-- devflow:master-only:start -->\n",
              "<!-- devflow:master-only:start -->\n<!-- devflow:master-only:start -->\n", 1)
assert n != t, "MM-2 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-readme-markers.sh "$D" "MM-2 巢狀 start(兩個 start 中間沒有 end 先閉合)"

D=$(seed mm-both-removed)
mutate "$D" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "README.md"
t = p.read_text(encoding="utf-8")
n = t.replace("<!-- devflow:master-only:start -->\n", "").replace(
    "<!-- devflow:master-only:end -->\n", "")
assert n != t, "MM-3 mutation 沒生效"
p.write_text(n, encoding="utf-8")
PY
expect fail check-readme-markers.sh "$D" "MM-3 start/end 整組被刪(0 對『平衡』但 sed 剝除變無操作)"

# ─────────────────────────────────── 結果 ───────────────────────────────────
printf '%s\n' "${RESULTS[@]}"
echo

FP_AFTER=$(fingerprint)
if [ "$FP_BEFORE" != "$FP_AFTER" ]; then
  echo "⛔ 正式 repo 指紋改變了 —— 測試污染了 working tree,這本身就是失敗" >&2
  exit 1
fi
echo "  ✓ 正式 repo 指紋未變($FP_BEFORE)—— working tree 零污染"
echo

if [ "$FAIL" -ne 0 ]; then
  echo "⛔ 架構守衛負向回歸測試:$FAIL 失敗 / $((PASS + FAIL)) 案"
  exit 1
fi
# ── 精確案例數地板(M-2)──────────────────────────────────────────────────────
# CONTROL_RUN / NEGATIVE_RUN 由 expect()/expect_local() 依 want 實際累計,不是硬編字串。
# 任何案例被刪(不論對照組或負向案)都會讓下面四條斷言其中之一對不上 → 非零退出。
TOTAL_RUN=$((CONTROL_RUN + NEGATIVE_RUN))
COUNT_ERR=0
if [ "$CONTROL_RUN" -ne "$EXPECTED_CONTROLS" ]; then
  echo "⛔ 對照組數不符:實際跑了 $CONTROL_RUN 個,釘死值 $EXPECTED_CONTROLS"
  COUNT_ERR=1
fi
if [ "$NEGATIVE_RUN" -ne "$EXPECTED_NEGATIVES" ]; then
  echo "⛔ 負向案數不符:實際跑了 $NEGATIVE_RUN 個,釘死值 $EXPECTED_NEGATIVES"
  COUNT_ERR=1
fi
if [ "$TOTAL_RUN" -ne "$EXPECTED_TOTAL" ]; then
  echo "⛔ 總案例數不符:實際跑了 $TOTAL_RUN 個,釘死值 $EXPECTED_TOTAL"
  COUNT_ERR=1
fi
if [ "$((PASS + FAIL))" -ne "$TOTAL_RUN" ]; then
  echo "⛔ PASS+FAIL($((PASS + FAIL)))≠ 實際案例數($TOTAL_RUN)—— 計數本身壞了"
  COUNT_ERR=1
fi
if [ "$COUNT_ERR" -ne 0 ]; then
  echo
  echo "   要**刻意**增減案例:同步改本檔頂部的 EXPECTED_CONTROLS / EXPECTED_NEGATIVES /"
  echo "   EXPECTED_TOTAL。這三個數字是真的會被比對的斷言,不是顯示用的裝飾。"
  exit 1
fi

echo "✅ 架構守衛負向回歸測試:$PASS/$PASS 全過"
# ⚠️ 變數必須帶大括號:全形「、」緊接 $VAR 時 bash 會把多位元組字元吃進變數名,
#    配上 set -u 就是 unbound variable(同檔 devflow-check.sh 已記過同型教訓)。
echo "   案例數核對通過:對照組 ${CONTROL_RUN}/${EXPECTED_CONTROLS}、負向 ${NEGATIVE_RUN}/${EXPECTED_NEGATIVES}、合計 ${TOTAL_RUN}/${EXPECTED_TOTAL}"
exit 0
