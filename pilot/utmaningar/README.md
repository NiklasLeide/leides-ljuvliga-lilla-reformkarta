# Utmaningskartan, pilot betyg — datamodell

`data/utmaningar-betyg.json` visar vilka utmaningar huvudmän (kommuner, enskilda huvudmän) och deras organisationer (SKR, Almega, Idéburna skolors riksförbund) pekade ut i sina remissvar på SOU 2025:18. Filen kopplar också utmaningarna till propositionens avsnitt och till beslutad lag.

- **Status:** pilot, ogranskad. Hela `pilot/` är exkluderad från GitHub Pages (`_config.yml`).
- **Byggs med:** `python3 research/remissanalys/skript/bygg-pilot.py`, som bara läser incheckade filer och ger deterministisk utdata.
- **Valideras med:** `python3 research/remissanalys/skript/validera-pilot.py`.

## Principer

- **Källor:** citat är ordagranna ur remissvar och propositioner, och varje värde har källa i formatet `{text, url}`. Saknade uppgifter är `null`, inte uppskattningar.
- **Tolkning:** fält märkta `tolkning: true` är tolkning. Det gäller utmaningstyp och koppling på nivån `tolkad`.
- **Redaktionellt:** kopplingen mellan utredningsförslag och propositionsavsnitt är märkt `redaktionell: true`.
- **Allt annat** är mekaniskt härlett ur källtext.
- **Ingen bedömning:** inget fält anger om en utmaning har lösts eller om propositionen har bemött den i sak.

## Toppnivå

| Nyckel | Innehåll |
|---|---|
| `meta` | Reform, kedjan SOU 2025:18 → remiss U2025/00401 → Prop. 2025/26:197 (+ del av 2025/26:194) → bet. 2025/26:UbU26 → rskr. 2025/26:335 med källor, hämtningsdatum (2026-11-10), korpus (29 publicerade remissvar, 28 avsändare med utmaningar, 6 opublicerade remissvar som saknas och från vilka grupper), förklaring av kopplingsnivåerna |
| `utmaningstyper` | De åtta typerna med definition |
| `avgorande_regel` | Regeln som skiljer Otydlighet i förslaget från Likvärdighet och konsekvenser för elever |
| `sakomraden` | SOU 2025:18:s kapitel 9–20 med kapitelrubrik ordagrant ur innehållsförteckningen |
| `fokusgrupper` | Kommuner, enskilda huvudmän, SKR, Almega, Idéburna; `grupp` = huvudman eller huvudmannaorganisation |
| `avsandare` | 28 avsändare med fokusgrupp, länk till remissvaret (`remissvar`) och antal utmaningar |
| `utmaningar` | 440 utmaningar (se nedan) |
| `propositionsavsnitt` | 19 avsnitt (17 i prop. 197, 6.7–6.8 i prop. 194): rubrik, `overensstammelse` (propositionens exakta fras), `avvikelse_beskriven`, `avvikelsetext` (ordagrant stycke om utredningens förslag), sida, url, `kopplade_utredningsforslag` (`redaktionell: true`) |
| `utredningsforslag` | 80 förslagsrutor ur SOU 2025:18: text, SOU-avsnitt och sida, propositionsavsnitt (`redaktionell: true`), `sfs` |
| `lagparagrafer` | Paragrafer som förslagen gäller: SOU:ns lydelse, propositionens lydelse, beslutad lydelse (SFS, ikraftträdande), `textlikhet_procent`, ordagrann ord-diff, `manuell_granskning`, pekare till belägget i `sfs-diff-betyg.json` |
| `avsandarrakning` | Unika avsändare och antal utmaningar per utmaningstyp, per sakområde och per kombination av dem, totalt och per fokusgrupp med avsändarlistor |

## Utmaning

| Fält | Innehåll |
|---|---|
| `id`, `avsandare`, `fokusgrupp`, `grupp` | Identitet och avsändare |
| `citat`, `sida`, `url`, `ocr`, `kalla`, `citatkontroll` | Ordagrant citat ur remissvaret, sida, länk, om texten kommer från OCR, och hur citatet kontrollerats mot källan |
| `utmaningstyp` | `primar`, `sekundar`, `motivering`, `tolkning: true`, `regelprovad`, `andrad_vid_regelprovning` |
| `koppling` | `niva` (`förslag` = hänvisningen pekar ut exakt ett förslag; `avsnitt` = SOU-avsnitt med flera förslag; `kapitel` = bara kapitel, ingen expansion till förslag; `tolkad` = ingen egen hänvisning, `tolkning: true`; `null`), `forslag`, `sou_avsnitt`, `kapitel`, `grund`/`motivering` |
| `sakomrade` | SOU-kapitlets rubrik för kopplingen, eller `null` |
| `skolform` | Skolformer som citatet uttryckligen nämner (mekanisk matchning) |
| `namngivning_i_propositionen` | `null` när utmaningen inte via förslag, avsnitt eller tolkad koppling hör till ett propositionsavsnitt. Annars `namngiven` (bool), `propositionsavsnitt`, `traffar` (ordagrann mening, sida, del och källa för varje förekomst av avsändarens namn i avsnittets text) och `sokt_i`. I prop. 194 avsnitt 6.7–6.8 söks inte delarna om SOU 2025:19 (Läroplansutredningen). |

## SFS-status per utredningsförslag

| Status | Betydelse |
|---|---|
| `i beslutad lag` | Paragraferna finns i beslutad lydelse (SFS 2026:1242/1243/1245, skollagen konsoliderad, riksdagens öppna data). Textlikhet mot SOU:ns lydelse anges per paragraf, med diff i `lagparagrafer`. Textlikheten säger inget om huruvida skillnaden är saklig. |
| `ej i SFS per 2026-11-10` | Förslag på förordningsnivå som inte finns i SFS per hämtningsdatum. |
| `ej lagtext` | Uppdrag eller myndighetsansvar. |
| `null` med `forklaring` | Inte undersökt. Förslaget hade ingen kopplad utmaning i förstudie 2. |

## Underlag

Byggskriptet läser följande filer:
- `research/remissanalys/v2/` (utmaningar v2, ändringslogg för steg 1, avvikelsetexter)
- `research/remissanalys/pilot-betyg.json`
- `research/remissanalys/sfs-diff-betyg.json`
- `research/remissanalys/kedjor.json`
- `research/remissanalys/utmaningar-betyg.json` (opublicerade remissvar)
- `research/remissanalys/arbetsfiler/`: byggskriptet läser `propositionsavsnitt-text.json` och `sou-innehall.json`. Katalogen innehåller också `propositioner-innehall.json`, som `validera-pilot.py` läser, och `passager-forstudie2.json`, som `skript/v2/bygg-granskning.py` läser.

Metod och begränsningar beskrivs i `research/remissanalys/v2/taxonomi.md` och `RAPPORT-datagrund.md`.
