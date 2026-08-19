#!/bin/bash
# check-hooks-accounting.sh — hooks 記帳對帳守衛(第 7 型「不對稱記帳」通解實例)。
#
# 抓什麼:`hooks/hooks.json`(掛載的機械正本)與所有「為了驗證而列舉 hook 的
# 文件」之間的漂移 —— 數量與名稱都比,任一處漏列/多列/數字過期就紅:
#   ① skills/dev-setup/SKILL.md:安裝健檢清單(N 支可執行、N 條掛載、逐條列舉)
#   ② README.md:執行守衛段的 hook 名稱列舉
#   ②' docs/PLUGIN.md:hooks 表 + skills 表(skills 對帳的機械正本 = skills/ 目錄)
#   ③ guides/guide-dev-flow.html:hooks 註冊表(event/matcher/command/timeout 鏡像
#      + 「這 N 支」計數字)
#
# 為什麼需要(2026-08-17 F1):hooks 從 5 條掛載長到 6 條(新增 devflow-dispatch-
# guard)時,runtime 消費端全對,唯獨 dev-setup 的健檢清單靜默停在 5 條/七支 ——
# 採用專案照它健檢,會把線上真實存在的第 6 支 hook 判成「多出來的」。而同一份
# 檔案自己寫過「案數以腳本輸出為準,不在本檔寫死」。這不是第 6 型(修法不對稱),
# 是**記帳**不對稱:沒有任何檢查在比對「機制 vs 列舉它的文件」。本守衛就是那個檢查。
#
# 文件裡「可以」寫死數字的前提 = 有這支守衛釘著;守衛在,數字才不會靜默腐化。
#
# exit code:0 = 三份文件與 hooks.json 一致;1 = 任一處漂移(列出哪裡);
# 2 = hooks.json 讀不到/解析不了(檢查本身故障,fail-closed)。

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

python3 - "$ROOT" <<'PY'
import json
import os
import re
import sys

root = sys.argv[1]
fails = []


def fail(msg):
    fails.append(msg)


# ── 機械正本:hooks/hooks.json ────────────────────────────────────────────
hooks_path = os.path.join(root, "hooks", "hooks.json")
try:
    with open(hooks_path, encoding="utf-8") as stream:
        cfg = json.load(stream)
    mounts = []          # (event, matcher, script_basename, timeout)
    for event, entries in cfg["hooks"].items():
        for entry in entries:
            for h in entry["hooks"]:
                name = os.path.basename(h["command"])
                mounts.append((event, entry["matcher"], name, h.get("timeout")))
except Exception as exc:
    print(f"FATAL: 讀不到/解析不了 {hooks_path}:{exc}(機械正本壞了,對帳無從談起)",
          file=sys.stderr)
    sys.exit(2)
if not mounts:
    print("FATAL: hooks.json 解析出 0 條掛載 —— 不是「文件都對」,是正本空了",
          file=sys.stderr)
    sys.exit(2)

mount_count = len(mounts)
script_names = sorted({m[2] for m in mounts})          # 含 .sh
CN_NUM = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
          6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}


def num_matches(text_num, expected):
    """文件裡的數字(阿拉伯或中文)是否等於 expected。"""
    return text_num == str(expected) or text_num == CN_NUM.get(expected, "")


# ── ① skills/dev-setup/SKILL.md ─────────────────────────────────────────
skill_path = os.path.join(root, "skills", "dev-setup", "SKILL.md")
skill = open(skill_path, encoding="utf-8").read()

m = re.search(r"hooks\.json 應有 ([0-9一二三四五六七八九十]+) 條掛載", skill)
if not m:
    fail("SKILL.md 找不到「hooks.json 應有 N 條掛載」句 —— 記帳句本身不得被刪")
elif not num_matches(m.group(1), mount_count):
    fail(f"SKILL.md 掛載數寫「{m.group(1)} 條」,hooks.json 實際 {mount_count} 條")

# 逐條列舉:`<event> \`matcher\`→name` —— 與實際掛載集合雙向比對。
# 事件名不寫死成 PreToolUse|PostToolUse:hooks.json 允許非工具事件(UserPromptSubmit
# 等),寫死會讓新掛的非工具 hook 永遠對不上、卻報成「SKILL.md 漏列」而不是
# 「這支守衛自己認不得」—— 一樣是第 7 型,只是漂的是這支守衛本身。
listed = set(re.findall(r"([A-Z][A-Za-z]+)\s*`([^`]+)`→([a-z0-9-]+)", skill))
listed = {x for x in listed if x[0] in {e for e, _m, _n, _t in mounts} | {
    "PreToolUse", "PostToolUse", "UserPromptSubmit"}}
