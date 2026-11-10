# Sprint 16 task 2: Datagrund för Utmaningskartan (pilot betyg) — rapport

**Datum:** 2026-11-10 · **Status:** research, inte publik data
**Filer i `research/remissanalys/v2/`:**
- `utmaningar-betyg-v2.json` (steg 1–4 och 7)
- `avsandare-betyg.json` (steg 5)
- `avvikelser-betyg.json` (steg 6)
- `taxonomi.md`

**Skript och kodning:** `research/remissanalys/skript/v2/` innehåller instruktionen, den ordagranna kodningen och byggskripten.

V1-filerna är orörda. Citaten i v2 är identiska med v1 för alla 440 utmaningar (kontrollerat maskinellt).

---

## 1. Utmaningstyp

Alla 440 utmaningar kodades om genom läsning av varje citat mot de åtta definitionerna. Fyra modellkodare fick samma instruktionsfil (`skript/v2/INSTRUKTION.md`) och 110 utmaningar var. Varje utmaning har exakt en primär typ, och 162 har även en sekundär. Allt är märkt `tolkning: true`.

| Utmaningstyp (primär) | Avsändare | Passager | varav kommuner (avs.) | SKR | Almega | Idéburna |
|---|---|---|---|---|---|---|
| Organisation och planering | 21 | 105 | 19 | 1 | 1 | 0 |
| Tidplan och reformtakt | 24 | 70 | 21 | 1 | 1 | 1 |
| Otydlighet i förslaget | 23 | 66 | 21 | 1 | 0 | 1 |
| Personal, kompetens och arbetsbelastning | 22 | 63 | 20 | 0 | 1 | 1 |
| Likvärdighet och konsekvenser för elever | 18 | 55 | 15 | 1 | 1 | 1 |
| Kostnader och finansiering | 22 | 43 | 19 | 1 | 1 | 1 |
| System och teknik | 17 | 29 | 15 | 1 | 1 | 0 |
| Övrigt | 6 | 9 | 4 | 1 | 1 | 0 |
| **Totalt** | **28** | **440** | 25 | 1 | 1 | 1 |

- Enskilda huvudmän har **0** i alla celler. Deras fem remissvar är spontana yttranden som inte publiceras på regeringen.se.
- Rangordningen skiljer sig beroende på om man räknar avsändare eller passager. *Organisation och planering* har flest passager (105) men bara 21 avsändare. *Tidplan och reformtakt* når flest avsändare (24 av 28).

**Andel Övrigt:** 9 av 440 = **2,0 %**, under stoppgränsen på 10 %. Inga nya typer infördes.

**Samstämmighet mellan kodarna:**
- 40 slumpvis valda utmaningar (seed 20261111) kodades av en femte, oberoende kodare med samma instruktion.
- **35 av 40 (87,5 %) fick samma primära typ**, med Cohens kappa 0,85.
- I 39 av 40 fall är den ena kodarens primära typ den andras primära eller sekundära.
- De fem avvikelserna:

| Utmaning | Kodare A | Kodare B |
|---|---|---|
| U041 | Otydlighet | Tidplan |
| U251 | Kostnader | Organisation |
| U315 | Organisation | Tidplan |
| U392 | Övrigt | Personal |
| U444 | Tidplan | System |

**Systematisk skillnad mellan kodarna, som stickprovet inte fångar:** citat om att modellen är *svår att förstå eller förklara* fick olika typ beroende på batch.
- Kodare 1 satte 6 sådana citat som *Likvärdighet och konsekvenser för elever*.
- Kodare 2–4 satte 7 liknande citat som *Otydlighet i förslaget*.

Det påverkar fördelningen mellan de två typerna med ungefär 6 passager. Jag har inte rättat det i efterhand, eftersom det skulle kräva en ny läsning och inte en regel. Se risker.

## 2. Kopplingsnivå

| Nivå | Antal | Andel |
|---|---|---|
| förslag | 139 | 31,6 % |
| tolkad (`tolkning: true`) | 142 | 32,3 % |
| kapitel | 59 | 13,4 % |
| null | 100 | 22,7 % |

- **Ingen utmaning på kapitelnivå är kopplad till enskilda förslag** (0 av 59).
- På nivån `förslag` pekar 89 av 139 på ett avsnitt som innehåller fler än ett förslag (`flera_forslag_i_hanvisat_avsnitt: true`). Ett exempel är 10.1, med sju förslagsrutor. Remissvarets hänvisning pekar alltså ofta ut ett avsnitt snarare än ett enskilt förslag.
- Ett avsnitt utan förslagsruta, till exempel konsekvensavsnitt som 13.5.1, räknas som `kapitel`. Det är en egen hänvisning och därför inte tolkad.

## 3. Sakområde och skolform

**Sakområde** är SOU-kapitlets rubrik, ordagrant ur innehållsförteckningen. 340 utmaningar har sakområde och 100 saknar det (ingen koppling). Störst är:

| Sakområde | Utmaningar |
|---|---|
| Förslag på ändringar i det nationella provsystemet | 85 |
| Införande och ikraftträdande | 56 |
| Förslag på betygsmodell för kommunal vuxenutbildning på gymnasial nivå | 53 |
| Förslag på reglering av betygssättning | 45 |

