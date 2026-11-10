// revision.test.js — enhetstester för revisionsskriptet (Sprint 14 T2).
// Inga ramverk: node:test + node:assert. Kör: node --test scripts/revision/revision.test.js
//
// Fixturerna är RIKTIGA API-svar (projektregel sedan bevakning T2-fix: mockar mot
// antagna fältformer är förbjudna där vi vet sanningen):
//   bet-HD01UbU30-planerat-2026-06-10.json  — UbU30 före beslut (kopia ur bevakning/fixtures)
//   bet-HD01UbU30-beslutad-2026-11-10.json  — UbU30 efter beslut, trimmad till
//                                              dokument/dokuppgift/dokaktivitet/dokreferens
//   dir-2026-98.json, sou-2026-65.json      — list-entries hämtade 2026-11-10
// Fall som inte finns live (BES inträffat men rskr saknas) HÄRLEDS ur den
// riktiga fixturen genom att ta bort just rskr-referensen — fältformerna är äkta.

'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const r = require('./revision.js');

const fx = (n) => JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', n), 'utf8'));
const first = (d) => { const x = d.dokumentlista.dokument; return Array.isArray(x) ? x[0] : x; };
const clone = (o) => JSON.parse(JSON.stringify(o));

// ---------------------------- RSKR-REGELN ------------------------------------

test('rskr-regeln: BES inträffat + rskr → riksdagsbeslut (UbU30 2026-11-10)', () => {
  const b = r.betankandeBeslut(fx('bet-HD01UbU30-beslutad-2026-11-10.json'));
  assert.equal(b.riksdagsbeslut, true);
  assert.equal(b.rskr, '2025/26:438');
  assert.equal(b.beslutsdatum, '2026-08-13');
  assert.equal(b.bet, '2025/26:UbU30');
});

test('rskr-regeln: BES planerat, ingen rskr → inget riksdagsbeslut (UbU30 2026-06-10)', () => {
  const b = r.betankandeBeslut(fx('bet-HD01UbU30-planerat-2026-06-10.json'));
  assert.equal(b.riksdagsbeslut, false);
  assert.equal(b.bes_status, 'planerat');
  assert.equal(b.beslutsdatum, null);
});

test('rskr-regeln: BES inträffat men rskr saknas → INTE riksdagsbeslut', () => {
  const d = clone(fx('bet-HD01UbU30-beslutad-2026-11-10.json'));
  const refs = d.dokumentstatus.dokreferens.referens;
  d.dokumentstatus.dokreferens.referens = (Array.isArray(refs) ? refs : [refs]).filter(x => x.referenstyp !== 'rskr');
  const b = r.betankandeBeslut(d);
  assert.equal(b.bes_status, 'inträffat');
  assert.equal(b.rskr, null);
  assert.equal(b.riksdagsbeslut, false);
});

test('rskr-regeln: rskr finns men BES ej inträffat → INTE riksdagsbeslut', () => {
  const d = clone(fx('bet-HD01UbU30-beslutad-2026-11-10.json'));
  const akt = d.dokumentstatus.dokaktivitet.aktivitet;
  for (const a of (Array.isArray(akt) ? akt : [akt])) if (a.kod === 'BES') a.status = 'planerat';
  const b = r.betankandeBeslut(d);
  assert.equal(b.rskr, '2025/26:438');
  assert.equal(b.riksdagsbeslut, false);
});

test('rskr-regeln: propens publiceringsstatus "Klar" påverkar inte utfallet', () => {
  // diffReformMotProp läser bara betänkandenas riksdagsbeslut — ett läge med
  // publiceringsstatus "Klar" men obeslutat betänkande får inte ge "beslutad".
  const bet = r.betankandeBeslut(fx('bet-HD01UbU30-planerat-2026-06-10.json'));
  const lage = { hittad: true, publiceringsstatus: 'Klar', url: 'u', betankanden: [bet], riksdagsbeslut: false };
  const f = r.diffReformMotProp({ id: 'vinst', ref: 'Prop. 2025/26:292', status: 'utredning', transition: '' }, lage);
  assert.equal(f.some(x => x.typ === 'status-efter-riksdagsbeslut'), false);
});

// ---------------------------- Diff reform ↔ prop -----------------------------

