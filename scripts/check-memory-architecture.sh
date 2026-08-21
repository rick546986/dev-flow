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
# 這一輪新增的維度也要釘住(P0-1…P1-6):少了它們,退步不會現形。
required_ids = {
    "status-stale-zh": "STALE 不得回 OK",
    "status-ok-zh": "已驗證的現況要回 OK",
    "correction-history-zh": "修正歷史查得到",
    "correction-history-mixed": "中英混合也查得到修正歷史",
    "exact-symbol-cjk": "exact symbol + 中文",
    "false-why-zh": "沒有 decision 時 WHY 不得硬猜",
}
case_ids = {case.get("id") for case in dataset["cases"]}
missing_ids = sorted(set(required_ids) - case_ids)
if missing_ids:
    bad("評測新維度", "缺 {0}".format(
        ["{0}({1})".format(i, required_ids[i]) for i in missing_ids]))
else:
    ok("評測資料集含本輪 6 個新維度")
statuses_covered = {case.get("expect_status") for case in dataset["cases"]}
for needed in ("OK", "NEEDS_VERIFICATION", "NO_RELIABLE_MATCH"):
    if needed not in statuses_covered:
        bad("評測 status 覆蓋", "沒有任何案例期望 {0}".format(needed))
    else:
        ok("評測含 expect_status={0} 的案例".format(needed))

thresholds = dataset.get("thresholds") or {}
for name in ("stale_hit_rate", "wrong_branch_rate", "no_hit_precision",
             "status_accuracy"):
    if name not in thresholds:
        bad("評測門檻", "缺 {0} 門檻".format(name))
    else:
        ok("評測門檻含 {0}={1}".format(name, thresholds[name]))

# ⑧ 耐久性屏障(durability barrier):不得在耐久性建立之前把狀態往前推。
# 這三條各對應一個實際發生過、而且**不會讓任何測試變紅**的缺陷 ——
# local DB 自己是自洽的,要到另一台機器 rebuild 才發現記憶不見了。
devtalk_src = read("memory/agentmem/devtalk.py")
i_correct = devtalk_src.find("def correct(")
i_after = devtalk_src.find("def checkpoint(", i_correct + 1)
correct_body = (devtalk_src[i_correct:i_after]
                if i_correct >= 0 and i_after > i_correct else None)
if correct_body is None:
    bad("devtalk.correct 抽取", "找不到 correct() ~ checkpoint() 窗口")
elif "SUPERSEDED" in correct_body and "upsert_knowledge" in correct_body:
    bad("correct() 提早 supersede",
        "correct() 裡同時出現 upsert_knowledge 與 SUPERSEDED —— 更正在固化"
        "成功之前就把舊值下架了。更正失敗(敏感內容 / abort / 寫檔失敗)時"
        "這個 key 在 local 沒有現況、在 durable 還是舊值,答案取決於這台機器"
        "有沒有 rebuild 過")
else:
    ok("correct() 不在 consolidation 成功前 supersede 現況")

sync_src = read("memory/agentmem/sync.py")
i_write = sync_src.find("durable.append_events(")
i_mark = sync_src.find("lineage.mark_durable(")
if i_write < 0 or i_mark < 0:
    bad("revision 落地順序", "找不到 append_events / mark_durable")
elif i_mark < i_write:
    bad("revision 落地順序",
        "mark_durable 出現在 append_events 之前 —— 寫檔失敗時 revision 已被"
        "標成已耐久,永遠不會再被嘗試,而 .dev-flow/ 裡從來沒有它")
else:
    ok("revision 先寫進 .dev-flow 才標 durable")

i_pef = sync_src.find("def promote_entity_facts(")
i_pef_end = sync_src.find("\ndef ", i_pef + 1)
pef_body = (sync_src[i_pef:i_pef_end] if i_pef >= 0 and i_pef_end > i_pef
            else None)
if pef_body is None:
    bad("promote_entity_facts 抽取", "找不到 promote_entity_facts 窗口")
elif "signal.gate(" not in pef_body:
    bad("fact 整檔寫回沒過 Signal Gate",
        "promote_entity_facts 整檔寫回一個 entity 的所有 fact,但沒有逐筆過"
        "gate —— fact 進 local DB 的路不只候選一條(truth.reverify / 公開 CLI"
        " verify --observed 直接寫值),一筆乾淨的候選會把同 entity 裡未檢查的"
        "鄰居一起帶進 Git")
