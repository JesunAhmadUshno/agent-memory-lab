# Release notes: agent-memory-lab (P29)

Compiled 2026-11-05 from the live GitHub releases, verified with
gh release list. Releases: v0.1, v0.5, and v1.0.

## v0.1: Learn, full context vs tiered memory

Release: https://github.com/JesunAhmadUshno/agent-memory-lab/releases/tag/v0.1

One synthetic conversation (24 turns, 179 words, 8 questions),
built in code. Full context 8 of 8 (accuracy 1.0) reading 1432
words; tiered memory (a canonical fact store of 7 entries plus a
4-turn recent window of 30 words) 7 of 8 (accuracy 0.875) reading
269 words. The single tiered miss was Q4, the door code, whose
non-canonical phrasing the write-time extractor missed. 76
hand-computed Learn checks plus the scaffold smoke test;
results_learn.json byte-identical across two runs. Grade 8,500
of 10,000. All data synthetic; cost is a word-count proxy and
latency a counted proxy, labelled as such.

## v0.5: Build, A/B run, full context vs tiered memory

Release: https://github.com/JesunAhmadUshno/agent-memory-lab/releases/tag/v0.5

The A/B run at larger scale: three synthetic conversations (54
turns, 418 words, 24 questions) in canonical, update,
noncanonical_extended, and noncanonical_unhandled strata. Full
context 21 of 24 (accuracy 0.875, 3344 words, 432 turns scanned);
tiered memory 15 of 24 (accuracy 0.625, 711 words, 120 counted
operations); tiered extended, measured separately, 21 of 24
(accuracy 0.875, 735 words). All three designs scored 0 of 3 on
noncanonical_unhandled and 3 of 3 on update questions. 284
hand-computed Build checks plus the 76 Learn checks and the
scaffold smoke test; results_build.json byte-identical across
two runs. Grade 7,850 of 10,000.

## v1.0: agent-memory-lab, Learn, Build and Deep done

Release: https://github.com/JesunAhmadUshno/agent-memory-lab/releases/tag/v1.0

Deep adds the written verdict, computed from the Build numbers
with no new benchmark run. Words per correct answer: full
159.238, tiered 47.4, tiered extended 35.0; correct per 1000
words: full 6.28, tiered 21.10, tiered extended 28.57 (rounded
here; full precision in level-3-deep/README.md). Tiered pays on
canonical plus update (15 of 15 at 468 words against 2090 for
full), does not pay in its original form on
noncanonical_extended (0 of 6), the extension recovers all 6 for
24 extra words (4.0 per recovered answer), and no design pays on
noncanonical_unhandled (0 of 3 for all). Tiered against full
saves 2633 words and loses 6 answers, break-even 438.833333
words per answer. The scaling table is a labelled projection,
not a measurement at scale. 68 hand-computed Deep checks plus
the 284 Build checks, the 76 Learn checks, and the scaffold
smoke test; results_deep.json byte-identical across two runs.
Grade 8,000 of 10,000.

The v1.1 backlog is ROADMAP.md in the repo: semantic extraction,
value-before-label coverage, real conversations reported
separately from synthetic results, real token and wall-time
measurement, a scale run, a history-aware store, a fallback
policy, and a window policy study. None of those items are in
v1.0.
