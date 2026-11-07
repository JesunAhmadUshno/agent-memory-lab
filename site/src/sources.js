// Reads the benchmark inputs straight out of the Python sources, so the site
// never keeps its own copy of the turn texts or questions.
// pyLiteral(src, 'TURNS') finds `TURNS = [ ... ]` and parses it as JSON:
// these literals use double-quoted strings only, so dropping trailing commas is enough.
export function pyLiteral(src, name) {
  const at = src.search(new RegExp(`^${name} = [\\[{]`, 'm'));
  if (at < 0) throw new Error(`${name} not found`);
  const start = src.indexOf(' = ', at) + 3;
  let depth = 0, inStr = false;
  for (let i = start; i < src.length; i++) {
    const c = src[i];
    if (inStr) { if (c === '\\') i++; else if (c === '"') inStr = false; continue; }
    if (c === '"') inStr = true;
    else if (c === '[' || c === '{') depth++;
    else if ((c === ']' || c === '}') && --depth === 0) {
      return JSON.parse(src.slice(start, i + 1).replace(/,(\s*[\]}])/g, '$1'));
    }
  }
  throw new Error(`${name} not closed`);
}

export function loadBenchmark({ memoryPy, buildPy, ablationsPy }) {
  return {
    window: +/^RECENT_WINDOW = (\d+)$/m.exec(memoryPy)[1],
    learn: { turns: pyLiteral(memoryPy, 'TURNS'), questions: pyLiteral(memoryPy, 'QUESTIONS') },
    build: { conversations: pyLiteral(buildPy, 'CONVERSATIONS'), questions: pyLiteral(buildPy, 'QUESTIONS_BUILD') },
    heldout: { turns: pyLiteral(ablationsPy, 'HELDOUT_CONVERSATION'), questions: pyLiteral(ablationsPy, 'HELDOUT_QUESTIONS') },
  };
}
