// automat.test.js — automatfilen (Sprint 15 T2). Kör: node --test scripts/revision/automat.test.js
// Test per regel. Fixturer i fixtures/automat/ är RIKTIGA API-svar (hämtade 2026-11-10); kantfall
// (delvis bifall, bara namnet stämmer m.m.) härleds ur dem genom att ändra just det fält som prövas.
'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const A = require('./automat.js');
const R = require('./revision.js');

const FX = path.join(__dirname, 'fixtures', 'automat');
const fx = (n) => JSON.parse(fs.readFileSync(path.join(FX, n), 'utf8'));
const klon = (o) => JSON.parse(JSON.stringify(o));
const lista = (d) => R.listDocs(d);

const BET_UBU30 = fx('bet-HD01UbU30-2026-11-10.json');
const lageFran = (bets) => ({ hittad: true, beteckning: 'Prop. 2025/26:292', titel: 'Skärpta villkor för friskolesektorn', url: 'u',
  betankanden: bets.map(b => R.betankandeBeslut(b)) });
const REFORM_PROP = { id: 'vinst', ref: 'Prop. 2025/26:292', status: 'proposition', transition: 'Propositionen överlämnad 2026-06-25.' };

// ---------------------------- Regel 1a ----------------------------------------
test('1a: rskr inträffat + fullt bifall → beslutad, mallmening framför befintlig text', () => {
  const r = A.regel1a(REFORM_PROP, lageFran([BET_UBU30]));
  assert.ok(r.andring);
  assert.equal(r.andring.nytt, 'beslutad');
  assert.equal(r.andring.transition_tillagg, 'Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30, rskr. 2025/26:438).');
  assert.equal(r.andring.andringar_post.text,
    'Riksdagen beslutade om propositionen Skärpta villkor för friskolesektorn (Prop. 2025/26:292). Hämtat automatiskt från riksdagens öppna data.');
  assert.equal(r.andring.andringar_post.datum, '2026-08-13');
});

test('1a: delvis bifall, reservation som vinner eller annat kammarbeslut → veckorutinen', () => {
  const varianter = [
    (d) => { d.dokumentstatus.dokuppgift.uppgift.find(u => u.kod === 'beslutssammanfattningusk').text = 'Bifall till propositionen delvis. Avslag på motionerna.'; },
    (d) => { d.dokumentstatus.dokutskottsforslag.utskottsforslag[1].vinnare = 'reservation 1'; },
    (d) => { d.dokumentstatus.dokuppgift.uppgift.find(u => u.kod === 'rdbeslut').text = 'Kammaren biföll utskottets förslag med ändring.'; },
    (d) => { d.dokumentstatus.dokuppgift.uppgift.find(u => u.kod === 'beslutssammanfattningusk').text = 'Avslag på propositionen.'; },
  ];
  for (const v of varianter) {
    const d = klon(BET_UBU30); v(d);
    const r = A.regel1a(REFORM_PROP, lageFran([d]));
    assert.equal(r.andring, undefined);
    assert.equal(r.veckorutin.regel, '1a');
    assert.match(r.veckorutin.skal, /inte fullt bifall/);
  }
});

test('1a: inget riksdagsbeslut än (rskr saknas) → ingen ändring och ingen veckorutin-punkt', () => {
  const d = klon(BET_UBU30);
  d.dokumentstatus.dokreferens.referens = d.dokumentstatus.dokreferens.referens.filter(x => x.referenstyp !== 'rskr');
  assert.deepEqual(A.regel1a(REFORM_PROP, lageFran([d])), {});
});

test('1a: gäller bara status "proposition" — beslutad eller utredning rörs inte', () => {
  for (const status of ['beslutad', 'utredning']) assert.deepEqual(A.regel1a({ ...REFORM_PROP, status }, lageFran([BET_UBU30])), {});
});

// ---------------------------- Regel 1b ----------------------------------------
const SKOLPLIKT = { id: 'utr-skolplikt', beteckning: 'U 2025:04', titel: 'Utredningen om tydligare regler vid undantag från skolplikten',
  direktiv: [{ nr: 'Dir. 2025:77' }, { nr: 'Dir. 2025:111' }], betankanden: [] };
