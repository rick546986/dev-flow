"""_report_impl.py — devflow-report-guard runtime(PostToolUse:Edit|Write)。

只掃缺陷回報檔(`.devflow/reports/*.md`,dev-report skill 的產出位置)的
**結構性**識別特徵。命中 → exit 2(PostToolUse 擋不住已發生的寫入,exit 2 是
把 stderr 回饋給模型要求立即去識別化 —— 與 devtalk-guard 同型)。
其餘路徑一律靜默 exit 0。

規則(機械可判的那一半):
  - 絕對路徑(/Users/、/home/、C:\\、~/)
  - git SHA(7-40 位 hex 單獨成詞,至少含一個 a-f)
  - email
  - 內網位址(192.168.*/10.*/172.16-31.*、*.local/*.internal/*.lan)
  - 分支名(feature/* fix/* bugfix/* hotfix/* release/*)
  - **不存在於母版 repo 的檔案路徑** —— 本 hook 最有價值的判準:不需要知道任何
    公司名稱,只問「這個相對路徑在母版存在嗎」;不存在 = 來自採用現場。
    (母版根解析優先序見 resolve_master_root();已安裝 plugin 執行時,舊版「本檔
    自身位置上兩層」拿到的是發版快照根而非使用者真正在改的母版 checkout —— 見
    issue #109。)

⚠️ 邊界(誠實宣告;skill 與回報流程都要複述):公司名、系統名、資料表名、業務
術語**沒有結構特徵**,本 hook 看不出來 —— 那一半靠 dev-report skill 的白名單
紀律 + 產出前人工確認。**不得宣稱「hook 上了就安全」。**
也**不得**用公司名稱黑名單來補:清單本身就是洩漏,而且會進 public repo。

fail-open:讀不到輸入/壞 JSON/檔案不存在/任何內部錯誤 → 放行(環境問題不是違規)。
"""
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True   # 對齊 _obs/_doctor:不落 __pycache__

from importlib.machinery import SourceFileLoader
L = SourceFileLoader("devflow_lib", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "devflow-lib.py")).load_module()

# 母版根解析優先序(issue #109):「路徑存不存在」問的是母版,不是採用專案
# (採用專案的路徑存在與否正是要判別的東西)。舊版只有下面的優先序 3,已安裝
# plugin 執行時拿到的是發版快照根,會把母版自己剛加的路徑誤判成「不存在」。
#   1. DEVFLOW_MASTER 環境變數(測試/移植用途,同 _gate_consistency_impl.py 的
#      DEVFLOW_MASTER/DEVFLOW_PLUGIN 慣例)—— 一樣要通過 _is_master_repo()
#      (name 為 dev-flow)才採信,不是只看 .claude-plugin/plugin.json 存在;
#      否則誤設的 DEVFLOW_MASTER 指到別的 plugin(name 不同)也會被接受,
#      「避免誤設環境變數指去無關目錄」這句話就只是嘴上說說(fresh 驗收抓到,
#      2026-09-04)。沒通過就落到優先序 2/3,並在訊息裡點名 env 被忽略的原因。
#   2. 回報檔所在 repo 的 git toplevel(devflow-report-guard.sh 已用
#      `git rev-parse --show-toplevel` 算好、以 argv[1] 傳入本檔)—— 若那裡本身
#      就是 dev-flow 母版(.claude-plugin/plugin.json 的 name 為 dev-flow),
#      代表這次執行就在母版 checkout 內(例如本 repo 自己開發時),直接採信。
#   3. Fallback:本檔(hooks/_report_impl.py)自身位置上兩層 —— 已安裝 plugin 的
#      發版快照根;優先序 1、2 都落空(採用專案不是母版、也沒設環境變數)才落到
#      這裡,是舊版原本唯一的判法。
# 實際採用的根會印在 deny 訊息裡,方便判讀「為什麼這個路徑被判不存在」。


