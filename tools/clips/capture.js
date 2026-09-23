// Capture the screens for the two social clips: screenshot at 2x plus the
// viewport rect of every callout target. Private text is scrubbed first.
// Run: node tools/clips/capture.js   (writes .design-loop/clips/cap/)
const { chromium } = require('C:/Users/jmarg/.claude/skills/design-loop/node_modules/playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, '../../.design-loop/clips/cap');
const FIX = 'file:///C:/Users/jmarg/work/olimazi-tracker/fixtures/sample-property/';
// The mail page is built from the sample property by make_fixture_pages.py.
const LOCALFIX = 'file:///' + path.join(__dirname, '../../.design-loop/clips/fixture/').split(path.sep).join('/') + '/';

// [id, url, prep(page), targets {name: [text, closestSelector?]}]
const SCENES = [
  ['rm-dash', FIX + 'SchE_Dashboard.html', null, {
    nav_flow: ['Flow', 'a'], bottom: ['SCH. E BOTTOM LINE', 'section,div.card,.panel,article'],
    line3: ['Rents received', 'tr,li,.row,div'], line7: ['Cleaning and maintenance', 'tr,li,.row,div'],
    open: ['RESOLVE HERE OR ON THE ORGANIZER', 'section,details,div.card,.panel,article'] }],
  ['rm-phone', LOCALFIX + 'SchE_Phone.html', null, {
    nav_flow: ['Flow', 'a'], on: ['Phone capture is on', 'div.card'], addr: ['192.168.1.20', 'p'],
    code: ['482913', 'p'], phone: ['Take a photo', 'body'] }],
  ['rm-flow', FIX + 'SchE_Flow.html', null, {
    nav_manage: ['Management', 'a'], floating: ['Floating — needs your answer', 'section,div.card,.panel,article'],
    proposed: ['Proposed rows — one click books', 'h2,h3'], red: ['SAMPLE-P1-01 repair invoice.pdf', 'tr'] }],
  ['rm-manage', FIX + 'SchE_Management.html', null, {
    nav_org: ['Organizer', 'a'], issue: ['AC outdoor unit dead', '.card,article,li,div.issue'],
    wo: ['Replace AC condenser fan motor', '.card,article,li,div'] }],
  ['rm-mail', LOCALFIX + 'SchE_Mail.html', async p => {
      // Served over http the buttons show; from file:// they stay hidden.
      await p.evaluate(() => document.querySelectorAll('button[hidden]').forEach(b => b.hidden = false)); }, {
    nav_org: ['Organizer', 'a'], card: ['Re: AC unit stopped working', 'article'],
    who: ['Last spoke', 'p'], flag: ['money', 'span'], send: ['Send this one', 'button'],
    waiting: ['Waiting for you', 'h2'] }],
  ['rm-org', FIX + 'SchE_Organizer.html', null, {
    export: ['Export preparer package', 'button,a'], qs: ['question(s) unanswered', 'span,b,a'],
    needed: ['Still needed for your preparer (3)', 'section,div.card,.panel,article'] }],

  ['ops-flow', 'http://127.0.0.1:8643/flow', null, {
    tab_review: ['REVIEW', 'a'], firing: ['FIRING NOW', 'section,div.card,.panel,article'],
    drop: ['The Drop', 'a,div'], queue: ['Review queue', 'a,div'], pub: ['Publisher', 'a,div'],
    surfaces: ['Surfaces', 'div'] }],
  ['ops-queue', 'http://127.0.0.1:8766/', null, {
    how: ['HOW THIS WORKS', 'section,div,pre,aside'], needs: ['Needs my click', 'a,button'],
    pending: ['Pending', 'a,button'], nav_slides: ['Slides', 'a'] }],
  ['ops-slides', 'http://127.0.0.1:8766/slides', async p => {
      await p.selectOption('#tw-deck', '2026-09-01/orange-creamsicle.json'); await p.waitForTimeout(2500); }, {
    tab_ops: ['OPS', 'a'], lines: ['lines', 'label,div,span'], canvas: ['Slide 1 of', 'div'],
    thumbs: ['1 · cover', 'div,button,a'], live: ['live', 'label'] }],
  // Same screen after the click on "guessing": the chip is on and the live
  // rebuild has painted the word red. The clip swaps to it at the click.
  ['ops-slides-b', 'http://127.0.0.1:8766/slides', async p => {
      await p.selectOption('#tw-deck', '2026-09-01/orange-creamsicle.json'); await p.waitForTimeout(2500);
      await p.locator('#p-accents .tw-chip', { hasText: /^guessing$/ }).click();
      await p.waitForTimeout(800);
      await p.waitForFunction(() => !document.querySelector('.tw-grid').classList.contains('tw-busy'), null, { timeout: 60000 });
      await p.waitForTimeout(1500); }, {
    lines: ['lines', 'label,div,span'], canvas: ['Slide 1 of', 'div'] }],
  ['ops-pulse', 'http://127.0.0.1:8643/pulse', null, {
    nav_brain: ['Second brain', 'a'], ninety: ['NINETY DAYS', 'section,div.card,.panel,article'],
    hourly: ['THE LAST SEVEN DAYS, HOUR BY HOUR', 'section,div.card,.panel,article'] }],
  ['ops-graph', 'http://127.0.0.1:8643/graph', null, {
    nav_lp: ['Launchpad', 'a'], files: ['FILES', 'div'], unfiled: ['UNFILED', 'div'] }],
  ['ops-lp', 'http://127.0.0.1:8643/', async p => {
      await p.evaluate(() => { const h = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && /THE SITE, SECTION BY SECTION/i.test(e.textContent)); window.scrollTo(0, h.getBoundingClientRect().top + scrollY - 60); });
      await p.waitForTimeout(600); }, {
    site: ['refuses to claim success', 'p,div'], drift: ['DRIFT', 'div.card,article,section,div'],
    built: ['Hero spec', 'div.card,article,section,div'] }],
  ['ops-skill', 'http://127.0.0.1:8643/', async p => {
      await p.evaluate(() => { const c = [...document.querySelectorAll('#skills .card')].find(e => /^Finder$/.test((e.querySelector('b') || {}).textContent || '')); window.scrollTo(0, c.getBoundingClientRect().top + scrollY - 250); });
      await p.waitForTimeout(600); }, {
    finder: ['Finder', '.card'], grid: ['what hooks in', '.card'], run: ['RUN', 'button'], nav_pulse: ['Pulse', 'a'] }],
];

