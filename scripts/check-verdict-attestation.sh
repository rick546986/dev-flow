#!/bin/bash
# check-verdict-attestation.sh — 「誰寫了 verdict」的機械檢查(契約 §7「G2 provenance」;ADR 0004)。
#
# 正本:notes/design/gate-verdict-write.md 鎖死 6 —— verdict 必附 verdict_source + attested_by;
# Jev／自動化不得寫 verdict、不得填 attested_by。判定沿用 scripts/devflow_jev/{attestation,g2auto}.py,
# 與 scripts/devflow_gate.py write-g2-auto 寫入前跑的是**同一支**(手改頂欄繞過寫入器也會在這裡紅)。
#
# 掃 docs/dev/*/{2-decision,4-spec,7-review}.md 與 example/*/ 同名檔。對每一份有 Human 三值 verdict 的檔:
#   紅(任何模式):verdict_source 不在允許集合;attested_by 指向 jev*;human_attested 卻 attested_by 是 agent;
#                 fresh_agent_reviewer 卻 attested_by 是 human;
#                 G1(2-decision)／G3(7-review)是 agent 寫的(只收人寫的 verdict)或帶 g2_mode;
#                 4-spec 是 agent 寫的(fresh_agent_reviewer 或 g2_mode: auto),卻不符合 G2 自動放行 ——
#                 用現在的 spec／2-decision／Stage 3 + 頂欄 g2r_jev 快照重算轉人條件,任一命中、
#                 author == approver、缺 authored_by／routed_by／g2r_case、機械檢查沒過 → 紅。
#   unverified(缺出處欄,P3-2 前的檔):預設只列不紅(legacy 不回頭打紅已出貨 feature);--strict 才紅。
# 負向 fixtures:scripts/fixtures/verdict-attestation/(每支必須落在預期分類)+ 兩個臨時 repo 的 G2 auto 案例。
#
# 用法:scripts/check-verdict-attestation.sh [--strict] [root]
# exit:0 = 全過 / 1 = 任一紅 / 2 = 治具故障
set -uo pipefail
SELF=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF/.." && pwd)
STRICT=0
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    -h|--help) sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) ROOT=$(cd "$arg" && pwd) || exit 2 ;;
  esac
done
[ -f "$SELF/devflow_jev/g2auto.py" ] || { echo "FATAL: 找不到 scripts/devflow_jev/g2auto.py" >&2; exit 2; }

PYTHONDONTWRITEBYTECODE=1 DEVFLOW_PLUGIN="${DEVFLOW_PLUGIN:-$(cd "$SELF/.." && pwd)}" \
  python3 - "$ROOT" "$STRICT" "$SELF" <<'PY'
import glob, os, re, shutil, sys, tempfile
root, strict, scripts = sys.argv[1], sys.argv[2] == "1", sys.argv[3]
sys.path.insert(0, scripts)
from devflow_jev import attestation, g2auto, policy

MIN_CHECKS = 15
checks, failures = 0, []


def check(ok, label, detail=""):
    global checks
    checks += 1
    print(("  ✓ " if ok else "  ✗ ") + label + ((" — " + detail) if (detail and not ok) else ""))
    if not ok:
        failures.append(label)


def read_fm(path):
    with open(path, encoding="utf-8") as fh:
        return attestation.parse_frontmatter(fh.read())


def classify_file(path, stage=None, repo_root=None, slug=None):
    """回 (kind, problems)。kind ∈ no_verdict|legacy_unverified|human|auto|bad。"""
    fm = read_fm(path)
    stage = stage or (fm.get("stage") or "").strip()
    kind, problems = g2auto.classify_gate_doc(stage, fm)
    if kind == "none":
        return "no_verdict", []
    if kind == "legacy":
        return "legacy_unverified", []
    if kind == "auto":
        if repo_root is None:
            return "bad", ["4-spec 是 agent 寫的 verdict,但這裡沒有可重算的 docs/dev/<slug>/(G2 auto 只准在專案 docs/dev/)"]
        problems = g2auto.auto_release_problems(repo_root, slug, fm)
        return ("auto" if not problems else "bad"), problems
    return kind, problems


print("-- 負向 fixtures --")
fixdir = os.path.join(scripts, "fixtures", "verdict-attestation")
expect = {"good-human.md": "human", "good-g2-human.md": "human", "legacy-unverified.md": "legacy_unverified",
          "bad-jev-wrote-verdict.md": "bad", "bad-source-kind-mismatch.md": "bad", "bad-unknown-source.md": "bad",
          "bad-g2-agent-without-auto-path.md": "bad", "bad-g1-agent-verdict.md": "bad",
          "bad-g3-agent-verdict.md": "bad", "bad-g3-g2-mode.md": "bad"}
