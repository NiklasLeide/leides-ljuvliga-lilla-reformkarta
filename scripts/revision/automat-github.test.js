// automat-github.test.js — regel 7 (automat-stopp-issue) och regel 9 (Automatlogg) med fejkad fetch.
// Kör: node --test scripts/revision/automat-github.test.js
'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const G = require('./automat-github.js');

function fejk(svar = {}) {
  const anrop = [];
  const fetchImpl = async (url, opt) => {
    const sokvag = url.replace('https://api.github.com/repos/o/r', '');
    anrop.push({ metod: opt.method, sokvag, body: opt.body ? JSON.parse(opt.body) : null, auth: opt.headers.Authorization });
    const s = svar[`${opt.method} ${sokvag.split('?')[0]}`];
    const v = typeof s === 'function' ? s() : s;
    return { ok: !(v && v.status >= 400), status: (v && v.status) || 200, json: async () => (v && v.body !== undefined ? v.body : v) };
  };
  return { api: G.klient({ token: 'T', repo: 'o/r', fetchImpl }), anrop };
}
const RAPPORT = { datum: '2026-11-11', stopp: 'regel 5: 6 ändringar > 5',
  andringar: [{ regel: '1b', post: 'utr-skolplikt', falt: 'direktiv (ny rad)', nytt: { nr: 'Dir. 2026:117' }, kalla_url: 'https://data.riksdagen.se/dokument/HEB1117.html' }],
  veckorutin: [{ post: 'utr-vinst', regel: '1c', skal: 'rad utan nummer', url: 'u' }], fel: [] };

test('regel 7: stopp skapar etiketten automat-stopp och en issue med orsak, ej publicerade ändringar och körnings-URL', async () => {
  const { api, anrop } = fejk({ 'POST /labels': { status: 422 }, 'POST /issues': { number: 41 } });
  const ut = await G.stopp({ api, rapport: RAPPORT, runUrl: 'https://github.com/o/r/actions/runs/1' });
  assert.equal(ut.number, 41);
  assert.equal(anrop[0].sokvag, '/labels'); assert.equal(anrop[0].body.name, 'automat-stopp');
  const issue = anrop[1].body;
  assert.equal(issue.title, 'Automat-stopp 2026-11-11');
  assert.deepEqual(issue.labels, ['automat-stopp']);
  assert.match(issue.body, /Ingenting publicerades/);
  assert.match(issue.body, /regel 5: 6 ändringar > 5/);
  assert.match(issue.body, /Dir\. 2026:117/);
  assert.match(issue.body, /actions\/runs\/1/);
  assert.equal(anrop[1].auth, 'Bearer T');
});

test('regel 9: logg kommenterar i befintlig Automatlogg-issue', async () => {
  const { api, anrop } = fejk({ 'GET /issues': [{ number: 7, title: 'Automatlogg' }], 'POST /issues/7/comments': { id: 1 } });
  assert.equal(await G.logg({ api, rapport: { ...RAPPORT, stopp: null }, sha: 'abcdef1234', runUrl: 'run' }), 7);
  const k = anrop.find(a => a.sokvag === '/issues/7/comments').body.body;
  assert.match(k, /^\*\*2026-11-11\*\* — publicerat i abcdef1/);
  assert.match(k, /\| 1b \| utr-skolplikt \| direktiv \(ny rad\) \| Dir\. 2026:117 \| https:\/\/data\.riksdagen\.se\/dokument\/HEB1117\.html \|/);
});

test('regel 9: saknas Automatlogg skapas den (med etikett) och får kommentaren', async () => {
  const { api, anrop } = fejk({ 'GET /issues': [], 'POST /labels': { status: 422 }, 'POST /issues': { number: 9 }, 'POST /issues/9/comments': { id: 1 } });
  assert.equal(await G.logg({ api, rapport: RAPPORT, sha: 'abc', runUrl: 'run' }), 9);
  const skapad = anrop.find(a => a.metod === 'POST' && a.sokvag === '/issues').body;
  assert.equal(skapad.title, 'Automatlogg'); assert.deepEqual(skapad.labels, ['automatlogg']);
});

test('HTTP-fel från GitHub kastas (arbetsflödets steg blir rött)', async () => {
  const { api } = fejk({ 'POST /labels': { status: 201, body: {} }, 'POST /issues': { status: 403 } });
  await assert.rejects(G.stopp({ api, rapport: RAPPORT, runUrl: 'r' }), /HTTP 403/);
});

// Beslut 2026-11-10 (tolkning 1): 1a-ändring → uppföljningsissue med etiketten bevakning.
const RAP_1A = { datum: '2026-11-12', andringar: [
  { regel: '1a', post: 'vinst', reform_namn: 'Vinst i skolan', transition_tillagg: 'Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30, rskr. 2025/26:438).',
    betankanden: [{ bet: '2025/26:UbU30', rskr: '2025/26:438', beslutsdatum: '2026-08-13', url: 'https://data.riksdagen.se/dokument/HD01UbU30.html' }] },
  { regel: '1b', post: 'utr-x', nytt: { nr: 'Dir. 2026:200' } },
] };

test('uppföljning: 1a skapar issue "Uppföljning efter riksdagsbeslut: {reform}" med etiketten bevakning och båda punkterna', async () => {
  const { api, anrop } = fejk({ 'POST /labels': { status: 422 }, 'GET /issues': [], 'POST /issues': { number: 50 } });
  assert.deepEqual(await G.uppfoljning({ api, rapport: RAP_1A, runUrl: 'run' }), [50]);
  const skapade = anrop.filter(a => a.metod === 'POST' && a.sokvag === '/issues');
  assert.equal(skapade.length, 1); // bara 1a, inte 1b
  const i = skapade[0].body;
  assert.equal(i.title, 'Uppföljning efter riksdagsbeslut: Vinst i skolan');
  assert.deepEqual(i.labels, ['bevakning']);
  assert.match(i.body, /- \[ \] Granska `transition` och `ikraft` mot den nya mallmeningen/);
  assert.match(i.body, /- \[ \] För in SFS och ikraftträdande när lagen är utfärdad/);
  assert.match(i.body, /stänger denna issue först när SFS och ikraftträdande är införda/);
  assert.match(i.body, /rskr\. 2025\/26:438/);
});

test('uppföljning: finns redan en öppen issue med samma titel skapas ingen ny', async () => {
  const { api, anrop } = fejk({ 'POST /labels': { status: 422 }, 'GET /issues': [{ number: 50, title: 'Uppföljning efter riksdagsbeslut: Vinst i skolan' }] });
  assert.deepEqual(await G.uppfoljning({ api, rapport: RAP_1A, runUrl: 'run' }), []);
  assert.equal(anrop.some(a => a.metod === 'POST' && a.sokvag === '/issues'), false);
});

test('uppföljning: inga 1a-ändringar → inga anrop alls', async () => {
  const { api, anrop } = fejk({});
  assert.deepEqual(await G.uppfoljning({ api, rapport: { datum: 'x', andringar: [{ regel: '1c', post: 'p' }] }, runUrl: 'r' }), []);
  assert.equal(anrop.length, 0);
});
