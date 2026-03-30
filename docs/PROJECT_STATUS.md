# Project Status — leides-ljuvliga-lilla-reformkarta

> **Last updated:** 2026-03-30
> **Current sprint:** Sprint 4 – Underhållsrutin
> **Sprint dates:** 2026-03-30 → TBD

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

## What's Working Now
Reformkartan finns som `index.html` i roten. GitHub Pages serverar sidan.
- 16 reformnoder med status, ikraftträdande och kategori
- Aktiv nod visas med tjock border i kategorifärg + scale, länkade noder med streckad blå border
- Noder kan dras runt (drag-and-drop), SVG-linjer ritas om i realtid
- Mobil portrait: listvy med accordion-kort, kopplingstext, klickbara länkar
- Mobil landscape: kartvy med zoom/pan, sidopanel (20% bredd) för detaljer
- Filter: område, tid, roll
- Skolverkets uppdragsstatus: indikator på noder (grön/gul/grå), detaljsektion med klickbar fulltext + modal
- **Målbildsvy** (malbild.html): 6 infrastrukturpelare, 16 reformer med beroendekopplingar, SVG-bezierlinjer, sidebar med motiveringstext, statistikrad, responsiv

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
