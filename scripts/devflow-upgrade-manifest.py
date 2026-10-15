#!/usr/bin/env python3
# devflow-upgrade-manifest.py — 照 ship-manifest 把方法包的散發檔複製/更新進採用專案(只標準庫)。
#
# 為什麼需要:dev-setup upgrade 原本只有散文步驟(「對每一列 cp 後 chmod」),沒有可直接跑的腳本,
# 採用專案(Prism 回報)只能照 docs/dev/ship-manifest.json 手動逐檔複製 —— 容易漏列、漏 chmod、
# 漏建子目錄,而且漏了之後 doctor 的逐列驗證才會發現。這支把「manifest 列 → 採用專案」這一段做成
# 指令:預設 dry-run 列出差異,帶 --apply 才寫。
#
# 範圍(嚴格):只動 `<pack>/docs/dev/ship-manifest.json` 每一列的 destination,**一個檔都不多碰**。
#   不在這支的範圍(仍照 skills/dev-setup/SKILL.md 的 upgrade 段):
#   docs/dev/README.md 剝除版與 docs/dev/_templates/ 的複製、出廠殘件刪除
#   (devflow-upgrade-leftovers.sh;只做「新增/覆蓋」,上游已移除的舊工具檔不會刪)、README／_templates 的 baseline 快照、.gitignore、
#   knowledge index bootstrap。
#   baseline(docs/dev/.devflow-baseline/):語意 = 「上次 install/upgrade 散發下去的上游新內容」,下次 upgrade 拿它當
#   「上游舊版」做三方比對(本地 ≠ baseline ⇒ 本地客製)。所以 upgrade 成功後 baseline 必須跟著換成這次散發的內容
#   (SKILL install 步 8;使用者拒絕覆蓋客製時 baseline 仍取上游新內容,不取本地現況)。本腳本 --apply 在「全部列寫入
#   成功」之後,把 manifest 列(docs/dev/ 底下的,含 tools/)的**上游新內容**同步進 baseline 對應路徑;不寫 baseline 就會
#   留下過期基準,下次 upgrade 把使用者根本沒改的檔誤判成「需同意」。只在 baseline 目錄已存在時才同步:
#   不存在 = 過渡態(SKILL:全部視為本地客製),腳本不替人建立只含一部分檔的 baseline。
#   不做乾淨替換(不刪 baseline 裡上游已移除的舊檔)、不碰 README／_templates 的 baseline —— 那些仍照 SKILL 步 8。
#   **例外(v3.26.4):「需同意:baseline 沒有此檔」而這次被跳過的列,baseline 也不新增該檔。** 理由:這種列本地內容 ≠ 上游,
#   又因 baseline 沒有此檔而無從判斷是否本地客製;沒加 --include-custom 時本地檔不動,若 baseline 卻先收了上游新內容,
#   就變成「專案檔仍是舊版、baseline 是新版」,下一輪 dry-run 的理由會從「baseline 沒有此檔」變成
#   「本地內容與 baseline 不同(本地客製)」,把沒客製的檔誤判成客製(Prism 在 docs/dev/ship-manifest.json 碰到)。
#   不新增就保持原狀,下一輪理由仍是「baseline 沒有此檔」,等使用者同意(--include-custom 寫入後該列的 baseline 才一併新增)。
#   只有這一種跳過列有此例外:「需同意:本地內容與 baseline 不同(本地客製)」被跳過的列,baseline 仍取上游新內容
#   (SKILL 現行規定,行為不變);實際寫入的列、本來就和上游相同的列、無 baseline 目錄的過渡態也都不變。
#
# 每列的狀態:
#   新增  採用專案沒有這個檔
#   變更  有,但內容或權限(mode)與方法包不同。再依 baseline 分兩種:
#         母版改寫 —— 本地 = baseline(docs/dev/.devflow-baseline/ 的上游舊版),使用者沒改過,可直接覆蓋
#         需同意   —— 本地 ≠ baseline、baseline 沒有此檔、或根本沒有 baseline(過渡態,依 SKILL 一律視為
#                    可能的本地客製):--apply 預設**跳過**並列出,要連它一起覆蓋須加 --include-custom
#                    (dev-setup 規定逐檔徵得使用者同意後才覆蓋)
#   相同  內容與權限都一樣
# baseline 路徑 = docs/dev/.devflow-baseline/<destination 去掉開頭的 docs/dev/>。
# baseline 同步另有四種狀態(只在 baseline 目錄存在時):新增(baseline 沒有此檔)/ 更新(內容不同)/ 相同 /
# 不新增(上面 v3.26.4 例外:baseline 沒有此檔、該列這次被跳過 —— 輸出會逐列標出並說明原因)。
#
# 安全:
#   · 先驗全部列再動手:manifest 結構(缺欄/重複 destination/非 644|755/絕對路徑/..)沿用
#     scripts/devflow_ship_manifest.py 的 fail-closed 檢查;任何一列越界 → exit 2、一個檔都不寫。
#   · 路徑防跳脫:destination 只准落在專案根內(realpath 比對);路徑上任何一層已存在的 symlink、
#     destination 本身是 symlink 或目錄 → 拒絕(不跟著 symlink 寫到專案外);不准寫 .git/ 底下;
#     source 只准在方法包內的一般檔。--root 與 --pack 不可是同一處。
#   · 寫入是暫存檔 + os.replace(同目錄、單檔原子);失敗不留暫存檔。manifest 自己那一列
#     (docs/dev/ship-manifest.json)最後寫,且前面有任何一列寫入失敗就不寫 —— 採用專案的 manifest 版本
#     不會比實際散發的檔還新(doctor 的逐列驗證才看得出缺件,不會被蓋過去)。
#     baseline 同步在所有列之後、且只在沒有任何寫入失敗時才做;baseline 的路徑也走同一套防跳脫檢查
#     (整批先驗,越界 → exit 2、一個檔都不寫),不跟著 symlink 寫到專案外。
#
# 用法:
#   python3 <方法包根>/scripts/devflow-upgrade-manifest.py --root <專案根> [--pack <方法包根>]
#                                                         [--apply] [--include-custom] [--diff]
#   --root           採用專案根(預設:目前目錄)
#   --pack           方法包根(預設:本腳本所在的 scripts/ 的上一層 = ${DEVFLOW_ROOT})
#   --apply          真的寫入(新增 + 母版改寫;需同意的列預設跳過)。不帶 = dry-run,不動任何檔
#   --include-custom 連「需同意」的列一起覆蓋(只有在你已逐檔徵得使用者同意後才用)
#   --diff           對「變更」的文字檔印 unified diff(每檔最多 60 行),給使用者過目用
# doctor 入口:<方法包根>/hooks/devflow-exec.sh doctor(不是 scripts/)。
# exit:0 = dry-run 完成,或 --apply 全部成功(含有跳過的需同意列)/ 1 = --apply 有寫入失敗 /
#       2 = 用法或邊界違規(manifest 壞、路徑越界、root==pack…),未寫任何檔

