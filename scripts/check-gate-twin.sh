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
    check(len(re.findall(r'<a class="cell"', local)) == 5,
          f"{st}:T1 動線頂區五格", f"實際 {local.count(chr(60) + chr(97) + chr(32) + chr(99))} 個")
    check(local.count('class="s-card') > 0 and 'id="done"' in local,
          "  T2 待審項目逐條可勾 + 進度計數")
    # 卡片殼在但內容全空 = 審查者什麼也看不到,而只數卡片數的斷言照樣過(複審缺口 E)
    n_cards = len(re.findall(r'<article class="s-card', local))
    empty_bodies = len(re.findall(r'<div class="gwt"></div>', local))
    # 三站都驗:卡片殼在但內容全空 = 審查者什麼都看不到,而只數卡片數的斷言照樣過。
    # 7-review 的 Exit Checklist 卡本來就只有標題,故允許「部分」空,但不得全空。
    check(n_cards > 0 and empty_bodies < n_cards,
          "  T2 卡片內容不得全空(欄位被砍空要現形)",
          f"{empty_bodies}/{n_cards} 張空卡")
    check('<details class="doc"' in local, "  T3 背景資料收進 details")
    # M10 修了但當時沒有守衛,退回缺陷態不會被抓(複審缺口 F)
    check(all(k in local for k in ('class="progress-in"', 'class="count"',
                                   'class="bar"', 'class="btn"')),
          "  T2 進度條 markup 齊(progress-in/count/bar/btn)")
    check(local.count('<div class="doc-in"></div>') == 0,
          "  T3 背景資料不得是空殼", "有 details 但內容為空")
    hrefs = re.findall(r'class="cell" href="#([^"]+)"', local)
    ids = set(re.findall(r'id="([^"]+)"', local))
    check(len(hrefs) == 5, f"{st}:T7 五格都是可點錨點", f"實際 {len(hrefs)} 個 href")
    check(bool(hrefs) and all(h in ids for h in hrefs),
          f"{st}:T7 每個錨點都有對應目標",
          f"落空:{[h for h in hrefs if h not in ids]}")
    # 全部指向同一個(例如都退化成 #cards)= 等於沒有跳轉,但「解析得到」照樣成立
    check(len(set(hrefs)) >= 4, f"{st}:T7 五格指向不同段落(不得退化成少數幾個)",
          f"只指向 {sorted(set(hrefs))}")
    check(bool(SHELL.search(local)) and not SHELL.search(art),
          "  T4 兩種殼:本機版完整文件、artifact 片段無外殼",
          "片段含 doctype/html/head/body" if SHELL.search(art) else "本機版缺外殼")

print("-- T8 五格內容對齊 README §6 規格 --")
# 規格正本:README §6〈審查動線頂區〉的三列表。格數對了但內容答非所問 = 沒做到
# (2026-08-15 獨立審查 H5:三站的格子內容當時與同一份 diff 新增的規格全不符)。
# ⚠️ 標籤集合**從 README §6 的表格解析**,不硬寫在本檔。
# 硬寫 = 斷言釘在副本而不是正本:改 README 的規格文字,守衛照樣全綠
#(2026-08-15 複審缺口 G;與 H2「守衛只驗字串在不在」是同一類病)。
def readme_keys():
    txt = (ROOT / "README.md").read_text(encoding="utf-8")
    out = {}
    for st in STAGES:
        m = re.search(r"^\|\s*\*\*" + re.escape(st) + r"\(G\d\)\*\*\s*\|(.+?)\|\s*$",
                      txt, re.M)
        if not m:
            continue
        # 反引號內的 `x/y` 斜線不是分隔符,先遮蔽再切
        cells = [c.strip() for c in re.sub(r"`[^`]*`", "``", m.group(1)).split("/")]
        out[st] = {re.split(r"[(（]", c)[0].strip().strip("*` ") for c in cells if c.strip()}
    return out


EXPECT_KEYS = readme_keys()
check(len(EXPECT_KEYS) == len(STAGES) and all(len(v) == 5 for v in EXPECT_KEYS.values()),
      "五格標籤能從 README §6 正本解析出三站各五格",
      f"解析到 {[(k, len(v)) for k, v in EXPECT_KEYS.items()]}")
for st in STAGES:
    txt = (proj / f"{st}.html").read_text(encoding="utf-8")
    keys = set(re.findall(r'class="cell"[^>]*><span class="k">([^<]+)</span>', txt))
    check(keys == EXPECT_KEYS.get(st, set()), f"{st}:五格標籤與 README §6 逐字一致",
          f"多 {sorted(keys - EXPECT_KEYS[st])} / 少 {sorted(EXPECT_KEYS[st] - keys)}")

