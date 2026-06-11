#!/usr/bin/env node
// rss.js — RSS-watcher för lagrådsremisser (Sprint 10 T3).
// CJS, zero-dependency, Node 20+ inbyggd fetch.
//
// Riksdagens API täcker INTE lagrådsremisser — detta skript bevakar dem via
// regeringen.se:s RSS-flöde, filtrerat på Utbildningsdepartementet. Det är
// RSS:ens enda jobb; allt annat sköts av riksdagen.js.
//
// FEED-DISCOVERY (utförd 2026-06-10, Sprint 10 T3):
// Feed-URL:erna genereras klient-side av filter-UI:t på
// https://www.regeringen.se/rattsliga-dokument/lagradsremiss/.
// Metod: hämtade sidan + /dist/js/rk-main.js. JS:et bygger länken som
// "/Filter/RssFeed?" + querystring från filter-modulens data-attribut:
//   - data-categories="2085"        → preFilteredCategories=2085 (taxonomi: Lagrådsremiss)
//   - data-rootpage="0"             → rootPageReference=0
//   - data-filtertype="Taxonomy"    → filterType=Taxonomy
//   - data-filterbytype="FilterablePageBase" → filterByType=FilterablePageBase
//   - data-displaylimited="True"    → displayLimited=true
// plus valda filterkryssrutor: Utbildningsdepartementet har data-cid="1294"
// → filteredContentCategories=1294.
// Verifierad 2026-06-10: flödet svarar med 100 poster (maj 2026 → dec 2012),
// varje item bär <category domain="1294">Utbildningsdepartementet</category>
// och <category domain="2085">Lagrådsremiss</category> — filtret biter alltså
// server-side, ingen departementsfiltrering behövs i kod.
// Fångat svar: fixtures/regeringen-lagradsremiss-udep.rss.xml
//
// Delta-format (samma stil som riksdagen.js):
//   { typ: "lagradsremiss", titel, datum, url }
//
// OBS fönstertäckning: RSS innehåller bara senaste N poster. Om --from ligger
// längre bak än äldsta posten i flödet kan vi inte skilja "tom vecka" från
// "för kort flöde" — rapporten flaggar då fonster_fullt_tackt: false.
//
// CLI:
//   node rss.js                          # default: tom=idag, from=idag-7d
//   node rss.js --from 2026-05-01 --tom 2026-05-31
//   node rss.js --verbose                # logga till stderr

'use strict';

const FEED_URL = 'https://www.regeringen.se/Filter/RssFeed'
  + '?filterType=Taxonomy'
  + '&filterByType=FilterablePageBase'
  + '&preFilteredCategories=2085'   // taxonomi-id: Lagrådsremiss
  + '&rootPageReference=0'
  + '&filteredContentCategories=1294' // taxonomi-id: Utbildningsdepartementet
  + '&displayLimited=true';

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

// Parsar hela flödet → [{ titel, datum, url }], nyast först (flödets ordning).
// Fail loud: 0 items eller item utan obligatoriska fält → throw.
function parseFeed(xml) {
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
    return { titel, datum, url };
  });
}

// ----------------------------- Toppfunktion ----------------------------------

async function buildReport({ from, tom, fetcher, verbose = false } = {}) {
  if (!from || !tom) throw new Error('buildReport: from och tom krävs (YYYY-MM-DD)');
  if (typeof fetcher !== 'function') fetcher = makeHttpFetcher({ verbose });

  const xml = await fetcher(FEED_URL);
  const items = parseFeed(xml);

  // ISO-datum jämförs lexikografiskt — inklusivt fönster.
  const iFonster = items.filter(it => it.datum >= from && it.datum <= tom);

  // Äldsta post i flödet avgör om fönstret är fullt täckt. Sträcker sig
  // fönstret bakom flödets svans kan en tom rapport bero på flödesdjupet,
  // inte på att inget publicerats.
  const aldsta = items.reduce((min, it) => (it.datum < min ? it.datum : min), items[0].datum);
  const fonsterFulltTackt = from >= aldsta;

  return {
    korning: new Date().toISOString(),
    fonster: { from, tom },
    kalla: FEED_URL,
    antal_i_flodet: items.length,
    aldsta_post_i_flodet: aldsta,
    fonster_fullt_tackt: fonsterFulltTackt,
    ...(fonsterFulltTackt ? {} : { varning: 'fönster ej fullt täckt av flödet' }),
    deltan: iFonster.map(it => ({ typ: 'lagradsremiss', titel: it.titel, datum: it.datum, url: it.url })),
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
  FEED_URL,
  buildReport,
  // exporterade för test
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