from __future__ import print_function

import argparse
import difflib
import os
import stat
import sys
import tempfile

SELF_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SELF_DIR)
sys.dont_write_bytecode = True

BASELINE_REL = os.path.join("docs", "dev", ".devflow-baseline")
MANIFEST_DEST = "docs/dev/ship-manifest.json"
DIFF_MAX_LINES = 60
NOTE_NO_BASELINE_FILE = "需同意:baseline 沒有此檔,無法判斷是否本地客製"
BASELINE_SKIP_REASON = ("baseline 沒有此檔且這列被跳過、本地檔不動 —— baseline 也不新增,"
                        "否則下一輪會把沒客製的檔誤判成本地客製;徵得同意加 --include-custom 寫入後才一併新增")


class Boundary(Exception):
    """邊界違規:整批拒絕,不寫任何檔。"""


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


def _inside(path, base):
    base = os.path.realpath(base)
    real = os.path.realpath(path)
    return real == base or real.startswith(base + os.sep)


def check_destination(root, rel):
    """destination 必須落在 root 內:路徑上已存在的每一層都不是 symlink,destination 本身若存在
    必須是一般檔(不是 symlink / 目錄)。回傳絕對路徑;違規 raise Boundary。"""
    parts = rel.split("/")
    if parts[0] == ".git":
        raise Boundary("%s:不准寫 .git/ 底下" % rel)
    cur = root
    for i, part in enumerate(parts):
        cur = os.path.join(cur, part)
        last = (i == len(parts) - 1)
        if os.path.islink(cur):
            raise Boundary("%s:路徑上的 %s 是 symlink,拒絕(不跟著 symlink 寫到專案外)"
                           % (rel, os.path.relpath(cur, root)))
        if os.path.lexists(cur):
            if last and not os.path.isfile(cur):
                raise Boundary("%s:既有的 destination 不是一般檔" % rel)
            if not last and not os.path.isdir(cur):
                raise Boundary("%s:路徑上的 %s 已存在但不是目錄" % (rel, os.path.relpath(cur, root)))
        if not _inside(cur, root):
            raise Boundary("%s:落在專案根之外" % rel)
    return os.path.join(root, *parts)


