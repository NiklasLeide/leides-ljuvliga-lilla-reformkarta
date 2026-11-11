# Utmaningskartan — metod (pilot, sju reformer)

Sprint 16 byggde piloten för betyg. Sprint 17 förde ut samma låsta metod till sju reformer genom en parametrisk kedja. Sidan heter `pilot/utmaningar/index.html`. Data ligger i `pilot/utmaningar/data/`, med en datafil per reform (`utmaningar-<id>.json`) och en översikt (`oversikt.json`). Datamodellen beskrivs i `pilot/utmaningar/README.md`, och kedjans steg och kommandon i `research/remissanalys/KEDJA.md`.

Utmaningskartan visar vilka utmaningar huvudmännen och deras organisationer pekade ut i sina remissvar på en utredning. Den visar också vad proposition och lag säger om de förslag som utmaningarna gällde.

| Id | Reform |
|---|---|
| `betyg` | Ett likvärdigt betygssystem |
| `studiero` | Bättre förutsättningar för trygghet och studiero i skolan |
| `stod` | Förbättrat stöd i skolan |
| `tid` | Tid för undervisningsuppdraget – åtgärder för god undervisning och läraryrkenas attraktivitet |
| `laroplaner` | Kunskap för alla – nya läroplaner med fokus på undervisning och lärande |
| `spraklig` | På språklig grund (har inget id i `data/reforms.json`) |
| `tioarig` | En tioårig grundskola – Införandet av en ny årskurs 1 i grundskolan, grundsärskolan, specialskolan och sameskolan |

## 1. Källor och kedja

Kedjan per reform står i `research/remissanalys/reformer/<id>.json` (`kedja`, `propositioner`, `lagar`) och följer med till datafilens `meta.kedja`.

| Reform | SOU | Remiss | Proposition(er) och avsnitt som ingår | Bet. | Rskr. (beslut) |
|---|---|---|---|---|---|
| betyg | SOU 2025:18 | U2025/00401 | Prop. 2025/26:197 (alla avsnitt). Prop. 2025/26:194 avsnitt 6.7–6.8 (SOU 2025:18 avsnitt 9.3–9.4) | 2025/26:UbU26 | 2025/26:335 (2026-06-09) |
| studiero | SOU 2025:8 | U2025/00202 | Prop. 2025/26:193 avsnitt 6.1, 6.2.1, 6.2.2, 6.4.1, 6.4.2, 7.1–7.5 och 8. Prop. 2025/26:194 avsnitt 6.2 (SOU 2025:8 avsnitt 3.2) | 2025/26:UbU22 | 2025/26:308 (2026-06-03) |
| stod | SOU 2025:44 | U2025/01067 | Prop. 2025/26:195 avsnitt 6.1–6.3, 6.5–6.9 och 8 | 2025/26:UbU24 | 2025/26:328 (2026-06-03) |
| tid | SOU 2025:26 | U2025/00740 | Prop. 2025/26:196 (alla avsnitt) | 2025/26:UbU25 | 2025/26:332 (2026-06-09) |
| laroplaner | SOU 2025:19 | U2025/00630 | Prop. 2025/26:194 avsnitt 6.1, 6.2, 6.3.2, 6.4–6.8 och 8. Prop. 2025/26:195 avsnitt 6.4 och 8. Prop. 2025/26:196 avsnitt 8 och 9 | 2025/26:UbU23 | 2025/26:327 (2026-06-03) |
| spraklig | SOU 2025:9 | U2025/00233 | Prop. 2025/26:194 avsnitt 7.1, 7.2 och 8 (bara betänkandets avsnitt 8 behandlas) | 2025/26:UbU23 | 2025/26:327 (2026-06-03) |
| tioarig | SOU 2021:33 | U2021/02645 | Prop. 2024/25:143 avsnitt 6.1–6.3, 6.4.2, 6.5, 7.2 och 10 | 2024/25:UbU17 | 2024/25:289 (2025-06-18) |

- **Delade propositioner:** prop. 2025/26:194 behandlar delar av fyra av utredningarna (betyg, studiero, laroplaner, spraklig). Prop. 2025/26:195 och 196 behandlar också delar av SOU 2025:19. Prop. 2025/26:193 behandlar även Ds 2025:9. I varje delad proposition tas bara utredningens egna avsnitt med. Vid namnsökningen hoppas andra utredningars delar över (config `propositioner[].hoppa_delar_vid_namnsokning`).
- **Remissförteckning:** propositionens bilaga med förteckningen över remissinstanserna. För spraklig är det prop. 2025/26:194 bilaga 12, för övriga bilaga 3 i reformens proposition.
- **Beslut:** beslutsaktiviteten med status "inträffat" i riksdagens dokumentstatus för betänkandet.
- **Hämtning:** källorna hämtades 2026-11-10 (`hamtningsdatum`). SFS-beläggen (A1) och remissidekontrollen (A2) gjordes 2026-11-11.

