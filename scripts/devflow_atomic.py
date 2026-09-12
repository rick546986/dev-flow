#!/usr/bin/env python3
"""devflow_atomic.py — tmp + os.replace 寫入原語。

形狀與 scripts/write-stack-inventory.py 的 atomic_write 相同:
tmp + os.replace + 補尾端 newline。本模組只擁有寫入,不做驗證。
驗證失敗後不得呼叫本函式(由 scripts/diagir.py 保證)。
"""
from __future__ import print_function

import os


def atomic_write(path, text):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")
    os.replace(tmp, path)
