#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F1 牙：RP-1…16 + dual-read 誠實。不鎖 annex 鍵名（OC-3）。"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STAGE_MD = (
    "1-discussion.md", "2-decision.md", "3-prototype.md", "4-spec.md",
    "5-tasks.md", "6-implementation-notes.md", "7-review.md",
)
NEW_FAMILY = ("intake.md", "decide.md", "spec.md", "build.md", "ship.md")
SLOTS = (
    "SLOT-PARSE-OLD7", "SLOT-PARSE-NEW5", "SLOT-MISSING-NEW5-DEFAULT",
    "SLOT-UNDECLARED-ROUTE", "SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS",
    "SLOT-DOCTOR-GREEN-MEANS", "SLOT-IN-FLIGHT-DETECT",
    "SLOT-RP-MIN-SET", "SLOT-SKIP-NEGATION",
)
RPS = tuple("RP-%d" % i for i in range(1, 17))
VAGUE_ALL = ("TBD", "之後再說", "實作再定")
F1_UNION = (
    "scripts/five_station_f1.py", "scripts/check-five-station-f1.sh",
    "scripts/test-five-station-f1.sh", "scripts/fixtures/five-station-simplify/",
    "notes/design/five-station-simplify-f1-dual-read-annex.md",
    "notes/design/five-station-simplify-f1-rp-min-set.md",
)
EVIDENCE8 = (
    "Final Fresh", "Required Layer", "Conditional Layer", "不得存在任何 fail",
    "Required Layer 不得為 unverified", "Explicitly Excluded",
    "Optional Layer", "Gauntlet PASS 不取代",
)
KIND_PREFIX = (
    ("dual-read-annex", "slots"), ("f1-rp-min-set", "rpset"),
    ("rp-min-set", "rpset"), ("skip-negation", "attest"),
    ("rp-16", "verdict"), ("rp-13", "attest"), ("rp-12", "attest"),
    ("rp-14", "attest"), ("rp-01", "tcard"), ("rp-02", "seam"),
    ("rp-06", "seam"), ("rp-03", "spec"), ("rp-04", "tname"),
    ("rp-05", "tcard"), ("brief-", "brief"), ("dual-", "dual"),
    ("slots-", "slots"), ("inflight-", "inflight"), ("rp-07", "quiz"),
    ("rp-08", "ship"), ("s-3-3", "evidence"), ("rp-09", "cap"),
    ("rp-10", "cap"), ("rp-11", "cap"), ("reopen-", "reopen"),
    ("q6-", "q6"),
)
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
T_BLOCK = re.compile(r"^##\s+(T-\S+)\s*(.*?)(?=^##\s|\Z)", re.M | re.S)
HUMAN_ATTEST = re.compile(r"Verdict attestation:\s*human:\S")
ACCEPTED = re.compile(r"Human verdict:\s*ACCEPTED")
PASS_LN = re.compile(r"^verdict:\s*PASS\b", re.M)
VERDICT = re.compile(r"^verdict:\s*(\S+)", re.M)
CHAT = re.compile(r"可以開 Stage 4|准開下一站")
PLEASE = re.compile(r"請 owner 看一下|要不要繼續|請人審")
SKIP_NEG = re.compile(r"(不|無|不得)[^。\n]{0,20}跳過")
DOCTOR_HOP = re.compile(
    r"(doctor (exit 0|綠)|COMPATIBLE).{0,24}(跟 hops|已切|可以跟 hops)"
)
IRREV = re.compile(r"schema|公開 API|權限|金流|資料遺失")
REOPEN = re.compile(r"改採\s*([12467][BC])")
TEST_FN = re.compile(r"\b(def\s+)?(test_[A-Za-z0-9_]+)\b")
SID_NAME = re.compile(r"(?i)s[_-]\d")
OPTIONAL = re.compile(r"四欄可選|可選 seam|已五站故省")


class Result:
    def __init__(self):
        self.items = []
        self.info = {}

    def red(self, code, msg):
        self.items.append((code, True, msg))

    @property
    def is_red(self):
        return any(flag for _, flag, _ in self.items)

    @property
    def red_codes(self):
        return [code for code, flag, _ in self.items if flag]

    def dump(self):
        lines = ["%s %s %s" % ("RED" if flag else "OK", code, msg)
                 for code, flag, msg in self.items]
        lines.extend("INFO %s=%s" % item for item in sorted(self.info.items()))
        return "\n".join(lines)


