#!/bin/bash
# devflow-evidence-gauntlet — 文檔方法論層的 Gauntlet 入口(可重跑、可進 CI)。
#
# 驗證一份含「## Verification Evidence」節的 markdown(通常是 7-review.md)
# 是否遵守 Evidence 契約(正本:notes/design/evidence-gauntlet.md):
#   E1  header 四欄非空(Source SHA / Final Fresh Run ID / Entry point / Toolchain)+ 層表存在
#   E2  Source SHA 綁定:--source-sha 給定時,宣告值必須與其相符(prefix 相容)
#       → 不符 = evidence 產生後又改過碼 = stale,Final Fresh Run 必須晚於最後修改
#   E3  Status 只能四值:pass | fail | unverified | n-a
#   E4  pass 列必有非空 Command + 非空 Result,且 Result 含數字(數字非形容詞)
#   E5  unverified / n-a 列必有 Skipped reason
#   E6  任一層 fail → 整體非零退出(Gauntlet 失敗不得宣告 PASS)
#   E7  Required 層必須 pass:預設讀 sibling(或 --profile)4-spec Verification
#       Profile;--require-layer 只能加嚴,不能把 Required 拿掉。已列入 Evidence
#       且非 n-a 的 Conditional 層同樣必須 pass。漏帶旗標不再 fail-open。
#       --review-file 找不到 Profile(無 sibling、無 --profile、或檔內無該節)
#       → E7 fail-closed,不得退回 1.2.0。
#   E8  coverage 層 pass → Result 必含 covered/total 分數(禁全域 % 虛榮數字)
#   E9  mutation 層:Result 含 ERROR 不得 pass;killed<total 且未標 equivalent 不得 pass
#   E10 Negative Constraint Mapping 節必在、狀態合法、skipped 列不得 pass
#   E11 --review-file 模式:Standards Axis / Spec Axis / 現象證據 /
#       Operational Walkthrough / Coverage Matrix 五節必在(只驗 heading 存在,
#       內容正確性仍屬 Reviewer)—— Gauntlet PASS 不得取代 Stage 7 雙軸審、
#       現象複驗與 Walkthrough(README §7 G3 第 8 點的五項全量)
#   E12 --report <path>:先刪舊 report(stale artifact 清除),再寫入本次
#       run-id / tool-version / SHA / 逐項結果
#   E13 表列 fail-closed:欄數 ≠ 預期的表列是明確 error,不得靜默丟列
#       (否則 fail 列多打一個 `|` 就整列被吞、E6 不觸發)
#
# 用法:
#   bash scripts/devflow-evidence-gauntlet.sh <file.md> \
#     [--source-sha <sha>] [--require-layer <名>]... [--profile <4-spec.md>]
#     [--review-file] [--report <path>]
# exit 0 = 契約全過;exit 1 = 有違規(逐條列出);exit 2 = 用法/檔案錯誤。
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
# 版本聲明:與 devflow-contract.json 的 schema_versions.gauntlet 同步(doctor 比對用)
GAUNTLET_VERSION="1.3.1"
export DEVFLOW_EG_VERSION="$GAUNTLET_VERSION"

usage_error() {
  echo "usage error: $1" >&2
  echo "usage: devflow-evidence-gauntlet.sh <file.md> [--source-sha <sha>] [--require-layer <名>]... [--profile <4-spec.md>] [--review-file] [--report <path>]" >&2
  exit 2
}