### SFS-nummer per reform

Riksdagens dokumentstatus för UbU17 och UbU22–UbU26 anger inga SFS-nummer. Ändrings-SFS i original (svenskforfattningssamling.se) och SFS-registret gick inte att nå från arbetsmiljön. Kopplingen mellan SFS-nummer och riksdagsbeslut har därför härletts på tre sätt (Sprint 17 A1):

1. ur raderna "Lag (…)", ikraftträdandedagarna och övergångsblocken i den konsoliderade lagtexten (riksdagens öppna data)
2. ur betänkandets beslutstext
3. ur propositionens lagförslag (paragrafuppsättning och ikraftträdande).

Varje nummer har sitt belägg i config `lagar[].andringar_kalla` (`sfs`, `prop`, `text`, `url`). Nummer som inte kan beläggas tas inte med, och skälet står i `lagar[].andringar_anm`.

| Reform | Lag | Reformens SFS-nummer | Anmärkning |
|---|---|---|---|
| betyg | Skollagen | 2026:1242, 2026:1243, 2026:1244, 2026:1245 | 2026:1244 tillkom i A1 (prop. 197 lagförslag 2.2, i kraft 2030-07-01). 2026:1242 är i huvudsak prop. 195 men bär prop. 194:s ändring av 3 kap. 2 § (avsnitt 6.7). |
| studiero | Skollagen | 2026:1198, 2026:1243 | 2026:1198 = prop. 193. Av 2026:1243 genomför bara 4 kap. 12 § (prop. 194 avsnitt 6.2) SOU 2025:8. |
| stod | Skollagen | 2026:1242 | Lagen antogs genom UbU26 (samordnad), inte i UbU24. |
| tid | Skollagen | 2026:1096, 2026:1097, 2026:1243 | Lagförslag 2.3 antogs formellt genom UbU26 och ingår i 2026:1243. |
| tid | Diskrimineringslagen | inga | Förslaget genomfördes inte (`andringar: []`). |
| laroplaner | Skollagen | 2026:1096, 2026:1242, 2026:1243, 2026:1245 | 2026:1245 tillkom och 2026:1636 togs bort i A1. 2026:1636 genomför ett annat beslut, och därför saknar 1 kap. 3 § beslutad lydelse. |
| spraklig | Skollagen | 2026:1243 | 2026:1242 och 2026:1245 tas inte med, eftersom deras paragrafer i prop. 194 hör till andra avsnitt än avsnitt 7. |
| tioarig | Skollagen | 2025:729, 2025:730 | 2025:730 tillkom i A1 (utskottets lagförslag 2 i UbU17, 6 a kap.). |
| tioarig | Offentlighets- och sekretesslagen | 2025:737 | 23 kap. 2 §. |

## 2. Fokusgrupper och korpus

- **Fokusgrupper** (låsta i `kedja/gemensamt.json`): kommuner och enskilda huvudmän (gruppen *huvudman*) samt SKR, Almega och Idéburna skolors riksförbund (gruppen *huvudmannaorganisation*). De två grupperna hålls isär i all data.
- **Organisationernas namn per remiss** står i config `fokusorganisationer`. För tioarig är `almega` null, och Friskolornas riksförbund är egen fokusgrupp (config `extra_fokusgrupper`). Remisslistan från 2021 har Friskolornas riksförbund och inte Almega. `gemensamt.json` ändras inte, och organisationer med olika namn likställs inte.
- **Korpus:** publicerade remissvar på regeringen.se från fokusgrupperna. Spontana yttranden publiceras inte ("Övriga yttranden finns tillgängliga i departementet") och har inte hämtats från andra källor.

