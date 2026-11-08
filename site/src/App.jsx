import { useMemo, useState, useEffect, useId } from 'react';
import learn from '../../results/results_learn.json';
import build from '../../results/results_build.json';
import abl from '../../results/results_ablations.json';
import deep from '../../results/results_deep.json';
import memoryPy from '../../src/memory.py?raw';
import buildPy from '../../src/memory_build.py?raw';
import ablationsPy from '../../src/ablations.py?raw';
import readme from '../../README.md?raw';
import report from '../../REPORT.md?raw';
import { loadBenchmark } from './sources.js';
import { buildStore, buildStoreExtended, answerFull, answerTiered, storedBy, runSet, totalCost, projectedRatio, wordCount } from './memory.js';

const REPO = 'https://github.com/JesunAhmadUshno/agent-memory-lab';
const blob = (p) => `${REPO}/blob/main/${p}`;
const fmt = (n) => Math.round(n).toLocaleString('en-US');
const bench = loadBenchmark({ memoryPy, buildPy, ablationsPy });
const W4 = bench.window;
const D = deep.designs;
const Q = deep.source_build.questions;
const DESIGNS = [['full', 'Full context', 'var(--muted)'], ['tiered', 'Tiered memory', 'var(--warn)'], ['extended', 'Tiered extended', 'var(--primary)']];
const STRATA = ['canonical', 'update', 'noncanonical_extended', 'noncanonical_unhandled'];
const sha = (file) => new RegExp(`results/${file} \\| sha256 ([0-9a-f]{64})`).exec(report)[1];
const checks = /\((\d+) Learn, (\d+) Build, (\d+) Deep\)/.exec(report).slice(1).map(Number);
// Stages and verdict are read from README.md, word for word.
const stages = [...readme.matchAll(/^- (\w+): ([A-Z]+)(?: (\d{4}-\d{2}-\d{2}))?$/gm)].map((m) => m.slice(1));
const verdict = (readme.match(/^\*\*Verdict\.\*\* ([^.]+)/m) || [])[1];
const convTurns = (c) => (c === 'learn' ? bench.learn.turns : bench.build.conversations[c]);
const convQuestions = (c) => (c === 'learn' ? bench.learn.questions : bench.build.questions.filter((q) => q.conversation === c));

const SECTIONS = [['top', 'Overview', '◎'], ['how', 'How it works', '⇄'], ['play', 'Playground', '▶'], ['window', 'Window sweep', '◫'], ['ab', 'A/B table', '▥'], ['frontier', 'Cost frontier', '◇'], ['projection', 'Projection', '↗'], ['limits', 'Limits', '!'], ['reproduce', 'Reproduce', '❯_']];

function useReveal() {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.08 });
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  }, []);
}

function MenuBar() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 30000); return () => clearInterval(t); }, []);
  return (
    <div className="menubar" role="banner">
      <span className="apple" aria-hidden="true">◆</span>
      <a className="app" href="#top">Agent Memory Lab</a>
      <a className="m" href={blob('PROPOSAL.md')}>Proposal</a>
      <a className="m" href={blob('REPORT.md')}>Report</a>
      <span className="spacer" />
      <span className="status"><i /> Byte-identical reruns</span>
      <a href={REPO}>GitHub ↗</a>
      <span className="clock">{now.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })}</span>
    </div>
  );
}

function Dock() {
  const [active, setActive] = useState('top');
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setActive(e.target.id)), { rootMargin: '-45% 0px -50% 0px' });
    SECTIONS.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  }, []);
  return (
    <nav className="dock" aria-label="Sections">
      {SECTIONS.map(([id, label, icon]) => (
        <a key={id} href={`#${id}`} className={active === id ? 'on' : ''} aria-current={active === id ? 'true' : undefined}>
          <span className="ico" aria-hidden="true">{icon}</span><span className="lbl">{label}</span>
        </a>
      ))}
    </nav>
  );
}

function Range({ label, value, min, max, step, onChange, show }) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label} <span>{show}</span></label>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} />
    </div>
  );
}

function Select({ label, value, onChange, options }) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
      </select>
    </div>
  );
}

export default function App() {
  useReveal();
  return (
    <div className="wrap">
      <MenuBar />
      <div className="glow" aria-hidden="true" />
      <Hero />
      <How />
      <Playground />
      <WindowSweep />
      <AB />
      <Frontier />
      <Projection />
      <Limits />
      <Reproduce />
      <Dock />
      <footer>
        Synthetic data built in code. Cost is a word count, latency is a counted proxy. Code: Apache-2.0. Every number on this page is read from the
        repo&apos;s <code>results_*.json</code> files and Python sources at build time; the playground and sliders run a checked JavaScript port in your browser.
      </footer>
    </div>
  );
}

