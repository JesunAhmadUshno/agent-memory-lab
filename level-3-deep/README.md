# Level 3, Deep: agent-memory-lab

Summary claim: Deep computed a verdict from the Build run on three synthetic conversations (54 turns, 418 words, 24 questions), with no new benchmark run and no real data: tiered memory pays on the canonical plus update strata (15 of 15 correct in both tiered designs at 468 words against 2090 words for full context) and does not pay in its original form on noncanonical_extended (0 of 6, the entire accuracy gap), tiered extended recovers all 6 of those questions for 24 extra words (4.0 words per recovered answer) matching full accuracy 21 of 24 at 735 words against 3344 for full (159.238095 words per correct for full, 47.4 for tiered, 35.0 for tiered extended), no design pays on noncanonical_unhandled (0 of 3 for full, tiered, and extended), tiered against full saves 2633 words and loses 6 answers for a break-even value of 438.833333 words per answer, and the scaling table in results_deep.json is a labelled projection from measured word counts under a fixed fact and question count assumption, not a measurement at scale, with 68 hand-computed Deep checks passing plus the 284 Build checks and the 76 Learn checks and the scaffold smoke test and results_deep.json byte-identical across two runs at sha256 aa6c04caad4c36a897641c26d998a1eefbce5473362b558eb57b3f7a3dd385fa.

## What Deep does

Learn sketched the trade-off and Build measured it at larger scale.
Deep runs no new benchmark. It imports the Build run, reads the Learn
totals for context, and computes the verdict the SPEC asks for: where
tiered memory pays, where it does not, with the run's numbers. The
hand-computed oracles and the verdict logic were written first, in
DEEP-SPEC.md. Learn and Build results files are not changed by this
level (their hashes still match their own levels).

Cost is still the Build word-count proxy and latency the counted
proxy. No real tokenizer tokens and no wall-clock time are claimed
anywhere in this level.

## Overall efficiency (measured inputs, derived here)

| Design | Accuracy | Correct | Words | Words per correct | Correct per 1000 words |
| --- | --- | --- | --- | --- | --- |
| Full context | 0.875 | 21 of 24 | 3344 | 159.238095 | 6.279904 |
| Tiered memory (Learn design) | 0.625 | 15 of 24 | 711 | 47.4 | 21.097046 |
| Tiered extended (Build change) | 0.875 | 21 of 24 | 735 | 35.0 | 28.571429 |

Savings against full context: tiered saves 2633 words (ratio
4.703235, fraction saved 0.787380) and loses 6 answers (accuracy
delta -0.25). Extended saves 2609 words (ratio 4.549660, fraction
saved 0.780203) and loses 0 answers.

## Per-stratum verdict

| Stratum | Q | Full words / correct | Tiered words / correct | Ext words / correct | Words per correct (full / tiered / ext) |
| --- | --- | --- | --- | --- | --- |
| canonical | 12 | 1672 / 12 | 375 / 12 | 375 / 12 | 139.333333 / 31.25 / 31.25 |
| update | 3 | 418 / 3 | 93 / 3 | 93 / 3 | 139.333333 / 31.0 / 31.0 |
| noncanonical_extended | 6 | 836 / 6 | 162 / 0 | 186 / 6 | 139.333333 / null / 31.0 |
| noncanonical_unhandled | 3 | 418 / 0 | 81 / 0 | 81 / 0 | null / null / null |

Words per correct is null where a design answers 0 correctly: it
spent words for no return, and no finite efficiency number is honest
there.

## Break-even and payoff

Let V be the value of one correct answer in words a caller would pay
to recover it (an analysis device, not a measured price).

- Tiered against full: saves 2633 words, loses 6 answers. Break-even
  V is 2633 / 6 = 438.833333 words per answer. Above that value the
  lost answers outweigh the saving on this accounting; below it the
  saving outweighs the loss. The accuracy loss can still rule tiered
  out for a use case regardless of V.
- Extended against tiered: costs 24 extra words, gains 6 answers.
  Cost per recovered answer is 24 / 6 = 4.0 words. The extension pays
  for any V above 4.0.
- Extended against full: saves 2609 words, loses 0 answers. On this
  set extended strictly dominates full. That dominance covers only
  the phrasing forms its extractors parse; it is not a general claim
  about real conversations.
- On canonical plus update alone, tiered and extended are identical:
  468 words and 15 of 15 each, against 2090 words for full. No
  extension is needed where the original extractor already covers
  the phrasing.

## Where tiered memory pays

- Facts stated in a form the write-time extractor covers and asked
  later (canonical stratum): 12 of 12 in both tiered designs at
  375 words against 1672 for full.
- Facts that change value (update stratum): 3 of 3 in all designs,
  the later value every time, at 93 tiered words against 418 for
  full. Overwrite at write time and last-match at read time both
  handle the single-value update case in this set.