const STYRNING = { id: 'utr-barnungdomsvard-styrning', beteckning: 'S 2025:08', titel: 'Utredningen om förstärkt statlig styrning och stöd inom den sociala barn- och ungdomsvården',
  direktiv: [{ nr: 'Dir. 2025:74' }], betankanden: [] };

test('1b: kommittébeteckning OCH namn stämmer → nytt tilläggsdirektiv (Dir. 2026:117, riktigt API-svar)', () => {
  const r = A.regel1b(SKOLPLIKT, lista(fx('dir-sok-U-2025-04.json')));
  const d117 = r.andringar.find(a => a.nytt.nr === 'Dir. 2026:117');
  assert.ok(d117, 'Dir. 2026:117 föreslås');
  assert.deepEqual(d117.nytt, { nr: 'Dir. 2026:117', datum: '2026-09-03', typ: 'tilläggs', titel: 'Tilläggsdirektiv till Utredningen om tydligare regler vid undantag från skolplikten' });
  assert.equal(d117.andringar_post.text,
    'Regeringen beslutade tilläggsdirektiv till Utredningen om tydligare regler vid undantag från skolplikten (Dir. 2026:117). Hämtat automatiskt från riksdagens öppna data.');
  // redan kända direktiv föreslås inte igen
  assert.equal(r.andringar.some(a => a.nytt.nr === 'Dir. 2025:111'), false);
});

test('1b: bara det ena stämmer → veckorutinen (Dir. 2026:98: riksdagens kommittébeteckning S 2025:06)', () => {
  const r = A.regel1b(STYRNING, lista(fx('dir-sok-S-2025-08.json')));
  assert.equal(r.andringar.length, 0);
  assert.equal(r.veckorutin.length, 1);
  assert.match(r.veckorutin[0].skal, /^Dir\. 2026:98: /);
});

test('1b: bara namnet stämmer (fel kommittébeteckning) → veckorutinen', () => {
  const e = klon(lista(fx('dir-sok-U-2025-04.json')).find(x => x.beteckning === '117'));
  e.undertitel = 'kommittébeteckning: U 2025:99';
  const r = A.regel1b(SKOLPLIKT, [e]);
  assert.equal(r.andringar.length, 0);
  assert.match(r.veckorutin[0].skal, /namnet stämmer men inte kommittébeteckningen/);
});

test('1b: utredning utan beteckning (departementsuppdrag) → ingenting', () => {
  assert.deepEqual(A.regel1b({ ...SKOLPLIKT, beteckning: null }, lista(fx('dir-sok-U-2025-04.json'))), { andringar: [], veckorutin: [] });
});

test('normNamn: "utredningen En reform …" och "Utredningen om en reform …" är samma namn', () => {
  assert.equal(A.normNamn('utredningen En reform av den statliga barn- och ungdomsvården'),
    A.normNamn('Utredningen om en reform av den statliga barn- och ungdomsvården'));
});

// ---------------------------- Regel 1c ----------------------------------------
const SKOLPENG = { id: 'utr-skolpeng', beteckning: 'U 2023:05', titel: 'Utredningen om en nationell skolpengsnorm för ökad likvärdighet', status: 'pagaende',
  direktiv: [], betankanden: [{ nr: 'SOU 2025:72', titel: 'x', typ: 'del', datum: '2025-06-12' }] };

test('1c: nytt betänkande läggs till med riksdagens datum och typ ur titelsidan (SOU 2026:65)', () => {
  const r = A.regel1c(SKOLPENG, lista(fx('sou-2026-65.json')));
  assert.equal(r.andringar.length, 1);
  assert.deepEqual(r.andringar[0].nytt, { nr: 'SOU 2026:65', titel: 'Verktyg för en mer likvärdig resursfördelning', typ: 'slut', datum: '2026-10-29' });
  assert.equal(r.andringar[0].andringar_post.text,
    'Slutbetänkandet SOU 2026:65 (Verktyg för en mer likvärdig resursfördelning) från Utredningen om en nationell skolpengsnorm för ökad likvärdighet publicerades. Hämtat automatiskt från riksdagens öppna data.');
});

