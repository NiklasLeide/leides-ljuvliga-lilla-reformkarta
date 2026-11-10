#!/usr/bin/env node
// render-test.js — renderingstest (Sprint 15, automatfilen regel 6 + CI på PR).
// Startar en statisk server över repots arbetskatalog och laddar alla publika sidor i Chromium
// (Playwright). Godkänt = varje sida svarar 200 och loggar 0 appfel i konsolen.
// Externa resurser som miljön inte når (Cloudflare-analys, typsnitt) räknas inte: resursens adress
// avgör (allt som inte är localhost är externt) — felkoden skiljer sig mellan sandbox och runner.
//   node scripts/revision/render-test.js [--rot <katalog>]
// Exit 0 = alla sidor gröna, 1 = minst ett appfel.
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const argRot = process.argv.indexOf('--rot');
const ROOT = path.resolve(argRot > 0 ? process.argv[argRot + 1] : path.join(__dirname, '..', '..'));
const SIDOR = ['index.html', 'reformer.html', 'uppdrag.html', 'tidslinje.html', 'utredningar.html', 'guide.html', 'guide-alla.html', 'andringar.html'];
const TYPER = { '.html': 'text/html', '.json': 'application/json', '.png': 'image/png', '.css': 'text/css', '.js': 'text/javascript' };

function arAppfel(m) {
  if (m.type() !== 'error') return false;
  const url = (m.location && m.location().url) || '';
  if (/^Failed to load resource/.test(m.text()) && url && !/^https?:\/\/(localhost|127\.0\.0\.1)(:|\/)/.test(url)) return false;
  return !/ERR_TUNNEL|ERR_NAME|ERR_CONNECTION|cloudflareinsights|fonts\.(googleapis|gstatic)/.test(m.text());
}

(async () => {
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
  let fel = 0;
  for (const sida of SIDOR) {
    const pg = await b.newPage({ viewport: { width: 1280, height: 900 } });
    const appfel = [];
    pg.on('console', m => { if (arAppfel(m)) appfel.push(m.text()); });
    pg.on('pageerror', e => appfel.push('pageerror: ' + e.message));
    let status = 0;
    try {
      const r = await pg.goto(bas + sida, { waitUntil: 'networkidle', timeout: 30000 });
      status = r ? r.status() : 0;
      await pg.waitForTimeout(500);
    } catch (e) { appfel.push('laddning: ' + e.message.split('\n')[0]); }
    const ok = status === 200 && appfel.length === 0;
    if (!ok) fel++;
    console.log(`${ok ? 'OK ' : 'FEL'} ${sida.padEnd(17)} HTTP ${status} appfel=${appfel.length}${appfel.length ? ' — ' + appfel.join(' | ') : ''}`);
    await pg.close();
  }
  await b.close(); srv.close();
  console.log(`${SIDOR.length - fel}/${SIDOR.length} sidor gröna`);
  process.exit(fel ? 1 : 0);
})().catch(e => { console.error('render-test FEL:', e); process.exit(1); });
