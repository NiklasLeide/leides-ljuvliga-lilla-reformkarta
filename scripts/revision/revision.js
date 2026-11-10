#!/usr/bin/env node
// revision.js — revisionsskript för strukturerade fält (Sprint 14 T2).
// CJS, zero-dependency, Node 20+ inbyggd fetch.
//
// För varje SPÅRAD proposition (reforms.json `ref`, utredningar.json `prop`) och
// varje SPÅRAD utredning (utredningar.json) hämtas aktuellt läge ur riksdagens
// öppna data, och en diffrapport skrivs mot datafilerna. Skriptet ÄNDRAR ALDRIG
// datafiler — det rapporterar. Klassning (RUTIN/BEDÖMNING) och patch görs av
// människa i ändringslistan (DEC-018). Sprint 15 bygger automatpublicering på
// rapportens JSON (DEC-019).
//
// RSKR-REGELN (Sprint 14, eget test i revision.test.js):
//   Ett riksdagsbeslut räknas FÖRST när propositionens betänkande har
//   (1) en beslutsaktivitet (dokaktivitet kod "BES") med status "inträffat"
//   OCH (2) en rskr-referens (dokreferens referenstyp "rskr").
//   Propens dokument.status ("Klar") betyder bara PUBLICERAD och ignoreras.
//   Betänkandets BES-aktivitet finns även före beslut (status "planerat") —
//   att BES finns räcker alltså inte (se bevakning/riksdagen.js SIGNALREGEL).
//
// MATCHNING UTREDNING ↔ RIKSDAGEN (verifierat mot live-API 2026-11-10):
//   - Direktiv: list-entryts `undertitel` bär "kommittébeteckning: U 2024:01"
//     för tilläggsdirektiv (och för huvuddirektiv efter att kommittén fått
//     beteckning). Fritextsök på beteckningen + exakt filtrering på
//     undertiteln. Varje direktiv i datafilen slås dessutom upp direkt
//     (doktyp=dir&rm=ÅÅÅÅ&bet=N) för datum och kommittékoppling.
//   - SOU: bär inget departement och ingen kommittébeteckning. Titelsidan i
//     `summary` innehåller "Slutbetänkande av <utredningsnamn>" /
//     "Delbetänkande av …" / "Betänkande av …". Namnet jämförs (normaliserat)
//     exakt mot utredningens `titel`. Ingen fuzzy-matchning — hellre miss än
//     falsk träff; missar fångas när SOU:n i datafilen slås upp direkt.
//
// CLI:
//   node scripts/revision/revision.js                 # skriver docs/revision/revision-<idag>.{json,md}
//   node scripts/revision/revision.js --datum 2026-11-10 --out docs/revision
//   node scripts/revision/revision.js --data /annan/data --verbose
// Går att köra om: samma datum skriver över samma filer, och utfallet beror
// bara på datafilerna + API:ts svar.

'use strict';

const fs = require('fs');
const path = require('path');

const API_BASE = 'https://data.riksdagen.se';
const USER_AGENT = 'reformkartan-revision (reformer.leide.se)';
const DELAY_MS_DEFAULT = 300;

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const asArray = (x) => (x == null ? [] : (Array.isArray(x) ? x : [x]));
const datum10 = (s) => (typeof s === 'string' && s.length >= 10 ? s.slice(0, 10) : null);
const norm = (s) => (typeof s === 'string' ? s.replace(/\s+/g, ' ').trim().toLowerCase() : '');
const absUrl = (raw) => (typeof raw === 'string' && raw.startsWith('//') ? `https:${raw}` : raw || null);

// ----------------------------- HTTP-lager ------------------------------------

