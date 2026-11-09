"""Hand-computed Build tests for agent-memory-lab.

Every expected value below is an oracle from experiments/2026-11-05-build-design.md,
computed from the fixed synthetic turn texts before the code ran.
Run: python tests/test_build_memory.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from memory import build_store, word_count  # noqa: E402
from memory_build import (  # noqa: E402
    CONVERSATIONS,
    QUESTIONS_BUILD,
    build_store_extended,
    conversation_words,
    run_all,
)

checks = 0


def check(cond, msg):
    global checks
    checks += 1
    assert cond, msg


# Conversation shapes and hand word counts.
check(len(CONVERSATIONS) == 3, "3 synthetic conversations")
check(sum(len(t) for t in CONVERSATIONS.values()) == 54, "54 turns total")
check(conversation_words(CONVERSATIONS["A"]) == 140, "conv A 140 words")
check(conversation_words(CONVERSATIONS["B"]) == 139, "conv B 139 words")
check(conversation_words(CONVERSATIONS["C"]) == 139, "conv C 139 words")
check(sum(conversation_words(t) for t in CONVERSATIONS.values()) == 418,
      "418 words total")
for cid, turns in CONVERSATIONS.items():
    check(len(turns) == 18, cid + " has 18 turns")
    check(sum(word_count(t) for t in turns[-4:]) == 27,
          cid + " recent window is 27 words")
check(word_count(CONVERSATIONS["A"][8]) == 15, "A turn 8 has 15 words")
check(word_count(CONVERSATIONS["B"][12]) == 13, "B turn 12 has 13 words")
check(len(QUESTIONS_BUILD) == 24, "24 questions")

# Strata sizes.
strata_counts = {}
for q in QUESTIONS_BUILD:
    strata_counts[q["stratum"]] = strata_counts.get(q["stratum"], 0) + 1
check(strata_counts == {"canonical": 12, "update": 3,
                        "noncanonical_extended": 6,
                        "noncanonical_unhandled": 3}, "strata sizes")

# Original tiered stores: hand-computed contents, updates, misses.
check(build_store(CONVERSATIONS["A"]) == {
    "name": "Maya Chen", "home city": "Toronto",
    "favorite color": "green", "project codename": "Aurora",
    "pet name": "Biscuit", "next flight number": "AC847",
}, "store A contents")
check(build_store(CONVERSATIONS["B"]) == {
    "name": "Jonas Reid", "home city": "Berlin",
    "favorite food": "sushi", "team codename": "Beacon",
    "dog name": "Rocky", "next train number": "ICE721",
}, "store B contents")
check(build_store(CONVERSATIONS["C"]) == {
    "name": "Priya Nair", "home city": "Mumbai",
    "favorite color": "yellow", "study codename": "Compass",
    "cat name": "Miso", "next bus number": "B42",
}, "store C contents")
for cid in ("A", "B", "C"):
    check(len(build_store(CONVERSATIONS[cid])) == 6,
          "original store size 6 for " + cid)
    check(len(build_store_extended(CONVERSATIONS[cid])) == 8,
          "extended store size 8 for " + cid)

# Updates: the later value wins in both store designs.
check(build_store(CONVERSATIONS["A"])["favorite color"] == "green",
      "A color update blue to green")
check(build_store(CONVERSATIONS["B"])["favorite food"] == "sushi",
      "B food update pasta to sushi")
check(build_store(CONVERSATIONS["C"])["favorite color"] == "yellow",
      "C color update red to yellow")

# Extended store additions and the unhandled keys absent everywhere.
ext_a = build_store_extended(CONVERSATIONS["A"])
check(ext_a["door code"] == "4821", "extended A door code")
check(ext_a["backup email"] == "maya@example.com", "extended A email")
check(build_store_extended(CONVERSATIONS["B"])["gate code"] == "1934",
      "extended B gate code")
check(build_store_extended(CONVERSATIONS["C"])["safe code"] == "6607",
      "extended C safe code")
for cid, key in (("A", "locker code"), ("B", "alarm code"),
                 ("C", "bike code")):
    check(key not in build_store(CONVERSATIONS[cid]),
          "unhandled key absent from original store " + cid)
    check(key not in build_store_extended(CONVERSATIONS[cid]),
          "unhandled key absent from extended store " + cid)
for cid, key in (("A", "door code"), ("B", "gate code"),
                 ("C", "safe code")):
    check(key not in build_store(CONVERSATIONS[cid]),
          "noncanonical code absent from original store " + cid)

# Totals through the runner.
r = run_all()
check(r["conversations"] == 3 and r["turns_total"] == 54, "runner shape")
check(r["words_total"] == 418, "runner words total 418")
check(r["full_correct"] == 21 and r["full_accuracy"] == 0.875,
      "full 21 of 24")
check(r["tiered_correct"] == 15 and r["tiered_accuracy"] == 0.625,
      "tiered 15 of 24")
check(r["extended_correct"] == 21 and r["extended_accuracy"] == 0.875,
      "extended 21 of 24")
check(r["full_words_total"] == 3344, "full words total 3344")
check(r["tiered_words_total"] == 711, "tiered words total 711")
check(r["tiered_words_mean"] == 29.625, "tiered words mean 29.625")
check(r["extended_words_total"] == 735, "extended words total 735")
check(r["extended_words_mean"] == 30.625, "extended words mean 30.625")
check(r["full_turns_scanned_total"] == 432, "full scans 432 total")
check(r["tiered_ops_total"] == 120, "tiered ops 120 total")
check(r["extended_ops_total"] == 120, "extended ops 120 total")

# Strata outcomes.
check(r["strata"]["canonical"] == {"questions": 12, "full_correct": 12,
      "tiered_correct": 12, "extended_correct": 12}, "canonical stratum")
check(r["strata"]["update"] == {"questions": 3, "full_correct": 3,
      "tiered_correct": 3, "extended_correct": 3}, "update stratum")
check(r["strata"]["noncanonical_extended"] == {
      "questions": 6, "full_correct": 6, "tiered_correct": 0,
      "extended_correct": 6}, "noncanonical_extended stratum")
check(r["strata"]["noncanonical_unhandled"] == {
      "questions": 3, "full_correct": 0, "tiered_correct": 0,
      "extended_correct": 0}, "noncanonical_unhandled stratum")

# Per-question answers, word counts, and ops.
conv_words = {"A": 140, "B": 139, "C": 139}
for row in r["per_question"]:
    qid = row["id"]
    check(row["full_words_read"] == conv_words[row["conversation"]],
          "full words for " + qid)
    check(row["full_turns_scanned"] == 18, "full scans 18 for " + qid)
    check(row["tiered_ops_count"] == 5, "tiered ops 5 for " + qid)
    check(row["extended_ops_count"] == 5, "extended ops 5 for " + qid)
    if row["stratum"] == "noncanonical_unhandled":
        check(row["full_answer"] is None, "full misses unhandled " + qid)
        check(row["tiered_answer"] is None, "tiered misses " + qid)
        check(row["extended_answer"] is None, "extended misses " + qid)
        check(row["tiered_words_read"] == 27, "miss words 27 for " + qid)
        check(row["extended_words_read"] == 27,
              "extended miss words 27 for " + qid)
    elif row["stratum"] == "noncanonical_extended":
        check(row["full_correct"] is True, "full gets extended " + qid)
        check(row["tiered_answer"] is None,
              "tiered misses extended stratum " + qid)
        check(row["tiered_words_read"] == 27,
              "tiered miss words 27 for " + qid)
        check(row["extended_correct"] is True,
              "extended gets its stratum " + qid)
        check(row["extended_words_read"] == 31,
              "extended hit words 31 for " + qid)
    else:
        check(row["full_correct"] is True, "full correct " + qid)
        check(row["tiered_correct"] is True, "tiered correct " + qid)
        check(row["extended_correct"] is True, "extended correct " + qid)
        expected_words = 32 if row["expected"] in (
            "AC847", "ICE721", "B42") else 31
        check(row["tiered_words_read"] == expected_words,
              "tiered hit words for " + qid)
        check(row["extended_words_read"] == expected_words,
              "extended hit words for " + qid)

# Update questions return the later value in all three designs.
for qid, later in (("A8", "green"), ("B8", "sushi"), ("C8", "yellow")):
    row = [x for x in r["per_question"] if x["id"] == qid][0]
    check(row["full_answer"] == later, qid + " full returns update")
    check(row["tiered_answer"] == later, qid + " tiered returns update")
    check(row["extended_answer"] == later, qid + " extended returns update")

# Results file, if present, matches the runner output exactly.
path = os.path.join(ROOT, "results", "results_build.json")
if os.path.exists(path):
    with open(path, encoding="utf-8") as fh:
        saved = json.load(fh)
    check(saved == r, "results_build.json matches run_all()")

print("build memory tests: PASS,", checks, "checks")
