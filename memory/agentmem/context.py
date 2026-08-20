"""Startup Context Builder(§27)。

**startup 不載入大量歷史。** 開場注入的東西只有一個標準:少了它,agent 會在
第一個回答就犯錯。其餘一律 on-demand retrieval。

固定七段(每段都有硬上限,總量也有上限):

    ①project identity + 當前 branch / HEAD / workspace 狀態
    ②critical verified truths(implementation truth 中 confidence 最高的幾條)
    ③critical invariants(業務不變量 —— 違反會出事)
    ④active intent(planned,**明確標示未實作**)
    ⑤open conflicts(domain 與 code 對不上的地方)
    ⑥recent important events(高訊號、近期)
    ⑦memory query instructions(怎麼問記憶,而不是把記憶全倒出來)

**不讀 CONTEXT.md。** 舊架構把「詞彙表」放在一個人工維護的 Markdown 檔並在開場
整份注入;新架構的 domain knowledge 住 `.dev-flow/knowledge/domain/`,由本檔按
需要挑重點,查詢時再按查詢取回。人工維護的單一大檔一定會腐化,而且它腐化時
沒有任何機制會發現。
"""
import json

from . import identity, truth

DEFAULT_BUDGET = 4000
"""startup context 的字元上限(預設值刻意小)。超過就砍段落,不砍成半句。"""

SECTION_LIMITS = {
    "verified_truths": 8,
    "invariants": 6,
    "intents": 4,
    "conflicts": 5,
    "events": 5,
}

QUERY_INSTRUCTIONS = (
    "記憶查詢方式(不要憑印象回答,也不要要求把記憶全部載入):\n"
    "- 現在實際怎麼運作 → `memory ask \"目前 <entity> 的 <fact> 是什麼\"`"
    "(CURRENT;走 Current Truth fast path)\n"
    "- 以前發生過什麼 → `memory ask \"之前 <主題> 改過什麼\"`(HISTORY)\n"
    "- 為什麼這樣做 → `memory ask \"為什麼 <決定>\"`(WHY;decision 優先)\n"
    "- 怎麼做某件事 → `memory ask \"怎麼 <動作>\"`(HOW;procedural skill)\n"
    "- 這個詞什麼意思 → `memory ask \"<詞> 是什麼意思\"`(DOMAIN)\n"
    "- 我們打算怎麼發展 → `memory ask \"未來打算 <主題>\"`(INTENT)\n"
    "查不到時工具會回 NO_RELIABLE_MATCH —— 那是合法答案,請據此說「沒有記錄」,"
    "不要拿相近的記憶頂替。"
)


def build(store, repo_root, workspace_id=None, snapshot=None,
          budget=DEFAULT_BUDGET):
    """組出 startup context。回傳 dict(sections / text / size / truncated)。"""
    project = identity.read_project(repo_root)
    snapshot = snapshot or identity.workspace_snapshot(repo_root)
    workspace_id = workspace_id or identity.workspace_key(
        project["project_id"] if project else "prj_" + "0" * 26,
        snapshot["local_path"])

    sections = []
    sections.append(("identity", _identity_lines(project, snapshot)))
    sections.append(("verified_truths",
                     _verified_truths(store, repo_root, workspace_id, snapshot)))
    sections.append(("invariants", _invariants(store)))
    sections.append(("intents", _intents(store)))
    sections.append(("conflicts", _conflicts(store)))
    sections.append(("events", _recent_events(store, snapshot)))
    sections.append(("instructions", [QUERY_INSTRUCTIONS]))

    rendered = []
    truncated = []
    size = 0
    for name, lines in sections:
        if not lines:
            continue
        block = _render(name, lines)
        # instructions 永遠保留:少了它,agent 會退回「憑印象回答」——
        # 那比少幾條 verified truth 糟得多。
        if size + len(block) > budget and name != "instructions":
            truncated.append(name)
            continue
        rendered.append(block)
        size += len(block)

    text = "\n\n".join(rendered)
    return {
        "project_id": project["project_id"] if project else None,
        "branch": snapshot["branch"], "head_sha": snapshot["head_sha"],
        "sections": dict(sections), "text": text, "size": len(text),
        "budget": budget, "truncated": truncated,
        "dirty_files": len(snapshot.get("dirty_files") or ()),
    }


