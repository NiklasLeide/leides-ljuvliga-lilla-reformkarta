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

## Sprint 5 — Listvy
- [ ] Fliknavigation: lägg till 'Reformer' och 'Uppdrag' som nya flikar (Målbild & infrastruktur ska INTE synas i navigationen)
- [ ] Reformtabell (reformer.html): sorterings- och filterbar tabell med kolumnerna reform, kategori, status, ikraftträdande, uppdragsstatus, antal infrastrukturberoenden
- [ ] Filter överst: kategori, status, uppdragsstatus
- [ ] Klick på rad öppnar sidebar med samma detaljpanel som reformkartan
- [ ] Uppdragsöversikt (uppdrag.html): lista med alla Skolverket-uppdrag grupperade per tidsperiod (Q2 2026, Q3 2026, Q4 2026, 2027, 2028+)
- [ ] Varje uppdrag visar: reformnamn, uppdragstyp (uppdrag/förberedande/ej), redovisningsdatum, kort beskrivning
- [ ] Visuell markering av vad som är snart (närmaste 30 dagarna)
- [ ] Responsiv

## Sprint 6 — Tidslinje
- [ ] Visuell horisontell tidslinje (2025–2031)
- [ ] Reformer som block/markörer längs tidsaxeln, färgkodade efter kategori
- [ ] Uppdragsdeadlines synliga (redovisningsdatum)
- [ ] Klick på reform öppnar samma detaljpanel
- [ ] Responsiv för bred skärm

## Later / Stretch
_TBD_

## Deferred / Won't Do
- Bygga egna sammanfattningar per reform — kollegorna är tjänstemän, originalhandlingarna tillför mer
- Använda Reformverkstaden som källa — inspiration, inte faktakälla
- Utbildningsguide — format ej bestämt, parkerat tills behov bekräftas
- NotebookLM som format — ifrågasatt om det räcker, parkerat

---
