#!/usr/bin/env node
// rapport.js — bygger veckorapportens issue-body (Sprint 10 T4).
// CJS, zero-dependency. Tar riksdagen-rapporten + rss-rapporten (JSON-filer
// producerade av riksdagen.js och rss.js) och skriver Markdown för GitHub-issuet.
//
// Sektioner per detekteringsjobb (A prop-status / B nya direktiv / B2 nya
// propositioner / C tilläggsdir / lagrådsremisser). Varje delta renderas som
// faktapar med primärkällänk och en tom triage-kryssruta — människan bockar av
// vid hantering. Okända delta-typer hamnar i "Övrigt" med rå JSON, aldrig
// tyst tappade.
//
// Workflow-kontrakt: om env GITHUB_OUTPUT är satt appendas
//   har_deltan=true|false
//   antal_deltan=<n>
//   titel=Bevakningsrapport v.<ISO-vecka> <ISO-år>
// dit — workflowet läser har_deltan för att hoppa över issue-skapandet vid tom
// körning. Fel (saknad/oparsbar indatafil) → exit 1, aldrig tom rapport.
//
// CLI:
//   node rapport.js --riksdagen delta.json --rss rss.json [--out rapport.md]
//   (utan --out skrivs Markdown till stdout)

'use strict';

const fs = require('fs');

// ----------------------------- ISO-vecka -------------------------------------

// ISO 8601-vecka + veckoår (UTC). OBS veckoåret skiljer sig från kalenderåret
// vid årsskiften: 2027-01-01 är v.53 2026.
function isoWeek(d) {
  const date = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  const day = date.getUTCDay() || 7; // söndag=0 → 7
  date.setUTCDate(date.getUTCDate() + 4 - day); // närmaste torsdag avgör vecka/år
  const year = date.getUTCFullYear();
  const yearStart = new Date(Date.UTC(year, 0, 1));
  const week = Math.ceil(((date - yearStart) / 86400000 + 1) / 7);
  return { week, year };
}

// ----------------------------- Rendering per delta-typ -----------------------

function mdEscape(s) {
  // Minimal: bara tecken som bryter länk-/listsyntax i våra fält.
  return String(s).replace(/([\[\]])/g, '\\$1');
}

function renderPropStatus(d) {
  const rader = [];
  const fil = d.datafilen_sager ? d.datafilen_sager.status : null;
  const kalla = d.kalla_fil || (d.datafilen_sager && d.datafilen_sager.kalla_fil) || '?';
  if (!d.api_sager || !d.api_sager.found) {
    rader.push(`- [ ] **${d.beteckning}** — hittades INTE i riksdagens API (anomali). Datafilen säger: \`${fil}\` (${kalla})`);
    rader.push(`  - [Sökfråga](${d.url})`);
    return rader;
  }
  rader.push(`- [ ] **${d.beteckning}** — datafilen säger: \`${fil}\` (${kalla})`);
  for (const b of d.api_sager.betankanden || []) {
    if (b.beslut_fattat) {
      const rskr = b.rskr ? `, rskr ${b.rskr}` : '';
      rader.push(`  - Betänkande ${b.bet}: ${b.statustext || 'beslut fattat'} — beslut ${b.beslutsdatum}${rskr}. ${b.rdbeslut || ''}`.trimEnd());
    } else {
      rader.push(`  - Betänkande ${b.bet}: ännu inget beslut${b.statustext ? ` (${b.statustext})` : ''}`);
    }
  }
  rader.push(`  - [Dokumentstatus](${d.url})`);
  return rader;
}

function renderEnkel(d) {
  // nytt-direktiv / ny-proposition: beteckning + titel + datum + källa
  return [`- [ ] **${d.beteckning}** ${mdEscape(d.titel || '(titel saknas)')} (${d.datum || 'datum saknas'}) — [källa](${d.url})`];
}

function renderSouLevererad(d) {
  return [`- [ ] **${d.beteckning}** ${mdEscape(d.titel || '(titel saknas)')} (${d.datum || 'datum saknas'}) — spårad utredning **${d.utredning}** har publicerat — [källa](${d.url})`];
}

function renderNySou(d) {
  const ledtrad = d.betankande_av ? ` — betänkande av ${mdEscape(d.betankande_av)}` : '';
  return [`- [ ] **${d.beteckning}** ${mdEscape(d.titel || '(titel saknas)')} (${d.datum || 'datum saknas'})${ledtrad} — [källa](${d.url})`];
}

function renderTillaggsdir(d) {
  return [`- [ ] **${d.direktiv_beteckning}** → spårad utredning **${d.kopplad_utredning}**: ${mdEscape(d.titel || '')} (${d.datum || 'datum saknas'}) — [källa](${d.url})`];
}

function renderLagradsremiss(d) {
  return [`- [ ] **${mdEscape(d.titel)}** (${d.datum}) — [lagrådsremiss](${d.url})`];
}

const SEKTIONER = [
  { typ: 'prop-status', rubrik: 'A. Propositionsstatus — betänkandebeslut att triagera', render: renderPropStatus },
  { typ: 'nytt-direktiv', rubrik: 'B. Nya direktiv (Utbildningsdep.)', render: renderEnkel },
  { typ: 'ny-proposition', rubrik: 'B2. Nya propositioner (Utbildningsdep.)', render: renderEnkel },
  // SOU bär inget departement i riksdagens data (se riksdagen.js EMPIRI SOU)
  // — ny-sou listar därför alla departement och människan avgör scope.
  { typ: 'sou-levererad', rubrik: 'B3. Betänkanden från spårade utredningar', render: renderSouLevererad },
  { typ: 'ny-sou', rubrik: 'B3. Nya SOU (alla departement — SOU saknar departementsdata)', render: renderNySou },
  { typ: 'tillaggsdir-till-tracked-utredning', rubrik: 'C. Tilläggsdirektiv till spårade utredningar', render: renderTillaggsdir },
  { typ: 'lagradsremiss', rubrik: 'Lagrådsremisser (Utbildningsdep.)', render: renderLagradsremiss },
];

