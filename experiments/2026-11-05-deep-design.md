# DEEP-SPEC: agent-memory-lab, Level 3 Deep (compressed)

Written before any Deep code, 2026-11-05. Scope from SPEC.md: a short
written verdict: where tiered memory pays, where it does not, with the
run's numbers. Compressed Deep per the December Compression Protocol:
the single hardest capability in the SPEC, built, tested, benchmarked,
with a failure-modes section. The rest of the v2 Deep scope is named
as the v1.1 backlog in the repo root ROADMAP.md.

## What Deep does and does not do

- Deep does NOT run a new conversation benchmark and does NOT change
  any Learn or Build result. It imports the measured Build results
  (level-2-build/results_build.json, via level-2-build/memory_build.py
  run_all) and the Learn totals (level-1-learn/results_learn.json,
  read only) and computes a verdict from those numbers alone.
- Every derived number below is hand-computed in this spec before the
  code runs. The code must reproduce them exactly. Any mismatch is a
  code bug, not a new finding.
- The scaling table is a PROJECTION from measured word counts under a
  stated assumption. It is never presented as measured at scale.

## Inputs (measured, from Build, 2026-11-05)

- 3 synthetic conversations, 54 turns, 418 words, 24 questions.
- Strata: canonical 12, update 3, noncanonical_extended 6,
  noncanonical_unhandled 3.
- Full context: 21 correct, accuracy 0.875, 3344 words, 432 turns
  scanned.
- Tiered memory (Learn design): 15 correct, accuracy 0.625, 711
  words, mean 29.625 per question, 120 operations.
- Tiered extended (Build change): 21 correct, accuracy 0.875, 735
  words, mean 30.625 per question, 120 operations.
- Per-stratum words and correct counts (summed by hand from the
  per-question rows in results_build.json):

| Stratum | Q | Full words | Tiered words | Ext words | Full | Tiered | Ext |
| --- | --- | --- | --- | --- | --- | --- | --- |
| canonical | 12 | 1672 | 375 | 375 | 12 | 12 | 12 |
| update | 3 | 418 | 93 | 93 | 3 | 3 | 3 |
| noncanonical_extended | 6 | 836 | 162 | 186 | 6 | 0 | 6 |
| noncanonical_unhandled | 3 | 418 | 81 | 81 | 0 | 0 | 0 |
| Total | 24 | 3344 | 711 | 735 | 21 | 15 | 21 |

Check: canonical tiered words: 9 hits at 31 plus 3 transport hits at
32 = 279 + 96 = 375. Update: 3 at 31 = 93. Extended stratum tiered:
6 misses at 27 = 162. Extended stratum extended: 6 hits at 31 = 186.
Unhandled: 3 misses at 27 = 81 in both tiered designs, 3 at the
conversation totals (140 + 139 + 139) = 418 for full.

## Hand-computed oracles (predicted before coding)

### Overall efficiency

- Words per correct answer: full 3344 / 21 = 159.238095 (rounded to
  6 places in results); tiered 711 / 15 = 47.4 exactly; extended
  735 / 21 = 35.0 exactly.
- Correct answers per 1000 words read: full 21 / 3344 x 1000 =
  6.279904; tiered 15 / 711 x 1000 = 21.097046; extended 21 / 735 x
  1000 = 28.571429 (all rounded to 6 places).
- Word savings against full: tiered saves 3344 - 711 = 2633 words,
  a ratio of 3344 / 711 = 4.703235 and a saved fraction of
  2633 / 3344 = 0.787380. Extended saves 3344 - 735 = 2609 words, a
  ratio of 3344 / 735 = 4.549660 and a saved fraction of
  2609 / 3344 = 0.780203 (ratios and fractions rounded to 6 places).
- Accuracy deltas against full: tiered 0.625 - 0.875 = -0.25;
  extended 0.875 - 0.875 = 0.0.

### Break-even and payoff

Define V as the value of one correct answer, expressed in words read
that a caller would pay to recover it. This is an analysis device,
not a measured price.

- Tiered against full: tiered saves 2633 words and loses 6 answers.
  Break-even V = 2633 / 6 = 438.833333. If V is above that, the lost
  answers cost more than the saving is worth and full wins on this
  accounting. If V is below that, tiered wins on this accounting.
  Either way the accuracy loss itself may be unacceptable for a use
  case, independent of V.
