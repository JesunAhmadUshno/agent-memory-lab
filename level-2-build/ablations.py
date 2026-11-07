"""Build ablations: window size, write-time cost, and a held-out phrasing probe.

Three cheap, deterministic additions over the Build run, standard
library only. No design is changed; each one varies or adds a single
thing and reuses the Learn and Build functions by import.

1) Window sweep. The recent window is fixed at 4 turns in Learn and
   Build. Here it varies from 0 to 18 turns over the 24 Build
   questions, for tiered and tiered extended. Window 4 must reproduce
   the recorded 15 of 24 at 711 words and 21 of 24 at 735 words.
2) Write-time accounting. The Build cost proxy counts only words read
   at question time. Building a store also reads every turn once.
   This adds that one-time write cost: each conversation's words per
   extractor pass, using the passes the code makes (one canonical
   pass for tiered, a canonical pass plus a pattern pass for extended).
3) Paired statistics. Wilson 95% intervals on each design's accuracy
   and an exact two-sided McNemar (sign) test on the discordant
   question pairs. The questions are hand-built, not sampled, so these
   describe sampling noise under an assumption the data does not meet;
   they are reported to show how little 24 questions can resolve.
4) Held-out phrasing probe. One new synthetic conversation with six
   facts in phrasings that neither the canonical form nor the two
   extended patterns were written for. The phrasings were written
   after the extended patterns, to differ from them; they are a probe
   of whether the patterns generalise, not a random sample of
   phrasings, so the result is not a rate.

Cost is the same word-count proxy as Build: len(text.split()).
"""
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "level-1-learn"))

from memory import answer_full, build_store, extract_value, store_entry_text, word_count  # noqa: E402
from memory_build import CONVERSATIONS, QUESTIONS_BUILD, build_store_extended, conversation_words, run_all  # noqa: E402

WINDOW_SIZES = tuple(range(0, 19))

HELDOUT_CONVERSATION = [
    "Hi again, I have a few more things to note today.",
    "Of course, go ahead whenever you are ready.",
    "My name is Sam Ortiz.",
    "Just so you know, my gym code is 7710.",
    "Got it, I will remember that one.",
    "Remember that the wifi password is tulip88.",
    "That is an easy one to keep in mind.",
    "The parking spot, in case it matters, turns out to be P14.",
    "Thanks, that helps with the visit.",
    "Oh, and my sister's name is Lena.",
    "That is a lovely name.",
    "By the way, the mailbox number happens to be 31.",
    "Noted, I will check it later.",
    "For the record, the storage unit is 12B.",
    "We spent the afternoon cleaning the garage.",
    "A tidy garage makes the week easier.",
    "Thanks for listening through all of this today.",
    "Talk to you again soon.",
]

HELDOUT_QUESTIONS = [
    {"id": "H1", "key_phrase": "my gym code is", "store_key": "gym code",
     "expected": "7710", "source_turn": 3, "form": "lead-in before My"},
    {"id": "H2", "key_phrase": "wifi password", "store_key": "wifi password",
     "expected": "tulip88", "source_turn": 5, "form": "Remember that the X is V"},
    {"id": "H3", "key_phrase": "parking spot", "store_key": "parking spot",
     "expected": "P14", "source_turn": 7, "form": "turns out to be"},
    {"id": "H4", "key_phrase": "my sister's name is", "store_key": "sister's name",
     "expected": "Lena", "source_turn": 9, "form": "lead-in before my"},
    {"id": "H5", "key_phrase": "mailbox number", "store_key": "mailbox number",
     "expected": "31", "source_turn": 11, "form": "By the way without the aside"},
    {"id": "H6", "key_phrase": "storage unit", "store_key": "storage unit",
     "expected": "12B", "source_turn": 13, "form": "For the record, the X is V"},
]


def answer_tiered_window(question, store, turns, size):
    """The Learn answer_tiered with the recent window size as a parameter.

    Same read path: read the window, read the one store entry on a hit,
    otherwise scan the window newest first with the shared extractor.
    At size 4 it equals memory.answer_tiered (checked in the tests).
    """
    window = turns[len(turns) - size:] if size else []
    words = sum(word_count(t) for t in window)
    ops = 1 + len(window)
    key = question["store_key"]
    if key in store:
        value = store[key]
        return value, words + word_count(store_entry_text(key, value)), ops
    for turn in reversed(window):
        if question["key_phrase"] in turn.lower():
            return extract_value(turn), words, ops
    return None, words, ops


