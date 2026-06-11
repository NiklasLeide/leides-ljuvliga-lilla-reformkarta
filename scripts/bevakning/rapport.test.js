// rapport.test.js — enhetstest för veckorapport-byggaren (Sprint 10 T4).
// Inga ramverk: node:test + node:assert. Kör: node --test scripts/bevakning/rapport.test.js
//
// Indatafixtures är RIKTIGA rapporter från skarpa körningar 2026-06-11:
//   rapport-riksdagen-delta.json — fönster 2026-04-25→2026-06-10: 9 prop-status,
//     1 nytt-direktiv, 1 ny-proposition, 5 ny-sou, 1 tilläggsdir (17 deltan)
//   rapport-rss-delta.json — fönster 2026-05-01→2026-06-01, multi-feed (T8+T9):
//     friskole-lagrådsremissen + 2 regeringsuppdrag + 1 regleringsbrev (4 deltan)

'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { buildRapport, isoWeek } = require('./rapport.js');

const FIXTURE_DIR = path.join(__dirname, 'fixtures');
function loadFixture(name) {
  return JSON.parse(fs.readFileSync(path.join(FIXTURE_DIR, name), 'utf8'));
}
const RIKSDAGEN = loadFixture('rapport-riksdagen-delta.json'); // 17 deltan, alla riksdagen-typer
const RSS = loadFixture('rapport-rss-delta.json');             // 4 deltan: 1 lagrådsremiss + 2 uppdrag + 1 regleringsbrev

const NU = new Date('2026-06-11T07:00:00Z');