- Longer transcripts, by projection only: the gap widens as the
  transcript grows and the store does not (see the projection table
  and its limits below).

## Where tiered memory does not pay

- Facts phrased outside the original extractor (noncanonical_extended
  stratum): the original tiered design answers 0 of 6. That stratum
  is the entire accuracy gap against full context (15 against 21).
  The saving is real and the answers are gone; on this accounting
  tiered pays only if a lost answer is worth less than 438.833333
  words.
- Facts in the value-before-label form (noncanonical_unhandled
  stratum): no design pays. Full, tiered, and extended all answer
  0 of 3. Re-reading everything does not help, because the failure is
  in extraction, not in storage or read cost.
- Any setting where extraction coverage cannot be checked in
  advance: this set shows the loss is silent (a miss returns None,
  not an error) and concentrated entirely in the uncovered forms.

## Scaling projection (projection, not measured)

Assumption: question count (24) and fact count stay fixed while the
transcript grows by the factor, as filler and history between the
same facts. Full re-reads everything per question, so its cost
scales with the factor. Tiered reads a fixed store entry plus the
fixed window, so its cost stays flat under this assumption.

| Factor | Full words (projected) | Tiered words | Ext words | Full scans (projected) | Tiered ratio (projected) |
| --- | --- | --- | --- | --- | --- |
| 1 | 3344 | 711 | 735 | 432 | 4.703235 |
| 5 | 16720 | 711 | 735 | 2160 | 23.516174 |
| 10 | 33440 | 711 | 735 | 4320 | 47.032349 |
| 50 | 167200 | 711 | 735 | 21600 | 235.161744 |
| 100 | 334400 | 711 | 735 | 43200 | 470.323488 |

Nothing above factor 1 was run. If facts grow with the transcript,
the store grows as well, tiered read cost rises, and these ratios
are upper bounds rather than predictions.

Learn context: the same trade-off appeared at the smaller scale
(full 179.0 words per correct, tiered 38.428571, ratio 5.32342).
Build is the verdict basis; Learn is not re-judged here.

## Failure modes

- Extraction is the bottleneck, not memory (observed across all
  levels): every accuracy difference in the run traces to which
  phrasing forms the write-time patterns cover. Storage size, window
  size, and read cost explain none of the misses.
- Pattern extension is whack-a-mole (observed): two added patterns
  recover exactly the two forms they were written for, at 4.0 words
  per recovered answer here. A new form needs a new pattern. Only
  semantic extraction changes that shape, and this project does not
  measure semantic extraction.
- Silent misses (observed): a tiered miss returns None with no
  signal that a fact existed but was not stored. A caller cannot
  tell a missing fact from an unasked one without a fallback read.
- Projection overreach (by construction): the scaling table assumes
  a fixed fact count. Real long conversations add facts as they
  grow, so the projected ratios flatter tiered memory. The table is
  a bound under a stated assumption, never a forecast.
- Break-even depends on V (by construction): the 438.833333 figure
  converts an accuracy loss into words. A use case where a wrong or
  missing answer is costly has a high V and should choose full
  context or a stronger extractor; the number does not make that
  choice for the caller.
- Single-value overwrite loses history (by design, from Build): the
  store keeps only the latest value. That is correct for the update
  questions here and wrong for any question about an earlier value,
  which this set does not ask.
- Window placement sensitivity (from Build): the recent window saved
  no missed fact in this set because every non-canonical fact sat
  outside it. Different placement would change tiered scores with no
  design change, so window luck is part of the measured gap.

## Grade

8,000 of 10,000 for this level, with named deductions summing to
2,000:

- Synthetic data only; no real conversation is measured at any
  level: minus 600.
- Small scale (54 turns, 24 questions); the scaling table is a
  projection, not a measurement at scale: minus 500.
- Extractors are hand-written patterns with no semantic retrieval;
  the verdict cannot judge semantic extraction: minus 350.
- Executed on the Muse VM, not the assigned BlackBoxV2 fleet node:
  minus 250.
- Cost and latency are proxies (word counts and operation counts),
  not real tokenizer tokens or measured wall time: minus 200.
- One fixed phrasing mix; the break-even value depends on the
  assumed value of a correct answer: minus 100.

Total deductions: 600 + 500 + 350 + 250 + 200 + 100 = 2,000.
Grade: 10,000 - 2,000 = 8,000.

## Run it

    python level-3-deep/run_deep.py
    python tests/test_deep_memory.py
    python tests/test_build_memory.py
    python tests/test_learn_memory.py
    python tests/test_smoke.py

results_deep.json is deterministic: two runs are byte-identical,
sha256 aa6c04caad4c36a897641c26d998a1eefbce5473362b558eb57b3f7a3dd385fa.
Assigned node for this project is BlackBoxV2; this Deep run executed
on the Muse VM, which is named as a grade deduction above, not
hidden.
