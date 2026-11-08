# 0002: Hand-written pattern extractors in both arms, no language model

Date: 2026-11-05 (recorded 2026-11-08). Status: accepted. Decided by: Jesun Ahmad Ushno.

## Context

"Full context against tiered memory" usually means a language model
reading the whole transcript against a model reading a memory store.
Running a model needs a GPU job or paid API calls, which the light
scope and the change rules excluded.

## Decision

Both arms use standard-library regular expressions. Full context scans
every turn for the question's key phrase and extracts the value from the
last match; tiered memory extracts "My X is V." facts at write time and
answers from the store plus a 4-turn window.

## Consequences

The question actually answered is narrower than the framing: a store of
pattern-extracted facts against a pattern scan of the transcript (the
research review's construct-validity gap). The study cannot show the
failures a real model has (for example, facts lost in the middle of a
long input). A model baseline (one GPU for under an hour, or about 24
paid calls) is the first item the ML field profile needs and is an
Owner decision.