function makeHttpFetcher({ verbose = false } = {}) {
  return async function httpFetcher(url) {
    let response;
    try {
      response = await fetch(url, { headers: { 'User-Agent': USER_AGENT, Accept: 'application/json' } });
    } catch (err) {
      throw new Error(`Nätverksfel mot ${url}: ${err.message}`);
    }
    if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText} från ${url}`);
    try {
      const json = await response.json();
      if (verbose) process.stderr.write(`[fetch] ${url}\n`);
      return json;
    } catch (err) {
      throw new Error(`Ogiltigt JSON-svar från ${url}: ${err.message}`);
    }
  };
}

function listDocs(data) {
  return asArray(data && data.dokumentlista && data.dokumentlista.dokument);
}

// ----------------------------- Rskr-regeln -----------------------------------

// Ren funktion över ett BETÄNKANDES dokumentstatus-svar. Se RSKR-REGELN ovan.
function betankandeBeslut(betDokstatus) {
  const ds = (betDokstatus && betDokstatus.dokumentstatus) || {};
  const dok = ds.dokument || {};

  const upg = {};
  for (const u of asArray(ds.dokuppgift && ds.dokuppgift.uppgift)) if (u && u.kod) upg[u.kod] = u.text;

  const bes = asArray(ds.dokaktivitet && ds.dokaktivitet.aktivitet).find(a => a && a.kod === 'BES');
  const besInträffat = !!(bes && bes.status === 'inträffat');

  const rskrRef = asArray(ds.dokreferens && ds.dokreferens.referens).find(r => r && r.referenstyp === 'rskr');
  const rskr = rskrRef
    ? (rskrRef.ref_dok_rm && rskrRef.ref_dok_bet ? `${rskrRef.ref_dok_rm}:${rskrRef.ref_dok_bet}` : (rskrRef.uppgift || null))
    : null;

  return {
    bet: dok.rm && dok.beteckning ? `${dok.rm}:${dok.beteckning}` : null,
    dok_id: dok.dok_id || null,
    bes_status: bes ? bes.status || null : null,
    rskr,
    beslutsdatum: besInträffat ? (datum10(upg.beslutdatumtid) || datum10(bes.datum)) : null,
    statustext: upg.statustext || null,
    // REGELN: båda villkoren krävs.
    riksdagsbeslut: besInträffat && !!rskr,
    url: dok.dok_id ? `${API_BASE}/dokument/${dok.dok_id}.html` : null,
  };
}

// ----------------------------- API-uppslag -----------------------------------

async function lookupDok({ doktyp, rm, nr, fetcher, delayMs }) {
  const params = new URLSearchParams({ doktyp, rm, bet: nr, utformat: 'json', sz: '5' });
  const url = `${API_BASE}/dokumentlista/?${params}`;
  const docs = listDocs(await fetcher(url));
  await sleep(delayMs);
  const exact = docs.find(d => String(d.rm) === String(rm) && String(d.beteckning) === String(nr) && d.doktyp === doktyp);
  return { entry: exact || null, query_url: url };
}

async function fetchDokumentstatus(dok_id, { fetcher, delayMs }) {
  const data = await fetcher(`${API_BASE}/dokumentstatus/${encodeURIComponent(dok_id)}.json`);
  await sleep(delayMs);
  return data;
}

// Propens läge: hittas den, vilka betänkanden, och har riksdagen beslutat
// enligt rskr-regeln?
async function propLage(beteckning, { fetcher, delayMs }) {
  const m = /^Prop\.\s*(\d{4}\/\d{2}):(\d+)$/.exec(beteckning);
  if (!m) return { beteckning, fel: 'ogiltig beteckning' };
  const { entry, query_url } = await lookupDok({ doktyp: 'prop', rm: m[1], nr: m[2], fetcher, delayMs });
  if (!entry) return { beteckning, hittad: false, query_url };

  const ds = await fetchDokumentstatus(entry.dok_id, { fetcher, delayMs });
  const refs = asArray(ds && ds.dokumentstatus && ds.dokumentstatus.dokreferens && ds.dokumentstatus.dokreferens.referens);
  const betRefs = refs.filter(r => r && r.referenstyp === 'behandlas_i' && r.ref_dok_id);

  const betankanden = [];
  for (const r of betRefs) {
    const bds = await fetchDokumentstatus(r.ref_dok_id, { fetcher, delayMs });
    betankanden.push(betankandeBeslut(bds));
  }
  return {
    beteckning,
    hittad: true,
    dok_id: entry.dok_id,
    titel: entry.titel || null,
    datum: datum10(entry.datum),
    publiceringsstatus: entry.status || null, // "Klar" = publicerad, INTE beslut
    url: absUrl(entry.dokument_url_html) || `${API_BASE}/dokument/${entry.dok_id}.html`,
    betankanden,
    riksdagsbeslut: betankanden.length > 0 && betankanden.every(b => b.riksdagsbeslut),
  };
}

// Kommittébeteckning ur dir-entryts undertitel ("kommittébeteckning: U 2024:01").
function kommittebeteckning(entry) {
  const m = /kommittébeteckning:\s*([A-ZÅÄÖ]{1,3}\s+\d{4}:\d+)/i.exec((entry && entry.undertitel) || '');
  return m ? m[1].replace(/\s+/g, ' ') : null;
}

function dirNr(entry) {
  return entry && entry.rm && entry.beteckning ? `Dir. ${entry.rm}:${entry.beteckning}` : null;
}

async function direktivForKommitte(bet, { fetcher, delayMs }) {
  const params = new URLSearchParams({ doktyp: 'dir', sok: `"${bet}"`, utformat: 'json', sz: '50' });
  const docs = listDocs(await fetcher(`${API_BASE}/dokumentlista/?${params}`));
  await sleep(delayMs);
  return docs.filter(d => kommittebeteckning(d) === bet);
}

// SOU-entryts betänkandetyp + utredningsnamn ur titelsidan i summary.
function souAvsandare(entry) {
  const text = (entry && (entry.summary || entry.notis)) || '';
  const m = /\b(Slut|Del)?betänkande av ([\s\S]*?)(?:\n\s*Stockholm|\nSOU |$)/i.exec(text);
  if (!m) return { typ: null, av: null };
  const typ = m[1] ? (m[1].toLowerCase() === 'slut' ? 'slut' : 'del') : null;
  return { typ, av: m[2].replace(/\s+/g, ' ').trim() || null };
}

function souNr(entry) {
  return entry && entry.rm && entry.beteckning ? `SOU ${entry.rm}:${entry.beteckning}` : null;
}

// Alla SOU från ett startdatum, med paginering via @nasta_sida (max 200/sida).
async function allaSou(from, { fetcher, delayMs }) {
  const params = new URLSearchParams({ doktyp: 'sou', from, sz: '200', sort: 'datum', sortorder: 'asc', utformat: 'json' });
  let url = `${API_BASE}/dokumentlista/?${params}`;
  const out = [];
  for (let sida = 0; url && sida < 50; sida++) {
    const data = await fetcher(url);
    await sleep(delayMs);
    out.push(...listDocs(data));
    const nasta = data && data.dokumentlista && data.dokumentlista['@nasta_sida'];
    url = nasta ? nasta.replace(/^http:/, 'https:') : null;
  }
  return out;
}

// ----------------------------- Diff-logik (rena funktioner) ------------------

// Ett fynd = en avvikelse mellan datafil och riksdagen. Fältet `typ` beskriver
// vilken sorts avvikelse; klassning RUTIN/BEDÖMNING görs i ändringslistan.
function fynd(fil, post, falt, nuvarde, api, url, typ, notering = null) {
  return { fil, post, falt, nuvarde: nuvarde === undefined ? null : nuvarde, api: api === undefined ? null : api, url, typ, notering };
}

function diffReformMotProp(reform, lage) {
  const ut = [];
  const F = (falt, nu, api, url, typ, not) => ut.push(fynd('reforms.json', reform.id, falt, nu, api, url, typ, not));
  if (!lage.hittad) {
    F('ref', reform.ref, null, lage.query_url, 'prop-saknas-i-api');
    return ut;
  }
  if (lage.riksdagsbeslut && reform.status !== 'beslutad') {
    F('status', reform.status, 'beslutad', lage.betankanden[0].url, 'status-efter-riksdagsbeslut');
  }
  if (!lage.riksdagsbeslut && reform.status === 'beslutad') {
    const b = lage.betankanden[0];
    F('status', reform.status, b ? `BES ${b.bes_status || 'saknas'}, rskr ${b.rskr || 'saknas'}` : 'inget betänkande',
      b ? b.url : lage.url, 'beslutad-utan-rskr-regel');
  }
  // transition renderas på reformkortet — granskas mot betänkandet/betänkandena.
  // En prop kan behandlas i flera betänkanden (t.ex. Prop. 2025/26:194 i
  // UbU23–UbU26, verifierat 2026-11-10). Varje betänkande ger HÖGST ett fynd:
  //   - inget betänkande nämns alls → ett fynd med samtliga bet/rskr/datum
  //   - nämnt betänkande → rskr resp. beslutsdatum kontrolleras
  //   - ytterligare betänkande (annat nämns redan) → ett informationsfynd
  const tr = reform.transition || '';
  const besk = (b) => [b.bet && `bet. ${b.bet}`, b.rskr && `rskr. ${b.rskr}`, b.beslutsdatum && `beslutsdatum ${b.beslutsdatum}`].filter(Boolean).join(', ');
  const namnda = lage.betankanden.filter(b => b.bet && tr.includes(b.bet));
  if (!namnda.length && lage.betankanden.length) {
    F('transition', tr, lage.betankanden.map(besk).join('; '), lage.betankanden[0].url, 'transition-saknar-riksdagsbeslut');
    return ut;
  }
  for (const b of lage.betankanden) {
    if (!namnda.includes(b)) { F('transition', tr, besk(b), b.url, 'ytterligare-betankande'); continue; }
    if (b.riksdagsbeslut && !tr.includes(b.rskr)) F('transition', tr, `rskr. ${b.rskr}`, b.url, 'transition-saknar-rskr');
    if (b.riksdagsbeslut && b.beslutsdatum && !tr.includes(b.beslutsdatum)) {
      F('transition', tr, `beslutsdatum ${b.beslutsdatum}`, b.url, 'transition-saknar-beslutsdatum');
    }
  }
  return ut;
}

// utredning: post ur utredningar.json. api: { direktivKommitte: [entries],
// direktivUppslag: {nr: {entry, query_url}}, souMatchade: [entries],
// souUppslag: {nr: {entry, query_url}} }
function diffUtredning(u, api) {
  const ut = [];
  const F = (falt, nu, v, url, typ, not) => ut.push(fynd('utredningar.json', u.id, falt, nu, v, url, typ, not));
  const dataDir = asArray(u.direktiv);
  const dataDirNr = new Set(dataDir.map(d => d && d.nr).filter(Boolean));

  for (const d of dataDir) {
    if (!d || !d.nr) continue;
    const upp = api.direktivUppslag[d.nr];
    if (!upp || !upp.entry) { F(`direktiv ${d.nr}`, d.nr, null, upp ? upp.query_url : null, 'direktiv-saknas-i-api'); continue; }
    const e = upp.entry;
    const url = absUrl(e.dokument_url_html);
    if (d.datum && datum10(e.datum) && d.datum !== datum10(e.datum)) {
      F(`direktiv ${d.nr}.datum`, d.datum, datum10(e.datum), url, 'datum-avviker');
    }
    const kb = kommittebeteckning(e);
    if (kb && u.beteckning && kb !== u.beteckning) {
      F(`direktiv ${d.nr}.kommitté`, u.beteckning, kb, url, 'direktiv-annan-kommitte', e.titel || null);
    }
    if (d.titel == null && e.titel) F(`direktiv ${d.nr}.titel`, null, e.titel, url, 'titel-saknas-i-data');
  }
  for (const e of api.direktivKommitte) {
    const nr = dirNr(e);
    if (nr && !dataDirNr.has(nr)) {
      F('direktiv', null, `${nr} (${datum10(e.datum)}) ${e.titel || ''}`.trim(), absUrl(e.dokument_url_html), 'nytt-direktiv-i-api');
    }
  }

  const dataSou = asArray(u.betankanden);
  const dataSouNr = new Set(dataSou.map(b => b && b.nr).filter(Boolean));
  for (const b of dataSou) {
    if (!b || !b.nr) continue;
    const upp = api.souUppslag[b.nr];
    if (!upp || !upp.entry) { F(`betankanden ${b.nr}`, b.nr, null, upp ? upp.query_url : null, 'sou-saknas-i-api'); continue; }
    const e = upp.entry;
    const url = absUrl(e.dokument_url_html);
    if (b.datum && datum10(e.datum) && b.datum !== datum10(e.datum)) {
      F(`betankanden ${b.nr}.datum`, b.datum, datum10(e.datum), url, 'datum-avviker');
    }
    const { typ } = souAvsandare(e);
    if (typ && b.typ && typ !== b.typ) F(`betankanden ${b.nr}.typ`, b.typ, typ, url, 'betankandetyp-avviker');
  }
  for (const e of api.souMatchade) {
    const nr = souNr(e);
    if (nr && !dataSouNr.has(nr)) {
      const { typ } = souAvsandare(e);
      F('betankanden', null, `${nr} (${datum10(e.datum)}) ${e.titel || ''}${typ ? ` [${typ}]` : ''}`.trim(), absUrl(e.dokument_url_html), 'nytt-betankande-i-api');
    }
  }
  const harSlut = api.souMatchade.some(e => souAvsandare(e).typ === 'slut') ||
    dataSou.some(b => b && b.typ === 'slut');
  if (harSlut && u.status === 'pagaende') {
    F('status', u.status, 'slutbetänkande finns', null, 'pagaende-med-slutbetankande');
  }
  return ut;
}

// ----------------------------- Huvudflöde ------------------------------------

function readJson(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (err) { throw new Error(`Kunde inte läsa ${p}: ${err.message}`); }
}

function nrParts(nr, prefix) {
  const m = new RegExp(`^${prefix}\\s*(\\d{4}):(\\d+)$`).exec(nr || '');
  return m ? { rm: m[1], nr: m[2] } : null;
}

async function buildRevision({ dataDir, fetcher, delayMs = DELAY_MS_DEFAULT, verbose = false, log = () => {} }) {
  const reforms = readJson(path.join(dataDir, 'reforms.json'));
  const utredningar = readJson(path.join(dataDir, 'utredningar.json'));
  const fel = [];
  const fyndLista = [];

  // --- Propositioner ---
  const props = new Map(); // beteckning -> { reforms: [], utredningar: [] }
  for (const r of reforms) if (/^Prop\./.test(r.ref || '')) {
    if (!props.has(r.ref)) props.set(r.ref, { reforms: [], utredningar: [] });
    props.get(r.ref).reforms.push(r);
  }
  for (const u of utredningar) if (/^Prop\./.test(u.prop || '')) {
    if (!props.has(u.prop)) props.set(u.prop, { reforms: [], utredningar: [] });
    props.get(u.prop).utredningar.push(u.id);
  }
  const propLagen = [];
  for (const [bet, ctx] of [...props.entries()].sort()) {
    log(`prop ${bet}`);
    try {
      const lage = await propLage(bet, { fetcher, delayMs });
      lage.reform_ids = ctx.reforms.map(r => r.id);
      lage.utrednings_ids = ctx.utredningar;
      propLagen.push(lage);
      for (const r of ctx.reforms) fyndLista.push(...diffReformMotProp(r, lage));
    } catch (err) {
      fel.push({ objekt: bet, fel: err.message });
    }
  }

  // --- Utredningar ---
  const tidigast = utredningar.map(u => u.tillsatt).filter(Boolean).sort()[0] || '2020-01-01';
  let souLista = [];
  try {
    log(`SOU från ${tidigast.slice(0, 4)}-01-01`);
    souLista = await allaSou(`${tidigast.slice(0, 4)}-01-01`, { fetcher, delayMs });
  } catch (err) {
    fel.push({ objekt: 'SOU-lista', fel: err.message });
  }
  const souByNr = new Map(souLista.map(e => [souNr(e), e]));

  const utredningsLagen = [];
  for (const u of utredningar) {
    log(`utredning ${u.beteckning}`);
    try {
      const api = { direktivKommitte: [], direktivUppslag: {}, souMatchade: [], souUppslag: {} };
      if (u.beteckning) api.direktivKommitte = await direktivForKommitte(u.beteckning, { fetcher, delayMs });
      for (const d of asArray(u.direktiv)) {
        const p = d && nrParts(d.nr, 'Dir\\.');
        if (p) api.direktivUppslag[d.nr] = await lookupDok({ doktyp: 'dir', rm: p.rm, nr: p.nr, fetcher, delayMs });
      }
      api.souMatchade = souLista.filter(e => { const { av } = souAvsandare(e); return av && norm(av) === norm(u.titel); });
      for (const b of asArray(u.betankanden)) {
        if (!b || !b.nr) continue;
        if (souByNr.has(b.nr)) { api.souUppslag[b.nr] = { entry: souByNr.get(b.nr), query_url: null }; continue; }
        const p = nrParts(b.nr, 'SOU');
        if (p) api.souUppslag[b.nr] = await lookupDok({ doktyp: 'sou', rm: p.rm, nr: p.nr, fetcher, delayMs });
      }
      utredningsLagen.push({
        id: u.id, beteckning: u.beteckning, titel: u.titel, status: u.status,
        direktiv_i_api: api.direktivKommitte.map(e => ({ nr: dirNr(e), datum: datum10(e.datum), titel: e.titel })),
        sou_i_api: api.souMatchade.map(e => ({ nr: souNr(e), datum: datum10(e.datum), titel: e.titel, typ: souAvsandare(e).typ })),
      });
      fyndLista.push(...diffUtredning(u, api));
    } catch (err) {
      fel.push({ objekt: u.beteckning || u.id, fel: err.message });
    }
  }

  return { propositioner: propLagen, utredningar: utredningsLagen, fynd: fyndLista, fel };
}

// ----------------------------- Rapport ---------------------------------------

const cell = (v) => (v == null ? '—' : String(v).replace(/\|/g, '\\|').replace(/\n/g, ' '));
const kort = (v, n = 120) => { const s = cell(v); return s.length > n ? `${s.slice(0, n)}…` : s; };

function renderMarkdown(rapport, { datum }) {
  const L = [];
  L.push(`# Revisionsrapport ${datum}`, '');
  L.push('Genererad av `scripts/revision/revision.js` mot riksdagens öppna data. Skriptet ändrar inga datafiler.');
  L.push('Rskr-regeln: riksdagsbeslut räknas först när betänkandet har BES-aktivitet med status "inträffat" OCH rskr-referens.', '');
  L.push(`Sammanfattning: ${rapport.propositioner.length} propositioner, ${rapport.utredningar.length} utredningar, ${rapport.fynd.length} fynd, ${rapport.fel.length} fel.`, '');

  L.push('## Fynd', '');
  if (!rapport.fynd.length) L.push('Inga avvikelser.', '');
  else {
    L.push('| # | Fil | Post | Fält | Nuvärde | Riksdagen | Typ | Källa |', '|---|---|---|---|---|---|---|---|');
    rapport.fynd.forEach((f, i) => L.push(`| ${i + 1} | ${f.fil} | ${f.post} | ${cell(f.falt)} | ${kort(f.nuvarde)} | ${kort(f.api)}${f.notering ? ` (${kort(f.notering, 80)})` : ''} | ${f.typ} | ${f.url || '—'} |`));
    L.push('');
  }

  L.push('## Propositioner', '');
  L.push('| Prop. | Titel | Betänkande | BES | Rskr | Beslutsdatum | Riksdagsbeslut | Poster |', '|---|---|---|---|---|---|---|---|');
  for (const p of rapport.propositioner) {
    if (!p.hittad) { L.push(`| ${p.beteckning} | EJ HITTAD | — | — | — | — | — | ${[...(p.reform_ids || []), ...(p.utrednings_ids || [])].join(', ')} |`); continue; }
    const b = p.betankanden;
    L.push(`| [${p.beteckning}](${p.url}) | ${kort(p.titel, 60)} | ${b.map(x => x.bet).join(', ') || '—'} | ${b.map(x => x.bes_status || '—').join(', ') || '—'} | ${b.map(x => x.rskr || '—').join(', ') || '—'} | ${b.map(x => x.beslutsdatum || '—').join(', ') || '—'} | ${p.riksdagsbeslut ? 'ja' : 'nej'} | ${[...p.reform_ids, ...p.utrednings_ids].join(', ')} |`);
  }
  L.push('');

  L.push('## Utredningar', '');
  L.push('| Beteckning | Status (data) | Direktiv i riksdagen (kommittébeteckning) | SOU i riksdagen (titelmatch) |', '|---|---|---|---|');
  for (const u of rapport.utredningar) {
    L.push(`| ${u.beteckning} | ${u.status} | ${u.direktiv_i_api.map(d => d.nr).join(', ') || '—'} | ${u.sou_i_api.map(s => `${s.nr}${s.typ ? ` [${s.typ}]` : ''}`).join(', ') || '—'} |`);
  }
  L.push('');

  if (rapport.fel.length) {
    L.push('## Fel', '');
    for (const f of rapport.fel) L.push(`- ${f.objekt}: ${f.fel}`);
    L.push('');
  }
  return L.join('\n');
}

