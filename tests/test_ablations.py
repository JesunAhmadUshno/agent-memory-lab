"""Checks for the Build ablations (src/ablations.py).

Run: python tests/test_ablations.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import memory  # noqa: E402
from ablations import answer_tiered_window, run_ablations  # noqa: E402
from memory_build import CONVERSATIONS, QUESTIONS_BUILD, build_store_extended, run_all  # noqa: E402

checks = 0


def check(cond, msg):
    global checks
    checks += 1
    assert cond, msg


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


# The window-parameterised read path equals answer_tiered at the recorded window of 4.
learn_store = memory.build_store()
for q in memory.QUESTIONS:
    check(answer_tiered_window(q, learn_store, memory.TURNS, 4) == memory.answer_tiered(q, store=learn_store),
          "learn parity " + q["id"])
for q in QUESTIONS_BUILD:
    turns = CONVERSATIONS[q["conversation"]]
    for st in (memory.build_store(turns), build_store_extended(turns)):
        check(answer_tiered_window(q, st, turns, 4) == memory.answer_tiered(q, store=st, turns=turns),
              "build parity " + q["id"])

r = run_ablations()
b = run_all()
sweep = {row["window"]: row for row in r["window_sweep"]}
check(sorted(sweep) == list(range(19)), "windows 0 to 18")
w4 = sweep[4]
check((w4["tiered_correct"], w4["tiered_words"]) == (15, 711), "window 4 tiered 15 of 24 at 711 words")
check((w4["extended_correct"], w4["extended_words"]) == (21, 735), "window 4 extended 21 of 24 at 735 words")
check(w4["tiered_ops"] == b["tiered_ops_total"] == 120, "window 4 ops 120")
for size, row in sweep.items():
    check(row["tiered_ops"] == 24 * (1 + size), "ops grow with window " + str(size))
    check(row["extended_correct"] == 21, "extended flat at 21 for window " + str(size))
    check(row["tiered_correct"] <= row["extended_correct"], "tiered never beats extended")
# The non-canonical facts sit at turns 8 and 10 of 18: windows of 8 and 10 reach them.
check(sweep[7]["tiered_correct"] == 15 and sweep[8]["tiered_correct"] == 18, "window 8 reaches turn 10")
check(sweep[9]["tiered_correct"] == 18 and sweep[10]["tiered_correct"] == 21, "window 10 reaches turn 8")

wt = r["write_time"]
check(wt["one_pass_words"] == 418 == b["words_total"], "one pass is the 418 Build words")
check(wt["designs"]["tiered"]["total_words"] == 711 + 418, "tiered read plus write")
check(wt["designs"]["extended"]["total_words"] == 735 + 2 * 418, "extended read plus two passes")
check(wt["designs"]["extended"]["total_words_one_pass"] == 735 + 418, "extended one-pass bound")
check(wt["designs"]["full"]["total_words"] == 3344, "full has no write cost")

h = r["heldout"]
check(h["questions"] == 6 and h["turns"] == 18, "held-out shape")
check((h["full_correct"], h["tiered_correct"], h["extended_correct"]) == (5, 0, 0), "held-out 5 / 0 / 0")
check(h["extended_store"] == h["store"] == {"name": "Sam Ortiz"}, "no held-out fact reaches either store")

ps = r["paired_stats"]
lo, hi = ps["accuracy_wilson95"]["full"]
check(lo < 21 / 24 < hi, "wilson interval contains the point estimate")
check(ps["mcnemar"]["full_vs_tiered"] == {"only_full": 6, "only_tiered": 0, "p_exact_two_sided": 0.03125},
      "tiered loses 6 discordant pairs, p = 2 / 2**6")
check(ps["mcnemar"]["full_vs_extended"]["p_exact_two_sided"] == 1.0, "no discordant pairs, p = 1")

path = os.path.join(ROOT, "results", "results_ablations.json")
check(load("results", "results_ablations.json") == json.loads(json.dumps(r)), "results file matches run")
check(os.path.exists(path), "results file present")

print("ablation tests: PASS,", checks, "checks")
