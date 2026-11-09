# REPORT: agent-memory-lab (P29)

Status: DRAFT, 2026-11-08. Results against the retrospective hypotheses
in PROPOSAL.md (not pre-registered). Folded in at the portfolio standard
v2 migration: the three level READMEs (Learn, Build, Deep), the
ablation results from the old README, docs/research-review.md and
docs/index.md. All data is synthetic and built in code. Cost is a
word-count proxy (words actually read, len(text.split())), not a real
tokenizer token count. Latency is a counted proxy (turns scanned or
operations counted); no wall-clock time is measured. Extractors are
hand-written patterns; there is no semantic retrieval.

## Summary

| Design | Accuracy (Wilson 95%) | Correct | Latency proxy (counted) | Cost proxy (words read) | Words per correct |
| --- | --- | --- | --- | --- | --- |
| Full context | 0.875 (0.69 to 0.96) | 21 of 24 | 432 turns scanned | 3344 | 159.238095 |
| Tiered memory (Learn design) | 0.625 (0.43 to 0.79) | 15 of 24 | 120 operations | 711 | 47.4 |
| Tiered extended (Build change) | 0.875 (0.69 to 0.96) | 21 of 24 | 120 operations | 735 | 35.0 |

Sources: results/results_build.json (counts, words, operations),
results/results_deep.json (words per correct), results/results_ablations.json
(paired_stats: Wilson intervals; exact McNemar: tiered against full 6
discordant questions, all lost, p = 0.03125; extended against full none,
p = 1.0). The 24 questions are hand-built, not sampled, so the intervals
are a floor on uncertainty, not a population estimate.

In one line: tiered pays on canonical plus update (15 of 15 at 468 words
against 2090 for full), does not pay in its original form on
noncanonical_extended (0 of 6), the extension recovers all 6 for 24
extra words (4.0 per recovered answer) but does not transfer to new
phrasings (0 of 6 held out), and no design pays on noncanonical_unhandled
(0 of 3 for all).

## Hypotheses scored

| ID | Pass line (PROPOSAL.md) | Result | Evidence | Outcome |
| --- | --- | --- | --- | --- |
| H1 | Covered strata: tiered correct = full correct, fewer words | 15 of 15 for tiered, extended and full; 468 words against 2090 | results_deep.json strata, covered_strata_canonical_plus_update | PASS |
| H2 | Tiered 0 of 6 on noncanonical_extended | 0 of 6 | results_build.json per stratum | PASS (the predicted loss happened) |
| H3 | Tiered extended 6 of 6 on noncanonical_extended | 6 of 6, for 24 extra words | results_build.json, results_deep.json breakeven | PASS |
| H4 | All designs 0 of 3 on noncanonical_unhandled | 0 of 3 for full, tiered and extended | results_build.json per stratum | PASS |
| H5 | All designs 3 of 3 on update | 3 of 3 for all | results_build.json per stratum | PASS |
| H6 | Extended beats tiered (0 of 6) on held-out phrasings | Extended 0 of 6; full context 5 of 6 | results_ablations.json heldout | MISS |

Caveat on H1 to H5: they were written alongside the results by the same
author who built the patterns and the data, so passing them shows the
code does what its design says, not that the claim generalises. H6, the
one hypothesis tested on phrasings written after the patterns, missed.

## Background

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
written first, in LEARN-SPEC.md (now experiments/2026-11-05-learn-design.md).

## Learn: one conversation (Baseline, 2026-11-05)

Summary claim: Learn built a standard-library agent memory sketch on one synthetic long conversation of 24 turns and 179 words, labelled synthetic everywhere with no real data used or claimed: full context answered 8 of 8 questions (accuracy 1.0) reading 179 words per question (1432 total), tiered memory (a canonical fact store of 7 entries plus a 4-turn recent window of 30 words) answered 7 of 8 (accuracy 0.875) reading 269 words total (mean 33.625 per question), the single tiered miss was Q4 the door code 4821 whose non-canonical phrasing the write-time extractor missed, both designs returned the updated favorite color green, with 76 hand-computed Learn checks passing plus the scaffold smoke test and results_learn.json byte-identical across two runs at sha256 e1dfa0e3f92bdcb1c6c5c3970b4fc4c271cccc05fc4dfa02a48ea516ec2c363e.

