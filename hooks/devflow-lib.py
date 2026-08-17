"""devflow-lib.py — 執行守衛共用邏輯(guard / postbash / prebash / exec / gate 共用)。
設計原則:fail-CLOSED —— sentinel 說「武裝中」而 exec.json 讀不到/壞掉 → 擋,不放行。

parallel(Stage 6)契約部分依 vnext-shared-contract §5/§7 與 parallel-stage6 設計
§2-§4/§10/§11 落地;行為正本 = 方法論 repo tests/parallel-stage6/ fixtures。
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

UPSTREAM = ("1-discussion", "2-decision", "3-prototype")
CONTRACT = UPSTREAM + ("4-spec",)


def read_hook_input():
    """hook payload 的唯一讀取口:stdin 正典,HOOK_INPUT 環境變數只是相容退路。

    為什麼不准經環境變數主傳(F2,2026-08-17):shell 殼層曾用
    `HOOK_INPUT=$(cat); export HOOK_INPUT` 傳遞 —— 整包 payload 進了 environ 之後,
    **每一個 exec 都要複製整份 environ**,payload 超過 ARG_MAX(macOS 約 1MB)時
    dirname/python3 全部 E2BIG → rc=126。對 hook 宿主而言那是「守衛自壞」,通常
    等同放行:fail-closed 守衛就此靜默降級成 fail-open,而且沒有任何紅字。
    stdin 沒有這個上限;殼層一律 exec python、不碰內容,由本函式在 python 端讀。
    環境變數退路只服務「直接呼叫 impl 的測試/診斷」小 payload,不走 shell export。

    回傳 dict;讀不到/解不出/非 dict → None(fail-open/closed 由各 impl 自行決定)。
    """
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""
    if not raw.strip():
        raw = os.environ.get("HOOK_INPUT", "")
    try:
        parsed = json.loads(raw or "{}")
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def is_ambient_path(rel):
    """True for filesystem metadata the execution guard must ignore."""
    parts = rel.split("/")
    base = parts[-1]
    return (base == ".DS_Store" or base.startswith("._") or base == "Thumbs.db"
            or base.endswith(".pyc") or "__pycache__" in parts)


def canonical_scope_path(raw):
    """Validate and canonicalize a Files/allow path relative to the Git root."""
    path = raw.strip()
    if not path:
        raise ValueError("空路徑")
    if os.path.isabs(path):
        raise ValueError("不可用絕對路徑；Files 必須以 Git repository root 為相對根")
    if any(part == ".." for part in path.split("/")):
        raise ValueError("不可含 .. traversal；Files 必須以 Git repository root 為相對根")
    is_dir = path.endswith("/")
    canonical = os.path.normpath(path)
    if canonical in ("", "."):
        raise ValueError("不可為空或含糊的 repository-root 條目")
    if canonical.startswith("../"):
        raise ValueError("不可離開 Git repository root")
    if is_dir:
        canonical += "/"
    return canonical


def git_dirty_paths(root, with_codes=False):
    """Return every changed repo-root-relative path from porcelain v1, including rename sources.

    掃描一律帶 --ignored=traditional：那是堵「把檔案加進 .gitignore 就繞過 scope
    守衛」的遮蔽漏洞用的,兩個呼叫端共用同一份輸出,不得拿掉。

    with_codes=False(預設,postbash 偵測網用):維持既有回傳型別 list[str],ignored
    檔照舊一起回傳、一起驗 —— 行為與本參數加入前完全相同。
    with_codes=True(start 前置掃描用):回傳 list[(code, path)],讓呼叫端能把 `!!`
    (被 .gitignore 忽略)與一般髒檔分流。start 不拿 ignored 檔擋開工,但仍收進
    baseline,所以遮蔽漏洞照堵(A-13)。
    rename/copy 的來源路徑沿用該筆記錄自己的 code,行為不變。
    """
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "-uall", "--ignored=traditional"],
        cwd=root, capture_output=True, text=True)
    if status.returncode:
        raise RuntimeError(status.stderr.strip() or "git status failed")

    fields = status.stdout.split("\0")
    entries, i = [], 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if not entry:
            continue
        if len(entry) < 4 or entry[2] != " ":
            raise RuntimeError(f"unparseable git status record: {entry!r}")
        code, path = entry[:2], entry[3:]
        if not path:
            raise RuntimeError("git status reported an empty path")
        entries.append((code, path))
        if "R" in code or "C" in code:
            if i >= len(fields) or not fields[i]:
                raise RuntimeError("git status rename/copy record is missing its source path")
            source = fields[i]
            i += 1
            if "R" in code:
                entries.append((code, source))
    return entries if with_codes else [path for _, path in entries]


IGNORED_CODE = "!!"  # porcelain v1 對 --ignored 列出的忽略檔所用的 status code


def protected_contract_hashes(root):
    """Fingerprint the complete protected contract path set beneath docs/dev/."""
    base = os.path.join(root, "docs", "dev")
    hashes = {}
    if not os.path.isdir(base):
        return hashes
    for dirpath, _, filenames in os.walk(base):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            rel = os.path.relpath(path, root)
            if is_contract_path(rel):
                hashes[rel] = sha(path)
    return dict(sorted(hashes.items()))


def scope_violation_message(header, paths=(), resolution=""):
    """Format scope diagnostics consistently for start, direct writes, and post-Bash."""
    lines = [header]
    lines.extend("  " + path for path in paths)
    lines.extend((
        "Files scope 一律以 Git repository root 為相對根：",
        "internal/x_test.go 與 backend-go/internal/x_test.go 在 monorepo 是不同 scope。",
    ))
    if resolution:
        lines.append(resolution)
    return "\n".join(lines)


def git_dir(root):
    r = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=root,
                       capture_output=True, text=True)
    d = r.stdout.strip()
    if not d:
        return os.path.join(root, ".git")
    return d if os.path.isabs(d) else os.path.join(root, d)


def sha(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except Exception:
        return ""


SHADOW_BASENAME = "devflow-armed-shadow"
# ⚠️ 檔名刻意含 "devflow-armed" 子字串:prebash 既有規則(cmd 含 devflow-armed 即擋)
# 連帶封鎖任何在 shell 命令中指名 shadow 檔的觸碰,免加新 regex。
GUARDED_STATE_FILES = ("exec.json", "parallel.json")


def shadow_path(root):
    return os.path.join(git_dir(root), SHADOW_BASENAME)


def update_shadow(root):
    """CLI 每次合法寫 .devflow/{exec,parallel}.json 後呼叫:現檔 hash 記進 git-dir
    shadow(MAJOR-C:heredoc/python 直寫繞得過 prebash regex,postbash 以 hash
    比對抓 out-of-band 竄改 —— fail-closed 偵測,不追求 prevention)。"""
    hashes = {}
    for name in GUARDED_STATE_FILES:
        path = os.path.join(root, ".devflow", name)
        if os.path.exists(path):
            hashes[name] = sha(path)
    sp = shadow_path(root)
    if hashes:
        with open(sp, "w") as f:
            json.dump(hashes, f)
    elif os.path.exists(sp):
        os.remove(sp)


def shadow_mismatch(root, name):
    """回傳竄改描述(空字串 = 一致或檔不存在)。fail-closed:檔在而 shadow 缺
    = 視同竄改(out-of-band 建立,或 shadow 遭清除)。"""
    path = os.path.join(root, ".devflow", name)
    if not os.path.exists(path):
        return ""
    try:
        recorded = json.load(open(shadow_path(root))).get(name, "")
    except Exception:
        recorded = ""
    if not recorded:
        return f".devflow/{name} 存在但 shadow hash 缺失(out-of-band 建立或 shadow 遭清除)"
    if sha(path) != recorded:
        return f".devflow/{name} 內容與 shadow hash 不符(出現 CLI 之外的寫入)"
    return ""


def load_state(root):
    """回傳 (state, armed_slug, error)。error 非空 = fail-closed 情境。"""
    sentinel = os.path.join(git_dir(root), "devflow-armed")
    armed = ""
    if os.path.exists(sentinel):
        try:
            armed = open(sentinel).read().strip()
        except Exception:
            armed = "?"
    execp = os.path.join(root, ".devflow", "exec.json")
    if not os.path.exists(execp):
        if armed:
            return None, armed, (
                f"⛔ devflow-guard:旗標檔 .devflow/exec.json 消失,但守衛仍武裝中"
                f"(slug={armed})。這是自我停權訊號 —— 正常收工請跑 devflow-exec.sh stop。")
        return None, "", ""          # 真的沒在執行 → 沉睡
    try:
        return json.load(open(execp)), armed, ""
    except Exception as e:
        return None, armed, (
            f"⛔ devflow-guard:.devflow/exec.json 損壞({e})。守衛 fail-closed 擋下動作。"
            f"修復或跑 devflow-exec.sh stop 後重新 start。")


def is_contract_path(rel, kinds=CONTRACT):
    """任何 feature 的契約/上游文件(跨 slug 保護),含 .html twin。"""
    parts = rel.split("/")
    if len(parts) < 4 or parts[0] != "docs" or parts[1] != "dev":
        return False
    return any(parts[3].startswith(k) for k in kinds)


def in_pool(rel, state):
    pool = list(state.get("scope", [])) + [e.get("file", "") for e in state.get("extra", [])]
    for s in pool:
        if not s:
            continue
        if (s.endswith("/") and rel.startswith(s)) or rel == s:
            return True
    return False


def rel_of(root, fp):
    """resolve symlink 後的 repo 相對路徑;repo 外回 None。"""
    real = os.path.realpath(fp)
    rel = os.path.relpath(real, os.path.realpath(root))
    return None if rel.startswith("..") else rel


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


# ====================================================================
# parallel 契約(vnext §5/§7;行為正本 = tests/parallel-stage6/)
# ====================================================================

class ContractError(Exception):
    pass


def files_overlap(a, b):
    """相等,或一方為目錄前綴蓋住另一方(設計 §4.3)。"""
    if a == b:
        return True
    if a.endswith("/") and b.startswith(a):
        return True
    if b.endswith("/") and a.startswith(b):
        return True
    return False


# ---------- run_id(exec-v2 §7;runtime 產,非 LLM)----------

_ULID_ENC = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"          # Crockford base32
RUN_ID_RE = re.compile(r"^run_[0-9A-HJKMNP-TV-Z]{26}$")


def new_run_id():
    """"run_" + 26 字 Crockford base32 ULID(48-bit ms timestamp + 80-bit entropy)。"""
    ts = int(time.time() * 1000) & ((1 << 48) - 1)
    rand = int.from_bytes(os.urandom(10), "big")
    n = (ts << 80) | rand
    body = "".join(_ULID_ENC[(n >> (5 * (25 - i))) & 31] for i in range(26))
    return "run_" + body


# ---------- 5-tasks 解析(設計 §2;fail-closed)----------

EXEC_KEYS = ("mode", "max_parallel_tasks", "rebuild_integration_on_rework")
FIELD_RE = re.compile(
    r"\s*-\s*(Covers|Files|Verify|Blocked-by|Integrate-after|Risk|Review-mode|"
    r"Semantic-conflicts-with|Intent|Boundaries|Owner):\s*(.*?)\s*$")
HEAD_RE = re.compile(r"^##\s+(T-\d+)\b\s*(.*)$")
EMPTY_MARKS = ("", "—", "-", "－", "—(選配)")
VNEXT_FIELD_RE = re.compile(
    r"^\s*-\s*(Integrate-after|Risk|Review-mode|Semantic-conflicts-with):", re.M)

# ---------- fence 遮蔽(R-1;engine-fence-masking 4-spec)----------
# 行首 ≤3 空白 + ```/~~~ 長度 ≥3 才算開啟;backtick 開啟行的 info string 若再含
# ` 視為非開啟(CommonMark 規則,防 inline code span 被誤判成 fence)。
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
# 收尾:同種字元、整行只有該字元(可有行首 ≤3 縮排／行尾空白),長度另在程式比對 ≥ 開啟。
FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`+|~+)[ \t]*$")


def _fence_mask(lines):
    """回傳與 lines 等長的 bool list:True = 該行落在 fenced code block 內(含開啟/
    收尾行本身),parse_5_tasks 逐行掃描時必須視而不見 —— 與 twin(markdown-it)的
    fence 判定看齊(R-1:幽靈任務與 fence 內假重複欄兩種誤讀消失)。

    ⚠️ 鏡射關係:本函式與 tests/parallel-stage6/contract_ref.py 同名函式逐字相同,
    改一邊記得同步另一邊(兩檔行為必須逐字一致,是 S-1.4 的驗收對象)。

    保守 stdlib 規則(hooks 在採用端無 pip,不得 import markdown_it,不追求
    CommonMark 完整合規):
      - 開啟:FENCE_OPEN_RE(行首 ≤3 空白 + ```` ``` ```` 或 `~~~`,長度 ≥3)。
      - 收尾:FENCE_CLOSE_RE 命中,且字元同種、長度 ≥ 開啟長度。
      - 未閉合(到檔尾都沒收尾):遮到檔尾。
    逐行迭代時直接跳過被遮蔽的行(不做等長字元佔位重建字串)——parse_5_tasks 本來
    就逐行處理且不依賴行號回報錯誤,跳過比維持等長字串簡單、也不改變既有輸出。

    已知與 twin(markdown-it/CommonMark)的邊界差異,本輪不追平(見 4-spec Out of
    Scope):list 項目內的縮排 code block(非 fence)不遮蔽;list 項目內巢狀四反引號
    fence 的邊界情形(部分 CommonMark 實作依縮排/info string 判法不同)未特別處理。
    """
    n = len(lines)
    masked = [False] * n
    i = 0
    while i < n:
        m = FENCE_OPEN_RE.match(lines[i])
        if not m:
            i += 1
            continue
        fence_run, info = m.group(1), m.group(2)
        fence_char, fence_len = fence_run[0], len(fence_run)
        if fence_char == "`" and "`" in info:
            i += 1
            continue
        j = i
        while j < n:
            masked[j] = True
            if j > i:
                cm = FENCE_CLOSE_RE.match(lines[j])
                if cm and cm.group(1)[0] == fence_char and len(cm.group(1)) >= fence_len:
                    j += 1
                    break
            j += 1
        i = j
    return masked


def has_vnext_fields(text):
    """5-tasks 是否含任何 VNext 選配欄位/execution 區塊(legacy 判定)。"""
    if VNEXT_FIELD_RE.search(text):
        return True
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if re.match(r"^execution:\s*(#.*)?$", line):
                return True
    return False


def _extract_ids(value):
    if value.strip() in EMPTY_MARKS:
        return []
    return re.findall(r"T-\d+", value)


def _clean_optional(value):
    """選填自由文字欄(Boundaries/Intent/Owner)的空值正規化:模板寫
    `無則 —`,若原樣帶出「—」會讓派工者看到一個看似有值、實則佔位的欄位。
    與 EMPTY_MARKS 同一組標記,一律正規化成 ""。"""
    v = value.strip()
    return "" if v in EMPTY_MARKS else v


def _parse_execution(fm_lines, errors):
    conf = {"mode": "sequential", "max_parallel_tasks": 3,
            "rebuild_integration_on_rework": True}
    i = 0
    while i < len(fm_lines):
        if re.match(r"^execution:\s*(#.*)?$", fm_lines[i]):
            i += 1
            while i < len(fm_lines) and re.match(r"^\s{2,}\S", fm_lines[i]):
                m = re.match(r"^\s{2,}([A-Za-z_]+):\s*([^#]*)", fm_lines[i])
                i += 1
                if not m:
                    continue
                key, value = m.group(1), m.group(2).strip()
                if key not in EXEC_KEYS:
                    errors.append(f"execution 未知 key:{key}(fail-closed 拒收)")
                    continue
                if key == "mode":
                    if value not in ("sequential", "parallel"):
                        errors.append(f"execution.mode 非法值:{value}(需 sequential|parallel)")
                    else:
                        conf["mode"] = value
                elif key == "max_parallel_tasks":
                    if not value.isdigit() or int(value) < 1:
                        errors.append(f"execution.max_parallel_tasks 非正整數:{value}")
                    else:
                        conf["max_parallel_tasks"] = int(value)
                else:
                    if value not in ("true", "false"):
                        errors.append(f"execution.rebuild_integration_on_rework 非 true|false:{value}")
                    else:
                        conf["rebuild_integration_on_rework"] = value == "true"
            continue
        i += 1
    return conf


def parse_5_tasks(text):
    """回傳 {"execution": conf, "tasks": [...], "errors": [...]}。
    errors 非空 = start 必須拒啟(fail-closed)。與可執行契約 contract_ref 行為一致。"""
    errors = []
    lines = text.splitlines()

    fm_lines = []
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            fm_lines.append(line)
    execution = _parse_execution(fm_lines, errors)

    blocks, current = [], None
    fenced = _fence_mask(lines)
    for idx, line in enumerate(lines):
        if fenced[idx]:
            continue
        head = HEAD_RE.match(line)
        if head:
            if current:
                blocks.append(current)
            current = {"id": head.group(1), "title": head.group(2).strip(), "fields": {}}
            continue
        if re.match(r"^##\s+", line):
            if current:
                blocks.append(current)
                current = None
            continue
        if current:
            m = FIELD_RE.match(line)
            if m:
                key = m.group(1)
                # 同一 T 的保留欄不得出現兩次。FIELD_RE 前綴是 `\s*`(容許任意縮排),
                # 因此 `Boundaries:`／`Intent:` 的續行若寫成 `  - Files: …` 子項,
                # 會被當成該 T 的 Files 欄。舊行為是 last-write-wins:真正的 Files 被
                # 靜默換掉且 errors 為空,而 Files 是 task_scope() 與 gate 的
                # files_within_scope 的唯一依據 —— scope 就這樣被無聲放寬。
                # 改為 fail-closed:記 error(errors 非空 = start 拒啟)並保留首筆。
                # 母版對應正本:dev-flow tests/parallel-stage6/contract_ref.py。
                if key in current["fields"]:
                    errors.append(
                        f"{current['id']} 重複保留欄「{key}」:同一 T 不得出現兩次,"
                        f"後筆不得覆蓋前筆(常見成因:`Boundaries:`／`Intent:` 續行"
                        f"寫成 `- {key}:` 子項;續行禁令見母版 _templates/5-tasks.md)")
                    continue
                current["fields"][key] = m.group(2).strip()
    if current:
        blocks.append(current)
    if not blocks:
        errors.append("5-tasks 找不到 ## T-n 區塊")

    tasks = []
    for block in blocks:
        tid, fields = block["id"], block["fields"]
        for name in ("Covers", "Files", "Verify", "Blocked-by"):
            if not fields.get(name):
                errors.append(f"{tid} 缺 {name}")
        files = []
        for raw in fields.get("Files", "").split(","):
            raw = raw.strip().strip("`")
            if not raw:
                continue
            try:
                files.append(canonical_scope_path(raw))
            except ValueError as e:
                errors.append(f"{tid} Files {e}")
        risk = fields.get("Risk", "").strip() or "normal"
        if risk not in ("normal", "high"):
            errors.append(f"{tid} Risk 非法值:{risk}(需 normal|high)")
            risk = "normal"
        explicit_rm = fields.get("Review-mode", "").strip()
        if explicit_rm and explicit_rm not in ("wave", "dedicated"):
            errors.append(f"{tid} Review-mode 非法值:{explicit_rm}(需 wave|dedicated)")
            explicit_rm = ""
        if risk == "high" and explicit_rm == "wave":
            errors.append(f"{tid} Risk: high 不得配 Review-mode: wave(high 一律 dedicated review)")
        review_mode = explicit_rm or ("dedicated" if risk == "high" else "wave")
        tasks.append({
            "id": tid, "title": block["title"],
            "covers": fields.get("Covers", ""),
            "files": files,
            "verify": fields.get("Verify", "").strip("`"),
            "blocked_by": _extract_ids(fields.get("Blocked-by", "")),
            "integrate_after": _extract_ids(fields.get("Integrate-after", "")),
            "semantic_conflicts": _extract_ids(fields.get("Semantic-conflicts-with", "")),
            "risk": risk, "review_mode": review_mode,
            # A-6:Boundaries/Intent/Owner 原本 FIELD_RE 有解析、母版模板寫得像
            # 機械契約,但解析後直接丟棄,不進 task dict —— 派工者(plan 輸出／
            # exec.json task 物件)拿不到。現在真的帶進來;欄位選填,缺席預設
            # 空字串,不因缺席而 fail-closed(與 Covers/Files/Verify/Blocked-by
            # 必填欄不同)。
            "boundaries": _clean_optional(fields.get("Boundaries", "")),
            "intent": _clean_optional(fields.get("Intent", "")),
            "owner": _clean_optional(fields.get("Owner", "")),
        })

    ids = {t["id"] for t in tasks}
    for t in tasks:
        for field in ("blocked_by", "integrate_after", "semantic_conflicts"):
            for ref in t[field]:
                if ref == t["id"]:
                    errors.append(f"{t['id']} {field} 自我引用")
                elif ref not in ids:
                    errors.append(f"{t['id']} 引用不存在的 {ref}({field})")

    parsed = {"execution": execution, "tasks": tasks, "errors": errors}
    if not errors:
        for name, edges in (("execution", execution_edges(parsed)),
                            ("integration", integration_edges(parsed))):
            cycle = _find_cycle(ids, edges)
            if cycle:
                errors.append(f"{name} DAG 有環:{' → '.join(cycle)}")
    return parsed


# ---------- 兩種 DAG(設計 §3)----------

def execution_edges(parsed):
    return {(p, t["id"]) for t in parsed["tasks"] for p in t["blocked_by"]}


def integration_edges(parsed):
    edges = set(execution_edges(parsed))
    edges |= {(p, t["id"]) for t in parsed["tasks"] for p in t["integrate_after"]}
    return edges


def _find_cycle(ids, edges):
    succ = {}
    for a, b in edges:
        succ.setdefault(a, []).append(b)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {i: WHITE for i in ids}
    stack = []

    def dfs(node):
        color[node] = GRAY
        stack.append(node)
        for nxt in sorted(succ.get(node, [])):
            if color[nxt] == GRAY:
                return stack[stack.index(nxt):] + [nxt]
            if color[nxt] == WHITE:
                found = dfs(nxt)
                if found:
                    return found
        stack.pop()
        color[node] = BLACK
        return None

    for node in sorted(ids):
        if color[node] == WHITE:
            found = dfs(node)
            if found:
                return found
    return None


# ---------- Wave(設計 §4;派生資料,不回寫)----------

def _tnum(tid):
    return int(tid.split("-")[1])


def compute_waves(parsed, done=frozenset(), max_parallel=None):
    if parsed["errors"]:
        raise ContractError(f"5-tasks 有錯,不派生 wave:{parsed['errors']}")
    if parsed["execution"]["mode"] != "parallel":
        raise ContractError("sequential 模式不派生 wave(照 Blocked-by 拓撲序逐 T)")
    max_p = max_parallel or parsed["execution"]["max_parallel_tasks"]
    tasks = {t["id"]: t for t in parsed["tasks"]}
    conflicts = {tid: set() for tid in tasks}
    for t in parsed["tasks"]:
        for other in t["semantic_conflicts"]:
            conflicts[t["id"]].add(other)
            conflicts[other].add(t["id"])

    done = set(done)
    waves = []
    remaining = [tid for tid in sorted(tasks, key=_tnum) if tid not in done]
    while remaining:
        ready = [tid for tid in remaining
                 if all(p in done for p in tasks[tid]["blocked_by"])]
        if not ready:
            raise ContractError("無 ready task(不應發生:環已在解析期擋掉)")
        wave = []
        for tid in ready:
            if len(wave) >= max_p:
                break
            overlap = any(files_overlap(fa, fb)
                          for member in wave
                          for fa in tasks[tid]["files"] for fb in tasks[member]["files"])
            conflict = any(member in conflicts[tid] for member in wave)
            if not overlap and not conflict:
                wave.append(tid)
        waves.append(wave)
        done |= set(wave)
        remaining = [tid for tid in remaining if tid not in done]
    return waves


def task_scope(parsed, task_id):
    """task-scoped guard 契約:start --task 的 scope = 該 T 自己的 Files。"""
    for t in parsed["tasks"]:
        if t["id"] == task_id:
            return sorted(t["files"])
    raise ContractError(f"找不到 {task_id}")


# ---------- Task 狀態機(設計 §10)----------

STATES = ["PENDING", "READY", "RUNNING", "CANDIDATE", "MECHANICAL_PASS",
          "QUEUED_FOR_INTEGRATION", "INTEGRATED", "IN_REVIEW", "REWORK",
          "ACCEPTED", "BLOCKED"]

ALLOWED_TRANSITIONS = {
    ("PENDING", "READY"), ("PENDING", "BLOCKED"), ("BLOCKED", "READY"),
    ("READY", "RUNNING"), ("READY", "BLOCKED"),
    ("RUNNING", "CANDIDATE"), ("RUNNING", "BLOCKED"),
    ("CANDIDATE", "MECHANICAL_PASS"), ("CANDIDATE", "REWORK"),
    ("MECHANICAL_PASS", "QUEUED_FOR_INTEGRATION"), ("MECHANICAL_PASS", "IN_REVIEW"),
    ("QUEUED_FOR_INTEGRATION", "INTEGRATED"), ("QUEUED_FOR_INTEGRATION", "REWORK"),
    ("INTEGRATED", "IN_REVIEW"), ("INTEGRATED", "REWORK"),
    ("IN_REVIEW", "ACCEPTED"), ("IN_REVIEW", "REWORK"),
    ("IN_REVIEW", "QUEUED_FOR_INTEGRATION"),
    ("REWORK", "RUNNING"),
}


def is_legal_transition(src, dst):
    return (src, dst) in ALLOWED_TRANSITIONS


def can_tick(state):
    """只有 ACCEPTED 才能勾 5-tasks checkbox(未 Review 不可完成)。"""
    return state == "ACCEPTED"


# ---------- Wave review schema(設計 §11)----------

def validate_wave_review(review, wave_tasks):
    errors = []
    if review.get("schema") != "devflow-wave-review.v1":
        errors.append(f"schema 非 devflow-wave-review.v1:{review.get('schema')}")
    seen = set()
    for e in review.get("tasks", []):
        tid = e.get("task")
        if tid in seen:
            errors.append(f"{tid} 重複 entry(同一 T 多筆 verdict;後筆不得覆蓋前筆,"
                          f"先 FAIL 後 PASS 必須整份退回重審)")
        seen.add(tid)
    entries = {e.get("task"): e for e in review.get("tasks", [])}
    for wt in wave_tasks:
        if wt not in entries:
            errors.append(f"缺 {wt} 的獨立 verdict")
        elif entries[wt].get("verdict") not in ("PASS", "FAIL"):
            errors.append(f"{wt} verdict 非法:{entries[wt].get('verdict')}")
    for tid in entries:
        if tid not in wave_tasks:
            errors.append(f"{tid} 不在本 wave,不得出現於 wave review")
    for entry in review.get("tasks", []):
        for finding in entry.get("findings", []):
            owner = finding.get("task")
            if not owner or owner not in wave_tasks:
                errors.append(f"finding {finding.get('id', '?')} 缺 task 歸屬或歸屬不在本 wave")
    if review.get("integration_verdict") not in ("PASS", "FAIL"):
        errors.append("缺 integration_verdict(或值非法)")
    return errors


# ---------- 4-spec Verification Profile(OC-4:fast+high 拒絕)----------

def spec_profile(spec_text):
    """讀 4-spec 的 lane / Risk(Verification Profile)。缺 = legacy(None)。

    Owner Call 例外(OC-4 fast+high)只認**結構化專用欄**,一行一欄、理由必填:
        - Owner Call 例外:<非空理由>
    (「Owner-Call 例外」/半形冒號亦可。)雜訊行 —— 標題、敘述、任何只是同時
    出現 Owner Call / fast / high 字樣的行 —— 一律不觸發(E2E N2 教訓:寬鬆
    關鍵字比對會被措辭誤觸,例外裁決必須是明確結構才算數)。"""
    lane = risk = None
    owner_call = False
    for line in spec_text.splitlines():
        m = re.match(r"^\s*-?\s*[Ll]ane:\s*([a-z]+)\b", line)
        if m:
            lane = m.group(1)
        m = re.match(r"^\s*-\s*Risk:\s*([a-z]+)\b", line)
        if m and risk is None:
            risk = m.group(1)
        if re.match(r"^\s*-\s*Owner[- ]Call ?例外\s*[::]\s*\S", line, re.IGNORECASE):
            owner_call = True
    return {"lane": lane, "risk": risk, "owner_call_fast_high": owner_call}


def contract_agg_hash(contract_hashes):
    """契約 hash 聚合值(status/candidate 對照用單一短 hash)。"""
    payload = "\n".join(f"{k}:{v}" for k, v in sorted(contract_hashes.items()))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
