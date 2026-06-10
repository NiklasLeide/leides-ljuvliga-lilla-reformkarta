// riksdagen.test.js — enhetstest för riksdags-watchern (Sprint 10 T2 + T2-fix).
// Inga ramverk: node:test + node:assert. Kör: node scripts/bevakning/riksdagen.test.js
//
// LÄRDOM (T2-fix, 2026-06-10): de ursprungliga mockarna antog FEL fältformer
// (dir-beteckning "Dir. 2099:100" istället för bart "100"+rm, departement på
// dokument istället för organ-kortkod "U-dep", relaterade i dokuppgift istället
// för dokreferens). De gav 8/8 grönt MEDAN jobb B var helt dött mot live API.
// Därför driver vi nu de centrala testerna med RIKTIGA, fångade API-svar som
// ligger som fixtures i fixtures/. Mockar mot antagna format förbjudna för de
// fält där vi nu vet sanningen.

'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {
  buildReport,
  jobB_nyttDirektivUtbildningsdep,
  jobC_tillaggsdirToTracked,
  lookupProp,
  normalizeDirBet,
  dirBetFromEntry,
  isUtbildningsdepOrgan,
  extractStatusOgRelaterade,
  buildDataIndex,
} = require('./riksdagen.js');

// ---- Riktiga API-svar fångade 2026-06-10 -----------------------------------
const FIXTURE_DIR = path.join(__dirname, 'fixtures');
function loadFixture(name) {
  return JSON.parse(fs.readFileSync(path.join(FIXTURE_DIR, name), 'utf8'));
}
const PROP_LIST = loadFixture('prop-dokumentlista-HB0320.json');       // Prop. 2023/24:20
const PROP_STATUS = loadFixture('prop-dokumentstatus-HB0320.json');    // HB0320, dokreferens behandlas_i
const DIR_WINDOW = loadFixture('dir-dokumentlista-window.json');       // 25 riktiga dir, organ-kortkoder

