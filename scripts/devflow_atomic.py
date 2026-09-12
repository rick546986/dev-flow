#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""原子寫入原語 —— tmp + os.replace + 尾端 newline。

形狀與 scripts/write-stack-inventory.py:30-37 相同。
本模組只擁有寫入;不做驗證,不得在驗證失敗後被呼叫。
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
