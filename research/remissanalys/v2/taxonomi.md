# Taxonomi — Utmaningskartan v2 (pilot betyg)

Gäller `utmaningar-betyg-v2.json`. Taxonomin har två axlar som hålls isär: **utmaningstyp** (vad utmaningen består i) och **sakområde** (vilken del av betänkandet den gäller). Skolform är en tredje, mekanisk tagg.

## 1. Utmaningstyp (tolkning)

Exakt en primär typ per utmaning, valfritt en sekundär. Satt genom läsning av varje citat mot definitionerna nedan (modellkodning med gemensam instruktion), inte med nyckelordsregel. Märkt `utmaningstyp.tolkning: true`.

| Utmaningstyp | Definition |
|---|---|
| Kostnader och finansiering | utgifter, ersättning, finansieringsprincipen, resursbehov i pengar |
| Tidplan och reformtakt | ikraftträdande, förberedelsetid, samtidiga reformer |
| Personal, kompetens och arbetsbelastning | bemanning, kompetensutveckling, lärares och rektorers arbetsbörda |
| System och teknik | digitala system, provplattform, infrastruktur, utrustning |
| Organisation och planering | schemaläggning, lokaler, genomförande i verksamheten, samordning mellan enheter |
| Otydlighet i förslaget | oklara begrepp, oklart ansvar, oklar tillämpning |
| Likvärdighet och konsekvenser för elever | effekter för elevgrupper, rättssäkerhet, likvärdig bedömning |
| Övrigt | inget av ovanstående |

**Avgörande regel (Sprint 16 T3):** Citat vars huvudpoäng är att modellen, regleringen eller begreppen är svåra att förstå eller förklara kodas som Otydlighet i förslaget, även när elever eller vårdnadshavare nämns som de som ska förstå. Likvärdighet och konsekvenser för elever kräver att citatet beskriver en effekt för elever eller skilda utfall mellan elevgrupper, skolor eller huvudmän. Alla utmaningar med primär typ Otydlighet eller Likvärdighet har prövats mot regeln av en och samma kodare; ändringarna loggas i `andringslogg-utmaningstyp.json` och tillämpas i pilotens datafil (`pilot/utmaningar/data/utmaningar-betyg.json`). `utmaningar-betyg-v2.json` innehåller typerna före prövningen.

**Kopplingsnivåerna i pilotens datafil (Sprint 16 T3):** nivån `förslag` delas i `förslag` (hänvisningen pekar ut exakt ett utredningsförslag) och `avsnitt` (hänvisningen pekar ut ett SOU-avsnitt med flera förslag). Övriga nivåer är oförändrade.

Kodinstruktionen som användes ordagrant finns i `../skript/v2/INSTRUKTION.md`. Skolform och sakområde är uttryckligen inte typer.

## 2. Kopplingsnivå

| Nivå | Betydelse | Tolkning |
|---|---|---|
| `förslag` | Remissvaret anger själv avsnitt, paragraf eller rubrik (i texten eller som rubrik passagen står under) som motsvarar ett avsnitt med förslagsruta i SOU 2025:18. Kopplas till förslagen i det avsnittet och dess underavsnitt. `flera_forslag_i_hanvisat_avsnitt: true` när avsnittet innehåller mer än ett förslag. | nej |
| `kapitel` | Remissvaret anger bara kapitel, eller ett avsnitt som saknar förslagsruta (t.ex. konsekvensavsnitt). Kopplas till kapitlet; **ingen expansion** till förslagen i kapitlet. | nej |
| `tolkad` | Ingen egen hänvisning; koppling till 1–3 förslag gjord genom tolkning (modellkodning i förstudie 2, med motivering). | ja (`tolkning: true`) |
| `null` | Ingen koppling. | — |

Egen hänvisning i passagens text går före rubrikens hänvisning. Paragrafhänvisningar ("16 kap. 29 §") översätts till avsnitt via SOU:ns författningskommentar (avsnitt 22.1, "Bestämmelsen behandlas i avsnitt …").

## 3. Sakområde (mekaniskt)

Kapitelrubriken i SOU 2025:18, ordagrant ur innehållsförteckningen, för det eller de kapitel utmaningen är kopplad till (via förslaget eller kapitlet). `null` utan koppling.

## 4. Skolform (mekaniskt)

Taggas endast när citatet uttryckligen nämner skolformen, inklusive böjningsformer: förskoleklass, grundskola, anpassad grundskola, specialskola, sameskola, gymnasieskola, anpassad gymnasieskola, kommunal vuxenutbildning (även "komvux" och "vuxenutbildning"). "Anpassad grundskola/gymnasieskola" matchas före och ger inte samtidigt "grundskola/gymnasieskola". Synonymer som "gymnasiet" eller "högstadiet" taggas inte.

## 5. SFS-status per förslag (mekaniskt)

| Status | Betydelse |
|---|---|
| `i beslutad lag` | Förslagets paragrafer (via SOU:ns författningskommentar) har en beslutad lydelse i SFS 2026:1242/1243/1245. Textlikhet mot SOU:ns lydelse anges i procent per paragraf, med länk till den ordagranna diffen i `sfs-diff-betyg.json`. Säger inget om huruvida skillnaden är saklig eller redaktionell. |
| `ej i SFS per 2026-11-10` | Förslaget avser förordningsnivå; de berörda förordningarna innehåller inte den nya betygsskalan per hämtningsdatum. |
| `ej lagtext` | Förslaget är ett uppdrag eller myndighetsansvar, inte författningstext. |

Etiketterna "ändrad" och "oförändrad" från v1 används inte.

## 6. Vad som är tolkning

Endast `utmaningstyp` (alla) och `koppling` med `niva: "tolkad"`. Allt annat — citat, sida, URL, kopplingsnivå `förslag`/`kapitel`, sakområde, skolform, SFS-status, avsändarräkning och propositionens avvikelsetexter — är mekaniskt härlett ur källtext. Inget fält anger om en utmaning är löst, kvarstår eller tillräckligt bemött.
