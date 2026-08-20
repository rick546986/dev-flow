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
# 本守衛不判斷內容好壞,只驗「SKILL.md 有沒有把這十條紀律講清楚」:
#   ①三方比對(上游舊快照/上游新/本地現況)
#   ②baseline 快照落地段落 scoped 綁定(落地位置 + 涵蓋 docs/dev/tools/;B-5)
#   ③逐檔徵同意(本地客製覆蓋前必須單獨列出並取得同意)
#   ④過渡態(無快照但 docs/dev/ 已存在 → 全部視為客製,逐檔徵同意)
#   ⑤master-only 剝除步驟(sed 抽取 <!-- devflow:master-only:start/end --> 之間以外)
#   ⑥gate twin 相依交代(markdown-it-py==4.0.0)
#   ⑦mkdir -p docs/dev/tools 在第一支工具 cp 之前(fresh install 不炸;A-2)
#   ⑧baseline 落地在步 7 最後一項驗證之後(不拍未驗證/未散發完的樹;A-2)
#   ⑨upgrade 的 baseline 來源綁 upstream-new 正本,禁抄 docs/dev/ 現況(A-2)
#   ⑩check 段的散發副本 parity 取自檔案地圖散發面標註(不得逐支硬列)、涵蓋
#     history-append.sh、且交代 contract 副本要單獨驗(2026-08-20 實際漏驗)
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

    # ── ②baseline 快照:落地段落 scoped 綁定(A-2/B-5,2026-08-18)─────────────
    # 舊版只驗「docs/dev/.devflow-baseline/」出現在全文任一處 —— baseline 段被改回
    # 舊版三項列舉(漏 docs/dev/tools/)時,同一字串在過渡態等段落仍在,照樣假綠
    # (第 4 型)。改成:先切出 install 收尾步的落地段落,needle 必須在段落內命中。
    i_install = src.find("## install")
    i_upgrade = src.find("## upgrade")
    need(0 <= i_install < i_upgrade,
         "SKILL.md 找不到 install/upgrade 兩節(或順序異常)—— 後續 scoped 檢查無從定位")
    install_sec = src[i_install:i_upgrade] if 0 <= i_install < i_upgrade else ""

    i_landing = install_sec.find("基準快照落地")
    landing = install_sec[i_landing:] if i_landing >= 0 else ""
    need("docs/dev/.devflow-baseline/" in landing,
         "install 收尾步的「基準快照落地」段落不存在、或段落內沒寫落地位置 "
         "`docs/dev/.devflow-baseline/` —— ①的「上游舊 blob」沒有實際落地位置,"
         "判別法是空話")
    need("docs/dev/tools/" in landing,
         "baseline 落地段落內沒有「docs/dev/tools/」—— 段落被改回舊版三項列舉的話,"
         "官方工具永遠不進 baseline,下次 upgrade 會把它們誤判成本地客製(B-5)")

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

    # ── ⑦mkdir 在第一支工具 cp 之前(A-2 fresh install 故障,字元位置比)────────
    i_mkdir = install_sec.find("mkdir -p docs/dev/tools")
    i_first_tool = install_sec.find("docs/dev/tools/history-append.sh")
    need(0 <= i_mkdir < i_first_tool,
         "install 節裡 `mkdir -p docs/dev/tools` 沒有出現在第一支工具"
         "(history-append.sh)散發之前 —— 照文件順序 fresh install,parent 目錄"
         "還沒建,步 1 三支工具的 cp 會直接失敗")

    # ── ⑧baseline 落地在最後一支工具的最後一項驗證之後(A-2 時序)─────────────
    # 步 7 的最後一項驗證 needle =「可執行位元一致」;落地段落的字元位置必須在它
    # 之後 —— 只驗「在最後一次 cp/chmod 後」不夠:插在 chmod 與驗證之間,
    # 驗證失敗時快照已經被污染。
    i_last_verify = install_sec.find("可執行位元一致")
    need(i_landing >= 0 and 0 <= i_last_verify < i_landing,
         "baseline 落地段落沒有出現在步 7 最後一項驗證(正副本可執行位元一致)"
         "之後 —— 拍在驗證前,驗證失敗時快照已被污染;拍在步 6、7 前更會把"
         "官方工具誤判成本地客製")

    # ── ⑨upgrade 的 baseline 來源綁定 upstream-new(A-2,scoped)───────────────
    upg_sec = src[i_upgrade:src.find("## refresh")] if i_upgrade >= 0 else ""
    i_src_para = upg_sec.find("上游舊 blob 的來源")
    i_transition = upg_sec.find("過渡態")
    src_para = upg_sec[i_src_para:i_transition] if 0 <= i_src_para < i_transition else ""
    need("這次覆蓋下去的上游新內容" in src_para,
         "upgrade 的「上游舊 blob 的來源」段落沒有把快照來源綁定在"
         "「這次覆蓋下去的上游新內容」(upstream-new 正本)—— 來源不明,"
         "三方比對的基準就可以被換成任何東西")
    need("現況直接抄成 baseline" in src_para,
         "upgrade 的來源段落少了「不准把可能已被本地改過的 docs/dev/ 現況直接抄成"
         " baseline」禁令 —— 抄現況會把本地客製記成「上游舊」,下次三方比對就"
         "分不出誰改的")

    # ── ⑩check 段的散發副本 parity 必須 map-driven,不得逐支硬列(2026-08-20)──
    # 起因:check 第 9/11/12 項逐支硬列了四支散發工具,而 history-append.sh 有散發
    # 卻從來沒被任何一項驗過。母版側的 parity 守衛
    # (check-integration-regression-guard.sh ④)早就因為「寫死五個 diff -q,新增
    # 第六支必漏驗」改成掃檔案地圖散發面標註了,採用專案側卻還停在硬列 —— 同一條
    # 不變量在兩側記帳不對稱(第 7 型)。現場實例:健檢者手打清單只點到三支,
    # 實際散發五支,而漏掉的正是 HISTORY.md 的唯一寫入口。
    i_check = src.find("## check")
    i_fix = src.find("## fix / uninstall")
    chk_sec = src[i_check:i_fix] if 0 <= i_check < i_fix else ""
    need("散發面:docs/dev/tools/" in chk_sec,
         "check 段沒有把散發副本 parity 的比對集合綁定在檔案地圖的"
         "「散發面:docs/dev/tools/」標註 —— 退回逐支硬列的話,下一支新散發工具"
         "必定漏驗(母版側已因同一理由改成 map-driven)")
    need("history-append.sh" in chk_sec,
         "check 段完全沒提 history-append.sh —— 它是 HISTORY.md 的唯一寫入口,"
         "副本過期或掉執行位元就寫不進去,而 G1 的巢狀路徑 bug 正是出在這支裡;"
         "散發了卻沒有任何一項健檢驗它(2026-08-20 實際漏過)")
    need("散發面標註涵蓋不到" in chk_sec,
         "check 段沒交代 devflow-contract.json 不住在 docs/dev/tools/、散發面標註"
         "涵蓋不到它、必須單獨驗 —— 併進 parity 總表就沒有人在驗 contract 副本"
         "(同 dev-release 步 2 把那行 diff -q 單獨留著的理由)")

