#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dev-flow gate — Human verdict 寫入器。

正本是 docs/dev/<slug>/<stage>.md 頂欄 verdict:(PASS | REQUEST_CHANGES | HOLD)。
HTML / localStorage / sidecar 都不是正本;sidecar 與 md 衝突時 md 勝。
全勾不算 PASS。只有「提交判定」才該呼叫本檔。

用法(等同 dev-flow gate …):
  python3 scripts/devflow_gate.py write --root DIR --slug SLUG --stage STAGE \\
      --verdict PASS|REQUEST_CHANGES|HOLD [--notes TEXT] [--reviewer NAME] \\
      [--checked id,id] [--source-sha SHA] [--no-sidecar]
  python3 scripts/devflow_gate.py write-g2-auto --root DIR --slug SLUG \\
      --reviewer agent:<id> --evidence-ref <agent reviewer 報告路徑或 PR> [--notes TEXT]
  python3 scripts/devflow_gate.py serve --root DIR [--port 8765]

write 是人的「提交判定」:有 reviewer 時同時落 verdict_source: human_attested + attested_by: human:<reviewer>;
reviewer 是 agent／Jev → 拒收(G1/G2/G3 的 write 只收人)。
write-g2-auto 是 **G2 agent reviewer 放行的唯一寫入路徑**(契約 §7「G2 審查者產生」):只收 4-spec、
只收 PASS、只收 agent:<id> 且 ≠ authored_by／owner;寫前要 G2R 紀錄判 AUTO(沒有命中任何轉人條件;
沒有 Jev = no-op,routed_by: none)、機械檢查全過,缺一就不改檔(exit 2)。放行時呼叫
`devflow-jev.py g2-misrelease release` 記一筆(誤放行率分母;只記錄、不設門檻、不回滾)。
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

HUMAN_VERDICTS = ("PASS", "REQUEST_CHANGES", "HOLD")
GATE_STAGES = ("2-decision", "4-spec", "7-review")
NOTE_RE = re.compile(r"^- Human verdict note:.*$", re.M)
VERDICT_LINE_RE = re.compile(r"^verdict:\s*.*$", re.M)
FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)
SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def read_canonical_verdict(text: str) -> str:
    """md 頂欄 verdict: 是正本。讀不到或不是 Human 三值 → 空字串。"""
    match = FM_RE.match(text)
    if not match:
        return ""
    found = re.search(r"^verdict:\s*(\S+)", match.group(1), re.M)
    if not found:
        return ""
    value = found.group(1)
    return value if value in HUMAN_VERDICTS else ""


def _set_front_field(front: str, key: str, value: str) -> str:
    """頂欄同名鍵有就換、沒有就緊接在 verdict: 之後補一行。"""
    line_re = re.compile(r"^%s:\s*.*$" % re.escape(key), re.M)
    if line_re.search(front):
        return line_re.sub(lambda _m: "%s: %s" % (key, value), front, count=1)
    return re.sub(r"^(verdict:\s*.*)$", lambda m: "%s\n%s: %s" % (m.group(1), key, value), front, count=1,
                  flags=re.M)


def is_agent_reviewer(reviewer: str) -> bool:
    who = (reviewer or "").strip().lower()
    return who.startswith(("agent:", "jev"))


def patch_md(text: str, verdict: str, notes: str | None = None, reviewer: str = "",
             fields: dict | None = None) -> str:
    """寫入同檔頂欄 verdict:;可另寫一行 Human verdict note。
    有 reviewer 時同時落 `verdict_source: human_attested` 與 `attested_by: human:<reviewer>`
    (本函式的 reviewer 只收人;agent 的 G2 放行走 write_g2_auto,由它傳 fields)。"""
    if verdict not in HUMAN_VERDICTS:
        raise ValueError("verdict 必須是 PASS | REQUEST_CHANGES | HOLD")
    match = FM_RE.match(text)
    if not match:
        raise ValueError("md 沒有 frontmatter,拒絕假裝寫入")
    front = match.group(1)
    rest = text[match.end():]
    if VERDICT_LINE_RE.search(front):
        front = VERDICT_LINE_RE.sub("verdict: " + verdict, front, count=1)
    elif re.search(r"^status:\s*", front, re.M):
        front = re.sub(
            r"^(status:\s*.*)$",
            r"\1\nverdict: " + verdict,
            front,
            count=1,
            flags=re.M,
        )
    else:
        front = "verdict: " + verdict + "\n" + front
    who = (reviewer or "").strip().replace(" ", "_")
    if who:
        if is_agent_reviewer(who):
            raise ValueError("reviewer 不得是 agent/Jev:本寫入器只收人的判定(G2 agent 放行走 write-g2-auto)")
        front = _set_front_field(front, "verdict_source", "human_attested")
        front = _set_front_field(front, "attested_by", "human:" + who)
    for key, value in (fields or {}).items():
        front = _set_front_field(front, key, value)
    if notes:
        line = "- Human verdict note: " + notes.splitlines()[0]
        if NOTE_RE.search(rest):
            rest = NOTE_RE.sub(line, rest, count=1)
        else:
            rest = line + "\n" + rest
    return "---\n" + front + "\n---\n" + rest