else:
    ok("fact 整檔寫回時逐筆重過 Signal Gate(durable writer 是最後一道防線)")

# 整檔取代 + 筆數視窗 = 刪掉視窗外的那些。它們上一輪已經在檔裡也已經
# durable=1,這一輪的取代把它們拿掉,而 local 仍聲稱「我就是檔裡的那份」
# —— durable-check 於是判 PASS 在一個不完整的鏡射上,砍掉 local 重建後
# 那些 fact 永遠回不來。docstring 不算證據,看的是實際呼叫。
pef_code = (re.sub(r'"""[\s\S]*?"""', "", pef_body) if pef_body else None)
if pef_code is None:
    pass  # 上面已經報過抽取失敗
elif re.search(r"store\.facts\([^)]*limit\s*=\s*(?!None)", pef_code):
    bad("durable 現況檔會被截斷",
        "promote_entity_facts 給 store.facts 傳了筆數視窗 —— 整檔取代會把視窗"
        "外的 fact 從 `.dev-flow/` 刪掉,而它們在 local 仍標 durable=1。"
        "任何預設值都會在「記憶夠多」的那天變成靜默資料遺失")
elif "statuses=" not in pef_code:
    bad("durable 現況檔的 status 過濾沒下推",
        "promote_entity_facts 沒把 statuses 下推到查詢 —— 過濾套在取列之後的"
        "話,夠多的 SUPERSEDED 鄰居就能把唯一的現況擠出去")
else:
    ok("durable 現況檔整檔取代時不設筆數視窗、status 下推到查詢")

if "durable_check" not in sync_src:
    bad("durable-check", "sync.py 沒有 durable_check —— 「記憶真的離開這台機器"
                         "了嗎」沒有任何可複驗的判定")
else:
    ok("durable_check 存在(Stage 6 W6-4 的機械驗證)")

# fact / event 的 durable 寫入發生在 consolidate 的候選迴圈**之後**(fact 要整個
# entity 一起寫回、event 要整批 append),所以它們的候選在迴圈裡只能登記、不能
# 結案。提早結案 = 寫檔失敗後重跑再也看不到它,`.dev-flow/` 永遠缺那一筆。
i_cons = sync_src.find("def consolidate(")
i_cons_end = sync_src.find("\n# ─────", i_cons + 1)
cons_body = (sync_src[i_cons:i_cons_end] if i_cons >= 0 and i_cons_end > i_cons
             else None)
if cons_body is None:
    bad("consolidate 抽取", "找不到 consolidate 窗口")
else:
    i_fact = cons_body.find('elif kind == "fact":')
    i_event = cons_body.find('elif kind == "event":')
    i_else = cons_body.find("\n        else:", max(i_fact, i_event))
    branch = (cons_body[min(i_fact, i_event):i_else]
              if i_fact >= 0 and i_event >= 0 and i_else > 0 else None)
    if branch is None:
        bad("fact/event 分支抽取", "找不到 consolidate 的 fact / event 分支")
    elif "CONSOLIDATED" in branch:
        bad("fact/event 候選提早結案",
            "consolidate 的 fact/event 分支裡出現 CONSOLIDATED —— 這兩類的"
            "durable 寫入在迴圈之後才發生,提早結案的話 write_state /"
            " append_events 失敗後重跑不再看到這筆候選,而 local 自洽、"
            "沒有任何測試會紅")
    else:
        ok("fact/event 候選只在 durable 寫入成功後才結案")

    i_add = cons_body.find("store.add_event(")
    i_append = cons_body.find("durable.append_events(")
    if i_add < 0 or i_append < 0:
        bad("event 落地順序", "找不到 add_event / append_events")
    elif i_add < i_append:
        bad("event 落地順序",
            "store.add_event(durable=True) 出現在 append_events 之前 —— "
            "local 宣稱已耐久,而 .dev-flow/ 要等後面才寫。寫檔失敗時那句"
            "「已耐久」指向一個不存在的檔,且是靜默的")
    else:
        ok("event 先寫進 .dev-flow 才在 local 標 durable")

# finalization 一律要求 session == OPEN。ABORTED 之後還能 checkpoint 的話,
# 「中止」就只是一個沒有效力的標籤 —— 使用者說先不要改,候選照樣進 Git。
session_src = read("memory/agentmem/session.py")
i_cp = session_src.find("def checkpoint(")
i_cp_end = session_src.find("\ndef ", i_cp + 1)
cp_body = (session_src[i_cp:i_cp_end] if i_cp >= 0 and i_cp_end > i_cp
           else None)
