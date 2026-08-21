"""Project identity(path-independent)與 local workspace metadata。

**核心規則**:`project_path` 不再是 identity,只是 local workspace metadata。

    identity(進 Git,跨機器同一份)   → .dev-flow/project.yaml 的 project_id
    workspace(不進 Git,每台機器一份)→ local SQLite 的 workspaces 表
                                        (local_path / os / branch / head / worktree)

同一個 project 在 Mac 的 `/Users/rick/dev/proj`、Windows 的 `D:\\dev\\proj`、
Linux 的 `/home/rick/proj` 是**同一個 project_id** —— 因為 project_id 來自
commit 進 Git 的 `project.yaml`,而不是來自 filesystem path。

remote repository 只能當 metadata/provenance(`origin` 欄),不能當 identity:
沒有 remote、remote 改名、fork、鏡像、同一份 code 推到兩個 remote,project_id 都不變。
"""
import ipaddress
import os
import platform
import re
import socket
import subprocess

from . import DURABLE_SCHEMA_VERSION, ids, paths, signal, yamlmini

MEMORY_DIR_ENV = "DEVFLOW_MEMORY_DIR"
DEFAULT_MEMORY_DIR = ".dev-flow"
PROJECT_FILE = "project.yaml"

_PROJECT_KEY_ORDER = ["schema_version", "project_id", "name", "created_at"]

_HEADER = """\
dev-flow durable Agent Memory —— project identity(進 Git,不要手改 project_id)。

project_id 是 path-independent 的 stable identity:
- 不含任何 filesystem path 成分 —— 換機器、改目錄名、換 worktree 都不變
- 不依賴 GitHub / remote URL —— origin 只是 provenance metadata
- dev-setup 重跑一律 reuse 既有值,不重新產生

本機的 local path / OS / branch / HEAD 屬 workspace metadata,住 local SQLite,
刻意不寫進這個檔(那些值每台機器不同,寫進 Git 只會製造無意義的 diff 與衝突)。"""


class IdentityError(RuntimeError):
    """identity 解析/建立失敗 —— 一律 fail-loud,不猜、不自動改寫既有 project_id。"""


def memory_dir_name():
    """durable memory 目錄名。預設 `.dev-flow`,可用 env 覆寫。

    為什麼留覆寫通道:本 repo 的 local runtime 目錄叫 `.devflow/`(無連字號、
    gitignored),durable 目錄叫 `.dev-flow/`(有連字號、進 Git)—— 兩者只差一個字元,
    是已知的命名風險。留一個單點覆寫,採用專案要改名時不必動程式碼。
    """
    return os.environ.get(MEMORY_DIR_ENV) or DEFAULT_MEMORY_DIR


def durable_root(repo_root_path):
    """durable memory 根目錄的絕對路徑(不建立目錄)。"""
    return os.path.join(repo_root_path, memory_dir_name())


def project_file(repo_root_path):
    return os.path.join(durable_root(repo_root_path), PROJECT_FILE)


# ── origin provenance 的淨化(單一入口)───────────────────────────────────────
# `remote.origin.url` 是**使用者的本機設定**,不是受控輸入。它實際上長成過:
#   https://user:ghp_xxx@github.com/org/repo.git   憑證
#   file:///Users/rick/dev/project                  本機絕對路徑
#   /Users/rick/dev/mirror.git                      本機絕對路徑
#   \\server\share\repo.git                        UNC
# 而 project.yaml 進 Git、會被 push —— 一旦進 commit,砍檔案不等於砍歷史。
#
# 設計取捨:provenance 是**選填**的 metadata,不是 identity(identity 是 ULID)。
# 所以這裡一律 **fail-safe 到不寫**:判不出安全就回 None,不猜、也不讓 setup 失敗。
_SCHEME_URL = re.compile(
    r"^(?P<scheme>https?|ssh|git)://"
    r"(?:(?P<userinfo>[^/@]*)@)?"
    r"(?P<host>[^/:?#\s]+)"
    r"(?P<port>:[0-9]+)?"
    r"(?P<path>/[^?#\s]*)?$")

