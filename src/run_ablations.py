"""Run the Build ablations and write results_ablations.json.

Deterministic: no timing fields, stable key order, so two runs produce
a byte-identical file.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ablations import run_ablations  # noqa: E402

if __name__ == "__main__":
    results = run_ablations()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "results_ablations.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")
    w4 = results["window_sweep"][4]
    h = results["heldout"]
    print("window 4: tiered", w4["tiered_correct"], w4["tiered_words"], "extended", w4["extended_correct"],
          w4["extended_words"])
    print("held-out: full", h["full_correct"], "tiered", h["tiered_correct"], "extended", h["extended_correct"],
          "of", h["questions"])
    print("wrote", out)