def window_sweep():
    stores = {c: build_store(t) for c, t in CONVERSATIONS.items()}
    ext = {c: build_store_extended(t) for c, t in CONVERSATIONS.items()}
    rows = []
    for size in WINDOW_SIZES:
        row = {"window": size}
        for name, st in (("tiered", stores), ("extended", ext)):
            correct = words = ops = 0
            for q in QUESTIONS_BUILD:
                a, w, o = answer_tiered_window(q, st[q["conversation"]], CONVERSATIONS[q["conversation"]], size)
                correct += a == q["expected"]
                words += w
                ops += o
            row[name + "_correct"] = correct
            row[name + "_words"] = words
            row[name + "_ops"] = ops
        rows.append(row)
    return rows


def write_time(build_results):
    """One-time store-build words added to the recorded read words."""
    per_conv = {c: conversation_words(t) for c, t in CONVERSATIONS.items()}
    one_pass = sum(per_conv.values())
    passes = {"tiered": 1, "extended": 2}
    out = {"per_conversation_words": per_conv, "one_pass_words": one_pass, "designs": {}}
    full_read = build_results["full_words_total"]
    out["designs"]["full"] = {"read_words": full_read, "write_words": 0, "total_words": full_read,
                              "correct": build_results["full_correct"]}
    for name, n in passes.items():
        read = build_results[name + "_words_total"]
        write = one_pass * n
        out["designs"][name] = {
            "read_words": read,
            "extractor_passes": n,
            "write_words": write,
            "total_words": read + write,
            "total_words_one_pass": read + one_pass,
            "ratio_full_vs_total": round(full_read / (read + write), 6),
            "correct": build_results[name + "_correct"],
        }
    return out


def heldout():
    turns = HELDOUT_CONVERSATION
    store = build_store(turns)
    ext = build_store_extended(turns)
    rows = []
    for q in HELDOUT_QUESTIONS:
        f = answer_full(q, turns=turns)
        t = answer_tiered_window(q, store, turns, 4)
        e = answer_tiered_window(q, ext, turns, 4)
        rows.append({
            "id": q["id"], "form": q["form"], "expected": q["expected"],
            "full_answer": f[0], "full_correct": f[0] == q["expected"], "full_words_read": f[1],
            "tiered_answer": t[0], "tiered_correct": t[0] == q["expected"], "tiered_words_read": t[1],
            "extended_answer": e[0], "extended_correct": e[0] == q["expected"], "extended_words_read": e[1],
        })
    return {
        "turns": len(turns),
        "words": conversation_words(turns),
        "questions": len(rows),
        "store": store,
        "extended_store": ext,
        "full_correct": sum(r["full_correct"] for r in rows),
        "tiered_correct": sum(r["tiered_correct"] for r in rows),
        "extended_correct": sum(r["extended_correct"] for r in rows),
        "per_question": rows,
    }


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 6), round(c + h, 6)]


def mcnemar_exact(b, c):
    """Exact two-sided McNemar p-value from discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return round(min(1.0, 2 * tail), 6)


def paired_stats(build_results):
    rows = build_results["per_question"]
    n = len(rows)
    out = {"questions": n, "accuracy_wilson95": {}, "mcnemar": {}}
    for k in ("full", "tiered", "extended"):
        out["accuracy_wilson95"][k] = wilson(build_results[k + "_correct"], n)
    for a, b in (("full", "tiered"), ("full", "extended"), ("extended", "tiered")):
        only_a = sum(1 for r in rows if r[a + "_correct"] and not r[b + "_correct"])
        only_b = sum(1 for r in rows if r[b + "_correct"] and not r[a + "_correct"])
        out["mcnemar"][a + "_vs_" + b] = {"only_" + a: only_a, "only_" + b: only_b,
                                          "p_exact_two_sided": mcnemar_exact(only_a, only_b)}
    return out


def run_ablations():
    b = run_all()
    return {
        "level": "build-ablations",
        "data_label": "synthetic",
        "cost_proxy_note": "words are the Build word-count proxy, len(text.split()) over the text read. "
                           "Not a real tokenizer token count.",
        "window_note": "Window sweep over the 24 Build questions. Window 4 is the recorded Build setting.",
        "write_time_note": "Derived from recorded counts: read words from the Build run plus one-time "
                           "store-build words (each conversation's words once per extractor pass).",
        "heldout_note": "Six phrasings written after the extended patterns, to differ from them. A probe of "
                        "generalisation, not a random sample, so the counts are not a rate.",
        "stats_note": "Wilson 95% intervals and exact McNemar tests treat the 24 hand-built questions as if "
                      "sampled. They are not, so read these as a floor on uncertainty, not a population claim.",
        "paired_stats": paired_stats(b),
        "window_sweep": window_sweep(),
        "write_time": write_time(b),
        "heldout": heldout(),
    }
