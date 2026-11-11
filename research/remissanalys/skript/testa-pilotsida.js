// Testar pilot/utmaningar/index.html i headless Chromium (Playwright). Sprint 16 T4; sju reformer sedan Sprint 17 del B.
// Kör från repo-roten:  node research/remissanalys/skript/testa-pilotsida.js
// Valfritt: SKARMBILD=<katalog> sparar startvyn i 1280 px och en reformvy i 375 px som PNG (deviceScaleFactor 1).
//
// Startar en lokal statisk webbserver för pilot/utmaningar/ och kontrollerar i 1280 px och 375 px:
// inga konsolfel/sidfel, banderoll, noindex, inga länkar till andra sidor på sajten, startvyns jämförelsetabell
// (= avsändarräkningen i varje datafil och oversikt.json), och för var och en av de sju reformerna: kedja, korpus,
// staplar, matris/lista, organisationer (B5), förslag som propositionen inte tar upp (B4), att samtliga utmaningar nås,
// citat med sida och länk, proposition och lag, metodruta, ingen modellskriven fritext, 44 px klickytor, ingen
// horisontell sidrullning vid 375 px och tangentbord. Alla förväntade värden härleds ur datafilerna.
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROT = path.resolve(__dirname, '../../../pilot/utmaningar');
const las = f => JSON.parse(fs.readFileSync(path.join(ROT, 'data', f), 'utf8'));
const OV = las('oversikt.json');
const IDS = ['betyg', 'studiero', 'stod', 'tid', 'laroplaner', 'spraklig', 'tioarig'];   // fast ordning enligt specifikationen
const DATA = Object.fromEntries(IDS.map(id => [id, las(`utmaningar-${id}.json`)]));
const TYPER = DATA[IDS[0]].utmaningstyper.map(t => t.namn);

const flest = (arr, f) => arr.reduce((a, b) => (f(b) > f(a) ? b : a));
const iSak = (u, k) => (u.sakomrade || []).some(x => x.kapitel === k);
const forslagsniva = n => n === 'förslag' || n === 'avsnitt' || n === 'tolkad';
const medProp = u => forslagsniva(u.koppling.niva) && u.namngivning_i_propositionen !== null;
const tal = (x, y) => `${x} av ${y}`;
const enc = (par) => '#' + par.map(([k, v]) => k + '=' + encodeURIComponent(v)).join('&');

