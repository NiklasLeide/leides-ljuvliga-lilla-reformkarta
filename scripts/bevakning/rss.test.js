// rss.test.js — enhetstest för RSS-watchern (Sprint 10 T3 + T8 multi-feed).
// Inga ramverk: node:test + node:assert. Kör: node --test scripts/bevakning/rss.test.js
//
// Kärntesterna drivs av RIKTIGA, fångade feed-svar (fixtures/
// regeringen-*-udep.rss.xml) — samma lärdom som T2-fix: mockar mot antagna
// format kan vara gröna medan skarp körning är död. CDATA-fallet testas med
// syntetisk XML eftersom de riktiga flödena inte använder CDATA men formatet
// kan ändras.
//
// Lagrådsremiss-testerna från T3 kör med feeds-injektion ([FEEDS[0]]) och har
// oförändrat beteende efter T8-refactorn — bara rapportformen (floden[]) är ny.

'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {
  buildReport,
  buildFeedResult,
  transformRegleringsbrev,
  parseFeed,
  extractTag,
  decodeEntities,
  pubDateToIso,
  FEEDS,
  REGLERINGSBREV_MYNDIGHETER,
} = require('./rss.js');

const FIXTURE = fs.readFileSync(
  path.join(__dirname, 'fixtures', 'regeringen-lagradsremiss-udep.rss.xml'), 'utf8');
const FIXTURE_UPPDRAG = fs.readFileSync(
  path.join(__dirname, 'fixtures', 'regeringen-uppdrag-udep.rss.xml'), 'utf8');
const FIXTURE_RB = fs.readFileSync(
  path.join(__dirname, 'fixtures', 'statskontoret-regleringsbrev.rss.xml'), 'utf8');

// Routar på feed-URL:en — okänd URL kastar (fångar feldragna konfigändringar).
const fixtureFetcher = async (url) => {
  if (url.includes('preFilteredCategories=2085')) return FIXTURE;
  if (url.includes('preFilteredCategories=1342')) return FIXTURE_UPPDRAG;
  if (url.includes('statskontoret.se')) return FIXTURE_RB;
  throw new Error(`fixtureFetcher: okänd feed-url ${url}`);
};

// T3-testerna kör enbart lagrådsremiss-feeden — identiskt beteende som före T8.
const ENBART_LAGRADSREMISS = [FEEDS[0]];

