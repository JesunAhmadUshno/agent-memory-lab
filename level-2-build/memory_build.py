"""Agent memory Build: the A/B run at larger scale than Learn.

Synthetic data only. Three fixed synthetic conversations (18 turns
each, 54 turns, 418 words, labelled synthetic), 24 labelled questions
in four named strata: canonical, update, noncanonical_extended, and
noncanonical_unhandled.

Designs, reusing the Learn code by import (level-1-learn/memory.py):
A) Full context: the Learn answer_full, per conversation.
B) Tiered memory: the Learn design unchanged (canonical store plus a
   4-turn recent window), answered by the Learn answer_tiered.
B-plus) Tiered extended, a Build design change measured separately:
   the store adds two write-time patterns for non-canonical forms;
   the read path is the same Learn answer_tiered.

Cost is a word-count proxy: len(text.split()) over the text actually
read. It is not a real tokenizer token count. The latency proxy is a
deterministic count of turns scanned or operations. No timing.
"""

import os
import re
import sys

_LEARN_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "level-1-learn")
sys.path.insert(0, _LEARN_DIR)

from memory import (  # noqa: E402
    answer_full,
    answer_tiered,
    build_store,
    word_count,
)

CONVERSATIONS = {
    "A": [
        "Hi there, I want to chat for a while today.",
        "Hello, happy to talk through the day with you.",
        "My name is Maya Chen.",
        "Nice to meet you, glad you are here.",
        "My home city is Toronto.",
        "My favorite color is blue.",
        "That shade works well in a quiet room.",
        "My project codename is Aurora.",
        "By the way, the door code, if you ever need it, happens to be 4821.",
        "Thanks, I will keep that note for the visit.",
        "For the record, my backup email is maya@example.com.",
        "Noted, I will use that address if needed.",
        "I set 8842 as my locker code, so I will not forget it.",
        "My pet name is Biscuit.",
        "My favorite color is green.",
        "I changed my mind after seeing the garden.",
        "My next flight number is AC847.",
        "Thanks for listening through all of this today.",
    ],
    "B": [
        "Good morning, I have a lot to share today.",
        "Morning, I am ready to listen and note things.",
        "My name is Jonas Reid.",
        "Good to meet you, please go on when ready.",
        "My home city is Berlin.",
        "My favorite food is pasta.",
        "That dish is filling and easy to share.",
        "My team codename is Beacon.",
        "By the way, the gate code, if you ever need it, happens to be 1934.",
        "Thanks, I will remember that for the gate.",
        "For the record, my backup email is jonas@example.com.",
        "Noted, I will use that address if needed.",
        "I set 5519 as my alarm code, so I will not forget it.",
        "My dog name is Rocky.",
        "My favorite food is sushi.",
        "I changed my mind after the market visit.",
        "My next train number is ICE721.",
        "Thanks for listening through all of this today.",
    ],
    "C": [
        "Hello there, I want to talk for a while.",
        "Hello, happy to talk through the day with you.",
        "My name is Priya Nair.",
        "Nice to meet you, glad you are here.",
        "My home city is Mumbai.",
        "My favorite color is red.",
        "That shade is bright and warm in summer.",
        "My study codename is Compass.",
        "By the way, the safe code, if you ever need it, happens to be 6607.",
        "Thanks, I will keep that note for the safe.",
        "For the record, my backup email is priya@example.com.",
        "Noted, I will use that address if needed.",
        "I set 2271 as my bike code, so I will not forget it.",
        "My cat name is Miso.",
        "My favorite color is yellow.",
        "I changed my mind after seeing the painting.",
        "My next bus number is B42.",
        "Thanks for listening through all of this today.",
    ],
}

