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
#   ⑦ 不留暫存檔;⑧ 只用標準庫(靜態);⑨ 套完後 doctor 的 ship-manifest／ship-deps 皆 ✓;
#   ⑫ `_templates/*` 納入升級與 doctor 內容雜湊(v3.26.7;3.26.6 改了 4-spec.md 而 manifest 不含模板,
#      採用專案只能手動同步):S1 本地 = baseline → 母版改寫、覆蓋並更新 baseline;S2 本地自改 → 需同意、預設不覆蓋、
#      baseline 照現行規則;S3 baseline 沒有此模板且被跳過 → baseline 不新增(v3.26.4);S4 doctor／check-ship-manifest
#      對模板內容不符會報出;S5 dry-run 不寫任何檔;3.26.6(manifest 無模板列)→ 3.26.7 的實際升級;
#      對照組:同一組情境用「manifest 排除模板」的 3.26.6 方法包(測試內臨時組出,正式碼沒有開關)跑,必須紅。
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
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

root, tool = sys.argv[1], sys.argv[2]
MIN_CASES = 119
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


def run(*args, tool_path=None):
    r = subprocess.run([sys.executable, tool_path or tool] + list(args), env=ENV, capture_output=True, text=True, timeout=120)
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
    check("baseline 的乾淨替換" in out and "README" in out and "不在這支範圍" in out, "輸出列出不在這支範圍的項目(README 剝除版/baseline 乾淨替換/殘件…)")
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
        "docs/dev/_templates/my-own-template.md": b"mine\n", "src/app.py": b"print(1)\n", "CLAUDE.md": b"x\n",
    }
    for rel, data in extras.items():
        p = os.path.join(a4, *rel.split("/")); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)
    mt = {rel: os.stat(os.path.join(a4, *rel.split("/"))).st_mtime_ns for rel in extras}
    rc, out, err = run("--root", a4, "--pack", pack, "--apply")
    check(rc == 0, "有既有檔的專案 --apply 成功")
    check(all(open(os.path.join(a4, *rel.split("/")), "rb").read() == data for rel, data in extras.items()),
          "README／STATUS／自己的工具／baseline／自己的模板(不在 manifest)／原始碼／CLAUDE.md 內容完全不變")
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

    # ── ⑪ 「baseline 沒有此檔」被跳過 → baseline 也不新增(v3.26.4)──────────────────
    # 起因(Prism 在 docs/dev/ship-manifest.json 碰到):baseline 沒有此檔、本地 ≠ 上游、沒加 --include-custom →
    # 該列被跳過(本地檔不動),但 baseline 同步仍把上游新內容「新增」進去 → 專案檔舊版、baseline 新版,
    # 下一輪 dry-run 理由變成「本地內容與 baseline 不同(本地客製)」,把沒客製的檔誤判成客製。
    # 本節以同一份情境 scenario_skip() 跑兩次:正式腳本必須全過;「舊寫法」(測試時複製腳本、移除新判斷的臨時對照組,
    # 正式程式碼沒有任何開關)必須讓 baseline 被誤新增而失敗 —— 證明這組測試抓得到 bug。
    print("-- ⑪ baseline 沒有此檔且被跳過 → baseline 不新增 --")
    T_NOBASE = "docs/dev/tools/diagir.py"            # baseline 沒有此檔、本地 ≠ 上游(Prism 的情境)
    T_CUSTOM = "docs/dev/tools/devflow_atomic.py"    # baseline 有舊版、本地客製(SKILL:baseline 仍取上游新內容)
    T_SAME = "docs/dev/tools/publish-pages.sh"       # baseline 沒有此檔、本地 = 上游(本來就相同:baseline 照舊新增)

    def scenario_skip(tag, tool_path, include_custom):
        """回傳 dict:專案 + 各項觀察。baseline 目錄在、缺 T_NOBASE 與 T_SAME、T_CUSTOM 有舊版 baseline。"""
        proj = os.path.join(work, "a11-" + tag); os.makedirs(proj)
        run("--root", proj, "--pack", pack, "--apply", tool_path=tool_path)      # 本地 = 舊版
        for r in docs_rows:
            if r["destination"] in (T_NOBASE, T_SAME):
                continue
            b = bl(proj, r["destination"]); os.makedirs(os.path.dirname(b), exist_ok=True)
            shutil.copyfile(os.path.join(proj, *r["destination"].split("/")), b)  # baseline = 舊版
        pk = make_pack("pack11-" + tag)
        for rel in ("diagir.py", "devflow_atomic.py"):
            with open(os.path.join(pk, "scripts", rel), "ab") as f:
                f.write(b"\n# upstream new for " + rel.encode() + b"\n")
        cust_p = os.path.join(proj, *T_CUSTOM.split("/"))
        with open(cust_p, "ab") as f:
            f.write(b"\n# my edit\n")
        local_nobase = open(os.path.join(proj, *T_NOBASE.split("/")), "rb").read()
        local_custom = open(cust_p, "rb").read()
        args = ["--root", proj, "--pack", pk]
        if include_custom:
            args.append("--include-custom")
        rc_d, out_d, _ = run(*args, tool_path=tool_path)                          # dry-run(預告)
        rc, out, err = run(*args, "--apply", tool_path=tool_path)
        rc2, out2, _ = run("--root", proj, "--pack", pk, tool_path=tool_path)    # 第二次 dry-run(不帶 --include-custom)
        row_of = lambda o, t: next((l for l in o.splitlines() if l.startswith("  變更  ") and t in l or l.startswith("  相同  ") and t in l), "")
        return {"proj": proj, "pk": pk, "rc": rc, "out": out, "err": err, "dry": out_d, "out2": out2,
                "local_nobase": local_nobase, "local_custom": local_custom, "row2": row_of(out2, T_NOBASE),
                "custom2": row_of(out2, T_CUSTOM),
                "up": lambda t: open(os.path.join(pk, "scripts", t), "rb").read()}

    def nobase_file(proj, t):
        return bl(proj, t)

    # (1)(2) 不加 --include-custom
    r1 = scenario_skip("real", None, False)
    pj = r1["proj"]
    check(r1["rc"] == 0 and ("跳過  " + T_NOBASE) in r1["out"], "(1) 不加 --include-custom --apply:該列被跳過、exit 0", "rc=%s %s" % (r1["rc"], r1["out"][-300:]))
    check(not os.path.exists(nobase_file(pj, T_NOBASE)), "(1) baseline 沒有此檔且被跳過 → baseline 仍沒有此檔(不新增)")
    check(open(os.path.join(pj, *T_NOBASE.split("/")), "rb").read() == r1["local_nobase"], "(1) 本地檔未改")
    check("需同意" in r1["row2"] and "baseline 沒有此檔" in r1["row2"] and "本地內容與 baseline 不同" not in r1["row2"],
          "(1) 第二次 dry-run 理由仍是「baseline 沒有此檔」(沒被誤判成本地客製)", r1["row2"])
    check("baseline 不新增  " + T_NOBASE in r1["dry"] and "不新增 1" in r1["dry"],
          "(1) dry-run 預告:baseline 不新增這列(逐列標出)", r1["dry"][-400:])
    check(("baseline 未同步  " + T_NOBASE) in r1["out"] and "baseline 沒有此檔且這列被跳過" in r1["out"] and "--include-custom" in r1["out"].split("baseline 未同步")[-1],
          "(1) --apply 輸出看得出這列 baseline 沒同步、以及原因與解法", r1["out"][-500:])
    check("不新增 1" in r1["out"], "(1) --apply 的 baseline 同步完成行帶出「不新增 1」")
    check(open(bl(pj, T_CUSTOM), "rb").read() == r1["up"]("devflow_atomic.py"),
          "(2) 本地客製(baseline 有舊版)被跳過 → baseline 仍更新成上游新內容(守住 SKILL 規定)")
    check(open(os.path.join(pj, *T_CUSTOM.split("/")), "rb").read() == r1["local_custom"], "(2) 本地客製的檔未被動")
    check("baseline 未同步  " + T_CUSTOM not in r1["out"] and "baseline 不新增  " + T_CUSTOM not in r1["dry"],
          "(2) 本地客製列不被標成「baseline 不新增」(例外只限 baseline 沒有此檔)")
    check("本地內容與 baseline 不同" in r1["custom2"], "(2) 第二次 dry-run:客製列理由仍是本地客製", r1["custom2"])
    check(open(bl(pj, T_SAME), "rb").read() == open(os.path.join(pack, "scripts", "publish-pages.sh"), "rb").read(),
          "本來就和上游相同、baseline 沒有此檔 → baseline 照舊新增(行為不變)")
    # (3) 加 --include-custom:該列寫入、baseline 新增
    r3 = scenario_skip("incl", None, True)
    pj3 = r3["proj"]
    check(r3["rc"] == 0 and ("寫入  " + T_NOBASE) in r3["out"] and "baseline 未同步" not in r3["out"] and "不新增 0" in r3["dry"],
          "(3) 加 --include-custom:該列寫入、不出現「baseline 未同步」、dry-run 預告不新增 0", r3["out"][-300:])
    check(open(os.path.join(pj3, *T_NOBASE.split("/")), "rb").read() == r3["up"]("diagir.py")
          and open(nobase_file(pj3, T_NOBASE), "rb").read() == r3["up"]("diagir.py"),
          "(3) 本地檔 = 上游新內容、baseline 新增且 = 上游新內容")
    check(open(bl(pj3, T_CUSTOM), "rb").read() == r3["up"]("devflow_atomic.py")
          and open(os.path.join(pj3, *T_CUSTOM.split("/")), "rb").read() == r3["up"]("devflow_atomic.py"),
          "(3) 本地客製列也覆蓋、baseline = 上游新內容")
    # 母版改寫/新增列的 baseline 行為不變:已由 ⑩(母版改寫+新增)覆蓋

    # (4) 對照組:臨時複製腳本、用 replace 移除新判斷(舊寫法);正式程式碼沒有任何後門開關
    old_tool_dir = os.path.join(work, "old-tool"); os.makedirs(old_tool_dir)
    src_txt = open(tool, encoding="utf-8").read()
    new_expr = '"不新增" if (note == NOTE_NO_BASELINE_FILE and is_skipped(state, note, include_custom)) else "新增"'
    check(src_txt.count(new_expr) == 1, "(4) 對照組前置:正式腳本裡恰有一處新判斷可被移除(patch 不會悄悄落空)", str(src_txt.count(new_expr)))
    open(os.path.join(old_tool_dir, "devflow-upgrade-manifest.py"), "w", encoding="utf-8").write(src_txt.replace(new_expr, '"新增"'))
    shutil.copyfile(os.path.join(os.path.dirname(tool), "devflow_ship_manifest.py"), os.path.join(old_tool_dir, "devflow_ship_manifest.py"))
    old_tool = os.path.join(old_tool_dir, "devflow-upgrade-manifest.py")
    ro = scenario_skip("old", old_tool, False)
    bug_reproduced = os.path.exists(nobase_file(ro["proj"], T_NOBASE))
    check(bug_reproduced, "(4) 對照組(舊寫法)重現 bug:baseline 被誤新增上游新內容 —— 同一測試 (1) 會失敗")
    check("本地內容與 baseline 不同" in ro["row2"] and "baseline 沒有此檔" not in ro["row2"],
          "(4) 對照組:第二次 dry-run 理由被誤判成「本地客製」(Prism 現場症狀)", ro["row2"])
    check(open(os.path.join(ro["proj"], *T_NOBASE.split("/")), "rb").read() == ro["local_nobase"] and "baseline 不新增" not in ro["dry"],
          "(4) 對照組:本地檔未改、且沒有「baseline 不新增」提示(舊行為)")

    # ── ⑫ `_templates/*` 納入升級與 doctor 內容雜湊(v3.26.7)─────────────────────────
    # 起因:manifest 刻意不含 `_templates/*`,3.26.6 改了 `_templates/4-spec.md`(g2r_jev risk 可為小數),
    # 升級腳本不同步模板、doctor 的 v2 內容雜湊也看不到模板落差,採用專案只能手動同步。
    # 現在模板是 manifest 的 1:1 列(`_templates/X` → `docs/dev/_templates/X`、644),走和其他列完全相同的規則。
    # 對照組:同一組情境改用「manifest 排除模板」的 3.26.6 方法包(測試內臨時組出;正式碼沒有任何開關),必須紅。
    print("-- ⑫ _templates/* 納入升級與 doctor --")
    sm_spec = importlib.util.spec_from_file_location("devflow_ship_manifest", os.path.join(root, "scripts", "devflow_ship_manifest.py"))
    sm_mod = importlib.util.module_from_spec(sm_spec)
    sm_spec.loader.exec_module(sm_mod)
    TPL_ROWS = [r for r in rows if r["source"].startswith("_templates/")]
    T4, T5, TJ = "docs/dev/_templates/4-spec.md", "docs/dev/_templates/5-tasks.md", "docs/dev/_templates/jev.yaml"
    check(TPL_ROWS and all(r["destination"] == "docs/dev/" + r["source"] and r["mode"] == "644" for r in TPL_ROWS),
          "manifest 模板列都是 1:1(_templates/X → docs/dev/_templates/X)、mode 644")
    check(sorted(r["source"][len("_templates/"):] for r in TPL_ROWS) == sorted(os.listdir(os.path.join(root, "_templates")))
          and any(r["destination"] == TJ for r in TPL_ROWS),
          "模板列 = 母版 _templates/ 的全部檔,含 jev.yaml(opt-in 範本也納入)")
    tool_src = open(tool, encoding="utf-8").read()
    check("skip-templates" not in tool_src and "exclude-templates" not in tool_src and "no-templates" not in tool_src
          and "environ" not in tool_src,
          "正式腳本沒有排除模板的旗標／環境變數後門(對照組只在測試內組出)")

    NEW4 = open(os.path.join(root, "_templates", "4-spec.md"), "rb").read()
    OLD4 = NEW4.replace("risk=<0..3,可小數>".encode(), "risk=<0-3>".encode())
    check(OLD4 != NEW4, "測試前置:能由現行 4-spec 還原出 3.26.6 前的舊版(g2r_jev risk 欄位寫法)")

    def make_pack_3266(name):
        """3.26.6 的方法包:manifest 沒有模板列(版本指紋與契約依實際內容重算,doctor 看起來一致),_templates/4-spec.md 是舊版。"""
        pk = make_pack(name)
        scratch = os.path.join(work, name + "-scratch"); os.makedirs(scratch)
        run("--root", scratch, "--pack", pk, "--apply")
        mp = os.path.join(pk, "docs", "dev", "ship-manifest.json")
        data = jload(mp)
        data["files"] = [r for r in data["files"] if not r["source"].startswith("_templates/")]
        data["version"] = sm_mod.compute_version(data, scratch)
        json.dump(data, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        cp = os.path.join(pk, "devflow-contract.json")
        txt = open(cp, encoding="utf-8").read()
        open(cp, "w", encoding="utf-8").write(re.sub(r'("ship_manifest_version"\s*:\s*")[^"]*(")', lambda m: m.group(1) + data["version"] + m.group(2), txt, count=1))
        open(os.path.join(pk, "_templates", "4-spec.md"), "wb").write(OLD4)
        shutil.rmtree(scratch)
        return pk

    def install_templates(proj, with_baseline=True, old=True):
        """模擬 dev-setup 的 `_templates/` 整目錄複製與 baseline 快照(上一版散發下去的內容;old=True 時 4-spec.md 是舊版)。"""
        for r in TPL_ROWS:
            data = open(os.path.join(root, *r["source"].split("/")), "rb").read()
            if old and r["destination"] == T4:
                data = OLD4
            for dst in ([os.path.join(proj, *r["destination"].split("/"))] +
                        ([bl(proj, r["destination"])] if with_baseline else [])):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, "wb").write(data)
                os.chmod(dst, 0o644)

    def tpl_project(tag, pk, with_baseline=True, old=True):
        """採用專案:先套 pk 的 manifest 列(舊版內容),再裝模板與 baseline(其他列的 baseline = 當時本地)。"""
        proj = os.path.join(work, "t12-" + tag); os.makedirs(proj)
        run("--root", proj, "--pack", pk, "--apply")
        if with_baseline:
            for r in docs_rows:
                if r["source"].startswith("_templates/"):
                    continue
                b = bl(proj, r["destination"]); os.makedirs(os.path.dirname(b), exist_ok=True)
                shutil.copyfile(os.path.join(proj, *r["destination"].split("/")), b)
        install_templates(proj, with_baseline, old)
        return proj

    def rd(path):
        return open(path, "rb").read() if os.path.exists(path) else None

    def prow(o, dest):
        return next((l for l in o.splitlines() if dest in l and (l.startswith("  變更  ") or l.startswith("  相同  ") or l.startswith("  新增  "))), "")

    def doctor_out(proj):
        r = subprocess.run([sys.executable, os.path.join(root, "hooks", "_doctor_impl.py"), proj],
                           cwd=proj, env=ENV, capture_output=True, text=True, timeout=300)
        return r.stdout + r.stderr

    MASTER_FILES = ["docs/dev/ship-manifest.json", "devflow-contract.json", "docs/dev/devflow-contract.json",
                    "guides/guide-dev-flow.html", "scripts/devflow_ship_manifest.py", "scripts/check-ship-manifest.sh"]

    def master_copy(tag):
        """check-ship-manifest.sh 需要的最小母版:manifest/契約/散發檔(source 與母版內存在的 destination 副本)/模板/檔案地圖。"""
        m = os.path.join(work, tag)
        need = set(MASTER_FILES)
        for r in rows:
            need.add(r["source"])
            if os.path.isfile(os.path.join(root, *r["destination"].split("/"))):
                need.add(r["destination"])
        need |= {"_templates/" + n for n in os.listdir(os.path.join(root, "_templates"))}
        for rel in sorted(need):
            dst = os.path.join(m, *rel.split("/")); os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(root, *rel.split("/")), dst)
        return m

    def scenarios(pk, rep, master=True):
        """同一組 S1~S5 + 母版端檢查。pk = 「新版」方法包;rep(label, cond, detail) 記結果(真跑記 check,對照組只收集)。"""
        snap = lambda proj: snapshot(proj)
        # S1:baseline 有模板、本地 = baseline(沒自改)、上游較新 → 母版改寫;--apply 覆蓋並更新 baseline
        p1 = tpl_project("s1-" + os.path.basename(pk), pk)
        before = snap(p1)
        rc, out, err = run("--root", p1, "--pack", pk)
        rep("S5 dry-run 不寫任何檔(專案含 baseline 的整棵樹逐位元組不變)", rc == 0 and snap(p1) == before, out[-200:] + err)
        row = prow(out, T4)
        rep("S1 dry-run:本地 = baseline 的 4-spec.md 標「母版改寫」(不是需同意)", "變更" in row and "母版改寫" in row and "需同意" not in row, row)
        rc, out, err = run("--root", p1, "--pack", pk, "--apply")
        local4, base4 = rd(os.path.join(p1, *T4.split("/"))), rd(bl(p1, T4))
        rep("S1 --apply:本地 4-spec.md 覆蓋成上游新內容", rc == 0 and local4 == NEW4, "rc=%s" % rc)
        rep("S1 --apply:baseline 的 _templates/4-spec.md 同步成上游新內容", base4 == NEW4)
        rc, out, err = run("--root", p1, "--pack", pk)
        rep("S1 再跑 dry-run:模板列全部相同(冪等)", all(prow(out, r["destination"]).startswith("  相同  ") for r in TPL_ROWS), prow(out, T4))
        # S2:本地自改模板 → 需同意、預設不覆蓋;baseline 照現行規則(仍取上游新內容);--include-custom 才覆蓋
        p2 = tpl_project("s2-" + os.path.basename(pk), pk)
        edited = OLD4 + b"\n<!-- my local customization -->\n"
        open(os.path.join(p2, *T4.split("/")), "wb").write(edited)
        rc, out, err = run("--root", p2, "--pack", pk)
        row = prow(out, T4)
        rep("S2 dry-run:自改的模板標「需同意」(本地客製)", "需同意" in row and "本地客製" in row, row)
        rc, out, err = run("--root", p2, "--pack", pk, "--apply")
        rep("S2 --apply 預設不覆蓋自改的模板、輸出「跳過」", rd(os.path.join(p2, *T4.split("/"))) == edited and ("跳過  " + T4) in out, out[-300:])
        rep("S2 被跳過的本地客製列:baseline 仍取上游新內容(現行行為不變,owner 2026-10-19 維持)", rd(bl(p2, T4)) == NEW4)
        rc, out, err = run("--root", p2, "--pack", pk, "--apply", "--include-custom")
        rep("S2 --include-custom 才覆蓋自改的模板", rd(os.path.join(p2, *T4.split("/"))) == NEW4, out[-200:])
        # S3:baseline 沒有此模板、本地 ≠ 上游 → 需同意:baseline 沒有此檔;被跳過 → baseline 不新增(v3.26.4)
        p3 = tpl_project("s3-" + os.path.basename(pk), pk)
        os.remove(bl(p3, T4))
        rc, out, err = run("--root", p3, "--pack", pk)
        row = prow(out, T4)
        rep("S3 dry-run:baseline 沒有此模板 → 「需同意:baseline 沒有此檔」", "需同意" in row and "baseline 沒有此檔" in row, row)
        rep("S3 dry-run 預告「baseline 不新增」這個模板", ("baseline 不新增  " + T4) in out, out[-300:])
        rc, out, err = run("--root", p3, "--pack", pk, "--apply")
        rep("S3 --apply:被跳過、本地不動、baseline 不新增該模板",
            rd(os.path.join(p3, *T4.split("/"))) == OLD4 and not os.path.exists(bl(p3, T4)) and ("baseline 未同步  " + T4) in out, out[-400:])
        rc, out, err = run("--root", p3, "--pack", pk)
        row = prow(out, T4)
        rep("S3 第二次 dry-run:理由仍是「baseline 沒有此檔」(沒被誤判成本地客製)", "baseline 沒有此檔" in row and "本地內容與 baseline 不同" not in row, row)
        rc, out, err = run("--root", p3, "--pack", pk, "--apply", "--include-custom")
        rep("S3 --include-custom:寫入且 baseline 一併新增", rd(os.path.join(p3, *T4.split("/"))) == NEW4 and rd(bl(p3, T4)) == NEW4, out[-200:])
        # S4:doctor 對模板內容不符會報出(整棵由 pk 散發的專案,模板為新內容)
        p4 = os.path.join(work, "t12-s4-" + os.path.basename(pk)); os.makedirs(p4)
        run("--root", p4, "--pack", pk, "--apply")
        install_templates(p4, with_baseline=False, old=False)
        o = doctor_out(p4)
        rep("S4 doctor:模板與當次散發一致 → ship-manifest ✓", "✓ ship-manifest:" in o, next((l for l in o.splitlines() if "ship-manifest" in l), ""))
        t4p = os.path.join(p4, *T4.split("/"))
        open(t4p, "ab").write(b"\n<!-- local drift -->\n")
        o = doctor_out(p4)
        rep("S4 doctor:模板內容與散發不同 → ✗ ship-manifest(內容雜湊重算不符,指路 upgrade 預覽)",
            "✗ ship-manifest" in o and "重算" in next((l for l in o.splitlines() if "✗ ship-manifest" in l), ""), next((l for l in o.splitlines() if "ship-manifest" in l), ""))
        open(t4p, "wb").write(NEW4)
        os.remove(os.path.join(p4, *T5.split("/")))
        o = doctor_out(p4)
        rep("S4 doctor:模板缺檔 → ✗ ship-manifest 並點名", "✗ ship-manifest" in o and T5 in o, next((l for l in o.splitlines() if "ship-manifest" in l), ""))
        # S4 母版端:check-ship-manifest.sh 對 _templates 內容改了沒重算指紋、新模板沒記帳都會紅
        # (對照組不跑這段:3.26.6 母版沒有這支守衛可比,指紋盲區已由 check-ship-manifest.sh 自己的「對照」案釘住)
        if not master:
            return
        m = master_copy("m12-" + os.path.basename(pk))
        mdata_rows = jload(os.path.join(pk, "docs", "dev", "ship-manifest.json"))["files"]
        shutil.copyfile(os.path.join(pk, "docs", "dev", "ship-manifest.json"), os.path.join(m, "docs", "dev", "ship-manifest.json"))
        shutil.copyfile(os.path.join(pk, "devflow-contract.json"), os.path.join(m, "devflow-contract.json"))
        shutil.copyfile(os.path.join(pk, "devflow-contract.json"), os.path.join(m, "docs", "dev", "devflow-contract.json"))
        def run_check(mm):
            r = subprocess.run(["bash", os.path.join(mm, "scripts", "check-ship-manifest.sh"), mm], env=ENV, capture_output=True, text=True, timeout=300)
            return r.returncode, r.stdout + r.stderr
        m4 = os.path.join(m, "_templates", "4-spec.md")
        # 母版端的模板內容以 pk 為準(3.26.6 方法包的 4-spec 是舊版;對照組的母版就是 3.26.6 母版)
        shutil.copyfile(os.path.join(pk, "_templates", "4-spec.md"), m4)
        rc, out = run_check(m)
        rep("S4 母版端 check-ship-manifest.sh:基線(模板內容與指紋一致)→ exit 0", rc == 0, out[-300:])
        open(m4, "ab").write(b"\n<!-- edited without --refresh -->\n")
        rc, out = run_check(m)
        rep("S4 母版端:只改 _templates/4-spec.md 沒重算指紋 → exit 1 且 manifest.version 過期", rc == 1 and "manifest.version 過期" in out, "rc=%s %s" % (rc, out[-300:]))
        shutil.copyfile(os.path.join(pk, "_templates", "4-spec.md"), m4)
        open(os.path.join(m, "_templates", "zz-new-template.md"), "w").write("new template without manifest row\n")
        rc, out = run_check(m)
        rep("S4 母版端:新增模板沒進 manifest → exit 1 且反向點名", rc == 1 and ("_templates/zz-new-template.md" in out) and any(r["source"].startswith("_templates/") for r in mdata_rows), "rc=%s %s" % (rc, out[-300:]))

    results = []
    scenarios(pack, lambda label, cond, detail="": (check(cond, label, detail), results.append(cond)))
    check(all(results) and len(results) >= 18, "S1~S5 情境全過(%d 項斷言)" % len(results))

    # ── 3.26.6(manifest 沒有模板列)→ 3.26.7 的實際升級 ───────────────────────────
    pack_old = make_pack_3266("pack-3266")
    check(not any(r["source"].startswith("_templates/") for r in jload(os.path.join(pack_old, "docs", "dev", "ship-manifest.json"))["files"]),
          "前置:3.26.6 方法包的 manifest 沒有任何模板列(重現舊狀態)")
    adopter = os.path.join(work, "adopter-3266"); os.makedirs(adopter)
    rc, out, err = run("--root", adopter, "--pack", pack_old, "--apply")
    check(rc == 0 and not os.path.exists(os.path.join(adopter, "docs", "dev", "_templates")),
          "3.26.6 的腳本只處理 manifest 列:模板由 dev-setup 整目錄複製,腳本沒碰", out[-200:])
    for r in docs_rows:
        if r["source"].startswith("_templates/"):
            continue
        b = bl(adopter, r["destination"]); os.makedirs(os.path.dirname(b), exist_ok=True)
        shutil.copyfile(os.path.join(adopter, *r["destination"].split("/")), b)
    install_templates(adopter, True, True)                     # 3.26.6 安裝下去的模板與 baseline(4-spec.md 舊版)
    custom5 = open(os.path.join(adopter, *T5.split("/")), "rb").read() + b"\n<!-- project customized 5-tasks -->\n"
    open(os.path.join(adopter, *T5.split("/")), "wb").write(custom5)
    o = doctor_out(adopter)
    check("✓ ship-manifest:" in o, "升級前:3.26.6 採用專案 doctor ship-manifest ✓(舊指紋看不到模板落差,這就是盲區)",
          next((l for l in o.splitlines() if "ship-manifest" in l), ""))
    rc, out, err = run("--root", adopter, "--pack", pack)
    check("母版改寫" in prow(out, T4) and "需同意" in prow(out, T5) and "本地客製" in prow(out, T5)
          and prow(out, TJ).startswith("  相同  ") and "baseline 不新增" not in out,
          "升到 3.26.7 dry-run:未自改的 4-spec.md = 母版改寫(自動同步)、自改的 5-tasks.md = 需同意、jev.yaml 相同",
          prow(out, T4) + " | " + prow(out, T5))
    rc, out, err = run("--root", adopter, "--pack", pack, "--apply")
    check(rc == 0 and rd(os.path.join(adopter, *T4.split("/"))) == NEW4 and rd(bl(adopter, T4)) == NEW4,
          "--apply:4-spec.md 自動同步成新內容、baseline 一併更新", out[-300:])
    check(rd(os.path.join(adopter, *T5.split("/"))) == custom5 and ("跳過  " + T5) in out,
          "--apply:自改的 5-tasks.md 沒被覆蓋(預設跳過,需同意)")
    check(rd(bl(adopter, T5)) == open(os.path.join(root, "_templates", "5-tasks.md"), "rb").read(),
          "自改且被跳過的 5-tasks.md:baseline 仍取上游新內容(現行行為不變)")
    o = doctor_out(adopter)
    check("✗ ship-manifest" in o and "重算" in next((l for l in o.splitlines() if "✗ ship-manifest" in l), ""),
          "自改模板未同意覆蓋 → doctor ✗ ship-manifest(與 docs/dev/tools 自改同一規則,指路 upgrade 預覽)",
          next((l for l in o.splitlines() if "ship-manifest" in l), ""))
    rc, out, err = run("--root", adopter, "--pack", pack, "--apply", "--include-custom")
    o = doctor_out(adopter)
    check(rc == 0 and rd(os.path.join(adopter, *T5.split("/"))) == open(os.path.join(root, "_templates", "5-tasks.md"), "rb").read()
          and "✓ ship-manifest:" in o,
          "同意覆蓋(--include-custom)後 → 5-tasks.md 還原、doctor ship-manifest ✓", next((l for l in o.splitlines() if "ship-manifest" in l), ""))

    # ── 對照組:「manifest 排除模板」的 3.26.6 方法包跑同一組情境 → 必須紅 ─────────────────────
    ctl = []
    scenarios(pack_old, lambda label, cond, detail="": ctl.append((label, cond)), master=False)
    red = [label for label, cond in ctl if not cond]
    check(len(red) >= 8 and any(l.startswith("S1 --apply:本地 4-spec.md") for l in red) and any(l.startswith("S4 doctor:模板內容與散發不同") for l in red),
          "對照組(manifest 排除模板)跑同一組情境:%d/%d 項斷言轉紅,含 S1 不覆蓋、S4 doctor 看不到模板被改" % (len(red), len(ctl)),
          "紅的:%s" % red)
    print("  (對照組轉紅 %d/%d:%s)" % (len(red), len(ctl), " | ".join(red)))

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