TARGET="" SOURCE_SHA="" REVIEW_FILE="0" REPORT="" PROFILE=""
REQUIRE_LAYERS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --version) echo "devflow-evidence-gauntlet $GAUNTLET_VERSION"; exit 0 ;;
    # B-4:診斷旗標,行為零變化 —— 只印出本副本自己解析到的 ROOT
    # (母版在 scripts/ 下,ROOT=repo 根;散發到 docs/dev/tools/ 後 ROOT 會變成
    # docs/dev/,深度不同)。doctor 靠這個探測散發副本的 ROOT 解析有沒有跑掉,
    # 不改 GAUNTLET_VERSION(版本語意是 E 檢查行為,動它會牽動 README §7 對版守衛)。
    # issue #5:Git Bash 的 pwd 印 POSIX 形式(/d/<專案根>/docs/dev),而 doctor 端
    # 用 Windows 原生 Python 的 os.path.realpath 去解,開頭的 `/` 會被當成「現行
    # 磁碟機根目錄下的路徑」→ D:\d\<專案根>\docs\dev,比期望值**多一層** \d\,
    # 於是 gauntlet-root 恆紅。有 cygpath 就先正規化成 Windows 形式再印,與同目錄
    # history-append.sh(靠 git rev-parse --show-toplevel 取根,本來就印 D:/...)
    # 的既有輸出對齊;非 Windows 環境沒有 cygpath,原樣印出、行為零變化。
    --print-root)
      if command -v cygpath >/dev/null 2>&1; then cygpath -m "$ROOT"; else echo "$ROOT"; fi
      exit 0 ;;
    --source-sha) [ $# -ge 2 ] || usage_error "$1 缺值"; SOURCE_SHA="$2"; shift 2 ;;
    --require-layer) [ $# -ge 2 ] || usage_error "$1 缺值"; REQUIRE_LAYERS+=("$2"); shift 2 ;;
    --profile) [ $# -ge 2 ] || usage_error "$1 缺值"; PROFILE="$2"; shift 2 ;;
    --review-file) REVIEW_FILE="1"; shift ;;
    --report) [ $# -ge 2 ] || usage_error "$1 缺值"; REPORT="$2"; shift 2 ;;
    -*) usage_error "unknown flag: $1" ;;
    *) TARGET="$1"; shift ;;
  esac
done
if [ -z "$TARGET" ] || [ ! -f "$TARGET" ]; then
  echo "usage: devflow-evidence-gauntlet.sh <file.md> [--source-sha <sha>] [--require-layer <名>]... [--profile <4-spec.md>] [--review-file] [--report <path>]" >&2
  exit 2
fi

# --review-file 漏帶 --source-sha → 預設當下 HEAD。宣告 SHA ≠ HEAD = stale,
# 作廢 G3(程式碼 commit 後未重跑 Final Fresh)。
# docs/dev/<feature>/7-review.md(排除 example/ 與 scripts/fixtures/):即使
# 顯式 --source-sha 也強制當下 HEAD —— 出貨樹機械作廢不能靠帶舊 SHA 繞過。
# 其他路徑(fixture / example / 歷史示範)顯式 --source-sha 仍只比對該值。
if [ "$REVIEW_FILE" = "1" ]; then
  target_dir=$(cd "$(dirname "$TARGET")" && pwd)
  if git -C "$target_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    prefix=$(git -C "$target_dir" rev-parse --show-prefix)
    rel="${prefix}$(basename "$TARGET")"
    if [[ "$rel" =~ ^docs/dev/[^/]+/7-review\.md$ ]]; then
      SOURCE_SHA=$(git -C "$target_dir" rev-parse HEAD)
    elif [ -z "$SOURCE_SHA" ]; then
      SOURCE_SHA=$(git -C "$target_dir" rev-parse HEAD)
    fi
  fi
fi

# 4-spec 正本:顯式 --profile 優先,否則 sibling 4-spec.md。
# --review-file 找不到檔就不讀、退回 1.2.0 = 假綠;改為 E7 fail-closed。
PROFILE_MISSING=0
if [ -n "$PROFILE" ]; then
  [ -f "$PROFILE" ] || usage_error "--profile 不是檔案:$PROFILE"
else
  sibling="$(cd "$(dirname "$TARGET")" && pwd)/4-spec.md"
  if [ -f "$sibling" ]; then
    PROFILE="$sibling"
  elif [ "$REVIEW_FILE" = "1" ]; then
    PROFILE_MISSING=1
  fi
fi

# E12 前半:stale artifact 清除 —— 舊 report 先刪,任何層都讀不到上一輪輸出。
if [ -n "$REPORT" ]; then
  rm -f "$REPORT"
fi

export DEVFLOW_EG_TARGET="$TARGET"
export DEVFLOW_EG_SOURCE_SHA="$SOURCE_SHA"
export DEVFLOW_EG_REVIEW_FILE="$REVIEW_FILE"
export DEVFLOW_EG_REPORT="$REPORT"
export DEVFLOW_EG_PROFILE="$PROFILE"
export DEVFLOW_EG_PROFILE_MISSING="$PROFILE_MISSING"
export DEVFLOW_EG_REQUIRE_LAYERS="$(printf '%s\n' "${REQUIRE_LAYERS[@]+"${REQUIRE_LAYERS[@]}"}")"

