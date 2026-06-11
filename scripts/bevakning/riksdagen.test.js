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
  jobB2_nyaPropositioner,
  jobC_tillaggsdirToTracked,
  lookupProp,
  normalizeDirBet,
  dirBetFromEntry,
  propBetFromEntry,
  isUtbildningsdepOrgan,
  extractStatusOgRelaterade,
  extractBetBeslut,
  buildDataIndex,
  TERMINAL_DATAFIL_STATUS,
} = require('./riksdagen.js');

// ---- Riktiga API-svar fångade 2026-06-10 -----------------------------------
const FIXTURE_DIR = path.join(__dirname, 'fixtures');
function loadFixture(name) {
  return JSON.parse(fs.readFileSync(path.join(FIXTURE_DIR, name), 'utf8'));
}
const PROP_LIST = loadFixture('prop-dokumentlista-HB0320.json');       // Prop. 2023/24:20
const PROP_STATUS = loadFixture('prop-dokumentstatus-HB0320.json');    // HB0320, dokreferens behandlas_i
const DIR_WINDOW = loadFixture('dir-dokumentlista-window.json');       // 25 riktiga dir, organ-kortkoder
const PROP_WINDOW = loadFixture('prop-dokumentlista-window.json');     // 31 riktiga props (T2-fix-4), 1 U-dep: HD03260
// Bet-dokumentstatus (T2-fix-3, fångade 2026-06-10):
const BET_BESLUTAD = loadFixture('bet-dokumentstatus-HB01UbU5.json');  // beslut 2023-12-20, rskr 2023/24:106
const BET_BESLUTAD_NY = loadFixture('bet-dokumentstatus-HD01UbU29.json'); // beslut 2026-05-27, rskr 2025/26:300
const BET_PLANERAD = loadFixture('bet-dokumentstatus-HD01UbU30.json'); // ALLA aktiviteter "planerat" (aug 2026)

// ---- Fixture-dataset på disk (våra egna datafiler) -------------------------
// Använder den RIKTIGA propen 2023/24:20 så manifestet matchar prop-fixturen,
// och utredning U 2022:04 så fixturens U-dep-tilläggsdir fångas av jobb C.
function writeDataset() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'bevakning-data-'));
  fs.writeFileSync(path.join(dir, 'reforms.json'), JSON.stringify([
    // Icke-terminal status → jobb A ska kontrollera den (regel 2).
    { id: 'reform-timplaner', short: 'Anpassad undervisningstid', ref: 'Prop. 2023/24:20', cat: 'kunskap', status: 'proposition' },
    // Terminal status → jobb A ska INTE röra den (regel 1). Mocken saknar
    // användbar rutt för denna prop — en felaktig fetch ger found:false-delta
    // och fäller integrationstestets antal.
    { id: 'reform-terminal', short: 'Redan beslutad reform', ref: 'Prop. 2022/23:54', cat: 'kunskap', status: 'beslutad' },
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
    // Fönsterrutten FÖRE lookup-rutten — bara fönster-URL:en bär &from=.
    [/doktyp=prop.*&from=/, PROP_WINDOW],
    [/dokumentlista.*doktyp=prop/, PROP_LIST],
    [/dokumentstatus\/HB0320/, PROP_STATUS],
    [/dokumentstatus\/HB01UbU5/, BET_BESLUTAD],
    [/dokumentlista.*doktyp=dir/, DIR_WINDOW],
    // Medvetet INGEN rutt för dir-dokumentstatus: om jobb B försöker detalj-
    // fetcha (organ finns ju på list-entryt) kastar mocken och testet faller.
  ]);

  const report = await buildReport({ from: '2024-01-01', tom: '2024-02-15', dataDir, fetcher });

  // --- Jobb A: signalregel — terminal prop skippad, icke-terminal rapporteras
  // med betänkandets beslutsläge (T2-fix-3) ---
  const propD = report.deltan.filter(d => d.typ === 'prop-status');
  assert.equal(propD.length, 1, `förväntade 1 prop-delta, fick ${propD.length}: ${propD.map(d => d.beteckning)}`);
  assert.equal(propD[0].beteckning, 'Prop. 2023/24:20');
  assert.equal(propD[0].api_sager.found, true);
  assert.equal(propD[0].api_sager.dok_id, 'HB0320');
  assert.equal(propD[0].api_sager.status, undefined); // publiceringsstatus "Klar" rapporteras inte längre
  assert.deepEqual(propD[0].api_sager.betankanden, [{
    bet: '2023/24:UbU5',
    dok_id: 'HB01UbU5',
    beslut_fattat: true,
    statustext: 'Ärendet är avslutat',
    beslutsdatum: '2023-12-20',
    rdbeslut: 'Kammaren biföll utskottets förslag.',
    rskr: '2023/24:106',
  }]);
  assert.equal(report.antal_kontrollerade.props_terminala_skippade, 1);

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

  // --- Jobb B2: ny U-dep-prop som inte finns i manifestet (T2-fix-4) ---
  const nyaProp = report.deltan.filter(d => d.typ === 'ny-proposition');
  assert.equal(nyaProp.length, 1, `förväntade 1 ny prop, fick ${nyaProp.length}: ${nyaProp.map(d => d.beteckning)}`);
  assert.deepEqual(nyaProp[0], {
    typ: 'ny-proposition',
    beteckning: 'Prop. 2025/26:260',
    titel: 'En mer ändamålsenlig reglering av etikprövning av forskning som avser människor',
    datum: '2026-04-30',
    url: 'https://data.riksdagen.se/dokument/HD03260.html', // protokoll-relativ url normaliserad
  });

  assert.equal(report.antal_kontrollerade.props, 2);
  assert.equal(report.antal_kontrollerade.props_i_fonster, 31);
  assert.equal(report.antal_kontrollerade.dir_i_fonster, 25);
});

