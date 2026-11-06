# ROADMAP: agent-memory-lab (P29), v1.1 backlog

v1.0 shipped 2026-11-05: Learn, Build, and compressed Deep are done.
Compressed Deep delivered the single hardest capability in the SPEC:
the written verdict on where tiered memory pays and where it does
not, computed from the Build numbers with break-even and per-stratum
analysis and a labelled scaling projection.

The rest of the v2 Deep scope is this v1.1 backlog. Nothing here is
done, measured, or claimed at v1.0.

## v1.1 backlog

1. Semantic extraction: replace or augment the hand-written
   write-time patterns with embedding or model-based extraction, and
   re-run the A/B table. The Build and Deep results predict the
   noncanonical strata are where any gain must appear.
2. Value-before-label and general phrasing coverage: extraction that
   handles the noncanonical_unhandled form (0 of 3 for every design
   at v1.0) without form-specific patterns.
3. Real conversations: run the same A/B design on real long
   conversations with consent and a recorded licence basis, reported
   separately from the synthetic results, never mixed into them.
4. Real cost and latency: a real tokenizer token count and a
   wall-time method with repeats, replacing the word-count and
   counted-operation proxies.
5. Scale run: conversations far longer than 54 turns, with fact
   counts that grow with the transcript, to test the Deep scaling
   projection where its fixed-fact assumption breaks.
6. History-aware store: keep prior values with timestamps so
   questions about earlier values can be answered, and measure the
   read-cost effect against the single-value overwrite store.
7. Fallback policy: a tiered design that falls back to a full read
   on a store miss, measured for accuracy recovery and for how much
   of the word saving the fallback gives back.
8. Window policy study: vary the recent window size and placement
   rules and measure the effect separately from extractor coverage,
   so window luck is no longer folded into the tiered score.

## Rules for v1.1 work

- Each item closes on evidence only: code, tests, measured numbers.
- Synthetic and real results are always reported in separate tables.
- Any public claim goes through the Jev claim_check gate first.
