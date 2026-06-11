#!/usr/bin/env node
// rss.js — RSS-watcher mot regeringen.se (Sprint 10 T3 + T8 multi-feed).
// CJS, zero-dependency, Node 20+ inbyggd fetch.
//
// Bevakar dokumenttyper som riksdagens API INTE täcker, via RSS:
//   - lagrådsremisser (T3, regeringen.se)
//   - regeringsuppdrag (T8, regeringen.se) — uppdrag.json var tidigare obevakad
//   - regleringsbrev + ändringsbeslut (T9, statsliggaren/Statskontoret)
// Allt riksdagsmaterial (prop/dir/bet/SOU) sköts av riksdagen.js.
//
// STATSLIGGAREN (T9, verifierad 2026-06-11): statsliggaren har flyttat från
// ESV till Statskontoret — statskontoret.se är kanonisk domän (flödets
// channel-link och alla item-länkar pekar dit; "esv--" i feed-sökvägen är
// bara legacy-namngivning). Itemstruktur, empiriskt fastställd:
//   - <media:keywords> = "Myndighet,Departement,År" för myndighetsbrev,
//     "Departement,År" för anslagsbrev utan myndighet → departements- och
//     myndighetsfiltrering sker här
//   - <title> = "Ändringsbeslut Myndighet <namn> (beslutsdatum YYYY-MM-DD)"
//     resp. "Regleringsbrev ..." — ändringsbeslut SÄRSKILJS I TITELN, därför
//     ingen egen deltatyp; beslutsdatum extraheras ur titeln och används som
//     delta-datum (verifieringsregel: beslutsdatum, inte publiceringsdatum;
//     pubDate är publiceringen, typiskt dagen efter beslutet)
//   - <link> = rbid-sidan (https://www.statskontoret.se/statsliggaren/
//     regleringsbrev/?rbid=NNNNN) — primärkällan för triage
//   - FLÖDESDJUP: bara ~3 månader (86 poster, äldsta 2026-03-16 vid
//     verifiering 2026-06-11) — mycket grundare än regeringen.se-flödena.
//     Veckofönstret täcks, men backdaterade körningar längre bak flaggas
//     "ej fullt täckt". Decembers RB-beslut nås alltså INTE retroaktivt
//     från en vårkörning — de fångas bara av veckocronen när de sker.
//
// FEED-DISCOVERY (T3 2026-06-10, T8 2026-06-11 — samma metod):
// Feed-URL:erna genereras klient-side av filter-UI:t på respektive listsida.
// Metod: hämta sidan + /dist/js/rk-main.js. JS:et bygger länken som
// "/Filter/RssFeed?" + querystring från filter-modulens data-attribut:
//   - data-categories="<id>"        → preFilteredCategories (dokumenttypens taxonomi-id)
//   - data-rootpage="0"             → rootPageReference=0
//   - data-filtertype="Taxonomy"    → filterType=Taxonomy
//   - data-filterbytype="FilterablePageBase" → filterByType=FilterablePageBase
//   - data-displaylimited="True"    → displayLimited=true
// plus valda filterkryssrutor: Utbildningsdepartementet har data-cid="1294"
// → filteredContentCategories=1294.
// Taxonomi-id per dokumenttyp (ur data-categories på respektive sida):
//   - Lagrådsremiss = 2085 (https://www.regeringen.se/rattsliga-dokument/lagradsremiss/)
//   - Regeringsuppdrag = 1342 (https://www.regeringen.se/regeringsuppdrag/)
// Båda flödena verifierade: 100 poster vardera, varje item bär
// <category domain="1294">Utbildningsdepartementet</category> + sin
// dokumenttypskategori — filtren biter server-side, ingen departements-
// filtrering behövs i kod. Djup vid verifiering: lagrådsremiss → dec 2012,
// uppdrag → maj 2019. Fångade svar: fixtures/regeringen-*-udep.rss.xml
//
// Delta-format (samma stil som riksdagen.js), typ per feed-konfig:
//   { typ: "lagradsremiss"|"regeringsuppdrag", titel, datum, url }
//
// OBS fönstertäckning: RSS innehåller bara senaste N poster. Om --from ligger
// längre bak än äldsta posten i ett flöde kan vi inte skilja "tom vecka" från
// "för kort flöde" — rapporten flaggar då fonster_fullt_tackt: false för det
// flödet (per feed i floden[]).
//
// CLI:
//   node rss.js                          # default: tom=idag, from=idag-7d
//   node rss.js --from 2026-05-01 --tom 2026-05-31
//   node rss.js --verbose                # logga till stderr

