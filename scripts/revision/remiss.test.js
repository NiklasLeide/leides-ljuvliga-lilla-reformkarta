// remiss.test.js — Remissläge (Sprint 14 T5). Kör: node --test scripts/revision/remiss.test.js
//
// Logiken ligger som ett <remiss-lib>-block i fyra självständiga sidor (DEC-001: ingen delad
// JS-fil). Testet (1) extraherar blocket ur alla fyra och kräver att de är byte-identiska —
// så kopiorna kan inte glida isär tyst — och (2) testar logiken med STYRBART datum:
// remissStatus tar dagens datum som argument, och remissIdag testas med en fejkad Date.

'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(__dirname, '..', '..');
const SIDOR = ['index.html', 'reformer.html', 'tidslinje.html', 'guide.html', 'guide-alla.html'];
const START = '// <remiss-lib>';
const SLUT = '// </remiss-lib>';

function block(sida) {
  const s = fs.readFileSync(path.join(ROOT, sida), 'utf8');
  const i = s.indexOf(START), j = s.indexOf(SLUT);
  assert.ok(i >= 0 && j > i, `${sida}: <remiss-lib>-blocket saknas`);
  assert.equal(s.indexOf(START, i + 1), -1, `${sida}: fler än ett <remiss-lib>-block`);
  return s.slice(i, j + SLUT.length);
}

// Laddar blocket som moduler; fetch/console/Date kan injiceras för att styra miljön.
function ladda({ fetch = undefined, console: kons = console, Date: D = Date } = {}) {
  const src = block('index.html');
  const fn = new Function('fetch', 'console', 'Date', `${src}
    return { remissStatus, remissNastaSteg, remissValidera, remissGiltiga, remisserForReform,
             remissKortHtml, remissDatumText, remissIdag, remissLadda };`);
  return fn(fetch, kons, D);
}

const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'remisser.json'), 'utf8'));
const REFORM_IDS = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'reforms.json'), 'utf8')).map(r => r.id);
const R = DATA[0];

test('blocket är byte-identiskt i alla fem sidor', () => {
  const ref = block(SIDOR[0]);
  for (const s of SIDOR.slice(1)) assert.equal(block(s), ref, `${s} avviker från ${SIDOR[0]}`);
});

test('läge 1 — före öppning: "Remiss öppnar {datum}"', () => {
  const L = ladda();
  const s = L.remissStatus(R, '2026-11-08');
  assert.equal(s.lage, 'oppnar');
  assert.equal(s.text, 'Remiss öppnar 9 november 2026');
});

test('läge 2 — öppen (inkl. första och sista dagen): "Remiss öppen till och med {datum}"', () => {
  const L = ladda();
  for (const idag of ['2026-11-09', '2026-12-24', '2027-01-20']) {
    const s = L.remissStatus(R, idag);
    assert.equal(s.lage, 'oppen', idag);
    assert.equal(s.text, 'Remiss öppen till och med 20 januari 2027');
  }
});

test('läge 3 — dagen efter sista svarsdag: "Remiss avslutad {datum}" + nästa steg', () => {
  const L = ladda();
  const s = L.remissStatus(R, '2027-01-21');
  assert.equal(s.lage, 'avslutad');
  assert.equal(s.text, 'Remiss avslutad 20 januari 2027');
  assert.equal(L.remissNastaSteg(R),
    'Skolverket lämnar omarbetade förslag till regeringen 14 maj 2027. Tillämpning från höstterminen 2028.');
});

test('remissIdag styrs av klockan (fejkad Date) och ger lokalt YYYY-MM-DD', () => {
  class FejkDate extends Date { constructor(...a) { super(...(a.length ? a : [2027, 0, 21, 12, 0, 0])); } }
  const L = ladda({ Date: FejkDate });
  assert.equal(L.remissIdag(), '2027-01-21');
  assert.equal(L.remissStatus(R, L.remissIdag()).lage, 'avslutad');
});

