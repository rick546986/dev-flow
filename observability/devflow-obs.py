#!/usr/bin/env python3
"""devflow-obs — DevFlow Agent Attempt ledger 工具(python3 標準庫,無第三方依賴)。

用法:
  devflow-obs.py validate <run_dir>...            # schema + 交叉引用驗證(髒→exit 1)
  devflow-obs.py validate-registry <registry.json>
  devflow-obs.py incomplete <run_dir>...          # crash 後可判定的 incomplete attempts
  devflow-obs.py resume <run_dir>                 # restart 恢復視圖(每 T 進度)
  devflow-obs.py derive <run_dir>...              # 重建 derived/run-events.jsonl
  devflow-obs.py stats --run <dir> [--run ...] [--legacy-md <md>] [--min-n N]
  devflow-obs.py recommend --run <dir> [...] [--min-n N] [--threshold X]

注意:本 CLI 是**讀取/衍生/統計**工具;事件寫入由 runtime(coordinator/hooks/
verifier)透過 devflow_obs.writer 進行,Worker agent 不得手改 ledger(四節)。
命令列引數避免直接鋪 .devflow/ 路徑前綴帶 rm/mv 字樣 —— 守衛 prebash 會攔。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from devflow_obs import event_validate, ledger, stats  # noqa: E402


def _print(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="devflow-obs")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("validate")
    p.add_argument("run_dirs", nargs="+")
    p = sub.add_parser("validate-registry")
    p.add_argument("registry")
    p = sub.add_parser("incomplete")
    p.add_argument("run_dirs", nargs="+")
    p = sub.add_parser("resume")
    p.add_argument("run_dir")
    p = sub.add_parser("derive")
    p.add_argument("run_dirs", nargs="+")
    for name in ("stats", "recommend"):
        p = sub.add_parser(name)
        p.add_argument("--run", action="append", default=[], dest="runs")
        p.add_argument("--legacy-md", action="append", default=[],
                       dest="legacy")
        p.add_argument("--min-n", type=int, default=5)
        if name == "recommend":
            p.add_argument("--threshold", type=float, default=0.6)
    args = parser.parse_args(argv)

    if args.cmd == "validate":
        report, dirty = {}, False
        for rd in args.run_dirs:
            key = os.path.basename(rd.rstrip("/"))
            try:
                errors = ledger.validate_run(rd)
            except Exception as e:
                errors = [{"code": "run_error", "field": rd,
                           "msg": f"{type(e).__name__}: {e}"}]
            report[key] = errors
            dirty = dirty or bool(errors)
        _print(report)
        return 1 if dirty else 0

    if args.cmd == "validate-registry":
        with open(args.registry) as f:
            errors = event_validate.validate_prompt_registry(json.load(f))
        _print(errors)
        return 1 if errors else 0

    if args.cmd == "incomplete":
        _print({os.path.basename(rd.rstrip("/")):
                ledger.incomplete_attempts(rd) for rd in args.run_dirs})
        return 0

    if args.cmd == "resume":
        _print(ledger.resume_state(args.run_dir))
        return 0

    if args.cmd == "derive":
        _print({os.path.basename(rd.rstrip("/")): ledger.derive(rd)
                for rd in args.run_dirs})
        return 0

    agg = stats.aggregate_runs(args.runs, legacy_paths=args.legacy,
                               min_n=args.min_n)
    if args.cmd == "stats":
        _print(agg)
        return 0
    _print(stats.recommendations(agg, success_threshold=args.threshold))
    return 0


if __name__ == "__main__":
    sys.exit(main())
