# Changelog — leides-ljuvliga-lilla-reformkarta

Format: `[YYYY-MM-DD] type: description`
Types: `feat` | `fix` | `refactor` | `docs` | `chore` | `perf`

---

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
