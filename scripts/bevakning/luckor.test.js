// luckor.test.js — bevakningens luckor 2026 (Sprint 15 T5). Kör: node --test scripts/bevakning/luckor.test.js
// Krav: Dir. 2026:105, 2026:117, 2026:123, U2026/01573, U2026/01569 och U2026/01547 fångas.
// Fixturer (fixtures/luckor/, hämtade 2026-11-10):
//   dir-rm2026.json   — riksdagens direktivlista för 2026 (riktigt svar, fälten bevakningen läser, inkl. systemdatum)
//   regeringen-kommittedirektiv-alla.rss.xml — regeringen.se, kommittédirektiv alla departement (riktigt flöde)
//   data-37c2616/     — datafilerna som de såg ut före Sprint 14 (då ingen av de sex var spårad)
// Sökningar per kommittébeteckning (jobb C2) besvaras genom att filtrera den riktiga direktivlistan på
// beteckningen i titel eller undertitel — samma urval som riksdagens fritextsökning ger för dessa fall.
'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const R = require('./riksdagen.js');
const RSS = require('./rss.js');
const { arSkolamne } = require('./amne.js');

const FX = path.join(__dirname, 'fixtures', 'luckor');
const DIR = JSON.parse(fs.readFileSync(path.join(FX, 'dir-rm2026.json'), 'utf8'));
const FEED = fs.readFileSync(path.join(FX, 'regeringen-kommittedirektiv-alla.rss.xml'), 'utf8');
const DATA = path.join(FX, 'data-37c2616');

async function fetcher(url) {
  const u = decodeURIComponent(url).replace(/\+/g, ' ');
  if (u.includes('doktyp=dir') && u.includes('sok=')) {
    const bet = /sok="([^"]+)"/.exec(u)[1];
    return { dokumentlista: { dokument: DIR.dokumentlista.dokument.filter(d => (d.titel || '').includes(bet) || (d.undertitel || '').includes(bet)) } };
  }
  if (u.includes('doktyp=dir') && u.includes('rm=2026')) return DIR;
  if (u.includes('doktyp=dir')) return { dokumentlista: { dokument: [] } }; // andra år: tomt i fixturen
  if (u.includes('doktyp=prop') || u.includes('doktyp=sou')) return { dokumentlista: { dokument: [] } };
  throw new Error('oväntad url ' + url);
}

test('riksdagen: Dir. 2026:105 (Ju-dep), 2026:117 och 2026:123 fångas över hösten 2026', async () => {
  const rap = await R.buildReport({ from: '2026-08-31', tom: '2026-11-09', dataDir: DATA, fetcher, delayMs: 0 });
  const b4 = rap.deltan.filter(d => d.typ === 'direktiv-annat-departement').map(d => d.beteckning);
  const c = rap.deltan.filter(d => d.typ === 'tillaggsdir-till-tracked-utredning').map(d => d.direktiv_beteckning);
  assert.ok(b4.includes('Dir. 2026:105'), `B4: ${b4}`);
  assert.ok(c.includes('Dir. 2026:117'), `C/C2: ${c}`);
  assert.ok(c.includes('Dir. 2026:123'), `C/C2: ${c}`);
  // inga dubbletter mellan C och C2
  assert.equal(new Set(c).size, c.length);
});

test('rotorsaken: sent inlagda direktiv hamnar i fönstret när de dök upp (systemdatum)', async () => {
  // Dir. 2026:117: datum 2026-09-03, systemdatum 2026-09-09 → v.38-fönstret (gamla koden: ingen vecka).
  const v38 = await R.fetchDirektivSystemdatum({ from: '2026-09-07', tom: '2026-09-14', fetcher, delayMs: 0 });
  assert.ok(v38.some(d => d.beteckning === '117'));
  // Dir. 2026:123: datum 2026-10-22, systemdatum 2026-11-03 → v.46-fönstret.
  const v46 = await R.fetchDirektivSystemdatum({ from: '2026-11-02', tom: '2026-11-09', fetcher, delayMs: 0 });
  assert.ok(v46.some(d => d.beteckning === '123'));
  // C2 är fönsteroberoende: 117 och 123 rapporteras även i ett fönster där inget av dem ligger.
  const rap = await R.buildReport({ from: '2026-06-01', tom: '2026-06-07', dataDir: DATA, fetcher, delayMs: 0 });
  const c = rap.deltan.filter(d => d.typ === 'tillaggsdir-till-tracked-utredning').map(d => d.direktiv_beteckning);
  assert.ok(c.includes('Dir. 2026:117') && c.includes('Dir. 2026:123'), `C2: ${c}`);
});

test('omindexering i bulk spolar inte in gamla direktiv (systemdatum räknas bara för direktiv ≤ 60 dagar)', async () => {
  const gammal = { dok_id: 'X', rm: '2026', beteckning: '1', datum: '2026-01-08', systemdatum: '2026-11-03 05:00:00', organ: 'U-dep', titel: 't' };
  const f = async () => ({ dokumentlista: { dokument: [gammal] } });
  assert.equal((await R.fetchDirektivSystemdatum({ from: '2026-11-02', tom: '2026-11-09', fetcher: f, delayMs: 0 })).length, 0);
});

test('regeringen.se: departementsuppdragen U2026/01573, U2026/01569 och U2026/01547 fångas', () => {
  const items = RSS.parseFeed(FEED, { extraTaggar: ['category*'] });
  const dep = items.map(RSS.transformDepartementsuppdrag).filter(Boolean)
    .filter(d => d.datum >= '2026-08-31' && d.datum <= '2026-09-14');
  const dnr = dep.map(d => d.dnr);
  for (const n of ['U2026/01573', 'U2026/01569', 'U2026/01547']) assert.ok(dnr.includes(n), `${n} saknas: ${dnr}`);
  // numrerade direktiv (adress med "dir…") släpps — riksdagens data täcker dem
  assert.equal(dep.some(d => /\/dir/.test(d.url)), false);
  const u1573 = dep.find(d => d.dnr === 'U2026/01573');
  assert.equal(u1573.titel, 'Uppdrag att föreslå obligatorisk förskola med språkutvecklande insatser');
  assert.equal(u1573.departement, 'Utbildningsdepartementet');
});

test('ämnesregeln (DEC-020): skolämne från alla departement in, yrkeshögskola/studiemedel ut', () => {
  assert.equal(arSkolamne({ titel: 'Åtgärder för att förebygga och förhindra allvarliga våldsdåd i skolmiljöer' }), true);
  assert.equal(arSkolamne({ titel: 'Uppdrag att utreda nationell yrkesutbildning', kategorier: ['Barn- och ungdomsutbildning'] }), true);
  assert.equal(arSkolamne({ titel: 'Bättre insyn och kontroll i yrkeshögskolan', kategorier: ['Utbildning för vuxna'] }), false);
  assert.equal(arSkolamne({ titel: 'Skydda barn och unga vuxna från spel om pengar' }), false);
  assert.equal(arSkolamne({ titel: 'Ändrade regler för studiemedel', kategorier: ['Studiefinansiering'] }), false);
});
