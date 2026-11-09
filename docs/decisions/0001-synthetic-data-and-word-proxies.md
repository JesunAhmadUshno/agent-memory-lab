# 0001: Synthetic data built in code, word and operation counts as proxies

Date: 2026-11-05 (recorded 2026-11-08). Status: accepted. Decided by: Jesun Ahmad Ushno.

## Context

The study needed conversations with planted facts whose answers are
known exactly, and a cost and latency measure that is identical on
every machine. Real conversations raise consent and licence questions;
tokenizer counts and wall time add dependencies and run-to-run noise.

## Decision

All conversations are synthetic, fixed lists of turns in the Python
sources, labelled synthetic everywhere. Cost is words read
(len(text.split())); latency is turns scanned or operations counted. No
real conversation, tokenizer or clock is used.

## Consequences

Every number is exact and every results file regenerates byte for byte,
so CI can prove reproduction. The price is external validity: the
questions are hand-built (intervals are a floor, not a population
estimate) and the proxies are not real tokens or time. Real data,
sampled public benchmarks (LoCoMo, LongMemEval) and real token and time
measurement are next-cycle items in PROPOSAL.md; changing the data is an
Owner decision.