Avsändarräkningen per sakområde och per kombination av typ och sakområde (66 kombinationer) finns i `avsandare-betyg.json`, med listor över avsändarna.

**Skolform** taggas mekaniskt bara när citatet uttryckligen nämner den:

| Skolform | Utmaningar |
|---|---|
| Kommunal vuxenutbildning | 48 |
| Gymnasieskola | 21 |
| Grundskola | 11 |
| Anpassad grundskola | 1 |
| Anpassad gymnasieskola | 1 |

Övriga 369 utmaningar nämner ingen skolform.

## 4. Propositionens avvikelsetexter

Jag gick igenom de 17 avsnitten i prop. 2025/26:197 som har en förslags- eller bedömningsruta, och de två avsnitten i prop. 2025/26:194 som behandlar förslag ur SOU 2025:18 (6.7 och 6.8).
- **Andel avsnitt med avvikelsetext: 19 av 19 (100 %).**
- Alla 19 stycken är kontrollerade automatiskt mot PDF-texten (pdftotext, med blanksteg och bindestreck normaliserade), och hela stycket hittades i samtliga.

| overensstammelse (exakt fras) | Antal |
|---|---|
| stämmer i huvudsak överens | 7 |
| stämmer också i huvudsak överens | 1 |
| stämmer överens | 6 |
| stämmer delvis överens | 5 |

`avvikelse_beskriven` är true för 13 avsnitt och false för 6. Den sätts mekaniskt till true när stycket har fler meningar än den inledande meningen om överensstämmelse. De sex med false är exakt de sex där frasen är "stämmer överens".

## 5. SFS

Diffarna från `sfs-diff-betyg.json` ligger kvar som belägg och länkas per paragraf som JSON-pekare. Statusetiketten per förslag är ersatt. 68 unika förslag är kopplade till minst en utmaning på nivån `förslag` eller `tolkad`.

| Status | Förslag |
|---|---|
| i beslutad lag (textlikhet i procent per paragraf + länk till diff) | 35 |
| ej i SFS per 2026-11-10 | 25 |
| ej lagtext | 8 |

Textlikheten mot SOU:ns lydelse har en median på 76,5 % per paragraf för de utmaningskopplade förslagen. Etiketterna "ändrad" och "oförändrad" används inte.

## 6. Ändringar mot v1

| Brist i v1 | Åtgärd i v2 |
|---|---|
| a. Kategorierna blandade utmaningstyp, sakområde och skolform och sattes med nyckelordsregel. | Tre separata axlar. Utmaningstypen är satt genom läsning (åtta givna typer), sakområde är SOU-kapitlets rubrik och skolform är en mekanisk tagg. |
| b. Kapitelhänvisningar expanderades till alla förslag i kapitlet. | Nivån `kapitel` kopplas bara till kapitlet. Förslagsnivån kräver ett avsnitt med förslagsruta, utan att falla tillbaka på överordnat avsnitt. |
| c. Räkningen avsåg passager. | `avsandare-betyg.json` räknar unika avsändare per typ, sakområde och kombination, totalt och per fokusgrupp. |
| d. SFS-etiketten "ändrad" gällde 92 av 93 paragrafer. | Ersatt med "i beslutad lag" plus textlikhet och diff-länk, "ej i SFS per 2026-11-10" och "ej lagtext". |

Övriga skillnader:
- Fältet `bemotande` från v1 är inte med i v2. Det byggde på v1:s koppling och skulle bli inaktuellt.
- Paragrafhänvisningar i remissvaren översätts fortfarande via SOU:ns författningskommentar.
- Den tolkade kopplingen återanvänds från förstudie 2, där en modell gjorde den med motivering.

## 7. Risker

1. **Kodarna drar olika gränser för vissa citat.** "Svår att förstå" hamnade under Likvärdighet hos en kodare och under Otydlighet hos de andra. Stickprovet med 87,5 % samstämmighet fångar inte sådana batchvisa mönster. Ett granskningsunderlag (task 5) bör rikta sig särskilt mot gränsen mellan Likvärdighet och Otydlighet, och mellan Organisation och Tidplan.
2. **Förslagsnivån är ofta avsnittsnivå.** 89 av 139 förankrade kopplingar pekar på avsnitt med flera förslag. Matrisen bör visa det, och inte låtsas att varje utmaning gäller ett enskilt förslag.
3. **Den tolkade kopplingen (142) och utmaningstypen (440) är modelltolkning.** Kopplingen har motivering men är inte granskad av människa.
4. **Avsändarräkningen visar bara de 28 avsändare som har publicerade svar.** Enskilda huvudmän saknas systematiskt (5 svar plus Almega utbildningsföretagen).
5. **Textlikhet i procent är inte ett mått på saklig ändring.** Den ska visas tillsammans med diffen och inte som en dom.
6. **`avvikelse_beskriven` är mekanisk** (fler än en mening). Den säger att stycket fortsätter, inte vad skillnaden består i.
7. **Byggskripten kräver den nedladdade korpusen och arbetsfilerna** (passager, förslagsrutor, innehållsförteckning) från förstudie 2. De kan inte köras fristående från repot. Task 3 behöver ett eget byggskript som läser enbart från incheckade filer.
