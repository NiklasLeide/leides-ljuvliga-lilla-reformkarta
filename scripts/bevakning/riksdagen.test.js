// riksdagen.test.js — enhetstest för riksdags-watchern (Sprint 10 T2).
// Inga ramverk: node:test + node:assert. Kör: node scripts/bevakning/riksdagen.test.js
//
// Strategi: skriv ett fixture-dataset på disk under /tmp och injicera en
// mock-fetcher i buildReport. Inga riktiga API-anrop — det är förbehållet
// Niklas skarpa smoke-test (network gated från sandboxen).

'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {
  buildReport,
  jobC_tillaggsdirToTracked,
  normalizeDirBet,
  buildDataIndex,
} = require('./riksdagen.js');

// ---- Fixture: minidataset med kända identifierare ---------------------------
function writeFixture() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'bevakning-fixture-'));
  fs.writeFileSync(path.join(dir, 'reforms.json'), JSON.stringify([
    { id: 'fixture-reform-a', short: 'Fixturreform A', ref: 'Prop. 2099/01:11', cat: 'kunskap', status: 'proposition' },
    { id: 'fixture-reform-b', short: 'Fixturreform B', ref: 'Prop. 2099/01:22', cat: 'kunskap', status: 'beslutad' },
  ]));
  fs.writeFileSync(path.join(dir, 'uppdrag.json'), JSON.stringify({
    'fixture-reform-a': { typ: 'ej', kallor: [], relaterade: [] },
  }));
  fs.writeFileSync(path.join(dir, 'utredningar.json'), JSON.stringify([
    {
      id: 'fixture-utr-tracked', beteckning: 'U 2099:05', titel: 'Spårad fixturutredning',
      status: 'pagaende', cat: 'styrning', tillsatt: '2099-01-01', redovisning: '2099-12-31',
      direktiv: [{ nr: 'Dir. 2099:50', datum: '2099-01-01', typ: 'huvud', titel: null }],
      betankanden: [], prop: null, kopplad_reform: 'fixture-reform-a', kallor: [], noteringar: null,
    },
  ]));
  return dir;
}

// ---- Mock-fetcher: routar URL → canned JSON --------------------------------
function makeMockFetcher(routes) {
  return async function(url) {
    for (const [matcher, payload] of routes) {
      if (matcher instanceof RegExp ? matcher.test(url) : url.includes(matcher)) {
        if (payload instanceof Error) throw payload;
        return JSON.parse(JSON.stringify(payload)); // skydda mot mutation
      }
    }
    throw new Error(`mock-fetcher: ingen rutt för ${url}`);
  };
}

// ---- Hjälpare för API-svar -------------------------------------------------
const propListResponse = (entry) => ({ dokumentlista: { dokument: entry ? [entry] : [] } });
const dokumentstatusResponse = (props) => ({
  dokumentstatus: {
    dokument: { dok_id: 'mock', ...(props.dokument || {}) },
    dokuppgift: { uppgift: props.uppgift || [] },
    dokaktivitet: { aktivitet: props.aktivitet || [] },
  },
});
const dirListResponse = (docs) => ({ dokumentlista: { dokument: docs } });