def parse_fm(text):
    match = FM_RE.match(text)
    if not match:
        return {}, text
    meta = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip()
    return meta, text[match.end():]


def infer_kind(path, meta):
    if meta.get("f1-kind"):
        return meta["f1-kind"]
    name = os.path.basename(path)
    for prefix, kind in KIND_PREFIX:
        if prefix in name:
            return kind
    return "generic"


def listed_files(meta, text):
    raw = meta.get("f1-files", "")
    if raw:
        return [bit.strip() for bit in re.split(r"[, ]+", raw) if bit.strip()]
    return re.findall(r"`([^`]+\.(?:md|html))`", text)


def in_flight(files):
    bases = {os.path.basename(item) for item in files}
    return any(name in bases for name in STAGE_MD)


def parse_tasks(text):
    out = []
    for match in T_BLOCK.finditer(text):
        body = match.group(2)

        def field(key):
            found = re.search(r"^-\s*%s:\s*(.*)$" % key, body, re.M)
            return found.group(1).strip() if found else None

        out.append({
            "name": match.group(1),
            "covers": field("Covers"),
            "files": field("Files"),
            "verify": field("Verify"),
            "blocked": field("Blocked-by"),
            "body": body,
        })
    return out


def split_files(value):
    if value is None:
        return None
    if value.strip() in ("", "—", "-", "n/a"):
        return []
    return [bit.strip() for bit in re.split(r"[,，]", value) if bit.strip()]


def run_c4(path, root):
    script = os.path.join(root, "scripts", "check-spec-gate.sh")
    if not os.path.isfile(script) or not path:
        return None
    proc = subprocess.run(
        ["bash", script, path], capture_output=True, text=True
    )
    blob = proc.stdout + proc.stderr
    if re.search(r"❌\s*C4\b", blob):
        return True
    if re.search(r"✅\s*C4\b", blob):
        return False
    return None


def fm_token(meta, key):
    raw = (meta.get(key) or "").strip()
    return raw.split()[0] if raw else ""


def ship_pass(meta, body):
    """7-review 正本：YAML `verdict:`；正文列只是後備。"""
    if fm_token(meta, "verdict") == "PASS":
        return True
    return bool(PASS_LN.search(body))


