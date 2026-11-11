# Utmaningskartan, pilot (sju reformer) — datamodell

`data/` har en datafil per reform och en översikt:

| Fil | Reform | SOU |
|---|---|---|
| `utmaningar-betyg.json` | Ett likvärdigt betygssystem | SOU 2025:18 |
| `utmaningar-studiero.json` | Bättre förutsättningar för trygghet och studiero i skolan | SOU 2025:8 |
| `utmaningar-stod.json` | Förbättrat stöd i skolan | SOU 2025:44 |
| `utmaningar-tid.json` | Tid för undervisningsuppdraget | SOU 2025:26 |
| `utmaningar-laroplaner.json` | Kunskap för alla – nya läroplaner | SOU 2025:19 |
| `utmaningar-spraklig.json` | På språklig grund | SOU 2025:9 |
| `utmaningar-tioarig.json` | En tioårig grundskola | SOU 2021:33 |
| `oversikt.json` | Startvyns jämförelse, byggd ur de sju filerna | |

Varje datafil visar vilka utmaningar huvudmän (kommuner, enskilda huvudmän) och deras organisationer pekade ut i sina remissvar på utredningen. Organisationerna är SKR, Almega och Idéburna skolors riksförbund, och för tioarig Friskolornas riksförbund i stället för Almega. Filen kopplar också utmaningarna till propositionens avsnitt och till beslutad lag.

- **Status:** pilot, ogranskad. Hela `pilot/` är exkluderad från GitHub Pages (`_config.yml`).
- **Metod:** `docs/utmaningskartan-metod.md`. Kedjan och kommandona står i `research/remissanalys/KEDJA.md`.

## Bygga och validera

Kör från repo-roten. `<id>` är `betyg`, `studiero`, `stod`, `tid`, `laroplaner`, `spraklig` eller `tioarig`.

```bash
python3 research/remissanalys/kedja/kor.py <id>               # bygger data/utmaningar-<id>.json (kedjans steg K6–K10)
python3 research/remissanalys/kedja/oversikt.py               # efter alla sju: bygger data/oversikt.json
python3 research/remissanalys/skript/validera-pilot.py <id>   # validerar datafilen (kod 1 = fel)
node research/remissanalys/skript/testa-pilotsida.js          # headless-test av sidan, alla sju reformer, 1280 och 375 px
```

- **Bara incheckade filer:** byggena läser bara incheckade filer under `research/remissanalys/reformer/<id>/`, reformens config `reformer/<id>.json` och `kedja/gemensamt.json`.
- **Deterministiskt:** utdatan har inga tidsstämplar, så ett bygge från en ren utcheckning ger identiska filer.
- **`meta.byggd_av`** är `research/remissanalys/kedja/bygg.py` i alla sju filer. `skript/bygg-pilot.py` finns kvar som omslag för `kor.py betyg`.

## Principer

- **Källor:** citat är ordagranna ur remissvar och propositioner, och varje värde har källa i formatet `{text, url}`. Saknade uppgifter är `null`, inte uppskattningar.
- **Tolkning:** fält märkta `tolkning: true` är tolkning. Det gäller utmaningstyp och koppling på nivån `tolkad`.
- **Redaktionellt:** kopplingen mellan utredningsförslag och propositionsavsnitt är märkt `redaktionell: true`.
- **Allt annat** är mekaniskt härlett ur källtext.
- **Ingen bedömning:** inget fält anger om en utmaning har lösts eller om propositionen har bemött den i sak.
- **Ingen fritext om begränsningar:** begränsningar lagras som koder med parametrar (`meta.begransningar`). Sidan visar en fast text per kod.

## Toppnivå i en datafil

