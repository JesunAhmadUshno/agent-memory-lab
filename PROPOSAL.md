# PROPOSAL: agent-memory-lab (P29)

Status: DRAFT, retrospective, NOT LOCKED. Written 2026-11-08 at the
portfolio standard v2 migration from SPEC.md, NOVELTY.md, DOSSIER.md,
ROADMAP.md and the three level designs, which it replaces.

**Not pre-registered.** The only plan committed before any code was the
2026-11-04 scaffold SPEC.md (commit 869f286). It names scope and
acceptance criteria but no hypotheses or pass lines. Each level design
(experiments/2026-11-05-*-design.md) says it was "written before any
code", and its hand-computed oracles did predict the results, but each
was committed in the same commit as that level's code and results
(1785039, 454796e, 5848049), so git cannot prove the order. No tag is
placed after the fact. The hypotheses below are a reconstruction of what
the study tested, written down so REPORT.md can score each one.

## Question

When does a tiered memory (facts extracted into a small store at write
time, plus a recent window) answer recall questions about a long
conversation as well as re-reading the whole transcript, and at what
read cost?

As built, both arms use hand-written patterns, so the question actually
answered is narrower: a store of pattern-extracted facts against a
pattern scan of the full transcript (decision 0002).

## Original scope (SPEC.md, 2026-11-04, kept verbatim)

Phase skill: spec-driven-development (house engineering pipeline).
Status: Wave 0 scaffold spec, from Roadmap v2 text and the v3 decision
pack. Fleet node: BlackBoxV2. Wave: Waves 6 to 7.

Subject: agent memory and long-context systems, light scope (Round 3
research rank 7).
- Learn: a memory layer sketch: full context against tiered memory on a
  small long-conversation set.
- Build: the A/B run: accuracy, latency, and cost for both designs, one
  table.
- Deep: a short written verdict: where tiered memory pays, where it does
  not, with the run's numbers.

Acceptance criteria (scaffold level):
- Learn closes when the level-1-learn code runs, its README teaches the
  idea, and a fresh-eyes reader can follow it.
- Build closes when the system runs end to end, tests pass, and one
  benchmark or result table with method is in the README.
- Deep closes when the Deep scope in the section text is done, the
  failure modes are written, and the dossier is updated to ship state.
- No level closes on a claim. Evidence only: code, tests, numbers, links.

## Prior work

- MemGPT (Packer et al., 2023, arXiv:2310.08560) pages facts between a
  model's context and external storage under model control. The tiered
  store here is a fixed, rule-based version of the same split. Letta is
  the framework that grew from it.
- Generative Agents (Park et al., 2023, arXiv:2304.03442) keep a memory
  stream and retrieve by recency, importance and relevance. This repo
  uses recency only (the window) plus an exact-key store.
- Lost in the Middle (Liu et al., 2023, arXiv:2307.03172): long-context
  models use facts in the middle of the input less reliably. A real
  full-context baseline would show that failure; the pattern scan here
  cannot.
- LoCoMo (Maharana et al., 2024, arXiv:2402.17753) and LongMemEval (Wu et
  al., 2024, arXiv:2410.10813): public long-term conversational memory
  benchmarks; either would replace the synthetic set.

Novelty (from NOVELTY.md, status DRAFT, PROPOSED, not verified): against
MemGPT and Letta class systems the project aimed to differ as a
from-zero build, measured in public, with the failure modes written
down. No measured difference against any prior system exists. Honest
size: the value is a small, fully reproducible teaching benchmark of the
extraction trade-off, not a new memory method. The novelty text does not
move into any public post until the Jev claim_check gate passes on it.

Context from DOSSIER.md: hiring value was scored in the 2026-11-04 fleet
pass (decision pack sections 4 and 5); the Round 3 research
(2026-11-04) found the market centre at post-training, evals,
environments and inference depth. Any forecast about this field is
unverified unless a dated primary source is added.