// ============================================================================
// Synteiskt huvudtestfall (sprintkrav): föråldrad uppgift i datafilen
// ============================================================================
test('synteiskt: föråldrad prop-status i datafil rapporteras som prop-status-delta', async () => {
  const dir = writeFixture();

  // API säger: Prop. 2099/01:11 är "Riksdagsbeslut" (datafilen säger "proposition" → föråldrad)
  // API säger: Prop. 2099/01:22 är "Riksdagsbeslut" (datafilen säger "beslutad" → konsistent vokabulär,
  //   men reglerna säger att vi rapporterar ALLA prop-pair, ingen mappning)
  const fetcher = makeMockFetcher([
    [/dokumentlista.*bet=11/, propListResponse({
      dok_id: 'H10311', rm: '2099/01', beteckning: '11', doktyp: 'prop', datum: '2099-03-15',
      titel: 'Fixturproposition A',
    })],
    [/dokumentstatus\/H10311/, dokumentstatusResponse({
      dokument: { dok_id: 'H10311', datum: '2099-03-15', status: 'Riksdagsbeslut', departement: 'Utbildningsdepartementet' },
      uppgift: [{ kod: 'bet', text: 'UbU8' }, { kod: 'rskr', text: '2099/01:42' }],
    })],
    [/dokumentlista.*bet=22/, propListResponse({
      dok_id: 'H10322', rm: '2099/01', beteckning: '22', doktyp: 'prop', datum: '2099-04-01',
      titel: 'Fixturproposition B',
    })],
    [/dokumentstatus\/H10322/, dokumentstatusResponse({
      dokument: { dok_id: 'H10322', datum: '2099-04-01', status: 'Riksdagsbeslut', departement: 'Utbildningsdepartementet' },
      uppgift: [{ kod: 'rskr', text: '2099/01:55' }],
    })],
    // Tom dir-lista i fönstret
    [/dokumentlista.*doktyp=dir/, dirListResponse([])],
  ]);

  const report = await buildReport({ from: '2099-01-01', tom: '2099-01-08', dataDir: dir, fetcher });

  // Båda props ska rapporteras med faktapar
  const propDeltan = report.deltan.filter(d => d.typ === 'prop-status');
  assert.equal(propDeltan.length, 2);

  // Det föråldrade fallet (Prop. 2099/01:11)
  const förald = propDeltan.find(d => d.beteckning === 'Prop. 2099/01:11');
  assert.ok(förald, 'Prop. 2099/01:11 saknas i rapporten');
  assert.equal(förald.api_sager.found, true);
  assert.equal(förald.api_sager.status, 'Riksdagsbeslut');
  assert.equal(förald.datafilen_sager.status, 'proposition');
  assert.equal(förald.kalla_fil, 'reforms.json');
  // Beskrivande fakta — ingen tolkning
  assert.ok(!('skillnad' in förald) && !('atgard' in förald), 'rapporten ska inte innehålla tolkning');

  // Antal_kontrollerade rapporteras
  assert.equal(report.antal_kontrollerade.props, 2);
  assert.equal(report.antal_kontrollerade.dir_i_fonster, 0);
});

// ============================================================================
// Jobb B: nytt direktiv från Utbildningsdep — filtrering
// ============================================================================
test('jobb B: nytt direktiv från Utbildningsdep rapporteras; andra dep filtreras bort', async () => {
  const dir = writeFixture();
  const fetcher = makeMockFetcher([
    [/dokumentlista.*bet=11/, propListResponse(null)],
    [/dokumentlista.*bet=22/, propListResponse(null)],
    [/dokumentlista.*doktyp=prop.*sok=/, propListResponse(null)], // sok-fallback
    [/dokumentlista.*doktyp=dir/, dirListResponse([
      // Träff: ny Dir. från Utbildningsdep, ej i manifestet
      { dok_id: 'D99-100', beteckning: 'Dir. 2099:100', titel: 'En utredning om skolan', datum: '2099-12-29', organ: 'Kommittédirektiv' },
      // Inte träff: Justitiedep
      { dok_id: 'D99-101', beteckning: 'Dir. 2099:101', titel: 'En utredning om straffrätt', datum: '2099-12-29', organ: 'Kommittédirektiv' },
      // Inte träff: redan i manifestet (Dir. 2099:50 hör till tracked utredning)
      { dok_id: 'D99-050', beteckning: 'Dir. 2099:50', titel: 'Originaldirektiv', datum: '2099-12-29', departement: 'Utbildningsdepartementet' },
    ])],
    // Detalj-fetch för D99-100 → Utbildningsdep
    [/dokumentstatus\/D99-100/, dokumentstatusResponse({
      dokument: { dok_id: 'D99-100', departement: 'Utbildningsdepartementet' },
    })],
    // Detalj-fetch för D99-101 → Justitie
    [/dokumentstatus\/D99-101/, dokumentstatusResponse({
      dokument: { dok_id: 'D99-101', departement: 'Justitiedepartementet' },
    })],
  ]);

  const report = await buildReport({ from: '2099-12-22', tom: '2099-12-31', dataDir: dir, fetcher });
  const nyaDir = report.deltan.filter(d => d.typ === 'nytt-direktiv');

  assert.equal(nyaDir.length, 1, `förväntade 1 nytt direktiv, fick ${nyaDir.length}: ${nyaDir.map(d=>d.beteckning)}`);
  assert.equal(nyaDir[0].beteckning, 'Dir. 2099:100');
  assert.equal(nyaDir[0].departement, 'Utbildningsdepartementet');
  assert.ok(nyaDir[0].titel.includes('skolan'));
});

