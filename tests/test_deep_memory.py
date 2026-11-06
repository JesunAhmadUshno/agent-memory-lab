"""Hand-computed Deep tests for agent-memory-lab.

Every expected value below is an oracle from level-3-deep/DEEP-SPEC.md,
computed by hand from the Build per-question rows before the Deep code
ran. Run: python tests/test_deep_memory.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))

from verdict import run_deep  # noqa: E402

checks = 0


def check(cond, msg):
    global checks
    checks += 1
    assert cond, msg


r = run_deep()

# Source shape: the verdict is over the Build run, nothing new.
check(r["level"] == "deep", "level deep")
check(r["data_label"] == "synthetic", "synthetic label")
check(r["source_build"] == {"conversations": 3, "turns_total": 54,
      "words_total": 418, "questions": 24}, "source build shape")

# Overall design totals, copied from the measured Build results.
check(r["designs"]["full"]["correct"] == 21, "full 21 correct")
check(r["designs"]["full"]["accuracy"] == 0.875, "full accuracy")
check(r["designs"]["full"]["words_total"] == 3344, "full words 3344")
check(r["designs"]["full"]["ops_total"] == 432, "full scans 432")
check(r["designs"]["tiered"]["correct"] == 15, "tiered 15 correct")
check(r["designs"]["tiered"]["accuracy"] == 0.625, "tiered accuracy")
check(r["designs"]["tiered"]["words_total"] == 711, "tiered words 711")
check(r["designs"]["tiered"]["ops_total"] == 120, "tiered ops 120")
check(r["designs"]["extended"]["correct"] == 21, "extended 21 correct")
check(r["designs"]["extended"]["accuracy"] == 0.875, "extended accuracy")
check(r["designs"]["extended"]["words_total"] == 735, "extended words 735")
check(r["designs"]["extended"]["ops_total"] == 120, "extended ops 120")

# Words per correct answer, hand divided in the spec.
check(r["designs"]["full"]["words_per_correct"] == 159.238095,
      "full words per correct")
check(r["designs"]["tiered"]["words_per_correct"] == 47.4,
      "tiered words per correct")
check(r["designs"]["extended"]["words_per_correct"] == 35.0,
      "extended words per correct")

# Correct per 1000 words.
check(r["designs"]["full"]["correct_per_1000_words"] == 6.279904,
      "full correct per 1000")
check(r["designs"]["tiered"]["correct_per_1000_words"] == 21.097046,
      "tiered correct per 1000")
check(r["designs"]["extended"]["correct_per_1000_words"] == 28.571429,
      "extended correct per 1000")

# Savings against full.
check(r["savings"]["tiered"]["words_saved_vs_full"] == 2633,
      "tiered saves 2633")
check(r["savings"]["tiered"]["ratio_vs_full"] == 4.703235,
      "tiered ratio 4.703235")
check(r["savings"]["tiered"]["fraction_saved_vs_full"] == 0.78738,
      "tiered fraction saved")
check(r["savings"]["tiered"]["accuracy_delta_vs_full"] == -0.25,
      "tiered accuracy delta -0.25")
check(r["savings"]["tiered"]["correct_delta_vs_full"] == -6,
      "tiered loses 6")
check(r["savings"]["extended"]["words_saved_vs_full"] == 2609,
      "extended saves 2609")
check(r["savings"]["extended"]["ratio_vs_full"] == 4.54966,
      "extended ratio 4.54966")
check(r["savings"]["extended"]["fraction_saved_vs_full"] == 0.780203,
      "extended fraction saved")
check(r["savings"]["extended"]["accuracy_delta_vs_full"] == 0.0,
      "extended accuracy delta 0")
check(r["savings"]["extended"]["correct_delta_vs_full"] == 0,
      "extended loses 0")

# Break-even and payoff.
b = r["breakeven"]
check(b["tiered_vs_full_words_saved"] == 2633, "breakeven saved 2633")
check(b["tiered_vs_full_answers_lost"] == 6, "breakeven lost 6")
check(b["tiered_vs_full_breakeven_value_words"] == 438.833333,
      "breakeven value 438.833333")
check(b["extended_vs_tiered_extra_words"] == 24, "extension extra 24")
check(b["extended_vs_tiered_answers_gained"] == 6, "extension gains 6")
check(b["extended_vs_tiered_cost_per_recovered_word"] == 4.0,
      "extension 4.0 words per recovered answer")
check(b["extended_vs_full_words_saved"] == 2609, "ext vs full saved")
check(b["extended_vs_full_answers_lost"] == 0, "ext vs full lost 0")
check(b["extended_dominates_full_on_this_set"] is True,
      "extended dominates full on this set")

# Per-stratum words, correct counts, and words per correct.
s = r["strata"]
check(s["canonical"] == {"questions": 12, "full_words": 1672,
      "tiered_words": 375, "extended_words": 375, "full_correct": 12,
      "tiered_correct": 12, "extended_correct": 12,
      "full_words_per_correct": 139.333333,
      "tiered_words_per_correct": 31.25,
      "extended_words_per_correct": 31.25}, "canonical stratum verdict")
check(s["update"] == {"questions": 3, "full_words": 418,
      "tiered_words": 93, "extended_words": 93, "full_correct": 3,
      "tiered_correct": 3, "extended_correct": 3,
      "full_words_per_correct": 139.333333,
      "tiered_words_per_correct": 31.0,
      "extended_words_per_correct": 31.0}, "update stratum verdict")
check(s["noncanonical_extended"]["questions"] == 6, "ext stratum size")
check(s["noncanonical_extended"]["full_words"] == 836, "ext full words")
check(s["noncanonical_extended"]["tiered_words"] == 162,
      "ext tiered words")
check(s["noncanonical_extended"]["extended_words"] == 186,
      "ext extended words")
check(s["noncanonical_extended"]["tiered_correct"] == 0,
      "ext tiered 0 correct")
check(s["noncanonical_extended"]["tiered_words_per_correct"] is None,
      "ext tiered per-correct null at 0 correct")
check(s["noncanonical_extended"]["extended_words_per_correct"] == 31.0,
      "ext extended per-correct 31.0")
check(s["noncanonical_unhandled"]["full_words"] == 418,
      "unhandled full words")
check(s["noncanonical_unhandled"]["tiered_words"] == 81,
      "unhandled tiered words")
check(s["noncanonical_unhandled"]["full_words_per_correct"] is None,
      "unhandled full per-correct null")
check(s["noncanonical_unhandled"]["tiered_words_per_correct"] is None,
      "unhandled tiered per-correct null")
check(s["noncanonical_unhandled"]["extended_words_per_correct"] is None,
      "unhandled extended per-correct null")

# Covered strata (canonical plus update): tiered already pays in full.
c = r["covered_strata_canonical_plus_update"]
check(c == {"questions": 15, "full_words": 2090, "tiered_words": 468,
      "extended_words": 468, "full_correct": 15, "tiered_correct": 15,
      "extended_correct": 15}, "covered strata totals")

# Scaling projection: labelled projection, hand-multiplied in the spec.
expected_projection = [
    {"factor": 1, "full_words_projected": 3344, "tiered_words": 711,
     "extended_words": 735, "full_scans_projected": 432,
     "tiered_ops": 120, "tiered_ratio_projected": 4.703235},
    {"factor": 5, "full_words_projected": 16720, "tiered_words": 711,
     "extended_words": 735, "full_scans_projected": 2160,
     "tiered_ops": 120, "tiered_ratio_projected": 23.516174},
    {"factor": 10, "full_words_projected": 33440, "tiered_words": 711,
     "extended_words": 735, "full_scans_projected": 4320,
     "tiered_ops": 120, "tiered_ratio_projected": 47.032349},
    {"factor": 50, "full_words_projected": 167200, "tiered_words": 711,
     "extended_words": 735, "full_scans_projected": 21600,
     "tiered_ops": 120, "tiered_ratio_projected": 235.161744},
    {"factor": 100, "full_words_projected": 334400, "tiered_words": 711,
     "extended_words": 735, "full_scans_projected": 43200,
     "tiered_ops": 120, "tiered_ratio_projected": 470.323488},
]
check(r["projection"] == expected_projection, "projection table")
check("not a measurement" in r["projection_note"],
      "projection labelled not a measurement")

# Verdict booleans.
v = r["verdict"]
check(v["tiered_pays_on_covered_strata"] is True, "tiered pays covered")
check(v["tiered_fails_on_noncanonical_extended"] is True,
      "tiered fails extended stratum")
check(v["extension_recovers_all_extended_stratum"] is True,
      "extension recovers its stratum")
check(v["no_design_pays_on_unhandled"] is True, "no design pays unhandled")
check(v["updates_return_later_value_in_all_designs"] is True,
      "updates return later value everywhere")

# Learn reference, context only.
lr = r["learn_reference"]
check(lr["full_words_total"] == 1432 and lr["full_correct"] == 8,
      "learn full reference")
check(lr["full_words_per_correct"] == 179.0, "learn full per correct")
check(lr["tiered_words_total"] == 269 and lr["tiered_correct"] == 7,
      "learn tiered reference")
check(lr["tiered_words_per_correct"] == 38.428571,
      "learn tiered per correct")
check(lr["tiered_ratio_vs_full"] == 5.32342, "learn ratio")

# Results file, if present, matches the runner output exactly.
path = os.path.join(ROOT, "level-3-deep", "results_deep.json")
if os.path.exists(path):
    with open(path, encoding="utf-8") as fh:
        saved = json.load(fh)
    check(saved == r, "results_deep.json matches run_deep()")

print("deep memory tests: PASS,", checks, "checks")
