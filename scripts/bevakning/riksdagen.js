#!/usr/bin/env node
// riksdagen.js — riksdags-API-watcher för bevakningsautomatiseringen (Sprint 10 T2).
// CJS, zero-dependency, Node 20+ inbyggd fetch.
//
// Producerar en delta-rapport som JSON till stdout. Fyra detekteringsjobb:
//   A)  prop-status: för varje Prop. i manifestet — vad säger API:t vs datafilen?
//   B)  nytt-direktiv: nya direktiv (7d) från Utbildningsdepartementet
//   B2) ny-proposition: nya props i fönstret från Utbildningsdepartementet
//       som inte redan finns i manifestet (T2-fix-4)
//   C)  tillaggsdir-till-tracked-utredning: tilläggsdir vars titel refererar en
//       tracked U-beteckning, oavsett departement
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
// VERIFIERAT MOT LIVE API 2026-06-10 (Sprint 10 T2-fix). Fångade svar ligger
// som fixtures i fixtures/ och driver enhetstesterna. Tidigare mockar antog fel
// fältformer och gav 8/8 grönt MEDAN jobb B var dött — lärdomen är inbakad här:
//
//   1. Prop-uppslag: doktyp=prop&rm=<RM>&bet=<NR> ger exakt en träff. API:t
//      returnerar beteckning som bart löpnummer ("20") + rm ("2023/24") — matchas
//      av d.beteckning === nr. sok=-fallbacken behövs inte i praktiken men behålls.
//
//   2. Departement: skiljer sig mellan doktyper!
//      - prop: list-entry `organ` = fullt namn ("Utbildningsdepartementet"),
//        `dokument.departement` saknas (undefined).
//      - dir:  list-entry `organ` = KORTKOD ("U-dep"), och `dokument.departement`
//        är undefined ÄVEN i detalj-svaret. Därför matchar jobb B på organ-koden
//        "U-dep" och gör INGEN detalj-fetch när organ finns på list-entryt.
//
//   3. Dir-beteckning: list-API:t ger `beteckning`/`nummer` som bart löpnummer
//      ("7") med årtalet i `rm` ("2024"). Full beteckning byggs som
//      "Dir. <rm>:<nummer>" (se dirBetFromEntry) — annars fallerar dedup mot
//      manifestet och rapporterad beteckning blir oanvändbar.
//
//   4. Relaterade bet/rskr finns i `dokumentstatus.dokreferens.referens` med
//      referenstyp "behandlas_i" — INTE i dokuppgift.uppgift (vars koder är
//      inlamnatav/statustext/tilldelat).
//
// SIGNALREGEL JOBB A (T2-fix-3, 2026-06-10): propens dokument.status ("Klar")
// är PUBLICERINGSSTATUS och bär ingen beslutsinformation — alla props
// rapporterar "Klar" för evigt. Beslutssignalen finns i stället i det kopplade
// BETÄNKANDETS dokumentstatus:
//   - dokuppgift: statustext ("Ärendet är avslutat"), beslutdatumtid, rdbeslut
//   - dokaktivitet: kod "BES"/"Beslut" — OBS att även OBESLUTADE betänkanden
//     har en BES-aktivitet, men med status "planerat" och framtida datum
//     (verifierat mot HD01UbU30 2026-06-10). Kriteriet är status "inträffat".
//   - rskr i betänkandets dokreferens (referenstyp "rskr")
// Regler: (1) props med terminal status i datafilen rapporteras inte alls
// (ingen API-fetch); (2) övriga rapporteras ENDAST när minst ett kopplat
// betänkande har fattat beslut — under utskottsbehandling är datafilen
// fortfarande korrekt. Undantag: prop som inte hittas i API:t rapporteras
// alltid (anomali — alla manifest-props ska finnas).

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