if cp_body is None:
    bad("session.checkpoint 抽取", "找不到 checkpoint 窗口")
elif "require_open(" not in cp_body:
    bad("checkpoint 沒有 fail closed",
        "session.checkpoint 沒有 require_open —— ABORTED / CLOSED / 不存在的"
        " session 都還能走 durable path。abort 的語意是「這一輪不算」,"
        "它之後還能把候選固化進 Git 等於中止沒有效力")
else:
    ok("checkpoint 要求 session == OPEN(finalization 一律 fail closed)")

store_src = read("memory/agentmem/store.py")
i_end = store_src.find("def end_session(")
i_end_stop = store_src.find("\n    def ", i_end + 1)
end_body = (store_src[i_end:i_end_stop] if i_end >= 0 and i_end_stop > i_end
            else None)
if end_body is None:
    bad("end_session 抽取", "找不到 end_session 窗口")
# **docstring 不算證據。** 先剝掉再比對:否則一句解釋這條不變量的註解就足以
# 讓守衛通過,而 SQL 本身早已被改掉 —— 守衛被自己的說明文字餵飽了。
elif "AND status='OPEN'" not in re.sub(r'"""[\s\S]*?"""', "", end_body):
    bad("end_session 不是 compare-and-set",
        "end_session 無條件 UPDATE —— abort 之後的 end 會把 ABORTED 覆寫成"
        " CLOSED,回顧時看不出那一輪其實沒收斂;不存在的 session 也會靜默"
        " no-op")
else:
    ok("end_session 是 OPEN → status 的 compare-and-set")

# durable 的 event append 必須以 event_id 去重並整檔原子取代。
# 「先寫檔、才動 local」對 deterministic 整檔取代的 writer 夠用,對 append-only
# 的 JSONL 不夠:檔案系統與 SQLite 沒有共同 transaction,「append 成功、local
# 還沒前進」那個視窗消不掉,而 open("a") 讓重跑把同一筆寫成第二行。
durable_src = read("memory/agentmem/durable.py")
i_ap = durable_src.find("def append_events(")
i_ap_end = durable_src.find("\ndef ", i_ap + 1)
ap_body = (durable_src[i_ap:i_ap_end] if i_ap >= 0 and i_ap_end > i_ap
           else None)
# docstring 不算證據(同 end_session 那條的理由):它解釋不變量,不實作它。
ap_code = re.sub(r'"""[\s\S]*?"""', "", ap_body) if ap_body else None
if ap_code is None:
    bad("append_events 抽取", "找不到 append_events 窗口")
elif '"a"' in ap_code or "'a'" in ap_code:
    bad("event append 不是原子取代",
        "append_events 還在用 append 模式 —— 同一個 event_id 重跑會變成第二"
        "行(JSONL 不是 keyed storage),而斷電會留下半行讓整個檔讀不出來")
elif "_atomic_write(" not in ap_code:
    bad("event append 不是原子取代",
        "append_events 沒有走 _atomic_write —— 寫到一半斷電會留下半行")
elif "event_id" not in ap_code:
    bad("event append 沒有去重依據",
        "append_events 沒有碰 event_id —— 沒有身分就無法在重跑時去重")
elif not re.search(r"seen\[event_id\]\s*!=", ap_code):
    # 釘的是「比內容」這個機制,不是有沒有出現 DurableError —— 檔裡另一條
    # (缺 event_id 就拒收)也會提供那個字串,守衛不能被它餵飽。
    bad("event 撞號被靜默吃掉",
        "append_events 看到已存在的 event_id 就跳過,沒有比對內容 —— 「id 已經"
        "在檔裡」只有在 id 真的決定內容時才等於「這筆寫過了」,推導 id 撞號時"
        "第二筆(內容不同的那筆)會永遠不存在而呼叫端拿到成功")
else:
    ok("event append 以 event_id 去重 + 整檔原子取代 + 撞號 fail closed")

# durable-check 的 remote 那一項必須問遠端本身。`rev-parse origin/<branch>` 是
# 本機快取:別台機器 force-push 或刪掉 branch 之後它還指著我的 commit,於是這
# 一關會替一個伺服器上已經不存在的 commit 背書 —— 那正是它唯一要防的事。
i_dchk = sync_src.find("def durable_check(")
i_dchk_end = sync_src.find("\ndef ", i_dchk + 1)
dchk_body = (sync_src[i_dchk:i_dchk_end] if i_dchk >= 0 and i_dchk_end > i_dchk
             else None)