// ----------------------------- CLI -------------------------------------------

function parseArgs(argv) {
  const a = { data: path.join(__dirname, '..', '..', 'data'), out: path.join(__dirname, '..', '..', 'docs', 'revision'), datum: new Date().toISOString().slice(0, 10), verbose: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--data') a.data = argv[++i];
    else if (argv[i] === '--out') a.out = argv[++i];
    else if (argv[i] === '--datum') a.datum = argv[++i];
    else if (argv[i] === '--verbose') a.verbose = true;
    else throw new Error(`Okänt argument: ${argv[i]}`);
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(a.datum)) throw new Error(`--datum måste vara YYYY-MM-DD: ${a.datum}`);
  return a;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const rapport = await buildRevision({
    dataDir: args.data,
    fetcher: makeHttpFetcher({ verbose: args.verbose }),
    log: (m) => process.stderr.write(`[revision] ${m}\n`),
  });
  rapport.datum = args.datum;
  fs.mkdirSync(args.out, { recursive: true });
  const base = path.join(args.out, `revision-${args.datum}`);
  fs.writeFileSync(`${base}.json`, JSON.stringify(rapport, null, 2) + '\n');
  fs.writeFileSync(`${base}.md`, renderMarkdown(rapport, { datum: args.datum }) + '\n');
  process.stderr.write(`[revision] ${rapport.fynd.length} fynd, ${rapport.fel.length} fel → ${base}.{json,md}\n`);
  // Fail loud: API-fel ska synas som nollskild exit, men rapporten skrivs ändå.
  if (rapport.fel.length) process.exitCode = 2;
}

if (require.main === module) {
  main().catch(err => { process.stderr.write(`[revision] FEL: ${err.stack || err.message}\n`); process.exit(1); });
}

module.exports = {
  betankandeBeslut, kommittebeteckning, souAvsandare, souNr, dirNr,
  diffReformMotProp, diffUtredning, buildRevision, renderMarkdown, parseArgs,
};
