---
description: Triagera senaste bevakningsrapport-issuet mot primärkällor och bygg datapatch
---

# /bevakning — triagera veckans bevakningsrapport

Du triagerar den automatiska bevakningsrapporten. Reglerna står i
**docs/BEVAKNING.md** (Verifieringsregler + Triage-klassning) — läs dem FÖRST
och följ dem; de upprepas inte här.

## Hårda regler
- **Overifierbart = eskalera. Gissa aldrig.** Kan ett delta inte verifieras
  direkt ur den länkade primärkällan klassas det som eskalera — du fyller
  aldrig i "troliga" värden.
- **Ändra aldrig datafiler utan explicit ja** från användaren på en visad diff.
- docs/BEVAKNING.md är regelkällan. Vid konflikt mellan detta kommando och
  BEVAKNING.md gäller BEVAKNING.md — och flagga konflikten.

## Rutinen

1. **Hämta rapporten.** Senaste öppna issue med label `bevakning`:
   `gh issue list --label bevakning --state open --json number,title,body --limit 1`
   Finns ingen öppen issue: säg det och stanna.

2. **Verifiera varje delta mot dess primärkällänk.** Hämta den länkade sidan
   (WebFetch) och läs riksdagens/regeringens EGEN text — rapportens påstående
   är en hypotes tills källan bekräftar den. Kontrollera enligt
   verifieringsreglerna i BEVAKNING.md (officiella namn, beslutsdatum,
   spårbarhet).

3. **Klassificera varje delta** enligt Triage-klassning i BEVAKNING.md:
   - `åtgärda` — källan bekräftar; ingår i datapatchen (steg 4)
   - `ignorera` — kräver motivering i klartext
   - `eskalera` — allt overifierbart; listas för research-flödet
     (RESEARCH_AGENT.md), ingår INTE i datapatchen

   Typspecifikt (utöver de allmänna reglerna):
   - `sou-levererad` — betänkandet är redan registrerat i utredningar.json
     (det är så matchningen sker); verifiera nr/titel/datum mot källan och
     bocka av. Om datafilen INTE har betänkandet trots deltat är något fel
     i kedjan → eskalera.
   - `ny-sou` — riksdagens SOU-data saknar departement, därför listas alla
     departement (det är inte en bugg). Avgör scope ur källan, med
     "betänkande av"-ledtråden som start: utanför skolscope → ignorera med
     motivering; inom scope → åtgärda (registrera utredning/betänkande i
     utredningar.json) eller eskalera om utredningskopplingen inte kan
     verifieras direkt.
   - `regeringsuppdrag` — verifiera mot uppdragssidan på regeringen.se
     (källänken). Uppdrag med dnr och myndighet hör hemma i uppdrag.json
     enligt befintligt format. U-dep-uppdrag till andra myndigheter än
     Skolverket rapporteras också — scope är din bedömning; utanför →
     ignorera med motivering. Ändringsbeslut av spårade uppdrag flödar
     genom samma feed: uppdatera befintlig post, skapa inte dubblett.
   - `regleringsbrev` — verifiera mot rbid-sidan i statsliggaren
     (källänken, statskontoret.se). Delta-datum är beslutsdatum (ur
     titeln), inte publiceringsdatum — använd det. Ändringsbeslut
     ("Ändringsbeslut Myndighet ..." i titeln) uppdaterar befintliga
     uppdragsposter i uppdrag.json, skapar inte dubbletter; läs på
     rbid-sidan VAD som ändrats innan du rör datafilen.

4. **Bygg datapatchen** för alla åtgärda-deltan enligt reglerna i
   BEVAKNING.md. Rör bara fält som källorna styrker. Uppdatera även
   docs/CHANGELOG.md (en rad per logisk ändring).
   - **Bumpa färskhetsstämpeln (Sprint 12 T3):** varje datapatch som ändrar
     en fil i `data/` ska i SAMMA commit sätta `data/meta.json`
     `senast_uppdaterad` till patchens datum (beslutsdatum om ett enda
     styrande beslut, annars dagens patchdatum — var konsekvent, notera valet
     i changelog-raden). Stämpeln "Senast uppdaterad …" på alla publika sidor
     läser detta fält; en datapatch utan bump ljuger om aktualiteten.
   - **Logga ändringen (Sprint 12 T4):** varje åtgärda-delta som ändrar
     innehåll ska i SAMMA commit lägga en post överst i `data/andringar.json`
     (omvänt kronologisk — nyast först): `{datum, text, reform_ids, kalla}`.
     `datum` = beslutsdatum (samma konvention som seedningen). `text` =
     deskriptiv mening enligt språkregeln ("Riksdagen beslutade …",
     "Ikraftträdande uppdaterat till …") — ALDRIG rådgivande. `reform_ids`
     måste finnas i reforms.json (annars fail-loud i andringar.html-konsolen).
     `kalla` = samma primärkälla som styrkte deltat. Kan posten inte
     källbeläggas läggs den inte till.

5. **Visa diffen och fråga.** Presentera hela diffen (`git diff`) plus en
   tabell delta → klassning → motivering. Vänta på explicit ja innan något
   committas. Nej/ändringar → justera och visa igen.

6. **Avsluta.** Efter godkännande:
   - `./commit.sh "Bevakning v.<vecka>: <kort sammanfattning>"`
   - Kommentera issuet med triage-utfallet per delta (klassning + motivering
     + ev. eskaleringar), via `gh issue comment`
   - Stäng issuet: `gh issue close <nr>`
   - Påminn om att deltan med status åtgärdad nu ska försvinna ur nästa
     veckorapport — om samma delta återkommer är något fel (se Felsökning i
     BEVAKNING.md).
