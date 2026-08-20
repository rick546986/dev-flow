#!/bin/bash
# check-memory-architecture.sh — Agent Memory 架構不變量的機械守衛(Repo-local)。
#
# 為什麼需要:memory 的核心分界全是**散文規則**,退回時不會有紅字 ——
#   ①`.dev-flow/` 進 Git、`.devflow/` 不進 Git(只差一個連字號,寫錯就是記憶不同步
#     或本機暫存被 commit)
#   ②durable 層不得依賴 SQLite、local 層不得依賴 durable(單向相依;反向會讓
#     「砍掉本機索引可重建」這條保證失效)
#   ③失效掃描只掃 implementation truth,**不得掃 knowledge**(§10:改一支不相關的
#     TypeScript 不能讓已確認的業務規則變成不可信)
#   ④沒有全域 `code > everything` 排序(domain 的權威在人身上)
#   ⑤`dev-setup` 是唯一 setup 入口 —— CLI 不得出現 init 之類的第二個安裝器
#   ⑥意圖分類用的線索詞與相關性計算用的框架詞是**兩份**,且帶內容的線索
#     (怎麼部署)不得進剝除清單(進了會讓「怎麼部署?」查不到 deploy 流程)
#   ⑦契約/能力宣告與程式碼裡的常數必須同值
#   ⑦b retrieval status 契約(四態)在程式碼 / 契約檔 / README 三處同值
#   ⑧評測資料集必須涵蓋六種問句意圖與三種語言(中/英/混合)
#
# 這八條每一條都對應一個真實的失敗模式,而且都是「壞掉之後所有既有檢查照樣全綠」
# 的型別 —— 與本 repo 其他守衛同一個理由存在。
#
# 用法:
#   scripts/check-memory-architecture.sh [root]   # 缺省 root = repo root
#
# exit:0 = 全過 / 1 = 有不變量被破壞 / 2 = 檢查自身無法執行(fail-closed,不猜)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import json
import os
import re
import sys

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root = sys.argv[1]
problems = []
checks = 0


def read(rel, required=True):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        if required:
            print("FATAL: 找不到 {0}".format(rel), file=sys.stderr)
            sys.exit(2)
        return None
    with open(path, encoding="utf-8") as stream:
        return stream.read()


def ok(label):
    global checks
    checks += 1
    print("  ✓ " + label)


def bad(label, detail):
    global checks
    checks += 1
    problems.append("{0}:{1}".format(label, detail))
    print("  ✗ {0}:{1}".format(label, detail))


# ── ①目錄分界 ──────────────────────────────────────────────────────────────
gitignore = read(".gitignore")
lines = [line.strip() for line in gitignore.splitlines()
         if line.strip() and not line.strip().startswith("#")]
if ".devflow/" in lines:
    ok(".gitignore 忽略 `.devflow/`(本機執行期暫存)")
else:
    bad(".gitignore", "缺 `.devflow/` —— 本機執行期暫存會被 commit 進去")
ignored_durable = [line for line in lines
                   if line.replace("/", "") in (".dev-flow", "!.dev-flow")
                   and not line.startswith("!")]
if ignored_durable:
    bad(".gitignore", "把 `.dev-flow/` 也忽略掉了({0})—— durable memory 就是要進 Git,"
                      "忽略它等於跨機器完全同步不到".format(ignored_durable))
else:
    ok(".gitignore 沒有忽略 `.dev-flow/`(durable memory 要進 Git)")

# ── ②單向相依 ──────────────────────────────────────────────────────────────
durable_src = read("memory/agentmem/durable.py")
if re.search(r"^\s*import\s+sqlite3|^\s*from\s+sqlite3", durable_src, re.M):
    bad("durable 層相依", "durable.py import 了 sqlite3 —— durable 是檔案格式層,"
                          "不該知道本機索引怎麼存")
else:
    ok("durable.py 不依賴 sqlite3(檔案格式層與索引層分離)")

store_src = read("memory/agentmem/store.py")
if re.search(r"^\s*from\s+\.\s+import\s+[^\n]*\bdurable\b", store_src, re.M):
    bad("local 層相依", "store.py import 了 durable —— 相依必須單向"
                        "(durable → local 由 sync.py 負責),反向會讓"
                        "「砍掉本機索引可重建」失效")
