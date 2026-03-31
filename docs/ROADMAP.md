# Roadmap — leides-ljuvliga-lilla-reformkarta

> Keep this honest. If something's not happening, move it to Deferred — don't leave it rotting in Next.

## Now (Sprint 1 — Grundfunktion live)
- [x] GitHub-repo + Pages
- [x] Faktakontroll mot originaldokument
- [x] Rätta betygssystem: status → proposition, ikraft 1 juli 2028, komplettera beskrivning med slutprovsdatum
- [x] Rätta yrkesutbildning: ny beskrivning (entreprenad, yrkesprov), PDF-länk
- [x] Nyansera studiero: ikraftträdande (merparten 1 aug 2026, stödundervisning 1 juli 2028)
- [x] ~Mobilanpassning v1 (pinch-to-zoom/pan, bottom sheet)~ — ersatt av v2
- [x] Mobil v2: listvy i portrait — accordion-kort per kategori, kopplingar som klickbara länkar
- [x] Mobil v2: kartvy i landscape — kompakta noder, zoom/pan, sidopanel 20% bredd
- [ ] DNS: reformer.leide.se (väntar propagering)
- [ ] Dela med 3–5 kollegor för feedback

## Now (Sprint 2 — Innehåll, struktur och kopplingar)
- [x] Skolverkets uppdragsstatus per reform — data från RB 2025/2026, klickbar fulltext med modal
- [x] Responsiv kartyta på desktop — full bredd, omplacerade noder med min 15% avstånd
- [x] Sätt upp dev/master-branching med commit.sh (bara dev) och deploy.sh (manuell bekräftelse för master)
- [x] Separera innehåll från gränssnitt — flytta reformdata, kopplingar och uppdrag till JSON-filer
- [ ] Granska alla 15 kopplingar — saknas/fel?
- [ ] Verifiera rollfilter (rektor/lärare/skolchef) per reform
- [ ] Uppdatera efter riksdagsbeslut (vårens voteringar)
- [ ] Komplettera ändrade timplaner (Prop. 2023/24:20)
- [ ] Verifiera budgetsiffra 95 Mkr för studiero (källa: budgetprop, inte Prop. 193)
- [ ] Feedback-runda #2 — bredare grupp

## Completed: Sprint 3 — Målbild och infrastrukturberoenden
- [x] Skapa data/malbild.json med pelardefinitioner och kopplingar reform→pelare
- [x] Bygga malbild.html med samma designspråk som reformkartan (header, navigation, sidebar)
- [x] Fliknavigation mellan reformkartan och målbildsvyn
- [x] Visa reformer och pelare med klickbara kopplingar (linjer)
- [x] Sidebar med detaljer vid klick (samma mönster som reformkartan)
- [x] Sammanhållen visiontext överst, fällbar
- [x] Statistikrad (antal reformer med beroenden, antal pelare, etc.)
- [x] Responsiv
- [x] Uppdatera infrastrukturberoenden efter strategisk analys (betyg, läroplaner, tid, studiero)

## Sprint 4 — Underhållsrutin
- [x] Definiera hur och när innehållet uppdateras (efter riksdagsbeslut, regleringsbrev, propositioner)
- [x] Skapa bevakningslista med URL:er per reform (docs/BEVAKNING.md)
- [ ] Dokumentera uppdateringsflöde i CLAUDE.md (vem gör vad, vilka källor kollas)
- [ ] Bevaka vårens riksdagsbeslut — uppdatera reformstatus när propositioner antas
- [ ] Sätt upp en checklista för kvartalsvis genomgång av reformdata

## Completed: Sprint 5 — Listvy och uppdragsöversikt
- [x] Fliknavigation: Reformkarta / Reformer / Uppdrag (Målbild dold)
- [x] Reformtabell (reformer.html): sorterings- och filterbar tabell med sidebar
- [x] Filter överst: kategori, status, uppdragsstatus
- [x] Klick på rad öppnar sidebar med detaljpanel
- [x] Uppdragsöversikt (uppdrag.html): individuella uppdrag (inkl. relaterade) grupperade per tidsperiod
- [x] Uppdragstitlar från regleringsbrevet som rubriker
- [x] Tvåvägslänkning: reformer.html ↔ uppdrag.html med deeplinks
- [x] Visuell markering av snart (närmaste 30 dagarna)
- [x] Responsiv

## Completed: Sprint 6 — Tidslinje
- [x] Skapa data/tidslinje.json med 30 händelser (2025–2031)
- [x] Expanderbar Gantt-layout: reformbars med händelsemarkörer, uppdragsbars med chevron expand/collapse
- [x] Fem händelsetyper med visuella markörer: diamant (ikraftträdande), cirklar (milstolpe, redovisning, riksdagsbeslut), fyrkant (delredovisning)
- [x] Färgkodning per reformkategori — solida bars med border
- [x] Filter: togglea händelsetyper och kategorier — dämpar icke-matchande (opacity 0.15)
- [x] Hoppa-till-knappar (2025–2029+) ersätter minikarta
- [x] Klick på händelsemarkörer öppnar sidebar med detalj + deeplinks
- [x] Klick på uppdragsnamn/bar öppnar sidebar med uppdragsinfo
- [x] Tooltip på trunkerade uppdragsnamn
- [x] Visa alla / Dölj alla detaljer-knapp
- [x] Responsiv — mobil touch-targets 44px, sidebar som overlay
- [x] Fliknavigation: Tidslinje tillagd på alla sidor

## Sprint 7 — Polering
- [ ] Kartan: starkare opacity på kopplingar och kortramar i defaultläge
- [ ] Kartan: klick på tom yta återställer vald reform
- [ ] Kartan: multi-select filter (checkbox istället för radio)
- [ ] Kartan: kategori-färg som bred vänsterkant på kort istället för prick
- [ ] Kartan: uppdragsstatus som textchip (Uppdrag/Förberedande/Ej uppdrag) istället för färgprick

## Kommande
- Nästa bevakningspunkt: 8 maj 2026 (Skolverkets genomförandeplan digitala slutprov)
- Riksdagsbeslut väntas april–juni 2026 — bevaka varannan vecka
- Autonom bevakningsagent — parkerad, tooling räcker inte ännu

## Later / Stretch

## Deferred / Won't Do
- Bygga egna sammanfattningar per reform — kollegorna är tjänstemän, originalhandlingarna tillför mer
- Använda Reformverkstaden som källa — inspiration, inte faktakälla
- Utbildningsguide — format ej bestämt, parkerat tills behov bekräftas
- NotebookLM som format — ifrågasatt om det räcker, parkerat

---
