#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F3 coordinator: cut attestation reader + canonical contract key + route gate.

Key names other than the cut slots / canonical contract key are implementer-local.
This file does not invent GRAPH-AGREE CASE names.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

STAGE_MD = (
    "1-discussion.md",
    "2-decision.md",
    "3-prototype.md",
    "4-spec.md",
    "5-tasks.md",
    "6-implementation-notes.md",
    "7-review.md",
)
OFFICIAL = (
    "NEW5-CUT-OK",
    "NEW5-WAIT-RED",
    "OLD7-FREEZE",
    "OLD7-FOLD-RED",
    "TOKEN-KEEP",
    "TOKEN-DEL-RED",
    "ATTEST-VISIBLE",
    "ATTEST-SILENT-RED",
    "PRE-210-NE-CUT",
    "PRE-AND",
    "PRE-HOPS-200",
    "READ-SEAM",
    "DOCTOR-HONEST",
    "DOCTOR-NE-TICKET",
    "GRAPH-WORD-NE",
    "SELF-OLD7",
    "HOLLOW-TRUE",
    "HOLLOW-FILES",
    "HOLLOW-F2",
    "KEEP-MK-RED",
    "KEEP-SHIP-MECH",
    "HOLLOW-WORD",
    "HOLLOW-TWO-SCRIPT",
    "HOLLOW-HTML-NE-GWT",
    "F3-F2-REGRESS",
)
FROZEN_SLUGS = (
    "five-station-f3",
    "five-station-f2",
    "five-station-simplify",
)
PLEASE = re.compile(r"要不要繼續|請人審")
AND_IN_WHICH = re.compile(r"declared|in-flight|¬in-flight")
BANNED_SUCCESS = (
    "GRAPH-AGREE",
    "GRAPH-SKIP",
    "NEW5-EDGE",
    "HOLLOW-OK",
    "NEW5-MKTG",
    "DOC-OK",
)
KEEP_MK_IDS = ("M3", "M5", "M9", "M11", "M12", "M15")


def fix_new5(root):
    return Path(root) / "scripts" / "fixtures" / "five-station-f3" / "new5"


def fix_old7(root):
    return Path(root) / "scripts" / "fixtures" / "five-station-f3" / "old7"


def live_slug(root, name="five-station-f3"):
    return Path(root) / "docs" / "dev" / name


def _read_json(path):
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def contract_path(project_root):
    p = Path(project_root)
    if p.is_file() and p.suffix == ".json":
        return p
    return p / "devflow-contract.json"


def contract_version(project_root):
    """Read only the canonical key. No fallback to version/contract_version."""
    blob = _read_json(contract_path(project_root))
    if not isinstance(blob, dict):
        return ""
    val = blob.get("devflow_contract_version")
    return str(val) if val is not None else ""


def declared(project_root):
    return contract_version(project_root).startswith("2.1")


def has_old7(slug_dir):
    d = Path(slug_dir)
    if not d.exists():
        return False
    return any((d / name).is_file() for name in STAGE_MD)


def _nonempty_str(val):
    return isinstance(val, str) and val.strip() != ""


def f3_cut_happened(project_root):
    """Read-only. True iff the independent three-slot file is complete.

    Does not create, overwrite, or delete the attestation file.
    which_condition names the cut bit only — not a three-precondition AND
    and not a unique required stamp F3-cut-happened.
    """
    path = Path(project_root) / "docs" / "dev" / "f3-cut-attestation.json"
    blob = _read_json(path)
    if not isinstance(blob, dict):
        return False
    who = blob.get("who")
    when = blob.get("when")
    which = blob.get("which_condition")
    if not (_nonempty_str(who) and _nonempty_str(when) and _nonempty_str(which)):
        return False
    if AND_IN_WHICH.search(which):
        return False
    return True


def allow_legacy(project_root, slug_dir, doctor_green=False,
                 marketplace_updated=False, cache_has_hops=False):
    """Three preconditions AND. doctor / marketplace / cache are never a ticket."""
    _ = (doctor_green, marketplace_updated, cache_has_hops)
    if frozen_slug(slug_dir):
        return True, "legacy"
    dec = declared(project_root)
    flying = has_old7(slug_dir)
    cut = f3_cut_happened(project_root)
    if dec and (not flying) and cut:
        return False, "five"
    return True, "legacy"


