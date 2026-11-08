// Known-answer parity gate, run by `npm run build` before vite.
// Runs the JS port (memory.js) on the turn texts parsed from the Python sources and
// fails unless every answer, word count and operation count matches the recorded results files.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { loadBenchmark } from './sources.js';
import { buildStore, buildStoreExtended, runSet, totalCost, projectedRatio } from './memory.js';

const root = new URL('../../', import.meta.url);
const read = (p) => readFileSync(new URL(p, root), 'utf8');
const json = (p) => JSON.parse(read(p));
const bench = loadBenchmark({ memoryPy: read('src/memory.py'), buildPy: read('src/memory_build.py'), ablationsPy: read('src/ablations.py') });
const learn = json('results/results_learn.json');
const build = json('results/results_build.json');
const abl = json('results/results_ablations.json');
const deep = json('results/results_deep.json');
const obj = (m) => Object.fromEntries(m);
let n = 0;
const eq = (a, b, msg) => { assert.deepEqual(a, b, msg); n++; };

// Learn: 8 questions on one conversation.
eq(bench.window, learn.recent_window_turns, 'window');
eq(obj(buildStore(bench.learn.turns)), learn.store, 'learn store');
const L = runSet(bench.learn.questions, () => bench.learn.turns);
L.rows.forEach((r, i) => {
  const w = learn.per_question[i];
  eq([r.q.id, r.full.answer, r.full.words, r.full.ops], [w.id, w.full_answer, w.full_words_read, w.full_turns_scanned], `learn full ${w.id}`);
  eq([r.tiered.answer, r.tiered.words, r.tiered.ops], [w.tiered_answer, w.tiered_words_read, w.tiered_ops_count], `learn tiered ${w.id}`);
});
eq([L.full.correct, L.full.words, L.tiered.correct, L.tiered.words], [learn.full_correct, learn.full_words_total, learn.tiered_correct, learn.tiered_words_total], 'learn totals');

// Build: 24 questions on three conversations, all three designs.
const conv = (q) => bench.build.conversations[q.conversation];
for (const [c, turns] of Object.entries(bench.build.conversations)) {
  eq(obj(buildStore(turns)), build.per_conversation[c].store, `store ${c}`);
  eq(obj(buildStoreExtended(turns)), build.per_conversation[c].extended_store, `extended store ${c}`);
}
const B = runSet(bench.build.questions, conv);
B.rows.forEach((r, i) => {
  const w = build.per_question[i];
  eq(r.q.id, w.id, 'order');
  for (const k of ['full', 'tiered', 'extended']) {
    const ops = k === 'full' ? w.full_turns_scanned : w[`${k}_ops_count`];
    eq([r[k].answer, r[k].words, r[k].ops], [w[`${k}_answer`], w[`${k}_words_read`], ops], `build ${k} ${w.id}`);
  }
});
for (const k of ['full', 'tiered', 'extended']) eq([B[k].correct, B[k].words], [build[`${k}_correct`], build[`${k}_words_total`]], `build ${k} totals`);

// Window slider: every window size 0 to 18 matches the recorded Python sweep.
for (const row of abl.window_sweep) {
  const R = runSet(bench.build.questions, conv, row.window);
  eq([R.tiered.correct, R.tiered.words, R.tiered.ops, R.extended.correct, R.extended.words, R.extended.ops],
    [row.tiered_correct, row.tiered_words, row.tiered_ops, row.extended_correct, row.extended_words, row.extended_ops], `window ${row.window}`);
}

// Held-out phrasing probe.
const H = runSet(bench.heldout.questions, () => bench.heldout.turns);
H.rows.forEach((r, i) => {
  const w = abl.heldout.per_question[i];
  for (const k of ['full', 'tiered', 'extended']) eq([r[k].answer, r[k].words], [w[`${k}_answer`], w[`${k}_words_read`]], `heldout ${k} ${w.id}`);
});

// Value-of-an-answer slider: crossovers land on the recorded break-even values.
const d = deep.designs, Q = deep.source_build.questions;
const cost = (k, V) => totalCost(d[k].words_total, Q - d[k].correct, V);
const v1 = deep.breakeven.tiered_vs_full_breakeven_value_words, v2 = deep.breakeven.extended_vs_tiered_cost_per_recovered_word;
assert.ok(Math.abs(cost('tiered', v1) - cost('full', v1)) < 1e-3, 'tiered vs full crossover'); n++;
assert.ok(Math.abs(cost('extended', v2) - cost('tiered', v2)) < 1e-9, 'extended vs tiered crossover'); n++;
assert.ok(cost('tiered', v1 - 1) < cost('full', v1 - 1) && cost('tiered', v1 + 1) > cost('full', v1 + 1), 'tiered/full order'); n++;

// Projection slider reproduces the recorded projection rows.
for (const p of deep.projection) { assert.ok(Math.abs(projectedRatio(d.full.words_total, p.factor, d.tiered.words_total) - p.tiered_ratio_projected) < 1e-5, `projection ${p.factor}`); n++; }

console.log(`memory parity ok: ${n} checks (learn ${L.rows.length}, build ${B.rows.length}, windows ${abl.window_sweep.length}, held-out ${H.rows.length})`);