def evaluate(text, path="", root=None):
    root = root or str(ROOT)
    meta, body = parse_fm(text)
    kind = infer_kind(path, meta)
    result = Result()
    result.info["kind"] = kind
    writer = meta.get("f1-writer", "")
    if "寫入者是 Agent" in body or "writer: agent" in body:
        writer = writer or "agent"

    if kind == "verdict":
        demo_attest = bool(HUMAN_ATTEST.search(body))
        if ACCEPTED.search(body) and not demo_attest:
            result.red("RP-16", "ACCEPTED 無 human attestation = 未寫")
        # Ship 未寫看頂欄作者，不看 Demo attestation（偽造 human: 不得洗白）
        if ship_pass(meta, body) and writer != "human":
            result.red("RP-16", "Ship PASS 無人類頂欄 = 未寫")
        result.info["unread"] = "RP-16" in result.red_codes

    if kind in ("slots", "annex"):
        missing = [slot for slot in SLOTS if slot not in body]
        if missing:
            result.red("S-5.8", "缺 SLOT: " + ",".join(missing))
        result.info["slots_ok"] = not missing

    if kind in ("rpset", "annex"):
        missing = [rp for rp in RPS if not re.search(r"\b%s\b" % rp, body)]
        if missing:
            result.red("S-2.6", "annex 少 RP: " + ",".join(missing))
        result.info["rp_listed"] = 16 - len(missing)

    if kind == "dual":
        if "缺新 5 欄" in body or "缺新五欄" in body or meta.get("f1-missing-new5") == "yes":
            result.info["missing_new5_legal"] = True
        if DOCTOR_HOP.search(body) or "doctor exit 0 所以可以跟 hops 走" in body:
            result.red("S-5.6", "doctor 綠不得跟 hops")
        if re.search(r"已切五站|COMPATIBLE\s*=\s*五站", body):
            result.red("S-5.5", "doctor 綠 ≠ 已切")
        if ("2.0.0" in body and re.search(r"五站預設|five-station-default", body)):
            result.red("S-5.7", "2.0.0+五站 hops → 仍舊 7")
            result.info["route"] = "old-7"
            result.info["doctor_not_arbiter"] = True

    if kind == "inflight":
        files = listed_files(meta, body)
        flying = in_flight(files)
        result.info["in_flight"] = flying
        want = meta.get("f1-request", "")
        if flying and (
            "five-station" in want or "五站 hop" in body or "五站自動前進" in body
        ):
            result.red("RP-15", "in-flight 不得五站 hop／寫五站狀態")
            result.info["hop_blocked"] = True

    if kind in ("tcard", "brief"):
        tasks = parse_tasks(body)
        declared = split_files(meta.get("f1-union")) if meta.get("f1-union") else None
        for task in tasks:
            cols = (
                ("Covers", task["covers"]), ("Files", task["files"]),
                ("Verify", task["verify"]), ("Blocked-by", task["blocked"]),
            )
            miss = [name for name, val in cols if val is None]
            if miss:
                result.red("RP-1", "%s 缺欄 %s" % (task["name"], miss))
            if task["verify"] and "看起來沒問題" in task["verify"]:
                result.red("RP-1", "%s Verify 無鑑別力" % task["name"])
            files = split_files(task["files"])
            if files == []:
                result.red("RP-5", "%s 缺 Files" % task["name"])
            if declared is not None and files:
                extra = [item for item in files if item not in declared]
                if extra:
                    result.red("RP-5", "%s Files 超出聯集 %s" % (task["name"], extra))
        if "五站已簡化" in body and (
            any(task["verify"] is None for task in tasks) or "可省" in body
        ):
            result.red("S-2.1", "少 Must-keep 違 brief")
        if OPTIONAL.search(body):
            result.red("S-2.7", "可選句擋 G2")

    if kind == "seam":
        if re.search(r"無 RED|RED:\s*(無|—|n/a|缺失)", body):
            result.red("RP-2", "無 RED 輸出")
        impl = re.search(r"implementer:\s*(\S+)", body)
        rev = re.search(r"reviewer:\s*(\S+)", body)
        if impl and rev and impl.group(1) == rev.group(1):
            result.red("RP-2", "reviewer=implementer")
        if re.search(r"完成宣稱|標完成", body) and re.search(r"摘要", body):
            if not re.search(r"檔:\s*\d+", body):
                result.red("RP-6", "只有摘要無原始輸出")

    if kind == "spec":
        if any(word in body for word in VAGUE_ALL):
            result.red("RP-3", "未定事項三詞")
            result.info["c4_fail"] = bool(run_c4(path, root))
        if "系統應處理錯誤" in body and not re.search(r"觀測|assert|exit", body):
            result.red("RP-3", "不可測 S")

    if kind == "tname":
        for match in TEST_FN.finditer(body):
            name = match.group(2)
            if not SID_NAME.search(name):
                result.red("RP-4", "測試名無 S-id: %s" % name)

    if kind == "attest":
        attest = bool(HUMAN_ATTEST.search(body))
        accepted = bool(ACCEPTED.search(body))
        trigger = meta.get("f1-trigger", "")
        if trigger == "miss" or "九條 trigger 全未勾" in body:
            result.info["demo_page"] = False
            if accepted or "強迫 ACCEPTED" in body or "必須有 ACCEPTED" in body:
                result.red("RP-12", "未命中卻強迫 ACCEPTED")
        if CHAT.search(body) and not attest:
            result.red("RP-13", "空 attestation + chat 不得離 Spec")
            result.info["leave_spec"] = False
        if (meta.get("f1-latch") == "no" or "latch=否" in body) and PLEASE.search(body):
            result.red("RP-14", "latch=否卻請人審")
        if SKIP_NEG.search(body):
            result.info["skip_oc"] = False
            if re.search(r"trigger_source\s*=\s*owner-call|當 skip OC|skip-oc:\s*yes", body):
                result.red("S-4.5", "否定跳過不得當 skip OC")
        if accepted and attest:
            result.info["hop_spec_build"] = True

    if kind == "quiz":
        if ("無 Quiz" in body or meta.get("f1-quiz") == "no") and (
            "不可逆" in body or IRREV.search(body)
        ):
            result.red("RP-7", "不可逆無 Quiz")
        if "可逆" in body and re.search(r"強制 Quiz|Quiz 當第三", body):
            result.red("S-1.10", "可逆強制 Quiz 當第三例行停")

    if kind == "ship":
        verdict = VERDICT.search(body)
        value = verdict.group(1) if verdict else ""
        if re.search(r"標 Done|狀態:\s*Done|slug-status:\s*Done", body):
            if value != "PASS":
                result.red("RP-8", "無人 PASS 卻 Done")

    if kind == "evidence":
        if "已經五站了" in body or any(point not in body for point in EVIDENCE8):
            result.red("S-3.3", "Evidence 八點不齊或摺站省略")

    if kind == "cap":
        if re.search(r"第\s*3\s*次|重寫第 3", body):
            result.red("RP-9", "hop 重寫第三次")
        if re.search(r"Decide 重開第\s*2|第\s*2\s*次.*Decide", body):
            result.red("RP-10", "Decide 重開第二次")
        if re.search(r"Goal 重開第\s*2|第\s*2\s*次.*Goal", body):
            result.red("RP-11", "Goal 重開第二次")

    if kind in ("reopen", "q6"):
        for match in REOPEN.finditer(body):
            result.red("S-8.6", "重開已拒案 %s" % match.group(1))
        if "採用現場" in body and re.search(r"已核|Observed|都蓋章", body):
            if not re.search(r"Assumption|仍待驗", body):
                result.red("S-6.3", "Q6 升格擋 G2")

    return result


