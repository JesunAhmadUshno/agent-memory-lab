"""Regenerate every results file in results/ from the code, or check them.

    python src/make_results.py           # write results/*.json
    python src/make_results.py --check   # exit 1 if any committed file differs

The data is synthetic and built in code, so the code is the evidence:
a byte-identical regeneration is the reproduction. Order matters: the
Deep verdict reads results/results_learn.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ablations import run_ablations  # noqa: E402
from memory import run_all as run_learn  # noqa: E402
from memory_build import run_all as run_build  # noqa: E402
from verdict import run_deep  # noqa: E402

RESULTS = os.path.join(os.path.dirname(HERE), "results")
RUNS = [("results_learn.json", run_learn), ("results_build.json", run_build),
        ("results_ablations.json", run_ablations), ("results_deep.json", run_deep)]


def render(run):
    return json.dumps(run(), indent=2, sort_keys=True) + "\n"


def stale(results_dir=RESULTS):
    """Names of the results files in results_dir that differ from a fresh run."""
    bad = []
    for name, run in RUNS:
        path = os.path.join(results_dir, name)
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if current != render(run):
            bad.append(name)
    return bad


if __name__ == "__main__":
    if "--check" in sys.argv:
        bad = stale()
        if bad:
            sys.exit("results differ from a fresh run: " + ", ".join(bad))
        print("results reproduced:", len(RUNS), "files byte-identical")
    else:
        for name, run in RUNS:
            with open(os.path.join(RESULTS, name), "w", encoding="utf-8") as fh:
                fh.write(render(run))
            print("wrote results/" + name)
