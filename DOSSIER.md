# DOSSIER: agent-memory-lab (P29)

Written under the documentation and publishing standard (past, present, future). Updated at ship time.
Version: v2, 2026-11-05 (Build ship). v1 was the 2026-11-04 scaffold.

## Past

Prior art for this project is named in NOVELTY.md (memory frameworks (MemGPT and Letta class systems)). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in SPEC.md and will be expanded with dated sources at the project's wave, before Build opens.

## Present

Current demand evidence: hiring value scored in the fleet pass (new candidates P23 to P29: see the decision pack Sections 4 and 5) [confirmed, fleet and scoring pass 2026-11-04; for P23 to P29, the decision pack 2026-11-04]. The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.

Learn (done, 2026-11-05): a standard-library memory sketch on one
synthetic conversation (24 turns, 179 words, 8 questions). Full
context 8 of 8 reading 1432 words; tiered memory (canonical store of
7 entries plus a 4-turn window) 7 of 8 reading 269 words. The single
tiered miss was the non-canonical door code. See
level-1-learn/README.md.

Build (done, 2026-11-05): the A/B run at larger scale, reusing the
Learn functions by import. Three synthetic conversations (54 turns,
418 words, 24 questions in canonical, update, noncanonical_extended,
and noncanonical_unhandled strata), labelled synthetic, no real data.
Measured: full context 21 of 24 (accuracy 0.875, 3344 words, 432
turns scanned); tiered memory with the unchanged Learn design 15 of
24 (accuracy 0.625, 711 words, 120 counted operations); tiered
extended, a Build design change adding two write-time patterns and
measured separately, 21 of 24 (accuracy 0.875, 735 words). All
designs scored 0 of 3 on the value-before-label unhandled stratum
and 3 of 3 on updates. Cost is a word-count proxy, not real tokens;
latency is a counted proxy, not wall time. Grade 7,850 of 10,000
with named deductions in level-2-build/README.md (largest: synthetic
data only, minus 600). This Build run executed on the Muse VM, not
the assigned BlackBoxV2 node; that is a named grade deduction, not
hidden.

## Future

Deep is still open: a short written verdict on where tiered memory
pays and where it does not, with the Build numbers, per SPEC.md.
Known open problems from the Build run: extraction that handles
value-before-label phrasing, semantic extraction instead of hand
patterns, and measurement on real long conversations with a real
tokenizer and wall-time method. Any forecast about this field is
[unverified] unless a dated primary source is added here.
