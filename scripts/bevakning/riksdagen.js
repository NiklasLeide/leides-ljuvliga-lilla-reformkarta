#!/usr/bin/env node
// riksdagen.js — riksdags-API-watcher för bevakningsautomatiseringen (Sprint 10 T2).
// CJS, zero-dependency, Node 20+ inbyggd fetch.
//
// Producerar en delta-rapport som JSON till stdout. Tre detekteringsjobb:
//   A) prop-status: för varje Prop. i manifestet — vad säger API:t vs datafilen?
//   B) nytt-direktiv: nya direktiv (7d) från Utbildningsdepartementet
//   C) tillaggsdir-till-tracked-utredning: tilläggsdir vars titel refererar en
//      tracked U-beteckning, oavsett departement
//
// Inga statusmappningar — skriptet tolkar inte, det rapporterar beskrivande
// faktapar. Människan triagar via veckorapportens triage-kryssrutor (T4).
//
// CLI:
//   node riksdagen.js                       # default: tom=idag, from=idag-7d
//   node riksdagen.js --from 2025-12-22 --tom 2025-12-31
//   node riksdagen.js --data /annan/data    # alternativ datakatalog
//   node riksdagen.js --verbose             # logga API-svar till stderr
//
// EMPIRISKA ANTAGANDEN (sandboxen kunde inte verifiera mot live API —
// Riksdagens API gated User-Agent, 403):
//
//   1. Prop-uppslag: doktyp=prop&rm=<RM>&bet=<NR>. Vid 0 träffar faller koden
//      tillbaka på sok=<full beteckning>. Verifieras vid första skarpa körning;
//      --verbose dumpar list-svaret så att Niklas kan justera om fältnamn
//      skiljer från docs.
//
//   2. Departement: kollas i denna ordning på list-entry: `departement`,
//      `dokumentstatus.dokument.departement` (via detalj-fetch), `organ`.
//      För doktyp=dir är `organ` ofta "Kommittédirektiv" och inte avsändande
//      departement — därför detalj-fetchen.

'use strict';

const fs = require('fs');
const path = require('path');
const { extractManifest } = require('./extract.js');

const API_BASE = 'https://data.riksdagen.se';
const USER_AGENT = 'reformkartan-bevakning (reformer.leide.se)';
const REQUEST_DELAY_MS = 600;

// ----------------------------- HTTP-lager ------------------------------------