// API:ts dokument_url_html är protokoll-relativ ("//data.riksdagen.se/...") —
// normalisera till https så länkarna fungerar överallt (issue-body, terminal).
function absUrl(raw) {
  if (typeof raw !== 'string' || raw === '') return raw;
  return raw.startsWith('//') ? `https:${raw}` : raw;
}

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
  const aktiviteter = (dokstatus && dokstatus.dokumentstatus && dokstatus.dokumentstatus.dokaktivitet
    && dokstatus.dokumentstatus.dokaktivitet.aktivitet) || [];
  // Relaterade betänkanden/riksdagsskrivelser ligger i dokreferens.referens med
  // referenstyp "behandlas_i" (verifierat 2026-06-10) — INTE i dokuppgift.uppgift.
  const referenser = (dokstatus && dokstatus.dokumentstatus && dokstatus.dokumentstatus.dokreferens
    && dokstatus.dokumentstatus.dokreferens.referens) || [];

  const aktArr = Array.isArray(aktiviteter) ? aktiviteter : [aktiviteter];
  const refArr = Array.isArray(referenser) ? referenser : [referenser];

  const status = (dok && dok.status) || (aktArr[0] && (aktArr[0].aktivitet || aktArr[0].beslutstext)) || null;
  const relaterade = refArr
    .filter(r => r && r.referenstyp === 'behandlas_i')
    .map(r => ({
      kod: r.ref_dok_typ || r.referenstyp || null,           // t.ex. "bet" / "rskr"
      text: r.uppgift || r.ref_dok_bet || r.ref_dok_titel || null, // t.ex. "2023/24:UbU5"
      dok_id: r.ref_dok_id || null,                          // för bet-dokumentstatus-uppslag
    }));

  return { status, relaterade };
}

// Terminal status i datafilen = riksdagsbehandlingen är redan avklarad enligt
// oss; betänkandebeslut tillför inget. Faktiska statusvärden i reforms.json
// idag: "proposition", "beslutad", "utredning" — endast "beslutad" är terminal.
// Nya terminala värden ("i kraft" o.likn.) måste läggas till här när de
// introduceras i datafilen.
const TERMINAL_DATAFIL_STATUS = new Set(['beslutad']);

