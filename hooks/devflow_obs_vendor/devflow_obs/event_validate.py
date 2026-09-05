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
# (a) 賦值形 secret:password/token/... 後接 : 或 =(含全形冒號 ：,比照
# _VALUE_LEAK_CONV_LINE,r2-#98 F3),再接 6+ 非空白字元(v1)。起頭鎖字界改用
# (?<![A-Za-z0-9]) 而不是 \b:\b 在底線前後不成立詞界,access_token=/
# refresh_token=/id_token=/client_secret: 這類複合詞會漏網(r2-#98 F2)。
# 詞表不放裸 "pwd"(r3-#98 F4,low):"pwd" 常見於「pwd=/usr/local/bin」這種
# shell 路徑輸出(current working directory),不是密碼;password/passwd 這
# 兩個詞不會有這種歧義,保留。
_VALUE_LEAK_ASSIGN = re.compile(
    r"(?i)(?<![A-Za-z0-9])"
    r"(?:password|passwd|secret|token|api[_-]?key)"
    r"\s*[:=：]\s*(?P<v1>\S{6,})"
)
# transcript/conversation/messages 是「賦值形才擋、裸字放行」的敘事型欄位
# (r2-#98 F5)。獨立成自己的正則(不跟 v1 共用一個 alternation)是刻意的:
# v2 的殘值要交給 Python 端判斷是否「像逐字稿」(見下方 _looks_like_transcript),
# 一旦判斷結果可能是 False,若跟 v1 共用同一次 finditer match,greedy 的
# v2 會把行尾其餘內容(含可能藏在後面的 password=... )一起吞進同一個 match、
# 判完 False 後 finditer 從行尾繼續掃,導致藏在 v2 殘值裡的 v1 洩漏永遠掃不到
# (例:"messages: 3 pending. password=hunter2")。拆開後兩條正則各自對 s
# 獨立掃一輪,v1 不再受 v2 吞了多少字元影響(r3-#98)。
_VALUE_LEAK_NARRATIVE = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:transcript|conversation|messages)"
    r"\s*[:=：]\s*(?P<v2>\S.*)"
)
# 遮蔽標記:賦值形抓到值後,若整段值只是「已遮蔽」的佔位符,不算外洩
# (r2-#98 F4;例:secret=redacted、password=REDACTED、token=******)。
_VALUE_LEAK_MASKED = re.compile(
    r"(?i)^(?:\[?redacted\]?|<redacted>|filtered|\*{3,}|x{3,}|\.{3,}|null|none)$"
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
# v2(transcript/conversation/messages)賦值後的殘值要不要擋,交給 Python 端
# 判斷「像不像逐字稿」,不在正則裡疊第二個不定長量詞夾字面(ReDoS 形狀)。
# 三選一命中就算(r3-#98,兩個審查鏡頭同時抓到「messages: 3 pending」這類
# 日常狀態敘述被舊版 4 字元門檻誤殺):
#   - 角色標記:值裡任何位置含 user/assistant/human/system(或中文)接冒號
#     (不要求在行首,因為 v2 本身就是「賦值後的殘值」,不是整行);
#   - 引號對話:值裡有一段用引號包住的片段,折成詞數(見下方 _token_count)
#     ≥4 才算(門檻拉到 4 詞只是不讓「"old field name"」這類 ≤3 詞的短識別
#     字片段單獨觸發這條路徑;"can you reset my password" 這類 ≥4 詞的
#     逐字稿式引號句仍擋得住)。引號字元類同時收 ASCII 直引號、CJK 括號
#     「」『』、CJK 彎引號""(r3-#98 F3,medium:原本只認 ASCII 直引號,
#     中文/日文常見的「」/『』/彎引號完全漏網),開閉只要成對出現、不要求
#     同款(「...’ 這種混搭也算,判斷交給内容詞數,不是括號本身);
#   - 落單於前兩者之外:值本身要夠長(≥60 字元)且夠多詞(≥10 個以空白分開
#     的詞)才算。r3-#98 首版門檻定 40 字元/6 詞,收斂 F1 找碴發現
#     「messages: renamed "old field name" to "new field name"」
#     (44 字元 8 詞,引號內各段只有 3 詞,不吃引號路徑)這類短的工程改名
#     敘述也被通用路徑誤擋——裁定拉高到 60/10,純數字、狀態詞
#     (started/pending/none/ok/done/available/empty/n-a)、單一檔名或
#     路徑、短識別字改名敘述天生構不成這個門檻,一律放行;真的長得像逐字稿
#     的一般敘述(refund 案例 89 字元 17 詞)仍擋得住。門檻數字(60/10)是
#     dispatcher 裁定值,取捨屬 dispatcher,這裡不擅改。
#     詞數怎麼算(r3-#98 F2,high):val.split() 對中日韓文字沒用——中文
#     一整段話中間沒有空白,split() 永遠只切出 1 個「詞」,再長的中文逐字
#     稿轉述也跨不過詞數門檻。_token_count 額外把 CJK 碼點(中日韓統一表意
#     文字 U+4E00-9FFF、日文假名 U+3040-30FF、諺文音節 U+AC00-D7AF)逐字
#     元計 1 詞,跟空白斷詞的結果相加,長度門檻(60/4)不變。
_VALUE_LEAK_ROLE_MARK = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:user|assistant|human|system|使用者|助理)\s*[:：]"
)
# 引號字元類:開字元 "'「『""''(ASCII 直引號 + CJK 括號 + CJK 彎引號),
# 閉字元同一批,不要求跟開字元同款成對(見上方 F3 註解)。ASCII 直單引號
# ' 額外加字界鎖:contraction/所有格(don't、customer's)裡的撇號前後都是
# 字母,若不鎖字界,兩個這種撇號中間夾的英文字剛好 ≥4 詞就會被誤判成引號
# 對話(對抗審查抓到:"don't ship the customer's patch" 曾被誤擋)——開
# 撇號前面不能是字母/數字、閉撇號後面不能是字母/數字,真正的引號用法
# ("'can you...'" 這種)前後接的是空白或標點,不受影響;CJK 括號/彎引號
# 本身不跟英文縮寫共用字元,不需要這道鎖。
# ReDoS(r3-#98 第四輪對抗審查,blocker):內容類原本是 [^\n]{4,}?——開閉
# 引號類不對稱時(例如整段字串全是開引號 "「"*16000,沒有半個閉引號),
# 懶惰量詞從每個起點都會往後掃到字串尾端才確認失敗,O(n^2)(n=8000 實測
# 0.47s、16000 1.95s)。改成兩件事:(a) 內容類上界 200(單一引號片段本來
# 就不該長到需要無界掃描,判斷是不是逐字稿只在乎有沒有 ≥4 詞,不是有多
# 長);(b) 內容類額外排除所有引號字元本身(含開闔兩批),讓每個起點的內容
# 掃描一遇到任何引號字元就得停(不論那是不是合法的閉引號),不會被閉引號
# 之外的其他引號字元硬拖著往後掃——兩者合起來讓每個起點的工作量有界
# (≤200),總工作量變回線性。
_VALUE_LEAK_QUOTED_SPAN = re.compile(
    r"(?:[\"「『\u201c\u2018]|(?<![A-Za-z0-9])')"
    r"([^\n\"'「」『』\u201c\u201d\u2018\u2019]{4,200})"
    r"(?:[\"」』\u201d\u2019]|'(?![A-Za-z0-9]))"
)
_CJK_CHAR = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")
_NARRATIVE_MIN_LEN = 60
_NARRATIVE_MIN_WORDS = 10
_NARRATIVE_QUOTE_MIN_WORDS = 4


