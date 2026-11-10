// stampel.test.js — färskhetsstämpeln (Sprint 15 T7). Kör: node --test scripts/revision/stampel.test.js
// Stämpelskriptet finns i alla publika sidor (DEC-001: ingen delad JS) och ska vara byte-identiskt;
// varje sidfot ska ha både [data-fresh] och [data-kontroll].
'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.join(__dirname, '..', '..');
const SIDOR = ['index.html', 'reformer.html', 'uppdrag.html', 'tidslinje.html', 'utredningar.html', 'guide.html', 'guide-alla.html', 'andringar.html'];
const blocket = (s) => (/\/\* Färskhetsstämpel \(Sprint 12 T3, utökad Sprint 15 T7\)[\s\S]*?\}\)\(\);/.exec(s) || [null])[0];

test('stämpelskriptet är byte-identiskt i alla åtta sidor', () => {
  const ref = blocket(fs.readFileSync(path.join(ROOT, SIDOR[0]), 'utf8'));
  assert.ok(ref, 'blocket saknas i ' + SIDOR[0]);
  for (const s of SIDOR) assert.equal(blocket(fs.readFileSync(path.join(ROOT, s), 'utf8')), ref, s);
});

test('varje sidfot har [data-fresh] och [data-kontroll]', () => {
  for (const s of SIDOR) {
    const html = fs.readFileSync(path.join(ROOT, s), 'utf8');
    const fot = html.slice(html.indexOf('<footer'), html.indexOf('</footer>'));
    assert.match(fot, /<span data-fresh><\/span><span data-kontroll><\/span>/, s);
  }
});

test('stämpellogiken: båda datumen, bara uppdaterad, och ogiltigt datum ger ingen text', async () => {
  const src = blocket(fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8'));
  async function kor(meta) {
    const el = { fresh: { textContent: '' }, kontroll: { textContent: '' } };
    const document = { querySelectorAll: (q) => [q === '[data-fresh]' ? el.fresh : el.kontroll] };
    const fetch = async () => ({ ok: true, json: async () => meta });
    new Function('fetch', 'document', src)(fetch, document);
    await new Promise(r => setTimeout(r, 0)); await new Promise(r => setTimeout(r, 0));
    return [el.fresh.textContent, el.kontroll.textContent];
  }
  assert.deepEqual(await kor({ senast_uppdaterad: '2026-11-10', senast_kontrollerad: '2026-11-12' }),
    [' · Senast uppdaterad 10 november 2026', ' · Senast avstämd mot riksdagens öppna data 12 november 2026']);
  assert.deepEqual(await kor({ senast_uppdaterad: '2026-11-10' }), [' · Senast uppdaterad 10 november 2026', '']);
  assert.deepEqual(await kor({ senast_uppdaterad: '2026-11-10', senast_kontrollerad: 'igår' }), [' · Senast uppdaterad 10 november 2026', '']);
});

test('T8b: texten är "Senast avstämd mot riksdagens öppna data" — "Senast kontrollerad" förekommer inte på någon sida', () => {
  for (const s of SIDOR) {
    const html = fs.readFileSync(path.join(ROOT, s), 'utf8');
    assert.match(html, /Senast avstämd mot riksdagens öppna data /, s);
    assert.doesNotMatch(html, /Senast kontrollerad/, s);
  }
});
