"""Agent memory Learn sketch: full context against tiered memory.

Synthetic data only. One fixed synthetic long conversation (24 turns,
labelled synthetic) with planted facts, and 8 labelled questions.
Two deterministic designs, standard library only:

A) Full context: scan every turn, take the last turn containing the
   question key phrase, extract the value from that turn.
B) Tiered memory: extract canonical "My ... is ..." facts into a store
   at write time (later writes overwrite), then answer from the store
   plus a recent window of the last 4 turns.

Cost is a word-count proxy: len(text.split()) over the text actually
read. It is not a real tokenizer token count. No timing is measured.
"""

import re

# Synthetic conversation. The texts are fixed in LEARN-SPEC.md and the
# word counts there are hand-computed from these exact strings.
TURNS = [
    "Hi there, I want to chat for a while today.",
    "Hello, happy to talk through the day with you.",
    "My name is Maya Chen.",
    "Nice to meet you, glad you are here.",
    "My home city is Toronto.",
    "My favorite color is blue.",
    "That shade works well in a quiet room.",
    "My project codename is Aurora.",
    "Noted, that sounds bright and clear.",
    "We spent the morning sorting papers and making tea.",
    "A slow morning can help clear the mind.",
    "By the way, the door code, if you ever need it, happens to be 4821.",
    "Thanks, I will keep that note for the visit.",
    "My pet name is Biscuit.",
    "What a friendly companion to have around.",
    "We talked about rain, books, and long walks.",
    "My favorite food is ramen.",
    "That dish is warm and filling on cold days.",
    "My favorite color is green.",
    "I changed my mind after seeing the garden.",
    "The afternoon passed with music and quiet reading.",
    "My next flight number is AC847.",
    "That trip sounds like a good break soon.",
    "Thanks for listening through all of this today.",
]

RECENT_WINDOW = 4

QUESTIONS = [
    {"id": "Q1", "key_phrase": "my name is", "store_key": "name",
     "expected": "Maya Chen", "source_turn": 2, "bucket": "early"},
    {"id": "Q2", "key_phrase": "my home city is", "store_key": "home city",
     "expected": "Toronto", "source_turn": 4, "bucket": "early"},
    {"id": "Q3", "key_phrase": "my project codename is", "store_key": "project codename",
     "expected": "Aurora", "source_turn": 7, "bucket": "early"},
    {"id": "Q4", "key_phrase": "door code", "store_key": "door code",
     "expected": "4821", "source_turn": 11, "bucket": "middle"},
    {"id": "Q5", "key_phrase": "my pet name is", "store_key": "pet name",
     "expected": "Biscuit", "source_turn": 13, "bucket": "middle"},
    {"id": "Q6", "key_phrase": "my favorite color is", "store_key": "favorite color",
     "expected": "green", "source_turn": 18, "bucket": "late"},
    {"id": "Q7", "key_phrase": "my favorite food is", "store_key": "favorite food",
     "expected": "ramen", "source_turn": 16, "bucket": "late"},
    {"id": "Q8", "key_phrase": "my next flight number is", "store_key": "next flight number",
     "expected": "AC847", "source_turn": 21, "bucket": "late"},
]

_CANONICAL = re.compile(r"^My (.+?) is (.+?)\.$")
_HAPPENS = re.compile(r"happens to be (.+?)\.?$")
_IS = re.compile(r" is (.+?)\.?$")


def word_count(text):
    return len(text.split())


def transcript_words(turns=TURNS):
    return sum(word_count(t) for t in turns)


def recent_window(turns=TURNS, size=RECENT_WINDOW):
    return turns[len(turns) - size:]


def extract_value(turn_text):
    """Extract the fact value from one turn, or None."""
    m = _HAPPENS.search(turn_text)
    if m:
        return m.group(1)
    m = _IS.search(turn_text)
    if m:
        return m.group(1)
    return None


def build_store(turns=TURNS):
    """Tiered write path: canonical facts only, later writes overwrite."""
    store = {}
    for turn in turns:
        m = _CANONICAL.match(turn)
        if m:
            store[m.group(1)] = m.group(2)
    return store


def store_entry_text(key, value):
    return key + " is " + value


def answer_full(question, turns=TURNS):
    """Design A. Returns (answer, words_read, turns_scanned)."""
    words = transcript_words(turns)
    found = None
    for turn in turns:
        if question["key_phrase"] in turn.lower():
            found = turn
    if found is None:
        return None, words, len(turns)
    return extract_value(found), words, len(turns)


def answer_tiered(question, store=None, turns=TURNS):
    """Design B. Returns (answer, words_read, ops_count).

    Always reads the recent window. On a store hit, also reads the one
    store entry text. The fallback window scan uses the same extractor
    as full context, but only over the window turns.
    """
    if store is None:
        store = build_store(turns)
    window = recent_window(turns)
    words = sum(word_count(t) for t in window)
    ops = 1 + len(window)
    key = question["store_key"]
    if key in store:
        value = store[key]
        words += word_count(store_entry_text(key, value))
        return value, words, ops
    for turn in reversed(window):
        if question["key_phrase"] in turn.lower():
            return extract_value(turn), words, ops
    return None, words, ops


def run_all():
    store = build_store()
    rows = []
    for q in QUESTIONS:
        f_ans, f_words, f_ops = answer_full(q)
        t_ans, t_words, t_ops = answer_tiered(q, store=store)
        rows.append({
            "id": q["id"],
            "bucket": q["bucket"],
            "source_turn": q["source_turn"],
            "expected": q["expected"],
            "full_answer": f_ans,
            "full_correct": f_ans == q["expected"],
            "full_words_read": f_words,
            "full_turns_scanned": f_ops,
            "tiered_answer": t_ans,
            "tiered_correct": t_ans == q["expected"],
            "tiered_words_read": t_words,
            "tiered_ops_count": t_ops,
        })
    full_correct = sum(1 for r in rows if r["full_correct"])
    tiered_correct = sum(1 for r in rows if r["tiered_correct"])
    n = len(rows)
    return {
        "level": "learn",
        "data_label": "synthetic",
        "data_note": "One fixed synthetic conversation built in code. No real data.",
        "cost_proxy_note": "words_read is a word-count proxy computed as len(text.split()) over the text actually read. It is not a real tokenizer token count.",
        "turns": len(TURNS),
        "transcript_words": transcript_words(),
        "recent_window_turns": RECENT_WINDOW,
        "recent_window_words": sum(word_count(t) for t in recent_window()),
        "store_size": len(store),
        "store": store,
        "questions": n,
        "full_correct": full_correct,
        "full_accuracy": full_correct / n,
        "tiered_correct": tiered_correct,
        "tiered_accuracy": tiered_correct / n,
        "full_words_total": sum(r["full_words_read"] for r in rows),
        "tiered_words_total": sum(r["tiered_words_read"] for r in rows),
        "tiered_words_mean": sum(r["tiered_words_read"] for r in rows) / n,
        "full_turns_scanned_total": sum(r["full_turns_scanned"] for r in rows),
        "tiered_ops_total": sum(r["tiered_ops_count"] for r in rows),
        "per_question": rows,
    }