- Extended against tiered: extended costs 735 - 711 = 24 extra words
  and gains 6 answers. Cost per recovered answer = 24 / 6 = 4.0
  words. Extended pays for any V above 4.0, which is every plausible
  V. This is the cheapest recovery in the run.
- Extended against full: extended saves 2609 words and loses 0
  answers. On this data set extended strictly dominates full: same
  accuracy, less cost. No break-even is needed. The dominance holds
  only for the phrasing forms its extractors cover; see the verdict
  limits below.
- On the canonical plus update subset alone (15 questions), tiered
  and extended cost the same 468 words (375 + 93) and both answer
  15 of 15. The original tiered design already pays in full there,
  with no extension needed.

### Per-stratum words per correct answer

- canonical: full 1672 / 12 = 139.333333; tiered 375 / 12 = 31.25;
  extended 375 / 12 = 31.25.
- update: full 418 / 3 = 139.333333; tiered 93 / 3 = 31.0;
  extended 93 / 3 = 31.0.
- noncanonical_extended: full 836 / 6 = 139.333333; tiered has 0
  correct, so words per correct is undefined (recorded as null, with
  162 words spent for 0 correct); extended 186 / 6 = 31.0.
- noncanonical_unhandled: all three designs have 0 correct, so words
  per correct is null for all three, with words spent 418 (full),
  81 (tiered), 81 (extended). Cost spent with no return in every
  design.

### Scaling projection (projection, not measured)

Assumption, stated wherever the table is used: the number of
questions (24) and the number of stored facts stay fixed while the
transcript grows by a factor f of filler and history between the
same facts. Full context re-reads the whole transcript per question,
so its total scales as 3344 x f and its scans as 432 x f. Tiered
reads a fixed store entry plus a fixed 4-turn window, so its totals
stay at 711 and 735 words and 120 operations under this assumption.

| Factor f | Full words (proj) | Tiered words | Ext words | Full scans (proj) | Tiered ratio (proj) |
| --- | --- | --- | --- | --- | --- |
| 1 | 3344 | 711 | 735 | 432 | 4.703235 |
| 5 | 16720 | 711 | 735 | 2160 | 23.516174 |
| 10 | 33440 | 711 | 735 | 4320 | 47.032349 |
| 50 | 167200 | 711 | 735 | 21600 | 235.161744 |
| 100 | 334400 | 711 | 735 | 43200 | 470.323488 |

Projection limits, named in the README: if the fact count grows with
the transcript instead of staying fixed, the store grows too and the
tiered read cost rises; the ratios above are then upper bounds, not
predictions. Nothing at f above 1 was run.

### Learn reference (measured at Learn, for scale context only)

- Learn: full 1432 words for 8 correct (179.0 per correct), tiered
  269 words for 7 correct (38.428571 per correct), ratio 5.323420.
  The Build run is the verdict basis; Learn is context that the same
  trade-off appeared at the smaller scale.

## Verdict logic (the Deep claim the numbers must support)

- Tiered pays where facts arrive in forms the write-time extractor
  covers and are asked later: canonical and update strata, 15 of 15
  in both tiered designs at 468 words against 2090 words for full
  (1672 + 418), and updates return the later value in all designs.
- Tiered does not pay, in its original form, where phrasing falls
  outside the extractor: 0 of 6 on noncanonical_extended, the entire
  accuracy gap against full.
- Extending the extractor pays almost for free on this set: 24 extra
  words recover all 6, at 4.0 words per recovered answer, matching
  full accuracy at 735 words against 3344.
- No design pays on the unhandled form: 0 of 3 for full, tiered, and
  extended. The bottleneck there is extraction, not storage or read
  cost, because even re-reading everything returns nothing.
- Therefore the honest verdict is conditional: tiered memory is a
  cost win exactly as far as its extraction coverage reaches, and an
  accuracy loss beyond it. This set cannot judge semantic extraction,
  real conversations, or real token and wall-time costs.

## Acceptance

- level-3-deep/verdict.py computes every oracle above from the Build
  run_all output and the Learn results file, with no hard-coded
  totals except the hand oracles checked in the tests.
- tests/test_deep_memory.py checks every oracle by the values in
  this spec: overall efficiency, break-even values, per-stratum
  efficiency including the null cases, the projection table, the
  verdict booleans, and the Learn reference.
- All Learn tests (76 checks), Build tests (284 checks), and the
  scaffold smoke test still pass unchanged.
- Running level-3-deep/run_deep.py twice produces
  level-3-deep/results_deep.json byte-identical.
- Learn and Build results files are not changed by this level.
