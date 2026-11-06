# Level 2, Build: agent-memory-lab

Summary claim: Build ran the A/B comparison at larger scale than Learn on three synthetic conversations (54 turns, 418 words, 24 questions in canonical, update, noncanonical_extended, and noncanonical_unhandled strata), labelled synthetic everywhere with no real data used or claimed: full context answered 21 of 24 questions (accuracy 0.875) reading 3344 words in total with 432 turns scanned, tiered memory (the unchanged Learn canonical store of 6 entries per conversation plus a 4-turn recent window of 27 words) answered 15 of 24 (accuracy 0.625) reading 711 words total (mean 29.625 per question) with 120 counted operations, the separately measured tiered extended design (two added write-time patterns, a Build design change) answered 21 of 24 (accuracy 0.875) reading 735 words total, all three designs scored 0 of 3 on the noncanonical_unhandled stratum and returned the updated values on all 3 update questions, with 284 hand-computed Build checks passing plus the 76 Learn checks and the scaffold smoke test and results_build.json byte-identical across two runs at sha256 799b925d11082c696c88f3ef3957b92574964179064a23b71f8beaaee62c49a9.

## The A/B run

Learn compared two designs on one synthetic conversation. Build runs
the same comparison, unchanged, on three synthetic conversations at
once, and adds one separately measured design change. The design and
the hand-computed oracles were written first, in BUILD-SPEC.md. The
Build code imports the Learn functions (answer_full, answer_tiered,
build_store) and runs them per conversation; Learn results are not
changed (results_learn.json still hashes to its Learn value).

The data (synthetic): three fixed synthetic conversations, 18 turns
each, 54 turns and 418 words in total, built in code in
memory_build.py. Each conversation asks 8 questions, 24 in total, in
four named strata: canonical (12), update (3, a fact stated twice and
the later value expected), noncanonical_extended (6, facts in the
"happens to be" form and the "For the record, my ... is ..." form),
and noncanonical_unhandled (3, the value before its label, a form no
extractor in this level parses). No real conversation or real data
is used.

Designs:

- Full context: scan all 18 turns of the question's conversation,
  extract from the last turn containing the key phrase.
- Tiered memory: the Learn design unchanged. A canonical fact store
  (6 entries per conversation) built at write time, plus the last
  4 turns (27 words) as a recent window at read time.
- Tiered extended (Build design change, reported separately): the
  store adds two write-time patterns, for the "happens to be" form
  and the "For the record" form, giving 8 entries per conversation.
  The read path is identical, so the difference against tiered is
  the isolated effect of extending the extractor.

Cost is a word-count proxy: words actually read, counted as
len(text.split()). It is not a real tokenizer token count. Latency
is a deterministic count proxy: turns scanned for full context,
counted operations (1 store lookup plus 4 window turns) for tiered.
No wall-clock time is measured.

## Results (measured, from results_build.json)

The one A/B table for this level:

| Design | Accuracy | Correct | Latency proxy (counted) | Cost proxy (words read) | Mean words per question |
| --- | --- | --- | --- | --- | --- |
| Full context | 0.875 | 21 of 24 | 432 turns scanned | 3344 | 139.333 |
| Tiered memory (Learn design) | 0.625 | 15 of 24 | 120 operations | 711 | 29.625 |
| Tiered extended (Build change) | 0.875 | 21 of 24 | 120 operations | 735 | 30.625 |

Mean words for full context: 3344 over 24 questions is 139.333 per
question (140 for conversation A, 139 for B and C).

By stratum:

| Stratum | Questions | Full | Tiered | Tiered extended |
| --- | --- | --- | --- | --- |
| canonical | 12 | 12 | 12 | 12 |
| update | 3 | 3 | 3 | 3 |
| noncanonical_extended | 6 | 6 | 0 | 6 |
| noncanonical_unhandled | 3 | 0 | 0 | 0 |

Reading the table: tiered reads about 4.7 times fewer words than
full context (711 against 3344) and loses 6 questions, all of them
in the noncanonical_extended stratum. Extending the write-time
extractor with two patterns recovers all 6 at a cost of 24 extra
words in total (735 against 711), matching full context accuracy at
about 4.5 times fewer words read. The unhandled stratum defeats all
three designs equally, including full context.

## Failure modes

- Extraction miss at scale (observed, tiered): every fact phrased
  outside the canonical form is lost to the original tiered store
  unless it sits in the recent window. At Learn scale this cost 1 of
  8 questions; at Build scale it costs 6 of 24. The miss rate is a
  property of the phrasing mix, not of the store.
- Extractor extension is pattern by pattern (observed): the two
  added patterns recover exactly the two forms they were written
  for. A third non-canonical form would need a third pattern. This
  is whack-a-mole unless extraction becomes semantic, which is Deep
  scope to judge, not Build scope to claim.
- Value before label (observed, all designs): on the
  noncanonical_unhandled stratum ("I set 8842 as my locker code"),
  even full context returns None, because the extractor looks for a
  value after " is " or "happens to be" at the end of the turn.
  Full context removes the storage problem, not the extraction
  problem. Any real system needs extraction that handles both
  orders, or a model in the loop.
- Update handling (observed, all designs): all 3 update questions
  return the later value in every design, by last-match in full
  context and by overwrite in both stores. No stale answer appears
  at this scale.
- Window edge (by design): the recent window holds the last 4 turns
  (27 words) of each conversation. Every non-canonical fact in this
  set was placed outside its window, so the window saved none of
  them. A window that happened to cover a missed fact would change
  the tiered score without any design change; placement is named in
  BUILD-SPEC.md so the effect is not hidden.

## Grade

7,850 of 10,000 for this level, with named deductions:

- Executed on the Muse VM, not the assigned BlackBoxV2 fleet node:
  minus 250.
- Synthetic data only; no real conversation is measured: minus 600.
- Scale is larger than Learn but still small (54 turns, 24
  questions; real long conversations are far longer): minus 500.
- Extractors are hand-written patterns with no semantic retrieval;
  the extended design adds only two patterns: minus 450.
- Cost and latency are proxies (word counts and operation counts),
  not real tokenizer tokens or measured wall time: minus 350.

## Run it

    python level-2-build/run_build.py
    python tests/test_build_memory.py
    python tests/test_learn_memory.py
    python tests/test_smoke.py

results_build.json is deterministic: two runs are byte-identical,
sha256 799b925d11082c696c88f3ef3957b92574964179064a23b71f8beaaee62c49a9.
Assigned node for this project is BlackBoxV2; this Build run executed
on the Muse VM, which is named as a grade deduction above, not
hidden.
