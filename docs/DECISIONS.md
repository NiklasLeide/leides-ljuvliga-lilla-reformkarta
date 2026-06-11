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

### DEC-009: Guidelagret som separat data/guide.json, inte utökning av reforms.json
**Date:** 2026-06-11
**Decision:** Huvudmannaguidens data (Sprint 11) ligger i en egen fil `data/guide.json` — en post per reform, nycklad på `reform_id` mot reforms.json. Synk-risken mellan filerna hanteras med runtime-validering: guide-vyn loggar reform-id utan guidepost och guideposter utan reform till konsolen (fail loud, aldrig tyst), och bevakningsautomatiseringens extract.js kan utökas att inkludera guide-id:n i manifestet.
**Reasoning:** (1) Etablerat mönster — varje datadimension är redan en egen fil (connections, uppdrag, malbild, tidslinje, utredningar; se DEC-004 med samma resonemang: separata data uppdateras utan att röra reformdatan). (2) reforms.json laddas av ALLA fem sidor vid varje sidvisning; guide-innehållet är textmassivt (ordagranna övergångsbestämmelser, kravlistor med källor) och behövs bara i guide-vyn — inbakat skulle det blåsa upp varje sidladdning och varje render-loop som itererar reformer. (3) /bevakning-patchar rör reforms.json-statusar ofta; en separat guide-fil ger mindre diffar och lägre konfliktyta per patch.
**Alternatives considered:** Utökning av reformposterna i reforms.json (noll synk-risk men filstorlek/rendering enligt ovan, och varje guide-uppdatering skulle diffa mot kartans kärndata); separat fil per reform (överdriven granularitet för ~16 poster, fler fetch:ar).

---

### DEC-008: Per-feed-degradering i RSS-watchern
**Date:** 2026-06-11
**Decision:** Ett RSS-flöde som inte går att hämta nollar inte övriga flödens täckning: felet fångas per feed och landar som `feed_fel` i rapportens floden[] → 🔴-varning i veckorapportens issue + "FEL" i footern. Exit 1 endast när ALLA flöden faller (då finns ingen RSS-täckning alls att rapportera).
**Reasoning:** statskontoret.se blockerar GitHub Actions-runners på nätverksnivå (fetch failed, persistent över flera körningar; lokalt fungerar flödet — trolig WAF/datacenter-IP-blockering, inte IPv6: domänen saknar AAAA). Med hård fail-loud per feed skulle ett permanent oåtkomligt externt värdskap göra HELA veckorapporten röd och utebliven — sämre än en rapport med explicit flaggad lucka. Fail loud-principen behålls i sak: felet är högljutt synligt i issuet, aldrig tyst.
**Alternatives considered:** Hård fail på första feed-felet (ursprungsdesign — ger permanent död veckorapport så länge statskontoret blockerar); retry/backoff (hjälper inte mot IP-blockering); proxy/spegel för statsliggaren (out of scope, ny infrastruktur). Regleringsbrev-deltan uteblir i CI tills blockeringen löses — fångas lokalt vid /bevakning-triage i stället.

---

### DEC-007: Riksdagen-watchern matchar på organ-kortkod + testas mot fångade API-svar
**Date:** 2026-06-10
**Decision:** Jobb B identifierar Utbildningsdepartementets direktiv via list-entryts `organ`-kortkod (`"U-dep"`), inte via fullständigt departementsnamn — och gör ingen detalj-fetch när `organ` redan finns på list-entryt. Full dir-beteckning byggs som `Dir. <rm>:<nummer>` (riksdagens list-API ger löpnumret och årtalet i skilda fält). Relaterade bet/rskr läses ur `dokumentstatus.dokreferens.referens` (referenstyp `behandlas_i`). Enhetstesterna drivs av RIKTIGA API-svar sparade som fixtures i `scripts/bevakning/fixtures/`.
**Reasoning:** Live-verifiering (T2-fix) visade att `dokument.departement` är `undefined` för direktiv även i detalj-svaret — bara `organ`-kortkoden finns. De tidigare mockarna antog fel format (fullt namn, beteckning med årtal, relaterade i dokuppgift) och gav 8/8 grönt medan jobb B i praktiken aldrig hittade något. Fixtures av skarpa svar gör att testerna fångar verkliga formatändringar istället för att cementera antaganden.
**Alternatives considered:** Matcha på fullt departementsnamn via detalj-fetch (omöjligt — fältet saknas för dir, och 1 extra anrop per dir/vecka i onödan); mappa organ-kortkod → fullt namn i rapporten (lätt tolkning, bryter mot principen att rapporten bara återger beskrivande faktapar); behålla syntetiska mockar (gav falskt grönsken — hela orsaken till T2-fix)

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