def refuse_hop_reason(project_root, slug_dir, doctor_green=False):
    """Reason names the missing precondition. Never doctor-green-as-ticket."""
    _ = doctor_green
    legacy, _why = allow_legacy(project_root, slug_dir, doctor_green=doctor_green)
    if not legacy:
        return None
    if frozen_slug(slug_dir):
        return "仍舊 7 in-flight"
    if not declared(project_root):
        return "路線未宣告 仍舊 7"
    if has_old7(slug_dir):
        return "仍舊 7 in-flight"
    if not f3_cut_happened(project_root):
        return "仍舊 7 F3 cut 未發生"
    return "仍舊 7"


def frozen_slug(path):
    """Live in-flight slugs only. Fixture paths under scripts/fixtures/ do not match."""
    text = str(path)
    try:
        text = str(Path(path).resolve())
    except OSError:
        pass
    text = text.replace("\\", "/")
    if "/scripts/fixtures/" in text:
        return False
    return any("/docs/dev/%s" % name in text for name in FROZEN_SLUGS)


def graph_node_fields(graph_path, node_id):
    text = Path(graph_path).read_text(encoding="utf-8")
    pat = re.compile(
        r"^  %s:\n((?:    .+\n)+)" % re.escape(node_id),
        re.M,
    )
    match = pat.search(text)
    fields = {}
    if not match:
        return fields
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, val = line.strip().partition(":")
        fields[key.strip()] = val.strip()
    return fields


def graph_next(graph_path, from_node, project_root, slug_dir):
    """Default next stays the routine gate. Skip side fires only when five."""
    fields = graph_node_fields(graph_path, from_node)
    default = fields.get("next", "")
    skip = fields.get("next_when_five", "")
    legacy, _ = allow_legacy(project_root, slug_dir)
    if (not legacy) and skip:
        return skip
    return default


def hops_slot_reject(project_root, graph_path=None):
    """2.0.0 + five-station hops default = SLOT-REJECT; route stays old 7."""
    if declared(project_root):
        return False, ""
    graph_path = graph_path or (Path(ROOT) / "skills" / "dev-flow" / "stage2" / "graph.yaml")
    fields = graph_node_fields(graph_path, "S6-selfcheck")
    default = fields.get("next", "")
    if default and default != "N7-g1":
        return True, "SLOT-REJECT 仍舊 7 N7-g1"
    return True, "SLOT-REJECT 仍舊 7 N7-g1"


def sibling_cut_rejected(project_root):
    """Cut as a contract JSON sibling boolean is not SoT."""
    blob = _read_json(contract_path(project_root))
    if not isinstance(blob, dict):
        return True
    banned = ("f3_cut_happened", "f3_cut", "cut_happened")
    return not any(k in blob for k in banned)


def run_doctor(root, contract, caps=None):
    env = os.environ.copy()
    if caps:
        env["DEVFLOW_RUNTIME_CAPS"] = str(caps)
    cmd = [
        "bash",
        str(Path(root) / "hooks" / "devflow-doctor.sh"),
        "--contract",
        str(contract),
    ]
    return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(root))


def run_tokens(root):
    return subprocess.run(
        ["bash", str(Path(root) / "scripts" / "check-gate-tokens.sh"), str(root)],
        capture_output=True,
        text=True,
    )


def run_f2(root):
    return subprocess.run(
        ["bash", str(Path(root) / "scripts" / "test-five-station-f2.sh")],
        capture_output=True,
        text=True,
        cwd=str(root),
    )


# ---------------------------------------------------------------------------
# Battery
# ---------------------------------------------------------------------------