else:
    ok("store.py 不依賴 durable(相依單向,由 sync.py 搬運)")

# ── ③失效掃描不得碰 knowledge ─────────────────────────────────────────────
truth_src = read("memory/agentmem/truth.py")


def executable_only(source):
    # 剝掉 docstring 與整行註解,只留會被執行的行。兩個方向都要防:註解裡寫了規則
    # 不算做到(本 repo 的註冊自審踩過那一面);註解裡**解釋**「這裡刻意不碰
    # knowledge」也不該被判成違規(反向的假陽性)。守衛比的一律是會被執行的行。
    stripped = re.sub(r'"""(?:.|\n)*?"""', "", source)
    return "\n".join(line for line in stripped.splitlines()
                      if not line.lstrip().startswith("#"))


bodies = re.findall(r"^def invalidate_[a-z_]+\(.*?(?=^def |\Z)", truth_src,
                    re.M | re.S)
if not bodies:
    print("FATAL: truth.py 找不到任何 invalidate_* 函式 —— 抽取窗口壞了",
          file=sys.stderr)
    sys.exit(2)
leaks = [b for b in bodies
         if re.search(r"\bknowledge\b|upsert_knowledge", executable_only(b))]
if leaks:
    bad("domain 失效隔離", "invalidate_* 內出現 knowledge —— §10:domain truth 不套"
                           "檔案指紋失效規則,改一支不相關的檔不能讓業務規則變不可信")
else:
    ok("invalidate_*({0} 支)只掃 facts,不碰 knowledge".format(len(bodies)))

# ── ④沒有全域 code > everything ───────────────────────────────────────────
tables = re.findall(r"^([A-Z_]+_AUTHORITY)\s*=\s*\{(.*?)\}", truth_src,
                    re.M | re.S)
if len(tables) < 4:
    bad("authority 表", "只找到 {0} 張權威表,預期至少 4 張"
                        "(implementation/domain/intent/decision)".format(len(tables)))
else:
    ok("四類記憶各有自己的權威表({0} 張)".format(len(tables)))
authority = dict(tables)
impl = authority.get("IMPLEMENTATION_AUTHORITY", "")
domain = authority.get("DOMAIN_AUTHORITY", "")


def score(block, key):
    m = re.search(r'"{0}"\s*:\s*(\d+)'.format(re.escape(key)), block)
    return int(m.group(1)) if m else None


impl_code = score(impl, "current_code")
impl_claim = score(impl, "user_claim")
domain_expert = score(domain, "domain_expert")
domain_code = score(domain, "code_inference")
if None in (impl_code, impl_claim, domain_expert, domain_code):
    bad("authority 分數", "抽不到比較用的分數(表結構改了?)—— fail-closed,不猜")
elif impl_code > impl_claim and domain_expert > domain_code:
    ok("權威排序不對稱:implementation 由程式碼說話、domain 由人說話")
else:
    bad("authority 排序", "出現全域 `code > everything` 傾向 —— domain truth 的權威"
                          "必須高於程式碼推論,否則程式寫錯業務規則時記憶會跟著錯")

# ── ⑤唯一 setup 入口 ──────────────────────────────────────────────────────
cli_src = read("memory/dev-memory.py")
if re.search(r'add_parser\(\s*["\']init["\']', cli_src):
    bad("唯一 setup 入口", "CLI 出現 init 子指令 —— dev-setup 必須是唯一入口")
else:
    ok("CLI 沒有 init 子指令(dev-setup 是唯一 setup 入口)")
if 'add_parser("setup"' not in cli_src:
    bad("setup 子指令", "CLI 缺 setup 子指令(dev-setup 要靠它做 memory 階段)")
else:
    ok("CLI 有 setup 子指令供 dev-setup 呼叫")

setup_skill = read("skills/dev-setup/SKILL.md")
if "memory/dev-memory.py" not in setup_skill:
    bad("dev-setup 掛載", "skills/dev-setup/SKILL.md 沒有呼叫 memory/dev-memory.py"
                          " —— 安裝器沒接上記憶建置,採用專案跑完 dev-setup 也沒有記憶")
else:
    ok("dev-setup SKILL.md 呼叫 memory/dev-memory.py")