def _is_master_repo(path):
    """path 是否就是 dev-flow 母版本身(.claude-plugin/plugin.json 的 name=dev-flow)。
    fail-open 用 except Exception(不只 OSError/ValueError):採用專案的
    .claude-plugin/plugin.json 若格式怪(例如頂層是 null 或陣列),.get() 會噴
    AttributeError —— 這裡不擋在 try 外面就會讓整支 hook rc=1(既非 deny 也非
    放行),違反本檔頭「任何內部錯誤 → 放行」的宣告(審查 HIGH-1 同型教訓)。"""
    try:
        with open(os.path.join(path, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            return json.load(f).get("name") == "dev-flow"
    except Exception:
        return False


def resolve_master_root(report_repo_root):
    """回傳 (母版根, 判讀用的來源說明) —— 優先序見上方模組註解。"""
    env_master = os.environ.get("DEVFLOW_MASTER")
    env_ignored_reason = None
    if env_master and os.path.isdir(env_master):
        if _is_master_repo(env_master):
            return env_master, "DEVFLOW_MASTER 環境變數"
        env_ignored_reason = (
            f"DEVFLOW_MASTER={env_master} 已忽略"
            "(.claude-plugin/plugin.json 缺席或 name 不是 dev-flow,"
            "不是真的母版)"
        )
    if report_repo_root and _is_master_repo(report_repo_root):
        src = "回報檔所在 repo 本身即母版(git toplevel)"
        return report_repo_root, (f"{env_ignored_reason};{src}" if env_ignored_reason else src)
    fallback = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = "fallback:hook 自身位置上兩層(已安裝 plugin 的發版快照根)"
    return fallback, (f"{env_ignored_reason};{src}" if env_ignored_reason else src)


RULES = (
    ("絕對路徑", re.compile(
        r"(?:^|[\s\"'`(=,;:])(?:/Users/|/home/|/private/|[A-Za-z]:\\\\|~/)[^\s\"'`),;]*")),
    ("git SHA", re.compile(r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.\w{2,}\b")),
    ("內網位址", re.compile(
        r"\b(?:192\.168\.\d{1,3}\.\d{1,3}"
        r"|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
        r"|[\w-]+\.(?:local|internal|lan))\b")),
    # issue #109:\b 在連字號後一樣成立(連字號不是 \w),`dev-release/SKILL.md`
    # 的 `release/` 前一字元是 "-" → \b 照樣判有邊界 → 誤命中分支名。改用負向
    # lookbehind,要求關鍵字前一字元「不是」word 字元也不是連字號,才會是真的
    # 分支名開頭(字串起點視同滿足,因為前面沒有字元)。
    ("分支名", re.compile(r"(?<![\w-])(?:feature|bugfix|hotfix|fix|release)/[\w./-]+")),
)
# 相對路徑候選:word 片段以 / 相連。placeholder(<slug> 之類)的 <> 天然斷詞,
# 不會成為候選;行尾 `:行號` 由 \b 自然切開。
# ⚠️ 審查 HIGH-2 教訓:第一版在此用「(?:/seg)*/name\.ext」形狀的正則,尾段與
# 重複段有歧義 → 對 32KB 的 slash 長行災難性回溯 8.4 秒,~60KB 就吃掉 15s
# timeout,掃描被殺 = fail-open。現版正則無歧義(/ 不在 [\w.-] 內,線性掃);
# 「最後一段要有副檔名」改到 python 端判,不進正則。
# issue #109:原本開頭用 \b,而 \b 只認 \w 邊界 —— "." 不是 \w,所以
# `.cursor-plugin/marketplace.json` 這種前導點的路徑,\b 只能從 "cursor-plugin/…"
# 開始配對,吃不到最前面那個 "."。改用負向 lookbehind(前一字元不是
# word/"."/"-" 才算候選起點)+ 可選的單一前導 "."。`\.?` 只是「零或一次」的
# 固定選擇,不是巢狀量詞,不會重新引入上面 HIGH-2 那種指數回溯(64KB 長行實測
# 仍是線性時間,與舊正則同量級)。
# ⚠️ lookbehind 排除集**不含 "/"**——這是刻意的:舊版 \b 在 "/" 後面一樣算邊界
# (`https://github.com/acmecorp/x.md` 的 "github" 前一字元是 "/",\b 照樣成立),
# 若把 "/" 也塞進排除集,等於讓這整類 URL/絕對路徑裡的候選 token 直接配不到,
# 從「會擋」倒退成「靜默放行」—— 本次修法只准新增放行(前導點),不准倒退既有
# 阻擋範圍,兩版正則已用差集腳本核對過(見回報)。
PATH_TOKEN = re.compile(r"(?<![\w.-])\.?[\w.-]+(?:/[\w.-]+)+")


def _looks_like_file_path(token):
    """最後一段帶 1-8 字的副檔名才當檔案路徑候選(其餘多為敘述性斜線用法)。"""
    last = token.rsplit("/", 1)[-1]
    if "." not in last:
        return False
    ext = last.rsplit(".", 1)[1]
    return 1 <= len(ext) <= 8 and ext.isalnum()


def scan(text):
    """回傳 [(行號, 規則名, 命中片段, 該行內容)]。"""
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        # issue #109:先掃 PATH_TOKEN、記下「母版確實存在」的片段範圍 —— 若母版
        # 路徑本身剛好含 feature/ release/ 之類字面(如未來新增 templates/release/
        # 這種目錄),分支名規則不該對已被路徑判定判為安全的同一段字元再誤判一次。
        # ⚠️ 目前母版沒有這種目錄(已用 find 核對),`dev-release/SKILL.md` 這類
        # 案例是被上面 PATH_TOKEN 的 lookbehind 修法直接解掉、根本不會落到這條
        # 分支——這段 skip 是前瞻性防線,現有 selftest 沒有案例真的走到它,改動
        # 這段前先確認有沒有新案例覆蓋。
        path_hits = []
        safe_spans = []
        for m in PATH_TOKEN.finditer(line):
            token = m.group(0)
            if not _looks_like_file_path(token):
                continue
            if os.path.exists(os.path.join(MASTER_ROOT, token)):
                safe_spans.append(m.span())
            else:
                path_hits.append((lineno, "不存在於母版的路徑(疑為採用專案的)",
                                   token, line.strip()[:90]))
        for rule_name, pat in RULES:
            # finditer(非 search):分支名規則若第一個命中剛好落在 safe_spans 內
            # (母版路徑字面含 feature/release 之類片段),不能整行跳過 —— 要接著
            # 找同一行後面「真正」的分支名。其餘規則本來就只有一個候選,行為不變。
            for m in pat.finditer(line):
                if rule_name == "分支名" and any(
                        s <= m.start() and m.end() <= e for s, e in safe_spans):
                    continue  # 這個命中落在已判定存在於母版的路徑內,採信路徑判定,找下一個
                hits.append((lineno, rule_name, m.group(0).strip(), line.strip()[:90]))
                break  # 維持原本「每規則每行只報一個」的精簡度
        hits.extend(path_hits)
    return hits


def _obs_deny(root, sid, target):
    """deny 時 best-effort 記機械事件;失敗絕不影響 deny 判定(比照 devtalk-guard)。"""
    try:
        payload = {"event_type": "mechanical_gate_completed", "gate": "report-guard",
                   "result": "FAIL", "violation": "other"}
        if target:
            payload["target"] = target
        if sid:
            payload["session_ref"] = sid
        subprocess.run(
            # sys.executable = 正在跑本檔的直譯器;不重新解析路徑,避免兩次解析在
            # 特殊環境(pyenv/conda/Windows Git Bash)下拿到不同直譯器。
            [sys.executable,
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "_obs_impl.py"),
             "hook-event", root],
            input=json.dumps(payload), text=True, capture_output=True, timeout=5)
    except Exception:
        pass


root = sys.argv[1] if len(sys.argv) > 1 else ""
h = L.read_hook_input()
if h is None:
    sys.exit(0)                                   # 壞 JSON = 環境問題,fail-open
try:
    fp = h.get("tool_input", {}).get("file_path", "")
except Exception:
    sys.exit(0)
if not isinstance(fp, str) or not fp:
    sys.exit(0)

# 審查 HIGH-3 教訓:第一版對原始字串做子字串比對,`.devflow/x/../reports/leak.md`
# 這種帶 .. 的等價路徑會被判「非回報路徑」而跳過掃描。先 normpath 摺掉 ./..
# 再比對(反向 `.devflow/reports/../../x.md` 摺完不含 reports/,本來就該跳過)。
norm = os.path.normpath(fp).replace("\\", "/")
if not norm.endswith(".md"):
    sys.exit(0)
# 2026-08-20 覆蓋缺口:原本只掃 `.devflow/reports/`,把回報檔寫到 `.devflow/` 底下
# 別的地方就整個繞過去,而且是**靜默**繞過(現場實例:健檢者把驗收報告放在
# `.devflow/verify-<版本>-<日期>.md`,帶著本機絕對路徑一路貼進 public issue,
# 守衛從頭到尾沒被觸發)。決定會不會被公開的是「位置」,而位置正是最容易寫錯的
# 東西 —— 所以掃描面放寬成 `.devflow/` 底下所有 .md。
if "/.devflow/" not in norm and not norm.startswith(".devflow/"):
    sys.exit(0)                                   # 非 .devflow/ 底下:一律靜默放行
# 例外:`.devflow/task/<T-id>/` 是 Worker 的執行期證據區,只在本機用、不會貼出去,
# 裡面出現本機絕對路徑是正常的。掃它等於在武裝狀態下把 Worker 寫證據擋掉 ——
# 那是過度封鎖,會直接卡死 Stage 6(比漏掃更嚴重,所以這條例外不能省)。
if "/.devflow/task/" in norm or norm.startswith(".devflow/task/"):
    sys.exit(0)

# root = devflow-report-guard.sh 已用 `git rev-parse --show-toplevel` 算好的
# 回報檔所在 repo 根(該殼層腳本與本檔同一次呼叫、同一個 cwd)—— 就是優先序 2
# 要問的「回報檔所在 repo 的 git toplevel」,不必在這裡重跑一次 git。到這裡才
# 解析(而非模組載入時就算)是因為前面每一個 sys.exit(0) 都代表「這次寫入根本
# 不是回報檔」,沒必要為那些多數情況多做 DEVFLOW_MASTER/git/plugin.json 這幾次
# stat。
MASTER_ROOT, MASTER_SRC = resolve_master_root(root)

try:
    # errors="replace":回報常貼 log,混到非 UTF-8 位元組不該讓守衛 crash
    # (審查 HIGH-1:曾以 traceback rc=1 收場,既非 deny 也非放行)。壞位元組
    # 換成 U+FFFD 後照掃 —— ASCII 結構特徵(路徑/SHA/email)不受影響,
    # 比「解碼失敗就放行」更保護。
    with open(fp, encoding="utf-8", errors="replace") as stream:
        text = stream.read()
except OSError:
    sys.exit(0)                                   # 檔案讀不到 = 環境問題,fail-open

try:
    hits = scan(text)
except Exception:
    sys.exit(0)                                   # 掃描自身故障不得誤傷寫入
if not hits:
    sys.exit(0)

print("⛔ report-guard:回報檔含結構性識別特徵(將貼到 public repo,先去識別化):",
      file=sys.stderr)
print(f"   （母版根:{MASTER_ROOT} —— {MASTER_SRC}）", file=sys.stderr)
for lineno, rule_name, frag, line in hits[:20]:
    print(f"  {lineno}:[{rule_name}] {frag}\n     {line}", file=sys.stderr)
if len(hits) > 20:
    print(f"  …另 {len(hits) - 20} 處", file=sys.stderr)
print("修法:照 dev-report skill 的白名單 —— 母版路徑/固定輸出/版本/數量可留,"
      "其餘泛化(<專案根>/<slug>/<系統B>)或詢問使用者。\n"
      "⚠️ 本 hook 只抓結構特徵;公司名/業務術語等語意識別要靠人工確認,"
      "不要因為本 hook 過了就當成安全。", file=sys.stderr)
_obs_deny(root, h.get("session_id", ""), norm)
sys.exit(2)