def live_close(root):
    result = Result()
    slug = Path(root) / "docs" / "dev" / "five-station-simplify"
    names = {path.name for path in slug.glob("*") if path.is_file()}
    old = [name for name in STAGE_MD if name in names]
    result.info["seven_old_count"] = len(old)
    result.info["new_family"] = any(name in names for name in NEW_FAMILY)
    if result.info["new_family"]:
        result.red("S-1.1", "新家族檔名存在")
    blob = ""
    for name in ("4-spec.md", "5-tasks.md"):
        path = slug / name
        if path.is_file():
            blob += path.read_text(encoding="utf-8")
    for token in ("G1", "G2", "ACCEPTED"):
        result.info["token_%s" % token] = token in blob
        if token not in blob:
            result.red("S-1.1", "缺 token %s" % token)
    tasks = slug / "5-tasks.md"
    if tasks.is_file():
        text = tasks.read_text(encoding="utf-8")
        if REOPEN.search(text):
            result.red("S-8.6", "5-tasks 出現改採已拒案")
        files = []
        for match in re.finditer(r"^-\s*Files:\s*(.*)$", text, re.M):
            files.extend(split_files(match.group(1)) or [])
        closed = True
        for item in files:
            if not any(item == allowed or item.startswith(allowed) for allowed in F1_UNION):
                closed = False
                result.red("S-8.5", "Files 越界 %s" % item)
        result.info["files_closed"] = closed
    spec = slug / "4-spec.md"
    if spec.is_file():
        spec_text = spec.read_text(encoding="utf-8")
        result.info["q6_open"] = bool(re.search(
            r"Q6[^\n]*採用現場[^\n]*\|\s*open\b", spec_text
        ))
        if not result.info["q6_open"]:
            result.red("S-6.2", "Q6 Assumption refs 不是 open")
        for i, line in enumerate(spec_text.splitlines(), 1):
            if "採用現場" not in line or not re.search(r"已核|Observed", line):
                continue
            if re.search(r"Assumption|仍待驗", line):
                continue
            if re.search(r"GIVEN|寫成 Observed|升格|不得把 Q6", line):
                continue
            result.red("S-6.3", "4-spec L%d Q6 升格" % i)
    result.info["live"] = True
    return result


def check_path(path, root=None):
    root = root or str(ROOT)
    return evaluate(Path(path).read_text(encoding="utf-8"), path=str(path), root=root)


def main(argv):
    parser = argparse.ArgumentParser(description="F1 five-station teeth")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--live", action="store_true")
    parser.add_argument("path", nargs="?")
    args = parser.parse_args(argv)
    if args.live:
        result = live_close(args.root)
    elif args.path:
        result = check_path(args.path, args.root)
    else:
        parser.print_help()
        return 2
    print(result.dump())
    return 1 if result.is_red else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