// Beslutsläge ur ett BETÄNKANDES dokumentstatus-svar. Beskrivande — riksdagens
// egna texter rapporteras, ingen tolkning. Se huvudkommentaren (SIGNALREGEL).
function extractBetBeslut(betDokstatus) {
  const ds = betDokstatus && betDokstatus.dokumentstatus;

  const upgRaw = (ds && ds.dokuppgift && ds.dokuppgift.uppgift) || [];
  const upg = {};
  for (const u of (Array.isArray(upgRaw) ? upgRaw : [upgRaw])) {
    if (u && u.kod) upg[u.kod] = u.text;
  }

  const aktRaw = (ds && ds.dokaktivitet && ds.dokaktivitet.aktivitet) || [];
  const bes = (Array.isArray(aktRaw) ? aktRaw : [aktRaw]).find(a => a && a.kod === 'BES');

  // Även obeslutade betänkanden HAR en BES-aktivitet (status "planerat",
  // framtida datum) — kriteriet är status "inträffat", inte att BES finns.
  // Fallback på beslutdatumtid om aktivitetslistan saknas helt.
  const beslutFattat = bes ? bes.status === 'inträffat' : !!upg.beslutdatumtid;

  const refRaw = (ds && ds.dokreferens && ds.dokreferens.referens) || [];
  const rskrRef = (Array.isArray(refRaw) ? refRaw : [refRaw]).find(r => r && r.referenstyp === 'rskr');
  const rskr = rskrRef
    ? (rskrRef.ref_dok_rm && rskrRef.ref_dok_bet
        ? `${rskrRef.ref_dok_rm}:${rskrRef.ref_dok_bet}`
        : (rskrRef.uppgift || rskrRef.ref_dok_id || null))
    : null;

  const datum = s => (typeof s === 'string' && s.length >= 10 ? s.slice(0, 10) : null);

  return {
    beslut_fattat: beslutFattat,
    statustext: upg.statustext || null,   // riksdagens egen text, t.ex. "Ärendet är avslutat"
    beslutsdatum: datum(upg.beslutdatumtid) || (beslutFattat && bes ? datum(bes.datum) : null),
    rdbeslut: upg.rdbeslut || null,       // t.ex. "Kammaren biföll utskottets förslag."
    rskr,                                  // t.ex. "2023/24:106"
  };
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
  let terminalaSkippade = 0;

  for (const entry of manifest.props) {
    const datafilenSager = dataIndex.props[entry.id] || null;
    const kallaFil = (entry.referenser[0] && entry.referenser[0].kalla_fil) || null;

    // Regel 1: terminal status i datafilen → riksdagsbehandlingen är redan
    // registrerad hos oss, dokumentstatus "Klar" tillför inget. Ingen fetch.
    if (datafilenSager && TERMINAL_DATAFIL_STATUS.has(datafilenSager.status)) {
      terminalaSkippade++;
      if (verbose) process.stderr.write(`[jobA] ${entry.id}: terminal datafil-status "${datafilenSager.status}" — skippas\n`);
      continue;
    }

    const resultat = await lookupProp(entry.id, { fetcher, verbose, delayMs });

    // Prop som inte hittas i API:t är en anomali (alla manifest-props ska
    // finnas) — rapporteras alltid, signalregeln gäller bara funna props.
    if (!resultat.found) {
      deltan.push({
        typ: 'prop-status',
        beteckning: entry.id,
        api_sager: { found: false },
        datafilen_sager: datafilenSager,
        kalla_fil: kallaFil,
        url: resultat.query_url,
      });
      continue;
    }

    const dokstatus = await fetchDokumentstatus(resultat.list_entry.dok_id, { fetcher, delayMs });
    const sr = extractStatusOgRelaterade(dokstatus);
    const dokument = (dokstatus && dokstatus.dokumentstatus && dokstatus.dokumentstatus.dokument) || {};

    // Regel 2: hämta beslutsläget för varje kopplat betänkande.
    const betankanden = [];
    for (const ref of sr.relaterade) {
      if (ref.kod !== 'bet' || !ref.dok_id) continue;
      const betStatus = await fetchDokumentstatus(ref.dok_id, { fetcher, delayMs });
      betankanden.push({ bet: ref.text, dok_id: ref.dok_id, ...extractBetBeslut(betStatus) });
    }

    // Delta ENDAST när minst ett betänkande fattat beslut. Under utskotts-
    // behandling (eller innan bet finns) är datafilens läge fortfarande korrekt.
    if (!betankanden.some(b => b.beslut_fattat)) {
      if (verbose) process.stderr.write(`[jobA] ${entry.id}: inget betänkandebeslut ännu — inget delta\n`);
      continue;
    }

    deltan.push({
      typ: 'prop-status',
      beteckning: entry.id,
      api_sager: {
        found: true,
        dok_id: resultat.list_entry.dok_id,
        datum: dokument.datum || resultat.list_entry.datum || null,
        betankanden,
      },
      datafilen_sager: datafilenSager,
      kalla_fil: kallaFil,
      url: absUrl(dokument.dokument_url_html) || `${API_BASE}/dokumentstatus/${resultat.list_entry.dok_id}.json`,
    });
  }
  return { deltan, terminalaSkippade };
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

async function fetchPropWindow({ from, tom, fetcher, delayMs = REQUEST_DELAY_MS_DEFAULT }) {
  const params = new URLSearchParams({
    doktyp: 'prop', sort: 'datum', sortorder: 'desc',
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
// Kommittébeteckning i tilläggsdir-titlar, t.ex. "(U 2023:05)". Löpnumret kan
// vara 2–3 siffror (verifierat: zero-paddat till minst 2, men kan vara 3).
const UTRBET_IN_TITEL_RE = /\(((?:U|Fi|S|Ju|A|Ku|N|M|Fö|UD)\s+\d{4}:\d{2,3})\)/;

// Organ-kortkod för Utbildningsdepartementet på dir-list-entries.
const UTBILDNINGSDEP_ORGAN = 'U-dep';

function normalizeDirBet(raw) {
  if (typeof raw !== 'string') return null;
  const m = DIR_BET_RE.exec(raw.trim()) || /^(\d{4}:\d+)$/.exec(raw.trim());
  if (!m) return null;
  return `Dir. ${m[1] || m[0]}`;
}

// Bygg full dir-beteckning från ett list-entry. Riksdagens list-API ger
// `beteckning`/`nummer` som bart löpnummer ("7") med årtalet i `rm` ("2024").
// Faller tillbaka på normalizeDirBet om entryt redan bär full beteckning.
function dirBetFromEntry(entry) {
  if (!entry) return null;
  const rm = entry.rm != null ? String(entry.rm) : null;
  const nr = entry.nummer != null ? String(entry.nummer)
    : (entry.beteckning != null ? String(entry.beteckning) : null);
  if (rm && nr && /^\d{4}$/.test(rm) && /^\d+$/.test(nr)) {
    return `Dir. ${rm}:${nr}`;
  }
  return normalizeDirBet(entry.beteckning);
}

// Matchar Utbildningsdepartementet oavsett om vi har kortkod (dir-list) eller
// fullt namn (prop-list / vissa detalj-svar).
function isUtbildningsdepOrgan(organ) {
  if (!organ) return false;
  return organ === UTBILDNINGSDEP_ORGAN || /utbildningsdepartementet/i.test(organ);
}

async function jobB_nyttDirektivUtbildningsdep({ direktivLista, manifest, fetcher, verbose, delayMs }) {
  const kandaDir = new Set(manifest.dir.map(d => d.id));
  const deltan = [];

  for (const entry of direktivLista) {
    const bet = dirBetFromEntry(entry);
    if (bet && kandaDir.has(bet)) continue; // redan i manifestet → inte nytt för oss

    // Avsändande departement står i list-entryts `organ` som kortkod ("U-dep").
    // Det fullständiga namnet saknas även i detalj-svaret för dir, så vi matchar
    // på organ-koden och gör ingen detalj-fetch när organ redan finns.
    let organ = entry.organ || null;
    let detailFetched = false;
    if (!organ) {
      try {
        const ds = await fetchDokumentstatus(entry.dok_id, { fetcher, delayMs });
        organ = extractDepartement(entry, ds);
        detailFetched = true;
      } catch (err) {
        if (verbose) process.stderr.write(`[jobB] dokumentstatus-fetch misslyckades för ${entry.dok_id}: ${err.message}\n`);
      }
    }

    if (!isUtbildningsdepOrgan(organ)) continue;

    deltan.push({
      typ: 'nytt-direktiv',
      beteckning: bet || entry.beteckning,
      titel: entry.titel || null,
      datum: entry.datum || null,
      departement: organ, // kortkod som API:t ger, t.ex. "U-dep"
      url: absUrl(entry.dokument_url_html) || `${API_BASE}/dokument/${entry.dok_id}`,
      detail_fetched: detailFetched,
    });
  }
  return deltan;
}

// Bygg full prop-beteckning från ett list-entry. Prop-listans `rm` har
// snedstrecksform ("2025/26") till skillnad från dir ("2024"); löpnumret står
// i `nummer`/`beteckning` som bart nummer ("260").
function propBetFromEntry(entry) {
  if (!entry) return null;
  const rm = entry.rm != null ? String(entry.rm) : null;
  const nr = entry.nummer != null ? String(entry.nummer)
    : (entry.beteckning != null ? String(entry.beteckning) : null);
  if (rm && nr && /^\d{4}\/\d{2}$/.test(rm) && /^\d+$/.test(nr)) {
    return `Prop. ${rm}:${nr}`;
  }
  return null;
}

// Jobb B2 (T2-fix-4): nya propositioner från Utbildningsdepartementet i
// fönstret som inte redan finns i manifestet. Till skillnad från dir bär
// prop-list-entries `organ` som FULLT NAMN ("Utbildningsdepartementet") —
// verifierat i T2-fix; isUtbildningsdepOrgan matchar båda formerna.
async function jobB2_nyaPropositioner({ propLista, manifest, fetcher, verbose, delayMs }) {
  const kandaProps = new Set(manifest.props.map(p => p.id));
  const deltan = [];

  for (const entry of propLista) {
    const bet = propBetFromEntry(entry);
    if (bet && kandaProps.has(bet)) continue; // redan i manifestet → inte ny för oss

    // Fullt departementsnamn finns på list-entryt; detalj-fetch bara som
    // fallback om organ saknas (samma mönster som jobb B).
    let organ = entry.organ || null;
    if (!organ) {
      try {
        const ds = await fetchDokumentstatus(entry.dok_id, { fetcher, delayMs });
        organ = extractDepartement(entry, ds);
      } catch (err) {
        if (verbose) process.stderr.write(`[jobB2] dokumentstatus-fetch misslyckades för ${entry.dok_id}: ${err.message}\n`);
      }
    }

    if (!isUtbildningsdepOrgan(organ)) continue;

    deltan.push({
      typ: 'ny-proposition',
      beteckning: bet || entry.beteckning,
      titel: entry.titel || null,
      datum: typeof entry.datum === 'string' ? entry.datum.slice(0, 10) : null,
      url: absUrl(entry.dokument_url_html) || `${API_BASE}/dokument/${entry.dok_id}`,
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
      direktiv_beteckning: dirBetFromEntry(entry) || entry.beteckning,
      kopplad_utredning: m[1],
      titel,
      datum: entry.datum || null,
      url: absUrl(entry.dokument_url_html) || `${API_BASE}/dokument/${entry.dok_id}`,
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
  // Jobb A: prop-status för icke-terminala manifest-props (se SIGNALREGEL)
  const jobA = await jobA_props({ manifest, dataIndex, fetcher, verbose, delayMs });
  deltan.push(...jobA.deltan);

  // Jobb B + C delar en list-fetch
  const direktivLista = await fetchDirektivWindow({ from, tom, fetcher, delayMs });
  const bDeltan = await jobB_nyttDirektivUtbildningsdep({ direktivLista, manifest, fetcher, verbose, delayMs });
  const cDeltan = jobC_tillaggsdirToTracked({ direktivLista, manifest });
  deltan.push(...bDeltan, ...cDeltan);

  // Jobb B2: nya propositioner i samma fönster
  const propLista = await fetchPropWindow({ from, tom, fetcher, delayMs });
  const b2Deltan = await jobB2_nyaPropositioner({ propLista, manifest, fetcher, verbose, delayMs });
  deltan.push(...b2Deltan);

  return {
    korning: new Date().toISOString(),
    fonster: { from, tom },
    antal_kontrollerade: {
      props: manifest.props.length,
      props_terminala_skippade: jobA.terminalaSkippade,
      props_i_fonster: propLista.length,
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
  jobB2_nyaPropositioner,
  jobC_tillaggsdirToTracked,
  fetchDirektivWindow,
  fetchPropWindow,
  lookupProp,
  normalizeDirBet,
  dirBetFromEntry,
  propBetFromEntry,
  isUtbildningsdepOrgan,
  buildDataIndex,
  extractStatusOgRelaterade,
  extractBetBeslut,
  extractDepartement,
  defaultWindow,
  TERMINAL_DATAFIL_STATUS,
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
