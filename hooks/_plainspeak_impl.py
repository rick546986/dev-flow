#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""devflow-plainspeak.sh 的實作本體:讀規則正本,包成 hook JSON 注入。

規則文字**不寫在這裡** —— 正本是同目錄的 plainspeak-rules.md 的 inject 區塊。
理由:規則同時被 hook(每輪注入)與個人帳號的 plain-language-zh skill(查閱)消費,
兩邊各存一份必漂移(本 repo 第 7 型「不對稱記帳」的同一種病)。

fail-open:規則檔不見或區塊抽不到 → 不輸出、exit 0。這支只是提醒,不是關卡,
壞掉不該讓使用者送不出訊息。
"""
import json
import pathlib
import re
import sys

START = "<!-- devflow:inject:start -->"
END = "<!-- devflow:inject:end -->"


def main():
    rules = pathlib.Path(__file__).resolve().parent / "plainspeak-rules.md"
    try:
        text = rules.read_text(encoding="utf-8")
    except OSError:
        return 0
    match = re.search(re.escape(START) + r"\n(.*?)\n" + re.escape(END), text, re.S)
    if not match:
        return 0
    body = match.group(1).strip()
    if not body:
        return 0
    # 兩個欄位都給:不同版本的 runtime 讀的欄位不同,多給一個不認得的鍵會被忽略,
    # 少給則整段靜默不生效。
    json.dump({
        "systemMessage": body,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": body,
        },
    }, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
