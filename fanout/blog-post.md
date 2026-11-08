# Tiered Memory Pays Only Where the Extractor Looks: A Measured Verdict

By Jesun Ahmad Ushno
Date: 2026-11-05
Status: DRAFT, written fan-out for P29 agent-memory-lab v1.0. Not posted.

## The problem

A long conversation does not fit cheaply into every prompt. One
design re-reads everything for each question. Another design pays
at write time: it extracts facts into a small store, keeps a short
recent window, and answers from the store plus the window. The
second design reads far less. The question is what it loses, and
where.

Repository: https://github.com/JesunAhmadUshno/agent-memory-lab

## Honest scope, stated first

All data in this project is synthetic, built in code: no real
conversation or real data is used or claimed at any level. Cost
is a word-count proxy: words actually read, counted as
len(text.split()). It is not a real tokenizer token count.
Latency is a counted proxy (turns scanned or operations counted);
no wall-clock time is measured. Extractors are hand-written
patterns; there is no semantic retrieval. The levels executed on
the Muse VM, not the assigned BlackBoxV2 fleet node; that is a
named limitation in REPORT.md, not hidden.

## What was built

Learn: both designs on one synthetic conversation (24 turns, 179
words, 8 questions). Full context 8 of 8 (accuracy 1.0, 1432
words); tiered memory 7 of 8 (accuracy 0.875, 269 words). The
single tiered miss was the door code, stated in a form the
write-time extractor does not match.

Build: the same A/B comparison at larger scale, plus one
separately measured design change. Three synthetic conversations
(54 turns, 418 words, 24 questions) in four named strata:
canonical (12), update (3), noncanonical_extended (6), and
noncanonical_unhandled (3).

Deep: no new benchmark run. A written verdict computed from the
Build numbers, with per-stratum analysis, break-even, and a
labelled scaling projection.

## The main result

On the Build A/B run over three synthetic conversations (54 turns, 418 words, 24 questions), full context answered 21 of 24 questions reading 3344 words, tiered memory answered 15 of 24 reading 711 words, and tiered extended answered 21 of 24 reading 735 words, with words per correct answer of 159.238 for full, 47.4 for tiered, and 35.0 for tiered extended.

In detail, by stratum: canonical 12 of 12 for all three designs;
update 3 of 3 for all three, the later value every time;
noncanonical_extended 6 of 6 for full, 0 of 6 for the original
tiered design, and 6 of 6 for tiered extended; and
noncanonical_unhandled 0 of 3 for all three designs, including
full context.

## The verdict

Tiered memory pays where its extractor covers the phrasing. On
canonical plus update it answers 15 of 15 at 468 words against
2090 for full context. It does not pay in its original form on
noncanonical_extended: that stratum is the entire accuracy gap
(15 against 21). Extending the extractor with two write-time
patterns recovers all 6 of those questions for 24 extra words in
total, 4.0 words per recovered answer, and on this measured set
tiered extended dominates full context: the same 21 of 24 at 735
words against 3344. That dominance covers only the phrasing forms
its extractors parse; it is not a general claim about real
conversations.

Tiered against full saves 2633 words and loses 6 answers, a
break-even value of 438.833333 words per answer: below that value
the saving outweighs the loss on this accounting, above it the
lost answers outweigh the saving, and a use case can still rule
tiered out on accuracy alone regardless of that number.

No design pays on noncanonical_unhandled (0 of 3 for all). The
facts there put the value before its label, a form no extractor
in this project parses. Re-reading everything does not help,
because the failure is in extraction, not in storage or read
cost.

The scaling table in the Deep README is a projection from
measured word counts under a fixed fact and question count
assumption, not a measurement at scale. If facts grow with the
transcript, the store grows too and the projected ratios are
upper bounds, not predictions.

## Limits

- Synthetic data only; no real conversation is measured.
- Small scale: 54 turns and 24 questions at Build.
- Hand patterns only; no semantic retrieval is measured.
- Cost and latency are proxies, not real tokens or wall time.
- A tiered miss is silent: it returns None, with no signal that
  a fact existed but was not stored.
- The store keeps only the latest value, so questions about an
  earlier value cannot be answered by design.

## Future

The v1.1 backlog is ROADMAP.md in the repo: semantic extraction,
value-before-label coverage, real conversations reported
separately from synthetic results, real token and wall-time
measurement, a scale run where fact counts grow, a history-aware
store, a fallback policy, and a window policy study. None of
that is claimed as done.

Tests: 428 checks in total (76 Learn, 284 Build, 68 Deep), plus
the scaffold smoke test.
