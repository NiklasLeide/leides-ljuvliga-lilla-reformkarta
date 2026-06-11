# Project Status — leides-ljuvliga-lilla-reformkarta

> **Last updated:** 2026-06-10
> **Current sprint:** Sprint 10 — Bevakningsautomatisering
> **Sprint dates:** juni 2026

---

## Sprint 10 — Bevakningsautomatisering

**Mål:** Detektering av dataändringar flyttas till en schemalagd GitHub Action som
producerar en veckorapport som GitHub Issue. Människan verifierar, maskinen bevakar.
Noll automatiska skrivningar till datafiler.

**Designbeslut:**
- Runtime-manifest — ingen committad bevakningsfil; manifestet beräknas vid varje körning
- Stateless diff mot datafilerna (inga state-filer mellan körningar)
- Zero-dependency Node (inga npm-paket, node:test för tester)
- Tom vecka = ingen issue skapas
- Cron måndagar 06:00 UTC + workflow_dispatch för manuell körning

**Out of scope:** automatisk skrivning till datafiler; HTML-scraping av regeringen.se;
bevakning av val26; notifiering utanför GitHub; AI-anrop.

**Stop condition:** Action körs på schema och manuellt; korrekt rapport mot känt
testfall; tom vecka ger ingen issue; workflow-permissions contents:read +
issues:write; BEVAKNING.md följbar utan chatkontext; DoD passerad.