def check_source(pack, rel):
    path = os.path.join(pack, *rel.split("/"))
    if os.path.islink(path) or not os.path.isfile(path):
        raise Boundary("%s:方法包內的 source 不是一般檔(缺檔或 symlink)" % rel)
    if not _inside(path, pack):
        raise Boundary("%s:source 落在方法包之外" % rel)
    return path


def baseline_path(root, rel):
    if not rel.startswith("docs/dev/"):
        return None
    return os.path.join(root, BASELINE_REL, *rel[len("docs/dev/"):].split("/"))


def local_mode_differs(path, want):
    if os.name != "posix":
        return False  # Windows 的 mode 位元不可靠,只比內容
    return stat.S_IMODE(os.stat(path).st_mode) != int(want, 8)


def is_skipped(state, note, include_custom):
    """這一列在這次 --apply 會被跳過(需同意、且沒加 --include-custom)。"""
    return state == "變更" and note.startswith("需同意") and not include_custom


def baseline_sync_plan(root, plan, include_custom):
    """baseline 目錄存在才有計畫:回傳 [(row, src, bdest, 狀態)],狀態 ∈ 新增/更新/相同(只比內容)/不新增;
    不新增 = baseline 沒有此檔、且該列這次被跳過(v3.26.4:不讓 baseline 先於專案檔變成上游新內容)。
    baseline 目錄不存在回傳 None(過渡態,不建立)。路徑越界 raise Boundary。"""
    bdir = os.path.join(root, BASELINE_REL)
    if not os.path.isdir(bdir) or os.path.islink(bdir):
        return None
    out = []
    for row, src, _dest, state, note in plan:
        bp = baseline_path(root, row["destination"])
        if bp is None:
            continue
        brel = os.path.relpath(bp, root).replace(os.sep, "/")
        bdest = check_destination(root, brel)
        if not os.path.lexists(bdest):
            st = "不新增" if (note == NOTE_NO_BASELINE_FILE and is_skipped(state, note, include_custom)) else "新增"
        elif _read(bdest) == _read(src):  # baseline 只比內容(它是三方比對的內容基準;權限差異不值得重寫)
            st = "相同"
        else:
            st = "更新"
        out.append((row, src, bdest, st))
    return out


def classify(root, row, src, dest):
    """回傳 (狀態, 細節)。狀態:新增 / 變更 / 相同;變更的細節:母版改寫 / 需同意:<原因>。"""
    if not os.path.lexists(dest):
        return "新增", ""
    same_content = _read(src) == _read(dest)
    if same_content and not local_mode_differs(dest, row["mode"]):
        return "相同", ""
    if same_content:
        return "變更", "母版改寫(僅權限;內容相同)"
    bdir = os.path.join(root, BASELINE_REL)
    bpath = baseline_path(root, row["destination"])
    if not os.path.isdir(bdir):
        return "變更", "需同意:無 baseline(過渡態,視為可能的本地客製)"
    if bpath is None or not os.path.isfile(bpath):
        return "變更", NOTE_NO_BASELINE_FILE
    if _read(bpath) == _read(dest):
        return "變更", "母版改寫"
    return "變更", "需同意:本地內容與 baseline 不同(本地客製)"