# ── ⑥線索詞兩份、帶內容的線索不得進剝除清單 ────────────────────────────────
cues_src = read("memory/agentmem/cues.py")
if "INTENT_CUES" not in cues_src or "PURE_FRAME_CUES" not in cues_src:
    bad("線索詞正本", "cues.py 缺 INTENT_CUES 或 PURE_FRAME_CUES —— 分類用與剝除用"
                      "必須是兩份,合成一份會讓帶內容的線索被剝掉")
else:
    ok("cues.py 同時有 INTENT_CUES(分類)與 PURE_FRAME_CUES(剝除)")
pure = re.search(r"PURE_FRAME_CUES\s*=\s*\((.*?)\n\)", cues_src, re.S)
if pure is None:
    bad("PURE_FRAME_CUES", "抽不到內容 —— fail-closed,不猜")
else:
    content_bearing = [w for w in ("怎麼部署", "怎麼跑", "步驟", "業務規則的內容")
                       if '"' + w + '"' in pure.group(1)
                       or "r\"" + w + "\"" in pure.group(1)]
    forbidden = [w for w in ("怎麼部署", "怎麼跑") if w in pure.group(1)]
    if forbidden:
        bad("剝除清單", "帶內容的線索 {0} 進了 PURE_FRAME_CUES —— 「怎麼部署?」的"
                        "內容詞會被一起剝掉,查不到 deploy 流程".format(forbidden))
    else:
        ok("PURE_FRAME_CUES 不含帶內容的線索(怎麼部署 / 怎麼跑)")

# ── ⑦契約 / 能力宣告與程式碼常數同值 ──────────────────────────────────────
init_src = read("memory/agentmem/__init__.py")
local_version = re.search(r"LOCAL_SCHEMA_VERSION\s*=\s*(\d+)", init_src)
durable_version = re.search(r"DURABLE_SCHEMA_VERSION\s*=\s*(\d+)", init_src)
if not (local_version and durable_version):
    print("FATAL: agentmem/__init__.py 抽不到 schema 版本常數", file=sys.stderr)
    sys.exit(2)
contract = json.loads(read("devflow-contract.json"))
caps = json.loads(read("hooks/runtime-capabilities.json"))
for label, source, key, expected in (
        ("contract.memory_local", contract["schema_versions"], "memory_local",
         local_version.group(1)),
        ("contract.memory_durable", contract["schema_versions"], "memory_durable",
         durable_version.group(1)),
        ("runtime.memory_local", caps["schema_versions"], "memory_local",
         local_version.group(1)),
        ("runtime.memory_durable", caps["schema_versions"], "memory_durable",
         durable_version.group(1))):
    actual = source.get(key)
    if str(actual) != expected:
        bad(label, "宣告 {0!r} ≠ 程式碼常數 {1!r}".format(actual, expected))
    else:
        ok("{0} = {1}".format(label, expected))

if "agent_memory_v3" not in caps.get("capabilities", []):
    bad("能力宣告", "runtime-capabilities.json 沒宣告 agent_memory_v3")
else:
    ok("runtime-capabilities.json 宣告 agent_memory_v3")

memory_contract = contract.get("memory") or {}
default_dir = re.search(r'DEFAULT_MEMORY_DIR\s*=\s*"([^"]+)"',
                        read("memory/agentmem/identity.py"))
if not default_dir:
    print("FATAL: identity.py 抽不到 DEFAULT_MEMORY_DIR", file=sys.stderr)
    sys.exit(2)
if memory_contract.get("durable_dir") != default_dir.group(1):
    bad("contract.memory.durable_dir",
        "契約寫 {0!r},程式碼預設 {1!r}".format(
            memory_contract.get("durable_dir"), default_dir.group(1)))
else:
    ok("contract.memory.durable_dir = {0}".format(default_dir.group(1)))
if memory_contract.get("setup_entry") != "dev-setup":
    bad("contract.memory.setup_entry",
        "應為 dev-setup(唯一入口),實得 {0!r}".format(
            memory_contract.get("setup_entry")))
else:
    ok("contract.memory.setup_entry = dev-setup")

# ── ⑦b retrieval status 契約:程式碼 / 契約檔 / README 三處同值 ────────────
# 這一條防的是「狀態在程式碼裡改了,契約檔與 README 沒跟上」——
# 外部 runtime 照契約檔實作,對不上的狀態會被當成未知值處理。
query_src = read("memory/agentmem/query.py")
declared = re.search(r"RETRIEVAL_STATUSES\s*=\s*\(([^)]*)\)", query_src, re.S)
if not declared:
    print("FATAL: query.py 抽不到 RETRIEVAL_STATUSES", file=sys.stderr)
    sys.exit(2)
