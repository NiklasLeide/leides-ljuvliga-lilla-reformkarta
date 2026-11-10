// automat-publicera.test.js — publicering + dev-synk (Sprint 15 T4). Kör: node --test scripts/revision/automat-publicera.test.js
// Allt sker i lokala git-repon i en temp-katalog med en bare-remote som "origin" — inget når GitHub.
'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync, spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const SKRIPT = path.join(__dirname, 'automat-publicera.sh');
const git = (cwd, ...a) => execFileSync('git', a, { cwd, encoding: 'utf8', env: { ...process.env, GIT_AUTHOR_NAME: 't', GIT_AUTHOR_EMAIL: 't@t', GIT_COMMITTER_NAME: 't', GIT_COMMITTER_EMAIL: 't@t' } }).trim();

// origin (bare) med master och dev på samma commit; master har mappen dev/ (preview-kopian).
function miljo({ devFore = false } = {}) {
  const rot = fs.mkdtempSync(path.join(os.tmpdir(), 'publ-'));
  const origin = path.join(rot, 'origin.git'); const arbete = path.join(rot, 'arbete');
  git(rot, 'init', '-q', '--bare', '-b', 'master', origin);
  git(rot, 'clone', '-q', origin, arbete);
  fs.mkdirSync(path.join(arbete, 'data')); fs.mkdirSync(path.join(arbete, 'dev'));
  fs.writeFileSync(path.join(arbete, 'data', 'meta.json'), '{\n  "senast_uppdaterad": "2026-11-01"\n}\n');
  fs.writeFileSync(path.join(arbete, 'dev', 'index.html'), '<p>preview</p>\n');
  fs.writeFileSync(path.join(arbete, 'index.html'), '<p>sajt</p>\n');
  git(arbete, 'add', '.'); git(arbete, 'commit', '-q', '-m', 'start'); git(arbete, 'push', '-q', 'origin', 'master');
  git(arbete, 'push', '-q', 'origin', 'master:dev');
  if (devFore) { // dev har ett eget, opublicerat arbete
    const d = path.join(rot, 'devklon'); git(rot, 'clone', '-q', '-b', 'dev', origin, d);
    fs.writeFileSync(path.join(d, 'index.html'), '<p>sajt ny</p>\n'); git(d, 'commit', '-q', '-am', 'arbete på dev'); git(d, 'push', '-q', 'origin', 'dev');
  }
  const rapport = path.join(rot, 'rapport.json');
  fs.writeFileSync(rapport, JSON.stringify({ commit: 'automat: utr-skolplikt Dir. 2026:117', andringar: [{ post: 'utr-skolplikt', regel: '1b', kalla_url: 'https://data.riksdagen.se/dokument/HEB1117.html' }] }));
  return { rot, origin, arbete, rapport };
}
const kor = (m) => spawnSync('bash', [SKRIPT, m.rapport], { cwd: m.arbete, encoding: 'utf8' });
const ref = (m, r) => git(m.origin, 'rev-parse', r);

test('publicerar data-ändring: commit "automat: …" med käll-URL, push master, dev snabbspolas, dev/ orörd', () => {
  const m = miljo();
  fs.writeFileSync(path.join(m.arbete, 'data', 'meta.json'), '{\n  "senast_uppdaterad": "2026-11-11"\n}\n');
  const r = kor(m);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(ref(m, 'master'), ref(m, 'dev'));
  const msg = git(m.origin, 'log', '-1', '--format=%B', 'master');
  assert.match(msg, /^automat: utr-skolplikt Dir\. 2026:117/);
  assert.match(msg, /https:\/\/data\.riksdagen\.se\/dokument\/HEB1117\.html/);
  assert.deepEqual(git(m.origin, 'show', '--name-only', '--format=', 'master').split('\n'), ['data/meta.json']);
  assert.equal(git(m.origin, 'show', 'master:dev/index.html'), '<p>preview</p>');
});

