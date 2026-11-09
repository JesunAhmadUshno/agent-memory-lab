# Changelog

All notable changes to this project. Format: Keep a Changelog 1.1.
Versions follow Semantic Versioning. The tags v0.1, v0.5 and v1.0 mark
the Learn, Build and Deep merges of the earlier ladder; they are kept as
history and are not a v1.0 release under the portfolio standard v2.

## [Unreleased]

### Changed
- 2026-11-08: Restructured to the portfolio standard v2. README is the
  abstract (verdict: Functional, not pre-registered). PROPOSAL.md (a
  retrospective draft, not locked) replaces SPEC.md, NOVELTY.md,
  DOSSIER.md and ROADMAP.md. REPORT.md replaces the three level READMEs,
  docs/research-review.md and docs/index.md, and scores six hypotheses
  (five pass, the held-out transfer test misses). Path moves:
  level-*/\*.py to src/; level-*/results_\*.json to results/ (byte
  identical); level-1-learn/LEARN-SPEC.md, level-2-build/BUILD-SPEC.md
  and level-3-deep/DEEP-SPEC.md to experiments/2026-11-05-{learn,build,deep}-design.md;
  PUBLICITY.md to docs/publicity.md. The drafts in fanout/ keep their
  original wording and old paths except the tutorial, whose commands now
  use the new paths.
- 2026-11-08: Internal grades removed from every public file (level
  READMEs, dossier, publicity log, fan-out drafts, research review).
  They are kept outside the repo.

### Added
- 2026-11-08: src/make_results.py regenerates all four results files and,
  with --check, fails if any differs; CI runs it on Python 3.11 and 3.12.
- 2026-11-08: tests/test_smoke.py is now the layout check: required
  files, no public grade, results regenerate, and a test that each of
  those checks fails when its target is wrong.
- 2026-11-08: docs/decisions/0001 (synthetic data and word proxies) and
  0002 (pattern extractors, no model); CHANGELOG.md, CITATION.cff,
  SECURITY.md; CodeQL for JavaScript (the dashboard) and Dependabot for
  npm.
- 2026-11-07: Vite upgraded to 6.4.5 (npm audit: no high or critical
  advisories).
- 2026-11-07: Ablations: window sweep 0 to 18, write-time cost,
  held-out phrasing probe, Wilson intervals and exact McNemar tests;
  research review; live dashboard in site/ with a Pages workflow.
- 2026-11-05: Fan-out drafts in fanout/ and the publicity log.
- 2026-11-05: Actions polish pack: CI matrix on Python 3.11 and 3.12
  with ruff, CodeQL, Dependabot, release, labeler, greetings, stale.
- 2026-11-05: Deep (tag v1.0): verdict, break-even and a labelled
  scaling projection computed from the Build numbers. The rest of the
  Deep scope became the backlog now in PROPOSAL.md, Next cycle.
- 2026-11-05: Build (tag v0.5): the A/B run on three synthetic
  conversations, 24 questions, four strata, plus tiered extended.
- 2026-11-05: Learn (tag v0.1): full context against tiered memory on
  one synthetic conversation.
- 2026-11-04: Scaffold: SPEC.md, DOSSIER.md, NOVELTY.md, level folders.
