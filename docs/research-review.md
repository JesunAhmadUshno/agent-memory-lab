# Research review: agent-memory-lab

Reviewed 2026-11-07 against a doctoral-level research rubric. Each
criterion gets a grade (A to F), the evidence in this repo, what this
change fixed, and, for every gap still open, the exact compute or
data it needs. Nothing in this review is a new claim beyond the
committed results files.

Scale used: A (publishable as is), B (sound, minor gaps), C (useful
but a named weakness limits the claim), D (the claim does not follow
from the evidence), F (missing).

## Summary

| Criterion | Grade before | Grade after | Main open item |
| --- | --- | --- | --- |
| Research question | B | B | Question is about pattern extraction, not model memory |
| Hypotheses | C | B- | Hypotheses are implicit in DEEP-SPEC verdict flags |
| Method | C | C+ | Full context is a regex scan, not a model (construct validity) |
| Baselines | C | C | No long-context model baseline |
| Statistics and uncertainty | F | C | 24 hand-built questions; intervals describe a floor only |
| Reproducibility | A | A | None |
| Threats to validity | B | B+ | Overfitting and placement now measured, not only named |
| Related work | F | C | Positioning added below; no measured comparison |
| Limitations | B | B+ | Write-time cost now counted |

## 1. Research question

Evidence: SPEC.md and the level READMEs ask when a tiered store
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

## 2. Hypotheses

Evidence: level-3-deep/verdict.py encodes five verdict flags
(tiered pays on covered strata, fails on noncanonical_extended, the
extension recovers that stratum, no design pays on unhandled, updates
return later values). They act as falsifiable hypotheses, but they were
written alongside the results rather than registered before.

Fixed here: the held-out probe (level-2-build/ablations.py) tests one
implied hypothesis that was not stated, "the extension generalises to
other non-canonical phrasings". Result: it does not (0 of 6, against
5 of 6 for full context).

Open: pre-registration is a process step, not a compute cost. Any
future level should commit its hypotheses and their pass rules before
running.

## 3. Method

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

## 4. Baselines

Evidence: full context is the baseline for tiered; tiered is the
baseline for extended. Both are internal and pattern based.

Open: the standard external baselines are a long-context model given
the whole transcript and a retrieval baseline (embedding top-k turns).
Needs: the model run above, plus an embedding model (CPU is enough at
this size, but it adds a dependency the study has so far avoided).

## 5. Statistics and uncertainty

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

## 6. Reproducibility

Evidence: every runner is deterministic, results files are
byte-identical across runs (sha256 recorded in each level README),
CI reruns and diffs them on Python 3.11 and 3.12, and 428 hand-computed
checks pass.

Added here: run_ablations.py is deterministic and CI-diffed the same
way; tests/test_ablations.py adds 132 checks. The dashboard build
(site/src/memory.check.mjs) re-runs a JavaScript port of the designs
on the turn texts parsed from the Python sources and fails unless every
recorded answer, word count and operation count matches, including all
19 window sizes.

Open: none.

## 7. Threats to validity

Named in the level READMEs: synthetic data, small scale, hand-written
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

## 8. Related work

Before: NOVELTY.md is DRAFT with "NO MEASUREMENT YET"; DOSSIER.md
defers prior art.

Positioning added here (no measured comparison is claimed):

- MemGPT (Packer et al., 2023, arXiv:2310.08560) pages facts between
  a model's context and external storage under model control. This
  repo's tiered store is a fixed, rule-based version of the same
  split.
- Generative Agents (Park et al., 2023, arXiv:2304.03442) keep a
  memory stream and retrieve by recency, importance and relevance.
  This repo uses recency only (the window) plus an exact-key store.
- Lost in the Middle (Liu et al., 2023, arXiv:2307.03172) shows long-
  context models use facts in the middle of the input less reliably.
  That is the failure a real full-context baseline would show and the
  regex scan here cannot.
- LoCoMo (Maharana et al., 2024, arXiv:2402.17753) and LongMemEval
  (Wu et al., 2024, arXiv:2410.10813) are public long-term
  conversational memory benchmarks; either would replace the synthetic
  set.

Open: a measured comparison against any of these needs the model runs
named under Method and Baselines.

## 9. Limitations

Stated in the READMEs and on the dashboard: synthetic data, 54 turns
and 24 questions, pattern extractors, word and operation proxies, a
projection (not a measurement) for scaling, self-assigned grades. The
scaling projection assumes a fixed fact count, which favours tiered
memory; the repo labels it an upper bound.

Fixed here: write-time cost (above) and a plain glossary on the
dashboard. The level READMEs still use internal project terms for
where runs executed; they are kept as recorded history.

## What this change does not do

- No model, GPU or paid API is used, so the construct-validity gap
  and external baselines stay open, each with its compute named above.
- The recorded Learn, Build and Deep results files are unchanged
  (their sha256 hashes still match the level READMEs).
- The Pages source switch from main:/docs to GitHub Actions is a repo
  setting left for the owner.