| Reform | Publicerade remissvar | Avsändare med utmaningar | Utmaningar | Opublicerade (saknas) |
|---|---|---|---|---|
| betyg | 29 | 28 | 490 | 6: 5 enskilda huvudmän, 1 Almega |
| studiero | 24 | 22 | 257 | 3: 2 enskilda huvudmän, 1 kommun |
| stod | 21 | 21 | 395 | 2: 2 enskilda huvudmän |
| tid | 27 | 26 | 615 | 6: 4 enskilda huvudmän, 2 kommuner |
| laroplaner | 24 | 24 | 284 | 5: 4 enskilda huvudmän, 1 kommun |
| spraklig | 20 | 17 | 140 | 2: 2 enskilda huvudmän |
| tioarig | 22 | 18 | 166 | 1: 1 kommun |
| **Summa** | **167** | **156** | **2 347** | **25** |

- Enskilda huvudmän saknas därför helt bland avsändarna i alla sju reformer.
- I spraklig kommer de publicerade svaren bara från kommuner och SKR (Almega avstod med ett publicerat brev, och Idéburna står på remisslistan utan svar). I tioarig har Friskolornas riksförbund inget publicerat svar.
- **Organisationernas status** (`meta.organisationer`) hämtas ur förteckningen och kan vara: svarat, spontant yttrande, avstått (publicerat avståendebrev), på remisslistan utan svar (förteckningen skiljer inte mellan avstått och inte inkommit) eller inte på remisslistan.
- **OCR:** två remissvar är inskannade och OCR-tolkade: Norrköpings kommun (betyg, 11 citat) och Åre kommun (tid, 25 citat). Citaten är märkta `ocr: true` och är automatiskt kontrollerade mot OCR-texten.

### Remissidekontroll (A2)

Publicerade dokument på remissidan från fokusgrupper som enligt förteckningen inte ingår i korpusen lästes 2026-11-11 för alla sju reformer. Regeln: ett yttrande med sakinnehåll ska ingå även om förteckningen anger att instansen avstått, medan rena avståendebrev inte ingår.

- **Utfall:** 7 dokument lästes. Alla var avståenden, och inget lades till.
  - stod: Ale kommun och Ystad kommun. Ale kommuns dokument är rubricerat "Yttrande", men övrig text är ett referat av betänkandet.
  - tid: Bromölla kommun.
  - spraklig: Almega Utbildning och Mullsjö kommun.
  - tioarig: Härryda kommun och Mörbylånga kommun.
- **Var det redovisas:** i config `remissida_kontroll`, som har `datum`, `regel`, `tillagda_yttranden` och `ej_med_avstaenden` med ordagrann mening och källa. I datafilen står det i `meta.remissida_kontroll` (datum och regel) och `meta.publicerade_avstaenden`.

## 3. Från remissvar till datafil

Kedjan är densamma för alla reformer (`research/remissanalys/kedja/`, steg K1–K13 med reformens id som argument; se `KEDJA.md`).

1. **Källor (K1–K5):** SOU:ns förslagsrutor, författningskommentar och innehållsförteckning, propositionernas avsnitt och lagförslag, konsoliderade lagar och förordningar samt remissvaren med förteckningen. Allt extraheras till incheckade mellanfiler under `research/remissanalys/reformer/<id>/`. De nedladdade källorna (`kallor/`) checkas inte in.
2. **Segmentering (K6):** remissvaren delas i passager med avsändare, sida och URL.
3. **Modellkodning (M1–M3)** enligt en enda instruktion för alla reformer, `research/remissanalys/kedja/KODINSTRUKTION.md`:
   - M1 identifierar utmaningar med ordagrant citat.
   - M2 sätter utmaningstyp.
   - M2c regelprövar.
   - M3 gör tolkad koppling när remissvaret saknar egen hänvisning.

   Underlag och sammanslagning görs med `kedja/kodning.py`, och kodningen checkas in under `reformer/<id>/kodning/`.
4. **Redaktionell koppling (R1):** varje utredningsförslag matchas mot de propositionsavsnitt som behandlar det. Propositionen anger inte vilka SOU-förslag den avser, så matchningen är redaktionell.
5. **Utmaningar (K7):**
   - Varje citat kontrolleras mot källsidans text.
   - Dubbletter inom samma avsändare markeras.
   - Kopplingsnivå och skolform härleds mekaniskt.
6. **SFS-jämförelse (K8):** se avsnitt 7.
7. **Propositionens avvikelsetexter (K9):** stycket om utredningens förslag tas ordagrant, med propositionens formulering om överensstämmelse fångad som den står (A3). Exempel: "stämmer i huvudsak överens", "stämmer inte överens", "överensstämmer i sak", "Överensstämmer huvudsakligen".
8. **Namngivning (K10):** för utmaningar som hör till ett propositionsavsnitt söks avsändarens namn i avsnittets text. Sökningen fångar fullt namn, kortform (SKR) och samordnade kommunuppräkningar.
9. **Bygge och kontroll (K10–K13):**
   - `kedja/bygg.py` sätter ihop datafilen.
   - `kedja/stoppregler.py` prövar stoppreglerna.
   - `skript/validera-pilot.py <id>` validerar datafilen.
   - `skript/testa-pilotsida.js` testar sidan.

   Därefter bygger `kedja/oversikt.py` översikten ur alla sju datafiler.

