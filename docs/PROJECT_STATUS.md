# Project Status — leides-ljuvliga-lilla-reformkarta

> **Last updated:** 2026-03-23
> **Current sprint:** Sprint 1 – Grundfunktion live
> **Sprint dates:** 2026-03-23 → TBD

---

## Current Sprint: Sprint 1 – Grundfunktion live

**Mål:** Reformkartan fungerar på reformer.leide.se och kan delas.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1 | GitHub-repo + Pages | ✅ Done | |
| 1.2 | DNS: reformer.leide.se → GitHub Pages | ⏸️ Väntar | CNAME konfigurerad i Loopia, väntar på propagering |
| 1.3 | Faktakontroll mot originaldokument | ✅ Done | 13/16 verifierade, 3 rättade |
| 1.4 | Rätta betygssystem: status, datum, länkar | ✅ Done | Prop. 2025/26:197, ikraft 1 juli 2028 |
| 1.5 | Rätta yrkesutbildning: fyll på innehåll | ✅ Done | Entreprenad, yrkesprov, PDF-länk |
| 1.6 | Nyansera studiero: ikraftträdande | ✅ Done | Merparten 1 aug 2026, delar 1 juli 2028 |
| 1.7 | ~Mobilanpassning v1~ | ⬜ Ersatt | Zoom/pan testat — för trångt. Ersatt av v2 |
| 1.8 | Mobil v2: listvy i portrait | ⬜ Todo | Scrollbar lista, accordion, kopplingar som klickbara länkar |
| 1.9 | Mobil v2: kartvy i landscape | ⬜ Todo | Orientation-switch, glesare nodlayout (max ~10% överlapp) |
| 1.10 | Dela med 3–5 kollegor för första feedback | ⬜ Todo | Kan göras när DNS fungerar |

**Status legend:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🚫 Blocked | ⏸️ Paused

---

## What's Working Now
Reformkartan finns som `index.html` i roten. GitHub Pages serverar sidan.
- 16 reformnoder med status, ikraftträdande och kategori
- Aktiv nod visas med tjock border i kategorifärg + scale, länkade noder med streckad blå border
- Noder kan dras runt (drag-and-drop), SVG-linjer ritas om i realtid
- Mobil v1 (zoom/pan) finns men ersätts av v2 (listvy portrait + kartvy landscape)
- Filter: område, tid, roll

```bash
# Öppna lokalt:
open index.html
# Live: https://niklasleide.github.io/leides-ljuvliga-lilla-reformkarta/
# Planerad: https://reformer.leide.se
```

---

## Blockers
- DNS-propagering för reformer.leide.se (sprint 1.8 beror på detta)

---

## Osäkert — kontrollera vid tillfälle
- Budgetsiffran 95 Mkr för trygghet/studiero — hämtad från budgetproposition, inte Prop. 193
- Ändrade timplaner (Prop. 2023/24:20) — begränsade detaljer

---
> Update this at the **end** of each Claude Code session, not the beginning.
> Move completed tasks to ✅ Done. Keep Blockers current.
