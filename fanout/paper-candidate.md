# Paper candidate brief: a verdict note on where tiered agent memory pays

Project: P29 agent-memory-lab
Status: CANDIDATE, brief dated 2026-11-05
Submission note: submission is Jesun's tap. Nothing is submitted by
this brief, and no venue has been contacted.

## Working title

Extraction coverage decides tiered memory: a measured verdict
on full context against tiered memory over synthetic long
conversations

## Candidate claim, in one line

On a measured A/B run over three synthetic conversations (54
turns, 24 questions in four named strata), tiered memory matches
full context where its write-time extractor covers the phrasing
and loses exactly the questions whose phrasing it does not cover,
and a two-pattern extractor extension recovers all of those
questions at 4.0 words per recovered answer, reaching 35.0 words
per correct answer against 159.238 for full context; the claim
is this measured result on synthetic data with word-count cost
proxies, not a claim about real conversations or semantic
retrieval.

## Scope, stated first

All data is synthetic, built in code; no real conversation is
measured at any level. Cost is a word-count proxy (words actually
read), not a real tokenizer token count. Latency is a counted
proxy (turns scanned or operations counted); no wall-clock time
is measured. Extractors are hand-written patterns; no semantic
retrieval is measured, so the verdict cannot judge semantic
extraction. The scaling table in the Deep level is a labelled
projection under a fixed fact and question count assumption,
not a measurement at scale, and it is not a result of this
candidate. Prior art is named in NOVELTY.md (MemGPT and Letta
class memory frameworks); the novelty statement there is still
PROPOSED and Jev-gated, and this brief claims the measured
verdict and its failure-mode analysis, not a novelty claim
beyond that gate.

## Abstract draft

Based only on the measured v1.0 results recorded in the repo.
Scope limits are stated inside the abstract, not after it.

Tiered agent memory trades read cost for extraction risk, but
the terms of that trade are usually asserted rather than
measured per phrasing type. This candidate reports a three level
open study on synthetic data only. Learn compares full context
and tiered memory on one synthetic conversation (24 turns, 8
questions): full 8 of 8 at 1432 words read, tiered 7 of 8 at 269
words, the single tiered miss a fact phrased non-canonically.
Build runs the A/B comparison on three synthetic conversations
(54 turns, 418 words, 24 questions) stratified as canonical
(12), update (3), noncanonical_extended (6), and
noncanonical_unhandled (3): full context 21 of 24 (accuracy
0.875) at 3344 words, tiered memory 15 of 24 (0.625) at 711
words, and a separately measured tiered extended design, adding
two write-time patterns, 21 of 24 (0.875) at 735 words. Deep
computes the verdict with no new run: words per correct answer
159.238 for full, 47.4 for tiered, and 35.0 for tiered extended;
tiered pays on canonical plus update (15 of 15 at 468 words
against 2090), does not pay in its original form on
noncanonical_extended (0 of 6, the entire accuracy gap), the
extension recovers all 6 for 24 extra words (4.0 per recovered
answer), and no design pays on noncanonical_unhandled (0 of 3
for all, including full context). Cost throughout is a
word-count proxy and latency a counted proxy; extractors are
hand patterns with no semantic retrieval. The candidate claims
the per-stratum verdict method and its measured result on this
synthetic set, nothing about real conversations.

## Method outline

1. Learn sketch. One fixed synthetic conversation, hand-computed
   oracles written first in LEARN-SPEC.md, both designs run on
   the same questions.
2. Build A/B run. Three fixed synthetic conversations, four
   named strata, oracles in BUILD-SPEC.md; the tiered extended
   design measured separately so the extension effect is
   isolated (same read path, two added write-time patterns).
3. Deep verdict. No new run: per-stratum words per correct,
   break-even (tiered against full saves 2633 words and loses 6
   answers, break-even 438.833333 words per answer), and a
   labelled scaling projection, with oracles in DEEP-SPEC.md.
4. Determinism. Every results file is byte-identical across two
   runs; hashes are recorded in the level READMEs and checked in
   CI on Python 3.11 and 3.12.

## Results table for the candidate

| Design | Accuracy | Correct | Words | Words per correct |
| --- | --- | --- | --- | --- |
| Full context | 0.875 | 21 of 24 | 3344 | 159.238 |
| Tiered memory | 0.625 | 15 of 24 | 711 | 47.4 |
| Tiered extended | 0.875 | 21 of 24 | 735 | 35.0 |

## Limits a reviewer will raise, named in advance

- Synthetic data only; real conversations may phrase facts in
  forms this set never plants.
- Small scale (54 turns, 24 questions); the scaling projection
  assumes a fixed fact count and flatters tiered memory.
- Hand patterns only; the verdict says nothing about semantic
  extraction, which is v1.1 item 1 in ROADMAP.md.
- Proxies, not tokens or wall time; a real tokenizer and a
  timed method are v1.1 item 4.
- One phrasing mix; the break-even figure depends on the
  assumed value of a correct answer.

## What would strengthen it before submission

Run v1.1 items 1, 3, and 4 (semantic extraction, real
conversations reported separately, real token and wall-time
measurement) and re-run the same stratified A/B design, so the
verdict can be stated for semantic extraction and real data
instead of hand patterns and synthetic data alone.