def git_sha(root: pathlib.Path) -> str:
    try:
        run = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        if run.returncode == 0:
            return run.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def sidecar_payload(stage: str, verdict: str, notes: str, checked, reviewer: str,
                    source_sha: str) -> dict:
    return {
        "gate": stage,
        "verdict": verdict,
        "notes": notes or "",
        "checked": list(checked or []),
        "source_sha": source_sha or "",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reviewer": reviewer or "",
    }


def md_path(root: pathlib.Path, slug: str, stage: str) -> pathlib.Path:
    if stage not in GATE_STAGES:
        raise ValueError("stage 必須是 2-decision | 4-spec | 7-review")
    if not SLUG_RE.match(slug):
        raise ValueError("slug 非法")
    path = (root / "docs" / "dev" / slug / f"{stage}.md").resolve()
    base = (root / "docs" / "dev").resolve()
    if base not in path.parents and path.parent != base:
        raise ValueError("拒絕寫出 docs/dev/ 之外")
    return path


def write_verdict(root: pathlib.Path, slug: str, stage: str, verdict: str,
                  notes: str = "", reviewer: str = "", checked=None,
                  source_sha: str = "", sidecar: bool = True) -> dict:
    path = md_path(root, slug, stage)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    text = path.read_text(encoding="utf-8")
    sha = source_sha or git_sha(root)
    if is_agent_reviewer(reviewer):
        raise ValueError("reviewer 不得是 agent/Jev:write 只收人的判定"
                         "(G1/G3 維持人審;G2 agent 放行只走 write-g2-auto)")
    extra = {"g2_mode": "human"} if stage == "4-spec" and reviewer.strip() else None
    patched = patch_md(text, verdict, notes or None, reviewer=reviewer, fields=extra)
    path.write_text(patched, encoding="utf-8")
    side_path = path.with_suffix(".verdict.json")
    if sidecar:
        payload = sidecar_payload(stage, verdict, notes, checked, reviewer, sha)
        side_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return {
        "path": str(path),
        "verdict": read_canonical_verdict(path.read_text(encoding="utf-8")),
        "sidecar": str(side_path) if sidecar else "",
        "source_sha": sha,
    }


def _load_g2auto():
    """G2 auto 判定住 devflow_jev/g2auto.py(與本檔並排散發)。找不到 → 拒絕(fail-closed:不當成可放行)。"""
    here = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isfile(os.path.join(here, "devflow_jev", "g2auto.py")):
        raise ValueError("找不到 devflow_jev/g2auto.py —— G2 agent 放行無法驗證,交給人審")
    if here not in sys.path:
        sys.path.insert(0, here)
    from devflow_jev import attestation, g2auto  # noqa: E402
    return attestation, g2auto


def _record_agent_release(root: pathlib.Path, slug: str, case_hash: str, evidence_ref: str,
                          reviewer: str) -> dict:
    """呼叫 `devflow-jev.py g2-misrelease release` 記一筆 agent 放行(誤放行率分母)。失敗 → 不放行。"""
    here = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(here, "devflow-jev.py")
    if not os.path.isfile(script):
        raise ValueError("找不到 devflow-jev.py —— 記不了 g2-misrelease release,不放行")
    run = subprocess.run(
        [sys.executable, script, "--root", str(root), "g2-misrelease", "release", "--slug", slug,
         "--case-hash", case_hash, "--evidence-ref", evidence_ref, "--reported-by", reviewer],
        capture_output=True, text=True, timeout=60, check=False)
    if run.returncode != 0:
        raise ValueError("g2-misrelease release 失敗(exit %d):%s" % (run.returncode, run.stderr.strip()[-300:]))
    return json.loads(run.stdout)