test('diffReformMotProp: transition utan rskr ger fynd, med rskr inget fynd', () => {
  const bet = r.betankandeBeslut(fx('bet-HD01UbU30-beslutad-2026-11-10.json'));
  const lage = { hittad: true, url: 'u', betankanden: [bet], riksdagsbeslut: true };
  const utan = r.diffReformMotProp({ id: 'vinst', status: 'beslutad',
    transition: 'Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30; rskr ej publicerad 2026-08-25).' }, lage);
  assert.deepEqual(utan.map(x => x.typ), ['transition-saknar-rskr']);
  assert.equal(utan[0].api, 'rskr. 2025/26:438');
  const med = r.diffReformMotProp({ id: 'vinst', status: 'beslutad',
    transition: 'Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30, rskr. 2025/26:438).' }, lage);
  assert.deepEqual(med, []);
});

test('diffReformMotProp: beslutad i data utan riksdagsbeslut enligt regeln → fynd', () => {
  const bet = r.betankandeBeslut(fx('bet-HD01UbU30-planerat-2026-06-10.json'));
  const f = r.diffReformMotProp({ id: 'x', status: 'beslutad', transition: '2025/26:UbU30' },
    { hittad: true, url: 'u', betankanden: [bet], riksdagsbeslut: false });
  assert.deepEqual(f.map(x => x.typ), ['beslutad-utan-rskr-regel']);
});

test('diffReformMotProp: flera betänkanden ger högst ett fynd per betänkande', () => {
  const b1 = { bet: '2025/26:UbU23', rskr: '2025/26:327', beslutsdatum: '2026-06-03', riksdagsbeslut: true, url: 'u1' };
  const b2 = { bet: '2025/26:UbU26', rskr: '2025/26:335', beslutsdatum: '2026-06-09', riksdagsbeslut: true, url: 'u2' };
  const lage = { hittad: true, url: 'u', betankanden: [b1, b2], riksdagsbeslut: true };
  const f = r.diffReformMotProp({ id: 'laroplaner', status: 'beslutad',
    transition: 'Riksdagen beslutade 2026-06-03 (bet. 2025/26:UbU23, rskr. 2025/26:327).' }, lage);
  assert.deepEqual(f.map(x => x.typ), ['ytterligare-betankande']);
  const ingen = r.diffReformMotProp({ id: 'timplan', status: 'beslutad', transition: 'Beslutad.' }, lage);
  assert.deepEqual(ingen.map(x => x.typ), ['transition-saknar-riksdagsbeslut']);
});

// ---------------------------- Utredningar ------------------------------------

test('kommittebeteckning + diffUtredning: direktiv kopplat till annan kommitté (Dir. 2026:98)', () => {
  const e = first(fx('dir-2026-98.json'));
  assert.equal(r.kommittebeteckning(e), 'S 2025:06');
  assert.equal(r.dirNr(e), 'Dir. 2026:98');
  const u = { id: 'utr-x', beteckning: 'S 2025:08', titel: 'X', status: 'pagaende',
    direktiv: [{ nr: 'Dir. 2026:98', datum: '2026-08-28', typ: 'tilläggs', titel: 'T' }], betankanden: [] };
  const f = r.diffUtredning(u, { direktivKommitte: [], direktivUppslag: { 'Dir. 2026:98': { entry: e } }, souMatchade: [], souUppslag: {} });
  const typer = f.map(x => x.typ).sort();
  assert.deepEqual(typer, ['datum-avviker', 'direktiv-annan-kommitte']);
  assert.equal(f.find(x => x.typ === 'datum-avviker').api, '2026-08-27');
});

test('souAvsandare + diffUtredning: slutbetänkande hittat via titelmatch, saknas i data', () => {
  const e = first(fx('sou-2026-65.json'));
  assert.deepEqual(r.souAvsandare(e), { typ: 'slut', av: 'Utredningen om en nationell skolpengsnorm för ökad likvärdighet' });
  const u = { id: 'utr-skolpeng', beteckning: 'U 2023:05', titel: 'Utredningen om en nationell skolpengsnorm för ökad likvärdighet',
    status: 'pagaende', direktiv: [], betankanden: [] };
  const f = r.diffUtredning(u, { direktivKommitte: [], direktivUppslag: {}, souMatchade: [e], souUppslag: {} });
  assert.deepEqual(f.map(x => x.typ).sort(), ['nytt-betankande-i-api', 'pagaende-med-slutbetankande']);
  assert.match(f.find(x => x.typ === 'nytt-betankande-i-api').api, /^SOU 2026:65 \(2026-10-29\)/);
});

