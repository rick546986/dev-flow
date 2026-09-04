"""事件 / context manifest / prompt registry 驗證器。

規則正本 = observability/schema/*.schema.json(本模組只解讀,不重抄規則)。
錯誤格式:{"code", "field", "msg"};空 list = 通過。
error codes:bad_json / missing_field / unknown_field / unknown_event_type /
invalid_format / invalid_enum / hook_forbidden_field /
privacy_forbidden_key / privacy_value_leak / privacy_value_too_long /
registry_inconsistent
"""
import datetime
import hashlib
import json
import os
import re

_SCHEMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schema")
_cache = {}


_CONTRACT_DIR = os.path.join(_SCHEMA_DIR, "..", "..")   # repo 根(devflow-contract.json 正本)


# ── 值洩漏形狀(不用裸字比對,見 #98 回歸紀錄)────────────────────
# (a) 賦值形 secret:password/token/... 後接 : 或 =,再接 6+ 非空白字元
_VALUE_LEAK_ASSIGN = re.compile(
    r"(?i)\b(?:password|passwd|pwd|secret|token|api[_-]?key)\s*[:=]\s*\S{6,}"
)
# (b) 已知憑證前綴(OpenAI/Anthropic/AWS/GitHub/Slack/JWT/PEM 私鑰/Bearer token)。
# 前面補 (?<![A-Za-z0-9]) 是因為 "sk-" 不加鎖字界會吃到 risk-assessment、
# disk-encryption 這類合法英文字(#98 教訓的同型回歸,換了觸發詞而已);
# 字元類也放寬含 - _,才擋得住 sk-live-...、sk-proj-... 這類含連字號的真實金鑰。
_VALUE_LEAK_CRED = re.compile(
    r"(?<![A-Za-z0-9])sk-ant-"
    r"|(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{8,}"
    r"|(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}"
    r"|(?<![A-Za-z0-9_])gh[pousr]_[A-Za-z0-9]{20,}"
    r"|(?<![A-Za-z0-9])xox[bpas]-"
    r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|Bearer\s+(?=[A-Za-z0-9._-]*\d)[A-Za-z0-9._-]{16,}"   # 至少含一位數字,排除 Bearer authentication-middleware 這類敘述
)
# (c) 對話結構:同一字串內 ≥3 行以 user/assistant/human/system(或中文)開頭
_VALUE_LEAK_CONV_LINE = re.compile(
    r"(?im)^\s*(?:user|assistant|human|system|使用者|助理)\s*[:：]"
)


def _value_leak(s):
    """值命中「洩漏形狀」:賦值形 secret、已知憑證前綴、或對話結構。
    不比對裸字(transcript/password 等單字本身),避免誤殺合法工程敘述
    (見 #98 PR #110 回歸:'removed the password field...' 曾被誤擋)。"""
    if _VALUE_LEAK_ASSIGN.search(s) or _VALUE_LEAK_CRED.search(s):
        return True
    return len(_VALUE_LEAK_CONV_LINE.findall(s)) >= 3


def _load(name):
    if name not in _cache:
        with open(os.path.join(_SCHEMA_DIR, name)) as f:
            _cache[name] = json.load(f)
    return _cache[name]


def _resolve_item_enum(spec):
    """array 欄的受控 enum:item_enum_source = '<repo 根檔名>#<key>'。
    正本住 devflow-contract.json(6.3),schema 只留指標,不重抄一份值。"""
    src = spec.get("item_enum_source")
    if not src:
        return spec.get("item_enum")
    key = "contract:" + src
    if key not in _cache:
        fname, _, field = src.partition("#")
        with open(os.path.join(_CONTRACT_DIR, fname)) as f:
            _cache[key] = json.load(f)[field]
    return _cache[key]


def task_tags_enum():
    """task_tags 受控 enum 現值(唯一正本 = devflow-contract.json)。"""
    return list(_resolve_item_enum(
        _load("agent-event.schema.json")["fields"]["task_tags"]))


def _err(code, field, msg):
    return {"code": code, "field": field, "msg": msg}


# ── 欄位型別檢查 ────────────────────────────────────────────────