function Hero() {
  const ratio = deep.savings.extended.ratio_vs_full.toFixed(1);
  return (
    <header className="card hero window" id="top" data-title="agent-memory-lab — README">
      <div className="head">
        <p className="eyebrow">Conversation memory · three-level study</p>
        <span className="pill warn">● Synthetic data · word-count cost · counted latency</span>
      </div>
      <h1>Tiered memory matched full context at {D.extended.correct} of {Q} answers while reading <em>{ratio}x fewer words</em> ({fmt(D.extended.words_total)} vs {fmt(D.full.words_total)}), but only after its extractor learned the two phrasings it was missing.</h1>
      <p className="sub">
        Two ways to answer questions about a long conversation: re-scan the whole transcript every time (full context), or pull facts into a small store
        as they are said and answer from the store plus the last {W4} turns (tiered memory). The study runs both on {build.conversations} synthetic conversations
        ({build.turns_total} turns, {Q} questions). Here &ldquo;full context&rdquo; is a pattern scan, not a language model reading the transcript; see the limits below.
      </p>
      <div className="actions">
        <a className="btn primary" href="#play">Open the memory playground</a>
        <a className="btn ghost" href={blob('REPORT.md')}>Read the report</a>
        <span className="hint">Reproduce with <code>python src/make_results.py --check</code></span>
      </div>
      <div className="tiles">
        {DESIGNS.map(([k, l]) => (
          <div className="tile" key={k}><div className="num">{D[k].correct}<small className="of">/{Q}</small></div><div className="cap">{l}: correct answers, {fmt(D[k].words_total)} words read</div></div>
        ))}
        <div className="tile"><div className="num">{D.extended.words_per_correct}</div><div className="cap">Words per correct answer, tiered extended (full: {D.full.words_per_correct.toFixed(2)}, tiered: {D.tiered.words_per_correct})</div></div>
      </div>
      <p className="sub" style={{ marginTop: 18 }}><b>Verdict: {verdict}.</b> Stages and verdict are read from README.md word for word; the plan is PROPOSAL.md.</p>
      <div className="chips" style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
        {stages.map(([s, st, d]) => <span key={s} className={`pill ${st === 'DONE' ? 'good' : st === 'DRAFT' ? 'warn' : 'info'}`}>{s}: {st}{d ? ` ${d}` : ''}</span>)}
      </div>
    </header>
  );
}

function How() {
  const lr = deep.learn_reference;
  const miss = learn.per_question.find((r) => !r.tiered_correct);
  const missTurn = bench.learn.turns[miss.source_turn];
  const W = 460, H = 250;
  const box = (x, y, w, h, t, s, tone) => (
    <g>
      <rect x={x} y={y} width={w} height={h} rx="10" fill="var(--surface-strong)" stroke={tone} strokeWidth="1.5" />
      <text x={x + w / 2} y={y + h / 2 - (s ? 3 : -4)} textAnchor="middle" style={{ fill: 'var(--text)', fontSize: 12.5, fontWeight: 600 }}>{t}</text>
      {s && <text x={x + w / 2} y={y + h / 2 + 13} textAnchor="middle">{s}</text>}
    </g>
  );
  return (
    <section id="how" className="card window reveal" data-title="memory.py — two designs">
      <p className="eyebrow">How it works</p>
      <h2>One design re-reads everything. The other <em>decides at write time</em> what is worth keeping.</h2>
      <div className="grid2" style={{ marginTop: 16 }}>
        <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Diagram of full context and tiered memory read paths">
          <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--muted)" /></marker></defs>
          <text x="0" y="14" style={{ fill: 'var(--text)', fontWeight: 700 }}>Full context</text>
          {box(0, 26, 140, 48, `All ${bench.learn.turns.length} turns`, 'scanned every question', 'var(--border)')}
          {box(170, 26, 130, 48, 'Last matching turn', 'by key phrase', 'var(--border)')}
          {box(330, 26, 130, 48, 'Extract value', 'value at the end', 'var(--muted)')}
          <line x1="140" y1="50" x2="168" y2="50" stroke="var(--muted)" markerEnd="url(#arr)" /><line x1="300" y1="50" x2="328" y2="50" stroke="var(--muted)" markerEnd="url(#arr)" />
          <text x="0" y="114" style={{ fill: 'var(--text)', fontWeight: 700 }}>Tiered memory</text>
          {box(0, 126, 140, 48, 'Each new turn', 'checked once on write', 'var(--border)')}
          {box(170, 126, 130, 48, 'Fact store', '"My X is V." only', 'var(--primary)')}
          {box(170, 190, 130, 48, `Recent ${W4} turns`, 'fallback scan', 'var(--warn)')}
          {box(330, 156, 130, 48, 'Answer', 'store hit, else window', 'var(--primary)')}
          <line x1="140" y1="150" x2="168" y2="150" stroke="var(--muted)" markerEnd="url(#arr)" />
          <line x1="300" y1="150" x2="328" y2="172" stroke="var(--muted)" markerEnd="url(#arr)" /><line x1="300" y1="214" x2="328" y2="190" stroke="var(--muted)" markerEnd="url(#arr)" />
        </svg>
        <div>
          <h3>Learn result (results_learn.json)</h3>
          <p className="hint" style={{ marginTop: 4 }}>One conversation of {learn.turns} turns, {learn.questions} questions.</p>
          <div className="tiles" style={{ gridTemplateColumns: '1fr 1fr', marginTop: 8 }}>
            <div className="tile"><div className="num">{lr.full_correct}/{learn.questions}</div><div className="cap">Full context, {fmt(lr.full_words_total)} words read</div></div>
            <div className="tile"><div className="num">{lr.tiered_correct}/{learn.questions}</div><div className="cap">Tiered memory, {fmt(lr.tiered_words_total)} words read ({lr.tiered_ratio_vs_full.toFixed(2)}x fewer)</div></div>
          </div>
          <p className="hint" style={{ marginTop: 12 }}>
            The one miss, <b>{miss.id}</b>: the door code {miss.expected} was said as <q>{missTurn}</q> That is not the canonical <q>My X is V.</q> form, so it never
            reached the store, and turn {miss.source_turn} sits outside the last {W4} turns.
          </p>
        </div>
      </div>
    </section>
  );
}

