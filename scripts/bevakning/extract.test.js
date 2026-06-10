// extract.test.js — enhetstest för identifierar-extraktionen (Sprint 10 T1).
// Inga ramverk: node:test + node:assert. Kör: node --test scripts/bevakning/
'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('path');
const { extractManifest } = require('./extract.js');

const EXTRACT_CLI = path.join(__dirname, 'extract.js');

test('manifest innehåller kända identifierare (facit)', () => {
  const m = extractManifest();
  const ids = cat => m[cat].map(e => e.id);

  // Facit enligt sprintspec — finns i dagens dataset
  assert.ok(ids('props').includes('Prop. 2025/26:198'), 'Prop. 2025/26:198 saknas');
  assert.ok(ids('sou').includes('SOU 2024:74'), 'SOU 2024:74 saknas');
  assert.ok(ids('dir').includes('Dir. 2025:103'), 'Dir. 2025:103 saknas');
  assert.ok(ids('utredningar').includes('U 2022:03'), 'U 2022:03 saknas');

  // Logga antal per kategori (krav i sprintspec)
  const counts = Object.fromEntries(Object.entries(m).map(([k, v]) => [k, v.length]));
  console.log('Antal poster per kategori:', JSON.stringify(counts));

  // Rimlighetsgränser — inte hårdkodade exakta antal (datasetet växer),
  // men tomma kategorier vore en regression
  for (const [cat, n] of Object.entries(counts)) {
    assert.ok(n > 0, `kategori ${cat} är tom`);
  }
});

test('utredningsbeteckningar = alla icke-aviserade poster i utredningar.json', () => {
  const m = extractManifest();
  const data = require('../../data/utredningar.json');
  const expected = data.filter(u => u.beteckning).map(u => u.beteckning).sort();
  const actual = m.utredningar.map(e => e.id).sort();
  assert.deepEqual(actual, expected);
});

test('deduplicering: samma beteckning från flera källor blir EN post med flera referenser', () => {
  const m = extractManifest();
  // Dir. 2024:30 finns både i direktiv-arrayen och i kallor för utr-elevhalsa
  const d = m.dir.find(e => e.id === 'Dir. 2024:30');
  assert.ok(d, 'Dir. 2024:30 saknas');
  assert.ok(d.referenser.length >= 2, `förväntade >=2 referenser, fick ${d.referenser.length}`);
  // Inga dubblett-id:n inom någon kategori
  for (const [cat, entries] of Object.entries(m)) {
    const ids = entries.map(e => e.id);
    assert.equal(ids.length, new Set(ids).size, `dubbletter i ${cat}`);
  }
});

test('referenser har obligatoriska fält', () => {
  const m = extractManifest();
  for (const entries of Object.values(m)) {
    for (const e of entries) {
      assert.ok(e.referenser.length > 0, `${e.id}: inga referenser`);
      for (const r of e.referenser) {
        assert.ok(r.kalla_fil, `${e.id}: kalla_fil saknas`);
        assert.ok(r.kalla_post, `${e.id}: kalla_post saknas`);
        assert.ok('registrerad_status' in r, `${e.id}: registrerad_status saknas`);
        assert.ok('registrerat_datum' in r, `${e.id}: registrerat_datum saknas`);
      }
    }
  }
});

test('diarienummer ger inte falska utredningsbeteckningar', () => {
  const m = extractManifest();
  // "Regeringsuppdrag (U2025/02427)" i uppdrag.json får inte tolkas som beteckning
  const false_hits = m.utredningar.filter(e => e.id.includes('/'));
  assert.equal(false_hits.length, 0, `falska träffar: ${false_hits.map(e => e.id)}`);
});

test('saknad datakatalog ger tydligt fel (funktion)', () => {
  assert.throws(() => extractManifest('/tmp/finns-inte-bevakning-test'), /Kunde inte läsa datafil/);
});

test('saknad datakatalog ger exit code != 0 (CLI)', () => {
  const res = spawnSync(process.execPath, [EXTRACT_CLI, '/tmp/finns-inte-bevakning-test'], { encoding: 'utf8' });
  assert.notEqual(res.status, 0, 'CLI borde ha misslyckats');
  assert.match(res.stderr, /FEL:/);
});

test('CLI skriver giltig JSON till stdout', () => {
  const res = spawnSync(process.execPath, [EXTRACT_CLI], { encoding: 'utf8' });
  assert.equal(res.status, 0, `CLI misslyckades: ${res.stderr}`);
  const parsed = JSON.parse(res.stdout);
  assert.deepEqual(Object.keys(parsed), ['props', 'sou', 'dir', 'utredningar']);
});
