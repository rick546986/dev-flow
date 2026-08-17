"""_dispatch_impl.py — devflow-dispatch-guard runtime(PreToolUse:Task|Agent)。

窄版「首派即最高階」攔截:只管一件事 —— 本 run 從沒出現過低階(haiku/sonnet)的
attempt_started,卻顯式指名最高階模型(opus/fable)當第一筆派工,這是分層紀律
(鐵律 3:haiku 機械活、sonnet 分析實作、opus/fable 只做最終判斷)被繞過的機械徵象。
升降級全流程的判斷(該不該升、升幾級、失敗幾次才升)不在本檔範圍 —— 那需要狀態
與人的判斷,hook 只做「沒照做會現形」這一半,prompt 紀律仍管「該怎麼做」。

fail-OPEN,不是 fail-closed:未武裝、schema 讀不到/對不上、或 model 參數缺席/非
字串,一律放行。這與 devflow-guard.sh(fail-closed)刻意不同 —— 本守衛只在
「exec-v2/exec-v3 武裝中且顯式指名最高階模型」這一窄口徑內下判斷,窄口徑外的
一切派工(含非 dev-flow 用途的一般 Task/Agent 呼叫)必須不受影響。

信任模型(2026-08-17 fresh 審查 X-5b,裁決=記錄邊界不修):本守衛防手滑與紀律
漂移,不防蓄意偽造 —— agent 可用不含 shell 重導向字面的直譯器寫檔繞過
_prebash_impl 的 .devflow/ 圍欄,偽造豁免卡或假 attempt_started 事件;這與
_prebash_impl.py 既有的字面圍欄同一個信任邊界(見該檔對應段落的互相引用),
接受並明文化,不做黑名單擴充的防禦劇場。
"""
import datetime
import glob
import json
import os
import sys

sys.dont_write_bytecode = True   # 對齊 _obs/_doctor/_guard:不落 __pycache__

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib.machinery import SourceFileLoader
L = SourceFileLoader("devflow_lib", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "devflow-lib.py")).load_module()

# 與 hooks/_exec_impl.py 的同名常數刻意重複而非 import:該檔是即刻執行的 CLI
# 腳本(讀 sys.argv[1]/[2] 當下就跑),動態載入它有副作用風險。兩處字面值是同一件
# 事的兩份抄本 —— 新增 exec schema 版本時兩檔必須同步改,否則本守衛會把新版誤判
# 成「未武裝」而整批放行。
EXEC_SCHEMAS = ("exec-v2", "exec-v3")

# 最高階與可升階兩層的判準皆用子字串、不分大小寫 —— 模型別名/版本後綴常變
# (例:claude-opus-4-1、claude-haiku-4-5),鎖死全字串比對只會讓判準脆弱漂移;
# 這裡寧可稍寬也不要因為別名格式變了就整條規則失能。
TOP_TIER_MARKERS = ("opus", "fable")
LOW_TIER_MARKERS = ("haiku", "sonnet")


def _has_marker(model, markers):
    lower = model.lower()
    return any(m in lower for m in markers)


