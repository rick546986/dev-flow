#!/bin/bash
# check-pages-hosting.sh — 站審 html 掛 Pages 契約牙
#
# 咬什麼:notes/design/pages-hosting.md 丟了鎖死句子
# (站審 html 檔名／shots/／相對路／github.io 超連／serve --root／
# 薄殼不抄正文／不要另開本機伺服器),
# 或三邊食譜缺一邊、拿掉 pages job、組樹漏 7-review.html／shots,
# 必須紅。
# README.md 與 guides/*.html 可點的 *.html 超連必須是既有 GitHub 超連規則
# https://<owner>.github.io/<repo>/<path-to-html>(本倉即
# https://rick546986.github.io/dev-flow/...),相對路或 blob 必須紅。
# 頁內 #錨 不算超連。md 正本／repo 路徑可留。
#
# 實跑 publish-pages.sh --root fixture:public/ 必須出現站審 html + shots/ + guides。
# 禁 check(True)。補助產品詞不得當通用規則。
# 不改 build-gate-twin.py STAGES、不改掃頁／第 6 站／#61 產器、不改 #60 正本。
#
# 用法:
#   scripts/check-pages-hosting.sh [root]
# exit:0 = 全過 / 1 = 契約或食譜壞了 / 2 = 環境或用法失敗

set -uo pipefail

SELF=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

root = sys.argv[1]
CONTRACT = "notes/design/pages-hosting.md"
README = "README.md"
PUBLISHER = "scripts/publish-pages.sh"
DIST = "docs/dev/tools/publish-pages.sh"
GITLAB = ".gitlab-ci.yml"
GITEA = ".gitea/workflows/pages.yml"
HELPER = "scripts/devflow_gate.py"
SKILL = "skills/dev-setup/SKILL.md"
FIXTURE = "scripts/fixtures/pages-hosting/good"
PAGES_HREF = "https://rick546986.github.io/dev-flow/"
STAGES = (
    "1-discussion.html",
    "2-decision.html",
    "5-tasks.html",
    "6-implementation-notes.html",
    "7-review.html",
)

failures = []
checks = 0


def check(ok, label):
    global checks
    checks += 1
    if ok:
        print("[ok] " + label)
        return
    print("[FAIL] " + label)
    failures.append(label)


def read(rel):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as stream:
        return stream.read()


CONTRACT_NEEDLES = (
    "1-discussion",
    "2-decision",
    "5-tasks",
    "6-implementation-notes",
    "7-review",
    "shots/",
    "相對",
    "github.io",
    "<owner>",
    "<repo>",
    "serve",
    "--root",
    "GitLab",
    "Gitea",
    "public/",
    "pages",
    "example",
    "guides",
    "薄殼",
    "不要另開",
    "publish-pages.sh",
)

FORBIDDEN = (
    "PLUS",
    "形成併取卵",
    "27004",
    "apply_date",
    "表五",
    "表六",
    "8604",
)


def readme_html_hrefs(text):
    """README 裡人點得到的 *.html 超連(markdown ](url) 與 <a href>)。不管 img src。"""
    if not text:
        return []
    found = []
    for match in re.finditer(r"(?<!!)\[(?:[^\]]*)\]\(([^)]+)\)", text):
        found.append(match.group(1).strip())
    for match in re.finditer(r"""(?i)<a\b[^>]*\bhref\s*=\s*["']([^"']+)["']""", text):
        found.append(match.group(1).strip())
    hrefs = []
    for raw in found:
        path = raw.split("#", 1)[0]
        if path.endswith(".html"):
            hrefs.append(raw)
    return hrefs


def judge_readme_html(readme_text):
    local = []
    if readme_text is None:
        local.append("README.md 存在")
        return local
    hrefs = readme_html_hrefs(readme_text)
    if not hrefs:
        local.append("README 至少有一條 *.html 超連")
        return local
    for href in hrefs:
        if not href.startswith(PAGES_HREF):
            local.append("README *.html 超連必須是 github.io Pages:" + href)
    return local


def html_hrefs(text):
    found = []
    for match in re.finditer(r"""(?i)<a\b[^>]*\bhref\s*=\s*["']([^"']+)["']""", text):
        found.append(match.group(1).strip())
    hrefs = []
    for raw in found:
        path = raw.split("#", 1)[0]
        if path.endswith(".html"):
            hrefs.append(raw)
    return hrefs


