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

4. **Bygg datapatchen** för alla åtgärda-deltan enligt reglerna i
   BEVAKNING.md. Rör bara fält som källorna styrker. Uppdatera även
   docs/CHANGELOG.md (en rad per logisk ändring).

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
