# Changelog — leides-ljuvliga-lilla-reformkarta

Format: `[YYYY-MM-DD] type: description`
Types: `feat` | `fix` | `refactor` | `docs` | `chore` | `perf`

---

[2026-03-31] feat: polera kartan — 4px vänsterkant i kategorifärg, uppdragsstatus som textchip, klick på tom yta återställer, multi-select filter (Set-baserat), prick och uppdragsdot borttagna
[2026-03-31] docs: lägg till sprint 7 polering i roadmap — opacity, klick-reset, multi-filter, vänsterkant, textchip
[2026-03-31] docs: markera sprint 5 och 6 som klara i roadmap, lägg till kommande bevakningspunkter
[2026-03-31] feat: tidslinje — smalare bars (16px reform, 8px uppdrag), tooltip på trunkerade uppdragsnamn (title-attribut), klick på uppdragsnamn/bar öppnar sidebar med titel, kort, redovisningsdatum, källor och deeplinks
[2026-03-31] feat: tidslinje — tjockare bars (24px reform, 12px uppdrag), alla markörer på bars (10px cirklar, 12px diamanter, 2px vit border), händelseraden borttagen, markörer på uppdragsbars
[2026-03-31] docs: uppdatera CLAUDE.md — stack, kommandon, katalogstruktur, designsystem, projektspecifika misstag
[2026-03-31] fix: mobilproblem i tidslinje — chevron touch-target 36px med active-state, markörer 44px touch-area via pseudo-element, dubbel stängknapp i sidebar fixad, clearDetail kraschar inte längre (#detailDefault återskapas), filter/knappar min-height 32px, sidebar-close 44px
[2026-03-31] fix: tidslinje — ta bort overflow från gantt-scroll (CSS-spec tvingar overflow-y:auto vid overflow-x:auto → klippte vertikalt), sidan hanterar nu all scroll, hoppa-knappar scrollar via getBoundingClientRect
[2026-03-31] fix: tidslinje — vertikal scrollning (overflow-y visible, align-items start), sidebar X-knapp för att återställa sammanfattning, hoppa-knappar hittar rätt position via tick-element
[2026-03-31] feat: förbättra tidslinjens design — solida färgade bars, diamant-ikraftträdande, zebraränder, streckade gridlinjer, kvartalmarkeringar, hoppa-till-knappar, kategorirubriker med bakgrundsfärg, hover-effekter, expanderat sidebar-default med sammanfattning
[2026-03-31] fix: tidslinje — bars och markörer synliga (explicit höjd på chart-celler), horisontell scroll fungerar (minmax grid + min-width:0)
[2026-03-30] refactor: bygg om tidslinje till expanderbar Gantt — ren default-vy med chevron-expand för uppdrag/milstolpar, visa/dölj alla, tooltips, animerad expand/collapse
[2026-03-30] refactor: bygg om tidslinje till Gantt-layout — horisontella reformbars, uppdragsbars, händelsemarkörer med tooltips, Nu-linje, legend, minimap
[2026-03-30] refactor: bygg om tidslinje till ensidigt höger-layout — tidsaxel vänster med månadsetiketter, 2-kolumns grid för täta månader, typ-badges, komprimerade tomma månader
[2026-03-30] fix: tidslinje — sticky filterrad, fixad minimap-scroll och klick, tydligare Nu-markör (mörk pill), tätare spacing mellan kort
[2026-03-30] feat: skapa tidslinje.html — vertikal tidslinje med swim lanes, mini-karta, filter (dämpar), snart/passerat-markeringar, deeplinks, fliknavigation uppdaterad på alla sidor
[2026-03-30] feat: skapa data/tidslinje.json med 30 händelser (2025–2031) — ikraftträdanden, redovisningar, milstolpar, riksdagsbeslut
[2026-03-30] docs: uppdatera roadmap med sprint 6 tidslinje — vertikal tidslinje, swim lanes, mini-karta, adaptiv spacing
[2026-03-30] docs: sprint 5 klar — uppdatera PROJECT_STATUS, ROADMAP och CHANGELOG inför deploy
[2026-03-30] feat: tvåvägslänkning mellan uppdrag.html och reformer.html — klickbara reformnamn, uppdragstitlar som länkar, URL-parametrar för deeplinks
[2026-03-30] fix: korrigera uppdragstitlar till formella namn från regleringsbrevet
[2026-03-30] feat: lägg till uppdragstitlar i uppdrag.json och visa som rubriker i uppdrag.html — nya relaterade uppdrag (brottsprevention, tillbud, kartläggningsmaterial SVA)
[2026-03-30] refactor: ändra uppdrag.html till att lista individuella uppdrag (inkl. relaterade) istället för reformer — typ=ej exkluderas
[2026-03-30] feat: skapa uppdrag.html — uppdragsöversikt med statuskolumner, tidsgruppering, snart-markering och sidebar
[2026-03-30] fix: ta bort infra-kolumn från reformer.html
[2026-03-30] fix: commit.sh synkar nu alla HTML-filer dynamiskt istället för hårdkodade filnamn
[2026-03-30] feat: skapa reformer.html — tabellvy med filter, sortering, sidebar och fliknavigation (Reformkarta/Reformer/Uppdrag)
[2026-03-30] docs: uppdatera roadmap med sprint 5 listvy — reformtabell, uppdragsöversikt, fliknavigation
[2026-03-30] feat: lägg till Cloudflare Web Analytics i index.html och malbild.html
[2026-03-30] fix: dölj fliknavigation till målbilden — sidan nås bara via direkt URL tills den är redo
[2026-03-30] docs: uppdatera PROJECT_STATUS, ROADMAP och CHANGELOG — sprint 3 klar, deploy till produktion
[2026-03-30] feat: uppdatera infrastrukturberoenden i malbild.json — nya kopplingar för betyg (datakontroll), läroplaner (likvärdig-miljö), undervisningstid (standarder) och studiero (datakontroll + likvärdig-miljö)
[2026-03-27] fix: cache-busting på fetch i malbild.html för att undvika gammal data
[2026-03-27] feat: specifik motivering per reform-pelare-koppling i malbild.json och sidebar
[2026-03-27] fix: malbild.html — bezier-kurvor istället för raka linjer, större runda badges, spridda ankarpunkter sorterade för minimala korsningar
[2026-03-27] fix: malbild.html — SVG-linjer bakom kort, rundade badges, spridda ankarpunkter, höjd dimmed-opacity, mer spacing
[2026-03-27] fix: commit.sh synkar nu malbild.html till dev-preview
[2026-03-27] feat: skapa malbild.html — infrastrukturberoendevy med chips, pelare, SVG-linjer, sidebar och fliknavigation
[2026-03-27] feat: lägg till fliknavigation i index.html och malbild.html (Reformkarta / Målbild & infrastruktur)
[2026-03-27] feat: skapa data/malbild.json med pelardefinitioner, visiontext och reformberoenden (sprint 3)
[2026-03-27] docs: roadmap — ny sprint 3 (målbild/infrastrukturberoenden), underhåll→sprint 4, listvy→sprint 5, tidslinje→sprint 6
[2026-03-24] feat: responsiv kartlayout — full bredd, omplacerade noder med mer luft, min 15% avstånd
[2026-03-24] refactor: separera reformdata, kopplingar och uppdrag till JSON-filer (data/), index.html hämtar med fetch()
[2026-03-24] chore: commit.sh synkar automatiskt dev-sidfiler till master:dev/ för preview på reformer.leide.se/dev/
[2026-03-24] chore: dev/deploy-flöde — commit.sh pushar bara till dev, deploy.sh mergar till master med manuell bekräftelse
[2026-03-24] feat: större kartyta på desktop — container 1400px, karta min-height 700px, panel 360px
[2026-03-23] feat: Skolverkets uppdragsstatus per reform — indikator på noder, detaljsektion med klickbar fulltext, modal med källa
[2026-03-23] fix: sidopanel stängs inte längre vid vertikal scroll (bara horisontell svep höger)
[2026-03-23] feat: landscape sidopanel (20% bredd) ersätter bottom sheet, kompakt text, svep höger stänger
[2026-03-23] fix: landscape zoom/pan hoppar inte längre vid start; visa kopplingstext i portrait-listvy
[2026-03-23] fix: listvy synlig i portrait — CSS-ordning korrigerad (display:none före media queries)
[2026-03-23] feat: mobil v2 — listvy med accordion i portrait, kartvy med zoom/pan i landscape
[2026-03-23] docs: behåll zoom/pan i landscape-kartvy (DEC-003 uppdaterad)
[2026-03-23] docs: komplettera changelog, lägg till DEC-002 mobilanpassning, dokumentera commit.sh-quirk
[2026-03-23] docs: planera mobil v2 — listvy (portrait) + kartvy med gles layout (landscape), ersätter zoom/pan
[2026-03-23] docs: lägg till felrättningar i roadmap sprint 1
[2026-03-23] docs: uppdatera PROJECT_STATUS och ROADMAP med sprintplan (sprint 1–3)
[2026-03-23] fix: faktakontroll — betyg: komplettera beskrivning med slutprovsdatum; yrkesutbildning: ny beskrivning + PDF-länk; studiero: nyanserat ikraftträdande
[2026-03-23] feat: mobile-responsive layout — pinch-to-zoom/pan, bottom sheet detail panel, compact nodes under 600px
[2026-03-23] docs: remove target audience from README purpose section
[2026-03-23] fix: connected nodes opaque background so SVG lines don't bleed through
[2026-03-23] fix: preserve active/dimmed line state when drawConnections redraws during drag
[2026-03-23] chore: add CNAME for reformer.leide.se custom domain
[2026-03-23] feat: distinct active vs connected node styling (solid category-color border vs dashed blue)
[2026-03-23] feat: drag-and-drop nodes with real-time SVG line redraw (pointer events, 5px click threshold)
[2026-03-23] feat: add reformkarta.html as index.html for GitHub Pages hosting
[2026-03-23] docs: add README.md with project description
[2026-03-23] chore: project initialized via starter kit