'use strict';

function feedUrl(preFilteredCategories) {
  return 'https://www.regeringen.se/Filter/RssFeed'
    + '?filterType=Taxonomy'
    + '&filterByType=FilterablePageBase'
    + `&preFilteredCategories=${preFilteredCategories}`
    + '&rootPageReference=0'
    + '&filteredContentCategories=1294' // taxonomi-id: Utbildningsdepartementet
    + '&displayLimited=true';
}

// Myndighetsfilter för statsliggaren-flödet (T9). Motivering: U-dep omfattar
// alla lärosäten — ofiltrerat blir det ~50 regleringsbrev varje december.
// Högskolesektorn ligger utanför kartans fasta scopegräns (PROJECT_STATUS),
// så filtret är en strukturell gräns, inte en redaktionell veckobedömning.
// Listan är konfig: ny skolmyndighet = ny rad här, ingen logikändring.
const REGLERINGSBREV_MYNDIGHETER = [
  'Statens skolverk',
  'Statens skolinspektion',
  'Specialpedagogiska skolmyndigheten',
  'Skolforskningsinstitutet',
  'Skolväsendets överklagandenämnd',
];

// Tvåstegsfilter + berikning för statsliggaren-items. Returnerar null för
// items som ska släppas (andra departement, lärosäten, anslagsbrev utan
// myndighet). Delta-datum = beslutsdatum ur titeln, inte pubDate.
function transformRegleringsbrev(item) {
  const kw = ((item.extra && item.extra['media:keywords']) || '')
    .split(',').map(s => s.trim());
  if (!kw.includes('Utbildningsdepartementet')) return null;          // steg 1: departement
  const myndighet = REGLERINGSBREV_MYNDIGHETER.find(m => kw.includes(m));
  if (!myndighet) return null;                                        // steg 2: skolmyndighet
  const bm = /\(beslutsdatum (\d{4}-\d{2}-\d{2})\)/.exec(item.titel);
  return {
    titel: item.titel,
    datum: bm ? bm[1] : item.datum, // beslutsdatum; pubDate-fallback om titelformatet ändras
    url: item.url,
    myndighet,
  };
}

// Feed-konfigen driver hela kedjan: samma parser, fönsterlogik och
// täckningsflaggning per feed. Ny bevakning = ny rad här (+ discovery-notis i
// huvudkommentaren, sektion i rapport.js och täckningskartan i BEVAKNING.md).
// Valfria fält: extraTaggar (extra taggar att plocka per item, hamnar i
// item.extra) och transform (filter + berikning; null = släpp itemet).
const FEEDS = [
  { namn: 'lagradsremiss', deltatyp: 'lagradsremiss', url: feedUrl(2085) },
  { namn: 'regeringsuppdrag', deltatyp: 'regeringsuppdrag', url: feedUrl(1342) },
  {
    namn: 'regleringsbrev',
    deltatyp: 'regleringsbrev',
    url: 'https://www.statskontoret.se/specialsidor/rss/esv--regleringsbrev/',
    extraTaggar: ['media:keywords'],
    transform: transformRegleringsbrev,
  },
];

const USER_AGENT = 'reformkartan-bevakning (reformer.leide.se)';

// ----------------------------- HTTP-lager ------------------------------------

