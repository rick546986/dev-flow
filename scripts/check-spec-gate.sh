#!/bin/bash
# G2 機械關卡 —— 對一份 4-spec.md 做**形狀**檢查(不做語意判斷)。
#
# 為什麼需要:G2 的三個條件(R/S 全審 + Drafting Decisions 全裁決 + Verification
# Profile 依 lane 正確填寫)在 2026-08-14 之前**全靠人眼**,沒有任何機械檢查。
# 兩個現場證據(notes/adoption-findings-2026-08-04.md 第三輪 B-9):
#   ①一份 4-spec 整節缺 Verification Profile,一路走到準備進 Stage 6 才被發現 ——
#     而 `lane:`/`Risk:` 正是 `devflow-exec.sh start` 會讀的欄位,缺了就開不了工。
#   ②同一份 spec 的 16 個 S 裡有 5 個缺「觀測」欄。`_templates/4-spec.md:53` 明文
#     寫著「完成 = 全 R 展開、**每 S 有觀測欄**、每段有確認」,但沒有東西在擋。
#
# 定位:**過濾器,不是審查者**。它只查「規則明文要求的欄位在不在、形狀對不對」,
# 讓 reviewer 把時間花在判斷 R/S 寫得對不對、DD 決策合不合理 —— 那些仍然是人審的事。
# 本腳本永遠不判斷內容好壞。
#
# 五項檢查(逐項印結果,全過才 exit 0):
#   C1 每個 S 都有觀測欄          _templates/4-spec.md:53(完成條件)、:99(欄位形式)
#   C2 Verification Profile 節存在,且 `- lane:` 與 `- Risk:` 可被解析
#                                 _templates/4-spec.md:181-182、:200(runtime 讀這兩行)
#   C3 lane: fast + Risk: high 且無 Owner Call 例外 → FAIL
#                                 _templates/4-spec.md:213-216(OC-4)
#   C4 模糊詞掃描                 _templates/4-spec.md:23-24(全文掃三詞)、
#                                 :49 逐 S 過三律(見 :22 第 1 條的模糊詞清單)
#   C5 Drafting Decisions 無殘留「待裁決」  _templates/4-spec.md:47(掃描零殘留)
#
# C2/C3 的 lane/Risk/Owner Call 解析**直接 import runtime 正本**
# (hooks/devflow-lib.py 的 `spec_profile()`),不另寫一份 —— G2 前置檢查與
# `devflow-exec.sh start` 的判定若漂移,就會出現「G2 過了卻 start 不了」。
#
# **exit code 契約(重要;與 scripts/check-task-slicing.sh 相反,別看混)**:
#   check-task-slicing.sh 是 warning-only,對真實檔案永遠不 exit 1。
#   **本腳本是 Gate**:FAIL 就是要擋下流程。
#     0 = 五項全過
#     1 = 任一項 FAIL —— G2 不得送審,修完再跑
#     2 = 用法錯誤 / 檔案讀不到 / runtime 正本載不進來(檢查本身故障)
#
# 用法:
#   scripts/check-spec-gate.sh <4-spec.md 路徑>

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

SPEC="${1:-}"
if [ -z "$SPEC" ]; then
  cat >&2 <<'USAGE'
usage: scripts/check-spec-gate.sh <4-spec.md 路徑>

G2 機械關卡:對一份 4-spec.md 做形狀檢查(五項,見腳本頂註)。
exit 0 = 全過 / 1 = 有 FAIL,G2 不得送審 / 2 = 用法錯誤或檢查本身故障。
USAGE
  exit 2
fi
if [ ! -f "$SPEC" ]; then
  echo "⛔ 讀不到 4-spec:$SPEC" >&2
  exit 2
fi

python3 - "$SPEC" "$ROOT" <<'PY'
import importlib.util
import os
import re
import sys

spec_path, root = sys.argv[1], sys.argv[2]

# ---- runtime 正本:lane / Risk / Owner Call 例外的解析器 ----
lib_path = os.path.join(root, "hooks", "devflow-lib.py")
try:
    loader = importlib.util.spec_from_file_location("devflow_lib", lib_path)
    L = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(L)
except Exception as exc:                                    # 檢查本身故障 → exit 2
    print(f"⛔ 載不進 runtime 正本 {lib_path}:{exc}", file=sys.stderr)
    raise SystemExit(2)

text = open(spec_path, encoding="utf-8").read()
lines = text.splitlines()

HEAD = re.compile(r"^#{2,6}\s")
S_HEAD = re.compile(r"^#{2,6}\s*S-\S+")
# 觀測欄:行首 dash + 可選 ** 粗體 + 「觀測」,同行要有冒號(半形或全形)。
# 模板寫 `- 觀測(承接…):…`,實際 spec 常寫 `- 觀測:…` 或 `- **觀測**:…`,三種都認。
# ⚠️ G3(2026-08-17):字元集曾把「:或：」打成**兩個半形冒號**(四碼全 0x3a,肉眼
# 看不出來),全形冒號寫的觀測欄被判缺欄 → 誘導使用者編造沒實跑過的觀測值。
# 現值:半形 0x3a + 全形 0xff1a。守衛 = check-regex-charclass.sh(重複半形標點掃描)
# + fixtures/spec-gate-fullwidth-colon(全形版必須通過)。
OBS = re.compile(r"^\s*-\s*\*{0,2}\s*觀測\*{0,2}[^:：\n]*[:：]")