def _scan_low_tier_attempt(root, run_id):
    """本 run 是否已出現任何低階 attempt_started —— 有就代表這是合法的升階派工,
    不是「首派即最高階」。逐行掃 JSONL、glob 找檔,不整檔載入、不整目錄一次讀盡
    (15 秒 timeout 內要跑完,run 內 attempts 數量不受本守衛控制)。"""
    if not run_id:
        return False
    pattern = os.path.join(root, ".devflow", "runs", run_id, "attempts", "*", "events.jsonl")
    for events_path in glob.glob(pattern):
        try:
            with open(events_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        continue
                    if ev.get("event_type") != "attempt_started":
                        continue
                    model = ev.get("model")
                    if isinstance(model, str) and _has_marker(model, LOW_TIER_MARKERS):
                        return True
        except OSError:
            continue
    return False


def _consume_exemption(exempt_path):
    """豁免一次性、留痕:用畢立刻標記 used=true+used_at,下一次同樣情境不再放行。"""
    try:
        card = json.load(open(exempt_path))
    except (ValueError, OSError):
        return False
    if not isinstance(card, dict) or card.get("used") is not False:
        return False
    card["used"] = True
    card["used_at"] = _iso_now()
    try:
        json.dump(card, open(exempt_path, "w"), ensure_ascii=False, indent=1)
    except OSError as exc:
        # F4(2026-08-17):本守衛自稱 fail-open —— 「豁免卡有效但標記寫不回去」
        # 是環境問題(唯讀檔案系統/權限),不該變成攔截。放行並印警告;代價 =
        # 卡片沒能標記已用,下次同情境會再放行一次 —— 可接受的降級(比「持有
        # 有效豁免卡卻被擋死」好;真要一次性就修環境讓寫入成功)。
        print(f"⚠️ tier-exempt 有效但標記寫入失敗({exc})—— fail-open 放行;"
              f"卡片未消耗,下次同情境仍會再放行一次。", file=sys.stderr)
        return True
    # 這行 stderr 只是 best-effort 通知(exit 0 時 PreToolUse stderr 不保證送到眼前,
    # 見 _guard_impl.py 的 A1 註解同一件事)——真正的裁決紀錄與可回溯留痕是上面
    # 已落盤的 used=true+used_at,不是這行字。別因為偶爾沒看到這行就誤以為要把
    # 這條路徑改成 exit 2:exit 0 才是正確行為,消耗是為了讓「下次不再放行」。
    print(f"tier-exempt 已消耗:{card.get('reason', '')}", file=sys.stderr)
    return True


def _iso_now():
    return datetime.datetime.now().isoformat(timespec="seconds")


root = sys.argv[1]
# F2:payload 從 stdin 讀(正本 devflow-lib.read_hook_input),不再經環境變數 ——
# export 大 payload 會讓殼層 exec 撞 ARG_MAX;本守衛 fail-open,自壞 = 永遠放行。
h = L.read_hook_input()
if h is None:
    sys.exit(0)

tool = h.get("tool_name", "")
if tool not in ("Task", "Agent"):
    sys.exit(0)          # matcher 已濾過,雙保險不做多餘判斷

tool_input = h.get("tool_input", {})
if not isinstance(tool_input, dict):
    sys.exit(0)
model = tool_input.get("model")
if not isinstance(model, str) or not model.strip():
    sys.exit(0)          # 沒帶 model 或非字串 → 繼承主迴圈,窄版只管顯式指定

if not _has_marker(model, TOP_TIER_MARKERS):
    sys.exit(0)          # 不是最高階派工,與本守衛無關

execp = os.path.join(root, ".devflow", "exec.json")
if not os.path.exists(execp):
    sys.exit(0)          # 未武裝 → 舊 state 行為不變(一律放行)
try:
    state = json.load(open(execp))
except (ValueError, OSError):
    sys.exit(0)          # exec.json 讀不到:corruption fail-closed 是既有守衛的職責,
                          # 本窄版守衛只認得住的 schema,讀不到就當未武裝處理
if not isinstance(state, dict) or state.get("schema") not in EXEC_SCHEMAS:
    sys.exit(0)          # 舊 exec-v1(無 schema 欄)或未知 schema → 一律放行

run_id = state.get("run_id") or ""
if _scan_low_tier_attempt(root, run_id):
    sys.exit(0)          # 本 run 已有低階 attempt,這是合法的升階路徑

exempt_path = os.path.join(root, ".devflow", "tier-exempt.json")
# ⚠️ 已知限制(未推廣,寫明取捨而非放著不提 —— 本檔主題就是防「不對稱保護」):
# 豁免卡是 repo 級,不是 run 級。stop 只清 exec.json/sentinel,不動這張卡 ——
# 若 run A 核了卡沒用掉,run B 的首派最高階會消耗掉那張理由不屬於它的卡。
# 現階段判定可接受(核發本來就要求人手動跑 CLI、留痕可回溯查 created_at 對不對得上
# 當時的 run);要收斂就在 stop 分支順手清掉未用的卡,見 Backlog。
if os.path.exists(exempt_path) and _consume_exemption(exempt_path):
    sys.exit(0)

L.die(
    "⛔ 派工分層守衛:本 run 尚未出現任何低階(haiku/sonnet)attempt,"
    f"首次派工卻直接指名最高階模型({model})—— 違反分層紀律"
    "(鐵律 3:haiku 機械活、sonnet 分析實作、opus/fable 只做最終判斷/合法升階)。\n"
    "→ 合法情境要豁免(例:G3 仲裁需要最高階首派):\n"
    '   bash hooks/devflow-exec.sh tier-exempt --reason "G3 仲裁需要最高階首派"\n'
    "→ 豁免一次性且留痕:.devflow/tier-exempt.json 記 used_at,用畢即失效,"
    "下次同樣情境仍會擋。")