def write_one(dest, data, mode):
    d = os.path.dirname(dest)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".devflow-upgrade-", dir=d)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.chmod(tmp, int(mode, 8))
        os.replace(tmp, dest)
    except BaseException:
        if os.path.lexists(tmp):
            os.unlink(tmp)
        raise


def text_diff(src, dest, rel):
    try:
        a = _read(dest).decode("utf-8").splitlines()
        b = _read(src).decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return ["    (非 UTF-8 文字檔,略過 diff)"]
    out = list(difflib.unified_diff(a, b, fromfile="本地 " + rel, tofile="方法包 " + rel, lineterm="", n=1))
    if len(out) > DIFF_MAX_LINES:
        out = out[:DIFF_MAX_LINES] + ["…(其餘 %d 行省略)" % (len(out) - DIFF_MAX_LINES)]
    return ["    " + ln for ln in out]


def main(argv):
    ap = argparse.ArgumentParser(add_help=True, description="照 ship-manifest 把方法包散發檔複製/更新進採用專案(預設 dry-run)")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--pack", default=os.path.dirname(SELF_DIR))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--include-custom", action="store_true")
    ap.add_argument("--diff", action="store_true")
    args = ap.parse_args(argv)

    root = os.path.realpath(args.root)
    pack = os.path.realpath(args.pack)
    if not os.path.isdir(root):
        print("拒絕:--root 不是目錄:%s" % args.root, file=sys.stderr)
        return 2
    if not os.path.isdir(pack):
        print("拒絕:--pack 不是目錄:%s" % args.pack, file=sys.stderr)
        return 2
    if root == pack:
        print("拒絕:--root 與 --pack 是同一處(%s)。--root 要是採用專案,不是方法包。" % root, file=sys.stderr)
        return 2

    from devflow_ship_manifest import ManifestError, load
    try:
        data = load(pack)
    except ManifestError as exc:
        print("拒絕:方法包的 ship-manifest 不合格(fail-closed):", file=sys.stderr)
        for p in exc.problems:
            print("  - %s" % p, file=sys.stderr)
        return 2

    plan = []
    try:
        for row in data["files"]:
            src = check_source(pack, row["source"])
            dest = check_destination(root, row["destination"])
            state, note = classify(root, row, src, dest)
            plan.append((row, src, dest, state, note))
        bplan = baseline_sync_plan(root, plan, args.include_custom)
    except Boundary as exc:
        print("拒絕:邊界違規,一個檔都沒寫:%s" % exc, file=sys.stderr)
        return 2

    mode_label = "APPLY" if args.apply else "dry-run"
    print("dev-flow upgrade(ship-manifest 列)[%s]" % mode_label)
    print("  專案:%s" % root)
    print("  方法包:%s(manifest %s,共 %d 列)" % (pack, data.get("version"), len(plan)))
    if not os.path.isdir(os.path.join(root, "docs", "dev")):
        print("  ⚠ 專案沒有 docs/dev/ —— 看起來還沒跑過 dev-setup install;這支只做 manifest 列,不做 install 的其他步驟。")
    counts = {"新增": 0, "變更": 0, "相同": 0}
    need_consent = 0
    for row, src, dest, state, note in plan:
        counts[state] += 1
        if state == "相同":
            print("  相同  %s" % row["destination"])
            continue
        flag = ""
        if state == "變更":
            flag = "  [%s]" % note
            if note.startswith("需同意"):
                need_consent += 1
        print("  %s  %s%s" % (state, row["destination"], flag))
        if args.diff and state == "變更":
            for ln in text_diff(src, dest, row["destination"]):
                print(ln)
    print("合計:新增 %d、變更 %d(其中需同意 %d)、相同 %d" % (counts["新增"], counts["變更"], need_consent, counts["相同"]))

    if bplan is None:
        print("baseline:docs/dev/.devflow-baseline/ 不存在(過渡態或尚未建立)—— 不建立、不同步;"
              "照 dev-setup SKILL 的過渡態規則處理(受管檔視為本地客製,逐檔徵同意,完成後才建快照)。")
    else:
        bc = {"新增": 0, "更新": 0, "相同": 0, "不新增": 0}
        for _r, _s, _b, st in bplan:
            bc[st] += 1
        print("baseline 同步(docs/dev/.devflow-baseline/,--apply 且全部列寫入成功後才做;內容 = 方法包上游新內容):"
              "新增 %d、更新 %d、相同 %d、不新增 %d" % (bc["新增"], bc["更新"], bc["相同"], bc["不新增"]))
        for row, _s, _b, st in bplan:
            if st == "不新增":
                print("  baseline 不新增  %s(%s)" % (row["destination"], BASELINE_SKIP_REASON))

    rc = 0
    if not args.apply:
        print("dry-run:沒有寫入任何檔案。加 --apply 寫入「新增」與「母版改寫」;"
              "「需同意」的列要逐檔徵得使用者同意後再加 --include-custom。")
    else:
        written = skipped = failed = 0
        # manifest 自己那一列最後寫;前面有失敗就不寫它(版本不會比實際散發的檔還新)
        ordered = [p for p in plan if p[0]["destination"] != MANIFEST_DEST] + \
                  [p for p in plan if p[0]["destination"] == MANIFEST_DEST]
        for row, src, dest, state, note in ordered:
            if state == "相同":
                continue
            if is_skipped(state, note, args.include_custom):
                skipped += 1
                print("  跳過  %s(%s;徵得同意後加 --include-custom)" % (row["destination"], note))
                continue
            if row["destination"] == MANIFEST_DEST and failed:
                skipped += 1
                print("  跳過  %s(前面有寫入失敗,manifest 最後才寫,避免版本比實際散發的檔還新)" % row["destination"])
                continue
            try:
                dest = check_destination(root, row["destination"])  # 寫之前再驗一次
                write_one(dest, _read(src), row["mode"])
                written += 1
                print("  寫入  %s" % row["destination"])
            except (Boundary, OSError) as exc:
                failed += 1
                print("  失敗  %s:%s" % (row["destination"], exc), file=sys.stderr)
        print("APPLY 完成:寫入 %d、跳過 %d、失敗 %d" % (written, skipped, failed))
        if failed:
            rc = 1
            if bplan:
                print("baseline:前面有寫入失敗 —— 不同步 baseline(基準不能比實際散發的檔還新);修好後重跑。")
        elif bplan:
            bw = bf = 0
            for row, src, _bdest, st in bplan:
                if st in ("相同", "不新增"):
                    continue
                try:
                    bdest = check_destination(root, os.path.relpath(
                        baseline_path(root, row["destination"]), root).replace(os.sep, "/"))
                    write_one(bdest, _read(src), row["mode"])
                    bw += 1
                except (Boundary, OSError) as exc:
                    bf += 1
                    print("  baseline 失敗  %s:%s" % (row["destination"], exc), file=sys.stderr)
            nb = [row["destination"] for row, _s, _b, st in bplan if st == "不新增"]
            print("baseline 同步完成:寫入 %d、失敗 %d(已相同的略過)%s" % (bw, bf, ("、不新增 %d" % len(nb)) if nb else ""))
            for d in nb:
                print("  baseline 未同步  %s(%s)" % (d, BASELINE_SKIP_REASON))
            if bf:
                rc = 1
    print("不在這支範圍(仍照 dev-setup SKILL 的 upgrade 段做):README／_templates 複製、"
          "殘件刪除(devflow-upgrade-leftovers.sh;上游已移除、manifest 不再列的舊工具檔這支不會刪)、"
          "README／_templates 的 baseline 快照與 baseline 的乾淨替換、.gitignore。"
          "做完後在專案內跑 doctor 確認 ship-manifest 逐列 ✓:bash %s doctor"
          "(入口在方法包的 hooks/,不是 scripts/)。" % os.path.join(pack, "hooks", "devflow-exec.sh"))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