### The data (synthetic)

One synthetic conversation, 24 turns, 179 words, built in code in
src/memory.py. Facts are planted in early, middle, and late turns. Eight
labelled questions each need one fact. One fact is updated later in the
conversation (favorite color: blue at turn 5, green at turn 18, and
green is the expected answer). One fact is phrased non-canonically
(the door code at turn 11). No real conversation or real data is used.

### How each design answers

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

### Results (measured, from results_learn.json)

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

### Failure modes

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


## Build: the A/B run at larger scale (2026-11-05)

Summary claim: Build ran the A/B comparison at larger scale than Learn on three synthetic conversations (54 turns, 418 words, 24 questions in canonical, update, noncanonical_extended, and noncanonical_unhandled strata), labelled synthetic everywhere with no real data used or claimed: full context answered 21 of 24 questions (accuracy 0.875) reading 3344 words in total with 432 turns scanned, tiered memory (the unchanged Learn canonical store of 6 entries per conversation plus a 4-turn recent window of 27 words) answered 15 of 24 (accuracy 0.625) reading 711 words total (mean 29.625 per question) with 120 counted operations, the separately measured tiered extended design (two added write-time patterns, a Build design change) answered 21 of 24 (accuracy 0.875) reading 735 words total, all three designs scored 0 of 3 on the noncanonical_unhandled stratum and returned the updated values on all 3 update questions, with 284 hand-computed Build checks passing plus the 76 Learn checks and the scaffold smoke test and results_build.json byte-identical across two runs at sha256 799b925d11082c696c88f3ef3957b92574964179064a23b71f8beaaee62c49a9.

### The A/B run

Learn compared two designs on one synthetic conversation. Build runs
the same comparison, unchanged, on three synthetic conversations at
once, and adds one separately measured design change. The design and
the hand-computed oracles were written first, in BUILD-SPEC.md (now experiments/2026-11-05-build-design.md). The
Build code imports the Learn functions (answer_full, answer_tiered,
build_store) and runs them per conversation; Learn results are not
changed (results_learn.json still hashes to its Learn value).

The data (synthetic): three fixed synthetic conversations, 18 turns
each, 54 turns and 418 words in total, built in code in
src/memory_build.py. Each conversation asks 8 questions, 24 in total, in
four named strata: canonical (12), update (3, a fact stated twice and
the later value expected), noncanonical_extended (6, facts in the
"happens to be" form and the "For the record, my ... is ..." form),
and noncanonical_unhandled (3, the value before its label, a form no
extractor in this level parses). No real conversation or real data
is used.

Designs:

- Full context: scan all 18 turns of the question's conversation,
  extract from the last turn containing the key phrase.
- Tiered memory: the Learn design unchanged. A canonical fact store
  (6 entries per conversation) built at write time, plus the last
  4 turns (27 words) as a recent window at read time.
- Tiered extended (Build design change, reported separately): the
  store adds two write-time patterns, for the "happens to be" form
  and the "For the record" form, giving 8 entries per conversation.
  The read path is identical, so the difference against tiered is
  the isolated effect of extending the extractor.

Cost is a word-count proxy: words actually read, counted as
len(text.split()). It is not a real tokenizer token count. Latency
is a deterministic count proxy: turns scanned for full context,
counted operations (1 store lookup plus 4 window turns) for tiered.
No wall-clock time is measured.

### Results (measured, from results_build.json)

The one A/B table for this level:

| Design | Accuracy | Correct | Latency proxy (counted) | Cost proxy (words read) | Mean words per question |
| --- | --- | --- | --- | --- | --- |
| Full context | 0.875 | 21 of 24 | 432 turns scanned | 3344 | 139.333 |
| Tiered memory (Learn design) | 0.625 | 15 of 24 | 120 operations | 711 | 29.625 |
| Tiered extended (Build change) | 0.875 | 21 of 24 | 120 operations | 735 | 30.625 |

Mean words for full context: 3344 over 24 questions is 139.333 per
question (140 for conversation A, 139 for B and C).

By stratum:

| Stratum | Questions | Full | Tiered | Tiered extended |
| --- | --- | --- | --- | --- |
| canonical | 12 | 12 | 12 | 12 |
| update | 3 | 3 | 3 | 3 |
| noncanonical_extended | 6 | 6 | 0 | 6 |
| noncanonical_unhandled | 3 | 0 | 0 | 0 |

Reading the table: tiered reads about 4.7 times fewer words than
full context (711 against 3344) and loses 6 questions, all of them
in the noncanonical_extended stratum. Extending the write-time
extractor with two patterns recovers all 6 at a cost of 24 extra
words in total (735 against 711), matching full context accuracy at
about 4.5 times fewer words read. The unhandled stratum defeats all
three designs equally, including full context.

### Failure modes

- Extraction miss at scale (observed, tiered): every fact phrased
  outside the canonical form is lost to the original tiered store
  unless it sits in the recent window. At Learn scale this cost 1 of
  8 questions; at Build scale it costs 6 of 24. The miss rate is a
  property of the phrasing mix, not of the store.
- Extractor extension is pattern by pattern (observed): the two
  added patterns recover exactly the two forms they were written
  for. A third non-canonical form would need a third pattern. This
  is whack-a-mole unless extraction becomes semantic, which is Deep
  scope to judge, not Build scope to claim.
- Value before label (observed, all designs): on the
  noncanonical_unhandled stratum ("I set 8842 as my locker code"),
  even full context returns None, because the extractor looks for a
  value after " is " or "happens to be" at the end of the turn.
  Full context removes the storage problem, not the extraction
  problem. Any real system needs extraction that handles both
  orders, or a model in the loop.
- Update handling (observed, all designs): all 3 update questions
  return the later value in every design, by last-match in full
  context and by overwrite in both stores. No stale answer appears
  at this scale.
- Window edge (by design): the recent window holds the last 4 turns
  (27 words) of each conversation. Every non-canonical fact in this
  set was placed outside its window, so the window saved none of
  them. A window that happened to cover a missed fact would change
  the tiered score without any design change; placement is named in
  the Build design (experiments/2026-11-05-build-design.md) so the effect is not hidden.


## Deep: the verdict (2026-11-05)

Summary claim: Deep computed a verdict from the Build run on three synthetic conversations (54 turns, 418 words, 24 questions), with no new benchmark run and no real data: tiered memory pays on the canonical plus update strata (15 of 15 correct in both tiered designs at 468 words against 2090 words for full context) and does not pay in its original form on noncanonical_extended (0 of 6, the entire accuracy gap), tiered extended recovers all 6 of those questions for 24 extra words (4.0 words per recovered answer) matching full accuracy 21 of 24 at 735 words against 3344 for full (159.238095 words per correct for full, 47.4 for tiered, 35.0 for tiered extended), no design pays on noncanonical_unhandled (0 of 3 for full, tiered, and extended), tiered against full saves 2633 words and loses 6 answers for a break-even value of 438.833333 words per answer, and the scaling table in results/results_deep.json is a labelled projection from measured word counts under a fixed fact and question count assumption, not a measurement at scale, with 68 hand-computed Deep checks passing plus the 284 Build checks and the 76 Learn checks and the scaffold smoke test and results/results_deep.json byte-identical across two runs at sha256 aa6c04caad4c36a897641c26d998a1eefbce5473362b558eb57b3f7a3dd385fa.

