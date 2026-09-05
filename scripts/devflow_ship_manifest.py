#!/usr/bin/env python3
# devflow_ship_manifest.py — 散發清單正本的讀取/校驗庫(Repo-local)。
#
# 正本:`docs/dev/ship-manifest.json`
# 每列 source / destination / mode。這是 install / check / baseline / upgrade /
# dev-release / parity / 檔案地圖「散發面」標註的同一份 expected set。
#
# 不准掃 docs/dev/tools/ 當 expected set —— 正副本同時被刪時掃目錄會少一項而全綠
# (第 4 型假綠)。contract 列的 destination 不住在 tools/,獨立比對不得刪。
#
# tools_rows()/contract_rows() 只各挑一種 destination 樣式,兩者外還有第三種
# (source == destination 的同步宣告列,例:docs/dev/readme-contract-extract.md)——
# 舊版沒有任何函式把它納入 expected set,刪掉該檔 15 項仍全綠(issue #92)。
# all_rows() 涵蓋全部列;source_existence_failures()/unclassified_sync_failures()
# 補上第三類列的存在性/內容/mode 驗證,不再各分類各挑各的。
#
# 本檔是庫。牙齒在 scripts/check-ship-manifest.sh。
# 用法(診斷):
#   python3 scripts/devflow_ship_manifest.py --list [root]
#   python3 scripts/devflow_ship_manifest.py --validate [root]

from __future__ import print_function

import html
import json
import os
import re
import sys

SCHEMA = "devflow-ship-manifest-v1"
MANIFEST_REL = os.path.join("docs", "dev", "ship-manifest.json")
LEGAL_MODES = ("644", "755")
LEGAL_KEYS = frozenset(("source", "destination", "mode"))
TOOLS_PREFIX = "docs/dev/tools/"
FILEMAP_MARK = "散發面:<code>docs/dev/tools/</code>"
CONTRACT_SOURCE = "devflow-contract.json"
CONTRACT_DEST = "docs/dev/devflow-contract.json"


class ManifestError(Exception):
    def __init__(self, problems):
        self.problems = list(problems)
        Exception.__init__(self, "; ".join(self.problems))


def _bad_path(rel):
    if not isinstance(rel, str) or not rel.strip():
        return "空路徑"
    if rel != rel.strip():
        return "路徑前後有空白:%s" % rel
    if rel.startswith("/") or rel.startswith("\\"):
        return "絕對路徑:%s" % rel
    if "\\" in rel:
        return "反斜線路徑:%s" % rel
    parts = rel.split("/")
    if ".." in parts or "." in parts:
        return "含 . 或 ..:%s" % rel
    return None


def schema_problems(data):
    """結構牙:缺欄/重複 destination/非法 mode → 非空 list。不讀磁碟。"""
    fails = []
    if not isinstance(data, dict):
        return ["正本頂層不是 object"]
    if data.get("schema") != SCHEMA:
        fails.append("schema 必須是 %s,得 %r" % (SCHEMA, data.get("schema")))
    files = data.get("files")
    if not isinstance(files, list):
        fails.append("files 必須是 array")
        return fails
    if not files:
        fails.append("files 是空陣列 —— expected set 空,無從對帳")
        return fails
    seen_dest = {}
    for i, row in enumerate(files):
        loc = "files[%d]" % i
        if not isinstance(row, dict):
            fails.append("%s 不是 object" % loc)
            continue
        extra = set(row) - LEGAL_KEYS
        if extra:
            fails.append("%s 多了不認識的欄:%s" % (loc, ",".join(sorted(extra))))
        for key in ("source", "destination", "mode"):
            if key not in row:
                fails.append("%s 缺欄 %s" % (loc, key))
                continue
            val = row[key]
            if not isinstance(val, str) or not val.strip():
                fails.append("%s.%s 必須是非空字串" % (loc, key))
        src = row.get("source")
        dst = row.get("destination")
        mode = row.get("mode")
        if isinstance(src, str) and src.strip():
            err = _bad_path(src)
            if err:
                fails.append("%s.source %s" % (loc, err))
        if isinstance(dst, str) and dst.strip():
            err = _bad_path(dst)
            if err:
                fails.append("%s.destination %s" % (loc, err))
            if dst in seen_dest:
                fails.append("destination 重複:%s(%s 與 %s)"
                             % (dst, seen_dest[dst], loc))
            else:
                seen_dest[dst] = loc
        if isinstance(mode, str) and mode not in LEGAL_MODES:
            fails.append("%s.mode 不是合法值(644|755),得 %r" % (loc, mode))
    return fails


def manifest_path(root):
    return os.path.join(root, MANIFEST_REL)


def load_raw(root):
    path = manifest_path(root)
    if not os.path.isfile(path):
        raise ManifestError(["找不到 %s" % MANIFEST_REL])
    try:
        return json.loads(open(path, encoding="utf-8").read())
    except ValueError as exc:
        raise ManifestError(["%s 不是合法 JSON:%s" % (MANIFEST_REL, exc)])