function makeHttpFetcher({ verbose = false } = {}) {
  return async function httpFetcher(url) {
    let response;
    try {
      response = await fetch(url, {
        headers: { 'User-Agent': USER_AGENT, 'Accept': 'application/rss+xml, application/xml, text/xml' },
      });
    } catch (err) {
      throw new Error(`Nätverksfel mot ${url}: ${err.message}`);
    }
    if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText} från ${url}`);
    const text = await response.text();
    if (verbose) process.stderr.write(`[fetch] ${url}\n[fetch] ${text.length} tecken\n`);
    return text;
  };
}

// ----------------------------- XML-strängparsning ----------------------------
// Ingen XML-lib (zero-dependency). Tål CDATA och attribut på taggarna.

// Plockar innehållet i första <tag ...>...</tag> ur ett fragment. CDATA packas
// upp; null om taggen saknas.
function extractTag(fragment, tag) {
  const re = new RegExp(`<${tag}(?:\\s[^>]*)?>([\\s\\S]*?)</${tag}>`, 'i');
  const m = re.exec(fragment);
  if (!m) return null;
  let inner = m[1].trim();
  const cdata = /^<!\[CDATA\[([\s\S]*?)\]\]>$/.exec(inner);
  if (cdata) inner = cdata[1].trim();
  return decodeEntities(inner);
}

function decodeEntities(s) {
  return s
    .replace(/&#x([0-9a-fA-F]+);/g, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(parseInt(dec, 10)))
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&'); // sist, annars dubbel-avkodas &amp;lt;
}

// RFC 822-datum ("Wed, 13 May 2026 13:27:52 +0200") → "2026-05-13".
// Datumdelarna tas direkt ur strängen — flödet anger svensk lokaltid och det
// är publiceringsdagen som visas på regeringen.se vi vill matcha. new Date()
// hade konverterat via värdmaskinens tidszon och kunnat flytta dygnet.
const MONTHS = { Jan: '01', Feb: '02', Mar: '03', Apr: '04', May: '05', Jun: '06',
                 Jul: '07', Aug: '08', Sep: '09', Oct: '10', Nov: '11', Dec: '12' };

function pubDateToIso(pubDate) {
  const m = /(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})/.exec(pubDate || '');
  if (!m) return null;
  return `${m[3]}-${MONTHS[m[2]]}-${m[1].padStart(2, '0')}`;
}

// Parsar hela flödet → [{ titel, datum, url, extra? }], nyast först (flödets
// ordning). extraTaggar plockar valfria taggar per item till item.extra
// (t.ex. media:keywords för statsliggaren). Fail loud: 0 items eller item
// utan obligatoriska fält → throw.
function parseFeed(xml, { extraTaggar = [] } = {}) {
  if (typeof xml !== 'string' || !/<rss[\s>]/i.test(xml)) {
    throw new Error('Oparsbart flöde: svaret är inte RSS-XML');
  }
  const itemBlocks = xml.match(/<item(?:\s[^>]*)?>[\s\S]*?<\/item>/gi) || [];
  if (itemBlocks.length === 0) {
    throw new Error('Oparsbart flöde: inga <item>-block hittades');
  }
  return itemBlocks.map((block, i) => {
    const titel = extractTag(block, 'title');
    const url = extractTag(block, 'link');
    const datum = pubDateToIso(extractTag(block, 'pubDate'));
    if (!titel || !url || !datum) {
      throw new Error(`Oparsbart item #${i + 1}: titel/link/pubDate saknas eller har okänt format`);
    }
    const item = { titel, datum, url };
    if (extraTaggar.length > 0) {
      item.extra = {};
      for (const tagg of extraTaggar) item.extra[tagg] = extractTag(block, tagg);
    }
    return item;
  });
}

// ----------------------------- Toppfunktion ----------------------------------

