"""G3 — 雙閘門:`TYPESAFE_API_KEY` + 每專案 `.dev-flow/jev.yaml` opt-in。

生效等級 = min(mode, gates[Jn]),全序 off < shadow < live。
- 只有 key、沒 opt-in → off(零出境)。
- 只有 opt-in、沒 key → off(no-op)。
- `mode: off` + `gates: {J5: live}` → off(min)。
- opt-in 檔存在但沒列該 gate → owner default:J1 live、J3 live(recommendation)、J5 shadow、其餘 off。
- 預設**不建** opt-in 檔;dev-setup 只在使用者同意後建(P0-4)。
- J5 的 live **未核准**(W6 `J5_LIVE_RATIFIED = False`):yaml 寫 live 也 cap 成 shadow、reason 留痕;
  即使日後核准,route_taken 是否能 AUTO 仍由 policy 的 graduation 門檻另管(G6)。

yaml 解析刻意窄(同 memory/agentmem/yamlmini 的哲學):只認 `mode:` 與 `gates:` 兩鍵、
兩層縮排、純 scalar;其它形狀 fail-loud,不猜。唯一例外是 `gates: MR:`(W11 MR rerank / mr-gate):

    mode: shadow
    gates:
      # 簡寫 = {level: shadow}
      MR: shadow
    # 或區塊(第三層縮排 4 格,只認下列兩鍵):
    mode: shadow
    gates:
      MR:
        # level 必填:off|shadow|live
        level: shadow
        # min_queries 選填:正整數;mr-eval／mr-gate 的資料量地板(不寫 = 20,未校準暫定值)
        # min_queries: <N>

註解一律自成一行:值後面接 `# …` 會被當成值的一部分 → fail-loud(exit 2),例如
`MR: shadow  # 簡寫` 解析成 `'shadow  # 簡寫'` 不在 off/shadow/live。
MR 生效等級 = min(mode, gates.MR.level):`mode: off` 時 `MR: shadow` 也是 off(mr-gate 回 off、exit 0)。

MR 不是 J1–J5:不進 `GATES`／`gates` dict,解析結果放在 `optin["mr"]`(沒寫 = None)。
MR 的 live **未核准**(`MR_LIVE_RATIFIED = False`,同 J5):寫 live 也 cap 成 shadow。
雙閘門(key + opt-in)對 J1–J5 的語意一行不變。
"""
import os

from . import GATES, JevError, LEVELS

OPTIN_RELPATH = os.path.join(".dev-flow", "jev.yaml")
KEY_ENV = "TYPESAFE_API_KEY"
OWNER_DEFAULT_GATES = {"J1": "live", "J2": "off", "J3": "live", "J4": "off", "J5": "shadow"}
# W6 P3-1(2026-09-23):J5 live 未核准。yaml 寫 `gates.J5: live` 也只到 shadow —— 這是硬拒不是旗標:
# 沒有環境變數、CLI 參數或 yaml 鍵能翻它;要開 live 必須改這個常數(= 新 commit、走 P3-2 契約同步 + L2/ADR)。
J5_LIVE_RATIFIED = False
# W11 MR:研究分支沒有 MR live;`gates.MR: live` 也只到 shadow。改它 = 新 commit + owner 裁決,沒有旗標。
MR_LIVE_RATIFIED = False
MR_GATE = "MR"
MR_KEYS = ("level", "min_queries")
_RANK = {level: i for i, level in enumerate(LEVELS)}


def level_min(a, b):
    for level in (a, b):
        if level not in _RANK:
            raise JevError("未知等級 %r(只有 %s)" % (level, "/".join(LEVELS)))
    return a if _RANK[a] <= _RANK[b] else b


def _mr_min_queries(value, lineno):
    if not value.isdigit() or int(value) < 1:
        raise JevError("jev.yaml:%d gates.MR.min_queries %r 必須是正整數" % (lineno, value))
    return int(value)