python3 <<'PY'
import datetime
import os
import platform
import re
import sys

VERSION = os.environ["DEVFLOW_EG_VERSION"]
target = os.environ["DEVFLOW_EG_TARGET"]
expected_sha = os.environ["DEVFLOW_EG_SOURCE_SHA"]
review_mode = os.environ["DEVFLOW_EG_REVIEW_FILE"] == "1"
report_path = os.environ["DEVFLOW_EG_REPORT"]
profile_path = os.environ.get("DEVFLOW_EG_PROFILE", "")
profile_missing = os.environ.get("DEVFLOW_EG_PROFILE_MISSING", "0") == "1"
flag_layers = [l for l in os.environ["DEVFLOW_EG_REQUIRE_LAYERS"].splitlines() if l.strip()]

with open(target, encoding="utf-8") as stream:
    source = stream.read()

STATUSES = {"pass", "fail", "unverified", "n-a"}
checks = 0
violations = []


def check(rule, condition, message):
    global checks
    checks += 1
    if not condition:
        violations.append(f"{rule}: {message}")


def section(heading):
    """回傳指定 ## 節的內文(至下一個 ## 或檔尾);不存在回 None。"""
    match = re.search(
        rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", source, re.M | re.S)
    return match.group(1) if match else None


def table_rows(body, expected_cols, table_label):
    """抽 markdown 表資料列(略過表頭與分隔列),回傳 list[list[str]]。

    fail-closed(E13):欄數 ≠ expected_cols 的表列是明確 error,不得靜默丟列 ——
    否則 fail 列只要 Result 多打一個 `|` 就整列被吞、E6 不觸發(anti-gaming 漏洞)。
    """
    rows = []
    for line in (body or "").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue  # 分隔列
        if len(cells) != expected_cols:
            check("E13", False,
                  f"{table_label} malformed 表列(欄數 {len(cells)} ≠ {expected_cols},"
                  f"不得靜默略過;儲存格內勿用原生 `|`):{stripped}")
            continue
        rows.append(cells)
    return rows[1:] if rows else []  # rows[0] = 表頭


def parse_profile_layers(spec_text):
    """從 4-spec Verification Profile 抽出 Required / Conditional / Excluded 層名。

    層名分隔認頓號、逗號、分號、換行、空白夾著的 /。括號條件與「——」「(=」
    之後的說明丟掉。認不到 Verification Profile 節就當沒有。
    """
    match = re.search(
        r"^##[ \t]+Verification Profile[^\n]*\n(.*?)(?=^## |\Z)",
        spec_text, re.M | re.S)
    if not match:
        return [], [], []
    body = match.group(1)
    key_re = re.compile(
        r"^-\s*(Required layers|Conditional layers|Explicitly excluded layers|"
        r"Explicitly Excluded layers|Explicitly excluded)"
        r"(?:\([^)]*\))?\s*[:：]\s*(.*)$",
        re.I)
    other_field = re.compile(r"^-\s+[\w\u4e00-\u9fff].*[:：]")
    fields = {}
    current = None
    chunks = []
    for line in body.splitlines():
        km = key_re.match(line)
        if km:
            if current is not None:
                fields[current] = "\n".join(chunks)
            current = km.group(1).lower()
            chunks = [km.group(2)]
            continue
        if current is not None and other_field.match(line) and not key_re.match(line):
            fields[current] = "\n".join(chunks)
            current = None
            chunks = []
            continue
        if current is not None:
            chunks.append(line)
    if current is not None:
        fields[current] = "\n".join(chunks)

    def split_layers(raw):
        if not raw:
            return []
        raw = re.split(r"——|\(=", raw, 1)[0]
        out = []
        for part in re.split(r"、|,|；|\n| / ", raw):
            name = part.strip().strip("-").strip()
            name = re.sub(r"\([^)]*\)\s*$", "", name).strip().strip("`")
            if not name or name.lower() == "final fresh run 必跑":
                continue
            out.append(name)
        return out

    def pick(*keys):
        for key in keys:
            if key in fields:
                return split_layers(fields[key])
        return []

    return (
        pick("required layers"),
        pick("conditional layers"),
        pick("explicitly excluded layers", "explicitly excluded"),
    )


spec_required, spec_conditional, spec_excluded = [], [], []
profile_section_missing = False
if profile_path:
    with open(profile_path, encoding="utf-8") as spec_stream:
        spec_text = spec_stream.read()
    if not re.search(r"^##[ \t]+Verification Profile", spec_text, re.M):
        profile_section_missing = True
    else:
        spec_required, spec_conditional, spec_excluded = parse_profile_layers(
            spec_text)
# 旗標只能加嚴:4-spec Required ∪ --require-layer,不能用旗標把 Required 拿掉。
required_layers = []
seen_req = set()
for name in spec_required + flag_layers:
    key = name.lower()
    if key in seen_req:
        continue
    seen_req.add(key)
    required_layers.append(name)
del spec_excluded  # Excluded 仍走 E3/E5(n-a + 理由),不另設必跑義務


# ---- E1 header + 層表 ----
evidence = section("Verification Evidence")
check("E1", evidence is not None, "缺「## Verification Evidence」節")
headers = {}
if evidence is not None:
    for field in ("Source SHA", "Final Fresh Run ID", "Entry point", "Toolchain"):
        match = re.search(rf"^- {re.escape(field)}:\s*(.*)$", evidence, re.M)
        value = match.group(1).strip() if match else ""
        headers[field] = value
        check("E1", bool(value), f"header 欄「{field}」缺漏或為空")

layers = table_rows(evidence, 5, "Verification Evidence") if evidence is not None else []
check("E1", bool(layers), "Layer 表缺漏或無資料列(| Layer | Command | Status | Result | Skipped reason |)")

# ---- E2 source SHA 綁定(Final Fresh Run 晚於最後修改的機械化身)----
# m1 加嚴:比對取宣告值的前導 hex token(容許尾隨註記),且兩端 token 皆須 ≥7 字元
# 才可比對 —— 否則「Source SHA: f」對任何 f 開頭的 SHA 互為前綴即過,綁定失效。
SHA_MIN = 7
declared_sha = headers.get("Source SHA", "")


def sha_token(value):
    match = re.match(r"[0-9a-fA-F]+", value)
    return match.group(0) if match else ""


declared_token = sha_token(declared_sha)
if declared_sha:
    check("E2", len(declared_token) >= SHA_MIN,
          f"宣告 Source SHA「{declared_sha}」的 hex 前綴長度 {len(declared_token)} "
          f"< {SHA_MIN},不足以可靠綁定,拒絕比對")
if expected_sha:
    expected_token = sha_token(expected_sha)
    check("E2", len(expected_token) >= SHA_MIN,
          f"--source-sha「{expected_sha}」的 hex 前綴長度 {len(expected_token)} "
          f"< {SHA_MIN},不足以可靠綁定,拒絕比對")
    if len(declared_token) >= SHA_MIN and len(expected_token) >= SHA_MIN:
        matched = declared_token == expected_token or \
            declared_token.startswith(expected_token) or \
            expected_token.startswith(declared_token)
        check("E2", matched,
              f"stale evidence:宣告 Source SHA「{declared_token}」≠ 當下「{expected_token}」"
              "(evidence 產生後 source 又動過,必須重跑 Final Fresh Run)")

# ---- E3–E9 逐層 ----
fraction = re.compile(r"(\d+)\s*/\s*(\d+)")
for name, command, status, result, reason in layers:
    label = name or "(未命名層)"
    check("E3", status in STATUSES,
          f"「{label}」status「{status}」不在四值 pass|fail|unverified|n-a 內")
    if status == "pass":
        check("E4", bool(command), f"「{label}」pass 但 Command 空(沒跑不能寫 PASS)")
        check("E4", bool(result), f"「{label}」pass 但 Result 空(沒跑不能寫 PASS)")
        if result:
            check("E4", bool(re.search(r"\d", result)),
                  f"「{label}」pass 但 Result 無任何數字(要貼數字,不是形容詞)")
    if status in ("unverified", "n-a"):
        check("E5", bool(reason), f"「{label}」status={status} 但無 Skipped reason")
    if status == "fail":
        check("E6", False,
              f"「{label}」fail —— Gauntlet 有失敗層,不得宣告 Stage 7 PASS")
    lowered = name.lower()
    if "coverage" in lowered and status == "pass":
        check("E8", bool(fraction.search(result)),
              f"「{label}」pass 但 Result 無 covered/total 分數(全域 % 是虛榮數字,"
              "要列 changed lines covered/total)")
    if "mutation" in lowered and status == "pass":
        check("E9", not re.search(r"\berror\b", result, re.I),
              f"「{label}」Result 含 ERROR —— tool error 不算 killed,run 無效")
        m = fraction.search(result)
        if m and int(m.group(1)) < int(m.group(2)):
            check("E9", "equivalent" in result.lower(),
                  f"「{label}」{m.group(0)} 有 survivor 且未標 equivalent+理由,不得 pass")

# ---- E7 required / triggered-conditional(對照 4-spec Verification Profile)----
# Required = 必須 pass。unverified/n-a/缺席都不滿足(fail 另由 E6 擋)。
# 來源:4-spec Required layers ∪ --require-layer(旗標只能加嚴)。
# --review-file 找不到 Profile → fail-closed,不得退回 1.2.0 漏帶即綠。
if review_mode and (profile_missing or profile_section_missing):
    check("E7", False,
          "--review-file 找不到 4-spec Verification Profile"
          "(無 sibling 4-spec.md、無 --profile、或檔內無該節);"
          "不得退回 1.2.0 讓漏帶 --require-layer 仍綠")
for wanted in required_layers:
    passed = any(wanted.lower() in row[0].lower() and row[2] == "pass"
                 for row in layers)
    check("E7", passed,
          f"required layer「{wanted}」缺席或未 pass(unverified/n-a 不滿足 required)")

# Conditional:Evidence 表已列且非 n-a = 已觸發 → 必須 pass。未列入視為未觸發。
for wanted in spec_conditional:
    hits = [row for row in layers if wanted.lower() in row[0].lower()]
    if not hits:
        continue
    status = hits[0][2]
    if status == "n-a":
        continue
    check("E7", status == "pass",
          f"triggered conditional layer「{wanted}」status={status},必須 pass")

# ---- E10 negative constraints ----
negative = section("Negative Constraint Mapping")
check("E10", negative is not None,
      "缺「## Negative Constraint Mapping」節(negative constraint 不得靜默消失)")
if negative is not None:
    negative_rows = table_rows(negative, 3, "Negative Constraint Mapping")
    check("E10", bool(negative_rows), "Negative Constraint Mapping 無資料列")
    for constraint, mapped, status in negative_rows:
        check("E10", status in STATUSES,
              f"constraint「{constraint}」status「{status}」不在四值內")
        if "skipped" in mapped.lower():
            check("E10", status != "pass",
                  f"constraint「{constraint}」標 skipped 卻寫 pass(skipped 只能 unverified/n-a)")

# ---- E11 review-file 模式:Gauntlet 不取代雙軸審 ----
if review_mode:
    # 五節 = README §7 G3 第 8 點列舉的全量;只驗 heading 存在,內容正確性屬 Reviewer。
    for heading in (
        "Standards Axis",
        "Spec Axis",
        "現象證據",
        "Operational Walkthrough",
        "Coverage Matrix",
    ):
        check("E11", re.search(rf"^## {re.escape(heading)}", source, re.M) is not None,
              f"review 檔缺「## {heading}」—— Gauntlet evidence 全 pass 也不得跳過"
              "雙軸審查與現象複驗(G3 信心 = Gauntlet + Code Review + Walkthrough)")

# ---- 輸出與 E12 report ----
verdict = "PASS" if not violations else "FAIL"
lines_out = []
if violations:
    lines_out.append(f"❌ evidence gauntlet: {len(violations)} violation(s) in {checks} checks — {target}")
    lines_out.extend(f"  - {violation}" for violation in violations)
else:
    lines_out.append(f"✅ evidence gauntlet: {checks} checks passed — {target}")
print("\n".join(lines_out))

if report_path:
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-p{os.getpid()}"
    with open(report_path, "w", encoding="utf-8") as stream:
        stream.write("# devflow evidence gauntlet report\n")
        stream.write(f"- run-id: {run_id}\n")
        stream.write(f"- tool-version: {VERSION}\n")
        stream.write(f"- python: {platform.python_version()}\n")
        stream.write(f"- target: {target}\n")
        stream.write(f"- declared-source-sha: {declared_sha or '(missing)'}\n")
        stream.write(f"- expected-source-sha: {expected_sha or '(not provided)'}\n")
        stream.write(f"- verdict: {verdict}\n")
        stream.write(f"- checks: {checks}\n")
        stream.write(f"- violations: {len(violations)}\n")
        for violation in violations:
            stream.write(f"  - {violation}\n")

sys.exit(0 if not violations else 1)
PY
