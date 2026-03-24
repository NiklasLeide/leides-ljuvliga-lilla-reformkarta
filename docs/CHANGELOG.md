# Changelog — leides-ljuvliga-lilla-reformkarta

Format: `[YYYY-MM-DD] type: description`
Types: `feat` | `fix` | `refactor` | `docs` | `chore` | `perf`

---

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
