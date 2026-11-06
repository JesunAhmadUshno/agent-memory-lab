# agent-memory-lab

Agent memory, light scope: tiered memory against full context on a long-conversation benchmark, one A/B table for accuracy, latency, and cost.

Status: v1.0. Learn DONE, Build DONE, and Deep DONE (2026-11-05, ROADMAP-V3-BATCH).
Project: P29. Fleet node: BlackBoxV2. Wave: Waves 6 to 7.

## Start here

1. Read SPEC.md for scope and acceptance criteria.
2. Read DOSSIER.md for the past, present, and future of this problem.
3. Read NOVELTY.md for the proposed novelty (DRAFT, pending the Jev claim_check gate).
4. Start at level-1-learn/README.md, then level-2-build, then level-3-deep/README.md.
5. Read ROADMAP.md for the v1.1 backlog (the rest of the v2 Deep scope).

## Level map

- Level 1, Learn: DONE. Full context against tiered memory on one
  synthetic conversation (24 turns, 8 questions): full 8 of 8,
  tiered 7 of 8. See level-1-learn/README.md.
- Level 2, Build: DONE. The A/B run at larger scale: three synthetic
  conversations (54 turns, 24 questions, four named strata), one
  table for accuracy, latency proxy, and cost word proxy, plus a
  separately measured tiered extended design. See
  level-2-build/README.md.
- Level 3, Deep: DONE (compressed). A written verdict computed from
  the Build numbers: where tiered memory pays, where it does not,
  with break-even and per-stratum analysis and a labelled scaling
  projection. See level-3-deep/README.md.

## Benchmarks

Build level, measured 2026-11-05, synthetic data only, word-count
cost proxy (not real tokens) and counted latency proxy (no wall
time). Full method and per-stratum table: level-2-build/README.md.

| Design | Accuracy | Correct | Latency proxy (counted) | Cost proxy (words read) |
| --- | --- | --- | --- | --- |
| Full context | 0.875 | 21 of 24 | 432 turns scanned | 3344 |
| Tiered memory (Learn design) | 0.625 | 15 of 24 | 120 operations | 711 |
| Tiered extended (Build change) | 0.875 | 21 of 24 | 120 operations | 735 |

Deep verdict, computed 2026-11-05 from the Build numbers above (no
new benchmark run). Full tables: level-3-deep/README.md.

| Measure | Full | Tiered | Tiered extended |
| --- | --- | --- | --- |
| Words per correct answer | 159.238095 | 47.4 | 35.0 |
| Correct per 1000 words | 6.279904 | 21.097046 | 28.571429 |

Verdict in one line: tiered pays on canonical plus update (15 of 15
at 468 words against 2090 for full), does not pay in its original
form on noncanonical_extended (0 of 6), the extension recovers all 6
for 24 extra words (4.0 per recovered answer), and no design pays on
noncanonical_unhandled (0 of 3 for all). The scaling table in the
Deep README is a projection from measured word counts, not a
measurement at scale.

Learn level, for reference: full context 8 of 8 (accuracy 1.0, 1432
words), tiered 7 of 8 (accuracy 0.875, 269 words), on one synthetic
conversation of 24 turns and 179 words.

## Fan-out

Written fan-out set for v1.0, in fanout/: blog-post.md,
tutorial.md, website-page.md, linkedin-post.md (DRAFT NOT
POSTED), paper-candidate.md, and release-notes.md. The channel
log and per-piece publicity grades are in PUBLICITY.md.

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