test('full rapport: alla sektioner, kryssrutor, källänkar och footer', () => {
  const r = buildRapport({ riksdagen: RIKSDAGEN, rss: RSS, nu: NU });

  assert.equal(r.harDeltan, true);
  assert.equal(r.antalDeltan, 21); // 17 riksdagen + 4 rss
  assert.equal(r.titel, 'Bevakningsrapport v.24 2026');

  // En tom triage-kryssruta per delta — varken fler eller färre.
  const kryssrutor = (r.body.match(/^- \[ \] /gm) || []).length;
  assert.equal(kryssrutor, 21);

  // Sektionsrubriker med antal
  assert.match(r.body, /## A\. Propositionsstatus — betänkandebeslut att triagera \(9\)/);
  assert.match(r.body, /## B\. Nya direktiv \(Utbildningsdep\.\) \(1\)/);
  assert.match(r.body, /## B2\. Nya propositioner \(Utbildningsdep\.\) \(1\)/);
  assert.match(r.body, /## B3\. Nya SOU \(alla departement — SOU saknar departementsdata\) \(5\)/);
  assert.match(r.body, /## C\. Tilläggsdirektiv till spårade utredningar \(1\)/);
  assert.match(r.body, /## Lagrådsremisser \(Utbildningsdep\.\) \(1\)/);
  assert.match(r.body, /## Regeringsuppdrag \(Utbildningsdep\.\) \(2\)/);
  assert.match(r.body, /## Regleringsbrev & ändringsbeslut \(skolmyndigheterna\) \(1\)/);

  // Regeringsuppdrag med primärkällänk (T8)
  assert.match(r.body, /\*\*Uppdrag till Statens skolverk om stöd i tillämpningen[^*]*\*\* \(2026-05-21\) — \[uppdrag\]\(https:\/\/www\.regeringen\.se\/regeringsuppdrag\//);

  // Faktapar prop-status: datafilens läge + betänkandebeslut + rskr + länk
  assert.match(r.body, /\*\*Prop\. 2025\/26:174\*\* — datafilen säger: `proposition`/);
  assert.match(r.body, /Betänkande 2025\/26:UbU29: Ärendet är avslutat — beslut 2026-05-27, rskr 2025\/26:300/);
  assert.match(r.body, /\[Dokumentstatus\]\(http/);

  // Lagrådsremissen med primärkällänk
  assert.match(r.body, /\*\*Skärpta villkor för friskolesektorn\*\* \(2026-05-13\) — \[lagrådsremiss\]\(https:\/\/www\.regeringen\.se\//);

  // Footer: antal_kontrollerade per kategori + körningsdatum
  assert.match(r.body, /\*\*Kontrollerat:\*\* 12 props i manifestet \(3 terminala skippade\) · 31 props i fönstret · 16 direktiv i fönstret · 5 SOU i fönstret · 27 spårade utredningar · RSS: lagradsremiss 100 poster, regeringsuppdrag 100 poster, regleringsbrev 86 poster/);
  assert.match(r.body, /\*\*Körningar:\*\* riksdagen 2026-06-11T.*· RSS /);
  assert.match(r.body, /\*\*Fönster:\*\* 2026-04-25 → 2026-06-10/);
});

test('tom delta-mängd: harDeltan=false, body markerar tom körning', () => {
  const riksdagen = { ...RIKSDAGEN, deltan: [] };
  const rss = { ...RSS, deltan: [] };
  const r = buildRapport({ riksdagen, rss, nu: NU });
  assert.equal(r.harDeltan, false);
  assert.equal(r.antalDeltan, 0);
  assert.match(r.body, /_Inga deltan i fönstret\._/);
  assert.equal((r.body.match(/^- \[ \] /gm) || []).length, 0);
  assert.doesNotMatch(r.body, /^## /m); // inga tomma sektioner
});

test('ej-funnen prop renderas som anomali, inte tyst tappad', () => {
  const riksdagen = {
    ...RIKSDAGEN,
    deltan: [{
      typ: 'prop-status', beteckning: 'Prop. 2099/00:1',
      api_sager: { found: false },
      datafilen_sager: { status: 'proposition', kalla_fil: 'reforms.json' },
      kalla_fil: 'reforms.json',
      url: 'https://data.riksdagen.se/dokumentlista/?x',
    }],
  };
  const r = buildRapport({ riksdagen, rss: { ...RSS, deltan: [] }, nu: NU });
  assert.match(r.body, /\*\*Prop\. 2099\/00:1\*\* — hittades INTE i riksdagens API \(anomali\)/);
});

test('okänd delta-typ hamnar i Övrigt med rå JSON — aldrig tyst tappad', () => {
  const riksdagen = {
    ...RIKSDAGEN,
    deltan: [{ typ: 'framtida-typ', nagonting: 'x' }],
  };
  const r = buildRapport({ riksdagen, rss: { ...RSS, deltan: [] }, nu: NU });
  assert.equal(r.antalDeltan, 1);
  assert.match(r.body, /## Övrigt — okänd delta-typ \(1\)/);
  assert.match(r.body, /"typ":"framtida-typ"/);
  assert.equal((r.body.match(/^- \[ \] /gm) || []).length, 1); // kryssruta även för okänd
});

test('B3-typerna renderas med egna sektioner (T7)', () => {
  const riksdagen = {
    ...RIKSDAGEN,
    deltan: [
      { typ: 'sou-levererad', beteckning: 'SOU 2025:9', titel: 'På språklig grund', datum: '2025-01-31', utredning: 'utr-grundlaggande-svenska', url: 'https://data.riksdagen.se/dokument/HDB39.html' },
      { typ: 'ny-sou', beteckning: 'SOU 2025:12', titel: 'AI-kommissionens Färdplan för Sverige', datum: '2025-02-03', betankande_av: 'AI-kommissionen', url: 'https://data.riksdagen.se/dokument/HDB312.html' },
      { typ: 'ny-sou', beteckning: 'SOU 2025:11', titel: 'Straffbarhetsåldern', datum: '2025-02-03', betankande_av: null, url: 'https://data.riksdagen.se/dokument/HDB311.html' },
    ],
  };
  const r = buildRapport({ riksdagen, rss: { ...RSS, deltan: [] }, nu: NU });
  assert.equal(r.antalDeltan, 3);
  assert.match(r.body, /## B3\. Betänkanden från spårade utredningar \(1\)/);
  assert.match(r.body, /\*\*SOU 2025:9\*\* På språklig grund \(2025-01-31\) — spårad utredning \*\*utr-grundlaggande-svenska\*\* har publicerat — \[källa\]/);
  assert.match(r.body, /## B3\. Nya SOU \(alla departement — SOU saknar departementsdata\) \(2\)/);
  assert.match(r.body, /\*\*SOU 2025:12\*\*.*— betänkande av AI-kommissionen — \[källa\]/);
  assert.doesNotMatch(r.body, /\*\*SOU 2025:11\*\*.*betänkande av/); // null-ledtråd renderas inte
  assert.doesNotMatch(r.body, /## Övrigt/); // typerna är kända, hamnar inte i Övrigt
  assert.equal((r.body.match(/^- \[ \] /gm) || []).length, 3);
});

test('regleringsbrev-typen renderas med myndighet och statsliggarlänk (T9)', () => {
  const rss = {
    ...RSS,
    deltan: [
      { typ: 'regleringsbrev', titel: 'Ändringsbeslut Myndighet Statens skolverk (beslutsdatum 2026-05-25)', myndighet: 'Statens skolverk', datum: '2026-05-25', url: 'https://www.statskontoret.se/statsliggaren/regleringsbrev/?rbid=26371' },
    ],
  };
  const r = buildRapport({ riksdagen: { ...RIKSDAGEN, deltan: [] }, rss, nu: NU });
  assert.match(r.body, /## Regleringsbrev & ändringsbeslut \(skolmyndigheterna\) \(1\)/);
  assert.match(r.body, /\*\*Statens skolverk\*\* — Ändringsbeslut Myndighet Statens skolverk \(beslutsdatum 2026-05-25\) — \[statsliggaren\]\(https:\/\/www\.statskontoret\.se\/statsliggaren\/regleringsbrev\/\?rbid=26371\)/);
  assert.doesNotMatch(r.body, /## Övrigt/);
});

test('feed_fel renderas som 🔴-varning och FEL i footern (DEC-008)', () => {
  const rss = {
    ...RSS,
    deltan: [],
    floden: [
      { namn: 'lagradsremiss', antal_i_flodet: 100, aldsta_post_i_flodet: '2012-12-11', fonster_fullt_tackt: true },
      { namn: 'regleringsbrev', kalla: 'https://www.statskontoret.se/...', feed_fel: 'Nätverksfel mot ...: fetch failed' },
    ],
  };
  const r = buildRapport({ riksdagen: { ...RIKSDAGEN, deltan: [] }, rss, nu: NU });
  assert.match(r.body, /🔴 RSS-flödet \*\*regleringsbrev\*\* kunde INTE hämtas \(Nätverksfel mot \.\.\.: fetch failed\)/);
  assert.match(r.body, /RSS: lagradsremiss 100 poster, regleringsbrev FEL/);
});

test('rss-varning "ej fullt täckt" tas med per flöde (multi-feed)', () => {
  const rss = {
    ...RSS,
    deltan: [],
    floden: [
      { namn: 'lagradsremiss', antal_i_flodet: 100, aldsta_post_i_flodet: '2012-12-11', fonster_fullt_tackt: true },
      { namn: 'regeringsuppdrag', antal_i_flodet: 100, aldsta_post_i_flodet: '2019-05-23', fonster_fullt_tackt: false, varning: 'fönster ej fullt täckt av flödet' },
    ],
  };
  const r = buildRapport({ riksdagen: { ...RIKSDAGEN, deltan: [] }, rss, nu: NU });
  assert.match(r.body, /⚠️ RSS-flödet regeringsuppdrag är inte fullt täckt av fönstret \(äldsta post: 2019-05-23\)/);
  assert.doesNotMatch(r.body, /⚠️ RSS-flödet lagradsremiss/); // täckt flöde varnar inte
});

test('isoWeek: ISO 8601-vecka och veckoår, inkl. årsskifteskantfall', () => {
  // Facit från GNU date (%V/%G)
  assert.deepEqual(isoWeek(new Date('2026-06-11T00:00:00Z')), { week: 24, year: 2026 });
  assert.deepEqual(isoWeek(new Date('2026-01-01T00:00:00Z')), { week: 1, year: 2026 });
  assert.deepEqual(isoWeek(new Date('2027-01-01T00:00:00Z')), { week: 53, year: 2026 }); // veckoår ≠ kalenderår
});

test('trasig indata kastar — aldrig tom rapport', () => {
  assert.throws(() => buildRapport({ riksdagen: {}, rss: RSS }), /saknar deltan/);
  assert.throws(() => buildRapport({ riksdagen: RIKSDAGEN, rss: null }), /saknar deltan/);
});
