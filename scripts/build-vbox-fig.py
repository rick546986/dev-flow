#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直式置中 SVG 方塊圖 —— 各站同類圖的共用產圖器。

契約:notes/design/vbox-fig-contract.md
牙:scripts/check-vbox-fig.sh

輸入是抽象步驟列(JSON):每步 kind(.b/.hl/.wn)、標題、一到三行小字。
輸出完整 <svg viewBox="0 0 280 …">,框寬 200、左右置中、框間直線。

用法:
  scripts/build-vbox-fig.py <steps.json>
  scripts/build-vbox-fig.py --fixture lifecycle

無參數或 --help 印用法並 exit 2。
exit:0 = 寫出 stdout / 1 = 步驟列不合法 / 2 = 用法錯誤、檔案讀不到
"""
from __future__ import print_function

import html
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIX_DIR = ROOT / "scripts" / "fixtures" / "vbox-fig"

CANVAS_W = 280
BOX_W = 200
BOX_X = 40
CX = 140
TOP = 10
BOTTOM = 10
GAP = 22
PAD_TOP = 12
TITLE_H = 16
LINE_H = 14
PAD_BOTTOM = 12
MAX_LINES = 3
KINDS = ("b", "hl", "wn")
FIXTURES = ("lifecycle",)


def usage():
    print(
        "用法:build-vbox-fig.py <steps.json>\n"
        "     build-vbox-fig.py --fixture lifecycle\n"
        "契約:notes/design/vbox-fig-contract.md\n"
        "輸入 JSON:每步 kind(b|hl|wn)、title、lines(一到三行)。\n"
        "輸出完整 <svg viewBox>,框寬 200、畫布 280、置中、max-width 360px。",
        file=sys.stderr,
    )


def die(code, msg):
    print(msg, file=sys.stderr)
    sys.exit(code)


def esc(text):
    return html.escape(text or "", quote=True)


def box_h(n_lines):
    return PAD_TOP + TITLE_H + n_lines * LINE_H + PAD_BOTTOM


def load_payload(path):
    try:
        raw = pathlib.Path(path).read_text(encoding="utf-8")
    except OSError as err:
        die(2, "讀不到步驟列:%s" % err)
    try:
        data = json.loads(raw)
    except ValueError as err:
        die(1, "步驟列不是 JSON:%s" % err)
    if isinstance(data, list):
        return "", data
    if isinstance(data, dict):
        steps = data.get("steps")
        if not isinstance(steps, list):
            die(1, "JSON 要有 steps 陣列,或直接給步驟陣列")
        aria = data.get("aria") or ""
        if not isinstance(aria, str):
            die(1, "aria 必須是字串")
        return aria, steps
    die(1, "JSON 必須是步驟陣列或含 steps 的物件")


def normalize(raw_steps):
    steps = []
    if not raw_steps:
        die(1, "步驟列是空的")
    for i, item in enumerate(raw_steps):
        if not isinstance(item, dict):
            die(1, "第 %d 步不是物件" % (i + 1))
        kind = item.get("kind")
        title = item.get("title")
        lines = item.get("lines")
        if kind not in KINDS:
            die(1, "第 %d 步 kind 只能是 b／hl／wn,不准發明 parked／第三態"
                % (i + 1))
        if not isinstance(title, str) or not title.strip():
            die(1, "第 %d 步缺標題" % (i + 1))
        if not isinstance(lines, list) or not (1 <= len(lines) <= MAX_LINES):
            die(1, "第 %d 步 lines 必須一到三行" % (i + 1))
        clean = []
        for line in lines:
            if not isinstance(line, str) or not line.strip():
                die(1, "第 %d 步有空的小字" % (i + 1))
            clean.append(line.strip())
        steps.append((kind, title.strip(), clean))
    return steps


def render_svg(aria, steps):
    heights = [box_h(len(lines)) for _kind, _title, lines in steps]
    height = TOP + sum(heights) + GAP * (len(steps) - 1) + BOTTOM
    label = aria.strip() or "直式步驟方塊"
    parts = [
        '<svg viewBox="0 0 %d %d" role="img" aria-label="%s" '
        'style="display:block;max-width:360px;margin:0 auto;height:auto">'
        % (CANVAS_W, height, esc(label)),
    ]
    y = TOP
    for i, (kind, title, lines) in enumerate(steps):
        h = heights[i]
        parts.append(
            '<rect class="%s" x="%d" y="%d" width="%d" height="%d" rx="6"/>'
            % (kind, BOX_X, y, BOX_W, h)
        )
        ty = y + PAD_TOP + 12
        parts.append(
            '<text class="nl" x="%d" y="%d" text-anchor="middle">%s</text>'
            % (CX, ty, esc(title))
        )
        ly = ty
        for line in lines:
            ly += LINE_H
            parts.append(
                '<text class="sm" x="%d" y="%d" text-anchor="middle">%s</text>'
                % (CX, ly, esc(line))
            )
        if i < len(steps) - 1:
            y1 = y + h
            y2 = y + h + GAP
            parts.append(
                '<line x1="%d" y1="%d" x2="%d" y2="%d" '
                'stroke="currentColor" stroke-width="1.4"/>'
                % (CX, y1, CX, y2)
            )
        y += h + GAP
    parts.append("</svg>")
    return "\n".join(parts)


def parse_args(argv):
    if not argv or argv[0] in ("-h", "--help", "help"):
        usage()
        sys.exit(2)
    if argv[0] == "--fixture":
        if len(argv) != 2 or argv[1] not in FIXTURES:
            usage()
            sys.exit(2)
        path = FIX_DIR / ("%s.json" % argv[1])
        if not path.is_file():
            die(2, "找不到 fixture:%s" % path)
        return str(path)
    if len(argv) != 1 or argv[0].startswith("-"):
        usage()
        sys.exit(2)
    path = argv[0]
    if not os.path.isfile(path):
        die(2, "讀不到步驟列:%s" % path)
    return path


def main(argv):
    path = parse_args(argv)
    aria, raw = load_payload(path)
    svg = render_svg(aria, normalize(raw))
    sys.stdout.write(svg + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