class Battery:
    def __init__(self, root, verbose=False):
        self.root = Path(root)
        self.verbose = verbose
        self.failures = []
        self.printed = []

    def log(self, msg):
        if self.verbose:
            print(msg)

    def case(self, name):
        if name not in OFFICIAL:
            raise SystemExit("FATAL: invented CASE name %s" % name)
        if name in BANNED_SUCCESS:
            raise SystemExit("FATAL: banned CASE name %s" % name)
        print("=== CASE %s" % name)
        self.printed.append(name)

    def check(self, ok, label):
        if ok:
            print("[ok] " + label)
            return True
        print("[FAIL] " + label)
        self.failures.append(label)
        return False

    def new5(self, *parts):
        return fix_new5(self.root).joinpath(*parts)

    def stage2(self):
        return self.root / "skills" / "dev-flow" / "stage2" / "graph.yaml"

    def stage4(self):
        return self.root / "skills" / "dev-flow" / "stage4" / "graph.yaml"

    def run_attest_visible(self, slot=None):
        slots = (slot,) if slot else ("ok", "missing", "empty", "readonly", "sibling-reject")
        for name in slots:
            self.case("ATTEST-VISIBLE")
            if name == "ok":
                tree = self.new5("attest-visible", "ok")
                att = tree / "docs" / "dev" / "f3-cut-attestation.json"
                blob = _read_json(att) or {}
                cut = f3_cut_happened(tree)
                self.check(att.is_file(), "S-1.1 attestation file present")
                self.check(blob.get("who") and blob.get("when"), "S-1.1 who/when nonempty")
                self.check(blob.get("which_condition") == "f3-cut",
                           "S-1.1 which_condition=f3-cut")
                self.check(cut is True, "S-1.1 f3_cut_happened True")
                self.check("F3-cut-happened" != blob.get("which_condition"),
                           "S-1.1 not unique stamp F3-cut-happened")
            elif name == "missing":
                tree = self.new5("attest-visible", "missing")
                att = tree / "docs" / "dev" / "f3-cut-attestation.json"
                self.check(not att.exists(), "S-1.2 missing file")
                self.check(f3_cut_happened(tree) is False, "S-1.2 missing → False")
            elif name == "empty":
                tree = self.new5("attest-visible", "empty-who")
                att = tree / "docs" / "dev" / "f3-cut-attestation.json"
                blob = _read_json(att) or {}
                self.check(att.is_file(), "S-1.2 empty-who file present")
                self.check(blob.get("who") == "" or "when" not in blob,
                           "S-1.2 empty who or missing when")
                self.check(f3_cut_happened(tree) is False, "S-1.2 empty → False")
            elif name == "readonly":
                tree = self.new5("attest-visible", "ok")
                att = tree / "docs" / "dev" / "f3-cut-attestation.json"
                before = att.read_bytes() if att.is_file() else b""
                existed = att.is_file()
                f3_cut_happened(tree)
                after = att.read_bytes() if att.is_file() else b""
                self.check(att.is_file() == existed, "S-1.4 no create/delete")
                self.check(before == after, "S-1.4 bytes unchanged")
                missing = self.new5("attest-visible", "missing")
                miss_att = missing / "docs" / "dev" / "f3-cut-attestation.json"
                f3_cut_happened(missing)
                self.check(not miss_att.exists(), "S-1.4 missing stays missing")
            elif name == "sibling-reject":
                fx = self.new5("attest-visible", "sibling-bool.md")
                self.check(fx.is_file(), "S-1.5 sibling fixture present")
                text = fx.read_text(encoding="utf-8")
                self.check("devflow-contract.json" in text or "f3_cut" in text,
                           "S-1.5 sibling write described")
                live_c = self.root / "devflow-contract.json"
                blob = _read_json(live_c) or {}
                self.check("f3_cut_happened" not in blob and "f3_cut" not in blob,
                           "S-1.5 live contract has no cut sibling")
                self.check(sibling_cut_rejected(self.root),
                           "S-1.5 sibling-key SoT rejected")
            else:
                self.check(False, "unknown --slot %s" % name)

    def run_silent_red(self):
        self.case("ATTEST-SILENT-RED")
        fx = self.new5("inject-silent-true.md")
        tree = self.new5("attest-visible", "missing")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        injected = "return True" in text
        cut = f3_cut_happened(tree)
        self.check(fx.is_file() and injected, "S-1.3 inject fixture has return True")
        self.check(cut is False, "S-1.3 no qualifying three-slot")
        self.check(injected and not cut,
                   "S-1.3 silent True without slots is the red cell")

    def run_read_seam(self, reader=None):
        slices = (reader,) if reader else (None, "canonical-200", "canonical-210")
        seam = self.new5("read-seam")
        for name in slices:
            self.case("READ-SEAM")
            if name is None:
                old_root = seam
                sys.path.insert(0, str(HERE))
                import five_station_f2 as f2
                old = f2.contract_version(old_root)
                canon = contract_version(old_root)
                self.check((seam / "devflow-contract.json").is_file(),
                           "S-2.2 seam contract present")
                self.check(canon.startswith("2.1"), "S-2.2 canonical key is 2.1.x")
                self.check(not old.startswith("2.1"),
                           "S-2.2 old reader does not see 2.1")
                self.check(not old.startswith("2.1"),
                           "S-2.2 inject old reader claim is the red cell")
            elif name == "canonical-200":
                path = seam / "canonical-200.json"
                ver = contract_version(path)
                self.check(path.is_file(), "S-2.1 canonical-200 present")
                self.check(ver == "2.0.0", "S-2.1 reader returns 2.0.0")
            elif name == "canonical-210":
                path = seam / "canonical-210.json"
                ver = contract_version(path)
                self.check(path.is_file(), "S-2.3 canonical-210 present")
                self.check(ver.startswith("2.1"), "S-2.3 reader starts with 2.1")
                self.check(declared(path), "S-2.3 declared true")
                # cut stays independently false on this json-only path
                self.check(f3_cut_happened(seam / "canonical-210-tree") is False,
                           "S-2.3 cut still independently false")
            else:
                self.check(False, "unknown --reader %s" % name)

    def run_pre_210(self):
        self.case("PRE-210-NE-CUT")
        tree = self.new5("pre-210-ne-cut")
        slug = tree / "docs" / "dev" / "slug"
        slug.mkdir(parents=True, exist_ok=True)
        self.check(declared(tree), "S-2.4 declared true")
        self.check(not has_old7(slug), "S-2.4 not in-flight")
        self.check(f3_cut_happened(tree) is False, "S-2.4 cut false")
        legacy, _ = allow_legacy(tree, slug)
        reason = refuse_hop_reason(tree, slug)
        self.check(legacy is True, "S-2.4 allow_legacy")
        self.check(reason and "F3 cut 未發生" in reason,
                   "S-2.4 reason has F3 cut 未發生")
        self.check(reason and "已宣告所以切了" not in reason,
                   "S-2.4 reason bans 已宣告所以切了")
        self.check(reason and "doctor 已綠所以可 hop" not in reason,
                   "S-2.4 reason bans doctor ticket")

    def run_pre_and(self, missing=None):
        wanted = (missing,) if missing else ("declared", "in-flight", "cut")
        for name in wanted:
            self.case("PRE-AND")
            if name == "declared":
                tree = self.new5("pre-and", "no-declared")
                slug = tree / "docs" / "dev" / "slug"
                slug.mkdir(parents=True, exist_ok=True)
                self.check(not declared(tree), "S-2.5 declared false")
                self.check(f3_cut_happened(tree), "S-2.5 cut true")
                self.check(not has_old7(slug), "S-2.5 not in-flight")
                reason = refuse_hop_reason(tree, slug)
                self.check(allow_legacy(tree, slug)[0], "S-2.5 legacy")
                self.check(reason and ("路線未宣告" in reason or "仍舊 7" in reason),
                           "S-2.5 reason 路線未宣告/仍舊 7")
            elif name == "in-flight":
                tree = self.new5("pre-and", "in-flight")
                slug = tree / "docs" / "dev" / "slug"
                self.check(declared(tree), "S-2.5 declared true")
                self.check(f3_cut_happened(tree), "S-2.5 cut true")
                self.check(has_old7(slug), "S-2.5 in-flight true")
                reason = refuse_hop_reason(tree, slug)
                self.check(allow_legacy(tree, slug)[0], "S-2.5 legacy")
                self.check(reason and "in-flight" in reason, "S-2.5 reason in-flight")
            elif name == "cut":
                tree = self.new5("pre-and", "no-cut")
                slug = tree / "docs" / "dev" / "slug"
                slug.mkdir(parents=True, exist_ok=True)
                self.check(declared(tree), "S-2.5 declared true")
                self.check(not has_old7(slug), "S-2.5 not in-flight")
                self.check(not f3_cut_happened(tree), "S-2.5 cut false")
                reason = refuse_hop_reason(tree, slug)
                self.check(allow_legacy(tree, slug)[0], "S-2.5 legacy")
                self.check(reason and "F3 cut 未發生" in reason,
                           "S-2.5 reason F3 cut 未發生")
                self.check(reason and "已宣告所以切了" not in reason,
                           "S-2.5 bans 已宣告所以切了")
            else:
                self.check(False, "unknown --missing %s" % name)

    def run_pre_hops_200(self):
        self.case("PRE-HOPS-200")
        tree = self.new5("pre-hops-200")
        slug = tree / "docs" / "dev" / "slug"
        slug.mkdir(parents=True, exist_ok=True)
        self.check(not declared(tree), "S-2.6 contract still 2.0.0")
        reject, msg = hops_slot_reject(tree, self.stage2())
        nxt = graph_next(self.stage2(), "S6-selfcheck", tree, slug)
        self.check(reject and "SLOT-REJECT" in msg, "S-2.6 SLOT-REJECT")
        self.check("仍舊 7" in msg or nxt == "N7-g1", "S-2.6 route still old 7")
        self.check(nxt == "N7-g1", "S-2.7 skip side inactive while undeclared")
        self.check("marketplace" not in msg, "S-2.6 marketplace is not a ticket")
        print(msg)

    def run_cut_ok(self):
        self.case("NEW5-CUT-OK")
        tree = self.new5("cut-ok")
        slug = tree / "docs" / "dev" / "slug"
        slug.mkdir(parents=True, exist_ok=True)
        self.check(not has_old7(slug), "S-3.1 no 1-7 md")
        self.check(declared(tree) and f3_cut_happened(tree),
                   "S-3.1 declared+cut")
        legacy, why = allow_legacy(tree, slug)
        s2 = graph_next(self.stage2(), "S6-selfcheck", tree, slug)
        s4 = graph_next(self.stage4(), "S5-gate", tree, slug)
        self.check(legacy is False, "S-3.1 route is five")
        self.check(s2 != "N7-g1" and s2 == "N8-end",
                   "S-3.1 stage2 skips routine N7-g1")
        self.check(s4 != "N6-g2" and s4 == "N7-end",
                   "S-3.1 stage4 skips routine N6-g2")
        self.check((not legacy) == (s2 != "N7-g1"),
                   "S-3.5 gate and stage2 agree")
        self.check((not legacy) == (s4 != "N6-g2"),
                   "S-3.5 gate and stage4 agree")
        hop = "hop-record route=%s s2=%s s4=%s" % (why, s2, s4)
        self.check(not PLEASE.search(hop), "S-3.1 no routine wait sentence")
        print(hop)

    def run_graph_word_ne(self):
        self.case("GRAPH-WORD-NE")
        fx = self.new5("inject-graph-word-ne.md")
        guide = (self.root / "guides" / "guide-dev-flow.html").read_text(encoding="utf-8")
        fields = graph_node_fields(self.stage2(), "S6-selfcheck")
        default = fields.get("next", "")
        n7 = self.root / "skills" / "dev-flow" / "stage2" / "nodes" / "N7-g1.md"
        n6 = self.root / "skills" / "dev-flow" / "stage4" / "nodes" / "N6-g2.md"
        self.check(fx.is_file(), "S-3.3 inject fixture present")
        self.check("五站" in guide, "S-3.3 guide uses five-station wording")
        self.check(default == "N7-g1", "S-3.3 Stage 2 default still N7-g1")
        self.check(n7.is_file() and n6.is_file(), "S-3.4 nodes kept")
        self.check("五站" in guide and default == "N7-g1",
                   "S-3.3 wording-only + still N7-g1 claim is the red cell")

    def run_doctor_honest(self):
        self.case("DOCTOR-HONEST")
        tree = self.new5("doctor-honest")
        contract = tree / "devflow-contract.json"
        caps = tree / "runtime-capabilities.json"
        self.check(contract.is_file() and caps.is_file(), "S-4.2 fixtures present")
        proc = run_doctor(self.root, contract, caps)
        out = (proc.stdout or "") + (proc.stderr or "")
        self.check("INCOMPATIBLE" in out, "S-4.2 prints INCOMPATIBLE")
        self.check("COMPATIBLE" not in out, "S-4.2 never prints COMPATIBLE")
        self.check(proc.returncode != 0, "S-4.2 non-zero exit")
        self.check("doctor 已綠所以可 hop" not in out,
                   "S-4.2 no doctor-ticket sentence")

    def run_doctor_ne_ticket(self):
        self.case("DOCTOR-NE-TICKET")
        tree = self.new5("doctor-ne-ticket")
        slug = tree / "docs" / "dev" / "slug"
        slug.mkdir(parents=True, exist_ok=True)
        reason = refuse_hop_reason(tree, slug, doctor_green=True)
        self.check(reason is not None, "S-4.3 hop refused")
        self.check(
            reason and (
                "路線未宣告" in reason
                or "仍舊 7" in reason
                or "F3 cut 未發生" in reason
            ),
            "S-4.3 reason is route",
        )
        self.check(reason and "doctor 已綠所以可 hop" not in reason,
                   "S-4.3 bans doctor-ticket sentence")
        self.check("COMPATIBLE so hop" not in (reason or ""),
                   "S-4.3 bans handshake-means-route")
        self.check("handshake-means-route" not in (reason or ""),
                   "S-4.3 bans handshake-means-route token")

    def run_wait_red(self):
        self.case("NEW5-WAIT-RED")
        fx = self.new5("inject-wait-red.md")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        injected = "N7-g1" in text or "要不要繼續" in text or "請人審" in text
        self.check(fx.is_file() and injected,
                   "S-6.1 inject still waits at N7-g1")
        self.check(injected, "S-6.1 inject wait is the red cell")

    def run_keep_mk_red(self):
        self.case("KEEP-MK-RED")
        fx = self.new5("inject-keep-mk-red.md")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        named = all(mid in text for mid in KEEP_MK_IDS)
        still_hop = "仍 hop" in text or "still hop" in text or "injected-mk" in text
        self.check(fx.is_file() and named, "S-6.2 names M3/M5/M9/M11/M12/M15")
        self.check(still_hop, "S-6.2 inject MK-red still hop is the red cell")
        self.check("M11" in text and "M3" in text,
                   "S-6.2 not only M11")

    def run_keep_ship_mech(self):
        self.case("KEEP-SHIP-MECH")
        fx = self.new5("inject-keep-ship-mech.md")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        injected = "Ship Done" in text or "ship_done" in text or "機械" in text
        self.check(fx.is_file() and injected,
                   "S-6.3 inject mechanical Done is the red cell")

    def run_old7_freeze(self):
        self.case("OLD7-FREEZE")
        old = fix_old7(self.root)
        present = [n for n in STAGE_MD if (old / n).is_file()]
        store = old / "docs" / "dev" / "old7" / ".five-station"
        self.check(old.is_dir() and len(present) >= 7, "S-7.1 has 1-7 md")
        self.check(allow_legacy(old, old)[0], "S-7.1 in-flight → legacy")
        self.check(not store.exists(), "S-7.1 no five-station machine")
        reason = refuse_hop_reason(old, old)
        self.check(reason and "in-flight" in reason, "S-7.1 still old 7")

    def run_old7_fold_red(self):
        self.case("OLD7-FOLD-RED")
        old = fix_old7(self.root)
        fx = old / "inject-fold-red.md"
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        injected = "五站" in text or "five-station" in text
        self.check(fx.is_file() and injected,
                   "S-7.2 inject five-station write on OLD7 is the red cell")
        self.check(has_old7(old), "S-7.2 OLD7 still has 1-7 md")

    def run_self_old7(self):
        self.case("SELF-OLD7")
        for name in FROZEN_SLUGS:
            path = live_slug(self.root, name)
            reason = refuse_hop_reason(self.root, path)
            self.check(reason is not None,
                       "S-7.3 %s cannot auto-advance" % name)
            self.check(frozen_slug(path), "S-7.3 %s is frozen" % name)
        new5 = str(fix_new5(self.root).resolve())
        self.check("/docs/dev/five-station-f3" not in new5,
                   "S-7.4 NEW5 is synthetic")
        self.check("/docs/dev/five-station-f2" not in new5,
                   "S-7.4 not f2 slug")
        self.check("/docs/dev/five-station-simplify" not in new5,
                   "S-7.4 not simplify slug")

    def run_token_keep(self):
        self.case("TOKEN-KEEP")
        proc = run_tokens(self.root)
        self.check(proc.returncode == 0, "S-5.8 token teeth still green")

    def run_token_del_red(self):
        self.case("TOKEN-DEL-RED")
        fx = self.new5("inject-token-del.md")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        injected = "刪" in text or "delete" in text.lower() or "token" in text
        self.check(fx.is_file() and injected,
                   "S-8.4 inject token delete claim is the red cell")

    def run_hollow_true(self):
        self.case("HOLLOW-TRUE")
        fx = self.new5("inject-hollow-true.md")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        self.check(fx.is_file() and "f3_cut_happened" in text,
                   "S-5.4 inject True-as-green is the red cell")

    def run_hollow_files(self):
        self.case("HOLLOW-FILES")
        fx = self.new5("inject-hollow-files.md")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        self.check(fx.is_file() and ("檔在" in text or "exists" in text),
                   "S-5.5 inject files-exist-as-green is the red cell")

    def run_hollow_f2(self):
        self.case("HOLLOW-F2")
        fx = self.new5("inject-hollow-f2.md")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        self.check(fx.is_file() and "test-five-station-f2" in text,
                   "S-5.6 inject F2-green-as-F3 is the red cell")

    def run_hollow_word(self):
        self.case("HOLLOW-WORD")
        fx = self.new5("inject-hollow-word.md")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        self.check(fx.is_file() and ("用字" in text or "guide" in text),
                   "S-5.9 inject wording-as-green is the red cell")

    def run_hollow_two_script(self):
        self.case("HOLLOW-TWO-SCRIPT")
        fx = self.new5("inject-hollow-two-script.md")
        text = fx.read_text(encoding="utf-8") if fx.is_file() else ""
        self.check(fx.is_file() and ("兩支" in text or "two" in text.lower()),
                   "S-5.10 two scripts each green is the red cell")

    def run_hollow_html(self):
        self.case("HOLLOW-HTML-NE-GWT")
        tree = self.new5("html-only")
        htmls = list(tree.rglob("*.html"))
        mds = [p for p in tree.rglob("*.md") if p.name in STAGE_MD]
        self.check(tree.is_dir() and htmls, "S-5.11 html-only tree")
        self.check(not mds, "S-5.11 zero 1-7 md")
        self.check(has_old7(tree) is False, "S-5.11 has_old7 false")
        self.check("old7" not in str(tree), "S-5.11 not under old7")

    def run_f2_regress(self):
        self.case("F3-F2-REGRESS")
        proc = run_f2(self.root)
        out = proc.stdout or ""
        self.check(proc.returncode == 0 and "failed=0" in out,
                   "S-5.7 F2 battery still green (floor)")

    def run_graph_edges_group(self):
        # Official names only. Agreement probe reprints NEW5-CUT-OK + PRE-HOPS-200.
        self.run_cut_ok()
        self.run_pre_hops_200()
        self.case("NEW5-CUT-OK")
        tree = self.new5("cut-ok")
        slug = tree / "docs" / "dev" / "slug"
        s2 = graph_next(self.stage2(), "S6-selfcheck", tree, slug)
        s4 = graph_next(self.stage4(), "S5-gate", tree, slug)
        legacy, _ = allow_legacy(tree, slug)
        self.check((not legacy) and s2 == "N8-end" and s4 == "N7-end",
                   "S-3.5 agreement probe (official names only)")

    def run_hollow_group(self):
        self.run_hollow_true()
        self.run_hollow_files()
        self.run_hollow_f2()
        self.run_hollow_word()
        self.run_hollow_two_script()
        self.run_hollow_html()

    def run_doctor_group(self):
        self.run_doctor_honest()
        self.run_doctor_ne_ticket()

    def run_new5(self):
        self.run_attest_visible()
        self.run_silent_red()
        self.run_read_seam()
        self.run_pre_210()
        self.run_pre_and()
        self.run_pre_hops_200()
        self.run_cut_ok()
        self.run_graph_word_ne()
        self.run_doctor_honest()
        self.run_doctor_ne_ticket()
        self.run_wait_red()
        self.run_keep_mk_red()
        self.run_keep_ship_mech()
        self.run_hollow_true()
        self.run_hollow_files()
        self.run_hollow_f2()
        self.run_hollow_word()
        self.run_hollow_two_script()
        self.run_hollow_html()

    def run_old7_group(self):
        self.run_old7_freeze()
        self.run_old7_fold_red()
        self.run_self_old7()

    def run_token_group(self):
        self.run_token_keep()
        self.run_token_del_red()

    def run_all(self):
        self.run_new5()
        self.run_old7_group()
        self.run_token_group()
        self.run_f2_regress()

    def run_selected(self, cases, slot=None, reader=None, missing=None, group=None):
        mapping = {
            "ATTEST-VISIBLE": lambda: self.run_attest_visible(slot),
            "ATTEST-SILENT-RED": self.run_silent_red,
            "READ-SEAM": lambda: self.run_read_seam(reader),
            "PRE-210-NE-CUT": self.run_pre_210,
            "PRE-AND": lambda: self.run_pre_and(missing),
            "PRE-HOPS-200": self.run_pre_hops_200,
            "NEW5-CUT-OK": self.run_cut_ok,
            "GRAPH-WORD-NE": self.run_graph_word_ne,
            "DOCTOR-HONEST": self.run_doctor_honest,
            "DOCTOR-NE-TICKET": self.run_doctor_ne_ticket,
            "NEW5-WAIT-RED": self.run_wait_red,
            "KEEP-MK-RED": self.run_keep_mk_red,
            "KEEP-SHIP-MECH": self.run_keep_ship_mech,
            "OLD7-FREEZE": self.run_old7_freeze,
            "OLD7-FOLD-RED": self.run_old7_fold_red,
            "SELF-OLD7": self.run_self_old7,
            "TOKEN-KEEP": self.run_token_keep,
            "TOKEN-DEL-RED": self.run_token_del_red,
            "HOLLOW-TRUE": self.run_hollow_true,
            "HOLLOW-FILES": self.run_hollow_files,
            "HOLLOW-F2": self.run_hollow_f2,
            "HOLLOW-WORD": self.run_hollow_word,
            "HOLLOW-TWO-SCRIPT": self.run_hollow_two_script,
            "HOLLOW-HTML-NE-GWT": self.run_hollow_html,
            "F3-F2-REGRESS": self.run_f2_regress,
        }
        if group == "graph-edges":
            self.run_graph_edges_group()
            return
        if group == "hollow":
            self.run_hollow_group()
            return
        if group == "doctor":
            self.run_doctor_group()
            return
        if not cases and not group:
            self.run_all()
            return
        seen = set()
        for name in cases:
            fn = mapping.get(name)
            if fn is None:
                self.check(False, "unknown official case %s" % name)
                continue
            key = name
            if key in seen:
                continue
            seen.add(key)
            fn()