print("-- G\u2032/G\u2033 跨檔規格一致:README §6 vs 三份模板頂註 --")
# N4 的根因:規格同時寫在 README §6 與三份模板頂註,兩邊不一致時沒有任何檢查。
# 把模板改回舊值 → 必須紅(2026-08-15 二次複審 G\u2033)。
TPL = {"2-decision": "_templates/2-decision.md", "4-spec": "_templates/4-spec.md",
       "7-review": "_templates/7-review.md"}


def tpl_keys(path):
    txt = (ROOT / path).read_text(encoding="utf-8")
    m = re.search(r"^>\s*\|\s*1\s*\|\s*\*\*動線頂區五格\*\*[^|]*\|(.+?)\|\s*$", txt, re.M)
    if not m:
        return set()
    cell = re.sub(r"`[^`]*`", "``", m.group(1))
    cell = re.sub(r"——.*$", "", cell)
    return {re.split(r"[(（]", c)[0].strip().strip("*` ")
            for c in cell.split("/") if c.strip()}


for st in STAGES:
    tk = tpl_keys(TPL[st])
    check(tk == EXPECT_KEYS.get(st, set()),
          f"{st}:模板頂註的五格與 README §6 逐字一致",
          f"模板 {sorted(tk)} vs README {sorted(EXPECT_KEYS.get(st, set()))}")

print("-- P4 回歸:整節只有一個 code fence 的章節不得消失 --")
p4 = TMP / "p4/docs/dev/demo"
p4.mkdir(parents=True)
FENCE = "`" * 3
(p4 / "4-spec.md").write_text(f"""---
stage: 4-spec
status: draft
---

# 4

## ADDED Requirements

### R-1: x
#### S-1
- GIVEN a
- WHEN b
- THEN c
- 觀測:d

## 變更架構圖

{FENCE}
一張只有程式碼區塊的圖 CANARY-P4
{FENCE}
""", encoding="utf-8")
r = run(TMP / "p4", "demo", "4-spec")
check(r.returncode == 0, "只有 fence 的章節:產得出來")
if r.returncode == 0:
    pt = (p4 / "4-spec.html").read_text(encoding="utf-8")
    check("CANARY-P4" in pt, "只有 fence 的章節不得整節消失",
          "該節被靜默丟掉(H_ANY 的 \\s 跨行吃掉了 body)")

print("-- S_HEAD 回歸:`#### S-1`(無尾隨標題文字)不得吞下一行的 GIVEN --")
# 同 P4 那類 bug,換一個正則:S_HEAD 的 `\s*` 含換行,`#### S-1` 沒有尾隨標題文字時
# 會跨行把下一行(通常是 `- GIVEN …`)整段吃進標題,GIVEN 欄從此消失
#(2026-08-15 三次複審 P4 同類,母版範例的 S-1 就中招)。
shd = TMP / "shead/docs/dev/demo"
shd.mkdir(parents=True)
(shd / "4-spec.md").write_text("""---
stage: 4-spec
status: draft
---

# 4. 規格

## ADDED Requirements

### R-1: x

#### S-1
- GIVEN 這行不得被吞
- WHEN b
- THEN c
- 觀測:d
""", encoding="utf-8")
r = run(TMP / "shead", "demo", "4-spec")
check(r.returncode == 0, "S_HEAD 回歸 fixture:產得出來")
if r.returncode == 0:
    sht = (shd / "4-spec.html").read_text(encoding="utf-8")
    # ⚠️ 不能只驗「這行不得被吞」這個子字串在不在 —— 被吞掉時,它照樣會出現,
    # 只是出現在標題而不是 GIVEN 欄位列(H2 的病:守衛只驗字串在不在)。
    # 要驗的是它落在**渲染出來的 GIVEN 欄位列**,不是隨便哪裡。
    check('<span class="gwt-k">GIVEN</span><span class="gwt-v">這行不得被吞</span>' in sht,
          "GIVEN 值渲染成 GIVEN 欄位列(不是被吞進標題)")
    m = re.search(r'<span class="s-id">S-1</span>\s*<span class="s-title">(.*?)</span>', sht)
    check(bool(m) and "GIVEN" not in m.group(1), "S-1 卡標題不含「GIVEN」(標題沒被跨行吃到下一行)",
          f"實際標題「{m.group(1) if m else '(無)'}」")

