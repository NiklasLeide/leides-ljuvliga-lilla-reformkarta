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
| T2 | Riksdagen-watcher: status-diff API vs datafiler | scripts/bevakning/riksdagen.js | ✅ Done | 8 tester (synteiskt testfall + jobb B/C-filtrering + nätverksfel-säkerhet) passerar. Skarp körning mot live API kräver att Niklas verifierar empiriska antaganden (prop-uppslag-parameter, departementsfält) — sandboxen blockerar Riksdagens API (HTTP 403). Se kodkommentar och --verbose. |
| T3 | RSS-watcher: regeringen.se, Utbildningsdep., 7-dagarsfönster | scripts/bevakning/rss.js | ⬜ Todo | Poster flaggas med titel+datum+URL; feed-URL:er ur verifierad mikrorunda |
| T4 | GitHub Action: veckocron + dispatch + Issue "Bevakningsrapport v.X" | .github/workflows/bevakning.yml | ⬜ Todo | Issue med deltan+länkar+triage-kryssrutor; tom körning = ingen issue |
| T5 | BEVAKNING.md: flöde och hanteringsrutin | BEVAKNING.md | ⬜ Todo | Följbar utan chatkontext; Dir. 2023:175 som exempel |
| T6 | Run DoD review for this sprint | (dod-reviewer) | ⬜ Todo | Sprint godkänd |

**Testkommando T1:** `node --test scripts/bevakning/extract.test.js` (OBS: inte
katalogformen `node --test scripts/bevakning/` — den snubblar på extract.js CLI-stdout).
CLI: `node scripts/bevakning/extract.js [dataDir]` skriver manifest som JSON till stdout.

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
