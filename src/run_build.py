"""Run the Build A/B comparison and write results_build.json.

Deterministic: no timing fields, stable key order, so two runs produce
a byte-identical file.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory_build import run_all  # noqa: E402

if __name__ == "__main__":
    results = run_all()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "results_build.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("full:", results["full_correct"], "of", results["questions"],
          "tiered:", results["tiered_correct"], "of",
          results["questions"], "extended:", results["extended_correct"],
          "of", results["questions"])
    print("words: full total", results["full_words_total"],
          "tiered total", results["tiered_words_total"],
          "extended total", results["extended_words_total"])
    print("wrote", out)
