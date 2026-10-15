#!/bin/bash
# test-upgrade-manifest.sh — scripts/devflow-upgrade-manifest.py 的行為牙(Repo-local)。
#
# 起因:Prism 回報 dev-setup 沒有可直接跑的 upgrade 腳本,只能照 ship-manifest 手動複製。
# 查證:upgrade 原本只有 SKILL 散文步驟 + devflow-upgrade-leftovers.sh(只刪殘件),沒有「manifest 列
# → 採用專案」的指令。新增這支(只標準庫),本檔釘它的承諾:
#   ① 預設 dry-run:列新增/變更/相同、一個檔都不寫;② --apply 才寫,內容與 mode 逐列正確,
#   再跑一次全部「相同」;③ 本地客製(無 baseline 過渡態、本地≠baseline)預設跳過,--include-custom
#   才覆蓋;本地 = baseline 的「母版改寫」直接覆蓋;④ 絕不碰 manifest 以外的檔(含 README／STATUS／
#   baseline／自己加的工具);⑤ 路徑防跳脫:..／絕對路徑／.git／symlink 上層／symlink 目的檔／
#   --root==--pack 全拒絕且一個檔都不寫;⑥ 寫入失敗時 manifest 那列最後寫、失敗就不寫;
#   ⑦ 不留暫存檔;⑧ 只用標準庫(靜態);⑨ 套完後 doctor 的 ship-manifest／ship-deps 皆 ✓。
#
# 用法:scripts/test-upgrade-manifest.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" 2>/dev/null && pwd) || { echo "找不到 root: $1" >&2; exit 2; }
fi
TOOL="$ROOT/scripts/devflow-upgrade-manifest.py"
for f in "$TOOL" "$ROOT/docs/dev/ship-manifest.json" "$ROOT/hooks/_doctor_impl.py"; do
  [ -f "$f" ] || { echo "FATAL: 找不到 $f" >&2; exit 2; }
done
command -v python3 >/dev/null 2>&1 || { echo "FATAL: 缺 python3" >&2; exit 2; }

python3 - "$ROOT" "$TOOL" <<'PY'
import ast
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

root, tool = sys.argv[1], sys.argv[2]
MIN_CASES = 65
passed = failed = 0
sys.dont_write_bytecode = True


def check(cond, label, detail=""):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print("  ✗ %s%s" % (label, (" — " + detail) if detail else ""))


ENV = {k: v for k, v in os.environ.items() if not k.startswith("DEVFLOW_") and k not in ("PYTHONPATH", "PYTHONHOME")}
ENV["PYTHONDONTWRITEBYTECODE"] = "1"