// ---------------------------- Körbar om --------------------------------------

test('buildRevision är deterministisk: två körningar mot samma svar ger identisk rapport', async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'rev-'));
  fs.writeFileSync(path.join(tmp, 'reforms.json'), JSON.stringify([
    { id: 'vinst', ref: 'Prop. 2025/26:292', status: 'beslutad', transition: 'bet. 2025/26:UbU30' },
  ]));
  fs.writeFileSync(path.join(tmp, 'utredningar.json'), JSON.stringify([
    { id: 'utr-skolpeng', beteckning: 'U 2023:05', titel: 'Utredningen om en nationell skolpengsnorm för ökad likvärdighet',
      status: 'pagaende', tillsatt: '2023-10-19', direktiv: [], betankanden: [] },
  ]));
  const bet = fx('bet-HD01UbU30-beslutad-2026-11-10.json');
  const sou = fx('sou-2026-65.json');
  const fetcher = async (url) => {
    if (url.includes('doktyp=prop')) return { dokumentlista: { dokument: [{ rm: '2025/26', beteckning: '292', doktyp: 'prop', dok_id: 'HD03292', titel: 'Skärpta villkor för friskolesektorn', datum: '2026-06-25', status: 'Klar' }] } };
    if (url.includes('/dokumentstatus/HD03292')) return { dokumentstatus: { dokreferens: { referens: [{ referenstyp: 'behandlas_i', ref_dok_id: 'HD01UbU30' }] } } };
    if (url.includes('/dokumentstatus/HD01UbU30')) return bet;
    if (url.includes('doktyp=sou')) return sou;
    if (url.includes('doktyp=dir')) return { dokumentlista: {} };
    throw new Error(`oväntad url ${url}`);
  };
  const a = await r.buildRevision({ dataDir: tmp, fetcher, delayMs: 0 });
  const b = await r.buildRevision({ dataDir: tmp, fetcher, delayMs: 0 });
  assert.deepEqual(a, b);
  assert.equal(a.fel.length, 0);
  assert.deepEqual(a.fynd.map(x => x.typ).sort(),
    ['nytt-betankande-i-api', 'pagaende-med-slutbetankande', 'transition-saknar-beslutsdatum', 'transition-saknar-rskr']);
  assert.equal(r.renderMarkdown(a, { datum: '2026-11-10' }), r.renderMarkdown(b, { datum: '2026-11-10' }));
});

test('markeraAccepterade: beslutade fynd märks med skäl; ändrat källvärde gör fyndet nytt igen', () => {
  const rap = { propositioner: [], utredningar: [], fel: [], fynd: [
    { fil: 'utredningar.json', post: 'utr-x', falt: 'betankanden SOU 2025:8.datum', api: '2025-01-29', typ: 'datum-avviker' },
    { fil: 'utredningar.json', post: 'utr-y', falt: 'betankanden SOU 2026:4.datum', api: '2026-01-21', typ: 'datum-avviker' },
  ] };
  const acc = { fynd: [
    { fil: 'utredningar.json', post: 'utr-x', falt: 'betankanden SOU 2025:8.datum', api: '2025-01-29', skal: 'beslutat' },
    { fil: 'utredningar.json', post: 'utr-y', falt: 'betankanden SOU 2026:4.datum', api: '2026-01-20', skal: 'beslutat' },
  ] };
  r.markeraAccepterade(rap, acc);
  assert.equal(rap.fynd[0].accepterad, 'beslutat');
  assert.equal(rap.fynd[1].accepterad, undefined); // källan säger nu 01-21 → nytt fynd
  const md = r.renderMarkdown(rap, { datum: '2026-11-10' });
  assert.match(md, /1 nya fynd, 1 accepterade/);
  assert.match(md, /## Accepterade \(redan beslutade att lämnas\)/);
});