Antal per reform efter K7, med dubbletter borträknade:

| Reform | Passager | Utmaningar före dubblettrensning | Utmaningar | Utredningsförslag | Propositionsavsnitt |
|---|---|---|---|---|---|
| betyg | 714 | 514 | 490 | 80 | 19 |
| studiero | 464 | 263 | 257 | 8 | 12 |
| stod | 361 | 413 | 395 | 9 | 9 |
| tid | 648 | 649 | 615 | 20 | 5 |
| laroplaner | 575 | 300 | 284 | 12 | 13 |
| spraklig | 332 | 155 | 140 | 13 | 3 |
| tioarig | 389 | 174 | 166 | 55 | 7 |

Alla citat i de sju datafilerna har `citatkontroll.ok = true` (automatiskt mot pdftotext-sidtext eller OCR-text). Inga citat är manuellt kontrollerade.

## 4. Vad som är tolkning

| Fält | Hur det tagits fram | Märkning |
|---|---|---|
| Att en passage är en utmaning | Modellkodning (M1) | Hela korpusen. Granskas i `research/remissanalys/granskning/` |
| Utmaningstyp (primär, sekundär) | Modellkodning genom läsning mot definitionerna (M2, M2c) | `tolkning: true` |
| Koppling med nivån `tolkad` | Modellkodning när remissvaret saknar egen hänvisning (M3) | `tolkning: true` |
| Koppling mellan utredningsförslag och propositionsavsnitt | Redaktionell matchning (R1) | `redaktionell: true`, visas som "Reformkartans koppling" |

Resten är mekaniskt härlett ur källtext:
- citat, sida och URL
- kopplingsnivåerna `förslag`, `avsnitt` och `kapitel` (remissvarets egen hänvisning)
- sakområde och skolform
- propositionens avvikelsetexter och formuleringen om överensstämmelse
- SFS-status och textlikhet
- namnträffar
- avsändarräkning
- organisationernas status

Kodarnas motiveringar finns i datafilen som spårbarhet men visas aldrig på sidan. Begränsningarna lagras som koder (se avsnitt 10), inte som fritext.

## 5. Taxonomi och avgörande regel

Taxonomin, regeln och kopplingsnivåerna är låsta i `kedja/gemensamt.json` och gemensamma för alla reformer.

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

Varje utmaning får exakt en primär typ och valfritt en sekundär.

**Avgörande regel:** Citat vars huvudpoäng är att modellen, regleringen eller begreppen är svåra att förstå eller förklara kodas som Otydlighet i förslaget, även när elever eller vårdnadshavare nämns som de som ska förstå. Likvärdighet och konsekvenser för elever kräver att citatet beskriver en effekt för elever eller skilda utfall mellan elevgrupper, skolor eller huvudmän.

**Kopplingsnivåer:**

| Nivå | Betydelse |
|---|---|
| `förslag` | Remissvarets hänvisning pekar ut exakt ett förslag |
| `avsnitt` | Hänvisningen pekar ut ett SOU-avsnitt med flera förslag |
| `kapitel` | Remissvaret anger bara kapitel (eller avsnitt utan förslagsruta). Ingen expansion till enskilda förslag |
| `tolkad` | Ingen egen hänvisning; koppling genom tolkning |
| `null` | Ingen koppling |

**Sakområde** är SOU-kapitlets rubrik, ordagrant ur innehållsförteckningen (kapitlen i config `sou.forslagskapitel`).

## 6. Kodning, samstämmighet och stoppregler

- **Instruktion:** `research/remissanalys/kedja/KODINSTRUKTION.md` (M1–M3, R1) gäller alla reformer. Kodningsmåtten står i datafilens `meta.kodning`.
- **Dubbelkodning av identifiering (M1b):** 40 slumpvis valda passager om minst 100 tecken identifieras av en oberoende kodare. Kodarna räknas som överens när båda anger minst en utmaning i passagen, eller ingen av dem.
- **Dubbelkodning av typning (M2b):** 40 slumpvis valda utmaningar typas av en oberoende kodare. Måttet är samma primära typ som ordinarie kodning före regelprövning.
- **Regelprövning (M2c):** en kodare prövar alla utmaningar med typen Otydlighet eller Likvärdighet mot den avgörande regeln.