# scp-like:`git@github.com:org/repo.git`(注意 host 後是冒號不是斜線)
_SCP_LIKE = re.compile(
    r"^(?:(?P<userinfo>[^/@:]+)@)?"
    r"(?P<host>[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+)"
    r":(?!/)(?P<path>[^\s?#]+)$")

_SAFE_HOST = re.compile(r"^[A-Za-z0-9._-]+$")
_SAFE_PATH = re.compile(r"^[A-Za-z0-9._~/-]*$")

# 明確不可寫進 durable 的 scheme:它們指向的是**這台機器**上的東西。
_LOCAL_SCHEMES = ("file://",)


# 唯一被接受的 userinfo:SSH 的慣例帳號 `git`(它不帶任何機密)。
# 其餘一律拒絕整條 URL,**不是**「剝掉 userinfo 後照用」——
# 理由:`https://ghp_xxx@host/…` 的 token 就住在 userinfo 位置,
# 而「哪些 userinfo 其實是 token」沒有可靠的判別法(pattern 永遠不完整)。
# 既然 provenance 是選填的,遇到任何非 `git` 的 userinfo 就整條放棄,
# 比「剝一剝應該就乾淨了」安全,而且規則一句話講得完。
_CREDENTIAL_FREE_USERS = ("git",)


def _userinfo_is_credential_free(userinfo):
    if not userinfo:
        return True
    return userinfo in _CREDENTIAL_FREE_USERS


def sanitize_origin_provenance(raw):
    """把 remote URL 淨化成可以寫進 Git 的 provenance;判不安全回 None。

    保留:scheme(限 http/https/ssh/git)、host、repository path。
    丟掉:SSH 慣例帳號 `git@` 的 user 部分。
    拒絕:任何非 `git` 的 userinfo(見 _userinfo_is_credential_free)、
          帶 query 或 fragment 的 URL、
          file://、本機絕對路徑、`~`、相對路徑、UNC、Windows drive、
          含空白或可疑字元的值、以及任何過得了上述關卡但仍被 secret /
          絕對路徑掃描命中的結果(雙保險 —— pattern 永遠不完整,
          所以最後一道用既有的守衛再掃一次)。
    """
    if not isinstance(raw, str):
        return None
    value = raw.strip()
    if not value or len(value) > 512:
        return None
    if any(ch.isspace() for ch in value):
        return None
    lowered = value.lower()
    for scheme in _LOCAL_SCHEMES:
        if lowered.startswith(scheme):
            return None
    # 本機/UNC/Windows 路徑:這些是「這台機器上的目錄」,不是可攜的 provenance
    if paths.looks_absolute(value) or value.startswith(("./", "../", ".\\", "..\\")):
        return None
    if "\\" in value:
        return None
    # query / fragment:整條拒絕,**不是**剝掉後保留。
    # 它們不是 git remote 定址的一部分,出現在這裡多半是別的東西(token、
    # proxy 參數)被塞進了 URL —— 而「這個 query 有沒有機密」同樣沒有可靠判別法。
    # provenance 是選填的,放棄比猜安全。
    if "?" in value or "#" in value:
        return None

    match = _SCHEME_URL.match(value)
    if match:
        if not _userinfo_is_credential_free(match.group("userinfo")):
            return None
        scheme = match.group("scheme")
        host = match.group("host")
        port = match.group("port") or ""
        path = match.group("path") or ""
        candidate = "{0}://{1}{2}{3}".format(scheme, host, port, path)
    else:
        match = _SCP_LIKE.match(value)
        if not match:
            return None
        if not _userinfo_is_credential_free(match.group("userinfo")):
            return None
        host = match.group("host")
        path = "/" + match.group("path").lstrip("/")
        candidate = "{0}{1}".format(host, path)

    if not _SAFE_HOST.match(host) or "." not in host:
        return None
    if not _SAFE_PATH.match(path) or not path.strip("/"):
        return None

    # 最後一道:過得了上面的形狀檢查,仍要通過既有的兩支守衛。
    # 這不是多餘 —— 形狀檢查認的是「長得像不像 URL」,守衛認的是「內容像不像
    # 機密或本機路徑」,兩者抓的東西不同。
    if signal.scan_sensitive(candidate) or paths.scan_absolute_paths(candidate):
        return None
    return candidate


