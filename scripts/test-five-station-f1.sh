#!/bin/bash
# test-five-station-f1.sh — F1 牙自檢
#
# 群組:
#   rp16         T-1  S-3.1
#   slots        T-2  S-5.8
#   dual-read    T-3  S-5.4…S-5.7／S-5.9
#   inflight     T-4  S-5.1…S-5.3
#   rp1          T-5  S-2.2
#   seam         T-6  S-2.3／S-2.9
#   spec-name    T-7  S-2.4／S-2.5
#   brief-files  T-8  S-2.1／S-2.7／S-2.8
#   attest       T-9  S-4.1…S-4.5／S-1.7
#   ship-quiz    T-10 S-1.10／S-3.2／S-3.3
#   rp-min-set   T-11 S-2.6
#   f1-close     T-12 S-1.1／S-6.2／S-6.3／S-8.1／S-8.5／S-8.6
#
# 用法: scripts/test-five-station-f1.sh [--group NAME] [-v] [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail
SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
GROUP=""
VERBOSE=0
POSITIONAL=()
while [ $# -gt 0 ]; do
  case "$1" in
    --group)
      GROUP=${2:-}
      [ -n "$GROUP" ] || { echo "FATAL: --group 需要名稱" >&2; exit 2; }
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=1
      shift
      ;;
    --)
      shift
      POSITIONAL+=("$@")
      break
      ;;
    -*)
      echo "FATAL: 未知旗標 $1" >&2
      exit 2
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done
if [ "${#POSITIONAL[@]}" -gt 0 ]; then
  ROOT=$(cd "${POSITIONAL[0]}" && pwd) || exit 2
fi

python3 - "$ROOT" "$GROUP" "$VERBOSE" <<'PY'
import os
import sys

root = sys.argv[1]
group = sys.argv[2]
verbose = sys.argv[3] == "1"
sys.path.insert(0, os.path.join(root, "scripts"))
import five_station_f1 as f1

fix = os.path.join(root, "scripts", "fixtures", "five-station-simplify")
annex_slots = os.path.join(
    root, "notes", "design", "five-station-simplify-f1-dual-read-annex.md"
)
annex_rp = os.path.join(
    root, "notes", "design", "five-station-simplify-f1-rp-min-set.md"
)
failures = []


def log(msg):
    if verbose:
        print(msg)


def case(name):
    print("=== CASE %s" % name)


def check(ok, label):
    if ok:
        print("[ok] " + label)
        return True
    print("[FAIL] " + label)
    failures.append(label)
    return False


def want_group(name):
    return group in ("", name)


def run_fix(name):
    return f1.check_path(os.path.join(fix, name), root)


def expect(name, fixture, should_red, codes=(), extras=()):
    case(name)
    result = run_fix(fixture)
    log(result.dump())
    ok = result.is_red is should_red
    check(ok, "%s red=%s" % (name, should_red))
    for code in codes:
        check(code in result.red_codes, "%s has %s" % (name, code))
    for key, value in extras:
        check(result.info.get(key) == value, "%s %s=%s" % (name, key, value))
    return result


# T-1
if want_group("rp16"):
    expect("test_s_3_1_agent_written_verdict_unread",
           "rp-16-agent-ship-pass.md", True, ["RP-16"])
    expect("test_s_3_1_human_accepted_not_killed",
           "rp-16-human-accepted-attest.md", False)

# T-2
if want_group("slots"):
    case("test_s_5_8_annex_nine_slot_semantics")
    result = f1.check_path(annex_slots, root)
    log(result.dump())
    check(not result.is_red and result.info.get("slots_ok"), "complete slots green")
    expect("test_s_5_8_missing_slot_red", "slots-missing-one.md", True, ["S-5.8"])

# T-3
if want_group("dual-read"):
    expect("test_s_5_4_old_seven_missing_new_fields_not_red",
           "dual-old7-missing-new5.md", False, extras=[("missing_new5_legal", True)])
    expect("test_s_5_6_doctor_green_follow_hops_text_fails",
           "dual-doctor-follow-hops.md", True, ["S-5.6"])
    expect("test_s_5_5_doctor_green_is_not_cut",
           "dual-doctor-green-means-cut.md", True, ["S-5.5"])
    expect("test_s_5_7_unupgraded_adopter_stays_old_7",
           "dual-200-plus-five-hops.md", True, ["S-5.7"],
           extras=[("route", "old-7"), ("doctor_not_arbiter", True)])
    expect("test_s_5_9_contract_vs_marketplace_hops_concurrency",
           "dual-hops-first-then-contract.md", True, ["S-5.7"],
           extras=[("route", "old-7")])

# T-4
if want_group("inflight"):
    expect("test_s_5_1_inflight_md_stays_old_7",
           "inflight-has-md.md", True, ["RP-15"], extras=[("in_flight", True)])
    expect("test_s_5_3_html_only_not_inflight",
           "inflight-html-only.md", False, extras=[("in_flight", False)])
    expect("test_s_5_2_this_slug_five_station_hop_blocked",
           "inflight-this-slug-five-hop.md", True, ["RP-15"],
           extras=[("hop_blocked", True)])

# T-5
if want_group("rp1"):
    expect("test_s_2_2_t_fake_missing_cols",
           "rp-01-missing-four-fields.md", True, ["RP-1"])
    expect("test_s_2_2_t_fake_red_on_card",
           "rp-01-verify-looks-fine.md", True, ["RP-1"])

# T-6
if want_group("seam"):
    expect("test_s_2_3_no_red_or_self_review_incomplete",
           "rp-02-no-red.md", True, ["RP-2"])
    expect("test_s_2_3_self_review_incomplete",
           "rp-02-self-review.md", True, ["RP-2"])
    expect("test_s_2_9_no_raw_output_red",
           "rp-06-summary-only.md", True, ["RP-6"])