print("-- H2 負向:背景資料「內容零刪減」要真的被驗 --")
# fixture 的每個非卡片章節都埋了 CANARY-n;渲染函式若被改成 return "",這裡必紅。
shutil.copytree(ROOT / "scripts/fixtures/gate-twin/zero-deletion", TMP / "zd")
r = run(TMP / "zd", "demo", "4-spec")
check(r.returncode == 0, "零刪減 fixture 產得出來")
if r.returncode == 0:
    zt = (TMP / "zd/docs/dev/demo/4-spec.html").read_text(encoding="utf-8")
    missing = [f"CANARY-{i}" for i in range(1, 6) if f"CANARY-{i}" not in zt]
    check(not missing, "背景資料內容零刪減(5 個 canary 全在)", f"不見了:{missing}")
    check(zt.count('class="s-card') == 1,
          "程式碼區塊裡的假標題不得產生幻影卡", f"卡數 {len(re.findall(chr(99)+chr(108)+chr(97)+chr(115)+chr(115)+chr(61)+chr(34)+chr(115)+chr(45)+chr(99)+chr(97)+chr(114)+chr(100), zt))}")
    check("S-9.1" not in zt.split("背景資料")[0], "幻影卡 S-9.1 不在待審區")

print("-- T6 置頂節:判定與其前提不得被摺疊 --")
# 2026-08-15 dogfood 抓到的真 bug:用本工具產自己的 7-review 時,「限制聲明」被收進
# 背景資料、`## Verdict` 整節消失(被一條過度粗暴的排除條件誤殺)——最該先讀的三樣全不見。
pin = TMP / "pin/docs/dev/demo"
pin.mkdir(parents=True)
(pin / "7-review.md").write_text("""---
stage: 7-review
verdict: PRE-REVIEW
---

# 7. 驗證

## Coverage Matrix

| 條款 | 證據 |
|---|---|
| C1 | 見某處 |

## Verdict

判定寫在這裡,不得被摺疊。

## Known Limits

- K-1 這條限界不得被摺疊
""", encoding="utf-8")
(pin / "2-decision.md").write_text("""---
stage: 2-decision
status: draft
---

# 2. 收斂

## Approaches Considered

| 方案 | 摘要 |
|---|---|
| A | 做法一 |

## Decision

採 A —— G1 的判定,不得被摺疊。

## Rejected Alternatives

- B:理由
""", encoding="utf-8")
r7 = run(TMP / "pin", "demo", "7-review")
r2 = run(TMP / "pin", "demo", "2-decision")
check(r7.returncode == 0 and r2.returncode == 0, "置頂節材料兩站都產得出來")
loc7 = (pin / "7-review.html").read_text(encoding="utf-8")
loc2 = (pin / "2-decision.html").read_text(encoding="utf-8")


def pinned_has(text, section_title):
    """該章節是不是被渲染成置頂節(而不是摺進背景資料)。

    ⚠️ 不要用「字串在 details 外面就算看得到」來判斷 —— 動線頂區的註解文字
    也含「Known Limits」「採 A」這些字,會讓斷言恆真(2026-08-15 重跑破壞實驗
    時實測:拿掉 PINNED_PAT 的 Decision,舊寫法照樣全綠)。改成直接查置頂節的 id。
    """
    sid = "sec-" + re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "-", section_title).strip("-")[:48]
    if f'id="{sid}"' not in text:
        return None
    return f'<section class="pinned" id="{sid}"' in text


check(loc7.count('<section class="pinned"') >= 1, "7-review:有置頂節")
for key in ("Verdict", "Known Limits"):
    v = pinned_has(loc7, key)
    check(v is True, f"7-review:「{key}」直接看得到",
          "整節不見了" if v is None else "被摺疊進背景資料")
v2 = pinned_has(loc2, "Decision")
check(v2 is True, "2-decision:G1 的判定(## Decision)直接看得到",
      "整節不見了" if v2 is None else "被摺疊進背景資料")
m = re.search(r'<span class="k">判定</span><span class="v">(.*?)</span>', loc7)
check(bool(m) and "|" not in (m.group(1) if m else "|"),
      "7-review:動線「判定」格取到 verdict 值,不是表格分隔線",
      f"實際「{m.group(1) if m else '(無)'}」")

print("-- T2 負向:缺必填欄要在卡上紅底現形 --")
fx = ROOT / "scripts/fixtures/gate-twin/missing-obs"
shutil.copytree(fx, TMP / "fx")
r = run(TMP / "fx", "demo", "4-spec")
check(r.returncode == 0, "缺觀測欄的 spec 仍產得出來(要讓人看見問題,不是擋住)")
if r.returncode == 0:
    t = (TMP / "fx/docs/dev/demo/4-spec.html").read_text(encoding="utf-8")
    check(t.count('class="s-card bad"') == 1, "缺「觀測」欄的那條 S 渲染成紅底",
          f"紅底卡 {t.count(chr(115) + chr(45) + chr(99) + chr(97) + chr(114) + chr(100) + chr(32) + chr(98) + chr(97) + chr(100))} 張,應為 1")
    check("缺觀測欄" in t, "動線頂區點出缺幾條")

