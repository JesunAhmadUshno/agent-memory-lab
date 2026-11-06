# agent-memory-lab

Agent memory, light scope: tiered memory against full context on a long-conversation benchmark, one A/B table for accuracy, latency, and cost.

Status: Learn DONE and Build DONE (2026-11-05, ROADMAP-V3-BATCH). Deep is still open. This is not v1.0.
Project: P29. Fleet node: BlackBoxV2. Wave: Waves 6 to 7.

## Start here

1. Read SPEC.md for scope and acceptance criteria.
2. Read DOSSIER.md for the past, present, and future of this problem.
3. Read NOVELTY.md for the proposed novelty (DRAFT, pending the Jev claim_check gate).
4. Start at level-1-learn/README.md, then level-2-build, then level-3-deep.

## Level map

- Level 1, Learn: DONE. Full context against tiered memory on one
  synthetic conversation (24 turns, 8 questions): full 8 of 8,
  tiered 7 of 8. See level-1-learn/README.md.
- Level 2, Build: DONE. The A/B run at larger scale: three synthetic
  conversations (54 turns, 24 questions, four named strata), one
  table for accuracy, latency proxy, and cost word proxy, plus a
  separately measured tiered extended design. See
  level-2-build/README.md.
- Level 3, Deep: OPEN. A short written verdict: where tiered memory
  pays, where it does not, with the run's numbers.

## Benchmarks

Build level, measured 2026-11-05, synthetic data only, word-count
cost proxy (not real tokens) and counted latency proxy (no wall
time). Full method and per-stratum table: level-2-build/README.md.

| Design | Accuracy | Correct | Latency proxy (counted) | Cost proxy (words read) |
| --- | --- | --- | --- | --- |
| Full context | 0.875 | 21 of 24 | 432 turns scanned | 3344 |
| Tiered memory (Learn design) | 0.625 | 15 of 24 | 120 operations | 711 |
| Tiered extended (Build change) | 0.875 | 21 of 24 | 120 operations | 735 |

Learn level, for reference: full context 8 of 8 (accuracy 1.0, 1432
words), tiered 7 of 8 (accuracy 0.875, 269 words), on one synthetic
conversation of 24 turns and 179 words.

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
