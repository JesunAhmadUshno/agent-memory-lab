"""Agent memory Deep: the verdict analysis over the Build run.

No new benchmark is run here. This module imports the measured Build
results (src/memory_build.py run_all) and reads the Learn
results file, then computes the cost-benefit verdict defined in
experiments/2026-11-05-deep-design.md: words per correct answer, savings, break-even values,
per-stratum efficiency, and a scaling projection.

The projection is arithmetic from measured word counts under a stated
assumption (fixed question and fact counts, transcript grows by a
factor). It is labelled a projection everywhere and is not a
measurement at scale.

Cost remains the Build word-count proxy and latency the counted
proxy. No wall-clock time, no real tokenizer. Standard library only,
deterministic: no timing fields, stable rounding to 6 places.
"""

import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src"))

from memory_build import run_all as build_run_all  # noqa: E402

PROJECTION_FACTORS = (1, 5, 10, 50, 100)


def _r6(x):
    return round(x, 6)


def _per_correct(words, correct):
    if correct == 0:
        return None
    return _r6(words / correct)


def run_deep():
    b = build_run_all()
    learn_path = os.path.join(_ROOT, "results", "results_learn.json")
    with open(learn_path, encoding="utf-8") as fh:
        learn = json.load(fh)

    designs = {
        "full": {
            "correct": b["full_correct"],
            "accuracy": b["full_accuracy"],
            "words_total": b["full_words_total"],
            "ops_total": b["full_turns_scanned_total"],
        },
        "tiered": {
            "correct": b["tiered_correct"],
            "accuracy": b["tiered_accuracy"],
            "words_total": b["tiered_words_total"],
            "ops_total": b["tiered_ops_total"],
        },
        "extended": {
            "correct": b["extended_correct"],
            "accuracy": b["extended_accuracy"],
            "words_total": b["extended_words_total"],
            "ops_total": b["extended_ops_total"],
        },
    }
    for d in designs.values():
        d["words_per_correct"] = _per_correct(d["words_total"], d["correct"])
        d["correct_per_1000_words"] = _r6(d["correct"] / d["words_total"] * 1000)

    full = designs["full"]
    tiered = designs["tiered"]
    ext = designs["extended"]

    savings = {}
    for name in ("tiered", "extended"):
        d = designs[name]
        saved = full["words_total"] - d["words_total"]
        savings[name] = {
            "words_saved_vs_full": saved,
            "ratio_vs_full": _r6(full["words_total"] / d["words_total"]),
            "fraction_saved_vs_full": _r6(saved / full["words_total"]),
            "accuracy_delta_vs_full": _r6(d["accuracy"] - full["accuracy"]),
            "correct_delta_vs_full": d["correct"] - full["correct"],
        }

    lost = full["correct"] - tiered["correct"]
    gained = ext["correct"] - tiered["correct"]
    extra = ext["words_total"] - tiered["words_total"]
    breakeven = {
        "tiered_vs_full_words_saved": full["words_total"] - tiered["words_total"],
        "tiered_vs_full_answers_lost": lost,
        "tiered_vs_full_breakeven_value_words": _r6(
            (full["words_total"] - tiered["words_total"]) / lost) if lost else None,
        "extended_vs_tiered_extra_words": extra,
        "extended_vs_tiered_answers_gained": gained,
        "extended_vs_tiered_cost_per_recovered_word": _r6(extra / gained) if gained else None,
        "extended_vs_full_words_saved": full["words_total"] - ext["words_total"],
        "extended_vs_full_answers_lost": full["correct"] - ext["correct"],
        "extended_dominates_full_on_this_set": (
            ext["correct"] == full["correct"]
            and ext["words_total"] < full["words_total"]),
    }

    # Per-stratum words, summed from the Build per-question rows.
    strata = {}
    for name in ("canonical", "update", "noncanonical_extended",
                 "noncanonical_unhandled"):
        rows = [r for r in b["per_question"] if r["stratum"] == name]
        fw = sum(r["full_words_read"] for r in rows)
        tw = sum(r["tiered_words_read"] for r in rows)
        ew = sum(r["extended_words_read"] for r in rows)
        fc = sum(1 for r in rows if r["full_correct"])
        tc = sum(1 for r in rows if r["tiered_correct"])
        ec = sum(1 for r in rows if r["extended_correct"])
        strata[name] = {
            "questions": len(rows),
            "full_words": fw,
            "tiered_words": tw,
            "extended_words": ew,
            "full_correct": fc,
            "tiered_correct": tc,
            "extended_correct": ec,
            "full_words_per_correct": _per_correct(fw, fc),
            "tiered_words_per_correct": _per_correct(tw, tc),
            "extended_words_per_correct": _per_correct(ew, ec),
        }

    covered = {
        "questions": strata["canonical"]["questions"] + strata["update"]["questions"],
        "full_words": strata["canonical"]["full_words"] + strata["update"]["full_words"],
        "tiered_words": strata["canonical"]["tiered_words"] + strata["update"]["tiered_words"],
        "extended_words": strata["canonical"]["extended_words"] + strata["update"]["extended_words"],
        "full_correct": strata["canonical"]["full_correct"] + strata["update"]["full_correct"],
        "tiered_correct": strata["canonical"]["tiered_correct"] + strata["update"]["tiered_correct"],
        "extended_correct": strata["canonical"]["extended_correct"] + strata["update"]["extended_correct"],
    }

    projection = []
    for f in PROJECTION_FACTORS:
        fw = full["words_total"] * f
        projection.append({
            "factor": f,
            "full_words_projected": fw,
            "tiered_words": tiered["words_total"],
            "extended_words": ext["words_total"],
            "full_scans_projected": full["ops_total"] * f,
            "tiered_ops": tiered["ops_total"],
            "tiered_ratio_projected": _r6(fw / tiered["words_total"]),
        })

    verdict = {
        "tiered_pays_on_covered_strata": (
            covered["tiered_correct"] == covered["questions"]
            and covered["tiered_words"] < covered["full_words"]),
        "tiered_fails_on_noncanonical_extended": (
            strata["noncanonical_extended"]["tiered_correct"] == 0
            and strata["noncanonical_extended"]["questions"] > 0),
        "extension_recovers_all_extended_stratum": (
            strata["noncanonical_extended"]["extended_correct"]
            == strata["noncanonical_extended"]["questions"]),
        "no_design_pays_on_unhandled": (
            strata["noncanonical_unhandled"]["full_correct"] == 0
            and strata["noncanonical_unhandled"]["tiered_correct"] == 0
            and strata["noncanonical_unhandled"]["extended_correct"] == 0),
        "updates_return_later_value_in_all_designs": (
            strata["update"]["full_correct"] == strata["update"]["questions"]
            and strata["update"]["tiered_correct"] == strata["update"]["questions"]
            and strata["update"]["extended_correct"] == strata["update"]["questions"]),
    }

    return {
        "level": "deep",
        "data_label": "synthetic",
        "data_note": "Verdict computed from the Build run on three fixed "
                     "synthetic conversations. No real data, no new "
                     "benchmark run at this level.",
        "cost_proxy_note": "words are the Build word-count proxy "
                           "computed as len(text.split()) over the text "
                           "actually read. It is not a real tokenizer "
                           "token count. Operations are counted proxies, "
                           "not wall time.",
        "projection_note": "The scaling table is a projection from "
                           "measured word counts, not a measurement at "
                           "scale. Assumption: question and fact counts "
                           "stay fixed while the transcript grows by the "
                           "factor. If fact counts grow with the "
                           "transcript, tiered read cost rises and the "
                           "projected ratios are upper bounds.",
        "source_build": {
            "conversations": b["conversations"],
            "turns_total": b["turns_total"],
            "words_total": b["words_total"],
            "questions": b["questions"],
        },
        "designs": designs,
        "savings": savings,
        "breakeven": breakeven,
        "strata": strata,
        "covered_strata_canonical_plus_update": covered,
        "projection": projection,
        "verdict": verdict,
        "learn_reference": {
            "full_words_total": learn["full_words_total"],
            "full_correct": learn["full_correct"],
            "full_words_per_correct": _per_correct(
                learn["full_words_total"], learn["full_correct"]),
            "tiered_words_total": learn["tiered_words_total"],
            "tiered_correct": learn["tiered_correct"],
            "tiered_words_per_correct": _per_correct(
                learn["tiered_words_total"], learn["tiered_correct"]),
            "tiered_ratio_vs_full": _r6(
                learn["full_words_total"] / learn["tiered_words_total"]),
        },
    }