| Nyckel | Innehåll |
|---|---|
| `meta` | Se nästa tabell |
| `utmaningstyper` | De åtta typerna med definition (`namn`, `definition`), lika i alla filer |
| `avgorande_regel` | Regeln som skiljer Otydlighet i förslaget från Likvärdighet och konsekvenser för elever |
| `sakomraden` | SOU:ns kapitel inom `sou.forslagskapitel` med kapitelrubrik ordagrant ur innehållsförteckningen (`kapitel`, `rubrik`, `kalla`) |
| `fokusgrupper` | `gemensamt.json`:s fem fokusgrupper plus reformens `extra_fokusgrupper` (tioarig: `friskolornas`); `grupp` = huvudman eller huvudmannaorganisation |
| `avsandare` | Avsändare med minst en utmaning: fokusgrupp, länk till remissvaret (`remissvar`) och antal utmaningar |
| `utmaningar` | Utmaningarna, utan dubbletter (se nedan) |
| `propositionsavsnitt` | Propositionsavsnitt (`ref` = `"<kort>:<avsnitt>"`): rubrik, `overensstammelse` (propositionens formulering som den står), `avvikelse_beskriven`, `avvikelsetext` (ordagrant stycke om utredningens förslag), sida, url, `kopplade_utredningsforslag` (`redaktionell: true`) |
| `utredningsforslag` | Förslagsrutor ur SOU:n: text, SOU-avsnitt med rubrik och sida, `propositionsavsnitt` (`refs`, `matchning`, `grund`, `redaktionell: true`), `sfs` |
| `lagparagrafer` | Objekt med paragrafbeteckningen som nyckel: SOU:ns lydelse, propositionens lydelse, beslutad lydelse (SFS, ikraftträdande), `textlikhet_procent`, ordagrann ord-diff, `manuell_granskning`, `belagg` (pekare till `research/remissanalys/reformer/<id>/sfs-diff.json`). Tomt för tioarig. |
| `avsandarrakning` | Unika avsändare och antal utmaningar per utmaningstyp, per sakområde, utan sakområde och per kombination av dem, totalt och per fokusgrupp med avsändarlistor |

Antal per fil:

| Reform | `utmaningar` | `avsandare` | `propositionsavsnitt` | `utredningsforslag` | `lagparagrafer` | `sakomraden` |
|---|---|---|---|---|---|---|
| betyg | 490 | 28 | 19 | 80 | 95 | 12 |
| studiero | 257 | 22 | 12 | 8 | 21 | 3 |
| stod | 395 | 21 | 9 | 9 | 13 | 2 |
| tid | 615 | 26 | 5 | 20 | 19 | 5 |
| laroplaner | 284 | 24 | 13 | 12 | 53 | 8 |
| spraklig | 140 | 17 | 3 | 13 | 8 | 12 |
| tioarig | 166 | 18 | 7 | 55 | 0 | 3 |

## meta

| Fält | Innehåll |
|---|---|
| `reform` | `id` och `namn` |
| `kedja` | SOU → remiss (diarienummer, datum) → proposition(er) (lista, med `anm` om delade propositioner) → utskottsbetänkande → rskr (nummer, beslutsdatum, status "inträffat"), varje led med källa |
| `hamtningsdatum` | Datum då källorna hämtades (2026-11-10 i alla sju) |
| `korpus` | `publicerade_remissvar`, `avsandare_med_utmaningar`, `utmaningar`, `beskrivning`, och `opublicerade_remissvar_som_saknas` (`antal`, `per_grupp`, `avsandare` med skäl och källa i förteckningen) |
| `organisationer` | Reformens fokusorganisationer (config `fokusorganisationer`; null tas inte med). Varje post har `id`, `namn`, `status` ur förteckningen och `kalla`. Status kan vara `svarat`, `spontant yttrande`, `avstått` (med `avstaende`: citat och källa ur det publicerade brevet), `på remisslistan utan svar` (med `anm`) eller `inte på remisslistan`. |
| `kodning` | `samstammighet_identifiering` och `samstammighet_typning` (`overens`, `antal`; 40 i båda) och `instruktion` (`research/remissanalys/kedja/KODINSTRUKTION.md`). Betyg har också `samstammighet_typning_efter_regelprovning` (71 av 80, regel A4). Finns ingen oberoende identifiering blir måttet `null` och `anm` förklarar. |
| `begransningar` | Lista med koder och parametrar, till exempel `{"kod": "delad_proposition", "propositioner": [...]}`. Koderna är `omkodad`, `delad_proposition`, `spontana_ej_publicerade`, `grova_forslagsrutor`, `forordning_ej_jamford`, `skolfs_ej_jamford`, `lag_utan_andring`, `beslutad_lydelse_saknas`, `samordnad_lag`, `ingen_paragraftext`, `egen_fokusgrupp` och `aldre_remiss`. Texterna står i `index.html` (`BEGR`). |
| `publicerade_avstaenden` | Dokument på remissidan som lästs vid remissidekontrollen och är rena avståenden: avsändare, fokusgrupp, förteckningens uppgift, ordagrann mening, källa. 7 totalt: stod 2, tid 1, spraklig 2, tioarig 2; tom lista för övriga. |
| `remissida_kontroll` | `datum` (2026-11-11) och `regel` för kontrollen av publicerade yttranden utanför korpusen (Sprint 17 A2). Detaljerna, inklusive `tillagda_yttranden` (tom i alla sju), står i reformens config. |
| `tolkning`, `ingen_bedomning` | Fasta texter om vad som är tolkning och att inget fält bedömer om en utmaning är löst |
| `kopplingsnivaer` | Förklaring av kopplingsnivåerna |
| `byggd_av` | `research/remissanalys/kedja/bygg.py` |