// The value-before-label turn from Build conversation A (question A6), cut at its first comma, and its canonical rewording.
const UNHANDLED = build.per_question.find((r) => r.stratum === 'noncanonical_unhandled');
const UNHANDLED_Q = bench.build.questions.find((q) => q.id === UNHANDLED.id);
const UNHANDLED_TURN = bench.build.conversations[UNHANDLED.conversation][UNHANDLED.source_turn];
const EXAMPLE = `${UNHANDLED_TURN.split(',')[0]}.`;
const REWORDED = `My ${UNHANDLED_Q.store_key} is ${UNHANDLED.expected}.`;

function Playground() {
  const [conv, setConv] = useState('learn');
  const [text, setText] = useState(() => convTurns('learn').join('\n'));
  const [qi, setQi] = useState(String(bench.learn.questions.findIndex((x) => x.id === learn.per_question.find((r) => !r.tiered_correct).id)));
  const [key, setKey] = useState(UNHANDLED_Q.store_key);
  const qs = convQuestions(conv);
  const pick = (c) => { setConv(c); setText(convTurns(c).join('\n')); setQi('0'); };
  const turns = useMemo(() => text.split('\n').map((t) => t.trim()).filter(Boolean), [text]);
  const custom = qi === 'custom';
  const q = custom ? { key_phrase: key.toLowerCase().trim(), store_key: key.trim(), expected: null } : qs[+qi];
  const store = useMemo(() => buildStore(turns), [turns]);
  const ext = useMemo(() => buildStoreExtended(turns), [turns]);
  const out = { full: answerFull(q, turns), tiered: answerTiered(q, store, turns, W4), extended: answerTiered(q, ext, turns, W4) };
  const edited = text !== convTurns(conv).join('\n');
  const winStart = Math.max(0, turns.length - W4);
  return (
    <section id="play" className="card window reveal" data-title="memory_playground — live">
      <div className="head">
        <div>
          <p className="eyebrow">Live playground</p>
          <h2>Edit the conversation and watch <em>phrasing</em> decide what gets stored.</h2>
          <p className="sub">
            A JavaScript port of <a href={blob('src/memory.py')}>memory.py</a> and <a href={blob('src/memory_build.py')}>memory_build.py</a> runs
            on the real benchmark turns, read from those files at build time. The build fails unless this port reproduces every recorded answer, word count and
            operation count. It opens on the Learn conversation&apos;s one tiered miss. Add <q>{EXAMPLE}</q>, ask about the custom label <i>{UNHANDLED_Q.store_key}</i>,
            and every design returns None; reword it as <q>{REWORDED}</q> and the store picks it up.
          </p>
        </div>
        <span className="pill info">● computed live</span>
      </div>
      <div className="controls">
        <Select label="Conversation" value={conv} onChange={pick} options={[['learn', `Learn (${bench.learn.turns.length} turns)`], ...Object.keys(bench.build.conversations).map((c) => [c, `Build ${c} (${convTurns(c).length} turns)`])]} />
        <Select label="Question" value={qi} onChange={setQi} options={[...qs.map((x, i) => [String(i), `${x.id}: ${x.store_key}`]), ['custom', 'Custom: ask about any label']]} />
        {custom && (
          <div className="field"><label htmlFor="pg-key">Ask about (label)</label><input id="pg-key" className="txt" value={key} onChange={(e) => setKey(e.target.value)} /></div>
        )}
      </div>
      <div className="grid2">
        <div>
          <div className="field">
            <label htmlFor="pg-turns">Turns, one per line <span>{turns.length} turns, {fmt(turns.reduce((s, t) => s + wordCount(t), 0))} words</span></label>
            <textarea id="pg-turns" className="turns" value={text} onChange={(e) => setText(e.target.value)} rows={12} spellCheck="false" />
          </div>
          <div className="actions" style={{ marginTop: 8 }}>
            <button className="btn ghost" onClick={() => setText(`${text.trimEnd()}\n${EXAMPLE}`)}>Add the value-before-label turn</button>
            <button className="btn ghost" onClick={() => setText(convTurns(conv).join('\n'))} disabled={!edited}>Reset</button>
          </div>
          <ol className="turnlist" aria-label="How each turn is handled">
            {turns.map((t, i) => {
              const by = storedBy(t);
              return (
                <li key={i} className={i >= winStart ? 'win' : ''}>
                  <span className="mono">{i}</span><span className="t">{t}</span>
                  {by && <span className={`pill ${by === 'canonical' ? 'info' : 'good'}`}>{by === 'canonical' ? 'stored' : 'extended only'}</span>}
                  {i >= winStart && <span className="pill warn">window</span>}
                </li>
              );
            })}
          </ol>
        </div>
        <div>
          <h3>Answers{q.expected != null && <> (expected <span className="mono">{q.expected}</span>)</>}</h3>
          <div className="answers">
            {DESIGNS.map(([k, l, c]) => {
              const r = out[k];
              const ok = q.expected == null ? null : r.answer === q.expected;
              return (
                <div className="tile ans" key={k} style={{ borderLeft: `4px solid ${c}` }}>
                  <div className="head" style={{ marginBottom: 4 }}><b>{l}</b>{ok !== null && <span className={`pill ${ok ? 'good' : 'bad'}`}>{ok ? 'correct' : 'wrong'}</span>}</div>
                  <div className="val">{r.answer ?? <span className="no">None (silent miss)</span>}</div>
                  <div className="hint">{fmt(r.words)} words read · {r.ops} {k === 'full' ? 'turns scanned' : 'operations'}</div>
                </div>
              );
            })}
          </div>
          <h3 style={{ marginTop: 16 }}>Extended store ({ext.size} facts; the original store holds {store.size})</h3>
          <div className="chips">
            {[...ext].map(([k, v]) => <span key={k} className={`pill ${store.has(k) ? 'info' : 'good'}`}><b>{k}</b>&nbsp;{v}</span>)}
          </div>
        </div>
      </div>
    </section>
  );
}