actual = {(e, mt, n[:-3] if n.endswith(".sh") else n) for e, mt, n, _t in mounts}
for miss in sorted(actual - listed):
    fail(f"SKILL.md 掛載列舉漏了:{miss[0]} `{miss[1]}`→{miss[2]}")
for extra in sorted(listed - actual):
    fail(f"SKILL.md 掛載列舉多了(hooks.json 沒有):{extra[0]} `{extra[1]}`→{extra[2]}")

# (下行的冒號字元集 [:：] = 半形+全形 —— 本檔第一版真的打成 [::] 被
#  check-regex-charclass.sh 當場抓到,G3 通解上線首日就逮到現行犯)
m = re.search(r"hooks/ ([0-9一二三四五六七八九十]+) 支可執行\**[:：]([^。]+)。", skill)
if not m:
    fail("SKILL.md 找不到「hooks/ N 支可執行:…。」句 —— 記帳句本身不得被刪")
else:
    names = [re.sub(r"[*\s]", "", x) for x in m.group(2).replace("\n", "").split("、")]
    names = [n for n in names if n]
    if not num_matches(m.group(1), len(names)):
        fail(f"SKILL.md 可執行清單自打:寫「{m.group(1)} 支」但列了 {len(names)} 個名字")
    for e, mt, n, _t in mounts:
        base = n[:-3] if n.endswith(".sh") else n
        if base not in names:
            fail(f"SKILL.md 可執行清單漏了掛載中的 {base}(hooks.json {e} `{mt}`)")
    for n in names:
        p = os.path.join(root, "hooks", n + ".sh")
        if not os.path.isfile(p):
            fail(f"SKILL.md 可執行清單列了不存在的 hooks/{n}.sh")
        elif not os.access(p, os.X_OK):
            fail(f"SKILL.md 說 {n} 可執行,但 hooks/{n}.sh 沒有執行權限")

# ── ② README.md:執行守衛段落必須點名每一支掛載中的 hook ─────────────────
readme = open(os.path.join(root, "README.md"), encoding="utf-8").read()
for name in script_names:
    base = name[:-3] if name.endswith(".sh") else name
    if base not in readme:
        fail(f"README.md 完全沒提到掛載中的 {base}(hooks.json 有,文件沒有)")

# ── ②' docs/PLUGIN.md:第四份列舉副本(hooks 表 + skills 表)────────────────
# 第一版守衛只掃三份文件,盤點當場抓到 PLUGIN.md 漏了 2 支 hook 與 1 個 skill ——
# 「正在蓋的對帳守衛剛好漏掉一份副本」正是第 7 型自身的復發樣態,列舉副本必須全數納管。
plugin_md = open(os.path.join(root, "docs", "PLUGIN.md"), encoding="utf-8").read()
for name in script_names:
    if name not in plugin_md:
        fail(f"docs/PLUGIN.md hooks 表漏了掛載中的 {name}")
skills_dir = os.path.join(root, "skills")
for d in sorted(os.listdir(skills_dir)):
    if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith("."):
        if f"`{d}`" not in plugin_md:
            fail(f"docs/PLUGIN.md skills 表漏了 skills/{d}(目錄存在,文件沒列)")

# ── ③ guides/guide-dev-flow.html:hooks 註冊表逐格鏡像 + 計數字 ───────────
guide = open(os.path.join(root, "guides", "guide-dev-flow.html"),
             encoding="utf-8").read()
for event, matcher, name, timeout in mounts:
    row = (rf"<td><code>{re.escape(event)}</code></td><td><code>{re.escape(matcher)}</code></td>\s*"
           rf"<td><code>\$\{{CLAUDE_PLUGIN_ROOT\}}/hooks/{re.escape(name)}</code></td>"
           rf"<td>{timeout}</td>")
    if not re.search(row, guide):
        fail(f"guide hooks 註冊表缺/不符:{event} `{matcher}` → {name}(timeout={timeout})"
             " —— event/matcher/command/timeout 四格須與 hooks.json 逐字一致")
cells = re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/hooks/([a-z0-9-]+\.sh)", guide)
if len(cells) != mount_count:
    fail(f"guide 註冊表的 command 格共 {len(cells)} 個,hooks.json 有 {mount_count} 條掛載"
         f"(多/少:{sorted(set(cells) ^ {m[2] for m in mounts})})")
for lineno, line in enumerate(guide.splitlines(), 1):
    if re.search(r"掛在哪|自動註冊|全部是第三種", line):
        for num in re.findall(r"這([0-9一二三四五六七八九十]+)支", line):
            if not num_matches(num, len(script_names)):
                fail(f"guide:{lineno} 寫「這{num}支」,實際掛載 {len(script_names)} 支不同腳本")