| ID | Task | Filer | Status | Acceptance |
|----|------|-------|--------|------------|
| T1 | Sprintregistrering + identifierar-extraktion | PROJECT_STATUS.md, scripts/bevakning/extract.js | ✅ Done | Plan i PROJECT_STATUS; komplett manifest (12 props, 21 SOU, 49 dir, 27 utredningar), inga hårdkodade id:n, 8 tester med facit passerar |
| T1-fix | commit.sh stagear scripts/ och .github/ | commit.sh | ✅ Done | Loop över stage-listan; verifierad med dry-run |
| T2 | Riksdagen-watcher: status-diff API vs datafiler | scripts/bevakning/riksdagen.js | ✅ Done | 8 tester med mockad fetcher (omarbetade i T2-fix). |
| T2-fix | Live-verifiering + API-fältkorrigeringar | riksdagen.js, riksdagen.test.js, fixtures/ | ✅ Done | Live-verifiering avslöjade 3 buggar som mockarna dolde: (1) relaterade i fel fält (dokuppgift→dokreferens.behandlas_i), (2) jobb B matchade fullt dept-namn som inte finns för dir → organ-kortkod "U-dep", (3) dir-beteckning byggd fel → `Dir. <rm>:<nummer>`. Jobb C-regex \d{2}→\d{2,3}. Testerna drivs nu av fångade riktiga API-svar (scripts/bevakning/fixtures/). 20/20 gröna. Skarp körning verifierad: 12 prop-deltan med relaterade bet, 1 U-dep-direktiv (Dir. 2026:43). Se DEC-007. **OBS triage (T2 rapporterar bara, ej åtgärdat):** 8 av 12 props (2025/26:174,191–198) säger api=Klar medan reforms.json säger "proposition" — datafilen kan vara föråldrad. |
| T2-fix-3 | Signalregel jobb A: betänkandebeslut, inte dokumentstatus | riksdagen.js, riksdagen.test.js, fixtures/ | ✅ Done | Dokumentstatus "Klar"=publiceringsstatus, bär ingen signal. Regel 1: terminal datafil-status (beslutad) → ingen rapport, ingen fetch. Regel 2: delta endast när ≥1 kopplat betänkande fattat beslut; faktapar med statustext/beslutsdatum/rdbeslut/rskr ur bet-dokumentstatus. API-fynd: obeslutade bet HAR BES-aktivitet med status "planerat" → kriteriet är "inträffat" (fixture HD01UbU30). 16/16 tester; skarp körning = exakt 9 deltan (174, 191–198), 3 terminala skippade. Ej-funnen prop rapporteras fortfarande (anomali). |
| T2-fix-4 | Jobb B2: nya propositioner från U-dep | riksdagen.js, riksdagen.test.js, fixtures/ | ✅ Done | doktyp=prop i B-fönstret, organ-fullnamnsfilter, manifest-dedup. Delta typ "ny-proposition". 19/19 tester (fixture: 31 riktiga props, 1 U-dep). Skarp körning: Prop. 2025/26:260 (etikprövning) fångad — saknas i manifestet, triagepunkt. Fynd: friskole-propositionen efter lagrådsremissen 13 maj finns INTE i API:t ännu (bet UbU30 = placeholder, beredning planerad aug 2026). **T4-krav: rapport.js behöver sektion för typ ny-proposition.** |
| T3 | RSS-watcher: regeringen.se, Utbildningsdep., 7-dagarsfönster | scripts/bevakning/rss.js | ✅ Done | Feed-discovery verifierad (rk-main.js bygger /Filter/RssFeed?, taxonomi 2085=lagrådsremiss + 1294=U-dep, filtret biter server-side). Delta `{typ:"lagradsremiss",titel,datum,url}`; fonster_fullt_tackt-flagga; fail loud. 12 tester mot fångad riktig fixture (100 poster, djup till 2012-12-11). Live smoke OK: friskole-lagrådsremissen 2026-05-13 fångas. |
| T4 | GitHub Action: veckocron + dispatch + Issue "Bevakningsrapport v.X" | bevakning.yml, rapport.js | ✅ Done | rapport.js: sektioner A/B/B2/C/lagrådsremisser, triage-kryssrutor, Övrigt-sektion för okända typer, GITHUB_OUTPUT-kontrakt, 7/7 tester. Permissions exakt contents:read+issues:write. Live-verifierat efter deploy 2026-06-11 (workflow_dispatch registreras först när filen finns på master — dispatch från dev 404:ar innan dess): scenario 1 (maj-fönster) → issue #1 med friskole-lagrådsremissen 2026-05-13 + Dir. 2026:39; scenario 2 (jan-fönster) → grön körning, alla fönsterberoende sektioner tomma, MEN issue #2 skapades med de 9 fönsteroberoende A-deltana — äkta tom körning kräver att A-backloggen triagerats i reforms.json (by design). Test-issues stängda ("testkörning T4"). T4-fix: absUrl i alla jobb + actions v5/v6 (Node 24-deprecation före cron 22 juni). **Cronen är LIVE på master sedan deploy — första schemalagda körning måndag 15 juni 06:00 UTC. OBS: T4-fix ligger bara på dev tills nästa deploy.** |
| T5 | BEVAKNING.md: flöde och hanteringsrutin | BEVAKNING.md | ⬜ Todo | Följbar utan chatkontext; Dir. 2023:175 som exempel |
| T6 | Run DoD review for this sprint | (dod-reviewer) | ⬜ Todo | Sprint godkänd |

**Testkommando:** `node --test scripts/bevakning/extract.test.js`,
`node --test scripts/bevakning/riksdagen.test.js` och
`node --test scripts/bevakning/rss.test.js` (kör filerna var för sig — inte
katalogformen `node --test scripts/bevakning/`, den snubblar på CLI-stdout).
CLI: `node scripts/bevakning/extract.js [dataDir]` skriver manifest som JSON till stdout;
`node scripts/bevakning/riksdagen.js --from YYYY-MM-DD --tom YYYY-MM-DD` kör skarp watcher;
`node scripts/bevakning/rss.js --from YYYY-MM-DD --tom YYYY-MM-DD` kör RSS-watchern skarpt.
riksdagen.test.js och rss.test.js använder fångade riktiga svar i `scripts/bevakning/fixtures/`.

---

## Completed: Sprint 9 — Utredningar på tidslinjen