# ── 檢查數地板:防止有人把上面整段刪成空迴圈仍然 exit 0 ──────────────────────
# ⚠️ 這個數字必須**等於當下的實際檢查數**,不是「大概抓個下限」(同 repo 慣例:
# check-stage67-enforcement.sh:232、check-no-stale-paths.sh 的 MIN_CHECKS)。
MIN_CHECKS = 18
if checks < MIN_CHECKS:
    fails.append(f"⛔ 實際只跑了 {checks} 項檢查(地板 {MIN_CHECKS})—— "
                 f"檢查本身被刪掉或迴圈跑了零圈,這比條款失效更嚴重")

if fails:
    print(f"⛔ check-dev-setup-discipline: {len(fails)} 條失敗(共跑 {checks} 項)")
    for f in fails:
        print(f"  ❌ {f}")
    raise SystemExit(1)

print(f"✅ check-dev-setup-discipline: dev-setup upgrade 三方比對紀律齊({checks} 項檢查全過)")
print("   三方比對 / baseline 落地段落 scoped / 逐檔徵同意 / 過渡態 / master-only 剝除"
      " / gate twin 相依 / mkdir 先於工具 cp / 落地在驗證後 / upgrade 來源綁 upstream-new"
      " / check 段散發副本 parity map-driven")
PY