// ============================================================================
// Bug 1 direkt: extractStatusOgRelaterade mot riktig dokumentstatus
// ============================================================================
test('Bug 1: relaterade läses ur dokreferens.referens (behandlas_i), ej dokuppgift', () => {
  const { status, relaterade } = extractStatusOgRelaterade(PROP_STATUS);
  assert.equal(status, 'Klar');
  assert.deepEqual(relaterade, [{ kod: 'bet', text: '2023/24:UbU5', dok_id: 'HB01UbU5' }]);
});

// ============================================================================
// SIGNALREGEL (T2-fix-3): beslutsläge ur betänkandets dokumentstatus
// ============================================================================
test('extractBetBeslut: beslutat betänkande → fattat, riksdagens text, datum, rskr', () => {
  const beslut = extractBetBeslut(BET_BESLUTAD_NY); // HD01UbU29, riktigt svar
  assert.deepEqual(beslut, {
    beslut_fattat: true,
    statustext: 'Ärendet är avslutat',
    beslutsdatum: '2026-05-27',
    rdbeslut: 'Kammaren biföll utskottets förslag.',
    rskr: '2025/26:300',
  });
});

test('extractBetBeslut: BES-aktivitet med status "planerat" är INTE fattat beslut', () => {
  // HD01UbU30 (riktigt svar): obeslutade betänkanden HAR en BES-aktivitet,
  // men med status "planerat" och framtida datum — kriteriet är "inträffat".
  const beslut = extractBetBeslut(BET_PLANERAD);
  assert.equal(beslut.beslut_fattat, false);
  assert.equal(beslut.beslutsdatum, null);
  assert.equal(beslut.rdbeslut, null);
});

test('signalregel 2: betänkande under behandling → inget prop-delta', async () => {
  const dataDir = writeDataset();
  const fetcher = makeMockFetcher([
    [/dokumentlista.*doktyp=prop/, PROP_LIST],
    [/dokumentstatus\/HB0320/, PROP_STATUS],
    // Samma prop, men betänkandet svarar med det riktiga "planerat"-svaret:
    [/dokumentstatus\/HB01UbU5/, BET_PLANERAD],
    [/dokumentlista.*doktyp=dir/, { dokumentlista: { dokument: [] } }],
  ]);
  const report = await buildReport({ from: '2024-01-01', tom: '2024-02-15', dataDir, fetcher });
  const propD = report.deltan.filter(d => d.typ === 'prop-status');
  assert.equal(propD.length, 0, 'utskottsbehandling pågår → datafilen är korrekt → inget delta');
});