def _check_field(name, value, spec, errors):
    t = spec["type"]
    if t == "string":
        if not isinstance(value, str) or not re.match(spec["pattern"], value):
            errors.append(_err("invalid_format", name,
                               f"須符合 {spec['pattern']}, 得到 {value!r}"))
        elif "maxlen" in spec and len(value) > spec["maxlen"]:
            # 6.6:欄位級長度上限(共享契約 §6 表),逐欄報錯含欄名與上限
            errors.append(_err("invalid_format", name,
                               f"{name} 長度 {len(value)} 超過上限 "
                               f"{spec['maxlen']}"))
    elif t == "text":
        if not isinstance(value, str):
            errors.append(_err("invalid_format", name, "須為字串"))
        elif len(value) > spec.get("maxlen", 500):
            errors.append(_err("invalid_format", name,
                               f"{name} 長度 {len(value)} 超過上限 "
                               f"{spec['maxlen']}"))
    elif t == "line":
        # 單行短摘要(ID-10 result_summary/command_ref):禁換行、禁長輸出
        if not isinstance(value, str):
            errors.append(_err("invalid_format", name, "須為字串"))
        elif "\n" in value or "\r" in value:
            errors.append(_err("invalid_format", name,
                               "須為單行(完整輸出住 artifact,不進 ledger)"))
        elif len(value) > spec.get("maxlen", 200):
            errors.append(_err("invalid_format", name,
                               f"{name} 長度 {len(value)} 超過上限 "
                               f"{spec['maxlen']}(一行摘要,禁塞完整輸出)"))
    elif t == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(_err("invalid_format", name, "須為整數"))
        elif "min" in spec and value < spec["min"]:
            errors.append(_err("invalid_format", name, f"須 ≥ {spec['min']}"))
    elif t == "enum":
        if value not in spec["values"]:
            errors.append(_err("invalid_enum", name,
                               f"須為 {spec['values']} 之一, 得到 {value!r}"))
    elif t == "timestamp":
        ok = False
        if isinstance(value, str):
            try:
                ok = datetime.datetime.fromisoformat(value).tzinfo is not None
            except ValueError:
                ok = False
        if not ok:
            errors.append(_err("invalid_format", name,
                               "須為含時區偏移的 ISO8601 時間"))
    elif t == "array":
        if not isinstance(value, list):
            errors.append(_err("invalid_format", name, "須為陣列(多選值請逐項列出)"))
            return
        item_enum = _resolve_item_enum(spec)
        for i, item in enumerate(value):
            if not isinstance(item, str):
                errors.append(_err("invalid_format", f"{name}[{i}]", "須為字串"))
            elif "item_pattern" in spec and not re.match(spec["item_pattern"], item):
                errors.append(_err("invalid_format", f"{name}[{i}]",
                                   f"須符合 {spec['item_pattern']}"))
            elif "item_maxlen" in spec and len(item) > spec["item_maxlen"]:
                errors.append(_err("invalid_format", f"{name}[{i}]",
                                   f"{name} 值長度 {len(item)} 超過上限 "
                                   f"{spec['item_maxlen']}"))
            elif item_enum is not None and item not in item_enum:
                errors.append(_err("invalid_enum", f"{name}[{i}]",
                                   f"須為受控 enum {item_enum} 之一, "
                                   f"得到 {item!r}(正本 = devflow-contract.json)"))
    elif t == "prompt":
        _check_prompt_object(name, value, errors)


def _check_prompt_object(name, value, errors):
    schema = _load("agent-event.schema.json")["prompt_object"]
    if not isinstance(value, dict):
        errors.append(_err("invalid_format", name, "prompt 須為物件 {id,version,hash}"))
        return
    for req in schema["required"]:
        if req not in value:
            errors.append(_err("missing_field", f"{name}.{req}", "prompt 物件必填"))
    allowed = set(schema["required"]) | set(schema["optional"])
    for key, val in value.items():
        if key not in allowed:
            errors.append(_err("unknown_field", f"{name}.{key}",
                               "prompt 物件僅允許 id/version/hash/source_sha/"
                               "rubric_version/context_packet_version(防 body 走私)"))
        else:
            _check_field(f"{name}.{key}", val, schema["fields"][key], errors)


# ── 隱私掃描(六節紅線)────────────────────────────────────────