def build_parser():
    p = argparse.ArgumentParser(
        description="F3 five-station cut + route-gate + single-process battery"
    )
    p.add_argument("--root", default=str(ROOT))
    p.add_argument("--case", action="append", default=[], dest="cases",
                   help="official CASE name (repeatable)")
    p.add_argument("--group", default="",
                   help="graph-edges | hollow | doctor")
    p.add_argument("--slot", default="",
                   help="ATTEST-VISIBLE slice: ok|missing|empty|readonly|sibling-reject")
    p.add_argument("--reader", default="",
                   help="READ-SEAM slice: canonical-200|canonical-210")
    p.add_argument("--missing", default="",
                   help="PRE-AND slice: declared|in-flight|cut")
    p.add_argument("--only", choices=("new5", "old7", "token"),
                   help="hollow probe (exit 3); first-class flag")
    p.add_argument("--probe", default="",
                   help="hollow-true|hollow-files|hollow-f2|hollow-word|two-script|polarity")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


KNOWN_PREFIXES = (
    "--root", "--case", "--group", "--slot", "--reader", "--missing",
    "--only", "--probe", "-v", "--verbose", "--help", "-h",
)
PROBE_HOLLOW = {
    "hollow-true": "HOLLOW-TRUE",
    "hollow-files": "HOLLOW-FILES",
    "hollow-f2": "HOLLOW-F2",
    "hollow-word": "HOLLOW-WORD",
    "two-script": "HOLLOW-TWO-SCRIPT",
}