def load(root):
    data = load_raw(root)
    problems = schema_problems(data)
    if problems:
        raise ManifestError(problems)
    return data


def rows(data):
    return list(data["files"])


def tools_rows(data):
    return [r for r in rows(data) if r["destination"].startswith(TOOLS_PREFIX)]


def contract_rows(data):
    return [r for r in rows(data)
            if r["source"] == CONTRACT_SOURCE
            or r["destination"] == CONTRACT_DEST]


def all_rows(data):
    """manifest 的完整列清單,不分類。tools_rows()/contract_rows() 各自只挑一種
    destination 樣式,兩者外還有第三種(例:source == destination,單純宣告
    「這個檔案本身就是散發面之一」的同步宣告列,如
    docs/dev/readme-contract-extract.md)。任何只用 tools_rows()/contract_rows()
    拼起來的 expected set 都會漏掉這一種 —— issue #92 的殘留就是這樣漏的:
    刪掉 readme-contract-extract.md,check-ship-manifest.sh 15 項仍全綠。
    全列存在性檢查(source_existence_failures)一律走這支,不要再各分類各挑各的。
    """
    return rows(data)


def unclassified_rows(data):
    """既不是 tools_rows()、也不是 contract_rows() 的列 —— 目前只有
    source == destination 的同步宣告列這一種,但用集合差(以 destination 字串
    當 key,schema 已保證 destination 不重複)而非硬編列名,未來再多一種
    第三類也不必回來改這裡。"""
    skip = {r["destination"] for r in tools_rows(data)}
    skip |= {r["destination"] for r in contract_rows(data)}
    return [r for r in all_rows(data) if r["destination"] not in skip]


def source_existence_failures(root, data=None):
    """全列 source 存在性:manifest 每一列的 source 檔在母版都必須存在,不分
    tools/contract/第三類。這是最外層的網子 —— tools_rows()/contract_rows()
    衍生的 parity 各自只驗自己那個子集的存在性,第三類列(例如
    docs/dev/readme-contract-extract.md 這種同步宣告列)過去完全沒有任何函式
    驗過它的 source 檔還在不在,刪掉整份清單仍全綠(issue #92)。
    """
    fails = []
    if data is None:
        try:
            data = load(root)
        except ManifestError as exc:
            return list(exc.problems)
    for row in all_rows(data):
        src = os.path.join(root, row["source"])
        if not os.path.isfile(src):
            fails.append("正本不存在:%s(destination=%s,清單列還在但找不到來源檔)"
                         % (row["source"], row["destination"]))
    return fails


def unclassified_sync_failures(root, data=None):
    """tools 列、contract 列以外的列(見 unclassified_rows())—— 若其
    destination 在母版內也是真實存在的檔(同步副本,例:source == destination
    的自我宣告列),內容與可執行位元要跟 source 一致,做法比照
    parity_failures() 對 tools 列的比對。destination 在母版內沒有對應檔的列
    不強求(可能純粹是給採用專案落地用、母版自己沒有另一份可比對),那種情況
    source_existence_failures() 已經驗過 source 半邊。
    contract 列的正副本比對刻意不在這裡做 —— 那條留給 dev-release 步驟 2 的
    獨立 `diff -q devflow-contract.json docs/dev/devflow-contract.json`
    (skills/dev-release/SKILL.md),兩邊重複沒有意義還可能各自漂移出不同的
    失敗訊息。
    """
    fails = []
    if data is None:
        try:
            data = load(root)
        except ManifestError as exc:
            return list(exc.problems)
    for row in unclassified_rows(data):
        src = os.path.join(root, row["source"])
        dst = os.path.join(root, row["destination"])
        if not (os.path.isfile(src) and os.path.isfile(dst)):
            continue
        if open(src, "rb").read() != open(dst, "rb").read():
            fails.append("內容不同:%s(改了正本沒重新散發)" % row["destination"])
        want = mode_int(row["mode"])
        src_m = actual_mode(src)
        dst_m = actual_mode(dst)
        if src_m != want:
            fails.append("正本 mode 與清單不一致:%s(清單 %s vs 檔 %03o)"
                         % (row["source"], row["mode"], src_m))
        if dst_m != want:
            fails.append("副本 mode 與清單不一致:%s(清單 %s vs 檔 %03o)"
                         % (row["destination"], row["mode"], dst_m))
        if src_m != dst_m:
            fails.append("可執行位元不一致:%s(正本 %03o vs 副本 %03o)"
                         % (row["destination"], src_m, dst_m))
    return fails


def mode_int(mode_str):
    return int(mode_str, 8)


def actual_mode(path):
    return os.stat(path).st_mode & 0o777


