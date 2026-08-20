#!/usr/bin/env python3
"""dev-memory — dev-flow Agent Memory v3 CLI(python3 標準庫,無第三方依賴)。

**沒有 init 指令。** 專案的 setup / repair / rebuild 入口只有一個:既有的
`dev-setup` skill。本 CLI 的 `setup` 子命令是給 dev-setup 呼叫的實作,
不是第二個安裝器(`dev-setup` 會呼叫它;使用者不需要記得它)。

用法:
  dev-memory.py setup [--path DIR] [--no-rebuild] [--no-embeddings] [--name N]
  dev-memory.py doctor [--path DIR]
  dev-memory.py status [--path DIR]
  dev-memory.py context [--path DIR] [--budget N] [--json]
  dev-memory.py ask "<問題>" [--path DIR] [--limit N] [--json]
  dev-memory.py remember --kind <event 種類> --title T [--body B] [--path-ref P]...
  dev-memory.py fact --entity-type T --entity-key K --fact-key F --value V
                     [--dep P]... [--verified]
  dev-memory.py verify --entity-type T --entity-key K --fact-key F
                       [--observed V | --undetermined]
  dev-memory.py know --kind <domain|invariant|entity|relationship|intent>
                     --key K --title T [--body B] [--authority A]
                     [--planned | --implemented]
  dev-memory.py talk start "<主題>" | turn <session> <role> "<文字>"
                | propose <session> --kind K --payload-json JSON --authority A
                | confirm <candidate> | reject <candidate> [--reason R]
                | correct <session> --kind K --key K2 --title T [--body B]
                | checkpoint <session> | end <session> | status <session>
  dev-memory.py reindex [--path DIR] [--force]
  dev-memory.py migrate-legacy [--path DIR] [--apply] [--promote]
  dev-memory.py eval [--path DIR] [--dataset FILE] [--json]
  dev-memory.py inventory [--path DIR]

exit code:0 = 成功 / 1 = 可判定的失敗(含 doctor FAIL)/ 2 = 用法或環境錯誤。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentmem import (context as context_mod, devtalk, durable, embedding,  # noqa: E402
                      evalharness, identity, legacy, paths, query,
                      setup as setup_mod, store as store_mod, truth)


def _print(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True))


def _resolve(args):
    """回傳 (root, project, store, workspace_id, snapshot);缺 identity 就 fail-loud。"""
    root = paths.repo_root(getattr(args, "path", None))
    if root is None:
        raise SystemExit("⛔ 不在 git repository 內 —— memory identity 住在 Git 裡")
    project = identity.read_project(root)
    if project is None:
        raise SystemExit(
            "⛔ 找不到 {0}/project.yaml —— 請跑 dev-setup(唯一 setup 入口)".format(
                identity.memory_dir_name()))
    snapshot = identity.workspace_snapshot(root)
    workspace_id = identity.workspace_key(project["project_id"],
                                          snapshot["local_path"])
    store = store_mod.Store.open(project["project_id"])
    return root, project, store, workspace_id, snapshot


def cmd_setup(args):
    _print(setup_mod.run(args.path, rebuild=not args.no_rebuild,
                         reindex_embeddings=not args.no_embeddings,
                         name=args.name))
    return 0


def cmd_doctor(args):
    report = setup_mod.doctor(args.path)
    _print(report)
    return 1 if report["verdict"] == "FAIL" else 0


def cmd_status(args):
    root, project, store, workspace_id, snapshot = _resolve(args)
    try:
        _print({
            "project_id": project["project_id"],
            "project_name": project.get("name"),
            "durable_dir": identity.memory_dir_name(),
            "durable_inventory": durable.inventory(root),
            "workspace": snapshot, "workspace_id": workspace_id,
            "workspaces_known": len(store.workspaces()),
            "local_db": store_mod.db_path(project["project_id"]),
            "indexed_items": store.item_count(),
            "capabilities": {k: bool(v) for k, v in store.caps.items()},
            "overlays": len(store.overlays(workspace_id)),
            "open_conflicts": truth.open_conflicts(store),
        })
    finally:
        store.close()
    return 0


def cmd_context(args):
    root, _project, store, workspace_id, snapshot = _resolve(args)
    try:
        payload = context_mod.build(store, root, workspace_id, snapshot,
                                    budget=args.budget)
        if args.json:
            _print(payload)
        else:
            print(payload["text"])
    finally:
        store.close()
    return 0


def cmd_ask(args):
    root, _project, store, workspace_id, snapshot = _resolve(args)
    try:
        answer = query.execute(store, root, args.question, workspace_id,
                               snapshot, embedding.Embedder(), limit=args.limit)
        if args.json:
            _print(answer)
        else:
            _render_answer(answer)
    finally:
        store.close()
    return 0


def _render_answer(answer):
    print("[{0}] {1}(confidence {2})".format(
        answer["primary_intent"], answer["retrieval_status"],
        answer["confidence"]))
    current = answer.get("current_truth")
    if current:
        print("  → {0}(fast path;verified_commit={1})".format(
            current["value"], (current.get("verified_commit") or "?")[:12]))
    for hit in answer["results"]:
        title = hit.get("title") or hit.get("key") or ""
        extra = ""
        if hit.get("implementation_state"):
            extra = "  [{0}]".format(hit["implementation_state"].upper())
        elif hit.get("status"):
            extra = "  [{0}]".format(hit["status"])
        print("  · {0}{1}".format(title, extra))
    for note in answer["uncertainty"]:
        print("  ⚠ " + note)


def cmd_remember(args):
    root, _project, store, _workspace_id, snapshot = _resolve(args)
    try:
        from agentmem import signal as signal_mod
        verdict = signal_mod.gate(args.kind, args.title, args.body or "")
        event_id = store.add_event(
            args.kind, args.title, args.body or "", branch=snapshot["branch"],
            commit_sha=snapshot["head_sha"], signal=verdict["signal"],
            file_paths=args.path_ref or [], source_type="runtime_evidence")
        _print({"event_id": event_id, "signal_gate": verdict,
                "durable": False,
                "note": "durable 寫入只發生在 checkpoint/consolidation"})
    finally:
        store.close()
    return 0


def cmd_fact(args):
    root, _project, store, _workspace_id, snapshot = _resolve(args)
    try:
        fact_id = truth.record_fact(
            store, root, args.entity_type, args.entity_key, args.fact_key,
            args.value, dependencies=args.dep or [],
            source_type=args.source_type, source_ref=args.source_ref,
            source_commit=snapshot["head_sha"],
            status=truth.VERIFIED if args.verified else truth.CANDIDATE,
            confidence=0.95 if args.verified else 0.5)
        _print({"fact_id": fact_id, "status": store.fact_row(fact_id)["status"]})
    finally:
        store.close()
    return 0


def cmd_verify(args):
    root, _project, store, workspace_id, snapshot = _resolve(args)
    try:
        fact = truth.live_fact(store, args.entity_type, args.entity_key,
                               args.fact_key)
        if fact is None:
            raise SystemExit("⛔ 找不到該 fact —— UNKNOWN 是合法狀態,不要硬驗")
        outcome = truth.reverify(
            store, root, fact["fact_id"], workspace_id,
            None if args.undetermined else args.observed,
            source_commit=snapshot["head_sha"])
        _print(outcome)
    finally:
        store.close()
    return 0


def cmd_know(args):
    root, _project, store, _workspace_id, _snapshot = _resolve(args)
    try:
        implemented = None
        if args.planned:
            implemented = False
        elif args.implemented:
            implemented = True
        knowledge_id, action = truth.assert_knowledge(
            store, args.kind, args.key, args.title, body=args.body or "",
            authority=args.authority, status=args.status,
            confidence=args.confidence, implemented=implemented)
        _print({"knowledge_id": knowledge_id, "action": action,
                "note": ("權威不足,未覆寫既有內容" if action == "refused"
                         else "已寫入 local;durable 需 checkpoint")})
    finally:
        store.close()
    return 0


def cmd_talk(args):
    root, _project, store, _workspace_id, snapshot = _resolve(args)
    try:
        if args.talk_cmd == "start":
            _print(devtalk.start(store, root, args.topic, snapshot))
        elif args.talk_cmd == "turn":
            _print({"seq": devtalk.record_turn(store, args.session, args.role,
                                               args.text),
                    "note": "原始對話只住 local,永遠不進 Git"})
        elif args.talk_cmd == "propose":
            payload = json.loads(args.payload_json)
            _print({"candidate_id": devtalk.propose(
                store, args.session, args.kind, payload, args.authority)})
        elif args.talk_cmd == "confirm":
            _print({"candidate_id": devtalk.confirm(store, args.candidate)})
        elif args.talk_cmd == "reject":
            _print({"candidate_id": devtalk.reject(store, args.candidate,
                                                   args.reason or "")})
        elif args.talk_cmd == "correct":
            _print({"candidate_id": devtalk.correct(
                store, args.session, args.kind, args.key, args.title,
                body=args.body or "", reason=args.reason or "")})
        elif args.talk_cmd == "checkpoint":
            _print(_relativize(devtalk.checkpoint(store, root, args.session),
                               root))
        elif args.talk_cmd == "end":
            _print(_relativize(devtalk.end(store, root, args.session), root))
        elif args.talk_cmd == "status":
            _print(devtalk.status(store, args.session))
        else:
            raise SystemExit("⛔ 未知的 talk 子命令")
    finally:
        store.close()
    return 0


def _relativize(result, root):
    """輸出裡的檔案路徑一律 repo-relative —— CLI 輸出也不外洩絕對路徑。"""
    if "written" in result:
        result["written"] = [
            os.path.relpath(p, root).replace("\\", "/") for p in result["written"]]
    return result


def cmd_reindex(args):
    _root, _project, store, _workspace_id, _snapshot = _resolve(args)
    try:
        embedder = embedding.Embedder()
        before = embedder.mismatch_report(store)
        count = embedder.reindex(store, force=args.force)
        _print({"before": before, "reindexed": count,
                "after": embedder.mismatch_report(store)})
    finally:
        store.close()
    return 0


def cmd_migrate_legacy(args):
    root, _project, store, _workspace_id, _snapshot = _resolve(args)
    try:
        report = legacy.migrate(root, store, apply_changes=args.apply,
                                promote=args.promote)
        _print(_relativize(report, root))
    finally:
        store.close()
    return 0


def cmd_eval(args):
    root, _project, store, workspace_id, snapshot = _resolve(args)
    try:
        report = evalharness.run(store, root, workspace_id, snapshot,
                                 dataset_path=args.dataset)
        if args.json:
            _print(report)
        else:
            evalharness.render(report)
        return 0 if report["passed"] else 1
    finally:
        store.close()


def cmd_inventory(args):
    root = paths.repo_root(args.path)
    if root is None:
        raise SystemExit("⛔ 不在 git repository 內")
    _print(durable.inventory(root))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="dev-memory", add_help=True)
    parser.add_argument("--path", default=None,
                        help="repo 內任一路徑(預設 cwd)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("setup", help="dev-setup 的 memory 階段(不是第二個安裝器)")
    p.add_argument("--no-rebuild", action="store_true")
    p.add_argument("--no-embeddings", action="store_true")
    p.add_argument("--name", default=None)
    p.set_defaults(func=cmd_setup)

    sub.add_parser("doctor").set_defaults(func=cmd_doctor)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("inventory").set_defaults(func=cmd_inventory)

    p = sub.add_parser("context")
    p.add_argument("--budget", type=int, default=context_mod.DEFAULT_BUDGET)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_context)

    p = sub.add_parser("ask")
    p.add_argument("question")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("remember")
    p.add_argument("--kind", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--body", default="")
    p.add_argument("--path-ref", action="append", default=[])
    p.set_defaults(func=cmd_remember)

    p = sub.add_parser("fact")
    p.add_argument("--entity-type", required=True)
    p.add_argument("--entity-key", required=True)
    p.add_argument("--fact-key", required=True)
    p.add_argument("--value", required=True)
    p.add_argument("--dep", action="append", default=[])
    p.add_argument("--source-type", default="current_code")
    p.add_argument("--source-ref", default=None)
    p.add_argument("--verified", action="store_true")
    p.set_defaults(func=cmd_fact)

    p = sub.add_parser("verify")
    p.add_argument("--entity-type", required=True)
    p.add_argument("--entity-key", required=True)
    p.add_argument("--fact-key", required=True)
    p.add_argument("--observed", default=None)
    p.add_argument("--undetermined", action="store_true")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("know")
    p.add_argument("--kind", required=True,
                   choices=sorted(durable.KNOWLEDGE_DIRS))
    p.add_argument("--key", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--body", default="")
    p.add_argument("--authority", default="domain_expert")
    p.add_argument("--status", default="CONFIRMED")
    p.add_argument("--confidence", type=float, default=0.9)
    p.add_argument("--planned", action="store_true")
    p.add_argument("--implemented", action="store_true")
    p.set_defaults(func=cmd_know)

    p = sub.add_parser("talk")
    talk = p.add_subparsers(dest="talk_cmd", required=True)
    t = talk.add_parser("start")
    t.add_argument("topic")
    t = talk.add_parser("turn")
    t.add_argument("session")
    t.add_argument("role", choices=("user", "agent"))
    t.add_argument("text")
    t = talk.add_parser("propose")
    t.add_argument("session")
    t.add_argument("--kind", required=True)
    t.add_argument("--payload-json", required=True)
    t.add_argument("--authority", default="user_confirmed")
    t = talk.add_parser("confirm")
    t.add_argument("candidate")
    t = talk.add_parser("reject")
    t.add_argument("candidate")
    t.add_argument("--reason", default="")
    t = talk.add_parser("correct")
    t.add_argument("session")
    t.add_argument("--kind", required=True)
    t.add_argument("--key", required=True)
    t.add_argument("--title", required=True)
    t.add_argument("--body", default="")
    t.add_argument("--reason", default="")
    for name in ("checkpoint", "end", "status"):
        t = talk.add_parser(name)
        t.add_argument("session")
    p.set_defaults(func=cmd_talk)

    p = sub.add_parser("reindex")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_reindex)

    p = sub.add_parser("migrate-legacy")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--promote", action="store_true")
    p.set_defaults(func=cmd_migrate_legacy)

    p = sub.add_parser("eval")
    p.add_argument("--dataset", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_eval)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