if dchk_body is None:
    bad("durable_check 抽取(remote 觀察)", "找不到 durable_check 窗口")
elif "_observe_remote(" not in dchk_body:
    bad("durable-check 沒有觀察遠端",
        "durable_check 沒有走 _observe_remote —— 只比對本機追蹤 ref 的話,"
        "遠端被改掉時它仍判 PASS,而這一關的問句正是「記憶離開這台機器了嗎」")
elif "ls-remote" not in sync_src:
    bad("durable-check 沒有問遠端",
        "沒有任何 ls-remote —— fetch 會改本機 ref(判定改變被判定的狀態),"
        "而 rev-parse 只問快取")
else:
    ok("durable-check 向遠端本身查證 HEAD(追蹤 ref 是快取,不是證據)")

# 連得上不等於在別台機器上。`origin` 可以是 /Volumes/backup/mirror.git、
# file:///…、ssh://git@localhost/… —— 這些都會讓 ls-remote 回報正確的 SHA,
# 而硬碟壞掉時它們跟工作樹一起消失。這一關的問句是「記憶離開這台機器了嗎」,
# 所以 URL 必須先被判定成別台機器,而且判的要是**改寫後**的 URL。
i_obs = sync_src.find("def _observe_remote(")
i_obs_end = sync_src.find("\ndef ", i_obs + 1)
obs_code = (sync_src[i_obs:i_obs_end] if i_obs >= 0 and i_obs_end > i_obs
            else None)
if obs_code is None:
    bad("_observe_remote 抽取", "找不到 _observe_remote 窗口")
elif "remote_is_offmachine(" not in executable_only(obs_code):
    bad("本機 remote 被當成離開本機的證據",
        "_observe_remote 沒有判定 remote 是否在別台機器上 —— 本機 bare repo、"
        "file://、localhost 都會讓 ls-remote 回報正確的 SHA,於是 durable-check"
        "判 PASS 而記憶其實跟工作樹在同一顆硬碟上")
elif "--get-url" not in executable_only(sync_src):
    bad("remote URL 判的是字面值不是實際連線目標",
        "沒有走 ls-remote --get-url —— `url.<base>.insteadOf` 會在連線時把設定"
        "檔裡的網路 URL 改寫成本機路徑,只讀 remote.<name>.url 的話那條路會"
        "掛著網路形狀的名字通過判定")
else:
    ok("durable-check 只認別台機器上的 remote(改寫後的 URL)")

# URL 形狀判定只看字面 host。一個具名的非 loopback 主機仍然可能解析回這台
# 機器(/etc/hosts 或內網 DNS 把 remote.example.test 重映到 127.0.0.1、或這
# 台機器自己的另一個介面),ls-remote 一樣回報正確的 SHA。所以形狀過關之後
# 還要再解析 host、驗位址不是 loopback/link-local/本機介面。
if obs_code is None:
    bad("_observe_remote 抽取(endpoint 解析)", "找不到 _observe_remote 窗口")
elif "resolve_host_ips(" not in executable_only(obs_code):
    bad("durable-check 沒有解析 remote 的位址",
        "_observe_remote 判過 URL 形狀之後沒有再解析 host 拿位址證據 —— "
        "remote.example.test 這類具名主機被重映到 127.0.0.1 或本機介面時,"
        "只看形狀會誤判成離開了這台機器")
elif "ip_is_offmachine(" not in executable_only(obs_code):
    bad("durable-check 解析出位址後沒有驗證",
        "_observe_remote 呼叫了 resolve_host_ips 卻沒有把結果拿去過 "
        "ip_is_offmachine —— 解析出位址不等於驗過它不是這台機器自己")
else:
    ok("durable-check 解析 remote 主機名並驗位址不是 loopback/本機介面")

# verdict 不得再把「只驗到本機」與「遠端真的觀察過」壓成同一個 PASS
# (owner 裁決 D-3)。--local-only 走的是 rev-parse <upstream> —— 本機快取,
# 所以 `pushed` 會是 True 而伺服器從頭到尾沒被問過;只讀 verdict 的呼叫端
# 因此分不出兩者,而「記憶離開這台機器了嗎」的答案完全取決於分得出來。
if dchk_body is None:
    bad("durable_check 抽取(verdict 三值)", "找不到 durable_check 窗口")
