// Testar pilot/utmaningar/index.html i headless Chromium (Playwright). Sprint 16 T4; förväntade tal och testvyer ur datafilen sedan Sprint 17 T7b.
// Kör från repo-roten:  node research/remissanalys/skript/testa-pilotsida.js
// Startar en lokal statisk webbserver för pilot/utmaningar/, laddar sidan i desktop- och 380 px-läge och kontrollerar:
// inga konsolfel/sidfel, banderoll, noindex, kedja, korpus, staplar = avsändarräkningen i datafilen, matris (riktig tabell),
// lista under 700 px, filter + URL-hash, detaljvy med citat (sida + länk), ingen modellskriven fritext, metodruta, tangentbord.
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROT = path.resolve(__dirname, '../../../pilot/utmaningar');
const D = JSON.parse(fs.readFileSync(path.join(ROT, 'data/utmaningar-betyg.json'), 'utf8'));
// Förväntade värden och testvyer härleds ur datafilen (Sprint 17 T7b: sidan ska testas även efter omkodning av betyg).
const K = D.meta.kedja, KORP = D.meta.korpus, HAMTAT = D.meta.hamtningsdatum;
const KEDJA_TEXTER = [K.utredningsbetankande.nr, [].concat(K.proposition)[0].nr, K.utskottsbetankande.bet.split(':').pop(), 'Rskr. ' + K.rskr.nr];
const KAP = Object.fromEntries(D.sakomraden.map(x => [x.rubrik, x.kapitel]));
const flest = (arr, f) => arr.reduce((a, b) => (f(b) > f(a) ? b : a));
const iSak = (u, k) => (u.sakomrade || []).some(x => x.kapitel === k);
const KOMBO = flest(D.avsandarrakning.per_kombination, k => k.antal_avsandare);           // matriscell att kontrollera
const RADSAK = flest(Object.keys(D.avsandarrakning.per_sakomrade), s => D.avsandarrakning.per_sakomrade[s].antal_avsandare);
const SAK_KOMMUN = flest(D.sakomraden.map(x => x.kapitel), k => D.utmaningar.filter(u => iSak(u, k) && u.fokusgrupp === 'kommuner' && !u.koppling.tolkning).length);
const SAK_MEST = flest(D.sakomraden.map(x => x.kapitel), k => D.utmaningar.filter(u => iSak(u, k)).length);
const medProp = u => u.namngivning_i_propositionen !== null;
const PROPVY = (() => { const k = flest(D.sakomraden.map(x => x.kapitel), k => D.utmaningar.filter(u => iSak(u, k) && medProp(u)).length);
  const t = flest(D.utmaningstyper.map(x => x.namn), t => D.utmaningar.filter(u => iSak(u, k) && medProp(u) && u.utmaningstyp.primar === t).length); return { k, t }; })();
const TYP_TOLK = flest(D.utmaningstyper.map(x => x.namn), t => { const uu = D.utmaningar.filter(u => u.utmaningstyp.primar === t);
  return uu.some(u => u.namngivning_i_propositionen && u.namngivning_i_propositionen.namngiven) ? uu.filter(u => u.koppling.niva === 'tolkad').length : -1; });