# ── ④ 兩份導覽的生命週期圖:圖上必須點名每一支掛載中的 hook ───────────────
# 為什麼要獨立於③:③比的是文字版 hooks 註冊表(event/matcher/command/timeout 四格),
# 生命週期圖是**另一個列舉面**,③掃不到它。而 check-guides-fig-sync.sh 只保證
# 「兩份圖彼此一致」,不保證圖與 hooks.json 一致 —— 兩份一起漏同一支時它照樣綠。
# 這不是假設:devflow-report-guard 2026-08-17 掛上,兩份圖都沒補,兩支守衛全綠到
# 2026-08-19 才被人眼抓到。把圖接到機械正本上,以後漏一支就紅(第 7 型:守衛比錯軸)。
# 圖上為排版用簡寫(dispatch-guard = devflow-dispatch-guard),兩種寫法都認。
FIGS = (("guides/guide-dev-flow.html", "fig-lifecycle"),
        ("guides/guide-quickstart.html", "fig-lifecycle-qs"))


def fig_hook_failures(text, sid, expected):
    """expected = 不含 .sh 的腳本名集合;回 failure 列表(雙向:漏列 + 多列)。"""
    m = re.search(r'<svg id="%s".*?</svg>' % re.escape(sid), text, re.S)
    if not m:
        return [f'找不到 <svg id="{sid}"> —— 圖被改名或刪掉,對帳無從談起']
    body = re.sub(r'aria-label="[^"]*"', "", m.group(0))   # 無障礙描述不算數,只看圖上的字
    ann = re.findall(r'<text class="dc"[^>]*>([^<]*)</text>', body)
    if not ann:
        return [f'{sid} 沒有任何 class="dc" 標註 —— 圖上不再點名 hook,這條檢查會空轉']
    tokens = set()
    for a in ann:
        for piece in a.split("·"):
            piece = piece.strip()
            if re.fullmatch(r"[a-z0-9-]+", piece):     # 純 ASCII 小寫才算 hook 名
                tokens.add(piece)                       # 中文說明/(Async) 之類自然被排除
    out = []
    forms = {}
    for base in sorted(expected):
        short = base[len("devflow-"):] if base.startswith("devflow-") else base
        forms[base] = {base, short}
        if not (forms[base] & tokens):
            out.append(f"{sid} 圖上沒點名掛載中的 {base}(hooks.json 有,圖沒有)")
    known = set().union(*forms.values()) if forms else set()
    for stray in sorted(tokens - known):
        out.append(f"{sid} 圖上點名了 {stray},但 hooks.json 沒這支(拆掉的 hook 沒從圖上撤)")
    return out


expected_bases = {n[:-3] if n.endswith(".sh") else n for n in script_names}
fig_texts = {}
for rel, sid in FIGS:
    fig_texts[rel] = open(os.path.join(root, *rel.split("/")), encoding="utf-8").read()
    for msg in fig_hook_failures(fig_texts[rel], sid, expected_bases):
        fail(f"{rel}:{msg}")

# 負向自檢:證明④真的有鑑別力,不是永遠回空清單。兩份各驗一次 —— 只驗一份的話,
# 另一份的檢查失效不會有任何訊號(而「兩份一起漏」正是這條要防的原始事故形態)。
for rel, sid in FIGS:
    if not fig_hook_failures(fig_texts[rel], sid, expected_bases | {"devflow-phantom-guard"}):
        fail(f"負向自檢失效:{rel} 的圖少一支新 hook 竟然沒被判漏列 —— ④ 沒有鑑別力")
    probe = sorted(expected_bases)[0]
    if not fig_hook_failures(fig_texts[rel], sid, expected_bases - {probe}):
        fail(f"負向自檢失效:{rel} 的圖點名了 hooks.json 沒有的 {probe} 竟然沒被判多列")

# ── 輸出 ─────────────────────────────────────────────────────────────────
print(f"=== hooks 記帳對帳:hooks.json {mount_count} 條掛載 / {len(script_names)} 支腳本 "
      f"vs SKILL.md + README + PLUGIN.md + guide 註冊表 + 兩份生命週期圖 ===")
if fails:
    print(f"❌ 記帳漂移 {len(fails)} 處(第 7 型:機制長大了,列舉它的文件沒跟上):")
    for f in fails:
        print(f"   {f}")
    print("   修法:讓文件跟上 hooks.json(或 hooks.json 才是錯的那邊 —— 人判斷,守衛只報不一致)。")
    sys.exit(1)
print("✅ 四份列舉文件 + 兩份生命週期圖與 hooks.json/skills 目錄一致(數量與名稱都比過,圖為雙向)")
PY