### What Deep does

Learn sketched the trade-off and Build measured it at larger scale.
Deep runs no new benchmark. It imports the Build run, reads the Learn
totals for context, and computes the verdict the scope asks for: where
tiered memory pays, where it does not, with the run's numbers. The
hand-computed oracles and the verdict logic were written first, in
DEEP-SPEC.md (now experiments/2026-11-05-deep-design.md). Learn and Build results files are not changed by this
level (their hashes still match their own levels).

Cost is still the Build word-count proxy and latency the counted
proxy. No real tokenizer tokens and no wall-clock time are claimed
anywhere in this level.

### Overall efficiency (measured inputs, derived here)

| Design | Accuracy | Correct | Words | Words per correct | Correct per 1000 words |
| --- | --- | --- | --- | --- | --- |
| Full context | 0.875 | 21 of 24 | 3344 | 159.238095 | 6.279904 |
| Tiered memory (Learn design) | 0.625 | 15 of 24 | 711 | 47.4 | 21.097046 |
| Tiered extended (Build change) | 0.875 | 21 of 24 | 735 | 35.0 | 28.571429 |

Savings against full context: tiered saves 2633 words (ratio
4.703235, fraction saved 0.787380) and loses 6 answers (accuracy
delta -0.25). Extended saves 2609 words (ratio 4.549660, fraction
saved 0.780203) and loses 0 answers.

### Per-stratum verdict

| Stratum | Q | Full words / correct | Tiered words / correct | Ext words / correct | Words per correct (full / tiered / ext) |
| --- | --- | --- | --- | --- | --- |
| canonical | 12 | 1672 / 12 | 375 / 12 | 375 / 12 | 139.333333 / 31.25 / 31.25 |
| update | 3 | 418 / 3 | 93 / 3 | 93 / 3 | 139.333333 / 31.0 / 31.0 |
| noncanonical_extended | 6 | 836 / 6 | 162 / 0 | 186 / 6 | 139.333333 / null / 31.0 |
| noncanonical_unhandled | 3 | 418 / 0 | 81 / 0 | 81 / 0 | null / null / null |

Words per correct is null where a design answers 0 correctly: it
spent words for no return, and no finite efficiency number is honest
there.

### Break-even and payoff

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

### Where tiered memory pays

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

### Where tiered memory does not pay

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

### Scaling projection (projection, not measured)

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

### Failure modes

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


## Ablations (2026-11-07)

src/ablations.py (run: python src/run_ablations.py, tests: python
tests/test_ablations.py) adds four cheap checks to the Build run,
written to results/results_ablations.json:

- Window sweep, 0 to 18 turns. Window 4 reproduces the recorded
  15 of 24 at 711 words (tiered) and 21 of 24 at 735 words
  (extended). Tiered reaches 21 of 24 only at a 10-turn window,
  reading 2095 words.
- Write-time cost. Building the store reads each conversation once
  per extractor pass (418 words per pass). Read plus write: tiered
  1129 words, extended 1571 (two passes), full context 3344.
- Paired statistics. Wilson 95% intervals on accuracy (full and
  extended 0.69 to 0.96, tiered 0.43 to 0.79) and an exact McNemar
  test: tiered against full has 6 discordant questions, all lost,
  p = 0.03125. The questions are hand-built, not sampled.
- Held-out phrasing probe. Six new phrasings written after the
  extended patterns: full context 5 of 6, tiered 0 of 6, extended
  0 of 6. The extension does not generalise beyond its two forms.
  (On 2026-11-07 one held-out fact was changed from a credential-like
  value to a meeting-room fact; the counts are those of the committed
  file.)

## Research review (2026-11-07): method, threats and limits

