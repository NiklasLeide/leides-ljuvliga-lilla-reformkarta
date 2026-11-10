#!/usr/bin/env node
// automat.js — automatfilen (Sprint 15 T2, DEC-019/DEC-022).
// Deterministiskt skript som tillämpar ENDAST rutinändringar ur riksdagens öppna data.
// Torrkörning är standard: utan --tillampa skrivs ingenting.
//
// REGLER (Sprint 15-briefen; varje regel har test i automat.test.js):
//  1a Spårad proposition (reforms.json, status "proposition", ref "Prop. …"): när ALLA betänkanden
//     som behandlar propositionen har riksdagsbeslut (BES inträffat + rskr) OCH fullt bifall →
//     status "beslutad" och transition får mallmeningen "Riksdagen beslutade {datum} (bet. …, rskr. …)."
//     framför befintlig text. Fullt bifall = varje förslagspunkt vunnen av utskottet, kammarens beslut
//     "Kammaren biföll utskottets förslag." och utskottets sammanfattning börjar med "Bifall till
//     proposition" utan delvis/i huvudsak/med ändring/avslag på proposition. Annars → veckorutinen.
//  1b Spårad utredning: nytt tilläggsdirektiv (nr, titel, datum) när BÅDE kommittébeteckning OCH
//     utredningens namn stämmer. Bara det ena → veckorutinen (riksdagens metadata var fel för Dir. 2026:98).
//  1c Spårad utredning: nytt betänkande (SOU-nr, titel, typ ur titelsidan, riksdagens datum).
//     Utredningens status ändras inte. Finns en betänkanderad utan nummer → veckorutinen.
//  1d Följdändringar: andringar-post (märkt "Hämtat automatiskt från riksdagens öppna data.") och
//     meta.json senast_uppdaterad. Ingen andringar-post för händelser före loggens första datum.
//  2  Aldrig: SFS, ikraftträdanden, övergångsbestämmelser, nya poster, strykningar, fritext.
//  3  Ett ifyllt värde skrivs aldrig över (utom statusbytet i 1a). Upprätthålls av vakt() som jämför
//     filerna före och efter — allt utanför de tillåtna ändringarna stoppar körningen.
//  4  Text byggs med fasta mallar (MALL) ur källans fält; status och transition ändras tillsammans.
//  5  Högst 5 ändringar (1a–1c) per körning; fler → stopp, ingenting skrivs.
// Regel 6–9 (validering före publicering, automat-stopp-issue, AUTOMAT_AKTIV, Automatlogg) ligger i
// .github/workflows/automat.yml, som använder rapporten (--rapport) från detta skript.
//
// CLI:
//   node scripts/revision/automat.js                         # torrkörning, rapport till stdout
//   node scripts/revision/automat.js --tillampa --rapport ut.json [--data dir] [--idag YYYY-MM-DD]
// Exit: 0 = klart (med eller utan ändringar), 3 = STOPP (regel 5 eller vakt), 1 = fel.
'use strict';

const fs = require('fs');
const path = require('path');
const R = require('./revision.js');

const MARKERING = 'Hämtat automatiskt från riksdagens öppna data.';
const MAX_ANDRINGAR = 5;
const asArray = (x) => (x == null ? [] : (Array.isArray(x) ? x : [x]));

// ----------------------------- Textmallar (regel 4) ---------------------------
const MALL = {
  transition1a: (b) => `Riksdagen beslutade ${b.beslutsdatum} (bet. ${b.bet}, rskr. ${b.rskr}).`,
  andring1a: (prop) => `Riksdagen beslutade om propositionen ${prop.titel} (${prop.beteckning}). ${MARKERING}`,
  kalla1a: (b) => `Riksdagsbeslut — bet. ${b.bet}, rskr. ${b.rskr}`,
  andring1b: (utr, dir) => `Regeringen beslutade tilläggsdirektiv till ${utr.titel} (${dir.nr}). ${MARKERING}`,
  andring1c: (utr, sou) => `${sou.typ === 'slut' ? 'Slutbetänkandet' : sou.typ === 'del' ? 'Delbetänkandet' : 'Betänkandet'} ${sou.nr} (${sou.titel}) från ${utr.titel} publicerades. ${MARKERING}`,
};