_TITLES = {
    "identity": "## Project",
    "verified_truths": "## Current implementation truth(已驗證)",
    "invariants": "## Invariants(違反會出事)",
    "intents": "## Intent(尚未實作 — 不要當成現況)",
    "conflicts": "## Open conflicts(不要挑一邊回答)",
    "events": "## Recent important events",
    "instructions": "## Memory",
}


def _render(name, lines):
    return "\n".join([_TITLES[name]] + ["- " + line if not line.startswith("-")
                                        and name != "instructions" else line
                                        for line in lines])


def _identity_lines(project, snapshot):
    lines = []
    if project:
        lines.append("project_id: {0}(path-independent;來自 "
                     "`.dev-flow/project.yaml`)".format(project["project_id"]))
        lines.append("name: {0}".format(project.get("name", "?")))
    else:
        lines.append("尚未初始化 durable memory —— 請跑 dev-setup(唯一 setup 入口)")
    lines.append("branch: {0} / HEAD: {1}".format(
        snapshot["branch"], (snapshot["head_sha"] or "")[:12]))
    lines.append("workspace: {0} on {1}{2}".format(
        snapshot["worktree"], snapshot["os"],
        "(工作樹有 {0} 個未提交檔案 → current truth 可能 STALE)".format(
            len(snapshot["dirty_files"])) if snapshot["dirty_files"] else ""))
    return lines


def _verified_truths(store, repo_root, workspace_id, snapshot):
    rows = [r for r in store.facts(statuses=(truth.VERIFIED,), limit=200)]
    rows.sort(key=lambda r: (-r["confidence"], r["entity_key"], r["fact_key"]))
    lines = []
    for row in rows[:SECTION_LIMITS["verified_truths"]]:
        resolved = truth.resolve_current(
            store, repo_root, row["entity_type"], row["entity_key"],
            row["fact_key"], workspace_id, snapshot)
        marker = "" if resolved["status"] == truth.VERIFIED else \
            "  ⚠ 本機 {0} — 需重新確認".format(resolved["status"])
        lines.append("{0}.{1}.{2} = {3}(confidence {4}){5}".format(
            row["entity_type"], row["entity_key"], row["fact_key"], row["value"],
            round(row["confidence"], 2), marker))
    return lines


def _invariants(store):
    rows = store.knowledge(kind="invariant",
                           statuses=("CONFIRMED", "CONFLICT"),
                           limit=SECTION_LIMITS["invariants"])
    return ["{0}: {1}({2})".format(r["key"], r["title"], r["authority"])
            for r in rows]


def _intents(store):
    rows = [r for r in store.knowledge(kind="intent",
                                       statuses=("CONFIRMED",), limit=50)
            if not r["implemented"]]
    return ["{0}: {1} — PLANNED,尚未實作".format(r["key"], r["title"])
            for r in rows[:SECTION_LIMITS["intents"]]]


def _conflicts(store):
    lines = []
    for record in truth.open_conflicts(store,
                                       limit=SECTION_LIMITS["conflicts"]):
        detail = ""
        if record["conflicts"]:
            detail = " ↔ 觀察:{0}".format(record["conflicts"][-1].get(
                "observation", ""))
        lines.append("[{0}] {1}:{2}{3}".format(
            record["type"], record["key"], record["title"], detail))
    return lines


def _recent_events(store, snapshot):
    rows = store.events(limit=SECTION_LIMITS["events"] * 3,
                        branch=snapshot.get("branch"))
    high = [r for r in rows if r["signal"] == "high"]
    return ["{0} · {1}:{2}".format((r["occurred_at"] or "")[:10], r["kind"],
                                   r["title"])
            for r in high[:SECTION_LIMITS["events"]]]


def as_json(payload):
    return json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True)