// ---- Fixture-dataset på disk (våra egna datafiler) -------------------------
// Använder den RIKTIGA propen 2023/24:20 så manifestet matchar prop-fixturen,
// och utredning U 2022:04 så fixturens U-dep-tilläggsdir fångas av jobb C.
function writeDataset() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'bevakning-data-'));
  fs.writeFileSync(path.join(dir, 'reforms.json'), JSON.stringify([
    { id: 'reform-timplaner', short: 'Anpassad undervisningstid', ref: 'Prop. 2023/24:20', cat: 'kunskap', status: 'beslutad' },
  ]));
  fs.writeFileSync(path.join(dir, 'uppdrag.json'), JSON.stringify({}));
  fs.writeFileSync(path.join(dir, 'utredningar.json'), JSON.stringify([
    {
      id: 'utr-skolsakerhet', beteckning: 'U 2022:04', titel: 'Skolsäkerhetsutredningen',
      status: 'pagaende', cat: 'trygghet', tillsatt: '2022-06-01', redovisning: '2024-12-31',
      direktiv: [{ nr: 'Dir. 2022:86', datum: '2022-06-01', typ: 'huvud', titel: null }],
      betankanden: [], prop: null, kopplad_reform: null, kallor: [], noteringar: null,
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

// ============================================================================
// INTEGRATION mot riktiga svarsformer: prop-status (jobb A) + nytt dir (jobb B)
// + tilläggsdir till tracked (jobb C) i en enda körning.
// ============================================================================
test('integration mot riktiga fixtures: A/B/C-deltan med korrekta fältformer', async () => {
  const dataDir = writeDataset();
  const fetcher = makeMockFetcher([
    [/dokumentlista.*doktyp=prop/, PROP_LIST],
    [/dokumentstatus\/HB0320/, PROP_STATUS],
    [/dokumentlista.*doktyp=dir/, DIR_WINDOW],
    // Medvetet INGEN rutt för dir-dokumentstatus: om jobb B försöker detalj-
    // fetcha (organ finns ju på list-entryt) kastar mocken och testet faller.
  ]);

  const report = await buildReport({ from: '2024-01-01', tom: '2024-02-15', dataDir, fetcher });

  // --- Jobb A: prop-status med relaterade ur dokreferens (Bug 1) ---
  const propD = report.deltan.filter(d => d.typ === 'prop-status');
  assert.equal(propD.length, 1);
  assert.equal(propD[0].beteckning, 'Prop. 2023/24:20');
  assert.equal(propD[0].api_sager.found, true);
  assert.equal(propD[0].api_sager.dok_id, 'HB0320');
  assert.equal(propD[0].api_sager.status, 'Klar');
  assert.deepEqual(propD[0].api_sager.relaterade, [{ kod: 'bet', text: '2023/24:UbU5' }]);

  // --- Jobb B: ett U-dep-direktiv, övriga departement bortfiltrerade (Bug 2+3) ---
  const nyaDir = report.deltan.filter(d => d.typ === 'nytt-direktiv');
  assert.equal(nyaDir.length, 1, `förväntade 1 U-dep-dir, fick ${nyaDir.length}: ${nyaDir.map(d => d.beteckning)}`);
  assert.equal(nyaDir[0].beteckning, 'Dir. 2024:7');     // byggd ur rm+nummer
  assert.equal(nyaDir[0].departement, 'U-dep');          // organ-kortkod
  assert.equal(nyaDir[0].detail_fetched, false);         // ingen detalj-fetch

  // --- Jobb C: tilläggsdir till tracked U 2022:04 ---
  const tillagg = report.deltan.filter(d => d.typ === 'tillaggsdir-till-tracked-utredning');
  assert.equal(tillagg.length, 1);
  assert.equal(tillagg[0].kopplad_utredning, 'U 2022:04');
  assert.equal(tillagg[0].direktiv_beteckning, 'Dir. 2024:7');

  assert.equal(report.antal_kontrollerade.props, 1);
  assert.equal(report.antal_kontrollerade.dir_i_fonster, 25);
});

// ============================================================================
// Bug 1 direkt: extractStatusOgRelaterade mot riktig dokumentstatus
// ============================================================================
test('Bug 1: relaterade läses ur dokreferens.referens (behandlas_i), ej dokuppgift', () => {
  const { status, relaterade } = extractStatusOgRelaterade(PROP_STATUS);
  assert.equal(status, 'Klar');
  assert.deepEqual(relaterade, [{ kod: 'bet', text: '2023/24:UbU5' }]);
});

// ============================================================================
// lookupProp mot riktig dokumentlista (bart löpnummer + rm matchas)
// ============================================================================
test('lookupProp: matchar prop när API ger beteckning som bart löpnummer', async () => {
  const fetcher = makeMockFetcher([[/dokumentlista/, PROP_LIST]]);
  const res = await lookupProp('Prop. 2023/24:20', { fetcher, delayMs: 0 });
  assert.equal(res.found, true);
  assert.equal(res.list_entry.dok_id, 'HB0320');
  assert.equal(res.list_entry.beteckning, '20');
  assert.equal(res.list_entry.rm, '2023/24');
});

// ============================================================================
// Bug 2: jobb B filtrerar på organ-kortkod, gör INGEN detalj-fetch
// ============================================================================
test('Bug 2: jobb B plockar bara U-dep ur riktig dir-lista utan detalj-fetch', async () => {
  const direktivLista = DIR_WINDOW.dokumentlista.dokument;
  // Throwing fetcher: varje detalj-fetch skulle kasta → bevisar att ingen sker.
  const fetcher = async (url) => { throw new Error(`oväntad detalj-fetch: ${url}`); };
  const manifest = { dir: [], utredningar: [] };
  const deltan = await jobB_nyttDirektivUtbildningsdep({ direktivLista, manifest, fetcher, verbose: false, delayMs: 0 });
  assert.equal(deltan.length, 1);
  assert.equal(deltan[0].beteckning, 'Dir. 2024:7');
  assert.equal(deltan[0].departement, 'U-dep');
  assert.equal(deltan[0].detail_fetched, false);
});

// ============================================================================
// Bug 3 / dedup: känd dir i manifestet rapporteras INTE som ny
// ============================================================================
test('Bug 3: dir som redan finns i manifestet (byggd beteckning) dedupas bort', async () => {
  const direktivLista = DIR_WINDOW.dokumentlista.dokument;
  const fetcher = async (url) => { throw new Error(`oväntad fetch: ${url}`); };
  const manifest = { dir: [{ id: 'Dir. 2024:7' }], utredningar: [] };
  const deltan = await jobB_nyttDirektivUtbildningsdep({ direktivLista, manifest, fetcher, verbose: false, delayMs: 0 });
  assert.equal(deltan.length, 0, 'känd dir skulle dedupas bort');
});

// ============================================================================
// Jobb C: tilläggsdir till spårad utredning — inkl. 3-siffrigt löpnummer
// ============================================================================
test('jobb C: tilläggsdir vars titel refererar tracked U-beteckning (2 och 3 siffror)', () => {
  const manifest = {
    props: [], sou: [], dir: [],
    utredningar: [{ id: 'U 2023:05', referenser: [] }, { id: 'U 2025:101', referenser: [] }],
  };
  const direktivLista = [
    { dok_id: 'X1', rm: '2099', nummer: '200', titel: 'Tilläggsdirektiv till Utredningen om foo (U 2023:05)', datum: '2099-12-29', dokument_url_html: 'https://example/X1' },
    { dok_id: 'X2', rm: '2099', nummer: '201', titel: 'Tilläggsdirektiv till Utredningen om tresiffrig (U 2025:101)', datum: '2099-12-29' },
    { dok_id: 'X3', rm: '2099', nummer: '202', titel: 'Tilläggsdirektiv till okänd utredning (U 2098:01)', datum: '2099-12-29' },
    { dok_id: 'X4', rm: '2099', nummer: '203', titel: 'Ett nytt direktiv utan parentes-referens', datum: '2099-12-29' },
  ];
  const deltan = jobC_tillaggsdirToTracked({ direktivLista, manifest });
  assert.equal(deltan.length, 2);
  const koppl = deltan.map(d => d.kopplad_utredning).sort();
  assert.deepEqual(koppl, ['U 2023:05', 'U 2025:101']);
  const tresiffrig = deltan.find(d => d.kopplad_utredning === 'U 2025:101');
  assert.equal(tresiffrig.direktiv_beteckning, 'Dir. 2099:201'); // byggd ur rm+nummer
});

// ============================================================================
// Tomt fönster ger inga deltan
// ============================================================================
test('tomt fönster ger inga B/C-deltan; prop-paren rapporteras (tomma utan props)', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'bevakning-empty-'));
  fs.writeFileSync(path.join(dir, 'reforms.json'), '[]');
  fs.writeFileSync(path.join(dir, 'uppdrag.json'), '{}');
  fs.writeFileSync(path.join(dir, 'utredningar.json'), '[]');
  const fetcher = makeMockFetcher([
    [/dokumentlista.*doktyp=dir/, { dokumentlista: { dokument: [] } }],
  ]);
  const report = await buildReport({ from: '2099-01-01', tom: '2099-01-08', dataDir: dir, fetcher });
  assert.equal(report.deltan.length, 0);
  assert.equal(report.antal_kontrollerade.props, 0);
  assert.equal(report.antal_kontrollerade.dir_i_fonster, 0);
});

// ============================================================================
// Nätverksfel ger fel — ALDRIG tyst tom rapport
// ============================================================================
test('nätverksfel kastar — ingen tyst tom rapport', async () => {
  const dir = writeDataset();
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
test('normalizeDirBet: olika ingångsformat (redan årtalsbärande strängar)', () => {
  assert.equal(normalizeDirBet('Dir. 2025:103'), 'Dir. 2025:103');
  assert.equal(normalizeDirBet('Dir.2025:103'), 'Dir. 2025:103');
  assert.equal(normalizeDirBet('2025:103'), 'Dir. 2025:103');
  assert.equal(normalizeDirBet('Prop. 2025/26:198'), null);
  assert.equal(normalizeDirBet('7'), null);           // bart löpnummer → behöver rm
  assert.equal(normalizeDirBet(null), null);
});

test('dirBetFromEntry: bygger full beteckning ur rm + nummer/beteckning', () => {
  assert.equal(dirBetFromEntry({ rm: '2024', nummer: '7' }), 'Dir. 2024:7');
  assert.equal(dirBetFromEntry({ rm: '2024', beteckning: '7' }), 'Dir. 2024:7');
  assert.equal(dirBetFromEntry({ rm: '2024', nummer: '103' }), 'Dir. 2024:103');
  assert.equal(dirBetFromEntry({ beteckning: 'Dir. 2023:175' }), 'Dir. 2023:175'); // fallback
  assert.equal(dirBetFromEntry(null), null);
});

test('isUtbildningsdepOrgan: kortkod och fullt namn matchar, andra dep ej', () => {
  assert.equal(isUtbildningsdepOrgan('U-dep'), true);
  assert.equal(isUtbildningsdepOrgan('Utbildningsdepartementet'), true);
  assert.equal(isUtbildningsdepOrgan('UD-dep'), false);   // Utrikesdepartementet
  assert.equal(isUtbildningsdepOrgan('Ju-dep'), false);
  assert.equal(isUtbildningsdepOrgan(null), false);
});

test('buildDataIndex: prop-strängar plockas från reforms.ref', () => {
  const dir = writeDataset();
  const idx = buildDataIndex(dir);
  assert.ok(idx.props['Prop. 2023/24:20']);
  assert.equal(idx.props['Prop. 2023/24:20'].kalla_fil, 'reforms.json');
});