test('1c: utredningens status ändras inte (planen innehåller ingen statusändring)', () => {
  const r = A.regel1c(SKOLPENG, lista(fx('sou-2026-65.json')));
  assert.equal(r.andringar[0].falt, 'betankanden (ny rad)');
  assert.equal(JSON.stringify(r).includes('"status"'), false);
});

test('1c: betänkanderad utan nummer finns → veckorutinen i stället för ny rad', () => {
  const r = A.regel1c({ ...SKOLPENG, betankanden: [{ nr: null, titel: null, typ: 'del', datum: '2025-03-28' }] }, lista(fx('sou-2026-65.json')));
  assert.equal(r.andringar.length, 0);
  assert.match(r.veckorutin[0].skal, /utan nummer/);
});

// ---------------------------- Testdata på disk ---------------------------------
// Minimal datakatalog i repots format (handformaterade direktiv-/betänkanderader i utredningar.json).
function datakatalog() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'automat-'));
  fs.writeFileSync(path.join(dir, 'reforms.json'), JSON.stringify([
    { id: 'vinst', ref: 'Prop. 2025/26:292', status: 'proposition', ikraft: '1 juli 2027', transition: 'Propositionen överlämnad 2026-06-25.' },
    { id: 'skolpeng', ref: 'SOU 2025:72', status: 'utredning', ikraft: 'Ej fastställt', transition: 'Utredning pågår.' },
  ], null, 2));
  fs.writeFileSync(path.join(dir, 'utredningar.json'), `[
  {
    "id": "utr-skolplikt",
    "beteckning": "U 2025:04",
    "titel": "Utredningen om tydligare regler vid undantag från skolplikten",
    "status": "pagaende",
    "tillsatt": "2025-07-01",
    "direktiv": [
      { "nr": "Dir. 2025:77", "datum": null, "typ": "huvud", "titel": "Tydligare regler vid undantag från skolplikten" },
      { "nr": "Dir. 2025:111", "datum": "2025-12-18", "typ": "tilläggs", "titel": "Tilläggsdirektiv till Utredningen om tydligare regler vid undantag från skolplikten" }
    ],
    "betankanden": [],
    "kopplad_reform": null
  },
  {
    "id": "utr-skolpeng",
    "beteckning": "U 2023:05",
    "titel": "Utredningen om en nationell skolpengsnorm för ökad likvärdighet",
    "status": "pagaende",
    "tillsatt": "2023-11-02",
    "direktiv": [],
    "betankanden": [
      { "nr": "SOU 2025:72", "titel": "Verktyg för en mer likvärdig resursfördelning till skolan", "typ": "del", "datum": "2025-06-12" }
    ],
    "kopplad_reform": "skolpeng"
  }
]
`);
  fs.writeFileSync(path.join(dir, 'andringar.json'), JSON.stringify([
    { datum: '2026-05-26', text: 'Äldsta posten.', reform_ids: [], kalla: { text: 'x', url: 'u' } },
  ], null, 2) + '\n');
  fs.writeFileSync(path.join(dir, 'meta.json'), JSON.stringify({ senast_uppdaterad: '2026-11-01' }, null, 2) + '\n');
  return dir;
}
// Fejkad fetcher som svarar med riktiga fixturer per URL.
function fetcher({ souLista } = {}) {
  return async (url) => {
    if (url.includes('doktyp=prop')) return fx('prop-292-lista.json');
    if (url.includes('/dokumentstatus/HD03292')) return fx('prop-HD03292-dokumentstatus.json');
    if (url.includes('/dokumentstatus/HD01UbU30')) return BET_UBU30;
    if (url.includes('doktyp=sou')) return souLista || fx('sou-2026-65.json');
    if (url.includes('doktyp=dir') && url.includes('U+2025%3A04')) return fx('dir-sok-U-2025-04.json');
    if (url.includes('doktyp=dir')) return { dokumentlista: {} };
    throw new Error('oväntad url ' + url);
  };
}
const lasAlla = (dir) => Object.fromEntries(['reforms.json', 'utredningar.json', 'andringar.json', 'meta.json'].map(f => [f, fs.readFileSync(path.join(dir, f), 'utf8')]));