test('dev har egna commits → master mergas in i dev (ingen force), dev:s arbete kvar', () => {
  const m = miljo({ devFore: true });
  const devFore = ref(m, 'dev');
  fs.writeFileSync(path.join(m.arbete, 'data', 'meta.json'), '{\n  "senast_uppdaterad": "2026-11-11"\n}\n');
  const r = kor(m);
  assert.equal(r.status, 0, r.stderr);
  git(m.origin, 'merge-base', '--is-ancestor', devFore, 'dev');        // dev:s gamla topp finns kvar
  git(m.origin, 'merge-base', '--is-ancestor', ref(m, 'master'), 'dev'); // master ingår i dev
  assert.equal(git(m.origin, 'show', 'dev:index.html'), '<p>sajt ny</p>');
  assert.match(git(m.origin, 'show', 'dev:data/meta.json'), /2026-11-11/);
});

test('ändring utanför data/ → STOPP (exit 4), ingenting pushas', () => {
  const m = miljo(); const fore = ref(m, 'master');
  fs.writeFileSync(path.join(m.arbete, 'data', 'meta.json'), '{}\n');
  fs.writeFileSync(path.join(m.arbete, 'dev', 'index.html'), '<p>ändrad</p>\n');
  const r = kor(m);
  assert.equal(r.status, 4); assert.match(r.stderr, /utanför data\//);
  assert.equal(ref(m, 'master'), fore);
});

test('inga ändringar → inget publiceras (exit 0)', () => {
  const m = miljo(); const fore = ref(m, 'master');
  const r = kor(m);
  assert.equal(r.status, 0); assert.match(r.stdout, /inget att publicera/);
  assert.equal(ref(m, 'master'), fore);
});

test('master har flyttat sig under körningen → push avvisas, STOPP (exit 4), dev orörd', () => {
  const m = miljo(); const devFore = ref(m, 'dev');
  const annan = path.join(m.rot, 'annan'); git(m.rot, 'clone', '-q', m.origin, annan);
  fs.writeFileSync(path.join(annan, 'index.html'), '<p>annan</p>\n'); git(annan, 'commit', '-q', '-am', 'annan push'); git(annan, 'push', '-q', 'origin', 'master');
  fs.writeFileSync(path.join(m.arbete, 'data', 'meta.json'), '{}\n');
  const r = kor(m);
  assert.equal(r.status, 4); assert.match(r.stderr, /push till master misslyckades/);
  assert.equal(ref(m, 'dev'), devFore);
});

test('otrackade filer (t.ex. node_modules) stoppar inte publiceringen', () => {
  const m = miljo();
  fs.mkdirSync(path.join(m.arbete, 'node_modules')); fs.writeFileSync(path.join(m.arbete, 'node_modules', 'x.js'), '');
  fs.writeFileSync(path.join(m.arbete, 'data', 'meta.json'), '{\n  "senast_uppdaterad": "2026-11-11"\n}\n');
  assert.equal(kor(m).status, 0);
});

test('synka-dev.sh: konflikt mellan dev och master → exit 4, dev orörd (ingen force)', () => {
  const m = miljo();
  const d = path.join(m.rot, 'devklon'); git(m.rot, 'clone', '-q', '-b', 'dev', m.origin, d);
  fs.writeFileSync(path.join(d, 'data', 'meta.json'), '{\n  "senast_uppdaterad": "dev-version"\n}\n');
  git(d, 'commit', '-q', '-am', 'dev ändrar samma rad'); git(d, 'push', '-q', 'origin', 'dev');
  const devFore = ref(m, 'dev');
  fs.writeFileSync(path.join(m.arbete, 'data', 'meta.json'), '{\n  "senast_uppdaterad": "2026-11-11"\n}\n');
  git(m.arbete, 'commit', '-q', '-am', 'master ändrar'); git(m.arbete, 'push', '-q', 'origin', 'master');
  const r = spawnSync('bash', [path.join(__dirname, 'synka-dev.sh'), git(m.arbete, 'rev-parse', 'HEAD')], { cwd: m.arbete, encoding: 'utf8' });
  assert.equal(r.status, 4); assert.match(r.stderr, /konflikt/);
  assert.equal(ref(m, 'dev'), devFore);
});