| Reform | Identifiering | Typning (40) | Regelprövning: prövade/ändrade | Övrigt |
|---|---|---|---|---|
| betyg | 35/40 | 31/40; efter regelprövning 71/80 (regel A4) | 155/1 | 4/490 = 0,8 % |
| studiero | 37/40 | 35/40 | 100/0 | 18/257 = 7,0 % |
| stod | 39/40 | 35/40 | 122/1 | 9/395 = 2,3 % |
| tid | 37/40 | 35/40 | 159/0 | 29/615 = 4,7 % |
| laroplaner | 39/40 | 36/40 | 106/2 | 22/284 = 7,7 % |
| spraklig | 38/40 | 38/40 | 40/0 | 5/140 = 3,6 % |
| tioarig | 36/40 | 34/40 | 27/1 | 0/166 = 0 % |

**Stoppregler** (`kedja/stoppregler.py <id>`, gränser i `gemensamt.json`):
- **Stopp:** Övrigt över 10 % av utmaningarna, räknat på primär typ efter regelprövning och utan dubbletter.
- **Stopp:** samstämmighet i typning (M2b) under 80 %, utom för betyg (se nedan).
- **Stopp:** typnamn som inte är de åtta.
- **Flaggas men stoppar inte:** samstämmighet i identifiering under 80 %, och färre än fem publicerade remissvar från fokusgrupperna.
- **Ingen omkodning för att klara gränserna.** Avvikelser rapporteras.

Alla sju reformer klarar stoppreglerna utan flaggor (körning 2026-11-11).

### Ändrad regel för betyg (Sprint 17 A4)

Betyg kodades i Sprint 16 med andra instruktioner. Sprint 16 gav 440 utmaningar, typning 35/40, och regelprövningen ändrade 11 av 121. I Sprint 17 kodades betyg om från M1 med den gemensamma instruktionen.

1. **T7b:** M1 gav 514 utmaningar, eller 490 efter dubblettrensning. Identifieringen blev 35/40. Typningen blev 31/40 (77,5 %), alltså under 80 %, och omkodningen stoppades.
2. **A4:** för betyg mäts samstämmigheten i typning i stället efter regelprövningen. Måttet är 80 dubbelkodade utmaningar (M2d, `kodning/dubbelkodning-efter-regelprovning.json`), och gränsen är 75 %. Utfallet blev 71/80 (88,8 %), så omkodningen används. Måttet före regelprövning (31/40) redovisas som information. `stoppregler.py` tillämpar A4-regeln när filen `dubbelkodning-efter-regelprovning.json` finns. Det gäller i dag bara betyg.
3. **Resultat:** 490 utmaningar (Sprint 16: 440) från 28 avsändare (oförändrat). Övrigt sjönk från 9 till 4.
4. **Sprint 16-filen** är sparad i `research/remissanalys/reformer/betyg/fore-omkodning/`: `utmaningar-betyg-sprint16.json`, `kodning-sprint16/` och `jamforelse.json` (antal och fördelning per typ före och efter, samt samstämmighet).

Betygs metodruta på sidan visar begränsningskoden `omkodad` med båda typningsmåtten.

## 7. SFS-jämförelse

- **Vad jämförs:** SOU:ns föreslagna paragrafer ur författningskommentaren jämförs med propositionens lagförslag och med beslutad lydelse. Alla utredningsförslag jämförs, även betygs (config `sfs_urval: "alla"`).
- **Koppling till förslag:** paragraferna knyts till förslagen på avsnittsnivå, via författningskommentarens avsnittshänvisningar.
- **Bara reformens egna SFS-nummer:** beslutad lydelse tas bara från paragrafversioner som är införda genom reformens egna SFS-nummer (config `lagar[].andringar`).
  - En paragraf som finns i lagen men saknar sådan version blir `ej med`, med förklaring.
  - Lydelser från andra SFS-nummer används inte, eftersom de genomför andra riksdagsbeslut.
  - Textlikhetsmatchning mot en annan paragraf i kapitlet görs bara när paragrafnumret saknas helt i den konsoliderade texten.