// ============================================================================
// Jobb C: tilläggsdir till spårad utredning, oavsett departement
// ============================================================================
test('jobb C: tilläggsdir vars titel refererar tracked U-beteckning rapporteras', () => {
  const manifest = {
    props: [], sou: [], dir: [],
    utredningar: [{ id: 'U 2023:05', referenser: [] }, { id: 'U 2099:05', referenser: [] }],
  };
  const direktivLista = [
    { dok_id: 'X1', beteckning: 'Dir. 2099:200', titel: 'Tilläggsdirektiv till Utredningen om foo (U 2023:05)', datum: '2099-12-29', dokument_url_html: 'https://example/X1' },
    { dok_id: 'X2', beteckning: 'Dir. 2099:201', titel: 'Tilläggsdirektiv till Utredningen om okänt ämne (U 2098:01)', datum: '2099-12-29' },
    { dok_id: 'X3', beteckning: 'Dir. 2099:202', titel: 'Ett nytt direktiv utan parentes-referens', datum: '2099-12-29' },
  ];
  const deltan = jobC_tillaggsdirToTracked({ direktivLista, manifest });
  assert.equal(deltan.length, 1);
  assert.equal(deltan[0].kopplad_utredning, 'U 2023:05');
  assert.equal(deltan[0].direktiv_beteckning, 'Dir. 2099:200');
  assert.equal(deltan[0].url, 'https://example/X1');
});

// ============================================================================
// 0 falska positiva: tom dir-lista + alla props matchar → inga B/C-deltan
// (men prop-status-paren rapporteras alltid)
// ============================================================================
test('tomt fönster ger inga B/C-deltan; prop-paren rapporteras (men kan vara tomma om inga props finns)', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'bevakning-empty-'));
  fs.writeFileSync(path.join(dir, 'reforms.json'), '[]');
  fs.writeFileSync(path.join(dir, 'uppdrag.json'), '{}');
  fs.writeFileSync(path.join(dir, 'utredningar.json'), '[]');
  const fetcher = makeMockFetcher([
    [/dokumentlista.*doktyp=dir/, dirListResponse([])],
  ]);
  const report = await buildReport({ from: '2099-01-01', tom: '2099-01-08', dataDir: dir, fetcher });
  assert.equal(report.deltan.length, 0);
  assert.equal(report.antal_kontrollerade.props, 0);
  assert.equal(report.antal_kontrollerade.dir_i_fonster, 0);
});

// ============================================================================
// Nätverksfel ger fel — ALDRIG tom rapport
// ============================================================================
test('nätverksfel kastar — ingen tyst tom rapport', async () => {
  const dir = writeFixture();
  const fetcher = makeMockFetcher([
    [/.*/, new Error('Nätverksfel mot https://data.riksdagen.se/: ECONNRESET')],
  ]);
  await assert.rejects(
    buildReport({ from: '2099-01-01', tom: '2099-01-08', dataDir: dir, fetcher }),
    /Nätverksfel|ECONNRESET/
  );
});

// ============================================================================
// Hjälpfunktioner
// ============================================================================
test('normalizeDirBet: olika ingångsformat', () => {
  assert.equal(normalizeDirBet('Dir. 2025:103'), 'Dir. 2025:103');
  assert.equal(normalizeDirBet('Dir.2025:103'), 'Dir. 2025:103');
  assert.equal(normalizeDirBet('2025:103'), 'Dir. 2025:103');
  assert.equal(normalizeDirBet('Prop. 2025/26:198'), null);
  assert.equal(normalizeDirBet(null), null);
});

test('buildDataIndex: prop-strängar plockas från reforms.ref och utredningar.prop', () => {
  const dir = writeFixture();
  const idx = buildDataIndex(dir);
  assert.ok(idx.props['Prop. 2099/01:11']);
  assert.equal(idx.props['Prop. 2099/01:11'].kalla_fil, 'reforms.json');
});

// ============================================================================
// Backdaterat fönster fångar känd dir-händelse (mockat — sandboxen kan inte
// nå Riksdagen). Niklas verifierar mot live API med:
//   node scripts/bevakning/riksdagen.js --from 2025-12-22 --tom 2025-12-31
// ============================================================================
test('backdaterat fönster: skolmyndighet-dir 2025-12-29 fångas av jobb B (mockat)', async () => {
  const dir = writeFixture();
  const fetcher = makeMockFetcher([
    [/dokumentlista.*bet=11/, propListResponse(null)],
    [/dokumentlista.*bet=22/, propListResponse(null)],
    [/dokumentlista.*doktyp=prop.*sok=/, propListResponse(null)],
    [/dokumentlista.*doktyp=dir/, dirListResponse([
      {
        dok_id: 'D25-120', beteckning: 'Dir. 2025:120',
        titel: 'En översyn av skolmyndigheterna',
        datum: '2025-12-29',
        departement: 'Utbildningsdepartementet',
      },
    ])],
  ]);
  const report = await buildReport({ from: '2025-12-22', tom: '2025-12-31', dataDir: dir, fetcher });
  const ny = report.deltan.find(d => d.typ === 'nytt-direktiv' && d.beteckning === 'Dir. 2025:120');
  assert.ok(ny, 'skolmyndighet-dir hittades inte i rapporten');
  assert.equal(ny.departement, 'Utbildningsdepartementet');
});
