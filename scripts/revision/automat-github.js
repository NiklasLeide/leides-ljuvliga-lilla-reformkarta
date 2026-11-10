#!/usr/bin/env node
// automat-github.js — automatfilens GitHub-sida (Sprint 15 T4): regel 7 (automat-stopp-issue)
// och regel 9 (kommentar i den fasta issuen "Automatlogg"). REST via fetch, GITHUB_TOKEN och
// GITHUB_REPOSITORY från Actions-miljön. Testbar med injicerad fetch (automat-github.test.js).
//   node scripts/revision/automat-github.js stopp --rapport r.json --run-url <url>
//   node scripts/revision/automat-github.js logg  --rapport r.json --sha <sha> --run-url <url>
'use strict';
const fs = require('fs');

const ETIKETT_STOPP = 'automat-stopp';
const ETIKETT_LOGG = 'automatlogg';
const LOGG_TITEL = 'Automatlogg';

function klient({ token, repo, fetchImpl = fetch }) {
  const bas = `https://api.github.com/repos/${repo}`;
  return async (metod, sokvag, body) => {
    const r = await fetchImpl(bas + sokvag, {
      method: metod,
      headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'User-Agent': 'reformkartan-automat' },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (metod === 'POST' && sokvag === '/labels' && r.status === 422) return null; // etiketten finns redan
    if (!r.ok) throw new Error(`GitHub ${metod} ${sokvag}: HTTP ${r.status}`);
    return r.status === 204 ? null : r.json();
  };
}

const rad = (a) => `| ${a.regel} | ${a.post} | ${a.falt} | ${typeof a.nytt === 'object' ? a.nytt.nr || JSON.stringify(a.nytt) : a.nytt} | ${a.kalla_url || '—'} |`;
function andringstabell(rapport) {
  if (!rapport.andringar || !rapport.andringar.length) return '_Inga ändringar._';
  return ['| Regel | Post | Fält | Nytt värde | Källa |', '|---|---|---|---|---|', ...rapport.andringar.map(rad)].join('\n');
}
function veckorutinlista(rapport) {
  const v = rapport.veckorutin || [];
  return v.length ? v.map(x => `- ${x.post} (${x.regel || '—'}): ${x.skal}${x.url ? ` — ${x.url}` : ''}`).join('\n') : '_Inga._';
}

function stoppBody(rapport, runUrl) {
  return [
    `Automatfilen stoppade ${rapport.datum}. **Ingenting publicerades.**`, '',
    `**Orsak:** ${rapport.stopp || 'fel i arbetsflödet (se körningen)'}`, '',
    '### Planerade ändringar (inte tillämpade)', andringstabell(rapport), '',
    '### Till veckorutinen', veckorutinlista(rapport), '',
    rapport.fel && rapport.fel.length ? `### Fel\n${rapport.fel.map(f => `- ${f.objekt}: ${f.fel}`).join('\n')}\n` : '',
    `Körning: ${runUrl}`, '',
    '_Veckorutinen läser öppna issues med etiketten automat-stopp. Stäng när orsaken är hanterad. Automatfilen stängs av med repovariabeln AUTOMAT_AKTIV (se docs/MAINTENANCE.md)._',
  ].join('\n');
}

function loggBody(rapport, sha, runUrl) {
  return [
    `**${rapport.datum}** — publicerat i ${sha ? sha.slice(0, 7) : '—'} (${runUrl})`, '',
    andringstabell(rapport), '',
    (rapport.veckorutin || []).length ? `Till veckorutinen:\n${veckorutinlista(rapport)}` : '',
  ].join('\n').trim();
}

async function stopp({ api, rapport, runUrl }) {
  await api('POST', '/labels', { name: ETIKETT_STOPP, color: 'b91c1c', description: 'Automatfilen stoppade — ingenting publicerades' });
  return api('POST', '/issues', { title: `Automat-stopp ${rapport.datum}`, body: stoppBody(rapport, runUrl), labels: [ETIKETT_STOPP] });
}

async function logg({ api, rapport, sha, runUrl }) {
  const oppna = await api('GET', `/issues?labels=${ETIKETT_LOGG}&state=open&per_page=10`);
  let nr = (oppna || []).find(i => i.title === LOGG_TITEL);
  if (!nr) {
    await api('POST', '/labels', { name: ETIKETT_LOGG, color: '1d4ed8', description: 'Fast logg över automatfilens publiceringar' });
    nr = await api('POST', '/issues', { title: LOGG_TITEL, labels: [ETIKETT_LOGG],
      body: 'Fast logg: automatfilen (scripts/revision/automat.js, .github/workflows/automat.yml) kommenterar här vid varje publicering. Stäng inte.' });
  }
  await api('POST', `/issues/${nr.number}/comments`, { body: loggBody(rapport, sha, runUrl) });
  return nr.number;
}

function arg(namn) { const i = process.argv.indexOf(namn); return i > 0 ? process.argv[i + 1] : null; }

if (require.main === module) {
  (async () => {
    const kommando = process.argv[2];
    const rapport = arg('--rapport') && fs.existsSync(arg('--rapport'))
      ? JSON.parse(fs.readFileSync(arg('--rapport'), 'utf8'))
      : { datum: new Date().toISOString().slice(0, 10), stopp: 'rapport saknas — automatfilen kraschade före rapporten', andringar: [], veckorutin: [], fel: [] };
    const api = klient({ token: process.env.GITHUB_TOKEN, repo: process.env.GITHUB_REPOSITORY });
    if (kommando === 'stopp') console.log('automat-stopp-issue #' + (await stopp({ api, rapport, runUrl: arg('--run-url') })).number);
    else if (kommando === 'logg') console.log('Automatlogg #' + (await logg({ api, rapport, sha: arg('--sha'), runUrl: arg('--run-url') })));
    else throw new Error('kommando: stopp | logg');
  })().catch(e => { console.error('automat-github FEL:', e.message); process.exit(1); });
}

module.exports = { klient, stopp, logg, stoppBody, loggBody, ETIKETT_STOPP, ETIKETT_LOGG, LOGG_TITEL };