test('reformkortets ruta: rätt läge, länkar bara till Skolverket, inga svarsinstruktioner', () => {
  const L = ladda();
  for (const [idag, lage] of [['2026-11-01', 'oppnar'], ['2026-11-20', 'oppen'], ['2027-02-01', 'avslutad']]) {
    const html = L.remissKortHtml(R, idag);
    assert.match(html, new RegExp(`data-lage="${lage}"`));
    const hrefs = [...html.matchAll(/href="([^"]+)"/g)].map(m => m[1]);
    assert.ok(hrefs.length >= 2);
    for (const h of hrefs) assert.match(h, /^https:\/\/www\.skolverket\.se\//, h);
    assert.doesNotMatch(html, /@|ämnesrad|e-post|mailto/i);
  }
});

test('data/remisser.json validerar mot reforms.json (0 fel)', () => {
  const L = ladda();
  assert.deepEqual(L.remissValidera(DATA, REFORM_IDS), []);
  assert.equal(L.remissGiltiga(DATA, REFORM_IDS).length, DATA.length);
  assert.deepEqual(L.remisserForReform(DATA, 'tioarig').map(r => r.id), [R.id]);
  assert.deepEqual(L.remisserForReform(DATA, 'betyg'), []);
});

test('okänt reform_id ger fel och remissen visas inte', () => {
  const L = ladda();
  const fel = { ...R, id: 'test-fel', reform_ids: ['laroplaner', 'finns-inte'] };
  const f = L.remissValidera([R, fel], REFORM_IDS);
  assert.equal(f.length, 1);
  assert.match(f[0], /okänt reform_id "finns-inte"/);
  assert.deepEqual(L.remissGiltiga([R, fel], REFORM_IDS).map(r => r.id), [R.id]);
});

test('remissLadda loggar fel med console.error (fail-loud) och returnerar bara giltiga', async () => {
  const loggat = [];
  const kons = { error: (...a) => loggat.push(a.join(' ')) };
  const fejkFetch = async () => ({ ok: true, json: async () => [R, { ...R, id: 'x', reform_ids: ['finns-inte'] }] });
  const L = ladda({ fetch: fejkFetch, console: kons });
  const ut = await L.remissLadda('data/remisser.json', REFORM_IDS);
  assert.deepEqual(ut.map(r => r.id), [R.id]);
  assert.equal(loggat.length, 1);
  assert.match(loggat[0], /Remissläge: Remiss x: okänt reform_id "finns-inte"/);
});

test('remissLadda med giltig data loggar inget', async () => {
  const loggat = [];
  const L = ladda({ fetch: async () => ({ ok: true, json: async () => DATA }), console: { error: (...a) => loggat.push(a) } });
  await L.remissLadda('x', REFORM_IDS);
  assert.equal(loggat.length, 0);
});

// ---------------------------- Sprint 15 T8 punkt 3 -----------------------------
function laddaT8() {
  const fn = new Function(`${block('index.html')}
    return { remissAktuella, remissTitelUtanLedord, remissAktuelltHtml, remissMarkering };`);
  return fn();
}
test('aktuellt-rad: "{statusrubrik}: {titel utan ledordet Remiss:}" med länk till första reform_id, i öppnar och öppen', () => {
  const L = laddaT8();
  for (const [idag, lage, status] of [['2026-11-01', 'oppnar', 'Remiss öppnar 9 november 2026'], ['2026-11-20', 'oppen', 'Remiss öppen till och med 20 januari 2027']]) {
    const html = L.remissAktuelltHtml(DATA, idag);
    assert.match(html, new RegExp(`data-lage="${lage}"`));
    assert.match(html, /href="reformer\.html\?reform=laroplaner"/);
    const text = html.replace(/<[^>]+>/g, '');
    assert.equal(text, `${status}: Förslag på nya läroplaner och kursplaner för grundskolan, anpassade grundskolan, specialskolan och sameskolan`);
  }
});
test('aktuellt-rad saknas i läget avslutad', () => {
  assert.equal(laddaT8().remissAktuelltHtml(DATA, '2027-01-21'), '');
});
test('flera öppna remisser: en rad per remiss, sorterade på sista svarsdag', () => {
  const L = laddaT8();
  const tidig = { ...R, id: 'tidig', titel: 'Remiss: Tidig', oppnar: '2026-10-01', svar_senast: '2026-12-15', reform_ids: ['betyg'] };
  const sen = { ...R, id: 'sen', titel: 'Remiss: Sen', oppnar: '2026-10-01', svar_senast: '2027-03-01', reform_ids: ['stod'] };
  const html = L.remissAktuelltHtml([sen, R, tidig], '2026-11-20');
  const ordning = [...html.matchAll(/reform=([a-z]+)/g)].map(m => m[1]);
  assert.deepEqual(ordning, ['betyg', 'laroplaner', 'stod']);
  assert.equal((html.match(/data-test="remiss-aktuellt-rad"/g) || []).length, 3);
});
test('markering "Remiss" på laroplaner och tioarig i öppnar/öppen, inte i avslutad, inte på andra reformer', () => {
  const L = laddaT8();
  for (const id of ['laroplaner', 'tioarig']) {
    assert.match(L.remissMarkering(DATA, id, '2026-11-01'), /data-test="remiss-markering">Remiss</);
    assert.match(L.remissMarkering(DATA, id, '2026-11-20'), /Remiss/);
    assert.equal(L.remissMarkering(DATA, id, '2027-01-21'), '');
  }
  assert.equal(L.remissMarkering(DATA, 'betyg', '2026-11-20'), '');
});
