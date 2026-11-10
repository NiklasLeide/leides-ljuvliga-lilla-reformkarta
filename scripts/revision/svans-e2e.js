#!/usr/bin/env node
// svans-e2e.js — Sprint 15 T8 (svansen) i webbläsaren. Kräver Playwright.
//   node scripts/revision/svans-e2e.js [--ut docs/automat/skarmbilder]
// (1) tidslinje.html håller viewportbredden med ÄKTA mobilemulering (isMobile) och tidsaxeln är sticky.
// (2) guide-alla.html visar remissen i rätt läge.
// (3) Aktuellt-rad på index/reformer/guide i lägena öppnar och öppen (saknas i avslutad); markering "Remiss"
//     på laroplaner/tioarig i kartan (noder + mobilens listkort) och i reformlistan; länken leder till ett
//     kort där remissrutan syns; flera remisser sorteras på sista svarsdag. Desktop och 375 px (isMobile),
//     låst klocka per läge, 0 appfel. Skärmbilder av aktuellt-raden.
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.join(__dirname, '..', '..');
const argUt = process.argv.indexOf('--ut');
const UT = path.resolve(ROOT, argUt > 0 ? process.argv[argUt + 1] : 'docs/automat/skarmbilder');
const LAGEN = [
  { lage: 'oppnar', klocka: '2026-11-05T12:00:00', status: 'Remiss öppnar 9 november 2026' },
  { lage: 'oppen', klocka: '2026-11-20T12:00:00', status: 'Remiss öppen till och med 20 januari 2027' },
  { lage: 'avslutad', klocka: '2027-02-01T12:00:00', status: null },
];
const VYER = [
  { namn: 'desktop', ctx: { viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 } },
  { namn: '375', ctx: { viewport: { width: 375, height: 812 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true } },
];
const TITEL = 'Förslag på nya läroplaner och kursplaner för grundskolan, anpassade grundskolan, specialskolan och sameskolan';
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
  const rapportera = (ok, txt) => { if (!ok) fel++; rader.push(`${ok ? 'OK ' : 'FEL'} ${txt}`); };

  async function sida(vy, klocka, url, setup) {
    const ctx = await b.newContext(vy.ctx);
    const pg = await ctx.newPage(); pg.setDefaultTimeout(8000);
    if (klocka) await pg.clock.setFixedTime(new Date(klocka));
    if (setup) await setup(pg);
    const appfel = [];
    pg.on('console', m => { if (arAppfel(m)) appfel.push(m.text()); });
    pg.on('pageerror', e => appfel.push('pageerror: ' + e.message));
    await pg.goto(bas + url, { waitUntil: 'networkidle' });
    await pg.waitForTimeout(400);
    return { ctx, pg, appfel };
  }

  // ---- (1) tidslinje med äkta mobilemulering
  {
    const { ctx, pg, appfel } = await sida(VYER[1], '2026-11-20T12:00:00', 'tidslinje.html');
    const r = await pg.evaluate(() => ({ iw: innerWidth, cw: document.documentElement.clientWidth }));
    await pg.evaluate(() => window.scrollTo(0, 900)); await pg.waitForTimeout(300);
    const top = await pg.evaluate(() => Math.round(document.querySelector('.gantt-header').getBoundingClientRect().top));
    await pg.evaluate(() => window.scrollTo(600, 900)); await pg.waitForTimeout(300);
    const sx = await pg.evaluate(() => window.scrollX);
    rapportera(r.iw === 375 && top < 100 && sx > 0 && !appfel.length,
      `(1) tidslinje isMobile 375: innerWidth=${r.iw} (krav 375), tidsaxel top=${top} efter skroll (sticky), scrollX=${sx} (sidled går), appfel=${appfel.length}`);
    await ctx.close();
  }

  // ---- (2) guide-alla visar remissen
  for (const l of LAGEN) for (const vy of VYER) {
    const { ctx, pg, appfel } = await sida(vy, l.klocka, 'guide-alla.html');
    const ruta = pg.locator('#remisser [data-test="remiss"]');
    const n = await ruta.count(), lage = n ? await ruta.first().getAttribute('data-lage') : null;
    rapportera(n === 1 && lage === l.lage && !appfel.length, `(2) guide-alla ${l.lage.padEnd(8)} ${vy.namn.padEnd(7)} remissruta=${n} läge=${lage} appfel=${appfel.length}`);
    await ctx.close();
  }

  // ---- (3) aktuellt-rad, markering, länk
  for (const l of LAGEN) for (const vy of VYER) for (const s of ['index.html', 'reformer.html', 'guide.html']) {
    const { ctx, pg, appfel } = await sida(vy, l.klocka, s);
    const radEl = pg.locator('#remissAktuellt [data-test="remiss-aktuellt-rad"]');
    const antal = await radEl.count();
    const notis = [];
    let ok = !appfel.length;
    if (l.status) {
      const text = antal ? (await radEl.first().innerText()).replace(/\s+/g, ' ').trim() : '';
      if (antal !== 1 || text !== `${l.status}: ${TITEL}`) { ok = false; notis.push(`rad="${text}" (${antal})`); }
      if (!(await radEl.first().isVisible())) { ok = false; notis.push('rad ej synlig'); }
    } else if (antal !== 0) { ok = false; notis.push(`rad finns i avslutad (${antal})`); }
    // markering
    const sel = s === 'reformer.html' ? (id) => `tr[data-id="${id}"] [data-test="remiss-markering"]`
      : s === 'index.html' ? (id) => (vy.namn === '375' ? `#list-${id} [data-test="remiss-markering"]` : `#node-${id} [data-test="remiss-markering"]`) : null;
    if (sel) for (const id of ['laroplaner', 'tioarig']) {
      const m = await pg.locator(sel(id)).count();
      if ((l.status ? 1 : 0) !== m) { ok = false; notis.push(`markering ${id}=${m}`); }
    }
    if (sel) { const ovr = await pg.locator(sel('betyg')).count(); if (ovr) { ok = false; notis.push('markering på betyg'); } }
    // skärmbild av raden (oppen + oppnar)
    if (l.status && antal) {
      const fil = `aktuellt-${l.lage}-${s.replace('.html', '')}-${vy.namn}.png`;
      await pg.evaluate(() => window.scrollTo(0, 0));
      const hdr = await pg.locator('header').boundingBox(), akt = await pg.locator('#remissAktuellt').boundingBox();
      await pg.screenshot({ path: path.join(UT, fil), clip: { x: 0, y: hdr.y, width: vy.ctx.viewport.width, height: Math.min(akt.y + akt.height - hdr.y + 70, 520) } });
      notis.push(fil);
    }
    // länken leder till ett kort med synlig remissruta
    if (l.status && antal && s !== 'reformer.html') {
      await radEl.first().click();
      await pg.waitForURL(/reformer\.html\?reform=laroplaner/); await pg.waitForLoadState('networkidle'); await pg.waitForTimeout(500);
      const kort = vy.namn === '375' ? '#mobileSidebar [data-test="remiss"]' : '#detailPanel [data-test="remiss"]';
      const syns = await pg.locator(kort).first().isVisible().catch(() => false);
      if (!syns) { ok = false; notis.push('länk: remissruta syns inte'); } else notis.push('länk → kort med remissruta');
    }
    rapportera(ok, `(3) ${l.lage.padEnd(8)} ${vy.namn.padEnd(7)} ${s.padEnd(13)} appfel=${appfel.length} ${notis.join(' · ')}`);
    await ctx.close();
  }

  // ---- (3c) flera öppna remisser sorteras på sista svarsdag
  {
    const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'remisser.json'), 'utf8'));
    const tidig = { ...data[0], id: 'prov-tidig', titel: 'Remiss: Provremiss med tidigare svarsdag', oppnar: '2026-10-01', svar_senast: '2026-12-15', reform_ids: ['betyg'] };
    const { ctx, pg, appfel } = await sida(VYER[0], '2026-11-20T12:00:00', 'reformer.html',
      (p) => p.route('**/data/remisser.json*', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify([data[0], tidig]) })));
    const hrefs = await pg.locator('#remissAktuellt [data-test="remiss-aktuellt-rad"]').evaluateAll(a => a.map(x => x.getAttribute('href')));
    const okSort = hrefs.length === 2 && /reform=betyg$/.test(hrefs[0]) && /reform=laroplaner$/.test(hrefs[1]);
    await pg.evaluate(() => window.scrollTo(0, 0));
    const hdr = await pg.locator('header').boundingBox(), akt = await pg.locator('#remissAktuellt').boundingBox();
    await pg.screenshot({ path: path.join(UT, 'aktuellt-tva-remisser-reformer-desktop.png'), clip: { x: 0, y: hdr.y, width: 1280, height: akt.y + akt.height - hdr.y + 20 } });
    rapportera(okSort && !appfel.length, `(3c) två öppna remisser: ordning ${hrefs.join(' , ')} (krav: tidigast svarsdag först), appfel=${appfel.length}`);
    await ctx.close();
  }

  await b.close(); srv.close();
  console.log(rader.join('\n'));
  console.log(`${rader.length - fel}/${rader.length} OK`);
  process.exit(fel ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