def _privacy_scan(obj, errors, path=""):
    privacy = _load("agent-event.schema.json")["privacy"]
    forbidden_exact = set(privacy["forbidden_exact"])
    substrings = privacy["forbidden_substrings"]
    allow = set(privacy["allowlist_exact"])
    max_len = privacy["max_string_len"]

    def scan_value(s, p):
        # dict 值、list 元素、字串葉節點三種路徑都走這個函式(#98:list 內
        # 字串曾經完全不掃)。
        if len(s) > max_len:
            errors.append(_err("privacy_value_too_long", p,
                               f"字串長 {len(s)} 超過 {max_len}"
                               "(ledger 不收完整 transcript/log/source,只收 ref/hash)"))
        if _value_leak(s):
            errors.append(_err("privacy_value_leak", p,
                               "值命中洩漏樣式(憑證前綴／賦值形 secret／對話結構,"
                               "隱私紅線)"))

    def walk(node, p):
        if isinstance(node, dict):
            for k, v in node.items():
                kp = f"{p}.{k}" if p else k
                low = str(k).lower()
                while low.startswith("x_"):          # 剝到底,#98:曾只剝一層
                    low = low[2:]
                if low not in allow:
                    if low in forbidden_exact:
                        errors.append(_err("privacy_forbidden_key", kp,
                                           f"禁載欄位 {k!r}(隱私紅線)"))
                        continue
                    if any(s in low for s in substrings):
                        errors.append(_err("privacy_forbidden_key", kp,
                                           f"欄位名 {k!r} 命中禁載樣式(隱私紅線)"))
                        continue
                walk(v, kp)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{p}[{i}]")
        elif isinstance(node, str):
            scan_value(node, p)

    walk(obj, path)


# ── 事件驗證 ────────────────────────────────────────────────────


def validate_event(event):
    """驗證單一事件 dict;回傳錯誤 list(空 = 通過)。"""
    schema = _load("agent-event.schema.json")
    errors = []
    if not isinstance(event, dict):
        return [_err("bad_json", "", "事件須為 JSON object")]

    env = schema["envelope"]
    for req in env["required"]:
        if req not in event:
            errors.append(_err("missing_field", req, "envelope 必填"))

    etype = event.get("event_type")
    edef = schema["events"].get(etype) if isinstance(etype, str) else None
    if etype is not None and edef is None:
        errors.append(_err("unknown_event_type", "event_type",
                           f"{etype!r} 不是已定義 lifecycle 事件"))

    allowed = set(env["required"]) | set(env["optional"])
    required_here = list(env["required"])
    if edef:
        allowed |= set(edef["required"]) | set(edef["optional"])
        required_here += edef["required"]

    for req in required_here:
        if req not in event and _err("missing_field", req, "envelope 必填") not in errors:
            errors.append(_err("missing_field", req, f"{etype} 必填欄位"))

    for cond in schema["conditional_required"].get(etype or "", []):
        if event.get(cond["when_field"]) == cond["equals"]:
            for req in cond["require"]:
                if req not in event:
                    errors.append(_err(
                        "missing_field", req,
                        f"{etype}: {cond['when_field']}={cond['equals']} 時必填"
                        "(失敗先分類再路由,指南 #five-laws 驗證五律 5)"))

    for group in schema.get("at_least_one_of", {}).get(etype or "", []):
        if not any(f in event for f in group):
            errors.append(_err("missing_field", "|".join(group),
                               f"{etype} 至少須有其一(status 為正式欄,"
                               "result 為相容別名,ID-10)"))

    for rule in schema.get("field_consistency", {}).get(etype or "", []):
        if not isinstance(rule, dict) or "a" not in rule:
            continue
        a, b = event.get(rule["a"]), event.get(rule["b"])
        if a is not None and b is not None and rule["map"].get(a) != b:
            errors.append(_err(
                "inconsistent_fields", f"{rule['a']}/{rule['b']}",
                f"{rule['a']}={a!r} 與 {rule['b']}={b!r} 不一致"
                f"(對應表 {rule['map']};unverified/n-a 不得帶 {rule['b']})"))

    fields = schema["fields"]
    for key, value in event.items():
        if key.startswith("x_"):
            continue                                 # 擴充欄位:只受隱私掃描約束
        if key not in allowed:
            errors.append(_err("unknown_field", key,
                               f"{etype} 不接受欄位 {key!r}(擴充請用 x_ 前綴)"))
            continue
        if key in fields:
            _check_field(key, value, fields[key], errors)

    if event.get("writer") == "hook":
        for banned in schema["hook_forbidden_fields"]:
            if banned in event:
                errors.append(_err(
                    "hook_forbidden_field", banned,
                    "hooks 不得推測 Agent Role / Prompt / model(七節);"
                    "歸屬由 Coordinator 在 derive 時關聯"))

    _privacy_scan(event, errors)
    return errors


