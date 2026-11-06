# Tutorial: P29 agent-memory-lab, course module

Module: P29-agent-memory-lab
By Jesun Ahmad Ushno
Date: 2026-11-05
License for this tutorial: CC BY 4.0. Code in the repo: Apache-2.0.

## What you will do

You will clone the agent-memory-lab repo, run all three levels,
run the test suite for each level, and read your own results
against the recorded v1.0 numbers. Every command below was
verified by running it in this fan-out cycle. The project needs
Python 3.11 or 3.12 and uses the standard library only. No GPU,
cluster, or credential is needed.

One scope fact governs every step: all data is synthetic, built
in code, with no real conversation or real data used. Cost is a
word-count proxy (words actually read, counted as
len(text.split())), not a real tokenizer token count. Latency is
a counted proxy (turns scanned or operations counted); no
wall-clock time is measured. Extractors are hand-written
patterns; there is no semantic retrieval.

## Step 0: Clone and enter the repo

```text
git clone https://github.com/JesunAhmadUshno/agent-memory-lab.git
cd agent-memory-lab
```

Optional smoke check, before the levels:

```text
python tests/test_smoke.py
```

Expected: scaffold smoke test: PASS, 8 files present.

## Step 1: Level 1, Learn, full context against tiered memory

Read level-1-learn/README.md first.

```text
python level-1-learn/run_learn.py
python tests/test_learn_memory.py
```

Expected: full: 8 of 8 tiered: 7 of 8; words: full total 1432
tiered total 269; learn memory tests: PASS, 76 checks. The
runner writes level-1-learn/results_learn.json deterministically:
two runs are byte-identical. The one tiered miss is Q4, the door
code, whose non-canonical phrasing the write-time extractor
misses.

## Step 2: Level 2, Build, the A/B run at larger scale

Read level-2-build/README.md and level-2-build/BUILD-SPEC.md.

```text
python level-2-build/run_build.py
python tests/test_build_memory.py
```

Expected: full: 21 of 24 tiered: 15 of 24 extended: 21 of 24;
words: full total 3344 tiered total 711 extended total 735;
build memory tests: PASS, 284 checks. The runner writes
level-2-build/results_build.json deterministically. Read the
per-stratum table in the Build README: the original tiered
design scores 0 of 6 on noncanonical_extended, the extended
design recovers all 6, and all three designs score 0 of 3 on
noncanonical_unhandled.

## Step 3: Level 3, Deep, the verdict

Read level-3-deep/README.md and level-3-deep/DEEP-SPEC.md. Deep
runs no new benchmark; it computes the verdict from the Build
run.

```text
python level-3-deep/run_deep.py
python tests/test_deep_memory.py
```

Expected: verdict: tiered pays on covered strata: True
extension cost per recovered answer: 4.0 words; deep memory
tests: PASS, 68 checks. The runner writes
level-3-deep/results_deep.json deterministically. Words per
correct answer: full 159.238, tiered 47.4, tiered extended 35.0.
The scaling table in the Deep README is a labelled projection
from measured word counts, not a measurement at scale.

## Step 4: Run the whole suite

```text
python tests/test_smoke.py
python tests/test_learn_memory.py
python tests/test_build_memory.py
python tests/test_deep_memory.py
```

Expected: 428 checks in total (76 Learn, 284 Build, 68 Deep),
plus the scaffold smoke test, all passing.

## What to try next

Change one planted fact in level-1-learn/memory.py to a new
non-canonical form, re-run Learn, and watch which design loses
the question and why. That single experiment teaches the central
lesson of this project: in a tiered design, extraction coverage,
not storage size, decides accuracy. The v1.1 backlog in
ROADMAP.md names the follow-on work, semantic extraction first.
None of the v1.1 items are done at v1.0.