Reviewed 2026-11-07 against a doctoral-level research checklist: the
evidence in this repo, what that change fixed, and, for every gap still
open, the exact compute or data it needs. Nothing in the review is a new
claim beyond the committed results files. Related work moved to
PROPOSAL.md, Prior work.

### Research question

Evidence: SPEC.md and the level READMEs (now PROPOSAL.md and this report) ask when a tiered store
(write-time fact extraction plus a recent window) answers recall
questions as well as re-reading the full transcript, and at what read
cost. The question is clear and answerable.

Weakness: as built, both designs use hand-written patterns, so the
question actually answered is "store of regex-extracted facts versus
regex scan of the transcript". That is narrower than the repo's
framing of tiered memory against full context.

Fixed here: the dashboard and this review state the narrower question
explicitly ("full context is a pattern scan, not a model").

Open: answering the broad question needs a model in both arms (see
Baselines).

### Hypotheses

Evidence: src/verdict.py encodes five verdict flags
(tiered pays on covered strata, fails on noncanonical_extended, the
extension recovers that stratum, no design pays on unhandled, updates
return later values). They act as falsifiable hypotheses, but they were
written alongside the results rather than registered before.

Fixed here: the held-out probe (src/ablations.py) tests one
implied hypothesis that was not stated, "the extension generalises to
other non-canonical phrasings". Result: it does not (0 of 6, against
5 of 6 for full context).

Open: pre-registration is a process step, not a compute cost. Any
future level should commit its hypotheses and their pass rules before
running.

### Method

Evidence: deterministic standard-library Python, fixed synthetic data,
word-count cost proxy and counted latency proxy, all disclosed in every
results file.

Weaknesses and fixes:

- Window size was fixed at 4. Fixed: a 0 to 18 turn sweep
  (results_ablations.json, window_sweep). Window 4 reproduces the
  recorded 15 of 24 at 711 words and 21 of 24 at 735 words; tiered
  reaches 21 of 24 only at window 10, reading 2095 words. The score is
  sensitive to where facts sit relative to the window.
- Only read-time words were counted. Fixed: write_time in
  results_ablations.json adds one-time store-build words (418 per
  extractor pass). Read plus write: tiered 1129, extended 1571 (two
  passes as coded, 1153 for a single pass), full context 3344. The
  read-only 4.5x saving becomes 2.1x to 3.0x once writes are counted.
- Construct validity (open): "full context" is a key-phrase regex,
  not a model reading the transcript. Needs: one long-context
  instruction model run over the 54 Build turns and 24 questions (and
  the 6 held-out), either a local open-weights model on one GPU for
  under an hour, or a paid API at roughly 24 calls of under 200 words
  each. Not run here because the change rules exclude GPU jobs and
  paid calls.
- Semantic extraction (open): the store side would need a model-based
  extractor at write time; same compute as above.

### Baselines

Evidence: full context is the baseline for tiered; tiered is the
baseline for extended. Both are internal and pattern based.

Open: the standard external baselines are a long-context model given
the whole transcript and a retrieval baseline (embedding top-k turns).
Needs: the model run above, plus an embedding model (CPU is enough at
this size, but it adds a dependency the study has so far avoided).

### Statistics and uncertainty

Before: no intervals or tests anywhere; the results were point counts.

Fixed here: results_ablations.json, paired_stats, reports Wilson 95%
intervals (full and extended 0.69 to 0.96, tiered 0.43 to 0.79) and an
exact two-sided McNemar test on paired questions. Tiered against full
has 6 discordant questions, all lost, p = 0.03125; extended against
full has none, p = 1.0. The 24 questions are hand-built rather than
sampled, so these numbers are a floor on uncertainty, not a population
estimate, and the dashboard says so.

Open: meaningful intervals need sampled data, for example a few
hundred questions drawn from LoCoMo or LongMemEval (public datasets,
no compute cost beyond CPU for the pattern designs). Not added here
because it changes the study's data, which is an owner decision.

### Reproducibility