DoD-granskad och GODKÄND (T5, 2026-06-10). T2-followup levererad samma dag — alla 27 icke-aviserade utredningar renderas nu.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 9.T2 | Bakåtförlängd axel (2021) + utredningsstaplar | ✅ Done | Modell A — gemensam axel. Efter T2-followup: 27/27 utredningar renderas. |
| 9.T3 | Bidirektionell navigering utredning↔reform | ✅ Done | Lookup utrByReform vid render. Reformdetaljvy med Utredningar-sektion (visas bara vid kopplingar); utredningsvyn länkar tillbaka. reforms.json oförändrad. |
| 9.T4 | Kopplingslinjer vid hover/markering | ✅ Done | SVG-overlay i gantt-body. Bezierlinje från utredningens slut till reformens start. Hover visar tillfälligt, klick pin:ar. Ingen full re-render vid hover. |
| 9.T5 | DoD-granskning + sprintstängning | ✅ Done | Alla T1–T4 maskinella kriterier uppfyllda. |
| 9.T2-followup | Datumkomplettering 6 utredningar | ✅ Done | utr-fler-vagar, utr-komvux, utr-heder, utr-grundlaggande-svenska, utr-undervisningstid, utr-lararutbildning — primärkällsverifierade datum. 0 skips. |

---

## Completed: Sprint 1 – Grundfunktion live

9/10 uppgifter klara. Kvar: 1.2 DNS (väntar propagering), 1.10 dela med kollegor.

---

## Completed: Sprint 2 – Innehåll, struktur och kopplingar

**Mål:** Separera data från gränssnitt, förbättra layout, verifiera innehåll.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.1 | Skolverkets uppdragsstatus per reform | ✅ Done | Data från RB 2025/2026, indikator + modal |
| 2.2 | Responsiv kartyta på desktop | ✅ Done | Full bredd, noder omplacerade med min 15% avstånd |
| 2.3 | dev/master-branching + deploy.sh | ✅ Done | commit.sh → dev, deploy.sh mergar till master |
| 2.4 | Separera data till JSON-filer | ✅ Done | data/reforms.json, connections.json, uppdrag.json — fetch() vid laddning |
| 2.5 | Granska alla 15 kopplingar | ⬜ Todo | Saknas/fel? |
| 2.6 | Verifiera rollfilter | ⬜ Todo | Stämmer rollerna per reform? |
| 2.7 | Uppdatera efter riksdagsbeslut | ⬜ Todo | Bevaka vårens voteringar |
| 2.8 | Komplettera ändrade timplaner | ⬜ Todo | Prop. 2023/24:20 |
| 2.9 | Verifiera budgetsiffra 95 Mkr studiero | ⬜ Todo | Källa: budgetprop, inte Prop. 193 |
| 2.10 | Feedback-runda #2 | ⬜ Todo | Bredare grupp |

---

## Completed: Sprint 3 – Målbild och infrastrukturberoenden

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3.1 | data/malbild.json med pelardefinitioner och kopplingar | ✅ Done | 6 pelare, 16 reformer, motiveringstext per koppling |
| 3.2 | malbild.html med chips, pelare, SVG-linjer, sidebar | ✅ Done | Samma designspråk som reformkartan |
| 3.3 | Fliknavigation mellan reformkarta och målbild | ✅ Done | Header-navigation i index.html och malbild.html |
| 3.4 | Klickbara kopplingar med bezier-kurvor | ✅ Done | Sorterade ankarpunkter, minimala korsningar |
| 3.5 | Sidebar med detaljer vid klick | ✅ Done | Reform- och pelardetaljer med motiveringstext |
| 3.6 | Sammanhållen visiontext | ✅ Done | Fällbar, första meningen synlig |
| 3.7 | Statistikrad | ✅ Done | Antal reformer med beroenden, pelare, totala kopplingar |
| 3.8 | Responsiv | ✅ Done | Mobilanpassad |
| 3.9 | Uppdatera infrastrukturberoenden | ✅ Done | Strategisk analys: betyg, läroplaner, tid, studiero |

---

## Completed: Sprint 5 – Listvy och uppdragsöversikt

