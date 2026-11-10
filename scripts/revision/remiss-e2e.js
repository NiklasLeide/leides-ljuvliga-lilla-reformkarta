#!/usr/bin/env node
// remiss-e2e.js — Remissläge i webbläsaren (Sprint 14 T5).
// Kräver Playwright (förinstallerat i molnmiljön, ingår inte i CI-sviten).
//   node scripts/revision/remiss-e2e.js [--ut docs/revision/skarmbilder]
// Startar en egen statisk server, låser webbläsarens klocka (page.clock) till ett datum per
// läge och öppnar remissen på reformkortet (karta + reformvy), i tidslinjen och i guidens hjul,
// i desktop (1280 px) och 375 px. Kontrollerar att rätt läge renderas och att inga appfel
// loggas i konsolen. Externa resurser som sandboxen inte når (Cloudflare-analys, typsnitt)
// räknas inte som appfel. Exit 1 vid fel.
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.join(__dirname, '..', '..');
const argUt = process.argv.indexOf('--ut');
const UT = path.join(ROOT, argUt > 0 ? process.argv[argUt + 1] : 'docs/revision/skarmbilder');
const LAGEN = [
  { lage: 'oppnar', klocka: '2026-11-05T12:00:00', text: 'Remiss öppnar 9 november 2026' },
  { lage: 'oppen', klocka: '2026-11-20T12:00:00', text: 'Remiss öppen till och med 20 januari 2027' },
  { lage: 'avslutad', klocka: '2027-02-01T12:00:00', text: 'Remiss avslutad 20 januari 2027' },
];
const VYER = [
  { namn: 'desktop', viewport: { width: 1280, height: 900 }, mobil: false },
  { namn: '375', viewport: { width: 375, height: 812 }, mobil: true },
];
const TYPER = { '.html': 'text/html', '.json': 'application/json', '.png': 'image/png', '.css': 'text/css', '.js': 'text/javascript' };
const EXTERNT = /ERR_TUNNEL|ERR_NAME|ERR_CONNECTION|cloudflareinsights|fonts\.(googleapis|gstatic)/;

function server() {
  return new Promise(res => {
    const s = http.createServer((req, rsp) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': TYPER[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(rsp);
    }).listen(0, () => res(s));
  });
}

// Per sida: öppna remissen och returnera elementet att fotografera.
const SIDOR = {
  async 'index.html'(pg, vy) {
    if (vy.mobil) {
      await pg.evaluate(() => toggleCard('laroplaner'));
      return pg.locator('#list-laroplaner');
    }
    await pg.evaluate(() => selectNode('laroplaner'));
    return pg.locator('#detailPanel');
  },
  async 'reformer.html'(pg, vy) {
    await pg.click('tr[data-id="laroplaner"]');
    return pg.locator(vy.mobil ? '#mobileSidebar' : '#detailPanel');
  },
  async 'tidslinje.html'(pg, vy) {
    await pg.evaluate(() => selectEvent('remiss-skolverket-2026-11-09-laroplaner-svar-laroplaner'));
    return pg.locator(vy.mobil ? '#mobileSidebar' : '#detailPanel');
  },
  async 'guide.html'(pg, vy, l) {
    // navNasta kan vara inaktiverad — klicka bara när den går att använda
    // Hjulets månad för remisspunkten: november före öppning, annars januari (sista svarsdag).
    const slot = l.lage === 'oppnar' ? 3 : 5;
    await pg.click(`[data-test="manad"][data-slot="${slot}"]`);
    for (let i = 0; i < 12 && !(await pg.locator('[data-test="remiss-guide"]').count()); i++) {
      if (await pg.locator('#navNasta').isDisabled()) break;
      await pg.click('#navNasta'); await pg.waitForTimeout(350);
    }
    return pg.locator('#detaljYta');
  },
};

