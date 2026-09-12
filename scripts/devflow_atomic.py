#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared tmp + os.replace write primitive.

Shape matches scripts/write-stack-inventory.py:30-37.
This module owns the write primitive only — no IR validation.
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