function makeHttpFetcher({ verbose = false } = {}) {
  return async function httpFetcher(url) {
    let response;
    try {
      response = await fetch(url, {
        headers: { 'User-Agent': USER_AGENT, 'Accept': 'application/json' },
      });
    } catch (err) {
      throw new Error(`Nätverksfel mot ${url}: ${err.message}`);
    }
    if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText} från ${url}`);
    let json;
    try {
      json = await response.json();
    } catch (err) {
      throw new Error(`Ogiltigt JSON-svar från ${url}: ${err.message}`);
    }
    if (verbose) process.stderr.write(`[fetch] ${url}\n[fetch] keys: ${Object.keys(json).join(', ')}\n`);
    return json;
  };
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// Default-delay för skarpa API-anrop. Tests kan sänka via buildReport({ delayMs: 0 }).
const REQUEST_DELAY_MS_DEFAULT = 600;

// ----------------------------- API-anrop -------------------------------------

async function lookupProp(beteckning, { fetcher, verbose = false, delayMs = REQUEST_DELAY_MS_DEFAULT }) {
  const m = /^Prop\.\s*(\d{4}\/\d{2}):(\d+)$/.exec(beteckning);
  if (!m) throw new Error(`Ogiltig prop-beteckning: ${beteckning}`);
  const rm = m[1], nr = m[2];

  // Primärparameter (empiriskt antagande, se huvudkommentar)
  const candidates = [
    new URLSearchParams({ doktyp: 'prop', rm, bet: nr, utformat: 'json', sz: '5' }),
    new URLSearchParams({ doktyp: 'prop', sok: beteckning, utformat: 'json', sz: '5' }),
  ];

  for (const params of candidates) {
    const url = `${API_BASE}/dokumentlista/?${params}`;
    const data = await fetcher(url);
    await sleep(delayMs);
    const docs = (data && data.dokumentlista && data.dokumentlista.dokument) || [];
    const docsArr = Array.isArray(docs) ? docs : [docs];
    // Riksdagens beteckning kan vara "198" eller "Prop. 2025/26:198"
    const exact = docsArr.find(d =>
      d.rm === rm && (d.beteckning === beteckning || d.beteckning === nr || d.beteckning === `${nr}`)
    );
    if (exact) return { found: true, list_entry: exact, query_url: url };
    if (verbose) process.stderr.write(`[prop] ingen exakt träff för ${beteckning} via ${params}\n`);
  }
  return { found: false, list_entry: null, query_url: `${API_BASE}/dokumentlista/?${candidates[0]}` };
}

async function fetchDokumentstatus(dok_id, { fetcher, delayMs = REQUEST_DELAY_MS_DEFAULT }) {
  if (!dok_id) throw new Error('fetchDokumentstatus: dok_id saknas');
  const url = `${API_BASE}/dokumentstatus/${encodeURIComponent(dok_id)}.json`;
  const data = await fetcher(url);
  await sleep(delayMs);
  return data;
}

// ----------------------------- Fältutvinning ---------------------------------

function extractDepartement(listEntry, dokstatus) {
  if (listEntry && listEntry.departement) return listEntry.departement;
  if (dokstatus && dokstatus.dokumentstatus && dokstatus.dokumentstatus.dokument
      && dokstatus.dokumentstatus.dokument.departement) {
    return dokstatus.dokumentstatus.dokument.departement;
  }
  if (listEntry && listEntry.organ) return listEntry.organ;
  return null;
}

function extractStatusOgRelaterade(dokstatus) {
  const dok = dokstatus && dokstatus.dokumentstatus && dokstatus.dokumentstatus.dokument;
  const uppgifter = (dokstatus && dokstatus.dokumentstatus && dokstatus.dokumentstatus.dokuppgift
    && dokstatus.dokumentstatus.dokuppgift.uppgift) || [];
  const aktiviteter = (dokstatus && dokstatus.dokumentstatus && dokstatus.dokumentstatus.dokaktivitet
    && dokstatus.dokumentstatus.dokaktivitet.aktivitet) || [];

  const uppgArr = Array.isArray(uppgifter) ? uppgifter : [uppgifter];
  const aktArr = Array.isArray(aktiviteter) ? aktiviteter : [aktiviteter];

  const status = (dok && dok.status) || (aktArr[0] && (aktArr[0].aktivitet || aktArr[0].beslutstext)) || null;
  const relaterade = uppgArr
    .filter(u => u && ['rskr', 'bet', 'utskottsforslag', 'lagrum'].includes(u.kod))
    .map(u => ({ kod: u.kod, text: u.text || u.value || u.dok_id || null }));

  return { status, relaterade };
}

// ----------------------------- Datafil-index ---------------------------------

// Bygger ett index från datafilerna: vad säger filerna om varje prop?
// Inga tolkningar — bara strängar.
function buildDataIndex(dataDir) {
  const reforms = JSON.parse(fs.readFileSync(path.join(dataDir, 'reforms.json'), 'utf8'));
  const utredningar = JSON.parse(fs.readFileSync(path.join(dataDir, 'utredningar.json'), 'utf8'));

  const props = {};
  for (const r of reforms) {
    if (r && typeof r.ref === 'string' && /^Prop\./i.test(r.ref)) {
      props[r.ref] = { status: r.status || null, kalla_fil: 'reforms.json', kalla_post: r.id };
    }
  }
  for (const u of utredningar) {
    if (u && typeof u.prop === 'string' && /^Prop\./i.test(u.prop) && !props[u.prop]) {
      props[u.prop] = { status: null, kalla_fil: 'utredningar.json', kalla_post: u.id };
    }
  }
  return { props };
}

// ----------------------------- Tre detekteringsjobb --------------------------

async function jobA_props({ manifest, dataIndex, fetcher, verbose, delayMs }) {
  const deltan = [];
  for (const entry of manifest.props) {
    const resultat = await lookupProp(entry.id, { fetcher, verbose, delayMs });
    let api_sager;
    let dokstatusUrl = null;

    if (!resultat.found) {
      api_sager = { found: false };
    } else {
      const dokstatus = await fetchDokumentstatus(resultat.list_entry.dok_id, { fetcher, delayMs });
      const sr = extractStatusOgRelaterade(dokstatus);
      const dokument = (dokstatus && dokstatus.dokumentstatus && dokstatus.dokumentstatus.dokument) || {};
      dokstatusUrl = dokument.dokument_url_html || `${API_BASE}/dokumentstatus/${resultat.list_entry.dok_id}.json`;
      api_sager = {
        found: true,
        dok_id: resultat.list_entry.dok_id,
        status: sr.status,
        datum: dokument.datum || resultat.list_entry.datum || null,
        relaterade: sr.relaterade,
      };
    }

    deltan.push({
      typ: 'prop-status',
      beteckning: entry.id,
      api_sager,
      datafilen_sager: dataIndex.props[entry.id] || null,
      kalla_fil: (entry.referenser[0] && entry.referenser[0].kalla_fil) || null,
      url: dokstatusUrl || resultat.query_url,
    });
  }
  return deltan;
}

async function fetchDirektivWindow({ from, tom, fetcher, delayMs = REQUEST_DELAY_MS_DEFAULT }) {
  const params = new URLSearchParams({
    doktyp: 'dir', sort: 'datum', sortorder: 'desc',
    sz: '50', utformat: 'json',
    from, tom,
  });
  const url = `${API_BASE}/dokumentlista/?${params}`;
  const data = await fetcher(url);
  await sleep(delayMs);
  const docs = (data && data.dokumentlista && data.dokumentlista.dokument) || [];
  return Array.isArray(docs) ? docs : [docs];
}

const DIR_BET_RE = /^Dir\.\s*(\d{4}:\d+)$/;
const UTRBET_IN_TITEL_RE = /\(((?:U|Fi|S|Ju|A|Ku|N|M|Fö|UD)\s+\d{4}:\d{2})\)/;

function normalizeDirBet(raw) {
  if (typeof raw !== 'string') return null;
  const m = DIR_BET_RE.exec(raw.trim()) || /^(\d{4}:\d+)$/.exec(raw.trim());
  if (!m) return null;
  return `Dir. ${m[1] || m[0]}`;
}

async function jobB_nyttDirektivUtbildningsdep({ direktivLista, manifest, fetcher, verbose, delayMs }) {
  const kandaDir = new Set(manifest.dir.map(d => d.id));
  const deltan = [];

  for (const entry of direktivLista) {
    const bet = normalizeDirBet(entry.beteckning);
    if (bet && kandaDir.has(bet)) continue; // redan i manifestet → inte nytt för oss

    let departement = entry.departement || null;
    let detailFetched = false;
    if (!departement || /kommitt[eé]direktiv/i.test(departement)) {
      try {
        const ds = await fetchDokumentstatus(entry.dok_id, { fetcher, delayMs });
        departement = extractDepartement(entry, ds);
        detailFetched = true;
      } catch (err) {
        if (verbose) process.stderr.write(`[jobB] dokumentstatus-fetch misslyckades för ${entry.dok_id}: ${err.message}\n`);
      }
    }

    if (!departement || !/utbildningsdepartementet/i.test(departement)) continue;

    deltan.push({
      typ: 'nytt-direktiv',
      beteckning: bet || entry.beteckning,
      titel: entry.titel || null,
      datum: entry.datum || null,
      departement,
      url: entry.dokument_url_html || `${API_BASE}/dokument/${entry.dok_id}`,
      detail_fetched: detailFetched,
    });
  }
  return deltan;
}

function jobC_tillaggsdirToTracked({ direktivLista, manifest }) {
  const kandaUtr = new Set(manifest.utredningar.map(u => u.id));
  const deltan = [];
  for (const entry of direktivLista) {
    const titel = entry.titel || '';
    const m = UTRBET_IN_TITEL_RE.exec(titel);
    if (!m) continue;
    if (!kandaUtr.has(m[1])) continue;

    deltan.push({
      typ: 'tillaggsdir-till-tracked-utredning',
      direktiv_beteckning: normalizeDirBet(entry.beteckning) || entry.beteckning,
      kopplad_utredning: m[1],
      titel,
      datum: entry.datum || null,
      url: entry.dokument_url_html || `${API_BASE}/dokument/${entry.dok_id}`,
    });
  }
  return deltan;
}

// ----------------------------- Toppfunktion ---------------------------------

async function buildReport({ from, tom, dataDir, fetcher, verbose = false, delayMs } = {}) {
  if (!dataDir) dataDir = path.join(__dirname, '..', '..', 'data');
  if (typeof fetcher !== 'function') {
    fetcher = makeHttpFetcher({ verbose });
    if (delayMs == null) delayMs = REQUEST_DELAY_MS_DEFAULT;
  } else if (delayMs == null) {
    delayMs = 0; // mock-fetcher → snabb path
  }

  const manifest = extractManifest(dataDir);
  const dataIndex = buildDataIndex(dataDir);

  const deltan = [];
  // Jobb A: prop-status (alltid alla manifest-props)
  const aDeltan = await jobA_props({ manifest, dataIndex, fetcher, verbose, delayMs });
  deltan.push(...aDeltan);

  // Jobb B + C delar en list-fetch
  const direktivLista = await fetchDirektivWindow({ from, tom, fetcher, delayMs });
  const bDeltan = await jobB_nyttDirektivUtbildningsdep({ direktivLista, manifest, fetcher, verbose, delayMs });
  const cDeltan = jobC_tillaggsdirToTracked({ direktivLista, manifest });
  deltan.push(...bDeltan, ...cDeltan);

  return {
    korning: new Date().toISOString(),
    fonster: { from, tom },
    antal_kontrollerade: {
      props: manifest.props.length,
      dir_i_fonster: direktivLista.length,
      utredningar_sparade: manifest.utredningar.length,
    },
    deltan,
  };
}

// ----------------------------- CLI ------------------------------------------

function parseArgs(argv) {
  const opts = { from: null, tom: null, dataDir: null, verbose: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--from') opts.from = argv[++i];
    else if (a === '--tom') opts.tom = argv[++i];
    else if (a === '--data') opts.dataDir = argv[++i];
    else if (a === '--verbose' || a === '-v') opts.verbose = true;
    else if (a === '--help' || a === '-h') opts.help = true;
  }
  return opts;
}

function defaultWindow() {
  const tom = new Date();
  const from = new Date(tom.getTime() - 7 * 24 * 60 * 60 * 1000);
  const iso = d => d.toISOString().slice(0, 10);
  return { from: iso(from), tom: iso(tom) };
}

module.exports = {
  buildReport,
  // exporterade för test
  jobA_props,
  jobB_nyttDirektivUtbildningsdep,
  jobC_tillaggsdirToTracked,
  fetchDirektivWindow,
  lookupProp,
  normalizeDirBet,
  buildDataIndex,
  extractStatusOgRelaterade,
  extractDepartement,
  defaultWindow,
};

if (require.main === module) {
  (async () => {
    const opts = parseArgs(process.argv.slice(2));
    if (opts.help) {
      process.stdout.write(`Användning: node riksdagen.js [--from YYYY-MM-DD] [--tom YYYY-MM-DD] [--data DIR] [--verbose]\n`);
      process.exit(0);
    }
    const win = defaultWindow();
    const from = opts.from || win.from;
    const tom = opts.tom || win.tom;
    try {
      const rapport = await buildReport({ from, tom, dataDir: opts.dataDir, verbose: opts.verbose });
      process.stdout.write(JSON.stringify(rapport, null, 2) + '\n');
    } catch (err) {
      process.stderr.write(`FEL: ${err.message}\n`);
      // ALDRIG tom rapport vid fel — exit 1 så Action:en kan flagga
      process.exit(1);
    }
  })();
}