(async () => {
  fs.mkdirSync(UT, { recursive: true });
  const srv = await server();
  const bas = `http://localhost:${srv.address().port}/`;
  const b = await chromium.launch();
  const resultat = []; let fel = 0;
  for (const l of LAGEN) for (const vy of VYER) for (const [sida, oppna] of Object.entries(SIDOR)) {
    // 375 px körs som viewport-bredd utan isMobile-emulering: med isMobile blir tidslinjens layout
    // 1433 px bred redan före T5 (befintligt mobilproblem, se PROJECT_STATUS Sprint 14 T5).
    const ctx = await b.newContext({ viewport: vy.viewport, deviceScaleFactor: 2, hasTouch: vy.mobil });
    const pg = await ctx.newPage();
    pg.setDefaultTimeout(8000);
    await pg.clock.setFixedTime(new Date(l.klocka));
    const konsol = [];
    pg.on('console', m => { if (m.type() === 'error' && !EXTERNT.test(m.text())) konsol.push(m.text()); });
    pg.on('pageerror', e => konsol.push('pageerror: ' + e.message));
    pg.on('requestfailed', () => {}); // externa resurser blockeras av sandboxen — inte appfel
    await pg.goto(bas + sida, { waitUntil: 'networkidle' });
    await pg.waitForTimeout(400);
    let ok = true, notis = '';
    try {
      const el = await oppna(pg, vy, l);
      await pg.waitForTimeout(450);
      const sel = sida === 'guide.html' ? '[data-test="remiss-guide"]' : '[data-test="remiss"]';
      const r = el.locator(sel).first(); // inom det fotograferade elementet (dolda vyer har egna kopior)
      const lage = await r.getAttribute('data-lage');
      const text = await r.innerText();
      if (lage !== l.lage) { ok = false; notis = `läge ${lage}`; }
      if (sida !== 'guide.html' && !text.includes(l.text)) { ok = false; notis += ` saknar "${l.text}"`; }
      if (sida === 'guide.html' && l.lage === 'oppen' && !text.includes('är på remiss till och med den 20 januari 2027')) { ok = false; notis += ' guidetext saknas'; }
      await r.scrollIntoViewIfNeeded();
      const fil = `${l.lage}-${sida.replace('.html', '')}-${vy.namn}.png`;
      await el.screenshot({ path: path.join(UT, fil) });
      notis = notis || fil;
    } catch (e) { ok = false; notis = e.message.split('\n')[0]; }
    if (konsol.length) { ok = false; notis += ' KONSOL: ' + konsol.join(' | '); }
    if (!ok) fel++;
    resultat.push(`${ok ? 'OK ' : 'FEL'} ${l.lage.padEnd(8)} ${vy.namn.padEnd(7)} ${sida.padEnd(15)} konsolfel=${konsol.length} ${notis}`);
    await ctx.close();
  }
  // Fail-loud i webbläsaren: remisser.json med okänt reform_id → console.error, ingen ruta visas.
  {
    const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
    const pg = await ctx.newPage(); pg.setDefaultTimeout(8000);
    const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'remisser.json'), 'utf8'));
    data[0].reform_ids = ['laroplaner', 'finns-inte'];
    await pg.route('**/data/remisser.json*', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify(data) }));
    const konsol = [];
    pg.on('console', m => { if (m.type() === 'error' && !EXTERNT.test(m.text())) konsol.push(m.text()); });
    await pg.goto(bas + 'reformer.html', { waitUntil: 'networkidle' });
    await pg.click('tr[data-id="laroplaner"]'); await pg.waitForTimeout(300);
    const rutor = await pg.locator('#detailPanel [data-test="remiss"]').count();
    const ok = rutor === 0 && konsol.length === 1 && /okänt reform_id "finns-inte"/.test(konsol[0]);
    if (!ok) fel++;
    resultat.push(`${ok ? 'OK ' : 'FEL'} okänt reform_id → console.error=${konsol.length} (${konsol[0] || '—'}), rutor=${rutor}`);
    await ctx.close();
  }
  await b.close(); srv.close();
  console.log(resultat.join('\n'));
  console.log(`${resultat.length - fel}/${resultat.length} OK`);
  process.exit(fel ? 1 : 0);
})();