- **Status per paragraf:** `oförändrad` (textlikhet ≥ 0,999), `ändrad` (med ordagrann ord-diff) eller `ej med`. Matchningar med under 80 % likhet flaggas för manuell granskning. I datafilen får ett förslag status `i beslutad lag` när alla dess paragrafer har beslutad lydelse.
- **Ej lagtext:** förslag om uppdrag eller myndighetsansvar.
- **Förordningar:** ett förordningsförslag får `ej i SFS per 2026-11-10` bara när en reformspecifik textmarkör (config `forordning_markor`) saknar träffar i de konsoliderade förordningarna. Markörerna är "betyget 4" för betyg (33 förslag) och "ogiltig frånvaro" för studiero (2 förslag). Saknas markör, eller har den träffar, blir status `null` med förklaring i stället för ett obelagt "ej i SFS".
- **Ingen paragraftext (tioarig):** SOU 2021:33:s författningskommentar återger inte paragraftexterna. Därför har tioarig ingen textjämförelse: 45 förslag har status `null` med förklaring, 10 är `ej lagtext`, och datafilen har 0 lagparagrafer.

| Reform | Förslag med status `i beslutad lag` | `null` | `ej lagtext` | `ej i SFS per 2026-11-10` | Lagparagrafer i datafilen |
|---|---|---|---|---|---|
| betyg | 29 | 10 | 8 | 33 | 95 |
| studiero | 3 | 3 | 0 | 2 | 21 |
| stod | 6 | 3 | 0 | 0 | 13 |
| tid | 8 | 9 | 3 | 0 | 19 |
| laroplaner | 4 | 8 | 0 | 0 | 53 |
| spraklig | 1 | 12 | 0 | 0 | 8 |
| tioarig | 0 | 45 | 10 | 0 | 0 |

## 8. Bygga om och kontrollera

Kör från repo-roten. Stegen K6–K10 läser bara incheckade filer och ger deterministisk utdata (inga tidsstämplar).

```bash
python3 research/remissanalys/kedja/kor.py <id>                # K6–K10 → pilot/utmaningar/data/utmaningar-<id>.json
python3 research/remissanalys/kedja/stoppregler.py <id>        # K11, kod 1 = stopp
python3 research/remissanalys/skript/validera-pilot.py <id>    # K12, kod 1 = fel
python3 research/remissanalys/kedja/oversikt.py                # efter alla sju: pilot/utmaningar/data/oversikt.json
node research/remissanalys/skript/testa-pilotsida.js           # K13, alla sju reformer i 1280 och 375 px (Playwright)
python3 research/remissanalys/kedja/granskning.py alla         # granskningsunderlaget, se avsnitt 11
```

- **`<id>`** är `betyg`, `studiero`, `stod`, `tid`, `laroplaner`, `spraklig` eller `tioarig`.
- **`skript/bygg-pilot.py`** är ett omslag som kör `kor.py betyg`. Datafilernas `meta.byggd_av` pekar på `research/remissanalys/kedja/bygg.py` för alla sju reformer.
- **Valideringen** (`validera-pilot.py`) kontrollerar:
  - antal utmaningar och avsändare mot mellanfilen
  - att varje citat har `citatkontroll.ok = true`
  - att varje värde har källa
  - förbjudna ord ("löst", "kvarstår", "bemött tillräckligt"); ordagrann källtext undantas
  - propositionsavsnittens rubriker mot innehållsförteckningen
  - fokusgrupperna mot `gemensamt.json` plus `extra_fokusgrupper`
- **Sidtestet** härleder alla förväntade värden ur datafilerna. Senaste körningen 2026-11-11 gav 323/323.
- **Regression:** från en ren utcheckning av `7cbd0c0` togs de deterministiska mellanfilerna (`passager.json`, `utmaningar.json`, `sfs-diff.json`, `avvikelser.json`) och `oversikt.json` bort. Därefter kördes `kor.py` för alla sju reformer och `oversikt.py`. Resultatet var byte-identiskt: `git diff --exit-code` gav ingen skillnad. `validera-pilot.py` gick igenom för alla sju, och `granskning.py alla` gav identiska CSV-filer. Stoppreglerna och sidtestet kördes i arbetskatalogen, som var lika med samma commit. Kommandona står i `KEDJA.md`.
- **Modellkodningen** (`kedja/kodning.py`) skriver sina underlag och råsvar till `reformer/<id>/kallor/kodning/`, som inte checkas in. Bara de sammanslagna kodfilerna under `reformer/<id>/kodning/` är incheckade. Kodningen kan alltså inte köras om från en ren utcheckning, men allt efter den kan det.

## 9. Sidan