def parse_optin(text):
    """解析 jev.yaml 子集 → {"mode": level, "gates": {Jn: level}, "mr": None | {"level", "min_queries"}}。fail-loud。"""
    mode = None
    gates = {}
    mr = None
    in_gates = False
    in_mr = False              # 正在讀 `  MR:` 的區塊(第三層)
    mr_block_line = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if "\t" in line:
            raise JevError("jev.yaml:%d tab 縮排不支援" % lineno)
        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()
        if in_mr and indent != 4:
            if mr.get("level") is None:
                raise JevError("jev.yaml:%d gates.MR 區塊缺 level:(off|shadow|live)" % mr_block_line)
            in_mr = False
        if indent == 0:
            in_gates = False
            if content == "gates:":
                in_gates = True
                continue
            if ":" not in content:
                raise JevError("jev.yaml:%d 不是 key: value" % lineno)
            key, _, value = content.partition(":")
            key, value = key.strip(), value.strip().strip('"')
            if key != "mode":
                raise JevError("jev.yaml:%d 未知頂層鍵 %r(只認 mode / gates)" % (lineno, key))
            if value not in LEVELS:
                raise JevError("jev.yaml:%d mode %r 不在 %s" % (lineno, value, "/".join(LEVELS)))
            mode = value
        elif indent == 2 and in_gates:
            key, sep, value = content.partition(":")
            key, value = key.strip(), value.strip().strip('"')
            if sep and key == MR_GATE:
                if mr is not None:
                    raise JevError("jev.yaml:%d gates.MR 重複" % lineno)
                if value:
                    if value not in LEVELS:
                        raise JevError("jev.yaml:%d gates.MR %r 不在 %s" % (lineno, value, "/".join(LEVELS)))
                    mr = {"level": value, "min_queries": None}
                else:
                    mr = {"level": None, "min_queries": None}
                    in_mr, mr_block_line = True, lineno
                continue
            if not sep or key not in GATES:
                raise JevError("jev.yaml:%d gates 鍵 %r 不是 J1–J5 或 MR" % (lineno, key))
            if value not in LEVELS:
                raise JevError("jev.yaml:%d gates.%s %r 不在 %s" % (lineno, key, value, "/".join(LEVELS)))
            gates[key] = value
        elif indent == 4 and in_mr:
            key, sep, value = content.partition(":")
            key, value = key.strip(), value.strip().strip('"')
            if not sep or key not in MR_KEYS:
                raise JevError("jev.yaml:%d gates.MR 未知鍵 %r(只認 %s)" % (lineno, key, " / ".join(MR_KEYS)))
            if mr.get("_seen_" + key):
                raise JevError("jev.yaml:%d gates.MR.%s 重複" % (lineno, key))
            mr["_seen_" + key] = True
            if key == "level":
                if value not in LEVELS:
                    raise JevError("jev.yaml:%d gates.MR.level %r 不在 %s" % (lineno, value, "/".join(LEVELS)))
                mr["level"] = value
            else:
                mr["min_queries"] = _mr_min_queries(value, lineno)
        else:
            raise JevError("jev.yaml:%d 縮排/結構不在支援子集" % lineno)
    if in_mr and mr.get("level") is None:
        raise JevError("jev.yaml:%d gates.MR 區塊缺 level:(off|shadow|live)" % mr_block_line)
    if mode is None:
        raise JevError("jev.yaml 缺 mode:(off|shadow|live)")
    if mr is not None:
        mr = {"level": mr["level"], "min_queries": mr["min_queries"]}
    return {"mode": mode, "gates": gates, "mr": mr}


def mr_effective_level(has_key, optin):
    """MR(rerank 出境)的生效等級 = min(mode, gates.MR.level),live cap 成 shadow;沒寫 gates.MR → 沿用 W11:只看 mode。
    沒 key／沒 opt-in → off(雙閘門不變)。回 (level, reason)。"""
    if not has_key:
        return "off", "no_api_key"
    if optin is None:
        return "off", "no_project_optin"
    mr = optin.get("mr")
    requested = optin["mode"] if mr is None else level_min(optin["mode"], mr["level"])
    how = "mode=%s" % optin["mode"] if mr is None else "min(mode=%s, gates.MR=%s)" % (optin["mode"], mr["level"])
    if requested == "off":
        return "off", how + "=off"
    if requested == "live" and not MR_LIVE_RATIFIED:
        return "shadow", "mr_live_not_ratified(%s=live; capped to shadow)" % how
    return requested, how


def load_optin(repo_root):
    """回 None = 專案未 opt-in(零出境)。檔在但壞 → fail-loud(不當成 off 靜默放過)。"""
    path = os.path.join(repo_root, OPTIN_RELPATH)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return parse_optin(fh.read())


def has_api_key(environ=None):
    environ = os.environ if environ is None else environ
    return bool((environ.get(KEY_ENV) or "").strip())


def effective_level(gate, has_key, optin):
    """回 (level, reason)。level ∈ LEVELS;reason 是人看得懂的一句。"""
    if gate not in GATES:
        raise JevError("未知 gate %r" % gate)
    if not has_key:
        return "off", "no_api_key"
    if optin is None:
        return "off", "no_project_optin"
    gate_level = optin["gates"].get(gate, OWNER_DEFAULT_GATES[gate])
    level = level_min(optin["mode"], gate_level)
    if level == "off":
        return "off", "min(mode=%s, gates.%s=%s)=off" % (optin["mode"], gate, gate_level)
    if gate == "J5" and level == "live" and not J5_LIVE_RATIFIED:
        return "shadow", "j5_live_not_ratified(requested min(mode=%s, gates.J5=%s)=live; capped to shadow)" % (
            optin["mode"], gate_level)
    return level, "min(mode=%s, gates.%s=%s)" % (optin["mode"], gate, gate_level)


def may_call(level):
    """只有 shadow/live 准出境。off 一律不呼叫、不 enqueue。"""
    return level in ("shadow", "live")
