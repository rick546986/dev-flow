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
  python3 scripts/devflow_gate.py serve --root DIR [--port 8765]
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


def patch_md(text: str, verdict: str, notes: str | None = None) -> str:
    """寫入同檔頂欄 verdict:;可另寫一行 Human verdict note。"""
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
    patched = patch_md(text, verdict, notes or None)
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
    serve(pathlib.Path(args.root).expanduser().resolve(), args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
