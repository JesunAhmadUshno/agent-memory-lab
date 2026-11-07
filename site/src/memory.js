// JavaScript port of the repo's memory designs, run live in the browser.
// Sources: level-1-learn/memory.py (word_count, extract_value, build_store,
// answer_full, answer_tiered) and level-2-build/memory_build.py
// (build_store_extended). memory.check.mjs fails the build unless this port
// reproduces every recorded answer, word count and operation count.

const CANONICAL = /^My (.+?) is (.+?)\.$/; // memory._CANONICAL, used with re.match
const HAPPENS = /happens to be (.+?)\.?$/; // memory._HAPPENS
const IS = / is (.+?)\.?$/; // memory._IS
const EXTENDED = [ // memory_build._EXTENDED_PATTERNS
  /^By the way, the (.+?), if you ever need it, happens to be (.+?)\.$/,
  /^For the record, my (.+?) is (.+?)\.$/,
];

// Python len(text.split()): whitespace-separated words.
export const wordCount = (t) => t.split(/\s+/).filter(Boolean).length;
const sumWords = (turns) => turns.reduce((s, t) => s + wordCount(t), 0);

export function extractValue(turn) {
  const m = HAPPENS.exec(turn) || IS.exec(turn);
  return m ? m[1] : null;
}

// Map, not a plain object, so a typed key like "__proto__" stays a plain key.
export function buildStore(turns) {
  const store = new Map();
  for (const t of turns) { const m = CANONICAL.exec(t); if (m) store.set(m[1], m[2]); }
  return store;
}

export function buildStoreExtended(turns) {
  const store = buildStore(turns);
  for (const t of turns) for (const p of EXTENDED) { const m = p.exec(t); if (m) store.set(m[1], m[2]); }
  return store;
}

// Which extractor (if any) stores a turn: 'canonical', 'extended' or null.
export function storedBy(turn) {
  if (CANONICAL.test(turn)) return 'canonical';
  return EXTENDED.some((p) => p.test(turn)) ? 'extended' : null;
}

// Design A: re-scan every turn, take the last one containing the key phrase.
export function answerFull(q, turns) {
  let found = null;
  for (const t of turns) if (t.toLowerCase().includes(q.key_phrase)) found = t;
  return { answer: found === null ? null : extractValue(found), words: sumWords(turns), ops: turns.length };
}

// Design B: read the recent window, then the store entry on a hit, else scan the window newest first.
// Python turns[len(turns) - size:] and JS slice agree for every size, including 0.
export function answerTiered(q, store, turns, size = 4) {
  const window = turns.slice(turns.length - size);
  let words = sumWords(window);
  const ops = 1 + window.length;
  if (store.has(q.store_key)) {
    const v = store.get(q.store_key);
    return { answer: v, words: words + wordCount(`${q.store_key} is ${v}`), ops };
  }
  for (const t of [...window].reverse()) if (t.toLowerCase().includes(q.key_phrase)) return { answer: extractValue(t), words, ops };
  return { answer: null, words, ops };
}

// All three designs over a question set; turnsFor(q) gives that question's conversation.
export function runSet(questions, turnsFor, size = 4) {
  const cache = new Map();
  const stores = (turns) => {
    if (!cache.has(turns)) cache.set(turns, { tiered: buildStore(turns), extended: buildStoreExtended(turns) });
    return cache.get(turns);
  };
  const rows = questions.map((q) => {
    const turns = turnsFor(q), s = stores(turns);
    return { q, full: answerFull(q, turns), tiered: answerTiered(q, s.tiered, turns, size), extended: answerTiered(q, s.extended, turns, size) };
  });
  const tot = (k) => ({
    correct: rows.filter((r) => r[k].answer === r.q.expected).length,
    words: rows.reduce((s, r) => s + r[k].words, 0),
    ops: rows.reduce((s, r) => s + r[k].ops, 0),
  });
  return { rows, full: tot('full'), tiered: tot('tiered'), extended: tot('extended') };
}

// Total cost in words when one missed answer is worth V words.
export const totalCost = (words, missed, V) => words + V * missed;

// Scaling projection from results_deep.json: full context grows with the transcript, tiered reads stay fixed.
export const projectedRatio = (fullWords, factor, tieredWords) => (fullWords * factor) / tieredWords;
