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
#   Gate Token       GT-0 對照組 / GT-1 刪 G2 一個 token / GT-2 G3 token 去粗體
#                    GT-3 刪 G3 錨定義八點中的一點
#   Version Sync     VS-0 對照組 / VS-1 README 9.9.9 / VS-2 contract 9.9.9
#                    VS-3 design doc 9.9.9 / VS-4 版本錨被刪
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
echo "✅ 架構守衛負向回歸測試:$PASS/$PASS 全過(3 對照組 + $((PASS - 3)) 個負向案例)"
exit 0
