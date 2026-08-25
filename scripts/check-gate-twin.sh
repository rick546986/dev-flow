#!/bin/bash
# gate twin 產生器守衛(Repo-local)。驗的是**規格有沒有真的被實作**,不是 html 好不好看。
#
# 規格正本:README §6〈審查動線頂區〉+ `_templates/{2-decision,4-spec}.md` 頂註。
# 三件必含,少一件那份 twin 就不是審查介面:
#   T1 動線頂區**五格**(格數固定,內容依 stage)
#   T2 待審項目逐條可勾 + 進度計數;**缺必填欄的項目要在卡上直接紅底現形**
#   T3 背景資料收進 <details>(預設收合、內容零刪減)
# 外加兩條產生器自身的契約:
#   T4 **預設只寫本機完整文件**:`{stage}.html` 必須是完整 html;預設不得產出
#      `{stage}-review.artifact.html`。設了 DEVFLOW_ARTIFACT_OUT 才寫片段,且
#      片段**不得含** doctype/html/head/body(發布時外層會自動包)。
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

DEVFLOW_ROOT="$ROOT" DEVFLOW_TMP="$TMP" python3 - "$0" <<'PY'
import ast
import hashlib
import html
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from markdown_it import MarkdownIt  # N-1 第 2 層:直接吃 repo 已釘的相依,不繞正則
except ImportError:
    # 本檔檔頭文件寫「exit:2 = 環境問題」——相依缺失正是這一類,不該讓它變成
    # 沒攔到的 ImportError traceback(那樣 rc 由 python 決定,不保證是 2)。
    print("缺相依 markdown-it-py:請跑 pip install 'markdown-it-py==4.0.0'", file=sys.stderr)
    sys.exit(2)

SELF_PATH = sys.argv[1] if len(sys.argv) > 1 else ""  # 供 guard-selfpin 群組自我核對用

ROOT = Path(os.environ["DEVFLOW_ROOT"])
TMP = Path(os.environ["DEVFLOW_TMP"])
BUILD = ROOT / "scripts/build-gate-twin.py"
EXAMPLE = ROOT / "example/contract-expiry-reminder"
STAGES = ("2-decision", "4-spec", "7-review", "5-tasks")
# 完整文件外殼的判準:片段裡出現這些就是把外殼寫進片段了(<header> 不算,故要求後接空白或 >)
SHELL = re.compile(r"<!doctype|<html[\s>]|<head[\s>]|<body[\s>]", re.I)

FAILED = 0
CHECKS = 0

# ── N-2:分節心跳(照 check-design-contract.sh 的既有寫法)────────────────────
# 檢查數地板只能偵測「大幅縮水」,抓不到「整區塊被刪、但別的區塊剛好補上檢查數」。
# 逐區塊斷言「這一區至少跑過一條」,任何區塊被整段刪掉都會顯性失敗、點名是哪一區。
REQUIRED_GROUPS = [
    "gate-stage-baseline",
    "dash-cells-readme",
    "risk-cell-count",
    "cross-file-parity",
    "p4-fence-section",
    "s-head-regression",
    "h2-zero-deletion",
    "t6-pinned",
    "t2-missing-required",
    "k7-missing-then",
    "k3-missing-intent",
    "k3-empty-tasks",
    "k3-task-count",
    "k3-boundaries-dag",
    "high2-dash-values",
    "high3-dag-waves",
    "high1-dup-field",
    "p5-sample-row",
    "t5-empty-spec",
    "n7-dist-copy",
    "n1-section-fate",
    "n4-unclosed-comment",
    "usage-error-message",
    "spec-review-shape",
    "decision-review-shape",
    "tasks-review-shape",
    "g3-review-shape",
    "guard-selfpin",
]
# 群組數的釘死常數(比照 MIN_CHECKS 的做法)——REQUIRED_GROUPS 被連刪帶藏
#(區塊本體 + 清單條目一起刪、再補等量填充檢查湊數)時,heartbeat 與 guard-selfpin
# 兩層都看不到缺口(兩者都只驗「清單裡列的東西有沒有跑」,清單本身縮水不影響它們),
# 只有這個獨立釘死的數字會現形。逐次同步成 REQUIRED_GROUPS 的實際長度,不是抓下限
#(理由同上方 MIN_CHECKS 說明)。這個字面值另外被 test-architecture-guards.sh 的
# GS-9 靜態互釘釘了一份,兩處要一起改。
EXPECTED_GROUPS = 28
CURRENT_GROUP = "gate-stage-baseline"
GROUPS_SEEN = {}
# 檢查數地板(次級 backstop):**釘死的常數**,不是跑完再回頭算 —— 回頭算等於
# 地板永遠等於實得數,刪掉整區塊也不會低於它,等同沒有牙齒。這個數字必須等於
# 「執行到這條地板斷言當下、除了它自己以外」的實得檢查數(地板斷言呼叫時,它自己
# 尚未計入 CHECKS,所以比對值天生就是「扣掉自己」那個值,見下方 check() 呼叫處)——
# 逐次同步成當下實測值,不是某一輪的固定數字,也不是留餘裕的下限。
# ⚠️ 2026-08-16 獨立審查 finding 4b:舊值 127 對實得 128 留了 1 檢查的鬆弛
#(刪 1 條檢查、實得掉到 127 仍 `>= 127` 通過),等於地板沒有真的釘死當下實況。
# 這個數字必須**逐次同步成實得數**,不是「大概抓個下限」——多留一點餘裕就是
# 少一分防禦,跟本檔 REQUIRED_GROUPS/EXPECTED_ALLOWLIST_LEN 這類地板同一個道理。
# 之後每加一條檢查都要把這裡同步調高;只有整區塊被砍掉、實得數掉到這個值以下
# 才會紅(這是本檔唯一的次級防線,見 test-architecture-guards.sh 的 GS-9 靜態互釘
# ——那邊另外釘了這個數字的字面值,兩處要一起改,見該檔的防禦邊界說明)。
MIN_CHECKS = 176


def check(cond, label, detail=""):
    global FAILED, CHECKS
    CHECKS += 1
    GROUPS_SEEN[CURRENT_GROUP] = GROUPS_SEEN.get(CURRENT_GROUP, 0) + 1
    if cond:
        print(f"  ✓ {label}")
    else:
        FAILED += 1
        print(f"  ✗ {label}" + (f" — {detail}" if detail else ""))


def run(root, slug, stage, extra_env=None):
    # 預設路徑必須在「沒有 DEVFLOW_ARTIFACT_OUT」下跑,否則本守衛自己的環境
    # 若剛好帶了這個變數,T4 的 sidecar-absent 斷言會被外部環境汙染。
    env = os.environ.copy()
    env.pop("DEVFLOW_ARTIFACT_OUT", None)
    if extra_env:
        env.update(extra_env)
    return subprocess.run([sys.executable, str(BUILD), str(root), slug, stage],
                          capture_output=True, text=True, env=env)


def read_html_or_none(path):
    """安全讀 twin 產出的 html。檔案不存在(通常是前面某個 stage 的 build 已經
    失敗、或本檔上游有回歸)→ 回 None,呼叫端據此讓該組斷言 check(False, ...) 標紅
    並跳過,不讓 .read_text() 的 FileNotFoundError 把整支守衛炸掉、後面 90+ 項
    全部跑不到(MED,2026-08-15 獨立審查:TASK_LEVEL 2→3 這類回歸曾讓本檔中途
    traceback 中斷,連帶讓真正該報的紅燈都沒機會印出來)。"""
    return path.read_text(encoding="utf-8") if path.is_file() else None


print("-- 三個 gate stage + 5-tasks 執行板對母版範例實跑(自帶回歸)--")
CURRENT_GROUP = "gate-stage-baseline"
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
    sidecar = proj / f"{st}-review.artifact.html"
    # 寫成活條件(而非硬寫 True)——雖然走到這裡當下必為真(上面已經
    # `if r.returncode != 0: ...continue` 濾掉),但硬寫 True 會被下面新加的
    # guard-selfpin「不得出現 check(True」自我掃描誤判成斷言被恆真化解除武裝。
    check(r.returncode == 0, f"{st}:產出成功")
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
    check(bool(SHELL.search(local)) and not sidecar.exists(),
          "  T4 預設只寫完整本機版、不寫 sidecar artifact",
          "寫了 sidecar" if sidecar.exists() else "本機版缺外殼")

# T4 opt-in:明確設定 DEVFLOW_ARTIFACT_OUT 才寫片段,且片段仍不得含外殼
# (舊 T4 片段半邊)。留在同一群組,避免動 EXPECTED_GROUPS / 群組名靜態釘。
art_out = TMP / "optin-art" / "4-spec-review.artifact.html"
r_art = run(TMP / "proj", "demo", "4-spec",
            extra_env={"DEVFLOW_ARTIFACT_OUT": str(art_out)})
art_txt = art_out.read_text(encoding="utf-8") if art_out.is_file() else ""
check(r_art.returncode == 0 and art_out.is_file() and not SHELL.search(art_txt)
      and not (proj / "4-spec-review.artifact.html").exists(),
      "T4 opt-in:DEVFLOW_ARTIFACT_OUT 寫出無外殼片段、且不寫預設 sidecar",
      ("片段含 doctype/html/head/body" if SHELL.search(art_txt) else
       "沒寫到 DEVFLOW_ARTIFACT_OUT" if not art_out.is_file() else
       "寫了預設 sidecar" if (proj / "4-spec-review.artifact.html").exists() else
       f"exit {r_art.returncode}"))

