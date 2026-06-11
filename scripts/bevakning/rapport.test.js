// rapport.test.js — enhetstest för veckorapport-byggaren (Sprint 10 T4).
// Inga ramverk: node:test + node:assert. Kör: node --test scripts/bevakning/rapport.test.js
//
// Indatafixtures är RIKTIGA rapporter från skarpa körningar 2026-06-10/11:
//   rapport-riksdagen-delta.json — fönster 2026-04-25→2026-06-10, alla 4 typer
//   rapport-rss-delta.json      — fönster 2026-05-01→2026-06-01, friskole-remissen

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
const RIKSDAGEN = loadFixture('rapport-riksdagen-delta.json'); // 12 deltan: 9 prop-status, 1 dir, 1 tilläggsdir, 1 ny prop
const RSS = loadFixture('rapport-rss-delta.json');             // 1 delta: friskole-lagrådsremissen

const NU = new Date('2026-06-11T07:00:00Z');

test('full rapport: alla sektioner, kryssrutor, källänkar och footer', () => {
  const r = buildRapport({ riksdagen: RIKSDAGEN, rss: RSS, nu: NU });

  assert.equal(r.harDeltan, true);
  assert.equal(r.antalDeltan, 13); // 12 riksdagen + 1 rss
  assert.equal(r.titel, 'Bevakningsrapport v.24 2026');

  // En tom triage-kryssruta per delta — varken fler eller färre.
  const kryssrutor = (r.body.match(/^- \[ \] /gm) || []).length;
  assert.equal(kryssrutor, 13);

  // Sektionsrubriker med antal
  assert.match(r.body, /## A\. Propositionsstatus — betänkandebeslut att triagera \(9\)/);
  assert.match(r.body, /## B\. Nya direktiv \(Utbildningsdep\.\) \(1\)/);
  assert.match(r.body, /## B2\. Nya propositioner \(Utbildningsdep\.\) \(1\)/);
  assert.match(r.body, /## C\. Tilläggsdirektiv till spårade utredningar \(1\)/);
  assert.match(r.body, /## Lagrådsremisser \(Utbildningsdep\.\) \(1\)/);

  // Faktapar prop-status: datafilens läge + betänkandebeslut + rskr + länk
  assert.match(r.body, /\*\*Prop\. 2025\/26:174\*\* — datafilen säger: `proposition`/);
  assert.match(r.body, /Betänkande 2025\/26:UbU29: Ärendet är avslutat — beslut 2026-05-27, rskr 2025\/26:300/);
  assert.match(r.body, /\[Dokumentstatus\]\(http/);

  // Lagrådsremissen med primärkällänk
  assert.match(r.body, /\*\*Skärpta villkor för friskolesektorn\*\* \(2026-05-13\) — \[lagrådsremiss\]\(https:\/\/www\.regeringen\.se\//);

  // Footer: antal_kontrollerade per kategori + körningsdatum
  assert.match(r.body, /\*\*Kontrollerat:\*\* 12 props i manifestet \(3 terminala skippade\) · 31 props i fönstret · 16 direktiv i fönstret · 27 spårade utredningar · 100 poster i RSS-flödet/);
  assert.match(r.body, /\*\*Körningar:\*\* riksdagen 2026-06-10T.*· RSS /);
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

test('rss-varning "ej fullt täckt" tas med i rapporten', () => {
  const rss = { ...RSS, deltan: [], fonster_fullt_tackt: false, aldsta_post_i_flodet: '2012-12-11' };
  const r = buildRapport({ riksdagen: { ...RIKSDAGEN, deltan: [] }, rss, nu: NU });
  assert.match(r.body, /⚠️ RSS-fönstret är inte fullt täckt av flödet \(äldsta post: 2012-12-11\)/);
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