Sidan läser `data/oversikt.json` vid start och en reforms fullständiga datafil först när reformen öppnas. Tillståndet ligger i URL-hashen (`#reform=<id>&typ=…&sak=…&forslag=ingen&fg=…&sf=…&tolk=0`).

- **Startvy** (utan `reform`): jämförelse reform × utmaningstyp. Varje cell visar "x av y", där x är antalet avsändare med minst en utmaning av typen och y är reformens antal avsändare med utmaningar. Färgstyrkan följer andelen. Under 700 px visas jämförelsen som lista. En cell öppnar reformen filtrerad på typen.
- **Vy per reform:**
  - sidhuvud med kedjan och korpusen
  - organisationernas status ur förteckningen (bara reformens fokusorganisationer; publicerade avståendebrev citeras)
  - filter (fokusgrupp, skolform, tolkade kopplingar)
  - utmaningar per typ
  - "Förslag som propositionen inte tar upp"
  - matris sakområde × typ
  - detaljer: "Vad huvudmännen skrev" och "Vad proposition och lag säger"
  - metodruta
- **Förslag som propositionen inte tar upp:** förslag vars redaktionella koppling har matchningen `ingen`, och de utmaningar som är kopplade till dem på nivån förslag, avsnitt eller tolkad. Sidan har en fast text om att det inte betyder att förslaget har fallit. Antal enligt datafilerna:

  | Reform | Förslag som inte tas upp | Utmaningar | Avsändare |
  |---|---|---|---|
  | betyg | 27 av 80 | 111 | 23 |
  | studiero | 2 av 8 | 27 | 10 |
  | stod | 0 av 9 | 0 | 0 |
  | tid | 2 av 20 | 15 | 8 |
  | laroplaner | 0 av 12 | 0 | 0 |
  | spraklig | 6 av 13 | 11 | 6 |
  | tioarig | 9 av 55 | 23 | 11 |

- **Metodrutan** per reform innehåller:
  - korpus och opublicerade yttranden
  - publicerade avståendebrev
  - samstämmighet (identifiering, typning och för betyg efter regelprövning)
  - hämtningsdatum och datum för remissidekontrollen
  - tolkning och namngivning
  - en fast mening per begränsningskod i `meta.begransningar` (texterna står i `index.html`; ingen fritext ur datan visas)
- **Oförändrat från Sprint 16:**
  - banderoll och `noindex`
  - inga länkar till andra sidor på sajten
  - ingen modellskriven fritext
  - klickytor minst 44 px

## 10. Kända begränsningar

Gemensamt för alla reformer:
- **Namngivning är inte bemötande.** "Avsändaren nämns i propositionens avsnitt" betyder bara att namnet förekommer i texten. Sidan bedömer inte om utmaningar är lösta eller om propositionen har tagit hänsyn till dem.
- **Textlikhet är inte saklig ändring.** Textlikheten fångar också ordval och samordning med andra propositioner.
- **Enskilda huvudmän saknas** i alla sju korpusar (kod `spontana_ej_publicerade`).
- **Utmaningar utan jämförelse mot propositionen:** de som har koppling bara till kapitel, ingen koppling eller koppling till förslag utan propositionsavsnitt (`namngivning_i_propositionen` är null). Antal: betyg 245, studiero 114, stod 68, tid 205, laroplaner 139, spraklig 80, tioarig 61.
- **Kopplingsnivåer per reform** (antal utmaningar):

  | Reform | förslag | avsnitt | kapitel | tolkad | ingen |
  |---|---|---|---|---|---|
  | betyg | 57 | 97 | 66 | 175 | 95 |
  | studiero | 76 | 15 | 30 | 79 | 57 |
  | stod | 201 | 23 | 13 | 103 | 55 |
  | tid | 157 | 64 | 79 | 198 | 117 |
  | laroplaner | 62 | 0 | 77 | 83 | 62 |
  | spraklig | 29 | 4 | 45 | 34 | 28 |
  | tioarig | 53 | 10 | 10 | 55 | 38 |

Per reform (begränsningskoder i config `begransningar` och datafilens `meta.begransningar`):