// ============================================================================
// Parsning av det riktiga flödet
// ============================================================================
test('parseFeed: riktiga fixturen ger 100 poster med titel/datum/url', () => {
  const items = parseFeed(FIXTURE);
  assert.equal(items.length, 100);
  // Nyaste posten = lagrådsremissen om skärpta villkor för friskolesektorn
  // (värdeöverföringsförbudet), publicerad 13 maj 2026.
  assert.equal(items[0].titel, 'Skärpta villkor för friskolesektorn');
  assert.equal(items[0].datum, '2026-05-13');
  assert.match(items[0].url, /^https:\/\/www\.regeringen\.se\/rattsliga-dokument\/lagradsremiss\/2026\/05\//);
  for (const it of items) {
    assert.match(it.datum, /^\d{4}-\d{2}-\d{2}$/);
    assert.match(it.url, /^https:\/\/www\.regeringen\.se\//);
  }
});

// ============================================================================
// Fönsterfiltrering
// ============================================================================
test('buildReport: fönster maj 2026 fångar friskole-lagrådsremissen, fullt täckt', async () => {
  const rapport = await buildReport({ from: '2026-05-01', tom: '2026-05-31', fetcher: fixtureFetcher, feeds: ENBART_LAGRADSREMISS });
  assert.equal(rapport.deltan.length, 1);
  assert.deepEqual(rapport.deltan[0], {
    typ: 'lagradsremiss',
    titel: 'Skärpta villkor för friskolesektorn',
    datum: '2026-05-13',
    url: 'https://www.regeringen.se/rattsliga-dokument/lagradsremiss/2026/05/skarpta-villkor-for-friskolesektorn/',
  });
  assert.equal(rapport.floden[0].fonster_fullt_tackt, true);
  assert.equal(rapport.floden[0].varning, undefined);
});

test('buildReport: tomt fönster inom flödets djup → 0 deltan men fullt täckt', async () => {
  // 1–7 jan 2026: inga lagrådsremisser publicerade, men flödet når till 2012
  // — en äkta tom vecka, ingen varning.
  const rapport = await buildReport({ from: '2026-01-01', tom: '2026-01-07', fetcher: fixtureFetcher, feeds: ENBART_LAGRADSREMISS });
  assert.equal(rapport.deltan.length, 0);
  assert.equal(rapport.floden[0].fonster_fullt_tackt, true);
});

test('buildReport: fönster bakom flödets äldsta post → "ej fullt täckt"-varning', async () => {
  const rapport = await buildReport({ from: '2010-01-01', tom: '2010-12-31', fetcher: fixtureFetcher, feeds: ENBART_LAGRADSREMISS });
  assert.equal(rapport.deltan.length, 0);
  assert.equal(rapport.floden[0].fonster_fullt_tackt, false);
  assert.equal(rapport.floden[0].varning, 'fönster ej fullt täckt av flödet');
  assert.match(rapport.floden[0].aldsta_post_i_flodet, /^\d{4}-\d{2}-\d{2}$/);
});

test('buildReport: fönstergränser är inklusiva', async () => {
  const rapport = await buildReport({ from: '2026-05-13', tom: '2026-05-13', fetcher: fixtureFetcher, feeds: ENBART_LAGRADSREMISS });
  assert.equal(rapport.deltan.length, 1);
  assert.equal(rapport.deltan[0].datum, '2026-05-13');
});

// ============================================================================
// Multi-feed (T8): regeringsuppdrag + per-feed-täckning
// ============================================================================
test('multi-feed: alla flöden körs, deltan typas per feed-konfig', async () => {
  // 20–31 dec 2025: känd händelse — tioårig grundskola-uppdraget 2025-12-22.
  const rapport = await buildReport({ from: '2025-12-20', tom: '2025-12-31', fetcher: fixtureFetcher });
  assert.deepEqual(rapport.floden.map(f => f.namn), ['lagradsremiss', 'regeringsuppdrag', 'regleringsbrev']);
  const uppdrag = rapport.deltan.filter(d => d.typ === 'regeringsuppdrag');
  const tioarig = uppdrag.find(d => /tioårig grundskola/.test(d.titel));
  assert.ok(tioarig, 'tioårig grundskola-uppdraget ska fångas');
  assert.equal(tioarig.titel, 'Uppdrag till Statens skolverk att förbereda införandet av en tioårig grundskola och ta fram förslag på nya läroplaner');
  assert.equal(tioarig.datum, '2025-12-22');
  assert.match(tioarig.url, /^https:\/\/www\.regeringen\.se\/regeringsuppdrag\/2025\/12\//);
});

test('multi-feed: täckningsflaggan sätts per feed, oberoende av varandra', async () => {
  // 2015: lagrådsremiss-flödet når 2012 (täckt) men uppdrag-flödet bara 2019.
  const rapport = await buildReport({ from: '2015-01-01', tom: '2015-12-31', fetcher: fixtureFetcher });
  const lr = rapport.floden.find(f => f.namn === 'lagradsremiss');
  const up = rapport.floden.find(f => f.namn === 'regeringsuppdrag');
  assert.equal(lr.fonster_fullt_tackt, true);
  assert.equal(up.fonster_fullt_tackt, false);
  assert.equal(up.varning, 'fönster ej fullt täckt av flödet');
});

// ============================================================================
// Regleringsbrev via statsliggaren (T9): tvåstegsfilter + beslutsdatum
// ============================================================================
const RB_FEED = [FEEDS.find(f => f.namn === 'regleringsbrev')];

test('transformRegleringsbrev: steg 1 departement, steg 2 myndighet, anslagsbrev släpps', () => {
  const skolverk = {
    titel: 'Ändringsbeslut Myndighet Statens skolverk (beslutsdatum 2026-05-25)',
    datum: '2026-05-26', url: 'https://www.statskontoret.se/statsliggaren/regleringsbrev/?rbid=1',
    extra: { 'media:keywords': 'Statens skolverk,Utbildningsdepartementet,2026' },
  };
  const ut = transformRegleringsbrev(skolverk);
  assert.equal(ut.myndighet, 'Statens skolverk');
  assert.equal(ut.datum, '2026-05-25', 'beslutsdatum ur titeln, inte pubDate');

  // Steg 1: annat departement släpps
  assert.equal(transformRegleringsbrev({
    titel: 'Ändringsbeslut Anslag 1:1 Utrikesdepartementet (beslutsdatum 2026-06-08)',
    datum: '2026-06-09', url: 'https://x/', extra: { 'media:keywords': 'Utrikesdepartementet,2026' },
  }), null);

  // Steg 2: U-dep men lärosäte släpps (högskolegränsen är fast scopegräns)
  assert.equal(transformRegleringsbrev({
    titel: 'Ändringsbeslut Myndighet Uppsala universitet (beslutsdatum 2026-05-11)',
    datum: '2026-05-12', url: 'https://x/', extra: { 'media:keywords': 'Uppsala universitet,Utbildningsdepartementet,2026' },
  }), null);

  // Anslagsbrev utan myndighet (U-dep) släpps
  assert.equal(transformRegleringsbrev({
    titel: 'Ändringsbeslut Anslag 2:63 och 2:65 Utbildningsdepartementet (beslutsdatum 2026-05-12)',
    datum: '2026-05-13', url: 'https://x/', extra: { 'media:keywords': 'Utbildningsdepartementet,2026' },
  }), null);
});

test('regleringsbrev: riktiga fixturen ger exakt Skolverkets två vårändringsbeslut', async () => {
  const rapport = await buildReport({ from: '2026-04-25', tom: '2026-05-31', fetcher: fixtureFetcher, feeds: RB_FEED });
  assert.equal(rapport.deltan.length, 2, 'lärosäten och andra departement bortfiltrerade');
  for (const d of rapport.deltan) {
    assert.equal(d.typ, 'regleringsbrev');
    assert.equal(d.myndighet, 'Statens skolverk');
    assert.match(d.titel, /^Ändringsbeslut/); // ändringsbeslut särskiljs i titeln — ingen egen typ
    assert.match(d.url, /\?rbid=\d+$/);
  }
  assert.deepEqual(rapport.deltan.map(d => d.datum).sort(), ['2026-04-28', '2026-05-25']);
  assert.equal(rapport.floden[0].fonster_fullt_tackt, true);
});

test('regleringsbrev: grunt flöde (~3 månader) flaggar ej fullt täckt bakåt', async () => {
  const rapport = await buildReport({ from: '2026-01-01', tom: '2026-01-31', fetcher: fixtureFetcher, feeds: RB_FEED });
  assert.equal(rapport.deltan.length, 0);
  assert.equal(rapport.floden[0].fonster_fullt_tackt, false);
  assert.equal(rapport.floden[0].aldsta_post_i_flodet, '2026-03-16'); // fixturens faktiska djup
});

test('REGLERINGSBREV_MYNDIGHETER: konfiglistan innehåller skolmyndigheterna', () => {
  assert.deepEqual(REGLERINGSBREV_MYNDIGHETER, [
    'Statens skolverk',
    'Statens skolinspektion',
    'Specialpedagogiska skolmyndigheten',
    'Skolforskningsinstitutet',
    'Skolväsendets överklagandenämnd',
  ]);
});

// ============================================================================
// Per-feed-degradering (DEC-008): ett fallet flöde nollar inte övriga
// ============================================================================
test('per-feed-degradering: fallet flöde ger feed_fel, övriga levererar', async () => {
  const fetcher = async (url) => {
    if (url.includes('statskontoret.se')) throw new Error('Nätverksfel mot https://www.statskontoret.se/...: fetch failed');
    return fixtureFetcher(url);
  };
  const rapport = await buildReport({ from: '2025-12-20', tom: '2025-12-31', fetcher });
  const rb = rapport.floden.find(f => f.namn === 'regleringsbrev');
  assert.match(rb.feed_fel, /fetch failed/);
  // Övriga flöden opåverkade — uppdrags-deltat finns kvar
  assert.ok(rapport.deltan.some(d => d.typ === 'regeringsuppdrag'));
  assert.equal(rapport.floden.length, 3);
});

test('per-feed-degradering: ALLA flöden fallna → throw (aldrig tom rapport)', async () => {
  const fetcher = async () => { throw new Error('Nätverksfel: ECONNRESET'); };
  await assert.rejects(() => buildReport({ from: '2026-06-01', tom: '2026-06-10', fetcher }),
    /Alla 3 RSS-flöden föll/);
});

test('uppdrag-fixturen: 100 poster, alla parsas med titel/datum/url', () => {
  const items = parseFeed(FIXTURE_UPPDRAG);
  assert.equal(items.length, 100);
  for (const it of items) {
    assert.match(it.datum, /^\d{4}-\d{2}-\d{2}$/);
    assert.match(it.url, /^https:\/\/www\.regeringen\.se\//);
  }
});

// ============================================================================
// CDATA och attributvariation (syntetisk — riktiga flödet saknar CDATA idag)
// ============================================================================
test('parseFeed: tål CDATA och attribut på taggarna', () => {
  const xml = `<?xml version="1.0"?><rss version="2.0"><channel>
    <item>
      <title xml:lang="sv"><![CDATA[Skola & framtid <test>]]></title>
      <link>https://www.regeringen.se/x/</link>
      <pubDate>Tue, 02 Jun 2026 09:00:00 +0200</pubDate>
    </item>
  </channel></rss>`;
  const items = parseFeed(xml);
  assert.equal(items.length, 1);
  assert.equal(items[0].titel, 'Skola & framtid <test>');
  assert.equal(items[0].datum, '2026-06-02');
});

test('decodeEntities: avkodar &amp;, numeriska och hex-entiteter', () => {
  assert.equal(decodeEntities('A &amp; B &#229; &#xE5; &quot;q&quot;'), 'A & B å å "q"');
  // &amp;lt; ska bli "&lt;" (en avkodningsnivå), inte "<"
  assert.equal(decodeEntities('&amp;lt;'), '&lt;');
});

test('pubDateToIso: RFC 822-varianter och skräp', () => {
  assert.equal(pubDateToIso('Wed, 13 May 2026 13:27:52 +0200'), '2026-05-13');
  assert.equal(pubDateToIso('3 Mar 2013 00:00:00 +0100'), '2013-03-03'); // utan veckodag, ensiffrig dag
  assert.equal(pubDateToIso('inte ett datum'), null);
  assert.equal(pubDateToIso(null), null);
});

// ============================================================================
// Fail loud
// ============================================================================
test('buildReport: nätverksfel propagerar — aldrig tom rapport', async () => {
  const fetcher = async () => { throw new Error('Nätverksfel mot ...: ECONNRESET'); };
  await assert.rejects(() => buildReport({ from: '2026-06-01', tom: '2026-06-10', fetcher }),
    /Nätverksfel/);
});

test('parseFeed: icke-XML och itemlöst flöde kastar', () => {
  assert.throws(() => parseFeed('<html>503 Service Unavailable</html>'), /inte RSS-XML/);
  assert.throws(() => parseFeed('<rss version="2.0"><channel></channel></rss>'), /inga <item>/);
});

test('parseFeed: item utan pubDate kastar (oparsbart, inte tyst skippat)', () => {
  const xml = `<rss version="2.0"><channel><item>
    <title>T</title><link>https://x/</link>
  </item></channel></rss>`;
  assert.throws(() => parseFeed(xml), /Oparsbart item #1/);
});

test('buildReport: kräver from och tom', async () => {
  await assert.rejects(() => buildReport({ fetcher: fixtureFetcher }), /from och tom krävs/);
});