# T-7
if want_group("spec-name"):
    vague = expect("test_s_2_4_vague_or_untestable_s_fails",
                   "rp-03-vague-tbd.md", True, ["RP-3"])
    check(vague.info.get("c4_fail") is True, "S-2.4 接 check-spec-gate C4")
    expect("test_s_2_4_untestable_error_fails",
           "rp-03-untestable-error.md", True, ["RP-3"])
    expect("test_s_2_5_test_name_requires_s_id",
           "rp-04-test-name-no-sid.md", True, ["RP-4"])

# T-8
if want_group("brief-files"):
    expect("test_s_2_1_missing_must_keep_is_brief_violation",
           "brief-missing-must-keep.md", True, ["S-2.1"])
    expect("test_s_2_7_optional_fields_block_this_g2",
           "brief-optional-four-fields.md", True, ["S-2.7"])
    expect("test_s_2_8_files_not_subset_red",
           "rp-05-files-outside-union.md", True, ["RP-5"])

# T-9
if want_group("attest"):
    expect("test_s_4_2_empty_attestation_plus_chat_cannot_leave_spec",
           "rp-13-empty-attestation-plus-chat.md", True, ["RP-13"],
           extras=[("leave_spec", False)])
    expect("test_s_4_3_miss_skips_demo_forced_accepted_fails",
           "rp-12-miss-forced-accepted.md", True, ["RP-12"],
           extras=[("demo_page", False)])
    expect("test_s_4_4_ask_human_when_latch_false_fails",
           "rp-14-please-review-latch-false.md", True, ["RP-14"])
    expect("test_s_4_5_negated_skip_is_not_skip_oc",
           "skip-negation-as-oc.md", True, ["S-4.5"],
           extras=[("skip_oc", False)])
    expect("test_s_1_7_a5_miss_builds_no_page",
           "rp-12-miss-forced-accepted.md", True, extras=[("demo_page", False)])

# T-10
if want_group("ship-quiz"):
    expect("test_s_1_10_b4_quiz_only_irreversible",
           "rp-07-irreversible-no-quiz.md", True, ["RP-7"])
    expect("test_s_1_10_reversible_forced_quiz_fails",
           "rp-07-reversible-forced-quiz.md", True, ["S-1.10"])
    expect("test_s_3_2_ship_done_without_human_pass_fails",
           "rp-08-done-without-pass.md", True, ["RP-8"])
    expect("test_s_3_3_ship_evidence_eight_points",
           "s-3-3-evidence-omit-eight.md", True, ["S-3.3"])

# T-11
if want_group("rp-min-set"):
    rp_fix = {
        "RP-1": "rp-01-verify-looks-fine.md",
        "RP-2": "rp-02-no-red.md",
        "RP-3": "rp-03-vague-tbd.md",
        "RP-4": "rp-04-test-name-no-sid.md",
        "RP-5": "rp-05-files-outside-union.md",
        "RP-6": "rp-06-summary-only.md",
        "RP-7": "rp-07-irreversible-no-quiz.md",
        "RP-8": "rp-08-done-without-pass.md",
        "RP-9": "rp-09-third-hop-rewrite.md",
        "RP-10": "rp-10-second-decide-reopen.md",
        "RP-11": "rp-11-second-goal-reopen.md",
        "RP-12": "rp-12-miss-forced-accepted.md",
        "RP-13": "rp-13-empty-attestation-plus-chat.md",
        "RP-14": "rp-14-please-review-latch-false.md",
        "RP-15": "inflight-this-slug-five-hop.md",
        "RP-16": "rp-16-agent-ship-pass.md",
    }
    for code, fixture in rp_fix.items():
        expect("test_s_2_6_rp_min_set_%s" % code.lower().replace("-", "_"),
               fixture, True, [code])
    expect("test_s_2_6_rp_min_set_add_only",
           "rp-min-set-delete-rp8.md", True, ["S-2.6"])

# T-12
if want_group("f1-close"):
    for name, fixture in (
        ("test_s_8_6_reopen_1b_delete_tokens", "reopen-1b-delete-tokens.md"),
        ("test_s_8_6_reopen_2b_old_file_red", "reopen-2b-old-file-red.md"),
        ("test_s_8_6_reopen_4c_this_slug_as_new5", "reopen-4c-this-slug-as-new5.md"),
        ("test_s_8_6_reopen_6b_must_keep_optional", "reopen-6b-must-keep-optional.md"),
        ("test_s_8_6_reopen_7c_merge_knives", "reopen-7c-merge-knives.md"),
    ):
        expect(name, fixture, True, ["S-8.6"])
    case("test_s_1_1_aliases_keep_seven_filenames")
    live = f1.live_close(root)
    log(live.dump())
    check(live.info.get("seven_old_count", 0) >= 5, "seven old names present")
    check(live.info.get("new_family") is False, "no intake.md family")
    case("test_s_1_1_tokens_remain")
    check(all(live.info.get("token_%s" % tok) for tok in ("G1", "G2", "ACCEPTED")),
          "G1/G2/ACCEPTED still in")
    case("test_s_8_5_this_slug_stage_5_to_7_is_f1_only")
    check(live.info.get("files_closed") is True, "Files union closed")
    case("test_s_6_2_q6_stays_assumption")
    check(live.info.get("q6_open") is True and "S-6.3" not in live.red_codes,
          "Q6 not promoted")
    expect("test_s_6_3_q6_as_fact_blocks_g2", "q6-as-fact.md", True, ["S-6.3"])

print("failed=%d" % len(failures))
sys.exit(1 if failures else 0)
PY
