#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROTOTYPE — not production code.

Stage 3 throwaway for requirement-discovery-gaps.
Locks leftover Stage-2 SHAPES only:

  1. Goals vs Requested solution (two sections, not one Goal that names a channel)
  2. Discovery vs adjudication question labels
  3. Disposition ledger row (quote | dest | why)
  4. Fast triage six questions (hit → dest)
  5. A-5 LIGHT Human verdict (one role/scene line)

NOT Stage 6. Does not patch _templates/, skills/, guards, or example/.
Does NOT implement a dashboard/API word blacklist (A-1 rejected that).
Wrong-column detection here is fixture-tagged contrast drafts only.

Usage:
  python3 shape_lab.py demo
  python3 shape_lab.py print
"""
from __future__ import print_function

import hashlib
import os
import sys

DESTS = ("本方案處理", "刻意維持", "Non-Goal", "另開 slug", "仍待驗")
FAST_Q = ("下一步", "權限", "等待語意", "交接", "系統外", "中斷恢復")
FAST_DESTS = ("升 full", "fast+mini", "OC 接受風險", "維持 Fast")
EVIDENCE = ("Observed", "Reported", "Inferred", "Assumption", "Conflict")

# Contrast drafts. Tagged, not a production tooth.
FIXTURES = {
    "goals-wrong": {
        "goals": ["業務登入後就能在 dashboard 一眼看到 30 天內到期"],
        "requested": [],
        "want": "wrong-column",
    },
    "goals-right": {
        "goals": ["到期前有人處理續約，不靠記憶與 Excel"],
        "requested": ["站內 dashboard 卡片（未定案）"],
        "want": "ok",
    },
    "discover-wrong": {
        "kind": "發現",
        "ask": "上次怎麼追到期？推薦：做 dashboard，因為最低成本。",
        "want": "recommend-on-discover",
    },
    "discover-right": {
        "kind": "發現",
        "ask": "上次真的怎麼追到期？講最近一次，不要翻 SOP。",
        "want": "ok",
    },
    "adjudge-right": {
        "kind": "裁決",
        "ask": "在已核「每季漏件」上，選站內清單還是口頭交接？差異：可見 vs 零碼。推薦：先比 no-build。",
        "want": "ok",
    },
    "disp-empty": {
        "quote": "Journey「痛點消失」",
        "dest": "",
        "why": "之後再說",
        "want": "empty-dest",
    },
    "disp-ok": {
        "quote": "Journey「痛點消失」",
        "dest": "本方案處理",
        "why": "4A：本表即去向帳",
        "want": "ok",
    },
    "fast-blank": {
        "answers": {q: {"hit": "", "note": "", "dest": ""} for q in FAST_Q},
        "want": "blank",
    },
    "fast-visual": {
        "answers": {
            "下一步": {"hit": "否", "note": "只改卡片底色", "dest": "維持 Fast"},
            "權限": {"hit": "否", "note": "誰能標狀態沒變", "dest": "維持 Fast"},
            "等待語意": {"hit": "否", "note": "等待法務四字沒改", "dest": "維持 Fast"},
            "交接": {"hit": "否", "note": "無新交接", "dest": "維持 Fast"},
            "系統外": {"hit": "否", "note": "仍用 Email", "dest": "維持 Fast"},
            "中斷恢復": {"hit": "否", "note": "中斷路徑沒動", "dest": "維持 Fast"},
        },
        "want": "ok",
    },
    "fast-wait-as-done": {
        "answers": {
            "下一步": {"hit": "是", "note": "完成態變成可點下一步", "dest": "升 full"},
            "權限": {"hit": "否", "note": "誰能標沒變", "dest": ""},
            "等待語意": {"hit": "是", "note": "把「等待法務」顯示成「已完成」", "dest": "升 full"},
            "交接": {"hit": "否", "note": "無", "dest": ""},
            "系統外": {"hit": "否", "note": "無", "dest": ""},
            "中斷恢復": {"hit": "否", "note": "無", "dest": ""},
        },
        "want": "ok",
    },
    "fast-hit-no-dest": {
        "answers": {
            "下一步": {"hit": "是", "note": "改了下一步", "dest": ""},
            "權限": {"hit": "否", "note": "無", "dest": ""},
            "等待語意": {"hit": "否", "note": "無", "dest": ""},
            "交接": {"hit": "否", "note": "無", "dest": ""},
            "系統外": {"hit": "否", "note": "無", "dest": ""},
            "中斷恢復": {"hit": "否", "note": "無", "dest": ""},
        },
        "want": "hit-no-dest",
    },
    "verdict-attest-only": {
        "verdict": "ACCEPTED",
        "role_scene": "",
        "attest": "human:someone @ 2026-09-13",
        "want": "missing-role-scene",
    },
    "verdict-light": {
        "verdict": "ACCEPTED",
        "role_scene": "角色:訪談對象；場景:AC-2 發現題不附推薦",
        "attest": "human:rick @ 2026-09-13",
        "want": "ok",
    },
}


def judge_goals(fx):
    if not fx["requested"] and any("dashboard" in g.lower() for g in fx["goals"]):
        return "wrong-column"
    if fx["requested"] and fx["goals"]:
        return "ok"
    return "shape-fail"


def judge_ask(fx):
    ask = fx["ask"]
    kind = fx["kind"]
    if kind == "發現" and ("推薦" in ask or "選項" in ask):
        return "recommend-on-discover"
    if kind not in ("發現", "裁決"):
        return "unlabeled"
    return "ok"


def judge_disp(fx):
    if not fx["quote"] or not fx["why"]:
        return "empty-dest"
    if fx["dest"] not in DESTS:
        return "empty-dest"
    return "ok"


def judge_fast(fx):
    answers = fx["answers"]
    if any(not answers[q]["hit"] for q in FAST_Q):
        return "blank"
    for q in FAST_Q:
        row = answers[q]
        if row["hit"] == "是" and row["dest"] not in FAST_DESTS:
            return "hit-no-dest"
    return "ok"


def judge_verdict(fx):
    if not fx.get("role_scene"):
        return "missing-role-scene"
    if "角色" not in fx["role_scene"] or "場景" not in fx["role_scene"]:
        return "missing-role-scene"
    return "ok"


JUDGE = {
    "goals-wrong": judge_goals,
    "goals-right": judge_goals,
    "discover-wrong": judge_ask,
    "discover-right": judge_ask,
    "adjudge-right": judge_ask,
    "disp-empty": judge_disp,
    "disp-ok": judge_disp,
    "fast-blank": judge_fast,
    "fast-visual": judge_fast,
    "fast-wait-as-done": judge_fast,
    "fast-hit-no-dest": judge_fast,
    "verdict-attest-only": judge_verdict,
    "verdict-light": judge_verdict,
}


def print_shapes():
    print("=== Goals vs Requested ===")
    print("錯欄 Goals:", FIXTURES["goals-wrong"]["goals"][0])
    print("對欄 Goals:", FIXTURES["goals-right"]["goals"][0])
    print("對欄 Requested:", FIXTURES["goals-right"]["requested"][0])
    print("=== 發現 / 裁決 ===")
    print("錯:", FIXTURES["discover-wrong"]["ask"])
    print("發現:", FIXTURES["discover-right"]["ask"])
    print("裁決:", FIXTURES["adjudge-right"]["ask"])
    print("=== disposition ===")
    print("列: 引用 | 去向(%s) | 理由" % "/".join(DESTS))
    print("=== Fast 六問 ===")
    print("問:", " / ".join(FAST_Q))
    print("命中去向:", " / ".join(FAST_DESTS))
    print("=== A-5 LIGHT ===")
    print("角色／場景: 角色:<Actor>；場景:<AC-id 一句>")
    print("=== lookback 四欄（次） ===")
    print("回看日 / owner / 資料來源 / 低於何值重開")
    print("=== evidence 枚舉（次） ===")
    print(" / ".join(EVIDENCE), "+ 來源 XOR Assumption+期限；點頭≠來源")
    print("=== manifest 檔名建議（次） ===")
    print("docs/dev/<slug>/evidence-manifest.md（4-spec 再釘）")


def demo():
    print("PROTOTYPE — not production code")
    rows = []
    all_ok = True
    for name in (
        "goals-wrong",
        "goals-right",
        "discover-wrong",
        "discover-right",
        "adjudge-right",
        "disp-empty",
        "disp-ok",
        "fast-blank",
        "fast-visual",
        "fast-wait-as-done",
        "fast-hit-no-dest",
        "verdict-attest-only",
        "verdict-light",
    ):
        fx = FIXTURES[name]
        got = JUDGE[name](fx)
        want = fx["want"]
        ok = got == want
        all_ok = all_ok and ok
        rows.append((name, want, got, ok))
        print("%s want=%s got=%s %s" % (name, want, got, "OK" if ok else "FAIL"))
    wait = FIXTURES["fast-wait-as-done"]["answers"]["等待語意"]
    print("WAIT_AS_DONE_HITS %s" % (wait["hit"] == "是" and wait["dest"] == "升 full"))
    print("NO_BLACKLIST True")
    print("DESTS %d FAST_Q %d" % (len(DESTS), len(FAST_Q)))
    print("SHAPE_ROWS %d" % len(rows))
    print("ALL_MATCH %s" % all_ok)
    return 0 if all_ok else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "demo"
    if cmd == "print":
        print_shapes()
        return 0
    if cmd == "demo":
        return demo()
    print("usage: shape_lab.py demo|print", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
