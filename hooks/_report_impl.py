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
    (母版根 = 本檔所在 plugin 的根,不是受測專案根。)

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

# 母版根 = plugin 自身的根(hooks/ 的上一層)—— 「路徑存不存在」問的是母版,
# 不是採用專案(採用專案的路徑存在與否正是要判別的東西)。
MASTER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    ("分支名", re.compile(r"\b(?:feature|bugfix|hotfix|fix|release)/[\w./-]+")),
)
# 相對路徑候選:word 片段以 / 相連。placeholder(<slug> 之類)的 <> 天然斷詞,
# 不會成為候選;行尾 `:行號` 由 \b 自然切開。
# ⚠️ 審查 HIGH-2 教訓:第一版在此用「(?:/seg)*/name\.ext」形狀的正則,尾段與
# 重複段有歧義 → 對 32KB 的 slash 長行災難性回溯 8.4 秒,~60KB 就吃掉 15s
# timeout,掃描被殺 = fail-open。現版正則無歧義(/ 不在 [\w.-] 內,線性掃);
# 「最後一段要有副檔名」改到 python 端判,不進正則。
PATH_TOKEN = re.compile(r"\b[\w.-]+(?:/[\w.-]+)+\b")


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
        for rule_name, pat in RULES:
            m = pat.search(line)
            if m:
                hits.append((lineno, rule_name, m.group(0).strip(), line.strip()[:90]))
        for m in PATH_TOKEN.finditer(line):
            token = m.group(0)
            if _looks_like_file_path(token) \
                    and not os.path.exists(os.path.join(MASTER_ROOT, token)):
                hits.append((lineno, "不存在於母版的路徑(疑為採用專案的)",
                             token, line.strip()[:90]))
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
