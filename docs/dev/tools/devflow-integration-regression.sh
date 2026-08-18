#!/bin/bash
# devflow-integration-regression.sh — Stage 7 Exit Checklist「(條件式)整合回歸」計算工具
# (散發給採用專案:正本 scripts/、散發副本 docs/dev/tools/;行為與 parity 由
#  scripts/check-integration-regression-guard.sh 釘住)。規格正本:
#  notes/dispatch-v380-blockers.md H-1(母版 repo)。
#
# 它做什麼:在 feature branch 的工作樹裡回答「我開分支之後,整合分支多了什麼、
#   跟我有沒有共同戰場」。**只算與只判,絕不動樹**(不 merge/rebase/checkout、
#   不寫任何檔進 repo);唯一會改動的 git 狀態是它自己跑的 `git fetch` 更新的
#   遠端追蹤 ref(refs/remotes/…),不影響工作樹與任何本地分支。合併與跑測試由人做。
# 為什麼分岔點要用 --fork-sha 而不是 merge-base:只要整合分支最新點是 HEAD 的祖先,
#   merge-base 就必然等於它 —— 「剛開分支」「已合併」「已 rebase」三種處境在圖上
#   長得一模一樣,runtime 座標無法區分;分岔點必須用開工當下持久化的錨點
#   (6-notes 步 0 記的 FORK_INTEGRATION_SHA)。缺錨點一律 exit 2,不退回猜。
#
# 用法:
#   devflow-integration-regression.sh --integration <remote-tracking ref> \
#                                     --fork-sha <FORK_INTEGRATION_SHA>
#   例:devflow-integration-regression.sh --integration origin/main --fork-sha 3f2a1c9…
#   (在 feature branch 的工作樹裡跑。--no-fetch 僅供診斷:帶了一律 exit 2,
#    輸出不得用於勾 Exit Checklist。)
#
# exit code:0  = N_A_NO_INCOMING(分岔後對方零新 commit;唯一可記 n-a 的狀態)
#           10 = SYNC_REQUIRED_NO_OVERLAP(要合併+跑全套測試)
#           11 = SYNC_REQUIRED_WITH_OVERLAP(上面兩件+交集逐檔看過)
#           2  = fail-closed:缺/非法錨點、--integration 非遠端追蹤 ref、不在 git repo、
#                工作樹髒、merge/rebase 進行中、ALREADY_SYNCED(輸出不算數)、
#                --no-fetch 診斷模式、fetch 失敗、用法錯誤
set -uo pipefail

INTEGRATION_ARG=""
FORK_ARG=""
NO_FETCH=0
while [ $# -gt 0 ]; do
  case "$1" in
    --integration) INTEGRATION_ARG=${2:-}; shift 2 ;;
    --fork-sha)    FORK_ARG=${2:-};        shift 2 ;;
    --no-fetch)    NO_FETCH=1;             shift ;;
    *) echo "用法:$0 --integration <remote-tracking ref> --fork-sha <FORK_INTEGRATION_SHA> [--no-fetch(僅診斷,一律 exit 2)]" >&2
       exit 2 ;;
  esac
done

DIR_INTEGRATION="$INTEGRATION_ARG" DIR_FORK="$FORK_ARG" DIR_NO_FETCH="$NO_FETCH" \
python3 - <<'PY'
import os
import subprocess
import sys

INTEGRATION_ARG = os.environ["DIR_INTEGRATION"]
FORK_ARG = os.environ["DIR_FORK"]
NO_FETCH = os.environ["DIR_NO_FETCH"] == "1"


def git(*args, check=False):
    """跑 git,回 (exit code, stdout 去尾空白)。check=True 時非 0 直接 fail-closed。"""
    proc = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        die(f"git {' '.join(args)} 失敗:{proc.stderr.strip() or proc.stdout.strip()}")
    return proc.returncode, proc.stdout.rstrip("\n")


def die(msg):
    print(f"  ✗ {msg}")
    print("⛔ fail-closed:先處理上面那件事,再重跑。不准帶著算。")
    sys.exit(2)


def ok(label):
    print(f"  ✓ {label}")


print("-- 前置檢查(fail-closed,任一不過即 exit 2)--")

rc, _ = git("rev-parse", "--git-dir")
if rc != 0:
    die("不在 git repo 裡")
ok("在 git repo 裡")

if not FORK_ARG:
    die("缺 --fork-sha(必填)。錨點 = 開這條 feature branch 當下整合分支的最新點,"
        "記在 6-implementation-notes.md 步 0 的輸出區(FORK_INTEGRATION_SHA,40 碼)。"
        "缺錨點不准退回用 merge-base 猜 —— 那在「已合併/已 rebase」的圖上必然算錯。")
ok("--fork-sha 已提供")

if not INTEGRATION_ARG:
    die("缺 --integration(必填),例:--integration origin/main")
rc, full_name = git("rev-parse", "--symbolic-full-name", INTEGRATION_ARG)
if rc != 0 or not full_name:
    die(f"--integration {INTEGRATION_ARG!r} 解析不到 ref")
if not full_name.startswith("refs/remotes/"):
    die(f"--integration 必須是遠端追蹤 ref(refs/remotes/…),實得 {full_name!r}。"
        "git fetch 更新的是 origin/<branch> 不是本地 <branch> —— 收本地 ref 會在"
        "沒 checkout 過整合分支的工作樹(並行時的常態)拿到過時的點。")
