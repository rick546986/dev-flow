#!/bin/bash
# test-status-update.sh — STATUS 單寫入者的行為牙
#
# 釘五件:
#   1. 帶鎖的更新器對兩列並行寫,兩列都在(同 checkout 不再 last-write-wins)
#   2. 今日手改(無鎖 read-modify-write)會丟一列 —— 這是 hazard 本身
#   3. 手改後蓋章對不上(`--verify-stamp` 紅)。今天沒有這顆牙,手改全綠;
#      拿掉蓋章檢查的 mutant 對同一份手改檔又變綠 —— 證明牙在蓋章,不在散文
#   4. feature 檔的 Active/Backlog 表列相對基準被改 → `--check-tables` 紅
#   5. --refresh-stamp 不准替手改表列補章:表列漂了就拒;表列與基準相同才准補章
#
# 用法:scripts/test-status-update.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

TOOL="$SELF_DIR/status-update.sh"
[ -f "$TOOL" ] || { echo "FATAL: 找不到 $TOOL" >&2; exit 2; }
chmod +x "$TOOL"

python3 - "$TOOL" "$ROOT" <<'PY'
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

tool, root = sys.argv[1], sys.argv[2]
passed = 0
failed = 0
MIN_CASES = 19

HEADER = """# 進行中變更索引

> 測試用 STATUS。

<!-- status-writer-rev:0000000000000000000000000000000000000000000000000000000000000000 -->

## Active

| Feature | Lane | Stage | Owner | Branch | Gates | Updated |
|---|---|---|---|---|---|---|
| [feat-a](./feat-a/) | full | 1-discussion | alice | n-a:尚未建立 branch | G1⬜ G2⬜ G3⬜ | 2026-08-01 |
| [feat-b](./feat-b/) | full | 1-discussion | bob | n-a:尚未建立 branch | G1⬜ G2⬜ G3⬜ | 2026-08-01 |

## Backlog

| 級 | 一句 | 來源 |
|---|---|---|
| B | row-alpha 待辦 | note-a |
| B | row-beta 待辦 | note-b |
"""