# 元素是識別字(`retrieval.OK` / `NEEDS_VERIFICATION`),不是字面字串 ——
# 抓引號會抓到零個而讓這條檢查靜默失效,所以抓識別字並剝掉模組前綴。
code_statuses = {name.split(".")[-1]
                 for name in re.findall(r"[A-Za-z_][A-Za-z0-9_.]*",
                                        declared.group(1))}
contract_statuses = set(memory_contract.get("retrieval_status_values") or [])
expected_statuses = {"OK", "NEEDS_VERIFICATION", "CONFLICT", "NO_RELIABLE_MATCH"}
if contract_statuses != expected_statuses:
    bad("contract.retrieval_status_values",
        "契約寫 {0},預期 {1}".format(sorted(contract_statuses),
                                     sorted(expected_statuses)))
else:
    ok("contract.retrieval_status_values 四態齊")
if code_statuses != expected_statuses:
    bad("query.RETRIEVAL_STATUSES",
        "程式碼寫 {0},預期 {1}".format(sorted(code_statuses),
                                       sorted(expected_statuses)))
else:
    ok("query.RETRIEVAL_STATUSES 與契約同值")
readme = read("README.md")
missing_doc = [s for s in sorted(expected_statuses) if s not in readme]
if missing_doc:
    bad("README status 契約", "README 沒說明 {0}".format(missing_doc))
else:
    ok("README 說明了四個 retrieval status")
# 嚴重度排序必須存在且方向正確(STALE 不得被當成 OK 的同級)
if not re.search(r"_SEVERITY\s*=\s*\{", query_src):
    bad("status 嚴重度", "query.py 沒有 _SEVERITY —— 多筆結果無法收斂成最嚴重的那個")
else:
    ok("query.py 有 status 嚴重度排序")

# ── ⑧評測資料集覆蓋面 ─────────────────────────────────────────────────────
dataset = json.loads(read("memory/fixtures/eval/dataset.json"))
languages = {case.get("language") for case in dataset["cases"]}
missing_lang = {"zh", "en", "mixed"} - languages
if missing_lang:
    bad("評測語言覆蓋", "缺 {0}".format(sorted(missing_lang)))
else:
    ok("評測資料集覆蓋中文 / 英文 / 中英混合")
kinds = {case.get("expect_kind") for case in dataset["cases"]}
missing_kind = {"CURRENT", "HISTORY", "WHY", "HOW", "DOMAIN", "INTENT"} - kinds
if missing_kind:
    bad("評測意圖覆蓋", "缺 {0}".format(sorted(missing_kind)))
else:
    ok("評測資料集覆蓋六種問句意圖")
no_hit = [c for c in dataset["cases"]
          if c.get("expect_status") == "NO_RELIABLE_MATCH"]
if not no_hit:
    bad("評測 no-hit 案", "沒有任何期望 NO_RELIABLE_MATCH 的案例 —— 「查不到就說"
                          "查不到」這條沒有被量測,退回成亂撈不會現形")
else:
    ok("評測資料集含 {0} 個 no-hit 案".format(len(no_hit)))
thresholds = dataset.get("thresholds") or {}
for name in ("stale_hit_rate", "wrong_branch_rate", "no_hit_precision"):
    if name not in thresholds:
        bad("評測門檻", "缺 {0} 門檻".format(name))
    else:
        ok("評測門檻含 {0}={1}".format(name, thresholds[name]))

MIN_CHECKS = 28
if checks < MIN_CHECKS:
    print("FATAL: 只跑了 {0} 項檢查(地板 {1})—— 抽取窗口可能壞了".format(
        checks, MIN_CHECKS), file=sys.stderr)
    sys.exit(2)

print()
if problems:
    print("⛔ check-memory-architecture:{0} 項不變量被破壞".format(len(problems)),
          file=sys.stderr)
    for problem in problems:
        print("   - " + problem, file=sys.stderr)
    sys.exit(1)
print("✅ check-memory-architecture:{0} 項不變量全過".format(checks))
PY