def run(*args):
    r = subprocess.run([sys.executable, tool] + list(args), env=ENV, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def snapshot(base):
    out = {}
    for d, _dirs, files in os.walk(base):
        for n in files:
            p = os.path.join(d, n)
            out[os.path.relpath(p, base)] = open(p, "rb").read() if not os.path.islink(p) else b"<link>"
    return out


work = tempfile.mkdtemp(prefix="test-upgrade-manifest-")
try:
    manifest = jload(os.path.join(root, "docs", "dev", "ship-manifest.json"))
    rows = manifest["files"]
    dests = [r["destination"] for r in rows]

    def make_pack(name):
        """方法包複本:manifest + 每列 source(內容與母版相同,測試可改其中一份)。"""
        pack = os.path.join(work, name)
        for r in rows:
            dst = os.path.join(pack, *r["source"].split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(root, *r["source"].split("/")), dst)
        mp = os.path.join(pack, "docs", "dev", "ship-manifest.json")
        os.makedirs(os.path.dirname(mp), exist_ok=True)
        shutil.copyfile(os.path.join(root, "docs", "dev", "ship-manifest.json"), mp)
        return pack

    pack = make_pack("pack")

    # ── ① dry-run:列新增、不寫 ───────────────────────────────────────
    print("-- ① dry-run --")
    a1 = os.path.join(work, "a1"); os.makedirs(a1)
    rc, out, err = run("--root", a1, "--pack", pack)
    check(rc == 0, "dry-run exit 0", "rc=%s %s" % (rc, err))
    check(out.count("  新增  ") == len(rows), "空專案:每列都標新增(%d)" % len(rows), out[-300:])
    check(os.listdir(a1) == [], "dry-run 沒有寫入任何檔(專案仍是空的)")
    check("dry-run" in out and "沒有寫入任何檔案" in out, "輸出明說 dry-run、沒寫檔")
    check("baseline 的乾淨替換" in out and "_templates" in out, "輸出列出不在這支範圍的項目(README/_templates/baseline…)")
    rc, out, err = run("--root", a1, "--pack", pack, "--include-custom")
    check(rc == 0 and os.listdir(a1) == [], "--include-custom 不帶 --apply 仍是 dry-run、不寫")

    # ── ② --apply:逐列內容與 mode 正確;再跑全相同 ────────────────────
    print("-- ② --apply --")
    rc, out, err = run("--root", a1, "--pack", pack, "--apply")
    check(rc == 0 and ("寫入 %d、跳過 0、失敗 0" % len(rows)) in out, "--apply 全部寫入", "rc=%s %s" % (rc, out[-200:] + err))
    ok_content = all(open(os.path.join(a1, *r["destination"].split("/")), "rb").read()
                     == open(os.path.join(pack, *r["source"].split("/")), "rb").read() for r in rows)
    check(ok_content, "每列內容與方法包 source 逐位元組相同")
    ok_mode = all(stat.S_IMODE(os.stat(os.path.join(a1, *r["destination"].split("/"))).st_mode) == int(r["mode"], 8) for r in rows)
    check(ok_mode, "每列 mode 與 manifest 一致(755 有執行位元)")
    nested = os.path.join(a1, "docs", "dev", "tools", "devflow_jev", "gate.py")
    check(os.path.isfile(nested), "子目錄(docs/dev/tools/devflow_jev/)自動建立")
    check(sorted(snapshot(a1)) == sorted(os.path.join(*d.split("/")) for d in dests),
          "寫完後專案裡的檔 = manifest destination 全集,沒有多出任何檔(含暫存檔)")
    rc, out, err = run("--root", a1, "--pack", pack)
    check(rc == 0 and out.count("  相同  ") == len(rows) and "新增 0、變更 0" in out, "再跑一次 dry-run:全部相同")
    check(rc == 0, "冪等")

    # ── ③ 本地客製 / 母版改寫 ────────────────────────────────────────
    print("-- ③ 本地客製與母版改寫 --")
    a3 = os.path.join(work, "a3"); os.makedirs(a3)
    run("--root", a3, "--pack", pack, "--apply")
    tgt = os.path.join(a3, "docs", "dev", "tools", "diagir.py")
    with open(tgt, "ab") as f:
        f.write(b"\n# local custom\n")
    custom_bytes = open(tgt, "rb").read()
    rc, out, err = run("--root", a3, "--pack", pack, "--diff")
    line = next((l for l in out.splitlines() if "docs/dev/tools/diagir.py" in l and "變更" in l), "")
    check("需同意" in line and "無 baseline" in line, "無 baseline(過渡態)→ 變更標需同意", line)
    check("local custom" in out or "-# local custom" in out, "--diff 印出本地多的那行")
    rc, out, err = run("--root", a3, "--pack", pack, "--apply")
    check(rc == 0 and open(tgt, "rb").read() == custom_bytes and "跳過  docs/dev/tools/diagir.py" in out,
          "--apply 預設跳過需同意的檔,本地客製原封不動、exit 0")
    rc, out, err = run("--root", a3, "--pack", pack, "--apply", "--include-custom")
    check(rc == 0 and open(tgt, "rb").read() == open(os.path.join(pack, "scripts", "diagir.py"), "rb").read(),
          "--include-custom 才覆蓋回方法包版本")
    # 有 baseline:本地 = baseline(母版改寫)直接覆蓋;本地 ≠ baseline(客製)跳過
    a3b = os.path.join(work, "a3b"); os.makedirs(a3b)
    run("--root", a3b, "--pack", pack, "--apply")
    base = os.path.join(a3b, "docs", "dev", ".devflow-baseline")
    for r in rows:
        if r["destination"].startswith("docs/dev/"):
            b = os.path.join(base, *r["destination"][len("docs/dev/"):].split("/"))
            os.makedirs(os.path.dirname(b), exist_ok=True)
            shutil.copyfile(os.path.join(a3b, *r["destination"].split("/")), b)
    pack2 = make_pack("pack2")
    with open(os.path.join(pack2, "scripts", "diagir.py"), "ab") as f:
        f.write(b"\n# upstream newer\n")
    with open(os.path.join(pack2, "scripts", "devflow_atomic.py"), "ab") as f:
        f.write(b"\n# upstream newer 2\n")
    cust = os.path.join(a3b, "docs", "dev", "tools", "devflow_atomic.py")
    with open(cust, "ab") as f:
        f.write(b"\n# my edit\n")
    cust_bytes = open(cust, "rb").read()
    rc, out, err = run("--root", a3b, "--pack", pack2)
    l1 = next((l for l in out.splitlines() if "tools/diagir.py" in l), "")
    l2 = next((l for l in out.splitlines() if "tools/devflow_atomic.py" in l), "")
    check("母版改寫" in l1 and "需同意" not in l1, "baseline 在、本地 = baseline → 母版改寫", l1)
    check("需同意" in l2 and "本地客製" in l2, "baseline 在、本地 ≠ baseline → 本地客製需同意", l2)
    rc, out, err = run("--root", a3b, "--pack", pack2, "--apply")
    check(open(os.path.join(a3b, "docs", "dev", "tools", "diagir.py"), "rb").read().endswith(b"# upstream newer\n"),
          "母版改寫的檔 --apply 直接覆蓋")
    check(open(cust, "rb").read() == cust_bytes, "本地客製的檔 --apply 沒被動")

    # mode-only 差異:內容同、權限不同 → 母版改寫(不當客製)
    a3c = os.path.join(work, "a3c"); os.makedirs(a3c)
    run("--root", a3c, "--pack", pack, "--apply")
    sh = os.path.join(a3c, "docs", "dev", "tools", "history-append.sh")
    os.chmod(sh, 0o644)
    rc, out, err = run("--root", a3c, "--pack", pack, "--apply")
    check(stat.S_IMODE(os.stat(sh).st_mode) == 0o755 and "僅權限" in out, "只有權限不同 → 補回 755、不當本地客製")

    # ── ④ 不碰 manifest 以外的檔 ─────────────────────────────────────
    print("-- ④ manifest 以外的檔不動 --")
    a4 = os.path.join(work, "a4")
    extras = {
        "docs/dev/README.md": b"readme\n", "docs/dev/STATUS.md": b"status\n",
        "docs/dev/tools/my-own-tool.py": b"mine\n", "docs/dev/.devflow-baseline/README.md": b"b\n",
        "docs/dev/_templates/jev.yaml": b"mode: off\n", "src/app.py": b"print(1)\n", "CLAUDE.md": b"x\n",
    }
    for rel, data in extras.items():
        p = os.path.join(a4, *rel.split("/")); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)
    mt = {rel: os.stat(os.path.join(a4, *rel.split("/"))).st_mtime_ns for rel in extras}
    rc, out, err = run("--root", a4, "--pack", pack, "--apply")
    check(rc == 0, "有既有檔的專案 --apply 成功")
    check(all(open(os.path.join(a4, *rel.split("/")), "rb").read() == data for rel, data in extras.items()),
          "README／STATUS／自己的工具／baseline／_templates／原始碼／CLAUDE.md 內容完全不變")
    check(all(os.stat(os.path.join(a4, *rel.split("/"))).st_mtime_ns == mt[rel] for rel in extras), "它們的 mtime 也沒變(連碰都沒碰)")
    now = set(snapshot(a4))
    # baseline 目錄已存在 → manifest 列(docs/dev/ 底下)的上游新內容同步進 baseline 對應路徑(見 ⑩);
    # 除此之外不得有別的檔。
    bl_extra = set(os.path.join("docs", "dev", ".devflow-baseline", *d[len("docs/dev/"):].split("/"))
                   for d in dests if d.startswith("docs/dev/"))
    check(now == set(os.path.join(*d.split("/")) for d in dests) | set(os.path.join(*e.split("/")) for e in extras) | bl_extra,
          "專案檔案集合 = 既有檔 ∪ manifest destination ∪ 對應的 baseline 副本(沒憑空多出別的檔)")

    # ── ⑤ 路徑防跳脫 ────────────────────────────────────────────────
    print("-- ⑤ 路徑防跳脫 --")

    def evil_pack(name, mutate):
        p = make_pack(name)
        mp = os.path.join(p, "docs", "dev", "ship-manifest.json")
        d = jload(mp)
        mutate(d)
        json.dump(d, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return p

    for label, mut in (
        ("destination 含 ..", lambda d: d["files"][0].__setitem__("destination", "../escaped.txt")),
        ("destination 是絕對路徑", lambda d: d["files"][0].__setitem__("destination", "/tmp/devflow-escaped.txt")),
        ("destination 含反斜線", lambda d: d["files"][0].__setitem__("destination", "docs\\dev\\x")),
        ("source 含 ..", lambda d: d["files"][0].__setitem__("source", "../outside.txt")),
        ("mode 不合法", lambda d: d["files"][0].__setitem__("mode", "777")),
        ("destination 重複", lambda d: d["files"][1].__setitem__("destination", d["files"][0]["destination"])),
    ):
        ap = evil_pack("evil-" + str(abs(hash(label))), mut)
        a5 = os.path.join(work, "a5-" + str(abs(hash(label)))); os.makedirs(a5)
        rc, out, err = run("--root", a5, "--pack", ap, "--apply")
        check(rc == 2 and os.listdir(a5) == [], "%s → exit 2、一個檔都沒寫" % label, "rc=%s %s" % (rc, err[:200]))
    check(not os.path.exists(os.path.join(work, "escaped.txt")) and not os.path.exists("/tmp/devflow-escaped.txt"),
          "越界目的地真的沒被建出來")
    ap = evil_pack("evil-git", lambda d: d["files"][0].__setitem__("destination", ".git/hooks/pre-commit"))
    a5g = os.path.join(work, "a5g"); os.makedirs(a5g)
    rc, out, err = run("--root", a5g, "--pack", ap, "--apply")
    check(rc == 2 and os.listdir(a5g) == [], "destination 在 .git/ 底下 → exit 2、不寫")
    # symlink 上層:docs/dev/tools -> 專案外
    outside = os.path.join(work, "outside"); os.makedirs(outside)
    a5s = os.path.join(work, "a5s"); os.makedirs(os.path.join(a5s, "docs", "dev"))
    os.symlink(outside, os.path.join(a5s, "docs", "dev", "tools"))
    rc, out, err = run("--root", a5s, "--pack", pack, "--apply")
    check(rc == 2 and os.listdir(outside) == [], "docs/dev/tools 是 symlink 指到專案外 → exit 2、外面一個檔都沒多", "rc=%s %s" % (rc, err[:200]))
    # symlink 目的檔
    victim = os.path.join(outside, "victim.txt"); open(victim, "w").write("secret")
    a5f = os.path.join(work, "a5f"); os.makedirs(os.path.join(a5f, "docs", "dev", "tools"))
    os.symlink(victim, os.path.join(a5f, "docs", "dev", "tools", "diagir.py"))
    rc, out, err = run("--root", a5f, "--pack", pack, "--apply")
    check(rc == 2 and open(victim).read() == "secret", "destination 檔本身是 symlink → exit 2、被指的檔不被改")
    # root == pack、不存在的目錄
    rc, out, err = run("--root", pack, "--pack", pack)
    check(rc == 2, "--root 與 --pack 同一處 → 拒絕")
    rc, out, err = run("--root", os.path.join(work, "nope"), "--pack", pack)
    check(rc == 2, "--root 不存在 → exit 2")
    # 方法包缺 source 檔
    pk = make_pack("pack-missing"); os.remove(os.path.join(pk, "scripts", "diagir.py"))
    a5m = os.path.join(work, "a5m"); os.makedirs(a5m)
    rc, out, err = run("--root", a5m, "--pack", pk, "--apply")
    check(rc == 2 and os.listdir(a5m) == [], "方法包缺 source 檔 → exit 2、一個檔都沒寫")

    # ── ⑥ 寫入失敗:manifest 列最後寫、失敗就不寫 ─────────────────────
    print("-- ⑥ 寫入失敗 --")
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        print("  (root 身分:唯讀目錄擋不住寫入,略過 ⑥ 的失敗注入案)")
    else:
        a6 = os.path.join(work, "a6")
        os.makedirs(os.path.join(a6, "docs", "dev", "tools", "devflow_jev"))
        os.chmod(os.path.join(a6, "docs", "dev", "tools", "devflow_jev"), 0o555)
        try:
            rc, out, err = run("--root", a6, "--pack", pack, "--apply")
        finally:
            os.chmod(os.path.join(a6, "docs", "dev", "tools", "devflow_jev"), 0o755)
        check(rc == 1 and "失敗" in err, "子目錄唯讀 → 該列失敗、exit 1", "rc=%s %s" % (rc, err[:200]))
        check(not os.path.exists(os.path.join(a6, "docs", "dev", "ship-manifest.json")),
              "有列失敗 → manifest 那列不寫(版本不會比實際散發的檔還新)")
        left = [n for d, _x, fs in os.walk(a6) for n in fs if n.startswith(".devflow-upgrade-")]
        check(not left, "失敗後沒有留下暫存檔")

    # manifest 列是最後一筆寫入
    a7 = os.path.join(work, "a7"); os.makedirs(a7)
    rc, out, err = run("--root", a7, "--pack", pack, "--apply")
    wl = [l for l in out.splitlines() if l.startswith("  寫入  ")]
    check(wl and wl[-1].endswith("docs/dev/ship-manifest.json"), "manifest 自己那列排在最後寫入")

    # ── ⑩ baseline 同步(docs/dev/.devflow-baseline/ 對應路徑)───────────────────────
    # 起因(採用現場回報):--apply 只寫 destination、不更新 baseline 裡的基準副本 → baseline 停在舊版,
    # 下次 upgrade 把使用者根本沒改的檔判成「本地 ≠ baseline = 需同意」。語意見腳本檔頭:baseline = 上次散發的
    # 上游新內容。只在 baseline 目錄已存在時同步;不存在不建立(過渡態)。
    print("-- ⑩ baseline 同步 --")

    def bl(proj, dest):
        return os.path.join(proj, "docs", "dev", ".devflow-baseline", *dest[len("docs/dev/"):].split("/"))

    def src_of(pk, row):
        return open(os.path.join(pk, *row["source"].split("/")), "rb").read()

    docs_rows = [r for r in rows if r["destination"].startswith("docs/dev/")]
    # (a) 無 baseline 目錄:--apply 後仍沒有(不建立只含一部分檔的 baseline)
    a10n = os.path.join(work, "a10n"); os.makedirs(a10n)
    rc, out, err = run("--root", a10n, "--pack", pack, "--apply")
    check(rc == 0 and not os.path.exists(os.path.join(a10n, "docs", "dev", ".devflow-baseline")),
          "無 baseline 目錄(過渡態)--apply 不建立 baseline", out[-200:])
    check("baseline:docs/dev/.devflow-baseline/ 不存在" in out, "輸出明說 baseline 不存在、不建立")
    # (b) 有 baseline(舊版)+ 本地 = 舊版;方法包升版;一份本地客製
    a10 = os.path.join(work, "a10"); os.makedirs(a10)
    run("--root", a10, "--pack", pack, "--apply")
    for r in docs_rows:
        b = bl(a10, r["destination"]); os.makedirs(os.path.dirname(b), exist_ok=True)
        shutil.copyfile(os.path.join(a10, *r["destination"].split("/")), b)
        os.chmod(b, 0o644)  # 舊 baseline 的權限不一定對;baseline 只比內容,被更新時才依 manifest mode 寫
    readme_b = os.path.join(a10, "docs", "dev", ".devflow-baseline", "README.md")
    open(readme_b, "wb").write(b"stripped readme baseline\n")
    pack10 = make_pack("pack10")
    for rel in ("diagir.py", "devflow_atomic.py", "build-gate-twin.py"):
        with open(os.path.join(pack10, "scripts", rel), "ab") as f:
            f.write(b"\n# upstream v2 for " + rel.encode() + b"\n")
    custom = os.path.join(a10, "docs", "dev", "tools", "devflow_atomic.py")
    with open(custom, "ab") as f:
        f.write(b"\n# my edit\n")
    custom_b = open(custom, "rb").read()
    old_twin_baseline = open(bl(a10, "docs/dev/tools/build-gate-twin.py"), "rb").read()
    snap_b = snapshot(os.path.join(a10, "docs", "dev", ".devflow-baseline"))
    rc, out, err = run("--root", a10, "--pack", pack10)
    check(rc == 0 and snapshot(os.path.join(a10, "docs", "dev", ".devflow-baseline")) == snap_b,
          "dry-run 不動 baseline", out[-200:])
    check("baseline 同步" in out and "更新 3" in out, "dry-run 預告 baseline 同步:更新 3(三個有改的 tools)", next((l for l in out.splitlines() if "baseline 同步" in l), ""))
    rc, out, err = run("--root", a10, "--pack", pack10, "--apply")
    check(rc == 0 and "baseline 同步完成:寫入 3、失敗 0" in out, "--apply 後 baseline 同步:寫入 3、失敗 0", out[-300:])
    check(open(bl(a10, "docs/dev/tools/build-gate-twin.py"), "rb").read() == src_of(pack10, next(r for r in rows if r["destination"].endswith("tools/build-gate-twin.py")))
          and open(bl(a10, "docs/dev/tools/build-gate-twin.py"), "rb").read() != old_twin_baseline,
          "baseline/tools/build-gate-twin.py 換成方法包新內容(不再是舊版)")
    check(all(open(bl(a10, r["destination"]), "rb").read() == src_of(pack10, r) for r in docs_rows),
          "baseline 裡每個 manifest 列(docs/dev/ 底下)= 方法包上游新內容(逐位元組)")
    check(open(custom, "rb").read() == custom_b, "本地客製的檔仍被跳過、內容不變")
    check(open(bl(a10, "docs/dev/tools/devflow_atomic.py"), "rb").read() == src_of(pack10, next(r for r in rows if r["destination"].endswith("tools/devflow_atomic.py"))),
          "客製被跳過時 baseline 仍取上游新內容(不取本地現況;SKILL 的 baseline 語意)")
    check(open(readme_b, "rb").read() == b"stripped readme baseline\n", "baseline/README.md(不在 manifest 列)不被碰")
    twin_b = bl(a10, "docs/dev/tools/build-gate-twin.py")
    check(stat.S_IMODE(os.stat(twin_b).st_mode) == 0o755, "被更新的 baseline 副本 mode 依 manifest 列(build-gate-twin.py 為 755)")
    left = [n for d, _x, fs in os.walk(a10) for n in fs if n.startswith(".devflow-upgrade-")]
    check(not left, "baseline 同步後沒有留下暫存檔")
    # 下一輪:自動被判成「母版改寫」而不是「需同意」(修前 baseline 停在舊版 → 全部誤判客製)
    pack11 = make_pack("pack11")
    with open(os.path.join(pack11, "scripts", "build-gate-twin.py"), "ab") as f:
        f.write(b"\n# upstream v3\n")
    rc, out, err = run("--root", a10, "--pack", pack11)
    lt = next((l for l in out.splitlines() if "tools/build-gate-twin.py" in l), "")
    check("母版改寫" in lt and "需同意" not in lt, "再升一版:沒改過的 build-gate-twin.py 判成母版改寫(不是誤判需同意)", lt)
    # 同步後再跑一次(用同一個 pack10):baseline 全部相同、冪等
    rc, out, err = run("--root", a10, "--pack", pack10)
    check("新增 0、更新 0" in out and "baseline 同步" in out, "同一方法包再跑:baseline 同步 新增 0、更新 0(冪等)", next((l for l in out.splitlines() if "baseline 同步" in l), ""))
    # (c) baseline 缺某檔(舊版 baseline 沒收這個檔)→ 新增
    os.remove(bl(a10, "docs/dev/tools/diagir.py"))
    rc, out, err = run("--root", a10, "--pack", pack10, "--apply")
    check(rc == 0 and os.path.isfile(bl(a10, "docs/dev/tools/diagir.py")), "baseline 缺檔 → --apply 補上(新增)", out[-200:])
    # (d) 寫入失敗 → 不同步 baseline
    if not (hasattr(os, "geteuid") and os.geteuid() == 0):
        a10f = os.path.join(work, "a10f")
        os.makedirs(os.path.join(a10f, "docs", "dev", "tools", "devflow_jev"))
        os.makedirs(os.path.join(a10f, "docs", "dev", ".devflow-baseline"))
        os.chmod(os.path.join(a10f, "docs", "dev", "tools", "devflow_jev"), 0o555)
        try:
            rc, out, err = run("--root", a10f, "--pack", pack, "--apply")
        finally:
            os.chmod(os.path.join(a10f, "docs", "dev", "tools", "devflow_jev"), 0o755)
        check(rc == 1 and snapshot(os.path.join(a10f, "docs", "dev", ".devflow-baseline")) == {} and "不同步 baseline" in out,
              "有列寫入失敗 → baseline 一個檔都不同步", "rc=%s %s" % (rc, out[-200:]))
    # (e) baseline 路徑防跳脫:baseline/tools 是 symlink 到專案外 → exit 2、外面不多檔、整批不寫
    out_dir = os.path.join(work, "outside10"); os.makedirs(out_dir)
    a10s = os.path.join(work, "a10s")
    os.makedirs(os.path.join(a10s, "docs", "dev", ".devflow-baseline"))
    os.symlink(out_dir, os.path.join(a10s, "docs", "dev", ".devflow-baseline", "tools"))
    rc, out, err = run("--root", a10s, "--pack", pack, "--apply")
    check(rc == 2 and os.listdir(out_dir) == [] and not os.path.exists(os.path.join(a10s, "docs", "dev", "tools")),
          "baseline/tools 是 symlink 指到專案外 → exit 2、外面沒多檔、docs/dev/tools 也沒寫(整批先驗)", "rc=%s %s" % (rc, err[:200]))
    # (f) baseline 目錄本身是 symlink → 視為不存在(不跟著寫到外面)
    out_dir2 = os.path.join(work, "outside10b"); os.makedirs(out_dir2)
    a10l = os.path.join(work, "a10l"); os.makedirs(os.path.join(a10l, "docs", "dev"))
    os.symlink(out_dir2, os.path.join(a10l, "docs", "dev", ".devflow-baseline"))
    rc, out, err = run("--root", a10l, "--pack", pack, "--apply")
    check(os.listdir(out_dir2) == [], "baseline 目錄本身是 symlink → 不跟著寫到專案外", "rc=%s" % rc)
    # (g) doctor 入口路徑正確:hooks/,不是 scripts/
    rc, out, err = run("--root", a10n, "--pack", pack)
    check("hooks/devflow-exec.sh" in out and "scripts/devflow-exec.sh" not in out and os.path.isfile(os.path.join(root, "hooks", "devflow-exec.sh")),
          "輸出的 doctor 入口是 <方法包>/hooks/devflow-exec.sh(不是 scripts/,且該檔真的存在)")

    # ── ⑧ 只標準庫(靜態)─────────────────────────────────────────────
    print("-- ⑧ 靜態 --")
    tree = ast.parse(open(tool, encoding="utf-8").read(), feature_version=(3, 9))
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module.split(".")[0])
    allowed = {"__future__", "argparse", "difflib", "os", "stat", "sys", "tempfile", "devflow_ship_manifest"}
    check(mods <= allowed, "只 import 標準庫(+ 同目錄的 devflow_ship_manifest):%s" % sorted(mods - allowed))

    # ── ⑨ 套完後 doctor ──────────────────────────────────────────────
    print("-- ⑨ doctor --")
    a9 = os.path.join(work, "a9"); os.makedirs(a9)
    run("--root", a9, "--pack", root, "--apply")
    r = subprocess.run([sys.executable, os.path.join(root, "hooks", "_doctor_impl.py"), a9],
                       cwd=a9, env=ENV, capture_output=True, text=True, timeout=300)
    o = r.stdout + r.stderr
    check("✓ ship-manifest" in o, "套完後 doctor ship-manifest 逐列 ✓", next((l for l in o.splitlines() if "ship-manifest" in l), ""))
    check("✓ ship-deps" in o and "✗ ship-deps" not in o, "套完後 doctor ship-deps ✓")
finally:
    shutil.rmtree(work, ignore_errors=True)

total = passed + failed
if total < MIN_CASES:
    print("FATAL: 案例數 %d 低於下限 %d(案例被刪?)" % (total, MIN_CASES), file=sys.stderr)
    sys.exit(2)
print("=== test-upgrade-manifest:%d/%d ===" % (passed, total))
sys.exit(0 if failed == 0 else 1)
PY