def write_g2_auto(root: pathlib.Path, slug: str, reviewer: str, evidence_ref: str,
                  notes: str = "", source_sha: str = "", sidecar: bool = True) -> dict:
    """G2 agent reviewer 放行(契約 §7):agent PASS + 機械檢查全過 + G2R 判 AUTO(未命中任何轉人條件)。
    任一不成立 → ValueError,md 不動、不記 release。成立 → 先記 release,再寫頂欄。"""
    attestation, g2auto = _load_g2auto()
    path = md_path(root, slug, "4-spec")
    if not path.is_file():
        raise FileNotFoundError(str(path))
    reviewer = (reviewer or "").strip()
    if not reviewer.startswith("agent:"):
        raise ValueError("write-g2-auto 只收 agent:<id>(人的判定走 write)")
    text = path.read_text(encoding="utf-8")
    fm = attestation.parse_frontmatter(text)
    record = g2auto.latest_g2r_record(str(root), slug)
    if record is None:
        raise ValueError("沒有 G2R 分流紀錄(.devflow/jev/g2r.jsonl)—— 先跑 devflow-jev.py g2r;"
                         "沒有 Jev 也要先跑(零網路,routed_by: none)")
    mech = g2auto.mechanical_checks(str(root), slug)
    candidate = dict(fm)
    fields = {
        "verdict_source": g2auto.AUTO_SOURCE,
        "attested_by": reviewer,
        "g2_mode": "auto",
        "routed_by": str(record.get("routed_by") or ""),
        "g2r_case": str(record.get("case_hash")),
        "g2r_jev": str(record.get("jev_snapshot") or g2auto.ROUTED_BY_NONE),
        "mechanical": mech["digest"],
    }
    candidate.update(fields)
    candidate["verdict"] = "PASS"
    problems = g2auto.auto_release_problems(str(root), slug, candidate, g2r_record=record,
                                            require_record=True, mechanical=mech)
    if problems:
        raise ValueError("G2 不能由 agent 放行,交給人審:" + ";".join(problems))
    release = _record_agent_release(root, slug, fields["g2r_case"], evidence_ref, reviewer)
    sha = source_sha or git_sha(root)
    patched = patch_md(text, "PASS", None, fields=fields)       # agent 的 notes 只進 sidecar,不冒充 Human verdict note
    path.write_text(patched, encoding="utf-8")
    side_path = path.with_suffix(".verdict.json")
    if sidecar:
        payload = sidecar_payload("4-spec", "PASS", notes, [], reviewer, sha)
        payload.update({"verdict_source": g2auto.AUTO_SOURCE, "g2_mode": "auto", "routed_by": fields["routed_by"]})
        side_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "path": str(path),
        "verdict": read_canonical_verdict(path.read_text(encoding="utf-8")),
        "verdict_source": g2auto.AUTO_SOURCE,
        "g2_mode": "auto",
        "routed_by": fields["routed_by"],
        "g2_misrelease_release": release.get("written"),
        "sidecar": str(side_path) if sidecar else "",
        "source_sha": sha,
    }