| # | Task | Status | Notes |
|---|------|--------|-------|
| 5.1 | Fliknavigation (Reformkarta/Reformer/Uppdrag) | ✅ Done | Målbild dold från nav, nås via direkt URL |
| 5.2 | Reformtabell (reformer.html) | ✅ Done | Sorterings- och filterbar, sidebar med detaljer |
| 5.3 | Filter: kategori, status, uppdragsstatus | ✅ Done | |
| 5.4 | Uppdragsöversikt (uppdrag.html) | ✅ Done | Individuella uppdrag, inkl. relaterade |
| 5.5 | Tidsgruppering per kvartal/år | ✅ Done | Q2–Q4 2026, 2027, 2028+ |
| 5.6 | Snart-markering (30 dagar) | ✅ Done | Orange kant + badge |
| 5.7 | Uppdragstitlar från regleringsbrevet | ✅ Done | Formella namn, visas som rubrik |
| 5.8 | Tvåvägslänkning reformer↔uppdrag | ✅ Done | Deeplinks med URL-parametrar |
| 5.9 | Responsiv | ✅ Done | Mobilanpassad med sidebar-overlay |

---

## Completed: Sprint 6 – Tidslinje

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.1 | data/tidslinje.json (30 händelser) | ✅ Done | Ikraftträdanden, redovisningar, milstolpar, riksdagsbeslut |
| 6.2 | Expanderbar Gantt-layout | ✅ Done | Reformbars med chevron expand/collapse |
| 6.3 | Händelsemarkörer på bars | ✅ Done | Diamant, cirklar, fyrkant — 10px med vit border |
| 6.4 | Filter (dämpar, döljer inte) | ✅ Done | Typ + kategori |
| 6.5 | Hoppa-till-knappar | ✅ Done | Ersätter minikarta |
| 6.6 | Klickbar sidebar (händelser + uppdrag) | ✅ Done | Deeplinks till reformer/uppdrag |
| 6.7 | Responsiv + mobil touch-targets | ✅ Done | 44px touch-areas, sidebar overlay |

---

## What's Working Now
Reformkartan finns som `index.html` i roten. GitHub Pages serverar sidan.
- 16 reformnoder med kategorifärgad bakgrund, uppdragsstatus-chip, drag-and-drop
- Kopplingslinjer bakom kort (2px, 0.5 opacity), aktiva linjer framhävda
- Multi-select filter (område, tid, roll) — checkbox-logik, inga valda = visa alla
- Klick på tom yta återställer vald reform
- Mobil portrait: listvy med accordion-kort; landscape: kartvy med zoom/pan
- **Målbildsvy** (malbild.html): 6 infrastrukturpelare, 16 reformer med beroendekopplingar, SVG-bezierlinjer, sidebar med motiveringstext, statistikrad, responsiv (dold från navigation, nås via direkt URL)
- **Reformtabell** (reformer.html): sorterings- och filterbar tabell, sidebar med detaljer, deeplinks till uppdragsvy
- **Uppdragsöversikt** (uppdrag.html): individuella uppdrag grupperade per tidsperiod, snart-markering, sidebar med fulltext, deeplinks till reformtabell
- **Tidslinje** (tidslinje.html): expanderbar Gantt med reformbars, uppdragsbars, händelsemarkörer, tooltips, klickbar sidebar, hoppa-knappar
- Fliknavigation: Reformkarta / Reformer / Uppdrag / Tidslinje
- Cloudflare Web Analytics på alla sidor

```bash
# Öppna lokalt:
open index.html
# Live: https://niklasleide.github.io/leides-ljuvliga-lilla-reformkarta/
# Planerad: https://reformer.leide.se
```

---

## Blockers
- DNS-propagering för reformer.leide.se (sprint 1.10 beror på detta)

---

## Osäkert — kontrollera vid tillfälle
- Budgetsiffran 95 Mkr för trygghet/studiero — hämtad från budgetproposition, inte Prop. 193
- Ändrade timplaner (Prop. 2023/24:20) — begränsade detaljer
- Uppdragsfulltext för betyg och standardiserade tester refererar till RB 2025 som inte laddats ner — nuvarande text baserad på Skolverkets sidor och pressmeddelanden

---
> Update this at the **end** of each Claude Code session, not the beginning.
> Move completed tasks to ✅ Done. Keep Blockers current.