# 指向「這台機器自己」的主機名。`.` 的存在不代表另一台機器(127.0.0.1)。
_LOOPBACK_HOSTS = frozenset((
    "localhost", "localhost.localdomain", "ip6-localhost",
    "0.0.0.0", "::1", "::", "[::1]"))


def remote_is_offmachine(url):
    """這個 git remote URL 指向的是**另一台機器**嗎?判不出來一律 False。

    存在的理由:`durable-check` 問的是「記憶離開這台機器了嗎」,而
    `git ls-remote` 成功只回答了嚴格較弱的一句話 ——「設定的 upstream 連得上
    而且有這個 commit」。remote 不必然在別台機器上:

        /Volumes/backup/mirror.git      本機路徑
        file:///Users/rick/mirror.git   本機路徑,換個寫法
        ssh://git@localhost/repo.git    網路 transport,但連的是自己

    這三個都會讓 `ls-remote` 回報正確的 SHA。硬碟壞掉時它們跟工作樹一起消失,
    而判定已經聲稱記憶離開了本機。

    所以這裡只認**網路 transport + 具名的非 loopback 主機**,其餘(本機路徑、
    UNC、Windows 磁碟機、未知 transport、單段主機名)一律 False。單段主機名
    也判 False 是刻意的:`ssh://git@buildbox/…` 可能是別台機器、也可能是本機
    的 `/etc/hosts` 別名,分不出來 —— 而**分不出來不得當成證據**。

    這支與 `sanitize_origin_provenance` 問的是不同的問題(那支問「能不能寫進
    Git」,這支問「在不在別台機器上」),所以刻意不共用回傳值:一條 URL 可以
    是 off-machine 卻不可寫入(帶 token 的 https 就是)。
    """
    host = _parse_host(url)
    if not host or host in _LOOPBACK_HOSTS or host.startswith("127."):
        return False
    return "." in host


def _parse_host(url):
    """從 remote URL 抽出 host;抽不出來回 None。

    與 `remote_is_offmachine` 共用同一套 parser(形狀判定),差別是這支只回
    host 字串,不判斷。存在的理由:形狀判定完之後,`_observe_remote` 還要拿
    這個 host 去做**會連網**的解析(見 `resolve_host_ips`)——那是另一個問句
    (「解析後的位址是不是這台機器自己」),刻意留在呼叫端做,這支維持不連網。
    """
    if not isinstance(url, str):
        return None
    value = url.strip()
    if not value or any(ch.isspace() for ch in value):
        return None
    if value.lower().startswith("file://"):
        return None
    if paths.looks_absolute(value) or "\\" in value:
        return None
    if value.startswith(("./", "../")):
        return None
    match = _SCHEME_URL.match(value) or _SCP_LIKE.match(value)
    if not match:
        return None
    return match.group("host").strip("[]").lower()