// Kör en feed genom hela kedjan: fetch → parse → transform → fönsterfilter
// → täckning.
async function buildFeedResult(feed, { from, tom, fetcher }) {
  const xml = await fetcher(feed.url);
  const items = parseFeed(xml, { extraTaggar: feed.extraTaggar || [] });

  // Äldsta post i flödet avgör om fönstret är fullt täckt — beräknas på det
  // RÅA flödet (före transform-filtret), det är flödets djup som ska mätas.
  // Sträcker sig fönstret bakom svansen kan en tom rapport bero på
  // flödesdjupet, inte på att inget publicerats.
  const aldsta = items.reduce((min, it) => (it.datum < min ? it.datum : min), items[0].datum);
  const fonsterFulltTackt = from >= aldsta;

  // Per-feed-transform: filtrering (null = släpp) + berikning (t.ex.
  // myndighet, beslutsdatum som datum). Utan transform passerar allt orört.
  const behallna = feed.transform ? items.map(feed.transform).filter(Boolean) : items;

  // ISO-datum jämförs lexikografiskt — inklusivt fönster.
  const iFonster = behallna.filter(it => it.datum >= from && it.datum <= tom);

  return {
    meta: {
      namn: feed.namn,
      kalla: feed.url,
      antal_i_flodet: items.length,
      aldsta_post_i_flodet: aldsta,
      fonster_fullt_tackt: fonsterFulltTackt,
      ...(fonsterFulltTackt ? {} : { varning: 'fönster ej fullt täckt av flödet' }),
    },
    deltan: iFonster.map(({ extra, ...it }) => ({ typ: feed.deltatyp, ...it })),
  };
}

async function buildReport({ from, tom, fetcher, verbose = false, feeds = FEEDS } = {}) {
  if (!from || !tom) throw new Error('buildReport: from och tom krävs (YYYY-MM-DD)');
  if (typeof fetcher !== 'function') fetcher = makeHttpFetcher({ verbose });

  const floden = [];
  const deltan = [];
  for (const feed of feeds) {
    try {
      const resultat = await buildFeedResult(feed, { from, tom, fetcher });
      floden.push(resultat.meta);
      deltan.push(...resultat.deltan);
    } catch (err) {
      // Per-feed-degradering (DEC-008): ett onåbart flöde får inte nolla
      // övriga flödens täckning (statskontoret.se blockerar t.ex. GitHub-
      // runners). Felet tystas INTE — feed_fel landar som 🔴-varning i
      // veckorapporten. Faller ALLA flöden är RSS-bevakningen död → throw.
      floden.push({ namn: feed.namn, kalla: feed.url, feed_fel: err.message });
      if (verbose) process.stderr.write(`[feed:${feed.namn}] FEL: ${err.message}\n`);
    }
  }
  if (floden.length > 0 && floden.every(f => f.feed_fel)) {
    throw new Error(`Alla ${floden.length} RSS-flöden föll: ${floden.map(f => `${f.namn}: ${f.feed_fel}`).join(' | ')}`);
  }

  return {
    korning: new Date().toISOString(),
    fonster: { from, tom },
    floden,
    deltan,
  };
}

// ----------------------------- CLI -------------------------------------------

function parseArgs(argv) {
  const opts = { from: null, tom: null, verbose: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--from') opts.from = argv[++i];
    else if (a === '--tom') opts.tom = argv[++i];
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
  FEEDS,
  REGLERINGSBREV_MYNDIGHETER,
  buildReport,
  // exporterade för test
  buildFeedResult,
  transformRegleringsbrev,
  parseFeed,
  extractTag,
  decodeEntities,
  pubDateToIso,
  defaultWindow,
};

if (require.main === module) {
  (async () => {
    const opts = parseArgs(process.argv.slice(2));
    if (opts.help) {
      process.stdout.write('Användning: node rss.js [--from YYYY-MM-DD] [--tom YYYY-MM-DD] [--verbose]\n');
      process.exit(0);
    }
    const win = defaultWindow();
    const from = opts.from || win.from;
    const tom = opts.tom || win.tom;
    try {
      const rapport = await buildReport({ from, tom, verbose: opts.verbose });
      process.stdout.write(JSON.stringify(rapport, null, 2) + '\n');
    } catch (err) {
      process.stderr.write(`FEL: ${err.message}\n`);
      // ALDRIG tom rapport vid fel — exit 1 så Action:en kan flagga
      process.exit(1);
    }
  })();
}
