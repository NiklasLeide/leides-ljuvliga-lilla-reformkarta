# Project Status — leides-ljuvliga-lilla-reformkarta

> **Last updated:** 2026-03-23
> **Current sprint:** Sprint 2 – Innehåll och kopplingar
> **Sprint dates:** 2026-03-23 → TBD

---

## Completed: Sprint 1 – Grundfunktion live

9/10 uppgifter klara. Kvar: 1.2 DNS (väntar propagering), 1.10 dela med kollegor.

---

## Current Sprint: Sprint 2 – Innehåll och kopplingar

**Mål:** Kopplingarna är korrekta och kartan tillför värde. Skolverkets uppdragsstatus synlig.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.1 | Skolverkets uppdragsstatus per reform | ✅ Done | Data från RB 2025/2026, indikator på noder, detaljsektion + modal |
| 2.2 | Granska alla 15 kopplingar | ⬜ Todo | Saknas kopplingar? Fel? |
| 2.3 | Verifiera rollfilter | ⬜ Todo | Stämmer rollerna per reform? |
| 2.4 | Uppdatera efter riksdagsbeslut | ⬜ Todo | Bevaka vårens voteringar |
| 2.5 | Komplettera ändrade timplaner | ⬜ Todo | Prop. 2023/24:20, begränsade detaljer |
| 2.6 | Feedback-runda #2 | ⬜ Todo | Bredare grupp |

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
