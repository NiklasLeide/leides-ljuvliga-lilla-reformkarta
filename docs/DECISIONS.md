# Decision Log — leides-ljuvliga-lilla-reformkarta

Record of key decisions made during the project. **Newest first.**

> The alternatives you *rejected* are as important as what you chose.
> Future sessions will read this — make the reasoning explicit.

---

## Format
```
### DEC-NNN: Title
**Date:** YYYY-MM-DD
**Decision:** What we chose
**Reasoning:** Why this option over the others
**Alternatives considered:** What was rejected and why
```

---

### DEC-006: SVG-overlay för kopplingslinjer i tidslinjen
**Date:** 2026-06-10
**Decision:** Kopplingslinjer utredning↔reform ritas i en enda SVG-overlay (`#ganttConnections`) inuti gantt-body, `pointer-events:none`, bezierkurvor beräknade från `getBoundingClientRect()`. Linjer ritas endast vid hover (tillfälligt) eller markering (pinned); aldrig vid load. Hover uppdaterar bara SVG-innehållet — ingen re-render av Gantt:en.
**Reasoning:** Gantt-body har variabel höjd (expanderbara rader) och staplar positionerade i procent. SVG ger exakta pixelkoordinater, rena diagonaler och skalar till multi-linjer (en reform → N utredningar) i ett enda lager som följer horisontell scroll automatiskt.
**Alternatives considered:** CSS-roterade divs (krångligt vid diagonaler, en div per linje, skalar dåligt), alltid-på-linjer (visuellt brus med 27 utredningar), Canvas (overkill för enstaka linjer)

---

### DEC-005: Utredningar på gemensam tidsaxel (Modell A)
**Date:** 2026-06-10
**Decision:** Tidslinjens axel förlängdes bakåt till 2021-01-01 och utredningar renderas som staplar på samma axel som reformerna, grupperade inom befintliga kategoriblock (kunskap/trygghet/larare/styrning) efter reformraderna. Visuell åtskillnad via dashed border + diagonalt stripe-mönster i samma kategoripalett. Poster utan verifierbart start/slutdatum skippas med console.warn — datum fabriceras aldrig. Reverse-links reform→utredningar beräknas vid render-tid från `kopplad_reform` (reforms.json modifieras inte).
**Reasoning:** En gemensam axel visar det kausala flödet utredning→reform direkt — utredningens slut ligger ofta nära reformens start. Separat vy eller fil hade dubblerat renderingslogik och tappat den visuella kopplingen.
**Alternatives considered:** Separat spatial fil/vy för utredningar (tappar tidssambandet med reformerna, mer kod att underhålla), egen sektion under Gantt:en (samma problem), datum i reforms.json (bryter mot principen att utredningsdata ägs av utredningar.json)

---

### DEC-004: Skolverkets uppdragsstatus som eget datalager
**Date:** 2026-03-23
**Decision:** Separat `skolverketUppdrag`-objekt med typ/kort/fulltext/kallor per reform. Visas som indikator (6px dot) på noder, detaljsektion i panelen, och modal för fulltext. Data från RB 2025/2026 och regeringsuppdrag.
**Reasoning:** Uppdragsstatus är en annan dimension än reformstatus (proposition vs beslutad). Separata data gör det enkelt att uppdatera utan att röra reformdatan. Modal för fulltext håller detaljpanelen kompakt.
**Alternatives considered:** Inline fulltext i detaljpanelen (för långt, scrollar bort annan info), tooltip (för liten för dessa textmängder)

---

### DEC-003: Mobil listvy (portrait) + kartvy (landscape)
**Date:** 2026-03-23
**Decision:** Portrait (<800px): scrollbar listvy med accordion-expandering, grupperad per kategori. Kopplingar som klickbara länkar. Landscape (mobil): växla till kartvyn med glesare nodlayout (max ~10% överlapp). Desktop: oförändrad kartvy.
**Reasoning:** 16 noder med linjer är för tätt för portrait-mobil oavsett zoom. En lista är det naturliga mobilmönstret. Landscape ger tillräckligt med yta för kartan om noderna separeras. Zoom/pan behålls i landscape för att navigera den glesare kartan.
**Alternatives considered:** Enbart zoom/pan utan listvy (testat i portrait, för trångt), enbart listvy utan kartväxling (tappar kopplingarna visuellt i landscape)

---

### DEC-002: ~~Mobilanpassning via zoom/pan + bottom sheet~~ (ERSATT av DEC-003)
**Date:** 2026-03-23
**Decision:** Pinch-to-zoom/pan på kartområdet, bottom sheet för detaljpanel, kompakta noder under 600px
**Reasoning:** Kartan har 16 noder med kopplingslinjer — för tät för en liten skärm utan zoom. Bottom sheet behåller kartan synlig medan detaljer visas. Ingen extern lib behövs.
**Alternatives considered:** Separat listvy för mobil (tappar det visuella), viewport-skalning via meta-tag (för grovt), extern lib som Panzoom (onödig dependency för ~50 rader JS)
**Utfall:** Testat — för trångt, dålig navigering. Ersatt av DEC-003.

---

### DEC-001: Single-file HTML with no build step
**Date:** 2026-03-23
**Decision:** Enkel HTML/CSS/JS i en fil (index.html), hostad via GitHub Pages
**Reasoning:** Projektet är en statisk informationsvisualisering utan backend. Inget byggsystem behövs. En fil är enklast att underhålla och dela.
**Alternatives considered:** React/Vite (onödig komplexitet för en sida), SSG som Astro (onödigt för en fil)

---