present = sorted(n for n in os.listdir(fixdir) if n.endswith(".md"))
check(present == sorted(expect), "fixture 清單與預期一致", "實得 %s" % present)
for name, want in expect.items():
    path = os.path.join(fixdir, name)
    got = classify_file(path)[0] if os.path.isfile(path) else "missing"
    check(got == want, "fixture %s → %s" % (name, want), "實得 %s" % got)

print("-- G2 auto 臨時 repo(頂欄是 agent 寫的:乾淨 → 過;命中轉人條件 → 紅)--")
example = os.path.join(root, "example", "contract-expiry-reminder", "4-spec.md")
if not os.path.isfile(example):
    example = os.path.join(os.path.dirname(scripts), "example", "contract-expiry-reminder", "4-spec.md")


def forged_repo(paths):
    tmp = tempfile.mkdtemp(prefix="attest-g2-")
    d = os.path.join(tmp, "docs", "dev", "demo")
    os.makedirs(d)
    with open(example, encoding="utf-8") as fh:
        text = fh.read()
    text = text.replace("## Diff Budget\n", "## Diff Budget\n- Paths: %s\n" % paths, 1)
    jev = g2auto.parse_jev_snapshot("AUTO_PASS p=0.9 risk=1")
    spec = os.path.join(d, "4-spec.md")
    head = ("verdict: PASS\nverdict_source: fresh_agent_reviewer\nattested_by: agent:reviewer-9\n"
            "authored_by: agent:author-1\ng2_mode: auto\nrouted_by: jev:g2r-20260927T000000Z-deadbeef\n"
            "g2r_case: @CASE@\ng2r_jev: AUTO_PASS p=0.9 risk=1\nmechanical: sha256:%s\n" % ("0" * 64))
    text = text.replace("status: approved\n", "status: approved\n" + head, 1)
    with open(spec, "w", encoding="utf-8") as fh:
        fh.write(text)
    case_hash = policy.g2r_case_hash(g2auto.build_case(tmp, "demo", jev=jev))   # case 含 authored_by_present
    with open(spec, "w", encoding="utf-8") as fh:
        fh.write(text.replace("@CASE@", case_hash, 1))
    return tmp, spec


if os.path.isfile(example):
    for paths, want, label in (("src/contracts/handler.go, tests/contracts/", "auto", "未命中轉人條件 → 過"),
                               ("auth/login.go, src/app.go", "bad", "命中 risk_paths 卻只有 agent verdict → 紅")):
        tmp, spec = forged_repo(paths)
        try:
            got, problems = classify_file(spec, "4-spec", tmp, "demo")
            check(got == want, "G2 auto:%s" % label, "實得 %s %s" % (got, problems[:2]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
else:
    check(False, "G2 auto 臨時 repo 治具", "找不到 example/contract-expiry-reminder/4-spec.md")

print("-- 真實文件(docs/dev/*、example/*)--")
files = []
for base in ("docs/dev", "example"):
    for stage in ("2-decision", "4-spec", "7-review"):
        for path in glob.glob(os.path.join(root, base, "*", stage + ".md")):
            files.append((base, stage, path))
files.sort()
counts, bad_files, legacy_files = {}, [], []
for base, stage, path in files:
    slug = os.path.basename(os.path.dirname(path))
    kind, problems = classify_file(path, stage, root if base == "docs/dev" else None, slug)
    counts[kind] = counts.get(kind, 0) + 1
    rel = os.path.relpath(path, root)
    if kind == "bad":
        bad_files.append("%s(%s)" % (rel, ";".join(problems)[:200]))
    elif kind == "legacy_unverified":
        legacy_files.append(rel)
check(len(files) > 0, "掃到 %d 份 gate 文件" % len(files), "0 份 = 檢查沒真的跑")
check(not bad_files, "沒有未授權／不一致的 verdict 出處(Jev、agent 冒 human、G1/G3 agent verdict、G2 agent verdict 命中轉人條件)",
      "; ".join(bad_files[:8]))
if strict:
    check(not legacy_files, "--strict:沒有缺 verdict_source/attested_by 的 verdict", "; ".join(legacy_files[:8]))
else:
    print("  • legacy unverified(P3-2 前的檔,不回頭打紅;--strict 才紅):%d 份" % len(legacy_files))
print("  分類:%s" % counts)

if checks < MIN_CHECKS:
    failures.append("檢查數地板:實跑 %d < %d" % (checks, MIN_CHECKS))
print()
if failures:
    print("⛔ verdict 出處守衛:%d/%d 失敗" % (len(failures), checks))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("✅ verdict 出處守衛:全過(%d 項)" % checks)
PY