print("-- T8 五格內容對齊 README §6 規格 --")
CURRENT_GROUP = "dash-cells-readme"
# 規格正本:README §6〈審查動線頂區〉的三列表。格數對了但內容答非所問 = 沒做到
# (2026-08-15 獨立審查 H5:三站的格子內容當時與同一份 diff 新增的規格全不符)。
# ⚠️ 標籤集合**從 README §6 的表格解析**,不硬寫在本檔。
# 硬寫 = 斷言釘在副本而不是正本:改 README 的規格文字,守衛照樣全綠
#(2026-08-15 複審缺口 G;與 H2「守衛只驗字串在不在」是同一類病)。
def readme_keys():
    txt = (ROOT / "README.md").read_text(encoding="utf-8")
    out = {}
    for st in STAGES:
        # 5-tasks 是執行板不是 gate,標籤是「(執行板)」不是「(G\d)」——K-3 擴充,
        # 兩種都要吃得到,不然改回只認 `(G\d)` 這條守衛對 5-tasks 就是形同虛設。
        m = re.search(r"^\|\s*\*\*" + re.escape(st) + r"\((?:G\d|執行板)\)\*\*\s*\|(.+?)\|\s*$",
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

# F5(2026-08-17,上輪 G′ 缺口):readme_keys() 在第一個括號截斷 —— 標籤守住了,
# 括號內的規格語意沒有(`狀態(frontmatter)` 改成 `狀態(frontmatter)X` 曾全綠)。
# 這裡把 §6 四列的**五格全文**(含括號)hash 釘死:改 README 的規格文字必須同
# commit 更新快照,漂移從「靜默」變「顯性」。快照不是第二正本,只是讓改動變吵
# —— 與 EXPECTED_CHECK_SKIP_CALLS、selftest MIN_CASES 同一手法。
PINNED_ROW_SHA = {
    "2-decision": "71dbe8e98e5a786b",
    "4-spec": "9fd6eced73b59343",
    "7-review": "bef9dfc2ddea381c",
    "5-tasks": "d780503d05ac8c0a",
}
_readme_txt = (ROOT / "README.md").read_text(encoding="utf-8")
for st in STAGES:
    _m = re.search(r"^\|\s*\*\*" + re.escape(st) + r"\((?:G\d|執行板)\)\*\*\s*\|(.+?)\|\s*$",
                   _readme_txt, re.M)
    _got = hashlib.sha256(_m.group(1).strip().encode()).hexdigest()[:16] if _m else "(缺列)"
    check(_got == PINNED_ROW_SHA[st],
          f"{st}:README §6 五格全文(含括號規格語意)與釘死快照一致",
          f"hash {_got} ≠ 釘死 {PINNED_ROW_SHA[st]} —— 改了 §6 規格文字要同 commit "
          f"更新本快照;現值:{_m.group(1).strip()[:80] if _m else '列不見了'}")
for st in STAGES:
    txt = read_html_or_none(proj / f"{st}.html")
    if txt is None:
        check(False, f"{st}:五格標籤與 README §6 逐字一致", f"{st}.html 不存在(前面已失敗)")
        continue
    keys = set(re.findall(r'class="cell"[^>]*><span class="k">([^<]+)</span>', txt))
    # ⚠️ 兩處都要用 `.get(st, set())`,不能直接 `EXPECT_KEYS[st]` —— check() 的參數在
    # 呼叫前就會全部求值,cond 是 False 不代表 detail 字串不會被算,README §6 缺列
    # 5-tasks 那一列時 `EXPECT_KEYS[st]` 會 KeyError 中斷整支守衛(MED,2026-08-15
    # 獨立審查實測:「刪 README §6 的 5-tasks 列」就是這個 crash)。
    check(keys == EXPECT_KEYS.get(st, set()), f"{st}:五格標籤與 README §6 逐字一致",
          f"多 {sorted(keys - EXPECT_KEYS.get(st, set()))} / 少 {sorted(EXPECT_KEYS.get(st, set()) - keys)}")

print("-- 盤點:7-review 動線「風險」格條數要對得上 md 的 Known Limits 實際條數 --")
CURRENT_GROUP = "risk-cell-count"
# 舊計數把表頭列與 |---| 分隔列都算進去(4 條報成 6)。守衛自己從 example md
# 數一次「資料列 + bullet 列」,斷言釘在正本,不釘在產生器的輸出邏輯上。
def _limit_rows(md_text):
    lines, in_sec = [], False
    for ln in md_text.splitlines():
        if re.match(r"^##\s+Known Limits", ln):
            in_sec = True
            continue
        if in_sec and re.match(r"^##\s+", ln):
            break
        if in_sec:
            lines.append(ln)
    pipe = [x for x in lines if x.lstrip().startswith("|")]
    sep = [x for x in pipe
           if all(re.fullmatch(r":?-{2,}:?", c) for c in x.strip().strip("|").split("|") if c.strip())]
    data = max(0, len(pipe) - len(sep) - (1 if pipe else 0))
    bullets = len([x for x in lines if re.match(r"^\s*[-*]\s+\S", x)])
    return data + bullets


_exp_kl = _limit_rows((EXAMPLE / "7-review.md").read_text(encoding="utf-8"))
_kl_txt = read_html_or_none(proj / "7-review.html")
if _kl_txt is None:
    check(False, "7-review:「風險」格條數 == md 實際條數(表頭/分隔列不算)",
          "7-review.html 不存在(前面已失敗)")
else:
    _m_kl = re.search(r'<span class="k">風險</span><span class="v">([^<]*)</span>', _kl_txt)
    check(bool(_m_kl) and _m_kl.group(1) == f"{_exp_kl} 條",
          "7-review:「風險」格條數 == md 實際條數(表頭/分隔列不算)",
          f"格值「{_m_kl.group(1) if _m_kl else '(無)'}」,md 實數 {_exp_kl}")

print("-- G\u2032/G\u2033 跨檔規格一致:README §6 vs 三份模板頂註 --")
CURRENT_GROUP = "cross-file-parity"
# N4 的根因:規格同時寫在 README §6 與三份模板頂註,兩邊不一致時沒有任何檢查。
# 把模板改回舊值 → 必須紅(2026-08-15 二次複審 G\u2033)。
TPL = {"2-decision": "_templates/2-decision.md", "4-spec": "_templates/4-spec.md",
       "7-review": "_templates/7-review.md", "5-tasks": "_templates/5-tasks.md"}


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
CURRENT_GROUP = "p4-fence-section"
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
CURRENT_GROUP = "s-head-regression"
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
CURRENT_GROUP = "h2-zero-deletion"
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
CURRENT_GROUP = "t6-pinned"
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

# finding 2(LOW,獨立審查):上面的斷言只驗「幾個關鍵字沒被摺疊」,PINNED_PAT
# 誤吞多餘章節(桶位變寬鬆、把不該置頂的節也置頂)完全沒有守衛。這裡對母版範例
# 三站(不是上面這份合成 fixture)釘死「置頂節 id 的精確集合」——從真正產出的
# html 撈 `<section class="pinned" id="...">` 的 id,逐一比對下面這份釘死清單。
# ⚠️ 這份清單是「當下實況」的字面快照,不是規格本身 —— PINNED_PAT 有意變更
#(新增/刪除關鍵字)時,必須同步改這裡的期望值,否則這條檢查會擋下正常修改,
# 而不是它原本要防的「誤吞/桶位擴大」。
EXPECT_PINNED_IDS = {
    "2-decision": {"sec-Decision"},
    "4-spec": set(),
    "7-review": {"sec-Verdict", "sec-Known-Limits"},
}
for _st in ("2-decision", "4-spec", "7-review"):
    _html_pin = read_html_or_none(proj / f"{_st}.html")
    if _html_pin is None:
        check(False, f"{_st}:置頂節 id 精確集合與釘死清單一致", f"{_st}.html 不存在(前面已失敗)")
        continue
    _actual_ids = set(re.findall(r'<section class="pinned" id="([^"]+)"', _html_pin))
    _expect_ids = EXPECT_PINNED_IDS[_st]
    check(_actual_ids == _expect_ids,
          f"{_st}:置頂節 id 精確集合與釘死清單一致(PINNED_PAT 誤吞/桶位擴大都要現形)",
          f"多 {sorted(_actual_ids - _expect_ids)} / 少 {sorted(_expect_ids - _actual_ids)}")

print("-- T2 負向:缺必填欄要在卡上紅底現形 --")
CURRENT_GROUP = "t2-missing-required"
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
CURRENT_GROUP = "k7-missing-then"
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

print("-- K-3 負向:5-tasks 缺 Intent 要在卡上紅底現形,其餘 T 不受牽連 --")
CURRENT_GROUP = "k3-missing-intent"
fxt = ROOT / "scripts/fixtures/gate-twin/tasks-missing-intent"
shutil.copytree(fxt, TMP / "fxt")
r = run(TMP / "fxt", "demo", "5-tasks")
check(r.returncode == 0, "缺 Intent 的 5-tasks 仍產得出來(要讓人看見問題,不是擋住)")
if r.returncode == 0:
    tt = (TMP / "fxt/docs/dev/demo/5-tasks.html").read_text(encoding="utf-8")
    check(tt.count('class="s-card bad"') == 1, "缺 Intent 的那個 T 恰渲染成 1 張紅卡",
          f"紅底卡 {tt.count('s-card bad')} 張,應為 1")
    check("缺「Intent」欄" in tt, "html 含「缺「Intent」欄」(守衛靠這個字串現形)")
    m = re.search(r'<article class="([^"]*)" data-sid="T-1">', tt)
    check(bool(m) and "bad" not in m.group(1), "欄位齊全的 T-1 不是紅卡",
          f"實際 class=\"{m.group(1) if m else '(無)'}\"")

print("-- K-3 負向:5-tasks 找不到任何 T → exit 1,不產空殼 --")
CURRENT_GROUP = "k3-empty-tasks"
empty_t = TMP / "empty-t/docs/dev/demo"
empty_t.mkdir(parents=True)
(empty_t / "5-tasks.md").write_text(
    "# 5. 任務\n\n## Split Decisions(拆分自判,選配)\n\n沒有任何 T,隨便寫點東西。\n",
    encoding="utf-8")
r = run(TMP / "empty-t", "demo", "5-tasks")
check(r.returncode == 1, "空 5-tasks(無任何 T) → exit 1", f"實際 exit {r.returncode}")
check(not (empty_t / "5-tasks.html").exists(), "空 5-tasks → 不產出空殼 html")

print("-- K-3 盤點:example 5-tasks 的 T 數 == twin 卡數 --")
CURRENT_GROUP = "k3-task-count"
_ex_5tasks_md = (EXAMPLE / "5-tasks.md").read_text(encoding="utf-8")
n_t_source = len(re.findall(r"^## T-\d+", _ex_5tasks_md, re.M))
tasks_local = read_html_or_none(proj / "5-tasks.html")
if tasks_local is None:
    check(False, "example/contract-expiry-reminder/5-tasks.md 的 `## T-` 數 == twin 卡數",
          "5-tasks.html 不存在(前面已失敗)")
    n_t_twin = 0
else:
    n_t_twin = len(re.findall(r'<article class="s-card[^"]*" data-sid="T-\d+"', tasks_local))
    check(n_t_source > 0 and n_t_source == n_t_twin,
          "example/contract-expiry-reminder/5-tasks.md 的 `## T-` 數 == twin 卡數",
          f"md {n_t_source} 個 T,twin {n_t_twin} 張卡")

print("-- K-3:5-tasks 的 Boundaries 摺疊 + #dag 都在,五格標籤與 README 一致(自帶回歸)--")
CURRENT_GROUP = "k3-boundaries-dag"
if tasks_local is None:
    check(False, "每張 T 卡都有 Boundaries 摺疊(<details class=\"t-bound\">)", "5-tasks.html 不存在(前面已失敗)")
    check(False, "T 依賴 DAG 區塊(#dag)存在", "5-tasks.html 不存在(前面已失敗)")
    check(False, "DAG 至少印出第一波", "5-tasks.html 不存在(前面已失敗)")
else:
    # ⚠️ 先落成變數再進 f-string:Python 3.11 及更早不允許 f-string 的表達式部分
    # 含反斜線(這裡是 \" 轉義)。守衛:scripts/check-py-floor.sh
    n_bound = tasks_local.count('class="t-bound"')
    check(n_bound == n_t_twin,
          "每張 T 卡都有 Boundaries 摺疊(<details class=\"t-bound\">)",
          f"details 數 {n_bound},卡數 {n_t_twin}")
    check('id="dag"' in tasks_local, "T 依賴 DAG 區塊(#dag)存在")
    check("Wave 1" in tasks_local, "DAG 至少印出第一波")

print("-- HIGH-2:5-tasks 執行板五格值盤點斷言(期望值釘 example md 正本,不硬寫)--")
CURRENT_GROUP = "high2-dash-values"
# 審查者實測:硬寫死一個值(例如「99 條」)這種斷言現在不會紅,因為根本沒有斷言
# 去驗五格的**值**(只驗格數、標籤)。這裡補的斷言全部由守衛自己從 example md 算,
# 不硬寫任何數字/字串常數,釘的是「twin 值 == md 正本算出來的值」這個關係。
def _tasks_dash_expected(md_text):
    """獨立算 5-tasks 執行板五格期望值,直接從 example md 正本算(不 import 產生器)。"""
    ids = re.findall(r"^##\s+(T-\d+)\b", md_text, re.M)
    idset = set(ids)
    edges = 0
    for m in re.finditer(r"^##\s+T-\d+\b.*?(?=^##\s|\Z)", md_text, re.M | re.S):
        bm = re.search(r"^\s*-\s*Blocked-by\s*:\s*(.*)$", m.group(0), re.M)
        val = bm.group(1).strip() if bm else ""
        if val in ("", "—", "-", "－", "無"):
            continue
        edges += len([r for r in re.findall(r"T-\d+", val) if r in idset])
    fm_m = re.match(r"\A---\n(.*?)\n---\n", md_text, re.S)
    fm_text = fm_m.group(1) if fm_m else ""
    mode_m = re.search(r"^\s*mode:\s*(\S+)", fm_text, re.M)
    mode = mode_m.group(1) if mode_m else "sequential"
    return len(ids), edges, mode


_exp_n_t, _exp_edges, _exp_mode = _tasks_dash_expected(_ex_5tasks_md)
if tasks_local is None:
    for _label in ("5-tasks:「任務」格數 == md `## T-` 數(盤點,不得硬寫)",
                   "5-tasks:「依賴」格數 == md 所有 Blocked-by 合法 T-id 引用總數(盤點)",
                   "5-tasks:「模式」格 == frontmatter execution.mode(未標=sequential)",
                   "5-tasks:「進度」格分母 == T 數"):
        check(False, _label, "5-tasks.html 不存在(前面已失敗)")
else:
    _m_task = re.search(r'<span class="k">任務</span><span class="v">([^<]*)</span>', tasks_local)
    check(bool(_m_task) and _m_task.group(1) == f"{_exp_n_t} 個 T",
          "5-tasks:「任務」格數 == md `## T-` 數(盤點,不得硬寫)",
          f"格值「{_m_task.group(1) if _m_task else '(無)'}」,md 實數 {_exp_n_t} 個 T")
    _m_dep = re.search(r'<span class="k">依賴</span><span class="v">([^<]*)</span>', tasks_local)
    check(bool(_m_dep) and _m_dep.group(1) == f"{_exp_edges} 條",
          "5-tasks:「依賴」格數 == md 所有 Blocked-by 合法 T-id 引用總數(盤點)",
          f"格值「{_m_dep.group(1) if _m_dep else '(無)'}」,md 實數 {_exp_edges} 條")
    _m_mode = re.search(r'<span class="k">模式</span><span class="v">([^<]*)</span>', tasks_local)
    check(bool(_m_mode) and _m_mode.group(1) == _exp_mode,
          "5-tasks:「模式」格 == frontmatter execution.mode(未標=sequential)",
          f"格值「{_m_mode.group(1) if _m_mode else '(無)'}」,預期「{_exp_mode}」")
    _m_prog = re.search(r'<span class="k">進度</span><span class="v">([^<]*)</span>', tasks_local)
    _prog_denom = _m_prog.group(1).split("/")[-1] if _m_prog else None
    check(_prog_denom == str(_exp_n_t),
          "5-tasks:「進度」格分母 == T 數",
          f"格值「{_m_prog.group(1) if _m_prog else '(無)'}」,預期分母 {_exp_n_t}")

print("-- HIGH-3:5-tasks DAG 分波正確性(guard 自己寫 Kahn,不 import 產生器)--")
CURRENT_GROUP = "high3-dag-waves"
def _expected_waves(md_text):
    """獨立實作拓撲分波(Kahn),從 md 正本的 Blocked-by 算 —— 刻意不 import
    build-gate-twin.py 的任何函式:斷言要釘在跟正本邏輯獨立的第二套實作,不然
    產生器和守衛用同一顆函式錯,兩邊會一起錯還一起綠(審查者的破壞法「DAG 全塞
    Wave 1」必須被這裡的獨立計算抓到)。"""
    ids = re.findall(r"^##\s+(T-\d+)\b", md_text, re.M)
    idset = set(ids)
    deps = {}
    for m in re.finditer(r"^##\s+(T-\d+)\b.*?(?=^##\s|\Z)", md_text, re.M | re.S):
        tid = m.group(1)
        bm = re.search(r"^\s*-\s*Blocked-by\s*:\s*(.*)$", m.group(0), re.M)
        val = bm.group(1).strip() if bm else ""
        refs = [] if val in ("", "—", "-", "－", "無") else \
            [r for r in re.findall(r"T-\d+", val) if r in idset and r != tid]
        deps[tid] = refs
    remaining = {t: list(deps[t]) for t in ids}
    resolved, wave_of, wave_no = set(), {}, 0
    while remaining:
        wave_no += 1
        wave = [t for t in ids if t in remaining and all(d in resolved for d in remaining[t])]
        if not wave:
            break  # 環;example md 目前無環,這裡只求不要無限迴圈
        for t in wave:
            wave_of[t] = wave_no
        for t in wave:
            del remaining[t]
        resolved |= set(wave)
    return deps, wave_of


def _actual_waves(dag_text):
    """解析 twin 印出的 `Wave N: T-x ←(...)、T-y` 這種行,回 {tid: wave_no}。
    只取每個逗號分隔項**最前面**的 T id(← 後面括號內是依賴來源、不是它自己的波次)。"""
    actual = {}
    for line in dag_text.splitlines():
        m = re.match(r"Wave (\d+): (.*)$", line.strip())
        if not m:
            continue
        wn = int(m.group(1))
        for entry in m.group(2).split("、"):
            tm = re.match(r"(T-\d+)", entry.strip())
            if tm:
                actual[tm.group(1)] = wn
    return actual


_exp_deps, _exp_wave_of = _expected_waves(_ex_5tasks_md)
if tasks_local is None:
    check(False, "5-tasks:DAG 分波 —— 有依賴的 T 不得在 Wave 1", "5-tasks.html 不存在(前面已失敗)")
    check(False, "5-tasks:DAG 分波 —— 逐 T 波次與獨立 Kahn 實作相等", "5-tasks.html 不存在(前面已失敗)")
else:
    _dag_sec_m = re.search(r'<section class="dag"[^>]*>.*?</section>', tasks_local, re.S)
    _dag_sec = _dag_sec_m.group(0) if _dag_sec_m else ""
    _dag_pre_m = re.search(r"<pre>(.*?)</pre>", _dag_sec, re.S)
    _dag_text = _dag_pre_m.group(1) if _dag_pre_m else ""
    _actual_wave_of = _actual_waves(_dag_text)
    _bad_wave1 = sorted(t for t in _exp_deps if _exp_deps[t] and _actual_wave_of.get(t) == 1)
    check(not _bad_wave1, "5-tasks:DAG 分波 —— 有依賴的 T 不得在 Wave 1",
          f"錯誤落在 Wave 1 的 T(有 Blocked-by 卻在第一波):{_bad_wave1}")
    check(_actual_wave_of == _exp_wave_of, "5-tasks:DAG 分波 —— 逐 T 波次與獨立 Kahn 實作相等",
          f"實際 {_actual_wave_of},預期(獨立算){_exp_wave_of}")

print("-- HIGH-1 負向:同一 T 內重複保留欄 → 紅卡 + flag 含「重複」;"
      "fence 內 `## T-99` → 引擎不長出(釘引擎行為)、twin 卡數不含它 --")
CURRENT_GROUP = "high1-dup-field"
fxd = ROOT / "scripts/fixtures/gate-twin/tasks-dup-field"
shutil.copytree(fxd, TMP / "fxd")
r = run(TMP / "fxd", "demo", "5-tasks")
check(r.returncode == 0, "重複欄 + fence 幽靈任務 fixture 仍產得出來(現形不擋產出)")
if r.returncode == 0:
    td = (TMP / "fxd/docs/dev/demo/5-tasks.html").read_text(encoding="utf-8")
    check(td.count('class="s-card bad"') == 1, "恰 1 張紅卡(重複欄的 T-1)",
          f"紅底卡 {td.count('s-card bad')} 張,應為 1")
    m_t1 = re.search(r'<article class="([^"]*)" data-sid="T-1">(.*?)</article>', td, re.S)
    check(bool(m_t1) and "bad" in m_t1.group(1), "T-1(重複 Files 欄)是紅卡")
    check(bool(m_t1) and "重複" in m_t1.group(2) and "Files" in m_t1.group(2),
          "T-1 卡的 flag 文字含「重複」與欄名 Files")
    m_t2 = re.search(r'<article class="([^"]*)" data-sid="T-2">', td)
    check(bool(m_t2) and "bad" not in m_t2.group(1), "T-2(fence canary 宿主)本身欄位齊全,不是紅卡")
    all_sids = re.findall(r'data-sid="([^"]+)"', td)
    check("T-99" not in all_sids, "T-99(fence 內的假標題)沒有變成卡片", f"卡片 sid 清單:{sorted(set(all_sids))}")
    check("重複保留欄" in (r.stderr or ""),
          "stderr NOTE 引用 contract_ref 的「重複保留欄」用語(訊息一致,便於對照)",
          (r.stderr or "").strip())
    # R-2/S-2.1:前提已消失(引擎 hooks/devflow-lib.py::parse_5_tasks 現在會遮蔽
    # fence,T-1 已修)—— twin 不再宣稱「引擎目前不遮蔽 fence…幽靈任務」這個過期
    # 事實。斷言改釘在引擎正本的實際行為:直接載入 hooks/devflow-lib.py,對同一份
    # fixture 跑 parse_5_tasks,斷言 tasks 不含 T-99。不斷言 errors 全空 ——
    # 這份 fixture 本身還有 T-1 的重複 Files 欄(非 fence 內容,H-1 回歸的一部分,
    # 上面那條「重複保留欄」斷言驗的就是它),那條 error 本該在,不是本條要驗的
    # 行為;這裡只額外斷言 errors 裡沒有任何提到 T-99 的訊息(fence 沒有洩漏進 errors)。
    _engine_spec = importlib.util.spec_from_file_location(
        "devflow_lib_selfcheck", str(ROOT / "hooks/devflow-lib.py"))
    _engine_mod = importlib.util.module_from_spec(_engine_spec)
    _engine_spec.loader.exec_module(_engine_mod)
    _engine_md = (fxd / "docs/dev/demo/5-tasks.md").read_text(encoding="utf-8")
    _engine_result = _engine_mod.parse_5_tasks(_engine_md)
    _engine_ids = [t["id"] for t in _engine_result["tasks"]]
    check("T-99" not in _engine_ids,
          "引擎(hooks/devflow-lib.py::parse_5_tasks)對同輸入不長出 T-99"
          "(fence 已遮蔽,R-2/S-2.1)",
          f"引擎解析到的 task id:{_engine_ids}")
    check(not any("T-99" in e for e in _engine_result["errors"]),
          "引擎 errors 不含任何提到 T-99 的訊息(fence 內容沒有洩漏進 errors)",
          f"errors:{_engine_result['errors']}")

print("-- P5:抽驗格決定論抽樣(不是隨機、可重現)--")
CURRENT_GROUP = "p5-sample-row"
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
txt7 = read_html_or_none(proj / "7-review.html")
if txt7 is None:
    check(False, "7-review:抽驗格不是舊常數「隨機一列」", "7-review.html 不存在(前面已失敗)")
    check(False, "7-review:抽驗格值 = Coverage Matrix 中位列第一欄(決定論、對正本算)",
          "7-review.html 不存在(前面已失敗)")
else:
    m = re.search(r'<span class="k">抽驗</span><span class="v">([^<]*)</span>', txt7)
    actual_sample = m.group(1) if m else None
    check(actual_sample is not None and "隨機一列" not in actual_sample,
          "7-review:抽驗格不是舊常數「隨機一列」", f"實際「{actual_sample}」")
    check(actual_sample == expect_sample,
          "7-review:抽驗格值 = Coverage Matrix 中位列第一欄(決定論、對正本算)",
          f"實際「{actual_sample}」,預期「{expect_sample}」")

print("-- T5 負向:解析不到任何待審項目要 exit 1,不產空殼 --")
CURRENT_GROUP = "t5-empty-spec"
empty = TMP / "empty/docs/dev/demo"
empty.mkdir(parents=True)
(empty / "4-spec.md").write_text("# 4. 規格\n\n## 沒有任何 R 或 S\n\n隨便寫點東西。\n",
                                 encoding="utf-8")
r = run(TMP / "empty", "demo", "4-spec")
check(r.returncode == 1, "空 spec → exit 1", f"實際 exit {r.returncode}")
check(not (empty / "4-spec.html").exists(), "空 spec → 不產出空殼 html")

print("-- N7 散發副本 --")
CURRENT_GROUP = "n7-dist-copy"
for name in ("build-gate-twin.py", "devflow_twin_ui.py"):
    src = ROOT / "scripts" / name
    dist = ROOT / "docs/dev/tools" / name
    check(dist.is_file() and src.read_text(encoding="utf-8") == dist.read_text(encoding="utf-8"),
          f"{name}:docs/dev/tools/ 副本與正本逐字一致",
          "缺檔" if not dist.is_file() else "內容不同(正本方向:scripts/ → docs/dev/tools/)")

print("-- N-1 第 2 層:通用章節下落對帳(獨立來源,防第 1 層自己被改壞)--")
CURRENT_GROUP = "n1-section-fate"
# 對母版範例**三站**(不是只跑合成 fixture):守衛自己用 markdown-it 數 L2 ATX 標題
#(token 層,fence 內不算),斷言 (a) 自算節數 == 產生器盤點 NOTE 的 N,
# (b) 逐節標題文字要出現在 html 的置頂 h2 / details summary / r-block,或出現在
# stderr 的 dropped NOTE —— 四者皆無就是消失,列出消失的節名。
# 刻意不 import build-gate-twin.py 的 sections()/H_ANY —— 兩層若共用同一套切法,
# 同一個 bug(例如 appendix 迴圈裡加一條 continue)就會兩邊一起錯還一起綠,
# 這正是 N-1 要防的「第 1 層自己被改壞」。


def l2_atx_titles(md_text):
    """獨立算:level-2 ATX 標題的原始標題文字(fence 內的假標題天生不會被
    markdown-it 判成 heading,不必再遮蔽一次)。"""
    lines = md_text.splitlines(keepends=True)
    out = []
    for tok in MarkdownIt("commonmark").parse(md_text):
        if tok.type != "heading_open" or not tok.map or int(tok.tag[1:]) != 2:
            continue
        i = tok.map[0]
        m = re.match(r"^##[ \t]+([^\n]*?)[ \t]*$", lines[i])
        if m:
            out.append(m.group(1))
    return out


def note_list(stderr_text, prefix):
    """把 stderr 裡『NOTE: <prefix>:[...]』那一行的 Python list-repr 解析回標題清單,
    找不到或解析失敗就回 []。"""
    m = re.search(re.escape(prefix) + r":(\[.*\])\s*$", stderr_text, re.M)
    if not m:
        return []
    try:
        return list(ast.literal_eval(m.group(1)))
    except (ValueError, SyntaxError):
        return []


def l2_sections_with_body(md_text):
    """獨立算 L2 章節與其本文(含子標題,直到下一個 level<=2 標題或檔尾為止)。

    不 import 產生器的 sections() —— 只切 L2 邊界,已足夠判斷「這節底下直接
    含哪些子孫標題」(finding 1 的 heads_here 判準只需要這個粒度)。"""
    lines = md_text.splitlines(keepends=True)
    line_start = [0] * (len(lines) + 1)
    for i, ln in enumerate(lines):
        line_start[i + 1] = line_start[i] + len(ln)
    heads = []
    for tok in MarkdownIt("commonmark").parse(md_text):
        if tok.type != "heading_open" or not tok.markup.startswith("#") or not tok.map:
            continue
        lvl = int(tok.tag[1:])
        if not (2 <= lvl <= 6):
            continue
        i = tok.map[0]
        m = re.match(r"^(#{2,6})[ \t]+([^\n]*?)[ \t]*$", lines[i])
        if not m:
            continue
        heads.append((lvl, m.group(2), line_start[i], line_start[i] + m.end()))
    out = []
    for idx, (lvl, title, _line_off, body_start) in enumerate(heads):
        if lvl != 2:
            continue
        end = len(md_text)
        for nxt_lvl, _t, nxt_line_off, _b in heads[idx + 1:]:
            if nxt_lvl <= 2:
                end = nxt_line_off
                break
        out.append((title, md_text[body_start:end]))
    return out


def _mask_fenced_indep(md_text):
    """獨立版 mask_fenced —— 不 import 產生器那份,語意相同:fenced code 換等長
    空白,判準來源同樣是 markdown-it 的 fence token(不是手刻正則)。"""
    lines = md_text.splitlines(keepends=True)
    fence_lines = set()
    for tok in MarkdownIt("commonmark").parse(md_text):
        if tok.type == "fence" and tok.map:
            fence_lines.update(range(tok.map[0], tok.map[1]))

    def blank(ln):
        return (" " * (len(ln) - 1) + "\n") if ln.endswith("\n") else " " * len(ln)

    return "".join(blank(ln) if i in fence_lines else ln for i, ln in enumerate(lines))


_R_HEAD_INDEP = re.compile(r"^#{2,6}[ \t]*(R-\d+)[ \t]*[:：·]?[ \t]*(.*)$", re.M)


def independent_droppable_l2(md_text, rendered_rids):
    """MED,獨立審查 finding 1:獨立重算「哪些 L2 節合法可 drop」。

    判準與產生器(build-gate-twin.py :1023-1029)**同語意**:該節本身不是 R 標題、
    本文非空、且本文底下直接就是**全部**已渲染 R 的標題行(heads_here 是
    rendered_rids 的 superset)。刻意不 import 產生器的 sections()/mask_fenced()/
    R_HEAD/rendered_rids 算法 —— 兩層若共用同一顆函式,產生器那行單字元 `>=`
    被手滑改成 `<=` 這種 bug 會兩邊一起錯還一起綠,守衛就形同虛設。這裡也刻意
    不信產生器 stderr 印的 dropped 清單字面 —— 舊版第 2 層(修這個 finding 前)
    正是把那份自報清單直接當真相用,產生器自己算錯,舊版斷言照樣通過,3 節被
    真的丟掉卻印假 NOTE 也偵測不到。
    """
    rendered = set(rendered_rids)
    if not rendered:
        return set()
    result = set()
    for title, body in l2_sections_with_body(md_text):
        if _R_HEAD_INDEP.match("## " + title):
            continue  # 節本身就是 R 標題,不是「父節」
        if not body.strip():
            continue  # 空節走 dropped_empty 這條路,不算這裡的 superset 判準
        masked = _mask_fenced_indep(body)
        heads_here = {m.group(1) for m in _R_HEAD_INDEP.finditer(masked)}
        if heads_here >= rendered:
            result.add(title)
    return result


# ⚠️ 刻意只跑三個 gate 站,**不要**直接改成 `for st in STAGES`(把 5-tasks 也塞進來)——
# 5-tasks 的 T 卡渲染走 `<span class="s-title">`(在 `data-sid="T-n"` 的 article 裡),
# 不是這裡認的 `r-name`/pinned h2/details summary 這三種殼,會讓所有 T 節誤判成
# 「消失」(假紅)。5-tasks 若要接進第 2 層,需要另外加一條 s-title/data-sid 的
# 抽取路徑,不在本輪範圍內(N-1 設計檔本身也只講「母版範例三站」)。
#
# ⚠️ 逐節比對用 `html.escape(title)` 而非產生器的 `inline()`(後者會把反引號轉
# `<code>`、`**粗體**` 轉 `<strong>`)——三站母版範例目前的 L2 標題都是純文字,
# 兩者結果剛好相同;哪天標題真的含反引號或粗體,這裡會誤報「消失」,到時候要嘛
# 補一份獨立的 inline 轉換(不能直接 import 產生器的 inline,道理同上),要嘛
# 放寬成子字串比對(但子字串比對本身就是本 repo 假綠型態②的溫床,取捨要謹慎)。
for st in ("2-decision", "4-spec", "7-review"):  # 母版範例三站,不是合成 fixture
    r = run(TMP / "proj", "demo", st)
    md_text = re.sub(r"\A---\n.*?\n---\n", "", (EXAMPLE / f"{st}.md").read_text(encoding="utf-8"),
                     flags=re.S)
    titles = l2_atx_titles(md_text)
    m_n = re.search(
        r"NOTE: 盤點 L2 共 (\d+) 節 = 卡片節 (\d+) \+ 置頂 (\d+) \+ 背景 (\d+) \+ dropped (\d+)",
        r.stderr or "")
    check(bool(m_n) and int(m_n.group(1)) == len(titles),
          f"{st}:守衛獨立數出的 L2 節數 == 產生器盤點 NOTE 的 N",
          f"守衛獨立數 {len(titles)},產生器 NOTE「{m_n.group(1) if m_n else '(無)'}」")
    # 只驗 N 對不對還不夠 —— N 是對 secs() 的原始節數,不受任何 continue 影響;
    # 真正會被「加一條 continue 卻忘了記帳」打破的是四個分項加總。這裡額外驗
    # 卡片+置頂+背景+dropped 這四個數字本身相加要等於 NOTE 宣稱的 N,
    # 不只是字面比對總數(2026-08-15 三次複審:層 1 被自己的盤點檢查恆過蒙混時,
    # 實測 NOTE 印出「共 13 節 = 卡片 0 + 置頂 0 + 背景 11 + dropped 1」,0+0+11+1=12≠13,
    # 這條斷言就是專門釘這種「N 沒錯、但拆解加總對不上」的破綻)。
    if m_n:
        _n, _a, _b, _c, _d = (int(x) for x in m_n.groups())
        check(_a + _b + _c + _d == _n,
              f"{st}:NOTE 拆解的四個分項相加 == 總節數 N(算式本身要一致,不只驗總數字面)",
              f"卡片 {_a} + 置頂 {_b} + 背景 {_c} + dropped {_d} = {_a + _b + _c + _d},"
              f"NOTE 宣稱 N={_n}")
    else:
        check(False, f"{st}:NOTE 拆解的四個分項相加 == 總節數 N", "NOTE 格式解析失敗,無法比對")
    html_local = read_html_or_none(proj / f"{st}.html")
    if html_local is None:
        check(False, f"{st}:每個 L2 章節都能在 html/NOTE 找到下落", "html 不存在(前面已失敗)")
        continue
    pinned_h2 = set(re.findall(r'<section class="pinned"[^>]*><h2>(.*?)</h2>', html_local, re.S))
    detail_summary = set(re.findall(
        r'<details class="doc"[^>]*><summary><span>(.*?)</span></summary>', html_local, re.S))
    r_names = set(re.findall(r'<span class="r-name">(.*?)</span>', html_local, re.S))
    dropped_notes = (
        set(note_list(r.stderr or "", "以下父節的內容已整段渲染成卡片,不重複顯示"))
        | set(note_list(r.stderr or "", "以下章節本文為空,視為 dropped(空),不進背景資料")))
    missing = [t for t in titles
               if html.escape(t) not in pinned_h2 and html.escape(t) not in detail_summary
               and html.escape(t) not in r_names and t not in dropped_notes]
    check(not missing, f"{st}:每個 L2 章節都能在 html/NOTE 找到下落(第 2 層,獨立於產生器)",
          f"消失的章節:{missing}")
    # ⚠️ X-1 補注(fresh 審查者第 9 輪):下面 gen_dropped / gen_dropped_empty 這兩條
    # 斷言比對用的字面前綴,跟緊接在本區塊之前那份 dropped_notes 白名單建構時用的
    # 字面前綴是同一組;兩者若被拆開改到不同步,措辭繞過白名單比對時,由上面那條
    # 「missing」斷言兜底抓到「找不到下落」。重構這段時不得把白名單 / missing 斷言 /
    # gen_dropped 斷言三者拆散到不同函式或不同 stage 分支,拆散會讓其中一段失去
    # 另一段的兜底(行號會漂,故不寫死,以「上面/緊接在本區塊之前」相對描述)。
    # finding 1(MED,獨立審查判「不對稱保護」推廣至三站):上面的「missing」斷言
    # 只驗『每節都有下落』,但下落若是「產生器聲稱 dropped」而產生器自己算錯,
    # 第 2 層直接信那份自報清單,兩層一起綠、章節被真的丟掉卻印假 NOTE。這裡不信
    # 自報清單,對「cards-dropped」與「空節 dropped」兩種 NOTE 都獨立重算,雙向
    # 比對(多報或少報都要紅)—— 舊版只對 4-spec 做,是本檔第三次「修法只套觸發
    # 實例」的病灶(見任務書 X-1),故三站都要跑,不能只跑觸發破壞實驗的那一站。
    #
    # cards-dropped 三站語意不同,分開處理:
    #   4-spec 有 R/S 兩層結構 —— `## ADDED Requirements` 這種父節,節本身不是 R
    #   標題,但底下直接就是**全部**已渲染 R 的標題(heads_here ⊇ rendered_rids),
    #   這是產生器合法的「父節整段被渲染成卡片,不重複顯示」路徑
    #   (build-gate-twin.py :1027),故用 independent_droppable_l2() 依同語意重算、
    #   雙向比對。
    #   2-decision/7-review 沒有這層結構(S-n 卡片不是靠「父節 = 全部子卡標題」
    #   的方式渲染),而且 build-gate-twin.py :1027 那行 `dropped.append(title)`
    #   本身就用 `if stage == "4-spec" and ...` 包住 —— 這兩站的產生器**沒有任何
    #   分支**會走到那個 append。既然合法路徑不存在,能斷言得比 4-spec 更嚴:自報
    #   清單必須是空集合,一旦非空,不是產生器被改壞(誤開了一條不該有的合法路
    #   徑),就是有人手動偽造下落,兩者都該現形。
    gen_dropped = set(note_list(r.stderr or "", "以下父節的內容已整段渲染成卡片,不重複顯示"))
    if st == "4-spec":
        rendered_rids_indep = set(re.findall(
            r'<section class="r-block" id="(R-\d+)"', html_local))
        indep_dropped = independent_droppable_l2(md_text, rendered_rids_indep)
        check(gen_dropped == indep_dropped,
              f"{st}:產生器 NOTE 的 dropped 清單 == 守衛獨立重算的可 drop 集合"
              "(雙向:多 drop 或少 drop 都紅)",
              f"產生器 dropped={sorted(gen_dropped)},守衛獨立算={sorted(indep_dropped)}"
              f" —— 產生器多算(可能誤丟真章節){sorted(gen_dropped - indep_dropped)} /"
              f" 產生器少算(該丟沒丟,可能重複顯示){sorted(indep_dropped - gen_dropped)}")
    else:
        check(gen_dropped == set(),
              f"{st}:此站產生器沒有任何合法 cards-drop 路徑,dropped 清單必須是空集合",
              f"出現「{sorted(gen_dropped)}」—— build-gate-twin.py 的 dropped.append 只在"
              ' stage=="4-spec" 分支內,出現此 NOTE = 產生器被改壞或有人偽造下落')

    # 同型破口(finding 1 延伸,任務書第 4 點):「以下章節本文為空,視為 dropped
    # (空)」這份自報清單,三站都從來沒人獨立重算過 —— 跟 cards-dropped 同一個
    # 道理:自報清單不可信,才需要第 2 層。此路徑三站語意相同(空節判準不分
    # stage,build-gate-twin.py :1005 的 `if not body.strip()` 沒有 stage 條件),
    # 故三站共用同一套獨立重算,不像 cards-dropped 要分岔。
    # 判準:從 md_text 用 l2_sections_with_body() 抓出本文為空的 L2 節,排除已在
    # html 別處出現的標題(pinned_h2/detail_summary/r_names)—— 這是在鏡射產生器
    # :1003『title in used → continue』的先行判斷,已經有下落的節不會走到「空
    # 節」這條路,若不排除,已被其他路徑合法吸收的節會被誤判成「該是空節 dropped
    # 卻沒被標記」的少報假紅。
    gen_dropped_empty = set(note_list(
        r.stderr or "", "以下章節本文為空,視為 dropped(空),不進背景資料"))
    indep_dropped_empty = {
        title for title, body in l2_sections_with_body(md_text)
        if not body.strip()
        and html.escape(title) not in pinned_h2
        and html.escape(title) not in detail_summary
        and html.escape(title) not in r_names
    }
    check(gen_dropped_empty == indep_dropped_empty,
          f"{st}:產生器 NOTE 的『空節 dropped』清單 == 守衛獨立重算的空節集合"
          "(雙向:多報或少報都紅)",
          f"產生器 dropped_empty={sorted(gen_dropped_empty)},"
          f"守衛獨立算={sorted(indep_dropped_empty)}"
          f" —— 產生器多報(可能誤丟非空章節){sorted(gen_dropped_empty - indep_dropped_empty)} /"
          f" 產生器少報(該標記沒標記,可能重複顯示或消失)"
          f"{sorted(indep_dropped_empty - gen_dropped_empty)}")

print("-- N-4:未閉合的 <!-- html 註解要有警告且指出行號 --")
CURRENT_GROUP = "n4-unclosed-comment"
shutil.copytree(ROOT / "scripts/fixtures/gate-twin/unclosed-html-comment", TMP / "uhc")
r = run(TMP / "uhc", "demo", "4-spec")
check(r.returncode == 0, "未閉合 <!-- 的 fixture 仍產得出來(現形不擋產出)",
      f"實際 exit {r.returncode}")
check("未閉合" in (r.stderr or "") and "<!--" in (r.stderr or ""),
      "stderr 警告未閉合的 <!-- html 註解", (r.stderr or "").strip())
_m_line = re.search(r"從第\s*(\d+)\s*行起", r.stderr or "")
check(bool(_m_line) and _m_line.group(1) == "17",
      "警告指出正確的起始行號(原始檔行號,含 frontmatter;fixture 的 <!-- 在第 17 行)",
      f"實際「{_m_line.group(1) if _m_line else '(無)'}」")

print("-- 用法錯誤(驗訊息內容,不是只驗 rc)--")
CURRENT_GROUP = "usage-error-message"
r = subprocess.run([sys.executable, str(BUILD)], capture_output=True, text=True)
check(r.returncode == 2, "無參數 → exit 2", f"實際 exit {r.returncode}")
err = r.stderr or ""
check(err.startswith("用法:"), "訊息以「用法:」開頭(與「缺相依」前綴可區分,不共用同一句話)",
      f"實際開頭:{err[:24]!r}")
check(all(st in err for st in STAGES), "訊息含四個 stage 名", f"缺:{[s for s in STAGES if s not in err]}")
check("<專案根目錄> <slug> <stage>" in err, "訊息含參數順序 <專案根目錄> <slug> <stage>",
      f"實際:{err.strip()!r}")
# 用法錯誤與相依失敗共用同一個 exit code(2),光看 rc 分不出是哪一種 —— 訊息前綴才是
# 唯一能區分的線索。相依失敗這條路徑在有 markdown-it-py 的環境裡跑不到(無法在不
# 破壞環境的前提下真的觸發),改驗原始碼裡那句訊息的前綴仍是「缺相依」而非「用法:」,
# 確保兩種錯誤的訊息前綴不會被改成一樣。
_build_src = BUILD.read_text(encoding="utf-8")
check('缺相依 markdown-it-py' in _build_src,
      "原始碼:相依失敗訊息前綴仍是「缺相依」(與「用法:」可區分)",
      "原始碼裡找不到「缺相依 markdown-it-py」這句前綴")

print("-- 4-spec 審查卡形狀:作業脈絡在 R、S 是問題+GWT+觀測、禁止 claim --")
CURRENT_GROUP = "spec-review-shape"
# 人要能只看 HTML 審每一條 S。兩種退回舊形狀都要紅:
#   (1) 又長出複寫 GWT 的 claim /「這一點在說什麼」
#   (2) 作業脈絡又貼回每一張 S(R 上合併一次才是樣張)
_spec4 = read_html_or_none(proj / "4-spec.html")
if _spec4 is None:
    for _lab in (
        "4-spec:不得出現複寫 GWT 的 claim /「這一點在說什麼」",
        "4-spec:作業脈絡在 R 上,不在每張 S 裡",
        "4-spec:每張 S 有 2–3 條「你要審什麼」(問題,不重述 GWT)",
        "4-spec:S 仍有 GWT + 觀測",
        "4-spec:R 寫不適用時是一行,不是空表",
        "2/5/7:卡本體沒被加進 4-spec 的審題/作業脈絡",
    ):
        check(False, _lab, "4-spec.html 不存在(前面已失敗)")
else:
    _s_cards = re.findall(r'<article class="s-card.*?</article>', _spec4, re.S)
    _r_blocks = re.findall(r'<section class="r-block".*?</section>', _spec4, re.S)
    _claim_hit = re.search(
        r"這一點在說什麼|class=\"claim\"|class=\"s-claim\"|s-claim", _spec4)
    check(not _claim_hit,
          "4-spec:不得出現複寫 GWT 的 claim /「這一點在說什麼」",
          f"命中 {_claim_hit.group(0) if _claim_hit else ''}")
    _oc_in_s = [re.search(r'data-sid="([^"]+)"', c).group(1)
                for c in _s_cards
                if 'class="r-oc"' in c or "作業脈絡" in c
                or re.search(r"Actor:|誰在用", c)]
    check(not _oc_in_s,
          "4-spec:作業脈絡在 R 上,不在每張 S 裡",
          f"S 卡內出現作業脈絡:{_oc_in_s}")
    check(all('class="r-oc"' in r for r in _r_blocks) and len(_r_blocks) >= 1,
          "4-spec:每張 R 有一份作業脈絡(合併一次)",
          f"{sum('class=\"r-oc\"' in r for r in _r_blocks)}/{len(_r_blocks)} 張 R 有 r-oc")
    _ask_ok = True
    _ask_detail = []
    for c in _s_cards:
        sid_m = re.search(r'data-sid="([^"]+)"', c)
        sid = sid_m.group(1) if sid_m else "?"
        qs = re.findall(
            r'<li><span class="qmark">\?</span><span>(.*?)</span></li>', c, re.S)
        qs_txt = [re.sub(r"<[^>]+>", "", q) for q in qs]
        gwt = re.findall(r'<span class="gwt-v">(.*?)</span>', c, re.S)
        gwt_txt = [re.sub(r"<[^>]+>", "", v) for v in gwt]
        if not (2 <= len(qs) <= 3):
            _ask_ok = False
            _ask_detail.append(f"{sid} 問題數 {len(qs)}")
            continue
        if any("？" not in q and "?" not in q for q in qs_txt):
            _ask_ok = False
            _ask_detail.append(f"{sid} 有不是問題的條目")
        if any(g and len(g) >= 8 and any(g in q for q in qs_txt) for g in gwt_txt):
            _ask_ok = False
            _ask_detail.append(f"{sid} 問題重述 GWT")
        if "你要審什麼" not in c:
            _ask_ok = False
            _ask_detail.append(f"{sid} 缺「你要審什麼」")
    check(_ask_ok and len(_s_cards) >= 1,
          "4-spec:每張 S 有 2–3 條「你要審什麼」(問題,不重述 GWT)",
          "; ".join(_ask_detail) or "沒有 S 卡")
    check(all('<span class="gwt-k">GIVEN</span>' in c
              and '<span class="gwt-k">WHEN</span>' in c
              and '<span class="gwt-k">THEN</span>' in c
              for c in _s_cards) and any('class="obs"' in c for c in _s_cards),
          "4-spec:S 仍有 GWT + 觀測",
          "GWT 或觀測欄被抽掉")
    _r2 = next((r for r in _r_blocks if 'id="R-2"' in r), "")
    check(bool(_r2) and 'class="r-oc-na"' in _r2 and "不適用" in _r2
          and 'class="r-oc-row"' not in _r2,
          "4-spec:R 寫不適用時是一行,不是空表",
          "R-2 沒有 r-oc-na 一行,或仍長出空列")
    _delta_n = sum("這條才變的" in c for c in _s_cards)
    check(0 < _delta_n < len(_s_cards),
          "4-spec:「這條才變的」只補有差的 S,不是每張都貼",
          f"{_delta_n}/{len(_s_cards)} 張有 delta")
    _other_ok = True
    _other_detail = []
    for _st in ("2-decision", "7-review", "5-tasks"):
        _oh = read_html_or_none(proj / f"{_st}.html")
        if _oh is None:
            _other_ok = False
            _other_detail.append(f"{_st}.html 不存在")
            continue
        # 4-spec 專用 class 仍不得漏進另三站。<style> 分站接:2-decision 用 g1-ask,
        # 5-tasks 用 t-ask,7-review 用 g3-ask,不是 s-ask/r-oc。
        if any(x in _oh for x in ('class="r-oc"', 'class="s-ask"', "這條才變的")):
            _other_ok = False
            _other_detail.append(f"{_st} 卡被加了 4-spec 審查塊")
    check(_other_ok, "2/5/7:卡本體沒被加進 4-spec 的 s-ask/r-oc/delta",
          "; ".join(_other_detail))

print("-- 2-decision 審查卡形狀:頁上一次脈絡,卡留裁決/否決/繫站 + 2–3 問 --")
CURRENT_GROUP = "decision-review-shape"
# 套 4-spec 已合的骨架,但 class 分站(g1-*),4-spec 形狀不准退。
_dec2 = read_html_or_none(proj / "2-decision.html")
if _dec2 is None:
    for _lab in (
        "2-decision:不得出現「這一點在說什麼」/claim",
        "2-decision:作業脈絡頁上一次,不進每張卡",
        "2-decision:每張卡 2–3 條「你要審什麼」(問題,不重述正本欄)",
        "2-decision:每張卡留裁決、否決項、綁到哪一站",
        "2-decision:用 g1-ask,不是 4-spec 的 s-ask",
        "4-spec:沒有 2-decision 的 g1-ask/g1-oc(已合形狀不准退)",
        "5-tasks:不用 g1-*／s-ask(本刀改走 t-ask)",
        "7-review:不用 g1-*／s-ask(改走 g3-ask)",
    ):
        check(False, _lab, "2-decision.html 不存在(前面已失敗)")
else:
    _d_cards = re.findall(r'<article class="s-card.*?</article>', _dec2, re.S)
    _claim2 = re.search(
        r"這一點在說什麼|class=\"claim\"|class=\"s-claim\"|s-claim", _dec2)
    check(not _claim2,
          "2-decision:不得出現「這一點在說什麼」/claim",
          f"命中 {_claim2.group(0) if _claim2 else ''}")
    _oc_n = _dec2.count('class="g1-oc"')
    _oc_in_card = [re.search(r'data-sid="([^"]+)"', c).group(1)
                   for c in _d_cards if 'class="g1-oc"' in c or 'class="r-oc"' in c]
    check(_oc_n == 1 and not _oc_in_card,
          "2-decision:作業脈絡頁上一次,不進每張卡",
          f"g1-oc {_oc_n} 次,卡內:{_oc_in_card}")
    _ask2_ok = True
    _ask2_detail = []
    for c in _d_cards:
        sid_m = re.search(r'data-sid="([^"]+)"', c)
        sid = sid_m.group(1) if sid_m else "?"
        qs = re.findall(
            r'<li><span class="qmark">\?</span><span>(.*?)</span></li>', c, re.S)
        qs_txt = [re.sub(r"<[^>]+>", "", q) for q in qs]
        gwt = re.findall(r'<span class="gwt-v">(.*?)</span>', c, re.S)
        gwt_txt = [re.sub(r"<[^>]+>", "", v) for v in gwt]
        if not (2 <= len(qs) <= 3):
            _ask2_ok = False
            _ask2_detail.append(f"{sid} 問題數 {len(qs)}")
            continue
        if any("？" not in q and "?" not in q for q in qs_txt):
            _ask2_ok = False
            _ask2_detail.append(f"{sid} 有不是問題的條目")
        if any(g and len(g) >= 8 and any(g in q for q in qs_txt) for g in gwt_txt):
            _ask2_ok = False
            _ask2_detail.append(f"{sid} 問題重述正本欄")
        if "你要審什麼" not in c or 'class="g1-ask"' not in c:
            _ask2_ok = False
            _ask2_detail.append(f"{sid} 缺 g1-ask")
    check(_ask2_ok and len(_d_cards) >= 1,
          "2-decision:每張卡 2–3 條「你要審什麼」(問題,不重述正本欄)",
          "; ".join(_ask2_detail) or "沒有卡")
    _fields_ok = all(
        '<span class="gwt-k">裁決</span>' in c
        and '<span class="gwt-k">否決項</span>' in c
        and '<span class="gwt-k">綁到哪一站</span>' in c
        for c in _d_cards)
    check(_fields_ok and len(_d_cards) >= 1,
          "2-decision:每張卡留裁決、否決項、綁到哪一站",
          "有卡缺這三欄")
    check('class="g1-ask"' in _dec2 and 'class="s-ask"' not in _dec2
          and 'class="r-oc"' not in _dec2,
          "2-decision:用 g1-ask,不是 4-spec 的 s-ask",
          "s-ask/r-oc 漏進 2-decision 或缺 g1-ask")
    _sids = [re.search(r'data-sid="([^"]+)"', c).group(1) for c in _d_cards]
    check(any(s.startswith("OC-") for s in _sids)
          and any(re.match(r"^[A-Z]( |$)", s) for s in _sids),
          "2-decision:Approach 卡與 Owner Call 卡都在(模板兩種待審都還在)",
          f"sid={_sids}")
    _spec4b = read_html_or_none(proj / "4-spec.html")
    check(bool(_spec4b) and "g1-ask" not in _spec4b and "g1-oc" not in _spec4b
          and 'class="s-ask"' in (_spec4b or ""),
          "4-spec:沒有 2-decision 的 g1-ask/g1-oc(已合形狀不准退)",
          "4-spec 被加了 g1-* 或丟了 s-ask")
    _later_ok = True
    _later_detail = []
    _oh5 = read_html_or_none(proj / "5-tasks.html")
    _oh7 = read_html_or_none(proj / "7-review.html")
    if _oh5 is None:
        _later_ok = False
        _later_detail.append("5-tasks.html 不存在")
    elif any(x in _oh5 for x in ("g1-ask", "g1-oc", 'class="s-ask"')):
        _later_ok = False
        _later_detail.append("5-tasks 吃了 2-decision/4-spec 的審題 class")
    if _oh7 is None:
        _later_ok = False
        _later_detail.append("7-review.html 不存在")
    elif any(x in _oh7 for x in ("g1-ask", "g1-oc", 'class="s-ask"', "t-ask")):
        _later_ok = False
        _later_detail.append("7-review 吃了 2-decision/4-spec/5-tasks 的審題 class")
    check(_later_ok, "5-tasks 不用 g1-*／s-ask；7-review 不用 g1/s/t-ask",
          "; ".join(_later_detail))

print("-- 5-tasks 審查卡形狀:T 卡 2–3 問,缺欄照舊紅底,作業脈絡通常不必 --")
CURRENT_GROUP = "tasks-review-shape"
# 套 4-spec 已合的骨架,但 class 分站(t-*),4-spec/2-decision 形狀不准退。
# 7-review 用 g3-ask,本組只釘 5-tasks 不漏 t-* 進別站。
_tsk5 = read_html_or_none(proj / "5-tasks.html")
if _tsk5 is None:
    for _lab in (
        "5-tasks:不得出現「這一點在說什麼」/claim",
        "5-tasks:作業脈絡通常不必(沒有 g1-oc/r-oc)",
        "5-tasks:每張 T 有 2–3 條「你要審什麼」(問題,不重述正本欄)",
        "5-tasks:禁止三張 T 同一句",
        "5-tasks:用 t-ask,不是 s-ask/g1-ask",
        "4-spec:沒有 5-tasks 的 t-ask(已合形狀不准退)",
        "2-decision:沒有 5-tasks 的 t-ask",
        "7-review:沒有 5-tasks 的 t-ask",
    ):
        check(False, _lab, "5-tasks.html 不存在(前面已失敗)")
else:
    _t_cards = re.findall(r'<article class="s-card.*?</article>', _tsk5, re.S)
    _t_cards = [c for c in _t_cards if re.search(r'data-sid="T-\d+"', c)]
    _claim5 = re.search(
        r"這一點在說什麼|class=\"claim\"|class=\"s-claim\"|s-claim", _tsk5)
    check(not _claim5,
          "5-tasks:不得出現「這一點在說什麼」/claim",
          f"命中 {_claim5.group(0) if _claim5 else ''}")
    check('class="g1-oc"' not in _tsk5 and 'class="r-oc"' not in _tsk5
          and "作業脈絡" not in _tsk5,
          "5-tasks:作業脈絡通常不必(沒有 g1-oc/r-oc)",
          "5-tasks 長出作業脈絡塊")
    _ask5_ok = True
    _ask5_detail = []
    _all_qs = []
    for c in _t_cards:
        sid_m = re.search(r'data-sid="([^"]+)"', c)
        sid = sid_m.group(1) if sid_m else "?"
        qs = re.findall(
            r'<li><span class="qmark">\?</span><span>(.*?)</span></li>', c, re.S)
        qs_txt = [re.sub(r"<[^>]+>", "", q) for q in qs]
        gwt = re.findall(r'<span class="gwt-v">(.*?)</span>', c, re.S)
        gwt_txt = [re.sub(r"<[^>]+>", "", v) for v in gwt]
        if not (2 <= len(qs) <= 3):
            _ask5_ok = False
            _ask5_detail.append(f"{sid} 問題數 {len(qs)}")
            continue
        if any("？" not in q and "?" not in q for q in qs_txt):
            _ask5_ok = False
            _ask5_detail.append(f"{sid} 有不是問題的條目")
        if any(g and len(g) >= 8 and any(g in q for q in qs_txt) for g in gwt_txt):
            _ask5_ok = False
            _ask5_detail.append(f"{sid} 問題重述正本欄")
        if "你要審什麼" not in c or 'class="t-ask"' not in c:
            _ask5_ok = False
            _ask5_detail.append(f"{sid} 缺 t-ask")
        _all_qs.extend(qs_txt)
    _theme_ok = (
        any(re.search(r"開工", q) for q in _all_qs)
        and any(re.search(r"Blocked-by|真的 T|前置", q) for q in _all_qs)
        and any(re.search(r"觀測|4-spec", q) for q in _all_qs))
    if not _theme_ok:
        _ask5_ok = False
        _ask5_detail.append("整頁問題沒蓋到開工／Blocked-by／4-spec 觀測")
    check(_ask5_ok and len(_t_cards) >= 1,
          "5-tasks:每張 T 有 2–3 條「你要審什麼」(問題,不重述正本欄)",
          "; ".join(_ask5_detail) or "沒有 T 卡")
    _seen_q = {}
    for _q in _all_qs:
        _seen_q[_q] = _seen_q.get(_q, 0) + 1
    _dup3 = [q for q, n in _seen_q.items() if n >= 3]
    check(not _dup3 and _all_qs,
          "5-tasks:禁止三張 T 同一句",
          f"重複≥3:{_dup3[:3]}")
    check('class="t-ask"' in _tsk5 and 'class="s-ask"' not in _tsk5
          and 'class="g1-ask"' not in _tsk5,
          "5-tasks:用 t-ask,不是 s-ask/g1-ask",
          "s-ask/g1-ask 漏進 5-tasks 或缺 t-ask")
    _spec4c = read_html_or_none(proj / "4-spec.html")
    check(bool(_spec4c) and "t-ask" not in _spec4c and "t-chk-hint" not in _spec4c
          and 'class="s-ask"' in (_spec4c or ""),
          "4-spec:沒有 5-tasks 的 t-ask(已合形狀不准退)",
          "4-spec 被加了 t-* 或丟了 s-ask")
    _dec2c = read_html_or_none(proj / "2-decision.html")
    check(bool(_dec2c) and "t-ask" not in _dec2c and "t-chk-hint" not in _dec2c
          and 'class="g1-ask"' in (_dec2c or ""),
          "2-decision:沒有 5-tasks 的 t-ask",
          "2-decision 被加了 t-* 或丟了 g1-ask")
    _rev7 = read_html_or_none(proj / "7-review.html")
    check(bool(_rev7) and "t-ask" not in _rev7 and "t-chk-hint" not in _rev7,
          "7-review:沒有 5-tasks 的 t-ask",
          "7-review 被加了 t-*")

print("-- 7-review 審查卡形狀:判定／出貨／爭點／風險／抽驗列,每列 2–3 問 --")
CURRENT_GROUP = "g3-review-shape"
# 套 4-spec 已合的骨架,但 class 分站(g3-*),4-spec/2-decision/5-tasks 形狀不准退。
_rev7b = read_html_or_none(proj / "7-review.html")
if _rev7b is None:
    for _lab in (
        "7-review:不得出現「這一點在說什麼」/claim",
        "7-review:作業脈絡通常不必(沒有 g1-oc/r-oc)",
        "7-review:每張卡 2–3 條「你要審什麼」(問題,不重述正本欄)",
        "7-review:禁止三張卡同一句",
        "7-review:用 g3-ask,不是 s-ask/g1-ask/t-ask",
        "4-spec:沒有 7-review 的 g3-ask(已合形狀不准退)",
        "2-decision:沒有 7-review 的 g3-ask",
        "5-tasks:沒有 7-review 的 g3-ask",
        "7-review:判定／出貨／爭點／風險／抽驗五種卡都在",
    ):
        check(False, _lab, "7-review.html 不存在(前面已失敗)")
else:
    _g3_cards = re.findall(r'<article class="s-card.*?</article>', _rev7b, re.S)
    _claim7 = re.search(
        r"這一點在說什麼|class=\"claim\"|class=\"s-claim\"|s-claim", _rev7b)
    check(not _claim7,
          "7-review:不得出現「這一點在說什麼」/claim",
          f"命中 {_claim7.group(0) if _claim7 else ''}")
    check('class="g1-oc"' not in _rev7b and 'class="r-oc"' not in _rev7b
          and "作業脈絡" not in _rev7b,
          "7-review:作業脈絡通常不必(沒有 g1-oc/r-oc)",
          "7-review 長出作業脈絡塊")
    _ask7_ok = True
    _ask7_detail = []
    _all_qs7 = []
    for c in _g3_cards:
        sid_m = re.search(r'data-sid="([^"]+)"', c)
        sid = sid_m.group(1) if sid_m else "?"
        qs = re.findall(
            r'<li><span class="qmark">\?</span><span>(.*?)</span></li>', c, re.S)
        qs_txt = [re.sub(r"<[^>]+>", "", q) for q in qs]
        gwt = re.findall(r'<span class="gwt-v">(.*?)</span>', c, re.S)
        gwt_txt = [re.sub(r"<[^>]+>", "", v) for v in gwt]
        if not (2 <= len(qs) <= 3):
            _ask7_ok = False
            _ask7_detail.append(f"{sid} 問題數 {len(qs)}")
            continue
        if any("？" not in q and "?" not in q for q in qs_txt):
            _ask7_ok = False
            _ask7_detail.append(f"{sid} 有不是問題的條目")
        if any(g and len(g) >= 8 and any(g in q for q in qs_txt) for g in gwt_txt):
            _ask7_ok = False
            _ask7_detail.append(f"{sid} 問題重述正本欄")
        if "你要審什麼" not in c or 'class="g3-ask"' not in c:
            _ask7_ok = False
            _ask7_detail.append(f"{sid} 缺 g3-ask")
        _all_qs7.extend(qs_txt)
    _theme7 = (
        any(re.search(r"檔:行|判失敗", q) for q in _all_qs7)
        and any(re.search(r"Matrix|授權", q) for q in _all_qs7))
    if not _theme7:
        _ask7_ok = False
        _ask7_detail.append("整頁問題沒蓋到檔:行判失敗／verdict 被 matrix 授權")
    check(_ask7_ok and len(_g3_cards) >= 1,
          "7-review:每張卡 2–3 條「你要審什麼」(問題,不重述正本欄)",
          "; ".join(_ask7_detail) or "沒有卡")
    _seen_q7 = {}
    for _q in _all_qs7:
        _seen_q7[_q] = _seen_q7.get(_q, 0) + 1
    _dup7 = [q for q, n in _seen_q7.items() if n >= 3]
    check(not _dup7 and _all_qs7,
          "7-review:禁止三張卡同一句",
          f"重複≥3:{_dup7[:3]}")
    check('class="g3-ask"' in _rev7b and 'class="s-ask"' not in _rev7b
          and 'class="g1-ask"' not in _rev7b and 'class="t-ask"' not in _rev7b,
          "7-review:用 g3-ask,不是 s-ask/g1-ask/t-ask",
          "s-ask/g1-ask/t-ask 漏進 7-review 或缺 g3-ask")
    _spec4d = read_html_or_none(proj / "4-spec.html")
    check(bool(_spec4d) and "g3-ask" not in _spec4d and "g3-chk-hint" not in _spec4d
          and 'class="s-ask"' in (_spec4d or ""),
          "4-spec:沒有 7-review 的 g3-ask(已合形狀不准退)",
          "4-spec 被加了 g3-* 或丟了 s-ask")
    _dec2d = read_html_or_none(proj / "2-decision.html")
    check(bool(_dec2d) and "g3-ask" not in _dec2d and "g3-chk-hint" not in _dec2d
          and 'class="g1-ask"' in (_dec2d or ""),
          "2-decision:沒有 7-review 的 g3-ask",
          "2-decision 被加了 g3-* 或丟了 g1-ask")
    _tsk5d = read_html_or_none(proj / "5-tasks.html")
    check(bool(_tsk5d) and "g3-ask" not in _tsk5d and "g3-chk-hint" not in _tsk5d
          and 'class="t-ask"' in (_tsk5d or ""),
          "5-tasks:沒有 7-review 的 g3-ask",
          "5-tasks 被加了 g3-* 或丟了 t-ask")
    _sids7 = [re.search(r'data-sid="([^"]+)"', c).group(1) for c in _g3_cards]
    _kinds7 = (
        any(s == "判定" for s in _sids7)
        and any(s.startswith("EC-") for s in _sids7)
        and any(re.match(r"^A\d+$", s) for s in _sids7)
        and any(s.startswith("KL-") or re.match(r"^K-\d+$", s) for s in _sids7)
        and any(re.match(r"^S-\d+", s) for s in _sids7)
        and 'class="tag main">抽驗</span>' in _rev7b)
    check(_kinds7,
          "7-review:判定／出貨／爭點／風險／抽驗五種卡都在",
          f"sid={_sids7}")

# ── guard-selfpin:原始碼裡的 CURRENT_GROUP 賦值集合必須等於 REQUIRED_GROUPS ──
# 心跳只能擋「刪掉一個區塊、卻忘了同時刪 REQUIRED_GROUPS 裡對應的名字」——
# 如果兩邊一起刪(連刪帶藏),heartbeat 完全看不到缺口。這裡反過來釘死:
# 原始碼裡實際出現的 CURRENT_GROUP 賦值,必須逐一對應 REQUIRED_GROUPS,不能只改一邊。
# (邊界:新增一個 print("-- … --") 卻忘了配 CURRENT_GROUP,檢查會靜靜掛在上一個
#  群組底下,這個自我掃描抓不到那種情況——老實承認,不假裝萬能。)
CURRENT_GROUP = "guard-selfpin"
if SELF_PATH and os.path.isfile(SELF_PATH):
    _own_source = Path(SELF_PATH).read_text(encoding="utf-8")
    _assigned = set(re.findall(r'^CURRENT_GROUP = "([a-z0-9-]+)"', _own_source, re.M))
    check(_assigned == set(REQUIRED_GROUPS),
          "原始碼中的 CURRENT_GROUP 賦值集合 = REQUIRED_GROUPS(無未註冊/已註冊但不存在的群組)",
          f"只在原始碼={sorted(_assigned - set(REQUIRED_GROUPS))} "
          f"只在 REQUIRED_GROUPS={sorted(set(REQUIRED_GROUPS) - _assigned)}")
    # 斷言不得被改成恆真(照 check-design-contract.sh 的既有寫法;2026-08-17 擴成三變體
    # `check(True` / `check(1 == 1` / `check(not False`——只認字面 True 的舊正則繞得過
    # `check(1 == 1, …)`,同步跟進 check-design-contract.sh 的修法)。
    _always_true = re.findall(r"^\s*check\(\s*(?:True|1\s*==\s*1|not\s+False)\b", _own_source, re.M)
    check(not _always_true,
          "沒有任何斷言被改成恆真(原始碼不得出現 `check(True`/`check(1 == 1`/`check(not False`)",
          f"命中 {len(_always_true)} 處 —— 恆真斷言等於該檢查被靜默解除武裝")
else:
    check(False, "取得本守衛自身路徑以做群組清單自我檢查", f"SELF_PATH={SELF_PATH!r}")

# 群組被連刪帶藏(區塊 + 清單條目一起刪、補填充檢查數湊 CHECKS)時,上面的
# guard-selfpin 只驗「賦值集合 == REQUIRED_GROUPS」——兩邊一起刪這個等式仍然成立,
# 而 heartbeat 只驗清單裡列的東西有沒有跑,清單本身變短它也看不出來。只有這個
# 釘死的字面數字會現形。
check(len(REQUIRED_GROUPS) == EXPECTED_GROUPS,
      f"REQUIRED_GROUPS 群組數 = EXPECTED_GROUPS({EXPECTED_GROUPS})",
      f"實得 {len(REQUIRED_GROUPS)} 個群組 —— 群組被連刪帶藏時只有這個釘死數字會現形")

# ── N-2 收尾:群組心跳(主要防線)+ 檢查數地板(次級 backstop)────────────────
CURRENT_GROUP = "gate-stage-baseline"
missing_groups = [g for g in REQUIRED_GROUPS if GROUPS_SEEN.get(g, 0) == 0]
if missing_groups:
    FAILED += 1
    print(f"  ✗ [heartbeat] 必跑檢查群組完全沒執行:{', '.join(missing_groups)}"
          " —— 幾乎都是某個區塊被整段刪掉了")
CHECKS += 1

check(CHECKS >= MIN_CHECKS, f"(次級 backstop)本檔檢查總數 ≥ {MIN_CHECKS}",
      f"實得 {CHECKS}")

print()
print(f"  • heartbeat:{len(REQUIRED_GROUPS)} 個必跑區塊全部有執行 "
      f"({', '.join(f'{g}={GROUPS_SEEN.get(g, 0)}' for g in REQUIRED_GROUPS)})")
if FAILED:
    print(f"❌ gate twin 產生器守衛:{FAILED} 項失敗(共 {CHECKS} 項)")
    sys.exit(1)
print(f"✅ gate twin 產生器守衛:全過({CHECKS} 項)")
PY