// ----------------------------- Regel 1a ---------------------------------------
const EJ_FULLT = /delvis|i huvudsak|med (den )?ändring|avslag på (regeringens )?propositione?n?|avslag på proposition/i;
function fulltBifall(betankanden) {
  if (!betankanden.length) return { ok: false, skal: 'inga betänkanden' };
  for (const b of betankanden) {
    const bi = b.bifall || {};
    if (!b.riksdagsbeslut) return { ok: false, skal: `${b.bet}: inget riksdagsbeslut enligt rskr-regeln` };
    if (!bi.alla_punkter_utskottet) return { ok: false, skal: `${b.bet}: inte alla förslagspunkter vunna av utskottet` };
    if (bi.rdbeslut !== 'Kammaren biföll utskottets förslag.') return { ok: false, skal: `${b.bet}: kammarens beslut "${bi.rdbeslut}"` };
    if (!/^Bifall till proposition/.test(bi.sammanfattning || '') || EJ_FULLT.test(bi.sammanfattning || '')) {
      return { ok: false, skal: `${b.bet}: utskottets förslag "${bi.sammanfattning}"` };
    }
  }
  return { ok: true, skal: null };
}

function regel1a(reform, lage) {
  if (reform.status !== 'proposition' || !/^Prop\./.test(reform.ref || '')) return {};
  if (!lage || !lage.hittad) return { veckorutin: { post: reform.id, skal: `${reform.ref} hittas inte i riksdagens data` } };
  if (!lage.betankanden.length || !lage.betankanden.every(b => b.riksdagsbeslut)) return {}; // inte beslutat än
  const fb = fulltBifall(lage.betankanden);
  if (!fb.ok) return { veckorutin: { post: reform.id, regel: '1a', skal: `inte fullt bifall — ${fb.skal}`, url: lage.betankanden[0].url } };
  const mening = lage.betankanden.map(MALL.transition1a).join(' ');
  const forsta = lage.betankanden[0];
  return {
    andring: {
      regel: '1a', fil: 'reforms.json', post: reform.id, falt: 'status + transition',
      nuvarde: reform.status, nytt: 'beslutad', transition_tillagg: mening, kalla_url: forsta.url,
      andringar_post: {
        datum: lage.betankanden.map(b => b.beslutsdatum).sort().slice(-1)[0],
        text: MALL.andring1a(lage), reform_ids: [reform.id],
        kalla: { text: lage.betankanden.map(MALL.kalla1a).join('; '), url: forsta.url },
      },
    },
  };
}