# Each question: id, conversation, key_phrase, store_key, expected,
# source_turn (index inside its conversation), stratum.
QUESTIONS_BUILD = [
    {"id": "A1", "conversation": "A", "key_phrase": "my name is",
     "store_key": "name", "expected": "Maya Chen", "source_turn": 2,
     "stratum": "canonical"},
    {"id": "A2", "conversation": "A", "key_phrase": "my home city is",
     "store_key": "home city", "expected": "Toronto", "source_turn": 4,
     "stratum": "canonical"},
    {"id": "A3", "conversation": "A", "key_phrase": "my project codename is",
     "store_key": "project codename", "expected": "Aurora",
     "source_turn": 7, "stratum": "canonical"},
    {"id": "A4", "conversation": "A", "key_phrase": "door code",
     "store_key": "door code", "expected": "4821", "source_turn": 8,
     "stratum": "noncanonical_extended"},
    {"id": "A5", "conversation": "A", "key_phrase": "my backup email is",
     "store_key": "backup email", "expected": "maya@example.com",
     "source_turn": 10, "stratum": "noncanonical_extended"},
    {"id": "A6", "conversation": "A", "key_phrase": "locker code",
     "store_key": "locker code", "expected": "8842", "source_turn": 12,
     "stratum": "noncanonical_unhandled"},
    {"id": "A7", "conversation": "A", "key_phrase": "my next flight number is",
     "store_key": "next flight number", "expected": "AC847",
     "source_turn": 16, "stratum": "canonical"},
    {"id": "A8", "conversation": "A", "key_phrase": "my favorite color is",
     "store_key": "favorite color", "expected": "green",
     "source_turn": 14, "stratum": "update"},
    {"id": "B1", "conversation": "B", "key_phrase": "my name is",
     "store_key": "name", "expected": "Jonas Reid", "source_turn": 2,
     "stratum": "canonical"},
    {"id": "B2", "conversation": "B", "key_phrase": "my home city is",
     "store_key": "home city", "expected": "Berlin", "source_turn": 4,
     "stratum": "canonical"},
    {"id": "B3", "conversation": "B", "key_phrase": "my team codename is",
     "store_key": "team codename", "expected": "Beacon",
     "source_turn": 7, "stratum": "canonical"},
    {"id": "B4", "conversation": "B", "key_phrase": "gate code",
     "store_key": "gate code", "expected": "1934", "source_turn": 8,
     "stratum": "noncanonical_extended"},
    {"id": "B5", "conversation": "B", "key_phrase": "my backup email is",
     "store_key": "backup email", "expected": "jonas@example.com",
     "source_turn": 10, "stratum": "noncanonical_extended"},
    {"id": "B6", "conversation": "B", "key_phrase": "alarm code",
     "store_key": "alarm code", "expected": "5519", "source_turn": 12,
     "stratum": "noncanonical_unhandled"},
    {"id": "B7", "conversation": "B", "key_phrase": "my next train number is",
     "store_key": "next train number", "expected": "ICE721",
     "source_turn": 16, "stratum": "canonical"},
    {"id": "B8", "conversation": "B", "key_phrase": "my favorite food is",
     "store_key": "favorite food", "expected": "sushi",
     "source_turn": 14, "stratum": "update"},
    {"id": "C1", "conversation": "C", "key_phrase": "my name is",
     "store_key": "name", "expected": "Priya Nair", "source_turn": 2,
     "stratum": "canonical"},
    {"id": "C2", "conversation": "C", "key_phrase": "my home city is",
     "store_key": "home city", "expected": "Mumbai", "source_turn": 4,
     "stratum": "canonical"},
    {"id": "C3", "conversation": "C", "key_phrase": "my study codename is",
     "store_key": "study codename", "expected": "Compass",
     "source_turn": 7, "stratum": "canonical"},
    {"id": "C4", "conversation": "C", "key_phrase": "safe code",
     "store_key": "safe code", "expected": "6607", "source_turn": 8,
     "stratum": "noncanonical_extended"},
    {"id": "C5", "conversation": "C", "key_phrase": "my backup email is",
     "store_key": "backup email", "expected": "priya@example.com",
     "source_turn": 10, "stratum": "noncanonical_extended"},
    {"id": "C6", "conversation": "C", "key_phrase": "bike code",
     "store_key": "bike code", "expected": "2271", "source_turn": 12,
     "stratum": "noncanonical_unhandled"},
    {"id": "C7", "conversation": "C", "key_phrase": "my next bus number is",
     "store_key": "next bus number", "expected": "B42",
     "source_turn": 16, "stratum": "canonical"},
    {"id": "C8", "conversation": "C", "key_phrase": "my favorite color is",
     "store_key": "favorite color", "expected": "yellow",
     "source_turn": 14, "stratum": "update"},
]