def judge_guides_html():
    local = []
    guides = os.path.join(root, "guides")
    if not os.path.isdir(guides):
        local.append("guides/ 存在")
        return local
    for name in sorted(os.listdir(guides)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(guides, name)
        text = open(path, encoding="utf-8").read()
        for href in html_hrefs(text):
            if not href.startswith(PAGES_HREF):
                local.append(name + " *.html 超連必須是 github.io Pages:" + href)
    return local


def judge(contract_text, gitlab_text, gitea_text, publisher_text, skill_text, helper_text):
    local = []

    def fail(label):
        local.append(label)

    if contract_text is None:
        fail("契約存在 " + CONTRACT)
        return local
    if "鎖死" not in contract_text:
        fail("契約標題／本文含「鎖死」")
    for needle in CONTRACT_NEEDLES:
        if needle not in contract_text:
            fail("契約含「%s」" % needle)
    for bad in FORBIDDEN:
        if bad in contract_text:
            fail("契約未把補助產品詞「%s」寫成通用規則" % bad)
    if "不要改" not in contract_text or "source path" not in contract_text:
        fail("契約寫清不要改 GitHub source path")
    if "https://<owner>.github.io/<repo>/" not in contract_text:
        fail("契約含 GitHub 超連 https://<owner>.github.io/<repo>/")

    if gitlab_text is None:
        fail("GitLab 薄殼存在 " + GITLAB)
    else:
        if "pages:" not in gitlab_text:
            fail("GitLab 薄殼有 pages job")
        if "public" not in gitlab_text:
            fail("GitLab pages artifacts 指向 public/")
        if "publish-pages.sh" not in gitlab_text:
            fail("GitLab 薄殼呼叫 publish-pages.sh")
        if "--root" not in gitlab_text:
            fail("GitLab 薄殼用 --root")
        if "cp " in gitlab_text and "7-review.html" in gitlab_text:
            fail("GitLab 薄殼不抄複製清單")

    if gitea_text is None:
        fail("Gitea 薄殼存在 " + GITEA)
    else:
        if "pages" not in gitea_text:
            fail("Gitea 薄殼有 pages 食譜")
        if "publish-pages.sh" not in gitea_text:
            fail("Gitea 薄殼呼叫 publish-pages.sh")
        if "--root" not in gitea_text:
            fail("Gitea 薄殼用 --root")
        if "cp " in gitea_text and "7-review.html" in gitea_text:
            fail("Gitea 薄殼不抄複製清單")

    if publisher_text is None:
        fail("食譜正文存在 " + PUBLISHER)
    else:
        for needle in STAGES:
            if needle not in publisher_text:
                fail("食譜正文會掛「%s」" % needle)
        if "shots" not in publisher_text:
            fail("食譜正文會掛 shots/")
        if "guides" not in publisher_text:
            fail("食譜正文會掛 guides/")
        if "--root" not in publisher_text:
            fail("食譜正文 CLI 用 --root")

    if skill_text is None:
        fail("dev-setup SKILL 存在")
    else:
        if "publish-pages.sh" not in skill_text:
            fail("dev-setup 散發 publish-pages.sh(同一條發散路)")
        if "docs/dev/tools/" not in skill_text:
            fail("dev-setup 散發落到 docs/dev/tools/")

    if helper_text is None:
        fail("serve 寫入器存在 " + HELPER)
    else:
        if "serve" not in helper_text:
            fail("本機對應仍是 serve")
        if "--root" not in helper_text:
            fail("serve CLI 用 --root")

    return local


contract_text = read(CONTRACT)
gitlab_text = read(GITLAB)
gitea_text = read(GITEA)
publisher_text = read(PUBLISHER)
skill_text = read(SKILL)
helper_text = read(HELPER)
readme_text = read(README)

real = judge(contract_text, gitlab_text, gitea_text, publisher_text, skill_text, helper_text)
check(not real, "完整食譜綠")
if real:
    for item in real:
        print("  - " + item)

readme_fails = judge_readme_html(readme_text)
check(not readme_fails, "README *.html 超連都是 github.io Pages")
if readme_fails:
    for item in readme_fails:
        print("  - " + item)

guide_fails = judge_guides_html()
check(not guide_fails, "guides/*.html 的 *.html 超連都是 github.io Pages")
if guide_fails:
    for item in guide_fails:
        print("  - " + item)

# 散發副本與正本一致(同一條發散路)
src = os.path.join(root, PUBLISHER)
dst = os.path.join(root, DIST)
src_ok = os.path.isfile(src)
dst_ok = os.path.isfile(dst)
check(src_ok and dst_ok, "正本與 docs/dev/tools/ 副本都在")
if src_ok and dst_ok:
    with open(src, "rb") as a, open(dst, "rb") as b:
        same = a.read() == b.read()
    check(same, "散發副本與正本逐字一致")
    src_x = os.stat(src).st_mode & stat.S_IXUSR
    dst_x = os.stat(dst).st_mode & stat.S_IXUSR
    check(bool(src_x) and bool(dst_x), "正副本都可執行")

# 實跑組樹
fixture = os.path.join(root, FIXTURE)
check(os.path.isdir(fixture), "fixture 存在 " + FIXTURE)
if os.path.isdir(fixture):
    tmp = tempfile.mkdtemp(prefix="pages-host.")
    try:
        out = os.path.join(tmp, "public")
        run = subprocess.run(
            ["bash", src, "--root", fixture, "--out", out],
            cwd=root, capture_output=True, text=True,
        )
        check(run.returncode == 0, "publish-pages.sh --root fixture → exit 0")
        review = os.path.join(out, "docs", "dev", "demo-feat", "7-review.html")
        shot = os.path.join(out, "docs", "dev", "demo-feat", "shots", "sample.png")
        guide = os.path.join(out, "guides", "guide-quickstart.html")
        ex = os.path.join(out, "example", "demo-feat", "7-review.html")
        check(os.path.isfile(review), "public/ 含 docs/dev/<feat>/7-review.html")
        check(os.path.isfile(shot), "public/ 含相對路 shots/")
        check(os.path.isfile(guide), "public/ 含 guides/")
        check(os.path.isfile(ex), "public/ 含 example 同名 7-review.html")
        # 相對路沒被改寫
        if os.path.isfile(review):
            body = open(review, encoding="utf-8").read()
            check('src="shots/sample.png"' in body, "組樹後仍是相對路 shots/")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --help 必須 exit 2
    help_run = subprocess.run(
        ["bash", src, "--help"],
        cwd=root, capture_output=True, text=True,
    )
    check(help_run.returncode == 2, "--help → exit 2")

    # 位置參數必須拒絕
    pos = subprocess.run(
        ["bash", src, fixture],
        cwd=root, capture_output=True, text=True,
    )
    check(pos.returncode == 2, "位置參數當根 → exit 2")

# 拿掉 pages job／漏掛必須紅(自咬)
if gitlab_text is not None:
    stripped = gitlab_text.replace("pages:", "")
    check(bool(judge(contract_text, stripped, gitea_text, publisher_text, skill_text, helper_text)),
          "牙咬:拿掉 pages job 必須紅")
if publisher_text is not None:
    no_review = publisher_text.replace("7-review.html", "")
    check(bool(judge(contract_text, gitlab_text, gitea_text, no_review, skill_text, helper_text)),
          "牙咬:食譜漏掉 7-review.html 必須紅")
    no_shots = publisher_text.replace("shots", "")
    check(bool(judge(contract_text, gitlab_text, gitea_text, no_shots, skill_text, helper_text)),
          "牙咬:食譜漏掉 shots 必須紅")
if contract_text is not None:
    no_url = contract_text.replace("https://<owner>.github.io/<repo>/", "")
    check(bool(judge(no_url, gitlab_text, gitea_text, publisher_text, skill_text, helper_text)),
          "牙咬:契約刪 GitHub 超連必須紅")
    no_serve = contract_text.replace("serve", "")
    check(bool(judge(no_serve, gitlab_text, gitea_text, publisher_text, skill_text, helper_text)),
          "牙咬:契約刪 serve 必須紅")
    poisoned = contract_text + "\nPLUS\n"
    check(bool(judge(poisoned, gitlab_text, gitea_text, publisher_text, skill_text, helper_text)),
          "牙咬:契約寫入補助產品詞必須紅")

if readme_text is not None:
    relative = readme_text.replace(PAGES_HREF + "guides/guide-dev-flow.html",
                                   "guides/guide-dev-flow.html", 1)
    check(bool(judge_readme_html(relative)),
          "牙咬:README 相對 *.html 必須紅")
    blob = readme_text.replace(
        PAGES_HREF + "guides/guide-dev-flow.html",
        "https://github.com/rick546986/dev-flow/blob/main/guides/guide-dev-flow.html",
        1)
    check(bool(judge_readme_html(blob)),
          "牙咬:README blob *.html 必須紅")

print("checks=%d" % checks)
if checks < 10:
    print("❌ FAIL:檢查數太少(%d)——牙自己沒跑" % checks)
    sys.exit(1)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:站審 html 掛 Pages 契約牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
