#!/bin/bash
# gate twin 產生器守衛(Repo-local)。驗的是**規格有沒有真的被實作**,不是 html 好不好看。
#
# 規格正本:README §6〈審查動線頂區〉+ `_templates/{2-decision,4-spec}.md` 頂註。
# 三件必含,少一件那份 twin 就不是審查介面:
#   T1 動線頂區**五格**(格數固定,內容依 stage)
#   T2 待審項目逐條可勾 + 進度計數;**缺必填欄的項目要在卡上直接紅底現形**
#   T3 背景資料收進 <details>(預設收合、內容零刪減)
# 外加兩條產生器自身的契約:
#   T4 **同一份內容兩種殼**:本機版是完整 html 文件;artifact 片段**不得含**
#      doctype/html/head/body(發布時外層會自動包)。這條錯了不會報錯,只會靜靜壞掉。
#   T5 解析不到任何待審項目 → exit 1,**不產出空殼**(空殼會讓人以為審過了)
#
# 三個 stage 都對母版自帶範例 `example/contract-expiry-reminder/` 實跑 —— 等於自帶回歸:
# 產生器壞了、或母版模板改了標題層級,這裡先紅。
#
# 用法:scripts/check-gate-twin.sh
# exit:0 = 全過 / 1 = 有 FAIL / 2 = 環境問題
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

DEVFLOW_ROOT="$ROOT" DEVFLOW_TMP="$TMP" python3 - <<'PY'
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ["DEVFLOW_ROOT"])
TMP = Path(os.environ["DEVFLOW_TMP"])
BUILD = ROOT / "scripts/build-gate-twin.py"
EXAMPLE = ROOT / "example/contract-expiry-reminder"
STAGES = ("2-decision", "4-spec", "7-review")
# 完整文件外殼的判準:片段裡出現這些就是把外殼寫進片段了(<header> 不算,故要求後接空白或 >)
SHELL = re.compile(r"<!doctype|<html[\s>]|<head[\s>]|<body[\s>]", re.I)

FAILED = 0
CHECKS = 0


def check(cond, label, detail=""):
    global FAILED, CHECKS
    CHECKS += 1
    if cond:
        print(f"  ✓ {label}")
    else:
        FAILED += 1
        print(f"  ✗ {label}" + (f" — {detail}" if detail else ""))


def run(root, slug, stage):
    return subprocess.run([sys.executable, str(BUILD), str(root), slug, stage],
                          capture_output=True, text=True)


print("-- 三個 gate stage 對母版範例實跑(自帶回歸)--")
proj = TMP / "proj/docs/dev/demo"
proj.mkdir(parents=True)
for st in STAGES:
    shutil.copy(EXAMPLE / f"{st}.md", proj / f"{st}.md")

for st in STAGES:
    r = run(TMP / "proj", "demo", st)
    if r.returncode != 0:
        check(False, f"{st}:產出成功", (r.stderr or r.stdout).strip().splitlines()[-1:] or "無輸出")
        continue
    local = (proj / f"{st}.html").read_text(encoding="utf-8")
    art = (proj / f"{st}-review.artifact.html").read_text(encoding="utf-8")
    check(True, f"{st}:產出成功")
    check(local.count('<div class="cell">') == 5,
          f"{st}:T1 動線頂區五格", f"實際 {local.count('<div class=chr(34)cell')} 格")
    check(local.count('class="s-card') > 0 and 'id="done"' in local,
          "  T2 待審項目逐條可勾 + 進度計數")
    check('<details class="doc">' in local, "  T3 背景資料收進 details")
    check(bool(SHELL.search(local)) and not SHELL.search(art),
          "  T4 兩種殼:本機版完整文件、artifact 片段無外殼",
          "片段含 doctype/html/head/body" if SHELL.search(art) else "本機版缺外殼")

print("-- T2 負向:缺必填欄要在卡上紅底現形 --")
fx = ROOT / "scripts/fixtures/gate-twin/missing-obs"
shutil.copytree(fx, TMP / "fx")
r = run(TMP / "fx", "demo", "4-spec")
check(r.returncode == 0, "缺觀測欄的 spec 仍產得出來(要讓人看見問題,不是擋住)")
if r.returncode == 0:
    t = (TMP / "fx/docs/dev/demo/4-spec.html").read_text(encoding="utf-8")
    check(t.count('class="s-card bad"') == 1, "缺「觀測」欄的那條 S 渲染成紅底",
          f"紅底卡 {t.count('class=chr(34)s-card bad')} 張,應為 1")
    check("缺觀測欄" in t, "動線頂區點出缺幾條")

print("-- T5 負向:解析不到任何待審項目要 exit 1,不產空殼 --")
empty = TMP / "empty/docs/dev/demo"
empty.mkdir(parents=True)
(empty / "4-spec.md").write_text("# 4. 規格\n\n## 沒有任何 R 或 S\n\n隨便寫點東西。\n",
                                 encoding="utf-8")
r = run(TMP / "empty", "demo", "4-spec")
check(r.returncode == 1, "空 spec → exit 1", f"實際 exit {r.returncode}")
check(not (empty / "4-spec.html").exists(), "空 spec → 不產出空殼 html")

print("-- 用法錯誤 --")
r = subprocess.run([sys.executable, str(BUILD)], capture_output=True, text=True)
check(r.returncode == 2, "無參數 → exit 2 並印用法", f"實際 exit {r.returncode}")

print()
if FAILED:
    print(f"❌ gate twin 產生器守衛:{FAILED} 項失敗(共 {CHECKS} 項)")
    sys.exit(1)
print(f"✅ gate twin 產生器守衛:全過({CHECKS} 項)")
PY
