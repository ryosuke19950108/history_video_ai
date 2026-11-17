// Text-on-text overlap check for a film page (window.TBOXES(t) → the text boxes drawn at t, subtitles included).
//   node tools/check_overlap.mjs <film_dir> [--lib ~/lemo-opuscar]
// Samples every scene at 3 points away from its transitions (after the reveals, middle, just before the end).
// Exit 1 when two different texts overlap by more than 3 px both ways.
import path from 'path'; import fs from 'fs'; import os from 'os';
const args = process.argv.slice(2), li = args.indexOf('--lib'), LIB = li >= 0 ? args.splice(li, 2)[1] : (process.env.LIB || path.join(os.homedir(), 'lemo-opuscar'));
const dir = path.resolve(args[0]);
const { openDemo, closeServer } = await import(path.join(LIB, 'core/render/page.mjs'));
const film = JSON.parse(fs.readFileSync(path.join(dir, 'film.json'), 'utf8'));
const { browser, page } = await openDemo(dir, {});
const bad = [];
for (const s of film.scenes) {
  const d = s.t1 - s.t0, ts = [Math.min(s.t0 + 2.2, s.t1 - .5), s.t0 + d / 2, s.t1 - .45].filter(t => t > s.t0 + .4 && t < s.t1 - .4);
  for (const t of ts) {
    const B = await page.evaluate(t => window.TBOXES(t), t);
    for (let i = 0; i < B.length; i++) for (let j = i + 1; j < B.length; j++) {
      const a = B[i], b = B[j]; if (a.text === b.text && Math.abs(a.x0 - b.x0) < 1 && Math.abs(a.y0 - b.y0) < 1) continue;
      const ox = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), oy = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
      if (ox > 3 && oy > 3) { const k = `${s.id}|${a.text}|${b.text}`; if (!bad.some(x => x.k === k)) bad.push({ k, id: s.id, t: t.toFixed(1), a: a.text, b: b.text }); }
    }
  }
}
await browser.close(); closeServer();
for (const b of bad) console.log(`NG ${b.id} @${b.t}s  「${b.a.slice(0, 24)}」×「${b.b.slice(0, 24)}」`);
console.log(bad.length ? `${bad.length} overlaps` : 'OK no text overlaps'); process.exit(bad.length ? 1 : 0);