function LineChart({ label, rows, ys, yMax, x, cur, fmtY = (v) => v, xLabel }) {
  const W = 460, H = 220, pad = { l: 42, r: 10, t: 12, b: 26 };
  const xMax = rows[rows.length - 1][x];
  const sx = (v) => pad.l + (v / xMax) * (W - pad.l - pad.r);
  const sy = (v) => pad.t + (1 - v / yMax) * (H - pad.t - pad.b);
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
      {[0, 0.5, 1].map((f) => <g key={f}><line className="axis" x1={pad.l} x2={W - pad.r} y1={sy(f * yMax)} y2={sy(f * yMax)} /><text x={pad.l - 6} y={sy(f * yMax) + 4} textAnchor="end">{fmtY(f * yMax)}</text></g>)}
      <line x1={sx(cur.x)} x2={sx(cur.x)} y1={pad.t} y2={H - pad.b} stroke="var(--text)" strokeDasharray="3 4" opacity="0.5" />
      {ys.map(([k, c]) => (
        <g key={k}>
          <polyline fill="none" stroke={c} strokeWidth="2.2" points={rows.map((r) => `${sx(r[x])},${sy(r[k])}`).join(' ')} />
          <circle cx={sx(cur.x)} cy={sy(cur[k])} r="5.5" fill={c} stroke="var(--surface-strong)" strokeWidth="2" />
        </g>
      ))}
      <text x={pad.l} y={H - 6}>{rows[0][x]}</text><text x={W - pad.r} y={H - 6} textAnchor="end">{xLabel}</text>
    </svg>
  );
}

function WindowSweep() {
  const [size, setSize] = useState(W4);
  const live = useMemo(() => runSet(bench.build.questions, (q) => bench.build.conversations[q.conversation], size), [size]);
  const rows = abl.window_sweep;
  const rec = rows.find((r) => r.window === size);
  const atDefault = size === W4;
  const maxW = rows[rows.length - 1].window;
  const firstFull = rows.find((r) => r.tiered_correct === r.extended_correct);
  const cur = { x: size, tiered_correct: live.tiered.correct, extended_correct: live.extended.correct, tiered_words: live.tiered.words, extended_words: live.extended.words };
  const yWords = Math.ceil(rows[rows.length - 1].extended_words / 500) * 500;
  return (
    <section id="window" className="card window reveal" data-title="window_sweep — results_ablations.json">
      <div className="head">
        <div>
          <p className="eyebrow">Ablation · recent-window size</p>
          <h2>The window rescues missed facts only when it grows to <em>{firstFull.window} turns</em>, and by then it reads {fmt(firstFull.tiered_words)} words.</h2>
          <p className="sub">
            The recorded runs fix the window at {W4} turns. Drag it from 0 to {maxW}: the port reruns tiered and tiered extended on all {Q} Build questions in your browser.
            Lines are the recorded Python sweep (<a href={blob('src/ablations.py')}>ablations.py</a>); the dots are computed live, and the build checks the two agree at every size.
            The jumps happen where the window first covers the turns holding the non-canonical facts, so this measures placement luck, not a better design.
          </p>
        </div>
        <span className="pill info">● computed live, checked against the record</span>
      </div>
      <div className="controls" style={{ gridTemplateColumns: 'minmax(0, 1fr)' }}>
        <Range label="Recent window (turns)" value={size} min={0} max={maxW} step={1} onChange={setSize} show={`${size} turns${atDefault ? ' (recorded setting)' : ''}`} />
      </div>
      <div className="tiles" style={{ marginTop: 0 }}>
        <div className="tile"><div className="num">{live.tiered.correct}/{Q}</div><div className="cap">Tiered correct at window {size}</div></div>
        <div className="tile"><div className="num">{fmt(live.tiered.words)}</div><div className="cap">Tiered words read</div></div>
        <div className="tile"><div className="num">{live.extended.correct}/{Q}</div><div className="cap">Tiered extended correct</div></div>
        <div className="tile"><div className="num">{fmt(live.extended.words)}</div><div className="cap">Extended words read (full context: {fmt(build.full_words_total)})</div></div>
      </div>
      <p className="hint" style={{ marginTop: 8 }}>
        {rec.tiered_correct === live.tiered.correct && rec.tiered_words === live.tiered.words ? `Matches results_ablations.json at window ${size}.` : 'Differs from the record.'}
        {atDefault && ` At ${W4} turns this is the published Build result: ${build.tiered_correct}/${Q} at ${build.tiered_words_total} words and ${build.extended_correct}/${Q} at ${build.extended_words_total} words.`}
      </p>
      <div className="grid2" style={{ marginTop: 12 }}>
        <div><h3>Correct answers by window size</h3>
          <LineChart label="Correct answers against recent window size" rows={rows} x="window" yMax={Q} cur={cur} xLabel={`${maxW} turns`}
            ys={[['tiered_correct', 'var(--warn)'], ['extended_correct', 'var(--primary)']]} /></div>
        <div><h3>Words read by window size</h3>
          <LineChart label="Words read against recent window size" rows={rows} x="window" yMax={yWords} cur={cur} fmtY={fmt} xLabel={`${maxW} turns`}
            ys={[['tiered_words', 'var(--warn)'], ['extended_words', 'var(--primary)']]} /></div>
      </div>
      <div className="legend"><span><i style={{ background: 'var(--warn)' }} />Tiered memory</span><span><i style={{ background: 'var(--primary)' }} />Tiered extended</span></div>
      <p className="hint">The two word lines nearly overlap: the extended store&apos;s longer entries add {build.extended_words_total - build.tiered_words_total} words at every window size.</p>
    </section>
  );
}