print("-- K-7 負向:缺 THEN(非觀測)也要紅底,動線改報「缺必填欄」 --")
# 模板要求 GIVEN/WHEN/THEN/觀測四欄皆必填,不是只有「觀測」——缺任何一欄都要紅底現形。
fx2 = ROOT / "scripts/fixtures/gate-twin/missing-then"
shutil.copytree(fx2, TMP / "fx2")
r = run(TMP / "fx2", "demo", "4-spec")
check(r.returncode == 0, "缺 THEN 欄的 spec 仍產得出來(要讓人看見問題,不是擋住)")
if r.returncode == 0:
    t2 = (TMP / "fx2/docs/dev/demo/4-spec.html").read_text(encoding="utf-8")
    check(t2.count('class="s-card bad"') == 1, "恰 1 張紅卡(只有 S-2 缺 THEN)",
          f"紅底卡 {t2.count(chr(115) + chr(45) + chr(99) + chr(97) + chr(114) + chr(100) + chr(32) + chr(98) + chr(97) + chr(100))} 張,應為 1")
    check("缺「THEN」欄" in t2, "html 含「缺「THEN」欄」(守衛靠這個字串現形)")
    check("缺必填欄" in t2, "動線頂區改報「缺必填欄」(這條沒缺觀測,缺的是 THEN)")
    m = re.search(r'<article class="([^"]*)" data-sid="S-1">', t2)
    check(bool(m) and "bad" not in m.group(1), "欄位齊全的 S-1 不是紅卡",
          f"實際 class=\"{m.group(1) if m else '(無)'}\"")

print("-- P5:抽驗格決定論抽樣(不是隨機、可重現)--")
# 獨立(不呼叫 build-gate-twin.py 的 table_rows)重算 Coverage Matrix 中位列 ——
# 斷言要釘在跟正本邏輯獨立的第二套實作,不是回頭呼叫同一顆函式驗自己。
def _sample_expect():
    txt = (EXAMPLE / "7-review.md").read_text(encoding="utf-8")
    m = re.search(r"^## Coverage Matrix\s*\n(.*?)(?=\n## |\Z)", txt, re.S | re.M)
    body = m.group(1) if m else ""
    rows = []
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    data_rows = rows[1:] if len(rows) > 1 else []
    if not data_rows:
        return "—"
    mid = data_rows[len(data_rows) // 2]
    val = mid[0] if mid else ""
    return (val[:14] + "…") if len(val) > 14 else (val or "—")


expect_sample = _sample_expect()
txt7 = (proj / "7-review.html").read_text(encoding="utf-8")
m = re.search(r'<span class="k">抽驗</span><span class="v">([^<]*)</span>', txt7)
actual_sample = m.group(1) if m else None
check(actual_sample is not None and "隨機一列" not in actual_sample,
      "7-review:抽驗格不是舊常數「隨機一列」", f"實際「{actual_sample}」")
check(actual_sample == expect_sample,
      "7-review:抽驗格值 = Coverage Matrix 中位列第一欄(決定論、對正本算)",
      f"實際「{actual_sample}」,預期「{expect_sample}」")

print("-- T5 負向:解析不到任何待審項目要 exit 1,不產空殼 --")
empty = TMP / "empty/docs/dev/demo"
empty.mkdir(parents=True)
(empty / "4-spec.md").write_text("# 4. 規格\n\n## 沒有任何 R 或 S\n\n隨便寫點東西。\n",
                                 encoding="utf-8")
r = run(TMP / "empty", "demo", "4-spec")
check(r.returncode == 1, "空 spec → exit 1", f"實際 exit {r.returncode}")
check(not (empty / "4-spec.html").exists(), "空 spec → 不產出空殼 html")

print("-- N7 散發副本 --")
for name in ("build-gate-twin.py", "devflow_twin_ui.py"):
    src = ROOT / "scripts" / name
    dist = ROOT / "docs/dev/tools" / name
    check(dist.is_file() and src.read_text(encoding="utf-8") == dist.read_text(encoding="utf-8"),
          f"{name}:docs/dev/tools/ 副本與正本逐字一致",
          "缺檔" if not dist.is_file() else "內容不同(正本方向:scripts/ → docs/dev/tools/)")

print("-- 用法錯誤 --")
r = subprocess.run([sys.executable, str(BUILD)], capture_output=True, text=True)
check(r.returncode == 2, "無參數 → exit 2 並印用法", f"實際 exit {r.returncode}")

print()
if FAILED:
    print(f"❌ gate twin 產生器守衛:{FAILED} 項失敗(共 {CHECKS} 項)")
    sys.exit(1)
print(f"✅ gate twin 產生器守衛:全過({CHECKS} 項)")
PY