// ----------------------------- Toppfunktion ----------------------------------

function buildRapport({ riksdagen, rss, nu = new Date() } = {}) {
  if (!riksdagen || !Array.isArray(riksdagen.deltan)) throw new Error('buildRapport: riksdagen-rapport saknar deltan');
  if (!rss || !Array.isArray(rss.deltan)) throw new Error('buildRapport: rss-rapport saknar deltan');

  const alla = [...riksdagen.deltan, ...rss.deltan];
  const { week, year } = isoWeek(nu);
  const titel = `Bevakningsrapport v.${week} ${year}`;

  const rader = [];
  rader.push(`**Fönster:** ${riksdagen.fonster.from} → ${riksdagen.fonster.tom}`);
  rader.push('');

  if (rss.fonster_fullt_tackt === false) {
    rader.push(`> ⚠️ RSS-fönstret är inte fullt täckt av flödet (äldsta post: ${rss.aldsta_post_i_flodet}). En tom lagrådsremiss-sektion kan bero på flödesdjupet, inte på att inget publicerats.`);
    rader.push('');
  }

  const renderade = new Set();
  for (const sektion of SEKTIONER) {
    const deltan = alla.filter(d => d.typ === sektion.typ);
    deltan.forEach(d => renderade.add(d));
    if (deltan.length === 0) continue; // tomma sektioner visas inte
    rader.push(`## ${sektion.rubrik} (${deltan.length})`);
    rader.push('');
    for (const d of deltan) rader.push(...sektion.render(d));
    rader.push('');
  }

  // Okända typer får aldrig försvinna tyst — rå JSON i egen sektion.
  const okanda = alla.filter(d => !renderade.has(d));
  if (okanda.length > 0) {
    rader.push(`## Övrigt — okänd delta-typ (${okanda.length})`);
    rader.push('');
    for (const d of okanda) rader.push(`- [ ] \`${JSON.stringify(d)}\``);
    rader.push('');
  }

  if (alla.length === 0) {
    rader.push('_Inga deltan i fönstret._');
    rader.push('');
  }

  const k = riksdagen.antal_kontrollerade || {};
  rader.push('---');
  rader.push(`**Kontrollerat:** ${k.props ?? '?'} props i manifestet (${k.props_terminala_skippade ?? '?'} terminala skippade) · ${k.props_i_fonster ?? '?'} props i fönstret · ${k.dir_i_fonster ?? '?'} direktiv i fönstret · ${k.utredningar_sparade ?? '?'} spårade utredningar · ${rss.antal_i_flodet ?? '?'} poster i RSS-flödet`);
  rader.push(`**Körningar:** riksdagen ${riksdagen.korning} · RSS ${rss.korning}`);
  rader.push('');
  rader.push('_Bocka av varje punkt när den är triagerad. Rutinen finns i docs/BEVAKNING.md._');

  return {
    titel,
    body: rader.join('\n'),
    antalDeltan: alla.length,
    harDeltan: alla.length > 0,
  };
}

// ----------------------------- CLI -------------------------------------------

function parseArgs(argv) {
  const opts = { riksdagen: null, rss: null, out: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--riksdagen') opts.riksdagen = argv[++i];
    else if (a === '--rss') opts.rss = argv[++i];
    else if (a === '--out') opts.out = argv[++i];
    else if (a === '--help' || a === '-h') opts.help = true;
  }
  return opts;
}

function lasJson(fil, namn) {
  let text;
  try {
    text = fs.readFileSync(fil, 'utf8');
  } catch (err) {
    throw new Error(`Kan inte läsa ${namn}-rapporten (${fil}): ${err.message}`);
  }
  try {
    return JSON.parse(text);
  } catch (err) {
    throw new Error(`Oparsbar JSON i ${namn}-rapporten (${fil}): ${err.message}`);
  }
}

module.exports = { buildRapport, isoWeek };

if (require.main === module) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help || !opts.riksdagen || !opts.rss) {
    process.stdout.write('Användning: node rapport.js --riksdagen <fil> --rss <fil> [--out <fil>]\n');
    process.exit(opts.help ? 0 : 1);
  }
  try {
    const riksdagen = lasJson(opts.riksdagen, 'riksdagen');
    const rss = lasJson(opts.rss, 'rss');
    const rapport = buildRapport({ riksdagen, rss });

    if (opts.out) fs.writeFileSync(opts.out, rapport.body + '\n');
    else process.stdout.write(rapport.body + '\n');

    // Workflow-kontrakt: skriv flaggor till GITHUB_OUTPUT när det finns.
    if (process.env.GITHUB_OUTPUT) {
      fs.appendFileSync(process.env.GITHUB_OUTPUT,
        `har_deltan=${rapport.harDeltan}\nantal_deltan=${rapport.antalDeltan}\ntitel=${rapport.titel}\n`);
    }
    process.stderr.write(`rapport: ${rapport.antalDeltan} deltan, titel "${rapport.titel}"\n`);
  } catch (err) {
    process.stderr.write(`FEL: ${err.message}\n`);
    process.exit(1);
  }
}