_EXTENDED_PATTERNS = [
    re.compile(r"^By the way, the (.+?), if you ever need it, "
               r"happens to be (.+?)\.$"),
    re.compile(r"^For the record, my (.+?) is (.+?)\.$"),
]


def build_store_extended(turns):
    """Build design change: Learn canonical store plus two patterns.

    The added patterns run in turn order over the same turns. Keys from
    the added patterns do not collide with canonical keys in this data
    set, so no canonical entry is overwritten by an added pattern.
    """
    store = build_store(turns)
    for turn in turns:
        for pattern in _EXTENDED_PATTERNS:
            m = pattern.match(turn)
            if m:
                store[m.group(1)] = m.group(2)
    return store


def conversation_words(turns):
    return sum(word_count(t) for t in turns)


def run_all():
    stores = {}
    stores_extended = {}
    conv_summary = {}
    for cid, turns in CONVERSATIONS.items():
        stores[cid] = build_store(turns)
        stores_extended[cid] = build_store_extended(turns)
        window = turns[len(turns) - 4:]
        conv_summary[cid] = {
            "turns": len(turns),
            "words": conversation_words(turns),
            "recent_window_turns": len(window),
            "recent_window_words": sum(word_count(t) for t in window),
            "store_size": len(stores[cid]),
            "store": stores[cid],
            "extended_store_size": len(stores_extended[cid]),
            "extended_store": stores_extended[cid],
        }
    rows = []
    for q in QUESTIONS_BUILD:
        turns = CONVERSATIONS[q["conversation"]]
        f_ans, f_words, f_ops = answer_full(q, turns=turns)
        t_ans, t_words, t_ops = answer_tiered(
            q, store=stores[q["conversation"]], turns=turns)
        e_ans, e_words, e_ops = answer_tiered(
            q, store=stores_extended[q["conversation"]], turns=turns)
        rows.append({
            "id": q["id"],
            "conversation": q["conversation"],
            "stratum": q["stratum"],
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
            "extended_answer": e_ans,
            "extended_correct": e_ans == q["expected"],
            "extended_words_read": e_words,
            "extended_ops_count": e_ops,
        })
    n = len(rows)
    full_correct = sum(1 for r in rows if r["full_correct"])
    tiered_correct = sum(1 for r in rows if r["tiered_correct"])
    ext_correct = sum(1 for r in rows if r["extended_correct"])
    strata = {}
    for name in ("canonical", "update", "noncanonical_extended",
                 "noncanonical_unhandled"):
        srows = [r for r in rows if r["stratum"] == name]
        strata[name] = {
            "questions": len(srows),
            "full_correct": sum(1 for r in srows if r["full_correct"]),
            "tiered_correct": sum(1 for r in srows if r["tiered_correct"]),
            "extended_correct": sum(
                1 for r in srows if r["extended_correct"]),
        }
    return {
        "level": "build",
        "data_label": "synthetic",
        "data_note": "Three fixed synthetic conversations built in "
                     "code. No real data.",
        "cost_proxy_note": "words_read is a word-count proxy computed "
                           "as len(text.split()) over the text "
                           "actually read. It is not a real tokenizer "
                           "token count.",
        "conversations": len(CONVERSATIONS),
        "turns_total": sum(len(t) for t in CONVERSATIONS.values()),
        "words_total": sum(
            conversation_words(t) for t in CONVERSATIONS.values()),
        "per_conversation": conv_summary,
        "questions": n,
        "strata": strata,
        "full_correct": full_correct,
        "full_accuracy": full_correct / n,
        "tiered_correct": tiered_correct,
        "tiered_accuracy": tiered_correct / n,
        "extended_correct": ext_correct,
        "extended_accuracy": ext_correct / n,
        "full_words_total": sum(r["full_words_read"] for r in rows),
        "tiered_words_total": sum(r["tiered_words_read"] for r in rows),
        "tiered_words_mean": sum(
            r["tiered_words_read"] for r in rows) / n,
        "extended_words_total": sum(
            r["extended_words_read"] for r in rows),
        "extended_words_mean": sum(
            r["extended_words_read"] for r in rows) / n,
        "full_turns_scanned_total": sum(
            r["full_turns_scanned"] for r in rows),
        "tiered_ops_total": sum(r["tiered_ops_count"] for r in rows),
        "extended_ops_total": sum(r["extended_ops_count"] for r in rows),
        "per_question": rows,
    }
