#!/bin/bash
# check-regex-charclass.sh — 全形半形打字陷阱掃描(G3 通解,2026-08-17)。
#
# 抓什麼:scripts/ 與 hooks/ 原始碼裡,方括號字元集內**相鄰重複的半形標點**
# (`[::]`、`[;;]`、`[,,]`、`[((]`…)。那是「本想寫『半形或全形』卻兩個都打成
# 半形」的機械徵象 —— 全形 `：`(0xff1a)與半形 `:`(0x3a)肉眼幾乎不可分,
# 寫的人本意是對的,看的人也看不出錯。
#
# 為什麼需要:2026-08-17 採用專案實踩 —— check-spec-gate C1 的 `[::]` 四碼全是
# 半形,全形冒號寫的觀測欄被判「缺欄」,誘導使用者編造沒實跑過的觀測值;同型
# 盤查一共 6 處,其中 2 處在 runtime(devflow-lib Owner Call 例外、_stage3 人類
# 確認)。單修那 6 處只是治標:下次再寫一個 `[::]` 又會重演,所以要這支通解。
#
# 邊界(誠實宣告):
#   - 只認「相鄰」重複:`[:x:]` 這種隔開的重複不在本掃描宣稱能擋的範圍
#     (現實中打錯全形的形態都是成對相鄰,如「:或：」寫成「::」)。
#   - 只掃**看起來帶正則的行**(re.compile/match/search/split/findall/finditer/
#     sub/fullmatch、grep -E、sed、awk、bash =~)裡**引號字串內**的字元集 ——
#     省略號 `[...]`、list comprehension 的 `))`、用法說明文字全都不是正則,
#     掃寬會淹在誤報裡(第一版實測 41 處誤報 vs 0 真命中)。
#   - POSIX 字元類(`[[:space:]]`/`[[:alpha:]]`)先剝除再掃,不誤報;
#     被 `\` 跳脫的 `\[` 不當字元集開頭。
#
# exit code:0 = 無命中;1 = 有命中(列出 檔:行 與該行內容);2 = 自檢失敗或掃到
# 0 檔(fail-closed:掃描器自己壞了不得偽裝成「沒有缺陷」)。

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

python3 - "$ROOT" <<'PY'
import glob
import os
import re
import sys

root = sys.argv[1]

# 監看的半形標點(各有全形攣生字):冒號 分號 逗號 句點 驚嘆 問號 括號
PUNCT = ":;,.!?()"
# 帶正則的行:python re 呼叫 / grep -E 族 / sed / awk / bash =~
REGEX_LINE = re.compile(
    r"re\.(?:compile|match|search|split|findall|finditer|sub|fullmatch)\s*\("
    r"|grep\s+-\w*E\b|\bsed\b|\bawk\b|=~")
# 引號字串(雙引號含跳脫;單引號不含跳脫,shell 語意)
QUOTED = re.compile(r'"(?:\\.|[^"\\\n])*"' + r"|'(?:\\.|[^'\\\n])*'")
POSIX_CLASS = re.compile(r"\[:\^?[a-z]+:\]")           # [:space:] / [:alpha:] …
BRACKET = re.compile(r"(?<!\\)\[(?:\\.|[^\]\\\n])*\]")  # 未跳脫的 [...] 字元集
ADJ_DUP = re.compile("(" + "|".join(re.escape(c) + "{2}" for c in PUNCT) + ")")


def scan_text(text):
    """回傳 [(行號, 該行內容, 命中片段)]。

    三層漏斗:①行要像帶正則(**本行或上一行**命中 —— 審查抓到跨行寫法
    `re.compile(\\n    r"[…]")` 的 pattern 字串在下一行,單行過濾看不見;
    兩行窗涵蓋最常見的跨一行排版,拆更多行仍是明文邊界)②只看引號字串內
    ③剝 POSIX 類與跳脫後,字元集內找相鄰重複半形標點。"""
    hits = []
    prev = ""
    for lineno, line in enumerate(text.splitlines(), 1):
        if REGEX_LINE.search(line) or REGEX_LINE.search(prev):
            for q in QUOTED.finditer(line):
                segment = POSIX_CLASS.sub("", q.group(0))
                for m in BRACKET.finditer(segment):
                    dup = ADJ_DUP.search(m.group(0))
                    if dup:
                        hits.append((lineno, line.strip()[:90], dup.group(1)))
        prev = line
    return hits


# ── 自檢:偵測器對已知毒樣本必須命中、對合法樣本必須放行 ──────────────────
# 毒樣本用串接組出,避免本檔自己出現字面 `[::]` 被自己掃到。
poison = "OBS = re.compile(r\"觀測[" + "::" + "]\")"          # 兩個半形冒號
poison2 = "ln = re.split(r\"[,。" + ";;" + "]\", ln)"          # 兩個半形分號
poison3 = "OBS = re.compile(\n    r\"觀測[" + "::" + "]\")"   # 跨行排版(審查 MED 抓到的盲區)
legit = 'OBS = re.compile(r"觀測[:：]")'                       # 半形+全形(正確寫法)
legit2 = 'if re.search(r"[[:space:]]+", s):'                   # POSIX 類(不得誤報)
legit3 = "arr=${list[@]:0:2}"                                  # bash 切片(無相鄰重複)
ok = (bool(scan_text(poison)) and bool(scan_text(poison2)) and bool(scan_text(poison3))
      and not scan_text(legit) and not scan_text(legit2) and not scan_text(legit3))
if not ok:
    print("FATAL: 掃描器自檢失敗 —— 偵測邏輯退化,本次結果不可信", file=sys.stderr)
    sys.exit(2)

# ── 掃描 scripts/ 與 hooks/ 的 .sh 與 .py ────────────────────────────────
targets = sorted(
    p for pat in ("scripts/*.sh", "scripts/*.py", "hooks/*.sh", "hooks/*.py")
    for p in glob.glob(os.path.join(root, pat)))
if len(targets) < 10:                 # 兩目錄現有 40+ 檔;掃到個位數 = 來源被縮小
    print(f"FATAL: 只掃到 {len(targets)} 檔 —— 掃描來源被縮小,不是「沒有缺陷」",
          file=sys.stderr)
    sys.exit(2)

all_hits = []
for path in targets:
    rel = os.path.relpath(path, root)
    try:
        with open(path, encoding="utf-8") as stream:
            text = stream.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"FATAL: 讀不到 {rel}:{exc}", file=sys.stderr)
        sys.exit(2)
    for lineno, line, frag in scan_text(text):
        all_hits.append((rel, lineno, line, frag))

print(f"=== 全形半形打字陷阱掃描:{len(targets)} 檔(scripts/ hooks/ 的 .sh/.py)===")
if all_hits:
    print(f"❌ 字元集內相鄰重複半形標點 {len(all_hits)} 處 —— 多半是「本想寫全形」打錯:")
    for rel, lineno, line, frag in all_hits:
        print(f"   {rel}:{lineno}  重複「{frag}」  {line}")
    print("   修法:把其中一個改成對應全形字(如「:或：」寫成 [:：]);"
          "真的要重複半形(理論上不存在)則需改寫使其不相鄰並在該行註明理由。")
    sys.exit(1)
print("✅ 無命中(自檢通過:毒樣本可偵測、POSIX 類與正確寫法不誤報)")
PY
