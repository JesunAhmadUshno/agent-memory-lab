# LEARN-SPEC: agent-memory-lab, Level 1 Learn

Written before any code, 2026-11-05. Scope from SPEC.md: a memory layer
sketch: full context against tiered memory on a small long-conversation set.

## Design

- Standard library only, deterministic, no timing fields anywhere.
- One synthetic long conversation, labelled synthetic everywhere. It is
  built in code as a fixed list of 24 turns (index 0 to 23). No real
  conversation, no downloaded data, no person is represented.
- Planted facts sit in early, middle, and late turns. Eight labelled
  questions at the end each need one planted fact.
- Design A, full context: for a question, scan every turn, keep the LAST
  turn containing the question key phrase (case-insensitive substring),
  and extract the value from that turn. Extraction tries, in order:
  "happens to be (.+)" then " is (.+)".
- Design B, tiered memory: at write time, extract facts from turns that
  match the canonical pattern ^My (.+?) is (.+?)\.$ into a store dict
  keyed by the captured key; a later turn with the same key overwrites
  the earlier value. At read time, look the question store key up in
  the store, and also scan the recent window (the last 4 turns) for the
  key phrase as a fallback. If neither holds the fact, answer None.
- The tiered extractor is deliberately a simple sketch: it only sees the
  canonical "My ... is ..." form. That limitation is part of the lesson
  and is predicted below to cost exactly one question.

## Cost proxy (labelled honestly)

- Words read per question is a word-count proxy, computed in code as
  len(text.split()) over the text actually read. It is NOT a real
  tokenizer token count and is never called tokens in results.
- Full context words per question: the words of all 24 turns.
- Tiered words per question: words of the recent window (last 4 turns)
  plus, on a store hit, the words of the store entry text
  "key is value". On a miss, only the recent window words.
- Latency proxy: counts only. Full scans 24 turns per question. Tiered
  does 1 store lookup plus a scan of 4 window turns, counted as 5.
  No wall-clock time is measured or claimed.

## The conversation and hand counts

Turn word counts, counted by hand word by word from the turn texts
fixed in this spec (the code carries the identical texts):

| Turn | Text | Words |
| --- | --- | --- |
| 0 | Hi there, I want to chat for a while today. | 10 |
| 1 | Hello, happy to talk through the day with you. | 9 |
| 2 | My name is Maya Chen. | 5 |
| 3 | Nice to meet you, glad you are here. | 8 |
| 4 | My home city is Toronto. | 5 |
| 5 | My favorite color is blue. | 5 |
| 6 | That shade works well in a quiet room. | 8 |
| 7 | My project codename is Aurora. | 5 |
| 8 | Noted, that sounds bright and clear. | 6 |
| 9 | We spent the morning sorting papers and making tea. | 9 |
| 10 | A slow morning can help clear the mind. | 8 |
| 11 | By the way, the door code, if you ever need it, happens to be 4821. | 15 |
| 12 | Thanks, I will keep that note for the visit. | 9 |
| 13 | My pet name is Biscuit. | 5 |
| 14 | What a friendly companion to have around. | 7 |
| 15 | We talked about rain, books, and long walks. | 8 |
| 16 | My favorite food is ramen. | 5 |
| 17 | That dish is warm and filling on cold days. | 9 |
| 18 | My favorite color is green. | 5 |
| 19 | I changed my mind after seeing the garden. | 8 |
| 20 | The afternoon passed with music and quiet reading. | 8 |
| 21 | My next flight number is AC847. | 6 |
| 22 | That trip sounds like a good break soon. | 8 |
| 23 | Thanks for listening through all of this today. | 8 |

Hand total: 10+9+5+8+5+5+8+5+6+9+8+15+9+5+7+8+5+9+5+8+8+6+8+8 = 179
words for the whole transcript.
Recent window (turns 20 to 23): 8+6+8+8 = 30 words.

## Hand-computed oracles (predicted before coding)

Tiered store after all 24 turns, in write order with overwrites applied:

- name = Maya Chen
- home city = Toronto
- favorite color = green (turn 18 overwrites blue from turn 5)
- project codename = Aurora
- pet name = Biscuit
- favorite food = ramen
- next flight number = AC847

Store size: 7 entries. The door code fact (turn 11) is NOT in the store,
because its sentence does not match the canonical pattern.

Store entry texts and word counts: "name is Maya Chen" 4,
"home city is Toronto" 4, "project codename is Aurora" 4,
"pet name is Biscuit" 4, "favorite color is green" 4,
"favorite food is ramen" 4, "next flight number is AC847" 5.

Questions, expected answers, and predicted outcomes:

| ID | Key phrase | Store key | Turn | Bucket | Expected | Full | Tiered |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | my name is | name | 2 | early | Maya Chen | correct | correct |
| Q2 | my home city is | home city | 4 | early | Toronto | correct | correct |
| Q3 | my project codename is | project codename | 7 | early | Aurora | correct | correct |
| Q4 | door code | door code | 11 | middle | 4821 | correct | WRONG (miss) |
| Q5 | my pet name is | pet name | 13 | middle | Biscuit | correct | correct |
| Q6 | my favorite color is | favorite color | 18 | late | green | correct | correct |
| Q7 | my favorite food is | favorite food | 16 | late | ramen | correct | correct |
| Q8 | my next flight number is | next flight number | 21 | late | AC847 | correct | correct |

- Q4 prediction: full context finds turn 11 and extracts 4821 through
  the "happens to be" pattern. Tiered has no store entry and turn 11 is
  outside the recent window (turns 20 to 23), so tiered returns None.
- Q6 prediction: both designs return the LAST value, green. Full takes
  the last matching turn; tiered takes the overwritten store value.
- Predicted accuracy: full 8 of 8 = 1.0; tiered 7 of 8 = 0.875.
- Predicted words: full 179 per question, 1432 over 8 questions.
  Tiered per question: Q1 34, Q2 34, Q3 34, Q4 30, Q5 34, Q6 34,
  Q7 34, Q8 35; total 269, mean 33.625.
- Predicted scan counts: full 24 turns per question (192 total);
  tiered 5 per question (40 total).

## Acceptance

- tests/test_learn_memory.py checks every oracle above by hand-computed
  values: store contents and size, extraction, the Q4 miss, the Q6
  update, per-question answers, accuracy counts, and word counts.
- Running level-1-learn/run_learn.py twice produces
  level-1-learn/results_learn.json byte-identical (no timing fields).
- The scaffold smoke test still passes and CI runs both test files
  plus the runner.