const TYPER_MED = D.utmaningstyper.map(x => x.namn).filter(t => D.utmaningar.some(u => u.utmaningstyp.primar === t));
const TYP_MINST = flest(TYPER_MED, t => -D.utmaningar.filter(u => u.utmaningstyp.primar === t).length);
const TYP_MEST = flest(TYPER_MED, t => D.utmaningar.filter(u => u.utmaningstyp.primar === t).length);
const TYP_ANDRA = flest(TYPER_MED.filter(t => t !== TYP_MEST), t => D.utmaningar.filter(u => u.utmaningstyp.primar === t).length);
const SAK_FORST = D.sakomraden.map(x => x.kapitel).find(k => D.utmaningar.some(u => iSak(u, k)));
const NOPUBL = KORP.opublicerade_remissvar_som_saknas;
const MIME = { '.html': 'text/html; charset=utf-8', '.json': 'application/json' };
const server = http.createServer((q, r) => {
  let rel = decodeURIComponent(q.url.split('?')[0].split('#')[0]);
  if (rel.endsWith('/')) rel += 'index.html';
  const p = path.join(ROT, rel);
  if (!p.startsWith(ROT) || !fs.existsSync(p)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(r);
});
const resultat = []; let fel = 0;
const ok = (namn, villkor, info = '') => { resultat.push(`${villkor ? 'OK ' : 'FEL'} ${namn}${info ? ' — ' + info : ''}`); if (!villkor) fel++; };

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const URL = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch();
  for (const vy of [{ namn: 'desktop', viewport: { width: 1280, height: 900 } }, { namn: '380px', viewport: { width: 380, height: 800 } }]) {
    const page = await browser.newPage({ viewport: vy.viewport });
    const konsol = [];
    page.on('console', m => { if (m.type() === 'error') konsol.push(m.text()); });
    page.on('pageerror', e => konsol.push(e.message));
    page.on('requestfailed', r => konsol.push('requestfailed ' + r.url()));
    await page.goto(URL); await page.waitForSelector('#staplar button');
    const v = vy.namn;

    ok(`${v}: banderoll`, (await page.textContent('.banderoll')).includes('Pilot under granskning. Kategoriseringar är maskinellt framtagna och inte kvalitetssäkrade.'));
    ok(`${v}: banderoll alltid synlig (sticky)`, await page.$eval('.banderoll', e => getComputedStyle(e).position === 'sticky'));
    ok(`${v}: meta noindex, nofollow`, (await page.getAttribute('meta[name=robots]', 'content')) === 'noindex, nofollow');
    const kedja = await page.$$eval('#kedja a', as => as.map(a => a.textContent + '|' + a.href));
    ok(`${v}: kedja med länkar (SOU, prop, bet, rskr)`, KEDJA_TEXTER.every(s => kedja.some(k => k.includes(s) && k.includes('|https://'))), kedja.length + ' länkar');
    const korpus = await page.textContent('#korpus');
    ok(`${v}: korpus i klartext`, korpus.includes(`${KORP.publicerade_remissvar} publicerade remissvar`) && korpus.includes(`${KORP.avsandare_med_utmaningar} avsändare`) && (!NOPUBL.antal || korpus.includes(`${NOPUBL.antal} opublicerade remissvar saknas`)) && (!(NOPUBL.per_grupp || {}).enskilda_huvudman || korpus.includes(`varav ${NOPUBL.per_grupp.enskilda_huvudman} från enskilda huvudmän`)));

    // Översikt 1 mot datafilens avsändarräkning
    const st = await page.$$eval('#staplar button', bs => bs.map(b => [b.dataset.typ, b.querySelector('.tal').textContent]));
    const forv = D.utmaningstyper.map(t => [t.namn, `${D.avsandarrakning.per_utmaningstyp[t.namn].antal_avsandare} av ${D.avsandarrakning.totalt.antal_avsandare}`]);
    ok(`${v}: översikt 1 = avsändarräkningen i datafilen`, JSON.stringify(st) === JSON.stringify(forv), st.map(x => x.join(': ')).join('; '));

    if (v === 'desktop') {
      ok(`${v}: matris är <table> med th scope (${D.utmaningstyper.length + 2} kolumnrubriker, ${D.sakomraden.length + 1} rader)`,
        await page.$eval('#matris', (t, [nc, nr]) => t.tagName === 'TABLE' && t.querySelectorAll('th[scope=col]').length === nc && t.querySelectorAll('th[scope=row]').length === nr, [D.utmaningstyper.length + 2, D.sakomraden.length + 1]));
      ok(`${v}: matrisen synlig, listan dold`, (await page.isVisible('#matris')) && !(await page.isVisible('#matrislista')));
      const kombo = KOMBO;
      const cell = await page.$eval(`#matris button[data-sak="${KAP[KOMBO.sakomrade]}"][data-typ="${KOMBO.utmaningstyp}"]`, b => b.textContent);
      ok(`${v}: matriscell kap ${KAP[KOMBO.sakomrade]} × ${KOMBO.utmaningstyp} = datafilen`, String(kombo.antal_avsandare) === cell, `${cell} / ${kombo.antal_avsandare}`);
      const rad = D.avsandarrakning.per_sakomrade[RADSAK].antal_avsandare;
      const radcell = await page.$eval(`#matris tr:has(th button[data-sak="${KAP[RADSAK]}"]) td:last-child button`, b => b.textContent);
      ok(`${v}: radsumma kap ${KAP[RADSAK]} (alla typer) = datafilen`, String(rad) === radcell, `${radcell} / ${rad}`);
    } else {
      ok(`${v}: lista ersätter matrisen under 700 px`, !(await page.isVisible('#matris')) && (await page.isVisible('#matrislista')));
      ok(`${v}: ingen horisontell sidrullning vid 380 px`, await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), await page.evaluate(() => document.documentElement.scrollWidth + ' px'));
    }

    await page.click('#staplar button[data-typ="Kostnader och finansiering"]');
    ok(`${v}: stapelklick filtrerar och skrivs i URL-hash`, (await page.evaluate(() => decodeURIComponent(location.hash))).includes('typ=Kostnader och finansiering'));
    ok(`${v}: stapelklick visar detaljvy`, /Utmaningstyp: Kostnader och finansiering/.test(await page.textContent('#detaljrubrik')));

    await page.goto(URL + `#sak=${SAK_KOMMUN}&fg=kommuner&tolk=0`); await page.waitForSelector('#skrev .citat');
    ok(`${v}: URL-hash återställer filter`, (await page.$eval('#tolk', i => !i.checked)) && (await page.$eval('input[name=fg][value=kommuner]', i => i.checked)));
    ok(`${v}: inga tolkade kopplingar när reglaget är av`, (await page.$$('#skrev .etikett.tolkad')).length === 0);

    // varje citat (i flera vyer) har sida och länk
    let antal = 0, utan = 0;
    for (const h of [`#sak=${SAK_MEST}`, '#sak=utan', `#typ=${TYP_MEST}`, `#typ=${TYP_MINST}`]) {
      await page.goto(URL + h); await page.waitForSelector('#skrev .citat');
      antal += await page.$$eval('#skrev .citat', c => c.length);
      utan += await page.$$eval('#skrev .citat', cs => cs.filter(c => !c.querySelector('a[href*="#page="]') || !/s\. \d+/.test(c.textContent)).length);
    }
    ok(`${v}: varje visat citat har sida och länk`, utan === 0, `${antal} citat kontrollerade`);
    ok(`${v}: tolkad koppling markeras när reglaget är på`, (await (async () => { await page.goto(URL + `#typ=${TYP_TOLK}`); await page.waitForSelector('#skrev .citat'); return (await page.$$('#skrev .etikett.tolkad')).length; })()) > 0);
    ok(`${v}: "avsändaren nämns" med utfällbar mening`, (await page.$$('#skrev .etikett.namn')).length > 0 && (await page.$$('#skrev details')).length > 0);

    await page.goto(URL + `#sak=${PROPVY.k}&typ=${PROPVY.t}`); await page.waitForSelector('#sager .prop');
    const sager = await page.textContent('#sager');
    ok(`${v}: proposition och lag (överensstämmelse, Reformkartans koppling, SFS-status)`,
      /Utredningens förslag stämmer/.test(sager) && /Reformkartans koppling/.test(sager) && new RegExp(`(i beslutad lag|ej i SFS per ${HAMTAT}|ej lagtext)`).test(sager));
    ok(`${v}: avvikelsetext och lagtext utfällbara`, (await page.$$('#sager details')).length >= 2);

    await page.goto(URL + '#sak=utan'); await page.waitForSelector('#skrev .citat');
    ok(`${v}: "Utan koppling" visas`, /Utan koppling till sakområde/.test(await page.textContent('#detaljrubrik')));
    const jmf = await page.textContent('#jamforelse');
    const med = D.utmaningar.filter(u => u.namngivning_i_propositionen !== null).length;
    ok(`${v}: antal med/utan jämförelse mot propositionen (${med}/${D.utmaningar.length - med})`,
      jmf.includes(`${med} av dem hör till ett propositionsavsnitt`) && jmf.includes(`${D.utmaningar.length - med} saknar`), jmf);

    // Ingen modellskriven fritext ur datafilen
    let traffar = [];
    const mot = [...new Set(D.utmaningar.flatMap(u => [u.utmaningstyp.motivering, u.koppling.motivering]).filter(m => m && m.length > 12 && !D.utmaningar.some(u => u.citat.includes(m))))];   // motivering som är ordagrann del av ett citat är källtext, inte fritext
    const meta = [D.meta.tolkning, D.meta.ingen_bedomning, D.meta.korpus.beskrivning, ...Object.values(D.meta.kopplingsnivaer)];
    for (const h of [`#typ=${TYP_ANDRA}`, `#typ=${TYP_MEST}`, `#sak=${SAK_FORST}`, '#sak=utan']) {
      await page.goto(URL + h); await page.waitForSelector('#skrev .citat');
      const body = await page.textContent('body');
      traffar = traffar.concat([...mot, ...meta].filter(m => body.includes(m)));
    }
    ok(`${v}: ingen modellskriven fritext (motiveringar, meta-texter) visas`, traffar.length === 0, traffar.slice(0, 2).join(' | '));

    // Samtliga 440 utmaningar nås: unionen av citat-id över alla sakområden och "Utan koppling", utan filter.
    const nadda = new Set(); let besok = 0;
    for (const sak of [...D.sakomraden.map(x => x.kapitel), 'utan']) {
      await page.goto(URL + '?v=' + (besok++) + '#sak=' + sak); await page.waitForSelector('#detaljrubrik');
      await page.waitForFunction(() => /utmaningar från/.test(document.getElementById('detaljrubrik').textContent) || /Inga utmaningar/.test(document.getElementById('skrev').textContent));
      (await page.$$eval('#skrev .citat', cs => cs.map(c => c.dataset.id))).forEach(i => nadda.add(i));
    }
    const saknas = D.utmaningar.map(u => u.id).filter(i => !nadda.has(i));
    ok(`${v}: samtliga ${D.utmaningar.length} utmaningar nås via sakområden + "Utan koppling"`, nadda.size === D.utmaningar.length && saknas.length === 0, `${nadda.size} unika id${saknas.length ? '; saknas: ' + saknas.slice(0, 10).join(', ') : ''}`);

    const metod = await page.textContent('#metod');
    ok(`${v}: metodruta`, /Tolkning/.test(metod) && /Saknade remissvar/.test(metod) && metod.includes(HAMTAT) && /inte att synpunkten har bemötts/.test(metod) && /bedömer inte om utmaningarna är lösta/.test(metod));

    await page.goto(URL); await page.waitForSelector('#staplar button');
    await page.focus('#staplar button[data-typ="System och teknik"]'); await page.keyboard.press('Enter');
    ok(`${v}: tangentbord (Enter på stapel)`, (await page.evaluate(() => decodeURIComponent(location.hash))).includes('typ=System och teknik'));
    ok(`${v}: inga länkar till andra sidor på sajten`, (await page.$$eval('a', as => as.filter(a => new URL(a.href).host === location.host && !a.href.includes('#')).length)) === 0);
    ok(`${v}: inga konsolfel`, konsol.length === 0, konsol.join(' | '));
    if (process.env.SKARMBILD) await page.screenshot({ path: path.join(process.env.SKARMBILD, 'pilot-' + v + '.png'), fullPage: false });
    await page.close();
  }
  await browser.close(); server.close();
  console.log(resultat.join('\n'));
  console.log(fel ? `\n${fel} FEL av ${resultat.length}` : `\nALLA ${resultat.length} KONTROLLER OK`);
  process.exit(fel ? 1 : 0);
})().catch(e => { console.error(e); server.close(); process.exit(1); });