def _token_count(val, cap):
    """英數詞照空白切 + CJK 碼點各算 1 詞(見上方 F2 註解),回傳
    min(實際詞數, cap)——只在乎有沒有跨過門檻 cap,不必真數到底,對超長
    殘值(ReDoS 驗收案例:200KB 重複同一句)友善,找到 cap 個就提早結束。
    先把 CJK 字元換成空白再切英數詞(r3-#98 第四輪對抗審查,nit):不這樣
    做的話,一整段連續 CJK 字元(中間沒有空白)會先被 split() 算成 1 個
    「詞」,又在下面 CJK finditer 逐字元各加 1 次,同一段字元被算兩次。"""
    non_cjk = _CJK_CHAR.sub(" ", val)
    words = len(non_cjk.split(None, cap - 1))
    if words >= cap:
        return cap
    total = words
    for _ in _CJK_CHAR.finditer(val):
        total += 1
        if total >= cap:
            return cap
    return total


def _looks_like_transcript(val):
    """v2 殘值是否像逐字稿內容,見上方三選一規則的註解。"""
    if _VALUE_LEAK_ROLE_MARK.search(val):
        return True
    for m in _VALUE_LEAK_QUOTED_SPAN.finditer(val):
        span = m.group(1).strip()
        if _token_count(span, _NARRATIVE_QUOTE_MIN_WORDS) >= _NARRATIVE_QUOTE_MIN_WORDS:
            return True
    if len(val) < _NARRATIVE_MIN_LEN:
        return False
    return _token_count(val, _NARRATIVE_MIN_WORDS) >= _NARRATIVE_MIN_WORDS