test('signalregel 1: terminal datafil-status → ingen API-fetch alls', async () => {
  assert.ok(TERMINAL_DATAFIL_STATUS.has('beslutad'));
  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'bevakning-terminal-'));
  fs.writeFileSync(path.join(dataDir, 'reforms.json'), JSON.stringify([
    { id: 'r1', short: 'X', ref: 'Prop. 2023/24:20', cat: 'kunskap', status: 'beslutad' },
  ]));
  fs.writeFileSync(path.join(dataDir, 'uppdrag.json'), '{}');
  fs.writeFileSync(path.join(dataDir, 'utredningar.json'), '[]');
  // Throwing fetcher för allt utom fönstren: varje prop-LOOKUP fäller testet.
  // (B2:s fönster-fetch är legitim — det är jobb A:s uppslag som inte får ske.)
  const fetcher = makeMockFetcher([
    [/dokumentlista.*doktyp=dir/, { dokumentlista: { dokument: [] } }],
    [/doktyp=prop.*&from=/, { dokumentlista: { dokument: [] } }],
  ]);
  const report = await buildReport({ from: '2024-01-01', tom: '2024-02-15', dataDir, fetcher });
  assert.equal(report.deltan.length, 0);
  assert.equal(report.antal_kontrollerade.props_terminala_skippade, 1);
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
// Jobb B2 (T2-fix-4): nya propositioner från U-dep
// ============================================================================
test('jobb B2: plockar bara U-dep-prop ur riktig prop-lista utan detalj-fetch', async () => {
  const propLista = PROP_WINDOW.dokumentlista.dokument;
  // Throwing fetcher: organ (fullnamn) finns på alla entries → ingen detalj-fetch.
  const fetcher = async (url) => { throw new Error(`oväntad detalj-fetch: ${url}`); };
  const manifest = { props: [] };
  const deltan = await jobB2_nyaPropositioner({ propLista, manifest, fetcher, verbose: false, delayMs: 0 });
  assert.equal(deltan.length, 1, `30 icke-U-dep-props ska filtreras bort, fick ${deltan.length}`);
  assert.equal(deltan[0].beteckning, 'Prop. 2025/26:260');
  assert.equal(deltan[0].typ, 'ny-proposition');
  assert.match(deltan[0].url, /^https:\/\//); // protokoll-relativ url normaliserad
});

test('jobb B2: prop som redan finns i manifestet dedupas bort', async () => {
  const propLista = PROP_WINDOW.dokumentlista.dokument;
  const fetcher = async (url) => { throw new Error(`oväntad fetch: ${url}`); };
  const manifest = { props: [{ id: 'Prop. 2025/26:260' }] };
  const deltan = await jobB2_nyaPropositioner({ propLista, manifest, fetcher, verbose: false, delayMs: 0 });
  assert.equal(deltan.length, 0, 'känd prop skulle dedupas bort');
});

test('propBetFromEntry: bygger full beteckning ur rm (snedstrecksform) + nummer', () => {
  assert.equal(propBetFromEntry({ rm: '2025/26', nummer: '260' }), 'Prop. 2025/26:260');
  assert.equal(propBetFromEntry({ rm: '2025/26', beteckning: '260' }), 'Prop. 2025/26:260');
  assert.equal(propBetFromEntry({ rm: '2024', nummer: '7' }), null);  // dir-form utan snedstreck
  assert.equal(propBetFromEntry({ rm: '2025/26' }), null);
  assert.equal(propBetFromEntry(null), null);
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
    [/doktyp=prop.*&from=/, { dokumentlista: { dokument: [] } }],
  ]);
  const report = await buildReport({ from: '2099-01-01', tom: '2099-01-08', dataDir: dir, fetcher });
  assert.equal(report.deltan.length, 0);
  assert.equal(report.antal_kontrollerade.props, 0);
  assert.equal(report.antal_kontrollerade.props_i_fonster, 0);
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