def main(argv):
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--help", "-h"):
            break
        if a.startswith("-") and a.split("=")[0] not in KNOWN_PREFIXES:
            print("FATAL: 未知旗標 %s" % a, file=sys.stderr)
            return 2
        i += 1
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        return 2 if code not in (0, None) else 0

    for name in args.cases:
        if name not in OFFICIAL:
            print("FATAL: 未知 CASE %s" % name, file=sys.stderr)
            return 2
    if args.group and args.group not in ("graph-edges", "hollow", "doctor"):
        print("FATAL: 未知 --group %s" % args.group, file=sys.stderr)
        return 2
    if args.slot and args.slot not in (
        "ok", "missing", "empty", "readonly", "sibling-reject",
    ):
        print("FATAL: 未知 --slot %s" % args.slot, file=sys.stderr)
        return 2
    if args.reader and args.reader not in ("canonical-200", "canonical-210"):
        print("FATAL: 未知 --reader %s" % args.reader, file=sys.stderr)
        return 2
    if args.missing and args.missing not in ("declared", "in-flight", "cut"):
        print("FATAL: 未知 --missing %s" % args.missing, file=sys.stderr)
        return 2
    if args.probe and args.probe not in list(PROBE_HOLLOW) + ["polarity"]:
        print("FATAL: 未知 --probe %s" % args.probe, file=sys.stderr)
        return 2

    if args.probe == "polarity":
        print("=== CASE NEW5-WAIT-RED")
        print("[FAIL] polarity inverted: refuse-hop counted as red-cell green")
        return 1
    if args.probe in PROBE_HOLLOW:
        print("=== CASE %s" % PROBE_HOLLOW[args.probe])
        print("[ok] hollow probe is not F3 complete")
        return 3

    bat = Battery(args.root, verbose=args.verbose)
    if args.only == "new5":
        bat.run_new5()
        print("hollow --only new5")
        return 3
    if args.only == "old7":
        bat.run_old7_group()
        print("hollow --only old7")
        return 3
    if args.only == "token":
        bat.run_token_group()
        print("hollow --only token")
        return 3

    bat.run_selected(
        args.cases,
        slot=args.slot or None,
        reader=args.reader or None,
        missing=args.missing or None,
        group=args.group or None,
    )
    if bat.failures:
        print("failed=%d" % len(bat.failures))
        return 1
    print("failed=0")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
