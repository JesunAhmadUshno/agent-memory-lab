# Website page copy: agent-memory-lab (P29)

Status: DRAFT copy only, 2026-11-05. No website was changed by
this file.
Project: P29 agent-memory-lab, v1.0 (light scope)
Repo: https://github.com/JesunAhmadUshno/agent-memory-lab

## Headline

Tiered memory pays only where the extractor looks.

## Summary

agent-memory-lab compares two ways to answer questions about a
long conversation: re-read everything (full context), or extract
facts into a small store at write time and answer from the store
plus a short recent window (tiered memory). It runs the
comparison on synthetic data only, measures accuracy against a
word-count cost proxy and a counted latency proxy, and computes
a written verdict on where tiered memory pays and where it does
not.

All data is synthetic. Cost and latency are proxies, labelled as
such: cost is words actually read, not real tokenizer tokens,
and latency is turns or operations counted, not wall-clock time.
Extractors are hand patterns; there is no semantic retrieval.

## The measured result

Build level, three synthetic conversations, 54 turns, 24
questions:

| Design | Accuracy | Correct | Words read |
| --- | --- | --- | --- |
| Full context | 0.875 | 21 of 24 | 3344 |
| Tiered memory | 0.625 | 15 of 24 | 711 |
| Tiered extended | 0.875 | 21 of 24 | 735 |

Words per correct answer (Deep verdict): full 159.238, tiered
47.4, tiered extended 35.0. Tiered extended answers 21 of 24 at
735 words against 3344 for full context on the measured set:
extended dominates full on this set, and that dominance covers
only the phrasing forms its extractors parse.

## Where tiered memory pays, and where it does not

- Pays: canonical plus update strata, 15 of 15 at 468 words
  against 2090 for full context.
- Does not pay in its original form: noncanonical_extended, 0
  of 6. Two added write-time patterns recover all 6 for 24 extra
  words, 4.0 words per recovered answer.
- No design pays: noncanonical_unhandled, 0 of 3 for full,
  tiered, and extended alike. The failure there is extraction,
  not storage.

## Levels and grades

- Learn: full 8 of 8, tiered 7 of 8, on one synthetic
  conversation. Grade 8,500 of 10,000.
- Build: the A/B run at larger scale, four named strata. Grade
  7,850 of 10,000.
- Deep: the written verdict, computed from the Build numbers
  with no new benchmark run. Grade 8,000 of 10,000.

Tests: 428 checks (76 Learn, 284 Build, 68 Deep), plus the
scaffold smoke test.

## Call to action

Read the verdict in level-3-deep/README.md, run the tutorial in
fanout/tutorial.md, and check the v1.1 backlog in ROADMAP.md:
semantic extraction, real conversations reported separately,
and real token and wall-time measurement. None of the v1.1 items
are claimed as done.