// ----------------------------- Regel 1b ---------------------------------------
// "Tilläggsdirektiv till Utredningen om X (U 2025:04)" → "Utredningen om X"
function namnUrDirTitel(titel) {
  const m = /^Tilläggsdirektiv till (.*?)\s*\(([A-ZÅÄÖ]{1,3}\s+\d{4}:\d+)\)\s*$/i.exec(titel || '');
  return m ? { namn: m[1], bet: m[2].replace(/\s+/g, ' ') } : null;
}
// Normaliserar utredningsnamn: gemener, enkla mellanslag, utan inledande "utredningen (om)".
function normNamn(s) {
  return R.norm(s).replace(/^utredningen\s+(om\s+)?/, '');
}
function regel1b(utr, dirEntries) {
  const ut = { andringar: [], veckorutin: [] };
  if (!utr.beteckning) return ut;
  const kanda = new Set(asArray(utr.direktiv).map(d => d && d.nr).filter(Boolean));
  const sedda = new Set();
  for (const e of dirEntries) {
    const dnr = e && e.rm && e.beteckning ? `Dir. ${e.rm}:${e.beteckning}` : null;
    if (!dnr || kanda.has(dnr) || sedda.has(dnr)) continue;
    const t = namnUrDirTitel(e.titel);
    if (!t) continue; // inte ett tilläggsdirektiv
    const kb = R.kommittebeteckning(e);
    const kbMatch = kb === utr.beteckning;
    const namnMatch = normNamn(t.namn) === normNamn(utr.titel);
    const titelBet = t.bet === utr.beteckning;
    if (!kbMatch && !namnMatch && !titelBet) continue; // sökträff som gäller annan utredning
    sedda.add(dnr);
    const url = R.absUrl(e.dokument_url_html) || `${R.API_BASE}/dokument/${e.dok_id}.html`;
    if (kbMatch && namnMatch) {
      const dir = { nr: dnr, datum: R.datum10(e.datum), typ: 'tilläggs', titel: (e.titel || '').replace(/\s*\([A-ZÅÄÖ]{1,3}\s+\d{4}:\d+\)\s*$/, '') };
      ut.andringar.push({
        regel: '1b', fil: 'utredningar.json', post: utr.id, falt: 'direktiv (ny rad)', nuvarde: null, nytt: dir, kalla_url: url,
        andringar_post: { datum: dir.datum, text: MALL.andring1b(utr, dir), reform_ids: [], kalla: { text: dnr, url } },
      });
    } else {
      ut.veckorutin.push({ post: utr.id, regel: '1b', url,
        skal: `${dnr}: ${kbMatch ? 'kommittébeteckningen' : 'namnet'} stämmer men inte ${kbMatch ? 'namnet' : 'kommittébeteckningen'} (riksdagen: ${kb || '—'}, titel: "${e.titel}")` });
    }
  }
  return ut;
}

// ----------------------------- Regel 1c ---------------------------------------
function regel1c(utr, souLista) {
  const ut = { andringar: [], veckorutin: [] };
  const kanda = new Set(asArray(utr.betankanden).map(b => b && b.nr).filter(Boolean));
  const harTomRad = asArray(utr.betankanden).some(b => b && !b.nr);
  const sedda = new Set();
  for (const e of souLista) {
    const { typ, av } = R.souAvsandare(e);
    if (!av || R.norm(av) !== R.norm(utr.titel)) continue;
    const nr = R.souNr(e);
    if (!nr || kanda.has(nr) || sedda.has(nr)) continue;
    sedda.add(nr);
    const url = R.absUrl(e.dokument_url_html) || `${R.API_BASE}/dokument/${e.dok_id}.html`;
    if (harTomRad) {
      ut.veckorutin.push({ post: utr.id, regel: '1c', url, skal: `${nr}: utredningen har en betänkanderad utan nummer — kan vara samma betänkande` });
      continue;
    }
    const sou = { nr, titel: e.titel || null, typ: typ || null, datum: R.datum10(e.datum) };
    ut.andringar.push({
      regel: '1c', fil: 'utredningar.json', post: utr.id, falt: 'betankanden (ny rad)', nuvarde: null, nytt: sou, kalla_url: url,
      andringar_post: { datum: sou.datum, text: MALL.andring1c(utr, sou), reform_ids: [], kalla: { text: nr, url } },
    });
  }
  return ut;
}

// ----------------------------- Planering (läser API) --------------------------
async function hamtaDir(bet, { fetcher, delayMs }) {
  const params = new URLSearchParams({ doktyp: 'dir', sok: `"${bet}"`, utformat: 'json', sz: '50' });
  const data = await fetcher(`${R.API_BASE}/dokumentlista/?${params}`);
  if (delayMs) await new Promise(r => setTimeout(r, delayMs));
  return R.listDocs(data);
}

