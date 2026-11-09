"""Hand-computed Learn tests for agent-memory-lab.

Every expected value below is an oracle from experiments/2026-11-05-learn-design.md,
counted by hand before the code was written. Run: python tests/test_learn_memory.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from memory import (  # noqa: E402
    QUESTIONS,
    TURNS,
    answer_full,
    answer_tiered,
    build_store,
    extract_value,
    recent_window,
    run_all,
    store_entry_text,
    transcript_words,
    word_count,
)

checks = 0


def check(cond, msg):
    global checks
    checks += 1
    assert cond, msg


# Conversation shape and hand word counts.
check(len(TURNS) == 24, "24 turns")
check(word_count(TURNS[0]) == 10, "turn 0 has 10 words")
check(word_count(TURNS[11]) == 15, "turn 11 has 15 words")
check(word_count(TURNS[21]) == 6, "turn 21 has 6 words")
check(transcript_words() == 179, "transcript is 179 words by hand count")
check(sum(word_count(t) for t in recent_window()) == 30, "recent window is 30 words")
check(len(recent_window()) == 4, "recent window is 4 turns")

# Extraction.
check(extract_value(TURNS[2]) == "Maya Chen", "name extraction")
check(extract_value(TURNS[11]) == "4821", "happens-to-be extraction")
check(extract_value(TURNS[21]) == "AC847", "flight extraction")
check(extract_value(TURNS[0]) is None, "filler turn has no is-value at end check")

# Tiered store: hand-computed contents, update, and the designed miss.
store = build_store()
check(store == {
    "name": "Maya Chen",
    "home city": "Toronto",
    "favorite color": "green",
    "project codename": "Aurora",
    "pet name": "Biscuit",
    "favorite food": "ramen",
    "next flight number": "AC847",
}, "store contents match hand oracle")
check(len(store) == 7, "store size 7")
check("door code" not in store, "door code missed by canonical extractor")
check(store["favorite color"] == "green", "turn 18 overwrites blue with green")
check(word_count(store_entry_text("name", "Maya Chen")) == 4, "name entry 4 words")
check(word_count(store_entry_text("next flight number", "AC847")) == 5, "flight entry 5 words")

# Per-question answers and word counts.
expected_tiered_words = {"Q1": 34, "Q2": 34, "Q3": 34, "Q4": 30,
                         "Q5": 34, "Q6": 34, "Q7": 34, "Q8": 35}
for q in QUESTIONS:
    f_ans, f_words, f_ops = answer_full(q)
    check(f_ans == q["expected"], "full answers " + q["id"])
    check(f_words == 179, "full reads 179 words for " + q["id"])
    check(f_ops == 24, "full scans 24 turns for " + q["id"])
    t_ans, t_words, t_ops = answer_tiered(q, store=store)
    check(t_words == expected_tiered_words[q["id"]], "tiered words " + q["id"])
    check(t_ops == 5, "tiered ops 5 for " + q["id"])
    if q["id"] == "Q4":
        check(t_ans is None, "tiered misses Q4 door code")
    else:
        check(t_ans == q["expected"], "tiered answers " + q["id"])

# Totals through the runner.
r = run_all()
check(r["full_correct"] == 8 and r["full_accuracy"] == 1.0, "full 8 of 8")
check(r["tiered_correct"] == 7 and r["tiered_accuracy"] == 0.875, "tiered 7 of 8")
check(r["full_words_total"] == 1432, "full words total 1432")
check(r["tiered_words_total"] == 269, "tiered words total 269")
check(r["tiered_words_mean"] == 33.625, "tiered words mean 33.625")
check(r["full_turns_scanned_total"] == 192, "full scans 192 total")
check(r["tiered_ops_total"] == 40, "tiered ops 40 total")
check(r["store_size"] == 7, "runner store size 7")
q4 = [row for row in r["per_question"] if row["id"] == "Q4"][0]
check(q4["full_correct"] is True and q4["tiered_correct"] is False, "Q4 is the trade-off case")
q6 = [row for row in r["per_question"] if row["id"] == "Q6"][0]
check(q6["full_answer"] == "green" and q6["tiered_answer"] == "green", "Q6 update handled by both")

# Results file, if present, matches the runner output exactly.
path = os.path.join(ROOT, "results", "results_learn.json")
if os.path.exists(path):
    with open(path, encoding="utf-8") as fh:
        saved = json.load(fh)
    check(saved == r, "results_learn.json matches run_all()")

print("learn memory tests: PASS,", checks, "checks")