// Private words never reach a frame: the owner's name, machine paths,
// personal-file node labels in the graph. The word list lives outside the
// repo in .design-loop/clips/scrub.json: {hide, replace: [[re, flags, to]], leaks, sourceLeaks}.
const CFG = JSON.parse(fs.readFileSync(path.join(__dirname, '../../.design-loop/clips/scrub.json'), 'utf8'));
const SCRUB = (cfg) => {
  const hide = new RegExp(cfg.hide, 'i'), reps = cfg.replace.map(([r, f, to]) => [new RegExp(r, f), to]);
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = []; while (w.nextNode()) nodes.push(w.currentNode);
  for (const n of nodes) {
    if (hide.test(n.nodeValue.trim())) { n.nodeValue = ''; continue; }
    n.nodeValue = reps.reduce((t, [re, to]) => t.replace(re, to), n.nodeValue);
  }
  document.querySelectorAll('svg text').forEach(e => { if (hide.test(e.textContent.trim())) e.textContent = ''; });
};

const FIND = `(targets) => {
  const out = {};
  const all = [...document.querySelectorAll('body *')].filter(e => e.offsetParent !== null || e.tagName === 'BODY');
  for (const [name, [text, sel]] of Object.entries(targets)) {
    const lo = text.toLowerCase();
    const hits = all.filter(e => !e.closest('svg') && ([...e.childNodes].some(c => c.nodeType === 3 && c.nodeValue.toLowerCase().includes(lo)) || String(e.value || '').toLowerCase().includes(lo)));
    let el = hits.find(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.top > -200 && r.top < innerHeight + 200; }) || hits[0];
    if (!el) { out[name] = null; continue; }
    if (sel) {
      const up = el.closest(sel);
      // climb only if the container is not the whole page column
      if (up && up.getBoundingClientRect().height < innerHeight * 0.95) el = up;
    }
    const r = el.getBoundingClientRect();
    out[name] = { x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height), tag: el.tagName };
  }
  return out;
}`;

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();
  const only = process.argv[2];
  for (const [id, url, prep, targets] of SCENES) {
    if (only && !id.startsWith(only)) continue;
    const p = await b.newPage({ viewport: { width: 1440, height: 1008 }, deviceScaleFactor: 2 });
    try {
      await p.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
      await p.waitForTimeout(id === 'ops-flow' ? 6000 : 2500);
      if (prep) await prep(p);
      await p.evaluate(SCRUB, CFG);
      await p.waitForTimeout(300);
      const rects = await p.evaluate(new Function('return ' + FIND)(), targets);
      const txt = await p.evaluate(() => document.body.innerText);
      const html = await p.content();
      const leaks = CFG.leaks.filter(s => txt.includes(s)).concat(CFG.sourceLeaks.filter(s => !txt.includes(s) && html.includes(s)).map(s => s + '(source-only)'));
      await p.screenshot({ path: path.join(OUT, id + '.png') });
      fs.writeFileSync(path.join(OUT, id + '.json'), JSON.stringify(rects, null, 1));
      console.log(id, 'leaks:', leaks.join(',') || 'none', JSON.stringify(rects));
    } catch (e) { console.log(id, 'ERR', e.message.slice(0, 120)); }
    await p.close();
  }
  await b.close();
})();