| Reform | Koder | Innebörd |
|---|---|---|
| betyg | `omkodad`, `delad_proposition` (prop. 197, 194), `spontana_ej_publicerade` | Omkodad med den gemensamma instruktionen (avsnitt 6). Förordningsförslag med "ej i SFS per 2026-11-10" kan beslutas senare av regeringen. |
| studiero | `grova_forslagsrutor` (8), `delad_proposition` (prop. 193, 194), `spontana_ej_publicerade` | 8 förslagsrutor med många punkter. Kopplingen gäller hela rutan. |
| stod | `delad_proposition` (prop. 195), `forordning_ej_jamford`, `spontana_ej_publicerade` | Förordningsförslag har inte jämförts maskinellt. SOU 2025:44 är ett delbetänkande. |
| tid | `lag_utan_andring` (diskrimineringslagen), `forordning_ej_jamford`, `skolfs_ej_jamford`, `spontana_ej_publicerade` | Förslaget till diskrimineringslagen genomfördes inte. Läroplansändringar (SKOLFS) finns inte i riksdagens öppna data. |
| laroplaner | `delad_proposition` (prop. 194, 195, 196), `skolfs_ej_jamford`, `beslutad_lydelse_saknas` (1 kap. 3 § skollagen), `spontana_ej_publicerade` | Läroplansförslagen (SKOLFS) är inte jämförda. 1 kap. 3 § saknar beslutad lydelse från reformens SFS-nummer. |
| spraklig | `delad_proposition` (prop. 194), `samordnad_lag` (SFS 2026:1243, bet. 2025/26:UbU26), `skolfs_ej_jamford`, `spontana_ej_publicerade` | Bara betänkandets avsnitt 8 behandlas i propositionen. 2026:1243 innehåller ändringar från flera propositioner. |
| tioarig | `ingen_paragraftext`, `egen_fokusgrupp` (Friskolornas riksförbund i stället för Almega), `aldre_remiss` (2021/2025), `spontana_ej_publicerade` | Ingen SFS-textjämförelse (avsnitt 7). Remissen är från 2021 och propositionen från 2025, så benämningar skiljer sig. Nio kommenterade paragrafer har ingen 2025:729-version kvar, eftersom senare lagar ändrat dem (config `lagar[].anm`). |

## 11. Granskningsunderlag

`research/remissanalys/granskning/` har en CSV per reform, byggd av `kedja/granskning.py <id|alla>` ur den aktuella datafilen och `passager.json`. Instruktionen till granskaren står i `granskning/README.md`, och `rakna-granskning.py` räknar ihop resultatet per reform och totalt.

- **Del 1, träffsäkerhet:** utmaningar jämnt fördelade över typerna, varav cirka 40 % med tolkad koppling. Varje rad har länk till rätt vy på pilotsidan.
- **Del 2, missade utmaningar:** passager om minst 200 tecken som inte kodades som utmaning och inte bara återger utredningens förslag.
- **Antal och urval:** betyg 40 + 20 rader, övriga 15 + 5. Slumpfröna är fasta per reform.
- **Historik:** Sprint 16:s granskningsfil för betyg ligger kvar i `research/remissanalys/v2/granskning/`.

## 12. Förhandsvisning: pilot-sync.sh

`pilot/` är exkluderad från GitHub Pages och når aldrig produktionsroten. Piloten visas bara under `https://reformer.leide.se/dev/utmaningar-pilot/`. Niklas kör synken.

```bash
./pilot-sync.sh --dry-run   # visar vad som skulle kopieras; ändrar ingenting
./pilot-sync.sh             # kopierar index.html och data/ (alla sju datafiler + oversikt.json) till master:dev/utmaningar-pilot/
./pilot-sync.sh --remove    # tar bort dev/utmaningar-pilot/ från master
```

Skriptet:
- kräver att man står på dev, med ren arbetskatalog och lokal dev lika med origin/dev
- arbetar mot master i ett tillfälligt worktree, så att man aldrig lämnar dev
- rör inget annat än `dev/utmaningar-pilot/`
- pushar bara som fast-forward

`commit.sh` tar aldrig bort något på master. Därför måste piloten tas bort med `--remove` när den inte längre ska visas.

## 13. Inför flytt till produktion

Flytt sker först efter manuell granskning. Piloten saknar medvetet två saker som ska läggas till vid flytt till produktion:

- **Cloudflare Web Analytics-snippet** före `</body>`, som alla produktionssidor har.
- **Webbtypsnitten** DM Sans och Source Serif 4 via Google Fonts. Piloten har inga externa beroenden och faller tillbaka på systemtypsnitt.

Dessutom ska man:
- ta bort `noindex` och banderollen
- lägga till sidan i fliknavigationen på alla sidor (varje HTML-fil är fristående)
- ta bort förhandsvisningen med `./pilot-sync.sh --remove`
