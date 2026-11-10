#!/usr/bin/env node
// stampel-e2e.js — sidfotens två datum i webbläsaren (Sprint 15 T7). Kräver Playwright.
//   node scripts/revision/stampel-e2e.js [--ut docs/automat/skarmbilder]
// meta.json ersätts via route (automatfilen sätter senast_kontrollerad först vid första skarpa körningen):
//   (1) båda fälten → varje sidas sidfot visar "Senast uppdaterad …" och "Senast kontrollerad …";
//   (2) bara senast_uppdaterad → ingen kontrolltext (tyst fallback).
// Alla åtta sidor, desktop och 375 px, 0 appfel. Skärmbilder av sidfoten (index + guide) i båda bredderna.
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.join(__dirname, '..', '..');
const argUt = process.argv.indexOf('--ut');
const UT = path.resolve(ROOT, argUt > 0 ? process.argv[argUt + 1] : 'docs/automat/skarmbilder');
const SIDOR = ['index.html', 'reformer.html', 'uppdrag.html', 'tidslinje.html', 'utredningar.html', 'guide.html', 'guide-alla.html', 'andringar.html'];
const VYER = [{ namn: 'desktop', viewport: { width: 1280, height: 900 } }, { namn: '375', viewport: { width: 375, height: 812 } }];
const TYPER = { '.html': 'text/html', '.json': 'application/json', '.png': 'image/png' };
function arAppfel(m) {
  if (m.type() !== 'error') return false;
  const url = (m.location && m.location().url) || '';
  if (/^Failed to load resource/.test(m.text()) && url && !/^https?:\/\/(localhost|127\.0\.0\.1)(:|\/)/.test(url)) return false;
  return !/ERR_TUNNEL|ERR_NAME|ERR_CONNECTION|cloudflareinsights|fonts\.(googleapis|gstatic)/.test(m.text());
}

(async () => {
  fs.mkdirSync(UT, { recursive: true });
  const srv = await new Promise(res => {
    const s = http.createServer((req, rsp) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': TYPER[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(rsp);
    }).listen(0, () => res(s));
  });
  const bas = `http://localhost:${srv.address().port}/`;
  const b = await chromium.launch();
  const rader = []; let fel = 0;
  const fall = [
    { namn: 'båda', meta: { senast_uppdaterad: '2026-11-10', senast_kontrollerad: '2026-11-12' }, ska: ['Senast uppdaterad 10 november 2026', 'Senast kontrollerad 12 november 2026'], skaInte: [] },
    { namn: 'bara uppdaterad', meta: { senast_uppdaterad: '2026-11-10' }, ska: ['Senast uppdaterad 10 november 2026'], skaInte: ['Senast kontrollerad'] },
  ];
  for (const fl of fall) for (const vy of VYER) for (const sida of SIDOR) {
    const ctx = await b.newContext({ viewport: vy.viewport, deviceScaleFactor: 2 });
    const pg = await ctx.newPage(); pg.setDefaultTimeout(8000);
    await pg.route('**/data/meta.json*', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify(fl.meta) }));
    const appfel = [];
    pg.on('console', m => { if (arAppfel(m)) appfel.push(m.text()); });
    pg.on('pageerror', e => appfel.push('pageerror: ' + e.message));
    await pg.goto(bas + sida, { waitUntil: 'networkidle' });
    await pg.waitForTimeout(300);
    const fot = pg.locator('footer').first();
    const text = (await fot.innerText()).replace(/\s+/g, ' ');
    const saknas = fl.ska.filter(t => !text.includes(t)), finns = fl.skaInte.filter(t => text.includes(t));
    const ok = !saknas.length && !finns.length && !appfel.length;
    if (!ok) fel++;
    let bild = '';
    if (fl.namn === 'båda' && (sida === 'index.html' || sida === 'guide.html')) {
      bild = `stampel-${sida.replace('.html', '')}-${vy.namn}.png`;
      await fot.scrollIntoViewIfNeeded();
      await fot.screenshot({ path: path.join(UT, bild) });
    }
    rader.push(`${ok ? 'OK ' : 'FEL'} ${fl.namn.padEnd(15)} ${vy.namn.padEnd(7)} ${sida.padEnd(17)} appfel=${appfel.length}${saknas.length ? ' saknar: ' + saknas.join(', ') : ''}${finns.length ? ' ska inte finnas: ' + finns.join(', ') : ''} ${bild}`);
    await ctx.close();
  }
  await b.close(); srv.close();
  console.log(rader.join('\n'));
  console.log(`${rader.length - fel}/${rader.length} OK`);
  process.exit(fel ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
