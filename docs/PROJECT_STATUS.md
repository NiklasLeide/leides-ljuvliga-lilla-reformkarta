# Project Status — leides-ljuvliga-lilla-reformkarta

> **Last updated:** 2026-03-31
> **Current sprint:** Underhåll — alla sprints (1–7) klara
> **Sprint dates:** —

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