def _value_leak(s):
    """值命中「洩漏形狀」:賦值形 secret、transcript/conversation/messages
    賦值形且值像逐字稿、已知憑證前綴、或對話結構;賦值形若整段值只是遮蔽標記
    (redacted/***/...)不算外洩(r2-#98 F4)。不比對裸字(transcript/password
    等單字本身),避免誤殺合法工程敘述(見 #98 PR #110 回歸:'removed the
    password field...' 曾被誤擋;r3-#98:'messages: 3 pending' 這類日常狀態
    敘述同理,見 _looks_like_transcript)。"""
    for m in _VALUE_LEAK_ASSIGN.finditer(s):
        v1 = m.group("v1")
        if v1 is not None and not _VALUE_LEAK_MASKED.match(v1):
            return True
    for m in _VALUE_LEAK_NARRATIVE.finditer(s):
        v2 = m.group("v2")
        if (v2 is not None and not _VALUE_LEAK_MASKED.match(v2)
                and _looks_like_transcript(v2)):
            return True
    if _VALUE_LEAK_CRED.search(s):
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


# r3-#98 第四輪對抗審查 F2(major):上一輪的 list 直屬字串 join(見下方
# walk() 內殘留註解)只看「list 裡直接是字串」這一種形狀,對
# [{"role":"user","content":"hi"},{"role":"assistant","content":"yo"},
# {"role":"user","content":"bye"}](OpenAI 訊息陣列,list 元素是 dict 不是
# 字串)、{"t1":"user: hi","t2":"assistant: yo","t3":"user: bye"}(逐字稿
# 被拆進一個 dict 的多個鍵而不是 list)兩種容器形狀完全視而不見。
#
# 修法:對每個容器節點(dict 或 list)遞迴收集其整棵子樹內所有字串葉節點的
# 對話行數,bottom-up 用整數相加(不是每層都重新 join/rescan 整棵子樹的
# 字串——那樣深層巢狀會變 O(n·depth));命中 ≥3 行就對該容器路徑報一次。
# OpenAI 風格的 {"role":"user","content":"hi"} 沒有「role: 」這種前綴長在
# content 值裡面,join 起來也不會命中 _VALUE_LEAK_CONV_LINE——所以額外判斷
# 一個 dict 是不是「role(值為 user/assistant/system/human)+ content/
# text/message」形狀的一個對話 turn;turn 本身不計進自己的對話行數,而是
# 回報給父層,父層(list 或 dict)直屬子節點裡湊到 ≥3 個 turn 也算對話結構
# 命中。兩個條件命中同一個容器路徑只報一次。
_TURN_ROLE_WORDS = {"user", "assistant", "system", "human"}
_TURN_CONTENT_KEYS = {"content", "text", "message"}