# 三律第 1 條的模糊詞(_templates/4-spec.md:22-23)—— 範圍是「每條 S」,逐 S 掃。
VAGUE_S = ("適當", "正確", "合理", "必要時", "妥善", "robust", "視情況", "等等")
# 未定事項三詞(_templates/4-spec.md:23-24 與步驟 4 的「全文掃」)—— 全檔掃。
VAGUE_ALL = ("TBD", "之後再說", "實作再定")

heads = [i for i, l in enumerate(lines) if HEAD.match(l)]


def block_end(start):
    for h in heads:
        if h > start:
            return h
    return len(lines)


s_blocks = [(lines[i].strip(), i, block_end(i)) for i in heads if S_HEAD.match(lines[i])]

results = []          # (code, ok, 標題, [明細行])


def record(code, ok, title, detail=()):
    results.append((code, ok, title, list(detail)))


# ---- C1:每個 S 都有觀測欄 ----
if not s_blocks:
    record("C1", False, "每個 S 都有觀測欄",
           ["找不到任何 `#### S-<id>` 區塊 —— 4-spec 至少要有一條 S"])
else:
    missing = [name for name, s, e in s_blocks
               if not any(OBS.match(lines[n]) for n in range(s, e))]
    record("C1", not missing, f"每個 S 都有觀測欄(共 {len(s_blocks)} 條 S)",
           [f"{name}(L{s + 1})缺觀測欄 —— 形式見 _templates/4-spec.md:78"
            for name, s, e in s_blocks if name in missing])

# ---- C2:Verification Profile 節存在,且 lane / Risk 可解析 ----
prof = L.spec_profile(text)
has_section = any(re.match(r"^#{2,6}\s*Verification Profile", l) for l in lines)
c2_bad = []
if not has_section:
    c2_bad.append("缺整節 `## Verification Profile` —— 模板 :175")
if prof["lane"] is None:
    c2_bad.append("解析不到 `- lane: full|fast` 行(runtime start 會讀)—— 模板 :181")
if prof["risk"] is None:
    c2_bad.append("解析不到 `- Risk: normal|high` 行(runtime start 會讀)—— 模板 :182")
record("C2", not c2_bad,
       f"Verification Profile 可解析(lane={prof['lane']} / Risk={prof['risk']})", c2_bad)

# ---- C3:lane: fast + Risk: high 且無 Owner Call 例外 → FAIL ----
fast_high = prof["lane"] == "fast" and prof["risk"] == "high"
c3_ok = not (fast_high and not prof["owner_call_fast_high"])
record("C3", c3_ok, "lane/Risk 組合合法(OC-4:fast + high 需 Owner Call 例外)",
       [] if c3_ok else [
           "`lane: fast` 配 `Risk: high`,但找不到 `- Owner Call 例外:<非空理由>`",
           "模板 :213-216 —— runtime(start 時)、模板檢查與 Gate 一律拒絕;"
           "fast lane 命中 high 必須自動升 full"])

# ---- C4:模糊詞掃描 ----
hits = []
for n, line in enumerate(lines):
    for w in VAGUE_ALL:
        if w in line:
            hits.append(f"L{n + 1} 未定事項詞「{w}」:{line.strip()[:70]}"
                        f"  → 只能列入 Drafting Decisions(標待裁決)或退回提問(模板 :23-24)")
for name, s, e in s_blocks:
    for n in range(s, e):
        for w in VAGUE_S:
            if w in lines[n]:
                hits.append(f"L{n + 1} {name} 模糊詞「{w}」:{lines[n].strip()[:70]}"
                            f"  → 反模糊三律第 1 條(模板 :22-23)")
record("C4", not hits, "模糊詞掃描(全文三詞 + 逐 S 三律清單)", hits)

# ---- C5:Drafting Decisions 無殘留「待裁決」 ----
dd = next((i for i in heads if re.match(r"^#{2,6}\s*Drafting Decisions", lines[i])), None)
if dd is None:
    record("C5", True, "Drafting Decisions 無殘留「待裁決」(本檔無 DD 節 = 零殘留)")
else:
    end = block_end(dd)
    left = [f"L{n + 1}:{lines[n].strip()[:70]}"
            for n in range(dd, end) if "待裁決" in lines[n]]
    record("C5", not left,
           f"Drafting Decisions 無殘留「待裁決」(L{dd + 1} 起)",
           [*left, "G2 條件明列「DD 全裁決」;有未裁決 DD 不得過(模板 :47)"] if left else [])

# ---- 輸出 ----
print(f"=== G2 spec gate:{spec_path} ===")
failed = 0
for code, ok, title, detail in results:
    print(f"{'✅' if ok else '❌'} {code} {title}")
    for d in detail:
        print(f"     {d}")
    if not ok:
        failed += 1
print()
if failed:
    print(f"⛔ G2 spec gate:{len(results) - failed}/{len(results)} 通過,{failed} 項 FAIL "
          f"—— 修完再送審(這是 Gate,不是 warning)。")
    raise SystemExit(1)
print(f"✅ G2 spec gate:{len(results)}/{len(results)} 全過(形狀檢查;R/S 與 DD 的"
      f"內容仍須人審)。")
PY