async function planera({ dataDir, fetcher, delayMs = 300 }) {
  const reforms = JSON.parse(fs.readFileSync(path.join(dataDir, 'reforms.json'), 'utf8'));
  const utredningar = JSON.parse(fs.readFileSync(path.join(dataDir, 'utredningar.json'), 'utf8'));
  const reformIds = new Set(reforms.map(r => r.id));
  const plan = { andringar: [], veckorutin: [], fel: [] };

  for (const r of reforms) {
    if (r.status !== 'proposition' || !/^Prop\./.test(r.ref || '')) continue;
    try {
      const res = regel1a(r, await R.propLage(r.ref, { fetcher, delayMs }));
      if (res.andring) plan.andringar.push(res.andring);
      if (res.veckorutin) plan.veckorutin.push(res.veckorutin);
    } catch (err) { plan.fel.push({ objekt: r.ref, fel: err.message }); }
  }

  const tidigast = utredningar.map(u => u.tillsatt).filter(Boolean).sort()[0] || '2020-01-01';
  let souLista = [];
  try { souLista = await R.allaSou(`${tidigast.slice(0, 4)}-01-01`, { fetcher, delayMs }); }
  catch (err) { plan.fel.push({ objekt: 'SOU-lista', fel: err.message }); }

  for (const u of utredningar) {
    const koppla = (a) => { if (a.andringar_post && reformIds.has(u.kopplad_reform)) a.andringar_post.reform_ids = [u.kopplad_reform]; return a; };
    try {
      if (u.beteckning) {
        const b = regel1b(u, await hamtaDir(u.beteckning, { fetcher, delayMs }));
        plan.andringar.push(...b.andringar.map(koppla)); plan.veckorutin.push(...b.veckorutin);
      }
      const c = regel1c(u, souLista);
      plan.andringar.push(...c.andringar.map(koppla)); plan.veckorutin.push(...c.veckorutin);
    } catch (err) { plan.fel.push({ objekt: u.beteckning || u.id, fel: err.message }); }
  }
  return plan;
}

// ----------------------------- Tillämpning (rena funktioner) ------------------
// utredningar.json har handformaterade rader ({ "nr": … } på en rad) — rader läggs till med samma
// format genom textinsättning i rätt lista, så att resten av filen lämnas orörd.
function radJson(obj) {
  return '{ ' + Object.entries(obj).map(([k, v]) => `${JSON.stringify(k)}: ${JSON.stringify(v)}`).join(', ') + ' }';
}
function laggTillRad(text, utrId, nyckel, obj) {
  const i = text.indexOf(`"id": ${JSON.stringify(utrId)}`);
  if (i < 0) throw new Error(`utredning ${utrId} saknas i texten`);
  const slutPost = text.indexOf('\n  }', i);
  const k = text.indexOf(`"${nyckel}": [`, i);
  if (k < 0 || k > slutPost) throw new Error(`${utrId}: listan ${nyckel} saknas`);
  const start = text.indexOf('[', k);
  let djup = 0, j = start;
  for (; j < text.length; j++) { if (text[j] === '[') djup++; else if (text[j] === ']') { djup--; if (djup === 0) break; } }
  const inne = text.slice(start + 1, j);
  const rad = radJson(obj);
  const ny = inne.trim() === '' ? `\n      ${rad}\n    ` : `${inne.replace(/\s*$/, '')},\n      ${rad}\n    `;
  return text.slice(0, start + 1) + ny + text.slice(j);
}

function tillampa(filer, plan, idag) {
  const reforms = JSON.parse(JSON.stringify(filer.reforms));
  let utrText = filer.utredningarText;
  const andringar = JSON.parse(JSON.stringify(filer.andringar));
  const meta = JSON.parse(JSON.stringify(filer.meta));
  const logStart = filer.andringar.map(a => a.datum).sort()[0] || '0000-00-00';
  const nyaPoster = [];
  for (const a of plan.andringar) {
    if (a.regel === '1a') {
      const r = reforms.find(x => x.id === a.post);
      r.status = 'beslutad';
      r.transition = r.transition ? `${a.transition_tillagg} ${r.transition}` : a.transition_tillagg;
    } else if (a.regel === '1b') {
      utrText = laggTillRad(utrText, a.post, 'direktiv', a.nytt);
    } else if (a.regel === '1c') {
      utrText = laggTillRad(utrText, a.post, 'betankanden', a.nytt);
    } else throw new Error(`okänd regel ${a.regel}`);
    if (a.andringar_post && a.andringar_post.datum >= logStart) nyaPoster.push(a.andringar_post);
  }
  const allaAndringar = nyaPoster.concat(andringar).sort((x, y) => (x.datum < y.datum ? 1 : x.datum > y.datum ? -1 : 0));
  if (plan.andringar.length) meta.senast_uppdaterad = idag;
  return { reforms, utredningarText: utrText, andringar: allaAndringar, meta, nyaPoster };
}