## Hypotheses and pass lines (retrospective)

Data: 3 synthetic conversations, 54 turns, 24 questions in four strata:
canonical (12), update (3), noncanonical_extended (6),
noncanonical_unhandled (3). Covered strata means canonical plus update.

| ID | Hypothesis | Pass line |
| --- | --- | --- |
| H1 | Tiered memory pays where its extractor covers the phrasing | On covered strata, tiered correct = full correct, and tiered reads fewer words |
| H2 | Tiered memory loses facts phrased outside its extractor | Tiered answers 0 of 6 on noncanonical_extended (outside the window) |
| H3 | Two write-time patterns recover that stratum | Tiered extended answers 6 of 6 on noncanonical_extended |
| H4 | Value-before-label phrasing defeats every design, full context included | All three designs answer 0 of 3 on noncanonical_unhandled |
| H5 | Updates return the later value | All designs answer 3 of 3 on the update stratum |
| H6 | The extension transfers to new non-canonical phrasings (added 2026-11-07 as the held-out probe) | Tiered extended answers more of the 6 held-out questions than tiered (0) |

H1 to H5 are the five verdict flags in src/verdict.py. H6 was implied
by the extension but never stated; it was tested after the fact.

## Design

- Standard library only, deterministic, no timing fields; every results
  file regenerates byte for byte (src/make_results.py).
- Full context: scan every turn of the conversation, take the last turn
  containing the question's key phrase, extract the value with the
  "happens to be" pattern, then " is ".
- Tiered memory: at write time, turns matching `^My (.+?) is (.+?)\.$`
  enter a store (later writes overwrite); at read time, look up the key
  and scan the last 4 turns as a fallback.
- Tiered extended: the same, plus patterns for the "happens to be" and
  "For the record, my ... is ..." forms.
- Cost: words read, len(text.split()). Latency: turns scanned or
  operations counted. Neither is a real token count or a wall time
  (decision 0001).
- Analysis: per-stratum counts, words per correct answer, break-even
  value per answer, a labelled scaling projection (not measured),
  Wilson 95% intervals and exact McNemar tests on paired questions,
  a 0 to 18 turn window sweep, write-time cost.

## Next cycle (from ROADMAP.md v1.1 backlog; not done, not claimed)

A confirmatory cycle would lock a new PROPOSAL.md (tag proposal-v1)
before any run. Candidate items, in the backlog's order:

1. Semantic extraction: replace or augment the hand-written write-time
   patterns with embedding or model-based extraction and re-run the A/B
   table. The noncanonical strata are where any gain must appear.
2. Value-before-label and general phrasing coverage without
   form-specific patterns (0 of 3 for every design today).
3. Real conversations, with consent and a recorded licence basis,
   reported separately from the synthetic results, never mixed.
4. Real cost and latency: a tokenizer token count and a wall-time method
   with repeats, replacing the proxies.
5. Scale run: conversations far longer than 54 turns, with fact counts
   that grow with the transcript, to test the projection where its
   fixed-fact assumption breaks.
6. History-aware store: keep prior values with timestamps and measure
   the read-cost effect against single-value overwrite.
7. Fallback policy: fall back to a full read on a store miss; measure
   accuracy recovered and how much of the saving it gives back.
8. Window policy study: vary window size and placement separately from
   extractor coverage, so window luck is no longer folded into the
   tiered score.

What the ML field profile adds before Evaluated is possible: a
long-context model baseline over the same 54 turns and 24 questions (a
local open-weights model on one GPU for under an hour, or about 24 paid
API calls of under 200 words each), a retrieval baseline (embedding
top-k turns, CPU is enough), and sampled questions (a few hundred from
LoCoMo or LongMemEval). Each needs GPU time, a paid call or a change of
data, so each is an Owner decision.

Rules carried over: each item closes on evidence only; synthetic and real
results are always reported in separate tables; any public claim goes
through the Jev claim_check gate first.
