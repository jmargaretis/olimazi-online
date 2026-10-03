// Render a clip frame by frame and encode with ffmpeg.
// node tools/clips/render.js rm            -> assets/clip-rm.mp4
// node tools/clips/render.js rm --wide     -> landscape cut for the site cards
// node tools/clips/render.js rm --stills 5 8 20   -> .design-loop/clips/stills/
const { chromium } = require('C:/Users/jmarg/.claude/skills/design-loop/node_modules/playwright');
const { spawn } = require('child_process'), path = require('path'), fs = require('fs');
const clip = process.argv[2] || 'rm', si = process.argv.indexOf('--stills'), wide = process.argv.includes('--wide');
const VW = wide ? 1600 : 1080, VH = wide ? 1150 : 1350, SFX = wide ? '-wide' : '';
// A clip with its own stage-<clip>.html uses it (os, os-appstore); the others share stage.html.
const STAGE = 'file:///' + path.join(__dirname, fs.existsSync(path.join(__dirname, `stage-${clip}.html`)) ? `stage-${clip}.html` : 'stage.html').split(path.sep).join('/') + '?clip=' + clip + (wide ? '&wide=1' : '');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: 1 });
  await p.goto(STAGE); await p.evaluate(() => window.ready);
  const { fps, len } = await p.evaluate(() => window.CLIP || ({ fps: CLIPS[new URLSearchParams(location.search).get('clip')].fps, len: CLIPS[new URLSearchParams(location.search).get('clip')].len }));
  if (si > 0) {
    const dir = path.join(__dirname, '../../.design-loop/clips/stills'); fs.mkdirSync(dir, { recursive: true });
    for (const t of process.argv.slice(si + 1).map(Number)) {
      await p.evaluate(t => window.render(t), t); await p.waitForTimeout(60);
      await p.screenshot({ path: path.join(dir, `${clip}${SFX}-${t}.png`) });
    }
    await b.close(); return;
  }
  const out = path.join(__dirname, '../../.design-loop/clips', `clip-${clip}${SFX}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const N = Math.round(len * fps);
  for (let f = 0; f < N; f++) {
    await p.evaluate(t => window.render(t), f / fps);
    const buf = await p.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(clip, f, '/', N);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  console.log('wrote', out);
})();