# loopback / link-local / unspecified:這三類位址不必解析錯誤就足以證明
# 「這台機器自己」,`ipaddress` 的 is_loopback/is_link_local/is_unspecified
# 涵蓋了 IPv4 與 IPv6 兩邊(127.0.0.0/8、169.254.0.0/16、fe80::/10、
# 0.0.0.0、::)。**不**檢查 is_private——一個私有網段位址(192.168.x.x、
# 10.x.x.x)完全可能是 LAN 上一台真正的別的機器,不是這台機器自己;
# 排除它會誤傷內網自架 git server 這個合法情境。
def ip_is_offmachine(raw_ip, local_ips=None):
    """這個(已解析出的)IP 位址,排除得掉「其實是這台機器自己」嗎?

    解析不出來的字串、loopback、link-local、unspecified,或等於
    `local_ips`(預設用 `_local_machine_ips()` 現查)裡的任何一個 ——
    一律 False。**分不出來不得當成證據**,與 `remote_is_offmachine` 同一條
    紀律,這支只是把它套用到「解析後的位址」而不是「URL 的形狀」。
    """
    if not isinstance(raw_ip, str) or not raw_ip:
        return False
    try:
        addr = ipaddress.ip_address(raw_ip.split("%", 1)[0])
    except ValueError:
        return False
    if addr.is_loopback or addr.is_link_local or addr.is_unspecified:
        return False
    if local_ips is None:
        local_ips = _local_machine_ips()
    return raw_ip not in local_ips


def resolve_host_ips(host):
    """DNS 解析 `host`,回傳位址字串的 frozenset;解析不到回 `None`。

    只給已經過 `remote_is_offmachine` 形狀檢查的 host 用。解析失敗
    (DNS 錯、host 其實是解析不出來的 SSH config 別名、離線)一律回 `None`,
    呼叫端要 fail closed——分不出來不得當成「離開這台機器」的證據,
    不能因為問不到就放行(同 `_observe_remote` 對 `ls-remote` 問不到的處理)。
    """
    if not isinstance(host, str) or not host:
        return None
    try:
        infos = socket.getaddrinfo(host, None)
    except (OSError, UnicodeError):
        return None
    ips = frozenset(info[4][0] for info in infos)
    return ips or None


def _local_machine_ips():
    """盡力而為收集這台機器可能用到的位址,用來擋『解析後其實是自己』的 remote。

    沒有純 stdlib、跨平台(含 Windows,本專案要求 parity)的辦法能列出所有
    網卡位址——那要嘛是 platform-specific syscall,要嘛是新依賴,兩者都在
    本輪範圍外。這裡用兩個**不送封包**的技巧盡力而為:

    - `socket.getaddrinfo(gethostname(), None)`:本機主機名解析,常見情況
      下會回報本機位址。
    - UDP `connect()` 後讀 `getsockname()`:UDP 的 connect() 只是讓核心決定
      「如果要送,會從哪個介面送出去」並不實際送出任何封包,藉此問到預設
      對外介面的位址,不需要真的連得上對方。

    兩者都是 best-effort;任何一步失敗就跳過,不當成錯誤。**回傳空集合代表
    兩種探測手法全部失敗**,不代表「這台機器沒有任何位址」——真正的呼叫端
    (`sync._observe_remote`)必須把空集合本身當成「這台機器的介面位址列表
    拿不到」,fail closed 到 `REMOTE_UNVERIFIED`,不能把它當成一個正常的
    (只是碰巧是空的)本機位址集合直接丟給 `ip_is_offmachine` 比對——那樣
    任何非 loopback/link-local/unspecified 的位址都會被誤判成離開這台機器
    (`GPT-P0-LOCAL-IP-INVENTORY-FAILOPEN`,已修)。
    """
    addrs = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            addrs.add(info[4][0])
    except (OSError, UnicodeError):
        pass
    for family, target in ((socket.AF_INET, ("8.8.8.8", 80)),
                           (socket.AF_INET6, ("2001:4860:4860::8888", 80))):
        try:
            probe = socket.socket(family, socket.SOCK_DGRAM)
        except OSError:
            continue
        try:
            probe.connect(target)
            addrs.add(probe.getsockname()[0])
        except OSError:
            pass
        finally:
            probe.close()
    return frozenset(addrs)


def _git(root, *args):
    """跑 git 並回傳 **strip 過** 的 stdout;失敗回 None。

    只給「輸出是單一 token」的指令用(rev-parse / config)。
    NUL 分隔的輸出**不要**走這支 —— strip 會吃掉狀態碼前面的空白與檔名尾端的
    空白,見 _git_raw 與 parse_porcelain_z 的註解。
    """
    raw = _git_raw(root, *args)
    if raw is None:
        return None
    return raw.strip() or None


