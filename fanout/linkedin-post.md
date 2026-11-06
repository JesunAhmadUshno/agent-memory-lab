# LinkedIn post draft: P29 agent-memory-lab v1.0

Status: DRAFT NOT POSTED
Date drafted: 2026-11-05
Author: Jesun Ahmad Ushno
Rule for this platform: the link goes in the first comment, not in the
post body. The first comment line is at the end of this file.

## Post body

Agent memory is a trade-off you can measure, not a slogan. I
built the two designs, full context and tiered memory, and
measured where each one pays.

agent-memory-lab v1.0 is done: Learn, Build, and Deep, all open,
Python standard library only.

The scope, up front: all data is synthetic. Cost is a word-count
proxy, not real tokens. Latency is a counted proxy, not wall
time. The extractors are hand patterns; there is no semantic
retrieval.

Learn, one synthetic conversation, 8 questions: full context 8
of 8 reading 1432 words; tiered memory 7 of 8 reading 269 words.
The one miss was a fact phrased outside the form the extractor
was written for.

Build, three synthetic conversations, 24 questions in four
strata: full context 21 of 24 at 3344 words; tiered memory 15 of
24 at 711 words; tiered extended, with two added write-time
patterns, 21 of 24 at 735 words.

Deep computed the verdict from those numbers. Words per correct
answer: full 159.238, tiered 47.4, tiered extended 35.0. Tiered
pays on canonical plus update facts: 15 of 15 at 468 words
against 2090. It fails in its original form on the extended
non-canonical stratum: 0 of 6, which is the entire accuracy gap.
The extension recovers all 6 for 24 extra words. And on the
unhandled form, value before label, every design scores 0 of 3,
including full context: re-reading everything does not fix an
extraction failure.

Grades, house scale: Learn 8,500, Build 7,850, Deep 8,000 of
10,000. 428 checks in total, plus the smoke test. Semantic
extraction and real conversation data are v1.1 items, and they
are not claimed here.

Where has extraction coverage, not storage, decided accuracy in
a memory system you have run?

## First comment (post this as the first comment, per the standing rule)

Repo, releases v0.1, v0.5, and v1.0, and the full tutorial: https://github.com/JesunAhmadUshno/agent-memory-lab