def filemap_ship_names(root):
    """檔案地圖標了散發面的列(basename 集合)。地圖不是正本,只拿來對帳。"""
    guide = os.path.join(root, "guides", "guide-dev-flow.html")
    if not os.path.isfile(guide):
        return None, ["找不到 guides/guide-dev-flow.html"]
    text = open(guide, encoding="utf-8").read()
    m = re.search(r'<h2 id="filemap">.*?(?=<h2 |\Z)', text, re.S)
    if not m:
        return None, ["找不到 filemap 節"]
    names = set()
    for row in re.findall(r"<tr>(.*?)</tr>", m.group(0), re.S):
        if FILEMAP_MARK not in row:
            continue
        cell = re.search(r"<td>(.*?)</td>", row, re.S)
        code = re.search(r"<code>(.*?)</code>", cell.group(1), re.S) if cell else None
        if code:
            names.add(html.unescape(code.group(1)).strip())
    return names, []


def parity_failures(root, data=None):
    """
    expected set 取自正本 tools 列,不掃 docs/dev/tools/。
    回傳失敗字串 list。正副本同刪、正本列還在 → 必紅。
    """
    fails = []
    if data is None:
        try:
            data = load(root)
        except ManifestError as exc:
            return list(exc.problems)
    expected = tools_rows(data)
    if not expected:
        return ["正本沒有任何 destination 落在 %s 的列 —— expected set 空,無從對帳"
                % TOOLS_PREFIX]
    expected_names = []
    for row in expected:
        name = os.path.basename(row["destination"])
        expected_names.append(name)
        src = os.path.join(root, row["source"])
        dst = os.path.join(root, row["destination"])
        if not os.path.isfile(src):
            fails.append("正本不存在:%s(清單列還在 → 正副本同刪也會紅)"
                         % row["source"])
        if not os.path.isfile(dst):
            fails.append("副本不存在:%s(忘記散發,或副本被刪)"
                         % row["destination"])
        if os.path.isfile(src) and os.path.isfile(dst):
            if open(src, "rb").read() != open(dst, "rb").read():
                fails.append("內容不同:%s(改了正本沒重新散發)" % name)
            want = mode_int(row["mode"])
            src_m = actual_mode(src)
            dst_m = actual_mode(dst)
            if src_m != want:
                fails.append("正本 mode 與清單不一致:%s(清單 %s vs 檔 %03o)"
                             % (row["source"], row["mode"], src_m))
            if dst_m != want:
                fails.append("副本 mode 與清單不一致:%s(清單 %s vs 檔 %03o)"
                             % (row["destination"], row["mode"], dst_m))
            if src_m != dst_m:
                fails.append("可執行位元不一致:%s(正本 %03o vs 副本 %03o)"
                             % (name, src_m, dst_m))
    tools_dir = os.path.join(root, "docs", "dev", "tools")
    if os.path.isdir(tools_dir):
        named = set(expected_names)
        for fname in sorted(os.listdir(tools_dir)):
            path = os.path.join(tools_dir, fname)
            if os.path.isfile(path) and fname not in named:
                fails.append("反向:docs/dev/tools/%s 不在正本 tools 列裡"
                             "(散發了但沒記帳)" % fname)
    return fails


def filemap_sync_failures(root, data=None):
    if data is None:
        try:
            data = load(root)
        except ManifestError as exc:
            return list(exc.problems)
    names, parse_fails = filemap_ship_names(root)
    if parse_fails:
        return parse_fails
    expected = {os.path.basename(r["destination"]) for r in tools_rows(data)}
    fails = []
    for name in sorted(expected - names):
        fails.append("檔案地圖缺散發面:%s(正本有,地圖沒標)" % name)
    for name in sorted(names - expected):
        fails.append("檔案地圖多散發面:%s(地圖有,正本沒有)" % name)
    if not expected:
        fails.append("正本 tools 列為空,檔案地圖對帳無從做")
    return fails


def _cli(argv):
    cmd = argv[1] if len(argv) > 1 else "--help"
    root = argv[2] if len(argv) > 2 else os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    if cmd in ("-h", "--help", "help"):
        print("usage: devflow_ship_manifest.py --list|--validate [root]")
        return 0
    if cmd == "--validate":
        try:
            load(root)
        except ManifestError as exc:
            print("⛔ " + "; ".join(exc.problems), file=sys.stderr)
            return 1
        print("✅ %s 結構合法" % MANIFEST_REL)
        return 0
    if cmd == "--list":
        try:
            data = load(root)
        except ManifestError as exc:
            print("⛔ " + "; ".join(exc.problems), file=sys.stderr)
            return 1
        for row in rows(data):
            print("%s\t%s\t%s" % (row["source"], row["destination"], row["mode"]))
        return 0
    print("usage: devflow_ship_manifest.py --list|--validate [root]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(_cli(sys.argv))