// ----------------------------- Vakt (regel 2 och 3) ---------------------------
const lika = (a, b) => JSON.stringify(a) === JSON.stringify(b);
function vakt(fore, efter) {
  const brott = [];
  // reforms.json: bara status proposition→beslutad + transition där gammal text ligger kvar ordagrant sist
  if (fore.reforms.length !== efter.reforms.length) brott.push('reforms.json: antal poster ändrat');
  fore.reforms.forEach((f, i) => {
    const e = efter.reforms[i] || {};
    if (f.id !== e.id) { brott.push(`reforms.json: post ${i} bytt id`); return; }
    const nycklar = new Set([...Object.keys(f), ...Object.keys(e)]);
    for (const k of nycklar) {
      if (lika(f[k], e[k])) continue;
      if (k === 'status' && f.status === 'proposition' && e.status === 'beslutad') continue;
      if (k === 'transition' && typeof e.transition === 'string' && /^Riksdagen beslutade \d{4}-\d{2}-\d{2} \(bet\. /.test(e.transition)
          && (!f.transition || e.transition.endsWith(' ' + f.transition))) continue;
      brott.push(`reforms.json ${f.id}.${k}: otillåten ändring`);
    }
    if ((f.status !== e.status) !== (f.transition !== e.transition)) brott.push(`reforms.json ${f.id}: status och transition måste ändras tillsammans`);
  });
  // utredningar.json: bara nya rader sist i direktiv/betankanden, med tillåtna nycklar
  const fu = JSON.parse(fore.utredningarText), eu = JSON.parse(efter.utredningarText);
  if (fu.length !== eu.length) brott.push('utredningar.json: antal poster ändrat');
  fu.forEach((f, i) => {
    const e = eu[i] || {};
    if (f.id !== e.id) { brott.push(`utredningar.json: post ${i} bytt id`); return; }
    for (const k of new Set([...Object.keys(f), ...Object.keys(e)])) {
      if (lika(f[k], e[k])) continue;
      const tillat = { direktiv: ['nr', 'datum', 'typ', 'titel'], betankanden: ['nr', 'titel', 'typ', 'datum'] }[k];
      const fa = asArray(f[k]), ea = asArray(e[k]);
      if (tillat && ea.length > fa.length && lika(ea.slice(0, fa.length), fa)
          && ea.slice(fa.length).every(x => lika(Object.keys(x), tillat) && x.nr)) continue;
      brott.push(`utredningar.json ${f.id}.${k}: otillåten ändring`);
    }
  });
  // andringar.json: alla gamla poster oförändrade och i samma ordning; nya poster märkta
  const nya = efter.andringar.filter(a => !fore.andringar.some(b => lika(a, b)));
  const gamlaKvar = efter.andringar.filter(a => fore.andringar.some(b => lika(a, b)));
  if (!lika(gamlaKvar, fore.andringar)) brott.push('andringar.json: befintliga poster ändrade, strukna eller omordnade');
  for (const n of nya) if (!String(n.text || '').endsWith(MARKERING)) brott.push(`andringar.json: ny post utan märkning (${n.datum})`);
  // meta.json: bara datumfälten
  for (const k of new Set([...Object.keys(fore.meta), ...Object.keys(efter.meta)])) {
    if (!lika(fore.meta[k], efter.meta[k]) && !['senast_uppdaterad', 'senast_kontrollerad'].includes(k)) brott.push(`meta.json ${k}: otillåten ändring`);
  }
  return brott;
}

// ----------------------------- Huvudflöde -------------------------------------
function lasFiler(dataDir) {
  const las = (f) => fs.readFileSync(path.join(dataDir, f), 'utf8');
  return {
    reformsText: las('reforms.json'), reforms: JSON.parse(las('reforms.json')),
    utredningarText: las('utredningar.json'),
    andringarText: las('andringar.json'), andringar: JSON.parse(las('andringar.json')),
    metaText: las('meta.json'), meta: JSON.parse(las('meta.json')),
  };
}
// Skriver med samma slutradbrytning som originalet (reforms.json har ingen, andringar/meta har en).
function skriv(dataDir, fil, obj, originalText) {
  const nl = originalText.endsWith('\n') ? '\n' : '';
  fs.writeFileSync(path.join(dataDir, fil), JSON.stringify(obj, null, 2) + nl);
}

async function kor({ dataDir, fetcher, tillampaLage = false, idag, delayMs }) {
  const plan = await planera({ dataDir, fetcher, delayMs });
  const rapport = { datum: idag, lage: tillampaLage ? 'tillampa' : 'torr', andringar: plan.andringar, veckorutin: plan.veckorutin, fel: plan.fel, stopp: null, skrivet: false };
  if (plan.fel.length) { rapport.stopp = `fel vid hämtning (${plan.fel.length})`; return rapport; }
  if (plan.andringar.length > MAX_ANDRINGAR) { rapport.stopp = `regel 5: ${plan.andringar.length} ändringar > ${MAX_ANDRINGAR}`; return rapport; }
  const fore = lasFiler(dataDir);
  const efter = tillampa(fore, plan, idag);
  const brott = vakt(fore, efter);
  if (brott.length) { rapport.stopp = 'vakt: ' + brott.join('; '); return rapport; }
  rapport.nya_andringar_poster = efter.nyaPoster;
  if (tillampaLage && plan.andringar.length) {
    skriv(dataDir, 'reforms.json', efter.reforms, fore.reformsText);
    fs.writeFileSync(path.join(dataDir, 'utredningar.json'), efter.utredningarText);
    skriv(dataDir, 'andringar.json', efter.andringar, fore.andringarText);
    skriv(dataDir, 'meta.json', efter.meta, fore.metaText);
    rapport.skrivet = true;
  }
  rapport.commit = plan.andringar.length
    ? `automat: ${plan.andringar.map(a => `${a.post} ${a.regel === '1a' ? 'beslutad' : a.regel === '1b' ? a.nytt.nr : a.nytt.nr}`).join(', ')}`
    : null;
  return rapport;
}

function parseArgs(argv) {
  const a = { data: path.join(__dirname, '..', '..', 'data'), tillampa: false, idag: new Date().toISOString().slice(0, 10), rapport: null };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--data') a.data = argv[++i];
    else if (argv[i] === '--tillampa') a.tillampa = true;
    else if (argv[i] === '--idag') a.idag = argv[++i];
    else if (argv[i] === '--rapport') a.rapport = argv[++i];
    else throw new Error(`Okänt argument: ${argv[i]}`);
  }
  return a;
}

if (require.main === module) {
  (async () => {
    const a = parseArgs(process.argv.slice(2));
    const rapport = await kor({ dataDir: path.resolve(a.data), fetcher: R.makeHttpFetcher(), tillampaLage: a.tillampa, idag: a.idag });
    const ut = JSON.stringify(rapport, null, 2);
    if (a.rapport) fs.writeFileSync(a.rapport, ut + '\n'); else process.stdout.write(ut + '\n');
    process.stderr.write(`[automat] ${rapport.lage}: ${rapport.andringar.length} ändringar, ${rapport.veckorutin.length} till veckorutinen${rapport.stopp ? `, STOPP: ${rapport.stopp}` : ''}${rapport.skrivet ? ', skrivet' : ''}\n`);
    process.exit(rapport.stopp ? 3 : 0);
  })().catch(err => { process.stderr.write(`[automat] FEL: ${err.stack || err.message}\n`); process.exit(1); });
}

module.exports = { MALL, MARKERING, MAX_ANDRINGAR, fulltBifall, regel1a, regel1b, regel1c, namnUrDirTitel, normNamn, planera, tillampa, vakt, laggTillRad, kor, parseArgs };
