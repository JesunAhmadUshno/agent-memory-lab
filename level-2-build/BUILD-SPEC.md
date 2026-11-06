# BUILD-SPEC: agent-memory-lab, Level 2 Build

Written before any Build code, 2026-11-05. Scope from SPEC.md: the A/B
run: accuracy, latency, and cost for full context against tiered memory,
in one table, at a larger scale than Learn.

## Design

- Standard library only, deterministic, no timing fields anywhere.
- Three synthetic conversations, labelled synthetic everywhere, built
  in code as fixed lists of 18 turns each (54 turns total, 418 words).
  No real conversation, no downloaded data, no person is represented.
  Conversation A reuses the Learn facts pattern with new turns around
  them; B and C are new synthetic people with parallel structure.
- Each conversation carries 8 labelled questions (24 total), in four
  named strata:
  - canonical: 4 per conversation, 12 total. Facts in the canonical
    "My ... is ..." form.
  - update: 1 per conversation, 3 total. A canonical fact stated
    twice; the later value is expected.
  - noncanonical_extended: 2 per conversation, 6 total. Facts in two
    non-canonical forms: the "happens to be" form and the
    "For the record, my ... is ..." form.
  - noncanonical_unhandled: 1 per conversation, 3 total. The value
    comes before its label ("I set 8842 as my locker code, ..."), a
    form none of the extractors in this level parse.
- Design A, full context: the Learn answer_full function, imported
  from level-1-learn/memory.py and run per conversation. It scans
  every turn of that conversation and extracts from the last turn
  containing the question key phrase.
- Design B, tiered memory: the Learn design, unchanged. The store is
  built by the Learn build_store (canonical pattern only) plus the
  last 4 turns as a recent window, answered by the Learn
  answer_tiered. Learn results are not changed by this level.
- Design B-plus, tiered extended (a Build design change, measured
  separately, never folded into Design B): the store starts from the
  Learn canonical store, then two added write-time patterns run in
  turn order:
  - ^By the way, the (.+?), if you ever need it, happens to be (.+?)\.$
  - ^For the record, my (.+?) is (.+?)\.$
  Read time is the Learn answer_tiered against the extended store.
  This isolates the effect of extending the extractor: same read
  path, same window, only the write-time store differs.

## Cost and latency proxies (labelled honestly)

- Cost is a word-count proxy: len(text.split()) over the text actually
  read, exactly as in Learn. It is NOT a real tokenizer token count
  and is never called tokens in results.
- Latency proxy is a deterministic count: full scans 18 turns per
  question for its conversation; tiered counts 1 store lookup plus
  4 window turns, 5 per question. No wall-clock time is measured.

## Hand counts

Per conversation, word counts counted from the fixed turn texts in
this spec's design (the code carries the identical texts):

| Conv | Turns | Words | Last 4 turns (window) words |
| --- | --- | --- | --- |
| A | 18 | 140 | 27 |
| B | 18 | 139 | 27 |
| C | 18 | 139 | 27 |
| Total | 54 | 418 | 81 across the three windows |

Turn word counts in order: A: 10, 9, 5, 8, 5, 5, 8, 5, 15, 9, 8, 8,
13, 5, 5, 8, 6, 8 (sum 140). B: 9, 9, 5, 9, 5, 5, 8, 5, 15, 8, 8, 8,
13, 5, 5, 8, 6, 8 (sum 139). C: 9, 9, 5, 8, 5, 5, 8, 5, 15, 9, 8, 8,
13, 5, 5, 8, 6, 8 (sum 139).

## Hand-computed oracles (predicted before coding)

Stores, per conversation:

- Original tiered store: 6 entries each. A: name Maya Chen, home city
  Toronto, favorite color green (turn 14 overwrites blue at turn 5),
  project codename Aurora, pet name Biscuit (planted, not asked),
  next flight number AC847. B: name Jonas Reid, home city Berlin,
  favorite food sushi (turn 14 overwrites pasta at turn 5), team
  codename Beacon, dog name Rocky (planted, not asked), next train
  number ICE721. C: name Priya Nair, home city Mumbai, favorite color
  yellow (turn 14 overwrites red at turn 5), study codename Compass,
  cat name Miso (planted, not asked), next bus number B42.
- Extended store: 8 entries each, the 6 above plus the door, gate, or
  safe code and the backup email from the noncanonical_extended turns.
- No store holds the unhandled code (locker, alarm, or bike), because
  no extractor pattern matches the value-before-label form, and those
  turns (index 12) are outside the recent windows (turns 14 to 17).

Predicted outcomes by stratum:

| Stratum | Questions | Full | Tiered | Tiered extended |
| --- | --- | --- | --- | --- |
| canonical | 12 | 12 | 12 | 12 |
| update | 3 | 3 | 3 | 3 |
| noncanonical_extended | 6 | 6 | 0 | 6 |
| noncanonical_unhandled | 3 | 0 | 0 | 0 |
| Total | 24 | 21 | 15 | 21 |

- Predicted accuracy: full 21 of 24 = 0.875; tiered 15 of 24 = 0.625;
  extended 21 of 24 = 0.875.
- Full failure prediction: on the unhandled stratum the last matching
  turn contains the label, but the Learn extract_value finds no
  "happens to be" and no " is " value at the end, so full returns
  None. Full context is not immune to extractor limits.
- Predicted words: full per question is its conversation total (140
  for A questions, 139 for B and C), total 8 x 140 + 16 x 139 = 3344.
  Tiered per question: 27 window words on a miss, 31 on a store hit
  with a 4-word entry, 32 on a hit with a 5-word entry (the
  next flight, train, or bus entries). Tiered hits 15 questions
  (12 at 31 plus 3 transport at 32 = 468) and misses 9 at 27 (243),
  total 711, mean 29.625. Extended hits 21 questions (18 at 31 plus
  3 transport at 32): the 15 original hits contribute 468, the 6
  extended hits contribute 6 at 31 = 186, total hit words 654, and
  the 3 misses contribute 81, total 735, mean 30.625.
- Predicted scan counts: full 18 per question, 432 total; tiered and
  extended 5 per question, 120 total each.

## Acceptance

- tests/test_build_memory.py checks every oracle above by values
  computed from this spec: conversation shapes and word counts, store
  contents and sizes for both store designs, per-question answers,
  strata totals, accuracy, word totals and means, and scan totals.
- All Learn tests and the scaffold smoke test still pass unchanged.
- Running level-2-build/run_build.py twice produces
  level-2-build/results_build.json byte-identical.
- CI runs the Build tests and the Build runner determinism check in
  addition to the existing steps.
- The level README carries one A/B table (accuracy, latency proxy,
  cost word proxy) for full against tiered, with the extended design
  reported as a separate row and a separate effect note.