def _git_raw(root, *args):
    """跑 git 並回傳**未經 strip** 的 stdout;失敗回 None。

    存在的理由是一個實際發生過的缺陷:`git status --porcelain=v1 -z` 的每一筆
    都以 `XY ` 開頭,而未修改索引時 X 是空白(` M path`)。對整份輸出做 strip
    會把第一筆的前導空白吃掉,後面用固定位移取路徑就整批偏一個字元 ——
    而且它只在「已追蹤檔被修改」這條路上發作,未追蹤檔(`?? path`)不受影響,
    所以看起來像是好的。檔名尾端的空白也會被 strip 吃掉。
    """
    try:
        out = subprocess.run(["git", "-C", root, *args],
                             capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout


def parse_porcelain_z(payload):
    """解析 `git status --porcelain=v1 -z` 的輸出,回傳受影響路徑集合。

    格式(實測確認,不是憑印象):每筆以 NUL 結尾,內容是 `XY<space><path>`;
    **rename / copy 多一個欄位**,順序是

        R  <new-path>\0<old-path>\0
        RM <new-path>\0<old-path>\0     (rename 後又改內容)
        C  <new-path>\0<source-path>\0

    所以不能對每個 NUL 欄位一律套固定位移 —— 第二個欄位是**裸路徑**,沒有
    `XY ` 前綴,套位移會把它砍成一條不存在的路徑,於是 fact 依賴的舊路徑
    永遠不出現在 dirty 清單裡,`git mv` 就完全逃過 LVP 失效。

    rename/copy 兩端都要回傳:fact 可能依賴舊路徑(它已經不代表當前 checkout),
    而新證據住在新路徑。

    無法解析的欄位一律**跳過並回報**(第二個回傳值),不猜 —— 猜錯會讓失效判定
    靜默漏掉檔案。
    """
    if not payload:
        return set(), []
    fields = payload.split("\0")
    if fields and fields[-1] == "":
        fields.pop()                      # NUL 結尾產生的空尾欄
    changed = set()
    unparsed = []
    index = 0
    while index < len(fields):
        record = fields[index]
        index += 1
        if len(record) < 4 or record[2] != " ":
            # 不是合法的 `XY <path>`:可能是我們沒預期的 git 版本行為。
            if record:
                unparsed.append(record)
            continue
        status = record[:2]
        changed.add(paths.to_posix(record[3:]))
        if "R" in status or "C" in status:
            if index < len(fields):
                original = fields[index]
                index += 1
                if original:
                    changed.add(paths.to_posix(original))
            else:
                unparsed.append(record)   # 宣告了 rename 卻沒有第二欄
    return changed, unparsed


def read_project(repo_root_path):
    """讀 `.dev-flow/project.yaml`;不存在回 None。內容不合法丟 IdentityError。"""
    path = project_file(repo_root_path)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as stream:
        text = stream.read()
    try:
        data = yamlmini.load(text)
    except yamlmini.YamlMiniError as exc:
        raise IdentityError(
            "{0} 解析失敗(不自動重建 —— 重建會換掉 project_id,"
            "等於讓這台機器變成另一個專案):{1}".format(path, exc))
    if not isinstance(data, dict):
        raise IdentityError("{0} 頂層必須是 mapping".format(path))
    pid = data.get("project_id")
    if not ids.is_valid_id("project", pid):
        raise IdentityError(
            "{0} 的 project_id 不合法({1!r});請人工修復,"
            "不要讓工具自動產生新的".format(path, pid))
    if data.get("schema_version") != DURABLE_SCHEMA_VERSION:
        # 不是錯誤:未來版本的檔案在舊工具上要能被辨識出「版本不同」而不是被誤讀。
        data["schema_version_mismatch"] = True
    return data


def ensure_project(repo_root_path, name=None, now=None, create=True):
    """回傳 (project_dict, created)。已存在一律 reuse(idempotent 的核心保證)。

    dev-setup 重跑不得產生新的 project_id —— 這是 §12 的硬條件,也是 §31 的測試案。
    """
    existing = read_project(repo_root_path)
    if existing is not None:
        return existing, False
    if not create:
        raise IdentityError(
            "{0} 不存在;請先跑 dev-setup(唯一 setup 入口)".format(
                project_file(repo_root_path)))
    data = {
        "schema_version": DURABLE_SCHEMA_VERSION,
        "project_id": ids.new_id("project"),
        "name": name or os.path.basename(os.path.realpath(repo_root_path)),
        "created_at": now or _utc_now(),
    }
    origin = sanitize_origin_provenance(
        _git(repo_root_path, "config", "--get", "remote.origin.url"))
    if origin:
        # provenance only —— 讀取端不得用它做 identity 比對(見本檔頂註)。
        # 已經過 sanitize_origin_provenance:判不安全時它回 None,這裡就不寫。
        data["origin_provenance"] = origin
    write_project(repo_root_path, data)
    return data, True


def write_project(repo_root_path, data):
    """deterministic 寫入 project.yaml(atomic;同目錄 temp + rename)。"""
    root = durable_root(repo_root_path)
    os.makedirs(root, exist_ok=True)
    payload = {k: v for k, v in data.items() if k != "schema_version_mismatch"}
    text = yamlmini.dump(payload, key_order=_PROJECT_KEY_ORDER, header=_HEADER)
    _atomic_write_text(project_file(repo_root_path), text)


def _atomic_write_text(path, text):
    import tempfile
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _utc_now():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def workspace_snapshot(repo_root_path):
    """當前 local workspace 的狀態(branch / HEAD / worktree / dirty files)。

    Current Truth 的驗證基準是**當前 checkout**,不是 main —— 所以這裡拿到的
    branch/HEAD/dirty 會直接餵給 LVP invalidation(見 truth.py)。
    """
    root = os.path.realpath(repo_root_path)
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD") \
        or _git(root, "symbolic-ref", "--short", "HEAD")
    head = _git(root, "rev-parse", "HEAD")
    common = _git(root, "rev-parse", "--git-common-dir")
    git_dir = _git(root, "rev-parse", "--git-dir")
    is_worktree = bool(common and git_dir
                       and os.path.realpath(os.path.join(root, common))
                       != os.path.realpath(os.path.join(root, git_dir)))
    # -uall:未追蹤的整個目錄會被 git 摺疊成 `src/` 一列,摺疊後對不上
    # fact 的 dependencies(那是逐檔路徑)—— 失效判定會整批漏掉。
    # 用 _git_raw + parse_porcelain_z:狀態碼的前導空白與 rename 的第二欄
    # 都必須原樣保留才解析得對(見那兩支的註解)。
    dirty, unparsed = parse_porcelain_z(
        _git_raw(root, "status", "--porcelain=v1", "-z", "-uall"))
    snapshot = {
        "local_path": root,
        "os": platform.system().lower() or "unknown",
        "branch": branch or "(detached)",
        "head_sha": head or "",
        "worktree": "linked" if is_worktree else "main",
        "dirty_files": sorted(dirty),
    }
    if unparsed:
        # 解析不出來的欄位要**看得見**:失效判定少算檔案是靜默的錯,
        # 而靜默的錯會讓 agent 拿 STALE 的值當現況回答。
        snapshot["status_unparsed"] = sorted(unparsed)
    return snapshot


def workspace_key(project_id, local_path):
    """同一台機器同一路徑 = 同一個 workspace。改路徑 = 新 workspace,project_id 不變。"""
    import hashlib
    material = "{0}\0{1}\0{2}".format(
        project_id, platform.node() or "unknown",
        paths.to_posix(os.path.realpath(local_path)))
    return "wsp_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
