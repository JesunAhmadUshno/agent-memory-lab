# agent-memory-lab

Agent memory, light scope: tiered memory against full context on a long-conversation benchmark, with one A/B table for accuracy, a latency proxy, and a cost word proxy. Plain scope, stated first: all data in this repo is synthetic, built in code. Cost is a word-count proxy (words actually read, counted as len(text.split())); it is not a real tokenizer token count. Latency is a counted proxy (turns scanned or operations counted); no wall-clock time is measured. Extractors are hand-written patterns; there is no semantic retrieval.

- Learn: full context against tiered memory on one synthetic conversation (24 turns, 179 words, 8 questions). Full 8 of 8 (accuracy 1.0, 1432 words); tiered 7 of 8 (accuracy 0.875, 269 words). The single tiered miss was the door code phrased non-canonically. 76 checks. Grade 8,500 of 10,000.
- Build: the A/B run at larger scale on three synthetic conversations (54 turns, 418 words, 24 questions, four named strata). Full context 21 of 24 (0.875, 3344 words, 432 turns scanned); tiered memory 15 of 24 (0.625, 711 words, 120 operations); tiered extended 21 of 24 (0.875, 735 words, 120 operations). 284 checks. Grade 7,850 of 10,000.
- Deep: a written verdict computed from the Build numbers, with no new benchmark run. Words per correct answer: full 159.238, tiered 47.4, tiered extended 35.0. Tiered pays on canonical plus update (15 of 15 at 468 words against 2090 for full), does not pay in its original form on noncanonical_extended (0 of 6), the extension recovers all 6 for 24 extra words (4.0 per recovered answer), and no design pays on noncanonical_unhandled (0 of 3 for all). The scaling table is a labelled projection, not a measurement at scale. 68 checks. Grade 8,000 of 10,000.

Tests: 428 checks in total (76 Learn, 284 Build, 68 Deep), plus the scaffold smoke test.

Grades on record (of 10,000): Learn 8,500, Build 7,850, Deep 8,000.

Every number above is already published in this repo (README.md, DOSSIER.md, and the three level READMEs and results files) and reproduced by the runners in this repo, checked in CI. The v1.1 backlog in ROADMAP.md names semantic extraction, real conversation data, and real token and wall-time measurement.

Releases: https://github.com/JesunAhmadUshno/agent-memory-lab/releases
