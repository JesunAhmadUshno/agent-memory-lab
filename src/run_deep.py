"""Run the Deep verdict analysis and write results_deep.json.

Deterministic: no timing fields, stable key order, so two runs produce
a byte-identical file.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verdict import run_deep  # noqa: E402

if __name__ == "__main__":
    results = run_deep()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "results_deep.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")
    b = results["breakeven"]
    print("verdict: tiered pays on covered strata:",
          results["verdict"]["tiered_pays_on_covered_strata"],
          "extension cost per recovered answer:",
          b["extended_vs_tiered_cost_per_recovered_word"], "words")
    print("wrote", out)