test('torrkörning är standard: planerar men skriver ingenting', async () => {
  const dir = datakatalog(); const fore = lasAlla(dir);
  const rap = await A.kor({ dataDir: dir, fetcher: fetcher(), idag: '2026-11-11', delayMs: 0 });
  assert.equal(rap.lage, 'torr'); assert.equal(rap.skrivet, false); assert.equal(rap.stopp, null);
  assert.ok(rap.andringar.length >= 3);
  assert.deepEqual(lasAlla(dir), fore);
});

test('1d + tillämpning: filerna skrivs, nya andringar-poster är märkta, meta = idag, övrig text orörd', async () => {
  const dir = datakatalog(); const fore = lasAlla(dir);
  const rap = await A.kor({ dataDir: dir, fetcher: fetcher(), tillampaLage: true, idag: '2026-11-11', delayMs: 0 });
  assert.equal(rap.stopp, null); assert.equal(rap.skrivet, true);
  const ref = JSON.parse(fs.readFileSync(path.join(dir, 'reforms.json'), 'utf8'));
  assert.equal(ref[0].status, 'beslutad');
  assert.equal(ref[0].transition, 'Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30, rskr. 2025/26:438). Propositionen överlämnad 2026-06-25.');
  assert.equal(ref[0].ikraft, '1 juli 2027'); // regel 2: ikraft rörs aldrig
  assert.equal(ref[1].status, 'utredning');
  const utr = JSON.parse(fs.readFileSync(path.join(dir, 'utredningar.json'), 'utf8'));
  assert.ok(utr[0].direktiv.some(d => d.nr === 'Dir. 2026:117'));
  assert.equal(utr[1].status, 'pagaende'); // regel 1c: status orörd
  assert.equal(utr[1].betankanden[1].nr, 'SOU 2026:65');
  // textinsättning: varje tidigare rad i utredningar.json finns kvar oförändrad
  const nyaRader = fs.readFileSync(path.join(dir, 'utredningar.json'), 'utf8').split('\n');
  for (const rad of fore['utredningar.json'].split('\n')) {
    assert.ok(nyaRader.includes(rad) || nyaRader.includes(rad + ','), `raden försvann: ${rad}`);
  }
  const and = JSON.parse(fs.readFileSync(path.join(dir, 'andringar.json'), 'utf8'));
  const nya = and.filter(a => a.text.endsWith(A.MARKERING));
  assert.ok(nya.length >= 3);
  assert.deepEqual(and[and.length - 1].text, 'Äldsta posten.');
  assert.equal(JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8')).senast_uppdaterad, '2026-11-11');
  // filformat: reforms utan slutradbrytning (som originalet), andringar/meta med
  assert.equal(fs.readFileSync(path.join(dir, 'reforms.json'), 'utf8').endsWith('\n'), false);
  assert.equal(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8').endsWith('\n'), true);
});

test('1d: händelser före loggens första datum får ingen andringar-post (Sprint 14-konventionen)', () => {
  const filer = { reforms: [], utredningarText: '[]', andringar: [{ datum: '2026-05-26', text: 'x' }], meta: {} };
  const plan = { andringar: [] };
  const gammal = { regel: '1x', andringar_post: { datum: '2024-08-22' } };
  assert.throws(() => A.tillampa(filer, { andringar: [gammal] }, '2026-11-11'), /okänd regel/);
  const ut = A.tillampa(filer, plan, '2026-11-11');
  assert.equal(ut.nyaPoster.length, 0);
});

// ---------------------------- Regel 2 och 3 (vakt) -----------------------------
function foreEfter() {
  const dir = datakatalog();
  const fore = { reforms: JSON.parse(fs.readFileSync(path.join(dir, 'reforms.json'), 'utf8')), utredningarText: fs.readFileSync(path.join(dir, 'utredningar.json'), 'utf8'),
    andringar: JSON.parse(fs.readFileSync(path.join(dir, 'andringar.json'), 'utf8')), meta: { senast_uppdaterad: '2026-11-01' } };
  return { fore, efter: klon(fore) };
}
test('vakt: oförändrat → inga brott', () => { const { fore, efter } = foreEfter(); assert.deepEqual(A.vakt(fore, efter), []); });

test('regel 2: SFS/ikraft, fritext, ny post och struken post stoppas', () => {
  const fall = [
    (e) => { e.reforms[0].ikraft = '2 juli 2027'; },
    (e) => { e.reforms[0].sfs = '2026:1634'; },
    (e) => { e.reforms[1].transition = 'Ny fritext.'; },
    (e) => { e.reforms.push({ id: 'ny', status: 'utredning' }); },
    (e) => { e.andringar = []; },
    (e) => { const u = JSON.parse(e.utredningarText); u.pop(); e.utredningarText = JSON.stringify(u); },
    (e) => { const u = JSON.parse(e.utredningarText); u[0].redovisning = '2027-03-31'; e.utredningarText = JSON.stringify(u); },
    (e) => { e.meta.annat = 'x'; },
  ];
  for (const f of fall) { const { fore, efter } = foreEfter(); f(efter); assert.ok(A.vakt(fore, efter).length > 0, f.toString()); }
});

test('regel 3: ifyllt värde skrivs aldrig över (direktivtitel, befintlig transition, andringar-post)', () => {
  const fall = [
    (e) => { const u = JSON.parse(e.utredningarText); u[0].direktiv[1].titel = 'Ny titel'; e.utredningarText = JSON.stringify(u); },
    (e) => { e.reforms[0].status = 'beslutad'; e.reforms[0].transition = 'Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30, rskr. 2025/26:438).'; }, // gammal text borta
    (e) => { e.andringar[0].text = 'Ändrad.'; },
    (e) => { const u = JSON.parse(e.utredningarText); u[0].direktiv.push({ nr: 'Dir. 2026:117', datum: '2026-09-03', typ: 'tilläggs', titel: 'x', extra: 1 }); e.utredningarText = JSON.stringify(u); },
  ];
  for (const f of fall) { const { fore, efter } = foreEfter(); f(efter); assert.ok(A.vakt(fore, efter).length > 0, f.toString()); }
});

test('regel 4: status och transition ändras tillsammans', () => {
  const { fore, efter } = foreEfter();
  efter.reforms[0].status = 'beslutad';
  assert.ok(A.vakt(fore, efter).some(b => /tillsammans/.test(b)));
});

test('regel 4: fasta mallar ur källans fält', () => {
  assert.equal(A.MALL.transition1a({ beslutsdatum: '2026-08-13', bet: '2025/26:UbU30', rskr: '2025/26:438' }), 'Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30, rskr. 2025/26:438).');
  assert.equal(A.MALL.andring1c({ titel: 'Utredningen om X' }, { nr: 'SOU 2027:1', titel: 'T', typ: 'del' }),
    'Delbetänkandet SOU 2027:1 (T) från Utredningen om X publicerades. Hämtat automatiskt från riksdagens öppna data.');
});

// ---------------------------- Regel 5 ------------------------------------------
test('regel 5: fler än 5 ändringar → STOPP och ingenting skrivs', async () => {
  const dir = datakatalog(); const fore = lasAlla(dir);
  const bas = lista(fx('sou-2026-65.json'))[0];
  const souLista = { dokumentlista: { dokument: [66, 67, 68, 69, 70, 71].map(n => ({ ...bas, beteckning: String(n), nummer: String(n), dok_id: `HEB3${n}` })) } };
  const rap = await A.kor({ dataDir: dir, fetcher: fetcher({ souLista }), tillampaLage: true, idag: '2026-11-11', delayMs: 0 });
  assert.match(rap.stopp, /^regel 5: \d+ ändringar > 5$/);
  assert.equal(rap.skrivet, false);
  assert.deepEqual(lasAlla(dir), fore);
});

test('fel vid hämtning → STOPP och ingenting skrivs', async () => {
  const dir = datakatalog(); const fore = lasAlla(dir);
  const rap = await A.kor({ dataDir: dir, fetcher: async (u) => { if (u.includes('doktyp=sou')) throw new Error('HTTP 503'); return fetcher()(u); }, tillampaLage: true, idag: '2026-11-11', delayMs: 0 });
  assert.match(rap.stopp, /fel vid hämtning/);
  assert.deepEqual(lasAlla(dir), fore);
});