// Förväntade värden per reform, härledda ur datafilen.
function forvantat(id) {
  const D = DATA[id], R = D.avsandarrakning, K = D.meta.kedja;
  const KAP = Object.fromEntries(D.sakomraden.map(x => [x.rubrik, x.kapitel]));
  const typerMed = TYPER.filter(t => D.utmaningar.some(u => u.utmaningstyp.primar === t));
  const antalTyp = t => D.utmaningar.filter(u => u.utmaningstyp.primar === t).length;
  const ingenF = D.utredningsforslag.filter(f => f.propositionsavsnitt && f.propositionsavsnitt.matchning === 'ingen');
  const ingenSet = new Set(ingenF.map(f => f.id));
  const ingenU = D.utmaningar.filter(u => forslagsniva(u.koppling.niva) && u.koppling.forslag.some(f => ingenSet.has(f)));
  const sakMedProp = D.sakomraden.map(x => x.kapitel).filter(k => D.utmaningar.some(u => iSak(u, k) && medProp(u)));
  let propvy = null;
  if (sakMedProp.length) {
    const k = flest(sakMedProp, k => D.utmaningar.filter(u => iSak(u, k) && medProp(u)).length);
    const t = flest(typerMed, t => D.utmaningar.filter(u => iSak(u, k) && medProp(u) && u.utmaningstyp.primar === t).length);
    propvy = { k, t };
  }
  // Modellskriven fritext och meta-beskrivningar som aldrig får visas. En motivering som är ordagrann del av ett citat är källtext.
  const citat = D.utmaningar.map(u => u.citat);
  const motiveringar = [...new Set(D.utmaningar.flatMap(u => [u.utmaningstyp.motivering, u.koppling.motivering]))]
    .filter(m => m && m.length > 12 && !citat.some(c => c.includes(m)));
  const m = D.meta;
  const metaTexter = [m.tolkning, m.ingen_bedomning, m.korpus.beskrivning, ...Object.values(m.kopplingsnivaer || {}),
    m.remissida_kontroll && m.remissida_kontroll.regel, ...(m.organisationer || []).map(o => o.anm),
    ...(m.publicerade_avstaenden || []).map(a => a.anm), ...[].concat(K.proposition).map(p => p.anm),
    ...((m.korpus.opublicerade_remissvar_som_saknas || {}).avsandare || []).map(a => a.skal),
    ...D.utredningsforslag.map(f => f.sfs && f.sfs.forklaring), ...D.utredningsforslag.map(f => f.propositionsavsnitt && f.propositionsavsnitt.grund),
    R.princip].filter(x => typeof x === 'string' && x.length > 12);
  return {
    D, R, K, KAP,
    kedjaTexter: [K.utredningsbetankande.nr, ...[].concat(K.proposition).map(p => p.nr), K.utskottsbetankande.bet.split(':').pop(), 'Rskr. ' + K.rskr.nr],
    kombo: flest(R.per_kombination, k => k.antal_avsandare),
    radsak: flest(Object.keys(R.per_sakomrade), s => R.per_sakomrade[s].antal_avsandare),
    sakKommun: flest(D.sakomraden.map(x => x.kapitel), k => D.utmaningar.filter(u => iSak(u, k) && u.fokusgrupp === 'kommuner' && u.koppling.niva !== 'tolkad').length),
    typMest: flest(typerMed, antalTyp),
    typMinst: flest(typerMed, t => -antalTyp(t)),
    sakForst: D.sakomraden.map(x => x.kapitel).find(k => D.utmaningar.some(u => iSak(u, k))),
    ingenF, ingenU, propvy, motiveringar, metaTexter,
    med: D.utmaningar.filter(medProp).length,
  };
}

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