elif "LOCAL_ONLY_PASS" not in executable_only(dchk_body):
    bad("local-only 與遠端觀察過共用同一個 verdict",
        "durable_check 沒有回 LOCAL_ONLY_PASS —— --local-only 跳過的正是"
        "唯一的遠端證據,卻與真的觀察過遠端拿到同一個 PASS,呼叫端無從分辨")
else:
    ok("durable-check verdict 把 local-only 與遠端觀察過分開(LOCAL_ONLY_PASS)")

# PASS 必須由**證據**推導,不得由呼叫端傳進來的 local_only 旗標推導
# (owner 裁決 D-2)。旗標說的是「呼叫端要求了什麼」,remote_ref_matches
# 說的是「實際拿到什麼證據」。釘證據那一側才擋得住「未來多一條也拿不到
# 遠端證據的路徑,忘了加分支就靜默回 PASS」。
if dchk_body is None:
    bad("durable_check 抽取(PASS 推導來源)", "找不到 durable_check 窗口")
elif "remote_ref_matches" not in executable_only(dchk_body):
    bad("durable-check 沒有 remote_ref_matches 這個誠實欄位",
        "durable_check 沒有算出/回報 remote_ref_matches —— 呼叫端只剩 `pushed`"
        "可讀,而 local-only 路徑的 pushed 來自本機追蹤 ref,它為真並不代表"
        "伺服器被問過")
elif not re.search(r"elif\s+remote_ref_matches\s*:", executable_only(dchk_body)):
    bad("PASS 不是從遠端 ref 證據推導出來的",
        "durable_check 有 remote_ref_matches 這個欄位,但 PASS 那一支不是"
        "由它決定 —— 欄位變成只是附註,verdict 仍可能在沒有遠端證據時說 PASS"
        "(守衛不能被自己要檢查的那個字串餵飽)")
else:
    ok("durable-check 的 PASS 由 remote_ref_matches 推導,不由 local_only 旗標")

# 兩個誠實欄位是必填,不是成功時才附上的裝飾。選填的話呼叫端得寫 .get(),
# 而 None 在布林語境下與 False 同義 —— 少一個欄位會靜默降級成某一邊,
# 取決於呼叫端怎麼寫,而不是取決於實際證據。
if dchk_body is None:
    bad("durable_check 抽取(誠實欄位必填)", "找不到 durable_check 窗口")
else:
    missing = [f for f in ("remote_ref_matches", "preflight_not_known_local")
               if '"{0}":'.format(f) not in dchk_body]
    if missing:
        bad("durable-check 的誠實欄位不是必填",
            "回傳 dict 裡沒有 {0} —— 呼叫端只能 .get(),而 None 與 False "
            "在布林語境下同義,少一個欄位就靜默降級".format("/".join(missing)))
    else:
        ok("durable-check 必填回報 remote_ref_matches 與 "
           "preflight_not_known_local")

# 檢索命中之後,答案的內容必須用主鍵撈。拿已知主鍵去掃「最近 N 筆」是錯的:
# 檢索索引沒有那個視窗,命中較舊的 decision/skill 時撈不到內容,而呼叫端仍然
# 回 OK —— 聲稱有可靠答案卻沒附上構成答案的欄位,比查不到更糟。
hydration = re.findall(r"store\.(decisions|skills)\(limit=\d+\)", query_src)
if hydration:
    bad("WHY/HOW 用「最近 N 筆」撈已知主鍵",
        "query.py 仍在 store.{0}(limit=…) 裡掃已知 id —— 命中視窗外的紀錄時"
        "reason/steps 撈不到,而 status 仍然是 OK".format(hydration[0]))
elif not re.search(r"store\.decision_row\(", query_src) \
        or not re.search(r"store\.skill_row\(", query_src):
    bad("WHY/HOW 沒有主鍵撈",
        "query.py 沒有走 store.decision_row / store.skill_row —— 檢索命中的是"
        "一個已知主鍵,撈它的內容不該經過任何視窗")
else:
    ok("WHY/HOW 的內容用主鍵撈(檢索索引沒有「最近 N 筆」這個視窗)")

# revision 的 event_id 不得隨機:去重的依據是 event_id,而隨機 id 讓去重永遠
# 對不上 —— 同一次 supersede 會在 events/ 累積成 N 筆,每筆都聲稱是它。
i_rev = sync_src.find("revision_records.append(")
window = sync_src[max(0, i_rev - 600):i_rev] if i_rev >= 0 else None
if window is None:
    bad("revision event_id 抽取", "找不到 revision_records 窗口")