ok(f"--integration 是遠端追蹤 ref:{full_name}")

# 工作樹髒 / merge / rebase 進行中一律擋:未提交與未追蹤的改動不會進入
# FEATURE_HEAD 的計算,「我這邊改了哪些檔」會少掉正在改的那些。
_, porcelain = git("status", "--porcelain")
if porcelain.strip():
    die("工作樹不乾淨(有未提交或未追蹤的改動)。先 commit 或收乾淨再跑。")
ok("工作樹乾淨")

_, git_dir = git("rev-parse", "--git-path", "MERGE_HEAD")
if os.path.exists(git_dir):
    die("merge 進行中(MERGE_HEAD 存在)。先收掉再跑。")
for state in ("rebase-merge", "rebase-apply"):
    _, p = git("rev-parse", "--git-path", state)
    if os.path.exists(p):
        die(f"rebase 進行中({state} 存在)。先收掉再跑。")
ok("沒有 merge / rebase 進行中")

remote = full_name[len("refs/remotes/"):].split("/", 1)[0]
fetched = False
if NO_FETCH:
    ok("--no-fetch:跳過 fetch(診斷模式,見下方標記)")
else:
    rc, _ = git("fetch", remote)
    if rc != 0:
        die(f"git fetch {remote} 失敗。忘記 fetch 是人必犯的錯,所以本工具自己跑;"
            "fetch 不了就不准算(算出來的是舊點)。")
    fetched = True
    ok(f"已 fetch {remote}(只更新遠端追蹤 ref,不動工作樹)")

rc, fork = git("rev-parse", "--verify", f"{FORK_ARG}^{{commit}}")
if rc != 0:
    die(f"--fork-sha {FORK_ARG!r} 不是可解析的 commit")
_, feature_head = git("rev-parse", "HEAD")
rc, integration_sha = git("rev-parse", "--verify", f"{full_name}^{{commit}}")
if rc != 0:
    die(f"{full_name} 解析不到 commit")

# 錨點必須同時是「整合分支現況」與「本 branch 現況」的祖先;
# 任一不成立 = 錨點給錯了,或歷史被改寫過 → 不准往下算。
rc, _ = git("merge-base", "--is-ancestor", fork, integration_sha)
if rc != 0:
    die("錨點不是整合分支現況的祖先 —— 錨點給錯,或整合分支歷史被改寫過")
rc, _ = git("merge-base", "--is-ancestor", fork, feature_head)
if rc != 0:
    die("錨點不是本 branch HEAD 的祖先 —— 錨點給錯,或本 branch 歷史被改寫過")
ok("錨點是兩端現況的共同祖先")

print("-- 判定 --")

overlap = []
if integration_sha == fork:
    status, code = "N_A_NO_INCOMING", 0
else:
    rc, _ = git("merge-base", "--is-ancestor", integration_sha, feature_head)
    if rc == 0:
        status, code = "ALREADY_SYNCED", 2
    else:
        # 兩邊的比較基準都是持久化的 FORK,不是 merge-base(merge-base 在已同步的
        # 圖上會漂到整合分支最新點,把交集算成空 —— 原始 bug 本人)。
        # --no-renames:兩邊的改名偵測結果可能不一致,關掉後口徑一致(舊路徑消失+
        # 新路徑出現),交集不漏。清單留在記憶體裡算,無固定檔名可互蓋。
        _, ours = git("diff", "--name-only", "--no-renames", f"{fork}..{feature_head}", check=True)
        _, theirs = git("diff", "--name-only", "--no-renames", f"{fork}..{integration_sha}", check=True)
        ours_set = {line for line in ours.splitlines() if line}
        theirs_set = {line for line in theirs.splitlines() if line}
        overlap = sorted(ours_set & theirs_set)
        if overlap:
            status, code = "SYNC_REQUIRED_WITH_OVERLAP", 11
        else:
            status, code = "SYNC_REQUIRED_NO_OVERLAP", 10

print(f"STATUS: {status}")
print(f"FORK_INTEGRATION_SHA: {fork}")
print(f"FEATURE_HEAD: {feature_head}")
print(f"INTEGRATION_SHA: {integration_sha}")
print(f"INTEGRATION_REF: {full_name}")
if overlap:
    print("共同戰場:")
    for path in overlap:
        print(path)
else:
    print("共同戰場:無")
print("fetch:已執行" if fetched else "fetch:未執行(--no-fetch)")

GUIDANCE = {
    "N_A_NO_INCOMING": "分岔後對方零新 commit,Exit Checklist 可記 n-a",
    "ALREADY_SYNCED": "你已經同步過了,本次輸出不算數 —— 交集必須在動樹之前算,"
                      "拿同步後的輸出當證據就是原本那個假綠",
    "SYNC_REQUIRED_NO_OVERLAP": "仍要合併 INTEGRATION_SHA + 跑全套測試"
                                "(沒有共同戰場不代表不會壞)",
    "SYNC_REQUIRED_WITH_OVERLAP": "合併 INTEGRATION_SHA + 全套測試 + 交集逐檔看過",
}
print(f"結論:STATUS={status} FORK={fork} HEAD={feature_head} "
      f"INTEGRATION={integration_sha}({full_name})—— {GUIDANCE[status]}")
if NO_FETCH:
    print("⚠️ 未 fetch,本次結果不得用於勾 Exit Checklist(--no-fetch 僅供診斷)")
    sys.exit(2)
sys.exit(code)
PY