Evidence: every runner is deterministic, results files are
byte-identical across runs (sha256 recorded in the Reproduction table below),
CI reruns and diffs them on Python 3.11 and 3.12, and 428 hand-computed
checks pass.

Added here: run_ablations.py is deterministic and CI-diffed the same
way; tests/test_ablations.py adds 132 checks. The dashboard build
(site/src/memory.check.mjs) re-runs a JavaScript port of the designs
on the turn texts parsed from the Python sources and fails unless every
recorded answer, word count and operation count matches, including all
19 window sizes.

Open: none.

### Threats to validity

Named in the level sections above: synthetic data, small scale, hand-written
extractors, proxies for cost and latency, window placement.

Fixed here: two threats moved from named to measured.

- Overfitting of the extension: its two patterns were written for the
  two phrasings in its own stratum. The held-out probe shows 0 of 6 on
  new phrasings. Caveat: the held-out phrasings were also written by
  hand, after the patterns and deliberately different from them, so
  this shows the patterns do not transfer; it does not estimate a rate.
- Window placement: measured by the sweep above.

Open: real dialogue (needs a public dataset, see Statistics) and
tokenizer-based cost (needs a tokenizer library; a CPU-only change).

### Limitations

Stated in the READMEs and on the dashboard: synthetic data, 54 turns
and 24 questions, pattern extractors, word and operation proxies, a
projection (not a measurement) for scaling. The
scaling projection assumes a fixed fact count, which favours tiered
memory; the repo labels it an upper bound.

Fixed here: write-time cost (above) and a plain glossary on the
dashboard. Where the runs executed is recorded once, below.


What the 2026-11-07 change did not do:

- No model, GPU or paid API is used, so the construct-validity gap
  and external baselines stay open, each with its compute named above.
- The recorded Learn, Build and Deep results files are unchanged
  (their sha256 hashes still match the Reproduction table).
- The Pages source switch from main:/docs to GitHub Actions is a repo
  setting left for the owner. (By 2026-11-08 Pages builds from the
  workflow; the dashboard is served from site/.)


## Where the runs executed

The assigned node for this project was BlackBoxV2. The Learn, Build and
Deep runs executed on the Muse VM instead. The runs are deterministic
standard-library Python, so the machine does not change any number;
the deviation from the plan is recorded here rather than hidden.

## Reproduction

Tests: 428 checks in the level suites (76 Learn, 284 Build, 68 Deep), plus 132 ablation checks and the layout check.

Every results file is byte-identical across runs and regenerates from
the code with `python src/make_results.py --check` (run in CI on Python
3.11 and 3.12):

| File | SHA-256 |
| --- | --- |
| results/results_learn.json | sha256 e1dfa0e3f92bdcb1c6c5c3970b4fc4c271cccc05fc4dfa02a48ea516ec2c363e |
| results/results_build.json | sha256 799b925d11082c696c88f3ef3957b92574964179064a23b71f8beaaee62c49a9 |
| results/results_ablations.json | sha256 3330df6b86abcd1068cc28151895a78fbfe0b0d8b1a5c8b1e889e29fc23f52e2 |
| results/results_deep.json | sha256 aa6c04caad4c36a897641c26d998a1eefbce5473362b558eb57b3f7a3dd385fa |

The dashboard build (site/src/memory.check.mjs) re-runs a JavaScript
port of the designs on the turn texts parsed from the Python sources
and fails unless every recorded answer, word count and operation count
matches, including all 19 window sizes.

## Conclusion

On this synthetic set, extraction coverage, not storage or read cost,
decides tiered memory's accuracy. Where the write-time patterns cover
the phrasing, tiered memory matches the full scan at about a fifth of
the words read; where they do not, the answers are lost silently, and
adding patterns fixes only the forms they were written for. The study
does not test a language model in either arm, real dialogue, or real
tokens and time; those are the next cycle in PROPOSAL.md and need Owner
decisions.