def _is_turn_dict(node):
    """node 是不是一個 role+content 對話 turn(鍵名不分大小寫)。"""
    lowered = {str(k).lower(): v for k, v in node.items()}
    role = lowered.get("role")
    if not isinstance(role, str) or role.strip().lower() not in _TURN_ROLE_WORDS:
        return False
    return any(k in lowered for k in _TURN_CONTENT_KEYS)


def _scan_conv_structure(node, p, errors):
    """回傳 (conv_count, turns, reported)。conv_count 是這個子樹內所有
    字串葉節點的對話行數總和;turns 是這個子樹內所有 role+content turn
    dict 的總數(含 node 自己,如果 node 本身就是一個 turn dict)。兩者都是
    bottom-up 整數相加(總工作量 O(子樹大小),不因為巢狀層數重複
    rescan)。reported 是這個子樹(含 node 自己)有沒有任何一筆因為這個
    機制報過 privacy_value_leak,只給根節點的例外判斷用(見下方)。
    r3-#98 第五輪對抗審查(major):上一輪的 turns 只數「直屬子節點是不是
    turn」,turn 藏在兄弟 list/dict 裡一層(例:
    {"a":[turn,turn],"b":[turn]})父層就完全看不到——list/dict 分支硬回傳
    turns=0/False,不繼續往上傳實際數字。改成子樹裡的 turn 總數整數相加,
    不管 turn 埋在直屬子節點還是更深的孫節點,只要同一個容器的子樹裡湊得到
    ≥3 個就算。
    子樹命中 conv_count + turns ≥ 3(兩種證據加總,不是各自獨立門檻),對這個容器
    路徑報一次 privacy_value_leak(兩個條件都中也只報一次;同一個 turn
    被多層祖先容器各自算進門檻、各自報一次是刻意的,見上一輪 F1/F2 決定,
    這裡不變)。
    根節點(p == "",_privacy_scan 頂層呼叫傳進來的 event/manifest/
    registry 本身)是唯一例外:turn 或對話行可能分散在好幾個頂層 x_*
    欄位,每個欄位自己都不到門檻,只有全部加總才到 ≥3——這種情況下沒有
    任何具名子路徑會報錯,原本「根節點不落地報錯,因為子路徑一定報過」的
    假設不成立,整個事件就這樣放行(r3-#98 第六輪對抗審查抓到:
    x_a=[T],x_b=[T],x_c=[T] 或 x_meta={"a":[T,T]},x_notes=[T] 都是
    []比對)。所以根節點改成:命中且子樹內沒有任何一個具名子路徑已經報過
    (reported 累積下來是 False)才在根節點自己報一次,path 用 "(event)"
    (訊息裡說明是分散在多個頂層欄位);子路徑已經報過就跳過,避免對同一件
    事重複報。"""
    if isinstance(node, str):
        return len(_VALUE_LEAK_CONV_LINE.findall(node)), 0, False
    if isinstance(node, dict):
        conv_count = 0
        turns = 1 if _is_turn_dict(node) else 0
        reported = False
        for k, v in node.items():
            c, t, r = _scan_conv_structure(v, f"{p}.{k}" if p else k, errors)
            conv_count += c
            turns += t
            reported = reported or r
        hit = conv_count + turns >= 3
        if p and hit:
            errors.append(_err(
                "privacy_value_leak", p,
                "容器子樹內字串葉節點合併後命中對話結構,或子樹內構成 ≥3 個"
                "role+content 對話 turn(隱私紅線;逐字稿被拆進多個鍵值或"
                "多個 turn 物件也算,turn 不必是直屬子節點)"))
            reported = True
        elif not p and hit and not reported:
            errors.append(_err(
                "privacy_value_leak", "(event)",
                "整個事件裡分散在多個頂層欄位的字串葉節點合併後命中對話"
                "結構,或分散的 role+content 對話 turn 合計 ≥3 個(隱私"
                "紅線;沒有任何單一具名欄位單獨達標,只有全部頂層欄位加總"
                "才到門檻,由根節點在這裡報一次)"))
            reported = True
        return conv_count, turns, reported
    if isinstance(node, list):
        conv_count = 0
        turns = 0
        reported = False
        for i, v in enumerate(node):
            c, t, r = _scan_conv_structure(v, f"{p}[{i}]", errors)
            conv_count += c
            turns += t
            reported = reported or r
        hit = conv_count + turns >= 3
        if p and hit:
            errors.append(_err(
                "privacy_value_leak", p,
                "容器子樹內字串葉節點合併後命中對話結構,或子樹內構成 ≥3 個"
                "role+content 對話 turn(隱私紅線;逐字稿被拆進多個 list"
                "元素或多個 turn 物件也算,turn 不必是直屬子節點)"))
            reported = True
        elif not p and hit and not reported:
            errors.append(_err(
                "privacy_value_leak", "(event)",
                "整個事件裡分散在多個頂層元素的字串葉節點合併後命中對話"
                "結構,或分散的 role+content 對話 turn 合計 ≥3 個(隱私"
                "紅線;沒有任何單一具名子路徑單獨達標,只有全部加總才到"
                "門檻,由根節點在這裡報一次)"))
            reported = True
        return conv_count, turns, reported
    return 0, 0, False


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
            # r3-#98 第四輪對抗審查(b):超過長度上限本來就是 backstop,已經
            # 報 privacy_value_too_long,不必再對這段超長字串跑一次
            # _value_leak(多條正則的完整掃描)——上限值本身(max_len,見
            # schema)已經界定「多長算太長」,不靠 _value_leak 兜底這段長度
            # 保護,提早 return 也順便把超長字串的 ReDoS 曝險面收斂到只剩
            # max_len 以內。
            return
        if _value_leak(s):
            errors.append(_err("privacy_value_leak", p,
                               "值命中洩漏樣式(憑證前綴／賦值形 secret／對話結構,"
                               "隱私紅線)"))

    def walk(node, p):
        if isinstance(node, dict):
            for k, v in node.items():
                kp = f"{p}.{k}" if p else k
                low = str(k).lower()
                # r2-#98 F1:while low.startswith("x_") 遇 x__transcript(雙底線)
                # 只剝掉 "x_" 兩字元,剩 "_transcript" 對 forbidden_exact 免疫。
                # 改成 regex 一次吃掉整段 (x + 1 個以上底線) 的重複前綴,
                # x__transcript / x___messages / x_x__body 都能剝到底。
                low = re.sub(r"^(?:x_+)+", "", low)
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
            # r3-#98 F1 的 list 直屬字串 join 邏輯已被下面的
            # _scan_conv_structure(遞迴、不限 list 直屬字串、也認
            # role+content turn 結構,見 F2 註解)取代,這裡只留逐元素
            # walk(forbidden-key/scan_value 那條路徑不變)。
            for i, v in enumerate(node):
                walk(v, f"{p}[{i}]")
        elif isinstance(node, str):
            scan_value(node, p)

    walk(obj, path)
    # r3-#98 F2(major):上面的 walk() 只逐元素掃字串葉節點本身
    # (forbidden-key、value_leak/too_long),不做「合併子樹判斷對話結構」
    # 這件事——那是另一個獨立的 bottom-up 遍歷,見 _scan_conv_structure。
    _scan_conv_structure(obj, path, errors)


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
