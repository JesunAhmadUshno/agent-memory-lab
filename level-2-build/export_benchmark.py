"""Export the benchmark inputs to benchmark.json.

Writes the Learn turns and questions, the Build conversations and
questions, and the held-out phrasing probe (level-2-build/ablations.py)
to one committed JSON file, so other tools (the site in site/) read the
exact turn texts from the repo instead of retyping them.

Deterministic: stable key order, so two runs produce a byte-identical
file. tests/test_ablations.py checks the file matches these sources.
Run: python level-2-build/export_benchmark.py
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "level-1-learn"))

import memory  # noqa: E402
import memory_build  # noqa: E402
from ablations import HELDOUT_CONVERSATION, HELDOUT_QUESTIONS  # noqa: E402

OUT = os.path.join(_HERE, "benchmark.json")


def benchmark():
    return {
        "data_label": "synthetic",
        "note": "Benchmark inputs exported from level-1-learn/memory.py, level-2-build/memory_build.py "
                "and level-2-build/ablations.py. Synthetic conversations built in code, no real data.",
        "recent_window": memory.RECENT_WINDOW,
        "learn": {"turns": memory.TURNS, "questions": memory.QUESTIONS},
        "build": {"conversations": memory_build.CONVERSATIONS, "questions": memory_build.QUESTIONS_BUILD},
        "heldout": {"turns": HELDOUT_CONVERSATION, "questions": HELDOUT_QUESTIONS},
    }


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(benchmark(), fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote", OUT)
