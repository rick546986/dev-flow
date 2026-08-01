"""事件 / context manifest / prompt registry 驗證器。

規則正本 = observability/schema/*.schema.json(本模組只解讀,不重抄規則)。
錯誤格式:{"code", "field", "msg"};空 list = 通過。
error codes:bad_json / missing_field / unknown_field / unknown_event_type /
invalid_format / invalid_enum / hook_forbidden_field /
privacy_forbidden_key / privacy_value_too_long / registry_inconsistent
"""
import datetime
import hashlib
import json
import os
import re

_SCHEMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schema")
_cache = {}


def _load(name):
    if name not in _cache:
        with open(os.path.join(_SCHEMA_DIR, name)) as f:
            _cache[name] = json.load(f)
    return _cache[name]


def _err(code, field, msg):
    return {"code": code, "field": field, "msg": msg}


# ── 欄位型別檢查 ────────────────────────────────────────────────


def _check_field(name, value, spec, errors):
    t = spec["type"]
    if t == "string":
        if not isinstance(value, str) or not re.match(spec["pattern"], value):
            errors.append(_err("invalid_format", name,
                               f"須符合 {spec['pattern']}, 得到 {value!r}"))
    elif t == "text":
        if not isinstance(value, str):
            errors.append(_err("invalid_format", name, "須為字串"))
        elif len(value) > spec.get("maxlen", 500):
            errors.append(_err("invalid_format", name,
                               f"長度 {len(value)} 超過上限 {spec['maxlen']}"))
    elif t == "line":
        # 單行短摘要(ID-10 result_summary/command_ref):禁換行、禁長輸出
        if not isinstance(value, str):
            errors.append(_err("invalid_format", name, "須為字串"))
        elif "\n" in value or "\r" in value:
            errors.append(_err("invalid_format", name,
                               "須為單行(完整輸出住 artifact,不進 ledger)"))
        elif len(value) > spec.get("maxlen", 200):
            errors.append(_err("invalid_format", name,
                               f"長度 {len(value)} 超過上限 {spec['maxlen']}"
                               "(一行摘要,禁塞完整輸出)"))
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
            errors.append(_err("invalid_format", name, "須為陣列"))
            return
        for i, item in enumerate(value):
            if not isinstance(item, str):
                errors.append(_err("invalid_format", f"{name}[{i}]", "須為字串"))
            elif "item_pattern" in spec and not re.match(spec["item_pattern"], item):
                errors.append(_err("invalid_format", f"{name}[{i}]",
                                   f"須符合 {spec['item_pattern']}"))
            elif "item_maxlen" in spec and len(item) > spec["item_maxlen"]:
                errors.append(_err("invalid_format", f"{name}[{i}]", "超長"))
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

    def walk(node, p):
        if isinstance(node, dict):
            for k, v in node.items():
                kp = f"{p}.{k}" if p else k
                low = str(k).lower()
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
        elif isinstance(node, str) and len(node) > max_len:
            errors.append(_err("privacy_value_too_long", p,
                               f"字串長 {len(node)} 超過 {max_len}"
                               "(ledger 不收完整 transcript/log/source,只收 ref/hash)"))

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
                        "(失敗先分類再路由,README §5 驗證五律 5)"))

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
