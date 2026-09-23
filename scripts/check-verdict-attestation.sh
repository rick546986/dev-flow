#!/bin/bash
# check-verdict-attestation.sh — 「誰寫了 verdict」的機械檢查(P3-2,jev-gate W6)。
#
# 正本:notes/design/gate-verdict-write.md 鎖死 6 —— verdict 必附 verdict_source + attested_by;
# Jev／自動化不得寫 verdict、不得填 attested_by。分類器沿用 scripts/devflow_jev/attestation.py(G7)。
#
# 掃 docs/dev/*/{2-decision,4-spec,7-review}.md 與 example/*/ 同名檔。對每一份有 Human 三值 verdict 的檔:
#   紅(任何模式):verdict_source 不在允許集合;attested_by 指向 jev*;human_attested 卻 attested_by 是 agent;
#                 fresh_agent_reviewer 卻 attested_by 是 human。
#   unverified(缺兩欄,P3-2 前的檔):預設只列不紅(legacy 不回頭打紅已出貨 feature);--strict 才紅。
# 負向 fixtures:scripts/fixtures/verdict-attestation/(good ×2、legacy ×1、bad ×3),每支必須落在預期分類。
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
    -h|--help) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) ROOT=$(cd "$arg" && pwd) || exit 2 ;;
  esac
done
[ -f "$ROOT/scripts/devflow_jev/attestation.py" ] || { echo "FATAL: 找不到 scripts/devflow_jev/attestation.py" >&2; exit 2; }

PYTHONDONTWRITEBYTECODE=1 python3 - "$ROOT" "$STRICT" <<'PY'
import glob, os, sys
root, strict = sys.argv[1], sys.argv[2] == "1"
sys.path.insert(0, os.path.join(root, "scripts"))
from devflow_jev import attestation

MIN_CHECKS = 8
checks, failures = 0, []


def check(ok, label, detail=""):
    global checks
    checks += 1
    print(("  ✓ " if ok else "  ✗ ") + label + ((" — " + detail) if (detail and not ok) else ""))
    if not ok:
        failures.append(label)


def classify_file(path):
    with open(path, encoding="utf-8") as fh:
        fm = attestation.parse_frontmatter(fh.read())
    cls = attestation.classify(fm)
    verdict = cls["verdict"]
    if cls["label"] == "none":
        return "no_verdict", cls
    src, by = (fm.get("verdict_source") or "").strip(), (fm.get("attested_by") or "").strip()
    if not src and not by:
        return "legacy_unverified", cls
    if src not in attestation.SOURCES:
        return "bad_unknown_source", cls
    if by.lower().startswith(("agent:jev", "jev")):
        return "bad_jev_attested", cls
    if cls["label"] == "unverified":
        return "bad_source_kind_mismatch", cls
    return "attested:" + cls["label"], cls


print("-- 負向 fixtures --")
expect = {"good-human.md": "attested:human_attested", "good-fresh-agent.md": "attested:fresh_agent_reviewer",
          "legacy-unverified.md": "legacy_unverified", "bad-jev-wrote-verdict.md": "bad_jev_attested",
          "bad-source-kind-mismatch.md": "bad_source_kind_mismatch", "bad-unknown-source.md": "bad_unknown_source"}
for name, want in expect.items():
    path = os.path.join(root, "scripts", "fixtures", "verdict-attestation", name)
    got = classify_file(path)[0] if os.path.isfile(path) else "missing"
    check(got == want, "fixture %s → %s" % (name, want), "實得 %s" % got)

print("-- 真實文件(docs/dev/*、example/*)--")
patterns = [os.path.join(root, "docs", "dev", "*", n + ".md") for n in ("2-decision", "4-spec", "7-review")]
patterns += [os.path.join(root, "example", "*", n + ".md") for n in ("2-decision", "4-spec", "7-review")]
files = sorted(set(p for pat in patterns for p in glob.glob(pat)))
counts = {}
bad_files, legacy_files = [], []
for path in files:
    kind, cls = classify_file(path)
    counts[kind] = counts.get(kind, 0) + 1
    rel = os.path.relpath(path, root)
    if kind.startswith("bad_"):
        bad_files.append("%s(%s)" % (rel, kind))
    elif kind == "legacy_unverified":
        legacy_files.append(rel)
check(len(files) > 0, "掃到 %d 份 gate 文件" % len(files), "0 份 = 檢查沒真的跑")
check(not bad_files, "沒有未授權／不一致的 verdict 出處(Jev／agent 冒 human／未知 source)", "; ".join(bad_files[:8]))
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
