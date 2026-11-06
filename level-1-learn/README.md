# Level 1, Learn: agent-memory-lab

Summary claim: Learn built a standard-library agent memory sketch on one synthetic long conversation of 24 turns and 179 words, labelled synthetic everywhere with no real data used or claimed: full context answered 8 of 8 questions (accuracy 1.0) reading 179 words per question (1432 total), tiered memory (a canonical fact store of 7 entries plus a 4-turn recent window of 30 words) answered 7 of 8 (accuracy 0.875) reading 269 words total (mean 33.625 per question), the single tiered miss was Q4 the door code 4821 whose non-canonical phrasing the write-time extractor missed, both designs returned the updated favorite color green, with 76 hand-computed Learn checks passing plus the scaffold smoke test and results_learn.json byte-identical across two runs at sha256 e1dfa0e3f92bdcb1c6c5c3970b4fc4c271cccc05fc4dfa02a48ea516ec2c363e.

## The idea

A long conversation does not fit cheaply into every prompt. Two designs
answer questions about it:

- Full context keeps nothing and re-reads everything. It is simple and
  hard to fool, but the read cost grows with the whole transcript.
- Tiered memory pays at write time instead: it extracts facts into a
  small store as turns arrive, keeps only the last few turns as a
  recent window, and answers from the store plus the window. The read
  is tiny, but the answer can only be as good as the extraction.

This level builds both on the same fixed synthetic conversation and
measures the trade-off. The design and the hand-computed oracles were
written first, in LEARN-SPEC.md.

## The data (synthetic)

One synthetic conversation, 24 turns, 179 words, built in code in
memory.py. Facts are planted in early, middle, and late turns. Eight
labelled questions each need one fact. One fact is updated later in the
conversation (favorite color: blue at turn 5, green at turn 18, and
green is the expected answer). One fact is phrased non-canonically
(the door code at turn 11). No real conversation or real data is used.

## How each design answers

- Full context (answer_full): scan all 24 turns, take the LAST turn
  containing the question key phrase, extract the value with the
  "happens to be" pattern first, then the " is " pattern.
- Tiered memory (build_store, answer_tiered): at write time, turns
  matching ^My (.+?) is (.+?)\.$ enter a store dict, later writes
  overwriting earlier ones. At read time, look up the store key and
  scan the recent window (last 4 turns, 30 words) as a fallback.

Cost is a word-count proxy: words actually read, counted as
len(text.split()). It is not a real tokenizer token count. The scan
counts are a deterministic latency proxy (turns or lookups counted);
no wall-clock time is measured.

## Results (measured, from results_learn.json)

| ID | Bucket | Turn | Expected | Full answer | Full words | Tiered answer | Tiered words |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | early | 2 | Maya Chen | Maya Chen | 179 | Maya Chen | 34 |
| Q2 | early | 4 | Toronto | Toronto | 179 | Toronto | 34 |
| Q3 | early | 7 | Aurora | Aurora | 179 | Aurora | 34 |
| Q4 | middle | 11 | 4821 | 4821 | 179 | None (miss) | 30 |
| Q5 | middle | 13 | Biscuit | Biscuit | 179 | Biscuit | 34 |
| Q6 | late | 18 | green | green | 179 | green | 34 |
| Q7 | late | 16 | ramen | ramen | 179 | ramen | 34 |
| Q8 | late | 21 | AC847 | AC847 | 179 | AC847 | 35 |

Totals: full context 8 of 8 correct, accuracy 1.0, 1432 words read,
192 turns scanned. Tiered memory 7 of 8 correct, accuracy 0.875,
269 words read (mean 33.625 per question), 40 counted operations
(1 store lookup plus 4 window turns per question). On this set tiered
reads about 5.3 times fewer words and loses one question.

## Failure modes

- Extraction miss (observed, Q4): the door code is stated as "happens
  to be 4821", which the canonical write-time extractor does not match.
  The fact never enters the store, turn 11 is outside the recent
  window, and tiered returns None. Full context finds it because it
  re-reads everything. This is the central trade-off of tiered memory:
  read savings are bought with extraction risk.
- Update handling (observed, Q6): both designs return green, but by
  different mechanisms. Full context relies on taking the last match;
  a first-match variant would answer the stale blue. Tiered relies on
  overwrite at write time; a store that keeps first writes would be
  stale the same way.
- Window edge: a fact stated recently but non-canonically can still be
  saved by the recent window fallback. A fact that is both
  non-canonical and old has no fallback in this sketch. That is Q4.
- Key phrase brittleness: full context here searches for an exact key
  phrase. A question phrased without that phrase would miss in both
  designs. Real systems need semantic retrieval, which is Build scope.
- Scale limit: 24 turns is a teaching set. The word gap widens with
  transcript length, but so does extraction-miss exposure. Nothing
  here measures either effect at real scale.

## Run it

    python level-1-learn/run_learn.py
    python tests/test_learn_memory.py
    python tests/test_smoke.py

results_learn.json is deterministic: two runs are byte-identical,
sha256 e1dfa0e3f92bdcb1c6c5c3970b4fc4c271cccc05fc4dfa02a48ea516ec2c363e.
Assigned node for this project is BlackBoxV2; this Learn run executed
on the Muse VM, which is named as a grade deduction in the batch
ledger, not hidden.