def _send_json(handler: BaseHTTPRequestHandler, code: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def make_handler(root: pathlib.Path):
    docs = (root / "docs" / "dev").resolve()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            sys.stderr.write("dev-flow gate serve: " + (fmt % args) + "\n")

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_POST(self):
            if urlparse(self.path).path != "/devflow-gate/verdict":
                _send_json(self, 404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length") or "0")
            if length <= 0 or length > 1_000_000:
                _send_json(self, 400, {"error": "bad body"})
                return
            try:
                data = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                _send_json(self, 400, {"error": "json"})
                return
            try:
                result = write_verdict(
                    root,
                    str(data.get("slug") or ""),
                    str(data.get("gate") or data.get("stage") or ""),
                    str(data.get("verdict") or ""),
                    notes=str(data.get("notes") or ""),
                    reviewer=str(data.get("reviewer") or ""),
                    checked=data.get("checked") or [],
                    source_sha=str(data.get("source_sha") or ""),
                    sidecar=bool(data.get("sidecar", True)),
                )
            except (ValueError, FileNotFoundError, OSError) as err:
                _send_json(self, 400, {"error": str(err)})
                return
            _send_json(self, 200, result)

        def do_GET(self):
            raw = unquote(urlparse(self.path).path)
            if raw in ("/", "/index.html"):
                body = (
                    "dev-flow gate serve\n"
                    "開 docs/dev/<slug>/<stage>.html 後按「提交判定」。\n"
                    "POST /devflow-gate/verdict 寫 md 頂欄 verdict:。\n"
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            rel = raw.lstrip("/")
            target = (root / rel).resolve()
            try:
                target.relative_to(docs)
            except ValueError:
                self.send_error(403, "only docs/dev/")
                return
            if not target.is_file():
                self.send_error(404, "missing")
                return
            data = target.read_bytes()
            ctype = "text/html; charset=utf-8" if target.suffix == ".html" else "application/octet-stream"
            if target.suffix == ".md":
                ctype = "text/markdown; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def serve(root: pathlib.Path, port: int) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), make_handler(root))
    print(
        f"dev-flow gate serve  http://127.0.0.1:{port}/  "
        f"(POST /devflow-gate/verdict → md 頂欄 verdict:)",
        flush=True,
    )
    httpd.serve_forever()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="dev-flow gate")
    sub = parser.add_subparsers(dest="cmd", required=True)

    write_p = sub.add_parser("write", help="寫同目錄 md 頂欄 verdict:")
    write_p.add_argument("--root", required=True)
    write_p.add_argument("--slug", required=True)
    write_p.add_argument("--stage", required=True, choices=GATE_STAGES)
    write_p.add_argument("--verdict", required=True, choices=HUMAN_VERDICTS)
    write_p.add_argument("--notes", default="")
    write_p.add_argument("--reviewer", default="")
    write_p.add_argument("--checked", default="")
    write_p.add_argument("--source-sha", default="")
    write_p.add_argument("--no-sidecar", action="store_true")

    auto_p = sub.add_parser("write-g2-auto",
                            help="G2 agent reviewer 放行(只 4-spec;需 G2R AUTO + 機械檢查全過 + author≠approver)")
    auto_p.add_argument("--root", required=True)
    auto_p.add_argument("--slug", required=True)
    auto_p.add_argument("--reviewer", required=True, help="agent:<id>(不得 = authored_by / owner / Jev)")
    auto_p.add_argument("--evidence-ref", required=True, help="agent reviewer 報告路徑或 PR 連結")
    auto_p.add_argument("--notes", default="")
    auto_p.add_argument("--source-sha", default="")
    auto_p.add_argument("--no-sidecar", action="store_true")

    serve_p = sub.add_parser("serve", help="本機 POST 寫入 md")
    serve_p.add_argument("--root", default=".")
    serve_p.add_argument("--port", type=int, default=int(os.environ.get("DEVFLOW_GATE_PORT", "8765")))

    args = parser.parse_args(argv)
    if args.cmd == "write":
        checked = [x for x in args.checked.split(",") if x]
        try:
            result = write_verdict(
                pathlib.Path(args.root).expanduser().resolve(),
                args.slug, args.stage, args.verdict,
                notes=args.notes, reviewer=args.reviewer, checked=checked,
                source_sha=args.source_sha, sidecar=not args.no_sidecar,
            )
        except (ValueError, FileNotFoundError, OSError) as err:
            print(str(err), file=sys.stderr)
            return 2
        print(json.dumps(result, ensure_ascii=False))
        return 0
    if args.cmd == "write-g2-auto":
        try:
            result = write_g2_auto(
                pathlib.Path(args.root).expanduser().resolve(), args.slug, args.reviewer,
                args.evidence_ref, notes=args.notes, source_sha=args.source_sha,
                sidecar=not args.no_sidecar,
            )
        except (ValueError, FileNotFoundError, OSError) as err:
            print(str(err), file=sys.stderr)
            return 2
        print(json.dumps(result, ensure_ascii=False))
        return 0
    serve(pathlib.Path(args.root).expanduser().resolve(), args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