elif 'ids.new_id("event")' in window:
    bad("revision event_id 是隨機的",
        "revision 的 event_id 用 ids.new_id —— 寫檔成功而 local 還沒前進時"
        "重跑會補寫成第二筆,而 durable 去重的依據正是 event_id")
elif "_derived_id(" not in window:
    bad("revision event_id 不是推導的",
        "revision 的 event_id 沒有從 revision_id 推導 —— 重跑必須補寫同一筆")
else:
    ok("revision 的 event_id 由 revision_id 推導(重跑補寫同一筆)")

# 候選不是進 facts 表的唯一一條路。`verify --observed`(公開 CLI)直接改值,
# 不建候選 —— consolidate 少了這一段的話,`.dev-flow/state/` 的現況檔會停在
# 舊值,砍掉 SQLite 再 rebuild 就退回 v1,而 local 說它 VERIFIED。
if cons_body is None:
    pass  # 上面已經 bad 過抽取失敗,不重複計數
elif "entities_pending_durable(" not in cons_body:
    bad("現況檔不會被重寫",
        "consolidate 沒有把 durable=0 的 live fact 的 entity 納入重寫 —— "
        "reverify 產生的新 current truth 永遠不會離開這台機器(revision 是"
        "歷史,不是現況物化視圖的替代品)")
else:
    ok("consolidate 會重寫所有還沒落地的 fact entity(不只候選碰到的)")

# durable-check 要分開報「歷史沒落地」與「現況沒落地」。只報前者的話,
# 「revision 寫成功、現況檔沒重寫」會判 PASS。
i_dc = sync_src.find("def durable_check(")
i_dc_end = sync_src.find("\ndef ", i_dc + 1)
dc_body = (sync_src[i_dc:i_dc_end] if i_dc >= 0 and i_dc_end > i_dc else None)
if dc_body is None:
    bad("durable_check 抽取", "找不到 durable_check 窗口")
elif "entities_pending_durable(" not in dc_body:
    bad("durable-check 漏掉現況沒落地",
        "durable_check 沒有檢查還沒重寫的 fact entity —— 「歷史沒落地」與"
        "「現況沒落地」是兩件事,只報前者的話後者是靜默的")
else:
    ok("durable-check 同時檢查現況檔還沒重寫的 entity")

# git status 解析不完整必須被 Current Truth 消化。parser 拒絕猜是對的,但那份
# 不確定性斷在 resolve_current 的話,系統會同時說「有一部分我看不懂」與
# 「VERIFIED + fast_path」。
truth_src = read("memory/agentmem/truth.py")
i_rc = truth_src.find("def resolve_current(")
i_rc_end = truth_src.find("\ndef ", i_rc + 1)
rc_body = (truth_src[i_rc:i_rc_end] if i_rc >= 0 and i_rc_end > i_rc else None)
# **docstring 與註解都不算證據。** 光找 "status_unparsed" 這個字串會被死碼
# 餵飽:把判斷式改成常數 False、留著底下那個引用它的分支,字串還在而行為
# 已經沒了。所以剝掉解釋性文字之後,還要釘住它真的參與 STALE 的判斷式。
rc_code = re.sub(r'"""[\s\S]*?"""', "", rc_body) if rc_body else None
rc_code = re.sub(r"(?m)#.*$", "", rc_code) if rc_code else None
i_cond = rc_code.find("if changed or dirty") if rc_code else -1
cond_line = (rc_code[i_cond:rc_code.find("\n", i_cond)] if i_cond >= 0 else "")
if rc_code is None:
    bad("resolve_current 抽取", "找不到 resolve_current 窗口")
elif "status_unparsed" not in rc_code:
    bad("解析不完整沒有 fail closed",
        "resolve_current 不看 status_unparsed —— git status 有讀不懂的欄位時"
        "dirty 清單是不完整的,而沒有指紋可比的依賴只剩 dirty 能證明它乾淨,"
        "卻仍然回 OK fast path")
elif i_cond < 0 or cond_line.strip() == "if changed or dirty:":
    bad("解析不完整沒有進入 STALE 判斷",
        "status_unparsed 出現在 resolve_current 裡,但 STALE 的判斷式仍是"
        " `if changed or dirty` —— 那個引用是死碼,行為上仍然回 OK fast path"
        "(守衛不能被自己要檢查的那個字串餵飽)")
else:
    ok("git status 解析不完整時,無指紋的依賴不得走 fast path")

MIN_CHECKS = 55
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