def validate_event_line(line):
    """驗證一行 JSONL;解析失敗回 bad_json。"""
    try:
        obj = json.loads(line)
    except ValueError as e:
        return [_err("bad_json", "", f"JSON 解析失敗: {e}")]
    return validate_event(obj)


# ── context manifest ───────────────────────────────────────────


def validate_context_manifest(manifest):
    schema = _load("context-manifest.schema.json")
    errors = []
    if not isinstance(manifest, dict):
        return [_err("bad_json", "", "manifest 須為 JSON object")]
    for req in schema["required"]:
        if req not in manifest:
            errors.append(_err("missing_field", req, "context manifest 必填"))
    allowed = set(schema["required"]) | set(schema["optional"])
    for key, value in manifest.items():
        if key.startswith("x_"):
            continue
        if key not in allowed:
            errors.append(_err("unknown_field", key, f"不接受欄位 {key!r}"))
            continue
        _check_field(key, value, schema["fields"][key], errors)
    _privacy_scan(manifest, errors)
    return errors


def context_manifest_hash(manifest):
    """canonical JSON(排序鍵、緊湊分隔)之 sha256 → context_manifest_hash 欄位值。"""
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ── prompt registry ────────────────────────────────────────────


def validate_prompt_registry(registry):
    schema = _load("prompt-registry.schema.json")
    errors = []
    if not isinstance(registry, dict):
        return [_err("bad_json", "", "registry 須為 JSON object")]
    for req in schema["required"]:
        if req not in registry:
            errors.append(_err("missing_field", req, "registry 必填"))
    if "schema" in registry:
        _check_field("schema", registry["schema"], schema["fields"]["schema"], errors)
    prompts = registry.get("prompts", {})
    if not isinstance(prompts, dict):
        return errors + [_err("invalid_format", "prompts", "須為物件")]
    for pid, entry in prompts.items():
        _check_field("prompts:<id>", pid, schema["fields"]["prompt_id"], errors)
        if not isinstance(entry, dict):
            errors.append(_err("invalid_format", f"prompts.{pid}", "須為物件"))
            continue
        cur = entry.get("current_version")
        if cur is None:
            errors.append(_err("missing_field", f"prompts.{pid}.current_version", "必填"))
        else:
            _check_field(f"prompts.{pid}.current_version", cur,
                         schema["fields"]["current_version"], errors)
        versions = entry.get("versions")
        if not isinstance(versions, list) or not versions:
            errors.append(_err("missing_field", f"prompts.{pid}.versions",
                               "須為非空陣列"))
            continue
        seen = set()
        for i, ventry in enumerate(versions):
            vp = f"prompts.{pid}.versions[{i}]"
            if not isinstance(ventry, dict):
                errors.append(_err("invalid_format", vp, "須為物件"))
                continue
            for req in schema["version_entry"]["required"]:
                if req not in ventry:
                    errors.append(_err("missing_field", f"{vp}.{req}", "必填"))
            for key, value in ventry.items():
                if key in schema["fields"]:
                    _check_field(f"{vp}.{key}", value, schema["fields"][key], errors)
            v = ventry.get("version")
            if v in seen:
                errors.append(_err("registry_inconsistent", f"{vp}.version",
                                   f"版本 {v} 重複"))
            seen.add(v)
        if cur is not None and seen and cur not in seen:
            errors.append(_err("registry_inconsistent",
                               f"prompts.{pid}.current_version",
                               f"current_version {cur} 不在 versions 內"))
    _privacy_scan(registry, errors)
    return errors