def expect(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("  ✓ " + label)
        return
    failed += 1
    print("  ✗ " + label, file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)


def run(path, *args):
    return subprocess.run(
        ["bash", tool, "--file", path, *args],
        capture_output=True,
        text=True,
    )


def unlocked_rmw(path, old, new, delay):
    """今日手改:讀整檔、睡、寫整檔。兩條交錯就是 last-write-wins。"""
    text = open(path, encoding="utf-8").read()
    time.sleep(delay)
    open(path, "w", encoding="utf-8").write(text.replace(old, new, 1))


with tempfile.TemporaryDirectory(prefix="status-update-") as tmp:
    # ── 1. 蓋章:表列與基準相同才准 refresh;手改表列 verify 紅 ──
    fx = os.path.join(tmp, "stamp.md")
    base_fx = os.path.join(tmp, "stamp-base.md")
    open(fx, "w", encoding="utf-8").write(HEADER)
    shutil.copy2(fx, base_fx)
    ref = run(fx, "--refresh-stamp", "--base-file", base_fx)
    ver = run(fx, "--verify-stamp")
    expect(
        "表列與基準相同時 refresh-stamp 後 verify-stamp 過",
        ref.returncode == 0 and ver.returncode == 0
        and "status-writer-rev:" in ver.stdout,
        (ref.stdout or "") + (ref.stderr or "") + (ver.stdout or "") + (ver.stderr or ""),
    )

    # destroy:手改一列再 --refresh-stamp → 必須拒,章不得變成漂表的合法章
    drifted = os.path.join(tmp, "drifted.md")
    shutil.copy2(fx, drifted)
    open(drifted, "w", encoding="utf-8").write(
        open(drifted, encoding="utf-8").read().replace("row-alpha 待辦", "row-alpha 手改後想補章", 1)
    )
    before_drift = open(drifted, encoding="utf-8").read()
    bless = run(drifted, "--refresh-stamp", "--base-file", base_fx)
    after_drift = open(drifted, encoding="utf-8").read()
    expect(
        "手改表列再 --refresh-stamp → 拒(不准替漂表補章)",
        bless.returncode != 0
        and "不准替手改表列補章" in (bless.stderr or "")
        and after_drift == before_drift,
        (bless.stdout or "") + (bless.stderr or ""),
    )
    expect(
        "被拒的漂表 verify-stamp 仍紅(章沒被改成合法)",
        run(drifted, "--verify-stamp").returncode != 0,
        after_drift,
    )

    # mutant:拿掉「表列與基準不同就拒」——今天的 --refresh-stamp 就是這種綠
    mutant_rs = os.path.join(tmp, "status-update.mutant-restamp.sh")
    src_rs = open(tool, encoding="utf-8").read()
    patched_rs = src_rs.replace(
        'fail("拒絕:--refresh-stamp 表列與基準不同,不准替手改表列補章(%s)" % title)',
        "pass  # mutant: bless drifted tables",
    )
    expect(
        "refresh-stamp 基準閘 mutant 源與正本不同",
        patched_rs != src_rs,
        "替換沒打中,基準閘沒被破壞",
    )
    open(mutant_rs, "w", encoding="utf-8").write(patched_rs)
    os.chmod(mutant_rs, 0o755)
    drift2 = os.path.join(tmp, "drifted-mutant.md")
    shutil.copy2(fx, drift2)
    open(drift2, "w", encoding="utf-8").write(
        open(drift2, encoding="utf-8").read().replace("row-alpha 待辦", "row-alpha 手改後想補章", 1)
    )
    forged_rs = subprocess.run(
        ["bash", mutant_rs, "--file", drift2, "--refresh-stamp", "--base-file", base_fx],
        capture_output=True, text=True,
    )
    expect(
        "拿掉基準閘的 mutant 對手改表列 refresh-stamp 綠(今天的後門)",
        forged_rs.returncode == 0
        and run(drift2, "--verify-stamp").returncode == 0,
        (forged_rs.stdout or "") + (forged_rs.stderr or ""),
    )

    hand = os.path.join(tmp, "hand.md")
    shutil.copy2(fx, hand)
    text = open(hand, encoding="utf-8").read()
    open(hand, "w", encoding="utf-8").write(
        text.replace("row-alpha 待辦", "row-alpha 被手改", 1)
    )
    bad = run(hand, "--verify-stamp")
    expect(
        "手改表列、不走更新器 → verify-stamp 紅(今天沒這顆牙會綠)",
        bad.returncode != 0 and "蓋章對不上" in (bad.stderr or ""),
        (bad.stdout or "") + (bad.stderr or ""),
    )

    # mutant:把 --verify-stamp 的失敗改成永遠成功,同一份手改檔就綠
    mutant = os.path.join(tmp, "status-update.mutant-nostamp.sh")
    src = open(tool, encoding="utf-8").read()
    # 把 verify 的 Python 整段換成立刻成功 —— 模擬「今天沒有蓋章牙」
    patched = re.sub(
        r'if \[ "\$VERIFY_STAMP" = "1" \]; then\n  python3 - "\$TARGET" verify <<\'PY\'\n.*?\nPY\n  exit \$\?\nfi',
        'if [ "$VERIFY_STAMP" = "1" ]; then\n  echo "status-writer-rev:forged"\n  exit 0\nfi',
        src,
        count=1,
        flags=re.S,
    )
    expect(
        "mutant 源與正本不同(蓋章檢查真的被拿掉)",
        patched != src,
        "正本與 mutant 一樣 —— 替換沒打中,牙沒被破壞",
    )
    open(mutant, "w", encoding="utf-8").write(patched)
    os.chmod(mutant, 0o755)
    forged = subprocess.run(
        ["bash", mutant, "--file", hand, "--verify-stamp"],
        capture_output=True, text=True,
    )
    expect(
        "拿掉蓋章檢查的 mutant 對手改檔綠(今天手改就是這種綠)",
        forged.returncode == 0,
        (forged.stdout or "") + (forged.stderr or ""),
    )

    # ── 2. --set 改一格,另一列不動,章跟著對 ──
    one = os.path.join(tmp, "one.md")
    shutil.copy2(fx, one)
    s = run(one, "--section", "backlog", "--match", "row-alpha",
            "--set", "一句=row-alpha 已改")
    after = open(one, encoding="utf-8").read()
    expect(
        "--set 只改對上的那一列",
        s.returncode == 0
        and "row-alpha 已改" in after
        and "row-beta 待辦" in after
        and run(one, "--verify-stamp").returncode == 0,
        (s.stdout or "") + (s.stderr or "") + after,
    )

    # ── 3. 帶鎖並行寫兩列,兩列都在 ──
    conc = os.path.join(tmp, "conc.md")
    shutil.copy2(fx, conc)
    p1 = subprocess.Popen(
        ["bash", tool, "--file", conc, "--section", "backlog",
         "--match", "row-alpha", "--set", "一句=row-alpha 鎖內"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    p2 = subprocess.Popen(
        ["bash", tool, "--file", conc, "--section", "backlog",
         "--match", "row-beta", "--set", "一句=row-beta 鎖內"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    o1, e1 = p1.communicate()
    o2, e2 = p2.communicate()
    both = open(conc, encoding="utf-8").read()
    expect(
        "兩支 status-update.sh 並行改不同列 → 兩列都在且章對",
        p1.returncode == 0 and p2.returncode == 0
        and "row-alpha 鎖內" in both
        and "row-beta 鎖內" in both
        and run(conc, "--verify-stamp").returncode == 0,
        "p1=%s\n%s\n%s\np2=%s\n%s\n%s\nfile=\n%s"
        % (p1.returncode, o1, e1, p2.returncode, o2, e2, both),
    )

    # ── 4. 今日手改並行:後寫蓋先寫,丟一列 ──
    clob = os.path.join(tmp, "clob.md")
    shutil.copy2(fx, clob)
    t1 = threading.Thread(
        target=unlocked_rmw,
        args=(clob, "row-alpha 待辦", "row-alpha 手改A", 0.25),
    )
    t2 = threading.Thread(
        target=unlocked_rmw,
        args=(clob, "row-beta 待辦", "row-beta 手改B", 0.05),
    )
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    lost = open(clob, encoding="utf-8").read()
    # t2 先寫(只改 beta),t1 後寫(從原檔只改 alpha)→ beta 的改動消失
    expect(
        "無鎖手改並行 → last-write-wins(至少一列改動消失)",
        not ("row-alpha 手改A" in lost and "row-beta 手改B" in lost),
        lost,
    )
    expect(
        "無鎖互蓋後 verify-stamp 紅(殘章,不是安靜綠)",
        run(clob, "--verify-stamp").returncode != 0,
        open(clob, encoding="utf-8").read(),
    )

    # ── 5. 取不到鎖 → exit 1 ──
    held = os.path.join(tmp, "held.md")
    shutil.copy2(fx, held)
    lock = held + ".lock"
    os.mkdir(lock)
    blocked = run(held, "--retries", "0", "--section", "backlog",
                  "--match", "row-alpha", "--set", "一句=不該寫入")
    os.rmdir(lock)
    expect(
        "鎖被佔且 --retries 0 → exit 1,檔案不動",
        blocked.returncode == 1
        and "row-alpha 待辦" in open(held, encoding="utf-8").read()
        and "不該寫入" not in open(held, encoding="utf-8").read(),
        (blocked.stdout or "") + (blocked.stderr or ""),
    )

    # ── 6. --check-tables:表列被改就紅 ──
    base = os.path.join(tmp, "base.md")
    feat = os.path.join(tmp, "feat.md")
    shutil.copy2(fx, base)
    shutil.copy2(fx, feat)
    ok_tbl = run(feat, "--check-tables", "--base-file", base)
    expect(
        "表列與基準相同 → check-tables 過",
        ok_tbl.returncode == 0 and "match" in ok_tbl.stdout,
        (ok_tbl.stdout or "") + (ok_tbl.stderr or ""),
    )
    open(feat, "w", encoding="utf-8").write(
        open(feat, encoding="utf-8").read().replace("row-alpha 待辦", "row-alpha 分支上改", 1)
    )
    bad_tbl = run(feat, "--check-tables", "--base-file", base)
    expect(
        "feature 檔改了 Backlog 列 → check-tables 紅",
        bad_tbl.returncode != 0 and "不准改" in (bad_tbl.stderr or ""),
        (bad_tbl.stdout or "") + (bad_tbl.stderr or ""),
    )

    # ── 7. 對本 repo 正本做表列變更,非 main → 拒(本測試就在 feature branch 上跑)──
    real = os.path.join(root, "docs", "dev", "STATUS.md")
    if os.path.isfile(real):
        branch = subprocess.run(
            ["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True,
        ).stdout.strip()
        before = open(real, encoding="utf-8").read()
        refused = subprocess.run(
            ["bash", tool, "--section", "backlog",
             "--match", "STATUS 真正的單寫入者", "--set", "級=A"],
            capture_output=True, text=True, cwd=root,
        )
        after_real = open(real, encoding="utf-8").read()
        if branch == "main":
            expect(
                "在 main 上略過「feature 拒改正本」案(本 tar 在整合分支)",
                True,
            )
        else:
            expect(
                "feature branch 對 docs/dev/STATUS.md --set → 拒且檔案不動",
                refused.returncode == 2
                and "不准改" in (refused.stderr or "")
                and after_real == before,
                (refused.stdout or "") + (refused.stderr or ""),
            )
            restamp = subprocess.run(
                ["bash", tool, "--refresh-stamp"],
                capture_output=True, text=True, cwd=root,
            )
            expect(
                "feature branch 對正本 --refresh-stamp → 拒且檔案不動",
                restamp.returncode == 2
                and "補章" in (restamp.stderr or "")
                and open(real, encoding="utf-8").read() == before,
                (restamp.stdout or "") + (restamp.stderr or ""),
            )
    else:
        expect("找不到 docs/dev/STATUS.md 治具", False, real)

    # ── 8. upsert / remove 在 fixture 上 ──
    up = os.path.join(tmp, "up.md")
    shutil.copy2(fx, up)
    add = run(
        up, "--section", "active", "--upsert",
        "--match", "feat-c",
        "--row", "| [feat-c](./feat-c/) | fast | 4-spec | cara | n-a:尚未建立 branch | G1⬜ G2⬜ G3⬜ | 2026-08-29 |",
    )
    up_txt = open(up, encoding="utf-8").read()
    expect(
        "upsert 加上第三列 Active",
        add.returncode == 0 and "feat-c" in up_txt and "feat-a" in up_txt,
        (add.stdout or "") + (add.stderr or "") + up_txt,
    )
    rm = run(up, "--section", "active", "--remove", "--match", "feat-c")
    expect(
        "remove 拿掉 feat-c,feat-a/b 還在",
        rm.returncode == 0
        and "feat-c" not in open(up, encoding="utf-8").read()
        and "feat-a" in open(up, encoding="utf-8").read(),
        (rm.stdout or "") + (rm.stderr or ""),
    )

if passed < MIN_CASES:
    print("⛔ 實際只跑了 %d 案(地板 %d)" % (passed + failed, MIN_CASES),
          file=sys.stderr)
    sys.exit(1)
if failed:
    print("⛔ test-status-update: %d 案失敗" % failed, file=sys.stderr)
    sys.exit(1)
print("✅ test-status-update: %d 案全過" % passed)
sys.exit(0)
PY