function AB() {
  const [conv, setConv] = useState('all');
  const [stratum, setStratum] = useState('all');
  const [hover, setHover] = useState(null);
  const S = build.strata;
  // One small chart per stratum; bar height is the share of that stratum answered correctly.
  const W = 220, H = 150, bw = 54;
  const sy = (f) => 22 + (1 - f) * (H - 30);
  const rows = build.per_question.filter((r) => (conv === 'all' || r.conversation === conv) && (stratum === 'all' || r.stratum === stratum));
  const cell = (r, k) => (
    <td className={r[`${k}_correct`] ? 'ok' : 'no'}>{r[`${k}_answer`] ?? 'None'} <span className="hint">· {r[`${k}_words_read`]}w</span></td>
  );
  return (
    <section id="ab" className="card window reveal" data-title={`results_build.json — ${Q} questions`}>
      <p className="eyebrow">A/B table and strata · recorded</p>
      <h2>The whole accuracy gap sits in <em>one stratum</em>: facts phrased outside the canonical form.</h2>
      <p className="sub">
        Correct answers by question stratum and design, from the recorded Build run. Canonical and update questions are answered by every design;
        noncanonical_extended is lost by the original store and recovered by the two added patterns; the value-before-label form beats all three.
      </p>
      <div className="strata" onMouseLeave={() => setHover(null)}>
        {STRATA.map((s) => (
          <figure key={s}>
            <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Correct answers by design on the ${s} stratum`}>
              <line className="axis" x1="0" x2={W} y1={sy(0)} y2={sy(0)} />
              {DESIGNS.map(([k, l, c], j) => {
                const v = S[s][`${k}_correct`], x = 14 + j * (bw + 12), h = Math.max(v / S[s].questions, 0.03);
                return (
                  <g key={k} onMouseEnter={() => setHover({ s, l, v, n: S[s].questions })}>
                    <rect x={x} y={sy(h)} width={bw} height={sy(0) - sy(h)} rx="5" fill={c} opacity={v ? 0.9 : 0.3} />
                    <text x={x + bw / 2} y={sy(h) - 6} textAnchor="middle" style={{ fill: 'var(--text)', fontSize: 13, fontWeight: 600 }}>{v}/{S[s].questions}</text>
                  </g>
                );
              })}
            </svg>
            <figcaption><b>{s}</b> · {S[s].questions} questions</figcaption>
          </figure>
        ))}
      </div>
      <div className="legend">{DESIGNS.map(([k, l, c]) => <span key={k}><i style={{ background: c }} />{l}</span>)}</div>
      <div className="tip" aria-live="polite">{hover ? `${hover.l} on ${hover.s}: ${hover.v} of ${hover.n} correct.` : 'Hover a bar for its count.'}</div>
      <p className="hint">
        Uncertainty (results_ablations.json): Wilson 95% intervals on accuracy are {DESIGNS.map(([k, l]) => `${l.toLowerCase()} ${abl.paired_stats.accuracy_wilson95[k].map((v) => v.toFixed(2)).join(' to ')}`).join(', ')}.
        Tiered against full context: {abl.paired_stats.mcnemar.full_vs_tiered.only_full} questions only full gets right, {abl.paired_stats.mcnemar.full_vs_tiered.only_tiered} the other way, exact McNemar p = {abl.paired_stats.mcnemar.full_vs_tiered.p_exact_two_sided}.
        The questions are hand-built, not sampled, so these are a floor on uncertainty, not a population claim.
      </p>
      <h3 style={{ marginTop: 20 }}>Question explorer (recorded replay of results_build.json)</h3>
      <div className="controls" style={{ marginTop: 10 }}>
        <Select label="Conversation" value={conv} onChange={setConv} options={[['all', 'All conversations'], ...Object.keys(build.per_conversation).map((c) => [c, `Conversation ${c}`])]} />
        <Select label="Stratum" value={stratum} onChange={setStratum} options={[['all', 'All strata'], ...STRATA.map((s) => [s, s])]} />
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table className="nowrap">
          <thead><tr><th>ID</th><th>Stratum</th><th>Turn</th><th>Expected</th><th>Full context</th><th>Tiered</th><th>Extended</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}><td className="mono">{r.id}</td><td>{r.stratum}</td><td>{r.source_turn}</td><td className="mono">{r.expected}</td>{cell(r, 'full')}{cell(r, 'tiered')}{cell(r, 'extended')}</tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="hint">{rows.length} of {Q} questions shown. Green is correct, red is wrong; <i>w</i> is words read for that question.</p>
    </section>
  );
}

function Frontier() {
  const [V, setV] = useState(100);
  const [write, setWrite] = useState(false);
  const be = deep.breakeven;
  const wt = abl.write_time.designs;
  const words = (k) => (write ? wt[k].total_words : D[k].words_total);
  const costs = DESIGNS.map(([k, l, c]) => ({ k, l, c, cost: totalCost(words(k), Q - D[k].correct, V) }));
  const best = costs.reduce((a, b) => (b.cost < a.cost ? b : a));
  const maxCost = Math.max(...costs.map((x) => x.cost));
  const W = 460, H = 256, pad = { l: 40, r: 16, t: 14, b: 46 };
  const xMax = Math.ceil(D.full.words_total / 500) * 500;
  const yLo = Math.min(...DESIGNS.map(([k]) => D[k].correct)) - 3;
  const sx = (v) => pad.l + (v / xMax) * (W - pad.l - pad.r);
  const sy = (v) => pad.t + (1 - (v - yLo) / (Q - yLo)) * (H - pad.t - pad.b);
  return (
    <section id="frontier" className="card window reveal" data-title="verdict.py — words vs answers">
      <p className="eyebrow">Cost frontier · arithmetic on recorded numbers</p>
      <h2>Which design wins depends on what a <em>missed answer</em> is worth.</h2>
      <p className="sub">
        Total cost = words read + V × answers missed, where V is the value of one correct answer in words. Tiered memory saves {fmt(be.tiered_vs_full_words_saved)} words
        against full context and loses {be.tiered_vs_full_answers_lost} answers, so it breaks even at V = {be.tiered_vs_full_breakeven_value_words.toFixed(2)}. The extension
        recovers {be.extended_vs_tiered_answers_gained} answers for {be.extended_vs_tiered_extra_words} extra words, {be.extended_vs_tiered_cost_per_recovered_word} words per answer
        (<a href={blob('results/results_deep.json')}>results_deep.json</a>). On this set the extended design never costs more than full context.
      </p>
      <div className="grid2" style={{ marginTop: 16 }}>
        <div>
          <h3>Words read against correct answers</h3>
          <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Scatter of words read against correct answers for three designs">
            {[0, xMax / 2, xMax].map((t) => <g key={t}><line className="axis" x1={sx(t)} x2={sx(t)} y1={pad.t} y2={H - pad.b} /><text x={sx(t)} y={H - pad.b + 16} textAnchor="middle">{fmt(t)}</text></g>)}
            {[yLo, Q].map((t) => <g key={t}><line className="axis" x1={pad.l} x2={W - pad.r} y1={sy(t)} y2={sy(t)} /><text x={pad.l - 6} y={sy(t) + 4} textAnchor="end">{t}</text></g>)}
            {DESIGNS.map(([k, l, c]) => (
              <g key={k}>
                <circle cx={sx(D[k].words_total)} cy={sy(D[k].correct)} r={best.k === k ? 9 : 7} fill={c} stroke={best.k === k ? 'var(--text)' : 'var(--surface-strong)'} strokeWidth="2" />
                <text x={sx(D[k].words_total) + (k === 'full' ? -12 : 12)} y={sy(D[k].correct) + (k === 'tiered' ? -12 : 20)} textAnchor={k === 'full' ? 'end' : 'start'} style={{ fill: 'var(--text)' }}>{l}: {D[k].correct}, {fmt(D[k].words_total)}w</text>
              </g>
            ))}
            <text x={(pad.l + W - pad.r) / 2} y={H - 4} textAnchor="middle">words read (read-time only)</text>
          </svg>
        </div>
        <div>
          <div className="controls" style={{ gridTemplateColumns: '1fr' }}>
            <Range label="V: value of one correct answer" value={V} min={0} max={1000} step={1} onChange={setV} show={`${fmt(V)} words`} />
            <label className="check"><input type="checkbox" checked={write} onChange={(e) => setWrite(e.target.checked)} /> Include one-time store-build words (derived)</label>
          </div>
          <div className="bars">
            {costs.map((x) => (
              <div className="bar-row" key={x.k}>
                <div className="lab"><span>{x.l}{x.k === best.k && <span className="pill good" style={{ marginLeft: 8 }}>cheapest</span>}</span><b>{fmt(x.cost)}</b></div>
                <div className="track"><div className="fill" style={{ width: `${(x.cost / maxCost) * 100}%`, background: x.c }} /></div>
              </div>
            ))}
          </div>
          <p className="hint" style={{ marginTop: 12 }}>
            Computed live from recorded word counts. {write ? `With store-build words, the tiered designs pay ${fmt(wt.tiered.write_words)} and ${fmt(wt.extended.write_words)} words once (results_ablations.json).` : `Below V = ${be.extended_vs_tiered_cost_per_recovered_word} plain tiered is cheapest; above it the extension wins.`}
          </p>
        </div>
      </div>
    </section>
  );
}

function Projection() {
  const [f, setF] = useState(10);
  const P = deep.projection;
  const ratio = projectedRatio(D.full.words_total, f, D.tiered.words_total);
  const W = 640, H = 240, pad = { l: 60, r: 16, t: 14, b: 30 };
  const fMax = P[P.length - 1].factor;
  const yMax = P[P.length - 1].full_words_projected;
  const sx = (v) => pad.l + (v / fMax) * (W - pad.l - pad.r);
  const sy = (v) => pad.t + (1 - v / yMax) * (H - pad.t - pad.b);
  return (
    <section id="projection" className="card window reveal" data-title="projection — not measured">
      <div className="head">
        <div>
          <p className="eyebrow">Scaling projection · not a measurement</p>
          <h2>If the transcript grew {f}x and the facts did not, tiered would read <em>{ratio.toFixed(1)}x fewer</em> words.</h2>
        </div>
        <span className="pill warn">● PROJECTION, not measured</span>
      </div>
      <p className="sub">{deep.projection_note}</p>
      <div className="controls" style={{ gridTemplateColumns: 'minmax(0, 1fr)', marginTop: 12 }}>
        <Range label="Transcript growth factor (projection)" value={f} min={1} max={fMax} step={1} onChange={setF} show={`${f}x: full ${fmt(D.full.words_total * f)} vs tiered ${fmt(D.tiered.words_total)} words`} />
      </div>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Projected words read against transcript growth factor, not measured">
        {[0, yMax / 2, yMax].map((t) => <g key={t}><line className="axis" x1={pad.l} x2={W - pad.r} y1={sy(t)} y2={sy(t)} /><text x={pad.l - 8} y={sy(t) + 4} textAnchor="end">{fmt(t)}</text></g>)}
        <polyline fill="none" stroke="var(--muted)" strokeWidth="2.2" strokeDasharray="6 5" points={P.map((p) => `${sx(p.factor)},${sy(p.full_words_projected)}`).join(' ')} />
        <line x1={sx(0)} x2={sx(fMax)} y1={sy(D.tiered.words_total)} y2={sy(D.tiered.words_total)} stroke="var(--warn)" strokeWidth="2.2" />
        {P.map((p) => <circle key={p.factor} cx={sx(p.factor)} cy={sy(p.full_words_projected)} r="4" fill="var(--muted)" />)}
        <line x1={sx(f)} x2={sx(f)} y1={pad.t} y2={H - pad.b} stroke="var(--text)" strokeDasharray="3 4" opacity="0.5" />
        <text x={sx(f) + 6} y={pad.t + 12} style={{ fill: 'var(--text)' }}>{f}x · ratio {ratio.toFixed(1)}</text>
        <text x={pad.l} y={H - 8}>growth factor 0</text><text x={W - pad.r} y={H - 8} textAnchor="end">{fMax}x (projection)</text>
      </svg>
      <div className="legend"><span><i style={{ background: 'var(--muted)' }} />Full context, projected (dots: factors {P.map((p) => p.factor).join(', ')} in results_deep.json)</span><span><i style={{ background: 'var(--warn)' }} />Tiered memory, held fixed at {fmt(D.tiered.words_total)} words</span></div>
    </section>
  );
}

function Limits() {
  const wt = abl.write_time.designs;
  const h = abl.heldout;
  const byStratum = (s) => build.per_question.filter((r) => r.stratum === s).map((r) => r.id).join(', ');
  const silent = build.per_question.filter((r) => r.tiered_answer === null).map((r) => r.id).join(', ');
  const winStart = Object.values(bench.build.conversations)[0].length - W4;
  const outside = build.per_question.filter((r) => r.stratum.startsWith('noncanonical') && r.source_turn < winStart).map((r) => r.id).join(', ');
  const heldMiss = h.per_question.filter((r) => !r.extended_correct).map((r) => r.id).join(', ');
  const modes = [
    ['Extraction is the bottleneck', `Every accuracy difference traces to which phrasings the write-time patterns cover. Tiered misses: ${byStratum('noncanonical_extended')}.`],
    ['Pattern whack-a-mole', `The two added patterns recover exactly the forms they were written for. On the held-out phrasings the extension misses ${heldMiss}.`],
    ['Silent misses', `A tiered miss returns None with no signal that a fact existed: ${silent}.`],
    ['Window-placement luck', `Every non-canonical fact sits before turn ${winStart}, outside the ${W4}-turn window: ${outside}. The sweep above shows how much a different window would change.`],
    ['Value before label', `"${EXAMPLE}" defeats all three designs, full context included: ${byStratum('noncanonical_unhandled')}.`],
  ];
  return (
    <section id="limits" className="card window reveal" data-title="ablations.py — write cost · held-out · limits">
      <p className="eyebrow">Limits and threats to validity</p>
      <h2>What this study <em>does not</em> show.</h2>
      <div className="grid2" style={{ marginTop: 16 }}>
        <div className="tile">
          <div className="head" style={{ marginBottom: 6 }}><h3>Full context here is a pattern scan, not a model</h3><span className="pill bad">Construct validity</span></div>
          <p className="hint" style={{ margin: 0 }}>The comparison is a fact store against a regex scan of the transcript. A language model reading the whole transcript would likely handle the value-before-label turns, so the 0/{build.strata.noncanonical_unhandled.questions} for full context does not transfer to long-context models.</p>
        </div>
        <div className="tile">
          <div className="head" style={{ marginBottom: 6 }}><h3>The extension was tuned on its test set</h3><span className="pill bad">Overfitting</span></div>
          <p className="hint" style={{ margin: 0 }}>Its two patterns were written for the two phrasings in its stratum. On {h.questions} held-out phrasings written afterwards, full context gets {h.full_correct}, tiered {h.tiered_correct} and extended {h.extended_correct}. The held-out set is a probe, not a random sample.</p>
        </div>
      </div>
      <h3 style={{ marginTop: 20 }}>Write-time cost (derived from recorded counts)</h3>
      <p className="hint" style={{ marginTop: 4 }}>The recorded cost counts only words read at question time. Building the store also reads every turn once per extractor pass ({fmt(abl.write_time.one_pass_words)} words per pass).</p>
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead><tr><th>Design</th><th>Correct</th><th>Read words</th><th>Store-build words</th><th>Total</th><th>Full context ÷ total</th></tr></thead>
          <tbody>
            {DESIGNS.map(([k, l]) => (
              <tr key={k}><td>{l}</td><td>{wt[k].correct}/{Q}</td><td>{fmt(wt[k].read_words)}</td><td>{fmt(wt[k].write_words)}{wt[k].extractor_passes ? ` (${wt[k].extractor_passes} pass${wt[k].extractor_passes > 1 ? 'es' : ''})` : ''}</td><td>{fmt(wt[k].total_words)}</td><td>{wt[k].ratio_full_vs_total ? `${wt[k].ratio_full_vs_total.toFixed(2)}x` : '1x'}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <h3 style={{ marginTop: 20 }}>Held-out phrasing probe (recorded, results_ablations.json)</h3>
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead><tr><th>ID</th><th>Phrasing form</th><th>Expected</th><th>Full context</th><th>Tiered</th><th>Extended</th></tr></thead>
          <tbody>
            {h.per_question.map((r) => (
              <tr key={r.id}><td className="mono">{r.id}</td><td>{r.form}</td><td className="mono">{r.expected}</td>
                {['full', 'tiered', 'extended'].map((k) => <td key={k} className={r[`${k}_correct`] ? 'ok' : 'no'}>{r[`${k}_answer`] ?? 'None'}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
      <h3 style={{ marginTop: 20 }}>Failure modes (from REPORT.md)</h3>
      <div className="grid2" style={{ marginTop: 10 }}>
        {modes.map(([t, d]) => <div className="tile" key={t}><h3>{t}</h3><p className="hint" style={{ margin: '4px 0 0' }}>{d}</p></div>)}
      </div>
      <h3 style={{ marginTop: 20 }}>Glossary</h3>
      <dl className="gloss">
        <dt>Full context</dt><dd>Scan every turn for the question&apos;s key phrase, take the last match, and pull the value after &ldquo;is&rdquo; or &ldquo;happens to be&rdquo;. A pattern scan, not a model.</dd>
        <dt>Tiered memory</dt><dd>Store facts said as &ldquo;My X is V.&rdquo; when they arrive (later values overwrite), then answer from the store plus the last {W4} turns.</dd>
        <dt>Tiered extended</dt><dd>The same, with two more write-time patterns for the &ldquo;By the way&rdquo; and &ldquo;For the record&rdquo; forms.</dd>
        <dt>Words read</dt><dd>Whitespace-separated words in the text a design reads. A proxy for tokens, not a tokenizer count.</dd>
        <dt>Operations</dt><dd>Turns scanned or store and window reads, counted. A latency proxy; no wall-clock time is measured.</dd>
      </dl>
      <p className="hint" style={{ marginTop: 12 }}>Also: {build.conversations} small hand-built conversations (so the intervals are a floor, not a population estimate), no real dialogue, and no measured comparison with related work. The full review is in <a href={blob('REPORT.md')}>REPORT.md</a>.</p>
    </section>
  );
}

function Reproduce() {
  const hashes = ['results_learn.json', 'results_build.json', 'results_ablations.json', 'results_deep.json'].map((f) => [f, sha(f)]);
  const docs = [
    ['PROPOSAL.md', 'Proposal', 'Question, hypotheses, next cycle (not pre-registered)'],
    ['REPORT.md', 'Report', 'Learn, Build, Deep, ablations, hypotheses scored'],
    ['experiments/2026-11-05-build-design.md', 'Designs', 'Level designs with hand-computed oracles'],
    ['src/ablations.py', 'Ablations', 'Window, write cost, held-out'],
  ];
  return (
    <section id="reproduce" className="card window reveal" data-title="Terminal — python run_*.py">
      <p className="eyebrow">Reproduce it</p>
      <h2>Standard-library Python, seconds to run, <em>byte-identical</em> output.</h2>
      <ol className="steps" style={{ marginTop: 16 }}>
        <li><span className="n">1</span><div><b>Regenerate the four results files and compare</b><div className="hint"><code>python src/make_results.py --check</code></div></div></li>
        <li><span className="n">2</span><div><b>Run the tests</b> ({checks[0]} Learn, {checks[1]} Build and {checks[2]} Deep checks, plus the layout and ablation tests)<div className="hint"><code>python tests/test_smoke.py && python tests/test_learn_memory.py && python tests/test_build_memory.py && python tests/test_deep_memory.py && python tests/test_ablations.py</code></div></div></li>
        <li><span className="n">3</span><div><b>Compare hashes</b> (recorded in REPORT.md)
          <div className="hint">{hashes.map(([f, h]) => <div key={f}><code>{f} {h}</code></div>)}</div></div></li>
      </ol>
      <div className="docs" style={{ marginTop: 20 }}>
        {docs.map(([p, t, d]) => <a key={p} href={blob(p)}><b>{t}</b><small>{d}</small></a>)}
      </div>
    </section>
  );
}
