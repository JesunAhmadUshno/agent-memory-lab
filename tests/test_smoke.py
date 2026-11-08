"""Portfolio standard checks: required files exist, no public grade, results regenerate.

Run: python tests/test_smoke.py (also collected by pytest).
There is no lock to pin: the repo is not pre-registered (see PROPOSAL.md).
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import make_results  # noqa: E402

REQUIRED = ["README.md", "PROPOSAL.md", "REPORT.md", "CHANGELOG.md", "CITATION.cff", "SECURITY.md", "LICENSE",
            "src/memory.py", "src/memory_build.py", "src/ablations.py", "src/verdict.py", "src/make_results.py",
            "results/results_learn.json", "results/results_build.json", "results/results_ablations.json",
            "results/results_deep.json", "experiments/2026-11-05-learn-design.md",
            "experiments/2026-11-05-build-design.md", "experiments/2026-11-05-deep-design.md",
            "docs/decisions/0001-synthetic-data-and-word-proxies.md",
            "docs/decisions/0002-pattern-extractors-no-model.md"]
GRADE_MARKS = ["of 10,000", "of 10000", "/10000", "/10,000", "Grade:", "Grade ", "grade on record", "/1000 |"]


def public_text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "dist", ".rubric", "__pycache__")]
        for f in files:
            if f.endswith((".md", ".jsx", ".js", ".html", ".cff")):
                yield os.path.join(base, f)


def test_required_files_exist():
    missing = [p for p in REQUIRED if not os.path.exists(os.path.join(ROOT, p))]
    assert not missing, "missing: " + ", ".join(missing)


def find_grades(paths):
    hits = []
    for path in paths:
        text = open(path, encoding="utf-8").read()
        hits += [os.path.relpath(path, ROOT) + ": " + m for m in GRADE_MARKS if m in text]
    return hits


def test_no_public_grade():
    hits = find_grades(public_text_files())
    assert not hits, "grades are internal only: " + "; ".join(hits)


def test_grade_scan_catches_a_grade():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "x.md")
        open(p, "w").write("Grade 8,000 of 10,000\n")
        assert find_grades([p])


def test_results_regenerate_and_check_catches_a_change():
    assert make_results.stale() == [], "committed results differ from a fresh run"
    with tempfile.TemporaryDirectory() as tmp:
        for name, _ in make_results.RUNS:
            shutil.copy(os.path.join(make_results.RESULTS, name), tmp)
        path = os.path.join(tmp, "results_build.json")
        data = json.load(open(path))
        data["full_correct"] += 1
        json.dump(data, open(path, "w"), indent=2, sort_keys=True)
        assert make_results.stale(tmp) == ["results_build.json"]


if __name__ == "__main__":
    tests = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    for t in tests:
        t()
    print("layout check: PASS,", len(tests), "checks,", len(REQUIRED), "required files")
