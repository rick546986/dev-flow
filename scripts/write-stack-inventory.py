#!/usr/bin/env python3
"""write-stack-inventory.py — 寫／核專案級 I2 `docs/dev/0-inventory.json`。

dev-setup install／upgrade／check 呼叫本檔。深度 = 宣告 pin + pin／requirements
第一層 direct_deps,不是 lock 全樹,也不是 per-slug。
I4(`--write-stack`)是選配投影,無 I2 不得先寫。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

SCHEMA = "devflow-stack-inventory/v1"
I2_REL = os.path.join("docs", "dev", "0-inventory.json")
I4_REL = os.path.join("docs", "dev", "0-stack.md")
REQ_LINE = re.compile(r"^([A-Za-z0-9_.-]+)==([^#\s]+)")


def die(msg, rc=1):
    print(msg, file=sys.stderr)
    raise SystemExit(rc)


def atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")
    os.replace(tmp, path)


def python_version(override):
    if override:
        return override
    try:
        out = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        blob = ((out.stdout or "") + " " + (out.stderr or "")).strip()
    except OSError:
        blob = ""
    match = re.search(r"(\d+\.\d+(?:\.\d+)?)", blob)
    return match.group(1) if match else "unknown"


def parse_requirements(path):
    pins = []
    if not os.path.isfile(path):
        return pins
    rel = path
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = REQ_LINE.match(line)
        if match:
            pins.append(
                {
                    "name": match.group(1),
                    "version": match.group(2),
                    "source": rel,
                }
            )
    return pins


def parse_package_json(path):
    pins = []
    if not os.path.isfile(path):
        return pins
    try:
        data = json.loads(open(path, encoding="utf-8").read())
    except (OSError, ValueError):
        return pins
    if not isinstance(data, dict):
        return pins
    for key in ("dependencies", "devDependencies"):
        block = data.get(key) or {}
        if not isinstance(block, dict):
            continue
        for name, version in block.items():
            pins.append(
                {
                    "name": str(name),
                    "version": str(version).lstrip("^~>=<"),
                    "source": path,
                }
            )
    return pins


def collect_pins(root):
    pins = []
    seen = set()

    def add(items, source_rel):
        for item in items:
            item = dict(item)
            item["source"] = source_rel
            key = (item["name"], item["version"], source_rel)
            if key in seen:
                continue
            seen.add(key)
            pins.append(item)

    candidates = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if d not in (".git", "node_modules", ".venv", "venv", "__pycache__")
        ]
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""
        for name in filenames:
            if name.startswith("requirements") and name.endswith(".txt"):
                rel = os.path.join(rel_dir, name).replace("\\", "/") if rel_dir else name
                candidates.append(("req", os.path.join(dirpath, name), rel))
            if name == "package.json" and rel_dir in ("",):
                candidates.append(("pkg", os.path.join(dirpath, name), name))

    # 方法包慣用路徑優先(不掃 lock)
    render = os.path.join(root, "scripts", "requirements-methodology-render.txt")
    if os.path.isfile(render):
        add(
            parse_requirements(render),
            "scripts/requirements-methodology-render.txt",
        )

    for kind, abs_path, rel in candidates:
        if rel == "scripts/requirements-methodology-render.txt":
            continue
        if kind == "req":
            add(parse_requirements(abs_path), rel)
        else:
            add(parse_package_json(abs_path), rel)
    return pins


def detect_kind(root, forced):
    if forced in ("methodology-pack", "product"):
        return forced
    if os.path.isfile(
        os.path.join(root, "scripts", "requirements-methodology-render.txt")
    ):
        return "methodology-pack"
    return "product"


def gaps_for(pins, runtime_version):
    out = []
    for pin in pins:
        if pin["name"] == "markdown-it-py" and pin["version"] == "4.0.0":
            if runtime_version.startswith("3.9"):
                out.append(
                    {
                        "local_runtime": runtime_version,
                        "requirement": "Python 3.12+",
                        "pin": "markdown-it-py==4.0.0",
                        "source": pin["source"],
                    }
                )
    return out


def build_inventory(root, kind, runtime_version, runtime_cmd):
    pins = collect_pins(root)
    return {
        "schema": SCHEMA,
        "written_by": "dev-setup",
        "written_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "project_kind": kind,
        "languages": [
            {
                "language": "Python",
                "runtime_version": runtime_version,
                "runtime_cmd": runtime_cmd,
            }
        ],
        "declared_pins": pins,
        "direct_deps": list(pins),
        "gaps": gaps_for(pins, runtime_version),
    }


def write_i2(root, payload):
    dest = os.path.join(root, I2_REL)
    atomic_write(
        dest,
        json.dumps(payload, ensure_ascii=False, indent=2),
    )
    return dest


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_i4(root, inventory, digest_paths):
    i2 = os.path.join(root, I2_REL)
    if not os.path.isfile(i2):
        die("無 I2 不得先寫 I4:缺 docs/dev/0-inventory.json", 1)
    dest = os.path.join(root, I4_REL)
    lines = [
        "# 堆疊摘要(I4)",
        "",
        "盤點正本是 `docs/dev/0-inventory.json`。",
        "digest 不是 lock 正本。套件版本爭議以 lock／pin 檔為準。",
        "",
        "## Runtime",
        "",
    ]
    for lang in inventory.get("languages") or []:
        lines.append(
            "- %s %s (`%s`)"
            % (
                lang.get("language", ""),
                lang.get("runtime_version", ""),
                lang.get("runtime_cmd", ""),
            )
        )
    lines.extend(["", "## declared_pins", ""])
    for pin in inventory.get("declared_pins") or []:
        lines.append("- %s %s (`%s`)" % (pin.get("name"), pin.get("version"), pin.get("source")))
    if digest_paths:
        lines.extend(["", "## digest", ""])
        for rel in digest_paths:
            path = os.path.join(root, rel)
            if not os.path.isfile(path):
                continue
            lines.append("`%s` sha256:%s" % (rel, sha256_file(path)))
    atomic_write(dest, "\n".join(lines) + "\n")
    return dest


def main(argv=None):
    parser = argparse.ArgumentParser(description="寫專案級 I2 堆疊盤點")
    parser.add_argument("--root", default=".")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--kind",
        choices=("auto", "methodology-pack", "product"),
        default="auto",
    )
    parser.add_argument("--runtime-version", default="")
    parser.add_argument("--runtime-cmd", default="python3 --version")
    parser.add_argument(
        "--write-stack",
        action="store_true",
        help="選配寫 docs/dev/0-stack.md(人要求才用)",
    )
    parser.add_argument(
        "--digest",
        action="append",
        default=[],
        help="I4 digest 檔(相對 root);可重複",
    )
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root)
    i2_path = os.path.join(root, I2_REL)
    if args.check and not os.path.isfile(i2_path):
        print("broken:缺 docs/dev/0-inventory.json", file=sys.stderr)
        return 1
    kind = detect_kind(root, None if args.kind == "auto" else args.kind)
    runtime_version = python_version(args.runtime_version)
    payload = build_inventory(root, kind, runtime_version, args.runtime_cmd)
    dest = write_i2(root, payload)
    print("wrote %s kind=%s pins=%d" % (dest, kind, len(payload["declared_pins"])))
    if args.write_stack:
        i4 = write_i4(root, payload, args.digest)
        print("wrote %s" % i4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