## Utmaning

| Fält | Innehåll |
|---|---|
| `id`, `avsandare`, `fokusgrupp`, `grupp` | Identitet och avsändare |
| `citat`, `sida`, `url`, `ocr`, `kalla`, `citatkontroll` | Ordagrant citat ur remissvaret, sida, länk, om texten kommer från OCR, och hur citatet kontrollerats mot källan (`metod`, `ok`) |
| `utmaningstyp` | `primar`, `sekundar`, `motivering`, `tolkning: true`, `regelprovad`, `andrad_vid_regelprovning` |
| `koppling` | `niva` (`förslag` = hänvisningen pekar ut exakt ett förslag; `avsnitt` = SOU-avsnitt med flera förslag; `kapitel` = bara kapitel, ingen expansion till förslag; `tolkad` = ingen egen hänvisning, `tolkning: true`; `null`), `forslag`, `sou_avsnitt`, `kapitel`, `grund`/`kalla_for_grund` eller `motivering` |
| `sakomrade` | SOU-kapitlets rubrik för kopplingen, eller `null` |
| `skolform` | Skolformer som citatet uttryckligen nämner (mekanisk matchning) |
| `namngivning_i_propositionen` | `null` när utmaningen inte via förslag, avsnitt eller tolkad koppling hör till ett propositionsavsnitt. Annars innehåller fältet `namngiven` (bool), `propositionsavsnitt`, `traffar` och `sokt_i`. `traffar` har ordagrann mening, sida, del och källa för varje förekomst av avsändarens namn i avsnittets text. I delade propositioner söks inte andra utredningars delar (config `propositioner[].hoppa_delar_vid_namnsokning`, beskrivet i `sokt_i`). |

## SFS-status per utredningsförslag (`utredningsforslag[].sfs`)

| Status | Betydelse |
|---|---|
| `i beslutad lag` | Alla förslagets paragrafer har beslutad lydelse från reformens egna SFS-nummer (config `lagar[].andringar`). Textlikhet mot SOU:ns lydelse anges per paragraf, med diff i `lagparagrafer`. Textlikheten säger inget om huruvida skillnaden är saklig. |
| `ej i SFS per 2026-11-10` | Förordningsförslag där reformens textmarkör (config `forordning_markor`) saknar träffar i de konsoliderade förordningarna. Gäller bara betyg och studiero. |
| `ej lagtext` | Uppdrag eller myndighetsansvar. |
| `null` med `forklaring` | Förslaget kan inte avgöras maskinellt. Det gäller i fyra fall: minst en paragraf saknar beslutad lydelse från reformens SFS-nummer; förordningsförslag utan avgörande markör; SOU:n återger inte paragraftexten (tioarig); inga förordningar att jämföra med. |

## oversikt.json

Byggs av `research/remissanalys/kedja/oversikt.py` ur de sju datafilerna i fast ordning (betyg, studiero, stod, tid, laroplaner, spraklig, tioarig). Skriptet stoppar om en fils `meta.reform.id` eller utmaningstyper avviker. Filen är deterministisk.

| Nyckel | Innehåll |
|---|---|
| `_meta` | `beskrivning` och `källa` (de sju datafilerna) |
| `reformer` | Per reform: `id`, `namn`, `sou`, `fil`, `totalt_avsandare`, `utmaningar` och `per_utmaningstyp` (antal avsändare per primär typ, ur `avsandarrakning`) |
| `utmaningstyper` | De åtta typnamnen i datafilernas ordning |

## Underlag

`kedja/bygg.py` läser för varje reform:
- config `research/remissanalys/reformer/<id>.json`
- `research/remissanalys/kedja/gemensamt.json`
- under `research/remissanalys/reformer/<id>/`:
  - `utmaningar.json`
  - `sfs-diff.json`
  - `avvikelser.json`
  - `sou-forslag.json`
  - `sou-innehall.json`
  - `propositionsavsnitt-text.json`
  - `remissvar.json`
  - `forslag-propositionsavsnitt.json`
  - `kodning/`

Sprint 16:s betygsfil och kodning finns i `research/remissanalys/reformer/betyg/fore-omkodning/`, med `jamforelse.json`.