// Konsistens oversikt.json ↔ datafilerna (oberoende av webbläsaren).
ok('oversikt.json: sju reformer i fast ordning', JSON.stringify(OV.reformer.map(r => r.id)) === JSON.stringify(IDS));
ok('oversikt.json: utmaningstyper = datafilernas', JSON.stringify(OV.utmaningstyper) === JSON.stringify(TYPER));
ok('oversikt.json: tal = avsändarräkningen i varje datafil', OV.reformer.every(r => { const D = DATA[r.id];
  return r.namn === D.meta.reform.namn && r.sou === D.meta.kedja.utredningsbetankande.nr && r.totalt_avsandare === D.avsandarrakning.totalt.antal_avsandare
    && r.utmaningar === D.utmaningar.length && TYPER.every(t => r.per_utmaningstyp[t] === D.avsandarrakning.per_utmaningstyp[t].antal_avsandare); }));

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const URL = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch();
  const FV = Object.fromEntries(IDS.map(id => [id, forvantat(id)]));

  for (const vy of [{ namn: '1280px', viewport: { width: 1280, height: 900 }, smal: false }, { namn: '375px', viewport: { width: 375, height: 800 }, smal: true }]) {
    const page = await browser.newPage({ viewport: vy.viewport, deviceScaleFactor: 1 });
    const konsol = [];
    page.on('console', m => { if (m.type() === 'error') konsol.push(m.text()); });
    page.on('pageerror', e => konsol.push(e.message));
    page.on('requestfailed', r => konsol.push('requestfailed ' + r.url()));
    const v = vy.namn;
    // Navigerar via hash och väntar tills sidan markerat vyn som färdigritad (<html data-klar="<hash>">).
    const nav = async h => {
      await page.evaluate(h => { location.hash = h; }, h);
      await page.waitForFunction(() => document.documentElement.dataset.klar === location.hash);
    };
    const vantaKlar = () => page.waitForFunction(() => document.documentElement.dataset.klar === location.hash);
    const hash = () => page.evaluate(() => decodeURIComponent(location.hash));
    // Alla klickbara element (länkar, knappar, väljare, summary, etiketter runt kryssrutor) som syns ska vara minst 44×44 px.
    const for44 = () => page.evaluate(() => {
      document.querySelectorAll('details').forEach(d => d.open = true);
      const els = [...document.querySelectorAll('a[href], button, select, summary, label:has(input)')];
      const sma = [];
      let n = 0;
      for (const e of els) {
        const r = e.getBoundingClientRect();
        if (!r.width || !r.height || getComputedStyle(e).visibility === 'hidden') continue;   // dolt (t.ex. tabellen under 700 px)
        n++;
        if (r.width < 43.5 || r.height < 43.5) sma.push(`${e.tagName.toLowerCase()} "${e.textContent.trim().slice(0, 30)}" ${Math.round(r.width)}×${Math.round(r.height)}`);
      }
      return { n, sma };
    });
    const ingenScroll = () => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);
    const sammaSajt = () => page.$$eval('a', as => as.filter(a => new URL(a.href).host === location.host && !a.href.includes('#')).length);

    // ---------- startvy ----------
    await page.goto(URL); await vantaKlar();
    ok(`${v}: banderoll`, (await page.textContent('.banderoll')).includes('Pilot under granskning. Kategoriseringar är maskinellt framtagna och inte kvalitetssäkrade.'));
    ok(`${v}: banderoll alltid synlig (sticky)`, await page.$eval('.banderoll', e => getComputedStyle(e).position === 'sticky'));
    ok(`${v}: meta noindex, nofollow`, (await page.getAttribute('meta[name=robots]', 'content')) === 'noindex, nofollow');
    ok(`${v}: startvy visas utan reform i hash`, (await page.isVisible('#startvy')) && !(await page.isVisible('#reformvy')));
    const valjare = await page.$$eval('#reformval option', os => os.map(o => o.value).filter(Boolean));
    ok(`${v}: reformväljare med alla sju`, JSON.stringify(valjare) === JSON.stringify(IDS), valjare.join(','));
    const forvCeller = IDS.flatMap(id => TYPER.map(t => [id, t, tal(DATA[id].avsandarrakning.per_utmaningstyp[t].antal_avsandare, DATA[id].avsandarrakning.totalt.antal_avsandare)]));
    if (!vy.smal) {
      ok(`${v}: jämförelsetabell är <table> med th scope (${TYPER.length + 1} kolumnrubriker, ${IDS.length} rader)`,
        await page.$eval('#jmftabell', (t, [nc, nr]) => t.tagName === 'TABLE' && t.querySelectorAll('th[scope=col]').length === nc && t.querySelectorAll('th[scope=row]').length === nr, [TYPER.length + 1, IDS.length]));
      ok(`${v}: tabellen synlig, listan dold`, (await page.isVisible('#jmftabell')) && !(await page.isVisible('#jmflista')));
      const celler = await page.$$eval('#jmftabell td a', as => as.map(a => [a.dataset.reform, a.dataset.typ, a.textContent.trim()]));
      ok(`${v}: jämförelsetabellens celler = avsändarräkningen ("x av y")`, JSON.stringify(celler) === JSON.stringify(forvCeller), `${celler.length} celler`);
      const farg = await page.$$eval('#jmftabell td', tds => tds.map(td => td.style.background));
      ok(`${v}: celler med färgintensitet (andel) och alltid text`, farg.some(f => f.includes('rgba')) && celler.every(c => /^\d+ av \d+$/.test(c[2])));
    } else {
      ok(`${v}: lista per reform ersätter tabellen under 700 px`, !(await page.isVisible('#jmftabell')) && (await page.isVisible('#jmflista')));
      const celler = await page.$$eval('#jmflista ul a', as => as.map(a => [a.dataset.reform, a.dataset.typ, a.querySelector('strong').textContent.trim()]));
      ok(`${v}: listans tal = avsändarräkningen ("x av y")`, JSON.stringify(celler) === JSON.stringify(forvCeller), `${celler.length} rader`);
    }
    const s44 = await for44();
    ok(`${v}: startvy, klickytor minst 44×44 px`, s44.sma.length === 0, `${s44.n} element${s44.sma.length ? '; för små: ' + s44.sma.slice(0, 5).join(' | ') : ''}`);
    if (vy.smal) ok(`${v}: startvy, ingen horisontell sidrullning`, await ingenScroll(), await page.evaluate(() => document.documentElement.scrollWidth + ' px'));
    ok(`${v}: startvy, inga länkar till andra sidor på sajten`, (await sammaSajt()) === 0);
    if (process.env.SKARMBILD && !vy.smal) await page.screenshot({ path: path.join(process.env.SKARMBILD, 'start-1280.png'), fullPage: false });
    // Klick på en cell öppnar reformen filtrerad på typen (cellen med störst andel).
    const [cr, ct] = flest(forvCeller, c => DATA[c[0]].avsandarrakning.per_utmaningstyp[c[1]].antal_avsandare / DATA[c[0]].avsandarrakning.totalt.antal_avsandare);
    await page.click(`${vy.smal ? '#jmflista ul' : '#jmftabell td'} a[data-reform="${cr}"][data-typ="${ct}"]`); await vantaKlar();
    ok(`${v}: cellklick öppnar ${cr} filtrerad på "${ct}"`, (await hash()).includes(`reform=${cr}`) && (await hash()).includes(`typ=${ct}`) && (await page.isVisible('#reformvy'))
      && (await page.textContent('#detaljrubrik')).includes('Utmaningstyp: ' + ct));
    await page.selectOption('#reformval', ''); await vantaKlar();
    ok(`${v}: väljaren tillbaka till jämförelsen`, await page.isVisible('#startvy'));

    // ---------- varje reform ----------
    for (const id of IDS) {
      const F = FV[id], D = F.D, m = D.meta, KORP = m.korpus, NOPUBL = KORP.opublicerade_remissvar_som_saknas || { antal: 0, per_grupp: {}, avsandare: [] };
      const p = `${v} ${id}`;
      await page.selectOption('#reformval', id); await vantaKlar();
      ok(`${p}: väljaren öppnar reformen (hash reform=${id})`, (await hash()) === '#reform=' + id && (await page.textContent('#reformnamn')) === m.reform.namn);

      const kedja = await page.$$eval('#kedja a', as => as.map(a => a.textContent + '|' + a.href));
      ok(`${p}: kedja med länkar (SOU, prop, bet, rskr)`, F.kedjaTexter.every(s => kedja.some(k => k.includes(s) && k.includes('|https://'))), kedja.length + ' länkar');
      const korpus = await page.textContent('#korpus');
      ok(`${p}: korpus i klartext`, korpus.includes(`${KORP.publicerade_remissvar} publicerade remissvar`) && korpus.includes(`${D.avsandare.length} avsändare`)
        && (NOPUBL.antal ? korpus.includes(`${NOPUBL.antal} opublicerade remissvar saknas`) && Object.values(NOPUBL.per_grupp).every(n => korpus.includes(`${n} från`)) : korpus.includes('Inga opublicerade')), korpus.slice(0, 160));

      const st = await page.$$eval('#staplar button', bs => bs.map(b => [b.dataset.typ, b.querySelector('.tal').textContent]));
      const forv = TYPER.map(t => [t, tal(F.R.per_utmaningstyp[t].antal_avsandare, F.R.totalt.antal_avsandare)]);
      ok(`${p}: staplar = avsändarräkningen`, JSON.stringify(st) === JSON.stringify(forv), st.map(x => x[1]).join('; '));

      if (!vy.smal) {
        ok(`${p}: matris är <table> med th scope (${TYPER.length + 2} kolumnrubriker, ${D.sakomraden.length + 1} rader)`,
          await page.$eval('#matris', (t, [nc, nr]) => t.tagName === 'TABLE' && t.querySelectorAll('th[scope=col]').length === nc && t.querySelectorAll('th[scope=row]').length === nr, [TYPER.length + 2, D.sakomraden.length + 1]));
        const cell = await page.$eval(`#matris button[data-sak="${F.KAP[F.kombo.sakomrade]}"][data-typ="${F.kombo.utmaningstyp}"]`, b => b.textContent);
        ok(`${p}: matriscell kap ${F.KAP[F.kombo.sakomrade]} × ${F.kombo.utmaningstyp} = datafilen`, String(F.kombo.antal_avsandare) === cell, `${cell} / ${F.kombo.antal_avsandare}`);
        const rad = F.R.per_sakomrade[F.radsak].antal_avsandare;
        const radcell = await page.$eval(`#matris tr:has(th button[data-sak="${F.KAP[F.radsak]}"]) td:last-child button`, b => b.textContent);
        ok(`${p}: radsumma kap ${F.KAP[F.radsak]} = datafilen`, String(rad) === radcell, `${radcell} / ${rad}`);
      } else {
        ok(`${p}: lista ersätter matrisen under 700 px`, !(await page.isVisible('#matris')) && (await page.isVisible('#matrislista')));
      }
      const jmf = await page.textContent('#jamforelse');
      ok(`${p}: antal med/utan jämförelse mot propositionen (${F.med}/${D.utmaningar.length - F.med})`, jmf.includes(`${F.med} av dem hör till ett propositionsavsnitt`) && jmf.includes(`${D.utmaningar.length - F.med} saknar`));

      // B5: exakt organisationerna i meta.organisationer, med status, källa och (för avstått) ordagrant citat.
      const org = await page.$$eval('#org li[data-org]', lis => lis.map(li => ({ id: li.dataset.org, text: li.textContent, hrefs: [...li.querySelectorAll('a')].map(a => a.href) })));
      const forvOrg = m.organisationer || [];
      ok(`${p}: organisationer = meta.organisationer (${forvOrg.map(o => o.id).join(', ')})`, JSON.stringify(org.map(o => o.id)) === JSON.stringify(forvOrg.map(o => o.id))
        && forvOrg.every((o, i) => org[i].text.includes(o.namn) && org[i].text.includes(o.status) && org[i].hrefs.includes(o.kalla.url)
          && (o.status !== 'avstått' || (org[i].text.includes(o.avstaende.citat) && org[i].hrefs.includes(o.avstaende.kalla.url)))), org.map(o => o.id).join(', '));

      // B4: förslag som propositionen inte tar upp.
      const ig = await page.$eval('#ingen .ingen-tal', e => [+e.dataset.forslag, +e.dataset.utmaningar, e.textContent]);
      const igText = await page.textContent('#ingen');
      ok(`${p}: B4-gruppens antal = data (${F.ingenF.length} förslag, ${F.ingenU.length} utmaningar)`, ig[0] === F.ingenF.length && ig[1] === F.ingenU.length
        && ig[2].includes(String(F.ingenU.length)) && ig[2].includes(String(F.ingenF.length)) && igText.includes('Att propositionen inte tar upp ett förslag betyder inte att förslaget har fallit.'));
      if (F.ingenF.length) {
        const fl = await page.$$eval('#ingen li[data-forslag]', lis => lis.map(li => ({ id: li.dataset.forslag, text: li.textContent, href: li.querySelector('a').href })));
        ok(`${p}: B4 listar förslagen ordagrant med SOU-avsnitt och källa`, fl.length === F.ingenF.length && F.ingenF.every((f, i) => fl[i].id === f.id && fl[i].text.includes(f.text) && fl[i].text.includes('avsnitt ' + f.sou_avsnitt) && fl[i].href.startsWith(f.kalla.url)));
        await page.click('#ingenknapp');
        await page.waitForFunction(() => location.hash.includes('forslag=ingen') && document.documentElement.dataset.klar === location.hash);
        const ids = await page.$$eval('#skrev .citat', cs => cs.map(c => c.dataset.id));
        const forvIds = F.ingenU.map(u => u.id);
        ok(`${p}: klick i B4 visar just de ${forvIds.length} utmaningarna`, ids.length === forvIds.length && forvIds.every(i => ids.includes(i)), `${ids.length} visade`);
      }

      // Filter i hash fungerar inom reformen.
      await nav(enc([['reform', id], ['sak', F.sakKommun], ['fg', 'kommuner'], ['tolk', '0']]));
      ok(`${p}: URL-hash återställer filter`, (await page.$eval('#tolk', i => !i.checked)) && (await page.$eval('input[name=fg][value=kommuner]', i => i.checked)) && (await page.$$('#skrev .etikett.tolkad')).length === 0);

      // Varje citat har sida och länk (vyerna med flest och minst utmaningar).
      let antal = 0, utan = 0;
      for (const h of [enc([['reform', id], ['typ', F.typMest]]), enc([['reform', id], ['typ', F.typMinst]])]) {
        await nav(h);
        antal += await page.$$eval('#skrev .citat', c => c.length);
        utan += await page.$$eval('#skrev .citat', cs => cs.filter(c => !c.querySelector('a[href*="#page="]') || !/s\. \d+/.test(c.textContent)).length);
      }
      ok(`${p}: varje visat citat har sida och länk`, antal > 0 && utan === 0, `${antal} citat kontrollerade`);

      // 44 px och horisontell rullning i en tung vy (flest utmaningar, alla utfällbara delar öppna).
      await nav(enc([['reform', id], ['typ', F.typMest]]));
      const r44 = await for44();
      ok(`${p}: klickytor minst 44×44 px`, r44.sma.length === 0, `${r44.n} element${r44.sma.length ? '; för små: ' + r44.sma.slice(0, 5).join(' | ') : ''}`);
      if (vy.smal) ok(`${p}: ingen horisontell sidrullning`, await ingenScroll(), await page.evaluate(() => document.documentElement.scrollWidth + ' px'));

      // Proposition och lag.
      if (F.propvy) {
        await nav(enc([['reform', id], ['sak', F.propvy.k], ['typ', F.propvy.t]]));
        const sager = await page.textContent('#sager');
        const oe = D.propositionsavsnitt.map(x => x.overensstammelse).filter(Boolean);
        ok(`${p}: proposition och lag (överensstämmelse, Reformkartans koppling, SFS-status)`, oe.some(x => sager.includes(x)) && /Reformkartans koppling/.test(sager)
          && /(i beslutad lag|ej i SFS per|ej lagtext|SFS-status saknas)/.test(sager) && (await page.$$('#sager details')).length >= 1);
      } else ok(`${p}: proposition och lag — inga utmaningar med propositionsavsnitt i data`, true);

      // Ingen modellskriven fritext i några vyer.
      let traffar = [];
      for (const h of [enc([['reform', id], ['typ', F.typMest]]), enc([['reform', id], ['sak', F.sakForst]]), enc([['reform', id], ['sak', 'utan']]), enc([['reform', id], ['forslag', 'ingen']])]) {
        await nav(h);
        const body = await page.evaluate(() => { document.querySelectorAll('details').forEach(d => d.open = true); return document.body.textContent; });
        traffar = traffar.concat([...F.motiveringar, ...F.metaTexter].filter(x => body.includes(x)));
      }
      ok(`${p}: ingen modellskriven fritext (motiveringar, meta-texter) visas`, traffar.length === 0, `${F.motiveringar.length + F.metaTexter.length} texter kontrollerade${traffar.length ? '; träff: ' + traffar.slice(0, 2).join(' | ') : ''}`);

      // Samtliga utmaningar nås: unionen av citat-id över alla sakområden och "Utan koppling", utan filter.
      const nadda = new Set();
      for (const sak of [...D.sakomraden.map(x => x.kapitel), 'utan']) {
        await nav(enc([['reform', id], ['sak', sak]]));
        (await page.$$eval('#skrev .citat', cs => cs.map(c => c.dataset.id))).forEach(i => nadda.add(i));
      }
      const saknas = D.utmaningar.map(u => u.id).filter(i => !nadda.has(i));
      ok(`${p}: samtliga ${D.utmaningar.length} utmaningar nås via sakområden + "Utan koppling"`, nadda.size === D.utmaningar.length && saknas.length === 0, `${nadda.size} unika id${saknas.length ? '; saknas: ' + saknas.slice(0, 10).join(', ') : ''}`);

      // Metodruta.
      const metod = await page.textContent('#metod');
      const k = m.kodning;
      const samTal = [k.samstammighet_identifiering, k.samstammighet_typning, k.samstammighet_typning_efter_regelprovning].filter(Boolean).map(x => tal(x.overens, x.antal));
      ok(`${p}: metodruta (hämtningsdatum, samstämmighet ${samTal.join(', ')}, korpus, opublicerade)`, metod.includes(m.hamtningsdatum) && samTal.every(s => metod.includes(s))
        && metod.includes(`${KORP.publicerade_remissvar} publicerade remissvar, ${KORP.avsandare_med_utmaningar} avsändare med utmaningar, ${KORP.utmaningar} utmaningar`)
        && (NOPUBL.avsandare || []).every(a => metod.includes(a.avsandare)) && /inte att synpunkten har bemötts/.test(metod) && /bedömer inte om utmaningarna är lösta/.test(metod)
        && (k.samstammighet_identifiering || /inte mätt/.test(metod)));
      const koder = await page.$$eval('#begransningar li', lis => lis.map(li => [li.dataset.kod, li.textContent]));
      ok(`${p}: begränsningar som fasta texter (${(m.begransningar || []).map(b => b.kod).join(', ')})`, JSON.stringify(koder.map(x => x[0])) === JSON.stringify((m.begransningar || []).map(b => b.kod))
        && (m.begransningar || []).every((b, i) => Object.entries(b).filter(([n]) => n !== 'kod').every(([, val]) => [].concat(val).every(x => koder[i][1].includes(String(x))))));

      // Tangentbord: Enter på en stapel filtrerar.
      await nav('#reform=' + id);
      await page.focus(`#staplar button[data-typ="${F.typMinst}"]`); await page.keyboard.press('Enter');
      await vantaKlar();
      ok(`${p}: tangentbord (Enter på stapel)`, (await hash()).includes('typ=' + F.typMinst));
      ok(`${p}: inga länkar till andra sidor på sajten`, (await sammaSajt()) === 0);
      if (process.env.SKARMBILD && vy.smal && id === 'tid') {
        await nav('#reform=' + id); await page.evaluate(() => { document.querySelectorAll('details').forEach(d => d.open = false); window.scrollTo(0, 0); });
        await page.screenshot({ path: path.join(process.env.SKARMBILD, 'reform-tid-375.png'), fullPage: false });
        await page.screenshot({ path: path.join(process.env.SKARMBILD, 'reform-tid-375-hel.png'), fullPage: true });
      }
    }
    ok(`${v}: inga konsolfel eller sidfel`, konsol.length === 0, konsol.slice(0, 5).join(' | '));
    await page.close();
  }
  await browser.close(); server.close();
  console.log(resultat.join('\n'));
  console.log(fel ? `\n${fel} FEL av ${resultat.length}` : `\nALLA ${resultat.length} KONTROLLER OK`);
  process.exit(fel ? 1 : 0);
})().catch(e => { console.error(e); server.close(); process.exit(1); });
