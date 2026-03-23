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

### DEC-002: Mobilanpassning via zoom/pan + bottom sheet
**Date:** 2026-03-23
**Decision:** Pinch-to-zoom/pan på kartområdet, bottom sheet för detaljpanel, kompakta noder under 600px
**Reasoning:** Kartan har 16 noder med kopplingslinjer — för tät för en liten skärm utan zoom. Bottom sheet behåller kartan synlig medan detaljer visas. Ingen extern lib behövs.
**Alternatives considered:** Separat listvy för mobil (tappar det visuella), viewport-skalning via meta-tag (för grovt), extern lib som Panzoom (onödig dependency för ~50 rader JS)

---

### DEC-001: Single-file HTML with no build step
**Date:** 2026-03-23
**Decision:** Enkel HTML/CSS/JS i en fil (index.html), hostad via GitHub Pages
**Reasoning:** Projektet är en statisk informationsvisualisering utan backend. Inget byggsystem behövs. En fil är enklast att underhålla och dela.
**Alternatives considered:** React/Vite (onödig komplexitet för en sida), SSG som Astro (onödigt för en fil)

---
