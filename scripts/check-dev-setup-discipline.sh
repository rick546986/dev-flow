#!/bin/bash
# dev-setup upgrade 三方比對紀律的機械檢查(Repo-local,REPO_REFERENCE only)。
#
# 起因:`skills/dev-setup/SKILL.md` 的 upgrade 段落(三方比對/baseline 快照/逐檔
# 徵同意/過渡態/master-only 剝除/gate twin 相依)全是散文規則,目前**零機械檢查**。
# 這份文檔一旦被改弱(哪怕只是改寫成看起來差不多的說明),後果是 upgrade 流程
# 靜默蓋掉使用者的本地客製 —— 與本 repo 已經記過的 A1/A3/A4/A5(見
# check-stage67-enforcement.sh 檔頭)是同一類「散文規則沒有牙齒」的問題,只是
# 發生在 dev-setup 而不是 Stage 6/7。
#
# 本檔**不**併入 check-stage67-enforcement.sh —— 那支專管 Stage 6/7 執行期模板
# 強制條款,這裡管的是 dev-setup 安裝器自己的 upgrade 紀律,職責不同(見派工裁決)。
#
# 本守衛不判斷內容好壞,只驗「SKILL.md 有沒有把這六條紀律講清楚」:
#   ①三方比對(上游舊快照/上游新/本地現況)
#   ②baseline 快照目錄 `docs/dev/.devflow-baseline/`
#   ③逐檔徵同意(本地客製覆蓋前必須單獨列出並取得同意)
#   ④過渡態(無快照但 docs/dev/ 已存在 → 全部視為客製,逐檔徵同意)
#   ⑤master-only 剝除步驟(sed 抽取 <!-- devflow:master-only:start/end --> 之間以外)
#   ⑥gate twin 相依交代(markdown-it-py==4.0.0)
#
# 用法:
#   scripts/check-dev-setup-discipline.sh [root]   # 缺省 = repo root
#
# 退出碼:0 = 全過;1 = 有 needle 缺失(逐條列出缺哪條);2 = 用法錯誤。

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  case "$1" in
    -h|--help|help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) ROOT=$(cd "$1" 2>/dev/null && pwd) || { echo "找不到 root: $1" >&2; exit 2; } ;;
  esac
fi

python3 - "$ROOT" <<'PY'
import os
import sys

root = sys.argv[1]
fails = []
checks = 0


def read(rel):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def need(cond, msg):
    """cond 為 False 即記一條失敗。每呼叫一次算一項檢查。"""
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


src = read("skills/dev-setup/SKILL.md")
need(src is not None, "skills/dev-setup/SKILL.md 不存在")

if src:
    # ── ①三方比對(上游舊快照/上游新/本地現況)────────────────────────────────
    # needle 選「判別法(三方比對)」(定義段落內的獨特字面;裸的「三方比對」四字
    # 在 install 步驟摘要句、過渡態收尾句各出現一次,子字串比對會在整段定義被刪掉
    # 後仍命中那兩處殘留引用而假綠 —— 2026-08-17 fresh 審查 B-2 抓到,見派工裁決)
    # 與「上游舊 blob」(三方之一,拿掉就只剩兩方比對,退化成猜本地現況)。
    need("判別法(三方比對)" in src,
         "SKILL.md upgrade 段沒有「判別法(三方比對)」定義 —— 少了它,本地客製與母版"
         "改寫無從分辨,upgrade 只能靠猜")
    need("上游舊 blob" in src,
         "SKILL.md 三方比對缺「上游舊 blob」這一方(baseline 快照當基準)—— "
         "沒有它,判別法退化成只比對「本地現況 vs 上游新」兩方,分不出本地是否被改過")

    # ── ②baseline 快照目錄 ──────────────────────────────────────────────────
    need("docs/dev/.devflow-baseline/" in src,
         "SKILL.md 沒寫出 baseline 快照目錄 `docs/dev/.devflow-baseline/` —— "
         "①的「上游舊 blob」沒有實際落地位置,判別法是空話")

    # ── ③逐檔徵同意(本地客製覆蓋前必須單獨列出並取得同意)────────────────────
    # needle 挑「徵得使用者明確同意」這個動作本身,不挑整句「逐檔單獨列出…」
    # (那句夠長、遣詞容易被改寫成同義句而不觸發,見任務裁決「needle 不釘會漂的長句」)。
    need("徵得使用者明確同意" in src,
         "SKILL.md upgrade 段的本地客製分類②沒有要求「徵得使用者明確同意」才可"
         "覆蓋 —— 少了這個動作,客製覆蓋前的同意變成選配")

    # ── ④過渡態(無快照但 docs/dev/ 已存在 → 全部視為客製,逐檔徵同意)────────
    need("過渡態" in src,
         "SKILL.md upgrade 段沒有「過渡態」條款 —— 本規則生效前既有安裝(無 "
         "baseline 快照但 docs/dev/ 已存在)會被誤套用「無快照=首次 install」"
         "分支,靜默蓋掉這些專案的本地客製")
    need("全部受管檔視為②本地客製,逐檔徵同意" in src,
         "SKILL.md 過渡態條款沒有把處置釘死成「全部受管檔視為②本地客製,逐檔"
         "徵同意」—— 少了這句,過渡態案例可能被自由心證併入①母版改寫直接覆蓋")

    # ── ⑤master-only 剝除步驟(sed 抽取)─────────────────────────────────────
    # needle 用實際會被複製貼上執行的 sed 指令本身(install 步 1 與 check 第 6
    # 項共用同一條管線)——拿掉這條指令,母版 README 的純 repo 導覽區塊會被
    # 原樣複製進散發專案的 docs/dev/README.md,成為死引用。
    sed_cmd = ("sed -n '/<!-- devflow:master-only:start -->/,"
               "/<!-- devflow:master-only:end -->/!p'")
    need(sed_cmd in src,
         "SKILL.md 沒有 master-only 區塊的 sed 剝除指令(install 步 1 / check 第 6 "
         "項共用管線)—— 少了它,母版 README 的 master-only 區塊會被原樣複製進"
         "採用專案,成為死引用")

    # ── ⑥gate twin 相依交代(markdown-it-py==4.0.0)──────────────────────────
    need("markdown-it-py==4.0.0" in src,
         "SKILL.md 沒交代 gate twin 產生器的相依版本 `markdown-it-py==4.0.0` —— "
         "解析層的判斷來源(CommonMark token stream)版本沒釘死,散發後可能"
         "裝到不相容版本卻無從察覺")

# ── 檢查數地板:防止有人把上面整段刪成空迴圈仍然 exit 0 ──────────────────────
# ⚠️ 這個數字必須**等於當下的實際檢查數**,不是「大概抓個下限」(同 repo 慣例:
# check-stage67-enforcement.sh:232、check-no-stale-paths.sh 的 MIN_CHECKS)。
MIN_CHECKS = 9
if checks < MIN_CHECKS:
    fails.append(f"⛔ 實際只跑了 {checks} 項檢查(地板 {MIN_CHECKS})—— "
                 f"檢查本身被刪掉或迴圈跑了零圈,這比條款失效更嚴重")

if fails:
    print(f"⛔ check-dev-setup-discipline: {len(fails)} 條失敗(共跑 {checks} 項)")
    for f in fails:
        print(f"  ❌ {f}")
    raise SystemExit(1)

print(f"✅ check-dev-setup-discipline: dev-setup upgrade 三方比對紀律齊({checks} 項檢查全過)")
print("   三方比對 / baseline 快照目錄 / 逐檔徵同意 / 過渡態 / master-only 剝除 / gate twin 相依")
PY
