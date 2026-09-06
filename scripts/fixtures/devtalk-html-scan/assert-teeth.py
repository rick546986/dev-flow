#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跑掃頁產生器對 good + 牙 1–4 bad fixture。不讀產品檔案系統。"""
from __future__ import print_function

import os
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILD = ROOT / "scripts" / "build-scan-html.py"

BAD = (
    ("bad-1-fields", "四段不齊"),
    ("bad-2-conclusion", "已解／假設／移交"),
    ("bad-3-path", "不在 Context"),
    ("bad-4-pipe", "舊單行"),
    ("bad-4-empty", "抽不到 Interview Log"),
)


def run_builder(md_path, out_path):
    return subprocess.run(
        [sys.executable, str(BUILD), "--action", str(md_path), "--out", str(out_path)],
        capture_output=True,
        text=True,
    )


def main():
    failures = []
    fd, out = tempfile.mkstemp(suffix=".html", prefix="scan-teeth-")
    os.close(fd)
    try:
        good = HERE / "good" / "1-discussion.md"
        proc = run_builder(good, out)
        if proc.returncode != 0:
            failures.append(
                "good 必須綠,rc=%s\n%s" % (proc.returncode, (proc.stderr or "")[-400])
            )
        else:
            text = pathlib.Path(out).read_text(encoding="utf-8")
            if 'id="scan-log"' not in text:
                failures.append("good 缺 #scan-log")
            if "<summary>問答摘要</summary>" not in text:
                failures.append("good summary 須含問答摘要")
            if 'open' in text.split('id="scan-log"', 1)[-1][:80]:
                failures.append("good #scan-log 不得預設 open")
            if 'class="tablewrap"' not in text:
                failures.append("good #scan-log 須包 .tablewrap")
            if "<th>Q</th><th>事實</th><th>推理</th><th>結論</th>" not in text:
                failures.append("good #scan-log 須為四欄表")
            if "<p>Q:" in text:
                failures.append("good 不得再逐條 <p> 問答")
        for name, needle in BAD:
            md = HERE / name / "1-discussion.md"
            proc = run_builder(md, out)
            blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
            if proc.returncode != 1:
                failures.append(
                    "%s 必須 exit 1,實際 rc=%s\n%s" % (name, proc.returncode, blob[-400])
                )
            elif needle not in blob:
                failures.append(
                    "%s stderr 須含「%s」\n%s" % (name, needle, blob[-400])
                )
    finally:
        try:
            os.remove(out)
        except OSError:
            pass
    if failures:
        print("FAIL:\n- " + "\n- ".join(failures), file=sys.stderr)
        return 1
    print("ok good + teeth 1-4 (%d bad)" % len(BAD))
    return 0


if __name__ == "__main__":
    sys.exit(main())
